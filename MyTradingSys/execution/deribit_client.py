"""
MyTradingSys/execution/deribit_client.py

Phase 1 of T050 (see MyTradingSys/items/T050_deribit_execution_layer.md):
read-only, unauthenticated connectivity to Deribit's testnet. No API key
used or required at this phase - this only proves the network path and
the client shape before any credential exists.

Module boundary: this file does not import, call, or modify anything in
MyTradingSys/runtime/. It is a standalone read. Per PROJECT_VISION.md
doctrine, modules never gate core behavior - nothing here is wired into
the candle-close loop yet, and phase 1 places no orders.

Run directly:
    python MyTradingSys/execution/deribit_client.py

sys.dont_write_bytecode set per USER.md CONFIG convention.
"""
import sys
sys.dont_write_bytecode = True

import json
import urllib.request
import urllib.error

TESTNET_BASE = "https://test.deribit.com/api/v2"


def get_ticker(instrument_name: str = "BTC-PERPETUAL", base_url: str = TESTNET_BASE) -> dict:
    """Fetch a public ticker. No auth. Raises on any non-200 or network failure -
    this phase does not swallow errors, since T050's own dependency list calls
    out that failure handling is the part that actually needs design, not the
    happy path."""
    url = f"{base_url}/public/ticker?instrument_name={instrument_name}"
    req = urllib.request.Request(url, headers={"User-Agent": "MTS-T050-phase1/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
            raise RuntimeError(f"unexpected HTTP status {resp.status} from {url}")
        body = json.loads(resp.read().decode("utf-8"))
    if "result" not in body:
        raise RuntimeError(f"unexpected response shape, no 'result' key: {body}")
    return body["result"]


def main() -> int:
    try:
        result = get_ticker()
    except urllib.error.URLError as e:
        print(f"FAIL: could not reach {TESTNET_BASE} - {e}")
        print("If this is a network/proxy restriction, run this from the desktop directly,")
        print("not from any sandboxed bridge or CI environment.")
        return 1
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        return 1

    print("OK: reached Deribit testnet public API")
    print(f"  instrument:    {result.get('instrument_name')}")
    print(f"  mark_price:    {result.get('mark_price')}")
    print(f"  best_bid:      {result.get('best_bid_price')}")
    print(f"  best_ask:      {result.get('best_ask_price')}")
    print(f"  state:         {result.get('state')}")
    print(f"  timestamp_ms:  {result.get('timestamp')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
