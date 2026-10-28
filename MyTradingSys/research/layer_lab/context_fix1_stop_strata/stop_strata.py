"""Count-only stop geometry and within-stop-timeframe E summaries for context V2.

Inputs are row mappings built from DEV decision-time fields (side, f3_stop_tf,
f3_stop_pct) and, for stratified E, already executed DEV outcome records. This
module does not load prices or read data after T.
"""
from collections import defaultdict
from collections.abc import Iterable, Mapping
from statistics import fmean

SIDES = ("long", "short")
POOLS = ("C", "control_pool")


def _field(row: Mapping, *names):
    for name in names:
        if name in row:
            return row[name]
    raise KeyError(f"row missing required field; expected one of {names}")


def _valid_stop_rows(rows: Iterable[Mapping]):
    """Return normalized side, stop timeframe and positive stop_pct rows."""
    normalized = []
    for row in rows:
        side = str(_field(row, "side"))
        tf = str(_field(row, "f3_stop_tf", "stop_tf", "ctrl_stop_tf"))
        pct = float(_field(row, "f3_stop_pct", "stop_pct"))
        if side not in SIDES:
            raise ValueError(f"invalid side: {side}")
        if tf == "none" or not tf:
            continue
        if pct <= 0:
            raise ValueError("stop_pct must be positive for a valid stop")
        normalized.append((side, tf, pct))
    return normalized


def summarize_stop_geometry(c_events: Iterable[Mapping], control_pool: Iterable[Mapping]):
    """Return per-pool, per-side timeframe shares and stop_pct median/p90."""
    result = {pool: {} for pool in POOLS}
    for label, rows in (("C", c_events), ("control_pool", control_pool)):
        by_side = defaultdict(list)
        for side, tf, pct in _valid_stop_rows(rows):
            by_side[side].append((tf, pct))
        for side in SIDES:
            values = by_side[side]
            n = len(values)
            if not n:
                result[label][side] = {
                    "n": 0, "shares": {}, "median_stop_pct": None, "p90_stop_pct": None,
                }
                continue
            counts = defaultdict(int)
            pcts = []
            for tf, pct in values:
                counts[tf] += 1
                pcts.append(pct)
            pcts.sort()
            result[label][side] = {
                "n": n,
                "shares": {tf: counts[tf] / n for tf in sorted(counts)},
                "median_stop_pct": _quantile(pcts, 0.5),
                "p90_stop_pct": _quantile(pcts, 0.9),
            }
    return result


def _quantile(sorted_values, q):
    """NumPy-compatible linear quantile without requiring NumPy."""
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = (len(sorted_values) - 1) * q
    lo = int(position)
    hi = min(lo + 1, len(sorted_values) - 1)
    fraction = position - lo
    return float(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * fraction)


def stop_comparability(summary, threshold=0.25):
    """Flag sides whose pool median stop width differs from C by > threshold, relative to C."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    output = {}
    for side in SIDES:
        c = summary["C"][side]["median_stop_pct"]
        control = summary["control_pool"][side]["median_stop_pct"]
        gap = None if c is None or control is None or c == 0 else abs(control - c) / abs(c)
        output[side] = {
            "c_median_stop_pct": c,
            "control_median_stop_pct": control,
            "relative_median_gap": gap,
            "r_units_not_comparable": gap is not None and gap > threshold,
        }
    return output


def stratified_e(c_events: Iterable[Mapping], controls: Iterable[Mapping], kmin=10):
    """Compute E = mean(C net_R) - mean(control net_R) by side and stop timeframe.

    Strata with fewer than kmin control records are omitted. The returned E is
    a plain outcome summary; callers must apply the registered verdict rule.
    """
    if kmin < 1:
        raise ValueError("kmin must be >= 1")
    event_values = defaultdict(list)
    control_values = defaultdict(list)
    for row in c_events:
        side = str(_field(row, "side"))
        tf = str(_field(row, "f3_stop_tf", "stop_tf"))
        value = float(_field(row, "net_R"))
        if side not in SIDES:
            raise ValueError(f"invalid side: {side}")
        if tf != "none":
            event_values[(side, tf)].append(value)
    for row in controls:
        side = str(_field(row, "side"))
        tf = str(_field(row, "f3_stop_tf", "stop_tf", "ctrl_stop_tf"))
        value = float(_field(row, "net_R", "ctrl_net_R"))
        if side not in SIDES:
            raise ValueError(f"invalid side: {side}")
        if tf != "none":
            control_values[(side, tf)].append(value)

    rows = []
    for side, tf in sorted(event_values):
        events = event_values[(side, tf)]
        control_r = control_values.get((side, tf), [])
        eligible = len(control_r) >= kmin
        mean_event = fmean(events)
        mean_control = fmean(control_r) if eligible else None
        rows.append({
            "side": side,
            "f3_stop_tf": tf,
            "n_events": len(events),
            "n_controls": len(control_r),
            "mean_event_net_R": mean_event,
            "mean_control_net_R": mean_control,
            "E": mean_event - mean_control if eligible else None,
            "eligible": eligible,
        })
    return rows


def count_dev_stop_geometry():
    """Load only cached decision frames and print V2 C/pool geometry by side.

    Requires the context_factors_2026-10-16 research folder and its cached DEV
    frames. No trade simulator, 1m bars, entry, or post-T price is accessed.
    """
    import sys
    from pathlib import Path

    context_dir = Path(__file__).resolve().parents[2] / "context_factors_2026-10-16"
    sys.path.insert(0, str(context_dir))
    import study  # local research implementation; frames() reads decision cache only

    frames = study.frames()
    c_rows = []
    pool_rows = []
    for side, frame in frames.items():
        ledger = study.tradeable_ledger(frame)
        c = study.form_c(ledger, side)
        times = frame["T"].to_numpy()
        c_times = c["T"].to_numpy()
        near_c = (abs(times[:, None] - c_times[None, :]) <= study.DAY).any(axis=1)
        pool_mask = (frame["f1_at_level"].to_numpy(bool)
                     & (frame["f3_stop_tf"].to_numpy() != "none") & ~near_c)
        pool = frame[pool_mask]
        for source, dest in ((c, c_rows), (pool, pool_rows)):
            rows = source[["f3_stop_tf", "f3_stop_pct"]].copy()
            rows["side"] = side
            rows.rename(columns={"f3_stop_pct": "stop_pct"}, inplace=True)
            dest.extend(rows.to_dict("records"))
    summary = summarize_stop_geometry(c_rows, pool_rows)
    comparisons = stop_comparability(summary)
    for pool_name in POOLS:
        print(pool_name)
        for side in SIDES:
            row = summary[pool_name][side]
            shares = ", ".join(f"{tf}={share:.4%}" for tf, share in row["shares"].items()) or "none"
            median = "NOT_IN_DATA" if row["median_stop_pct"] is None else f"{row['median_stop_pct']:.6f}%"
            p90 = "NOT_IN_DATA" if row["p90_stop_pct"] is None else f"{row['p90_stop_pct']:.6f}%"
            print(f"  {side}: n={row['n']}; shares: {shares}; median={median}; p90={p90}")
    for side in SIDES:
        item = comparisons[side]
        flag = "R units not comparable" if item["r_units_not_comparable"] else "comparable"
        print(f"gap {side}: {item['relative_median_gap']:.4%}; {flag}")
    return summary


if __name__ == "__main__":
    count_dev_stop_geometry()
