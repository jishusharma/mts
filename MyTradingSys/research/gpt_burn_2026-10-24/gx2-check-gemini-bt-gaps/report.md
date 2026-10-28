# Cross-vendor review: Gemini backtest standards gaps

Reviewed 2026-10-24 in `F:/MTS/gq/gx2-check-gemini-bt-gaps`.
Source report: `F:/MTS/gq/gb-bt-standards/MyTradingSys/research/gemini_burn_2026-10-24/backtest_standards_gaps.md`.

All **7** numbered gaps were checked. Gaps 1–6 contain confirmed, narrower omissions; gap 7 does not demonstrate a present survivorship defect. Several subclaims are wrong or already handled. No observed fee-net OOS verdict reversal was established: this is a code review with synthetic reproductions, not a run on sealed market data. Gemini's CRITICAL labels are not substantiated by an actual OOS pass reaching deployment.

Only this report and `audit.py` were written, within the authorized task directory. No git, sync, push, existing-code/test/card edits, servers, market-data loaders, or validation/holdout runs. The explicit audit restrictions supersede the normal boot/ship workflow. Existing research output remains unchecked unless independently reproduced here. External quotations, fee schedules and asserted typical funding rates in Gemini's report were not independently authenticated; they are not evidence for this review's conclusions.

## Reproduction and completeness

From the worktree root:

```powershell
python -B MyTradingSys/research/gpt_burn_2026-10-24/gx2-check-gemini-bt-gaps/audit.py
```

RESULT (2026-10-24, current worktree): exit 0. Parsed the source report's 389 lines and counted 7 GAP headings (178, 201, 231, 258, 281, 310, 338). Parsed the CSV as CSV: 30 rows, all DEV, 17 `pre-registered`; Gemini's 14-row characterization is incomplete. Its ledger header has 7 metadata columns, **no scalar return summaries**, and no return vectors (`MyTradingSys/research/TRIAL_LEDGER.csv:1`). Status `pre-registered` does not establish that a trial executed.

The script reads 1,042 Python files under `MyTradingSys`, `scripts`, and `src`, excluding caches, audit output and backup_session; 0 read/AST parse errors. It finds 0 CPCV text occurrences and 0 MinTRL text occurrences, but 69 walk-forward/purge/embargo occurrences and 4 matching AST definitions (including tests). These are bounded Python-source search results, not a claim about every language, external library or historical branch. `rg` was unavailable; Python/PowerShell provided the fallback. Conclusions below use parsed counts and selected source reads, not truncated search output.

EXPECT: all numerical expectations derive independently from `MyTradingSys/backtest/layers/FORMULAS.md:13` (Wilder recurrence), `:181`–`:200` (Sharpe/PSR/DSR/CSCV), and `:343`–`:354` (net return after fees, slippage, funding). Convert a return fraction to R by dividing by the specified stop fraction. Synthetic prices, costs beyond the canonical default, sample moments and independence assumptions are **OURS**, for sensitivity examples, not measured exchange behavior. Implementation modules are imported only to obtain actual results, not expected values.

## Ranking by potential to change a fee-net OOS verdict

Ranking reflects direct P&L effects first, then selection/evidence quality. It is conditional on the same omissions being carried into an OOS evaluator; the desk itself cannot return an OOS verdict.

| Rank | Gemini gap / confirmed part | Severity | Potential verdict effect |
|---|---|---|---|
| 1 | G1: no extra slippage/spread allowance; touch-filled resting targets and levels entries | HIGH | Broad execution sensitivity. Synthetic target touch versus subsequent stop changes +0.9298 R to −1.0995 R. Canonical 2 bps RT subtracts 0.02 R with a 1% stop, 0.04 R with a 0.5% stop. |
| 2 | G3: funding omitted in desk | HIGH | Particularly large for swing holds. At 1% risk, 15 positive settlements of 0.03%–0.08% cost a long 0.45–1.20 R. Direction reverses for shorts. |
| 3 | G6: no mark-price stop input in desk | HIGH | If the intended contract triggers on mark, different trigger bars alter outcomes. Synthetic mark-only stop changes −0.1000 R to −1.0995 R. Direction is not uniformly optimistic. |
| 4 | G2: no multiplicity-adjusted desk verdict | HIGH | Can select a spurious DEV winner. A separate sealed validation run limits the direct OOS effect; absence of a DSR/PBO gate is not itself evidence of a false OOS pass. |
| 5 | G5: no required power/track-length qualification before a desk pass | LOW | Weak precision for a small edge; does not directly change fee-net returns. Existing CI and insufficient-data branches substantially narrow Gemini's claim. |
| 6 | G4: no desk rolling/CPCV stability evaluation | LOW | Additional regime/path evidence could change trust in a result, but a static sealed OOS design is not inherently invalid. Repo already contains other walk-forward/purging implementations. |

