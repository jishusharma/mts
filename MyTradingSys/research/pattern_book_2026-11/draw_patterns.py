"""Draw the detector's patterns and trendlines on BTCUSDT charts (one PNG per timeframe + the 2013-2026 cycle chart).

Usage: python draw_patterns.py [--out charts]      (needs data/ from fetch_klines.py and the btc_cycles history csv)
Look of the charts: price candles in neutral ink (hollow = up, filled = down, so colour is not the only cue); two hues only:
blue = bullish bias / support, orange = bearish bias / resistance, grey = neutral or already resolved. Numbered circles tie each
drawing to the legend under the chart. Everything is OURS (see detect_patterns.py); the operator checks it by eye.
"""
import argparse
import datetime as dt
import math
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import detect_patterns as dp  # noqa: E402

INK, MUTED, GRID = "#1f2933", "#6b7785", "#e3e7eb"
BULL, BEAR, NEUT, OLD = "#1f6fb2", "#d1541f", "#7a5ea8", "#9aa5b1"
BIAS_COL = {"bull": BULL, "bear": BEAR, "neutral": NEUT}
WINDOW = {"1h": 400, "4h": 400, "1d": 330, "1w": None}
ABBR = {"hammer": "HM", "hanging_man": "HG", "shooting_star": "SS", "bullish_engulfing": "BE", "bearish_engulfing": "XE",
        "morning_star": "MS", "evening_star": "ES", "dark_cloud_cover": "DC", "piercing_line": "PL",
        "three_white_soldiers": "3W", "three_black_crows": "3B", "doji": "DJ"}


def num(t):
    return mdates.date2num(dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc))


def px(v, _=None):
    return f"{v:,.0f}"


def candles(ax, bars, i0):
    n = len(bars)
    w = 0.6 * (num(bars[1]["t"]) - num(bars[0]["t"])) if n > 1 else 0.6
    for b in bars[i0:]:
        x = num(b["t"]) + w / 1.2
        up = b["c"] >= b["o"]
        ax.vlines(x, b["l"], b["h"], color=INK, lw=0.8, zorder=2)
        lo, hi = min(b["o"], b["c"]), max(b["o"], b["c"])
        ax.add_patch(Rectangle((x - w / 2, lo), w, max(hi - lo, (b["h"] - b["l"]) * 0.01), fc="white" if up else INK, ec=INK,
                               lw=0.8, zorder=3))
    return w


def draw_pattern(ax, bars, r, k, active, xshift):
    col = BIAS_COL[r["bias"]] if active else OLD
    lw = 1.8 if active else 1.0
    pts = r["points"]
    xs = [num(p["t"]) + xshift for p in pts]
    ys = [p["price"] for p in pts]
    if r["pattern"].startswith(("double", "head")):
        ax.plot(xs, ys, color=col, lw=lw, marker="o", ms=5 if active else 3.5, zorder=5)
    else:
        ax.scatter(xs, ys, color=col, s=22 if active else 10, zorder=5)
    for ln in r["lines"]:
        i2 = ln.get("ext", ln["i2"])
        x1, x2 = num(bars[ln["i1"]]["t"]) + xshift, num(bars[min(i2, len(bars) - 1)]["t"]) + xshift
        ax.plot([x1, x2], [ln["p1"], dp.line_at(ln, min(i2, len(bars) - 1))], color=col, lw=lw, zorder=4)
    if r["pattern"].startswith("double") and r["neck"]:
        ax.hlines(r["neck"], xs[0], xs[2] + (xs[2] - xs[0]) * 0.5, color=col, lw=lw, ls="--", zorder=4)
    if active and r["target"]:
        ax.hlines(r["target"], xs[-1], xs[-1] + (xs[-1] - xs[0]) * 0.35 + 1e-6, color=col, lw=1.2, ls=":", zorder=4)
        ax.text(xs[-1] + (xs[-1] - xs[0]) * 0.36 + 1e-6, r["target"], f"({k}) target {r['target']:,.0f}", color=col, fontsize=7.5, va="center")
    ax.annotate(str(k), (xs[0], ys[0]), xytext=(0, 11 if r["bias"] != "bull" else -11), textcoords="offset points", ha="center",
                va="center", fontsize=9, color="white", zorder=6,
                bbox=dict(boxstyle="circle,pad=0.25", fc=col, ec="none"))


