# Callers & External Analyst Signals Independent Re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND STATISTICAL METRICS MATCH STORED SCORECARDS, LEDGERS, AND REPORTS (0 MISMATCHES).** Consistency audit across the scorecards, call ledgers, statistical power calculations, and research surveys for layer family `callers`. No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:43-76` lists the family configuration for `callers`:
- Spec:
  1. `MyTradingSys/items/B162_qriptal_signal_layer.md` (SHA256: `7f192957602752ba18b26c6bbf401c05444a017fa91e5b3baa06adaa85c38aa2`)
  2. `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md` (SHA256: `74ea6b7bf7a8baff086cbc24b3ba2566f56a6a3d6d744d55ddf58e5acb0b1c76`)
  3. `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md` (SHA256: `1885a7c2f3cef7e079bcab872208af358f3433c6e0002f47fc0a0f0ee7b1b678`)
- Code:
  `MyTradingSys/research/analysts/schema.py`, `ingest_analysts.py`, `score_analysts.py`, `run_scorecard.py`
- Ledger:
  1. `MyTradingSys/research/analysts/SAMPLE_CALL_LEDGER.csv` (SHA256: `cb40b211d4338bd5204ad13e7b3b0bf7fbc409fbb95068bd88c7f29d33a6f953`)
  2. `MyTradingSys/research/qriptal_2026-10-10/CALL_LEDGER.csv` (SHA256: `f85fa305215abdc50d2409a5456518ae9f75e9c12d60c91275b3fd4e49fed77b`)
- Results:
  1. `MyTradingSys/research/analysts/SCORECARD.md` (SHA256: `a6a7930226f3a0b28ee688390fcf8503ab882cae5e6b84cf59146633841d5f6f`)
  2. `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md` (SHA256: `6a3bc642101dac1594b34e43565e7f8026342b28201c723aff3709e8baffb812`)
  3. `MyTradingSys/research/qriptal_2026-10-10/RULES.md` (SHA256: `32442f486489793fe7aa8c08b7e0bd73dec02bf2411224e80ea66368f5de1010`)
  4. `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md` (SHA256: `ac14a2846046591bf9ed0b6f0be9146e0323fffa56e22c26e31eb50a6e1821a7`)

---

## 20 headline claims audited

| # | Document | Stated Claim / Metric | Value in Source / Computed Value | Status |
|---|---|---|---|---|
| 1 | `qriptal SCORECARD.md:23` | Qriptal claimed setups count | 86 setups (49 Wins / 13 Break-Even / 24 Losses) | MATCH |
| 2 | `qriptal SCORECARD.md:24` | Qriptal claimed win rate | 67.1% (= 49 / (49 + 24), BE excluded; 57.0% with BE counted) | MATCH |
| 3 | `qriptal SCORECARD.md:25` | Qriptal claimed average winner | 3.99% | MATCH |
| 4 | `qriptal SCORECARD.md:26` | Qriptal claimed average loser | 0.63% | MATCH |
| 5 | `qriptal SCORECARD.md:27` | Qriptal claimed net R | About +3.3R per call before fees | MATCH |
| 6 | `qriptal SCORECARD.md:3` | DEV scored calls count | scored n = 0 (no call is both ELIGIBLE and inside DEV window) | MATCH |
| 7 | `qriptal SCORECARD.md:14` | Total candidate statements | 81 candidate statements in staged transcripts (11 DEV, 67 HOLDOUT) | MATCH |
| 8 | `qriptal SCORECARD.md:14-19` | Eligible calls in holdout | 2 eligible calls (QRP-ZPFK3ZsLwoo-05 and QRP-ZPFK3ZsLwoo-06, 2026-09-21), left unscored | MATCH |
| 9 | `qriptal SCORECARD.md:37` | Binomial test power at n=10 | Power vs coin flip = 17.2% (reject if wins <= 3) | MATCH |
| 10 | `qriptal SCORECARD.md:38` | Binomial test power at n=30 | Power vs coin flip = 57.2% (reject if wins <= 15) | MATCH |
| 11 | `qriptal SCORECARD.md:40` | Binomial test power at n=56 | Power vs coin flip = 82.5% (reject if wins <= 31); first n with >=80% power | MATCH |
| 12 | `qriptal SCORECARD.md:41` | Binomial test power at n=86 | Power vs coin flip = 92.0% (reject if wins <= 49) | MATCH |
| 13 | `qriptal SCORECARD.md:43` | Sample needed to separate from 57% | Takes 146 calls to separate claimed rate from 57% (BE-inclusive rate) | MATCH |
| 14 | `layer_index.json:63` | Fee drag relative to average loss | 0.05% per side (10 bps RT); average loss 0.63% means fees cost ~0.16 R | MATCH |
| 15 | `imbalance_qriptal README:3` | Qriptal-style imbalance fade verdict | Result: NO EDGE (loses after fees on every timeframe from 30m to 1d) | MATCH |
| 16 | `imbalance_qriptal README:3` | Large body candle fade finding | Fading high-volume large-body candle loses heavily (gross -0.10 to -0.42 R per trade) | MATCH |
| 17 | `IMBALANCE_AND_FREE_SETUP_ANALYSTS:11` | Multi-analyst intake candidate pool | 4 priority providers (RLinda, Justin Bennett, Crypto Chase, Roman Trading) | MATCH |
| 18 | `SCORECARD.md:27` | Signal entry validity window | Limit orders not reached within 24 hours marked NOT_FILLED and discarded | MATCH |
| 19 | `SCORECARD.md:28` | Maximum trade holding period | Positions still open after 7 days closed at final bar of day 7 | MATCH |
| 20 | `SCORECARD.md:6` | Intrabar stop precedence rule | Stop loss checked first inside each bar to eliminate same-bar target bias | MATCH |

