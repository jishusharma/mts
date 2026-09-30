# FABIO V3 SPEC - trade model as a layer module (location -> context -> trigger -> management)

Status: SPEC (DSA_BACKLOG.md:21, item B). Nothing here is a result. Input for the offline module
`MyTradingSys/backtest/layers/fabio/fabio_v3.py` (next backlog item, DSA_BACKLOG.md:22) and for spec-derived tests.
Fabio is a separate layer, never a Tom filter (PROJECT_VISION.md:94). The module imports only stdlib and
`orderflow_bars` (parse_fp, load_days); no import from execution/, layers/alerts/, Tom code or live code.
Sources: FABIO_TRADE_MODEL.md (S1-S8 :31-40, test plan :57-68), FABIO_BTC_RESEARCH_2026-09-30.md (models :27-32, audit
:34-60, item E :90-93), MISSING_PIECES_2026-09-30.md (new pieces :109-129, floor :312-313, H2 :356-365, H3 :375-398),
FABIO_RULEBOOK.md (testable core :131-147), BACKTEST_PROTOCOL.md (research/core_readiness_2026-09-27, :25-72).
Rule: every threshold not stated by Fabio is marked UNDEFINED-IN-SOURCE and is either a registered grid parameter or a
fixed design choice (FIXED) that is not tuned. FIXED values may not be changed after IS results are seen.

## 1. Data inputs
1m order-flow bars from `orderflow_bars.py` (columns :39-42, semantics :10-23), loaded with `load_days` (:176-190):
`t` (minute open, epoch ms UTC), `o,h,l,c`, `buy_vol, sell_vol, delta (= buy-sell)`, `cvd_day`, `cvd` (stitched),
`n_agg, n_trades, max_trade`, `b99_buy_vol, b99_sell_vol, b99_buy_n, b99_sell_n`, `b999_*` (same at thr999),
`thr99, thr999, thr_days`, `poc_price, poc_delta, poc_vol`, `fp` = footprint "binlow:buy:sell|..." in 10 USD bins
(`parse_fp`, :167-173). Derived: `v[i] = buy_vol[i] + sell_vol[i]`, `d[i] = delta[i]`.
- Big-trade thresholds are the causal prior-30-day 99th / 99.9th row-size percentiles (:19-23). Days with `thr_days == 0`
  use own-day thresholds (look-ahead) and are EXCLUDED (:22-23).
- Contiguity: a window [a, i] is valid only if `t[i] - t[a] == (i-a)*60000`. Invalid window -> signal returns None.
  A session window with > 5 missing minutes is excluded from evaluation (FIXED).
- Venue caveat: Binance USD-M aggTrades; "big print" = one aggTrades row, not one order (FABIO_BTC_RESEARCH:55-57).
- TICK = 0.1 USD (Binance BTCUSDT tick, as fabio_of_model.py:34). Parameter; Deribit tick not verified here.
- Profile bin `B_prof = 50 USD` (FIXED): fp bins re-binned as `k50 = floor(binlow/50)*50`. Reason: 10 USD bins (~0.01%)
  make LVN minima noise (FABIO_BTC_RESEARCH:52-54). Tests may pass any bin size.

## 2. Conventions
- Causality: every function f(bars, i, ...) reads bars[0..i] only; decisions are made at the close of bar i and act from
  bar i+1. Deleting bars > i must not change f (look-ahead canary, BACKTEST_PROTOCOL.md:35-37).
- `s` = direction: +1 long / buyers, -1 short / sellers.
- NY window (DST-aware, PROJECT_VISION.md:105; G11 in MISSING_PIECES:242): for a UTC date D that is Mon-Fri,
  `open(D) = 13:30 UTC` if US DST is in force on D, else `14:30 UTC`. US DST in force iff
  `second Sunday of March <= D < first Sunday of November` (date level is enough: windows are weekdays only).
  Window = 390 bars `[open, open+390 min)`; last bar = open+389 min. No new entries (first legs or adds) at or after
  open+330 min. Weekends: no window. US holidays: not excluded in v3 (open item 12.3).
- Other windows (stage 3 only, each a registered trial): London open 08:00 local (07:00 UTC in BST, 08:00 UTC otherwise;
  UK BST = last Sunday March .. last Sunday October), Asia 00:00 UTC. Same 390-bar length.
- TR and ATR: FORMULAS.md section 12 (plain SMA of TR, not Wilder). `ATR_N(i) = mean(TR[i-N+1..i])`, needs i >= N.
- z-score: `z(x_i; L) = (x_i - mean(x[i-L..i-1])) / pstdev(x[i-L..i-1])` (population sd, as FORMULAS.md section 10).
  pstdev == 0 -> None. Previous L bars only (the current bar is not in its own baseline).
- Profile P(window) = dict bin -> sum(buy+sell) over fp entries of the window's bars, re-binned to B_prof.
  POC = bin with max volume, ties -> lower bin; `poc_center = bin + B/2`.
