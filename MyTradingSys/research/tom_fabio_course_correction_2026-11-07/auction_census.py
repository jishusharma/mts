"""Event census for classify_level_interaction (auction_context.py), card auction-context-event-census-1108.

Walk-forward, zero lookahead: at every bar t the classifier sees bars[t-59..t] only. Entry = close of bar t, outcome from bars t+1..t+H.
Levels per UTC day D (all from bars that closed before D): prior-day VAL/VAH (volume profile, spread_range), prior-day low/high,
prior-week (last full ISO week) low/high. Public market data only (Bybit linear BTCUSDT 5m; Binance spot BTCUSDT 1h/1d).

Parameter labels: SOURCED = taken from a cited file; OURS = chosen here, not a trader's number.
  fee round trip 10 bps taker   SOURCED fees.py via auction_context.DEFAULT_TAKER_RT_BPS
  fee_r gate <= 0.25 R          SOURCED d-stops-follow-trade-1106 / auction_context.DEFAULT_MAX_FRICTION_R
  rel_vol >= 2.0, knife 2%/25%, 6-bar acceptance, reclaim <= 3 bars   inside classify_level_interaction (labels in that file)
  WINDOW 60 bars, SETUP_BACK 12, COOLDOWN, H, rr=1, stop = sweep extreme (no buffer), accepted stop = level   OURS
  htf bias = prior-day close vs SMA20 of daily closes; regime band +-2% around SMA20   OURS
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import math
import statistics as st
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("auction_context", HERE / "auction_context.py")
ac = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ac)

RT_BPS = ac.DEFAULT_TAKER_RT_BPS
MAX_FEE_R = ac.DEFAULT_MAX_FEE_R if hasattr(ac, "DEFAULT_MAX_FEE_R") else ac.DEFAULT_MAX_FRICTION_R
WINDOW = 60
SETUP_BACK = 12
RR = 1.0
FIRING = ("FAST_REJECTION", "WEAK_REJECTION", "REJECTED_KNIFE_SKIP", "ACCEPTED", "STALE_REJECTION")


def simulate(direction, entry, stop, future, horizon, rt_bps=RT_BPS, rr=RR):
    """direction +1 long / -1 short. future = bars after entry (dicts h,l,c). Stop wins a same-bar tie.
    Returns dict(outcome, gross_r, fee_r, net_r) or None when the stop is not on the loss side."""
    dist = (entry - stop) * direction
    if dist <= 0.0 or entry <= 0.0:
        return None
    target = entry + direction * rr * dist
    fee_r = rt_bps / (dist / entry * 1e4)
    out, gross = "open", None
    seg = future[:horizon]
    for b in seg:
        hit_stop = b["l"] <= stop if direction > 0 else b["h"] >= stop
        hit_tgt = b["h"] >= target if direction > 0 else b["l"] <= target
        if hit_stop:
            out, gross = "stop", -1.0
            break
        if hit_tgt:
            out, gross = "target", rr
            break
    if gross is None:
        if not seg:
            return None
        gross = (seg[-1]["c"] - entry) * direction / dist
    return {"outcome": out, "gross_r": gross, "fee_r": fee_r, "net_r": gross - fee_r}


def day_of(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.UTC).date()


def build_levels(day_bars, day, bin_frac):
    """Levels for UTC `day` from bars strictly before it. day_bars: date -> list of bars. Returns [(name, price, side)] or []."""
    prev = day_bars.get(day - dt.timedelta(days=1), [])
    if len(prev) < 12:
        return []
    mon = day - dt.timedelta(days=day.weekday())
    wk = [b for k in range(1, 8) for b in day_bars.get(mon - dt.timedelta(days=k), [])]
    close = prev[-1]["c"]
    lv = []
    prof = ac.compute_volume_profile(prev, bin_size=max(1.0, round(close * bin_frac)), spread_range=True)
    if prof:
        lv += [("VAL", float(prof["val"]), "support"), ("VAH", float(prof["vah"]), "resistance")]
    lv += [("PDL", min(b["l"] for b in prev), "support"), ("PDH", max(b["h"] for b in prev), "resistance")]
    if len(wk) >= 12:
        lv += [("PWL", min(b["l"] for b in wk), "support"), ("PWH", max(b["h"] for b in wk), "resistance")]
    return lv


def daily_bias(daily):
    """date -> (bias, regime) from the prior day's close vs SMA20 of the 20 closes up to and including it."""
    out = {}
    closes = [d["c"] for d in daily]
    for i, d in enumerate(daily):
        if i < 19:
            continue
        sma = sum(closes[i - 19:i + 1]) / 20.0
        c = closes[i]
        bias = "bull" if c > sma else "bear"
        regime = "bull" if c > sma * 1.02 else "bear" if c < sma * 0.98 else "range"
        out[day_of(d["t"]) + dt.timedelta(days=1)] = (bias, regime)  # known at the start of the next day
    return out


