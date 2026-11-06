"""Score the 9 priced Habib plans (PLAN_LEDGER.csv) against Binance klines and tag each with book concepts.

Scoring = plan_score.score_plan unchanged (24 h fill window, 7 d open window, PARTIAL_FRAC 0.5; execution excluded) per
PRE_REG_HABIB_PLANS.md s3. Descriptive only: the pre-reg kill rule 1 (fewer than 12 distinct posts) forbids a p-value or claim.
Holdout release for these 9 plans: operator order of 2026-11-06 (decision d-habib-calls-unsealed-1106, recorded by Lead C per the
session brief). Scoring tunes nothing of ours.

Usage (repo root): python MyTradingSys/research/habib_concept_book_2026-11/calls_score.py
Writes CALLS_SCORED.csv next to this file. Network: data-api.binance.vision public klines.
"""
import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "habib_plan_imbalance_2026-10-20"))
import habib_common as hc  # noqa: E402
import plan_score as ps  # noqa: E402

LEDGER = HERE.parent / "habib_plan_imbalance_2026-10-20" / "PLAN_LEDGER.csv"
OUT = HERE / "CALLS_SCORED.csv"
FEE_BP = 10.0               # PRE_REG s3: 0.05 % per side, both legs
FEE_DOMINATED_BP = 20.0     # PRE_REG s3
STOPS = {"QRP-ZPFK3ZsLwoo-05": 82800.0, "QRP-ZPFK3ZsLwoo-06": 82800.0}   # CALL_LEDGER.csv stop column (the only priced stops)
SEARCH_DAYS = {"1d": 30, "12h": 21, "4h": 14, "1h": 5, "30m": 3}        # OURS: how far back an underlying imbalance candle is searched
FETCH_DAYS = {"1d": 100, "12h": 100, "4h": 50, "1h": 25, "30m": 12}     # enough history for the 50-bar median plus the search window
TF_ORDER = ["1d", "12h", "4h", "1h", "30m"]


def parse_utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def fill_and_path(bars, direction, entry, target, posted_ms, stop=None):
    """First fill minute inside 24 h, then first target / stop touch inside 7 d. Same-minute stop+target resolves to the stop."""
    sign = 1 if direction == "long" else -1
    fill = None
    for k in bars:
        if k[0] < posted_ms:
            continue
        if k[0] >= posted_ms + 86_400_000:
            break
        if k[3] <= entry <= k[2]:
            fill = k[0]
            break
    if fill is None:
        return None
    mae = 0.0   # worst adverse excursion (fraction of entry) before the target or the end
    hit = None
    stopped = None
    end = posted_ms + 7 * 86_400_000
    for k in bars:
        if k[0] < fill or k[0] >= end:
            continue
        reach = k[2] if sign == 1 else k[3]
        adverse = k[3] if sign == 1 else k[2]
        st_hit = stop is not None and ((adverse - stop) * sign <= 0)
        tg_hit = (reach - target) * sign >= 0
        if st_hit and stopped is None and (hit is None):
            stopped = k[0]
        if tg_hit and hit is None:
            hit = k[0]
            if stopped is not None:
                pass
            break
        mae = max(mae, (entry - adverse) * sign / entry)
    last_close = [k for k in bars if k[0] < end][-1][4]
    return {"fill": fill, "hit": hit, "stopped_first": stopped is not None and (hit is None or stopped <= hit),
            "mae": mae, "last_close": last_close}


def swing_levels(bars, now_ms):
    """Prior 7 d / 14 d high and low (1m bars strictly before now): the 'sweep of a recent high/low' family."""
    out = {}
    for n in (7, 14):
        w = [k for k in bars if now_ms - n * hc.DAY <= k[0] < now_ms]
        if len(w) >= n * 1440 - 120:
            out[f"Prior {n}d high"] = max(k[2] for k in w)
            out[f"Prior {n}d low"] = min(k[3] for k in w)
    return out