## G1 — CONFIRMED, with entry-order correction (HIGH)

**CONFIRMED — slippage/spread omission.** `MyTradingSys/research/sim_desk/studies/_bars.py:120`–`:129` fills a market entry at the next open or a triggered entry at trigger/gap-open; `:144`–`:159` prices stop exits at stop/gap-open and subtracts only fees. There is no separate slippage or spread allowance. Gap-open handling exists, so “no adverse execution whatsoever” would be wrong. Also, OHLC trade prices alone do not establish a measured missing half-spread amount.

Reproduction: `audit.py` G1 flat trade, entry/exit 100, stop 99, taker 0.0005 each side: actual fee-only net = −0.1000 R. Independent section-13 expectation with 0.0002 RT slippage = −0.1200 R. Gemini's separate OURS stress, 5 bps / 50 bps risk = 0.10 R, is arithmetically correct; it is not an empirical estimate of every trade's cost.

**CONFIRMED — resting target/level touch fills.** `_bars.py:138`–`:148` accepts an exact target touch (except on the entry bar). The levels study uses a different simulator: `MyTradingSys/research/sim_desk/studies/levels.py:180`–`:186` calls `ladder.simulate`; the actual unconditional initial fill is `MyTradingSys/research/levels_confluence_2026-10-14/ladder.py:172`–`:178`. Subsequent entries use touch comparisons at `ladder.py:68`–`:74`; targets at `:76`–`:81`. No queue or partial execution model is present there.

Reproduction: G1 entry 100, stop 99, target 101; the next bar's high equals 101, followed by a later stop. Actual target net = `1 − (0.0005*100 + 0.0002*101) = +0.9298 R`. If the target stays unfilled, eventual stop net = `−1 − (0.0005*100 + 0.0005*99) = −1.0995 R`, a 2.0293 R difference. Removing the target in the reproduction represents that explicit unfilled-order scenario; it is not a calibrated queue simulation.

**WRONG CLAIM — triggered RSI entries are limits.** Gemini source `:187` misclassifies `_bars.py`'s trigger. `_bars.py:110`–`:111` explicitly defines a **stop entry**, `:125` uses high >= trigger for a long, and `:129` permits a worse gap-open price. `:156` charges taker on entry. RSI selects a breakout above the signal high at `MyTradingSys/research/sim_desk/studies/rsi.py:101`–`:113`. A queue-at-resting-limit critique does not describe this entry.

**ALREADY HANDLED elsewhere, not in desk.** `MyTradingSys/backtest/maker_model.py:46` enables regime C's through-tick stress; `:62` and `:85` apply it to entry and target. `MyTradingSys/backtest/bt/bt_engine.py:85` supports `target_through`. `MyTradingSys/backtest/layers/positioning/trade_costs.py:50`–`:68` already subtracts a slippage parameter. These implementations do not cure the desk's distinct execution paths. A fixed $0.50 tick should not be imposed on every desk asset merely because it belongs to the cited Deribit BTC specification.

## G2 — CONFIRMED gate omission; logging and probability claims corrected (HIGH)

**CONFIRMED — no DSR/PBO in the desk decision.** Correct location is `MyTradingSys/research/sim_desk/desk.py:74`–`:91`, not Gemini's `:23`–`:37`. Given `n=30, lo=0.01, hi=0.3`, `audit.py` returns `PASSED` without trial count, DSR or PBO inputs. `desk.py:150` reports try count separately. The correction modules exist at `MyTradingSys/backtest/bt/bt_stats.py:46`–`:99`; their presence does not wire them into the desk.

**ALREADY HANDLED — a desk pass is not an OOS acceptance.** `desk.py:85`–`:86` explicitly says DEV only and requires validation. `desk.py:34`–`:44` rejects validation dates; reproduction rejects 2024-07-01. `_bars.py:89` additionally asserts loaded data ends before July 2024. The cited stricter protocol is **PROPOSED**, `MyTradingSys/research/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md:2`, and describes a different DEV period at `:24`. Gemini cannot equate bypassing that proposal in an exploratory UI with bypassing an enforced OOS production gate.

