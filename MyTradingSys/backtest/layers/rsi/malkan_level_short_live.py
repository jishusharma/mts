"""Malkan level short, live and context-only (card malkan-level-short-testnet-forward-1109).

Pure decision code for the runner: NO order, NO exchange call, NO auto_trader path. All signal logic stays in
malkan_level_short.signals() / outcome() (imported, not copied); this file only adapts them to a live feed.

Arm (frozen, pinned in research/malkan_level_shorts_2026-11-09/FORWARD_PREREG.md): the count arm "+structure div 3-10
close (SOURCED window)", n=126, +0.10 R net, not significant: layers level + structure(div) + trigger, div_window (3, 10),
price_mode close, target 2R, 60-bar time stop, fee BINANCE_TAKER. WaveTrend and HTF are not layers of this arm; the
daily and weekly history is still required (fail closed when short) and the FULL-stack agreement at the same bar rides
along as `full_stack` context.

events(bars4h, bars1d, bars1w) -> runner events for the newest CLOSED 4h bar only ("t" = its open ms). signals() needs the
entry bar after the trigger, which a live feed does not have yet, so one synthetic fill bar is appended after the newest
bar (open = high = close of the newest bar, low far under the prior open): the trigger layers read data up to the trigger
bar's close only (parity test: batch == one-bar-at-a-time feed), so the synthetic bar decides nothing but the fill the live
alert cannot know. The alert carries the planned entry reference (the trigger bar's open: a stop-sell under it within 3
bars) and the provisional stop; the real fill, stop and target are written by the paper journal once later bars exist.

Event shape: collection_only + shadow_side "short", NO "side" (the auto_trader cannot map it, same pattern as wlow_bounce).
Journal (jsonl, append-only, runtime_data/ is git-ignored): rows kind signal | outcome | no_fill | unresolved | kill.
Kill rule (FORWARD_PREREG.md, operator-set, OURS): after KILL_TRADES closed paper trades net R <= 0 -> verdict KILL, alerts stop.
"""
import json
import math
import sys
from pathlib import Path

from MyTradingSys.backtest.layers.rsi import malkan_level_short as M

PARAMS_ID = "malkan_level_short_4h_div3_10_2026-11-09"
EVENT = "MALKAN_LEVEL_SHORT_DIV3_10"
ARM = {"layers": M.BASE | {"structure"}, "structure": "div", "div_window": (3, 10), "price_mode": "close"}
STEP_4H = 4 * 3600 * 1000
DAY, WEEK = 86400000, 7 * 86400000
MIN_4H = M.LEVEL_LOOKBACK + 40      # history must cover the 360-bar level lookback (fail closed below this)
MIN_1D = 30                         # daily RSI(14) plus the 2 rows the htf layer reads, with slack
MIN_1W = 20                         # weekly RSI(14) plus the 3 rows the htf layer reads, with slack
NO_FILL_AFTER = 3                   # signals() looks for the entry on the 3 bars after the trigger
KILL_TRADES = 30
JOURNAL_DEFAULT = "runtime_data/malkan_level_short_forward.jsonl"


def _err(msg):
    print(json.dumps({"key": "malkan_level_short_live", "error": msg}), file=sys.stderr, flush=True)


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


def _closed(bars, step, t_close):
    return [x for x in bars if x["t"] + step <= t_close]


def _inputs(b4, b1d, b1w):
    """(b4, closed daily, closed weekly) or None when anything is missing, unclean or too short."""
    if not b4 or len(b4) < MIN_4H or not b1d or not b1w:
        return None
    tc = b4[-1]["t"] + STEP_4H
    d, w = _closed(b1d, DAY, tc), _closed(b1w, WEEK, tc)
    if len(d) < MIN_1D or len(w) < MIN_1W or not (_clean(b4) and _clean(d) and _clean(w)):
        return None
    return d, w


def _with_fill_bar(b4):
    """b4 + one synthetic bar that always trades under the last bar's open (see module docstring)."""
    last = b4[-1]
    return b4 + [{"t": last["t"] + STEP_4H, "o": last["c"], "h": last["c"], "l": min(last["o"], last["c"]) * 0.5, "c": last["c"]}]


