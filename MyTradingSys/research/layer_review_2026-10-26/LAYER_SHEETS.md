# Layer sheets - 13 families (Lead, 2026-10-26)
Source: `MyTradingSys/system/LAYERS.md` (L = line there) plus LAYER_PROVENANCE_AUDIT totals and BACKTEST_ERRORS part 1. Facts only; "recorded" = what the repo says, not my decision. Nothing here keeps, drops or parks a layer. Parameter label counts are SOURCED / CONCEPT-ONLY / NO-SOURCE from `LAYER_PROVENANCE_AUDIT.md:31-38`; families with no row there say NOT_IN_DATA (find: `grep -n "SOURCED" MyTradingSys/research/*PROVENANCE*.md`).
Each sheet ends with the `lf-<family>-gemini-facts` slot: when that sheet lands, add one row of agreements and differences. Gemini sheets were not on trunk when this was written.
Do not trust these numbers over the report they point at; the report line is given in each row.

| Family | Idea (family title, L8) | Source (L) | Parameters | Backtests recorded (L) | Errors found (BACKTEST_ERRORS ids) | Combines with |
|---|---|---|---|---|---|---|
| tom | Order flow + volume profile; Tom v2 being redefined (L11,13) | `TOM_LAYER_V2_SPEC.md`, `SOURCED_RULES.md`, `TOM_VERBATIM_INDEX.md` (L24) | book_imbalance never counts in historical snapshots; P06 volume spike NO-SOURCE (L14); counts NOT_IN_DATA | TOM-CORE-0929 net -0.30 R, holdout -0.32 R n=254 (L23); TOM-CORE-1007 net -2.91 R, holdout -2.80 R (L21); VP anchors: 46/48 CIs straddle 0 (L19) | B146, B147, B131, B085, B084 | guidance (Q33) |
| fabio | Order-flow layer; v3 OOS FAIL, 79 trades -0.1038 R; being redefined as v2 (L45) | `FABIO_V3_SPEC.md`, `FABIO_RULEBOOK.md` (L58) | legacy fee pair on fabio_of (L51); counts NOT_IN_DATA | L1-FABIO no edge (L57); FABIO-OF insufficient n (L55); CVD divergence adds nothing over price (L53) | B142 (extra-setup stop), T09 F1/F4 (side inverted, 99-bar window; LAYER_REALITY:8) | guidance |
| guidance | Tom/Fabio cross-guidance, BB, LVN, regime filters (L73) | `GUIDANCE_AUDIT.md`, `PRE_REG_Q33.md` (L79) | NOT_IN_DATA | Q33: no cell survives, smallest q 0.62 (L78) | none recorded | Tom, Fabio |
| rsi | RSI 40/60 levels (Malkan), divergence, Kurisko quad rotation (L85) | `KURISKO_SPEC.md`, `FORMULAS.md` (L95) | 4 / 10 / 12 (provenance:31); no sourced exit | L1-D3 1h support PBO 0.030, rest 0.39-0.91 (L94); RSI-DIV-MTF 31 of 32 net negative (L91) | T09 F3 (live event set differs); provenance exits | Krown regime (same-object pair, design:37) |
| cryptocred | S/R flip, fib pullback, failed MSB setups (L106) | B143 item, FORMULAS (L114) | 6 / 11 / 8 (provenance:32); 1.5:1 and 2:1 are minimum filters used as targets (provenance:41-42) | FAIL after trade-through rerun (L107); BIGTRADE-EXIT first row negative (L111) | B143, B151, B145 | levels layers |
| positioning | Funding, OI, whale / FlowHorse (L121) | `whale_positioning_evidence_2026-09-12.md` (L130) | 0 / 4 / 3 (provenance:33) | T055-C1 rerun OOS net -0.0453% (L128); OI-DELTA descriptive (L129) | funding tf 1h live vs 15m tested (LAYER_REALITY:17); B103 | context for others |
| session_timing | Session levels, turn of candle, session momentum (L138) | `TURN_OF_CANDLE_ORIGIN_2026-10-09.md` (L152) | session 1/2/3, turn_of_candle 2/1/2 (provenance:34-35) | T087 net -0.036% t -1.72 (L148); T055-C2 rerun +0.0177% 1 of 2 years positive (L150); C3 no edge (L151); EUR-low sweeps blocked by power gate (L145) | B102 (no DST), B187 | levels, Krown |
| volume_candles_ma | Volume, candle patterns, daily MA, bigtrade (L159) | `FORMULAS.md` (L182) | ma_daily numbers NO-SOURCE, from a chatbot handoff (L164) | VOLUME no validated edge, volume HOLDOUT sealed (L169, L162); ALPHA labelled NO-SOURCE (L168) | B163 (the chatbot handoff) | context |
| callers | Posted trade calls: Qriptal, RLinda, Bennett, Crypto Chase, Roman (L208) | B162 item, analysts REVIEW (L211) | NOT_IN_DATA | none; self-reported 67.1% wins, avg win 3.99%, avg loss 0.63%, unverified (L209) | B139 | JUDGE role |
| krown | TA 101 zones, volume, candles, averages, ranges (L221) | `KROWN_LAYER_SPEC.md`, `PRE_REG_KROWN.md` (L224) | one structural stop; stop distance and size are OURS (L222) | none: no DEV event study (L222, LAYER_REALITY:13) | B141; detector recall 3 of 12 (LAYER_REALITY:13) | CONTEXT slot (design:20) |
| wavetrend | LazyBear oscillator (L243) | `PARITY_CONTRACT.md`, `ATLAS_STUDY_SPEC.md` (L246) | NOT_IN_DATA | W01-03, W09 FAIL; W04-08 INCONCLUSIVE; W07/W08 use an invalid detector (L244) | invalid C1 detector (L244) | RSI |
| pitchfork | Andrews / Schiff / Morge median line (L256) | papers 01-03 (L260) | NOT_IN_DATA | none recorded; detector with unit tests (L259) | studies span 2020-2026, not DEV-only (LAYER_REALITY:18) | levels |
| live_engine | Engine, execution, live reads; feeds every layer (L191) | `live_session_protocol.md` (L194) | proof bands 3 and 5, net_rr floor 1.25, min stop floors are NO-SOURCE (BUGS.md:228,264,227) | no backtest row | B075, B081, B116-B118, B136, T085 | all |

