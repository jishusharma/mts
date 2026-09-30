# FABIO V3 SPEC - trade model as a layer module (location -> context -> trigger -> management)

Version: v3.1 (2026-09-30): folds in FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md 5.4 (M1-M8, M10) and the operator decisions on the
v3.0 open items. v3.0 = git HEAD before this edit. T01-T50 hold unless marked "v3.1"; new behaviour is T51-T64.
Status: SPEC (DSA_BACKLOG.md:21). Nothing here is a result. Input for `backtest/layers/fabio/fabio_v3*.py` and
`pending_test_fabio_v3.py`. Fabio is a separate layer, never a Tom filter (PROJECT_VISION.md:94). Imports: stdlib and
`orderflow_bars` only; nothing from execution/, layers/alerts/, Tom or live code.
Transcripts `raw_transcripts_canonical/<id>_raw.txt`: fZ = fZlNGWvd2Ko, ja = jasv3L-d8ZE, 0j = 0jM5Y31YJak (all text on line
4), 8C = 8CWKfoSJu3c, LQ = LQvv5xgy_ik. Docs: FABIO_TRADE_MODEL (FTM), FABIO_LINE_BY_LINE (LBL), MISSING_PIECES_2026-09-30
(MP), FABIO_BTC_RESEARCH_2026-09-30 (FBR), BACKTEST_PROTOCOL (BP).
Provenance (CLAUDE.md): every parameter is in table 7.1 with a Fabio quote (file:line) or a label: NS-grid (NO-SOURCE,
registered grid value), NS-fixed (NO-SOURCE, fixed, never tuned), SAFETY (exempt), SIM (venue/data/cost/protocol convention).

## 0. Changes v3.0 -> v3.1
1. mgmt "event" (grid default): the other side's absorbed push moves the stop to BE / ratchets it (E_opp, M1).
2. Own-side absorption lowers risk (stop to the last own control level), never an exit (E_own, M2).
3. S8(b) exits only on a new balance favouring the other side (M3; X02 changed). 4. Model D failed-auction breakout (S5D,
M4); model B variant "trail" without the fixed target (M5). 5. S8(d) climax + failed auction exit (event mode, M6).
6. Day R carried London -> NY; after the day has been in profit: floor 0, first-leg risk <= closed day profit (M7).
7. Event mode trails to S6 only after a close through the level the other side defended (S9, M8). 8. Data gap M10 (section 1).
Operator: adds before BE only as a registered variant (open risk <= closed day profit, floor 0); S7 default + variant off;
US holidays excluded; dealer gamma dropped (no data); Deribit tick and basis: verify on desktop. Provenance: max adds 3 -> 2.

## 1. Data inputs
1m order-flow bars from `orderflow_bars.py` (columns :39-42, semantics :10-23, `load_days` :176-190). Used: `t` (minute open,
epoch ms UTC), `o,h,l,c`, `buy_vol, sell_vol, delta`, `b99_buy_vol, b99_sell_vol`, `b999_*`, `thr_days`, `fp` = footprint
"binlow:buy:sell|..." in 10 USD bins (`parse_fp` :167-173). `v[i] = buy_vol[i] + sell_vol[i]`, `d[i] = delta[i]`.
- Big-trade thresholds are the causal prior-30-day 99th / 99.9th row-size percentiles (:19-23). Days with `thr_days == 0`
  use own-day thresholds (look-ahead) and are EXCLUDED (:22-23).
- Contiguity: window [a, i] valid only if `t[i] - t[a] == (i-a)*60000`, else the signal returns None. A session window with
  > 5 missing minutes is excluded.
- "Big print" = one Binance aggTrades row, not one order (FBR:55-57).
- TICK = 0.1 USD (Binance BTCUSDT). Deribit tick and the Binance-Deribit basis (BP:43-44): VERIFY ON DESKTOP BEFORE RUNS.
- Profile bin `B_prof = 50 USD`: fp bins re-binned as `k50 = floor(binlow/50)*50` (10 USD bins make LVNs noise, FBR:52-54).
  Tests may pass any bin size.
- DATA GAP (M10): big-trade volume per price bin (body vs wick, fZ:117-118) is not in the bars (b99/b999 are per bar).
  Needs a new orderflow_bars column; not used in v3.1. Passive liquidity ("buyers wall", fZ:98) needs L2: not available.

## 2. Conventions
- Causality: every function f(bars, i, ...) reads bars[0..i] only; decisions at the close of bar i act from bar i+1.
  Deleting bars > i must not change f (look-ahead canary, BP:35-37).
- `s` = direction: +1 long / buyers, -1 short / sellers. `max_s(x, y)` = max for s = +1, min for s = -1.
- NY window (DST-aware, PROJECT_VISION.md:105): for a UTC date D, Mon-Fri and not in US_CLOSED, `open(D) = 13:30 UTC` if
  US DST is in force on D, else `14:30 UTC`. US DST iff `second Sunday of March <= D < first Sunday of November`.
  Window = 390 bars `[open, open+390 min)`. No new entries (first legs or adds) at or after open+330.
- US_CLOSED (v3.1, operator decision; NYSE full closures and 13:00 ET early closes, dates to VERIFY on desktop against the
  NYSE calendar): 2024-12-24, 2024-12-25; 2025-01-01, 01-09, 01-20, 02-17, 04-18, 05-26, 06-19, 07-03, 07-04, 09-01, 11-27,
  11-28, 12-24, 12-25; 2026-01-01, 01-19, 02-16, 04-03, 05-25, 06-19, 07-03, 09-07, 11-26, 11-27, 12-24, 12-25.
  `ny_open_utc(D)` returns None on these dates.
- London window (stage 3): open 07:00 UTC if UK BST (last Sunday March <= D < last Sunday October) else 08:00 UTC, Mon-Fri,
  390 bars (ends at the NY open). UK holidays not excluded. Asia: 00:00 UTC, 390 bars.
