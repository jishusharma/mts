# MARKET ANALYSIS 2026-10-02: BTCUSDT tape vs Tom core and Fabio v3

Session MTS-2026-10-02-1530Z-CLI-ANA-tom-fabio-session (Opus, CLI, ANA). Read-only analysis; no live-path file touched.
Data cutoff: 2026-10-02T15:50:10Z (apparatus_log.txt:19446). Every number is from a disk read this session.

Source keys:
- LOG = `runtime_data/apparatus_log.txt` (line numbers given).
- SNAP = `runtime_data/snapshots/BTCUSDT_<local-date>_<epoch ms>.json`. The filename date is local (+0530), so use the timestamp_utc field.
- CMS = `MyTradingSys/runtime/current_market_state.md` (version 15:50:10Z).
- DIAG = `research/_archive/loose_2026-10/TOM_BT_SHORT_DIAGNOSIS_2026-10-02.md`.
- DR = `research/_archive/loose_2026-10/DIRECTION_REVIEW_2026-10-02.md`.
- STD = `scripts/core/start-trading-day.ps1`.
- VPY = `MyTradingSys/backtest/verdict.py`.

Coverage limits:
- The tape has a hole from 2026-10-01T19:44:09Z (LOG:18586) to 2026-10-02T13:01:15Z (LOG:18598): the apparatus was not writing. No snapshot exists in that window either.
- 2026-10-01 13:30-14:32Z has no log row. Session fields from later snapshots still cover it.
- "Outcome" checks below use the ~1/min snapshot `current_price` samples, not 1m OHLC. Fills and stops between samples are UNVERIFIED. Session high/low fields from the snapshot `session` block are true extremes.

## 0. Context: the week before (2026-09-24 .. 2026-10-01)

These values are daily H/L/C from the `prior_day` block of the first snapshot of the following UTC day. Days are anchored at UTC 00:00, which `crypto_adaptations.md:50` marks UNVALIDATED (DR:53).

| UTC day | high | low | close | source snapshot (first of next day) |
|---|---|---|---|---|
| 09-24 | 84901.6 | 82832.0 | 84370.0 | 2026-09-25 08:09Z |
| 09-25 | 85224.0 | 83130.1 | 84056.0 | 2026-09-26 17:52Z |
| 09-26 | 84458.6 | 83750.0 | 84403.3 | 2026-09-27 00:00Z |
| 09-27 | 85146.4 | 84074.3 | 84432.9 | 2026-09-28 15:33Z |
| 09-28 | 84966.8 | 82500.1 | 83461.0 | 2026-09-29 00:00Z |
| 09-29 | 84554.9 | 82724.3 | 83624.5 | 2026-09-30 17:43Z |
| 09-30 | 85632.7 | 82901.3 | 83576.9 | 2026-10-01 14:32Z |
| 10-01 | 85265.3 | 83136.6 | 84829.6 | 2026-10-02 13:01Z |

- The week's range was 82500.1 (09-28 low) to 85632.7 (09-30 high).
- No daily close was above 84829.6 (10-01).
- Weekly profile at the cutoff: VAL 82910.49 / POC 83851.38 / VAH 85097.56, shape TWOPEAK (CMS:21-24). Prior-week POC was 84189.76 (CMS:25).

## 4.1 Session summary (since 2026-10-01T13:30Z)

**2026-10-01, NY session (anchor 13:30Z):**
- Open 83432.5, initial balance 83426.9-83998.4. Source: SNAP 10-01T14:32:17Z `session` block.
- The session low 83426.9 equals the IB low and was never broken. Session low is 83426.9 in every 10-01 snapshot.
- The first logged price was 84033.5 at 14:32:16Z (LOG:17044). The lowest sampled price was 83745.2 at 14:53:10Z (LOG:17146).
- `day_type` changed balance -> trend_up at 16:36:10Z (SNAP 10-01T16:36:10Z).
- The session high printed 85265.3 by 18:39:11Z (SNAP); the sampled price was 85208.0 at 18:39:10Z (LOG:18261). 85265.3 is also the full UTC-day high (`prior_day.high`, CMS:46).
- The daily VAH migrated up from 84023.88 (14:59Z) to 84313.65 (19:44Z), per the hourly SNAP table in the appendix.
- Position states: 202 of 307 logged rows were `TWOPEAK/above_vah` and 105 were `in_va` (parsed LOG rows for 10-01).
- Last logged price: 84617.1 at 19:44:09Z (LOG:18586). The UTC-day close was 84829.6 (CMS:45).

