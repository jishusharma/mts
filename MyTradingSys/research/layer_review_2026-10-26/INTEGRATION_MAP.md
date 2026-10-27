# Layer integration map and confluence rule (Lead, 2026-10-26) - DRAFT 1
Card: layer-review-after-simulator. Docs only. No layer is kept, dropped, demoted or parked here: the operator said NO to that until he has reviewed each layer in the simulator (MAINNET_PATH_2026-10-25.md:34).
Labels: SOURCED = file:line opened this session. OURS = my design choice. NOT_IN_DATA = repo does not say; the command that would find it is given.
Status: draft 2. All earlier [LINE NOT RE-OPENED] rows were re-checked on 2026-10-26 and now carry file:line. The per-parameter provenance tables and the full errors register are NOT copied here; see "Not done yet".
layer_facts sheets (NUC Gemini lane): none on trunk when this was written (NOT_IN_DATA; find with `git ls-tree -r origin/fast-track --name-only | grep layer_facts`). Each sheet gets one reconciliation row per layer when it lands; Claude reviews it, the producer does not.

## 1. How the layers combine today
- Nothing combines on a live trade. `promoted_setups.json` ships empty (LAYER_REALITY_2026-10-25.md:2; MAINNET_PATH_2026-10-25.md:8). So no confluence rule has ever decided a real trade.
- Governance: a layer gates another only after it passes S3 (a standalone read) alone (LAYER_REALITY:36, step 12). Until then confluence is alert-only tags (PROJECT_VISION.md:262: "Confluence may gate a trade only after each input passed S3 on its own").
- The independent review found the Krown design broke that rule: it said "gate only after 5", and the Krown context has had no independent read, so the context is a tag only until it gets its own S3-style read or the operator signs an amendment to line 262 (`krown_audit_2026-10-22/REVIEW_OPUS.md:23`, finding F5).
- Designed, not tested: roles instead of votes - CONTEXT, REGIME, LOCATION, TRIGGER, RISK, JUDGE; one layer per role, and layers that compute the same object count once (`LAYER_CONFLUENCE_DESIGN.md:18-19,49`). Example same-object pair: Malkan's daily-60 sell and Krown's RSI regime (`:37`). Today every live adapter is a TRIGGER firing alone (`:20`). Pre-registered family: Holm m = 18, z 2.991 (`PRE_REG_CONFLUENCE.md:35,44`).
- Tested so far: one prior context study, INCONCLUSIVE (`LAYER_CONFLUENCE_DESIGN.md:134`, pointing at `research/context_factors_2026-10-16/RESULT.md`); cross-guidance Q33, no cell survives (LAYER_REALITY:22).

## 2. Per layer: recorded state (the repo's classes, not my decisions)
Class = the doctor's label in LAYER_REALITY, not an operator decision. "Role" = my reading of where the layer would sit in the role slots (OURS, untested).
| Layer | Recorded class | Evidence (SOURCED) | Role slot (OURS) | In simulator? |
|---|---|---|---|---|
| Tom (old BTC encoding) | DEAD; v2 LAGGING-BUILD | holdout -0.32 R, n=254 (LAYER_REALITY:7) | CONTEXT/TRIGGER, v2 undefined | no |
| Fabio (cvd_absorption, escalation, volume_fvg, v3) | DEAD encodings; LAGGING-PARITY | v3 OOS 79 trades -0.1038 R; volume_fvg side inverted 0/24 (:8) | TRIGGER | no |
| CryptoCred (sr_flip, fib_pullback, failed_msb) | DEAD as tested; exits LAGGING-PARITY | stop/target unsourced (:9) | LOCATION/TRIGGER | no |
| RSI 40/60 levels (Malkan) | LAGGING-PARITY | live event set differs from tested set (:10) | REGIME | yes (rsi study) |
| RSI divergence | DEAD | 31 of 32 net negative (:11) | TRIGGER | yes (rsi study) |
| Kurisko Quad Rotation | LAGGING-TEST | fee 2.1-2.3 R on 1m (:12) | TRIGGER | no |
| Krown | LAGGING-TEST | 127 rules, detectors built, recall 3 of 12 (:13) | CONTEXT (higher-timeframe) | yes: `sim_desk/studies/krown.py` exists (Glob 2026-10-26); LAYER_REALITY:28 lists only three, so that note is stale |
| WaveTrend | LAGGING-TEST | none passes gross screen (:14) | REGIME/TRIGGER | yes |
| Habib | LAGGING-BUILD | needs his typed level prices (:15) | LOCATION | no |
| Levels-confluence | DEAD on DEV, provisional | frozen -0.039 R, n 772; VALIDATION never read (:16) | LOCATION | yes |
| Funding/CVD fade | DEAD | OOS net -0.0453%; live 1h vs test 15m (:17) | CONTEXT | no |
| Pitchfork | LAGGING-TEST | no VERDICTS row, no DEV-only rerun (:18) | LOCATION | no |
| Trend-line | LAGGING-TEST | audit FIX-FIRST, 0 of 40 blind marks (:19) | LOCATION | no |
| session_momentum, turn_of_candle | DEAD (parity good) | turn_of_candle = 71% of live alerts (:20) | TRIGGER | no |
| session levels, candle_close, wlow_bounce, bb_top_reversal, fabio v3_grid | DEAD (provisional) | parity not diffed (:21) | various | no |
| Cross-guidance, volume, candle patterns, ma_daily, bigtrade | DEAD | no cell survives (:22) | CONTEXT | no |
| Callers (Qriptal, RLinda, Bennett, Crypto Chase, Roman) | LAGGING-TEST | 67.1% self-reported wins unverified (:23) | JUDGE input | no |

