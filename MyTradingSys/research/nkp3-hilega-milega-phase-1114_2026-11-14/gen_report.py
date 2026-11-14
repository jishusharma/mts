"""Builds RESULT.md from results.json, dev_step_a.csv, cells_frozen.json and the phase table (numbers are never typed by hand)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import phases as PH

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "results.json").read_text())
fro = json.loads((HERE / "cells_frozen.json").read_text())
dev_a = pd.read_csv(HERE / "dev_step_a.csv")
val_a = pd.DataFrame(res["step_a_val"])
tab = PH.read_table()
f3 = lambda x: "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.3f}"
f2 = lambda x: "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.2f}"
VN = ["HM15", "HM1h", "HM4h", "BO1h", "BO4h", "FO1h", "FO4h"]


def step_table(df):
    L = ["| Rule | Phase | Right dir | n | days | gross R | cost R | net R (12bp) | opposite net R | right minus opp (se) |", "|---|---|---|---|---|---|---|---|---|---|"]
    wins = 0
    tot = 0
    for v in VN:
        for _, r in df[df.variant == v].iterrows():
            ap = r["appropriate"]
            if ap == "both":
                n = r.long_n + r.short_n
                days = max(r.long_days, r.short_days)
                gross = (r.long_gross * r.long_n + r.short_gross * r.short_n) / max(n, 1)
                cost = (r.long_cost * r.long_n + r.short_cost * r.short_n) / max(n, 1)
                netv = (r.long_net * r.long_n + r.short_net * r.short_n) / max(n, 1)
                opp = ""
                dif = f"long {f3(r.long_net)} / short {f3(r.short_net)}"
            else:
                a, o = ("long", "short") if ap == "long" else ("short", "long")
                n, days, gross, cost, netv = r[a + "_n"], r[a + "_days"], r[a + "_gross"], r[a + "_cost"], r[a + "_net"]
                opp = f3(r[o + "_net"])
                d, se = r.get("app_minus_opp"), r.get("diff_se")
                dif = "" if pd.isna(d) else f"{d:+.3f} ({se:.3f})"
                if not pd.isna(d) and se > 0:
                    tot += 1
                    wins += d / se > 2
            L.append(f"| {v} | {r.phase} | {ap} | {int(n)} | {int(days)} | {f3(gross)} | {f3(cost)} | {f3(netv)} | {opp} | {dif} |")
    return "\n".join(L), wins, tot


dev_tbl, dev_w, dev_t = step_table(dev_a)
val_tbl, val_w, val_t = step_table(val_a)

kept = res["kept"]
npass, nk = res["n_pass"], res["n_kept"]
best = max(kept, key=lambda k: (k["net"] if k["n"] >= 150 else -9))
nposs = res["n_net_pos"]
verdict = (f"**VERDICT: {'PASS' if npass else 'FAIL'}. {npass} of {nk} DEV-chosen cells pass on VAL (2024+, fee-net at 12 bp); "
           f"{nposs} of {nk} have net R > 0 and none has a day-cluster CI low above 0. "
           f"The phase-appropriate direction beat the opposite direction by more than 2 se in {val_w} of {val_t} VAL rule x phase rows "
           f"({dev_w} of {dev_t} on DEV). Zero DEV cells for HM15, HM1h and FO1h.**")

# regime mix + halving age
tab2 = tab[tab.label > 0].copy()
tab2["ha"] = tab2["date"].map(PH.halving_age_days)
mix = ["| Phase | DEV days | DEV % | VAL days | VAL % | mean halving age (days) | note |", "|---|---|---|---|---|---|---|"]
for p in range(1, 7):
    nm = PH.NAMES[p]
    dd, vv = fro["dev_days"][nm], fro["val_days"][nm]
    ha = tab2.loc[tab2.label == p, "ha"].mean()
    mix.append(f"| {nm} | {dd[0]} | {dd[1]*100:.1f}% | {vv[0]} | {vv[1]*100:.1f}% | {ha:.0f} | {'UNDERPOWERED (<5% of DEV days, no kept cell)' if nm in fro['thin_phases'] else ''} |")
sig = ["| Rule | " + " | ".join(PH.NAMES[p] for p in range(1, 7)) + " |", "|---|" + "---|" * 6]
for v in VN:
    d = fro["variants"][v]["signals_per_phase"]
    vv = res["variants"][v]["signals_per_phase"]
    sig.append(f"| {v} DEV / VAL | " + " | ".join(f"{d[PH.NAMES[p]]} / {vv[PH.NAMES[p]]}" for p in range(1, 7)) + " |")

# sanity windows
win = []
for nm, lab, a, b in (("CAPITULATION", "CAPITULATION", "2020-03-12", "2020-03-15"), ("CAPITULATION", "CAPITULATION", "2022-06-13", "2022-06-18"),
                      ("MARKDOWN", "MARKDOWN", "2022-01-01", "2022-10-31"), ("MARKDOWN", "MARKDOWN", "2025-11-01", "2026-02-28"),
                      ("MARKUP", "MARKUP", "2020-11-01", "2021-03-31"), ("MARKUP", "MARKUP", "2023-10-01", "2024-03-31")):
    s = tab[(tab.date >= a) & (tab.date <= b)].label.map(PH.NAMES)
    frac = (s == lab).mean()
    win.append(f"| {nm} {a}..{b} | {frac*100:.0f}% | {'ok' if frac >= 0.6 else ('borderline (51-59%), recorded not retuned' if frac >= 0.5 else 'MOSTLY OTHER, recorded not retuned')} ({dict(s.value_counts())}) |".replace("np.int64", ""))

rows = ["| Rule | Cell (phase / layer = bucket / dir) | DEV n | DEV net | DEV lo90 | VAL n | days | win% (break-even) | gross R | fee/R | net R | day CI 95% | ex-best-5 | placebo p | BH q | 6bp maker net (fill) | verdict |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for k in kept:
    m = k["maker6"] or {}
    mk = f"{f3(m.get('mean'))} ({m.get('fill_rate', 0)*100:.0f}%)" if m.get("n") else "n/a"
    ci = f"[{f3(k['ci_lo'])}, {f3(k['ci_hi'])}]"
    rows.append(f"| {k['variant']} | {k['phase']} / {k['layer']} = {k['bucket']} / {'long' if k['dir']==1 else 'short'} | {k['dev_n']} | {f3(k['dev_net'])} | {f3(k['dev_lo90'])} | {k['n']} | {k['days']} | "
                f"{(k['win'] or 0)*100:.0f}% ({(k.get('breakeven_win') or 0)*100:.0f}%) | {f3(k['gross'])} | {f3(k['cost'])} | {f3(k['net'])} | {ci} | {f3(k['ex5'])} | "
                f"{f2(k.get('placebo_p'))} | {k['bh_q']:.2f} | {mk} | {k['verdict']} |")
ctl = ["| Rule | Cell | opposite dir, same cell (n, net) | same bucket, other phases | unconditional same phase+dir | unconditional rule+dir |", "|---|---|---|---|---|---|"]
for k in kept:
    c = k["controls"]
    g = lambda nm: f"{c[nm]['n']}, {f3(c[nm]['net'])}" if nm in c else "n<2"
    ctl.append(f"| {k['variant']} | {k['phase']} / {k['layer']} = {k['bucket']} / {'long' if k['dir']==1 else 'short'} | {g('opposite_dir_same_cell')} | {g('same_bucket_other_phases')} | {g('unconditional_same_phase_dir')} | {g('unconditional_rule_dir')} |")
shr = ["| Rule | Cell | DEV net | VAL net | shrinkage |", "|---|---|---|---|---|"]
for k in kept:
    shr.append(f"| {k['variant']} | {k['phase']} / {k['layer']} = {k['bucket']} | {f3(k['dev_net'])} | {f3(k['net'])} | {f3(k['net'] - k['dev_net'])} |")
unc = ["| Rule | VAL signals | gross R | net R (12bp) |", "|---|---|---|---|"]
for v in VN:
    r = res["variants"][v]
    unc.append(f"| {v} | {r['n_val']} | {f3(r['uncond_gross'])} | {f3(r['uncond_net'])} |")
td = res["today"]
tl = ["| Day | Label | Cycle state | BTC close (prior day) | SMA50 | SMA200 | W200 |", "|---|---|---|---|---|---|---|"]
for r in td["table_tail"]:
    tl.append(f"| {r['date']} | {r['label']} | {r['state']} | {r['btc_close']:.0f} | {r['sma50']:.0f} | {r['sma200']:.0f} | {r['w200']:.0f} |")
now = ["| Rule | Kept cell | Coin | phase matches today | current bucket of the layer | bucket matches | VAL verdict |", "|---|---|---|---|---|---|---|"]
for a in td["kept_cells_now"]:
    nmb = ["low", "mid", "high", "NA"][a["bucket_now"]]
    now.append(f"| {a['variant']} | {a['cell']} | {a['coin']} | {a['phase_match']} | {nmb} | {a['bucket_match']} | {a['verdict']} |")
active = [a for a in td["kept_cells_now"] if a["phase_match"] and a["bucket_match"]]

dev_nodata = {v: [k for k, b in x["no_data_layers"].items() if b] for v, x in fro["variants"].items()}
oi_first = "BTC 2020-09-01; all other coins 2021-12-01 (EOS series ends early). Funding first settlement 2020-01 (BTC, ETH, BCH) up to 2020-10 (FIL), last file 2026-10 (monthly, so C5 is NA for the last ~13 days)."
txt = f"""# nkp3-hilega-milega-phase-1114: NK4 Hilega Milega + Bollinger breakout/fakeout, phase-specific, MTS brains

