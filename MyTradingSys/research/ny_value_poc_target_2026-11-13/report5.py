"""Render results.json to markdown tables. python -I report5.py <results.json>  (prints to stdout)"""
import sys, json

def f(x, n=3):
    return "n/a" if x is None or x != x else f"{x:.{n}f}"

def name(r):
    return f"{r['reg']} / stop {r['stop']} / {r['side']}"

def tables(res, key):
    rows = res[key]["rows"]
    o = ["### Count table", "", "| cell | n | days | reach-POC % | reach-stop % | median RR | mean R gross | mean R net | best 10 days R / total R (sum over trades) | per-year mean net R (n) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r["n"]:
            o.append(f"| {name(r)} | 0 | 0 | | | | | | | |"); continue
        yrs = " ".join(f"{y}:{f(v[1], 2)}({v[0]})" for y, v in r["years"].items())
        o.append(f"| {name(r)} | {r['n']} | {r['days']} | {f(r['reach_poc'], 1)} | {f(r['reach_stop'], 1)} | {f(r['rr_med'], 2)} | {f(r['gross'])} | {f(r['net'])} | {f(r["top10_sum"], 1)} / {f(r["total_sum"], 1)} | {yrs} |")
    o += ["", "### Trade table", "", "| cell | n | days | reach-POC % | median RR | mean R gross | mean R net | trade CI | day CI | placebo p (mean / p95) | 2024+ mean (n) | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r["n"]:
            continue
        v = r["verdict"] if key == "new" else r["verdict"] + " (seen, info)"
        o.append(f"| {name(r)} | {r['n']} | {r['days']} | {f(r['reach_poc'], 1)} | {f(r['rr_med'], 2)} | {f(r['gross'])} | {f(r['net'])} | [{f(r['t_lo'])}, {f(r['t_hi'])}] | [{f(r['d_lo'])}, {f(r['d_hi'])}] | {f(r['plc_p'], 4)} ({f(r['plc_mean'])} / {f(r['plc_p95'])}) | {f(r['net_2024'])} ({r['n_2024']}) | {v} |")
    o += ["", "Failed checks per cell: " + "; ".join(f"{name(r)}: " + (",".join(k for k, v in r["checks"].items() if not v) or "none") for r in rows if r["n"])]
    return "\n".join(o)

def cover(res, key):
    o = ["| coin | first | last | 1m bars | sessions | open outside | setups | skipped (POC < 36 bp) |", "|---|---|---|---|---|---|---|---|"]
    for s, c in res[key]["cover"].items():
        o.append(f"| {s} | {c['first']} | {c['last']} | {c['bars']:,} | {c['sessions_used']} | {c['open_outside']} | {c['setups']} | {c['skipped_lt36bp']} |")
    t_su = sum(c["setups"] for c in res[key]["cover"].values()); t_sk = sum(c["skipped_lt36bp"] for c in res[key]["cover"].values())
    o.append(f"| total | | | | | | {t_su} | {t_sk} ({100 * t_sk / max(t_su, 1):.1f}%) |")
    return "\n".join(o)

if __name__ == "__main__":
    res = json.load(open(sys.argv[1]))
    print("## Coverage new coins\n\n" + cover(res, "new"))
    print("\n## New coins (TEST)\n\n" + tables(res, "new"))
    print("\n## Coverage seen data\n\n" + cover(res, "seen"))
    print("\n## Seen data (BTC/ETH/SOL, NOT part of the verdict)\n\n" + tables(res, "seen"))
    print("\n## Per coin, stop A, both sides, all days\n\n| coin | n | reach-POC % | mean net R |\n|---|---|---|---|")
    for s, p in res["per_coin_stopA"].items():
        print(f"| {s} | {p['n']} | {f(p['reach'], 1)} | {f(p['net'])} |")
    m = res["regime"]
    print(f"\nRegime mix: BTC UTC days (close vs 200-day SMA, 5% band): DEV bull {m['days']['DEV']['bull']}% / bear {m['days']['DEV']['bear']}% / range {m['days']['DEV']['range']}%; "
          f"2024+ bull {m['days']['S2024']['bull']}% / bear {m['days']['S2024']['bear']}% / range {m['days']['S2024']['range']}%. "
          f"New-coin setups (stop A, all days) by that label: DEV {m['setups']['DEV']}; 2024+ {m['setups']['S2024']}.")
