# Supervisor log (Opus supervisor sessions)

One entry per supervisor session. Next supervisor: read this plus STATUS.md; nothing else from the chat is needed.

## 2026-09-28 - session 1

Landed: 0bbace1 L6 re-arm (T4 safety review: breach check still runs after re-arm, never blocks the
protective stop), 3f98dc8 CryptoCred cc_structure/cc_retest/cc_setups + 19 tests (2 Qwen bugs in
cc_setups caught by plan-derived tests), 01d0eed six Tom extracts (quote-verified), 63383f7 gate step 5b
(layer tests, also under --quick), 65815f9 lesson OUTPUT_TOKENS, 4f74c20 RSI/timeframe design +
operator directive verbatim in PROJECT_VISION, 3569ee3 1m history 2022-01..2025-08 fetched.

Operator decisions: bin NUC 019 (done: .rejected_019 + verdict). Download 1m history to 2022 (done).
RSI 40/60 is private to the MalkanView sub-layer; every other RSI use is standard (14, 70/50/30).
Wants: smoothed RSI MA + support on it per timeframe; tolerance ("slippage") around 40/60 found by
backtest for every edge case; alerts per timeframe incl. 1,2,3,10m and 2d,3d,5d; params tunable on
testnet from operator and trusted-professional input. NUC should do as much backtesting as possible.

Supervisor decisions: RSI_TF_LAYER_DESIGN.md D1-D7 (timeframe layer serves all layers, core later;
RSI split core/ma/events/malkan_40_60; params files with provenance; backtests on desktop now, NUC
"RUN" job type later if sweeps exceed ~30 min and Python is on the NUC).

Caught: test plans must come from definitions, not code - rsi TEST_PLAN C1 had been copied from
bt_rsi.py.new (off vs textbook Wilder: idx5 70.0 vs 77.777778). Fixed; 071 repacked. NUC tasks
070-075 moved to Dumps/workers/NUC-QUEUE/held/ until the formula audit (FORMULAS.md, re-derivation
of all plan numbers, Qwen 076 formula_audit.py) repacks them into incoming/.
Also caught: 031 packed with OUTPUT_TOKENS 3500 and 063/064 with 2500 (both would truncate); raised.

Open: formula audit agent; worker-model research (WORKER_MODEL_RESEARCH.md); NUC 031 was 66+ min
without a heartbeat at 09:10Z (longest earlier task 57 min) - check the NUC if still silent;
L6 part 2 (P/L from transaction log, 095ea22) not built; prob_table.py.new and bt_rsi.py.new
unreviewed (bt_rsi superseded by layers/rsi, do not promote); make_status "Open Findings" stale;
TF-B5 native-1d gate needs a real-data test; Malkan rules have no verbatim extract yet (only
research/malkan_rsi_2026-09-28/WEB_RESEARCH.md; NUC 040 reply PARTIAL) - multi-timeframe 5-star
composition (monthly+weekly gate daily) is a later task.
Next: Qwen self-validation technique -> pick from research, add to spec template and queue_tool.

Worker research (WORKER_MODEL_RESEARCH.md) -> decisions: keep qwen3-coder:30b; pilot one alternative
(glm-4.7-flash class MoE) on 2-3 already-verified specs before any switch; Devstral Small 2 24B (dense)
too slow for this CPU. Worker v3 batch (Sonnet session, T049): (1) EDIT output mode (search/replace
blocks) for changes to existing files - full rewrites only for new files; (2) execution-feedback retry:
verify runs the spec's tests, on failure auto-packs NNNr with the failure log, max 2 repairs; (3) sample-
and-vote (3 candidates) only for execution/risk specs; (4) package options num_thread 6 (physical cores;
research said 8, llama.cpp guidance is physical cores - measure both), keep_alive long. Operator sets
OLLAMA_FLASH_ATTENTION=1 and OLLAMA_KV_CACHE_TYPE=q8_0 on the NUC (server env; not reachable from here).

