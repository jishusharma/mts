5 BLOCKERS, 19 AMBIGUITIES

## Summary Table (One Row per Test Brief)

| test | finding | file:line | severity | fix sentence |
|---|---|---|---|---|
| Test 1: Causal confirmation ladder, long side | `base` phase has no causal definition ("after the cycle low" in `BUY_ZONE_MAP.md:98` is ex-post) and `RANGE` is omitted; `10 days` lockout (`NEXT5_TESTS.md:14`) conflicts with `30 days` hold + "no overlapping trades"; plus 4 ambiguities (pivot left/right bars, `RSI or WT` primary choice, ex-ante 20-coin list, `0.5%` stop anchor & `2 x ATR` trail mechanics). | `NEXT5_TESTS.md:31-45` | BLOCKER | Define `base` causally from `t-1` daily bars, map or exclude `RANGE`, state lockout as `max(10d, exit+1d)`, fix the 20-coin universe ex-ante, pick `RSI` or `WT` and pivot/trail rules in `PRE_REG.md`, and align the `0.5%` stop anchor to entry. |
| Test 2: Multi-timeframe context rule, both sides | Entry `4H close that breaks the 4H swing` (`NEXT5_TESTS.md:57`) enters at the signal close instead of next 4H open (lookahead/execution impossibility), `1W/3D` causal confirmation timing is unspecified, and `base`/`post-peak bear` lack causal definitions; plus 4 ambiguities (4 context combos, 4H pivot/opposite-signal rules, omitted 12/6 bp costs & DEV/VAL/RECENT & funding, unfixed 20-coin universe & no abort rule). | `NEXT5_TESTS.md:53-63` | BLOCKER | Change entry to next 4H open after causal 4H swing-break close, require `1W/3D` divergence to be closed-bar + pivot-confirmed before `t`, define `base`/`post-peak bear` causally (and handle `RANGE`), and add 12/6 bp costs, funding, DEV/VAL/RECENT columns, and an abort threshold. |
| Test 3: Bear-phase 4H divergence short, replication | `post-peak bear = previous day's close below 50-week SMA AND no base reclaim` (`NEXT5_TESTS.md:72`) leaves `no base reclaim` undefined and `50-week SMA` (closed weekly bar vs 350d rolling) unstated; plus 4 ambiguities (BB params & `RSI or WT` primary choice, causal pivot left/right bars, `0.5%` stop anchor & `2 x ATR` trail mechanics, Bybit funding DEV coverage & shared-rule restatement). | `NEXT5_TESTS.md:71-80` | BLOCKER | Define `no base reclaim` with an explicit causal rule on `t-1` daily bars, specify closed-weekly-bar 50w SMA, lock BB (`20, 2.0`), primary oscillator (`RSI` or `WT`), and causal pivot left/right bars in `PRE_REG.md`, and align stop/trail/Bybit-funding rules. |
| Test 4: Capitulation signature at lows | Hidden lookahead: `38 anatomy lows from BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:89`) were selected with future bars (`NEXT5_TESTS.md:119`), and measuring `funding negative at the low` + `1d, 3d, 7d` forward returns from the low when `failed breakdown` (`close back above within 2 weeks`) confirms up to 14 days later leaks future data; Step 2 (`NEXT5_TESTS.md:92`) also lacks a stop, making `mean R` (`NEXT5_TESTS.md:21`) undefined; plus 4 ambiguities (`random lows-like bars`, OI/funding/swing-low rules, BTC vs 20 coins, DEV/VAL split on >=6 lows). | `NEXT5_TESTS.md:88-96` | BLOCKER | Recompute lows causally and index all Step 1/Step 2 forward returns from the reclaim close (not the ex-post low), define a stop (e.g. `max(0.6 x ATR, 0.5%)` below the low) and `lows-like` placebo criteria for Step 2, and specify BTC-only vs 20-coin scope and DEV/VAL handling. |
| Test 5: Large-flow lead test with a proper lag | `non-overlapping windows` (`NEXT5_TESTS.md:106`) conflicts with `All days` + `t+1 to t+72 h` (daily steps overlap 48h on 72h returns), and Test 5's Verdict (`NEXT5_TESTS.md:112`) omits `DEV sign agrees` and `CI low > 0` from the shared verdict (`NEXT5_TESTS.md:21`) and leaves `>= $1M` vs `>= $5M` pass criteria unstated; plus 3 ambiguities (`t+1` bar boundary, flow unit/venue & BTC scope, in-sample quintile lookahead & Coinbase premium test). | `NEXT5_TESTS.md:104-112` | BLOCKER | Use non-overlapping 24h (1d step) and 72h (3d step) blocks, require `DEV sign agrees` + bootstrap `CI low > 0` + explicit `>= $1M`/`$5M` and shuffle-percentile pass rules, fit quintile cutoffs ex-ante/in-DEV only, and define exact `t+1` boundaries and Coinbase premium testing. |

