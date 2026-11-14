"""Render RESULT.md from the summary CSV/JSON written by analyze.py (no new statistics here except the descriptive 'now' block)."""
import os, sys, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phases as PH
import ctx as CX
import study as S


def f(x, d=3):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def now_block(summary, fr, V):
    """descriptive only: today's phase label (from BTC) and which kept cells are active for BTC/ETH at the latest cached bar."""
    now = summary["now"]
    rows = []
    for sym in ("BTC", "ETH"):
        a = S.load5(sym)
        df5 = S.df_from(a)
        spot, oi, fund = S.read_ctx_files(sym)
        # refresh spot 1d with nothing: context is as of the last cached 5m bar (stale by the cache age, stated below)
        c = CX.Ctx(df5, spot, oi, fund)
        T = int(a[-1, 0]) + S.MS5
        row = c.at([T]).iloc[0]
        rows.append((sym, pd.to_datetime(T, unit="ms"), row))
    lines = []
    pid = int(float(now["phase_id"])) if now["phase_id"] not in ("nan", "None") else 0
    lines.append(f"Today's label ({summary['now_date']}, from BTC closes through the previous day): **{now['phase']}** (cycle state {now['M']}, BTC 40d range position {float(now['pos40']):.2f}, RSI14d {float(now['rsi']):.1f}, drawdown from ATH {float(now['dd'])*100:.1f}%). Allowed direction in this phase: {'long' if PH.ALLOWED.get(pid)==1 else 'short' if PH.ALLOWED.get(pid)==-1 else 'both by range position'}.")
    kept = [(v, c) for v, cs in fr["kept"].items() for c in cs]
    if not kept:
        lines.append("No kept cell exists, so no cell is active. Descriptive only, not advice.")
        return "\n".join(lines), None
    act = []
    for v, c in kept:
        same = c["phase"] == pid
        for sym, T, row in rows:
            bk = int(row[f"b{c['layer']}"])
            act.append(dict(variant=v, cell=f"{PH.PHASES[c['phase']]} x C{c['layer']}={CX.LABELS['C'+str(c['layer'])][c['bucket']]}", symbol=sym,
                            phase_matches_today=same, bucket_now=("NO-DATA" if bk < 0 else CX.LABELS['C' + str(c['layer'])][bk]),
                            context_matches=(bk == c["bucket"]), ACTIVE=bool(same and bk == c["bucket"])))
    A = pd.DataFrame(act)
    ages = ", ".join(f"{s}: context read at {T:%Y-%m-%d %H:%M} UTC" for s, T, _ in rows)
    lines.append(f"Cell filter state per kept cell ({ages}; the 5m cache ends before today, so layer buckets are stale by that age). ACTIVE = today's phase and the layer bucket both match; the NK signal itself must also fire for a trade to exist.")
    return "\n".join(lines), A


