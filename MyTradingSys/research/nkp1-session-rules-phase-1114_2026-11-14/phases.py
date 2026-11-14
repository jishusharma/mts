"""MTS BRAINS phase table (6 causal phases from BTC daily). Implements MTS_BRAINS_SPEC_1114 s1 exactly.
Label for UTC day d = state computed from closes through d-1 (PHASE_LAG=1). PHASE_LAG=0 is the deliberate look-ahead bug used by test_study.py."""
import os, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BTC_DAILY = HERE.parent / "btc_cycles_2026-11" / "btc_daily.csv"
BTC_TAIL = Path(r"F:\MTS\data_cache\binance_1d\BTCUSDT_1d_tail.csv")
SHARED = Path(r"F:\MTS\data_cache\mts_brains\phase_daily.csv")
PHASES = {1: "CAPITULATION", 2: "MARKDOWN", 3: "RELIEF", 4: "ACCUM-RANGE", 5: "MARKUP", 6: "DISTRIBUTION"}
ALLOWED = {1: 1, 2: -1, 3: 1, 4: 0, 5: 1, 6: -1}   # +1 long only, -1 short only, 0 both (ACCUM: long in lower half of 40d range, short in upper half)
HALVINGS = ["2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20"]


def lag():
    return int(os.environ.get("PHASE_LAG", "1"))


def load_btc_daily():
    d = pd.read_csv(BTC_DAILY, parse_dates=["date"]).set_index("date")[["high", "low", "close"]]
    if BTC_TAIL.exists():
        t = pd.read_csv(BTC_TAIL, parse_dates=["date"]).set_index("date")[["high", "low", "close"]]
        d = pd.concat([d, t[t.index > d.index[-1]]])
    d = d[~d.index.duplicated()].sort_index()
    return d.reindex(pd.date_range(d.index[0], d.index[-1], freq="D")).ffill()


def wilder_rsi(c, n=14):
    """Wilder RSI seeded with the simple mean of the first n changes (FORMULAS s1)."""
    x = c.to_numpy(float)
    out = np.full(len(x), np.nan)
    dlt = np.diff(x)
    if len(dlt) < n:
        return pd.Series(out, index=c.index)
    g = np.where(dlt > 0, dlt, 0.0)
    l = np.where(dlt < 0, -dlt, 0.0)
    ag, al = g[:n].mean(), l[:n].mean()
    out[n] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n, len(dlt)):
        ag = (ag * (n - 1) + g[i]) / n
        al = (al * (n - 1) + l[i]) / n
        out[i + 1] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return pd.Series(out, index=c.index)


def state_table(d):
    """per-day STATE computed from data through that day's close (no label lag yet)."""
    c, h, l = d.close, d.high, d.low
    s = pd.DataFrame(index=d.index)
    s["close"] = c
    s["sma20"], s["sma50"], s["sma200"] = c.rolling(20).mean(), c.rolling(50).mean(), c.rolling(200).mean()
    s["w200"] = c.rolling(1400).mean()
    s["s50"] = s.sma50 / s.sma50.shift(10) - 1
    s["r10"] = c / c.shift(10) - 1
    s["rb30"] = c / l.rolling(30).min() - 1
    s["dd"] = c / c.cummax() - 1
    s["rsi"] = wilder_rsi(c, 14)
    lo40, hi40 = l.rolling(40).min(), h.rolling(40).max()
    s["rng40"] = (hi40 - lo40) / lo40
    s["pos40"] = (c - lo40) / (hi40 - lo40)
    flag = (l < l.shift(1).rolling(60).min()).astype(float)
    s["newlow15"] = flag.rolling(15).max() > 0
    M = np.where((s.dd <= -0.20) & (c < s.sma200), "BEAR", np.where((c > s.w200) & (s.dd > -0.20), "BULL", "BASE"))
    s["M"] = M
    trig = (s.M != "BULL") & (s.r10 <= -0.20) & (s.rsi <= 30)
    cap = trig.astype(float).rolling(3).max() > 0
    ph = np.full(len(s), 6)
    # first match wins: assign from the lowest priority upward
    near50 = (c / s.sma50 - 1).abs() <= 0.07
    ph = np.where((c > s.sma50) & (s.s50 >= 0.01) & ((c > s.sma200) | (s.M == "BULL")), 5, ph)
    ph = np.where((s.M != "BULL") & (s.rng40 <= 0.30) & near50 & (~s.newlow15), 4, ph)
    ph = np.where((s.M != "BULL") & (c > s.sma20) & (s.rb30 >= 0.12) & (c <= 1.05 * s.sma200), 3, ph)
    ph = np.where((c < s.sma50) & (s.s50 <= -0.01) & ((s.M == "BEAR") | (c < s.sma200)), 2, ph)
    ph = np.where(cap, 1, ph)
    ph = pd.Series(ph, index=s.index).astype(float)
    ph[s.sma200.isna() | s.s50.isna() | s.rsi.isna() | s.rng40.isna() | s.dd.isna()] = np.nan
    s["phase_id"] = ph
    return s


def halving_age(idx):
    hv = pd.to_datetime(HALVINGS)
    out = []
    for t in idx:
        past = hv[hv <= t]
        out.append((t - past[-1]).days if len(past) else np.nan)
    return np.array(out)


def phase_daily(d=None, L=None):
    """label table indexed by UTC label day; day d uses state at d-L (L=1 causal)."""
    d = load_btc_daily() if d is None else d
    L = lag() if L is None else L
    s = state_table(d)
    s = s.reindex(pd.date_range(s.index[0], s.index[-1] + pd.Timedelta(days=1), freq="D"))
    lab = s[["close", "phase_id", "pos40", "rsi", "dd", "r10", "s50"]].shift(L)
    lab["M"] = s["M"].shift(L)
    lab["phase"] = lab.phase_id.map(lambda x: PHASES.get(int(x)) if x == x else None)
    lab["halving_age_d"] = halving_age(lab.index)
    lab.index.name = "date"
    # one extra label day after the last data day (today) so "now" can be read
    return lab


def allowed_side(phase_id, pos40):
    """+1 long allowed, -1 short allowed, 0 none (NaN). ACCUM: long if pos40<=0.5 else short."""
    a = ALLOWED.get(int(phase_id)) if phase_id == phase_id else None
    if a is None:
        return 0
    if a == 0:
        return 1 if pos40 <= 0.5 else -1
    return a


def build_shared(force=False):
    """Write the shared phase table once (atomic); other workers read it and spot-verify."""
    if SHARED.exists() and not force:
        return SHARED
    t = phase_daily(L=1)
    ext = t.copy()
    SHARED.parent.mkdir(parents=True, exist_ok=True)
    tmp = SHARED.with_suffix(".tmp")
    out = ext.reset_index()
    out.to_csv(tmp, index=False)
    sha = hashlib.sha256(tmp.read_bytes()).hexdigest()
    os.replace(tmp, SHARED)
    json.dump(dict(source="phases.py (nkp1) from btc_daily.csv + binance 1d tail", rows=len(out), sha256=sha, key="date",
                   note="label day d = state at close of d-1"), open(str(SHARED) + ".meta.json", "w"))
    return SHARED
