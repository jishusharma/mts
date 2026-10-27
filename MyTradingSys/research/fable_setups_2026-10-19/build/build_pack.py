"""Build the Fable run 4 pack (LOOK window only). Usage: python build_pack.py <raw_dir> <pack_dir>
Source: public Binance USD-M BTCUSDT 1m klines (data.binance.vision monthly zips), downloaded into raw_dir
(NOT into the repo). Every other timeframe is aggregated from the 1m bars so all files agree.
Window: bar open in [2022-01-01, 2023-06-30 23:59 UTC]. Asserted below; leak_check.py re-checks the output."""
import csv, io, os, sys, urllib.request, zipfile
from datetime import datetime, timezone, timedelta
import numpy as np

START_MS = int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
END_MS = int(datetime(2023, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)  # exclusive
MONTHS = [(2022 + (m // 12), m % 12 + 1) for m in range(18)]
W = 10.0  # FORMULAS 18.1 bin width (NO-SOURCE there, reused unchanged)
VA = 0.70
MIN = 60000
DAY = 86400000
# Session windows, UTC minutes of day. DECISION (OURS): Asia/EU from session_levels.py (0-480, 480-840);
# NY = US open (840) to day end, because session_levels has no NY window.
SESSIONS = {"asia": (0, 480), "london": (480, 840), "ny": (840, 1440)}


def fetch(raw_dir):
    os.makedirs(raw_dir, exist_ok=True)
    rows = []
    for y, m in MONTHS:
        name = f"BTCUSDT-1m-{y}-{m:02d}"
        p = os.path.join(raw_dir, name + ".zip")
        if not os.path.exists(p):
            urllib.request.urlretrieve(f"https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1m/{name}.zip", p)
        with zipfile.ZipFile(p) as z:
            for line in io.TextIOWrapper(z.open(name + ".csv")):
                f = line.strip().split(",")
                if not f[0].isdigit():
                    continue
                rows.append((int(f[0]), float(f[1]), float(f[2]), float(f[3]), float(f[4]), float(f[5]), float(f[9])))
    a = np.array(rows, dtype=float)
    a = a[np.argsort(a[:, 0])]
    assert a[0, 0] == START_MS, a[0, 0]
    assert a[:, 0].max() < END_MS, "bar open at or after the LOOK window end"
    assert len(np.unique(a[:, 0])) == len(a), "duplicate 1m bars"
    return a  # cols: t,o,h,l,c,v,tbv


def profile(h, l, v, w=W):
    """FORMULAS 18.1. h,l,v arrays of one bar set. Returns (poc_price, val, vah) or None."""
    if len(h) == 0 or v.sum() <= 0:
        return None
    k_lo = int(np.floor(l.min() / w)); k_hi = int(np.floor(h.max() / w))
    vol = np.zeros(k_hi - k_lo + 1)
    for hh, ll, vv in zip(h, l, v):
        if vv == 0:
            continue
        if hh == ll:
            vol[int(np.floor(ll / w)) - k_lo] += vv
            continue
        a = int(np.floor(ll / w)); b = int(np.floor(hh / w))
        ks = np.arange(a, b + 1)
        ov = np.minimum(hh, (ks + 1) * w) - np.maximum(ll, ks * w)
        vol[ks - k_lo] += vv * ov / (hh - ll)
    total = vol.sum()
    poc = int(np.argmax(vol))  # first max = lowest bin
    lo = hi = poc; acc = vol[poc]
    while acc < VA * total and (lo > 0 or hi < len(vol) - 1):
        vl = vol[lo - 1] if lo > 0 else -1
        vh = vol[hi + 1] if hi < len(vol) - 1 else -1
        if vl >= vh and lo > 0:
            lo -= 1; acc += vol[lo]
        else:
            hi += 1; acc += vol[hi]
    return ((poc + k_lo) * w + w / 2, (lo + k_lo) * w, (hi + k_lo + 1) * w)


def agg(a, step_ms, origin_ms=0, complete_only=True):
    """Aggregate 1m rows to bars of step_ms aligned to origin. Drops bars not fully inside the window."""
    key = (a[:, 0] - origin_ms) // step_ms
    out = []
    for k in np.unique(key):
        s = a[key == k]
        t0 = origin_ms + int(k) * step_ms
        if complete_only and (t0 < START_MS or t0 + step_ms > END_MS or len(s) != step_ms // MIN):
            continue
        out.append((t0, s[0, 1], s[:, 2].max(), s[:, 3].min(), s[-1, 4], s[:, 5].sum(), s[:, 6].sum()))
    return out


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(header); w.writerows(rows)


def session_cols(s, t0):
    """Session H/L for 1m rows s of a period; returns [asia_h, asia_l, london_h, london_l, ny_h, ny_l]."""
    mod = ((s[:, 0] - t0) % DAY) // MIN
    out = []
    for lo, hi in SESSIONS.values():
        m = (mod >= lo) & (mod < hi)
        out += [round(s[m, 2].max(), 2), round(s[m, 3].min(), 2)] if m.any() else ["", ""]
    return out


def levels(a, step_ms, origin_ms):
    rows = []
    key = (a[:, 0] - origin_ms) // step_ms
    for k in np.unique(key):
        s = a[key == k]; t0 = origin_ms + int(k) * step_ms
        if t0 < START_MS or t0 + step_ms > END_MS or len(s) != step_ms // MIN:
            continue
        poc, val, vah = profile(s[:, 2], s[:, 3], s[:, 5])
        rows.append([iso(t0), s[0, 1], s[:, 2].max(), s[:, 3].min(), s[-1, 4],
                     poc, vah, val] + session_cols(s, t0))
    return rows


def main(raw_dir, pack_dir):
    a = fetch(raw_dir)
    os.makedirs(pack_dir, exist_ok=True)
    wk_origin = int(datetime(2021, 12, 27, tzinfo=timezone.utc).timestamp() * 1000)  # a Monday
    for name, step, origin in (("1w", 7 * DAY, wk_origin), ("1d", DAY, 0), ("12h", DAY // 2, 0), ("4h", DAY // 6, 0)):
        bars = agg(a, step, origin)
        write_csv(os.path.join(pack_dir, f"ohlcv_{name}.csv"),
                  ["open_time_utc", "open", "high", "low", "close", "volume", "taker_buy_volume"],
                  [[iso(b[0])] + [round(x, 2) if i < 4 else round(x, 3) for i, x in enumerate(b[1:])] for b in bars])
        print(name, len(bars), iso(bars[0][0]), iso(bars[-1][0]))
    hdr = ["period_open_utc", "open", "high", "low", "close", "poc", "vah", "val",
           "asia_high", "asia_low", "london_high", "london_low", "ny_high", "ny_low"]
    write_csv(os.path.join(pack_dir, "levels_daily.csv"), hdr, levels(a, DAY, 0))
    wrows = levels(a, 7 * DAY, wk_origin)
    write_csv(os.path.join(pack_dir, "levels_weekly.csv"), hdr, wrows)
    print("levels", len(wrows), "weeks")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
