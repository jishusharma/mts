# Pizzino Layer Parameter Labels (`file:line` sweep)

Date: 2026-10-30  
Card: `gemini-param-labels-pizzino`  
Goal: List each numeric parameter default in `MyTradingSys/backtest/layers/pizzino` code, find its source (analyst extract, FORMULAS.md, or none) and label SOURCED (quote + path) or OURS. Report only; no verdicts.

## Summary

- **Total numeric parameters / structural constants swept**: 32
- **SOURCED count**: 14
- **OURS count**: 18
- **UNLABELED count**: 0

---

## 1. Parameter and Constant Inventory (`layers/pizzino/`)

| ID | Parameter / Constant | File:Line (Code) | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| P01 | Trend state set | `layers/pizzino/pizzino_indicators.py:52` | 3 states (`up (+1)`, `down (-1)`, `neutral (0)`) | SOURCED | Sourced quote: "up on the one-day one-bar ... down on the mid-term ... neutral on the high-term" (`MyTradingSys/research/pizzino_layer_2026-10-27/method_extraction.md:36`; `SPEC.md:46,130`). |
| P02 | Number of nested degrees | `layers/pizzino/pizzino_indicators.py:67,72` | `3` degrees (1-bar, 2-bar, 3-bar) | SOURCED | Sourced quote: "one-day one-bar, two-bar, three-bar" (`method_extraction.md:22,36`; `SPEC.md:46,131`). |
| P03 | Confluence condition | `layers/pizzino/pizzino_indicators.py:68` | `abs(conf) == 3` | SOURCED | Sourced quote: "confluence across multiple time frames just showing the strong downward bias" (`method_extraction.md:22,29`; `SPEC.md:46,132`). |
| P04 | 1-bar lead indicator | `layers/pizzino/pizzino_indicators.py:72` | Lead flag exists (1-bar turns first) | SOURCED | Sourced quote: 1-bar turn is "always a precursor" (`method_extraction.md:43,50`; `SPEC.md:46,133`). |
| P05 | Bar-count signal length | `layers/pizzino/pizzino_indicators.py:100` | `3` bars | SOURCED | Sourced quote: "three bars up from the low", "three in a row from a significant turning point" (`method_extraction.md:82`; `SPEC.md:67,134`). |
| P06 | Bar-count direction condition | `layers/pizzino/pizzino_indicators.py:106-107` | `HH + HL` (up) / `LH + LL` (down) | SOURCED | Sourced quote: "higher high, higher low" (`method_extraction.md:82,96`; `SPEC.md:67,135`). |
| P07 | Turning point significance | `layers/pizzino/pizzino_indicators.py:87` | Significant turning point required | SOURCED | Sourced quote: turning point "generally means all-time high, but not always" (`method_extraction.md:82,89`; `SPEC.md:67,136`). |
| P08 | Permitted timeframes | `layers/pizzino/pizzino_indicators.py:1` | `D`, `3D`, `W` | SOURCED | Sourced quote: used on 3-day and weekly bars as well as daily (`method_extraction.md:96,110`; `SPEC.md:67,137`). |
| P09 | 50% line definition | `layers/pizzino/pizzino_indicators.py:117` | `mid = (PH + PL) / 2` | SOURCED | Sourced quote: "Top, bottom, halfway through", midpoint of the prior major run (`method_extraction.md:133,154`; `SPEC.md:85,138`). |
| P10 | 50% line strength regime | `layers/pizzino/pizzino_indicators.py:121` | `close > mid` strong, `< mid` weak | SOURCED | Sourced quote: above 50% is strong half, below is weak half (`method_extraction.md:126`; `SPEC.md:85,139`). |
| P11 | Pivot breakout confirmation | `layers/pizzino/pizzino_indicators.py:148` | Close-beyond confirmation required | SOURCED | Sourced quote: "higher time frame closes above those pivot points" (`method_extraction.md:73,184`; `SPEC.md:95,140`). |
| P12 | Retest outcome reading | `layers/pizzino/pizzino_indicators.py:160` | `hold` continuation, `fail` reversal | SOURCED | Sourced quote: hold = continuation; retest from underneath is weak (`method_extraction.md:214,235`; `SPEC.md:95,141`). |
| P13 | Target selection | `layers/pizzino/pizzino_indicators.py:173,176` | Nearest confirmed opposing pivot | SOURCED | Sourced quote: "look up to that next pivot point where price is likely going to rally to next" (`method_extraction.md:66`; `SPEC.md:113,142`). |
| P14 | Invalidation level | `layers/pizzino/pizzino_indicators.py:171` | Stop at last swing extreme `PL(1)` | SOURCED | Sourced quote: invalidation is a "change in trend beneath $88" / swing bottom (`method_extraction.md:161,205`; `SPEC.md:113,143`). |
| P15 | Swing degree lookbacks | `layers/pizzino/pizzino_indicators.py:18,41` | `n = 1, 2, 3` for degrees 1, 2, 3 | OURS | Discretization of "1-bar, 2-bar, 3-bar" swing size (`SPEC.md:19,144`, V-n). |
| P16 | Fractal strictness | `layers/pizzino/pizzino_indicators.py:22,25` | Strict inequalities both sides | OURS | Strict inequality choice on fractal window (`SPEC.md:18,145`, V-frac). |
| P17 | Pivot alternation convention | `layers/pizzino/pizzino_indicators.py:29` | Keep extreme on duplicate pivot kinds | OURS | Tie-breaking rule for alternating pivots (`SPEC.md:18,146`). |
| P18 | Trend state formula | `layers/pizzino/pizzino_indicators.py:60,62` | Close beyond last swing low/high | OURS | Algorithmic implementation of Gann Swing Pro (`SPEC.md:47,147`, V-state). |
| P19 | Lead window `L` | `layers/pizzino/pizzino_indicators.py:81` | `L = 5` bars | OURS | Maximum bars elapsed for 1-bar lead status (`SPEC.md:47,148`, V-L). |
| P20 | Significance window `W` | `layers/pizzino/pizzino_indicators.py:90` | `W = 50` bars | OURS | Lookback window for significant turning point (`SPEC.md:68,149`, V-W). |
| P21 | Degree of turning point `T` | `layers/pizzino/pizzino_indicators.py:96` | Degree `3` | OURS | Degree of pivot selected for bar-count origin (`SPEC.md:68,150`, V-T). |
| P22 | Major-run degree `dm` | `layers/pizzino/pizzino_indicators.py:117` | Degree `3` | OURS | Degree of pivots bounding the 50% midpoint leg (`SPEC.md:86,151`, V-dm). |
| P23 | Break confirmation consecutive closes | `layers/pizzino/pizzino_indicators.py:141` | `N = 2` closes | OURS | Consecutive closes required to confirm a level break (`SPEC.md:96,152`, V-N). |
| P24 | Retest touch tolerance | `layers/pizzino/pizzino_indicators.py:141` | `tol = 0.005` (0.5%) | OURS | Retest touch band margin (`SPEC.md:96,153`, V-tol). |
| P25 | Retest window | `layers/pizzino/pizzino_indicators.py:141` | `R = 20` bars | OURS | Maximum window to observe retest after breakout (`SPEC.md:96,154`, V-R). |
| P26 | Entry confluence threshold | `layers/pizzino/pizzino_indicators.py:68` | `conf >= +2` (long) / `-2` (short) | OURS | Entry filter confluence score threshold (`SPEC.md:114,155`, V-conf). |
| P27 | Minimum Reward/Risk `RRmin` | `layers/pizzino/pizzino_indicators.py:166` | `rr_min = 1.0` | OURS | Minimum acceptable reward-to-risk ratio (`SPEC.md:114,156`, V-RR). |
| P28 | Fallback target multiple | `layers/pizzino/pizzino_indicators.py:166,174,177` | `fallback_r = 2.0` | OURS | Target distance when no confirmed opposing pivot exists (`SPEC.md:114,157`, V-tgt). |
| P29 | Time stop duration | `layers/pizzino/pizzino_indicators.py:111` | `TS = 20` bars | OURS | Maximum trade holding period in bars (`SPEC.md:114,158`, V-TS). |
| P30 | Three-bar count filter | `layers/pizzino/pizzino_indicators.py:110` | Off by default (`B = 5` bars) | OURS | Optional entry confluence filter (`SPEC.md:114,159`, V-B). |
| P31 | Daily session boundary | `layers/pizzino/pizzino_indicators.py:9` | `00:00 UTC` | OURS | Daily bar boundary convention for 24/7 crypto (`SPEC.md:124,160`). |
| P32 | Base chart timeframe | `layers/pizzino/pizzino_indicators.py:9` | `1D` (Daily) | OURS | Primary observation timeframe (`SPEC.md:124,161`, V-tf). |

---

## 2. Details and Observations

1. **Separation of Concerns**:
   - Jason Pizzino's method (`bar_count_from`, 3-bar directional sequence from major high/low) and Michael Pizzino's method (`swing_state`, 1-bar/2-bar/3-bar nested trend structure and 50% level) are implemented as isolated analytical modules in `pizzino_indicators.py` per `SPEC.md:0`.
2. **Trader Sourced vs Repo Engineering**:
   - 14 parameters/concepts (P01–P14) represent direct quotations from Jason and Michael Pizzino (3-bar count, 50% midpoint strength line, next-pivot targets, structural trend states).
   - 18 parameters (P15–P32) represent repo-engineered discretizations (fractal degree values $n \in \{1, 2, 3\}$, break confirmation $N=2$, retest tolerance $0.5\%$, time stop $TS=20$, and fallback target $2.0R$), each mapped to an explicit trial-ledger identifier (`V-n`, `V-tol`, `V-N`, etc.).
