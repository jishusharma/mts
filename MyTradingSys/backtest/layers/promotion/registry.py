"""Promoted-setups registry reader (stdlib only, pure). Used by the live runner (shadow marking) and by promote.py.

File: MyTradingSys/execution/promoted_setups.json = {"version": 1, "entries": [{"setup_id", "mode", "manifest",
"promoted_at", "commit"}]}. setup_id is a trade-source prefix such as "layer:fabio:volume_fvg:" (the same prefix form
auto_trader uses: source = "layer:<layer>:<sub>:<tf>"). mode is "shadow" (alerts collected, never traded) or "testnet".

Fail closed: a missing, unreadable or malformed registry means NO alert may trade (every alert is made collection-only).
A well-formed empty registry changes nothing. A layer that is not in the registry keeps today's behaviour."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DEFAULT_PATH = REPO / "MyTradingSys" / "execution" / "promoted_setups.json"
MODES = ("shadow", "testnet")
ENTRY_KEYS = ("setup_id", "mode", "manifest", "promoted_at", "commit")


def load_registry(path=None):
    """(entries, error). error is None when the file is well formed (entries may be empty), else a reason string and
    entries == []. Never raises."""
    p = Path(path) if path else DEFAULT_PATH
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [], "promoted_setups unreadable: %r" % (e,)
    if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("entries"), list):
        return [], "promoted_setups malformed (need {version: 1, entries: [...]})"
    seen = set()
    for i, e in enumerate(raw["entries"]):
        if not isinstance(e, dict):
            return [], "entry %d is not an object" % i
        for k in ENTRY_KEYS:
            if not isinstance(e.get(k), str) or not e[k].strip():
                return [], "entry %d: %s missing or not a non-empty string" % (i, k)
        if e["mode"] not in MODES:
            return [], "entry %d: mode %r not in %s" % (i, e["mode"], MODES)
        if e["setup_id"] in seen:
            return [], "entry %d: duplicate setup_id %s" % (i, e["setup_id"])
        seen.add(e["setup_id"])
    return list(raw["entries"]), None


def alert_source(alert):
    """Trade-source string auto_trader derives for a layer alert."""
    return "layer:%s:%s:%s" % (alert.get("layer"), alert.get("sub"), alert.get("tf"))


def entry_for_source(source, entries):
    """Longest-prefix registry entry for a source, or None."""
    hits = [e for e in entries if source.startswith(e["setup_id"])]
    return max(hits, key=lambda e: len(e["setup_id"])) if hits else None


def make_collection_only(alert, why):
    """Strip the tradable side (kept as shadow_side) and tag the alert collection-only. Returns a new dict."""
    a = dict(alert)
    side = a.pop("side", None)
    if side in ("long", "short") and "shadow_side" not in a:
        a["shadow_side"] = side
    a["collection_only"] = True
    a["promotion_note"] = why
    return a


def apply_promotion_gate(alerts, path=None):
    """Alerts for a registry entry in mode shadow become collection-only. Mode testnet and unregistered sources pass
    unchanged (today's behaviour). Unreadable/malformed registry: every alert becomes collection-only."""
    entries, err = load_registry(path)
    if err:
        return [make_collection_only(a, "registry error, fail closed: " + err) for a in alerts]
    out = []
    for a in alerts:
        e = entry_for_source(alert_source(a), entries)
        out.append(make_collection_only(a, "shadow: " + e["setup_id"]) if e and e["mode"] == "shadow" else a)
    return out