- Value area (70%), algorithm reused from fabio_of_model.py:84-99 (not its module BIN constant): dense bin array v[0..n-1]
  from min to max bin; start a=z=POC index, acc = v[POC]; while acc < 0.70*total and bins remain: up = v[z+1]+v[z+2],
  dn = v[a-1]+v[a-2] (missing = 0); if no bins above, or (bins below and dn > up) take up to 2 bins below, else up to 2
  above (tie -> above). `VAL = lowbin(a)`, `VAH = lowbin(z) + B`.
- LVN of a profile (fabio_of_model.py:101-104): interior index i (1..n-2) with `v[i] < v[i-1] and v[i] <= v[i+1] and
  v[i] <= 0.5*med`, `med = sorted nonzero v [len//2]` (upper median). LVN price = bin + B/2.

## 3. Signals (pure functions)
### S1 balance(bars, i, N, k_bal) -> {H, L, R, poc} or None
Window W = [i-N+1, i]. `H = max h[W]`, `L = min l[W]`, `R = H - L`, `poc = poc_center(P(W))`.
Balance iff `R <= k_bal * sqrt(N) * ATR_N(i)` AND `|c[i] - poc| <= 0.25 * R` (0.25 FIXED).
Deviation from FABIO_TRADE_MODEL.md:33 ("range <= k x ATR"): a random walk's N-bar range grows ~sqrt(N) x 1-bar range, so
a fixed k would mean different things at N = 60/120/240; sqrt(N) makes k_bal comparable across N. k_bal UNDEFINED-IN-SOURCE.
### S2 pressure(bars, i, N, p, q=0.25) -> +1 / -1 / 0
Only where S1(i) is not None. `P = sum(d[W]) / sum(v[W])`; `drift = |c[i] - o[i-N+1]| / R`.
S2 = sign(P) if `|P| >= p` and `drift <= q`, else 0. +1 = accumulation, -1 = distribution (FABIO_TRADE_MODEL.md:10-13;
FR-10 FABIO_RULEBOOK.md:14). p UNDEFINED-IN-SOURCE (grid); q FIXED 0.25.
### S3 effort_result(bars, i, L=60, z_hi, r_abs=0.25, r_ctl=1.0) -> {control, absorbed}
`e = z(d_i; L)`, `res = z(r_i; L)` with `r = c - o`. For s in {+1,-1}:
- CONTROL = s if `s*e >= z_hi` and `s*res >= r_ctl` (effort with result, FABIO_TRADE_MODEL.md:14-16).
- ABSORBED = s if `s*e >= z_hi` and `s*res <= r_abs` (side s aggressed, no result or against; FR-16 "almost zero",
  FABIO_RULEBOOK.md:20). Absorbed side s implies bias -s.
Either z None -> {0,0}. At most one side can pass `s*e >= z_hi`. r_abs, r_ctl FIXED; L FIXED 60; z_hi grid.
### S4 big_push(bars, i, m, s) -> bool, with adaptive tier
`tier(i) = "999"` if `VR(i) >= 1.5` else `"99"` (1.5 FIXED). `VR(i)` = session volume so far (sum v from window open to i)
divided by the median over the prior 20 valid weekdays of their session volume over the same elapsed minutes; None
(fewer than 10 prior days) -> tier "99". Source: "Today there is a lot of volume. So I need to bigger filter"
(MISSING_PIECES:71, :116-117). `net(i; m) = sum over [i-m+1, i] of (bT_buy_vol - bT_sell_vol)` with T = tier(i).
S4 = `s * net(i; m) > 0`. m grid (model C) else FIXED 15.
### S5 breakout(bars, i, ...) -> +1 / -1 / 0
Uses S1 and S2 evaluated at i-1 (the balance before the bar). S5 = s if `S2(i-1) == s`, `s*(c[i] - E_s) > 0` with
`E_{+1} = H(i-1)`, `E_{-1} = L(i-1)`, and S4(i, m, s). Else 0 (FABIO_TRADE_MODEL.md:37).
### S6 control_level(bars, ctrl, a, i, s) -> price or None
`ctrl[j]` = S3 control at j. Last j in (a, i] with `ctrl[j] == s`; level = `l[j]` if s = +1, `h[j]` if s = -1
("last point of aggression", FABIO_TRADE_MODEL.md:20-23, 38). None if no such j.
### S7 curve(bars, i, sess_open) -> "premium" / "fair" / "discount"
Profile of the session so far [sess_open, i], value area as section 2. premium if `c[i] > VAH`, discount if
`c[i] < VAL`, else fair. Adds: no long add in premium, no short add in discount (FABIO_TRADE_MODEL.md:39, :18-19).
### S8 exhaustion(bars, i, trade) -> bool (trade side s, entry index e_i, last S6 level lvl)
Any of: (a) `i - e_i >= 15` and `s * net(i; 15) <= 0` (big trades stopped pushing, FR-15 FABIO_RULEBOOK.md:19);
(b) redistribution: S1(i, N=60, k_bal) not None and `i - 59 > e_i` (a new balance formed after entry);
(c) reversal: S3(i).control == -s and `s*(c[i] - lvl) < 0` (opposite control breaks the last S6 level, FR-30 :34).
Exit taker at o[i+1]. The 15 and N=60 are FIXED.

