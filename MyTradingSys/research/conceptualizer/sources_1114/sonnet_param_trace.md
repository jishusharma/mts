# Gap hunt 1113: sonnet_param_trace (code-to-source trace, pattern 1, stage C/T)

Method: every numeric constant, threshold, window and boolean branch in six code files was listed, then each was searched in the 164 canonical raw transcripts (`origin/fast-track:raw_transcripts_canonical/`, read with `git archive`, regex over the whole text, Python). Code read from `origin/fast-track` (main checkout stale). Read-only; nothing committed.

Files traced (line numbers refer to the `origin/fast-track` copy):
- AC = `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py` (973 lines)
- SIG = `MyTradingSys/backtest/layers/fabio/v3/signals.py` (443), MOD = `.../v3/models.py` (467); helper reads: `costs.py`, `manage.py` headers only
- VPR = `MyTradingSys/backtest/vp_return_to_value.py` (381)
- TVP = `MyTradingSys/research/sim_desk/studies/tom_vp.py` (288)
- LS = `MyTradingSys/tools/live_aid/levelstory.js` (91)

Labels: SOURCED = exact transcript quote + id. SCON = SOURCED-CONCEPT-OURS-NUMBER (he names the idea, we picked the number or mechanics). OURS = no trader statement found. MISLABELLED = a comment/doc says SOURCED (or attributes to a trader) and no quote supports it, or the source is our own file.
All quotes in this file were machine-checked as exact substrings of the named raw transcript (whitespace/timestamps/`>>` normalised). Speaker: Tom = Tom Vorwald channel; Fabio = Fabio Valentini (Chart Fanatics, "Fabervaale"); `7IxfsuD2wCM` = Krown and `j-JVi02_C88` = Benjamin Cowen (NOT Tom/Fabio, cited only to show where a number really comes from); `5Ljfwvtktek` = interview guest. `4P5WAxyPCis` speaker not stated in the file (guest on Tom's channel).

---------------------------------------------------------------------------------------------------------

## 1. Gap table (brief format)

| id | stage | pattern | gap in one line | evidence | in iter 1? | fix |
|---|---|---|---|---|---|---|
| PT-01 | T | 5 | Fabio himself says he does NOT use order flow on Bitcoin, yet Fabio v3 (S1-S9, Models A-D) is built and tested on BTC perp 1m bars. No doc records his statement; the transfer is treated as a neutral port. | Is1HvdfQm5c [15:41]: "Yes, but Bitcoin guys, I don't use order from Bitcoin. I use on-chain analysis". Contrast FawPrRUGNpk: "Financial markets, stock, crypto, everything, every financial asset class that comes to your mind, it's moved by a flow of orders matching liquidity." (concept transfers; his practice does not). | N (iter 1 Q14 covers Tom-on-BTC only) | re-frame (label v3 "transfer, not his practice"); extract (any Fabio/Tom line on BTC order-flow practice) |
| PT-02 | T | 1, 4 | His "big trade" is a FIXED size filter (60 on the chart) on RANGE bars (40-range at NY open, "close to the 5 minutes"; 80-range), because 1-minute candles are "huge" and aggregate the data. v3 uses a data-relative 99th/99.9th percentile of the prior 30 days on 1-MINUTE time bars (SIG:25-41 header P05; MOD all bars `MIN_MS`). The percentile, 30 d, tier switch VR 1.5 / 20 d / min 10 (SIG:32-34) have no transcript. | Is1HvdfQm5c [1:29:41]: "the big trades guys are 60 the filter it's on 60 and you know what one time frame that I'm loving recently that is based on the range is the 80 range". DyS79Eb92Ug [5:33]: "I made the 40 range now. So it's a range chart because when you are in New York opening if you do one minute candle you can have huge candle and all the data inside gets aggregated." DyS79Eb92Ug [50:53]: "40 range is really close to the 5 minutes." | N | extract (units of "60": contracts? which instrument?); re-code (range or volume bars + absolute-size filter scaled to BTC notional); test (percentile vs fixed-lot on same days) |
| PT-03 | C | 1, 4 | The "balance" our S1 detects is not his balance. He says balance is 60-70% of the time (Tom: "about 70%"); our S1 `R <= 0.8*sqrt(N)*ATR_N` and `|c-poc| <= 0.25R` (SIG:183-205, constants :26-27) is true in ~3.1% of 1m windows (FACTS E16, from FABIO_V3_L3_NOT_MEASURED). A 20x gap between the trader's base rate and our operationalisation is proof the definition is something else (engine "deaf": A, B, D never fire). | BB3c8visnkI: "depending on the profile shape, but especially 60 to 70% of the time, we have so-called balance equilibrium profiles". Ly62G168MkQ: "And you have to know sideways phases make up about 70% of the market." | Partly (iter 1 Q1/Q2 give the 60-70% numbers; nobody compared them to S1's 3.1%) | re-frame (S1 = our "tight 60m box", not his balance); re-code (balance = sideways phase by closing prices / profile shape) |
| PT-04 | C | 4 | The HTF ladder (AC:424-454, 464-483) is a CANDLE ladder (1M colour vs 20M SMA, weekly streak >= 3, forming-candle P_keep). Tom's higher-timeframe step is the WEEKLY VOLUME PROFILE: VPOC/value rising, flat or falling, double distributions. The streak/"N red weeks" idea appears only in Cowen (`j-JVi02_C88`), and Tom shows SMA-200 as the popular method he sets aside for sideways-phase reading. No 20-period SMA, monthly colour, or streak count exists in any Tom/Fabio transcript. | Ld1dhjGdTCA: "The weekly profiles show me immediately if the V POX are rising, staying the same or even falling". -dMWA_bbm3o: "The balance, despite swinging down sharply at times, is situated quite high up across all the weekly candles. And then we have a beautiful, what's called a double distribution here." Sy-x5AQ9-Pk: "they very much like to use a so-called moving average, usually calculated over 200 days." j-JVi02_C88 (Cowen): "you had about seven or you had about nine weeks in a row that were just simply red". | Partly (FACTS B1: "idea SOURCED, every threshold OURS"; the source MISMATCH, candle vs profile, is new) | re-code (weekly VPOC/VAH/VAL migration as HTF bias); re-frame (ladder = Cowen-style cycle read, not Tom) |
| PT-05 | C/T | 3, 4 | LVN is four incompatible things across the sources, our code has a fifth. Tom: low-volume area is a magnet the market "likes to fill in"; a counter-trend scalp at the LVN edge when interaction is strong; repeated LVNs = join-the-trend. Fabio (o-w5Gxss6T0): the fair-value-gap/LVN is the lowest-volume bin INSIDE the value area of a fixed A-to-B profile, one tick wide, and price rejects there. Ours: AC `lvn_ratio 0.25*POC` contiguous bins (AC:209,285) as a "FAST_TRAVERSE" trend level; v3 `<= 0.5*upper-median` single-bin local minimum (SIG:36,158-169) as a pullback entry for Model A; Java computes LVN and never consumes it. | 0CrkbfuIhkc: "that's a typical low volume area that the market then likes to fill in." 4P5WAxyPCis: "when it comes into such a low volume area and we see that suddenly at the edge or the low of this low volume area, there is very strong interaction." and "when the market moves up or down and repeatedly, so to speak, low areas, meaning low volume areas are created, then it's actually a very good very good opportunity to join the trend". o-w5Gxss6T0: "It's where the volume didn't transacted in a balanced way." | Partly (FACTS C5 notes Fabio's inside-VA definition; the Tom fill-magnet and edge-scalp uses are new) | re-code (Fabio LVN = min bin inside VA of a swing profile; Tom fill-target as a target type); test |
| PT-06 | C | 1 | Acceptance has three code definitions and none has a trader number. AC default 6 x 5m closes (AC:724, "OURS") with `n_early = round(2/3 N)` and `bars_in_zone >= 6` branches (AC:725-726, OURS, no doc); LS 2 closes of 15m (LS:42); TVP `accept_n` 6 on 5m (TVP:36). The module docstring still calls 6 bars "2x30m closes ... [SOURCED: accept80.py 77% ...]" (AC:13-14): wrong twice (6x5m = 30 min, not 2x30m = 60 min; `accept80.py` is our file and 77% is a same-day drift, not a trader figure). LS header: "2 closes, as accept80.py uses 2 x 30m" (LS:5-6) = 2x15m = 30 min, half of what it cites. | Tom gives no count: Ly62G168MkQ (iter 1 Q3) "the moment it accepts these levels best via closing price and sideways phase..." ; Sy-x5AQ9-Pk "And and this is the most important thing, does another sideways phase emerge after that?" Only numeric near-miss: 5Ljfwvtktek (guest) "if it stays there longer, let's say at least four or five candles". | Y for the body (card census-acceptance-threshold-mislabel-1109); N for the stale docstring (AC:13-14), LS:5-6, and the three-way inconsistency | re-frame (fix 2 comments); re-code (one shared acceptance function); test |
| PT-07 | T | 4 | Tom's trade build is not what TVP/AC build. Tom plans the target at a PREDEFINED level (prior value / profit planning "about as large as that first impulse"), averages RR "2 2.5 as a rule", and explicitly does NOT trail: he explains why he did not trail a runner. TVP: market entry, stop 1.0 x ATR14(1h) (TVP:36,48), target POC or one VA width or 2R (TVP:34,254-266). AC: stop at sweep extreme + 5 bps (25 bps min for acceptance), nearest qualifying node, plus a runner (AC:826,868-947). FACTS A6 attributes "trail aggressively" to BOTH traders; for Tom the transcript says the opposite. | UOBgXV20yCM: "Is exactly an average risk-reward ratio of a good 2 2.5 as a rule." and "Many say, "Yes, why didn't Tom do that?" I can tell you, because I simply know from my mathematics, this plannable distance has often resulted in the following for me." 7BQPMJ39WpI: "you can make a trend accelerated trade down here, and this trade is usually, and this is the great thing, to be valued in terms of profit planning, about as large as that first impulse already showed you." | N (iter 1 x2 covered stops/adds; the no-trail statement and the measured-move target are new) | re-code (measured-move target = first impulse size; no-trail variant); re-frame FACTS A6 |
| PT-08 | C | NEW | Whole decision layer missing: day-skip / event / gap gate. Tom's step 2 of 13 is "will I even trade today", GDP/news means do not hold positions, and a gap is first classed closable vs breakaway before any setup. None of the six files has a no-trade-day, news or gap branch (TVP/VPR run every UTC day; AC and v3 have only fee/RR/knife/session gates). | Ld1dhjGdTCA: "will I even trade today or have such groundbreaking things happened overnight that brings us to the gap so I'd better stay on the sidelines for now". Fj4FDZQxw0I: "Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will." | N | extract (his gap and news rules with numbers, if any); re-code (day filter); test |
| PT-09 | C | 3 | The "70% return to value" count (VPR) tests a claim stated for a different object: the quote ties the 70/30 to the profile shape ("especially when the curves look like bell curves") and to the weekly (and then daily cash-session) value area; the target is to "get back into the area ... equilibrium". VPR takes every UTC day regardless of profile shape, event = first 5m close beyond prior-day VA (VPR:13,51), return = touch of POC (VPR:54), day-end censoring (VPR:53-56). No shape condition, no week variant in the count, no "back into area" primary. | BB3c8visnkI: "Especially when the curves look like bell curves, the market participant will try to bring the price back into this range." and "within this zone here the market has traded 70% of the total liquidity for this week." and "these profiles only show you the period where the so-called cash session is". | Partly (iter 1 Q2 "three 70s"; the bell-curve/profile-shape condition and weekly anchor of the claim are new) | re-frame (E6/E7 tested a different claim); re-code (shape filter: balance profile only); test |
| PT-10 | T | 5 | IVB/Model C and the NY-window gate rest on a reason Fabio gives for US EQUITIES, and he waits 30 minutes before trading the open. Code: IB = first 30 one-minute bars after 13:30/14:30 UTC, break with big push, one try per day, entries until open+329 min (MOD:35,194-228, 280). On BTC there is no opening auction; the anchor is arbitrary UTC clock. | LQvv5xgy_ik [31:51-31:53]: "the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening" and "that the bottom of the first 30 minutes is giving a lot of value in the direction of the day". DyS79Eb92Ug [4:17]: "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session". | Y for session transfer (iter 1 pattern 5); N for his stated equity-specific reason and for "he waits" | re-frame (Model C = equity-open idea ported to a BTC clock) |
| PT-11 | T | 4 | Live Aid "evidence" set (LS:46-68) is built from Bollinger, WaveTrend, open interest and a 15m close, under a header that credits Tom (auction) and Fabio (order flow). Fabio rates Bollinger F tier and RSI D tier; Tom names Bollinger only negatively (S7). WaveTrend/OI/BB-position carry vote weights (+1/+1/0) that decide the printed "idea" (LS:72,77: turn or thru >= 3). | 3JZH06L28us (Fabio): "It's a proxy for volatility. It change every time. I never managed to be profitable with it." and "RSI. D tier. It's a lagging indicator and I will not use it." | N | re-frame (header: BB/WT/OI are OURS/analyst-call context, not T/F); test (does idea hit-rate change without BB/WT? E29 says coin flip overall) |
| PT-12 | T | 4 | Level-failure logic is first-probe-only; the trader's rule is that a level weakens with every test, and a volume spike must TRADE OFF afterward. AC picks the FIRST probing bar in the last 12 bars and never counts prior touches (AC:617-624); LS looks back 3 bars (LS:12,34). AC "effort" = `max_rel_vol >= 2.0` anywhere in the window (AC:703,784) with no "then volume falls" test. | Is1HvdfQm5c [30:34]: "remember that every time that you attack the level the level gets weaker because other orders gets filled". HySZZSjMxF8: "When the volume spikes strongly at a high point and this elevated volume is then traded off again, you have the confirmation for a clean counter trade." | N | re-code (touch counter per level; spike-then-fade confirmation); test |
| PT-13 | T | 4 | Entry-bar mismatch: Fabio reads 1m and 5m together and takes the trigger at the 5-minute close, on bubble (big-trade) data; v3 evaluates every signal on 1m closes (S5 trigger on the 1m close, SIG:307-322; windows m in {5,15} bars) and never reads a 5m close. At NY open he switches to range bars because 1m candles are too big (PT-02). | 9IliXww64uM: "And the 5-minute was about to close right over here and that was my signal for the entry." (iter 1/FACTS A3 location [8:28]) + DyS79Eb92Ug [5:33] above | N | re-code (5m-close trigger variant or range bars); test |
| PT-14 | C | 3 | Sizing tier `full_with_htf` vs `scalp_counter_or_range` (AC:953-957) and `min_net_rr 1.20` (AC:49) have no trader source and sit BELOW both traders' stated floors: Tom averages "2 2.5" (UOBgXV20yCM) and swing needs "at least ... 1.5" (M7ompiwv5co per FACTS A8). Tom's sizing is % of wealth (iter 1 Q12), Fabio's is "only risking the profit of the day" (fZlNGWvd2Ko). The tier uses the PT-04 candle bias. | UOBgXV20yCM quote in PT-07; sizing quotes in iter 1 Q12 | Partly (RR floor 1.5 in FACTS; the sizing tier itself unsourced is new) | re-frame (tier = OURS); re-code (floor >= 1.5) |
| PT-15 | T | 1 | Internal inconsistency between our own modules: AC and v3 give different value areas for the same data (AC one-bin expansion up>=dn; SIG two-bin pair expansion with `up = v[z+1]+v[z+2]`, AC:261-274 vs SIG:128-155), different POC tie rules, different bins (AC 50 USD hlc3 or spread; SIG 50 re-binned from 10 fp; TVP/VPR 10 USD via `vp_pivot_probe.build_profile`), different LVN rules, different stop buffers (v3 `+1 TICK` = 0.1 USD ~ 0.1 bp, MOD:101,175; AC 5 bps / 25 bps). Results from the six files are not comparable with each other. | code only (AC:261-274, SIG:128-155, MOD costs TICK=0.1, TVP:152-154 `bin_width`) | N | re-code (one profile library); test (same day, three VAs) |
| PT-16 | T | 1 | `NAKED_PCT = 0.003` is labelled "SOURCED: NakedPocTracker.java:26" (VPR:28): the "source" is our own Java constant `REVISIT_THRESHOLD_PCT = 0.003 // 0.3%`. Naked-POC as a concept exists in the transcripts (BVpYGKz9PBU "Naked PC's"; Is1HvdfQm5c "nice level with the naked POC") but no percentage does. | VPR:28 vs `src/main/java/datafeed/NakedPocTracker.java:26` | N | re-frame (OURS) |
| PT-17 | C | 4 | Tom's profile unit for "time at price" is the 30-minute block (TPO): a single print is a price "never actually stayed at ... for more than 30 minutes"; acceptance is "more time above or below". All our profiles are volume-per-price from 1m/5m bars; no TPO count, no single-print detector, no "two single prints better than one". | 1utSjHs_Mq8: "the price never actually stayed at this specific level for more than 30 minutes". 4P5WAxyPCis (iter-1-adjacent): single prints "if there are two, it's always better than if there's only one". | Partly (iter 1 tf-x4 notes 30-minute TPO block) | re-code (TPO/30m time-at-price counter beside volume profile) |
| PT-18 | C | 3 | Tom's "re-enters an old value area and finds acceptance, then profile fully traversed" (the rule `accept80.py` reproduces as the Dalton 80% rule) is described as Tom's rule in 1utSjHs_Mq8, yet FACTS B3 labels it "Dalton idea". The traded counterpart (AC Setup 2 / TVP ACCEPT: "trade on away from value", target one VA width, TVP:34,262) is the OPPOSITE direction (away from value) of the re-entry traverse (through value to the far side). | 1utSjHs_Mq8: "a market re-enters an old value area and finds acceptance there, then we know there are rules that clearly tell us the probability is high that the profile will be fully traversed" | N | re-code (re-entry-and-accept = traverse-to-far-edge setup, directly from the quote); test |

## 2. Branches the code has that no trader describes (all OURS)

| where | branch | note |
|---|---|---|
| AC:747-764 | STALE_REJECTION (reclaim older than `max_bars_since_reclaim` 3 bars -> skip) | no trader says a setup expires after N bars |
| AC:766-783 | REJECTED_KNIFE_SKIP (2% / 25% / 12 bars, fail closed if touch_idx < 3) | concept near Ly62G168MkQ "a real impulse always arises when no large pullbacks take place" (SCON), no figure |
| AC:726 | `n_early = round(2N/3)` accept-while-outside, and `bars_in_zone >= 6 and not probed` => ACCEPTED/balance_hold | invented, undocumented elsewhere |
| AC:895-909 | SKIP_FEE_TRAP, SKIP_LOW_RR (`max_fee_r` 0.25, `min_net_rr` 1.2) | operator fee decision d-stops-follow-trade-1106, not a trader rule |
| AC:946-947, 953-957 | primary + runner target, sizing tier | OURS |
| AC:424-454 | "nascent" month flag (elapsed < 0.10 and P_keep < 0.60), `p_close_colour` Brownian formula | OURS math (SIGMA_K = 2*sqrt(2/pi)), no trader uses candle-colour probability |
| MOD:32-36 | Model B 5-bar reclaim window, 3-bar rest validity, Model D 3-bar rest + cancel on level failure | OURS (P36/P39 "NS-fixed") |
| MOD:216-228 | one IVB attempt per day (first qualifying bar only) | OURS |
| SIG:393-442 | S8 exhaustion clause numbers 15 and 60, climax variant | concept of (a)/(b) is SCON (below), numbers OURS |
| TVP:182-191 | `migration()` = yesterday's value ENTIRELY beyond the day-before's, used to skip counter trades | concept SCON (Ld1dhjGdTCA "V POX rising/falling"); "entirely beyond" is OURS |
| TVP:230-241 | RETURN/FADE trades "dropped (exit) after N consecutive closes outside value" | OURS |
| VPR:201 | censoring audit `CENS_MIN_LEFT = 12`, placebo cycle d, `NEAR_MAX_D = 1.0` | OURS, post-hoc |
| LS:42 | `nb >= 2 && prevIn ? 'ACCEPTED' : nb >= 2 ? 'ACCEPTED'` (both arms identical, dead branch) | code smell; `prevIn` has no effect |
| LS:45-60,72,77 | vote weights (BB +1, wick +1, vol +1, absorb +2, CVD +/-1, close -3/-1, trap +2, WT +/-1), idea threshold `idea: 3` | OURS |

## 3. Branches the traders describe that the code lacks

| trader statement (id) | coded? |
|---|---|
| Day-skip / news / gap-closable vs breakaway (Ld1dhjGdTCA; UOBgXV20yCM "I had to evaluate whether this gap ... is likely to be closed") | none (PT-08) |
| Opening range large = unlikely to hold, small = likely holds (Fj4FDZQxw0I) | none (IVB in MOD uses a fixed 30 bars, no size filter) |
| Weekly VPOC/value migration and double distribution as bias (Ld1dhjGdTCA, -dMWA_bbm3o) | TVP migration() only as a skip filter on 1-day profiles; AC uses candle colour instead (PT-04) |
| Profile shape (bell vs trend profile, P/B/D) conditions the 70/30 claim (BB3c8visnkI, m3IMdc7QwN4) | none (PT-09, PT-03) |
| Low-volume area as fill target / edge scalp / trend-join (0CrkbfuIhkc, 4P5WAxyPCis) | partial: one use each in AC / v3, not the others (PT-05) |
| Volume spike must trade off before the counter trade (HySZZSjMxF8) | none (PT-12) |
| Level weakens with each test (Is1HvdfQm5c [30:34]) | none (PT-12) |
| Single prints, "two is better than one" (1utSjHs_Mq8, 4P5WAxyPCis) | none (PT-17) |
| Re-entry into old value + acceptance => traverse profile (1utSjHs_Mq8) | none as a trade (PT-18) |
| Planned target = size of first impulse; no trailing of a planned target (7BQPMJ39WpI, UOBgXV20yCM) | none (PT-07) |
| Partials, "let part of the position keep running" (e83njGZFrPw) and "I'll add to the position again at the breakout." (4MoNjEQ2Dd8) | adds only in Fabio v3 (manage.py); Tom side none |
| Heat-map/L2 wall and "one or two ticks ahead" of a big resting order (4P5WAxyPCis) | not codable on candles (FACTS C4: 34 of 97 rulebook rows need L2) |
| Counting closing prices / P-B-D structure (iter 1 Q1) | none (confirmed, 116 transcripts, no number) |

## 4. Sourced concepts the code does implement (so the table is not one-sided)

| code | concept source |
|---|---|
| SIG:36 S7 `curve` premium/discount used to gate adds (manage.py `add_allowed`) | 8CWKfoSJu3c [2:05]: "I could only position myself in discount and is not the best idea when you are already loaded with 10 contracts here to raise the exposure low in the curve." (numbers: none needed) |
| SIG S8(a)/(b) exhaustion (big trades stop pushing; opposite balance forms) | 0jM5Y31YJak: "I start to see that the big trades are not pushing anymore the price down." (15 and 60 are OURS) |
| SIG S3/S5D effort-vs-result, failed auction | o-w5Gxss6T0, 0jM5Y31YJak (FACTS A4); thresholds OURS |
| VA share 0.70 (AC:45, SIG:35, VPR) | aursfDVYzUk: "As a rule, you use 68.2 or 70% of all trades of the day"; Pz8f0wWW12M: "68% of the volume of the distribution" (so 0.70 and 0.682 are both his; code never tests 0.682) |
| MOD:35 IB 30 min | LQvv5xgy_ik (but see PT-10: his reason is equity-specific) |

## 5. Top 5 gaps

1. **PT-04** HTF ladder is a candle ladder (1M colour vs 20M SMA, streaks, P_keep) with its only streak/MA source in Cowen's video; Tom's higher-timeframe step is weekly VOLUME-profile VPOC/value migration. Feeds AC sizing tier and bias for everything downstream.
2. **PT-03** Our S1 "balance" fires in ~3.1% of windows; he says balance is 60-70% of the time. The state machine behind Models A, B, D is gated by something that is not his concept, which is why those models "never fire".
3. **PT-02** Big trades: he uses a fixed 60 filter on 40/80-range bars; we use a 99/99.9th percentile on 1-minute bars. The flow signal that all of v3 depends on is measured on a different object.
4. **PT-01** Fabio states he does not apply order flow to Bitcoin; the entire v3 family is a BTC transfer that no document flags as such.
5. **PT-09** The 70/30 count tests every UTC day; his claim is tied to bell-curve (balance) profile shape and a weekly or cash-session profile.

**Single biggest hole: PT-03 / PT-04 together, the context layer.** The two things the traders do before any setup (read whether the market is balanced by profile shape, and read the weekly value migration) are both replaced in code by candle statistics and a rolling 60-minute box. Every setup in the six files sits downstream of that substitution, so a negative result on setups says nothing about their context-first method. (Pattern 4, method lost in translation, with pattern 1 supplying the numbers.)

---------------------------------------------------------------------------------------------------------

## Appendix A. Full parameter list

Format: `loc | what | value | label | evidence`. "none" = searched, not found in the 164 transcripts (regexes in section A-end).

### A.1 AC (auction_context.py)

| loc | what | value | label | evidence |
|---|---|---|---|---|
| 43 | SIGMA_K = 2*sqrt(2/pi) (Brownian range constant) | 1.5958 | OURS | none; math, no trader uses candle-colour probability |
| 44 | DEFAULT_BIN_SIZE | 50 USD | OURS | none ("bin size", "tick size", "row size" 0 hits) |
| 45 | DEFAULT_VA_SHARE | 0.70 | SOURCED | aursfDVYzUk "68.2 or 70%"; Pz8f0wWW12M "68%" |
| 46-47 | taker RT 10 bps, maker 2 bps/side | from fees.py | OURS (venue, Deribit) | not a trader quantity |
| 48 | DEFAULT_MAX_FRICTION_R | 0.25 R | OURS (operator d-stops-follow-trade-1106) | Fabio stops 0.014-0.061% (FACTS A6) contradict it as a trader norm |
| 49 | DEFAULT_MIN_NET_RR | 1.20 | OURS | Tom "2 2.5" (UOBgXV20yCM); swing 1.5 (M7ompiwv5co); below both |
| 51-52 | BEARISH/BULLISH_HTF_BIASES sets | strings | OURS | PT-04 |
| 54-61 | side aliases support/val/low, resistance/vah/high | map | OURS | n/a |
| 80-93 | ATR14 = mean TR of 14 closed bars, needs 16 bars | 14 | OURS number; ATR use SCON | 3JZH06L28us: "ATR it's B tier. You can use it to frame the correct risk and points to manage the stop loss and take profit, but on itself, it's not giving you any kind of edge."; UOBgXV20yCM uses ATR as a key figure for expected opening move; no "14" |
| 96-103 | SMA length 20, includes forming bar | 20 | OURS | "20 period moving average" appears only in -NXzJs5JRks, LD_LOEeKzMs, PpysVy2NNQ4 (other analysts); Sy-x5AQ9-Pk shows SMA-200 as the conventional tool, not 20 |
| 106-129 | closed_streak R4/G2 colour counter | n/a | OURS (concept only in Cowen j-JVi02_C88) | PT-04 |
| 135 | sma_len default 20 | 20 | OURS | as above |
| 156 | candle validity tolerance 1e-9 | tiny | OURS | n/a |
| 160-164 | pos_in_range, upper/lower wick % | formula | OURS | wick-share thresholds not in T/F (9 "wick" files are other analysts) |
| 172-173 | tau / t_left from now_ms and close_t | formula | OURS | none |
| 176-177 | d_atr = (c-o)/ATR14, p_keep | formula | OURS | none |
| 209 | lvn_ratio | 0.25 of POC volume | OURS | PT-05 |
| 238-247 | spread_range option, hlc3 binning, `+1e-9` floor | n/a | OURS | none |
| 261-274 | VA expansion: one bin, up>=dn -> up | rule | OURS (conv. matches CME one-bin? SIG uses pairs) | PT-15 |
| 285-309 | LVN runs: bins <= 0.25*POC, bounded by strictly higher neighbours | rule | OURS | none |
| 315 | HVN: local max and >= 0.5*POC, not POC | 0.5 | OURS | none |
| 333-352 | NY cash session 09:30-16:00 ET with DST rule | 570-960 min | SOURCED in concept (cash session) | 9IliXww64uM "the volume profile of the regular trading hour session, the so-called New York session"; Pz8f0wWW12M "I only trade in the New York session" (FACTS A7); BB3c8visnkI "these profiles only show you the period where the so-called cash session is". Hours: standard NYSE; BTC use is transfer (PT-10) |
| 366, 373 | prior_ny_session_profile look-back 6 days, weekdays only, holidays not modelled | 6 | OURS | n/a |
| 405-407 | prior day / prior week / developing day profiles at 50 USD | 50 | OURS | Tom's week/day profile concept SOURCED (BB3c8visnkI, Ld1dhjGdTCA); anchors UTC (OURS), his = cash session |
| 429 | nascent month: elapsed < 0.10 and P_keep < 0.60 | 0.10, 0.60 | OURS | none |
| 430-441 | 1M colour x SMA20 4-way bias | rules | OURS | PT-04 |
| 449 | weekly streak >= 3 sets bias when neutral | 3 | OURS | none in T/F |
| 526-567 | knife: lookback 12 bars, drop/rise >= 2.0%, bounce < 25%, fail closed touch_idx < 3 | 12, 2.0%, 25%, 3 | SCON (concept: Ly62G168MkQ "a real impulse always arises when no large pullbacks take place, but it goes straight in one direction or the other"); numbers OURS (wick_census origin) | none for figures |
| 574 | zone_tol_pct | 0.15% | OURS | none |
| 576 | max_bars_since_reclaim | 3 | OURS | "speed" SOURCED TOM-010 without a number (FACTS B3); iter 1 Q4: speed = tape tempo, not a bar count |
| 578 | bar_minutes default | 5 | OURS | n/a |
| 617 | touch scan window | last 12 bars | OURS | none |
| 637 | pre-touch volume baseline | up to 48 bars median | OURS | none |
| 675, 691 | absorption: delta sign vs candle, or wick >= 50% of range and rel_vol >= 2.0 | 0.5, 2.0 | OURS number; concept SOURCED (absorption) | wick/range ratio none; rel_vol 2.0 nearest quote is Krown 7IxfsuD2wCM "you'll see typically around like two times the average of the last 30 days" (not T/F) |
| 703 | LVN fast traverse: 1-3 bars beyond, rel_vol >= 2.0 | 3, 2.0 | OURS | PT-05 |
| 724 | accept N | 6 bars (or accept_minutes/bar_minutes) | OURS; docstring MISLABELLED (AC:13-14) | PT-06 |
| 725 | n_early | round(2N/3) | OURS | none |
| 726 | bars_in_zone >= 6 and not probed -> ACCEPTED | 6 | OURS | none |
| 747 | fast rejection requires bars_beyond <= 3 | 3 | OURS | none |
| 784 | has_effort = rel_vol >= 2.0 or absorption | 2.0 | OURS | PT-12 |
| 826 | stop_buffer_pct_10k default | 5.0 bps | OURS (concept: Is1HvdfQm5c/FACTS "cover yourself above the area") | buffer none |
| 868, 873 | acceptance/LVN stop buffer min | 25 bps | OURS | none |
| 912-947 | qualifying targets sorted by nearest, 2nd = runner | n/a | OURS; "next high-volume price" SOURCED (qLnQan0KGmQ TOM-018) | node target SCON; planned-target-by-impulse (PT-07) not coded |
| 953-957 | sizing tier full_with_htf / scalp | n/a | OURS | PT-14 |

### A.2 SIG (signals.py) and MOD (models.py)

| loc | what | value | label | evidence |
|---|---|---|---|---|
| SIG:25 | B_PROF bin | 50 USD | OURS (P41 SIM) | none |
| SIG:26-27 | BAL_POC_BAND, K_BAL | 0.25, 0.8 | OURS ("NS-fixed") | none; PT-03 |
| SIG:28 | DRIFT_Q | 0.25 | OURS | none |
| SIG:29-31 | EFFORT_L 60, R_ABS 0.25, R_CTL 1.0 | 60, 0.25, 1.0 | OURS (FACTS: "0 of 8 grid rows SOURCED"); concept effort-vs-result SOURCED; his threshold "almost zero" (0jM5Y31YJak per FACTS A4) | z-score mechanics: none |
| SIG:32-34 | VR_TIER 1.5, VR_DAYS 20, VR_MIN_DAYS 10 | as listed | OURS | PT-02 (he uses a fixed 60 filter) |
| SIG:35 | VA_PCT | 0.70 | SOURCED | aursfDVYzUk |
| SIG:36 | LVN_FRAC | 0.5 x upper-median | OURS | PT-05 |
| SIG:37-38 | S8_AGE 15, S8_N 60 | 15, 60 | OURS (concept SOURCED 0jM5Y31YJak) | none for numbers |
| SIG:39-40 | S8_Z_HI 2.5, S8_P 0.10 | 2.5, 0.10 | OURS (grid) | none |
| SIG:51 | lru_cache 16384 | n/a | n/a | n/a |
| SIG:93-95 | ATR_N plain SMA of TR over N=60 (S1) | 60 | OURS | ATR not used by Fabio for balance (he draws a fixed profile A to B, o-w5Gxss6T0) |
| SIG:98-105 | profile rebin floor(lo/B)*B | n/a | OURS | none |
| SIG:119-125 | POC ties -> lower bin | rule | OURS | none |
| SIG:143-153 | VA two-bin expansion | rule | OURS (CME-style) | PT-15 |
| SIG:167 | LVN median = upper median of nonzero bins | rule | OURS | none |
| SIG:172-179 | select_lvn retrace >= 0.25 of leg, c beyond LVN | 0.25 | OURS (spec: "not in these transcripts") | none |
| SIG:198 | balance iff `R <= k_bal*sqrt(N)*ATR` | k 0.8 | OURS | PT-03 |
| SIG:203 | `|c-poc| <= 0.25R` | 0.25 | OURS | none |
| SIG:218 | `|P| >= p and drift <= q` pressure | p grid, q 0.25 | OURS; concept SCON (o-w5Gxss6T0 "cumulative volume delta compared to price") | none |
| SIG:243-247 | control: s*e >= z_hi and s*res >= r_ctl; absorbed: s*res <= r_abs | as constants | OURS; concept SOURCED | none |
| SIG:289 | tier "999" iff VR >= 1.5 | 1.5 | OURS | PT-02 |
| SIG:307-322 | S5: break of H/L(i-1) on the CLOSE with S4(i,m,s); m grid 5/15 | m | OURS; "trigger on the close" cited FABIO (P08) | 9IliXww64uM: "And the 5-minute was about to close right over here and that was my signal for the entry." (5-minute close, not 1-minute; PT-13) |
| SIG:325-349 | S5D: break against absorbed pressure; absorption look-back N bars | N | OURS; concept SOURCED (failed auction, o-w5Gxss6T0) | none |
| SIG:353-367 | S6/S9 control/defended level = last control/absorbed bar extreme | rule | SCON (Fabio levels from absorption) | none |
| SIG:370-383 | S7 curve premium if c > VAH, discount if c < VAL | rule | SCON | 8CWKfoSJu3c [2:05] |
| SIG:409-441 | S8 (a) net15 <= 0; (b) new opposite balance N60 or n(s)>n(-s); (c) opposite control and close through last control level; (d) climax | clauses | concept SCON (0jM5Y31YJak); all numbers OURS | none |
| MOD:32 | RECLAIM_BARS | 5 | OURS | none |
| MOD:33-34 | REST_VALID_B, REST_VALID_D | 3, 3 | OURS | none |
| MOD:35 | IB_MINUTES | 30 | SOURCED for equities (LQvv5xgy_ik), transfer OURS | PT-10 |
| MOD:38-43 | D = max(f*entry, structural); no arm if D > Dmax*entry | f 0.3/0.5%, Dmax 1.0% | OURS | Fabio "super small stop" 0.014-0.061% (FACTS A6) |
| MOD:101,175 etc. | structural stop = level distance + 1 TICK (0.1 USD) | 0.1 USD | OURS; header P32 labels "FABIO / NS-fixed" but no tick figure is in any transcript | PT-15 |
| MOD:111-112 | model A confirm: touch + ctrl == s; entry o[j+1] | rule | OURS | none |
| MOD:123-135 | Model B reclaim: close back inside AND absorbed in probe within 5 bars | rule | OURS; concept SOURCED | none |
| MOD:167 | Model B target = opposite balance edge | rule | OURS (Tom/Fabio say edge-to-edge/node, FACTS A5) | none |
| MOD:194-228 | Model C IB break with big push, stop at IB mid, one try/day | rule | OURS; concept IVB SOURCED | PT-10 |
| MOD:239-260 | Model D rest limit at edge, 3 bars, cancel if close through lvl | rule | OURS | none |
| MOD:280 etc. | last_entry_idx = open+329 (decision bar) | 329 | OURS (P33) | none |

### A.3 VPR (vp_return_to_value.py)

| loc | what | value | label | evidence |
|---|---|---|---|---|
| 26 | NS Part B N set | (3, 6, 12) | OURS ("NO-SOURCE" in code, correct) | none |
| 27 | PLACEBO_D cycle | -3..3 x ATR | OURS | n/a (method) |
| 28 | NAKED_PCT | 0.3% | MISLABELLED "SOURCED" (our Java constant) | PT-16 |
| 29 | BARS_PER_DAY | 288 | OURS (5m, UTC day) | none |
| 13,51-52 | event = first 5m close beyond prior-day VA | rule | OURS | BB3c8visnkI says "imbalance"; PT-09 |
| 54 | return = later 5m bar range contains prior POC | rule | OURS; concept "return to equilibrium/liquidity" SOURCED | BB3c8visnkI "bring the price back into this range" = back into VA, not POC |
| 55-56 | event on the last bar = censored/no-return | rule | OURS | n/a |
| 60-69 | acceptance N closes beyond same edge, then touch of POC | N | OURS | PT-06 |
| 184 | NEAR_MAX_D | 1.0 | OURS (post-hoc) | n/a |
| 201 | CENS_MIN_LEFT | 12 | OURS (post-hoc) | n/a |
| 268 | verdict 0.70 inside CI | 0.70 | SOURCED claim (BB3c8visnkI) | PT-09 |
| (via P) | atr_sma, 1h ATR14, bin 10 USD, 2000 bootstrap, seed | | OURS | method |
| 352-353 | cash session NOT_IN_DATA; LVN not built ("beyond the LVN side" read as VA edge) | stated | stated honestly in file | consistent with PT-05 |

### A.4 TVP (tom_vp.py)

| loc | what | value | label | evidence |
|---|---|---|---|---|
| 5-13 | header SOURCED list: VA 70% [TOM-277], 60-70% balance and 30% runaway [TOM-275/278/280], counter-trade to equilibrium [TOM-279], accepted thin area [TOM-273/274], daily profiles/shifted equilibrium [TOM-281-284], gaps need not close [TOM-285] | concepts | SOURCED concepts (all extract_BB3c8visnkI); header's own OURS list is accurate | PT-09 for scope |
| 26 | BAR | 5 min | OURS | n/a |
| 36 | accept_n default | 6 | OURS | PT-06 |
| 36 | stop_atr default | 1.0 x ATR14 (1h) | OURS | PT-07: Tom "stop loss belongs below the last liquidity" (TOM-072) |
| 36 | target_r default | 2.0 | OURS | Tom "2 2.5" average |
| 36-37 | fees maker/taker/slip, dates 2022-04-01..2024-06-30 | from `_bars` | OURS | n/a |
| 45-50 | UI ranges accept_n 0-48, stop 0.25-5, target_r 0.5-10 | bounds | OURS | none |
| 154 | bin_width: 10 if mean close >= 5000, 1 if >= 500, else 0.5 | 10/1/0.5 | OURS | none |
| 182-191 | migration: y.val > b.vah or y.vah < b.val | rule | SCON | Ld1dhjGdTCA (rising/flat/falling VPOC and value) |
| 196-227 | RETURN at first close outside; FADE = touch edge from inside and close back (`pc` inside); ACCEPT at the N-th consecutive outside close | rules | OURS; RETURN/FADE SCON, ACCEPT SCON | BB3c8visnkI |
| 214-216 | RETURN only once per side per period (`left`) | rule | OURS | none |
| 224 | skip counter trades against migration | rule | OURS | none |
| 230-241 | accept_exit: N consecutive closes beyond | rule | OURS | none |
| 253-273 | entry at next bar; stop = close -/+ stop_atr*ATR; target POC (return if already past) or VA width (ACCEPT) or multiple of risk; hold to end of period | rules | OURS | PT-07 |
| 142-149 | period = UTC day, or Monday week (1970-01-01 Thursday offset +3) | n/a | OURS ("he uses the cash session") | BB3c8visnkI "only show you the period where the so-called cash session is" |

### A.5 LS (levelstory.js)

| loc | what | value | label | evidence |
|---|---|---|---|---|
| 12 | P.touch | 0.0005 (5 bps) | OURS | none |
| 12 | P.near | 0.003 | OURS | none |
| 12 | P.wick | 0.5 | OURS | none |
| 12 | P.relVol | 1.5 | OURS | HySZZSjMxF8 spike then fade (PT-12); no figure |
| 12 | P.bbNear | 0.1 of BB width | OURS | PT-11 |
| 12 | P.look | 3 bars | OURS | none |
| 12 | P.idea | 3 votes | OURS | none |
| 21 | min 25 completed 15m bars | 25 | OURS | none |
| 27 | Bollinger(20, 2) | 20, 2 | OURS, NO-SOURCE (Fabio F tier, 3JZH06L28us) | PT-11 |
| 28 | avg volume of 20 bars | 20 | OURS | none |
| 36 | touch bar: reached within 0.05%, closed back | rule | OURS | none |
| 42 | ACCEPTED = 2 closes beyond (both ternary arms identical) | 2 x 15m | OURS; comment cites accept80 "2 x 30m" (MISLABELLED duration) | PT-06 |
| 41 | failed break: closed beyond in last 3 bars, now back | 3 | OURS | none |
| 45-61 | evidence weights (BB +1, wick +1, vol +1, absorb +2, CVD +1, close -3/-1, trap +2, WT +/-1, OI 0) | weights | OURS | PT-11; absorption concept SOURCED (Fabio) but weight OURS |
| 64-66 | WaveTrend hot/cold zone, cross within 2 bars | rule | OURS (no source in any T/F transcript) | PT-11 |
| 68 | OI: |doi| > 0.0005 shown, weight 0 | 0.0005 | OURS | OI discussed only in P3rDSh187TE (non-T/F) |
| 72, 77 | idea = SHORT/LONG only if turn (or thru) >= 3 and exceeds the other | 3 | OURS | none |
| 85 | "crowd": level.n >= 3 calls | 3 | OURS (operator wording: wait for the close) | none |
| 4 | analyst-call levels: "wait for the close" | concept | operator + analyst, not T/F | n/a |

### A-end. Searches run (for repeatability)

`python g.py <regex>` over `raw_transcripts_canonical/*_raw.txt` (timestamps stripped, whitespace collapsed). Zero T/F hits: `bin size|tick size|price steps|row size|cluster size`; `knife|vertical move|without pullback`; `percentile|99th|99.9` (only BBWP/competition contexts in Krown/Cowen/Fabio-personal); `(\d+) % (of|less|below).*(volume|POC|node)` for any LVN threshold; `monthly (profile|candle|close)` (only ridY2Z0hSQA "weekly chart, the monthly chart or the daily chart" with no rule); `20.month`. Non-trivial hits followed up by reading 600-2500 characters of context (Sy-x5AQ9-Pk, BB3c8visnkI, UOBgXV20yCM, 7BQPMJ39WpI, LQvv5xgy_ik, o-w5Gxss6T0, 3JZH06L28us, Is1HvdfQm5c, DyS79Eb92Ug).

Noticed: (1) `levelstory.js:42` has two identical ternary arms (`prevIn` unused); (2) FACTS A6 credits Tom with "trail aggressively" while UOBgXV20yCM says he does not trail planned targets; (3) `3JZH06L28us` (Fabio tool tier list) is a 1.6 KB file holding several explicit indicator verdicts (BB F, RSI D, MACD F, VWAP S, ATR B, EMA B, liquidity heat map S, deep trades S) that no extract cites; worth one card; (4) speaker of `4P5WAxyPCis` should be confirmed before any "Tom" attribution.
