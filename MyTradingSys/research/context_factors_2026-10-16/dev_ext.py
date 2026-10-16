"""DEV_EXT loader: Binance USD-M BTCUSDT 1m klines 2020-01-01 .. 2021-12-31, a SEPARATE segment read only by DEV-stage work.

DECISION (OURS) D3 (MyTradingSys/system/OPERATOR_DECISIONS.md, operator may overrule): DEV_EXT sits immediately before DEV
(bar open < 2022-01-01). DEV (2022-01-01..2024-06-30), VALIDATION (2024-07-01..2025-06-30) and HOLDOUT boundaries are unchanged.
DEV_EXT is OFF unless a caller passes include_dev_ext=True. Whatever the flag, no bar with open >= C.DEV_END_MS (2024-07-01)
is ever returned, and the extension files are listed by month, so a file for another period is never opened.
Perp 1m klines are public only from 2019-12-31 (monthly files from 2020-01); 2019 spot is NOT mixed in (basis, other venue).

  python dev_ext.py        -> prints days / bars / first / last of the segment
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import context_asof as C  # noqa: E402

EXT_DIR = Path("F:/MTS/data/dev_ext_2019_2021")          # klines/*.csv (unzipped), zips/*.zip (+ .CHECKSUM), outside the repo
DEV_EXT_START_MS = 1_577_836_800_000                      # 2020-01-01 00:00 UTC
DEV_EXT_END_MS = C.DEV_START_MS                           # 2022-01-01 00:00 UTC: DEV starts here
EXT_CACHE = C.CACHE / "btcusdt_5m_dev_ext.npz"


def ext_months():
    for y in (2020, 2021):
        for m in range(1, 13):
            yield f"{y}-{m:02d}"


def _read_month(f):
    with Path(f).open("rb") as fh:
        head = fh.read(16)
    df = pd.read_csv(f, header=0 if head.startswith(b"open_time") else None, usecols=range(6))
    df.columns = ["ot", "o", "h", "l", "c", "v"]
    return df


def load_ext_1m(ext_dir=None):
    """1m rows of DEV_EXT only: bar open in [2020-01-01, 2022-01-01). Rows outside are dropped, never returned."""
    d = Path(ext_dir or EXT_DIR) / "klines"
    parts = [_read_month(d / f"BTCUSDT-1m-{ym}.csv") for ym in ext_months()]
    m = pd.concat(parts, ignore_index=True).drop_duplicates("ot").sort_values("ot")
    m = m[(m["ot"] >= DEV_EXT_START_MS) & (m["ot"] < DEV_EXT_END_MS)]
    if len(m) and int(m["ot"].max()) >= DEV_EXT_END_MS:
        raise ValueError("DEV/VALIDATION bar in the DEV_EXT load")
    return m


def load_ext_5m(ext_dir=None, use_cache=True):
    cached = use_cache and ext_dir is None
    if cached and EXT_CACHE.exists():
        z = np.load(EXT_CACHE)
        return {k: z[k] for k in z.files}
    m = load_ext_1m(ext_dir)
    k = (m["ot"].to_numpy(np.int64) // C.MIN5) * C.MIN5
    a = C._agg_frame(m.assign(key=k), "key")
    out = {"ot": a.index.to_numpy(np.int64), "o": a["o"].to_numpy(), "h": a["h"].to_numpy(), "l": a["l"].to_numpy(),
           "c": a["c"].to_numpy(), "v": a["v"].to_numpy()}
    if cached:
        C.CACHE.mkdir(parents=True, exist_ok=True)
        np.savez(EXT_CACHE, **out)
    return out


def load_ext_funding(ext_dir=None):
    import zipfile
    d = Path(ext_dir or EXT_DIR) / "zips"
    rows = []
    for ym in ext_months():
        z = zipfile.ZipFile(d / f"BTCUSDT-fundingRate-{ym}.zip")
        rows.append(pd.read_csv(z.open(z.namelist()[0])))
    f = pd.concat(rows, ignore_index=True).sort_values("calc_time")
    f = f[f["calc_time"] < DEV_EXT_END_MS]
    return f["calc_time"].to_numpy(np.int64), f["last_funding_rate"].to_numpy(float)


def assert_dev_stage(bars):
    """Raise unless every bar opens before 2024-07-01 (VALIDATION / HOLDOUT never pass)."""
    if len(bars["ot"]) and int(np.max(bars["ot"])) >= C.DEV_END_MS:
        raise ValueError("bar at/after 2024-07-01 (VALIDATION/HOLDOUT) refused")
    return bars


def load_dev_bars(include_dev_ext=False, base_loader=None, ext_loader=None, ext_funding_loader=None):
    """C.load_dev() unchanged when include_dev_ext is False; DEV_EXT bars + funding prepended when True.
    The three loaders are injectable for tests."""
    base = (base_loader or C.load_dev)()
    if not include_dev_ext:
        return assert_dev_stage(base)
    ext = (ext_loader or load_ext_5m)()
    ef_t, ef_r = (ext_funding_loader or load_ext_funding)()
    keep = (ext["ot"] >= DEV_EXT_START_MS) & (ext["ot"] < DEV_EXT_END_MS)   # the segment can only end where DEV begins
    out = {k: np.concatenate([ext[k][keep], base[k]]) for k in ("ot", "o", "h", "l", "c", "v")}
    ft = np.concatenate([ef_t[ef_t < DEV_EXT_END_MS], base["fund_t"]]) if "fund_t" in base else ef_t[ef_t < DEV_EXT_END_MS]
    fr = np.concatenate([ef_r[ef_t < DEV_EXT_END_MS], base["fund_r"]]) if "fund_r" in base else ef_r[ef_t < DEV_EXT_END_MS]
    o = np.argsort(ft, kind="stable")
    out["fund_t"], out["fund_r"] = ft[o], fr[o]
    return assert_dev_stage(out)


if __name__ == "__main__":
    e = load_ext_5m()
    print("DEV_EXT 5m bars", len(e["ot"]), "days", len(e["ot"]) / 288, "first", pd.to_datetime(e["ot"][0], unit="ms"),
          "last", pd.to_datetime(e["ot"][-1], unit="ms"))
