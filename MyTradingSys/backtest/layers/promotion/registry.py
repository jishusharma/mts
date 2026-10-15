"""Promoted-setups registry reader (stdlib only, pure). Used by the live runner (shadow marking) and by promote.py.

File: MyTradingSys/execution/promoted_setups.json = {"version": 1, "entries": [{"setup_id", "mode", "manifest",
"promoted_at", "commit"}]}. setup_id is a trade-source prefix such as "layer:fabio:volume_fvg:" (the same prefix form
auto_trader uses: source = "layer:<layer>:<sub>:<tf>"). mode is "shadow" (alerts collected, never traded) or "testnet".

Fail closed: a missing, unreadable or malformed registry means NO alert may trade (every alert is made collection-only).
DEFAULT-DENY (fable H1, enforced in auto_trader): a source with no registry entry may trade only if it is on the explicit
pre_pipeline_sources grandfather list in auto_trader_config.json; see decision_for_source. apply_promotion_gate below
(live runner) only marks shadow entries."""
import json
import re
from datetime import date
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


def grandfather_error(grandfather):
    """None when `grandfather` is a well-formed pre_pipeline_sources table {prefix: {reason, review_by}}, else a reason.
    An empty table is well formed (nothing grandfathered). Pure."""
    if not isinstance(grandfather, dict):
        return "pre_pipeline_sources is not an object"
    for prefix, v in grandfather.items():
        if not isinstance(prefix, str) or not prefix.strip():
            return "pre_pipeline_sources: empty or non-string prefix"
        if not isinstance(v, dict):
            return "pre_pipeline_sources[%s] is not an object" % prefix
        if not isinstance(v.get("reason"), str) or not v["reason"].strip():
            return "pre_pipeline_sources[%s]: reason missing" % prefix
        rb = v.get("review_by")
        if not isinstance(rb, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", rb):
            return "pre_pipeline_sources[%s]: review_by must be YYYY-MM-DD" % prefix
        try:
            date.fromisoformat(rb)
        except ValueError:
            return "pre_pipeline_sources[%s]: review_by is not a date" % prefix
    return None


def decision_for_source(source, entries, grandfather):
    """Pure default-deny lookup -> 'trade' | 'shadow' | 'unregistered' | 'registry_error'.
    entries: load_registry() entries, or None when the registry could not be read; grandfather: pre_pipeline_sources.
    A registry entry wins (shadow never trades, even for a grandfathered prefix; testnet trades). No entry: trades only
    when the source starts with a grandfathered prefix, else 'unregistered'. entries None or a malformed grandfather
    table -> 'registry_error' (callers reject everything)."""
    if entries is None or grandfather_error(grandfather) is not None or not isinstance(source, str):
        return "registry_error"
    e = entry_for_source(source, entries)
    if e is not None:
        return "shadow" if e["mode"] == "shadow" else "trade"
    return "trade" if any(source.startswith(p) for p in grandfather) else "unregistered"


def size_entry(v, ceiling=10000):
    """Shared size_overrides entry check (auto_trader.size_override and promote.has_testnet_flag): -> (size_usd,
    max_loss_usd), or raises ValueError. size: int (not bool), 0 < size <= ceiling, a multiple of 10 (Deribit contract);
    max_loss_usd: a positive finite number. Pure."""
    size = v.get("size_usd") if isinstance(v, dict) else None
    loss = v.get("max_loss_usd") if isinstance(v, dict) else None
    if not (isinstance(size, int) and not isinstance(size, bool) and 0 < size <= ceiling and size % 10 == 0):
        raise ValueError("size_usd %r" % (size,))
    if not (isinstance(loss, (int, float)) and not isinstance(loss, bool) and loss > 0 and loss != float("inf")):
        raise ValueError("max_loss_usd %r" % (loss,))
    return size, loss


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
