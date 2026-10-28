# ANGLES: five checks of the context factors, and the prior-verdict review (2026-10-16)

Every number here is a count, a definition or a hand recomputation; no outcome was read. Scripts: `run_dev.py`
(angle a), `angle_b.py` (b), `angle_c.py` (c), `redteam.py` (d), `counts.py` (e).

## a) Two independent builds: replay (bars[0..t] only) vs vectorised

| run | rows compared | disagreements |
|---|---|---|
| synthetic 110-day tape with gaps, test suite (`test_replay_equals_vectorised`) | >= 40 hours x 2 sides x every key | 0 |
| real DEV, every decision hour 2022-04-01 .. 2024-06-30, final code | 39,458 (19,729 h x 2 sides) | 0 |

The replay recomputes every candle, band, ATR, percentile, profile window and level from the prefix it is given (its
window is the last 120 days, Monday-aligned) with scalar Python; the vectorised build uses pandas/numpy on the full array.
Floats are compared at 1e-9 relative, everything else exactly.

What the angle did and did not catch (said plainly, because 0 disagreements can mean "both wrong the same way"):
- Found: a stale key name (`f4_<tf>_eng_opr`) left in the warm-up branch of BOTH builds after the engulf rename; it never
  fires on real DEV hours (all have >= 3 candles) and was caught by the planted-leak test on the synthetic tape (KeyError),
  then fixed in both.
- Found by design review, then fixed: the first version shared five small helpers between the builds (Krown chaining,
  nearest-level pick, phase A map, funding and touch categories, session map). They were rewritten on the vectorised side
  (`_cluster_np`, `_near_np`, `_phase_a_np`, `_fund_np`, lookups) and the full DEV comparison re-run: still 0.
- Still shared: the constants, `vp_pivot_probe.build_profile` (FORMULAS 18.1, tested in its own study) and the spec.
  Two builds of one wrong definition agree; angles b-d exist for that, and they found five spec errors (below).

## b) Trader's eye: 12 seeded DEV decision hours (seed 20261016)

`angle_b.py` rebuilds the chart from the raw 1m archive (its own groupby, not the 5m tape or any builder): last closed
D/12h/8h/4h candles with the partial current ones, prior week, ATR14(D), ATR14(1h), 1h BB(20,2), session VWAP. My reading
of each chart, then the builder row:

| T (UTC) | what a trader sees at T | builder | verdict |
|---|---|---|---|
| 2022-08-23 21:00 | Price 21,470 under yesterday's open 21,505.6 (long not armed, short armed). Long stop under yesterday's low 20,858.6 = 2.85 %, inside one day's ATR 4.83 %. Short stop above yesterday's high 21,550 is only 0.37 % away: too tight to pay costs. Today already printed 21,667 above. | long D 2.85 % ok; short: D 0.37 % -> 12h 0.36 % -> **8h high 21,667 = 0.92 %** | **MISMATCH 1**: the ladder descended on a stop that was too tight and picked a wider 8h stop. The rule refines a stop that is "too much". Fixed: descend only when wider than W_max, else no stop. Also **MISMATCH 2**: nearest resistance shown as yesterday's high 21,550 while today's high 21,667 is what a trader watches. Fixed: developing session high/low added as a layer. |
| 2022-10-29 01:00 | One hour into Saturday. Long armed (20,613.6 > 20,285.6). D low 19,951 is 3.21 % away, more than ATR(D) 2.79 %, so refine: 12h low is the same 19,951, 8h low 20,438.8 = 0.85 %. | long 8h 0.85 % | match (the ladder doing what O1 says). **MISMATCH 3**: nearest long support = session VWAP 20,574.7 after one hour, i.e. the last hour's average price; no trader calls that a level. Fixed: session VWAP only after 4 h (and weekly after 1 day). |
| 2023-01-09 13:00 | 4h closes riding the upper band (Jan 2023 rally). Price 17,242.6 is above yesterday's high 17,181.1, so a short cannot put its stop above yesterday's candle: no short. Long armed, D stop 1.96 % > ATR(D) 1.37 % -> 12h low 17,098.2 = 0.84 %. | short none; long 12h; bb4h walk_upper | match. **MISMATCH 2 again**: short's nearest resistance shown 4.4 ATR away (Krown 17,546) while today's high 17,277.7 sits 0.5 ATR above. Fixed by the session layer. |
| 2023-03-06 08:00 | On the 8h/4h boundary: the 00-08 8h candle just closed, no partial 8h/4h. Long armed; stop under yesterday's low 0.92 %. Short stop above yesterday's high 1.20 %. | same; candles aligned at the boundary | match |
| 2023-05-14 22:00 | Long armed, stop 0.82 %. Short stop 0.58 % (just over the 0.56 % floor). Round 27,000 overhead 0.9 ATR. 12h candle has a 62 % lower wick: hammer. Weekly trend still above its 10-week average (phase A markup) while the 30-day return is -12 % (phase B markdown). | same | match; phase A and B disagree (see e) |
| 2023-07-02 10:00 | Short not possible: yesterday's high only 0.51 % above. 8h: green doji then red candle closing below its open: engulf. | short none; 8h bear_engulf | match, but the engulfed candle is a 12-USD doji: engulfing it is trivial (also seen 2023-01-09 on D). Kept; logged as risk R4 below. |
| 2023-08-28 06:00 | Price 25,950 is under yesterday's low 25,955.6 and under the 12h/8h lows: no long stop under any candle. 1h close below the lower band. | long none; short D 0.86 %; bb1h break_lower | match |
| 2023-11-12 02:00 | The 36,588 wick shows as a hammer on 12h, 8h and 4h at once. | pin_bull on all three | match; **finding**: the timeframes are nested, so one wick counts three times. Not a bug, but F4 per timeframe is one family, not four independent factors (Holm counts it so). |
| 2023-11-16 00:00 | Midnight: no partial D. After a +6.5 % day the long stop under yesterday's low is 6.59 %; 12h 4.93 %; 8h 4.30 %: all wider than ATR(D) 3.61 %. No trade. | none | match |
| 2023-12-21 06:00 | Long armed, D stop 3.04 % within ATR(D) 4.02 %. Today's low 43,317 just below. | long D; nearest pw_va 1.17 ATR | **MISMATCH 2 again** (today's low missing before the fix) |
| 2024-05-10 15:00 | Yesterday was a big bullish engulf, but today has already given all of it back (63,050 -> 61,035). | D bull_engulf "with" for the long | match on the rule (completed candles only), **finding**: a trader sees the engulf invalidated by the partial day; F4 cannot. Operator decision D3 in REPORT.md. |
| 2024-05-18 22:00 | Long armed, stop 2.70 % under yesterday's low. | same | match |

