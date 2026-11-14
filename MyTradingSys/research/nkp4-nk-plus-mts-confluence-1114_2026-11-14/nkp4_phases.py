"""Daily BTC phase table (MTS brains spec section 1). Label for UTC day d uses closes through d-1 only (PHASE_LAG=1)."""
import os, subprocess
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ROOT = Path(r"F:\MTS\data_cache")
BTC_CSV = REPO / "MyTradingSys" / "research" / "btc_cycles_2026-11" / "btc_daily.csv"
PHASE_CSV = ROOT / "mts_brains" / "phase_daily.csv"
LABELS = ["CAPITULATION", "MARKDOWN", "RELIEF", "ACCUM-RANGE", "MARKUP", "DISTRIBUTION"]
# direction each phase allows: +1 long, -1 short, 0 both (ACCUM: geometry decides)
PHASE_DIR = {"CAPITULATION": 1, "MARKDOWN": -1, "RELIEF": 1, "ACCUM-RANGE": 0, "MARKUP": 1, "DISTRIBUTION": -1}


def phase_lag():
    if os.environ.get("STUDY_BUG"):
        return 0
    return int(os.environ.get("PHASE_LAG", "1"))


def rsi_wilder(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def daily_features(df):
    """df: index date, columns high low close. Features AT each date's own close (no lag applied here)."""
    c, h, l = df["close"], df["high"], df["low"]
    f = pd.DataFrame(index=df.index)
    f["close"] = c
    f["sma20"] = c.rolling(20).mean(); f["sma50"] = c.rolling(50).mean(); f["sma200"] = c.rolling(200).mean()
    f["s50"] = f["sma50"] / f["sma50"].shift(10) - 1
    f["r10"] = c / c.shift(10) - 1
    f["rb30"] = c / c.rolling(30).min() - 1
    f["dd"] = c / c.cummax() - 1
    f["w200"] = c.rolling(1400).mean()
    f["rsi14"] = rsi_wilder(c)
    hi40, lo40 = h.rolling(40).max(), l.rolling(40).min()
    f["rng40"] = (hi40 - lo40) / c
    f["lo40"], f["hi40"] = lo40, hi40
    nl = c < c.shift(1).rolling(60).min()
    f["newlow15"] = nl.rolling(15).max().fillna(0).astype(bool)
    return f


def label_from_features(f):
    """f: features aligned so row d holds the features the label of day d may use. Returns Series of labels (NaN where undefined)."""
    c = f["close"]
    bear = (f["dd"] <= -0.20) & (c < f["sma200"])
    bull = (c > f["w200"]) & (f["dd"] > -0.20)
    notbull = ~bull
    trig = notbull & (f["r10"] <= -0.20) & (f["rsi14"] <= 30)
    cap = trig | trig.shift(1, fill_value=False) | trig.shift(2, fill_value=False)
    markdown = (c < f["sma50"]) & (f["s50"] <= -0.01) & (bear | (c < f["sma200"]))
    relief = notbull & (c > f["sma20"]) & (f["rb30"] >= 0.12) & (c <= 1.05 * f["sma200"])
    accum = notbull & (f["rng40"] <= 0.30) & ((c / f["sma50"] - 1).abs() <= 0.07) & (~f["newlow15"].fillna(False).astype(bool))
    markup = (c > f["sma50"]) & (f["s50"] >= 0.01) & ((c > f["sma200"]) | bull)
    lab = pd.Series("DISTRIBUTION", index=f.index, dtype=object)
    for name, m in (("MARKUP", markup), ("ACCUM-RANGE", accum), ("RELIEF", relief), ("MARKDOWN", markdown), ("CAPITULATION", cap)):
        lab[m] = name  # applied in reverse priority so first match wins
    lab[f[["sma200", "s50", "r10", "rb30", "rsi14", "rng40", "w200"]].isna().any(axis=1)] = np.nan
    cyc = pd.Series("BASE", index=f.index, dtype=object); cyc[bear] = "BEAR"; cyc[bull] = "BULL"
    return lab, cyc


def phase_table(daily, lag=None):
    """daily: DataFrame index = date (datetime64), columns high low close. Row d label uses features at d-lag."""
    lag = phase_lag() if lag is None else lag
    f = daily_features(daily)
    fl = f.shift(lag) if lag else f
    # sticks: shifting features by lag keeps the cap stickiness relative to label days
    lab, cyc = label_from_features(fl)
    out = pd.DataFrame({"label": lab, "cycle": cyc, "lo40": fl["lo40"], "hi40": fl["hi40"]})
    out["rsi14"] = fl["rsi14"]; out["close_used"] = fl["close"]
    return out


def load_btc_daily():
    df = pd.read_csv(BTC_CSV, parse_dates=["date"]).set_index("date")[["high", "low", "close"]]
    d15 = np.load(ROOT / "binance_spot" / "BTCUSDT_15m.npz")
    ts = d15["ts"] if "ts" in d15.files else d15["t"]
    k = pd.DataFrame({"ts": ts, "h": d15["h"], "l": d15["l"], "c": d15["c"]})
    k["date"] = pd.to_datetime(k["ts"] // 86400000 * 86400000, unit="ms")
    g = k.groupby("date").agg(high=("h", "max"), low=("l", "min"), close=("c", "last"), n=("c", "size"))
    last = df.index.max()
    new = g[(g.index > last)]
    complete = new[new["n"] >= 96][["high", "low", "close"]]
    df = pd.concat([df, complete])
    partial = new[new["n"] < 96][["high", "low", "close"]]
    return df, partial


def git_hash():
    try:
        return subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build_phase_daily(force=False):
    """Built once into the shared cache; other workers read and run verify (spec s4). Rebuild only if absent or force."""
    if PHASE_CSV.exists() and not force:
        return pd.read_csv(PHASE_CSV, parse_dates=["date"], index_col="date")
    daily, partial = load_btc_daily()
    # extend one row (tomorrow) so the label for the day after the last closed day exists
    ext = pd.concat([daily, partial])
    nxt = ext.index.max() + pd.Timedelta(days=1)
    ext.loc[nxt] = [np.nan, np.nan, np.nan]
    t = phase_table(ext.ffill())
    t["provisional"] = (t.index - pd.Timedelta(days=1)).isin(partial.index)
    t["builder_git"] = git_hash()
    PHASE_CSV.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(PHASE_CSV, index_label="date")
    return t


def verify_phase(n=30, seed=0, table=None):
    """Recompute n random days from BTC closes through d-1 only and compare with the shared table (spec s4)."""
    table = build_phase_daily() if table is None else table
    daily, partial = load_btc_daily()
    rng = np.random.default_rng(seed)
    days = table.loc["2019-01-01":daily.index.max()].index
    bad = []
    for d in rng.choice(days, n, replace=False):
        d = pd.Timestamp(d)
        cut = daily.loc[: d - pd.Timedelta(days=1)].copy()
        cut.loc[d] = cut.iloc[-1]
        lab = phase_table(cut).loc[d, "label"]
        if lab != table.loc[d, "label"]:
            bad.append((str(d.date()), lab, table.loc[d, "label"]))
    return bad
