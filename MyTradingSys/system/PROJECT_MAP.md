# PROJECT MAP (generated 2026-10-15, definitions as of 2026-10-09; do not hand-edit)
# Source of truth: MyTradingSys/system/groups.json (definitions, path claims, row assignments, focus lines) + MyTradingSys/research/BUGS.md (rows).
# Regenerate: python scripts/dev/make_groups.py. Which group is a row in: python scripts/dev/make_groups.py --of B146.
# Purpose: one answer to "which section does this belong to". Counts are registry rows, not percentages; they are not a measure of how finished a group is.
# Counts are frozen at generation time; the live one-line version is the GROUPS line in research/STATUS.md.

## How the groups fit
```
 SRC   what the traders said ── rules ──►  CORE  Tom engine ── verdicts ──┐
                                             ▲                            ▼
 DATA  feeds and snapshot ── snapshot ───────┤                          EXEC  testnet orders, risk
                                             │                            ▲
 DATA  candles, OI, order flow ──────────►  LAYR  modules ── fires ───────┘
                                             (never gate CORE)

 EVID  replays CORE and LAYR fires on DATA history: do they catch big, profitable moves?
 VIS   charts and screenshots: checks DATA, CORE and LAYR against what the operator sees
 DESK  the operator's window onto all of it     OPS  sessions, workers, process     INFRA  machines, plumbing
```

## Progress at a glance
| Group | What it is | Open (HIGH) | Closed | Won't fix | Files | Live path |
|---|---|---|---|---|---|---|
| **DATA** | Market data and snapshot engine | 5 (0) | 29 | 16 | 84 | yes |
| **SRC** | Rule sources and extraction | 4 (0) | 9 | 4 | 293 | no |
| **CORE** | Tom core engine and verdicts | 4 (0) | 30 | 11 | 55 | yes |
| **LAYR** | Independent layers (switchable modules) | 8 (1) | 7 | 3 | 217 | yes |
| **EVID** | Backtest and evidence | 14 (2) | 4 | 8 | 103 | no |
| **EXEC** | Execution and risk (Deribit testnet) | 7 (3) | 10 | 0 | 124 | yes |
| **VIS** | Charts, screenshots and observation | 1 (0) | 1 | 0 | 38 | no |
| **DESK** | Operator interface (DSA and live desk) | 2 (1) | 9 | 4 | 35 | no |
| **OPS** | AI workforce and process | 16 (4) | 25 | 5 | 1461 | no |
| **INFRA** | Machines, runtime plumbing, housekeeping | 7 (3) | 12 | 3 | 147 | yes |
| | all rows | 68 (14) | 136 | 54 | 2557 | |

## DATA - Market data and snapshot engine
The Java feed and snapshot producer, kline / open-interest / order-flow recorders, funding, higher-timeframe context, and the volume profile, VWAP and CVD numbers the snapshot carries.

- Operator's words: "the data from the Java engine"
- Start reading: `MyTradingSys/market_data/data_state_document.md`, `MyTradingSys/market_data/data_schema_v1.2.0.md`
- Who works on it: Code session (Sonnet) for Python; Java needs mvn compile and a supervisor restart window
- Where it lives: `src/`, `pom.xml`, `MyTradingSys/market_data/`, `MyTradingSys/data/`, `MyTradingSys/runtime/oi_live/`, `MyTradingSys/runtime/orderflow_live/`, `MyTradingSys/research/htf_context/`, `runtime_data/naked_pocs/`, `scripts/dev/refresh_klines.py`, `MyTradingSys/runtime/kline_archiver.py`, `MyTradingSys/runtime/update_market_state.py`, `MyTradingSys/runtime/test_update_market_state.py`
- Progress is tracked in: registry rows plus the bigtrade findings F-BT-09..16 (not yet in the registry)
- Focus (hand-written, as of 2026-10-09): Running. Known defects not yet fixed: Java volume profile does not conserve volume (POC 300-690 points off), snapshot OI is hourly-stepped with 46 h of recorder holes, VWAP anchor says 13:30Z but is 00:00Z, naked-POC list frozen since 2026-08-28 (bigtrade FINDINGS F-BT-09..16). Java fixes wait for a restart window.