- TR and ATR: FORMULAS.md section 12 (plain SMA of TR). `ATR_N(i) = mean(TR[i-N+1..i])`, needs i >= N.
- z-score: `z(x_i; L) = (x_i - mean(x[i-L..i-1])) / pstdev(x[i-L..i-1])` (population sd). pstdev == 0 -> None.
- Profile P(window) = dict bin -> sum(buy+sell) over fp entries of the window's bars, re-binned to the bin size.
  POC = bin with max volume, ties -> lower bin; `poc_center = bin + B/2`.
- Value area (70%), algorithm of fabio_of_model.py:84-99 with bin as a parameter: dense v[0..n-1] from min to max bin; a=z=POC
  index, acc = v[POC]; while acc < 0.70*total and bins remain: up = v[z+1]+v[z+2], dn = v[a-1]+v[a-2] (missing = 0); if no bins
  above, or (bins below and dn > up) take up to 2 bins below, else up to 2 above (tie -> above). `VAL = lowbin(a)`,
  `VAH = lowbin(z) + B`.
- LVN (fabio_of_model.py:101-104): interior i with `v[i] < v[i-1] and v[i] <= v[i+1] and v[i] <= 0.5*med`, med = upper median
  of nonzero v. LVN price = bin + B/2.

## 3. Signals (pure functions)
### S1 balance(bars, i, N, k_bal) -> {H, L, R, poc} or None
W = [i-N+1, i]. `H = max h[W]`, `L = min l[W]`, `R = H - L`, `poc = poc_center(P(W))`.
Balance iff `R <= k_bal * sqrt(N) * ATR_N(i)` AND `|c[i] - poc| <= 0.25 * R`. sqrt(N) keeps k_bal comparable across N.
### S2 pressure(bars, i, N, p, q=0.25) -> +1 / -1 / 0
Only where S1(i) is not None. `P = sum(d[W]) / sum(v[W])`; `drift = |c[i] - o[i-N+1]| / R`.
S2 = sign(P) if `|P| >= p` and `drift <= q`, else 0. +1 = accumulation, -1 = distribution (FTM:10-13).
### S3 effort_result(bars, i, L=60, z_hi, r_abs=0.25, r_ctl=1.0) -> {control, absorbed}
`e = z(d_i; L)`, `res = z(r_i; L)` with `r = c - o`. For s in {+1,-1}: CONTROL = s if `s*e >= z_hi` and `s*res >= r_ctl`;
ABSORBED = s if `s*e >= z_hi` and `s*res <= r_abs` (side s aggressed, no result or against; bias -s). Either z None -> {0,0}.
Arrays: `ctrl[j]`, `absb[j]` = S3(j).control / .absorbed (tests inject them).
In-trade events (v3.1): `E_opp(i)`: absb[i] == -s (the other side's push absorbed). `E_own(i)`: absb[i] == s (own side failed).
### S4 big_push(bars, i, m, s) -> bool, with adaptive tier
`tier(i) = "999"` if `VR(i) >= 1.5` else `"99"`. VR(i) = session volume so far / median of the prior 20 valid weekdays'
volume over the same elapsed minutes; fewer than 10 prior days -> "99". `net(i; m) = sum over [i-m+1, i] of
(bT_buy_vol - bT_sell_vol)`, T = tier. S4 = `s * net(i; m) > 0`.
### S5 breakout(bars, i, ...) -> +1 / -1 / 0 (break WITH the pressure)
S5 = s if `S2(i-1) == s`, `s*(c[i] - E_s) > 0` with `E_{+1} = H(i-1)`, `E_{-1} = L(i-1)`, and S4(i, m, s). Else 0.
### S5D failed_auction(bars, i, N, k_bal, p, m, absb) -> {s, lvl, edge} or None (v3.1, break AGAINST absorbed pressure)
Balance B = S1(i-1) not None and `S2(i-1) == -s` (side -s pressed), some j in W(i-1) = [i-N, i-1] with `absb[j] == -s`
(the pressing side was absorbed), `s*(c[i] - E_s) > 0` (E as S5) and S4(i, m, s). Then `edge = E_s`, `lvl` = the absorption
level of the LAST such j: `l[j]` if s = +1, `h[j]` if s = -1. At most one s can pass (S2 has one sign). Else None.
### S6 control_level(bars, ctrl, a, i, s) -> price or None
Last j in (a, i] with `ctrl[j] == s`; `l[j]` if s = +1, `h[j]` if s = -1. None if no such j.
### S7 curve(bars, i, sess_open) -> "premium" / "fair" / "discount"
Session profile [sess_open, i], value area as section 2. premium if `c[i] > VAH`, discount if `c[i] < VAL`, else fair.
Add gate (default s7 on): no long add in premium, no short add in discount. Variant s7 off: no curve gate.
### S8 exhaustion(bars, i, trade, k_bal, tier, bin_size, z_hi=2.5, p=0.10, climax=False) -> bool
trade = {s, e_i (entry bar), lvl (last S6 level)}. S3 inside uses L 60 and z_hi. True if any of:
(a) `i - e_i >= 15` and `s * net(i; 15) <= 0` (big trades stopped pushing).
(b) v3.1: new balance favouring the other side: B' = S1(i, 60, k_bal) not None, `i - 59 > e_i`, and
    (`S2(i, 60, p) == -s` OR `n(s) > n(-s)`), n(x) = count of j in [i-59, i] with S3(j).absorbed == x (S3 None counts 0).
    A new balance where the other side was absorbed, or neutral, is a HOLD (fZ:97-106).
(c) `S3(i).control == -s` and `s*(c[i] - lvl) < 0` (opposite control breaks the last S6 level).
(d) v3.1, only if climax: bar x = i-1 made a new trade extreme (`s*(ext(x) - ext_prev) > 0`, ext = h for long / l for short,
    ext_prev = best ext over [e_i, x-1], needs x-1 >= e_i), with `s * net(x; 1) > 0` (burst), and `S3(i).absorbed == s`.
Too few bars for a clause -> that clause is False (never raises). Exit taker at o[i+1].
### S9 defended_level(bars, absb, a, i, s) -> price or None (v3.1)
Last j in (a, i] with `absb[j] == s` (our side absorbed there = the level the other side defends); `h[j]` if s = +1,
`l[j]` if s = -1. None if no such j.

## 4. Models (state machines, one per model, run independently per window)
Common: one open trade per model; first legs only while section 6 allows. `D = max(f * entry, structural)`; no arm if
`D > Dmax * entry` (Dmax 1.0%). Entry (grid): `rest` = maker limit armed before the touch (5.1); `confirm` = taker at the
next open as each model says. mgmt (5.2) and adds apply to every model.

### Model A - LVN pullback trend (FBR:28-29)
States IDLE -> IMPULSE -> ARMED -> IN_TRADE -> DONE.
- IDLE -> IMPULSE at bar i_b with S5(i_b) = s and day gate open (section 6). O = E_s of the balance (H for long).
- IMPULSE/ARMED, each bar i: X = leg extreme since i_b; leg profile = P([i_b, i]); candidates = LVNs with
  `s*(X - lvn) >= 0.25 * s*(X - O)` and `s*(c[i] - lvn) > 0`; LVN* = candidate nearest to X. ARMED (limit at LVN*,
  re-priced each close) if LVN* exists, else IMPULSE. confirm: taker at o[j+1] after the first armed bar j touching the
  limit with S3(j).control == s.
- Cancel -> IDLE: `s*(c[i] - O) < 0`, S8(c), or bar >= open+330. Structural stop = `s*(entry - O) + TICK`.

### Model B - failed-breakout reclaim, mean reversion (FR-19, FR-86)
- IDLE: balance B = S1(i-1). PROBE at bar i with `s_b*(c[i] - E_{s_b}) > 0`; Xp = probe extreme;
  `absorbed = any absb[j] == s_b` in the probe.
- PROBE -> RECLAIM at the first bar j <= i+5 with `s_b*(c[j] - E_{s_b}) < 0` and absorbed. Else IDLE. Side s = -s_b.
- rest: limit at c[j] (valid 3 bars); confirm: taker at o[j+1]. Structural stop = `|Xp - entry| + TICK`.
- target_mode "edge" (default): target = opposite balance edge E_s (maker, fill-through). target_mode "trail" (v3.1
  variant, M5): no target; managed by 5.2 + S8 like A. No day gate.

### Model C - IVB, first 30 minutes (LQ:841-843)
IB = bars [open, open+30). `IBH = max h`, `IBL = min l`, `mid = (IBH+IBL)/2`. At the first bar i >= open+30 with
`s*(c[i] - IB_s) > 0` (IB_{+1} = IBH) and S4(i, m, s) and day gate open: rest = limit at IB_s armed at i close;
confirm = taker at o[i+1]. Structural stop = `s*(entry - mid) + TICK`. One IVB trade per day. May not port (MP:128).

### Model D - failed-auction breakout (v3.1, M4; fZ:36-49)
- At bar k with S5D(k) = {s, lvl, edge} and day gate open (g off in the grid): rest = limit at `edge` armed at k close,
  valid bars k+1..k+3, cancelled if a close before the fill has `s*(c - lvl) < 0` (the level failed); confirm = taker at o[k+1].
- Structural stop = `s*(entry - lvl) + TICK` (behind the absorption level). No target; 5.2 + S8 like A.
- Function `model_d_trade(bars, k, s, edge, lvl, ...)` takes the S5D output as injected values (tests T58).

## 5. Fill rules, management, costs
### 5.1 Fills (BP:50-51; fixes FBR:43-46)
- A limit at P placed at the close of bar i is live from bar i+1. Buy fills in bar j iff `l[j] <= P - TICK`; sell fills iff
  `h[j] >= P + TICK` (1e-9 tolerance). Fill price = P.
- Fill bar j: only the stop is checked; all management and S8 start at bar j+1. A taker fill at o[j] makes j the fill bar.
- Missed winner: an armed order that never fills while price later reaches `P + s*2D` before the window ends.
### 5.2 Management
Order at each close i > fill bar: (1) stop check happened intrabar; (2) stop moves per mgmt; (3) S8; (4) add.
Every stop change is recorded in `moves` as (i, new_stop, kind). A stop exit's reason = kind of the last move ("stop" if
none); other exits: "s8", "target", "window_end".
- Stop hit in bar i (long `l[i] <= stop`): exit at stop, or at o[i] if beyond it (gap). Stop-first when a target is also
  touched (BP:45-47); also report target-first.
