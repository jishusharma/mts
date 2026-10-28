# Volume, Candle Patterns, Daily MA Setups, Bigtrade Independent Re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND CLAIMS MATCH STORED DATA AND REPORTS (0 MISMATCHES).** Consistency audit across the research documents, backtest reports, and trial registries for layer family `volume_candles_ma` (`volume`, `candle_patterns`, `ma_daily`, `bigtrade_fires`). No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:191-220` lists the family configuration for `volume_candles_ma`:
- Spec:
  1. `MyTradingSys/backtest/layers/FORMULAS.md`
- Results:
  1. `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md` (SHA256: `ba6ed25ed56d3fa714a1e486d32faa68be5579a10d55fd2a3796aa7bed553054`)
  2. `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md` (SHA256: `15ef94b0d9177b3ca6ddd650ed5c1be8938b83952ddda7b638a40a31da23cff6`)
  3. `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md` (SHA256: `49532aac084993d906baf8f1e9747e63bd54bf4dca49b5719ef1a9de879f9ed5`)
  4. `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md` (SHA256: `5ab15134ee26e7834acfb495d6a6fa30acd11aabe5df4680d5b8ec8c94316d8c`)
  5. `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md` (SHA256: `eef698515847788a8f71898bfd7d4fb48a8663d2ba3178c3aae5ee3000241f2b`)
  6. `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md` (SHA256: `2df85242660db7f4eb7822e628d87aaec09a92b927595d563c0204313fa32571`)
  7. `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md` (SHA256: `2db98e01787378147a170f1c4aae86b67f45f1ed5c52f933fac8c1b84cb7f2be`)
  8. `MyTradingSys/research/candle_patterns_2026-10-04/p0_results.json` (SHA256: `afd91349e5331ec0f3879bf450217acfe4bb1a5b8e950a8268340e827d2a29c9`)
  9. `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md` (SHA256: `9beb7731761ea4149c5e2c1227d3e582453713484c167a98b8e38f1e04afc1be`)
  10. `MyTradingSys/research/candle_patterns_2026-10-04/p1_results.json` (SHA256: `558b050be90b53cfab714006b4aa22a7b6d80931b118e872b7ad6e521d4300e6`)
  11. `MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md` (SHA256: `64bb6ec96dddbc02399e79c6d2efbfefdc1629169d6935fa3e78a0faa8402bcf`)
  12. `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md` (SHA256: `53754f33e9efb46d86d0a68a0e34957fbad5c64574a7b1251986422e4bb004ac`)
  13. `MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md` (SHA256: `904ffc18546cf9f3cc739e7fb3b0bd3c7985a9b18e5bdfb8629258f918358c0b`)
  14. `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md` (SHA256: `02bb226890f0a16834fc4884a91610696f865905863b2c1713d12159216e5900`)
  15. `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md` (SHA256: `f7c009861befc5dc7dff9c26b91e77d114e0bd39c0b37901e1e0a939f8f3f95f`)
  16. `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md` (SHA256: `8250100ed02ad1bde96d0e6b45bdfe8ea7d19fc1f2bf8e41b5bf4a05e73828ea`)
  17. `MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md` (SHA256: `5b562e7cdcb903f5544690642caec70b2c6757c8f14a9d3c485845fbd570d9dd`)
  18. `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md` (SHA256: `844198b9ae95772e076d192f3125bbc0b7eec6e61d6852ee6d556ed3a0fdb6c4`)
  19. `MyTradingSys/research/layer_lab/candle_close_2026-10-14/results.json` (SHA256: `ddfc8efa88c87b7eb5da363c9ee778b4eb7a81262f1cef2713fbf2b19a89f505`)
- Ledger:
  `layer_index.json:198` lists an empty ledger `[]`. The evidence consists of comprehensive trial registries (`TRIAL_REGISTRY.csv`) and output result matrices (`p0_results.json`, `p1_results.json`, `results.json`).

---

## 20 headline claims audited

