"""Analyst price levels from the CBP store, sorted by price, next to where BTC trades now.

Operator 2026-10-30: Michael's 78k/75k and Krown's 76-77k wick were in CBP before the 10-29 break, but neither
Eagle_Eyes nor the dashboard showed them. This is the one place that turns CBP rows into a level ladder.

  python scripts/dev/analyst_levels.py                 # last 10 days, live price + hit/open per level (public spot klines)
  python scripts/dev/analyst_levels.py --offline       # no network (hooks): levels only
  python scripts/dev/analyst_levels.py --symbol ETH    # another symbol (band in SYMBOL_BANDS)
  python scripts/dev/analyst_levels.py --json          # for the dashboard

Levels are parsed from each row's `pointers` (prices inside SYMBOL_BANDS[symbol]; BTC 40k..200k); hit = traded within TOUCH_TOL (0.05 %) of the level since 00:00 UTC of the day AFTER
the publish date (only the date is stored, so publish-day bars could predate the video: audit 2026-10-30 finding 3).
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "MyTradingSys"))
import cbp  # noqa: E402
try:
    from MyTradingSys.runtime.binance_doh import urlopen as _urlopen  # ISP DNS block fix: Binance hosts via DoH
except ImportError:  # run from outside the repo root layout
    sys.path.insert(0, ROOT)
    from MyTradingSys.runtime.binance_doh import urlopen as _urlopen

# A wick within 0.05 % of a level counts as a touch (OURS, one constant; 11-08 21:55Z BTC spot low 73,510 vs level 73,500 = 0.014 %,
# perp traded ~73,333). Used by mark() here and by the live LEVEL TOUCH alert.
TOUCH_TOL = 0.0005

# Per-symbol price band a pointer number must fall in to count as a level. BTC 40k..200k as before; the rest are OURS
# (not sourced from any analyst): wide enough for the 2026 range of the name, tight enough to drop counts and dates.
SYMBOL_BANDS = {"BTC": (40_000, 200_000), "ETH": (1_000, 10_000)}
LO, HI = SYMBOL_BANDS["BTC"]
_NUM = (r"\$?(\d{1,3}(?:,\d{3})+|\d{1,3}(?:\.\d+)?\s*[kK]\b|\d{2,3}(?:\.\d+)?\s*thousand|\d{4,6})")
_RANGE_K = re.compile(r"\b(\d{2,3}(?:\.\d+)?)\s*[kK]?\s*-\s*(\d{2,3}(?:\.\d+)?)\s*[kK]\b")
_NOT_PRICE = re.compile(r"(?i)(?<![\d,.])\b\d{2,3}(?:\.\d+)?\s*[kK]?\s*(?:in\s+)?(?:liquidations?|liquidated|contracts?|coins?|"
                        r"subscribers?|followers?|views?|votes?|people|wallets?|addresses|transactions?|traders?)\b")

_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
# A bare 2020-2039 is a year only with a date cue before it ("in 2026", "by 2030", "October 2026"); "ETH 2030 support" is a price.
_YEAR = re.compile(r"(?i)\b(?:in|by|of|since|during|until|through|from|year|q[1-4]|" + _MONTH + r")\s+20[2-3]\d(?![,.]?\d)")


def _val(tok):
    t = tok.replace("$", "").replace(",", "").strip().lower()
    if t.endswith("thousand"):
        return float(t[:-8].strip()) * 1000
    if t.endswith("k"):
        return float(t[:-1].strip()) * 1000
    return float(t)


def parse_levels(text, symbol="BTC"):
    """Prices named in one pointer, in order, de-duplicated. '90-92k' gives 90,000 and 92,000.
    Only values inside SYMBOL_BANDS[symbol] count (unknown symbol: none)."""
    lo, hi = SYMBOL_BANDS.get(symbol, (None, None))
    if lo is None:
        return []
    out = []
    text = _NOT_PRICE.sub(" ", text)  # "100k liquidations" is a count, not a price
    text = _YEAR.sub(" ", text)
    for a, b in _RANGE_K.findall(text):
        out += [float(a) * 1000, float(b) * 1000]
    for tok in re.findall(_NUM, text):
        out.append(_val(tok))
    seen, res = set(), []
    for v in out:
        if lo <= v <= hi and v not in seen:
            seen.add(v)
            res.append(v)
    return res


def ladder(rows, symbol="BTC"):
    lv, seen = [], set()
    for r in rows:
        if symbol not in [cbp._norm_symbol(s) for s in r.get("symbols") or []]:
            continue
        for p in r.get("pointers") or []:
            for v in parse_levels(p, symbol):
                if (v, r.get("video_id")) in seen:
                    continue  # one level per video: the first pointer that names it
                seen.add((v, r.get("video_id")))
                lv.append(dict(level=v, analyst=r["analyst"], published=r["published"], bias=r.get("bias", ""),
                               video_id=r.get("video_id", ""), said=p, expires_at=r.get("expires_at", "")))
    return sorted(lv, key=lambda x: -x["level"])


def recent_rows(days, now, store=None):
    cutoff = (now - timedelta(days=days)).date().isoformat()
    return [r for r in cbp.load(store)["rows"] if not cbp.validate_row(r) and (r.get("published") or "") >= cutoff]


def touched(level, low, high, tol=TOUCH_TOL):
    """True when the bar range [low, high] comes within `tol` (fraction of the level) of `level`, or crosses it."""
    return low <= level * (1 + tol) and high >= level * (1 - tol)


def _pages(url_fmt, since, timeout, symbol):
    out, start = [], int(since.timestamp() * 1000)
    for _ in range(20):
        with _urlopen(url_fmt.format(symbol=symbol, start=start), timeout=timeout) as f:
            page = json.load(f)
        out += [(k[0] // 1000, float(k[2]), float(k[3]), float(k[4])) for k in page]
        if len(page) < 1000:
            break
        start = page[-1][0] + 3_600_000
    return out


def perp_1h(since, timeout=15, symbol="BTC"):
    """Binance USDT-M perpetual 1h klines (fapi.binance.com, via binance_doh) from `since` to now, paged like spot_1h."""
    return _pages("https://fapi.binance.com/fapi/v1/klines?symbol={symbol}USDT&interval=1h&limit=1000&startTime={start}",
                  since, timeout, symbol)


def bars_with_source(since, timeout=15, symbol="BTC"):
    """(bars, "perp"|"spot"): perp first (the operator trades it), spot when perp fails or is empty."""
    try:
        bars = perp_1h(since, timeout, symbol)
        if bars:
            return bars, "perp"
    except (OSError, ValueError):
        pass
    return spot_1h(since, timeout, symbol), "spot"


def spot_1h(since, timeout=15, symbol="BTC"):
    """Public Binance spot 1h klines (data-api.binance.vision) from `since` (UTC datetime) to now.
    One call returns at most 1000 bars (~41.6 days), so page forward until the series reaches the present."""
    out, start = [], int(since.timestamp() * 1000)
    for _ in range(20):
        url = (f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}USDT&interval=1h&limit=1000"
               f"&startTime={start}")
        with urllib.request.urlopen(url, timeout=timeout) as f:
            page = json.load(f)
        out += [(k[0] // 1000, float(k[2]), float(k[3]), float(k[4])) for k in page]
        if len(page) < 1000:
            break
        start = page[-1][0] + 3_600_000
    return out


def hit_from(published):
    """First UTC instant a bar may count as a hit: 00:00 of the day after the (date-only) publish date."""
    return datetime.fromisoformat(published[:10]).replace(tzinfo=timezone.utc) + timedelta(days=1)


def mark(lv, bars, now):
    if not bars:
        raise ValueError("no klines returned: cannot price the ladder")
    price = bars[-1][3]
    for x in lv:
        t0 = hit_from(x["published"]).timestamp()
        seg = [b for b in bars if b[0] >= t0]
        x["hit"] = bool(seg) and touched(x["level"], min(b[2] for b in seg), max(b[1] for b in seg))
        x["dist_pct"] = round((x["level"] / price - 1) * 100, 2)
        x["expired"] = cbp.parse_expiry(x["expires_at"]) <= now if x["expires_at"] else False
    return price


def render(lv, price=None, width=90, symbol="BTC"):
    lines = []
    head = f"ANALYST LEVELS (CBP, {len({(x['analyst'], x['video_id']) for x in lv})} {symbol} rows)"
    lines.append(head + (f" | {symbol} spot {price:,.0f}" if price else " | offline: no price"))
    placed = price is None
    for x in lv:
        if not placed and x["level"] < price:
            lines.append(f"  ---- now {price:,.0f} ----")
            placed = True
        tag = ""
        if price is not None:
            tag = f"{x['dist_pct']:+6.2f}% {'HIT ' if x['hit'] else 'open'}"
            if x.get("expired"):
                tag += " exp"
        said = x["said"] if len(x["said"]) <= width else x["said"][:width - 3] + "..."
        lines.append(f"  {x['level']:>9,.0f} {tag:<17} {x['analyst']} {x['published'][5:]} {x['bias'][:4]}: {said}")
    if not placed:
        lines.append(f"  ---- now {price:,.0f} ----")
    return "\n".join(lines)


def hook_block(days=7, band_pct=6.0):
    """Short, for the screenshot notice: live levels within band_pct of spot (3 s fetch; offline = all live levels). Never raises."""
    try:
        now = datetime.now(timezone.utc)
        lv = [x for x in ladder(recent_rows(days, now)) if cbp.parse_expiry(x["expires_at"]) > now]
        if not lv:
            return ""
        price = None
        try:
            since = min(datetime.fromisoformat(x["published"]) for x in lv).replace(tzinfo=timezone.utc)
            price = mark(lv, bars_with_source(since, timeout=3)[0], now)
            lv = [x for x in lv if abs(x["dist_pct"]) <= band_pct]
        except Exception:
            pass
        return render(lv, price, width=60) + chr(10) + "  (all levels: python scripts/dev/analyst_levels.py)"
    except Exception:
        return ""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=10)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--store")
    ap.add_argument("--symbol", default="BTC", type=lambda v: cbp._norm_symbol(v))
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    rows = recent_rows(a.days, now, a.store)
    lv = ladder(rows, a.symbol)
    price, source = None, None
    if not a.offline and lv:
        since = min(datetime.fromisoformat(x["published"]) for x in lv).replace(tzinfo=timezone.utc)
        bars, source = bars_with_source(since, symbol=a.symbol)
        price = mark(lv, bars, now)
    if a.json:
        print(json.dumps(dict(asof=now.isoformat(timespec="seconds"), price=price, source=source, levels=lv), indent=1))
    else:
        print(render(lv, price, symbol=a.symbol) + (f"\n  (source: {source}; touch tol {TOUCH_TOL:.2%})" if source else ""))


if __name__ == "__main__":
    main()
