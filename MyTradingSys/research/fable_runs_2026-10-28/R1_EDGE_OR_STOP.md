# R1: EDGE OR STOP (Fable 5.1, 2026-10-28, reading and reasoning only)

Question: after everything run so far, is there a credible path to a fee-net, out-of-sample edge on BTC, and what is the single cheapest experiment that confirms or kills it?

**Answer: no tested configuration has a fee-net edge, and every intraday (1m to 2h horizon) family is dead on costs alone: the best measured gross effect on DEV is 3.8 bp per trade against a 14 bp round trip (`dsa_backtest_audit_2026-10-16/scripts/T06/breakeven.csv:2-14`). The only fee-net out-of-sample PASS in the repo is unlevered funding carry, which is a yield, not a BTC trading edge, and cannot run on the Deribit-testnet live path (no spot leg). The one credible remaining path is a 4h-and-up rule with an event rate high enough to be powered; whether such a rule exists is a counts-only question that costs about 15 Sonnet turns and reads no outcome. That is the single cheapest experiment (section 4, E1).**

Scope kept: VALIDATION and HOLDOUT unread, no backtest run, no code changed. Labels: SOURCED = file:line in this repo; OURS = this session's choice or arithmetic (formula given).

## 1. Verdict per family

| Family | Verdict | Deciding evidence (SOURCED) |
|---|---|---|
| Tom | UNTESTABLE-AS-BUILT (tested encodings DEAD) | Encodings run so far lose fee-net OOS: TOM-CORE-0929 net -0.30 R, holdout -0.32 R n=254 (`research/layer_review_2026-10-26/PER_LAYER_REVIEW.md:38-41,57`); median stop 0.082 % so fees dominate (B146, `:45-47`). The sourced order-flow core cannot be tested on DEV: order-flow bars start 2024-12-02, after DEV ends (`research/gross_effect_screen_2026-10-15/PRE_REG.md:20`; `PER_LAYER_REVIEW.md:52-56`). The session-extreme fade with delta flow is INCONCLUSIVE at n_T=40 (`gross_effect_screen_2026-10-15/RESULT.md:1,8`). |
| Fabio | UNTESTABLE-AS-BUILT (v3 DEAD) | FABIO-V3 OOS FAIL n=79 mean -0.1038 R fee-net (`PER_LAYER_REVIEW.md:65-66`); all 5 order-flow layers NOT_IN_DATA on the desk, order-flow history starts 2024-12 (`:72-78`); live side inverted 0 of 24 (`:70`). |
| Malkan (RSI 40/60) | DEAD intraday; UNTESTABLE on 1d | RSI divergence 31 of 32 cells net negative after a 10 bp round trip (`PER_LAYER_REVIEW.md:113-114`); the one cell clearing a PBO bar earns gross +0.043 % at h=5 (`:110-111`), below the 14 bp cost. Daily rule: 2 filled trades in 27 months, mean -1.036 R (`research/layer_lab/TRIALS.md:274`); it fires about twice in DEV (`research/sim_desk/ROADMAP.md:18`). |
| Krown | UNTESTABLE-AS-BUILT | Only fee-net 4h result: S5 n=35, +0.278 R, 95 % -0.161..+0.750 (`TRIALS.md:280`); 35 trades can only rule out edges above +0.64 R (`research/sim_desk/results/desk-krown-634f1a37.json` why). Detector recall FAIL 3 of 12, S1-S9 `enabled:false` (`PER_LAYER_REVIEW.md:300-302`). No DEV event study exists (`:293`). |
| Levels | DEAD | 243 ladder cells, every mean net R negative, e.g. -0.441 [-0.475,-0.409] n=5,976 (`TRIALS.md:18-260`); best of 240 tries still -0.119 R per filled trade, gross +0.217 R, fee 0.337 R (`research/sim_desk/results/levels_ladder.json` kpis, why). Zero-fee variant +0.072 R [-0.007,+0.151] (`TRIALS.md:272`): the gross is fee-sized. |
| RSI / WaveTrend | DEAD | WaveTrend 1h band 53: n=369, -0.158 R, whole 95 % range below zero [-0.288,-0.023] (`TRIALS.md:273`); 0 of 9 frozen gross cells pass (`research/sim_desk/results/wavetrend_atlas.json` why). RSI: see Malkan row. |
| Funding carry | ALIVE as a yield, not as a BTC edge | Unlevered always-on carry PASS net 15.35 / 12.06 / 6.26 %/yr on its DEV / VAL / HOLD windows (`research/carry_basis_2026-10-18/RESULT.md:3,12,27-29`); it is the GO-PRIVATE trigger B (`research/STATUS.md:7`). Caveats: its "HOLD" window 2024-07..2025-06 is the project VALIDATION window (`carry_basis_2026-10-18/PRE_REG.md:16`), yield decays 15 -> 12 -> 6 %/yr (`RESULT.md:31`), 3x margin arm liquidated 2021-05-19 (`RESULT.md:3`), needs long spot + short perp on one venue: Deribit testnet has no spot leg (OURS). The directional funding-fade cousin is DEAD: T055-C1 OOS n=76 net -0.0453 % (`PER_LAYER_REVIEW.md:167-170`); f5 non-overlapping n=177, +0.050 R [-0.205,+0.306], FAILED after 144 variants (`TRIALS.md:279`). |

