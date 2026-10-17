"""Fire counts per detector and per setup S1-S9 on BTCUSDT 1d / 1w, DEV only (2020-01 .. 2024-06).

Bars are aggregated from local 1m kline files (UTC day, Monday-start week); nothing from 2024-07 on is read
(VALIDATION / HOLDOUT stay sealed). The 2017-2019 DEV years are not on this machine: NOT_IN_DATA, so counts
cover 2020-01..2024-06 only. Volume is the Binance 1m file's (perp or spot as stored): venue question q-krown-volume-venue.
Usage: python run_fire_counts.py [out.md]
"""
import csv
import io
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import krown_core as kc  # noqa: E402
import krown_events as ke  # noqa: E402

DEV_END = (2024, 6)
SRC_A = Path("F:/MTS/data/dev_ext_2019_2021/klines")          # BTCUSDT-1m-YYYY-MM.csv, 2020-01..2021-12
SRC_B = Path("F:/MTS/data/candle_close_dev_2022_2024")        # BTCUSDT-1m-YYYY-MM.zip, 2022-01..2024-06
DAY = 86400000


def month_rows(y, m):
    name = f"BTCUSDT-1m-{y}-{m:02d}"
    if (SRC_A / f"{name}.csv").exists():
        f = open(SRC_A / f"{name}.csv", newline="", encoding="utf-8")
    elif (SRC_B / f"{name}.zip").exists():
        z = zipfile.ZipFile(SRC_B / f"{name}.zip")
        f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline="")
    else:
        return
    with f:
        for r in csv.reader(f):
            if r and r[0].isdigit():
                yield int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])


def daily_bars():
    days = {}
    for y in range(2020, DEV_END[0] + 1):
        for m in range(1, 13):
            if (y, m) > DEV_END:
                break
            for t, o, h, l, c, v in month_rows(y, m):
                d = t // DAY
                b = days.get(d)
                if b is None:
                    days[d] = [d * DAY, o, h, l, c, v, 1]
                else:
                    b[2] = max(b[2], h)
                    b[3] = min(b[3], l)
                    b[4] = c
                    b[5] += v
                    b[6] += 1
    return [b[:6] for d, b in sorted(days.items()) if b[6] == 1440]  # full UTC days only


