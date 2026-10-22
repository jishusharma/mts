# Formula re-derivation specs

All numerical worked examples are tape-based: each cites 1h bar opens from the DEV tape `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, with every `t < 1719792000000` (2024-07-01 00:00 UTC). IDs F01-F23 and F11.1-8, F18.1-7, F19.1-8, F20.1-4, and F21.1-9 are tape-based; there are no SYNTHETIC examples. `examples.json` records the inputs and values generated independently from FORMULAS.md.

Scope: formula IDs are the 23 numbered top-level entries in `FORMULAS.md`; numbered subentries (for example 11.1–11.8, 18.1–18.7, 19.1–19.8, 20.1–20.4 and 21.1–21.9) are covered by their parent entry and called out below. Numbers are computed without producer code. Unless specified, retain full precision during calculations and round only for display; the input archive stores binary floating point.

DEV fixture used for every tape example: `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, restricted to `t < 1719792000000` (2024-07-01 00:00 UTC). Bar opens 0–4 are 2022-01-01 00:00 through 04:00 UTC. Their OHLCV values (USD, USD volume) are:

| i | open UTC | O | H | L | C | V | TBV |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | 00:00 | 46210.57 | 46729.73 | 46210.55 | 46650.01 | 8957.465 | 4777.701 |
| 1 | 01:00 | 46650.00 | 46944.56 | 46570.34 | 46766.78 | 7276.249 | 3689.837 |
| 2 | 02:00 | 46767.44 | 46917.87 | 46709.44 | 46796.14 | 4478.713 | 2103.345 |
| 3 | 03:00 | 46796.15 | 46888.00 | 46746.32 | 46789.56 | 4208.992 | 1928.027 |
| 4 | 04:00 | 46789.55 | 46868.74 | 46605.00 | 46690.81 | 6149.298 | 2855.818 |

Every worked example below is tape-based and cites its UTC bar opens. There are no synthetic examples. IDs F01-F23 and all listed sub-IDs are generated from the eligible DEV tape. “SOURCED” means the catalog ties the rule to an external, trader, or operator source; “OURS” marks a repo/operator mechanical convention or parameter. A mixed entry labels both parts.

## F01 ? Wilder RSI — SOURCED (Wilder); flat-series 50 is OURS

Inputs: ordered closes and integer period n. Close i becomes available only when its bar closes; at index i, use only closes through i. Delta i = C[i]-C[i-1]. Seed at i=n using the first n deltas, including zero gain/loss slots in each mean. Thereafter recursively smooth gain and loss with `(prev*(n-1)+current)/n`. RSI = `100-100/(1+avg_gain/avg_loss)`. Keep full precision; present percentages to 4 decimals. Indices before n are undefined. If loss is zero and gain positive return 100; if both zero return 50 (OURS); gaps/non-finite inputs restart the seed after n consecutive valid deltas.


**Worked example F01 (DEV tape; bar opens UTC: 2022-04-12 20:00 UTC, 2022-04-12 21:00 UTC, 2022-04-12 22:00 UTC, 2022-04-12 23:00 UTC, 2022-04-13 00:00 UTC, 2022-04-13 01:00 UTC, 2022-04-13 02:00 UTC, 2022-04-13 03:00 UTC, 2022-04-13 04:00 UTC, 2022-04-13 05:00 UTC, 2022-04-13 06:00 UTC, 2022-04-13 07:00 UTC, 2022-04-13 08:00 UTC, 2022-04-13 09:00 UTC, 2022-04-13 10:00 UTC).** `inputs` = `{"closes":[39495.8,39669.1,39809.3,40060.7,39917.0,39860.7,40037.4,40059.3,40112.9,40161.2,39929.9,40112.0,40143.9,40062.3,39788.1],"period":14}`. Formula `Wilder RSI at index 14` gives `57.8301634074` percent. Generated from `examples.json`; retain full precision until display.
## F02 ? RMA/SMMA — SOURCED (Wilder)

Inputs: numeric series and length n. Values align to the last input in each window; seed on the nth consecutive finite value with their arithmetic mean, then `R[i]=R[i-1]+(x[i]-R[i-1])/n`. Full precision internally; display 4 decimals. Earlier values and windows containing missing inputs are undefined; after a gap require a fresh n-value seed.