def reach_diag(h1, direction, entry, target, posted_ms):
    """DESCRIPTIVE, outside the pre-reg classes (1h bars): closest approach to the entry inside 24 h, and whether the entry
    was touched inside 7 d / 30 d and the target reached afterwards inside 30 d."""
    sign = 1 if direction == "long" else -1
    def gap(w):
        """bp the 24 h range missed the entry by (0 = touched). Works for entries above or below the post-time price."""
        if not w:
            return None
        hi, lo = max(k[2] for k in w), min(k[3] for k in w)
        return max(entry - hi, lo - entry, 0.0) / entry * 1e4
    w24 = [k for k in h1 if posted_ms <= k[0] < posted_ms + hc.DAY]
    res = {"gap_bp_24h": f"{gap(w24):.0f}" if w24 else ""}
    touch = None
    for k in h1:
        if k[0] >= posted_ms and k[3] <= entry <= k[2]:
            touch = k[0]
            break
    after = [k for k in h1 if touch is not None and k[0] >= touch and k[0] < posted_ms + 30 * hc.DAY]
    tgt = next((k[0] for k in after if k[0] > touch and ((k[2] if sign == 1 else k[3]) - target) * sign >= 0), None)  # strictly later bar: no same-bar order guess
    prog = max([((k[2] if sign == 1 else k[3]) - entry) * sign for k in after if k[0] > touch] or [0.0])
    res["progress_30d"] = f"{max(prog, 0.0) / abs(target - entry):.0%}" if touch is not None else ""
    res["entry_touch_h"] = f"{(touch - posted_ms) / 3.6e6:.0f}" if touch is not None and touch < posted_ms + 30 * hc.DAY else "never<=30d"
    res["target_after_touch_30d"] = f"{(tgt - touch) / 3.6e6:.0f}h" if tgt is not None else "no"
    return res


def underlying_imbalance(tfrows, level, posted_ms):
    """Highest-timeframe flagged candle closed before the post whose open/midpoint (tight) or range (loose) holds the level."""
    best = None
    for tf in TF_ORDER:
        rows = tfrows[tf]
        flags = hc.imbalance_flags(rows)
        lo_ms = posted_ms - SEARCH_DAYS[tf] * hc.DAY
        for r, f in zip(reversed(rows), reversed(flags)):
            if f is None or r[0] + hc.TF_MS[tf] > posted_ms or r[0] < lo_ms:
                continue
            mid = (r[2] + r[3]) / 2
            tight = ("open" if abs(r[1] - level) / level <= hc.TOL_MID else
                     "mid" if abs(mid - level) / level <= hc.TOL_MID else None)
            loose = r[3] * (1 - hc.TOL_RANGE) <= level <= r[2] * (1 + hc.TOL_RANGE)
            if tight or loose:
                cand = (0 if tight else 1, TF_ORDER.index(tf), -r[0], tf, r, f, tight or "range")
                if best is None or cand[:3] < best[:3]:
                    best = cand
    if best is None:
        return "none"
    _, _, _, tf, r, f, how = best
    return f"{tf} {hc.utc(r[0]):%m-%d %H:%M} rv{f['rv']:.1f} {f['bclass']} {f['wick']} [{how}]"


def trigger_candle(tfrows, fill_ms, direction):
    """Flagged 30m/1h candle that contains the fill minute or is the next one; rejection wick on the side facing the move."""
    found = []
    for tf in ("1h", "30m"):
        rows = tfrows[tf]
        flags = hc.imbalance_flags(rows)
        step = hc.TF_MS[tf]
        for r, f in zip(rows, flags):
            if f is None:
                continue
            if r[0] <= fill_ms < r[0] + step or r[0] == (fill_ms - fill_ms % step) + step:
                u, l = hc.wicks(r)
                rej = u if direction == "short" else l
                found.append(f"{tf} {hc.utc(r[0]):%m-%d %H:%M} rv{f['rv']:.1f} {f['bclass']} rej-wick {rej:.0%}")
    return "; ".join(found) if found else "none"


