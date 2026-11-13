"""Live Aid forced-move collector (requirement R25). Public data only: no keys, no account or order endpoints, stdlib only.

Writes, each 60 s cycle (or once with --once: REST only, no websocket, exits):
  runtime_data/live_aid/flow_state.json   machine-readable state (gitignored runtime data)
  runtime_data/live_aid/flow_digest.txt   at most 30 fixed-key lines for a Haiku/Sonnet reader (see FLOW_READER.md)
  MyTradingSys/tools/live_aid/flow_feed.js  window.LIVEAID_FLOW for the page (large perp prints, perp CVD buckets, footprint lines); loop mode only
Sources: Bybit v5 linear BTCUSDT kline + open-interest (REST), spot taker volume from data-api.binance.vision klines (field 9 = taker buy
base volume; delta = 2 x takerBuy - volume, labelled "spot CVD"), and the Bybit websocket topic publicTrade.BTCUSDT (S = taker side,
v = BTC, p = price) for perp CVD, large trades (>= 500,000 USD, OURS) and the 15 m / 1 h footprint (10 USD price buckets).
The classification here is mirrored in flow_chart.js; both are tested against flow_fixture.json. Thresholds: STEPS.md (OURS, fixed before data).
Run by hand (no scheduler, no service, not the live tree):  python MyTradingSys/tools/live_aid/flow_collector.py   (Ctrl+C to stop)
"""
from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RT = ROOT / "runtime_data" / "live_aid"
STATE = RT / "flow_state.json"
DIGEST = RT / "flow_digest.txt"
TRADES = RT / "flow_trades.jsonl"
PERP = RT / "flow_perp.json"
FEED = HERE / "flow_feed.js"                       # inside the served folder, gitignored

FLAT = 0.1                                          # percent, the page's existing flat threshold
RUN_MIN_BARS, RUN_MIN_OI = 3, 0.5
BIG_USD = 500_000
EPS = 1e-9
TFS = {"5m": {"ms": 300_000, "bybit": "5", "oi": "5min", "spot": "5m", "key": "5M"},
       "30m": {"ms": 1_800_000, "bybit": "30", "oi": "30min", "spot": "30m", "key": "30M"},
       "1h": {"ms": 3_600_000, "bybit": "60", "oi": "1h", "spot": "1h", "key": "1H"}}
BARS = 72
FP_BUCKET = 10                                      # USD price bucket for the footprint POC
DAY = 86_400_000


# ---------------------------------------------------------------- pure rules (mirror of flow_chart.js)
def _ok(x) -> bool:
    return x is not None and x == x and abs(x) != float("inf")


def pct(a, b):
    return (b - a) / a * 100 if _ok(a) and _ok(b) and a != 0 else None


def r2(x):
    v = round(x + 0.0, 2)
    return 0.0 if v == 0 else v


def bar_state(dpx, doi, cvd) -> dict:
    if not _ok(dpx) or not _ok(doi):
        state = "NO_DATA"
    elif abs(dpx) < FLAT or abs(doi) < FLAT:
        state = "FLAT"
    elif dpx > 0:
        state = "NEW_LONGS" if doi > 0 else "FORCED_BUYING"
    else:
        state = "NEW_SHORTS" if doi > 0 else "FORCED_SELLING"
    if state == "NO_DATA" or not _ok(cvd):
        taker = "NOT_IN_DATA"
    elif state == "FLAT" or cvd == 0:
        taker = "na"
    else:
        taker = "agree" if (cvd > 0) == (dpx > 0) else "disagree"
    return {"state": state, "taker": taker}


def series(bars: list) -> list:
    out = []
    for i in range(1, len(bars)):
        a, b = bars[i - 1], bars[i]
        dpx, doi = pct(a.get("c"), b.get("c")), pct(a.get("oi"), b.get("oi"))
        s = bar_state(dpx, doi, b.get("cvd"))
        out.append({"i": i, "t": b["t"], "dpx": None if dpx is None else r2(dpx), "doi": None if doi is None else r2(doi),
                    "cvd": b.get("cvd") if _ok(b.get("cvd")) else None, **s})
    return out