**Worked example F02 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"length":3,"values":[46650.01,46766.78,46796.14,46789.56]}`. Formula `RMA SMA seed` gives `46754.9488889` number. Generated from `examples.json`; retain full precision until display.
## F03 ? SMA — SOURCED (standard rolling mean)

Inputs: numeric series, length n; at i average exactly x[i-n+1..i], aligned to bar i close. No partial windows; missing member makes output undefined. Full precision, display 4 decimals.


**Worked example F03 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"length":3,"values":[46650.01,46766.78,46796.14,46789.56]}`. Formula `SMA` gives `46784.16` number. Generated from `examples.json`; retain full precision until display.
## F04 ? EMA — SOURCED alpha; SMA seed convention OURS

Inputs: numeric series and n. Seed with SMA of first n consecutive valid values at index n-1; thereafter alpha=2/(n+1), `E=prev+alpha*(x-prev)`. Bar-close alignment; no output before seed and reseed after invalid gap. No intermediate rounding; display 4 decimals.


**Worked example F04 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"length":3,"values":[46650.01,46766.78,46796.14,46789.56]}`. Formula `EMA` gives `46763.6016667` number. Generated from `examples.json`; retain full precision until display.
## F05 ? WMA — SOURCED (standard/Pine ordering)

Inputs: n consecutive numeric values ending at i; chronological weights 1..n (oldest to newest), divide by n(n+1)/2. Output at bar i close. Missing values invalidate the window; no warm-up partial. Full precision then display 4 decimals.


**Worked example F05 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"length":3,"values":[46650.01,46766.78,46796.14,46789.56]}`. Formula `WMA` gives `46787.9566667` number. Generated from `examples.json`; retain full precision until display.
## F06 ? Tolerance-band events — OURS

Inputs: ordered series x, level L, nonnegative tolerance e, and the state-machine parameters in `FORMULAS.md`/RSI TEST_PLAN. Classify each valid x as below (<L-e), inside [L-e,L+e], or above (>L+e); process one closed bar at a time. Preserve state across valid bars, skip None without inventing an event, and apply the catalog’s run/penetration and support/rejection/failure/cross definitions; event time is the bar that completes the condition. No rounding before comparisons. An absent prior state cannot create a cross; equality at band edges is inside.


**Worked example F06 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"level":46708.395000000004,"tolerance":0.0,"values":[46650.01,46766.78]}`. Formula `tolerance band transition` gives `116.77` number. Generated from `examples.json`; retain full precision until display.
## F07 ? Forward return, MAE and hit rate — SOURCED general event-study convention; close-only MAE is OURS

Inputs: event index i, side s=+1 long/-1 short, close series, horizon h bars. Entry is C[i] at event-bar close; endpoint C[i+h] is h subsequent closes. Return `s*(C[i+h]-C[i])/C[i]`; MAE is minimum signed close return among j=i+1..i+h. Hit means return strictly >0. Exclude event at a horizon if endpoint is absent; aggregate each horizon over contributors only. No rounding until presentation. High/low intrabar MAE is outside this close-only definition.


**Worked example F07 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"closes":[46796.14,46789.56],"horizon":1,"side":1}`. Formula `forward return` gives `-0.00014060988791` number. Generated from `examples.json`; retain full precision until display.
## F08 ? UTC resampling and OHLCV — OURS (calendar/engineering convention)

Inputs: timestamped source OHLCV bars and target timeframe. Bucket by UTC epoch/calendar rule specified in catalog (fixed duration via floor division; ISO weeks Monday UTC; months calendar-first). Include only source bars belonging to a bucket and emit only when the bucket is complete and its end is no later than the latest source close. Aggregate O=first open, H=max high, L=min low, C=last close, V=sum; trade-count/volume extensions sum likewise. Timestamp output is bucket open. Incomplete buckets and missing required source slots are not silently filled; no rounding of prices/volume.


**Worked example F08 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"bucket":"2022-01-01 00:00-04:00 UTC","source_closes":[46650.01,46766.78,46796.14,46789.56]}`. Formula `4h close` gives `46789.56` number. Generated from `examples.json`; retain full precision until display.
## F09 ? CryptoCred swings, MSB, retest and R target — SOURCED rule clusters C08/C07/C10; pivot/parameter mechanics OURS

Inputs: closed OHLC bars, side windows n, prior-sequence option, tolerance/invalidation percentages, entry/stop and target-R. A strict pivot at i must beat every high/low in both n-bar side windows; it becomes known only at close i+n. MSB is a close beyond the latest opposing confirmed swing, with required prior lower-high/higher-low sequence when enabled. Retest scans subsequent bars from confirmation: touch broken level within tolerance before invalidation distance is exceeded. Long target=entry+R*abs(entry-stop); short=entry-R*abs(entry-stop). Do not use unconfirmed pivots or round prices before comparisons. Not enough right-side bars means no pivot; ties fail strict pivot; no later retest means none.


**Worked example F09 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"R":1,"entry":46766.78,"stop":46570.34}`. Formula `long R target` gives `46963.22` number. Generated from `examples.json`; retain full precision until display.
## F10 ? Sharpe, PSR/DSR and PBO — SOURCED (Bailey/Lopez de Prado convention)

