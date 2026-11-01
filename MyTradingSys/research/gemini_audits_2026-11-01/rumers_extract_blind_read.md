# SUPPORTED: 2, PARTLY: 6, NOT_IN_QUOTE: 0

# Rumers Extracts 1 & 2 Blind Re-Read Audit

Audit of the 8 testable mechanical setup rules defined in Section 3 of `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md` and `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md`.
For each rule, the Entry, Stop Loss, and Target conditions are checked against the verbatim caption quotes cited in Section 2 of each extract and canonical transcripts in `raw_transcripts_canonical/`.
Facts only, no verdict on edge.

## Summary Counts

- **Total Rules Audited**: 8
- **SUPPORTED**: 2 (all Entry, Stop, and Target specifications directly match verbatim caption quotes)
- **PARTLY**: 6 (Entry, Stop, or Target supported; one or more specific execution nuances or levels not present in Section 2 verbatim quotes)
- **NOT_IN_QUOTE**: 0

---

## Audit Table

| Rule | Field | Status | Extract File:Line | Quote File:Line |
| :--- | :--- | :--- | :--- | :--- |
| `RUMERS_EXTRACT_1 s3 T1 (RUMERS-ORB-MANIP-REVERSAL)` | Entry, Stop, Target | SUPPORTED | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:139-145` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:63,66,69,124,127,130` (`raw_transcripts_canonical/6WfTIyJ-YzQ_raw.txt:8`, `raw_transcripts_canonical/aTMFouI9mF4_raw.txt:8`) |
| `RUMERS_EXTRACT_1 s3 T2 (RUMERS-BOX-PDH-PDL-FADE)` | Stop, Target supported; Entry (5m rejection candle closing back inside box not in verbatim quote) | PARTLY | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:147-153` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:76,79,82,85` (`raw_transcripts_canonical/EoQDQVblmMY_raw.txt:8`) |
| `RUMERS_EXTRACT_1 s3 T3 (RUMERS-VWAP-SEPARATOR-MEAN-REVERSION)` | Entry, Target supported; Stop (exhaustion wick stop not in Section 2 verbatim quote) | PARTLY | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:155-161` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:108,111,114` (`raw_transcripts_canonical/kozesVBKkg4_raw.txt:8`) |
| `RUMERS_EXTRACT_1 s3 T4 (RUMERS-VWAP-KISS-PIVOT-CONTINUATION)` | Entry supported; Stop (swing pivot) and Target (1:2 R:R) not in Section 2 verbatim quote | PARTLY | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:163-169` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:117` (`raw_transcripts_canonical/kozesVBKkg4_raw.txt:8`) |
| `RUMERS_EXTRACT_2 s3 Setup T1 (15-Minute Pattern Scalp Reversal)` | Entry, Stop supported; Target (50% midpoint target not in Section 2 verbatim quote) | PARTLY | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:139-148` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:54,57,63,66` (`raw_transcripts_canonical/T0H_jpQXdVI_raw.txt:8`) |
| `RUMERS_EXTRACT_2 s3 Setup T2 (4-Point Boundary Confluence Fade)` | Entry, Stop supported; Target (midpoint or opposite boundary not in Section 2 verbatim quote) | PARTLY | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:150-159` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:70,73,76,79,82` (`raw_transcripts_canonical/pcYO-yzAtrQ_raw.txt:8`) |
| `RUMERS_EXTRACT_2 s3 Setup T3 (Hourly RSI Liquidity Reversal)` | Entry, Stop supported; Target (previous swing / trail toward RSI 50 not in Section 2 verbatim quote) | PARTLY | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:161-171` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:86,89,92,95,98` (`raw_transcripts_canonical/hMURCHLnZVE_raw.txt:8`) |
| `RUMERS_EXTRACT_2 s3 Setup T4 (9 EMA 20% ATR Separation Reversion)` | Entry, Stop, Target | SUPPORTED | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:173-183` | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:111,114,121,124,127,130` (`raw_transcripts_canonical/xtN0U-j_4Jc_raw.txt:8`, `raw_transcripts_canonical/l0j1irTKIUw_raw.txt:8`) |

---

## Detailed Field Checks

### 1. `RUMERS_EXTRACT_1` T1: `RUMERS-ORB-MANIP-REVERSAL`
- **Entry**: Supported by `6WfTIyJ-YzQ` lines 66, 69 and `aTMFouI9mF4` lines 124, 127 (reversal candle breaking extreme, Power of Tower 30-50%, John Wick formation).
- **Stop**: Supported by `6WfTIyJ-YzQ` lines 63 ("stop loss goes below the low of the day"), 69 ("stop loss would go above the high of the day") and `aTMFouI9mF4` line 124 ("stop loss would be at the high of the day").
- **Target**: Supported by `6WfTIyJ-YzQ` line 63 ("target price is either 50% to 100% of the range"), line 69 ("Target price goes down into the middle of that range"), and `aTMFouI9mF4` line 130 ("Target would be probably somewhere here about half of that range").
- **Status**: SUPPORTED

