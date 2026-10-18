# TRENDLINE_CONTRACT.md: causal trend-line detector contract (v1, 2026-10-17)

Card `trendline-contract-spec`. Spec only: no code, no market data read, no backtest, no VALIDATION/HOLDOUT read. Two coders reading this must write the same detector. Formulas with hand-computed numbers: `backtest/layers/FORMULAS.md` section 19.

Labels (CLAUDE.md "Numbers"): **SOURCED** = the trader's or a named source's words (quote + file:line); **OURS** = our judgement, fixed here once, not tuned, not Krown's. Any later change is a new contract version plus a trial-ledger line. Sensitivity arms are listed per row; they are trial-ledger variants, not alternative primaries.

Source files (paths from repo root):
- `E` = `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_14bxwxC8gBQ.md` (Krown, video 14bxwxC8gBQ; extract ids K-14bxwxC8gBQ-nn = rule-source ids TRL-nn in KROWN_RULES.csv). Quotes below are verbatim from `E` (`verify_extract_quotes.py` PASS, see Verification).
- `R` = `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` (rows named by rule_id; a row is one CSV line, cited as `R:KR-xx`).
- `F` = `MyTradingSys/backtest/layers/FORMULAS.md`.

## 1. Frame

| # | Parameter | Value | Tag | Source / reason |
|---|---|---|---|---|
| F1 | Instrument and venue | Binance USD-M BTCUSDT perpetual, OHLCV from the repo kline store; spot lines are a separate tag, never mixed | OURS | REPORT.md line 54 and 89 (repo target) |
| F2 | Time | UTC; bar stamped by open time; a bar exists to the detector only after its close | OURS | REPORT.md line 55 |
| F3 | Line timeframe (LTF) set | 1h, 4h, 1d, each its own detector instance; no cross-TF pooling of lines | OURS | Krown: "it is timeframe dependent" (`E:71`); 1m excluded until data and power audit (REPORT.md line 79) |
| F4 | Trigger timeframe | equals LTF in the primary arm; a lower trigger TF (1m) is a separate study; store `line_tf` and `trigger_tf` as two fields | OURS | REPORT.md line 79 |
| F5 | Data stage | construction, counts and arm selection on DEV only: 2022-01-01..2024-06-30 (DEV_EXT 2020-01-01..2021-12-31 allowed for DEV-stage reads only). VALIDATION 2024-07-01..2025-06-30 and HOLDOUT are not touched by this contract or by the module card's tests. Old bigtrade TRAIN/TEST labels are not inherited. Every DEV read gets an EXPOSURE_LEDGER line | OURS | `MyTradingSys/system/OPERATOR_DECISIONS.md:883`; CLAUDE_VERIFY.md section (c) |
| F6 | Bar aggregation | reuse `layers/timeframe/tf_resample.py` (closed-bar resample, real-data gate); no new resampler | OURS | CLAUDE_VERIFY.md (b) |

## 2. Pivots (anchors)

| # | Parameter | Value | Tag | Source / reason |
|---|---|---|---|---|
| P1 | Anchors only on confirmed swings | yes | SOURCED | "a trend line may only be anchored to swing points or swing highs and swing lows a confirmed high or a confirmed low" (`E:44`) |
| P2 | Swing definition shape | swing low = low with strictly higher lows on both sides; swing high mirror | SOURCED | "a swing low is effectively a low with higher lows on both sides" (`E:53`) |
| P3 | Bars each side, k | **k = 3** (primary). Sensitivity arms k=2 and k=5 | OURS | Krown gives no bar count (`R:KR-L01` params "bars on each side not given"). Existing repo default is 2 (`layers/cryptocred/cc_structure.py:11`); 3 chosen so a swing needs a visible turn on the 1h and 4h. Not tuned |
| P4 | Ties | strict inequality on both sides. A bar equal to the candidate within the k window on either side disqualifies it, for both candidate bars (equal double bottoms yield no pivot). Logged as `reject=tie` | OURS | follows "higher lows" (`E:53`); the conservative reading avoids choosing which of two equal bars is the anchor |
| P5 | Price used for the pivot | wick arm (primary): low for swing lows, high for swing highs. Close arm (secondary, separate line ids): close series with the same k and tie rule | OURS | Krown looks at a line chart (closes): "putting your chart on a line chart" (`E:62`) but breaks on the "wick low of ... a major higher low" (`E:225`). Both stay arms (`R:KR-L01` "arm: swings on closes versus highs and lows") |
| P6 | Availability time | pivot at bar i is known only from the close of bar i+k, never earlier. Anchors are immutable once available | SOURCED (lag shape) + OURS (value) | `R:KR-Z05` "confirm_lag >= 1 bar"; "just because it's in hindsight doesn't mean that it can't be pulled forward" (`E:73`) allows use only forward. k=3 is OURS (P3) |
| P7 | Unfinished ZigZag leg | never an anchor | OURS | REPORT.md line 56 |
| P8 | Obvious swings only? | not applied in the mechanical detector. "If it ain't obvious it's probably not a trend line" (`E:35`) is an eye-read concept: it is handled by the G3 marks pack (`trendline-g3-marks-pack`), not by a parameter here | SOURCED (concept), OURS (deferral) | CLAUDE_VERIFY.md (d) |

