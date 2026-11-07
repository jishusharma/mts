# Gemini Blind Read: `cryptocred_s3_pooled_2026-11/RESULT_10SYM.md`

- **Card:** `gemini-blind-read-of-cc-s3-10sym-result-`
- **Model:** `gemini-4-argon-medium`
- **Date:** 2026-11-07
- **Folder Data Read First:** `MyTradingSys/research/cryptocred_s3_pooled_2026-11/count_10sym.json`, `result_10sym.json`, `gate_output_10sym.txt`, `PRE_REG_10SYM.md`, `cc_s3_10sym_run.py`
- **Target Report:** `MyTradingSys/research/cryptocred_s3_pooled_2026-11/RESULT_10SYM.md`

## 1. Regime Mix & Power Gate Check

| Item | Folder Data (`result_10sym.json` / `gate_output_10sym.txt`) | `RESULT_10SYM.md` Prose | Diff |
|---|---|---|---|
| Regime mix (130 weeks DEV) | `130 weeks: bull 25 (19%) \| bear 0 (0%) \| range 105 (81%) \| n/a 0 (0%)` (`result_10sym.json:105`, OURS) | `130 weeks DEV ... bull 25 (19%) \| bear 0 (0%) \| range 105 (81%) \| n/a 0 (0%)` (`RESULT_10SYM.md:1`) | `0` (MATCH) |
| Power gate (`gate_output_10sym.txt:1`) | `n 1981 sd 1.24 m 221 z_holm 3.688 MDE 0.126 R + cost 0.068 = 0.194 vs max plausible gross 0.3; n needed 586` (`PASS: may freeze`, OURS) | `n 1981 (gate needed 586: PASS, gate_output_10sym.txt)`, `MDE 0.126 R` (`RESULT_10SYM.md:9,30`) | `0` (MATCH) |

## 2. Pooled Summary Table Diff (`result_10sym.json:2-12` vs `RESULT_10SYM.md:7-15`)

Recomputed pooled filled count from per-symbol counts:
$$\sum_{i=1}^{10} n_i = 207 + 202 + 193 + 212 + 198 + 188 + 178 + 203 + 200 + 200 = 1981$$
Recomputed pooled fee-net mean $R$ from weighted per-symbol means:
$$\frac{\sum_{i=1}^{10} n_i \cdot \bar{R}_{\text{net},i}}{1981} = \frac{-92.54463954731535}{1981} = -0.0467161229416029\text{ R}$$

| Pooled Metric | Recomputed / Raw (`result_10sym.json`) | Reported (`RESULT_10SYM.md:7-15`) | Diff (Reported - Raw) | Status |
|---|---|---|---|---|
| `n fills` | `1981` (`count_10sym.json:62`, `result_10sym.json:2`, OURS) | `1981` | `0` | MATCH |
| `fee-net mean R` | `-0.046716` (`result_10sym.json:3`, OURS) | `-0.0467` | `+0.000016` (4 d.p. rounding) | MATCH |
| `95 % day-block CI` | `[-0.109666, +0.016198]` (`result_10sym.json:4-5`, OURS) | `[-0.1097, +0.0162]` | `0.0000` (4 d.p. rounding) | MATCH |
| `two-sided p` | `0.153923` (`result_10sym.json:6`, OURS) | `0.154` | `+0.000077` (3 d.p. rounding) | MATCH |
| `Holm p (m = 221)` | `1.0` (`min(1.0, 221 * 0.153923) = 1.0`, `result_10sym.json:7-8`, OURS) | `1.000` | `0.000` | MATCH |
| `gross mean R` | `+0.003999` (`result_10sym.json:10`, OURS) | `+0.0040` | `+0.000001` (4 d.p. rounding) | MATCH |
| `measured sd of R` | `1.224303` (`result_10sym.json:9`, OURS) | `1.224` | `-0.000303` (3 d.p. rounding) | MATCH |
| `symbols with fee-net mean R > 0` | `2` (`BNBUSDT +0.083038`, `AVAXUSDT +0.021296`, `result_10sym.json:11`, OURS) | `2 of 10` | `0` | MATCH |
| `verdict` | `FAIL` ($\bar{R}_{\text{net}} = -0.0467 \le 0$, `PRE_REG_10SYM.md:31`, OURS) | `FAIL` | `0` | MATCH |

## 3. Per-Symbol Table Diff (`result_10sym.json:13-103` & `PRE_REG_10SYM.md:22` vs `RESULT_10SYM.md:17-28`)

| Symbol | Tick (`PRE_REG_10SYM.md:22`) | Signals (Raw / Rep) | Filled $n$ (Raw / Rep) | Unfilled | Fee-Net Mean $R$ Raw | Fee-Net Mean $R$ Rep | Hit $1.5\text{ R}$ Raw | Hit $1.5\text{ R}$ Rep | Cell Diff |
|---|---|---|---|---|---|---|---|---|---|
| `BTCUSDT` | `0.1` / `0.1` | `217` / `217` | `207` / `207` | `10` | `-0.132913` | `-0.133` | `37.681 %` | `37.7 %` | `0` (MATCH) |
| `ETHUSDT` | `0.01` / `0.01` | `210` / `210` | `202` / `202` | `8` | `-0.045722` | `-0.046` | `40.594 %` | `40.6 %` | `0` (MATCH) |
| `SOLUSDT` | `0.01` / `0.01` | `205` / `205` | `193` / `193` | `12` | `-0.103090` | `-0.103` | `36.788 %` | `36.8 %` | `0` (MATCH) |
| `BNBUSDT` | `0.01` / `0.01` | `222` / `222` | `212` / `212` | `10` | `+0.083038` | `+0.083` | `45.755 %` | `45.8 %` | `0` (MATCH) |
| `XRPUSDT` | `0.0001` / `0.0001` | `205` / `205` | `198` / `198` | `7` | `-0.008023` | `-0.008` | `41.414 %` | `41.4 %` | `0` (MATCH) |
| `DOGEUSDT` | `0.00001` / `0.00001` | `196` / `196` | `188` / `188` | `8` | `-0.060789` | `-0.061` | `39.362 %` | `39.4 %` | `0` (MATCH) |
| `ADAUSDT` | `0.0001` / `0.0001` | `189` / `189` | `178` / `178` | `11` | `-0.053472` | `-0.053` | `39.326 %` | `39.3 %` | `0` (MATCH) |
| `AVAXUSDT` | `0.001` / `0.001` | `210` / `210` | `203` / `203` | `7` | `+0.021296` | `+0.021` | `42.365 %` | `42.4 %` | `0` (MATCH) |
| `LINKUSDT` | `0.001` / `0.001` | `209` / `209` | `200` / `200` | `9` | `-0.065118` | `-0.065` | `39.000 %` | `39.0 %` | `0` (MATCH) |
| `LTCUSDT` | `0.01` / `0.01` | `207` / `207` | `200` / `200` | `7` | `-0.111340` | `-0.111` | `37.500 %` | `37.5 %` | `0` (MATCH) |

- **Archive bar counts (`count_10sym.json` / `result_10sym.json`):** 7 symbols have `1,313,280` 1m bars; `SOLUSDT`, `XRPUSDT`, and `LTCUSDT` have `1,306,080` 1m bars (`1,313,280 - 1,306,080 = 7,200` missing 1m bars each, matching `RESULT_10SYM.md:30` and `PRE_REG_10SYM.md:23`, SOURCED `MANIFEST.md`).
- **All cells and prose claims verified:** 0 discrepancies found across all pooled and per-symbol numbers.

VERDICT: MATCH