### 2. `RUMERS_EXTRACT_1` T2: `RUMERS-BOX-PDH-PDL-FADE`
- **Entry**: PARTLY. Section 2 quotes line 76 ("close to, at or above that box... be sell side focused") and line 79 ("close to, at or below that box, do not sell"). The specific trigger "5m rejection candle closing back inside the previous day box" appears in the timestamped rules (R08) but not in the 5 verbatim quotes in Section 2.
- **Stop**: Supported by line 85 ("Stop is going to be below the low of the day").
- **Target**: Supported by line 82 ("take a line and draw right through the center of that box... don't diddle in the middle").
- **Status**: PARTLY

### 3. `RUMERS_EXTRACT_1` T3: `RUMERS-VWAP-SEPARATOR-MEAN-REVERSION`
- **Entry**: Supported by `kozesVBKkg4` line 108 ("take advantage of the separation between that assets price and the VWAP... That is going to become our trade entry") and line 111 ("90% of these trades, the very best ones, happen at the first 15 to 20 minutes of market open").
- **Stop**: NOT IN SECTION 2 QUOTE. Timestamp 00:14:56 cited for stop placement ("Placed beyond extreme exhaustion wick") is not represented in the 5 verbatim quotes selected for Section 2.
- **Target**: Supported by line 108 ("our exit is going to be the nuance of them reconvening with one another here in the future").
- **Status**: PARTLY

### 4. `RUMERS_EXTRACT_1` T4: `RUMERS-VWAP-KISS-PIVOT-CONTINUATION`
- **Entry**: Supported by `kozesVBKkg4` line 117 ("KISS pivot... usually comes after the separator. Once we've had that retracement that moves us back into VWAP, what we're going to be looking to do is have that thing right off the VWAP").
- **Stop**: NOT IN SECTION 2 QUOTE. Timestamp 00:16:17 cited for swing pivot stop is not in the Section 2 quotes.
- **Target**: NOT IN SECTION 2 QUOTE. 1:2 risk-to-reward ratio is not in the Section 2 quotes.
- **Status**: PARTLY

### 5. `RUMERS_EXTRACT_2` Setup T1: 15-Minute Pattern Scalp Reversal
- **Entry**: Supported by `T0H_jpQXdVI` lines 54, 57, 63 ("enter on the next candle, important, the next candle that takes out the top of the John Wick... enter immediately as it breaks the top"), and 66 ("high to be taken out of the John Wick... That's the entry").
- **Stop**: Supported by lines 63 ("place our stop underneath of that") and 66 ("our stop is going to go below").
- **Target**: NOT IN SECTION 2 QUOTE. 50% midpoint target is detailed in Section 1 rule R04 (line 21), but the 5 verbatim quotes in Section 2 omit the target quote.
- **Status**: PARTLY

### 6. `RUMERS_EXTRACT_2` Setup T2: 4-Point Boundary Confluence Fade
- **Entry**: Supported by `pcYO-yzAtrQ` lines 76-77 ("against a known seller... one of these candles to close under the other one") and line 79 ("broke our structure. Right there was the ideal entry").
- **Stop**: Supported by line 79 ("stop out above the high here, but let's go ahead and stay with a very tight risk").
- **Target**: NOT IN SECTION 2 QUOTE. Midpoint / opposite boundary target is in Section 1 rule R09 (line 26), but not in the Section 2 verbatim quotes.
- **Status**: PARTLY

### 7. `RUMERS_EXTRACT_2` Setup T3: Hourly RSI Liquidity Reversal
- **Entry**: Supported by `hMURCHLnZVE` line 95 ("As soon as that hourly candlestick closes green, our entry is happening above the high of that first green candlestick").
- **Stop**: Supported by line 98 ("stop loss can be placed slightly above that red candlestick right here").
- **Target**: NOT IN SECTION 2 QUOTE. Target previous swing / trailing stop toward RSI 50 is in Section 1 rule R14 (line 31), but omitted from the 5 Section 2 quotes.
- **Status**: PARTLY

### 8. `RUMERS_EXTRACT_2` Setup T4: 9 EMA 20% ATR Separation Reversion
- **Entry**: Supported by `xtN0U-j_4Jc` lines 102, 105 and `l0j1irTKIUw` lines 121, 124 ("If the distance between the 9 EMA and the price of the asset is $2.20 or more, then you have adequate separation").
- **Stop**: Supported by `l0j1irTKIUw` line 127 ("Stop goes either above the red bar or for the riskier traders, above the green bar") and line 121 ("placed the stop loss just right above the 9 EMA").
- **Target**: Supported by `xtN0U-j_4Jc` line 111 ("The target becomes revisitation of that 9 EMA"), line 114 ("use that 9 EMA as a stop-loss and even a profit trailing guide"), and `l0j1irTKIUw` line 130 ("target price becomes a break of the 9 EMA, then a follow of the 9 EMA").
- **Status**: SUPPORTED

---

Noticed: In both extracts, the 25 Section 1 stated rules cite specific video timestamps that cover every entry, stop, and target field, but the 25 Section 2 verbatim quotes (constrained to 5 quotes per video) prioritized entry triggers and stop placement over target rules for 6 of the 8 setups, resulting in PARTLY quote coverage when evaluating Section 3 exclusively against Section 2.