def oi_runs(bars: list) -> list:
    runs, i, n = [], 1, len(bars)

    def sgn(k):
        d = pct(bars[k - 1].get("oi"), bars[k].get("oi"))
        return 0 if d is None or d == 0 else (1 if d > 0 else -1)
    while i < n:
        s = sgn(i)
        if not s:
            i += 1
            continue
        j = i
        while j + 1 < n and sgn(j + 1) == s:
            j += 1
        base = bars[i - 1]
        cum, dpx = pct(base["oi"], bars[j]["oi"]), pct(base.get("c"), bars[j].get("c"))
        if j - i + 1 >= RUN_MIN_BARS and (cum >= RUN_MIN_OI - EPS if s > 0 else cum <= -RUN_MIN_OI + EPS):
            runs.append({"kind": "BUILD" if s > 0 else "UNWIND",
                         "dir": "flat" if dpx is None else ("up" if dpx >= FLAT else "down" if dpx <= -FLAT else "flat"),
                         "bars": j - i + 1, "doi": r2(cum), "dpx": None if dpx is None else r2(dpx), "start": i, "end": j})
        i = j + 1
    return runs


def window_state(bars: list, n: int):
    if len(bars) < n + 1:
        return None
    base, last = bars[-n - 1], bars[-1]
    vals = [b.get("cvd") for b in bars[-n:]]
    cvd = None if any(not _ok(v) for v in vals) else sum(vals)
    dpx, doi = pct(base.get("c"), last.get("c")), pct(base.get("oi"), last.get("oi"))
    s = bar_state(dpx, doi, cvd)
    return {**s, "dpx": None if dpx is None else r2(dpx), "doi": None if doi is None else r2(doi), "cvd": None if cvd is None else r2(cvd)}


def is_stale(bars: list, tf_ms: int, now_ms: int) -> bool:
    return not bars or now_ms - (bars[-1]["t"] + tf_ms) > 2 * tf_ms


# ---------------------------------------------------------------- REST
def fetch_json(url: str, timeout: float = 10):
    req = Request(url, headers={"User-Agent": "mts-live-aid-flow/1"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def build_bars(kl, oi_list, spot, tf_ms, now_ms) -> list:
    """kl: Bybit rows newest first [startMs,o,h,l,c,...]; oi_list: [{openInterest,timestamp}]; spot: Binance rows or None. Closed bars only."""
    oi = {int(x["timestamp"]): float(x["openInterest"]) for x in (oi_list or [])}
    cv = {int(x[0]): 2 * float(x[9]) - float(x[5]) for x in spot} if spot else {}
    bars = [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4]),
             "oi": oi.get(int(k[0])), "cvd": cv.get(int(k[0])) if spot else None} for k in kl]
    bars = [b for b in bars if b["t"] + tf_ms <= now_ms]
    bars.sort(key=lambda b: b["t"])
    return bars[-BARS:]


def load_frames(now_ms: int, get=fetch_json) -> dict:
    out = {}
    for tf, c in TFS.items():
        f = {"bars": [], "err": {}}
        u = f"limit={BARS + 2}"
        try:
            kl = get(f"https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval={c['bybit']}&{u}")["result"]["list"]
        except Exception as e:  # noqa: BLE001
            kl = []
            f["err"]["bybit_kline"] = f"{type(e).__name__}: {e}"[:120]
        try:
            ol = get(f"https://api.bybit.com/v5/market/open-interest?category=linear&symbol=BTCUSDT&intervalTime={c['oi']}&{u}")["result"]["list"]
        except Exception as e:  # noqa: BLE001
            ol = []
            f["err"]["bybit_oi"] = f"{type(e).__name__}: {e}"[:120]
        try:
            sp = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={c['spot']}&{u}")
        except Exception as e:  # noqa: BLE001
            sp = None
            f["err"]["spot_kline"] = f"{type(e).__name__}: {e}"[:120]
        f["bars"] = build_bars(kl, ol, sp, c["ms"], now_ms)
        out[tf] = f
    return out


# ---------------------------------------------------------------- trades and footprint
def parse_trades(msg) -> list:
    """Bybit publicTrade message -> [(t_ms, 'buy'|'sell', btc, px, trade_id)]. S = taker side. Junk rows skipped."""
    if not isinstance(msg, dict) or msg.get("topic") != "publicTrade.BTCUSDT":
        return []
    out = []
    for d in msg.get("data") or []:
        try:
            side = {"Buy": "buy", "Sell": "sell"}[d["S"]]
            btc, px = float(d["v"]), float(d["p"])
            if btc > 0 and px > 0:
                out.append((int(d["T"]), side, btc, px, str(d.get("i", ""))))
        except (KeyError, ValueError, TypeError):
            continue
    return out


