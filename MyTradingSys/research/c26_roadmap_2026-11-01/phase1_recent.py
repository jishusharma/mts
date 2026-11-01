"""C26 roadmap, Phase 1 (operator 2026-11-01: understand the recent phases FIRST, then decide how to backtest).

Descriptive only: no P&L, no trade rule, no verdict. This window is the DESIGN set; it never counts as a test.
Window: 2026-07-01 (the 57.8k low) .. now, split at the highest high in it (up phase / down phase).

The roadmap (high side; the low side is the exact mirror):
  H1      = C26 pivot high (highest high of +-16 15m bars), confirmed 16 bars later
  L1      = lowest low between H1 and its retest; needs a pull-back >= 0.8 % (C26)
  retest  = first bar with high within 0.4 % under H1, H1 never exceeded, H1 age <= 72h; held = 4 bars later still
            below H1 and closed below it (C26 decision bar j)
  sweep   = after j, a low under L1 (longs taken) BEFORE H1 is taken
  take-out= after j, first high above H1 (within 72h)
  drop    = after the take-out: closed back under H1 within 4 bars (sweep back), and the move 24h later
All C26 numbers are OURS (C26_PRE_REG.md). New OURS readouts here:
  session (UTC bar open): ASIA 00-07, LONDON 07-13:30, US 13:30-20, LATE 20-24
  OI change L1 -> j: Binance USDT-M BTCUSDT sum_open_interest (5m metrics), last row at or before each bar close
  WaveTrend at H1: wt1 of the H1 bar (layers/wavetrend, LazyBear SOURCED params); OB = wt1 >= 53
  RSI(14) bearish divergence at H1: an earlier C26 pivot high within 72h is lower in price but higher in RSI
  volume node: 72h volume profile before H1 on 15m bars, 0.1 % bins by typical price; HVN = bin in the top 20 % by
               volume; "H1 at HVN" = H1's bin or a neighbour is an HVN; POC distance in %
  overshoot: highest high in the 4h after the take-out, % above H1 (how far a stop above H1 had to be)
Usage: python phase1_recent.py <repo> <cache_dir> [--until 2026-11-01T07:45] [--sim-json FILE] > out.md
  (cache_dir holds public klines/metrics, never committed; --until keeps bars opening at or before that UTC time so a
  re-run reproduces a dated output; --sim-json also writes the simulator result card, sim_desk/results/<id>.json)
"""
import csv, io, json, math, os, sys, urllib.request, zipfile
from bisect import bisect_right
from datetime import datetime, timedelta, timezone

REPO, CACHE = sys.argv[1], sys.argv[2]
_opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
UNTIL = int(datetime.fromisoformat(_opt["--until"]).replace(tzinfo=timezone.utc).timestamp() * 1000) if "--until" in _opt else None
SIM_JSON = _opt.get("--sim-json")
sys.path.insert(0, REPO)
from MyTradingSys.backtest.layers.wavetrend.wavetrend import compute as wt_compute  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

W, PB, NEAR, MAXAGE, CONF = 16, 0.008, 0.004, 288, 4  # C26, OURS
TF = 900000
START = datetime(2026, 7, 1, tzinfo=timezone.utc)
WARM = START - timedelta(days=10)
LOCAL_METRICS = [os.path.join(REPO, "Dumps", "backtest", "raw", "metrics"), "F:/MTS/data/binance_metrics"]


def utc(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc)


def klines():
    path = os.path.join(CACHE, "btc15m_recent.json")
    if os.path.exists(path) and (datetime.now().timestamp() - os.path.getmtime(path)) < 3600:
        return json.load(open(path))
    start, out = int(WARM.timestamp() * 1000), []
    while True:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=1000&startTime=%d" % start
        b = json.loads(urllib.request.urlopen(u, timeout=20).read())
        if not b:
            break
        out += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in b]
        if len(b) < 1000:
            break
        start = b[-1][0] + 1
    json.dump(out, open(path, "w"))
    return out


def metrics_day(day):
    """5m OI rows of one UTC day: local copies first, else the public data.binance.vision daily zip (cached)."""
    name = "BTCUSDT-metrics-%s.csv" % day
    for d in LOCAL_METRICS + [CACHE]:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    u = "https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-%s.zip" % day
    try:
        z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(u, timeout=30).read()))
    except Exception:
        return None
    txt = z.read(z.namelist()[0]).decode("utf-8")
    open(os.path.join(CACHE, name), "w", encoding="utf-8", newline="\n").write(txt)
    return txt


