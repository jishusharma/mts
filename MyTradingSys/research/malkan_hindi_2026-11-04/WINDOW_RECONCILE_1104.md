# Malkan divergence window reconciliation (2026-11-04)

Verdict: regular divergence evidence supports a conservative 3-10 bar default, with mixed evidence around 15-20. No primary source found supports the operator's 12 STRONG / 13-18 OK / >18 WEAK regular window. Hindi clips say under 15 bars is powerful and include 12 among diluting counts; they give no 18-bar rule. Reverse PRD/NRD is separate and internally conflicting (under 15 versus 5-50).

## Source check

Searched the English extracts in `MyTradingSys/research/malkan_extract_2026-10-15/extracts/`, the six Hindi transcripts listed in `MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md:5-10`, and `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt`. Quotes below are from the extracts or raw transcripts. Hindi quote strings are copied from line 8 and verified as exact substrings of their raw transcript files.

| Video ID | Quote | Language | Type | Evidence / note |
|---|---|---|---|---|
| `cQ-y1oULkBw` | "The fewer they are, the more powerful it will be. That means there are three bars, five bars, seven bars." | English | Regular | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:144`; 3/5/7 are called powerful. |
| `cQ-y1oULkBw` | "As the number of bars increases, you see 15, 20, 25, 30, 40 bars. The divergence gets diluted completely and it has not worked." | English | Regular | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:146`. |
| `cQ-y1oULkBw` | "15 to 20 times, this is still fine" | English | Regular | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:200`; conflicts with a hard 15 cutoff. |
| `Wvq1TZh8aF0` | "Three. Because one will go up, one down, then one up again. Right? So three is the minimum requirement." | English | Regular | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:129`. |
| `Wvq1TZh8aF0` | "Meaning three times divergence, five times divergence, seven times divergence, at the most 10 times divergence." | English | Regular | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:131`. |
| `Wvq1TZh8aF0` | "I will say that less than 10 bars is the most powerful divergence. It should be between three and 10." | English | Regular | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:133`; explicit 3-10. |
| `GbXnw_tNMtw` | "divergence was within seven eight bars" / "this is like more than fifteen twenty" / "bars so I that dilutes the reverse" | English | Reverse PRD/NRD | `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt:354-357`. |
| `GbXnw_tNMtw` | "number of bars which are less than 15" | English | Reverse PRD/NRD | `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt:382`. |
| `GbXnw_tNMtw` | "should be between five to fifty" | English | Reverse PRD/NRD | `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt:460-461`; conflicts with under-15. |
| `TO3pLafk7Us` | "जैसे जैसे नंबर ऑफ बर्स बढ़ते जाते 12 15 20 25 30 40 वो बिल्कुल डाइल्यूट हो जाता है डायवर्जेंस" | Hindi | Regular | `raw_transcripts_canonical/TO3pLafk7Us_raw.txt:8`; lists 12, 15, 20, 25, 30, 40 among diluting spans. |
| `TrZQ4Xat_sQ` | "दो पॉइंट के बीच में वो बहुत जरूरी है कि 15 से कम हो अगर वो ज्यादा होते जाते हैं जैसे 20 25 50 तो फिर वो डायवर्जेंस डाइल्यूट हो जाता है" | Hindi | Regular | `raw_transcripts_canonical/TrZQ4Xat_sQ_raw.txt:8`; says under 15 is important and longer 20/25/50 dilutes. |
| `TrZQ4Xat_sQ` | "दो पॉइंट के बीच में वो बहुत जरूरी है कि 15 से कम हो अगर वो ज्यादा होते जाते हैं जैसे 20 25 50 तो फिर वो डायवर्जेंस डाइल्यूट हो जाता है" | Hindi | Regular | `raw_transcripts_canonical/TrZQ4Xat_sQ_raw.txt:8`; within 15 candles is powerful. |
| `kVIvcn7T44o` | "नंबर ऑफ़ बार्स डायवर्जेंस के जितने कम होंगे उतना डायवर्जेंस ज्यादा पावरफुल होगा" | Hindi | Regular | `raw_transcripts_canonical/kVIvcn7T44o_raw.txt:8`; shorter is stronger, minimum three, >10 dilutes. |

## Threshold verdicts