Raw-data cross-checks on all 12: every candle O/H/L/C, ATR14(D), ATR14(1h) and 1h BB(20,2) from the 1m-direct rebuild
equals the builder's to the printed decimal. VWAP differs by 0.2-1.2 USD: the builder uses 5m hlc3, a 1m chart's VWAP uses
1m hlc3. Both are VWAPs; a chart user should expect that much difference.

Classic engulf (the first chosen definition) was checked against the data after these readings: in 449 of 911 DEV daily
candles (2,742 of 5,471 4h candles) the open differs from the previous close by 0.1-4.4 USD, so "open at or below the previous
close" is decided by tick noise half the time. **MISMATCH 4, fixed**: the operator's rule (colours flip, close past the
previous open) became the chosen definition; classic is the logged variant.

## c) Hand arithmetic (T = 2022-10-29 01:00, raw values printed by `angle_c.py`)

| factor | by hand from the raw bars | builder |
|---|---|---|
| ATR14(D) | 14 true ranges: 252.8, 357.9, 518.0, 625.4, 299.8, 467.6, 640.0, 146.5, 640.0, 447.3, 1187.0, 988.9, 693.7, 789.0; sum 8,053.9 / 14 = 575.28 -> 575.28 / 20,613.6 = 2.7908 % | f3_wmax 2.7908 |
| F3 long | armed: 20,613.6 > prior D open 20,285.6. D width (20,613.6 - 19,951.0) / 20,613.6 = 3.2144 % > 2.7908 -> 12h low 19,951.0 same 3.2144 % -> 8h low 20,438.8: 174.8 / 20,613.6 = 0.8480 % in [0.56, 2.79] -> 8h; cost 0.14 / 0.848 = 0.1651 R | 8h, 0.848, 0.1651 |
| F3 short | high 20,740: 126.4 / 20,613.6 = 0.6132 % -> D; cost 0.2283 R | D, 0.6132, 0.2283 |
| F6 phase A | SMA10 of the last 10 weekly closes = 198,362.3 / 10 = 19,836.23; two weeks earlier 207,011.6 / 10 = 20,701.16; close 19,560.7 below, slope -864.9 -> markdown | markdown |
| F6 phase B | 30-day return 20,582.8 / 19,407.3 - 1 = +6.06 % (inside +-7.5 %) -> range; position (20,582.8 - 17,917.8) / (25,200 - 17,917.8) = 0.366 -> balance | balance |
| F6 intraday | net 20,613.6 - 20,273.6 = 340.0; path = sum of 24 absolute 1h moves = 1,461.2; ER 0.233 < 0.3 -> balance | balance |
| F7 htf_align | SMA20(D) = 389,532.0 / 20 = 19,476.6 < D close 20,582.8; SMA20(4h) = 409,543.1 / 20 = 20,477.2 < 4h close 20,582.8 -> long 2, short 0 | 2 / 0 |
| F7 approach | (c[j-3] - c[j]) / ATR = (20,583.9 - 20,613.6) / 157.0 = -0.19 -> long away; short +0.19 -> slow | away / slow |
| F7 session, weekend | decision bar opens 00:00 Saturday -> asia, weekend | asia, weekend |
| F4 12h | prev 12h red (20,285.6 -> 20,163.4), last green (20,163.4 -> 20,582.8) closing above the prev open 20,285.6 -> bull_engulf | bull_engulf |
| F1 short (before fix) | nearest resistance = session high 20,617.2 after one hour: (20,617.2 - 20,613.6) / 157.0 = 0.023 ATR | 0.0229 |

