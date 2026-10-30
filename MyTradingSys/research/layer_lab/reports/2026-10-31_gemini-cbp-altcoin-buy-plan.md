# Layer Lab Report: CBP Altcoin Buy Plan (2026-10-31)

- **Date:** 2026-10-31
- **Task:** `gemini-cbp-altcoin-buy-plan`
- **Goal:** Extract stated rules on when to buy alts (BTC dominance level, cycle phase, BTC level, date window) and which alts from the latest 5 videos of 6 T1 CBP analysts (@RektCapital, @benjaminjcowen, @bobloukas3493, @jalacrypto, @michaelvdpoppe, @CryptoCrewUniversity).
- **Analyst Coverage:** 6 channels x 5 videos = 30 videos processed. SOURCED (`fetch_captions_timed.py`).

## 1. Metric Summary

| Metric | SOURCED / OURS | Value | Notes |
|---|---|---|---|
| Videos Read | SOURCED | 30 | 5 latest per channel across 6 channels |
| Rules Found | OURS | 11 | 1 rule from Jala (`lJ8rI4iiXG4`), 10 rules from vdPoppe (`Jn9hM3jwEik`, `MiQePVTGCXQ`, `SfPE7sWygLE`, `fnRXA4AzEcI`, `_QG1bt4iwQc`) |
| Analysts with NOT_IN_DATA | OURS | 4 | Rekt, Cowen, Bob Loukas, CCU |
| Verification Gate | SOURCED | PASS (0 problems) | `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/cbp/ALT_BUY_PLAN_2026-10-31.md` |

## 2. Findings by Analyst

1. **@RektCapital (`NOT_IN_DATA`):**
   - Videos examined: `MRBXsqgIGb8`, `ZAGbis1hfXw`, `XMbLOHZRSFo`, `BFMztI2UDQ4`, `P0v26DCPiZ4`.
   - Focus is exclusively on Bitcoin macro accumulation ranges and halving cycles. Altcoins are not discussed.

2. **@benjaminjcowen (`NOT_IN_DATA`):**
   - Videos examined: `bekghgecip8`, `21mBnslOLd0`, `4oHSuPTr8H0`, `bWdXPK3Hlok`, `eN6dpreDIk4`.
   - Discusses rising Bitcoin dominance targets (60% to 66%) and ETH breaking below moving averages, but provides no active buy rules or buy timing recommendations for altcoins.

3. **@bobloukas3493 (`NOT_IN_DATA`):**
   - Videos examined: `VWsFf5rQoqE`, `aKbB7gV67M4`, `ctJSV8aTDSk`, `fk1dkrGUar4`, `BU6j1p-bNUY`.
   - Notes altcoin carnage and potential further 50% downside, mentions holding Ethereum on his subscription platform, but gives no public buy rules or altcoin buy criteria.

4. **@jalacrypto (1 Rule Found):**
   - Videos examined: `dmC1U_r8PFc`, `5x8DhXBwX9c`, `EU77lbF-rMI`, `xIUHpTirh_g`, `lJ8rI4iiXG4`.
   - Stated rule: When Bitcoin begins losing dominance, altcoins holding structure take off (`lJ8rI4iiXG4` at `00:11:55`).

5. **@michaelvdpoppe (10 Rules Found):**
   - Videos examined: `fnRXA4AzEcI`, `Jn9hM3jwEik`, `MiQePVTGCXQ`, `SfPE7sWygLE`, `_QG1bt4iwQc`.
   - Rules include:
     - Liquidation trigger: Allocate cash when altcoins experience a 10% to 15% liquidation week (`Jn9hM3jwEik` at `00:12:16`).
     - Cycle phase: De-risk altcoins into risk-free assets deeper into a bull market (`MiQePVTGCXQ` at `00:08:06`).
     - Asset selection: Select real market leaders showing relative strength on BTC pair (`MiQePVTGCXQ` at `00:09:12`).
     - Strategy: Apply DCA accumulation rather than pure buy-and-hold (`MiQePVTGCXQ` at `00:10:20`).
     - Bitcoin condition: Altcoins perform when Bitcoin consolidates or trends upward (`SfPE7sWygLE` at `00:04:37`).
     - Asymmetric setup: Buy unhyped assets in multi-month accumulation ranges before breakout (`SfPE7sWygLE` at `00:16:03`).
     - Early narrative: Buy emerging narratives (e.g. RWAs, tokenization) before parabolic run (`fnRXA4AzEcI` at `00:08:35`).
     - Risk-capped consolidation: Accumulate long-duration sideways ranges with capped 20-30% downside (`fnRXA4AzEcI` at `00:14:22`).
     - Risk minimization: Buy when nobody is looking at the asset (`_QG1bt4iwQc` at `00:03:59`).
     - Profit rotation: Reallocate profits from mature runners into consolidating next narratives (`_QG1bt4iwQc` at `00:14:45`).

6. **@CryptoCrewUniversity (`NOT_IN_DATA`):**
   - Videos examined: `tp78FKX8pMc`, `FlDFTA4s7XE`, `4WpAJxcyUzk`, `OGAIlXwmV1Q`, `kZ5q1K3KzqI`.
   - Uses altcoins solely in promotional hooks for a VIP webinar; public videos contain no actionable buy rules or altcoin buy criteria.

Noticed: 4 of the 6 major CBP analysts focus almost exclusively on Bitcoin in their latest uploads, with Michaël van de Poppe being the sole analyst providing an active, multi-rule altcoin accumulation and rotation framework.