- mgmt "dist" (v3.0; registered variant): BE when `s*(ext - e1) >= be_k * D` (ext = best price from fill bar+1 to i):
  stop -> e1 if tighter (kind "be"). Trail only after BE: `trail_update`: cand = S6(fill bar, i) - s*TICK; stop -> cand iff
  `s*(cand - stop) > 0` and `s*(c[i] - cand) > 0` (kind "trail").
- mgmt "event" (v3.1 default; M1, M2, M8). No distance BE (be_k unused).
  (i) E_opp(i): a = last j in [fill+1, i-1] with ctrl[j] == s, else a = fill bar; pb = adverse extreme of (a, i] (min l for
  long, max h for short). `opp_stop(s, e1, stop, pb, c[i])`: candidates {e1, pb - s*TICK}; keep those with
  `s*(c[i] - x) > 0`; best = max_s of them; stop -> best iff `s*(best - stop) > 0` (kind "opp").
  (ii) E_own(i): stop -> trail_update(stop, S6(fill bar, i), c[i]) (kind "own"; no-op if S6 None); arm DL = S9 at i
  (h[i] long, l[i] short). Never an exit.
  (iii) DL armed at a bar < i and `s*(c[i] - DL) > 0`: stop -> trail_update(stop, S6(fill bar, i), c[i]) (kind "trail");
  DL cleared. No other S6 trail in event mode.
  (iv) S8 with clause (d) on (climax=True).