def weekly_bars(days):
    wk = {}
    for t, o, h, l, c, v in days:
        w = (t // DAY - 4) // 7  # 1970-01-01 is a Thursday: day 4 is the first Monday
        wk.setdefault(w, []).append((t, o, h, l, c, v))
    out = []
    for w, rows in sorted(wk.items()):
        if len(rows) == 7 and all(rows[i][0] + DAY == rows[i + 1][0] for i in range(6)):
            out.append((rows[0][0], rows[0][1], max(r[2] for r in rows), min(r[3] for r in rows), rows[-1][4],
                        sum(r[5] for r in rows)))
    return out


def detector_counts(o, h, l, c, v, p):
    n = len(c)
    out = {}
    st = kc.trend_state(h, l, c, p["zone_k"], p["swing_tol"])
    out["swing highs/lows (confirmed)"] = len(kc.swings(h, l, p["zone_k"]))
    out["trend state: up bars"] = sum(1 for s in st if s["state"] == "up")
    out["trend state: down bars"] = sum(1 for s in st if s["state"] == "down")
    out["trend reversals (state flips up<->down)"] = sum(
        1 for a, b in zip(st, st[1:]) if {a["state"], b["state"]} == {"up", "down"})
    sw = kc.swings(h, l, p["zone_k"])
    ratio = kc.vol_ratio(v, p["vol_sma"])
    out["bars with >=1 ranked zone"] = sum(1 for t in range(n) if kc.zones_from(sw, h, l, c, ratio, t, p))
    out["volume >= 2x (prior-20 baseline)"] = sum(1 for r in ratio if r is not None and r >= p["vol_mult"])
    slot = kc.vol_ratio_slot(v, p["vol_slots"], p["vol_slot_prev"])
    out["volume >= 2x (same-slot baseline)"] = sum(1 for r in slot if r is not None and r >= p["vol_mult"])
    out["volume <= 0.5x"] = sum(1 for r in ratio if r is not None and r <= p["vol_half"])
    bw = kc.bbwp(c, p["bbwp_basis"], p["bbwp_lookback"], p["bbwp_mult"])
    out["BBWP >= 85 (expansion)"] = sum(1 for x in bw if x is not None and x >= p["bbwp_high"])
    out["BBWP <= 30 (compression)"] = sum(1 for x in bw if x is not None and x <= p["bbwp_low"])
    out["strict bullish engulfing"] = sum(1 for t in range(1, n) if kc.engulfing(h, l, c, t) == "bull")
    out["strict bearish engulfing"] = sum(1 for t in range(1, n) if kc.engulfing(h, l, c, t) == "bear")
    out["hammer"] = sum(1 for t in range(n) if kc.is_hammer(o[t], h[t], l[t], c[t], p))
    out["shooting star"] = sum(1 for t in range(n) if kc.is_shooting_star(o[t], h[t], l[t], c[t], p))
    out["doji"] = sum(1 for t in range(n) if kc.is_doji(o[t], h[t], l[t], c[t], p))
    out["three black crows"] = sum(1 for t in range(n) if kc.three_crows(o, c, t))
    out["21/55 EMA crosses"] = sum(1 for x in kc.crosses(kc.ema(c, p["ma_fast"]), kc.ema(c, p["ma_slow"])) if x)
    out["leash events (5 EMA, >=3 closes)"] = len(kc.leash(l, h, kc.ema(c, p["ma_leash"]), p["leash_n"]))
    r = kc.rsi(c, p["rsi_period"])
    out["RSI zone bars: bull/range/bear"] = "/".join(str(sum(1 for x in r if kc.rsi_zone(x) == z))
                                                    for z in ("bull", "range", "bear"))
    out["bearish RSI divergences"] = len(kc.bear_divergence(h, l, r, p["zone_k"]))
    rs = [kc.range_state(h, l, c, t, p) for t in range(n)]
    out["range bars (n=20 prior, width<=25%)"] = sum(1 for x in rs if x)
    out["range edge bars"] = sum(1 for x in rs if x and x["edge"])
    out["range breakout closes"] = sum(1 for x in rs if x and x["breakout"])
    return out


def main():
    p = kc.load_params()
    days = daily_bars()
    series = {"1d": days, "1w": weekly_bars(days)}
    lines = ["# Krown v0 fire counts, BTCUSDT DEV only", "",
             f"Bars: 1d {len(series['1d'])} ({datetime.fromtimestamp(days[0][0] / 1000, timezone.utc):%Y-%m-%d} .. "
             f"{datetime.fromtimestamp(days[-1][0] / 1000, timezone.utc):%Y-%m-%d}), 1w {len(series['1w'])}. "
             "DEV 2020-01..2024-06 from local 1m files (2017-2019 NOT_IN_DATA here). VALIDATION/HOLDOUT not read. "
             "Ceiling (PRE_REG_KROWN item 3): <= 1.0 event per 10 daily bars per setup.", ""]
    for tf, rows in series.items():
        o = [r[1] for r in rows]
        h = [r[2] for r in rows]
        l = [r[3] for r in rows]
        c = [r[4] for r in rows]
        v = [r[5] for r in rows]
        lines += [f"## {tf} ({len(c)} bars)", "", "| detector | count |", "|---|---|"]
        for k, x in detector_counts(o, h, l, c, v, p).items():
            lines.append(f"| {k} | {x} |")
        ev = ke.build_events(o, h, l, c, v, enabled=True)
        fc = ke.fire_counts(ev, len(c))
        lines += ["", "| setup | events | per 10 bars | long/short |", "|---|---|---|---|"]
        for s in ke.SETUPS:
            ls = f"{sum(1 for e in ev if e['setup'] == s and e['side'] == 'long')}/" \
                 f"{sum(1 for e in ev if e['setup'] == s and e['side'] == 'short')}"
            lines.append(f"| {s} | {fc[s]['n']} | {fc[s]['per_10_bars']} | {ls} |")
        over = ke.over_ceiling(fc, 1.0)
        lines += ["", f"Over the 1.0 per 10 bars ceiling: {', '.join(over) if over else 'none'}", ""]
    text = "\n".join(lines) + "\n"
    print(text)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
