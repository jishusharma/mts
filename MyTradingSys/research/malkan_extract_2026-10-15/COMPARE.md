# COMPARE: Malkan's 5-star and 7-star rules, his words versus web research, RSI_2A_SPEC and the code (2026-10-16)

Card `malkan-extract-5star-7star` (gate G1/G2, LAYER_REBUILD_PLAN). Every quote below is copied by script from `extracts/extract_<id>.md`; the
`:N` after it is the quote's line in that extract. `python scripts/dev/verify_extract_quotes.py` checks each quote against the raw transcript.
Tier T3: a quote shows what he teaches, not an edge. Hindi videos (W1HrDl70Lhk, A-CQiV_UFB4): the English line is a YouTube machine translation;
the Hindi original sits beside every quote in the extract at the line given.

## 0. Findings

1. **Stars are a confluence grade, not one fixed setup.** In his own English captions (Wvq1TZh8aF0) a daily divergence while the monthly RSI is above 60
   goes "from three star to five star or five star to seven star"; in A-CQiV_UFB4 he says reverse divergence is graded 3, 5 or 7 star by conditions he does not give.
2. **His 7-star (Wvq1TZh8aF0, END): monthly RSI above 60 + daily RSI below 40 + daily divergence; target doubled, stop unchanged.** No timeframe pairing for
   the weekly RSI is said. The mirror (short) is not stated.
3. **WEB_RESEARCH.md:162-172 7-star (Chartink screener text: monthly, weekly AND daily RSI above 60, previous 3 days above 60) is a screener author's
   definition, not Malkan's words, and it contradicts his: his daily leg is a pullback below 40, the screener's is a trend above 60.** Do not encode the screener version as his.
4. **The 5-star (W1HrDl70Lhk) is a presenter's (Trader Insights) walk-through, Hindi audio with machine translation, 4 of the 6 stop/target sentences garbled.** The readable
   parts: higher-timeframe gate = weekly AND monthly RSI above 60 (below 60 sic for the sell side); entry type 2 = RSI comes back to the sixty line and takes support, entry
   above the signal candle's high, stop below its low. No numeric target is recoverable ("2068" is a stock price on his example chart).
5. **Code:** `malkan_mtf.py` does compose the daily 40-bounce with weekly and monthly regimes (the stale docstring at `malkan_40_60.py:14-17` still says single timeframe),
   but its "BULL" regime is `min >= 40 and max >= 60` over 20 bars (the range-shift reading from WEB_RESEARCH.md:39-62), NOT "RSI above 60"; there is no divergence leg, no star grade,
   and the signal carries no entry price, stop or target. So the code encodes neither the 5-star as he states it nor the 7-star.

## 1. The 5-star (W1HrDl70Lhk, presenter explaining Malkan's 5 star RSI; SECONDARY)

### 1.1 Gate: weekly AND monthly RSI above 60 (long)

> "you can see the cream representative is better than hey, weekly and monthly all the zones are ill controlled soft condition was like it should be above Rs.60"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source: `extracts/extract_W1HrDl70Lhk.md:317`

> "I keep weekly and monthly in it every time, as soon as weekly and monthly active goes up, both the conditions will be according to both, then only that part will become cream, as long as both of them will remain above it"
**Source GPS: W1HrDl70Lhk | END**
- Source (indicator idea: zone goes cream while both stay above): `extracts/extract_W1HrDl70Lhk.md:667`

> "no green channel was created here Swami, we will not buy it now"
**Source GPS: W1HrDl70Lhk | END**
- Source (no zone, no buy): `extracts/extract_W1HrDl70Lhk.md:536` (also :899)

- Web research (WEB_RESEARCH.md:108-134): monthly >= 60, weekly >= 60, daily <= 40. **Match** on the gate.
- Caveat: the first mention of the level is garbled to "100" (`extract_W1HrDl70Lhk.md:153`, M-13; the later reading is at line 321); 60 is read from two later sentences, flagged INFERRED in the extract.
- Code: `malkan_mtf.py:53-76` gates on weekly == BULL and monthly == BULL where BULL = min(RSI, 20 bars) >= 40 and max >= 60. **PARTIAL**: stricter on the floor (40) and looser on the ceiling (touching 60 at any point in 20 bars) than "above 60" now.

### 1.2 Entry type 2 (the clearer one): RSI comes back to the sixty line and takes support

> "security tech support and 16th means how is it, it should cross the Srishti from below and then go back above the support at sixty"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source (setup): `extracts/extract_W1HrDl70Lhk.md:241` (also :760)

> "entry abodh this candle"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source (entry): `extracts/extract_W1HrDl70Lhk.md:339` (also :765)

> "stop loss will be below the candle"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source (stop, stop class CLEAR): `extracts/extract_W1HrDl70Lhk.md:350` (also :770)