## 4. Models (state machines, one per model, run independently per window)
Common: at most one open trade per model; first-leg entries only while the day rules (section 6) allow.
Stop distance `D = max(f * entry, structural)`; skip the setup if `D > Dmax * entry` (Dmax FIXED 1.0%, top of the H1
grid MISSING_PIECES:264). f is the stop floor (grid 0.3% / 0.5%, MISSING_PIECES:312-313).
Entry mode (grid): `rest` = maker limit armed before the touch (section 5); `confirm` = taker at o[j+1] after the first
bar j (while armed, price at or through the limit) with S3(j).control == s.

### Model A - LVN pullback trend (FABIO_BTC_RESEARCH:28-29; FR-20 :24, FR-95/96 :99-100)
States IDLE -> IMPULSE -> ARMED -> IN_TRADE -> DONE.
- IDLE -> IMPULSE at bar i_b with S5(i_b) = s and day gate open (section 6). O = E_s of the balance (H for long).
- IMPULSE/ARMED, each bar i: X = extreme of the leg (max h[i_b..i] for long, min l for short); leg profile = P([i_b, i]);
  candidates = LVNs with `s*(X - lvn) >= 0.25 * s*(X - O)` (retrace >= 25%, FIXED) and `s*(c[i] - lvn) > 0`;
  LVN* = the candidate nearest to X. ARMED (limit at LVN*, re-priced each close) if LVN* exists, else IMPULSE.
- Cancel -> IDLE: `s*(c[i] - O) < 0` (leg failed back into balance), S8(c) reversal, or bar >= open+330.
- Structural stop = `s*(entry - O) + TICK` (1 tick beyond the breakout edge). Fill -> IN_TRADE (section 5).

### Model B - failed-breakout reclaim, mean reversion (FABIO_BTC_RESEARCH:30; FR-19 :23, FR-86 :90)
States IDLE -> PROBE -> RECLAIM -> IN_TRADE -> DONE.
- IDLE: balance B = S1(i-1) known. PROBE at bar i with `s_b*(c[i] - E_{s_b}) > 0` (close outside the balance, side s_b).
  Track Xp = probe extreme. Record `absorbed = any S3(j).absorbed == s_b` for j in the probe.
- PROBE -> RECLAIM at the first bar j <= i+5 (5 FIXED) with `s_b*(c[j] - E_{s_b}) < 0` and absorbed true.
  No reclaim in 5 bars -> IDLE. Trade side s = -s_b.
- rest: limit at c[j] (posted at j close, valid 3 bars, FIXED); confirm: taker at o[j+1].
- Structural stop = `|Xp - entry| + TICK`. Target = opposite balance edge E_{s} (maker limit, fill-through, FR-44 :48).
No day gate (it is the compression-day model).

### Model C - IVB, first 30 minutes (MISSING_PIECES:105-106, :127-128; FR-81 FABIO_RULEBOOK.md:85)
- IB = bars [open, open+30). `IBH = max h`, `IBL = min l`, `mid = (IBH+IBL)/2`.
- At the first bar i >= open+30 with `s*(c[i] - IB_s) > 0` (IB_{+1} = IBH, IB_{-1} = IBL) and S4(i, m, s) and day gate
  open: rest = limit at IB_s armed at i close (price is beyond it, pre-touch); confirm = taker at o[i+1].
- Structural stop = `s*(entry - mid) + TICK`. One IVB trade per day; later breakouts are ignored.
Portability flag: IVB rests on equity upside skew and may not port (MISSING_PIECES:128).

## 5. Fill rules, management, costs
### 5.1 Fills (BACKTEST_PROTOCOL.md:50-51 stress rule; fixes audit item FABIO_BTC_RESEARCH:43-46)
- A resting limit at P placed at the close of bar i is live from bar i+1. Buy fills in bar j iff `l[j] <= P - TICK`;
  sell fills iff `h[j] >= P + TICK` (compare with 1e-9 tolerance). Fill price = P (no improvement).
- Fill bar: only the stop is checked (if `l[j] <= stop` for long -> -1R "stop_fill_bar"); BE, trail, adds and S8 start
  at bar j+1 (intrabar order unknown).
- Missed winner: an armed order that never fills while price later reaches `P + s*2D` before the window ends. Report
  fill rate = fills / arms and missed winners / arms.
### 5.2 Management (FABIO_TRADE_MODEL.md:17-26, :61-65; MISSING_PIECES:118-120)
Order at each close i, in trade: (1) stop check happened intrabar; (2) BE; (3) trail; (4) S8; (5) add.
- Stop hit in bar i (long: `l[i] <= stop`): exit at stop, or at o[i] if `o[i] < stop` (gap, worse). Stop-first when a
  target is also touched (BACKTEST_PROTOCOL.md:45-47); also report target-first.
