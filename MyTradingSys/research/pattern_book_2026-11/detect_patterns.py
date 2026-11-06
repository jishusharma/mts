"""MTS pattern book detector (2026-11): chart patterns, candlesticks and trendlines on BTCUSDT bars.

Definitions follow PATTERN_BOOK.md (Edwards & Magee / Bulkowski / Nison shapes); every threshold below is OURS unless a
comment says SOURCED. This is a detector for the operator's eye and the testnet watch list, not a backtest: no result here
is a trading edge. Bars are dicts {t,o,h,l,c,v} of CLOSED bars (t = open time ms).

Causality: a pivot is only confirmed `conf` bars after it printed (zigzag retrace), and every pattern status is computed from
bars up to the last bar given, never beyond it.
Geometry is done in log price (y = ln p), so lines and tolerances mean the same on a 2015 chart at 200 USD and a 2026 chart
at 75,000 USD. Targets are measured in price (linear), as the published measuring rules are.
"""
import csv
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
DATA = HERE / "data"
HISTORY = HERE.parent / "btc_cycles_2026-11" / "btc_daily.csv"

TFS = ("1h", "4h", "1d", "1w")
# zigzag scales per timeframe: swing = a retrace of `mult` x ATR% (OURS). Several scales = minor and major structure.
SCALES = {"1h": (3.0, 6.0), "4h": (3.0, 6.0), "1d": (2.0, 3.0, 6.0, 12.0), "1w": (2.0, 3.0, 5.0)}
# how many bars back a pattern may have ended / broken out and still count as "active now" (OURS)
RECENT = {"1h": 48, "4h": 30, "1d": 20, "1w": 8}

P = {
    "dt_depth_atr": 1.5,      # valley between the two extremes at least this many ATR% deep
    "dt_tol_frac": 0.40,      # extremes within 40 % of the valley depth of each other (log) ...
    "dt_abs_tol": 0.15,       # ... and never more than 15 % apart
    "min_sep": 6,             # bars between the two extremes
    "expire_mult": 3.0,       # an unconfirmed double top/bottom expires after 3 x its width
    "hs_lo": 0.35, "hs_hi": 0.90,   # shoulder height as a fraction of head height above the neckline
    "hs_sym": 0.35,           # shoulders differ by at most 35 % of head height
    "fake_n": 3,              # a break that closes back inside within 3 bars ...
    "fake_exc": 1.0,          # ... after an excursion smaller than 1 ATR% is a fakeout (a bigger one that returns is a pullback)
    "hmax_atr": 20.0, "hmax_abs": 0.5,   # a consolidation is at most 20 ATR% (and 50 % log) tall; taller = a trend leg, not a pattern
    "touch_tol": 0.35,        # a pivot touches a boundary within 0.35 ATR%
    "flat": 0.20, "conv": 0.75, "par_hi": 1.33,
    "pole_atr": 4.0, "pole_ret": 0.5, "flag_len": 2.0,
}


# ---------------------------------------------------------------- data
def load_csv(tf):
    rows = []
    with open(DATA / f"BTCUSDT_{tf}.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({"t": int(r["t"]), "o": float(r["o"]), "h": float(r["h"]), "l": float(r["l"]),
                         "c": float(r["c"]), "v": float(r["v"])})
    return rows