def main():
    plans = list(csv.DictReader(open(LEDGER, encoding="utf-8")))
    rows_out = []
    cache = {}
    for p in plans:
        posted = parse_utc(p["posted_utc"])
        pm = hc.ms_of(posted)
        d, e, t = p["direction"], float(p["entry"]), float(p["target1"])
        key = p["posted_utc"]
        if key not in cache:
            bars = hc.fetch_klines("1m", pm - 15 * hc.DAY, pm + 8 * hc.DAY)
            tfrows = {tf: hc.fetch_klines(tf, pm - FETCH_DAYS[tf] * hc.DAY, pm + 8 * hc.DAY) for tf in TF_ORDER}
            h30 = hc.fetch_klines("1h", pm, pm + 31 * hc.DAY)
            cache[key] = (bars, tfrows, h30)
        bars, tfrows, h30 = cache[key]
        diag = reach_diag(h30, d, e, t, pm)
        candles = [(hc.utc(k[0]), k[2], k[3]) for k in bars]
        try:
            status = ps.score_plan(candles, d, e, t, posted)
        except ps.NoData:
            status = "NO_DATA"
        stop = STOPS.get(p["call_id"])
        path = fill_and_path(bars, d, e, t, pm, stop)
        sign = 1 if d == "long" else -1
        dist_bp = abs(t - e) / e * 1e4
        net = ""
        if path is not None:
            if dist_bp < FEE_DOMINATED_BP:
                net = "fee-dominated"
            elif status == "full":
                net = f"{dist_bp - FEE_BP:.0f}"
            else:
                net = f"{(path['last_close'] - e) * sign / e * 1e4 - FEE_BP:.0f}"
        lv = hc.prior_day_levels(bars, pm)
        lv.update(hc.week_month_levels(bars, pm))
        lv.update(swing_levels(bars, pm))
        near = hc.nearest_level(e, lv)
        if path is not None:
            fl = hc.prior_day_levels(bars, path["fill"])
            fl.update(hc.week_month_levels(bars, path["fill"]))
            fl.update(swing_levels(bars, path["fill"]))
            near_fill = hc.nearest_level(e, fl)
            near = near or near_fill
        round_hit = abs(e - round(e / 1000) * 1000) / e <= 0.0015
        rows_out.append({
            "call_id": p["call_id"], "posted_utc": p["posted_utc"], "direction": d, "entry": int(e), "target1": int(t),
            "status": status,
            "fill_utc": f"{hc.utc(path['fill']):%m-%d %H:%M}" if path else "",
            "target_utc": f"{hc.utc(path['hit']):%m-%d %H:%M}" if path and path["hit"] else "",
            "mae_pct_before_target": f"{path['mae'] * 100:.2f}" if path else "",
            "stop_given": int(stop) if stop else "",
            "stopped_before_target": ("yes" if path and path["stopped_first"] else "no") if stop and path else "",
            "target_dist_bp": f"{dist_bp:.0f}",
            "net_bp_fee10_nostop": net,
            "nearest_known_level": f"{near[0]} {near[1]:.0f} ({near[2] * 100:.2f}%)" if near else "none within 0.3%",
            "gap_bp_24h": diag["gap_bp_24h"], "entry_touch_h_after_post": diag["entry_touch_h"],
            "target_after_touch_30d": diag["target_after_touch_30d"], "progress_to_target_30d": diag["progress_30d"],
            "round_1000": "yes" if round_hit else "no",
            "underlying_imbalance": underlying_imbalance(tfrows, e, pm),
            "trigger_candle": trigger_candle(tfrows, path["fill"], d) if path else "not filled",
        })
    cols = list(rows_out[0])
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)
    for r in rows_out:
        print(r["call_id"], r["status"], r["fill_utc"], r["target_utc"], "mae", r["mae_pct_before_target"], "|", r["nearest_known_level"],
              "|", r["underlying_imbalance"], "|", r["trigger_candle"])
    by = {}
    for r in rows_out:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print(by)


if __name__ == "__main__":
    main()