## 3. Candidate lines (anchor pairs)

Let b be the newly available pivot, a an earlier same-side available pivot, bar indices ia < ib, prices pa, pb (wick arm prices).

| # | Parameter | Value | Tag | Source / reason |
|---|---|---|---|---|
| L1 | Pairing | on each new pivot b, form a candidate with every earlier same-side pivot a satisfying L2-L5, filtered by L6 | OURS | REPORT.md line 56 |
| L2 | Direction | support: swing lows with pb > pa (rising). Resistance: swing highs with pb < pa (falling). Flat pairs are routed to horizontal controls (L7) | OURS | REPORT.md line 56; Fidelity "join rising lows or falling highs" (REPORT.md line 17) |
| L3 | Minimum anchor spacing | ib - ia >= 10 bars | OURS | StockCharts: spacing matters (REPORT.md line 18); value not stated by anyone |
| L4 | Maximum anchor spacing | ib - ia <= 200 bars | OURS | `R:KR-T01` "min_periods=200" is the history Krown wants, reused as a window cap |
| L5 | Maximum line age | line retired when t - ib > 500 bars (t = current bar index); arm: no cap | OURS | `R:KR-T01` "ideal_periods=500" (SOURCED number reused as a cap = OURS use); `R:KR-Z06` states no expiry, so the cap is the OURS arm named there ("optional OURS arm: maximum age") and the no-cap run is mandatory as a second arm |
| L6 | Strict (external) penetration test | tested once, at availability of b, over bars ia..ib only (later bars are governed by E5-E7 and B1, so a later break never voids a ledger row, see B8). For support: every bar j has low[j] >= L(j) - 0.10 * ATR_b and close[j] >= L(j) (mirror for resistance). A line failing the test is not eligible and is logged `reject=penetration` | OURS | "the left line slices through the candle ... it's bent to fit it has to break" (`E:126`); "slices through" needs a tolerance (`R:KR-L05` blocker). Tolerance 0.10 ATR is OURS |
| L7 | Flat pair | if abs(pb - pa) <= 0.25 * ATR_b the pair is horizontal and goes to the horizontal-control family only | OURS | Horizontals matter more: "flat trend lines horizontal trend lines ... are actually the most important" (`E:167`); threshold OURS |
| L8 | Transform | log price (primary); linear is a separate-id arm. L(t) formulas in F section 19.2 | OURS | REPORT.md line 67 (different geometries) |
| L9 | No regression lines | line passes exactly through the two anchors; never refit | SOURCED | "we don't want to fit like a regression trend lines that's not gonna matter" (`E:128`) |
| L10 | Versioning | a line is (side, ia, ib, transform, price arm); version 1 at availability of b. A new anchor makes a new line id; old lines are never moved. State is append-only | OURS | REPORT.md line 57 |
| L11 | Selector for "the" line | nearest eligible line on the relevant side, measured as abs(close - L(t)) at the decision bar; ties go to the newer ib, then the newer ia. All candidates stay in the ledger | OURS | REPORT.md line 59 |

ATR_b = ATR(14) at the close of bar ib, fixed for the line version (plain SMA of True Range, F section 12, not Wilder). Length 14 is OURS (Krown gives no ATR). Also store the current ATR separately for features.

## 4. Eligibility: "two points are a hypothesis, three touches a trend"

Krown's KR-L02 has two readings; each is its own arm and its own line family label `arm`.

