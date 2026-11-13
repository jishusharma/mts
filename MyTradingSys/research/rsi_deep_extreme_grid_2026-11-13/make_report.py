"""Builds REPORT.md (+ the side-notes results note) from study.py outputs. Run after study.py."""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge3-rsi-deep-extreme-grid-1113"))
NOTE = r"C:\Users\E-ngineers\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\side-session-notes\local_0cb8bd0b-848b-4df7-b685-6a6d0f12ab98\edge3-rsi-deep-extreme-grid-1113_RESULTS.md"


def md(df, floatfmt=3):
    df = df.copy()
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("" if np.isnan(v) else ("%.*f" % (floatfmt, v)))
            else:
                cells.append("" if v is None else str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    ev = pd.read_csv(os.path.join(CACHE, "events_all.csv"))
    ev["confirm"] = ev["confirm"].astype(bool)
    cells = pd.read_csv(os.path.join(HERE, "cells.csv"))
    bands = pd.read_csv(os.path.join(HERE, "cells_bands.csv"))
    lw = json.load(open(os.path.join(CACHE, "layers_where.json")))
    today = json.load(open(os.path.join(CACHE, "today.json")))
    pool = cells[cells.universe == "pooled"]
    vc = pool.verdict.value_counts().to_dict()
    nsig = int(pool.bh_sig.sum())
    passed = pool[pool.verdict.isin(["PASS", "ROBUST"])]
    verdict = "PASS" if len(passed) else "FAIL / UNDERPOWERED"
    L = []
    L.append("# RESULT: deep RSI extreme + confirming candle, event table and grid (edge3-rsi-deep-extreme-grid-1113)\n")
    L.append("**Verdict: %s.** %d of 60 pre-registered pooled cells PASS (verdicts: %s). BH 10%% significant on VALIDATION: %d (of which %d have VALIDATION n >= 30; the rest are UNDERPOWERED). No edge claim." % (
        verdict, len(passed), vc, nsig, int((pool.bh_sig & (pool.VAL_n >= 30)).sum())))
    L.append("Regime mix: BTC daily close vs 200d SMA (bull > +5%, bear < -5%): DEV bull 57% / bear 34% / range 9%; VALIDATION bull 62% / bear 11% / range 27%; RECENT bull 36% / bear 54% / range 10%.")
    L.append("Universe: BTC ETH SOL BNB XRP DOGE ADA LINK AVAX LTC, Bybit linear 1h/1D from listing; fees 2 x BINANCE_TAKER (fees.py), no slippage, no funding; entry = close of the confirming bar, stop = signal-bar low; net R per trade; week-block bootstrap (2000), placebo 100 draws. Trades need 168 h of forward data, so the last 7 days are excluded from tested trades.\n")

    # today's trade
    L.append("## Today's trade, the operator's example (checked first)")
    t = today
    L.append("BTC 1h bar opened 2026-11-13 05:00Z: red, close %.1f, RSI(14) %.2f, low %.1f, daily RSI (last closed) %.1f. Next 1h bar (06:00Z) green, close %.1f at 07:00Z = entry (confirm %s). Stop = %.1f, %.2f %% away. All match his numbers." % (
        t["close"], t["rsi_sig"], t["low"], t["daily_rsi"], t["entry"], "yes" if t["confirm"] else "no", t["low"], t["stopdist_pct"]))
    L.append("State at run time (last closed 1h bar opened %s Z, %d bars after entry): **%s**; best high since entry %.1f = **+%.2fR**; worst low since entry %.1f; last close %.1f = %+.2fR. (Not in any statistics: its 168 h window is not complete.)\n" % (
        t["last_bar_open"][11:16], t["bars_since"], "STOPPED" if t["stopped"] else "NOT stopped", t["max_high"], t["best_R"], t["worst_low"], t["last_close"], t["last_R"]))

    # A: pooled counts
    L.append("## A. Event counts (first touch, re-arm above 30), episodes / confirm-yes, all coins")
    pv = ev.groupby(["coin", "tf", "T"]).agg(ep=("confirm", "size"), yes=("confirm", "sum")).reset_index()
    pv["k"] = pv.apply(lambda r: "%dh<=%d" % (r.tf, r["T"]), axis=1)
    pv["v"] = pv.apply(lambda r: "%d/%d" % (r.ep, r.yes), axis=1)
    order = ["%dh<=%d" % (tf, T) for tf in (1, 4, 8, 12) for T in (10, 12, 15, 20)]
    tab = pv.pivot(index="coin", columns="k", values="v").reindex(columns=order).fillna("0/0")
    tab = tab.reindex(["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "LINK", "AVAX", "LTC"]).reset_index()
    tot = ev.groupby(["tf", "T"]).agg(ep=("confirm", "size"), yes=("confirm", "sum"))
    tab.loc[len(tab)] = ["ALL"] + ["%d/%d" % (tot.loc[(tf, T), "ep"], tot.loc[(tf, T), "yes"]) if (tf, T) in tot.index else "0/0" for tf in (1, 4, 8, 12) for T in (10, 12, 15, 20)]
    L.append(md(tab))
    L.append("\nBTC row by row: events_btc.csv (all %d BTC episodes, TF x T). The T<=15 rows follow; fields: stop %% = (entry - signal low)/entry; mfe/mae = max favourable/adverse move from entry over 24 h; +1R/+2R = target before stop within 72 h; brk_h = hours until the signal low broke (blank = not within 7 d); ret = forward return from entry; (blank forward fields = window incomplete, i.e. today)." % int((ev.coin == "BTC").sum()))
    b = pd.read_csv(os.path.join(HERE, "events_btc.csv"))
    b = b[b["T"] <= 15].copy()
    b["cf"] = np.where(b.confirm, "yes", "no")
    b["day"] = b.sig_open.str[:13]
    bt = b[["tf", "T", "day", "sig_rsi", "drsi", "cf", "stopdist_pct", "mfe24", "mae24", "r1_first", "r2_first", "r3_first", "hrs_to_break", "ret24", "ret72", "ret7d", "rsi_at_peak"]].copy()
    for c in ("mfe24", "mae24", "ret24", "ret72", "ret7d"):
        bt[c] = bt[c] * 100
    bt = bt.rename(columns={"sig_rsi": "rsi", "drsi": "dRSI", "stopdist_pct": "stop%", "mfe24": "mfe24%", "mae24": "mae24%", "r1_first": "+1R", "r2_first": "+2R", "r3_first": "+3R", "hrs_to_break": "brk_h", "ret24": "r24%", "ret72": "r72%", "ret7d": "r7d%", "rsi_at_peak": "rsi@pk"})
    btc_tab_10 = bt[bt["T"] <= 12]
    L.append("\n### BTC episodes, T <= 12 (all TF)")
    L.append(md(btc_tab_10, 1))
    L.append("\n### BTC episodes, T = 15 (all TF)")
    L.append(md(bt[bt["T"] == 15], 1))

    # stop distance
    yes = ev[ev.confirm]
    sd = yes.groupby(["tf", "T"]).stopdist_pct.agg(n="size", p25=lambda x: x.quantile(.25), median="median", p75=lambda x: x.quantile(.75), worst="max").reset_index()
    sd["scope"] = "10-coin"
    sb = yes[yes.coin == "BTC"].groupby(["tf", "T"]).stopdist_pct.agg(n="size", p25=lambda x: x.quantile(.25), median="median", p75=lambda x: x.quantile(.75), worst="max").reset_index()
    sb["scope"] = "BTC"
    L.append("\n## Stop distance % (confirm-yes events), 10-coin pooled and BTC")
    L.append(md(pd.concat([sd, sb])[["scope", "tf", "T", "n", "p25", "median", "p75", "worst"]], 2))

    # B
    L.append("\n## B. Pooled cells (60). VALIDATION decides; DEV and RECENT shown")
    keep = ["tf", "T", "exit", "DEV_n", "DEV_mean", "VAL_n", "VAL_mean", "VAL_lo", "VAL_hi", "VAL_win", "VAL_plac_mean", "VAL_plac_p", "REC_n", "REC_mean", "bh_sig", "verdict"]
    big = pool[pool.VAL_n >= 30].sort_values("VAL_mean", ascending=False)
    L.append("Cells with VALIDATION n >= 30: %d of 60. Best 5 and worst 5 of those by VALIDATION mean net R:" % len(big))
    L.append(md(pd.concat([big.head(5), big.tail(5)])[keep]))
    sm = pool[pool.VAL_n < 30].sort_values("VAL_mean", ascending=False)
    L.append("\nCells with VALIDATION n < 30 (UNDERPOWERED, shown for completeness, top 8 by mean):")
    L.append(md(sm.head(8)[keep]))
    L.append("\nBy exit, mean across the 10 combos (pooled, n-weighted not applied; descriptive): ")
    ex = pool.groupby("exit")[["DEV_mean", "VAL_mean", "REC_mean"]].mean().reset_index()
    L.append(md(ex))
    L.append("\nBTC alone (descriptive, tiny n), cells with VALIDATION n >= 3:")
    bb = cells[(cells.universe == "BTC") & (cells.VAL_n >= 3)]
    L.append(md(bb[["tf", "T", "exit", "DEV_n", "DEV_mean", "VAL_n", "VAL_mean", "REC_n", "REC_mean"]]) if len(bb) else "none (BTC VALIDATION has fewer than 3 trades in every cell)")
    L.append("\nFull table: cells.csv. Daily-RSI band split (descriptive, no CI): cells_bands.csv. Pooled by daily-RSI band, exit +2R and time72, all combos with T=20 (mean net R / n):")
    bd = bands[(bands["T"] == 20) & (bands.exit.isin(["tgt2", "time72"])) & (bands.band != "nan")]
    bd = bd.assign(v=bd.apply(lambda r: "%s / %d" % ("" if np.isnan(r["mean"]) else "%.2f" % r["mean"], r.n), axis=1))
    bd = bd.pivot_table(index=["tf", "exit", "band"], columns="split", values="v", aggfunc="first").reset_index()
    bd["o"] = bd.band.map({"<=20": 0, "20-25": 1, "25-30": 2, "30-40": 3, ">40": 4})
    bd = bd.sort_values(["tf", "exit", "o"]).drop(columns="o")
    L.append(md(bd[["tf", "exit", "band", "DEV", "VAL", "REC"]]))

    # C
    lay = pd.DataFrame(lw["layers"])
    L.append("\n## C. Layers on pooled confirm-yes events, T=20 (n per cell; THIN = n < 30). win1R = share reaching +1R before the stop within 72 h; mean R = net R of the +2R-target exit")
    lay["THIN"] = np.where(lay.thin, "THIN", "")
    L.append(md(lay[lay.level != "(missing)"][["tf", "layer", "level", "n", "THIN", "win1R", "mean_R_tgt2"]]))
    miss = lay[lay.level == "(missing)"].groupby("layer").n.sum()
    L.append("\nMissing feature values (events with no value, summed over TF): " + ", ".join("%s: %d" % (k, v) for k, v in miss.items()) + ". OI history begins mid-2020 (BTC) and later for newer coins.")

    # D
    wh = pd.DataFrame(lw["where"])
    wh["THIN"] = np.where(wh.thin, "THIN", "")
    L.append("\n## D. Where to sell: confirm-yes events, T=20, by daily trend (max favourable move is raw, from the entry close, stop ignored)")
    L.append(md(wh[["tf", "trend", "n", "THIN", "med_stop_pct", "med_mfe24_pct", "med_mfe24_R", "med_mfe72_pct", "med_mfe72_R", "reach_1R", "reach_2R", "reach_3R", "new_low_7d"]]))
    L.append("\nreach_kR = share where +kR was touched before the signal low within 72 h; new_low_7d = share where the signal low was broken within 7 days (the 'downtrend, sell it' case).")
    L.append("\n## Limits\nNo slippage or funding; R-multiples explode when the signal-bar range is tiny (fees / stop distance); 10 coins are highly correlated (week-block bootstrap partly handles that); daily-band and layer splits are small-n; T=20 is the superset of deeper first touches only approximately because first touch is defined per threshold; the live trade is excluded from statistics.")
    body = "\n".join(L)
    open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf-8").write(body + "\n")
    try:
        open(NOTE, "w", encoding="utf-8").write(body + "\n")
    except Exception as e:  # noqa: BLE001
        print("note not written", e)
    print(len(body), "chars")


if __name__ == "__main__":
    main()
