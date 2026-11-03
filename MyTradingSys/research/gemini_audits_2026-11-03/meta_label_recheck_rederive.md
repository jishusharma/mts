FOUND: 21 | DIFF: 0 | NOT_IN_DATA: 0

# Independent Re-derivation: Meta-Label Recheck Numbers (`RECHECK.md`)

- **Card:** `gemini-recheck-meta-label-bh-nneed-1103`
- **Auditor:** Gemini (independent cross-vendor review of GPT/Codex producer commit `dc8e33291`)
- **Date (UTC):** 2026-11-03
- **Sources Audited:**
  - `MyTradingSys/research/layer_lab/meta_label_recheck_1103/RECHECK.md`
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/numbers.json`
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/PRE_REG_EXT.md`
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/RESULT.md`

---

## 1. Item-by-Item Verification Table

| Item / Claim in `RECHECK.md` | Stated Value | Computed / Verified Value | Source File:Line | Status |
|---|---|---|---|---|
| Placebo p-value formula | `7/301` | `0.023255813953488372` | `numbers.json:47`, `PRE_REG_EXT.md:12` | FOUND |
| Shuffled placebo count | 300 shuffles (+1 real = 301) | 300 shuffles | `PRE_REG_EXT.md:12`, `numbers.json:44` | FOUND |
| Family size $m$ | 2 | 2 | `PRE_REG_EXT.md:13`, `numbers.json:502` | FOUND |
| BH $q$ with duplicated $p$ (`[p, p]`) | `0.023255813953488372` | `0.023255813953488372` | `numbers.json:501` | FOUND |
| Comparison P0 nonpassing $p$ | 0.60 | 0.60 | `RESULT.md:19` | FOUND |
| BH correction $q_{(1)}$ with $p=0.60$ | `min(2*0.023256, 0.60) = 0.046512` | `0.046511627906976744` | Arithmetic from `numbers.json:47`, `RESULT.md:19` | FOUND |
| Holm adjustment $p$ ($m=2$) | `0.046512` | `0.046511627906976744` | `numbers.json:500` | FOUND |
| Top-tercile sample count $n_{top}$ | 139 | 139 | `numbers.json:10` | FOUND |
| Realized minimum detectable effect $\delta_{min}$ | 0.509289 R | `0.509289099934907` R | `numbers.json:50` | FOUND |
| Implied standard deviation $sd$ from $\delta_{min}$ | 2.143209 R | `0.509289099934907 / sqrt(7.849 / 139) = 2.143209456617` R | Re-derived from `numbers.json:10,50` | FOUND |
| $n_{need}$ for 0.30 R lift (realized $sd$) | 401 | `ceil(7.849 * (2.143209456617 / 0.30)^2) = 401` | `numbers.json:201`, `PRE_REG_EXT.md:21` | FOUND |
| Prior standard deviation $sd_{prior}$ | 2.3817 R | 2.3817 R | `PRE_REG_EXT.md:3,21` | FOUND |
| $n_{need}$ from prior $sd$ | 495 | `ceil(7.849 * (2.3817 / 0.30)^2) = 495` | `PRE_REG_EXT.md:21` | FOUND |
| Trade count threshold condition ($< 100$) | $139 \ge 100 \implies$ FALSE | $139 \ge 100$ | `numbers.json:10`, `PRE_REG_EXT.md:18` | FOUND |
| Top-tercile 95% day-block CI | `[+0.028402, +0.869065]` R | `[0.028402001017956174, 0.8690648043906535]` R | `numbers.json:31-34` | FOUND |
| Conditional power-floor trigger | False (95% CI strictly $> 0$) | CI does not span 0; conditional branch does not fire | `PRE_REG_EXT.md:18`, `numbers.json:31-34` | FOUND |
| Top-tercile fee-net mean | `+0.429609` R | `0.4296087377127243` R $> 0$ | `numbers.json:14`, `PRE_REG_EXT.md:18` | FOUND |
| Real top-minus-bottom spread | `+0.644763` R | `0.6447628513105128` R | `numbers.json:39` | FOUND |
| Placebo 95th percentile spread | `+0.521435` R | `0.5214348375382599` R | `numbers.json:45` | FOUND |
| Spread $>$ Placebo p95 condition | $0.644763 > 0.521435 \implies$ TRUE | Spread exceeds placebo p95 | `numbers.json:39,45`, `PRE_REG_EXT.md:18` | FOUND |
| Top-tercile 97.5% CI (reported beside) | `[-0.023873, +0.937316]` R | `[-0.023873377173401447, 0.9373159399292992]` R | `numbers.json:35-38` | FOUND |
| Arithmetic pooled $n_{top}$ ($162 + 139$) | 301 | 301 | `RESULT.md:19`, `numbers.json:503` | FOUND |

---

## 2. Frozen-Rule Decision Reading (`PRE_REG_EXT.md:18`)

`PRE_REG_EXT.md:18` establishes the exact classification logic:
1. `NOT ENOUGH DATA`:
   - Condition A: Fewer than 100 trades in top tercile ($n_{top} < 100$). Stated $n_{top} = 139 \ge 100$, so Condition A is FALSE.
   - Condition B: 95% CI spans 0 while $n_{top} < n_{need}$. 95% CI is `[+0.028402, +0.869065] R`, which is strictly positive and does NOT span 0. Therefore Condition B is FALSE.
2. `PASSED`:
   - Top-tercile fee-net mean $> 0$: `+0.429609 R > 0` (PASS).
   - 95% day-block CI lower bound $> 0$: `+0.028402 R > 0` (PASS).
   - Real spread $>$ placebo 95th percentile: `+0.644763 R > +0.521435 R` (PASS).

Result: The frozen rule literal verdict is **PASS STANDS** (`PRE_REG_EXT.md:18`), confirming the conclusion in `RECHECK.md:1,19`.

---

Noticed: Although the literal rule passes because the 95% CI lower bound is slightly above zero (+0.028 R), the 97.5% CI spans zero (-0.024 R), the realized sample (139) is well below the 401 trades needed to resolve a 0.30 R lift, and the ranking across terciles is non-monotone (middle -0.355 R is worse than bottom -0.215 R); the report's conservative parking of the setup without touching validation data adheres strictly to protocol.
