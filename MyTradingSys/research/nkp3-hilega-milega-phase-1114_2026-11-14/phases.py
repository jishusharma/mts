"""Daily BTC phase table (MTS_BRAINS_SPEC_1114 s1). Label for day d uses closes through d-PHASE_LAG (default 1)."""
import os, subprocess
from pathlib import Path
import numpy as np
import pandas as pd

D1 = 86400000
HERE = Path(__file__).resolve().parent
CSV_OLD = HERE.parents[1] / "research" / "btc_cycles_2026-11" / "btc_daily.csv"
BTC5 = Path(r"F:/MTS/data_cache/binance/BTCUSDT_5m.npz")
OUT = Path(r"F:/MTS/data_cache/mts_brains/phase_daily.csv")
NAMES = {0: "NA", 1: "CAPITULATION", 2: "MARKDOWN", 3: "RELIEF", 4: "ACCUM-RANGE", 5: "MARKUP", 6: "DISTRIBUTION"}
# phase-appropriate directions: +1 long, -1 short ; ACCUM both
ALLOWED = {1: (1,), 2: (-1,), 3: (1,), 4: (1, -1), 5: (1,), 6: (-1,)}
HALVINGS = ["2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20"]


def phase_lag():
    if os.environ.get("STUDY_BUG") == "1":
        return 0
    return int(os.environ.get("PHASE_LAG", "1"))


def btc_daily():
    old = pd.read_csv(CSV_OLD)
    old = old[old.date < "2019-01-01"]
    d0 = pd.DataFrame({"dn": (pd.to_datetime(old.date) .astype("datetime64[s]").astype("int64") // 86400).values,
                       "high": old.high.values, "low": old.low.values, "close": old.close.values})
    a = np.load(BTC5)["a"]
    f = pd.DataFrame({"dn": (a[:, 0] // D1).astype(np.int64), "h": a[:, 2], "l": a[:, 3], "c": a[:, 4]})
    g = f.groupby("dn").agg(high=("h", "max"), low=("l", "min"), close=("c", "last"), n=("c", "size"))
    last = g.index.max()
    g = g[(g.n >= 250) & ~((g.index == last) & (g.n < 288))].reset_index()[["dn", "high", "low", "close"]]
    d = pd.concat([d0, g]).drop_duplicates("dn", keep="last").set_index("dn").sort_index()
    return d.reindex(np.arange(d.index.min(), d.index.max() + 1)).ffill()


def wilder_rsi(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    r[dn == 0] = 100.0
    r.iloc[:n] = np.nan
    return r


def features(d):
    c = d.close
    f = pd.DataFrame(index=d.index)
    f["c"] = c
    f["sma20"] = c.rolling(20).mean()
    f["sma50"] = c.rolling(50).mean()
    f["sma200"] = c.rolling(200).mean()
    f["w200"] = c.rolling(1400).mean()
    f["s50"] = f.sma50 / f.sma50.shift(10) - 1
    f["r10"] = c / c.shift(10) - 1
    f["rb30"] = c / c.rolling(30).min() - 1
    f["dd"] = c / c.cummax() - 1
    f["rsi"] = wilder_rsi(c, 14)
    f["rng40"] = (d.high.rolling(40).max() - d.low.rolling(40).min()) / c
    lowc = (c < c.shift(1).rolling(60).min()).astype(float)
    f["newlow15"] = lowc.rolling(15, min_periods=1).max() > 0
    return f


def labels_from_features(f):
    c = f.c
    bear = (f.dd <= -0.2) & (c < f.sma200)
    bull = (c > f.w200) & (f.dd > -0.2)
    cap = ((~bull) & (f.r10 <= -0.2) & (f.rsi <= 30)).astype(float).rolling(3, min_periods=1).max() > 0
    m2 = (c < f.sma50) & (f.s50 <= -0.01) & (bear | (c < f.sma200))
    m3 = (~bull) & (c > f.sma20) & (f.rb30 >= 0.12) & (c <= 1.05 * f.sma200)
    m4 = (~bull) & (f.rng40 <= 0.30) & ((c / f.sma50 - 1).abs() <= 0.07) & (~f.newlow15)
    m5 = (c > f.sma50) & (f.s50 >= 0.01) & ((c > f.sma200) | bull)
    lab = np.full(len(f), 6, dtype=np.int8)
    for code, m in ((5, m5), (4, m4), (3, m3), (2, m2), (1, cap)):
        lab[m.values] = code
    lab[(f.sma200.isna() | f.s50.isna() | f.rsi.isna()).values] = 0
    state = np.where(bear, "BEAR", np.where(bull, "BULL", "BASE"))
    return pd.Series(lab, index=f.index), pd.Series(state, index=f.index)


def build_table(d=None, lag=None):
    """label per day number index; day d's label comes from features at d-lag."""
    lag = phase_lag() if lag is None else lag
    d = btc_daily() if d is None else d
    f = features(d)
    lab, state = labels_from_features(f)
    out = pd.DataFrame({"label": lab.shift(lag).fillna(0).astype(int), "state": state.shift(lag).fillna("BASE")})
    out.index.name = "dn"
    nxt = d.index.max() + 1  # day after the last closed day: label from the last close when lag=1
    if lag >= 1:
        out.loc[nxt] = [int(lab.iloc[-1]) if lag == 1 else 0, state.iloc[-1] if lag == 1 else "BASE"]
    for k, col in enumerate(["c", "sma50", "sma200", "w200", "dd", "rsi"]):
        out["f_" + col] = f[col].shift(lag).reindex(out.index) if lag >= 1 else f[col].reindex(out.index)
    if lag >= 1:
        for col in ["c", "sma50", "sma200", "w200", "dd", "rsi"]:
            out.loc[nxt, "f_" + col] = f[col].iloc[-1]
    return out


def label_slow(d, day, lag=1):
    """independent recompute for one day: truncate the daily history at day-lag, label the last row."""
    t = d[d.index <= day - lag]
    f = features(t)
    lab, _ = labels_from_features(f)
    return int(lab.iloc[-1])


def git_hash():
    try:
        return subprocess.check_output(["git", "-C", str(HERE), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "nogit"


def write_table():
    t = build_table()
    t["date"] = pd.to_datetime(t.index * 86400, unit="s").strftime("%Y-%m-%d")
    t["builder_git"] = git_hash()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT)
    return t


def read_table():
    t = pd.read_csv(OUT).set_index("dn")
    return t


def halving_age_days(date):
    ts = pd.Timestamp(date)
    prev = [pd.Timestamp(h) for h in HALVINGS if pd.Timestamp(h) <= ts]
    return (ts - prev[-1]).days if prev else np.nan