Gate board note: `research/STATUS.md:39-42` still lists "next: G3 blind marks" for Tom, Fabio, Malkan and Krown; G3 blind marking was dropped on 2026-10-28 (`system/OPERATOR_DECISIONS.md` d-live-validation). Those four "next" lines are stale.

## 2. The multiple-comparisons bill

| Item | Value | Label |
|---|---|---|
| Ledger rows in TRIALS.md | 281 (243 lc-ladder rows incl. the FROZEN row, 11 sim-desk, 16 event tables, 4 candle_close, 7 other) | OURS, counted this session from `research/layer_lab/TRIALS.md` (rows starting with "\| 2026-") |
| Cells named inside rows, outcome read | candle_close 2,016 (`TRIALS.md:263`) + exit_policies 114 (`:6`) + mfe_exit 51 (`:7`) + f5 144 (`:279`) + oi_pivot 32 (`:281`) + wavetrend 9 (`:273`) + rsi-div 32 (`PER_LAYER_REVIEW.md:113`) + Q33 guidance 336 (`:86`) + ladder 243 + sim-desk 11 + gross screen 30 (`RESULT.md:21`) = 3,018 | OURS (sum; lower bound, placebo and recount cells excluded) |
| Threshold for a DEV-mined result, m = 281 | two-sided Bonferroni z = Phi^-1(1 - 0.05 / (2 x 281)) = 3.75 | OURS, same formula as `pit_levels_2026-10-16/PRE_REG_V2.md:36` (Holm step 1) |
| Threshold for a DEV-mined result, m = 3,018 | z = 4.31; luck line sqrt(2 ln N) = 4.00 | OURS; luck-line formula SOURCED `research/audits_2026-10-26/FABLE_FULL_AUDIT.md:32` (desk.py:107) |
| Threshold for a fresh pre-registered family | z_holm = 3.241 at m = 42, then ONE VALIDATION read | SOURCED `pit_levels_2026-10-16/PRE_REG_V2.md:36`; re-derived: Phi^-1(1 - 0.05/84) = 3.241 |

Rule (OURS): any number mined from DEV needs t >= 4.0 to be taken seriously. A result that avoids the bill must be pre-registered with its own Holm pool (m <= 42, z 3.24) and confirmed by a single VALIDATION read; nothing mined from DEV is ever confirmed on DEV.

## 3. What a fee-net edge must look like

Cost: C = 14 bp round trip = taker 5 + 5 bp fee plus 2 + 2 bp slippage (SOURCED `gross_effect_screen_2026-10-15/PRE_REG.md:28-32`; fee constants `backtest/fees.py:27-28`). `FORMULAS.md:345-346` (section 13) uses 10 bp fee + 2 bp slippage = 12 bp. The prompt's "0.14 % + 0.02 %" double-counts slippage; C = 16 bp is shown as the conservative column.

