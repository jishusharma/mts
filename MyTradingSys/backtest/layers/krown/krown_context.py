"""Krown point-in-time CONTEXT rows (step S1 of research/krown_audit_2026-10-22/FABLE_CARD_CONFLUENCE.md).

Pure functions of closed bars. No outcome, no P&L, no live wiring. Every Krown-derived field is "OURS impl. of KR-x" (the
detectors failed recall, RECALL.md:36): field names end `_ours` or sit in OURS_FIELDS. Naive baselines are columns of the same
table so a later step can race Krown trend against them.

Point-in-time rule (PRE_REG_S1_COUNTS.md s2.3): a row built from a bar that opens at `open_ms` with period P has
    available_at = open_ms + P + LATENCY_MS            (bar close + 1 min write latency, OURS, REVIEW_OPUS F17)
and an event with decision_ts = event bar open + event tf may use the row iff available_at < decision_ts (strict).
`join_row` is the only join. `check_point_in_time` is the test hook: it FAILS on any joined row that is not yet available.

Parameters: params/krown_params.json (SOURCED with a ledger id, or OURS). Extra OURS numbers are the module constants below.
"""
import bisect
import math
from pathlib import Path

import krown_core as kc

HERE = Path(__file__).parent

DAY_MS = 86_400_000
H4_MS = 4 * 3_600_000
WEEK_MS = 7 * DAY_MS
LATENCY_MS = 60_000                 # OURS: REVIEW_OPUS F17 (write latency 1 min)
ATR_N = 14                          # OURS period; plain SMA ATR is SOURCED (FORMULAS.md:324, operator decision 2026-09-28)
SMA_LONG = 200                      # OURS naive baseline (REVIEW_OPUS F12)
RET_N = 20                          # OURS naive baseline (REVIEW_OPUS F12)
FRESH_LOOKBACK = 6                  # OURS (design s3 D2: "rose from <= 30 within 6 bars")
FRESH_FROM = 30                     # OURS (= bbwp_low)
FRESH_TO = 50                       # SOURCED bbwp_confirm 50 (KR-Q02), params json
Z_NEAR_ATR = 0.5                    # OURS default (design s3 D3); the frozen value is chosen in run/COUNTS.md from counts
EDGE_FRAC = 0.2                     # OURS = params range_edge
MID_LO, MID_HI = 1.0 / 3, 2.0 / 3   # "middle third of a daily range" (design s3 D3)

OURS_FIELDS = ("trend_1d_ours", "trend_1w_ours", "bbwp_1d_ours", "rsi_1d_ours", "rsi_zone_1d_ours", "zones_ours",
               "range_top_ours", "range_bottom_ours", "bbwp_4h_ours", "bbwp_4h_min6_ours", "exp_dir_4h_ours",
               "atr14_1d")
NAIVE_FIELDS = ("naive_trend_sma200", "naive_trend_ret20")


# ---- small pure helpers -------------------------------------------------------------------------------------------

def atr_sma(h, l, c, n):
    """Plain SMA of true range (FORMULAS.md section 12, worked example 2.1667). TR[i] needs a prior close, so first value at i = n."""
    out = [None] * len(c)
    tr = [None] * len(c)
    for i in range(1, len(c)):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    for t in range(n, len(c)):
        out[t] = sum(tr[t - n + 1:t + 1]) / n
    return out


def _sign(x):
    return 0 if x == 0 else (1 if x > 0 else -1)


def naive_trend_sma(c, n=SMA_LONG):
    out = [None] * len(c)
    for t in range(n - 1, len(c)):
        m = sum(c[t - n + 1:t + 1]) / n
        out[t] = _sign(c[t] - m)
    return out


def naive_trend_ret(c, n=RET_N):
    out = [None] * len(c)
    for t in range(n, len(c)):
        out[t] = _sign(c[t] - c[t - n])
    return out


def trend_code(state):
    return {"up": 1, "down": -1, "range": 0}.get(state)


def week_start_ms(open_ms):
    """Monday 00:00 UTC of the ISO week holding open_ms (epoch day 0 is a Thursday)."""
    d = open_ms // DAY_MS
    return (d - (d + 3) % 7) * DAY_MS


def weekly_from_daily(t, o, h, l, c):
    """Rebuild 1w bars from 1d (the 1w file has 8 gaps in 2022). Only weeks with all 7 daily bars; lists keyed by week open."""
    wk = {}
    for i in range(len(t)):
        wk.setdefault(week_start_ms(t[i]), []).append(i)
    wt, wo, wh, wl, wc = [], [], [], [], []
    for ws in sorted(wk):
        idx = wk[ws]
        if len(idx) != 7:
            continue
        wt.append(ws)
        wo.append(o[idx[0]])
        wh.append(max(h[i] for i in idx))
        wl.append(min(l[i] for i in idx))
        wc.append(c[idx[-1]])
    return wt, wo, wh, wl, wc


