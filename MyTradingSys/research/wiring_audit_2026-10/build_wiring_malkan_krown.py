"""Rerunnable builder for WIRING_MALKAN_KROWN.{csv,md} and QUOTES_USED_MALKAN_KROWN.md.

Card extracted-rules-wiring-audit (2026-10-28). Read-only audit: reads the Krown rule ledger, the Krown extracts, the
Malkan glossary and the layer code; writes only the three files above. Verdicts and notes are the hand-made tables
below (judgement); quotes, file:line, params and counts are computed from disk each run.

Run (repo root): python MyTradingSys/research/wiring_audit_2026-10/build_wiring_malkan_krown.py
Check:           python scripts/dev/verify_extract_quotes.py MyTradingSys/research/wiring_audit_2026-10/QUOTES_USED_MALKAN_KROWN.md
"""
import csv
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MTS = HERE.parents[1]                      # .../MyTradingSys
REPO = MTS.parent
KR = MTS / "research" / "krown_ta101_2026-10-13"
GLOS = MTS / "research" / "setup_catalog_2026-10-15" / "malkan" / "MALKAN_DIVERGENCE_GLOSSARY.md"
LAY = MTS / "backtest" / "layers"
OUT_CSV = HERE / "WIRING_MALKAN_KROWN.csv"
OUT_MD = HERE / "WIRING_MALKAN_KROWN.md"
OUT_Q = HERE / "QUOTES_USED_MALKAN_KROWN.md"


def rel(p):
    return Path(p).resolve().relative_to(REPO).as_posix()


# ---------------------------------------------------------------- code / test location resolvers
_cache = {}


def lines_of(path):
    if path not in _cache:
        _cache[path] = Path(path).read_text(encoding="utf-8").splitlines()
    return _cache[path]


def loc(path, sym):
    """path:line of `def sym` / `class sym` / json key / first literal match of sym."""
    p = LAY / path
    for i, ln in enumerate(lines_of(p), 1):
        if re.search(r"(def|class)\s+%s\b" % re.escape(sym), ln) or ('"%s"' % sym) in ln.split(":")[0] and p.suffix == ".json":
            return "%s:%d" % (rel(p), i)
    for i, ln in enumerate(lines_of(p), 1):
        if sym in ln:
            return "%s:%d" % (rel(p), i)
    raise SystemExit("symbol not found: %s %s" % (path, sym))


C, E, X = "krown/krown_core.py", "krown/krown_events.py", "krown/krown_context.py"
RD, RD2, RM, RMT = "rsi/rsi_divergence.py", "rsi/test_rsi_divergence.py", "rsi/malkan_40_60.py", "rsi/malkan_mtf.py"
TC, TE, TX = "krown/test_krown_core.py", "krown/test_krown_events.py", "krown/test_krown_context.py"
KP, DF, MP = "krown/params/krown_params.json", "rsi/test_div_flags_chart.py", "rsi/params/malkan_divergence_default.json"


def L(*pairs):
    return "; ".join(loc(a, b) for a, b in pairs)


