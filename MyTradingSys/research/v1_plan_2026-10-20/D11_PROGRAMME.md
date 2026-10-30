# D11. Work programme for the super sessions (Fable, 2026-10-30, operator ask)

The operator's goals, in his words (voice, 2026-10-30): "build powerful, accurate tools, start testing on testnet all the latest
layers that are fixed, enhanced, and try to understand what kind of trades we are going to place on the testnet so that we can
choose from them for the actual trades ... understand how I could be guided during a live trading session ... learn from the
mistakes that we have made in the past ... remove any contradiction ... even cheap models could be deployed for testing, for
reviews, for finding bugs ... never falling short of work. Right now there is no work for GPT, Gemini, most of the time."

This file is the standing answer: which streams the super sessions work, in what order, what goes wrong in each, how each is
tested and reviewed, which model does what, and the mechanism that keeps every lane fed. D7_ROADMAP.md stays the roadmap; this
file says how its stages get worked. Decision record: OPERATOR_DECISIONS.md `d-super-session-programme`.

## 1. Where we stand (RESULT, measured 2026-10-30 17:00Z on trunk 8bd86620d from the desktop)
| Thing | Number | What it means |
|---|---|---|
| promoted_setups.json entries | 0 | no layer has passed the funnel; the GO_LIVE_BAR counts nothing yet |
| testnet engine | live owner = the Lenovo (desktop-f7iu69n); `live_mirror.py brief` from the desktop: UNCONFIRMED | nothing on this machine can say whether testnet is trading, halted or paused; the desktop's own HALT (10-15 settlement) and AUTO_PAUSE (10-22 host move) files are leftovers of the move; `system/live_host.txt` still says JIS-NB |
| what trades on testnet | `auto_trader_config.json pre_pipeline_sources`: cryptocred and fabio families at calibration sizes 20-1000 USD, "grandfathered ... review_by 2026-10-23" (lapsed) | the operator's "see what trades we would place" already exists as calibration trades; nobody reads them daily and they must never count toward the bar |
| ready cards | 32: SONNET 21, CODEX-GPT 6, GEMINI 0, HAIKU 0, OPUS 4, JIS-NB 4, DSA-NUC 1; 20 flagged STALE scope | Claude has work, GPT has 6 audits, Gemini and Haiku have nothing: the lanes the operator named as idle are idle by construction |
| GPT lane | 6 ready, nothing ran for 20.8 h; GPT week 53 % used | prepaid quota unused |
| Gemini lane | 16 parameter-label cards done today, 0 ready; usage NOT_IN_DATA (logs stay on the NUC) | fed only when somebody writes `[GEMINI]` cards by hand |
| Claude weekly | A 2 % (Lenovo), B 57 % (stale reading), C 37 % (desktop) | most of the week is unspent |
| super sessions | none running; `bug-supervisor-idles-after-wake-retired` (Opus, p1) unfixed | the dispatcher that should feed the lanes is itself the open bug |
| hygiene | worktrees 51 (13 unshipped), 6 stale published pages, 9 OVERDUE asks | S0 exits (worktrees <= 8, claims <= 4) not met |

