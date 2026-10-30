# Pitchfork Layer Parameter Labels (`file:line` sweep)

Date: 2026-10-30  
Card: `gemini-param-labels-pitchfork`  
Goal: List each numeric parameter default in `MyTradingSys/backtest/layers/pitchfork` code, find its source (analyst extract, FORMULAS.md, architecture spec, or none), and label SOURCED (quote + path) or OURS. Report only; no verdicts.

## Summary

- **Total numeric parameters / structural constants swept**: 19
- **SOURCED count**: 9
- **OURS count**: 10
- **UNLABELED count**: 0

---

## 1. Parameter and Constant Inventory (`layers/pitchfork/`)

| Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|
| Default pitchfork variant | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:59` | `variant = PitchforkVariant.STANDARD` | SOURCED | Dr. Alan Hall Andrews (1900-1985), private Babson Action-Reaction Course (1960-1975) (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`). |
| Schiff time displacement ratio | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:72` | `0.5` | SOURCED | Jerome Schiff formulation: origin shifted 50% in time towards P1: $t_{0,\text{Schiff}} = \frac{t_0 + t_1}{2}$ (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128`). |
| Schiff price displacement ratio | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:73` | `0.5` | SOURCED | Jerome Schiff formulation: origin shifted 50% in price towards P1: $p_{0,\text{Schiff}} = \frac{p_0 + p_1}{2}$ (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128`). |
| Modified Schiff price displacement ratio | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:77` | `0.5` | SOURCED | Modified Schiff formulation: shifts vertical midpoint between P0 and P1 ($p_0 + 0.5(p_1 - p_0)$) maintaining original $t_0$ (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:130-136`). |
| Midpoint time construction | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:82` | `(t1 + t2) / 2.0` | SOURCED | Geometric vector definition of Andrews Median Line midpoint vector $M = \frac{P_1 + P_2}{2}$ (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`). |
| Midpoint price construction | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:83` | `(p1 + p2) / 2.0` | SOURCED | Geometric vector definition of Andrews Median Line midpoint vector $M = \frac{P_1 + P_2}{2}$ (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`). |
| Warning line multiplier spacing | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:145, 149` | `level * half_width` | SOURCED | Timothy Morge (2002) warning line formulation ($WL_1, WL_2, WL_3$ spaced by channel width / half-width) (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:144-152`). |
| Inner quartile line factor | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:153, 157` | `0.5 * offset` | SOURCED | Timothy Morge (2002) quartile parallel lines (25% and 75% inner parallels) (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:144-152`). |
| Hagopian approach progress threshold | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:202, 205` | `0.15` | OURS | Minimum approach threshold (15% distance traveled towards ML from origin tine before rollover qualifies as a Hagopian failure); repo choice. |
| Auto-Schiff slope switch toggle | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:313` | `auto_schiff: bool = True` | OURS | Automatic slope-steepness fallback toggle from Standard to Modified Schiff; repo engineering choice. |
| Auto-Schiff max slope ratio | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:314, 328` | `max_slope_bars_ratio: float = 1.0` | OURS | Relative slope steepness ratio for triggering auto Schiff switch (`pitchfork_detector.py:328`). |
| Log scale pitchfork toggle | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:315` | `log_scale: bool = False` | OURS | Logarithmic pitchfork transformation toggle (`papers/02_PITCHFORK_APPLICATION_ON_BTC.md:43-58`). |
| ZigZag pivot lookback confirmation | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:337` | `lookback: int = 3` | SOURCED | Patrick Mikula (2002:42) swing confirmation clearance requirement: $N \ge 3$ bars clearance (`RESEARCH_PITCHFORK_LAYER.md:24`). |
| ZigZag minimum change threshold | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:338, 369, 378` | `min_change_pct: float = 0.02` | OURS | 2% reversal threshold in ZigZag pivot detector; repo choice. |
| Scanner setup mode default | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:392` | `setup_mode: str = "BOUNCE"` | OURS | Scanner setup mode selector; repo choice. |
| Scanner VP confluence filter default | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:393` | `vp_filter: str = "VA"` | OURS | Volume profile filter default (70% Value Area filter $[VAL, VAH]$) (`PHASE2_4H_POC_STUDY.md:26,80-82`). |
| Scanner 4H pivot lookback | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:394` | `lookback: int = 4` | OURS | 4-bar (16-hour) swing confirmation lookback for 4H bars (`PHASE2_4H_POC_STUDY.md:8`). |
| Scanner stop loss offset pct | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:396` | `stop_offset_pct: float = 0.015` | OURS | 1.5% fixed stop buffer beyond tine extreme (`PHASE2_4H_POC_STUDY.md:278`). |
| Scanner max evaluation bars | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:397` | `max_eval_bars: int = 60` | OURS | Maximum evaluation window after P2 confirmation before expiry; repo choice. |

---

## 2. Details and Observations

1. **Theoretical Foundations vs Algorithmic Codification**:
   - The geometric vector equations of the Median Line and parallel tines, Schiff and Modified Schiff 50% origin coordinate offsets, Morge quartile/warning parallels, and Andrews' 80% median line reach rule are SOURCED from historical literature (Andrews, Schiff, Morge, Mikula).
   - Numerical engineering thresholds for automated execution—specifically the 15% Hagopian rollover minimum approach threshold, the 2% ZigZag reversal filter, the 1.5% stop offset, and the 60-bar evaluation window—are internally defined (`OURS`).
2. **Volume Profile Confluence Integration**:
   - `pitchfork_detector.py` wires anchored volume profiles via `vp_pivot_probe.build_profile` over the $P_0 \to P_2$ anchor window using a default bin width of $10.0 USD and a 70% Value Area boundary condition (`OURS`).