- Adds (FR-05, FR-03): allowed iff fewer than 2 adds so far (3 entries, P22), bar i < open+330, S3(i).control == s,
  S4(i,15,s), S7 gate (unless s7 off), and add_mode "be" (default): stop at or beyond e1. Taker at `pa = o[i+1]`.
  `locked = sum_k q_k * s*(stop - e_k)`; `dist = s*(pa - stop)`; `q_add = min(q1, (budget + locked) / dist)`; skip if
  `q_add < 0.25*q1`. add_mode "be": budget = 0, so P&L at the stop after the add is >= 0. add_mode "day" (registered
  variant, operator decision): no BE gate; `budget = max(0, closed day R) * U` (U = q1*D1/r1, section 6), so total open risk at
  the stop after the add <= closed day profit. Adverse-add ladders stay REJECTED (MP:356-365).
- Exit: stop, S8 (taker at next open), model B edge target (maker), window end (taker at c of the last window bar).
### 5.3 Costs (sim.py wins, B080)
- `FEE_MAKER = 0.0`, `FEE_TAKER = 0.0005` (sim.py:17-21, :111-112). fabio_of_model.py:43-44 FEE_* are not imported.
- R unit = `q1 * D1`. Leg gross R = `q_k * s*(x_k - e_k) / (q1*D1)`; fee R = `(fee_in + fee_out) * e_k * q_k / (q1*D1)`
  (fees on the entry notional, sim.py:77-78). Slippage stress 0 / 2 / 5 bps per taker leg: `slip * e_k * q_k / (q1*D1)`.
- Funding: FORMULAS.md section 13 on entry notional per 8h record in (t_in, t_out]; own line; stress 2x (BP:48-49).

## 6. Day rules and gates
- Unit = the day (UTC date). Day R = sum over its trades of `risk_u * net_r` (risk_u default 1); no trade -> 0.
  Stage 2 (NY only) starts every day at 0. Stage 3 "LN" runs London then NY on the same date: London's closed R is the
  NY `carry` (M7).
- Closed prefix sums `P = [0, carry, carry+n1, carry+n1+n2, ...]`, C = last, peak = max(P). `first_leg_allowed(closed_nets,
  n_first_legs=0, carry=0.0)` is False iff any of: n_first_legs >= 10; C <= -3 (SAFETY); some P_k <= -1 and a later
  P_m >= 0 (stop after recovery, MP:121-126); peak > 0 and C <= 0 (floor at 0, v3.1). Open trades keep being managed.
- `first_leg_risk(...)` (v3.1) = 0 if not allowed; else `min(1, C)` if peak > 0; else 1. Trades carry `risk_u` = this r1.
- Report only: worst-case day R per bar (closed + open trades at their stops).
- Day gate (A, C; FR-91): at bar i >= open+60, `G(i) = (max h - min l over [open, i]) / median over the prior 20 valid
  weekdays of the same elapsed range`; open iff `G(i) >= g`, g grid {off, 0.8}; closed before open+60 when g != off.
  Dealer-gamma day type: DROPPED (no options history; ja:163-164 stays unmodelled).
- Ex-post day type (reporting only): trend iff `|c_last - o_first| / (Hwin - Lwin) >= 0.6`, else balance.