---

## Shared Rules Baseline Check (`NEXT5_TESTS.md:5-23`)

Before checking each brief, note four cross-cutting issues in the Shared Rules themselves:
1. **Phase definitions are non-exclusive and partly ex-post (`BUY_ZONE_MAP.md:70-98`, `NEXT5_TESTS.md:9`):**
   - `UP` (`BUY_ZONE_MAP.md:70`: `price above rising 200d, DI+ over DI-`), `DOWN` (`BUY_ZONE_MAP.md:77`: `below falling MA20, DI- over DI+`), `RANGE` (`BUY_ZONE_MAP.md:84`: `ADX low, price inside value`), `Post-peak bear` (`BUY_ZONE_MAP.md:91`: `after a cycle top, below 50w, no base yet`), and `Base` (`BUY_ZONE_MAP.md:98`: `after the cycle low, reclaiming, higher lows`) can overlap on the same day (e.g., `DOWN` and `Post-peak bear`, or `UP` and `Base`). `Base` ("after the cycle low") is ex-post. No precedence order is given.
2. **Lockout vs hold length (`NEXT5_TESTS.md:14`):** `10 days between events on the same coin (no overlapping trades)` is ambiguous whenever hold > 10 days (e.g., Test 1's 30-day hold): coders may enforce `>= 10d` from prior *entry* (which allows overlapping trades) or `>= 10d` from prior *exit*.
3. **Verdict placebo threshold & `RECENT` boundary (`NEXT5_TESTS.md:12, 21`):** `RECENT` has no start date, and `beats the placebo band` (`NEXT5_TESTS.md:21`) does not specify the percentile cutoff (e.g., > 95th percentile of `N >= 1000` draws).
4. **Stop `0.5%` base (`NEXT5_TESTS.md:11` vs `40, 58, 75`):** Shared rule says `max(0.6 x ATR, 0.5%) from entry`, while Tests 1, 2, and 3 say `below the second low` / `beyond the 4H pivot` / `above the divergence high` (two different percentage bases: `0.5%` of entry vs `0.5%` of pivot).

---

## Per-Test Detailed Review

### Test 1: Causal confirmation ladder, long side (rank 1) (`NEXT5_TESTS.md:27-46`)

#### Parameters (SOURCED vs OURS)
| Parameter | Value in `NEXT5_TESTS.md` | Label | Source Quote & `file:line` |
|---|---|---|---|
| Candidate A (`HL_BREAK`) | Second swing low above first; entry on close above high between lows (1D) | SOURCED | `"HL_BREAK: second low above first, close above the high between them"` (`BUY_ZONE_MAP.md:101`); `"HL_BREAK, or bullish 1D divergence then close above the between-lows high"` (`BUY_ZONE_MAP.md:109`) |
| Candidate B (`BULL_DIV`) | 1D bullish RSI or WaveTrend divergence on second low, then close above high between lows (1D) | SOURCED (RSI/WT choice OURS) | `"bullish 1D divergence then close above the between-lows high"` (`BUY_ZONE_MAP.md:109`); `"Bullish divergence on 1D / 4H (RSI, WT, CVD) on the second low"` (`BUY_ZONE_MAP.md:21`) |
| Primary vs secondary | Pre-register ONE as primary, other as secondary | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:31`) |
| Universe | BTC, ETH and 20 liquid coins; Binance spot 2017+; Bybit funding where needed | SOURCED | `"Run on BTC, ETH and 20 coins"` / `"Binance spot 2017+ plus Bybit funding"` (`BUY_ZONE_MAP.md:109`) |
| Phase filter | Long only in `UP` and `base`; report `DOWN` and `post-peak bear` as control | SOURCED (selection OURS) | `"phase-split"` (`BUY_ZONE_MAP.md:109`); phases listed in `BUY_ZONE_MAP.md:70-98` |
| Entry | Next 1D open after confirming close | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:39`) |
| Stop | `max(0.6 x ATR14, 0.5%)` below the second low | OURS (placebo match SOURCED) | `"versus the placebo at the same stop"` (`BUY_ZONE_MAP.md:109`); formula in `NEXT5_TESTS.md:11,40` |
| Exit | First of trailing stop (`2 x ATR`) or `30 days` | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:41`) |
| Costs / Lockout / Bootstrap / Placebo | 12 bp main, 6 bp sensitivity; 10-day lockout; block bootstrap (block = hold); placebo `N >= 1000` | SOURCED (12 bp, lockout, block bootstrap); OURS (6 bp, `N >= 1000`) | `"fee-net"`, `"10-day lockout between events and a block bootstrap"` (`BUY_ZONE_MAP.md:109`); `"12 bp round trip"` (`BUY_ZONE_MAP.md:115`) |
| Abort rule | `< 30` events in VAL pooled -> report `"underpowered"` | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:45`) |

