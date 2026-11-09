"""Offline tests: Krown S8 4h forward test wiring in auto_trader (card krown-s8-4h-testnet-build; FORWARD_PREREG.md s1, s4).
No exchange, no subprocess, no real secrets, no order. Run: python -m pytest MyTradingSys/execution/test_auto_trader_krown_s8.py

Rule under test: alert layer:krown:s8_break:4h -> stop = the event's own stop (percent of entry, 4 dp), target = targets_r x that,
time exit 100 bars of 4h = 24,000 min, size 100 USD, own account krown_s8 (a missing secret rejects, never the main slot),
grandfathered by its own pre_pipeline_sources prefix (reason R7, review_by 2026-12-09). Live-path rules: restart state, non-trade balance moves, API errors, fail closed.
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402

SHIPPED = Path(__file__).resolve().parent / "auto_trader_config.json"
SRC = "layer:krown:s8_break:4h"
T_OPEN = int(datetime(2026, 11, 9, 8, 0, tzinfo=timezone.utc).timestamp() * 1000)     # bar 08:00-12:00
NOW = datetime(2026, 11, 9, 12, 1, tzinfo=timezone.utc)                                # one minute after the close


def alert(side="long", entry=100000.0, stop=95000.0, t=T_OPEN):
    return {"layer": "krown", "sub": "s8_break", "tf": "4h", "event": "S8", "side": side, "entry_price": entry,
            "stop": stop, "bbwp": 61.0, "t_close": t, "params_id": "krown_s8_4h_r7_2026-11-09"}


def arg(sig, k):
    return sig["plan_args"][sig["plan_args"].index(k) + 1]


class Proc:
    def poll(self):
        return None


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        for p in (mock.patch.object(at, "SECRETS_DIR", self.dir), mock.patch.object(at, "LOG_PATH", self.dir / "log.jsonl"),
                  mock.patch.object(at, "_warned_missing", set()), mock.patch.object(at, "tom_signal", lambda *a, **k: None),
                  mock.patch.object(at, "AUTO_PAUSE", self.dir / "NOPAUSE"), mock.patch.object(at, "brakes", lambda: [])):
            p.start()
            self.addCleanup(p.stop)
        self.cfg = at.load_config(SHIPPED)

    def events(self):
        p = self.dir / "log.jsonl"
        return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []

    def give_secret(self):
        (self.dir / "testnet_krown_s8.secret.json").write_text("{}", encoding="utf-8")


class ExitTest(Base):
    def test_long_event_stop_target_2r_hold_24000_size(self):
        s = at.layer_signal(alert(), self.cfg, NOW)
        self.assertNotIn("reject", s, s.get("reject"))
        self.assertEqual(s["source"], SRC)
        self.assertEqual(s["side"], "long")
        self.assertEqual(float(arg(s, "--stop")), 5.0)                  # |100000-95000|/100000
        self.assertEqual(float(arg(s, "--targets")), 10.0)              # 2 x 5
        self.assertEqual(float(arg(s, "--max-hold-minutes")), 24000.0)  # 100 x 4h
        self.assertEqual(arg(s, "--size"), "100")
        self.assertEqual(arg(s, "--max-loss"), "25")
        self.assertTrue(s["log"]["bracket_source"].startswith("TESTED:"))

    def test_short_event_and_four_decimal_rounding(self):
        s = at.layer_signal(alert("short", 64000.0, 66151.7), self.cfg, NOW)   # 3.3620 % -> round 4 dp
        self.assertNotIn("reject", s, s.get("reject"))
        self.assertAlmostEqual(float(arg(s, "--stop")), 3.362, places=4)
        self.assertAlmostEqual(float(arg(s, "--targets")), 6.724, places=4)

    def test_wrong_side_or_missing_event_stop_rejects(self):
        for a in (alert(stop=101000.0), alert("short", stop=99000.0), {**alert(), "stop": None}, {**alert(), "entry_price": None},
                  {**alert(), "stop": float("nan")}):
            self.assertIn("bad layers.exits", at.layer_signal(a, self.cfg, NOW).get("reject", ""), a)

    def test_malformed_targets_r_rejects_fail_closed(self):
        good = self.cfg["layers"]["exits"][SRC]
        for bad in ({"targets_r": 0}, {"targets_r": -2}, {"targets_r": "2"}, {"targets_r": True}, {"targets_r": float("nan")},
                    {"targets_r": float("inf")}, {"targets_r": None}, {"targets": "2"}, {"stop": "event", "targets": "2"}):
            c = json.loads(json.dumps(self.cfg))
            e = {**good, **bad}
            if "targets" in bad:
                e = {k: v for k, v in e.items()}                     # targets AND targets_r present
            c["layers"]["exits"][SRC] = e
            self.assertIn("bad layers.exits", at.layer_signal(alert(), c, NOW).get("reject", ""), bad)
        c = json.loads(json.dumps(self.cfg))                          # targets_r with a fixed stop_pct is meaningless
        c["layers"]["exits"][SRC] = {"stop_pct": 2.0, "targets_r": 2, "max_hold_bars": 100, "source": good["source"]}
        self.assertIn("bad layers.exits", at.layer_signal(alert(), c, NOW).get("reject", ""))

    def test_stale_alert_rejected(self):
        later = datetime(2026, 11, 9, 21, 0, tzinfo=timezone.utc)    # 9 h after the bar closed > max_age_bars 2.0 x 4 h
        self.assertIn("stale", at.layer_signal(alert(), self.cfg, later).get("reject", ""))


class PromotionTest(Base):
    """promoted_setups.json needs a screen-PASS manifest (promote.py verify) that a kill-test forward run cannot have, so the R7
    source is grandfathered on its own prefix with its own reason; every other layer still defaults to deny."""

    def test_shipped_config_lets_the_krown_source_trade(self):
        self.assertIsNone(at.promotion_reject(SRC, self.cfg))
        self.assertTrue(self.cfg["pre_pipeline_sources"]["layer:krown:"]["reason"].startswith("R7 forward test"))

    def test_default_deny_without_the_grandfather_entry(self):
        c = json.loads(json.dumps(self.cfg))
        del c["pre_pipeline_sources"]["layer:krown:"]
        self.assertIn("unregistered", at.layer_signal(alert(), c, NOW).get("reject", ""))

    def test_unrelated_layers_stay_denied_and_registry_stays_empty(self):
        self.assertIn("unregistered", at.promotion_reject("layer:ichimoku:cloud:4h", self.cfg) or "")
        self.assertEqual(json.loads((Path(at.PROMOTED_SETUPS)).read_text(encoding="utf-8"))["entries"], [])


class AccountTest(Base):
    def test_routed_to_own_account_when_secret_exists(self):
        self.give_secret()
        self.assertEqual(at.account_for(SRC, self.cfg), "krown_s8")
        self.assertIsNone(at.account_secret_missing(SRC, self.cfg))

    def test_missing_secret_rejects_and_never_reaches_the_main_slot(self):
        self.assertEqual(at.account_secret_missing(SRC, self.cfg), "krown_s8")
        placed = []
        with mock.patch.object(at, "layer_signal", lambda a, c, n: {"source": SRC, "key": "k", "side": "long", "plan_args": ["--size", "100"]}), \
                mock.patch.object(at, "read_new_layer_alerts", lambda st: [alert()]), \
                mock.patch.object(at, "place", lambda *a, **k: placed.append(a)):
            at.cycle({}, self.cfg, False, {}, now=NOW, extra={})
        self.assertEqual(placed, [])
        self.assertEqual([e["reason"] for e in self.events() if e["event"] == "signal_rejected"], ["account_secret_missing"])

    def test_other_layers_keep_their_accounts(self):
        self.assertTrue(at.account_secret_missing("layer:fabio:cvd_absorption:15m", self.cfg) == "fabio"
                        or "layer:fabio:" in self.cfg["accounts"])
        self.assertEqual(list(self.cfg["accounts"]).index("layer:krown:") < list(self.cfg["accounts"]).index("layer:"), True)


class LivePathTest(Base):
    """Restart / reset state, non-trade balance moves, API errors (CLAUDE.md live-path rules)."""

    def run_cycle(self, active=None, extra=None, place=None):
        with mock.patch.object(at, "read_new_layer_alerts", lambda st: [alert(t=T_OPEN + 4 * 3600 * 1000)]), \
                mock.patch.object(at, "deribit_mark", lambda instrument="BTC-PERPETUAL": 100000.0), \
                mock.patch.object(at, "available_funds_btc", lambda account=None: 5.0), \
                mock.patch.object(at, "place", place or (lambda sig, dry, acct=None: {"outcome": "entered", "plan_id": "pK", "proc": Proc()})):
            extra = {} if extra is None else extra
            return at.cycle({}, self.cfg, False, active or {}, now=datetime(2026, 11, 9, 16, 1, tzinfo=timezone.utc), extra=extra), extra

    def test_restart_with_open_position_adopts_it_and_skips_busy_never_a_second_entry(self):
        self.give_secret()
        at.log({"event": "trade_attempt", "outcome": "entered", "plan_id": "pOPEN", "source": SRC, "account": "krown_s8"})
        active, extra = at.recover_slots(procs=[])                    # no manager process alive: dead slot, exchange check next
        self.assertEqual(extra["krown_s8"]["plan_id"], "pOPEN")
        self.assertEqual(extra["krown_s8"]["source"], SRC)
        self.assertEqual(active, {})
        placed = []
        with mock.patch.object(at, "exchange_flat", lambda acct=None: False), \
                mock.patch.object(at, "spawn_manager", lambda pid, acct=None: Proc()):
            _, extra = self.run_cycle(extra=extra, place=lambda *a, **k: placed.append(a))
        self.assertEqual(placed, [])                                  # position still open: the new event is busy-skipped
        ev = [e["event"] for e in self.events()]
        self.assertIn("manager_lost", ev)                             # exchange open + manager dead: respawned, not abandoned
        self.assertIn("skipped_busy", ev)

    def test_restart_after_flat_close_frees_the_slot_for_the_next_event(self):
        self.give_secret()
        at.log({"event": "trade_attempt", "outcome": "entered", "plan_id": "pOLD", "source": SRC, "account": "krown_s8"})
        _, extra = at.recover_slots(procs=[])
        placed = []
        with mock.patch.object(at, "exchange_flat", lambda acct=None: True), mock.patch.object(at, "record_ledger", lambda *a: None):
            _, extra = self.run_cycle(extra=extra, place=lambda sig, dry, acct=None: placed.append(acct) or {"outcome": "no_fill", "plan_id": "pN"})
        self.assertEqual(placed, ["krown_s8"])

    def test_non_trade_balance_moves_never_change_the_size(self):
        base = at.layer_signal(alert(), self.cfg, NOW)["plan_args"]
        for funds in (50.0, 0.0001, 1e-9, None):                      # deposit, withdrawal, dust, unreadable
            with mock.patch.object(at, "available_funds_btc", lambda account=None, f=funds: f):
                self.assertEqual(at.layer_signal(alert(), self.cfg, NOW)["plan_args"], base)
        sig = {"margin_btc": 0.002}
        with mock.patch.object(at, "available_funds_btc", lambda account=None: 0.0001):
            self.assertFalse(at.margin_ok(sig, "krown_s8")[0])        # a withdrawal refuses the entry, it never shrinks it
        with mock.patch.object(at, "available_funds_btc", lambda account=None: None):
            self.assertEqual(at.margin_ok(sig, "krown_s8"), (False, "balance_unreadable"))

    def test_api_error_on_entry_leaves_no_manager_and_no_busy_slot(self):
        self.give_secret()

        def fake_run(cmd, timeout=900, account=None):
            return (0, "SAVED plan-x") if "new_plan.py" in cmd[1] else (1, "HTTP 500 from exchange")
        spawned = []
        with mock.patch.object(at, "run", fake_run), mock.patch.object(at, "spawn_manager", lambda *a, **k: spawned.append(a)), \
                mock.patch.object(at, "available_funds_btc", lambda account=None: 5.0):
            out = at.place({"plan_args": ["--size", "100"], "margin_btc": 0.001}, False, "krown_s8")
            self.assertEqual(out["outcome"], "entry_failed")
            self.assertEqual(spawned, [])
            _, extra = self.run_cycle(place=lambda sig, dry, acct=None: out)
        self.assertEqual(extra, {})                                   # no proc = no slot held, next event may try again
        self.assertEqual([e["outcome"] for e in self.events() if e["event"] == "trade_attempt"], ["entry_failed"])

    def test_unreadable_balance_refuses_before_any_plan_is_saved(self):
        ran = []
        with mock.patch.object(at, "run", lambda *a, **k: ran.append(a) or (0, "")), \
                mock.patch.object(at, "available_funds_btc", lambda account=None: None):
            out = at.place({"plan_args": ["--size", "100"], "margin_btc": 0.001}, False, "krown_s8")
        self.assertEqual(out["outcome"], "margin_short")
        self.assertEqual(ran, [])


if __name__ == "__main__":
    unittest.main()