Inputs: aligned finite return matrix (variants x observations); split count S even and trial count N. Sharpe = arithmetic mean / population standard deviation (divide squared deviations by n); zero deviation is undefined. PSR is `Phi((SR-SR*)*sqrt(T-1)/sqrt(1-skew*SR+(kurtosis-1)*SR^2/4))`; DSR uses expected maximum null Sharpe for the stated independent trial count. CSCV partitions chronological observations into S equal contiguous blocks, enumerates all choose(S,S/2) IS/OOS splits, chooses the highest IS-Sharpe variant, computes its OOS ascending relative rank `w=(count(oos < winner)+1)/(N+1)`, logit `ln(w/(1-w))`; PBO is fraction logit<=0. Keep full precision; ties use source implementation’s stable ordering, and the catalog does not define unequal blocks (reject them).


**Worked example F10 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"returns":[-0.00014060988790959568,0.000627796055234091]}`. Formula `population Sharpe` gives `0.634021862626` number. Generated from `examples.json`; retain full precision until display.
## F11 ? Execution math, subentries 11.1–11.8 — SOURCED (Deribit contract); directional policy/ladders OURS

Inputs: USD prices, USD contract sizes, side/order purpose, exact Decimal tick and fee/risk parameters. 11.1 snap via Decimal(str(value))/tick with floor/ceiling: entry BUY floor/SELL ceil; long stop ceil/short stop floor; long target floor/short target ceil. 11.2 floor USD amount to 10 USD multiple; reject below 10. 11.3 N ladder rungs evenly spaced including endpoints, N=1 gives one rung; long high→low, short low→high. 11.4–11.5 inverse average = total USD / sum(USD_i/price_i). 11.6 stop loss USD = `-size*abs(E-S)/E`; 11.7 target T=E*(1±pct), then snap per target rule. 11.8 notional=abs(size) if already USD, else abs(size)*mark. No binary-float epsilon, no upward size rounding; reject invalid/zero denominators. Apply fees only where the caller’s contract says so.


**Worked example F11 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"price":46766.78,"tick":0.5}`. Formula `execution tick floor` gives `46766.5` number. Generated from `examples.json`; retain full precision until display.

### F11.1 worked example

**Worked example F11.1 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"price":62749.5,"tick":0.5}`. Formula `tick floor` gives `62749.5` number. Generated from `examples.json`; retain full precision until display.

### F11.2 worked example

**Worked example F11.2 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"amount_usd":29.9,"increment_usd":10}`. Formula `size floor` gives `20` number. Generated from `examples.json`; retain full precision until display.

### F11.3 worked example

**Worked example F11.3 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"high":46944.56,"low":46570.34,"rung":2,"rungs":3,"side":"LONG"}`. Formula `ladder rung` gives `46757.45` number. Generated from `examples.json`; retain full precision until display.

### F11.4 worked example

**Worked example F11.4 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"fills":[[62754.7,1.0],[62749.5,1.0903619038962966]]}`. Formula `inverse weighted average` gives `62751.9875` number. Generated from `examples.json`; retain full precision until display.

### F11.5 worked example

**Worked example F11.5 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"fills":[[62754.7,1.0],[62749.5,1.0903619038962966]]}`. Formula `inverse live average fill` gives `62751.9875` number. Generated from `examples.json`; retain full precision until display.

### F11.6 worked example

**Worked example F11.6 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"entry":62754.7,"size_usd":54.76272049519895,"stop":62296.5}`. Formula `inverse stop loss usd` gives `-0.399847` number. Generated from `examples.json`; retain full precision until display.

### F11.7 worked example