def main():
    A = pd.read_csv(os.path.join(HERE, "stepA_phase_table.csv"))
    V = pd.read_csv(os.path.join(HERE, "val_kept_cells.csv"))
    D = pd.read_csv(os.path.join(HERE, "dev_cells_all.csv"))
    C = pd.read_csv(os.path.join(HERE, "layer_coverage.csv"))
    sm = json.load(open(os.path.join(HERE, "summary.json")))
    fr = json.load(open(os.path.join(HERE, "cells_frozen.json")))
    npass = int((V.verdict == "PASS").sum()) if "verdict" in V else 0
    nkept = len(V)
    if nkept == 0:
        verdict = "NO KEPT CELLS: no DEV cell met n>=150, >=40 days and a positive lower 90% bound, so nothing went to VAL (FAIL for both NK rules)."
    elif npass:
        verdict = f"PASS: {npass} of {nkept} DEV-kept cells passed every VAL gate (see table; one VAL regime, not a cycle law)."
    else:
        verdict = f"FAIL: 0 of {nkept} DEV-kept cells pass VAL (net R>0, CI low>0, ex-best-5>0, placebo p<0.05, BH q<0.10, n>=150)."
    L = [f"# RESULT nkp1-session-rules-phase-1114", "", f"**VERDICT: {verdict}**", ""]
    L += ["Rules: NK1 first-hour low break + VWAP (UTC and NY sessions, E3 session-end exit) and NK5 session open 15/10/5 (NY-asia, UTC-4h), 20 original coins each, taker 12 bp + funding, 6 bp maker row. Phase = BTC 6-phase label (causal, d-1 closes), 8 context layers, cells chosen on DEV (<=2023-12-31), frozen in git (code commit `%s`), run once on VAL (>=2024-01-01)." % fr["code_commit"][:9], ""]
    L += ["## Context", "", "Regime mix (share of BTC days per phase; VAL is a single regime, 2024-26):", ""]
    mix = pd.DataFrame({"DEV": sm["mix"]["DEV"], "VAL": sm["mix"]["VAL"]}).fillna(0)
    L += [md(mix.reset_index().rename(columns={"index": "phase"})), ""]
    L += [f"Cycle state M: DEV {sm['mix']['DEV_M']}, VAL {sm['mix']['VAL_M']}. Days: DEV {sm['mix']['DEV_days']}, VAL {sm['mix']['VAL_days']}. ONE-REGIME flag: " +
          ("VAL: " + ", ".join(k for k, v in sm['mix']['VAL'].items() if v > 0.85) if any(v > 0.85 for v in sm['mix']['VAL'].values()) else "none (no phase >85% in either split)"), ""]
    L += ["Trades (signals) by phase, all dates:", "", md(pd.DataFrame(sm["trade_phase_share"]).fillna(0).astype(int).reset_index().rename(columns={"index": "phase"})), ""]
    L += ["Sanity windows (not tuned; spec s1):", "", md(pd.DataFrame([dict(window=k, expected=v["expected"], share_expected=v["share_expected"], mix=v["mix"]) for k, v in sm["sanity_windows"].items()])), ""]
    L += [f"Median halving age (days) per phase (reported, not used): {sm['halving_age_median_by_phase']}", ""]
    L += ["## Step A: per-phase table (no pooled headline)", "",
          "net R at 12 bp + funding; gross R and cost R are per R (stop distance); app = phase-appropriate direction, opp = opposite (control); diff = app minus opp with day-cluster SE.", ""]
    for per in ("DEV", "VAL"):
        t = A[["variant", "phase"] + [c for c in A.columns if c.startswith(per + "_")]].copy()
        t.columns = ["variant", "phase", "n_app", "days_app", "gross_R", "cost_R", "net_R_app", "n_opp", "net_R_opp", "diff", "diff_se"]
        for c in ("gross_R", "cost_R", "net_R_app", "net_R_opp", "diff", "diff_se"):
            t[c] = t[c].map(f)
        L += [f"### {per}", "", md(t), ""]
    L += ["## DEV-chosen cells on VAL (kept cells only, run once)", ""]
    if nkept:
        t = V.copy()
        keep = ["variant", "phase", "layer", "bucket", "dev_n", "dev_net", "n", "days", "net", "ci_lo", "ci_hi", "gross", "costR", "ex5", "placebo_p", "bh_q", "shrink", "net_maker6", "verdict"]
        t = t[[c for c in keep if c in t.columns]]
        for c in t.columns:
            if t[c].dtype.kind == "f":
                t[c] = t[c].map(f)
        t = t.rename(columns={"dev_net": "DEV_net_R", "net": "VAL_net_R", "ci_lo": "day_CI_low", "ci_hi": "day_CI_high", "gross": "gross_R", "costR": "fee_funding_R", "ex5": "ex_best5", "shrink": "VAL-DEV", "net_maker6": "maker6bp_net_R"})
        L += [md(t), ""]
        cc = V[[c for c in ["variant", "phase", "layer", "bucket", "ctl_opp_n", "ctl_opp_net", "ctl_otherph_n", "ctl_otherph_net", "ctl_uncond_n", "ctl_uncond_net", "placebo_mean"] if c in V.columns]].copy()
        for c in cc.columns:
            if cc[c].dtype.kind == "f":
                cc[c] = cc[c].map(f)
        L += ["Control rows on VAL (opposite direction in the same cell; same bucket in the other 5 phases; the unconditional rule; placebo mean):", "", md(cc), ""]
        L += [f"DEV-kept cells that pass VAL: {npass} of {nkept}. Mean DEV-to-VAL shrinkage (VAL net R minus DEV net R): {f(float(V.shrink.mean()))}.", ""]
    else:
        L += ["No DEV cell qualified. Largest DEV scores (not eligible or score<=0):", "", md(D.sort_values('score', ascending=False).head(8).round(3)), ""]
    L += ["## Layer coverage (signals with data per layer)", "", md(C), ""]
    L += [f"Coins without a futures funding file: {sm['fund_missing_coins'] or 'none'}. First available context date per coin and layer is in summary.json (`ctx_first_avail`).", ""]
    L += ["## Useful trades now (descriptive only, no advice)", ""]
    txt, Act = now_block(sm, fr, V)
    L += [txt, ""]
    if Act is not None:
        L += [md(Act), ""]
    L += ["## Notes and limits", "",
          "- Phase is BTC-only, so effective n is days; 4 cycles only. VAL = one regime.",
          "- The shared phase table `F:\\MTS\\data_cache\\mts_brains\\phase_daily.csv` was built by another worker (git 5b21ebe34); this study uses its own committed `phases.py` and spot-verified it against the shared table: 97.2% label agreement over 2012-2026 (all differences are ACCUM-RANGE edges), cycle state 100%, last 30 days 100%.",
          "- All layer cutoffs except RSI 40/60 and WT +-53 are OURS. HM, the session mapping and C8 (constant per variant) are OURS.",
          "- Step A VAL rows that look positive (for example NK5-NYasia MARKDOWN short, NK1-NY DISTRIBUTION short, NK5-NYasia MARKUP/DISTRIBUTION) were NOT chosen on DEV; their DEV net R was negative. Reading them as edge would be selecting on VAL, so they are descriptive only. Where the appropriate-minus-opposite difference is under ~1.5 SE it is noise.",
          "- C2 (WaveTrend) values exist only after the 200-bar warm-up; the first-available date in summary.json is the first bar, not the first valid value. C4 (OI) starts 2021-12 for all coins (Binance published metrics from then), so C4 cells have no 2019-2021 DEV data. C6 had no data at the 'now' read (stale cache).",
          "- Coins: NK1 uses its original 20, NK5 its original 20 (union 23 incl. EOS, DASH, IOTA; EOS ends 2025-05, so NK5 EOS has no VAL rows; EOS/DASH/IOTA have no NK1 pool).",
          "- E1/E2 exits of NK1 and three NK5 rows were dropped to keep cells at 144 per variant.", ""]
    open(os.path.join(HERE, "RESULT.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L)[:4000])


if __name__ == "__main__":
    main()
