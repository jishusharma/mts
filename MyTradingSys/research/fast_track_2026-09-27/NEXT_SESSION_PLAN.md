# Next session plan - Opus supervisor, auto mode (written 2026-09-28 ~14:30Z by supervisor session 2)

Start: "Supervisor: read NEXT_SESSION_PLAN.md". Read this file + STATUS.md only (SUPERVISOR_LOG.md = history).
Goal: finish the testnet live-readiness gate, then the Fabio backtest. Never mainnet.

## 0. First 3 minutes (T0)
1. `python scripts/dev/make_status.py` -> read STATUS.md. `git log --oneline -15`.
2. `python scripts/worker/queue_tool.py status`; `ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 status`
   (+ `logs 10`). Expect 082 done and 083 packed or not (see 3.W2).
3. Ask the operator for the R3 testnet output if it hasn't been pasted yet.

## 1. Operator decisions already made (session 2) - do NOT re-ask
- Live testing = BOTH: Tom core testnet order runs + indicator-layer ALERTS (alert-only, never orders/filters).
- Core ATR stays a plain SMA of TR (documented in FORMULAS.md section 12).
- L6 part 2 deferred for testnet (build before mainnet). OPEN_FINDINGS.md: that is the only open item.
- R1 order-math: side-aware rounding approved and promoted (see 2).
- Still OPEN for the operator: the Tom-vs-Fabio override ruling (SESSION_4_HANDOFF item 4: proof/absorption/FVG only was
  recommended); 1-2 named professionals whose params seed the params files.

## 2. Readiness gate R1-R6
| # | State | Evidence |
|---|---|---|
| R1 exec math tests | DONE | 08f5ea0 + 61e55f3 (T4 reviewed): FORMULAS.md s11; snap_price(price, mode) Decimal floor/ceil (entry never worse, stop/target toward entry); round_size floors and rejects <10 USD; harmonic ladder avg; tests plan_compiler 20, executor_math 2, risk_guard 13 (mutant R3 killed); Java NET_RR_FRICTION + NetRRConstantTest 6 |
| R2 full gate | DONE | run_all_tests.py (Maven + backtest) ALL PASS after R1 |
| R3 testnet re-run | DONE 15:10Z (base 6/6, G1/G2 4/4, FT-2 4/4) - was OPERATOR | `python MyTradingSys/execution/testnet/run_testnet_suite_ft2.py` -> expect base 6/6, G1/G2 4/4, FT-2 4/4 (T-c may fail on zero fees - see FT2_RUNBOOK). Plans checked compatible with the new rounding. Haiku reads the output; if green, log it and mark R3 done |
| R4 L6 | DONE | re-arm in; part 2 deferred |
| R5 layers | NEARLY | promoted: 070-075, 077 (f0b44fe), 078 13558c0, 079 ae30eda, 080 alert emitter 4f7204e (JSONL only; boundary test 84de108), 081 8ea2f68. OPEN: formula audit 082/083 |
| R6 backtest baseline | DONE | BACKTEST_L1_REPORT.md (3e99093, c509f3c): only 1h RSI-40 support tol 0.5 has PBO 0.03, and its edge (+0.043% h5) is < fees. CryptoCred: no edge. setup2 bug fixed 54ad393 |
When R3 is green: Tom testnet order runs are READY. Layer alerts on testnet need a runner that wires bar_closed -> 080 emitter
(not built yet - next NUC spec, see 3.W3).

