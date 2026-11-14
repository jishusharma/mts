# PRE_REG nkn05-hm-htf-state-1114 (written and committed with study.py and test_study.py BEFORE any outcome is computed)

Operator order 2026-11-14 06:12Z: NK rules are not tested blindly; context applied correctly, thought about from phases / context / crypto context / layers / levels. An all-bars mechanical test is not acceptable.
Rule NKN-05: weekly Hilega-Milega "red line down" = buy state (SOURCED FzNDQm7wC_s 00:03:09 and 00:03:12, a CLAIM) plus a daily gate (Hyp B). The frozen design is `nkn_design/NKN-05.md` (side-session notes local_62e478d7). It is copied below and is binding; nothing here is NK's own number unless labelled SOURCED.

## Hypothesis
H-A: in the post-fall turn cell (PC) a coin whose closed weekly bar is in HM BUY state has a higher 4-week forward return than the same coins in HM SELL state, and the buy entry is profitable after fees. H-A2: that buy-minus-sell gap is larger AT the weekly SMA50 than AWAY from it. If the gap is equal at and away from the level, NKN-05 reduces to the plain HM claim. Prior is low (0 of about 100 NK rows have passed). A FAIL or UNDERPOWERED verdict is a valid result.

## Context
- Regime: BTC cycle state M (BEAR / BASE / BULL) read from `phase_daily.csv` at the entry-week Monday row; PRIMARY cell PC requires cycle in {BEAR, BASE}; BULL weeks are controls only. Regime mix (BULL / BEAR / BASE shares and the six label shares, DEV and VAL) is printed in RESULT before any verdict.
- Phase: BTC phase label (RELIEF, ACCUM-RANGE for PC; MARKUP, MARKDOWN, DISTRIBUTION as controls) taken from `F:/MTS/data_cache/mts_brains/phase_daily.csv`, label at the entry-week Monday row, applied to all coins (one BTC label for all alts is a stated doubt). Look-ahead poke done by the code at run time: the file's `close_used` at date d is compared with the BTC daily close of d-1 (lag 1) and d (lag 0); if lag 0 matches better the labels are shifted one day. Provisional rows never enter. CAPITULATION is not a cell (its weeks stay in the R0 reference row only).
- Session: week open Monday 00:00 UTC (OURS); decision on the closed Sunday weekly bar, entry at the next weekly open. London/NY opens and expiry are dropped (not translatable).
- Entry: weekly HM state W on a closed weekly bar (BUY = red < green AND red < RSI9) inside the cell; tradeable version enters long at the next Monday 00:00 open (market, next-bar open), 4-week hold, stop 1R. Layer variants V0 / V1 / V2 below.

## Frozen design (copied from NKN-05.md)

