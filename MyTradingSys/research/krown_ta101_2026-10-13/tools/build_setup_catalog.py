"""build_setup_catalog.py: writes KROWN_SETUP_CATALOG.md (gate G2 of LAYER_REBUILD_PLAN_2026-10-15.md).

Every block quote is COPIED by script from extracts/extract_<id>.md (or, for the cross-trader table, from the Tom/Fabio catalogue
and the Malkan summary), never retyped. A token in the text below is replaced like this:
    [[Q SNR 12 | Only a close beyond]]   -> the quote line + its Source GPS line, from concept SNR-12 (code per MANIFEST.csv)
    [[Q SNR 05 | #0]]                    -> the first quote of that concept
    [[L SNR 12 | Only a close beyond]]   -> extracts/extract_<id>.md:<line> (SNR-12), the file:line of that quote
    [[QF TC | substring]]                -> a quote block from another catalogue (TC = SETUP_CATALOG.md, MS = Malkan SETUP_SUMMARY.md,
                                            MXA = Malkan extract A-CQiV_UFB4)
A lookup that does not match exactly one line stops the build (exit 1) and lists every failure.

Usage (repo root):  python -I MyTradingSys/research/krown_ta101_2026-10-13/tools/build_setup_catalog.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KROWN = HERE.parent
ROOT = HERE.parents[3]
OUT = KROWN / "KROWN_SETUP_CATALOG.md"

CODES = {"CAN": "8MvxK_nxO-0", "TFR": "_t_XIBrcjRk", "TRL": "14bxwxC8gBQ", "SNR": "qEfES84jwwo", "VOL": "UqAvU1loT_k",
         "MAV": "-NXzJs5JRks", "RNG": "6aA-P4Gvhrc", "FEE": "HhV4HI9p5Uw", "GDE": "Aysdt7PBETQ", "TRD": "2-nG9bsMoPQ",
         "LVL": "2ei4fj-Ba24", "VJZ": "vjzy_KxJ_y8", "RSI": "INOCBmqQupc", "KCM": "kcMnnQr1VFg", "TOP": "7IxfsuD2wCM"}
OTHER = {"TC": ROOT / "MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md",
         "MS": ROOT / "MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md",
         "MXA": ROOT / "MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md"}
ERR = []
_cache = {}


def lines_of(path):
    if path not in _cache:
        _cache[path] = path.read_text(encoding="utf-8").splitlines()
    return _cache[path]


def find_in(lines, lo, hi, sub, tag):
    qs = [i for i in range(lo, hi) if lines[i].startswith('> "')]
    if sub == "#0":
        hits = qs[:1]
    else:
        hits = [i for i in qs if sub.lower() in lines[i].lower()]
    if len(hits) != 1 or not lines[hits[0] + 1].startswith("**Source GPS"):
        ERR.append(f"{tag} {sub!r}: {len(hits)} hit(s)")
        return None
    return hits[0]


def q_lookup(code, n, sub):
    vid = CODES[code]
    path = KROWN / "extracts" / f"extract_{vid}.md"
    lines = lines_of(path)
    head = f"### K-{vid}-{n:02d} "
    s = next((i for i, l in enumerate(lines) if l.startswith(head)), None)
    if s is None:
        ERR.append(f"{code}-{n:02d}: concept not found")
        return None
    e = next((i for i in range(s + 1, len(lines)) if lines[i].startswith("#")), len(lines))
    i = find_in(lines, s, e, sub, f"{code}-{n:02d}")
    return None if i is None else (vid, lines[i], lines[i + 1], i + 1)


def replace(m):
    kind, arg, sub = m.group(1), m.group(2).strip(), m.group(3).strip()
    if kind == "QF":
        lines = lines_of(OTHER[arg])
        i = find_in(lines, 0, len(lines), sub, f"QF {arg}")
        return "<MISSING>" if i is None else f"\n{lines[i]}\n{lines[i + 1]}\n"
    code, n = arg.split()
    r = q_lookup(code, int(n), sub)
    if r is None:
        return "<MISSING>"
    vid, q, gps, line = r
    if kind == "Q":
        return f"\n{q}\n{gps}\n"
    return f"extracts/extract_{vid}.md:{line} ({code}-{int(n):02d})"


TOKEN = re.compile(r"\[\[(Q|L|QF) ([^|\]]+?)\s*\|\s*([^\]]+?)\]\]")


def render(text):
    return TOKEN.sub(replace, text)


# ---------------------------------------------------------------------------------------------------------------------------
# summary data: id, name, one-line chart, timeframes, stop class (CLEAR / OURS / NOT STATED), BTC visible, older id
# ---------------------------------------------------------------------------------------------------------------------------
SUMMARY = [
    ("KR-S1", "ZONE-TEST: a marked zone is tested and a proof candle appears", "price returns to a wick-to-close zone that turned at least twice; a hammer, shooting star, strict engulfing or doji closes there, ideally on outsized volume, with the trend", "1d, 1w (first); 4h/6h timing", "CLEAR", "YES*", "S1"),
    ("KR-S2", "BREAK-CLOSE: a candle closes through a zone or range boundary", "a close (not a wick) beyond the outer boundary, volume expanding, then either no retest or a retest that holds", "zone's own timeframe; weekly and daily examples", "OURS", "YES*", "S2"),
    ("KR-S3", "RANGE-EDGE: trade the floor or the ceiling, never the middle", "two zones with price stuck between; proof at an edge, or the close back inside after a poke beyond it (fake-out)", "1d, 1w", "OURS", "YES*", "S3"),
    ("KR-S4", "COIL-BREAK: a range on falling volume resolves", "a range with every bounce quieter and the wedge tighter, volume down toward half its average, then the S2 close", "1d, 1w", "OURS", "YES*", "S4"),
    ("KR-S5", "MA-CONTEXT: averages as filter, band and first-touch level", "21/55 EMA cross against the 200, first touch of the 200 after a long absence, pullback into the 21-55 band, weekly 55 EMA bias, range break with the averages", "1d, 1w", "OURS", "YES", "S5"),
    ("KR-S6", "LEASH: whole candle floats above the 5 EMA", "the candle low stays above the 5 EMA for about three closes; price tends to come back to the line", "1d (Bitcoin)", "OURS", "YES", "S6"),
    ("KR-S7", "CAPITULATION: hammer on the biggest volume bar", "after a long downtrend one mega candle with a huge lower wick and a strong close on the biggest volume bar of the chart", "1w, 1d", "OURS", "YES*", "S7"),
    ("KR-S8", "VOL-COMPRESSION BREAKOUT (BBWP)", "volatility percentile below about 25-35 and falling from a high; the first candle that breaks the range with volatility back above the 50th percentile", "higher term (Bitcoin); his chart timeframe not named", "CLEAR", "YES", "S8"),
    ("KR-S9", "TOP-4 SELL FRAMEWORK for a long-term holding", "three of four around the same weeks: reversal candle, volume at 2x the 30-day average, volatility above the 85th percentile, bearish RSI divergence or MACD cross", "1w (Bitcoin), 1M (traditional markets)", "NOT STATED", "PARTIAL", "S9"),
    ("KR-S10", "TREND LINE, FIRST RETURN: reaction at a volume-anchored line", "a line through two high-volume turning points (or three touches); price comes back to it for the first time", "NOT STATED", "NOT STATED", "YES*", "new (rule KR-L04)"),
    ("KR-S11", "TREND LINE BREAK, then buy the higher low on the broken line", "a legitimate line breaks with follow-through; the line becomes a base for a higher low", "NOT STATED", "NOT STATED", "YES", "new (rules KR-L06, KR-Z09)"),
    ("KR-S12", "TREND REVERSAL CONFIRMED BY A CLOSE (dominant level)", "price closes below the dominant higher low (or above the dominant lower high); the reclaim is the confirmation", "every timeframe; higher outranks lower", "NOT STATED", "YES", "new (rule KR-L10, a filter in the spec)"),
    ("KR-S13", "EFFORT VERSUS RESULT: huge volume, tiny candle (absorption)", "the biggest volume of the chart on a tiny candle at a level; or a huge candle on no volume", "1d, 1w", "NOT STATED", "YES*", "new (rule KR-V06)"),
    ("KR-S14", "RSI DIVERGENCE: regular and hidden", "price makes a new low or high that the RSI does not confirm (regular), or a higher low / lower high that the RSI exceeds (hidden)", "1w/1M for tops; otherwise NOT STATED", "NOT STATED", "YES", "new (rule KR-S05, descriptive only in the spec)"),
    ("KR-S15", "200-WEEK SMA: buy at or below the line", "price at or below the weekly 200 SMA (about four years of price in one line)", "1w", "NOT STATED", "PARTIAL", "new (rule KR-M04)"),
    ("KR-S16", "COUNTER-TREND AT A VOLATILITY EXTREME", "enter against the move when volatility is very high; exit as volatility comes down", "NOT STATED", "NOT STATED", "YES", "new (KCM-50, no rule id)"),
]

# cross-trader overlap: (KR rows, other rows, same level type + trigger, differs, strength, evidence, quote tokens)
OVERLAP = [
    ("KR-S1", "TOM-15", "support or resistance area first, then a candle formation there", "his three formations (three in a line, inside bar, outside bar) vs hammer, star, strict engulfing, doji", "STRONG", "quoted-both-sides"),
    ("KR-S1", "FAB-5", "a level defended again and again by one side", "price zone proven by wicks/candles vs a resting order wall proven by absorption in the tape", "PARTIAL", "quoted-both-sides"),
    ("KR-S2", "TOM-6", "breakout of a balance/zone judged on the close, with volume behind it", "Tom adds clear space to the left and order flow; Krown adds the retest routine and range-height target", "STRONG", "quoted-both-sides"),
    ("KR-S3", "TOM-2", "sell the top and buy the bottom of a balance, the middle is noise", "Tom's proof is the profile (b-profile, finished auction); Krown's is a candle at the edge", "STRONG", "quoted-both-sides"),
    ("KR-S3", "TOM-12", "price pokes outside the balance, fails, and the return inside is the signal", "Tom trades the pullback after the return with the move and targets the start of the impulse; Krown acts on the close back inside", "STRONG", "quoted-both-sides"),
    ("KR-S3", "FAB-4", "a probe out of a balance that fails and comes back inside", "FAB-4 has no verbatim quote in SETUP_CATALOG.md (its rows are OURS and a frame note), so only Krown's side is in his words", "STRONG", "paraphrase"),
    ("KR-S3", "TOM-7", "short the top and long the bottom of a range, scalp", "Tom's range is measured around a flat VWAP; Krown's is two wick-to-close zones", "PARTIAL", "quoted-both-sides"),
    ("KR-S4, KR-S8", "TOM-15, TOM-6", "a compression comes first, then the breakout", "Tom reads compression in any form at a breakout level (and waits for consolidation after news); Krown measures it with falling volume or a volatility percentile", "PARTIAL", "quoted-both-sides"),
    ("KR-S4, KR-S8", "FAB-1", "a flat balance, then the first candle that breaks out with volume behind it", "Fabio's volume is order-flow (CVD, big trades) on an intraday chart; Krown's is bar volume or the volatility percentile on daily/weekly bars", "PARTIAL", "quoted-both-sides"),
    ("KR-S5", "TOM-4", "a rising average used as the pullback line inside a healthy trend", "VWAP anchored to the day (Tom) vs EMA/SMA of closes (Krown): a different line, same role", "PARTIAL", "quoted-both-sides"),
    ("KR-S9", "TOM-16", "extreme volume at a high, then sellers take over", "Tom: hedger volume and an aggressive seller, entry on the break of the last big buyers; Krown: 2x the 30-day average plus a weekly reversal candle, one of four signals", "PARTIAL", "quoted-both-sides"),
    ("KR-S9", "MAL-16", "bearish RSI divergence (price higher high, RSI lower high) as the momentum leg", "Malkan trades it alone with a red-candle confirmation; Krown uses it only as one of four top signals", "PARTIAL", "quoted-both-sides"),
    ("KR-S13", "FAB-2, FAB-5", "big effort (volume or delta) with no price result means the other side is absorbing", "bar volume against candle size (Krown) vs delta against price result in the footprint (Fabio)", "PARTIAL", "quoted-both-sides"),
    ("KR-S13", "TOM-2 (viT_ trade)", "selling pressure shown but price keeps rising", "Tom's remark is a reason to abandon a counter trade; Krown's is a setup description", "PARTIAL", "quoted-both-sides"),
    ("KR-S14", "MAL-14, MAL-16, MAL-17", "regular divergence: price makes a new extreme, the RSI does not", "Malkan gives entry on a confirming candle, stop at the swing, target the midpoint C; Krown gives none of the three", "STRONG", "quoted-both-sides"),
    ("KR-S14", "MAL-7, MAL-8, MAL-9", "reverse divergence = hidden divergence: with the trend, price holds a higher low while the RSI makes a lower low", "Malkan builds a daily/weekly entry on it; Krown only says to expect continuation", "STRONG", "quoted-both-sides"),
    ("KR-S16", "TOM-1", "fade an overextended move, exit as the extreme unwinds", "Krown's extreme is a volatility percentile with one sentence of text; Tom's is a stalled push with thin profile above value", "PARTIAL", "paraphrase"),
]
NO_OVERLAP = ["KR-S6", "KR-S7", "KR-S10", "KR-S11", "KR-S12", "KR-S15"]

# ---------------------------------------------------------------------------------------------------------------------------
HEADER = """# KROWN SETUP CATALOG: every setup Krown's 15 extracts teach, in plain chart terms (2026-10-15)

