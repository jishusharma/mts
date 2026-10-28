# LIVE SESSION JOURNAL
# Append-only. Everything the session produces that no other file holds.
# Types: QUOTE (verbatim user), REQ (requirement stated), OBS (observation),
#        DECISION (call made), LANDED (artifact created), READ (market read).
# Written the moment it happens. Never deferred.
# Supersedes live_session_log.md (2026-09-17). That file held only READ.


## RETROFIT - 2026-09-17 session MTS-2026-09-17-1241Z
## Written 14:20Z. Earlier material captured before this file existed.

### READ entries copied from retired live_session_log.md

## 2026-09-17T12:41:16Z | 76872.50
STATE:   A | bearish 3 / bullish 0
SETUP:   ct_short at weekly_vah 76890.04 | net_rr 1.89 | proof 5 | WAIT_RR
SLOPES:  cvd_session rising | cvd_1h rising | oi_1h flat | net_delta_5m -136
READ:    Short at weekly VAH. Gate 2.0 refusing by 0.11. Book imbalance unusable (4.29 then 1.11 in one minute).

---

## 2026-09-17T12:52:16Z | 76842.50
STATE:   A | bearish 3 / bullish 0
SETUP:   ct_short at weekly_vah 76890.04 | net_rr 1.80 | proof 4 | WAIT_RR
SLOPES:  cvd_session rising | cvd_1h rising but decelerating (1426 to 826 over twelve minutes) | oi_1h flat | net_delta_5m -193
READ:    Flow flipped bearish at 12:40. Five-minute net delta negative every bar since. Gate still refusing.

---

## 2026-09-17T12:11-13:24Z | pre-open ramp-fade
PRICE:   76598 -> 77072 -> 76562
SHAPE:   ramp into level stack, fade back through
LEVELS:  76722 fvg_top | 76748 vwap_band_+1 | 76788 daily_vah | 76890 weekly_vah | 77072 high
READ:    Engine short-biased the whole move, did not fire. No session frame until 13:30 anchor. No pre-open playbook rule in any condition file.

---

### QUOTES

[QUOTE] 13:52Z "we need compiled comparisions/or protocols to remove AI mistakes during live sesion"
[QUOTE] 13:59Z "these things we need to understand as we work and improve. You will use session context to uidentify such gaps and write it as and when needed"
[QUOTE] 13:20Z "at the moment - what setps are building - and what is the direction u are looking at?"
[QUOTE] 14:05Z "hey - i need to paste it on your screen - so i asked for a running terminal from where keep pasting every 3- to 60 secs data"
[QUOTE] 14:18Z "what MTS says abt liqudation magnets? how MTS is wired to that?"
[QUOTE] 13:58Z "look at this - the price is trying to revit the ceiling where we did not short - what is MTS thesis abt such moves?"
[QUOTE] 14:02Z "also - when we get the alet in the first go - it is different than second and third - based on context fuel can increase or decrease - are these things taken care by MTS Tom rules?"
[QUOTE] 14:03Z "log a task for this so that we check it later inside the session log itself. we will implement changes as per observations and proof from there"
[QUOTE] 13:44Z "do not add delays like 35 going forward"
[QUOTE] 13:45Z "i need u to be ready so fetch what u can - that makes sense - the dynamics are"
[QUOTE] 13:53Z "now we will continue the same session from a new chat window - how can we prepare?"
[QUOTE] 13:24Z "hey market opened -"
[QUOTE] 13:19Z "price is falling back to sessionlows - check what is haoening - we missed the short?"
[QUOTE] 13:31Z "just beofr US open - we saw that move up. was it expected? do u have session refernce?"
[QUOTE] 13:14Z "track all data and signals like divergence every 30 sec -possible?"
[QUOTE] 13:16Z "what are are setups?"
[QUOTE] 13:30Z "the tape tail read: no, not needed. it will produce output on its own. - ake sure never happens - fix it for good"
[QUOTE] 13:47Z "no writes during US session"

### REQUIREMENTS

[REQ] 13:52Z live_session_protocol rule 1: quote the number. Every price, level, state, or flow claim must be a direct quote from a paste.
[REQ] 13:52Z live_session_protocol rule 2: delta check before any of: new, broke, failed, rejected, confirmed, held, flipped.
[REQ] 13:52Z live_session_protocol rule 3: timestamp every temporal claim. If paste older than 60s, say so.
[REQ] 13:52Z live_session_protocol rule 4: label inference. Chart reads and mental models distinct from system values.
[REQ] 13:44Z live_session_protocol rule 5: no Start-Sleep in issued commands. Any delay lives inside a script file.
[REQ] 13:52Z live_session_protocol rule 8: doc notes are not code. Write when the gap is seen, do not defer.
[REQ] 13:52Z live_session_protocol rule 9: corrections are one line. State corrected fact, move on.
[REQ] 13:59Z operator standing rule: identify gap, write it, do not defer.
[REQ] 14:05Z one combined source for paste. mts-watch.log tail 40 gives full state.
[REQ] 13:30Z no visible window needed for the monitor. File + one read command.

### OBSERVATIONS

[OBS] 13:20Z Book imbalance unstable. Twelve readings 0.6 to 4.29 in twelve minutes. B024 evidence, live today.
[OBS] 13:40Z OI flat 0.05% through the entire 75975 drop and bounce. Neither short covering nor new positioning by the OI read.
[OBS] 13:31Z day_type balance/provisional at first anchor read. Needs two more snapshots. B042.
[OBS] 13:35Z I23 live, long side. State S with bear 3 while long setups at daily_val are trigger-ready and clear the gate. No reconciliation rule.
[OBS] 13:45Z I23 live, short side, earlier in session. State A while short setups at weekly_vah trigger-ready. Same class.
[OBS] 14:18Z Liquidation layer: adapter exists and is complete, four breaks in the pipeline, field emits 0.0/false. Note on disk.
[OBS] 13:47Z Attempt-number context at a zone missing. Three touches of 76120-76174 in twenty minutes, engine blind to first vs third.
[OBS] 13:53Z Pre-open playbook gap. London-NY handoff 12:11-12:31, 474-point ramp then 510-point fade. No condition-file rule names it.
[OBS] 13:35Z flow vs state mismatch. cvd_slope rising but nd1m bearish, cvd_trade_flow_aligned True. Field semantics need review.
[OBS] 13:07Z snapshot structure.lookbacks are {24,16,12} on {1h,15m,5m}. One-hour timeframe looks back 24 hours. Not multi-day.
[OBS] 13:07Z buildStructure pivot detection undone by Math.min/max lines. swing_high always lookback high, never pivot.
[OBS] 13:35Z tape-watch duplicate line when snapshot does not change between 30s ticks. Cosmetic.

### DECISIONS

[DECISION] 13:20Z Sidecar watchers, not start-trading-day.ps1 edits. Loop stays live, no critical-file write during session.
[DECISION] 13:52Z Codify AI-side checks as live_session_protocol.md. Ten rules, mistake ledger for the day.
[DECISION] 13:53Z Continuation via SESSION_RESUME.md. Manifest boot_supplemental carries it into the new chat.
[DECISION] 13:57Z Manifest append via + failed, replaced array. Switched to text splice with anchor count check.
[DECISION] 14:20Z live_session_log.md retired. Journal supersedes. Narrow log duplicated apparatus_log and mts-watch.log.

### LANDED

[LANDED] 13:26Z live_session_log.md created, later retired.
[LANDED] 13:35Z tape-watch.ps1 created. Divergence classifier, 30s tick, popup on non-neutral.
[LANDED] 13:48Z mts-watch.ps1 created. Full-state console feed + runtime_data\mts-watch.log.
[LANDED] 13:48Z live_session_protocol.md created. 10 AI-side checks + mistake ledger.
[LANDED] 13:53Z SESSION_RESUME.md created. Continuation brief.
[LANDED] 13:52Z Task logged in session_log.json: attempt-number context at a zone.
[LANDED] 13:29Z Pre-open playbook gap appended to apparatus_fixes.md OPEN.
[LANDED] 13:57Z SESSION_MANIFEST.json updated: SESSION_RESUME.md, live_session_protocol.md, live_session_log.md added.
[LANDED] 14:20Z This journal created. live_session_log.md moved to backup_session/.

### TASKS AND BUGS

[REF] Open tasks and bugs live in session_log.json and BUGS.md. Not duplicated here.
[REF] Code-readiness items queued for after close: B043 supervisor double-start,
      supervisor singleton lock, mode.ps1 guard, atomic lock, buildStructure pivot,
      tape-watch duplicate line, liquidation layer decision, multi-day ladder /
      CVD anchor / OI trajectory.

[REF] 2026-09-17T14:37:07Z Session MTS-2026-09-17-1357Z: liquidation layer re-evaluation task logged from NOTE - LIQUIDATION MAGNETS IN MTS (VALIDATED).txt. Decision pending: wire adapter (three-line change), mark manual (Tom has no liquidation language), or retire BinanceLiquidationAccumulator.java. No code without three-snapshot proof. B031 candidate: 75975 flush 13:39-13:40Z.

[DECISION] 2026-09-17T14:55:05Z Liquidation layer: Option B, leave permanently manual. No wire, no retire. Rationale: Tom extracts zero liquidation language (TOM_VERBATIM_INDEX TOM-001..010), crypto_adaptations L48 UNVALIDATED, Section 10 blocks engine rule without three-snapshot proof. W3 verified four breaks on disk. W4 recommended B. Adapter file stays on disk as dormant. Reversible by later decision.
[LANDED] 2026-09-17T14:56:18Z Workers closed: W1_verify_context, W2_live_tracking, W3_liquidation_verify, W4_liquidation_decision. Each folder holds its prompt/material and a worker_reply.md. No open worker sessions.
[LANDED] 2026-09-17T15:01:01Z Session MTS-2026-09-17-1357Z close. Liquidation decision B logged. Workers W3/W4 closed. PROCESS SPEED RULES added to live_session_protocol.md (7 rules). Loop left running for data collection.
# END

## CLOSE - 2026-09-17T15:12Z

[DECISION] Session MTS-2026-09-17-1503Z closed.
[LANDED] SESSION_PASTE.txt trimmed 116KB to 71KB via five cuts.
[LANDED] start-session.ps1: new head_to_end read mode, audit tracker sliced from ## AUDIT SUMMARY, SESSION_RESUME dropped from manifest, journal tail 150->60, duplicate CANONICAL FIELDS block removed.
[LANDED] apparatus_fixes.md: added # END before the historical SESSION NOTES block so head_to_end cuts there.
[LANDED] Build-Check.ps1 line 15: Get-Date replaced with [DateTime]::UtcNow. Label had claimed UTC while writing local. Off by 5h30m.
[LANDED] 03_FILE_INDEX.md: SIZE 10.6KB -> 12.3KB, LAST UPDATED 2026-09-13 -> 2026-09-17.
[OBS] Build-Check.ps1 Active sessions section is dead code: no writer to runtime\locks, only Build-Check reads it. Real lock at runtime_data\apparatus.lock.
[OBS] Dormant UTC parse bug at Build-Check.ps1:89. Same class as the fixed line 15.
[OBS] apparatus_fixes.md now has two # END markers. B011 class.
[NOTE] Loop left running at close. No stop-day, no mode.ps1.
## MTS-2026-09-17-1514Z QUICK WINS - 2026-09-17T16:09:23Z

[LANDED] start-trading-day.ps1 no-change log now prints verdict (B026).
[LANDED] Build-Check.ps1 line 89 UTC parse fix.
[LANDED] start-session.ps1 tail read default lines=60 (manifest guard).
[LANDED] apparatus_fixes.md truncated to first # END. Historical tail at backup_session/apparatus_fixes_historical_20260917.md. B011 fixed.
[CLOSED] B027 false alarm. OI updates hourly. Live snapshot matches direct endpoint.
[IN-FIX] B034 CVD ring clear on UTC day rollover. StateCodeEmitter.java. Compile OK. Pending loop restart.
[REF] B032 deferred. session_end_logs.md writer is StateCodeEmitter.java:442-443, path MyTradingSys/system. Not a defect.
## MTS-2026-09-17-1514Z POST-RESTART - 2026-09-17T16:20:38Z

[LANDED] B034 live. StateCodeEmitter.class recompiled 16:09Z, java 596 started 16:19Z, class loaded.
[LANDED] B043 partial: PROCESS SPEED RULE 8 added -- never call mode.ps1 or start-trading-day.ps1 with & from a script that needs to continue. Verified by failure: restart-with-b034.ps1 hung at mode.ps1 call.
[OBS] B043 root cause: supervisor matcher keys on 'start-trading-day' in command line. When mode.ps1 launches the wrapper, cmd line says 'mode.ps1' not 'start-trading-day'. Supervisor misses it. Second supervisor started twice during recovery.
[OBS] Supervisor 18264, wrapper 17792, java 596. Single of each. Lock 17792. Clean.
## MTS-2026-09-17-1514Z CLOSE - 2026-09-17T16:22:23Z

[LANDED] B027 CLOSED. B034, B026, B011 fixed. Build-Check UTC fixed. start-session tail default.
[LANDED] B043 fixed. Supervisor matcher extended to mode.ps1.
[LANDED] PROCESS SPEED RULES 8 (no ampersand on mode.ps1) and 9 (direct-kill supervisors) added.
[LANDED] Commits: 73b7d9f, 78da5bc, f50abc1.
[OBS] Recovery lesson: restart utility that calls mode.ps1 with & hangs forever. Ctrl+C killed the wrapper. Supervisor auto-recovered but spawned duplicate during grace.
[NOTE] Loop left running. Supervisor 8200, wrapper 17792, java 596. B034 loaded.
## MTS-2026-09-17-1624Z DASHBOARD - 2026-09-17T16:45Z

