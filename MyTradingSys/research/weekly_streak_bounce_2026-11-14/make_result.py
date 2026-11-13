"""Render RESULT.md from rows.json + btc_streaks.json. Usage: python make_result.py <outdir> <result.md>"""
import sys, json, time, pathlib
o = pathlib.Path(sys.argv[1]); rows = json.load(open(o / "rows.json")); bs = json.load(open(o / "btc_streaks.json"))
d = lambda ms: time.strftime("%Y-%m-%d", time.gmtime(ms / 1000))
pc = lambda v, k=1: "-" if v is None else f"{v*100:.{k}f}%"
nm = lambda r: f"{r['event']} {r['entry']} {r['exit']}"
def line(r):
    unit = (lambda v: "-" if v is None else f"{v:.2f}R") if r["exit"] == "XS" else pc
    return (f"| {nm(r)} | {r['nDEV']}/{r['nVAL']} | {pc(r.get('win'),0)} | {unit(r.get('mean'))} ({pc(r.get('mean_pct'))}) | "
            f"{unit(r.get('ci_lo'))} | {'-' if r.get('p') is None else f'{r['p']:.3f}'} | {unit(r.get('ex3'))} | {unit(r.get('devmean'))} | {r['verdict']} |")
H = ("| Row (event entry exit) | Events DEV/VAL | Win | Mean VAL (R for XS; % in brackets) | CI low (week-cluster) | Placebo p | Without best 3 weeks | DEV mean | Verdict |\n"
     "|---|---|---|---|---|---|---|---|---|")
npass = sum(r["verdict"] == "PASS" for r in rows)
ev = [r for r in rows if r["entry"] == "E1" and r["exit"] == "X1"]
mix = ", ".join(f"{r['event']} {pc(r['bear_share_val'],0)}" for r in ev)
s5 = next(r for r in rows if r["event"] == "S5" and r["entry"] == "E1" and r["exit"] == "X1")
perc = ", ".join(f"{k} {v}" for k, v in sorted(s5["coins_val"].items(), key=lambda kv: -kv[1]))
best = sorted([r for r in rows if r["nVAL"] >= 30 and r.get("p") is not None], key=lambda r: r["p"])[:3]
T = []
T.append(f"# RESULT: weekly red-streak bounce, LONG only (edge9, 2026-11-14)\n\nResearch, not advice. PRE_REG.md governs (code: study.py, make_result.py, test_study.py). Data: Binance spot daily via data-api.binance.vision, 22 coins (BTC, ETH + 20 largest others with >=4y history), weeks Monday 00:00 UTC, last complete week = Mon 2026-11-02. Costs 12 bp round trip (fees.py).\n")
T.append(f"## Verdict\n**{npass} of 48 rows PASS. No entry trigger shows a fee-net edge after N red weeks.** Mean returns are mostly within noise of zero, and the week-cluster CI lower bound is below 0 on every row with >= 30 VAL events. Streak N=6 (the operator's setup) has only {next(r for r in rows if r['event']=='S6' and r['entry']=='E1' and r['exit']=='X1')['nVAL']} VAL events on E1 and is UNDERPOWERED on E2/E3.\n")
T.append("Closest to a signal (descriptive, not a pass): " + "; ".join(f"{nm(r)} mean {pc(r['mean_pct'])}, CI low {pc(r['ci_lo']) if r['exit']!='XS' else '%.2fR'%r['ci_lo']}, p {r['p']:.3f}" for r in best) + ".\n")
T.append(f"Regime mix: share of VAL events fired while weekly close < 50-week MA (BEAR): {mix}. Unknown-regime events (first 50 weeks of a coin) are excluded from the share. VALIDATION (2022-01-01 on) is dominated by the 2022 bear, the 2023 to 2026 chop and the 2026 slide, so the result says little about a bull-phase streak.\n")
T.append("## Main table: STREAK-5 (primary), all 12 rows\n" + H + "\n" + "\n".join(line(r) for r in rows if r["event"] == "S5") + "\n")
T.append(f"S5 E1 VAL events per coin: {perc} (total {s5['nVAL']} trades, {s5['nclusters']} calendar-week clusters).\n")
T.append("## All other rows\n" + H + "\n" + "\n".join(line(r) for r in rows if r["event"] != "S5") + "\n")
T.append("## BTC: every streak of >= 5 red weeks (Coinbase BTC-USD, 2015 on, complete weeks)\nForward returns: next Monday open to the close of week +1/+2/+4/+8 (no costs). Swept = traded below the last red week's low within 3 weeks; Reclaim = then a daily close back above it.\n\n| Streak start to last red week | Weeks | Open-to-close depth | +1w | +2w | +4w | +8w | Swept / Reclaim |\n|---|---|---|---|---|---|---|---|")
for b in bs:
    T.append(f"| {d(b['start'])} to {d(b['end'])} | {b['n']} | {pc(b['depth'])} | {pc(b['r1'])} | {pc(b['r2'])} | {pc(b['r4'])} | {pc(b['r8'])} | {'Y' if b['swept'] else 'N'} / {'Y' if b['reclaim'] else 'N'} |")
T.append(f"\n{len(bs)} rows only (Coinbase series is gap-free from 2015-07-20): the last row is the ONGOING streak, 5 completed red weeks (the 6th, from 2026-11-09, was still open at data pull), so it has no forward returns. Two finished streaks in 11 years cannot power any test; descriptive only. Neither reclaimed the last red week's low within 3 weeks (2022 swept it and kept falling; 2026 never swept it).\n")
T.append("""## Caveats
- Survivorship: coins are today's large caps (listed >= 4y), which favours longs; XMR delisted from Binance (data to 2024-02) and is kept for the span it has.
- XS rows: R is net return divided by (entry - stop)/entry; tiny stop distances make R fat-tailed and the XS means are unstable (win rate 23-42%). Read the % return in brackets and the CI.
- DD20 events and E3/E2 entries overlap in calendar weeks across coins (one crash week fires many coins); the CI is week-clustered but the effective sample is a few dozen independent weeks.
- Gate 4 (BH 10%) is applied to the 48 placebo p-values; no row reached it.
- Test: test_study.py has 4 tests; with STUDY_BUG=lookahead (E1 entry one day early) test_streak_event_and_e1_is_next_monday_open fails, without it all pass.
""")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(T))