## 2. The streams (what the super sessions work, in this order)
| Stream | D7 stage | First card now | Then | Where it goes wrong (past mistake) | Test and review | Lanes |
|---|---|---|---|---|---|---|
| A Setup truth: which setups are Tom's and Fabio's, rule by rule | S1 | `setup-review-with-operator` (his verdicts TOM-1a, 1b, 2, 3 pending); the 5 `layer-review-*` sheets | storybook v2 (done 10-30) feeds the picks; 2-3 picks go to B | OURS rules called Tom's; setups extracted but never reviewed (d-setup-review-before-backtest); invented quotes (Gemini video reads) | `verify_extract_quotes.py` exit 0 on every sheet; GPT formula audits (6 ready); a `[GEMINI]` blind read of every sheet; SOURCED/OURS on every number | SONNET build, GPT audit, GEMINI review |
| B Funnel: pre-reg, DEV, one VALIDATION read, promotion | S3 | D4 slots: Levels Confluence (`lc-validation` after LC3 DEV says go) and CryptoCred 4h/1d; then A's picks | `promoted_setups.json` gets its first entry or both FAIL and the next two enter (D7) | look-ahead; fee-less numbers; variant counting without Holm; tests "fixed to match the code" (LESSONS 1-2); DEV p-values promoted | PRE_REG_TEMPLATE 12 items with file:line before any run; planted-error canaries (DSA T03, done); T05/T06 audits moved to GPT and Sonnet (DSA bridges closed); every headline number re-derived by another vendor before it is quoted | SONNET run, GPT re-derive, GEMINI review |
| C Testnet picture: what the fixed layers would trade, read daily | S5 prep | `testnet-trade-readout-daily` (JIS-NB lane = the live host): `testnet_status.py` + `funnel_report.py` on the live owner, one page per day, every row labelled calibration or promoted, engine state stamped (owner, HALT, AUTO_PAUSE); fix `live_host.txt` | `live-not-fired-audit-1029` (fired vs silent on the 10-29 cascade); forward parity when `fable-run7-forward-test` leaves HOLD | trades from a halted or paused engine read as evidence; calibration trades counted toward the bar; live owner unknown from other machines (today) | each readout fails closed on a missing ledger (NOT_IN_DATA, never zero); GO_LIVE_BAR counts promoted rows only (`test_auto_trader_promotion.py`); a Haiku Agent recounts one day | JIS-NB run, SONNET build, HAIKU count, GPT audit of the counting rule |
| D Live guidance: the operator in a live session | S5 | `live-aid-replay-mode-fixture-feeds` (rendered numbers checked, not just no-crash); `live-engine-analyst-levels`; `live-aid-macro-calendar` | `sim-desk-page-click-test`; `cbp-analyst-desk-repo-copy-and-open-check`; republish the 6 stale pages | a number shown before it could be known (analyst hit look-ahead, found by Argon 10-30); a page that goes blank or shows NaN; stale published copies | ARTIFACT_TESTING.md four layers (maths, build, open-it, time honesty); `test_artifact_pages.py` opens all 10 pages offline on every desktop ship; GPT audit of `live_aid_indicators.js` vs FORMULAS.md; `[GEMINI]` labels on every page parameter | SONNET build, GPT audit, GEMINI labels, HAIKU republish |
| E Platform hardening: the live path survives restarts | S2 | `statecode-backfill-race-coverage`, `settlement-capture-testnet-second-log`, `wire-binanceliquidationaccumulator-into-` (JIS-NB) | `gap-g7-stop-slippage`; 14-day heartbeat >= 95 % on the live owner; one HALT drill, one restart drill with EXPECT before and RESULT after | restart, reset, transfer, partial fill and API error paths untested; a guard that opens instead of closing (LESSONS 3) | one restart/reset test per live file in the same change; diff-only Sonnet review Agent before ship; `--full` gate | SONNET (live path), JIS-NB desk |
| F Machinery repair, no growth | S0 | `bug-supervisor-idles-after-wake-retired` (Opus, operator-approved d-supervisor-idle-bug) | `claim-lease-expiry-and-b2-hole`, `ship-gate-flaky-under-load-3sig-3cr-5b`, Codex lane stalled, worktrees 51 -> 8, `two-workers-built-the-same-ready-card-li` | coordinators idle 8 h with ready work (10-30); two workers on one card; three gates colliding; 68 compactions losing state | `test_supervisor.py` (lane floors, this ship); status board RED "idle with ready work"; Haiku spot-check of every worker claim | OPUS (named), SONNET, HAIKU |

Order: F first for one wake (nothing moves without a dispatcher), then A, C and D in parallel (different files), B as soon as A
yields picks or LC3 says go, E in parallel on the live-path files. Three workers at most (D7 capacity rule), default 2.

