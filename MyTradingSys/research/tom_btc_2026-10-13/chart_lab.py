"""Blind, DEV-only chart sampler for Tom's BTC T2 review. All thresholds are OURS."""
from __future__ import annotations

import argparse
import csv
import gzip
import random
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "MyTradingSys" / "backtest" / "layers" / "fabio"))
from orderflow_bars import INT_COLS, parse_fp  # noqa: E402

DEV_START, DEV_END = date(2024, 12, 1), date(2025, 3, 31)
ANCHORS = ("00:00", "07:00", "US_CASH")
SEED = 20261013


def _value_area(rows):
    """70% volume value area, OURS: contiguous bins grown from POC, ties lower."""
    profile = defaultdict(float)
    for row in rows:
        for price, buy, sell in parse_fp(row["fp"]):
            profile[price] += buy + sell
    if not profile:
        return None
    prices = sorted(profile)
    poc = max(prices, key=lambda p: (profile[p], -p))
    target, total = sum(profile.values()) * 0.70, profile[poc]
    lo = hi = prices.index(poc)
    while total < target and (lo > 0 or hi < len(prices) - 1):
        lower = profile[prices[lo - 1]] if lo else -1
        upper = profile[prices[hi + 1]] if hi < len(prices) - 1 else -1
        if upper > lower:
            hi += 1
            total += profile[prices[hi]]
        else:
            lo -= 1
            total += profile[prices[lo]]
    return {"val": prices[lo], "vah": prices[hi], "poc": poc}


def _anchor_dt(day, anchor):
    if anchor == "US_CASH":
        local = datetime.combine(day, time(9, 30), ZoneInfo("America/New_York"))
        return local.astimezone(timezone.utc)
    h, m = map(int, anchor.split(":"))
    return datetime.combine(day, time(h, m), timezone.utc)


def _minute_dt(row):
    return datetime.fromtimestamp(int(row["t"]) / 1000, timezone.utc)


def _ohlcv5(rows):
    groups = {}
    for r in rows:
        bucket = int(r["t"]) // 300_000 * 300_000
        a = groups.get(bucket)
        if a is None:
            a = groups[bucket] = {"t": bucket, "end_t": r["t"], "o": r["o"], "h": r["h"], "l": r["l"], "c": r["c"],
                                  "delta": 0.0, "buy_vol": 0.0, "sell_vol": 0.0, "fp_bins": defaultdict(lambda: [0.0, 0.0])}
        a["h"], a["l"], a["c"] = max(a["h"], r["h"]), min(a["l"], r["l"]), r["c"]
        a["end_t"] = r["t"]
        a["delta"] += r["delta"]
        a["buy_vol"] += r["buy_vol"]
        a["sell_vol"] += r["sell_vol"]
        for px, buy, sell in parse_fp(r["fp"]):
            a["fp_bins"][px][0] += buy
            a["fp_bins"][px][1] += sell
    return [groups[t] for t in sorted(groups)]


