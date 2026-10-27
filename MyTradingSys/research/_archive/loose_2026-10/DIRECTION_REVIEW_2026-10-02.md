# DIRECTION REVIEW 2026-10-02 (Opus, CLI-SUP, session MTS-2026-10-02-1050Z-CLI-SUP-direction)
# Tags: RESULT = read or run this session on JIS desktop; EXPECT = prediction; OPINION = supervisor judgment.

## 0. One-paragraph answer
We are on the right *method* (trader's own words -> code -> measured on BTC) but the wrong *feedback loop*. In 72 h the
project produced audits, a kappa study, conformance checklists, a v3 spec and 93 unit tests, and **zero Tom or Fabio
trades on testnet** (RESULT: trade_ledger.jsonl 14 rows = 8 turn_of_candle, 5 rsi, 1 smoke; Tom 0, Fabio 0). The live
stack has been **down since 2026-09-29 ~22:30Z (auto_trader) and 2026-10-01 19:44Z (Tom Java apparatus)**, and nothing
flagged it. Nothing yet shows that the system "is correct to apply to BTC": `methodology/crypto_adaptations.md:18-36`
*asserts* 13 Tom rules transfer "Identical"; every validation row (:72-80) is "After S02 live" and none was run. What
we have measured on BTC is negative or broken (section 2). Next: stop adding documents, put Tom on testnet, fix the
three measured breaks, then re-test. More Opus rule extraction is not the bottleneck.

## 1. Sonnet session validation (MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3)
| Claim | Check this session | Verdict |
|---|---|---|
| 14 files promoted, pure renames | `git show --stat eddd237`: 13 renames at 0 lines changed + README.md new (46 lines) | PASS |
| v3 pytest 93 passed | re-ran `python -m pytest .../fabio/v3/tests -q` -> `93 passed in 0.52s` | PASS |
| no .new left in v3 | recursive count = 0 | PASS |
| v3 not in gate | consistent with OPUS_PLAN:33; not re-checked | accepted |
Notes: (a) it ran as Sonnet but the plan header says "(Opus, ...)" (OPUS_PLAN_2026-10-02.md:2); the session record
says Sonnet, so the header is the error. (b) v3/README.md:5 still says "Status: STAGED ... still .py.new"; it is stale.
(c) Its plan is sound as a v3 hardening plan, but it orders work inside Fabio v3 and never asks whether any of it reaches
a trade. Section 4 re-orders it.

## 2. What is measured on BTC so far (RESULT unless tagged)
1. **Testnet:** Tom 0 trades. All 19 Tom decisions in auto_trades.jsonl are `signal_rejected` (WAIT_RR 14, WAIT_TRIGGER 3,
   WATCH 2) plus 1 `skipped_auto_pause` (tom#70). auto_trader_config.json was changed at 2026-09-29 20:22Z to accept
   WAIT_RR with min_net_rr 1.25 (mtime); the trader died about 2 h later, so **that change was never exercised**.
   Tom alerts #71-#82 (runtime_data/alert_counter.txt = 82; auto_trader_state.json tom_last_alert_no = 70) were
   emitted with no trader running and are lost.
2. **The live Tom engine still enforces NO-SOURCE gates:** last apparatus line 2026-10-01 19:44Z reads
   `TWOPEAK/above_vah | WAIT_RR (net_rr 1.83 < 2.0)`. That 2.0 floor is verdict.py:105-111 (cites operator ruling
   D1(a) 2026-09-27); the [2.0, 3.5]R nearest-level window is PROVENANCE_AUDIT_TOM A08-A10 = NO-SOURCE, and it puts 67%
   of snapshots into WAIT_RR. TWOPEAK is M03 = NO-SOURCE. The provenance rule (CLAUDE.md, 2026-09-30) has not reached the
   running engine.
3. **Tom backtest is not yet a verdict.** 19 SETUP_FORMING in 2022-2026, **all short** (TOM_CORE_BT_REVIEW H1: p about
   4e-6 under 50/50). That points to a bug in archive mode (fail-closed proof_dir or derived CVD), not to a property of
   Tom. The "null is as good" result is partly a fill-mechanics artefact (H2). So "Tom has no edge on BTC" is NOT shown.
4. **Fabio:** L1 detectors show no edge (PBO 0.756); the OF model nets negative after fees (median gross +0.13R vs fee
   drag about 0.66R), per CONSOLIDATION_REPORT:31. v3 is unit-tested code with no live path. It also cannot run until 8
   grid parameters are chosen (v3/README.md:25: `N, p, z_hi, m_c, f, g, entry_mode, mgmt`, "NS-grid, no defaults"),
   and the provenance rule forbids tuning them.

## 3. The emerging pattern (OPINION, built on MISSING_PIECES_2026-09-30.md:11-28)
The edge both traders describe lives in the **trade shape**, and our pipeline cuts it off:
- **Right tail:** Tom risks 12 ticks to make 97; Fabio recovers a -9k day with one 1:20. Our engine caps targets at 3.5R
  and floors them at 2.0R (A08-A10). The Fabio sim caps at 3R.
- **Costs vs stop width are the real crypto adaptation, and no one has done it.** A 12-tick ES stop is about 0.04%. On
  Deribit a stop that tight costs at least 1R in fees. At the engine's 0.2% fallback the round trip is 0.25-0.5R. DAX/ES
  stop distances do not port 1:1, and that question decides edge more than any rule row.
- **Entry timing is inverted:** they rest limits before the touch; we enter after proof or a trigger bar.
- **The location anchor is a crypto hack:** "UTC 00:00 as daily open" (crypto_adaptations.md:50, UNVALIDATED) defines
  every prior-day VAH/VAL/POC Tom trades from. Tom never traded BTC, so his words cannot settle it; it needs a
  pre-registered level-reaction test, not a trade backtest.
So the answer to "are we on the right path": the provenance discipline is right and is already removing what cut the
tail. But the project spends its tokens proving documents, not observing trades. Tom himself sets the bar at
"200-300 trades for key figures" (crypto_adaptations.md:34). We have 0.

## 4. What to do more, less, and in what order
| # | Item | Tier / surface | Why first | Done = |
|---|---|---|---|---|
| P0 | Restart the live stack (both vbs launchers + auto_trader stack). **Operator / supervisor only.** | operator | 0 Tom trades because nothing runs; the WAIT_RR >= 1.25 config has never run | canary GREEN; first Tom `trade_attempt` in auto_trades.jsonl |
| P1 | Testnet canary every 30 min + daily Haiku summary (section 5) | T0 script + T1 | 2.5 days of downtime went unnoticed | scheduled task runs; RED reaches OPERATOR inbox |
| P2 | Tom all-short diagnosis: tabulate the 301 proof-5 rows lost by verdict gate x direction (TOM_CORE_BT_REVIEW H1 fix) | Sonnet, CL, F: data | decides whether the BTC backtest verdict is real or a bug; highest information per token | table committed; bug named or ruled out |
| P3 | Remove NO-SOURCE gates from the live Tom path: net_rr 2.0 floor (verdict.py:105-111), [2.0,3.5]R window (SCB:150-175) -> Tom's "next node" target (Q03, Q12) | operator ruling (reverses D1(a)), then Sonnet build `.new` + Opus safety review, live path | the provenance rule is binding but not yet in the engine; restores the right tail | gate PASS, supervisor restart, Tom trades with targets > 3.5R appear |
| P4 | Cost-portability table: for each Tom/Fabio trade quoted in transcripts: stop in ticks and % of price, target R, outcome R | **new extraction angle**, Sonnet or DSA (free) over existing transcripts | the trade, not the rule, is the unit of edge (MISSING_PIECES:12); feeds the stop-width decision | CSV of trades with file:line quotes, verify_extract_quotes PASS |
| P5 | Session-anchor test for BTC levels (UTC00 vs NY open vs CME): pre-registered reaction study | Sonnet backtest, CL | validates crypto hack #5, the location half of "does Tom transfer" | pre-reg file, then one run, trial registry row |
| P6 | Fabio v3: oracle + mutation + gate step (OPUS_PLAN item 2) | Sonnet, CL | hardens code; keep it, but it does not create a trade | per OPUS_PLAN section 5 |
| P7 | Fabio v3 to testnet: source the 8 NS-grid values from Fabio's words where a quote exists; the rest run **shadow-only** (all grid points logged as collection-only signals, no orders, per LESSONS G turn_of_candle rule) | operator decision, then Sonnet; live emitter = layers/alerts/ = owner claim + `.new` | the only way v3 meets live BTC without tuning | shadow signals in runtime/alerts with a `collection_only` tag |
| P8 | Tom 22 both-reader NO-SOURCE rows re-extraction (OPUS_PLAN item 6) | Sonnet | keep; lower value than P2-P4 | per OPUS_PLAN |
**Less / stop:** new Opus rule extractions (602 kept sentences and 213 indexed rules already exist; rules are lost
between prose and code, not in extraction, CONSOLIDATION_REPORT:16-18); more kappa rounds; more meta-docs and prompt
checklists (LESSONS_LEARNED lists 11 USD on 2026-10-01 plus about 18 USD on 2026-10-02 of cloud burn, and about 12 prompts in 6 h).
**Gemini / Grok:** low value. Web and X posts can tell us practitioner conventions (how BTC volume-profile traders
anchor the "day"), not whether there is an edge, and they pass the research gate at T3 at best. Spend at most one free
DSA/Gemini turn on the P5 anchor-convention question and nothing more. Do not use them to "validate" the system.

## 5. Cheap testnet worker (the operator asked for Haiku)
- Running trades needs no model. The live stack (auto_trader + live_runner_cli + Java apparatus) trades every alert
  that passes config. New code reaches testnet when it is committed, gated and the supervisor restarts the process.
- So the worker is **T0**: `scripts/dev/testnet_canary.py` (built this session, see the session record). It checks
  processes, freshness, unconsumed Tom alerts, brakes, and new commits on Tom/Fabio/live paths. With `--run-gates` it
  runs the gates and prints `RESTART NEEDED (supervisor only)` when committed live code is newer than the running
  process. It never restarts anything.
- **Haiku (T1) only reads:** a daily `claude -p --model haiku` run over the CANARY and TESTNET_STATUS files that writes 10
  lines to the supervisor inbox (per family: trades, net, rejects by reason; RED events). Creating the Windows scheduled
  tasks is persistent config: operator approval needed (section 6).
- New Tom/Fabio code that is not yet live-wired (Fabio v3) cannot be "run on testnet" by any worker until P7 exists.

## 6. Operator decisions needed (blocking, in order)
1. P0: approve the restart of the live stack now (only you or the supervisor restart; execution/ is claimed by
   MTS-2026-10-02-0930Z-DSA-COO until 2026-10-02 per SUPERVISOR_LOG).
2. P1: approve two scheduled tasks: canary every 30 min (T0), daily Haiku summary (T1).
3. P3: reverse ruling D1(a) (the net_rr >= 2.0 floor) and the [2.0, 3.5]R window, as NO-SOURCE under your 2026-09-30
   provenance rule. Yes or no.
4. P7: Fabio v3 NS-grid parameters: source-or-shadow (recommended) vs keep v3 backtest-only.

## 7. Decision log

### A1 - Scheduled tasks for the 12-hour window (2026-10-03)

Operator ruling: leave the system running 12 hours; plan only for that period; frequency as per tasks planned.

Decision (DSA, 2026-10-03):
- Canary stays at 30-minute cadence. Already installed; leave as-is.
- Approve Haiku worker in event mode: fires on canary RED only. SCHEDULER_PLAN section 2a.
- Approve Haiku worker in digest mode at two checkpoints only: +1h after the R2 restart settles, and +12h at the window close. Not the daily 06:00 default.
- Do not install the permanent daily schedule yet. Revisit at window close.
- Cost for the window: 2-3 Haiku runs, about $0.05-0.08.

Section 6 item 2 is CLOSED for this window. Permanent schedule deferred to window close.