| # | Parameter | Value | Tag | Source / reason |
|---|---|---|---|---|
| E1 | Quote | "two points draw a line but two points is basically a hypothesis" (`E:80`); "what makes this a trend is three touches three touches makes it a trend" (`E:82`) | SOURCED | `R:KR-L02` touches=3 |
| E2 | Arm A (2 anchors + 1 test) | line becomes eligible at the end of the first contact episode after ib that satisfies E5. Eligibility time = the first bar where the episode is closed by distance-away reset (E6), not the contact bar | OURS reading of E1 | REPORT.md line 58: validation becomes knowable after first contact; never credit it to an earlier entry |
| E3 | Arm B (3 anchors) | a third available same-side pivot c (ic > ib) whose price lies within 0.25 * ATR_b of L(ic); eligible at the availability time of c (close of ic+3). Anchors a, b, c are all pivots | OURS reading of E1 | reading C1 with `R:KR-Z13` (tests: more tests weaken); both arms stay |
| E4 | Arm V (volume early line) | two anchors eligible immediately if both anchor bars have volume >= 2.0 x mean(volume of the 20 bars before the anchor bar) | SOURCED multiplier 2 and "recent bars" = 20 (`R:KR-V02` vol_mult=2 of the 20-period average, VOL-09); "double or more the recent volume bars around those lows or highs" (`E:93`) | "around" is read causally as the 20 bars before the anchor (no future bars): OURS. Baseline 30-day arm from `R:KR-V02` is a named sensitivity arm |
| E5 | What counts as a touch (contact) | bar j > ib with low[j] <= L(j) + 0.25 * ATR_b (support; mirror for resistance) and close[j] >= L(j) (no break, see B1) | OURS | tolerance: `R:KR-L05` blocker, `R:KR-L02` gives no tolerance |
| E6 | Contact episode and distance-away reset | an episode starts at the first contact bar and continues while contacts continue. It ends when a bar's low > L(j) + 1.0 * ATR_b (support; mirror). A cluster of candles riding the line is one episode. A contact after the reset is a new episode | OURS | REPORT.md line 58 requires a declared reset; 1.0 ATR OURS |
| E7 | Poke | a bar with low < L(j) - 0.10 ATR_b but close >= L(j) is a poke (stop harvest), a contact, not a break; logged `poke` | SOURCED shape | "an intrabar poke that snaps back is a stop harvest, not a break" (`R:KR-Z07`); thresholds OURS |
| E9 | Gap bars in an episode | a bar with L+0.25 ATR_b < low <= L+1.0 ATR_b is neither a contact nor a reset: it neither starts nor ends an episode and keeps an open episode open | OURS | closes the E5/E6 gap |
| E10 | Break before reset | a break (B1) during an open episode ends it as a failed test: arm A never becomes eligible and the line goes to `broken` without `eligible` | OURS | |
| E11 | Pivots after a break | a pivot b' formed after a line's break may not pair with that line's anchors (a broken line is not extended); pairing with other available pivots is unchanged | OURS | |
| P9 | Series edges | a bar with fewer than k bars on either side inside the series is never a pivot; ATR needs 14 bars of TR (first TR at bar 1), so no line before bar 15 | OURS | |
| E8 | Minimum touches after eligibility | none; contact count is a feature (episodes counted, anchors excluded), not a gate | OURS | REPORT.md line 83: contact-count comparisons need survival treatment, not gating |

## 5. Break, retest, lifecycle

| # | Parameter | Value | Tag | Source / reason |
|---|---|---|---|---|
| B1 | Break | the first bar whose **close** is beyond L(t): close < L(t) for support, close > L(t) for resistance | SOURCED | "when you close below the wick low of in this case a major higher low" (`E:225`); `R:KR-Z07` "close beyond outer boundary" (applied to a line); `R:KR-L09` |
| B2 | Break margin | 0 (any close beyond the line). Sensitivity arm: close beyond by >= 0.10 ATR_b | OURS | Krown states no margin |
| B3 | Which timeframe's close | the line's own timeframe | OURS | `R:KR-Z07` blocker: "OURS = the zone's own timeframe" |
| B4 | Break features (entry-time safe) | distance beyond line / ATR_b; body / range; close location = (close - low) / (high - low); volume / mean(20 prior bars); distance to nearest horizontal level (when the zone module exists) | OURS | REPORT.md line 71; "clean candle" thresholds not set here (no gate on them) |
| B5 | Follow-through and snapback | outcomes only, never entry features. Defined in the count/PRE_REG cards | OURS | `R:KR-L06` follow-through size not given; REPORT.md line 73 |
| B6 | Retest | after a break, retest = a bar within the next 20 bars of the line's TF whose extreme returns to within 0.25 ATR_b of L(t) from the broken side. Reclaim = a close back on the original side of the line. Both are outcome labels with their own timestamps | OURS | "the same line you were vying against becomes the ceiling or resistance" (`E:178`); window 20 OURS |
| B7 | States | proposed, eligible, touched, broken, retested, reclaimed, retired; transitions append-only, each row timestamped to the bar close that caused it | OURS | REPORT.md line 57 |
| B8 | Broken line | stays in the ledger as broken; it is not retired at break, and role flip is recorded as the retest event | SOURCED shape | "a break is not your line failing it's the market telling you the trend is changing" (`E:176`) |

## 6. Slope (no degrees)