Per-encounter spread at h = 60 min: sd = SE x sqrt(n) = 0.0246 x sqrt(1439) = 0.933 % (OURS from `RESULT.md:10`). Power gate re-derived: n_needed = ((z_holm + 0.8416) x sd / (plausible - cost))^2 = ((3.241 + 0.842) x 1.46 / 0.121)^2 = 2,427 days (SOURCED `PRE_REG_V2.md:20,28`; OURS recomputation gives 2,426.9). MDE of the gross screen T arm = 2.8 x 0.1304 = 0.365 % (SOURCED `RESULT.md:12`; recomputed 0.3651).

Minimum mean gross per trade, g >= C + (z + 0.8416) x sd / sqrt(n), 80 % power (OURS):

| trades n | z = 2.0 (pre-reg t_cost bar, `PRE_REG.md:78`), C = 14 bp | z = 3.92 (bill, m ~ 500), C = 14 bp | C = 16 bp, z = 3.92 |
|---|---|---|---|
| 40 (gross screen T arm) | 0.56 % | 0.84 % | 0.86 % |
| 200 (pre-reg N_min, `PRE_REG.md:77`) | 0.33 % | 0.45 % | 0.47 % |
| 500 | 0.26 % | 0.34 % | 0.36 % |
| 1,000 | 0.22 % | 0.28 % | 0.30 % |
| 5,000 | 0.18 % | 0.20 % | 0.22 % |

Measured against that: the largest gross effect ever measured on DEV is 3.8 bp (H2 preopen n=104) and 3.6 bp (AD mtf n=282), negative headroom under every fee regime except all-maker Deribit, where 1.8-1.9 bp per fill of slippage room remains (`breakeven.csv:8,10`; `T06_cost_fill_realism.md:104-121`). So at 1m to 2h horizons the edge needed is 5 to 10 times anything observed.

Minimum trades and days at a plausible gross of 0.30 % per trade (OURS: about 2x cost):

| bar | trades | days at the control rate 1.579/day (`RESULT.md:47`) | days at the T-arm rate 40 per 912 (`RESULT.md:8`) |
|---|---|---|---|
| z = 2.0 | 275 | 174 | 6,263 |
| z = 3.92 | 771 | 488 | 17,585 |

Reading: a family is testable on DEV only if it fires about once a day or more at 0.30 % per trade; a rare-event rule (Tom flow arm, Malkan 1d, Krown 4h at 35 trades per 27 months) can never be powered on 912 days. In desk units (1 % stop, 1 R = 1 %): fee = 0.14 R, and a 0.30 R effect with sd 1.37 R (OURS from the Krown CI: 0.4555 / 1.96 x sqrt(35)) needs 440 filled trades at z = 4.0.

## 4. Ranked experiments (information per unit of quota)

