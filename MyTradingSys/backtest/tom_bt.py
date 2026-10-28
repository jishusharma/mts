import sys
sys.dont_write_bytecode = True
"""Tom core outcome backtest library (research, offline, stdlib only).

Pipeline (BACKTEST_PROTOCOL.md): historical snapshots (Java TomSnapshotGen over ArchiveHistoricalSource, built in a
%TEMP% copy) -> snapshot_to_row (verdict.py, fail-closed proof direction) -> signals (episode / rule A) ->
sim_limit_trade on the 1m archive -> stats (bootstrap CI, Wilson CI).

Conventions (all frozen in bt_runs/<run>/FROZEN.md before a run):
- Signal at snapshot close t (asOf). Entry = limit at the candidate zone price E (the price SetupCandidatesBuilder's
  gross_rr is computed from), stop/target = rank-1 candidate math.stop / math.target.
- The order lives 8 bars of the zone timeframe (zone tf = SetupCandidatesBuilder.getSwingTF), then is cancelled
  (unfilled). It is also cancelled if price reaches the target before touching E ("ran").
- Fill bar: fills at E; only the stop is evaluated inside the fill bar (conservative: stop assumed after fill).
- After the fill bar: stop / target on each 1m bar; both in one bar -> stop first (conservative) unless
  stop_first=False (reported as the resolution risk). Gap through the stop -> filled at the bar open (worse).
  Timeout = 8 zone-tf bars after the fill, exit at the close of the last 1m bar (taker).
- Fees (fraction of price per side): entry/target maker, stop/timeout taker. Default Deribit BTC-PERPETUAL as in
  sim.py: maker 0, taker 0.0005. Stress: 0.0005 on every fill; extra slippage on stop/timeout fills.
- Funding is NOT modelled (holding periods <= 8 zone bars = at most 8h); stated in the report.
"""
import csv
import math
import os
import random
from array import array
from pathlib import Path

ZONE_TF_MIN = {"1h": 60, "15m": 15, "5m": 5}
STEP_S = 900  # snapshot cadence (TomSnapshotGen stepMin=15)


def zone_tf(zone_type):
    """Mirror of SetupCandidatesBuilder.getSwingTF (source of truth: that Java method)."""
    z = zone_type or ""
    if z.startswith("weekly_"):
        return "1h"
    if z.startswith(("daily_", "pf_", "4h_", "prior_day_")):
        return "15m"
    if z.startswith("vwap") or z == "fvg" or z.startswith("5m_swing_"):
        return "5m"
    if z.startswith("15m_swing_"):
        return "15m"
    if z.startswith("1h_swing_"):
        return "1h"
    return "15m"


# ---------------------------------------------------------------- data
class Bars1m:
    """Contiguous 1m bars in primitive arrays. idx(ts_ms) is O(1) because continuity is checked at load."""

    def __init__(self, t0, o, h, l, c, v, tbv, real=None):
        self.t0, self.o, self.h, self.l, self.c, self.v, self.tbv = t0, o, h, l, c, v, tbv
        self.n = len(o)
        # real[i] == 1 where bar i came from the file, 0 where the loader filled a closed minute (fill_gaps only).
        # None = a contiguous feed (BTC): every bar is real.
        self.real = real

    def idx(self, ts_ms):
        return (ts_ms - self.t0) // 60000


