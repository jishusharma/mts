# Blind Read: Malkan Window Bands with Wide Pivots (`malkan_window_wide_2026-11`)

- **Card**: `gemini-blind-read-malkan-window-wide-1106`
- **Reader**: Gemini (independent blind read worker), 2026-11-06
- **Target Study**: `MyTradingSys/research/malkan_window_wide_2026-11/RESULT.md`
- **Pre-Registration**: `MyTradingSys/research/malkan_window_wide_2026-11/PRE_REG.md`
- **Source Data Files**:
  - `MyTradingSys/research/malkan_window_wide_2026-11/counts.csv`
  - `MyTradingSys/research/malkan_window_wide_2026-11/gate_lines.csv`
  - `MyTradingSys/research/malkan_window_wide_2026-11/symbols.json`
  - `MyTradingSys/research/malkan_window_wide_2026-11/regime_mix_count.txt`
  - Raw 1m klines: `F:/MTS/data/tom_raw/klines/<SYM>USDT-1m-*.csv` (10 symbols)
- **Verification Test Command**:
  `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/layer_lab/reports/2026-11-06_BLIND_READ_MALKAN_WIDE_1106.md'); assert p.exists() and 'VERDICT' in p.read_text()"`

---

## 1. Protocol Adherence & Blind Read Methodology

The blind read protocol was strictly followed:
1. `PRE_REG.md`, `counts.csv`, `gate_lines.csv`, `symbols.json`, and `regime_mix_count.txt` were inspected line-by-line prior to synthesizing any conclusions.
2. All raw 1m kline data across the 10 pre-registered USD-M symbols (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `XRPUSDT`, `DOGEUSDT`, `ADAUSDT`, `AVAXUSDT`, `LINKUSDT`, `LTCUSDT`) were processed independently across the DEV window (`2022-01-01` to `2024-06-30` UTC, ending strictly before `2024-07-01 00:00:00 UTC`).
3. Pivots of strength $L=3$ (confirmed at bar $b+L$, causal), regular close-to-close divergences with 14-period RSI, swing distance between 3 and 50 bars, and 10-bar forward return distributions were computed from raw data independently of the study's runtime scripts.
4. MDE calculations, Holm family adjustments ($m=238$), and the $0.30\%$ power gate were recomputed and compared against `gate_lines.csv` and `RESULT.md`.

---

## 2. Per-Claim Verification Table

Every quoted number, parameter, and narrative statement from `RESULT.md`, `counts.csv`, `gate_lines.csv`, `symbols.json`, and `PRE_REG.md` is cross-verified below. All numbers are labeled **SOURCED** (with exact `file:line` citation) or **OURS** (independently recomputed).

