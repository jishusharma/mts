AGREE

# Blind Re-derivation: `rsi_range_census_2026-11-13`

## 1. Frozen Rule from `PRE_REG.md` (read before `results.json` and `REPORT.md`)

- **Verdict / Pass-Fail Rule**: None (`SOURCED`).
  - `MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:1`: `# PRE_REG: RSI range census (descriptive, no trade rule)`
  - `MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:20`: `- No pass rule (descriptive). Cells with n < 30 flagged. Overlapping forward windows: n counts episodes, not independent samples.`
- **Decision Cell / Threshold**: No trade rule or decision cell (`MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:6-9`, `SOURCED`).
  - `MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:16`: `- Bands (OURS, operator words): rarely hit = below own 1st pct; sometimes hit = 1st-5th pct; common = above 5th.` (`SOURCED`).
- **Sample Count (`n`)**:
  - `MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:17`: `- Episode = run of consecutive closed bars below a threshold; counted by start year.` (`SOURCED`).
  - `MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:20`: cells with `n < 30` flagged (`SOURCED`).
- **Cost / Fee**:
  - `MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:19`: forward returns are `gross of fees` at `+1/4/12/24/72` bars (`SOURCED`).

Expected pass/fail test: **DESCRIPTIVE (no pass/fail rule)**; check that `REPORT.md` declares no pass rule, flags `n < 30` cells, and reports `n` and forward-return statistics consistent with `results.json`.

---

## 2. Re-derivation from `results.json`

