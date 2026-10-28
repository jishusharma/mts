# MTS picture and plan of actions (Eagle_Eyes draft, corrected by an Opus review, 2026-10-28)

Draft: Eagle_Eyes (Sonnet observer). Review: Opus session `opus-picture-review`, worktree on origin/fast-track as of 2026-10-28 ~17:35Z. Source of the ask: `MyTradingSys/system/EAGLE_EYES_BIBLE.md` (operator, verbatim).
Tags: SOURCED = read in a file (path:line) or on a web page this session; OURS = reasoning or arithmetic of this review; NOT_IN_DATA = not visible from this host.
Host note: this review ran on JIS-NB (the desktop). The live testnet loop runs on DESKTOP-F7IU69N (the Lenovo laptop). Everything "live" below that is not NOT_IN_DATA comes from the stale mirror `runtime_data/_mirror` (copied 2026-10-27 13:13Z, data up to 2026-10-20 17:45Z; the mirror marks itself "NOT LIVE. Data only").
Section 7 lists every correction made to the draft.

## 1. What MTS is for

- Final goal: a first mainnet BTC trade on whatever fee-net edge exists, even the simplest one (SOURCED Bible). Today: testnet only, Deribit test, BTC-PERPETUAL (SOURCED CLAUDE.md; `execution/auto_trader.py:6-7` "no mainnet path").
- Rule that decides what trades: layers, no fixed core, fee-net out-of-sample results decide (SOURCED CLAUDE.md). Promotion is default-deny: a source trades for real only when it is in `execution/promoted_setups.json`, which is EMPTY (`"entries": []`, SOURCED). Every testnet trade today runs on a "grandfathered" calibration list, explicitly "not an edge claim" (SOURCED `execution/auto_trader_config.json` `pre_pipeline_sources`; all `review_by` dates 2026-10-23 have passed and are not enforced, `_pre_pipeline_note`).
- The operator's own practice: take a bias, build a position, trade the setups Tom describes, read the chart from screenshots (SOURCED Bible). MTS does not encode this method today (section 3).

## 2. What is built, and where the value is

| Part | State (verified) | Value |
|---|---|---|
| Simulator / desk (backtest, scenario replay, Krown/RSI studies) | built and used; ledger of 281 trial rows / about 3,018 cells read (SOURCED `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md` s.2). E2 Krown S8 4h = INCONCLUSIVE; a desk cross-check of its mechanics was approved 2026-10-28 (SOURCED `system/OPERATOR_DECISIONS.md:1361-1363`) | the real asset today: it has shown, cheaply, what is NOT an edge |
| Edge verdict across all families | Tom, Fabio, Krown: UNTESTABLE-AS-BUILT; Malkan intraday, Levels: DEAD. Every 1m-2h family is dead on cost: best gross effect ever measured on DEV 3.8 bp/trade vs a 14 bp round trip (SOURCED R1 s.1, s.3; `breakeven.csv:2-14` cited there) | tells us where not to spend more |
| The one fee-net OOS PASS | unlevered spot-perp funding carry: net 15.35 % DEV, 12.06 % VAL, 6.26 %/yr HOLD; the 2025-07+ window is SEALED, unread, waiting on one operator line (SOURCED `research/carry_basis_2026-10-18/EXECUTABILITY.md` s.2, s.4). It is a yield, not a BTC trading edge, and the testnet path has no spot leg (SOURCED same, s.3). It already fired GO-PRIVATE trigger B (SOURCED `research/STATUS.md` line "GO-PRIVATE: A=0 B=1 TRIGGER B:carry_basis_2026-10-18") | the only candidate for "the simplest edge" (section 5) |
| Layers wired to the live alert runner | turn_of_candle, rsi (cross/failure/support/rejection), malkan, session, positioning, fabio (cvd_absorption, escalation, volume_fvg), cryptocred (sr_flip, fib_pullback, failed_msb), levels, rsi_divergence, session_levels, bb_top_reversal, candle_close, wlow_bounce (SOURCED `auto_trader_config.json` accounts/size_overrides; `backtest/layers/alerts/live_*.py`) | the inputs that fire today; none promoted |
| Flow layers in research (CVD, net delta, OI, top-trader ratios, liquidations, CoinGlass Whale Index) | concepts and usage notes only (SOURCED `research/flow_layers_concepts_2026-10-28`, `research/coinglass_usage_2026-10-28`); not wired live. Binance keeps only 30 days of ratio history (SOURCED `coinglass_usage_2026-10-28/B_positioning.md:48,52`) | bias context; cannot be backtested until we record them ourselves |
| WaveTrend | card `items/T061_wavetrend_lazybear.md`; 9 desk cells read (SOURCED R1 s.2) | one more indicator; no edge shown |
| Live engines on the laptop (three, not one) | (a) Tom apparatus `scripts/core/start-trading-day.ps1`: verdict loop, popups via `show-alert.ps1`, counter `runtime_data/alert_counter.txt`; (b) layer alert runner `backtest/layers/alerts/live_runner_cli.py` -> `alert_emitter.append_alerts_jsonl` -> `MyTradingSys/runtime/alerts/<tf>.jsonl` (no popup); (c) `execution/auto_trader.py` reads both and trades testnet through new_plan -> executor -> position_manager (SOURCED those files). Current run state: NOT_IN_DATA | the loop exists end to end on testnet |
| Live dashboard v1 | requirements only: `tools/live_aid/REQUIREMENTS.md` R01-R10; no dashboard code on trunk (SOURCED `ls tools/live_aid`); being designed by session dash-designer | one screen while in a position (R01) |
| Eagle_Eyes live reads | `research/live_reads`; 34 screenshots landed, 33 overdue (SOURCED `research/STATUS.md` Screenshots) | cross-check of engine against the chart |
| Gate board (trader sources) | tom, fabio, malkan, krown all at G2; "NO GATE MOVED IN 24h"; research share of commits 24 %, "other" 72 % (SOURCED `research/STATUS.md` Gate Board) | the process is busy, not moving gates |