**WRONG CLAIM — returns are not persisted / PBO is impossible post hoc.** The two text ledgers do not contain return vectors, but `desk.py:139`–`:141` serializes the **whole result**, including arrays, to local JSON. `_bars.py:176`–`:199` returns `day`, `touch_t`, `net`, `gross`, `fees`, `filled` and refs. The separate levels path returns them at `levels.py:215`–`:239`. Thus per-trade return persistence is **ALREADY HANDLED locally**. Retained caches can support reconstruction. What remains missing is a durable registry-linked, consistently aligned T×N matrix, handling zero-position days/nonfills, plus a PBO decision step. Cache deletion or missing settings associations would make reconstruction incomplete; array position is not common calendar time across variants.

Reproduction evidence: read `desk.py:133`–`:141` and result fields above; inventory parses ledger schema. No cache-writing desk run was needed. The trial CSV is a metadata registry, not the sole result archive.

**WRONG CLAIM — >80% false discovery after either 50 or 100 tries.** Gemini source `:223` supplies no dependence/null/prior assumptions and confuses family-wise error with false discovery rate. Under an explicitly OURS independent all-null model, positive lower endpoint of a symmetric 95% CI has nominal probability 0.025, so `1 − 0.975**50 = 71.8012%`, `1 − 0.975**100 = 92.0483%` for at least one false positive. These are illustrative family-wise probabilities, not estimates of the actual adaptive day-bootstrap search's FDR. Passing only `try_no` into DSR is also insufficient: `bt_stats.py:65` requires `var_sr`, and FORMULAS section 10 specifies the independent-variant interpretation.

## G3 — CONFIRMED desk funding omission; proxy interpretation narrowed (HIGH)

**CONFIRMED.** `MyTradingSys/research/sim_desk/studies/_bars.py:155`–`:159` subtracts only fees; the signature at `:107` has no funding input. `MyTradingSys/research/sim_desk/studies/rsi.py:20`, `:22`, `:113` permit maximum holds of 100 hours / 400 hours / 100 days for the three timeframes (actual exits can be earlier). Levels' separate net formula is also fee-only at `MyTradingSys/research/levels_confluence_2026-10-14/ladder.py:221`–`:224`.

Reproduction: G3 flat five-day long at 100, stop 99, actual net −0.1000 R. Independent canonical `(t_in,t_out]` funding with 15 settlements at 0.0003 costs `15*0.0003/0.01 = 0.45 R`, expected net −0.5500 R; at 0.0008 it costs 1.20 R, expected net −1.3000 R. The rates are OURS sensitivity choices carried over from Gemini's example, not a verified historical range. Missing funding can overstate longs or understate shorts at positive rates.

**ALREADY HANDLED — general discrete funding.** `MyTradingSys/backtest/bt/bt_engine.py:23`–`:25` rejects implicit `funding=None`; `:68`–`:76` charges settlement records, `:107`–`:109` checks coverage and `:119`–`:120` subtracts funding R. `funding=[]` deliberately means no funding model. `MyTradingSys/backtest/layers/positioning/trade_costs.py:12`–`:47` implements the canonical entry-notional settlement convention. Gemini's `[t_in,t_out]` wording at source `:240` is wrong: FORMULAS.md:348 and both implementations exclude exact entry-time settlements.

**CONFIRMED only as a model limitation — continuous funding not implemented in this engine.** The settlement loop cannot itself accrue a prorated two-minute continuous hold. But this is not an undisclosed vendor mistake: `BACKTEST_PROTOCOL.md:48`–`:49` explicitly calls the Binance 8h series a proxy for continuous Deribit funding and asks for a 2× stress. Two minutes versus eight hours gives a 1/240 fraction under a constant-rate continuous assumption; using a raw Binance settlement record for Deribit is a proxy whose adequacy needs measurement. No caller-specific Deribit verdict reversal was demonstrated.

## G4 — CONFIRMED missing desk stability feature; broad leakage claim unsupported (LOW)

**CONFIRMED — desk lacks rolling/CPCV evaluation.** `MyTradingSys/research/sim_desk/desk.py:27`, `:129`–`:150` runs one normalized date range and one pooled statistic. `_bars.py:22` fixes the last loaded month to June 2024. The Python inventory finds 0 CPCV occurrences. `bt_stats.py:69` implements **CSCV PBO**, which is not purged CPCV. These facts establish feature absence, not “extreme overfitting” of a particular fitted rule.