- BE: when `s*(ext - e1) >= be_k * D` (ext = best price since the bar after fill, inclusive of i), stop -> e1 (only if
  that tightens). be_k FIXED 1.0 (sensitivity 2.0 registered, section 7).
- Trail (only after BE): `cand = S6 - s*TICK` (a = fill bar). stop -> cand iff `s*(cand - stop) > 0` and
  `s*(c[i] - cand) > 0`. No bar or ATR trailing.
- Add (adds only after risk is zero, funded by locked profit; FR-05 FABIO_RULEBOOK.md:9, FR-03 :7): allowed iff stop is
  at or beyond BE, fewer than 3 adds so far (FABIO_TRADE_MODEL.md:64), bar i < open+330, S3(i).control == s, S4(i,15,s),
  and S7 not premium (long) / not discount (short). Add is taker at `pa = o[i+1]`.
  `locked = sum_k q_k * s*(stop - e_k)`; `dist = s*(pa - stop)`; `q_add = min(q1, locked / dist)`; skip if
  `q_add < 0.25*q1` (FIXED). Hence the P&L at the common stop after the add is >= 0. Adverse-add ladders are REJECTED
  (MISSING_PIECES:356-365).
- Exit: stop, S8 (taker at next open), model B target (maker), window end (taker at c of the last window bar).
### 5.3 Costs (operator 2026-09-30: sim.py wins, B080; system/sessions/MTS-2026-09-30-1005Z-CLD-ANA-connected-system.md:35)
- `FEE_MAKER = 0.0`, `FEE_TAKER = 0.0005` (sim.py:17-21, :111-112). fabio_of_model.py:43-44 constants are display-only;
  do not import them.
- R unit = `q1 * D1` (first-leg size x first-leg stop distance). Leg k gross R = `q_k * s*(x_k - e_k) / (q1*D1)`.
  Leg k fee R = `(fee_in_k + fee_out_k) * e_k * q_k / (q1*D1)` (sim.py:77-78 convention: fees on the entry notional).
  Linear approximation; USD for the inverse contract per FORMULAS.md 11.6 is reported separately, not used for R.
- Slippage stress 0 / 2 / 5 bps per taker leg: `slip * e_k * q_k / (q1*D1)` (BACKTEST_PROTOCOL.md:41-42).
- Funding: FORMULAS.md section 13 convention on entry notional for every Binance 8h record in (t_in, t_out] (NY windows
  contain 16:00 UTC). Reported as its own line; stress 2x (BACKTEST_PROTOCOL.md:48-49).

## 6. Day rules and gates
- Unit of evaluation is the day (MISSING_PIECES:109-111). Day net R = sum of net R of trades entered that day; a
  valid window day with no trade counts as 0.
- Daily stop: no new first legs after the day's closed net R <= -3R (FIXED; FR-04 FABIO_RULEBOOK.md:8, value
  UNDEFINED-IN-SOURCE). Stop after recovery: if the day's closed net R reached <= -1R and a later close brings it >= 0,
  no new first legs (MISSING_PIECES:121-126; FR-90 is probably inverted, :123-126). Max 10 first legs/day (FR-06 :10).
- Day gate (trend models A, C only; FR-91 :95, FABIO_TRADE_MODEL.md:26-28): at bar i >= open+60,
  `G(i) = (max h - min l over [open, i]) / median over prior 20 valid weekdays of the same elapsed range`;
  gate open iff `G(i) >= g`. g grid {off, 0.8}. Before open+60 the gate is closed when g != off.
  Dealer gamma is NOT in v3 (options history on F: unknown, MISSING_PIECES:113-115).
- Ex-post day type (reporting only, never an input): trend day iff `|c_last - o_first| / (Hwin - Lwin) >= 0.6` (FIXED)
  over the window, else balance day.

## 7. Parameters, grid, trial count
FIXED (not tuned): q 0.25, S1 poc band 0.25, L 60, r_abs 0.25, r_ctl 1.0, VR tier 1.5, S8 15 bars / N 60, retrace 25%,
reclaim 5 bars, rest validity (B) 3 bars, Dmax 1.0%, be_k 1.0, max adds 3, min add 0.25 q1, daily stop -3R, trend-day 0.6,
B_prof 50 USD, TICK 0.1.
| model | grid (values) | cells |
|---|---|---|
| Event study (stage 1) | N {60,120,240} x p {0.05,0.10}; k_bal 0.8 | 6 |
| A LVN pullback | N {60,120,240} x p {0.05,0.10} x f {0.3%,0.5%} x entry {rest,confirm} x g {off,0.8}; k_bal 0.8, z_hi 2.5 | 48 |
| B failed breakout | N {60,120,240} x z_hi {2.0,3.0} x f {0.3%,0.5%} x entry {rest,confirm}; k_bal 0.8 | 24 |
| C IVB | m {5,15} x f {0.3%,0.5%} x entry {rest,confirm} x g {off,0.8} | 16 |
| BE sensitivity | be_k 2.0 on each model's IS-chosen variant | 3 |
| NY total registered | | 97 |
| Stage 3 (only if NY passes) | London, Asia x chosen variant per model | +6 = 103 |
Stress runs (stop-first/target-first, slip 0/2/5, funding 2x) are reported on the chosen variant, not selected over,
and are not trials. Register all rows in TRIAL_REGISTRY.csv before any run (file does not exist in the repo yet;
FABIO_BTC_RESEARCH:95 requires it). p, k_bal, z_hi, f, g values are UNDEFINED-IN-SOURCE starting points.

