"""G3 trend-line marking pack: seeded windows, a causal pre-filter, blind candle charts, marking sheets.

Question the readers answer: "is there an obvious legitimate trend line on this chart?" (READER_PROTOCOL.md section 4).
DEV only. Every number here is OURS (a definition or a window-selection filter), fixed before any outcome was read.
Structure copied from research/g3_marks_2026-10-16/g3_pack.py with its 2026-10-17 blindness fixes: ids <unit>-NN, no clock
labels, the same overlays on every chart (none: candles and volume only), selection rule only in the closed key folder.
Charts are drawn through Windows GDI+ (render_png.ps1); the geometry is built here and is pure Python.

  python g3_pack.py counts              # eligible edges and pre-filter candidates per unit (no outcomes involved)
  python g3_pack.py build               # WINDOWS.csv, MARKING_SHEET_reader{1,2}.csv, ANSWER_KEY_CLOSED/KEY.csv
  python g3_pack.py draw --out DIR      # one PNG per window, rebuilt from WINDOWS.csv (PNGs are not committed)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import subprocess
import tempfile
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 20261017
N_HALF = 10
MIN, HOUR, DAY = 60_000, 3_600_000, 86_400_000
KLINES_1M = r"F:\MTS\data\tom_raw\klines"
DAILY_DIR = r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps\backtest\raw_1d\klines"
# standard DEV: 1m store from 2022-01-01 (DEV_EXT daily from 2021-03-01), last day 2024-06-30; VALIDATION/HOLDOUT never opened
DEV_LAST = date(2024, 6, 30)
H4_FIRST, H4_EDGE0 = date(2022, 1, 1), date(2022, 3, 1)
D1_FIRST, D1_EDGE0 = date(2020, 1, 1), date(2021, 3, 1)

# code: label, timeframe, bars shown, minimum spacing between windows in bars
UNITS = {
    "TL4H": dict(label="TL-4H", tf="4h", shown=200, space=40),
    "TL1D": dict(label="TL-1D", tf="1d", shown=180, space=20),
}
K_SWING, ATR_N = 3, 14                 # contract P3, L-block ATR length (OURS)
SPAN_MIN, SPAN_MAX = 10, 200           # contract L3, L4 (OURS)
PEN_ATR, TOUCH_ATR = 0.10, 0.25        # contract L6, E5 (OURS)
NEAR_ATR = 3.0                         # pre-filter only: line within 3 average ranges of the last close (OURS)


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ms_of(d):
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)


# ---------------------------------------------------------------- data (DEV fences: a date loop and a timestamp fence)
def load_4h(klines=KLINES_1M):
    """Closed 4h bars from the 1m store, 2022-01-01..2024-06-30; a bucket needs all 240 minutes."""
    end_ms = ms_of(DEV_LAST) + DAY
    out, cur, ms4 = [], None, 4 * HOUR
    d = H4_FIRST
    ym_seen = set()
    for f in sorted(Path(klines).glob("BTCUSDT-1m-????-??.csv")):
        y, m = (int(x) for x in f.stem.split("-")[2:4])
        if (y, m) < (H4_FIRST.year, H4_FIRST.month) or (y, m) > (DEV_LAST.year, DEV_LAST.month):
            continue  # file-level fence: nothing after 2024-06 is ever opened
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t >= end_ms:
                    continue
                b = t // ms4 * ms4
                if cur is None or cur["t"] != b:
                    if cur and cur["n"] == 240:
                        out.append(cur)
                    cur = dict(t=b, o=float(r[1]), h=float(r[2]), l=float(r[3]), c=float(r[4]), vol=0.0, n=0)
                cur["h"], cur["l"], cur["c"] = max(cur["h"], float(r[2])), min(cur["l"], float(r[3])), float(r[4])
                cur["vol"] += float(r[5])
                cur["n"] += 1
    if cur and cur["n"] == 240:
        out.append(cur)
    return out


def load_daily(dir_path=DAILY_DIR):
    bars, end = {}, ms_of(DEV_LAST) + DAY
    for p in sorted(Path(dir_path).glob("BTCUSDT-1d-*.csv")):
        with open(p, newline="") as f:
            for row in csv.reader(f):
                if row and row[0].isdigit() and int(row[0]) < end:  # DEV fence
                    bars[int(row[0])] = dict(t=int(row[0]), o=float(row[1]), h=float(row[2]), l=float(row[3]), c=float(row[4]), vol=float(row[5]))
    return [bars[k] for k in sorted(bars)]


# ---------------------------------------------------------------- pre-filter (OURS; causal: bars up to index i only)
def atr_sma(B, j):
    """Plain SMA of true range over ATR_N bars ending at j (contract: not Wilder)."""
    if j < ATR_N:
        return None
    return sum(max(B[q]["h"] - B[q]["l"], abs(B[q]["h"] - B[q - 1]["c"]), abs(B[q]["l"] - B[q - 1]["c"])) for q in range(j - ATR_N + 1, j + 1)) / ATR_N


def swings(B, i, side, k=K_SWING):
    """Confirmed swing indices j with j + k <= i: strict extremum against k bars on both sides (ties disqualify)."""
    key = "l" if side == "support" else "h"
    out = []
    for j in range(max(k, i - SPAN_MAX - 60), i - k + 1):
        v = B[j][key]
        side_vals = [B[q][key] for q in list(range(j - k, j)) + list(range(j + 1, j + k + 1))]
        if (side == "support" and all(v < x for x in side_vals)) or (side == "resistance" and all(v > x for x in side_vals)):
            out.append(j)
    return out


def line_ok(B, i, side, ia, ib, ics):
    """True if swings ia, ib define a legitimate line at decision bar i with a third confirmed swing on it."""
    key = "l" if side == "support" else "h"
    pa, pb = B[ia][key], B[ib][key]
    if (side == "support" and pb <= pa) or (side == "resistance" and pb >= pa) or not SPAN_MIN <= ib - ia <= SPAN_MAX:
        return False
    atr = atr_sma(B, ib)
    if not atr or abs(pb - pa) <= 0.25 * atr:
        return False  # flat pair: horizontal family, not a trend line here
    sl = (math.log(pb) - math.log(pa)) / (ib - ia)
    L = lambda j: math.exp(math.log(pa) + sl * (j - ia))
    sgn = 1 if side == "support" else -1
    for j in range(ia, ib + 1):  # strict penetration test over the anchor span
        if sgn * (B[j][key] - L(j)) < -PEN_ATR * atr or sgn * (B[j]["c"] - L(j)) < 0:
            return False
    if any(sgn * (B[j]["c"] - L(j)) < 0 for j in range(ib + 1, i + 1)):
        return False  # already broken at the decision bar
    near = atr_sma(B, i)  # the line must be live: price within NEAR_ATR current ranges of it at the decision bar
    if not near or abs(B[i]["c"] - L(i)) > NEAR_ATR * near:
        return False
    return any(ic > ib and abs(B[ic][key] - L(ic)) <= TOUCH_ATR * atr for ic in ics)


def pf_line(B, i):
    """'support' / 'resistance' / 'both' when a three-swing legitimate line exists at bar i, else None."""
    if i < 2 * K_SWING + ATR_N + 20:
        return None
    found = set()
    for side in ("support", "resistance"):
        sw = swings(B, i, side)
        for x, ib in enumerate(sw):
            for ia in sw[:x]:
                if line_ok(B, i, side, ia, ib, sw[x + 1:]):
                    found.add(side)
                    break
            if side in found:
                break
    return "both" if len(found) == 2 else next(iter(found), None)


# ---------------------------------------------------------------- window selection (seeded)
def spaced_pick(order, taken, space, n):
    got = []
    for i in order:
        if len(got) >= n:
            break
        if all(abs(i - j) >= space for j in taken + got):
            got.append(i)
    return got


def pick(code, eligible, tag_of, quota=None, seed=SEED):
    """Half enriched (pre-filter true at the edge, seeded draw), half random; spaced; returns records unsorted."""
    u = UNITS[code]
    rng = random.Random(f"{seed}-{code}")
    cands = [i for i in eligible if tag_of(i)]
    rng.shuffle(cands)
    taken, recs = [], []
    quota = quota or {"*": N_HALF}
    for tag, n in quota.items():
        pool = [i for i in cands if tag == "*" or tag_of(i) == tag]
        got = spaced_pick(pool, taken, u["space"], n)
        taken += got
        recs += [dict(edge=i, half="enriched", tag=tag_of(i)) for i in got]
    rest = list(eligible)
    rng.shuffle(rest)
    got = spaced_pick(rest, taken, u["space"], N_HALF)
    recs += [dict(edge=i, half="random", tag=tag_of(i) or "") for i in got]
    rng.shuffle(recs)
    for k, r in enumerate(recs, 1):
        r["window_id"] = f"{code}-{k:02d}"
    return recs




# ---------------------------------------------------------------- drawing geometry (blind: no dates, % axis)
W_PX, H_PX, X0, X1 = 1400, 860, 70, 1300
GREEN, RED, GREY, TXT = "#39bd93", "#e66c6c", "#6b7a88", "#d7dee5"


def nice_step(span):
    for s in (0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 50, 100):
        if span / s <= 9:
            return s
    return 200


class Chart:
    def __init__(self, title, n):
        self.p = [dict(k="rect", x=0, y=0, w=W_PX, h=H_PX, c="#101820")]
        self.n, self.title = n, title
        self.text(12, 8, title, 14)

    def text(self, x, y, s, size=11, c=TXT):
        self.p.append(dict(k="text", x=x, y=y, s=s, c=c, size=size))

    def x(self, k):
        return X0 + (k + 0.5) * (X1 - X0) / self.n

    def panel(self, top, height, lo, hi, label, fmt="{:.2f}", step=None):
        self.top, self.h, self.lo, self.hi = top, height, lo, hi
        self.p.append(dict(k="line", pts=[[X0, top], [X1, top], [X1, top + height], [X0, top + height], [X0, top]], c="#2a3744", w=1))
        self.text(X0 + 4, top + 2, label, 11, GREY)
        step = step or (hi - lo) / 6
        v = (lo // step + 1) * step
        while v < hi:
            self.line([(X0, self.y(v)), (X1, self.y(v))], "#1b2733")
            self.text(8, self.y(v) - 7, fmt.format(v), 10, GREY)
            v += step

    def y(self, v):
        return self.top + self.h - (v - self.lo) / (self.hi - self.lo) * self.h

    def line(self, pts, c, w=1):
        pts = [[round(a, 1), round(b, 1)] for a, b in pts]
        if len(pts) >= 2:
            self.p.append(dict(k="line", pts=pts, c=c, w=w))

    def series(self, vals, c, w=1):
        run = []
        for k, v in enumerate(vals):
            if v is None:
                self.line(run, c, w)
                run = []
            else:
                run.append((self.x(k), self.y(v)))
        self.line(run, c, w)

    def seg(self, k0, k1, v, c, label=""):
        if not self.top <= self.y(v) <= self.top + self.h:
            return  # outside the visible price range: not drawn
        self.line([(self.x(k0) - 3, self.y(v)), (self.x(k1) + 3, self.y(v))], c, 1)
        if label:
            self.text(self.x(k1) + 4, self.y(v) - 7, label, 10, c)

    def bars(self, vals, base, color_of):
        w = max(1.0, (X1 - X0) / self.n * 0.6)
        for k, v in enumerate(vals):
            y0, y1 = self.y(base), self.y(v)
            self.p.append(dict(k="rect", x=round(self.x(k) - w / 2, 1), y=round(min(y0, y1), 1), w=round(w, 1), h=max(1.0, round(abs(y1 - y0), 1)), c=color_of(k, v)))


def draw_price(ch, vis, ref, top, height, hmargin=0.0):
    pct = lambda p: (p / ref - 1) * 100
    lo, hi = pct(min(b["l"] for b in vis)), pct(max(b["h"] for b in vis))
    pad = (hi - lo) * 0.04 or 0.1
    lo, hi = lo - pad, hi + pad
    ch.panel(top, height, lo, hi, "price, % from last close", "{:+.2f}%", nice_step(hi - lo))
    w = max(1.0, (X1 - X0) / ch.n * 0.6)
    for k, b in enumerate(vis):
        col = GREEN if b["c"] >= b["o"] else RED
        ch.line([(ch.x(k), ch.y(pct(b["h"]))), (ch.x(k), ch.y(pct(b["l"])))], col, 1)
        y0, y1 = ch.y(pct(b["o"])), ch.y(pct(b["c"]))
        ch.p.append(dict(k="rect", x=round(ch.x(k) - w / 2, 1), y=round(min(y0, y1), 1), w=round(w, 1), h=max(1.0, round(abs(y1 - y0), 1)), c=col))
    return pct



def render(jobs, ps1=HERE / "render_png.ps1", batch=20):
    with tempfile.TemporaryDirectory() as td:  # primitives never land in the repo folder
        for s in range(0, len(jobs), batch):
            tmp = Path(td) / f"render_{s}.json"
            tmp.write_text(json.dumps([dict(out=str(j["out"]), w=W_PX, h=H_PX, prims=j["prims"]) for j in jobs[s:s + batch]]), encoding="utf-8")
            subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1), str(tmp)], check=True)




# ---------------------------------------------------------------- units, chart, outputs
def unit_series(code, h4, daily):
    u = UNITS[code]
    B = h4 if u["tf"] == "4h" else daily
    lo = ms_of(H4_EDGE0 if u["tf"] == "4h" else D1_EDGE0)
    hi = ms_of(DEV_LAST)
    elig = [i for i, b in enumerate(B) if lo <= b["t"] <= hi + DAY and i >= u["shown"]]
    return B, elig


def edge_end(code, B, i):
    return B[i]["t"] + (4 * HOUR if UNITS[code]["tf"] == "4h" else DAY)


def build_windows(h4, daily):
    recs = []
    for code in UNITS:
        B, elig = unit_series(code, h4, daily)
        for r in pick(code, elig, lambda i, B=B: pf_line(B, i)):
            recs.append(dict(r, unit=code, end=edge_end(code, B, r["edge"])))
    return recs


def tl_chart(code, B, i, blind_id):
    """Candles + volume only, identical for every window: nothing drawn depends on the pre-filter or on bars after i."""
    u = UNITS[code]
    n = u["shown"]
    if i - n + 1 < 0:
        raise ValueError("window starts before the first bar")
    vis = B[i - n + 1:i + 1]
    ch = Chart(f"{blind_id} | {u['label']} | BTCUSDT {u['tf']} | last closed bar = right edge (offset 0) | dates hidden", n)
    pct = draw_price(ch, vis, vis[-1]["c"], 36, 600)
    for k in range(0, n, 20):  # bar offsets from the right edge, never a clock time or a date
        ch.text(ch.x(k) - 8, ch.top + ch.h + 2, str(k - n + 1), 10, GREY)
    ch.panel(36 + 600 + 24, 110, 0, max(b["vol"] for b in vis) * 1.05, "volume (BTC)", "{:.0f}")
    ch.bars([b["vol"] for b in vis], 0, lambda k, v: GREEN if vis[k]["c"] >= vis[k]["o"] else RED)
    ch.text(12, H_PX - 18, "Offset 0 = last closed bar. Mark: is there an obvious legitimate trend line? Give its anchor bar offsets.", 10, GREY)
    return ch


SHEET_COLS = ["window_id", "row", "reader", "obvious_line", "side", "anchor_offsets", "note"]


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def cmd_build(args):
    recs = build_windows(load_4h(args.klines), load_daily(args.daily))
    order = {c: n for n, c in enumerate(UNITS)}
    recs.sort(key=lambda r: (order[r["unit"]], r["window_id"]))
    win = [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], timeframe=UNITS[r["unit"]]["tf"], bars_shown=UNITS[r["unit"]]["shown"],
                right_edge_utc=iso(r["end"]), seed=f"{SEED}-{r['unit']}") for r in recs]
    write_csv(HERE / "WINDOWS.csv", list(win[0]), win)
    key = [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], half=r["half"], prefilter_tag=r["tag"], right_edge_utc=iso(r["end"])) for r in recs]
    (HERE / "ANSWER_KEY_CLOSED").mkdir(exist_ok=True)
    write_csv(HERE / "ANSWER_KEY_CLOSED" / "KEY.csv", list(key[0]), key)
    for n, who in ((1, "operator"), (2, "claude")):
        write_csv(HERE / f"MARKING_SHEET_reader{n}_{who}.csv", SHEET_COLS,
                  [dict(window_id=r["window_id"], row=UNITS[r["unit"]]["label"], reader=f"reader{n}_{who}") for r in recs])
    sha = hashlib.sha256((HERE / "ANSWER_KEY_CLOSED" / "KEY.csv").read_bytes()).hexdigest()
    print(f"windows={len(recs)} key_sha256={sha}")
    per = defaultdict(lambda: defaultdict(int))
    for r in recs:
        per[UNITS[r["unit"]]["label"]][r["half"]] += 1
    for k, v in per.items():
        print(k, dict(v))


def cmd_counts(args):
    h4, daily = load_4h(args.klines), load_daily(args.daily)
    for code in UNITS:
        B, elig = unit_series(code, h4, daily)
        tags = [pf_line(B, i) for i in elig]
        print(code, "bars", len(B), "eligible", len(elig), "candidates", sum(1 for t in tags if t), {t: tags.count(t) for t in set(tags) if t})


def cmd_draw(args):
    h4, daily = load_4h(args.klines), load_daily(args.daily)
    label_to_code = {u["label"]: c for c, u in UNITS.items()}
    jobs = []
    Path(args.out).mkdir(parents=True, exist_ok=True)
    for w in csv.DictReader(open(HERE / "WINDOWS.csv", encoding="utf-8")):
        code = label_to_code[w["row"]]
        B = h4 if UNITS[code]["tf"] == "4h" else daily
        end = int(datetime.strptime(w["right_edge_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000)
        i = next(k for k in range(len(B) - 1, -1, -1) if edge_end(code, B, k) == end)
        jobs.append(dict(out=Path(args.out) / f"{w['window_id']}.png", prims=tl_chart(code, B, i, w["window_id"]).p))
    render(jobs)
    print(f"drawn={len(jobs)} -> {args.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["counts", "build", "draw"])
    ap.add_argument("--klines", default=KLINES_1M)
    ap.add_argument("--daily", default=DAILY_DIR)
    ap.add_argument("--out", default=r"F:\MTS\data\g3_trendline_pack_2026-10-17\charts")
    a = ap.parse_args()
    {"counts": cmd_counts, "build": cmd_build, "draw": cmd_draw}[a.cmd](a)