### Phase tested
- Weekly decision. BTC phase label read at the week-open Monday row. provisional rows never enter a result.
- **PRIMARY cell PC:** label in {RELIEF, ACCUM-RANGE} AND cycle in {BEAR, BASE} (post-fall turn; OURS reading of NK's bear-to-bull framing). Phase is the cell, not a filter row; Hyp A is never tested pooled across phases.
- Side: long, weekly HM buy state; contrast = same coins in HM sell state, same cell.
- Controls (each alone, never pooled): C1 buy in MARKUP; C2 buy in MARKDOWN; C3 buy in DISTRIBUTION; C4 sell state in PC; C5 matched random coin-weeks in PC (placebo, month-of-year spread of the real cell, 1000 draws); C6 neutral state in PC. Pooled all-weeks buy appears only as the labelled REFERENCE row R0.

### Context conditions
1. HM state W (formula OURS; "red line down" SOURCED FzNDQm7wC_s 00:03:09 and 00:03:12): closed weekly bar, RSI9 (Wilder, ewm alpha 1/9); green = EMA3 (span 3, adjust False) of RSI9; red = WMA21 (newest weight 21) of RSI9. BUY = red < green AND red < RSI9. SELL = red > green AND red > RSI9. Else NEUTRAL (three states SOURCED B7iGQef_z6I 00:03:22; neutral is not short). Strict inequalities on both lines (OURS, fixed once).
2. Weekly anchor UTC Monday 00:00 (OURS); state read on the closed Sunday bar; reference = next Monday open; forward windows 1, 2, 4 weeks (OURS; 4 weeks is the only gating horizon).
3. Phase = PC, label and cycle thresholds as-is from the shared builder (OURS, no re-tuning).
4. V1 BTC trend (rule SOURCED t1b_1h2QMXw 00:18:13 "trade with the index"; BTC proxy OURS): BTC weekly close > its weekly SMA20 (SMA not EMA: SOURCED FzNDQm7wC_s 00:02:39). BTC itself exempt. Alts reported with and without (P1 vs P2, C7 = V1 complement).
5. V2 daily agreement (SOURCED fZvp72BBmRI 00:04:58 RSI(14) > 50; ysq6x0eCFvI 00:04:37 close above SMA20): last closed daily bar before entry (the Sunday bar): daily RSI14 (Wilder) > 50 AND close > SMA20. AND with V1 and with HM (his entry gate is "HM must agree"; the draft OR is dropped).
6. Level split, weekly SMA50 (OURS; NK names no weekly level): L = SMA50 of weekly closes through the signal week, A = Wilder ATR14 of weekly bars (ewm alpha 1/14). AT-ABOVE: |close-L| <= 1.0 A and close >= L; AT-BELOW: |close-L| <= 1.0 A and close < L; AWAY: otherwise. One value, no second band. (Idea of no-first-touch-support from fZvp72BBmRI 00:18:39 is used as a split, not a veto.)
7. Funding split (OURS, no NK source): mean of the last 9 eight-hour settlements strictly before the entry instant (about 3 days), required fresh (<= 9 h old); terciles computed on DEV PC buy coin-weeks only, frozen, applied to VAL. Descriptive only; 17 of the 20 coins have funding (no ALGO, FIL, NEAR).
8. Dropped from the Context angle: overheat veto > 86 (caption UNCONFIRMED), RSI30 recovery, 2-close persistence on HM, 1 ATR vs 20-week-low level, OI (history from 2020-09 only).
9. HM formula is OURS and unverified against his chart. The TradingView cross-check of 3 dated weekly BTC bars has NOT been done in this study (no browser step available to this worker); until it is done any PASS carries the label UNVERIFIED-HM.

### Crypto translation
- Session open = week open Monday 00:00 UTC; daily gate bars close 00:00 UTC. No gap replacement: entry = next weekly open (continuous market).
- Funding: descriptive crowding split (cond. 7), replaces expiry. OI dropped. BTC market filter = V1 (weak Nifty proxy: alts are BTC beta); BTC-own rows are reported separately as a descriptor, not a cell.
- Does NOT translate: "market does not go down" (index of 50 names vs one coin; ported only as 4-week return distribution), weekly expiry, gap, options, ADX/WT layers.
- Headline metric is the excess over the unconditional forward return of the same cell weeks (crypto drifts): excess = mean 4-week return of the cell minus mean 4-week return of ALL coin-weeks in the same phase base (any HM state, same split).
- Cluster by calendar week; effective n is the number of distinct weeks (about 150 on VAL at most), not coin-weeks; distinct weeks and distinct BTC label spells are printed beside every row.

### Layer variants
| Variant | Exact layer read |
|---|---|
| V0 rule alone | weekly HM state W inside the cell, nothing else |
| V1 | V0 AND BTC weekly close > weekly SMA20 (BTC exempt) |
| V2 | V1 AND daily RSI14 > 50 AND daily close > SMA20 |
Overlap (share of PC buy weeks kept by V1 and V2) is reported. The cycle layer is inside PC. ADX/DI dropped. C4 is the control for every variant (prior evidence: RSI-CONFIRM-LAYERS 0/56).

### Level type
One primary level: weekly SMA50, at-level = within 1.0 weekly ATR14, away = complement. H-A2 role as above. 1 ATR may cover 40-50% of weeks; not tuned.

### Timeframes
Native weekly (decision and forward windows) and native daily (V2 gate). 15m, 1h and 4h rows are NOT run: the claim is a weekly state; lower timeframes would be a different rule (NK4 tested the intraday HM flip: FAIL). One timeframe row (weekly). Fee-net rows only for the filtered-entry version.

### Cells (22) and primary cells (3)
| ID | Phase cell | Variant | Level | Side/state | Role |
|---|---|---|---|---|---|
| P1 | PC | V0 | all | long, buy | PRIMARY |
| P2 | PC | V1 | all | long, buy | PRIMARY |
| P3 | PC | V2 | all | long, buy | PRIMARY |
| C1 | MARKUP | V0 | all | buy | CONTROL |
| C2 | MARKDOWN | V0 | all | buy | CONTROL |
| C3 | DISTRIBUTION | V0 | all | buy | CONTROL |
| C4 | PC | V0 | all | sell | CONTROL (contrast for P1-P3) |
| C5 | PC | placebo random weeks | all | long | CONTROL |
| C6 | PC | V0 | all | neutral | CONTROL |
| C7 | PC | V1 complement (BTC <= SMA20, alts only) | all | buy | CONTROL |
| R0 | all labelled phases pooled | V0 | all | buy | REFERENCE (labelled) |
| L1-L3 | PC | V0 | AT-ABOVE / AT-BELOW / AWAY | buy | CONTROL (descriptive) |
| L4-L6 | PC | V0 | AT-ABOVE / AT-BELOW / AWAY | sell | CONTROL (descriptive) |
| F1-F3 | PC | V0 | all | buy, funding tercile low/mid/high | CONTROL (descriptive) |
| N1-N2 | PC | V0 and V2 | all | buy, fee-net filtered entry | CONTROL (the same trades as the tradeable version of P1 and P3) |

**Total cells tried: 22.** **Primary cells: 3** (P1, P2, P3). Extra reported rows that are NOT cells and never enter BH: BTC-only P1-P3 (descriptor), fresh-holdout P1-P3 (design: run once, reported separately), H-A2 gap, overlap shares.

## Universe, data, splits
- Universe fixed now: 20 Binance spot coins from `binance_spot/<SYM>_15m.npz`: BTC, ETH, BNB, XRP, ADA, DOGE, SOL, TRX, LINK, LTC, BCH, XLM, ETC, ATOM, ALGO, AVAX, DOT, FIL, NEAR, UNI. A coin enters from its 52nd weekly bar after its data start (OURS; survivorship: all coins are listed today, stated bias). Fresh holdout (reported separately, run once, descriptive): AAVE, ENJ, GRT, HBAR, MANA, SAND, THETA, XTZ from `binance_fresh/nk5_nyasia/*_5m.npz`.
- ONE source per coin: weekly and daily bars are resampled from that coin's finest series (15m, holdout 5m). Weekly bar = Monday 00:00 to Sunday 23:59 UTC; accepted only if the first and last fine bar of the group exist and coverage >= 95% (daily >= 90%). Loader asserts the time key (`t` or `ts`, or the 2-D `a` layout), strictly increasing timestamps, every step a multiple of the bar size with minimum step equal to the bar size (gaps allowed and counted); per-file first/last/gaps are printed in RESULT. Resampler cross-checked against `binance_spot_htf` weekly for BTC and ETH.
- DEV = signal week start before 2024-01-01 UTC; VALIDATION = on/after. Split by the SIGNAL week, never entry or exit.
- No data was fetched; nothing was written to the cache.

## Trades (tradeable filtered-entry version)
Signal on the closed Sunday bar; entry long at the next Monday 00:00 open (next-bar open); stop = entry x (1 - df), df = max(0.5%, 0.6 x weekly ATR14 / entry) (OURS) so R = df x entry; time exit at the Monday open 4 weeks later (OURS); stop checked on every fine bar (15m, holdout 5m) from the entry bar, fill at the stop, or at the bar open if the bar opens at or through the stop (gap). There is no target, so stop-before-target ordering does not arise. Fee-net R: gross R = (x - e)/(e df); fee R = (bp/2e4) (e + x) / (df e), i.e. bp/2 of the notional on EACH leg: 12 bp = 6 bp entry + 6 bp exit (taker, primary verdict), 6 bp = 3 + 3 (maker, secondary, assumed filled at the same prices: optimistic, non-gating). No funding charge (spot-equivalent). Consecutive buy weeks of one coin give overlapping 4-week trades; calendar-week clustering handles the cross-section only, so a 4-week-block bootstrap CI low is printed as information.

## Statistics and gates (VAL primary cells P1-P3)
Event study (4-week forward return, entry Monday open to Monday open 4 weeks later, gross, no fees):
- E1 week-cluster bootstrap (5000 draws) 95% CI low of mean(buy) - mean(sell in PC, same split) > 0;
- E2 ex-best-5-weeks diff > 0; E3 beats the placebo (C5-like: random coin-weeks of PC, any state, same split, same month-of-year spread, matched count, 1000 draws; p = (1+#draw>=real)/(1001) <= 0.05);
- E4 same sign of the buy-sell difference on DEV; E5 Benjamini-Hochberg q <= 0.10 over P1-P3 on the one-sided week-cluster p (diff <= 0).
Tradeable version (fee-net R at 12 bp):
- T1 mean net R > 0; T2 coin-week bootstrap CI low > 0 (5000); T3 calendar-week-cluster CI low > 0; T4 ex-best-5-weeks mean > 0; T5 placebo (random PC coin-weeks, same simulated trade/stop/fee, matched count and month spread) beaten, p <= 0.05; T6 BH q <= 0.10 over P1-P3.
- A primary cell is UNDERPOWERED (not FAIL, not PASS) when n VAL < 100 coin-weeks (event study or trades) or fewer than 20 distinct VAL calendar weeks (reported UNDERPOWERED-WEEKS). PASS needs every gate E1-E5 AND T1-T6, and only the tradeable version counts toward PASS. "Beats placebo" is reported separately from "profitable". HM TradingView check not done: any PASS is labelled UNVERIFIED-HM.
- Overall verdict: PASS if any primary cell passes; UNDERPOWERED if all three are underpowered; otherwise FAIL.
- Controls are descriptive; they carry no verdict and are never pooled with primary.

## Parameters (SOURCED / OURS)
| Parameter | Value | Label |
|---|---|---|
| HM red line "down" = buy | red < green AND red < RSI9 | SOURCED claim FzNDQm7wC_s 00:03:09, 00:03:12; formula OURS |
| RSI period 9, EMA 3, WMA 21 | 9, 3, 21 | OURS (reconstruction, unverified) |
| Three states incl. neutral | buy/sell/neutral | SOURCED B7iGQef_z6I 00:03:22 |
| Weekly SMA for BTC trend | SMA20 | SOURCED FzNDQm7wC_s 00:02:39 (SMA not EMA); length 20 OURS |
| "Trade with the index" | V1 | SOURCED t1b_1h2QMXw 00:18:13; BTC proxy OURS |
| Daily RSI14 > 50 | 14, 50 | SOURCED fZvp72BBmRI 00:04:58 |
| Close above SMA20 daily | 20 | SOURCED ysq6x0eCFvI 00:04:37 |
| Weekly SMA50 level, 1.0 ATR14 band | 50, 1.0, 14 | OURS |
| Phase cell PC and cycle states | RELIEF/ACCUM-RANGE x BEAR/BASE | OURS |
| Funding window and terciles | 9 settlements, DEV terciles | OURS |
| Weekly anchor Monday 00:00, horizons 1/2/4 w, gating 4 w | | OURS |
| Stop: max(0.5%, 0.6 x weekly ATR14); time exit 4 weeks | | OURS |
| Fees 12 bp taker (gating), 6 bp maker | | OURS (cost assumption) |
| Min coin age 52 weeks; coverage 95% / 90% | | OURS |
| Bootstrap 5000, placebo 1000, seeds fixed in code | | OURS |
Every OURS parameter takes one value; no grid; none is described as NK's.

## Kill rules
No cell, parameter or horizon is added or changed after the first real run. A bug fix is allowed only as a separate commit and is listed in RESULT "Deviations". If PC on VAL is thin the verdict is UNDERPOWERED; it is not rescued by pooling phases, lowering n, or using BULL cycle weeks.

## Design items not implemented (declared before any run)
- The TradingView cross-check of the weekly HM (condition 9): not done by this worker; verdict label carries UNVERIFIED-HM.
- 15m / 1h / 4h signal-timeframe rows: not expressible for a weekly state (design "Timeframes").
- Post-2026-11-13 forward weeks: the cache ends 2026-11-13, so no forward-only rows exist; the 4-week horizon also leaves the newest 5 weeks without an outcome (they are dropped from outcome rows).
- Funding and the fee-net/funding rows for the fresh-holdout coins: no funding file for them; holdout rows are P1-P3 only.
- "First week of the state" descriptor: not implemented (dropped; the design lists it only as an optional descriptor).
- `MTS_BRAINS_SPEC_1114.md` is not in the worktree; labels rely on `phase_daily.csv` (poked at run time as described).
- CI hygiene: the ship gate wants this test file listed in `scripts/dev/extra_tests.tsv`; that file is outside this worker's folder and is left to the coordinator.