> "I will just put it on high and stop loss against below the longest"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source (order on the high, stop below the lowest): `extracts/extract_W1HrDl70Lhk.md:438`

- On which timeframe the sixty-line support is read is NOT STATED in these sentences; the chart is "prepared on one base time frame" (M-07) and the other two RSIs are overlays.
- Web research bullish 5-star uses a different trigger: daily RSI near 40 with a green candle. His 40 trigger appears in the host recaps (1.4), not in this video's words. **CONFLICT between sources, not resolved here.**
- Code: `malkan_setup_bull` fires on an RSI `support` event at level 40 (tolerance 2.0, OURS) with a green bar; it does not implement the sixty-line support. **No match** for entry type 2; **match** for the 40 variant.

### 1.3 Entry type 1: both higher RSIs above the level, enter on the green candle (stop and target garbled)

> "so entry will be better half green candle"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source (entry, garbled): `extracts/extract_W1HrDl70Lhk.md:175` (also :736)

> "and stop loss will be block printed not retired children"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source (stop, stop class GARBLED, not used): `extracts/extract_W1HrDl70Lhk.md:186` (also :741)

- Nothing recoverable beyond "enter on a green candle while the weekly and monthly RSI are above the level". Not encodable; stays NOT STATED.

### 1.4 Target and sizing

> "told how much target to keep here, he himself keeps the raw test one,"
**Source GPS: W1HrDl70Lhk | MIDDLE**
- Source (target size, unresolved): `extracts/extract_W1HrDl70Lhk.md:263` (also :775)

> "target is 2068 solar heater go"
**Source GPS: W1HrDl70Lhk | END**
- Source (a price on his stock chart, not a rule): `extracts/extract_W1HrDl70Lhk.md:503` (also :867)

- No target rule can be quoted. Web research gives "first target daily RSI 60" from elearnmarkets, not from his words.
- Code: no target. A study must define the exit from ATR or the opposite RSI level and label it OURS.

### 1.5 Sell side (mirror)

> "look here, below both the teams, weekly and monthly, this candle has been taken on the screen, it is good"
**Source GPS: W1HrDl70Lhk | END**
- Source (sell example): `extracts/extract_W1HrDl70Lhk.md:579`

> "stop loss will be or Buddha Hi"
**Source GPS: W1HrDl70Lhk | END**
- Source (stop above the high, garbled): `extracts/extract_W1HrDl70Lhk.md:590` (also :820)

> "that the sale is very limited in Maithili Delhi time love"
**Source GPS: W1HrDl70Lhk | END**
- Source (few sell signals on this timeframe): `extracts/extract_W1HrDl70Lhk.md:634` (also :826)

- Mirror gate level is said as "below Rs. 60" (M-63), almost certainly 40 as in the host recaps; the extract keeps the word 60 as spoken.
- Code: `malkan_mtf_bear` (level 60, weekly and monthly BEAR). **Match** in structure, not verifiable on the numbers.

### 1.6 Host recaps of the same 5-star (other creators' words, T3 secondary)

> "To trade on the long side you have to find such trades whose 14 month RSI is above 60"
**Source GPS: -CBvFi40sIQ | BEGIN**
- Source (monthly above 60): `extracts/extract_-CBvFi40sIQ.md:32` (also :281)

> "The daily RSI i.e. 14 day RSI must be near 40"
**Source GPS: -CBvFi40sIQ | BEGIN**
- Source (daily near 40): `extracts/extract_-CBvFi40sIQ.md:48` (also :285)

> "will be above the high of the signal candle and the stoploss you will have"
**Source GPS: -CBvFi40sIQ | BEGIN**
- Source (entry above the signal candle high): `extracts/extract_-CBvFi40sIQ.md:68` (also :288)

> "to be below the low of the signal candle than your stoploss will be done"
**Source GPS: -CBvFi40sIQ | BEGIN**
- Source (stop below the signal candle low): `extracts/extract_-CBvFi40sIQ.md:76` (also :291)

> "I showed you a couple of examples of what we call as the by setup on setup number one which is five star setup with monthly about 60 weekly about 60 and daily at 40 support was the trend"
**Source GPS: 2HcJ3NeZmEQ | BEGIN**
- Source (five star = monthly 60, weekly 60, daily 40): `extracts/extract_2HcJ3NeZmEQ.md:22` (also :202, :208)

- These two videos agree with WEB_RESEARCH.md (daily 40 pullback inside weekly and monthly above 60; entry above the signal candle high; stop below its low). **Match.**

## 2. The 7-star

### 2.1 A-CQiV_UFB4 (Malkan, Hindi, machine translation): the grade, with the conditions withheld

