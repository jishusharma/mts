"""build_ledger.py: Phase 2/3 for Krown. One data list -> KROWN_RULES.csv + KROWN_CONSOLIDATED.md.

Every source token `CODE-NN` must match a real `### K-<video id>-NN` heading in extracts/ (CODE per MANIFEST.csv); a dead
pointer stops the build (exit 1). `rule` is OUR paraphrase of the extract's "Stated mechanics"; his words are in the extracts.
phase3: READY = a detector/event can be built now (parameters labelled SOURCED or OURS); BLOCKED = waits on an answer
(a pending video, the operator, or data); REJECT = framing, a claim kept only as a hypothesis, or out of scope.
n_videos < 3 = PROVISIONAL (extraction.md SAFEGUARD 2: a cluster needs >= 3 videos).

Usage (repo root):  python -I MyTradingSys/research/krown_ta101_2026-10-13/tools/build_ledger.py
"""
import csv
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# code -> video id (MANIFEST.csv is the source of truth; checked below)
CODES = {"CAN": "8MvxK_nxO-0", "TFR": "_t_XIBrcjRk", "TRL": "14bxwxC8gBQ", "SNR": "qEfES84jwwo", "VOL": "UqAvU1loT_k",
         "MAV": "-NXzJs5JRks", "RNG": "6aA-P4Gvhrc", "FEE": "HhV4HI9p5Uw",
         # batch 2 (2026-10-14): the March-June 2026 videos
         "GDE": "Aysdt7PBETQ", "TRD": "2-nG9bsMoPQ", "LVL": "2ei4fj-Ba24", "VJZ": "vjzy_KxJ_y8", "RSI": "INOCBmqQupc",
         "KCM": "kcMnnQr1VFg", "TOP": "7IxfsuD2wCM",
         # batch 3 (2026-10-18): Foundations ep8 (order book)
         "OBK": "ftK2BqggabQ"}

FAMILIES = {
    "T": "Top-down and context (timeframes, modes)",
    "Z": "Zones: support and resistance",
    "L": "Swings and trend lines",
    "V": "Volume",
    "C": "Candles",
    "M": "Moving averages",
    "R": "Range, coil and breakout",
    "Q": "Volatility (BBWP, compression and expansion)",
    "S": "RSI and momentum",
    "P": "Major tops: the four-signal sell framework",
    "X": "Risk and execution",
    "F": "Framing and claims (not rules)",
    "OBK": "Order book and market structure (Foundations ep8)",
}

# id, name, side, type, rule, params, label, sources, mirror, encodability, phase3, blockers
R = []


def add(*a):
    assert len(a) == 12, a[0]
    R.append(list(a))


def ext(rid, extra):
    """batch 2: add source tokens to an existing rule."""
    for r in R:
        if r[0] == rid:
            r[7] = r[7] + ";" + extra
            return
    raise KeyError(rid)


def setf(rid, idx, value):
    """batch 2: replace one field (idx as in add(): 5 params, 6 label, 9 encodability, 10 phase3, 11 blockers)."""
    for r in R:
        if r[0] == rid:
            r[idx] = value
            return
    raise KeyError(rid)


# ---- T: top-down and context
add("KR-T01", "Highest timeframe with enough history", "none", "PROCESS",
    "Work on the highest timeframe that has enough history: at least about 200 periods on it, around 500 ideal; zoom out first, start high, finish low.",
    "min_periods=200; ideal_periods=500", "SOURCED", "TFR-04;TFR-09;SNR-05;CAN-05", "n/a", "MECHANICAL", "READY",
    "data gate only: weekly needs about 4 years of bars for 200 periods (check BTC spot history from 2017)")
add("KR-T02", "Higher timeframe outranks lower", "none", "CONTEXT/REGIME",
    "Importance ladder 1w > 1d > 12h > 6h > 4h > 1h > 30m > 5m; a higher-timeframe signal outranks a lower one; one daily close outweighs many small closes.",
    "ladder only; no numbers beyond the ladder", "SOURCED", "TFR-03;TFR-10;TFR-11;CAN-25;SNR-05", "n/a", "PARTIAL", "READY",
    "what 'outranks' means when signals disagree is not defined: OURS rule = higher-timeframe trend state vetoes the lower one")
add("KR-T03", "Top-down routine: tide, decision, timing", "both", "PROCESS",
    "Weekly = tide (do not fight it), daily = where the decision is made, 4h or 6h = timing only after weekly and daily agree; if they disagree take no trade or the other side.",
    "roles: 1w tide, 1d decide, 4h/6h timing", "MIXED", "TFR-13;TFR-14;TFR-15;TFR-16;TFR-21", "n/a", "PARTIAL", "READY",
    "'agree' is not defined (TFR gap t=00:14:00): OURS arm = trend state from side of 200 SMA and order of 21/55 EMA")
add("KR-T04", "Daily close at 00:00 UTC, closed candles only", "none", "PROCESS",
    "The daily candle closes at 00:00 UTC; a candle is not final until its clock expires; decisions use closed candles.",
    "daily close = 00:00 UTC", "SOURCED", "CAN-06;TFR-05", "n/a", "MECHANICAL", "READY", "none (matches Binance 1d bars)")
add("KR-T05", "Obvious or nothing; most days no trade", "none", "PROCESS",
    "If it is not obvious it is not there; most of the time there is no trade; sit on your hands; there is no extra pay for low-probability trades.",
    "no numbers", "NONE", "TFR-17;SNR-09;VOL-10;TRL-03;TRL-21", "n/a", "DISCRETIONARY", "READY",
    "the eye part is DISCRETIONARY; it becomes a fire-rate ceiling in the pre-registration, not a detector")
add("KR-T06", "Two modes: read the mode before the signal", "none", "CONTEXT/REGIME",
    "The market is in trend mode or range mode; trend tools (averages, crosses, trend lines, breakouts) fail in a range, so classify the mode first. Averages lag: they confirm, they do not predict, and whipsaw in chop.",
    "no numbers", "OURS", "RNG-02;RNG-09;MAV-24;MAV-03;MAV-22;TRL-25", "n/a", "PARTIAL", "READY",
    "classifier thresholds (flat slope, braid, volume decline) are all OURS")
add("KR-T07", "Range tell: flat tangled averages plus shrinking volume", "none", "INDICATOR",
    "Flat, tangled moving averages together with falling volume signal that a sideways box (a coil) is starting.",
    "no numbers", "OURS", "RNG-03;MAV-24;VOL-24", "n/a", "PARTIAL", "READY", "slope, braid and volume-decline thresholds are OURS")
add("KR-T08", "Timeframe scope of the layer", "none", "PROCESS",
    "Live on the daily; the lowest he would go is 4h or 6h; weekly above; for 24/7 markets 2d and 3d are underrated; below 4h is noise, fees and stress.",
    "tf set = 1w, 1d, 6h, 4h (2d, 3d optional)", "SOURCED", "TFR-09;TFR-12;TFR-06;TFR-20;CAN-05", "n/a", "MECHANICAL", "READY",
    "scope rule: no sub-4h signal belongs to this layer (tension with MTS intraday layers, conflict C8)")
# ---- Z: zones
add("KR-Z01", "A level is a zone: wick extreme to close", "both", "LEVEL",
    "A support or resistance zone spans from the wick extreme to the close of the same pivot candle; price remembers areas, not exact numbers.",
    "zone = [close, wick extreme] of the pivot candle", "SOURCED", "SNR-01;SNR-02;SNR-04;RNG-01", "yes (support and resistance)", "MECHANICAL", "READY",
    "which candle is the pivot: see KR-Z05 and KR-L01")
add("KR-Z02", "A zone needs at least two turns", "both", "LEVEL",
    "One touch is an event, two is a memory: mark a zone only where price turned at least twice (heavy volume lets you mark earlier).",
    "min_turns=2", "SOURCED", "SNR-06", "yes", "MECHANICAL", "READY", "size of a 'turn' (reaction) is not given (SNR gap t=00:07:24): OURS minimum reaction")
add("KR-Z03", "Three to five zones, ranked", "both", "PROCESS",
    "Keep at most 3 to 5 zones; more only confuses; start from the daily and weekly; rank by timeframe, heavy volume and obviousness.",
    "max_zones=5 (3-5)", "MIXED", "SNR-05;SNR-07;SNR-08;SNR-09", "n/a", "PARTIAL", "READY", "ranking weights are OURS")
add("KR-Z04", "Heavy-volume pivot zones outrank the rest", "both", "LEVEL",
    "A pivot bar on outsized volume (2x the 20-period average or more) is marked wick to close as a zone and outranks other zones; a swing on thin volume is noise that looks like structure; volume is the tiebreaker when picking anchors.",
    "vol_mult=2 (2-3 typical); volume SMA=20", "SOURCED", "SNR-08;VOL-11;VOL-14;VOL-15;VOL-16;TRL-10;SNR-06", "yes", "MECHANICAL", "READY",
    "TRL-09 uses 'double or more the recent volume bars around' the pivot, bar count not given: OURS arm")
add("KR-Z05", "Pivot confirmation lag", "both", "PROCESS",
    "A local high or low is confirmed only when the next candle closes as a reversal (it can take one more candle); with heavy volume the pivot can be marked on that candle. Swings are found in hindsight and pulled forward.",
    "confirm_lag >= 1 bar", "SOURCED", "SNR-10;TRL-07", "yes", "MECHANICAL", "READY", "causality: no zone exists before its confirming close")
add("KR-Z06", "Zones and lines do not expire", "both", "LEVEL",
    "Pull zones and lines through the chart: they come back into contact with price, and volume-anchored ones are respected months or years later.",
    "no expiry stated", "NONE", "SNR-10;TRL-20", "yes", "MECHANICAL", "READY", "optional OURS arm: maximum age")
add("KR-Z07", "A break is a close beyond the outer boundary", "both", "ENTRY-TRIGGER",
    "A zone is broken only by a candle CLOSE above the wick high of a resistance zone or below the wick low of a support zone; an intrabar poke that snaps back is a stop harvest, not a break.",
    "close beyond outer boundary", "SOURCED", "SNR-12;SNR-22;RNG-15;RNG-19;RNG-20;VOL-17;VOL-22;TRL-23;TRL-24;CAN-20", "yes", "MECHANICAL", "READY",
    "which timeframe's close counts is not stated (SNR gap t=00:28:40): OURS = the zone's own timeframe")
add("KR-Z08", "Inside an unbroken zone: fade or stay out", "both", "ENTRY-TRIGGER",
    "While a resistance zone is unbroken, price inside it can be scalped short or simply not bought; the support mirror: buy dips while no close below. Play both sides.",
    "no numbers", "NONE", "SNR-13;RNG-06;TRL-12;RNG-09", "yes", "PARTIAL", "READY",
    "event is buildable; entry price, stop, target, size and the length of a 'scalp' are not given: OURS arms")
add("KR-Z09", "Role flip", "both", "LEVEL",
    "A broken floor becomes a ceiling and a broken ceiling becomes a floor; same zone, same people, opposite job; a broken level is a selling or buying area, not binary.",
    "no numbers", "NONE", "SNR-14;TRL-19;RNG-14;TRL-15", "yes", "MECHANICAL", "READY", "none")
