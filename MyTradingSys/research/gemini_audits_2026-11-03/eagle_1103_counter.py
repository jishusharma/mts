"""Independent blind-read counter for Eagle_Eyes 11-03 counts (commit 3f73289b6).

Task: gemini-blind-read-eagle-1103-counts
Never imports producer scripts (us_open_roundtrip.py, ethbtc_wt_top.py).

One-line setup restatements from docstrings only:
1. us_open_roundtrip.py: On BTCUSDT 1m weekdays (2022-01..2025-06), select days where
   high(13:30..14:25Z) >= open(13:30Z) * 1.004 and close(14:24Z) < open(13:30Z), then
   measure from close(14:24Z) to 15:30Z/16:30Z whether the 13:30..14:25Z low breaks or
   high is retaken first, along with returns and 1h range.
2. ethbtc_wt_top.py: On synthetic ETHBTC 4h bars built by folding ETHUSDT/BTCUSDT 1m
   closes (2022-01..2025-06), count (a) WaveTrend(10,21,4) cross-down with wt1 > 53,
   (b) same with RSI(14) > 60 at the cross, and (c) RSI(14) first closing > 60 after
   >= 30 consecutive 4h bars <= 60 (Krown regime flip), measuring 12/30/60-bar (2/5/10d)
   forward close returns and 30-bar max up/down.
"""

import csv
import datetime as dt
import glob
import io
import os
import statistics as st
import zipfile
from zoneinfo import ZoneInfo

SPOT_SCRATCH_DIR = os.environ.get(
    "EAGLE_1103_SPOT_DIR",
    r"C:\Users\e-ngineers\AppData\Local\Temp\rederive_vp_klines",
)
UM_SCRATCH_DIR = os.environ.get(
    "EAGLE_1103_UM_DIR",
    r"C:\Users\e-ngineers\AppData\Local\Temp\eagle_1103_um_klines",
)
RAW_DIR = "F:/MTS/data/tom_raw/klines"


def iter_1m_klines(
    sym: str,
    start_ym: str = "2022-01",
    end_ym: str = "2025-06",
    source_dir: str | None = None,
):
    """Yield (utc_ts_seconds, open, high, low, close) from F:/MTS or scratch zips."""
    active_dir = source_dir or (RAW_DIR if os.path.isdir(RAW_DIR) else UM_SCRATCH_DIR)
    csv_files = sorted(glob.glob(os.path.join(active_dir, f"{sym}-1m-*.csv")))
    if csv_files:
        for fpath in csv_files:
            base = os.path.basename(fpath)
            ym = base[len(sym) + 4 : len(sym) + 11]
            if ym < start_ym or ym > end_ym:
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                for r in csv.reader(f):
                    if not r or r[0] == "open_time":
                        continue
                    t = int(r[0])
                    if t > 10**14:
                        t //= 1000
                    t //= 1000
                    yield t, float(r[1]), float(r[2]), float(r[3]), float(r[4])
    else:
        zip_files = sorted(glob.glob(os.path.join(active_dir, f"{sym}-1m-*.zip")))
        for zpath in zip_files:
            base = os.path.basename(zpath)
            ym = base[len(sym) + 4 : len(sym) + 11]
            if ym < start_ym or ym > end_ym:
                continue
            with zipfile.ZipFile(zpath) as zf:
                for name in zf.namelist():
                    with zf.open(name) as raw:
                        for r in csv.reader(io.TextIOWrapper(raw, encoding="utf-8")):
                            if not r or r[0] == "open_time":
                                continue
                            t = int(r[0])
                            if t > 10**14:
                                t //= 1000
                            t //= 1000
                            yield t, float(r[1]), float(r[2]), float(r[3]), float(r[4])


