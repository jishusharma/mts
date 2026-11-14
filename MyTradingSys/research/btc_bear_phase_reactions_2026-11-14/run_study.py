"""Builds episodes, outcome stats, level hit rates and the 'today' tables. Writes episodes.csv and tables.md."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import btc_bear as b

HERE = os.path.dirname(os.path.abspath(__file__))
NOW = pd.Timestamp("2026-11-14")


def pct(x, nd=0):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x * 100:.{nd}f}%"


def q(vals, p):
    v = [x for x in vals if x is not None and not np.isnan(x)]
    return float(np.percentile(v, p)) if v else float("nan")


def ab(x):
    return "n/a" if x is None else ("above" if x else "below")


def main():
    d = b.load_daily()
    w = b.to_weekly(d)
    eps = b.build_episodes(d, w)
    for e in eps:
        b.episode_features(d, w, e)
    ongoing = [e for e in eps if e["post_weeks"] == 0 and e["low_date"] >= NOW - pd.Timedelta(days=14)]
    hist = [e for e in eps if e not in ongoing]
    for e in hist:
        e["strict"] = "streak" in e["kinds"] and "fall" in e["kinds"]
    strict = [e for e in hist if e["strict"]]
    out = []

    rows = []
    for e in eps:
        rows.append({"start_week": e["start_week"].date(), "detect": e["detect_date"].date(), "kinds": "+".join(sorted(e["kinds"])),
                     "red_streak": e["streak_len"], "low_date": e["low_date"].date(), "low": round(e["low"], 2),
                     "depth_vs_8w_high_close": round(e["depth"], 3), "b1w": e["bounce"][1], "b2w": e["bounce"][2],
                     "b4w": e["bounce"][4], "b8w": e["bounce"][8], "days_detect_to_low": e["days_trig_to_low"],
                     "above50w": e["ma50_t"], "above200w": e["ma200_t"], "cycle": e["cycle"],
                     "days_since_halving": e["days_halving"], "days_since_peak": e["days_peak"],
                     "swing_low": e["swing_low"], "bear_trap": e["trap"], "retest": e["retest"],
                     "outcome26w": e["outcome_short"], "post_weeks": e["post_weeks"]})
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "episodes.csv"), index=False)

    out.append("## T1 strict episodes (>=5 red weekly closes AND >=18% fall)\n")
    out.append("| Detect (5th red close) | Red wks | Depth* | Low vs detect close | Low (date) | 50w/200w at detect | Cycle at low | Bounce 1/2/4/8w | Days detect->low | Trap | Retest | 26w outcome |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for e in strict + ongoing:
        og = e in ongoing
        bn = "open" if og else "/".join(pct(e["bounce"][k]) for k in (1, 2, 4, 8))
        out.append(f'| {e["detect_date"].date()} | {e["streak_len"]} | {pct(e["depth"])} | {pct(e["low_vs_detect"])} | {e["low"]:,.0f} ({e["low_date"].date()}) | '
                   f'{ab(e["ma50_t"])}/{ab(e["ma200_t"])} | {e["cycle"]} ({e["days_peak"]}d post-peak) | {bn} | {e["days_trig_to_low"]} | '
                   f'{"-" if e["trap"] is None else ("Y" if e["trap"] else "N")} | {e["retest"]} | {"open" if og else e["outcome_short"]} |')
    out.append("\n*Depth = low vs highest weekly close of the 8 weeks before the trigger.\n")

    def agg(name, lst):
        vals = {k: [e["bounce"][k] for e in lst] for k in (1, 2, 4, 8)}
        tr = [e["trap"] for e in lst if e["trap"] is not None]
        oc = {k: sum(1 for e in lst if e["outcome_short"] == k) for k in ("UP", "LH", "LH+newlow")}
        dl = [e["days_trig_to_low"] for e in lst]
        return (f'| {name} | {len(lst)} | ' + " / ".join(pct(q(vals[k], 50)) for k in (1, 2, 4, 8)) + " | " +
                " ; ".join(pct(q(vals[k], 25)) + " to " + pct(q(vals[k], 75)) for k in (4, 8)) +
                f' | {np.median(dl):.0f} | {sum(tr)}/{len(tr)} | {oc["UP"]}/{oc["LH"]}/{oc["LH+newlow"]} |')

    out.append("## T2 outcome stats (bounce = max high after the low / low - 1)\n")
    out.append("| Set | n | Median bounce 1/2/4/8w | IQR 4w ; 8w | Median days detect->low | Bear trap Y/n | 26w UP / LH / LH+newlow |")
    out.append("|---|---|---|---|---|---|---|")
    out.append(agg("strict (a)+(b)", strict))
    out.append(agg("all (b) union (a), 2011+", hist))
    out.append(agg("all, 2014+", [e for e in hist if e["low_date"] >= pd.Timestamp("2014-01-01")]))
    out.append(agg("cycle label post-peak bear", [e for e in hist if e["cycle"] == "post-peak bear"]))
    out.append(agg("cycle label post-bottom base", [e for e in hist if e["cycle"] == "post-bottom base"]))
    out.append(agg("cycle label post-halving bull", [e for e in hist if e["cycle"] == "post-halving bull"]))
    rt = {}
    for e in hist:
        if e["swept"]:
            rt[e["retest"]] = rt.get(e["retest"], 0) + 1
    out.append(f'\nRetest outcomes where the prior swing low was undercut (n={sum(rt.values())}): {rt}\n')
    below200 = [e for e in hist if e["ma200_t"] is False]
    above200 = [e for e in hist if e["ma200_t"] is True]
    out.append(f'200w state at detect: above n={len(above200)} (UP {sum(e["outcome_short"] == "UP" for e in above200)}), '
               f'below n={len(below200)} (UP {sum(e["outcome_short"] == "UP" for e in below200)})\n')
    c = {}
    for e in hist:
        k = (e["cycle"], e["ma200_t"])
        c[k] = c.get(k, 0) + 1
    out.append(f'Regime mix counts (cycle label, above200w): {c}\n')

    out.append("## T3 level hit rates (within 2% of the episode low)\n")
    out.append("| Level type | Episodes with the level (n) | Hit | Hit % | Strict hit | Base rate: any weekly low, 2014-06+ | Median nearest dist |")
    out.append("|---|---|---|---|---|---|---|")
    ht = b.hit_table(d, w, hist)
    hs = b.hit_table(d, w, strict)
    for t, r in ht.items():
        s = hs.get(t, {"n": 0, "hit": 0})
        out.append(f'| {t} | {r["n"]} | {r["hit"]} | {pct(r["hit"] / r["n"] if r["n"] else float("nan"))} | {s["hit"]}/{s["n"]} | '
                   f'{pct(r["bhit"] / r["bn"] if r["bn"] else float("nan"))} (n={r["bn"]}) | '
                   f'{pct(float(np.median(r["dists"])) if r["dists"] else float("nan"), 1)} |')
    anyhit = 0
    for e in hist:
        ls = b.level_set(d, w, e["low"], e["low_date"])
        if any((b.within(e["low"], v)[1] or False) for t, v in ls.items() if not t.startswith("round")):
            anyhit += 1
    out.append(f'\nAt least one non-round level within 2%: {anyhit}/{len(hist)}\n')
    und26 = und52 = und6m = 0
    for e in hist:
        ls = b.level_set(d, w, e["low"], e["low_date"])
        und26 += int(bool(ls["range low 26w"]) and e["low"] < ls["range low 26w"][0])
        und52 += int(bool(ls["range low 52w"]) and e["low"] < ls["range low 52w"][0])
        win = d.loc[e["low_date"] - pd.Timedelta(days=182): e["low_date"] - pd.Timedelta(days=1), "low"]
        und6m += int(len(win) > 0 and e["low"] < win.min())
    out.append(f'Episode low below the 26w range low (days -182..-28): {und26}/{len(hist)}; below the 52w range low: {und52}/{len(hist)}; '
               f'below every daily low of the prior 6 months: {und6m}/{len(hist)} (no volume node can sit there).\n')
    h5 = b.hit_table(d, w, hist, tol=0.05)
    out.append('Within 5% instead of 2% (hit % vs base %): ' + '; '.join(
        f'{t} {pct(r["hit"] / r["n"] if r["n"] else float("nan"))} vs {pct(r["bhit"] / r["bn"] if r["bn"] else float("nan"))}'
        for t, r in h5.items()) + '\n')

    price = float(d["close"].iloc[-1])
    wk = w.iloc[-1]
    on = ongoing[0]
    L = b.level_set(d, w, price, NOW)
    out.append(f'## T4 today ({NOW.date()}; last Binance spot close {price:,.0f}; week open {wk["open"]:,.0f}; week low so far {wk["low"]:,.0f})\n')
    out.append("| Level type | Price(s) near | Distance from close |")
    out.append("|---|---|---|")
    for t, lv in L.items():
        near = sorted(sorted(lv, key=lambda x: abs(x / price - 1))[:6])
        out.append(f'| {t} | {", ".join(f"{x:,.0f}" for x in near)} | {", ".join(f"{(x / price - 1) * 100:+.1f}%" for x in near)} |')
    if on["swing_low"]:
        out.append(f'| prior swing low in force (26w before episode start) | {on["swing_low"]:,.0f} | {(on["swing_low"] / price - 1) * 100:+.1f}% |')
    s50, s200 = b.sma(w["close"], 50).iloc[-1], b.sma(w["close"], 200).iloc[-1]
    st = {"above50": price > s50, "above200": price > s200}
    out.append(f'\nNow: close vs 50w SMA {s50:,.0f}: {price / s50 - 1:+.1%}; vs 200w SMA {s200:,.0f}: {price / s200 - 1:+.1%}. '
               f'Completed red weeks: {on["streak_len"]} (+ current week red so far, open {wk["open"]:,.0f}); '
               f'depth to date {pct(on["depth"])} (at the 5th red close {pct(on["depth_detect"])}) from 8w high close {on["ref"]:,.0f}. '
               f'Days since peak 2025-10-06: {(NOW - pd.Timestamp("2025-10-06")).days}; since provisional bottom 2026-07-01: '
               f'{(NOW - pd.Timestamp("2026-07-01")).days}; since halving: {(NOW - pd.Timestamp("2024-04-20")).days}.\n')

    def score(e):
        s = abs(e["streak_len"] - 5) / 3 + abs(e["depth_detect"] - on["depth_detect"]) / 0.10
        s += 0 if e["ma50_t"] is None else float(e["ma50_t"] != st["above50"])
        s += 0 if e["ma200_t"] is None else float(e["ma200_t"] != st["above200"])
        s += 0 if e["cycle"] in ("post-peak bear", "post-bottom base") else 1
        return s

    rank = sorted([e for e in hist if e["low_date"] >= pd.Timestamp("2014-01-01")], key=score)[:6]
    out.append("## T5 closest analogues (OURS score: streak gap/3 + depth gap/10pp + 50w, 200w and cycle-label mismatches; 2014+)\n")
    out.append("| Score | Detect | Red wks | Depth | 50w/200w | Cycle | Low | Bounce 1/2/4/8w | Trap | 26w |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for e in rank:
        out.append(f'| {score(e):.1f} | {e["detect_date"].date()} | {e["streak_len"]} | {pct(e["depth"])} | {ab(e["ma50_t"])}/{ab(e["ma200_t"])} | '
                   f'{e["cycle"]} | {e["low"]:,.0f} ({e["low_date"].date()}) | {"/".join(pct(e["bounce"][k]) for k in (1, 2, 4, 8))} | {e["trap"]} | {e["outcome_short"]} |')
    rr = {k: [e["bounce"][k] for e in rank] for k in (1, 2, 4, 8)}
    out.append("\nAnalogue bounce ranges (min to max): " + "; ".join(f'{k}w {pct(min(v))} to {pct(max(v))}' for k, v in rr.items()))
    out.append(f'\nAnalogue 26w outcomes: {[e["outcome_short"] for e in rank]}\n')

    by = pd.read_csv(os.path.join(HERE, "data", "bybit_1d.csv"))
    by["date"] = pd.to_datetime(by["ts_ms"], unit="ms").dt.normalize()
    by = by.set_index("date")
    out.append("## Bybit BTCUSDT perp vs Binance spot lows (2020+, +-3 days)\n")
    out.append("| Low date | Binance spot | Bybit perp | Diff |")
    out.append("|---|---|---|---|")
    for e in hist + ongoing:
        if e["low_date"] >= by.index[0] + pd.Timedelta(days=10):
            m = float(by.loc[e["low_date"] - pd.Timedelta(days=3): e["low_date"] + pd.Timedelta(days=3), "low"].min())
            out.append(f'| {e["low_date"].date()} | {e["low"]:,.0f} | {m:,.0f} | {(m / e["low"] - 1) * 100:+.2f}% |')
    bw = by.loc["2026-11-09":]
    out.append(f'\nBybit this week: open {bw["open"].iloc[0]:,.0f}, low {bw["low"].min():,.1f}, last close {bw["close"].iloc[-1]:,.0f}. '
               f'Bybit weekly open 2026-10-05: {by.loc["2026-10-05", "open"]:,.0f}.')
    open(os.path.join(HERE, "tables.md"), "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
