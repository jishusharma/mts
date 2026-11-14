# REPORT: NK RSI / Hilega Milega on crypto perps (edge-nk-rsi-hilega-1113)

Pre-registered in PRE_REG.md (commit dc470f9f0, before any outcome). 10 Bybit USDT perps, 5m 2020..2026-11, fees 2 x BINANCE_TAKER = 10 bp RT. Raw per-cell numbers: results.csv, per-symbol VALIDATION: persym_validation.json. No tuning on any split.

**Verdict: R1 FAIL, R2 FAIL, R3 FAIL (closest, still not a pass), R4 FAIL. 0 of 42 cells pass; 0 survive BH 10% on VALIDATION.**

| Rule | VALIDATION n | best cell fee-net mean | 95% CI | note |
|---|---|---|---|---|
| R1 session-close RSI extreme (CONT, his gap logic) | 297-349 per cell | +0.30% (00UTC, 8h) | -0.46%..+1.11% | CI spans 0; REV (mirror) mostly negative; DEV/RECENT signs flip across cells |
| R2 Hilega flip + daily filter, 10m/15m | 3.3k-13.7k | -0.07% (15m SHORT) | -0.15%..+0.01% | gross edge ~0 (+0.00..+0.03%), fees alone make every cell negative; 4/4 net-negative in all 3 splits |
| R3 R1 AND 5m+10m Hilega agree | 123-181 | +1.16% (00UTC CONT 8h) | -0.15%..+2.41%, p=0.047 | beats placebo but fails BH (1/42 needs p<=0.0024), RECENT mean -0.17%, n=123 |
| R4 daily Hilega + SMA20 / weekly engulfing | 205 long / 183 short | +5.28% long | -2.5%..+15.7% | long = bull-market beta: time-shift placebo p95 is +6.8%, higher than the rule; short -0.77% |

Reading: the 70/30 zone alone has no continuation or reversal signal at 1/4/8h after 00:00 or the US close. Adding his 5m+10m confirm raises n down and the means up, the usual small-sample look; one cell reaches p=0.047 uncorrected and is not significant after 42 cells nor in RECENT. R2 is a fee-bleed (10-14k trades, ~0 gross). R4 VALIDATION window was a +70% BTC bull; the rule just rode beta (placebo equal or better; RECENT long -1.1%).
Caveats: Hilega formula is OURS-EXTERNAL (NK never states it); crypto has no gap/close so R1/R3 are weak ports of his claim, not tests of it on Nifty; 1h/4h/8h horizons and event times are OURS. RECENT/DEV tables are in results.csv.
Best next test (if any): R3 CONT at 00:00 UTC 8h is the only cell with positive net mean in VALIDATION across both CI-ish and placebo; replicate it on a fresh window (RECENT n=198, mean -0.17%, so expect fail) or on 4h/1d close of the extreme alone with maker fees. Not recommended; drop NK-RSI from the stack.
