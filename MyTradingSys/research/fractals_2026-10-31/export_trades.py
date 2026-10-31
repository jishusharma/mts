"""Write the percent-only trade lists of F1 and F2 next to their RESULT.md (no re-run, no re-tuning, DEV only).

F1: reads the run's events.csv (default F:/MTS/runs/fractal_f1/events.csv, written by f1/run_f1.py) and writes
    f1/trades_pct.csv (real events only: time, group, side, why, net_r, net_pct).
F2: joins the hourly H series (F:/MTS/runs/fractal_f2/h1h.csv, written by f2/run_f2.py) to the P1b RSI events and the
    F1 fade events with the same lookup run_f2.py uses, and writes f2/gate_events.csv (layer, time, h, net_r).
F3 writes its own f3/trades_pct.csv from run_f3.py.
No prices are written: the repo is public.

Usage: python export_trades.py [f1_events.csv] [f2_h1h.csv]
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
F1_EVENTS = "F:/MTS/runs/fractal_f1/events.csv"
F2_H = "F:/MTS/runs/fractal_f2/h1h.csv"
NL = chr(10)


def iso(ts):
    return pd.to_datetime(pd.Series(np.asarray(ts)), unit="s", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def f1_real(path):
    ev = pd.read_csv(path)
    return ev[ev.kind == "real"].sort_values("t").reset_index(drop=True)


def export_f1(path=F1_EVENTS, out=None):
    out = out or os.path.join(HERE, "f1", "trades_pct.csv")
    r = f1_real(path)
    df = pd.DataFrame({"time": iso(r["t"]).to_numpy(), "group": r["group"].to_numpy(),
                       "side": np.where(r["side_kind"] > 0, "short", "long"),   # fade: resistance -> short
                       "why": r["why"].to_numpy(), "net_r": r["net_r"].round(6).to_numpy(), "net_pct": r["net_pct"].round(6).to_numpy()})
    df.to_csv(out, index=False, lineterminator=NL)
    return len(df)


def export_f2(h_path=F2_H, f1_path=F1_EVENTS, out=None):
    out = out or os.path.join(HERE, "f2", "gate_events.csv")
    hs = pd.read_csv(h_path)
    avail = hs["avail"].to_numpy(np.int64)
    h = hs["h"].to_numpy(float)
    rsi = pd.read_csv(os.path.join(HERE, "p1b_rsi_feenet", "events_feenet.csv"))
    rsi["ts"] = (pd.to_datetime(rsi["time"], utc=True) - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)
    fade = f1_real(f1_path)
    raw = {"RSI-DIV-MTF": (rsi["ts"].to_numpy(np.int64), rsi["r_net"].to_numpy(float)),
           "FADE": (fade["t"].to_numpy(np.int64), fade["net_r"].to_numpy(float))}
    rows = []
    for layer, (t, y) in raw.items():
        idx = np.searchsorted(avail, t, side="right") - 1      # same lookup as f2/run_f2.py lookup_idx
        ok = idx >= 0
        ok[ok] = ~np.isnan(h[idx[ok]])
        for tt, hh, yy in zip(t[ok], h[idx[ok]], y[ok]):
            rows.append((layer, iso([tt])[0], round(float(hh), 6), round(float(yy), 6)))
    pd.DataFrame(rows, columns=["layer", "time", "h", "net_r"]).to_csv(out, index=False, lineterminator=NL)
    return len(rows)


if __name__ == "__main__":
    a = sys.argv[1:]
    print("f1 trades", export_f1(*(a[:1])))
    print("f2 gate events", export_f2(*(a[1:2]), *(a[:1])))
