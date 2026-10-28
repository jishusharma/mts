- 2026-09-29 01:55 | running 100-fabio-0ky-a, waiting 20 | NEW: 092-096 PASS+committed (092 d7e64a8, 093 004ed8e, 094 af3df38, 095 19448b3, 096 d5d9b93); 097/098 DONE audit PASS; 099 PARTIAL out-of-scope extract not written
  run_all_tests --quick: Step 5b layer tests FAIL (turn_of_candle .new unpromoted, unrelated) | head 9e34bf0
- 2026-09-29 02:48 | running 103-fabio-8cwk, waiting 17 | PASS 091,0985,0986,0987; HOLD 0988 (cutoff, repack), 101 (waits on 100 BLOCKED), 102 (GPS/scope, repack) | head 90b8729
  note: promoted .new copies left in place (gitignored); fabio_escalation.py.new has a test but no task id, not gated
2026-09-29 03:45 | running 106-fabio-faw-c, waiting 14 | HOLD 103 (9 bad quotes), 104 (BLOCKED cutoff), 105 (10 bad quotes; Haiku wrote unscoped file extracts/processed/fabio_valentini/FawPrRUGNpk/extract_FawPrRUGNpk_2of3.md, uncommitted - supervisor review) | head 90b8729
supervisor-worker 2026-09-29 04:50 | Task A: 103 PASS commit 10759e8 (GPS retag 6 tags). Task B: 082 verdict OUTPUT_TOKENS insufficient, repacked 085 with 15000. Task C: 105 HOLD reason "Stucky Grill" quote missing from FawPrRUGNpk raw transcript.
- 2026-09-29 04:49 | running 108-fabio-lqv-b (heartbeat 26m), waiting 4 | PASS 0989 turn_of_candle 5392309 (Haiku changed event-detection logic + 29 edge tests; supervisor should review vs FORMULAS 16); HOLD 106 (out-of-scope proposal); BLOCKED 107 (GPS line missing)
  testnet: 3 runners up; turn_of_candle NOT wired (FORMULAS 16: direction not stated, needs supervisor side choice); since 22:15Z 13 signal_rejected (top: stale 75621s x2, rsi failure unmapped), smoke attempt entered=1 | head 5392309
- 2026-09-29 05:50 | running 110-fabio-fzl, waiting 1 | HOLD 108 (out-of-scope proposal), 109 (no FILE block; inline quotes 5 NO-TRANSCRIPT); 085 already promoted; no agent spawned | head 5392309
  testnet: 3 runners up, no HALT; since 23:19Z 6 signal_rejected (tom 3, rsi 15m 1, rsi 1h 2; top: verdict WAIT_RR x2), 0 trade_attempt
- 2026-09-29 06:45 | queue idle, waiting 0 -> backfill packed audits 900-902 | HOLD 110 (out-of-scope proposal), 111 (DONE but no FILE block; 8 quotes NO-TRANSCRIPT); Haiku gate | head 5392309
  testnet: 3 runners up, no HALT; since 00:20Z session_momentum 15m long entry_failed (PREFLIGHT R8: instrument has position/open orders - leftover smoke position?); signal_rejected tom 3, rsi 3 (top: WAIT_RR x2, unmapped rsi:failure x2)
- 2026-09-29 07:44 | queue idle, waiting 0 -> backfill packed audits 903-905; 900 BLOCKED (cut off at 1536 tok), 901/902 PASS | HOLD formula_audit.py.new (no test/spec); no agent spawned | head 2b8b19a
  testnet: 3 runners up, no HALT; since 01:15Z rsi 15m 1 entered; signal_rejected rsi 1h 4, rsi 15m 1, tom 1 (top: unmapped rsi:failure, WAIT_RR, stale 298842 s)
- 2026-09-29 08:43 | queue idle, waiting 0 -> backfill packed audits 906-908; 903/904/905 PASS | no NEW builds (all .new are gated leftovers or held); no agent | head 2b8b19a
  testnet: 3 runners up, no HALT; since 02:14Z rsi 15m skipped_busy 2; signal_rejected rsi 1h 3, rsi 15m 1, malkan 1h 1, tom 1 (top: unmapped rsi:failure, WAIT_RR, stale)