def aggregate_4h(t, o, h, l, c):
    """4h bars (open on 00/04/08/12/16/20 UTC) from 1h bars; only buckets with all four 1h bars."""
    b = {}
    for i in range(len(t)):
        b.setdefault(t[i] // H4_MS * H4_MS, []).append(i)
    ot, oo, oh, ol, oc = [], [], [], [], []
    for k in sorted(b):
        idx = b[k]
        if len(idx) != 4 or [t[i] for i in idx] != [k + j * 3_600_000 for j in range(4)]:
            continue
        ot.append(k)
        oo.append(o[idx[0]])
        oh.append(max(h[i] for i in idx))
        ol.append(min(l[i] for i in idx))
        oc.append(c[idx[-1]])
    return ot, oo, oh, ol, oc


# ---- context rows -------------------------------------------------------------------------------------------------

def _zones_str(zs):
    return ";".join("%s:%.10g:%.10g" % (z["kind"], z["lo"], z["hi"]) for z in zs)


def parse_zones(s):
    out = []
    for part in (s or "").split(";"):
        if part:
            k, lo, hi = part.split(":")
            out.append((k, float(lo), float(hi)))
    return out


def build_daily_rows(t, o, h, l, c, v, p=None):
    """One row per CLOSED 1d bar (OURS impl. of KR-L10 trend, KR-Q01 BBWP, KR-S02 RSI zones, KR-Z zones, KR-R01 range).
    Row at index i is a function of bars[0..i] only; `available_at` = close + LATENCY_MS."""
    p = p or kc.load_params()
    n = len(t)
    ts = kc.trend_state(h, l, c, p["zone_k"], p["swing_tol"])
    wt, wo, wh, wl, wc = weekly_from_daily(t, o, h, l, c)
    wts = kc.trend_state(wh, wl, wc, p["zone_k"], p["swing_tol"])
    wclose = [x + WEEK_MS for x in wt]
    bb = kc.bbwp(c, p["bbwp_basis"], p["bbwp_lookback"], p["bbwp_mult"])
    rs = kc.rsi(c, p["rsi_period"])
    atr = atr_sma(h, l, c, ATR_N)
    sma = naive_trend_sma(c)
    ret = naive_trend_ret(c)
    sw = kc.swings(h, l, p["zone_k"])
    ratio = kc.vol_ratio(v, p["vol_sma"])
    rows = []
    for i in range(n):
        close_ms = t[i] + DAY_MS
        wi = bisect.bisect_right(wclose, close_ms) - 1          # last 1w bar closed at or before this 1d close
        zs = kc.zones_from(sw, h, l, c, ratio, i, p)
        rg = kc.range_state(h, l, c, i, p)
        rows.append({
            "open_ms": t[i], "available_at": close_ms + LATENCY_MS,
            "trend_1d_ours": trend_code(ts[i]["state"]),
            "trend_1w_ours": trend_code(wts[wi]["state"]) if wi >= 0 else None,
            "naive_trend_sma200": sma[i], "naive_trend_ret20": ret[i],
            "bbwp_1d_ours": bb[i], "rsi_1d_ours": rs[i], "rsi_zone_1d_ours": kc.rsi_zone(rs[i], p["rsi_bull"], p["rsi_bear"]),
            "atr14_1d": atr[i], "close_1d": c[i],
            "zones_ours": _zones_str(zs),
            "range_top_ours": rg["top"] if rg else None, "range_bottom_ours": rg["bottom"] if rg else None,
        })
    return rows


def build_h4_rows(t, o, h, l, c, p=None):
    """One row per CLOSED 4h bar: BBWP_4h (OURS tf, REVIEW_OPUS F6), min of the previous 6 BBWP values, 6-bar price direction."""
    p = p or kc.load_params()
    bb = kc.bbwp(c, p["bbwp_basis"], p["bbwp_lookback"], p["bbwp_mult"])
    rows = []
    for i in range(len(t)):
        prev = [x for x in bb[max(0, i - FRESH_LOOKBACK):i] if x is not None]
        full = i >= FRESH_LOOKBACK and len(prev) == FRESH_LOOKBACK
        rows.append({
            "open_ms": t[i], "available_at": t[i] + H4_MS + LATENCY_MS,
            "bbwp_4h_ours": bb[i], "bbwp_4h_min6_ours": min(prev) if full else None,
            "exp_dir_4h_ours": _sign(c[i] - c[i - FRESH_LOOKBACK]) if i >= FRESH_LOOKBACK else None,
            "close_4h": c[i],
        })
    return rows


# ---- the join -----------------------------------------------------------------------------------------------------

_KEY_CACHE = {}


def availability_keys(rows):
    """available_at list of `rows`, cached by object identity (rows lists are built once and never mutated)."""
    k = id(rows)
    hit = _KEY_CACHE.get(k)
    if hit is None or hit[0] is not rows or len(hit[1]) != len(rows):
        hit = (rows, [r["available_at"] for r in rows])
        _KEY_CACHE[k] = hit
    return hit[1]


def join_row(rows, decision_ts, availability=None):
    """Latest row with available_at < decision_ts (strict), else None. `rows` sorted by available_at.
    `availability` is for tests only: a list of the keys to bisect on (default: the rows' available_at). Passing bar-open keys
    reproduces the leaking join that the point-in-time check must catch."""
    keys = availability if availability is not None else availability_keys(rows)
    i = bisect.bisect_left(keys, decision_ts) - 1
    return rows[i] if i >= 0 else None


def check_point_in_time(pairs):
    """pairs: iterable of (decision_ts, row_or_None). Returns the list of violations (empty = PASS).
    A violation is a row whose available_at is not strictly before decision_ts (planted-leak lint, PRE_REG s2.4)."""
    bad = []
    for dts, r in pairs:
        if r is not None and not r["available_at"] < dts:
            bad.append((dts, r["open_ms"], r["available_at"]))
    return bad


# ---- the three dimensions -----------------------------------------------------------------------------------------

def d1_direction(side, trend_1d, trend_1w):
    """+1 both agree with the event side (side = +1 long / -1 short); 0 one agrees and the other is range, or both range;
    -1 any disagrees. None when a trend is unavailable (not usable)."""
    if trend_1d is None or trend_1w is None:
        return None
    a, b = trend_1d * side, trend_1w * side
    if a < 0 or b < 0:
        return -1
    if a > 0 and b > 0:
        return 1
    return 0


FADE, BREAKOUT = "fade", "breakout"


def d2_regime(event_type, side, bbwp_4h, bbwp_min6, exp_dir, bbwp_high=85):
    """Per event, from the 4h expansion relative to the event side (design s9.2). EXH = BBWP_4h >= bbwp_high and the expansion
    ran against the event side (a fade has room); FRESH = BBWP_4h rose from <= 30 within 6 bars to > 50 (a new expansion).
    FADE: +1 EXH, -1 FRESH (any direction: no fade into a new expansion). BREAKOUT: +1 only for FRESH in the event direction
    (exp_dir == side); -1 for EXH or for FRESH against the event side. Both or neither: 0. None when a field is missing (OURS)."""
    if bbwp_4h is None or exp_dir is None:
        return None
    exh = bbwp_4h >= bbwp_high and exp_dir == -side
    fresh = bbwp_min6 is not None and bbwp_min6 <= FRESH_FROM and bbwp_4h > FRESH_TO
    fresh_with = fresh and exp_dir == side
    if exh == fresh:
        return 0
    if event_type == FADE:
        return 1 if exh else -1
    return 1 if fresh_with else -1


def d3_location(side, price, zones, atr, top, bottom, near_atr=Z_NEAR_ATR, edge=EDGE_FRAC):
    """+1 within near_atr x ATR14(1d) of a ranked zone on the correct side (long: support 'L', short: resistance 'H') or in the
    range's edge on that side; -1 in the middle third of the daily range (no man's land) when not +1; 0 otherwise."""
    if atr is None or atr <= 0 or price is None:
        return None
    want = "L" if side > 0 else "H"
    for kind, lo, hi in zones:
        if kind != want:
            continue
        dist = 0.0 if lo <= price <= hi else min(abs(price - lo), abs(price - hi))
        if dist <= near_atr * atr:
            return 1
    if top is not None and bottom is not None and top > bottom:
        pos = (price - bottom) / (top - bottom)
        if (side > 0 and pos <= edge + 1e-9) or (side < 0 and pos >= 1 - edge - 1e-9):
            return 1
        if MID_LO <= pos <= MID_HI:
            return -1
    return 0


# ---- statistics that need no outcome ------------------------------------------------------------------------------

def z_holm(m):
    """Phi^-1(1 - 0.05/(2m)) by bisection on erfc (same definition as scripts/dev/prereg_gate.py)."""
    target = 0.05 / m
    lo, hi = 0.0, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if math.erfc(mid / math.sqrt(2)) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def mde_slope(n, weeks, sd_s, sd_r=1.5, rho=0.1, m=1, power_z=0.84):
    """Minimum detectable slope (R per S unit), week-clustered: (z_holm(m) + 0.84) * sd_r * sqrt(deff) / (sqrt(n) * sd_s),
    deff = 1 + (n/weeks - 1) * rho. sd_r = 1.5 R and rho = 0.1 are OURS (no outcome is read here; sd_r from
    context_factors_2026-10-16/COUNTS_DEV_EXT.md n_needed line, rho a conservative guess)."""
    if n <= 0 or weeks <= 0 or sd_s <= 0:
        return None
    deff = 1 + (n / weeks - 1) * rho
    return (z_holm(m) + power_z) * sd_r * math.sqrt(deff) / (math.sqrt(n) * sd_s)


def mde_mean(n, weeks, sd_r=1.5, rho=0.1, m=1, power_z=0.84):
    """MDE of a mean R in a cell, week-clustered, same conventions as mde_slope."""
    if n <= 0 or weeks <= 0:
        return None
    deff = 1 + (n / weeks - 1) * rho
    return (z_holm(m) + power_z) * sd_r * math.sqrt(deff) / math.sqrt(n)