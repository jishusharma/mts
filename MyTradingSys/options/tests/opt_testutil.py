"""Shared test helpers for the options collector tests: sys.path wiring, fixtures, and a fake Deribit HTTP server.

Nothing here touches the network: FakeDeribit.transport() replaces urllib so the REAL client code (URL building,
retry/backoff, parameter names, pagination logic) runs against recorded response shapes + synthetic datasets.
OPT_COLLECTOR_DIR can point the tests at a modified copy of the collector (used for the broken-variant checks).
"""
import json
import os
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLLECTOR_DIR = Path(os.environ.get("OPT_COLLECTOR_DIR") or (HERE.parent / "collector"))
sys.path.insert(0, str(COLLECTOR_DIR))

import deribit_opt_common as C  # noqa: E402

FIXTURES = HERE / "fixtures"
HOUR = 3600000
DAY = 86400000
# a fixed "now" for deterministic tests: 2026-10-08 19:30:00 UTC
NOW = C.date_to_ms("2026-10-08") + 19 * HOUR + 30 * 60000


def fixture(name):
    with open(FIXTURES / name, "r", encoding="utf-8") as f:
        return json.load(f)


class ApiError(Exception):
    def __init__(self, code, message="error", data=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def envelope_ok(result):
    return json.dumps({"jsonrpc": "2.0", "result": result, "usIn": 1, "usOut": 2, "usDiff": 1, "testnet": False}).encode()


def envelope_err(code, message="error", data=None):
    err = {"code": code, "message": message}
    if data:
        err["data"] = data
    return json.dumps({"jsonrpc": "2.0", "error": err, "testnet": False}).encode()


class ScriptedTransport:
    """Returns pre-scripted (status, body, headers) tuples / raises exceptions, one per request."""

    def __init__(self, script):
        self.script = list(script)
        self.urls = []

    def __call__(self, url, timeout):
        self.urls.append(url)
        item = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(item, Exception):
            raise item
        return item


class FakeClock:
    """Deterministic clock+sleep: sleep() advances time instead of waiting."""

    def __init__(self, t=1000.0):
        self.t = t
        self.sleeps = []

    def clock(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s

    def advance(self, s):
        self.t += s


class FakeDeribit:
    """Serves the public methods the collector uses from synthetic datasets + recorded fixtures."""

    def __init__(self, trade_floor_ms=0, dvol_page=1000, tv_cap=5001):
        self.calls = []                 # (method, params) in order
        self.trade_floor_ms = trade_floor_ms
        self.dvol_page = dvol_page
        self.tv_cap = tv_cap
        self.dvol = {}                  # resolution -> [[ts,o,h,l,c], ...] ascending
        self.perp = {}                  # resolution -> [[ts,o,h,l,c,volume,cost], ...]
        self.funding = []               # dicts, ascending
        self.delivery = []              # newest first: {"date","delivery_price"}
        self.trades = []                # dicts with timestamp, trade_id, instrument_name
        self.summary = fixture("book_summary.json")
        self.expired = fixture("instruments_expired.json")
        self.index_price = fixture("index_price.json")
        self.ticker_fail = set()        # instrument names whose ticker raises a non-retryable error
        self.on_call = None             # optional hook(method, params)
        self.max_calls = 5000           # runaway-pagination guard: a looping collector must fail the test, not hang it

    # -- transport ------------------------------------------------------------------------------------
    def transport(self, url, timeout):
        p = urllib.parse.urlparse(url)
        assert p.path.startswith("/api/v2/public/"), "non-public path requested: %s" % p.path
        method = "public/" + p.path.rsplit("/", 1)[1]
        params = {k: v[0] for k, v in urllib.parse.parse_qs(p.query).items()}
        assert "Authorization" not in params and "client_secret" not in params
        self.calls.append((method, params))
        assert len(self.calls) <= self.max_calls, "runaway pagination: more than %d requests" % self.max_calls
        try:
            if self.on_call:
                self.on_call(method, params)
            return 200, envelope_ok(self.handle(method, params)), {}
        except ApiError as e:
            return 200, envelope_err(e.code, e.message, e.data), {}

    def client(self, base=C.LIVE_BASE, **kw):
        kw.setdefault("rate", 5.0)
        kw.setdefault("sleep", lambda s: None)
        kw.setdefault("jitter", False)
        return C.DeribitPublic(base, transport=self.transport, **kw)

    def n_calls(self, method=None):
        return sum(1 for m, _ in self.calls if method is None or m == method)

    # -- handlers -------------------------------------------------------------------------------------
    def handle(self, method, p):
        fn = getattr(self, "h_" + method.split("/", 1)[1], None)
        if fn is None:
            raise AssertionError("FakeDeribit: unexpected method %s" % method)
        return fn(p)

    def h_get_index_price(self, p):
        return self.index_price

    def h_get_book_summary_by_currency(self, p):
        assert p["currency"] == "BTC" and p["kind"] == "option"
        return self.summary

    def h_ticker(self, p):
        name = p["instrument_name"]
        if name in self.ticker_fail:
            raise ApiError(13020, "Instrument not found")
        row = next(r for r in self.summary if r["instrument_name"] == name)
        t = json.loads(json.dumps(fixture("ticker.json")))
        t["instrument_name"] = name
        t["mark_iv"] = row.get("mark_iv")
        t["underlying_price"] = row.get("underlying_price")
        return t

    def h_get_volatility_index_data(self, p):
        res, start, end = p["resolution"], int(p["start_timestamp"]), int(p["end_timestamp"])
        step = {"3600": HOUR, "1D": DAY, "60": 60000}[res]
        data = [r for r in self.dvol.get(res, []) if start <= r[0] <= end]
        take = data[-self.dvol_page:]
        older = data[:-self.dvol_page] if len(data) > self.dvol_page else []
        return {"data": take, "continuation": (take[0][0] - step) if older else None}

    def h_get_tradingview_chart_data(self, p):
        assert p["instrument_name"] == "BTC-PERPETUAL"
        start, end = int(p["start_timestamp"]), int(p["end_timestamp"])
        rows = [r for r in self.perp.get(p["resolution"], []) if start <= r[0] <= end][-self.tv_cap:]
        out = {k: [r[i] for r in rows] for i, k in enumerate(("ticks", "open", "high", "low", "close", "volume", "cost"))}
        out["status"] = "ok" if rows else "no_data"
        return out

    def h_get_funding_rate_history(self, p):
        start, end = int(p["start_timestamp"]), int(p["end_timestamp"])
        return [r for r in self.funding if start <= r["timestamp"] <= end][-744:]

    def h_get_delivery_prices(self, p):
        off, cnt = int(p["offset"]), int(p["count"])
        return {"data": self.delivery[off: off + min(cnt, 100)], "records_total": len(self.delivery)}

    def h_get_instruments(self, p):
        assert p["expired"] == "true"
        return self.expired

    def h_get_last_trades_by_currency_and_time(self, p):
        cnt = int(p["count"])
        if cnt > 10000:
            raise ApiError(-32602, "Invalid params", {"reason": "value is too high", "param": "count"})
        start, end = int(p["start_timestamp"]), int(p["end_timestamp"])
        rows = [t for t in self.trades if start <= t["timestamp"] <= end and t["timestamp"] >= self.trade_floor_ms]
        rows.sort(key=lambda t: (t["timestamp"], int(t["trade_id"])))
        if p.get("sorting") == "desc":
            rows.reverse()
        return {"trades": rows[:cnt], "has_more": len(rows) > cnt}


# -- synthetic datasets ----------------------------------------------------------------------------------

def make_ohlc(first_ts, n, step, base=40.0):
    return [[first_ts + i * step, base + i % 7, base + 1 + i % 7, base - 1 + i % 7, base + 0.5 + i % 7] for i in range(n)]


def make_perp(first_ts, n, step):
    return [[first_ts + i * step, 100.0 + i, 101.0 + i, 99.0 + i, 100.5 + i, 1000.0 + i, 10.0 + i] for i in range(n)]


def make_funding(first_ts, n):
    return [{"timestamp": first_ts + i * HOUR, "index_price": 50000.0 + i, "interest_8h": 1e-6 * i,
             "interest_1h": 1e-7 * i, "prev_index_price": 49999.0 + i} for i in range(n)]


def make_trade(ts, tid, name="BTC-27NOV26-88000-C"):
    return {"timestamp": ts, "trade_id": str(tid), "trade_seq": tid % 1000, "instrument_name": name, "price": 0.01,
            "amount": 1.0, "direction": "buy", "iv": 40.0, "index_price": 80000.0, "mark_price": 0.01,
            "tick_direction": 1, "starbase_match_id": 123456789, "starbase_timestamp": ts * 1000}


def make_chain(now_ms=NOW, underlying=82000.0, strikes=range(60000, 110001, 1000)):
    """Synthetic summary rows: expiries 8OCT26 (already expired at 08:00), 9OCT26, 30OCT26, 25DEC26, 26MAR27."""
    rows = []
    for exp in ("8OCT26", "9OCT26", "30OCT26", "25DEC26", "26MAR27"):
        for k in strikes:
            for cp in ("C", "P"):
                rows.append({"instrument_name": "BTC-%s-%d-%s" % (exp, k, cp), "bid_price": 0.01, "ask_price": 0.011,
                             "mark_price": 0.0105, "mark_iv": 40.0 + (k - underlying) / 5000.0, "open_interest": 10.0,
                             "volume": 1.0, "volume_usd": 80000.0, "last": 0.01, "high": 0.02, "low": 0.005,
                             "price_change": 0.0, "underlying_price": underlying, "underlying_index": "BTC-" + exp,
                             "interest_rate": 0.0, "creation_timestamp": now_ms, "base_currency": "BTC"})
    return rows
