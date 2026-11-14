"""NKN-05 weekly HM buy state in the post-fall turn cell (PRE_REG.md). Pure functions are importable (tests use synthetic data);
`python study.py run` reads the shared cache read-only and writes results.json (RESULT.md comes from report.py).
Time: all timestamps are epoch ms UTC. Weeks start Monday 00:00 UTC (week number wn = (t - 4 days) // 7 days)."""
import sys, json, time, csv
import datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DAY, WEEK = 86400000, 7 * 86400000
MON = 4 * DAY                      # 1970-01-05 is the first Monday
SPLIT_MS = 1704067200000           # 2024-01-01 00:00 UTC; DEV = signal week start < SPLIT_MS
CACHE = Path(r"F:\MTS\data_cache")
PHASE_CSV = CACHE / "mts_brains" / "phase_daily.csv"
HTF_DIR = CACHE / "binance_spot_htf"
FUND_DIR = CACHE / "binance_futures" / "nkp1"
UNIVERSE = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT", "TRXUSDT", "LINKUSDT", "LTCUSDT",
            "BCHUSDT", "XLMUSDT", "ETCUSDT", "ATOMUSDT", "ALGOUSDT", "AVAXUSDT", "DOTUSDT", "FILUSDT", "NEARUSDT", "UNIUSDT"]
HOLDOUT = ["AAVEUSDT", "ENJUSDT", "GRTUSDT", "HBARUSDT", "MANAUSDT", "SANDUSDT", "THETAUSDT", "XTZUSDT"]
# ---- parameters (labels in PRE_REG.md) ----
MIN_WEEKS = 52          # a coin enters from its 52nd week (OURS)
FLOOR_R = 0.005         # R floor (OURS)
ATR_MULT = 0.6          # R = max(0.5%, 0.6 x weekly ATR14) (OURS)
HOLD_W = 4              # gating horizon, weeks (OURS)
LEVEL_ATR = 1.0         # AT-level band, weekly ATR14 (OURS)
HORIZONS = (1, 2, 4)
NB, NPLACEBO = 5000, 1000
N_MIN, WEEKS_MIN = 100, 20
LABELS = ["CAPITULATION", "MARKDOWN", "RELIEF", "ACCUM-RANGE", "MARKUP", "DISTRIBUTION"]
LAB_ID = {n: i + 1 for i, n in enumerate(LABELS)}
CYC_ID = {"BEAR": 1, "BASE": 2, "BULL": 3}
PC_LABS = (LAB_ID["RELIEF"], LAB_ID["ACCUM-RANGE"])
PC_CYC = (CYC_ID["BEAR"], CYC_ID["BASE"])


# ---------------- loading ----------------
def check_series(t, step_ms, name, key):
    d = np.diff(t)
    assert (d > 0).all(), f"{name}: timestamps not strictly increasing"
    assert (d % step_ms == 0).all() and d.min() == step_ms, f"{name}: bar step not constant (min diff {d.min()} vs {step_ms})"
    return dict(file=name, key=key, n=int(len(t)), first=int(t[0]), last=int(t[-1]), gaps=int((d > step_ms).sum()), step_ms=int(step_ms))


def load_fine(path, step_ms):
    """-> ((t,o,h,l,c), provenance) from an npz: named arrays t|ts,o,h,l,c,v or one 2-D array 'a' (t,o,h,l,c,v). Asserts the time key exists,
    strictly increasing, every difference a positive multiple of step_ms and the smallest difference == step_ms (gaps are allowed and counted)."""
    z = np.load(path)
    if "a" in z.files:
        a = z["a"]
        t, o, h, l, c = (a[:, k] for k in range(5))
        key = "a[:,0]"
    else:
        key = "t" if "t" in z.files else "ts"
        assert key in z.files, f"{path}: no time key in {z.files}"
        t, o, h, l, c = z[key], z["o"], z["h"], z["l"], z["c"]
    t = t.astype(np.int64)
    return (t, o.astype(float), h.astype(float), l.astype(float), c.astype(float)), check_series(t, step_ms, str(path), key)


def resample(t, o, h, l, c, period, anchor, step, min_cov):
    """complete groups only: first fine bar at the group start, last fine bar at group end - step, coverage >= min_cov of period/step bars.
    group start = anchor + k*period. Returns (start_ms, o, h, l, c)."""
    g = (t - anchor) // period
    idx = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    ends = np.r_[idx[1:], len(t)]
    start = anchor + g[idx] * period
    cnt = ends - idx
    ok = (t[idx] == start) & (t[ends - 1] == start + period - step) & (cnt >= min_cov * period / step)
    hh = np.maximum.reduceat(h, idx)
    ll = np.minimum.reduceat(l, idx)
    return start[ok], o[idx][ok], hh[ok], ll[ok], c[ends - 1][ok]


