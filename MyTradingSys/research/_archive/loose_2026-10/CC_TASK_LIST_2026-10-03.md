# CC TASK LIST 2026-10-03 - follow-on work found while reading the TF5 lines

Session: MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec (Task B, read-only). Written 2026-10-03.
Scope: the lines TF5 Task A names (AT:57, :108, :121-139, :156-158, :206-219, :336; CFG:10; PS1:292; DO:438;
EX:125, :419-457, :541) and what they call. Every row below was read from disk this session.
Short names as in EXEC_PROVENANCE_AUDIT.md:10. AT.new = MyTradingSys/execution/auto_trader.py.new (TF5 staged).

Deduplicated against: BUILD_PIPELINE.md waves 0-9 (read in full, 137 lines), research/BUGS.md OPEN/IN-FIX rows
(read in full, 195 lines), and TF5 Task A itself. Dropped duplicates are listed in the last table.

Surfaces (SURFACE_POLICY.md sections 1 and 1b): App = Claude Win App, Code mode (reads/writes disk, runs tests,
commits). CLI-SUP = desktop CLI supervisor (owns live-process restarts and promotes). CLD = cloud session (committed
files only, no gitignored data, no Maven). NUC lane: none (T049 CLOSED, Qwen decommissioned 2026-10-01).
AIBridge (F:\AIBridge) is the PowerShell run-command surface for a web AI; no row below needs it.

Columns: file:line | current state | proposed change | gate | independence.
Batches group rows by file set; one batch = one CC session. No numeric cap (SURFACE_POLICY section 3).

## Batch 1 - TF5 promote (CLI-SUP; live path)

| # | file:line | current state | proposed change | gate | independence |
|---|---|---|---|---|---|
| 1.1 | execution/auto_trader.py, auto_trader_config.json, test_auto_trader.py (+ .new, .pre_tf5 beside each) | TF5 staged, not promoted; the running auto_trader still uses size 10, zone-TF time exit, no basis | promote the 3 .new files (backups .pre_tf5 already written), re-gate, restart auto_trader | run_all_tests.py --quick, Build-Check.ps1, then one live Tom alert: trade_attempt row carries basis, venue_entry, deribit_mark | first; blocks 2.1, 3.1, 4.1 and pipeline rows 7.1 (R7 lists 1.7) and 8.3 (LY3 stages the same config file) |

## Batch 2 - auto_trader fail-closed config load (App, stages .new; CLI-SUP promotes)

| # | file:line | current state | proposed change | gate | independence |
|---|---|---|---|---|---|
| 2.1 | AT:602 (AT.new:652) `load_json(Path(a.config), {})`; AT:93-97 load_json returns the default on OSError/ValueError | a missing or unparsable auto_trader_config.json is silent: the trader starts on DEFAULT_CONFIG (tom size 200, max_loss 25, verdicts without WAIT_RR, accounts {"layer:fabio:": "fabio"} only, AT:57-81). Fails open on a live path | refuse to start (log + exit non-zero) when the config file is absent or not a JSON object; no fallback to defaults | new test: unreadable config -> main() returns non-zero and places nothing (fails on pre-change code: it trades size 200); --quick | after 1.1 (same file); independent of every other batch |

## Batch 3 - basis measured at one instant (App for AT; CLI-SUP for PS1, a critical file)

| # | file:line | current state | proposed change | gate | independence |
|---|---|---|---|---|---|
| 3.1 | AT.new:243-265 apply_venue_price; PS1:165 (`$price = [double]$snap.current_price`, Binance), PS1:292 (card PRICE); AT:57 max_age_seconds 300 | TF5 E1a as specified: basis = Deribit mark at placement minus card PRICE at the card TIME. The two reads are up to 300 s apart, so market drift since the alert moves the limit with the basis (the limit follows the market, a partial chase) | read both legs of the basis at one instant: either AT reads Binance last at placement beside the Deribit mark, or PS1 Build-Card writes a Deribit mark line next to PRICE (PS1 is a DSA critical file: hash before/after) | test with a card PRICE 50 USD below the Binance read at placement: limit moves by the basis only; Build-Check if PS1 changes | after 1.1; decision first: which leg moves (operator or SUP) |