def evaluate_us_open_roundtrip(end_ym: str = "2025-06", source_dir: str | None = None):
    start_date = dt.date(2022, 1, 1)
    end_year, end_month = map(int, end_ym.split("-"))
    if end_month == 12:
        end_date = dt.date(end_year + 1, 1, 1)
    else:
        end_date = dt.date(end_year, end_month + 1, 1)

    days_data = {}
    for t, o, h, l, c in iter_1m_klines("BTCUSDT", "2022-01", end_ym, source_dir):
        u = dt.datetime.fromtimestamp(t, dt.timezone.utc)
        d = u.date()
        if d < start_date or d >= end_date or u.weekday() > 4:
            continue
        m = u.hour * 60 + u.minute
        if 720 <= m <= 1020:
            days_data.setdefault(d, {})[m] = (o, h, l, c)

    ny_tz = ZoneInfo("America/New_York")

    doc_rows = []
    prod_rows = []
    prod_all = []
    ny_dst_rows = []  # DST-adjusted: 08:30..09:24 NY setup -> 09:30..10:30 NY outcome

    for d in sorted(days_data):
        b = days_data[d]
        if any(m not in b for m in (810, 864, 870, 930, 990)):
            continue
        o_810 = b[810][0]
        hi_pre = max(b[m][1] for m in range(810, 865) if m in b)
        lo_pre = min(b[m][2] for m in range(810, 865) if m in b)
        c_864 = b[864][3]
        is_setup = (hi_pre >= o_810 * 1.004) and (c_864 < o_810)

        dt_1330 = dt.datetime(d.year, d.month, d.day, 13, 30, tzinfo=dt.timezone.utc)
        ny_dt = dt_1330.astimezone(ny_tz)
        is_edt = ny_dt.hour == 9 and ny_dt.minute == 30

        # Producer outcome window: m in range(870, 931) [14:30Z..15:30Z inclusive]
        first_p = None
        for m in range(870, 931):
            if m not in b:
                continue
            if first_p is None:
                if b[m][1] >= hi_pre:
                    first_p = "HI"
                elif b[m][2] < lo_pre:
                    first_p = "LO"
        rng_p = (
            max(b[m][1] for m in range(870, 931) if m in b)
            - min(b[m][2] for m in range(870, 931) if m in b)
        ) / c_864
        row_p = dict(
            d=d,
            setup=is_setup,
            first=first_p,
            r1=b[930][3] / c_864 - 1,
            r2=b[990][3] / c_864 - 1,
            rng=rng_p,
            is_edt=is_edt,
        )
        prod_all.append(row_p)
        if is_setup:
            prod_rows.append(row_p)

        # Docstring outcome window: from close(14:24) [m=865] to 15:30Z [m=929 close]
        if is_setup:
            first_d = None
            for m in range(865, 930):
                if m not in b:
                    continue
                if first_d is None:
                    if b[m][1] >= hi_pre:
                        first_d = "HI"
                    elif b[m][2] < lo_pre:
                        first_d = "LO"
            doc_rows.append(
                dict(
                    d=d,
                    first=first_d,
                    r1_929=b[929][3] / c_864 - 1 if 929 in b else b[930][3] / c_864 - 1,
                    r1_930=b[930][3] / c_864 - 1,
                    is_edt=is_edt,
                )
            )

        # DST-consistent NY pre-open (08:30..09:24 NY) -> NY cash open (09:30..10:30 NY)
        shift = -60 if is_edt else 0
        m0, m1, m2, m3, m4 = 810 + shift, 864 + shift, 870 + shift, 930 + shift, 990 + shift
        if all(m in b for m in (m0, m1, m2, m3, m4)):
            o_ny = b[m0][0]
            hi_ny = max(b[m][1] for m in range(m0, m1 + 1) if m in b)
            lo_ny = min(b[m][2] for m in range(m0, m1 + 1) if m in b)
            c_ny = b[m1][3]
            if hi_ny >= o_ny * 1.004 and c_ny < o_ny:
                first_ny = None
                for m in range(m2, m3 + 1):
                    if m not in b:
                        continue
                    if first_ny is None:
                        if b[m][1] >= hi_ny:
                            first_ny = "HI"
                        elif b[m][2] < lo_ny:
                            first_ny = "LO"
                ny_dst_rows.append(dict(d=d, first=first_ny, r1=b[m3][3] / c_ny - 1))

    return prod_all, prod_rows, doc_rows, ny_dst_rows


def ema_series(xs, period: int):
    alpha = 2.0 / (period + 1)
    out = [xs[0]]
    for x in xs[1:]:
        out.append(out[-1] + alpha * (x - out[-1]))
    return out


