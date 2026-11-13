"""Live Aid cross-exchange forced-selling collector (card live-aid-xliq-1113).

Collects BTC perp LIQUIDATIONS from public feeds only (no keys, no account or order endpoints):
  BYBIT    websocket wss://stream.bybit.com/v5/public/linear  topic allLiquidation.BTCUSDT
           https://bybit-exchange.github.io/docs/v5/websocket/public/all-liquidation   S=Buy means a LONG was liquidated, v = base qty (BTC), p = bankruptcy price
  BINANCE  websocket wss://fstream.binance.com/ws/btcusdt@forceOrder  (REST allForceOrders is gone: 404, measured 2026-11-13)
           https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams
           o.S=SELL means a LONG was liquidated; o.z = filled qty (BTC), o.ap = average price. Reached by DoH pinned IP (binance_doh.resolve).
  OKX      REST https://www.okx.com/api/v5/public/liquidation-orders?instType=SWAP&uly=BTC-USDT&state=filled (polled; DoH pinned)
           https://www.okx.com/docs-v5/en/#public-data-rest-api-get-liquidation-orders   posSide long = a LONG was liquidated; sz in contracts, 1 contract = 0.01 BTC (ctVal)
  HYPERLIQUID has no public market-wide liquidation feed (only per-user fills), so it is not collected.
Notional (USD) = BTC qty x price. Every print is appended to runtime_data/live_aid/xliq_events.jsonl (gitignored runtime data, 8 days kept);
each cycle writes xliq_feed.js into THIS folder (the :8765 server serves this folder as its root, so ../ URLs 404) as window.LIVEAID_XLIQ.
BIG = a print above the venue's p99 over the last 7 days of stored prints; until the venue has 7 days of history AND >= 100 prints the
feed says 'building' and nothing is ever marked BIG (fail closed). p99 and the 15 m window are OURS.

Run by hand (no scheduler, no service, not the live tree):  python MyTradingSys/tools/live_aid/xliq_collector.py   (Ctrl+C to stop)
"""
from __future__ import annotations

import base64
import json
import math
import os
import socket
import ssl
import struct
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HERE = Path(__file__).resolve().parent
OUT = HERE / "xliq_feed.js"                                     # inside the served folder
EVENTS = ROOT / "runtime_data" / "live_aid" / "xliq_events.jsonl"
META = ROOT / "runtime_data" / "live_aid" / "xliq_meta.json"
VENUES = ("BYBIT", "BINANCE", "OKX")
WIN_MS = 15 * 60 * 1000          # OURS: the row's window
BASE_MS = 7 * 86400 * 1000       # OURS: p99 baseline span
KEEP_MS = 8 * 86400 * 1000
MIN_N = 100                      # OURS: fewer prints than this cannot carry a p99
OKX_CT_BTC = 0.01                # SOURCED: BTC-USDT-SWAP ctVal 0.01 BTC


# ---- pure parsers: decoded message -> [(t_ms, side, usd, px)]; side is the POSITION that was liquidated ----------------
def _num(x) -> float:
    v = float(x)
    if not math.isfinite(v) or v <= 0:
        raise ValueError("bad number")
    return v


def parse_bybit(msg) -> list:
    if not isinstance(msg, dict) or msg.get("topic") != "allLiquidation.BTCUSDT":
        return []
    out = []
    for d in msg.get("data") or []:
        try:
            px = _num(d["p"])
            out.append((int(d["T"]), "long" if d["S"] == "Buy" else "short", _num(d["v"]) * px, px))
        except (KeyError, ValueError, TypeError):
            continue
    return out


def parse_binance(msg) -> list:
    o = msg.get("o") if isinstance(msg, dict) and msg.get("e") == "forceOrder" else None
    if not o or o.get("s") != "BTCUSDT":
        return []
    try:
        px = _num(o["ap"]) if float(o.get("ap") or 0) > 0 else _num(o["p"])
        return [(int(o["T"]), "long" if o["S"] == "SELL" else "short", _num(o["z"]) * px, px)]
    except (KeyError, ValueError, TypeError):
        return []


def parse_okx(reply) -> list:
    out = []
    try:
        for blk in reply["data"]:
            for d in blk.get("details") or []:
                try:
                    px = _num(d["bkPx"])
                    side = d["posSide"] if d.get("posSide") in ("long", "short") else ("long" if d["side"] == "sell" else "short")
                    out.append((int(d["ts"]), side, _num(d["sz"]) * OKX_CT_BTC * px, px))
                except (KeyError, ValueError, TypeError):
                    continue
    except (KeyError, TypeError):
        return []
    return out


# ---- baseline + window maths ---------------------------------------------------------------------------------------
def p99(values):
    """Nearest-rank 99th percentile: the value at 1-based rank ceil(0.99 n) of the sorted list; None for an empty list."""
    v = sorted(values)
    return v[max(0, math.ceil(0.99 * len(v)) - 1)] if v else None