| # | Experiment | Cost | Pass rule, fixed now | If it fails, we stop |
|---|---|---|---|---|
| E1 | **Counts-only power screen, 4h and up.** For Krown S5/S8 (4h), Malkan RSI 40/60 (1d, 1w) and pitchfork (1d): count DEV events on BTC, plus DEV_EXT 2020-21 (operator-approved d3-dev-ext, `research/BUGS.md:302`) and ETH/SOL 1m for the same DEV months (public data, pre-approved; `ROADMAP.md:21`). No outcome column read. n_needed per family from section 3 with sd 1.37 R, cost_R = 0.14 % / median stop %, plausible 0.30 R, Holm m = cells in the family. | about 15 Sonnet turns + two public kline fetches (about 1.3 M rows per symbol); zero sealed reads | PASS = at least one family with n_available >= n_needed and events pooled across assets with a per-day cluster correction (OURS: one cluster per UTC day across symbols). | All DEV outcome studies on BTC stop; the trading-edge program has no powered test on our data, and only E3 (carry) remains. |
| E2 | **One pre-registered DEV outcome run for the E1 winner, then one VALIDATION read.** Desk studies exist (`studies/krown.py`, `studies/rsi.py`); cells frozen (<= 9), Holm over them, stop >= 4x round-trip fee (`FABLE_FEE_STOP_RULE.md` via `PER_LAYER_REVIEW.md:371-375`). | about 25 Sonnet turns + desk runtime; one VALIDATION read (card, with the operator told) | DEV: mean net R > 0 with t >= 3.24 in the primary cell; VALIDATION: mean net R > 0 with t >= 2.0 and the same sign; gross >= 4x fee. | That family is DEAD; the trader-source program (Tom, Fabio, Malkan, Krown extraction and gates) stops producing new backtests until new data (order-flow history before 2024-12) exists. |
| E3 | **Carry executability memo.** Which venue offers long spot + short perp at <= 0.10 % per leg with zero borrow; what the latest unread year paid (needs the sealed 2025-07+ read: operator decision, one line); what the live path lacks (spot leg). | about 5 turns, no backtest | PASS = a venue exists and the latest-year net >= 4 %/yr (OURS) and the operator approves the sealed read and going private (`q-go-private-on-edge`). | Carry parks; GO-PRIVATE trigger B withdrawn; the repo has no fee-net OOS PASS left. |

E1 is the single cheapest experiment: it can kill the whole BTC trading-edge path for about 15 turns without reading an outcome, and a PASS makes E2 the one run that confirms.

## 5. STOP list (pause; delete nothing)

| Work | Why it cannot change the verdict |
|---|---|
| G3 blind marks for Tom / Fabio / Malkan / Krown (`STATUS.md:39-42` "next") | Dropped by d-live-validation 2026-10-28; chart reads do not add trades to a powered test. |
| More levels / lc-ladder cells, levels confluence grids | 243 cells all negative; the best of 240 tries loses 0.119 R after fees (`TRIALS.md:18-260,272`; `levels_ladder.json`). |
| Any 1m to 2h horizon fee-net study on any family (gross screen v2, candle_close, mal_bb, opr_*, mfe_exit reruns) | Max measured gross 3.8 bp vs 14 bp cost (`breakeven.csv:2-14`); the Fable major run S1/S2 (`research/fable_major_run/CARD_2026-10-20.md`) recounts a T arm that needs 17,585 days at its event rate. |
| WaveTrend atlas variants W01-W09 routing, `wavetrend-c1-v2` card | Family DEAD: n=369 whole CI below zero (`TRIALS.md:273`). |
| Krown detector recall fixes (S1-S9 `enabled:false`), volume loading for S1/S2/S7 | Pointless before E1 says the family can be powered at all. |
| Live-parity fixes T09 F1-F6 and new live layers for FAILED families | No layer has an edge to carry live; T09's 94 % time exits and side inversion make live worse, never better (`research/sim_desk/results/t09_live_parity.json` why). Keep the testnet path frozen. |
| GPT lab recount queue on DEAD families (`lf-tom/fabio/wavetrend/pitchfork-gpt-rederive`, `gpt-formulas-rederive-*`, `gem-*-recount`; 46 ready, `STATUS.md` Layer Lab) | Recounts of numbers already below cost; t06/t07/t09 recounts (`layer_lab/reports/2026-10-27_gpt-t06-breakeven-recount.md`, `..._t07-...`, `2026-10-28_gpt-t09-table-recount.md`) found prose and count errors only, no verdict flip. |
| Page / deck regeneration for stale artifacts (6 STALE, `STATUS.md`) | Presentation of results that do not change. |
| mfe_exit non-reproduction chase (966 DIFF cells, `..._t07-rerun-recount.md:12`) | The family's gross is +0.3 bp (`breakeven.csv:14`); reproducing it exactly changes nothing. |

Findings that do not change the verdict but must stay on record: T07 mfe_exit does not reproduce; T09 volume_fvg trades the inverted side 0 of 24 and RSI live fires on untested events; both make the live path less trustworthy, not the backtests more.