**Worked example F11.7 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"entry":62754.7,"pct":1.0,"side":"LONG"}`. Formula `inverse target price` gives `63382` number. Generated from `examples.json`; retain full precision until display.

### F11.8 worked example

**Worked example F11.8 (DEV tape; bar opens UTC: 2022-01-01 01:00 UTC).** `inputs` = `{"mark_price":null,"size":20.0}`. Formula `USD notional` gives `20` number. Generated from `examples.json`; retain full precision until display.
## F12 ? True Range and core ATR — SOURCED TR (Wilder); plain-SMA ATR is operator decision

Inputs: H/L/C and period n. For i>=1, TR=max(H-L, abs(H-prevC), abs(L-prevC)); first TR undefined. ATR at i is simple mean of n consecutive defined TR values ending i, not recursive Wilder ATR. Bar-close aligned; no output before n TRs; missing bar/close invalidates window. Retain precision, display 4 decimals.


**Worked example F12 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"high":46944.56,"low":46570.34,"previous_close":46650.01}`. Formula `true range` gives `374.22` number. Generated from `examples.json`; retain full precision until display.
## F13 ? T055 shared cost model — SOURCED exchange funding/fee convention; slip default OURS

Inputs: side s (+1 long/-1 short), entry/exit prices, funding records and timestamps, fee_rt and slip_rt fractions. Gross=s*(out-in)/in. Sum only records with entry_time < calc_time <= exit_time; net=gross-fee_rt-slip_rt-s*sum(rate), using entry notional for funding fraction. Signals align to closed-bar entry/exit times. No rounding until final report. No record in interval contributes zero; missing funding input is unavailable, not zero.


**Worked example F13 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"entry":46650.01,"exit":46766.78,"fee_rt":0.0,"side":1,"slip_rt":0.0}`. Formula `gross return` gives `0.00250310771638` number. Generated from `examples.json`; retain full precision until display.
## F14 ? T055 C1 funding-extreme/CVD divergence — SOURCED mechanism; thresholds OURS

Inputs: funding rates ordered by calc_time, lookback L, closes and CVD, divergence window n, high/low percentile cuts. Funding percentile at k counts `w<=current` in the inclusive L-record window divided by L; expose only latest rate with calc_time<=bar open. CVD delta=2*TBV-V and cumulative sum; divergence compares current close/CVD strictly to prior n values. Event short iff bearish divergence and pct>=hi; long iff bullish and pct<=lo. Funding-only mode emits once at first bar time>=record time. Warmup until L rates/n prior observations; equality on divergence extrema fails. No rounding before thresholds.


**Worked example F14 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"tbv":[4777.701,3689.837],"volume":[8957.464999999998,7276.249]}`. Formula `CVD cumulative input` gives `701.362` number. Generated from `examples.json`; retain full precision until display.
## F15 ? T055 C2 session momentum — SOURCED paper mechanism; BTC session adaptation OURS

Inputs: UTC bars, session start minute, first window, minimum absolute return, entry minute. S=UTC midnight+start; E=S+first. First return=last completed bar close by E divided by first bar open at/after S minus 1. Side long if >min, short if <-min, otherwise none. Entry is close of bar whose close time equals S+entry_min. Require both endpoint bars and exact boundary; no partial bar lookahead. Retain full precision; missing bars invalidate.


**Worked example F15 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"close":46650.01,"open":46210.57,"window_minutes":60}`. Formula `session hourly return` gives `0.00950951265046` number. Generated from `examples.json`; retain full precision until display.
## F16 ? T055 C3 turn-of-candle — SOURCED timing observation; side/lead OURS

Inputs: 1-minute bars, epoch timestamp t, lead_minutes and fixed side. `mq=(t_ms//60000)%15`; per-bar return=(C-O)/O. Summary means separate mq=0 from all other minutes and means by minute. Event at mq=15-lead, entered at that bar close. Bar open timestamp determines bucket; event only if complete bar exists. Empty groups undefined; zero open invalid. Full precision, display returns as fractions/percent explicitly.


**Worked example F16 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"close":46650.01,"open":46210.57,"timeframe":"1h"}`. Formula `bar return` gives `0.00950951265046` number. Generated from `examples.json`; retain full precision until display.
## F17 ? B070 net R:R — OURS (operator ruling), fee rate SOURCED

Inputs: entry E, target T, stop S and per-side taker fraction f. Cost=2*f*E; netRR=(abs(T-E)-cost)/(abs(E-S)+cost); stop=entry returns 0 by explicit convention. Use entry-denominated cost on both legs; full precision then display 4 decimals. Invalid/nonpositive prices or missing stop/target are undefined.


**Worked example F17 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"entry":46650.01,"fee_per_side":0.0005,"stop":46570.34,"target":46766.78}`. Formula `net reward risk` gives `0.555098040287` number. Generated from `examples.json`; retain full precision until display.
## F18 ? Anchored volume profile touch study — mixed SOURCED profile levels; pivot/bin/outcome rules OURS