## 3. Alerts and testnet trades: what the data shows

### 3.1 What fires as alerts
| Producer | What it fires | Shown to the operator? | Evidence |
|---|---|---|---|
| Tom apparatus | popup when the verdict, zone, price or STATE changes and verdict is SETUP_FORMING/SETUP_CONFIRMED, or the change text matches STATE/ADVERSE/STOP NEAR/TARGET NEAR; suppressions for open position, cooldown, scalp preconditions | yes, one PowerShell window per alert | SOURCED `start-trading-day.ps1:693-697,700-760`. Last mirrored: #508, 2026-10-20 15:05Z, VERDICT NO_TRADE "no candidates" (SOURCED mirror `last_alert.json`, `alert_counter.txt` = 508) |
| Layer alert runner | layer events per timeframe to JSONL. Mirror tail (last 300 rows per file, counts only): 1m 300 (268 turn_of_candle toc_m14, rest levels), 5m 300 (234 rsi cross, 32 failure, 22 support, 12 rejection), 15m 300 (97 rsi cross, 39 fabio, 45 cryptocred sr_flip, 34 fib_pullback, ...), 1h 113 | NO: no popup, no UI; only the auto-trader reads them | SOURCED mirror `MyTradingSys/runtime/alerts/*.jsonl` (OURS count); `live_runner_cli.py` has no popup call (grep) |
| tape-watch sidecar | popup "TAPE #n - <divergence>" on non-neutral CVD/OI divergence, cooldown 180 s | yes, separate window | SOURCED `scripts/live/tape-watch.ps1:4,87-91` |
| live health check | popup "MTS live health RED" when the failing set changes or every REPOPUP_SEC | yes, separate window | SOURCED `scripts/sched/check_live_health.py:91-105` |
| `alerts` console command | prints the last 10 "ALERT #" lines of `runtime_data/apparatus_log.txt` | text only | SOURCED `scripts/live/alerts.ps1` |

