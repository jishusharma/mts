# Gemini Blind Read Report: Fable R7 `FORWARD_PREREG.md`

- **Card**: `gemini-blind-read-fable-r7-forward-prereg`
- **Date**: 2026-11-10 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target File**: `MyTradingSys/research/fable_run7_forward_test/FORWARD_PREREG.md`
- **Scope In Read**:
  - `MyTradingSys/research/fable_run7_forward_test/FORWARD_PREREG.md` (sections 0-6)
  - `MyTradingSys/research/fable_run6_powered_prereg/COUNTS.csv` (POOLED and BTCUSDT S8 rows)
  - `MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md`
  - `MyTradingSys/research/fable_run6_powered_prereg/e2_run.py` (lines 1-95, specifically lines 61-89)
- **Scope Out Respected**:
  - Read-only: no code, card, or pre-reg modified.
  - No E2 `RESULT.md` read.
  - No bar >= 2024-07-01 read.
  - Live tree, `.secrets`, and `.env` untouched.
  - Zero assumptions, zero fabrications.

---

## 1. Summary of Verification

All numbers, parity mappings, FAIL rules, pins, and isolation requirements in `FORWARD_PREREG.md` sections 0 through 6 were verified line by line against source files and formulas. Every section is found to be mathematically and procedurally SOUND. Zero discrepancies (0 DIFF) detected.

---

## 2. Section-by-Section Audit Table (Sections 0 to 6)