**2026-10-02 overnight (no tape):**
- At 13:01:15Z price was 86777.1 (LOG:18598).
- The NY open was 86560.0. `gap_from_prior_close` was 1730.4 and `gap_direction` up (newest SNAP, 15:50:10Z).
- Between 19:44Z and 13:01Z price moved from 84617.1 to 86777.1. The path is UNVERIFIED (no data).
- The overnight move cleared the week's 85632.7 high and the 85097.56 weekly VAH. When that happened is UNVERIFIED.

**2026-10-02, NY session (anchor 13:30Z):**

| Time (UTC) | Event | Source |
|---|---|---|
| 13:30 | IB opens at 86560.0 | SNAP |
| 13:30-13:39 | Rally to session high 87123.0, printed by 13:39:11Z. The 13:38-13:39Z rally went above the daily VAH (87064.46 at 13:40Z) and back. `sweep_flag` true, `liquidity_sweep_direction` above, from 13:31:10Z | SNAP |
| 13:40:10 | Sampled price 87050.7, the highest log sample of the day | LOG:18795 |
| 13:58:11 | IB low set at 86415.7 | SNAP |
| 14:11:11 | IB low broken (session low 86369.7) | SNAP |
| 14:28:11 | Price first `below_val` at 86129.6. Daily VAL then 85983.64-86143.76 (drifting) | LOG:19036; appendix |
| 14:31:25 | ALERT #83 `in_va -> below_val` | LOG:19052 |
| 14:35:11 | `day_type` balance -> trend_down at 85763.1 | SNAP; LOG:19071 |
| 15:47:10 | Session low 85250.1 by the 15:47:10Z snapshot; sampled price 85280.1 | SNAP; LOG:19431 |
| 15:50:10 | 85358.7. Snapshot VAL/POC/VAH 85903.58/86799.26/87049.45 | LOG:19446; SNAP |

At the 15:50:10Z cutoff:
- Price was below VWAP 86100.08: under the -1σ band 85537.22 and above the -2σ band 84974.35 (CMS:71-76).
- CVD slope was rising (CMS:79-80), but session CVD was -3941.70 (state_code.json:12).

**Levels: held or failed:**

| Level | Value | Result | Source |
|---|---|---|---|
| Daily VAH | ~87064 | Pierced intrabar (87123.0); price failed back inside within the minute samples | LOG:18795, SNAP |
| IB low | 86415.7 | Failed at 14:11Z | SNAP |
| Daily VAL | ~85984-86144 | Failed at 14:28Z; stayed below from 14:30Z to the cutoff | LOG |
| Prior-day high | 85265.3 | Pierced by 15.2 (session low 85250.1); every sampled price stayed above | CMS:46, SNAP |
| Weekly VAH | 85097.56 | Not tested (session low 85250.1 > 85097.56) | CMS:23 |

## 4.2 Tom rules on this tape

The rules evaluated are the Compute-Verdict gate chain:
- STD:169 `net_ok = net_rr >= 1.25`. This was edited from 2.0 in commit d84fb83, and the file mtime is 2026-10-02 13:49:45Z.
- The tier gate, then proof < 3 = WAIT_PROOF, proof < 5 = WATCH, else SETUP_FORMING (STD:204-215).
- The Python port VPY:110-137 also has the proof-direction downgrade (:122-123), broken-VA + CVD (:129-132) and flow contradiction (:133-137). VPY:84 still uses `net_rr_sanity`, the Java 2.0 test.

**Which floor was live when:**
- Process started 13:02:03Z (LOG:18601). All 48 rows from 13:01Z to 13:49Z run under the 2.0 floor. 38 are `WAIT_RR` with net_rr between 1.50 and 1.83, so all 38 would pass 1.25 (parsed LOG rows).
- Process restarted 13:50:32Z (LOG:18844). The 120 rows after that contain zero `WAIT_RR`, although 24 of them have net_rr in [1.25, 2.0). The new floor is live from 13:50:32Z. That this process loaded the edited file is inferred from that count.
- The WAIT_RR reason string at STD:205 still prints "< 2.0" whatever the floor.