def evaluate_ethbtc_wt_top(end_ym: str = "2025-06", source_dir: str | None = None):
    start_date = dt.date(2022, 1, 1)
    end_year, end_month = map(int, end_ym.split("-"))
    if end_month == 12:
        end_date = dt.date(end_year + 1, 1, 1)
    else:
        end_date = dt.date(end_year, end_month + 1, 1)

    eth_4h = {}
    eth_1m_hlc = {}
    for t, o, h, l, c in iter_1m_klines("ETHUSDT", "2022-01", end_ym, source_dir):
        b4 = t - (t % 14400)
        if t % 14400 == 14340:
            eth_4h[b4] = c
        eth_1m_hlc[t] = c

    btc_4h = {}
    ethbtc_4h_hl = {}
    for t, o, h, l, c in iter_1m_klines("BTCUSDT", "2022-01", end_ym, source_dir):
        b4 = t - (t % 14400)
        if t % 14400 == 14340:
            btc_4h[b4] = c
        if t in eth_1m_hlc and c > 0:
            ratio = eth_1m_hlc[t] / c
            if b4 not in ethbtc_4h_hl:
                ethbtc_4h_hl[b4] = [ratio, ratio]
            else:
                if ratio > ethbtc_4h_hl[b4][0]:
                    ethbtc_4h_hl[b4][0] = ratio
                if ratio < ethbtc_4h_hl[b4][1]:
                    ethbtc_4h_hl[b4][1] = ratio

    ks = sorted(
        k
        for k in eth_4h
        if k in btc_4h
        and start_date <= dt.datetime.fromtimestamp(k, dt.timezone.utc).date() < end_date
    )
    closes = [eth_4h[k] / btc_4h[k] for k in ks]
    hlc3 = [
        (ethbtc_4h_hl[k][0] + ethbtc_4h_hl[k][1] + (eth_4h[k] / btc_4h[k])) / 3.0
        for k in ks
    ]
    n = len(closes)

    # 1. Producer WaveTrend(10, 21, 4) on 4h closes
    esa = ema_series(closes, 10)
    dev = ema_series([abs(c - e) for c, e in zip(closes, esa)], 10)
    ci = [(c - e) / (0.015 * d) if d else 0.0 for c, e, d in zip(closes, esa, dev)]
    wt1 = ema_series(ci, 21)
    wt2 = [None] * 3 + [sum(wt1[i - 3 : i + 1]) / 4.0 for i in range(3, n)]

    # 2. Standard WaveTrend(10, 21, 4) on 4h HLC3
    esa_h = ema_series(hlc3, 10)
    dev_h = ema_series([abs(ap - e) for ap, e in zip(hlc3, esa_h)], 10)
    ci_h = [(ap - e) / (0.015 * d) if d else 0.0 for ap, e, d in zip(hlc3, esa_h, dev_h)]
    wt1_h = ema_series(ci_h, 21)
    wt2_h = [None] * 3 + [sum(wt1_h[i - 3 : i + 1]) / 4.0 for i in range(3, n)]

    # Wilder RSI(14) on 4h closes
    rsi = [None] * n
    ag = al = 0.0
    for i in range(1, n):
        ch = closes[i] - closes[i - 1]
        g = max(ch, 0.0)
        lo = max(-ch, 0.0)
        if i <= 14:
            ag += g / 14.0
            al += lo / 14.0
        else:
            ag = (ag * 13.0 + g) / 14.0
            al = (al * 13.0 + lo) / 14.0
        if i >= 14:
            rsi[i] = 100.0 - 100.0 / (1.0 + ag / al) if al else 100.0

    def outcomes_prod(i):
        p = closes[i]
        w = closes[i + 1 : i + 31]
        return dict(
            i=i,
            r12=closes[i + 12] / p - 1.0,
            r30=closes[i + 30] / p - 1.0,
            r60=closes[min(n - 1, i + 60)] / p - 1.0,
            mx=max(w) / p - 1.0,
            mn=min(w) / p - 1.0,
        )

    wt_all_prod, wt_rsi_prod, krown_prod = [], [], []
    side = 0
    under = 0
    for i in range(60, n - 31):
        s = 1 if wt1[i] > wt2[i] else (-1 if wt1[i] < wt2[i] else 0)
        if side == 1 and s == -1 and wt1[i] > 53:
            wt_all_prod.append(outcomes_prod(i))
            if rsi[i] > 60:
                wt_rsi_prod.append(outcomes_prod(i))
        if s:
            side = s
        if rsi[i] > 60:
            if under >= 30:
                krown_prod.append(outcomes_prod(i))
            under = 0
        else:
            under += 1

    # HLC3 WaveTrend with producer loop
    wt_rsi_hlc3 = []
    side_h = 0
    for i in range(60, n - 31):
        s = 1 if wt1_h[i] > wt2_h[i] else (-1 if wt1_h[i] < wt2_h[i] else 0)
        if side_h == 1 and s == -1 and wt1_h[i] > 53 and rsi[i] > 60:
            wt_rsi_hlc3.append(outcomes_prod(i))
        if s:
            side_h = s

    # Docstring-strict loop: track state from warmup (i >= 14) and require full 60-bar horizon (i < n - 60)
    wt_rsi_doc, krown_doc = [], []
    side_d = 0
    under_d = 0
    for i in range(14, n - 60):
        s = 1 if wt1[i] > wt2[i] else (-1 if wt1[i] < wt2[i] else 0)
        if i >= 60 and side_d == 1 and s == -1 and wt1[i] > 53 and rsi[i] > 60:
            wt_rsi_doc.append(outcomes_prod(i))
        if s:
            side_d = s
        if rsi[i] > 60:
            if i >= 60 and under_d >= 30:
                krown_doc.append(outcomes_prod(i))
            under_d = 0
        else:
            under_d += 1

    baseline_prod = [outcomes_prod(i) for i in range(60, n - 31)]
    return dict(
        n_bars=n,
        start_dt=dt.datetime.fromtimestamp(ks[0], dt.timezone.utc).date(),
        end_dt=dt.datetime.fromtimestamp(ks[-1], dt.timezone.utc).date(),
        baseline=baseline_prod,
        wt_all=wt_all_prod,
        wt_rsi=wt_rsi_prod,
        wt_rsi_hlc3=wt_rsi_hlc3,
        krown=krown_prod,
        wt_rsi_doc=wt_rsi_doc,
        krown_doc=krown_doc,
    )