Answer to the operator (OURS): alerts DO fire, a lot, but the operator only ever sees Tom verdict-change windows. All layer alerts (several hundred per day in the mirror) go silently into JSONL. His bias-and-position (Tom) setups are not encoded as an alert at all: the apparatus pops on verdict changes of the Tom engine, which is a tested-and-dead encoding (R1 s.1), not his discretionary read. T067 (event alerts, absorption at marked zones, "buy detection") is still OPEN since 2026-10-05 (SOURCED `items/T067_alert_improvements.md`).

### 3.2 Why the popups pile up (SOURCED `scripts/core/show-alert.ps1`, OURS reading)
1. One new PowerShell process and one window per alert, from three producers that do not know each other.
2. The only "kill the previous popup" step (`start-trading-day.ps1`, before `Start-Process wscript.exe`) matches window titles `"MTS #"`. The default title is `"MTS ALERT #n"` (alert #508 had it), tape titles are `"TAPE #n"`, health titles `"MTS live health RED"`: none match, so those windows are never cleaned up.
3. `TopMost = $false` and `FormBorderStyle = FixedToolWindow`: the window sits behind the IDE and a tool window has no taskbar button, so a buried popup cannot be found except by moving windows.
4. Position cascades by alert number modulo 6 (40 px steps from 40,40): windows overlap in the top-left corner over whatever the operator is reading.
5. `ShowWithoutActivation = true` is set, but the form is opened with `ShowDialog()`; OURS (to test): the no-activation override is honoured by `Show()`, so the popup may still take focus. A 600x680 fixed window with a 5-minute auto-close and a beep per alert.

### 3.3 Testnet trades fired by the engine
- Live host, now: NOT_IN_DATA (owner DESKTOP-F7IU69N; `sync.py start` refused the mirror: "copy is from JIS-NB but the owner is desktop-f7iu69n").
- Stale mirror, 500 rows 2026-10-17 22:15Z .. 2026-10-20 17:45Z of `execution/auto_trades.jsonl` (counts only, OURS): 0 trades placed; 414 `skipped_halt` with brakes HALT + HALT_DAILY_LOSS; 85 `signal_rejected` (37 "unmapped rsi:cross", 18 verdict WAIT_PROOF, 7 WATCH, 4 stale, 2 WAIT_TRIGGER). Signals by source: turn_of_candle 267, rsi 100, tom 42, cryptocred 31, levels 29, fabio 18, others 13.
- Reading (OURS): in the last mirrored window the auto-trader was braked and traded nothing; whether it trades today is unknown here and must be read on the laptop (Plan step 1).
- The operator's own discretionary Deribit trades are account data: not recorded in this public repo (the draft's per-trade numbers were removed, section 7).

## 4. Gaps on the way to mainnet (verified)

| # | Gap | State | Tag |
|---|---|---|---|
| G1 | No validated BTC trading edge; intraday is dead on cost; only carry passed and it is a yield | R1 s.1-s.3; carry EXECUTABILITY s.2 | SOURCED |
| G2 | Alerts not visible: layer alerts have no UI; popups pile up and hide; operator's method is not an alert | section 3 | SOURCED + OURS |
| G3 | Operator's discretionary trades are not journaled with the layer state at entry/exit (journal must stay out of the public repo) | no such journal found under `execution/journal` (it holds auto plans only) | OURS |
| G4 | Flow series history: Binance ratio history is 30 days only; liquidation tape has no recorder host | `coinglass_usage_2026-10-28/B_positioning.md:52` | SOURCED; recorder host NOT_IN_DATA |
| G5 (corrected) | Trunk CI is GREEN, not red: `CI green: 5bf37d8f6 (2026-10-28 23:02 IST)`; deploys only ever take `origin/green/fast-track`, so a red tip does not block a deploy of the last green | `make_status.py` output 17:37Z; `DEPLOY_RUNBOOK.md:18,32` | SOURCED |
| G6 (corrected) | Disk: JIS-NB C: 12 GB free (hook warns < 15 GB); the laptop's C: (live host, one drive, no F:) is NOT_IN_DATA | `df` this session; `LIVE_HOST_MOVE.md` s.1 | SOURCED / NOT_IN_DATA |
| G7 (new) | F-GAP-1, BLOCKS-LIVE: a restart between entry fill and stop journal leaves the position with no stop; `_manage_impl` still raises "journal has no entry/stop - nothing to manage" | `R3_LIVE_REDTEAM.md` s.1; code unchanged at `execution/position_manager.py:341-342` on trunk | SOURCED |
| G8 (new) | Live exits are a fixed 1 %/2 %/8-bar bracket that no backtest used (97 % time exits) | `R3_LIVE_REDTEAM.md` F-T09-2 | SOURCED |
| G9 (new) | Promotion gate empty: `promoted_setups.json` has 0 entries; all testnet trading is grandfathered; review dates expired 2026-10-23 | `auto_trader_config.json` | SOURCED |
| G10 (new) | Brakes: in the mirror the auto-trader sat on HALT + HALT_DAILY_LOSS for 414 of 500 decisions; current brake state NOT_IN_DATA | mirror | SOURCED (stale) / NOT_IN_DATA |
| G11 (new) | Carry needs a spot leg, delta-neutral sizing, funding accounting, margin watch; none built; mainnet would be operator-run and needs going private first | `EXECUTABILITY.md` s.3 | SOURCED |
| G12 (new) | Repo is public while GO-PRIVATE trigger B is set | `STATUS.md`; CLAUDE.md "go private at mainnet or the first fee-net OOS pass" | SOURCED |