def venue_summary(events, since_ms, now_ms, err="") -> dict:
    """events: [(t, side, usd, px)] of ONE venue. since_ms: when the collector first saw this venue (None = never)."""
    base = [e for e in events if now_ms - BASE_MS <= e[0] <= now_ms]
    win = [e for e in events if now_ms - WIN_MS < e[0] <= now_ms]
    ready = since_ms is not None and now_ms - since_ms >= BASE_MS and len(base) >= MIN_N
    thr = p99([e[2] for e in base]) if ready else None
    big = [e for e in win if thr is not None and e[2] > thr]
    mx = max(win, key=lambda e: e[2]) if win else None
    bigpx = (sum(e[3] * e[2] for e in big) / sum(e[2] for e in big)) if big else None
    return {"long15": round(sum(e[2] for e in win if e[1] == "long")), "short15": round(sum(e[2] for e in win if e[1] == "short")),
            "n15": len(win), "max15": round(mx[2]) if mx else 0, "maxside": mx[1] if mx else None,
            "p99": round(thr) if thr is not None else None, "baseline": "ready" if ready else "building",
            "have_days": round((now_ms - since_ms) / 86400000, 2) if since_ms is not None else 0, "n7d": len(base),
            "big": len(big), "bigside": max(("long", "short"), key=lambda s: sum(e[2] for e in big if e[1] == s)) if big else None,
            "bigpx": round(bigpx) if bigpx else None, "err": err}


def build_feed(by_venue: dict, since: dict, errs: dict, now_ms: int) -> dict:
    return {"t": now_ms, "venues": {v: venue_summary(by_venue.get(v, []), since.get(v), now_ms, errs.get(v, "")) for v in VENUES}}


def write_feed(feed: dict, path: Path = OUT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write("window.LIVEAID_XLIQ = " + json.dumps(feed, separators=(",", ":")) + ";\n")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


# ---- storage -------------------------------------------------------------------------------------------------------
def load_events(path: Path = EVENTS, now_ms=None) -> dict:
    now_ms = now_ms or int(time.time() * 1000)
    out = {v: [] for v in VENUES}
    if not Path(path).exists():
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
                if d["v"] in out and d["t"] >= now_ms - KEEP_MS:
                    out[d["v"]].append((d["t"], d["s"], d["usd"], d["px"]))
            except (ValueError, KeyError, TypeError):
                continue
    return out


def append_events(venue: str, evs, path: Path = EVENTS) -> None:
    if not evs:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for t, s, usd, px in evs:
            f.write(json.dumps({"v": venue, "t": t, "s": s, "usd": round(usd, 2), "px": px}, separators=(",", ":")) + "\n")


def prune(by_venue: dict, now_ms: int, path: Path = EVENTS) -> None:
    keep = {v: [e for e in es if e[0] >= now_ms - KEEP_MS] for v, es in by_venue.items()}
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        for v, es in keep.items():
            for t, s, usd, px in es:
                f.write(json.dumps({"v": v, "t": t, "s": s, "usd": round(usd, 2), "px": px}, separators=(",", ":")) + "\n")
    os.replace(tmp, path)
    by_venue.update(keep)


# ---- minimal websocket client (stdlib only; text frames, ping/pong, close) -----------------------------------------
class WS:
    def __init__(self, host, path, timeout=30, ip=None):
        raw = socket.create_connection((ip or host, 443), timeout)
        self.s = ssl.create_default_context().wrap_socket(raw, server_hostname=host)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\nUser-Agent: mts-live-aid-xliq/1\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            c = self.s.recv(1024)
            if not c:
                raise OSError("closed during handshake")
            head += c
        head, self.buf = head.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise OSError("handshake refused: " + head.split(b"\r\n")[0].decode(errors="replace"))

    def _need(self, n):
        while len(self.buf) < n:
            c = self.s.recv(65536)
            if not c:
                raise OSError("connection closed")
            self.buf += c
        r, self.buf = self.buf[:n], self.buf[n:]
        return r

    def send(self, data: bytes, op=1):
        mask = os.urandom(4)
        n = len(data)
        hdr = bytes([0x80 | op]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n))
        self.s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def recv(self):
        """Next text message (ping answered, other frames skipped). Raises on close; socket.timeout when idle."""
        msg = b""
        while True:
            b0, b1 = self._need(2)
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._need(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._need(8))[0]
            data = self._need(n)
            op = b0 & 0x0F
            if op == 9:
                self.send(data, 10)
            elif op == 8:
                raise OSError("server closed")
            elif op in (1, 0):
                msg += data
                if b0 & 0x80:
                    return msg.decode("utf-8", "replace")

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