add("KR-Z10", "Break, wait, retest routine", "both", "ENTRY-TRIGGER",
    "Step 1 a candle closes through the zone (a wick does not count); step 2 do nothing, do not chase; step 3 price comes back from the other side: if the zone holds the break was real, if price slices back through it was a harvest and you stand down.",
    "no numbers", "NONE", "SNR-15;VOL-23;RNG-20", "yes", "PARTIAL", "READY",
    "'holds' is not defined and entries, stops and targets were deferred to a later video: OURS arms; in tension with KR-Z11 (conflict C2)")
add("KR-Z11", "A retest is not required", "both", "ENTRY-TRIGGER",
    "The best breakouts do not retest; a retest is not mandatory, but if one comes it must hold.",
    "no numbers", "NONE", "RNG-21", "yes", "PARTIAL", "READY", "second arm against KR-Z10 (conflict C2)")
add("KR-Z12", "Round numbers act as levels", "both", "LEVEL",
    "Round numbers (100,000 on Bitcoin and similar) act as support and resistance with no price history; price overshoots or undershoots them; trade the area, not the exact print.",
    "'within a few percent' (he says he does not know)", "NONE", "SNR-16;SNR-17", "yes", "PARTIAL", "BLOCKED",
    "tolerance is vague and he cannot say why it works; low priority, revisit after the core arms")
add("KR-Z13", "Every touch weakens a level", "both", "CONTEXT/REGIME",
    "Contrary to the common view, a level tested more often is weaker because each test eats resting orders: the first test bounces most; beyond three tests the break probability is much higher; four to six tests = mature.",
    "tests_threshold=3 (4-6 mature)", "SOURCED", "SNR-18;SNR-19", "yes", "MECHANICAL", "READY", "conflict C1 with KR-L02 (touches validate a line)")
add("KR-Z14", "Stops are harvested beside obvious levels", "both", "EXIT/STOP",
    "Under every obvious floor sits a pile of stops; do not place a stop just below the level or the last low; keep stops away from the obvious price; the zone resolves only on a close beyond its wick boundary.",
    "distance never given", "NONE", "SNR-20;SNR-21", "yes", "PARTIAL", "BLOCKED", "no stop distance anywhere in episodes 1-7; wait for the pending videos, else OURS")
add("KR-Z15", "A defended level bounces", "both", "LEVEL",
    "Two hammers (several wicks) at the same level mean it was defended twice, so a bounce is likely; the same candle floating in chop is noise: location beats shape.",
    "count of wicks into a zone; no number beyond 'twice'", "SOURCED", "CAN-21;CAN-22;SNR-11;RNG-18", "yes", "MECHANICAL", "READY", "none")
add("KR-Z16", "Confluence: static zone plus rising average", "both", "LEVEL",
    "When a horizontal zone and a major moving average (the 55 EMA, the 200) meet at the same place at the same time, that is confluence and a stronger area.",
    "tolerance not given", "OURS", "MAV-15;MAV-14", "yes", "PARTIAL", "READY", "touch tolerance is OURS")
# ---- L: swings and trend lines
add("KR-L01", "Anchors only on confirmed swings", "both", "LEVEL",
    "A swing low is a low with higher lows on both sides, a swing high the mirror; trend lines and zones are anchored only on swings; seeing them on a line chart (closes) makes them obvious.",
    "bars on each side not given", "OURS", "TRL-04;TRL-05;TRL-06;TRL-07", "yes", "MECHANICAL", "READY", "k (bars each side) is OURS; arm: swings on closes versus highs and lows")
add("KR-L02", "Two points are a hypothesis, three touches a trend", "both", "PATTERN",
    "A line through two points is a hypothesis; three touches make a trend; the market respecting the line without you touching it is the good sign.",
    "touches=3", "SOURCED", "TRL-08", "n/a", "MECHANICAL", "READY", "conflict C1 with KR-Z13")
add("KR-L03", "Two touches are enough on heavy volume", "both", "PATTERN",
    "Two touches may be drawn early if both turning points carry heavy volume, meaning double or more the recent volume bars around them; such lines carry weight for a long time.",
    "touches=2; vol_mult=2 vs recent bars (count not given)", "MIXED", "TRL-09;TRL-10", "n/a", "MECHANICAL", "READY", "number of recent bars is OURS")
add("KR-L04", "Reaction at a volume-anchored line", "both", "ENTRY-TRIGGER",
    "When price first returns to a line drawn between two high-volume pivots, expect a reaction, at least a bounce and maybe a reversal; the first pass usually gives a decent scalp, not a home run; do not hold it forever.",
    "no numbers", "NONE", "TRL-11;TRL-12", "yes", "PARTIAL", "READY", "event study only; stop, target and hold time are not given: OURS arms")
add("KR-L05", "No bent-to-fit lines", "both", "PROCESS",
    "A line that slices through candles to hit a wanted price is bent to fit and must break; no regression lines; one honest line beats ten hopeful ones.",
    "no numbers", "OURS", "TRL-13;TRL-03;TRL-21", "n/a", "PARTIAL", "READY", "'slices through' needs a tolerance: OURS")
add("KR-L06", "A line break is new information", "both", "PATTERN",
    "A real break gives real follow-through, a phantom line snaps back; the broken line changes jobs and can base higher lows.",
    "no numbers", "NONE", "TRL-14;TRL-15;TRL-19", "yes", "PARTIAL", "READY", "follow-through size is not given")
add("KR-L07", "Steepness is a countdown", "both", "CONTEXT/REGIME",
    "The steeper the line the shorter the trend; sustainable trends climb like a staircase (he names 4 to 5 degrees); the way up is the way down.",
    "4-5 degrees, no chart scale", "SOURCED", "TRL-16;TRL-17", "yes", "PARTIAL", "BLOCKED", "degrees depend on chart scaling: unusable until normalised; hypothesis only")
add("KR-L08", "Horizontal levels matter more than diagonals", "both", "LEVEL",
    "Horizontal levels are the most important; the most violent moves happen at horizontal levels; important highs and lows are always also marked with a horizontal bar.",
    "no numbers", "NONE", "TRL-18;TRL-22;TRL-25", "n/a", "MECHANICAL", "READY", "priority weight: zones before diagonal lines")
add("KR-L09", "Trend change needs a close", "both", "CONTEXT/REGIME",
    "A downtrend reversal is confirmed only by a close above the horizontal line of the last lower high; an uptrend is intact while major higher lows hold and breaks on a close below the wick low of a major higher low.",
    "close beyond last lower high / wick low of higher low", "SOURCED", "TRL-23;TRL-24", "yes", "MECHANICAL", "READY", "none")
# ---- V: volume
add("KR-V01", "Volume yardstick: 20-period simple average", "none", "INDICATOR",
    "Put a simple moving average with a 20-period lookback on the volume bars; it answers whether a bar is big, average or nothing; bars are shown grey (colour-agnostic).",
    "SMA length=20", "SOURCED", "VOL-07;VOL-06;MAV-02", "n/a", "MECHANICAL", "READY", "none")
add("KR-V02", "Outsized volume = 2x the average or more", "none", "INDICATOR",
    "Volume matters when it is two or more times the average (two to three times typical, 'depends on the market'); small bars do not matter.",
    "vol_mult=2 (2-3)", "SOURCED", "VOL-09;VOL-10;TRL-09;TRL-10;SNR-08", "n/a", "MECHANICAL", "READY",
    "conflict C5: plain relative volume is a clock for BTC (LESSONS_DIGEST); test his plain SMA20 arm AND a same-slot baseline arm")
add("KR-V03", "Major pivots come on outsized volume", "both", "PATTERN",
    "Macro and major highs and lows (almost always lows; highs on parabolic blow-offs, not all tops) come on significantly outsized volume; a loud pivot is structure.",
    "examples: 2x, 3-3.5x average (his charts)", "SOURCED", "VOL-08;VOL-13;VOL-25;VOL-20;SNR-08", "yes", "MECHANICAL", "READY", "hypothesis H-V1: a claim to test, not a given")
add("KR-V04", "Volume confirms or condemns a signal", "none", "CONTEXT/REGIME",
    "Volume does not create a signal, it confirms or condemns it: a hammer on outsized volume is a signal, on thin volume wallpaper; a level born on big volume is real memory.",
    "no numbers beyond KR-V02", "NONE", "VOL-11;CAN-22;SNR-08;RNG-18", "n/a", "MECHANICAL", "READY", "used as a filter on other rules")
add("KR-V05", "A breakout needs fuel", "both", "ENTRY-TRIGGER",
    "A real break of a real zone comes with volume expanding as price escapes; a break without volume is bait for a stop hunt; stop hunts are quiet.",
    "'bigger than the average in a discernible way'", "MIXED", "VOL-12;VOL-17;VOL-22;RNG-20;RNG-23", "yes", "PARTIAL", "READY", "threshold between 1x and 2x is OURS")
add("KR-V06", "Effort versus result", "both", "PATTERN",
    "Huge volume with a tiny candle = absorption (at resistance price likely turns back, at support selling is absorbed then bounces); a huge candle on no volume is hollow and ripe for a fake-out.",
    "no numbers", "OURS", "VOL-18;VOL-19", "yes", "PARTIAL", "READY", "'tiny' and 'huge' candle thresholds are OURS; one video only")
add("KR-V07", "Capitulation hammer", "long", "PATTERN",
    "After a long downtrend a mega candle with a huge lower wick and a strong close on the biggest volume bar of the chart can mark capitulation and a macro low.",
    "'biggest volume bar on the chart'; 'strong close' not quantified", "OURS", "VOL-20;CAN-13", "no (highs: blow-off tops, not all)", "PARTIAL", "READY", "lookback for 'biggest' and 'long downtrend' are OURS; rare event: power")
add("KR-V08", "Apathy versus panic", "both", "CONTEXT/REGIME",
    "A drift to a low on no volume is apathy, not panic, and is rarely finished; panic ends trends, apathy only pauses them.",
    "no numbers", "OURS", "VOL-21", "yes", "PARTIAL", "READY", "one video only")
add("KR-V09", "The coil: a range on declining volume", "none", "PATTERN",
    "A range whose volume keeps falling (each bounce quieter, the wedge tighter) is maturing like a compressed spring; falling volume says a big move is loading, not which way.",
    "no numbers", "OURS", "VOL-24;RNG-10;RNG-03;MAV-24", "n/a", "PARTIAL", "READY", "volume-slope and tightness thresholds are OURS")
add("KR-V10", "Volume near half its average before a breakout", "none", "INDICATOR",
    "In his weekly Bitcoin examples volume fell to roughly 50 % of its average right before the breakout; he says it is not necessarily a rule, but once volume is that low the breakout odds are much higher; low volume is the best timing factor.",
    "0.5 x average (observation, not a rule)", "SOURCED", "RNG-13;RNG-24", "n/a", "MECHANICAL", "READY", "hypothesis H-R2; one video only")
add("KR-V11", "Read volume on major venues", "none", "PROCESS",
    "Crypto volume can be faked: read it on major venues (Coinbase, the TradingView index, CME); be aware of coin versus dollar volume in long history.",
    "no numbers", "NONE", "VOL-04;VOL-05", "n/a", "NOT_TA", "BLOCKED", "data decision (conflict C6): our feed is Binance klines; need a Coinbase or index volume series, or accept a wash-trade caveat in PRE_REG item 4")