## 5. What MTS needs next, ranked (OURS; blunt)

Blunt summary: nothing in MTS is a proven BTC trading edge. The only fee-net out-of-sample PASS is carry, a funding yield that has decayed every year (15.35 -> 12.06 -> 6.26 %/yr) and whose latest year is unread. A first mainnet trade "on the simplest edge" therefore means either carry (a yield) or a tiny mechanical test trade with no edge claim. Everything else is unproven.

| Rank | Step | Why first | Done when |
|---|---|---|---|
| 1 | Operator one-liner on carry: approve the single sealed 2025-07+ read, and say whether carry alone justifies going private | the only PASS; one read decides it; costs one script run | answer recorded in OPERATOR_DECISIONS.md; read run by its card; PASS/park written to `carry_basis_2026-10-18/RESULT.md` |
| 2 | Fix F-GAP-1 (re-place the stop or flatten + HALT when the journal shows a fill and no stop) with the failing test from R3 | a naked position on restart is unacceptable on testnet and fatal on mainnet | test fails on old code, passes on new; shipped; deployed by the live owner only |
| 3 | Read the laptop's live state (owner session): alert counter, last 7 days of `auto_trades.jsonl` and `runtime/alerts/*.jsonl` as counts, brake files present | the operator asked "what fires, what trades"; this host cannot see it | one table of counts by source/event/outcome posted back; no account numbers in the repo |
| 4 | Alert Dock (spec: `ALERT_DOCK_SPEC.md`): one window, all producers, layer alerts visible, no pile-up | the operator's direct ask; makes the system observable | spec tests pass; owner deploys in a restart window |
| 5 | E1 counts-only power screen for 4h-and-up families (Krown S5/S8, Malkan 1d/1w, pitchfork 1d) | cheapest remaining test of whether any trading edge can be powered (about 15 Sonnet turns, zero sealed reads) | R1 E1 pass rule applied; PASS -> E2 card, FAIL -> trading-edge program stops |
| 6 | If carry PASSes: go private, then build the minimum carry path (spot leg, delta-neutral sizing, funding accounting, margin watch) and a mainnet plan the operator runs by hand at the 50 USD notional cap | it would be the first mainnet trade on the only edge we have | operator decision; MAINNET_READINESS_CHECKLIST.md rows green; operator places the trade |
| 7 | Operator trade journal (private, outside the repo): time, side, his reason, layer readings at entry/exit | the only way to turn his discretionary method into a testable rule | schema in repo, data outside it; first 20 trades logged |
| 8 | Align live exits with what was backtested (G8) before any layer is promoted | otherwise backtest verdicts say nothing about live results | bracket from the promoted study, test proves it |
| 9 | Record flow series ourselves (ratios, liquidations, OI) on a named host | without history these layers can never be tested | recorder host named in DEVICES.md; 30 days stored |

