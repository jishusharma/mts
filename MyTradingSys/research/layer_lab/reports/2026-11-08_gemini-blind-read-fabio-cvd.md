# Counts: 24 SUPPORTED, 0 UNSUPPORTED, 0 NOT_IN_DATA (24/24 SUPPORTED, 0 DIFF)

- Card: `gemini-blind-read-fabio-cvd-result-1108`
- Reader: Gemini (`gemini-3.8-flash-low`, blind read worker), 2026-11-08
- Scope: Independent blind read of `MyTradingSys/research/fabio_cvd_2026-10-30/RESULT.md` (claims and numbers) against `MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md` and `MyTradingSys/research/fabio_cvd_2026-10-30/cvd_u7_u8.py`.

---

## 1. Audit Table: RESULT.md Claims vs Code & Concepts

| Item # | Target / Section | Claim / Value in RESULT.md | Source / Computation | Status | Verification & Notes |
|---|---|---|---|---|---|
| 1 | Header: Data range & bars | Binance USD-M BTCUSDT 1m, DEV only 2022-01-01..2024-06-30 (87,552 15m bars); no VALIDATION/HOLDOUT opened | SOURCED `cvd_u7_u8.py:19,38,118-120` | SUPPORTED | Exact match: `cvd_u7_u8.py:19` sets `DEV_LAST = '2024-06'`, line 38 guards `t >= 1719792000` (2024-07-01T00:00Z). Output prints exactly `15m bars 87552  2022-01-01..2024-06-30`. No validation or holdout data accessed. |
| 2 | Header: Delta definition | Delta = 2 x taker buy volume - volume | SOURCED `cvd_u7_u8.py:4,39` | SUPPORTED | Exact match: `d = 2 * float(r[9]) - v` in `load_15m` matches standard taker delta arithmetic. |
| 3 | U7 Verdict: Price vs CVD | CVD sign lines up with first break (59% vs 35% up, all days), but box price direction alone gives 63% vs 27% | SOURCED `cvd_u7_u8.py:124-126,131-136` | SUPPORTED | Exact match: all days CVD+ up share is 142/(142+99) = 58.9% (59%), CVD- is 99/(99+187) = 34.6% (35%). Baseline box price up is 173/275 = 62.9% (63%), box price down is 68/252 = 27.0% (27%). |
| 4 | U7 Verdict: Added information | Holding price direction fixed, CVD sign adds +6 pp (up boxes) and -5 pp (down boxes) | SOURCED `cvd_u7_u8.py:131-136` | SUPPORTED | Exact match: for box price up, CVD+ gives 135/210 = 64.3% vs CVD- gives 38/65 = 58.5% (+5.8 pp -> +6 pp). For box price down, CVD+ gives 7/31 = 22.6% vs CVD- gives 61/221 = 27.6% (-5.0 pp -> -5 pp). |
| 5 | U8 Verdict: Reversal rate | Divergence lows reverse in 4h 28.5% vs 31.5% for matched controls | SOURCED `cvd_u7_u8.py:145,151-154` | SUPPORTED | Exact match: divergence reversal rate is 28.5%, distance-matched control is 31.5%. |
| 6 | U8 Verdict: Low broken rate & z-score | The low breaks more often (65.4% vs 59.2%, z about 3.4) | SOURCED `cvd_u7_u8.py:145,151-154` | SUPPORTED | Exact match: divergence broke rate is 65.4% vs matched control 59.2% (raw control 59.3%). Two-proportion pooled z-score: (0.6535 - 0.5928) / 0.01796 = 3.38 (z about 3.4). |
| 7 | U8 Verdict: Annual sign consistency | Same sign in each of 2022, 2023, 2024 | SOURCED `cvd_u7_u8.py:155-157` | SUPPORTED | Exact match: low broken rate is consistently higher for divergence vs control in all 3 years: 2022 (67.3% vs 57.5%), 2023 (65.7% vs 60.4%), 2024 (62.1% vs 58.8%). |
| 8 | U7 Table: Squeeze (C17) + | n=47, first up=26, first down=12, both/none=9, up share=68% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 26 / (26 + 12) = 68.42% (68%). |
| 9 | U7 Table: Squeeze (C17) - | n=54, first up=23, first down=24, both/none=7, up share=49% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 23 / (23 + 24) = 48.94% (49%). |
| 10 | U7 Table: All days + | n=298, first up=142, first down=99, both/none=57, up share=59% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 142 / (142 + 99) = 58.92% (59%). |
| 11 | U7 Table: All days - | n=332, first up=99, first down=187, both/none=46, up share=35% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 99 / (99 + 187) = 34.62% (35%). |
| 12 | U7 Table: Strong third + | n=95, first up=58, first down=16, both/none=21, up share=78% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 58 / (58 + 16) = 78.38% (78%). |
| 13 | U7 Table: Strong third - | n=115, first up=23, first down=70, both/none=22, up share=25% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 23 / (23 + 70) = 24.73% (25%). |
| 14 | U7 Table: Box price up + | n=257, first up=135, first down=75, both/none=47, up share=64% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 135 / (135 + 75) = 64.29% (64%). |
| 15 | U7 Table: Box price up - | n=72, first up=38, first down=27, both/none=7, up share=58% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 38 / (38 + 27) = 58.46% (58%). |
| 16 | U7 Table: Box price down + | n=41, first up=7, first down=24, both/none=10, up share=23% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 7 / (7 + 24) = 22.58% (23%). |
| 17 | U7 Table: Box price down - | n=260, first up=61, first down=160, both/none=39, up share=28% | SOURCED `cvd_u7_u8.py:128-136` | SUPPORTED | Exact match: 61 / (61 + 160) = 27.60% (28%). |
| 18 | U7 Notes: Price baseline & squeeze z | box close > open: 63% of 275; box close <= open: 27% of 252; squeeze gap 68% vs 49% (38 and 47 events) is z about 1.8 | SOURCED `cvd_u7_u8.py:124-126` | SUPPORTED | Exact match: baseline prints 63% of 275 and 27% of 252. Squeeze directional events are 38 (26 up, 12 dn) and 47 (23 up, 24 dn); pooled z = (0.6842 - 0.4894) / 0.1077 = 1.81 (z about 1.8). |
| 19 | U8 Table: Divergence (CVD lower low) | n=1469, reversal 4h=28.5%, low broken 4h=65.4%, mean 4h return=-0.006% | SOURCED `cvd_u7_u8.py:154` | SUPPORTED | Exact match: prints `1469 \| 28.5% \| 65.4% \| -0.006%`. |
| 20 | U8 Table: Control raw | n=1439, reversal 4h=31.4%, low broken 4h=59.3%, mean 4h return=+0.009% | SOURCED `cvd_u7_u8.py:154` | SUPPORTED | Exact match: prints `1439 \| 31.4% \| 59.3% \| +0.009%`. |
| 21 | U8 Table: Control distance-matched | n=1439, reversal 4h=31.5%, low broken 4h=59.2%, mean 4h return=+0.010% | SOURCED `cvd_u7_u8.py:154` | SUPPORTED | Exact match: prints `1439 \| 31.5% \| 59.2% \| +0.010%`. |
| 22 | U8 Table: 2022 yearly breakdown | div: n=431, rev=27.6%, broke=67.3%, ret=-0.030% / ctrl: n=505, rev=31.8%, broke=57.5%, ret=-0.072% | SOURCED `cvd_u7_u8.py:155-157` | SUPPORTED | Exact match: both rows print identical numbers. |
| 23 | U8 Table: 2023 yearly breakdown | div: n=711, rev=28.1%, broke=65.7%, ret=+0.001% / ctrl: n=700, rev=30.8%, broke=60.4%, ret=+0.052% | SOURCED `cvd_u7_u8.py:155-157` | SUPPORTED | Exact match: both rows print identical numbers. |
| 24 | U8 Table: 2024 yearly breakdown | div: n=327, rev=30.3%, broke=62.1%, ret=+0.009% / ctrl: n=234, rev=32.4%, broke=58.8%, ret=+0.057% | SOURCED `cvd_u7_u8.py:155-157` | SUPPORTED | Exact match: both rows print identical numbers. |

