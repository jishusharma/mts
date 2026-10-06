"""Single source of the net_rr floor: MyTradingSys/system/net_rr_floor.json.

Python (verdict.py, math_object_builder.py), PowerShell (start-trading-day.ps1 Compute-Verdict) and Java
(NetRrFloor.java) must all take the number from that file, every cycle, with no second copy anywhere.
Expected values are by hand: floor F, candidate net_rr N -> passes iff N >= F.
  N = 1.50: floor 1.25 -> pass; floor 2.00 -> WAIT_RR "net_rr 1.50 < 2.00".
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "runtime"))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest"))
sys.dont_write_bytecode = True

import net_rr_floor as nrf  # noqa: E402
from verdict import compute_verdict  # noqa: E402
from math_object_builder import build_math_object  # noqa: E402

PS1 = ROOT / "scripts" / "core" / "start-trading-day.ps1"
PWSH = shutil.which("pwsh") or shutil.which("powershell")


def snap(net_rr=1.5, sanity=False, proof=4):
    """Short candidate at the daily VAH, trigger_ready, proof `proof`. net_rr_sanity is Java's old 2.0 flag."""
    return {"timestamp_utc": "2026-10-02T13:40:10Z", "current_price": 87000.0,
            "conditions": {"vp_shape": "TWOPEAK", "price_vs_va": "in_va", "cvd_slope": "flat"},
            "daily_vp": {"poc": 86800.0, "vah": 87064.46, "val": 86143.76},
            "structure": {"1h": {"swing_high": 87500.0, "swing_low": 86000.0},
                          "15m": {"swing_high": 87300.0, "swing_low": 86500.0}},
            "setup_candidates": [{"rank": 1, "direction": "short", "setup_type": "ct_short",
                                  "zone": {"name": "daily_vah", "price": 87064.46, "type": "daily_vah"},
                                  "math": {"net_rr": net_rr, "net_rr_sanity": sanity, "tier": "trigger_ready",
                                           "stop": 87200.0, "target": 86200.0, "gross_rr": 2.0, "rr_sanity": True},
                                  "proof": {"book_imbalance": 1.0, "finished_auction": {"direction": ""}},
                                  "score": {"proof_count": proof, "raw": 70, "confidence": "B"}}]}


class FloorFileMixin:
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.floor_file = self.tmp / "net_rr_floor.json"
        self.set_floor(1.25)
        p = mock.patch.object(nrf, "FLOOR_PATH", self.floor_file)
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def set_floor(self, v):
        self.floor_file.write_text(json.dumps({"net_rr_floor": v}), encoding="utf-8", newline="\n")


class TestLoader(FloorFileMixin, unittest.TestCase):
    def test_reads_value(self):
        self.assertEqual(nrf.load_floor(), 1.25)
        self.set_floor(2)
        self.assertEqual(nrf.load_floor(), 2.0)  # re-read on every call, no caching

    def test_shipped_file_is_valid(self):
        self.assertGreater(nrf.load_floor(ROOT / "MyTradingSys" / "system" / "net_rr_floor.json"), 0)

    def test_fails_closed(self):
        for bad in ('{"net_rr_floor": "x"}', '{"net_rr_floor": true}', '{"net_rr_floor": 0}', '{"net_rr_floor": -1}',
                    '{"net_rr_floor": NaN}', '{"other": 1}', "not json", "[]"):
            self.floor_file.write_text(bad, encoding="utf-8")
            with self.assertRaises(nrf.NetRrFloorError, msg=bad):
                nrf.load_floor()
        self.floor_file.unlink()
        with self.assertRaises(nrf.NetRrFloorError):
            nrf.load_floor()


class TestVerdictPy(FloorFileMixin, unittest.TestCase):
    def test_floor_comes_from_the_file_not_from_java_sanity_flag(self):
        # Java baked net_rr_sanity=False (its 2.0) but net 1.5 >= floor 1.25 -> must pass the gate.
        v = compute_verdict(snap(1.5, sanity=False), "aligned")
        self.assertEqual(v["verdict"], "WATCH")
        self.set_floor(2.0)
        v = compute_verdict(snap(1.5, sanity=True), "aligned")  # sanity flag True must not rescue it
        self.assertEqual((v["verdict"], v["reason"]), ("WAIT_RR", "net_rr 1.50 < 2.00"))

    def test_boundary_is_inclusive(self):
        self.assertNotEqual(compute_verdict(snap(1.25), "aligned")["verdict"], "WAIT_RR")
        self.assertEqual(compute_verdict(snap(1.24), "aligned")["verdict"], "WAIT_RR")

    def test_unreadable_floor_raises(self):
        self.floor_file.unlink()
        with self.assertRaises(nrf.NetRrFloorError):
            compute_verdict(snap(5.0), "aligned")


class TestMathObjectPy(FloorFileMixin, unittest.TestCase):
    def flag(self, net, sanity):
        s = snap(net, sanity)
        s["setup_candidates"][0]["math"]["distance_pct"] = 0.1
        return build_math_object(s)["hard_stops_compiled"]["top_candidate_rr_below_threshold"]

    def test_hard_stop_uses_file_floor(self):
        self.assertFalse(self.flag(1.5, sanity=False))   # net 1.5 >= 1.25
        self.set_floor(2.0)
        self.assertTrue(self.flag(1.5, sanity=True))     # net 1.5 < 2.0 whatever Java said

    def test_unreadable_floor_fails_closed(self):
        self.floor_file.unlink()
        self.assertTrue(self.flag(9.0, sanity=True))