**MISMATCH 5, fixed**: the last row shows the session high/low has the same first-hours problem as the session VWAP
(a one-hour-old "session high" 3.6 USD above price). The session layer now also starts 4 h into the day.
Profile levels (POC/VAH/VAL) were not recomputed by hand: they come from `vp_pivot_probe.build_profile`, whose worked
examples are FORMULAS 18.1 A-C; the PIT part (which bars feed it) is covered by the truncation tests.

## d) Red team: five ways this could still be wrong, top three tested

| # | risk | test | result |
|---|---|---|---|
| R1 | Look-ahead at bucket boundaries (a D/8h/4h candle counted as closed one bar early, or the bar ending at T missed) | `redteam.py` R1: 40 seeded real DEV hours (20 on 00:00 day boundaries, 20 mid-4h), vectorised from bars[0..t] vs the full-DEV frame | **0 mismatches** in 80 rows |
| R2 | Wrong side: a support above price, a stop on the profit side, a negative distance | `redteam.py` R2 over all 39,458 rows | **0** wrong-side levels, 0 negative distances, 0 wrong-side stops |
| R3 | Levels that move or vanish between bars without being broken (re-chained Krown zones, rolling windows, the day roll) | `redteam.py` R3: for every at-level hour not broken by the next close, is the same layer's level still within 1 USD one hour later? | static layers (prior_dw, pd_va, pw_va) **never** vanish inside a day (0 of 10,248 hours); Krown 2.4-4.4 % (re-chaining when a new pivot joins, 60-day ageing), round 2.4-2.9 % (only the nearest 1,000 each side is listed); dynamic layers move by design (VWAP 78-79 %, session 31-33 %, bb4h 22 %). At the 00:00 roll 342 / 378 static levels are replaced (yesterday becomes "two days ago" and is dropped) |
| R4 | Candle patterns that are trivially true (engulfing a doji; one wick counted on three timeframes) | not tested; seen in b | logged; PRE_REG keeps F4 out of the composite |
| R5 | Overfitting through OURS parameters (about 25: k, zones, W_max, N, windows) | not testable on counts; every one fixed before any outcome, variants logged (trials.csv, 16 rows), Holm m = 37 in PRE_REG | open by nature |

## e) Two reasonable definitions, counts under each (trials.csv)

Decision events = cooled-down ledger before the stop filter (3,814 long, 3,817 short), summed over both sides.

| factor | definition A | n | definition B | n | chosen and why (never by outcome) |
|---|---|---|---|---|---|
| F1 role flip | 1h close through (mean same-side levels per hour, long + short) | 21.23 | 1h and last 4h close (contested excluded) | 20.37 | A: the decision timeframe is 1h; B removes about 4 % of levels |
| F2 confluence | distinct layers >= 2 | 4,532 | distinct names >= 2 | 5,457 | layers: pd_va is one computation that Tom and Fabio share; names would count it twice |
| F3 armed | close past prior D open | 3,795 | partial-day extreme past it | 5,196 | close: "has moved past" read as where price is at T, not where it went |
| F3 W_max | 1.0 x ATR14(D) | 5,598 with a stop | fixed 3.0 % | 5,743 | ATR: "too much" relative to how far BTC moves in a day; fixed 3 % ignores 2022 vs 2024 volatility |
| F4 engulf (D, trade side) | operator: close past previous open | 977 | classic incl. open <= previous close | 716 | operator: classic is decided by 0.1-4.4 USD tick gaps on 24/7 bars (b) |
| F5 walk | closes at/beyond the band | 263 | %b cushion 0.05 | 462 | strict: the only definition with no free number besides N |
| F5 veto | prompt: walk against the trade | 126 | operator's "dance": any close at/beyond the band in the last 2 bars | 701 | prompt's, as instructed; the operator's own words support B (CONTEXT_FACTORS_SPEC F5); operator decision D2 |
| F6 phase | weekly close vs SMA10(W) + slope | 7,631 rows | 30 d trend tag + 90 d range | 7,631 | A: B's trend part is the context_null `trend` key, so its effect would be matched away |

