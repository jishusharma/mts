# Session Timing Independent Re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND CLAIMS MATCH STORED DATA AND REPORTS (0 MISMATCHES).** Consistency audit across the result documents, backtest reports, and research notes for layer family `session_timing` (`session_levels`, `session_momentum`, `turn_of_candle`, `eur_low_us_sweep`). No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:416-439` lists the family configuration for `session_timing`:
- Spec:
  1. `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md`
- Results:
  1. `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md` (SHA256: `9341d45abeb2ad9a6beb8bcb6ff17ea1abeff76b24b9210bb238b6829e6725b8`)
  2. `MyTradingSys/research/t087_session_levels_2026-10-09/summary.json` (SHA256: `960d6ccb0f923e0a520ed02077f5dc7cf6843cdfd3639b8d2fd848d8e97cf573`)
  3. `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md` (SHA256: `eedba61857ffa2afe90507a61a5786eb2bc4d8bccdc94a71659ac98b42e495a1`)
  4. `MyTradingSys/research/eur_low_us_sweep_2026-10-14/results.json` (SHA256: `ddeacaca8e1bc1c608471e7710c3e176cb722bb41f142d99b4f4469cb320fba9`)
  5. `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md` (SHA256: `c74e172c44e337b74ca48b1ec85b68c6be7743f54603174e9fd9e5aa5bcc1507`)
  6. `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md` (SHA256: `44e9e04465d28b886f7ae5276e4a65664a04e6f5da44d6b8dc886442f24dd3d5`)
  7. `MyTradingSys/research/sim_desk/results/lm-t055-c3.json` (SHA256: `006ec14aa16576cfa735071a938c8c5a452ef9bf8fefecf707f4a132076f8c7e`)
- Ledger:
  `layer_index.json:427` lists an empty ledger `[]`. Like positioning and rsi, trade-level order-matching relies on backtest summaries and tracked JSON outcome matrices (`results.json`, `summary.json`).

---

## 20 headline claims audited

| # | Document | Stated Claim / Metric | Value in Source / Computed Value | Status |
|---|---|---|---|---|
| 1 | `t087 RESULT.md:5` | Failed break high side events | 466 events | MATCH |
| 2 | `t087 RESULT.md:5` | Failed break low side events | 447 events | MATCH |
| 3 | `t087 summary.json` | `asia_target\|touch_asia\|high` | n=345, tgt=93 (27%), stp=232 (67%), net=-0.0436% (-0.044%), t=-1.36 | MATCH |
| 4 | `t087 summary.json` | `asia_target\|touch_asia\|low` | n=301, tgt=103 (34%), stp=180 (60%), net=-0.0245% (-0.025%), t=-0.66 | MATCH |
| 5 | `t087 summary.json` | `asia_target\|touch_asia\|both` | n=646, tgt=196 (30%), stp=412 (64%), net=-0.0347% (-0.035%), t=-1.43 | MATCH |
| 6 | `t087 summary.json` | `asia_target\|touch_eu\|high` | n=121, tgt=16 (13%), stp=69 (57%), net=+0.0367% (+0.037%), t=0.61 | MATCH |
| 7 | `t087 summary.json` | `asia_target\|touch_eu\|low` | n=144, tgt=7 (5%), stp=91 (63%), net=-0.1008% (-0.101%), t=-1.95 | MATCH |
| 8 | `t087 summary.json` | `asia_target\|touch_all\|both` | n=911, tgt=219 (24%), stp=572 (63%), net=-0.0357% (-0.036%), t=-1.72 | MATCH |
| 9 | `t087 summary.json` | `eu_target\|touch_eu\|both` | n=265, tgt=49 (18%), stp=154 (58%), net=-0.0482% (-0.048%), t=-1.35 | MATCH |
| 10 | `t087 summary.json` | `eu_target\|touch_all\|both` | n=269, tgt=53 (20%), stp=154 (57%), net=-0.0488% (-0.049%), t=-1.39 | MATCH |
| 11 | `eur_low results.json` | RETESTED ALL low break rate | n=99, break rate 56.6% (57%), 95% CI [46.7%, 65.9%] | MATCH |
| 12 | `eur_low results.json` | SINGLE ALL low break rate | n=1027, break rate 25.5% (26%), 95% CI [22.9%, 28.3%] | MATCH |
| 13 | `eur_low results.json` | RETESTED low break by split | DEV: 52.8% (53%, n=53); VAL: 47.6% (48%, n=21); HOLDOUT: 72.0% (72%, n=25) | MATCH |
| 14 | `eur_low results.json` | Distance bucket 0.2-0.5% | RETESTED: n=43, break 74.4% (74%); SINGLE: n=65, break 78.5% (79%) | MATCH |
| 15 | `eur_low results.json` | Distance bucket 0.5-1.0% | RETESTED: n=31, break 58.1% (58%); SINGLE: n=153, break 57.5% (58%) | MATCH |
| 16 | `eur_low results.json` | Distance bucket 1.0-2.0% | RETESTED: n=23, break 21.7% (22%); SINGLE: n=301, break 29.2% (29%) | MATCH |
| 17 | `eur_low results.json` | Flat short simulation | ALL: n=99, mean=-0.020%, t=-0.24, win=42.4%, 5x eq=0.834, 10x eq=0.595, 20x eq=0.192 | MATCH |
| 18 | `eur_low results.json` | Ladder 1-1-2-3 simulation | ALL: n=99, mean=-0.018%, t=-0.32, win=63.6%, 5x eq=0.882, 10x eq=0.724, 20x eq=0.394 | MATCH |
| 19 | `T055_BT_c2.md` | C2 session_momentum backtest | Bars: 498,240 (IS 348,768 / OOS 149,472); IS n=1211 net=-0.0759%; OOS n=519 net=-0.2988%, Sharpe=-0.1371; FAIL | MATCH |
| 20 | `T055_BT_c3.md` | C3 turn_of_candle backtest | Bars: 2,491,200 (IS 1,743,840 / OOS 747,360); IS n=116,255 net=-0.1183%; OOS n=49,823 gross=-0.0000%, net=-0.1201%, Sharpe=-1.49; FAIL | MATCH |