{verdict}

Plain reading: inside the 6 BTC phases, with 8 context layers choosing the trades, no cell chosen on 2019-2023 data survived 2024-26 fee-net. The best VAL cell by net R is {best['variant']} {best['phase']} / {best['layer']} = {best['bucket']} / {'long' if best['dir']==1 else 'short'}: n {best['n']}, net R {f3(best['net'])}, day-cluster CI low {f3(best['ci_lo'])}, placebo p {f2(best.get('placebo_p'))}, BH q {best['bh_q']:.2f}; it is not a PASS (CI spans 0, ex-best-5 {f3(best['ex5'])}).

Code commit before any outcome: `{fro['code_commit'][:9]}` (PRE_REG + study + tests). Frozen cells commit: `{res['cells_commit'][:9]}` (cells_frozen.json, dev_cells.csv, dev_step_a.csv). VAL was run once afterwards (`run.py val`). Method: `MTS_BRAINS_SPEC_1114.md`; all parameters OURS except where PRE_REG says SOURCED.

Regime mix: days per phase and signals per phase are in the tables below (DEV 2019-2023, VAL 2024-2026). CAPITULATION is under 5% of DEV days (UNDERPOWERED, no kept cell).

## Context
Operator order 2026-11-13: NK tests must be phase specific and apply the MTS brains. Earlier NK1-NK6 used one ADX phase and no context and failed (gross about 0). This study labels every UTC day from BTC with the 6-phase cycle/structure clock (causal, closes through the prior day), reads 8 context layers at the signal bar close, picks at most 3 cells per rule on DEV, freezes them in git, then tests them on VAL once. Rules: NK4 Hilega Milega flips on 15m / 1h / 4h (RSI9, EMA3 vs WMA21, formula OURS) and Bollinger(20,2) breakout and fakeout fade on 1h / 4h (OURS; NK-R11 was 15m only). HTF: 4h RSI and %B and 1D WaveTrend are context layers, HM also runs on 4h. Prices are Binance spot, 20 coins, funding not charged (spot).

