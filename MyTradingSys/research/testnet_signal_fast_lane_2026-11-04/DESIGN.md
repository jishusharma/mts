# Testnet signal fast lane: a named concept to a live SIGNAL the same day (design, 2026-11-04)

Ask: when the operator names a concept (e.g. "WT retest after the dot + RSI confluence"), it must be watching live, with a chart and drawn flags, the same day, without waiting for a full backtest-to-promotion cycle.
Status: design only. No code, no deploy, no orders, no mainnet. Implementation = later cards. Labels: SOURCED = existing repo/decision fact, OURS = our choice.

Basis: `d-live-validation` (2026-10-28: live signal + chart of drawn flags; operator confirms/corrects once per unique category; look-alikes inherit; differing goes to DOUBTS, never an auto-verdict). `d-cotrade-testnet-carveout` (2026-10-31: testnet orders he calls by name, only through `execution/cotrade.py`, journaled, never mainnet).

## 1. Host runner

| Piece | Choice | Source |
|---|---|---|
| Runner that hosts the signal | `backtest/layers/alerts/live_runner_cli.py` + `live_runner_core.py` (alert-only: public klines, registered layers, no execution imports, no keys) | SOURCED |
| New concept enters as | one more registered layer event function (same shape as `rsi_events`, `cvd_absorption_events`) passed to the runner by a `--concept <layer_id>` flag; no change to core logic | OURS |
| Verdict store / doubts | `alerts/live_validation.py` (category = symbol, tf, type, side; fail closed to DOUBT/PENDING) | SOURCED |
| Where it runs | by hand on a station, operator-started (no scheduler, SCHEDULING_POLICY); never in the live tree (`.mts_live`) | SOURCED |
| Order path | none inside the runner. Orders only when the operator says a trade by name and Claude runs `cotrade.py place` (testnet, stop mandatory, caps, HALT check) | SOURCED |

## 2. What is drawn

| Item | Content |
|---|---|
| Chart | candles of the signal timeframe + 1 higher timeframe for context |
| Flags | the concept's own event markers (e.g. WT cross dot, retest bar, RSI divergence pivots A..B), one colour per category |
| Levels | trigger level, invalidation level (the would-be stop, shown, not ordered), day high/low |
| Label | category key (symbol, tf, type, side), "matches validated case #n" or "NEW: needs your read" or "DOUBT" |
| Footer | base rate for this state if a DEV-window study exists, else the word UNMEASURED; trailing `1m | 5m` legend (operator ask 11-02) |
| Never drawn | entry/size/exit calls (Eagle_Eyes rule), mainnet data of the account |

## 3. Same-day steps

| # | Step | Gate |
|---|---|---|
| 1 | Operator names the concept; Builder writes it as one structured rule (inputs, trigger, invalidation) and a labeled parameter list, each SOURCED or OURS | rule quotes the operator's words |
| 2 | Add the event function as a layer; test-first: a unit test on a hand-built bar series that fails before the function exists, plus a lookahead lint pass (`lookahead_lint.py --new`) | CI green |
| 3 | Seed categories from history on the DEV window only (never VALIDATION/HOLDOUT); count flags per category | counts reported |
| 4 | Start the runner by hand with `--concept`; each new category sends one signal + chart to the operator | operator confirms/corrects once per category |
| 5 | Confirmed category: look-alikes inherit and are logged only; corrected or differing: DOUBTS list | no auto-verdict |
| 6 | If the operator wants to trade a signal he calls it by name: `cotrade.py place --said "<verbatim>" ... --stop <p>` on testnet, journal line written | cotrade hard limits |

Target: steps 1-4 in one session (size S per concept once the runner takes `--concept`).

## 4. Stays gated

| Stays gated | Why |
|---|---|
| Promotion to the live tree / confluence stack | needs a fee-net out-of-sample pass (PRE_REG with Context and regime mix); a signal being confirmed on a chart is validation of the reading, not an edge claim |
| Any auto-order from a signal | no path exists; cotrade.py is operator-called only |
| Mainnet, subaccount keys | separate money gate |
| Deploys, restarts, HALT | coordinator deploy runbook only |
| VALIDATION / HOLDOUT windows | sealed until promotion test |
| Parameter labels | every OURS value stays labeled OURS, never called the trader's |

Later cards (not built here): (a) `--concept` flag and layer registry hook in `live_runner_cli.py`; (b) chart renderer for a layer's flags; (c) category seeding script for a new concept.
