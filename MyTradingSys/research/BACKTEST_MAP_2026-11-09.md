# Backtest map 2026-11-09: where backtesting stands, where to start

**147 verdict rows are 48 ideas, not 147 failures; 0 setups proven, and the old pass-a-long-backtest gate was replaced on 11-06 by phase-first testnet-forward.**

Source: research/VERDICTS.csv (147 rows, counted 2026-11-09), execution/promoted_setups.json (0 entries), D7_ROADMAP.md, OPERATOR_DECISIONS.md.

## 1. The numbers, read right
| Verdict | Rows | What it really means |
|---|---|---|
| FAIL | 64 | this exact mechanical rule, under its cost, lost money; one study counts many times (imbalance 22, tf-break 6, jala 4) |
| INCONCLUSIVE | 51 | too few trades to say; mostly BTC-only on 1h+ (cannot reach power alone) |
| BLOCKED | 15 | never ran (no data, no engine): Kurisko 8, EUR-low follow-ups 3 |
| UNPARSED | 13 | old result files the counter cannot read |
| PASS | 2 | carry-basis arms; carry is dropped (not MTS's style) |

## 2. Three eras
| Era | Dates | What was tested | Why it failed (method, not only market) |
|---|---|---|---|
| A. Mechanical | 10-09..10-18 | single concepts as fixed rules (imbalance, BB, wavetrend crosses, levels) | no context: bought crosses in downtrends (d-context-retest-1104); fixed small stops vs 0.14 % cost |
| B. S3 funnel | 10-30..11-04 | roadmap run list (meta-label, Tom v2, Jala, tf-break, Rumers, CryptoCred) + context re-runs | pooled multi-year windows across bull/bear phases; BTC alone underpowered; Tom VP net -0.20..-0.26 R |
| C. Phase-first | 11-06 onward | patterns valid in the current phase -> testnet, run until they fail | backtest is no longer the gate (d-phase-first-method-1106); Tom/Fabio census 11-08 still ran the old way (7y pooled, -0.087 R) |

## 3. What a FAIL still tells us
| Keep | Do not conclude |
|---|---|
| that fixed-stop, no-context version does not pay fees (each row's kill_scope says exactly what died) | the concept is dead: no layer is discarded before the simulator review (operator 10-25) |
| tight stops on 10 bps perps lose to fees by geometry | that the trader's own method fails: most tests were OUR proxies, labelled OURS |

## 4. Where to start looking (only these)
| # | Look at | Why |
|---|---|---|
| 1 | this page | the whole picture on one screen |
| 2 | the Fable + Opus reviews of the Tom/Fabio work (REVIEW_FABLE.md, POSTMORTEM_OPUS.md, running now) | they say whether the latest no-edge result is real or a method fault, and how far Argon followed phase-first |
| 3 | the testnet-forward list: fable-run7-forward-test (ready, Krown S8 4h), auction-plan-testnet-forward-1108 (raw) | under the 11-06 method this is where edge is proven now |

## 5. Moving forward on the roadmap
| Stage | Before 11-06 | Now (phase-first, d-phase-first-method-1106) |
|---|---|---|
| S3 | one config passes a fee-net VALIDATION backtest -> promoted_setups.json | a pattern valid in the current phase, with a PRE_REG `## Context` and its invalidation stop, goes to testnet; a short current-phase check only rules out an obvious loser |
| S5 | promoted config trades testnet 30-60 d | same run: the testnet record IS the fee-net out-of-sample record |
| S6 mainnet | needs fee-net OOS | unchanged (Hard rule): the testnet record supplies it |
| Old backtests | the gate | sanity check and failure map: in which phase each pattern breaks |

Next moves: 1) the two reviews land and are compared; 2) fable-run7 and the auction plan go testnet-forward with a kill rule; 3) every new idea gets a phase tag and Context before any run.