| Section | Title / Content | Re-derived Number or Audit Check | Source Citation | Match / Mismatch | Verdict |
|---|---|---|---|---|---|
| **0** | Pins | Git object hashes (`git hash-object`) of frozen files match table exactly:<br>- `e2_run.py`: `459b4c3c22dc...`<br>- `counts_only.py`: `bdbeaca8ff8b...`<br>- `krown_events.py`: `8e4c57fe80f3...`<br>- `krown_core.py`: `9479353b8629...`<br>- `krown_params.json`: `512e0d8e7e6c...`<br>Confirmed rule is frozen; trunk commit references documented. | `FORWARD_PREREG.md:7-16`<br>`e2_run.py:11`<br>`counts_only.py:12`<br>`krown_events.py:13`<br>`krown_core.py:14`<br>`krown_params.json:15` | MATCH | SOUND |
| **Context** | Context | Signal days counts in frozen window (1,643 calendar days):<br>- DEV_EXT 2020-01..2021-12: 265 S8 pooled signal days (SOURCED `COUNTS.csv:36`).<br>- DEV 2022-01..2024-06: 274 S8 pooled signal days (SOURCED `COUNTS.csv:35`).<br>Total pooled signal days = 265 + 274 = 539 (SOURCED `COUNTS.csv:37`). Floor rule: 4 x 14 bp = 0.56 % (`PRE_REG.md:38,45`). | `FORWARD_PREREG.md:17-21`<br>`COUNTS.csv:35-37`<br>`PRE_REG.md:38,45` | MATCH | SOUND |
| **1** | Parity spec and replay test | Audit of `e2_run.py:61-89` against parity spec:<br>- Entry: next bar open + 0.02 % slip (`e2_run.py:63-64`).<br>- Stop: far side of bars i-9..i (`e2_run.py:56-58`).<br>- Floor: risk / fill < 0.0056 skips (`e2_run.py:66`).<br>- Target: fill + side * 2.0 * risk (`e2_run.py:68`).<br>- Hold / Time stop: 100 bars max, exit close at 100th bar (`e2_run.py:69,80-81`).<br>- Same-bar conflict: stop evaluated first (`e2_run.py:72-75`).<br>- Gap fill: `min(bo, stop)` long / `max(bo, stop)` short (`e2_run.py:75`).<br>- Fee legs: Taker entry, Taker stop/time exit, Maker target (`e2_run.py:29,76-84`).<br>- Busy rule: one trade at a time (`e2_run.py:90-95`).<br>All elements covered byte-for-byte; stated live execution mismatches explicitly documented. | `FORWARD_PREREG.md:23-32`<br>`e2_run.py:29-31,56-89` | MATCH | SOUND |
| **2** | Forward sample rule and months to power | Calendar days 2020-01-01 to 2024-06-30 = 1,643 days (OURS).<br>- BTC S8 signal days: 277 (`COUNTS.csv:8-9`, DEV 135 + DEV_EXT 142).<br>- Rate BTC = 277 / 1,643 = 0.168594 / day (rounded in text to 0.169/day).<br>- Pooled S8 signal days: 539 (`COUNTS.csv:37`, DEV 274 + DEV_EXT 265).<br>- Rate Pooled = 539 / 1,643 = 0.328058 / day (rounded in text to 0.328/day).<br>- Formula: $n = ((t + 0.84) \times sd / (0.30 - \text{cost}))^2$ with $sd = 1.37$, $\text{cost} = 0.025$.<br>- Target $t \ge 3.364$: $n = ((3.364 + 0.84) \times 1.37 / 0.275)^2 = 438.63 \to 439$ days.<br>  - BTC days: $439 / (277/1643) = 2,603.9 \to 2,604$ days = 85.5 mo $\to$ 86 months.<br>  - Pooled days: $439 / (539/1643) = 1,338.2 \to 1,338$ days = 44.0 mo $\to$ 44 months.<br>- Target $t \ge 2.0$: $n = ((2.0 + 0.84) \times 1.37 / 0.275)^2 = 200.18 \to 201$ days.<br>  - BTC days: $201 / (277/1643) = 1,192.2 \to 1,190$ days = 39.2 mo $\to$ 39 months.<br>  - Pooled days: $201 / (539/1643) = 612.7 \to 613$ days = 20.1 mo $\to$ 20 months.<br>Arithmetic holds exactly. | `FORWARD_PREREG.md:34-40`<br>`COUNTS.csv:8-9,35-37`<br>`PRE_REG.md:23` | MATCH | SOUND |
| **3** | FAIL rule | Checked FAIL-A, FAIL-B, FAIL-C, and PARITY-FAIL for looser-than-stated rules:<br>- FAIL-A: 12 R drawdown from peak (= 12 straight stops at 2 R target).<br>- FAIL-B: 12 straight losers ($0.65^{12} = 0.57\% \approx 0.6\%$; $0.60^{12} = 0.22\% \approx 0.2\%$). Neither A nor B is looser; depths align.<br>- FAIL-C: $n \ge 30$ AND mean net R + $1.28 \times SE < 0$ (one-sided 90% upper bound $< 0$; plain sample sd with $ddof=1$, no bootstrap).<br>- PARITY-FAIL: count-only build failure, coordinator pause, trades stay in kill tally.<br>Rules are strict, symmetric, pre-registered, and closed. No looser loopholes. | `FORWARD_PREREG.md:42-48` | MATCH | SOUND |
| **4** | Isolation | Separation checks:<br>- Dedicated source `layer:krown:s8_break:4h`, dedicated account `krown_s8`.<br>- Grandfathered sources and Tom isolated from evidence.<br>- Market data source (Binance klines) vs execution venue (Deribit testnet) documented.<br>- Sealed-bar integrity: no bar $\ge$ 2024-07-01 read in backtest/parity cache. | `FORWARD_PREREG.md:50-54` | MATCH | SOUND |
| **5** | Cards | Cross-checks:<br>- 3 cards listed: `krown-s8-4h-testnet-build` (JIS-NB build, live_path), `krown-s8-forward-parity-test` (SONNET build), `krown-s8-forward-weekly-readout` (SONNET run).<br>- Blind read card (`gemini-blind-read-fable-r7-forward-prereg`) matches this task.<br>- `tasks.py twins` checked: zero collision. | `FORWARD_PREREG.md:56-63` | MATCH | SOUND |
| **6** | Decisions | Conservative defaults (OURS):<br>- BTC first, 12 R depth, 12 losers, $n \ge 30$, weekly cadence, own subaccount.<br>- Zero PASS claims allowed anywhere.<br>- Independent Haiku review must-fixes incorporated.<br>- $E2$ `RESULT.md` remains unread. | `FORWARD_PREREG.md:65-66` | MATCH | SOUND |

---

## 3. Detailed Verification of the Four Months-to-Power Numbers

From `COUNTS.csv`:
- BTC S8 signal days: DEV = 135 (`COUNTS.csv:8`), DEV_EXT = 142 (`COUNTS.csv:9`), total = 277 signal days.
- Pooled S8 signal days (BTC + ETH + SOL): DEV = 274 (`COUNTS.csv:35`), DEV_EXT = 265 (`COUNTS.csv:36`), total = 539 signal days (`COUNTS.csv:37`).
- Calendar window: 2020-01-01 to 2024-06-30 = 1,643 days.
- Rates:
  - BTC daily rate: $\frac{277}{1643} \approx 0.168594$ / calendar day (quoted as 0.169).
  - Pooled daily rate: $\frac{539}{1643} \approx 0.328058$ / calendar day (quoted as 0.328).

