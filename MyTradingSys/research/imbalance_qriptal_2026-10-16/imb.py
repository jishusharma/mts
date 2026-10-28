"""Qriptal-style "imbalance" candles on Binance BTCUSDT: candle-definition check and fade test.

Qriptal (Habib) defines an imbalance as a volume anomaly on one exchange's candle; a SMALL-body imbalance means
traders opened positions that failed to move price, and price comes back for that liquidity (reversal). His
indicator's formula is sold and undisclosed, so the detector here is OURS (relative volume), and labels.json is
the answer key: candles he names with a timeframe and a price. See README.md for the full spec and results.

Commands (repo root):
  python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py verify-labels
  python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py fetch          # public Binance TF klines, spot + um
  python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py parity         # our 1m->TF resample vs Binance's own TF klines
  python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py label-check    # writes LABEL_CHECK.md
  python MyTradingSys/research/imbalance_qriptal_2026-10-16/imb.py backtest --k 2.0   # writes BACKTEST.md (design + check, no holdout)
"""
import argparse
import io
import json
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RAW_TX = REPO / "extracts" / "_staged_2026-09-27" / "raw"
PUBLISH = REPO / "MyTradingSys" / "research" / "qriptal_2026-10-10" / "PUBLISH_TIMES.tsv"
KLINES_1M = Path(os.environ.get("MTS_KLINES_1M", "F:/MTS/data/tom_raw/klines"))   # Binance USD-M perp BTCUSDT 1m
TF_DIR = Path(os.environ.get("MTS_BINANCE_TF", "F:/MTS/data/binance_tf"))
TF_MS = {"30m": 1_800_000, "1h": 3_600_000, "4h": 14_400_000, "12h": 43_200_000, "1d": 86_400_000}
MIN_MS = 60_000

# ---- every number below is OURS (judgement), none is the trader's ----
VOL_LOOKBACK = 50            # bars of the same TF for the volume median
K_GRID = (1.5, 2.0, 2.5, 3.0)  # relative-volume thresholds tried in the label check
TOL_RANGE = 0.004            # level within the candle range, +-0.4% (spoken prices are rounded to 100)
TOL_MID = 0.0025             # level equals the candle midpoint within 0.25%
LOOKBACK_DAYS = {"30m": 7, "1h": 7, "4h": 14, "12h": 30, "1d": 60}
SMALL_BODY = 0.30            # |close-open| / (high-low)
LARGE_BODY = 0.70
NORMAL_VOL = 1.2             # control group: relative volume below this
EXTREME_N = 20               # candle makes a new 20-bar low (long) or high (short)
HOLD_BARS = 24               # time exit, in bars of the signal TF
TARGETS_R = (1.0, 2.0)
FEE_SIDE = 0.0005            # Binance/Deribit taker per side (backtest/fees.py)
DESIGN = ("2022-01-01", "2025-09-01")
CHECK = ("2025-09-01", "2026-06-26")   # BACKTEST_PROTOCOL DEV window; holdout 2026-06-26.. is not read here
SEED = 12345


# ------------------------------------------------------------------ quotes / labels
def _norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def transcript(video):
    """Raw transcript as (joined normalised text, list of (char_offset, line_no))."""
    path = RAW_TX / f"qriptal_{video}_raw.txt"
    parts, starts, pos = [], [], 0
    for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        txt = _norm(re.sub(r"^\[[0-9:]+\]\s*", "", line))
        if not txt:
            continue
        starts.append((pos, no))
        parts.append(txt)
        pos += len(txt) + 1
    return " ".join(parts), starts


def locate_quote(video, quote):
    """Return 'path:first-last' for a verbatim quote, or None."""
    text, starts = transcript(video)
    q = _norm(quote)
    at = text.find(q)
    if at < 0:
        return None
    first = last = None
    for off, no in starts:
        if off <= at:
            first = no
        if off <= at + len(q) - 1:
            last = no
    rel = (RAW_TX / f"qriptal_{video}_raw.txt").relative_to(REPO).as_posix()
    return f"{rel}:{first}-{last}"


def load_labels():
    return json.loads((HERE / "labels.json").read_text(encoding="utf-8"))["labels"]


def publish_times():
    out = {}
    for line in PUBLISH.read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t")
        out[f[0]] = pd.Timestamp(f[1]).value // 1_000_000
    return out