#### Shared Rules Check
- **Phase split from `t-1` daily bar only:** Violated/blocked for `base` (`BUY_ZONE_MAP.md:98`: `"after the cycle low, reclaiming, higher lows"` is ex-post). `RANGE` phase (`NEXT5_TESTS.md:9`) is omitted from `NEXT5_TESTS.md:37`.
- **Lockout 10 days:** Contradicts `30 days` max hold + `"no overlapping trades"` (`NEXT5_TESTS.md:14` vs `41`).
- **Placebo `N >= 1000` & 12/6 bp & DEV/VAL & PASS rule:** Inherited from Shared Rules (`NEXT5_TESTS.md:10,12,13,21`); `PRE_REG.md` must still fix which placebo percentile counts as `"beats the placebo band"`.

#### Ambiguities Two Coders Would Read Differently
1. **Swing-low pivot definition:** Left/right bar counts and min/max bar spacing between first and second low are unstated; causal confirmation only occurs after `right_bars` close.
2. **`BULL_DIV` indicator & primary pick:** `"RSI or WaveTrend"` is not narrowed to one primary, and RSI/WT periods are unstated.
3. **20-coin universe & Bybit funding:** Which 20 coins (and how selected without survivorship bias) is unstated; `Bybit funding where needed` is unexplained for a spot-long test.
4. **Stop & trailing-stop mechanics:** `0.5%` from entry (`NEXT5_TESTS.md:11`) vs `0.5%` below second low (`NEXT5_TESTS.md:40`); `2 x ATR` trailing stop omits ATR period, anchor (`close` vs `high`), closed-bar vs intrabar check, and whether initial stop remains active.

---

### Test 2: Multi-timeframe context rule, both sides (rank 2) (`NEXT5_TESTS.md:49-63`)