def events(b4, b1d, b1w, layers=None, structure=None):
    """Runner events for the newest closed 4h bar. `layers`/`structure` override the arm (tests: the 5-layer C3 read)."""
    try:
        got = _inputs(b4, b1d, b1w)
        if got is None:
            return []
        d, w = got
        kw = dict(ARM)
        if layers is not None:
            kw["layers"] = layers
        if structure is not None:
            kw["structure"] = structure
        i = len(b4) - 1
        sig = [s for s in M.signals(_with_fill_bar(b4), d, w, **kw) if s["i"] == i]
        if not sig:
            return []
        full = [s for s in M.signals(_with_fill_bar(b4), d, w, layers=M.FULL, structure="either",
                                     div_window=kw["div_window"], price_mode=kw["price_mode"]) if s["i"] == i]
        s = sig[0]
        return [{"t": b4[i]["t"], "event": EVENT, "shadow_side": "short", "collection_only": True,
                 "entry_ref": b4[i]["o"], "stop": s["stop"], "target_r": M.TARGET_R, "max_bars": M.MAX_BARS,
                 "full_stack": bool(full)}]
    except Exception as exc:  # noqa: BLE001 - fail closed: no event, runner keeps running
        _err(f"events: {exc!r}"[:200])
        return []


def resolve(b4, b1d, b1w, t_trigger, layers=None, structure=None):
    """Paper outcome of the trigger at open time `t_trigger` on the bars known now (real bars, no synthetic one).
    status: unknown (trigger not in b4) | pending (fill window not over) | no_fill (never filled, or skipped by the 6-bar
    rule) | open (filled, no stop/target yet and under 60 bars) | closed (stop/target/time; carries stop, target, net_r)."""
    try:
        idx = {b["t"]: k for k, b in enumerate(b4)}
        if t_trigger not in idx:
            return {"status": "unknown"}
        i = idx[t_trigger]
        got = _inputs(b4, b1d, b1w)
        if got is None:
            return {"status": "unknown"}
        d, w = got
        kw = dict(ARM)
        if layers is not None:
            kw["layers"] = layers
        if structure is not None:
            kw["structure"] = structure
        s = next((x for x in M.signals(b4, d, w, **kw) if x["t_trigger"] == t_trigger), None)
        if s is None:
            return {"status": "no_fill" if len(b4) - 1 - i >= NO_FILL_AFTER + 1 else "pending"}
        o = M.outcome(b4, s["j"], s["entry"], s["stop"])
        risk = s["stop"] - s["entry"]
        base = {"entry": s["entry"], "stop": s["stop"], "target": s["entry"] - M.TARGET_R * risk, "t_fill": b4[s["j"]]["t"]}
        if o["exit"] == "time" and len(b4) - s["j"] < M.MAX_BARS:
            return {"status": "open", **base}
        return {"status": "closed", **base, "exit": o["exit"], "gross_r": o["gross_r"], "net_r": o["net_r"],
                "bars": o["bars"], "hit_1r": o["hit_1r"]}
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


def step(b4, b1d, b1w, journal_path=JOURNAL_DEFAULT):
    """One poll on a new closed 4h bar: settle open paper trades, check the kill rule, then return the alert events (and
    journal each new signal once). journal_path None = events only. Never raises."""
    try:
        evs = events(b4, b1d, b1w)
        if not journal_path:
            return evs
        rows = _read(journal_path)
        done = {r["t_trigger"] for r in rows if r.get("kind") in ("outcome", "no_fill", "unresolved")}
        new = []
        for r in rows:
            if r.get("kind") != "signal" or r["t_trigger"] in done:
                continue
            res = resolve(b4, b1d, b1w, r["t_trigger"])
            if res["status"] == "closed":
                new.append({"kind": "outcome", "t_trigger": r["t_trigger"], "params_id": PARAMS_ID, **res})
            elif res["status"] == "no_fill":
                new.append({"kind": "no_fill", "t_trigger": r["t_trigger"], "params_id": PARAMS_ID})
            elif res["status"] == "unknown" and b4 and r["t_trigger"] < b4[0]["t"]:
                new.append({"kind": "unresolved", "t_trigger": r["t_trigger"], "params_id": PARAMS_ID,
                            "why": "trigger bar left the history window"})
        rows_all = rows + new
        k = kill_status(rows_all)
        if k["verdict"] == "KILL":
            if not any(r.get("kind") == "kill" for r in rows_all):
                new.append({"kind": "kill", "params_id": PARAMS_ID, **k})
            _append(journal_path, new)
            return []
        have = {r["t_trigger"] for r in rows_all if r.get("kind") == "signal"}
        for e in evs:
            if e["t"] not in have:
                new.append({"kind": "signal", "t_trigger": e["t"], "params_id": PARAMS_ID, "entry_ref": e["entry_ref"],
                            "stop_provisional": e["stop"], "target_r": e["target_r"], "full_stack": e["full_stack"]})
        _append(journal_path, new)
        return evs
    except Exception as exc:  # noqa: BLE001
        _err(f"step: {exc!r}"[:200])
        return []
