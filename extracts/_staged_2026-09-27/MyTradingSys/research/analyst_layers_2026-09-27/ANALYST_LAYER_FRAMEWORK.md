# ANALYST LAYER FRAMEWORK + CORE COMPLETENESS ASSESSMENT
# Author: Opus 5.5 | Date: 2026-09-27 | Status: PROPOSAL (staged, nothing live changed)
# Inputs read: SESSION_3_HANDOFF, CORE_READINESS_PLAN, D1_D7_DECISION_BRIEF, extraction.md,
#   playbook.md Part I, crypto_adaptations.md, CONSOLIDATED_RULES.md (Tom), FvgCalculator.java,
#   SetupCandidatesBuilder.java (classifyState, 9.2 absorption), 2 new transcripts.

---

## 1. WHERE WE ARE (2026-09-27)

| Layer | State | Evidence |
|---|---|---|
| Execution / Deribit testnet | WORKS on testnet. Not mainnet-ready. | T050 Ph2+3 closed, proof suite 6/6 PASS. Files still .new (executor, deribit_orders, plan_compiler, run_testnet_suite). Open: G1 post-entry mgmt (stop not shrunk on partial target fill), G2 reconciler v2 + forced-mismatch test. |
| Signal core (Tom) | NOT complete. Half-way through Phase C. | C1 built, uncommitted, baseline not written. C2/C3 (Java) need Maven on desktop. C5 (D5/D6a doc text) unwritten. D6b (real SETUP_CONFIRMED trigger) not filed. |
| Backtest data layer | L0 fetch started (metrics 104 ok, funding 11, mark klines 38). L1-L4 not built. | archive_fetch2.log; SESSION_3 plan. |
| Analyst layers beyond Tom | Folders exist for cryptocred/flowhorse only; mixed into Tom's `fresh/`. No registry. | Section 6. |

Answer to "is core complete?": **No.** The execution plumbing is ahead of the signal it is
supposed to execute. Right now testnet proves we can place and protect an order; it proves
nothing about whether MTS knows *when* to.

## 2. WHY THE CORE FEELS INCOMPLETE — four root causes (measured, not opinion)

