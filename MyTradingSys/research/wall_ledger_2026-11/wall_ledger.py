"""Offline wall ledger over a sequence of Binance depth snapshots (no live wiring).

A snapshot is {"ts": seconds, "bids": {price: qty}, "asks": {price: qty},
"trades": [(price, qty), ...]} where trades are the prints since the previous snapshot.

Parameters:
- THRESHOLD_USD 1.5M per cell: OURS, adopted from the CoinGlass BTC wall minimum (SOURCED there,
  FIELD_GUIDE.md row "Wall").
- GRID_USD 10: OURS, adopted from the CoinGlass BTC default row size (FIELD_GUIDE.md "Price grid").
- PERSIST 3 consecutive snapshots: OURS (CoinGlass says only "persist across consecutive updates").
"""

THRESHOLD_USD = 1_500_000
GRID_USD = 10
PERSIST = 3


def bucket(price, grid=GRID_USD):
    return (price // grid) * grid


def cell_usd(levels, grid=GRID_USD):
    cells = {}
    for price, qty in levels.items():
        b = bucket(price, grid)
        cells[b] = cells.get(b, 0.0) + price * qty
    return cells


def candidates(s, threshold=THRESHOLD_USD, grid=GRID_USD):
    out = {}
    for side, key in (("bid", "bids"), ("ask", "asks")):
        for level, usd in cell_usd(s[key], grid).items():
            if usd >= threshold:
                out[(side, level)] = usd
    return out


def mid(s):
    if not s["bids"] or not s["asks"]:
        return None
    return (max(s["bids"]) + min(s["asks"])) / 2


def _in_cell(price, level, grid):
    return level <= price < level + grid


def _touched(s, level, grid):
    prices = [p for p, _ in s["trades"]]
    if s["bids"]:
        prices.append(max(s["bids"]))
    if s["asks"]:
        prices.append(min(s["asks"]))
    return any(_in_cell(p, level, grid) for p in prices)


def _traded(s, level, grid):
    return any(q > 0 and _in_cell(p, level, grid) for p, q in s["trades"])


def build_ledger(snaps, threshold=THRESHOLD_USD, grid=GRID_USD, persist=PERSIST):
    """One row per wall life: side, level, placed_ts, end_ts, outcome (open/pulled/filled),
    max_usd, distance_pct (to mid at first sight), age_s, touched."""
    pending = {}  # key -> {"first": snapshot index, "count", "max_usd", "touched", "traded"}
    rows = []
    for i, s in enumerate(snaps):
        cur = candidates(s, threshold, grid)
        for key in list(pending):
            if key in cur:
                continue
            st = pending.pop(key)
            touched = st["touched"] or _touched(s, key[1], grid)
            traded = st["traded"] or _traded(s, key[1], grid)
            if st["count"] >= persist:
                rows.append(_row(key, st, snaps, s["ts"], "filled" if traded else "pulled", touched))
        for key, usd in cur.items():
            st = pending.setdefault(key, {"first": i, "count": 0, "max_usd": 0.0,
                                          "touched": False, "traded": False})
            st["count"] += 1
            st["max_usd"] = max(st["max_usd"], usd)
            st["touched"] = st["touched"] or _touched(s, key[1], grid)
            st["traded"] = st["traded"] or _traded(s, key[1], grid)
    last_ts = snaps[-1]["ts"] if snaps else None
    for key, st in pending.items():
        if st["count"] >= persist:
            rows.append(_row(key, st, snaps, last_ts, "open", st["touched"]))
    return rows


def _row(key, st, snaps, end_ts, outcome, touched):
    first = snaps[st["first"]]
    m = mid(first)
    return {
        "side": key[0],
        "level": key[1],
        "placed_ts": first["ts"],
        "end_ts": None if outcome == "open" else end_ts,
        "outcome": outcome,
        "max_usd": st["max_usd"],
        "distance_pct": None if m is None else (key[1] - m) / m * 100,
        "age_s": end_ts - first["ts"],
        "touched": touched,
    }


def summary(rows):
    count = {o: sum(1 for r in rows if r["outcome"] == o) for o in ("open", "pulled", "filled")}
    before = sum(1 for r in rows if r["outcome"] == "pulled" and not r["touched"])
    closed = count["pulled"] + count["filled"]
    return {"placed": len(rows), **count, "pulled_before_touch": before,
            "pulled_before_touch_rate": before / closed if closed else None}