class Collector:
    def __init__(self, events_path=EVENTS, meta_path=META, out=OUT, now=time.time):
        self.now, self.events_path, self.meta_path, self.out = now, events_path, meta_path, out
        self.lock = threading.Lock()
        self.by = load_events(events_path, int(now() * 1000))
        self.errs = {v: "not connected yet" for v in VENUES}
        self.seen = {v: {(e[0], e[2]) for e in self.by[v]} for v in VENUES}
        try:
            self.since = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.since = {}

    def add(self, venue, evs):
        fresh = []
        with self.lock:
            for e in evs:
                k = (e[0], e[2])
                if k not in self.seen[venue]:
                    self.seen[venue].add(k)
                    fresh.append(e)
            self.by[venue].extend(fresh)
        append_events(venue, fresh, self.events_path)

    def mark_connected(self, venue):
        with self.lock:
            self.errs[venue] = ""
            if venue not in self.since:
                self.since[venue] = int(self.now() * 1000)
                Path(self.meta_path).parent.mkdir(parents=True, exist_ok=True)
                Path(self.meta_path).write_text(json.dumps(self.since), encoding="utf-8")

    def snapshot(self):
        with self.lock:
            return build_feed(self.by, self.since, self.errs, int(self.now() * 1000))

    # ---- venue loops (run in threads; any failure = error text + reconnect, never a guess)
    def ws_loop(self, venue, host, path, sub, parser, stop):
        while not stop.is_set():
            ws = None
            try:
                ip = None
                if venue == "BINANCE":
                    from MyTradingSys.runtime import binance_doh
                    ip = binance_doh.resolve(host)[0]
                ws = WS(host, path, ip=ip)
                if sub:
                    ws.send(json.dumps(sub).encode())
                self.mark_connected(venue)
                ws.s.settimeout(20)
                while not stop.is_set():
                    try:
                        m = ws.recv()
                    except socket.timeout:
                        if venue == "BYBIT":
                            ws.send(b'{"op":"ping"}')
                        else:
                            ws.send(b"", 9)
                        continue
                    self.add(venue, parser(json.loads(m)))
            except Exception as e:  # noqa: BLE001
                self.errs[venue] = f"{type(e).__name__}: {e}"[:160]
            finally:
                if ws:
                    ws.close()
            stop.wait(5)

    def okx_loop(self, stop, interval=30):
        from MyTradingSys.runtime.doh_http import urlopen_pinned
        url = "https://www.okx.com/api/v5/public/liquidation-orders?instType=SWAP&uly=BTC-USDT&state=filled"
        while not stop.is_set():
            try:
                with urlopen_pinned(url, timeout=10) as r:
                    reply = json.loads(r.read().decode("utf-8"))
                if reply.get("code") != "0":
                    raise ValueError(f"okx code {reply.get('code')}")
                self.mark_connected("OKX")
                self.add("OKX", parse_okx(reply))
            except Exception as e:  # noqa: BLE001
                self.errs["OKX"] = f"{type(e).__name__}: {e}"[:160]
            stop.wait(interval)

    def run(self, cycles=0, interval=15):
        stop = threading.Event()
        sub = {"op": "subscribe", "args": ["allLiquidation.BTCUSDT"]}
        ths = [threading.Thread(target=self.ws_loop, args=("BYBIT", "stream.bybit.com", "/v5/public/linear", sub, parse_bybit, stop), daemon=True),
               threading.Thread(target=self.ws_loop, args=("BINANCE", "fstream.binance.com", "/ws/btcusdt@forceOrder", None, parse_binance, stop), daemon=True),
               threading.Thread(target=self.okx_loop, args=(stop,), daemon=True)]
        for t in ths:
            t.start()
        n, last_prune = 0, time.time()
        try:
            while True:
                time.sleep(interval)
                feed = self.snapshot()
                write_feed(feed, self.out)
                print("[xliq] " + time.strftime("%H:%M:%S") + " " + " | ".join(
                    f"{v} n15={s['n15']} L={s['long15']:,} S={s['short15']:,} {s['baseline']}{(' ERR ' + s['err']) if s['err'] else ''}"
                    for v, s in feed["venues"].items()), flush=True)
                if time.time() - last_prune > 6 * 3600:
                    with self.lock:
                        prune(self.by, int(self.now() * 1000), self.events_path)
                    last_prune = time.time()
                n += 1
                if cycles and n >= cycles:
                    return 0
        except KeyboardInterrupt:
            return 0
        finally:
            stop.set()


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Live Aid cross-exchange liquidation collector (public data, run by hand)")
    ap.add_argument("--cycles", type=int, default=0)
    ap.add_argument("--interval", type=float, default=15)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--events", default=str(EVENTS))
    ap.add_argument("--meta", default=str(META))
    a = ap.parse_args(argv)
    return Collector(Path(a.events), Path(a.meta), Path(a.out)).run(a.cycles, a.interval)


if __name__ == "__main__":
    sys.exit(main())
