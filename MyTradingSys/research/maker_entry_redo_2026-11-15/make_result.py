"""Builds RESULT.md from cells.csv (table only; the prose is fixed text checked against cells.csv by hand). Run: python make_result.py"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
d = pd.read_csv(HERE / "cells.csv")


def f(x, n=3):
    return format(x, "+.%df" % n)


rows = []
for _, r in d.iterrows():
    tk = f(r["tk_net"]) if r["arm"] == "BB" else "n/a"
    c = [r["arm"], r["cell"], int(r["signals"]), "%.1f%%" % (100 * r["fill_rate"]), "%d / %d" % (r["m_n"], r["m_days"]), f(r["m_gross"]), f(r["t_net"]),
         "%s [%s, %s]" % (f(r["m_net"]), f(r["m_ci_lo"], 2), f(r["m_ci_hi"], 2)), "%.3f" % r["holm_p"], f(r["w1_net"]), f(r["w2_net"]), tk,
         f(r["m_net_per_signal"]), f(r["t_net_per_signal"])]
    rows.append("| " + " | ".join(str(x) for x in c) + " |")
hdr = ("| arm | cell | signals | fill rate | maker n / fill days | maker gross % | T0 net % (parent entry) | maker net % [95% CI] | Holm p (m=21) | "
       "net 24-01..25-06 | net 25-07..26-11 | TK net % (1m touch control, BB) | net per signal M % | net per signal T0 % |\n" + "|---" * 14 + "|")
tab = hdr + "\n" + "\n".join(rows) + "\n"
n_imp = int((d["m_net_per_signal"] > d["t_net_per_signal"]).sum())
top = """Regime mix: 150 weeks: bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%)  (BTC, 2024-01-01..2026-11-14, research_kit.regime_tag; never bear in this window)

# RESULT maker_entry_redo_2026-11-15: maker (limit) entry vs taker entry, 10 symbols, 2024+ out of sample

**Verdict: NO EDGE. 0 of 21 pre-registered cells survive (survivors.json is []): the best maker cell nets -0.010 % per trade (WT 30m sell div, n 522, CI [-0.205, +0.185], Holm p 1.0); 13 of 21 maker nets have a CI entirely below zero (9 with Holm p < 0.05), none is positive. Maker entry beat the parent taker entry per signal in only @N@ of 21 cells (by 0.005 to 0.020 %) and lost in the other @M@ (by up to 0.36 %).** Power-qualified: the gate BLOCKs most cells (POWER_GATE.md ceiling wording): "NO EDGE, underpowered for a +0.30 % gross, INCONCLUSIVE ceiling", never an unqualified FAIL.

Pre-registration `PRE_REG.md` (frozen in 3d1d8910c before any cost-adjusted figure was read), code `study.py`, tests `test_study.py` (8; two mutations, a touch counted as a fill and a target hit allowed on the fill minute, each made one test fail). Costs imported: research_kit.TAKER_RT_PCT 0.14 % (T0 / TK) and research_kit.MAKER_IN_RT_PCT 0.09 % (maker entry, taker exit); no cost constant is defined here. Data: parents' Binance spot signal bars, shared Binance 1m archive for fills and exits; 10 symbols BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, signals 2024-01-01..2026-11-12 (cells overlap in signals).

## Context
Regime: BB = BTC RANGE (Malkan 60/40 band) with session-range tag; WT = the symbol's own daily SMA200 side agrees with the trade. Phase: BB range-to-range retest of the Bollinger band; WT dot with RSI or divergence confluence, dot-bar-midpoint retest. Session: BB asia / london / ny; WT pooled. Entry: resting limit at the parent's retest level (OURS fill model in PRE_REG.md). Parents unchanged.

## Table (2024+ is out of sample for both rules; day-clustered SE across symbols; Holm m = 21 on the maker p)
""".replace("@N@", str(n_imp)).replace("@M@", str(21 - n_imp))
mid = """
T0 = parent entry rule (touch fill on the signal timeframe, 0.14 %). TK = same 1m exit engine as the maker model with a touch fill and 0.14 % (BB only): the like-for-like taker control. M = limit filled only when a 1m bar trades through by one tick, fill at the limit, 0.09 %. Net per signal counts a miss as 0.

