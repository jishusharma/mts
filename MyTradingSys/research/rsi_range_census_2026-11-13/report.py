"""Builds REPORT.md and the BTC key-tables file from results.json (+ live fetch for section 4)."""
import json, sys, time, urllib.request, datetime as dt
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "backtest" / "layers" / "rsi"))
from rsi_core import rsi_core
from census_lib import band, PCTS

R = json.load(open(HERE / "results.json"))
TFS = ["5m", "15m", "1h", "4h", "1d", "1w"]
DN = ["<25", "25-30", "30-35", "35-40", "40-45", "45-50", "50-60", "60-70", ">70"]
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
NOTES_TABLES = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def f(x, d=1):
    return "-" if x is None else f"{x:.{d}f}"


def mark(n):
    return f"{n}*" if n < 30 else str(n)


def sec1_md(sym, tf_src):
    L = [f"### {sym}: min/max and percentiles\n",
         "| tf | bars | from | min (date UTC) | max (date UTC) | " + " | ".join(f"p{p:g}" for p in PCTS) + " |",
         "|" + "---|" * (5 + len(PCTS))]
    for tf in TFS:
        s = tf_src[tf]
        L.append(f"| {tf} | {s['n']} | {s['first'][:10]} | {s['min']:.1f} ({s['min_at']}) | {s['max']:.1f} ({s['max_at']}) | "
                 + " | ".join(f(s['pct'][str(p)]) for p in PCTS) + " |")
    L.append("\nBands in his words (RSI levels): rarely hit = below p1; sometimes hit = p1 to p5; common = above p5. Low side and high side (mirror: rare high = above p99, sometimes = p95-p99).\n")
    L.append("| tf | rarely hit (low) below | sometimes hit (low) | sometimes hit (high) | rarely hit (high) above |")
    L.append("|---|---|---|---|---|")
    for tf in TFS:
        p = tf_src[tf]["pct"]
        L.append(f"| {tf} | {p['1']:.1f} | {p['1']:.1f} - {p['5']:.1f} | {p['95']:.1f} - {p['99']:.1f} | {p['99']:.1f} |")
    L.append("\nEpisodes (separate runs of consecutive bars below the level) per year; total, and bars below:\n")
    L.append("| tf | level | total episodes | bars below | per year |")
    L.append("|---|---|---|---|---|")
    for tf in TFS:
        s = tf_src[tf]
        for th in ["30", "25", "20", "15", "10"]:
            ys = s["eps"][th]
            L.append(f"| {tf} | <{th} | {s['eps_total'][th]} | {s['bars_below'][th]} | " + ", ".join(f"{y}:{n}" for y, n in sorted(ys.items())) + " |")
    return "\n".join(L)


