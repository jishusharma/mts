"""NKN-03: NK full intraday sequence (video 3KnEiKNh1pc) as ONE pre-registered, context-conditioned study. Design: PRE_REG.md (frozen before any run).

    python study.py run        # DEV + VALIDATION in one run, writes results.json (refuses to run on uncommitted code)

Session row (NY: open 13:30 UTC, exit 20:00 UTC; UTC control: open 00:00, exit 08:00). All bar arithmetic is on a dense bar grid (NaN = missing bar),
so every window is a fixed slice. Everything read at the decision time uses bars closed before it. Causal by construction, tested in test_study.py."""
import os
import sys
import json
import hashlib
import subprocess
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LAYERS = HERE.parents[1] / "backtest" / "layers"
DAY = 86400000
SPLIT_MS = 1704067200000  # 2024-01-01 00:00 UTC; DEV < SPLIT <= VAL, by SIGNAL time (open + 60 min), never by entry or exit
CACHE = Path(r"F:\MTS\data_cache")
FETCHED = CACHE / "nkn_1114" / "nkn03-intraday-sequence"
SPOT15 = CACHE / "binance_spot"
FUND = CACHE / "binance_futures" / "nkp1"
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"
COINS_1M = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM".split()
COINS_15M = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()

# ---- parameters (labels in PRE_REG.md) ----
SCAN_HI, SCAN_LO = 0.02, 0.01      # SOURCED 3KnEiKNh1pc 00:09:15 (2%, alternate 1%)
TRAP_MIN = 10                      # SOURCED 00:07:24 (first 5-10 minutes); 1m bars OURS
SKIP_RANGE = 0.04                  # OURS cap on the first 1h range (NK said only "big", 00:12:01)
FLOOR_PCT, FLOOR_ATR = 0.005, 0.6  # OURS R floor: max(structural, 0.5%, 0.6 x ATR14 daily through d-1)
AT_BAND = 0.25                     # OURS: at-level band in daily ATR14
ENTRY_AFTER_MIN = 60               # SOURCED patience (00:15:10): no entry before open + 60 min
V1_RSI, V2_ADX = 50.0, 20.0        # 50 OURS; ADX 20 SOURCED (NK55 common block)
MIN_N, NB_BOOT = 100, 5000
BIG = 10 ** 9
ROWS = {  # name -> (open minute of UTC day, session length in minutes)
    "NY": (13 * 60 + 30, 390),
    "UTC": (0, 480),
}


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rsi_core = _load(LAYERS / "rsi" / "rsi_core.py", "nkn_rsi_core").rsi_core
adx_di = _load(LAYERS / "adx" / "adx.py", "nkn_adx").adx_di


# ------------------------------------------------------------------ data
def check_time(t, step):
    """strictly increasing and a constant bar step (every gap is a whole multiple of the step; the smallest equals it)."""
    t = np.asarray(t)
    assert len(t) > 1, "empty series"
    d = np.diff(t)
    assert (d > 0).all(), "timestamps not strictly increasing"
    assert (d % step == 0).all() and int(d.min()) == step, "bar step not constant"


def load_npz(path, step):
    z = np.load(path)
    keys = [k for k in ("t_ms", "ts", "t") if k in z.files]
    assert len(keys) >= 1, f"no time key in {path}: {z.files}"
    t = z[keys[0]].astype(np.int64)
    check_time(t, step)
    assert "v" in z.files, "volume column needed for VWAP"
    return dict(t=t, o=z["o"].astype(float), h=z["h"].astype(float), l=z["l"].astype(float), c=z["c"].astype(float), v=z["v"].astype(float), key=keys[0])


def dense(b, step):
    """place bars on a grid that starts at a UTC midnight and ends at a UTC midnight; missing bars are NaN. cf = forward-filled close (closes only)."""
    bpd = DAY // step
    T0 = (int(b["t"][0]) // DAY) * DAY
    nd = (int(b["t"][-1]) - T0) // DAY + 1
    n = nd * bpd
    ix = (b["t"] - T0) // step
    D = dict(T0=T0, step=step, bpd=bpd, nd=nd, day0=T0 // DAY)
    for k in "ohlcv":
        a = np.full(n, np.nan)
        a[ix] = b[k]
        D[k] = a
    D["cf"] = pd.Series(D["c"]).ffill().to_numpy()
    return D


def daily(D):
    nd, bpd = D["nd"], D["bpd"]
    h = np.fmax.reduce(D["h"].reshape(nd, bpd), axis=1)
    l = np.fmin.reduce(D["l"].reshape(nd, bpd), axis=1)
    c = D["cf"].reshape(nd, bpd)[:, -1]
    return h, l, c


def wilder_atr(h, l, c, n=14):
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + (tr[i] if np.isfinite(tr[i]) else out[i - 1])) / n
    return out


def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.r_[0.0, x])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def nanify(lst):
    return np.array([np.nan if v is None else v for v in lst], dtype=float)


def daily_feats(D):
    """features at index j use data through the CLOSE of UTC day j. Session day d reads index d-1."""
    h, l, c = daily(D)
    dip, dim, adx = adx_di(h.tolist(), l.tolist(), c.tolist(), 14)
    F = dict(day0=D["day0"], c=c, atr=wilder_atr(h, l, c), sma20=sma(c, 20), sma50=sma(c, 50), adx=nanify(adx), dip=nanify(dip), dim=nanify(dim))
    s20 = F["sma20"]
    slope = np.full(len(c), np.nan)
    slope[5:] = s20[5:] / s20[:-5] - 1
    F["slope5"] = slope
    return F


