# Kurisko Layer Parameter Labels (`file:line` sweep)

Date: 2026-10-30  
Card: `gemini-param-labels-kurisko`  
Goal: List each numeric parameter default in `MyTradingSys/backtest/layers/kurisko` code, find its source (analyst extract, FORMULAS.md, or none) and label SOURCED (quote + path) or OURS. Report only; no verdicts.

## Summary

- **Total numeric parameters / structural constants swept**: 12
- **SOURCED count**: 6
- **OURS count**: 5
- **OPERATOR-HYPOTHESIS count**: 1
- **UNLABELED count**: 0

---

## 1. Parameter and Constant Inventory (`layers/kurisko/`)

| Parameter / Constant | File:Line (Definition) | File:Line (Code Usage) | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `enabled` | `layers/kurisko/params/kurisko_default.json:4` | `layers/kurisko/quad_rotation.py:1` | `false` | OURS | Flag-gated default OFF (alert-only layer, `quad_rotation.py:1`). |
| `band_1` | `layers/kurisko/params/kurisko_default.json:30` | `layers/kurisko/quad_rotation.py:25` | `(9, 3)` | SOURCED | Sourced quote / spec row: `KURISKO_SPEC.md:s3` row Stochastic 1 (S4), `(9, 3)`. |
| `band_2` | `layers/kurisko/params/kurisko_default.json:39` | `layers/kurisko/quad_rotation.py:25` | `(14, 3)` | SOURCED | Sourced quote / spec row: `KURISKO_SPEC.md:s3` row Stochastic 2 (S4), `(14, 3)`. |
| `band_3` | `layers/kurisko/params/kurisko_default.json:48` | `layers/kurisko/quad_rotation.py:25` | `(40, 4)` | OURS | Lookback 40 is SOURCED: R1 ("These are 40 candles and these are 60 candles", char 21291); smoothing `d=4` is OURS adopted default from slide S4 (not in spoken words; `KURISKO_SPEC.md:s5 gap 1`). |
| `band_4` | `layers/kurisko/params/kurisko_default.json:56` | `layers/kurisko/quad_rotation.py:25` | `(60, 10)` | SOURCED | Sourced quote / spec row: `KURISKO_SPEC.md:s3` row Stochastic 4 (S4 Full Stoch `(60,10,10)`; S3 `(60,10)`; R1 "60 candles") with `d=10`. |
| `line` | `layers/kurisko/params/kurisko_default.json:65` | `layers/kurisko/stoch_core.py:5,37` | `"D"` | SOURCED | Sourced quote: R8 "here I'm using the D line. And the D line is the signal line"; `D = SMA_d(raw %K)` (`FORMULAS.md:s24`). |
| `level_lo` | `layers/kurisko/params/kurisko_default.json:70` | `layers/kurisko/quad_rotation.py:27,85,96` | `20` | SOURCED | Sourced quote: R2 "all of these bands get oversold below 20" (char 20846); `KURISKO_SPEC.md:s3` Levels (S4, S2). |
| `level_hi` | `layers/kurisko/params/kurisko_default.json:75` | `layers/kurisko/quad_rotation.py:27,87,96` | `80` | SOURCED | `KURISKO_SPEC.md:s3` Levels 20/80 (S4, S2); used by the short mirror. |
| `turn_rule` | `layers/kurisko/params/kurisko_default.json:80` | `layers/kurisko/quad_rotation.py:77` | `fast[t] > fast[t-1]` | OURS | No source defines the number for "turn back up" (R3 "visual confirmation", `KURISKO_SPEC.md:s5 gap 3`). |
| `short_side` | `layers/kurisko/params/kurisko_default.json:85` | `layers/kurisko/quad_rotation.py:77,87` | `all four > level_hi and fast falls` | OURS | Marked NO-SOURCE: trader never states "all four above 80" (`KURISKO_SPEC.md:s5 gap 6`; R10 only states the same goes for the downside). |
| `rsi_bands` | `layers/kurisko/params/kurisko_default.json:90` | `layers/kurisko/quad_rotation.py:26,54,63` | `[(9,0), (14,0), (40,0), (60,0)]` | OPERATOR-HYPOTHESIS | Operator hypothesis from memory ("4 RSI with params"); "RSI" occurs 0 times in Kurisko video S8 (`KURISKO_SPEC.md:s4`). |
| `stoch_slow` | `layers/kurisko/stoch_core.py:37` | `layers/kurisko/stoch_core.py:39-40` | `slow = 1` | OURS | Default un-slowed stochastic calculation; slowing variant `(60,10,10)` is a trial parameter (`FORMULAS.md:s24`). |

---

## 2. Details and Observations

1. **Parameter Management**:
   - Kurisko Quad Rotation parameters are stored in `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json` and consumed directly by `quad_rotation.py`.
   - The parameters are classified per rule citations into SOURCED quotes, OURS mechanical defaults, or OPERATOR-HYPOTHESIS variations.
2. **Trader Sourced vs Repo Engineering**:
   - The 4 Stochastic lookback periods `(9, 14, 40, 60)`, signal line selection (`D line`), and oversold/overbought levels (`20 / 80`) are explicitly SOURCED from John Kurisko's TA presentation (`extracts/processed/kurisko/QUAD_ROTATION.md`).
   - The specific smoothing factor for the third band (`d=4`), the numeric definition of a "turn" (`fast[t] > fast[t-1]`), and the RSI alternative arm are engineered choices (`OURS` / `OPERATOR-HYPOTHESIS`).