# ---- C: candles
add("KR-C01", "Candle definitions", "none", "INDICATOR",
    "A candle has open, high, low and close; colour is only close versus open and is not conclusive; the body is open to close and a wick is anything outside it; a candle is a block of time.",
    "no numbers", "SOURCED", "CAN-02;CAN-03;CAN-04;CAN-07", "n/a", "MECHANICAL", "READY", "definitions only")
add("KR-C02", "A wick is a failed move; size is rejection", "both", "PATTERN",
    "A long wick under a candle means buyers took everything thrown at it (rejection, price typically tries higher); every wick is a failed move; bigger wick, bigger rejection; only big wicks with a reversal close have an edge.",
    "'big' wick not quantified", "OURS", "CAN-08;CAN-09;CAN-13", "yes", "PARTIAL", "READY", "wick-to-range ratio is OURS")
add("KR-C03", "Hammer", "long", "PATTERN",
    "A candle with a long lower wick that closes strong (green) at the exact low of the move (nothing lower to the left or right); price likely tries up and closes positive over the next three to five candles.",
    "horizon 3-5 candles; wick ratio not given", "MIXED", "CAN-10;CAN-12;VOL-20;RNG-18;SNR-11", "yes (KR-C04)", "PARTIAL", "READY", "wick ratio and 'exact low' lookback are OURS")
add("KR-C04", "Shooting star", "short", "PATTERN",
    "The mirror of the hammer: a long upper wick at the top of a trend after a new high that closes down, nothing higher to the left; the next three to five candles likely negative.",
    "horizon 3-5 candles; wick ratio not given", "MIXED", "CAN-11;CAN-12;VOL-13;SNR-11", "stated", "PARTIAL", "READY", "same OURS parameters as KR-C03")
add("KR-C05", "Full-body candle shows conviction", "both", "PATTERN",
    "A candle with no major wick signals conviction: green probably goes up from there, red down.",
    "no numbers", "OURS", "CAN-14", "yes", "PARTIAL", "READY", "one video only; wick fraction is OURS")
add("KR-C06", "Engulfing, his strict definition", "both", "PATTERN",
    "Bullish engulfing: the candle trades below the prior low AND closes above the prior HIGH; bearish: trades above the prior high AND closes below the prior low; the looser textbook version has no edge in his view. He has used this for about 15 years.",
    "both conditions required", "SOURCED", "CAN-16;CAN-17;RNG-18", "stated", "MECHANICAL", "READY", "check whether earlier candle studies (CANDLE-P1) used this strict form before reusing their verdict")
add("KR-C07", "Doji and its confirmation", "both", "PATTERN",
    "A doji is a bodyless (very small body) candle, a weak indecision signal; the reversal is confirmed by the first candle that closes above its high or below its low.",
    "body ratio not given", "OURS", "CAN-18;CAN-19;SNR-11", "stated", "PARTIAL", "READY", "body ratio is OURS")
add("KR-C08", "Trade the confirmation, not the first candle", "both", "ENTRY-TRIGGER",
    "For hammer, shooting star, engulfing and doji wait for a close in the same direction beyond the pattern's wick high or low; better than trading the first candle.",
    "close beyond pattern wick", "SOURCED", "CAN-20;CAN-19", "stated", "MECHANICAL", "READY", "none")
add("KR-C09", "Only four patterns", "none", "PROCESS",
    "Only hammer, shooting star, engulfing and doji matter; engulfing are the best, doji the least; other named patterns lack the edge to trade.",
    "4 patterns", "SOURCED", "CAN-15;CAN-24", "n/a", "MECHANICAL", "READY", "scope rule")
add("KR-C10", "Pattern counts only at a level, ideally on volume", "both", "CONTEXT/REGIME",
    "Patterns aligned with horizontal support or resistance are far more powerful and volume adds conviction; the same candle floating in chop fades.",
    "no numbers beyond KR-V02", "NONE", "CAN-21;CAN-22;VOL-11;SNR-11;RNG-18", "yes", "MECHANICAL", "READY", "hypothesis H-C1")
# ---- M: moving averages
add("KR-M01", "Starter set: 21 EMA, 55 EMA, 200 SMA", "none", "INDICATOR",
    "Use the 21 EMA, the 55 EMA and the 200 SMA on any timeframe (period = memory: on the daily about a month, a quarter, most of a year); pick lines and keep them; each timeframe has its own line, higher timeframe = more powerful.",
    "EMA 21, EMA 55, SMA 200; his live stack also 5 EMA and '377' EMA (caption inference)", "SOURCED", "MAV-07;MAV-09;MAV-06;MAV-10;RNG-17", "n/a", "MECHANICAL", "READY", "377 is a caption inference and stays unverified")
add("KR-M02", "Silver Cross: 21 versus 55 EMA", "both", "ENTRY-TRIGGER",
    "A 21 EMA cross of the 55 EMA marks the short and medium trend turning; strongest with the 200 SMA: below the 200 plus a down-cross preceded the big drops, a cross plus a reclaim of the 200 was the reversal; crosses fail in chop, so match with trend and structure.",
    "21/55 EMA cross; 200 SMA side", "SOURCED", "MAV-11;MAV-12;MAV-23;MAV-22;RNG-17", "stated", "MECHANICAL", "READY", "supplies SOURCED numbers for the daily-MA layer that was NO-SOURCE; no stop or target given")
add("KR-M03", "The 200 SMA reacts on first contact", "both", "LEVEL",
    "Price almost always reacts when it first touches the 200 SMA after a long time away, on almost any timeframe; in an uptrend with the 21 below the 55 but price above the 200, corrections around the 200 are a bounce area for a scalp.",
    "'a long time' not defined", "OURS", "MAV-08;MAV-13;MAV-25", "yes", "MECHANICAL", "READY", "hypothesis H-M1; 'long time away' is OURS; one video only")
add("KR-M04", "The 200-week SMA", "long", "LEVEL",
    "The weekly 200 SMA is about four years of price; Bitcoin's lows in 2015, 2018, 2020 and 2022 were called by it; buys at or below it were valuable long term (his claim: 26 years, 6 assets, 80 touches).",
    "200 SMA on 1w", "SOURCED", "MAV-16", "no", "MECHANICAL", "READY", "hypothesis H-M2; few touches, descriptive only; his back-test is a claim (conflict C7)")
add("KR-M05", "21 and 55 EMA as dynamic support", "long", "LEVEL",
    "In uptrends the 55 EMA and the 21 EMA act as dynamic support (buy between the two lines); a rising 55 EMA is a support zone walking uphill; the space between the lines is a zone.",
    "band between EMA 21 and EMA 55", "SOURCED", "MAV-13;MAV-14", "n/a", "MECHANICAL", "READY", "one video only; no stop or target")
add("KR-M06", "The leash: disconnect from the 5 EMA", "both", "PATTERN",
    "When the whole candle floats above a very short average (the low does not touch the 5 EMA) that is a disconnect; price usually reconnects; three closes without touching means you are late, not early; basing near the 5 EMA is expected on short pullbacks.",
    "5 EMA; disconnect = candle low above EMA; late at about 3 closes", "SOURCED", "MAV-17;MAV-18;MAV-19", "n/a", "MECHANICAL", "READY",
    "hypothesis H-M3: his statistics (5,284 candles, 476 disconnects, median 1 close, 82 % reconnect within 2, longest 7) are claims to recompute; one video only")
add("KR-M07", "Golden and death cross, slope of the 200", "both", "CONTEXT/REGIME",
    "The 50 SMA above the 200 SMA is a golden cross (long-term upside, not short-term), below is a death cross; a death cross while the 200's slope is still up is ignored; with the 200 sloping down it starts the long-term downtrend (sell rallies toward the 200).",
    "SMA 50 vs SMA 200; slope of 200", "MIXED", "MAV-20;MAV-21;MAV-22", "stated", "MECHANICAL", "READY", "slope threshold is OURS; one video only")
add("KR-M08", "SMA versus EMA", "none", "INDICATOR",
    "The EMA weights recent closes more: it turns faster and is faked out faster; both have a place, EMA is his favourite.",
    "no numbers", "NONE", "MAV-05", "n/a", "MECHANICAL", "READY", "arm: SMA versus EMA variants (OURS)")
# ---- R: range, coil, breakout
add("KR-R01", "Range: trade the edges or stay flat", "both", "ENTRY-TRIGGER",
    "A range is two zones (floor and ceiling, drawn wick to close) with price stuck between; only the floor and the ceiling have an edge; the middle is no man's land (no memory, no edge, fees); trade the edges or stay flat; scalp the boundaries, never use a trend strategy inside.",
    "no numbers", "NONE", "RNG-01;RNG-06;RNG-07;RNG-08;RNG-09;TRL-25;SNR-13", "yes", "PARTIAL", "READY", "middle-of-range exclusion is a clean filter; entries and exits OURS")
add("KR-R02", "Edge entry and the fake-out", "both", "ENTRY-TRIGGER",
    "At the floor wait for the test and demand proof (hammer or engulfing, ideally on volume); the ceiling is the mirror; a quick poke beyond the edge that snaps back is the signature fake-out: act only on the close back inside with proof.",
    "no numbers", "NONE", "RNG-18;RNG-19;SNR-22;VOL-22", "yes", "PARTIAL", "READY", "stop and target not given")
add("KR-R03", "Coil: declining volume and tightening wedge", "none", "PATTERN",
    "A range on declining volume, each bounce quieter, is a coil (a symmetrical triangle when both sides tighten); the break odds rise as volume tails off to near nothing; the coil itself gives no direction.",
    "no numbers", "OURS", "RNG-10;RNG-11;VOL-24;MAV-24", "n/a", "PARTIAL", "READY", "same thresholds as KR-V09")
add("KR-R04", "Longer and tighter means a bigger breakout", "none", "CONTEXT/REGIME",
    "The longer and tighter price consolidates the bigger the breakout (spring analogy); he says 'damn close' to always and never says always.",
    "'longer', 'tighter' undefined", "OURS", "RNG-12;RNG-10;RNG-25", "n/a", "PARTIAL", "READY", "hypothesis H-R1; one video only; magnitude not direction")
add("KR-R05", "Bias from the structure inside the range", "both", "CONTEXT/REGIME",
    "Same lows with lower highs = sellers more aggressive, down is likely; same highs with higher lows = buyers stronger, up is likely; moving-average posture helps the bias but is not confirmation; only the close resolves it.",
    "no numbers", "OURS", "RNG-16;RNG-17;RNG-23", "stated", "PARTIAL", "READY", "one video only")
add("KR-R06", "Breakout checklist: close, fuel, retest", "both", "ENTRY-TRIGGER",
    "A real resolution has (1) a close through the zone not a wick, (2) volume expansion, (3) a retest that holds if one comes; no full-on confirmation, no trade; stacking the checks raises the probability but never to 100 %.",
    "close; volume above average; retest optional", "MIXED", "RNG-20;RNG-21;RNG-15;VOL-22;VOL-23;SNR-15", "yes", "PARTIAL", "READY", "composite of KR-Z07, KR-V05, KR-Z10/Z11")