def hm_pack(D):
    """HM(9,3,21) on epoch-aligned 1h closes: g = EMA3(RSI9), red = WMA21(RSI9) (formula OURS, class video Qdug_K_TNHg), plus RSI9."""
    bph = 3600000 // D["step"]
    c1 = D["cf"].reshape(-1, bph)[:, -1]
    r = np.full(len(c1), np.nan)
    ok = np.flatnonzero(np.isfinite(c1))
    if len(ok) > 40:
        r9 = nanify(rsi_core(c1[ok[0]:].tolist(), 9))
        r[ok[0]:] = r9
    g = pd.Series(r).ewm(span=3, adjust=False).mean().to_numpy()
    w = np.arange(21, 0, -1, dtype=float)
    red = np.full(len(r), np.nan)
    if len(r) >= 21:
        sw = np.lib.stride_tricks.sliding_window_view(r, 21)  # window oldest..newest
        red[20:] = (sw * w[::-1]).sum(axis=1) / w.sum()
    return dict(r9=r, g=g, red=red)


def rsi4h(D):
    b4 = 4 * 3600000 // D["step"]
    c4 = D["cf"].reshape(-1, b4)[:, -1]
    out = np.full(len(c4), np.nan)
    ok = np.flatnonzero(np.isfinite(c4))
    if len(ok) > 20:
        out[ok[0]:] = nanify(rsi_core(c4[ok[0]:].tolist(), 14))
    return out


def load_labels():
    d = pd.read_csv(PHASE_CSV)
    d = d[~d["provisional"].astype(str).str.lower().eq("true")]
    d = d[d["label"].notna() & d["label"].astype(str).str.len().gt(0)]
    day = (pd.to_datetime(d["date"]).astype("datetime64[ms]").astype(np.int64)) // DAY
    return dict(zip(day.tolist(), d["label"].astype(str).tolist()))


def load_funding(coin):
    p = FUND / f"{coin}USDT_funding.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    ts = d["ts"].to_numpy(np.int64)
    assert (np.diff(ts) > 0).all(), "funding timestamps not increasing"
    return dict(ts=ts, rate=d["rate"].to_numpy(float))


def rate_at(F, stamp_ms):
    if F is None:
        return np.nan
    i = int(np.searchsorted(F["ts"], stamp_ms - 60000))
    if i < len(F["ts"]) and abs(int(F["ts"][i]) - int(stamp_ms)) <= 60000:
        return float(F["rate"][i])
    return np.nan


# ------------------------------------------------------------------ pure rule pieces
def fee_r(e, x, dist, bp):
    """round-trip fee in R. bp = round-trip bp: bp/2 charged on entry notional (e) and bp/2 on exit notional (x). R = dist (price units)."""
    return (bp / 2e4) * (e + x) / dist


def split_label(signal_ms):
    return "DEV" if signal_ms < SPLIT_MS else "VAL"


def pivots(h, l, c):
    p = (h + l + c) / 3.0
    return p, 2 * p - h, 2 * p - l  # P, S1, R1


def vwap_cum(H, L, C, V):
    """session VWAP through bar j inclusive, typical price x volume; NaN while cumulative volume is 0. Arrays (nd, nb)."""
    tp = (H + L + C) / 3.0
    pv = np.cumsum(np.where(np.isfinite(tp) & np.isfinite(V), tp * V, 0.0), axis=1)
    vv = np.cumsum(np.where(np.isfinite(V), V, 0.0), axis=1)
    with np.errstate(all="ignore"):
        return np.where(vv > 0, pv / vv, np.nan)


def simulate(side, O, H, L, C, CF, VW, k, e, atr, bm, open_min):
    """one trade on ONE day's session arrays. entry bar k, fill price e (VWAP limit or open). Stop = session low (high for shorts) through bar k-1,
    widened to R = max(structural, 0.5% e, 0.6 ATR); the stop is checked from the entry bar on (stop first, gap through the stop fills at the bar open).
    VWAP stop: close of an epoch-aligned 1h bar beyond the session VWAP exits at that close. Exit otherwise at the session-end close.
    returns (x, xm, dist, stop)."""
    nb = len(O)
    if side > 0:
        struct = e - np.fmin.reduce(L[:k])
    else:
        struct = np.fmax.reduce(H[:k]) - e
    struct = struct if np.isfinite(struct) else 0.0
    dist = max(struct, FLOOR_PCT * e, FLOOR_ATR * atr)
    stop = e - side * dist
    hit = (L[k:] <= stop) if side > 0 else (H[k:] >= stop)
    fs = int(np.argmax(hit)) if hit.any() else BIG
    m = np.arange(k, nb)
    endbar = ((open_min + (m + 1) * bm) % 60) == 0
    cond = (C[k:] < VW[k:]) if side > 0 else (C[k:] > VW[k:])
    cond = cond & endbar
    fv = int(np.argmax(cond)) if cond.any() else BIG
    if fs == BIG and fv == BIG:
        return float(CF[nb - 1]), nb - 1, dist, stop
    if fs <= fv:
        if fs == 0:
            return float(stop), k, dist, stop
        px = min(stop, O[k:][fs]) if side > 0 else max(stop, O[k:][fs])
        return float(px), k + fs, dist, stop
    return float(C[k:][fv]), k + fv, dist, stop