| # | Item / Claim Description | SOURCED Citation & Quoted Value | OURS (Independently Recomputed / Verified) | Status |
|---|---|---|---|---|
| 1 | Overall study verdict | SOURCED `RESULT.md:1`: `BLOCKED` | OURS: All 8 (TF, band) cells fail power gate (MDE+cost > 0.30%); matches `PRE_REG.md:27` verdict rule | MATCH |
| 2 | Window regime mix total weeks | SOURCED `RESULT.md:2`, `regime_mix_count.txt:1`: `130 weeks` | OURS: 2022-01-01 to 2024-07-01 = 130 weeks | MATCH |
| 3 | Bull regime count & share | SOURCED `RESULT.md:2`, `regime_mix_count.txt:1`: `bull 25 (19%)` | OURS: 25 weeks / 130 weeks = 19.23% -> 19% | MATCH |
| 4 | Bear regime count & share | SOURCED `RESULT.md:2`, `regime_mix_count.txt:1`: `bear 0 (0%)` | OURS: 0 weeks / 130 weeks = 0.00% -> 0% | MATCH |
| 5 | Range regime count & share | SOURCED `RESULT.md:2`, `regime_mix_count.txt:1`: `range 105 (81%)` | OURS: 105 weeks / 130 weeks = 80.77% -> 81% | MATCH |
| 6 | N/A regime count & share | SOURCED `RESULT.md:2`, `regime_mix_count.txt:1`: `n/a 0 (0%)` | OURS: 0 weeks / 130 weeks = 0.00% -> 0% | MATCH |
| 7 | Pivot strength parameter | SOURCED `RESULT.md:6`, `PRE_REG.md:11`: `Pivot strength 3 (OURS)` | OURS: 3 lookaround bars each side | MATCH |
| 8 | Round-trip trading cost | SOURCED `RESULT.md:6`, `PRE_REG.md:17`: `cost 0.14 %` | OURS: 0.14% round trip (`research_kit.TAKER_RT_PCT`) | MATCH |
| 9 | Exit horizon | SOURCED `RESULT.md:6`, `PRE_REG.md:16`: `exit 10 bars` | OURS: exit close 10 bars after confirmation bar | MATCH |
| 10 | Clustering dimension | SOURCED `RESULT.md:6`, `PRE_REG.md:18`: `cluster = symbol x day` | OURS: distinct symbol x UTC calendar day | MATCH |
| 11 | Holm family size m | SOURCED `RESULT.md:6`, `gate_lines.csv:2-9`: `Holm m = 238 (222 repo-wide DEV + 16 new cells)` | OURS: 222 (from `verdicts.count_with_ledger` at commit `934d47597575`) + 16 new cells = 238 | MATCH |
| 12 | Loader cutoff date | SOURCED `RESULT.md:6,27`, `PRE_REG.md:15`: `Bars from 2024-07-01 never opened` | OURS: DEV cutoff `2024-07-01 00:00:00 UTC` enforced by loader | MATCH |
| 13 | Number of symbols loaded | SOURCED `RESULT.md:7`, `PRE_REG.md:13`: `all 10 loaded` | OURS: 10 symbols loaded (`BTC`, `ETH`, `SOL`, `BNB`, `XRP`, `DOGE`, `ADA`, `AVAX`, `LINK`, `LTC`) | MATCH |
| 14 | Symbol 1h bar range | SOURCED `RESULT.md:7`: `21768-21888 1h bars each` | OURS: min bars = 21768 (`SOL`, `XRP`, `LTC`), max bars = 21888 (`BTC`, `ETH`, `BNB`, `DOGE`, `ADA`, `AVAX`, `LINK`) from `symbols.json:1-42` | MATCH |
| 15 | No-signal exclusion floor | SOURCED `RESULT.md:7`, `PRE_REG.md:14`: `above the 7200 floor; none no-signal` | OURS: all 10 symbols have >= 21768 bars, none excluded | MATCH |
| 16 | 1h S3_10 events n | SOURCED `RESULT.md:11`, `gate_lines.csv:5`: `2359` | OURS: 1119 bearish + 1240 bullish (`counts.csv:5,9`) = 2359 events | MATCH |
| 17 | 1h S3_10 days | SOURCED `RESULT.md:11`, `gate_lines.csv:5`: `2119` | OURS: 2119 distinct symbol-days across both sides | MATCH |
| 18 | 1h S3_10 10-bar return sd | SOURCED `RESULT.md:11`, `gate_lines.csv:5`: `2.795` | OURS: raw pooled sd = 2.7954335% -> round(sd, 3) = 2.795 | MATCH |
| 19 | 1h S3_10 MDE + cost | SOURCED `RESULT.md:11`, `gate_lines.csv:5`: `0.416` | OURS: MDE = (3.70657 + 0.84)*2.79543/sqrt(2119) = 0.27608%; + 0.14% = 0.41608% -> 0.416 | MATCH |
| 20 | 1h S3_10 gate | SOURCED `RESULT.md:11`, `gate_lines.csv:5`: `BLOCK` | OURS: 0.416% > 0.30% max plausible gross -> BLOCK | MATCH |
| 21 | 1h B11_12 events n | SOURCED `RESULT.md:12`, `gate_lines.csv:2`: `443` | OURS: 211 bearish + 232 bullish (`counts.csv:2,6`) = 443 events | MATCH |
| 22 | 1h B11_12 days | SOURCED `RESULT.md:12`, `gate_lines.csv:2`: `432` | OURS: 432 distinct symbol-days | MATCH |
| 23 | 1h B11_12 10-bar return sd | SOURCED `RESULT.md:12`, `gate_lines.csv:2`: `2.795` | OURS: 2.795% | MATCH |
| 24 | 1h B11_12 MDE + cost | SOURCED `RESULT.md:12`, `gate_lines.csv:2`: `0.751` | OURS: MDE = 0.61144%; + 0.14% = 0.75144% -> 0.751 | MATCH |
| 25 | 1h B11_12 gate | SOURCED `RESULT.md:12`, `gate_lines.csv:2`: `BLOCK` | OURS: 0.751% > 0.30% -> BLOCK | MATCH |
| 26 | 1h C13_18 events n | SOURCED `RESULT.md:13`, `gate_lines.csv:3`: `487` | OURS: 228 bearish + 259 bullish (`counts.csv:3,7`) = 487 events | MATCH |
| 27 | 1h C13_18 days | SOURCED `RESULT.md:13`, `gate_lines.csv:3`: `479` | OURS: 479 distinct symbol-days | MATCH |
| 28 | 1h C13_18 10-bar return sd | SOURCED `RESULT.md:13`, `gate_lines.csv:3`: `2.795` | OURS: 2.795% | MATCH |
| 29 | 1h C13_18 MDE + cost | SOURCED `RESULT.md:13`, `gate_lines.csv:3`: `0.721` | OURS: MDE = 0.58063%; + 0.14% = 0.72063% -> 0.721 | MATCH |
| 30 | 1h C13_18 gate | SOURCED `RESULT.md:13`, `gate_lines.csv:3`: `BLOCK` | OURS: 0.721% > 0.30% -> BLOCK | MATCH |
| 31 | 1h D19_50 events n | SOURCED `RESULT.md:14`, `gate_lines.csv:4`: `140` | OURS: 73 bearish + 67 bullish (`counts.csv:4,8`) = 140 events | MATCH |
| 32 | 1h D19_50 days | SOURCED `RESULT.md:14`, `gate_lines.csv:4`: `140` | OURS: 140 distinct symbol-days | MATCH |
| 33 | 1h D19_50 10-bar return sd | SOURCED `RESULT.md:14`, `gate_lines.csv:4`: `2.795` | OURS: 2.795% | MATCH |
| 34 | 1h D19_50 MDE + cost | SOURCED `RESULT.md:14`, `gate_lines.csv:4`: `1.214` | OURS: MDE = 1.07400%; + 0.14% = 1.21400% -> 1.214 | MATCH |
| 35 | 1h D19_50 gate | SOURCED `RESULT.md:14`, `gate_lines.csv:4`: `BLOCK` | OURS: 1.214% > 0.30% -> BLOCK | MATCH |
| 36 | 4h S3_10 events n | SOURCED `RESULT.md:15`, `gate_lines.csv:9`: `599` | OURS: 298 bearish + 301 bullish (`counts.csv:13,17`) = 599 events | MATCH |
| 37 | 4h S3_10 days | SOURCED `RESULT.md:15`, `gate_lines.csv:9`: `591` | OURS: 591 distinct symbol-days across both sides | MATCH |
| 38 | 4h S3_10 10-bar return sd | SOURCED `RESULT.md:15`, `gate_lines.csv:9`: `5.454` | OURS: raw pooled sd = 5.4543829% -> round(sd, 3) = 5.454 | MATCH |
| 39 | 4h S3_10 MDE + cost | SOURCED `RESULT.md:15`, `gate_lines.csv:9`: `1.160` | OURS: MDE = (3.70657 + 0.84)*5.45438/sqrt(591) = 1.01997%; + 0.14% = 1.15997% -> 1.160 | MATCH |
| 40 | 4h S3_10 gate | SOURCED `RESULT.md:15`, `gate_lines.csv:9`: `BLOCK` | OURS: 1.160% > 0.30% -> BLOCK | MATCH |
| 41 | 4h B11_12 events n | SOURCED `RESULT.md:16`, `gate_lines.csv:6`: `116` | OURS: 53 bearish + 63 bullish (`counts.csv:10,14`) = 116 events | MATCH |
| 42 | 4h B11_12 days | SOURCED `RESULT.md:16`, `gate_lines.csv:6`: `116` | OURS: 116 distinct symbol-days | MATCH |
| 43 | 4h B11_12 10-bar return sd | SOURCED `RESULT.md:16`, `gate_lines.csv:6`: `5.454` | OURS: 5.454% | MATCH |
| 44 | 4h B11_12 MDE + cost | SOURCED `RESULT.md:16`, `gate_lines.csv:6`: `2.443` | OURS: MDE = (3.70657 + 0.84)*5.45438/sqrt(116) = 2.30251%; + 0.14% = 2.44251% -> round 2.443 | MATCH |
| 45 | 4h B11_12 gate | SOURCED `RESULT.md:16`, `gate_lines.csv:6`: `BLOCK` | OURS: 2.443% > 0.30% -> BLOCK | MATCH |
| 46 | 4h C13_18 events n | SOURCED `RESULT.md:17`, `gate_lines.csv:7`: `158` | OURS: 74 bearish + 84 bullish (`counts.csv:11,15`) = 158 events | MATCH |
| 47 | 4h C13_18 days | SOURCED `RESULT.md:17`, `gate_lines.csv:7`: `158` | OURS: 158 distinct symbol-days | MATCH |
| 48 | 4h C13_18 10-bar return sd | SOURCED `RESULT.md:17`, `gate_lines.csv:7`: `5.454` | OURS: 5.454% | MATCH |
| 49 | 4h C13_18 MDE + cost | SOURCED `RESULT.md:17`, `gate_lines.csv:7`: `2.113` | OURS: MDE = 1.97271%; + 0.14% = 2.11271% -> 2.113 | MATCH |
| 50 | 4h C13_18 gate | SOURCED `RESULT.md:17`, `gate_lines.csv:7`: `BLOCK` | OURS: 2.113% > 0.30% -> BLOCK | MATCH |
| 51 | 4h D19_50 events n | SOURCED `RESULT.md:18`, `gate_lines.csv:8`: `38` | OURS: 28 bearish + 10 bullish (`counts.csv:12,16`) = 38 events | MATCH |
| 52 | 4h D19_50 days | SOURCED `RESULT.md:18`, `gate_lines.csv:8`: `38` | OURS: 38 distinct symbol-days | MATCH |
| 53 | 4h D19_50 10-bar return sd | SOURCED `RESULT.md:18`, `gate_lines.csv:8`: `5.454` | OURS: 5.454% | MATCH |
| 54 | 4h D19_50 MDE + cost | SOURCED `RESULT.md:18`, `gate_lines.csv:8`: `4.163` | OURS: MDE = 4.02257%; + 0.14% = 4.16257% -> 4.163 | MATCH |
| 55 | 4h D19_50 gate | SOURCED `RESULT.md:18`, `gate_lines.csv:8`: `BLOCK` | OURS: 4.163% > 0.30% -> BLOCK | MATCH |
| 56 | Plausible gross ceiling | SOURCED `RESULT.md:20`, `PRE_REG.md:24`, `prereg_gate.py:21`: `0.30 %` | OURS: `MAX_PLAUSIBLE_GROSS = 0.30` | MATCH |
| 57 | Fixed detector OURS events (1h) | SOURCED `RESULT.md:23`: `1h 1070` | OURS: 443 (B11_12) + 487 (C13_18) + 140 (D19_50) = 1070 events | MATCH |
| 58 | Fixed detector OURS events (4h) | SOURCED `RESULT.md:23`: `4h 312 events` | OURS: 116 (B11_12) + 158 (C13_18) + 38 (D19_50) = 312 events | MATCH |
| 59 | Headline claim on 1h S3_10 days | SOURCED `RESULT.md:24`: `2119 days` | OURS: 2119 distinct symbol-days | MATCH |
| 60 | Headline claim on 1h return sd | SOURCED `RESULT.md:24`: `2.8 %` | OURS: 2.795% rounds to 2.8% | MATCH |
| 61 | Headline claim on repo Holm m | SOURCED `RESULT.md:24`: `238` | OURS: 238 | MATCH |
| 62 | Minimum detectable net quote | SOURCED `RESULT.md:24`: `0.42 %` | OURS: 0.416% rounds to 0.42% | MATCH |
| 63 | No-outcome assertion | SOURCED `RESULT.md:25`: `No outcome was computed (--pass dev run only for passing bands: none). Not a PASS, not a FAIL.` | OURS: Confirmed `dev_cells.csv` was not created and no post-signal returns were evaluated | MATCH |
| 64 | Partitions not read | SOURCED `RESULT.md:27`: `Not read: VALIDATION, HOLDOUT, any bar from 2024-07-01.` | OURS: Strict adherence to DEV split boundary confirmed | MATCH |

