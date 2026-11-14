"""results.json -> RESULT.md. python report.py <results.json> <RESULT.md>"""
import sys, json
r = json.load(open(sys.argv[1]))
f = lambda x, d=1: "n/a" if x != x else f"{x:.{d}f}"
L = []
cname = lambda w: f"{w['reg']} / {'skip30' if w['skip'] else 'no-skip'} / {w['side']}"
npass = sum(w["pass"] for w in r["rows"])
L.append("# RESULT: Tom's return-to-value on the prior NY cash-session value area (BTC, ETH, SOL)\n")
L.append(f"**Verdict: FAIL. {npass} of 12 cells pass. Price that re-enters the prior NY-session value reaches the OPPOSITE edge only about 40% of the time (his claim 70-80%), and no cell has a fee-net edge on VALIDATION.**\n")
L.append("Slug edge4-ny-session-value-1113. Pre-registered in PRE_REG.md (committed before any outcome). Code: fetch_1m.py, study.py, report.py, test_ny_session_value.py, spot_check.py.\n")
L.append("## Window, data, rule (state of the run)")
L.append("- Profile window = prior NY cash session via `auction_context.prior_ny_session_profile` (the previously unused function): 13:30-20:00 UTC in US daylight time, 14:30-21:00 UTC in winter (code `_us_dst`: 2nd Sunday March to 1st Sunday November). Weekdays only; Monday uses Friday; US holidays not modelled; sessions < 90% bars skipped.")
L.append("- Data: Binance spot 1m klines (data.binance.vision monthly archive), 2020-01-01 (SOL 2020-09-01) to 2026-10-31. " + "; ".join(f"{k}: {v['bars']:,} bars, {v['sessions_used']} sessions, {v['open_outside']} open outside prior value" for k, v in r["cover"].items()) + ". No monthly file missing. Spot volume as weight.")
L.append(f"- Costs: 5 bp taker + 1 bp slippage per side = {r['cost']['rt']*1e4:.0f} bp round trip (fees.py BINANCE_TAKER; the order said 4 bp/side, this is 2 bp/side harsher). Stop at session extreme + 1 bp; trades with stop < 10 bp skipped.")
L.append("- DEV to 2023-12-31, VALIDATION 2024-01-01 to 2026-10-31. Pooled over three coins, bootstrap by session date (5000), placebo 500 draws, BH 10% over 12 cells.")
L.append("- Independent check: `spot_check.py` recomputed one prior-session value area (BTC 2024-03-12) without the repo code; VAL/VAH/POC identical to the cent.\n")
L.append("## 1. Plain count (Tom's claim): setup = open outside prior value, two 30m closes back inside; reach = price touches the opposite edge before session end (stop ignored)\n")
L.append("| cell | n DEV | reach % DEV | n VAL | reach-other-edge % VAL | reach before stop % VAL |\n|---|---|---|---|---|---|")
for w in r["rows"]:
    L.append(f"| {cname(w)} | {w['n_dev']} | {f(w['reach_dev'])} | {w['n_val']} | {f(w['reach_val'])} | {f(w['reachbs_val'])} |")
L.append("\nSupplementary descriptive counts (NOT pre-registered cells; both splits, pooled sides and coins):\n")
L.append("| split | sessions opening outside value | any 1m touch of value % | setup (skip30) n / % of those | setup reaches POC % | setup reaches OTHER EDGE % |\n|---|---|---|---|---|---|")
for s in r["supp"]:
    k = s["skip1"]
    L.append(f"| {s['split']} | {s['n_open_outside']} | {f(s['touch_value_pct'])} | {k['n']} / {f(k['setup_pct_of_open_outside'])} | {f(k['reach_poc_pct'])} | {f(k['reach_edge_pct'])} |")
L.append("\nRead: his 70% is reproduced for the return to the POC (about 68-70% once two 30m closes are back inside value), not for the opposite edge (about 40%). The trade targets the opposite edge, so the claim the trade needs is the 40%, not the 70%. This POC split was added after seeing the numbers: descriptive, it is not a tested edge.\n")
L.append("## 2. Trade result, fee-net, VALIDATION\n")
L.append("| cell | n VAL | reach-other-edge % | mean R net | 95% CI | mean R DEV | win % | placebo mean / p95 | beats placebo | BH 10% | verdict |\n|---|---|---|---|---|---|---|---|---|---|---|")
for w in r["rows"]:
    L.append(f"| {cname(w)} | {w['n_val']} | {f(w['reach_val'])} | {f(w['mean_val'],3)} | [{f(w['lo'],3)}, {f(w['hi'],3)}] | {f(w['mean_dev'],3)} | {f(w['win_val'])} | {f(w['plc_mean'],3)} / {f(w['plc_p95'],3)} | {'yes' if w['beats'] else 'no'} | {'yes' if w['bh'] else 'no'} | {'PASS' if w['pass'] else 'FAIL'} |")
L.append("\nPass needs all of: n >= 30, mean > 0, CI lower bound > 0, beats placebo p95, BH 10%. 'Beats placebo' alone is weak here: placebo entries at random times inside value lose about 0.1-0.2 R, so the setup timing beats random entry yet still does not make money.\n")
L.append("## 3. Per coin, descriptive (both sides, all days)\n")
L.append("| coin | variant | n DEV | mean R DEV | n VAL | reach % VAL | mean R VAL |\n|---|---|---|---|---|---|---|")
for p in r["persym"]:
    L.append(f"| {p['sym']} | {'skip30' if p['skip'] else 'no-skip'} | {p['n_dev']} | {f(p['mean_dev'],3)} | {p['n_val']} | {f(p['reach_val'])} | {f(p['mean_val'],3)} |")
m, t = r["mixes"], r["trade_mix"]
L.append("\n## Regime mix")
L.append(f"Regime mix: BTC UTC days, close vs 200-day SMA (band 5%): DEV bull {m['DEV']['bull']}% / bear {m['DEV']['bear']}% / range {m['DEV']['range']}%; VALIDATION bull {m['VAL']['bull']}% / bear {m['VAL']['bear']}% / range {m['VAL']['range']}%.")
L.append(f"Setups (skip30, all coins) by that label: DEV bull {t['DEV']['bull']}% / bear {t['DEV']['bear']}% / range {t['DEV']['range']}% (n/a {t['DEV']['n/a']}% = first 200 days, no SMA), balanced-day share {t['DEV']['balanced_share']}% of {t['DEV']['n_trades_skip_yes']}; VALIDATION bull {t['VAL']['bull']}% / bear {t['VAL']['bear']}% / range {t['VAL']['range']}%, balanced share {t['VAL']['balanced_share']}% of {t['VAL']['n_trades_skip_yes']}.")
L.append("VALIDATION is a bull-leaning window (BTC above its 200d SMA most days); short cells are fading that, long cells riding it.\n")
L.append("## Limits")
L.append("- Spot volume, not perp; US holidays treated as sessions; 30m closes taken from 1m closes; fills at the close with fixed 1 bp slippage; stop gaps inside a 1m bar not modelled.")
L.append("- Balanced-day rule (inside day OR small opening range) and the 5 bp bin, 10 bp min stop, 1 bp buffer are OURS.")
L.append("- 12 cells share the same sessions (long/short disjoint, regimes overlap), so cells are not independent.")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(L) + "\n")