Operator 2026-09-28: FORMULAS.md must cover EVERY formula MTS uses (core, execution sizing/fees/P&L,
indicators, probability, backtest stats), not only the RSI/backtest layers. Inventory agent running;
money-affecting untested formulas get audited first. NUC heartbeat: nuc-worker.ps1 writes heartbeat only
at task start and calls Ollama with stream=false (timeout 7200 s), so silence during a long task is
normal, not a hang. Worker v3 adds: stream + heartbeat every 60 s with tokens so far. HDMI unplug on the
NUC does not affect CPU inference.

Formula audit (layers) done 248ab9d: FORMULAS.md s1-10, every plan number re-derived, only C1 was wrong.
RSI flat-series = 50 (TradingView gives 100) kept as a documented deviation. NUC 070-076 released.
Whole-MTS inventory: FORMULA_INVENTORY.md (priority list at bottom). Pending operator decision: core ATR
is SMA of TR, not Wilder - keep (Tom's numbers) or switch?

NEXT SESSION BRIEFS (Sonnet, one each):
A. "Execution formula tests": FORMULA_INVENTORY priority 1+2. Add FORMULAS.md sections for execution
   math; tests for plan_compiler/executor/risk_guard from definitions (fail on a mutated copy); Java net R:R
   shared constant + JUnit. Stage as .new; Opus supervisor T4-reviews before promotion.
B. "Worker v3" (T049): EDIT output mode, test-failure retry (max 2), sample-and-vote for execution specs,
   streaming + heartbeat every 60 s with tokens so far, options num_thread 6 / keep_alive. Pilot
   glm-4.7-flash-class model on 2-3 verified specs.
C. "NUC replies": verify 031/063/064/070-076 as they land; write tests for 070-075 from the committed
   plans; run formula_audit.py once 070-073 are promoted; then first backtests (RSI tolerance sweep,
   CryptoCred setups) per RSI_TF_LAYER_DESIGN D3/D5.
D. Later: Java indicator JUnit tests (priority 3), L6 part 2, make_status stale findings, TF-B5 real-data gate.

NUC remote access (2026-09-28, verified): desktop key ~/.ssh/nuc_gate, forced command
C:\MTS-Worker
uc-gate.ps1 (source: Dumps/workers/NUC-QUEUE/setup-ssh/). `ssh -i ~/.ssh/nuc_gate
e-ngineers@192.168.29.110 status|logs N|ollama-ps|env|restart-worker confirm`; anything else refused
(tested: echo refused). Firewall: port 22 from 192.168.29.188 only; password auth off. restart-ollama needs
task MTS-Ollama (not created). OLLAMA_FLASH_ATTENTION / KV_CACHE_TYPE still unset (operator via RDP);
user env has NUM_PARALLEL=1, KEEP_ALIVE=30m. At 11:20Z NUC on 076 (last queued) - queue about to go idle.

Session 1 closed ~11:30Z. Handoff + next-session waves: NEXT_SESSION_PLAN.md.

## 2026-09-28 - session 2 (Opus supervisor, auto mode)
Operator decisions (asked once at start):
- "Live testing" = BOTH: testnet order runs with Tom core signals + indicator-layer ALERTS (alert-only).
- Core ATR: KEEP plain average of True Range; document it in FORMULAS.md (no Wilder switch).
- R4: L6 part 2 DEFERRED for testnet (L6 re-arm suffices); must be built before any mainnet use.
~13:05Z: queue shows 076 running with a 105-minute-old heartbeat; the SSH gate shows Ollama active (qwen3-coder:30b
loaded, ctx 22528) but TWO worker processes (pid 4084, 10368) - check for a duplicate worker.
Wave 1 launched in background: W1 layers (Sonnet), W2 execution math (Sonnet, staged only), W3 replies
(Haiku), W5 NUC specs 077-081 (Sonnet).