[HEADLINE] No trade passes the gate. Engine WAIT_RR six cycles straight.
[MARKET] price 76770.0. anchor 13:30Z. open 76440.9. high 77096.7. low 75975.0. range_pos 70.87. gap up 266.3. sweep above. day_type balance provisional. in_value. sweep_flag true. intraday_4h VA 76 points wide 76645.98-76722.11.
[STRUCTURE] weekly TWOPEAK 75719.66/76895.04/75444.57. daily TWOPEAK 76361.58/76898.77/76276.23. post_funding 76893.75/77069.47/76421.83. intraday_4h 76672.46/76722.11/76645.98. prior_day 75750.0/76080.0/75430.0 close 76174.6. Three-week POC down 79892.45 to 77155.43 to 75719.66.
[FLOW] vwap 76527.13 rising. cvd -107.722 falling. net_delta 1m +5.044 5m -32.43 15m -7.837 1h +152.362. last_3_delta neg neg pos. cvd_recent slope_1h rising slope_4h falling delta_1h 164.153 delta_4h -134.447. book bid_ask_ratio 0.27. oi falling -0.24pc 1h. funding 9.485e-05 not extreme. basis -0.04 discount.
[POSITIONING] retail lsr 1.4558 ch1h +0.0263 ch4h -0.0121. whale lsr 2.3332 ch1h +0.0152 ch4h +0.0474.
[SPEED] trades_per_sec 11.55 baseline 14.63 historical 18.21. trades_ratio 0.79 volume_ratio 1.06. speed_state maintaining. speed_vs_historical 0.63.
[STATE] state_code A. bearish 0 bullish 2 available 3. seconds_in_state 60. last_transition 16:23:15Z. signals net_delta_1m bullish price_vs_vwap bullish last_3_delta neutral cvd_slope null volume_ratio null.
[CANDIDATES] rank1 ct_short 4h_vah 76722.11 net 1.70 B proof4 gate FAIL. rank2 scalp_short vwap+1 76773.1 net 1.72 B proof4 gate FAIL. rank3 ct_short weekly_vah 76895.04 net 1.57 B proof2 gate FAIL. rank11 fvg_long 76689.5 net 2.01 C proof0 gate PASS.
[DIVERGENCES] D1 price above rising VWAP bullish vs CVD falling bearish vs book 0.27 ask-heavy bearish. D2 delta split 1m +5.044 5m -32.43 15m -7.837 1h +152.362. D3 cvd_recent slope_1h rising vs slope_4h falling. D4 state_code 2 of 5 signals null cvd_slope volume_ratio. D5 top 3 candidates short only gate-passing setup is rank11 long. D6 day_type balance provisional vs range_pos 70.87 and sweep_flag true. D7 pd flag flipped contradiction 16:17 to aligned 16:18. D8 cvd_trade_flow_aligned true while conditions.cvd_slope falling. D9 price up 76725.90 to 76770.00 while OI falling 0.24pc 1h, short-covering pattern, inference from two points. D10 book 0.27 ask-heavy vs rising price and bullish state.
[LEVELS] 77149.8 1h swing high ct_short stop. 76895-76898 weekly+daily VAH. 76773.1 vwap+1s rank2 zone price at it now. 76722.11 4h VAH rank1 zone. 76689.5 fvg bottom rank11 zone. 76276.23 daily VAL. 75975.0 session low flush 13:39-13:40Z. 75750.0 prior day POC ct_short target.
[ACTIONS] A1 nothing on trade side. A2 watch net_rr ct_short cross 2.0. A3 watch proof count fvg_long rise above zero. A4 loop running supervisor 8200 wrapper 17792 java 596 lock 17792, do not stop, do not bare-kill java, do not run mode.ps1 with lock held. A5 pre-open playbook gap unresolved 474pt ramp 12:11-12:31Z then 510pt fade 12:31-13:24Z, engine stayed short did not fire, decision pending.
[LOOP] snapshot age 0.1 min. state_code age 0.1 min.


## MTS-2026-09-17-1624Z WATCH SPLICE LIVE - 2026-09-17T17:37Z

[LANDED] mts-watch.ps1 extended by 36 lines. Blocks added: HSTOP (hard_stops_compiled 4 booleans), PROOFDIR (proof_direction_status + details), CAND (rank-1 setup_candidate full), DELTA (px/cvd/book vs prior snapshot). Verified live. 101 -> 137 lines. CRLF preserved, no BOM, PARSE OK.
[FIX] First splice corrupted file (throw did not abort in interactive session, PROCESS SPEED RULE 2 lesson). Recovered from .corrupt backup using last 101 lines. Second splice: $rt variable was out of scope, replaced with $R (file-local, defined L12). Verified lines 83, 84, 106.
[OBS] Live feed at 17:36Z: HSTOP atZone=True anyZoneRRfail=True topCandRRfail=True chase=False. PROOFDIR=aligned. CAND r1 ct_short@weekly_vah 76890.04 dist=0.03% tier=trigger_ready nrr=1.53 gate=False p=6 conf=B. DELTA px -63.30 cvd -51.937 book +0.22.
[FINDING] Rank-1 at-zone with 6 proofs but gate fails on nrr < 2.0. No trade. Book flipped 1.26 -> 0.36 in one cycle (B024 live). CVD -333.688 -> -368.705 while price fell -63.30. 4 cycles WAIT_RR with nrr frozen 1.53, zone not closing.
[ANOMALY] PROC line shows wrap empty, !!! WRAP COUNT=0 !!!. Lock still 17792, supervisor 8200, java 596. Snapshot age 30-42s. Loop running. Wrapper matcher not finding wrapper. Not urgent, flag only.


## MTS-2026-09-17-1624Z FEED NAMING - 2026-09-17T17:40Z

[DECISION] Live feed naming scheme locked. Commands: mts-live, mts-live-fast, mts-live-stop, mts-live-log, mts-tape. Blocks: MTS-PROC, MTS-SNAP, MTS-VWAP, MTS-SESS, MTS-COND, MTS-SET, MTS-STATE, MTS-SIG, MTS-FLOW, MTS-HSTOP, MTS-PROOF, MTS-CAND, MTS-DELTA, MTS-CYCLES, MTS-TAPE, MTS-SLOW.
[LANDED] MTS_DICTIONARY.md LIVE FEED NAMES section. load.ps1 aliases. mts-watch.ps1 v1.1.0 header + prefix rename. NEXT_SESSION_HANDOFF.md rewritten FIRST ACTION to start with mts-live. 03_FILE_INDEX.md row updated to canonical. live_session_protocol.md PROCESS SPEED RULE 10 added.
[RULE] Every live session runs mts-live. Every live session adds at least one block or field to the feed.


## MTS-2026-09-17-1624Z CLOSE - 2026-09-17T17:45Z

[LANDED] mts-watch.ps1 v1.1.0: 4 compiled blocks (MTS-HSTOP, MTS-PROOF, MTS-CAND, MTS-DELTA). All 15 prefixes MTS-.
[LANDED] MTS_DICTIONARY.md LIVE FEED NAMES section. load.ps1 aliases: mts-live, mts-live-fast, mts-live-stop, mts-live-log, mts-tape.
[LANDED] NEXT_SESSION_HANDOFF.md FIRST ACTION = mts-live. 03_FILE_INDEX.md row 249 canonical. live_session_protocol.md rule 10.
[LANDED] DSA_SESSION_PROMPT.md section 9 live-mode rule + section 11 rewrite to 5 lines.
[LANDED] BUGS.md B044 B045 appended. WRAP matcher fix (start-trading-day|mode.ps1).
[OBS] WRAP COUNT=0 anomaly closed: matcher extended to mode.ps1 (B043 class).
[NOTE] Loop left running. Supervisor 8200, java 596, lock 17792. No stop-day, no mode.ps1.

## MTS-2026-09-17-1757Z JAVA COUNT=2 RESOLVED - 2026-09-17T18:08Z

[OBS] JAVA COUNT=2 resolved. Second java is the Maven snapshot child (exec.args=snapshot BTCUSDT). Not a duplicate state machine. Not a defect.
[EVIDENCE] Poll caught PID 6472 at 2026-09-17T18:08:12Z. Creation 18:08:10Z. Same classworlds launcher as PID 596. exec.args snapshot BTCUSDT vs statemachine BTCUSDT. Self-clears on snapshot write.

## MTS-2026-09-17-1757Z DASHBOARD BUILD AND OPEN QUESTIONS - 2026-09-17T19:30Z

[LANDED] mts-dashboard.ps1 v1.2.0. One-shot command. Reads latest snapshot, state_code.json, apparatus_log.txt, and the compiled math object (via build_mo_cli.py). Prints SUMMARY / TRADES table / MARKET-FLOW-LEVELS-WATCH grid / PREPARE / legend. Fixed 132-char frame. ASCII tables. Color on data only: labels gray, values white, deltas green or red by sign, engine WAIT red. No new logic, no new I/O, no engine touch.

[LANDED] mts-dashboard -Watch. Same script, loops with Clear-Host, 30s interval, Ctrl-C to exit. One-shot default unchanged.

[LANDED] load.ps1 alias mts-dashboard. Loaded message now reads live quick deltas trend snapshot overview health alerts context regime dashboard.

[LANDED] mts-watch.ps1 plain-word render. MTS-HSTOP now reads: at a trigger-ready zone / any zone gross reward-to-risk below 1.5 / top candidate net reward-to-risk below 2.0 / price chasing. MTS-PROOF: proof direction. MTS-CAND: rank-1 setup at zone, distance, tier, substate, net reward-to-risk, gate pass, proofs, confidence, stop, target, gross reward-to-risk. MTS-DELTA: price / cvd / book. Values unchanged.

[VERIFIED] Field audit at 18:46Z. 29 of 29 snapshot fields match dashboard. All setup_candidates match. State fields match. Engine health matches. Zero fabrication.

[VERIFIED] Engine-gate alignment. Dashboard GATE column reads the engine verdict from apparatus_log, not per-candidate net_rr_sanity. Rank 1 shows WAIT when engine waits. Lower ranks show dash. Summary line reads from the log verdict, not a counter.

[OBS] B024 book instability live and loud. Book flipped 7 distinct values in 7 minutes: 0.12, 1.34, 0.53, 2.14, 2.17, 0.26, 1.14. Do not weight book-heavy proof flags.

[OBS] State vote layer and setup layer diverge. In the 12-frame window 19:09 to 19:16, state was S for ten frames then A for two. One transition, at 19:14:15. Rank-1 setup (scalp_long at VWAP) stayed stable the whole window.

[OBS] Java count anomaly fully diagnosed. Second java is the Maven snapshot child (exec.args=snapshot BTCUSDT). Self-clearing. Not a duplicate state machine. Not a defect. Sightings this session: PID 17644, 956, 6472, 6280, 7068, 17584.

[PROCESS] Interactive PowerShell throw does not abort the current paste. PS 5.1 continues to the next line after a thrown exception in a multi-line scripted block. Live confirmation of PROCESS SPEED RULE 2 in live_session_protocol.md. Correct pattern: compute all anchors first, set a flag, wrap the write in a single if. Atomic check-then-write.

[OPEN] CVD anchor mismatch. DSA CVD anchors at 00:00 UTC. CoinGlass CVD anchors at the leftmost visible bar. Values are not comparable. Question: change DSA to a rolling window, keep session-anchored and add a rolling-window field, or accept and document. No engine consumer needs the change today. This is a comparison problem, not a decision problem.

[OPEN] OI panel magnitude vs direction. Dashboard shows direction falling with change_1h_pct. CoinGlass OI panel shows absolute K value. Direction agrees. Magnitude comparison is not built. Question: add a rolling-window OI delta field to the snapshot, or accept direction-only and document the CoinGlass panel as chart-read only.

[OPEN] Net Delta positioning vs flow. Dashboard trade_flow.net_delta_* is FLOW per MTS_DICTIONARY. CoinGlass Net Delta panel is POSITIONING (longs minus shorts). Never cross-validate by sign or magnitude. Question: expose a positioning field on the dashboard, or keep flow-only and document CoinGlass positioning as chart-read only.

[OPEN] What we trade on. The engine trades on rank-1 net_rr_sanity plus the setup_candidate structure. It does not read CoinGlass panels. CoinGlass is a visual cross-check, not an input. Question: confirm this stays true, or name a CoinGlass field that should be wired as a cross-check input. Owner: operator.

[OPEN] Pre-open playbook gap. Carried from prior session. London-NY handoff on 09-17 produced a 474-point ramp then a 510-point fade. Engine stayed short-biased and did not fire. No condition-file rule names the pattern. Decision pending: build a rule or mark permanently manual.

## MTS-2026-09-17-1757Z CLOSE ADDENDUM - 2026-09-17T19:40Z

CORRECTIONS TO PRIOR HANDOFF

- Prior handoff NOT YET DONE section is stale. All four items completed at 19:38Z: gitsnap commit b92051d tag last-snapshot moved dirty=0; 03_FILE_INDEX.md row for scripts\live\mts-dashboard.ps1 added; MTS_DICTIONARY.md entries for mts-dashboard and -Watch added; mts-watch.ps1 version bumped v1.1.0 to v1.1.1.
- Prior handoff does not record mts-dashboard version evolution: v1.0.0 plain dashboard, v1.1.0 tables plus colors, v1.2.0 fixed frame plus engine-gate alignment plus full state header. Only v1.2.0 exists on disk.
- Prior handoff does not mention mts-live-stop flag is not cleared by mts-live on launch. After a stop, remove runtime_data\mts_watch_stop.flag before running mts-live again. Small usability gap. One-line fix candidate in load.ps1.

ADDITIONS

1. Backup files created this session under backup_session\: live_session_journal_before_java2_*.md, live_session_journal_before_dash_*.md, live_session_journal_before_addendum_*.md, load_before_dashboard_*.ps1, mts-watch_before_plainwords_*.ps1, mts-watch_before_ver_*.ps1, mts-dashboard_before_tables_*.ps1, mts-dashboard_before_colors_*.ps1, mts-dashboard_before_layout_*.ps1, mts-dashboard_before_fix5_*.ps1, mts-dashboard_before_cleanup_*.ps1, mts-dashboard_before_watch_*.ps1, mts-dashboard_before_enginegate_*.ps1, 03_FILE_INDEX_before_dash_*.md, MTS_DICTIONARY_before_dash_*.md.

2. Historical pre-open playbook gap references in journal: line 81 OBS 13:53Z, line 103 LANDED 13:29Z, line 169 ACTIONS A5, line 234 OPEN new. Four total references. Open item 5 context.

