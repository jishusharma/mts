"""Pizzino level export: OHLC bars of any time frame -> plain JSON levels and states.

Uses the pz-3 functions (pizzino_indicators.py, SPEC.md sections 1-5) unchanged. Output shape is
the live aid overlay contract (MyTradingSys/tools/live_aid, `A.pizzino` in live_aid_indicators.js
computes the same dict; test_live_aid.py checks both agree).

Rows: [open_time_ms, open, high, low, close, volume] (Binance kline order; strings allowed), closed
bars, oldest first. Observation only: no entry, exit or size wording.

Usage:
  python pizzino_levels.py --klines bars.json --tf 4h            # file: list of rows or {"klines": [...]}
  python pizzino_levels.py --fetch --tf 1d,4h,1h,15m,5m,1m       # Binance fapi BTCUSDT public klines
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pizzino_indicators as pz  # noqa: E402

# Every parameter with its label. SOURCED = the traders' words (SPEC.md P-ids, ME lines); OURS = ours.
PARAMS = {
    "degrees": ([1, 2, 3], "SOURCED: three nested degrees, 1-bar / 2-bar / 3-bar (SPEC P02, ME:22, ME:36)"),
    "pivot_n": ([1, 2, 3], "OURS: degree d = strict fractal of n = d bars each side (SPEC P15/P16, ambiguity A1)"),
    "count_len": (3, "SOURCED: three bars up from the low (SPEC P05, ME:82)"),
    "count_degree": (3, "OURS: turning point T = latest significant degree-3 pivot (SPEC P21)"),
    "W": (50, "OURS: significance window in bars (SPEC P20)"),
    "mid_degree": (3, "OURS: the 50% leg = last degree-3 PH and PL (SPEC P22); 50% = (top + bottom) / 2 is SOURCED (P09)"),
    "N": (2, "OURS: consecutive closes to confirm a break (SPEC P23)"),
    "tol": (0.005, "OURS: retest band 0.5% (SPEC P24)"),
    "R": (20, "OURS: retest window in bars (SPEC P25)"),
    "parents": ({"4h": "1d", "1h": "4h", "15m": "4h", "5m": "4h", "1m": "4h"}, "OURS: lower-time-frame nesting (LTF_RULE)"),
}

LTF_RULE = ("OURS (the traders use D, 3D and W only; 4h and lower is NOT_IN_DATA): the same pivot, state, "
            "count, 50% and retest maths run unchanged on 4h/1h/15m/5m/1m bars, lower bars folded from 1m on "
            "UTC boundaries; each frame is read nested under its parent (4h under 1d, 1h/15m/5m/1m under 4h): "
            "aligned = sign(state sum) equals the parent half (strong +1, weak -1); state sum 0 = not aligned.")

TF_MS = {"1m": 60000, "5m": 300000, "15m": 900000, "1h": 3600000, "4h": 14400000, "1d": 86400000}


def fold(rows, ms):
    """Fold bars into UTC buckets of `ms` (open first, high max, low min, close last, volume sum)."""
    out = []
    for r in rows:
        t = int(r[0]) // ms * ms
        o, h, l, c, v = (float(x) for x in r[1:6])
        if out and out[-1][0] == t:
            b = out[-1]
            b[2], b[3], b[4], b[5] = max(b[2], h), min(b[3], l), c, b[5] + v
        else:
            out.append([t, o, h, l, c, v])
    return out


def _r(x):
    return None if x is None else round(float(x), 8)


def _latest_retest(level, close, high, low, start, N, tol, R):
    """Retest status of `level` over bars start..end: the later of the up and down break."""
    best = None
    for d in ("up", "down"):
        res = pz.break_retest(level, close[start:], high[start:], low[start:], N=N, tol=tol, R=R, direction=d)
        if res["break_confirmed_at"] is None:
            continue
        b = res["break_confirmed_at"] + start
        if best is None or b > best["break_at"]:
            rt = None if res["retest_bar"] is None else res["retest_bar"] + start
            last = len(close) - 1
            if rt is not None:
                status = "retest " + res["outcome"]
            elif last - b >= R:
                status = "no retest in R"
            else:
                status = "awaiting retest"
            best = {"dir": d, "break_at": b, "retest_at": rt, "status": status}
    return best or {"dir": None, "break_at": None, "retest_at": None, "status": "no break"}


def levels_for(rows, tf, parent=None, mid_degree=3, W=50, N=2, tol=0.005, R=20):
    """Pizzino levels and states at the last closed bar of `rows`. `parent` = levels_for() of the parent frame."""
    t = [int(r[0]) for r in rows]
    high = [float(r[2]) for r in rows]
    low = [float(r[3]) for r in rows]
    close = [float(r[4]) for r in rows]
    last = len(close) - 1
    out = {"tf": tf, "asof": t[last] if t else None, "bars": len(close), "close": close[last] if close else None,
           "degrees": [], "conf": 0, "mid": None, "half": None, "leg": None, "count": None, "retest": None,
           "parent": None, "aligned": None, "levels": []}
    if not close:
        return out
    piv = {}
    for d in (1, 2, 3):
        p = pz.find_pivots(high, low, d)  # confirmed_at = index + d <= last by construction
        piv[d] = p
        ph = [x.price for x in p if x.kind == "H"]
        pl = [x.price for x in p if x.kind == "L"]
        state, brk = pz.swing_state(ph, pl, close[last])
        out["degrees"].append({"d": d, "state": state, "break": _r(brk), "ph": _r(ph[-1] if ph else None),
                               "pl": _r(pl[-1] if pl else None)})
        out["conf"] += state
        if ph:
            out["levels"].append({"n": f"PZ {tf} PH{d}", "p": _r(ph[-1]), "kind": "PH", "d": d})
        if pl:
            out["levels"].append({"n": f"PZ {tf} PL{d}", "p": _r(pl[-1]), "kind": "PL", "d": d})
    pm = piv[mid_degree]
    hs = [x for x in pm if x.kind == "H"]
    ls = [x for x in pm if x.kind == "L"]
    if hs and ls:
        h, l = hs[-1], ls[-1]
        mid = pz.mid_line(h.price, l.price)
        prev = None
        for c in close[max(h.confirmed_at, l.confirmed_at):]:
            prev = pz.half_state(c, mid, prev)
        out["mid"], out["half"] = _r(mid), prev
        out["leg"] = {"from": "H" if h.index < l.index else "L", "ph": _r(h.price), "pl": _r(l.price),
                      "ph_t": t[h.index], "pl_t": t[l.index]}
        out["levels"].append({"n": f"PZ {tf} 50%", "p": _r(mid), "kind": "MID", "d": mid_degree})
        out["retest"] = _latest_retest(mid, close, high, low, max(h.confirmed_at, l.confirmed_at), N, tol, R)
    p3 = piv[PARAMS["count_degree"][0]]
    for p in reversed(p3):
        if pz.is_significant(low if p.kind == "L" else high, p.index, p.kind, W):
            c = pz.bar_count_from(high, low, p.index, p.kind)[-1]
            out["count"] = {"from": p.kind, "t": t[p.index], "price": _r(p.price), "count": c,
                            "three_bar": abs(c) >= PARAMS["count_len"][0]}
            break
    if parent is not None and parent.get("half"):
        ps = 1 if parent["half"] == "strong" else -1
        out["parent"] = {"tf": parent["tf"], "half": parent["half"], "mid": parent["mid"]}
        out["aligned"] = out["conf"] != 0 and (1 if out["conf"] > 0 else -1) == ps
    return out


def export(bars_by_tf):
    """{tf: rows} -> {"layer": "pizzino", "frames": [...], "params": ..., "ltf_rule": ...}; parents first."""
    order = [tf for tf in ("1d", "4h", "1h", "15m", "5m", "1m") if tf in bars_by_tf]
    done = {}
    for tf in order:
        par = PARAMS["parents"][0].get(tf)
        done[tf] = levels_for(bars_by_tf[tf], tf, parent=done.get(par))
    return {"layer": "pizzino", "frames": [done[tf] for tf in order],
            "params": {k: {"value": v, "label": lab.split(":")[0], "note": lab} for k, (v, lab) in PARAMS.items()},
            "ltf_rule": LTF_RULE}


def _fetch(tf, limit=1500):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval={tf}&limit={limit}"
    with urllib.request.urlopen(url, timeout=20) as r:
        rows = json.load(r)
    return rows[:-1]  # drop the forming bar


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tf", default="1d,4h,1h,15m,5m,1m")
    ap.add_argument("--klines", help="JSON file of 1m (or --tf-sized) rows; lower frames are folded from it")
    ap.add_argument("--fetch", action="store_true", help="Binance fapi BTCUSDT public klines per frame")
    a = ap.parse_args(argv)
    tfs = a.tf.split(",")
    if a.fetch:
        bars = {tf: _fetch(tf) for tf in tfs}
    elif a.klines:
        raw = json.loads(Path(a.klines).read_text(encoding="utf-8"))
        raw = raw["klines"] if isinstance(raw, dict) else raw
        bars = {tf: fold(raw, TF_MS[tf]) for tf in tfs}
    else:
        ap.error("give --klines or --fetch")
    sys.stdout.write(json.dumps(export(bars), indent=1) + "\n")


if __name__ == "__main__":
    main()
