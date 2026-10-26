"""DEV pilot (PRE_REG.md): 5m/15m, 2024-06-01..06-30, writes pilot_table.csv. Reads no bar with open >= 2024-07-01."""
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
T_WARM = int(dt.datetime(2024, 5, 29, tzinfo=UTC).timestamp() * 1000)
T_START = int(dt.datetime(2024, 6, 1, tzinfo=UTC).timestamp() * 1000)
T_END = int(dt.datetime(2024, 7, 1, tzinfo=UTC).timestamp() * 1000)  # DEV cut, exclusive
K, H = 1.0, 24


def load_1m():
    rows = []
    for f in (KL / "BTCUSDT-1m-2024-05.csv", KL / "BTCUSDT-1m-2024-06.csv"):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if T_WARM <= t < T_END:
                    rows.append({"t": t, "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5]), "tb": float(r[9])})
    rows.sort(key=lambda x: x["t"])
    return rows


def load_oi():
    CACHE.mkdir(parents=True, exist_ok=True)
    oi = {}
    d = dt.date(2024, 5, 29)
    while d <= dt.date(2024, 6, 30):
        p = CACHE / f"BTCUSDT-metrics-{d}.csv"
        if not p.exists():
            url = f"https://data.binance.vision/data/futures/um/daily/metrics/BTCUSDT/BTCUSDT-metrics-{d}.zip"
            with urllib.request.urlopen(url, timeout=60) as r:
                z = zipfile.ZipFile(io.BytesIO(r.read()))
            p.write_bytes(z.read(z.namelist()[0]))
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if r and r[0][:1].isdigit():
                    t = int(dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).timestamp() * 1000)
                    oi[t] = float(r[2])
        d += dt.timedelta(days=1)
    return oi


def day_of(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).strftime("%Y-%m-%d")


def main():
    rows, oi = load_1m(), load_oi()
    out = []
    for tf in (5, 15):
        bars = C.aggregate(rows, tf)
        last = len(bars) - 1
        sel = [f for f in C.candidates(bars, oi) if bars[f["i"]]["t"] >= T_START]
        # baseline: every bar in the window, both sides
        base = defaultdict(list)
        for i in range(len(bars)):
            if bars[i]["t"] < T_START:
                continue
            a = C.atr(bars, i)
            if a is None or i + 1 > last:
                continue
            for side in ("BOTTOM", "TOP"):
                o = C.outcome(bars, i, a, side, K, H, last)
                if o != "CENSORED":
                    base[side].append((day_of(bars[i]["t"]), int(o == "HIT")))
        pb = {s: C.cluster_p_se(v) for s, v in base.items()}
        cells = defaultdict(list)
        ncens = defaultdict(int)
        counts = defaultdict(lambda: defaultdict(int))
        for f in sel:
            key = (f["name"], f["location"], f["context"])
            o = C.outcome(bars, f["i"], f["atr"], f["side"], K, H, last)
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
                    # baseline matched to the side mix of the cell
                    nb = sum(pb[s][0] for _, _, s in v) / len(v) if v else float("nan")
                    c = counts[key]
                    out.append({"tf": f"{tf}m", "candidate": name, "location": loc, "context": ctx, "n": len(v),
                                "days": len({d for d, _, _ in v}), "HIT": c["HIT"], "MISS": c["MISS"], "AMBIGUOUS": c["AMBIGUOUS"],
                                "TIMEOUT": c["TIMEOUT"], "CENSORED": ncens[key],
                                "P": "" if not v else f"{p:.4f}", "SE_day": "" if not v else f"{se:.4f}",
                                "P_base": "" if not v else f"{nb:.4f}", "diff": "" if not v else f"{p - nb:+.4f}"})
    with open(HERE / "pilot_table.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for tf in ("5m", "15m"):
        print(tf, "bars baseline", {s: (round(v[0], 4), round(v[1], 4)) for s, v in pb.items()} if tf == "15m" else "")
    print(f"rows {len(out)}; cells with n>0: {sum(1 for r in out if r['n'])}")


if __name__ == "__main__":
    main()
