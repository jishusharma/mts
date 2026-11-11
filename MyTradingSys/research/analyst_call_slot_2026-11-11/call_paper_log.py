"""Analyst-call paper slot logger (PREREG.md, frozen). Paper only: NO order, NO account, NO scheduler, NO loop.

Three arms per PREREG: `setup` (call zone + trigger T1 RSI divergence or T2 flow turn inside 16 bars of the touch), `placebo_a`
(zone touch, no trigger), `placebo_b` (trigger more than 1 % away from every live zone). Costs only from backtest/fees.py.
State comes from the journal (append-only jsonl in runtime_data/, git-ignored); every poll recomputes from closed bars, so a
restart or a repeated poll writes nothing twice. Fails closed (writes nothing) on bad or short data. Never raises from step().
Usage: python call_paper_log.py --once [--journal PATH] [--calls PATH]
"""
import argparse
import datetime as dt
import json
import math
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest import fees  # noqa: E402
from MyTradingSys.backtest.layers.alerts.live_rsi_divergence import rsi_divergence_layer  # noqa: E402

PARAMS_ID = "analyst_call_slot_2026-11-11"
SOURCE = "layer:call:where_when_size"
STEP = 900000
BAND = 0.0025            # single price -> zone of 25 bp each side
WINDOW = 16              # bars from the touch bar in which a trigger counts (4 h)
FLOW_LOOKBACK = 3
MIN_STOP = 0.0040        # EDGE_PLAN a
RR = 2.0
HORIZON = 96             # 24 h
AWAY = 0.01              # placebo B: more than 1 % from every live zone
B_STOP_BARS = 10
LIFE_MS = 7 * 86400000
MIN_BARS = 200
FETCH_BARS = 3000
STOP_N = 30
JOURNAL_DEFAULT = str(ROOT / "runtime_data/analyst_call_forward.jsonl")
CALLS_DEFAULT = str(HERE / "calls.jsonl")
URL = "https://data-api.binance.vision/api/v3/klines"
SIDE = {"long": 1, "short": -1}


def _err(msg):
    print(json.dumps({"key": "call_paper_log", "error": msg}), file=sys.stderr, flush=True)


def clean(bars):
    last = None
    for b in bars:
        for k in ("o", "h", "l", "c"):
            v = b.get(k)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
                return False
        d, t = b.get("d"), b.get("t")
        if isinstance(d, bool) or not isinstance(d, (int, float)) or not math.isfinite(d):
            return False
        if isinstance(t, bool) or not isinstance(t, int) or (last is not None and t - last != STEP):
            return False
        if b["h"] < max(b["o"], b["c"]) or b["l"] > min(b["o"], b["c"]):
            return False
        last = t
    return True


def load_calls(path):
    """Valid call rows only. A single `level` becomes a 25 bp zone. Bad rows are dropped (reported on stderr)."""
    out, p = [], Path(path)
    if not p.exists():
        return out
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
            side = r["side"]
            if "level" in r:
                lo, hi = float(r["level"]) * (1 - BAND), float(r["level"]) * (1 + BAND)
            else:
                lo, hi = float(r["lo"]), float(r["hi"])
            t0 = int(r["t_logged"])
            exp = int(r.get("expires") or t0 + LIFE_MS)
            if side not in SIDE or not (0 < lo <= hi) or not math.isfinite(hi) or exp <= t0:
                raise ValueError("bad field")
            out.append({"id": str(r["id"]), "analyst": str(r.get("analyst", "")), "side": side, "lo": lo, "hi": hi,
                        "t_logged": t0, "expires": exp})
        except (KeyError, TypeError, ValueError) as exc:
            _err(f"calls line {n + 1} dropped: {exc!r}"[:160])
    return out


def cost_frac(kind):
    f = fees.FEES_ALL_TAKER
    return f["entry"] + f[{"stop": "stop", "target": "target", "time": "timeout"}[kind]] + fees.SLIPPAGE_RT_S13


