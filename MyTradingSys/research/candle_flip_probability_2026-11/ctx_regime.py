"""Regime mix of the two study windows, from research_kit.regime_tag (Malkan weekly/monthly RSI 60/40 band + daily SMA200 side).
Uses public Binance spot 1d / 1w / 1M klines from 2017-08 (warm-up for the monthly RSI); no outcome of the flip study is read.
Writes regime_mix.txt (one line per window)."""
import json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

DAY = 86400000
CUT = 1735689600000  # 2025-01-01T00:00Z
START = 1704067200000  # 2024-01-01T00:00Z
URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=%s&limit=1000&startTime=%d"


def klines(iv):
    out, t = [], 1502928000000  # 2017-08-17
    while True:
        with urllib.request.urlopen(URL % (iv, t), timeout=30) as r:
            b = json.loads(r.read())
        if not b:
            break
        out += [(k[0], float(k[4])) for k in b]
        t = b[-1][0] + 1
        if len(b) < 1000:
            break
    return out


def rsi_series(bars):
    r = rsi_core([c for _, c in bars], 14)
    keep = [k for k in range(len(bars) - 1) if r[k] is not None]  # last bar dropped: its close time is unknown
    return [bars[k + 1][0] for k in keep], [r[k] for k in keep]


def week_starts(lo, hi):
    d0 = lo // DAY
    d0 += (4 - d0) % 7
    return [d * DAY for d in range(d0, hi // DAY, 7)]


def main():
    d, w, m = klines("1d"), klines("1w"), klines("1M")
    daily = ([t + DAY for t, _ in d], [c for _, c in d])
    wk, mo = rsi_series(w), rsi_series(m)
    import time
    now = int(time.time() * 1000)
    lines = []
    for name, lo, hi in (("fit 2024-01-01..2025-01-01", START, CUT), ("score 2025-01-01..now", CUT, now)):
        tags = [rk.regime_tag(t, daily, wk, mo)["regime"] for t in week_starts(lo, hi)]
        lines.append("Regime mix (%s): %s" % (name, rk.regime_mix_line(tags)))
    (HERE / "regime_mix.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
