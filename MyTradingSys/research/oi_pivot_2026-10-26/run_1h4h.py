"""DEV follow-up (PRE_REG_1H4H.md): 1h/4h, 2022-01-01..2024-06-30, writes pilot_1h4h_table.csv. Reads no bar with open >= 2024-07-01."""
import csv
import datetime as dt
import io
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as C  # noqa: E402

HERE = Path(__file__).resolve().parent
KL = Path("F:/MTS/data/tom_raw/klines")
CACHE = Path("F:/MTS/data/oi_pivot_2026-10-26")
UTC = dt.timezone.utc
D0, D1 = dt.date(2022, 1, 1), dt.date(2024, 6, 30)
T_END = int(dt.datetime(2024, 7, 1, tzinfo=UTC).timestamp() * 1000)  # DEV cut, exclusive
K, H = 1.0, 24
TFS = (60, 240)
C.TF_BARS_4H.update({60: 4, 240: 4})  # E4: 4h-context lookback 4 bars (OURS)
GATE_CARD, GATE_NOW = 401, 452  # PRE_REG.md n needed; prereg_gate today (PRE_REG_1H4H.md)


def _guard(bars):
    if bars and bars[-1]["t"] >= T_END:  # bars are sorted
        raise ValueError(f"bar open {bars[-1]['t']} >= DEV cut {T_END}")


def label(bars, i, a, side, H=H):
    """Outcome per PRE_REG.md (candidates.outcome); refuses any bar list reaching the DEV cut."""
    _guard(bars)
    return C.outcome(bars, i, a, side, K, H, len(bars) - 1)


def load_1m(files):
    rows = []
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t < T_END:
                    rows.append({"t": t, "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5]), "tb": float(r[9])})
    rows.sort(key=lambda x: x["t"])
    return rows


def load_bars():
    """Per month (bounded memory): 1m -> 1h/4h; months start on 4h boundaries so no bar spans two files."""
    out = {tf: [] for tf in TFS}
    y, m = D0.year, D0.month
    while (y, m) <= (D1.year, D1.month):
        rows = load_1m([KL / f"BTCUSDT-1m-{y}-{m:02d}.csv"])
        for tf in TFS:
            out[tf].extend(C.aggregate(rows, tf))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    for tf in TFS:
        _guard(out[tf])
    return out


def load_oi():
    CACHE.mkdir(parents=True, exist_ok=True)
    oi = {}
    d = D0
    while d <= D1:
        p = CACHE / f"BTCUSDT-metrics-{d}.csv"
        if not p.exists():
            url = f"https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-{d}.zip"
            with urllib.request.urlopen(url, timeout=60) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
            p.write_bytes(z.read(z.namelist()[0]))
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if r and r[0][:1].isdigit() and r[2]:
                    t = int(dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).timestamp() * 1000)
                    oi[t] = float(r[2])
        d += dt.timedelta(days=1)
    return oi


def day_of(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).strftime("%Y-%m-%d")


def main():
    allbars, oi = load_bars(), load_oi()
    out = []
    for tf in TFS:
        bars = allbars[tf]
        base = defaultdict(list)
        for i in range(len(bars) - 1):
            a = C.atr(bars, i)
            if a is None:
                continue
            for side in ("BOTTOM", "TOP"):
                o = label(bars, i, a, side)
                if o != "CENSORED":
                    base[side].append((day_of(bars[i]["t"]), int(o == "HIT")))
        pb = {s: C.cluster_p_se(v) for s, v in base.items()}
        print(f"{tf}m bars {len(bars)} baseline", {s: (round(v[0], 4), round(v[1], 4), len(base[s])) for s, v in pb.items()})
        cells, ncens = defaultdict(list), defaultdict(int)
        counts = defaultdict(lambda: defaultdict(int))
        for f in C.candidates(bars, oi):
            key = (f["name"], f["location"], f["context"])
            o = label(bars, f["i"], f["atr"], f["side"])
            counts[key][o] += 1
            if o == "CENSORED":
                ncens[key] += 1
            else:
                cells[key].append((day_of(bars[f["i"]]["t"]), int(o == "HIT"), f["side"]))
        for name in ("oi_flip", "pv_oi_div", "delta_sign", "vol_spike"):
            for loc in ("AT_LEVEL", "OTHER"):
                for ctx in ("WITH", "AGAINST"):
                    key = (name, loc, ctx)
                    v = cells.get(key, [])
                    p, se = C.cluster_p_se([(d, h) for d, h, _ in v])
                    nb = sum(pb[s][0] for _, _, s in v) / len(v) if v else float("nan")  # side-mix matched
                    nd = len({d for d, _, _ in v})
                    c = counts[key]
                    ok = bool(v) and se > 0
                    out.append({"tf": "1h" if tf == 60 else "4h", "candidate": name, "location": loc, "context": ctx,
                                "n_events": len(v), "n_day_clusters": nd, "HIT": c["HIT"], "MISS": c["MISS"],
                                "AMBIGUOUS": c["AMBIGUOUS"], "TIMEOUT": c["TIMEOUT"], "CENSORED": ncens[key],
                                "P": f"{p:.4f}" if v else "", "P_base": f"{nb:.4f}" if v else "",
                                "diff": f"{p - nb:+.4f}" if v else "", "SE_day": f"{se:.4f}" if v else "",
                                "z": f"{(p - nb) / se:+.2f}" if ok else "",
                                "n_vs_401": "PASS" if nd >= GATE_CARD else "SHORT", "n_vs_452": "PASS" if nd >= GATE_NOW else "SHORT"})
    with open(HERE / "pilot_1h4h_table.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"rows {len(out)}; events {sum(r['n_events'] for r in out)}; cells n_day_clusters >= 401: {sum(r['n_vs_401'] == 'PASS' for r in out)}")


if __name__ == "__main__":
    main()