---

## 3. Disaggregated Side Counts (`counts.csv`) Cross-Check

All 16 rows of `counts.csv` were verified against independent counts from the raw klines:

| Band | Direction | TF | SOURCED `counts.csv` Days | SOURCED `counts.csv` n | OURS Days | OURS n | Match |
|---|---|---|---|---|---|---|---|
| `B11_12` | bearish | 1h | 205 (line 2) | 211 (line 2) | 205 | 211 | MATCH |
| `C13_18` | bearish | 1h | 226 (line 3) | 228 (line 3) | 226 | 228 | MATCH |
| `D19_50` | bearish | 1h | 73 (line 4) | 73 (line 4) | 73 | 73 | MATCH |
| `S3_10` | bearish | 1h | 1024 (line 5) | 1119 (line 5) | 1024 | 1119 | MATCH |
| `B11_12` | bullish | 1h | 228 (line 6) | 232 (line 6) | 228 | 232 | MATCH |
| `C13_18` | bullish | 1h | 253 (line 7) | 259 (line 7) | 253 | 259 | MATCH |
| `D19_50` | bullish | 1h | 67 (line 8) | 67 (line 8) | 67 | 67 | MATCH |
| `S3_10` | bullish | 1h | 1123 (line 9) | 1240 (line 9) | 1123 | 1240 | MATCH |
| `B11_12` | bearish | 4h | 53 (line 10) | 53 (line 10) | 53 | 53 | MATCH |
| `C13_18` | bearish | 4h | 74 (line 11) | 74 (line 11) | 74 | 74 | MATCH |
| `D19_50` | bearish | 4h | 28 (line 12) | 28 (line 12) | 28 | 28 | MATCH |
| `S3_10` | bearish | 4h | 294 (line 13) | 298 (line 13) | 294 | 298 | MATCH |
| `B11_12` | bullish | 4h | 63 (line 14) | 63 (line 14) | 63 | 63 | MATCH |
| `C13_18` | bullish | 4h | 84 (line 15) | 84 (line 15) | 84 | 84 | MATCH |
| `D19_50` | bullish | 4h | 10 (line 16) | 10 (line 16) | 10 | 10 | MATCH |
| `S3_10` | bullish | 4h | 297 (line 17) | 301 (line 17) | 297 | 301 | MATCH |

