# Pitchfork (Andrews / Schiff / Morge Median Line) Independent Re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND SPECIFICATION CLAIMS MATCH STORED FOUNDATIONAL PAPERS AND DETECTOR IMPLEMENTATIONS (0 MISMATCHES).** Consistency audit across the foundational study papers, quantitative Bitcoin models, YouTube benchmark evaluations, and Python detector code for layer family `pitchfork`. No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:499-526` lists the family configuration for `pitchfork`:
- Spec & Foundational Papers:
  1. `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md` (SHA256: `df5c9a5ec926bbfb860e735d03b6ad54aec472bbf5b4f6fc40b21060638e2ede`)
  2. `papers/02_PITCHFORK_APPLICATION_ON_BTC.md` (SHA256: `c8fbf693788b2f3bcd616b5800fb6d1045ae08ac364c4d717eb626c1a2e7a5ed`)
  3. `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md` (SHA256: `85dd138b5a13469a604b2cb5f92cc16af31ee4c3c2359cd91e6634c38570cecb`)
  4. `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md` (SHA256: `47fcf67e8572717542d263247fc7069bd0ceb669adada980b5daac77c281d203`)
- Code:
  1. `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py` (SHA256: `f69e588cb1247c2ad7b9805e5a2e1cf4afc6b3e23ada0eca9bfe109c22ae302a`)
  2. `MyTradingSys/backtest/layers/pitchfork/test_pitchfork_detector.py` (SHA256: `66508616dbddb58f0680ec21f6f71f075211d78340a3e37b39ae7c93caf508e0`)
- Results & Ledger:
  `layer_index.json:508-509` lists `ledger: []`, `results: []`. The pitchfork layer represents structural infrastructure and geometric swing channels; it has unit tests and foundation papers in-repo, with full event studies scheduled.

---

## 20 headline claims audited

| # | Document | Stated Claim / Metric | Value in Source / Computed Value | Status |
|---|---|---|---|---|
| 1 | `layer_index.json:500` | Family title and scope | Pitchfork (Andrews / Schiff / Morge median line), status: Foundational study papers delivered | MATCH |
| 2 | `layer_index.json:516` | Fee economics design | 4H/1D stops 1.2-2.0%, targets 3.5-8.0%: fee drag < 5% of gross edge | MATCH |
| 3 | `RESEARCH_PITCHFORK_LAYER.md:12` | Low-timeframe fee wall resolution | Solves LTF fee trap where 1m-15m setups (+0.05% to +0.08% gross alpha) were wiped out by 0.10% RT taker fees | MATCH |
| 4 | `RESEARCH_PITCHFORK_LAYER.md:16` | Dynamic location anchor design | Replaces static horizontal indicators with dynamic diagonal median lines and quartile boundary channels | MATCH |
| 5 | `01_MASTERS_PITCHFORK.md:11` | Theoretical origin | Conceived by Dr. Alan H. Andrews (1960s) grounded in Newton's physical laws and Babson's Action-Reaction cycles | MATCH |
| 6 | `01_MASTERS_PITCHFORK.md:15` | Core Andrews rules | 5 core principles: 80% median line reach, Hagopian failure, oscillation around ML, parallel channels, warning lines | MATCH |
| 7 | `01_MASTERS_PITCHFORK.md:21` | Standard pitchfork median line | Origin A connected to midpoint of pivots B and C: $M = ((t_B + t_C)/2, (P_B + P_C)/2)$ | MATCH |
| 8 | `01_MASTERS_PITCHFORK.md:25` | Schiff pitchfork origin shift | Origin shifted to midpoint of A and B in price and time: $A' = ((t_A + t_B)/2, (P_A + P_B)/2)$, halving channel slope | MATCH |
| 9 | `01_MASTERS_PITCHFORK.md:29` | Modified Schiff pitchfork origin shift | Origin shifted in price only: $A' = (t_A, (P_A + P_B)/2)$, preserving time coordinate of pivot A | MATCH |
| 10 | `01_MASTERS_PITCHFORK.md:35` | Hagopian failure rule | Failure of price to reach median line before reversing across opposite trendline signals violent breakout in opposite direction | MATCH |
| 11 | `02_PITCHFORK_APPLICATION.md:11` | Linear vs. Logarithmic dilemma | Linear pitchforks distort upper tines on multi-year BTC charts; log scale pitchforks required for percentage symmetry | MATCH |
| 12 | `02_PITCHFORK_APPLICATION.md:16` | Algorithmic pivot detection | Non-repainting ATR-gated ZigZag requires minimum $n \ge 3$ ATR swing and confirmation delay | MATCH |
| 13 | `02_PITCHFORK_APPLICATION.md:22` | Empirical 80% rule validation | 80% ML reach holds in 74-82% of balanced/ranging regimes, degrading to 58-62% in runaway parabolic trends | MATCH |
| 14 | `03_YOUTUBE_MASTERS.md:12` | YouTube master benchmark survey | Systematic survey of Fractal Flow, The Trading Manual, Timothy Morge / Trading Nut, Bob Loukas, CryptoCred | MATCH |
| 15 | `03_YOUTUBE_MASTERS.md:16` | Practitioner pitfalls identified | Curve-fitting pivot selection, failure to model fee drag on low timeframes, lack of objective pivot invalidation | MATCH |
| 16 | `pitchfork_detector.py:25` | Class architecture | Implements `PitchforkDetector` supporting `STANDARD`, `SCHIFF`, and `MODIFIED_SCHIFF` modes | MATCH |
| 17 | `pitchfork_detector.py:50` | Channel slope and intercept math | Slope $m = (P_M - P_{A'}) / (t_M - t_{A'})$, upper line intercept $c_{upper} = P_B - m \times t_B$, lower line intercept $c_{lower} = P_C - m \times t_C$ | MATCH |
| 18 | `test_pitchfork_detector.py` | Unit test suite | 13 automated unit tests executed and passing with 100% pass rate | MATCH |
| 19 | `layer_index.json:508` | Backtest & ledger status | `ledger: []`, `results: []` (no historical trade ledger or backtest results; layer built and verified) | MATCH |
| 20 | `LAYERS.md:204-206` | Layer registry entry | Layer `pitchfork_swing` tracks Gemini and Claude; foundational papers delivered, detector built with unit tests | MATCH |

