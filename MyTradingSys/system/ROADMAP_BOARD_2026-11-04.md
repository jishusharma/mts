# Roadmap board 2026-11-04 (week start, login C reset)

Source of each number: D7_ROADMAP.md (stages), VERDICTS.csv (118 rows), execution/promoted_setups.json (empty),
system/tasks/*.json (card states), STATUS.md generated 2026-11-04 01:10. Read: it says where every stage stands today.
Rewrite this file at each week start; never let it grow.

## Stages (D7)
| Stage | Goal | Exit | State today | Blocked on |
|---|---|---|---|---|
| S0 Freeze and clean | small, clean repo | ready<=15, claims<=4, trees<=8, bookkeeping<30% | WAIVED 11-03 (claims 43, bookkeeping 67% of 186 commits/24h) | cleanup keeps running beside S1 |
| S1 Spec signed | one signal schema, bar revision, seam test | D2 signed, GO_LIVE_BAR revision, seam test green | SIGNED 11-04 (d-s1-defaults-1104, 11c2703d); D7 Now: S2, S3, S4 in parallel | - |
| S2 Platform hardening | live loop that survives restart, gaps, API errors | 4 cards done test-first, 14 d heartbeat>=95%, HALT+restart drill | NOT STARTED: state-code-accumulator-backfill refined, s2-uptime-heartbeat refined, L6/B149 settlement open, gap-g7 no card | S1 exit; builder on JIS-NB |
| S3 Two-layer funnel | one config passes fee-net VALIDATION | promoted_setups.json gets one entry | 0 promoted. Rumers 5 rules DEV 11-04: 0 pass (3 FAIL, 2 thin), 561df2f0. Run list 7: 5 done (meta-label FAIL, Fabio-C parked, CryptoCred BLOCKED power, Tom v2 FAIL, reclaim INCONCLUSIVE); lc-validation refined (HOLD A-20261018-5), rsi-deep-run-dev refined | prerequisites on 2 cards; nobody runs them |
| S4 CBP module | analyst rows flow producer->consumer | one real row end to end, harness green | NOT STARTED: s4-cbp-golden-set-harness ready, s4-cbp-module-e2e ready; 5 cbp-* blocked | S1 exit; a SONNET builder |
| S5 Testnet to the bar | promoted config trades on testnet 30-60 d | bar holds (sign) | cannot start | S2 exit AND one promoted config |
| S6 Mainnet decision | tiny size, repo private | signed | - | S5 |

## Evidence (what the research produced so far)
| Measure | Number | Meaning |
|---|---|---|
| VERDICTS rows | 118: FAIL 55, INCONCLUSIVE 40, UNPARSED 13, BLOCKED 8, PASS 2 | the 2 PASS are funding-carry basis arms, not a trade setup |
| Layers with a surviving fee-net PASS | 0 of 37 | STATUS.md "Layer pass" |
| Promoted configs | 0 | nothing may trade on testnet yet |
| Cards | 729 done, 130 refined, 142 dropped, 28 ready, 30 blocked, 15 raw | 130 refined = specified, never run |
| Claims | 43, many 80-116 h stale | S0 target 4 |
| Open operator questions | 1131 | unanswerable backlog; archive all but S1's three |
| Pages stale | 3 (mts_home, sim_desk, mts_layer_map) | MTS Home rebuild card still ready, not shipped |

## What blocks movement (plain)
1. S1 is no longer blocking: the operator answered yes to q-v1-bar, q-v1-layers and q-v1-spec (d-s1-defaults-1104, 2026-11-04, chat yes relayed by Super Session, not verbatim per line). D7 "Now:" is S2, S3, S4 in parallel.
2. Two thirds of trunk commits are bookkeeping (claims, releases, merges, card folds). Research is one third.
3. The S3 funnel has 2 untried studies and 5 finished ones that mostly failed; the 2 untried sit in "refined" behind prerequisites nobody owns.
4. The PASS rule (VERDICTS row + causal replay + independent re-run) is right-sized; the guard card research-pass-needs-rerun-gate is ready, not built. Testing is not the shortage; runs are.

## Week plan 2026-11-04 to 11-10 (coordinator: Unblock MTS super session, login C)
| # | Move | Owner | Done when |
|---|---|---|---|
| 1 | DONE 11-04: S1 signed (d-s1-defaults-1104, 11c2703d); q-v1-bar, q-v1-layers, q-v1-spec all yes | C drafted (S1_SIGN_DRAFT_2026-11-04.md), operator answered | OPERATOR_DECISIONS.md entry and D7 "Now:" line moved to S2/S3/S4 (both met) |
| 2 | S3: run lc-validation and rsi-deep-run-dev under the PASS guard (build research-pass-needs-rerun-gate first) | B (NUC) + guard card SONNET | VERDICTS rows + sim_desk/results json, PASS or FAIL written |
| 3 | S2 M1+M4 on JIS-NB: state-code-accumulator-backfill, s2-uptime-heartbeat-jis-nb, test-first | C lane JIS-NB | tests failed on old code once, CI green |
| 4 | Declutter: release stale claims (q-8df7bd), archive 1131 open questions except S1's three, republish MTS Home | C | claims<=8, STATUS pages stale 0 |
| 5 | Machinery freeze: no new pages, docs, lanes or tools this week; only the four moves above | all | commits 24h bookkeeping share < 50% |