add("KR-R07", "Range height projects the first leg", "both", "EXIT/STOP",
    "Measure the range from bottom to top and project that height from the breakout trigger as the first area of interest; a heuristic, not a law.",
    "target = range height from breakout", "SOURCED", "RNG-22", "stated", "MECHANICAL", "READY", "the only target in episodes 1-7; no stop is given with it")
add("KR-R08", "Every trend is born in a box", "none", "MENTAL-MODEL",
    "Zoomed out price moves like stairs: long sideways boxes, then a step; the range is where positioning happens and the trend is the outcome; ranges resolve on no schedule.",
    "no numbers", "NONE", "RNG-25;RNG-05;RNG-24", "n/a", "NOT_TA", "REJECT", "framing; the actionable part (volume tail-off as timing) is KR-V10")
# ---- X: risk and execution
add("KR-X01", "Manage risk yourself, exit on the close", "both", "EXIT/STOP",
    "He prefers not to leave a resting stop: he manages risk himself and exits when the zone breaks on a close, taking the small loss; good risk management means a high win rate is not needed.",
    "no numbers (70 % win rate only as an illustration)", "NONE", "SNR-21;SNR-20", "yes", "PARTIAL", "BLOCKED",
    "conflict C3: MTS requires a protective stop on every live position; backtest only as a close-based exit plus an OURS hard stop; operator ruling needed for anything live")
add("KR-X02", "Limit beats market for fees", "none", "PROCESS",
    "A limit (maker) order has the lowest commission, a limit priced through the best offer fills as a market order, a far limit may never fill.",
    "retail exchange fee figures only", "NONE", "FEE-05;FEE-06;FEE-07;FEE-08;FEE-09", "n/a", "NOT_TA", "REJECT", "retail DCA fees on one exchange; supports the existing maker model, adds no signal")
add("KR-X03", "Fund by bank transfer; referral discount", "none", "PROCESS",
    "Debit-card top-up costs about 4 %, bank transfer nothing; simple mode charges the most; his referral link gives a discount.",
    "4 %, 3.49 vs 0.24 per 100", "NONE", "FEE-02;FEE-03;FEE-04;FEE-01", "n/a", "NOT_TA", "REJECT", "referral promotion, not a trading rule")
# ---- F: framing and claims (not rules)
add("KR-F01", "Probabilities, not certainties; lag", "none", "MENTAL-MODEL",
    "Technical analysis gives probabilities; indicators confirm what price did and do not predict; anyone saying the line knows the future is selling something.",
    "none", "NONE", "TRL-01;MAV-03;MAV-04;CAN-03", "n/a", "NOT_TA", "REJECT", "framing")
add("KR-F02", "Levels exist because of regret", "none", "MENTAL-MODEL",
    "Trapped holders, regret and unfilled orders explain why levels exist.", "none", "NONE", "SNR-03", "n/a", "NOT_TA", "REJECT", "explanation, not a rule")
add("KR-F03", "Follow the big players' footprint", "none", "MENTAL-MODEL",
    "Lines, zones and volume are footprints of big players; retail should read them and trade alongside.", "none", "NONE", "TRL-02;CAN-26;VOL-13", "n/a", "NOT_TA", "REJECT", "framing")
add("KR-F04", "Volume is the lie detector", "none", "MENTAL-MODEL",
    "Volume is participation, the receipts behind the price story.", "none", "NONE", "VOL-01;VOL-02;VOL-03", "n/a", "NOT_TA", "REJECT", "framing; the operational parts are KR-V01 to KR-V05")
add("KR-F05", "Patterns are vocabulary, read pressure", "none", "MENTAL-MODEL",
    "Beginners memorise patterns; traders read who pushed and who fought back.", "none", "NONE", "CAN-23;CAN-01", "n/a", "NOT_TA", "REJECT", "framing")
add("KR-F06", "Moving average = the market's memory", "none", "MENTAL-MODEL",
    "A moving average is the market's memory drawn as a line that travels.", "none", "NONE", "MAV-01;MAV-14", "n/a", "NOT_TA", "REJECT", "framing")
add("KR-F07", "Panic ends trends, boredom builds them", "none", "MENTAL-MODEL",
    "The crowd leaves during the range and chases the trend; the box is the market loading.", "none", "NONE", "RNG-25;RNG-04", "n/a", "NOT_TA", "REJECT", "framing")
add("KR-F08", "His own statistics", "none", "RISK/SIZING",
    "5,284 daily candles, 476 disconnects, median 1 close, 82 % reconnect within 2, longest 7 closes (5 EMA, Bitcoin daily, 14+ years); a 200-week SMA back-test over 26 years, 6 assets, 80 touches; examples with 43 %, 27.5 %, 21.5 % moves.",
    "as stated", "NONE", "MAV-18;MAV-16;VOL-13;CAN-13", "n/a", "NOT_TA", "REJECT", "T3 claims without data or costs: REJECT as evidence (playbook Part I); kept as hypotheses H-M2, H-M3")
add("KR-F09", "'Almost always' claims", "none", "MENTAL-MODEL",
    "Statements such as 'almost always a reaction', 'damn close' to always, 'exponentially higher': not quantified.", "none", "NONE", "MAV-08;RNG-12;RNG-13;SNR-19", "n/a", "NOT_TA", "REJECT", "qualitative; each becomes a measured hypothesis")

# =====================================================================================================================
# BATCH 2 (2026-10-14): 7 more extracts (GDE guide, TRD trend, LVL levels, VJZ moving averages, RSI, KCM volatility, TOP tops).
# Existing rows gain sources (more videos = fewer PROVISIONAL rows); new rows are added; a few fields are corrected.
# =====================================================================================================================
ext("KR-T02", "TRD-05;TRD-38;TRD-43")
ext("KR-T03", "TRD-39;TRD-40;TRD-41;TRD-43")
setf("KR-T03", 11, "'agree' is still not defined for timeframes, but KR-L10 now gives a sourced trend-state definition per timeframe (dominant highs and lows): use it; the 4h-with-daily example is TRD-39/TRD-40 (long case only stated)")
ext("KR-T05", "LVL-09;LVL-31;TRD-48")
ext("KR-T06", "KCM-19;KCM-52;KCM-77;VJZ-24;VJZ-37;VJZ-40;RSI-09;RSI-19;GDE-14;TRD-09")
ext("KR-T07", "KCM-17;VJZ-24;VJZ-45;RSI-18;RSI-28;RSI-29")
setf("KR-T07", 11, "three sourced tells now: flat/braided averages, shrinking volume, RSI hanging in 40-60, BBWP below about 25-35; thresholds for the first two are OURS")
ext("KR-T08", "LVL-19;TOP-37")
ext("KR-Z01", "LVL-05;LVL-06;LVL-07;LVL-10;LVL-16;LVL-27")
ext("KR-Z02", "LVL-27;LVL-30")
ext("KR-Z03", "LVL-01;LVL-08;LVL-17;LVL-25;LVL-30")
ext("KR-Z07", "LVL-12;LVL-13;LVL-18")
ext("KR-Z09", "LVL-24;VJZ-15;VJZ-47")
ext("KR-Z10", "LVL-26;LVL-28")
ext("KR-Z13", "LVL-29")
setf("KR-Z13", 11, "conflicts C1 with KR-L02 and C9: LVL-29 says more touches make a level matter more, not stronger, and the breakout response stronger (he calls the slide wording misleading)")
setf("KR-Z14", 11, "no stop distance beside a level anywhere; the only structural stop is the far side of the compression zone (KR-Q05); wait for the pending videos, else OURS")
ext("KR-Z16", "VJZ-51;KCM-59")
ext("KR-L01", "TRD-11;TRD-24;TRD-36;TRD-37")
ext("KR-L09", "TRD-16;TRD-18;TRD-22")
ext("KR-V01", "TOP-16")
setf("KR-V01", 5, "SMA length=20 (VOL-07); 30 or 60 in the tops video (TOP-16)")
ext("KR-V02", "TOP-05;TOP-17")
setf("KR-V02", 5, "vol_mult=2 (2-3) of the 20-period average (VOL-09) or of the 30-day average (TOP-05)")
setf("KR-V02", 11, "conflicts C5 (plain relative volume is a clock for BTC) and C10 (20 versus 30 versus 60 periods): test his plain 20, his 30-day, and a same-slot baseline")
ext("KR-V03", "TOP-06;TOP-12;TOP-17;TOP-07")
ext("KR-V09", "KCM-09;KCM-16;KCM-17;KCM-18;KCM-30")
ext("KR-C04", "TOP-04;TOP-21;TOP-23;TOP-27;KCM-70")
ext("KR-C06", "TOP-04;TOP-21;TOP-23")
setf("KR-C06", 11, "TOP-21: he refuses to call a near-engulfing a bearish engulfing (second video that holds the strict definition); check whether earlier candle studies used this form (conflict C4)")
ext("KR-C07", "TOP-24")
ext("KR-M01", "VJZ-18;VJZ-19;VJZ-21;VJZ-22;VJZ-31")
setf("KR-M01", 5, "EMA 21, EMA 55, SMA or EMA 200, EMA 5, EMA 377 (stated again in VJZ-21); 34 and 89 are named but not used by him")
setf("KR-M01", 11, "the 377 EMA is now stated explicitly in a second video (VJZ-21); no choice between 200 EMA and 200 SMA (VJZ-20)")
ext("KR-M02", "VJZ-26;VJZ-27;VJZ-35")
ext("KR-M03", "VJZ-20")
ext("KR-M05", "VJZ-15;VJZ-23;VJZ-47;VJZ-48;VJZ-49;VJZ-50;VJZ-51;KCM-59")
ext("KR-M08", "VJZ-08;VJZ-09")
ext("KR-R01", "KCM-27;KCM-56;RSI-30;VJZ-39")
ext("KR-R03", "KCM-09;KCM-17;KCM-18")
ext("KR-R04", "KCM-43")
ext("KR-R05", "KCM-22;KCM-64;TRD-33")
ext("KR-R06", "LVL-12;VJZ-38;KCM-31;KCM-53")
ext("KR-X01", "TRD-45;KCM-24;KCM-48")
setf("KR-X01", 11, "conflict C3: MTS requires a protective stop on every live position; he does give structural stops in KCM-66/67 (KR-Q05) but still no distance; backtest as close-based exit plus an OURS hard stop")
ext("KR-F01", "GDE-01;GDE-22;GDE-23;VJZ-16")
ext("KR-F08", "TRD-20;TRD-30;VJZ-27;KCM-29;LVL-01;TOP-12")
setf("KR-F08", 4, "5,284 daily candles, 476 disconnects, median 1 close, 82 % reconnect within 2, longest 7 closes (5 EMA, Bitcoin daily); a 200-week SMA back-test over 26 years, 6 assets, 80 touches; the dominant-high/low method 'keeps you on the right side more than 90 %, maybe 95 %' (TRD); the 21/55 cross 'more than 80 %, less than 95 %' on a daily (VJZ); compression 70 % of the time (KCM); 'less than 10 % of lines matter' (LVL); examples with 43 %, 27.5 %, 21.5 % moves.")
setf("KR-F08", 11, "T3 claims without data or costs: REJECT as evidence (playbook Part I); kept as hypotheses H-M2, H-M3, H-L1, H-Q1")