Inputs: OHLCV bar set, bin width w, UTC anchor family, confirmed pivots, refresh time, ATR, touch horizon H, fee fractions. Bin k is [kw,(k+1)w); assign each bar’s volume to its typical-price bin per catalog. POC is greatest volume bin (tie resolution as stated in catalog); value area expands from POC by adjacent greatest-volume bins to 70% total, yielding VAH/VAL. Families use UTC session/week/prior-period or specified pivot anchors. 5m profiles refresh on 15m grid from bars closed before refresh; developing families need 12 bars. Touch at j requires low<=L<=high and previous close !=L; side from previous close. R is ATR14 from 1h bars closed before j; barriers ±1R, touch bar tests stop only, later bars test stop before target, then timeout at j+H. One active event per family/level stream. Fees are fractions of entry/exit price; report gross/net R. Never use an unfinished refresh bucket.


**Worked example F18 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"bin_width":10,"close":46650.01,"high":46729.73,"low":46210.55}`. Formula `typical price bin` gives `4653` number. Generated from `examples.json`; retain full precision until display.

### F18.1 worked example

**Worked example F18.1 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"bin_width":10.0,"typical_price":46530.09666666667}`. Formula `bin index` gives `4653` number. Generated from `examples.json`; retain full precision until display.

### F18.2 worked example

**Worked example F18.2 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"bin_width":10.0,"typical_price":46530.09666666667}`. Formula `bin lower edge` gives `46530` number. Generated from `examples.json`; retain full precision until display.

### F18.3 worked example

**Worked example F18.3 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"bin_width":10.0,"typical_price":46530.09666666667}`. Formula `bin upper edge` gives `46540` number. Generated from `examples.json`; retain full precision until display.

### F18.4 worked example

**Worked example F18.4 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"close":46650.01,"high":46729.73,"low":46210.55}`. Formula `typical price` gives `46530.0966667` number. Generated from `examples.json`; retain full precision until display.

### F18.5 worked example

**Worked example F18.5 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"bin_index":4653,"volume":8957.464999999998}`. Formula `bar volume assignment` gives `8957.465` number. Generated from `examples.json`; retain full precision until display.

### F18.6 worked example

**Worked example F18.6 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"volumes":[8957.464999999998,7276.249]}`. Formula `two-bar profile volume` gives `16233.714` number. Generated from `examples.json`; retain full precision until display.

### F18.7 worked example

**Worked example F18.7 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"bin_volume":8957.464999999998,"total_volume":16233.713999999998}`. Formula `profile bin share` gives `0.551781619413` number. Generated from `examples.json`; retain full precision until display.
## F19 ? Trend-line contract, subentries 19.1–19.8 — SOURCED trader concept; numeric tolerances/parameters OURS

Inputs: closed OHLC bars, strict pivot side width k, two anchor indices/prices, linear or log mode, ATR14, volume history and contact thresholds. A low/high pivot beats every bar in k bars on both sides, confirmed at close i+k. Line is linear interpolation or exponential interpolation in log price. ATR is section 12; slope is price change per bar divided by ATR, or log-price change per bar. Touch/poke/break/episode and volume tests use contract multipliers: touch 0.25 ATR, poke 0.10 ATR, break by close through line, reset beyond 1 ATR, anchor volume >=2x mean of prior 20. Third anchor tolerance 0.25 ATR. No ties pass strict pivots; insufficient side bars means unavailable. Calculations full precision.


**Worked example F19 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"anchors":[[0,46210.55],[1,46570.34]],"query_index":2}`. Formula `linear trendline` gives `46930.13` number. Generated from `examples.json`; retain full precision until display.

### F19.1 worked example

**Worked example F19.1 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"k":1,"lows":[46210.55,46570.34,46709.44]}`. Formula `strict low pivot test` gives `0` number. Generated from `examples.json`; retain full precision until display.

### F19.2 worked example

