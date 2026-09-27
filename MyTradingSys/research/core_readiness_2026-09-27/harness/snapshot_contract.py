import sys
sys.dont_write_bytecode = True
"""
snapshot_contract.py - L0 contract: what MarketDataSnapshot.java is required to
hand every downstream layer, checked over every archived snapshot in
runtime_data/snapshots. Task A5 of CORE_READINESS_PLAN.md.

Layer: L0 (ingest). Pure read. No network. No writes. Checks shape and range,
not correctness of the numbers themselves (that is core_invariants.py's job,
one layer up).

Each invariant is a numbered check with a BASELINE count of known violations
measured 2026-09-27 on the full corpus. Result:
  PASS  - every check <= its baseline and no unknown check/enum value fired
  FAIL  - any check above baseline (regression), or an unseen enum value
Counts below baseline are reported as IMPROVED (update the baseline on purpose).

Run from repo root:
  python MyTradingSys/research/core_readiness_2026-09-27/harness/snapshot_contract.py
"""
import argparse
from collections import Counter, defaultdict

import _common  # noqa: F401
from snapshots import iter_snapshots, parse_ts  # noqa: E402

REQUIRED_TOP = [
    "timestamp_utc", "asset", "current_price", "weekly_vp", "daily_vp",
    "post_funding_vp", "intraday_4h_vp", "vwap", "cvd", "trade_flow",
    "structure", "order_book_depth", "conditions", "prior_day", "funding",
    "open_interest", "session", "session_timing", "spot_perp_basis",
    "liquidation_clusters", "oi_breakdown", "order_flow",
]

# enum fields: dotted path -> observed set (2026-09-27). A value outside this
# set is UNKNOWN (fails), not silently accepted - that is the point of a
# contract check: a new enum value must be a reviewed decision, not a surprise.
# Observed sets measured 2026-09-27 on the full corpus (9,216 snapshots).
# A value outside this set is UNKNOWN (fails) - a genuinely new enum value
# must be a reviewed decision (add it here on purpose), not a silent pass.
ENUM_FIELDS = {
    "cvd.slope": {"rising", "falling", "flat"},
    "vwap.slope": {"rising", "falling", "flat"},
    "conditions.cvd_slope": {"rising", "falling", "flat"},
    "conditions.vwap_slope": {"rising", "falling", "flat"},
    "conditions.price_vs_va": {"in_va", "above_vah", "below_val"},
    "conditions.price_vs_poc": {"above", "below"},
    "open_interest.direction": {"rising", "falling", "flat"},
    "open_interest.delta_state": {"neutral", "building", "unwinding",
                                   "rekt_short", "rekt_long", "aggressive_long", "aggressive_short"},
    "open_interest.delta_state_price": {"neutral", "building", "unwinding",
                                         "rekt_short", "rekt_long", "aggressive_long", "aggressive_short"},
    "spot_perp_basis.direction": {"premium", "discount", "flat"},
    "session.day_type": {"trend_up", "trend_down", "balance", "range", "UNKNOWN"},
    "session.gap_direction": {"up", "down", "flat"},
    "session.open_location": {"in_value", "above_value", "below_value"},
    "session.liquidity_sweep_direction": {"above", "below", "none"},
    "session_timing.current_session": {"us_premarket", "us_cash_open", "us_europe_overlap",
                                        "us_core", "asia_europe_overlap", "european",
                                        "after_hours", "asian", "us_close"},
}

VP_BLOCKS = ["weekly_vp", "daily_vp", "post_funding_vp", "intraday_4h_vp", "prior_day"]

PRICE_PATHS = [
    "weekly_vp.poc", "weekly_vp.vah", "weekly_vp.val",
    "weekly_vp.prior_week_poc", "weekly_vp.two_week_ago_poc",
    "daily_vp.poc", "daily_vp.vah", "daily_vp.val",
    "post_funding_vp.poc", "post_funding_vp.vah", "post_funding_vp.val",
    "intraday_4h_vp.poc", "intraday_4h_vp.vah", "intraday_4h_vp.val",
    "prior_day.poc", "prior_day.vah", "prior_day.val",
    "prior_day.close", "prior_day.high", "prior_day.low",
    "vwap.price", "vwap.bands.+1s", "vwap.bands.+2s", "vwap.bands.-1s", "vwap.bands.-2s",
    "structure.1w.swing_high", "structure.1w.swing_low",
    "structure.1d.swing_high", "structure.1d.swing_low",
    "structure.4h.swing_high", "structure.4h.swing_low",
    "structure.1h.swing_high", "structure.1h.swing_low",
    "structure.15m.swing_high", "structure.15m.swing_low",
    "structure.5m.swing_high", "structure.5m.swing_low",
    "conditions.fvg_nearest_unfilled.top", "conditions.fvg_nearest_unfilled.bottom",
    "spot_perp_basis.spot_price", "spot_perp_basis.mark_price",
    "liquidation_clusters.nearest_above.price", "liquidation_clusters.nearest_below.price",
]