**ALREADY HANDLED — other repo walk-forward and purging.** `MyTradingSys/backtest/stop_buffer_wf.py:205`–`:215` selects k from pre-test training bounded by `lo - embargo` and evaluates the next block. `:14`–`:17` documents expanding monthly windows and one-day embargo. `MyTradingSys/backtest/layers/run_bracket_grid.py:121`–`:125` excludes IS trades whose exits cross the IS/OOS boundary. Neither is wired into desk; their existence disproves a repo-wide absence of walk-forward/purging. Reproduction: inventory lists the walk-forward function and relevant tests; inspect those boundary predicates.

**WRONG CLAIM — monolithic fitting is forced / existing sealed split is itself leakage.** Default is the full 27-month DEV window, but `MyTradingSys/research/sim_desk/studies/rsi.py:38`–`:39` exposes subranges, and `desk.py:34`–`:44` enforces dates. `MyTradingSys/research/sim_desk/studies/_bars.py:182`–`:185` caps a trade at the chosen end and removes a later signal exit. No train/test fitting fold exists inside this desk execution to which the asserted missing purge can automatically apply. Multiple DEV subranges are not independently sealed OOS folds, but a once-only later validation period is a legitimate safeguard. One path cannot prove regime robustness; that limitation is not proof of contamination.

The CSV rows encode `split=DEV`, not the evaluation procedure or proof that every registered trial ran monolithically. The parsed total is 30, not 14. Gemini's proposed `C(6,2)=15` counts test-fold combinations; it should not be called 15 distinct assembled OOS paths without defining a path assembly algorithm. A blanket one-day embargo is also unjustified for RSI's allowed 100-day holds; label horizons and boundary overlap must determine the purge/embargo requirements.

## G5 — CONFIRMED missing MinTRL qualification; sample-size conclusion overstated (LOW)

**CONFIRMED — floor 30, no MinTRL gate.** `MyTradingSys/research/sim_desk/desk.py:29` sets 30 and `:84`–`:86` can pass any qualifying positive CI without a power/track-length requirement. The 1,042-file inventory finds no MinTRL text. Reproduction: `audit.py` n30 positive-CI example returns `PASSED`. Independently inverting section-10 PSR for OURS SR=0.1, skew=0, kurtosis=3, benchmark SR*=0, PSR>=0.95 yields `T >= 1 + 1.005*(1.644853627/0.1)^2 = 272.907117`, hence 273 observations. This is a specified-moments PSR confidence calculation, **not** an 80%-power requirement or an empirical recommended sample size.

**ALREADY HANDLED — power/uncertainty is not absent.** `MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py:153`–`:170` bootstraps **days**, preserving trades grouped within a day; this is not an iid-trade naive bootstrap. `:193`–`:196` calculates sample-SD MDE and power. `desk.py:87`–`:91` uses power for a negative decision and otherwise returns `NOT ENOUGH DATA` for a wide range. Reproduction: n30, CI [−0.3,+0.5], power 0.079 returns `NOT ENOUGH DATA`, not `FAILED`. The proposed protocol's separate OOS rule already asks for 100 trades (`BACKTEST_PROTOCOL.md:69`), although it is not proof of an enforced gate everywhere.

**WRONG CLAIM — low power means an observed pass is almost certainly noise, or that an inconclusive run rejects the edge.** These do not follow from Type II error. For OURS iid normal returns, sigma=1 R, mean=0.1 R, n30, known-sigma two-sided 5% testing gives power **8.5016%**, supporting the narrow “less than 12%” statement. Exact normal quantiles give ceiling **785** trades for 80% power; Gemini's **784** is the rounded-z approximation, not a material defect. A two-sided test's 1.96 and one-sided positive-edge test's 1.645 must not be silently mixed. Increasing the floor to 100 would still not provide 80% power for this example.

Repo OOS exposure is more concrete at `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:59` and `:85`–`:90`: `n_oos=30, mean_net_oos=0.001, pbo=0.1` satisfies its literal `edge` predicate. It is not a CI/DSR/power gate. This is evidence that the proposal's 100-OOS standard is not universal, not proof that any actual 30-trade pass is false. The script does not execute that data-loading runner.

## G6 — mark omission CONFIRMED; pre-scan look-ahead WRONG CLAIM (HIGH for mark mismatch)

**CONFIRMED — no independent mark series.** `MyTradingSys/research/sim_desk/studies/_bars.py:65`–`:67` loads ordinary OHLC, and `:135`–`:146` checks the same trade-bar low/high for stops. There is no mark input in `:107`. If comparison is against the mark-trigger policy at `BACKTEST_PROTOCOL.md:43`, the desk cannot implement it.

