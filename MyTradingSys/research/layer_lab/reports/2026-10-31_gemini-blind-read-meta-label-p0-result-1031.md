# Blind Read Audit: meta_label_tom_fabio_2026-10-31/output.md

**Date**: 2026-10-31  
**Card**: `gemini-blind-read-meta-label-p0-result-1031`  
**Auditor**: Gemini Flash Worker (Antigravity)  
**Scope**: Blind read and factual lookup of every number and cited reference in `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/output.md` against `numbers.json` and `PRE_REG.md` (and `ROADMAP.md` for amendment references).  
**Result Verdict Policy**: Facts only, no verdicts; one table row per cited number with lookup file:line; FOUND / DIFF / NOT_IN_DATA.

## Summary of Findings

- **Total Cited Numbers / Items Audited**: 193
- **FOUND**: 193 (100.0%)
- **DIFF**: 0 (0.0%)
- **NOT_IN_DATA**: 0 (0.0%)

## Detailed Audit Table

| Output Line | Section | Item Description | Cited Number / Text | Lookup File:Line | Actual Content Found | Verdict | Notes |
|---|---|---|---|---|---|---|---|
| L1 | Title / Header | Amendments range | `1-8` | `MyTradingSys/research/meta_label_roadmap_2026-10-31/ROADMAP.md:153-160` | `1. Stamp features at fill bar... 8. Power line per setup` | **FOUND** | Located in ROADMAP.md; not present in numbers.json or PRE_REG.md |
| L1 | Title / Header | Roadmap section | `2.1` | `MyTradingSys/research/meta_label_roadmap_2026-10-31/ROADMAP.md:152` | `### 2.1 Amendments to the running test` | **FOUND** | Located in ROADMAP.md; not present in numbers.json or PRE_REG.md |
| L3 | Tom VP Header | Accept N setting | `6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/PRE_REG.md:11` | `accept_n 6` | **FOUND** | Defined in PRE_REG.md:11; not keyed in numbers.json |
| L3 | Tom VP Header | Best third mean net R | `-0.277` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:15` | `"mean": -0.27717333411825906` | **FOUND** | Rounds to -0.277 R |
| L3 | Tom VP Header | Top third 95% CI lower | `-0.344` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:33` | `-0.3437770189983512` | **FOUND** | Rounds to -0.344 |
| L3 | Tom VP Header | Top third 95% CI upper | `-0.211` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:34` | `-0.21097820002547227` | **FOUND** | Rounds to -0.211 |
| L3 | Tom VP Header | Random third mean net R | `-0.265` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:55` | `"random_third_mean": -0.26532868662786435` | **FOUND** | Rounds to -0.265 R (also line 9 mean_model_sample) |
| L5 | Tom VP Placebo | Holm-adjusted placebo p | `1.000` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:485` | `"holm_p": 1.0` | **FOUND** | Formatted as 1.000 |
| L5 | Tom VP Placebo | Family m | `2` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:487` | `"family_m": 2` | **FOUND** | Exact match m = 2 |
| L5 | Tom VP Placebo | BH q-value | `0.761` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:486` | `"bh_q": 0.760797342192691` | **FOUND** | Rounds to 0.761 |
| L9 | Tom VP Table (Row 01) | Layer reading condition | `BBWP (1h): normal, 30 to 85` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:58` | `"BBWP (1h): normal, 30 to 85",` | **FOUND** | Feature reading definition |
| L9 | Tom VP Table (Row 01) | Trades count | `963` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:59` | `"963",` | **FOUND** | Exact match: "963" |
| L9 | Tom VP Table (Row 01) | Win percentage | `38.9` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:60` | `"38.9",` | **FOUND** | Exact match: "38.9" |
| L9 | Tom VP Table (Row 01) | Average R after fees | `-0.220` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:61` | `"-0.220"` | **FOUND** | Exact match: "-0.220" |
| L10 | Tom VP Table (Row 02) | Layer reading condition | `BBWP (1h): compression, 30 or below` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:64` | `"BBWP (1h): compression, 30 or below",` | **FOUND** | Feature reading definition |
| L10 | Tom VP Table (Row 02) | Trades count | `630` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:65` | `"630",` | **FOUND** | Exact match: "630" |
| L10 | Tom VP Table (Row 02) | Win percentage | `34.6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:66` | `"34.6",` | **FOUND** | Exact match: "34.6" |
| L10 | Tom VP Table (Row 02) | Average R after fees | `-0.339` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:67` | `"-0.339"` | **FOUND** | Exact match: "-0.339" |
| L11 | Tom VP Table (Row 03) | Layer reading condition | `BBWP (1h): expansion, 85 or above` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:70` | `"BBWP (1h): expansion, 85 or above",` | **FOUND** | Feature reading definition |
| L11 | Tom VP Table (Row 03) | Trades count | `219` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:71` | `"219",` | **FOUND** | Exact match: "219" |
| L11 | Tom VP Table (Row 03) | Win percentage | `40.2` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:72` | `"40.2",` | **FOUND** | Exact match: "40.2" |
| L11 | Tom VP Table (Row 03) | Average R after fees | `-0.190` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:73` | `"-0.190"` | **FOUND** | Exact match: "-0.190" |
| L12 | Tom VP Table (Row 04) | Layer reading condition | `D1 trend: up (close above 50-day average)` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:76` | `"D1 trend: up (close above 50-day average)",` | **FOUND** | Feature reading definition |
| L12 | Tom VP Table (Row 04) | Trades count | `913` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:77` | `"913",` | **FOUND** | Exact match: "913" |
| L12 | Tom VP Table (Row 04) | Win percentage | `36.3` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:78` | `"36.3",` | **FOUND** | Exact match: "36.3" |
| L12 | Tom VP Table (Row 04) | Average R after fees | `-0.274` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:79` | `"-0.274"` | **FOUND** | Exact match: "-0.274" |
| L13 | Tom VP Table (Row 05) | Layer reading condition | `D1 trend: down (close below 50-day average)` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:82` | `"D1 trend: down (close below 50-day average)",` | **FOUND** | Feature reading definition |
| L13 | Tom VP Table (Row 05) | Trades count | `899` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:83` | `"899",` | **FOUND** | Exact match: "899" |
| L13 | Tom VP Table (Row 05) | Win percentage | `38.9` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:84` | `"38.9",` | **FOUND** | Exact match: "38.9" |
| L13 | Tom VP Table (Row 05) | Average R after fees | `-0.241` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:85` | `"-0.241"` | **FOUND** | Exact match: "-0.241" |
| L14 | Tom VP Table (Row 06) | Layer reading condition | `Cowen band (daily close): not available` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:88` | `"Cowen band (daily close): not available",` | **FOUND** | Feature reading definition |
| L14 | Tom VP Table (Row 06) | Trades count | `111` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:89` | `"111",` | **FOUND** | Exact match: "111" |
| L14 | Tom VP Table (Row 06) | Win percentage | `41.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:90` | `"41.4",` | **FOUND** | Exact match: "41.4" |
| L14 | Tom VP Table (Row 06) | Average R after fees | `-0.136` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:91` | `"-0.136"` | **FOUND** | Exact match: "-0.136" |
| L15 | Tom VP Table (Row 07) | Layer reading condition | `Cowen band (daily close): below the band` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:94` | `"Cowen band (daily close): below the band",` | **FOUND** | Feature reading definition |
| L15 | Tom VP Table (Row 07) | Trades count | `637` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:95` | `"637",` | **FOUND** | Exact match: "637" |
| L15 | Tom VP Table (Row 07) | Win percentage | `39.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:96` | `"39.4",` | **FOUND** | Exact match: "39.4" |
| L15 | Tom VP Table (Row 07) | Average R after fees | `-0.255` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:97` | `"-0.255"` | **FOUND** | Exact match: "-0.255" |
| L16 | Tom VP Table (Row 08) | Layer reading condition | `Cowen band (daily close): inside the band` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:100` | `"Cowen band (daily close): inside the band",` | **FOUND** | Feature reading definition |
| L16 | Tom VP Table (Row 08) | Trades count | `39` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:101` | `"39",` | **FOUND** | Exact match: "39" |
| L16 | Tom VP Table (Row 08) | Win percentage | `30.8` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:102` | `"30.8",` | **FOUND** | Exact match: "30.8" |
| L16 | Tom VP Table (Row 08) | Average R after fees | `-0.332` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:103` | `"-0.332"` | **FOUND** | Exact match: "-0.332" |
| L17 | Tom VP Table (Row 09) | Layer reading condition | `Cowen band (daily close): above the band` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:106` | `"Cowen band (daily close): above the band",` | **FOUND** | Feature reading definition |
| L17 | Tom VP Table (Row 09) | Trades count | `1025` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:107` | `"1025",` | **FOUND** | Exact match: "1025" |
| L17 | Tom VP Table (Row 09) | Win percentage | `36.3` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:108` | `"36.3",` | **FOUND** | Exact match: "36.3" |
| L17 | Tom VP Table (Row 09) | Average R after fees | `-0.269` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:109` | `"-0.269"` | **FOUND** | Exact match: "-0.269" |
| L18 | Tom VP Table (Row 10) | Layer reading condition | `Funding sign: positive` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:112` | `"Funding sign: positive",` | **FOUND** | Feature reading definition |
| L18 | Tom VP Table (Row 10) | Trades count | `1615` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:113` | `"1615",` | **FOUND** | Exact match: "1615" |
| L18 | Tom VP Table (Row 10) | Win percentage | `37.1` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:114` | `"37.1",` | **FOUND** | Exact match: "37.1" |
| L18 | Tom VP Table (Row 10) | Average R after fees | `-0.270` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:115` | `"-0.270"` | **FOUND** | Exact match: "-0.270" |
| L19 | Tom VP Table (Row 11) | Layer reading condition | `Funding sign: negative` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:118` | `"Funding sign: negative",` | **FOUND** | Feature reading definition |
| L19 | Tom VP Table (Row 11) | Trades count | `197` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:119` | `"197",` | **FOUND** | Exact match: "197" |
| L19 | Tom VP Table (Row 11) | Win percentage | `41.6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:120` | `"41.6",` | **FOUND** | Exact match: "41.6" |
| L19 | Tom VP Table (Row 11) | Average R after fees | `-0.152` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:121` | `"-0.152"` | **FOUND** | Exact match: "-0.152" |
| L20 | Tom VP Table (Row 12) | Layer reading condition | `Session (UTC): Europe, 07-13` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:124` | `"Session (UTC): Europe, 07-13",` | **FOUND** | Feature reading definition |
| L20 | Tom VP Table (Row 12) | Trades count | `406` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:125` | `"406",` | **FOUND** | Exact match: "406" |
| L20 | Tom VP Table (Row 12) | Win percentage | `36.7` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:126` | `"36.7",` | **FOUND** | Exact match: "36.7" |
| L20 | Tom VP Table (Row 12) | Average R after fees | `-0.310` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:127` | `"-0.310"` | **FOUND** | Exact match: "-0.310" |
| L21 | Tom VP Table (Row 13) | Layer reading condition | `Session (UTC): US, 13-21` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:130` | `"Session (UTC): US, 13-21",` | **FOUND** | Feature reading definition |
| L21 | Tom VP Table (Row 13) | Trades count | `641` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:131` | `"641",` | **FOUND** | Exact match: "641" |
| L21 | Tom VP Table (Row 13) | Win percentage | `38.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:132` | `"38.4",` | **FOUND** | Exact match: "38.4" |
| L21 | Tom VP Table (Row 13) | Average R after fees | `-0.294` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:133` | `"-0.294"` | **FOUND** | Exact match: "-0.294" |
| L22 | Tom VP Table (Row 14) | Layer reading condition | `Session (UTC): Asia, 21-07` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:136` | `"Session (UTC): Asia, 21-07",` | **FOUND** | Feature reading definition |
| L22 | Tom VP Table (Row 14) | Trades count | `765` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:137` | `"765",` | **FOUND** | Exact match: "765" |
| L22 | Tom VP Table (Row 14) | Win percentage | `37.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:138` | `"37.4",` | **FOUND** | Exact match: "37.4" |
| L22 | Tom VP Table (Row 14) | Average R after fees | `-0.199` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:139` | `"-0.199"` | **FOUND** | Exact match: "-0.199" |
| L23 | Tom VP Table (Row 15) | Layer reading condition | `RSI 14 (1h): middle, 40 to 60` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:142` | `"RSI 14 (1h): middle, 40 to 60",` | **FOUND** | Feature reading definition |
| L23 | Tom VP Table (Row 15) | Trades count | `1524` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:143` | `"1524",` | **FOUND** | Exact match: "1524" |
| L23 | Tom VP Table (Row 15) | Win percentage | `38.1` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:144` | `"38.1",` | **FOUND** | Exact match: "38.1" |
| L23 | Tom VP Table (Row 15) | Average R after fees | `-0.248` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:145` | `"-0.248"` | **FOUND** | Exact match: "-0.248" |
| L24 | Tom VP Table (Row 16) | Layer reading condition | `RSI 14 (1h): low, 40 or below` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:148` | `"RSI 14 (1h): low, 40 or below",` | **FOUND** | Feature reading definition |
| L24 | Tom VP Table (Row 16) | Trades count | `163` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:149` | `"163",` | **FOUND** | Exact match: "163" |
| L24 | Tom VP Table (Row 16) | Win percentage | `33.7` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:150` | `"33.7",` | **FOUND** | Exact match: "33.7" |
| L24 | Tom VP Table (Row 16) | Average R after fees | `-0.279` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:151` | `"-0.279"` | **FOUND** | Exact match: "-0.279" |
| L25 | Tom VP Table (Row 17) | Layer reading condition | `RSI 14 (1h): high, 60 or above` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:154` | `"RSI 14 (1h): high, 60 or above",` | **FOUND** | Feature reading definition |
| L25 | Tom VP Table (Row 17) | Trades count | `125` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:155` | `"125",` | **FOUND** | Exact match: "125" |
| L25 | Tom VP Table (Row 17) | Win percentage | `36.0` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:156` | `"36.0",` | **FOUND** | Exact match: "36.0" |
| L25 | Tom VP Table (Row 17) | Average R after fees | `-0.343` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:157` | `"-0.343"` | **FOUND** | Exact match: "-0.343" |
| L26 | Tom VP Table (Row 18) | Layer reading condition | `WaveTrend (1h): middle` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:160` | `"WaveTrend (1h): middle",` | **FOUND** | Feature reading definition |
| L26 | Tom VP Table (Row 18) | Trades count | `1754` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:161` | `"1754",` | **FOUND** | Exact match: "1754" |
| L26 | Tom VP Table (Row 18) | Win percentage | `38.3` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:162` | `"38.3",` | **FOUND** | Exact match: "38.3" |
| L26 | Tom VP Table (Row 18) | Average R after fees | `-0.251` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:163` | `"-0.251"` | **FOUND** | Exact match: "-0.251" |
| L27 | Tom VP Table (Row 19) | Layer reading condition | `WaveTrend (1h): overbought` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:166` | `"WaveTrend (1h): overbought",` | **FOUND** | Feature reading definition |
| L27 | Tom VP Table (Row 19) | Trades count | `22` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:167` | `"22",` | **FOUND** | Exact match: "22" |
| L27 | Tom VP Table (Row 19) | Win percentage | `13.6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:168` | `"13.6",` | **FOUND** | Exact match: "13.6" |
| L27 | Tom VP Table (Row 19) | Average R after fees | `-0.657` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:169` | `"-0.657"` | **FOUND** | Exact match: "-0.657" |
| L28 | Tom VP Table (Row 20) | Layer reading condition | `WaveTrend (1h): oversold` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:172` | `"WaveTrend (1h): oversold",` | **FOUND** | Feature reading definition |
| L28 | Tom VP Table (Row 20) | Trades count | `36` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:173` | `"36",` | **FOUND** | Exact match: "36" |
| L28 | Tom VP Table (Row 20) | Win percentage | `19.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:174` | `"19.4",` | **FOUND** | Exact match: "19.4" |
| L28 | Tom VP Table (Row 20) | Average R after fees | `-0.331` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:175` | `"-0.331"` | **FOUND** | Exact match: "-0.331" |
| L29 | Tom VP Table (Row 21) | Layer reading condition | `Relative volume (1h): low third` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:178` | `"Relative volume (1h): low third",` | **FOUND** | Feature reading definition |
| L29 | Tom VP Table (Row 21) | Trades count | `604` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:179` | `"604",` | **FOUND** | Exact match: "604" |
| L29 | Tom VP Table (Row 21) | Win percentage | `33.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:180` | `"33.4",` | **FOUND** | Exact match: "33.4" |
| L29 | Tom VP Table (Row 21) | Average R after fees | `-0.244` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:181` | `"-0.244"` | **FOUND** | Exact match: "-0.244" |
| L30 | Tom VP Table (Row 22) | Layer reading condition | `Relative volume (1h): high third` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:184` | `"Relative volume (1h): high third",` | **FOUND** | Feature reading definition |
| L30 | Tom VP Table (Row 22) | Trades count | `604` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:185` | `"604",` | **FOUND** | Exact match: "604" |
| L30 | Tom VP Table (Row 22) | Win percentage | `37.9` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:186` | `"37.9",` | **FOUND** | Exact match: "37.9" |
| L30 | Tom VP Table (Row 22) | Average R after fees | `-0.296` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:187` | `"-0.296"` | **FOUND** | Exact match: "-0.296" |
| L31 | Tom VP Table (Row 23) | Layer reading condition | `Relative volume (1h): middle third` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:190` | `"Relative volume (1h): middle third",` | **FOUND** | Feature reading definition |
| L31 | Tom VP Table (Row 23) | Trades count | `604` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:191` | `"604",` | **FOUND** | Exact match: "604" |
| L31 | Tom VP Table (Row 23) | Win percentage | `41.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:192` | `"41.4",` | **FOUND** | Exact match: "41.4" |
| L31 | Tom VP Table (Row 23) | Average R after fees | `-0.233` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:193` | `"-0.233"` | **FOUND** | Exact match: "-0.233" |
| L33 | Fabio C Header | Best third mean net R | `-0.003` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:502` | `"mean": -0.0027238851403699714` | **FOUND** | Rounds to -0.003 R |
| L33 | Fabio C Header | Top third 95% CI lower | `-0.364` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:520` | `-0.3642359712021382` | **FOUND** | Rounds to -0.364 |
| L33 | Fabio C Header | Top third 95% CI upper | `+0.404` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:521` | `0.40423677540109976` | **FOUND** | Rounds to +0.404 |
| L33 | Fabio C Header | Random third mean net R | `+0.029` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:542` | `"random_third_mean": 0.02870938193788221` | **FOUND** | Rounds to +0.029 R (also line 496 mean_model_sample) |
| L35 | Fabio C Placebo | Holm-adjusted placebo p | `1.000` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:940` | `"holm_p": 1.0` | **FOUND** | Formatted as 1.000 |
| L35 | Fabio C Placebo | Family m | `2` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:942` | `"family_m": 2` | **FOUND** | Exact match m = 2 |
| L35 | Fabio C Placebo | BH q-value | `0.761` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:941` | `"bh_q": 0.760797342192691` | **FOUND** | Rounds to 0.761 |
| L39 | Fabio C Table (Row 01) | Layer reading condition | `BBWP (1h): normal, 30 to 85` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:545` | `"BBWP (1h): normal, 30 to 85",` | **FOUND** | Feature reading definition |
| L39 | Fabio C Table (Row 01) | Trades count | `320` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:546` | `"320",` | **FOUND** | Exact match: "320" |
| L39 | Fabio C Table (Row 01) | Win percentage | `32.8` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:547` | `"32.8",` | **FOUND** | Exact match: "32.8" |
| L39 | Fabio C Table (Row 01) | Average R after fees | `+0.034` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:548` | `"+0.034"` | **FOUND** | Exact match: "+0.034" |
| L40 | Fabio C Table (Row 02) | Layer reading condition | `BBWP (1h): compression, 30 or below` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:551` | `"BBWP (1h): compression, 30 or below",` | **FOUND** | Feature reading definition |
| L40 | Fabio C Table (Row 02) | Trades count | `117` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:552` | `"117",` | **FOUND** | Exact match: "117" |
| L40 | Fabio C Table (Row 02) | Win percentage | `29.9` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:553` | `"29.9",` | **FOUND** | Exact match: "29.9" |
| L40 | Fabio C Table (Row 02) | Average R after fees | `-0.094` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:554` | `"-0.094"` | **FOUND** | Exact match: "-0.094" |
| L41 | Fabio C Table (Row 03) | Layer reading condition | `BBWP (1h): expansion, 85 or above` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:557` | `"BBWP (1h): expansion, 85 or above",` | **FOUND** | Feature reading definition |
| L41 | Fabio C Table (Row 03) | Trades count | `81` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:558` | `"81",` | **FOUND** | Exact match: "81" |
| L41 | Fabio C Table (Row 03) | Win percentage | `29.6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:559` | `"29.6",` | **FOUND** | Exact match: "29.6" |
| L41 | Fabio C Table (Row 03) | Average R after fees | `+0.396` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:560` | `"+0.396"` | **FOUND** | Exact match: "+0.396" |
| L42 | Fabio C Table (Row 04) | Layer reading condition | `D1 trend: up (close above 50-day average)` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:563` | `"D1 trend: up (close above 50-day average)",` | **FOUND** | Feature reading definition |
| L42 | Fabio C Table (Row 04) | Trades count | `277` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:564` | `"277",` | **FOUND** | Exact match: "277" |
| L42 | Fabio C Table (Row 04) | Win percentage | `29.2` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:565` | `"29.2",` | **FOUND** | Exact match: "29.2" |
| L42 | Fabio C Table (Row 04) | Average R after fees | `-0.055` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:566` | `"-0.055"` | **FOUND** | Exact match: "-0.055" |
| L43 | Fabio C Table (Row 05) | Layer reading condition | `D1 trend: down (close below 50-day average)` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:569` | `"D1 trend: down (close below 50-day average)",` | **FOUND** | Feature reading definition |
| L43 | Fabio C Table (Row 05) | Trades count | `241` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:570` | `"241",` | **FOUND** | Exact match: "241" |
| L43 | Fabio C Table (Row 05) | Win percentage | `34.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:571` | `"34.4",` | **FOUND** | Exact match: "34.4" |
| L43 | Fabio C Table (Row 05) | Average R after fees | `+0.196` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:572` | `"+0.196"` | **FOUND** | Exact match: "+0.196" |
| L44 | Fabio C Table (Row 06) | Layer reading condition | `Cowen band (daily close): not available` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:575` | `"Cowen band (daily close): not available",` | **FOUND** | Feature reading definition |
| L44 | Fabio C Table (Row 06) | Trades count | `27` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:576` | `"27",` | **FOUND** | Exact match: "27" |
| L44 | Fabio C Table (Row 06) | Win percentage | `48.1` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:577` | `"48.1",` | **FOUND** | Exact match: "48.1" |
| L44 | Fabio C Table (Row 06) | Average R after fees | `+0.661` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:578` | `"+0.661"` | **FOUND** | Exact match: "+0.661" |
| L45 | Fabio C Table (Row 07) | Layer reading condition | `Cowen band (daily close): below the band` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:581` | `"Cowen band (daily close): below the band",` | **FOUND** | Feature reading definition |
| L45 | Fabio C Table (Row 07) | Trades count | `172` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:582` | `"172",` | **FOUND** | Exact match: "172" |
| L45 | Fabio C Table (Row 07) | Win percentage | `30.2` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:583` | `"30.2",` | **FOUND** | Exact match: "30.2" |
| L45 | Fabio C Table (Row 07) | Average R after fees | `+0.102` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:584` | `"+0.102"` | **FOUND** | Exact match: "+0.102" |
| L46 | Fabio C Table (Row 08) | Layer reading condition | `Cowen band (daily close): inside the band` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:587` | `"Cowen band (daily close): inside the band",` | **FOUND** | Feature reading definition |
| L46 | Fabio C Table (Row 08) | Trades count | `15` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:588` | `"15",` | **FOUND** | Exact match: "15" |
| L46 | Fabio C Table (Row 08) | Win percentage | `40.0` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:589` | `"40.0",` | **FOUND** | Exact match: "40.0" |
| L46 | Fabio C Table (Row 08) | Average R after fees | `-0.207` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:590` | `"-0.207"` | **FOUND** | Exact match: "-0.207" |
| L47 | Fabio C Table (Row 09) | Layer reading condition | `Cowen band (daily close): above the band` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:593` | `"Cowen band (daily close): above the band",` | **FOUND** | Feature reading definition |
| L47 | Fabio C Table (Row 09) | Trades count | `304` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:594` | `"304",` | **FOUND** | Exact match: "304" |
| L47 | Fabio C Table (Row 09) | Win percentage | `30.6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:595` | `"30.6",` | **FOUND** | Exact match: "30.6" |
| L47 | Fabio C Table (Row 09) | Average R after fees | `-0.001` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:596` | `"-0.001"` | **FOUND** | Exact match: "-0.001" |
| L48 | Fabio C Table (Row 10) | Layer reading condition | `Funding sign: positive` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:599` | `"Funding sign: positive",` | **FOUND** | Feature reading definition |
| L48 | Fabio C Table (Row 10) | Trades count | `453` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:600` | `"453",` | **FOUND** | Exact match: "453" |
| L48 | Fabio C Table (Row 10) | Win percentage | `31.6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:601` | `"31.6",` | **FOUND** | Exact match: "31.6" |
| L48 | Fabio C Table (Row 10) | Average R after fees | `+0.055` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:602` | `"+0.055"` | **FOUND** | Exact match: "+0.055" |
| L49 | Fabio C Table (Row 11) | Layer reading condition | `Funding sign: negative` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:605` | `"Funding sign: negative",` | **FOUND** | Feature reading definition |
| L49 | Fabio C Table (Row 11) | Trades count | `65` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:606` | `"65",` | **FOUND** | Exact match: "65" |
| L49 | Fabio C Table (Row 11) | Win percentage | `32.3` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:607` | `"32.3",` | **FOUND** | Exact match: "32.3" |
| L49 | Fabio C Table (Row 11) | Average R after fees | `+0.105` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:608` | `"+0.105"` | **FOUND** | Exact match: "+0.105" |
| L50 | Fabio C Table (Row 12) | Layer reading condition | `Session (UTC): US, 13-21` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:611` | `"Session (UTC): US, 13-21",` | **FOUND** | Feature reading definition |
| L50 | Fabio C Table (Row 12) | Trades count | `518` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:612` | `"518",` | **FOUND** | Exact match: "518" |
| L50 | Fabio C Table (Row 12) | Win percentage | `31.7` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:613` | `"31.7",` | **FOUND** | Exact match: "31.7" |
| L50 | Fabio C Table (Row 12) | Average R after fees | `+0.062` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:614` | `"+0.062"` | **FOUND** | Exact match: "+0.062" |
| L51 | Fabio C Table (Row 13) | Layer reading condition | `RSI 14 (1h): middle, 40 to 60` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:617` | `"RSI 14 (1h): middle, 40 to 60",` | **FOUND** | Feature reading definition |
| L51 | Fabio C Table (Row 13) | Trades count | `311` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:618` | `"311",` | **FOUND** | Exact match: "311" |
| L51 | Fabio C Table (Row 13) | Win percentage | `34.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:619` | `"34.4",` | **FOUND** | Exact match: "34.4" |
| L51 | Fabio C Table (Row 13) | Average R after fees | `+0.161` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:620` | `"+0.161"` | **FOUND** | Exact match: "+0.161" |
| L52 | Fabio C Table (Row 14) | Layer reading condition | `RSI 14 (1h): low, 40 or below` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:623` | `"RSI 14 (1h): low, 40 or below",` | **FOUND** | Feature reading definition |
| L52 | Fabio C Table (Row 14) | Trades count | `108` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:624` | `"108",` | **FOUND** | Exact match: "108" |
| L52 | Fabio C Table (Row 14) | Win percentage | `27.8` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:625` | `"27.8",` | **FOUND** | Exact match: "27.8" |
| L52 | Fabio C Table (Row 14) | Average R after fees | `-0.192` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:626` | `"-0.192"` | **FOUND** | Exact match: "-0.192" |
| L53 | Fabio C Table (Row 15) | Layer reading condition | `RSI 14 (1h): high, 60 or above` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:629` | `"RSI 14 (1h): high, 60 or above",` | **FOUND** | Feature reading definition |
| L53 | Fabio C Table (Row 15) | Trades count | `99` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:630` | `"99",` | **FOUND** | Exact match: "99" |
| L53 | Fabio C Table (Row 15) | Win percentage | `27.3` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:631` | `"27.3",` | **FOUND** | Exact match: "27.3" |
| L53 | Fabio C Table (Row 15) | Average R after fees | `+0.027` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:632` | `"+0.027"` | **FOUND** | Exact match: "+0.027" |
| L54 | Fabio C Table (Row 16) | Layer reading condition | `WaveTrend (1h): middle` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:635` | `"WaveTrend (1h): middle",` | **FOUND** | Feature reading definition |
| L54 | Fabio C Table (Row 16) | Trades count | `427` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:636` | `"427",` | **FOUND** | Exact match: "427" |
| L54 | Fabio C Table (Row 16) | Win percentage | `31.9` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:637` | `"31.9",` | **FOUND** | Exact match: "31.9" |
| L54 | Fabio C Table (Row 16) | Average R after fees | `+0.085` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:638` | `"+0.085"` | **FOUND** | Exact match: "+0.085" |
| L55 | Fabio C Table (Row 17) | Layer reading condition | `WaveTrend (1h): oversold` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:641` | `"WaveTrend (1h): oversold",` | **FOUND** | Feature reading definition |
| L55 | Fabio C Table (Row 17) | Trades count | `42` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:642` | `"42",` | **FOUND** | Exact match: "42" |
| L55 | Fabio C Table (Row 17) | Win percentage | `28.6` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:643` | `"28.6",` | **FOUND** | Exact match: "28.6" |
| L55 | Fabio C Table (Row 17) | Average R after fees | `-0.107` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:644` | `"-0.107"` | **FOUND** | Exact match: "-0.107" |
| L56 | Fabio C Table (Row 18) | Layer reading condition | `WaveTrend (1h): overbought` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:647` | `"WaveTrend (1h): overbought",` | **FOUND** | Feature reading definition |
| L56 | Fabio C Table (Row 18) | Trades count | `49` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:648` | `"49",` | **FOUND** | Exact match: "49" |
| L56 | Fabio C Table (Row 18) | Win percentage | `32.7` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:649` | `"32.7",` | **FOUND** | Exact match: "32.7" |
| L56 | Fabio C Table (Row 18) | Average R after fees | `-0.001` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:650` | `"-0.001"` | **FOUND** | Exact match: "-0.001" |
| L57 | Fabio C Table (Row 19) | Layer reading condition | `Relative volume (1h): low third` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:653` | `"Relative volume (1h): low third",` | **FOUND** | Feature reading definition |
| L57 | Fabio C Table (Row 19) | Trades count | `173` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:654` | `"173",` | **FOUND** | Exact match: "173" |
| L57 | Fabio C Table (Row 19) | Win percentage | `28.9` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:655` | `"28.9",` | **FOUND** | Exact match: "28.9" |
| L57 | Fabio C Table (Row 19) | Average R after fees | `-0.002` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:656` | `"-0.002"` | **FOUND** | Exact match: "-0.002" |
| L58 | Fabio C Table (Row 20) | Layer reading condition | `Relative volume (1h): high third` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:659` | `"Relative volume (1h): high third",` | **FOUND** | Feature reading definition |
| L58 | Fabio C Table (Row 20) | Trades count | `173` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:660` | `"173",` | **FOUND** | Exact match: "173" |
| L58 | Fabio C Table (Row 20) | Win percentage | `32.4` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:661` | `"32.4",` | **FOUND** | Exact match: "32.4" |
| L58 | Fabio C Table (Row 20) | Average R after fees | `+0.137` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:662` | `"+0.137"` | **FOUND** | Exact match: "+0.137" |
| L59 | Fabio C Table (Row 21) | Layer reading condition | `Relative volume (1h): middle third` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:665` | `"Relative volume (1h): middle third",` | **FOUND** | Feature reading definition |
| L59 | Fabio C Table (Row 21) | Trades count | `172` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:666` | `"172",` | **FOUND** | Exact match: "172" |
| L59 | Fabio C Table (Row 21) | Win percentage | `33.7` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:667` | `"33.7",` | **FOUND** | Exact match: "33.7" |
| L59 | Fabio C Table (Row 21) | Average R after fees | `+0.049` | `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json:668` | `"+0.049"` | **FOUND** | Exact match: "+0.049" |

---

Noticed: `amendments 1-8 of ROADMAP 2.1` in output.md line 1 are located in `MyTradingSys/research/meta_label_roadmap_2026-10-31/ROADMAP.md:152-160` (not in numbers.json or PRE_REG.md); setup parameter `n6` is defined in `PRE_REG.md:11` and `analyze.py:358` but omitted from numbers.json setup metadata; and every one of the 176 outcome metrics and single-feature table cells across Tom VP and Fabio Model C matches `numbers.json` bit-identically.
