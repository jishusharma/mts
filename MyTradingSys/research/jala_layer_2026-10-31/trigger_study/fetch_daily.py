"""Fetch public Binance spot 1d klines (data.binance.vision monthly zips) into Dumps/jala_trigger/<SYM>.csv.
Warmup from 2020-06 (SMA only); end 2024-06 (DEV ends 2024-07-01). Public data only."""
import io, sys, urllib.request, urllib.error, zipfile
from pathlib import Path
import pandas as pd

UNIVERSE = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "DOT", "LTC", "LINK", "BCH", "XLM", "TRX", "ETC",
            "ATOM", "VET", "FIL", "ALGO", "AVAX", "MATIC", "UNI"]
OUT = Path(__file__).resolve().parents[4] / "Dumps" / "jala_trigger"
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "qv", "n", "tbb", "tbq", "ig"]


def months(a="2020-06", b="2024-06"):
    return [m.strftime("%Y-%m") for m in pd.period_range(a, b, freq="M")]


def fetch(sym):
    frames = []
    for m in months():
        url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}USDT/1d/{sym}USDT-1d-{m}.zip"
        raw = None
        for _ in range(4):
            try:
                raw = urllib.request.urlopen(url, timeout=30).read()
                break
            except urllib.error.HTTPError:
                break
            except Exception:
                continue
        if raw is None:
            continue
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            frames.append(pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS))
    df = pd.concat(frames)
    ot = df["open_time"].astype("int64")
    ot = ot.where(ot < 10**14, ot // 1000)  # 2025+ files are microseconds; not expected here
    df["date"] = pd.to_datetime(ot, unit="ms").dt.normalize()
    df = df.drop_duplicates("date").sort_values("date")
    return df[["date", "close"]]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for s in UNIVERSE:
        if (OUT / f"{s}.csv").exists():
            continue
        d = fetch(s)
        d.to_csv(OUT / f"{s}.csv", index=False)
        print(s, len(d), d["date"].min().date(), d["date"].max().date())
