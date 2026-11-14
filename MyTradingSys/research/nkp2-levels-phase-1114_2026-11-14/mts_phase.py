"""MTS phase labels (MTS_BRAINS_SPEC_1114 s1). One label per UTC day d, from BTC daily data through the close of d-PHASE_LAG (default lag 1).
PHASE_LAG=0 or STUDY_BUG=1 env = deliberate look-ahead (same-day close), used only by the failing tests.
Thresholds are OURS (spec s5 ledger); cycle state M follows the cycle-conditioned PRE_REG (SOURCED)."""
import os, csv, datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BTC_DAILY = REPO / "MyTradingSys" / "research" / "btc_cycles_2026-11" / "btc_daily.csv"
SPOT15 = Path(r"F:\MTS\data_cache\binance_spot") / "BTCUSDT_15m.npz"
PHASE_CSV = Path(r"F:\MTS\data_cache") / "mts_brains" / "phase_daily.csv"
DAY = 86400000
PH_NAMES = {1: "CAPITULATION", 2: "MARKDOWN", 3: "RELIEF", 4: "ACCUM-RANGE", 5: "MARKUP", 6: "DISTRIBUTION"}
# phase-appropriate direction: +1 long, -1 short, 0 both
PH_DIR = {1: 1, 2: -1, 3: 1, 4: 0, 5: 1, 6: -1}


def phase_lag():
    if os.environ.get("STUDY_BUG") == "1":
        return 0
    return int(os.environ.get("PHASE_LAG", "1"))


def load_btc_daily():
    """(day_numbers, high, low, close). btc_daily.csv (blockchain.info then binance, to 2026-11-06) + Binance 15m for later complete UTC days."""
    d, h, l, c = [], [], [], []
    for r in csv.DictReader(open(BTC_DAILY)):
        d.append(int(dt.date.fromisoformat(r["date"]).toordinal() - 719163))
        h.append(float(r["high"])); l.append(float(r["low"])); c.append(float(r["close"]))
    d, h, l, c = map(np.array, (d, h, l, c))
    z = np.load(SPOT15)
    t, hh, ll, cc = z["t"], z["h"], z["l"], z["c"]
    dn = t // DAY
    for day in range(int(d[-1]) + 1, int(dn[-1]) + 1):
        m = dn == day
        if m.sum() != 96:
            continue
        d = np.r_[d, day]; h = np.r_[h, hh[m].max()]; l = np.r_[l, ll[m].min()]; c = np.r_[c, cc[m][-1]]
    return d, h, l, c


def load_btc_partial_today():
    """(day_number, high, low, close, n_bars) of the newest incomplete UTC day from 15m data, or None."""
    z = np.load(SPOT15)
    t = z["t"]
    day = t[-1] // DAY
    m = t // DAY == day
    if m.sum() == 96:
        return None
    return int(day), float(z["h"][m].max()), float(z["l"][m].min()), float(z["c"][m][-1]), int(m.sum())


def _roll(x, n, f):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        w = np.lib.stride_tricks.sliding_window_view(x, n)
        out[n - 1:] = f(w, axis=1)
    return out


def wilder_rsi(c, n=14):
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    out[n] = 100 - 100 / (1 + au / ad) if ad > 0 else 100
    for i in range(n + 1, len(c)):
        au = (au * (n - 1) + up[i - 1]) / n
        ad = (ad * (n - 1) + dn[i - 1]) / n
        out[i] = 100 - 100 / (1 + au / ad) if ad > 0 else 100
    return out


def features(h, l, c):
    """per row j: features at the CLOSE of day j."""
    n = len(c)
    sma = lambda k: _roll(c, k, np.mean)
    s20, s50, s200, w200 = sma(20), sma(50), sma(200), sma(1400)
    s50_10 = np.full(n, np.nan)
    s50_10[10:] = s50[:-10]
    S50 = s50 / s50_10 - 1
    R10 = np.full(n, np.nan)
    R10[10:] = c[10:] / c[:-10] - 1
    RB30 = c / _roll(c, 30, np.min) - 1
    DD = c / np.maximum.accumulate(c) - 1
    rsi = wilder_rsi(c, 14)
    RNG40 = (_roll(h, 40, np.max) - _roll(l, 40, np.min)) / c
    prior_min60 = np.full(n, np.nan)
    prior_min60[60:] = _roll(c, 60, np.min)[59:-1]
    with np.errstate(invalid="ignore"):
        newlow = (c < prior_min60).astype(float)
    nl15 = _roll(newlow, 15, np.max)
    return dict(c=c, s20=s20, s50=s50, s200=s200, w200=w200, S50=S50, R10=R10, RB30=RB30, DD=DD, rsi=rsi, RNG40=RNG40, NL15=nl15)