Phase A vs B on the stop-ledger events (5,598): they agree on 45.8 %. Crosstab (rows A, columns B):

| A \ B | accumulation | balance | distribution | markdown | markup |
|---|---|---|---|---|---|
| accumulation | 2 | 165 | 60 | 246 | 50 |
| distribution | 21 | 188 | 49 | 28 | 314 |
| markdown | 607 | 80 | 6 | 1,028 | 167 |
| markup | 2 | 323 | 582 | 196 | 1,484 |

"Phase" is not one measurable thing: 607 events are weekly markdown but daily accumulation, 582 weekly markup but daily
distribution. Any phase claim must name its definition.

## Prior-verdict review (`verdicts.py check` output in PRE_REG.md s.9)

Was the context these one-run studies used built point in time? And is a context FILTER here a different family from
their SETUP?

| study (verdict) | context it used and whether it was point in time | different family from this PRE_REG because |
|---|---|---|
| mal_bb_mid_engulf_2026-10-16 (FAIL, A1 and A2) | HTF filter = last CLOSED 1h/4h bar by index arithmetic (`study.py:63-65`, used at `:85-87`): PIT, valid because the tape is index-aligned with NaN rows for missing minutes. No phase or level context; the engulf is on closed 5m bars. | it tested a 5m trigger (midline bounce + bearish engulf + second break, SHORT, h = 60 min); here an engulf is one optional context factor on D/12h/8h/4h and is not in the composite |
| opr_bb_mtf_center_2026-10-16 (AU INCONCLUSIVE, AD FAIL) | 1h BB mid touched at bar k with mid[k] including close k, decision at the close of k (`study.py:31-58`): PIT for a close-of-bar decision; the slope uses mid[k-1]. Krown ranges (`study.py:81-95`) are descriptive tables, built on windows ending at j: PIT. | it tested the touch of the 1h mid as a trigger at h = 120 min; here the 4h mid is one level among eight layers |
| wlow_bounce_bbrsi60_2026-10-16 (INCONCLUSIVE, n = 8) | prior ISO-week low "known at the OPEN of bar i (uses bars strictly before i)" (`backtest/layers/wlow_bounce/detector.py:49-63`): PIT; weeks with a missing hour are skipped | prior-week low is one level of the prior_dw layer here; no break-bounce-hold trigger |
| opr_weekly_low_round_sweep_2026-10-16 (FAIL, RL and AS) | prior full Monday-Sunday week low per 1m bar (`study.py:35-46`) and round levels from price (`:48`): PIT | its family is the 1m break of a weekly low / round 1,000 with a reclaim within 5 min or three closes below, h = 60 min. Our f7_sweep (1h wick through any same-side level, close back) is the nearest relative; it is REFUSED_POWER and not in the composite, so it is not re-tested |
| rsi_divergence_mtf_2026-10-09 (no edge; cells FAIL/insufficient) | swing pivots need the next bar (`backtest/layers/rsi/rsi_divergence.py:20-26`), the event is stamped at that bar and the return starts at its close (`run_divergence_mtf.py:72, :97, :108-113`): PIT | no RSI factor here |
| gross_effect_screen_2026-10-15 (T INCONCLUSIVE, C FAIL) | session extreme, leg percentile vs the previous 20 days, all from bars <= t (PRE_REG.md:45-48): PIT | its kill scope is the 1m session-extreme fade with delta flow; here the developing session high/low is only one level layer, no fade trigger |

None of the six built a phase or a daily-candle stop; only mal_bb_mid_engulf used a higher-timeframe context (RSI/BB-mid
filter), and it was point in time. So their verdicts say nothing about the context factors; equally, nothing here can
rescue or re-test their setups.

`eur_low_us_sweep_2026-10-14`: VERDICTS.csv lists split DEV+VALIDATION+HOLDOUT. Not a parse error: its RESULT.md:8 says
"DEV 2022-2024, VAL 2025, HOLDOUT 2026, reported side by side", and :21 prints "HOLDOUT 72%". It is a real holdout read,
and wider than its label: the project split puts HOLDOUT at 2025-07-01 .. 2026-09-30, so its "VAL 2025" second half is
also holdout. Recorded in REPORT.md.
