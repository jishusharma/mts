# Next session plan - Opus supervisor, auto mode (written 2026-09-28 ~11:30Z by supervisor session 1)

Goal of the session: **ready for live testing on Deribit TESTNET** (never mainnet). Start with
"Supervisor: read NEXT_SESSION_PLAN.md". Read this file + STATUS.md only; SUPERVISOR_LOG.md has the history.

## 0. First 3 minutes (T0, no agents)
1. `python scripts/dev/make_status.py` then read STATUS.md (56 lines).
2. `python scripts/worker/queue_tool.py status` and
   `ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 status` (see memory nuc-ssh-gate).
3. Ask the operator the two open questions in section 6 in ONE message, then start wave 1 without waiting.

## 1. State at handoff
- Branch fast-track, all work committed (last: 91065eb). Gate: `run_all_tests.py --quick` green at 63383f7.
- NUC: 070-075 delivered (not yet verified), 076-formula-audit running (started 11:18Z), queue then EMPTY.
  Unverified replies: 9 (031 runbook, 063/064 Tom halves, 070-076). NUC needs new specs (wave 1, W5).
- Layers: cryptocred committed + tested (19). timeframe/rsi/runner: plans + params + FORMULAS.md committed;
  implementations only in NUC replies. No layer backtested yet.
- Execution: FIX4 verified on testnet (4d0a5de), L6 re-arm committed (0bbace1). Execution MATH untested
  (FORMULA_INVENTORY.md priority 1-2) - the main blocker for live testing.
- Data on desktop: 1m BTCUSDT 2022-01..now (raw_1m_2022 + raw), 1d 2020-01..2025-08 (raw_1d).

## 2. Live-testing readiness gate (all must be true before a testnet live run)
| # | Criterion | Owner |
|---|---|---|
| R1 | Execution formula tests (plan_compiler, executor, risk_guard mark=None, Java net R:R constant) written from FORMULAS definitions, fail on a mutated copy, promoted after Opus T4 review (lesson B) | W2 + Opus |
| R2 | Full offline gate green WITHOUT --quick (Maven + backtest) | W6 (Haiku) |
| R3 | Testnet suite re-run after R1 changes: base, G1/G2, FT-2, kill switch (same as 4d0a5de) | operator runs, Haiku reads receipts |
| R4 | Daily loss guard: L6 re-arm in; L6 part 2 either built or explicitly deferred for testnet by operator | Opus decision |
| R5 | Layers promoted (timeframe, rsi, runner) + formula_audit.py all PASS; layers produce ALERTS ONLY on testnet, never orders, never Tom filters | W1 |
| R6 | First backtest reports exist (RSI tolerance sweep, CryptoCred setups) so testnet tuning has a baseline | W7 |

## 3. Waves (spawn in parallel; every agent returns <=20 lines; Opus never reads whole files)
Wave 1 - start immediately, background, all at once:
- **W1 Sonnet "layers"**: `queue_tool.py verify 070 071 072 073 074 075`; write test_*.py.new for each from
  the committed plans (timeframe/TEST_PLAN.md, rsi/TEST_PLAN.md, TEST_PLAN_runner.md, cryptocred/TEST_PLAN.md
  for 075); fix impl minimally only where the plan is clearly right; promote passing modules + tests with gate;
  commit per module. Report failures with plan case ids. (When 076 lands: run formula_audit.py, report table.)
- **W2 Sonnet "execution math"** (brief A): add FORMULAS.md sections for execution math (tick snap, size
  rounding, ladder, inverse avg fill = harmonic, worst-case loss, target from pnl%, notional cap); tests from
  those definitions; mutate-copy check; Java: one shared friction constant + JUnit for net R:R. STAGE ONLY
  (.new). Return diff stats + findings; Opus T4-reviews, then W2 promotes.
- **W3 Haiku "replies"**: verify 031 (FT2_RUNBOOK >= 250 lines, has "### HALT Files (Post-FIX3)"), 063/064
  (merge into extract_hQ8sOq67x5o.md.new, verify_extract_quotes PASS); promote passing, commit.
