"""Live Aid open-interest poller (card live-aid-oi-poller-all-venues-1110).

Fetches BTC USDT-perp open interest from public market-data endpoints only (no keys, no account or order endpoints) and writes
runtime_data/live_aid/oi_snapshot.js atomically as  window.LIVEAID_OI_SNAP = {t, venues: {NAME: {btc, px, t, err}}}.
The Live Aid page reloads that file every 30 s and shows a venue only when its t is under 60 s old (fail closed).
Hosts that the ISP DNS-blocks are reached by DoH + pinned IP + SNI (MyTradingSys/runtime/doh_http.py); no machine DNS change.
No state between runs: every cycle builds the snapshot from scratch; nothing is read back from the previous file.

Run by hand (no scheduler, no service):  python MyTradingSys/tools/live_aid/oi_poller.py            (Ctrl+C to stop)
                                          python MyTradingSys/tools/live_aid/oi_poller.py --cycles 2  (two cycles, then exit)

Contract sizes, each SOURCED from the venue docs (url) and cross-checked against a live reply on 2026-11-10:
  BINANCE   openInterest is in BTC (1 BTCUSDT contract = 1 BTC)   https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest
  OKX       oiCcy is the OI in BTC (oi = contracts, ctVal 0.01 BTC) https://www.okx.com/docs-v5/en/#public-data-rest-api-get-open-interest
  BITGET    openInterestList[0].size is in BTC (base coin)         https://www.bitget.com/api-doc/contract/market/Get-Open-Interest
  BITMEX    XBTUSDT openInterest is in contracts; BTC = openInterest / underlyingToPositionMultiplier (read from the same reply)
            https://www.bitmex.com/api/explorer/#!/Instrument/Instrument_get
            BitMEX answers 403 (CloudFront geo-block) from India, so this adapter could not be checked against a live reply here.
  KRAKEN    PF_XBTUSD openInterest is in BTC (multi-collateral linear, 1 contract = 1 BTC)  https://docs.kraken.com/api/docs/futures-api/trading/get-tickers
  BINGX     openInterest is the USDT value of open positions (measured: 1.07e9 vs price 74.7k = 14.3k BTC; as BTC it would be 1 bn BTC), BTC = value / price
            https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Get%20Swap%20Open%20Positions
  HTX       linear-swap BTC-USDT: amount is the OI in BTC (volume = contracts, 1 contract = 0.001 BTC)  https://www.htx.com/en-us/opend/newApiPages/?id=8cb81b5d-77b5-11ed-9966-0242ac110003
  MEXC      holdVol is in contracts, BTC = holdVol x contractSize (0.0001 BTC, from /contract/detail)  https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-contract-information
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "runtime_data" / "live_aid" / "oi_snapshot.js"
INTERVAL_S = 30
VENUE_TIMEOUT_S = 8.0     # per HTTP call
POLL_DEADLINE_S = 20.0    # OURS: a whole cycle never waits longer than this for a slow venue


def _num(x) -> float:
    v = float(x)
    if not math.isfinite(v):
        raise ValueError("non-finite number")
    return v


# ---- pure parsers: dict of decoded reply bodies -> (btc, px) --------------------------------------------------------
def parse_binance(r):
    return _num(r["oi"]["openInterest"]), _num(r["px"]["markPrice"])


def parse_okx(r):
    return _num(r["oi"]["data"][0]["oiCcy"]), _num(r["px"]["data"][0]["last"])


def parse_bitget(r):
    return _num(r["oi"]["data"]["openInterestList"][0]["size"]), _num(r["px"]["data"][0]["lastPr"])


def parse_bitmex(r):
    i = next(x for x in r["inst"] if x["symbol"] == "XBTUSDT")
    return _num(i["openInterest"]) / _num(i["underlyingToPositionMultiplier"]), _num(i["markPrice"])


def parse_kraken(r):
    t = next(x for x in r["tk"]["tickers"] if x["symbol"] == "PF_XBTUSD")
    return _num(t["openInterest"]), _num(t["markPrice"])


def parse_bingx(r):
    px = _num(r["px"]["data"]["price"])
    return _num(r["oi"]["data"]["openInterest"]) / px, px


def parse_htx(r):
    d = next(x for x in r["oi"]["data"] if x["contract_code"] == "BTC-USDT")
    return _num(d["amount"]), _num(r["px"]["tick"]["close"])


def parse_mexc(r):
    cs = _num(r["detail"]["data"]["contractSize"])
    t = r["tk"]["data"]
    return _num(t["holdVol"]) * cs, _num(t["lastPrice"])


# name -> (use DoH pinning, {reply key: url}, parser)
VENUES = {
    "BINANCE": (True, {"oi": "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT",
                       "px": "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT"}, parse_binance),
    "OKX": (True, {"oi": "https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId=BTC-USDT-SWAP",
                   "px": "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT-SWAP"}, parse_okx),
    "BITGET": (True, {"oi": "https://api.bitget.com/api/v2/mix/market/open-interest?symbol=BTCUSDT&productType=USDT-FUTURES",
                      "px": "https://api.bitget.com/api/v2/mix/market/ticker?symbol=BTCUSDT&productType=USDT-FUTURES"}, parse_bitget),
    "BITMEX": (True, {"inst": "https://www.bitmex.com/api/v1/instrument?symbol=XBTUSDT"}, parse_bitmex),
    "KRAKEN": (True, {"tk": "https://futures.kraken.com/derivatives/api/v3/tickers"}, parse_kraken),
    "BINGX": (True, {"oi": "https://open-api.bingx.com/openApi/swap/v2/quote/openInterest?symbol=BTC-USDT",
                     "px": "https://open-api.bingx.com/openApi/swap/v2/quote/price?symbol=BTC-USDT"}, parse_bingx),
    "HTX": (False, {"oi": "https://api.hbdm.com/linear-swap-api/v1/swap_open_interest?contract_code=BTC-USDT",
                    "px": "https://api.hbdm.com/linear-swap-ex/market/detail/merged?contract_code=BTC-USDT"}, parse_htx),
    "MEXC": (False, {"tk": "https://contract.mexc.com/api/v1/contract/ticker?symbol=BTC_USDT",
                     "detail": "https://contract.mexc.com/api/v1/contract/detail?symbol=BTC_USDT"}, parse_mexc),
}


def http_json(url: str, pinned: bool):
    """GET one public URL -> decoded JSON. Pinned = DoH + IP + SNI (ISP-blocked hosts)."""
    if pinned:
        from MyTradingSys.runtime.doh_http import urlopen_pinned
        with urlopen_pinned(url, timeout=VENUE_TIMEOUT_S) as r:
            return json.loads(r.read().decode("utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": "mts-live-aid-oi-poller/1"})
    with urllib.request.urlopen(req, timeout=VENUE_TIMEOUT_S) as r:
        return json.loads(r.read().decode("utf-8"))


def poll_venue(name: str, fetch, now) -> dict:
    """One venue -> {btc, px, t, err}. Any failure or implausible number = btc/px/t None + err text (never a guess)."""
    pinned, urls, parser = VENUES[name]
    try:
        replies = {k: fetch(u, pinned) for k, u in urls.items()}
        btc, px = parser(replies)
        if not (btc > 0 and px > 0):
            raise ValueError(f"implausible btc={btc} px={px}")
        return {"btc": btc, "px": px, "t": int(now() * 1000), "err": ""}
    except Exception as e:  # noqa: BLE001 - one venue failing must never stop the others
        return {"btc": None, "px": None, "t": None, "err": f"{type(e).__name__}: {e}"[:160]}


def poll_once(fetch=http_json, now=time.time, deadline=POLL_DEADLINE_S) -> dict:
    """All venues in parallel; a venue still running at the deadline is reported as timed out and not waited for."""
    ex = ThreadPoolExecutor(max_workers=len(VENUES))
    futs = {n: ex.submit(poll_venue, n, fetch, now) for n in VENUES}
    wait(list(futs.values()), timeout=deadline)
    out = {}
    for n, f in futs.items():
        out[n] = f.result() if f.done() else {"btc": None, "px": None, "t": None, "err": f"timeout after {deadline:g} s"}
    ex.shutdown(wait=False, cancel_futures=True)
    return {"t": int(now() * 1000), "venues": out}


def write_snapshot(snap: dict, path: Path = OUT) -> None:
    """Atomic: write a temp file beside the target, then os.replace (a page reading mid-write sees old or new, never half)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write("window.LIVEAID_OI_SNAP = " + json.dumps(snap, separators=(",", ":")) + ";\n")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Live Aid BTC perp open-interest poller (public data, run by hand)")
    ap.add_argument("--cycles", type=int, default=0, help="stop after N cycles (0 = until Ctrl+C)")
    ap.add_argument("--interval", type=float, default=INTERVAL_S)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    n = 0
    try:
        while True:
            t0 = time.time()
            snap = poll_once()
            write_snapshot(snap, Path(a.out))
            got = {k: round(v["btc"]) for k, v in snap["venues"].items() if v["btc"]}
            bad = {k: v["err"] for k, v in snap["venues"].items() if not v["btc"]}
            print(f"[oi_poller] {time.strftime('%H:%M:%S')} ok {len(got)}/{len(VENUES)} BTC {got}" + (f" failed {bad}" if bad else ""), flush=True)
            n += 1
            if a.cycles and n >= a.cycles:
                return 0
            time.sleep(max(0.0, a.interval - (time.time() - t0)))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