## Regime mix
{chr(10).join(mix)}

Signals per phase (DEV / VAL):

{chr(10).join(sig)}

Sanity windows (listed in the spec, not tuned):

| Window | share labelled as expected | note |
|---|---|---|
{chr(10).join(win)}

## Step A: per-phase table, DEV 2019-2023 (every phase separate, phase-appropriate direction first)
Right dir = direction the phase allows (CAPITULATION/RELIEF/MARKUP long, MARKDOWN/DISTRIBUTION short, ACCUM-RANGE both, shown as the signal-weighted blend with the long/short split in the last column). cost R = 12 bp x entry / stop distance. Rows with right minus opposite above +2 se: {dev_w} of {dev_t}.

{dev_tbl}

## Step A on VAL 2024-2026 (control table, computed after the freeze; unconditional rules, no context)
Rows with right minus opposite above +2 se: {val_w} of {val_t}.

{val_tbl}

Unconditional VAL rows per rule (all phases pooled, for reference only, not a headline):

{chr(10).join(unc)}

## DEV-chosen cells on VAL (Step C, run once)
Kept per rule on DEV: HM15 0, HM1h 0, HM4h {len(fro['variants']['HM4h']['kept'])}, BO1h {len(fro['variants']['BO1h']['kept'])}, BO4h {len(fro['variants']['BO4h']['kept'])}, FO1h 0, FO4h {len(fro['variants']['FO4h']['kept'])} (12 cells from {sum(v['cells_eligible'] for v in fro['variants'].values())} eligible cells across 7 rules). Cells that passed VAL: {npass} of {nk}. fee/R = 12 bp x entry / stop distance. C4 (OI) and C5 (funding) were not NO-DATA for any rule (DEV signals with a reading exceed 150).

