# PRE-REGISTRATION: BTC volume study V0-V2 (frozen before any outcome is computed)

Session MTS-2026-10-09-APP-ANA-btc-volume (App, JIS-NUC work tree). Written 2026-10-09. The commit that adds this file precedes the commit
that adds any result file; `git log` is the proof. Status of everything below: EXPLORATORY TRIAL. Nothing here adopts a rule
(BACKTEST_PROTOCOL.md section 6 is not met by a DEV run).

Operator ask (2026-10-09, core): "Buy volume and Sell Volume ... 'Volume cannot be hidden' ... trading verified strategies clubbed with volume and
candle stick patterns ... consolidations and patterns ... mid/long term ... Price Action, Volatility tools like BB, momentum tool like RSI (preferably 40/60) ...
Exhaustion volume ... how MTS will use it" and (follow-up) "Also combine time analysis to this list".

## 0. Provenance and scope (CLAUDE.md Provenance, PROJECT_VISION)
- Trader transcripts (raw_transcripts_canonical, 102 files) name volume concepts (absorption, exhaustion, volume profile, cumulative delta) but give NO numeric rule;
  "volume cannot be hidden" is not in the corpus. So every number below is an engineering/literature candidate, tagged NO-SOURCE-TRADER, EVIDENCE-ONLY.
  Outcome: results can create a separate read layer with data provenance. They never enter Tom as a filter or a proof.
- Literature ranks what to test; only our own OOS result decides (BTC_SESSION_EXTERNAL rule).
- Known priors from this repo: 0/108 classical candle patterns pass triage; rsi 40/60 events, fabio cvd_absorption/volume_fvg, funding_cvd_fade all NO-EDGE
  (MARKET_GUIDE_RESULTS_2026-10-07.md). Expectation before any run: most volume rules also fail. A null is a finding.

## 1. Data and split (fixed)
BTCUSDT USD-M perpetual, data.binance.vision monthly archive, UTC bars, fields open_time, o, h, l, c, volume (base), quote_volume, trades, taker_buy_base (tbv).
- 1d and 1h: 2020-01-01 .. 2026-09-30 (downloaded 2026-10-09 by fetch_binance_archive.py, SHA256 verified, under Dumps/backtest/raw_1d, raw_1h). 4h = 4 consecutive 1h bars at 00/04/08/12/16/20 UTC, complete buckets only.
- Funding: archive fundingRate monthly (Dumps/backtest/raw_fund), 8h settlements 00/08/16 UTC.
- DEV: bar open < 2024-07-01. VALIDATION: 2024-07-01 .. 2025-06-30 (run once per frozen candidate set). HOLDOUT: 2025-07-01 .. 2026-09-30, sealed; the loader refuses it without unseal=True,
  which V0/V1 never pass. Mid/long-term focus: primary timeframes 1d and 4h. 1h is used only for the descriptive time map. Weekly bars are NOT tested (about 230 DEV bars = no power; stated, not hidden).
- Taker-buy caveat: tbv is Binance-perp taker volume (one venue); the volume in "volume cannot be hidden" is one venue's, not market-wide.

## 2. Cost model (all event results are NET unless labelled gross)
Round trip 14 bps (taker 5 bps + 2 bps slippage per side, backtest/fees.py); funding realised inside the hold: long pays, short receives. Entry open(i+1), exit open(i+1+h).
Net per trade = sign*ln(exit/entry) - 0.0014 - sign*sum(funding in [entry, exit)).

## 3. Definitions (per bar i; all use data up to the close of bar i only; rolling windows end at i-1 unless stated)
- ret=ln(c/o); rng=h-l; TR_i=max(h-l,|h-c_prev|,|l-c_prev|); ATR14_i = mean(TR over bars i-14..i-1); RR=rng/ATR14. CLV=(c-l)/rng (rng=0 bars never signal). up bar c>o, down bar c<o.
- Delta volume dv=2*tbv-v; DP=dv/v in [-1,1] (buy share minus sell share). CVD=running sum of dv from series start (FORMULAS.md section 14: "delta = 2*tbv - v"). DPz_i=(DP_i-mean(DP_{i-60..i-1}))/std(DP_{i-60..i-1}).
- RV (plain relative volume) = v_i / median(v_{i-20..i-1}).
- RVadj (TIME-ADJUSTED relative volume, the time-analysis core): 4h bars: v_i / median(v at the same 4h slot-of-day over the previous 20 days); 1d bars: v_i / median(v of the same weekday over the previous 8 weeks).
  Events use RVadj; the ablation "plain RV vs RVadj" is a registered contrast (section 6, C7).