## Batch 4 - measure the TF5 values (App; reads gitignored logs, so not CLD)

| # | file:line | current state | proposed change | gate | independence |
|---|---|---|---|---|---|
| 4.1 | scripts/dev/funnel_report.py (TF2); execution/auto_trades.jsonl trade_attempt rows | funnel has no basis, venue_entry or deribit_mark column; TF5 writes them (AT.new:261-262) | add the three fields to the Tom funnel rows and a fill-rate line split pre/post TF5 (baseline: 7 of 9 no_fill, EXEC_PROVENANCE_AUDIT.md B.1) | test_funnel_report.py new case, fails before; --quick | can be built now; data only after 1.1 |
| 4.2 | AT.new:57-62 (max_hold_minutes 120, max_entry_seconds 600, flagged MEASURE) | values kept at what the live path already did; Ruling 3 accepted 2026-10-04 (OPERATOR_RULINGS_2026-10-02.md, MEASURED, testnet only) | write PRE_REG for both values (metric, n, decision rule) before any change; inputs: funnel 4.1, trade_ledger.jsonl | doc gate: Build-Check | after 4.1; not R7 (7.1 re-runs the BT target rule, not the live wait/hold) |

## Batch 5 - H5 items 4-6 that have no queue row (App docs; CLD can do 5.1-5.2 on committed files)

| # | file:line | current state | proposed change | gate | independence |
|---|---|---|---|---|---|
| 5.1 | SCB:48 (MIN_STOP_PCT), SCB:117-129 (0.2 % fallback, 0.1 % floor); MOB:255-259 mirror | NO-SOURCE engine rows A03/A04; 8 of 9 Tom plans carry exactly 0.2 % (EXEC_PROVENANCE_AUDIT.md E8b) | add a pipeline row (wave 4) for the operator decision: remove the fallback or source it; no code until ruled | pipeline row only | independent; blocker = operator |
| 5.2 | BUILD_PIPELINE.md:47 (1.8 TF6), :119 (7.1 R7); PM:609-614 | TF6/R7 Next cells do not name the E7 variant "stop stays structural after leg 1" (Q13, Q14 oppose the BE default) | append the variant to the 1.8 and 7.1 Next cells | doc gate | independent |

## Batch 6 - CL prompt composer (App; scripts/sched is not a live import)

| # | file:line | current state | proposed change | gate | independence |
|---|---|---|---|---|---|
| 6.1 | scripts/sched/pick_task.py:184-228 compose(); CLAUDE.md:9 ("Prompt <= 30 lines") | composer output is 37-40 lines (9 queue samples, CL_PROMPT_TEMPLATE_REVIEW_2026-10-03.md), over the cap; ~511 of ~682 est. tokens are standing text that CLAUDE.md or SURFACE_POLICY already carries | move the standing contract into CLAUDE.md once; compose() emits the 5-line row-specific template (review section 4) | test_pick_task.py: output <= 30 lines and carries no standing line (fails on pre-change compose) | independent; the CLAUDE.md edit and compose() ship in one commit |

## Dropped as duplicates or already decided

| found at | why no row |
|---|---|
| AT.new:332-333 layer time exit 8 x alert TF | EXEC_PROVENANCE_AUDIT.md E2-F: KEEP (Ruling 2), REMOVE@LIVE; not TF5 |
| AT:286 layer market entry, AT:64 stop 1 %, targets 2 % | E1-F, E8-F, E9-F KEEP; v3 places no order (H5 item 8) |
| V2/kXh:65 entry-before-proof label | BUGS.md B097 OPEN |
| 4Mo trade 1 golden scenario | pipeline 1.8 (TF6) already reads 4MoNjEQ2Dd8 v2 |
| EX:125, EX:419-457 limit wait / deadline | TF5 item 1(c): unchanged by design; EX:541 already takes the flag |
| DO:438 get_ticker | used as is; public, testnet base by default (DO:73, :146-147) |
| E4, E5, E6, E9 | H5 item 7: keep; revisit after 30 runner trades |
| LY3 config change (pipeline 8.3) | existing row; ordering note only (after 1.1, same file) |
| Build-Check rewrites BUILD_REPORT.md / session_log.json each run (seen this session) | BUGS.md B091 OPEN |

# END