## 8. Evaluation
Order (H3 narrow window first, MISSING_PIECES:375-398): stage 0 data QA -> stage 1 event study -> stage 2 NY model sim ->
stage 3 other windows -> holdout once.
- Stage 1 (FABIO_TRADE_MODEL.md:59-60; FABIO_BTC_RESEARCH:88-89): events = first bar of each S1+S2 run inside NY windows
  and the 60 min before open; outcome = `S2 * (c[i+h]/c[i] - 1)` for h = 120, 240 min. Placebo = S1 bars with S2 = 0.
  Continue only if, on IS days, mean signed return > placebo mean and its bootstrap 95% CI lower bound > 0 for at least
  one cell. Else STOP: the model is not portable (FABIO_TRADE_MODEL.md:60).
- Stage 2 metrics per model: per day - mean, SD, share > 0, worst day, max DD (R, days), days to recover; per trade -
  n, win %, avg gross/net R, fee drag R, PF, share of total R from the top 10% of trades, BE share, fill rate, missed
  winners; split trend vs balance days (section 6) and by regime tag.
- Splits: data 2024-12-02 onward (676 day files, FABIO_BTC_RESEARCH:60). Chronological IS 2024-12-02..2025-12-31,
  OOS 2026-01-01..2026-06-25, holdout 2026-06-26..2026-09-26 run once after freeze (BACKTEST_PROTOCOL.md:25).
  By regime (BACKTEST_PROTOCOL.md:27-29; thresholds UNDEFINED there, FIXED here): tag per day from the prior 30 daily
  closes, `r30 = c[D-1]/c[D-31] - 1`: up if > +10%, down if < -10%, else range; vol tercile from 30d realised vol with
  cutoffs frozen on IS. Leave-one-regime-out: for each trend tag, choose the variant on the other two tags' non-holdout
  days, evaluate on that tag. Pass needs same sign in >= 2 of 3 tags and no tag with CI upper bound < 0.
- Selection: per model, the IS-best variant by mean day net R at 2 bps. PBO by CSCV on the IS T x N matrix of daily
  net R (rows days, columns that model's variants), S = 16 (BACKTEST_PROTOCOL.md:57-58; FORMULAS.md section 10;
  reuse run_backtest.pbo_from_columns :107-119 with S=16). PBO > 0.2 -> not trusted. DSR >= 0.95 with N = registered
  trials (97 or 103).
- Null (BACKTEST_PROTOCOL.md:61-63): same model and management, first-leg entry moved to a random bar of the same window
  with the same side and D; 1000 permutations; p < 0.05.
- Sample size: to detect a mean of delta = 0.2R at two-sided alpha 0.05 and power 0.8,
  `n = ((1.96 + 0.8416) * SD / delta)^2`. SD = 1.5 -> 442 trades; SD = 1.82 -> 650 (the "~650" of
  FABIO_BTC_RESEARCH:37). Use the measured IS SD (runner payoffs are right-skewed, SD likely > 1.5) and the same formula
  on day R with day SD. OOS n below it -> verdict "insufficient N", never "no edge". 95% CI half-width at n = 30,
  SD 1.5 = 1.96*1.5/sqrt(30) = 0.537R (FABIO_BTC_RESEARCH:36-37 "about +/-0.55R").
- Pass (all; BACKTEST_PROTOCOL.md:66-72): OOS mean day net R > 0 with bootstrap CI lower > 0; PBO <= 0.2; DSR >= 0.95;
  null p < 0.05; survives 5 bps slip, stop-first and 2x funding; n requirement met; regime rule met; holdout same sign.
  Then it may go to testnet as its own layer (jishu_3 slot, FABIO_TRADE_MODEL.md:69) via a separate supervisor task.

