"""Exchange hot-wallet drain watch (REPORT N4): public ETH JSON-RPC, no keys, no scheduler.
Run by hand (`python scripts/dev/hot_wallet_watch.py`); polls until Ctrl-C and prints a line when a wallet's ETH
balance falls >= DROP_PCT within WINDOW_S. Observation only.

DECISION (OURS): wallet list = Etherscan-labelled exchange addresses only (SOURCED: Etherscan name tags; re-check on
etherscan.io/accounts/label/exchange before relying on one). DROP_PCT / WINDOW_S are OURS (20 % / 10 min)."""
import json
import sys
import time
import urllib.request

RPC_URL = "https://ethereum-rpc.publicnode.com"
DROP_PCT = 20.0
WINDOW_S = 600
POLL_S = 60
# Each address verified against its public Etherscan label (read-only web, 2026-10-31):
#   Binance 14   0x28C6c06298d514Db089934071355E5743bf21d60  label "Binance 14"          https://etherscan.io/address/0x28C6c06298d514Db089934071355E5743bf21d60
#   Binance 7    0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8  label "Binance: Cold Wallet 7" https://etherscan.io/address/0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8
#   Coinbase 1   0x71660c4005BA85c37ccec55d0C4493E66Fe775d3  label "Coinbase 1"           https://etherscan.io/address/0x71660c4005BA85c37ccec55d0C4493E66Fe775d3
#   OKX 1        0x6cC5F688a315f3dC28A7781717a9A798a59fDA7b  label "OKX" (Exchange)       https://etherscan.io/address/0x6cC5F688a315f3dC28A7781717a9A798a59fDA7b
#   Bybit hot    0xf89d7b9c864f589bbF53a82105107622B35EaA40  label "Bybit: Hot Wallet"    https://etherscan.io/address/0xf89d7b9c864f589bbF53a82105107622B35EaA40
WALLETS = {
    "Binance 14": "0x28C6c06298d514Db089934071355E5743bf21d60",
    "Binance 7": "0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8",
    "Coinbase 1": "0x71660c4005BA85c37ccec55d0C4493E66Fe775d3",
    "OKX 1": "0x6cC5F688a315f3dC28A7781717a9A798a59fDA7b",
    "Bybit hot": "0xf89d7b9c864f589bbF53a82105107622B35EaA40",
}


def http_post(url, payload):
    req = urllib.request.Request(url, json.dumps(payload).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def balance_eth(addr, post=http_post, url=RPC_URL):
    out = post(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBalance", "params": [addr, "latest"]})
    if "result" not in out:
        raise ValueError("rpc error: %s" % str(out.get("error"))[:100])
    return int(out["result"], 16) / 1e18


class Watcher:
    def __init__(self, drop_pct=DROP_PCT, window_s=WINDOW_S):
        self.drop_pct, self.window_s, self.hist = drop_pct, window_s, {}

    def update(self, name, eth, t):
        h = self.hist.setdefault(name, [])
        h.append((t, eth))
        h[:] = [x for x in h if t - x[0] <= self.window_s]
        peak = max(v for _, v in h)
        if peak > 0 and (peak - eth) / peak * 100 >= self.drop_pct:
            return ["%s: %.0f -> %.0f ETH (-%.0f%% in %d s)" % (name, peak, eth, (peak - eth) / peak * 100, t - h[0][0])]
        return []


def poll(watcher, t, post=http_post):
    alerts, errors = [], []
    for name, addr in WALLETS.items():
        try:
            alerts += watcher.update(name, balance_eth(addr, post=post), t)
        except (OSError, ValueError, KeyError) as e:
            errors.append("%s: %s" % (name, e))  # fail visible: an unreadable wallet is reported, never assumed fine
    return alerts, errors


def main():
    w = Watcher()
    while True:
        alerts, errors = poll(w, time.time())
        for line in alerts:
            print("DRAIN?", line, flush=True)
        for line in errors:
            print("rpc error", line, file=sys.stderr, flush=True)
        time.sleep(POLL_S)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