if __name__ == "__main__":
    for label, sdir in [("UM_FUTURES", UM_SCRATCH_DIR), ("SPOT", SPOT_SCRATCH_DIR)]:
        if not os.path.isdir(sdir):
            continue
        print(f"================ {label} ({sdir}) ================")
        for ym in ("2025-06", "2024-06"):
            prod_all, prod_rows, doc_rows, ny_rows = evaluate_us_open_roundtrip(ym, sdir)
            k = len(prod_rows)
            lo_pct = 100.0 * sum(x["first"] == "LO" for x in prod_rows) / k
            hi_pct = 100.0 * sum(x["first"] == "HI" for x in prod_rows) / k
            r1_med = 100.0 * st.median(x["r1"] for x in prod_rows)
            rng_med = 100.0 * st.median(x["rng"] for x in prod_rows)
            rng_all = 100.0 * st.median(x["rng"] for x in prod_all)
            print(
                f"  [US Open Producer 2022-01..{ym}] weekdays={len(prod_all)} n={k} "
                f"low_first={lo_pct:.2f}% ({lo_pct:.0f}%) high_first={hi_pct:.2f}% ({hi_pct:.0f}%) "
                f"r@15:30={r1_med:+.2f}% 1h_rng={rng_med:.2f}% vs {rng_all:.2f}%"
            )
            kd = len(doc_rows)
            print(
                f"    [Docstring 14:25..15:29Z] n={kd} "
                f"low_first={100*sum(x['first']=='LO' for x in doc_rows)/kd:.2f}% "
                f"high_first={100*sum(x['first']=='HI' for x in doc_rows)/kd:.2f}%"
            )
            edt = [x for x in prod_rows if x["is_edt"]]
            est = [x for x in prod_rows if not x["is_edt"]]
            kny = len(ny_rows)
            print(
                f"    [DST] EDT(summer 09:30NY) n={len(edt)} LO={100*sum(x['first']=='LO' for x in edt)/len(edt):.1f}% HI={100*sum(x['first']=='HI' for x in edt)/len(edt):.1f}% | "
                f"EST(winter 08:30NY) n={len(est)} LO={100*sum(x['first']=='LO' for x in est)/len(est):.1f}% HI={100*sum(x['first']=='HI' for x in est)/len(est):.1f}% | "
                f"NY-aligned(08:30..09:24NY->09:30..10:30NY) n={kny} LO={100*sum(x['first']=='LO' for x in ny_rows)/kny:.1f}% HI={100*sum(x['first']=='HI' for x in ny_rows)/kny:.1f}%"
            )
        for ym in ("2024-06", "2025-06"):
            res = evaluate_ethbtc_wt_top(ym, sdir)
            wt = res["wt_rsi"]
            kw = res["krown"]
            wth = res["wt_rsi_hlc3"]
            wtd = res["wt_rsi_doc"]
            kwd = res["krown_doc"]
            print(
                f"  [ETHBTC 2022-01..{ym}] bars={res['n_bars']} "
                f"WT_top+RSI>60: n={len(wt)} 10d={100*st.median(x['r60'] for x in wt):+.2f}% "
                f"(HLC3 WT: n={len(wth)} 10d={100*st.median(x['r60'] for x in wth):+.2f}%; "
                f"full-60b doc: n={len(wtd)} 10d={100*st.median(x['r60'] for x in wtd):+.2f}%) | "
                f"Krown: n={len(kw)} 5d={100*st.median(x['r30'] for x in kw):+.2f}% "
                f"(full-60b+warmup doc: n={len(kwd)} 5d={100*st.median(x['r30'] for x in kwd):+.2f}%)"
            )
