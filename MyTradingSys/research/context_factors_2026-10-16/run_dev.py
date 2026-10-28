"""DEV run (no outcome column): vectorised frames for both sides, replay at every DEV decision hour, and the comparison.

  python run_dev.py vec        -> CACHE/frame_long.pkl, frame_short.pkl (every DEV hour from 2022-04-01)
  python run_dev.py replay     -> CACHE/replay.pkl (every DEV hour with a closing 5m bar, 10 processes)
  python run_dev.py compare    -> prints disagreement counts per key (compact) and writes CACHE/disagree.csv
Decisions start 2022-04-01 (OURS warmup: 90 days of 1h ATR history for the volatility percentile, SMA10 weekly + slope).
"""
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
import context_asof as C  # noqa: E402

START_MS = 1_648_771_200_000      # 2022-04-01 00:00 UTC (OURS warmup)
_B = None


def decisions(bars):
    ends = bars["ot"] + C.MIN5
    return ends[(ends % C.HOUR == 0) & (ends >= START_MS) & (ends <= C.DEV_END_MS)]


def _init():
    global _B
    _B = C.load_dev()


def _one(T):
    t = C.decision_index(_B, int(T))
    return C._replay_both(_B, t)


def main(cmd):
    bars = C.load_dev()
    Ts = decisions(bars)
    if cmd == "vec":
        for s in ("long", "short"):
            t0 = time.time()
            f = C.context_frame(bars, s, decisions=Ts)
            f.to_pickle(C.CACHE / f"frame_{s}.pkl")
            print(s, len(f), f"{time.time() - t0:.0f}s")
    elif cmd == "replay":
        t0 = time.time()
        with Pool(10, initializer=_init) as p:
            res = p.map(_one, list(Ts), chunksize=64)
        rows = [r[s] for r in res for s in ("long", "short")]
        pd.DataFrame(rows).to_pickle(C.CACHE / "replay.pkl")
        print("replay rows", len(rows), f"{time.time() - t0:.0f}s")
    elif cmd == "compare":
        rp = pd.read_pickle(C.CACHE / "replay.pkl")
        bad = []
        for s in ("long", "short"):
            f = pd.read_pickle(C.CACHE / f"frame_{s}.pkl")
            r = rp[rp["side"] == s].set_index("T", drop=False)
            assert len(r) == len(f), (len(r), len(f))
            for T in f.index:
                for k in C.row_diff(r.loc[T].to_dict(), f.loc[T].to_dict()):
                    bad.append((s, int(T), k, r.loc[T, k], f.loc[T, k]))
        d = pd.DataFrame(bad, columns=["side", "T", "key", "replay", "vectorised"])
        d.to_csv(C.CACHE / "disagree.csv", index=False)
        print("rows compared", len(rp), "disagreements", len(d))
        if len(d):
            print(d.groupby(["key", "side"]).size().to_string())


if __name__ == "__main__":
    main(sys.argv[1])