## 9. Reuse map of existing code (per audit FABIO_BTC_RESEARCH:34-60)
| existing | verdict |
|---|---|
| orderflow_bars.py COLUMNS/load_days/parse_fp (:39-42, :167-190) | REUSE as the only data API |
| fabio_of_model.profile_levels VA + LVN logic (:74-108) | REUSE the algorithm with bin as a parameter (module BIN=10 is fixed at :36) |
| fabio_of_model.build_profile "true" flow (:50-58) | REUSE, add re-binning to B_prof |
| fabio_of_model.simulate_trade (:267-329) | DO NOT REUSE: 3R/HVN target cap, 1R trail, no adds, no S8 (audit item 4) |
| fabio_of_model FEE_* (:43-44), SESSIONS fixed 13:30 UTC (:45) | DO NOT REUSE (B080; no DST) |
| fade/break events, limit placed after trigger (:179-263) | DO NOT REUSE (AND-chain, adverse fills, audit items 3, 5) |
| run_backtest.pbo_from_columns (:107-119), trade_stats (:347-364) | REUSE (PBO S=16) |
| fabio_cvd_absorption / fabio_escalation / fabio_volume_fvg | DO NOT REUSE: kline tbv proxies; true flow exists |
| prior-30d thresholds, stop-first, IS-frozen choice | KEEP (audit item 8) |

## 10. TEST PLAN (hand-derived; EXPECT values from the definitions above, never from repo code)
Tests go in `backtest/layers/fabio/test_fabio_v3.py`. Each must fail on the pre-change code (module absent) at least once.
Unless given, volumes and big volumes are 0. State-machine tests (T35-T40) inject S3/S4 flags and levels as stated.
**Fixture F1** (bin 1.0, TICK 0.1):
| i | o | h | l | c | buy | sell | fp |
|---|---|---|---|---|---|---|---|
| 0 | 100 | 101 | 99 | 100 | 5 | 5 | 100:5:5 |
| 1 | 100 | 102 | 99 | 101 | 6 | 4 | 100:6:4 |
| 2 | 101 | 102 | 100 | 100 | 3 | 7 | 100:3:7 |
| 3 | 100 | 101 | 99 | 100 | 4 | 6 | 99:4:6 |
| 4 | 100 | 101 | 99 | 100.5 | 3 | 7 | 100:3:7 |
| 5 | 100 | 100.5 | 98 | 98.5 | 2 | 8 | 98:2:8; b99_sell_vol 3, b99_buy_vol 0 |

- T01 ATR: F1, N=4, i=4. TR1 = max(3,2,1) = 3; TR2 = TR3 = TR4 = 2. EXPECT: ATR_4(4) = 2.25.
- T02 ATR undefined: i=3, N=4. EXPECT: None.
- T03 S1 true: F1, i=4, N=4, k_bal 0.8. H 102, L 99, R 3; limit 0.8*2*2.25 = 3.6; profile {99:10, 100:30}, poc 100.5;
  |100.5-100.5| = 0 <= 0.75. EXPECT: {H:102, L:99, R:3, poc:100.5}.
- T04 S1 false: same, k_bal 0.6 (limit 2.7 < 3). EXPECT: None.
- T05 S1 poc band: same as T03 but c[4] = 99.7 (|99.7-100.5| = 0.8 > 0.75). EXPECT: None.
- T06 S2: F1, i=4, N=4, p 0.10. sum d = 2-4-2-4 = -8, sum v = 40, P = -0.2; drift |100.5-100|/3 = 0.1667 <= 0.25.
  EXPECT: -1.
- T07 S2 threshold: p 0.25. EXPECT: 0.
- T08 S2 drift: o[1] = 99.5 -> drift 1.0/3 = 0.333 > 0.25. EXPECT: 0 (S1 still true).
- T09 S4: F1, i=5, m=1, tier 99, s=-1: net = 0 - 3 = -3; -1*-3 > 0. EXPECT: True; s=+1 EXPECT: False.
- T10 S5: F1, i=5, N=4, k_bal 0.8, p 0.10, m 1. S2(4) = -1, c[5] = 98.5 < L 99, S4 true. EXPECT: -1.
- T11 S5 no close outside: c[5] = 99.2. EXPECT: 0. T12: b99 buy 3 / sell 0 in bar 5. EXPECT: 0.
- T13 adaptive tier: prior session volumes over the same elapsed minutes [150, 250, 200] (min prior days lowered to 3
  for the test), today 300 -> VR 1.5. EXPECT: "999". Today 290 -> 1.45. EXPECT: "99". Two prior days (below min).
  EXPECT: "99".
- T14 S3 absorbed: L=4, previous d = [1,-1,1,-1] (mean 0, pstdev 1), previous r = [0.5,-0.5,0.5,-0.5] (pstdev 0.5);
  bar d = 3, r = 0; z_hi 2.5. e = 3, res = 0. EXPECT: {control 0, absorbed +1}.
- T15 S3 control: same, r = 1.0 -> res 2.0 >= 1.0. EXPECT: {control +1, absorbed 0}.
- T16 S3 against: r = -0.5 -> res -1. EXPECT: {0, +1}. T17: d = -3, r = -1.0 -> e -3, res -2. EXPECT: {control -1, 0}.
- T18 S3 in between: d = 3, r = 0.25 -> res 0.5 (> 0.25, < 1.0). EXPECT: {0, 0}. T19: previous d all 1 (pstdev 0).
  EXPECT: {0, 0}.
