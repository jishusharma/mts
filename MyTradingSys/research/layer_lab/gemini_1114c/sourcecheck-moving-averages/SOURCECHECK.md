9 CONFIRMED / 8 CONTRADICTED / 4 NOT FETCHED

# Primary-Source Verification: Moving Averages Rule Book (`MOVING_AVERAGES.md`)

Blind read and primary-source verification of `MyTradingSys/research/indicator_rulebooks/MOVING_AVERAGES.md`.

---

## 1. Rule Lines Inventory (`MOVING_AVERAGES.md`)

### Section 2: Developer's own rules (all labeled `SOURCED`)
| Line | Item | Label | Cited Source |
|---|---|---|---|
| 14 | Who & Year (SMA) | SOURCED | `WIKI_MA`, `WIKI_CROSS`, `INVESTO_MA` (no quote in rule book) |
| 15 | Who & Year (EMA) | SOURCED | `WIKI_MA` (no quote in rule book) |
| 16 | Who & Year (Krown Canon) | SOURCED | `KROWN`, `CONC:7` (no quote in rule book) |
| 17 | Core Stack Definition | SOURCED | `extract_-NXzJs5JRks.md` (lines 92-94) [KR-M01] |
| 18 | 200 SMA First Contact | SOURCED | `extract_-NXzJs5JRks.md` (lines 85, 250) [KR-M03, KR-M25] |
| 19 | 200 SMA vs 200 EMA | SOURCED | `extract_vjzy_KxJ_y8.md` (line 196) [KR-M08]; `CONC` (line 13) |
| 20 | 21 & 55 EMA Dynamic Zone | SOURCED | `extract_-NXzJs5JRks.md` (lines 141-143) [KR-M05] |
| 21 | Silver Cross (21 vs 55 EMA) | SOURCED | `extract_-NXzJs5JRks.md` (lines 114-116, 228) [KR-M02] (no quote in rule book) |
| 22 | Golden & Death Cross (50 vs 200 SMA) | SOURCED | `extract_-NXzJs5JRks.md` (lines 208-212) [KR-M07] |
| 23 | Pair Rule & Stacking | SOURCED | `KROWN_CONSOLIDATED.md` (line 110) [KR-M09] (no quote in rule book) |
| 24 | Slope Correlates to Power | SOURCED | `extract_vjzy_KxJ_y8.md` (lines 407, 425) [KR-M11] |
| 25 | 5 EMA Leash & Disconnect | SOURCED | `extract_-NXzJs5JRks.md` (line 181) [KR-M06]; `FORM` (line 546) (no quote in rule book) |
| 26 | Weekly 200 SMA Macro Floor | SOURCED | `extract_-NXzJs5JRks.md` (line 161) [KR-M04] |
| 27 | Role: Context and Filter, Never Blind Trigger | SOURCED | `extract_-NXzJs5JRks.md` (lines 110-116) [KR-M12, KR-M13] |