#### Parameters (SOURCED vs OURS)
| Parameter | Value in `NEXT5_TESTS.md` | Label | Source Quote & `file:line` |
|---|---|---|---|
| Universe | 20 coins, pooled | SOURCED | `"pooled across 20 coins"` (`BUY_ZONE_MAP.md:110`) |
| Phase filter | Daily phase from previous day's bar only; long in `UP`/`base`, short in `DOWN`/`post-peak bear` | SOURCED (phase filter); OURS (side mapping) | `"phase filter (daily)"` (`BUY_ZONE_MAP.md:110`); mapping in `NEXT5_TESTS.md:55,57` |
| Context | `1W` or `3D` RSI/WT divergence present in last `4 weeks` (causal) | SOURCED (`1W/3D` div); OURS (`RSI/WT`, `4 weeks`) | `"1W/3D divergence as context"` (`BUY_ZONE_MAP.md:110`) |
| Entry | `4H` close that breaks the `4H` swing in direction of phase | SOURCED (`4H` TF); OURS (swing-break trigger) | `"4H/1D entry; both sides"` (`BUY_ZONE_MAP.md:110`) |
| Stop | `max(0.6 x ATR14 on 4H, 0.5%)` beyond the `4H` pivot | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:58`) |
| Exit | Opposite `4H` signal or `10 days` | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:59`) |
| Placebo | Same phase, same side, same hold, entries at random `4H` bars (`N >= 1000` via shared) | SOURCED | `"placebo on every pooled table"` (`BUY_ZONE_MAP.md:110`) |
| Top-coin ablation | Report result with top coin removed | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:63`) |

#### Shared Rules Check
- **Phase split from `t-1` daily bar only:** Stated at `NEXT5_TESTS.md:55`, but `base` and `post-peak bear` lack causal definitions in `BUY_ZONE_MAP.md`, and `RANGE` is unmapped.
- **12/6 bp costs, DEV/VAL/RECENT, Lockout 10d, Placebo `N >= 1000`, PASS rule:** None are restated in Test 2's Outputs (`NEXT5_TESTS.md:63`), and `DEV/VAL/RECENT` columns are omitted from Test 2's output spec (unlike Test 1). Funding for 10-day shorts is also omitted.

#### Blockers & Ambiguities Two Coders Would Read Differently
1. **BLOCKER — Lookahead at entry (`NEXT5_TESTS.md:57`):** Entering *on* the `4H close` instead of `next 4H open` assumes knowledge of the close at the moment of execution.
2. **BLOCKER — `1W/3D` causal confirmation timing:** A `1W` or `3D` divergence is only causal after the `1W`/`3D` bar closes AND right-pivot bars close; `"in the last 4 weeks"` does not specify whether `4 weeks` is 28 days from that confirmation bar.
3. **Context & direction ambiguity:** `1W` vs `3D` and `RSI` vs `WT` yield 4 variants with no primary; bullish-for-long / bearish-for-short is implied, not stated.
4. **`4H swing` / `4H pivot` / `opposite 4H signal`:** No pivot left/right bar counts or swing-break rule (`close` vs `wick`), and `"opposite 4H signal"` could mean opposite swing break, opposite 4H divergence, or full opposite context+entry.
5. **Universe & abort rule:** 20 coins not fixed ex-ante; no minimum `n` abort rule in VAL.

---

### Test 3: Bear-phase 4H divergence short, replication (rank 3) (`NEXT5_TESTS.md:67-80`)

#### Parameters (SOURCED vs OURS)
| Parameter | Value in `NEXT5_TESTS.md` | Label | Source Quote & `file:line` |
|---|---|---|---|
| Universe | 20 coins | SOURCED | `"on 20 coins"` (`BUY_ZONE_MAP.md:111`) |
| Phase flag | `post-peak bear` = previous day's close `< 50-week SMA` AND `no base reclaim` (ex-ante) | SOURCED | `"below 50w, no base yet"` (`BUY_ZONE_MAP.md:91`); `"using the daily phase of the previous day only"` (`BUY_ZONE_MAP.md:111`) |
| Signal | `4H` bearish divergence outside upper Bollinger band (`RSI` or `WT`), pivot-based | SOURCED (BB div); OURS (`RSI or WT`) | `"4H divergence outside band with pivot stop, only in bear phase"` (`BUY_ZONE_MAP.md:94`) |
| Entry | Short on next `4H` open after confirming close | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:74`) |
| Stop | `max(0.6 x ATR14 4H, 0.5%)` above divergence high | OURS (pivot stop SOURCED) | `"with pivot stop"` (`BUY_ZONE_MAP.md:94`); formula in `NEXT5_TESTS.md:11,75` |
| Exit | First of `2 x ATR` trailing or `7 days` | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:76`) |
| Funding | Actual funding paid while held; report with and without funding | SOURCED | `"with funding"`, `"Funding history"` (`BUY_ZONE_MAP.md:111`) |
| Fees & Verdict | 12 bp main, 6 bp sensitivity; shared verdict rule | SOURCED (12 bp); OURS (6 bp, verdict) | `"fee 12 bp round trip"` (`BUY_ZONE_MAP.md:111`); `NEXT5_TESTS.md:10,21,78,80` |

#### Shared Rules Check
- **Phase split from `t-1` daily bar only:** Explicitly required (`NEXT5_TESTS.md:72`), but `no base reclaim` is undefined and `50-week SMA` (last closed weekly bar vs rolling 350d) is unstated.
- **Lockout 10d, Placebo `N >= 1000`, DEV/VAL/RECENT, CI low > 0 & DEV sign:** Covered via `shared verdict rule` (`NEXT5_TESTS.md:80`), though Test 3 omits explicit per-coin vs pooled output table specs and `RANGE`/`UP`/`DOWN`/`base` control reporting.

#### Blockers & Ambiguities Two Coders Would Read Differently
1. **BLOCKER — Undefined `no base reclaim` & `50-week SMA`:** Two coders cannot implement `post-peak bear` identically without a formal rule for `no base reclaim` and closed-weekly vs 350d SMA.
2. **Bollinger Band & oscillator parameters:** BB `(period, std_dev)` and whether *both* divergence peaks or only one must close/wick outside the upper BB are unstated; `RSI or WT` is not narrowed to one primary.
3. **Causal pivot confirmation:** `pivot-based` lacks left/right bar counts; `"confirming close"` must be the close of the `right_bars`-th bar after the second pivot high to satisfy `NEXT5_TESTS.md:16`.
4. **Stop/trail & Bybit funding coverage:** `0.5%` anchor conflict (`entry` vs `divergence high`), `divergence high` (second peak vs max of both), `2 x ATR` trailing mechanics, and whether Bybit funding covers all 20 coins across DEV (`<= 2023-12-31`).

---

### Test 4: Capitulation signature at lows (rank 4, descriptive first) (`NEXT5_TESTS.md:84-96`)

#### Parameters (SOURCED vs OURS)
| Parameter | Value in `NEXT5_TESTS.md` | Label | Source Quote & `file:line` |
|---|---|---|---|
| Signature: funding | Funding negative at the low | SOURCED | `"funding negative"` (`BUY_ZONE_MAP.md:112`) |
| Signature: OI unwind | OI down `>= 5%` over prior `7 days` | OURS (threshold); SOURCED (concept) | `"plus OI unwind"` (`BUY_ZONE_MAP.md:112`); `>= 5%` / `7 days` in `NEXT5_TESTS.md:88` |
| Signature: failed breakdown | Undercut of a swing low, close back above within `2 weeks` | SOURCED | `"undercuts a swing low, closes back above within 2 weeks"` (`BUY_ZONE_MAP.md:95`); `"failed breakdown"` (`BUY_ZONE_MAP.md:112`) |
| Data & sample | Bybit OI & funding from `2020-07`; `38` anatomy lows + new lows by same rule | SOURCED | `"Bybit OI from 2020-07; 6+ lows plus the 38 anatomy lows"` (`BUY_ZONE_MAP.md:112`) |
| Step 1 (descriptive) | Count matches; forward `1d, 3d, 7d` median return; share making lower low within `26 weeks` | SOURCED | `"forward 1d to 7d"`, `"descriptive first"` (`BUY_ZONE_MAP.md:112`); `"within 26 weeks"` (`BUY_ZONE_MAP.md:9`) |
| Step 2 (trade test) | Only if `>= 6` lows match: forward `1d to 7d` fee-net test vs placebo of `"random lows-like bars"` in same phase | SOURCED (`>= 6`, `1d to 7d`); OURS (placebo wording) | `"6+ lows"`, `"forward 1d to 7d"` (`BUY_ZONE_MAP.md:112`) |
| Today's reading | Funding positive, OI at `99.7th` percentile of `365 days` (reading only, not a sample) | SOURCED | `"Funding: Still positive"` (`BUY_ZONE_MAP.md:52`); `"Bybit OI at 99.7th percentile of 365 days"` (`BUY_ZONE_MAP.md:50`) |

#### Shared Rules Check
- **Causality (`NEXT5_TESTS.md:16, 119`):** Violated! Using `38 anatomy lows` (picked with future bars) and measuring forward returns `at the low` when `failed breakdown` confirms up to 14 days later introduces lookahead.
- **Stop (`NEXT5_TESTS.md:11`) & PASS rule (`NEXT5_TESTS.md:21`):** Step 2 has **no stop**, so `mean R` and `CI low > 0` cannot be computed. Splitting `>= 6` lows since `2020-07` into `DEV <= 2023-12-31` and `VAL >= 2024-01-01` across 5 phases leaves near-zero VAL counts without an abort rule.
- **12/6 bp costs & 10-day lockout:** Omitted from Test 4's text.

#### Blockers & Ambiguities Two Coders Would Read Differently
1. **BLOCKER — Anatomy-low & 14-day reclaim lookahead:** Both the `38 anatomy lows` selection and measuring `1d, 3d, 7d` returns from the low instead of the reclaim close leak future bars.
2. **BLOCKER — Missing stop in Step 2:** `mean R` in the shared verdict rule requires a defined `1R` stop distance.
3. **Undefined `random lows-like bars`:** Step 2's placebo population cannot be coded without a rule for `"lows-like"`.
4. **Signature & scope ambiguities:** `OI down >= 5%` (7d point-to-point vs 7d peak-to-trough), `funding negative` (single 8h print vs 24h mean), `swing low` definition, and BTC-only vs 20-coin scope are unstated.

---

### Test 5: Large-flow lead test with a proper lag (rank 5) (`NEXT5_TESTS.md:100-112`)

#### Parameters (SOURCED vs OURS)
| Parameter | Value in `NEXT5_TESTS.md` | Label | Source Quote & `file:line` |
|---|---|---|---|
| Baseline correlation | `+0.45` same window, `+0.05` next `24 h` | SOURCED | `"correlation +0.45 with the prior 24 h, +0.05 with the next 24 h"` (`BUY_ZONE_MAP.md:64`) |
| Data & cutoffs | Binance daily large-trade dumps (`>= $1M` and `>= $5M`); `11-13` files via `fetch_hourly.py`; Coinbase premium extra feature | SOURCED | `"Large flow (>= $1M...)"` / `"(>= $5M)"` (`BUY_ZONE_MAP.md:56-57`); `"Binance daily dumps (11-13 files not yet published; rerun fetch_hourly.py); Coinbase premium as an extra feature"` (`BUY_ZONE_MAP.md:113`) |
| Design | Non-overlapping windows; flow over `t`, return over `t+1 to t+24 h` and `t+1 to t+72 h`; all days | SOURCED | `"next 24 h and 72 h return versus prior flow, non-overlapping windows, all days, not only low-centred windows"` (`BUY_ZONE_MAP.md:113`) |
| Test | Rank correlation and quintile spread (top minus bottom) for next-24h and next-72h, per phase, DEV/VAL split | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:107`) |
| Placebo | Shuffled flow across days within same phase (`1000` shuffles) | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:108`) |
| Fee note | Lead-signal test only; separate fee-net trade test pre-registered if it passes | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:110`) |
| Verdict | PASS only if next-day spread holds in VAL and beats shuffle band; else KILL with number | OURS | Not in `BUY_ZONE_MAP.md` (`NEXT5_TESTS.md:112`) |