Status: gate G2 of research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md (section 3 Krown, work order item 4). Rewrite of
the nine setups S1-S9 of KROWN_LAYER_SPEC.md:57-65 into the catalogue format of research/setup_catalog_2026-10-15/SETUP_CATALOG.md
(that file and the Malkan SETUP_SUMMARY.md are not edited), plus seven setups the extracts teach that S1-S9 miss (KR-S10 to KR-S16).
No code, no detector, no backtest, no fees, no stop-size math, no VALIDATION/HOLDOUT read. Nothing here is an MTS rule. Corpus: 14 TA
videos + 1 fees video (KROWN_RULES.csv, 120 rules); the 4 videos still blocked by HTTP 429 (MANIFEST.csv) and the 18 hidden playlist
entries are NOT read. Fable 5.1 audits this file against the raw transcripts on 2026-10-20.

How to read the quotes
- Block quotes `> "..."` + `**Source GPS: <id> | BEGIN/MIDDLE/END | t=<hh:mm:ss>**` are checked against `raw_transcripts_canonical/<id>_raw.txt` by
  `python scripts/dev/verify_extract_quotes.py` (verbatim after case/punctuation normalising, position third). They are copied by
  `tools/build_setup_catalog.py` from the extracts (Krown) or from the Tom/Fabio catalogue and the Malkan summary (section 4 only);
  nothing is retyped. The `t=` stamp is the caption time and shows where to listen.
- Captions are YouTube auto-captions (English, Krown speaks English): a quote proves what he says, never a price, date or edge. Garbled
  caption words are copied as written; the extract marks them INFERRED and the note is repeated here where it matters.
- `(paraphrase)` = the extract's "Stated mechanics" or an earlier spec, not his words. NOT STATED = he gives nothing in words; nothing is
  filled in. A chart shown with "here" and no words is NOT STATED too.
- Every number is labelled. SOURCED = his words, with the `extracts/...md:<line>` of the quote (a line number is the line of the quote in
  the extract). OURS = copied from KROWN_LAYER_SPEC.md (judgement or a grid value; never presented as his).
- Stop class (per row, from his words only): CLEAR = he states a readable reference where the trade is wrong (a level, a close beyond a
  zone); OURS = he states none and the earlier spec supplied one, shown as OURS; NOT STATED = he states none and the spec has none (or the
  row is a sell signal, not an entry). A CLEAR stop is a structure, never a distance: no stop distance exists anywhere in the corpus.
- BTC visible (Y/P/N) uses the key of SETUP_CATALOG.md: klines 1m (OHLC, volume), aggTrades, and profiles computed from them are held;
  Krown needs OHLCV only (KROWN_LAYER_SPEC.md:30-34). `YES*` = needs volume, and we hold Binance volume only; he says crypto volume can be
  faked (his words follow) and should be read on major venues (VOL-04, paraphrase), which our feed does not meet (rule KR-V11 BLOCKED, conflict C6). PARTIAL =
  the data exists but the history or the number of events is too thin (stated per row). His words (volume episode):
"""

SHARED = """
## 2. Shared frame (applies to every setup)

