"""Krown recall check (PRE_REG_KROWN item 3, card krown-recall-check): verify his dated chart examples against klines,
then run the v0 detectors on the verified ones (recall within 2 bars) and report the fire rate per setup.

Reads only DEV bars (open_time < 2024-07-01 UTC) from the checksum-verified public klines in F:/MTS/data/krown_daily
(DATA_MANIFEST.csv, all OK). Examples that fall in VALIDATION or HOLDOUT (VOL-08 Feb 2026, SNR-17 about 108,000) are
NOT READ and dropped. No P&L. Detector parameters stay at v0 (krown_params.json): an example that does not verify is
listed and dropped, never fixed.

Usage: python run_recall_check.py --prereg   -> writes RECALL_PREREG.md (rules, before any run)
       python run_recall_check.py            -> writes RECALL.md (verification + recall + fire rate)
"""
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import krown_core as kc  # noqa: E402
import krown_events as ke  # noqa: E402
from run_fire_counts import weekly_bars  # noqa: E402

DATA = Path("F:/MTS/data/krown_daily")
RES = Path(__file__).resolve().parents[3] / "research" / "krown_ta101_2026-10-13"
DEV_END_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)  # exclusive: nothing later is kept
DAY = 86400000
WIN = 2  # bars either side

PREREG = """\
# Krown recall check: rules fixed before the run (PRE_REG_KROWN item 3)

Data: Binance spot BTCUSDT 1d and 1w_from_1d, Coinbase BTC-USD 1d (weekly built Monday-start, full weeks), all from
`F:/MTS/data/krown_daily` (DATA_MANIFEST.csv: every zip matched its published checksum). Only bars with open time before
2024-07-01 UTC are loaded (DEV); VALIDATION and HOLDOUT are not read. Detector parameters stay at v0.

**Pass bars (OURS, from PRE_REG_KROWN item 3, restated):**
1. RECALL: detector fires within 2 bars (either side) of the example's target bar for at least 6 examples that verify against klines.
   Strict count = every verified example, an example with no v0 detector counts as a miss. A covered count (verified
   AND a v0 detector is mapped) is shown next to it, never instead of it.
2. FIRE RATE: per setup S1..S9 pooled on Binance 1d DEV, at most 1.0 event per 10 daily bars. Weekly rates are shown for information.
3. Chance baseline per row: share of all bars of that series that have a matching event within 2 bars (so a hit is read against it).

**Verification rule per example** (a caption is not evidence; the klines are). Tolerances are OURS and fixed here:
- R01 VOL-13 weekly low March 2020: target = lowest-low week among weeks opening 2020-02-17..2020-04-13 (Binance 1w); verified if that week's volume >= 2.5x the mean of the prior 20 weeks (he says 3 to 3.5x). Detector: any long event S1-S8, 1w.
- R03 TRL-20 Dec 2018 anchor respected Mar 2020: verified if the Mar 2020 weekly low is above the Dec 2018 weekly low and the Dec 2018 low week volume >= 2x the prior 20 weeks (Binance 1w). A trend line has no price in the caption: only these two facts are checked. Detector: none in v0 (no trend-line detector).
- R04 RNG-05 2018 range, about February to November: span 2018-02-15..2018-11-13 (Binance 1d); verified if max close / min close <= 2.0. Detector: `range_state` non-empty on >= 50% of the span's days (S3 and S4 counts shown).
- R06a-d MAV-16 weekly 200 SMA lows 2015, 2018, 2020, 2022 (Coinbase 1w, the only series long enough): verified if the cycle-low week's low is within +-15% of the weekly SMA200 (a 200-week average needs 200 weeks: 2015 and 2018 lows come before the first Coinbase week that has one = NOT_IN_DATA). Cycle-low weeks: 2020 = lowest low weeks opening 2020-02-17..2020-04-13; 2022 = lowest low among weeks opening 2022-05-01..2022-12-31. Detector: none in v0 (S5 uses the 200 SMA of its own timeframe, not a weekly touch).
- R07 MAV-21 death cross January 2022 (Binance 1d): verified if the SMA50 crosses below the SMA200 on a day in 2021-12-15..2022-02-15 and the SMA200 is lower than 30 days earlier. Detector: S5 short within 2 daily bars of the cross (S5 is the only cross setup; its 21/55 cross is a different pair from his 50/200).
- R09 TOP-12 Bitcoin 2017 weekly top (Coinbase 1w; Binance weekly has only about 17 weeks before December, too few for BBWP): target = highest-high week among weeks opening 2017-09-01..2018-03-31; verified if (a) it opens in December 2017, (b) BBWP (v0 params) >= 85 on at least 8 weeks opening 2017-05-01..target, (c) the target week volume >= 2x the prior 30 weeks, (d) weekly RSI14 (own Wilder) at the target < its maximum over the prior 12 weeks while the target high exceeds all 12 prior highs, (e) own MACD(12,26,9) crosses down within 8 weeks after the target. Detector: S9 short, 1w, Coinbase.
- R10 TOP-32 Bitcoin 2021 weekly top (Binance 1w): target = highest-high week among weeks opening 2021-10-01..2021-12-31; verified if (a) RSI14 at the target < RSI14 at the highest-high week opening 2021-03-01..2021-05-31 while the target high is higher, (b) the target week or the week before is a shooting star on raw bars (upper wick >= 2x body, body in the lower third of the range), (c) own MACD crosses down within 8 weeks after the target. Detector: S9 short, 1w.
- R12 VJZ-50 coming off the 2018 lows, 55 EMA reclaim then break, about 4,000 to 14,000 (Binance 1w, inferred weekly): target = first weekly close above the weekly EMA55 after the lowest-low week opening 2018-11-01..2019-01-31; verified if that close is within 3,000..5,000 and the highest high in the next 26 weeks is within 12,600..15,400. Detector: S2 or S5 long, 1w.
- R13 VJZ-49 about 40,000 to 52,000 (Binance 1d, timeframe inferred daily): low bar = lowest low among days 2024-01-01..2024-02-10; verified if that low is within 38,000..42,000 and the highest high in the next 30 days is within 50,500..53,500. Detector: S2, S5 or S8 long on any day from the low bar to the first day with high >= 50,500 (generous window: the caption names no signal bar).

**Dropped without a read (listed in RECALL.md):** VOL-08 (February 2026 low: HOLDOUT, sealed), SNR-17 (the 100,000 test reached
about 108,000: after 2024-07, sealed), MAV-11/MAV-15 (no date, price or extract cite in the pre-reg row), VJZ-13 (weekly 55 EMA
reclaim given up in two closes: no date or price in the caption), KCM-15 (two BBWP-high dumps: no date or price).
"""