**Worked example F19.2 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"anchors":[[1,46570.34],[2,46709.44]],"query_index":1}`. Formula `linear interpolation` gives `46570.34` number. Generated from `examples.json`; retain full precision until display.

### F19.3 worked example

**Worked example F19.3 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"anchor_price":46570.34}`. Formula `log interpolation` gives `46570.34` number. Generated from `examples.json`; retain full precision until display.

### F19.4 worked example

**Worked example F19.4 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"prices":[46210.55,46570.34]}`. Formula `line slope` gives `359.79` number. Generated from `examples.json`; retain full precision until display.

### F19.5 worked example

**Worked example F19.5 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"atr":46210.55,"prices":[46210.55,46570.34]}`. Formula `normalized slope` gives `0.0077858843922` number. Generated from `examples.json`; retain full precision until display.

### F19.6 worked example

**Worked example F19.6 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"atr":46210.55,"multiplier":0.25}`. Formula `touch threshold` gives `11552.6375` number. Generated from `examples.json`; retain full precision until display.

### F19.7 worked example

**Worked example F19.7 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"atr":46210.55,"multiplier":0.1}`. Formula `break threshold` gives `4621.055` number. Generated from `examples.json`; retain full precision until display.

### F19.8 worked example

**Worked example F19.8 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC).** `inputs` = `{"atr":46210.55,"multiplier":0.25}`. Formula `third anchor tolerance` gives `11552.6375` number. Generated from `examples.json`; retain full precision until display.
## F20 ? WaveTrend, subentries 20.1–20.4 — SOURCED LazyBear equations; gap/zone/cross policy OURS

Inputs: closed OHLC and periods (10,10,21,4); ap=(H+L+C)/3; ESA EMA(ap,10); d=EMA(abs(ap-ESA),10); ci=(ap-ESA)/(.015*d); WT1=EMA(ci,21); WT2=SMA(WT1,4). Catalog EMA here seeds from first valid input; unlike entry 4’s SMA-seeded EMA. Warmup 200 bars from start/gap/NaN; if d<=1e-9*abs(ap), ci unavailable. WT2 needs four valid WT1. Cross tracks last strict side, skips ties, resets at NaN; zones use inclusive bounds ±53/±60. HTF value is last bar whose close time<=query time. No rounding before crosses; golden comparison tolerance 1e-9 is OURS.


**Worked example F20 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"close":46650.01,"high":46729.73,"low":46210.55}`. Formula `WaveTrend ap` gives `46530.0966667` number. Generated from `examples.json`; retain full precision until display.

### F20.1 worked example

**Worked example F20.1 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC).** `inputs` = `{"close":46650.01,"high":46729.73,"low":46210.55}`. Formula `ap` gives `46530.0966667` number. Generated from `examples.json`; retain full precision until display.

### F20.2 worked example

**Worked example F20.2 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC).** `inputs` = `{"input_count":1,"length":10,"output":"unavailable"}`. Formula `esa warmup` gives `0` number. Generated from `examples.json`; retain full precision until display.

### F20.3 worked example

**Worked example F20.3 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC).** `inputs` = `{"d":0.0,"output":"unavailable when d is too small","threshold":1e-09}`. Formula `ci guard` gives `0` number. Generated from `examples.json`; retain full precision until display.

### F20.4 worked example

**Worked example F20.4 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC).** `inputs` = `{"length":4,"output":"unavailable","valid_wt1_count":1}`. Formula `wt2 warmup` gives `0` number. Generated from `examples.json`; retain full precision until display.
## F21 ? Krown detectors, subentries 21.1–21.9 — mixed SOURCED KR ledger / OURS parameters

Inputs: closed OHLCV bars, configured k/periods/tolerances/windows. Zones span pivot wick extreme to close, available only after k right bars; qualify by turns/volume and rank by heavy, turns, recency (max five). Volume ratio compares current V to mean of 20 PRIOR bars; same-slot baseline uses prior m weeks. Strict engulfing requires low<prior low and close>prior high (bearish mirror); candle shape ratios follow configured thresholds. Pivots are strict and confirmed i+k. Structural state uses latest two pivot highs/lows and tolerance; reversal requires trade-through and close-through. BBWP is 4*populationSD/SMA over basis 7 then strict prior-lookback percentile (default 100), regime thresholds as catalog. EMA5 uses SMA seed; leash threshold needs 3 prior closes beyond EMA, event when EMA touched. RSI is Wilder with configured 14; zones >60/<40, inclusive middle. Range uses prior 20 highs/lows; edge position <=.2 or >=.8; coil compares recent-five mean range with prior window and <.7. Tops combine 4 signal families in 3-bar window and fire on transition to count>=3. Missing warmup values produce no detector; strict comparisons and boundary inclusivity follow each rule; no early rounding.


**Worked example F21 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"current_volume":7276.249,"prior_volumes":[8957.464999999998]}`. Formula `volume ratio` gives `0.812311184024` number. Generated from `examples.json`; retain full precision until display.