#### Shared Rules Check
- **12/6 bp costs, Stop, Lockout:** Explicitly deferred by `Fee note` (`NEXT5_TESTS.md:110`) — consistent.
- **PASS rule (`NEXT5_TESTS.md:21` vs `112`):** **Conflicts** with Shared Verdict — Test 5 omits `DEV sign agrees` and bootstrap `CI low > 0`.
- **Phase split (`NEXT5_TESTS.md:9`) & `RECENT` (`NEXT5_TESTS.md:12`):** `RECENT` is omitted from Test 5 (`NEXT5_TESTS.md:107` only names `DEV/VAL split`); shared phase-definition gaps (`base`, `post-peak bear`, precedence) still apply.

#### Blockers & Ambiguities Two Coders Would Read Differently
1. **BLOCKER — `non-overlapping windows` vs `All days` + `t+1 to t+72 h`:** Stepping daily (`All days`) makes 72h forward returns overlap by 48h, violating `non-overlapping windows` (and invalidating i.i.d. daily shuffling for 72h).
2. **BLOCKER — Verdict mismatch & missing cutoff rule:** Test 5's verdict omits `DEV sign agrees`, `CI low > 0`, which cutoff (`>= $1M` vs `>= $5M`) must pass, and the shuffle-band percentile threshold.
3. **`t+1` boundary, flow metric & universe:** Unclear if `t+1 to t+24 h` starts at the exact close of daily window `t` or 1h later; unstated whether flow is net bp of volume (`BUY_ZONE_MAP.md:56`) or USD, spot+futures or spot-only, and BTC-only or multi-coin.
4. **Quintile cutoffs & Coinbase premium:** Computing quintiles over the full sample leaks VAL into DEV (must be DEV-fitted or expanding ex-ante); how `Coinbase premium` is tested as an extra feature is unstated.