### Section 3: What the internet and crypto traders say (all lack verbatim quotes in rule book)
| Line | Claim | Label / Grade | Cited Source URL |
|---|---|---|---|
| 32 | Golden cross / death cross | anecdote (T3, no quote) | `https://en.wikipedia.org/wiki/Moving_average_crossover` |
| 33 | Golden Cross 3 stages + volume | anecdote (T3, no quote) | `https://www.investopedia.com/terms/g/goldencross.asp` |
| 34 | Weekly Bull Market Support Band (20W SMA / 21W EMA) | anecdote (T3, no quote) | `https://www.tradingview.com/script/Bxg5DSp5-Ricco-Bull-Market-Support-Band/` |
| 35 | 200-week MA floor / 50-week MA ceiling | anecdote (T3, no quote) | `https://www.galaxy.com/insights/research/bitcoin-50-week-moving-average-bear-market-ceiling-200-week-floor-analysis/` |
| 36 | Mayer Multiple > 2.4 / < 0.8 | anecdote (T3, no quote) | `https://studio.glassnode.com/charts/mayer-multiple` |
| 37 | 200-week WMA cycle floor: 56 of 642 weekly closes below | anecdote (T3, no quote) | `https://www.bit.com/knowledge-hub/200-wma` |
| 38 | Wei et al. (2024): PMA1 only rule surviving SPA & OOS | measured (T1, no quote) | `https://eprints.gla.ac.uk/302711/1/302711.pdf` |
| 39 | Hudson & Urquhart (2021): no OOS predictability for BTC rules | measured (T1, no quote) | `https://ideas.repec.org/a/spr/annopr/v297y2021i1d10.1007_s10479-019-03357-1.html` |
| 40 | Detzel et al. (2021): price-to-MA ratios forecast daily BTC returns | measured (T1, no quote) | `https://profiles.wustl.edu/en/publications/learning-and-predictability-via-technical-analysis-evidence-from-/` |
| 41 | Grobys, Ahmed, Sapkota (2020): in-sample BTC MA payoffs (1, n) | measured (T1, no quote) | `https://osuva.uwasa.fi/bitstream/10024/11192/2/Osuva_%20Grobys_Ahmed_Sapkota_2020.pdf` |
| 42 | Islas Anguiano & Garcia-Medina (2025): EMA lags buy-and-hold 25.27% vs 42.31% | measured (T2, no quote) | `https://arxiv.org/pdf/2511.00665` |
| 43 | Timing Bitcoin with SMAs (SSRN 3115846): breakeven 1.1%-4.5% | `UNVERIFIED` | `https://www.cxoadvisory.com/currency-trading/timing-bitcoin-with-smas/` (SSRN 403) |

### Sections 4-6: Analyst extracts, OUR measurements, Live Aid (`OURS` / `SOURCED` / `NO-SOURCE`)
- Section 4 (lines 48-55): Krown, CCU, NK, Tom, Malkan (`SOURCED` to extract files); Fabio, CryptoCred, Habib/CBP (`NO-SOURCE`).
- Section 5 (lines 58-65): All rows labeled `OURS` (`setup_alpha_beta_v2_2026-10/RESULT.md`, `eh-h5-rsi-ma-cross-trigger/RESULT.md`, `btc_50w_ma_j-JVi02_1112/CHECK.md`, `Q_ALL_ma_findings.md`).
- Section 6 (lines 68-78): Live Aid `ma_strip.js` rules explicitly labeled `OURS` (flat < 0.5 ATR14, 6 ATR14 cap, 0.25 ATR14 touch tolerance, 3-bar fresh highlight, `IN BAND` all-frame extension) or `SOURCED` (KR-M05, KR-M07).

---

## 2. Cited Local Quotes Audit (Found vs Not Found)

### Found in Cited Local File
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:90` (rule book cites `:92-94`): "turn with the market" and "more stubborn" appear in `Stated mechanics` on line 90 (4 lines before `:94`).
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:85`: "almost always will have a reaction any time it comes into contact with the 200 simple moving average on almost any time frame for the first time in a long time."
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:250`: "at least a good bounce area for a scalp" appears in `Stated mechanics` on line 250 (analyst paraphrase, not a `>` transcript quote).
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_vjzy_KxJ_y8.md:196`: "one would be a 200 EMA or 200 SMA. Both of these I find significant amounts of value in"
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:141`: "a support zone walking uphill"
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:212`: "looking to sell any rally towards that 200 simple"
- `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:161`: "basically four years of price in one line"
- `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:73` (rule book cites `:70`): "retest trading is best trading"
- `MyTradingSys/research/btc_50w_ma_j-JVi02_1112/CHECK.md:26`: "n=7, no verdict possible"