def run_census(bars, start_day, end_day, horizon, cooldown, bias_map, bin_frac):
    """Return list of event dicts. bars sorted by t (ms), keys t,o,h,l,c,v."""
    events = []
    by_day, day_bars = {}, {}
    for i, b in enumerate(bars):
        by_day.setdefault(day_of(b["t"]), []).append(i)
        day_bars.setdefault(day_of(b["t"]), []).append(b)
    day = start_day
    while day <= end_day:
        idxs = by_day.get(day)
        lv = build_levels(day_bars, day, bin_frac) if idxs else []
        last_fire = {name: -10 ** 9 for name, _, _ in lv}
        for t in (idxs or []):
            if t < WINDOW:
                continue
            win = bars[t - WINDOW + 1:t + 1]
            for name, price, side in lv:
                if t - last_fire[name] < cooldown:
                    continue
                inside_ref = win[-1 - SETUP_BACK]["c"]
                if (side == "support" and inside_ref <= price) or (side == "resistance" and inside_ref >= price):
                    continue  # approach must start from the inside of the level
                r = ac.classify_level_interaction(win, price, side)
                v = r.get("verdict")
                if v not in FIRING:
                    continue
                last_fire[name] = t
                fut = bars[t + 1:t + 1 + horizon]
                entry = bars[t]["c"]
                ev = {"t": bars[t]["t"], "day": day.isoformat(), "level": name, "side": side, "verdict": v,
                      "bias": bias_map.get(day, ("n/a", "n/a"))[0], "regime": bias_map.get(day, ("n/a", "n/a"))[1],
                      "knife": bool(r.get("knife")), "bias_trade": r.get("trade_bias"), "sim": None, "dir": 0}
                if v == "ACCEPTED" and r["trade_bias"] == "continuation":
                    d = -1 if side == "support" else 1
                    ev["dir"], ev["sim"] = d, simulate(d, entry, price, fut, horizon)
                elif v == "ACCEPTED":
                    ev["verdict"] = "ACCEPTED_HOLD"
                elif v in ("FAST_REJECTION", "WEAK_REJECTION", "REJECTED_KNIFE_SKIP"):
                    d = 1 if side == "support" else -1
                    ev["dir"], ev["sim"] = d, simulate(d, entry, r["sweep_extreme"], fut, horizon)
                if ev["dir"]:
                    b_ = ev["bias"]
                    ev["align"] = "with" if (ev["dir"] > 0 and b_ == "bull") or (ev["dir"] < 0 and b_ == "bear") else "against"
                else:
                    ev["align"] = "n/a"
                events.append(ev)
        day += dt.timedelta(days=1)
    return events


def stats(evs):
    """Parsed counts and fee-net R for a list of events (sim not None)."""
    sims = [e["sim"] for e in evs if e["sim"]]
    n = len(sims)
    if not n:
        return dict(n=0)
    gate = [s for s in sims if s["fee_r"] <= MAX_FEE_R]

    def agg(x):
        if not x:
            return dict(n=0)
        nets = [s["net_r"] for s in x]
        return dict(n=len(x), tgt=sum(s["outcome"] == "target" for s in x), stp=sum(s["outcome"] == "stop" for s in x),
                    opn=sum(s["outcome"] == "open" for s in x), gross=st.mean(s["gross_r"] for s in x),
                    fee=st.mean(s["fee_r"] for s in x), net=st.mean(nets),
                    se=(st.stdev(nets) / math.sqrt(len(nets))) if len(nets) > 1 else float("nan"))
    return dict(n=n, all=agg(sims), gate=agg(gate))