def load_bars_1m(klines_dir, fill_gaps=None):
    """Loads every *.csv under klines_dir (Binance 1m klines, header optional), dedupes, requires zero gaps.

    fill_gaps (market with closing hours, DAX): closed minutes become flat bars at the last close with volume 0 so the
    simulator can index by minute; Bars1m.real marks the bars that came from the file. Default None = env
    TOM_MARKET_CLOSES == "1", else False: the BTC path is unchanged and still raises on any gap."""
    if fill_gaps is None:
        fill_gaps = os.environ.get("TOM_MARKET_CLOSES") == "1"
    rows = {}
    for f in sorted(Path(klines_dir).glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0].isdigit():
                    continue
                t = int(r[0])
                if t not in rows:
                    rows[t] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9]))
    ts = sorted(rows)
    if not ts:
        raise ValueError("no klines in %s" % klines_dir)
    if not fill_gaps:
        for a, b in zip(ts, ts[1:]):
            if b - a != 60000:
                raise ValueError("1m gap between %d and %d" % (a, b))
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    real = bytearray() if fill_gaps else None
    prev = None
    for t in ts:
        r = rows[t]
        if fill_gaps:
            if prev is not None:
                for _ in range((t - prev) // 60000 - 1):  # closed minutes: flat at the last close, no volume
                    lc = c[-1]
                    o.append(lc); h.append(lc); l.append(lc); c.append(lc); v.append(0.0); tbv.append(0.0)
                    real.append(0)
            real.append(1)
        o.append(r[0]); h.append(r[1]); l.append(r[2]); c.append(r[3]); v.append(r[4]); tbv.append(r[5])
        prev = t
    return Bars1m(ts[0], o, h, l, c, v, tbv, real)


def resample_dicts(b, tf_min):
    """Aligned (UTC epoch) closed bars as dicts {t,o,h,l,c,v,tbv} for the Fabio detectors."""
    pm = tf_min * 60000
    first = -(-b.t0 // pm) * pm
    j0 = (first - b.t0) // 60000
    out = []
    while j0 + tf_min <= b.n:
        j1 = j0 + tf_min
        out.append({"t": b.t0 + j0 * 60000, "o": b.o[j0], "h": max(b.h[j0:j1]), "l": min(b.l[j0:j1]),
                    "c": b.c[j1 - 1], "v": sum(b.v[j0:j1]), "tbv": sum(b.tbv[j0:j1])})
        j0 = j1
    return out


# ---------------------------------------------------------------- snapshot -> row
def snapshot_to_row(s, parse_ts, compute_verdict, proof_dir_of):
    """One compact row per snapshot. proof direction (expensive) only when it can change the verdict."""
    v = compute_verdict(s, "aligned")
    pd = "aligned"
    if v["verdict"] in ("WATCH", "SETUP_FORMING"):
        pd = proof_dir_of(s, fail_closed=True)
        v = compute_verdict(s, pd)
    top = v.get("top") or {}
    m = top.get("math") or {}
    z = top.get("zone") or {}
    return dict(t=parse_ts(s.get("timestamp_utc", "")), price=float(s["current_price"]), verdict=v["verdict"],
                proof=v.get("proof"), pd=pd, setup=top.get("setup_type"), dir=v.get("direction"),
                zone=z.get("name"), ztype=z.get("type"), zprice=z.get("price"), stop=m.get("stop"),
                target=m.get("target"), gross_rr=m.get("gross_rr"), net_rr=m.get("net_rr"), tier=m.get("tier"))


# ---------------------------------------------------------------- signals
def _key(r):
    return (r["setup"], r["dir"], r["zone"], r["zprice"])


VARIANTS = {
    "A": lambda r: r["verdict"] == "SETUP_FORMING",
    "episode": lambda r: r["verdict"] == "SETUP_FORMING",
    "watch_episode": lambda r: r["verdict"] in ("WATCH", "SETUP_FORMING"),
    "p4_episode": lambda r: r["verdict"] in ("WATCH", "SETUP_FORMING") and (r.get("proof") or 0) >= 4,
}


def signals(rows, variant):
    """variant 'A': every SETUP_FORMING row (one-at-a-time filtering happens in run_variant, as sim.py rule A);
    'episode': first row of each SETUP_FORMING episode (same setup/dir/zone, consecutive rows);
    'watch_episode': same for WATCH or SETUP_FORMING; 'p4_episode': WATCH/SETUP_FORMING with proof >= 4.
    Historical snapshots lack book-imbalance / funding / OI (no raw source), so max proof is 6 and
    SETUP_FORMING (proof >= 5) is rare: the WATCH-based variants are sensitivity, not the live rule."""
    pred = VARIANTS[variant]
    out, prev = [], None
    for r in rows:
        is_sig = pred(r) and r.get("stop") and r.get("target") and r.get("zprice")
        if is_sig:
            if variant == "A":
                out.append(r)
            else:
                cont = (prev is not None and pred(prev) and _key(prev) == _key(r)
                        and r["t"] - prev["t"] <= 1.5 * STEP_S)
                if not cont:
                    out.append(r)
        prev = r
    return out


# ---------------------------------------------------------------- simulation
from MyTradingSys.backtest.fees import FEES_DERIBIT, FEES_ALL_TAKER, FEES_FDAX  # noqa: E402  (single source of truth, B081)

_DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "dev"))
if _DEV_DIR not in sys.path:
    sys.path.insert(0, _DEV_DIR)
