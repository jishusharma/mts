# BUILD PIPELINE
# Session: MTS-2026-10-03-0328Z-DSA-COO
# Written: 2026-10-03
# Purpose: single queue for all pending work. One row per item. Every item runs
#          the same T0-T5 contract and the same gate. Waves run in order.

## HOW AN ITEM RUNS

1. Read the row. Read the item doc.
2. Compose a CL or DSA prompt carrying a T0-T5 contract (same shape R4 used):
   T0 questions answered first, T1 file shape, T2 output shape,
   T3 tests (fail-before proof), T4 disk verification, T5 MISSED deviations.
3. Ship the prompt. Wait for reply. Same-turn verify against disk.
4. Gate: T1-T4 PASS, tests pass, Build-Check PASS, commit with session ID trailer.
   Live-path items also restart and verify.
5. Mark LANDED. Move to next row.

## STATUS VALUES

QUEUED / IN-FLIGHT / GATED / LANDED / BLOCKED / PARKED

## WAVE 0 - SCAFFOLD

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 0.1 | - | OPERATOR_DIRECTIVE_2026-10-03-historical-testing.md | LANDED | - | - |
| 0.2 | - | BUILD_PIPELINE.md (this file) | IN-FLIGHT | - | index row |
| 0.3 | - | 03_FILE_INDEX rows for 0.1 + 0.2 | QUEUED | 0.2 | splice + Build-Check |

## WAVE 1 - UNBLOCK

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 1.1 | B080 | dsa_worker hourly-cap misfires on stale pace entries | QUEUED | - | reproduce, fix, test |
| 1.2 | B075 | historical mode unfit for backtesting | QUEUED | - | fix zeroed flow fields + look-ahead |

## WAVE 2 - R4 FINISH

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 2.1 | R4-T1 | provenance read: K_BAL 0.8 / BAL_POC_BAND 0.25 / B_PROF 50 | QUEUED | - | CL prompt ready, ship |
| 2.2 | R4-T2 | false-vs-null collapse in failed_breakout | QUEUED | - | same CL prompt as 2.1 |
| 2.3 | R4-T3 | historical backtest of balance() parameters, OPERATOR-EXPERIMENT sweep | QUEUED | 1.2 | sweep ranges from operator |
| 2.4 | R4-D | parameter decision (accept / remove / replace-via-backtest) | BLOCKED | 2.1, 2.3 | operator |

## WAVE 3 - R5 / R6

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 3.1 | R5 | Model B failed-breakout shadow on 15m/4H | BLOCKED | 2.4 | shadow until n>=30 |
| 3.2 | R6 | canary as Windows scheduled task | QUEUED | operator yes | register task |

## WAVE 4 - ENGINE DEFECTS

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 4.1 | B070 | demote UTC 00:00 anchor + 0.75 slippage from gating | QUEUED | - | audit + demote |
| 4.2 | B076 | SETUP_CONFIRMED unreachable | QUEUED | - | trace verdict path |
| 4.3 | T052 | Tom-cited SETUP_CONFIRMED trigger | QUEUED | 4.2 | cite or reject |
| 4.4 | B059 | pf_vp bin-edge drift live verify | QUEUED | - | live tape confirm |
| 4.5 | T042 | OI/CVD peak reference still not emitted | QUEUED | - | add producer |
| 4.6 | B072 | L2 input validation for current_price | QUEUED | - | guard in build_math_object |
| 4.7 | B073 | net_rr rounding inconsistency | QUEUED | - | round-then-sanity |
| 4.8 | B074 | rule-order: contradiction cap before broken-value | QUEUED | - | reorder |
| 4.9 | B066 | rank-1 shown at trigger_ready 150 pts away | QUEUED | - | distance gate |
| 4.10 | B063 | divergence: restore in schema or deprecate | QUEUED | - | decide |
| 4.11 | T034 | positioning states (Net Longs/Shorts) | QUEUED | Rule 33 readers | design |
| 4.12 | T037 | test coverage gap 8 engine files | QUEUED | pom edit | operator pom approval |
| 4.13 | T040 | tick-based delta layer | QUEUED | research gate | threshold source |
| 4.14 | T044 | hybrid REST/WS divergence alert | QUEUED | - | build |
| 4.15 | T046 | stage 3 pending decisions bundle | QUEUED | - | resolve 5 items |
| 4.16 | B069 | STATE_UPDATE_WARN exit=1 under wrapper | QUEUED | - | wrapper exit handling |

## WAVE 5 - EXECUTION

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 5.1 | T050 | Deribit execution layer, phases 3+ | QUEUED | - | order placement testnet |
| 5.2 | B077 | stop order wrong type | QUEUED | - | stop_market fix |
| 5.3 | B078 | cancel_all_by_label overscope | QUEUED | - | label-scoped cancel |
| 5.4 | B079 | caps_check not enforced | QUEUED | - | within_max enforcement |
| 5.5 | T048 | satellite framework | BLOCKED | T050 ph4 | design doc |
| 5.6 | T051 | backtest MTS raw verdict | BLOCKED | T050 ph4 | parked |

## WAVE 6 - RESEARCH / MAINTENANCE

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 6.1 | T053 | two-account hedge / scalping | QUEUED | - | research |
| 6.2 | T054 | US session / pre-market / news | QUEUED | - | research |
| 6.3 | T055 | positioning + proven setups | QUEUED | - | research |
| 6.4 | T056 | audit program (Qwen decommissioned) | QUEUED | re-scope | redesign |
| 6.5 | T057 | simplify / declutter | QUEUED | - | DEV_VELOCITY_AUDIT follow-up |
| 6.6 | T058 | broken extremes: sweep vs continuation | QUEUED | - | research |
| 6.7 | T060 | low-volatility anomaly BTC | QUEUED | - | T3 evidence, backtest decides |
| 6.8 | T061 | WaveTrend LazyBear layer | QUEUED | - | integrate as layer |
| 6.9 | T059 | SESSION_PASTE size guard | QUEUED | - | 80 KB split |

## WAVE 7 - TOM ENGINE RE-RUN

| # | ID | Slug | Status | Blocker | Next |
|---|---|---|---|---|---|
| 7.1 | R7 | Tom BT re-run on D1 target rule | BLOCKED | Wave 4 | old-vs-new R distribution |

# END