| # | Parameter | Value | Tag | Source / reason |
|---|---|---|---|---|
| S1 | Degrees | not implemented. Krown's "four to five degree angle" (`E:153`) depends on chart scaling; `R:KR-L07` is BLOCKED | SOURCED (stated) / not used | `R:KR-L07` |
| S2 | Slope measures stored | (a) slope_atr = (L(ib) - L(ia)) / (ib - ia) / ATR_b, linear price per bar over ATR, fixed at creation; (b) slope_log = (ln pb - ln pa) / (ib - ia) per bar; (c) percent per bar derived from (b) | OURS | REPORT.md line 69; compared within a timeframe only |
| S3 | ATR | length 14, plain SMA of TR | OURS | `F` section 12 (operator 2026-09-28, plain SMA) |

## 7. Truncation (repaint) test cases for the module card

The module is causal iff the line set at decision bar t, computed on data cut at t, equals the same set computed on all data and read at t. Cases (each a unit test; expected values from F section 19, not from code):
1. Cut at ib+k-1: pivot b absent; cut at ib+k: pivot b present with `available_at = close(ib+k)`.
2. Tie pivot (equal lows within the k window): no pivot in either cut.
3. Penetration appearing after the line was drawn: the old line row is unchanged; a `broken` event appears at the break bar only.
4. A third pivot appearing later does not alter earlier lines (arm B creates a new eligibility event, not a new anchor on the old line).
5. Contact episode: one cluster of 3 consecutive contact bars counts 1; after a bar with low > L + 1.0 ATR_b a new contact counts as the 2nd.
6. ATR_b fixed: a later ATR spike leaves slope_atr of an existing version unchanged.
7. Cut at the exact bar of eligibility vs one bar before (arm A: eligibility at reset bar, not at contact bar).
8. Log versus linear ids differ for the same anchors and never collapse.
9. Empty and short series (fewer than 2k+1 bars, fewer than 14 bars for ATR): no pivots / no line, no exception.

## 8. Daily-ledger schema fix (`daily/ledger.jsonl`, schema version 2)

Fixes the gaps in CLAUDE_VERIFY.md (b): first observed was a run window, not per post; no content hash; selection rule applied loosely; image-read geometry counted as lines.

| Field | Value | Tag |
|---|---|---|
| `captured_utc` | UTC time the specific post page/chart was opened (per post, not per run) | OURS |
| `content_sha256` | sha256 of the captured text/metadata snapshot (UTF-8, sorted-key JSON, compact separators) and, when an image is saved, `image_sha256` of its bytes. A later edit is a new record with a new hash and `supersedes` = old id | OURS |
| `selection_string` | the exact string matched in the title/preview text (case-insensitive) that made the post eligible, e.g. `trendline`, `trend line`, `channel`, `triangle`, `wedge`, `diagonal`; null and `eligible=false` when no string matches. The list is fixed in `daily/SELECTION_STRINGS.txt` before outcomes | OURS |
| `selection_list_version` | version of that list | OURS |
| `geometry_source` | `none` / `author_coordinates` / `reader_marks`. `image_read` lines (geometry read off a picture) get `geometry_status=unscored` and are excluded from every line count until two readers agree under `research/layer_rebuild_2026-10-15/READER_PROTOCOL.md` (then `reader_agreed`) | OURS |
| `record_sha256` | sha256 of the record without this field, serialised with `json.dumps(sort_keys=True, separators=(",", ":"))`, UTF-8. (Verified 4/4 on the current ledger; default separators do NOT match.) A self-hash: tamper-evident only against casual edits | OURS |
| kept fields | `id, author, instrument, timeframe, published_ist, update_ist, observation_date, anchors, equation, price_transform, touches, status, outcomes_scored, geometry_gap, receipt` | unchanged |
| popularity | stored with label and capture time only; never a selection variable | OURS |

Rule: a record with `geometry_status != reader_agreed` and `geometry_source != author_coordinates` carries `eligible=false`, `NOT_IN_DATA`, and is not a line.

## 9. Zero-unset check

Every row above has a value and a tag. Parameters with no external number (k, tolerances, spacing, age, reset, ATR length, windows) are OURS and fixed once. The only Krown-numbers used are touches=3/2 (E1-E4), volume 2x / 20 bars (E4), 200/500 periods (L4, L5), close-break (B1). Defaults taken without asking (logged): primary price arm = wick; primary transform = log; k=3; sensitivity arms limited to those named in the rows.

## 10. Verification

- Quotes: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_14bxwxC8gBQ.md` PASS (no new transcript quote introduced; all quoted text is already in that extract).
- Spec lint: `python MyTradingSys/research/trendlines_2026-10-17/lint_contract.py` (every parameter row has a tag, none unset).
