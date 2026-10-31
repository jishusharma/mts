"""hot_wallet_watch: ETH balance drop >= 20 % within 10 min lights the alert; RPC stubbed, no network."""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hot_wallet_watch as h


def rpc(wei_by_call):
    it = iter(wei_by_call)

    def post(url, payload):
        v = next(it)
        if isinstance(v, Exception):
            raise v
        return {"jsonrpc": "2.0", "id": 1, "result": hex(v)}
    return post


ETH = 10 ** 18


class Watch(unittest.TestCase):
    def test_wallet_list_is_labelled_addresses(self):
        self.assertTrue(h.WALLETS)
        for name, addr in h.WALLETS.items():
            self.assertRegex(addr, r"^0x[0-9a-fA-F]{40}$")
            self.assertTrue(re.match(r"^(Binance|Bybit|OKX|Coinbase)", name))

    def test_balance_parses_hex_wei_to_eth(self):
        self.assertEqual(h.balance_eth("0x" + "1" * 40, post=rpc([5 * ETH])), 5.0)

    def test_drop_of_20_percent_in_10_min_alerts(self):
        w = h.Watcher()
        self.assertEqual(w.update("Binance 14", 1000.0, 0), [])
        self.assertEqual(w.update("Binance 14", 900.0, 300), [])      # -10 %
        a = w.update("Binance 14", 790.0, 540)                         # -21 % vs t=0
        self.assertEqual(len(a), 1)
        self.assertIn("Binance 14", a[0])

    def test_slow_drain_beyond_window_does_not_alert(self):
        w = h.Watcher()
        w.update("OKX 1", 1000.0, 0)
        w.update("OKX 1", 900.0, 400)
        self.assertEqual(w.update("OKX 1", 790.0, 800), [])  # t=0 sample is 800 s old; vs 900 only -12 %

    def test_poll_survives_rpc_error_and_reports_it(self):
        w = h.Watcher()
        names = list(h.WALLETS)
        seq = [ETH * 100] + [OSError("down")] * (len(names) - 1)
        alerts, errors = h.poll(w, 0, post=rpc(seq))
        self.assertEqual(alerts, [])
        self.assertEqual(len(errors), len(names) - 1)


if __name__ == "__main__":
    unittest.main()
