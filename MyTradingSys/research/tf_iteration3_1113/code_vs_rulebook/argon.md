# Code vs. Rulebook Mismatch Audit (Argon — Iteration 3, 2026-11-13)

Read order per brief:
1. `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py`
2. `MyTradingSys/backtest/layers/fabio/v3/models.py` (with its directly imported helpers in `MyTradingSys/backtest/layers/fabio/v3/signals.py`, `MyTradingSys/backtest/layers/fabio/v3/manage.py`, and `MyTradingSys/backtest/layers/fabio/v3/day_gates.py`)
3. `MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md`

Note on transcript timestamps: Fabio caption files (`9IliXww64uM`, `DyS79Eb92Ug`, `Is1HvdfQm5c`, `LQvv5xgy_ik`, `Pz8f0wWW12M`, `fZlNGWvd2Ko`, `8CWKfoSJu3c`, `FawPrRUGNpk`) carry `[mm:ss]` markers in `raw_transcripts_canonical/<id>_raw.txt`. Tom (and guest) auto-caption files (`M7ompiwv5co`, `3JqMyzE8jIQ`, `k0zm5NYn0IQ`, `0jM5Y31YJak`, `4P5WAxyPCis`, `ACb0Qtt3DSQ`, `Ld1dhjGdTCA`, `qLnQan0KGmQ`, `NkQeOVDTAec`, `y67l86cSqb8`, `YkclL6xgu-s`, `zQTbdEweG3c`, `DVZVE9rXGtU`, `Of_wlv3xaZo`, `BB3c8visnkI`, `Sy-x5AQ9-Pk`, `4MoNjEQ2Dd8`, `3o1VVsfBmmU`, `1utSjHs_Mq8`, `-dMWA_bbm3o`, `kXhIAug0Gh8`, `QClPWDJ-BrU`) are single-paragraph transcripts without `[mm:ss]` markers; for those, `[no-ts, BEGIN|MIDDLE|END]` records that timestamps are `NOT_SEEN` in the canonical file alongside the verified transcript third.

---