## 3. What the old backtests got wrong (only items in hand this session)
| Item | Category | Evidence | Fixed? |
|---|---|---|---|
| 94% of live exits are time exits; the 1%/2%/8-bar bracket was never backtested, so live and tested numbers are not comparable for any layer | ASSUMPTION/BUG (parity) | LAYER_REALITY:26; MAINNET_PATH:9 | Open: card t09-f2 claimed (MAINNET_PATH:17) |
| volume_fvg side inverted (0 of 24) | BUG | LAYER_REALITY:8 | card t09-f1 (:8) |
| RSI live trades events no backtest covered (384 of 461 on 5m) | BUG (parity) | LAYER_REALITY:10 | card t09-f3 ready |
| Funding/CVD tested on 15m, live on 1h, 0 of 34 coincide | BUG (timeframe) | LAYER_REALITY:17 | card positioning-c1 raw |
| CryptoCred stop and target unsourced; 15m never backtested | UNVETTED_PARAM | LAYER_REALITY:9 | open |
| WaveTrend divergence detector wrong (W07/W08 invalid) | BUG | LAYER_REALITY:14 | card wavetrend-c1-v2 |
| Tom V1: 32 extracts fail the quote check; 26 of 84 transcripts never extracted | FABRICATION risk | LAYER_REALITY:7 | open |
| Pitchfork studies span 2020-2026, not DEV-only | UNVETTED_PARAM (data window) | LAYER_REALITY:18 | open |
| Levels-confluence: VALIDATION read never done, so the DEAD label rests on DEV only | ASSUMPTION | LAYER_REALITY:16 | card lc-validation |
| Provenance: 17 SOURCED / 34 CONCEPT-ONLY / 30 NO-SOURCE parameters; no non-core layer has a sourced exit | UNVETTED_PARAM | `LAYER_PROVENANCE_AUDIT.md:38` (81 rows) and `:40-42` (no sourced exit; CryptoCred's 1.5:1 and 2:1 minimum filters used as fixed targets) | open |
Effect on the labels: every DEAD label above was set on a generic exit, a mismatched event set, or DEV only. Whether correcting these flips any label is NOT_IN_DATA; the corrected numbers were never computed.

## 4. The confluence rule (OURS, proposed, nothing tested)
A trade fires only when all five hold, in this order. Every threshold N is OURS and set only on DEV.
1. CONTEXT and REGIME layers agree on direction (higher timeframe first).
2. A LOCATION layer marks a price level within a set distance.
3. A TRIGGER layer fires on that side within N bars after (2).
4. Layers that read the same object (e.g. two RSI event types) count once.
5. Each layer used has passed S3 alone (LAYER_REALITY:36). Before that, steps 1-4 only tag alerts.
Exit: the layer's own sourced exit where one exists (none for non-core layers, see section 3); otherwise the generic bracket, stated as such.

## 5. Two ways to find which layers confirm each other
| | A. Role-slot confluence (Krown v2 design) | B. Pair discovery in the simulator |
|---|---|---|
| What | Pre-registered S3, S4, S5; Holm m=18 | Use the existing post-filter `layer_b` ("layer_b fired within last N bars", `sim_desk/conditions.py:16-17,27,41-43`) on DEV for pairs among the plug-in layers |
| Cost (OURS) | Days: needs S3 results for every input first | Hours per pair; tool exists |
| Payoff | A defensible rule for live gating | A first look at which pairs show any agreement lift, to feed A |
| Risk | Most inputs have no S3 yet, so it waits | Many pairs on one DEV window inflates false positives; every pair must go in the trial ledger and under the placebo and Holm rules |
Recommendation (OURS): run B on the three simulator layers first, ledgered, then use the survivors as S3 inputs for A. Under 30 trades = NOT ENOUGH DATA (`sim_desk/desk.py:33,198`). Note the provenance total is 17 SOURCED / 34 CONCEPT-ONLY / 30 NO-SOURCE across 81 rows, not counting 19 plumbing rows.

## Not done yet
- Per-layer idea/source/parameter sheets (needs `LAYER_PROVENANCE_AUDIT.md` tables and `LAYERS.md`; I stopped 16 agents that had written no rows).
- Full errors register (BUGS.md, DSA audits T01-T10, lab reports).
- layer_facts reconciliation (13 `lf-*-gemini-facts` cards re-running on the NUC; review each `gemini-q/lf-*` branch as it lands).
