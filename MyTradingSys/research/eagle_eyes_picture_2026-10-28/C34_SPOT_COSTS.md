# C34: Spot Cost Re-score of Long Leads (C30 and C28)

**Verdict: NO-LEAD.**

Context: BTCUSDT public klines on Binance, DEV period 2022-01-01..2024-06-30 (HOLDOUT sealed). Spot cost model = 2 bps maker round trip, zero funding, long only (SOURCED BACKTEST_CANDIDATES.md:43, Deribit BTC_USDC Coinbase-routed); perp cost model = 10 bps taker fee round trip (fees.BINANCE_TAKER*2, SOURCED fees.py:36), with optional 2 bps slip per FORMULAS.md section 13.
Regime mix: 2022 bear (BTC -65%) C30 30m n=47 (+0.599%), C30 15m n=18 (+0.272%), C28 2h n=22 (+0.295%); 2023 range/recovery (BTC +155%) C30 30m n=26 (-0.149%), C30 15m n=15 (+0.219%), C28 2h n=32 (+0.713%); 2024 H1 bull (BTC +48%) C30 30m n=15 (+0.411%), C30 15m n=11 (+0.299%), C28 2h n=15 (+0.133%). C30 30m shows regime instability (-0.15% in 2023 range) consistent with its subsequent out-of-sample failure.

## 1. Reference DEV Leads and Spot Cost Comparison

Cost model citation: FORMULAS.md section 13 (T055 shared cost model: net = gross - fee_rt - slip_rt - funding; funding = 0 for spot). Units: returns are reported in % per trade (with 1 R = 1.0% return on unit notional / capital as standard when no stop is defined).

| Lead | n | Gross R | Perp fee-net R | Spot fee-net R | FORMULAS s13 cited | Reference / Source |
|---|---|---|---|---|---|---|
| C30: 30m buy dot <= -53 + bull div, any trend, exit X1 | 88 | +0.446% | +0.346% | +0.426% | FORMULAS s13: perp 10 bp taker vs spot 2 bp maker, 0 funding | SOURCED BACKTEST_CANDIDATES.md:39 (+0.35% net) |
| C28: 2h uptrend buy dot <= 0, exit X3 (dot after far band) | 69 | +0.554% | +0.454% | +0.534% | FORMULAS s13: perp 10 bp taker vs spot 2 bp maker, 0 funding | SOURCED BACKTEST_CANDIDATES.md:37 (+0.45% net) |
| C30 (H2): 15m buy dot <= -53 + bull div, 2h trend up, exit X1 | 44 | +0.361% | +0.261% | +0.341% | FORMULAS s13: perp 10 bp taker vs spot 2 bp maker, 0 funding | SOURCED PRE_REG_C30.md:16 (+0.261% net) |

Notes on costs:
- Perp fee-net matches committed scripts `wt_rsi_div.py` and `wt_context.py` using `fees.BINANCE_TAKER * 2` = 10 bps (0.10%).
- Spot maker fee: 2 bps (0.02%) round trip, zero funding (SOURCED BACKTEST_CANDIDATES.md:43, Deribit BTC_USDC routed to Coinbase at 2 bps maker / 5 bps taker).
- If 2 bps slippage per FORMULAS section 13 is added to perp, perp fee-net R becomes +0.326% (C30 30m), +0.434% (C28 2h), and +0.241% (C30 15m).

## 2. Validation Out-of-Sample Performance (C30_VALIDATION.md)

Carrying the pre-registered C30 VALIDATION read on 2024-07-01..2025-06-30 (SOURCED C30_VALIDATION.md:9-10):

| Hyp | Chart / rule | n | Win | Mean (perp fee-net) | Mean (spot 2 bp net) | SD | 95 % CI | Worst | p one-sided | Holm p (m=2) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 30m, any trend | 35 | 74 % | -0.066 % | +0.014 % | 1.97 | -0.720 .. +0.588 | -6.63 % | 0.578 | 0.578 | FAIL (mean <= 0) |
| H2 | 15m, 2h trend up | 22 | 73 % | +0.220 % | +0.300 % | 0.81 | -0.120 .. +0.560 | -1.45 % | 0.109 | 0.218 | INCONCLUSIVE |

Quoting C30_VALIDATION.md:
- "H1: 30m, any trend | 35 | 74 % | -0.066 % | FAIL (mean <= 0)"
- "H2: 15m, 2h trend up | 22 | 73 % | +0.220 % | INCONCLUSIVE"
- "H1 has no edge over random entries (beats 10/30 random entries, random median +0.001 %)."
- "H2 matches the DEV sign (+0.261 % DEV vs +0.220 %) but the CI includes 0 and Holm p 0.218 > 0.05: not a pass. As pre-registered, no re-tuning on VALIDATION; promotion needs the HOLDOUT read (operator's call)."

## 3. Conclusion and Verdict

**Verdict: NO-LEAD.**

1. While 2 bps maker spot fees improve DEV numbers by +0.08% across all leads, spot fee savings cannot resurrect a lead that failed validation.
2. C30 H1 (30m) failed its pre-registered VALIDATION test (-0.066% net, FAIL). Even with spot costs, its validation mean is +0.014% with a wide confidence interval including zero (-0.64% .. +0.67%) and p=0.578. The 30m row is an accounting cost check, never an edge claim.
3. C30 H2 (15m 2h-up) was INCONCLUSIVE on validation (Holm p = 0.218 > 0.05); it does not meet the pipeline promotion bar.
4. C28 (2h uptrend) is an in-sample exploratory selection from ~40 cells on DEV and has never been validated out of sample.
5. No row implies a live lead. The leads remain parked; zero live or testnet orders.