Reproduction: G6 trade-bar low 99.5 never reaches stop 99; flat trade net is −0.1000 R. A synthetic corresponding mark low of 98.9 would trigger stop 99, with trade fill assumed 99: independent expected net −1.0995 R. This explicitly specifies the trigger and fill assumptions; it does not estimate actual mark/trade basis. Reverse divergence can stop the trade-bar model when the mark model would remain open, so the bias direction is conditional. Gemini's assertion that all live perpetual stops necessarily use mark price is not established by this repo review; use the intended order's trigger configuration.

**ALREADY HANDLED elsewhere.** `MyTradingSys/backtest/bt/bt_engine.py:78`–`:89` checks the supplied mark bar while pricing fills from trade bars. It falls back to trade bars when a mark bar is missing, so its optional capability does not certify full mark coverage or handle desk execution.

**WRONG CLAIM — scanning future RSI exits proves look-ahead.** Correct location: `MyTradingSys/research/sim_desk/studies/rsi.py:107`–`:113`. The code finds the **first** post-signal RSI crossing, sets `t_exit` to that higher-timeframe bar's close, then simulates earlier stop/target hits before it. `_bars.py:133`–`:154` restricts the path to before that timestamp, prioritizes stops/targets and otherwise exits at the last minute close. An exit determined from that bar's causal RSI is an outcome rule, not information fed into the entry selection. Entry, stop and target at `rsi.py:101`–`:105` do not depend on the future scan.

Reproduction: an independent Wilder implementation from FORMULAS section 1 matches all 166 available RSI values in a synthetic 180-close series. All 166 progressively extended prefixes match the full series' corresponding prefixes (0 mismatches). `MyTradingSys/backtest/layers/rsi/rsi_core.py:23`–`:44` seeds from the first period and smooths forward. This supports causality of the cited indicator; it is not a comprehensive proof about every study or partial-bar/gap case. Gemini's hypothetical “if parameters depend on dynamic future state” is not an exhibited defect in this code. Incremental reimplementation alone would not add execution slippage or a mark series.

## G7 — WRONG CLAIM as a present defect; future universe control is conditional (LOW)

`MyTradingSys/research/sim_desk/studies/_bars.py:37` restricts bar studies to named BTCUSDT/ETHUSDT instruments; `:45`–`:49` rejects other choices. `MyTradingSys/research/sim_desk/studies/levels.py:27` names BTCUSDT. These are named-instrument strategies, not a backtest selecting current survivors from a historical cross-sectional universe. No present cross-sectional selection rule, omitted delisted constituent, or distorted historical portfolio is identified by Gemini.

Reproduction: the literal symbol map has **2** entries. `MyTradingSys/research/sim_desk/ROADMAP.md:21` discusses possibly fetching ETH/SOL; it does not implement a current-top-20 portfolio. `TRIAL_LEDGER.csv:1` has no separate symbol column; its data-source/description fields do not prove Gemini's blanket “all 14 variants executed solely on BTCUSDT” assertion. Parsed counts are 30 rows / 17 pre-registered, including count-only-blocked and descriptive non-trading studies.

**ALREADY HANDLED in scope labels:** the symbol map explicitly labels the instruments OURS, RSI title names them at `MyTradingSys/research/sim_desk/studies/rsi.py:19`, and `:74` labels the selected instrument in the result description. A BTC-specific result cannot establish an altcoin-class edge, but lack of generalizability is not automatically survivorship bias within a fixed named-asset estimand. **Conditional confirmed requirement only:** any future historically ranked multi-asset universe needs point-in-time membership and delisting handling. No present fee-net OOS correction or numerical bias magnitude can be assigned to that hypothetical expansion.

## Disposition

Keep the confirmed execution/cost omissions as the first audit follow-ups, with explicit stress assumptions and the correct simulator path. Retain selection/power and regime checks as evidence-quality work, respecting the desk's DEV-only scope. Do not carry forward the false claims that cached trial returns do not exist, all repo walk-forward/purging is missing, causal RSI exit pre-scanning proves look-ahead, or named BTC/ETH testing proves survivorship bias. No existing code was changed and no production/OOS acceptance is granted by this review.

Result: Reviewed all 7 Gemini gaps; confirmed 6 narrower omissions, ranked execution costs and funding highest, corrected unsupported subclaims, and made no sealed-data or observed OOS-edge claim.