def _ps_function(name):
    lines = PS1.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("function %s " % name))
    end = next(i for i in range(start + 1, len(lines)) if lines[i] == "}")
    return "\n".join(lines[start:end + 1])


@unittest.skipUnless(PWSH, "no PowerShell on PATH")
class TestWrapperPs(unittest.TestCase):
    def run_ps(self, steps, net_rr=1.5):
        """steps: list of floor values (or None = delete the file). One PowerShell process runs Compute-Verdict
        once per step, rewriting the floor file between calls - the same process, like the live loop."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "MyTradingSys" / "system").mkdir(parents=True)
        (tmp / "snap.json").write_text(json.dumps(snap(net_rr, sanity=False)), encoding="utf-8")
        ff = tmp / "MyTradingSys" / "system" / "net_rr_floor.json"
        body = ["$R = '%s'" % str(tmp).replace("'", "''"), "$ff = '%s'" % str(ff).replace("'", "''"),
                "$snap = Get-Content '%s' -Raw | ConvertFrom-Json" % (tmp / "snap.json"), "$out = @()"]
        for f in steps:
            if f is None:
                body.append("Remove-Item -ErrorAction SilentlyContinue $ff")
            else:
                body.append("Set-Content -Path $ff -Value '{\"net_rr_floor\": %s}' -Encoding UTF8" % f)
            body.append("$v = Compute-Verdict $snap 'aligned'; $out += [PSCustomObject]@{verdict=$v.verdict; reason=$v.reason}")
        body.append("$out | ConvertTo-Json -Compress -AsArray")
        script = tmp / "run.ps1"
        script.write_text(_ps_function("Get-NetRrFloor") + "\n" + _ps_function("Compute-Verdict") + "\n" + "\n".join(body),
                          encoding="utf-8")
        r = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(script)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)

    def test_wrapper_rereads_floor_each_cycle(self):
        # net 1.5: floor 1.25 -> past the net_rr gate (WATCH, proof 4); floor 2.0 -> WAIT_RR; back to 1.25 -> WATCH. No restart.
        out = self.run_ps([1.25, 2.0, 1.25])
        self.assertEqual([o["verdict"] for o in out], ["WATCH", "WAIT_RR", "WATCH"])
        self.assertEqual(out[1]["reason"], "net_rr 1.50 < 2.00")

    def test_wrapper_fails_closed_when_floor_unreadable(self):
        out = self.run_ps([None])
        self.assertEqual(out[0]["verdict"], "WAIT_RR")
        self.assertIn("floor unreadable", out[0]["reason"])

    def test_wrapper_matches_python_on_the_boundary(self):
        for net, floor in ((1.25, 1.25), (1.24, 1.25), (2.0, 2.0)):
            ps = self.run_ps([floor], net_rr=net)[0]["verdict"]
            with tempfile.TemporaryDirectory() as d:
                ff = Path(d) / "f.json"
                ff.write_text(json.dumps({"net_rr_floor": floor}), encoding="utf-8")
                with mock.patch.object(nrf, "FLOOR_PATH", ff):
                    py = compute_verdict(snap(net), "aligned")["verdict"]
            self.assertEqual(ps, py, (net, floor))


class TestNoSecondCopy(unittest.TestCase):
    """Static guard: no gate site may carry its own numeric floor."""
    SITES = ["scripts/core/start-trading-day.ps1", "MyTradingSys/backtest/verdict.py", "MyTradingSys/runtime/math_object_builder.py",
             "src/main/java/datafeed/SetupCandidatesBuilder.java", "src/main/java/datafeed/ExtraSetupBuilder.java"]
    # `net_rr`/`netRR`/`_net` compared to a number literal; or a min_net_rr config key with a number.
    LITERAL = re.compile(r"(net_?rr\w*|_net)\s*(>=|<=|<|>|-ge|-lt)\s*\d|min_net_rr\"?\s*[:=]\s*\d", re.I)

    def test_no_numeric_floor_in_gate_sites(self):
        sites = list(self.SITES)
        ex = "MyTradingSys/execution/auto_trader.py"
        sites.append(ex + ".new" if (ROOT / (ex + ".new")).exists() else ex)  # staged copy until the supervisor promotes it
        hits = []
        for rel in sites:
            for n, line in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
                code = line.split("#", 1)[0] if rel.endswith((".py", ".ps1")) else line.split("//", 1)[0]
                if self.LITERAL.search(code):
                    hits.append("%s:%d: %s" % (rel, n, line.strip()))
        self.assertEqual(hits, [])

    def test_executor_config_file_carries_no_floor(self):
        for rel in ("MyTradingSys/execution/auto_trader_config.json.new", "MyTradingSys/execution/auto_trader_config.json"):
            p = ROOT / rel
            if p.exists():
                self.assertNotIn("min_net_rr", json.loads(p.read_text(encoding="utf-8")).get("tom", {}), rel)
                break


if __name__ == "__main__":
    unittest.main()