---

## 2. Conceptual Consistency Audit vs CVD_CONCEPTS.md

1. **Mapping of U7 to F-CVD2 (`Pressure builds before the breakout`)**:
   - `CVD_CONCEPTS.md:25` defines F-CVD2: *"In balance (sideways), a CVD that trends one way shows which side is loading. Falling CVD in a flat range = distribution, rising = accumulation"*.
   - `CVD_CONCEPTS.md:79` specifies U7 test design: *"In a pre-US coil (C17 events), does the CVD slope inside the box predict the break side?"*.
   - `RESULT.md:10-33` tests exactly this setup using the pre_us_squeeze definitions (box A-8h..A, BW percentile <= 20%). The finding that CVD tracks price direction and provides no independent edge is completely consistent with `CVD_CONCEPTS.md:79` and strictly within the scope computed by `cvd_u7_u8.py`.

2. **Mapping of U8 to F-CVD3 (`Absorption = CVD lower low, price at the same level`)**:
   - `CVD_CONCEPTS.md:26` defines F-CVD3: *"Absorption = CVD lower low, price at the same level ... Sellers hit hard but price does not drop, so passive buyers are taking it. Expect the failed auction to reverse"*.
   - `CVD_CONCEPTS.md:80` specifies U8 test design: *"CVD lower low with price within 0.1% of the prior low (F-CVD3): reversal rate vs matched non-divergence lows"*.
   - `RESULT.md:12,34-47` measures this directly (1469 divergence pairs vs 1439 control pairs) and finds the opposite outcome (low breaks *more* often: 65.4% vs 59.2%, reversal is lower: 28.5% vs 31.5%). The verdict in `RESULT.md` accurately describes the test results without exceeding the empirical findings of `cvd_u7_u8.py`.

3. **Limits & Decisions Transparency**:
   - `RESULT.md:48-58` explicitly notes limitations:
     - Tests bar-close 15m CVD rather than sub-bar order book footprint.
     - Swing definition (K=2 bars each side, 24h pairing) and reversal definition are OURS.
     - Squeeze subset is small (n=101 days).
     - DEV-only boundary is respected (no rows at or after 2024-07-01).
     - Baseline price direction control is documented as OURS.
   - None of the claims in `RESULT.md` goes beyond what `cvd_u7_u8.py` calculates.

---

## 3. Verdict

**COVERED**: All 24 claims and numbers in `RESULT.md` are 100% verified against `cvd_u7_u8.py` output and fully consistent with the theoretical definitions in `CVD_CONCEPTS.md`.