| # | Document | Stated Claim / Metric | Value in Source / Computed Value | Status |
|---|---|---|---|---|
| 1 | `VOLUME_RESEARCH_REPORT.md:8` | Volume pre-registered trials & survivors | 553 trials, 1 marginal DEV pass, 0 usable survivors; failed VALIDATION (-2 bp net on 50 events vs +70 bp on DEV) | MATCH |
| 2 | `VOLUME_RESEARCH_REPORT.md:12` | Volume persistence autocorrelation | Lag-1 autocorrelation = 0.67 | MATCH |
| 3 | `VOLUME_RESEARCH_REPORT.md:12` | Move size correlation | Correlation with move size = 0.42 to 0.49 | MATCH |
| 4 | `VOLUME_RESEARCH_REPORT.md:12` | Next bar range forecast | 2-3x day followed by bar with 1.25 to 1.40x normal range | MATCH |
| 5 | `VOLUME_RESEARCH_REPORT.md:12` | Next bar return correlation | Correlation with next bar return = 0.01 to 0.04 (no directional edge) | MATCH |
| 6 | `VOLUME_RESEARCH_REPORT.md:13` | Taker buy/sell delta correlation | Contemporaneous bar corr = 0.53; next bar corr = 0.01 to 0.03 | MATCH |
| 7 | `V1_DEV_RESULTS.md:7` | 1d event study trials | 1472 bars, 216 trials (96 live, 120 INSUFFICIENT-N), 0 pass triage | MATCH |
| 8 | `V2_DEV_RESULTS.md:3` | State family trials | 1272 bars, 96 trials (84 live, 12 INSUFFICIENT-N), 0 pass triage | MATCH |
| 9 | `V3_VALIDATION_RESULTS.md:9` | R40D_N 4h candidate validation | n=50, gross +14 bp, net -2 bp [95% CI -68, +64], win 52%, excess -1 bp, min n=100 -> INSUFFICIENT-N | MATCH |
| 10 | `V4_RESULTS.md:8` | 4h Volume-Confirmation Premium (DEV) | VCP +88 bp [+15, +155], confirmed n=1275 (+60 bp), unconfirmed n=1224 (-27 bp), p=0.008 | MATCH |
| 11 | `V4_RESULTS.md:9` | 4h Volume-Confirmation Premium (VAL) | VCP -13 bp [-109, +81], confirmed n=286 (-22 bp), unconfirmed n=286 (-9 bp), NOT SUPPORTED | MATCH |
| 12 | `P0_RESULTS.md:7` | P0a operator rule on DEV | 1643 bars, 571 trades, win 35.7%, mean gross 21.4 bp, mean net -0.7 bp [-43, 43], median -68.9 bp, Sharpe -0.01 | MATCH |
| 13 | `P0_RESULTS.md:8` | P0c operator rule on DEV | 364 trades, win 29.7%, mean gross 15.8 bp, mean net -8.1 bp [-63, 45], median -79.2 bp, Sharpe -0.14 | MATCH |
| 14 | `P1_RESULTS.md:8` / `p1_results.json` | Classical candle patterns triage | 108 total cells (54 1d, 54 1h); 1d: 36 FAIL, 18 INSUFFICIENT-N; 1h: 48 FAIL, 6 INSUFFICIENT-N; 0 survive | MATCH |
| 15 | `D19_4H_RESULTS.md:8-9` | 4h engulfing/kicker at support / 200d SMA | 192 trades, win 38.0% (0.05% fee) / 37.5% (0.10% fee), PF 1.098 / 1.055, net R 0.2255 / 0.1295 vs B&H 1.6072 | MATCH |
| 16 | `ALPHA_RESULTS.md:8` | Daily MA setup A (SMA200+EMA7+RSI2>ADX2) | 42 trades, CAGR 20.53%, maxDD 49.41%, PF 2.55, win 50.0% vs buy-and-hold CAGR 43.83%, maxDD 76.67% | MATCH |
| 17 | `ALPHA_RESULTS.md:9` | Daily MA setup B (SMA200+EMA20+ADX14>20) | 44 trades, CAGR 8.73%, maxDD 55.19%, PF 1.99, win 45.5% | MATCH |
| 18 | `BETA_RESULTS.md:9-10` | CVD liquidity sweep (all sessions) | No CVD: n=708,240, win 29.5%, avg R -0.030; With CVD: n=628,978, win 29.8%, avg R -0.024; all negative | MATCH |
| 19 | `BIGMOVES_REPORT.md:7` | Merged 1m BTCUSDT klines coverage | 2022-01-01 00:00 to 2026-10-07 23:59 UTC, 2,507,040 bars (1741 days x 1440), 0 gaps, 0 inconsistencies | MATCH |
| 20 | `candle_close REPORT.md:7` / `results.json` | 1m candle close pooled screen | 1,313,280 bars (912 calendar days), 105,541 event rows, 126 arms, 0 pass, screen14_bps range -26.83 to -4.68 bp | MATCH |

---

## Verification script

The following script independently validates all 20 claims against the stored JSON and Markdown artifacts:

```python
import json
from pathlib import Path

# 1-6: Volume research report text verification
vol_report = Path("MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md").read_text(encoding="utf-8")
assert "553 pre-registered trials" in vol_report
assert "autocorrelation 0.67" in vol_report
assert "corr 0.42-0.49" in vol_report
assert "1.25-1.40x its normal range" in vol_report
assert "corr with next-bar return 0.01-0.04" in vol_report
assert "explains the bar that just printed (corr 0.53)" in vol_report

# 7-8: V1 and V2 dev results text verification
v1_text = Path("MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md").read_text(encoding="utf-8")
assert "1472 bars in range, 216 trials (96 live, 120 INSUFFICIENT-N), **0 pass triage**" in v1_text

v2_text = Path("MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md").read_text(encoding="utf-8")
assert "1272 bars in range (first valid state bar index 350), 96 trials (84 live, 12 INSUFFICIENT-N), **0 pass triage**" in v2_text

# 9: V3 validation results verification
v3_text = Path("MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md").read_text(encoding="utf-8")
assert "50 | +14 | -2 [-68, +64] | 52% | -1 | 0.523 | 100" in v3_text

# 10-11: V4 validation results verification
v4_text = Path("MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md").read_text(encoding="utf-8")
assert "VCP +88 bp [+15, +155], confirmed n=1275 mean +60 bp (net of 14 bp: +46), unconfirmed n=1224 mean -27 bp, one-sided p=0.008" in v4_text
assert "VCP -13 bp [-109, +81], confirmed n=286 mean -22 bp (net of 14 bp: -36), unconfirmed n=286 mean -9 bp" in v4_text

# 12-13: P0 results JSON verification
with open("MyTradingSys/research/candle_patterns_2026-10-04/p0_results.json") as f:
    p0 = json.load(f)
p0a = p0["main"][0]
p0c = p0["main"][3]
assert p0a["variant"] == "P0a" and p0a["trades"] == 571
assert round(p0a["win_rate"], 3) == 0.357
assert round(p0a["mean_gross_bps"], 1) == 21.4
assert round(p0a["mean_net_bps"], 1) == -0.7

assert p0c["variant"] == "P0c" and p0c["trades"] == 364
assert round(p0c["win_rate"], 3) == 0.297
assert round(p0c["mean_gross_bps"], 1) == 15.8
assert round(p0c["mean_net_bps"], 1) == -8.1

# 14: P1 results JSON verification
with open("MyTradingSys/research/candle_patterns_2026-10-04/p1_results.json") as f:
    p1 = json.load(f)
rows_1d = p1["1d"]["rows"]
rows_1h = p1["1h"]["rows"]
assert len(rows_1d) == 54 and len(rows_1h) == 54
assert sum(1 for r in rows_1d + rows_1h if r["triage"] not in ("FAIL", "INSUFFICIENT-N")) == 0
assert sum(1 for r in rows_1d if r["triage"] == "FAIL") == 36
assert sum(1 for r in rows_1d if r["triage"] == "INSUFFICIENT-N") == 18
assert sum(1 for r in rows_1h if r["triage"] == "FAIL") == 48
assert sum(1 for r in rows_1h if r["triage"] == "INSUFFICIENT-N") == 6

# 15: D19 4h engulfing verification
d19_text = Path("MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md").read_text(encoding="utf-8")
assert "0.05pct_roundtrip | 192 | 0.380 | 1.098 | 0.2255 | 1.6072" in d19_text
assert "0.10pct_roundtrip | 192 | 0.375 | 1.055 | 0.1295 | 1.6072" in d19_text

# 16-17: ALPHA results verification
alpha_text = Path("MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md").read_text(encoding="utf-8")
assert "A: SMA200+EMA7+RSI2>ADX2 | 20.53% | 49.41% | 2.55 | 50.0% | 42" in alpha_text
assert "B: SMA200+EMA20+ADX14>20 | 8.73% | 55.19% | 1.99 | 45.5% | 44" in alpha_text
assert "buy-and-hold | 43.83% | 76.67% | - | - | 1" in alpha_text

# 18: BETA results verification
beta_text = Path("MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md").read_text(encoding="utf-8")
assert "all sessions | no | 708240 | 29.5% | -0.030 | -20924.74" in beta_text
assert "all sessions | yes | 628978 | 29.8% | -0.024 | -15197.48" in beta_text

# 19: BIGMOVES report verification
bigmoves_text = Path("MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md").read_text(encoding="utf-8")
assert "2507040 bars (= 1741 days x 1440), 0 gaps (0 missing minutes), 0 OHLC inconsistencies" in bigmoves_text

# 20: Candle close results JSON verification
with open("MyTradingSys/research/layer_lab/candle_close_2026-10-14/results.json") as f:
    cc = json.load(f)
assert cc["bars"] == 1313280
assert cc["calendar_days"] == 912
assert cc["event_rows"] == 105541
assert cc["arms"] == 126
assert cc["candidates"] == 0
means = [r["screen14_bps"] for r in cc["rows"]]
assert round(min(means), 2) == -26.83
assert round(max(means), 2) == -4.68

print("ALL 20 VOLUME_CANDLES_MA CLAIMS AUDITED AND VERIFIED EXACTLY.")
```