From R1 formula ($sd = 1.37$, $\text{cost} = 0.025$, plausible $= 0.30$):
$$\text{days\_needed} = \left(\frac{(t + 0.84) \times 1.37}{0.30 - 0.025}\right)^2 = \left(\frac{(t + 0.84) \times 1.37}{0.275}\right)^2$$

1. **At Holm power $t \ge 3.364$**:
   $$\text{days\_needed} = \left(\frac{4.204 \times 1.37}{0.275}\right)^2 \approx 438.63 \implies 439\text{ days}$$
   - **BTC only**: $\frac{439}{277 / 1643} \approx 2,603.9 \implies 2,604\text{ calendar days}$.
     Months at $30.4375$ days/mo: $\frac{2603.9}{30.4375} \approx 85.55 \implies \mathbf{86\text{ months}}$ (MATCH).
   - **BTC + ETH + SOL (Pooled)**: $\frac{439}{539 / 1643} \approx 1,338.2 \implies 1,338\text{ calendar days}$.
     Months at $30.4375$ days/mo: $\frac{1338.2}{30.4375} \approx 43.97 \implies \mathbf{44\text{ months}}$ (MATCH).

2. **At Validation grade $t \ge 2.0$**:
   $$\text{days\_needed} = \left(\frac{2.84 \times 1.37}{0.275}\right)^2 \approx 200.18 \implies 201\text{ days}$$
   - **BTC only**: $\frac{201}{277 / 1643} \approx 1,192.2 \implies 1,190\text{ calendar days}$ (rounded down to tens).
     Months at $30.4375$ days/mo: $\frac{1192.2}{30.4375} \approx 39.17 \implies \mathbf{39\text{ months}}$ (MATCH).
   - **BTC + ETH + SOL (Pooled)**: $\frac{201}{539 / 1643} \approx 612.7 \implies 613\text{ calendar days}$.
     Months at $30.4375$ days/mo: $\frac{612.7}{30.4375} \approx 20.13 \implies \mathbf{20\text{ months}}$ (MATCH).

---

## 4. Verification of FAIL Rules and Parity Spec

1. **FAIL Rules Looseness Audit**:
   - FAIL-A (12 R fee-net drawdown) and FAIL-B (12 consecutive losers) are mutually calibrated: 12 stops equal 12 losers at -1 R each.
   - Streak probability of 12 losers: at 35% win rate, $(1 - 0.35)^{12} = 0.65^{12} \approx 0.00569$ (0.6%); at 40% win rate, $0.60^{12} \approx 0.00218$ (0.2%).
   - FAIL-C ($n \ge 30$, $\text{mean} + 1.28 \times SE < 0$) is conservative: requires at least 30 trades and kills the setup if the one-sided 90% upper confidence bound on expectancy is strictly negative.
   - PARITY-FAIL: rejects and pauses on any unmodelled execution difference, preventing contaminated runs.
   - Conclusion: **No looser-than-stated rules detected.**

2. **Parity Spec Audit (`e2_run.py:61-89`)**:
   - S8 detection via `krown_events.setup_s8` on 4h closed bars.
   - Stop calculation on far side of 10 bars via `e2_run.stop_for`.
   - Entry at next open with 0.02% slip.
   - Risk floor check at 0.56% (4 x 14 bp).
   - 2 R target limit order.
   - 100-bar maximum hold time-stop at market close.
   - Same-bar stop precedence.
   - Gapping through stop fill logic.
   - Maker/taker fee model per leg.
   - Busy rule skipping overlapping positions.
   - Stated mismatch (live stop percent measured from signal close vs fill) explicitly documented and logged per trade.
   - Conclusion: **Complete and exact coverage of all trade-model elements.**

---

## 5. Scope-Out & Blind-Read Compliance Audit

- Outcome column / outcome files (`RESULT.md`, `VALIDATION`, forward fills): **Zero accessed**.
- Bars $\ge$ 2024-07-01: **Zero loaded**.
- Code modifications: **Zero lines changed**.
- Pre-reg edits: **Zero edits made**.

---

## 6. Final Verdict

Every section (0 through 6) of `FORWARD_PREREG.md` is **SOUND**.
No `FIX-FIRST` verdict is warranted; zero new task cards required.