> "seven star reverse divergence means if all the conditions are matched then it will become seven star, seven star means its strike rate means its chances of running become very high almost 80-90 but if it is five star then its chances of running will be 60-70, if it is three star then it is fine, it is loose, it will run on it, I do n't know"
**Source GPS: A-CQiV_UFB4 | END**
- Source: `extracts/extract_A-CQiV_UFB4.md:439`

> "so there are certain conditions but I think if I give so much together then you will feel like over whelm"
**Source GPS: A-CQiV_UFB4 | END**
- Source (conditions withheld): `extracts/extract_A-CQiV_UFB4.md:450`

- Raw transcript: `raw_transcripts_canonical/A-CQiV_UFB4_raw.txt:292-301` (quote spans these lines). The 80-90 and 60-70 are his claimed chances of running, no sample shown (extract Gaps, line 609).
- **7-star here = reverse divergence (PRD/NRD) with every condition matched; the list of conditions is NOT STATED.** Do not infer them from the other videos without saying so.

### 2.2 Wvq1TZh8aF0 (Malkan, English auto captions): the only stated 7-star conditions

> "but if the monthly is at 60 and there is divergence on the daily, then it becomes a seven star signal"
**Source GPS: Wvq1TZh8aF0 | END**
- Source (grade up): `extracts/extract_Wvq1TZh8aF0.md:393` (also :533)

> "RSI monthly above 60 and RSI daily below 40 and there is divergence visible, that is one of the best trades"
**Source GPS: Wvq1TZh8aF0 | END**
- Source (long: monthly above 60, daily below 40, divergence): `extracts/extract_Wvq1TZh8aF0.md:395` (also :521)

> "then double the target. The stop loss will remain the same."
**Source GPS: Wvq1TZh8aF0 | END**
- Source (target doubled, stop unchanged): `extracts/extract_Wvq1TZh8aF0.md:403` (also :527, :530)

- "above 60" and "at 60" are both said for the monthly RSI (extract Gaps, line 582); "double the target" is not defined (twice the C distance or a second target). The short mirror is NOT STATED (line 583).

### 2.3 Web research and spec

- WEB_RESEARCH.md:162-172: "Monthly RSI > 60, Weekly RSI > 60, Daily RSI > 60, Previous 3 days RSI > 60" (Chartink screener title). Not Malkan's words. **Conflicts with 2.2 on the daily leg.**
- RSI_2A_SPEC.md:20-33 (answers table, row "Higher-TF stack") already carries the Wvq1 reading (monthly > 60 + daily < 40 + divergence = best, double the target) and the 5-star row from `extract_-CBvFi40sIQ`. **Match** with 2.2 and 1.6.
- Code: `run_divergence_mtf.py` measures divergence per timeframe (imports `rsi_divergence` only), and `malkan_mtf.py` imports only `malkan_40_60`; nothing combines a monthly-above-60 gate with a daily-below-40 divergence. **Not encoded.**

## 3. Rule-by-rule summary

| rule | his words | web research | code | status |
|---|---|---|---|---|
| 5-star gate: weekly and monthly RSI above 60 | W1Hr (presenter), -CBv, 2HcJ | agrees | `malkan_mtf.py` with a different regime definition | PARTIAL |
| 5-star daily trigger: RSI near 40, green candle | -CBv, 2HcJ (hosts); not in W1Hr's readable words | agrees | `malkan_setup_bull` level 40, tol 2.0 (OURS) | MATCH (secondary) |
| 5-star entry type 2: support at the sixty line | W1Hr | not covered | not encoded | NOT ENCODED |
| 5-star entry/stop | above the signal candle high / below its low (W1Hr entry type 2, -CBv) | agrees | signal only, no entry price or stop | NOT ENCODED |
| 5-star target | not recoverable | daily RSI 60 (elearnmarkets, not his words) | none | NOT STATED |
| 7-star conditions | Wvq1: monthly above 60 + daily below 40 + divergence; A-CQiV: withheld | screener: all three above 60 + 3 prior days | none | CONFLICT (web vs his) |
| 7-star exit | Wvq1: double the target, stop unchanged | none | none | NOT ENCODED |
| grade strike rates (5-star 60-70, 7-star 80-90) | A-CQiV claim, no sample | none | none | UNVERIFIED CLAIM |

## 4. What G3/G5 can use (counts and MDE are in `research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md`)

- Testable from his words with stops on daily/weekly/monthly bars: MAL-2 (RSI back at sixty, stop below the signal candle), MAL-5 (order on the high, stop below the lowest), MAL-16/17 (divergence A-B-C), MAL-19 (7-star). Anything else needs a number the video does not give; label the choice OURS.
- The 5-star daily 40 trigger (hosts, secondary) is a legitimate layer row but is tier T3-secondary; write it as such in the catalogue.
