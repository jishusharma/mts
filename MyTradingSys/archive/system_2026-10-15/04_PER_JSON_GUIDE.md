# FILE: 04_PER_JSON_GUIDE.md
# READ ORDER: 7 of 8
# PURPOSE: Per-JSON index — what to load for each market snapshot analysis
# LAST UPDATED: 2026-08-27
# SIZE: ~2KB
# NEXT FILE: 05_NORMS.md
# PREVIOUS FILE: 03_FILE_INDEX.md
# ---

# WORKFLOW QUICKREF — JSON to Trading Card
# Purpose: Per-JSON index. Load this FIRST per analysis, then load only the rule files needed.
# Size: ~25 lines. Load time: <1 sec.
# Canonical path: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\system/04_PER_JSON_GUIDE.md

---

## PER-JSON LOAD ORDER

| Step | File | Purpose | Load If |
|------|------|---------|---------|
| 1 | system/04_PER_JSON_GUIDE.md | This file — index of what to load | ALWAYS |
| 2 | mts/conditions/market_state_rules.md | Balance/trend taxonomy, state-to-setup matrix | State unclear from JSON |
| 3 | mts/conditions/zone_identification_rules.md | 9 zone types, VAH/VAL/POC/VWAP rules | Zone unclear from JSON |
| 4 | mts/conditions/setup_type_rules.md | 4 execution modes, idea+proof framework | Setup candidate exists |
| 5 | mts/conditions/proof_requirements_formatted.md | 14 proof categories, cross-cutting layer | Proof check needed |
| 5.5 | mts/conditions/entry_timing_triggers.md | Section 0.5 (Runtime Quickref only) — Trigger taxonomy | Setup candidate exists (after proof) |
| 6 | mts/conditions/risk_protocol.md | Stops, sizing, R:R, targets, drawdown | Risk validation needed |
| 7 | mts/cards/trading_card_generator.md | Card format spec, verdict tree | ALWAYS (output template) |

---

## WHEN SYSTEM FLAGS VISUAL GAP

If JSON lacks footprint data or proof is unclear:
1. System asks JISHU: "Pull 15m footprint from CoinGlass"
2. JISHU describes what they see (absorption, rejection, delta flip, finished auction)
3. System references proof_requirements_formatted.md Section 2.3 for definitions
4. System updates verdict based on visual confirmation

No separate visual checklist file needed. Proof rules are in proof_requirements_formatted.md.

---

## ABBREVIATIONS

| Abbr | Full |
|------|------|
| VP | Volume Profile |
| POC | Point of Control |
| VAH | Value Area High |
| VAL | Value Area Low |
| VWAP | Volume-Weighted Average Price |
| FVG | Fair Value Gap |
| LVN | Low Volume Node |
| CT | Counter-Trade |
| TC | Trend-Continuation |
| BO | Breakout |
| SC | Scalp |
| R:R | Risk:Reward ratio |

# END