Source: `MyTradingSys/research/rsi_range_census_2026-11-13/results.json` (top-level keys: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BTC_LONG`).

### Formulas (`OURS`)

For Section 3 (`sec3[thr]` across the 9 daily-RSI buckets `<25`, `25-30`, `30-35`, `35-40`, `40-45`, `45-50`, `50-60`, `60-70`, `>70`):

$$n_{\text{ALL}} = \sum_{b \in \text{buckets}} n_b$$

$$\text{mean}_{\text{ALL}}(h) = \frac{\sum_{b \in \text{buckets}} n_{b,h} \cdot \text{mean}_{b,h}}{\sum_{b \in \text{buckets}} n_{b,h}}, \qquad h \in \{1, 4, 12, 24, 72\}$$

For Section 1 (`sec1[tf]`):

$$\text{eps\_total}(\text{thr}) = \sum_{y \in \text{years}} \text{eps}(\text{thr}, y)$$

### Recomputed `sec3` Pooled (`ALL`) Means & Episode Counts (`OURS`, from `results.json`)

| Symbol | Threshold | Recomputed `n` (`sum(n_b)`) | `+1h` mean (%) | `+4h` mean (%) | `+12h` mean (%) | `+24h` mean (%) | `+72h` mean (%) | `n < 30` flag |
|---|---|---|---|---|---|---|---|---|
| `BTCUSDT` | `<=30` | `797` (`796` at `+72h`) | `+0.02` (`0.0193`) | `+0.09` (`0.0869`) | `-0.02` (`-0.0174`) | `+0.12` (`0.1212`) | `+0.40` (`0.3973`) | No |
| `BTCUSDT` | `<=25` | `384` (`379` at `+72h`) | `+0.10` (`0.0995`) | `+0.12` (`0.1228`) | `-0.09` (`-0.0892`) | `+0.19` (`0.1943`) | `+0.23` (`0.2254`) | No |
| `BTCUSDT` | `<=20` | `138` (`137` at `+24h`, `136` at `+72h`) | `+0.20` (`0.1985`) | `+0.32` (`0.3190`) | `+0.13` (`0.1345`) | `+0.40` (`0.3965`) | `+0.66` (`0.6600`) | No |
| `BTCUSDT` | `<=15` | `29` (`28` at `+72h`) | `-0.12` | `+0.23` | `+0.16` | `+0.46` | `+0.76` | **Yes (`*`)** |
| `BTCUSDT` | `<=10` | `5` (`4` at `+72h`) | `+1.05` | `+1.31` | `+1.85` | `+2.13` | `+5.81` | **Yes (`*`)** |
| `ETHUSDT` | `<=30` | `704` (`701` at `+72h`) | `+0.02` | `+0.06` | `-0.05` | `-0.04` | `+0.01` | No |
| `ETHUSDT` | `<=25` | `342` (`340` at `+72h`) | `+0.01` | `-0.03` | `-0.24` | `-0.33` | `-0.95` | No |
| `ETHUSDT` | `<=20` | `119` (`118` at `+72h`) | `-0.06` | `-0.13` | `-0.24` | `+0.36` | `-0.23` | No |
| `ETHUSDT` | `<=15` | `44` (`43` at `+72h`) | `-0.03` | `+0.38` | `+0.27` | `+1.69` | `+1.10` | No |
| `ETHUSDT` | `<=10` | `6` | `+0.64` | `+0.98` | `+1.73` | `+3.71` | `+2.99` | **Yes (`*`)** |
| `SOLUSDT` | `<=30` | `595` (`592` at `+72h`) | `+0.16` | `+0.23` | `+0.18` | `+0.16` | `+0.19` | No |
| `SOLUSDT` | `<=25` | `256` (`254` at `+72h`) | `+0.08` | `+0.11` | `+0.13` | `+0.15` | `-1.06` | No |
| `SOLUSDT` | `<=20` | `80` (`79` at `+72h`) | `+0.69` | `+0.48` | `+1.76` | `+2.61` | `+0.86` | No |
| `SOLUSDT` | `<=15` | `18` | `+0.01` | `+0.35` | `+1.30` | `+0.43` | `+2.87` | **Yes (`*`)** |
| `SOLUSDT` | `<=10` | `1` | `+2.71` | `+6.24` | `+7.06` | `+11.01` | `+9.50` | **Yes (`*`)** |

All 75 weighted means (`3 symbols × 5 thresholds × 5 horizons`) match `results.json` `ALL[h]["mean"]` to within `1e-9` (`OURS`). All `sec1` `eps_total` values across all 3 symbols and 6 timeframes match `sum(eps[year])` (`OURS`).

PASS/FAIL call: **DESCRIPTIVE, no pass/fail rule** (`MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md:20`, `SOURCED`).

---

## 3. Claim-by-Claim Comparison with `REPORT.md`

| Claim | Claimed (`REPORT.md`) | Recomputed (`PRE_REG.md` / `results.json`) | Status | Source (`file:line`) |
|---|---|---|---|---|
| Headline verdict | `**Verdict: DESCRIPTIVE, no trade rule, no pass rule.**` | Descriptive census, no trade rule, no pass rule (`n < 30` flagged) | **MATCH** | [REPORT.md:3](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L3) ; [PRE_REG.md:20](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md#L20) |
| BTC 1st & 5th pct (5m–1d) and 1w min | `below about 22-24 is the 1st percentile, below about 30-32 the 5th. Weekly is tighter (1st pct 27.0, all-time low 25.7 in 2022-06; the 2013+ daily-built weekly low is also 25.7).` | `p1`: 5m `23.70`, 15m `22.92`, 1h `22.34`, 4h `22.57`, 1d `23.78`; `p5`: `32.32`, `31.73`, `30.44`, `30.93`, `32.00`; 1w `p1=27.03`, `min=25.71` (`2022-06-27`); `BTC_LONG.1w.min=25.72` (`2022-06-27`) | **MATCH** | [REPORT.md:11](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L11) ; [REPORT.md:25-30](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L25-L30) ; [REPORT.md:194](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L194) |
| BTC `1h \| 1d` share touching `<30` when daily `<25` vs `>70` | `42%` (`41.9%`, `n=31`) vs `13%` (`12.8%`, `n=242`) | `<25`: `n=31`, `lt30=41.94%`; `>70`: `n=242`, `lt30=12.81%` | **MATCH** | [REPORT.md:15](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L15) ; [REPORT.md:204](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L204) ; [REPORT.md:212](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L212) |
| BTC 1h `<=20` pooled (`ALL`) forward returns & drop24 | `n=138`; `+24h` med `+0.17%` (~`+0.2%`), mean `+0.40%`, `51%` pos; `+72h` mean `+0.66%`; `drop24` med `-2.79%` (~`-2.8%`), `-2.52` ATR (~`2.5`) | `n=138` (`137` at `+24h`, `136` at `+72h`); `+24h` med `+0.17%`, weighted mean `+0.40%`, `51.09%` pos; `+72h` weighted mean `+0.66%`; `dd_med=-2.79%`, `ddatr_med=-2.52` | **MATCH** | [REPORT.md:17](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L17) ; [REPORT.md:393](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L393) |
| BTC 1h `<=30` pooled (`ALL`) `n` and means | `n=797`; `+1h` `+0.02`, `+4h` `+0.09`, `+12h` `-0.02`, `+24h` `+0.12`, `+72h` `+0.40` | `sum(n_b)=797`; weighted means `+0.02`, `+0.09`, `-0.02`, `+0.12`, `+0.40` | **MATCH** | [REPORT.md:359](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L359) |
| ETH 1h `<=20` pooled (`ALL`) `n` and means | `n=119`; `+1h` `-0.06`, `+4h` `-0.13`, `+12h` `-0.24`, `+24h` `+0.36`, `+72h` `-0.23` | `sum(n_b)=119`; weighted means `-0.06`, `-0.13`, `-0.24`, `+0.36`, `-0.23` | **MATCH** | [REPORT.md:471](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L471) |
| SOL 1h `<=20` pooled (`ALL`) `n` and means | `n=80`; `+1h` `+0.69`, `+4h` `+0.48`, `+12h` `+1.76`, `+24h` `+2.61`, `+72h` `+0.86` | `sum(n_b)=80`; weighted means `+0.69`, `+0.48`, `+1.76`, `+2.61`, `+0.86` | **MATCH** | [REPORT.md:550](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L550) |
| Section 4 live BTC snapshot (`2026-11-13 16:08 UTC`) & raw 5m kline-to-RSI series | `5m` `42.6`, `15m` `46.3`, `1h` `33.6`, `4h` `23.3`, `1d` `29.6`, `1w` `47.9` | Not in `results.json`; raw Bybit 5m klines not stored in repo | **UNVERIFIABLE** | [REPORT.md:574-585](file:///C:/Users/e-ngineers/.gemini/mts-gq/rederive-rsi-range-census-gemini2-1114/MyTradingSys/research/rsi_range_census_2026-11-13/REPORT.md#L574-L585) |