from tom_noise_units import min_stop_width


def sim_limit_trade(b, i0, side, entry, stop, target, fill_window, hold_bars, fees=FEES_DERIBIT,
                    stop_first=True, slip=0.0, slip_pts=0.0, through_ticks=0.0):
    """Limit entry at `entry`, first eligible 1m bar index i0 (the bar opening at the signal time).

    through_ticks is a price offset applied to entry and target triggers; zero preserves touch fills.
    """
    sgn = 1.0 if side == "long" else -1.0
    if not (sgn * (stop - entry) < 0 and sgn * (target - entry) > 0):
        return dict(filled=False, reason="bad_geometry")
    risk = abs(entry - stop)
    n = b.n
    fill_i = None
    for i in range(i0, min(i0 + fill_window, n)):
        lo, hi = b.l[i], b.h[i]
        if (lo <= entry - through_ticks) if sgn > 0 else (hi >= entry + through_ticks):
            fill_i = i
            break
        if (hi >= target + through_ticks) if sgn > 0 else (lo <= target - through_ticks):
            return dict(filled=False, reason="ran")
    if fill_i is None:
        return dict(filled=False, reason="no_fill" if i0 + fill_window <= n else "open_at_end")

    def done(kind, px, j, amb):
        if kind in ("stop", "timeout"):
            px = px - sgn * slip * px - sgn * slip_pts  # worse fill (slip: fraction of price; slip_pts: index points)
        gross = sgn * (px - entry) / risk
        fee_r = (fees["entry"] * entry + fees[kind] * px) / risk
        return dict(filled=True, reason=kind, gross_r=gross, net_r=gross - fee_r, fee_r=fee_r, fill_i=fill_i,
                    exit_i=j, bars_held=j - fill_i, ambiguous=amb)

    # fill bar: stop only (conservative)
    if (b.l[fill_i] <= stop) if sgn > 0 else (b.h[fill_i] >= stop):
        px = min(b.o[fill_i], stop) if sgn > 0 else max(b.o[fill_i], stop)
        return done("stop", px, fill_i, 0)
    amb = 0
    last = fill_i + hold_bars
    for j in range(fill_i + 1, last + 1):
        if j >= n:
            return dict(filled=True, reason="open_at_end", fill_i=fill_i)
        s_hit = (b.l[j] <= stop) if sgn > 0 else (b.h[j] >= stop)
        t_hit = (b.h[j] >= target + through_ticks) if sgn > 0 else (b.l[j] <= target - through_ticks)
        if s_hit and t_hit:
            amb += 1
        if s_hit and (stop_first or not t_hit):
            px = min(b.o[j], stop) if sgn > 0 else max(b.o[j], stop)
            return done("stop", px, j, amb)
        if t_hit:
            return done("target", target, j, amb)
        if j == last:
            return done("timeout", b.c[j], j, amb)
    return dict(filled=True, reason="open_at_end", fill_i=fill_i)


def run_variant(sigs, b, fees=FEES_DERIBIT, stop_first=True, slip=0.0, one_at_a_time=True, slip_pts=0.0,
                min_width=None):
    """One position/pending order at a time. Returns a list of trade dicts (unfilled orders included).

    min_width: None keeps every existing output identical; else a callable asof_ms -> n5 (TOM_LAYER_V2_SPEC.md 11.4).
    A signal with a stop narrower than min_stop_width is dropped with reason stop_below_min_width, never widened.
    """
    out = []
    busy_until_i = -1
    for r in sigs:
        tf = zone_tf(r["ztype"])
        tfm = ZONE_TF_MIN[tf]
        i0 = b.idx(int(round(r["t"] * 1000)))
        if i0 < 0 or i0 >= b.n:
            continue
        if one_at_a_time and i0 <= busy_until_i:
            continue
        if min_width is not None:
            asof_ms = int(round(r["t"] * 1000))
            n5_val = min_width(asof_ms) if callable(min_width) else float(min_width)
            w_min = min_stop_width(float(r["zprice"]), n5_val, fees)
            if abs(float(r["zprice"]) - float(r["stop"])) < w_min:
                t = dict(r)
                t.update(filled=False, reason="stop_below_min_width")
                t["zone_tf"] = tf
                out.append(t)
                continue
        res = sim_limit_trade(b, i0, r["dir"], float(r["zprice"]), float(r["stop"]), float(r["target"]),
                              8 * tfm, 8 * tfm, fees, stop_first, slip, slip_pts)
        if res["reason"] == "open_at_end":
            continue
        if res["filled"]:
            busy_until_i = res["exit_i"]
        else:
            busy_until_i = i0 + 8 * tfm - 1 if res["reason"] == "no_fill" else i0
        t = dict(r)
        t.update(res)
        t["zone_tf"] = tf
        out.append(t)
    return out


