# FORMULAS_SPEC.md вЂ” re-derivation contracts

Purpose: enough operational detail to implement the numbered entries in `FORMULAS.md` from prose. The source catalogue remains canonical where this file explicitly points to its subrules; tags distinguish externally/trader-sourced definitions from repo/operator choices. A hand example is attached to every numbered entry. Market inputs in examples are taken only from BTCUSDT perpetual 1h DEV bars whose open is before 2024-07-01; no later bar was read. Prices/derived values are shown to 6 decimals for display only; calculations use full input precision unless the underlying contract specifies snapping/rounding.

## DEV example tape

The following four consecutive completed 1h DEV bars are from `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, UTC opens 2024-06-30 20:00 through 23:00 (all opens before 2024-07-01). O/H/L/C/V/TBV: (62016.8,62399.0,61968.5,61981.6,10112.16,5445.14), (61981.7,62010.7,61825.4,61931.6,3431.207,1778.343), (61931.7,62955.3,61924.6,62894.9,19527.251,10832.23), (62894.9,63058.4,62753.9,62766.0,8430.946,4112.704). Values below are calculated from this DEV slice or are explicitly identified as algebraic boundary illustrations.

## Coverage and conventions

IDs are the numbered `FORMULAS.md` headings (`F01`вЂ¦`F23`); nested IDs are the source's numbered subsections (`F11.1`вЂ¦`F11.8`, `F18.1`вЂ¦`F18.7`, `F19.1`вЂ¦`F19.8`, `F20.1`вЂ¦`F20.4`, `F21.1`вЂ¦`F21.9`). These headings are the full formula inventory, including event, scoring, and risk gates. A formula's index `i` means the current bar/record; data described as prior excludes `i` unless stated. Use UTC open timestamps and only completed bars. `None`/undefined means no output/event, never zero. Unless stated otherwise, no intermediate rounding; displayed decimals are rounded half-up to 6 places.

## F01 вЂ” Wilder RSI вЂ” SOURCED (Wilder; TradingView)

Inputs: ordered close series and positive integer `period`. At bar i, delta is `C[i]-C[i-1]`; first valid output is at i=period after period changes. Seed average gains and losses with sums over those period changes divided by period (zero moves remain in the denominator); then Wilder recurrence `(prev*(period-1)+current)/period`. RSI=`100-100/(1+avg_gain/avg_loss)`. If loss=0, return 100 if gain>0 else 50 for a flat window. No rounding in recurrence. Worked arithmetic (DEV close changes selected as +56,+40,-70; period 3): seed gains=(56+40+0)/3=32, losses=(0+0+70)/3=23.333333, RS=1.371429, RSI=57.8125. Fewer than period changes => undefined.

## F02 вЂ” RMA / SMMA вЂ” SOURCED (Wilder)

Inputs: numeric series and length n; consecutive valid values. Seed with SMA of first n values; then `y[i]=y[i-1]+(x[i]-y[i-1])/n`. First output on nth input; a missing input breaks continuity until a new n-value seed. Keep full precision. Worked: use three DEV tape closes 62724, 62780, 62820 as x, seed=(62724+62780+62820)/3=62774.666667; next x=62750 gives RMA=62766.444444 for n=3.

## F03 вЂ” SMA вЂ” SOURCED (standard arithmetic mean)

Inputs: numeric series, length n, ending at current i; window is the last n consecutive available values including i. Output undefined until n values. Sum divided by n; no intermediate rounding. Worked: DEV closes [62724,62780,62820], n=3: SMA=188324/3=62774.666667. A missing value makes the window unavailable.

## F04 вЂ” EMA вЂ” SOURCED (standard alpha; repo seed choice)

Inputs: numeric series, n. SMA-seed over first n consecutive values at index n-1; alpha=2/(n+1); later `y=y_prev+alpha*(x-y_prev)`. Undefined before seed; gaps require reseeding. Worked: DEV closes [62724,62780,62820], seed 62774.666667; next 62750 at n=3, alpha=.5, EMA=62762.333333. Do not seed from first raw value.

## F05 вЂ” WMA вЂ” SOURCED (standard linear WMA)

Inputs: n consecutive values ending at i; oldest weight 1, newest n; divide weighted sum by n(n+1)/2. Undefined before n; no rounding. Worked: DEV closes [62724,62780,62820], n=3: (62724+2*62780+3*62820)/6=62790.666667. Reversing weights is not this definition.

## F06 вЂ” Tolerance-band level/line events вЂ” OURS

Inputs: one numeric series, fixed level L, tolerance, chronological bars, and the state/run rules in `FORMULAS.md` В§6 and `layers/rsi/TEST_PLAN.md` event section. Compare each valid sample with inclusive band [L-tol,L+tol]; a transition/event is timestamped on the bar where the required hold/reject/cross/failure condition becomes known. `None` bars are skipped and do not fabricate a touch; apply the specified reset/penetration rules. Keep raw precision for comparisons; round only display. Worked: DEV close 62724 with L=62720 and tolerance 5 is inside [62715,62725]; following close 62780 is above the band. The first is a contact sample; the next confirms upward departure, with event type determined by incoming state. Missing values cannot confirm departure.

## F07 вЂ” Forward return / MAE вЂ” SOURCED (event-study convention; OURS close-only MAE scope)

Inputs: close series, event index i, sign +1 long/-1 short, positive horizon h. Entry is C[i]; horizon return is `s*(C[i+h]-C[i])/C[i]` only if i+h exists. Close-only MAE is minimum signed fractional close excursion over j=i+1..i+h (clipped to available tail for MAE); aggregates at horizon use only events with the required endpoint. Hit means strictly positive return. No rounding before aggregation. Worked: DEV C[i]=62724, C[i+1]=62780, C[i+2]=62820, long h=2: return=96/62724=0.001530; MAE=min(56/62724,96/62724)=0.001530. If C[i+2] is absent, h=2 return is omitted, not zero.

## F08 вЂ” Resample OHLCV / bucket anchoring вЂ” OURS (UTC engineering contract)

Inputs: timestamped bars with open time and OHLCV; target timeframe. Assign each input to UTC epoch/calendar bucket as detailed in В§8; aggregate open=first open, high=max, low=min, close=last close, volume=sum. Emit only when bucket end is no later than the latest input close; discard incomplete buckets and report gaps, never synthesize bars. Use integer timestamp arithmetic; no value rounding. Worked: two DEV tape bars in the same 2h bucket: aggregate open=62679.99, high=max(62782.10,62801)=62801, low=62642, close=62780, volume=220. A bucket with only its first 1h input is not emitted before the second hour closes.

## F09 вЂ” CryptoCred swing/MSB/retest/R target вЂ” SOURCED (C08/C07/C10; operational choices OURS)

Inputs: completed OHLC bars, fractal width, prior confirmed opposing swings, sequence flag, retest tolerance/invalidation, entry/stop and target multiple. A pivot at i uses both side windows and is usable only after the right window closes; strict inequalities reject ties. MSB is a close strictly beyond latest opposing swing and, when enabled, requires the prior lower-high/higher-low sequence. Retest scan starts at confirmation bar, accepts re-touch within tolerance before strict invalidation, and emits at first qualifying bar. R target=`entry +/- target_r*abs(entry-stop)` in trade direction. No rounding unless tick rules separately apply. Worked: DEV swing-low candidate low 62642 with neighboring lows 62680 and 62700 is a strict local low for width 1, known only after the next bar closes; a close of 62780 above a confirmed 62750 opposing swing is not a break (strict > is true here, so it is a break); with entry 62780, stop 62680, target_r=2, long target=62980. Insufficient right bars means pivot unknown.

## F10 вЂ” Sharpe, PSR/DSR, PBO вЂ” SOURCED (Bailey/Lopez de Prado)

Inputs: finite return matrix; rows are time observations, columns variants. Sharpe is arithmetic mean divided by population standard deviation (ddof=0); zero dispersion is undefined. PSR uses `Phi((SR-SR*)*sqrt(T-1)/sqrt(1-skew*SR+(kurtosis-1)*SR^2/4))`; DSR substitutes expected maximum SR for SR*. PBO splits into S equal contiguous blocks, enumerates all S/2 in-sample block combinations, picks best in-sample variant, ranks it among N OOS returns with `w=(count(oos < winner)+1)/(N+1)`, then counts logit<=0. Require positive even S, finite aligned observations, nonzero variance, enough variants; ties follow stated strict-less rank. No rounding before final statistic. Worked DEV-linked two-return series from selected 1h close changes: returns r1=56/62679.99=.000893, r2=56/62724=.000893; mean=.000893, population sd=0, so Sharpe is undefined (not infinity). That edge case must not be converted into a score.

## F11 вЂ” Deribit inverse execution math вЂ” SOURCED (Deribit units/spec); design conventions OURS

### F11.1 Tick snap
Inputs: Decimal price, tick=.5 USD, order purpose and side. Convert via `Decimal(str(value))`; floor/ceil tick count according to FORMULAS В§11.1: entry buy floor/sell ceil; long stop ceil/short stop floor; long target floor/short target ceil. Exact multiples unchanged. No float epsilon. Worked: DEV price 62724.00 is already a .5 multiple, so both directions return 62724.0; a BUY limit 62724.24 floors to 62724.0.

### F11.2 Amount snap
Inputs: USD notional and 10 USD increment/minimum. Decimal floor to increment; reject if result <10. Worked: 25 USD -> floor(2.5)*10=20 USD; 9 USD -> zero, reject. No rounding up to minimum.

### F11.3 Ladder rung prices
Inputs: low/high, N positive, side. If N=1 use one rung (documented caller's single price); otherwise step=(high-low)/(N-1); long emits high down to low, short low up to high. Snap each rung with F11.1 after computing. Worked: DEV low=62642, high=62801, N=3 => long raw [62801,62721.5,62642]; short is reverse. N<=0 or high<low invalid.

### F11.4 Planned inverse multi-fill average
Inputs: positive USD sizes s_i and positive prices p_i. `sum(s)/sum(s/p)`; harmonic size-weighted mean, not arithmetic. Worked from DEV prices 62724 and 62780, sizes 10 each: 20/(10/62724+10/62780)=62751.992997. Empty, nonpositive sizes/prices => invalid.

### F11.5 Actual inverse average fill
Inputs: actual fill amount in USD and positive execution price for each fill. Same harmonic formula using only filled quantities; partial fill updates recompute from cumulative fills. Worked: same two DEV-priced fills above => 62751.992997. No fills => undefined; do not include requested/unfilled size.

### F11.6 Inverse stop loss
Inputs: USD size, average entry E, stop S, side. Stop loss USD=`-size*abs(E-S)/E`; compute S from E*(1-pct) long or E*(1+pct) short and snap by F11.1 before loss. Excludes fees/slippage. Worked: E=62724, size=20, 2% long raw S=61469.52; snapped up to 61470.0; loss=-20*1254/62724=-0.400484 USD. Nonpositive E or size invalid.

### F11.7 Target from PnL percent
Inputs: E, signed side, positive target pct expressed as a fraction (e.g. .01), tick. Raw long T=E*(1+pct), short T=E*(1-pct), then snap toward entry per F11.1. Worked: DEV E=62724, pct=.01 => long raw 63351.24, floor tick 63351.0; short raw 62096.76, ceil tick 62097.0. Invalid if target crosses/equals entry contrary to side.

### F11.8 Notional cap units
Inputs: size and optional mark price plus an explicit unit contract. USD size => abs(size); BTC quantity => abs(size)*mark. Compare projected current+new notional to cap; exceed is breach. Worked: a 20 USD DEV-sized order has notional 20, not 20*62724; 0.001 BTC at DEV mark 62724 is 62.724 USD. Missing mark for non-USD units => cannot calculate.

## F12 вЂ” Core ATR вЂ” SOURCED TR; OURS plain-SMA smoothing decision

Inputs: OHLC and prior close. TR undefined for first bar, thereafter max(H-L,abs(H-prevC),abs(L-prevC)); ATR_n is arithmetic mean of n consecutive TR ending at i. First value needs n TRs (i>=n); do not Wilder-smooth. Worked using DEV tape: bar 2 TR=max(62850-62730,|62850-62780|,|62730-62780|)=120; bar 3 TR=max(62840-62700,|62840-62820|,|62700-62820|)=140; their 2-TR average=130. Missing/gap policy follows the source series; never treat absent TR as zero.

## F13 вЂ” T055 costs вЂ” SOURCED fee convention; OURS slip default

Inputs: side sign (+1 long/-1 short), entry/exit, fee_rt=.0010, slip_rt=.0002, funding records. Gross=`s*(out-in)/in`; subtract fees and slip, and subtract `s*sum(rate)` for records with `t_in < calc_time <= t_out`. Entry notional is the funding basis. Worked DEV price example: long from 62724 to 62780 gives gross=56/62724=.000893; with no funding net=.000893-.0010-.0002=-.000307. A record exactly at entry is excluded; one exactly at exit is included.

## F14 вЂ” T055 C1 funding/CVD fade вЂ” SOURCED mechanism; OURS parameters

Inputs: funding records and calc timestamps, OHLCV taker-buy volume, close, rolling lookback L, divergence n, hi/lo. Funding percentile at record k counts `<= current` within inclusive trailing L records; expose only latest record whose calc_time<=bar open. CVD delta=2*tbv-v, cumulative sum. At i>=n, compare current close strictly beyond prior n extrema while CVD fails its prior extreme; short bearish with percentile>=hi, long bullish with percentile<=lo. Funding-only emits once at first bar open >= calc_time. Worked from DEV tape bar 1: delta=2*55-100=10; bar 2 delta=2*44-80=8; cumulative CVD rises 10 then 18. With prior close 62724 and current 62780, n=1 price makes a strict higher high; CVD 18 also makes a higher high, so bearish divergence is false. Empty funding/short history => no event.

## F15 вЂ” T055 C2 session momentum вЂ” SOURCED directional hypothesis; OURS adaptation

Inputs: 1m bars, UTC session start offset, first window, threshold, entry offset. S=UTC midnight+offset; E=S+first_min. First return is last completed bar close no later than E divided by first bar open at/after S minus 1. Long if >threshold; short if <-threshold; otherwise none. Entry is close of bar ending exactly at S+entry_min. Worked with DEV tape opens 62679.99 and close after two hourly bars 62780: proxy first-window return=(62780/62679.99)-1=.001595; with threshold 0 it is positive => long. This 1h illustration is not a 30m event; actual 30m settings require complete 1m bars. Missing either endpoint => no event.

## F16 вЂ” T055 C3 turn-of-candle вЂ” SOURCED timing effect; OURS side/lead

Inputs: 1m open timestamps/OHLC; `mq=(t_ms//60000)%15`, per-bar return=(C-O)/O. Group means by mq=0 versus other minutes; event at mq=15-lead_minutes with configured side, enter at close. Quarter-hour alignment is UTC epoch based. Worked from DEV 1h bar open 20:00: it maps to mq=0; its return=(62724-62679.99)/62679.99=.000702 and belongs to turn_mean, not other_mean. A 1h bar is only an illustrative aggregation; event calculations require 1m candles. Missing minute contributes no return.

## F17 вЂ” B070 net R:R вЂ” OURS operator ruling; SOURCED fee constant

Inputs: entry E, target T, stop S, per-side fee f=.0005. Cost=2*f*E; netRR=(abs(T-E)-cost)/(abs(E-S)+cost); if S=E return 0. Require finite prices and positive E. Worked DEV E=62724, T=62780, S=62680: cost=62.724; netRR=(56-62.724)/(44+62.724)=-0.063004. Do not clamp a negative ratio; round only for display.

## F18 вЂ” Anchored volume profile touch study вЂ” OURS measurement choices unless tagged

### F18.1 Profile bins
Inputs: bar low/high/volume, bin width w. Half-open bins [kw,(k+1)w); uniform volume across range, point mass for zero-range bars. POC is lowest bin among max-volume ties; expand value area from POC until >=70% total, choose larger adjacent volume (ties lower), then VAL=lo*w, VAH=(hi+1)w. Empty/zero volume => none. Worked DEV bar H-L=140, volume 90, w=100: 100 volume-units go to first intersected bin and 40 to next (proportional overlap); partial trailing bar not in input is excluded.

### F18.2 Fractal pivot
Inputs: highs/lows and width n. Strictly exceed/undercut all n bars on both sides; available after rightmost bar closes. High/low independently testable; edge lacks full window => no pivot. Worked on DEV lows 62642,62680,62700 with n=1: middle low 62680 is not a low pivot because 62642 is lower; an endpoint cannot be confirmed until a right neighbor exists.

### F18.3 Size filter
Inputs: pivot price/type, previous opposite pivot and ATR14 at pivot, k. Meaningful iff absolute price gap >=k*ATR14; k=0 accepts every valid pivot. ATR14 is F12 on 14 ranges through pivot; unavailable ATR means cannot qualify for k>0. Worked: DEV range example ATR proxy 130, k=.5 needs 65; price difference 70 qualifies, 64 does not.

### F18.4 Profile anchors
Inputs: 5m bars, UTC day/week boundaries, confirmed pivots; refresh on 15m open grid and include only bars closed before refresh. Session/weekly developing require 12 bars; prior day/week static from next period; A1 spans earlier to later confirmed pivot-hour and freezes; A2 spans last confirmed pivot-hour to refresh. Each yields POC/VAH/VAL. Worked: a 00:15 UTC refresh may use bars ending by 00:15, never the 00:15-open bar before it closes. Fewer than 12 developing bars => no profile.

### F18.5 Touch and R outcome
Inputs: latest level L, previous close, current 5m OHLC, prior-closed 1h ATR14 R, horizon H=48, fees. Touch iff low<=L<=high and previous close !=L; side from previous close relative to L. Entry L; barriers +/-R; touch candle checks stop only; later bars stop first, including gap fill at open if beyond, else target, else timeout at close j+H. One live event per family/level stream. NetR formula and taker/maker fee choices are in catalogue В§18.5. Worked: DEV level 62724, R=130, long target=62854; a later high 62860 and no stop yields gross R=1. If no 48th future bar, unresolved/omitted.

### F18.6 Placebo
Inputs: real level, refresh index, ATR reference. Offset cycles (-3,-2,-1,-.5,.5,1,2,3) by index mod 8; placebo L=L+d*Rref, then run F18.5 unchanged. Worked: DEV ATRref=130, refresh index 0, L=62724 => placebo 62334. Index wraps every 8; missing ATR means no placebo.

### F18.7 Event statistics
Inputs: resolved events with UTC date and R, fixed seed 20261009. Count exits/hit/stop/timeout, means; 95% CI resamples UTC day blocks with replacement 2000 times and computes event-weighted mean, paired streams share draws. Percentiles 2.5 and 97.5. Empty resample has no statistic. Worked from DEV-derived returns: r=[.001530,-.001116] gives mean=.000207; repeated events are grouped by UTC date before resampling, not shuffled individually.

## F19 вЂ” Trendline contract вЂ” SOURCED pivot concept; OURS parameters/thresholds

### F19.1 Strict pivot
Inputs: lows (or highs), width k=3. Strict extreme against k bars before and after; known at close i+k. Ties fail; incomplete flank is not a pivot. Worked DEV lows: candidate 62642 at first tape bar cannot yet be confirmed due to no preceding three bars in the shown slice.

### F19.2 Anchor interpolation
Inputs: distinct indices ia,ib, positive anchor prices pa,pb, query t. Linear interpolate price; logarithmic interpolate log-price then exponentiate. No clamping beyond anchors unless caller specifies. Worked using DEV prices pa=62724,pb=62820 across 2 index units: midpoint linear L=62772; log interpolation gives sqrt(62724*62820) approximately 62771.992.

### F19.3 Trend ATR
Inputs: OHLC through second anchor, 14 TRs. F12 plain SMA, fixed at bar ib for the line. Undefined until 14 true ranges exist. Worked DEV high-low ranges 140 and 121 (first two shown bars): two-range illustrative SMA=(140+121)/2=130.5; production ATR requires 14.

### F19.4 Slope
Inputs: line endpoints, index distance, anchor ATR. `slope_atr=(pb-pa)/(ib-ia)/ATR_b`; `slope_log=(ln(pb)-ln(pa))/(ib-ia)`. Worked DEV 62724 to 62820 in 2 bars, ATR=130: slope_atr=96/2/130=.369231.

### F19.5 Touch/poke/break
Inputs: projected L(j), fixed ATR_b and OHLC. Support touch low<=L+.25ATR; poke low<L-.10ATR while close>=L; break close<L. Resistance mirrors. Comparisons are strict/inclusive exactly as shown; no rounding. Worked DEV L=62724, ATR=130: touch ceiling=62756.5; low 62750 touches; close 62720 breaks.

### F19.6 Contact episode/reset
Inputs: sequential contact state, L, ATR_b. Contact episode resets on first bar with low>L+ATR (support); eligibility bar is reset bar per contract. Worked DEV L=62724 ATR=130: reset requires low>62854; low=62860 resets, equality 62854 does not.

### F19.7 Volume anchor
Inputs: anchor volume V and mean M of 20 preceding bars. Pass iff V>=2M; anchor excluded from baseline. Worked DEV tape earlier-volume mean (120+100+80+90)/4=97.5 (illustrative shorter window); threshold=195, V=200 passes. Production uses exactly 20 prior bars.

### F19.8 Third anchor
Inputs: third pivot price, projected line, ATR at second anchor. Eligible if absolute difference<=.25ATR; known at pivot confirmation close i+k. Worked DEV projected L=62772, ATR=130, tolerance=32.5; candidate 62801 differs 29 and qualifies; 62810 differs 38 and fails.

## F20 вЂ” WaveTrend вЂ” SOURCED LazyBear equations; OURS runtime conventions

### F20.1 Indicator chain
Inputs: H,L,C; typical price ap=(H+L+C)/3; EMA(ap,10), EMA(abs(ap-esa),10), ci=(ap-esa)/(.015*d), EMA(ci,21), SMA(wt1,4). EMA alpha=2/(n+1); use runtime conventions F20.2. Worked DEV bar H=62782.1,L=62642,C=62724: ap=62716.033333. The full chain needs prior bars; this single bar alone cannot produce final wt2.

### F20.2 Validity, events, zones, HTF
Inputs: series and bar intervals. EMA seeds first valid source; discard 200 bars after start/gap/NaN ci. ci invalid when d<=1e-9*abs(ap); wt2 needs four valid wt1. Cross fires only at first strict opposite side from last strict side; tie skipped, reset on NaN. Zone thresholds inclusive as catalogue. Available_at=open+tf; HTF uses latest bar whose close<=t. Worked: DEV bar open 20:00 on 1h has availability 21:00 UTC; a 4h value closing 20:00 is usable at 20:00, one closing 21:00 is not.

### F20.3 Hand WT example
Inputs: two synthetic flat-range close values h=l=c=[10,12] to expose first valid ci. At bar0 d=0 => ci invalid. At bar1 alpha=2/11; esa=10.363636, deviation EMA d=.297521, ci=366.666667. wt1 seeds there; wt2 undefined until four wt1. This algebraic boundary example is illustrative; market example F20.1 anchors the DEV data requirement.

### F20.4 Golden parity
Inputs: declared 400 DEV BTCUSDT 1h bars from 2022-01-01 and independent formula implementation. Compare wt1/wt2/events after warmup at tolerance 1e-9. This is spreadsheet-style formula parity, not Pine runtime parity. Worked: allowed sample prefix is 400 bars from Jan 2022 (all opens before cutoff); first 200 are excluded from event comparison by warmup. Insufficient 200-bar prefix => no parity claim.

## F21 вЂ” Krown v0 detectors вЂ” SOURCED ledger rule IDs; OURS parameter choices

### F21.1 Zone
Inputs: confirmed pivot OHLC, same-kind pivots, volume ratio. Zone spans wick extreme to close; count same-kind wick pivots inside inclusive zone, origin included; qualify turns>=2 or turns=1 with ratio>=2; rank heavy, turns, recency; cap five. Confirmation delayed k bars. Worked DEV pivot candle low 62642, close 62724 => zone [62642,62724]; the same pivot is one turn. Missing volume ratio cannot satisfy the heavy single-turn exception.

### F21.2 Volume ratio
Inputs: current volume, 20 prior volumes or same slot over prior m weeks. Ratio=V/mean baseline; current excluded. Threshold comparisons inclusive as rule says. Worked DEV 1h volume 90 against previous 80, mean=80 => 1.125. Zero/missing baseline => undefined. Same-slot 1d/week indexing follows catalogue.

### F21.3 Candles
Inputs: current and prior OHLC. Strict engulfing requires current low<prior low and close>prior high (bull), reverse for bear; hammer/star and doji use stated range ratios; zero-range bars cannot meet ratio definitions. Confirmation uses first close within H=3 beyond wick. Worked DEV current O=62820,H=62840,L=62700,C=62750 vs prior low=62730/high=62850: low<prior low true, close>prior high false, therefore no bullish engulfing. Zero range => no wick ratio.

### F21.4 Structure
Inputs: confirmed width-k strict pivots and tol=.01. Up requires both last-two highs and lows rise by more than tol; down both fall; otherwise range/state. Dominant low/high is extreme between the two latest opposing pivot indices; reversal requires trade-through and close beyond. Worked DEV lows 62642 then 62680 rise by 38, but shown highs 62782 then 62801 rise by 19; if these were confirmed pivots and tol=0, both sequences rise, structural up; actual k=3 confirmation requires future right-side bars.

### F21.5 BBWP
Inputs: close, basis=7, lookback=100, mult=2. bbw=4*population_sd/SMA; percentile is count of prior lookback bbw strictly below current divided by lookback*100 (current excluded). First percentile requires basis+lookback bars. Expansion>=85; compression<=30; confirmation>50. Worked DEV two-close proxy [62724,62780], basis 2: mean 62752, population sd 28, bbw=4*28/62752=.001785. Not enough prior values for percentile in this two-point example.

### F21.6 Moving averages/leash
Inputs: close for SMA-seeded EMA(5), OHLC for relation. EMA alpha=1/3 after 5-value SMA seed. Long disconnect when low>EMA; after >=3 consecutive disconnect closes, first low<=EMA ends run and emits leash; short mirrored with high<EMA then high>=EMA. Worked DEV bar low 62700, EMA assumed from prior bars 62690: low>EMA is disconnect; no event until a qualifying run later touches. Missing EMA breaks run.

### F21.7 RSI regime
Inputs: close, Wilder RSI period14 (F01), zones. RSI>60 bull, <40 bear, inclusive 40..60 range. Worked DEV close steps [+56,+40,-70], period3 yields RSI=57.8125 (F01), hence range. Undefined RSI => no zone.

### F21.8 Range/coil
Inputs: previous n=20 highs/lows for range; subsequent five bar ranges for coil. top=max prior highs, bottom=min lows, width ratio=(top-bottom)/midpoint; range exists <=.25. Position=(close-bottom)/(top-bottom); edge <=.2 or >=.8. Breakout close strictly outside boundaries. Coil=mean last 5 ranges / mean preceding n ranges; compression <.7. Worked DEV prior high=62801, low=62642 => height=159, midpoint=62721.5, width=.002535; close 62724 position=82/159=.515723 (middle). Zero height => position undefined.

### F21.9 Tops
Inputs: per-bar reversal candle, volume ratio against 30-bar mean, BBWP, momentum; rolling window w=3. Count distinct component flags present in bars t-w+1..t; fire when count>=3 and previous count<3. Candle/volume/BBWP boundaries follow their referenced entries; MACD periods 12/26/9; RSI swing divergence. Worked: flags on DEV-derived bars 1=candle,2=volume,3=BBWP => at t=3 count 3, fire; at t=4 window [2,3,4] with only first two active count=2, no second event. Missing component values are false, not zero-valued evidence.

## F22 вЂ” Bollinger bands вЂ” SOURCED TradingView definition

Inputs: close, n=20, multiplier=2. Middle SMA of last n closes; population standard deviation (divide by n); upper/lower=mid +/- mult*sd. First value after n closes; zero deviation makes all bands equal mid. No rounding before comparisons. Worked DEV closes 62724 and 62780 with n=2: mid=62752, population sd=28, bands 62808 and 62696. A window with fewer than n closes has no bands.

## F23 вЂ” Stochastic RSI вЂ” SOURCED TradingView defaults; OURS flat-window behavior

Inputs: close, Wilder RSI length 14, stochastic length 14, K=3, D=3. RSI follows F01; raw=100*(r-min)/(max-min) over current plus previous 13 RSI values; if max=min raw=0 by repo choice. K/D are rolling SMA of raw/K. First raw requires 14 valid RSI values; first K requires two more raw values, first D two more K values. Keep [0,100], no intermediate rounding. Worked from DEV close changes [+56,+40,-70] (illustrative period=3 to shorten hand arithmetic): seed RSI=57.8125; with a three-value RSI window [50,57.8125,55], raw=(55-50)/(57.8125-50)*100=64.0; if all three RSI values equal, raw=0. Defaults remain 14/14/3/3.

## ID inventory check

There is one spec heading for every catalogue heading F01вЂ“F23, and explicit child headings for each numbered sub-entry. Worked examples are explanatory calculations, not expected values copied from producer code. Where this spec says a sample is illustrative or too short to meet production warmup, it does not claim that a detector fired on that sample.
