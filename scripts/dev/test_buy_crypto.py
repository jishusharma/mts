import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import buy_crypto as b


class T(unittest.TestCase):
    def test_pct(self):
        self.assertAlmostEqual(b.pct(110, 100), 10.0)
        self.assertIsNone(b.pct(None, 100))
        self.assertIsNone(b.pct(5, 0))

    def test_scenario_uses_down_beta_below_up_beta_above(self):
        # ZEC down 1.44, up 1.84 (ALT_PICKS 11-03); BTC 80k -> 72k is -10 %
        self.assertAlmostEqual(b.scenario("ZEC", 80000, 72000), -14.4)
        self.assertAlmostEqual(b.scenario("ZEC", 70000, 77000), 10.0 * 1.84)
        self.assertIsNone(b.scenario("INJ", 80000, 72000))      # not measured -> no number
        self.assertIsNone(b.scenario("PLUME", 80000, 72000))    # down-beta n/a

    def test_price_at_picks_nearest_day(self):
        d = 86400000
        pr = [[b.SINCE_TS * 1000 - d, 1], [b.SINCE_TS * 1000 + 1000, 2], [b.SINCE_TS * 1000 + d, 3]]
        self.assertEqual(b.price_at(pr, b.SINCE_TS), 2)
        self.assertIsNone(b.price_at([], b.SINCE_TS))

    def test_build_coin_relative_to_btc(self):
        row = {"id": "x", "current_price": 120.0, "price_change_percentage_7d_in_currency": 5.0,
               "price_change_percentage_30d_in_currency": -2.0, "ath_change_percentage": -40}
        c = b.build_coin("ZEC", "leader", row, 10000.0, [[b.SINCE_TS * 1000, 100.0]], 75000, -3.0, -1.0)
        self.assertAlmostEqual(c["since_1103"], 20.0)
        self.assertAlmostEqual(c["vs_btc_7d"], 8.0)
        self.assertAlmostEqual(c["vs_btc_since"], 21.0)
        self.assertEqual(c["inr"], 10000.0)
        self.assertAlmostEqual(c["scen"]["72000"], (72000 / 75000 - 1) * 100 * 1.44)

    def test_alt_proxy_skips_btc_and_stables(self):
        k = "price_change_percentage_30d_in_currency"
        rows = [{"id": "bitcoin", "symbol": "btc", k: 0}, {"id": "tether", "symbol": "usdt", k: 50},
                {"id": "a", "symbol": "a", k: 5}, {"id": "c", "symbol": "c", k: -5}]
        self.assertEqual(b.alt_proxy(rows, 0.0), 50.0)

    def test_coin_list_matches_the_plan(self):
        syms = [c[0] for c in b.COINS]
        self.assertEqual(len(syms), len(set(syms)))
        self.assertEqual(len(syms), 28)
        self.assertEqual({c[2] for c in b.COINS}, {"anchor", "leader", "darkhorse", "watch", "asked", "avoid"})
        # dropped 11-10: never back in a bucket the plan can open (EIGEN is shown as "asked", no buy)
        buyable = {c[0] for c in b.COINS if c[2] in ("anchor", "leader", "darkhorse")}
        self.assertFalse({"GRASS", "AERO", "EIGEN"} & buyable)
        self.assertFalse({"GRASS", "AERO"} & set(syms))


if __name__ == "__main__":
    unittest.main()
