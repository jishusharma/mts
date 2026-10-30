# Parameter Labels Audit: turn_of_candle

Audit of numeric parameter defaults in `MyTradingSys/backtest/layers/turn_of_candle/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `quarter period` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3` | `15` | `SOURCED` | Shanaev, Vasenin, Stepanov, *Heliyon*, PMC10015199 (T1): returns concentrate at opening of 15-minute candles; `FORMULAS.md` s16 |
| `turn minute` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:36` | `0` | `SOURCED` | Shanaev et al. PMC10015199: candle opening minute (minutes 0, 15, 30, 45 of the hour) |
| `lead_minutes` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:59` | `1` | `OURS` | Lead time before candle open: `FORMULAS.md` s16: "at bars with `mq == 15 - lead_minutes`... enter just before candle opens" |
| `side` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:59` | `"long"` | `OURS` | Direction of effect is not stated in source paper; `FORMULAS.md` s16: "direction of the effect is NOT stated in the report, so both are grid-searched IS only" |
| `minute ms divisor` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3` | `60000` | `SOURCED` | Standard millisecond constant for 1 minute |