**R1. The source corpus itself is only half-processed.**
  89 Tom raw transcripts on disk. 50 have any extraction; **39 (44%) were never extracted.**
  Only 26 are cited anywhere in conditions/*.md, 10 in compiled_engine.md, and
  compiled_engine.md carries **1** TOM- tag (T043 traceability still open).
  (Counts by 11-char video-ID match; citation formats that don't include the ID are missed,
  so treat as approximate.)

**R2. Extraction captured WHAT Tom says, not HOW he decides.**
  CONSOLIDATED_RULES.md is a sentence filter ("Kept 51/121 sentences"). It yields nouns
  (VAH, absorption, single prints, proof) but not operational definitions. Every open
  decision item is exactly such a missing definition: D5/B063 (what is divergence /
  unhealthy trend), D6b (what confirms a setup), and classifyState can never return
  trend_unhealthy/transition because nobody defined them. Tom teaches visually on a
  footprint; the "proof" step was never quantified.

**R3. Concepts were implemented under the right name with the wrong construct.**
  - FVG: FvgCalculator.java = 3-candle price gap. Tom (Fj4FDZQxw0I) uses single prints and
    says FVGs work only in trend-stable phases (~30%). Fabio (o-w5Gxss6T0) says the candle
    gap is "typically wrong"; the real FVG is the lowest-volume price inside the value area
    of a fixed profile over one swing. Two sources, same verdict, code does neither.
  - Absorption: Java 9.2 = one candle (vol>2x, small range, delta vs colour). Fabio's
    absorption = CVD makes a new extreme while price holds its level (swing construct).
    Same word, different signal.
  This is the pattern the operator sensed: the engine has the vocabulary, not the mechanics.

**R4. No layering: one flat rule set trying to do context, location, trigger and bias at once.**
  A working discretionary system has at least: HTF bias/plan → auction state → location
  (where) → orderflow proof (when) → execution/management. MTS has location (strong),
  a weak state classifier, a thin proof step, and no bias layer. Result on 2 weeks of data:
  260 SETUP_FORMING → 23 after D1/D4 corrections. That is a thin signal, not a tuned one.

## 3. THE ANALYSTS — who they are (flags where the brief and the evidence differ)

| Analyst | Channel | What they actually teach | Fit | Flags |
|---|---|---|---|---|
| Tom Vorwald | (existing corpus) | Auction/VP context, idea+proof, zones | CORE context + location | 39 videos unextracted |
| Fabio Valentini | @fabervaaleEng (13 ENG videos, all fetched) | Orderflow: absorption, aggression, CVD-vs-price, volume-defined FVG, liquidity, risk protocol | CORE proof layer — fills exactly Tom's undefined step | Instrument is NQ, not BTC. "Student of Tom" and competition rankings: UNVERIFIED by me; treat as operator-stated. |
| Qriptal | @qriptal (daily BTC videos; 21/40 recent fetched) | Weekly BTC plan: levels, sweeps, "imbalances", wickless candles, monthly/weekly pivots, invalidations; posts his own trades | IDEA FEED + HTF bias candidate. Not a rule source yet. | Not an orderflow/Tom-school method. Sells an "imbalance indicator" whose calculation is undisclosed → any rule depending on it = REJECT tier (playbook Part I). His "imbalance" = small-body high-volume candle, NOT a price gap — do not merge with FVG. |
| CryptoCred, The Flow Horse | existing | Cross-trader CT-001..085 | existing layer | Flow Horse files mixed into Tom `fresh/` |
| Unnamed "crypto trader community" | crypto_adaptations.md hacks #1-6 | funding/OI/liq/UTC open | MISC bucket | source analyst lost → `misc_unattributed` |

Note on the operator's brief: the attachment's "world champ, student of Tom, transcript
below" paragraph sits under the Qriptal link but the transcript is Fabio's video
(o-w5Gxss6T0). I've treated the champion/Tom-student description as Fabio's.

## 4. TARGET ARCHITECTURE — layers with a single contract each

```
L4  EXECUTION        plan_compiler → executor → Deribit (DONE on testnet; G1/G2 open)
      ^ trade plan (entry/stop/targets/size)            
L3  PROOF / TRIGGER  WHEN: orderflow evidence at the location     <- Fabio (FAB-*), Tom proof
      ^ candidate zone + side                                   
L2  LOCATION         WHERE: VA/VPOC/VWAP/volume-FVG/single prints <- Tom (TOM-*), Fabio FAB-005
      ^ allowed sides                                          
L1  STATE            WHAT regime: balance / trend-healthy / trend-unhealthy / transition
                                                                  <- Tom + Fabio FAB-007/008
L0  BIAS / PLAN      Weekly plan, HTF levels, invalidation        <- Qriptal (scored feed), later own
X   CRYPTO CONTEXT   funding/OI/liqs — veto/size modifiers only   <- misc hacks (UNVALIDATED)
```
Contract rule: each layer emits ONE typed object, cites rule IDs for every field, and may
only consume the layer directly below. Analysts do not "sit on top" of Tom globally —
they own specific layers. That is how Fabio becomes core without replacing Tom:
Tom owns L1/L2 context, Fabio owns L3 proof and sharpens L1 (divergence) and L2 (FVG).

Qriptal enters differently: as an **external signal to be scored**, not as rules.
Every call is logged as a structured idea (entry, stop, targets, invalidation, time) and
scored against Binance archive data. Only a method that scores well AND is fully disclosed
may be extracted into L0 rules. First score (1 week, 1 video — anecdote, not evidence):
Sept-20 plan (short to 72-73k, hard invalidation 82.8k) was invalidated ~14h later
(09-21 08:00 UTC, run to 87.4k). QRP-ZPFK-01 = stop-out; -02 never triggered.

## 5. EXTRACTION → RULE PIPELINE for new analysts (the careful part)

Keeps extraction.md Phases 1-4. Adds four gates learned from Fabio/Qriptal:

G-A  **Term collision check** (Phase 2): every rule term is looked up in a
     glossary (`extracts/_registry/glossary.md`) that maps TERM → per-analyst construct.
     Same word, different construct (FVG, absorption, imbalance) → separate IDs, never merged.
G-B  **Operational completeness** (Phase 3): a rule may enter the engine only when each
     of: input data, parameters, window/anchor, output is defined. Missing → GAP with the
     exact undefined parameter named (see FAB-005 "UNDEFINED" lines). Parameter values we
     choose ourselves are tagged [SYSTEM] and must be swept in backtest, never presented
     as the analyst's.
G-C  **Example ≠ threshold**: numbers read off a chart example are recorded as example
     values, never as thresholds.
G-D  **Testable-claim register**: every frequency claim ("thousand of times") becomes a
     backtest hypothesis with a pass criterion, not a probability.

Rule ID namespaces: TOM-### (existing), FAB-###, QRP-<video>-## (trade ideas),
QRP-R-### (Qriptal method rules, later), CT-### (existing cross-trader), MISC-###.

## 6. FOLDER LAYOUT + MIGRATION (manifest; worker W5 builds a dry-run script)

```
extracts/
  _registry/analysts.json          # id, channel, role/layer, tier, lineage, status
  _registry/glossary.md            # term -> construct per analyst (G-A)
  tom/raw  tom/extracts  tom/consolidated
  fabio_valentini/raw  .../extracts  .../consolidated
  qriptal/raw  qriptal/trade_log  qriptal/scorecard.md
  cryptocred/  flowhorse/  misc_unattributed/
```
Moves (no deletes; old paths archived by copy first):
- raw_transcripts_canonical/*.txt (89, all Tom) → extracts/tom/raw/
- extracts/fresh/extract_*_fresh.md (48 Tom) → extracts/tom/extracts/
- extracts/fresh/*_the_flow_horse.txt (2) → extracts/flowhorse/
- extracts/processed/tom/CONSOLIDATED_RULES.md → extracts/tom/consolidated/
- extracts/processed/{cryptocred,flowhorse}/ → extracts/{cryptocred,flowhorse}/
- extracts/pending_raw/tom/new_selected_10/ → extracts/tom/raw/ (dedupe by ID; one file
  "WQ_OAdz-PJ8_I_Tested_10..." check channel before moving)
- crypto_adaptations.md hacks #1-6 get source=MISC tags (text edit, file stays).
Every script/tool that reads the old paths (harvest_tom_quotes.py, rebuild_tom_index_and_tag.py,
verify_harvest_vs_corpus.py, verify_rule_citations.ps1, update_prompt.py) must be grepped
and repointed in the SAME change, or a symlink/junction kept — W5 lists them.

## 7. CORE-CHANGE CANDIDATES from Fabio (proposed, each needs its own proof)

| ID | Change | Replaces / fills | Data needed | Proof gate |
|---|---|---|---|---|
| CC-1 | Volume-FVG: fixed-range profile over last impulse swing → lowest-volume price inside its 70% VA | FvgCalculator 3-candle gap (keep old as `candle_gap`, rename) | 1m klines + volume-at-price (aggTrades best; 1m klines as approximation [SYSTEM]) | Backtest FAB-006 rejection rate vs candle-gap FVG vs random level, holdout 3 mo |
| CC-2 | `absorption_cvd` swing signal (FAB-007): CVD new extreme, price holds prior swing within tolerance | fills D5/B063 divergence; sits beside existing single-candle `absorption_bar` (renamed) | 1m taker_buy → exact 1m CVD (archive has it) | replay on archive; event count + forward return by state |
| CC-3 | Failed-auction confirmation (FAB-008) as candidate trigger for SETUP_CONFIRMED | D6b | CC-2 + zone breakout attempt | same |
| CC-4 | Trend-continuation proof (FAB-009): counter-aggression with no price result inside momentum | TC setups' proof step | CC-2 | same |
| CC-5 | Big-trader filter (FAB-001) | none today | aggTrades (size) | only after Fabio's other videos define size |

Do NOT implement CC-1..4 before U2 (breakout-vs-reversal discriminator) is answered from
Fabio's other videos — wiring absorption without it risks trading the wrong direction.

## 8. WORKER DISPATCH (Opus designs; lower models execute)

| # | Task | Worker | Input | Output | Done when |
|---|---|---|---|---|---|
| W1 | Phase-1 extraction, Fabio 12 remaining videos, one file each, template = extract_o-w5Gxss6T0.md. Priority order: Khgj5q1-ln8, cUTsoU-15Tc, Pz8f0wWW12M, 06R-ebyOhDI, FawPrRUGNpk, LQvv5xgy_ik, StaphlRH8NQ, then the rest | Sonnet (1 agent per 3 videos) | fabio_valentini/raw | fabio_valentini/extracts/*.md | every rule has quote+timestamp+UNDEFINED list; U2 addressed if any video covers it |
| W2 | Qriptal trade logs for the 21 fetched videos, template = tradelog_ZPFK3ZsLwoo.md | Haiku or Sonnet | qriptal/raw | qriptal/trade_log/*.md | per template |
| W3 | Fetch remaining 19 Qriptal transcripts (YouTube IpBlocked after ~34 requests; throttle 20-30 s, resume list) | NUC qwen3-coder (script) or desktop | q_list.txt | qriptal/raw | 40/40 |
| W4 | Qriptal scorer: parse trade_log ideas → score vs Binance 1m archive (triggered? stop/target first? MFE/MAE) | NUC qwen3-coder + unit tests | trade_log + backtest data | qriptal/scorecard.md | unit tests on 3 hand-scored ideas |
| W5 | Folder migration: dry-run script from §6 manifest + list of path consumers | NUC qwen3-coder | this doc | MIGRATE_ANALYSTS.py.new (dry-run default) | operator runs dry-run, then real |
| W6 | Tom backlog: Phase-1 extraction of the 39 never-extracted videos, SAME template (rules + UNDEFINED), not sentence filtering | Sonnet | tom/raw | tom/extracts | 39/39 |
| W7 | Phase-2 consolidation Fabio + glossary.md (G-A) | Opus review of Sonnet draft | W1 output | fabio consolidated + glossary | conflicts listed, not resolved |
| W8 | CC-1/CC-2 design review → implementation tasks | Opus (design), Sonnet/NUC (code) | W7 + backtest L0/L1 | task files | after U2 answered |

Parallel track (unchanged, do not stall it): finish Phase C (C1 commit, C2/C3 on Maven,
C5 text), G1/G2 before mainnet, backtest L1 adapter.

## 9. ONE DECISION NEEDED FROM OPERATOR (before W8)
Should Fabio's definitions be allowed to OVERRIDE Tom's where they conflict (L3 proof),
or only fill gaps where Tom is silent? Recommendation: fill gaps + override only where
Tom is visually-only (no operational definition) — i.e. proof/absorption/FVG — and keep
Tom authoritative for context (state, zones, R:R).
# END