# ---- T09 order of work
add("KR-T09", "Order of work: trend, levels, volatility and momentum, indicators", "none", "PROCESS",
    "Order of work: (1) trend or range, (2) key levels = structure, (3) momentum and volatility, (4) indicators for confirmation. Before any indicator answer two questions: is the market trending or ranging, and where has price reacted before. Learn trend and structure without indicators first; indicators measure price with a formula, react and lag, and add context, not certainty; an indicator output is a yes or no.",
    "order of four steps; ranking trend > support/resistance > volatility > momentum", "SOURCED",
    "GDE-11;GDE-12;GDE-14;GDE-20;GDE-22;GDE-24;GDE-26;GDE-28;LVL-31;KCM-73;RSI-21;TRD-50", "n/a", "PARTIAL", "READY",
    "conflict C11: KCM-73 gives two different orders for structure and volatility inside the same video; the step order of GDE-26 is the one we use")
# ---- Z17, Z18 level context
add("KR-Z17", "Levels work with the trend", "both", "CONTEXT/REGIME",
    "Support works best in an uptrend and resistance in a downtrend; levels against the trend are weaker (shorting an uptrend support risks being run over); levels do not work in isolation but inside trend context; old support very commonly becomes new resistance.",
    "no numbers", "NONE", "LVL-22;LVL-23;LVL-24", "yes", "PARTIAL", "READY", "one video; 'weaker' is not measured")
add("KR-Z18", "Keep levels relevant: dominant only, look left, favour recent", "both", "PROCESS",
    "Mark only the dominant highs and lows (the absolute best ones); look left to confirm a level was respected before; favour recent touches and bounces; revisit and update levels as history grows; do not force levels; stick to one or two timeframes and add others later as filters.",
    "no numbers", "NONE", "LVL-17;LVL-19;LVL-20;LVL-21;LVL-27;LVL-30", "yes", "PARTIAL", "READY", "'recent' and how far left are not defined: OURS; one video")
# ---- L10-L12 trend state
add("KR-L10", "Trend state from dominant highs and lows", "both", "CONTEXT/REGIME",
    "Every market on every timeframe is always in one of three states: uptrend (higher highs and higher lows, price staying above the previous dominant higher low), downtrend (lower lows and lower highs, price below the dominant lower high) or a range (about the same highs and lows). A dominant low is the lowest low before price makes a new high within the trend; a dominant lower high is the most recent local high from which a new low was created and it moves with each new lower low. A reversal is confirmed only when price trades and CLOSES below the dominant higher low (uptrend) or reclaims the dominant lower high by closing above it (downtrend); a short-term counter-trend swing that does not take that level is just a range; one-bar jagged peaks are not highs or lows.",
    "state machine; close beyond the dominant level; no bar counts", "SOURCED",
    "TRD-04;TRD-07;TRD-08;TRD-09;TRD-14;TRD-15;TRD-16;TRD-17;TRD-18;TRD-19;TRD-20;TRD-21;TRD-22;TRD-24;TRD-25;TRD-26;TRD-27;TRD-28;TRD-29;TRD-32;GDE-17;GDE-18;GDE-19;TRL-23;TRL-24",
    "yes", "MECHANICAL", "READY",
    "which timeframe's close counts, any buffer, and the size of a 'one-bar peak' are not stated (TRD gaps): OURS; hypothesis H-L1 (his claim: right side 90-95 %)")
add("KR-L11", "Trade only with the trend: the trend filter", "both", "CONTEXT/REGIME",
    "Only trade in the direction of the current trend (the quickest way to raise the hit rate of almost any strategy); the higher-timeframe trend is the dominant one; if there is no trend in the needed direction there is no trade; do not fight the trend; every strategy of his starts with a trend filter. Moving averages can confirm the trend but structure defines it.",
    "no numbers (a 4h strategy referenced to the 12h or daily trend is the only example)", "NONE",
    "TRD-01;TRD-03;TRD-05;TRD-39;TRD-40;TRD-46;TRD-47;TRD-48;TRD-49;TRD-50;VJZ-33;RSI-21", "stated (long case TRD-40/47, short case VJZ-33)", "MECHANICAL", "READY",
    "the filter form is not given; use KR-L10; hypothesis H-T1")
add("KR-L12", "In a sideways range favour the previous trend", "both", "CONTEXT/REGIME",
    "In a sideways range consolidation favour the previous trend; the bias is for continuation (look for higher lows after an uptrend, lower highs after a downtrend); keep the trend until proven otherwise.",
    "no numbers", "NONE", "TRD-33;KCM-22;KCM-64;VJZ-34", "stated", "PARTIAL", "READY", "one to two videos")
# ---- M09-M13
add("KR-M09", "Pair rule: lower period above higher period", "both", "INDICATOR",
    "For any pair, the lower-period average above the higher-period one means that trend is probably up (5 versus 21 short term, 21 versus 55, 200 versus 377 very long term) and vice versa; higher periods carry more weight, lower periods respond faster.",
    "pairs 5/21, 21/55, 200/377", "SOURCED", "VJZ-29;VJZ-30;VJZ-26;VJZ-21", "stated", "MECHANICAL", "READY", "one video; no stop or target")
add("KR-M10", "Weekly 55 EMA bias", "both", "CONTEXT/REGIME",
    "On the weekly chart price above the 55 EMA is generally bullish and below it generally bearish (Bitcoin, most assets, not perfect); a reclaim that is given up within about two closes is a bull trap and downside is very likely; the average works as support in uptrends and resistance once broken.",
    "weekly EMA 55; 'two closes' as an example", "MIXED", "VJZ-12;VJZ-13;VJZ-14;VJZ-15", "stated", "MECHANICAL", "READY", "one video; hypothesis H-M4")
add("KR-M11", "Slope of an average = strength of the trend", "both", "INDICATOR",
    "The slope of a moving average correlates with the strength of the trend: nearly vertical = a strong trend emerging (a strong trend is likely to get more trend); flat or flattening = chopping sideways, do not trend trade; a death cross with the 200 still sloping up is ignored.",
    "no angle or threshold", "OURS", "VJZ-43;VJZ-44;VJZ-45;MAV-21;MAV-24", "stated", "PARTIAL", "READY", "slope measure and thresholds are OURS; hypothesis H-M4")
add("KR-M12", "Averages are filters, not entry signals", "both", "CONTEXT/REGIME",
    "Moving averages are a secondary confirmation tool, not entry signals and not predictive: going long or short at every cross will not work; they help avoid bad trades (do not short while they show an uptrend), keep you with the trend, and validate higher-probability trades; the power is in how they are used inside the strategy's context.",
    "no numbers", "NONE", "VJZ-01;VJZ-02;VJZ-03;VJZ-05;VJZ-10;VJZ-11;VJZ-33;VJZ-36;VJZ-40;MAV-12;MAV-03", "short case only stated for the filter", "MECHANICAL", "READY", "feeds KR-T03 and KR-L11")
add("KR-M13", "Range break with the averages", "both", "ENTRY-TRIGGER",
    "A range break is validated only by a close beyond the range edge with the moving averages confirming the same direction (averages turning up inside the range alert you early); a cross against the range without a range break is a range play, not a reversal: scalp the range if you do anything.",
    "close beyond the range edge", "SOURCED", "VJZ-38;VJZ-39", "upside case stated", "PARTIAL", "READY", "one video; no number of closes, stop, target or size")
# ---- C11
add("KR-C11", "Three black crows", "short", "PATTERN",
    "Three black crows is, in his loose description, three down bars from the high; on a higher timeframe usually disastrous; one of his reversal-candle forms for a top.",
    "3 down bars from the high", "MIXED", "TOP-04;TOP-20;TOP-23", "n/a", "PARTIAL", "READY", "he is unsure of the name; no body or wick definition; one video")
# ---- Q volatility
add("KR-Q01", "BBWP: definition and his settings", "none", "INDICATOR",
    "His preferred volatility indicator is the Bollinger Band Width Percentile (BBWP, 'The Caretaker' on TradingView): where today's band width ranks against the past. Settings he likes on Bitcoin for higher timeframes: basis moving average length 7, lookback 100; SMA or EMA basis are interchangeable; price source close; a longer lookback for slower settings (252 as a relaxed example); Bollinger Bands, ATR and percentiles are all fine tools.",
    "basis length=7; lookback=100 (252 relaxed); close", "MIXED", "KCM-10;KCM-11;KCM-37;KCM-38;KCM-62;KCM-78;TOP-14", "n/a", "MECHANICAL", "READY",
    "band multiplier and the exact percentile formula are not stated (OURS: 2 and share of the last N widths <= today's); the '5 period average' is a garbled caption (KCM-11); define it in FORMULAS.md before use")
add("KR-Q02", "BBWP thresholds", "none", "INDICATOR",
    "On Bitcoin high volatility is BBWP above 85 (timeframe dependent; expansion reads 80-85 and up; 100 is the extreme); low volatility is below about 25 (the setup says about 30, 35 or 25-35, especially falling from a high); a break is confirmed when volatility rises above the 50th percentile; a read near the 93rd means most of the move is seen.",
    "high>=85; expansion 80-85+; low<=25 (25-35 in the setup); confirm>50; 93 as an example", "SOURCED", "KCM-12;KCM-13;KCM-28;KCM-63;KCM-65;KCM-69;TOP-13;TOP-14", "n/a", "MECHANICAL", "READY",
    "conflict C13: 85 versus 80-85 and 25 versus 25-35 inside the same video; 'extremely' red/blue levels are not given")
add("KR-Q03", "Compression and expansion cycle", "none", "CONTEXT/REGIME",
    "Markets compress and expand in cycles; low volatility always precedes high volatility and every breakout is preceded by low volatility; markets compress about 70 % of the time and expand about 30 % ('not super scientific', maybe 80/20); low volatility can last far longer than high volatility (about a month and a half versus under a week on his chart; months versus at most a couple of weeks on higher timeframes).",
    "70/30 (maybe 80/20); no thresholds", "SOURCED", "KCM-09;KCM-18;KCM-20;KCM-26;KCM-29;KCM-30;KCM-41;KCM-72", "n/a", "MECHANICAL", "READY",
    "the shares and 'always' are T3 claims: hypothesis H-Q1")
add("KR-Q04", "Volatility is direction-neutral and times the move", "none", "CONTEXT/REGIME",
    "Volatility does not say up or down: the trend gives direction and volatility times when a move is worth acting on (the gas pedal); right trend and right momentum with bad timing still loses, 'even if you are early you are wrong'; indicators use the same settings in every regime, which is why the same signal works one day and fails the next.",
    "no numbers", "NONE", "KCM-01;KCM-02;KCM-04;KCM-07;KCM-51;KCM-74;GDE-11", "n/a", "PARTIAL", "READY", "priority order is contradictory in KCM-73 (conflict C11)")