# ---------------------------------------------------------------- Krown verdict table
# id -> (verdict, extent, code pairs, test pairs, note). verdict: W wired, U unwired-worth-wiring, N not-worth-wiring
W, U, N = "wired", "unwired-worth-wiring", "not-worth-wiring"
KV = {
 "KR-T01": (N, "", [], [], "process rule: pick the highest timeframe with 200+ bars; a data check done when the run is set up, not a signal"),
 "KR-T02": (W, "partial", [(X, "d1_direction")], [(TX, "test_d1_table")], "daily vs weekly trend table (1d/1w only); the full ladder 1w>1d>12h>...>5m is not coded"),
 "KR-T03": (W, "partial", [(X, "d1_direction"), (X, "d2_regime"), (X, "d3_location")], [(TX, "test_d1_table"), (TX, "test_d2_fade_and_breakout")], "tide (trend), decision (regime), timing (location) exist as context dimensions D1-D3 for the event study; no routine that gates a trade"),
 "KR-T04": (W, "full", [(X, "build_daily_rows")], [(TX, "test_boundary_is_strict")], "one row per CLOSED 1d bar; point-in-time tests (join, truncation) pass"),
 "KR-T05": (N, "", [], [], "discretion (most days no trade); the fire-rate ceiling in krown_events.over_ceiling is the nearest mechanical echo, OURS"),
 "KR-T06": (W, "partial", [(C, "trend_state")], [(TC, "test_dominant_low_and_reversal")], "trend/range mode is the up/down/range state; the mode-first routing of signals is not coded"),
 "KR-T07": (U, "", [], [], "flat tangled averages plus shrinking volume as a range tell: not coded (range_state uses highs/lows only)"),
 "KR-T08": (W, "full", [(X, "weekly_from_daily"), (X, "build_daily_rows")], [(TX, "test_week_start_and_weekly_rebuild")], "1d and 1w rebuilt from klines; 4h aggregation for timing"),
 "KR-T09": (N, "", [], [], "order of work for the analyst (trend, levels, volatility, momentum); the layer computes all of them"),
 "KR-Z01": (W, "full", [(C, "zone_bounds")], [(TC, "test_zone_bounds")], "zone = close to wick extreme of the pivot bar"),
 "KR-Z02": (W, "full", [(C, "zones_from")], [(TC, "test_needs_two_turns_unless_heavy_volume")], "zone_min_turns=2 SOURCED"),
 "KR-Z03": (W, "full", [(C, "zones_from")], [(TC, "test_at_most_five_zones")], "zone_max=5 SOURCED (the 3 minimum is not enforced)"),
 "KR-Z04": (W, "full", [(C, "zones_from")], [(TC, "test_needs_two_turns_unless_heavy_volume")], "heavy-volume pivot (>=2x) sorts first and passes with one turn"),
 "KR-Z05": (W, "full", [(C, "swings")], [(TC, "test_zone_not_used_before_confirming_close")], "swing known only k bars later (avail = i+k)"),
 "KR-Z06": (W, "partial", [(C, "zones_from")], [], "code expires pivots older than zone_lookback=250 bars (OURS) although he says zones do not expire"),
 "KR-Z07": (W, "full", [(E, "build_events"), (C, "trend_state")], [(TC, "test_no_reversal_on_wick_only")], "S2 and the trend reversal use the close beyond the boundary, never the wick"),
 "KR-Z08": (W, "partial", [(E, "build_events")], [(TE, "test_schema")], "S1 trades the test of a zone; the scalp-inside / do-not-buy-inside-resistance behaviour is not coded"),
 "KR-Z09": (U, "", [], [], "role flip (broken support becomes resistance): no detector; S2 stops at the break"),
 "KR-Z10": (U, "", [], [], "break, wait, retest routine: S2 fires on the break close only; retest leg not coded"),
 "KR-Z11": (W, "partial", [(E, "build_events")], [], "S2 takes the break with no retest, which matches 'not required'; no retest arm to compare"),
 "KR-Z12": (N, "", [], [], "round-number levels: BLOCKED in the ledger (no mechanical definition of which round number); no source number"),
 "KR-Z13": (W, "partial", [(C, "zones_from")], [], "zone carries touches and mature (>3 tests) flag; no setup consumes it"),
 "KR-Z14": (N, "", [], [], "stop harvesting beside levels: BLOCKED, needs order-book / stop-cluster data we do not hold"),
 "KR-Z15": (W, "full", [(E, "build_events")], [(TE, "test_schema")], "S1: zone tested and held with the trend, proof candle, volume >= 2x"),
 "KR-Z16": (U, "", [], [], "confluence of a static zone with a rising average: no code joins zones and averages"),
 "KR-L01": (W, "full", [(C, "swings")], [(TC, "test_swings")], "zone_k=3 OURS (he gives no number); strict swings"),
 "KR-L02": (U, "", [], [], "trend lines (two points = hypothesis, three touches = line): no line code anywhere in the layer"),
 "KR-L03": (U, "", [], [], "two touches suffice on heavy volume: line rule, no line code (zones have the heavy-volume exception, lines do not exist)"),
 "KR-L04": (U, "", [], [], "reaction at a volume-anchored line = setup KR-S10: not coded (no trend line)"),
 "KR-L05": (U, "", [], [], "no bent-to-fit lines: needs the line detector first"),
 "KR-L06": (U, "", [], [], "line break is new information = setup KR-S11: not coded"),
 "KR-L07": (N, "", [], [], "steepness is a countdown: BLOCKED in the ledger, no measurable threshold"),
 "KR-L08": (N, "", [], [], "horizontal levels matter more than diagonals: a weighting claim; zones are horizontal already"),
 "KR-L09": (W, "full", [(C, "trend_state")], [(TC, "test_no_reversal_on_wick_only")], "trend change needs a close beyond the dominant level"),
 "KR-V01": (W, "full", [(C, "vol_ratio")], [(TC, "test_ratio_and_flags")], "vol_sma=20 SOURCED"),
 "KR-V02": (W, "full", [(C, "vol_flags")], [(TC, "test_ratio_and_flags")], "vol_mult=2 SOURCED"),
 "KR-V03": (W, "partial", [(C, "zones_from")], [(TC, "test_needs_two_turns_unless_heavy_volume")], "heavy pivots rank first; the claim that major pivots come on outsized volume is not itself tested"),
 "KR-V04": (W, "full", [(E, "build_events")], [(TE, "test_schema")], "S1 needs volume >= 2x, S2 above average"),
 "KR-V05": (W, "partial", [(E, "build_events")], [], "S2 fuel gate = volume >= s2_vol_mult 1.0 (OURS); his 'fuel' has no number"),
 "KR-V06": (U, "", [], [], "effort vs result (huge volume on tiny candle) = setup KR-S13: not coded"),
 "KR-V07": (W, "partial", [(E, "build_events")], [(TE, "test_schema")], "S7 hammer on the biggest volume bar of 100 after a downtrend; thresholds OURS, provisional"),
 "KR-V08": (U, "", [], [], "apathy versus panic (volume regime labels): not coded"),
 "KR-V09": (W, "partial", [(C, "coil_score")], [(TC, "test_coil_score")], "coil score uses price ranges only; the declining-volume leg is not used"),
 "KR-V10": (W, "partial", [(C, "vol_flags")], [(TC, "test_ratio_and_flags")], "vol_half=0.5 flag computed; no setup requires it"),
 "KR-V11": (N, "", [], [], "read volume on major venues: BLOCKED, we hold Binance volume only (conflict C6)"),
 "KR-C01": (W, "partial", [(C, "is_hammer"), (C, "is_shooting_star")], [(TC, "test_hammer_star_doji")], "candle shapes coded with OURS ratios"),
 "KR-C02": (W, "partial", [(C, "is_hammer")], [(TC, "test_hammer_star_doji")], "hammer_wick=0.6 OURS stands for 'big wick'"),
 "KR-C03": (W, "full", [(C, "is_hammer")], [(TC, "test_hammer_star_doji")], "hammer: ratios OURS, location and 3-5 bar horizon SOURCED"),
 "KR-C04": (W, "full", [(C, "is_shooting_star")], [(TC, "test_hammer_star_doji")], "mirror of the hammer"),
 "KR-C05": (U, "", [], [], "full-body candle as conviction: not coded"),
 "KR-C06": (W, "full", [(C, "engulfing")], [(TC, "test_strict_engulfing")], "strict: trades beyond prior extreme and closes beyond prior opposite extreme"),
 "KR-C07": (W, "partial", [(C, "is_doji"), (C, "confirm_index")], [(TC, "test_hammer_star_doji")], "doji coded but not used in proof(); confirmation exists as confirm_index"),
 "KR-C08": (W, "full", [(C, "confirm_index")], [(TC, "test_confirmation_close_beyond_wick")], "first close beyond the pattern wick within confirm_horizon=3"),
 "KR-C09": (W, "full", [(C, "is_hammer"), (C, "is_shooting_star"), (C, "engulfing"), (C, "is_doji")], [(TC, "test_hammer_star_doji")], "the four patterns exist"),
 "KR-C10": (W, "full", [(E, "build_events")], [(TE, "test_schema")], "S1 and S3 accept a proof candle only at a zone / range edge, with volume at S1"),
 "KR-M01": (W, "full", [(C, "ema"), (C, "sma")], [(TC, "test_ema_sma_seed")], "21 EMA, 55 EMA, 200 SMA SOURCED"),
 "KR-M02": (W, "full", [(E, "setup_s5")], [(TE, "test_s5_cross_with_200_context")], "S5: 21/55 cross with price on the same side of the 200"),
 "KR-M03": (U, "", [], [], "first contact with the 200 after a long absence (KR-S5 variant): not coded"),
 "KR-M04": (U, "", [], [], "200-week SMA (setup KR-S15): weekly 200 SMA not computed; needs about 4 years of weekly bars, BTC history allows it"),
 "KR-M05": (U, "", [], [], "21/55 EMA band as dynamic support (KR-S5 variant): not coded"),
 "KR-M06": (W, "full", [(C, "leash"), (E, "setup_s6")], [(TC, "test_leash"), (TE, "test_s6_maps_leash")], "5 EMA, 3 closes SOURCED"),
 "KR-M07": (U, "", [], [], "golden/death cross of 50/200 and slope: run_recall_check notes S5 uses 21/55, not his 50/200; the 50/200 cross is not coded"),
 "KR-M08": (N, "", [], [], "SMA versus EMA: a note on which average reacts; both exist"),
 "KR-R01": (W, "full", [(C, "range_state"), (E, "build_events")], [(TC, "test_range_hand_values")], "S3 trades the edge with a proof candle"),
 "KR-R02": (W, "partial", [(E, "build_events")], [(TC, "test_breakout_close")], "edge entry coded; the fake-out arm (poke beyond, close back inside) is not"),
 "KR-R03": (W, "partial", [(C, "coil_score"), (E, "build_events")], [(TC, "test_coil_score")], "S4 coil-break; the volume half of 'declining volume + tightening wedge' is not used"),
 "KR-R04": (U, "", [], [], "longer and tighter range predicts a bigger breakout: no duration/tightness grading of S4"),
 "KR-R05": (U, "", [], [], "bias from the structure inside the range: not coded"),
 "KR-R06": (W, "partial", [(E, "build_events")], [], "S2 has close and fuel; the retest leg of the checklist is not coded"),
 "KR-R07": (U, "", [], [], "range height projects the first leg: the layer emits events only (no targets); exits are a backtest step"),
 "KR-R08": (N, "", [], [], "REJECT in the ledger: slogan (every trend is born in a box), no mechanic"),
 "KR-X01": (N, "", [], [], "BLOCKED in the ledger: manage risk yourself, exit on the close; no number"),
 "KR-X02": (N, "", [], [], "REJECT: limit orders for fees; execution advice, not a signal"),
 "KR-X03": (N, "", [], [], "REJECT: funding by bank transfer / referral"),
 "KR-F01": (N, "", [], [], "REJECT: philosophy"),
 "KR-F02": (N, "", [], [], "REJECT: philosophy"),
 "KR-F03": (N, "", [], [], "REJECT: philosophy"),
 "KR-F04": (N, "", [], [], "REJECT: philosophy"),
 "KR-F05": (N, "", [], [], "REJECT: philosophy"),
 "KR-F06": (N, "", [], [], "REJECT: philosophy"),
 "KR-F07": (N, "", [], [], "REJECT: philosophy"),
 "KR-F08": (N, "", [], [], "REJECT: his own statistics, not testable by us"),
 "KR-F09": (N, "", [], [], "REJECT: 'almost always' claims, no number"),
 "KR-Z17": (W, "full", [(E, "build_events")], [(TE, "test_schema")], "S1 long only in an up state, short only in a down state"),
 "KR-Z18": (W, "partial", [(C, "zones_from")], [], "zone_lookback=250 OURS stands for 'recent'; dominant-only and look-left are not separate rules"),
 "KR-L10": (W, "full", [(C, "trend_state")], [(TC, "test_dominant_low_and_reversal"), (TC, "test_state_is_causal")], "dominant-high/low state machine, swing_tol OURS"),
 "KR-L11": (W, "partial", [(E, "build_events"), (X, "d1_direction")], [(TX, "test_d1_table")], "S1 and the D1 dimension apply the filter; S2-S9 do not"),
 "KR-L12": (U, "", [], [], "in a sideways range favour the previous trend: not coded"),
 "KR-M09": (U, "", [], [], "pair rule (lower period average above higher): not coded"),
 "KR-M10": (U, "", [], [], "weekly 55 EMA bias: not coded (hypothesis H-M4 in the ledger)"),
 "KR-M11": (U, "", [], [], "slope of an average as trend strength: not coded"),
 "KR-M12": (N, "", [], [], "averages are filters not entries: design principle; S5 respects it only partly"),
 "KR-M13": (U, "", [], [], "range break with the averages: not coded"),
 "KR-C11": (W, "full", [(C, "three_crows")], [(TC, "test_three_black_crows")], "crows_bars=3 SOURCED; feeds the S9 candle signal"),
 "KR-Q01": (W, "full", [(C, "bbwp")], [(TC, "test_bbwp_hand_values")], "basis 7 and lookback 100 SOURCED; multiplier 2.0 OURS"),
 "KR-Q02": (W, "full", [(C, "bbwp_regime")], [(TC, "test_regime")], "85 high, 50 confirm SOURCED; low 30 OURS (he gives 25-35)"),
 "KR-Q03": (W, "partial", [(E, "setup_s8")], [(TE, "test_s8_compression_breakout")], "compression then expansion encoded as S8 only"),
 "KR-Q04": (W, "partial", [(X, "d2_regime")], [(TX, "test_d2_fade_and_breakout")], "direction-neutral volatility used as a regime dimension"),
 "KR-Q05": (W, "partial", [(E, "setup_s8")], [(TE, "test_s8_compression_breakout")], "S8: s8_recent and s8_break_n OURS; his chart timeframe not named"),
 "KR-Q06": (U, "", [], [], "volatility-based profit taking: no exit logic in the layer"),
 "KR-Q07": (U, "", [], [], "the volatility trap: not coded"),
 "KR-Q08": (U, "", [], [], "indicators behave differently by regime: D2 labels regime but no per-indicator switching"),
 "KR-Q09": (N, "", [], [], "volatility and sizing: sizing is outside the layer"),
 "KR-Q10": (W, "partial", [(X, "d2_regime"), (E, "build_events")], [(TX, "test_d2_fade_and_breakout")], "BBWP > 85 is a top-signal leg (S9) and a regime flag; turning-point claim not tested by itself"),
 "KR-Q11": (N, "", [], [], "REJECT: options, not BTC spot/perp"),
 "KR-S01": (N, "", [], [], "RSI is momentum, not direction: caveat, no mechanic"),
 "KR-S02": (W, "partial", [(X, "build_daily_rows"), (C, "rsi")], [(TC, "test_wilder_hand_values")], "RSI computed (period 14 OURS); the 'overbought is not a sell' rule exists only as the absence of an RSI>70 sell"),
 "KR-S03": (W, "full", [(C, "rsi_zone")], [(TC, "test_zone")], "40/60 SOURCED; also Malkan 40/60 in rsi/malkan_40_60.py"),
 "KR-S04": (U, "", [], [], "RSI extremes and asymmetry: not coded"),
 "KR-S05": (W, "partial", [(C, "bear_divergence"), ("rsi/krown_hidden_divergence.py", "krown_hidden_divergence")], [(TC, "test_bearish_divergence")], "bearish regular divergence feeds S9; generic hidden divergence is kept in the RSI folder as a Krown confluence feed; no bullish regular arm for entries"),
 "KR-S06": (U, "", [], [], "RSI-confirmed breakout: not coded (hypothesis H-S2 in the ledger)"),
 "KR-S07": (W, "full", [(C, "macd")], [(TC, "test_macd_defined_after_slow_period")], "MACD cross is the momentum leg of S9; periods 12/26/9 OURS"),
 "KR-P01": (W, "full", [(C, "tops"), (E, "setup_s9")], [(TC, "test_three_of_four_fires_once"), (TE, "test_s9_is_a_sell_signal")], "three of four SOURCED; window 3 OURS"),
 "KR-P02": (N, "", [], [], "scale out instead of selling the top: position management, outside the layer"),
 "KR-P03": (U, "", [], [], "ranking/order of the top signals: all four legs weigh the same in tops()"),
 "KR-P04": (W, "partial", [(C, "tops")], [(TC, "test_stale_signals_do_not_fire")], "no early call = need 3 of 4 inside the window; not a separate rule"),
 "KR-P05": (W, "partial", [("krown/run_recall_check.py", "R09")], [("krown/test_recall_table.py", "test")], "Bitcoin top examples are the recall check cases (R09, R10)"),
 "KR-P06": (N, "", [], [], "BLOCKED: wait for a reset after all four signals; no definition of reset"),
 "KR-F10": (N, "", [], [], "REJECT: philosophy"),
 "KR-F11": (N, "", [], [], "REJECT: process advice (test, document, iterate); it is how we work, not a layer rule"),
 "KR-OBK01": (N, "", [], [], "maker/taker fee gap: fees live in sim.py (canonical schedule), not in this layer"),
 "KR-OBK02": (N, "", [], [], "spread and depth health: needs order-book history we do not hold"),
 "KR-OBK03": (N, "", [], [], "market orders move price: execution fact"),
 "KR-OBK04": (N, "", [], [], "hidden size / iceberg / TWAP: needs L2 and tape we do not hold"),
 "KR-OBK05": (N, "", [], [], "painting the book / spoofing: needs L2 history"),
 "KR-OBK06": (N, "", [], [], "REJECT: order book is a poor direction tool"),
 "KR-OBK07": (N, "", [], [], "pre-execution habit: discipline"),
 "KR-LQC01": (U, "", [], [], "liquidation cascade anatomy: not coded; needs liquidation feed (check data availability first)"),
 "KR-LQC02": (U, "", [], [], "funding rate and open interest as liquidation weather: not coded; funding history exists for backtests, OI history not checked"),
 "KR-LQC03": (N, "", [], [], "deleveraging flush recovery pattern: discretionary description"),
 "KR-LQC04": (N, "", [], [], "liquidation risk defence and distance: sizing / leverage advice"),
}