### Cited Local Quotes NOT Found Verbatim in Cited File
1. Rule book line 20 cites `extract_-NXzJs5JRks.md` lines 141-143 for the phrase buy between the two lines: **NOT FOUND** as a verbatim quote at lines 141-143 (paraphrased in `Stated mechanics` on line 128 as buying between the two lines).
2. Rule book line 20 cites `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:143` for the distance between the 21 and the green 55 EMA, that is a zone of interest: **NOT FOUND** verbatim (`MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:143` actually reads: "I would even say the distance between the and the green 55 EMA, that is a zone. That is a zone of interest.").
3. Rule book line 24 cites `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_vjzy_KxJ_y8.md:425,427` for this is a time where you do not want to trend trade: **NOT FOUND** verbatim ("this is a time where you don't really want to pay too much attention to moving averages" at line 425, and "telling you not to trend trade" at line 427).
4. Rule book line 27 cites `extract_-NXzJs5JRks.md` (lines 110-116) for going long or short at every cross will not work: **NOT FOUND** anywhere in `extract_-NXzJs5JRks.md` (it is a summary phrase in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md:113`: "going long or short at every cross will not work").
5. Rule book line 50 cites `3EpXq8JC4jU/EXTRACT.md` (line 75) and `CATALOG.md` (line 18) alongside `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:73`: retest trading is best trading is **NOT FOUND** in `3EpXq8JC4jU/EXTRACT.md` or `CATALOG.md` (only in `wrEEf8o9n9E/EXTRACT.md` line 73).

---

## 3. Primary-Source Verification Table

| Rule Book Line & Claim | Source / URL Checked | Verbatim Quote or NOT FETCHED | Verdict |
|---|---|---|---|
| L14: Who & Year (SMA) — Hooker (1901), Yule (1909), Donchian (1930s-1950s), Granville (1960) | `https://en.wikipedia.org/wiki/Moving_average`, `https://en.wikipedia.org/wiki/Moving_average_crossover`, `https://www.investopedia.com/terms/m/movingaverage.asp` | `"Donchian channel"` (navbox only on `WIKI_MA`; zero occurrences of Hooker, Yule, 1901, 1909, or Granville across all three cited pages) | CONTRADICTED |
| L15: Who & Year (EMA) — P. N. Haurlan at Jet Propulsion Laboratory in 1960s | `https://en.wikipedia.org/wiki/Moving_average` | `"In statistics, a moving average (rolling average or running average or moving mean or rolling mean) is a calculation to analyze data points by creating a series of averages of different subsets of the full data set."` (zero occurrences of Haurlan or Jet Propulsion on `WIKI_MA`) | CONTRADICTED |
| L16: Who & Year (Krown Canon) — former NYSE ARCA market maker, TA 101, codified 2020-2023 | `MyTradingSys/research/ma_layer_2026-11/MA_CONCEPTS.md:7`, `MyTradingSys/research/krown_ta101_2026-10-13/EXTRACT_TEMPLATE.md:18` | `"Analyst: Krown (@ECKrown), playlist TA 101 - Everything You Need To Know."` (zero occurrences of NYSE ARCA or 2020-2023 in `KROWN` or `CONC:7`) | CONTRADICTED |
| L20: 21 & 55 EMA Dynamic Zone — buy between the two lines; distance between the 21 and the green 55 EMA | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:141,143` | `"So a rising 55 EMA is a support zone walking uphill with the trend."` / `"I would even say the distance between the and the green 55 EMA, that is a zone. That is a zone of interest."` | CONTRADICTED |
| L21: Silver Cross (21 vs 55 EMA) (no quote in rule book) | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:228` | `"the cross I actually watch, which is what you see on my shows pretty much every day, is the 21 versus the 55 EMA, which is known as the Silver Cross."` | CONFIRMED |
| L23: Pair Rule & Stacking (no quote in rule book) | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md:110` | `"For any pair, the lower-period average above the higher-period one means that trend is probably up (5 versus 21 short term, 21 versus 55, 200 versus 377 very long term) and vice versa; higher periods carry more weight, lower periods respond faster."` | CONFIRMED |
| L24: Slope Correlates to Power — do not want to trend trade quote | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_vjzy_KxJ_y8.md:425,427` | `"when your slope is flattening or flat in general, like you see right here, this is a time where you don't really want to pay too much attention to moving averages. Why? Cuz you're chopping around."` | CONTRADICTED |
| L25: 5 EMA Leash & Disconnect (no quote in rule book) | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_-NXzJs5JRks.md:181,183` | `"I've measured this 14 plus years, by the way, 5,284 candles, 476 disconnects."` / `"Median lasted one candle, 82% reconnect within two candles."` | CONFIRMED |
| L27: Role: Context and Filter — going long or short at every cross quote | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md:113` | `"going long or short at every cross will not work"` (absent from cited `extract_-NXzJs5JRks.md` lines 110-116) | CONTRADICTED |
| L32: Golden cross / death cross (50 vs 200 SMA) | `https://en.wikipedia.org/wiki/Moving_average_crossover` | `"Golden cross occurs when 50 days simple moving average crosses 200 days simple moving average from below."` | CONFIRMED |
| L33: Golden Cross 3 stages | `https://www.investopedia.com/terms/g/goldencross.asp` | `"The indicator generally has three stages: The first stage requires that a downtrend eventually bottoms out as buyers overpower sellers. In the second stage, the shorter moving average crosses over the larger moving average to trigger a breakout and confirms a downward trend reversal."` | CONFIRMED |
| L34: Weekly Bull Market Support Band (20W SMA / 21W EMA) | `https://www.tradingview.com/script/Bxg5DSp5-Ricco-Bull-Market-Support-Band/` | `NOT FETCHED` (HTTP 404 Not Found) | NOT FETCHED |
| L35: 200-week MA floor / 50-week MA ceiling | `https://www.galaxy.com/insights/research/bitcoin-50-week-moving-average-bear-market-ceiling-200-week-floor-analysis/` | `"Historically, two key bitcoin moving averages have framed every bitcoin bear market – often, the 200-week moving average (MA) has set a floor, and the 50-week moving average has formed the ceiling."` | CONFIRMED |
| L36: Mayer Multiple > 2.4 / < 0.8 | `https://studio.glassnode.com/charts/mayer-multiple` | `NOT FETCHED` (HTTP 403 Forbidden) | NOT FETCHED |
| L37: 200-week WMA cycle floor: 56 of 642 weekly closes below 200 WMA | `https://www.bit.com/knowledge-hub/200-wma` | `"2022–2023 bear market: Price fell significantly below the 200 WMA in June–December 2022 — the most sustained period below this level in Bitcoin's history — before recovering in 2023"` (2022 breach confirmed, but `56` and `642` do not appear on the page) | CONTRADICTED |
| L38: Wei et al. (2024): short-horizon log price-to-MA ratio (PMA1) only rule surviving SPA & OOS | `https://eprints.gla.ac.uk/302711/1/302711.pdf` | `"We observe predictability for a small set of technical and fundamental rules, while only the short-term log moving average-based ratio and Hashrate Index demonstrate genuine in-sample and out-of-sample profitability."` | CONFIRMED |
| L39: Hudson & Urquhart (2021): claimed no OOS predictability for BTC rules | `https://ideas.repec.org/a/spr/annopr/v297y2021i1d10.1007_s10479-019-03357-1.html` | `"We employ almost 15,000 technical trading rules from the main five classes of technical trading rules and find significant predictability and profitability for each class of technical trading rule in each cryptocurrency."` | CONTRADICTED |
| L40: Detzel et al. (2021): ratios of price to MAs forecast daily BTC returns in & out of sample | `https://profiles.wustl.edu/en/publications/learning-and-predictability-via-technical-analysis-evidence-from-/` | `"We document that ratios of prices to their moving averages forecast daily Bitcoin returns in and out of sample. Trading strategies based on these ratios generate an economically significant alpha and Sharpe ratio gains relative to a buy-and-hold position."` | CONFIRMED |
| L41: Grobys, Ahmed, Sapkota (2020): in-sample BTC MA payoffs (1, n) | `https://osuva.uwasa.fi/bitstream/10024/11192/2/Osuva_%20Grobys_Ahmed_Sapkota_2020.pdf` | `NOT FETCHED` (anti-bot challenge: `"Making sure you're not a bot!"`) | NOT FETCHED |
| L42: Islas Anguiano & Garcia-Medina (2025): EMA lags buy-and-hold 25.27% vs 42.31% net of 0.1% fee | `https://arxiv.org/pdf/2511.00665` | `"Buy & Hold ... EMA # Trades 2 ... 8 Cumulative Return with 0.1% fee ... 42.31% ... 25.27%"` | CONFIRMED |
| L43: Timing Bitcoin with SMAs (SSRN 3115846): breakeven friction 1.1% to 4.5% (`UNVERIFIED`) | `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3115846` | `NOT FETCHED` (primary SSRN URL returned HTTP 403 Forbidden; secondary CXO Advisory page at `https://www.cxoadvisory.com/currency-trading/timing-bitcoin-with-smas/` repeats `"Has breakeven Bitcoin-cash switching frictions increasing systematically from 1.1% for a 5-day SMA to 4.5% for a 100-day SMA."`) | NOT FETCHED |