## 7. Provenance, grid, trial count
### 7.1 Provenance (quotes verbatim; `[m:ss]` stamps dropped; "concept" = the idea is his, the number is not)
| id | parameter | value | label | source |
|---|---|---|---|---|
| P01 | S1 balance; N | {60,120,240} | NS-grid | concept 0j:4 "the market is balanced at this time" |
| P02 | k_bal; POC band | 0.8; 0.25 | NS-fixed | concept 0j:4 "there is the fair value on the middle" |
| P03 | S2 pressure p; drift q | {0.05,0.10}; 0.25 | NS-grid; NS-fixed | concept 0j:4 "the market is clearly building pressure down" |
| P04 | S3 L, z_hi, r_abs, r_ctl | 60, {2.0,2.5,3.0}, 0.25, 1.0 | NS-grid (z_hi) / NS-fixed | concept 0j:4 "the result of the price for a pressure in by delta was almost zero"; 8C:42-44 "the punch to the wall" |
| P05 | big trade = 99th/99.9th pct, prior 30 d | - | NS-fixed | concept 0j:4 "where the big players are pushing the price" |
| P06 | tier VR 1.5, 20 d, min 10 | - | NS-fixed | concept ja:25-26 "Today there is a lot of volume. So I need to bigger filter" |
| P07 | S4 window m | {5,15} (C), 15 | NS-grid / NS-fixed | concept 0j:4 "You see again big trades in the direction of the trend" |
| P08 | S5 trigger on the close | - | FABIO | 0j:4 "confirmation from price was exactly this candle" |
| P09 | S5D / model D trigger | - | FABIO | fZ:36-42 "capitalize on the failed auction of the seller and then aggression of the level of the buyers" |
| P10 | S6 anchor = last own control | - | FABIO | 8C:201-202 "the last point of aggression of the sellers" |
| P11 | S7 add gate; VA 70% | on; 0.70 | FABIO; NS-fixed | 8C:52-54 "to raise the exposure low in the curve" (not the best idea) |
| P12 | S7 off | variant | NS-grid | operator decision (ja:70-71 "We can scale other two contract here on the way down") |
| P13 | S8(a) 15 bars | 15 | NS-fixed | concept 0j:4 "the big trades are not pushing anymore the price down" |
| P14 | S8(b) rule; N 60 | 60 | FABIO; NS-fixed | 0j:4 "We are in a redistribution phase"; hold: fZ:98-99 "The sellers got completely absorbed here" |
| P15 | S8(c) | - | FABIO | 8C:207-208 "take back control, I want to be out of the market" |
| P16 | S8(d); 1-bar look-back | on (event) | FABIO; NS-fixed | fZ:144-146 "all these aggression and a failed auction and this is the reason I closed my trade" |
| P17 | E_opp stop to BE | event | FABIO | fZ:113-115 "stop loss to zero. Why? Because we already saw that the sellers got stopped again" |
| P18 | E_opp ratchet to pb | event | FABIO | fZ:132-134 "sellers took control but stopped on these big trades. So I can take other profit"; fZ:121-122 "Now I'm covered below this low" |
| P19 | E_own de-risk; by stop (not size) | event | FABIO; NS-fixed | fZ:67-68 "buyers failed again. So I want to lower my risk" |
| P20 | trail after defended break | event | FABIO | fZ:93-96 "sellers are trying to protect this level. So if we have another breakout, we can trail our stop" |
| P21 | mgmt dist, be_k | {1.0,2.0} | NS-grid | concept 0j:4 "the market exploded in my direction and I put my stop loss to break even" |
| P22 | max adds | 2 (3 entries) | FABIO | fZ:152-154 "we loaded the first one here, then we reloaded here, then we reloaded here"; 0j:4 "This was the third position." |
| P23 | add_mode be (default) | - | FABIO | 0j:4 "open a second one with the profit of the first one" |
| P24 | add_mode day | variant | FABIO, variant by operator | fZ:57-59 "I'm loading and scaling in position trying to get my losses smaller and smaller" |
| P25 | add cap q1; min add 0.25 q1 | - | NS-fixed | - |
| P26 | floor at day R 0 | - | FABIO | fZ:29-31 "maximum drawdown that is break even. So if we go back to break even, we stop the session" |
| P27 | carry; first-leg risk <= C | - | FABIO | fZ:15-17 "we came from a London session where we did pretty good amount of profit"; fZ:60-61 "I'm only risking the profit of the day" |
| P28 | stop after recovery; -1R | -; -1 | FABIO; NS-fixed | ja:181-182 "we locked in $12,000 and we are out of the position" |
| P29 | daily stop | -3R | SAFETY | value NO-SOURCE; fZ:79-81 "in the worst session that I can make, I lose around 5,000, 10,000" |
| P30 | max 10 first legs; Dmax 1.0% | - | SAFETY; NS-fixed | - |
| P31 | stop floor f | {0.3%,0.5%} | NS-grid | - (LESSONS E: Tom's floor was unsourced) |
| P32 | structural stop behind the level, +1 TICK | - | FABIO; NS-fixed | fZ:44-46 "if this level failed, this one become the new pivot" |
| P33 | NY cash-open window; 390; cutoff 330; window-end exit | - | FABIO; SIM; NS-fixed; NS-fixed | 8C:7-8 "I scalp the NASDAQ during the New York session" |
| P34 | US_CLOSED excluded; London/Asia windows | - | SIM (operator); NS-grid | - |
| P35 | model A LVN, retrace 25% | - | NS-fixed | not in these transcripts (FBR:28-29) |
| P36 | model B reclaim 5, rest 3 bars, edge target | - | NS-fixed | concept 8C:40-42 "the buyers getting completely absorbed" |
| P37 | model B trail variant | variant | FABIO | fZ:50-52 "amazing risk to reward trades to take the top of the day" |
| P38 | model C IB 30 min | 30 | FABIO | LQ:841-843 "the bottom of the first 30 minutes is giving a lot of value in the direction" |
| P39 | model D rest validity | 3 bars | NS-fixed | - |
| P40 | day gate g, 20 d, open+60 | {off,0.8} | NS-grid | concept 8C:85-87 "volatility is not there every day" |
| P41 | fees, slip, funding, fills, stop-first, TICK, B_prof, VA/LVN, ATR, day-type 0.6, regimes, stats | - | SIM | BP, FORMULAS.md, sim.py |

### 7.2 Grid (all rows in TRIAL_REGISTRY.csv before any run; the file does not exist yet, FBR:95)
Main grid runs mgmt event, add_mode be, s7 on, S8(d) on. k_bal 0.8, z_hi 2.5 unless listed.
| model | grid (values) | cells |
|---|---|---|
| Event study (stage 1) | N {60,120,240} x p {0.05,0.10} | 6 |
| A LVN pullback | N x p x f {0.3%,0.5%} x entry {rest,confirm} x g {off,0.8} | 48 |
| B failed breakout (edge target) | N x z_hi {2.0,3.0} x f x entry | 24 |
| C IVB | m {5,15} x f x entry x g | 16 |
| D failed auction (g off) | N x p x f x entry; m 15 | 24 |
| Variants on each model's IS-chosen cell (A,B,C,D) | dist be_k 1.0; dist be_k 2.0; S8(d) off; s7 off; add_mode day | 20 |
| B trail | target_mode trail on B's chosen cell | 1 |
| NY total registered (v3.0: 97) | | 139 |
| Stage 3 (only if NY passes) | London, Asia x chosen (A,B,C,D) = 8; LN carry x chosen = 4 | +12 = 151 (v3.0: 103) |
Stress runs (stop-first/target-first, slip 0/2/5, funding 2x) are reported on the chosen variant, not selected over.

## 8. Evaluation
Order (MP:375-398): stage 0 data QA -> 1 event study -> 2 NY model sim -> 3 other windows -> holdout once.
- Stage 1 (FTM:59-60): events = first bar of each S1+S2 run in NY windows and the 60 min before open; outcome
  `S2 * (c[i+h]/c[i] - 1)`, h 120, 240 min; placebo = S1 bars with S2 = 0. Continue only if on IS days some cell has mean >
  placebo and bootstrap 95% CI lower > 0; else STOP (not portable). Also report S5D events (AGAINST relation).
- Stage 2 per model: day mean, SD, share > 0, worst day, max DD, days to recover; trade n, win %, gross/net R, fee drag, PF,
  top-10% share, BE share, fill rate, missed winners, moves by kind; splits trend/balance day, regime, side, relation
  (WITH: A, C; AGAINST: B, D).
- Data 2024-12-02 onward (676 day files, FBR:60). IS 2024-12-02..2025-12-31, OOS 2026-01-01..2026-06-25, holdout
  2026-06-26..2026-09-26 once after freeze (BP:25). Regime per day: `r30 = c[D-1]/c[D-31] - 1`, up > +10%, down < -10%,
  else range; vol tercile of 30d realised vol, cutoffs frozen on IS. Leave-one-regime-out; pass needs the same sign in >= 2
  of 3 tags and no tag with CI upper < 0.
- Selection: IS-best variant per model by mean day net R at 2 bps. PBO (CSCV, S 16, run_backtest.pbo_from_columns
  :107-119) > 0.2 -> not trusted. DSR >= 0.95 with N = 139 (NY) or 151. Null (BP:61-63): first-leg entry at a random bar of
  the same window, same side and D, 1000 permutations, p < 0.05.
- Sample size `n = ((1.96 + 0.8416) * SD / delta)^2`, delta 0.2R: SD 1.5 -> 442, SD 1.82 -> 650; use the IS SD, also on
  day R; OOS n below it -> "insufficient N". CI half-width n 30, SD 1.5 = 0.537R.
- Pass (BP:66-72): OOS day net R > 0 with CI lower > 0; PBO <= 0.2; DSR >= 0.95; null p < 0.05; survives 5 bps, stop-first,
  2x funding; n met; regime rule; holdout same sign. Then testnet as its own layer (FTM:69) via a supervisor task.

## 9. Reuse map (FBR:34-60)
REUSE: orderflow_bars COLUMNS/load_days/parse_fp (:39-42, :167-190) as the only data API; fabio_of_model VA + LVN algorithm
(:74-108) with bin as a parameter; build_profile "true" flow (:50-58) plus re-binning; run_backtest.pbo_from_columns
(:107-119), trade_stats (:347-364); prior-30d thresholds, stop-first, IS-frozen choice.
DO NOT REUSE: fabio_of_model.simulate_trade (:267-329), FEE_* (:43-44), SESSIONS (:45), fade/break events (:179-263);
fabio_cvd_absorption / fabio_escalation / fabio_volume_fvg (kline proxies).

## 10. TEST PLAN (hand-derived; EXPECT values from the definitions above, never from repo code)
Tests: `pending_test_fabio_v3.py` (renamed test_fabio_v3.py when the module lands); each fails while the module is absent. Unset volumes and big volumes are 0. State-machine tests inject ctrl/absb/levels.
**Fixture F1** (bin 1.0, TICK 0.1), rows i: o/h/l/c buy sell fp: 0: 100/101/99/100 5 5 100:5:5; 1: 100/102/99/101 6 4
100:6:4; 2: 101/102/100/100 3 7 100:3:7; 3: 100/101/99/100 4 6 99:4:6; 4: 100/101/99/100.5 3 7 100:3:7; 5: 100/100.5/98/98.5
2 8 98:2:8 with b99_sell_vol 3, b99_buy_vol 0.
T01-T50 are unchanged from v3.0 (full derivations there and in the test comments); EXPECT values:
- T01 ATR_4(4) = 2.25 (TR 3,2,2,2). T02 i=3, N=4: None. T03 S1(4, N 4, k_bal 0.8) = {H 102, L 99, R 3, poc 100.5} (limit
  3.6, profile {99:10, 100:30}). T04 k_bal 0.6: None. T05 c[4] 99.7: None. T06 S2 p 0.10: -1 (P -0.2, drift 0.1667).
  T07 p 0.25: 0. T08 o[1] 99.5 (drift 0.333): 0. T09 S4(5, m 1): s -1 True, s +1 False. T10 S5(5): -1. T11 c[5] 99.2: 0.
  T12 b99 buy 3 / sell 0: 0. T13 tier: prior [150, 250, 200], 300 -> "999", 290 -> "99", 2 prior days -> "99".
- T14-T19 S3 (L 4, prev d [1,-1,1,-1], prev r [0.5,-0.5,0.5,-0.5], z_hi 2.5): d 3 r 0 {0,+1}; r 1.0 {+1,0}; r -0.5 {0,+1};
  d -3 r -1.0 {-1,0}; r 0.25 {0,0}; prev d all 1 {0,0}.
- T20 S6 (s -1, a 10; ctrl[11] -1 h 105, ctrl[12] +1, ctrl[13] -1 h 103): i 14 -> 103, i 12 -> 105, i 10 -> None; s +1 with
  ctrl[11] +1 (l 95): 95. T21 VA bin 10 {100:10,110:20,120:40,130:15,140:5,150:10}: VAL 100, VAH 130, poc_center 125;
  c 135 premium, 99 discount, 115 fair, 130 fair. T22 {100:10,110:30,120:10}: VAL 110, VAH 130 (tie goes up).
  T23 LVN {100:30,110:25,120:5,130:20,140:4,150:30,160:10}: [125, 145]. T24 LVN* (long, O 100, X 165): c 160 -> 145; c 140 -> 125.
- T25 S8a (long, window [i-14, i]): sum -1 True, 0 True, +1 False, age 14 False. T26 S8c (lvl 101, control -1): c 100.9
  True, c 101.0 False. T27 fill-through: sell 100: h 100.1 fill, 100.05 no, 100.0 no; buy 104: l 103.9 fill, 103.95 no.
  T28 no fill in the arming bar. T29 short maker 100000, D 300, taker stop: net -1.16667; taker entry -1.33333; slip 2 bps
  0.06667 per taker leg. T30 target maker: fee_out 0.
- T31 dist BE (long e1 100, D 1, stop 99; bars h 101 l 99.5, then l 99.9): exit 100.0 "be", fee 0.05, net -0.05.
  T32 add_size (e1 100, pa 104, budget 0): stop 102 -> 1.0; 101 -> 0.33333; 100.5 -> 0; 100 -> 0. T33 add gates: premium,
  3 adds, bar open+330, no control, no push, stop 99 each block; short: discount blocks, premium does not.
  T34 trail_update: 100.9; 100.9; 101.9; 100.9; level None unchanged.
- T35 model A dist (Dmax 5%, f 0.3%, O 100, LVN* 104): fill bar 2 at 104.0, D 4.1, stop0 99.9; bar 3 BE then trail 104.4;
  bar 4 exit 104.4 "trail", gross 0.097561, fee 0.012683, net 0.084878; gap o 104.0: exit 104.0, gross 0. T36 Dmax 1%: no arm.
- T37 model B edge: fill 101.5 bar 7, D 1.6, stop0 103.1, target 99; exit 99.0 "target", gross = net 1.5625, fee 0.
  T38 no absorption, or reclaim after 6 bars: no trade. T39 model C (IB 3 bars): fill 105 bar 4, D 2.6, stop 102.4 hit bar 6,
  gross -1; second breakout ignored; gate closed: no arm. T40 missed winner: high 110.2 -> (arms 1, fills 0, missed 1); 110.1 -> 0.
- T41 NY open: 2024-12-02 14:30; 2025-03-07 14:30; 2025-03-10 13:30; 2025-10-31 13:30; 2025-11-03 14:30; 2026-03-09 13:30;
  2026-10-30 13:30; 2026-11-02 14:30; Sat/Sun None. T42 entry at open+330 no, +329 yes; window end exit c, taker, net 0.35.
  T43 day R [2.6, 0, -1.2], mean 0.46667. T44 first legs: -1.2, -2.4 yes; -3.6, -3.0 no; [-1.2, +1.5] no; [-0.5, 0.6] yes;
  10 first legs no. T45 day gate (prior [500,450,600]): range 400 open; 390 closed; g off open; before open+60 closed.
  T46 day type 8/11 trend, 3/11 balance. T47 n 442, 650; CI 0.53677. T48 thr_days 0 excluded; 6 missing min excluded;
  5 missing kept. T49 look-ahead canary S1-S8. T50 import isolation.
- X02 (v3.1, changed): calm balance bars (buy 1, sell 0, b99 buy 1), long since e_i 10, i 80: S2 of the new balance = +1
  (favours the long). EXPECT False (v3.0: True).

**v3.1 tests** (bars "a/b/c/d" = o/h/l/c; long trades q1 1, e1 100, D 1, stop0 99, maker entry, fill bar 0, unless given):
- T51 opp_stop(s, e1, stop, pb, c): (+1,100,99,99.9,100.6) cands 100.0, 99.8 -> 100.0. (+1,100,100.4,100.8,101.3) -> 100.7.
  (+1,100,99,99.5,99.8): 100.0 not below c -> 99.4. (+1,100,100.7,100.5,101.0): 100.4 looser -> 100.7. (-1,100,101,100.3,
  99.5): cands 100.0, 100.4 -> min 100.0.
- T52 S9 on T53 bars: absb[3] = +1 (h 101.6), absb[4] = -1 (l 100.8). EXPECT (a 0, i 5, +1) 101.6; (0, 2, +1) None;
  (3, 5, +1) None (a exclusive); (0, 5, -1) 100.8.
- T53 event management end to end. Bars 0: 100.2/100.6/99.8/100.3; 1: 100.3/100.8/99.9/100.6; 2: 100.6/101.5/100.5/101.4;
  3: 101.4/101.6/101.0/101.1; 4: 101.1/101.5/100.8/101.3; 5: 101.3/102.0/101.2/101.9; 6: 101.9/102.1/101.0/101.5.
  ctrl[2] = ctrl[5] = +1; absb[1] = -1, absb[3] = +1, absb[4] = -1; end bar 6.
  Bar 1 E_opp: a 0, pb 99.9 -> 100.0 (dist: fav 0.8 < 1, no BE). Bar 2 control: no move. Bar 3 E_own: S6 l[2] 100.5 ->
  100.4, DL 101.6, no exit. Bar 4 E_opp: a 2, pb 100.8 -> 100.7. Bar 5 c 101.9 > DL: S6 l[5] 101.2 -> 101.1. Bar 6 l 101.0. EXPECT moves [(1,100.0,opp),(3,100.4,own),(4,100.7,opp),(5,101.1,trail)],
  exit_idx 6, reason "trail", gross 1.1, fee 0.05 (0.0005*100/1), net 1.05.
  Same bars, mgmt dist: bar 2 fav 1.5 >= 1 -> BE 100.0, trail 100.4; bar 5 trail 101.1. EXPECT moves [(2,100.0,be),
  (2,100.4,trail),(5,101.1,trail)], exit 101.1.
- T54 event, T53 bars and ctrl, absb all 0: EXPECT moves [], exit c[6] 101.5 "window_end", gross 1.5, net 1.45. Only
  absb[3] = +1, ctrl all 0 (S6 None: no de-risk, no trail at the DL break): EXPECT the same (own absorption never exits).
- T55 S8(b) v3.1, k_bal 0.8, p 0.10, bin 1.0. Calm bars (o 100.5, h 101, l 100, c 100.5, fp 100:1:0; R 1, ATR 1, poc 100.5):
  buy 0 / sell 1, b99 buy 1; long e_i 10, i 80: P -1, drift 0 -> S2 -1 = -s; (a) net +15 false. EXPECT True; e_i 30
  EXPECT False (21 > 30 no). Short mirror (buy 1 / sell 0, b99 sell 1), e_i 10: EXPECT True.
  Count clause: 121 alternating bars (even j: o 100, c 100.5, buy 1; odd: o 100.5, c 100, sell 1; b99 buy 1 each); bar 100
  is o = c = 100, buy 3 (e 3, res 0: absorbed +1, the only S3 event). i 120, W' [61,120]: R 0.5, c = poc 100.5; P 2/62 =
  0.032 < p -> S2 0; n(+1) 1 > n(-1) 0. Long e_i 10 EXPECT True. Bar 100 sell 3 (P -4/62, n(-1) 1): EXPECT False (hold).
- T56 S8(d): bars 0..59 alternate (even o 100 c 100.5 buy 1; odd o 100.5 c 100 sell 1); bar 60 o 100 h 102 l 100 c 101.8
  buy 1, b99 buy 5; bar 61 o 101.8 h 102 l 101.5 c 101.8 buy 3. Long e_i 55, i 61, z_hi 2.5. S3(61): d baseline (bars 1..60)
  sum 0, sd 1 -> e 3; r baseline sum 1.3, mean 0.021667, E[r^2] 17.99/60, sd 0.547142 -> res -0.0396 -> absorbed +1.
  Bar 60 new extreme (102 > 100.5), net 5. EXPECT climax True -> True; climax False -> False ((a) age 6, (b) no, (c) no).
  Bar 61 c 102.5, h 102.6 (res 1.2398, control +1): EXPECT False. Bar 60 without b99: EXPECT False.
- T57 S5D on F1 with bar 5 = 101/103/100.8/102.5, buy 6 sell 4, b99 buy 3; absb[3] = -1; N 4, k_bal 0.8, p 0.10, m 1.
  S2(4) = -1, c[5] 102.5 > H 102, net +3. EXPECT {s +1, lvl l[3] 99.0, edge 102.0}; breakout() EXPECT 0 on the same bar.
  absb all 0 EXPECT None; absb[0] = -1 only (outside [1,4]) EXPECT None; c[5] 101.9 EXPECT None; b99 sell 3 EXPECT None.
- T58 model D (k 0, s +1, edge 102.0, lvl 99.0, f 0.3%, Dmax 5%, dist, ctrl[3] = +1). Bars 0: 101/102.8/100.9/102.5;
  1: 102.5/102.9/102.0/102.6; 2: 102.6/102.7/101.9/102.4; 3: 102.4/105.2/102.3/105.0; 4: 104.0/104.2/102.1/102.5.
  rest: bar 1 no fill (102.0 > 101.9); bar 2 fill 102.0, D max(0.306, 3.1) = 3.1, stop0 98.9; bar 3 fav 3.2: BE, trail 102.2;
  bar 4 exit 102.2 "trail". EXPECT gross 0.064516, fee 0.0005*102/3.1 = 0.016452, net 0.048065. Dmax 1% (3.1 > 1.02) EXPECT arms 0. Bar 2 l 102.0 and bar 4 l 101.8:
  EXPECT arms 1, fills 0 (expired after bar 3), missed 0 (108.2 never reached). confirm: taker o[1] 102.5, D 3.6, stop0
  98.9, fill_idx 1; bar 3 fav 2.7 < 3.6; EXPECT exit c[4] 102.5 "window_end", gross 0, fee 0.028472, net -0.028472.
- T59 model B trail: T37 bars, target_mode "trail". Bar 8 fav 1.5 < 1.6; bar 9 fav 2.7 -> BE 101.5; no target. EXPECT exit
  c[9] 99.0 "window_end", no target key value, gross 1.5625, fee 0.0005*101.5/1.6 = 0.031719, net 1.530781.
- T60 day floor / carry: [1.0, -1.0] EXPECT not allowed (peak 1, C 0). [1.0, -0.5] allowed, risk 0.5. [2.0] risk 1.0.
  [] carry 0.6 risk 0.6. [-0.6] carry 0.6 not allowed. [] carry -0.4 risk 1.0. [1.5] carry -1.2 (P 0, -1.2, 0.3) not allowed.
  [-0.5, 0.6] risk 0.1. [] risk 1.0. [-1.2,-1.2] risk 1.0. [-1.2]*3 risk 0.0. T44 cases unchanged.
- T61 day R with risk_u: d1 [{net 2.0, risk_u 0.5}, {net -1.1}], d2 none. EXPECT [-0.1, 0.0].
- T62 adds v3.1: add_size(+1, [(1, 100)], stop 99, pa 101, q1 1, budget 3.0): locked -1, (3-1)/2 = 1.0 EXPECT 1.0 (open risk
  at the stop 1 + 2 = 3 = budget); budget 1.5 EXPECT 0.25; budget 1.0 EXPECT 0.0. add_allowed: T33 base with n_adds 2
  EXPECT False, n_adds 1 True; stop 99 add_mode "day" EXPECT True; premium with s7 False EXPECT True.
- T63 calendar: ny_open_utc None on 2024-12-25, 2025-01-09, 2025-04-18, 2025-07-03, 2025-07-04, 2025-11-27, 2025-11-28,
  2025-12-24, 2026-04-03, 2026-07-03; 2025-12-26 EXPECT 14:30; 2025-07-07 EXPECT 13:30. london_open_utc: 2025-03-28 08:00;
  2025-03-31 07:00; 2025-10-24 07:00; 2025-10-27 08:00; 2025-03-29 Sat None.
- T64 look-ahead canary (as T49) for S5D, S9 and S8 with climax True.

## 11. Implementation notes
- Signals take parameters explicitly (no module constants in formulas) so tests can use N=4, L=4, bin 1.0.
- Function defaults mgmt "dist", add_mode "be", s7 True, target_mode "edge", climax False keep T01-T50 valid; the runner
  always passes the grid values explicitly (main grid: mgmt "event").
- Output: trades.csv (model, variant, day, side, relation, legs, moves, R, risk_u, reason, day type, regime), days.csv,
  tables.md, results.json off C:; TRIAL_REGISTRY rows before the run.
- Gate: `python scripts/dev/run_all_tests.py --quick` before any commit (CLAUDE.md gates).

## 12. Open items (v3.0 items resolved by the operator 2026-09-30)
1. Adds before BE: only the registered add_mode "day" variant. 2. S7: default on, variant off. 3. US holidays: excluded
(US_CLOSED). 4. Dealer gamma: dropped. 5. Deribit tick and basis: verify on desktop before runs.
Not applied: M9 scratch-and-re-pivot re-entry (not in the approved list; needs its own registered trial); M2 "close 50%"
cell (the transcript does not say how risk was lowered, fZ:67-68, LBL ambiguity 3; partial exits would need new leg
accounting). Left open: which way the L69-72 snapback goes (LBL 7.1); reload prices vs the first entry (LBL 7.2).
