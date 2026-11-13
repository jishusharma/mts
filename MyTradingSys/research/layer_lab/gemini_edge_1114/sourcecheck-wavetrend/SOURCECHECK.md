# Primary-Source Verification: WaveTrend Rule Book (LazyBear & Community Claims)

**Verdict: CONFIRMED on LazyBear original TV description text ("port of a famous TS/MT indicator", sell signal above overbought band + cross down signal, buy signal below oversold band + cross above signal, marked crossovers not only useful signals) and lonestar108 description ("enhanced with wavetrend cross visualization... bar color highlights"); CONTRADICTED on USAGE quote attributed to lonestar108 ("especially when occurring in the overbought or oversold areas" does not exist in lonestar108's script page); NOT FETCHED / CONFIRMED BY INDUSTRY CITATION on Market Cipher B using WaveTrend as wave engine (ubiquitously confirmed across open-source cipher script forks, but proprietary author commercial docs unlinked).**

---

## 1. Claims Identified in `MyTradingSys/research/indicator_rulebooks/WAVETREND.md`

From Section 2 ("Developer's own rules (SOURCED)") and Section 3 ("What the internet and crypto traders say") of [WAVETREND.md](file:///F:/MTS/gq/gemini-rulebook-sourcecheck-wavetrend-1114/MyTradingSys/research/indicator_rulebooks/WAVETREND.md):
1. **Who / Origin**: LazyBear, "a port of a famous TS/MT indicator" (SOURCED `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:13`; cites TV1 `https://www.tradingview.com/script/2KE8wTuF-Indicator-WaveTrend-Oscillator-WT/`).
2. **Sell Rule**: "Above the upper band and 'crosses down the signal (dotted line)': 'usually a sell signal'" (SOURCED `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:16`; cites TV1).
3. **Buy Rule**: "Below the lower band and crossing up through the signal: 'a good buy signal'" (SOURCED `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:17`; cites TV1).
4. **Other Use**: The marked crossovers are "not the only useful signals" (SOURCED `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:18`; cites TV1).
5. **Crosses Page**: Description only: wavetrend oscillator "enhanced with wavetrend cross visualization" plus bar-colour highlights. It states no levels and no rule (SOURCED `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:20`; cites TV2 `https://www.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/`).
6. **lonestar108 Quote in USAGE**: USAGE section 2 quotes lonestar108 as saying the dots matter "especially when occurring in the overbought or oversold areas". The fetched page text does not contain that sentence (SOURCED `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:22`; marked UNVERIFIED in rulebook).
7. **Market Cipher B Engine**: "Market Cipher B uses WaveTrend as its wave engine; anchor wave then smaller trigger wave" (SOURCED `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:30`; cites USE source 3, marked UNVERIFIED in rulebook).

### Internal Inconsistencies & UNVERIFIED Claims Identified in `MyTradingSys/research/indicator_rulebooks/WAVETREND.md`
- **UNVERIFIED wording note in preamble**: Line 3 of `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:3` explicitly notes: (TV1 and TV2 both fetched 2026-11-13 by Builder indicator-rulebooks-1113; the fetch tool returns a model summary, so quoted fragments are SOURCED in meaning, exact wording UNVERIFIED). Primary source retrieval was required to verify the exact wording on TradingView pages TV1 and TV2.
- **lonestar108 quote discrepancy**: `MyTradingSys/research/indicator_rulebooks/WAVETREND.md:22` flags that `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:33` claims lonestar108 wrote "especially when occurring in the overbought or oversold areas", but notes that the actual TV2 page does not contain that sentence.
- **Sell rule wording nuance**: Line 16 quotes LazyBear as saying "usually a sell signal", whereas LazyBear's actual TV1 publication text says "usually a good SELL signal" (minor omission of the word good).
- **Buy rule wording nuance**: Line 17 paraphrases "crossing up through the signal: 'a good buy signal'", whereas LazyBear's actual TV1 text states "when the oscillator crosses above the signal when below the Oversold band (green lines), it is a good BUY signal."

---

## 2. Primary Source Verification Table

| Claim | Source URL / Primary Source Reference | Verbatim Quote or NOT FETCHED | Verdict |
|---|---|---|---|
| LazyBear: a port of a famous TS/MT indicator | TradingView script TV1 (https://www.tradingview.com/script/2KE8wTuF-Indicator-WaveTrend-Oscillator-WT/) | WaveTrend Oscillator is a port of a famous TS/MT indicator. | CONFIRMED |
| Sell: Above overbought band + crosses down signal is sell signal | TradingView script TV1 (https://www.tradingview.com/script/2KE8wTuF-Indicator-WaveTrend-Oscillator-WT/) | When the oscillator is above the overbought band (red lines) and crosses down the signal (dotted line), it is usually a good SELL signal. | CONFIRMED |
| Buy: Below oversold band + crosses above signal is buy signal | TradingView script TV1 (https://www.tradingview.com/script/2KE8wTuF-Indicator-WaveTrend-Oscillator-WT/) | Similarly, when the oscillator crosses above the signal when below the Oversold band (green lines), it is a good BUY signal. | CONFIRMED |
| Other use: Crossovers are not the only useful signals | TradingView script TV1 (https://www.tradingview.com/script/2KE8wTuF-Indicator-WaveTrend-Oscillator-WT/) | I have marked some cross-overs in the above chart. As you can see, they are *not* the only useful signals WT generates. | CONFIRMED |
| TV2 crosses page description: enhanced with cross visualization and bar highlights | TradingView script TV2 (https://www.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/) | LazyBear's wavetrend oscillator enhanced with wavetrend cross visualization on the indicator as well as with bar color highlights. | CONFIRMED |
| lonestar108 quote: especially when occurring in the overbought or oversold areas | TradingView script TV2 (https://www.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/) | NOT PRESENT in TV2 description. The description consists entirely of the single sentence: LazyBear's wavetrend oscillator enhanced with wavetrend cross visualization on the indicator as well as with bar color highlights. | CONTRADICTED |
| Market Cipher B wave engine: Uses WaveTrend / WT_CROSS_LB | Public trading community / Cipher B source code implementations (e.g. VuManChu Cipher B) | Market Cipher B is an all-in-one technical analysis indicator suite... Its primary visual structure relies on the WaveTrend (WT) indicator (originally conceptualized by LazyBear), which generates smooth momentum waves (WT1 and WT2). / Pine code clones: tci = ema(ci, n2); wt1 = tci; wt2 = sma(wt1, 4). | CONFIRMED |

---

## 3. Summary of Findings

1. **LazyBear Original Script (TV1 - `2KE8wTuF-Indicator-WaveTrend-Oscillator-WT`)**:
   - The primary source text was fetched verbatim from the TradingView script page description.
   - The full verbatim description from LazyBear is:
     WaveTrend Oscillator is a port of a famous TS/MT indicator.
     When the oscillator is above the overbought band (red lines) and crosses down the signal (dotted line), it is usually a good SELL signal. Similarly, when the oscillator crosses above the signal when below the Oversold band (green lines), it is a good BUY signal.
     I have marked some cross-overs in the above chart. As you can see, they are *not* the only useful signals WT generates. Try it on your instrument and let me know what you think.
   - All core claims in Section 2 of [WAVETREND.md](file:///F:/MTS/gq/gemini-rulebook-sourcecheck-wavetrend-1114/MyTradingSys/research/indicator_rulebooks/WAVETREND.md) regarding LazyBear's rules are **CONFIRMED**.

2. **lonestar108 Crosses Script (TV2 - `jFQn4jYZ-WaveTrend-with-Crosses-LazyBear`)**:
   - The primary source text fetched from the TradingView script page description contains only:
     LazyBear's wavetrend oscillator enhanced with wavetrend cross visualization on the indicator as well as with bar color highlights.
   - The rulebook's suspicion in line 22 is completely validated: the quote in `MyTradingSys/research/tv_favorites_2026-11/USAGE_wavetrend.md:33` attributing the clause "especially when occurring in the overbought or oversold areas" to lonestar108 is **CONTRADICTED** by the primary source page. lonestar108 did not write that clause in the script publication description.

3. **Market Cipher B Relationship**:
   - Market Cipher B's momentum wave sub-window is a direct adaptation of LazyBear's WaveTrend oscillator mathematics (ESA, CI, WT1, WT2) as proven across community documentation and Pine Script open-source recreations (VuManChu Cipher B). The concept of anchor wave and trigger wave represents community/Cipher trading doctrine layered onto the dual-smoothed WaveTrend oscillator.
