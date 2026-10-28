"""Generate golden_wt_btcusdt_1h_dev_2022-01.csv from FORMULAS.md section 20 with pandas, NOT from wavetrend.py.

Independent recomputation (pandas ewm adjust=False = first-value seed recursion, rolling mean), the stand-in for the
spreadsheet the contract asks for. This is spreadsheet-style parity, not Pine-runtime parity (no TradingView export).
Run: python make_golden.py   (rewrites the golden CSV; review the diff before committing)
"""
import numpy as np
import pandas as pd
from pathlib import Path

here = Path(__file__).parent
bars = pd.read_csv(here / "fixture_btcusdt_1h_dev_2022-01.csv")
ap = (bars.high + bars.low + bars.close) / 3.0
esa = ap.ewm(span=10, adjust=False).mean()
d = (ap - esa).abs().ewm(span=10, adjust=False).mean()
ci = (ap - esa) / (0.015 * d)
wt1 = ci.ewm(span=21, adjust=False).mean()
wt2 = wt1.rolling(4).mean()
# cross "le": sign of wt1-wt2 with ties dropped, forward-filled; event where the strict side flips
side = np.sign(wt1 - wt2).replace(0, np.nan)
last = side.ffill().shift(1)
ev = np.where(side.notna() & last.notna() & (side != last), side, 0).astype(int)
out = pd.DataFrame({"open_time": bars.open_time, "wt1": wt1, "wt2": wt2, "event": ev})
out.to_csv(here / "golden_wt_btcusdt_1h_dev_2022-01.csv", index=False, lineterminator="\n", float_format="%.12f")
print(len(out), "rows;", int((out.event != 0).sum()), "events after bar 200:", int((out.event.iloc[200:] != 0).sum()))