## 3. Work queue (cheapest tier first; agents return <=15 lines; spot-check one claim each)
OPERATOR (2026-09-28): "keep using Qwen for whatever tasks you can". Default every IMPLEMENTATION to a NUC spec
(<= ~5k prompt tokens, one module each). Claude agents only write specs + hand-computed tests, verify, promote, run
backtests. For W4 below: 3 Qwen specs (087 fabio_cvd_absorption, 088 fabio_escalation, 089 fabio_volume_fvg), each
with its hand-computed test plan inside the spec; then a Sonnet agent verifies, promotes and runs the backtest/report.
Keep the NUC queue non-empty: when it has < 2 waiting, write the next specs first.
- W1 Haiku "R3 receipts": read the operator's pasted testnet output, compare it against the expected lines, append to SUPERVISOR_LOG.
- W2 Sonnet "audit": when 082-formula-audit-a lands: verify it (full slug), promote by RENAME, run formula_audit.py, report
  its table. 083-formula-audit-b spec is written (Dumps/workers/NUC-QUEUE/specs/083-*.md) but must be packed AFTER 082 is
  verified (its SCOPE = 082's output). Session 2's auto-pack poller was stopped - pack 083 by hand:
  `queue_tool.py pack 083-formula-audit-b`. Then the audit covers FORMULAS s11/s12 (execution math, ATR) -> spec 084.
- W3 Sonnet "feed NUC" (specs <= ~4-7k prompt tokens: 4-7 min each; 15k timed out at 7200 s):
  084 formula-audit s11-12; 085 live alert runner (poll closed bars per tf -> layers -> 080 emitter -> JSONL; testnet
  alerts only, no execution import); 086 tighten test_layer_boundaries to also catch bare-name imports (sys.path style).
- W4 Sonnet "Fabio backtest" - RE-LAUNCH (session 2 stopped it before it wrote any files). The brief is in SUPERVISOR_LOG
  session 2 "Fabio" entry. Summary: source = extracts/_staged_2026-09-27/extracts/fabio_valentini/extracts/extract_o-w5Gxss6T0.md
  (FAB-001..009, video "3 Order-flow Trading Tricks"). Testable on 1m klines (taker_buy_volume -> exact 1m CVD):
  FAB-007/008 CVD absorption (CVD lower low, price holds the prior swing low within tol -> long), FAB-002/003 escalation
  breakout (record volume W + delta/vol >= k at a defended level -> breakout), FAB-005/006 volume FVG (lowest-volume bin
  inside the 70% VA of the swing-leg profile; control = random VA bins). All thresholds are UNDEFINED in the video -> grids,
  70/30 IS/OOS, PBO, vs 0.10% fees. Fabio = a SEPARATE layer (layers/fabio/); the Tom comparison is descriptive only
  (Tom setups with vs without an agreeing Fabio signal), and only if Tom setups are reproducible in Python - else say so.
  Output FABIO_L1_REPORT.md. The operator's question: "is core MTS + Fabio producing quality setups?"
- W5 Haiku "cleanup" (ASK the operator first - deletion): the 13 byte-identical .new leftovers of 070-075 (after 082/083 are
  verified), move backup_session/ (139 MB) out of the repo, archive superseded handoffs. Audit: clutter medium-high.
- Later: trace 2 Tom rules extract -> definition -> code (the audit skipped it); worker v3 (streaming .partial.txt output,
  num_thread 6, `queue_tool.py perf`; deploy only when the queue is idle); verify the 2023-11-10 1m-vs-1d volume outlier (12%).

## 4. Gotchas learned in session 2 (also in SUPERVISOR_LOG)
- "Gate green" is only real if the new test module is IN run_all_tests.py's step lists - ask agents for per-module counts.
- An agent's staged test file can silently REPLACE an existing tracked test file - diff test counts before promoting.
- Agents promoted by copy -> byte-identical .new leftovers; instruct "promote by RENAME".
- queue_tool verify needs the full slug (070-tf-resample), not the bare number.
- Worker heartbeat stays stale while Ollama generates (stream=false); a stale heartbeat != dead. RequestTimeoutSec=7200.
- scripts/dev/run_all_tests.py working tree has UNCOMMITTED Step 3b/3c guide-checker lines from another session
  (check_guide.py untracked) - leave them; commit only your own lines (build the index blob from HEAD).
- Windows Python can't see bash /tmp - use the scratchpad path.
- NUC: two worker processes reported (pid 4084, 10368) - operator to check via RDP
  (Get-CimInstance Win32_Process powershell CommandLine). OLLAMA_FLASH_ATTENTION / KV_CACHE_TYPE q8_0 / power plan:
  operator via RDP, apply between tasks.

## 5. Auto-mode rules (unchanged)
Allowed: agents, gates, commits on fast-track, queue pack/verify, ssh gate read commands.
Ask first: promoting execution code (after T4), any testnet run that places orders, `restart-worker confirm` mid-task, deleting.
Never mainnet, never read .secrets/.env/keys, never push/merge/rebase/reset.

## 6. Session 2 close-out (~15:45Z) - read this first
- R3 DONE on testnet (e2f5497). Tom testnet order runs READY (mts plan -> mts check -> mts guard -> mts trade).
- Market loop STARTED 15:31Z (mts start; armed, alerts only). If the state machine was still stale: `mts status`.
- Committed: operator tooling 309d115, research extracts ba4a396.
- FABIO: agent STOPPED (tokens). NUC replies 087, 089 delivered, 088 unusable -> 090-fabio-escalation-retry queued/ran.
  Tests + driver exist UNCOMMITTED in MyTradingSys/backtest/layers/fabio/ (test_fabio_*.py, run_backtest.py).
  Next: a Sonnet agent verifies 087/089/090 (full slugs), promotes by RENAME, runs run_backtest.py, writes
  FABIO_L1_REPORT.md. Brief = 3.W4. Passing rules -> ALERTS only; the Tom override ruling is still the operator's.
- T040 TICK LAYER: operator decided (2026-09-28): (1) full-history rank tiers = the documented exception, usable live
  as FLAGS (context only, never gate Tom); (2) data 2022-01..now 1m klines + metrics OI (5m -> OI tiers 5/10/15m
  only); (3) start now via Qwen. Spec agent STOPPED mid-way: check specs/091-093 + layers/tick/ for partial work,
  finish/pack: 091 tick-extremes (net_delta, cvd_change, volume, price_change_pct x 1/2/3/5/10/15m; rank top/bottom,
  gap-jump tiers, session+funding tags -> tiers.json), 092 OI extremes, 093 live flagger (public websocket, tier
  crossing -> JSONL source:"tick", cooldown per indicator/tf/side, replay mode). Append the decisions to
  items/T040_tick_delta_layer.md.
- NUC speed: FLASH_ATTENTION=1 + KV q8_0 active since the reboot; 089 ran at ~1.4 tok/s vs ~3 before. If 090 is also
  slow, remove OLLAMA_KV_CACHE_TYPE first. "2 worker processes" = launcher + worker (normal).
- 082 formula-audit-a output = exactly 6144 tokens (the cap) -> likely truncated; check before 083.

## 7. Operator research asks - ON FAST-TRACK (2026-09-28)
| Item | Ask | Status |
|---|---|---|
| T040 | all-time extreme rankings per indicator x tf -> severity tiers -> live anomaly flags | decisions made (s6), specs 091-093 NOT written yet |
| T054 | anomalies x liquidity runs at the US open; US pre-market alert; US-equity/BTC correlation; news (free sources first) | filed, not started; depends on T040 |
| T053 | two-account hedge / leveraged scalping (a, b1, b2) - research what works, then backtest | filed, not started |
| T055 | net/new longs-shorts positioning flow (how pros use it, MTF trend bias, confluence) + most reliable BTC setups per style | filed; web research running (Sonnet) -> T055a/T055b reports |
| T048 | satellite framework + exchange API layer | OPEN (design); T053 feeds it |
Order: T040 (Qwen) -> T054 step 2-3 research (Sonnet, Qwen for code) -> T053 research (Sonnet web research, then backtest).
