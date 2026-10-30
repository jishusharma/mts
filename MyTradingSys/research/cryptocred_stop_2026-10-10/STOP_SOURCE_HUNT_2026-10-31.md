# CryptoCred Stop Buffer - Source Hunt

**Date:** 2026-10-31 UTC  
**Task:** `gemini-cryptocred-stop-buffer-source-hunt`  
**Registry:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Reference:** LAYERS.md B143 / D20 (unsourced 0.1% buffer in `cc_setups.py`)  

---

## 1. Executive Summary

CryptoCred setups FAIL under backtesting and the stop buffer was historically hardcoded at `0.1%` without source attribution (B143). An exhaustive hunt was conducted across all existing transcript extracts under `extracts/processed/cryptocred/` and the latest 10 @CryptoCred YouTube video captions fetched into `MyTradingSys/research/cryptocred_stop_2026-10-10/transcripts_2026-10-31/`.

### Findings:
1. **Numeric Stop Buffer:** **`NOT_IN_DATA`** across all transcripts, videos, and extracts. CryptoCred never specifies a fixed percentage buffer (e.g. 0.1%, 0.25%, 0.5%) or tick offset. The 0.1% buffer is confirmed strictly **OURS (NO-SOURCE)**.
2. **Stop Placement Rule:** In CryptoCred's methodology, stop placement is strictly structural invalidation derived directly from the trade idea:
   - **S/R Flip (Retest):** Invalidation/stop is placed at the swing extreme or beyond the structural level being retested (e.g., market structure based stop at the low/high).
   - **Fibonacci Pullback:** Invalidation is a structural failure to form a higher low (bullish) or lower high (bearish), beyond the anchor low/high.
   - **Failed MSB Reversal:** Invalidation is a break beyond the swing high/low that broke structure (where the opposing trend's participants are proven right).

---

## 2. Setup Stop Rules & Quotes

| Setup | Stop Rule in His Words | Buffer Number if Any | Video ID | Timestamp | Quote |
|---|---|---|---|---|---|
| **S/R Flip** (Retest) | Invalidation / market structure based stop loss at the structural low/high | NOT_IN_DATA | `inqHN8q57X4` | `[00:11:23]` | "a market structure based stop loss at the low" |
| **Fib Pullback** | Invalidation is structural failure to make a higher low (bullish) or lower high (bearish) | NOT_IN_DATA | `BHwoN7VPrBE` | `[01:01:06]` | "it's higher highs and higher lows if it fails to make a higher low" |
| **Failed MSB** (Reversal) | Invalidation is a higher high (bearish) or lower low (bullish) where opposing positions are invalidated | NOT_IN_DATA | `BHwoN7VPrBE` | `[01:14:38]` | "invalidation is a higher high because if it's bearish it should be making lower lows and lower highs" |

---

## 3. Verbatim Extraction Blocks (GPS Tagged)

These extract blocks are verified against canonical transcripts using `scripts/dev/verify_extract_quotes.py`.

### S/R Flip Setup (Retest)
> "a market structure based stop loss at the low"
**Source GPS: inqHN8q57X4 | BEGIN**

> "invalidation would be unchanged right let's say it's more or less above this high"
**Source GPS: inqHN8q57X4 | MIDDLE**

### Fibonacci Pullback Setup
> "it's higher highs and higher lows if it fails to make a higher low"
**Source GPS: BHwoN7VPrBE | MIDDLE**

> "if on this bounce it fails to make a lower high then the structure's broken and that's no longer valid"
**Source GPS: BHwoN7VPrBE | MIDDLE**

### Failed MSB Reversal Setup
> "invalidation is a higher high because if it's bearish it should be making lower lows and lower highs"
**Source GPS: BHwoN7VPrBE | END**

> "if price fails and makes a higher high they are invalidated and closing those shorts which become longs at market"
**Source GPS: BHwoN7VPrBE | END**

### General Stop Placement & Invalidation Principles
> "stop placement is inextricably linked with the trade idea itself your stop reflects your invalidation and we know that your invalidation is derived from the trade idea"
**Source GPS: XeQV2ECtZVQ | BEGIN**

> "if you don't know where to put a stop that often means the idea itself was not defined very clearly"
**Source GPS: XeQV2ECtZVQ | BEGIN**

> "would i want to buy where my long gets stopped out and or would i want to sell where my short gets stopped out if the answer is yes then there's a good chance that the trade sucks"
**Source GPS: XeQV2ECtZVQ | BEGIN**