- Wilder RSI(14) per FORMULAS.md section 1 (SMA seed over first 14 deltas); tests take expected values from the FORMULAS.md worked example, not from repo code.
- Bollinger: mid=SMA20(close), sd=population std of the same 20 closes, bands mid +/- 2 sd, BBW=(upper-lower)/mid. Squeeze at bar j: BBW_j <= 20th percentile of BBW over bars j-120..j-1.
- Donchian: DONUP_i: c_i > max(h_{i-20..i-1}); DONDN_i: c_i < min(l_{i-20..i-1}).
- New-extreme: NH_i: h_i > max(h_{i-20..i-1}); NL_i: l_i < min(l_{i-20..i-1}). Trend context UP: c_{i-1} > c_{i-11}; DOWN: c_{i-1} < c_{i-11}.
- Time keys: slot = 4h slot of day (0..5 = 00,04,...,20 UTC); weekday 0=Mon; weekend = Sat/Sun UTC; session group SG: A = slots 0,1 (00-08 UTC, Asia), B = slots 2,3 (08-16 UTC, Europe + US open), C = slots 4,5 (16-24 UTC, US afternoon/late).
  The US cash-open DST shift (13:30/14:30 UTC) is NOT modelled in the 4h slots; stated limit. Daily bars have weekday/weekend keys only.

## 4. Event families (36 events; definitions fixed; thresholds not tuned)
Every event is tested with BOTH signs (continuation = bar/breakout direction, reversal = opposite) as separate trials, because the literature names both.
For direction-free events (V3 ABS_*, NODEM/NOSUP) the "continuation" direction is the prior-trend / extreme direction.
- V1 volume spike [4]: SP2_UP, SP2_DN (RVadj>=2, bar up / down); SP3_UP, SP3_DN (RVadj>=3).
- V2 climax vs breakaway [4]: BCLX = RVadj>=2 & NH & CLV<=1/3 (dir +1; textbook reversal); SCLX = RVadj>=2 & NL & CLV>=2/3 (dir -1); BAWAY_UP = RVadj>=2 & NH & CLV>=2/3; BAWAY_DN = RVadj>=2 & NL & CLV<=1/3.
- V3 effort-vs-result [4]: ABS_LOW = RVadj>=2 & RR<=0.8 & context DOWN (dir -1); ABS_HIGH = same & context UP (dir +1); NODEM_HIGH = NH & RVadj<=0.8 (dir +1); NOSUP_LOW = NL & RVadj<=0.8 (dir -1).
- V4 taker delta / CVD / OBV [6]: DBUY = DPz>=2 & up bar; DSELL = DPz<=-2 & down bar; CVDDIV_BEAR = c_i>max(c_{i-20..i-1}) & CVD_i<max(CVD_{i-20..i-1}) (dir +1, textbook reversal); CVDDIV_BULL = mirror (dir -1);
  OBVDIV_BEAR / OBVDIV_BULL same with OBV = cumsum(sign(c-c_prev)*v).
- V5 consolidation + breakout + volume [10]: BBSQ_UP_V / BBSQ_UP_N: squeeze in any of bars i-5..i-1 & c_i > upper band computed at i-1 & RVadj>=1.5 / <1.5; BBSQ_DN_V / BBSQ_DN_N mirror (close below lower band);
  BBALL_UP, BBALL_DN: band breakouts without the squeeze condition (any RV); DON_UP_V / DON_UP_N / DON_DN_V / DON_DN_N: Donchian breakout with RVadj>=1.5 / <1.5.
- V6 pre-breakout dry-up [2]: DRY_UP = squeeze in i-5..i-1 & mean(RVadj over i-5..i-1)<=0.8 & c_i > upper band(i-1) & RVadj_i>=1.5; DRY_DN mirror.
- V7 RSI 40/60 x volume [6]: R60U_V / R60U_N: RSI_{i-1}<60<=RSI_i with RVadj>=1.5 / <1.5; R40D_V / R40D_N: RSI_{i-1}>40>=RSI_i (dir -1); R40RECL_V: RSI_{i-1}<40<=RSI_i & RVadj>=1.5; R60REJ_V: RSI_{i-1}>60>=RSI_i & RVadj>=1.5 (dir -1).
Horizons h (bars): 1d: {3,10,20}; 4h: {6,18,42} (1, 3 and 7 days). Trials = 36 events x 3 h x 2 signs = 216 per timeframe, 432 total.
INSUFFICIENT-N: n<30 (1d), n<100 (4h); still counted as trials.