### 2.1 Time, timeframes, trend filter, "obvious or nothing"
His home is Bitcoin and crypto on the daily and weekly, daily close 00:00 UTC (rules KR-T04, KR-T08). Closed candles only.
[[Q CAN 06 | the daily close is at zero zero UTC]]
[[Q CAN 06 | nothing is final until that clock hits zero]]
[[Q TFR 12 | the daily is a gold standard for most cryptos]]
Top-down routine (rule KR-T03): weekly = tide, daily = decision, 4h/6h = timing after the first two agree. "Agree" is not defined for
timeframes (the dominant-level trend state of KR-S12 is the nearest sourced definition).
[[Q TFR 13 | the weekly time frame in general that's gonna be your tide]]
[[Q TFR 14 | the daily time frame is generally where you're gonna want to make that decision]]
[[Q TFR 15 | really you only want to act on a four-hour time frame only after the first two agree]]
[[Q TFR 16 | if the weekly and daily disagree]]
Trend filter in front of every strategy (rule KR-L11), "obvious or nothing" (rule KR-T05):
[[Q TRD 03 | all you need to do is incorporate a condition]]
[[Q TRD 48 | I don't even have a trade]]
[[Q TRD 49 | Every every strategy I use starts]]
[[Q SNR 09 | If it ain't obvious]]
The eye test "obvious" has no formula; it becomes a fire-rate ceiling at G5, not a detector (rule KR-T05).

### 2.2 Management he states (all setups; none carries a number)
- He prefers to manage risk himself and exit when a zone breaks on a close, not to leave a resting stop. MTS requires a protective stop on
  every position (conflict C3, decision q-krown-stop open); the CLEAR stop class below is his close-based exit, not a stop order.
[[Q SNR 21 | I don't like having stop losses]]
[[Q SNR 21 | if my zone actually is breaking]]
- He warns against the obvious stop placement (a pile of stops sits just under every obvious floor); no replacement distance is given.
[[Q SNR 20 | Under every obvious floor]]
[[Q SNR 20 | keep stops away from the obvious price]]
- Sizing: volatility up means wider stops and bigger risk, so size down (rule KR-Q09, one video); the tops row scales out 20-85 % (KR-S9).
- His own statistics (82 % reconnect within two closes, 80-95 % for the 21/55 cross, 70 % compression, 26 years of 200-week back-test,
  right side of the trend 90-95 %) are claims without data in the videos (rule KR-F08): hypotheses H-M3, H-M2, H-L1, H-Q1, never inputs.
- No hit rate or R:R is stated for any setup (the 70 % win rate in SNR-21 is an illustration of risk management, not a result).
"""

ROWS = {}

ROWS["KR-S1"] = """### KR-S1 ZONE-TEST: a marked zone is tested and a proof candle appears
1. **Name / trader.** Krown (episodes SNR, LVL, CAN, RNG, VOL). Older spec id S1 (KROWN_LAYER_SPEC.md:57). His words: "zone", "wick to close", "reversal candle", "location beats shape". Side: both (the ceiling is the mirror of the floor). Rules: KR-Z01-Z04, Z08, Z15, Z17, C03-C10, V04.
2. **What you see.**
   - A zone on the daily or weekly chart, drawn from the wick extreme to the close of the pivot candle, where price turned at least twice; three to five zones at most; a pivot on heavy volume outranks the rest:
[[Q SNR 04 | anchor from a wick extreme]]
[[Q SNR 06 | That's where the price turned at least twice]]
[[Q SNR 07 | three to five zones maximum]]
[[Q SNR 08 | zone stamped on heavy volume]]
   - Price comes back to it and a proof candle prints at the zone. The four candles he teaches, each with its location rule:
[[Q CAN 10 | when a lot of buyers step in]]
[[Q CAN 11 | you get a big long wick to the upside at the top of a trend]]
[[Q CAN 16 | an engulfing candle must trade below the low of the prior]]
[[Q CAN 17 | you got a green candlestick prior]]
[[Q CAN 18 | a doji is just a complicated word]]
[[Q CAN 12 | it must be at the low the exact low]]
   - The pattern only counts at the zone, and volume adds weight:
[[Q CAN 21 | location beats shape]]
[[Q SNR 11 | candlestick formation plus volume]]
[[Q VOL 11 | volume doesn't create the signal]]
3. **Entry, stop, target (his words).**
   - Entry: wait for the test, ask for proof; then trade the confirmation close beyond the pattern's wick, not the first candle. Trigger price and order type: NOT STATED.
[[Q RNG 18 | at the floor, wait for the test]]
[[Q LVL 28 | Price reacts to the level]]
[[Q CAN 20 | you wanna see a closure in that same direction]]
[[Q CAN 20 | it's better in my experience to trade the confirmation]]
   - Inside an unbroken resistance zone he also scalps short or simply does not buy:
[[Q SNR 13 | short scalps]]
   - Stop [stop class: CLEAR, structure only]: the zone is resolved only by a close beyond its outer wick boundary, and that close is where he takes the loss; no resting stop, no distance:
[[Q SNR 20 | it's a zone, in order to resolve the zone]]
[[Q SNR 21 | if my zone actually is breaking]]
   - Target: NOT STATED. (The nearest words are scalps: "first pass you almost always have a decent scalp", KR-S10, and "scalp the boundaries", KR-S3.)
   - Management: NOT STATED beyond section 2.2.
4. **Context and timeframe(s).** Support works best in an uptrend and resistance in a downtrend; a level against the trend is weaker. Testing a level more than three times raises the chance it breaks (C1: the levels episode, LVL-29, says more touches make a level more significant, not stronger). Timeframe: daily and weekly first, 4h/6h only for timing (section 2.1).
[[Q LVL 22 | support works best in an uptrend]]
[[Q LVL 23 | against trend levels are weaker]]
[[Q SNR 19 | more than three times]]
5. **BTC visibility: YES\\*.** Wick/close zones, candles and trend state come from klines resampled to 1d/1w; volume is Binance only (section 0).
6. **Evidence.** 0 trades in a ledger. Chart examples in the extracts (T3); one winner is shown without an entry price: "price goes from 84 to 126" ([[L LVL 26 | That was a great trade]]), instrument and timeframe not named.
7. **Gaps and numbers.**
   - SOURCED: at least 2 turns ([[L SNR 06 | That's where the price turned at least twice]]); 3 to 5 zones ([[L SNR 07 | three to five zones maximum]]); heavy volume = 2x or more of the 20-period average ([[L VOL 09 | two or more times the average]], [[L VOL 07 | A 20 period simple moving average]]); hammer/star horizon the next 3 to 5 candles ([[L CAN 10 | over the next three to five candles]]); more than 3 tests ([[L SNR 19 | more than three times]]).
   - OURS (spec :57): stop A beyond the zone's far wick boundary; stop B = his close-back-beyond-zone exit plus a hard stop at 1.5 x ATR14; target = opposite zone or 2R; size of a "turn" in ATR units; ranking weights; what counts as "recent" touches.
   - NOT STATED: what makes a wick "big", how recent a touch must be, trigger price, target. Conflict C1 (more touches weaker, SNR-18/19, vs LVL-29: more touches matter more and the breakout response is stronger) is unresolved.
"""

ROWS["KR-S2"] = """### KR-S2 BREAK-CLOSE: a candle closes through a zone or range boundary
1. **Name / trader.** Krown (SNR, RNG, VOL, LVL). Older spec id S2 (KROWN_LAYER_SPEC.md:58). His words: "break", "closure", "harvest", "fuel", "retest". Side: both. Rules: KR-Z07, Z10, Z11, V05, R06, R07, M13.
2. **What you see.** Price closes beyond the outer wick boundary of a zone or range edge (above the wick high of a ceiling, below the wick low of a floor); volume expands as price leaves; afterwards the old zone acts as the opposite level if price comes back. A wick through that snaps back is a stop harvest:
[[Q SNR 12 | Only a close beyond the zone breaks a level]]
[[Q RNG 15 | how do you resolve the breakout]]
[[Q VOL 22 | a real break of a real zone comes with fuel]]
[[Q VOL 22 | The harvest is usually quiet]]
[[Q SNR 22 | the obvious poke that snaps back]]
3. **Entry, stop, target (his words).**
   - Entry: his checklist is a close through the zone, expanding volume, and a retest that holds if one comes. He says two things about the retest (conflict C2, both his): wait for it, and it is not required.
[[Q RNG 20 | One, a close through the zone]]
[[Q RNG 20 | Real breakouts bring volume expansion]]
[[Q VOL 23 | close through the zone on expanding volume]]
[[Q SNR 15 | don't chase the break]]
[[Q SNR 15 | The break was real slices back through it]]
[[Q RNG 21 | The best breakouts do not retest]]
[[Q RNG 21 | if you do get a retest]]
   - Stop [stop class: OURS]: NOT STATED. The retest video defers "entries, stops and targets" to his course (SNR-15 Stated mechanics, paraphrase). The spec's stop is OURS (below).
   - Target: when the broken zone is the edge of a range, the range height from the trigger, which he calls a heuristic:
[[Q RNG 22 | read the height of the range]]
[[Q RNG 22 | that is a heuristic not a law]]
   For a zone that is not a range edge: NOT STATED.
4. **Context and timeframe(s).** Confirmations he adds: the trend and an RSI above 70 in an upside resolution, or the averages turning the same way; each only "confirms", the close decides:
[[Q RSI 22 | If the trend is up, and you're resolving a range]]
[[Q RSI 23 | that's a damn good indication you're entering into a real reversal]]
[[Q VJZ 38 | you can't really validate that breakout]]
   A level tested more than three times is "mature" (KR-S1). Timeframe: the zone's own (which timeframe's close counts is not stated, OURS); his examples are weekly and daily Bitcoin.
5. **BTC visibility: YES\\*.** Closes, zone boundaries, bar volume against its 20-period average.
6. **Evidence.** 0 trades in a ledger. Weekly Bitcoin range examples (RNG, T3). Note: Tom's TOM-6 shows the same close-based verdict (section 4).
7. **Gaps and numbers.**
   - SOURCED: range height projected from the trigger (RNG-22, line above); RSI above 70 as the upside confirmation ([[L RSI 40 | Two, use the RSI for confirmation]]); more than 3 tests ([[L SNR 19 | more than three times]]).
   - OURS (spec :44, :58): enter at the close (arm 1) or at the first retest that holds (arm 2); "discernible" volume threshold grid {1.0, 1.25, 1.5} x the average; stop = close back inside the zone; target 2R; which timeframe's close counts.
   - NOT STATED: stop, a "discernible" volume size, number of closes, target for a non-range zone.
"""

ROWS["KR-S3"] = """### KR-S3 RANGE-EDGE: trade the floor or the ceiling, never the middle
1. **Name / trader.** Krown (episode RNG, KCM, VJZ). Older spec id S3 (KROWN_LAYER_SPEC.md:59). His words: "range", "floor and ceiling", "no man's land", "fake out". Side: both. Rules: KR-R01, R02, Z08, T06.
2. **What you see.** A range = two zones (floor and ceiling, drawn wick to close) with price stuck between. Only the two edges have an edge; the middle is no man's land. A quick poke beyond an edge that snaps back inside is the signature fake-out:
[[Q RNG 06 | exactly two places with an edge]]
[[Q RNG 07 | no man's land]]
[[Q RNG 09 | you can scalp a lot there]]
[[Q RNG 19 | The quick poke below the floor]]
   Tells that a range is forming (flat, tangled averages and shrinking volume; the RSI hanging between 40 and 60):
[[Q RNG 03 | #0]]
[[Q RSI 28 | #0]]
3. **Entry, stop, target (his words).**
   - Entry: at the edge, after the test, with proof (a candle, ideally on volume); in a fake-out only on the close back inside with proof. Scalp the range, do not use a trend strategy inside it. Order and price: NOT STATED.
[[Q RNG 18 | at the floor, wait for the test]]
[[Q RNG 19 | Only act on the close back inside with proof]]
[[Q RNG 19 | The close is effectively your verdict]]
[[Q KCM 27 | buy near the low side of the range]]
   - Stop [stop class: OURS]: NOT STATED for range trades. His only zone-failure rule is the close beyond the zone (KR-S1, SNR-21), which he says about support and resistance, not about range edges. The spec's stop is OURS (below).
   - Target: NOT STATED (the range videos say "scalp the boundaries"; no exit price or level). The opposite edge is OURS.
4. **Context and timeframe(s).** Read the mode first (trend tools fail in a range). A downside cross of the averages with no break of the range is a range play, not a reversal:
[[Q VJZ 39 | there's no real reversal, and it is more or less a range play]]
   Timeframe: daily and weekly Bitcoin examples; the scalp is "a short hold he does not size" (KR-T08, KR-R01).
5. **BTC visibility: YES\\*.** Two zones from klines; proof candle and volume as in KR-S1.
6. **Evidence.** 0 trades in a ledger; Bitcoin range examples (T3).
7. **Gaps and numbers.**
   - SOURCED: RSI hanging between 40 and 60 during a consolidation ([[L RSI 28 | #0]]); his own range view 40 to 60 against the textbook 30 to 70 ([[L RSI 27 | My personal experience]]). No other number.
   - OURS (spec :59): stop = close beyond the edge; target = opposite edge; flat-average slope threshold; tightness score.
   - NOT STATED: edge width, how many touches before the edge counts, exit, stop.
"""

ROWS["KR-S4"] = """### KR-S4 COIL-BREAK: a range on falling volume resolves
1. **Name / trader.** Krown (RNG, VOL, KCM). Older spec id S4 (KROWN_LAYER_SPEC.md:60). His words: "coil", "symmetrical triangle", "spring", "longer and tighter". Side: both (bias from the structure inside). Rules: KR-V09, R03, R04, R05, V10, T07.
2. **What you see.** A range where each bounce is quieter than the last and the wedge tightens; volume tails off toward half its average; the averages are flat and braided. The coil itself gives no direction; the structure inside does (same lows with lower highs = sellers; same highs with higher lows = buyers):
[[Q RNG 10 | every bounce quieter than the last]]
[[Q RNG 10 | We can call that a coil]]
[[Q RNG 11 | symmetrical triangle]]
[[Q VOL 24 | Falling volume tells you a big move is loading]]
[[Q RNG 12 | The longer and tighter that you consolidate]]
[[Q RNG 12 | I don't want to say always]]
[[Q RNG 16 | sellers are getting more aggressive while buyers are not]]
[[Q RNG 16 | you got same highs for sellers higher lows for buyers]]
[[Q RNG 13 | it becomes almost like 50% of the average]]
[[Q RNG 13 | not necessarily a rule]]
3. **Entry, stop, target (his words).**
   - Entry: the resolution of KR-S2 (close beyond the edge, volume expansion). He waits for the volume to tail off as the best timing factor:
[[Q RNG 24 | wait for that volume to tail off]]
[[Q RNG 15 | how do you resolve the breakout]]
   - Stop [stop class: OURS]: NOT STATED (the spec says "as S2", OURS).
   - Target: the height of the range projected from the trigger (a heuristic):
[[Q RNG 22 | read the height of the range]]
   - Management: NOT STATED.
4. **Context and timeframe(s).** Bias from the previous trend when the range is sideways (rule KR-L12). Timeframe: weekly Bitcoin examples (the volume-near-half observation is from weekly charts); daily by extension (OURS).
5. **BTC visibility: YES\\*.** Range, falling bar volume, wedge: klines.
6. **Evidence.** 0 trades in a ledger. His 70 % compression claim and "damn close to always" are claims (H-R1).
7. **Gaps and numbers.**
   - SOURCED: volume near 50 % of its average right before the breakout, an observation he says is not necessarily a rule ([[L RNG 13 | it becomes almost like 50% of the average]], [[L RNG 13 | not necessarily a rule]]); range height as the first target ([[L RNG 22 | read the height of the range]]).
   - OURS (spec :44, :60): volume-slope and tightness thresholds; flat-MA slope threshold; RSI 40-60 as a second tell; stop and target as S2.
   - NOT STATED: how long, how tight, how low the volume must go.
"""

ROWS["KR-S5"] = """### KR-S5 MA-CONTEXT: averages as filter, band and first-touch level
1. **Name / trader.** Krown (MAV, VJZ). Older spec id S5 (KROWN_LAYER_SPEC.md:61). His words: "Silver Cross", "dynamic areas of interest", "first test after a long time". Side: both. Rules: KR-M01, M02, M03, M05, M07, M09-M13. He says an average is not an entry tool, so this row lists the variants he describes; each is a context or a location, none has an entry, stop or target in his words:
[[Q VJZ 01 | #0]]
   The extract's gap note says the same in plain words: "No stop or target rules given for any moving-average trade" (extract_-NXzJs5JRks.md, Gaps section, paraphrase).
2. **What you see.**
   - 5a. Silver Cross: the 21 EMA crosses the 55 EMA; strongest with the 200 SMA (below it with a down-cross preceded the big drops; a cross plus a reclaim of the 200 was a reversal):
[[Q MAV 11 | once the 21 EMA crossed the downside]]
[[Q MAV 11 | it wasn't until Bitcoin was trading below the 200 simple]]
[[Q MAV 11 | plus Bitcoin reclaiming the 200 simple]]
[[Q VJZ 26 | the 21 EMA crossing above the green 55 EMA]]
   - 5b. First touch of the 200 after a long absence:
[[Q MAV 08 | almost always will have a reaction]]
[[Q VJZ 20 | an asset that is first testing a 200 moving average]]
   - 5c. Pullback into the 21-55 band in an uptrend, best where a horizontal zone meets the 55 EMA:
[[Q MAV 13 | the green 55 EMA as dynamic support]]
[[Q VJZ 23 | Bitcoin likes to kind of base off of them]]
[[Q VJZ 51 | really high quality bounce or pullback zone]]
   - 5d. Weekly 55 EMA bias; a reclaim given up within about two closes is a bull trap:
[[Q VJZ 12 | Whenever Bitcoin's above it]]
[[Q VJZ 13 | traditional bull trap]]
[[Q VJZ 13 | gave that up just two closures]]
   - 5e. Range break validated by a close beyond the edge with the averages turning the same way (a downside cross without a range break is a range play, KR-S3):
[[Q VJZ 38 | you can't really validate that breakout]]
   - 5f. Golden/death cross of the 50 and 200 SMA, discounted when the 200 still slopes the other way:
[[Q MAV 20 | A golden cross, as the name would imply]]
[[Q MAV 21 | The slope of the 200 simple was still up]]
[[Q MAV 21 | sell any rally]]
3. **Entry, stop, target (his words).**
   - Entry: NOT STATED for every variant (5c: the pullback into the band is "a bounce area", no trigger). Stop [stop class: OURS]: NOT STATED; the spec's stop (below the 55 EMA, or a close beyond the line) and the trail on the 55 EMA are OURS. Target: NOT STATED. For 5a he accepts giving back profit because the cross comes after the reversal:
[[Q VJZ 35 | That is the essence of trend trading]]
4. **Context and timeframe(s).** The averages are filters: they stop you shorting an uptrend and fail in chop. Timeframe: daily, and the weekly for 5d (Bitcoin, "most assets, not perfect") and the 200-week of KR-S15. Averages: 21 and 55 EMA, 200 SMA; 5 and 377 EMA on the edges.
5. **BTC visibility: YES.** All variants are closes and averages of closes.
6. **Evidence.** 0 trades in a ledger. He shows chart examples with moves (about 40,000 to 52,000 in VJZ-49, about 4,000 to 14,000 in VJZ-50); they are outcomes of a chart, not trades.
7. **Gaps and numbers.**
   - SOURCED: EMA 21, EMA 55, SMA 200 ([[L MAV 09 | #0]]); EMA 377 ([[L VJZ 21 | #0]]); EMA 5 ([[L MAV 19 | your five EMA is probably where]]); 50/200 SMA pair ([[L MAV 20 | If you're getting the 50 period]]); weekly EMA 55 (the weekly and the 55 are in the extract's Stated mechanics of VJZ-12, paraphrase; the spoken line is [[L VJZ 12 | Whenever Bitcoin's above it]]); "about two closes" as an example of a failed reclaim ([[L VJZ 13 | gave that up just two closures]]). His "more than 80 %, less than 95 %" for the 21/55 cross is a claim ([[L VJZ 27 | more than 80% of the time, less than 95% of the time]]), hypothesis H-M4, not an input.
   - OURS (spec :47, :61): "long time away" for 5b; slope thresholds; touch tolerance for the confluence in 5c; stop and trail.
   - NOT STATED: any entry, stop or target; what "a long time" is; slope numbers.
"""

ROWS["KR-S6"] = """### KR-S6 LEASH: the whole candle floats above the 5 EMA (provisional)
1. **Name / trader.** Krown (MAV only: one video, PROVISIONAL). Older spec id S6 (KROWN_LAYER_SPEC.md:62). His words: "leash", "disconnect". Side: both. Rule: KR-M06.
2. **What you see.** On the Bitcoin daily the candle low stays above a 5 EMA (the candle does not touch the line). Price is "at the end of the leash"; it tends to reconnect or go sideways until it does:
[[Q MAV 17 | short moving averages act like a leash]]
[[Q MAV 17 | not reconnecting with the line is what we call a disconnect]]
[[Q MAV 17 | Even when it disconnects, it goes sideways]]
3. **Entry, stop, target (his words).**
   - Entry: NOT STATED. What he says is a reading: with about three closes not connecting you are late, and the 5 EMA is where to expect a basing pullback:
[[Q MAV 19 | you're not really early]]
[[Q MAV 19 | your five EMA is probably where]]
   - Stop [stop class: OURS]: NOT STATED; the spec's "close below the 5 EMA" is OURS. Target: NOT STATED (prior extreme is OURS).
4. **Context and timeframe(s).** Bitcoin daily. No trend condition is stated for the disconnect itself.
5. **BTC visibility: YES.** Daily closes and a 5 EMA.
6. **Evidence.** His own statistics (a claim, hypothesis H-M3, to be recomputed, never an input):
[[Q MAV 18 | 5,284 candles]]
[[Q MAV 18 | Median lasted one candle]]
[[Q MAV 18 | strongest disconnect]]
7. **Gaps and numbers.**
   - SOURCED: EMA 5 ([[L MAV 19 | your five EMA is probably where]]). "About 3 closes" = late is in the extract's Stated mechanics of MAV-19 (paraphrase); the spoken line is [[L MAV 19 | you're not really early]].
   - OURS (spec :62): the pullback-entry reading, stop at a close below the 5 EMA, target the prior extreme.
"""

ROWS["KR-S7"] = """### KR-S7 CAPITULATION: hammer on the biggest volume bar (provisional)
1. **Name / trader.** Krown (VOL, CAN: PROVISIONAL, two videos). Older spec id S7 (KROWN_LAYER_SPEC.md:63). His words: "capitulation", "mega candle". Side: long. Rule: KR-V07 (with KR-V03).
2. **What you see.** After a long downtrend, one mega candle with a huge lower wick and a strong close, sitting on the biggest volume bar of the chart; a hammer at the exact low of the move:
[[Q VOL 20 | massive mega candle]]
[[Q VOL 20 | bottoms love heavy volume]]
[[Q CAN 13 | you're looking for big wicks the upside]]
[[Q CAN 13 | that is gonna be indicative that the low is probably in at least for now]]
   Major pivots come on outsized volume (his weekly Bitcoin examples):
[[Q VOL 13 | when you get that major spike in volume on a higher timeframe]]
[[Q VOL 13 | three and a half times the average]]
3. **Entry, stop, target (his words).**
   - Entry: NOT STATED (the hammer's confirmation close, KR-S1, is the only entry wording). Stop [stop class: OURS]: NOT STATED; the spec's "below the hammer low" is OURS. Target: NOT STATED.
4. **Context and timeframe(s).** A long downtrend with "everyone bleeding"; a drift to a low on no volume is apathy and is rarely finished:
[[Q VOL 21 | a market drifting to a low on no volume]]
   Timeframe: weekly and daily Bitcoin. Rare: his named lows are three, so power is nil.
5. **BTC visibility: YES\\*.** Needs Binance volume only; "the biggest volume bar of the chart" depends on the lookback (OURS).
6. **Evidence.** 0 trades in a ledger. Named lows (FTX, June 2022, March 2020) are from the extract's Stated mechanics (paraphrase).
7. **Gaps and numbers.**
   - SOURCED: about 2x the average at a macro low and 3 to 3.5 x at the March 2020 low are examples, not thresholds ([[L VOL 08 | This one was about 2x the moving average on it]], [[L VOL 13 | three and a half times the average]]).
   - OURS (spec :63): lookback for "biggest" and for "long downtrend"; wick ratio; stop.
"""

ROWS["KR-S8"] = """### KR-S8 VOL-COMPRESSION BREAKOUT (BBWP)
1. **Name / trader.** Krown (kcMnnQr1VFg, "How to Know Exactly When to Enter a Trade", 2026-04-06). One video, PROVISIONAL, but the only setup with an entry, a stop and an exit all in his words. Older spec id S8 (KROWN_LAYER_SPEC.md:64). He presents it as a quick hypothetical on a chart (KCM-63 Stated mechanics, paraphrase). Side: both. Rules: KR-Q01-Q07, KR-Q05.
2. **What you see.**
   - The volatility percentile (BBWP, Bollinger Band Width Percentile) falls below about 25-35, "especially if it's coming down from a high level", while price sits in a range:
[[Q KCM 63 | about 30, 35 or 25 to 35]]
[[Q KCM 13 | anywhere below about 25% tile]]
[[Q KCM 18 | low volatility periods always precede high volatility periods]]
   - Bias from the previous trend (up: look for higher lows; down: lower highs); he is positioned during the compression, not after the expansion:
[[Q KCM 64 | If it's up, our bias is for further continuation]]
[[Q KCM 22 | As long as Bitcoin's within this range]]
[[Q KCM 75 | Position during a compression, not after expansion]]
3. **Entry, stop, target (his words).**
   - Entry: do not anticipate; wait for the first candle that breaks the range with volatility rising through the 50th percentile and the momentum oscillator agreeing. His preferred variant enters earlier, inside the range, near the edge on the side of the bias, so a wrong break costs little:
[[Q KCM 65 | Wait for the first candle that breaks the range]]
[[Q KCM 47 | The right way to do it is position during compression]]
[[Q KCM 23 | I would prefer to pick a lower high]]
[[Q KCM 24 | as close to the top side of the range as possible]]
[[Q KCM 48 | I don't have to risk as much]]
   - Stop [stop class: CLEAR, structure only]: the opposite side of the compression zone; for an upside break a close below the bottom of the range; after the break it can move to the breakout area. Distance beyond the structure: NOT STATED.
[[Q KCM 66 | stop on the opposite side of the compression zone]]
[[Q KCM 67 | a closure below the bottom end of this range]]
[[Q KCM 68 | move that stop to the breakout area]]
   - Target / exit: take profit as volatility peaks; his chart example reads the 93rd percentile, then a reversal candle on high volatility:
[[Q KCM 49 | Ideally, enter when volatility is low]]
[[Q KCM 69 | 93rd percentile]]
[[Q KCM 70 | this is a shooting star right here]]
   - Management: size down as volatility rises (KR-Q09). He warns that chasing the breakout after expansion is the classic loss and that breakouts "fail very very often":
[[Q KCM 76 | These will fail very very often]]
4. **Context and timeframe(s).** His settings are for Bitcoin on higher timeframes; his chart timeframe for this example is not named:
[[Q KCM 11 | basis moving average length seven]]
[[Q KCM 12 | anything above 85%]]
5. **BTC visibility: YES.** The indicator is computed from closes; no volume venue issue.
6. **Evidence.** 0 trades in a ledger; the setup is an illustration on a chart, no result is given.
7. **Gaps and numbers.**
   - SOURCED: BBWP basis length 7 and lookback 100 ([[L KCM 11 | basis moving average length seven]]); low below about 25-35 ([[L KCM 63 | about 30, 35 or 25 to 35]]); high above 85 ([[L KCM 12 | anything above 85%]]); confirm above the 50th ([[L KCM 65 | Wait for the first candle that breaks the range]]); 93rd as an example, not a rule ([[L KCM 69 | 93rd percentile]]); 252 as a relaxed lookback ([[L KCM 38 | #0]]).
   - OURS (spec :45, :64): band multiplier 2; exact percentile formula; grid {80, 85, 90} x {25, 30, 35}; distance beyond the structure stop; range height (RNG-22) as a second exit arm.
   - NOT STATED: stop distance, which oscillator, how a range is identified, position size.
"""

ROWS["KR-S9"] = """### KR-S9 TOP-4 SELL FRAMEWORK for a long-term holding
1. **Name / trader.** Krown (7IxfsuD2wCM, "Here's How I Know When To Sell My Long Term Investments", 2026-06-28). One video, PROVISIONAL. Older spec id S9 (KROWN_LAYER_SPEC.md:65). It is a sell signal for a long-term holder, not a short entry. Side: sell (long). Rules: KR-P01-P06, C11, V02, Q02, S05, S07.
2. **What you see.** Four things around the same weeks on a weekly (Bitcoin) or monthly (traditional markets) chart: a reversal candle, extreme volume, extreme volatility and a momentum signal (bearish RSI divergence or a MACD cross). Three of four = at least a major top; all four = probably a macro top:
[[Q TOP 01 | if three of the four align]]
[[Q TOP 01 | of these four indications necessarily need to happen]]
[[Q TOP 01 | you see all four, especially]]
   - Reversal candle (the most powerful and often first; three black crows = three down bars from the high):
[[Q TOP 18 | once you see this, you should start to look for those other signals]]
[[Q TOP 20 | three black crows]]
[[Q TOP 21 | Some people would call this and define this as a bearish engulfing]]
   - Extreme volume = about 2 x the average of the past 30 days; extreme volatility = BBWP above 85; momentum = bearish RSI divergence (a MACD cross is the weakest, ignored alone):
[[Q TOP 05 | two times the the average of the past 30 days]]
[[Q TOP 14 | even just above 85%]]
[[Q TOP 28 | higher high in price, lower high in oscillator]]
[[Q TOP 08 | completely ignore it]]
3. **Entry, stop, target (his words).**
   - Entry: not an entry. He sells part of a holding when three or four signals fire; signals usually confirm a bar or two after the high, and the goal is to sell well, not the exact top:
[[Q TOP 35 | you want to see at least three]]
[[Q TOP 03 | The goal isn't to sell literally the exact top]]
[[Q TOP 03 | most of them will confirm maybe a bar or two]]
   - How much: 20 % to 80-85 % of the holding, set by the asset and its role:
[[Q TOP 02 | as much as 80 to 85%]]
   - Stop [stop class: NOT STATED]: n/a (a sell signal). Target / exit: after all four, wait for the signals to reset; "reset" and the time to reposition are not defined (rule KR-P06 BLOCKED):
[[Q TOP 36 | just wait for them to reset]]
4. **Context and timeframe(s).** Weekly and monthly, sometimes quarterly; the daily only for a very new asset:
[[Q TOP 37 | weekly, monthly, really is what we're operating]]
   Ranking: the reversal candle first, volume and volatility matter for parabolic highs, divergence is last ("the nail in the coffin"); one signal alone means little, and he lists his own non-tops (KR-P04):
[[Q TOP 09 | the reversal candle, certainly the most important]]
[[Q TOP 10 | within a few bars of each other]]
5. **BTC visibility: PARTIAL.** All four signals are OHLCV-derived (YES\\*, Binance volume). The weekly Bitcoin sample is a handful of tops (his examples: 2017, 2021); if the series we hold starts in 2017-08 (card k0) the 2017 top has no warm-up for the 100-bar BBWP lookback and the 30-bar volume average. Not verified against the disk here.
6. **Evidence.** 0 trades in a ledger. Dated Bitcoin examples for the recall check (rule KR-P05): 2017 weekly, 2021 weekly.
7. **Gaps and numbers.**
   - SOURCED: 3 of 4 ([[L TOP 35 | you want to see at least three]]); volume 2 x the 30-day average ([[L TOP 05 | two times the the average of the past 30 days]]); BBWP above 85 ([[L TOP 14 | even just above 85%]]); scale out 20-85 % ([[L TOP 02 | as much as 80 to 85%]]); signals 1-2 bars after the high ([[L TOP 03 | most of them will confirm maybe a bar or two]]); three down bars ([[L TOP 20 | three black crows]]); weekly/monthly ([[L TOP 37 | weekly, monthly, really is what we're operating]]).
   - OURS (spec :51, :65): "a few bars" = {2, 3, 4}; which 3 of 4; MACD (12, 26, 9); the 1/3-per-signal scale-out arm.
   - NOT STATED: "a few bars", reversal-candle size, reset rule, reposition level.
"""

ROWS["KR-S10"] = """### KR-S10 TREND LINE, FIRST RETURN: reaction at a volume-anchored line
1. **Name / trader.** Krown (TRL). Not in the spec's S1-S9 (rule KR-L04 only, "event study"). His words: "reaction", "first pass", "scalp". Side: both. Rules: KR-L01-L05, L08.
2. **What you see.** A line through swing highs or lows (a line through two points is a hypothesis; three touches make a trend); two touches are enough if both turning points sit on heavy volume, "double or more the recent volume bars around those lows or highs". Price comes back to the line for the first time:
[[Q TRL 08 | two points draw a line]]
[[Q TRL 08 | what makes this a trend is three touches]]
[[Q TRL 09 | two touches on heavy volume]]
[[Q TRL 09 | double or more the recent volume bars]]
[[Q TRL 10 | big volume spikes on highs or lows]]
3. **Entry, stop, target (his words).**
   - Entry: expect a reaction on the first return, at least a bounce; the first pass gives a decent scalp, not a home run. Trigger: NOT STATED.
[[Q TRL 11 | we should expect a reaction there]]
[[Q TRL 12 | first pass you almost always have a decent scalp]]
[[Q TRL 12 | we're not trying to predict the future]]
   - Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED. Management: NOT STATED.
4. **Context and timeframe(s).** Horizontal levels matter more than diagonals (KR-L08). Timeframe: NOT STATED (his Bitcoin examples; the spec scopes the layer to 1w/1d/6h/4h, OURS).
5. **BTC visibility: YES\\*.** Swings from klines; "heavy volume" is Binance volume.
6. **Evidence.** 0 trades in a ledger; one short scalp into a resistance line is described.
7. **Gaps and numbers.**
   - SOURCED: 3 touches for a trend ([[L TRL 08 | what makes this a trend is three touches]]); 2 touches on heavy volume, double or more the recent bars ([[L TRL 09 | double or more the recent volume bars]]).
   - OURS: number of recent bars for "recent", swing size k (spec :42), line tolerance ("slices through").
   - NOT STATED: stop, target, hold time, size.
"""

ROWS["KR-S11"] = """### KR-S11 TREND LINE BREAK, then buy the higher low on the broken line
1. **Name / trader.** Krown (TRL, SNR). Not in the spec's S1-S9 (rules KR-L06, Z09). His words: "a break is new information", "the line changes jobs". Side: both.
2. **What you see.** A legitimate line (not bent to fit) breaks with real follow-through; the same line then becomes the base for one or more higher lows (or the ceiling for lower highs). A phantom line breaks and crashes back:
[[Q TRL 14 | when it breaks out over here you actually get real fall through]]
[[Q TRL 19 | a break is not your line failing]]
[[Q TRL 19 | old support new resistance]]
[[Q TRL 19 | not gonna be as binary]]
3. **Entry, stop, target (his words).**
   - Entry: buy a higher low at the broken line after the break. Trigger candle and price: NOT STATED.
[[Q TRL 15 | uses it more importantly that same trend line as a basing point]]
[[Q TRL 15 | a pretty easy chance to buy what is effectively a higher low]]
   - Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED. Management: NOT STATED. He adds that the line can break again, especially on lower timeframes (TRL-15, paraphrase).
4. **Context and timeframe(s).** The zone version of the same flip is the retest of KR-S2 (SNR-14). Timeframe: NOT STATED.
5. **BTC visibility: YES.** Line and closes from klines.
6. **Evidence.** 0 trades in a ledger; chart example with a Bitcoin low base (T3).
7. **Gaps and numbers.** No number. NOT STATED: how many higher lows, how far the follow-through must run, stop, target.
"""

ROWS["KR-S12"] = """### KR-S12 TREND REVERSAL CONFIRMED BY A CLOSE (dominant level)
1. **Name / trader.** Krown (TRD; the "dominant highs and lows" episode, 2026-03-16). In the spec only as a filter (rule KR-L10); catalogued here because he says when a reversal entry is "not late". Side: both. Rules: KR-L09, L10, L11, L12.
2. **What you see.** Every market on every timeframe is an uptrend (higher highs and higher lows), a downtrend (lower lows and lower highs) or a range. A dominant low is the lowest low before price makes a new high; in a downtrend the dominant lower high is the most recent high from which a new low was made. A reversal is not confirmed until price trades and closes beyond the dominant level:
[[Q TRD 07 | higher highs and higher lows]]
[[Q TRD 14 | the dominant lows are the lows]]
[[Q TRD 16 | I would not confirm a reversal]]
[[Q TRD 18 | in a downtrend, the dominant lower highs]]
[[Q TRD 22 | very much skeptical]]
   One-bar jagged peaks are not treated as highs or lows:
[[Q TRD 24 | #0]]
3. **Entry, stop, target (his words).**
   - Entry: after the reclaim close; he reframes feeling late as being on time with a confirmation. Trigger price: NOT STATED.
[[Q TRD 23 | right on time with a confirmation]]
   - Stop [stop class: NOT STATED]: NOT STATED. He accepts a trap loss quickly; no level, no size:
[[Q TRD 44 | your bull trap effectively]]
[[Q TRD 45 | I'm okay with losing on that]]
   - Target: NOT STATED.
4. **Context and timeframe(s).** In a sideways range favour the previous trend; the higher timeframe is the dominant trend:
[[Q TRD 33 | The previous trend is your friend]]
   Timeframe: every timeframe; which timeframe's close counts is not stated (OURS).
5. **BTC visibility: YES.** A state machine over swings and closes.
6. **Evidence.** 0 trades in a ledger. His claim that this keeps you on the right side of the trend 90-95 % of the time is hypothesis H-L1, not an input (rule KR-F08, paraphrase).
7. **Gaps and numbers.**
   - SOURCED: no numeric parameter; the state machine is in words.
   - OURS (spec :42): bars each side {2, 3, 5}; size of a "one-bar peak"; swings on closes vs highs/lows; "about the same" range tolerance.
   - NOT STATED: entry order, stop, target.
"""

ROWS["KR-S13"] = """### KR-S13 EFFORT VERSUS RESULT: huge volume, tiny candle (absorption)
1. **Name / trader.** Krown (UqAvU1loT_k, volume episode, 2026-09-26). Not in the spec's S1-S9 (rule KR-V06). One video, PROVISIONAL. His words: "effort versus result", "absorbed", "hollow". Side: both.
2. **What you see.** A tiny candle on the biggest volume of the chart: someone absorbed everything without letting price move. At a ceiling price likely turns back; at a floor the selling is absorbed and a bounce follows. The mirror: a huge candle on no volume is hollow:
[[Q VOL 18 | Someone threw everything at this price]]
[[Q VOL 18 | When they agree, trust the move]]
[[Q VOL 18 | you get a bounce]]
[[Q VOL 19 | a huge candle on no volume]]
3. **Entry, stop, target (his words).** Entry, stop [stop class: NOT STATED], target: all NOT STATED. He states the expectation (turn at resistance, bounce at support), not an order.
4. **Context and timeframe(s).** Daily and weekly bars; it matters at a level (compare KR-S1). Volume is Binance only (section 0).
5. **BTC visibility: YES\\*.** Volume against candle range from klines.
6. **Evidence.** 0 trades in a ledger.
7. **Gaps and numbers.** No number: "tiny", "huge" and "biggest volume of the chart" are undefined; OURS would be a ratio of range to ATR and of volume to its average.
"""

ROWS["KR-S14"] = """### KR-S14 RSI DIVERGENCE: regular and hidden
1. **Name / trader.** Krown (INOCBmqQupc "RSI Is Lying to You", 2026-04-03; also TOP). In the spec as a descriptive rule only (KR-S05, conflict C14: an earlier repo study found no edge on any timeframe). His words: "divergence", "hidden or continuation divergence". Side: both. He calls divergence the primary value of an oscillator but also "a confirmation, not a trigger".
2. **What you see.**
   - Regular bullish: price makes new lows while the RSI makes higher lows, the downtrend is weakening. Hidden bullish (continuation): price makes a higher low while the RSI makes a lower low, in an uptrend. Hidden bearish: a lower high on price while the RSI makes a higher high, in a downtrend. Regular bearish: higher high in price, lower high in the RSI:
[[Q RSI 34 | And it is effectively looking for divergences]]
[[Q RSI 36 | regular bullish divergence happens when your downtrend is weakening]]
[[Q RSI 37 | hidden bullish divergence happens in uptrends]]
[[Q RSI 39 | hidden bearish divergence is in the context of a downtrend]]
[[Q TOP 28 | higher high in price, lower high in oscillator]]
   - At weekly or monthly tops it shows three, sometimes four drives, rarely two (TOP-31). He misspoke the regular bearish case in INOCBmqQupc and the extract records it as spoken:
[[Q RSI 38 | Bearish divergence, both regular and hidden]]
3. **Entry, stop, target (his words).**
   - Entry: NOT STATED. He says what to expect, "look for a bounce" (regular bullish), "another move to the upside" (hidden bullish), continuation of the downside (hidden bearish). He also says the RSI is never a trigger:
[[Q RSI 20 | #0]]
   - Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED. Management: NOT STATED.
4. **Context and timeframe(s).** Trend first, RSI second (RSI-40). Weekly or monthly (quarterly for a long-history index) for the tops version; otherwise NOT STATED.
[[Q RSI 40 | Two, use the RSI for confirmation]]
5. **BTC visibility: YES.** RSI of closes; the period is never stated (OURS 14, spec :48).
6. **Evidence.** 0 trades in a ledger.
7. **Gaps and numbers.** No numeric parameter in his words. OURS (spec :48): RSI period 14, divergence lookback and spacing. NOT STATED: lookback, spacing, size of the RSI difference, entry, stop, target.
"""

ROWS["KR-S15"] = """### KR-S15 200-WEEK SMA: buy at or below the line
1. **Name / trader.** Krown (-NXzJs5JRks, moving-average episode, 2026-10-03). Not in the spec's S1-S9 (rule KR-M04, hypothesis H-M2). Side: long.
2. **What you see.** Price at or below the 200 SMA on the weekly chart, "about four years of price in one line". The extract (paraphrase of the Stated mechanics) records that Bitcoin's lows of 2015, 2018, 2020 and 2022 were called by it, and that buys at or below it were valuable long term. His back-test (26 years, six assets, 80 touches) is a claim stated in another video:
[[Q MAV 16 | This 200 simple on the weekly]]
[[Q MAV 16 | I back tested 26 years]]
3. **Entry, stop, target (his words).** Entry, stop [stop class: NOT STATED], target: all NOT STATED. The buy-at-or-below wording is the extract's paraphrase; there is no verbatim quote for it in the block.
4. **Context and timeframe(s).** Weekly only.
5. **BTC visibility: PARTIAL.** A 200-period weekly SMA needs 200 weekly bars. If the series we hold starts in 2017-08 (card k0, not verified against the disk) the first valid value is about mid-2021, so only the 2022 low of his four is on our data. Few events: descriptive only.
6. **Evidence.** 0 trades in a ledger; the touches are chart observations.
7. **Gaps and numbers.** SOURCED: 200 periods on the weekly ([[L MAV 16 | This 200 simple on the weekly]]). His 26 years / 6 assets / 80 touches is a claim (rule KR-F08), conflict C7. NOT STATED: how far below, how long, entry, stop, target.
"""

ROWS["KR-S16"] = """### KR-S16 COUNTER-TREND AT A VOLATILITY EXTREME
1. **Name / trader.** Krown (kcMnnQr1VFg). A single sentence, not in the spec and not in the rules ledger as its own rule (it sits next to KR-Q05/Q06). He calls it "a little more advanced" and defers detail to a course that is not in the corpus. Side: both (against the move).
2. **What you see.** Volatility very high (BBWP at the extremes, above 85 on Bitcoin) after an expansion; he plays the move that runs against the trend and leaves as volatility comes down:
[[Q KCM 50 | enter in the opposite direction when volatility is very high]]
   His high-volatility reading (KR-S8) and what he says about very high volatility:
[[Q KCM 12 | anything above 85%]]
[[Q KCM 35 | #0]]
3. **Entry, stop, target (his words).**
   - Entry: "enter in the opposite direction when volatility is very high" and nothing more (trigger NOT STATED). Exit: as volatility comes down (SOURCED in the quote above). Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED.
4. **Context and timeframe(s).** Timeframe NOT STATED; his BBWP settings are for higher-term Bitcoin (KR-S8).
5. **BTC visibility: YES.** The indicator is computed from closes.
6. **Evidence.** 0 trades in a ledger; no example is walked through.
7. **Gaps and numbers.** SOURCED: BBWP above 85 as "high" ([[L KCM 12 | anything above 85%]]). Everything else NOT STATED. Treat as a lead, not a rule.
"""

SECTION4_HEAD = """
## 4. Cross-trader overlap (research leads, not findings)

Agreement between independent traders is a research lead, not evidence: Tom, Fabio, Malkan and Krown teach in different markets and
timeframes, and none of the rows has a fee-net result. A row is listed only where both describe the same chart event, meaning the same
level type and the same trigger class. STRONG = same level type and same trigger class; PARTIAL = same event seen through a different
instrument or trigger (the difference is stated). Evidence: `quoted-both-sides` = both rows carry a block quote for the event (quotes below
or in the cited rows); `paraphrase` = only one side is in his words, or the match is my reading of a thin quote.

| KR row | other trader's row | same chart event | what differs | strength | evidence |
|---|---|---|---|---|---|
"""

SECTION4_QUOTES = """
### 4.1 The side-by-side quotes behind the quoted-both-sides rows

**KR-S3 and TOM-2 (the middle is noise).**
[[Q RNG 07 | no man's land]]
[[QF TC | everything in between is just noise]]

**KR-S3 and TOM-12 (poke outside the balance, then the return inside).**
[[Q RNG 19 | The quick poke below the floor]]
[[QF TC | The market has traded, crossed over briefly]]

**KR-S2 and TOM-6 (the close is the verdict).**
[[Q SNR 12 | Only a close beyond the zone breaks a level]]
[[QF TC | in the PBD concept, we don't use the absolute high and low points]]
[[QF TC | I have a breakout here with this higher closing price]]

**KR-S1 and TOM-15 (a candle formation only counts at a support or resistance area).**
[[Q CAN 22 | when you align these things]]
[[QF TC | it's also absolutely essential to check whether there was a resistance or support area beforehand]]

**KR-S1 and FAB-5 (a level defended again and again).**
[[Q CAN 21 | if you get a same hammer twice]]
[[QF TC | you have a protection wall that is there]]

**KR-S3 and TOM-7 (short the top, long the bottom).**
[[Q KCM 27 | buy near the low side of the range]]
[[QF TC | keep looking for shorts at the top]]

**KR-S4, KR-S8 and TOM-15, TOM-6 (compression first).**
[[Q RNG 10 | We can call that a coil]]
[[QF TC | check beforehand whether a compression has built up]]
[[QF TC | I wait to see if a consolidation occurs]]

**KR-S4, KR-S8 and FAB-1 (the first candle that breaks out with volume).**
[[Q KCM 65 | Wait for the first candle that breaks the range]]
[[QF TC | the first moment that we had some kind of follow up on volume]]

**KR-S5 and TOM-4 (a rising average as the pullback line in a trend).**
[[Q MAV 13 | the green 55 EMA as dynamic support]]
[[QF TC | can wait until the VWAP gives me a pullback]]

**KR-S9 and TOM-16 (extreme volume at a high, then sellers).**
[[Q TOP 05 | two times the the average of the past 30 days]]
[[QF TC | This volume isn't created by us traders]]
[[QF TC | an aggressive seller finally comes in]]

**KR-S9, KR-S14 and MAL-16 (bearish RSI divergence).**
[[Q TOP 28 | higher high in price, lower high in oscillator]]
[[QF MS | It is making a new high from A to B but RSI has made a lower high]]

**KR-S14 and MAL-17, MAL-14 (regular bullish divergence).**
[[Q RSI 36 | regular bullish divergence happens when your downtrend is weakening]]
[[QF MS | Bullish divergence will come in a down trend]]
[[QF MS | this divergence is now telling us to buy]]

**KR-S14 and MAL-7, MAL-8, MAL-9 (reverse divergence = hidden divergence).**
[[Q RSI 37 | hidden bullish divergence happens in uptrends]]
[[QF MXA | many people also call hidden divergence]]
[[QF MS | Whenever you look at an up trend, what I have to look for is a positive reverse divergence]]

**KR-S13 and FAB-2, FAB-5 (effort without result).**
[[Q VOL 18 | Someone threw everything at this price]]
[[QF TC | the result of the price for a pressure in by delta was almost zero]]

**KR-S13 and TOM-2 (the viT_ trade).**
[[Q VOL 18 | When they agree, trust the move]]
[[QF TC | Thirdly, although the delta showed]]

### 4.2 Context overlap that is not a row

Krown's RSI regime (KR-S03: in an uptrend the RSI generally holds above 40, in a downtrend below 60, 40-60 means a range) is the same
40/60 regime Malkan's RSI system uses (MAL-2, MAL-10, MAL-13; KROWN_LAYER_SPEC.md:89 already records this). Krown uses it as a context
filter, Malkan as the entry rule (RSI taking support at 60, daily RSI near 40 under a monthly/weekly RSI above 60). It is a lead for the
Malkan layer's G3 marks, not a Krown setup.
[[Q RSI 17 | #0]]
[[QF MS | I showed you a couple of examples]]
"""

FOOT = """
## 5. What this catalogue does not settle

- Corpus: 14 TA videos + 1 fees video. The 4 videos blocked by HTTP 429 (hNfjyrJEytI, fMRvOt26xcA, LB3DRYxnA0A, _JoJbu_Ug-A) and the 18 hidden
  playlist entries are unread; a setup there would be missing from this file. 67 of the 105 non-reject rules come from fewer than 3 videos
  (PROVISIONAL, KROWN_LAYER_SPEC.md:15); every KR row except KR-S1 to KR-S4 and the filters in 2.1 rests on one or two videos.
- No Krown trade exists: the corpus is a concept course, so there is no ledger and no real-trade evidence for any row (tier T3).
- Stops: only KR-S1 (close-based exit) and KR-S8 (far side of the compression zone) have a stated structure; no distance exists. His preference
  not to leave a resting stop conflicts with the MTS protective-stop rule (C3, decision q-krown-stop).
- Volume: all `YES*` rows need volume and we hold Binance volume only (C6, KR-V11 BLOCKED).
- Open conflicts carried from KROWN_CONSOLIDATED.md and not settled here: C1 (touches weaken vs matter), C2 (retest required vs not), C3
  (resting stop), C5/C10 (plain relative volume is a clock on BTC; 20 vs 30 vs 60 periods), C13 (85 vs 80-85, 25 vs 25-35), C14 (RSI divergence
  has no edge in the repo's own study).
- Earlier repo evidence is not friendly to the S/R, candle and divergence rows (KROWN_LAYER_SPEC.md:21-24); this file does not test it.
- Next steps (not done here): G3 blind eye-read of KR-S1 to KR-S4, KR-S8 by two readers on BTC charts; the Krown cards Q66-Q69 stay untouched until then.
"""


def build():
    out = [render(HEADER).rstrip("\n")]
    out.append("""[[Q VOL 04 | #0]]""")
    out[-1] = render(out[-1])
    # summary
    s = ["", "## 0. Summary", "",
         "| id | setup | what you see (one line) | timeframe(s) | stop class | BTC visible | older id |", "|---|---|---|---|---|---|---|"]
    for r in SUMMARY:
        s.append("| " + " | ".join(r) + " |")
    cnt = {}
    for r in SUMMARY:
        cnt[r[4]] = cnt.get(r[4], 0) + 1
    btc = {}
    for r in SUMMARY:
        k = r[5].rstrip("*")
        btc[k] = btc.get(k, 0) + 1
    st = sum(1 for o in OVERLAP if o[4] == "STRONG")
    pa = sum(1 for o in OVERLAP if o[4] == "PARTIAL")
    qb = sum(1 for o in OVERLAP if o[5] == "quoted-both-sides")
    s += ["",
          f"Counts: {len(SUMMARY)} setups = the nine of the older spec (KR-S1 to KR-S9) + {len(SUMMARY) - 9} the extracts teach that S1-S9 miss "
          f"(KR-S10 to KR-S16). Stop class: CLEAR {cnt.get('CLEAR', 0)}, OURS {cnt.get('OURS', 0)}, NOT STATED {cnt.get('NOT STATED', 0)}. "
          f"BTC visible: YES {btc.get('YES', 0)} (of which {sum(1 for r in SUMMARY if r[5] == 'YES*')} need volume, YES*), PARTIAL {btc.get('PARTIAL', 0)}, NO {btc.get('NO', 0)}. "
          f"Cross-trader overlap: {len(OVERLAP)} pairs (STRONG {st}, PARTIAL {pa}; quoted-both-sides {qb}, paraphrase {len(OVERLAP) - qb}); "
          f"{len(NO_OVERLAP)} rows have none ({', '.join(NO_OVERLAP)}).", ""]
    out.append("\n".join(s))
    out.append("""## 1. Where the older S1-S9 went (duplicate map)

| older id (KROWN_LAYER_SPEC.md:57-65) | now | what changed |
|---|---|---|
| S1 ZONE-TEST | KR-S1 | stop re-read from his words: close-based exit (CLEAR); the 1.5 x ATR14 hard stop and the opposite-zone / 2R target stay OURS |
| S2 BREAK-CLOSE | KR-S2 | stop is OURS (he gives none); the range-height target is his, and only for a range edge |
| S3 RANGE-EDGE | KR-S3 | stop is OURS (the close-beyond-the-edge rule is his for S/R zones, not said for range edges) |
| S4 COIL-BREAK | KR-S4 | the "volume near 50 % of average" cue is his, labelled an observation |
| S5 MA-CONTEXT | KR-S5 | split into variants 5a-5f; none has an entry, stop or target in his words |
| S6 LEASH, S7 CAPITULATION | KR-S6, KR-S7 | provisional (one or two videos); stops OURS |
| S8 VOL-COMPRESSION BREAKOUT | KR-S8 | unchanged in substance: the only setup with entry, stop structure and exit in his words |
| S9 TOP-4 SELL FRAMEWORK | KR-S9 | a sell signal, so stop class NOT STATED; BTC visibility lowered to PARTIAL for history/warm-up |
| none | KR-S10 to KR-S16 | trend-line first return, trend-line break and higher low, dominant-level reversal, effort vs result, RSI divergence, 200-week SMA, counter-trend at a volatility extreme |

Context filters of the spec (trend state per timeframe, mode, range-middle exclusion, volatility gates, RSI zones, volume confirms,
higher-timeframe veto) are not setups; they appear as "Context" lines in the rows and in section 2.
""")
    out.append(render(SHARED).strip("\n"))
    out.append("\n## 3. Krown setups\n")
    for r in SUMMARY:
        out.append(render(ROWS[r[0]]).rstrip("\n") + "\n")
    out.append(render(SECTION4_HEAD).rstrip("\n"))
    for o in OVERLAP:
        out.append("| " + " | ".join(o) + " |")
    out.append("")
    out.append("No overlap found for: " + ", ".join(NO_OVERLAP) + " (leash on a 5 EMA, capitulation hammer, volume-anchored trend lines, dominant-level trend flips, the 200-week SMA have no counterpart in the Tom, Fabio or Malkan rows read for this file).")
    out.append(render(SECTION4_QUOTES).rstrip("\n"))
    out.append(render(FOOT).rstrip("\n"))
    text = "\n".join(out) + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main():
    text = build()
    if ERR or "<MISSING>" in text:
        print("BUILD FAILED, lookups that did not match exactly one quote:")
        for e in ERR:
            print("  ", e)
        return 1
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"wrote {OUT} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