# ---------------------------------------------------------------- regime tags (no look-ahead: data <= t)
def regime_features(b, t_s):
    """ret30 = close now / close 30d ago - 1; vol30 = stdev of hourly log returns over the prior 30 days."""
    i = b.idx(int(round(t_s * 1000))) - 1  # last closed bar
    if i < 30 * 1440:
        return None
    ret30 = b.c[i] / b.c[i - 30 * 1440] - 1.0
    rs = []
    for k in range(i - 30 * 1440 + 60, i + 1, 60):
        rs.append(math.log(b.c[k] / b.c[k - 60]))
    m = sum(rs) / len(rs)
    vol = math.sqrt(sum((x - m) ** 2 for x in rs) / (len(rs) - 1))
    return ret30, vol


def trend_tag(ret30, thr=0.075):
    return "trend_up" if ret30 >= thr else "trend_down" if ret30 <= -thr else "range"


def tercile_cuts(values):
    s = sorted(values)
    return s[len(s) // 3], s[2 * len(s) // 3]


def vol_tag(vol, cuts):
    return "vol_low" if vol <= cuts[0] else "vol_mid" if vol <= cuts[1] else "vol_high"


# ---------------------------------------------------------------- fabio tag (DESCRIPTIVE ONLY)
def fabio_tag(events, t_s, side, n_bars):
    """events: sorted list of (avail_ms, side, tf_ms). True if an event of the same side became available
    (its bar closed) at or before the signal time and within n_bars of its own timeframe. Never a filter."""
    t_ms = t_s * 1000.0
    for avail, sd, tfm in events:
        if avail > t_ms:
            break
        if sd == side and t_ms - avail <= n_bars * tfm:
            return True
    return False


# ---------------------------------------------------------------- stats
def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def boot_ci(x, n_boot=2000, seed=12345, alpha=0.05):
    if not x:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(x)
    means = sorted(sum(rng.choices(x, k=n)) / n for _ in range(n_boot))
    return means[int(alpha / 2 * n_boot)], means[int((1 - alpha / 2) * n_boot) - 1]


def diff_ci(a, b, alpha=0.05, n_boot=2000, seed=99):
    """Bootstrap CI of mean(a) - mean(b), independent resampling. Returns (diff, lo, hi)."""
    rng = random.Random(seed)
    na, nb = len(a), len(b)
    d = sorted(sum(rng.choices(a, k=na)) / na - sum(rng.choices(b, k=nb)) / nb for _ in range(n_boot))
    return (sum(a) / na - sum(b) / nb, d[int(alpha / 2 * n_boot)], d[int((1 - alpha / 2) * n_boot) - 1])


def summarize(trades, key="net_r"):
    """Stats over FILLED trades that resolved (target/stop/timeout)."""
    filled = [t for t in trades if t.get("filled") and t["reason"] in ("target", "stop", "timeout")]
    n_sig = len(trades)
    if not filled:
        return dict(n_signals=n_sig, n_filled=0)
    g = [t["gross_r"] for t in filled]
    nt = [t[key] for t in filled]
    wins = sum(1 for t in filled if t["reason"] == "target")
    lo, hi = wilson(wins, len(filled))
    gl, gh = boot_ci(g)
    nl, nh = boot_ci(nt)
    return dict(n_signals=n_sig, n_filled=len(filled), fill_rate=len(filled) / n_sig,
                win=wins / len(filled), win_ci=(lo, hi),
                mean_gross=sum(g) / len(g), gross_ci=(gl, gh), mean_net=sum(nt) / len(nt), net_ci=(nl, nh),
                exits={k: sum(1 for t in filled if t["reason"] == k) for k in ("target", "stop", "timeout")},
                ambiguous=sum(t.get("ambiguous", 0) for t in filled))
