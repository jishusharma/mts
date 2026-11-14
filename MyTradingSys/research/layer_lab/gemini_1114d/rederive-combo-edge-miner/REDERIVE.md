FAIL — overall study verdict ("VERDICT: FAIL"), trial count (210,684), active-now phase (MIX_L), and Top-10 ex-best-5 failure match, but exact `n` and headline `VAL net R` mismatch because `F:\MTS\data_cache\binance\combo-edge-miner-1114` is not mounted on this laptop (local `MTS_data_cache` has 19/20 coins, missing `ZEC`, col-9 taker-buy volume, Binance 8h funding, Binance daily OI, and `d200w`).

# Blind Re-derivation: combo-edge-miner-1114

- **Source spec**: [PRE_REG.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-combo-edge-miner-gemini4-1114/MyTradingSys/research/combo-edge-miner-1114_2026-11-14/PRE_REG.md) and [FORMULAS.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-combo-edge-miner-gemini4-1114/MyTradingSys/backtest/layers/FORMULAS.md) (no study code read).
- **Independent script**: [recompute.py](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-combo-edge-miner-gemini4-1114/MyTradingSys/research/layer_lab/gemini_1114d/rederive-combo-edge-miner/recompute.py) (OURS).
- **Data used**: `C:\Users\e-ngineers\MTS_data_cache\binance_spot_1d` and `binance_spot_4h` (19/20 coins; `ZECUSDT`, taker-buy volume col 9, Binance 8h funding, Binance daily OI, and `d200w` absent).

## Claim Table

| Claim | Recomputed (OURS) | Stated (SOURCED) | Source `file:line` | Status |
|---|---|---|---|---|
| Study verdict | FAIL (0/10 Top-10 pass VAL `ex-best-5 > 0`; 9/10 fail VAL CI > 0) | "VERDICT: FAIL. None of the 10 DEV-selected combinations passes the VAL gates at 12 bp" | `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:1` | MATCH |
| Total trials | 210,600 + 84 = 210,684 | "210,600; plus 84 named thinker trials = 210,684 total trials" | `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:19` | MATCH |
| VAL six-label shares (1d) | UP_E 39.2%, UP_L 19.0%, MIX_E 11.1%, MIX_L 4.0%, DOWN_E 1.3%, DOWN_L 25.4% | "UP_E 28.0% | 39.1%, UP_L 23.4% | 19.0%, MIX_E 8.2% | 11.1%, MIX_L 12.9% | 4.1%, DOWN_E 0.9% | 1.3%, DOWN_L 26.7% | 25.4%" | `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:15` | MATCH (within 0.1% coin-day rounding) |
| Active now (BTC/ETH, 2026-11-13) | BTC & ETH phase `MIX_L`; all 10 Top-10 states `false` | "BTC and ETH are in MIX_L today, so it is not active" | `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:3` | MATCH |
| Top 10 #1 (`1d L UP_E RIDE ADX_DI+VOLX`) | DEV n=109, mean=2.874; VAL n=89, mean=1.076, ex5=-0.269 | "ADX_DI+VOLX | 118 | 2.429 [1.212, 3.646] | 2.663 | 0.007 | 1.004 | 0.128 | 1.000 | 96 | 1.582 | [-0.030, 3.628] | 1.587 | -0.174" | `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:30` | MISMATCH (missing ZEC + funding) |
| Top 10 #8 (`1d L UP_E RIDE BRK5+ADX_DI+VOLX`, headline best VAL) | VAL n=73, mean=1.246, CI [-0.115, 2.933], ex5=-0.240 | "best VAL mean net R 1.788 on n=79" | `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:1` | MISMATCH (missing ZEC + funding) |
| Top 10 #7 (`1d L UP_E RIDE RSI_MOM+TREND_MA+VOLX`) | DEV n=109, mean=2.523; VAL n=74, mean=1.071, CI [0.067, 2.157], ex5=-0.033 | "RSI_MOM+TREND_MA+VOLX | 114 | 2.233 [1.066, 3.399] | 2.472 | 0.007 | 0.808 | 0.196 | 1.000 | 80 | 1.625 | [0.185, 3.461] | 1.630 | -0.008" | `MyTradingSys/research/combo-edge-miner-1114_2026-11-14/RESULT.md:36` | MISMATCH (missing ZEC + funding) |
