"""results json -> markdown tables on stdout. python -I report.py <results.json>"""
import sys, json
R = json.load(open(sys.argv[1]))
f = lambda x, n=3: "-" if x is None else f"{x:.{n}f}"
def line(r, setn):
    d = r[setn]
    if "mean" not in d:
        return f"| {r['row']} {r['ex']} | {d['n_dev']}/{d['n_val']} | - | - | - | - | - | - | - | n/a |"
    return (f"| {r['row']} {r['ex']} | {d['n_dev']}/{d['n_val']} | {d['win']*100:.1f}% | {d['mean']:+.3f} | "
            f"[{d['ci_trade'][0]:+.3f}, {d['ci_trade'][1]:+.3f}] | [{d['ci_day'][0]:+.3f}, {d['ci_day'][1]:+.3f}] | "
            f"{f(d.get('placebo_p'))} | {d['no_best5']:+.3f} | {d.get('dev_mean', float('nan')):+.3f} | "
            + (r.get('verdict', '') if setn == 'down' else 'control') + " |")
H = "| row exit | trades DEV/VAL | win rate VAL | mean R VAL | CI per-trade | CI day-cluster | placebo p | w/o best 5 days | mean R DEV | verdict |\n|---|---|---|---|---|---|---|---|---|---|"
print("## DOWN-phase rows (verdict table)\n" + H)
for r in R["rows"]: print(line(r, "down"))
print("\n## Control: same signals on ALL days (descriptive)\n" + H)
for r in R["rows"]:
    if r["row"] in ("ALL", "K1", "K2", "K3+"): print(line(r, "all"))
print("\ncoverage:", R["coverage"]); print("signal bars:", R["n_signal_bars"]); print("trades:", R["n_trades"])
print("regime_btc:", R["regime_btc"]); print("btc_down_days [down, total]:", R["btc_down_days"]); print("signals in DOWN [down,total]:", R["down_share_signals"])
print("levels:", json.dumps(R["btc_levels"], indent=1))
