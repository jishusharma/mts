"""
Consensus hook: the one call the live alert runner makes after each poll (ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43).

When EITHER core fires, write one consensus row (writer.append_row) built from what is already on disk:
  - Fabio core fired  = this poll emitted at least one alert with layer "fabio".
  - Tom core fired    = runtime_data/last_alert.json carries an alert number greater than the one stored in the hook's
                        own state file (the Tom card is written by the market loop, a different process).
  - rsi block         = rsi/observation.read_latest() (the newest rsi_events record per timeframe the runner persisted).
  - snapshot          = the newest runtime_data/snapshots/BTCUSDT_*.json; its file stem is the snapshot_id (nothing else
                        mints one, see consensus/README.md open item 1), current_price comes from the file.

OBSERVATION ONLY: nothing here gates, vetoes or delays a core. Imports nothing from execution/ (the Tom card is
parsed with the same field names as execution/auto_trader.py CARD_FIELD / parse_tom_alert, copied, not imported:
test_layer_boundaries.py forbids the import). consensus_after_poll never raises: any error is swallowed and the
poll goes on. The only files written are the consensus daily jsonl and the hook's own tiny state file.
"""
import json
import logging
import math
import re
from pathlib import Path

from MyTradingSys.backtest.layers.consensus import writer
from MyTradingSys.backtest.layers.rsi import observation

_LOG = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[4]
TOM_ALERT = REPO_ROOT / "runtime_data" / "last_alert.json"
SNAP_DIR = REPO_ROOT / "runtime_data" / "snapshots"
ALERTS_DIR = REPO_ROOT / "MyTradingSys" / "runtime" / "alerts"
STATE_PATH = REPO_ROOT / "MyTradingSys" / "runtime" / "consensus_hook_state.json"

CARD_FIELD = re.compile(r"^(VERDICT|TIME|PRICE|SETUP|ZONE|ENTRY|STOP|TARGET|RUNNER_TARGET|R:R):\s*(.*)$", re.M)
ALERT_NO = re.compile(r"#(\d+)")


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def read_tom(path=None):
    """The Tom card as {alert_no, verdict, setup, side, entry, stop, target, net_rr}, or None (no file, no ENTRY/STOP/
    TARGET, unreadable). Same field rules as auto_trader.parse_tom_alert."""
    alert = _load_json(path or TOM_ALERT)
    if not isinstance(alert, dict):
        return None
    fields = {k: v.strip() for k, v in CARD_FIELD.findall(alert.get("card_text") or "")}
    entry, stop, target = _num(fields.get("ENTRY")), _num(fields.get("STOP")), _num(fields.get("TARGET"))
    if entry is None or stop is None or target is None:
        return None
    m = ALERT_NO.search(alert.get("title") or "")
    setup = fields.get("SETUP", "")
    side = "long" if setup.endswith("_long") else "short" if setup.endswith("_short") else None
    rr = re.search(r"net\s+([0-9.]+)", fields.get("R:R", ""))
    return {"alert_no": int(m.group(1)) if m else None, "verdict": fields.get("VERDICT", ""), "setup": setup,
            "side": side, "entry": entry, "stop": stop, "target": target,
            "net_rr": float(rr.group(1)) if rr else None}


def fabio_from_alerts(alerts):
    """The newest layer-"fabio" alert of this poll as the consensus fabio block, or None. A collection-only (shadow)
    alert carries shadow_side instead of side; it is reported (this is an observation) with the same side key."""
    mine = [a for a in alerts or [] if isinstance(a, dict) and a.get("layer") == "fabio"]
    if not mine:
        return None
    a = max(mine, key=lambda x: x.get("t_close") or 0)
    return {"verdict": "%s:%s" % (a.get("sub"), a.get("event")), "model": a.get("model"),
            "side": a.get("side") or a.get("shadow_side"),
            "entry": a.get("entry_ref") if a.get("entry_ref") is not None else a.get("entry"),
            "stop": a.get("stop"), "target": a.get("target")}


def latest_snapshot(snap_dir=None):
    """{"snapshot_id": <file stem>, "current_price": float|None} for the newest BTCUSDT_*.json, or None."""
    try:
        files = sorted(Path(snap_dir or SNAP_DIR).glob("BTCUSDT_*.json"))
    except OSError:
        return None
    if not files:
        return None
    snap = _load_json(files[-1])
    price = _num(snap.get("current_price")) if isinstance(snap, dict) else None
    return {"snapshot_id": files[-1].stem, "current_price": price}


def _read_state(path):
    st = _load_json(path)
    return st if isinstance(st, dict) else {}


def _write_state(path, st):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(st) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def consensus_after_poll(alerts, *, tom_path=None, snap_dir=None, alerts_dir=None, state_path=None,
                         base_dir=None, now=None):
    """Write one consensus row if a core fired this poll. Returns True when a row was written. Never raises."""
    try:
        state_path = Path(state_path or STATE_PATH)
        state = _read_state(state_path)
        tom = read_tom(tom_path)
        seen = state.get("tom_alert_no")
        tom_new = bool(tom) and tom["alert_no"] is not None and (seen is None or tom["alert_no"] > seen)
        fabio = fabio_from_alerts(alerts)
        if tom_new:
            state["tom_alert_no"] = tom["alert_no"]
            _write_state(state_path, state)
            if seen is None:
                # First start: remember the current Tom alert, do not log a row for a card that predates the hook.
                tom_new = False
        if not fabio and not tom_new:
            return False
        notes = "trigger=" + "+".join(t for t, on in (("tom", tom_new), ("fabio", bool(fabio))) if on)
        return writer.append_row(latest_snapshot(snap_dir), tom, fabio,
                                 observation.read_latest(alerts_dir=alerts_dir or ALERTS_DIR),
                                 notes=notes, base_dir=base_dir, now=now)
    except Exception as exc:  # noqa: BLE001 - the runner must never notice this hook
        try:
            _LOG.warning("consensus hook: %s: %s", type(exc).__name__, exc)
        except Exception:  # noqa: BLE001
            pass
        return False