## 3. Models: cheap first (who does what)
| Model | Lane / channel | Use it for | Never for |
|---|---|---|---|
| Haiku | lane HAIKU, one-use Agents (max 5) | counts, stale-card refresh, test registration, republish and `publish-record`, recount one worker claim, data-file checks | judgement, the live path |
| Gemini Flash (effort low) | lane CODEX, title `[GEMINI]`, `gemini_queue.py run <id>:low` | SOURCED/OURS labels, blind reads of sheets and reports, cross-vendor review of GPT and Claude results, doc contradiction scans with file:line, search | verdicts; a number we quote without a second vendor |
| GPT luna medium | lane CODEX, `codex_run.py` | formula audits vs FORMULAS.md, re-derivations, spec-derived and mutation tests, cross-vendor review of Claude and Gemini results | live-path edits; anything it cannot run on the lab data |
| Sonnet | lane SONNET, background Agents | builds, pre-regs, DEV runs, layer sheets, audits needing judgement, diff review of live-path changes | a card it already got wrong twice (then Opus, by the operator's word) |
| Opus | lane OPUS, `approved_by` | only cards the operator named: supervisor idle bug, cost checkup, O3 overhead cut | "better quality" |
| Fable 5.1 | operator-run sessions | design and reviews with the operator (this file, setup review verdicts), R5 and R7 | background work; nobody starts or messages it |
| DeepSeek bridges | closed (standing operator hold) | nothing until he reopens them | |

**Feeder rule (the never-empty mechanism).** Every ship produces its check in another vendor's lane in the same wake, so the
cheap lanes fill from the work itself, not from someone remembering:
- a new `.py` without a test -> `gpt-spec-tests-<name>` (CODEX, kind audit);
- a result or audit file with numbers -> `[GEMINI]` blind re-read (or a GPT re-derive when Gemini produced it);
- a page or panel -> Haiku open-check (`test_artifact_pages.py`) and republish + `publish-record`;
- a live-path diff -> the diff-only Sonnet review Agent (SUPER_SESSION rule 3).
`supervisor.py plan` prints `LANE LOW <lane> <n> (< floor)` for SONNET 6, HAIKU 3, GEMINI 4 (CODEX keeps its < 8 line); the
Session_Planner feeds that lane from section 6 first, then refines raw cards. The weekly read stays D7's: one line per stream on
the decision page (stage, exit metric, today's number, blocked-on).

## 4. Contradictions found on 2026-10-30 and how they are resolved (all recorded in `d-super-session-programme`)
| # | One place says | Another says | Resolution (DECISION OURS unless marked operator) |
|---|---|---|---|
| 1 | D7 freeze: "new pages" frozen | the operator builds the sim desk, live aid and CBP desks and asks for them to be improved | the freeze covers machinery pages (registry docs, boards); trading tools are the product and may grow, each under ARTIFACT_TESTING.md |
| 2 | D7 S5: "the promoted config(s) trade on testnet" | `pre_pipeline_sources` lets cryptocred and fabio trade on testnet since 10-08 under a lapsed `review_by 2026-10-23` | testnet has two kinds of trade: calibration (any fixed layer, shows what we would place, never counted toward the bar) and promoted (counts). The daily readout labels every row; `review_by` moves to the S3 first pass; the operator may prune the list any day |
| 3 | SUPER_SESSION Mechanics: "sessions on operator turns, Agents on event turns" | WORKERS rule 7: workers are background Agents, never `start_session` | workers are Agents always; `start_session` only for interactive roles and for the super session itself when the operator kicks it off |
| 4 | ROUTING.md: a Gemini card is lane CODEX with a `[GEMINI]` title | `supervisor.py` counted a `vendor` field that no card has: 0 Gemini cards ever, so no Gemini worker ever spawned | fixed in this ship (`lane_counts`, test `test_plan_lines_lane_floors_every_lane_not_only_codex`) |
| 5 | ANNOUNCEMENTS A-20261018-3/4: the Codex lab runs on the NUC | signal b-230ce8 told the desktop to run `codex_run.py`; the Lenovo acked "lab runs belong on NUC"; the lab has not run for 20.8 h | the NUC owns the lab; when no NUC supervisor heartbeat is under 2 h old, the desktop super session claims the card (`sync.py claim`) and runs `codex_run.py tick` once per wake; the claim prevents a double run |
| 6 | D8 rule 5: DSA and Gemini retired unless their rows drain | A-20261026-1 and the operator (10-25) put all YouTube and heavy work on Gemini at the NUC | Gemini stays (the later operator word); DSA bridges stay closed (standing hold); D8 rule 5 reads: lanes = Claude, GPT, Gemini, Operator |
| 7 | S0 exit: ready cards <= 15 | every lane needs a floor (6 + 3 + 4 + 8 = 21) | the <= 15 cap applies to the Claude lanes (SONNET + HAIKU + OPUS); GPT and Gemini are prepaid and counted apart (operator 10-28: exhaust GPT) |
| 8 | GO_LIVE_BAR: 200 closed trades from configs that passed walk-forward | `fable-run7-forward-test` HOLD: a powered forward read needs about 72 months | a forward test is parity and trade-shape evidence, never the verdict; verdicts stay with the pre-registered backtests (stream B); the bar is unchanged |
| 9 | `system/live_host.txt` = JIS-NB | the live owner is the Lenovo since the 10-22 move (`live_mirror.py brief`) | the readout card corrects the file from the owner; until then every live read says "owner UNCONFIRMED" |

## 5. Mistakes of the past that shaped this (LESSONS_DIGEST.md -> rule applied here)
- Look-ahead reached the live aid unseen (10-30) and "backtests before encoding" (10-12): layer 4 time-honesty tests and the 12-item pre-reg before any run.
- Tests fixed to match the implementation: expected values hand-derived from FORMULAS.md; GPT writes spec tests from the spec, never from the code.
- Coordinators idle 8 h with READY work (10-30): lane floors, RED idle on the status board, watcher re-armed after compaction (stream F).
- Two workers built the same card (live-aid-news-panel): one writer per file set, claim before dispatch.
- 68 compactions, 39 lost work (10-15): the notes file is rewritten every wake, rebuilt from disk after compaction.
- Ultracode burned a 5 h window (10-26): default 2 workers, waves <= 4, `get_usage` before every spawn.
- Gemini "watched" a video and invented quotes: captions plus `verify_extract_quotes.py` exit 0 before any extract is used.
- Chat decisions never written (the Docker card ran): every operator decision lands in OPERATOR_DECISIONS.md the same turn.

## 6. Backlog by lane (filed 2026-10-30; the Planner feeds from here on LANE LOW)
| Lane | Cards filed today | Next seeds (not filed; file when the lane is low) |
|---|---|---|
| GPT (CODEX) | `gpt-audit-live-aid-indicators-vs-formulas`, `gpt-audit-analyst-levels-asof-rule`, `gpt-mutation-tests-sim-desk-conditions`, `gpt-audit-testnet-counting-rule-vs-bar` + the 6 formula audits already ready | spec tests for every live_aid `.js` maths file; re-derive of each layer review sheet's headline number; mutation tests on `analyst_levels.py` |
| Gemini (CODEX, `[GEMINI]`) | `gemini-review-gpt-formula-audits-1030`, `gemini-param-labels-live-aid-analyst-levels`, `gemini-doc-contradiction-scan-v1-plan`, `gemini-blind-read-layer-review-sheets` | blind read of every new research REPORT.md; labels on each new study in `sim_desk/studies` |
| Haiku | `haiku-refresh-stale-ready-cards`, `haiku-register-orphan-tests`, `haiku-recount-testnet-readout` | republish + `publish-record` after each page ship; one recount per worker claim |
| Sonnet | `testnet-trade-readout-daily` (JIS-NB lane, live host) + the 21 ready | per stream table above |
| Opus | none new (operator names them) | |

## 7. Super session 1 (kicked off 2026-10-30 from the desktop, login C, Sonnet)
Start line: `You are Supervisor. Run the super session per MyTradingSys/system/SUPER_SESSION.md for up to 24 h; never ask, take the
defaults. Programme: MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md (streams in order; feeder rule every wake).`
First wake, in this order: `get_usage` and `supervisor.py plan`; GPT lane (contradiction 5: claim, `codex_run.py tick`; signal
b-230ce8 `ack done` once a run lands); stream F: the Opus idle-bug card is operator-approved, start it; streams A, C, D: one Sonnet
Agent each on `layer-review-tom-guidance`, `testnet-trade-readout-daily` (ask the Lenovo by signal; it owns the live files),
`live-aid-replay-mode-fixture-feeds`; Haiku: `haiku-refresh-stale-ready-cards` (20 STALE flags block dispatch). Stop conditions
and hand-over per SUPER_SESSION D6; every wake ends with `supervisor.py watchcheck` exit 0.