3. Git CRLF warnings on commit b92051d. Files flagged: state_code_regime.json, supervisor_log.txt, mts-watch.ps1, load.ps1, mts-dashboard.ps1. Git will normalize to LF on next touch. mts-watch.ps1 and load.ps1 were written LF this session, so the working-copy CRLF is unexpected. Verify next session.

4. Book flips values in the 7-minute window 19:09 to 19:16: 0.12, 1.34, 0.53, 2.14, 2.17, 0.26, 1.14. Seven distinct. B024 evidence.

5. State vote layer observation: in the 12-frame -Watch window, state was S for ten frames then A for two. One transition at 19:14:15. Rank-1 setup unchanged the whole window. Vote layer jittery, setup layer stable.

6. Session timings: session start name MTS-2026-09-17-1757Z. Session close time 19:40Z. Duration about 1h45m wall clock.

7. Self-corrections made live this session: wrong state cycle claim (S to A to S to A) corrected to S-then-A one transition; wrong line count 16 corrected to 32; wrong OPEN count six corrected to five; unverified line 169 content then verified as ACTIONS A5.

8. Audit format directive for next session: every response carries a per-claim audit with source, check, arithmetic, reason, confidence (confirmed / inferred / unverified), and corrections to prior statements. User requested this running behavior.

## MTS-2026-09-17-1757Z PROOF DETECTOR AUDIT AND OPEN DESIGN QUESTION - 2026-09-17T19:52Z

[VERIFIED] delta source. SetupCandidatesBuilder.java lines 615-620. deltas[i] = 2 * takerBuy - volumes[i], reading kline index 9 (taker buy base asset volume). Expands to takerBuy minus takerSell. This is the kline taker-buy proxy, consistent with B044. Not aggTrade.

[VERIFIED] rejection_wick. Lines 623-666. Scan last 20 candles. For a short setup, wick high must be >= zone and close < zone. For a long setup, wick low must be <= zone and close > zone. Quality by wickPct = 1 - body/range and bodyPct = body/range: STRONG wickPct>0.8 bodyPct<0.2; MODERATE wickPct>0.5 bodyPct<0.5; else WEAK. Actual level is the wick tip price. The ONLY proof with an explicit setup-direction check inside the detector.

[VERIFIED] absorption. Lines 670-692. Scan last 10 candles within 0.1% of zone. All three must hold: volume > 2.0x avgVol20; range < 0.3x ATR14; delta sign opposite to candle color. Strength by maxVolRatio: strong if > 5.0, else moderate. No direction field.

[VERIFIED] finished_auction. Lines 695-706. Scan last 20 candles. Condition: abs(delta[i]) > 3.0x avgAbsDelta20. Reversal: extreme candle direction opposite to close move next candle. No-follow: abs(delta[i+1]) < 0.5x abs(delta[i]). Direction stored as buy or sell (the extreme candle direction). follow_through hardcoded false. No setup-direction check in count.

[VERIFIED] delta_flip. Lines 712-735. Scan last 20 candles. Condition: sign change between deltas[i-1] and deltas[i]. Proximity gate 0.1% of zone. Nearest-zone attribution: reject if another zone is closer. from_negative stored. actual_level is close at flip candle. No setup-direction check in count.

[VERIFIED] volume_spike. Lines 742-753. Baseline = 240-minute average volume. magnitude = current volume / 240-min average. detected = magnitude > 2.0. at_level = last close within 0.1% of zone. Both must be true to count. No direction field.

[VERIFIED] speed. Lines 755-777. atrRatio = ATR14 current / ATR14 prior window. maxConsec = longest run of last 10 candles with range > 1.5x avgRange20. speedScore = min(10, atrRatio * 3 + maxConsec * 2). picking_up = score > 5. direction = VWAP slope direction, NOT setup direction. Count uses only picking_up.

[VERIFIED] cvd_aligned. Lines 778-792. Internal consistency: cvd.slope and trade_flow.net_delta_1m point the same way. Flat main slope falls back to cvd_recent.slope_1h. Not a setup-direction check. A long setup with falling CVD and negative netDelta would still get cvd_aligned=true.

[VERIFIED] book_imbalance. Line 795 reads order_book_depth.bid_ask_ratio. Count condition (line 537): != 0.0 AND (< 0.67 OR > 1.5). Any extreme counts, either side. Bid-heavy and ask-heavy both count the same for any setup direction.

[FINDING] 7 of 8 proof detectors have no setup-direction check. Only rejection_wick does. The countSignals block at lines 528-539 increments every proof that fires, regardless of direction fit. Consequence: a long setup at a low can count a buy-direction finished_auction as supporting proof, which is directionally a contradiction (buying climax at a low, not selling exhaustion). Same for cvd_aligned falling on a long, book ask-heavy on a long, speed direction down on a long.

[EXAMPLE] Alert at 19:35:16Z. SETUP_FORMING, proof 5, ct_long @ 4h_val 76513.85. Five counted proofs: rejection_wick MODERATE at 76505.3; finished_auction buy extreme +57.75; delta_flip from_negative at zone; speed picking_up vwap rising; book_imbalance 2.76. Directionally fitting a long: 4 of 5. The finished_auction buy is a buying climax, a contradiction counted as support.

[CONSEQUENCE] The proof count overstates directional support. Operators and the engine confidence grading read the count as if all proofs point the same way. They do not. Counts will drop across the board if the count is made direction-aware.

[OPEN QUESTION - PRIMARY] What is the right approach? Three options. Option A: direction-aware counting. For a long, only count finished_auction if direction=sell, only count cvd_aligned if cvd.slope=rising, only count book_imbalance if >1.5, only count speed if direction=up. Mirror for short. Java change in SetupCandidatesBuilder.java lines 528-539. Consequence: proof counts drop, confidence grades drop, history comparison breaks. Option B: keep the raw count but add a separate direction_fit field that shows how many proofs point the setup way. Engine still counts raw, dashboard and alerts show both. Non-breaking. Option C: do nothing. Accept that the count is a signal count, not a conviction score. Update documentation to say so.

[OPEN QUESTION] Related: what does the engine confidence grade (A, B, C, C+) actually mean? If it is derived from proof count, the direction-blind count propagates into confidence. Verify in a future session.

[OPEN QUESTION] Related: does the alert reader (operator or AI) need a separate contradiction line? The current alert card shows the raw proof detail. A compact summary like "4 supportive, 1 contradicting" would make the direction fit visible without engine change.

[CORRECTIONS] Three claims made earlier in the session that this code read corrected. (1) "3 of 8 proofs have no direction check" is wrong. Actual is 7 of 8. (2) rejection_wick was implicitly treated as having no check. It is the only one that does. (3) delta source was "likely kline proxy" inferred. Confirmed as kline index 9 taker-buy proxy.

[BUGS SUGGESTION - NOT FILED] Potential B046: OPEN, HIGH, "7 of 8 proof detectors lack setup-direction check; count overstates directional support". Evidence SetupCandidatesBuilder.java lines 528-539 countSignals vs lines 627-640 rejection_wick. Not filed. Do not file until the approach is decided.

[SESSION CLOSE] MTS-2026-09-17-1757Z. Close time 2026-09-17T19:52Z. Duration about 1h55m. No trade taken. No session_state thesis change. Loop left running: supervisor 8200, wrapper 17792, java 596, lock 17792 held. Build-Check PASS at boot. Commit b92051d at 19:38Z. Journal appends this close: dashboard build block 32 lines, close addendum 26 lines, this proof audit append.

[FIRST ACTION NEXT SESSION] Read this journal tail 60 lines. Run mts-dashboard to confirm render. Review the three OPEN questions on proof counting. Do not file BUGS.md B046 until the approach is decided. Investigate the right approach: A direction-aware count, B separate direction_fit field, C accept raw count and document. Owner: operator.

## MTS-2026-09-17-1757Z FIRE BUG FIXED AND REMAINING OPEN - 2026-09-17T19:53Z

[FIXED] mts-dashboard FIRE bug. Live defect at 19:32:27Z printed GATE=FIRE and "Engine FIRE" for a SETUP_FORMING verdict. Cause: binary not-WAIT test in GATE cell and summary line. Fix: read verdict word verbatim from apparatus_log field 5, split by pipe, strip parenthetical. Verdict word printed as-is. SETUP_CONFIRMED is the only fire word. Four anchors, atomic check, all count 1. Verified 19:52:03Z: banner SETUP_FORMING, GATE SETUP_FORMING, summary "Engine says: SETUP_FORMING. setup forming". No false FIRE.

[LOGGED] Verdict word taxonomy observed this session: WATCH (setup being watched), SETUP_FORMING (structure building), SETUP_CONFIRMED (entry condition met, not seen today), WAIT_RR (at zone, ratio below gate), WAIT_TRIGGER (ratio ok, price not at zone). Not yet in MTS_DICTIONARY.md. Add next session.

[LOGGED] DIRECTION request open. Alert card and dashboard TRADES table do not print LONG or SHORT as a word. Direction is embedded in the setup_type suffix (_long or _short). Snapshot has a direction field per candidate. Fix: add DIRECTION column to dashboard TRADES table, reading $c.direction. One column, two lines. Non-critical.

[REMAINING] DSA_SESSION_PROMPT.md section 11 not updated this session. Critical file. Four-step proof required: hash before, edit, hash after, diff. Defer to next session. Section 11 currently reads state from MTS-2026-09-17-1624Z close.

[REMAINING] session_log.json not written this session. Ledger has no entry for MTS-2026-09-17-1757Z. Journal carries the detail. Ledger write is a one-liner for next session.

[SESSION CLOSE FINAL] MTS-2026-09-17-1757Z. Close time 2026-09-17T19:53Z. No trade taken. No session_state thesis change. Loop running: sup 8200, wrap 17792, java 596, lock 17792. Build-Check PASS at boot. Commit b92051d at 19:38Z. Journal appends this close: dashboard build 32 lines, close addendum 26 lines, proof audit 40 lines, this fix log. FIRE bug: found, fixed, verified live. Next session first action: update DSA_SESSION_PROMPT.md section 11, write session_log.json entry, add verdict taxonomy to MTS_DICTIONARY.md.

## MTS-2026-09-17-1757Z OPEN ITEMS MASTER - 2026-09-17T20:15Z

This entry consolidates every open item from the session not already logged elsewhere in the journal. Every claim carries a file reference and line number where verified. Unverified items are marked [UNVERIFIED]. Reference format: path:line.

=== CATEGORY A - FIXES NEEDED (no investigation required) ===

A1. mts-live-stop flag not auto-cleared. Proof: scripts\load.ps1 line 21 mts-live-stop writes runtime_data\mts_watch_stop.flag. mts-live (line 20) does not remove it. Observed live at 19:09Z: mts-live printed "mts-watch: stop flag, exiting". One-line fix. Non-critical.

A2. DIRECTION column on dashboard TRADES table. Proof: scripts\live\mts-dashboard.ps1 TRADES table render, no $c.direction column. Snapshot field exists: runtime_data\snapshots\BTCUSDT_*.json setup_candidates[n].direction (values "long" or "short" observed in the 18:46Z field audit). One column, two lines. Non-critical.

A3. Verdict word taxonomy into MTS_DICTIONARY.md. Proof: five words observed live in runtime_data\apparatus_log.txt this session: WATCH (20:01-20:05Z cycles 198-203), SETUP_FORMING (19:32Z, 19:35Z), SETUP_CONFIRMED (never observed this session), WAIT_RR (18:41-19:59Z), WAIT_TRIGGER (17:56Z, 20:06Z). None appear in MyTradingSys\research\MTS_DICTIONARY.md. Non-critical.

A4. session_log.json entry for MTS-2026-09-17-1757Z. Proof: MyTradingSys\runtime\session_log.json not written this session. Journal carries detail. One line. Non-critical.

A5. DSA_SESSION_PROMPT.md section 11 update. Proof: DSA_SESSION_PROMPT.md section 11 still reads "Last live read: 2026-09-17T17:45Z, session MTS-2026-09-17-1624Z closing". Critical file per section 6. Four-step proof required. Deferred.

A6. mts-watch.ps1 header version. Proof: scripts\live\mts-watch.ps1 line 2 reads "# Version: v1.1.1" after the 19:38Z bump. Plain-word render happened at 18:57Z under version v1.1.0. The bump to v1.1.1 was for the render. Claim corrected: this item is DONE, not open. [CORRECTION to prior entry].

A7. Rank-1-only gate design. Proof: MyTradingSys\runtime\math_object_builder.py lines 357-370, top_candidate_rr_fail reads setup_candidates[0] only. Observed live at 19:59:15Z: rank 1 nrr 1.86 below gate while rank 3 nrr 2.01 above gate, engine did not fire. Design question. Decision needed: keep rank-1-only or scan all candidates.

=== CATEGORY B - INVESTIGATIONS NEEDED (read code or docs, no change yet) ===

B1. Possible sign error in proof direction check. Proof: src\main\java\datafeed\SetupCandidatesBuilder.java line 703 sets finishedAuctionDirection = deltas[i] < 0 ? "sell" : "buy", the EXTREME candle direction. MyTradingSys\runtime\math_object_builder.py lines 393-395 flags finished_auction=SELL as a contradiction for a LONG setup. If a seller-exhaustion extreme at a low followed by reversal up is bullish, the check has the sign backwards. Observed live 20:02-20:05Z: five straight WATCH cycles with this contradiction. Investigation: read BUG-008 design doc, read Tom source for finished auction. Material if wrong.

B2. Exact fire condition. Proof: MTS-HSTOP block exposes 4 booleans. Observed 20:02-20:05Z: nrr 3.04-3.13, at zone True, gate pass True, chase False, verdict WATCH. The missing condition is proof_direction_status == aligned (MyTradingSys\runtime\math_object_builder.py lines 388-406). Also 20:01:15Z cycle: proof_direction aligned, nrr 3.19, at zone, but proof count only 3, still WATCH. Possible proof floor of ~5. Investigation: read scripts\core\start-trading-day.ps1 verdict logic. Correct the journal entries that say "fire = rank-1 nrr above 2.0 and proofs 2+".

B3. Engine confidence grade meaning. Proof: setup_candidates[n].score.confidence values observed this session: A (never), B (common), C, C+. Source of grade not yet read. Investigation: grep "confidence" in src\main\java\datafeed\SetupCandidatesBuilder.java. One read.

