"""T06 RSI-MA cross, live and context-only (card t06-paper-forward-build-1110).

Pure decision code for the runner: NO order, NO exchange call, NO auto_trader path. All rule logic stays in the frozen study
file research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/rsi_ma_cross.py (loaded by path, not copied):
find_events (RSI14 vs its SMA14, armed by 60/40 within 6 bars), simulate (stop-order entry, 6-bar swing stop, 2.5R, 30 bars),
fee_r. This file only adapts them to a live feed, same pattern and journal row kinds as malkan_level_short_live.py.

events(b4) -> runner events for the newest CLOSED 4h bar only ("t" = its open ms), both sides pooled (T06). RSI is causal, so
the signal on bar i is the same on any history that ends at i (parity test: batch == one-bar-at-a-time feed).
Event shape: collection_only + shadow_side, NO "side" (the auto_trader cannot map it). Source tag for the ledger/readout:
layer:rsi:rsi_ma_cross (forward_readout.py slot t06_rsi_ma).
Journal (jsonl, append-only, runtime_data/ is git-ignored): rows kind signal | outcome | no_fill | unresolved | kill.
Kill rule (OURS, same as the Malkan forward): after KILL_TRADES closed paper trades net R <= 0 -> verdict KILL, alerts stop.
DECISIONS (OURS): funding is not charged in paper net R (context-only; the study's funding term was negligible in R); the busy rule
(one trade per side) is replayed over the history window given, so it can differ from a longer batch only for a signal whose
entry falls inside a trade that started before the window.
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_STUDY = ROOT / "research/edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/rsi_ma_cross.py"
_spec = importlib.util.spec_from_file_location("rsi_ma_cross_study", _STUDY)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

SOURCE = "layer:rsi:rsi_ma_cross"
PARAMS_ID = "t06_rsi_ma_cross_4h_2026-11-10"
EVENT = {"short": "RSI_MA_CROSS_SHORT", "long": "RSI_MA_CROSS_LONG"}
SIDES = ("short", "long")
STEP_4H = 4 * 3600 * 1000
MIN_4H = 200                         # OURS: Wilder RSI14 + SMA14 + 6-bar arm have converged; fail closed below this
KILL_TRADES = 30
JOURNAL_DEFAULT = "runtime_data/t06_rsi_ma_cross_forward.jsonl"


def _err(msg):
    print(json.dumps({"key": "rsi_ma_cross_live", "error": msg}), file=sys.stderr, flush=True)


def _clean(bars):
    last = None
    for b in bars:
        for k in ("o", "h", "l", "c"):
            v = b.get(k)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
                return False
        t = b.get("t")
        if isinstance(t, bool) or not isinstance(t, int) or (last is not None and t <= last):
            return False
        last = t
    return True


def _ok(b4):
    return bool(b4) and len(b4) >= MIN_4H and _clean(b4)


def events(b4):
    """Runner events for the newest closed 4h bar. Never raises."""
    try:
        if not _ok(b4):
            return []
        i = len(b4) - 1
        out = []
        for side in SIDES:
            if i in S.events_for(b4, side):
                win = b4[i - S.STOP_BARS + 1:i + 1]
                out.append({"t": b4[i]["t"], "event": EVENT[side], "shadow_side": side, "collection_only": True,
                            "entry_ref": b4[i]["o"],
                            "stop": max(x["h"] for x in win) if side == "short" else min(x["l"] for x in win),
                            "target_r": S.TARGET_R, "max_bars": S.HOLD_BARS})
        return out
    except Exception as exc:  # noqa: BLE001 - fail closed: no event, runner keeps running
        _err(f"events: {exc!r}"[:200])
        return []


def resolve(b4, t_trigger, side):
    """Paper outcome of the trigger at open time `t_trigger` on the real bars known now.
    status: unknown | pending (entry bar not here yet) | no_fill (entry bar did not trade through, or skipped by the busy rule)
    | open (filled, no exit yet) | closed (stop/target/time; carries fill, stop, target, net_r)."""
    try:
        idx = {b["t"]: k for k, b in enumerate(b4)}
        if t_trigger not in idx or not _ok(b4):
            return {"status": "unknown"}
        i = idx[t_trigger]
        evs = S.events_for(b4, side)
        if i not in evs:
            return {"status": "unknown"}
        if i == len(b4) - 1:
            return {"status": "pending"}
        tr = next((x for x in S.simulate(b4, evs, side) if x["signal_t"] == t_trigger), None)
        if tr is None:
            return {"status": "no_fill"}
        sgn = -1.0 if side == "short" else 1.0
        base = {"entry": tr["fill"], "stop": tr["stop"], "target": tr["fill"] + sgn * S.TARGET_R * tr["risk"],
                "t_fill": tr["entry_t"]}
        if tr["exit_reason"] == "open_at_end":
            return {"status": "open", **base}
        fee = S.fee_r(tr["risk"] / tr["fill"] * 1e4)
        return {"status": "closed", **base, "exit": tr["exit_reason"], "gross_r": tr["gross_r"], "fee_r": fee,
                "net_r": tr["gross_r"] - fee, "bars": tr["exit_bar"] - tr["entry_bar"] + 1}
    except Exception as exc:  # noqa: BLE001
        _err(f"resolve: {exc!r}"[:200])
        return {"status": "unknown"}


def kill_status(rows):
    """Verdict over the journal rows: closed paper trades only (no_fill/unresolved never count)."""
    nets = [r["net_r"] for r in rows if r.get("kind") == "outcome" and r.get("status") == "closed"]
    n, total = len(nets), sum(nets)
    verdict = "RUNNING" if n < KILL_TRADES else ("KILL" if total <= 0 else "PAST_30")
    return {"verdict": verdict, "closed": n, "net_r_sum": total, "net_r_mean": (total / n) if n else None}


def _read(path):
    rows = []
    p = Path(path)
    if not p.exists():
        return rows
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def _append(path, rows):
    if not rows:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def _key(r):
    return (r["t_trigger"], r.get("side"))


def step(b4, journal_path=JOURNAL_DEFAULT):
    """One poll on a new closed 4h bar: settle open paper trades, check the kill rule, return alert events (journal each new
    signal once). journal_path None = events only. Never raises."""
    try:
        evs = events(b4)
        if not journal_path:
            return evs
        rows = _read(journal_path)
        done = {_key(r) for r in rows if r.get("kind") in ("outcome", "no_fill", "unresolved")}
        new = []
        for r in rows:
            if r.get("kind") != "signal" or _key(r) in done:
                continue
            res = resolve(b4, r["t_trigger"], r["side"])
            base = {"t_trigger": r["t_trigger"], "side": r["side"], "params_id": PARAMS_ID, "source": SOURCE}
            if res["status"] == "closed":
                new.append({"kind": "outcome", **base, **res})
            elif res["status"] == "no_fill":
                new.append({"kind": "no_fill", **base})
            elif res["status"] == "unknown" and b4 and r["t_trigger"] < b4[0]["t"]:
                new.append({"kind": "unresolved", **base, "why": "trigger bar left the history window"})
        rows_all = rows + new
        k = kill_status(rows_all)
        if k["verdict"] == "KILL":
            if not any(r.get("kind") == "kill" for r in rows_all):
                new.append({"kind": "kill", "params_id": PARAMS_ID, "source": SOURCE, **k})
            _append(journal_path, new)
            return []
        have = {_key(r) for r in rows_all if r.get("kind") == "signal"}
        for e in evs:
            if (e["t"], e["shadow_side"]) not in have:
                new.append({"kind": "signal", "t_trigger": e["t"], "side": e["shadow_side"], "params_id": PARAMS_ID,
                            "source": SOURCE, "entry_ref": e["entry_ref"], "stop_provisional": e["stop"],
                            "target_r": e["target_r"]})
        _append(journal_path, new)
        return evs
    except Exception as exc:  # noqa: BLE001
        _err(f"step: {exc!r}"[:200])
        return []


def make_layer(get_4h, journal_path=None):
    """Runner wiring stub (NOT wired into live_runner_cli.py: out of this card's scope). get_4h(bars) -> closed 4h history
    list or None; returns fn(bars) -> events, the shape of make_malkan_level_short_layer. A builder card wires it."""
    def _layer(bars):
        b4 = get_4h(bars)
        return step(b4, journal_path or JOURNAL_DEFAULT) if b4 else []
    _layer.raw = _layer
    return _layer
