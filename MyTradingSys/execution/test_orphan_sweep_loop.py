"""Offline tests for the scheduled orphan sweep (orphan_watchdog_cli --interval N --confirm-sweeps K).
Spec: orphan_watchdog_cli.py docstring. No exchange: clients are fakes; sleep is injected.
Run: python -m pytest MyTradingSys/execution/test_orphan_sweep_loop.py"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import orphan_watchdog_cli as cli  # noqa: E402
import pm_heartbeat  # noqa: E402


class _Done(BaseException):
    """Ends the loop; BaseException so nothing in the CLI swallows it."""


class Read:
    def __init__(self, size=0, fail=False):
        self.size, self.fail = size, fail

    def get_positions(self, token, currency="BTC", kind="future"):
        if self.fail:
            raise ConnectionError("down")
        return [{"instrument_name": "BTC-PERPETUAL", "size": self.size}] if self.size else []

    def get_open_orders(self, token, instrument_name="BTC-PERPETUAL", type_="all"):
        return []


class LoopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="owloop_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.hb, self.halt, self.log = self.tmp / "hb", self.tmp / "HALT", self.tmp / "log.jsonl"
        self.cfg = self.tmp / "cfg.json"
        self.cfg.write_text(json.dumps({"accounts": {"layer:a:": "jishu_7"}}), encoding="utf-8")
        self.alive_pids = set()

    def loop(self, script, confirm=2, extra=None, secret_check=None):
        """script: one {label: Read} per sweep; before_sweep hooks run before sweep i (by index)."""
        sweeps = iter(script)
        current = {"c": next(sweeps)}
        n = {"i": 0}

        def sleep(_):
            n["i"] += 1
            if extra and n["i"] in extra:
                extra[n["i"]]()
            try:
                current["c"] = next(sweeps)
            except StopIteration:
                raise _Done()
        try:
            cli.main(["--interval", "60", "--confirm-sweeps", str(confirm)],
                     get_client=lambda lab: (current["c"][lab], "tok"), hb_dir=self.hb, halt_path=self.halt,
                     log_path=self.log, alive=lambda pid: pid in self.alive_pids, config_path=self.cfg,
                     secret_check=secret_check, sleep=sleep)
        except _Done:
            pass

    def halt_lines(self):
        return self.halt.read_text(encoding="utf-8").splitlines() if self.halt.exists() else []

    ORPHAN = {"default": Read(), "jishu_7": Read(size=10)}
    FLAT = {"default": Read(), "jishu_7": Read()}
    ERR = {"default": Read(), "jishu_7": Read(fail=True)}

    def test_single_orphan_sweep_does_not_halt(self):
        self.loop([self.ORPHAN, self.FLAT])
        self.assertEqual(self.halt_lines(), [])

    def test_two_consecutive_orphan_sweeps_halt_once_and_loop_continues(self):
        self.loop([self.ORPHAN, self.ORPHAN, self.ORPHAN, self.ORPHAN])
        lines = self.halt_lines()
        self.assertEqual(len(lines), 1)
        self.assertIn("jishu_7", lines[0])
        ev = [json.loads(x)["event"] for x in self.log.open(encoding="utf-8")]
        self.assertEqual(sum(1 for e in ev if e != "orphan_halt"), 4)          # all four sweeps ran
        self.assertEqual(ev.count("orphan_halt"), 1)                           # B148: the halt itself is logged once

    def test_flat_sweep_resets_the_streak(self):
        self.loop([self.ORPHAN, self.FLAT, self.ORPHAN, self.FLAT])
        self.assertEqual(self.halt_lines(), [])

    def test_read_error_neither_counts_nor_resets(self):
        self.loop([self.ORPHAN, self.ERR, self.FLAT])
        self.assertEqual(self.halt_lines(), [])
        self.loop([self.ORPHAN, self.ERR, self.ORPHAN])
        self.assertEqual(len(self.halt_lines()), 1)

    def test_manager_heartbeat_arriving_between_sweeps_prevents_halt(self):
        def pm_starts():
            pm_heartbeat.write_heartbeat("p1", account="jishu_7", pid=77, hb_dir=self.hb)
            self.alive_pids.add(77)
        self.loop([self.ORPHAN, self.ORPHAN], extra={1: pm_starts})
        self.assertEqual(self.halt_lines(), [])

    def test_new_episode_after_recovery_is_reported_again(self):
        self.loop([self.ORPHAN, self.ORPHAN, self.FLAT, self.ORPHAN, self.ORPHAN])
        self.assertEqual(len(self.halt_lines()), 2)

    def test_accounts_without_secret_are_skipped(self):
        seen = []
        clients = {"default": Read(), "jishu_7": Read(size=10)}

        def gc(lab):
            seen.append(lab)
            return clients[lab], "tok"
        rc = cli.main(["--once"], get_client=gc, hb_dir=self.hb, halt_path=self.halt, log_path=self.log,
                      alive=lambda p: False, config_path=self.cfg, secret_check=lambda lab: lab == "default")
        self.assertEqual((rc, seen, self.halt_lines()), (0, ["default"], []))

    def test_has_secret_checks_existence_and_always_keeps_main(self):
        saved = cli.SECRETS_DIR
        self.addCleanup(setattr, cli, "SECRETS_DIR", saved)
        cli.SECRETS_DIR = self.tmp
        (self.tmp / "testnet_jishu_7.secret.json").write_text("{}", encoding="utf-8")
        self.assertEqual([cli.has_secret(x) for x in ("default", "jishu_7", "jishu_8")], [True, True, False])

    def test_once_mode_unchanged_halts_on_first_orphan(self):
        rc = cli.main(["--once"], get_client=lambda lab: (self.ORPHAN[lab], "tok"), hb_dir=self.hb,
                      halt_path=self.halt, log_path=self.log, alive=lambda p: False, config_path=self.cfg)
        self.assertEqual(rc, 3)
        self.assertEqual(len(self.halt_lines()), 1)


class ScheduleTest(unittest.TestCase):
    REPO = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])   # run_staged_tests: temp dir

    def test_confirm_window_outlasts_the_longest_resting_entry(self):
        """A limit entry rests up to max_entry_seconds with open orders and no position_manager yet: the sweep's
        confirmation window, interval x (confirm-1), must be longer or every resting Tom entry would HALT."""
        import re
        import executor
        vbs = (self.REPO / "runtime_data" / "launch-orphan-sweep.vbs").read_text(encoding="utf-8")
        interval = int(re.search(r"--interval (\d+)", vbs).group(1))
        confirm = int(re.search(r"--confirm-sweeps (\d+)", vbs).group(1))
        cfg = json.loads((Path(cli.__file__).parent / "auto_trader_config.json").read_text(encoding="utf-8"))
        longest = max(executor.DEFAULT_MAX_ENTRY_SECONDS, cfg.get("tom", {}).get("max_entry_seconds", 0))
        self.assertGreater(interval * (confirm - 1), longest)

    def test_daily_task_runs_exactly_the_confirm_count_and_waits(self):
        import re
        vbs = (self.REPO / "runtime_data" / "launch-orphan-sweep.vbs").read_text(encoding="utf-8")
        confirm = int(re.search(r"--confirm-sweeps (\d+)", vbs).group(1))
        self.assertEqual(int(re.search(r"--max-sweeps (\d+)", vbs).group(1)), confirm)
        self.assertIn("WScript.Quit sh.Run(", vbs)            # LastTaskResult = the CLI exit code
        self.assertRegex(vbs, r", 0, True\)")


class MaxSweepsTest(unittest.TestCase):
    setUp, halt_lines = LoopTest.setUp, LoopTest.halt_lines
    ORPHAN, FLAT = LoopTest.ORPHAN, LoopTest.FLAT

    def bounded(self, script, max_sweeps, confirm=2):
        it = iter(script)
        cur = {"c": next(it)}

        def sleep(_):
            cur["c"] = next(it)
        return cli.main(["--interval", "60", "--confirm-sweeps", str(confirm), "--max-sweeps", str(max_sweeps)],
                        get_client=lambda lab: (cur["c"][lab], "tok"), hb_dir=self.hb, halt_path=self.halt,
                        log_path=self.log, alive=lambda pid: False, config_path=self.cfg, sleep=sleep)

    def test_stops_after_max_sweeps(self):
        rc = self.bounded([self.FLAT] * 3, 3)
        self.assertEqual(rc, 0)
        self.assertEqual(sum(1 for _ in self.log.open(encoding="utf-8")), 3)

    def test_returns_3_when_any_sweep_halted(self):
        rc = self.bounded([self.ORPHAN, self.ORPHAN, self.FLAT], 3)
        self.assertEqual(rc, 3)
        self.assertEqual(len(self.halt_lines()), 1)

    def test_orphan_only_in_last_sweeps_below_confirm_no_halt(self):
        rc = self.bounded([self.FLAT, self.FLAT, self.ORPHAN], 3)
        self.assertEqual(rc, 0)
        self.assertEqual(self.halt_lines(), [])

if __name__ == "__main__":
    unittest.main()
