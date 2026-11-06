"""Daily Habib watch: BTCUSDT candles on 1h / 4h / 1d that meet our stand-in for his imbalance definition, one line per candidate.

Candidate = a CLOSED candle with relative volume >= REL_VOL_K (volume / median of the prior 50 bars of the same timeframe; k = 2.0 is OURS,
his number is not public: imbalance_qriptal_2026-10-16/README.md:39). Each line gives the body class (small / mid / large), the wick label,
and whether the candle sits at a known level: prior-day high / low / close / POC / VAH / VAL (port of MyTradingSys/tools/live_aid/tf_strip.js
levels()), weekly open, monthly open, prior-week high / low. Levels are computed causally at the candle's own open time.
No trades, no backtest, no advice. A line is a CANDIDATE, never "his" candle. The forming candle is excluded.

Usage (repo root):
  python MyTradingSys/research/habib_concept_book_2026-11/habib_watch.py [--now 2026-11-07T12:00:00Z] [--k 2.0]
Public klines only (data-api.binance.vision).
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import habib_common as hc  # noqa: E402

# window per timeframe: how many closed candles back are listed (OURS)
WINDOW = {"1h": 24, "4h": 12, "1d": 7}
READ = {"small": "small body: effort without result (C2)", "large": "large body: strength, do not fade (C3)", "mid": "mid body"}


def level_hits(candle, levels):
    """Known levels the candle sits at. -> list of (name, price, how) with how = open / mid (tight) or range (loose)."""
    out = []
    mid = (candle[2] + candle[3]) / 2
    for name, v in levels.items():
        if abs(candle[1] - v) / v <= hc.TOL_MID:
            how = "open"
        elif abs(mid - v) / v <= hc.TOL_MID:
            how = "mid"
        elif candle[3] * (1 - hc.TOL_RANGE) <= v <= candle[2] * (1 + hc.TOL_RANGE):
            how = "range"
        else:
            continue
        out.append((name, v, how))
    out.sort(key=lambda x: ({"open": 0, "mid": 0, "range": 1}[x[2]], abs(candle[4] - x[1])))
    return out


def candidates(rows_by_tf, bars1m, now_ms, k=hc.REL_VOL_K):
    """Candidate lines for the closed candles in each timeframe's window. Pure: no network."""
    lines = []
    for tf in ("1d", "4h", "1h"):
        rows = rows_by_tf[tf]
        rv = hc.rel_volume(rows)
        step = hc.TF_MS[tf]
        closed = [i for i, r in enumerate(rows) if r[0] + step <= now_ms]
        for i in closed[-WINDOW[tf]:]:
            x = rv[i]
            if x is None or x < k:
                continue
            r = rows[i]
            lv = hc.prior_day_levels(bars1m, r[0])
            lv.update(hc.week_month_levels(bars1m, r[0]))
            hits = level_hits(r, lv)
            b = hc.body_frac(r)
            cls = hc.body_class(r)
            u, l = hc.wicks(r)
            if hits:
                n, v, how = hits[0]
                where = f"at {n} {v:,.0f} [{how}]" + (f" +{len(hits) - 1} more" if len(hits) > 1 else "")
            else:
                where = "no known level"
            lines.append((r[0], f"{tf:>2} {hc.utc(r[0]):%m-%d %H:%M}Z rv {x:4.1f} body {b:4.0%} {cls:<5} {hc.wick_label(r):<15} "
                                f"wicks up {u:3.0%} dn {l:3.0%} | {where} | {READ.get(cls, cls)}"))
    return [t for _, t in sorted(lines, key=lambda z: z[0], reverse=True)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--now", help="UTC time for a replay, e.g. 2026-11-07T12:00:00Z (default: now)")
    ap.add_argument("--k", type=float, default=hc.REL_VOL_K, help="relative-volume threshold (OURS, default 2.0)")
    a = ap.parse_args(argv)
    now = (datetime.strptime(a.now, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) if a.now else datetime.now(timezone.utc))
    nm = hc.ms_of(now)
    rows = {}
    for tf in ("1h", "4h", "1d"):
        n_hist = hc.VOL_LOOKBACK + WINDOW[tf] + 2
        rows[tf] = hc.fetch_klines(tf, nm - n_hist * hc.TF_MS[tf], nm)
    need_from = nm - (WINDOW["1d"] + 16) * hc.DAY       # prior-week levels for the oldest daily candle
    bars = hc.fetch_klines("1m", need_from, nm)
    out = candidates(rows, bars, nm, a.k)
    print(f"Habib watch BTCUSDT (Binance spot), {now:%Y-%m-%d %H:%M}Z, rv >= {a.k} vs 50-bar median (OURS); closed candles only; "
          f"1h last {WINDOW['1h']}, 4h last {WINDOW['4h']}, 1d last {WINDOW['1d']}")
    if not out:
        print("no candidates")
    for line in out:
        print(line)
    lv = hc.prior_day_levels(bars, nm)
    lv.update(hc.week_month_levels(bars, nm))
    print("levels now: " + "; ".join(f"{n} {v:,.0f}" for n, v in lv.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