- T20 S6: s = -1, a = 10, ctrl[11] = -1 (h 105), ctrl[13] = -1 (h 103), ctrl[12] = +1. EXPECT at i=14: 103; at i=12:
  105; at i=10: None. Mirror s=+1 with ctrl[11]=+1 (l 95): EXPECT at i=14: 95.
- T21 S7 / value area (bin 10): profile {100:10, 110:20, 120:40, 130:15, 140:5, 150:10}, total 100, target 70.
  POC 120 (acc 40); up = 15+5 = 20, dn = 20+10 = 30 -> take 110, 100 -> acc 70. EXPECT: VAL 100, VAH 130,
  poc_center 125. c = 135 EXPECT premium; 99 discount; 115 fair; 130 fair (not > VAH).
- T22 VA tie goes up: {100:10, 110:30, 120:10}; total 50, target 35; POC 110 (acc 30); up = 10, dn = 10 -> take 120 ->
  acc 40. EXPECT: VAL 110, VAH 130.
- T23 LVN (bin 10): {100:30, 110:25, 120:5, 130:20, 140:4, 150:30, 160:10}; nonzero sorted [4,5,10,20,25,30,30], med 20,
  cut 10. 120: 5<25, 5<=20, 5<=10 yes; 140: 4<20, 4<=30 yes; 110: 25>10 no; 130: 20 not < 5; 150: 30 not < 4.
  EXPECT: [125, 145].
- T24 LVN* selection (model A): T23 profile, long, O = 100, X = 165, c = 160. 0.25*(165-100) = 16.25; 165-145 = 20 ok,
  165-125 = 40 ok; nearest to X. EXPECT: 145. With c = 140 (145 not below c): EXPECT: 125.
- T25 S8a: long, e_i = 0, i = 20, per-bar b99 net over bars 6..20 sums to -1. EXPECT: True. Sum 0. EXPECT: True.
  Sum +1. EXPECT: False. i = 14 (age 14 < 15), sum -1. EXPECT: False (and (b),(c) false).
- T26 S8c: long, lvl 101.0, S3 control -1 at i, c = 100.9. EXPECT: True; c = 101.0. EXPECT: False.
- T27 fill-through: sell limit 100.0, TICK 0.1: h 100.1 EXPECT fill at 100.0; h 100.05 EXPECT no fill; h 100.0 EXPECT
  no fill. Buy limit 104.0: l 103.9 EXPECT fill; l 103.95 EXPECT no fill.
- T28 limit live from next bar: limit armed at close of bar i; bar i itself trades through. EXPECT: no fill in bar i.
- T29 cost R: short, maker entry 100000, D = 300 (0.3%), stop exit taker. gross -1; fee R = 0.0005*100000/300 = 0.16667.
  EXPECT: net -1.16667. Taker entry: fee 0.33333, EXPECT net -1.33333 (matches MISSING_PIECES:280). Slip 2 bps per
  taker leg adds 0.06667 per leg.
- T30 target is maker: model B exit at target. EXPECT: fee_out 0.
- T31 BE: long maker entry e1 100, D 1, be_k 1, stop 99. Bar j+1 h 101, l 99.5 -> no stop, BE set at close. Bar j+2 l 99.9, o 100.5.
  EXPECT: exit 100.0, gross 0, reason "be", fee R = 0.0005*100/1 = 0.05, net -0.05.
- T32 add sizing: long e1 100, q1 1, D1 1. stop 102 -> locked 2, pa 104, dist 2. EXPECT q_add 1.0 (P&L at stop after
  add = 2 - 2 = 0). stop 101 -> locked 1, dist 3. EXPECT q_add 0.33333. stop 100.5 -> 0.5/3.5 = 0.142857 < 0.25.
  EXPECT: no add. stop 100 (BE) -> locked 0. EXPECT: no add.
- T33 add gates: T32 stop-102 case with S7 = premium. EXPECT: no add. Same with 3 adds done. EXPECT: no add. Same at
  bar open+330. EXPECT: no add.
- T34 trail: long, stop 100 after BE, control bar +1 with l 101.0, c 102. EXPECT stop 100.9. A later control bar l 100.5.
  EXPECT stop stays 100.9. Control bar l 102.0, c 101.95 (cand 101.9, c > cand). EXPECT 101.9. Same with c 101.85.
  EXPECT stays 100.9.
- T35 model A end to end (Dmax 5% and f 0.3% for this test; injected O 100, LVN* 104, armed at close k with c[k] 106):
  bar k+1 l 103.95 -> no fill. bar k+2 l 103.9 -> fill 104.0; D = max(0.312, 4.1) = 4.1, stop 99.9. bar k+3 h 108.2,
  l 104.5, c 108, ctrl +1 -> fav 4.2 >= 4.1: BE stop 104.0, then trail cand 104.4 -> stop 104.4.
  bar k+4 o 107, l 104.3. EXPECT: exit 104.4, gross 0.4/4.1 = 0.097561, fee R 0.0005*104/4.1 = 0.012683,
  net 0.084878, reason "trail". Variant bar k+4 o 104.0 (gap below stop). EXPECT: exit 104.0, gross 0.
