# Gap hunt iteration 3: merged index (2026-11-13)

Inputs: 14 Gemini outputs in `MyTradingSys/research/tf_iteration3_1113/` (flash and argon) over 9 topics, merged into one file per topic in `ITERATION_3/`. Brief and the 5 patterns: `tf_iteration3_1113/BRIEF.md`. Iteration 2 reference: `ITERATION_2.md`. No code change, no backtest, no card.
Folder fix done first: `market-profile/argon.md` moved to `market_profile/argon.md` with `git mv` (not committed).

How rows were merged (read before trusting a count):
- A flash row and an argon row are one item (AGREED) when they cite the same video id and share a 5-word run of the quote, or (second pass) share at least 20% of the distinctive words of rule plus topic. Management was also paired by hand per concept (BE, trail, partials, targets, exit on a failed auction), because the two models quoted different lines for the same rule. Concept agreement with different quotes elsewhere can still sit as two SINGLE rows, so AGREED is a floor.
- Topics run on one model only (code_vs_rulebook, i2_refute, other_layers: argon; conceptualizer_audit, crypto: flash) have no AGREED row by construction.
- Pattern, ledger and fix-type columns are first-pass labels set by rule from the source rows (code column, numbers, transfer words, the model's own tags); the ledger column matches video id plus three shared content words against `out/tf-s1-answer-ledger-1113/ANSWER_LEDGER.md`. They are a sort aid, not a re-read.
- Quotes: every quote in the topic files was re-checked against `raw_transcripts_canonical/<id>_raw.txt` by `verify_extract_quotes.py` (exit 0 on all 9). A model quote that failed was cut to its longest sentence that does occur; where nothing occurred the row says UNVERIFIED.

## 1. Counts and gate per topic

| topic | models | rows | AGREED | SINGLE | CONFLICT | UNVERIFIED | verified quotes | gate exit |
|---|---|---|---|---|---|---|---|---|
| balance_shape | flash+argon | 48 | 13 | 34 | 1 | 0 | 27 | 0 |
| code_vs_rulebook | argon only | 35 | 0 | 35 | 0 | 0 | 13 | 0 |
| conceptualizer_audit | flash only | 15 | 0 | 15 | 0 | 0 | 4 | 0 |
| crypto | flash only | 23 | 0 | 23 | 0 | 0 | 12 | 0 |
| i2_refute | argon only | 25 | 0 | 25 | 0 | 0 | 10 | 0 |
| management | flash+argon | 31 | 7 | 22 | 2 | 0 | 17 | 0 |
| market_profile | flash+argon | 100 | 20 | 80 | 0 | 0 | 54 | 0 |
| ny_open | flash+argon | 49 | 9 | 39 | 1 | 0 | 30 | 0 |
| other_layers | argon only | 20 | 0 | 20 | 0 | 1 | 17 | 0 |
| **total** | | 346 | 49 | 293 | 4 | 1 | 184 | |

UNVERIFIED (1): OL-05 (Malkan buy-stop quote). The quote exists only in `W1HrDl70Lhk_asr_raw.txt`; the gate reads `W1HrDl70Lhk_raw.txt`, where it is absent. Needs a decision on which caption variant counts.

## 2. CONFLICT list (all need a third check)

| id | topic | the two claims | who or what checks |
|---|---|---|---|
| BS-49 | balance_shape | Flash: neither trader says D-shape or b-shape. Argon: Tom names D, P and B profiles in 20+ videos. | Settled in this merge by grep of the base transcripts: "D profile" in 17 files, "B profile" in 5, "P profile" in 6, "b-shape" and "D shape" in 0. Both right on the literal word, Argon right on the concept. Lead confirms by reading `m3IMdc7QwN4` (quote in the topic file). |
| MG-08 | management | Argon: Tom does not trail a clean planned target (about 6:1). Flash: always trail behind structure. | Speaker split (Tom vs Fabio ASR), not a fact error. A third reader lists every trail line per trader in `k0zm5NYn0IQ`, `UOBgXV20yCM`, `Is1HvdfQm5c`, `e83njGZFrPw`. Iteration 2 Q6 already says per-trade choice. |
| MG-11 | management | Argon: hold the full target when well up on the day. Flash: take partials rather than wait for 1:20-1:30. | Third reader checks the day P&L state at both passages (`8CWKfoSJu3c`, `DyS79Eb92Ug`); likely a P&L-keyed rule neither model states. |
| NY-12 | ny_open | Argon: opening-range window 15 to 30 minutes. Flash: 15, 30 or 60 minutes. | Lead reads `cUTsoU-15Tc` around [2:10] and [4:26]; the 60-minute option is in the flash quote (verified). Our IB_LEN = 30 stays OURS either way. |

Also noted, not a model conflict: Fabio's own numbers differ for the value area, 68% (`Pz8f0wWW12M`, BS-04) against 70% (`o-w5Gxss6T0`, BS-06); our `VA_PCT = 0.70` matches only the second.

Single-model refutations that overturn an iteration-2 gap and have no second model: IR-01, IR-05, IR-08, IR-09, IR-14, IR-18, IR-19, IR-23 (argon only; `i2_refute.md`). They need a second reader before ITERATION_2.md is amended. Argon's headline for them: iteration 2 treated Tom and Fabio as one rulebook, but each contradicts himself or the other across videos (30-minute skip vs 15-minute ORB, 1m vs range bars, trail vs no trail, London skipped vs traded).

## 3. Top 10 items (AGREED first, then new against iteration 2)

| rank | id | item | new vs iteration 2 |
|---|---|---|---|
| 1 | MP-47 | Buying or selling tail = at least 3 single TPO letters alone at the extreme | Yes: iteration 2 had only a tail quote, no rule or number |
| 2 | MP-35, MP-41 | Single print = one 30-minute letter; several single prints veto counter-trend VWAP fades | Yes: single prints not separated in I2-10 |
| 3 | MP-06 | Time-based POC = price touched by most 30-minute blocks (basis for the time-vs-volume POC anomaly) | Yes |
| 4 | BS-20 | Fabio P-shape: POC above 50% of the daily range, thin absorbed low below | Yes: first stated number for a shape |
| 5 | BS-38 | Out of balance only when both price and volume accept outside VAH or VAL | Partly: I2-09 has acceptance, not the volume half |
| 6 | NY-23 | Big-trade bubble 20 contracts in London, 30 in New York (session-dependent) | Yes: I2-06 only had the 60 filter |
| 7 | BS-36 | Merge overlapping daily profiles into a 2 to 3 day composite balance | Yes |
| 8 | NY-05, NY-07 | Narrow 30-minute opening range = trend day; very large = will not hold | Partly: I2-07 names opening-range size, no direction rule |
| 9 | MP-10 | Daily close inside or outside the market-profile value area flags a structural shift | Partly: I2-09 |
| 10 | MG-09 | Partials at liquidity clusters or resistance, runner stays | Partly: I2-12 |

Open as a CONFLICT, not ranked: BS-49 (D/P/B vocabulary; our Java `shape` emits P for any skew, so a b-profile never appears).

## 4. New pattern-2 holes (concept in 10+ videos, never coded)

Method: case-insensitive grep over the 161 base transcripts (the `_asr_` and `_hi_` variants excluded); code check = `git grep` of the term over `MyTradingSys/backtest`, `MyTradingSys/tools/live_aid`, the course-correction folder and `src`, noise hits (trade ledger, `topLongShort...`) removed by hand.

| concept | videos | code | in iteration 2 | verdict |
|---|---|---|---|---|
| single prints | 35 | 0 files | named only inside I2-10 | NEW hole (extracted in market_profile MP-35 to MP-46 and MP-62 to MP-82; coding next) |
| buying and selling tails | 14 | 0 files | one quote only | NEW hole (MP-47 to MP-52, MP-63 to MP-66) |
| hedging | 15 (14 without sponsor copy) | 0 files | listed, no definition | STILL OPEN: no iteration 3 topic covered it |
| P, B, D profile letters | D 17, P 6, B 5 (phrase counts) | Java `shape` emits P and D by volume ratio, not his method | listed (distribution, 15) | known, coded as a different thing (pattern 4) |
| weak highs, lows, ledgers | 8 | 0 | no | below 10 |
| initial balance | 7 | Model C only | partly | below 10 |
| double distribution (exact phrase) | 3 | 0 | listed | below 10 by phrase |
| VPOC migration | 4 | 1 | partly | below 10 |

## 5. Stopping rule for iteration 4

**ITERATION 4: GO, narrow.** Reason: the rule fires on holes with no extraction yet. Single prints (35 videos) and tails (14) are new holes, but iteration 3 already extracted them, so their next step is coding and tests, not another hunt. Hedging (15 videos, 0 code, no definition, not covered by any of the 9 topics) is still open, and 5 of the 9 topics ran on one model only, so their SINGLE rows lack a second reader. Scope for iteration 4: (1) hedging, every video that names it, what he says it is and the trade it feeds; (2) a second model on code_vs_rulebook, conceptualizer_audit, crypto, i2_refute, other_layers; (3) the third checks in section 2. Stop after that unless it returns a new 10-video hole.