def oi_series(first_ms, last_ms):
    t, v, missing = [], [], []
    d = utc(first_ms).date()
    while d <= utc(last_ms).date():
        txt = metrics_day(d.isoformat())
        if txt is None:
            missing.append(d.isoformat())
        else:
            for r in csv.DictReader(io.StringIO(txt)):
                ts = datetime.strptime(r["create_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                t.append(int(ts.timestamp() * 1000)); v.append(float(r["sum_open_interest"]))
        d += timedelta(days=1)
    z = sorted(zip(t, v))
    return [a for a, _ in z], [b for _, b in z], missing


def session(ms):
    h = utc(ms).hour + utc(ms).minute / 60
    return "ASIA" if h < 7 else "LONDON" if h < 13.5 else "US" if h < 20 else "LATE"


rows = klines()
rows = [r for r in rows if r[0] <= UNTIL] if UNTIL else rows[:-1]  # last bar still open
T = [r[0] for r in rows]; O = [r[1] for r in rows]; H = [r[2] for r in rows]; L = [r[3] for r in rows]
C = [r[4] for r in rows]; V = [r[5] for r in rows]; N = len(rows)
i0 = bisect_right(T, int(START.timestamp() * 1000) - 1)
top_i = max(range(i0, N), key=lambda i: H[i])
WT = [r.wt1 for r in wt_compute([(T[i], H[i], L[i], C[i]) for i in range(N)], TF)]
RSI = rsi_core(C, 14)
OIt, OIv, OI_MISSING = oi_series(T[i0] - 4 * 86400000, T[-1])


def oi_at(close_ms):
    k = bisect_right(OIt, close_ms) - 1
    return OIv[k] if k >= 0 and close_ms - OIt[k] <= 15 * 60000 else None


def vol_node(p, lvl, side):
    lo = max(0, p - 288)
    prof = {}
    for k in range(lo, p):
        b = _bin((H[k] + L[k] + C[k]) / 3)
        prof[b] = prof.get(b, 0) + V[k]
    if not prof:
        return None, None
    cut = sorted(prof.values())[int(0.8 * (len(prof) - 1))]
    hvn = {b for b, v in prof.items() if v >= cut}
    poc = max(prof, key=prof.get)
    lb = _bin(lvl)
    at = any(b in hvn for b in (lb - 1, lb, lb + 1))
    poc_price = BIN ** (poc + 0.5)
    return at, (lvl - poc_price) / lvl * 100 * side


BIN = 1.001  # 0.1 % log bins (OURS)


def _bin(price):
    return int(math.log(price) / math.log(BIN))


def run(side):
    """side +1 = highs (shorts build under a held high), -1 = lows (mirror). Prices mirrored for one code path."""
    Hs = [h if side > 0 else -l for h, l in zip(H, L)]; Ls = [l if side > 0 else -h for h, l in zip(H, L)]
    Cs = [c * side for c in C]
    Rs = [(r if side > 0 else 100 - r) if r is not None else None for r in RSI]
    pivots, events, confirmed = [], [], []
    for i in range(2 * W, N - 1):
        p = i - W
        if Hs[p] == max(Hs[i - 2 * W:i + 1]):
            pivots.append(dict(p=p, lvl=Hs[p], pulled=False, done=False, l1=Ls[p], l1i=p))
            confirmed.append(p)
        for pv in pivots:
            if pv["done"]:
                continue
            if i - pv["p"] > MAXAGE or Hs[i] > pv["lvl"]:
                pv["done"] = True; continue
            if i <= pv["p"] + W:
                if Ls[i] < pv["l1"]:
                    pv["l1"], pv["l1i"] = Ls[i], i
                continue
            if Ls[i] < pv["l1"]:
                pv["l1"], pv["l1i"] = Ls[i], i
            if Ls[i] <= pv["lvl"] - PB * abs(pv["lvl"]):
                pv["pulled"] = True
            if not pv["pulled"]:
                continue
            if Hs[i] >= pv["lvl"] - NEAR * abs(pv["lvl"]):
                pv["done"] = True
                j = i + CONF
                if j >= N or any(Hs[m] > pv["lvl"] for m in range(i, j + 1)) or Cs[j] >= pv["lvl"]:
                    continue
                if T[pv["p"]] < T[i0]:
                    continue
                events.append(dict(pv, i=i, j=j))
        pivots = [pv for pv in pivots if not pv["done"]]
    out = []
    for e in events:
        p, j, lvl, l1 = e["p"], e["j"], e["lvl"], e["l1"]
        sweep = take = None
        for k in range(j + 1, min(N, j + 1 + MAXAGE)):
            if sweep is None and Ls[k] < l1:
                sweep = k
            if Hs[k] > lvl:
                take = k; break
        back = after = over = reach_l1 = None
        if take is not None:
            back = any(Cs[m] < lvl for m in range(take, min(N, take + CONF + 1)))
            after = (C[take + 96] / C[take] - 1) * 100 * side if take + 96 < N else None  # - = fell back after take-out
            over = (max(Hs[take:min(N, take + 16)]) - lvl) / abs(lvl) * 100
            reach_l1 = any(Ls[m] < l1 for m in range(take, min(N, take + 97))) if take + 1 < N else None
        prev = [q for q in confirmed if q < p and p - q <= MAXAGE and Hs[q] < lvl]
        div = None
        if Rs[p] is not None and prev:
            div = any(Rs[q] is not None and Rs[q] > Rs[p] for q in prev)
        oa, ob = oi_at(T[e["l1i"]] + TF), oi_at(T[j] + TF)
        hvn, poc = vol_node(p, abs(lvl), side)
        out.append(dict(
            side="H" if side > 0 else "L", phase="UP" if p <= top_i else "DOWN",
            h1_t=T[p], h1=abs(lvl), age_h=(e["i"] - p) / 4, l1=abs(l1), depth=(lvl - l1) / abs(lvl) * 100,
            j_t=T[j], j_sess=session(T[j]),
            oi=(ob / oa - 1) * 100 if oa and ob else None,
            wt=(WT[p] * side) if WT[p] == WT[p] else None, div=div, hvn=hvn, poc=poc,
            sweep_h=(sweep - j) / 4 if sweep is not None and (take is None or sweep < take) else None,
            sweep_sess=session(T[sweep]) if sweep is not None and (take is None or sweep < take) else None,
            take_h=(take - j) / 4 if take is not None else None, take_sess=session(T[take]) if take is not None else None,
            back=back, after=after, over=over, reach_l1=reach_l1, open=take is None and N - j < MAXAGE,
            _p=p, _j=j, _l1i=e["l1i"], _take=take, _sweep=sweep if sweep is not None and (take is None or sweep < take) else None))
    return out


def fmt(x, f="%.1f"):
    return "-" if x is None else (("yes" if x else "no") if isinstance(x, bool) else f % x)


def summary(ev, label):
    n = len(ev)
    if n == 0:
        return "| %s | 0 |" % label + " - |" * 9
    def pct(c, d):
        return "%d/%d (%.0f%%)" % (c, d, 100 * c / d) if d else "0/0"
    closed = [e for e in ev if not e["open"]]
    tk = [e for e in closed if e["take_h"] is not None]
    t24 = [e for e in closed if e["take_h"] is not None and e["take_h"] <= 24]
    sw = [e for e in closed if e["sweep_h"] is not None]
    sw_tk = [e for e in sw if e["take_h"] is not None]
    bk = [e for e in tk if e["back"]]
    rl = [e for e in tk if e["reach_l1"]]
    oi_up = [e for e in closed if e["oi"] is not None and e["oi"] > 0]
    oi_n = [e for e in closed if e["oi"] is not None]
    us = [e for e in tk if e["take_sess"] == "US"]
    return "| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        label, n, pct(len(t24), len(closed)), pct(len(tk), len(closed)), pct(len(sw), len(closed)), pct(len(sw_tk), len(sw)),
        pct(len(bk), len(tk)), pct(len(rl), len(tk)), pct(len(oi_up), len(oi_n)), pct(len(us), len(tk)))


def main():
    ev = run(1) + run(-1)
    ev.sort(key=lambda e: e["h1_t"])
    print("# Phase 1 output (generated %s, bars to %s UTC)" % (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
                                                             utc(T[-1]).strftime("%Y-%m-%d %H:%M")))
    print("window %s .. %s; top %.0f at %s splits UP / DOWN; OI days missing: %s" % (
        utc(T[i0]).date(), utc(T[-1]).date(), H[top_i], utc(T[top_i]).strftime("%Y-%m-%d %H:%M"), ",".join(OI_MISSING) or "none"))
    print()
    print("| group | held retests | taken <=24h | taken <=72h | L1 swept first | ...then H1 taken | take-out closed back <=1h |"
          " back to L1 <=24h after take-out | OI up L1->retest | take-out in US |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for ph in ("UP", "DOWN"):
        for sd, nm in (("H", "highs"), ("L", "lows")):
            print(summary([e for e in ev if e["phase"] == ph and e["side"] == sd], "%s %s" % (ph, nm)))
    print()
    print("Context splits (highs and lows pooled, mirrored; closed events only). 'taken <=24h' = of held retests;"
          " 'back to L1' = of take-outs. Small n: description, not evidence.")
    print()
    print("| phase | factor | yes: n, taken <=24h, back to L1 | no: n, taken <=24h, back to L1 |")
    print("|---|---|---|---|")
    facts = (("OI up L1->retest", lambda e: None if e["oi"] is None else e["oi"] > 0),
             ("RSI divergence at H1", lambda e: e["div"]),
             ("WaveTrend OB at H1 (wt1 >= 53)", lambda e: None if e["wt"] is None else e["wt"] >= 53),
             ("H1 at a 72h HVN", lambda e: e["hvn"]),
             ("L1 swept before take-out", lambda e: e["sweep_h"] is not None),
             ("retest held in US/LATE", lambda e: e["j_sess"] in ("US", "LATE")))
    for ph in ("UP", "DOWN"):
        closed = [e for e in ev if e["phase"] == ph and not e["open"]]
        for name, f in facts:
            cells = []
            for want in (True, False):
                g = [e for e in closed if f(e) is want]
                tk = [e for e in g if e["take_h"] is not None]
                t24 = sum(1 for e in tk if e["take_h"] <= 24)
                rl = sum(1 for e in tk if e["reach_l1"])
                cells.append("n=%d, %s, %s" % (len(g), "%.0f%%" % (100 * t24 / len(g)) if g else "-",
                                               "%d/%d" % (rl, len(tk))))
            print("| %s | %s | %s | %s |" % (ph, name, cells[0], cells[1]))
    print()
    print("| H1/L1 side | H1 time UTC | phase | level | age h | depth % | OI % L1->j | WT | RSI div | HVN | POC % | retest held (UTC, session) |"
          " L1 swept after h (sess) | taken after h (sess) | overshoot % | back <=1h | 24h after % | back to L1 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for e in ev:
        print("| %s | %s | %s | %.0f | %.1f | %.1f | %s | %s | %s | %s | %s | %s %s | %s | %s | %s | %s | %s | %s |" % (
            e["side"], utc(e["h1_t"]).strftime("%m-%d %H:%M"), e["phase"], e["h1"], e["age_h"], e["depth"], fmt(e["oi"]),
            fmt(e["wt"], "%.0f"), fmt(e["div"]), fmt(e["hvn"]), fmt(e["poc"]), utc(e["j_t"]).strftime("%m-%d %H:%M"), e["j_sess"],
            "-" if e["sweep_h"] is None else "%.1f (%s)" % (e["sweep_h"], e["sweep_sess"]),
            ("open" if e["open"] else "no") if e["take_h"] is None else "%.1f (%s)" % (e["take_h"], e["take_sess"]),
            fmt(e["over"], "%.2f"), fmt(e["back"]), fmt(e["after"], "%+.2f"), fmt(e["reach_l1"])))
    if SIM_JSON:
        card = sim_card(ev, facts)
        with open(SIM_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(card, f, indent=1, ensure_ascii=False)
            f.write("\n")


def pctl(xs, q):
    """Median (q=0.5, middle pair averaged) or lower-rank percentile xs[int((n-1)*q)], as in PHASE1_RECENT.md."""
    xs = sorted(xs)
    if q == .5:
        m = len(xs) // 2
        return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2
    return xs[int((len(xs) - 1) * q)]


def event_svg(e, caption):
    """One event as a 300x160 candle chart in percent from the held level (no prices stored): held level (dashed),
    pull-back extreme L1 (blue), pivot (grey dot), retest held (blue dot), L1 sweep (orange), take-out (cross)."""
    Wd, Ht, top, bot = 300, 160, 6, 22
    a = max(0, e["_p"] - 8)
    stop = (e["_take"] if e["_take"] is not None else e["_j"]) + 96
    b = min(N - 1, stop)
    span = next(s for s in (1, 2, 4, 8, 16, 32) if (b - a + 1) / s <= 64)
    lvl = e["h1"]
    pc = lambda x: (x / lvl - 1) * 100
    cs = []
    for k in range(a, b + 1, span):
        m = range(k, min(b + 1, k + span))
        cs.append((pc(O[k]), pc(max(H[i] for i in m)), pc(min(L[i] for i in m)), pc(C[m[-1]])))
    l1 = pc(e["l1"])
    ys = [x for c in cs for x in c[1:3]] + [0.0, l1]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * .05 or .1
    lo, hi = lo - pad, hi + pad
    y = lambda v: top + (hi - v) / (hi - lo) * (Ht - top - bot)
    cw = Wd / len(cs)
    x = lambda i: ((i - a) / span) * cw + cw / 2
    wick, up, dn = [], [], []
    for n_, (o, h, l_, c) in enumerate(cs):
        xc = n_ * cw + cw / 2
        wick.append("M%.1f %.1fV%.1f" % (xc, y(h), y(l_)))
        t1, b1 = y(max(o, c)), y(min(o, c))
        (up if c >= o else dn).append("M%.1f %.1fh%.1fV%.1fh%.1fZ" % (xc - cw * .35, t1, cw * .7, max(b1, t1 + .6), -cw * .7))
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (Wd, Ht, Wd, Ht),
         '<path d="%s" stroke="#8a8f98" stroke-width="1"/>' % "".join(wick),
         '<path d="%s" fill="#9fb8a6"/><path d="%s" fill="#c4a3a3"/>' % ("".join(up), "".join(dn))]
    for v, col, dash, name in ((0.0, "#6b7280", ' stroke-dasharray="3 3"', "held %s 0%%" % ("high" if e["side"] == "H" else "low")),
                               (l1, "#2563eb", "", "L1 %+.1f%%" % l1)):
        s.append('<path d="M0 %.1fH%d" stroke="%s" stroke-width="1.2"%s/><text x="%d" y="%.1f" text-anchor="end" font-size="9" '
                 'fill="%s">%s</text>' % (y(v), Wd, col, dash, Wd - 2, y(v) - 2, col, name))
    s.append('<circle cx="%.1f" cy="%.1f" r="3" fill="#6b7280"/>' % (x(e["_p"]), y(0.0)))
    s.append('<circle cx="%.1f" cy="%.1f" r="3.2" fill="#2563eb"/>' % (x(e["_j"]), y(pc(C[e["_j"]]))))
    if e["_sweep"] is not None:
        s.append('<path d="M%.1f %.1fl4 7h-8Z" fill="#d97706"/>' % (x(e["_sweep"]), y(l1)))
    if e["_take"] is not None:
        xt, yt = x(e["_take"]), y(0.0)
        s.append('<path d="M%.1f %.1fl6 6m0 -6l-6 6" stroke="#111" stroke-width="1.6"/>' % (xt - 3, yt - 3))
    s.append('<text x="4" y="%d" font-size="10" font-family="sans-serif" fill="#374151">%s</text></svg>' % (Ht - 7, caption))
    return "".join(s)


def _caption(e):
    t = utc(e["h1_t"]).strftime("%Y-%m-%d %H:%M")
    if e["take_h"] is None:
        what = "still open" if e["open"] else "held 72h"
    else:
        what = "taken %.0fh (%s)" % (e["take_h"], e["take_sess"]) + (", 24h %+.1f%%" % e["after"] if e["after"] is not None else "")
    return "%s %s %s: %s" % (t, e["phase"], "high" if e["side"] == "H" else "low", what)


def pick_examples(ev):
    """Labelled events for the charts: the operator's own chart, the typical case of each finding, and the open level."""
    def nearest(g, key, target):
        return min(g, key=lambda e: abs(key(e) - target)) if g else None
    used, out = set(), []

    def add(label, note, e):
        if e is not None and id(e) not in used:
            used.add(id(e)); out.append((label, note, e))
    op = [e for e in ev if e["side"] == "H" and utc(e["h1_t"]).strftime("%m-%d %H:%M") == "10-28 08:30"]
    add("operator's 10-31 chart", "10-28 highs held, taken 10-29, then the drop", op[0] if op else None)
    dn = [e for e in ev if e["phase"] == "DOWN" and e["side"] == "H" and e["take_h"] is not None and e["reach_l1"] and e["after"] is not None]
    add("typical DOWN high", "taken, then back to L1 (60 % of DOWN take-outs)",
        nearest(dn, lambda e: e["after"], pctl([e["after"] for e in dn], .5) if dn else 0))
    upk = [e for e in ev if e["phase"] == "UP" and e["side"] == "H" and e["take_h"] is not None and not e["reach_l1"] and e["after"] is not None]
    add("typical UP high", "taken and kept going (UP: back to L1 only 38 %)",
        nearest(upk, lambda e: e["after"], pctl([e["after"] for e in upk], .5) if upk else 0))
    ch = [e for e in ev if e["side"] == "H" and e["_sweep"] is not None and e["take_h"] is not None]
    add("full chain", "L1 swept first, then the high taken (about 1 in 5)", ch[-1] if ch else None)
    held = [e for e in ev if e["side"] == "H" and e["take_h"] is None and not e["open"]]
    add("high that held", "not taken within 72h", held[-1] if held else None)
    opn = [e for e in ev if e["open"]]
    for e in opn[-2:]:
        add("open now", "level still live at the end of the data", e)
    return out


def sim_card(ev, facts):
    """Simulator result card (sim_desk/DESIGN.md schema): percent and times only, no prices."""
    def grp(ph, sd):
        return [e for e in ev if e["phase"] == ph and e["side"] == sd]
    step_cols = ["group", "held retests", "taken <=24h", "taken <=72h", "L1 swept first", "...then H1 taken",
                 "take-out closed back <=1h", "back to L1 <=24h after take-out", "OI up L1->retest", "take-out in US"]
    step_rows, move_rows = [], []
    for ph in ("UP", "DOWN"):
        for sd, nm in (("H", "highs"), ("L", "lows")):
            g = grp(ph, sd)
            step_rows.append([c.strip() for c in summary(g, "%s %s" % (ph, nm)).strip("|").split("|")])
            aft = [e["after"] for e in g if e["after"] is not None]
            ov = [e["over"] for e in g if e["over"] is not None]
            move_rows.append(["%s %s" % (ph, nm), "%+.2f %%" % pctl(aft, .5) if aft else "-",
                              "%.2f %% / %.2f %%" % (pctl(ov, .5), pctl(ov, .8)) if ov else "-", str(len(aft))])
    ctx_rows = []
    for ph in ("UP", "DOWN"):
        closed = [e for e in ev if e["phase"] == ph and not e["open"]]
        for name, f in facts:
            row = [ph, name]
            for want in (True, False):
                g = [e for e in closed if f(e) is want]
                tk = [e for e in g if e["take_h"] is not None]
                row += [str(len(g)), "%.0f %%" % (100 * sum(1 for e in tk if e["take_h"] <= 24) / len(g)) if g else "-",
                        "%d/%d" % (sum(1 for e in tk if e["reach_l1"]), len(tk))]
            ctx_rows.append(row)
    dnh = grp("DOWN", "H"); uph = grp("UP", "H")

    def rate(g, num, den):
        d = [e for e in g if den(e)]
        return "%.0f %%" % (100 * sum(1 for e in d if num(e)) / len(d)) if d else "-"
    taken = lambda e: e["take_h"] is not None
    items = [{"kind": "event", "label": lab, "note": note, "svg": event_svg(e, _caption(e))} for lab, note, e in pick_examples(ev)]
    end = utc(T[-1]).strftime("%Y-%m-%d %H:%M")
    return {
        "id": "dir-c26_roadmap_2026-11-01", "kind": "backtest",  # named after its catalogue row (build_catalogue step 6) "parity": None,
        "family": "Eagle_Eyes chart ideas (operator, 10-30/31)", "provenance": "run",
        "title": "C26 roadmap Phase 1: held high -> pull-back -> held retest -> L1 sweep -> take-out -> drop, recent UP vs DOWN phase",
        "date": "2026-11-01",
        "what": [
            {"name": "Source", "value_plain": "operator 2026-11-01 roadmap (short the first high, retest fails, longs taken, high taken, "
             "then the fall); card c26-scenario-roadmap-sequence", "label": "SOURCED"},
            {"name": "Held level", "value_plain": "C26: pivot high/low of +-16 15m bars, pull-back >= 0.8 %, retest within 0.4 % that "
             "holds 4 bars, level age <= 72h; lows are the mirror", "label": "OURS"},
            {"name": "Steps measured", "value_plain": "L1 swept before the take-out, take-out within 24h / 72h, closed back within 1h, "
             "back to L1 within 24h, move 24h later, overshoot in the 4h after", "label": "OURS"},
            {"name": "Context", "value_plain": "OI change L1 -> retest (Binance USDT-M), WaveTrend wt1 >= 53 at H1, RSI(14) divergence, "
             "72h volume node at H1, session of the retest (US 13:30-20 UTC)", "label": "OURS"},
            {"name": "Phase split", "value_plain": "UP = 2026-07-01 low to the 2026-09-21 top, DOWN = after it (one top, by eye)", "label": "OURS"},
            {"name": "Trades", "value_plain": "none: descriptive counts, no entry, no fees, no P&L", "label": "OURS"},
        ],
        "how": "phase1_recent.py on Binance spot 15m bars %s .. %s UTC; every held high and low in the window, followed bar by bar "
               "until taken or 72h. Re-run: python phase1_recent.py <repo> <cache> --until %s --sim-json <this file>." % (
                   utc(T[i0]).date(), end, utc(T[-1]).strftime("%Y-%m-%dT%H:%M")),
        "window": "RECENT design window %s .. %s (not DEV; seen, never counts as a test)" % (utc(T[i0]).date(), utc(T[-1]).date()),
        "verdict": {"label": "Design look only: no trade rule tested yet. The phase decides what happens after the take-out", "tone": "warn"},
        "why": [
            "The magnet does not change with the phase: 68-76 % of held levels are taken within 24h in UP and DOWN (4-year C26: 72 %).",
            "After a high is taken, DOWN phase: back to L1 within 24h %s, UP phase %s; median 24h later %s vs %s." % (
                rate(dnh, lambda e: e["reach_l1"], taken), rate(uph, lambda e: e["reach_l1"], taken),
                move_rows[2][1], move_rows[0][1]),
            "The full chain (L1 swept first, then the high taken) is about 1 in 5; once L1 is swept, the high is taken within 24h only about 40 %.",
            "OI rising into the retest is not the fuel: it rose in only 42-49 % of cases, and DOWN retests with OI up were taken less often.",
            "Next: Phase 2 freezes the regime rule and the core / hedge legs; Phase 3 tests them on DEV 2022-04..2024-06 on the desk.",
        ],
        "kpis": [
            {"label": "held levels (events)", "value": str(len(ev))},
            {"label": "DOWN highs taken <=24h", "value": rate(dnh, lambda e: taken(e) and e["take_h"] <= 24, lambda e: not e["open"])},
            {"label": "DOWN highs back to L1 after take-out", "value": rate(dnh, lambda e: e["reach_l1"], taken), "tone": "warn"},
            {"label": "UP highs back to L1 after take-out", "value": rate(uph, lambda e: e["reach_l1"], taken)},
            {"label": "DOWN highs, median 24h after", "value": move_rows[2][1]},
        ],
        "examples": [
            {"kind": "charts", "title": "Events on the chart (percent from the held level)", "items": items,
             "caption": "Grey dot = the high/low, blue dot = retest held, orange = L1 swept, cross = taken; dashed = held level, "
                        "blue line = pull-back extreme L1. Times UTC. No prices are stored."},
            {"kind": "table", "title": "Step odds by phase", "cols": step_cols, "rows": step_rows,
             "caption": "taken = of closed held retests; 'back to L1' and 'closed back' = of take-outs"},
            {"kind": "table", "title": "Move after the take-out", "cols": ["group", "24h after (median)", "overshoot 4h after, median / 80th pct", "n"],
             "rows": move_rows, "caption": "+ = kept going through the level, - = reversed"},
            {"kind": "table", "title": "Context splits (highs and lows pooled, mirrored)",
             "cols": ["phase", "factor", "yes n", "yes taken <=24h", "yes back to L1", "no n", "no taken <=24h", "no back to L1"],
             "rows": ctx_rows, "caption": "small n: a description, not evidence; 12 looks logged in TRIAL_REGISTRY_c26_roadmap.csv"},
        ],
        "source_files": ["MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RECENT.md",
                         "MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_EVENTS.md",
                         "MyTradingSys/research/c26_roadmap_2026-11-01/phase1_recent.py"],
        "commit": "this card",
    }


if __name__ == "__main__":
    main()