def simulate(d, bars, e, raw_stop):
    """Trade entered at the open of bars[e]. Stop moved out to MIN_STOP when nearer (or on the wrong side). Stop before target
    in one bar. Returns None while still open (fewer than HORIZON bars and no hit)."""
    if e >= len(bars):
        return None
    entry = bars[e]["o"]
    dist = d * (entry - raw_stop)
    dist = max(dist, MIN_STOP * entry) if dist > 0 else MIN_STOP * entry
    stop, target = entry - d * dist, entry + d * RR * dist
    kind = px = k = None
    for k in range(e, min(e + HORIZON, len(bars))):
        b = bars[k]
        if (b["l"] <= stop) if d > 0 else (b["h"] >= stop):
            kind, px = "stop", stop
            break
        if (b["h"] >= target) if d > 0 else (b["l"] <= target):
            kind, px = "target", target
            break
    if kind is None:
        if e + HORIZON > len(bars):
            return None
        k = e + HORIZON - 1
        kind, px = "time", bars[k]["c"]
    gross = d * (px - entry) / entry
    sf = dist / entry
    return {"t_fill": bars[e]["t"], "t_exit_bar": bars[k]["t"], "entry": entry, "exit": px, "stop": stop, "target": target,
            "why": kind, "stop_frac": sf, "gross_r": gross / sf, "net_r": (gross - cost_frac(kind)) / sf, "status": "closed"}


def flow_turn(bars, i, d):
    """T2 on closed bar i: delta and body in direction d, and one of the 3 bars before it had opposite delta."""
    if i < 1:
        return False
    b = bars[i]
    if not (d * b["d"] > 0 and d * (b["c"] - b["o"]) > 0):
        return False
    return any(d * bars[m]["d"] < 0 for m in range(max(0, i - FLOW_LOOKBACK), i))


def div_map(bars):
    """{bar open time: set of directions} of confirmed regular RSI divergences (Malkan params, closes)."""
    out = {}
    for e in rsi_divergence_layer(bars):
        out.setdefault(e["t"], set()).add(SIDE[e["side"]])
    return out


def trigger(bars, divs, i, d):
    t1 = d in divs.get(bars[i]["t"], ())
    t2 = flow_turn(bars, i, d)
    return ("T1+T2" if t1 and t2 else "T1" if t1 else "T2") if (t1 or t2) else None


def touch_index(bars, call):
    d = SIDE[call["side"]]
    for i, b in enumerate(bars):
        if b["t"] <= call["t_logged"]:
            continue
        if b["t"] >= call["expires"]:
            return None
        if (b["l"] <= call["hi"]) if d > 0 else (b["h"] >= call["lo"]):
            return i
    return None


def regime(bars, i):
    """D SMA20 +-2 % regime from the last 20 completed UTC days before bar i; None when the history is too short."""
    day = lambda t: t // 86400000
    closes, cur = {}, day(bars[i]["t"])
    for b in bars[:i]:
        if day(b["t"]) < cur:
            closes[day(b["t"])] = b["c"]
    ds = sorted(closes)[-20:]
    if len(ds) < 20:
        return None
    sma, last = sum(closes[x] for x in ds) / 20, closes[ds[-1]]
    return "bull" if last > sma * 1.02 else "bear" if last < sma * 0.98 else "range"


def _read(path):
    rows, p = [], Path(path)
    if not p.exists():
        return rows
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def _append(path, rows):
    if not rows:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def arm_stats(rows, arm):
    nets = [r["net_r"] for r in rows if r.get("arm") == arm and r.get("kind") == "outcome" and r.get("status") == "closed"]
    return {"n": len(nets), "mean_r": (sum(nets) / len(nets)) if nets else None}