add("KR-Q05", "Compression breakout setup (volatility)", "both", "ENTRY-TRIGGER",
    "Identify compression (BBWP below about 25-35, ideally falling from a high); take the bias from the previous trend; do not anticipate the expansion: wait for the first candle that breaks the range with volatility rising above the 50th percentile and the momentum oscillator agreeing; enter with defined risk and the stop on the opposite side of the compression zone (for an upside break a CLOSE below the bottom of the range); after the break the stop can move to the breakout area; take some or all profit as volatility peaks. His preferred variant enters inside the compression, near the edge on the side of the bias (a lower high in a downtrend range), so a wrong break costs little.",
    "BBWP<25-35; confirm>50; stop = far side of the compression zone (close beyond); exit at the BBWP peak (93 as an example)", "MIXED",
    "KCM-21;KCM-22;KCM-23;KCM-24;KCM-47;KCM-48;KCM-49;KCM-63;KCM-64;KCM-65;KCM-66;KCM-67;KCM-68;KCM-69;KCM-70;KCM-75", "stated (downtrend lower-high entry; upside breakout example)", "PARTIAL", "READY",
    "the first complete setup with a sourced stop and a sourced exit; still open: how a range is identified, stop distance beyond the structure, which oscillator, how 'volatility coming down' is defined; one video only; hypothesis H-Q2")
add("KR-Q06", "Volatility-based profit taking", "both", "EXIT/STOP",
    "Volatility tells when a move is mostly played out: very high volatility means the move is mostly or all done; once volatility loses its own moving average and comes down the move is basically over; a move that continues while volatility falls is a weakening trend; a reversal candle on high volatility is a reason to take profit; afterwards look for the next sideways range. Ideally enter when volatility is low and exit when it is high.",
    "BBWP >= 85-93 as examples; 'loses its moving average' undefined", "MIXED", "KCM-05;KCM-32;KCM-33;KCM-34;KCM-35;KCM-36;KCM-40;KCM-49;KCM-69;KCM-70;TOP-15", "n/a", "PARTIAL", "READY",
    "'coming down' has no definition (KCM gap t=00:15:10); hypothesis H-Q3")
add("KR-Q07", "The volatility trap", "both", "ENTRY-TRIGGER",
    "Do not enter after volatility has already expanded: chasing the breakout candle at the top, or shorting the bottom of an expansion, is the classic beginner loss; when an asset is hammered by news and YouTubers you are probably at the volatility peak; position during compression, not after expansion (breakout trading fails very often but can be made to work).",
    "no threshold of its own (use KR-Q02)", "NONE", "KCM-44;KCM-45;KCM-46;KCM-75;KCM-76", "stated", "MECHANICAL", "READY", "as a filter: no entry in the trend direction while BBWP is above the high threshold")
add("KR-Q08", "Indicators behave differently by volatility regime", "none", "CONTEXT/REGIME",
    "Low volatility: oscillators give constant false signals, breakouts fail and reverse quickly, averages lag and risk-reward compresses, volume dries up, the only real trades are scalps at the edges of the range. High volatility: oscillators stay pegged at extremes (the RSI stays high in an upside breakout) yet are more efficacious while volatility rises, averages act as dynamic support and resistance, risk-reward expands and volume confirms conviction. Indicators are not broken, they are used in the wrong regime.",
    "no numbers", "NONE", "KCM-51;KCM-52;KCM-53;KCM-54;KCM-55;KCM-57;KCM-58;KCM-59;KCM-60;KCM-61;KCM-77;RSI-06", "n/a", "PARTIAL", "READY", "becomes the regime strata of PRE_REG item 12")
add("KR-Q09", "Volatility and sizing", "none", "RISK/SIZING",
    "Rising volatility means wider stops, bigger ranges, larger position risk and faster drawdowns, so size down rather than up.",
    "no multiple, no ratio", "NONE", "KCM-39", "n/a", "PARTIAL", "READY", "OURS arm: size by volatility bucket; one video")
add("KR-Q10", "Volatility extremes mark major turning points", "both", "PATTERN",
    "High-volatility regimes mark major highs and major lows almost always; extreme volatility on a high timeframe means the move has gone parabolic and parabolas do not last; extreme volatility alone is only a warning (price can go higher: Bitcoin 2017 stayed at high volatility for months).",
    "BBWP 100 / above 85 as the warning", "SOURCED", "KCM-14;KCM-42;TOP-06;TOP-11;TOP-12;TOP-13;TOP-15", "yes", "MECHANICAL", "READY", "hypothesis H-Q3; descriptive on few events")
add("KR-Q11", "Options aside: buy premium when implied volatility is low", "none", "CONTEXT/REGIME",
    "When option premiums collapse a big move is loading; buy premium only when implied volatility is low, never when it is high.",
    "no threshold", "NONE", "KCM-71", "n/a", "NOT_TA", "REJECT", "options scope: see the options module (options/research); no spot signal")
# ---- S RSI and momentum
add("KR-S01", "RSI is momentum, not direction and not a trigger", "none", "CONTEXT/REGIME",
    "The RSI measures strength, not direction: the trend decides direction and the RSI says how hard price is pushing; it is a secondary confirmation tool, never a trigger; waiting for a cross of MACD or stochastic RSI and entering 'will not work'; analyse the trend first, then use the RSI to confirm momentum in that context; never use it in isolation; momentum becomes useful once trend and structure are clear.",
    "no numbers", "NONE", "RSI-01;RSI-04;RSI-06;RSI-20;RSI-21;RSI-41;RSI-42;GDE-12;GDE-13;VJZ-52;KCM-61", "n/a", "PARTIAL", "READY", "four videos: cluster OK")
add("KR-S02", "Overbought is momentum, not a sell signal", "both", "CONTEXT/REGIME",
    "Overbought is anything over 70; in a strong trend it is a feature, not a warning: the first move of an upside breakout is immediately overbought and the RSI can stay over 70 for weeks on a daily chart; selling or shorting there misses the move; weak uptrends see the RSI fall; the oversold side is the same for a strong downtrend.",
    "overbought > 70; RSI period not stated", "SOURCED", "RSI-02;RSI-07;RSI-08;RSI-10;RSI-11;RSI-12;RSI-13;RSI-14;RSI-15;RSI-16;RSI-33;KCM-57", "stated", "MECHANICAL", "READY",
    "RSI period and data source are never stated (OURS 14); the oversold number is not spoken")
add("KR-S03", "RSI zones by trend: 40 and 60", "both", "CONTEXT/REGIME",
    "In an uptrend the RSI generally stays above 40 (holding 40-80, higher lows around 40-50, highs around 70-80 or more); in a downtrend it generally stays below 60 (typically 20-60, highs around 60); an RSI hanging between 40 and 60 means a sideways, trendless range (the textbook band is 30-70, his own view 40-60): do not trend trade it; holding back above 60 means something else is emerging.",
    "uptrend 40-80; downtrend 20-60; range 40-60 (textbook 30-70)", "SOURCED", "RSI-09;RSI-17;RSI-18;RSI-19;RSI-24;RSI-25;RSI-26;RSI-27;RSI-28;RSI-29", "stated", "MECHANICAL", "READY",
    "conflict C12 (lows above 40 versus 40-50; 30-70 versus 40-60); RSI period not stated; the same 40/60 regime as the Malkan layer (rsi_levels): its tolerance study applies")
add("KR-S04", "RSI extremes and asymmetry", "both", "PATTERN",
    "An RSI in the teens or single digits very rarely happens and does not last (a read of 10 suggests an exaggerated move and a snapback); the market can stay overbought much longer than it stays oversold.",
    "RSI 10 as an example", "OURS", "RSI-26;RSI-31;RSI-32", "no", "PARTIAL", "READY", "one video; thresholds OURS")
add("KR-S05", "RSI divergences", "both", "PATTERN",
    "Divergence is the primary value of an oscillator: regular bullish = price makes a new low and the RSI a higher low (downtrend weakening, look for a bounce); hidden bullish = price higher low with an RSI lower low (uptrend continuation); bearish = price higher high with an RSI lower high (strength going down); hidden bearish = price lower high with an RSI higher high (downtrend continuation); at weekly or monthly tops it shows three, sometimes four drives, rarely two.",
    "no lookback, spacing or size; 3-4 drives at tops", "OURS", "RSI-34;RSI-35;RSI-36;RSI-37;RSI-38;RSI-39;TOP-08;TOP-28;TOP-31", "stated", "PARTIAL", "READY",
    "he misspoke the regular bearish description (RSI-38, INFERRED); conflict C14: the earlier RSI divergence study found no edge on any timeframe")
add("KR-S06", "RSI-confirmed breakout or breakdown", "both", "ENTRY-TRIGGER",
    "With the trend up and a range resolving, an RSI above 70 confirms the breakout and the next leg up; with the trend down (or a range breaking below the most recent support) and the RSI turning oversold it is a real reversal and more downside is expected; the RSI confirms, structure decides.",
    "RSI > 70 for the upside case", "MIXED", "RSI-13;RSI-22;RSI-23;RSI-40;KCM-65", "stated", "PARTIAL", "READY", "no entry order, stop or target; oversold number not spoken")
add("KR-S07", "MACD cross as the last top signal", "short", "INDICATOR",
    "A bearish MACD cross on a weekly or monthly chart (quarterly for assets with long history) is usually the last of the top signals; alone it is the least important and is ignored.",
    "weekly or monthly; settings not stated", "OURS", "TOP-08;TOP-29;TOP-30", "no", "MECHANICAL", "READY", "MACD settings are OURS (standard); one video")
# ---- P tops
add("KR-P01", "Four-signal major top (selling framework)", "long", "EXIT/STOP",
    "At a major or macro top he looks for four things working in unison around the same time: a reversal candle, extreme volume, extreme volatility and a momentum signal (bearish RSI divergence or a MACD cross), on weekly or monthly charts (a weekly for Bitcoin, a monthly for traditional markets). Three of four = at least a major top, high probability; all four = probably a macro top; sometimes two; any single signal alone means little. Not a short signal: it is when he sells part of a long-term holding.",
    "3 of 4 within 'a few bars'; weekly or monthly", "MIXED", "TOP-01;TOP-09;TOP-10;TOP-18;TOP-35;TOP-40", "no (a bottom version is not given)", "PARTIAL", "READY",
    "'a few bars' undefined; which 3 of 4 is open; no stop or target; H-P1 on Bitcoin weekly has only a handful of events: descriptive")
add("KR-P02", "Scale out, do not sell the exact top", "long", "RISK/SIZING",
    "Sell some, not necessarily all: as much as 80-85 % or as little as 20 % of the holding, set by the asset, how much is a core position, where it came from and what he wants to do with it; then trade around; the goal is to sell well, not the exact top; most signals confirm a bar or two after the actual high.",
    "20 % to 85 % of the holding; signals 1-2 bars after the high", "SOURCED", "TOP-02;TOP-03;TOP-36;TOP-39;TOP-41", "no", "PARTIAL", "READY", "the split is a per-holding judgement; OURS arms (e.g. 1/3 per extra signal)")
add("KR-P03", "Ranking and order of the top signals", "long", "PROCESS",
    "The reversal candle is the most important and usually first; volume and volatility are very important only for parabolic highs, not for indices that march up (there volume and volatility often decline into the high); bearish divergence is the nail in the coffin and usually comes last (the MACD almost always last).",
    "no numbers", "NONE", "TOP-07;TOP-09;TOP-18;TOP-29", "no", "PARTIAL", "READY", "one video")