- **W5 Sonnet "feed NUC"**: write + pack specs so the NUC never idles (order by value):
  077 timeframe real-data gate script (TF-B5: resampled 1d vs raw_1d native, report); 078 rsi_ma support/
  rejection events per D2 (if not in 072); 079 malkan multi-timeframe composer (monthly+weekly gate daily,
  MLK-GAP1); 080 alert emitter: bar_closed(tf) -> layer events -> alerts JSONL per timeframe (testnet
  alerts, no orders); 081 backtest sweep driver for D3 tolerance grid. Test plans first (hand-computed),
  OUTPUT_TOKENS >= 4096 and >= file size, EXPECT lines naming new text.
Wave 2 - after W1 promotes:
- **W7 Sonnet "first backtests"**: run layers runner on 1m 2022..now for RSI tolerance grid (D3) and
  CryptoCred setups via 075 adapter; manifest per run under Dumps/backtest/runs/; short report
  BACKTEST_L1_REPORT.md (per timeframe: events, hit rate, fwd returns, chosen tolerance OOS, PBO).
  Long runs: one background shell, not a polling agent.
- **W6 Haiku "full gate"**: run `run_all_tests.py` (no --quick) after W1+W2 promotions; report.
Wave 3 - if time: **W4 Sonnet "worker v3"** (brief B). CAUTION: deploy/nuc-worker.ps1 auto-installs on the
NUC at next launch - test offline first, keep old worker as .pre_v3, deploy only when the queue is idle.

## 4. Auto-mode rules for the supervisor
- Allowed without asking: agents, gates, commits on fast-track, queue pack/verify, ssh gate read commands.
- Ask the operator first: promoting execution code (after T4 review), any testnet run that places orders,
  `restart-worker confirm` while a task runs, deleting anything.
- The auto-mode classifier blocks persistence (NUC keys, scheduled tasks, security settings): do not route
  around it; hand those steps to the operator.
- Never mainnet. Never read .secrets/.env/keys. Never push/merge/rebase/reset.
- Spot-check one claim per agent report (this session caught 4 real errors that way: RSI C1 copied from code,
  OUTPUT_TOKENS too small twice, a wrong Wilson-divergence claim).
- Token discipline: agents return tables <= 20 lines; background everything; Opus reads diffs only for T4.
  Restart the supervisor at ~25 operator turns or after wave 2, appending to SUPERVISOR_LOG.md first.

## 5. NUC CPU at the ceiling - tuning
100% CPU during generation is expected (CPU inference uses every core). The problem is EFFICIENCY:
log timings show throughput collapsing with context: 064 (3.6k in / 1.1k out) 213 s, but 073
(8.3k in / 2.2k out) 1553 s - about 5x slower per token at ~2x context. Fixes, in order:
1. Operator via RDP: `setx OLLAMA_FLASH_ATTENTION 1 /M`, `setx OLLAMA_KV_CACHE_TYPE q8_0 /M`, restart Ollama
   between tasks. Expected biggest gain at 8k+ context.
2. Worker v3: pass `num_thread 6` (physical cores; hyperthreads usually hurt llama.cpp) and measure vs 12.
3. Operator: Windows power plan High performance; NUC BIOS fan = performance / cooling priority; keep vents
   clear. A 15-25 W U-series CPU throttles under sustained load - thermals may be the real cap.
4. Keep specs small: <= ~8k prompt tokens (scope line ranges, not whole files).
Measure before/after with the log lines ("tokens in X, out Y; Z s"); W4 adds `queue_tool.py perf`.

## 6. Open operator questions (ask once, early)
1. What exactly is "live testing": (a) execution soak on testnet with Tom core signals, (b) indicator-layer
   ALERTS on testnet with operator tuning, or both? (Plan assumes both; layers alert-only.)
2. Core ATR is a plain average of True Range, not Wilder: keep (document) or switch (backtest both first)?
Also pending: L6 part 2 build now or defer for testnet (R4); 1-2 named professionals whose parameters should
seed params files (source field).