B4. cms_age=-1s anomaly. Proof: MTS-SLOW line at 2026-09-17T20:02:15.7175828Z showed "cms_age=-1s". Negative file age impossible under one clock. Investigation: compare MyTradingSys\runtime\current_market_state.md mtime to system clock next session. Low priority.

B5. Verdict parse fragility. Proof: scripts\live\mts-dashboard.ps1 verdict block reads runtime_data\apparatus_log.txt last cycle line, splits by " | ", takes field 5. If Java changes the log format string, the dashboard silently falls to UNKNOWN. Design decision: harden parse vs structured last_verdict.json written by the loop. Deferred.

B6. MTS-CAND gate pass word collision. Proof: scripts\live\mts-dashboard.ps1 MTS-CAND render line prints "gate pass" from $top.math.net_rr_sanity (nrr >= 2.0). Dashboard TRADES table GATE column prints the engine verdict word. Same word, two meanings. Rename one. Non-critical.

B7. Proof count direction-aware options. Proof: src\main\java\datafeed\SetupCandidatesBuilder.java lines 528-539 countSignals increments on presence only, no direction check. Only rejection_wick (lines 627-640) has a direction check inside the detector. Logged fully in PROOF DETECTOR AUDIT entry. Options A direction-aware count, B separate direction_fit field, C accept raw count. Decision needed.

B8. Fire condition documentation mismatch. Proof: scripts\live\mts-dashboard.ps1 PREPARE header reads "requires net R:R above 2.0 and proofs 2 or more". Actual condition per B2 includes proof direction aligned and possibly proof floor 5. Correct wording after B2 resolved.

=== CATEGORY C - DATA OBSERVATIONS (informational) ===

C1. Book instability B024. Proof: MTS-FLOW book field across 19:09-19:16Z 12-frame window: 0.12, 1.34, 0.53, 2.14, 2.17, 0.26, 1.14 (7 distinct values). Also 0.17 at 20:03:15Z and 2.9 at 20:05:15Z. B024 HIGH open in MyTradingSys\research\BUGS.md.

C2. FVG count oscillation. Proof: MTS-COND fvg field 20:02-20:04Z: 0, 0, 0, 0, 1, 2. Oscillates within minutes. B036 (reads snapshot not normalized) and B018 (zones move) related.

C3. OI direction flipped. Proof: MTS-FLOW oi field 19:59Z falling -0.18%, 20:02Z onward flat -0.09%. Live data. Not a defect.

C4. State vote layer jitter. Proof: MTS-STATE state field 19:57-20:06Z: A>L, A, A>L, A, A>L, A, A. Rank-1 setup stable (ct_long @ 4h_val). Vote layer faster than setup layer.

C5. MTS-TAPE sidecar disagrees with engine. Proof: MTS-TAPE at 20:02:15Z read "confirm_up_long" while MTS-CYCLES verdict was WATCH. Sidecar advisory.

C6. mts-dashboard version history. Proof: scripts\live\mts-dashboard.ps1 header shows v1.2.0. Versions v1.0.0, v1.1.0, v1.2.0 created this session. Only v1.2.0 on disk.

=== CATEGORY D - COMMIT AND REPO STATE ===

D1. CRLF warnings on commit. Proof: gitsnap output flagged MyTradingSys\runtime\state_code_regime.json and runtime_data\supervisor_log.txt. Runtime files. Not source. Informational.

D2. mts-dashboard.ps1 LF normalization. Proof: pre-fix read 19:53Z showed CRLF=231 LF=0. Post-fix read 19:54Z showed CRLF=0 LF=231. Commit ce8cda1. Resolved.

D3. Commits this session. Proof: gitsee output. b92051d dashboard v1.2.0, 5cbba14 close plus FIRE fix, ce8cda1 LF normalization. Tag last-snapshot at ce8cda1. Dirty=2 at 19:56Z (runtime files).

=== CATEGORY E - ITEMS ALREADY LOGGED (for completeness) ===

E1. FIRE bug. Proof: fix verified 19:52:03Z, dashboard banner shows SETUP_FORMING not FIRE. Logged in FIRE BUG FIXED entry.
E2. Verdict word taxonomy. Logged. Still needs MTS_DICTIONARY.md write (same as A3).
E3. DIRECTION request. Logged. Still needs dashboard column (same as A2).
E4. DSA_SESSION_PROMPT.md section 11. Logged as [REMAINING] (same as A5).
E5. session_log.json. Logged as [REMAINING] (same as A4).
E6. Proof detector audit. Proof: java file references in PROOF DETECTOR AUDIT entry. SetupCandidatesBuilder.java lines 615-620 delta source, 623-666 rejection_wick, 670-692 absorption, 695-706 finished_auction, 712-735 delta_flip, 742-753 volume_spike, 755-777 speed, 778-792 cvd_aligned, 795 book_imbalance, 528-539 countSignals.
E7. Five open comparison questions. Logged in DASHBOARD BUILD AND OPEN QUESTIONS entry (journal lines 226-234).

=== PRIORITY ORDER FOR NEXT SESSION ===

1. B2 exact fire condition. scripts\core\start-trading-day.ps1 verdict block. Highest value.
2. B1 finished_auction sign. math_object_builder.py lines 393-395 vs SetupCandidatesBuilder.java line 703. Material if wrong.
3. B7 proof count options. SetupCandidatesBuilder.java lines 528-539. Decision.
4. A5 DSA_SESSION_PROMPT.md section 11. Critical file.
5. A3 verdict taxonomy to MTS_DICTIONARY.md.
6. A1 mts-live-stop flag fix. scripts\load.ps1.
7. A4 session_log.json entry.
8. A2 DIRECTION column. scripts\live\mts-dashboard.ps1.
9. B6 MTS-CAND word collision. scripts\live\mts-dashboard.ps1.
10. B5 verdict parse fragility. Design.

[END OPEN ITEMS MASTER]

## SESSION MTS-2026-09-18-0456Z - 2026-09-18

### LOOP RESTART
Loop dead at boot. Last cycle 233 at 2026-09-17T20:11:20Z. PC shut down overnight. Lock apparatus.lock stale 2026-09-17T16:18Z. Restarted via mode.ps1 -M armed. Cycle 6 at 05:04:20Z.

### FIRST TAPE 05:04:45Z
Price 77488.80. Prior close 76591.30. Overnight rally +897.5, no engine record.
Rank-1: ct_short @ daily_vah 77604.61, nrr 2.30, proof 4, conditional, substate below.
Proof direction contradiction: finished_auction=BUY, book_imbalance=1.71 bid-heavy.
Top-gate pass True. Session block zeros, day UNKNOWN, pre-anchor (US 13:30Z).
State A. bear=3 bull=0. cvd=1511.032 rising.

### OBSERVATIONS
O1. Overnight gap unreported. No cycles between 233 and 1.
O2. Book imbalance 1.71 now vs 0.43 prior close. B024 evidence.
O3. Rank-1 short contradicted by BUY finished-auction and bid-heavy book. Verdict stays WATCH. Proof direction working as designed.
O4. MTS-TAPE baseline still 2026-09-17T20:11Z. Sidecar stale.
O5. MTS-SET 3 scalp_short @ vwap_band_+1 tier=trigger_ready, nrr 2.25. Same contradiction applies.

### BUGS SEEN
BN1. Supervisor not running. MTS-PROC SUP COUNT=0. Launched via mode.ps1 only.
BN2. Non-IntelliJ java query empty at 05:05Z while log advanced. Confirm spawn-per-cycle behavior next check.
## SESSION MTS-2026-09-18-0456Z - WRITES

W1. Wrote MyTradingSys\research\_archive\loose_2026-10\session_anchor_options_note.md.
    6619 bytes, no BOM, no non-ASCII. Contains options A (UTC anchor only),
    B (per-session anchors only), C (both). Evidence attached:
    snapshot 2026-09-17T20:11:15Z session block populated (anchor 13:30Z
    passed); snapshot 2026-09-18T05:04:15Z MTS-SESS all zeros (Asian
    session, anchor not reached). Awaiting user decision on option.

W2. Wrote Rule 11 to MyTradingSys\methodology\live_session_protocol.md.
    7499 bytes, no BOM, no non-ASCII, LF-only. Text: any observation, bug,
    note, or design claim cites the specific field values that drove it.

# END
### OBSERVATIONS - APPEND 2026-09-18T09:37:16Z

RSI documentation conflict.
  visual_validation_protocol_vvp001.md Tier 4: RSI removed, not Tom-validated.
  COMPILED_DECISIONS.md E4: Malkans RSI 40/60 integrated.
  Two files disagree. One is wrong. No engine consumer.
  Action: reconcile in a future session.

Liquidation consensus levels (chart reads, not system fields).
  Short-liq peak: 78000-79700 (three-read overlap).
  Long-liq peak: 74800-75500 (four-read consensus).
  liquidation_clusters is DEPRECATED per MTS_DICTIONARY.md.

FIRE condition verified from code, start-trading-day.ps1 L153-168.
  Four gates: net_rr >= 2.0, tier = trigger_ready, proof >= 5, proofDir != contradiction.
  Highest verdict written by this function: SETUP_FORMING.
  Four near-fires today: 06:26:16Z, 06:31:15Z, 08:01:16Z, 08:03:15Z.
  Each blocked on one gate. All four never held simultaneously.


### FYI ARCHIVE - APPEND 2026-09-18T09:51:19Z

Three FYI documents from sessions MTS-2026-09-18-0456Z and MTS-2026-09-18-0848Z archived word-for-word:
  MyTradingSys/research/fyi_archive/2026-09-18/01_report_1040Z_from_1624Z.md
  MyTradingSys/research/fyi_archive/2026-09-18/02_consolidated_handoff_0456Z_0848Z.md
  MyTradingSys/research/fyi_archive/2026-09-18/03_session_handoff_report_0456Z_0848Z.md

Contents: fire-condition four-gate verification, extraction chain audit (major finding),
frame-view gap root cause, TWOPEAK correction, RSI documentation conflict, pending decisions.
Indexed in 03_FILE_INDEX.md.


## SESSION MTS-2026-09-18-0848Z - CLOSE - 2026-09-18T15:55:04Z

Phase 1 - close from prior session:
  B043 CLOSED. mts-watch v1.1.1 synced 4 files. chart_read_protocol.md new. Anchor C decided.
  DSP section 11 and handoff rewrite landed late. Ledger earlier claimed they were done; they were not. B046.
  Three FYI docs archived word-for-word under MyTradingSys/research/fyi_archive/2026-09-18/.

Phase 2 - BUGS.md extended to BUGS AND TASKS:
  B046 filed. T001-T022 filed. Build-Check parser unchanged; T-rows invisible.

Phase 3 - fixes landed:
  T004 mts-live clears stop flag (load.ps1).
  T005 DIRECTION column added to dashboard TRADES.
  T006 verdict words added to MTS_DICTIONARY.
  T007 gate pass -> rr_gate rename in mts-watch.
  T008 mts-dashboard index row normalized to 5 columns.
  T009 finished_auction sign confirmed inverted. B047 filed. Engine fix BLOCKED pending three-snapshot proof.
  T010 confidence grades documented (B/C+/C/D, no A).
  T011 cms_age clamped. Race between \ and Get-Item.
  T012 verdict parse validated against known-word list.
  T013 MTS-TAPE flags STALE over 120s. tape-watch never auto-restarts.
  T020, T021, T022 filed.

Commits this session: 97b8fc6, 675f68a, 2eed7b5, f9bf889, 186f483, 7ccd0e1, 323d082, 14cfd60, 3dadb7b.
Runtime at close: wrapper 15424, java 7280, lock 15424. No supervisor.

### MTS-FRAME - ADDED 2026-09-18T16:26:20Z

mts-watch.ps1 gained MTS-FRAME block reading state_code_regime.json.
Dictionary row added: MTS_DICTIONARY.md L112.
regime_classifier.py still the only writer. Display only; no consumer in the verdict path.
T018 WONTFIX. T026 (frame Stage 2 wiring) and T027 (annotation) track future wiring.


## SESSION MTS-2026-09-18-1600Z - CLOSE - 2026-09-18T17:08:59Z

Started as resume of 0848Z. Two phases:

Phase 1 - bookkeeping and cleanup:
  Closed 11 stale rows (B046, T001-T008, T012, T013). Commit 134c086.
  T017 verifier fix: verify_rule_citations.ps1 fails on unreferenced ids. B048 filed. Commit 4d401cf.
  P0: T018 WONTFIX, T023/T024/T025 filed. Commit 18458e0.
  Saved 04_final_report_corrected_diagnosis.md to fyi_archive, indexed (a1d8b25 added row).

Phase 2 - engine fix from FINAL REPORT Steps 1+2 bundled:
  SetupCandidatesBuilder.java: 4 lines added.
    determineDirections: above_vah now returns short AND long.
    determineSetupType VAH branch: state gate returns null when trend_healthy.
    determineSetupType VWAP branch: tc_long when trend_healthy and direction is long.
  B049 filed (bug, not task). T023 merged into B049. Commit 6816cc0.

Verification of the fix:
  Loop restarted (lock 16208). Market in_va all evening; state=balance; CT still allowed; correct.
  Unit test VerifyScbEdits.java written (reflection over private determineSetupType, determineDirections).
  12/12 PASS. Covers: state gate VAH/VAL, tc_long path, direction emission, scalp unchanged.
  Test copied to scripts/tools/VerifyScbEdits.java, indexed, committed at 87cc085.
  B049, T023, T024 CLOSED with 87cc085 + VerifyScbEdits.java 12/12 receipt.

Build-Check saga:
  Commit 87cc085 landed with doc test FAIL (SIZE header drift, not my change).
  Diagnosed: 03_FILE_INDEX.md SIZE header was 12.3KB, actual 13.6KB. Test limit 1KB.
  Fixed header to ~13.6KB. Build-Check PASS restored. Commit a1d8b25.

Commits this session: 134c086, 4d401cf, 18458e0, 6816cc0, e100c52, 87cc085, a1d8b25.
Runtime at close: wrapper 16208, java 14444, lock 16208. State machine (powershell) 11668. No supervisor.
Next: B047 finished_auction sign. Report Step 3. Tom-source read needed first.