class Footprint:
    """Per 15 m bucket: delta, volume per 10 USD price bucket, largest print, large-trade counts. 1 h = four 15 m buckets merged."""
    SPAN = 900_000

    def __init__(self):
        self.b = {}
        self.first_t = None

    def add(self, t, side, btc, px):
        if self.first_t is None:
            self.first_t = t
        k = t // self.SPAN * self.SPAN
        x = self.b.setdefault(k, {"delta": 0.0, "poc": {}, "big": None, "lb": 0, "ls": 0, "n": 0})
        x["delta"] += btc if side == "buy" else -btc
        pk = int(px // FP_BUCKET * FP_BUCKET)
        x["poc"][pk] = x["poc"].get(pk, 0.0) + btc
        if x["big"] is None or btc > x["big"][0]:
            x["big"] = (btc, side, px)
        if btc * px >= BIG_USD:
            x["lb" if side == "buy" else "ls"] += 1
        x["n"] += 1

    def prune(self, now_ms):
        for k in [k for k in self.b if k < now_ms - 4 * 3_600_000]:
            del self.b[k]

    def summary(self, start, span):
        ks = [k for k in range(start, start + span, self.SPAN) if k in self.b]
        if not ks:
            return None
        poc, delta, big, lb, ls, n = {}, 0.0, None, 0, 0, 0
        for k in ks:
            x = self.b[k]
            delta += x["delta"]
            lb, ls, n = lb + x["lb"], ls + x["ls"], n + x["n"]
            for p, v in x["poc"].items():
                poc[p] = poc.get(p, 0.0) + v
            if x["big"] and (big is None or x["big"][0] > big[0]):
                big = x["big"]
        pp = sorted(poc.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        return {"from": start, "delta": round(delta, 3), "poc": pp, "big_btc": round(big[0], 4), "big_side": big[1], "big_px": big[2],
                "large_buy": lb, "large_sell": ls, "n": n, "partial": self.first_t is not None and self.first_t > start}


def hhmm(t) -> str:
    return time.strftime("%H:%MZ", time.gmtime(t / 1000))


def fp_line(tf: str, s) -> str:
    if not s:
        return f"{tf} NOT_IN_DATA"
    return (f"{tf} {hhmm(s['from'])} delta {s['delta']:+.1f} BTC, POC {s['poc']}, biggest {s['big_btc']:.2f} BTC {s['big_side'].upper()}, "
            f"large {s['large_buy']} buy / {s['large_sell']} sell" + (" (partial)" if s["partial"] else ""))


def fp_all(fp: Footprint, now_ms: int) -> dict:
    out = {}
    for tf, span in (("15m", 900_000), ("1h", 3_600_000)):
        cur = now_ms // span * span
        out[tf] = {"cur": fp.summary(cur, span), "last": fp.summary(cur - span, span)}
    return out


# ---------------------------------------------------------------- state and digest
def build_state(frames: dict, big: list, fp, now_ms: int, ws_on: bool) -> dict:
    st = {"t": now_ms, "px": None, "tf": {}, "hour": None, "big": big[-10:], "fp": fp, "stale": [], "ws": ws_on,
          "thresholds": {"flat_pct": FLAT, "run_bars": RUN_MIN_BARS, "run_oi_pct": RUN_MIN_OI, "big_usd": BIG_USD}}
    for tf, c in TFS.items():
        f = frames.get(tf) or {"bars": [], "err": {}}
        bars = f["bars"]
        e = {"stale": is_stale(bars, c["ms"], now_ms), "err": f["err"], "n": len(bars), "last": None, "run": None}
        if bars and tf == "5m":
            st["px"] = bars[-1]["c"]
        ser = series(bars)
        if ser and not e["stale"]:
            e["last"] = ser[-1]
        runs = oi_runs(bars)
        if runs and not e["stale"]:
            r = runs[-1]
            e["run"] = {**r, "from": bars[r["start"]]["t"], "active": r["end"] >= len(bars) - 2}
        st["tf"][tf] = e
        for feed, why in f["err"].items():
            st["stale"].append(f"{feed}_{tf} ERR {why}")
        if not f["err"] and e["stale"]:
            st["stale"].append(f"{tf} last_bar={hhmm(bars[-1]['t']) if bars else 'none'}")
    f5 = (frames.get("5m") or {}).get("bars") or []
    if f5 and not st["tf"]["5m"]["stale"]:
        st["hour"] = window_state(f5, 12)
    if not ws_on:
        st["stale"].append("trades_ws not_running")
    return st


def _n(x, f):
    return "NOT_IN_DATA" if x is None else format(x, f)


def digest(st: dict) -> str:
    L = [f"T {time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(st['t'] / 1000))} | PX {_n(st['px'] and round(st['px']), 'd')}"]
    for tf in ("1h", "30m", "5m"):
        k, e = TFS[tf]["key"], st["tf"][tf]
        x = e["last"]
        if x:
            L.append(f"{k} LAST state={x['state']} dpx={_n(x['dpx'], '+.2f')} doi={_n(x['doi'], '+.2f')} cvd={_n(x['cvd'], '+.0f')} taker={x['taker']} bar={hhmm(x['t'])}")
        else:
            L.append(f"{k} LAST NOT_IN_DATA")
        r = e["run"]
        L.append(f"{k} RUN kind={r['kind']} dir={r['dir']} bars={r['bars']} doi={r['doi']:+.1f} dpx={r['dpx']:+.1f} from={hhmm(r['from'])} active={int(r['active'])}" if r else f"{k} RUN none")
    h = st["hour"]
    L.append(f"60M WINDOW state={h['state']} dpx={_n(h['dpx'], '+.2f')} doi={_n(h['doi'], '+.2f')} cvd={_n(h['cvd'], '+.0f')} taker={h['taker']}" if h else "60M WINDOW NOT_IN_DATA")
    fp = st.get("fp")
    for tf in ("15m", "1h"):
        for which in ("cur", "last"):
            s = fp and fp[tf][which]
            L.append(f"FP {tf.upper()} {which} {fp_line(tf, s)[len(tf) + 1:]}" if s else f"FP {tf.upper()} {which} NOT_IN_DATA")
    if st["big"]:
        for b in st["big"]:
            L.append(f"BIG {hhmm(b['t'])} {b['side'].upper()} {b['usd'] / 1e6:.1f}M @{round(b['px'])}")
    else:
        L.append("BIG none")
    for s in st["stale"][:6]:
        L.append("STALE " + s)
    L.append(f"NOTE descriptive only; flat {FLAT}% run {RUN_MIN_BARS} bars {RUN_MIN_OI}% OI big {BIG_USD} USD (OURS)")
    return "\n".join(L[:30]) + "\n"


def write_atomic(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def build_feed(now_ms: int, big: list, perp: dict, fp) -> dict:
    lines = {}
    if fp:
        for tf in ("15m", "1h"):
            parts = [fp_line(tf, fp[tf]["last"])]
            if fp[tf]["cur"]:
                parts.append("open bar " + f"{fp[tf]['cur']['delta']:+.1f} BTC")
            lines[tf] = "; ".join(parts)
    return {"t": now_ms, "trades": [{"t": b["t"], "side": b["side"], "btc": b["btc"], "px": b["px"], "usd": b["usd"]} for b in big[-300:]],
            "perp": perp, "fp": {"t": now_ms, "lines": lines, "data": fp} if fp else None}


def load_big(path: Path, now_ms: int) -> list:
    out = []
    try:
        for ln in path.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(ln)
                if d["t"] >= now_ms - DAY:
                    out.append(d)
            except (ValueError, KeyError):
                continue
    except OSError:
        pass
    return out


class Collector:
    def __init__(self, now=time.time):
        self.now = now
        self.lock = threading.Lock()
        nm = int(now() * 1000)
        self.big = load_big(TRADES, nm)
        self.seen = {d.get("i") for d in self.big if d.get("i")}
        self.fp = Footprint()
        self.buckets, self.since, self.last_msg = {}, None, 0
        try:
            m = json.loads(PERP.read_text(encoding="utf-8"))
            if nm - m["last_t"] <= 600_000:                # gap over 10 min: perp CVD restarts, never bridged
                self.buckets = {int(k): v for k, v in m["b"].items()}
                self.since = m["since"]
        except (OSError, ValueError, KeyError):
            pass

    def add(self, trades):
        fresh = []
        with self.lock:
            for t, side, btc, px, tid in trades:
                self.last_msg = int(self.now() * 1000)
                if self.since is None:
                    self.since = t // 300_000 * 300_000 + 300_000
                k = t // 300_000 * 300_000
                x = self.buckets.setdefault(k, [0.0, 0.0])
                x[0 if side == "buy" else 1] += btc
                self.fp.add(t, side, btc, px)
                if btc * px >= BIG_USD and tid not in self.seen:
                    self.seen.add(tid)
                    d = {"t": t, "side": side, "btc": btc, "px": px, "usd": round(btc * px), "i": tid}
                    self.big.append(d)
                    fresh.append(d)
        if fresh:
            TRADES.parent.mkdir(parents=True, exist_ok=True)
            with open(TRADES, "a", encoding="utf-8", newline="\n") as f:
                f.write("".join(json.dumps(d) + "\n" for d in fresh))

    def ws_loop(self, stop):
        from xliq_collector import WS
        while not stop.is_set():
            ws = None
            try:
                ws = WS("stream.bybit.com", "/v5/public/linear")
                ws.send(json.dumps({"op": "subscribe", "args": ["publicTrade.BTCUSDT"]}).encode())
                ws.s.settimeout(20)
                while not stop.is_set():
                    try:
                        m = ws.recv()
                    except socket.timeout:
                        ws.send(b'{"op":"ping"}')
                        continue
                    self.add(parse_trades(json.loads(m)))
            except Exception:  # noqa: BLE001
                pass
            finally:
                if ws:
                    ws.close()
            stop.wait(5)

    def cycle(self, frames=None):
        nm = int(self.now() * 1000)
        frames = frames or load_frames(nm)
        with self.lock:
            cut = nm - DAY
            self.big = [d for d in self.big if d["t"] >= cut]
            self.buckets = {k: v for k, v in self.buckets.items() if k >= cut}
            self.fp.prune(nm)
            ws_on = nm - self.last_msg <= 90_000
            fp = fp_all(self.fp, nm) if ws_on else None
            perp = {"since": self.since, "b": {str(k): v for k, v in self.buckets.items()}} if ws_on and self.since else None
            big = list(self.big)
            write_atomic(PERP, json.dumps({"since": self.since, "last_t": nm, "b": {str(k): v for k, v in self.buckets.items()}}))
        st = build_state(frames, big, fp, nm, ws_on)
        top = {}
        for d in big:
            top.setdefault(time.strftime("%H", time.gmtime(d["t"] / 1000)), []).append(d)
        st["top_by_hour"] = {h: sorted(v, key=lambda d: -d["usd"])[:10] for h, v in top.items()}
        write_atomic(STATE, json.dumps(st, indent=1))
        write_atomic(DIGEST, digest(st))
        write_atomic(FEED, "window.LIVEAID_FLOW = " + json.dumps(build_feed(nm, big, perp, fp), separators=(",", ":")) + ";\n")
        return st

    def run(self, interval=60, cycles=0):
        stop = threading.Event()
        threading.Thread(target=self.ws_loop, args=(stop,), daemon=True).start()
        n = 0
        try:
            while True:
                try:
                    st = self.cycle()
                    print("[flow] " + time.strftime("%H:%M:%S") + f" ws={int(st['ws'])} stale={len(st['stale'])} big24h={len(st['big'])}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print("[flow] cycle failed: " + f"{type(e).__name__}: {e}", flush=True)
                n += 1
                if cycles and n >= cycles:
                    return 0
                time.sleep(interval)
        except KeyboardInterrupt:
            return 0
        finally:
            stop.set()


def once(now=time.time) -> str:
    nm = int(now() * 1000)
    st = build_state(load_frames(nm), load_big(TRADES, nm), None, nm, False)
    text = digest(st)
    write_atomic(STATE, json.dumps(st, indent=1))
    write_atomic(DIGEST, text)
    return text


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Live Aid forced-move collector (public data, run by hand)")
    ap.add_argument("--once", action="store_true", help="REST only, no websocket: write state + digest and exit")
    ap.add_argument("--interval", type=float, default=60)
    ap.add_argument("--cycles", type=int, default=0)
    a = ap.parse_args(argv)
    if a.once:
        sys.stdout.write(once())
        return 0
    return Collector().run(a.interval, a.cycles)


if __name__ == "__main__":
    sys.exit(main())