def legend_lines(items, tf):
    out = []
    for k, r in items:
        trig = f"{r['trigger']:,.0f}" if r["trigger"] else "-"
        tgt = f"{r['target']:,.0f}" if r["target"] else "-"
        inv = f"{r['invalid']:,.0f}" if r["invalid"] else "-"
        out.append(f"({k}) {r['pattern'].replace('_', ' ')}  x{r['scale']:g}  {r['status'].replace('_', ' ')}   "
                   f"trigger {trig} | target {tgt} | invalid {inv}   {r['note']}")
    return out


def chart(tf, out_dir, turns=None, history=None):
    bars = dp.load_csv(tf)
    n = len(bars)
    win = WINDOW[tf]
    i0 = max(0, n - win) if win else 0
    res = dp.detect_chart_patterns(bars, tf)
    active = [r for r in res if dp.is_active(r, n, tf)]
    old = [r for r in res if not dp.is_active(r, n, tf) and r["end_i"] >= i0 and r["status"] != "expired"]
    old.sort(key=lambda r: -r["end_i"])
    old = old[:3 if tf != "1w" else 8]
    shown = active + old
    figh = 7.2 + 0.26 * max(4, len(shown) + 8)
    fig = plt.figure(figsize=(13.5, figh), dpi=110)
    gs = fig.add_gridspec(2, 1, height_ratios=[7.2, 0.26 * max(4, len(shown) + 8)], hspace=0.06)
    ax = fig.add_subplot(gs[0])
    tx = fig.add_subplot(gs[1])
    tx.axis("off")
    w = candles(ax, bars, i0)
    xshift = w / 1.2
    lo = min(b["l"] for b in bars[i0:])
    hi = max(b["h"] for b in bars[i0:])
    items, k = [], 1
    for r in shown:
        if r["end_i"] < i0 - 5 and r["points"][0]["i"] < i0 - 400:
            continue
        draw_pattern(ax, bars, r, k, r in active, xshift)
        items.append((k, r))
        k += 1
    # trendlines: strip rule (what the live-aid strip will show) and the tested research detector
    tl_txt = []
    for side, col in (("support", BULL), ("resistance", BEAR)):
        t = dp.strip_trendline(bars, side)
        if t:
            x1, x2 = num(bars[max(t["i1"], i0)]["t"]) + xshift, num(bars[-1]["t"]) + xshift
            i1 = max(t["i1"], i0)
            ax.plot([x1, x2], [dp.line_at(t, i1), t["value"]], color=col, lw=1.6, ls="-" if t["touches"] == 3 else (0, (5, 3)), zorder=4)
            ax.text(x2, t["value"], f" {side[:3].upper()} {t['touches']}t {t['slope_pct_per_bar']:+.3f}%/bar, {t['dist_pct']:+.1f}% to price",
                    color=col, fontsize=8.5, va="center")
            tl_txt.append(f"strip {side} {t['touches']}t slope {t['slope_pct_per_bar']:+.3f}%/bar value {t['value']:,.0f} price is {t['dist_pct']:+.1f}% away")
    try:
        for c in dp.core_trendlines(bars, tf):
            if c["i1"] < i0 - 400 or abs(c["dist_pct"]) > 30:
                continue
            col = BULL if c["side"] == "support" else BEAR
            ax.plot([num(bars[c["i1"]]["t"]) + xshift, num(bars[-1]["t"]) + xshift], [c["p1"], c["value"]], color=col, lw=1.0, ls=":",
                    zorder=3)
            tl_txt.append(f"core {c['side']} (log, wick, arm {c['arm']}) value {c['value']:,.0f} price is {c['dist_pct']:+.1f}% away")
    except Exception as e:   # the research detector is optional for the picture
        tl_txt.append(f"core lines unavailable: {e}")
    # candle patterns on the last bars of the window
    atr = dp.atr_pct(bars)
    ev = [e for e in dp.candle_patterns(bars) if e["trend_ok"] and e["bias"] != "neutral" and e["i"] >= n - {"1h": 60, "4h": 45, "1d": 40, "1w": 30}[tf]]
    for e in ev:
        b = bars[e["i"]]
        up = e["bias"] == "bull"
        ax.annotate(ABBR[e["name"]], (num(b["t"]) + xshift, b["l"] if up else b["h"]), xytext=(0, -13 if up else 13),
                    textcoords="offset points", ha="center", fontsize=7.5, color=BULL if up else BEAR)
    c = bars[-1]["c"]
    ax.axhline(c, color=MUTED, lw=0.7, ls="-", zorder=1)
    ax.text(ax.get_xlim()[0], c, f"  last {c:,.0f}", color=MUTED, fontsize=8.5, va="bottom")
    ax.set_yscale("log")
    pad = (hi / lo) ** 0.04
    ax.set_ylim(lo / pad, hi * pad)
    cand = [3e3, 4e3, 5e3, 6e3, 7e3, 8e3, 10e3, 12e3, 15e3, 20e3, 25e3, 30e3, 40e3, 50e3, 55e3, 60e3, 65e3, 70e3, 75e3, 80e3, 85e3, 90e3,
            100e3, 110e3, 120e3, 130e3]
    ticks = [v for v in cand if ax.get_ylim()[0] <= v <= ax.get_ylim()[1]]
    while len(ticks) > 9:
        ticks = ticks[::2]
    ax.set_yticks(ticks)
    ax.yaxis.set_major_formatter(FuncFormatter(px))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.grid(color=GRID, lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9)
    fmt = {"1h": "%d %b %H:%M", "4h": "%d %b", "1d": "%b %Y", "1w": "%Y"}[tf]
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))
    ax.set_xlim(num(bars[i0]["t"]) - w, num(bars[-1]["t"]) + (num(bars[-1]["t"]) - num(bars[i0]["t"])) * 0.30)
    t_last = dt.datetime.fromtimestamp(bars[-1]["t"] / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ax.set_title(f"BTCUSDT {tf}  |  last closed bar {t_last}  |  log price  |  {len(active)} active, {len(old)} recent resolved",
                 loc="left", fontsize=12, color=INK, fontweight="bold")
    # Bible turns on the weekly chart: the daily-history detections, drawn in their own dates
    if turns:
        for label, pat, rec in turns:
            if rec is None or num(rec["points"][0]["t"]) < ax.get_xlim()[0]:
                continue
            col = BEAR if pat == "double_top" else BULL
            xs = [num(p["t"]) + xshift for p in rec["points"]]
            ys = [p["price"] for p in rec["points"]]
            ax.plot(xs, ys, color=col, lw=2.0, marker="o", ms=6, zorder=6)
            ax.hlines(rec["neck"], xs[0], xs[2] + (xs[2] - xs[0]) * 0.4, color=col, lw=1.4, ls="--", zorder=5)
            ax.annotate(label, (xs[0] if pat == "double_top" else xs[2], ys[0] if pat == "double_top" else ys[2]),
                        xytext=(0, 16 if pat == "double_top" else -18), textcoords="offset points", ha="center", fontsize=9.5,
                        color=col, fontweight="bold")
    lines = legend_lines(items, tf)
    head = ["Numbered circles = patterns (orange bear, blue bull, purple neutral, grey = already resolved). Dashed = neckline. Dotted = target.",
            "Trend lines: solid/dashed blue = strip support, orange = strip resistance (3t = 3 touches within 0.2%, dashed = 2 touches); dotted = research detector.",
            "Letters on candles: HM hammer, HG hanging man, SS shooting star, BE bull engulfing, XE bear engulfing, MS/ES morning/evening star, DC dark cloud, PL piercing, 3W/3B soldiers/crows."]
    body = head + [""] + tl_txt + [""] + lines
    tx.text(0.0, 1.0, "\n".join(body), transform=tx.transAxes, va="top", ha="left", fontsize=8.6, color=INK, family="DejaVu Sans")
    out = out_dir / f"btc_{tf}_patterns.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out, len(active), len(old)


def cycle_chart(out_dir, turns):
    h = dp.load_history()
    fig, ax = plt.subplots(figsize=(13.5, 7.4), dpi=110)
    xs = [num(b["t"]) for b in h]
    ax.plot(xs, [b["c"] for b in h], color=INK, lw=1.0, zorder=2)
    ax.fill_between(xs, [b["l"] for b in h], [b["h"] for b in h], color=GRID, zorder=1)
    for label, pat, rec in turns:
        if rec is None:
            continue
        col = BEAR if pat == "double_top" else BULL
        pxs = [num(p["t"]) for p in rec["points"]]
        pys = [p["price"] for p in rec["points"]]
        ax.plot(pxs, pys, color=col, lw=2.0, marker="o", ms=6, zorder=5)
        ax.hlines(rec["neck"], pxs[0], pxs[2] + (pxs[2] - pxs[0]) * 0.35, color=col, lw=1.3, ls="--", zorder=4)
        ax.annotate(f"{label}\n{pys[0]:,.0f} / {pys[2]:,.0f}", (pxs[1], pys[1] if pat == "double_bottom" else max(pys[0], pys[2])),
                    xytext=(0, 20 if pat == "double_top" else -34), textcoords="offset points", ha="center", fontsize=9.5,
                    color=col, fontweight="bold")
    # the Bible's 2015 pair is outside the detector's tolerance: marked, not claimed
    d15 = [(num(int(dt.datetime(2015, 1, 15, tzinfo=dt.timezone.utc).timestamp() * 1000)), 172),
           (num(int(dt.datetime(2015, 8, 25, tzinfo=dt.timezone.utc).timestamp() * 1000)), 211)]
    ax.plot([d15[0][0], d15[1][0]], [d15[0][1], d15[1][1]], color=OLD, lw=1.4, marker="o", ms=5, ls="--", zorder=4)
    ax.annotate("2015 bottom (Bible)\n172 / 211: 20% apart,\nnot called by the detector", d15[1], xytext=(10, -48), textcoords="offset points",
                fontsize=8.5, color=MUTED)
    ax.set_yscale("log")
    ax.set_ylim(60, 600000)
    ax.set_yticks([100, 1000, 10000, 100000])
    ax.yaxis.set_major_formatter(FuncFormatter(px))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(num(h[0]["t"]) + 365 * 3.5, num(h[-1]["t"]) + 120)
    ax.grid(color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.set_title("BTC daily 2013-2026 (log): Bible cycle turns as the detector reads them (orange top, blue bottom, dashed neckline)", loc="left", fontsize=10.5, color=INK, fontweight="bold")
    out = out_dir / "btc_cycle_turns.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "charts"))
    a = ap.parse_args()
    out_dir = pathlib.Path(a.out)
    out_dir.mkdir(exist_ok=True)
    hist = dp.load_history()
    turns = [(lab, pat, dp.find_turn(hist, pat, d1, d2)) for lab, pat, d1, d2 in dp.BIBLE_TURNS]
    print(cycle_chart(out_dir, turns))
    for tf in dp.TFS:
        print(chart(tf, out_dir, turns if tf == "1w" else None))


if __name__ == "__main__":
    main()