- T36 model A skip: same with Dmax 1.0% (4.1 > 1.04). EXPECT: no order armed.
- T37 model B end to end (Dmax 5%): balance H 102, L 99 at i-1. Bar 5 c 102.5, h 103.0, S3 absorbed +1 -> PROBE,
  Xp 103.0. Bar 6 c 101.5 -> RECLAIM, side short, rest sell 101.5. Bar 7 h 101.7 (>= 101.6) -> fill 101.5;
  D = max(0.3045, 1.5 + 0.1) = 1.6, stop 103.1, target 99. Bar 8 h 101.8, l 100.0 (fav 1.5 < 1.6, no BE). Bar 9 h 100.5,
  l 98.8 (<= 98.9). EXPECT: exit 99.0 target, gross 2.5/1.6 = 1.5625, fees 0, net 1.5625.
- T38 model B without absorption in the probe. EXPECT: no trade. Reclaim at bar 5+6. EXPECT: no trade.
- T39 model C (IB length 3 for the test, Dmax 5%): IB h max 105, l min 100 -> mid 102.5. Bar 3 c 105.5, S4 +1 -> buy
  limit 105. Bar 4 l 104.9 -> fill 105; D = max(0.315, 2.5 + 0.1) = 2.6. EXPECT: stop 102.4. A second breakout later in
  the day. EXPECT: not armed (one per day).
- T40 missed winner: buy limit 105 never filled (lows >= 104.95), D 2.6, a later high 110.2 (= 105 + 5.2). EXPECT:
  missed_winners 1, fill rate 0/1.
- T41 DST open: 2024-12-02 Mon EXPECT 14:30; 2025-03-07 Fri 14:30; 2025-03-10 Mon 13:30; 2025-10-31 Fri 13:30;
  2025-11-03 Mon 14:30; 2026-03-09 Mon 13:30; 2026-10-30 Fri 13:30; 2026-11-02 Mon 14:30; 2025-03-08 Sat EXPECT no window.
- T42 entry cutoff: first-leg signal at open+330. EXPECT: no entry; at open+329 EXPECT allowed. Window end exit at c of
  bar open+389, taker.
- T43 day aggregation: day 1 trades net [-1.2, -1.2, +5.0] -> 2.6; day 2 no trade -> 0; day 3 [-1.2]. EXPECT: day R
  [2.6, 0, -1.2], mean 0.46667.
- T44 day rules: closed day R -1.2, -2.4, then -3.6. EXPECT: no new first leg after -3.6. Sequence -1.2 then +1.5
  (day +0.3 after being <= -1). EXPECT: no new first leg. Open trades keep being managed in both cases.
- T45 day gate: elapsed range 400, prior medians [500, 450, 600] -> median 500, G 0.8. EXPECT open (g 0.8); range 390 ->
  0.78 EXPECT closed; g off EXPECT open; i < open+60 with g 0.8 EXPECT closed.
- T46 ex-post day type: window o 100, c 108, h 110, l 99 -> 8/11 = 0.727. EXPECT trend. c 103 -> 0.273. EXPECT balance.
- T47 sample size: SD 1.5, delta 0.2 -> (1.96+0.8416)*7.5 = 21.012, squared 441.50. EXPECT ceil 442.
  SD 1.82 -> 649.97. EXPECT 650. CI half-width n 30, SD 1.5. EXPECT 0.53677.
- T48 thr_days: a day with thr_days 0. EXPECT: excluded from windows. A window with 6 missing minutes. EXPECT: excluded.
- T49 look-ahead canary: for 20 random i in a synthetic 2-day series, S1-S8 at i with bars > i deleted. EXPECT: identical.
- T50 isolation: grep of fabio_v3.py imports. EXPECT: no execution, layers.alerts, Tom/core or fabio_of_model FEE_* import.

## 11. Implementation notes
- Signals take parameters explicitly (no module constants in formulas) so tests can use N=4, L=4, bin 1.0.
- Output per run: trades.csv (model, variant, day, legs, R gross/net, reason, day type, regime), days.csv, a
  tables.md and results.json off C:; TRIAL_REGISTRY rows written before the run.
- Gate: `python scripts/dev/run_all_tests.py --quick` before any commit (CLAUDE.md gates).

## 12. Open items (operator)
1. Adds rule is stricter than jasv3L (he adds at stop-zero with some fresh risk, MISSING_PIECES:77-78). v3 funds adds
   only from locked profit. Alternative (fresh 0.5R per add) would be a new registered trial.
2. S7 blocks shorts adding in discount, while jasv3L adds "on the way down". Kept per FABIO_TRADE_MODEL.md:39.
3. US holidays are not excluded; add a holiday list if stage 1 shows NY-specific structure.
4. Dealer-gamma day type needs Deribit options history (availability unknown).
5. Deribit tick size and the Binance-vs-Deribit basis (BACKTEST_PROTOCOL.md:43-44) are not checked here.