def verdict(rows):
    s, a, b = (arm_stats(rows, x) for x in ("setup", "placebo_a", "placebo_b"))
    if s["n"] < STOP_N:
        return "RUNNING"
    if s["mean_r"] <= 0:
        return "STOP"
    ok = all(p["mean_r"] is not None and s["mean_r"] > p["mean_r"] for p in (a, b))
    return "EDGE-CANDIDATE" if ok else "RUNNING (does not beat both placebos)"


def _row(arm, kind, t, call=None, **kw):
    r = {"arm": arm, "kind": kind, "t": t, "params_id": PARAMS_ID, "source": SOURCE, **kw}
    if call:
        r.update(call_id=call["id"], analyst=call["analyst"], side=call["side"])
    return r


def step(bars, calls, journal_path=JOURNAL_DEFAULT, min_bars=MIN_BARS):
    """One poll on closed 15m bars (dicts t,o,h,l,c,d; newest last). Returns the rows appended."""
    try:
        if not bars or len(bars) < min_bars or not clean(bars):
            _err("bad or short history: no evaluation")
            return []
        rows = _read(journal_path)
        if any(r.get("kind") == "kill" for r in rows):
            return []
        divs, new = div_map(bars), []
        done = {(r.get("arm"), r.get("call_id")) for r in rows if r.get("call_id")}
        last_t = bars[-1]["t"]

        def busy_until(arm):
            ts = [r["t_exit_bar"] for r in rows + new if r.get("arm") == arm and r.get("kind") == "outcome"]
            return max(ts) if ts else None

        cands = []
        for c in calls:
            d = SIDE[c["side"]]
            ti = touch_index(bars, c)
            if ti is None:
                continue
            if ("placebo_a", c["id"]) not in done:
                raw = min(bars[ti]["l"], c["lo"]) if d > 0 else max(bars[ti]["h"], c["hi"])
                res = simulate(d, bars, ti + 1, raw)
                if res:
                    new.append(_row("placebo_a", "outcome", res["t_fill"], c, **res))
            if ("setup", c["id"]) in done:
                continue
            hit = None
            for j in range(ti, min(ti + WINDOW, len(bars))):
                trg = trigger(bars, divs, j, d)
                if trg:
                    hit = (j, trg)
                    break
            if hit:
                cands.append((bars[hit[0]]["t"], c, ti, hit[0], hit[1]))
            elif ti + WINDOW <= len(bars):
                new.append(_row("setup", "no_trigger", bars[ti]["t"], c, t_touch=bars[ti]["t"]))
        open_setup = False
        for t_trig, c, ti, j, trg in sorted(cands, key=lambda x: x[0]):
            d = SIDE[c["side"]]
            bu = busy_until("setup")
            if open_setup or (bu is not None and t_trig + STEP <= bu):
                if not open_setup:
                    new.append(_row("setup", "skipped_busy", t_trig, c, trigger=trg))
                continue
            seg = bars[ti:j + 1]
            raw = min(min(b["l"] for b in seg), c["lo"]) if d > 0 else max(max(b["h"] for b in seg), c["hi"])
            res = simulate(d, bars, j + 1, raw)
            if res is None:
                open_setup = True            # entered or pending: later signals wait for the next poll
                continue
            new.append(_row("setup", "outcome", res["t_fill"], c, trigger=trg, t_touch=bars[ti]["t"], t_trigger=t_trig,
                            regime=regime(bars, j + 1), **res))
        if calls:                            # placebo B runs only while the slot has calls on file
            start = max(min(c["t_logged"] for c in calls), busy_until("placebo_b") or 0)
            i = next((k for k, b in enumerate(bars) if b["t"] > start), len(bars))
            while i < len(bars):
                b = bars[i]
                live = [c for c in calls if c["t_logged"] < b["t"] < c["expires"]]
                far = all(b["c"] > c["hi"] * (1 + AWAY) or b["c"] < c["lo"] * (1 - AWAY) for c in live)
                got = None
                if far and i >= B_STOP_BARS:
                    for d in (1, -1):
                        trg = trigger(bars, divs, i, d)
                        if trg:
                            got = (d, trg)
                            break
                if not got:
                    i += 1
                    continue
                d, trg = got
                seg = bars[i - B_STOP_BARS + 1:i + 1]
                raw = min(x["l"] for x in seg) if d > 0 else max(x["h"] for x in seg)
                res = simulate(d, bars, i + 1, raw)
                if res is None:
                    break
                new.append(_row("placebo_b", "outcome", res["t_fill"], None, side="long" if d > 0 else "short",
                                trigger=trg, t_trigger=b["t"], **res))
                i = next((k for k, x in enumerate(bars) if x["t"] > res["t_exit_bar"]), len(bars))
        if verdict(rows + new) == "STOP":
            new.append(_row("setup", "kill", last_t, None, **arm_stats(rows + new, "setup")))
        _append(journal_path, new)
        return new
    except Exception as exc:  # noqa: BLE001 - fail closed
        _err(f"step: {exc!r}"[:200])
        return []