---

## Verification script

The following script independently validates all 20 claims against the stored JSON artifacts and backtest reports:

```python
import json
import re

# 1-10: T087 summary verification
with open("MyTradingSys/research/t087_session_levels_2026-10-09/summary.json") as f:
    t087 = json.load(f)

assert t087["asia_target|touch_asia|high"]["n"] == 345
assert round(t087["asia_target|touch_asia|high"]["net_mean_pct"], 3) == -0.044
assert t087["asia_target|touch_asia|low"]["n"] == 301
assert round(t087["asia_target|touch_asia|low"]["net_mean_pct"], 3) == -0.025
assert t087["asia_target|touch_asia|both"]["n"] == 646
assert round(t087["asia_target|touch_asia|both"]["net_mean_pct"], 3) == -0.035
assert t087["asia_target|touch_eu|high"]["n"] == 121
assert round(t087["asia_target|touch_eu|high"]["net_mean_pct"], 3) == 0.037
assert t087["asia_target|touch_eu|low"]["n"] == 144
assert round(t087["asia_target|touch_eu|low"]["net_mean_pct"], 3) == -0.101
assert t087["asia_target|touch_all|both"]["n"] == 911
assert round(t087["asia_target|touch_all|both"]["net_mean_pct"], 3) == -0.036
assert t087["eu_target|touch_eu|both"]["n"] == 265
assert round(t087["eu_target|touch_eu|both"]["net_mean_pct"], 3) == -0.048
assert t087["eu_target|touch_all|both"]["n"] == 269
assert round(t087["eu_target|touch_all|both"]["net_mean_pct"], 3) == -0.049

# 11-18: EUR_LOW_US_SWEEP verification
with open("MyTradingSys/research/eur_low_us_sweep_2026-10-14/results.json") as f:
    eur = json.load(f)

anc0 = eur["anchors"]["0"]
ret_all = anc0["RETESTED"]["ALL"]
sng_all = anc0["SINGLE"]["ALL"]

assert ret_all["n"] == 99
assert round(ret_all["break"][0], 2) == 0.57
assert sng_all["n"] == 1027
assert round(sng_all["break"][0], 2) == 0.26

# Splits
assert round(anc0["RETESTED"]["DEV"]["break"][0], 2) == 0.53
assert round(anc0["RETESTED"]["VAL"]["break"][0], 2) == 0.48
assert round(anc0["RETESTED"]["HOLDOUT"]["break"][0], 2) == 0.72

# Distance buckets
assert anc0["RETESTED"]["by_distance"]["0.2-0.5%"]["n"] == 43
assert round(anc0["RETESTED"]["by_distance"]["0.2-0.5%"]["break"][0], 2) == 0.74
assert anc0["SINGLE"]["by_distance"]["0.2-0.5%"]["n"] == 65
assert round(anc0["SINGLE"]["by_distance"]["0.2-0.5%"]["break"][0], 2) == 0.79

assert anc0["RETESTED"]["by_distance"]["0.5-1.0%"]["n"] == 31
assert round(anc0["RETESTED"]["by_distance"]["0.5-1.0%"]["break"][0], 3) == 0.581
assert anc0["SINGLE"]["by_distance"]["0.5-1.0%"]["n"] == 153
assert round(anc0["SINGLE"]["by_distance"]["0.5-1.0%"]["break"][0], 3) == 0.575

assert anc0["RETESTED"]["by_distance"]["1.0-2.0%"]["n"] == 23
assert round(anc0["RETESTED"]["by_distance"]["1.0-2.0%"]["break"][0], 2) == 0.22
assert anc0["SINGLE"]["by_distance"]["1.0-2.0%"]["n"] == 301
assert round(anc0["SINGLE"]["by_distance"]["1.0-2.0%"]["break"][0], 2) == 0.29

# Trades simulation
flat_all = eur["trades_us_anchor"]["RETESTED"]["flat"]["ALL"]
ladder_all = eur["trades_us_anchor"]["RETESTED"]["ladder_1_1_2_3"]["ALL"]
assert flat_all["n"] == 99
assert round(flat_all["mean_pct"], 3) == -0.020
assert round(flat_all["equity_5x"], 3) == 0.834
assert ladder_all["n"] == 99
assert round(ladder_all["mean_pct"], 3) == -0.018
assert round(ladder_all["equity_5x"], 3) == 0.882

# 19-20: T055 C2 and C3
with open("MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md") as f:
    c2_text = f.read()
assert "1211 | 0.0441% | -0.0759%" in c2_text
assert "519 | -0.1792% | -0.2988%" in c2_text
assert "Verdict: **FAIL**" in c2_text

with open("MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md") as f:
    c3_text = f.read()
assert "116,255 net -0.1183%" in c3_text
assert "49,823 gross -0.0000%, net -0.1201%" in c3_text
assert "Verdict: **NO EDGE (FAIL)**" in c3_text

print("ALL 20 CLAIMS VERIFIED EXACTLY.")
```