def _row(label, evs):
    s = stats(evs)
    if not s["n"]:
        return f"| {label} | {len(evs)} | 0 | - | - | - | - | - | - | - |"
    a, g = s["all"], s["gate"]
    gs = f"{g['n']} ({g['tgt']}/{g['stp']}/{g['opn']})" if g["n"] else "0"
    return (f"| {label} | {len(evs)} | {s['n']} | {a['tgt']}/{a['stp']}/{a['opn']} | {a['gross']:+.3f} | {a['fee']:.3f} | {a['net']:+.3f} +-{a['se']:.3f} "
            f"| {gs} | {(g['net'] if g['n'] else float('nan')):+.3f} | {(g['se'] if g['n'] else float('nan')):.3f} |")


HDR = ("| {k} | events | simulated | tgt/stop/open (all) | gross R | fee R | net R +-SE (all) | gate-pass n (tgt/stp/open) | net R (gate-pass) | SE |\n"
       "|---|---|---|---|---|---|---|---|---|---|")


def tables(events, title):
    out = [f"### {title}", ""]
    vs = ["FAST_REJECTION", "WEAK_REJECTION", "REJECTED_KNIFE_SKIP", "ACCEPTED", "ACCEPTED_HOLD", "STALE_REJECTION"]
    out += ["Events by verdict x level (parsed from the event list):", "", "| verdict | " + " | ".join(["VAL", "VAH", "PDL", "PDH", "PWL", "PWH"]) + " | total |", "|---|---|---|---|---|---|---|---|"]
    for v in vs:
        row = [sum(1 for e in events if e["verdict"] == v and e["level"] == lv) for lv in ("VAL", "VAH", "PDL", "PDH", "PWL", "PWH")]
        out.append(f"| {v} | " + " | ".join(map(str, row)) + f" | {sum(row)} |")
    out += ["", "Forward result by verdict (FAST/WEAK/KNIFE = fade the sweep; ACCEPTED = continuation, stop at the level; KNIFE is the counterfactual of the skipped fade):", "", HDR.format(k="verdict")]
    for v in vs[:4]:
        out.append(_row(v, [e for e in events if e["verdict"] == v]))
    out += ["", "By level family (VA edges vs prior-day extremes vs prior-week extremes):", "", HDR.format(k="verdict / family")]
    fam = {"VA": ("VAL", "VAH"), "PD": ("PDL", "PDH"), "PW": ("PWL", "PWH")}
    for v in vs[:4]:
        for f, names in fam.items():
            out.append(_row(f"{v} / {f}", [e for e in events if e["verdict"] == v and e["level"] in names]))
    out += ["", "By htf bias alignment of the trade (with = long in bull / short in bear; bias = prior-day close vs SMA20, OURS):", "", HDR.format(k="verdict / align")]
    for v in vs[:4]:
        for a in ("with", "against"):
            out.append(_row(f"{v} / {a}", [e for e in events if e["verdict"] == v and e["align"] == a]))
    days = sorted({e["day"] for e in events})
    out += ["", f"Event days with at least one event: {len(days)}. Events by regime (bull/bear/range on the event day): "
            + ", ".join(f"{r}={sum(1 for e in events if e['regime'] == r)}" for r in ("bull", "bear", "range", "n/a")) + "."]
    return "\n".join(out)


# ---------------------------------------------------------------- public data
def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mts-census"})
    for _ in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            import time
            time.sleep(2)
    raise RuntimeError("fetch failed " + url)


def fetch_bybit_5m(start_ms, end_ms):
    out, end = {}, end_ms
    while True:
        r = _get(f"https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=5&start={start_ms}&end={end}&limit=1000")["result"]["list"]
        if not r:
            break
        for k in r:
            out[int(k[0])] = dict(t=int(k[0]), o=float(k[1]), h=float(k[2]), l=float(k[3]), c=float(k[4]), v=float(k[5]))
        oldest = min(int(k[0]) for k in r)
        if oldest <= start_ms:
            break
        end = oldest - 1
    return [out[k] for k in sorted(out)]


