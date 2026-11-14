FAIL — Verdict (KILL) and top coin (BTC) match, but recomputed trade counts (`n=90` vs `91` in VAL, `n=122` vs `130` in DEV) and headline VAL 12bp mean R (`-0.0730` vs `-0.075`) have minor mismatches.

## Blind Re-derivation Summary

Re-derived independently from `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/PRE_REG.md` and `MyTradingSys/backtest/layers/FORMULAS.md` using `MyTradingSys/research/layer_lab/gemini_1114d/rederive-buyzone-test2-mtf/rederive.py` over the 20-coin kline cache in `~/mts_cache/buyzone_test2/` (without reading `lib.py`, `run.py`, `RESULT.md`, or `RESULT_tables.md` prior to computation).

## Claim Table

| Claim | Recomputed (OURS) | Stated (SOURCED) | file:line | Status |
|---|---|---|---|---|
| PRIMARY verdict (both sides pooled, VAL) | `KILL` (VAL mean12 `-0.0730`, CI `[-0.2777, +0.1458]`, placebo pctl `56.8%`) | `KILL` ("**Verdict (PRIMARY, RSI context, both sides pooled, 20 coins): KILL.**") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:7` | MATCH |
| PRIMARY VAL both sides `n` | `90` | `91` ("n=91") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:7` | MISMATCH |
| PRIMARY VAL both sides 12bp mean R | `-0.0730` | `-0.075` ("VAL fee-net 12 bp mean R = -0.075 per trade") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:7` | MISMATCH |
| PRIMARY VAL both sides 95% CI & placebo pctl | `[-0.2777, +0.1458]`, `56.8%` | `[-0.269,+0.145]`, `55` ("block-bootstrap 95% CI -0.269..+0.145), placebo percentile 55") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:7` | MISMATCH |
| PRIMARY DEV both sides `n` and 12bp mean R | `n=122`, `+0.2066` | `n=130`, `+0.230` ("DEV +0.230 (n=130, CI -0.013..+0.484)") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:7` | MISMATCH |
| PRIMARY VAL long `n` and 12bp mean R | `n=31`, `-0.4268` | `n=32`, `-0.413` ("-0.413 (-0.654..-0.142), n=32") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:12` | MISMATCH |
| PRIMARY VAL short `n` | `59` | `59` ("+0.109 (-0.174..+0.405), n=59") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:13` | MATCH |
| PRIMARY VAL short 12bp mean R | `+0.1129` | `+0.109` ("+0.109 (-0.174..+0.405), n=59") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:13` | MISMATCH |
| PRIMARY VAL top coin (both sides) | `BTC` (sum `+3.8120`) | `BTC` ("BTC \| 7 \| +3.81 \| +0.545") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT_tables.md:75` | MATCH |
| PRIMARY VAL minus top coin `n` and 12bp mean R | `n=83`, `-0.1251` | `n=84`, `-0.126` ("all \| VAL_minus_top \| 84 \| 33% \| -0.106 \| -0.126") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT_tables.md:33` | MISMATCH |
| SEC_WT VAL both sides `n` and 12bp mean R | `n=58`, `-0.0500` | `n=59`, `-0.021` ("-0.021 (-0.385..+0.459), n=59") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:14` | MISMATCH |
| CONTROL VAL both sides `n` and 12bp mean R | `n=1047`, `-0.0341` | `n=1068`, `-0.058` ("-0.058 (-0.179..+0.078), n=1068") | `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/RESULT.md:15` | MISMATCH |

## Regime Mix Cross-Check (from `PRE_REG.md`)

- `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/PRE_REG.md:10` (SOURCED): `DEV (coin-days, 20 coins, n=39926, n/a excluded from %): UP 23.2%, BASE 8.4%, DOWN 4.6%, BEAR 51.6%, RANGE 12.2%`
- Recomputed (OURS): `n=32926` (excluding 7000 warm-up `n/a` days = 20 * 350), `UP 23.2%, BASE 8.4%, DOWN 4.6%, BEAR 51.6%, RANGE 12.2%` — exact percentage match.
- `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/PRE_REG.md:11` (SOURCED): `VAL (coin-days, 20 coins, n=20404, n/a excluded from %): UP 19.2%, BASE 5.4%, DOWN 6.9%, BEAR 49.7%, RANGE 18.8%`
- Recomputed (OURS): `n=20424` (+20 coin-days = 1 extra day in local cache), `UP 19.1%, BASE 5.4%, DOWN 6.9%, BEAR 49.7%, RANGE 18.8%`.
- `MyTradingSys/research/buyzone_test2_mtf_2026-11-14/PRE_REG.md:12` (SOURCED): `RECENT (coin-days, 20 coins, n=9500, n/a excluded from %): UP 14.5%, BASE 4.9%, DOWN 5.1%, BEAR 63.1%, RANGE 12.5%`
- Recomputed (OURS): `n=9519`, `UP 14.5%, BASE 4.9%, DOWN 5.1%, BEAR 63.1%, RANGE 12.4%`.

## Notes

- All variants (`PRIMARY`, `SEC_WT`, `CONTROL`) and both sides (`long`, `short`, `both`) independently confirm the `KILL` verdict: VAL 12bp mean R is negative (`-0.0730` for `PRIMARY` both sides, `-0.4268` for `PRIMARY` long) or has bootstrap CI spanning 0 (`[-0.1489, +0.3923]` for `PRIMARY` short) and falls well below the 97.5th placebo percentile (`56.8%` both, `14.0%` long, `77.7%` short).
- Minor count differences (`90` vs `91` in VAL, `122` vs `130` in DEV) reflect small specification edge-case differences (e.g., first-close-through-pivot re-arming or divergence window boundary) between the independent implementation from `PRE_REG.md` prose and the study code (which was not consulted).