def detect_candidates(rows, anchors=ANCHORS, prior_legs=20, va_days=1):
    """Detect completed 1m legs; decision is exactly the third consecutive non-extension bar."""
    by_day = defaultdict(list)
    for r in rows:
        by_day[_minute_dt(r).date()].append(r)
    days = sorted(by_day)
    profiles = {d: _value_area(by_day.get(d - timedelta(days=va_days), [])) for d in days}
    history = defaultdict(list)
    found = []
    for d in days:
        dayrows = by_day[d]
        for anchor in anchors:
            start_dt = _anchor_dt(d, anchor)
            start = int(start_dt.timestamp() * 1000)
            active = [r for r in dayrows if start <= r["t"] < start + 4 * 3600_000]
            if not active:
                continue
            # Causal ranking uses only completed legs on earlier dates for this anchor.
            prior = history[anchor][-prior_legs:]
            median = sorted(prior)[(len(prior) - 1) // 2] if len(prior) >= prior_legs else None
            origin = active[0]["o"]
            extremes = {1: active[0]["h"], -1: active[0]["l"]}
            extreme_rows = {1: active[0], -1: active[0]}
            stalls = {1: 0, -1: 0}
            candidate = None
            for r in active[1:]:
                for direction in (1, -1):
                    extends = r["h"] > extremes[1] if direction > 0 else r["l"] < extremes[-1]
                    if extends:
                        extremes[direction] = r["h"] if direction > 0 else r["l"]
                        extreme_rows[direction], stalls[direction] = r, 0
                    else:
                        stalls[direction] += 1
                        if stalls[direction] == 3:
                            extreme = extremes[direction]
                            size = abs(extreme - origin)
                            va = profiles.get(d)
                            outside = va and (extreme > va["vah"] if direction > 0 else extreme < va["val"])
                            if median is not None and size > median and outside:
                                candidate = {"day": d.isoformat(), "anchor": anchor, "anchor_t": start, "direction": direction,
                                             "size_ours": size, "median20_ours": median, "extreme": extreme,
                                             "extreme_t": extreme_rows[direction]["t"], "decision_t": r["t"], "vah": va["vah"],
                                             "val": va["val"], "poc": va["poc"]}
                                break
                if candidate:
                    break
            if candidate:
                found.append(candidate)
            # Record one completed anchor leg per day for future same-anchor comparisons.
            history[anchor].append(max(extremes[1] - origin, origin - extremes[-1]))
    return found


def plot_chart(rows, candidate, output_path=None, blind_id=""):
    """Draw only bars ending at decision_t; return the visible 5m bars for audit/tests."""
    decision = candidate["decision_t"]
    start = candidate.get("anchor_t", decision - 4 * 3600_000) - 2 * 3600_000
    visible = [r for r in rows if start <= r["t"] <= decision]
    bars = _ohlcv5(visible)
    if not bars:
        raise ValueError("no bars before decision")
    W, H = 1500, 920
    im = Image.new("RGB", (W, H), "#101820")
    d = ImageDraw.Draw(im)
    font = ImageFont.load_default()
    prices = [x for b in bars for x in (b["h"], b["l"])] + [candidate[k] for k in ("vah", "val", "poc")]
    pmin, pmax = min(prices), max(prices)
    if pmax == pmin:
        pmax += 1
    def y(p): return int(610 - (p - pmin) / (pmax - pmin) * 520)
    d.text((25, 15), f"{blind_id}  |  BTCUSDT 5m  |  {candidate['day']} {candidate['anchor']} UTC", fill="white", font=font)
    d.text((25, 35), f"OURS: 4h scan; prior20 median; 70% VA; 3rd stall; leg={candidate['size_ours']:.2f}; median={candidate['median20_ours']:.2f}", fill="#e6c76a", font=font)
    for name, color in (("VAH", "#d98b65"), ("VAL", "#d98b65"), ("POC", "#55b9d1")):
        price = candidate[name.lower()]
        yy = y(price)
        d.line((70, yy, 1430, yy), fill=color, width=1)
        d.text((8, yy - 5), f"{name} {price:.1f}", fill=color, font=font)
    dx = 1330 / max(1, len(bars)); candle_w = max(2, int(dx * .58))
    deltas = []
    for i, b in enumerate(bars):
        x = 75 + i * dx
        color = "#39bd93" if b["c"] >= b["o"] else "#e66c6c"
        d.line((x, y(b["h"]), x, y(b["l"])), fill=color)
        d.rectangle((x - candle_w // 2, y(max(b["o"], b["c"])), x + candle_w // 2, y(min(b["o"], b["c"]))), fill=color)
        deltas.append((x, b["delta"]))
    # Session profile from the visible anchor-to-decision bars, aggregated from their footprint bins.
    session_profile = defaultdict(float)
    for b in bars:
        if b["t"] < candidate.get("anchor_t", start + 2 * 3600_000):
            continue
        for px, sides in b["fp_bins"].items():
            session_profile[px] += sides[0] + sides[1]
    max_profile = max(session_profile.values(), default=1) or 1
    for px, volume in session_profile.items():
        yy = y(px)
        d.line((1435, yy, 1435 + int(volume / max_profile * 55), yy), fill="#7793aa", width=2)
    d.text((25, 640), "5m delta (green buy surplus / red sell surplus); footprint at top three | volume bars", fill="white", font=font)
    maxd = max((abs(v) for _, v in deltas), default=1) or 1
    for x, value in deltas:
        width = max(1, int(abs(value) / maxd * 15))
        d.line((x, 690, x + (width if value >= 0 else -width), 690), fill="#39bd93" if value >= 0 else "#e66c6c", width=3)
    top = sorted(bars, key=lambda b: b["buy_vol"] + b["sell_vol"], reverse=True)[:3]
    for i, b in enumerate(top):
        items = sorted(b["fp_bins"].items(), key=lambda kv: kv[1][0] + kv[1][1], reverse=True)[:5]
        s = "  ".join(f"{px:.0f}:{v[0]:.2f}/{v[1]:.2f}" for px, v in items)
        d.text((25, 715 + i * 22), f"FP {_minute_dt({'t': b['t']}).strftime('%H:%M')} buy/sell: {s}", fill="#a9c6dc", font=font)
    d.text((25, 890), "All thresholds and profile convention shown are OURS. Blind chart; no post-decision outcome is plotted.", fill="#e6c76a", font=font)
    if output_path:
        im.save(output_path)
    return {"bars": bars, "image": im}


def load_dev(data_dir):
    """Read only DEV daily gzip rows plus one available warm-up day; no later dates."""
    rows = []
    for p in sorted(Path(data_dir).glob("????-??-??.csv.gz")):
        day = date.fromisoformat(p.name[:10])
        if DEV_START - timedelta(days=1) <= day <= DEV_END:
            with gzip.open(p, "rt", encoding="utf-8", newline="") as f:
                for raw in csv.DictReader(f):
                    rows.append({k: (int(v) if k in INT_COLS else v if k == "fp" else float(v)) for k, v in raw.items()})
    return rows


def run(data_dir, out_dir):
    rows = load_dev(data_dir)
    candidates = detect_candidates(rows)
    rng = random.Random(SEED)
    selected = sorted(candidates, key=lambda x: rng.random())[:60]
    # Random moments are anchor/day draws, with only past-visible candles at the sampled timestamp.
    by_day = defaultdict(list)
    for r in rows:
        if DEV_START <= _minute_dt(r).date() <= DEV_END:
            by_day[_minute_dt(r).date()].append(r)
    moments = []
    for day, dayrows in by_day.items():
        prior_profile = _value_area(by_day.get(day - timedelta(days=1), []))
        if not prior_profile:
            continue
        for anchor in ANCHORS:
            at = int(_anchor_dt(day, anchor).timestamp() * 1000)
            eligible = [r for r in dayrows if at + 2 * 3600_000 <= r["t"] < at + 4 * 3600_000]
            if eligible:
                r = rng.choice(eligible)
                moments.append({"day": day.isoformat(), "anchor": anchor, "anchor_t": at, "decision_t": r["t"], "vah": prior_profile["vah"],
                                "val": prior_profile["val"], "poc": prior_profile["poc"], "size_ours": 0.0, "median20_ours": 0.0,
                                "direction": 0, "extreme": r["c"], "extreme_t": r["t"], "kind": "random"})
    random_sample = rng.sample(moments, min(20, len(moments)))
    samples = [("candidate", x) for x in selected] + [("random", x) for x in random_sample]
    out = Path(out_dir) / "charts"
    out.mkdir(parents=True, exist_ok=True)
    keys = []
    counts = defaultdict(int)
    all_counts = defaultdict(int)
    for item in candidates:
        all_counts[item["anchor"]] += 1
    for kind, item in samples:
        keys.append((kind, item["day"], item["anchor"], item["decision_t"]))
    rng.shuffle(keys)
    index = []
    for n, (kind, day, anchor, ts) in enumerate(keys, 1):
        blind = f"C{n:03d}"
        item = next(x for x in samples if x[0] == kind and x[1]["day"] == day and x[1]["anchor"] == anchor and x[1]["decision_t"] == ts)[1]
        item = dict(item, kind=kind)
        plot_chart(rows, item, out / f"{blind}.png", blind)
        index.append({"blind_id": blind, "file": f"{blind}.png"})
    with open(out / "_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(["blind_id", "kind", "day", "anchor", "decision_t"]); w.writerows(keys)
    with open(out / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["blind_id", "file"], lineterminator="\n"); w.writeheader(); w.writerows(index)
    print(f"candidates={len(candidates)} sampled={len(selected)} random={len(random_sample)} per_anchor={dict(all_counts)} charts={len(samples)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=r"F:\MTS\data\orderflow_1m")
    ap.add_argument("--out", default=str(HERE))
    args = ap.parse_args()
    run(args.data, args.out)
