# Formula re-derivation specs

Scope: formula IDs are the 23 numbered top-level entries in `FORMULAS.md`; numbered subentries (for example 11.1–11.8, 18.1–18.7, 19.1–19.8, 20.1–20.4 and 21.1–21.9) are covered by their parent entry and called out below. Numbers are computed without producer code. Unless specified, retain full precision during calculations and round only for display; the input archive stores binary floating point.

DEV fixture used for examples: `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, restricted to `t < 1719792000000` (2024-07-01 00:00 UTC). Bar opens 0–4 are 2022-01-01 00:00 through 04:00 UTC. Their OHLCV values (USD, USD volume) are:

| i | open UTC | O | H | L | C | V | TBV |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | 00:00 | 46210.57 | 46729.73 | 46210.55 | 46650.01 | 8957.465 | 4777.701 |
| 1 | 01:00 | 46650.00 | 46944.56 | 46570.34 | 46766.78 | 7276.249 | 3689.837 |
| 2 | 02:00 | 46767.44 | 46917.87 | 46709.44 | 46796.14 | 4478.713 | 2103.345 |
| 3 | 03:00 | 46796.15 | 46888.00 | 46746.32 | 46789.56 | 4208.992 | 1928.027 |
| 4 | 04:00 | 46789.55 | 46868.74 | 46605.00 | 46690.81 | 6149.298 | 2855.818 |

The examples below explicitly reuse these observed values where the formula permits. “SOURCED” means the catalog ties the rule to an external, trader, or operator source; “OURS” marks a repo/operator mechanical convention or parameter. A mixed entry labels both parts.

## 1. Wilder RSI — SOURCED (Wilder); flat-series 50 is OURS

Inputs: ordered closes and integer period n. Close i becomes available only when its bar closes; at index i, use only closes through i. Delta i = C[i]-C[i-1]. Seed at i=n using the first n deltas, including zero gain/loss slots in each mean. Thereafter recursively smooth gain and loss with `(prev*(n-1)+current)/n`. RSI = `100-100/(1+avg_gain/avg_loss)`. Keep full precision; present percentages to 4 decimals. Indices before n are undefined. If loss is zero and gain positive return 100; if both zero return 50 (OURS); gaps/non-finite inputs restart the seed after n consecutive valid deltas.

DEV example, n=2, closes from bars 0–2: [46650.01, 46766.78, 46796.14]. Deltas [116.77, 29.36], seed gain 73.065, loss 0; RSI at bar 2 = 100. Bar 1 has no RSI yet.

## 2. RMA/SMMA — SOURCED (Wilder)

Inputs: numeric series and length n. Values align to the last input in each window; seed on the nth consecutive finite value with their arithmetic mean, then `R[i]=R[i-1]+(x[i]-R[i-1])/n`. Full precision internally; display 4 decimals. Earlier values and windows containing missing inputs are undefined; after a gap require a fresh n-value seed.

DEV example, closes 0–2, n=3: seed `(46650.01+46766.78+46796.14)/3 = 46737.6433`, available at close of 02:00 bar.

## 3. SMA — SOURCED (standard rolling mean)

Inputs: numeric series, length n; at i average exactly x[i-n+1..i], aligned to bar i close. No partial windows; missing member makes output undefined. Full precision, display 4 decimals.

DEV example, n=3 on closes 0–2: sum 140212.93 / 3 = 46737.6433 at bar 2 close.

## 4. EMA — SOURCED alpha; SMA seed convention OURS

Inputs: numeric series and n. Seed with SMA of first n consecutive valid values at index n-1; thereafter alpha=2/(n+1), `E=prev+alpha*(x-prev)`. Bar-close alignment; no output before seed and reseed after invalid gap. No intermediate rounding; display 4 decimals.

DEV example, n=3, closes 0–3: seed at bar 2 = 46737.6433. At bar 3 alpha=.5, EMA = 46737.6433 + .5*(46789.56-46737.6433) = 46763.6017.

## 5. WMA — SOURCED (standard/Pine ordering)

Inputs: n consecutive numeric values ending at i; chronological weights 1..n (oldest to newest), divide by n(n+1)/2. Output at bar i close. Missing values invalidate the window; no warm-up partial. Full precision then display 4 decimals.

DEV example, n=3 closes 0–2: `(46650.01+2*46766.78+3*46796.14)/6 = 46762.9983`.

## 6. Tolerance-band events — OURS

Inputs: ordered series x, level L, nonnegative tolerance e, and the state-machine parameters in `FORMULAS.md`/RSI TEST_PLAN. Classify each valid x as below (<L-e), inside [L-e,L+e], or above (>L+e); process one closed bar at a time. Preserve state across valid bars, skip None without inventing an event, and apply the catalog’s run/penetration and support/rejection/failure/cross definitions; event time is the bar that completes the condition. No rounding before comparisons. An absent prior state cannot create a cross; equality at band edges is inside.

DEV example: bar 0 close 46650.01, bar 1 close 46766.78; choose OURS L=46700, e=10. Values are below (46650.01<46690) then above (46766.78>46710), so the series crosses the whole band by bar 1 close. This is an arithmetic fixture, not evidence for a trading threshold.

## 7. Forward return, MAE and hit rate — SOURCED general event-study convention; close-only MAE is OURS

Inputs: event index i, side s=+1 long/-1 short, close series, horizon h bars. Entry is C[i] at event-bar close; endpoint C[i+h] is h subsequent closes. Return `s*(C[i+h]-C[i])/C[i]`; MAE is minimum signed close return among j=i+1..i+h. Hit means return strictly >0. Exclude event at a horizon if endpoint is absent; aggregate each horizon over contributors only. No rounding until presentation. High/low intrabar MAE is outside this close-only definition.

DEV example: long event at bar 2 close 46796.14, h=1, endpoint bar 3 close 46789.56: return/MAE = `(46789.56-46796.14)/46796.14 = -0.00014061` (about -0.0141%); hit=false.

## 8. UTC resampling and OHLCV — OURS (calendar/engineering convention)

Inputs: timestamped source OHLCV bars and target timeframe. Bucket by UTC epoch/calendar rule specified in catalog (fixed duration via floor division; ISO weeks Monday UTC; months calendar-first). Include only source bars belonging to a bucket and emit only when the bucket is complete and its end is no later than the latest source close. Aggregate O=first open, H=max high, L=min low, C=last close, V=sum; trade-count/volume extensions sum likewise. Timestamp output is bucket open. Incomplete buckets and missing required source slots are not silently filled; no rounding of prices/volume.

DEV example, 1h bars 0–3 form 00:00–04:00 UTC: O=46210.57, H=46944.56, L=46210.55, C=46789.56, V=24921.419. This 4h bucket is complete at 04:00 UTC; bar 4 starts the next bucket.

## 9. CryptoCred swings, MSB, retest and R target — SOURCED rule clusters C08/C07/C10; pivot/parameter mechanics OURS

Inputs: closed OHLC bars, side windows n, prior-sequence option, tolerance/invalidation percentages, entry/stop and target-R. A strict pivot at i must beat every high/low in both n-bar side windows; it becomes known only at close i+n. MSB is a close beyond the latest opposing confirmed swing, with required prior lower-high/higher-low sequence when enabled. Retest scans subsequent bars from confirmation: touch broken level within tolerance before invalidation distance is exceeded. Long target=entry+R*abs(entry-stop); short=entry-R*abs(entry-stop). Do not use unconfirmed pivots or round prices before comparisons. Not enough right-side bars means no pivot; ties fail strict pivot; no later retest means none.

DEV example (formula arithmetic from observed bar 0–1): the upward close change is 46766.78-46650.01=116.77. Treating these as an illustrative entry/target pair with stop 46570.34 (bar 1 low) and target_R=1 (OURS), long target = 46766.78+|46766.78-46570.34| = 46963.22. The two bars alone do not establish a confirmed swing or MSB.

## 10. Sharpe, PSR/DSR and PBO — SOURCED (Bailey/Lopez de Prado convention)

Inputs: aligned finite return matrix (variants x observations); split count S even and trial count N. Sharpe = arithmetic mean / population standard deviation (divide squared deviations by n); zero deviation is undefined. PSR is `Phi((SR-SR*)*sqrt(T-1)/sqrt(1-skew*SR+(kurtosis-1)*SR^2/4))`; DSR uses expected maximum null Sharpe for the stated independent trial count. CSCV partitions chronological observations into S equal contiguous blocks, enumerates all choose(S,S/2) IS/OOS splits, chooses the highest IS-Sharpe variant, computes its OOS ascending relative rank `w=(count(oos < winner)+1)/(N+1)`, logit `ln(w/(1-w))`; PBO is fraction logit<=0. Keep full precision; ties use source implementation’s stable ordering, and the catalog does not define unequal blocks (reject them).

DEV example: one-bar return for bars 2→3 is -0.00014061 as in entry 7; with this single observation population deviation is 0, so Sharpe is undefined, not zero. This demonstrates the edge case on actual DEV input.

## 11. Execution math, subentries 11.1–11.8 — SOURCED (Deribit contract); directional policy/ladders OURS

Inputs: USD prices, USD contract sizes, side/order purpose, exact Decimal tick and fee/risk parameters. 11.1 snap via Decimal(str(value))/tick with floor/ceiling: entry BUY floor/SELL ceil; long stop ceil/short stop floor; long target floor/short target ceil. 11.2 floor USD amount to 10 USD multiple; reject below 10. 11.3 N ladder rungs evenly spaced including endpoints, N=1 gives one rung; long high→low, short low→high. 11.4–11.5 inverse average = total USD / sum(USD_i/price_i). 11.6 stop loss USD = `-size*abs(E-S)/E`; 11.7 target T=E*(1±pct), then snap per target rule. 11.8 notional=abs(size) if already USD, else abs(size)*mark. No binary-float epsilon, no upward size rounding; reject invalid/zero denominators. Apply fees only where the caller’s contract says so.

DEV example: bar 0 close E=46650.01; observed bar 1 low S=46570.34. For illustrative size 20 USD, stop loss = `-20*(79.67)/46650.01 = -0.034156 USD` (rounded display -0.03). Tick 0.5, a long stop is ceiled to 46570.5, giving loss `-20*79.51/46650.01=-0.03409`. This is a unit demonstration, not a trading plan.

## 12. True Range and core ATR — SOURCED TR (Wilder); plain-SMA ATR is operator decision

Inputs: H/L/C and period n. For i>=1, TR=max(H-L, abs(H-prevC), abs(L-prevC)); first TR undefined. ATR at i is simple mean of n consecutive defined TR values ending i, not recursive Wilder ATR. Bar-close aligned; no output before n TRs; missing bar/close invalidates window. Retain precision, display 4 decimals.

DEV example, bar 1: TR=max(46944.56-46570.34, |46944.56-46650.01|, |46570.34-46650.01|)=374.22. Bar 2 TR=max(208.43,151.09,59.27)=208.43. Period-2 ATR at bar 2=(374.22+208.43)/2=291.325.

## 13. T055 shared cost model — SOURCED exchange funding/fee convention; slip default OURS

Inputs: side s (+1 long/-1 short), entry/exit prices, funding records and timestamps, fee_rt and slip_rt fractions. Gross=s*(out-in)/in. Sum only records with entry_time < calc_time <= exit_time; net=gross-fee_rt-slip_rt-s*sum(rate), using entry notional for funding fraction. Signals align to closed-bar entry/exit times. No rounding until final report. No record in interval contributes zero; missing funding input is unavailable, not zero.

DEV example, long from bar 0 close 46650.01 to bar 1 close 46766.78: gross=116.77/46650.01=0.0025027. With catalog defaults 0.0010 fee and 0.0002 slip and no funding records supplied, net=0.0013027. The candle archive has no funding values; this example does not infer funding.

## 14. T055 C1 funding-extreme/CVD divergence — SOURCED mechanism; thresholds OURS

Inputs: funding rates ordered by calc_time, lookback L, closes and CVD, divergence window n, high/low percentile cuts. Funding percentile at k counts `w<=current` in the inclusive L-record window divided by L; expose only latest rate with calc_time<=bar open. CVD delta=2*TBV-V and cumulative sum; divergence compares current close/CVD strictly to prior n values. Event short iff bearish divergence and pct>=hi; long iff bullish and pct<=lo. Funding-only mode emits once at first bar time>=record time. Warmup until L rates/n prior observations; equality on divergence extrema fails. No rounding before thresholds.

DEV example, bar 1 taker delta=2*3689.837-7276.249=103.425; cumulative from bar 0 delta `(2*4777.701-8957.465)=597.937` becomes 701.362. This computes the input series only; funding archive values are required for a signal and are not fabricated.

## 15. T055 C2 session momentum — SOURCED paper mechanism; BTC session adaptation OURS

Inputs: UTC bars, session start minute, first window, minimum absolute return, entry minute. S=UTC midnight+start; E=S+first. First return=last completed bar close by E divided by first bar open at/after S minus 1. Side long if >min, short if <-min, otherwise none. Entry is close of bar whose close time equals S+entry_min. Require both endpoint bars and exact boundary; no partial bar lookahead. Retain full precision; missing bars invalidate.

DEV example: for first 1h bar, O=46210.57 and close=46650.01, full-hour return=439.44/46210.57=0.0095097. For a 60-minute first window (OURS illustrative), this would be positive; it is not the default 30-minute calculation because 1h data cannot resolve that boundary.

## 16. T055 C3 turn-of-candle — SOURCED timing observation; side/lead OURS

Inputs: 1-minute bars, epoch timestamp t, lead_minutes and fixed side. `mq=(t_ms//60000)%15`; per-bar return=(C-O)/O. Summary means separate mq=0 from all other minutes and means by minute. Event at mq=15-lead, entered at that bar close. Bar open timestamp determines bucket; event only if complete bar exists. Empty groups undefined; zero open invalid. Full precision, display returns as fractions/percent explicitly.

DEV example limitation: supplied candle archives here are 1h/15m, not 1m DEV bars. Using observed bar 0, return=(46650.01-46210.57)/46210.57=0.0095097, but its 1h candle cannot identify mq or the C3 event. This example is arithmetic only; C3 event example is NOT_IN_DATA in this archive.

## 17. B070 net R:R — OURS (operator ruling), fee rate SOURCED

Inputs: entry E, target T, stop S and per-side taker fraction f. Cost=2*f*E; netRR=(abs(T-E)-cost)/(abs(E-S)+cost); stop=entry returns 0 by explicit convention. Use entry-denominated cost on both legs; full precision then display 4 decimals. Invalid/nonpositive prices or missing stop/target are undefined.

DEV example: E=bar 0 close 46650.01; use bar 1 close 46766.78 as target and low 46570.34 as stop; f=.0005. Reward=116.77, risk=79.67, cost=46.65001; netRR=(116.77-46.65001)/(79.67+46.65001)=0.5551.

## 18. Anchored volume profile touch study — mixed SOURCED profile levels; pivot/bin/outcome rules OURS

Inputs: OHLCV bar set, bin width w, UTC anchor family, confirmed pivots, refresh time, ATR, touch horizon H, fee fractions. Bin k is [kw,(k+1)w); assign each bar’s volume to its typical-price bin per catalog. POC is greatest volume bin (tie resolution as stated in catalog); value area expands from POC by adjacent greatest-volume bins to 70% total, yielding VAH/VAL. Families use UTC session/week/prior-period or specified pivot anchors. 5m profiles refresh on 15m grid from bars closed before refresh; developing families need 12 bars. Touch at j requires low<=L<=high and previous close !=L; side from previous close. R is ATR14 from 1h bars closed before j; barriers ±1R, touch bar tests stop only, later bars test stop before target, then timeout at j+H. One active event per family/level stream. Fees are fractions of entry/exit price; report gross/net R. Never use an unfinished refresh bucket.

DEV example: bar 0 observed range [46210.55,46729.73], typical price=(H+L+C)/3=(46729.73+46210.55+46650.01)/3=46530.0967. With illustrative OURS w=10, it maps to bin floor(46530.0967/10)=4653, interval [46530,46540). A single bar cannot define a profile/value area or 5m touch event.

## 19. Trend-line contract, subentries 19.1–19.8 — SOURCED trader concept; numeric tolerances/parameters OURS

Inputs: closed OHLC bars, strict pivot side width k, two anchor indices/prices, linear or log mode, ATR14, volume history and contact thresholds. A low/high pivot beats every bar in k bars on both sides, confirmed at close i+k. Line is linear interpolation or exponential interpolation in log price. ATR is section 12; slope is price change per bar divided by ATR, or log-price change per bar. Touch/poke/break/episode and volume tests use contract multipliers: touch 0.25 ATR, poke 0.10 ATR, break by close through line, reset beyond 1 ATR, anchor volume >=2x mean of prior 20. Third anchor tolerance 0.25 ATR. No ties pass strict pivots; insufficient side bars means unavailable. Calculations full precision.

DEV example: actual bar 0 low 46210.55 and bar 1 low 46570.34; as illustrative linear anchors (i=0,p=46210.55),(i=1,p=46570.34), L(2)=46930.13. This does not assert either bar is a confirmed pivot.

## 20. WaveTrend, subentries 20.1–20.4 — SOURCED LazyBear equations; gap/zone/cross policy OURS

Inputs: closed OHLC and periods (10,10,21,4); ap=(H+L+C)/3; ESA EMA(ap,10); d=EMA(abs(ap-ESA),10); ci=(ap-ESA)/(.015*d); WT1=EMA(ci,21); WT2=SMA(WT1,4). Catalog EMA here seeds from first valid input; unlike entry 4’s SMA-seeded EMA. Warmup 200 bars from start/gap/NaN; if d<=1e-9*abs(ap), ci unavailable. WT2 needs four valid WT1. Cross tracks last strict side, skips ties, resets at NaN; zones use inclusive bounds ±53/±60. HTF value is last bar whose close time<=query time. No rounding before crosses; golden comparison tolerance 1e-9 is OURS.

DEV example, bar 0 ap=(46729.73+46210.55+46650.01)/3=46530.0967. This is the source input for ESA; output is not yet valid under the 200-bar warmup. Early warmup and d=0 are explicit no-signal cases.

## 21. Krown detectors, subentries 21.1–21.9 — mixed SOURCED KR ledger / OURS parameters

Inputs: closed OHLCV bars, configured k/periods/tolerances/windows. Zones span pivot wick extreme to close, available only after k right bars; qualify by turns/volume and rank by heavy, turns, recency (max five). Volume ratio compares current V to mean of 20 PRIOR bars; same-slot baseline uses prior m weeks. Strict engulfing requires low<prior low and close>prior high (bearish mirror); candle shape ratios follow configured thresholds. Pivots are strict and confirmed i+k. Structural state uses latest two pivot highs/lows and tolerance; reversal requires trade-through and close-through. BBWP is 4*populationSD/SMA over basis 7 then strict prior-lookback percentile (default 100), regime thresholds as catalog. EMA5 uses SMA seed; leash threshold needs 3 prior closes beyond EMA, event when EMA touched. RSI is Wilder with configured 14; zones >60/<40, inclusive middle. Range uses prior 20 highs/lows; edge position <=.2 or >=.8; coil compares recent-five mean range with prior window and <.7. Tops combine 4 signal families in 3-bar window and fire on transition to count>=3. Missing warmup values produce no detector; strict comparisons and boundary inclusivity follow each rule; no early rounding.

DEV example, volume section: bar 1 V=7276.249; prior bar 0 V=8957.465, so with a one-bar illustrative prior baseline ratio=0.8123. For actual configured 20-bar baseline this early point is warmup and has no volume signal. Example shows why warmup must not be treated as a ratio.

## 22. Bollinger Bands — SOURCED TradingView definition/defaults

Inputs: closes, n=20 and multiplier=2 unless overridden. At bar close t use last n closes; middle=mean, standard deviation is population (divide squared deviations by n), upper/lower=middle±mult*sd. None before n observations; full precision, display per caller. A missing close invalidates the window; zero variance gives equal bands.

DEV example, n=2, closes bars 0–1 [46650.01,46766.78]: mean=46708.395, population sd=58.385, bands with multiplier 2 are 46591.625 and 46825.165 at bar 1 close.

## 23. Stochastic RSI — SOURCED default periods; flat-range raw=0 OURS

Inputs: close series; RSI is entry 1; defaults RSI length 14, stochastic length 14, K SMA 3, D SMA 3. For each t with 14 RSI values, raw=100*(RSI[t]-window_min)/(window_max-window_min); if max=min raw=0. K is SMA of 3 raw values, D SMA of 3 K values. Values align to the last input bar; no output until all nested warmups complete. Missing values invalidate/restart windows; do not divide by zero. Keep full precision; display 4 decimals.

DEV example: bars 0–2 produce RSI at bar 2 of 100 (entry 1); only one RSI exists, so a 14-value stochastic window and K/D are unavailable. This is a data-derived warmup example, not an invented oscillator value.
