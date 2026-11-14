# RESULT: reclaim at the close, stop = close back beyond the level, 10 symbols, OOS 2024-01..2026-11 (PRE_REG.md frozen before any return)

Regime mix: 150 weeks: bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%)

**Verdict: NO EDGE.** Fee-net at 0.14 % round trip (research_kit.TAKER_RT_PCT) the rule loses on 4h and is indistinguishable from zero on 1D. Underpowered by the gate (POWER_GATE.md: 4h MDE 0.299 + cost 0.14 vs 0.30 plausible), so the strongest wording is NO EDGE, INCONCLUSIVE ceiling, not an unqualified FAIL.

| arm (10 symbols pooled, sides pooled) | n | days | gross % | net % | day-clustered SE % | t | p | Holm p (m=2) | net 2024-01..2025-06 | net 2025-07..2026-11 | EDGE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4h | 1345 | 639 | +0.004 | -0.136 | 0.109 | -1.25 | 0.21 | 0.42 | -0.126 | -0.145 | no |
| 1D | 200 | 135 | +0.218 | +0.078 | 0.577 | +0.14 | 0.89 | 0.89 | -0.170 | +0.298 | no |

- 4h: gross is zero (+0.004 %), so the 0.14 % cost alone makes net negative; 57 % of trades end on the level stop, win rate 35 %, mean hold 3.9 bars. Both sub-windows negative. Range regime -0.216 % (n 858), bull +0.005 % (n 487), bear 0 events (BTC never in the bear regime in this window).
- 4h per side: long after low-break reclaim n 680, net -0.204 %; short after high-break n 665, net -0.067 %. Per symbol net: SOL +0.245, XRP +0.260, DOGE +0.174, LINK +0.047, rest negative (AVAX -0.709, BNB -0.379, BTC -0.289); no symbol is individually significant at p < 0.01 (AVAX p 0.012, BNB p 0.023 are the negative ones). Descriptive only, not verdict cells.
- 1D: sub-windows disagree in sign (-0.170 / +0.298); the short side +0.895 % (n 98, p 0.17) vs long -0.707 % (n 102) is noise-sized (SE 0.65-0.93 %). n 200 is below nothing the gate can power.
- vs the BTC-only study (DEV 2022-01..2024-06, 4h n 114, net +0.271 % at 0.10 %): that point estimate did not replicate. BTC alone in 2024+ is n 140, net -0.289 %; the pooled 10-symbol 4h net is -0.136 %. The +0.27 % was inside its own CI (-0.25..0.81) and is consistent with noise.

What this does not say: intrabar stops or slippage (stop fills at the bar close, optimistic), maker fees, other swing definitions or caps, USD-M perpetual prices (spot used), the mirror trade (fading the failed reclaim), timeframes other than 4h/1D. Spot not perpetual; 10 survivor majors (survivorship bias favours the rule, and it still fails).
Holdout/validation 2024-07+ BURNED for the reclaim-close-stop family (logged in holdout_reads.csv). Files: study.py, fetch.py, counts.csv, cells.csv, regime_mix.txt, test_10sym.py (3 pass).
