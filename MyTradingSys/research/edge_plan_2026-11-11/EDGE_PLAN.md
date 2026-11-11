# Edge plan 2026-11-11: four forward slots, one stop rule, one decision date (Edge lead, Sonnet)

**Result: no rule has a passing fee-net result (0 of 15 trials); four leads go to testnet/paper-forward and stop at 30 trades if net R <= 0. Operator decision date proposed: 2026-12-31.** No edge claim, no forecast. Labels: SOURCED = file cited, OURS = this plan's choice.

## (a) Fee break-even and the size rule
Win rate needed with target = stop = the move (OURS arithmetic; 10 bp round trip taker SOURCED fees.py via AUCTION_CENSUS_1108.md; source table: four_model_review_2026-11-11/COMPARE.md s4):
| Move per BTC | Market orders (70 USD) | Limit orders (35 USD) |
|---|---|---|
| 100 USD | 85 % | 68 % |
| 300 USD | 62 % | 56 % |
| 500 USD | 57 % | 54 % |
| 1,000 USD | 54 % | 52 % |
| 2,000 USD | 52 % | 51 % |

**Rule (OURS, from this table): no NEW rule is tested or traded with a planned move under 500 USD per BTC or a stop under 40 bp.** Fades with 40 bp stops lost -0.106 R, n 1,484 (CENSUS_5M15M_1109.md). Honest exception: the four leads below were frozen before this rule; they run as frozen, paper/testnet only, and the plan flags those under the size line (C30 H2 averages +0.26 % = about 200 USD at 80k). They are not promoted on size grounds; the 30-trade rule decides.

## (b) The four leads (all inconclusive; none is an edge)
| Slot | Rule (frozen file) | Evidence | Trades/yr (OURS est.) | Mode |
|---|---|---|---|---|
| T06L | 4h RSI14 crosses above its SMA14, long, BTC+ETH (`backtest/layers/rsi/rsi_ma_cross_live.py`) | +0.105 R, n 623, CI -0.024..+0.233, Holm 0.83 (eh-h5 RESULT:44) | ~250 | paper |
| MLK | 4h Malkan level short, divergence 3-10 bars on closes, BTC (`malkan_level_short_live.py`) | +0.10 R, n 126, 0.9 SE (malkan_level_shorts REPORT:3) | ~50 | paper |
| KS8 | Krown S8 4h squeeze break, BTC (`fable_run7_forward_test/FORWARD_PREREG.md`, krown_live) | R6 DEV only, parity 277/277; forward slot started 11-09 | ~60 (0.169 signal-days/day, busy skips) | testnet |
| C30 | 15m WaveTrend buy dot <= -53 + RSI bull divergence, 2h trend up, exit wt1 > 0 (`eagle_eyes_picture_2026-10-28/PRE_REG_C30.md`) | +0.22 % net, n 22, CI -0.12..+0.56, beats random 30/30 (C30_VALIDATION:10-12) | ~18-22 | paper |

## (c) Stop rule for every slot
30 closed trades, then net R per trade <= 0 means the slot stops (SOURCED: REVIEW_FABLE d, null -0.087 R; OD d-phase-first-method-1106). Earlier: E- reaches 10 after 10 trades kills; Krown also keeps FAIL-A/B/C (12 R drawdown, 12 straight losers). E+ reaching 80 after 30 trades marks "worth a longer run", never "edge" (needs fee-net OOS plus operator for mainnet). RETIRE undecided at 150 trades or 12 months. Smallest edge worth a slot: 0.25 R. One combined readout: `forward_readout_all.py` (one row per slot: trades, net R, E+/E-).

## (d) Proposed decision date (the operator decides; this plan does not)
**2026-12-31.** By then (7 weeks from 11-11): T06L about 40 trades (30-trade rule reached about 2026-12-25), MLK about 7, KS8 about 8, C30 about 3. So on that date only T06L can be read; the other three show pace only. A second look **2027-05-31** is when KS8 and MLK reach about 30. Estimates are OURS from DEV rates and move with the market.
Honest limit: only one slot can reach a verdict by the proposed date, and a +0.10 R slot cannot be proven at n 30 (SD 1.4 R: detectable effect about 0.64 R at one-sided 5 percent, 80 percent power: 2.49 x 1.4 / sqrt(30); Gemini recompute 2026-11-11). The 30-trade rule can kill a slot, it cannot promote one.

## (e) Overfit rules for every backtest in this plan (Lopez de Prado, Advances in Financial ML ch. 7-9; added on the Supervisor's request)
The best-looking settings are the most overfit, and overlapping trades leak between train and test. So: (1) no parameter sweeps: thresholds are fixed in the pre-registration, a changed value is a new trial; (2) one trade at a time per rule, so outcomes do not overlap; (3) a gap of at least the longest holding time between the DEV and VALIDATION periods (24 h for the 15m with-trend rules, 100 bars = 16.7 days for Krown 4h).
Status, stated plainly: with-trend Shape A (pre-registered before this rule arrived) takes one event per direction per day with a 24 h hold, so a long and a short, or two days in a row, can overlap; it used no sweeps and no DEV/VALIDATION split (pooled diagnostic). Its FAIL does not depend on that, but any re-run must enforce (2) and (3).

## (f) Results so far (2026-11-11)
- Combined readout `fable_run7_forward_test/forward_readout_all.py` prints the four rows (Krown S8, Malkan, T06L, C30); all show n 0 today. C30 has a frozen rule and logger (`c30_forward_2026-11-11/`, live fetch not yet run). Malkan and T06 loggers exist but are not deployed (card deploy-malkan-level-short-forward-1109 is the coordinator's); Krown S8 is wired for testnet.
- With-trend Shape A (`with_trend_session_2026-11-11/RESULT_A.md`): FAIL, n 717, gross +0.045 R, net -0.088 R taker (SE 0.050), -0.015 R Deribit; every session negative (Asia -0.118, London -0.039, NY -0.061); random with-trend entries scored higher (+0.12 R) than the acceptance signal in 100 % of draws.
- Shape B (Opus trend pullback to value): 2 events on DEV against 30 needed: INSUFFICIENT n, no return computed, forward slot only; as written it can never reach n 30 in DEV.
