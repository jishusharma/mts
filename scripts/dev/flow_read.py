"""Live BTC order-flow read on BINANCE FUTURES data, fetched through MyTradingSys/runtime/binance_doh (DNS block fix).

Public market data only; no orders, no sizes. Context, not a signal.
  python scripts/dev/flow_read.py --since 9h --tf 15m [--last 12] [--thresholds] [--symbol BTCUSDT]
Per bar: OHLC, perp volume x median, perp taker delta (kline field 9), spot delta (data-api.binance.vision),
OI change over the bar, top-trader long/short position ratio, label, absorption mark.
Labels (price direction x OI change; OURS): up+OI up = NEW LONGS, up+OI down = SHORT COVER,
down+OI down = LONGS EXIT, down+OI up = NEW SHORTS, |OI change| < OI_FLAT of OI = flat.
Absorption (OURS): ABSORB-BUY = heavy aggressive perp selling (delta/vol <= -ABS_RATIO, volume >= 1x median) and the low
holds (next bar low >= this low; last bar: close in upper 60%); ABSORB-SELL is the mirror at the high.
--thresholds: the three live checks from the Opus bottom study (research bottom_signatures.md, 4h basis).
Fetch failures exit non-zero and print which endpoint failed (fail closed, never a silent Bybit fallback)."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from MyTradingSys.runtime import binance_doh as bd  # noqa: E402

FAPI = "https://fapi.binance.com"
SPOT = "https://data-api.binance.vision"
TF_MS = {"5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000}
OI_FLAT = 0.0002        # OURS: |OI change| under 0.02% of OI counts as flat
ABS_RATIO = 0.08        # OURS: |perp taker delta| / volume at/above this = heavy aggressive side
ABS_CLOSE_POS = 0.6     # OURS: last (unconfirmed) bar: close in the upper 60% of range = the low held
# Thresholds from bottom_signatures.md (4h basis, Opus study 2026-11-12; the numbers are SOURCED from that study)
TH_OI_PCT = -5.0        # OI change from bar -3 to bar +1 around the low, percent
TH_TAKER_PCT = 3.0      # spot taker buy - sell as % of volume on the low bar
TH_SPOT_12H = 670.0     # BTC spot delta in the 12 h after the low bar


def parse_dur(s: str) -> int:
    m = re.fullmatch(r"(\d+)([mhd])", s.strip())
    if not m:
        raise ValueError(f"bad duration {s!r} (use 90m, 9h, 2d)")
    return int(m.group(1)) * {"m": 60_000, "h": 3_600_000, "d": 86_400_000}[m.group(2)]


def http_json(url: str, tries: int = 3):
    err = None
    for i in range(tries):
        try:
            with bd.urlopen(url, timeout=20) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(1 + i)
    raise RuntimeError(f"fetch failed {url.split('?')[0]}: {type(err).__name__}: {err}")


def paged(fetch, base: str, start: int, end: int, limit: int, key=None):
    """Page forward from start until a short page; key(row) -> row timestamp ms."""
    key = key or (lambda r: r[0])
    out, s = [], start
    while s < end:
        rows = fetch(f"{base}&startTime={s}&endTime={end}&limit={limit}")
        if not isinstance(rows, list) or not rows:
            break
        out += rows
        if len(rows) < limit:
            break
        s = key(rows[-1]) + 1
    return out


# ---------------------------------------------------------------- pure functions (fixture-tested)
def kl(rows):
    """Binance kline rows -> {open_ms: dict}. delta = taker buy - taker sell in base units (field 9 = taker buy base)."""
    out = {}
    for x in rows:
        v, tb = float(x[5]), float(x[9])
        out[int(x[0])] = {"o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4]), "v": v,
                          "delta": 2 * tb - v, "close_ms": int(x[6])}
    return out


def hist(rows, field):
    return {int(r["timestamp"]): float(r[field]) for r in rows}


def median(xs):
    s = sorted(xs)
    return s[len(s) // 2] if s else 0.0


def label(price_chg: float, oi_chg, oi_ref, flat=OI_FLAT) -> str:
    if oi_chg is None or not oi_ref:
        return "n/a"
    if abs(oi_chg) < flat * oi_ref or price_chg == 0:
        return "flat"
    up = price_chg > 0
    if up:
        return "NEW LONGS" if oi_chg > 0 else "SHORT COVER"
    return "NEW SHORTS" if oi_chg > 0 else "LONGS EXIT"


def absorb(bar: dict, nxt, volx: float) -> str:
    v = bar["v"]
    if not v or volx < 1.0:
        return ""
    r = bar["delta"] / v
    rng = bar["h"] - bar["l"]
    pos = (bar["c"] - bar["l"]) / rng if rng else 0.5
    if r <= -ABS_RATIO:  # heavy aggressive selling: did the low hold?
        held = nxt["l"] >= bar["l"] if nxt else pos >= ABS_CLOSE_POS
        return "ABSORB-BUY" if held else ""
    if r >= ABS_RATIO:   # heavy aggressive buying: did the high hold?
        held = nxt["h"] <= bar["h"] if nxt else pos <= 1 - ABS_CLOSE_POS
        return "ABSORB-SELL" if held else ""
    return ""


def build_rows(perp: dict, spot: dict, oi: dict, topr: dict, globr: dict, takr: dict, tf_ms: int, since_ms: int,
               flat=OI_FLAT):
    """One dict per bar with open_ms >= since_ms. Median volume uses every perp bar fetched (incl. the warm-up bars)."""
    med = median([b["v"] for b in perp.values()])
    keys = sorted(perp)
    rows = []
    for i, t in enumerate(keys):
        if t < since_ms:
            continue
        b = perp[t]
        o_a, o_b = oi.get(t), oi.get(t + tf_ms)
        oi_chg = (o_b - o_a) if o_a is not None and o_b is not None else None
        volx = b["v"] / med if med else 0.0
        nxt = perp[keys[i + 1]] if i + 1 < len(keys) else None
        sp = spot.get(t)
        rows.append({
            "t": t, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "volx": volx, "delta": b["delta"],
            "spot_delta": sp["delta"] if sp else None, "oi_chg": oi_chg, "oi": o_a,
            "top": topr.get(t), "glob": globr.get(t), "tkr": takr.get(t),
            "label": label(b["c"] - b["o"], oi_chg, o_a, flat),
            "absorb": absorb(b, nxt, volx),
        })
    return rows


def thresholds(perp4: dict, spot4: dict, oi4: dict, spot_fine: dict, now_ms: int, low_window_ms: int):
    """Three live checks, 4h basis. Low bar = the 4h bar with the lowest low inside low_window_ms (perp).
    Returns a list of (name, status, detail); status in MET / MISSED / PENDING. MET can be provisional while PENDING
    data is still arriving (detail says 'so far')."""
    H4 = TF_MS["4h"]
    keys = sorted(perp4)
    cand = [t for t in keys if t >= now_ms - low_window_ms]
    if not cand:
        return [("low bar", "PENDING", "no 4h bars in window")]
    lo = min(cand, key=lambda t: perp4[t]["l"])
    lo_close = lo + H4
    head = f"low bar {fmt_t(lo)}Z low {perp4[lo]['l']:.0f}" + (" (forming)" if lo_close > now_ms else "")
    res = [("low bar", "INFO", head)]
    # 1. OI change from bar -3 (open stamp) to the close of bar +1 (= open stamp of bar +2)
    a, b_stamp = lo - 3 * H4, lo + 2 * H4
    oa = oi4.get(a)
    ob = oi4.get(b_stamp)
    last_ts = max(oi4) if oi4 else None
    used = b_stamp
    if ob is None and last_ts is not None and last_ts > lo:
        ob, used = oi4[last_ts], last_ts
    if oa is None or ob is None:
        res.append(("OI -5% into low", "PENDING", "OI history missing for the window"))
    else:
        pct = (ob / oa - 1) * 100
        complete = used == b_stamp
        st = "MET" if pct <= TH_OI_PCT else ("MISSED" if complete else "PENDING")
        res.append(("OI -5% into low", st, f"{pct:+.2f}% ({oa:,.0f} -> {ob:,.0f} BTC at {fmt_t(used)}Z)"
                    + ("" if complete else " so far")))
    # 2. spot taker buy - sell > 3% of volume on the low bar
    sb = spot4.get(lo)
    if sb is None or not sb["v"]:
        res.append(("taker buy>sell 3% on low bar", "PENDING", "no spot bar"))
    else:
        r = sb["delta"] / sb["v"] * 100
        pr = perp4[lo]
        pr_r = pr["delta"] / pr["v"] * 100 if pr["v"] else 0.0
        done = lo_close <= now_ms
        st = "MET" if r > TH_TAKER_PCT else ("MISSED" if done else "PENDING")
        res.append(("taker buy>sell 3% on low bar", st,
                    f"spot {r:+.2f}% of vol ({sb['delta']:+.0f} BTC), perp {pr_r:+.2f}%" + ("" if done else " so far")))
    # 3. spot delta >= +670 BTC in the 12 h after the low bar (summed from fine spot bars)
    end12 = lo_close + 12 * 3_600_000
    tot = sum(b["delta"] for t, b in spot_fine.items() if lo_close <= t < end12)
    if lo_close > now_ms:
        res.append(("spot delta >= +670 BTC in 12h after", "PENDING", "low bar still forming"))
    else:
        el = min(now_ms, end12) - lo_close
        st = "MET" if tot >= TH_SPOT_12H else ("MISSED" if now_ms >= end12 else "PENDING")
        res.append(("spot delta >= +670 BTC in 12h after", st,
                    f"{tot:+.0f} BTC after {el / 3_600_000:.1f}h of 12h"))
    return res


def fmt_t(ms: int) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%m-%d %H:%M")


def f(x, spec, dash="   -"):
    return dash if x is None else format(x, spec)


def render(rows, last=None) -> str:
    if last:
        rows = rows[-last:]
    hdr = ("UTC          open    high    low     close   volx  perpDelta  spotDelta  OIchg  topL/S globL/S  label        absorb")
    out = [hdr]
    for r in rows:
        out.append(f"{fmt_t(r['t'])}  {r['o']:7.0f} {r['h']:7.0f} {r['l']:7.0f} {r['c']:7.0f} {r['volx']:5.1f}"
                   f" {r['delta']:+9.0f}  {f(r['spot_delta'], '+9.0f', '        -')} {f(r['oi_chg'], '+6.0f', '     -')}"
                   f"  {f(r['top'], '5.2f', '    -')}  {f(r['glob'], '5.2f', '    -')}  {r['label']:<12} {r['absorb']}")
    return "\n".join(out)


# ---------------------------------------------------------------- live fetch
def fetch_all(sym, tf, since_ms, now_ms, fetch=http_json):
    ms = TF_MS[tf]
    warm = since_ms - 30 * ms
    q = f"symbol={sym}"
    perp = kl(paged(fetch, f"{FAPI}/fapi/v1/klines?{q}&interval={tf}", warm, now_ms, 1500))
    spot = kl(paged(fetch, f"{SPOT}/api/v3/klines?symbol={sym}&interval={tf}", warm, now_ms, 1000))
    hp = f"symbol={sym}&period={tf}"
    oi = hist(paged(fetch, f"{FAPI}/futures/data/openInterestHist?{hp}", since_ms - ms, now_ms, 500,
                    lambda r: int(r["timestamp"])), "sumOpenInterest")
    top = hist(paged(fetch, f"{FAPI}/futures/data/topLongShortPositionRatio?{hp}", since_ms - ms, now_ms, 500,
                     lambda r: int(r["timestamp"])), "longShortRatio")
    glob = hist(paged(fetch, f"{FAPI}/futures/data/globalLongShortAccountRatio?{hp}", since_ms - ms, now_ms, 500,
                      lambda r: int(r["timestamp"])), "longShortRatio")
    tak = hist(paged(fetch, f"{FAPI}/futures/data/takerlongshortRatio?{hp}", since_ms - ms, now_ms, 500,
                     lambda r: int(r["timestamp"])), "buySellRatio")
    fund = fetch(f"{FAPI}/fapi/v1/fundingRate?symbol={sym}&limit=4")
    return perp, spot, oi, top, glob, tak, fund


def fetch_thresholds(sym, now_ms, low_window_ms, fetch=http_json):
    H4 = TF_MS["4h"]
    start = now_ms - low_window_ms - 4 * H4
    perp4 = kl(paged(fetch, f"{FAPI}/fapi/v1/klines?symbol={sym}&interval=4h", start, now_ms, 1500))
    spot4 = kl(paged(fetch, f"{SPOT}/api/v3/klines?symbol={sym}&interval=4h", start, now_ms, 1000))
    oi4 = hist(paged(fetch, f"{FAPI}/futures/data/openInterestHist?symbol={sym}&period=4h", start, now_ms, 500,
                     lambda r: int(r["timestamp"])), "sumOpenInterest")
    spot_fine = kl(paged(fetch, f"{SPOT}/api/v3/klines?symbol={sym}&interval=15m", start, now_ms, 1000))
    return perp4, spot4, oi4, spot_fine


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", default="9h")
    ap.add_argument("--tf", default="15m", choices=["5m", "15m", "1h"])
    ap.add_argument("--last", type=int, default=0, help="print only the last N bars")
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--thresholds", action="store_true", help="add the three bottom-study checks (4h basis)")
    ap.add_argument("--low-window", default="24h", help="window searched for the 4h low bar (default 24h)")
    a = ap.parse_args(argv)
    now = int(time.time() * 1000)
    since = now - parse_dur(a.since)
    try:
        perp, spot, oi, top, glob, tak, fund = fetch_all(a.symbol, a.tf, since, now)
        rows = build_rows(perp, spot, oi, top, glob, tak, TF_MS[a.tf], since)
        print(f"{a.symbol} Binance USD-M perp, tf {a.tf}, since {a.since}, source fapi via binance_doh, spot data-api.binance.vision")
        print(render(rows, a.last or None))
        done = [r for r in rows if r["spot_delta"] is not None]
        print(f"cum perp taker delta {sum(r['delta'] for r in rows):+.0f} BTC | cum spot delta {sum(r['spot_delta'] for r in done):+.0f} BTC"
              f" | OI change {sum(r['oi_chg'] for r in rows if r['oi_chg'] is not None):+.0f} BTC")
        if isinstance(fund, list) and fund:
            print("funding (last): " + ", ".join(f"{fmt_t(int(x['fundingTime']))}Z {float(x['fundingRate']) * 100:+.4f}%" for x in fund[-3:]))
        if a.thresholds:
            p4, s4, o4, sf = fetch_thresholds(a.symbol, now, parse_dur(a.low_window))
            print("\nTHRESHOLDS (bottom_signatures.md, 4h basis; context, not a signal)")
            for name, st, det in thresholds(p4, s4, o4, sf, now, parse_dur(a.low_window)):
                print(f"  {st:<8} {name:<36} {det}")
    except (RuntimeError, OSError) as e:
        print(f"FLOW_READ FAIL: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