def funding_r(side, e, dist, entry_abs_min, exit_end_abs_min, rate):
    """funding paid at an 8h stamp strictly after the entry bar start and at/before the exit bar end. Long pays positive rate. 0 if no stamp or no rate."""
    n = int(exit_end_abs_min // 480 - entry_abs_min // 480)
    if n <= 0 or not np.isfinite(rate):
        return 0.0
    return side * rate * n * e / dist


# ------------------------------------------------------------------ per coin / row session build
class Sess:
    pass


def gather(D, row, bm_override=None):
    """dense arrays -> per-day session slices (nd, nb) and the prior window H/L/close. Day index i is absolute day D['day0'] + i."""
    open_min, sess_min = ROWS[row]
    bm = D["step"] // 60000
    nb, nbp, ob, bpd = sess_min // bm, 1440 // bm, open_min // bm, D["bpd"]
    days = np.arange(1, D["nd"])
    Sx = days * bpd + ob
    ix = Sx[:, None] + np.arange(nb)
    px = Sx[:, None] - nbp + np.arange(nbp)
    S = Sess()
    S.days, S.bm, S.nb, S.open_min, S.row = days, bm, nb, open_min, row
    for k in "ohlcv":
        setattr(S, k.upper(), D[k][ix])
    S.CF = D["cf"][ix]
    S.PH = np.fmax.reduce(D["h"][px], axis=1)
    S.PL = np.fmin.reduce(D["l"][px], axis=1)
    S.PC = D["c"][Sx - 1]
    S.abs_day = D["day0"] + days
    return S


def conditions(S, side):
    """arming conditions for one side from bars up to open + 60 min only. returns dict of bool arrays (nd,) plus the first-hour return."""
    bm = S.bm
    nb1 = 60 // bm
    ntrap = -(-TRAP_MIN // bm)
    O, H, L, C = S.O, S.H, S.L, S.C
    out = {}
    with np.errstate(all="ignore"):
        ret = C[:, nb1 - 1] / O[:, 0] - 1
        out["ret"] = ret
        out["scan_hi"] = side * ret >= SCAN_HI
        out["scan_lo"] = side * ret >= SCAN_LO
        pc = S.PC[:, None]
        dip = (L[:, :ntrap] < pc) if side > 0 else (H[:, :ntrap] > pc)
        has = dip.any(axis=1)
        di = np.argmax(dip, axis=1)
        rec = (C[:, :nb1] > pc) if side > 0 else (C[:, :nb1] < pc)
        rec = rec & (np.arange(nb1)[None, :] >= di[:, None])
        out["trap"] = has & rec.any(axis=1)
        out["conf"] = (C[:, nb1 - 1] > S.PH) if side > 0 else (C[:, nb1 - 1] < S.PL)
        rng = (np.fmax.reduce(H[:, :nb1], axis=1) - np.fmin.reduce(L[:, :nb1], axis=1)) / O[:, 0]
        out["skip"] = rng > SKIP_RANGE
        okcov = np.isfinite(O[:, :nb1]).mean(axis=1) >= 0.9
        out["valid"] = okcov & np.isfinite(S.PC) & np.isfinite(S.PH) & np.isfinite(S.PL) & np.isfinite(ret)
    return out


def day_reads(S, D, F, HM, R4, side):
    """read-time conditions (HM on last closed 1h, V1 4h RSI, V2 daily ADX/DI) and daily context for each session day. Read time = open + 60 min."""
    bm = S.bm
    read_ms = (S.abs_day * DAY + (S.open_min + 60) * 60000)
    hi = (read_ms - D["T0"]) // 3600000 - 1
    h4 = (read_ms - D["T0"]) // (4 * 3600000) - 1
    j = S.days - (0 if os.environ.get("NKN_BUG") == "1" else 1)  # last closed UTC day (NKN_BUG=1: the same day = look-ahead, used by the negative-control test run)
    out = {}
    with np.errstate(all="ignore"):
        g, red, r9 = HM["g"][hi], HM["red"][hi], HM["r9"][hi]
        out["hm"] = ((g > red) & (r9 > 50)) if side > 0 else ((g < red) & (r9 < 50))
        r4 = R4[h4]
        out["v1"] = (r4 >= V1_RSI) if side > 0 else (r4 <= V1_RSI)
        adx, dip, dim = F["adx"][j], F["dip"][j], F["dim"][j]
        out["v2"] = (adx >= V2_ADX) & ((dip > dim) if side > 0 else (dim > dip))
        out["atr"] = F["atr"][j]
        s5, adx_ = F["slope5"][j], adx
        out["tag"] = np.where((s5 > 0) & (adx_ >= 20) & (dip > dim), 1, np.where((s5 < 0) & (adx_ >= 20) & (dim > dip), -1, 0))
    return out


def btc_index_ok(BTC, abs_day):
    """index filter tag: BTC daily close d-1 above SMA20 and SMA50 (SOURCED 00:15:29; BTC as the Nifty proxy OURS)."""
    j = abs_day - 1 - BTC["day0"]
    ok = (j >= 0) & (j < len(BTC["c"]))
    jj = np.clip(j, 0, len(BTC["c"]) - 1)
    with np.errstate(all="ignore"):
        return ok & (BTC["c"][jj] > BTC["sma20"][jj]) & (BTC["c"][jj] > BTC["sma50"][jj])


def find_entry(S, VW, side, cand):
    """first bar from open+60 min with low <= VWAP through the PREVIOUS bar (long) / high >= it (short); fill at that VWAP, or at the open if it opens beyond it.
    Touch must come before the last bar of the session. returns (k, e) arrays, k = -1 for no touch."""
    nb1 = 60 // S.bm
    nb = S.nb
    # VW[:, k-1] is VWAP through bar k-1; bars k = nb1 .. nb-2
    Vprev = VW[:, nb1 - 1:nb - 2]
    with np.errstate(all="ignore"):
        touch = (S.L[:, nb1:nb - 1] <= Vprev) if side > 0 else (S.H[:, nb1:nb - 1] >= Vprev)
    touch &= np.isfinite(Vprev) & np.isfinite(S.O[:, nb1:nb - 1])
    touch &= cand[:, None]
    any_ = touch.any(axis=1)
    kk = np.where(any_, nb1 + np.argmax(touch, axis=1), -1)
    e = np.full(len(kk), np.nan)
    ii = np.flatnonzero(any_)
    vp = Vprev[ii, kk[ii] - nb1]
    op = S.O[ii, kk[ii]]
    e[ii] = np.where(op < vp, op, vp) if side > 0 else np.where(op > vp, op, vp)
    return kk, e


def at_level(side, e, P, S1, R1, atr):
    lv2 = S1 if side > 0 else R1
    with np.errstate(all="ignore"):
        return np.minimum(abs(e - P), abs(e - lv2)) <= AT_BAND * atr


def sim_row(D, F, HM, R4, row, side, phases, labels, BTC, fund, coin, src):
    """all trades of one coin / row / side, plus the funnel and the day table. phases = labels traded."""
    S = gather(D, row)
    C0 = conditions(S, side)
    R = day_reads(S, D, F, HM, R4, side)
    lab = np.array([labels.get(int(d), "") for d in S.abs_day])
    inph = np.isin(lab, list(phases))
    VW = vwap_cum(S.H, S.L, S.C, S.V)
    valid = C0["valid"] & np.isfinite(R["atr"])
    base = valid & C0["trap"] & C0["conf"] & ~C0["skip"] & R["hm"] & C0["scan_lo"] & inph
    kk, e = find_entry(S, VW, side, base)
    P, S1, R1 = pivots(S.PH, S.PL, S.PC)
    atl = at_level(side, e, P, S1, R1, R["atr"])
    idxok = btc_index_ok(BTC, S.abs_day)
    fun = dict(days=int(inph.sum()), valid=int((inph & valid).sum()), scan_lo=int((inph & valid & C0["scan_lo"]).sum()), scan_hi=int((inph & valid & C0["scan_hi"]).sum()))
    a = inph & valid & C0["scan_hi"]
    fun["trap"] = int((a & C0["trap"]).sum())
    a &= C0["trap"]
    fun["conf"] = int((a & C0["conf"]).sum())
    a &= C0["conf"]
    fun["noskip"] = int((a & ~C0["skip"]).sum())
    a &= ~C0["skip"]
    fun["hm"] = int((a & R["hm"]).sum())
    a &= R["hm"]
    fun["touch"] = int((a & (kk >= 0)).sum())
    recs = []
    bm, open_min = S.bm, S.open_min
    for i in np.flatnonzero(kk >= 0):
        k = int(kk[i])
        x, xm, dist, stop = simulate(side, S.O[i], S.H[i], S.L[i], S.C[i], S.CF[i], VW[i], k, float(e[i]), float(R["atr"][i]), bm, open_min)
        day_ms = int(S.abs_day[i]) * DAY
        e_abs = day_ms // 60000 + open_min + k * bm
        x_abs = day_ms // 60000 + open_min + (xm + 1) * bm
        stamp = (x_abs // 480) * 480 * 60000
        rate = rate_at(fund, stamp) if x_abs // 480 > e_abs // 480 else 0.0
        fr = funding_r(side, float(e[i]), dist, e_abs, x_abs, rate)
        recs.append(dict(coin=coin, src=src, side=side, abs_day=int(S.abs_day[i]), sig_ms=day_ms + (open_min + 60) * 60000, ph=lab[i], scan2=bool(C0["scan_hi"][i]),
                         v1=bool(R["v1"][i]), v2=bool(R["v2"][i]), atl=bool(atl[i]), idx=bool(idxok[i]), tag=int(R["tag"][i]), k=k, e=float(e[i]), x=x, dist=dist,
                         g=side * (x - float(e[i])) / dist, f12=fee_r(float(e[i]), x, dist, 12.0), f6=fee_r(float(e[i]), x, dist, 6.0), fund=fr,
                         nofund=bool(not np.isfinite(rate)) if x_abs // 480 > e_abs // 480 else False, hold=int(xm - k + 1) * bm, xk=xm))
    return recs, fun, dict(S=S, VW=VW, R=R, lab=lab, valid=valid, atr=R["atr"], P=P, S1=S1, R1=R1, C0=C0, kk=kk)


PLACEBO_K = 10  # entry grid step in minutes (placebo)


def placebo_pool(D, F, HM, R4, labels, fund, coin, S, VW, R, lab, valid, P, S1):
    """random-entry pool for the NY long row on VAL MARKUP days: entry at the OPEN of a bar on a 10-minute grid from open+60 min, same stop / exit / fee logic."""
    bm, nb, open_min = S.bm, S.nb, S.open_min
    nb1 = 60 // bm
    sig = S.abs_day * DAY + (open_min + 60) * 60000
    days = np.flatnonzero((lab == "MARKUP") & valid & (sig >= SPLIT_MS))
    grid = list(range(nb1, nb - 1, PLACEBO_K // bm))
    rows = []
    for i in days:
        for gi, k in enumerate(grid):
            e = S.O[i, k]
            if not np.isfinite(e):
                continue
            x, xm, dist, stop = simulate(1, S.O[i], S.H[i], S.L[i], S.C[i], S.CF[i], VW[i], k, float(e), float(R["atr"][i]), bm, open_min)
            day_ms = int(S.abs_day[i]) * DAY
            e_abs = day_ms // 60000 + open_min + k * bm
            x_abs = day_ms // 60000 + open_min + (xm + 1) * bm
            rate = rate_at(fund, (x_abs // 480) * 480 * 60000) if x_abs // 480 > e_abs // 480 else 0.0
            fr = funding_r(1, float(e), dist, e_abs, x_abs, rate)
            atl = bool(at_level(1, np.array([e]), P[i], S1[i], 0.0, R["atr"][i])[0])
            rows.append((coin, gi, int(S.abs_day[i]), bool(R["v1"][i]), bool(R["v2"][i]), atl, (x - e) / dist, fee_r(e, x, dist, 12.0), fee_r(e, x, dist, 6.0), fr))
    return rows


# ------------------------------------------------------------------ cells
CELLS = [
    ("P1", "PRIMARY", "MARKUP", "V0", "+2%", "all", "NY 1m/1h"),
    ("P2", "PRIMARY", "MARKUP", "V0", "+1%", "all", "NY 1m/1h"),
    ("P3", "PRIMARY", "MARKUP", "V1", "+2%", "all", "NY 1m/1h/4h"),
    ("P4", "PRIMARY", "MARKUP", "V2", "+2%", "all", "NY 1m/1h/4h/1d"),
    ("P5", "PRIMARY", "MARKUP", "V0", "+2%", "at-level", "NY 1m/1h"),
    ("C1", "CONTROL", "MARKUP", "V0", "+2%", "away", "NY 1m/1h"),
    ("C2", "CONTROL", "ACCUM-RANGE", "V0", "+2%", "all", "NY 1m/1h"),
    ("C3", "CONTROL", "DISTRIBUTION", "V0", "+2%", "all", "NY 1m/1h"),
    ("C4", "CONTROL", "MARKDOWN", "V0 mirror short", "-2%", "all", "NY 1m/1h"),
    ("C5", "CONTROL", "MARKUP", "V0 UTC-day row", "+2%", "all", "UTC 1m/1h"),
    ("C6", "CONTROL", "MARKUP", "V0 15m trap, 20 coins", "+2%", "all", "NY 15m/1h"),
    ("C7", "CONTROL", "MARKUP", "V0 AND NOT V1", "+2%", "all", "NY 1m/1h/4h"),
    ("C8", "CONTROL", "MARKUP", "V0 AND V1 AND NOT V2", "+2%", "all", "NY 1m/1h/4h/1d"),
    ("C9", "CONTROL", "MARKUP", "placebo for P1", "n/a", "all", "NY 1m"),
    ("C10", "CONTROL", "MARKUP", "placebo for P5", "n/a", "at-level", "NY 1m"),
]
PRIMARY = [c[0] for c in CELLS if c[1] == "PRIMARY"]


def cell_masks(T):
    """boolean mask of trades per traded cell (C9/C10 are placebo rows, built elsewhere). A trade of a control phase can never enter a primary cell:
    every primary mask requires src NY1m, side +1 and phase MARKUP."""
    src, side, ph = T["src"], T["side"], T["ph"]
    ny = (src == "NY1m") & (side == 1)
    mk = ny & (ph == "MARKUP")
    s2, v1, v2, atl = T["scan2"], T["v1"], T["v2"], T["atl"]
    return {
        "P1": mk & s2, "P2": mk, "P3": mk & s2 & v1, "P4": mk & s2 & v1 & v2, "P5": mk & s2 & atl,
        "C1": mk & s2 & ~atl, "C2": ny & (ph == "ACCUM-RANGE") & s2, "C3": ny & (ph == "DISTRIBUTION") & s2,
        "C4": (src == "NY1m") & (side == -1) & (ph == "MARKDOWN") & s2,
        "C5": (src == "UTC1m") & (side == 1) & (ph == "MARKUP") & s2,
        "C6": (src == "NY15m") & (side == 1) & (ph == "MARKUP") & s2,
        "C7": mk & s2 & ~v1, "C8": mk & s2 & v1 & ~v2,
    }


# ------------------------------------------------------------------ statistics
def boot_trade(R, nb, seed):
    n = len(R)
    rng = np.random.default_rng(seed)
    out, chunk, done = [], max(1, int(2e6 // n)), 0
    while done < nb:
        b = min(chunk, nb - done)
        out.append(R[rng.integers(0, n, (b, n))].mean(axis=1))
        done += b
    return np.concatenate(out)


def boot_day(R, day, nb, seed):
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    nn = np.bincount(inv).astype(float)
    D = len(u)
    rng = np.random.default_rng(seed)
    out, chunk, done = [], max(1, int(2e6 // D)), 0
    while done < nb:
        b = min(chunk, nb - done)
        ix = rng.integers(0, D, (b, D))
        out.append(sR[ix].sum(axis=1) / nn[ix].sum(axis=1))
        done += b
    return np.concatenate(out)


def ex_best5(R, day):
    """mean net R per trade after removing the 5 best DAYS (by summed R)."""
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    worst = np.argsort(-sR)[:5]
    m = ~np.isin(inv, worst)
    return float(R[m].mean()) if m.any() else float("nan")


def bh(ps, q=0.10):
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        j = order[rank - 1]
        prev = min(prev, ps[j] * m / rank)
        adj[j] = prev
    return [float(x) for x in adj]


def net_of(T, bp):
    f = T["f12"] if bp == 12 else T["f6"]
    return T["g"] - f - T["fund"]


def stats(T, seed=11):
    n = len(T["g"])
    if n == 0:
        return dict(n=0)
    R12, R6 = net_of(T, 12), net_of(T, 6)
    day = T["abs_day"]
    bt = boot_trade(R12, NB_BOOT, seed) if n > 1 else np.array([np.nan])
    bd = boot_day(R12, day, NB_BOOT, seed + 1) if n > 1 else np.array([np.nan])
    return dict(n=int(n), days=int(len(np.unique(day))), gross=float(T["g"].mean()), fee12=float(T["f12"].mean()), fee6=float(T["f6"].mean()), fund=float(T["fund"].mean()),
                net12=float(R12.mean()), net12_nofund=float((T["g"] - T["f12"]).mean()), net6=float(R6.mean()), win=float((R12 > 0).mean() * 100),
                ci_trade_lo=float(np.percentile(bt, 2.5)), ci_day_lo=float(np.percentile(bd, 2.5)), ci_day_hi=float(np.percentile(bd, 97.5)),
                p_day_le0=float((1 + (bd <= 0).sum()) / (len(bd) + 1)), ex5=ex_best5(R12, day), hold_min=float(np.mean(T["hold"])))


def sub(T, m):
    return {k: v[m] for k, v in T.items()}


def placebo_p(real_net, trades_val, pool, cellmask_pool, B=2000, seed=5):
    """placebo: for each real trade a random pool entry of the SAME coin, same entry clock (10-min grid), same layer / at-level flags, a random MARKUP VAL day.
    p = (1 + #(placebo mean >= real mean)) / (B + 1)."""
    rng = np.random.default_rng(seed)
    coin, gi = pool["coin"], pool["gi"]
    net = pool["net12"]
    tot = np.zeros(B)
    n = len(trades_val["g"])
    for c, kk in zip(trades_val["coin"], trades_val["gi"]):
        sel = np.flatnonzero(cellmask_pool & (coin == c) & (gi == kk))
        if len(sel) == 0:
            sel = np.flatnonzero(cellmask_pool & (coin == c))
        if len(sel) == 0:
            return dict(p=float("nan"), mean=float("nan"), note="empty pool")
        tot += net[sel[rng.integers(0, len(sel), B)]]
    pm = tot / n
    return dict(p=float((1 + (pm >= real_net).sum()) / (B + 1)), mean=float(pm.mean()), lo=float(np.percentile(pm, 2.5)), hi=float(np.percentile(pm, 97.5)))


# ------------------------------------------------------------------ run
def git_state():
    def g(*a):
        return subprocess.run(["git", "-C", str(HERE)] + list(a), capture_output=True, text=True).stdout.strip()
    return g("rev-parse", "HEAD"), g("status", "--porcelain", "--", str(HERE / "study.py"), str(HERE / "PRE_REG.md"), str(HERE / "test_study.py"))


def provenance_line(name, b, step):
    return dict(file=name, key=b["key"], first=pd.to_datetime(int(b["t"][0]), unit="ms").strftime("%Y-%m-%d %H:%M"),
                last=pd.to_datetime(int(b["t"][-1]), unit="ms").strftime("%Y-%m-%d %H:%M"), rows=int(len(b["t"])),
                gaps=int((np.diff(b["t"]) > step).sum()), missing=int(((np.diff(b["t"]) // step) - 1).sum()))


def concat(recs):
    df = pd.DataFrame(recs)
    return {k: df[k].to_numpy() for k in df.columns}


FUN0 = dict(days=0, valid=0, scan_hi=0, trap=0, conf=0, noskip=0, hm=0, touch=0)


def funnel_update(funnel, src, side, phases, X):
    """cumulative funnel per (row, side, phase, split): days, valid, scanner, trap, confirm, skip, HM, VWAP touch (counts of coin-days)."""
    S = X["S"]
    sig = S.abs_day * DAY + (S.open_min + 60) * 60000
    C0, R = X["C0"], X["R"]
    for sp, mk in (("DEV", sig < SPLIT_MS), ("VAL", sig >= SPLIT_MS)):
        for ph in phases:
            inph = mk & (X["lab"] == ph)
            st = funnel.setdefault(f"{src}|{side}|{ph}|{sp}", dict(FUN0))
            a = inph & X["valid"]
            st["days"] += int(inph.sum())
            st["valid"] += int(a.sum())
            for key, cond in (("scan_hi", C0["scan_hi"]), ("trap", C0["trap"]), ("conf", C0["conf"]), ("noskip", ~C0["skip"]), ("hm", R["hm"]), ("touch", X["kk"] >= 0)):
                a = a & cond
                st[key] += int(a.sum())


def run():
    head, dirty = git_state()
    if dirty and not os.environ.get("NKN_ALLOW_DIRTY"):
        print("REFUSED: uncommitted study.py / PRE_REG.md / test_study.py: " + dirty)
        sys.exit(2)
    labels = load_labels()
    prov, funnel, trades, pool_rows, daymix, cov = [], {}, [], [], [], {}
    BTC = None
    for coin in COINS_1M:
        path = FETCHED / f"{coin}USDT_1m.npz"
        b = load_npz(path, 60000)
        pl = provenance_line(path.name, b, 60000)
        prov.append(pl)
        print("1m", pl, flush=True)
        D = dense(b, 60000)
        del b
        F = daily_feats(D)
        if coin == "BTC":
            BTC = F
        HM, R4, fund = hm_pack(D), rsi4h(D), load_funding(coin)
        for row, side, phases, src in (("NY", 1, ("MARKUP", "ACCUM-RANGE", "DISTRIBUTION"), "NY1m"), ("NY", -1, ("MARKDOWN",), "NY1m"), ("UTC", 1, ("MARKUP",), "UTC1m")):
            recs, fun, X = sim_row(D, F, HM, R4, row, side, phases, labels, BTC, fund, coin, src)
            trades += recs
            funnel_update(funnel, src, side, phases, X)
            if row == "NY" and side == 1:
                pool_rows += placebo_pool(D, F, HM, R4, labels, fund, coin, X["S"], X["VW"], X["R"], X["lab"], X["valid"], X["P"], X["S1"])
                daymix.append((coin, X["lab"], X["S"].abs_day * DAY + (X["S"].open_min + 60) * 60000))
                cov[coin] = int(X["valid"].sum())
        del D
    prov15 = []
    for coin in COINS_15M:
        path = SPOT15 / f"{coin}USDT_15m.npz"
        try:
            b = load_npz(path, 900000)
        except AssertionError as ex:
            prov15.append(dict(file=path.name, excluded=str(ex)))
            print("15m EXCLUDED", path.name, ex, flush=True)
            continue
        pl = provenance_line(path.name, b, 900000)
        prov15.append(pl)
        print("15m", pl, flush=True)
        D = dense(b, 900000)
        F = daily_feats(D)
        HM, R4, fund = hm_pack(D), rsi4h(D), load_funding(coin)
        recs, fun, X = sim_row(D, F, HM, R4, "NY", 1, ("MARKUP",), labels, BTC, fund, coin, "NY15m")
        trades += recs
        funnel_update(funnel, "NY15m", 1, ("MARKUP",), X)
        del D
    T = concat(trades)
    out = analyse(T, pool_rows, funnel, daymix, labels, prov, prov15, cov)
    out["git_head_at_run"] = head
    out["code_sha256"] = hashlib.sha256((HERE / "study.py").read_bytes()).hexdigest()
    (HERE / "results.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out["summary"], indent=1))


def analyse(T, pool_rows, funnel, daymix, labels, prov, prov15, cov):
    masks = cell_masks(T)
    sig = T["sig_ms"]
    dev, val = sig < SPLIT_MS, sig >= SPLIT_MS
    pool = {k: np.array([r[i] for r in pool_rows]) for i, k in enumerate(["coin", "gi", "day", "v1", "v2", "atl", "g", "f12", "f6", "fund"])}
    pool["net12"] = pool["g"] - pool["f12"] - pool["fund"]
    pool["net6"] = pool["g"] - pool["f6"] - pool["fund"]
    # entry-clock index of a real trade on the 10-minute grid (NY 1m row)
    nb1 = 60
    T["gi"] = np.where(T["src"] == "NY1m", np.clip(np.rint((T["k"] - nb1) / PLACEBO_K).astype(int), 0, None), 0)
    # ---- DEV check (printed and stored BEFORE the validation statistics are computed)
    res = {"cells": {}, "dev_check": {}}
    for cid, role, *_ in CELLS:
        if cid in ("C9", "C10"):
            continue
        m = masks[cid]
        d = stats(sub(T, m & dev), seed=21)
        res["cells"].setdefault(cid, {})["DEV"] = d
        if role == "PRIMARY":
            ok = d["n"] > 0 and d["gross"] >= 2 * d["fee12"]
            res["dev_check"][cid] = dict(n=d["n"], gross=d.get("gross"), fee12=d.get("fee12"), gross_ge_2x_fee=bool(ok))
    print("DEV check (gross >= 2 x fee R):", json.dumps(res["dev_check"]), flush=True)
    for cid, role, *_ in CELLS:
        if cid in ("C9", "C10"):
            continue
        m = masks[cid] & val
        s = stats(sub(T, m), seed=31)
        res["cells"][cid]["VAL"] = s
        if role == "PRIMARY" and s["n"] > 0:
            Y = sub(T, m)
            pm = pool["day"] >= 0  # placebo: VAL MARKUP pool, flagged per cell
            if cid == "P3":
                pm = pool["v1"]
            elif cid == "P4":
                pm = pool["v1"] & pool["v2"]
            elif cid == "P5":
                pm = pool["atl"]
            pr = placebo_p(s["net12"], Y, pool, pm)
            s["placebo"] = pr
    # ---- BH across the 5 primary cells
    ps = [res["cells"][c]["VAL"].get("p_day_le0", 1.0) if res["cells"][c]["VAL"]["n"] > 1 else 1.0 for c in PRIMARY]
    for c, q in zip(PRIMARY, bh(np.array(ps))):
        res["cells"][c]["VAL"]["bh_q"] = q
    # ---- C9 / C10 placebo rows (pool means) and at-level share
    for cid, pm in (("C9", pool["day"] >= 0), ("C10", pool["atl"])):
        R = pool["net12"][pm]
        res["cells"][cid] = {"VAL": dict(n=int(pm.sum()), gross=float(pool["g"][pm].mean()), fee12=float(pool["f12"][pm].mean()), net12=float(R.mean()), net6=float(pool["net6"][pm].mean()),
                                         win=float((R > 0).mean() * 100), days=int(len(np.unique(pool["day"][pm]))))}
    p1 = masks["P1"]
    res["atlevel_share"] = {sp: (float(T["atl"][p1 & mk].mean()) if (p1 & mk).any() else None) for sp, mk in (("DEV", dev), ("VAL", val))}
    res["atlevel_share_all"] = float(T["atl"][p1].mean()) if p1.any() else None
    res["index_filter_redundancy"] = float(T["idx"][p1].mean()) if p1.any() else None
    res["tag_mix_P1"] = {str(t): int(((T["tag"] == t) & p1).sum()) for t in (1, 0, -1)}
    res["nofund_share_P1"] = float(T["nofund"][p1].mean()) if p1.any() else None
    # layer lifts on gross R (VAL and DEV): V1 over V0, V2 over V1
    lift = {}
    for sp, mk in (("DEV", dev), ("VAL", val)):
        mk0 = masks["P1"] & mk
        mk1 = masks["P3"] & mk
        mk2 = masks["P4"] & mk
        lift[sp] = dict(V0=_mg(T, mk0), V1=_mg(T, mk1), V2=_mg(T, mk2), V0_notV1=_mg(T, masks["C7"] & mk), V1_notV2=_mg(T, masks["C8"] & mk))
    res["layer_lift_gross"] = lift
    # regime mix: cycle label share of session days, DEV and VAL (NY row, BTC-labelled days of all BTC-session days)
    coin, lab, sg = [x for x in daymix if x[0] == "BTC"][0]
    mix = {}
    for sp, mk in (("DEV", sg < SPLIT_MS), ("VAL", sg >= SPLIT_MS)):
        l = lab[mk]
        l = l[l != ""]
        mix[sp] = {u: round(float((l == u).mean()), 4) for u in sorted(set(l.tolist()))}
        mix[sp]["n_days"] = int(len(l))
    res["regime_mix"] = mix
    res["funnel"] = funnel
    res["provenance_1m"] = prov
    res["provenance_15m"] = prov15
    res["valid_days_per_coin"] = cov
    res["cells_total"] = len(CELLS)
    res["cells_primary"] = len(PRIMARY)
    res["cell_defs"] = CELLS
    # ---- verdicts
    markup_dev_share = mix["DEV"].get("MARKUP", 0.0)
    ver = {}
    for cid in PRIMARY:
        v, d = res["cells"][cid]["VAL"], res["dev_check"][cid]
        if v["n"] < MIN_N or markup_dev_share < 0.05:
            ver[cid] = "UNDERPOWERED"
            continue
        pl = v.get("placebo", {})
        ok = (v["net12"] > 0 and v["ci_trade_lo"] > 0 and v["ci_day_lo"] > 0 and v["ex5"] > 0 and pl.get("p", 1) < 0.05 and v["bh_q"] <= 0.10 and d["gross_ge_2x_fee"])
        ver[cid] = "PASS" if ok else "FAIL"
    if res["atlevel_share_all"] is not None and res["atlevel_share_all"] > 0.90:
        ver["P5"] = "REDUNDANT (UNDERPOWERED)"
        res["cells"]["C1"]["VAL"]["note"] = "UNDERPOWERED by design rule (at-level share > 90%)"
    res["verdicts"] = ver
    allv = list(ver.values())
    overall = "PASS" if "PASS" in allv else ("FAIL" if any(x == "FAIL" for x in allv) else "UNDERPOWERED")
    pv = [(c, res["cells"][c]["VAL"]) for c in PRIMARY if res["cells"][c]["VAL"]["n"] > 0]
    best = max(pv, key=lambda x: x[1]["net12"]) if pv else None
    res["summary"] = dict(verdict=overall, best_primary=(best[0] if best else None), best_net12=(best[1]["net12"] if best else None), n_val=(best[1]["n"] if best else 0),
                          verdicts=ver, underpowered=int(sum(1 for x in allv if x.startswith(("UNDER", "REDUN")))))
    return res


def _mg(T, m):
    return dict(n=int(m.sum()), gross=float(T["g"][m].mean()) if m.any() else None)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        print(__doc__)