def fetch_binance(interval, start_ms, end_ms):
    out, cur = [], start_ms
    while cur < end_ms:
        r = _get(f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={interval}&startTime={cur}&endTime={end_ms}&limit=1000")
        if not r:
            break
        out += [dict(t=int(k[0]), o=float(k[1]), h=float(k[2]), l=float(k[3]), c=float(k[4]), v=float(k[5])) for k in r]
        cur = int(r[-1][0]) + 1
        if len(r) < 1000:
            break
    return out


def cached(path, fn):
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text())
    data = fn()
    p.write_text(json.dumps(data))
    return data


def ms(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.UTC).timestamp() * 1000)


def main(cache):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    end7 = ms(2026, 11, 8)
    daily = cached(cache / "binance_1d.json", lambda: fetch_binance("1d", ms(2019, 6, 1), end7))
    bias = daily_bias(daily)
    # --- 5m window (matches CENSUS_5m: 2026-10-03 00:00 UTC, 10233 bars)
    s5 = ms(2026, 10, 3)
    b5_all = cached(cache / "bybit_5m.json", lambda: fetch_bybit_5m(ms(2026, 9, 20), end7))
    census_bars = [b for b in b5_all if b["t"] >= s5][:10233]
    last_t = census_bars[-1]["t"]
    b5 = [b for b in b5_all if b["t"] <= last_t]
    print(f"# bars: bybit 5m fetched {len(b5_all)} from 2026-09-20; census window bars {len(census_bars)} "
          f"{dt.datetime.fromtimestamp(census_bars[0]['t']/1000, dt.UTC):%Y-%m-%d %H:%M} .. {dt.datetime.fromtimestamp(last_t/1000, dt.UTC):%Y-%m-%d %H:%M} UTC")
    ev5 = run_census(b5, dt.date(2026, 10, 3), day_of(last_t), horizon=24, cooldown=48, bias_map=bias, bin_frac=50 / 75000)
    json.dump(ev5, open(cache / "events_5m.json", "w"))
    print(tables(ev5, "A. 5m window 2026-10-03..11-07 (Bybit linear BTCUSDT)"))
    days5 = [d for d in sorted(bias) if dt.date(2026, 10, 3) <= d <= day_of(last_t)]
    print("\nRegime mix (window days, prior-day close vs SMA20 +-2%, OURS): "
          + " / ".join(f"{r} {sum(1 for d in days5 if bias[d][1] == r)}/{len(days5)}" for r in ("bull", "bear", "range")))
    # --- 7y 1h
    s7 = ms(2019, 11, 8)
    b1 = cached(cache / "binance_1h.json", lambda: fetch_binance("1h", ms(2019, 10, 20), end7))
    print(f"\n# bars: binance 1h {len(b1)} from {dt.datetime.fromtimestamp(b1[0]['t']/1000, dt.UTC):%Y-%m-%d}")
    ev7 = run_census(b1, day_of(s7), dt.date(2026, 11, 7), horizon=24, cooldown=12, bias_map=bias, bin_frac=50 / 75000)
    json.dump(ev7, open(cache / "events_1h.json", "w"))
    print("\n" + tables(ev7, "B. 7y 1h (Binance spot BTCUSDT 2019-11-08..2026-11-07)"))
    days7 = [d for d in sorted(bias) if day_of(s7) <= d <= dt.date(2026, 11, 7)]
    print("\nRegime mix (7y days, same rule, OURS): "
          + " / ".join(f"{r} {sum(1 for d in days7 if bias[d][1] == r)}/{len(days7)}" for r in ("bull", "bear", "range")))
    # per-year FAST_REJECTION net R (stability)
    print("\nPer-year FAST_REJECTION (gate-pass) net R, 7y 1h:\n\n| year | n gate-pass | net R |\n|---|---|---|")
    for y in range(2019, 2027):
        g = [e for e in ev7 if e["verdict"] == "FAST_REJECTION" and e["sim"] and e["sim"]["fee_r"] <= MAX_FEE_R and e["day"].startswith(str(y))]
        print(f"| {y} | {len(g)} | {(st.mean(e['sim']['net_r'] for e in g) if g else float('nan')):+.3f} |")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "census_cache")
