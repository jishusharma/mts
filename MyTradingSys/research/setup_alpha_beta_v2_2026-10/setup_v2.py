"""B163 v2: Alpha (daily SMA200 long-flat) and Beta (15m sweep + CVD absorption), DEV/VAL only. Rules: PRE_REG.md."""
import sys, os, glob, json, math
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from backtest.fees import BINANCE_TAKER as FEE

# backtest/splits.py is not on origin/fast-track yet: dates hard-coded (sim_desk/ROADMAP.md 2.1).
DEV = ("2022-01-01", "2024-06-30")
VAL = ("2024-07-01", "2025-06-30")
SEAL_MS = int(pd.Timestamp("2025-07-01", tz="UTC").timestamp() * 1000)  # HOLDOUT starts here: never loaded
SEAL_MONTH = "2025-07"

DUMPS = os.environ.get("MTS_DUMPS", r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest")
DIR_2020 = os.path.join(DUMPS, "raw_1m_2019", "klines")
DIR_2022 = os.environ.get("TOM_RAW_DIR", r"F:\MTS\data\tom_raw") + "/klines"
DIR_FUND = os.path.join(DUMPS, "raw", "fundingRate")
NAMES = ["open_time", "open", "high", "low", "close", "volume", "tb"]


def month_of(path):
    return os.path.basename(path).split("-1m-")[1][:7]


def dedupe(df):
    return df.drop_duplicates("open_time", keep="first").sort_values("open_time").reset_index(drop=True)


def load_1m():
    files = []
    for d in (DIR_2020, DIR_2022):
        files += glob.glob(os.path.join(d, "BTCUSDT-1m-*.csv"))
    parts = []
    for f in sorted(files):
        if month_of(f) >= SEAL_MONTH:
            continue  # sealed HOLDOUT: file never opened
        p = pd.read_csv(f, usecols=[0, 1, 2, 3, 4, 5, 9], header=0, dtype=float)
        p.columns = NAMES
        parts.append(p)
    df = dedupe(pd.concat(parts, ignore_index=True))
    df["open_time"] = df["open_time"].astype("int64")
    df = df[df["open_time"] < SEAL_MS].reset_index(drop=True)
    assert df["open_time"].max() < SEAL_MS
    return df


def load_funding():
    parts = []
    for f in sorted(glob.glob(os.path.join(DIR_FUND, "BTCUSDT-fundingRate-*.csv"))):
        if f[-11:-4] >= SEAL_MONTH:
            continue
        parts.append(pd.read_csv(f, usecols=["calc_time", "last_funding_rate"]))
    fd = pd.concat(parts).drop_duplicates("calc_time").sort_values("calc_time")
    fd = fd[fd["calc_time"] < SEAL_MS]
    return fd["calc_time"].to_numpy(np.int64), fd["last_funding_rate"].to_numpy(float)


def resample(df, ms, need):
    g = (df["open_time"] // ms) * ms
    a = df.groupby(g).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                          close=("close", "last"), volume=("volume", "sum"), tb=("tb", "sum"),
                          n=("open", "size"))
    a = a[a["n"] == need]
    a.index.name = "t"
    return a.reset_index()


def to_ms(s):
    return int(pd.Timestamp(s, tz="UTC").timestamp() * 1000)


def fund_sum(ft, fr, t0, t1):
    """sum of settled funding rates with t0 < calc_time <= t1 (ms)."""
    i = np.searchsorted(ft, t0, side="right")
    j = np.searchsorted(ft, t1, side="right")
    return float(fr[i:j].sum())


# ---------------- Alpha ----------------
def atr14(d):
    pc = d["close"].shift(1)
    tr = pd.concat([d["high"] - d["low"], (d["high"] - pc).abs(), (d["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(14).mean()


def metrics(daily, in_mkt):
    eq = np.cumprod(1 + daily)
    yrs = len(daily) / 365.25
    sd = daily.std(ddof=1)
    pk = np.maximum.accumulate(eq)
    pk = np.maximum(pk, 1.0)
    return {"cagr": float(eq[-1] ** (1 / yrs) - 1),
            "sharpe": float(daily.mean() / sd * math.sqrt(365)) if sd > 0 else 0.0,
            "maxdd": float(np.max(1 - eq / pk)), "end_equity": float(eq[-1]), "time_in_market": float(in_mkt)}


def alpha_split(day, ft, fr, win):
    """Day i earns close[i-1] -> close[i]; the signal is read at close[i-1]. Window cuts at the split end."""
    t0, t1 = to_ms(win[0]), to_ms(win[1]) + 86400000
    c = day["close"].to_numpy(); sma = day["sma"].to_numpy(); atr = day["atr"].to_numpy(); tt = day["t"].to_numpy()
    idx = [i for i in range(1, len(day)) if t0 <= tt[i] < t1]
    daily, bh, trades = [], [], []
    pos = False; cur = None; inm = 0
    for k, i in enumerate(idx):
        want = (not np.isnan(sma[i - 1])) and c[i - 1] > sma[i - 1]
        f = fund_sum(ft, fr, tt[i], tt[i] + 86400000 - 1)
        last = k == len(idx) - 1
        g = 1.0
        if want and not pos:
            g *= 1 - FEE; pos = True
            cur = {"eq": 1 - FEE, "atr": atr[i - 1], "e": c[i - 1]}
        elif pos and not want:
            g *= 1 - FEE; cur["eq"] *= 1 - FEE
            trades.append(cur); pos = False
        if pos:
            inm += 1
            rd = (c[i] / c[i - 1] - 1) - f
            g *= 1 + rd; cur["eq"] *= 1 + rd
            if last:  # forced close at the split end
                g *= 1 - FEE; cur["eq"] *= 1 - FEE
                trades.append(cur); pos = False
        daily.append(g - 1)
        b = (1 + (c[i] / c[i - 1] - 1) - f)
        if k == 0: b *= 1 - FEE
        if last: b *= 1 - FEE
        bh.append(b - 1)
    daily = np.array(daily); bh = np.array(bh)
    rs = []
    for tr in trades:
        risk = 2 * tr["atr"] / tr["e"]
        if risk == risk and risk > 0:
            rs.append((tr["eq"] - 1) / risk)
    rs = np.array(rs)
    a = metrics(daily, inm / len(idx))
    a.update({"n": len(trades), "win": float((rs > 0).mean()) if len(rs) else 0.0,
              "mean_R": float(rs.mean()) if len(rs) else 0.0})
    b = metrics(bh, 1.0)
    b.update({"n": 1, "win": 1.0 if (1 + bh).prod() > 1 else 0.0, "mean_R": None})
    return {"alpha": a, "bh": b, "days": len(idx)}


def run_alpha(df, ft, fr):
    day = resample(df, 86400000, 1440)
    day["sma"] = day["close"].rolling(200).mean()
    day["atr"] = atr14(day)
    return {"DEV": alpha_split(day, ft, fr, DEV), "VAL": alpha_split(day, ft, fr, VAL)}


# ---------------- Beta ----------------
def find_events(b15, look=8):
    """b15: 15m frame (t, open, high, low, close, volume, tb). One event per (UTC day, side).
    Uses only bars <= i and the PREVIOUS day's high/low. Returns one dict per sweep event."""
    t = b15["t"].to_numpy(); h = b15["high"].to_numpy(); l = b15["low"].to_numpy(); c = b15["close"].to_numpy()
    cvd = np.cumsum(2 * b15["tb"].to_numpy() - b15["volume"].to_numpy())
    day = t // 86400000
    hi_by, lo_by = {}, {}
    for d in np.unique(day):
        m = day == d
        hi_by[d] = h[m].max(); lo_by[d] = l[m].min()
    pdh = {d: hi_by[d - 1] for d in hi_by if (d - 1) in hi_by}  # PREVIOUS day only
    pdl = {d: lo_by[d - 1] for d in lo_by if (d - 1) in lo_by}
    seen = set(); evs = []
    for i in range(look + 1, len(t)):
        d = day[i]
        if d not in pdh or t[i] - t[i - 1] != 900000:
            continue
        hour = (t[i] % 86400000) // 3600000
        for side in ("short", "long"):
            if (d, side) in seen:
                continue
            if side == "short":
                lvl = pdh[d]
                hit = h[i] > lvl and c[i] < lvl and c[i - 1] <= lvl
                cv = h[i] > h[i - look:i].max() and cvd[i] <= cvd[i - look:i].max()
                ext = h[i]
            else:
                lvl = pdl[d]
                hit = l[i] < lvl and c[i] > lvl and c[i - 1] >= lvl
                cv = l[i] < l[i - look:i].min() and cvd[i] >= cvd[i - look:i].min()
                ext = l[i]
            if hit:
                seen.add((d, side))
                evs.append({"i": i, "t": int(t[i]), "side": side, "ext": float(ext), "cvd": bool(cv),
                            "sess": bool(7 <= hour < 21)})
    return evs


def sim_event(ev, b15, m1_t, m1_o, m1_h, m1_l, m1_c, ft, fr):
    """Entry at the open of bar i+1 (taker); manage on 1m bars. Returns dict (R) or {dropped}/{skipped}."""
    i = ev["i"]
    if i + 1 >= len(b15):
        return {"dropped": True}
    ent_t = int(ev["t"]) + 900000; end_t = ent_t + 6 * 900000
    a = np.searchsorted(m1_t, ent_t); z = np.searchsorted(m1_t, end_t)
    if z - a < 90 or m1_t[a] != ent_t or m1_t[z - 1] != end_t - 60000:
        return {"dropped": True}
    entry = m1_o[a]; side = 1 if ev["side"] == "long" else -1
    stop = ev["ext"] - 0.1 if side == 1 else ev["ext"] + 0.1
    risk = abs(entry - stop)
    if (side == 1 and entry <= stop) or (side == -1 and entry >= stop) or risk <= 0:
        return {"skipped": True}
    tgt = entry + side * 1.5 * risk
    exit_p = None; exit_t = end_t
    for k in range(a, z):
        if side == 1:
            if m1_l[k] <= stop: exit_p = stop; exit_t = m1_t[k] + 60000; break
            if m1_h[k] >= tgt: exit_p = tgt; exit_t = m1_t[k] + 60000; break
        else:
            if m1_h[k] >= stop: exit_p = stop; exit_t = m1_t[k] + 60000; break
            if m1_l[k] <= tgt: exit_p = tgt; exit_t = m1_t[k] + 60000; break
    if exit_p is None:
        exit_p = m1_c[z - 1]
    f = fund_sum(ft, fr, ent_t, exit_t)
    rp = risk / entry
    r = (side * (exit_p - entry) / entry - 2 * FEE - side * f) / rp
    return {"R": r, "fee_R": 2 * FEE / rp}


def stats(rs, fees):
    n = len(rs)
    if n == 0:
        return {"n": 0, "win": 0.0, "mean_R": 0.0, "se": 0.0, "t": 0.0, "median_fee_R": 0.0}
    a = np.array(rs); se = a.std(ddof=1) / math.sqrt(n) if n > 1 else 0.0
    return {"n": n, "win": float((a > 0).mean()), "mean_R": float(a.mean()), "se": float(se),
            "t": float(a.mean() / se) if se > 0 else 0.0, "median_fee_R": float(np.median(fees))}


def run_beta(df, ft, fr):
    b15 = resample(df, 900000, 15)
    b15 = b15[b15["t"] >= to_ms("2021-12-31")].reset_index(drop=True)  # prior day for the first PDH/PDL
    evs = find_events(b15)
    m1 = df[df["open_time"] >= to_ms("2021-12-31")]
    m1_t = m1["open_time"].to_numpy(np.int64)
    arrs = [m1[c].to_numpy() for c in ("open", "high", "low", "close")]
    arms = {"S1": lambda e: e["sess"] and e["cvd"], "S0": lambda e: e["sess"],
            "A1": lambda e: e["cvd"], "A0": lambda e: True}
    for e in evs:
        e["sim"] = sim_event(e, b15, m1_t, *arrs, ft, fr)
    res = {}
    for sp, win in (("DEV", DEV), ("VAL", VAL)):
        t0, t1 = to_ms(win[0]), to_ms(win[1]) + 86400000
        for arm, fn in arms.items():
            sel = [e for e in evs if t0 <= e["t"] < t1 and fn(e)]
            rs, fees, drop, skip = [], [], 0, 0
            for e in sel:
                s = e["sim"]
                if s.get("dropped"): drop += 1; continue
                if s.get("skipped"): skip += 1; continue
                rs.append(s["R"]); fees.append(s["fee_R"])
            st = stats(rs, fees); st.update({"events": len(sel), "dropped": drop, "skipped": skip})
            res[f"{arm}_{sp}"] = st
    return res


def verdicts(alpha, beta):
    ap = all(alpha[s]["alpha"]["sharpe"] > alpha[s]["bh"]["sharpe"] and alpha[s]["alpha"]["maxdd"] < alpha[s]["bh"]["maxdd"]
             for s in ("DEV", "VAL"))
    d, v = beta["S1_DEV"], beta["S1_VAL"]
    if d["n"] >= 100 and d["mean_R"] > 0 and d["t"] >= 2 and v["n"] >= 30 and v["mean_R"] > 0:
        bv = "PASS"
    elif d["n"] < 100 or v["n"] < 30:
        bv = "INCONCLUSIVE"
    else:
        bv = "FAIL"
    return {"alpha": "PASS" if ap else "FAIL", "beta": bv}


def main():
    df = load_1m(); ft, fr = load_funding()
    assert df["open_time"].max() < SEAL_MS
    alpha = run_alpha(df, ft, fr); beta = run_beta(df, ft, fr)
    out = {"alpha": alpha, "beta": beta, "verdict": verdicts(alpha, beta), "rows": int(len(df)),
           "last_bar_utc": str(pd.Timestamp(int(df["open_time"].max()), unit="ms", tz="UTC"))}
    with open(os.path.join(HERE, "result_numbers.json"), "w", newline="\n") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