def load(name):
    rows = []
    with open(DATA / name, newline="", encoding="utf-8") as f:
        for r in csv.reader(f):
            if not r or not r[0].isdigit():
                continue
            t = int(r[0])
            if t >= DEV_END_MS:
                break
            rows.append((t, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])))
    return rows


def day(t):
    return datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%Y-%m-%d")


def ms(s):
    return int(datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


def idx_range(rows, a, b):
    """indices with open date in [a, b] (inclusive dates)."""
    return [i for i, r in enumerate(rows) if ms(a) <= r[0] <= ms(b)]


def argmin_low(rows, a, b):
    return min(idx_range(rows, a, b), key=lambda i: rows[i][3])


def argmax_high(rows, a, b):
    return max(idx_range(rows, a, b), key=lambda i: rows[i][2])


def vol_x(rows, i, n):
    base = sum(r[5] for r in rows[i - n:i]) / n
    return rows[i][5] / base if i >= n and base else None


def ema_own(x, n):
    a = 2 / (n + 1)
    out = [x[0]]
    for v in x[1:]:
        out.append(out[-1] + a * (v - out[-1]))
    return out


def rsi_own(c, n=14):
    out = [None] * len(c)
    g = [max(c[i] - c[i - 1], 0) for i in range(1, len(c))]
    l_ = [max(c[i - 1] - c[i], 0) for i in range(1, len(c))]
    ag, al = sum(g[:n]) / n, sum(l_[:n]) / n
    for i in range(n, len(c)):
        if i > n:
            ag = (ag * (n - 1) + g[i - 1]) / n
            al = (al * (n - 1) + l_[i - 1]) / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def macd_down_after(c, i, within):
    m = [a - b for a, b in zip(ema_own(c, 12), ema_own(c, 26))]
    s = ema_own(m, 9)
    for t in range(i + 1, min(i + within + 1, len(c))):
        if m[t - 1] >= s[t - 1] and m[t] < s[t]:
            return t
    return None


def star_raw(r):
    o, h, l, c = r[1], r[2], r[3], r[4]
    body, rng = abs(c - o), h - l
    return rng > 0 and (h - max(o, c)) >= 2 * body and max(o, c) <= l + rng / 3


class Series:
    def __init__(self, name, rows):
        self.name, self.rows = name, rows
        self.o, self.h, self.l, self.c, self.v = ([r[k] for r in rows] for k in (1, 2, 3, 4, 5))
        self.events = ke.build_events(self.o, self.h, self.l, self.c, self.v, enabled=True)
        self.p = kc.load_params()

    def match(self, setups, side):
        return sorted(e["i"] for e in self.events if e["setup"] in setups and (side is None or e["side"] == side))

    def baseline(self, setups, side):
        ev = self.match(setups, side)
        n = len(self.rows)
        return sum(1 for t in range(n) if any(abs(i - t) <= WIN for i in ev)) / n

    def hit(self, target, setups, side):
        near = [i - target for i in self.match(setups, side) if abs(i - target) <= WIN]
        return (min(near, key=abs) if near else None), self.baseline(setups, side)


def row(eid, ids, cite, verdict, evidence, hit, extra=""):
    return dict(id=eid, rule=ids, cite=cite, verdict=verdict, evidence=evidence, hit=hit, extra=extra)


def kl(series_file, rows, i):
    r = rows[i]
    return (f"{series_file} open_time_ms={r[0]} ({day(r[0])}) O={r[1]:g} H={r[2]:g} L={r[3]:g} C={r[4]:g} V={r[5]:.0f}")


def cb_weekly():
    return weekly_bars(load("COINBASE_BTC-USD_1d.csv"))


def main():
    if "--prereg" in sys.argv:
        (RES / "RECALL_PREREG.md").write_text(PREREG, encoding="utf-8", newline="\n")
        print("wrote RECALL_PREREG.md")
        return
    d1 = Series("BTCUSDT 1d", load("BTCUSDT_1d.csv"))
    w1 = Series("BTCUSDT 1w_from_1d", load("BTCUSDT_1w_from_1d.csv"))
    cw = Series("COINBASE BTC-USD 1w_from_1d", cb_weekly())
    F1, FW, FC = "BTCUSDT_1d.csv", "BTCUSDT_1w_from_1d.csv", "COINBASE_BTC-USD_1d.csv(weekly)"
    LONG_ANY = ke.SETUPS[:8]
    out = []

    def fmt(h):
        return "NO DETECTOR" if h == "none" else ("MISS" if h[0] is None else f"HIT offset {h[0]:+d}")

    # R01 VOL-13
    i = argmin_low(w1.rows, "2020-02-17", "2020-04-13")
    vx = vol_x(w1.rows, i, 20)
    ok = vx is not None and vx >= 2.5
    h = w1.hit(i, LONG_ANY, "long") if ok else None
    out.append(row("R01", "VOL-13", "extract_UqAvU1loT_k.md:120-130", "VERIFIED" if ok else "NOT VERIFIED",
                   f"{kl(FW, w1.rows, i)}; vol/mean20 = {vx:.2f}x (rule >= 2.5x)", h, "any long S1-S8, 1w"))
    # R03 TRL-20
    a = argmin_low(w1.rows, "2018-12-01", "2018-12-31")
    b = argmin_low(w1.rows, "2020-02-17", "2020-04-13")
    va = vol_x(w1.rows, a, 20)
    ok = w1.rows[b][3] > w1.rows[a][3] and va is not None and va >= 2
    out.append(row("R03", "TRL-20", "extract_14bxwxC8gBQ.md:183-192", "VERIFIED (two facts only)" if ok else "NOT VERIFIED",
                   f"Dec 2018 {kl(FW, w1.rows, a)}; vol {va:.2f}x; Mar 2020 low {w1.rows[b][3]:g} ({day(w1.rows[b][0])})",
                   "none" if ok else None, "no trend-line detector in v0"))
    # R04 RNG-05
    idx = idx_range(d1.rows, "2018-02-15", "2018-11-13")
    cl = [d1.rows[k][4] for k in idx]
    ratio = max(cl) / min(cl)
    ok = ratio <= 2.0
    rs = [kc.range_state(d1.h, d1.l, d1.c, k, d1.p) for k in idx]
    frac = sum(1 for x in rs if x) / len(idx)
    s34 = sum(1 for e in d1.events if e["setup"] in ("S3", "S4") and idx[0] <= e["i"] <= idx[-1])
    out.append(row("R04", "RNG-05", "extract_6aA-P4Gvhrc.md:50-57", "VERIFIED" if ok else "NOT VERIFIED",
                   f"{FILE_SPAN(FILE=F1, rows=d1.rows, idx=idx)}; max/min close = {ratio:.2f} (rule <= 2.0)",
                   ("RANGE" if frac >= 0.5 else None) if ok else None,
                   f"range_state on {frac:.0%} of {len(idx)} days (rule >= 50%); S3+S4 events in span: {s34}"))
    # R06 a-d
    sma200 = kc.sma(cw.c, 200)
    for eid, yr, lo, hi in (("R06a", 2015, None, None), ("R06b", 2018, None, None),
                            ("R06c", 2020, "2020-02-17", "2020-04-13"), ("R06d", 2022, "2022-05-01", "2022-12-31")):
        if lo is None:
            out.append(row(eid, "MAV-16", "extract_-NXzJs5JRks.md:157-165", "NOT_IN_DATA",
                           f"{yr} cycle low precedes the first Coinbase week with a 200-week SMA "
                           f"({day(cw.rows[199][0])}); Binance starts 2017-08", None, ""))
            continue
        k = argmin_low(cw.rows, lo, hi)
        ratio = cw.rows[k][3] / sma200[k]
        ok = abs(ratio - 1) <= 0.15
        out.append(row(eid, "MAV-16", "extract_-NXzJs5JRks.md:157-165", "VERIFIED" if ok else "NOT VERIFIED",
                       f"{kl(FC, cw.rows, k)}; SMA200w = {sma200[k]:.0f}; low/SMA200w = {ratio:.2f} (rule within 0.85..1.15)",
                       "none" if ok else None, "no weekly SMA200 touch detector in v0"))
    # R07 MAV-21
    sma50, sma200d = kc.sma(d1.c, 50), kc.sma(d1.c, 200)
    cr = kc.crosses(sma50, sma200d)
    win = idx_range(d1.rows, "2021-12-15", "2022-02-15")
    k = next((t for t in win if cr[t] == "down"), None)
    ok = k is not None and sma200d[k] < sma200d[k - 30]
    h = d1.hit(k, ("S5",), "short") if ok else None
    out.append(row("R07", "MAV-21", "extract_-NXzJs5JRks.md:197-213", "VERIFIED" if ok else "NOT VERIFIED",
                   (f"{kl(F1, d1.rows, k)}; SMA50 {sma50[k]:.0f} < SMA200 {sma200d[k]:.0f}; SMA200 30d earlier "
                    f"{sma200d[k - 30]:.0f}") if k is not None else "no 50/200 down-cross in 2021-12-15..2022-02-15", h,
                   "S5 short, 1d"))
    # R09 TOP-12 (Coinbase weekly)
    i = argmax_high(cw.rows, "2017-09-01", "2018-03-31")
    bw = kc.bbwp(cw.c, cw.p["bbwp_basis"], cw.p["bbwp_lookback"], cw.p["bbwp_mult"])
    wk = [t for t in idx_range(cw.rows, "2017-05-01", day(cw.rows[i][0])) if bw[t] is not None and bw[t] >= 85]
    vx = vol_x(cw.rows, i, 30)
    r14 = rsi_own(cw.c)
    prior = range(i - 12, i)
    div = r14[i] < max(r14[t] for t in prior) and cw.h[i] > max(cw.h[t] for t in prior)
    mc = macd_down_after(cw.c, i, 8)
    conds = [day(cw.rows[i][0]).startswith("2017-12"), len(wk) >= 8, vx is not None and vx >= 2, div, mc is not None]
    ok = all(conds)
    h = cw.hit(i, ("S9",), "short") if ok else None
    out.append(row("R09", "TOP-12", "extract_7IxfsuD2wCM.md:126-136", "VERIFIED" if ok else "NOT VERIFIED",
                   f"{kl(FC, cw.rows, i)}; conditions a-e = {conds}; BBWP>=85 weeks {len(wk)}; vol/mean30 "
                   f"{vx if vx is None else round(vx, 2)}; RSI {r14[i]:.1f} vs prior-12 max {max(r14[t] for t in prior):.1f}; "
                   f"MACD down-cross {day(cw.rows[mc][0]) if mc else 'none'}", h, "S9 short, 1w, Coinbase weekly"))
    # R10 TOP-32
    i = argmax_high(w1.rows, "2021-10-01", "2021-12-31")
    j = argmax_high(w1.rows, "2021-03-01", "2021-05-31")
    r14 = rsi_own(w1.c)
    conds = [r14[i] < r14[j] and w1.h[i] > w1.h[j], star_raw(w1.rows[i]) or star_raw(w1.rows[i - 1]),
             macd_down_after(w1.c, i, 8) is not None]
    ok = all(conds)
    h = w1.hit(i, ("S9",), "short") if ok else None
    out.append(row("R10", "TOP-32", "extract_7IxfsuD2wCM.md:343-350", "VERIFIED" if ok else "NOT VERIFIED",
                   f"{kl(FW, w1.rows, i)}; Apr-2021 high week {day(w1.rows[j][0])} H={w1.h[j]:g}; RSI {r14[i]:.1f} vs "
                   f"{r14[j]:.1f}; conditions a-c = {conds}", h, "S9 short, 1w"))
    # R12 VJZ-50
    low = argmin_low(w1.rows, "2018-11-01", "2019-01-31")
    e55 = ema_own(w1.c, 55)
    T = next((t for t in range(low + 1, len(w1.c)) if w1.c[t] > e55[t]), None)
    hi = max(w1.h[T + 1:T + 27]) if T is not None else None
    ok = T is not None and 3000 <= w1.c[T] <= 5000 and 12600 <= hi <= 15400
    h = w1.hit(T, ("S2", "S5"), "long") if ok else None
    out.append(row("R12", "VJZ-50", "extract_vjzy_KxJ_y8.md:458-476", "VERIFIED" if ok else "NOT VERIFIED",
                   (f"low week {day(w1.rows[low][0])} L={w1.l[low]:g}; reclaim {kl(FW, w1.rows, T)}; EMA55w {e55[T]:.0f}; "
                    f"max high next 26 weeks {hi:g}") if T is not None else "no reclaim", h, "S2/S5 long, 1w"))
    # R13 VJZ-49
    k = argmin_low(d1.rows, "2024-01-01", "2024-02-10")
    nxt = d1.h[k + 1:k + 31]
    hi = max(nxt)
    ok = 38000 <= d1.l[k] <= 42000 and 50500 <= hi <= 53500
    h = None
    if ok:
        end = next(t for t in range(k + 1, k + 31) if d1.h[t] >= 50500)
        near = [i - k for i in d1.match(("S2", "S5", "S8"), "long") if k <= i <= end]
        h = (near[0] if near else None, d1.baseline(("S2", "S5", "S8"), "long"))
    out.append(row("R13", "VJZ-49", "extract_vjzy_KxJ_y8.md:458-476", "VERIFIED" if ok else "NOT VERIFIED",
                   f"{kl(F1, d1.rows, k)}; max high next 30 days {hi:g}", h, "S2/S5/S8 long on any day low bar..first high >= 50,500 (window, not +-2)"))

    ver = [r for r in out if r["verdict"].startswith("VERIFIED")]
    hits = [r for r in ver if r["hit"] not in (None, "none") and (r["hit"][0] is not None if isinstance(r["hit"], tuple) else r["hit"] == "RANGE")]
    covered = [r for r in ver if r["hit"] != "none"]
    passed = len(hits) >= 6
    # fire rates
    fr = {}
    for s in (d1, w1, cw):
        fc = ke.fire_counts(s.events, len(s.rows))
        fr[s.name] = (len(s.rows), fc, ke.over_ceiling(fc, 1.0))
    L = [PREREG.replace("# Krown recall check: rules fixed before the run", "# Krown recall check: RESULT (rules fixed before the run)", 1), "",
         "---", "", "## Result", "",
         f"Examples listed {len(out)} (+5 dropped without a read). Verified: {len(ver)}. Recall hits within 2 bars: "
         f"**{len(hits)}** strict (of {len(ver)} verified), {len(hits)} of {len(covered)} covered (verified with a mapped v0 detector). "
         f"Bar: >= 6 strict. **RECALL {'PASS' if passed else 'FAIL'}**.", "",
         "| id | rule | extract cite | verdict | klines evidence | result | detector / note |", "|---|---|---|---|---|---|---|"]
    for r in out:
        h = r["hit"]
        if h == "none":
            res = "NO DETECTOR (miss)"
        elif h == "RANGE":
            res = "HIT (range_state coverage)"
        elif h is None:
            res = "n/a" if not r["verdict"].startswith("VERIFIED") else "MISS"
        else:
            res = (f"HIT offset {h[0]:+d}" if h[0] is not None else "MISS") + f" (chance baseline {h[1]:.0%})"
        L.append(f"| {r['id']} | {r['rule']} | `{r['cite']}` | {r['verdict']} | {r['evidence']} | {res} | {r['extra']} |")
    L += ["", "Dropped without a read: VOL-08 (HOLDOUT), SNR-17 (after 2024-07), MAV-11/MAV-15, VJZ-13, KCM-15 (no date or price); see rules above.", "",
          "## Fire rate (v0 detectors, DEV bars before 2024-07-01)", "",
          "| series | bars | " + " | ".join(ke.SETUPS) + " | over 1.0 per 10 bars |", "|---|---|" + "---|" * 10]
    for name, (n, fc, over) in fr.items():
        L.append(f"| {name} | {n} | " + " | ".join(f"{fc[s]['n']} ({fc[s]['per_10_bars']:.3f})" for s in ke.SETUPS)
                 + f" | {', '.join(over) if over else 'none'} |")
    L += ["", "Cells: events (per 10 bars). Ceiling applies to the Binance 1d row; weekly rows are for information.",
          f"**FIRE RATE {'PASS' if not fr['BTCUSDT 1d'][2] else 'FAIL: ' + ', '.join(fr['BTCUSDT 1d'][2])}** (Binance 1d pooled).", ""]
    (RES / "RECALL.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L))


def FILE_SPAN(FILE, rows, idx):
    return f"{FILE} open_time_ms {rows[idx[0]][0]} ({day(rows[idx[0]][0])}) .. {rows[idx[-1]][0]} ({day(rows[idx[-1]][0])})"


if __name__ == "__main__":
    main()