# ---------------------------------------------------------------- quote lookup for Krown rules
def manifest():
    m = {}
    with (KR / "MANIFEST.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            m[r["code"]] = r["video_id"]
    return m


GPS = re.compile(r"Source GPS:\s*([A-Za-z0-9_-]{11})\s*\|\s*(BEGIN|MIDDLE|END)")
QRE = re.compile(r'^>\s*"(.*)"\s*$')


def quote_blocks(ls, start, stop):
    """Quote blocks (quote line, GPS line, next line) of an already-written text file between 1-based lines start..stop.
    Pure text parsing of a finished document, no market data."""
    trio = list(zip(ls, ls[1:], ls[2:] + [""]))
    for n in range(start - 1, min(stop, len(trio))):
        q, g, nxt = trio[n]
        if q.startswith("### ") and n >= start:
            return
        mq, mg = QRE.match(q), GPS.search(g)
        if mq and mg:
            yield n + 1, mq.group(1), mg.group(1), mg.group(2), nxt


def krown_quote(sources, codes):
    """First resolvable concept id in `sources` -> (quote, vid, pos, 'file:line', concept). Else None."""
    for tok in sources.split(";"):
        mm = re.match(r"^([A-Z]+)-(\d+)$", tok.strip())
        if not mm or mm.group(1) not in codes:
            continue
        vid, n = codes[mm.group(1)], int(mm.group(2))
        f = KR / "extracts" / ("extract_%s.md" % vid)
        if not f.exists():
            continue
        ls = lines_of(f)
        head = "### K-%s-%02d " % (vid, n)
        for i, ln in enumerate(ls, 1):
            if ln.startswith(head):
                for lineno, q, v, pos, _ in quote_blocks(ls, i + 1, i + 40):
                    return q, v, pos, "%s:%d" % (rel(f), lineno), tok.strip()
    return None


# ---------------------------------------------------------------- Malkan table
# id, glossary anchor line (quote = first quote block at/after it), rule, verdict, extent, code pairs, test pairs, param, note
MV = [
 ("MLK-D01", 42, "2.1 Normal (regular) divergence is contra-trend: a reversal signal", W, "full", [(RD, "rsi_divergence")], [(RD2, "test_bullish_single"), (RD2, "test_bearish")], "kinds bullish/bearish", "4 videos agree"),
 ("MLK-D02", 62, "2.1 Compare close to close (RSI is built on the close)", W, "full", [(RD, "_pivots")], [(RD2, "test_equal_closes_are_not_pivots")], "compare=close_to_close (params json)", "swings are strict extremes of the close; G speaks of swing lows (conflict C4), code follows W and C"),
 ("MLK-D03", 78, "2.2 Bearish divergence: price higher high, RSI lower high, inside an uptrend", W, "partial", [(RD, "rsi_divergence")], [(RD2, "test_bearish")], "", "shape coded; the 'inside an uptrend' context is not required for the regular kinds"),
 ("MLK-D04", 96, "2.2 Read it on the weekly, trade it on the daily; bigger timeframe = bigger U-turn", W, "partial", [("rsi/run_divergence_mtf.py", "run_tf")], [("rsi/test_run_divergence_mtf.py", "test")], "", "run per timeframe; no rule that reads the weekly and enters on the daily"),
 ("MLK-D05", 105, "2.2 Confirmation: wait for the red candle after B", U, "", [], [], "", "the divergence module stops at the event ('Not here: candle confirmation'); the backtest enters at the event with a generic bracket"),
 ("MLK-D06", 109, "2.2 Stop above the high including the shadow", U, "", [], [], "", "run_rsi_backtest uses a flat 1% stop / 2% target (OURS), not his stop; testable"),
 ("MLK-D07", 113, "2.2 Target = point C between A and B", U, "", [], [], "", "target C not coded; generic 2% target used; testable"),
 ("MLK-D08", 117, "2.2 Wait for a trendline break before acting (C only)", U, "", [], [], "", "no trend line code in the repo layers; single video"),
 ("MLK-D09", 122, "2.2 Divergence is a slowing down, not a guaranteed turn", N, "", [], [], "", "caveat, no mechanic"),
 ("MLK-D10", 130, "2.3 Bullish divergence: price lower low, RSI higher low, in a downtrend", W, "partial", [(RD, "rsi_divergence")], [(RD2, "test_bullish_single")], "", "mirror of D03; downtrend context not required"),
 ("MLK-D11", 152, "2.3 Bullish confirmation: wait for the bullish candle", U, "", [], [], "", "same gap as D05"),
 ("MLK-D12", 164, "2.4 Minimum 3 bars between A and B", W, "full", [(RD, "rsi_divergence")], [(RD2, "test_bar_window"), (RD2, "test_validation")], "min_bars=3 (params json)", "SOURCED (W); counted inclusive of A and B"),
 ("MLK-D13", 168, "2.4 Most powerful at 3 to 10 bars", W, "full", [(RD, "rsi_divergence")], [(RD2, "test_params_file_matches_sourced_values")], "max_bars=10", "W 10; C says 3, 5, 7 and later tolerates 15-20 (kept as conflict)"),
 ("MLK-D14", 172, "2.4 Diluted beyond 30 to 50 bars", W, "partial", [(RD, "rsi_divergence")], [(RD2, "test_too_far_apart")], "max_bars=10", "windows above 10 are excluded outright; the 'diluted, weaker' gradient is not graded"),
 ("MLK-D15", 189, "2.4 Strongest bearish divergence near RSI 60, bullish near 40", U, "", [], [], "", "UNVERIFIED (one video); rsi_level argument exists only for PRD/NRD; testable on held data"),
 ("MLK-D16", 193, "2.4 Extremes (70-80 / 20-30) are weaker", U, "", [], [], "", "UNVERIFIED (one video); same filter as D15"),
 ("MLK-D17", 198, "2.4 Short swing use: 3- and 5-bar divergence for 2-4 day trades", W, "partial", [(RD, "rsi_divergence")], [(RD2, "test_bar_window")], "min_bars=3", "3-5 bar windows can be run; no 2-4 day holding rule"),
 ("MLK-P01", 207, "2.5 PRD definition: price higher low, RSI lower low", W, "full", [(RD, "rsi_divergence")], [(DF, "test_prd")], "kind=prd", "2 videos (A Hindi, G English)"),
 ("MLK-P02", 298, "2.5 PRD needs an uptrend, marked by RSI above 60 at both points", W, "full", [(RD, "rsi_divergence")], [(DF, "test_prd_shape_correct_but_not_uptrend")], "prd_min_rsi=60.0 (SOURCED 'about sixty'); strict >= compare OURS", "his words: 'both the point should be about sixty'"),
 ("MLK-P03", 234, "2.5 PRD means continuation up, with the trend", W, "partial", [(RD, "rsi_divergence")], [(DF, "test_prd")], "", "event is emitted; the long entry is left to the caller"),
 ("MLK-P04", 257, "2.5 In an uptrend look for PRD first", W, "partial", [(RD, "rsi_divergence")], [(DF, "test_prd")], "", "PRD is computed; no routine that prefers PRD over a bearish divergence (see MLK-W01)"),
 ("MLK-P05", 266, "2.5 There can be several PRDs in one trend", W, "full", [(RD, "rsi_divergence")], [(RD2, "test_chain_counts_multiple_divergences")], "chain counter", "chain counts consecutive diverging pairs"),
 ("MLK-P06", 270, "2.5 PRD timeframes: daily mostly, weekly at most, monthly hard", W, "partial", [("rsi/run_divergence_mtf.py", "main")], [("rsi/test_run_divergence_mtf.py", "test")], "", "timeframes are a runner argument"),
 ("MLK-P07", 281, "2.5 PRD entry: buy at support on the retracement, stop below the swing low (G only)", U, "", [], [], "", "UNVERIFIED (one video); entry and stop not coded; A withholds them"),
 ("MLK-P08", 290, "2.5 Bar count for PRD: 7-8 good, under 15, 5 to 50", W, "partial", [(RD, "rsi_divergence")], [(RD2, "test_params_file_matches_sourced_values")], "reverse.min_bars=5, max_bars=14 (OURS+UNVERIFIED)", "sources conflict (glossary C1); the pair of numbers is OURS"),
 ("MLK-P09", 303, "2.5 Best case: the PRD at the very start of the trend, right after RSI crosses 60", U, "", [], [], "", "UNVERIFIED (one video); needs a 'first PRD after the 60 cross' tag"),
 ("MLK-N01", 311, "2.6 NRD definition: price lower high, RSI higher high, in a downtrend (RSI below 40)", W, "full", [(RD, "rsi_divergence")], [(DF, "test_nrd")], "nrd_max_rsi=40.0 (SOURCED 'below forty')", "2 videos (A, G)"),
 ("MLK-N02", 337, "2.6 NRD is seen inside a running downtrend; the sell comes on the new low", W, "partial", [(RD, "rsi_divergence")], [(DF, "test_nrd")], "", "the NRD event is coded; the 'new low' confirmation is not"),
 ("MLK-H01", 356, "2.7 Hidden divergence = another name for reverse divergence (A only)", W, "partial", [("rsi/krown_hidden_divergence.py", "krown_hidden_divergence")], [(DF, "test_prd")], "krown_hidden_bars 3..10 OURS", "operator 2026-10-28: generic hidden divergence (no trend condition) is a Krown rule and lives in krown_hidden_divergence.py; Malkan's version is PRD/NRD"),
 ("MLK-W01", 383, "2.8 When PRD and regular divergence meet, PRD wins (trend following)", N, "", [], [], "", "A is internally inconsistent (conflict C5: 'depends on your skill and judgment')"),
 ("MLK-W02", 399, "2.8 When the PRD fails, look at the bearish divergence", N, "", [], [], "", "discretionary sequence, no failure definition"),
 ("MLK-G01", 408, "2.9 3, 5 and 7 star grades of reverse divergence", N, "", [], [], "", "conditions withheld by the trader (code: 'NOT implemented'); nothing to encode"),
 ("MLK-G02", 420, "2.9 Seven star: monthly at 60 plus divergence on the daily (W)", U, "", [], [], "", "UNVERIFIED (one video); malkan_mtf.py gates 40/60 bounces by weekly/monthly regime but not divergence; testable"),
 ("MLK-G03", 424, "2.9 Monthly RSI above 60, daily below 40, divergence visible: one of the best trades (W)", U, "", [], [], "", "UNVERIFIED (one video); same composer gap as G02"),
 ("MLK-G04", 429, "2.9 Single / multiple divergences; Class A/B/C", W, "partial", [(RD, "rsi_divergence")], [(RD2, "test_chain_counts_multiple_divergences")], "chain counter", "single/multiple = chain; classes undefined in any fetched video (not codable)"),
 ("MLK-G05", 433, "2.9 Monthly above 60 with double / triple divergence goes like a rocket (W)", W, "partial", [(RD, "rsi_divergence")], [(RD2, "test_chain_counts_multiple_divergences")], "chain >= 2/3", "chain exists; the monthly > 60 gate is not applied to divergence"),
]


def glossary_quote(anchor):
    ls = lines_of(GLOS)
    for lineno, q, v, pos, nxt in quote_blocks(ls, anchor, anchor + 25):
        cite = nxt[len("- cite:"):].strip() if nxt.startswith("- cite:") else ""
        return q, v, pos, "%s:%d" % (rel(GLOS), lineno), cite
    return None


# ---------------------------------------------------------------- build
def main():
    rows, quotes = [], []
    codes = manifest()
    rules = list(csv.DictReader((KR / "KROWN_RULES.csv").open(encoding="utf-8", newline="")))
    missing = [r["rule_id"] for r in rules if r["rule_id"] not in KV]
    extra = [k for k in KV if k not in {r["rule_id"] for r in rules}]
    if missing or extra:
        raise SystemExit("verdict table mismatch: missing %s extra %s" % (missing, extra))
    rule_file = rel(KR / "KROWN_RULES.csv")

    for r in rules:
        v, ext, code, test, note = KV[r["rule_id"]]
        q = krown_quote(r["sources"], codes)
        if q:
            quotes.append((r["rule_id"], q[0], q[1], q[2]))
            quote, qloc, qsrc, qstat = q[0], q[3], q[1], "OK"
        else:
            quote, qloc, qsrc, qstat = "", "", "", "NO_QUOTE"
        rule_loc = rule_file + ":" + str(next(i for i, ln in enumerate(lines_of(KR / "KROWN_RULES.csv"), 1) if ln.startswith(r["rule_id"] + ",")))
        nv = int(r["n_videos"] or 0)
        pr = ""
        if v == U:
            pr = "H" if nv >= 4 else ("M" if nv >= 2 else "L")
        rows.append({
            "trader": "Krown", "rule_id": r["rule_id"], "rule": r["name"], "quote": quote, "quote_file_line": qloc,
            "rule_file_line": rule_loc, "source": qsrc,
            "code_file_line": "; ".join(loc(a, b) if b != "R09" else loc(a, b) for a, b in code) or "none (no code)",
            "param": ("%s (%s)" % (r["params"], r["param_label"])) if r["params"] and r["param_label"] != "NONE" else "",
            "test": "; ".join(loc(a, b) for a, b in test) or "none",
            "verdict": v, "extent": ext, "priority": pr, "n_videos": nv, "quote_status": qstat, "note": note,
        })

    for (mid, anchor, rule, v, ext, code, test, param, note) in MV:
        g = glossary_quote(anchor)
        if not g:
            raise SystemExit("no quote for " + mid)
        quotes.append((mid, g[0], g[1], g[2]))
        cite = g[4]
        rows.append({
            "trader": "Malkan", "rule_id": mid, "rule": rule, "quote": g[0], "quote_file_line": g[3],
            "rule_file_line": rel(GLOS) + ":" + str(anchor), "source": g[1],
            "code_file_line": "; ".join(loc(a, b) for a, b in code) or "none (no code)",
            "param": param, "test": "; ".join(loc(a, b) for a, b in test) or "none",
            "verdict": v, "extent": ext, "priority": ("M" if v == U else ""), "n_videos": "",
            "quote_status": "OK", "note": (note + ("; extract cite " + cite if cite else "")),
        })

    cols = ["trader", "rule_id", "rule", "quote", "quote_file_line", "rule_file_line", "source", "code_file_line", "param", "test",
            "verdict", "extent", "priority", "n_videos", "quote_status", "note"]
    with OUT_CSV.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    with OUT_Q.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Quotes used by WIRING_MALKAN_KROWN.csv (generated by build_wiring_malkan_krown.py; one block per rule)\n\n")
        fh.write("Check: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/wiring_audit_2026-10/QUOTES_USED_MALKAN_KROWN.md` (exit 0).\n\n")
        for rid, q, vid, pos in quotes:
            fh.write("<!-- %s -->\n> \"%s\"\n**Source GPS: %s | %s**\n\n" % (rid, q, vid, pos))

    write_md(rows)
    print("rows", len(rows))


def write_md(rows):
    cnt = Counter((r["trader"], r["verdict"] if r["verdict"] != W else "wired (%s)" % r["extent"]) for r in rows)
    tot = Counter(r["trader"] for r in rows)

    def c(t, k):
        return cnt.get((t, k), 0)
    md = []
    a = md.append
    a("# Wiring audit: Malkan, Krown (every sourced rule vs layer code, params, tests)\n")
    a("Card `extracted-rules-wiring-audit`, 2026-10-28, MTS_Doctor (Sonnet). Read-only: no layer code, params or backtests changed. Sibling: `WIRING_TOM_FABIO_HABIB.md`.")
    a("Table: `WIRING_MALKAN_KROWN.csv`. Rebuild: `build_wiring_malkan_krown.py` (verdicts are its hand-made tables; quotes, file:line and counts are computed). Quotes checked with `scripts/dev/verify_extract_quotes.py` on `QUOTES_USED_MALKAN_KROWN.md`.\n")
    a("## 1. What a row is")
    a("- Krown: one row per rule of the ledger `KROWN_RULES.csv` (131 rules, KR-T01..KR-LQC04); the 16 setups KR-S1..KR-S16 of `KROWN_SETUP_CATALOG.md` are built from these rules and cite them by id, so every catalog rule is counted once. Quote = the first quote under the rule's first source concept id in the extracts (`extracts/extract_<video>.md:<line>`). 22 of 131 rules are REJECT (16) or BLOCKED (6) in the ledger; they get not-worth-wiring or, where the block is only missing code, unwired, with the reason.")
    a("- Malkan: one row per rule bullet of `MALKAN_DIVERGENCE_GLOSSARY.md` section 2 (2.1 to 2.9), 36 rows. Only his sourced PRD/NRD counts; generic hidden divergence is a Krown rule (operator 2026-10-28), kept in `rsi/krown_hidden_divergence.py`. Quote = the glossary quote block (its extract cite is in the note). Hindi originals are not separate rows. `SETUP_CATALOG.md` itself holds no Malkan rule (0 mentions); it covers Tom and Fabio (sibling card).")
    a("- Malkan rules outside these three documents (the 40/60 regime and bounce setups `rsi/malkan_40_60.py`, `rsi/malkan_mtf.py`, from `malkan_rsi_2026-09-28/WEB_RESEARCH.md`) are wired and tested but not rows here; listed in section 5.")
    a("- Verdict: `wired` (extent `full` = the rule as he states it is coded; `partial` = a stated part is missing, see note); `unwired-worth-wiring` = mechanical, data we hold, not coded; `not-worth-wiring` = philosophy, sizing, execution, needs L2/option data we do not hold, or no mechanic. Wiring means a pre-registered test first, never a live change.")
    a("- Param labels: SOURCED = his number; OURS = our choice (never his). Krown thresholds in `krown/params/krown_params.json` carry their label per key. Layer flag `enabled=false`: alert-only, no live wiring.")
    a("- Priority of unwired rows: Krown H/M/L = rule stated in 4+ / 2-3 / 1 videos (`n_videos`, how strongly he stresses it); Malkan rows are M (the glossary marks most as one video, UNVERIFIED).\n")
    a("## 2. Counts by verdict\n")
    a("| Trader | wired (full) | wired (partial) | unwired-worth-wiring | not-worth-wiring | rows |")
    a("|---|---|---|---|---|---|")
    for t in ("Malkan", "Krown"):
        a("| %s | %d | %d | %d | %d | %d |" % (t, c(t, "wired (full)"), c(t, "wired (partial)"), c(t, U), c(t, N), tot[t]))
    a("| **all** | %d | %d | %d | %d | %d |\n" % (sum(c(t, "wired (full)") for t in tot), sum(c(t, "wired (partial)") for t in tot), sum(c(t, U) for t in tot), sum(c(t, N) for t in tot), len(rows)))
    a("Reading: Krown's v0 layer codes zones, trend state, volume, candles, averages, BBWP, ranges and the four-signal top; it has no trend-line code, no exits and no weekly 200 SMA, which is where most unwired rows sit. Malkan's divergence core (regular, PRD, NRD with the 60/40 regime, bar window, chain) is coded and tested; his confirmation, stop and target are not (the backtest uses a flat 1%/2% bracket).\n")
    a("## 3. Top 10 unwired-worth-wiring (by how strongly he stresses it)\n")
    un = [r for r in rows if r["verdict"] == U and r["trader"] == "Krown"]
    un.sort(key=lambda r: (-int(r["n_videos"] or 0), r["rule_id"]))
    a("| rank | id | videos | rule | what is missing |")
    a("|---|---|---|---|---|")
    for i, r in enumerate(un[:10], 1):
        a("| %s%d | %s | %s | %s | %s |" % (r["priority"], i, r["rule_id"], r["n_videos"], r["rule"][:70], r["note"][:150]))
    a("\nMalkan unwired, in order of fit with the existing layer: D05/D11 candle confirmation, D06 stop above the high incl. shadow, D07 target at point C, then D15 RSI level near 40/60 on regular divergence, G02/G03 monthly-60 gate on divergence.\n")
    a("## 4. NO_QUOTE")
    nq = [r for r in rows if r["quote_status"] != "OK"]
    if nq:
        a("Rules whose source ids (LQC, liquidation episode) have no quote block in the extracts (kept, verdict from the ledger text and the code):\n")
        for r in nq:
            a("- %s %s: %s" % (r["rule_id"], r["rule"], r["note"]))
    else:
        a("None: every row has a verified quote.")
    a("")
    a("## 5. Findings for the operator")
    a("- Every wired Krown core function and PRD/NRD (`test_div_flags_chart.py`) has a unit test; a test that pins a number to his quote exists only for the Malkan bar window (`test_params_file_matches_sourced_values`).")
    a("- Wired but unused: `mature` zone flag (KR-Z13), `vol_half` (KR-V10), doji (KR-C07): computed, consumed by no setup.")
    a("- A conflict between the layer and his words: zones expire after 250 bars in code (OURS) while KR-Z06 says they do not.")
    a("- Outside the three documents: `rsi/malkan_40_60.py` (MLK-R1, S1, S2) and `rsi/malkan_mtf.py` (MLK-GAP1) are wired with tests `test_malkan_40_60.py`, `test_malkan_mtf.py`.\n")
    a("ROWS: %d" % len(rows))
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
