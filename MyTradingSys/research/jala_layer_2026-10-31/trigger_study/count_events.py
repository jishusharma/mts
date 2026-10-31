"""COUNT-ONLY: events per trigger/universe/horizon. Reads closes only to find cross dates; prints no returns."""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import trigger_study as ts
import fetch_daily as fd


def load_all():
    return {s: pd.read_csv(fd.OUT / f"{s}.csv", parse_dates=["date"]).set_index("date")["close"] for s in fd.UNIVERSE}


if __name__ == "__main__":
    C = load_all()
    for s, c in C.items():
        assert c.index.max() == pd.Timestamp("2024-06-30"), s
    for kind in ("under", "over", "golden", "death"):
        for h in ts.HORIZONS:
            per = {s: len(ts.dev_event_filter(c, ts.events(c, kind), h)) for s, c in C.items()}
            alts = sum(v for k, v in per.items() if k != "BTC")
            print(f"{kind:7s} h{h:<3d} BTC {per['BTC']:3d} alts {alts:4d} (symbols with >=1: {sum(1 for k,v in per.items() if v and k!='BTC')})")
