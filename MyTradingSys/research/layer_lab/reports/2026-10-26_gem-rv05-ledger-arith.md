# Lab Report: Re-computation of Fabio Ledger Entry Prices from Stop Labels (2026-10-28)

**Task**: `gem-rv05-ledger-arith`  
**Card Title**: `[GEMINI] Recompute GPT's Fabio ledger entry prices from stop labels (F8, F12-m2, F13)`  
**Producer**: GPT `gpt-6-luna` ([`MyTradingSys/research/gpt_burn_2026-10-24/gx3-rv05-h2/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-rv05-ledger-arith/MyTradingSys/research/gpt_burn_2026-10-24/gx3-rv05-h2/report.md), [`ledger_adjudication.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-rv05-ledger-arith/MyTradingSys/research/gpt_burn_2026-10-24/gx3-rv05-h2/ledger_adjudication.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md` (lines 105–120, 181–192)
- `MyTradingSys/research/gpt_burn_2026-10-24/gx3-rv05-h2/report.md`
- `MyTradingSys/research/gpt_burn_2026-10-24/gx3-rv05-h2/ledger_adjudication.md`

*Constraint adherence*: In strict adherence to the card brief, `ledger_adjudication.md` was not read or referenced until our own independent calculations were completed.

---

## 1. Executive Summary

1. **Arithmetic Formula & Re-computations Verified**:
   - Formula: $\text{Entry} = \text{Stop} + \frac{|\text{STP \$}|}{\text{Contracts} \times \$20/\text{pt}}$.
   - **F8**: $25{,}021.75 + \frac{2{,}040}{8 \times 20} = 25{,}021.75 + 12.75 = \mathbf{25{,}034.50}$ (displayed frame average $25{,}034.53$, diff $-0.03\text{ pt}$).
   - **F12-m2**: $25{,}098.25 + \frac{2{,}050}{10 \times 20} = 25{,}098.25 + 10.25 = \mathbf{25{,}108.50}$ (displayed frame average $25{,}108.50$, exact tie on H1 stop $25{,}098.25$).
   - **F13**: $25{,}097.00 + \frac{1{,}520}{8 \times 20} = 25{,}097.00 + 9.50 = \mathbf{25{,}106.50}$ (displayed frame average $25{,}108.90$, diff $-2.40\text{ pt}$).
   - **F13-m1**: $25{,}097.00 + \frac{1{,}760}{8 \times 20} = 25{,}097.00 + 11.00 = \mathbf{25{,}108.00}$ (displayed frame average $25{,}108.05$, diff $-0.05\text{ pt}$).

2. **Flagging F13 vs Displayed Average 25,108.90**:
   - The label-derived entry for F13 is **25,106.50** (initial stop width $9.50\text{ pt}$, implied risk $\$1{,}520$).
   - The recorded position-line average on frame is **25,108.90** (initial stop width $11.90\text{ pt}$, implied risk $\$1{,}904$).
   - Discrepancy is $+2.40\text{ pt}$ ($\$384$ on 8 lots). This represents a genuine unreconciled platform discrepancy (flagged as UNRESOLVED H1 in `FABIO_TRADE_LEDGER.md:114, 191`), correctly identified by GPT.

---

## 2. Independent Calculations Breakdown

| Row ID | STP Label on Frame | Stop Price Used | Contracts / Denominator | Calculated Width (pt) | Recomputed Entry Price | Displayed Average on Frame | Difference vs Displayed |
|---|---|---|---|---|---|---|---|
| **F8** | `STP -8 -2040$` | 25,021.75 | 8 lots $\times \$20/\text{pt} = \$160/\text{pt}$ | $\frac{2040}{160} = 12.75\text{ pt}$ | **25,034.50** | 25,034.53 | -0.03 pt (-$4.80) |
| **F12-m2** | `STP -10 -2050$` | 25,098.25 (H1 tie) | 10 lots $\times \$20/\text{pt} = \$200/\text{pt}$ | $\frac{2050}{200} = 10.25\text{ pt}$ | **25,108.50** | 25,108.50 | 0.00 pt ($0.00) |
| **F13** | `STP -8 -1520$` | 25,097.00 | 8 lots $\times \$20/\text{pt} = \$160/\text{pt}$ | $\frac{1520}{160} = 9.50\text{ pt}$ | **25,106.50** | **25,108.90** | **-2.40 pt (-$384.00)** |
| **F13-m1** | `STP -8 -1760$` | 25,097.00 | 8 lots $\times \$20/\text{pt} = \$160/\text{pt}$ | $\frac{1760}{160} = 11.00\text{ pt}$ | **25,108.00** | 25,108.05 | -0.05 pt (-$8.00) |

### Notes on Row-Specific Nuances
- **F12-m2 H1 Tie**: The row stop recorded in the trade table is $25{,}098.75$, but the STP label $-2{,}050\$$ ties mathematically to stop $25{,}098.25$ ($10 \times 10.25 \times 20 = 2{,}050$). If $25{,}098.75$ were used with entry $25{,}108.50$, the cash stop would be $-1{,}950\$$ (a $\$100$ discrepancy).
- **F13 Denominator & Coverage**: At F13-m1, 10 lots were open but the stop label explicitly covered 8 lots (`STP -8 -1760$`). Recomputed entry evaluates the label's own 8 lots ($1{,}760 / 160 = 11.00\text{ pt} \implies 25{,}108.00$). If 10 lots had been used, the width would be $8.80\text{ pt} \implies 25{,}105.80$.

---

## 3. Findings Table

| Severity | File:Line | What is wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| HIGH | [`FABIO_TRADE_LEDGER.md:111, 188-191`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-rv05-ledger-arith/MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md#L111) | F13 stop label (`-1520$` on 8 lots) and recorded displayed average ($25{,}108.90$) conflict by $2.40\text{ pt}$ ($\$384$). | Label implies entry $25{,}106.50$ (width $9.50\text{ pt}$); displayed average $25{,}108.90$ implies stop risk $-\$1{,}904$. | Retain both values clearly labelled with explicit UNRESOLVED H1 provenance marker, keeping displayed average as primary chart observation per RV05 precedence rule. |
| LOW | [`FABIO_TRADE_LEDGER.md:110, 187`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-rv05-ledger-arith/MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md#L110) | F12-m2 stop label $-2{,}050\$$ ties to $25{,}098.25$, differing by $0.50\text{ pt}$ ($\$100$) from the row table stop $25{,}098.75$. | $10 \times (25{,}108.50 - 25{,}098.75) \times 20 = \$1{,}950 \ne \$2{,}050$. | Maintain the documented H1 note explaining the $0.50\text{ pt}$ tick tie between the platform stop order and the chart marker. |

---

## 4. Verdict

**Verdict: SOUND.**  
GPT's recomputed Fabio ledger entry prices in `gx3-rv05-h2/report.md` and `ledger_adjudication.md` are mathematically sound, fully reproducible, and verified:
1. Recomputed prices: **F8 = 25034.50**, **F12-m2 = 25108.50**, **F13 = 25106.50**, **F13-m1 = 25108.00**.
2. F13 discrepancy against displayed average 25,108.90 is confirmed as **2.40 pt ($384)**, matching the documented H1 accounting gap.