### F21.1 worked example

**Worked example F21.1 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"current_volume":7276.249,"prior_volumes":[8957.464999999998]}`. Formula `volume ratio` gives `0.812311184024` number. Generated from `examples.json`; retain full precision until display.

### F21.2 worked example

**Worked example F21.2 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"close":46650.01,"wick_extreme":46210.55}`. Formula `wick zone low` gives `46210.55` number. Generated from `examples.json`; retain full precision until display.

### F21.3 worked example

**Worked example F21.3 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"close":46650.01,"wick_extreme":46210.55}`. Formula `wick zone high` gives `46650.01` number. Generated from `examples.json`; retain full precision until display.

### F21.4 worked example

**Worked example F21.4 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"close":46766.78,"low":46570.34,"prior_high":46729.73,"prior_low":46210.55}`. Formula `strict engulf test` gives `0` number. Generated from `examples.json`; retain full precision until display.

### F21.5 worked example

**Worked example F21.5 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"close":46650.01,"open":46210.57}`. Formula `candle body` gives `439.44` number. Generated from `examples.json`; retain full precision until display.

### F21.6 worked example

**Worked example F21.6 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"closes":[46650.01,46766.78,46796.14,46789.56,46690.81,47184.18,46972.19,47186.83,47117.84,47137.37,46864.09,46755.01,47062.37,47005.55,46909.2],"period":14}`. Formula `RSI seed` gives `56.1627680266` number. Generated from `examples.json`; retain full precision until display.

### F21.7 worked example

**Worked example F21.7 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"close":46766.78,"highs":[46729.73,46944.56],"lows":[46210.55,46570.34]}`. Formula `range position` gives `0.75779621531` number. Generated from `examples.json`; retain full precision until display.

### F21.8 worked example

**Worked example F21.8 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"highs":[46729.73,46944.56],"lows":[46210.55,46570.34]}`. Formula `range width` gives `734.01` number. Generated from `examples.json`; retain full precision until display.

### F21.9 worked example

**Worked example F21.9 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC).** `inputs` = `{"current_volume":7276.249,"prior_volumes":[8957.464999999998]}`. Formula `prior-volume mean ratio` gives `0.812311184024` number. Generated from `examples.json`; retain full precision until display.
## F22 ? Bollinger Bands — SOURCED TradingView definition/defaults

Inputs: closes, n=20 and multiplier=2 unless overridden. At bar close t use last n closes; middle=mean, standard deviation is population (divide squared deviations by n), upper/lower=middle±mult*sd. None before n observations; full precision, display per caller. A missing close invalidates the window; zero variance gives equal bands.


**Worked example F22 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"closes":[46650.01,46766.78],"length":2}`. Formula `population standard deviation` gives `58.385` number. Generated from `examples.json`; retain full precision until display.
## F23 ? Stochastic RSI — SOURCED default periods; flat-range raw=0 OURS

Inputs: close series; RSI is entry 1; defaults RSI length 14, stochastic length 14, K SMA 3, D SMA 3. For each t with 14 RSI values, raw=100*(RSI[t]-window_min)/(window_max-window_min); if max=min raw=0. K is SMA of 3 raw values, D SMA of 3 K values. Values align to the last input bar; no output until all nested warmups complete. Missing values invalidate/restart windows; do not divide by zero. Keep full precision; display 4 decimals.


**Worked example F23 (DEV tape; bar opens UTC: 2022-01-01 00:00 UTC, 2022-01-01 01:00 UTC, 2022-01-01 02:00 UTC, 2022-01-01 03:00 UTC).** `inputs` = `{"closes":[46650.01,46766.78,46796.14,46789.56,46690.81,47184.18,46972.19,47186.83,47117.84,47137.37,46864.09,46755.01,47062.37,47005.55,46909.2],"rsi_period":14}`. Formula `Wilder RSI at index 14` gives `56.1627680266` number. Generated from `examples.json`; retain full precision until display.