**Engine output vs tape, key episodes.** Top candidates with proof >= 4, from SNAP `setup_candidates[0]`:

| UTC | Engine said | Tape did (sampled) | Agree? |
|---|---|---|---|
| 10-01 15:11-15:18 | ct_short @ 4h_vah 84009.38, stop 84177.4, net_rr 1.72-1.74, proof 4-5 -> WAIT_RR (LOG:17261) | price 84185.0 at 15:20 (above stop) | Gate kept it out of a loser |
| 10-01 15:57-16:58 | Four ct_short candidates at daily VAH / 5m swing high, net_rr 1.52-1.82 -> WAIT_RR | each sampled fill went on to the stop (16:33, 16:34, 16:34, 17:07); price trended up to 85265.3 | Gate kept it out of losers |
| 10-01 16:57:10 | **SETUP_FORMING** scalp_short @ vwap_band_+1 84115.81, stop 84284.04, target 83591.65, net_rr 2.34, proof 5, book_imbalance 0.39 (LOG:17766). The popup was suppressed: `SCALP_SUPPRESSED reasons=vwap_slope_not_sideways:'rising'` (LOG:17767; mts_math.py:473; STD:688-691) | 84359.3 at 17:03:10 (LOG:17797), above stop | Verdict and tape disagree. The suppression agreed with the tape. No ALERT number was issued (alerts between 16:50Z and 17:04Z are #81 and #82 only). |
| 10-01 16:46 | ct_long @ 5m_swing_low 84185.5, net_rr 1.69 -> WAIT_RR | sampled fill 16:51, target 84564.82 sampled at 17:18 | Gate blocked a winner (net_rr floor 2.0) |
| 10-01 18:10-18:22 | ct_long @ 5m_swing_low 84683.7, proof 4-5, net_rr 1.54 -> WAIT_RR (LOG:18116) | no sampled fill; target 85032.39 reached 18:38 | No trade either way |
| 10-02 13:40-13:41 | ct_short @ daily_vah 87064.46, trigger_ready, proof 5, pd aligned, stop 87238.59, target 86687.55, net_rr 1.62 -> WAIT_RR "1.62 < 2.0" (LOG:18795) | stop never traded (session high 87123.0 stays to cutoff); price at 86626.2 by 13:55 (LOG:18871); then ran down to 85250.1 | **Disagree.** VPY `compute_verdict` on these snapshots with only `net_rr_sanity` forced true returns `SETUP_FORMING proof 5` (13:40, 13:41) and `WAIT_TRIGGER` (13:42). Run this session. Only the net_rr floor (2.0, NO-SOURCE per DR:32-36) blocked it. A fill at 87064.46 after 13:40:10Z is UNVERIFIED: 87050.7 was sampled and the session high 87123.0 printed by 13:39:11Z. |
| 10-02 13:53-14:07 | ct_long @ 4h_val 86682.54 / 86667.48, proof 3-4, pd mixed -> WATCH / WAIT_PROOF (flow contradiction) / WAIT_TRIGGER | sampled stop 86560.0 at 13:58 and 14:08 | Gates kept it out of losers |
| 10-02 14:12-14:47 | ct_long @ 1h_swing_low 86250.2, then 5m_swing_low 85763.1 -> WAIT_PROOF flow contradiction / WAIT_TRIGGER | stops at 14:30 and 14:55 (sampled) | Gates kept it out of losers |
| 10-02 15:28-15:34 | tc_long @ vwap_band_-1 ~85555, proof 3-4, pd contradiction -> WATCH (LOG:19366) | stop 85338.5 sampled-hit 15:42 (85334.1) | Gate kept it out of a loser |

**Rule-level disagreements:**
- **net_rr floor (STD:169 before d84fb83; VPY:84/110-111 still).** It blocked the 10-02 13:40Z daily-VAH short, which hit its target, and the 10-01 16:46Z long, which hit its target (sampled). On 10-01 it also blocked six shorts that would have stopped out (15:11-16:58, sampled).
- **Target choice (nearest level, [2.0, 3.5]R window, DR:33-35).** The 13:40Z short's target 86687.55 was 377 points below entry. The tape moved 1814 points from entry 87064.46 to the session low 85250.1. Nothing in the engine output carries the larger move.
- **Scalp suppression (mts_math.py:470-479).** It removed the only SETUP_FORMING of the two days. The sampled outcome was a stop.
- **Proof-direction and flow gates.** These were on the right side of every sampled outcome on 10-02. All 63 ct_long and 10 tc_long candidate rows came during a sweep-and-trend-down session, and none reached SETUP_FORMING.

## 4.3 Fabio v3 on this tape

The v3 engine was not run. Two inputs are missing, so it is BLOCKED for this tape.
- `run(bars, config)` needs 1m order-flow bars for the NY 390-minute window (v3/README.md:3, :20).
- The newest order-flow bar file on `F:\MTS\data\orderflow_1m` is `2026-09-28.csv.gz` (directory listing this session). There are no bars for 2026-10-01 or 2026-10-02.
- The snapshots hold one price sample a minute, not OHLCV or footprint bars.
- The config needs `N, p, z_hi, m_c, f, g, entry_mode, mgmt` with "no defaults" (v3/README.md:25). Choosing them here would be tuning, which the provenance rule forbids (CLAUDE.md; DR:41-43).

Prior-session evidence only (no claim about today):
- FABIO_L1_REPORT:31-36: no L1 rule survives 0.10% round-trip fees out of sample with PBO < 0.5. Escalation at 1h has PBO 0.76 with n = 182.
- FABIO_OF_REPORT (Findings): every variant with OOS n >= 30 has negative net expectancy.
- FABIO_OF_REPORT (Findings): median OOS gross is +0.13R against a median fee drag of about 0.66R.
- FABIO_OF_REPORT (Findings): NY is the least-bad scope. NY combined 15m: win 44%, PF 0.90, net -0.05R, but OOS n = 16.
- FABIO_OF_REPORT (Recommendation): keep Fabio context-only, log-only forward test.
- FABIO_OF_REPORT (Limits): the OF data is 90 days in one regime (2026-07-01..2026-09-28).

The snapshot `session` block (sweep_flag, liquidity_sweep_direction, day_type) belongs to the core snapshot builder. It is not Fabio v3 output, and this document does not restate it as a Fabio signal.

## 4.4 The all-shorts finding, applied to today

DIAG:73 found that the backtest's zero proof-5 longs came from `book_imbalance == 0.0`, the archive placeholder. It was fixed in 13295c8, and the cache predates the fix.
- **On the live tape the bug condition is absent.** `conditions.book_imbalance == 0.0` occurs in 0 of 477 snapshots from 2026-10-01T13:30Z to the cutoff. Candidate `proof.book_imbalance` values seen include 0.39, 4.44, 0.48, 0.18, 17.44 and 1.3.
- **2026-10-01:** 1 SETUP_FORMING out of 307 rows, **short**: scalp_short at 16:57:10Z (LOG:17766). The popup was suppressed (LOG:17767).
- **2026-10-01, proof-direction by side** (candidate rows): long 44 aligned / 44 contradiction; short 58 aligned / 25 contradiction.
- **2026-10-02:** **0 SETUP_FORMING** out of 168 rows.
  - Pre-restart, 13:01-13:49Z, 48 rows: WAIT_RR 38, NO_TRADE 8, WAIT_PROOF 2.
  - Post-restart, 13:50Z to cutoff, 120 rows: NO_TRADE (no candidates) 67, WAIT_TRIGGER (price not at zone) 33, WAIT_PROOF 13 (flow contradiction 11, proof 2 2), WATCH 7 (proof 3 or 4).
  - Proof-direction by side (candidate rows): long 35 aligned / 39 contradiction; short 10 aligned / 9 contradiction.
- **Consecutive cycles without SETUP_FORMING:**
  - All 168 logged cycles today, of which 120 ran under the 1.25 floor.
  - Longest single-gate runs today: WAIT_RR 20 cycles (13:12:10-13:31:10Z) and NO_TRADE 40 cycles (14:48:09-15:27:09Z).
  - The final run at cutoff is NO_TRADE (no candidates), 10 cycles (15:41:09-15:50:10Z).
- **The one proof-5 setup today was a short** (ct_short @ daily_vah, 13:40-13:46Z, LOG:18795). The only gate that blocked it was net_rr under the pre-restart 2.0 floor.

## 4.5 Open questions raised by the tape

- Was the 13:40Z daily-VAH short filled at 87064.46 after 13:40:10Z? The minute samples cannot show it.
- What did price do between 2026-10-01T19:44Z and 2026-10-02T13:01Z? There is no log or snapshot for that window.
- Why did the apparatus stop writing at 2026-10-01T19:44:09Z, when the last START was 17:55:10Z (LOG:18039)?
- Why was no ALERT issued between 13:01Z and 14:31Z today? The verdict changed several times, and ALERT #83 at 14:31:25Z (LOG:19052) is the only alert today.
- auto_trades.jsonl has one row since 2026-10-01: `start` at 2026-10-02T13:07:35Z with `tom_last_alert_no` 70. `alert_counter.txt` reads 83. Are alerts #71-#83 being consumed?
- STD:205 prints "< 2.0" in the WAIT_RR reason while STD:169 tests 1.25. The two disagree in log text.
- VPY:84 (backtest/parity port) still gates on `net_rr_sanity` (Java 2.0), while the live gate is 1.25. Is the parity guard named in VPY:16-18 now broken?
- The log regime tag says `rg=TREND_UP` at 15:47-15:50Z (LOG:19431, 19446) while snapshot `session.day_type` says trend_down and CMS:64 says `trend_healthy`. Three labels describe the same minutes.
- Why did no short candidate appear on the way down? The last short candidate row is 13:49:09Z (ct_short @ 5m_swing_high 87050.70). Every candidate row from then to the cutoff is a long: ct_long, tc_long or scalp_long.
- At cutoff, price is above the prior-day high (85265.3) and the weekly VAH (85097.56) and below the daily VAL (85903.58). Neither weekly level had been broken by the cutoff.

## Appendix: hourly timeline (newest snapshot per hour; log row at the same minute)

| snapshot_utc | price | position | shape | daily VAL/POC/VAH | verdict (LOG) | zone |
|---|---|---|---|---|---|---|
| 2026-10-01T14:59:09Z | 83924.5 | in_va | TWOPEAK | 83427.35/83908.59/84023.88 | WAIT_RR (net_rr 1.72 < 2.0) | ct_short @ daily_vah 84023.88 |
| 2026-10-01T15:59:10Z | 84066.9 | in_va | TWOPEAK | 83572.72/83908.59/84224.4 | WAIT_RR (net_rr 1.52 < 2.0) | ct_short @ 5m_swing_high 84209.60 |
| 2026-10-01T16:59:10Z | 84107.3 | in_va | TWOPEAK | 83537.5/83828.16/84264.14 | WAIT_RR (net_rr 1.82 < 2.0) | ct_short @ daily_vah 84264.14 |
| 2026-10-01T17:59:11Z | 84774.9 | above_vah | TWOPEAK | 83411.7/83911.88/84267.01 | NO_TRADE (no candidates) | - |
| 2026-10-01T18:59:10Z | 84782.2 | above_vah | TWOPEAK | 83311.9/83902.93/84278.58 | WAIT_PROOF (proof 2) | ct_long @ 15m_swing_low 84762.10 |
| 2026-10-01T19:44:09Z | 84617.1 | above_vah | TWOPEAK | 83311.9/83902.93/84313.65 | WAIT_RR (net_rr 1.83 < 2.0) | ct_long @ 5m_swing_low 84572.10 |
| (gap 19:44Z - 13:01Z) | | | | | | |
| 2026-10-02T13:59:10Z | 86590.3 | in_va | TWOPEAK | 86143.76/86799.26/87064.46 | WATCH (proof 3) | ct_long @ 4h_val 86667.48 |
| 2026-10-02T14:59:10Z | 85638.7 | below_val | TWOPEAK | 85983.64/86799.26/87049.45 | NO_TRADE (no candidates) | - |
| 2026-10-02T15:51:09Z | 85325.7 | below_val | TWOPEAK | 85903.58/86799.26/87049.45 | (after log cutoff) | - |

Method: the scratch parsers (`parse_log.py`, `hourly.py`, `episodes.py`) ran in the session scratchpad, read-only over LOG and SNAP. The regex covered all 475 verdict rows for 10-01 and 10-02, with 0 unparsed.
