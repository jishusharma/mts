"""flow_read.py fixtures (no network) + the fapi-needs-binance_doh lint (operator 2026-11-12: today's read fell back to Bybit)."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import flow_read as fr  # noqa: E402

# Grandfathered raw-fapi callers (exist before 2026-11-12); a NEW file calling fapi without binance_doh fails the lint.
GRANDFATHERED = {
    "MyTradingSys/research/coinglass_field_guide_2026-11-01/depth_band_check.py",
    "MyTradingSys/research/eagle_eyes_picture_2026-10-28/flow_state_pairs_1m.py",
    "MyTradingSys/research/orderflow_views_2026-10-14/study.py",
    "scripts/dev/test_analyst_levels.py",
}
M15 = 900_000


def k(t, o, h, l, c, v, tb):
    return [t, str(o), str(h), str(l), str(c), str(v), t + M15 - 1, "0", 1, str(tb), "0", "0"]


class Flow(unittest.TestCase):
    def test_delta_is_two_tb_minus_v(self):
        self.assertAlmostEqual(fr.kl([k(0, 1, 2, 1, 2, 100, 30)])[0]["delta"], -40.0)

    def test_labels(self):
        self.assertEqual(fr.label(+5, +500, 100000), "NEW LONGS")
        self.assertEqual(fr.label(+5, -500, 100000), "SHORT COVER")
        self.assertEqual(fr.label(-5, -500, 100000), "LONGS EXIT")
        self.assertEqual(fr.label(-5, +500, 100000), "NEW SHORTS")
        self.assertEqual(fr.label(-5, +5, 100000), "flat")
        self.assertEqual(fr.label(-5, None, 100000), "n/a")

    def test_absorb_buy_when_low_holds(self):
        sell = {"o": 100, "h": 101, "l": 90, "c": 95, "v": 100.0, "delta": -20.0}
        self.assertEqual(fr.absorb(sell, {"l": 91, "h": 99}, 2.0), "ABSORB-BUY")
        self.assertEqual(fr.absorb(sell, {"l": 85, "h": 99}, 2.0), "")       # low broke
        self.assertEqual(fr.absorb(sell, None, 0.5), "")                     # not heavy volume

    def test_build_rows_and_oi(self):
        p = fr.kl([k(0, 10, 11, 9, 10.5, 100, 50), k(M15, 10.5, 12, 10, 11, 100, 60), k(2 * M15, 11, 11, 10, 10, 100, 40)])
        s = fr.kl([k(M15, 1, 1, 1, 1, 10, 7)])
        rows = fr.build_rows(p, s, {M15: 1000.0, 2 * M15: 800.0}, {M15: 1.5}, {}, {}, M15, M15)
        self.assertEqual([r["t"] for r in rows], [M15, 2 * M15])
        self.assertEqual(rows[0]["oi_chg"], -200.0)
        self.assertEqual(rows[0]["label"], "SHORT COVER")
        self.assertAlmostEqual(rows[0]["spot_delta"], 4.0)
        self.assertIsNone(rows[1]["oi_chg"])

    def test_thresholds_met_missed_pending(self):
        H = fr.TF_MS["4h"]
        lo = 10 * H
        p4 = {lo - H: dict(o=1, h=2, l=1.5, c=1, v=1, delta=0, close_ms=0), lo: dict(o=1, h=2, l=1, c=1.5, v=100, delta=5, close_ms=0)}
        s4 = {lo: dict(o=1, h=2, l=1, c=1, v=1000, delta=50, close_ms=0)}      # +5% of volume
        oi4 = {lo - 3 * H: 1000.0, lo + 2 * H: 940.0}                           # -6%
        fine = {lo + H + i * M15: dict(delta=20.0, v=1, o=1, h=1, l=1, c=1, close_ms=0) for i in range(40)}
        now = lo + H + 40 * M15                                                  # 10 h after the low bar closes
        st = {n: s for n, s, _ in fr.thresholds(p4, s4, oi4, fine, now, 6 * H)}
        self.assertEqual(st["OI -5% into low"], "MET")
        self.assertEqual(st["taker buy>sell 3% on low bar"], "MET")
        self.assertEqual(st["spot delta >= +670 BTC in 12h after"], "MET")      # 800
        s4[lo]["delta"] = 10.0
        oi4[lo + 2 * H] = 990.0
        fine2 = {t: dict(b, delta=5.0) for t, b in fine.items()}                # 200 BTC so far
        st = {n: s for n, s, _ in fr.thresholds(p4, s4, oi4, fine2, now, 6 * H)}
        self.assertEqual(st["OI -5% into low"], "MISSED")
        self.assertEqual(st["taker buy>sell 3% on low bar"], "MISSED")
        self.assertEqual(st["spot delta >= +670 BTC in 12h after"], "PENDING")
        late = lo + H + 12 * 3_600_000 + 1
        st = {n: s for n, s, _ in fr.thresholds(p4, s4, oi4, fine2, late, 6 * H)}
        self.assertEqual(st["spot delta >= +670 BTC in 12h after"], "MISSED")

    def test_parse_dur(self):
        self.assertEqual(fr.parse_dur("9h"), 9 * 3_600_000)
        with self.assertRaises(ValueError):
            fr.parse_dur("9")


class FapiNeedsDoh(unittest.TestCase):
    def test_no_new_raw_fapi_callers(self):
        files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "scripts/dev/*.py", "MyTradingSys/research/*.py"],
                               capture_output=True, text=True).stdout.split()
        bad = []
        for rel in files:
            if rel in GRANDFATHERED or rel.endswith("test_flow_read.py"):
                continue
            src = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
            if "fapi.binance.com" in src and "binance_doh" not in src:
                bad.append(rel)
        self.assertFalse(bad, f"calls fapi.binance.com without binance_doh (DNS is blocked here; use MyTradingSys/runtime/binance_doh): {bad}")


class XliqLine(unittest.TestCase):
    """card live-aid-xliq-1113: one cross-exchange liquidation line per wake, from the collector feed."""
    NOW = 1_794_600_000_000

    def _feed(self, tmp, t, venues):
        p = Path(tmp) / "xliq_feed.js"
        p.write_text("window.LIVEAID_XLIQ = " + __import__("json").dumps({"t": t, "venues": venues}) + ";", encoding="utf-8")
        return p

    def _v(self, **k):
        d = {"long15": 0, "short15": 0, "n15": 0, "baseline": "building", "n7d": 5, "big": 0, "bigside": None, "err": ""}
        d.update(k)
        return d

    def test_building_line_never_says_big(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = self._feed(tmp, self.NOW - 5000, {"BYBIT": self._v(long15=1_250_000, short15=40_000), "OKX": self._v(long15=900)})
            line = fr.xliq_line(p, self.NOW)
        self.assertEqual(line, "xliq 15m forced liquidations: Bybit long $1.25M / short $40k | Okx long $900 / short $0 | no BIG print (baseline building: Bybit, Okx)")

    def test_big_line_and_missing_or_stale_feed(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = self._feed(tmp, self.NOW, {"BYBIT": self._v(baseline="ready", long15=3_000_000, big=2, bigside="long")})
            self.assertIn("BIG: Bybit long", fr.xliq_line(p, self.NOW))
            self.assertIn("feed stale (200 s old)", fr.xliq_line(p, self.NOW + 200_000))
            self.assertIn("no liquidation feed", fr.xliq_line(Path(tmp) / "absent.js", self.NOW))

    def test_main_prints_the_line(self):
        src = (ROOT / "scripts" / "dev" / "flow_read.py").read_text(encoding="utf-8")
        self.assertIn("print(xliq_line())", src)


if __name__ == "__main__":
    unittest.main()