# ------------------------------------------------------------------ data
def _read_kline_csv(fobj):
    df = pd.read_csv(fobj, header=None)
    if not str(df.iloc[0, 0]).strip().lstrip("-").isdigit():
        df = df.iloc[1:]
    df = df.iloc[:, :6].astype(float)
    df.columns = ["t", "o", "h", "l", "c", "v"]
    df["t"] = df["t"].astype(np.int64)
    us = df["t"] > 10**14            # Binance spot files from 2025 carry microseconds
    df.loc[us, "t"] = df.loc[us, "t"] // 1000
    return df


def load_1m(start=None, end=None):
    frames = [_read_kline_csv(p) for p in sorted(KLINES_1M.glob("BTCUSDT-1m-*.csv"))]
    df = pd.concat(frames).drop_duplicates("t").sort_values("t").reset_index(drop=True)
    if start:
        df = df[df.t >= pd.Timestamp(start).value // 1_000_000]
    if end:
        df = df[df.t < pd.Timestamp(end).value // 1_000_000]
    return df.reset_index(drop=True)


def resample(df1m, tf):
    """1m -> TF bars aligned to UTC (Binance alignment). Incomplete bars are dropped."""
    ms = TF_MS[tf]
    g = df1m.assign(b=(df1m.t // ms) * ms).groupby("b", sort=True)
    out = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "v": g.v.sum(), "n": g.t.size()})
    out = out[out.n == ms // MIN_MS].drop(columns="n")
    out.index.name = "t"
    return out.reset_index()


def tf_official(market, tf):
    files = sorted((TF_DIR / market / tf).glob("*.zip"))
    frames = []
    for p in files:
        with zipfile.ZipFile(p) as z:
            frames.append(_read_kline_csv(io.BytesIO(z.read(z.namelist()[0]))))
    if not frames:
        raise SystemExit(f"no {market} {tf} klines under {TF_DIR}; run: imb.py fetch")
    return pd.concat(frames).drop_duplicates("t").sort_values("t").reset_index(drop=True)


def fetch(months, markets=("spot", "um")):
    base = {"spot": "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT",
            "um": "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT"}
    for m in markets:
        for tf in TF_MS:
            d = TF_DIR / m / tf
            d.mkdir(parents=True, exist_ok=True)
            for ym in months:
                dst = d / f"BTCUSDT-{tf}-{ym}.zip"
                if dst.exists():
                    continue
                url = f"{base[m]}/{tf}/BTCUSDT-{tf}-{ym}.zip"
                try:
                    with urllib.request.urlopen(url, timeout=60) as r:
                        dst.write_bytes(r.read())
                    print("got", m, tf, ym)
                except Exception as e:   # a month not yet published is reported, not fatal
                    print("MISSING", m, tf, ym, e)


# ------------------------------------------------------------------ detector
def rel_volume(v, n=VOL_LOOKBACK):
    """v[i] / median(v[i-n .. i-1]); NaN until n prior bars exist."""
    s = pd.Series(np.asarray(v, dtype=float))
    med = s.shift(1).rolling(n, min_periods=n).median()
    return (s / med).to_numpy()


def body_frac(o, h, l, c):
    o, h, l, c = (np.asarray(x, dtype=float) for x in (o, h, l, c))
    rng = h - l
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(rng > 0, np.abs(c - o) / rng, np.nan)


def level_match(h, l, level, how):
    h, l = np.asarray(h, dtype=float), np.asarray(l, dtype=float)
    if how == "mid":
        return np.abs((h + l) / 2 - level) / level <= TOL_MID
    return (l * (1 - TOL_RANGE) <= level) & (level <= h * (1 + TOL_RANGE))


def prob_at_least(probs, k):
    """P(X >= k) for X = sum of independent Bernoulli(probs) (Poisson-binomial, exact DP)."""
    dist = np.zeros(len(probs) + 1)
    dist[0] = 1.0
    for p in probs:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return float(dist[k:].sum())


# ------------------------------------------------------------------ label check
def label_check(markets=("spot", "um")):
    labels, pub = load_labels(), publish_times()
    rows, summary = [], []
    bars = {(m, tf): tf_official(m, tf) for m in markets for tf in TF_MS}
    for (m, tf), b in bars.items():
        b["rv"] = rel_volume(b.v)
    for m in markets:
        for k in K_GRID:
            hits = exp_hit = 0.0
            probs, pos_n, neg_ok, neg_exp, neg_n, untestable = [], 0, 0, 0.0, 0, 0
            for lab in labels:
                b = bars[(m, lab["tf"])]
                ms = TF_MS[lab["tf"]]
                t_pub = pub[lab["video"]]
                win = b[(b.t + ms <= t_pub) & (b.t >= t_pub - LOOKBACK_DAYS[lab["tf"]] * 86_400_000)]
                flag = win.rv >= k
                rate = float(flag.mean()) if len(win) else 0.0
                if lab["kind"] == "pos":
                    mt = level_match(win.h, win.l, lab["level"], lab["match"])
                    n_match = int(mt.sum())
                    n_flag = int((mt & flag.to_numpy()).sum())
                    chance = 1 - (1 - rate) ** n_match
                    hit = n_flag >= 1
                    pos_n += 1
                    if n_match == 0:
                        untestable += 1
                    hits += hit
                    exp_hit += chance
                    probs.append(chance)
                    rows.append((m, k, lab["id"], lab["tf"], lab["kind"], n_match, n_flag, round(rate, 3), round(chance, 3), "HIT" if hit else ("NO PRICE MATCH" if n_match == 0 else "miss")))
                else:
                    lo, hi = (pd.Timestamp(x).value // 1_000_000 for x in lab["low_window"])
                    w2 = b[(b.t >= lo) & (b.t + ms <= hi)].reset_index(drop=True)
                    j = int(w2.l.idxmin())
                    near = w2.iloc[max(0, j - 1): j + 2]
                    flagged = int((near.rv >= k).sum())
                    ok = flagged == 0
                    neg_n += 1
                    neg_ok += ok
                    neg_exp += (1 - rate) ** len(near)
                    low_t = pd.Timestamp(int(w2.t[j]), unit="ms").strftime("%Y-%m-%d %H:%M")
                    rows.append((m, k, lab["id"], lab["tf"], lab["kind"], len(near), flagged, round(rate, 3), round((1 - rate) ** len(near), 3), ("agree" if ok else "DISAGREE") + f" (low {w2.l[j]:.0f} at {low_t})"))
            p = prob_at_least(probs, int(hits))
            summary.append((m, k, pos_n, int(hits), round(exp_hit, 2), round(hits / exp_hit, 2) if exp_hit else float("nan"), round(p, 4), untestable, neg_n, neg_ok, round(neg_exp, 2)))
    return rows, summary


def write_label_check(rows, summary):
    out = ["# Label check: does a relative-volume detector flag the candles Qriptal names? (generated by imb.py label-check)", "",
           "Answer key: labels.json (22 named imbalance candles with a timeframe and a spoken price, 3 'no imbalance at this low' statements).",
           "Data: Binance's own TF klines (data.binance.vision), spot and USD-M perp, BTCUSDT. Detector: volume / median(volume of the prior "
           f"{VOL_LOOKBACK} bars of the same TF) >= k. A positive label is a HIT if at least one candle of that TF that closed before the video "
           f"and opened within {LOOKBACK_DAYS} days of it matches the price (range +-{TOL_RANGE:.1%} or midpoint +-{TOL_MID:.2%}) AND is flagged.",
           "Chance = probability of the same HIT if the same number of flags were scattered at random over that window: 1-(1-rate)^matches.",
           "p = P(hits >= observed) under chance (exact Poisson-binomial). A detector that flags everything scores every hit and has chance 1: lift, not hits, is the measure.", "",
           "## Summary", "", "| market | k | positive labels | hits | hits expected by chance | lift | p | labels with no price match | negatives | negatives agreed | agreed by chance |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(x) for x in s) + " |" for s in summary]
    out += ["", "## Per label", "", "| market | k | label | tf | kind | candles matching price (neg: low bar +-1) | of them flagged | flag rate in window | chance | result |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    (HERE / "LABEL_CHECK.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ fade test
def classify(b, k):
    """Event class per TF bar: imb_small / imb_large / normal_small, and side (+1 long at a new low, -1 short at a new high)."""
    rv = rel_volume(b.v)
    bf = body_frac(b.o, b.h, b.l, b.c)
    l, h = b.l.to_numpy(), b.h.to_numpy()
    prior_lo = pd.Series(l).shift(1).rolling(EXTREME_N, min_periods=EXTREME_N).min().to_numpy()
    prior_hi = pd.Series(h).shift(1).rolling(EXTREME_N, min_periods=EXTREME_N).max().to_numpy()
    new_lo, new_hi = l < prior_lo, h > prior_hi
    side = np.where(new_lo & ~new_hi, 1, np.where(new_hi & ~new_lo, -1, 0))
    cls = np.full(len(b), "", dtype=object)
    cls[(rv >= k) & (bf <= SMALL_BODY)] = "imb_small"
    cls[(rv >= k) & (bf >= LARGE_BODY)] = "imb_large"
    cls[(rv < NORMAL_VOL) & (bf <= SMALL_BODY)] = "normal_small"
    return cls, side


def resolve(side, entry, stop, target, hi, lo, close):
    """Walk 1m bars; stop first when stop and target are in the same minute. Returns (exit_price, outcome)."""
    if side > 0:
        s_hit, g_hit = lo <= stop, hi >= target
    else:
        s_hit, g_hit = hi >= stop, lo <= target
    s = int(np.argmax(s_hit)) if s_hit.any() else len(hi)
    g = int(np.argmax(g_hit)) if g_hit.any() else len(hi)
    if s == len(hi) and g == len(hi):
        return float(close[-1]), "time"
    if s <= g:
        return float(stop), "stop"
    return float(target), "target"


def trade_r(side, entry, stop, exit_px, fee=FEE_SIDE):
    risk = abs(entry - stop)
    gross = side * (exit_px - entry) / risk
    cost = fee * (entry + exit_px) / risk
    return gross, cost, gross - cost


def run_events(df1m, tf, k, start, end):
    b = resample(df1m, tf)
    cls, side = classify(b, k)
    t1, o1, h1, l1, c1 = (df1m[x].to_numpy() for x in ("t", "o", "h", "l", "c"))
    s_ms, e_ms = (pd.Timestamp(x).value // 1_000_000 for x in (start, end))
    ms = TF_MS[tf]
    n_hold = HOLD_BARS * ms // MIN_MS
    out = []
    for i in np.flatnonzero((cls != "") & (side != 0)):
        t_entry = int(b.t[i]) + ms
        if not (s_ms <= int(b.t[i]) < e_ms):
            continue
        a = int(np.searchsorted(t1, t_entry))
        z = a + n_hold
        if a >= len(t1) or t1[a] != t_entry or z > len(t1) or t1[z - 1] - t_entry != (n_hold - 1) * MIN_MS:
            continue   # missing minutes: not scored
        sd = int(side[i])
        entry = float(o1[a])
        stop = float(b.l[i]) if sd > 0 else float(b.h[i])
        if sd * (entry - stop) <= 0:
            continue   # entry already beyond the stop
        far = float(b.h[i]) if sd > 0 else float(b.l[i])   # the candle's other extreme ("the liquidity" left behind)
        rec = {"tf": tf, "cls": cls[i], "t": int(b.t[i]), "side": sd, "entry": entry, "stop": stop,
               "risk_bp": abs(entry - stop) / entry * 1e4}
        hh, ll, cc = h1[a:z], l1[a:z], c1[a:z]
        fx, fo = resolve(sd, entry, stop, far, hh, ll, cc) if sd * (far - entry) > 0 else (far, "target")
        rec["far_before_stop"] = fo == "target"
        for R in TARGETS_R:
            tgt = entry + sd * R * abs(entry - stop)
            xp, oc = resolve(sd, entry, stop, tgt, hh, ll, cc)
            g, cst, net = trade_r(sd, entry, stop, xp)
            rec[f"gross_{R}"], rec[f"fee_{R}"], rec[f"net_{R}"], rec[f"out_{R}"] = g, cst, net, oc
        out.append(rec)
    return pd.DataFrame(out)


def boot_ci(day, x, n=2000, seed=SEED):
    """Day-block bootstrap CI95 of the mean."""
    if len(x) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({"d": day, "x": x})
    g = df.groupby("d").x.agg(["sum", "count"])
    s, c = g["sum"].to_numpy(), g["count"].to_numpy()
    idx = rng.integers(0, len(g), size=(n, len(g)))
    means = s[idx].sum(1) / c[idx].sum(1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(ev):
    rows = []
    if ev.empty:
        return rows
    ev = ev.assign(day=ev.t // 86_400_000)
    for (tf, cls), g in ev.groupby(["tf", "cls"], sort=False):
        for R in TARGETS_R:
            lo, hi = boot_ci(g.day, g[f"net_{R}"].to_numpy())
            rows.append({"tf": tf, "cls": cls, "R": R, "n": len(g), "win": round(float((g[f"net_{R}"] > 0).mean()), 3),
                         "gross_R": round(float(g[f"gross_{R}"].mean()), 3), "fee_R": round(float(g[f"fee_{R}"].mean()), 3),
                         "net_R": round(float(g[f"net_{R}"].mean()), 3), "ci_lo": round(lo, 3), "ci_hi": round(hi, 3),
                         "far_before_stop": round(float(g.far_before_stop.mean()), 3), "median_risk_bp": round(float(g.risk_bp.median()), 1)})
    return rows


def backtest(k):
    df1m = load_1m(end=CHECK[1])
    res = {}
    for name, (s, e) in (("design", DESIGN), ("check", CHECK)):
        evs = [run_events(df1m, tf, k, s, e) for tf in TF_MS]
        ev = pd.concat([x for x in evs if not x.empty], ignore_index=True)
        ev.to_csv(HERE / f"events_{name}.csv", index=False, lineterminator="\n")
        res[name] = summarize(ev)
    return res


def verdict(res):
    """PASS per TF/R: imb_small net CI95 low > 0 in design AND check, and imb_small net > normal_small net in both."""
    out = []
    for tf in TF_MS:
        for R in TARGETS_R:
            ok = True
            for name in ("design", "check"):
                d = {r["cls"]: r for r in res[name] if r["tf"] == tf and r["R"] == R}
                a, c = d.get("imb_small"), d.get("normal_small")
                if not a or not c or not (a["ci_lo"] > 0 and a["net_R"] > c["net_R"]):
                    ok = False
            out.append((tf, R, "PASS" if ok else "NO EDGE"))
    return out


def write_backtest(k, res):
    cols = ["tf", "cls", "R", "n", "win", "gross_R", "fee_R", "net_R", "ci_lo", "ci_hi", "far_before_stop", "median_risk_bp"]
    out = [f"# Imbalance fade test on Binance BTCUSDT perp (generated by imb.py backtest --k {k})", "",
           f"Events on 30m/1h/4h/12h/1d bars resampled from Binance USD-M 1m klines. imb_small = relative volume >= {k} and body <= {SMALL_BODY:.0%} of range "
           f"(Qriptal's trapped-traders candle); imb_large = relative volume >= {k} and body >= {LARGE_BODY:.0%} (his 'sign of strength', the fade should fail); "
           f"normal_small = relative volume < {NORMAL_VOL} and body <= {SMALL_BODY:.0%} (control: same shape, no volume anomaly).",
           f"Side: long when the candle makes a new {EXTREME_N}-bar low, short at a new {EXTREME_N}-bar high. Entry next bar open (1m open); stop = the candle's own low (long) / high (short); "
           f"target R x risk; time exit after {HOLD_BARS} bars; stop first when stop and target share a minute; taker {FEE_SIDE:.2%} per side on both legs.",
           "far_before_stop = share of events where price reached the candle's other extreme (the 'recovery') before the stop. CI95 = day-block bootstrap of mean net R, seed 12345.",
           f"Design {DESIGN[0]}..{DESIGN[1]}, check {CHECK[0]}..{CHECK[1]} (BACKTEST_PROTOCOL DEV). Holdout 2026-06-26.. not read. Pre-stated PASS: imb_small net CI95 low > 0 in design AND check, and above normal_small in both.", ""]
    for name in ("design", "check"):
        out += [f"## {name}", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in res[name]]
        out.append("")
    out += ["## Verdict per TF and target", "", "| tf | R | verdict |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in verdict(res)]
    (HERE / "BACKTEST.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def parity(market="um"):
    df1m = load_1m(start="2025-11-01")
    out = []
    for tf in TF_MS:
        ours = resample(df1m, tf).set_index("t")
        off = tf_official(market, tf).set_index("t")
        j = ours.join(off, rsuffix="_b", how="inner")
        if j.empty:
            out.append((tf, 0, "no overlap"))
            continue
        bad = 0
        for c in "ohlc":
            bad = np.maximum(bad, (np.abs(j[c] - j[c + "_b"]) > 1e-6).to_numpy())
        vbad = (np.abs(j.v - j.v_b) / j.v_b > 1e-6).to_numpy()
        out.append((tf, len(j), f"OHLC mismatches {int(bad.sum())}, volume mismatches {int(vbad.sum())}"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["verify-labels", "fetch", "parity", "label-check", "backtest"])
    ap.add_argument("--k", type=float, default=2.0)
    a = ap.parse_args(argv)
    if a.cmd == "verify-labels":
        bad = 0
        for lab in load_labels():
            loc = locate_quote(lab["video"], lab["quote"])
            print(lab["id"], loc or "QUOTE NOT FOUND")
            bad += loc is None
        return 1 if bad else 0
    if a.cmd == "fetch":
        months = [p.strftime("%Y-%m") for p in pd.period_range("2025-11", "2026-09", freq="M")]
        fetch(months)
        return 0
    if a.cmd == "parity":
        for r in parity():
            print(*r)
        return 0
    if a.cmd == "label-check":
        rows, summary = label_check()
        write_label_check(rows, summary)
        for s in summary:
            print(*s)
        return 0
    res = backtest(a.k)
    write_backtest(a.k, res)
    for r in verdict(res):
        print(*r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