def labels_from_features(F):
    """label per feature row j (state at close of j, first-match order), CAPITULATION sticky 3 rows (j..j+2). 0 = not enough history."""
    c = F["c"]
    n = len(c)
    with np.errstate(invalid="ignore"):
        bear = (F["DD"] <= -0.20) & (c < F["s200"])
        bull = (c > F["w200"]) & (F["DD"] > -0.20)
        cap_raw = (~bull) & (F["R10"] <= -0.20) & (F["rsi"] <= 30)
        cap = cap_raw.copy()
        cap[1:] |= cap_raw[:-1]
        cap[2:] |= cap_raw[:-2]
        t2 = (c < F["s50"]) & (F["S50"] <= -0.01) & (bear | (c < F["s200"]))
        t3 = (~bull) & (c > F["s20"]) & (F["RB30"] >= 0.12) & (c <= 1.05 * F["s200"])
        t4 = (~bull) & (F["RNG40"] <= 0.30) & (np.abs(c / F["s50"] - 1) <= 0.07) & (F["NL15"] == 0)
        t5 = (c > F["s50"]) & (F["S50"] >= 0.01) & ((c > F["s200"]) | bull)
    lab = np.full(n, 6, dtype=np.int8)
    for k, t in ((5, t5), (4, t4), (3, t3), (2, t2), (1, cap)):  # reverse order so the first match wins
        lab[t] = k
    warm = np.isnan(F["w200"]) | np.isnan(F["s200"]) | np.isnan(F["S50"]) | np.isnan(F["RNG40"]) | np.isnan(F["NL15"])
    lab[warm] = 0
    state = np.where(bear, "BEAR", np.where(bull, "BULL", "BASE"))
    return lab, state


def day_labels(d, h, l, c, lag=None):
    """(day_numbers the labels apply to, label, state, features). Label for day D = rows through D-lag."""
    lag = phase_lag() if lag is None else lag
    F = features(h, l, c)
    lab, state = labels_from_features(F)
    return d + lag, lab, state, F


def label_for_day(d, h, l, c, day, lag=None):
    """label for ONE UTC day computed only from rows with day number <= day - lag (the causal test hook). 0 = unavailable."""
    lag = phase_lag() if lag is None else lag
    m = d <= day - lag
    if not m.any() or d[m][-1] != day - lag:
        return 0
    dl, lab, state, F = day_labels(d[m], h[m], l[m], c[m], lag=lag)
    return int(lab[-1])


def build_csv(path=PHASE_CSV):
    d, h, l, c = load_btc_daily()
    dl, lab, state, F = day_labels(d, h, l, c, lag=1)
    hv = [dt.date(2012, 11, 28), dt.date(2016, 7, 9), dt.date(2020, 5, 11), dt.date(2024, 4, 20)]
    hv = [x.toordinal() - 719163 for x in hv]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    git = os.popen(f'git -C "{REPO}" rev-parse HEAD').read().strip()
    with open(tmp, "w", newline="") as f:
        f.write(f"# built by nkp2-levels-phase-1114 mts_phase.py git={git} lag=1 spec=MTS_BRAINS_SPEC_1114\n")
        w = csv.writer(f)
        w.writerow(["date", "phase", "phase_name", "state", "close_prev", "sma20", "sma50", "sma200", "w200", "S50", "R10", "RB30", "DD", "rsi14d", "RNG40", "NL15", "halving_age_days"])
        for k in range(len(d)):
            day = int(dl[k])
            if lab[k] == 0:
                continue
            ages = [day - x for x in hv if day >= x]
            w.writerow([dt.date.fromordinal(day + 719163).isoformat(), int(lab[k]), PH_NAMES[int(lab[k])], state[k], F["c"][k], F["s20"][k], F["s50"][k], F["s200"][k], F["w200"][k],
                        F["S50"][k], F["R10"][k], F["RB30"][k], F["DD"][k], F["rsi"][k], F["RNG40"][k], F["NL15"][k], ages[-1] if ages else ""])
    os.replace(tmp, path)
    return path


def read_phase_csv(path=PHASE_CSV):
    """dict day_number -> phase int (label for that UTC day from BTC data through the prior close). Reads both csv layouts seen in the shared
    folder (mine: `phase` id column; the sibling worker's: `label` name column); rows flagged provisional are skipped."""
    ids = {v: k for k, v in PH_NAMES.items()}
    out = {}
    with open(path) as f:
        first = f.readline()
        if not first.startswith("#"):
            f.seek(0)
        for r in csv.DictReader(f):
            if str(r.get("provisional", "False")).lower() == "true":
                continue
            v = r.get("phase") or ids.get(r.get("label", ""), "")
            if v == "":
                continue
            out[dt.date.fromisoformat(r["date"]).toordinal() - 719163] = int(v)
    return out


def phase_table_for_study():
    """(day_numbers, labels) from the shared csv; builds it once if absent (other workers read it, then run verify_phase.py)."""
    if not PHASE_CSV.exists():
        build_csv()
    m = read_phase_csv()
    days = np.array(sorted(m))
    return days, np.array([m[x] for x in days], dtype=np.int8)


if __name__ == "__main__":
    print(build_csv())