def load_history():
    """2010..now daily from btc_cycles_2026-11/btc_daily.csv. Before 2017-08-17 only one price per day (h=l=c, o=previous close)."""
    import datetime as dt
    rows, pc = [], None
    with open(HISTORY, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = int(dt.datetime.fromisoformat(r["date"]).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
            h, l, c = float(r["high"]), float(r["low"]), float(r["close"])
            if l <= 0:
                continue
            rows.append({"t": t, "o": pc if pc else c, "h": h, "l": l, "c": c, "v": 0.0})
            pc = c
    return rows


def tr(bars, i):
    pc = bars[i - 1]["c"]
    return max(bars[i]["h"] - bars[i]["l"], abs(bars[i]["h"] - pc), abs(bars[i]["l"] - pc))


def atr_pct(bars, n=14):
    """ATR (SMA of true range, n bars) as a fraction of the close; None for the first n bars."""
    out = [None] * len(bars)
    for i in range(n, len(bars)):
        out[i] = sum(tr(bars, j) for j in range(i - n + 1, i + 1)) / n / bars[i]["c"]
    return out


def _atr_at(atrp, i):
    for j in range(i, -1, -1):
        if atrp[j] is not None:
            return atrp[j]
    for v in atrp:
        if v is not None:
            return v
    return 0.02


# ---------------------------------------------------------------- pivots
def swings(bars, mult, atrp=None):
    """ATR zigzag in log price. Returns (pivots, provisional). pivot = {i, price, kind 'H'|'L', conf}; wick prices.
    A pivot is confirmed when price retraces mult x ATR% from the running extreme; `conf` is that bar's index."""
    n = len(bars)
    atrp = atrp or atr_pct(bars)
    if n < 20:
        return [], None
    piv, mode = [], None
    hi, lo = (0, bars[0]["h"]), (0, bars[0]["l"])
    for i in range(1, n):
        b = bars[i]
        thr = mult * _atr_at(atrp, i)
        new_hi, new_lo = b["h"] > hi[1], b["l"] < lo[1]
        # a bar that extends the tracked extreme counts as continuation: the order of its own high and low is unknown
        if mode in (None, "up") and not new_hi and math.log(hi[1] / b["l"]) >= thr and mode != "down" and                 (mode == "up" or hi[0] < i):
            piv.append({"i": hi[0], "price": hi[1], "kind": "H", "conf": i})
            mode, lo, hi = "down", (i, b["l"]), (i, b["h"])
            continue
        if mode in (None, "down") and not new_lo and math.log(b["h"] / lo[1]) >= thr and                 (mode == "down" or lo[0] < i):
            piv.append({"i": lo[0], "price": lo[1], "kind": "L", "conf": i})
            mode, hi, lo = "up", (i, b["h"]), (i, b["l"])
            continue
        if new_hi:
            hi = (i, b["h"])
        if new_lo:
            lo = (i, b["l"])
    prov = None
    if mode == "up":
        prov = {"i": hi[0], "price": hi[1], "kind": "H", "conf": None}
    elif mode == "down":
        prov = {"i": lo[0], "price": lo[1], "kind": "L", "conf": None}
    return piv, prov


# ---------------------------------------------------------------- helpers
def line_at(ln, i):
    """Log-linear line through (i1,p1),(i2,p2) evaluated at bar i."""
    f = (i - ln["i1"]) / (ln["i2"] - ln["i1"])
    return math.exp(math.log(ln["p1"]) + (math.log(ln["p2"]) - math.log(ln["p1"])) * f)


def _pt(bars, i, price, role):
    return {"i": i, "t": bars[i]["t"], "price": price, "role": role}


def _rec(pattern, tf, scale, bias, status, bars, **kw):
    r = {"pattern": pattern, "tf": tf, "scale": scale, "bias": bias, "status": status, "points": [], "lines": [],
         "neck": None, "trigger": None, "target": None, "invalid": None, "confirm_i": None, "start_i": None,
         "end_i": None, "note": ""}
    r.update(kw)
    return r


def break_after(bars, i0, up_fn, lo_fn, fake_n, exc_thr):
    """Scan bars after i0 against boundary functions (None = no boundary on that side). Returns
    (direction 'up'|'down'|None, break_i, fakeout bool). Fakeout = within fake_n bars a close is back inside AND the excursion
    beyond the boundary stayed under exc_thr (log); a bigger excursion that returns is a pullback, not a fakeout."""
    for i in range(i0 + 1, len(bars)):
        c = bars[i]["c"]
        u = up_fn(i) if up_fn else None
        l = lo_fn(i) if lo_fn else None
        d = "up" if (u is not None and c > u) else "down" if (l is not None and c < l) else None
        if d:
            exc = abs(math.log(c / (u if d == "up" else l)))
            fake = False
            for j in range(i + 1, min(len(bars), i + 1 + fake_n)):
                u2 = up_fn(j) if up_fn else None
                l2 = lo_fn(j) if lo_fn else None
                cj = bars[j]["c"]
                if (d == "up" and u2 is not None and cj <= u2) or (d == "down" and l2 is not None and cj >= l2):
                    fake = exc < exc_thr
                    break
                exc = max(exc, abs(math.log(cj / (u2 if d == "up" else l2))))
            return d, i, fake
    return None, None, False


def fake_after(bars, conf, level_fn, s, exc_thr):
    """Neckline break at bar conf (s=+1 break down, s=-1 break up). Returns (fake, back_i): fake is True when a close is back
    across the neckline within fake_n bars after an excursion smaller than exc_thr (log); back_i is that bar."""
    def exc(i):
        return s * math.log(level_fn(i) / bars[i]["c"])
    mx = exc(conf)
    for j in range(conf + 1, min(len(bars), conf + 1 + P["fake_n"])):
        if exc(j) <= 0:
            return mx < exc_thr, j
        mx = max(mx, exc(j))
    return False, None


def resolve_neck(bars, start, neck_fn, extreme, s, exc_thr, horizon):
    """Walk bars from `start`: returns (status, confirm_i, fakes). A close beyond `extreme` first = failed; a close through the
    neckline = confirmed unless it is a fakeout (then keep looking: the pattern may still break for real); `horizon` bars
    without a confirmation = expired. Status 'forming' while neither has happened and the horizon is not over."""
    n, fakes, i = len(bars), 0, start
    while i < n:
        c = bars[i]["c"]
        if i - start > horizon:
            return "expired", None, fakes
        if s * (c - extreme) > 0:
            return "failed", None, fakes
        if s * (neck_fn(i) - c) > 0:
            fk, back = fake_after(bars, i, neck_fn, s, exc_thr)
            if not fk:
                return "confirmed", i, fakes
            fakes += 1
            i = back + 1
            continue
        i += 1
    return "forming", None, fakes


def measured_target(neck, top, s):
    """Edwards & Magee measured move: neckline -/+ the pattern height. Linear, unless that leaves the chart (a huge pattern):
    then the same percentage move (log). Returns (target, method)."""
    h = abs(top - neck)
    lin = neck - s * h
    if lin > 0.4 * neck or s == -1 and h < neck:
        return lin, "linear"
    return neck * (neck / top) ** s if s == 1 else neck * (neck / top), "log"


# ---------------------------------------------------------------- double top / bottom
def double_tops(bars, piv, s, tf, scale, atrp):
    """s=+1 double top (H L H), s=-1 double bottom (L H L). Neckline = the valley between. Confirmed by a close through it."""
    ek, vk = ("H", "L") if s == 1 else ("L", "H")
    name, bias = ("double_top", "bear") if s == 1 else ("double_bottom", "bull")
    out = []
    n = len(bars)
    for j in range(2, len(piv)):
        p1, pv, p2 = piv[j - 2], piv[j - 1], piv[j]
        if not (p1["kind"] == ek and pv["kind"] == vk and p2["kind"] == ek):
            continue
        e_less = min(p1["price"], p2["price"]) if s == 1 else max(p1["price"], p2["price"])
        top = max(p1["price"], p2["price"]) if s == 1 else min(p1["price"], p2["price"])
        depth = s * math.log(e_less / pv["price"])
        diff = abs(math.log(p2["price"] / p1["price"]))
        a = _atr_at(atrp, p2["i"])
        if depth < P["dt_depth_atr"] * a or diff > min(P["dt_tol_frac"] * depth, P["dt_abs_tol"]):
            continue
        if p2["i"] - p1["i"] < P["min_sep"]:
            continue
        if j >= 3 and piv[j - 3]["kind"] == vk and s * math.log(p1["price"] / piv[j - 3]["price"]) < 0.5 * depth:
            continue   # nothing to reverse: the run into the first extreme must be at least half the valley depth
        neck = pv["price"]
        width = p2["i"] - p1["i"]
        status, conf, fakes = resolve_neck(bars, p2["i"] + 1, lambda i: neck, top, s, P["fake_exc"] * a,
                                           P["expire_mult"] * width)
        target, how = measured_target(neck, top, s)
        if conf is not None:
            reach = "l" if s == 1 else "h"
            for i in range(conf + 1, min(n, conf + 1 + int(P["expire_mult"] * width))):
                if s * (bars[i]["c"] - top) > 0:
                    status = "failed"
                    break
                if s * (bars[i][reach] - target) <= 0:
                    status = "target_hit"
                    break
        out.append(_rec(name, tf, scale, bias, status, bars,
                        points=[_pt(bars, p1["i"], p1["price"], "peak1" if s == 1 else "low1"),
                                _pt(bars, pv["i"], pv["price"], "neckline"),
                                _pt(bars, p2["i"], p2["price"], "peak2" if s == 1 else "low2")],
                        neck=neck, trigger=neck, target=target, invalid=top, confirm_i=conf,
                        start_i=p1["i"], end_i=conf if conf is not None else p2["i"],
                        note=f"extremes {diff * 100:.1f}% apart, valley {depth * 100:.0f}% deep, target by {how} measure, {fakes} fakeout(s) first"))
    return out


# ---------------------------------------------------------------- head and shoulders
def head_shoulders(bars, piv, s, tf, scale, atrp):
    ek, vk = ("H", "L") if s == 1 else ("L", "H")
    name, bias = ("head_shoulders_top", "bear") if s == 1 else ("head_shoulders_bottom", "bull")
    out, n = [], len(bars)
    for j in range(4, len(piv)):
        e1, v1, e2, v2, e3 = piv[j - 4:j + 1]
        if [e1["kind"], v1["kind"], e2["kind"], v2["kind"], e3["kind"]] != [ek, vk, ek, vk, ek]:
            continue
        if s * math.log(e2["price"] / e1["price"]) <= 0 or s * math.log(e2["price"] / e3["price"]) <= 0:
            continue
        base = math.sqrt(v1["price"] * v2["price"])
        h = s * math.log(e2["price"] / base)
        s1, s3 = s * math.log(e1["price"] / base), s * math.log(e3["price"] / base)
        if h < P["dt_depth_atr"] * _atr_at(atrp, e3["i"]):
            continue
        if not (P["hs_lo"] * h <= s1 <= P["hs_hi"] * h and P["hs_lo"] * h <= s3 <= P["hs_hi"] * h):
            continue
        if abs(s1 - s3) > P["hs_sym"] * h:
            continue
        w1, w2 = e2["i"] - e1["i"], e3["i"] - e2["i"]
        if max(w1, w2) > 3 * min(w1, w2):
            continue
        neck_ln = {"i1": v1["i"], "p1": v1["price"], "i2": v2["i"], "p2": v2["price"]}
        neck_fn = lambda i: line_at(neck_ln, i)   # noqa: E731
        status, conf, fakes = resolve_neck(bars, e3["i"] + 1, neck_fn, e2["price"], s,
                                           P["fake_exc"] * _atr_at(atrp, e3["i"]), P["expire_mult"] * (e3["i"] - e1["i"]))
        head_h = abs(e2["price"] - neck_fn(e2["i"]))
        tgt = None
        if conf is not None:
            tgt = neck_fn(conf) - s * head_h
            if tgt <= 0.3 * neck_fn(conf):
                tgt = neck_fn(conf) * (neck_fn(conf) / e2["price"]) ** s if s == 1 else neck_fn(conf) * (neck_fn(conf) / e2["price"])
            reach = "l" if s == 1 else "h"
            for i in range(conf + 1, min(n, conf + 1 + 3 * (e3["i"] - e1["i"]))):
                if s * (bars[i]["c"] - e2["price"]) > 0:
                    status = "failed"
                    break
                if s * (bars[i][reach] - tgt) <= 0:
                    status = "target_hit"
                    break
        nk_now = line_at(neck_ln, n - 1)
        out.append(_rec(name, tf, scale, bias, status, bars,
                        points=[_pt(bars, e1["i"], e1["price"], "left shoulder"), _pt(bars, v1["i"], v1["price"], "neck1"),
                                _pt(bars, e2["i"], e2["price"], "head"), _pt(bars, v2["i"], v2["price"], "neck2"),
                                _pt(bars, e3["i"], e3["price"], "right shoulder")],
                        lines=[dict(neck_ln, name="neckline", ext=min(n - 1, (conf or e3["i"]) + max(w1, w2)))],
                        neck=nk_now, trigger=nk_now, target=tgt if tgt is not None else nk_now - s * head_h,
                        invalid=e2["price"], confirm_i=conf, start_i=e1["i"], end_i=conf if conf is not None else e3["i"],
                        note=f"head {h * 100:.0f}% above neckline; stop-plan: beyond right shoulder {e3['price']:.0f}"))
    return out


# ---------------------------------------------------------------- boundaries, triangles, wedges, rectangles, flags
def fit_boundary(bars, pivs, side, tol):
    """Best straight (log) line through two of `pivs` (all same kind) with no pivot poking out by more than tol and no close beyond
    it from the first anchor to the last pivot of the window. Prefers more touches, then the longer line. None if no line."""
    best, bkey = None, None
    sgn = 1 if side == "upper" else -1
    for x in range(len(pivs)):
        for y in range(x + 1, len(pivs)):
            a, b = pivs[x], pivs[y]
            ln = {"i1": a["i"], "p1": a["price"], "i2": b["i"], "p2": b["price"]}
            ok, touches = True, 0
            for p in pivs:
                if p["i"] < a["i"]:
                    continue
                d = sgn * math.log(p["price"] / line_at(ln, p["i"]))
                if d > tol:
                    ok = False
                    break
                if d >= -tol:
                    touches += 1
            if not ok:
                continue
            for i in range(a["i"], pivs[-1]["i"] + 1):
                if sgn * math.log(bars[i]["c"] / line_at(ln, i)) > 0:
                    ok = False
                    break
            if not ok:
                continue
            key = (touches, b["i"] - a["i"])
            if bkey is None or key > bkey:
                best, bkey = dict(ln, touches=touches), key
    return best


def consolidations(bars, piv, tf, scale, atrp):
    """Triangles, wedges, rectangles, flags and pennants from windows of 4..8 pivots ending at, or just before, the last pivot."""
    out, n = [], len(bars)
    for end_off in range(0, 3):
        for size in range(4, 9):
            hi_idx = len(piv) - end_off
            lo_idx = hi_idx - size
            if lo_idx < 1:
                continue
            w = piv[lo_idx:hi_idx]
            hs = [p for p in w if p["kind"] == "H"]
            ls = [p for p in w if p["kind"] == "L"]
            if len(hs) < 2 or len(ls) < 2:
                continue
            a = _atr_at(atrp, w[-1]["i"])
            tol = P["touch_tol"] * a * 2
            up, lo = fit_boundary(bars, hs, "upper", tol), fit_boundary(bars, ls, "lower", tol)
            if not up or not lo:
                continue
            i0, i1 = w[0]["i"], w[-1]["i"]
            if i1 - i0 < 8:
                continue
            yu = lambda i: math.log(line_at(up, i))   # noqa: E731
            yl = lambda i: math.log(line_at(lo, i))   # noqa: E731
            w0, w1 = yu(i0) - yl(i0), yu(i1) - yl(i1)
            if w0 <= 0 or w1 <= 0 or w0 > min(P["hmax_atr"] * a, P["hmax_abs"]):
                continue
            span = i1 - i0
            du = (yu(i1) - yu(i0)) / max(w0, w1)
            dl = (yl(i1) - yl(i0)) / max(w0, w1)
            flat = lambda d: abs(d) <= P["flat"]   # noqa: E731
            conv = w1 <= P["conv"] * w0
            par = P["conv"] < w1 / w0 < P["par_hi"]
            kind = bias = None
            if par and flat(du) and flat(dl):
                kind, bias = "rectangle", "neutral"
            elif conv and flat(du) and dl > P["flat"]:
                kind, bias = "ascending_triangle", "bull"
            elif conv and flat(dl) and du < -P["flat"]:
                kind, bias = "descending_triangle", "bear"
            elif conv and du < -P["flat"] and dl > P["flat"]:
                kind, bias = "symmetrical_triangle", "neutral"
            elif conv and du > P["flat"] and dl > P["flat"]:
                kind, bias = "rising_wedge", "bear"
            elif conv and du < -P["flat"] and dl < -P["flat"]:
                kind, bias = "falling_wedge", "bull"
            elif par and du < -P["flat"] and dl < -P["flat"]:
                kind, bias = "channel_down", "neutral"
            elif par and du > P["flat"] and dl > P["flat"]:
                kind, bias = "channel_up", "neutral"
            if not kind:
                continue
            note = ""
            # flag / pennant: a sharp pole just before the window, then a small counter-trend (or converging) body
            p0 = piv[lo_idx - 1]
            pole_kind = None
            if w[0]["kind"] == "H" and p0["kind"] == "L":
                pole_kind = "bull"
            elif w[0]["kind"] == "L" and p0["kind"] == "H":
                pole_kind = "bear"
            if pole_kind:
                pole = abs(math.log(w[0]["price"] / p0["price"]))
                plen = w[0]["i"] - p0["i"]
                against = (pole_kind == "bull" and du <= P["flat"] and dl <= P["flat"] + 0.1) or \
                          (pole_kind == "bear" and du >= -P["flat"] - 0.1 and dl >= -P["flat"])
                if pole >= P["pole_atr"] * a and w0 <= 0.5 * pole and span <= P["flag_len"] * max(plen, 4) \
                        and (par or conv) and against and kind not in ("ascending_triangle", "descending_triangle"):
                    retr = (math.log(w[0]["price"] / min(x["price"] for x in ls)) if pole_kind == "bull"
                            else math.log(max(x["price"] for x in hs) / w[0]["price"]))
                    if retr <= P["pole_ret"] * pole:
                        kind = ("bull_" if pole_kind == "bull" else "bear_") + ("flag" if par else "pennant")
                        bias = pole_kind
                        note = f"pole {pole * 100:.0f}% in {plen} bars"
            # status after the window
            ufn = lambda i: line_at(up, i)   # noqa: E731
            lfn = lambda i: line_at(lo, i)   # noqa: E731
            d, bi, fake = break_after(bars, i1, ufn, lfn, P["fake_n"], P["fake_exc"] * a)
            if d:
                status = "fakeout" if fake else f"breakout_{d}"
            elif conv and w1 > 0 and (n - 1 - i1) > 2 * span:
                status = "expired"
            elif (n - 1 - i1) > 3 * span:
                status = "expired"
            else:
                status = "forming"
            if bi is not None and n - 1 - bi > RECENT[tf] * 2:
                continue
            if bi is None and n - 1 - i1 > RECENT[tf] * 2:
                continue
            h_price = line_at(up, i0) - line_at(lo, i0)
            now_u, now_l = line_at(up, n - 1), line_at(lo, n - 1)
            if kind.endswith("flag") or kind.endswith("pennant"):
                pole_px = abs(w[0]["price"] - p0["price"])
                if bias == "bull":
                    trig, tgt, inv = now_u, now_u + pole_px, min(x["price"] for x in ls)
                else:
                    trig, tgt, inv = now_l, now_l - pole_px, max(x["price"] for x in hs)
            elif bias == "bull":
                trig, tgt, inv = now_u, now_u + h_price, now_l
            elif bias == "bear":
                trig, tgt, inv = now_l, now_l - h_price, now_u
            else:
                trig, tgt, inv = (now_u, now_u + h_price, now_l)   # neutral: long trigger shown; short side = now_l - h_price
            if d and not fake:   # already broken out: report the realised side (trigger = the line at the break bar)
                if d == "up":
                    base_u = ufn(bi)
                    trig, inv = base_u, lfn(bi)
                    tgt = base_u + (abs(w[0]["price"] - p0["price"]) if kind.endswith(("flag", "pennant")) else h_price)
                else:
                    base_l = lfn(bi)
                    trig, inv = base_l, ufn(bi)
                    tgt = base_l - (abs(w[0]["price"] - p0["price"]) if kind.endswith(("flag", "pennant")) else h_price)
            ext = min(n - 1, (bi if bi is not None else i1) + max(4, span // 4))
            out.append(_rec(kind, tf, scale, bias, status, bars,
                            points=[_pt(bars, p["i"], p["price"], "H" if p["kind"] == "H" else "L") for p in w],
                            lines=[dict(up, name="upper", ext=ext), dict(lo, name="lower", ext=ext)],
                            trigger=trig, target=tgt, invalid=inv, confirm_i=bi, start_i=i0,
                            end_i=bi if bi is not None else i1,
                            note=(note + f" touches {up['touches']}+{lo['touches']}; height {h_price:.0f}").strip(),
                            short_target=(now_l - h_price) if bias == "neutral" else None, short_trigger=now_l if bias == "neutral" else None))
    # keep the best candidate per (pattern, status class): most touches, then most recent end
    best = {}
    for r in out:
        k = (r["pattern"], r["status"].startswith("breakout"), r["status"])
        sc = (sum(l["touches"] for l in r["lines"]), r["end_i"])
        if k not in best or sc > best[k][0]:
            best[k] = (sc, r)
    return [v[1] for v in best.values()]


# ---------------------------------------------------------------- all chart patterns on one timeframe
def detect_chart_patterns(bars, tf, scales=None):
    atrp = atr_pct(bars)
    res = []
    for sc in (scales or SCALES[tf]):
        piv, _prov = swings(bars, sc, atrp)
        for s in (1, -1):
            res += double_tops(bars, piv, s, tf, sc, atrp)
            res += head_shoulders(bars, piv, s, tf, sc, atrp)
        res += consolidations(bars, piv, tf, sc, atrp)
    seen, uniq = set(), []
    for r in res:   # the same shape found at two scales keeps the larger scale
        key = (r["pattern"], r["start_i"], r["end_i"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def is_active(r, n, tf):
    """Active now: still forming, confirmed/broken out recently, not failed / expired / target already hit."""
    if r["status"] in ("failed", "expired", "target_hit", "fakeout"):
        return False
    if r["status"] == "forming":
        return n - 1 - r["end_i"] <= RECENT[tf] * 2
    return r["confirm_i"] is not None and n - 1 - r["confirm_i"] <= RECENT[tf]


# ---------------------------------------------------------------- candlesticks (Nison shapes; context rule OURS)
def _parts(b):
    rng = b["h"] - b["l"]
    body = abs(b["c"] - b["o"])
    top, bot = max(b["o"], b["c"]), min(b["o"], b["c"])
    return rng, body, b["h"] - top, bot - b["l"]


def trend_into(bars, i, atrp, n=10):
    """Prior trend in ATR units over the n closes before bar i: >= +1 up, <= -1 down, else flat (OURS)."""
    if i < n + 1 or atrp[i] is None:
        return "flat"
    x = math.log(bars[i - 1]["c"] / bars[i - 1 - n]["c"]) / atrp[i]
    return "up" if x >= 1.0 else "down" if x <= -1.0 else "flat"


def candle_patterns(bars):
    """List of {i, name, bias, trend_ok}. i = the last bar of the pattern; trend_ok = the prior-trend context the book requires."""
    atrp = atr_pct(bars)
    ev = []
    for i in range(12, len(bars)):
        b = bars[i]
        rng, body, up_sh, lo_sh = _parts(b)
        if rng <= 0:
            continue
        tr_ = trend_into(bars, i, atrp)
        green, red = b["c"] > b["o"], b["c"] < b["o"]

        def add(name, bias, ok):
            ev.append({"i": i, "name": name, "bias": bias, "trend_ok": ok})
        if body <= 0.1 * rng:
            add("doji", "neutral", True)
        if lo_sh >= 2 * body and up_sh <= 0.15 * rng and body > 0 and body <= 0.4 * rng:
            add("hammer", "bull", tr_ == "down")
            add("hanging_man", "bear", tr_ == "up")
        if up_sh >= 2 * body and lo_sh <= 0.15 * rng and body > 0 and body <= 0.4 * rng:
            add("shooting_star", "bear", tr_ == "up")
        p = bars[i - 1]
        prng, pbody, _, _ = _parts(p)
        pgreen, pred = p["c"] > p["o"], p["c"] < p["o"]
        if pred and green and b["o"] <= p["c"] and b["c"] >= p["o"] and body > pbody:
            add("bullish_engulfing", "bull", tr_ == "down")
        if pgreen and red and b["o"] >= p["c"] and b["c"] <= p["o"] and body > pbody:
            add("bearish_engulfing", "bear", tr_ == "up")
        if pred and green and prng > 0 and pbody >= 0.5 * prng and b["o"] <= p["c"] and p["c"] < b["c"] < p["o"] \
                and b["c"] > (p["o"] + p["c"]) / 2:
            add("piercing_line", "bull", tr_ == "down")
        if pgreen and red and prng > 0 and pbody >= 0.5 * prng and b["o"] >= p["c"] and p["o"] < b["c"] < p["c"] \
                and b["c"] < (p["o"] + p["c"]) / 2:
            add("dark_cloud_cover", "bear", tr_ == "up")
        if i >= 2:
            a0 = bars[i - 2]
            r0, b0, _, _ = _parts(a0)
            r1, b1, _, _ = _parts(p)
            if a0["c"] < a0["o"] and r0 > 0 and b0 >= 0.5 * r0 and b1 <= 0.3 * b0 and green \
                    and b["c"] > (a0["o"] + a0["c"]) / 2:
                add("morning_star", "bull", trend_into(bars, i - 1, atrp) == "down")
            if a0["c"] > a0["o"] and r0 > 0 and b0 >= 0.5 * r0 and b1 <= 0.3 * b0 and red \
                    and b["c"] < (a0["o"] + a0["c"]) / 2:
                add("evening_star", "bear", trend_into(bars, i - 1, atrp) == "up")
            c3 = [bars[i - 2], bars[i - 1], b]
            if all(x["c"] > x["o"] for x in c3) and c3[0]["c"] < c3[1]["c"] < c3[2]["c"] \
                    and all(c3[k - 1]["o"] <= c3[k]["o"] <= c3[k - 1]["c"] for k in (1, 2)) \
                    and all(_parts(x)[2] <= 0.3 * max(_parts(x)[1], 1e-9) for x in c3):
                add("three_white_soldiers", "bull", trend_into(bars, i - 2, atrp) != "up")
            if all(x["c"] < x["o"] for x in c3) and c3[0]["c"] > c3[1]["c"] > c3[2]["c"] \
                    and all(c3[k - 1]["c"] <= c3[k]["o"] <= c3[k - 1]["o"] for k in (1, 2)) \
                    and all(_parts(x)[3] <= 0.3 * max(_parts(x)[1], 1e-9) for x in c3):
                add("three_black_crows", "bear", trend_into(bars, i - 2, atrp) != "down")
    return ev


def candle_next_stats(bars, events, need_trend=True):
    """Per pattern: n events and the share whose NEXT close is in the pattern's expected direction (vs this bar's close);
    baseline = share of all bars whose next close is up. Descriptive, no costs, no multiple-testing control (OURS)."""
    n = len(bars)
    up_all = sum(1 for i in range(n - 1) if bars[i + 1]["c"] > bars[i]["c"]) / max(1, n - 1)
    st = {}
    for e in events:
        if e["i"] >= n - 1 or e["bias"] == "neutral" or (need_trend and not e["trend_ok"]):
            continue
        up = bars[e["i"] + 1]["c"] > bars[e["i"]]["c"]
        d = st.setdefault(e["name"], {"n": 0, "hit": 0, "bias": e["bias"]})
        d["n"] += 1
        d["hit"] += 1 if (up if e["bias"] == "bull" else not up) else 0
    out = {k: {"n": v["n"], "rate": v["hit"] / v["n"], "bias": v["bias"]} for k, v in st.items()}
    return out, up_all


# ---------------------------------------------------------------- trendlines
def pivots_fractal(bars, k=3):
    """k-bar fractal pivots on wicks (card: 3-bar lookback). Returns (highs, lows) as {i, price}; a pivot at i is known at i+k."""
    hs, ls = [], []
    for i in range(k, len(bars) - k):
        nb = [bars[j] for j in range(i - k, i + k + 1) if j != i]
        if all(bars[i]["h"] > x["h"] for x in nb):
            hs.append({"i": i, "price": bars[i]["h"]})
        if all(bars[i]["l"] < x["l"] for x in nb):
            ls.append({"i": i, "price": bars[i]["l"]})
    return hs, ls


def strip_trendline(bars, side, k=3, tol=0.002, lookback=6):
    """Live-aid strip rule (card live-aid-trendlines-liquidations-1106): among the last `lookback` fractal pivots of one side,
    the most recent triple whose middle pivot lies within tol (0.2 %) of the line through the outer two = a 3-touch line.
    Else the line through the last two same-side pivots, marked touches=2. Returns None when fewer than two pivots exist or
    the line is already broken by a close. side 'support' (lows) | 'resistance' (highs).
    Fields: slope_pct_per_bar (log slope x 100), value (line price at the last bar), dist_pct = (close - value)/close x 100."""
    hs, ls = pivots_fractal(bars, k)
    pv = (ls if side == "support" else hs)[-lookback:]
    n = len(bars)
    cands = []
    for c in range(len(pv) - 1, 1, -1):
        for a in range(c - 2, -1, -1):
            for m in range(a + 1, c):
                ln = {"i1": pv[a]["i"], "p1": pv[a]["price"], "i2": pv[c]["i"], "p2": pv[c]["price"]}
                if abs(pv[m]["price"] / line_at(ln, pv[m]["i"]) - 1) <= tol:
                    cands.append((3, ln))
        if cands:
            break
    ln, touches = (cands[-1][1], 3) if cands else (None, 2)
    if ln is None and len(pv) >= 2:
        ln = {"i1": pv[-2]["i"], "p1": pv[-2]["price"], "i2": pv[-1]["i"], "p2": pv[-1]["price"]}
    if ln is None or ln["i2"] == ln["i1"]:
        return None
    for i in range(ln["i2"] + 1, n):   # a close through the line kills it
        v = line_at(ln, i)
        if (bars[i]["c"] < v) if side == "support" else (bars[i]["c"] > v):
            return None
    val = line_at(ln, n - 1)
    c = bars[-1]["c"]
    slope = (math.log(ln["p2"]) - math.log(ln["p1"])) / (ln["i2"] - ln["i1"])
    return dict(ln, side=side, touches=touches, value=val, slope_pct_per_bar=slope * 100, dist_pct=(c - val) / c * 100,
                n=n)


def core_trendlines(bars, tf):
    """Nearest live eligible lines from the tested research detector (trendline_core: log, wick, k=3). Returns up to two
    dicts {side, i1,p1,i2,p2, value, dist_pct, arm}: an up-trend support line and a down-trend resistance line."""
    sys.path.insert(0, str(REPO))
    from MyTradingSys.backtest.layers.trendlines.trendline_core import TrendlineDetector
    det = TrendlineDetector(tf=tf, k=3, transform="log", price_arm="wick", max_age=500)
    det.feed([dict(b) for b in bars])
    t = len(bars) - 1
    out = []
    for side in ("support", "resistance"):
        for arm in ("B", "A"):
            ln = det.nearest(side, arm)
            if ln:
                v = det._L(ln, t)
                out.append({"side": side, "i1": ln["ia"], "p1": ln["pa"], "i2": ln["ib"], "p2": ln["pb"], "value": v,
                            "dist_pct": (bars[t]["c"] - v) / bars[t]["c"] * 100, "arm": arm, "thirds": list(ln["thirds"])})
                break
    return out


# ---------------------------------------------------------------- Bible turns (BIBLE.md section 2), found on the daily history
BIBLE_TURNS = (
    ("2021 top", "double_top", "2021-04-14", "2021-11-10"),
    ("2025 top", "double_top", "2025-08-14", "2025-10-06"),
    ("2018-19 bottom", "double_bottom", "2018-12-15", "2019-01-29"),
    ("2022 bottom", "double_bottom", "2022-06-18", "2022-11-21"),
    ("2026 bottom", "double_bottom", "2026-02-06", "2026-07-01"),
)


def find_turn(history, pattern, d1, d2, tol_days=3, scales=(2, 3, 4, 5, 6, 8, 12)):
    """The double top/bottom on `history` (daily bars) whose first and last extreme sit within tol_days of d1 and d2, else None."""
    import datetime as dt
    day = 86400000
    ms = lambda d: int(dt.datetime.fromisoformat(d).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)   # noqa: E731
    t1, t2 = ms(d1), ms(d2)
    atrp = atr_pct(history)
    s = 1 if pattern == "double_top" else -1
    for sc in scales:
        piv, _ = swings(history, sc, atrp)
        for r in double_tops(history, piv, s, "1d", sc, atrp):
            if abs(r["points"][0]["t"] - t1) <= tol_days * day and abs(r["points"][2]["t"] - t2) <= tol_days * day:
                return r
    return None