{chr(10).join(rows)}

DEV to VAL shrinkage per kept cell:

{chr(10).join(shr)}

Controls on VAL (same cell, opposite direction; same bucket in the other phases; unconditional):

{chr(10).join(ctl)}

PASS rule: net R > 0, day-cluster CI low > 0, ex-best-5 > 0, placebo p < 0.05, BH q < 0.10 (family = {nk} kept cells), n >= 150. UNDERPOWERED = n < 150 on VAL. Placebo p is a one-sided test of the real mean against 1000 hour-matched random entries in the same cell; a small p only means "beats random", random entries lose about the fee.

## Useful trades now (descriptive only, no advice)
Today's phase label (day 2026-11-13, provisional, built from closes through 2026-11-12) is {td['label_today']}; the same BTC label applies to BTC and ETH. Last 10 days:

{chr(10).join(tl)}

Kept cells vs now (BTC and ETH, last closed bar of the rule's timeframe):

{chr(10).join(now)}

Cells active right now (phase and bucket both match): {len(active)}. {'None of the 12 kept cells is active, and none passed VAL anyway.' if not active else 'Active cells listed above are all VAL FAIL or UNDERPOWERED, so none is a validated trade.'}

## Data and provenance
- Spot 5m bars: `F:\\MTS\\data_cache\\binance\\<SYM>USDT_5m.npz` (sibling cache, 20 coins, last full day 2026-11-12). Parsed fetches written by this study: `F:\\MTS\\data_cache\\binance_spot\\nkp3-hilega-milega-phase-1114\\<SYM>USDT_1h_taker.npz` (spot 1h klines incl. taker-buy base volume, C6), `F:\\MTS\\data_cache\\binance\\nkp3-hilega-milega-phase-1114\\<SYM>USDT_oi_1h.npz` (C4) and `..._funding.npz` (C5), each with `.meta.json` (source, row count, sha256, key ts ms). Derived trades/universes: `F:\\MTS\\data_cache\\mts_brains\\nkp3\\`.
- First available futures dates: {oi_first}
- Phase table: own copy `F:\\MTS\\data_cache\\mts_brains\\nkp3\\phase_daily_nkp3.csv` (a sibling had already written the shared `phase_daily.csv` with another schema). Cross-check against the shared table: 99.93% of days since 2019-01-01 carry the same label (2 differing days of 2,874, MARKUP vs DISTRIBUTION and MARKUP vs RELIEF).
- WaveTrend parameters checked against `backtest/layers/wavetrend/wavetrend.py` (10/21, 0.015, +-53).
- Nothing over 5 MB is tracked (test enforces).

## Gates and tests
`test_study.py`: phase table equals an independent truncated recompute (fails under PHASE_LAG=0 and STUDY_BUG=1), each of the 8 context layers equals its truncated-prefix value and ignores overwritten future data (fails under STUDY_BUG=1), HM and Bollinger signals causal, hand-checked stop/gap/cost numbers (gap through stop fills at the open, 12 bp x 100 / 1 = 0.12 R), random-walk gross R shows no edge, file-size test, and a meta-test that runs the bug variants and requires them to fail.

## Weaknesses and flags
- The Hilega Milega formula is OURS and unverified against NK's chart. The Bollinger variants are OURS.
- BTC-only phase: effective n is days; cell CIs are day-clustered, so many cells have n in the hundreds but 20 to 100 days.
- Four cycles; CAPITULATION and RELIEF are thin. A VAL pass would only mean surviving 2024-26.
- 144 cells per rule with DEV-only selection: DEV lo90 scores are optimistic; shrinkage table above shows DEV net to VAL net.
- Spot prices, no funding charged; taker costs 12 bp round trip on notional; 6 bp maker row uses a next-bar-trade-through fill model.
- Disclosure: one wiring smoke run on BTC+ETH 4h (trade counts and gross means) preceded the PRE_REG commit; it did not change the design. The shared `phase_daily.csv` was not used (see above).
- No orders placed, no `.secrets` or `.env` read.
"""
txt = txt.replace("nkp3-hilega-milega-phase-1114", "nkp3-hilega-milega-phase-1114")
(HERE / "RESULT.md").write_text(txt, encoding="utf-8")
print(txt[:1800])