def load_funding(sym):
    p = FUND_DIR / f"{sym}_funding.csv"
    if not p.exists():
        return None
    a = np.loadtxt(p, delimiter=",", skiprows=1)
    ts = a[:, 0].astype(np.int64)
    assert (np.diff(ts) > 0).all(), f"{p}: funding ts not increasing"
    return ts, a[:, 1], dict(file=str(p), n=int(len(ts)), first=int(ts[0]), last=int(ts[-1]))


# ---------------- indicators (causal: value at i uses bars <= i) ----------------
def ewm(x, alpha):
    """pandas ewm(adjust=False): starts at the first non-NaN value; later NaN inputs carry the last value."""
    out = np.full(len(x), np.nan)
    s = np.nan
    for i, v in enumerate(x):
        if np.isnan(v):
            out[i] = s
            continue
        s = v if np.isnan(s) else s + alpha * (v - s)
        out[i] = s
    return out


def rsi_wilder(c, n):
    d = np.r_[np.nan, np.diff(c)]
    up = ewm(np.where(np.isnan(d), np.nan, np.maximum(d, 0)), 1.0 / n)
    dn = ewm(np.where(np.isnan(d), np.nan, np.maximum(-d, 0)), 1.0 / n)
    with np.errstate(all="ignore"):
        return 100 - 100 / (1 + up / np.where(dn == 0, np.nan, dn))


def wma(x, n):
    w = np.arange(n, 0, -1, dtype=float)       # newest bar weight n
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        seg = x[i - n + 1:i + 1][::-1]
        if not np.isnan(seg).any():
            out[i] = (w * seg).sum() / w.sum()
    return out


def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(x, n).mean(axis=1)
    return out


def atr_wilder(h, l, c, n=14):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.fmax(np.fmax(h - l, np.abs(h - pc)), np.abs(l - pc))
    return ewm(tr, 1.0 / n)


def hm_state(c):
    """+1 BUY (red < green AND red < RSI9), -1 SELL (red > green AND red > RSI9), 0 NEUTRAL or NaN. green = EMA3(RSI9), red = WMA21(RSI9). OURS."""
    r = rsi_wilder(c, 9)
    g = ewm(r, 0.5)
    red = wma(r, 21)
    s = np.zeros(len(c), dtype=np.int8)
    with np.errstate(invalid="ignore"):
        s[(red < g) & (red < r)] = 1
        s[(red > g) & (red > r)] = -1
    return s


def week_features(wh, wl, wc):
    """all columns at the CLOSE of weekly bar i."""
    atr = atr_wilder(wh, wl, wc, 14)
    s50 = sma(wc, 50)
    with np.errstate(invalid="ignore"):
        near = np.abs(wc - s50) <= LEVEL_ATR * atr
        lvl = np.where(np.isnan(s50) | np.isnan(atr), -1, np.where(near & (wc >= s50), 0, np.where(near, 1, 2))).astype(np.int8)
    return dict(hm=hm_state(wc), atr=atr, s50=s50, s20=sma(wc, 20), lvl=lvl)


def daily_gate(dc):
    """V2 daily agreement at the CLOSE of daily bar j: RSI14 > 50 AND close > SMA20 (NaN -> False)."""
    r = rsi_wilder(dc, 14)
    s = sma(dc, 20)
    with np.errstate(invalid="ignore"):
        return (r > 50) & (dc > s)


# ---------------- trades ----------------
def simulate_trade(ft, fo, fl, t_entry, t_exit, e, x_open, df):
    """long, entry at e (open of the entry bar), stop e*(1-df), time exit at x_open (open of the exit week). Fine bars with t_entry <= t < t_exit
    are checked; the first bar whose low <= stop stops the trade, filled at the bar open if the bar opens at/below the stop (gap) else at the stop."""
    i0, i1 = np.searchsorted(ft, t_entry), np.searchsorted(ft, t_exit)
    stop = e * (1 - df)
    hit = np.flatnonzero(fl[i0:i1] <= stop)
    if hit.size == 0:
        return x_open
    k = i0 + hit[0]
    return fo[k] if fo[k] <= stop else stop