## 5. Inference
Per timeframe: studentised single-step max-T White Reality-Check over the 216 trials (stats_lite.block_boot_family from the candle pilot, circular block bootstrap, 1000 resamples, seed 12345),
statistic = sign*(mean fwd return | event - mean fwd return | all bars) so BTC drift cancels. Block length 25 (1d) / 60 (4h) bars (>= max h). Secondary: two-sided BH q over the 216.
Net per trade with block-bootstrap 95 percent CI. Common bar range i in [0, n-2-hmax] for all h.
Minimum detectable effect (80 percent power, alpha .05 one-sided, analytic from sd(fwd) and n) is printed beside every result, so "no effect" reads as "no effect larger than MDE".
Pipeline calibration (V0b): the full RC family is re-run on 20 placebo series where the volume and tbv columns are circularly shifted by a random lag >= 500 bars (seeds 1..20).
Expected family-wise pass rate <= 0.10; if the observed placebo pass rate exceeds 0.20 the pipeline is declared miscalibrated and no V1 result is reported as evidence.

## 6. Registered contrasts (does volume add information?) - 8 trials, own BH family
C1 BBSQ_UP_V minus BBSQ_UP_N (sign*fwd at the median horizon: 1d h10, 4h h18). C2 BBSQ_DN_V minus _N (sign -1). C3 DON_UP_V minus DON_UP_N. C4 DON_DN_V minus DON_DN_N (sign -1).
C5 R60U_V minus R60U_N. C6 R40D_V minus R40D_N (sign -1). C7 time-adjustment value: SP3_* events defined with RVadj vs the same events defined with plain RV (compare mean signed excess return).
C8 weekend vs weekday SP3 events (TH2). Each contrast: difference of means with a circular block bootstrap 95 percent CI; "supported" only if the CI excludes 0 AND the BH q < 0.10 within the contrast family.

## 7. Time analysis (operator addition 2026-10-09)
T0 descriptive map (no pass/fail, never evidence): on 1h/4h/1d, per UTC hour / 4h slot / weekday / month: median volume share, median RVadj, mean DP, mean |ret|, corr(v, |ret|);
   share of plain-RV>=2 spikes landing in each slot versus the RVadj>=2 share (shows what the time adjustment removes).
T1 time-conditioned event study (inference; 3 pre-registered hypotheses, own BH family, h = median horizon):
   TH1 SP3_UP and SP3_DN continuation return differs between session groups C and A on 4h. TH2 SP3 events on weekends revert relative to weekdays (= C8). TH3 BBSQ_UP_V / BBSQ_DN_V continuation differs by session group B vs A on 4h.
T2 time-decay profile (descriptive): mean sign*fwd path at h = 1..42 bars after each event that passes DEV triage, to read the right hold time.
T3 exploratory stratification (labelled EXPLORATORY): for events that pass DEV triage only, mean excess return by session group, by weekend flag, and by regime (close above/below the 200-day SMA of daily closes).
   These cannot create a candidate; they can only be listed as hypotheses for a new registration.

## 8. Decision rule (triage only)
An event x horizon x sign "passes triage" only if: N >= minimum; mean NET per trade > 0 with block-bootstrap 95 percent CI lower bound > 0; RC adjusted p < 0.10 within the timeframe family; statistic > 0.
Passing triage means "worth VALIDATION on the frozen definition, once". It never means adopt. VALIDATION pass = same four conditions at n >= minimum on 2024-07..2025-06 AND the same sign; then and only then HOLDOUT once.
Adoption into MTS is a separate decision (BACKTEST_PROTOCOL section 6, PBO < 0.5, supervisor). A result that fails is reported as is. No definition, threshold, window or horizon is changed after seeing any output;
a change is a new registered hypothesis with its own trial rows.

## 9. Trial registry
Every run appends rows to TRIAL_REGISTRY.csv (run_id, date, family, event, tf, h, sign, window, n, mean_net_bps, p_adj, note). Trials for deflation = rows of the family. A result without its trial count is invalid.
Planned rows: V1 432, contrasts 8, time hypotheses 3 (TH2 = C8), placebo 20 runs x 2 tf (calibration, not edge trials).