---

## 4. Contradiction Analysis with `PRE_REG.md`

1. **Gate Formula & Decision Rule**:
   - `PRE_REG.md:24` specifies $MDE = (z_{holm} + 0.84) \times sd / \sqrt{days}$, BLOCK when $MDE + cost > 0.30\%$.
   - Recomputed values strictly obey this formula and threshold. Zero contradictions found.
2. **Outcome Suppression**:
   - `PRE_REG.md:25` mandates `--pass dev` computes returns ONLY for $(TF, band)$ that PASS the gate. Bands that BLOCK receive only counts and the gate line.
   - `RESULT.md:25` confirms no outcome returns were evaluated because all cells blocked. Zero contradictions found.
3. **Verdict Syntax**:
   - `PRE_REG.md:27` requires `BLOCKED when every band blocks` and `Verdict word first in RESULT.md`.
   - `RESULT.md:1` begins with `BLOCKED:`. Zero contradictions found.
4. **Data Isolation**:
   - `PRE_REG.md:15` mandates DEV window only (`2022-01-01` to `2024-07-01`) and forbids opening later files.
   - `RESULT.md:27` confirms strict adherence. Zero contradictions found.

---

## 5. Defects and Discrepancies

- Total discrete claims and table metrics checked: 80 (64 claims/metrics in Section 2 + 16 disaggregated rows in Section 3).
- Matching: 80 of 80 (100.0%).
- Contradictions with `PRE_REG.md`: 0.
- Defects cited: None.

---

VERDICT: MATCH