- 2026-09-29 09:43 | queue idle, waiting 0 -> backfill packed 909, 911 (910 REFUSED: PROJECT_VISION critical, needs operator OVERRIDE); 906/907/908 PASS | no NEW builds; no agent | head 2b8b19a
  testnet: 3 runners up, no HALT; since 03:13Z no trade_attempt; rsi 15m skipped_busy 1; signal_rejected rsi 15m 13, rsi 1h 1, tom 2 (top: stale 63-75k s; unmapped rsi:failure 3; tom WATCH/WAIT_TRIGGER)
- 2026-09-29 10:43 | queue idle, waiting 0 -> backfill packed 913 (A7 kill-switch), 914 (A1 bt-stats sharpe); A6-project-vision-layers FAILED to pack; 909/911 PASS | no NEW builds; no agent | head 0825ed9
  testnet: 3 runners up, no HALT; since 04:13Z no trade_attempt; fabio cvd_absorption 1h skipped_busy 1; signal_rejected rsi 15m 5, rsi 1h 1, tom 4 (top: stale 6; tom WAIT_RR 3, WAIT_TRIGGER 1)
- 2026-09-29 11:43 | running 122-orphan-watchdog-core, waiting 6 | no promotable builds: 121-pm-heartbeat BLOCKED (bad file name, repack), 914 bt_stats proposal deletes 94 lines -> discard, 913/916 audits DONE, 917 BLOCKED; no agent | head 08b75b1
  testnet: 3 runners up, no HALT; since 05:13Z no trade_attempt; signal_rejected tom 2, rsi 15m 2 (top: tom WAIT_RR 2; unmapped rsi:failure 1; stale 1)
- 2026-09-29 12:43 | running 922-audit-a2-live-layers, waiting 4 | no NEW builds (129 BLOCKED; mainnet_pnl.py.new identical to committed live, stale); no agent | head a4d82d6
  testnet: 3 runners up, no HALT; since 06:13Z no trade_attempt; signal_rejected rsi 15m 4 (top: stale 71-72k s; unmapped rsi:failure 1)
- 2026-09-29 13:44 | running 925-audit-a2-live-runner-cli, waiting 1 | no NEW builds (140 gpt-oss BLOCKED cut-off; 141 gpt-oss bake-off proposal, not for promotion; mainnet modules already in d115b0d/924d7a0; bt_stats.py.new stale subset); no agent | head 6c24f0b
  testnet: 3 runners up, no HALT; since 07:13Z no trade_attempt; skipped_busy rsi:malkan_bear:1h 1, cryptocred:fib_pullback:1h 1; no signal_rejected
- 2026-09-29 14:43 | running 150-journal-env-q36, waiting 3 | no NEW builds (925-937 audits all PASS, 0 proposals; 141 gpt-oss bake-off not for promotion); no agent | head 6c24f0b
  testnet: 3 runners up but HALT + HALT_DAILY_LOSS present (day over, nothing started/stopped); last hour: rsi_events:15m trade_closed 1, auto_trader start 2, no trade_attempt/signal_rejected
- 2026-09-29 15:44 | queue idle, waiting 0 -> backfill packed 946/947 audits (A6-project-vision-layers pack FAILED) | no NEW builds (150-152 BLOCKED, 153 PARTIAL: q36 bake-off of already-committed modules, not for promotion); no agent | head 26d154f
  testnet: no HALT; auto_trader was down -> restarted (pid 23168); since 09:13Z tom signal_rejected 1 (verdict WAIT_RR), no trade_attempt