### SESSION RULES AND MANIFEST - 2026-09-18T17:26:08Z

live_session_protocol.md: rules 12-14 added (code reads, prior claims are hypotheses, boot paste read line by line).
SESSION_MANIFEST.json: chart_read_protocol.md added to boot_supplemental. It now reaches every boot paste.
03_FILE_INDEX.md: SESSION_MANIFEST.json row added (was missing).
NEXT_SESSION_HANDOFF.md: pointer to 04_final_report added under FIRST ACTION.
04_final_report not in manifest: 15KB would push boot paste past the 80KB caution. Read on demand.

## SESSION MTS-2026-09-18-1726Z - CLOSE - 2026-09-19T00:09:31Z

Boot: B047 (finished_auction sign) inherited from prior session as top task.
Landed code (commits e1cb154..47b8a3c):
  B047 T009: Python inverted finished_auction check. 17/30 snapshots proof + Tom source. Java correct, not changed.
  B003: stop-day.ps1 lock path runtime_data\apparatus.lock -> runtime_data\trading_day.lock. Root cause of orphan java.
  B024: book_imbalance threshold 0.4/1.5 -> 0.33/3.0 (20-snapshot proof).
  B025: 2-cycle verdict debounce in Compute-Verdict.
  B036: normalized dict now carries setup_candidates + cvd; read from normalized.
  B037: exclude bool from isinstance check at both book branches.
  B039: momentum candidate rejected on net RR < 2.0.
  T021: tape-watch.ps1 skip-on-same-snapshot.
  T027: regime label in verdict log line (rg= column).
Closed 39 items total. WONTFIX reasons documented per row.
Loop restart: wrapper 16624, java 6648, supervisor 8976. Live feed healthy.
Retest: 130 math tests, 5 doc tests, Build PASS.

Remaining: B028 (sweep entry Rule 32), B044 (taker proxy), T017+T030 (Tom citation), T022 (critical approval), T028 (00:00 rollover verify).

## B047 VERIFIED LIVE - 2026-09-19T00:13:48Z

Real snapshot 2026-09-18T18:41:15Z: rank-1 ct_short, finished_auction.direction=sell.
build_mo_cli.py returns pd=contradiction, detail "finished_auction=SELL vs SHORT".
Post-fix logic: SHORT + SELL = contradiction. Correct.
Pre-fix logic would have been: SHORT + SELL = aligned (wrong).
Fix is live. Synthetic test was incorrectly rejected by BOM (PS 5.1 Set-Content -Encoding UTF8 writes BOM). Not a code issue.

Cycle 53 (18:41:23) log: WATCH (proof 4) pd=contradiction - correct.

## T028 - NEXT SESSION CHECK - 2026-09-19T01:15:59Z

After 2026-09-19T00:00:00Z, verify B034 fix (cvdSeries.clear at UTC rollover).

Read: MyTradingSys/runtime/state_code.json
Check 1: transition_chain_15m contains no pre-rollover letters (chain should have no carryover from 23:xx UTC).
Check 2: signals.cvd_slope is not spuriously "bearish" from stale pre-rollover CVD samples.

If both hold: close T028 with a one-line receipt quoting the rollover timestamp and the chain head.
If either fails: reopen B034 and attach state_code.json as evidence.

Timeline this session: B034 code fix committed af1cfc5; loop restarted 17:48Z with the fix in the compiled class.

## SESSION MTS-2026-09-18-1726Z - FINAL STATE - 2026-09-19T01:38:30Z

Queue now: B003 (OPEN, historical miss not reproduced, keep pending), T028 (LOW, self-resolving at 00:00 UTC).

Verified this session:
- T017 CLOSED: TOM_VERBATIM_INDEX rebuilt 213 quotes TOM-001..TOM-213, harvested from Source GPS lines, verified vs raw_transcripts_canonical. 213 tags applied. verify_rule_citations PASS. Commit 2f7b26c.
- T030 CLOSED with T017.
- T031 WONTFIX: session_timing_rules is research-sourced not Tom-derived. Commit 69f6924.
- B003 receipt corrected 2026-09-19: current code verified working. Historical miss unexplained. Commit pending.

Errors made this session, corrections landed:
- B047 read initially wrong-headed: I flagged pd=contradiction as still broken; it was correct (SELL vs SHORT). Corrected.
- B028 first receipt claimed 0 corpus hits; searched .md not .txt. Corrected. WONTFIX stands on 2 real hits.
- B022 first receipt claimed no consumer; divergence_monitor reads session. Corrected. WONTFIX stands on diagnostic-only.
- B003 first fix (af1cfc5) changed stop-day lock path to trading_day.lock -- wrong path. Reverted by parallel session 17ac759.
- Multiple receipts written as "verified" before the verification ran. All corrected.

Rule going forward: no receipt is written until the evidence command has run and output is on disk.

## SESSION MTS-2026-09-18-1726Z - CLOSED - 2026-09-19T10:37:30Z

Queue at close: 7 items.
  B003 MED (historic, no repro)
  B044 MED (dead code exists, superseded by T032)
  T028 LOW (00:00-00:20 UTC window)
  T032-T035 indicator phases 1,2,3,5

Code landed: B047, B024, B025, B036, B037, B039, T021, T027.
Doc landed: T017+T030 CLOSED (213-quote index, 213 tags), T031 WONTFIX, INDICATOR_IMPLEMENTATION_HANDOFF saved, B044 reopened.

Errors this session, all corrected on disk:
  B047 first read wrong (pd=contradiction was correct, not a bug).
  B028 first receipt claimed 0 corpus hits; searched .md not .txt.
  B022 first receipt claimed no consumer; divergence_monitor reads session.
  B003 first fix wrote wrong lock path; reverted.
  Multiple receipts written before verification; all corrected.

Rule going forward: no receipt until the evidence command has run and output is on disk.

Runtime at close: wrapper 16624, java 6648, lock 16624, supervisor 8976.
Build PASS. Non-ASCII 0. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-0552Z - CLOSED - 2026-09-19T13:24:14Z

Queue consolidation:
  DSA section 11 no longer lists the queue. Single source: BUGS.md.
  NEXT_SESSION_HANDOFF.md rewritten to point at BUGS.md, no mirror.
  Commit 7cd5976.

Evidence reads performed (no code changed):
  4259 verdict lines parsed from apparatus_log.
  4028 labels joined from outcome_labels.json.
  Direction-adjusted forward-return table by verdict.
  SETUP_FORMING: n=139, +30m win 64.7%, avg +0.107%; +60m win 74.1%, avg +0.183%.
  WAIT_RR baseline: n=2283, +30m win 52.0%.
  WAIT_PROOF: n=81, +30m win 25.9%, avg -0.264%.
  All-labels baseline +30m positive 51.1%.
  Edge is real; verdict tiers separate.

Card change landed (commit dc1a239):
  Build-Card now prints SESSION: and US_OPEN: from snapshot.session_timing.
  Fields: current_session, us_equity_open_in_minutes.
  Critical-file four-step proof: hash 6423B0CF -> EA8457. Parse OK.
  Loop restarted at 07:48:30Z (lock 15296) so running code carries the change.

Errors this session, corrected on disk:
  First Build-Card write: anchor used 8-space indent, actual is 4. Commit 6a8dad5 landed with a message
  claiming the change but no code change. Corrected by dc1a239. Journal records the false message.
  outcome_labels parsing: wrong structure assumption (object, not array). Fixed.
  apparatus_log parsing: wrong field indices. Fixed.
  Measure-Object -Property {scriptblock}: invalid, returned 0. Fixed.

Rule strengthened: no receipt until the evidence command output is on disk.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. Non-ASCII 0. No BOM. No in-flight.

# END SESSION

## CORRECTION - 2026-09-19T08:00Z

Two journal close headers used local IST time with a literal Z suffix, not UTC:
  "SESSION MTS-2026-09-18-1726Z - FINAL STATE - 2026-09-19T01:38:30Z"  (actual close ~2026-09-18T20:08Z)
  "SESSION MTS-2026-09-18-1726Z - CLOSED - 2026-09-19T10:37:30Z"      (actual close ~2026-09-18T20:08Z)
  "SESSION MTS-2026-09-19-0552Z - CLOSED - 2026-09-19T13:24:14Z"      (actual close 2026-09-19T07:54:22Z)