add("KR-P04", "No early call", "long", "PROCESS",
    "Do not sell or short on volatility alone and not before the reversal; one bad candle is not a top; one signal alone is not enough; his own non-tops (defense names, home builders, Tesla) show how not to call it; a massive shooting star alone was 'not that helpful'.",
    "no numbers", "NONE", "TOP-11;TOP-12;TOP-25;TOP-26;TOP-27", "no", "PARTIAL", "READY", "filter on KR-P01")
add("KR-P05", "Bitcoin top examples", "long", "PATTERN",
    "Bitcoin 2017 (weekly): volatility was high for months (about May to December) while price marched up, so volatility alone was no signal; the top came at the highest volatility read with bearish divergence, extreme volume and a later MACD cross down. 2021: RSI lower highs, a shooting star and the MACD cross (three of four; volatility and volume did not stand out). Gold: three drives of divergence, extreme volatility and a weekly MACD cross a couple of bars after the high.",
    "no numbers", "NONE", "TOP-12;TOP-31;TOP-32;TOP-33;TOP-34", "no", "MECHANICAL", "READY", "dated examples for the recall check (PRE_REG item 3), to be verified against klines first")
add("KR-P06", "After all four signals: wait for a reset", "long", "PROCESS",
    "With all four signals, wait for them to reset: price usually takes a long time to correct such moves, it will happen again, but those moves hold for quite some time.",
    "no numbers", "NONE", "TOP-36;TOP-03", "no", "DISCRETIONARY", "BLOCKED", "'reset' and the time to reposition are not defined")
# ---- F additions
add("KR-F10", "Price is the output; TA says how, not why", "none", "MENTAL-MODEL",
    "Technical analysis studies price behaviour (supply, demand and human psychology); price is the final output of millions of decisions and the only thing that shows what people actually did; TA cannot say why; news and social media come last and are subjective; ignore the noise and focus on price.",
    "none", "NONE", "GDE-02;GDE-05;GDE-06;GDE-07;GDE-08;GDE-09;GDE-10", "n/a", "NOT_TA", "REJECT", "framing")
add("KR-F11", "Put it into a testable format, test, document, iterate", "none", "PROCESS",
    "After the four steps the idea is put into a testable format (the scientific method applied to trading), tested, the results documented and then either iterated or put into motion.",
    "no test length, sample or pass criterion", "NONE", "GDE-27", "n/a", "NOT_TA", "REJECT", "meta: this is our own protocol (PRE_REG_KROWN.md)")

# =====================================================================================================================
# BATCH 3 (2026-10-18): Foundations ep8 (ftK2BqggabQ, order book). Execution lesson, not a directional setup video.
# Krown explicitly rejects using the order book to pick direction (REJECT).
# =====================================================================================================================
add("KR-OBK01", "Maker vs taker fee gap", "none", "PROCESS",
    "A resting limit order adds liquidity and fills as a maker at lower fees (even placed 1 cent below the best bid); a market order crosses the spread, consumes liquidity, and fills as a taker at higher fees. Fee gap is an execution and cost input, not a directional setup.",
    'maker lower fees: "maker orders will incur significantly less fees than taker orders" (ftK2BqggabQ t=00:09:51); "even if you put it like 1 cent below the best bid, you are still a maker" (ftK2BqggabQ t=00:07:42)',
    "SOURCED", "OBK-06;OBK-07", "n/a", "MECHANICAL", "READY",
    "cost realism input only (gap-g7, dsa-audit-06); use exchange published fee tables, not affiliate figures (t=00:09:44); no directional signal")
add("KR-OBK02", "Healthy market has tight spread and deep book", "none", "CONTEXT/REGIME",
    "The spread is the gap between the highest bid and the lowest ask (to buy now pay ask, to sell now hit bid). A healthy market has an extremely small spread and a deep book that is cheap to cross; a wide spread represents a large friction tax on takers.",
    'tight spread / deep book: "extremely small between the best bid and the best ask" (ftK2BqggabQ t=00:03:40); "deep book, which is cheap to cross" (ftK2BqggabQ t=00:04:03); 1 cent spread example on BTC at 79,260 (t=00:03:55)',
    "SOURCED", "OBK-03;OBK-04", "n/a", "PARTIAL", "READY",
    "thresholds for tight spread and deep book are not defined; execution cost filter, not a directional rule")
add("KR-OBK03", "Market orders move price; resting orders cannot", "none", "MENTAL-MODEL",
    "Market orders never appear in the order book; they lift or hit resting orders, show up on the tape (recent trades), and are the only orders that move price. Limit orders cannot move the market; resting orders can be cancelled at any moment and are advertisement, not a promise.",
    'market orders move price: "Market orders never appear in the order books" (ftK2BqggabQ t=00:17:52); "A limit order cannot move price" (ftK2BqggabQ t=00:18:32); "Limit orders cannot move the market" (ftK2BqggabQ t=00:18:49)',
    "SOURCED", "OBK-10;OBK-13;OBK-05", "n/a", "NOT_TA", "READY",
    "market structure mental model; supports measuring taker flow (CVD/aggTrades); no order-book layer")
add("KR-OBK04", "Hidden size: iceberg, hidden orders, TWAP", "none", "PATTERN",
    "Large participants hide size using iceberg orders, straight hidden orders, split orders, or TWAP execution; the visible book stopping at a price with no liquidity beyond it is a tell, and real walls are typically invisible.",
    'hidden size: "You can do what\'s called iceberg orders or just straight up hidden orders" (ftK2BqggabQ t=00:19:06); "real walls typically are invisible" (ftK2BqggabQ t=00:19:29); "T-WP, you know, time weighted average price order" (ftK2BqggabQ t=00:25:35)',
    "SOURCED", "OBK-14", "n/a", "PARTIAL", "READY",
    "no quantitative detection algorithm or threshold given in extract; descriptive pattern of large player execution")
add("KR-OBK05", "Painting the book and spoofing", "none", "PATTERN",
    "Displayed depth is often manipulated by painting the book or spoofing: showing big size with no intent to get filled to bait other participants and algos, then pulling the orders before execution. Obvious outlier walls are typically spoofing or tricky orders.",
    'spoofing: "that\'s where you show big size that you never intend to get filled" (ftK2BqggabQ t=00:19:55); "Those are the ones to pay attention to because those are typically, you know, spoofing or tricky orders" (ftK2BqggabQ t=00:30:21)',
    "SOURCED", "OBK-12;OBK-21", "n/a", "PARTIAL", "READY",
    "no quantitative spoof detection rule; qualitative pattern; any wall idea needs its own PRE_REG with null expectation")
add("KR-OBK06", "Order book is a poor direction tool", "none", "MENTAL-MODEL",
    "The order book is one of the worst ways to pick market direction and staring at the book to predict moves is misleading; resting orders vanish with a click. The book is the worst compass to use but the best receipt for execution. Direction belongs to chart skills (episodes 1-7).",
    'REJECT for direction: "The order book is one of the worst ways to pick directions" (ftK2BqggabQ t=00:25:00); "anyone telling you they predict markets by staring at the book in my opinion is misleading you" (ftK2BqggabQ t=00:25:38); "worst compass to use but it is the best receipt" (ftK2BqggabQ t=00:31:03)',
    "SOURCED", "OBK-17;OBK-11;OBK-01", "n/a", "NOT_TA", "REJECT",
    "REJECT for directional trading: Krown explicitly rejects using order book depth or walls to predict direction; negative rule; no order-book layer")
add("KR-OBK07", "The 10-second pre-execution habit", "long", "PROCESS",
    "Three checks taking no more than 10 seconds before clicking buy: (1) look at spread and depth (avoid paying a silent tax on a wide spread), (2) when patient, prefer the limit order for lower maker fees, (3) respect size versus depth (an order big relative to resting depth moves price against you before filling).",
    '10-second habit: "three checks. It should take you no more than 10 seconds before you click buy" (ftK2BqggabQ t=00:28:13); "chew through all the order book until it fills that 10 Bitcoin" causing 30-40 dollar slippage illustration (ftK2BqggabQ t=00:27:10, t=00:27:23)',
    "SOURCED", "OBK-20;OBK-19", "yes (short execution mirror implied)", "DISCRETIONARY", "READY",
    "human pre-execution checklist; testnet orders are too small for size-vs-depth slippage; cost/slippage inputs map to gap-g7 and dsa-audit-06")


CONFLICTS = [
    ("C1", "KR-Z13 vs KR-L02", "More touches weaken a level, beyond three it breaks (SNR-18, SNR-19); three touches make a line a trend (TRL-08).",
     "Different objects (a horizontal level versus a trend line) but the same counting variable pulls opposite ways. Not resolved: test touch count against bounce size and break rate separately for levels and lines."),
    ("C2", "KR-Z10 vs KR-Z11", "Do not chase the break, wait for the retest (SNR-15, VOL-23) versus the best breakouts do not retest and a retest is not required (RNG-21).",
     "He addresses it himself in RNG-21 but gives no rule for when to enter. Not resolved: both are arms."),
    ("C3", "KR-X01 vs house rules", "He manages risk himself and exits on the close (SNR-21); MTS requires a protective stop on a live position (LESSONS_DIGEST s3, CLAUDE.md live-path rules).",
     "Not resolved. Backtest as a close-based exit plus an OURS hard stop; live use needs an operator ruling."),
    ("C4", "KR-C03..C07 vs earlier candle studies", "CANDLE-P0/P1/D19 found no edge on BTC and CANDLE-CLOSE-DEV was exploratory negative (layer_map.json).",
     "Unknown whether those studies used his strict engulfing definition or his 'exact low' location rule. Verify before reusing their verdicts."),
    ("C5", "KR-V02 vs LESSONS_DIGEST s2", "His rule is volume >= 2x the plain 20-period average; our lesson says plain relative volume is a clock for BTC and a same-slot baseline is required.",
     "Not resolved: SOURCED arm = his plain SMA20 x2, OURS arm = same-slot (hour or weekday) baseline x2; both in the trial ledger."),
    ("C6", "KR-V11 vs our data", "He reads volume on Coinbase, the TradingView index or CME because crypto volume can be faked; our feed is Binance klines.",
     "Not resolved: needs a data decision (PRE_REG item 4)."),
    ("C7", "KR-M04, KR-M06 claims vs our history", "His windows (14+ years daily, 26 years weekly) are longer than Binance history (spot from 2017).",
     "His statistics cannot be replicated in full; a recompute on 2017-2026 is descriptive and underpowered for the 200-week line."),
    ("C8", "KR-T08 vs MTS intraday layers", "He says anything below 4h is noise and the daily is where to live; Tom and Fabio layers run on 1m to 15m.",
     "Not a contradiction of evidence but a different home: the Krown layer is a swing layer; fee share of R is small, sample size per year is small."),
    ("C9", "KR-Z13 vs LVL-29 (KR-Z03 family)", "Every test eats resting orders, the first test bounces most and beyond three tests a break is much likelier (SNR-18, SNR-19) versus more touches make a level matter more, not stronger, and the breakout response stronger (LVL-29, where he says his slide wording was misleading).",
     "Both say touches do not make a level stronger; they differ on whether the level is more likely to break. Not resolved: test bounce size and break rate by touch index (H-Z1)."),
    ("C10", "KR-V01/V02 averages", "The volume yardstick is a 20-period simple average (VOL-07) in the volume video, a 30-day average with 60 as an alternative in the tops video (TOP-05, TOP-16, TOP-17); 'depends on the market' (VOL-09).",
     "Not resolved: test 20, 30 and 60, plain and same-slot (with C5)."),
    ("C11", "KR-T09, KR-Q04 priority order", "Trend first, then support/resistance, then volatility, then momentum (GDE-11) versus trend, then structure, then volatility (first statement in KCM-73) versus trend, then volatility, then structure (second statement in KCM-73, 'neck and neck').",
     "He contradicts himself inside KCM-73 and says it is not a priority list. Not resolved; the four-step order of GDE-26 (trend or range, levels, momentum and volatility, indicators) is used for the build."),
    ("C12", "KR-S03 RSI zones", "Uptrend RSI lows 'above 40' (RSI-17) versus 'lows 40 to 50' (RSI-24); range 30-70 (textbook, RSI-27) versus 40-60 (his view); downtrend 'below 60' versus 'holds 20-60'; no RSI period is ever stated.",
     "Not resolved: test 40/60 against 30/70 on the same bars (the Malkan 40/60 study exists), RSI(14) as OURS."),
    ("C13", "KR-Q02 BBWP thresholds", "High volatility above 85 (KCM-12, TOP-14) versus 'above 80 to 85' for expansion (KCM-28); low 'below about 25' (KCM-13) versus 'about 30, 35 or 25 to 35' (KCM-63); BBWP 'timeframe dependent'.",
     "Not resolved: grid {80,85,90} and {25,30,35}; every cell in the trial ledger."),
    ("C14", "KR-S05 vs earlier RSI study", "He calls divergence the primary value of the RSI (RSI-34, TOP-08); the repo's RSI-DIV-MTF study found no edge on any timeframe that reached 300 events (layer_map.json).",
     "Not resolved: his use is weekly/monthly tops (few events) and as confirmation in a trend context, which that study did not test; keep it descriptive."),
]