def sec2_md(sym):
    L = []
    for key, title in [("1h|1d", "1h RSI low reached that day, given last CLOSED daily RSI"),
                       ("4h|1d", "4h RSI low reached that day, given last CLOSED daily RSI"),
                       ("15m|1h", "15m RSI low reached in the hour, given last CLOSED 1h RSI")]:
        t = R[sym]["sec2"][key]
        L.append(f"### {sym}: {title}\n")
        L.append("Cells: lowest lower-timeframe RSI seen inside the period (n periods; * = n<30). Columns lt = share of periods touching below the level.\n")
        L.append("| given RSI | n | min | p1 | p5 | p25 | median | <30 | <25 | <20 | <15 | <10 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for b in DN:
            c = t[b]
            if not c:
                L.append(f"| {b} | 0 | - | - | - | - | - | - | - | - | - | - |")
                continue
            L.append(f"| {b} | {mark(c['n'])} | {c['min']:.1f} | {c['p1']:.1f} | {c['p5']:.1f} | {c['p25']:.1f} | {c['med']:.1f} | "
                     + " | ".join(f"{c['lt'+str(x)]:.1f}%" for x in [30, 25, 20, 15, 10]) + " |")
        L.append("")
    return "\n".join(L)


def sec3_md(sym):
    L = []
    for thr in ["30", "25", "20", "15", "10"]:
        t = R[sym]["sec3"][thr]
        L.append(f"### {sym}: first touch of 1h RSI <= {thr}, by last closed daily RSI bucket\n")
        L.append("Forward return from touch-bar close, gross of fees: median / mean / % positive / worst (%). Max further drop = lowest low in next 24 1h bars vs entry (median %, worst %, median and worst in 1h-ATR14 multiples). * = n<30.\n")
        L.append("| daily RSI | n | 1h | 4h | 12h | 24h | 72h | drop24 med % | drop24 worst % | drop24 med ATR | worst ATR |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for b in DN + ["ALL"]:
            c = t[b]
            if not c:
                continue
            cells = []
            for h in ["1", "4", "12", "24", "72"]:
                x = c[h]
                cells.append("-" if not x else f"{x['med']:.2f} / {x['mean']:.2f} / {x['pos']:.0f}% / {x['worst']:.1f}")
            L.append(f"| {b} | {mark(c['n'])} | " + " | ".join(cells)
                     + f" | {f(c['dd_med'],2)} | {f(c['dd_worst'],1)} | {f(c['ddatr_med'],2)} | {f(c['ddatr_worst'],1)} |")
        L.append("")
    return "\n".join(L)


def get_live(sym, interval, limit=1000):
    u = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval={interval}&limit={limit}"
    for k in range(5):
        try:
            return json.loads(urllib.request.urlopen(u, timeout=30).read())["result"]["list"][::-1]
        except Exception:
            time.sleep(1 + k)
    raise RuntimeError("live fetch failed")


def live_md():
    now = dt.datetime.now(dt.timezone.utc)
    L = [f"Fetched {now.strftime('%Y-%m-%d %H:%M')} UTC from Bybit linear BTCUSDT. 'last closed' = most recent finished bar; 'forming' = bar in progress.\n",
         "| tf | last closed RSI | forming RSI | band (vs BTC history) | approx percentile | price |",
         "|---|---|---|---|---|---|"]
    for tf, iv in [("5m", "5"), ("15m", "15"), ("1h", "60"), ("4h", "240"), ("1d", "D"), ("1w", "W")]:
        k = get_live("BTCUSDT", iv)
        closes = [float(x[4]) for x in k]
        r = rsi_core(closes)
        s = R["BTCUSDT"]["sec1"][tf]["pct"]
        v = r[-2]
        pts = sorted((s[str(p)], p) for p in PCTS)
        pct = "<0.1" if v < pts[0][0] else (">99.9" if v > pts[-1][0] else None)
        if pct is None:
            for (a, pa), (b, pb) in zip(pts, pts[1:]):
                if a <= v <= b:
                    pct = f"{pa + (pb - pa) * ((v - a) / (b - a) if b > a else 0):.1f}"
                    break
        bd = band(v, s["1"], s["5"]) if v < s["50"] else ("high side: " + ("rarely hit" if v > s["99"] else "sometimes hit" if v >= s["95"] else "common"))
        L.append(f"| {tf} | {v:.1f} | {r[-1]:.1f} | {bd} | {pct} | {closes[-1]:.0f} |")
    return "\n".join(L)


def main():
    parts = ["# RSI range census (descriptive), 2026-11-13\n",
             "**Verdict: DESCRIPTIVE, no trade rule, no pass rule.** Wilder RSI(14) on closes via `rsi_core`; Bybit linear 5m klines (BTC from 2020-03, ETH from 2021-03, SOL from 2021-10) rolled up to 15m/1h/4h/1d (UTC) and 1w (Monday UTC). First 150 bars dropped (50 for 1w). Closed bars only. Gross of fees, so no fee import needed.\n",
             "Regime mix: all regimes pooled (2020-2026 incl. the 2020-21 bull, 2022 bear, 2023 chop, 2024-25 bull/top, 2025-26 drawdown); no regime filter. Context: none, because descriptive census.\n",
             "Caveat: forward windows of touches in the same sell-off overlap; n counts episodes, not independent samples. Cells with n<30 are marked *.\n",
             "## Key readings (BTC)\n",
             "- Rare band is almost the same on every timeframe from 5m to 1d: below about 22-24 is the 1st percentile, below about 30-32 the 5th. Weekly is tighter (1st pct 27.0, all-time low 25.7 in 2022-06; the 2013+ daily-built weekly low is also 25.7).\n",
             "- All-time lows: 5m 3.9, 15m 4.2, 1h 5.9, 4h 5.2, 1d 15.4 (2026-06-06; 10.5 on 2018-11-20 in the long csv), 1w 25.7.\n",
             "- Daily RSI barely changes how DEEP the 1h RSI goes (the 1% tail sits near 15-19 in almost every bucket) but changes how OFTEN it dips: 1h touches below 30 on 42% of days when daily is under 25 versus 13% when daily is over 70.\n",
             "- A 1h touch of <=20 is not a bounce signal by itself: median 24h forward return about +0.2% (51% positive, n=138 pooled) and median further drop within 24h about -2.8% (2.5 hourly ATRs). Section 3 splits by daily bucket (most cells n<30).\n",
             "## 1. How far RSI goes\n"]
    for sym in SYMS:
        parts.append(sec1_md(sym, R[sym]["sec1"]))
    parts.append("### BTC long history (repo csv `btc_cycles_2026-11/btc_daily.csv`, 2013+, mixed sources: blockchain.info/Binance)\n")
    ls = R["BTC_LONG"]
    parts.append("| tf | bars | from | min (date) | max (date) | p0.1 | p1 | p5 | p50 | p95 | p99 | p99.9 |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for tf in ["1d", "1w"]:
        s = ls[tf]; p = s["pct"]
        parts.append(f"| {tf} | {s['n']} | {s['first'][:10]} | {s['min']:.1f} ({s['min_at'][:10]}) | {s['max']:.1f} ({s['max_at'][:10]}) | "
                     + " | ".join(f"{p[k]:.1f}" for k in ["0.1", "1", "5", "50", "95", "99", "99.9"]) + " |")
    parts.append("\n## 2. Given the higher-timeframe RSI, how low does the lower one go\n")
    for sym in SYMS:
        parts.append(sec2_md(sym))
    parts.append("## 3. After a 1h RSI touch of the low levels\n")
    for sym in SYMS:
        parts.append(sec3_md(sym))
    parts.append("## 4. BTC right now\n")
    parts.append(live_md())
    open(HERE / "REPORT.md", "w", encoding="utf-8").write("\n".join(parts) + "\n")
    if NOTES_TABLES:
        b = ["# RSI census key tables (BTCUSDT, Bybit linear), from rsi_range_census_2026-11-13\n", "## 1\n", sec1_md("BTCUSDT", R["BTCUSDT"]["sec1"]),
             "\n## 2\n", sec2_md("BTCUSDT"), "\n## 3\n", sec3_md("BTCUSDT")]
        open(NOTES_TABLES, "w", encoding="utf-8").write("\n".join(b) + "\n")


if __name__ == "__main__":
    main()