| Open item | Sev | Status | Title |
|---|---|---|---|
| B141 | MED | OPEN | htf_context_live bal_4h / bal_1d are null on every row: NS-fixed k_bal 0.8 balance rule is satisfied by 0.4% ( |
| B163 | MED | OPEN | operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff (daily SMA200 trend engine + 15m/1h liquidity sw |
| T042 | MED | OPEN | Snapshot schema lacks 4h/daily/weekly structure and OI/CVD peak reference; producer gap feeding T041 |
| B161 | LOW | OPEN | screenshot indicator header values (BB, RSI, VWAP) are hand-typed and recomputed ad hoc per read; no check too |
| T044 | LOW | OPEN | Hybrid run mode divergence alert; REST vs WebSocket >3pt divergence must alert, not silently override |

## SRC - Rule sources and extraction
What the traders said and how it becomes a rule: transcripts, extracts, the verbatim-quote gate, provenance (every parameter from a quote or it does not exist), the analyst pipeline.

- Operator's words: "Tom's rules, transcripts, extracting"
- Start reading: `MyTradingSys/PROJECT_VISION.md`, `scripts/dev/verify_extract_quotes.py`
- Who works on it: Code session (Sonnet); extraction judgment by Opus
- Where it lives: `extracts/`, `raw_transcripts_canonical/`, `MyTradingSys/PROJECT_VISION.md`, `scripts/dev/verify_extract_quotes.py`, `scripts/dev/test_verify_extract_quotes.py`
- Progress is tracked in: registry rows; there is no extraction-coverage tracker (PROJECT_VISION gap classes 1-2)
- Focus (hand-written, as of 2026-10-09): Tom transcripts still extracting. PROJECT_VISION gap classes 1 and 2 (rule not extracted, extracted wrong) have no coverage mechanism. NO-SOURCE parameters are flagged but not resolved (B117, B142-B145, B153).

| Open item | Sev | Status | Title |
|---|---|---|---|
| B119 | MED | OPEN | Revalidation items gated on desktop or operator: 9 papers unopened, W3 kappa has no clean reader, T2 run needs |
| B120 | MED | OPEN | Tom provenance audit doc follow-ups from W3 and revalidation not delivered |
| B139 | MED | OPEN | CBP adapter (queue/cbp_adapter.py) has no tracked item; candidates file never produced on the real queue; anal |
| B167 | MED | OPEN | PROJECT_VISION.md is stale (last real edit 2026-09-28, 833 commits behind): what is missing from the vision |

## CORE - Tom core engine and verdicts
The deterministic rule engine: compiled_engine, condition files, proof counting, setup states (WAIT_PROOF to SETUP_CONFIRMED), net_rr, the math object and start-trading-day.

- Operator's words: "the rules that are coded and applied to the data; Tom is core"
- Start reading: `MyTradingSys/runtime/compiled_engine.md`, `MyTradingSys/system/COMPILED_DECISIONS.md`
- Who works on it: Code session (Sonnet) with tests from the spec; live-path files go through the supervisor
- Where it lives: `MyTradingSys/conditions/`, `MyTradingSys/runtime/compiled_engine.md`, `MyTradingSys/system/COMPILED_DECISIONS.md`, `MyTradingSys/system/net_rr_floor.json`, `MyTradingSys/system/runner_min_distance.json`, `MyTradingSys/research/core_readiness_2026-09-27/`, `MyTradingSys/runtime/`
- Progress is tracked in: registry rows; SUPERVISOR_LOG.md for live-path claims
- Focus (hand-written, as of 2026-10-09): Running. Evidence is weak: Tom gross R is -0.15 [-0.29, +0.04] before fees, and the live rule shows 0 signals where an older run on the same history showed 19 (B147). Admission thresholds are unsourced (B117, B153).

| Open item | Sev | Status | Title |
|---|---|---|---|
| B063 | MED | OPEN | Divergence handling fragmented; no dictionary definition, no condition-file rule, no verdict consumer |
| B117 | MED | OPEN | Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING in start-trading-day.ps1 |
| T052 | MED | OPEN | Define a Tom-cited trigger for SETUP_CONFIRMED, per operator D6b ruling (not removal) |
| B074 | LOW | OPEN | Rule-order dependence in Compute-Verdict: contradiction cap runs before the broken-value override |

## LAYR - Independent layers (switchable modules)
Everything that sits on top of Tom and never gates it: RSI / Malkan, CryptoCred, Fabio, session frame, positioning, tick delta, timeframe layer, turn-of-candle, consensus, probability, options (Deribit), WaveTrend, alerts.

- Operator's words: "every other indicator system is a separate layer"
- Start reading: `MyTradingSys/backtest/layers/FORMULAS.md`, `MyTradingSys/PROJECT_VISION.md`
- Who works on it: Code session (Sonnet); formulas from FORMULAS.md, never from existing code
- Where it lives: `MyTradingSys/backtest/layers/`, `MyTradingSys/options/`, `MyTradingSys/research/malkan_rsi_2026-09-28/`, `MyTradingSys/research/t067/`
- Progress is tracked in: registry rows plus the bigtrade capture matrix (lift per layer and side)
- Focus (hand-written, as of 2026-10-09): Built, none proven: 0 of 34 layer/side rows reach lift 1.15 at 96 bars with r 1.5, k 3 (capture matrix 2026-10-09). turn_of_candle is 79 % of live testnet trades but failed its backtest (F-BT-02, awaiting an operator yes/no). Freeze on new layers stands until B146-B148 report.

| Open item | Sev | Status | Title |
|---|---|---|---|
| T040 | HIGH | OPEN | Tick-based delta layer: standalone Python process subscribing to raw tick feed, computing fast deltas over rol |
| B143 | MED | BLOCKED | CryptoCred 0.1 percent stop buffer and 1.5R target are NO-SOURCE |
| B144 | MED | OPEN | Exhaustion proxy (SCB volume 2.0x over 240 one-minute bars) is NO-SOURCE; tag SCREENER |
| B162 | MED | OPEN | Qriptal (Habib) signal layer: operator asks for his Discord feed, his past record verified, and his calls trad |
| B177 | MED | OPEN | operator: Control Room 'Layer Board' tab - per active layer: dev/test activity, combined indicators, step coun |
| B179 | MED | OPEN | operator: turn the Tom and Fabio layers story (principles and concepts) into a slide deck artifact so the oper |
| T034 | MED | OPEN | Add Net Longs / Net Shorts / (New) positioning states from OI + CVD cross |
| T061 | MED | OPEN | WaveTrend with Crosses [LazyBear] integration as a separate indicator layer (module, never core, never a Tom f |

## EVID - Backtest and evidence
The harness, trial registry, holdouts, the big-trade study and capture matrix, and the research questions we answer with data (hypothesis queue).

- Operator's words: "back test so layers fire on big, profitable trades"
- Start reading: `MyTradingSys/backtest/layers/FORMULAS.md`, `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md`
- Who works on it: Code session (Sonnet); verdict wording by Opus; one HOLDOUT look per layer
- Where it lives: `MyTradingSys/backtest/`, `MyTradingSys/research/bigtrade_2026-10-09/`, `MyTradingSys/research/btc_ma_2026-10-03/`, `MyTradingSys/research/candle_patterns_2026-10-04/`, `MyTradingSys/research/p1_cost_floor/`, `MyTradingSys/research/session_sweeps/`
- Progress is tracked in: the registry has almost no rows for this group: progress is the bigtrade PLAN.md steps A-F and FINDINGS.md
- Focus (hand-written, as of 2026-10-09): Big-move ground truth (A), kline fire history (B1), capture matrix and exit policies (C) are done; order-flow fires (B2), walk-forward tuning (D), gap list (E) and chart observations (F) are not. Operator 2026-10-09: tune layers toward big profitable trades, labelled BT-TUNED, never written to live files by a worker.

| Open item | Sev | Status | Title |
|---|---|---|---|
| B171 | HIGH | OPEN | operator: get a profitable imbalance indicator into the Armory (implement, backtest, run on testnet); repo sho |
| T081 | HIGH | OPEN | Backtest D: walk-forward tuning of stop_buffer_atr (stop = structure +/- k x ATR) for Tom and every tight-stop |
| B154 | MED | OPEN | No regime-stratified and no session-stratified backtest verdict exists; every reported edge is one aggregate n |
| B185 | MED | OPEN | Build-Check passes an over-wide BUGS.md row silently: bars inside an evidence cell split it and Bugs still rep |
| T051 | MED | BLOCKED | Backtest on MTS raw verdict done; parked by operator 2026-09-26; reopens only when T050 phase 4 + B071 fixed |
| T053 | MED | OPEN | Two-account hedge / leveraged BTC scalping research (hedge thresholds, fee cover, trigger conditions) |
| T054 | MED | OPEN | US session / pre-market alert, US-equity and BTC correlation, news sentiment research |
| T055 | MED | OPEN | Positioning flow (Net / New Longs and Shorts) and proven BTC setups research |
| T058 | MED | OPEN | Broken lows/highs by timeframe: continuation vs liquidity sweep |
| T060 | MED | OPEN | Low-volatility anomaly: does trailing realized-vol rank predict BTC forward return at any horizon MTS can comp |
| T082 | MED | OPEN | Re-run the capture matrix and the Tom core backtest after the Stage 1 data fixes land (volume profile, naked P |
| T083 | MED | OPEN | Lead check: rsi_events 1h (3 of 3 live testnet wins, +9.75 USD) on full 2022-2026 history with fees |
| T084 | MED | OPEN | Lead check: fabio escalation 1h (best capture-matrix lift 1.24-1.38 at 24 bars, small n) with walk-forward and |
| T090 | MED | OPEN | 7h timeframe research under playbook PART I (who uses it, anchor, any tested evidence) |

## EXEC - Execution and risk (Deribit testnet)
Everything that places or protects an order: auto_trader, position_manager, daily-loss monitor, orphan watchdog, deribit_orders, runner, kill switch, fee model, subaccounts.

- Operator's words: "testnet trades, maximise testnet trades"
- Start reading: `MyTradingSys/execution/README.md`
- Who works on it: Code session writes in a worktree; ONLY the supervisor deploys, restarts, touches HALT files or opens trades
- Where it lives: `MyTradingSys/execution/`, `scripts/live/`, `MyTradingSys/research/testnet_status/`
- Progress is tracked in: registry rows; MyTradingSys/research/testnet_status/ reports; SUPERVISOR_LOG.md
- Focus (hand-written, as of 2026-10-09): Testnet live: 333 closed trades 2026-09-28..10-08. Requested first by the supervisor (2026-10-09): B148 daily-loss monitor re-authenticates as MAIN, B146 no minimum stop width, B147. All still OPEN.

| Open item | Sev | Status | Title |
|---|---|---|---|
| B148 | HIGH | IN-FIX | Daily-loss monitor re-authenticates as the MAIN account when a named subaccount token expires; it also silentl |
| T048 | HIGH | OPEN | Satellite framework + exchange API layer; operator goal is API-ready trading with MTS |
| T086 | HIGH | OPEN | Go-live bar for real money: written, operator-signed criteria (proposal = Control Room decision D06-gate) |
| B123 | MED | OPEN | Zero-trade and QUIET family follow-ups from the 2026-09-30 maintainer report: Tom main and fabio jishu_3 after |
| T085 | MED | OPEN | 97 % of testnet trades end on the time exit: find why targets/stops are almost never reached and fix exits so  |
| B121 | LOW | OPEN | Bar-aligned polling and 5 s auto_trader poll not landed; live_runner_cli 60 s and auto_trader 20 s defaults un |
| B122 | COSMETIC | OPEN | auto_trader.py reject text uses alert.get('event') instead of the fallback key |

## VIS - Charts, screenshots and observation
The operator's eyes: TradingView and CoinGlass charts, footprint and heatmap panels, random screenshots with a meaning, missed-trade capture, the chart-read method. Finds what the data pipeline misses.

- Operator's words: "screenshots are a completely different view"
- Start reading: `MyTradingSys/methodology/screenshot_intake.md`, `MyTradingSys/methodology/chart_read_protocol.md`
- Who works on it: Any session via the hook; chart sets read by Sonnet or better
- Where it lives: `MyTradingSys/observation/`, `my_charts/`, `MyTradingSys/research/screenshots/`, `MyTradingSys/research/missed_trades/`, `MyTradingSys/research/visual_validation_protocol_vvp002.md`, `MyTradingSys/methodology/chart_read_protocol.md`, `MyTradingSys/methodology/screenshot_intake.md`, `MyTradingSys/methodology/observation_capture_protocol.md`, `scripts/dev/shot.py`, `scripts/dev/test_shot.py`, `runtime_data/screenshot_extracts/`
- Progress is tracked in: the registry has no rows for this group yet: progress is `python scripts/dev/shot.py status` (also the Screenshots block of STATUS.md)
- Focus (hand-written, as of 2026-10-09): Intake pipeline built 2026-10-09 (scripts/dev/shot.py, hook, template). 22 images recovered into the store: 9 non-charts closed, 13 charts classified and not closed (9 analysed by the bigtrade study but not yet linked, 4 from 2026-10-02 never read). Standing gaps: operator drawings are stored nowhere, T066 (read TradingView layouts) blocked since 2026-10-05, DSA chat cannot save images, the hook is active only after the supervisor deploys it to the live tree.

| Open item | Sev | Status | Title |
|---|---|---|---|
| B159 | MED | OPEN | screenshot claim rows (MATCH/MISMATCH/NOT_IN_DATA) are kept only as counts; context reads without a side are n |

## DESK - Operator interface (DSA and live desk)
How the operator talks to the system: the DSA chat surface and its prompt, the live-desk helper, session paste, trading cards, user guide, launcher commands.

- Operator's words: "DSA, the desk, what I see when I ask"
- Start reading: `DSA_SESSION_PROMPT.md`, `MTS_USER_GUIDE.md`, `operator_reminders.md`
- Who works on it: DSA (chat) plus Code sessions that edit the prompt files; prompt changes are size-budgeted and eval-gated
- Where it lives: `DSA_SESSION_PROMPT.md`, `USER.md`, `MTS_USER_GUIDE.md`, `operator_reminders.md`, `COMMANDS.md`, `mts.ps1`, `Launch_alert.vbs`, `MyTradingSys/cards/`, `scripts/operator/`, `scripts/start-session.ps1`, `scripts/load.ps1`
- Progress is tracked in: registry rows; DSA_SESSION_PROMPT.md.pending_patch_* files
- Focus (hand-written, as of 2026-10-09): DSA slim boot + eval shipped 2026-10-09 (commit 02e7598). B132 (DSA dispatches everything to Claude Code) is open. A screenshot rule for DSA waits as DSA_SESSION_PROMPT.md.pending_patch_2026-10-09_screenshots.md.

| Open item | Sev | Status | Title |
|---|---|---|---|
| B132 | HIGH | OPEN | DSA is dispatching all work to Claude Code instead of doing quick wins and unblock work itself; the operator p |
| B180 | MED | OPEN | operator: DSA picks its tasks by default from the machine it runs on, and something assigns DSA tasks on a sch |

## OPS - AI workforce and process
How the work gets done: surfaces and session naming, scheduler and pick_task, sync.py and parallel worktrees, workers (NUC retired, AIBridge), cloud credits, test gate, CI, lessons learned, supervisor log, item registry.

- Operator's words: "sessions, workers, budget, who does what"
- Start reading: `MyTradingSys/system/PARALLEL.md`, `MyTradingSys/system/SURFACE_POLICY.md`, `MyTradingSys/system/LESSONS_LEARNED.md`
- Who works on it: Opus supervisor decides; Code sessions execute
- Where it lives: `scripts/dev/`, `scripts/sched/`, `scripts/worker/`, `scripts/tools/`, `MyTradingSys/system/`, `MyTradingSys/queue/`, `MyTradingSys/methodology/`, `MyTradingSys/items/`, `MyTradingSys/research/`, `MyTradingSys/tests/`, `tests/`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `VERSION`, `WORKSTATION_MODES.md`, `.github/`, `.claude/`, `.gitignore`, `MyTradingSys/runtime/sched/`, `MyTradingSys/runtime/BUILD_PIPELINE.md`, `MyTradingSys/runtime/BUILD_REPORT.md`, `MyTradingSys/runtime/NEXT_SESSION_HANDOFF.md`, `MyTradingSys/runtime/SESSION_MANIFEST.json`, `MyTradingSys/runtime/SESSION_RESUME.md`, `MyTradingSys/runtime/session_log.json`, `MyTradingSys/runtime/RESEARCH_TASK_PREMARKET.md`, `MyTradingSys/runtime/live_session_journal.md`, `MyTradingSys/runtime/v4.2.0_optimization_spec.md`, `scripts/Build-Check.ps1`
- Progress is tracked in: registry rows; LESSONS_LEARNED.md; SUPERVISOR_LOG.md
- Focus (hand-written, as of 2026-10-09): NUC/Qwen lane retired 2026-10-01; AIBridge is the run-command surface; every session works in its own worktree and ships with sync.py. Open: B150 test gate is a hand-kept allow-list, B090 cloud credit plan, B095 per-session cost not on disk. Freeze on new audit documents until B146-B148 report.

| Open item | Sev | Status | Title |
|---|---|---|---|
| B090 | HIGH | OPEN | Cloud credit approval plan: two-bucket split of the ~$100 awgp spend, C1 audit-reconcile landed 2026-10-04 on  |
| B172 | HIGH | OPEN | operator: the Sonnet ritual (relay/dispatcher sessions) uses a lot of tokens; investigate latest guidance and  |
| B173 | HIGH | OPEN | operator: a terminal window flashes on screen (most likely Python, a scheduled job) and steals focus while typ |
| B178 | HIGH | OPEN | operator: CI/CD end-to-end speed - deploy gate runs the full layer suite as one cold call; backup_snapshot com |
| B095 | MED | OPEN | Per-session cost is visible only inside the Claude CLI Status panel and is never written to disk; no per-sessi |
| B128 | MED | OPEN | Audit PARTIAL group (f): 18 findings where the code is partial or unwired and has no test; references T037 |
| B168 | MED | IN-FIX | AI Bridge: auto-run stops between turns and is slow; second bridge (NUC) undocumented |
| B176 | MED | OPEN | AIBridge (F:\AIBridge, outside MTS repo): auto-run refuses read-only python/node script blocks; agent.ps1 acce |
| B181 | MED | OPEN | operator: Control Room Inbox shows no progress per item; an item without a registry ref shows nothing |
| B182 | MED | OPEN | operator: design DSA AIBridge tasks so several sessions run in parallel and finish quickly, with NB/NUC scope  |
| B183 | MED | OPEN | operator: sessions still run the start ritual after the AI-health changes; audit whether that is expected/opti |
| B184 | MED | OPEN | AIBridge: multi-block replies are miscounted and half-run (first block runs, rest dropped, check runs after ex |
| T046 | MED | OPEN | Stage 3 pending decisions bundle; five coordinator decisions gate Stage 4 |
| T057 | MED | OPEN | Simplify architecture, optimise, declutter |
| B126 | LOW | OPEN | Cloud to SUP inbox consumption cannot be verified; SUPERVISOR_LOG.md:203 is still the last inbox line |
| B170 | LOW | OPEN | GitHub emails every failed CI - fast-track run; green/fast-track is stuck at 24197c4 while fast-track is 6e66d |

## INFRA - Machines, runtime plumbing, housekeeping
The computers and the plumbing under everything: desktop / NUC / laptop, supervisor and launchers, disk health, the Dumps share, retention, backups, archive.

- Operator's words: "the machine, the stack is down"
- Start reading: `MyTradingSys/system/DEVICES.md`, `MyTradingSys/system/RETENTION_POLICY.md`
- Who works on it: Operator and supervisor; hardware work is the operator's
- Where it lives: `scripts/core/`, `scripts/monitor/`, `runtime_data/`, `Dumps/`, `backup_session/`, `_archive/`, `MyTradingSys/archive/`, `MyTradingSys/runtime/locks/`, `MyTradingSys/system/DEVICES.md`, `MyTradingSys/system/RETENTION_POLICY.md`, `scripts/dev/retention.py`, `scripts/dev/declutter_backups.py`, `scripts/Dump_All.ps1`
- Progress is tracked in: registry rows; the supervisor's loop health in STATUS.md
- Focus (hand-written, as of 2026-10-09): B140 desktop WHEA hardware errors every 1-3 days since 2026-07-19 (HIGH, SMART unread, live java runs from D:). B138 Dumps diverged between C: and F:. B152 retention.py deletes files other tools read.

| Open item | Sev | Status | Title |
|---|---|---|---|
| B138 | HIGH | OPEN | Dumps move to F: left C:\...\Dumps and F:\MTS\Dumps as two diverging copies; the \\JIS-NB\MTS-Queue share stil |
| B140 | HIGH | BLOCKED | Desktop WHEA Id 1 "fatal hardware error" every 1-3 days since 2026-07-19 (43 events); every record names STORP |
| B175 | HIGH | OPEN | operator: Defender MsMpEng.exe holds ~0.94 CPU core on JIS-NB after ESET removal and exclusions |
| B098 | MED | OPEN | Host CPU 79 percent from seven Python processes each spinning ~9 percent with zero disk and zero network; CLOS |
| B137 | MED | OPEN | Device roles are undecided after the Qwen lane ended: open questions block the rethink of what runs on desktop |
| B174 | MED | OPEN | Snapshot open_interest.change_1h_pct is a two-decimal gauge; the full-precision OI series exists on disk but i |
| B069 | LOW | OPEN | STATE_UPDATE_WARN exit=1 under wrapper; update_market_state.py exits 0 when run directly |

## Checks
- UNGROUPED registry rows: 0
- Tracked files no group claims: 21 -> scripts/aibridge (19), .gitattributes (1), DSA_SESSION_PROMPT.md.pending_patch_2026-10-09_screenshots.md (1)
- Fix either by adding an "assign" entry or a keyword / path in groups.json.