HYPOTHESES = [
    ("H-V1", "KR-V03", "Major swing pivots coincide with volume >= 2x SMA20 more often than non-pivot bars (lows more than highs).", "Pivot hit rate versus base rate; plain and same-slot baselines."),
    ("H-V2", "KR-V05, KR-R06", "Closes beyond a zone on expanding volume follow through more than closes on thin volume.", "Forward return and excursion after the break, volume split."),
    ("H-M1", "KR-M03", "The first touch of the 200 SMA after N days away reverses more often than other touches.", "N is OURS; reaction rate versus random touches."),
    ("H-M2", "KR-M04", "Weekly 200 SMA touches line up with macro lows.", "Descriptive on 2017-2026; few events."),
    ("H-M3", "KR-M06", "5 EMA daily leash: his counts and the 82 % reconnect figure recomputed on our data.", "Counts of candles, disconnects, median, share reconnecting within 2, maximum."),
    ("H-Z1", "KR-Z13", "Bounce size shrinks with touch index; break rate rises after 3 tests.", "Per touch index; levels from KR-Z01/Z02."),
    ("H-R1", "KR-R03, KR-R04, KR-V09", "Longer, tighter, lower-volume consolidation precedes a larger range expansion.", "Compression score versus subsequent range expansion (magnitude, not direction)."),
    ("H-R2", "KR-V10", "Breakouts begin when volume is near 50 % of its average.", "Volume ratio distribution before range breaks."),
    ("H-C1", "KR-C10, KR-Z15", "Hammer, shooting star and strict engulfing at a zone outperform the same patterns away from zones.", "Forward return at zone versus elsewhere, same window."),
    ("H-C2", "KR-C06", "His strict engulfing differs from the loose one.", "Forward return, both definitions, same bars."),
    ("H-T1", "KR-T03", "A weekly/daily agreement filter improves the net result of any lower-timeframe signal.", "Signal with and without the filter, fee-net."),
    ("H-Q1", "KR-Q03", "Breakouts are preceded by low BBWP (below 25-35) and markets spend about 70 % of the time compressed.", "Share of bars with BBWP below 25 / 35; BBWP state before each range break versus random bars."),
    ("H-Q2", "KR-Q05, KR-Q06", "His compression-breakout setup (stop on the far side of the range, exit as BBWP peaks) is profitable fee-net.", "Frozen rule from the spec, DEV only, both retest/entry arms, trade-through fills."),
    ("H-Q3", "KR-Q10, KR-Q06", "After BBWP above 85-93 most of the move is done (forward returns in the trend direction shrink or reverse).", "Forward return and excursion after BBWP crosses the grid, versus all bars."),
    ("H-L1", "KR-L10", "The dominant-high/low trend state keeps you on the right side of the trend more than 90 % of the time (his claim).", "Share of days where the state direction matches the forward N-day trend, versus a 21/55 EMA state; recomputed, not trusted."),
    ("H-S1", "KR-S03", "In uptrends the RSI holds above 40 and in downtrends below 60; 40-60 marks ranges.", "Coverage of RSI zones by L10 trend state; compare 40/60 with 30/70."),
    ("H-S2", "KR-S02, KR-S06", "An RSI above 70 at an upside breakout in an uptrend is followed by continuation, not reversal.", "Forward return after breakouts with and without RSI > 70, in uptrend state only."),
    ("H-P1", "KR-P01, KR-P05", "Three or four of the four top signals on the weekly line up with Bitcoin major tops (2017-12, 2021).", "Descriptive on 2017-2026: signal dates versus the highs; very few events, no P&L."),
    ("H-M4", "KR-M10, KR-M11", "Weekly price above or below the 55 EMA gives the bias and a steep slope predicts continuation.", "Forward weekly return by side and slope bucket; underpowered, descriptive."),
]


def concept_ids():
    ids = set()
    for p in (BASE / "extracts").glob("extract_*.md"):
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^### K-(.+)-(\d\d)\b", line)
            if m:
                ids.add((m.group(1), m.group(2)))
    return ids


def main():
    have = concept_ids()
    bad = []
    rows = []
    for (rid, name, side, typ, rule, params, label, sources, mirror, enc, ph3, blockers) in R:
        codes = set()
        for tok in sources.split(";"):
            code, num = tok.split("-")
            if code not in CODES or (CODES[code], num) not in have:
                bad.append((rid, tok))
            codes.add(code)
        n = len(codes)
        rows.append(dict(rule_id=rid, family=re.match(r"^KR-([A-Z]+)", rid).group(1), name=name, side=side, type=typ, rule=rule, params=params,
                         param_label=label, sources=sources, n_videos=n,
                         cluster=("OK" if n >= 3 else "PROVISIONAL"), mirror_stated=mirror, encodability=enc,
                         phase3=ph3, blockers=blockers, tier="T3"))
    if len(set(r["rule_id"] for r in rows)) != len(rows):
        print("DUPLICATE rule id")
        return 1
    if bad:
        for b in bad:
            print("DEAD_POINTER", b)
        return 1
    cols = list(rows[0].keys())
    with open(BASE / "KROWN_RULES.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    total = len(rows)
    by3 = {k: sum(1 for r in rows if r["phase3"] == k) for k in ("READY", "BLOCKED", "REJECT")}
    prov = sum(1 for r in rows if r["cluster"] == "PROVISIONAL" and r["phase3"] != "REJECT")
    out = []
    out.append("# KROWN CONSOLIDATED RULE LIST (Phase 2/3) - generated by tools/build_ledger.py, do not hand-edit\n")
    n_ext = len({v for v, _ in have})
    n_conc = len(have)
    out.append(f"Corpus: {n_ext} extracts ({n_ext - 1} TA videos + 1 fees video, {n_conc} concepts), TA 101 playlist; which reachable videos are still "
               "missing is in MANIFEST.csv and STATE.md. Tier T3 throughout: ideas and "
               "definitions only; his predictive claims are hypotheses for our own fee-net out-of-sample tests (playbook Part I; CLAUDE.md 2026-10-13).\n")
    out.append("Rules below are OUR paraphrase of each extract's 'Stated mechanics'; his words and GPS lines are in the extracts. Source key "
               "`CODE-NN` = concept `K-<video id>-NN` (codes in MANIFEST.csv). Batch 1 (Aug-Oct 2026): CAN=ep1 candles, TFR=ep2 timeframes, TRL=ep3 trend lines, "
               "SNR=ep4 support/resistance, VOL=ep5 volume, MAV=ep6 moving averages, RNG=ep7 range, FEE=fees video. Batch 2 (Mar-Jun 2026): "
               "GDE=intro guide, TRD=trend (dominant highs and lows), LVL=levels, VJZ=moving-average setup, RSI=RSI, KCM=volatility (BBWP) and entry timing, "
               "TOP=selling long-term holdings at tops. Batch 3 (Oct 2026): OBK=ep8 order book. Every source token was "
               "checked against the real concept headings: dead pointers = 0.\n")
    out.append(f"**{total} consolidated rules: {by3['READY']} READY, {by3['BLOCKED']} BLOCKED, {by3['REJECT']} REJECT** "
               f"(READY or BLOCKED rows seen in fewer than 3 videos are PROVISIONAL: {prov}). Parameter labels: SOURCED = his words carry the number, "
               "OURS = our choice (DEV only, one VALIDATION look, holdout once, every variant in the trial ledger), MIXED = some of each, NONE = no number involved.\n")
    out.append("Not in any extract (so not in this list): a stop DISTANCE anywhere (the only stops are structural: the far side of the compression zone, KR-Q05, "
               "and a close beyond a zone, KR-X01), a general position-size rule (only 'size down as volatility rises' and the 20-85 % scale-out at tops), "
               "a target other than the range height (KR-R07) and volatility-based profit taking (KR-Q06), and anything from videos not yet extracted or "
               "hidden. Do not fill these from memory.\n")
    for fam, title in FAMILIES.items():
        sub = [r for r in rows if r["family"] == fam]
        if not sub:
            continue
        out.append(f"\n## {fam}. {title}\n")
        out.append("| id | rule | params (label) | sources | n | phase3 | blockers / notes |")
        out.append("|---|---|---|---|---|---|---|")
        for r in sub:
            nv = f"{r['n_videos']}" + ("*" if r["cluster"] == "PROVISIONAL" else "")
            out.append(f"| {r['rule_id']} {r['name']} | {r['rule']} | {r['params']} ({r['param_label']}) | {r['sources']} | {nv} | {r['phase3']} | {r['blockers']} |")
    out.append("\n(* = fewer than 3 videos: PROVISIONAL under extraction.md SAFEGUARD 2)\n")
    out.append("\n## Conflicts and tensions (flagged, NOT resolved: extraction.md Phase 2 step 4)\n")
    out.append("| id | rules | the tension | status |")
    out.append("|---|---|---|---|")
    for c in CONFLICTS:
        out.append(f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} |")
    out.append("\n## Hypotheses to test (his claims, T3; each is a DEV event study under the pre-registration, fee-net, same-window placebo)\n")
    out.append("| id | rules | claim | measure |")
    out.append("|---|---|---|---|")
    for h in HYPOTHESES:
        out.append(f"| {h[0]} | {h[1]} | {h[2]} | {h[3]} |")
    (BASE / "KROWN_CONSOLIDATED.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"built {total} rules: READY {by3['READY']} BLOCKED {by3['BLOCKED']} REJECT {by3['REJECT']}; provisional {prov}; dead pointers 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