## 1. Mismatch Table: `auction_context.py` & `models.py` vs. `RULEBOOK.md` and Verbatim Transcripts

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
|---|---|---|---|---|---|---|
| R1 / R4: Breakout confirmation via impulse candle + volume expansion | Tom | If we happen to go above this specific level here, for example, then first of all, we absolutely need to wait for a clear entry signal to confirm the move. That could be a strong impulse candle with volume, for example. | M7ompiwv5co [no-ts, MIDDLE] | Wait for a clear breakout confirmation signal such as a strong impulse candle accompanied by rising volume/liquidity. | NOT_SEEN (no bar count, no relative-volume multiplier, no percentile threshold stated) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724-744` (`ACCEPTED`continuation ignores volume completely; only `LVN_FAST_TRAVERSE` at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:703` checks `max_rel_vol >= 2.0`); `MyTradingSys/backtest/layers/fabio/v3/models.py:289` calls `breakout` (`MyTradingSys/backtest/layers/fabio/v3/signals.py:307-322`) which uses 30-day 99th/99.9th percentile big-trade net push over `m=15` 1m bars |
| R2: Delta divergence + 5m candle close entry trigger | CONTESTED (9IliXww64uM, listed as Fabio in RULEBOOK) | you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through. And the 5-minute was about to close right over here and that was my signal for the entry. | 9IliXww64uM [8:28] | Negative delta with positive price action shows seller effort without follow-through; enter as the 5-minute bar closes. | SOURCED: 5-minute candle close; delta divergence threshold = NOT_SEEN | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:675,691` (checks `(delta < 0 and c >= o)` or 50% wick + `rv >= 2.0`, but requires reclaim after probing beyond level and does not trigger on 5m close inside range); `MyTradingSys/backtest/layers/fabio/v3/models.py:138-191` (`model_b` runs on 1m bars, requires `S3` z-score `z_hi` over `L=60` bars at `MyTradingSys/backtest/layers/fabio/v3/signals.py:251-261`, not 5m close) |
| R3: Rejection speed (tape velocity vs. bar count) | Tom | The market showed me that there is rejection up here. And the market also showed me that the speed with which it rejected this is promising for me. | k0zm5NYn0IQ [no-ts, END] | Fast rejection speed on the tape confirms immediate entry. | NOT_SEEN (no bar count stated; speed is tape/order-flow tempo) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:591,747` (codes speed as `bars_beyond <= 3` and `max_bars_since_reclaim = 3`, which on 1h bars is 3 hours); `MyTradingSys/backtest/layers/fabio/v3/models.py:32,127` (codes `RECLAIM_BARS = 5` bars in `_b_probe`) |
| R4: Breakout momentum driven by liquidity expansion | Tom | Trading volumes that have increased here, so we know that the momentum is driven by liquidity. | M7ompiwv5co [no-ts, END] | Breakout momentum out of a sideways phase must be accompanied by increasing trading volume. | NOT_SEEN (no numeric volume ratio or z-score stated) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724-744` (`ACCEPTED` continuation has zero volume check); `MyTradingSys/backtest/layers/fabio/v3/models.py:203,289` (`model_c` and `scan_model_a` require `big_push` 99th/99.9th percentile filter rather than rising bar volume) |
| R5: Absorption ('buyers punching a wall', almost-zero price result) | Fabio | the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position. | 0jM5Y31YJak [no-ts, END] | High buy-delta pressure producing almost zero price movement confirms passive seller absorption to enter short. | SOURCED: 'almost zero' price result (qualitative); exact z-score or body ratio = NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/signals.py:29-31,232-248` (fed into `MyTradingSys/backtest/layers/fabio/v3/models.py:121-135,274`: codes `EFFORT_L = 60`, `s * e >= z_hi` and `s * res <= r_abs` with `R_ABS = 0.25` population SD z-score); `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:675,691` (allows 50% wick with `rv >= 2.0` even when `delta == 0`) |
| R6: Front-running resting L2 liquidity blocks by 1-2 ticks | Tom (GUEST: 4P5WAxyPCis) | And then it's just really nice to position yourself one or two ticks ahead of that position because at first the market always since many people and also algorithmic systems see that, the market usually moves away from it at first. | 4P5WAxyPCis [no-ts, BEGIN] | Place limit entries 1 or 2 ticks in front of visible resting limit-order blocks on the heatmap/DOM. | SOURCED: 1 or 2 ticks ahead of resting L2 block; block size = NOT_SEEN | NONE (neither `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:821-881` nor `MyTradingSys/backtest/layers/fabio/v3/models.py:89-260` reads L2 resting depth or front-runs a level by 1-2 ticks; `MyTradingSys/backtest/layers/fabio/v3/models.py:101,181,219,244` places rest limits directly on `lvn`, `c[j]`, `IBs`, or `edge`) |
| R7: Pullback entry into low-volume nodes (LVNs) in a trend | Tom (GUEST: 4P5WAxyPCis) | when the market moves up or down and repeatedly, so to speak, low areas, meaning low volume areas are created, then it's actually a very good very good opportunity to join the trend | 4P5WAxyPCis [no-ts, MIDDLE] | Join a trend on a pullback into low-volume areas created during the impulse move. | NOT_SEEN (no bin-to-POC ratio or minimum retrace fraction stated) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:209,285,703` (defines LVN as `vk <= 0.25 * poc_vol` and only trades `LVN_FAST_TRAVERSE` when slicing *through* an LVN on `>= 2.0x` vol, never a pullback *into* an LVN); `MyTradingSys/backtest/layers/fabio/v3/models.py:314` calls `lvn_levels` and `select_lvn` (`MyTradingSys/backtest/layers/fabio/v3/signals.py:36,158-179`: `v[k] <= 0.5 * med` and `s*(X - lvn) >= 0.25*s*(X - O)` 25% retrace floor, both `NS-fixed` OURS) |
| R8: Fast traverse through low-resistance / clear road | Tom | When the market is a bit clear, meaning there's no resistance, the price gets pushed very strongly and very quickly in one direction. | ACb0Qtt3DSQ [no-ts, BEGIN] | When price enters a low-volume / no-resistance pocket, it moves rapidly through the pocket in one direction. | NOT_SEEN (no bar-count cap or volume multiplier stated) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:703,870-874` (hardcodes `1 <= bars_beyond <= 3`, `max_rel_vol >= 2.0`, and stop buffer `max(stop_buffer_bps, 25.0)` bps); NONE in `MyTradingSys/backtest/layers/fabio/v3/models.py:89-260` |
| R9 / R10: Two-phase market classification (Range/Balance vs. Trend) driving setup selection | Tom | Whether it's trend or balance because I have to use different setups there and that is absolutely crucial. | Ld1dhjGdTCA [no-ts, END] | Classify the market into balance (range/accumulation) vs. trend and switch setup families accordingly. | SOURCED: 2 phases (range/balance vs. trend), balance 60-70% of the time (`BB3c8visnkI`); box formula or candle-streak formula = NOT_SEEN | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:424-455,859-875` (computes `htf_bias` from 1M candle colour vs. 20M SMA, Brownian `p_keep_colour`, and 1w >=3 same-colour streak, and never disables fade or breakout setups by phase—only changes `sizing_tier` at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:957`); `MyTradingSys/backtest/layers/fabio/v3/signals.py:183-205` (used by `MyTradingSys/backtest/layers/fabio/v3/models.py:291,335,444`: `balance()` requires `R <= 0.8 * sqrt(N) * ATR_N` and `|c - poc| <= 0.25 * R` over 60 1m bars, true in 3.1% of windows) |
| R11: Real acceptance requires new range/sideways phase outside level, not N closes | Tom | Not with quick spikes but with real acceptance. | qLnQan0KGmQ [no-ts, END] | Acceptance beyond a level requires price to build a new sideways range / equilibrium there, not just quick spikes or a fixed bar count. | NOT_SEEN (no bar count stated anywhere in transcripts) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:13-15,598-602,724-726` (codes `n_acc = 6` consecutive closes beyond level, or `n_early = 4` while outside, or `bars_in_zone >= 6` within `0.15%` of the level, and docstring at line 13 cites `accept80.py` `2x30m` closes as `SOURCED`); NONE in `MyTradingSys/backtest/layers/fabio/v3/models.py:289,339,403` (breaks trigger on a single 1m bar close `s * (c - E) > 0`) |
| R11b: Breakout acceptance defined as a range forming outside the level | Tom | does another sideways phase emerge after that? Then we have a new model where we can clearly say that the equilibrium, meaning the new acceptance, because the market then spends more time above or below there | Sy-x5AQ9-Pk [no-ts, MIDDLE] | A new acceptance equilibrium is established only when another sideways phase emerges above or below the broken level. | NOT_SEEN (no bar count) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724-744` (counts `consec_beyond >= 6` bars instead of detecting a new sideways range outside the level; worse, `bars_in_zone >= 6 and not probed_beyond` at line 726 marks a stall *inside* the level as `ACCEPTED`) |
| R12: High-volume node (HVN) as reaction magnet | Tom | where high volume occurs, we often see a reaction when a market returns there. | NkQeOVDTAec [no-ts, BEGIN] | High-volume nodes act as reaction magnets when price returns to them. | NOT_SEEN (no `0.5 * poc_vol` threshold stated) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:311-316,494-505` (`compute_volume_profile` computes `hvns` with `vk >= 0.5 * poc_vol`, but `build_mtf_context` at lines 494-505 never adds `hvns` to `levels`—only POC, VAH, VAL, and LVNs are added!); NONE in `MyTradingSys/backtest/layers/fabio/v3/models.py:89-260` |
| R13: Order flow confirms idea only at strong technical levels | Tom | Because if I also have a strong technical level here, then I know there was an exhaustion here, which means an extremum. | y67l86cSqb8 [no-ts, MIDDLE] | Order-flow exhaustion/absorption is valid only when it occurs at a strong HTF/session technical level. | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:289-292,335-344,444` (scanners `scan_model_a/b/d` anchor exclusively on a rolling 60-minute 1m box `balance(bars, b-1, N=60)`, completely ignoring prior-day/weekly VAH, VAL, POC, and session levels) |
| R14: Volume judged relative to session/time-of-day baseline | Tom | whenever trading volumes decrease, supply and demand are no longer as high. This means that fewer large market participants are interested in being active in the markets at that time | YkclL6xgu-s [no-ts, BEGIN] | Judge volume relative to when large participants are active (session / time-of-day baseline). | NOT_SEEN (no 48-bar median or `2.0x` multiplier stated) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:593,637-638,784` (uses median of last 48 bars before touch regardless of session time-of-day and requires `max_rel_vol >= 2.0`); `MyTradingSys/backtest/layers/fabio/v3/signals.py:277-289` (`volume_tier` compares elapsed session volume to prior 20 weekdays with `VR_TIER = 1.5` NS-fixed) |
| R15 / R16 / R17 / R18: Structural stop placed below the entire sideways accumulation floor / value zone | Tom | I would always place the risk below the last sideways phase at the latest because if the market moves above this and then accepts the equilibrium again, that's initially an indication that it showed rejection up here. | M7ompiwv5co [no-ts, END] | Place the stop loss below the entire last sideways accumulation phase (or behind the support zone where the opposite move is expected), not tightly at the breakout level or wick. | NOT_SEEN (no bps buffer stated; in `k0zm5NYn0IQ` Tom uses 20 DAX points = ~8 bps) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:863-874` (places stop on `FAST_REJECTION` at `sweep_extreme +/- 5 bps`, and on `ACCEPTED` / `LVN_FAST_TRAVERSE` at `level_price +/- 25 bps` inside the broken level rather than beyond the sideways accumulation floor); `MyTradingSys/backtest/layers/fabio/v3/models.py:101,199,244` (Model A places stop behind `O` = near edge of balance `s*(lvn - O) + tick`; Model C places stop at IB midpoint `mid = (IBH + IBL) / 2.0`) |
| R19 / R20: Tighter order-flow stop behind trapped participants / absorption candle | CONTESTED (9IliXww64uM) / Tom (3JqMyzE8jIQ) | as I saw the candle reabsorbing. Stop was likely somewhere above here | 9IliXww64uM [10:28] | Place intraday order-flow stop just above/below the absorption candle / trapped participants. | NOT_SEEN (exact tick/bps buffer unstated; measured Fabio NQ stops are 1-6 bps, Tom DAX stop is 20 pts = ~8 bps) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:48,895-909` (`SKIP_FEE_TRAP` rejects any trade with `fee_r > 0.25`, requiring `stop_bps >= 40 bps` on 10 bps taker RT—which rejects both Fabio's 1-6 bps stops and Tom's 8 bps DAX stops!); `MyTradingSys/backtest/layers/fabio/v3/models.py:38-43` (`d_and_stop` inflates structural stop to `D = max(f * entry, structural)` and skips if `D > dmax * entry`) |
| R21: Profit target placed at high-liquidity cluster / prior HVN (or opposite range edge) | Tom | I'll define the next target where there was a lot of liquidity. Because the fact that the market will slow down there at first is simply a probability. | M7ompiwv5co [no-ts, MIDDLE] | Set profit target at the next high-liquidity cluster / HVN (or opposite boundary of the range). | NOT_SEEN | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:931-947` (sorts all candidate levels nearest-first and picks the closest level with `net_rr >= 1.20`, while `hvns` are omitted from `build_mtf_context` levels at lines 494-505); `MyTradingSys/backtest/layers/fabio/v3/models.py:11,104,167,221,252` (Models A, C, and D have `target=None`—no target at all! Only Model B has `target = H if s > 0 else L`) |
| R22: Target at all-time highs mirrors previous momentum impulse (measured move) | Tom | Alternatively, if we happen to be trading at all-time highs, we simply mirror the current momentum move to the upside to determine our next target. | M7ompiwv5co [no-ts, MIDDLE] | When trading at highs without overhead liquidity references, project a 1:1 measured move of the prior momentum impulse leg as the target. | SOURCED: 1x mirror of prior impulse leg distance | NONE (neither `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:821-973` nor `MyTradingSys/backtest/layers/fabio/v3/models.py:89-260` computes impulse-leg measured-move targets; `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:934` returns `SKIP_LOW_RR` if no overhead level exists in `targets`) |
| R23 / R24 / R30 / R34: Market Profile single-print / fair-value-gap revisit only with target context | Tom | The market never made a pullback from here upwards. And that's why we call this price area a fast trend. And the market profiler sees a single print area here. | 3JqMyzE8jIQ [no-ts, BEGIN] | Fast trend leaves a Market Profile single-print (unfair price) area that is only traded when returning first to a fair-value area with a predefined high-probability target. | NOT_SEEN | NONE (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:205-330` and `MyTradingSys/backtest/layers/fabio/v3/signals.py:98-170` compute only Volume Profile bins, never time-based Market Profile / TPO single prints) |
| R25 / R29: Minimum reward-to-risk ratio >= 1.5 | Tom | And only if that is, for example, at least greater than 1.5 or so, then I have a really great strategy that will make me money. | M7ompiwv5co [no-ts, END] | Require reward-to-risk ratio > 1.5 (and in intraday videos >= 2.0 to 2.5, or 1:16-1:19 on Fabio curve-low runners). | SOURCED: R:R > 1.5 (`M7ompiwv5co`) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:49,829,932` (sets `DEFAULT_MIN_NET_RR = 1.20`, below Tom's stated 1.5 floor); `MyTradingSys/backtest/layers/fabio/v3/models.py:89-260` (enforces no minimum R:R gate at all on any of Models A, B, C, or D) |
| R28: Daily closing patience / swing horizon on 24/7 BTC | Tom | in swing trading, where we can simply wait for daily closing prices, we can trade much, much more patiently. | M7ompiwv5co [no-ts, END] | For swing trading (including 24/7 markets like Bitcoin), wait for daily closing prices rather than overtrading intraday noise. | SOURCED: 1d (daily closing prices) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:578-580` (classifier defaults to `bar_minutes: int = 5` intraday bars); `MyTradingSys/backtest/layers/fabio/v3/models.py:35,274-467` (hardcoded to 1-minute bars over a 390-bar intraday window) |
| R31: Market Profile open-drive and buying tails offer zero support on revisit | Tom | if I know the rules of market profiling, then I know that this was simply an open drive here and the market just gave me a strong buying tail at this point and that really won't offer any support for me. | 3JqMyzE8jIQ [no-ts, END] | Do not fade or buy pullbacks into a Market Profile open-drive buying tail; it offers no support. | NOT_SEEN | NONE (neither `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py` nor `MyTradingSys/backtest/layers/fabio/v3/models.py` detects Market Profile open-drive or buying/selling tails; `MyTradingSys/backtest/layers/fabio/v3/models.py:89-118` Model A actively places resting buy limits inside the impulse leg LVN!) |
| R32 / R35: Do not fade active institutional forced dumps / position building vs. arbitrary knife rule | Tom | there's just no point in going against it. You just have to wait until you can see that it's over. | DVZVE9rXGtU [no-ts, MIDDLE] | Do not fade active institutional selling / forced flow; wait until order flow shows the move is over. | NOT_SEEN (no `-2.0%` 12-bar drop or `< 25%` bounce formula stated) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:526-568` (`is_knife_approach` hardcodes a 12-bar geometric rule: drop `<= -2.0%` and `max_bounce < 0.25 * (top - o)` from `wick_census.py` OURS); `MyTradingSys/backtest/layers/fabio/v3/models.py:138-191` (`model_b` has no knife or forced-flow filter at all) |
| R33: Never fade repeated high-speed absorption at stable velocity | Tom (GUEST: 4P5WAxyPCis) | if you see absorption happening at a very high speed, and you can see that it's being absorbed again and again, and the speed is stable in that sense, then the probability is very high that the absorption won't hold | 4P5WAxyPCis [no-ts, BEGIN] | Repeated absorption at stable high tape speed means the level is breaking (orders being eaten), so do not fade it—trade the breakout instead. | NOT_SEEN | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:675,691,784-786` (treats ANY `absorption_seen` on a probe that closes inside within 3 bars as `FAST_REJECTION` fade confirmation, with no check for repeated absorption or tape speed); `MyTradingSys/backtest/layers/fabio/v3/models.py:126-132` (`_b_probe` treats any single `absb == sb` bar as a fade trigger, though `failed_auction` S5D at `MyTradingSys/backtest/layers/fabio/v3/signals.py:325-349` trades breakouts after in-balance absorption) |
| Context Gap 1 (Pattern 4): HTF bias from 1M candle colour `Phi(|d_atr|*1.5958/sqrt(t_left))`, 20M SMA, and 1w candle streaks vs. Weekly VPOC migration | Tom | The weekly profiles show me immediately if the V POX are rising, staying the same or even falling | Ld1dhjGdTCA [no-ts, MIDDLE] | Read higher-timeframe directional bias from whether weekly Volume Profile POCs (VPOCs) and value areas are migrating higher, flat, or lower. | NOT_SEEN (no 20M SMA, no Brownian `Phi` formula, no 3-week candle-colour streak stated by Tom or Fabio) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:43,69-77,106-129,424-455` (synthesizes `htf_bias` from 1M candle colour vs. `sma20`, Brownian `p_close_colour`, and `w_state['streak']['count'] >= 3`, while `prior_week_vp` at line 406 is only a single week and never checks week-over-week VPOC migration); NONE in `MyTradingSys/backtest/layers/fabio/v3/models.py` |
| Context Gap 2 (Pattern 5): 24h UTC Volume Profile vs. Cash-Session Profile | Tom | You can't say, I only trade the cash session. But then refer to 24-hour profiles. Why? That's inherently quite meaningless. | Of_wlv3xaZo [no-ts, END] | Cash-session traders must anchor Volume Profiles to the cash session, not 24-hour UTC days. | SOURCED: cash-session profile (NY 09:30-16:00 ET / DAX cash hours) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:355-381,405-408` (`prior_ny_session_profile` is defined at line 355, but `build_mtf_context` at lines 405-408 never calls it and instead builds `prior_day_vp` from whatever 24h bar slice is passed in); `MyTradingSys/backtest/layers/fabio/v3/signals.py:370-383` (`curve` builds session profile from `sess_open`, but is only called for adds in `MyTradingSys/backtest/layers/fabio/v3/manage.py:87-90`, never in `models.py`) |
| Context Gap 3 (Pattern 2): Market Profile (30-min TPO blocks, time at price, double distribution) | Tom | the price never actually stayed at this specific level for more than 30 minutes | 1utSjHs_Mq8 [no-ts, MIDDLE] | Use time-based Market Profile (30-minute TPO periods, single prints, buying/selling tails, double distributions) alongside Volume Profile to judge acceptance and levels. | SOURCED: 30 minutes (TPO block duration) | NONE (zero TPO / Market Profile functions in `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py` or `MyTradingSys/backtest/layers/fabio/v3/models.py`; also note `compute_volume_profile` at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:264-274` expands 1 bin at a time whereas `value_area` at `MyTradingSys/backtest/layers/fabio/v3/signals.py:143-153` expands 2 bins at a time) |
| Session Open Gap (Pattern 5): Skipping first 30 minutes of NY open vs. trading from bar 0 | Tom & Fabio | stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that. | Of_wlv3xaZo [no-ts, MIDDLE] | Wait out the first 30 minutes of the New York session (and evaluate the opening range size) before taking trades. | SOURCED: 30 minutes skip at NY open (also Fabio in `DyS79Eb92Ug` `[2:52]`) | `MyTradingSys/backtest/layers/fabio/v3/models.py:35,197,283,334,434` (only `model_c` waits `IB_MINUTES = 30`; `scan_model_a`, `scan_model_b`, and `scan_model_d` start scanning at `open_idx` = minute 0 of the session unless an external `gate` is passed, and `day_gate_open` at `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:151` defaults to `g="off"` in `model_c` line 194 and is absent from `model_b`) |
| Model C IVB Gap (Pattern 1 & 5): US-equities opening behavior & IB midpoint stop | Fabio | On this strategy, the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day | LQvv5xgy_ik [31:42] | The 30-minute Initial Balance (IVB) strategy relies on predictable opening behavior of US equities, where the extreme of the first 30 minutes gives directional value for the day. | SOURCED: first 30 minutes IB on US equities; IB midpoint stop and 1-attempt-per-day cap = NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:194-228,385-424` (applies `model_c` to 24/7 BTC, hardcodes structural stop at the IB midpoint `mid = (IBH + IBL) / 2.0` via `s * (entry - mid) + tick` at lines 199, 209, 219, 224, and allows only one qualifying bar attempt per day) |
| Execution Object Gap (Pattern 4): 40/80 Range Bars & Fixed Big-Trade Filter 60 vs. 1m Bars & 30-day Percentile | Fabio | the big trades guys are 60 the filter it's on 60 and you know what one time frame that I'm loving recently that is based on the range is the 80 range | Is1HvdfQm5c [25:05] | Execute on range bars (40 range or 80 range so NY-open volatility is not aggregated into one huge 1m bar) with a big-trade filter set to 60. | SOURCED: 40 range (`DyS79Eb92Ug` `[1:51]`), 80 range, and filter = 60 (`Is1HvdfQm5c` `[25:05]`, units NOT_SEEN) | `MyTradingSys/backtest/layers/fabio/v3/models.py:35,274-467` and `MyTradingSys/backtest/layers/fabio/v3/signals.py:25,45-48,58-63` (hardcoded to 1-minute time bars `MIN_MS = 60000` and 30-day 99th/99.9th percentile `b99`/`b999` volume columns) |
| Entry Order Type & Rest Validity Gap (Pattern 1 & 4): Buy-stop / Market / Half-candle limit vs. 3-bar Resting Limit or Next-Open Taker | Fabio | I can start to build by stop. | DyS79Eb92Ug [7:27] | Enter breakouts/reclaims via stop orders (`build by stop`) or immediate market execution while the bar is moving, rather than waiting for bar close + 3-bar resting limit. | NOT_SEEN (no 3-bar rest-limit expiration or 330-minute entry cutoff stated in transcripts) | `MyTradingSys/backtest/layers/fabio/v3/models.py:33-34,62-85,186,247,281` (only supports `entry_mode='rest'` maker limit at close of bar `k` expiring after `REST_VALID_B = 3` or `REST_VALID_D = 3` bars, or `entry_mode='confirm'` taker at next open, with hardcoded `last_entry_idx = open_idx + 329`) |
| Post-Fill Management Gap 1 (Pattern 4): Immediate / Event Break-Even and Structural Trail vs. `be_k * D` Distance Mode | Fabio & Tom | And the first position went to break even immediately. | 0jM5Y31YJak [no-ts, MIDDLE] | Fabio moves the stop to break-even immediately (`not even one candle` in `Is1HvdfQm5c` `[38:15]`); Tom either does not trail a planned target (`k0zm5NYn0IQ`) or moves the stop only where the opposite move is expected (`4MoNjEQ2Dd8`). | SOURCED: immediate / `< 1 candle` BE (Fabio); `be_k = 1.0 * D` distance = NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:89,138,195,232` (all 4 trade functions default to `mgmt='dist'` and `be_k=1.0`, which in `MyTradingSys/backtest/layers/fabio/v3/manage.py:28-32,155-164` waits for price to travel `+1.0 * D`—where `D` is inflated by `f * entry`—before moving to BE, and then immediately trails every `S6` control bar); `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:821-973` (has zero post-fill management) |
| Post-Fill Management Gap 2 (Pattern 2 & 4): Partial Profits, Scale-In from Fractional First Size, and Unwired Engine Adds | Tom & Fabio | Now, I didn't load it full size because I want to scale as we go up. | DyS79Eb92Ug [9:09] | Start with a partial position size to scale in as price moves in favor, and take partial profits at intermediate liquidity levels while letting a runner go (`k0zm5NYn0IQ`). | NOT_SEEN (exact first-entry fraction and partial-take fraction unstated; `MyTradingSys/backtest/layers/fabio/v3/manage.py:23` uses `MIN_ADD_FRAC = 0.25` NS-fixed) | `MyTradingSys/backtest/layers/fabio/v3/models.py:72,82` (calls `simulate_trade` in `MyTradingSys/backtest/layers/fabio/v3/manage.py:204-222`, which executes a single leg `q1=1.0` with a single exit and zero partial exits; `simulate_trade_legs` at `MyTradingSys/backtest/layers/fabio/v3/manage.py:225` is never called by `models.py`) |
| Post-Fill Management Gap 3 (Pattern 1 & 2): Re-entry After Stop-Out and Day Stop-Count / P&L Rules Unwired | Tom & Fabio | if I reach a maximum of 3 stop loss either I lower the exposure but usually a stop for the day | Is1HvdfQm5c [1:10:36] | Re-enter when the trade idea remains valid after a tight stop-out (`k0zm5NYn0IQ`), and stop trading for the day after 3 stop-losses (or if P&L drops back to break-even after being up, `fZlNGWvd2Ko` `[1:11]`). | SOURCED: max 3 stop-losses per day (`Is1HvdfQm5c` `[1:10:36]`); `-3.0 R` sum and `MAX_FIRST_LEGS = 10` = NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:189,227` (`model_b` breaks after one filled trade; `model_c` returns after one attempt; neither calls `first_leg_allowed` or `first_leg_risk` in `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:15-16,120-147`, which itself codes `DAILY_STOP_R = -3.0` R sum instead of 3 stop-outs and `MAX_FIRST_LEGS = 10` NO-SOURCE) |
| Asset Transfer Contradiction (Pattern 5): Fabio Order Flow on Bitcoin vs. US Index Futures | Fabio | Bitcoin guys, I don't use order from Bitcoin. I use on-chain analysis | Is1HvdfQm5c [15:41] | In `Is1HvdfQm5c` Fabio says he does not use order flow on Bitcoin (uses on-chain analysis), whereas in `DyS79Eb92Ug` (`[1:48:37]`, `[1:54:14]`) he says crypto order-flow scalping on Saturdays is extremely profitable; for US indices he trades NY session only (`Pz8f0wWW12M` `[29:00]`). | CONTRADICTION across `Is1HvdfQm5c` `[15:41]` vs. `DyS79Eb92Ug` `[1:48:37]` | `MyTradingSys/backtest/layers/fabio/v3/models.py:1-467` (applies US-index NY-session 1m order-flow models A/B/C/D directly to BTC weekday NY windows without resolving the BTC vs. US-index regime or weekend crypto scalping context) |

---

## 2. TOP 5 Mismatches Between Code (`auction_context.py` & `models.py`) and Rulebook / Transcripts

1. **Context & Phase Classifier Lost in Translation (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:424-455` & `MyTradingSys/backtest/layers/fabio/v3/models.py:291,335` / `MyTradingSys/backtest/layers/fabio/v3/signals.py:183` vs. R9, R10, Context Gaps 1–3):**
   - **What they do:** Tom classifies the market into Balance (60–70% of the time, read from Volume + Market Profile shape) vs. Trend (30% of the time), uses weekly VPOC migration (`Ld1dhjGdTCA`) and cash-session profiles (`Of_wlv3xaZo`, rejecting 24h UTC profiles as *'inherently quite meaningless'*), and switches setup families strictly by phase (*'Whether it's trend or balance because I have to use different setups there and that is absolutely crucial'*).
   - **What we coded:** `auction_context.py` builds 24h UTC profiles (`prior_ny_session_profile` at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:355` is dead code never called by `build_mtf_context`), computes HTF bias from a monthly candle colour vs. 20M SMA, a Brownian range formula `Phi(|d_atr|*1.5958/sqrt(t_left))`, and a 3-bar weekly candle colour streak (`R4`/`G2`), and never switches setups by phase (only changes `sizing_tier` at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:957`). Meanwhile, `MyTradingSys/backtest/layers/fabio/v3/signals.py:183` defines balance as a 60-minute 1m box (`R <= 0.8*sqrt(60)*ATR` and `|c - poc| <= 0.25*R`) that fires in only 3.1% of windows and ignores HTF/session profiles completely.

2. **Acceptance & Rejection Speed Turned into Arbitrary Bar Counts (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:591-602,724-748` & `MyTradingSys/backtest/layers/fabio/v3/models.py:32,127` vs. R3, R11, R33):**
   - **What they do:** Acceptance is qualitative—a close plus a new sideways range/equilibrium forming outside the level (`Sy-x5AQ9-Pk`, `qLnQan0KGmQ`: *'Not with quick spikes but with real acceptance'*). Rejection speed is tape/order-book tempo (`k0zm5NYn0IQ`, `-dMWA_bbm3o`), and high-speed repeated absorption (`4P5WAxyPCis`: R33) is a warning *not* to fade.
   - **What we coded:** `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724-726` hardcodes acceptance as `n_acc = 6` consecutive closes (or 4 early closes, or 6 bars parked inside the `0.15%` zone—which misclassifies a pre-breakout stall under resistance as `ACCEPTED`), and cites `accept80.py` (`2x30m` closes) in its docstring (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:13`) as `SOURCED`. Rejection speed is coded as `bars_beyond <= 3` (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:747`, which is 3 hours on 1h bars!) or `RECLAIM_BARS = 5` (`MyTradingSys/backtest/layers/fabio/v3/models.py:32`).

3. **Stop Geometry vs. Fee Gate & Distance Floor Conflict (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:48,863-909` & `MyTradingSys/backtest/layers/fabio/v3/models.py:38-43,101,199` vs. R16–R20):**
   - **What they do:** In swing/structural trades (R16–R18), Tom places the stop beyond the entire sideways accumulation floor / value zone (`M7ompiwv5co`). In intraday order-flow scalps (R19–R20), Fabio places a tight stop just behind the absorption candle (`9IliXww64uM`: 1–6 bps on NQ; Tom `k0zm5NYn0IQ`: 20 DAX points = ~8 bps).
   - **What we coded:** `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:868-874` places breakout/LVN stops only 25 bps inside the broken level (not below the sideways accumulation floor), while `SKIP_FEE_TRAP` (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:895-909`) rejects any stop under 40 bps on 10 bps round-trip taker fees—automatically rejecting 100% of Fabio's 1–6 bps stops and Tom's 8 bps DAX stops. Conversely, `MyTradingSys/backtest/layers/fabio/v3/models.py:38-43` (`d_and_stop`) artificially pads tight stops out to `D = max(f * entry, structural)` (5–8x wider than Fabio's actual stop), destroying the reward-to-risk ratio, or places Model C's stop at the arbitrary IB midpoint `mid = (IBH + IBL) / 2.0` (`MyTradingSys/backtest/layers/fabio/v3/models.py:199`).

4. **Post-Fill Management & Target Vacuum (`MyTradingSys/backtest/layers/fabio/v3/models.py:72-85,89-260`, `MyTradingSys/backtest/layers/fabio/v3/manage.py:28-32,155-164,204-222` & `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:931-947` vs. R21, R22, R25, Post-Fill Gaps 1–3):**
   - **What they do:** Fabio moves his stop to break-even immediately (`0jM5Y31YJak`: *'went to break even immediately'*; `Is1HvdfQm5c`: *'not even one candle'*), enters with a partial size to scale in as price moves (`DyS79Eb92Ug`), and targets the opposite range edge or curve extreme (`1:16` to `1:19` R:R in `8CWKfoSJu3c`). Tom requires R:R > 1.5 (`M7ompiwv5co` R25), takes partial profits (`k0zm5NYn0IQ`), defines targets at prior HVNs (R21) or 1:1 mirrored impulse legs at highs (R22), does not trail a planned target, and re-entries after a stop-out if the idea holds.
   - **What we coded:** `auction_context.py` has zero post-fill management, omits `hvns` from `build_mtf_context` levels (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:494-505`), has no impulse-mirror target (R22), and lowers the R:R floor to `1.20` (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:49`). In `models.py`, Models A, C, and D have `target=None` (`MyTradingSys/backtest/layers/fabio/v3/models.py:104,221,252`), no R:R floor is checked, `simulate_trade` runs a single leg with no partials and no wired adds, re-entries are blocked (`model_b` exits after 1 fill, `model_c` after 1 attempt), and the default `mgmt='dist'` waits for `+1.0 * D` (the padded stop distance!) before moving to break-even.

5. **Market Profile (TPO) & L2 Order-Book Blindness (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:205-330` & `MyTradingSys/backtest/layers/fabio/v3/models.py:1-467` vs. R6, R23, R24, R31, Context Gap 3):**
   - **What they do:** Across 23 videos (`3o1VVsfBmmU`, `1utSjHs_Mq8`, `-dMWA_bbm3o`, `3JqMyzE8jIQ`, `kXhIAug0Gh8`), Tom combines time-based Market Profile (30-minute TPO blocks, single-print fast-trend zones, buying/selling tails, open-drive no-support rules, double distributions) with Volume Profile, and front-runs visible L2 resting liquidity blocks by 1–2 ticks (R6, `4P5WAxyPCis`).
   - **What we coded:** Zero Market Profile / TPO logic exists anywhere in `auction_context.py` or `models.py`. In fact, where R31 explicitly warns that an open-drive buying tail / fast impulse leaves a single-print zone that *'really won't offer any support for me'*, `MyTradingSys/backtest/layers/fabio/v3/models.py:89-118,314` (Model A) actively places resting buy limits inside the impulse leg's LVN!

---

## 3. SINGLE BIGGEST HOLE

**The Uncoded Context-to-Setup Switch & Market/Volume Profile Phase Engine (Combined with Post-Fill Event Management):**

Neither `auction_context.py` nor `models.py` actually implements how Tom and Fabio read the market before and after entry:
1. **Before entry (Context & Phase Switch):** Both traders first determine whether the session is in **Balance** (60–70% of days: trade failed-breakout fades at cash-session VAH/VAL back toward POC/opposite edge) or **Out-of-Balance / Trend** (30% of days: skip the first 30 minutes of NY open, read weekly VPOC migration and Market Profile single prints / open-drive tails, and trade breakouts or trend pullbacks). In our code, `auction_context.py` replaces this with a 24h UTC profile (leaving `prior_ny_session_profile` uncalled) plus a monthly/weekly candle-colour and 20M SMA formula that never switches setup families, while `models.py` runs on a 60-minute 1-minute box (`MyTradingSys/backtest/layers/fabio/v3/signals.py:183`) that is blind to prior-day/weekly cash-session Value Areas and fires in only 3.1% of windows.
2. **After entry (Risk & Management):** Intraday order-flow entries rely on tiny structural stops behind absorption (1–8 bps) paired with **immediate** break-even (`not even one candle`), scale-ins, and partial exits toward high-liquidity targets (R:R > 1.5 to 19). `auction_context.py` blocks those trades outright via its 40 bps `SKIP_FEE_TRAP` gate and has no trade management, while `models.py` pads the stop to `D = max(f * entry, structural)` and defaults to `mgmt='dist'` (`be_k = 1.0 * D`) with `target=None` on Models A/C/D and one-exit-per-leg execution.

---

## 4. Verbatim Quote Verification Blocks (Gated by `verify_extract_quotes.py`)

#### R1: Breakout confirmed by strong impulse candle with volume
> "If we happen to go above this specific level here, for example, then first of all, we absolutely need to wait for a clear entry signal to confirm the move. That could be a strong impulse candle with volume, for example."
**Source GPS: M7ompiwv5co | MIDDLE**

#### R2: Delta divergence confirming seller exhaustion on 5m candle close
> "you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through. And the 5-minute was about to close right over here and that was my signal for the entry."
**Source GPS: 9IliXww64uM | MIDDLE**

#### R3: Fast rejection speed confirms immediate entry
> "The market showed me that there is rejection up here. And the market also showed me that the speed with which it rejected this is promising for me."
**Source GPS: k0zm5NYn0IQ | END**

#### R4: Breakout momentum driven by liquidity expansion
> "Trading volumes that have increased here, so we know that the momentum is driven by liquidity."
**Source GPS: M7ompiwv5co | END**

#### R5: Entering on absorption after aggressive buyers punch a wall
> "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position."
**Source GPS: 0jM5Y31YJak | END**

#### R6: Front running resting liquidity blocks
> "And then it's just really nice to position yourself one or two ticks ahead of that position because at first the market always since many people and also algorithmic systems see that, the market usually moves away from it at first."
**Source GPS: 4P5WAxyPCis | BEGIN**

#### R7: Pullback entry into low volume nodes in strong trend
> "when the market moves up or down and repeatedly, so to speak, low areas, meaning low volume areas are created, then it's actually a very good very good opportunity to join the trend"
**Source GPS: 4P5WAxyPCis | MIDDLE**

#### R8: Clear road with absent resistance signals rapid breakout push
> "When the market is a bit clear, meaning there's no resistance, the price gets pushed very strongly and very quickly in one direction."
**Source GPS: ACb0Qtt3DSQ | BEGIN**

#### R9: Classify market phase strictly into range or trend
> "And when I look at it this way and keep it simple and rudimentary, I quickly realize that markets can basically be classified into two phases. Phase one, those [clears throat] are the so-called range or accumulation phases. And phase two, those are the so-called trend phases."
**Source GPS: M7ompiwv5co | BEGIN**

#### R10: Trend vs balance dictates distinct setup families
> "Whether it's trend or balance because I have to use different setups there and that is absolutely crucial."
**Source GPS: Ld1dhjGdTCA | END**

#### R11: Real acceptance requires time and closes, not quick spikes
> "Not with quick spikes but with real acceptance."
**Source GPS: qLnQan0KGmQ | END**

#### R11b: Acceptance as a new sideways phase emerging beyond the level
> "does another sideways phase emerge after that? Then we have a new model where we can clearly say that the equilibrium, meaning the new acceptance, because the market then spends more time above or below there"
**Source GPS: Sy-x5AQ9-Pk | MIDDLE**

#### R12: High volume node acts as a reaction magnet
> "where high volume occurs, we often see a reaction when a market returns there."
**Source GPS: NkQeOVDTAec | BEGIN**

#### R13: Order flow confirms idea only at strong technical levels
> "Because if I also have a strong technical level here, then I know there was an exhaustion here, which means an extremum."
**Source GPS: y67l86cSqb8 | MIDDLE**

#### R14: Volume must be judged relative to historical baseline
> "whenever trading volumes decrease, supply and demand are no longer as high. This means that fewer large market participants are interested in being active in the markets at that time"
**Source GPS: YkclL6xgu-s | BEGIN**

#### R15: Trend emerges away from prior sideways boundaries
> "And you can see quite clearly that whenever a market moves away from such high or low points where a sideways phase previously ended, a trend emerges."
**Source GPS: M7ompiwv5co | MIDDLE**

#### R16: Stop loss placed strictly below previous sideways accumulation floor
> "I would always place the risk below the last sideways phase at the latest because if the market moves above this and then accepts the equilibrium again, that's initially an indication that it showed rejection up here."
**Source GPS: M7ompiwv5co | END**

#### R17: Stop loss placement where premise of trade is falsified
> "And that's why in swing trading a stop loss should always be placed where, at the end of the day, the opposite of your move is to be expected."
**Source GPS: M7ompiwv5co | END**

#### R18: Structural stop anchored below key technical support level
> "I say, my stop loss belongs right down here, below the support level. And finally, I say, now I have complete mathematical clarity regarding both my risk and my potential reward."
**Source GPS: M7ompiwv5co | END**

#### R19: Footprint granularity protects capital on stops
> "footprint charts are a great tool to make the whole process much more targeted with regard to protecting your capital."
**Source GPS: 3JqMyzE8jIQ | END**

#### R20: Tighter stop behind trapped market participants
> "as I saw the candle reabsorbing. Stop was likely somewhere above here"
**Source GPS: 9IliXww64uM | END**

#### R21: Profit target placed at high liquidity cluster / prior HVN
> "I'll define the next target where there was a lot of liquidity. Because the fact that the market will slow down there at first is simply a probability."
**Source GPS: M7ompiwv5co | MIDDLE**

#### R22: Target at all-time highs mirrors previous momentum impulse
> "Alternatively, if we happen to be trading at all-time highs, we simply mirror the current momentum move to the upside to determine our next target."
**Source GPS: M7ompiwv5co | MIDDLE**

#### R23: Price revisiting unfair levels returns first to fair value
> "The probability that a market will revisit an unfair price level is quite high. But first, it will usually return to the next fair price area."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

#### R24: Unfair single-print areas get revisited
> "The market never made a pullback from here upwards. And that's why we call this price area a fast trend. And the market profiler sees a single print area here."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

#### R25: Minimum reward to risk ratio threshold of 1.5
> "And only if that is, for example, at least greater than 1.5 or so, then I have a really great strategy that will make me money."
**Source GPS: M7ompiwv5co | END**

#### R26: Win rate evaluation requires 200 to 300 trade sample
> "You must determine your win rates for yourself, and you must know exactly what my average win rate is after many, many trades. I always say, you should have two or 300 trades."
**Source GPS: M7ompiwv5co | END**

#### R27: Three pillars of execution: Idea, Proof, Clean Risk Math
> "First, you have an idea. Second, you have proof that it's really time now to implement the idea. And third, you have a really clean risk management so that the math is on your side."
**Source GPS: zQTbdEweG3c | BEGIN**

#### R28: Daily closing patience avoids intraday overtrading
> "in swing trading, where we can simply wait for daily closing prices, we can trade much, much more patiently."
**Source GPS: M7ompiwv5co | END**

#### R29: Low reward to risk forces unachievable win rates
> "If we had a riskreward ratio of 1: one, you would need at least 51% without order fees just to break even."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

#### R30: Do not assume every fair value gap closes
> "Retail traders think that pretty much every gap will eventually be closed."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

#### R31: Open drive and buying tails offer zero support
> "if I know the rules of market profiling, then I know that this was simply an open drive here and the market just gave me a strong buying tail at this point and that really won't offer any support for me."
**Source GPS: 3JqMyzE8jIQ | END**

#### R32: Do not stand in the way of active institutional forced dumps
> "there's just no point in going against it. You just have to wait until you can see that it's over."
**Source GPS: DVZVE9rXGtU | MIDDLE**

#### R33: Never fade fast absorption at stable high velocity
> "if you see absorption happening at a very high speed, and you can see that it's being absorbed again and again, and the speed is stable in that sense, then the probability is very high that the absorption won't hold"
**Source GPS: 4P5WAxyPCis | BEGIN**

#### R34: A gap is not an entry trigger without predefined target
> "I can't just use this fair value gap as an entry trigger. I also need to know where is the probability high that the market will move back there."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

#### R35: Never fade big players establishing initial positions
> "if the big players start to move, if the big players have to start building positions, forget it."
**Source GPS: DVZVE9rXGtU | MIDDLE**

#### Context Gap 1: Weekly VPOC migration for higher-timeframe bias
> "The weekly profiles show me immediately if the V POX are rising, staying the same or even falling"
**Source GPS: Ld1dhjGdTCA | MIDDLE**

#### Context Gap 2: 24-hour profiles meaningless for a cash-session trader
> "You can't say, I only trade the cash session. But then refer to 24-hour profiles. Why? That's inherently quite meaningless."
**Source GPS: Of_wlv3xaZo | END**

#### Context Gap 3: Market Profile 30-minute time-at-price blocks
> "the price never actually stayed at this specific level for more than 30 minutes"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### Session Open Gap: Stop trading in the first 30 minutes of the New York session
> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that."
**Source GPS: Of_wlv3xaZo | MIDDLE**

#### Model C IVB Gap: US equities opening behavior and first 30 minutes
> "On this strategy, the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

#### Execution Object Gap: Big-trade filter 60 and 80-range chart
> "the big trades guys are 60 the filter it's on 60 and you know what one time frame that I'm loving recently that is based on the range is the 80 range"
**Source GPS: Is1HvdfQm5c | MIDDLE**

#### Entry Order Type Gap: Build position by stop order
> "I can start to build by stop."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### Post-Fill Management Gap 1: First position to break-even immediately
> "And the first position went to break even immediately."
**Source GPS: 0jM5Y31YJak | MIDDLE**

#### Post-Fill Management Gap 2: Partial initial size to scale in as price moves up
> "Now, I didn't load it full size because I want to scale as we go up."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### Post-Fill Management Gap 3: Maximum of 3 stop-losses per day
> "if I reach a maximum of 3 stop loss either I lower the exposure but usually a stop for the day"
**Source GPS: Is1HvdfQm5c | MIDDLE**

#### Asset Transfer Contradiction: Fabio on Bitcoin order flow vs. on-chain analysis
> "Bitcoin guys, I don't use order from Bitcoin. I use on-chain analysis"
**Source GPS: Is1HvdfQm5c | BEGIN**
