# Guided simulator session: how to read failures and look for an edge (plan by Lead C on Fable, 2026-11-10)

For a Sonnet guide working live with the operator. The operator clicks; the guide reads the result and says what it means.
Operator order 2026-11-10 13:00Z: "only failures to look at ... how to look at it so that I am able to do something positive
... a Sonnet session guided by a plan set by the Fable model". Labels: every number rule below is OURS unless a file is named.

## 1. The idea in one line
A failed backtest is a map of WHERE a rule loses. The session turns one failure into one sentence ("it loses mostly in X"),
one thing the operator sees on the charts that the rule does not, and one filter tested once. That is how an edge is looked for.

## 2. What the simulator can do today (HANDOVER_SIMV2.md, ROADMAP.md; not re-checked on 11-10, step 0 checks it)
| Tool on the page | Used for |
|---|---|
| Studies: levels, RSI 40/60, WaveTrend | the rule under test |
| Numbers strip (win rate, profit factor, max drawdown, gross / fee / net) | is it losing before fees or only after |
| Breakdown table (year, side, 4-hour UTC block; n and mean net R) | where it loses |
| Clickable trade list with candle chart | what the operator's eye sees |
| CONDITIONS panel, run A against B on the equity curve | test one filter |
| Monte Carlo band and luck line | is the result more than luck |
Start it: `python MyTradingSys/research/sim_desk/desk.py` (opens the browser, prints the address). DEV window only: 2022-04-01 to 2024-06-30.

## 3. The session, six steps (60 to 90 minutes, one idea only)
| Step | Min | Operator does | Guide says | Output |
|---|---|---|---|---|
| 0 Open | 5 | nothing | starts the desk, confirms the page loads and the tests pass; if not, stops and reports | desk open |
| 1 One run | 10 | picks one study, clicks Run with default settings | three numbers only: filled trades, mean net R, share of the loss that is fees | "this rule loses N R per trade, M of it fees" |
| 2 Where it loses | 15 | reads the breakdown table with the guide | the worst cell and the best cell that has 30 trades or more; cells under 30 are named "too few" and ignored | one sentence: "it loses mostly in X" |
| 3 Look at trades | 15 | opens the 5 worst losers and the 5 best winners, says what he sees | writes each remark as a tag (trend against, no level, late entry, news hour) and counts the tags | the most common tag |
| 4 One filter | 15 | chooses the filter that matches the top tag | writes the expectation in one line BEFORE the run, then runs A against B | filter result with n |
| 5 Verdict | 5 | decides with the guide | applies the table in section 4 | one of three verdicts |
| 6 Close | 5 | nothing | writes the 5-line note (section 6), files the next card, ships | note on trunk |

## 4. Verdicts (step 5)
| Result after the filter | Verdict | Next |
|---|---|---|
| mean net R still below 0 | PARK, with the sentence from step 2 | a row in the failure map: the phase or hour where it breaks |
| above 0 but fewer than 30 trades, or under the luck line | NEEDS DATA | card: same run on ETH and SOL for the same months |
| 0.25 R or more, 30 trades or more, above the luck line | CANDIDATE | card for a paper or testnet forward slot, read weekly with E+ and E- (PLAN_24H_2026-11-10 section 1). Never mainnet |
0.25 R is the smallest edge worth a slot (eh-f1-testnet-design/DESIGN.md).

## 5. Limits that keep the result honest
- Two filters at most per idea per session. Every extra try makes a lucky result likelier; the luck line already counts tries.
- The expectation is written before the run, never after.
- No look at the VALIDATION or HOLDOUT windows.
- A PARK is a finding about that exact rule, not about the trader's method (BACKTEST_MAP_2026-11-09.md section 3).

## 6. The note the guide writes (5 lines, `research/sim_desk/sessions/SESSION_<date>.md`)
Idea and study | where it loses | what the operator saw (top tag, count) | filter tried and its numbers | verdict and next card.

## 7. What to watch first (in this order)
| # | Idea | Why first | Source |
|---|---|---|---|
| 1 | RSI study on the 4-hour chart | nearest on the desk to the best leftover of the edge hunt, T06: +0.048 R, n=1322 | PLAN_24H_2026-11-10 section 1 |
| 2 | WaveTrend crosses, filtered by the 15m and 30m side | the Live Aid "timing check" strip uses this agreement; its thresholds are not backtested | commit 61be0d9cc (not on trunk at 13:00Z) |
| 3 | Levels study, losers by hour | 255 filled trades, -0.189 R with slippage; the breakdown has enough trades to read | HANDOVER_SIMV2.md |
| 4 | Tom/Fabio 5m and 15m census | waiting for that session's report | CENSUS_5M15M_1109.md (not on trunk at 13:00Z) |

## 8. Rules for the guide
- One step at a time. Each reply: a bold result line, under 8 lines, plain words, at most one question, one new term explained.
- The guide reads `results/desk-*.json` itself and never asks the operator to read numbers aloud.
- No forecasts and no trade advice. No code changes during the session: a missing feature becomes a card.
- If the desk does not start or a number looks wrong: stop, say so, file the card.