NUMERIC_PATHS_SAMPLE = [
    "current_price", "cvd.value", "vwap.price", "order_book_depth.bid_ask_ratio",
    "funding.current_rate", "session.range_position_pct",
]

# BASELINE_FULL measured 2026-09-27 on 9,217 archived snapshots.
# C01=1768: the "session" block did not exist before 2026-09-16T12:26:18Z
# (last snapshot without it: BTCUSDT_2026-09-16_1789559417149.json). All
# snapshots from that point on carry it - use --since to get 0 on current code.
BASELINE_FULL = {
    "C01 missing required top-level key": 1768,
    "C02 enum value outside observed set": 0,
    "C03 VP block val<=poc<=vah violated": 0,
    "C04 price field beyond 25pct of current_price": 0,
    "C05 numeric field not int/float": 0,
    "C06 current_price non-positive or missing": 0,
}
BASELINE_SINCE = {k: 0 for k in BASELINE_FULL}
SESSION_BLOCK_ADDED = "2026-09-16T12:26:18Z"


def get(d, dotted):
    cur = d
    for k in dotted.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def check(snaps):
    hits = Counter(); ex = defaultdict(list)

    def hit(k, e):
        hits[k] += 1
        if len(ex[k]) < 5:
            ex[k].append(e)

    for p, s, t in snaps:
        for k in REQUIRED_TOP:
            if k not in s:
                hit("C01 missing required top-level key", (p.name, k))
        cp = s.get("current_price")
        if not isinstance(cp, (int, float)) or cp <= 0:
            hit("C06 current_price non-positive or missing", (p.name, cp))
            cp = None
        for path, allowed in ENUM_FIELDS.items():
            v = get(s, path)
            if v is not None and v not in allowed:
                hit("C02 enum value outside observed set", (p.name, path, v))
        for blk in VP_BLOCKS:
            b = s.get(blk) or {}
            val, poc, vah = b.get("val"), b.get("poc"), b.get("vah")
            if None not in (val, poc, vah):
                if not (val - 1e-6 <= poc <= vah + 1e-6):
                    hit("C03 VP block val<=poc<=vah violated", (p.name, blk, val, poc, vah))
        if cp:
            for path in PRICE_PATHS:
                v = get(s, path)
                if v is None or v == 0.0:
                    continue
                if not isinstance(v, (int, float)):
                    hit("C05 numeric field not int/float", (p.name, path, v))
                    continue
                if abs(v - cp) / cp > 0.25:
                    hit("C04 price field beyond 25pct of current_price", (p.name, path, v, cp))
        for path in NUMERIC_PATHS_SAMPLE:
            v = get(s, path)
            if v is not None and not isinstance(v, (int, float)):
                hit("C05 numeric field not int/float", (p.name, path, v))
    return hits, ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="ISO timestamp; only snapshots at/after it")
    a = ap.parse_args()
    snaps, stats = iter_snapshots()
    base_table = BASELINE_FULL
    if a.since:
        b = parse_ts(a.since)
        snaps = [x for x in snaps if x[2] >= b]
        base_table = BASELINE_SINCE
    print("load stats:", stats, "| checked snapshots:", len(snaps))
    hits, ex = check(snaps)
    fail = False
    for k, base in base_table.items():
        n = hits.get(k, 0)
        tag = "OK" if n == base else ("IMPROVED" if n < base else "REGRESS")
        if n > base:
            fail = True
        print("  %-8s %-55s %6d (baseline %d)" % (tag, k, n, base))
        if n > base:
            for e in ex[k]:
                print("           e.g.", e)
    unknown = [k for k in hits if k not in base_table]
    for k in unknown:
        fail = True
        print("  UNKNOWN  %s %d" % (k, hits[k]))
        for e in ex[k][:5]:
            print("           e.g.", e)
    print("RESULT:", "FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