def readout(journal_path=JOURNAL_DEFAULT):
    rows = _read(journal_path)
    f = lambda s: f"{s['mean_r']:+.3f}" if s["n"] else "-"
    L = ["| Arm | Trades | Net R |", "|---|---|---|"]
    for arm, name in (("setup", "Call + trigger (the setup)"), ("placebo_a", "Placebo A: level, no trigger"),
                      ("placebo_b", "Placebo B: trigger, no level")):
        s = arm_stats(rows, arm)
        L.append(f"| {name} | {s['n']} | {f(s)} |")
    nt = sum(1 for r in rows if r.get("kind") == "no_trigger")
    L += ["", f"State: {verdict(rows)}. Calls touched with no trigger: {nt}.",
          f"Rule: STOP at {STOP_N} setup trades with net R <= 0; edge candidate only at {STOP_N}+ trades, net R > 0 and above "
          "both placebos. Below that the only word is RUNNING."]
    return "\n".join(L) + "\n"


def fetch_closed(n=FETCH_BARS, now_ms=None, timeout=20):
    """Closed 15m BTCUSDT klines with delta, oldest first, public endpoint. Raises on any problem (caller fails closed)."""
    now_ms = int(time.time() * 1000) if now_ms is None else now_ms
    out, end = [], now_ms
    while len(out) < n:
        with urllib.request.urlopen(f"{URL}?symbol=BTCUSDT&interval=15m&limit=1000&endTime={end}", timeout=timeout) as r:
            page = json.loads(r.read())
        if not isinstance(page, list) or not page:
            raise ValueError("empty or bad klines page")
        out = [{"t": int(x[0]), "o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4]),
                "d": 2 * float(x[9]) - float(x[5]), "ct": int(x[6])} for x in page] + out
        end = page[0][0] - 1
    seen, uniq = set(), []
    for x in out:
        if x["ct"] < now_ms and x["t"] not in seen:
            seen.add(x["t"])
            uniq.append({k: x[k] for k in ("t", "o", "h", "l", "c", "d")})
    return sorted(uniq, key=lambda x: x["t"])[-n:]


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--once", action="store_true")
    g.add_argument("--readout", action="store_true")
    ap.add_argument("--journal", default=JOURNAL_DEFAULT)
    ap.add_argument("--calls", default=CALLS_DEFAULT)
    a = ap.parse_args(argv)
    if a.readout:
        sys.stdout.write(readout(a.journal))
        return 0
    try:
        bars = fetch_closed()
    except Exception as exc:  # noqa: BLE001
        _err(f"fetch: {exc!r}"[:200])
        return 2
    new = step(bars, load_calls(a.calls), a.journal)
    print(json.dumps({"key": "call_paper_log", "bar": dt.datetime.fromtimestamp(bars[-1]["t"] / 1000, dt.UTC).isoformat(),
                      "appended": [f"{r['arm']}:{r['kind']}" for r in new]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
