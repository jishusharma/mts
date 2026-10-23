"""Render the 31 naked charts from pack CSVs only. Usage: python render_charts.py <pack_dir>
Candles + volume, no indicators; one solid line per prior-week POC (blue), VAH/VAL (orange dashed), each drawn over the
week AFTER the week it describes. Context only: rules may use pack columns, never chart-read levels."""
import csv, io, os, sys
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image

FMT = "%Y-%m-%d %H:%M"


def rd(p):
    with open(p) as f:
        return list(csv.DictReader(f))


def bars(pack, tf):
    return [(datetime.strptime(r["open_time_utc"], FMT), *(float(r[k]) for k in ("open", "high", "low", "close", "volume")))
            for r in rd(os.path.join(pack, f"ohlcv_{tf}.csv"))]


def chart(rows, step, wk, title, path):
    fig, (ax, av) = plt.subplots(2, 1, figsize=(11, 6), dpi=72, sharex=True, gridspec_kw={"height_ratios": [4, 1]})
    w = step.total_seconds() / 86400 * 0.7
    for t, o, h, l, c, v in rows:
        col = "#1a9850" if c >= o else "#d73027"
        x = mdates.date2num(t + step / 2)
        ax.vlines(x, l, h, color=col, lw=0.8)
        ax.bar(x, abs(c - o) or 1, bottom=min(o, c), width=w, color=col)
        av.bar(x, v, width=w, color="#777")
    t0, t1 = rows[0][0], rows[-1][0] + step
    for r in wk:
        ws = datetime.strptime(r["period_open_utc"], FMT) + timedelta(days=7)
        we = ws + timedelta(days=7)
        if we <= t0 or ws >= t1:
            continue
        a, b = mdates.date2num(max(ws, t0)), mdates.date2num(min(we, t1))
        ax.hlines(float(r["poc"]), a, b, color="#2166ac", lw=1.2)
        ax.hlines([float(r["vah"]), float(r["val"])], a, b, color="#e08214", lw=1.0, ls="--")
    ax.set_xlim(mdates.date2num(t0), mdates.date2num(t1))
    ax.set_title(title + "  | blue=prior-week POC, orange dashed=VAH/VAL", fontsize=9)
    ax.grid(alpha=0.2); av.grid(alpha=0.2)
    av.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m-%d"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, format="png")
    plt.close(fig)
    im = Image.open(path).convert("P", palette=Image.ADAPTIVE, colors=64)  # shrink; no data change
    im.save(path, optimize=True)


def main(pack):
    out = os.path.join(pack, "charts"); os.makedirs(out, exist_ok=True)
    wk = rd(os.path.join(pack, "levels_weekly.csv"))
    n = 0
    b = bars(pack, "1w"); chart(b, timedelta(days=7), wk, "BTCUSDT 1W 2022-01..2023-06", os.path.join(out, "1w_all.png")); n += 1
    for tf, step in (("1d", timedelta(days=1)), ("12h", timedelta(hours=12))):
        b = bars(pack, tf)
        for y, q in [(2022, 1), (2022, 2), (2022, 3), (2022, 4), (2023, 1), (2023, 2)]:
            s = [x for x in b if x[0].year == y and (x[0].month - 1) // 3 + 1 == q]
            chart(s, step, wk, f"BTCUSDT {tf} {y}Q{q}", os.path.join(out, f"{tf}_{y}Q{q}.png")); n += 1
    b = bars(pack, "4h")
    for y, m in [(2022 + i // 12, i % 12 + 1) for i in range(18)]:
        s = [x for x in b if x[0].year == y and x[0].month == m]
        chart(s, timedelta(hours=4), wk, f"BTCUSDT 4h {y}-{m:02d}", os.path.join(out, f"4h_{y}-{m:02d}.png")); n += 1
    sizes = [os.path.getsize(os.path.join(out, f)) for f in os.listdir(out)]
    print(n, "charts; max", max(sizes), "total", sum(sizes))
    assert n == 31 and max(sizes) < 150_000 and sum(sizes) < 5_000_000


if __name__ == "__main__":
    main(sys.argv[1])