| Threshold | Verdict | Source-grounded reason |
|---|---|---|
| 10 | SOURCED - `Wvq1TZh8aF0` | "between three and 10" and "at the most 10" (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:131,133`). |
| 12 | SOURCED - `TO3pLafk7Us` | Hindi dilution list explicitly includes 12 (`raw_transcripts_canonical/TO3pLafk7Us_raw.txt:8`). It does not support 12 as STRONG. |
| 15 | SOURCED - `TrZQ4Xat_sQ`; counterexample `cQ-y1oULkBw` | Hindi says within 15 is powerful / less than 15 is important. English also says 15-20 is "still fine," so the edge varies by context. |
| 18 | NOT_IN_DATA | No source found giving 18 as a bar threshold. The six Hindi transcript occurrences described in `MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md:22` are publication dates, not a rule. |

## Proposed windows

Regular uses sourced minimum 3 and sourced maximum 10 as a conservative default. That does not imply every 11+ divergence is invalid, given the English 15-20 acceptable example. Reverse uses sourced minimum 5 and OURS maximum 14 to encode the under-15 statement alongside the conflicting 5-50 statement; the transcript does not resolve the conflict.

```json
{
  "min_bars": {"value": 3, "label": "SOURCED"},
  "max_bars": {"value": 10, "label": "SOURCED"},
  "reverse": {
    "min_bars": {"value": 5, "label": "SOURCED"},
    "max_bars": {"value": 14, "label": "OURS"}
  }
}
```

## Effect on current decision and params

`MyTradingSys/system/OPERATOR_DECISIONS.md:1685-1686` calls 12 primary / 18 secondary / >18 WEAK "all three SOURCED, Malkan." The sources above do not support that regular window; those thresholds should be relabelled OURS unless a distinct primary source is found. Current regular params at `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4-8` use 3-10, matching the explicit English range. Reverse params at lines 12-17 use 5-14; only the minimum is sourced, while 14 is OURS as the exclusive-under-15 boundary. The existing reverse label acknowledges source conflict.

## Claude spot-check (2026-11-05)

Each cited file and line was opened and the quote compared with the table. Labels: SOURCED = a quote exists in the source; OURS = our own choice, not the trader's.

| Threshold | Check | Evidence line |
|---|---|---|
| 10 | CONFIRMED (SOURCED) | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:131` "at the most 10 times divergence"; `:133` "It should be between three and 10." |
| 12 | CONFIRMED (12 is a diluting count, not STRONG) | `raw_transcripts_canonical/TO3pLafk7Us_raw.txt:8` contains "12 15 20 25 30 40 वो बिल्कुल डाइल्यूट हो जाता है डायवर्जेंस" (exact substring). |
| 15 | CONFIRMED (Hindi under 15; English 15-20 "still fine") | `raw_transcripts_canonical/TrZQ4Xat_sQ_raw.txt:8` contains "15 से कम हो" and "20 25 50"; `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:200` "15 to 20 times, this is still fine". |
| 18 | CONFIRMED NOT_IN_DATA | A script searched 160 files (English extracts plus every canonical raw transcript) for 18 / eighteen / अठारह. All 21 hits are other traders' money or trade counts. None is in the Malkan extracts or the Hindi divergence transcripts. None is a bar count. |

Notes on the table above (none change a verdict):
- The `TrZQ4Xat_sQ` rows repeat one quote. The claim that 15 candles or fewer is powerful rests on a different string that exists in the transcript: "अगर 15 कैंडल 15 बार के अंदर आता है तो लडी पावरफुल है" (`raw_transcripts_canonical/TrZQ4Xat_sQ_raw.txt:8`, also `MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md:21`).
- The 18 row cites `MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md:22` for "publication dates". That line says no such thing. The conclusion holds because the 18 search found no bar-count use.
- The statement that no primary source exists holds for the 12 / 18 / >18 window, which lives in `MyTradingSys/system/OPERATOR_DECISIONS.md:1686` ("all three SOURCED, Malkan"). It does not hold for `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json`: that file has min_bars 3 / max_bars 10, and the 3-10 range is quoted at `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:133`. Only the reverse max 14 is OURS.
- Proposed windows stay as labelled above: regular 3 / 10 SOURCED; reverse min 5 SOURCED, max 14 OURS. No param or code file was changed. Changing the 12 / 18 window is a separate operator decision.