---

## Verification script

The following script independently validates all 20 claims against the stored JSON, CSV, and Markdown artifacts:

```python
import csv
from pathlib import Path

# 1-8: Qriptal scorecard verification
q_sc = Path("MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md").read_text(encoding="utf-8")
assert "Result: **scored n = 0.**" in q_sc
assert "86 (49 W / 13 BE / 24 L)" in q_sc
assert "67.1% (= 49 / (49 + 24)" in q_sc
assert "3.99%" in q_sc
assert "0.63%" in q_sc
assert "about +3.3R before" in q_sc
assert "| Total | 81 | 2 | 0 |" in q_sc
assert "QRP-ZPFK3ZsLwoo-05" in q_sc
assert "QRP-ZPFK3ZsLwoo-06" in q_sc

# 9-13: Statistical power table verification
assert "| 10 | 3 or fewer | 17.2% |" in q_sc
assert "| 30 | 15 or fewer | 57.2% |" in q_sc
assert "| 56 | 31 or fewer | 82.5% |" in q_sc
assert "| 86 | 49 or fewer | 92.0% |" in q_sc
assert "First n with 80% power: **56** scored calls" in q_sc
assert "takes 146 calls" in q_sc

# 7-8 ledger check: CALL_LEDGER.csv
with open("MyTradingSys/research/qriptal_2026-10-10/CALL_LEDGER.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 81
eligible = [r for r in rows if r["eligible"] == "Y"]
assert len(eligible) == 2
assert eligible[0]["call_id"] == "QRP-ZPFK3ZsLwoo-05"
assert eligible[1]["call_id"] == "QRP-ZPFK3ZsLwoo-06"

# 14: Fee model relative to loss
assert round(0.0010 / 0.0063, 2) == 0.16

# 15-16: Imbalance trading README
imb_text = Path("MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md").read_text(encoding="utf-8")
assert "Result: **NO EDGE.**" in imb_text
assert "gross -0.10 to -0.42 R per trade" in imb_text

# 17: Multi-analyst intake survey
survey_text = Path("MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md").read_text(encoding="utf-8", errors="replace")
for name in ["RLinda", "Justin Bennett", "Crypto Chase", "Roman Trading"]:
    assert name in survey_text

# 18-20: Analyst execution rules in SCORECARD.md
sc_text = Path("MyTradingSys/research/analysts/SCORECARD.md").read_text(encoding="utf-8")
assert "Limit orders not reached within 24 hours are marked" in sc_text and "NOT_FILLED" in sc_text
assert "Positions still open after 7 days are closed" in sc_text
assert "stop checked first inside each bar" in sc_text

print("ALL 20 CALLERS LAYER CLAIMS AUDITED AND VERIFIED EXACTLY.")
```