Not proven (OURS, say it plainly): Tom setups as encoded; Fabio v3; RSI divergence; Levels ladder; Krown S5 (n=35, CI crosses zero); any flow layer; carry beyond 2025-06; whether the laptop auto-trader trades at all today.

## 6. Alert redesign (summary; full spec in `ALERT_DOCK_SPEC.md`)

Modern practice (SOURCED web, read 2026-10-28; links in the spec): one notification surface, not a window per alert; replace-by-key and group-by-key instead of stacking duplicates (Windows toast tag/group, PagerDuty dedup_key); cap the visible stack at about 3 (Maersk) or 1 (Canva); duration per severity, timer paused on hover, always a close control; never steal focus (WS_EX_NOACTIVATE, status-not-alert semantics); snooze/silence per alert kind with an expiry; a history list behind the stack.
MTS redesign: one single-instance "MTS Alert Dock" docked to a screen corner; all producers append to one inbox file instead of spawning windows; cards grouped by key with a repeat count; four severities; max 3 cards visible, the rest in a history drawer; pin, snooze 15 min / 1 h, close, close-all; never takes focus; remembers its corner per monitor. Spec and tests only; the live owner deploys.

## 7. Corrections made to the Eagle_Eyes draft

| # | Draft said | Verified | Change |
|---|---|---|---|
| C1 | One "live engine + alerts" | three producers (Tom apparatus, layer runner, tape-watch) plus a health popup, and a separate auto-trader | section 2 row and 3.1 rewritten |
| C2 | Only alert content seen is a NO_TRADE card; whether setups fire NOT_IN_DATA | mirror holds about 1,000 layer alert rows that are never shown; the apparatus pops on state changes, not only actionable verdicts | 3.1 |
| C3 | Popup "not top-most" is the likely pile-up cause | true but partial: the kill-previous step's title regex misses "MTS ALERT #n", "TAPE #n" and health titles; tool window has no taskbar button; one process per alert; ShowDialog vs ShowWithoutActivation | 3.2 |
| C4 | auto_trades NOT_IN_DATA | right for live; the mirror shows 0 trades placed, 414 halted, 85 rejected | 3.3 |
| C5 | Operator's Deribit trade with contracts, price and net BTC | account/order data in a PUBLIC repo (hard rule) | removed |
| C6 | G1 "no validated edge" without the carry PASS | carry is the only fee-net OOS PASS and set GO-PRIVATE trigger B; intraday cost wall 3.8 bp vs 14 bp | G1, rank 1, section 2 |
| C7 | G5 trunk CI RED, nothing deploys | CI green 5bf37d8f6; deploys take the last green SHA anyway | G5 corrected; plan step "fix CI first" dropped |
| C8 | G6 about 7 GB free on the desktop | JIS-NB 12 GB now; laptop (live host) NOT_IN_DATA | G6 |
| C9 | Dashboard v1 "being built" in `tools/live_aid` | only REQUIREMENTS.md R01-R10 on trunk; T067 lives in `items/`, not `tools/live_aid` | section 2 |
| C10 | Layers list (CVD, OI, ratios, liquidation) as the layers | those are research only; the live-wired layers are a different list | section 2 |
| C11 | Missing gaps | added G7 F-GAP-1 (BLOCKS-LIVE), G8 exit mismatch, G9 empty promotion, G10 brakes, G11 carry path, G12 public repo vs trigger | section 4 |
| C12 | Plan: "staging and restart by the desktop supervisor" | the live host is DESKTOP-F7IU69N (laptop); its owner deploys and restarts | plan ranks 2, 4 |
| C13 | Plan order: CI fix and data capture early | re-ranked by information per cost and by what blocks a mainnet trade | section 5 |

## 8. Open points for the operator (defaults apply if no answer)

- Carry: one sealed read yes/no, and go private on carry alone yes/no. Default: no read until he says yes (sealed data rule).
- Which two or three of his Tom setups should become alerts first. Default: none invented; the Dock shows what already fires.
- Where the Dock sits (corner, which monitor). Default: bottom-right of the primary monitor, movable, remembered.