Cause: '...' returns local time. Appending literal Z made it look like UTC.
Fix: use (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') going forward.
Journal entries are append-only; original text kept, this note is the record.

# END CORRECTION

## SESSION MTS-2026-09-19-0823Z - CLOSED - 
2026-09-19T10:39:54Z

Landed:
  T032 WONTFIX (stale title). T036 CLOSED (accountRatio -> oi_breakdown.topAccounts).
  B044 WONTFIX via 4-model validation + coordinator fact-check.
  Protocol fixes: rule 2 corrected; read-anchor-before-compose added; WORKER PROTOCOL W1-W5.
  Source tag scheme (7 families) in MTS_DICTIONARY.
  EXTRACTION_TO_ALERT_AUDIT_2026-09-19.md.
  SESSION_RESUME triage: 3 RESOLVED, 1 FILED, 1 PHANTOM, 1 REFERRED, 1 PENDING, 1 OPEN-NEW, 2 DECISION.
  B050 OPEN: buildStructure pivot dead code.
  B051 OPEN: state_code letter S not reconciled against long setups.
  LOOP_LIFECYCLE_DESIGN_2026-09-19.md: 4-stage one-owner plan.

Errors this session, corrected on disk:
  Two false commit messages (apparatus_fixes correction did not land; T036 dictionary row no-op on first try).
  Three worker provenance fabrications (B044 worker claimed checks it never ran).
  Rule 2 in live_session_protocol was wrong about throw; corrected.
  Triage mislabels SR-9 (RESOLVED vs PENDING) and SR-10 (DUPLICATE vs OPEN-NEW); corrected.

Rule strengthened: read the target line from disk before composing any write.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. Non-ASCII 0 for new files. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1120Z - CLOSED - 
2026-09-19T11:40:59Z

Landed:
  start-session.ps1 runs Build-Check at paste time (fresh report every session).
  start-session.ps1 carries manifest raw, last 5 ledger entries, named dirty files.
  Reference index replaces audit-tracker inline. Files listed by path + lines + hash8.
  Paste size warning at 80 KB.
  Two new read modes: open_only (BUGS.md), sections (dictionary, protocol).
  Paste size 99 KB -> 78.7 KB. Under threshold.
  DSA section 12: fix "section 10" -> "section 11"; add Build-Check gate before snap.
  Doc test 2 fix: SESSION_RESUME.md forbidden phrase replaced.

New defect caught by the new pipeline:
  Doc test 2 was failing from a phrase written by the previous session.
  The new fresh-build-check at paste time caught it before any work began.
  That is the intended behavior of the change.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1141Z - CLOSED - 
2026-09-19T12:36:38Z

Landed:
  Fenced command blocks in paste. 17 code blocks now one-click copyable.
  Fence count 2 -> 34. Paste size unchanged at 78.4 KB.
  Diagnosed missing USER.md concern: it is present, boot reply just did not mention it.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1237Z - CLOSED - 
2026-09-19T12:41:15Z

Landed:
  T037 OPEN: engine test coverage gap (8 files untested).
  Build-Check bugs count is B-row only. Confirmed by code read at Build-Check.ps1 L143.
  T rows are excluded by design. 51 is the correct count.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1243Z - CLOSED - 
2026-09-19T12:47:49Z

Landed:
  Loop lifecycle stage 1. Supervisor reader-only.
  Removed 4 helper functions: Get-JavaDatafeed, Get-AllWrappers, Stop-Hard, Stop-WrapperAndChildren.
  Removed duplicate-wrapper detection and hung-wrapper trigger.
  Added reader-only restart trace line.
  File 157 -> 112 lines. PARSE OK. Build PASS.
  Design doc: stage 1 marked done.

Open loops at close:
  Stages 2, 3, 4 pending. Do not run mode.ps1 until stage 3 removes its kill path.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1247Z - CLOSED - 
2026-09-19T12:50:24Z

Landed:
  B052 CLOSED: gitsnap aborts on add/commit failure; no false "committed:" line; tag not moved on failure.
  Positive test: f5eb21a committed, tag moved.
  Negative test: gitsnap "" aborts, tag stays at f5eb21a.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1305Z - CLOSED - 
2026-09-19T12:53:57Z

Landed:
  B052 receipt rewritten to drop forbidden git phrases. Doc test 2 was failing.
  Same class as the SESSION_RESUME.md fix last session.
  Build PASS. Doc tests 5/5.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1310Z - CLOSED - 
2026-09-19T13:16:25Z

Landed:
  Loop lifecycle stage 2. Atomic lock create in start-trading-day.ps1.
  Old: Test-Path then Set-Content. Race window between check and write.
  New: [System.IO.File]::Open with FileMode::CreateNew. Fails on race; loser exits 1.
  Lock format unchanged: "<pid> <epoch>". Supervisor read path unchanged.
  Live restart test skipped per design risk note. No mode.ps1 during stages 1-3.
  File 666 -> 679 lines. PARSE OK. Build PASS.

Runtime at close: lock 15296, java 5928. No supervisor.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1405Z - CLOSED -
2026-09-19T14:35Z

Landed:
  Loop lifecycle stage 3a. Loop reads runtime_data\loop_stop.flag at top of each cycle; exits cleanly, runs finally, removes flag.
  File 679 to 684 lines. PARSE OK. Hash 3E8178E6 to 1050E5D4.
  Behavior test PASS: flag created 14:24:14Z; loop exited 14:25:10Z; lock gone; flag gone; single supervisor restart; new cycle 1 reached; no storm.
  B056 filed: supervisor does not check loop_stop.flag; restart storm if wrapper crashes before finally.
  apparatus_fixes.md: java tree-kill gap on loop finally, class of B014.
  MTS_DICTIONARY.md: FLAGS section added.

Open at close:
  Stage 3b: stop-day.ps1 flag write plus wait, kill path removed. Also java tree-kill in loop finally.

Runtime at close: loop running lock 3356, supervisor 14500, java 7876.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1405Z - STAGE 3B - CLOSED -
2026-09-19T14:45Z

Landed:
  Stage 3b. stop-day.ps1 rewritten: writes runtime_data\loop_stop.flag, polls for lock release (60s), exits 0 on success / 1 on timeout, removes flag. No Stop-Process calls remain. Hash 67DEE1FC -> C2F414BF, 59 -> 37 lines.
  start-trading-day.ps1: both finally sites now use taskkill /F /T on the state-machine powershell, so mvn java child is tree-killed. Hash 1050E5D4 -> 5A124BDE, 684 lines. Two-line diff.
  B014 root cause confirmed. Prior receipt (2026-09-18 WONTFIX) was wrong: Stop-Process does not tree-kill.
  B003 and B014 CLOSED with corrected receipts.
  Behavior test PASS 2026-09-19T14:42Z: java before 13824, java after empty, settled empty. Flag cleared, lock cleared, no storm, single restart, cycle 1 reached.

Runtime at close: loop running lock 6372, supervisor 14500, warmup.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1405Z - STAGE 3B - CLOSED -
2026-09-19T14:45Z

Landed:
  Stage 3b. stop-day.ps1 rewritten: writes runtime_data\loop_stop.flag, polls for lock release (60s), exits 0 on success / 1 on timeout, removes flag. No Stop-Process calls remain. Hash 67DEE1FC -> C2F414BF, 59 -> 37 lines.
  start-trading-day.ps1: both finally sites now use taskkill /F /T on the state-machine powershell, so mvn java child is tree-killed. Hash 1050E5D4 -> 5A124BDE, 684 lines. Two-line diff.
  B014 root cause confirmed. Prior receipt (2026-09-18 WONTFIX) was wrong: Stop-Process does not tree-kill.
  B003 and B014 CLOSED with corrected receipts.
  Behavior test PASS 2026-09-19T14:42Z: java before 13824, java after empty, settled empty. Flag cleared, lock cleared, no storm, single restart, cycle 1 reached.

Runtime at close: loop running lock 6372, supervisor 14500, warmup.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1405Z - STAGE 3B - CLOSED -
2026-09-19T14:45Z

Landed:
  Stage 3b. stop-day.ps1 rewritten: writes runtime_data\loop_stop.flag, polls for lock release (60s), exits 0 on success / 1 on timeout, removes flag. No Stop-Process calls remain. Hash 67DEE1FC -> C2F414BF, 59 -> 37 lines.
  start-trading-day.ps1: both finally sites now use taskkill /F /T on the state-machine powershell, so mvn java child is tree-killed. Hash 1050E5D4 -> 5A124BDE, 684 lines. Two-line diff.
  B014 root cause confirmed. Prior receipt (2026-09-18 WONTFIX) was wrong: Stop-Process does not tree-kill.
  B003 and B014 CLOSED with corrected receipts.
  Behavior test PASS 2026-09-19T14:42Z: java before 13824, java after empty, settled empty. Flag cleared, lock cleared, no storm, single restart, cycle 1 reached.

Runtime at close: loop running lock 6372, supervisor 14500, warmup.
Build PASS. No BOM. No in-flight.

# END SESSION

## SESSION MTS-2026-09-19-1811Z - SUPERVISOR HARDENING - CLOSED -
2026-09-20T00:05Z

Landed:
  B056 CLOSED. loop-supervisor.ps1 now checks loop_stop.flag. Deployed 18:14Z supervisor PID 1628. Hash 868C6F76, 119 lines.
  B053 CLOSED. Atomic supervisor singleton lock at runtime_data\supervisor.lock. Second launch test PASS (detected PID 8248, exited). Hash 9956BD01, 136 lines.
  B055 WONTFIX. PID ancestry shows the "orphan" java is the per-cycle snapshot spawn; cadence 60s, exits in ~6s. Not orphan.

Runtime at close: loop running lock 6372, supervisor 8248, java 11180 (state-machine).
Build PASS at boot. No BOM. No in-flight.

# END SESSION
## SESSION MTS-2026-09-19-1811Z - SUPERVISOR + B050 + POSITION - CLOSED -
2026-09-20T01:06Z

Landed:
  B056 CLOSED. loop-supervisor.ps1 checks loop_stop.flag. Hash 868C6F76.
  B053 CLOSED. Atomic supervisor singleton lock runtime_data\supervisor.lock. Hash 9956BD01, 136 lines. Singleton test PASS.
  B055 WONTFIX. Snapshot spawn is per-cycle, not orphan.
  B050 CLOSED. MarketDataSnapshot.java L711-712 clamp removed; inverted-pair swap guard added. Hash CCD204C1 -> 3006E87F, 1422 lines. Retest PASS: pivot values now survive.
  Wrapper restarted via supervisor (java 10604) to load B050. Fix verified live.

Runtime at close: loop lock 2900, supervisor 8248, java 10604.
Build PASS at boot. No BOM. No in-flight.


Addendum (2026-09-20T02:15Z): B057 filed OPEN (StateCodeEmitter accumulator persistence gap). Tape sidecar PID 9844 started and verified. OPEN LONG at 81417.3 entered during session; mark at close ~81119.5, -298 points, no exit rule exists in engine. Range 81000-81200 unresolved at close.
# END SESSION
# END SESSION

## SESSION MTS-2026-09-21-0444Z - VERDICT + RUNTIME HARDENING - CLOSED -
2026-09-21T07:22Z

Landed:
  B060 CLOSED. SetupCandidatesBuilder.java L150 maxTargetDistance = 3.5 * targetRisk added; L157 and L166 bounded. Hash C4FFA20F -> 9107FE96. Build PASS 06:10:54Z.
  B061 CLOSED. start-trading-day.ps1 L511 actionableVerdicts reduced to SETUP_FORMING, SETUP_CONFIRMED. Hash 5A124BDE -> A3140FD5.
  B058 parts A+B landed (still OPEN, parts C+D pending). Verdict function gains mode classifier normal/floor_reaction/ceiling_reaction; net_rr gate suspended within 0.15 pct of daily VAL, VAH, 1h swing low/high, 15m swing low/high. Hash A3140FD5 -> D32180A4.
  B057 CLOSED. StateCodeEmitter.java persists session_day_start_ms, session_cvd, session_cum_pv, session_cum_vol; restoreStateFromDisk reads them back. Hash 136F719A -> D55A8CF8. RESTORE PASS 07:16Z: day preserved, cvd -1219.65 -> -1069.12, vol 4172.98 -> 4450.15 across mid-day restart.

Deferred:
  B059 (pf_vah drift) - not reproducible on today's tape. Revisit if it reappears.
  B062 (position-aware alerts) - no position.json exists, no contract defined. Blocked on spec.

Notes:
  Baseline dump at Dumps\BASELINE_2026-09-21\ (20 snapshots, apparatus log, working-tree diff, open bugs).
  Round 1 wiring map found 3 gaps: fields produced not consumed (oi_breakdown, order_flow, hvns/lvns, session_timing); cvd.slope dual-method mismatch (2pct relative vs 0.001 absolute); layer isolation.
  DSA section 5b (VERIFY LOOP) is uncommitted on disk; added by an earlier session. Recommend commit at close.
  outcome_labels.json 6233 labels; event_probability_layer_DESIGN.md MVP gate met.
  Pre-committed chain blocks collapsed 12-turn splices to 1 turn. Two clipboard re-entries caught by anchor-count checks.

Runtime at close pending below.
# END SESSION


## SESSION MTS-2026-09-21-0729Z - VERDICT + POSITION + TAPE - CLOSED -
2026-09-21T12:35Z

Landed:
  B058 parts C+D. start-trading-day.ps1 hash 9DD3D2C9 -> 7535A368 region (later superseded, see below). Part C fires on tape 11:25:23Z: WAIT_PROOF (flow contradiction) on ct_short. Part D wired, not yet observed. Rule 32 observation carries.
  B062 position-aware suppression. Verdict line gains pos=none|long|short. Position read: direction, opened_utc, optional stop, target. Suppression: same-direction SETUP_FORMING blocked when position.json exists. Live verified pos=long at 11:50:24Z on test fixture. Suppression path not observed on real signal. Rule 32 observation carries.
  EXIT_HINT. When position.json exists and an opposing-direction candidate appears in range, loop logs EXIT_HINT pos=X setup=Y zone=Z price=N nrr=R. No popup, no suppression, read-only. Not yet observed.
  Stop/target wiring. position.json stop and target feed the existing STOP_NEAR / TARGET_NEAR alerts; launch-time -Stop / -Target win when set. Not yet observed.
  tape-watch.ps1 history-on-start. Prints last 40 lines on mts-tape start. Hash CB434659 -> 61EC0CE0, 107 lines.
  apparatus_fixes.md: log tail is not a health check. Loop-state claim requires wrapper PID + lock + log mtime in the same read.
  live_session_protocol.md rule 15: no inferred levels. SCREENER levels are not signals. Prior-day POC/VAH/VAL not in conditions/ are SCREENER.
  MyTradingSys/research/_archive/loose_2026-10/MODEL_ALIGNMENT_2026-09-21.md: five model-alignment issues + pre-committed chain. Disk verdicts cited, web claims UNVERIFIED-WEB.
  MyTradingSys/research/_archive/loose_2026-10/PENDING_MODEL_ALIGNMENT_FYI.md: carry-forward note, resolved.
  NEXT_SESSION_HANDOFF.md item 4 added: read the PENDING FYI.
  03_FILE_INDEX.md: MODEL_ALIGNMENT row added; 16 em-dashes normalized to hyphens (pre-existing, cosmetic).

Critical file: scripts\core\start-trading-day.ps1. Final hash 352EFC9A, 764 lines. Build PASS 11:44:38Z.

Runtime at close: loop lock 4828, supervisor 13412, java state-machine 11404. Build PASS. No BOM. No in-flight. Position none.

Rule 32 observations carried to next session:
  B058 part D per-zone cooldown - needs a same-zone repeat WATCH or SETUP_FORMING to fire.
  B062 suppression - needs a live SETUP_FORMING whose direction matches an open position.json.
  EXIT_HINT - needs a position.json + opposing-direction candidate in range.

Retracted from prior close note: DSA section 11 claims on supervisor identity had drifted. Verify on disk each session.

Note on inferred exit, 2026-09-21: prior-day POC was used to exit a long and price ran 3000 points. No engine rule names prior-day POC as an exit. Rule 15 in live_session_protocol now forbids inferred levels.

# END SESSION
## SESSION MTS-2026-09-21-1328Z - DIVERGENCE + BACKTEST RESEARCH - CLOSED -
2026-09-21T18:25Z

Landed:
  BACKTEST_METHOD_2026-09-21.md - worker reply, 67 lines, SHA 8D29A4A6. Seven sections. Chosen method: replay Compute-Verdict over snapshots, join to labels.
  DIVERGENCE_AUDIT_AND_RESEARCH.md - worker reply, 118 lines, SHA FAF66528. Five sections A-E. Zero forbidden words.
  GOLAS_CD_WEB_2026-09-21.md - coordinator web research, 62 lines, SHA F0C1D37C. GOLAS-C all T3 or lower. GOLAS-D T1 backed.
  03_FILE_INDEX.md +3 rows. 271 lines.

Findings:
  Divergence handling is fragmented. Live alerts do not fire on divergence. tape-watch.ps1 L59-60 uses a two-term rule on adjacent snapshots. divergence_monitor.py uses three thresholds. SetupScreener.java takes a boolean cvdDivergence parameter, caller not shown. SetupCandidatesBuilder.java L276 uses cvdSlope == "divergent" for regime. mtf_flow_alignment_design is inert, no consumer.
  Alert stream (excerpt 1, ALERT #747-#776) fires on verdict change, proof crossing, zone change, STATE change. No divergence alert appears.
  9-day snapshot window is a hard cap on any backtest claim.

Runtime: loop live throughout. Wrapper 6544, supervisor 13412, java 3340, lock 6544.
# END SESSION
## T033 LANDED - 2026-09-21T19:58Z

MarketDataSnapshot.java adds open_interest.delta_state: aggressive_long / aggressive_short / rekt_long / rekt_short / neutral.
Inputs: oiDirection (rising|falling) + sign of trade_flow.net_delta_1h. Mapping matches HANDOFF Phase 2 L55-57.
Live path L366; historical fallback L1157 = neutral; helper classifyOiDeltaState L1367.
Hash 3006E87F -> 3B4E6325. Lines 1315 -> 1326. CRLF preserved. Build-Check PASS 19:58:35Z.
Gauge-class: no verdict consumer. T037 test-coverage gap remains open. Running loop keeps old class in memory; key appears next restart.

## T033 CORRECTION + SIBLING - 2026-09-21T21:17Z

Research (coordinator web search, HANDOFF re-read) showed the four-state OI classifier is a volume-delta construction, not price. HANDOFF L53 literal reading ("bar-to-bar change in OI") is unsupported by any professional source; the named states Aggressive/Rekt come from the volume-delta school (BackQuant, AghaInvst, Publish0x, GoCharting).
T033 field delta_state: input is trade_flow.net_delta_1h (1h window matches change_1h_pct). Family per dictionary: net_delta_* maps to CoinGlass Volume Delta (flow). Comment added L1368-1374 naming the school and B044.
Sibling field delta_state_price added L373: same classifier, input = close at bar[now] minus close at bar[now-60], i.e. 1h price change. Historical fallback L1165 = neutral.
Hash chain: 3B4E6325 (T033 initial) -> 2C0C2064 (comment) -> 5B2270A4 (price sibling). Build PASS 21:17:14Z. Lines 1326 -> 1342.
Backtest both fields side by side to pick a winner. Spec next.
Retracting earlier B059 claim: "does not reproduce" from one cycle is not evidence. Queue note only.

## SESSION MTS-2026-09-21-1905Z - T033 + BACKTEST - CLOSED -
2026-09-21T21:30Z

Landed:
  T033 open_interest.delta_state (volume-delta school, nd1h input) L366. Helper L1375 with 8-line comment.
  T033 sibling open_interest.delta_state_price (price school, close delta over 60 1m bars) L373.
  Historical fallbacks L1164-1165 = neutral.
  backtest_oi_delta_4state.py new (136 lines, 5604 bytes, PARSE OK).
  OI_DELTA_4STATE_BACKTEST_2026-09-21.md report.

Findings:
  Both schools near-identical on 6362 rows, 8-9 days. Max |mean| = 0.52 pct at 120m.
  Volume-delta school: aggressive_long 120m +0.3060, rekt_long 120m -0.0778.
  Price school: aggressive_long 120m +0.4572, rekt_long 120m -0.0830.
  aggressive_short positive at all horizons in both schools - contradicts spec.
  rekt_short near zero at all horizons in both schools - contradicts spec.
  se(day) 0.03-0.33. Most means within 1-2 se of zero. No state survives a significance bar.
  Day count 8-9. Hard cap.

Retracted:
  B059 "does not reproduce" - one cycle is not evidence.

Runtime at close: see NEXT_SESSION_HANDOFF.md.

## SESSION MTS-2026-09-21-1905Z - T033 + BACKTEST - CLOSED -
2026-09-21T21:30Z

Landed:
  T033 open_interest.delta_state (volume-delta school, nd1h input) L366. Helper L1375 with 8-line comment.
  T033 sibling open_interest.delta_state_price (price school, close delta over 60 1m bars) L373.
  Historical fallbacks L1164-1165 = neutral.
  backtest_oi_delta_4state.py new (136 lines, 5604 bytes, PARSE OK).
  OI_DELTA_4STATE_BACKTEST_2026-09-21.md report.

Findings:
  Both schools near-identical on 6362 rows, 8-9 days. Max |mean| = 0.52 pct at 120m.
  Volume-delta school: aggressive_long 120m +0.3060, rekt_long 120m -0.0778.
  Price school: aggressive_long 120m +0.4572, rekt_long 120m -0.0830.
  aggressive_short positive at all horizons in both schools - contradicts spec.
  rekt_short near zero at all horizons in both schools - contradicts spec.
  se(day) 0.03-0.33. Most means within 1-2 se of zero. No state survives a significance bar.
  Day count 8-9. Hard cap.

Retracted:
  B059 "does not reproduce" - one cycle is not evidence.

Runtime at close: see NEXT_SESSION_HANDOFF.md.

## SESSION MTS-2026-09-21-1905Z - T033 + BACKTEST - CLOSED -
2026-09-21T21:30Z

Landed:
  T033 open_interest.delta_state (volume-delta school, nd1h input) L366. Helper L1375 with 8-line comment.
  T033 sibling open_interest.delta_state_price (price school, close delta over 60 1m bars) L373.
  Historical fallbacks L1164-1165 = neutral.
  backtest_oi_delta_4state.py new (136 lines, 5604 bytes, PARSE OK).
  OI_DELTA_4STATE_BACKTEST_2026-09-21.md report.

Findings:
  Both schools near-identical on 6362 rows, 8-9 days. Max |mean| = 0.52 pct at 120m.
  Volume-delta school: aggressive_long 120m +0.3060, rekt_long 120m -0.0778.
  Price school: aggressive_long 120m +0.4572, rekt_long 120m -0.0830.
  aggressive_short positive at all horizons in both schools - contradicts spec.
  rekt_short near zero at all horizons in both schools - contradicts spec.
  se(day) 0.03-0.33. Most means within 1-2 se of zero. No state survives a significance bar.
  Day count 8-9. Hard cap.

Retracted:
  B059 "does not reproduce" - one cycle is not evidence.

Runtime at close: see NEXT_SESSION_HANDOFF.md.

## SESSION MTS-2026-09-21-1905Z - T033 + BACKTEST - CLOSED -
2026-09-21T21:35Z

Landed:
  T033 open_interest.delta_state (volume-delta school, nd1h input) L366. Helper L1375 with 8-line comment.
  T033 sibling open_interest.delta_state_price (price school, close delta over 60 1m bars) L373.
  Historical fallbacks L1164-1165 = neutral.
  backtest_oi_delta_4state.py new (136 lines, 5604 bytes, PARSE OK).
  OI_DELTA_4STATE_BACKTEST_2026-09-21.md report.

Findings:
  Both schools near-identical on 6362 rows, 8-9 days. Max |mean| = 0.52 pct at 120m.
  Volume-delta school: aggressive_long 120m +0.3060, rekt_long 120m -0.0778.
  Price school: aggressive_long 120m +0.4572, rekt_long 120m -0.0830.
  aggressive_short positive at all horizons in both schools - contradicts spec.
  rekt_short near zero at all horizons in both schools - contradicts spec.
  se(day) 0.03-0.33. Most means within 1-2 se of zero. No state survives a significance bar.
  Day count 8-9. Hard cap.

Retracted:
  B059 "does not reproduce" - one cycle is not evidence.

Runtime: loop left running per revised close rule.

## CLOSE NOTE 2026-09-21T21:33Z

Four close entries appear for this session (L998, 1022, 1046, 1070) because the close block ran twice. No deletes per rule. This line records the fact.
Loop restarted 21:30:21Z, wrapper 10456, java 2284, cycle 1 landed 21:31:17Z.
First live snapshot with both new fields: BTCUSDT_2026-09-22_1790026277952.json.
delta_state=rekt_short (volume-delta school), delta_state_price=rekt_long (price school). First observed disagreement between the two schools.
## SESSION MTS-2026-09-22-1215Z - LIVE MODE + FEED v1.1.3
2026-09-22T15:30Z

Landed:
  mts-watch.ps1 v1.1.2 (commit 0eef490): wrapper detection falls back to lock PID when the wrapper command line does not match.
  mts-watch.ps1 v1.1.3: MTS-OID block surfaces open_interest.delta_state + delta_state_price; wrapSrc token on MTS-PROC names lock vs cmdline detection.

Runtime at the time of this entry:
  Wrapper 9636, java 6996, supervisor 11348, sidecar 4544, mts-live v1.1.3 in its own window.
  Supervisor restarted wrapper at 14:02:39Z after old wrapper 1800 died (RESTART reason=wrapper_dead).

Section 9 satisfied: this live session added MTS-OID and wrapSrc to the feed.

Open:
  T034 spec gap: Phase 3 names net_longs, net_longs_new, net_shorts, net_shorts_new but defines no distinction between suffixed and unsuffixed. Parked pending definition.
  MTS-TAPE was stale 4699s; sidecar relaunched PID 4544 at 20:52 local.

## SESSION MTS-2026-09-22-1215Z - LIVE MODE + B063 + T039 + ITEMS CONVENTION
2026-09-22T17:30Z

Landed:
  mts-watch.ps1 v1.1.2 (0eef490): wrapper detection falls back to lock PID.
  mts-watch.ps1 v1.1.3 (c5e4979): MTS-OID block surfaces open_interest.delta_state and delta_state_price; wrapSrc token on MTS-PROC.
  Journal commit a97cebb - mid-session.
  B063 opened (98c8821) + fix shape (1849c2f): divergence handling fragmented; no dictionary definition, no condition-file rule, no verdict consumer.
  items/ convention established (a255c27): one item one doc. MyTradingSys/items/B063_divergence.md carries the verbatim operator ask and chronological updates. Register holds state + pointer.
  T039 registered HIGH (a255c27, corrected f9bdd06): functionality-doc sweep. Sources to fold: dsa_developer_implementation_tasks.md L365, compiled_output_audit_20260915.md L104, ALERT_REDESIGN_PROPOSAL.md L87, what_is_next.md Stage 3, INDICATOR_IMPLEMENTATION_HANDOFF.md Phase 3.
  MTS_DICTIONARY.md DIVERGENCE section added. Names the four detector implementations and states that none is authoritative.
  Two prior research files obsolete-marked: DIVERGENCE_AUDIT_AND_RESEARCH.md and GOLAS_CD_WEB_2026-09-21.md now point at items/B063_divergence.md.
  Runtime churn untracked (a255c27): klines cache, state_code_regime, supervisor_log now gitignored and removed from index.

Open at close:
  T034 spec gap. Definition locked this session: net_longs (standing, OI), net_longs_new (entering, CVD), net_shorts (standing, OI), net_shorts_new (entering, CVD). Output type (boolean vs strength vs both, backtest both) still pending operator answer.
  T039 not yet executed. Build-Check enforcement (every OPEN row has matching items/ file) is a stated plan, not written.
  B058, B059, B062 OPEN.
  Build-Check row count discrepancy: boot 62, now 63, expected 64 after two adds. Cause unknown. Not a parse failure.

Runtime at close:
  Wrapper 9636, java 6996, supervisor 11348, sidecar 4544, mts-live v1.1.3 running.
  Supervisor restarted wrapper 14:02:39Z after old 1800 died.


## CORRECTION 2026-09-22T18:15Z - commits not recorded in the 1215Z entry above

The 1215Z entry listed seven commits. Twelve landed that session. Five were not recorded here.
Times are IST (UTC+5:30). All five landed after this journal file was last written at 22:54:56 IST.

  c0d4669  22:58:11  T040 register tick-delta layer. Item doc + worker dispatch created.
  261a181  22:59:15  PROJECT_VISION add 2026-09-22 directive.
  d431b24  23:02:51  operator_reminders.md created.
  9d0a4bf  23:06:41  operator_reminders add machine section.
  0cfc96c  23:07:03  operator_reminders restore C1 line.

All five were made on this desktop, host JIS-NB. Same session, same author. No new work is implied beyond what those commits contain.

## SESSION MTS-2026-09-22-1737Z CLOSE - 2026-09-22T18:45Z

Landed:
  NEXT_SESSION_HANDOFF.md rebuilt (was stale by one session).
  SESSION_MANIFEST.json: operator_reminders.md added to boot_supplemental.
  session_log.json: two entries appended (91->93).
  DSA section 11 amended.
  T039 sweep: eight item docs created (B058, B059, B062, T034, T035, T037, T038, T039). 10 items total with B063 and T040.
  Build-Check enforcement: OPEN/IN-FIX/BLOCKED rows in BUGS.md need matching items/ file. Regex widened B-only to B-or-T. Row count 63->103. First run caught T038.
  Journal correction appended: five unrecorded commits from 1215Z logged.
  W1 dispatch file created at Dumps/workers/W1_divergence_audit/DISPATCH.md.
  Sidecar restarted (mts-tape live).
  PS7 7.6.6 installed side-by-side. Five spawn sites migrated to pwsh. COMMANDS.md updated. All scripts parse. WinForms, mvn, pytest confirmed OK in pwsh.
  Build-Check scan widened to runtime/*.md.

Not done:
  PS7 Part 2 (loop restart under pwsh). Default: next natural restart picks it up.

Runtime at close:
  Wrapper 9636, java 6996, supervisor 11348. Sidecar restarted.

## SESSION MTS-2026-09-22-1737Z FINAL CLOSE - 2026-09-22T19:00Z

Continued after cd3dd79 close. Work landed in continuation:
  Protocol rules relabeled R1-R5 (were W1-W5) in live_session_protocol.md, T040 dispatch, B063 item, MTS_PLAYBOOK, operator_reminders, PENDING_BACKTEST_AUDIT. No rule label uses W; folder names keep W# prefix.
  Six worker dispatches ready: W1_divergence_audit, W2_institutional_definitions, W3_cross_indicator_relationships, W4_btc_tuning_consensus, W5_backtest_design, T040_tick_delta. All carry R1-R5 inline, PATHS AND COMMANDS, EVIDENCE ALREADY PROVIDED, output spec.
  T041 registered (HIGH, OPEN). Engine verdict has no multi-hour timeframe awareness; 7h leg on 1h klines never read. Also structure.1h.stale=true while 1h klines fresh on disk. Item doc + worker dispatch + BUGS row.
  T041 dispatch: Dumps/workers/T041_verdict_timeframe_audit/DISPATCH.md (62 lines). Part A audit (disk), Part B research (web), Part C verdict.
  Journal mojibake on line 600 fixed (Cyrillic mangle of em dash). Build-Check scan widened to runtime/*.md so this file is covered.
  Build-Check enforcement confirms each OPEN row has items/ file. 104 rows.

Zero worker replies received. All dispatches are ready-to-send; the send is a coordinator step (paste into fresh chat, save reply).

Runtime at close: wrapper 9636, java 6996, supervisor 11348. Loop still 5.1; next natural restart spawns pwsh.

Note: this is the second close for MTS-2026-09-22-1737Z. First close cd3dd79 was premature; work continued. Recorded for ledger honesty.

## POST-CLOSE NOTE 2026-09-23T01:30Z

Operator chart read + web cross-check on current BTCUSDT tape. Logged to items/T041_verdict_timeframe_gap.md as evidence.
Key facts: short covering confirmed (648M USD short liquidations, volume/OI ratio ~2, funding neutral). Options expiry pin Sept 25 at 85K/88K.
Anchor mismatch warning restated: chart CVD (CoinGlass leftmost bar) vs system CVD (session 00:00 UTC) not comparable.
Schema gap observed: no 30m/4h/daily/weekly structure in snapshot. No OI/CVD peak reference. 1h structure stale while 1h klines fresh.
No engine change. T041 evidence only.
Candidate T042 (schema gap) noted for next session. Not yet registered.

## POST-CLOSE NOTE 2026-09-23T01:30Z

Operator chart read + web cross-check on current BTCUSDT tape. Logged to items/T041_verdict_timeframe_gap.md as evidence.
Key facts: short covering confirmed (648M USD short liquidations, volume/OI ratio ~2, funding neutral). Options expiry pin Sept 25 at 85K/88K.
Anchor mismatch warning restated: chart CVD (CoinGlass leftmost bar) vs system CVD (session 00:00 UTC) not comparable.
Schema gap observed: no 30m/4h/daily/weekly structure in snapshot. No OI/CVD peak reference. 1h structure stale while 1h klines fresh.
No engine change. T041 evidence only.
Candidate T042 (schema gap) noted for next session. Not yet registered.

## SESSION MTS-2026-09-23-0430Z CLOSE - 2026-09-23T05:52Z

Landed:
  Loop restarted under pwsh (first time; PS7 Part 2 closed). Supervisor 3184 + wrapper 2736, then wrapper 11988 after supervisor restart.
  T042 candidate noted; not registered.
  Seven worker dispatches sent this session: W1, W2, W3 replied. W4-W5, T040, T041 still pending send.
  Worker folder convention adopted: parent-prefix naming (B063-W1-divergence-audit etc). README index at Dumps/workers/README.md. Archive at Dumps/workers/_archive/.
  Research-gate fix applied to W2/W3/W4/T041 dispatches (playbook Part I three steps inlined).
  W1 result: only tape-watch.ps1 fires. divergence_monitor.py dead (scripts/tools/, never invoked). SetupScreener.cvdDivergence dead parameter (no producer, no caller). mtf_flow inert.
  W2 result: RSI T2, MACD T1, OBV T1. CVD no validated T1/T2 evidence. Volume profile and OI corrected T1->T2 at storage.
  W3 result: no T1/T2 cross-indicator matrix. Best-effort T3 matrix stored.

Not done:
  W4, W5, T040, T041 dispatches not sent.
  T042 not registered (schema gap: no 4h/daily/weekly structure).
  B064 filed (supervisor does not honor supervisor_stop.flag).

Runtime at close: loop stopped by operator request (powering off). No procs. No locks. Direct kill of supervisor 3184 required.

## SESSION MTS-2026-09-23-0831Z CLOSE - 2026-09-23T11:35Z

Landed:
  B064 CLOSED. Not reproducible. Controlled test: supervisor 16480 wrote flag at 10:34:10Z, exited within one cycle. Check already present at loop-supervisor.ps1 L71.
  T041 CLOSED. Reframed: no HTF direction layer exists or was claimed. Worker rounds 1-3 established engine was fading the leg, not missing it. HTF principle remains [PRINCIPLE - NOT ALGORITHM] in compiled_engine.md.
  B065 filed. structure.{tf}.stale computed at MarketDataSnapshot.java L719-722, propagated by mts_math.py L321-327, no consumer in extractZones or getSwingTF.
  T042 filed. Snapshot schema lacks 4h/daily/weekly structure and OI/CVD peak reference.
  T043 filed. Source-to-code traceability mechanism absent. Prior audits (2026-08-30, 2026-09-19) found the same gap; no gate followed.
  T043 Phase 1 done: compiled_engine is merge point, not generated artifact.
  T043 Phase 2 done: 13 SYSTEM, 73 PRINCIPLE, 2 VISUAL FLAG, 9 hard stops.
  Four worker dispatches replied and stored: B063-W4, B063-W5, T040-W1, T041-W1 (3 rounds). README rows flipped.
  Tom corpus scan: HTF terms near-zero. Auction vocabulary dominant.
  Parked research: PARKED_2026-09-23_T041_TREND_RESEARCH.md.
  Apparatus fix: PowerShell escaping rule appended.

Not done:
  T043 Phase 3 (hard stops slice audit). B058 part D. B059. B062. T039 expiry 2026-10-06.
  T041 Part B web research (dropped; design question closed by A+C evidence).
  Cross-check noted: EXTRACTION_TO_ALERT_AUDIT_2026-09-19 claims 19 CT ids in compiled_engine L772-849. This session counted 0. Discrepancy for next session.

Runtime at close: loop ALIVE. Supervisor 11680, wrapper 4468, java 10388, both locks fresh.

## SESSION MTS-2026-09-23-1236Z CLOSE - 2026-09-23T12:55Z

Landed:
  Architecture doctrine locked in MyTradingSys/PROJECT_VISION.md.
  Verbatim blocks preserved: 2026-09-15 directive, 2026-09-22 directive,
  operator statement 2026-09-23 (Tom is core), four gap classes 2026-09-23.
  PROJECT_VISION.md: 92 -> 155 lines, sha E4A55CF2 -> 9459DC50.
  Two worker types defined in DSA_SESSION_PROMPT.md (section 1) and in
  live_session_protocol.md (new section WORKER TYPES, rules I1-I8).
  DSA: 231 -> 238 lines, sha 3B93B8C8 -> after section 11 update (see hash
  in receipt). Protocol: 226 -> 259 lines.
  Hard stops slice audit (T043 Phase 3): 9 rules mapped to impl site.
  3 fully wired, 2 label-principle, 2 wired indirectly, 2 gaps.
  CT-id reconciliation: 19 ids confirmed at compiled_engine L790-819.
  Prior session count of 0 was wrong.
  Six Independent Worker dispatch stubs written under Dumps/workers/
  RUN-2026-09-23-<LAYER>/dispatch.md: RSI, PROB, ANALYST, SESSION, TICK,
  ASSIST.

Not done:
  compiled_engine.md retag of CT/SCREENER to module candidate (deferred).
  MTS_DICTIONARY [VISUAL FLAG] + [CORE]/[MODULE] families not yet added.
  T043 Phase 3 gap #3 not filed as BUGS row.

Runtime at close: loop ALIVE. Supervisor 11680, wrapper 4468, java 10388.
## SESSION MTS-2026-09-23-1236Z - operator_reminders.md update - 2026-09-23T13:35Z

Landed:
  operator_reminders.md (boot-loaded): 173 -> 242 lines, sha 8EA92693 -> 4A5D91C0.
  Header range fixed A-E -> A-G.
  B1: added regex-vs-Split verbatim-check line.
  B2: added "verify by other method than the one used to write".
  B7: added "new file vs amend - prefer amending" line.
  D2: rewritten for two worker types (Dependent R1-R5, Independent I1-I8).
  New section G: HANDOFF FOR NEXT SESSION (G1-G6), printed as one fenced
  code block, mandatory DO-NOT-MISS, shape template, section-11 regen rule.
## SESSION MTS-2026-09-23-1730Z CLOSE - 2026-09-24T01:45Z

Loop stopped by operator request. stop-day.ps1 clean exit at 19:43:11 UTC (apparatus_log).
Supervisor 11680 killed directly (B064: stop flag not honored).
stale supervisor.lock removed.

Landed: DSA sec 1 Independent removed; protocol rule 15 dedup + rule 16 added; Build-Check
label Cyrillic scope; apparatus_fixes mojibake row; B058 closed; B062 closed (position-aware
alert gating); B065 closed (stale-swing rejection in extractZones + stop selection);
T039 closed (enforcement already on disk); T042 producer landed (structure.1w/1d/4h);
T043 WONTFIX; B059 reverted to producer-side fix; timestamp ISO fix at start-trading-day.ps1
L130; NEXT_SESSION_HANDOFF rewritten with T042 wiring gap note.

Not done: T042 wiring (new keys emitted, no consumer). B059 producer-side freeze.
B063 operator decision. Open queue: B059, B063, T034, T035, T037, T038, T040, T042, T044, T045, T046.

Runtime at close: loop stopped clean. No java. No wrapper. Supervisor killed. supervisor.lock removed.
## SESSION MTS-2026-09-23-1730Z - ADDENDUM 2 (loop hardening) - 2026-09-24T06:26Z

After the initial close, this session continued with loop diagnostics and hardening.
Root cause of repeated SNAPSHOT_FAIL: pwsh 7 spawned via Start-Process from an IDE
terminal inherits a PATH missing system32 and Maven bin. Invoke-WithTimeout with
UseShellExecute=false resolves bare names via PATH only.

Landed:
  8960218  PATH prepend at start-trading-day.ps1 top (system32 + Maven bin);
           absolute cmd.exe/taskkill.exe in Invoke-WithTimeout; warmup+cycle +5s
  e3d028f  mojibake fix on start-trading-day.ps1 (14 -> 0 non-ASCII). Handoff-1445Z
           claim of mojibake was correct. Earlier session claim of clean UTF-8
           was wrong; bytes were D0 B2 D0 82 E2 80 9D at two sites.
  bc70456  load.ps1: mts-up polls lock acquisition up to 30s (not fixed 3s)
  f7c16ef  mode.ps1 Gap 6 lock validation + 7b orphan sweep extension;
           start-session.ps1 supervisor heartbeat age in loop health

Deferred to next session: single stop flag, stale detection with kill-tree +
debounce + circuit breaker, loop_state.json, mts-loop CLI.

Claude architecture review decided: kill-only on stale (not restart-on-stale);
PID-alive detection for state-machine death; state_code.json mtime for hang with
150-180s threshold.

Loop at close: ALIVE. Supervisor 15896, wrapper 10872, state-machine 2672,
cmd 4476, java 13260. Snapshot age 0.8 min. Loop is still running pre-fix code;
mode.ps1 changes take effect on next mts-up start.

## SESSION MTS-2026-09-24-0639Z - loop-supervisor hardening - 2026-09-24T06:58Z

Claude-scope steps 2-4 landed in one pass.

Landed:
  loop-supervisor.ps1 rewritten 136 -> 235 lines sha256 F60B265D.
    Single stop flag: runtime_data\loop_stop.flag, honored by wrapper, supervisor,
    and stop-day.ps1. supervisor_stop.flag retired.
    Stale detection: snapshot OR state_code.json mtime >150s for 2
    consecutive ticks -> taskkill /F /T on wrapper tree, restart.
    Circuit breaker: 5 restarts / 15 min -> refuse restart, log breaker.
    loop_state.json written every tick with action, reason, pids, ages,
    strikes, restart count.
    Java PID detected via command line match.
  stop-day.ps1 sha256 C2F414BF -> BA246AFA. Waits on both apparatus.lock
    AND supervisor.lock so stop returns only after supervisor exits.
  load.ps1 L64-76: mts-loop start|stop|status dispatcher.
  scripts\start-session.ps1 L108: chat-title line removed.

Supervisor restart: old PID 15896 killed directly. New PID 13368 launched.
Wrapper 10872 and java 13260 untouched. First loop_state.json write
06:56:33Z: action=ok, snapAge=20s, scAge=17s, strikes=0.

Not done: B059 producer freeze. B063 operator decision. T042 wiring.

Runtime at close: loop ALIVE. Supervisor 13368, wrapper 10872,
state-machine 2672, java 13260.
## SESSION MTS-2026-09-24-0639Z - B059 fix - 2026-09-24T07:11Z

B059 deep-dived and fixed. Prior framing (window drift, fix in
buildStructure) was wrong on both counts. Corrected from disk:
  - Anchor MarketDataSnapshot.java L75-77 stable within a UTC day.
  - Drift mechanism: bin edges at L501-514 anchored to window min/max.
  - Pf_vp built at L144 and L1066, not in buildStructure.

Fix: new overload buildVp(bars, hvns, fixedBinSize). fixedBinSize=10.0
for post_funding. Bin edges snap to floor(minP/10)*10 grid. Other VPs
unchanged (call sites pass 0.0 via the 2-arg wrapper, so grid mode is
off by default).

sha256 74B14A74 -> 52FF88CF. CRLF preserved (1468), LF-only 0,
BOM NO. Build-Check PASS 2026-09-24T07:10Z.

Not fixed: rank-1 zone distance gate. B059 evidence also cited a
150-pt gap between rank-1 pf_vah and price. Separate defect. File
as own row next session.

Running java 13260 is old bytecode. Fix takes effect on next loop
start. Not restarting without operator call.
## SESSION MTS-2026-09-24-0639Z CLOSE - 2026-09-24T10:00Z

Landed:
  loop-supervisor.ps1 sha256 5CC593B1, 250 lines. Added java-dead
  detection (smPid from statemachine command-line match). Dead ->
  kill_restart on wrapper tree. Prior check missed because snapshot
  writer is a separate transient java.
  Build-Check: items/INDEX.md mechanical check (open-status only).
  B066 filed: rank-1 distance gate (split from B059).
  B066 item doc + INDEX.md row.
  T040 item doc updated with operator-refined scope.
  Bug dedup: B066 inserted twice via anchor collision. Fixed.

Commits: 9c841f9, 64a6c3a, 0731348, 65694bc, 9be0b09, f093596,
  b205d1c, 6ca60b7.

Runtime at close: loop ALIVE. Supervisor 6552, wrapper 10872,
  state-machine 2672/4476, java 13260. Build PASS 2026-09-24T10:00Z.
  java 13260 still pre-B059 bytecode.

## SESSION MTS-2026-09-24-1100Z - post_funding_vp demoted - 2026-09-24T13:26Z

Scope: isolate crypto-hack module from Tom-sourced core.

Landed:
  SetupCandidatesBuilder.java L129/L136/L143: pf poc/vah/val removed from
  target list. L316-318: pf poc/vah/val removed from candidate zone list,
  replaced with demotion comment. Module now display-only.
  sha256 9137C219 -> 9B058AED, LF preserved, 846 -> 842 lines.
  math_object_builder.py vp_map and target pool: post_funding_vp removed.
  sha256 28659A91 -> BF2E7FE2, CRLF preserved (415), Build-Check PASS
  2026-09-24T13:26:04Z.
  test_math_object_builder.py::test_v120_4h_and_pf_vp_present inverted to
  assert post_funding_vp_poc NOT in zones. CRLF preserved. 130/130 pass.
  B067 filed: systematic audit of remaining crypto hacks for gating.

Rationale: PROJECT_VISION.md doctrine says modules never gate core.
  crypto_adaptations.md labels funding-reset window as hack #6, UNVALIDATED,
  Tom never mentions. post_funding_vp was producing 781 of 8200 rank-1
  verdict lines. Module still emitted in snapshot, visible in feed,
  still shown as POST_FUNDING in current_market_state.md. Cannot drive
  tier, stop, target, or rank-1 any more.

Also landed this session:
  Folder flatten MyTradingSys/mts/* -> MyTradingSys/*.
  data/ -> runtime_data/. MyTradingSys/data/ -> MyTradingSys/market_data/.
  Three extracts folders consolidated to extracts/.
  197 files rewritten for new paths. Java StateCodeEmitter L446+L477 fixed.
  start-trading-day.ps1 L53 $LogDir fixed. 5 Python files path-fixed.
  PROJECT_VISION.md added to SESSION_MANIFEST.json boot_files.
  USER.md: two rules added (close items on decision; label sub-item context).
  T045 closed. T046 d5 mapping confirmed.

Open:
  B059 bin size 10.0 tagged SCREENER pending sensitivity replay.
  B067 crypto-hack gating audit. UTC 00:00 CVD anchor is candidate next.
  Sensitive: no old-vs-new grid replay run yet.

Loop ALIVE post-restart. Log writes to runtime_data/.
Build PASS 2026-09-24T13:26:04Z.