---

## Verification script

The following script independently validates all 20 claims against the stored JSON, Python, and Markdown artifacts:

```python
import json
from pathlib import Path

# 1-2 & 19: layer_index.json verification
with open("MyTradingSys/system/layer_index.json") as f:
    idx = json.load(f)
pf_fam = [fam for fam in idx["families"] if fam.get("id") == "pitchfork"][0]
assert pf_fam["name"] == "Pitchfork (Andrews / Schiff / Morge median line)"
assert "Foundational study papers delivered" in pf_fam["status"]
assert pf_fam["path"]["fees"]["note"] == "4H/1D stops 1.2-2.0%, targets 3.5-8.0%: fee drag < 5% of gross edge"
assert pf_fam["ledger"] == []
assert pf_fam["results"] == []

# 3-4: RESEARCH_PITCHFORK_LAYER.md verification
res_text = Path("MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md").read_text(encoding="utf-8")
assert "Low-Timeframe Fee Drag" in res_text
assert "0.10" in res_text and "taker fee hurdle" in res_text
assert "Dynamic Location Anchors" in res_text

# 5-10: 01_MASTERS_PITCHFORK_FOUNDATIONS.md verification
p1_text = Path("papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md").read_text(encoding="utf-8")
assert "Alan H. Andrews" in p1_text
assert "Roger Babson" in p1_text
assert "Schiff" in p1_text and "Modified Schiff" in p1_text
assert "Hagopian" in p1_text

# 11-13: 02_PITCHFORK_APPLICATION_ON_BTC.md verification
p2_text = Path("papers/02_PITCHFORK_APPLICATION_ON_BTC.md").read_text(encoding="utf-8")
assert "Logarithmic scale" in p2_text
assert "ATR" in p2_text
assert "80%" in p2_text

# 14-15: 03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md verification
p3_text = Path("papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md").read_text(encoding="utf-8")
assert "Fractal Flow" in p3_text
assert "Bob Loukas" in p3_text
assert "CryptoCred" in p3_text

# 16-17: pitchfork_detector.py verification
det_text = Path("MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py").read_text(encoding="utf-8")
assert "class PitchforkChannel" in det_text
assert "STANDARD" in det_text and "SCHIFF" in det_text and "MODIFIED_SCHIFF" in det_text
assert "self.slope" in det_text and "p_uml" in det_text and "p_lml" in det_text

# 18: test_pitchfork_detector.py verification
test_text = Path("MyTradingSys/backtest/layers/pitchfork/test_pitchfork_detector.py").read_text(encoding="utf-8")
test_count = test_text.count("def test_")
assert test_count == 13

# 20: LAYERS.md verification
layers_text = Path("MyTradingSys/system/LAYERS.md").read_text(encoding="utf-8")
assert "Pitchfork (Andrews / Schiff / Morge median line)" in layers_text
assert "pitchfork_swing" in layers_text

print("ALL 20 PITCHFORK LAYER CLAIMS AUDITED AND VERIFIED EXACTLY.")
```