## What the maker model does (fill model and queue position are OURS and conservative: back of the queue = through by one tick, fill at the limit)
| Finding | Evidence |
|---|---|
| Fill rate is high, 83-98 %: the limits sit within a fraction of an ATR of the post-signal price (BB 90 / 94 / 98 % for k 0.25 / 0.5 / 1.0; WT 83-91 %) | fill rate column |
| Like for like (BB, M against TK) the maker entry gains the fee difference and nothing else: +0.043 to +0.050 % per filled trade (0.14 - 0.09 = 0.05 minus a few lost fills) | maker net minus TK net, all 9 BB cells |
| Against the PARENT entry (T0) maker is worse on BB, up to -0.36 % per signal at k = 1.0: the parent's 15m bracket never reads the rest of the fill bar, so its stops are optimistic; the 1m walk reads it (TK shows the same drop, gross -0.38 % at k = 1.0 with a touch fill). The T0 column is flattering; TK is the fair taker number | maker gross -0.488 to +0.006 vs T0 gross -0.084 to +0.057 (BB) |
| Adverse selection is small: the parent's gross over the maker-filled signals minus over all parent-filled ones is -0.021 to 0.000 % | cells.csv adverse_gross |
| WT (no stop, close exit after a fixed 12 bars): maker net per filled trade is within -0.10 to +0.02 % of T0 (worse in 10 of 12 cells, better in 2); the 0.05 % fee saving is eaten by filling exactly at the limit where the parent fills at the better open of a gap-through bar, and by the 9-17 % of signals that never fill | WT rows: maker net minus T0 net per filled trade |
| BB asia and ny at k = 0.5 and 1.0 are significantly NEGATIVE after Holm (p 0.000-0.001): a wider limit waits for a deeper pullback, by which time the reclaim has failed | BB rows |

## Questions
1. Does a resting limit entry improve fee-net results on the strategies already studied? **No.** It saves the 0.05 % fee difference per filled trade like for like, but no cell's maker net is above -0.010 %, and per signal (misses = 0) it beats the parent entry in @N@ of 21 cells.
2. Does any cell become a fee-net EDGE? **No**: 0 of 21. Every cell with Holm p < 0.05 is NEGATIVE.
3. Why: gross is about zero on these rules (BB maker gross -0.49 to +0.01 %, WT -0.51 to +0.08 %); the maker discount (0.05 %) is a third of the 0.14 % cost and cannot cover a zero gross. The gap is gross edge (about +0.30 % needed, EDGE_POSTMORTEM_1114), not execution.

## Replication of the parent
T0 reproduced on the parent window (signals to 2026-11-14): n 1882 / 1974 / 2046 (asia), 1428 / 1486 / 1547 (london), 1677 / 1771 / 1832 (ny) for k 0.25 / 0.5 / 1.0, identical to bb_range_retest_10sym_2026-11-15 RESULT; net -0.190, -0.185, -0.186 (asia), -0.093, -0.090, -0.085 (london), -0.223, -0.218, -0.208 (ny), equal to the parent to 3 decimals. WT T0 uses the parent functions unchanged (this study's window ends 2026-11-12, so n is slightly below the parent's).

## Caveats
- Fill model (through by one tick, fill at L even when a bar opens through it, back of the queue, no partial fills) is OURS; a front-of-queue order fills on a touch and would sit between M and the TK / T0 columns. No funding, no rebate; the target exit is taker (so the 0.09 % holds).
- 1m archive ends 2026-11-13 23:59 and has a few missing minutes per symbol: missing minutes can only remove fills, so fill rates are a lower bound.
- The BB parent's 15m bracket is optimistic (fill bar not read); this study's 1m walk is the more faithful engine, which is why BB maker gross is lower than the parent's.
- Only the confirmatory families of two parents were rerun; the maker-entry-1114 rows (NK2/3/5/6, value area, sweep) are not re-derived here (their 0 of 6 stays in git history). No independent checker agent was run; the tests and the T0 replication are the checks.

## Files
`MyTradingSys/research/maker_entry_redo_2026-11-15/`: PRE_REG.md, RESULT.md, study.py, test_study.py, make_result.py, counts.csv, cells.csv, survivors.json, regime_mix.txt. Holdout read logged in research/holdout_reads.csv.
""".replace("@N@", str(n_imp))
(HERE / "RESULT.md").write_text(top + tab + mid, encoding="utf-8", newline="\n")