def fee_r(e, x, df, bp):
    """round-trip bp: bp/2 charged on entry notional AND bp/2 on exit notional, divided by the stop distance (df*e), in R."""
    return (bp / 2e4) * (e + x) / (df * e)


def stop_frac(atr, e):
    return np.maximum(FLOOR_R, ATR_MULT * atr / e)


# ---------------- per-coin rows ----------------
FIELDS = ["coin", "wn", "sig_t", "hm", "lvl", "v1", "v2", "fund", "lab", "cyc", "e", "x", "df", "ok_t"] + [f"f{h}" for h in HORIZONS]


def coin_rows(sym, fine, step, btc_week, fund, phase, is_btc, with_trades=True):
    """fine = (t,o,h,l,c). btc_week = (wn_array, close, sma20) of BTC. phase = (lab_by_day, cyc_by_day, day0). One row per signal week that has an entry
    week (wn+1) and is past the MIN_WEEKS rule. Signal columns use only data closed at the end of the signal week; forward columns are labelled f*/e/x."""
    ft, fo, fh, fl, fc = fine
    wt, wo, wh, wl, wc = resample(ft, fo, fh, fl, fc, WEEK, MON, step, 0.95)
    dt_, _, _, _, dc = resample(ft, fo, fh, fl, fc, DAY, 0, step, 0.90)
    wn = (wt - MON) // WEEK
    F = week_features(wh, wl, wc)
    gd = daily_gate(dc)
    dday = dt_ // DAY
    pos = {int(k): i for i, k in enumerate(wn)}
    rows = {k: [] for k in FIELDS}
    bw_pos = {int(k): i for i, k in enumerate(btc_week[0])}
    lab_by_day, cyc_by_day, day0 = phase
    for i in range(len(wn)):
        if i < MIN_WEEKS:
            continue
        j = pos.get(int(wn[i]) + 1)
        if j is None:
            continue
        entry_day = int(wt[j] // DAY)
        if is_btc:
            v1 = True
        else:
            b = bw_pos.get(int(wn[i]))
            v1 = bool(b is not None and not np.isnan(btc_week[2][b]) and btc_week[1][b] > btc_week[2][b])
        k = np.searchsorted(dday, entry_day - 1)
        v2 = bool(k < len(dday) and dday[k] == entry_day - 1 and gd[k])
        fu = np.nan
        if fund is not None:
            ts, rate = fund[0], fund[1]
            q = np.searchsorted(ts, int(wt[j]), side="left") - 1      # settlements strictly before the entry instant
            if q >= 8 and int(wt[j]) - ts[q] <= 9 * 3600000:
                fu = float(rate[q - 8:q + 1].mean())
        di = entry_day - day0
        lab = int(lab_by_day[di]) if 0 <= di < len(lab_by_day) else 0
        cyc = int(cyc_by_day[di]) if 0 <= di < len(cyc_by_day) else 0
        fw = []
        for h_ in HORIZONS:
            jj = pos.get(int(wn[i]) + 1 + h_)
            fw.append(wo[jj] / wo[j] - 1 if jj is not None else np.nan)
        e = x = df = np.nan
        ok_t = False
        if with_trades and not np.isnan(fw[2]) and not np.isnan(F["atr"][i]):
            jj = pos[int(wn[i]) + 1 + HOLD_W]
            e = wo[j]
            df = float(stop_frac(F["atr"][i], e))
            x = simulate_trade(ft, fo, fl, int(wt[j]), int(wt[jj]), e, wo[jj], df)
            ok_t = True
        for key, val in zip(FIELDS, [sym, int(wn[i]), int(wt[i]), int(F["hm"][i]), int(F["lvl"][i]), v1, v2, fu, lab, cyc, e, x, df, ok_t, *fw]):
            rows[key].append(val)
    return rows


def concat_rows(list_rows):
    out = {}
    for k in FIELDS:
        v = [x for r in list_rows for x in r[k]]
        out[k] = np.array(v, dtype=object) if k == "coin" else np.array(v)
    for k in ("hm", "lvl", "lab", "cyc"):
        out[k] = out[k].astype(int)
    for k in ("v1", "v2", "ok_t"):
        out[k] = out[k].astype(bool)
    for k in ("fund", "e", "x", "df") + tuple(f"f{h}" for h in HORIZONS):
        out[k] = out[k].astype(float)
    out["wn"] = out["wn"].astype(np.int64)
    out["sig_t"] = out["sig_t"].astype(np.int64)
    return out


# ---------------- phase file ----------------
def read_phase(path=PHASE_CSV):
    """-> (day_numbers, label_id, cycle_id, close_used); provisional rows dropped; empty label -> 0."""
    days, lab, cyc, cu = [], [], [], []
    with open(path) as f:
        first = f.readline()
        if not first.startswith("#"):
            f.seek(0)
        for r in csv.DictReader(f):
            if str(r.get("provisional", "False")).lower() == "true":
                continue
            days.append(dt.date.fromisoformat(r["date"]).toordinal() - 719163)
            lab.append(LAB_ID.get(r["label"], 0))
            cyc.append(CYC_ID.get(r["cycle"], 0))
            cu.append(float(r["close_used"]) if r["close_used"] not in ("", None) else np.nan)
    return np.array(days), np.array(lab), np.array(cyc), np.array(cu)


def phase_lag_check(days, close_used, btc_dday, btc_dclose):
    """poke test on real data: share of rows whose close_used equals the BTC daily close of day d-1 (lag 1) vs of day d (lag 0)."""
    m = {int(d): c for d, c in zip(btc_dday, btc_dclose)}
    r1 = r0 = n = 0
    for d, cu in zip(days, close_used):
        if np.isnan(cu) or int(d) - 1 not in m or int(d) not in m:
            continue
        n += 1
        r1 += abs(cu / m[int(d) - 1] - 1) < 1e-3
        r0 += abs(cu / m[int(d)] - 1) < 1e-3
    return dict(n=n, lag1=r1 / max(n, 1), lag0=r0 / max(n, 1))


def phase_arrays(days, lab, cyc, shift=0):
    """dense arrays by day number; shift=1 means the label used for day d is the file label of day d-1 (applied only if the file uses close d)."""
    day0 = int(days.min())
    n = int(days.max()) - day0 + 1
    la = np.zeros(n, dtype=int)
    ca = np.zeros(n, dtype=int)
    la[days - day0] = lab
    ca[days - day0] = cyc
    if shift:
        la = np.r_[0, la[:-1]]
        ca = np.r_[0, ca[:-1]]
    return la, ca, day0


# ---------------- cells ----------------
def split_of(T):
    return np.where(T["sig_t"] < SPLIT_MS, 0, 1)      # 0 DEV, 1 VAL, by the SIGNAL week start


def pc_mask(T):
    return np.isin(T["lab"], PC_LABS) & np.isin(T["cyc"], PC_CYC)


def cell_defs(T, fund_edges):
    """the 22 frozen cells (NKN-05.md): (id, role, mask over all coin-weeks, base mask = unconditional same-phase weeks, side). Split not applied here."""
    pc = pc_mask(T)
    buy, sell, neu = T["hm"] == 1, T["hm"] == -1, T["hm"] == 0
    not_btc = T["coin"] != "BTCUSDT"
    lab, lv, fu = T["lab"], T["lvl"], T["fund"]
    lo, hi = fund_edges if fund_edges is not None else (np.nan, np.nan)
    with np.errstate(invalid="ignore"):
        f1, f2, f3 = fu <= lo, (fu > lo) & (fu <= hi), fu > hi
    allm = lab > 0
    mk, md, ds = lab == LAB_ID["MARKUP"], lab == LAB_ID["MARKDOWN"], lab == LAB_ID["DISTRIBUTION"]
    return [
        ("P1", "PRIMARY", pc & buy, pc, "long"),
        ("P2", "PRIMARY", pc & buy & T["v1"], pc, "long"),
        ("P3", "PRIMARY", pc & buy & T["v1"] & T["v2"], pc, "long"),
        ("C1", "CONTROL", mk & buy, mk, "long"),
        ("C2", "CONTROL", md & buy, md, "long"),
        ("C3", "CONTROL", ds & buy, ds, "long"),
        ("C4", "CONTROL", pc & sell, pc, "sell-state"),
        ("C5", "CONTROL", pc, pc, "placebo (all PC weeks)"),
        ("C6", "CONTROL", pc & neu, pc, "neutral-state"),
        ("C7", "CONTROL", pc & buy & ~T["v1"] & not_btc, pc, "long"),
        ("R0", "REFERENCE", allm & buy, allm, "long"),
        ("L1", "CONTROL", pc & buy & (lv == 0), pc, "long"),
        ("L2", "CONTROL", pc & buy & (lv == 1), pc, "long"),
        ("L3", "CONTROL", pc & buy & (lv == 2), pc, "long"),
        ("L4", "CONTROL", pc & sell & (lv == 0), pc, "sell-state"),
        ("L5", "CONTROL", pc & sell & (lv == 1), pc, "sell-state"),
        ("L6", "CONTROL", pc & sell & (lv == 2), pc, "sell-state"),
        ("F1", "CONTROL", pc & buy & f1, pc, "long"),
        ("F2", "CONTROL", pc & buy & f2, pc, "long"),
        ("F3", "CONTROL", pc & buy & f3, pc, "long"),
        ("N1", "CONTROL", pc & buy, pc, "long, fee-net filtered entry (V0)"),
        ("N2", "CONTROL", pc & buy & T["v1"] & T["v2"], pc, "long, fee-net filtered entry (V2)"),
    ]


# ---------------- statistics ----------------
def cluster_arrays(R, wk):
    u, inv = np.unique(wk, return_inverse=True)
    return u, np.bincount(inv, weights=R, minlength=len(u)), np.bincount(inv, minlength=len(u)).astype(float), inv


def _boot(sum_fn, D, nb, seed):
    rng = np.random.default_rng(seed)
    out = []
    step = max(1, int(3e6 // max(D, 1)))
    for a in range(0, nb, step):
        out.append(sum_fn(rng.integers(0, D, (min(step, nb - a), D))))
    return np.concatenate(out)


def boot_mean_week(R, wk, nb=NB, seed=1):
    """calendar-week cluster bootstrap of the mean."""
    u, s, n, _ = cluster_arrays(R, wk)
    return _boot(lambda ix: s[ix].sum(1) / np.maximum(n[ix].sum(1), 1), len(u), nb, seed)


def boot_mean_iid(R, nb=NB, seed=2):
    return _boot(lambda ix: R[ix].mean(1), len(R), nb, seed)


def boot_diff_week(Rb, wb, Rs, ws, nb=NB, seed=3):
    """cluster bootstrap of mean(buy) - mean(sell), calendar weeks resampled jointly."""
    weeks = np.union1d(np.unique(wb), np.unique(ws))
    ib, isl = np.searchsorted(weeks, wb), np.searchsorted(weeks, ws)
    D = len(weeks)
    sb, nbb = np.bincount(ib, weights=Rb, minlength=D), np.bincount(ib, minlength=D).astype(float)
    ss, ns = np.bincount(isl, weights=Rs, minlength=D), np.bincount(isl, minlength=D).astype(float)
    return _boot(lambda ix: sb[ix].sum(1) / np.maximum(nbb[ix].sum(1), 1) - ss[ix].sum(1) / np.maximum(ns[ix].sum(1), 1), D, nb, seed)


def ex_best5_mean(R, wk):
    u, s, n, inv = cluster_arrays(R, wk)
    m = ~np.isin(inv, np.argsort(-s)[:5])
    return float(R[m].mean()) if m.any() else float("nan")


def ex_best5_diff(Rb, wb, Rs):
    u, s, n, inv = cluster_arrays(Rb, wb)
    m = ~np.isin(inv, np.argsort(-s)[:5])
    return float(Rb[m].mean() - Rs.mean()) if m.any() and len(Rs) else float("nan")


def p_one_sided(boot):
    """P(statistic <= 0) with +1 smoothing."""
    return (1 + int((boot <= 0).sum())) / (1 + len(boot))


def bh_q(p):
    p = np.asarray(p, float)
    m = len(p)
    o = np.argsort(p)
    q = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        i = o[rank - 1]
        prev = min(prev, p[i] * m / rank)
        q[i] = prev
    return q


def placebo_draws(values, month, pool_mask, cell_mask, nd=NPLACEBO, seed=5):
    """like-for-like random coin-weeks: pool = same phase cell (any HM state) and same split; the real cell's month-of-year spread is reproduced; matched
    count. values = per-row fwd4 return or net R. Returns nd draw means."""
    rng = np.random.default_rng(seed)
    pool = np.flatnonzero(pool_mask & ~np.isnan(values))
    cell = np.flatnonzero(cell_mask & ~np.isnan(values))
    if len(pool) == 0 or len(cell) == 0:
        return np.full(nd, np.nan)
    tot = np.zeros(nd)
    for m in np.unique(month[cell]):
        k = int((month[cell] == m).sum())
        pm = pool[month[pool] == m]
        if len(pm) == 0:
            pm = pool
        tot += values[pm][rng.integers(0, len(pm), (nd, k))].sum(1)
    return tot / len(cell)


def month_of_year(sig_t):
    return np.array([dt.datetime.fromtimestamp(int(t) // 1000, dt.timezone.utc).month for t in sig_t])


def grossR(T):
    return (T["x"] - T["e"]) / (T["e"] * T["df"])


def netR(T, bp):
    return grossR(T) - fee_r(T["e"], T["x"], T["df"], bp)


def cell_stats(T, defs):
    """every cell on DEV and VAL (descriptive numbers). n = coin-weeks with a 4-week forward return; n_tr = coin-weeks with a simulated trade."""
    sp = split_of(T)
    wk = T["wn"]
    R12, R6, G = netR(T, 12.0), netR(T, 6.0), grossR(T)
    for a in (R12, R6, G):
        a[~T["ok_t"]] = np.nan
    f4 = T["f4"]
    out = {}
    for cid, role, mask, base, side in defs:
        r = dict(role=role, side=side)
        for s, name in ((0, "DEV"), (1, "VAL")):
            m = mask & (sp == s)
            me = m & ~np.isnan(f4)
            bs = base & (sp == s) & ~np.isnan(f4)
            mt = m & T["ok_t"]
            d = dict(n_all=int(m.sum()), n=int(me.sum()), weeks=int(len(np.unique(wk[me]))), n_tr=int(mt.sum()),
                     coins=int(len(np.unique(T["coin"][me]))) if me.any() else 0)
            for h_ in HORIZONS:
                v = T[f"f{h_}"][m]
                v = v[~np.isnan(v)]
                d[f"mean_f{h_}"] = float(v.mean()) if len(v) else np.nan
            d["excess_f4"] = float(f4[me].mean() - f4[bs].mean()) if me.any() and bs.any() else np.nan
            if mt.any():
                d.update(gross=float(G[mt].mean()), net12=float(R12[mt].mean()), net6=float(R6[mt].mean()), win=float((R12[mt] > 0).mean()))
            else:
                d.update(gross=np.nan, net12=np.nan, net6=np.nan, win=np.nan)
            if mt.sum() >= 2:
                bw = boot_mean_week(R12[mt], wk[mt])
                d["net12_week_ci_low"] = float(np.percentile(bw, 2.5))
            r[name] = d
        out[cid] = r
    return out


def primary_gates(T, defs):
    """full gate machinery for P1-P3 on VAL: the event study (4-week return, buy minus sell in PC) AND the tradeable filtered-entry version."""
    sp = split_of(T)
    mon = month_of_year(T["sig_t"])
    wk, f4 = T["wn"], T["f4"]
    R12 = netR(T, 12.0)
    R12[~T["ok_t"]] = np.nan
    pc = pc_mask(T)
    sell = pc & (T["hm"] == -1)
    res = {}
    for cid, role, mask, base, side in defs:
        if role != "PRIMARY":
            continue
        g = {"DEV": {}, "VAL": {}}
        for s, name in ((0, "DEV"), (1, "VAL")):
            m = mask & (sp == s) & ~np.isnan(f4)
            sm = sell & (sp == s) & ~np.isnan(f4)
            g[name]["diff"] = float(f4[m].mean() - f4[sm].mean()) if m.sum() >= 2 and sm.sum() >= 2 else np.nan
        v = g["VAL"]
        m = mask & (sp == 1) & ~np.isnan(f4)
        sm = sell & (sp == 1) & ~np.isnan(f4)
        if m.sum() >= 2 and sm.sum() >= 2:
            b = boot_diff_week(f4[m], wk[m], f4[sm], wk[sm])
            v["ev_ci_low"] = float(np.percentile(b, 2.5))
            v["ev_p"] = p_one_sided(b)
            v["ev_ex5"] = ex_best5_diff(f4[m], wk[m], f4[sm])
            pl = placebo_draws(f4, mon, pc & (sp == 1), mask & (sp == 1))
            v["ev_placebo_mean"] = float(np.nanmean(pl))
            v["ev_placebo_p"] = (1 + int((pl >= f4[m].mean()).sum())) / (1 + len(pl))
        mt = mask & (sp == 1) & T["ok_t"]
        if mt.sum() >= 2:
            R = R12[mt]
            v["tr_ci_low"] = float(np.percentile(boot_mean_iid(R), 2.5))
            bw = boot_mean_week(R, wk[mt])
            v["tr_week_ci_low"] = float(np.percentile(bw, 2.5))
            v["tr_blk4_ci_low"] = float(np.percentile(boot_mean_week(R, wk[mt] // 4, NB, 4), 2.5))   # info only: 4-week blocks (overlapping holds)
            v["tr_p"] = p_one_sided(bw)
            v["tr_ex5"] = ex_best5_mean(R, wk[mt])
            pl = placebo_draws(R12, mon, pc & (sp == 1) & T["ok_t"], mt)
            v["tr_placebo_mean"] = float(np.nanmean(pl))
            v["tr_placebo_p"] = (1 + int((pl >= R.mean()).sum())) / (1 + len(pl))
        res[cid] = g
    ids = list(res)
    for key, qk in (("ev_p", "ev_q"), ("tr_p", "tr_q")):
        qs = bh_q([res[c]["VAL"].get(key, 1.0) for c in ids])
        for c, q in zip(ids, qs):
            res[c]["VAL"][qk] = float(q)
    return res


def verdict_cell(cid, st, g):
    """per-cell verdict on VAL: UNDERPOWERED (n < 100 coin-weeks or < 20 distinct weeks), else PASS only if every event-study AND tradeable gate holds."""
    v, dv, gv = st[cid]["VAL"], g[cid]["DEV"], g[cid]["VAL"]
    if v["n"] < N_MIN or v["n_tr"] < N_MIN or v["weeks"] < WEEKS_MIN:
        return "UNDERPOWERED" + ("-WEEKS" if v["n"] >= N_MIN and v["weeks"] < WEEKS_MIN else "")
    gates = [gv.get("ev_ci_low", -1) > 0, gv.get("ev_ex5", -1) > 0, gv.get("ev_placebo_p", 1) <= 0.05, dv["diff"] > 0, gv.get("ev_q", 1) <= 0.10,
             v["net12"] > 0, gv.get("tr_ci_low", -1) > 0, gv.get("tr_week_ci_low", -1) > 0, gv.get("tr_ex5", -1) > 0,
             gv.get("tr_placebo_p", 1) <= 0.05, gv.get("tr_q", 1) <= 0.10]
    return "PASS" if all(bool(x) for x in gates) else "FAIL"


def overall(verd):
    v = list(verd.values())
    if "PASS" in v:
        return "PASS"
    if all(x.startswith("UNDERPOWERED") for x in v):
        return "UNDERPOWERED"
    return "FAIL"


def fund_terciles(T):
    """frozen on DEV: terciles of the funding mean over DEV PC buy coin-weeks with funding."""
    m = pc_mask(T) & (T["hm"] == 1) & (split_of(T) == 0) & ~np.isnan(T["fund"])
    if m.sum() < 30:
        return None
    return float(np.percentile(T["fund"][m], 100 / 3)), float(np.percentile(T["fund"][m], 200 / 3))


def spells_in(T, m):
    """distinct BTC label spells among the selected rows: a maximal run of consecutive calendar weeks sharing one label+cycle."""
    if not m.any():
        return 0
    wn, key = T["wn"][m], (T["lab"] * 10 + T["cyc"])[m]
    k = {int(w): int(key[wn == w][0]) for w in np.unique(wn)}
    n, pw, pk = 0, None, None
    for w in sorted(k):
        if pw is None or w != pw + 1 or k[w] != pk:
            n += 1
        pw, pk = w, k[w]
    return n


def descriptors(T):
    sp, pc, f4 = split_of(T), pc_mask(T), T["f4"]
    out = {}
    for s, name in ((0, "DEV"), (1, "VAL")):
        m = sp == s
        n = max(int(m.sum()), 1)
        out[f"cycle_mix_{name}"] = {k: float((T["cyc"][m] == v).sum() / n) for k, v in CYC_ID.items()}
        out[f"label_mix_{name}"] = {k: float((T["lab"][m] == v).sum() / n) for k, v in LAB_ID.items()}
        out[f"pc_share_{name}"] = float(pc[m].sum() / n)
        out[f"pc_spells_{name}"] = spells_in(T, m & pc)
        out[f"pc_weeks_{name}"] = int(len(np.unique(T["wn"][m & pc])))
        g = {}
        for grp, lv in (("AT", (0, 1)), ("AWAY", (2,))):
            b = pc & (T["hm"] == 1) & m & np.isin(T["lvl"], lv) & ~np.isnan(f4)
            se = pc & (T["hm"] == -1) & m & np.isin(T["lvl"], lv) & ~np.isnan(f4)
            g[grp] = dict(n_buy=int(b.sum()), n_sell=int(se.sum()), gap=float(f4[b].mean() - f4[se].mean()) if b.sum() and se.sum() else None)
        out[f"HA2_{name}"] = g
        mb = pc & (T["hm"] == 1) & m
        nb_ = max(int(mb.sum()), 1)
        out[f"overlap_{name}"] = dict(n_buy=int(mb.sum()), kept_v1=float((mb & T["v1"]).sum() / nb_), kept_v2=float((mb & T["v1"] & T["v2"]).sum() / nb_))
    return out


def to_py(o):
    if isinstance(o, dict):
        return {k: to_py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def run():
    t0 = time.time()
    prov = []
    (bt, bo, bh, bl, bc), pv = load_fine(CACHE / "binance_spot" / "BTCUSDT_15m.npz", 900000)
    prov.append(pv)
    bwt, _, _, _, bwc = resample(bt, bo, bh, bl, bc, WEEK, MON, 900000, 0.95)
    btc_week = ((bwt - MON) // WEEK, bwc, sma(bwc, 20))
    bdt, _, _, _, bdc = resample(bt, bo, bh, bl, bc, DAY, 0, 900000, 0.90)
    days, lab, cyc, cu = read_phase()
    lag = phase_lag_check(days, cu, bdt // DAY, bdc)
    shift = 1 if lag["lag0"] > lag["lag1"] else 0
    phase = phase_arrays(days, lab, cyc, shift)
    xchk = {}
    for s in ("BTCUSDT", "ETHUSDT"):
        w = np.array(json.load(open(HTF_DIR / f"{s}_1w.json")), float)
        fine = load_fine(CACHE / "binance_spot" / f"{s}_15m.npz", 900000)[0]
        rt, ro, rh, rl, rc = resample(*fine, WEEK, MON, 900000, 0.95)
        _, a, b = np.intersect1d(rt, w[:, 0].astype(np.int64), return_indices=True)
        rel = lambda x, y: np.abs(x / y - 1)
        xchk[s] = dict(common_weeks=int(len(a)), max_rel_open=float(rel(ro[a], w[b, 1]).max()), max_rel_high=float(rel(rh[a], w[b, 2]).max()),
                       max_rel_low=float(rel(rl[a], w[b, 3]).max()), max_rel_close=float(rel(rc[a], w[b, 4]).max()), median_rel_close=float(np.median(rel(rc[a], w[b, 4]))))
    rows, rows_h, fcov = [], [], {}
    for sym in UNIVERSE:
        fine, pv = load_fine(CACHE / "binance_spot" / f"{sym}_15m.npz", 900000)
        prov.append(pv)
        fu = load_funding(sym)
        fcov[sym] = None if fu is None else fu[2]
        rows.append(coin_rows(sym, fine, 900000, btc_week, fu, phase, sym == "BTCUSDT"))
        print(f"{sym} rows={len(rows[-1]['wn'])} {time.time() - t0:.0f}s", flush=True)
    for sym in HOLDOUT:
        fine, pv = load_fine(CACHE / "binance_fresh" / "nk5_nyasia" / f"{sym}_5m.npz", 300000)
        prov.append(pv)
        rows_h.append(coin_rows(sym, fine, 300000, btc_week, None, phase, False))
        print(f"{sym} (holdout) rows={len(rows_h[-1]['wn'])} {time.time() - t0:.0f}s", flush=True)
    T, TH = concat_rows(rows), concat_rows(rows_h)
    edges = fund_terciles(T)
    defs = cell_defs(T, edges)
    st = cell_stats(T, defs)
    gates = primary_gates(T, defs)
    verd = {c: verdict_cell(c, st, gates) for c in gates}
    defsh = cell_defs(TH, None)
    sth = cell_stats(TH, defsh)
    gh = primary_gates(TH, defsh)
    isb = T["coin"] == "BTCUSDT"
    Tb = {k: v[isb] for k, v in T.items()}
    stb = cell_stats(Tb, cell_defs(Tb, None))
    out = dict(provenance=prov, funding_cov=fcov, phase_lag_check=lag, phase_shift_applied=shift, resampler_crosscheck=xchk, fund_edges=edges,
               cells=st, gates=gates, verdicts=verd, holdout=dict(cells={k: sth[k] for k in ("P1", "P2", "P3")}, gates=gh),
               btc_only={k: stb[k] for k in ("P1", "P2", "P3")}, descriptors=descriptors(T), n_rows=int(len(T["wn"])), n_rows_holdout=int(len(TH["wn"])),
               universe=UNIVERSE, holdout_coins=HOLDOUT, total_cells=22, primary_cells=3, overall=overall(verd), runtime_s=time.time() - t0)
    (HERE / "results.json").write_text(json.dumps(to_py(out), indent=1), encoding="utf-8")
    print("overall", out["overall"], verd, f"{time.time() - t0:.0f}s")
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        print(__doc__)