## Stale statements found while reading (facts, not decisions)
- `LAYERS.md:222` says Krown detectors are "not built, not backtested"; `LAYER_REALITY:13` says detectors S1-S9 exist with 49 tests and a failed recall check; `sim_desk/studies/krown.py` exists. LAYERS.md is generated, so the status text needs a source fix (NOT_IN_DATA where).
- `LAYERS.md:222` says "120-rule ledger from 15 of 19 videos"; LAYER_REALITY:13 says 127 rules from 16 of 20.
- 13 `lf-*-gemini-facts` and 13 `lf-*-gpt-rederive` cards are open (LAYERS.md lines 32-33, 64-65, ...), so every sheet above has a second, independent fact sheet coming.

## What each family offers a combined rule (OURS, no judgement of worth)
| Slot | Families that could fill it | Standalone test status |
|---|---|---|
| CONTEXT | krown (trend, volatility, structure), positioning, volume_candles_ma | none passed S3 |
| REGIME | rsi levels, wavetrend, krown BBWP | none passed S3 |
| LOCATION | levels layers, cryptocred, pitchfork, habib | levels: DEV done, VALIDATION never read (LAYER_REALITY:16) |
| TRIGGER | tom, fabio, session_timing, rsi divergence | none positive fee-net on DEV (LAYER_REALITY:3) |
| RISK | krown (part), sourced exits | no non-core layer has a sourced exit (provenance:40) |
| JUDGE | callers | scorecard unverified (L209) |