- 2026-09-29 16:43 | queue idle, waiting 0 -> backfill packed 961 (A5 trade-costs), 962 (A2 malkan-40-60); A6-project-vision-layers pack FAILED | no NEW builds (946-959 audits PASS, 0 proposals; 955 BLOCKED cut-off at 1536 tokens; .new.new files are bake-off copies, not for promotion); no agent | head b6d0da8
  testnet: 3 runners up, no HALT; since 10:13Z no trade_attempt; tom signal_rejected 1 (verdict WAIT_RR)
- 2026-09-29 17:42 | running 979-audit-a2-rsi-ma-events, waiting 1 | no NEW builds (970-978 audits PASS, 0 proposals; bt_stats.py.new is stale, 94 lines shorter than live, not promoted); no agent | head e6a5105
  testnet: 3 runners up, no HALT; no auto_trades events since 10:49Z (last: tom signal_rejected WAIT_RR)
- 2026-09-29 18:44 | running 121-paste-size-guard (hb 16 min), waiting 2 | NEW: bt_stats.py.new HOLD (6-line stub, only sharpe; test ImportError wilson); 979-984 audits PASS, 0 proposals | head e8fec95
  testnet: 3 runners up, no HALT; auto_trader restarted 12:57Z+13:01Z; no trade_attempt/signal events since 10:49Z (tom WAIT_RR)
- 2026-09-29 19:42 | running 994-audit-a2-tick-extremes, waiting 4 | no NEW builds (985-992 audits PASS, 0 proposals; 121 BLOCKED; no .new files touched in 2h); no agent | head 384282b
  testnet: 3 runners up, no HALT; no auto_trades events since 13:01Z start (last signal tom WAIT_RR 10:49Z)
- 2026-09-29 20:42 | running 1000-audit-a7-auto-trader, waiting 2 | no NEW builds (1000-a1/a2/a5, 910-a6, 994-998 audits PASS, 0 proposals; no .new touched in 2h); no agent | head 76876ee
  testnet: 3 runners up, no HALT; since 14:12Z: rsi_events:15m short ENTERED (S-mkt-0929-1501), turn_of_candle 2x signal_rejected 'unmapped toc_m14 (add a layer_rules entry)'
- 2026-09-29 21:42 | running 1000-audit-a7-journal, waiting 0 | no NEW builds (a7 deribit-orders/deribit-read/executor audits PASS, 0 proposals; deribit-client PARTIAL); no agent | head 3a4d4d2
  testnet: 3 runners up, no HALT; since 15:12Z: rsi_events:15m trade_closed 1 (+ledger row), turn_of_candle 4x signal_rejected 'unmapped toc_m14 (add a layer_rules entry)'
2026-09-29 22:42 queue 0 waiting/0 running; no NEW tasks (all in GATE_REPORT); ran audit_rotation --backfill (packed audits); watchdog: 3/3 running, no HALT; scoreboard skipped. head 863bae6 Manager survives transient net errors; auto_trader frees slot only when exchange is flat
- 2026-09-29 23:42 | queue 0 waiting/0 running (5 audit replies unverified, no NEW builds); ran audit_rotation --backfill (packed a2-live-runner-cli) | head 863bae6
  testnet: 3 runners up, no HALT; since 15:00Z: rsi_events:15m 1 entered/1 closed, turn_of_candle 13x signal_rejected 'unmapped toc_m14 (add a layer_rules entry)'
2026-09-30 01:42 queue 0 waiting/0 running; QUEUE IDLE - NUC cooling (backfill paused); no NEW verdicts; head b998cd3. Watchdog 3/3 up. Last hr: 4 signal_rejected turn_of_candle (unmapped toc_m14, needs layer_rules), 1 tom skipped_auto_pause.
2026-09-30T02:38 | dsa-feeder | worker idle | gated 2 (998 PASS, 997 ping PARTIAL) | packed 999-tom-rulebook-merge
2026-09-30 02:42 queue 0 waiting/0 running; QUEUE IDLE - NUC cooling (backfill paused); no NEW verdicts; head ca073ba. Watchdog 3/3 up, no HALT. Last ~hr: turn_of_candle 3 entered/3 closed/1 signal_rejected, rsi 15m 1 closed.
