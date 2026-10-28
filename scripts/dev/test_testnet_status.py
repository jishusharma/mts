"""Tests for testnet_status.py against synthetic fixtures (no live files, no network).

Fixture window: now = 2026-09-30T12:00:00Z, hours = 24 -> window starts 2026-09-29T12:00:00Z.
Expected numbers below are hand-derived from the fixture rows, not from the script.
"""
import json
import os
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

NOW = "2026-09-30T12:00:00Z"
ORDER_ID = "BTC-18273645123"
ORDER_ID2 = "ETH-99887766554"
KEY = "sk_live_4f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c"
PLAN = "L-mkt-0930-0001"
CONFIG = {"accounts": {"layer:turn_of_candle:": "jishu_1", "layer:fabio:": "jishu_3",
                       "layer:rsi:rsi_events:15m": "jishu_2", "layer:rsi:": "jishu_3", "layer:": "jishu_4"}}
TOC = "layer:turn_of_candle:toc_m14:1m"
FAB = "layer:fabio:cvd_absorption:1h"
RSI15 = "layer:rsi:rsi_events:15m"
RSI5 = "layer:rsi:rsi_events:5m"


def jl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")


def build_fixture(d):
    d = pathlib.Path(d)
    (d / "auto_trader_config.json").write_text(json.dumps(CONFIG), encoding="utf-8")
    log = [
        # before the window: a closed toc trade (excluded from counts) and an unclosed rsi 5m trade (still "open")
        {"ts": "2026-09-28T10:00:00Z", "event": "trade_attempt", "source": TOC, "outcome": "entered",
         "plan_id": "P0", "account": "jishu_1"},
        {"ts": "2026-09-28T10:10:00Z", "event": "trade_closed", "plan_id": "P0", "source": TOC},
        {"ts": "2026-09-28T11:00:00Z", "event": "trade_attempt", "source": RSI5, "outcome": "entered",
         "plan_id": "P4", "account": "jishu_3"},
        # in window
        {"ts": "2026-09-29T13:00:00Z", "event": "trade_attempt", "source": TOC, "outcome": "entered",
         "plan_id": PLAN, "account": "jishu_1", "output": f"order_id {ORDER_ID} api_key {KEY}"},
        {"ts": "2026-09-29T13:10:00Z", "event": "trade_closed", "plan_id": PLAN, "source": TOC},
        {"ts": "2026-09-29T14:00:00Z", "event": "trade_attempt", "source": TOC, "outcome": "entered",
         "plan_id": "P2", "account": "jishu_1"},
        {"ts": "2026-09-29T14:10:00Z", "event": "trade_closed", "plan_id": "P2", "source": TOC},
        {"ts": "2026-09-29T15:00:00Z", "event": "trade_attempt", "source": TOC, "outcome": "plan_refused",
         "account": "jishu_1", "output": "refused"},
        {"ts": "2026-09-29T16:00:00Z", "event": "signal_rejected", "source": TOC,
         "reason": "unmapped turn_of_candle:toc_m14 (add a layer_rules entry)"},
        {"ts": "2026-09-29T17:00:00Z", "event": "skipped_busy", "source": TOC, "busy_with": "P2",
         "account": "jishu_1"},
        {"ts": "2026-09-29T18:00:00Z", "event": "skipped_halt", "source": TOC, "brakes": ["HALT"]},
        {"ts": "2026-09-29T19:00:00Z", "event": "signal_rejected", "source": "tom", "reason": "verdict WAIT"},
        {"ts": "2026-09-29T20:00:00Z", "event": "skipped_auto_pause", "source": "tom"},
        {"ts": "2026-09-29T19:00:00Z", "event": "skipped_auto_pause", "source": FAB},
        {"ts": "2026-09-29T15:01:00Z", "event": "trade_attempt", "source": RSI15, "outcome": "entered",
         "plan_id": "P3", "account": "jishu_2"},
        {"ts": "2026-09-29T15:02:00Z", "event": "start", "brakes": []},
        "this line is not json {",
        {"ts": "2026-09-29T15:03:00Z", "event": "transfer", "amount_btc": 2.5, "account": "jishu_1"},
    ]
    jl(d / "auto_trades.jsonl", log)
    led = [
        {"ts": "2026-09-28T10:11:00Z", "source": TOC, "account": "jishu_1", "plan_id": "P0",
         "net_pnl_usd": -5.0},                                       # before the window
        {"ts": "2026-09-29T13:11:00Z", "source": TOC, "account": "jishu_1", "plan_id": PLAN,
         "net_pnl_usd": -0.03, "order_id": ORDER_ID2, "exit_reason": "time_exit"},
        {"ts": "2026-09-29T14:11:00Z", "source": TOC, "account": "jishu_1", "plan_id": "P2",
         "net_pnl_usd": 0.05},
        {"ts": "2026-09-29T16:00:00Z", "source": RSI15, "account": "jishu_2", "plan_id": "P3",
         "net_pnl_usd": None, "unresolved": "exchange read failed"},
        # transfer-like, not a trade: no plan_id (one even carries a source and a net figure)
        {"ts": "2026-09-29T15:30:00Z", "type": "transfer", "account": "jishu_1", "amount_btc": 1.5},
        {"ts": "2026-09-29T15:31:00Z", "type": "transfer", "source": TOC, "account": "jishu_1",
         "net_pnl_usd": 100.0},
    ]
    jl(d / "trade_ledger.jsonl", led)
    (d / "OPERATOR_ALERTS.log").write_text(
        "2026-09-20T01:00:00Z auto_trader old line outside window\n"
        f"2026-09-30T08:00:00Z auto_trader manager exhausted order {ORDER_ID} key={KEY}\n", encoding="utf-8")
    hh = d / "halt_history"
    hh.mkdir()
    for name, iso in (("HALT_20260930_080000.txt", "2026-09-30T08:00:00Z"),
                      ("HALT_DAILY_LOSS_2026-09-20_old", "2026-09-20T08:00:00Z")):
        p = hh / name
        p.write_text(f"secret {KEY}", encoding="utf-8")
        t = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
        os.utime(p, (t, t))
    (d / "AUTO_PAUSE").write_text("", encoding="utf-8")


def run(exec_dir, out_dir, extra=()):
    import testnet_status as ts
    rc = ts.main(["--exec-dir", str(exec_dir), "--out-dir", str(out_dir), "--now", NOW, *extra])
    return rc


def table(text, title_prefix="## Per family"):
    """Parse the markdown table under the heading -> {(family, account): {header: cell}}."""
    lines = text.split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith(title_prefix))
    rows = [l for l in lines[i + 1:] if l.startswith("|")]
    # stop at first non-table line after the table started
    out, hdr = {}, None
    for l in lines[i + 1:]:
        if not l.startswith("|"):
            if hdr:
                break
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if hdr is None:
            hdr = cells
        elif not set(l) <= set("|-: "):
            out[(cells[0], cells[1])] = dict(zip(hdr, cells))
    return out


class T(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._t.name)
        self.ex = self.root / "execution"
        self.ex.mkdir()
        self.out = self.root / "out"

    def tearDown(self):
        self._t.cleanup()

    def report(self):
        self.assertEqual(run(self.ex, self.out), 0)
        files = list(self.out.glob("TESTNET_STATUS_*.md"))
        self.assertEqual([f.name for f in files], ["TESTNET_STATUS_2026-09-30.md"])
        return files[0].read_bytes().decode("utf-8")

    def test_counts_per_family_account(self):
        build_fixture(self.ex)
        rows = table(self.report())
        toc = rows[("turn_of_candle", "jishu_1")]
        self.assertEqual((toc["Alerts"], toc["Entered"], toc["Closed"], toc["Wins"]), ("6", "2", "2", "1"))
        self.assertEqual((toc["Busy"], toc["AutoPause"], toc["Unmapped"], toc["Rejected"], toc["Halt"]),
                         ("1", "0", "1", "0", "1"))
        self.assertEqual(toc["Failed"], "1")
        self.assertEqual(toc["Net USD"], "+0.0200")       # -0.03 + 0.05; P0 (-5.0) is outside the window
        tom = rows[("tom", "main")]
        self.assertEqual((tom["Alerts"], tom["Entered"], tom["Rejected"], tom["AutoPause"]), ("2", "0", "1", "1"))
        fab = rows[("fabio", "jishu_3")]
        self.assertEqual((fab["Alerts"], fab["Entered"], fab["AutoPause"]), ("1", "0", "1"))
        rsi = rows[("rsi", "jishu_2")]
        self.assertEqual((rsi["Alerts"], rsi["Entered"], rsi["Closed"], rsi["Unresolved"]), ("1", "1", "0", "1"))
        self.assertEqual(rsi["Net USD"], "+0.0000")

    def test_transfer_like_rows_not_trades(self):
        build_fixture(self.ex)
        text = self.report()
        toc = table(text)[("turn_of_candle", "jishu_1")]
        self.assertEqual(toc["Closed"], "2")              # the 100.0 transfer row did not become a closed trade
        self.assertNotIn("100.0", text)
        self.assertNotIn("transfer", [k[0] for k in table(text)])

    def test_zero_trade_flags(self):
        build_fixture(self.ex)
        text = self.report()
        flags = [l for l in text.split("\n") if l.startswith("- FLAG 0 trades in 24 h")]
        got = sorted(l.split(": ", 1)[1] for l in flags)
        self.assertEqual(got, ["fabio / jishu_3", "rsi / jishu_3", "tom / main"])

    def test_open_positions_last_logged(self):
        build_fixture(self.ex)
        text = self.report()
        sec = text.split("## Open positions")[1].split("\n## ")[0]
        self.assertIn("last logged", sec)
        self.assertIn("not live", sec)
        rows = {l.split("|")[1].strip(): l.split("|")[2].strip() for l in sec.split("\n")
                if l.startswith("| jishu") or l.startswith("| main")}
        self.assertEqual((rows["jishu_1"], rows["jishu_2"], rows["jishu_3"]), ("0", "1", "1"))

    def test_halt_and_alert_sections(self):
        build_fixture(self.ex)
        text = self.report()
        self.assertIn("HALT_20260930_080000.txt", text)               # in window
        self.assertNotIn("HALT_DAILY_LOSS_2026-09-20_old", text.split("## HALT")[1].split("\n## ")[0]
                         .split("older")[0])                          # outside window is only counted
        self.assertIn("AUTO_PAUSE", text)                             # present at run time
        self.assertIn("manager exhausted", text)                      # in-window operator alert, scrubbed
        self.assertNotIn("old line outside window", text)
        self.assertIn("skipped_halt decisions in window: 1", text)

    def test_missing_files(self):
        text = self.report()                                          # empty exec dir, no config
        for name in ("auto_trades.jsonl", "trade_ledger.jsonl", "OPERATOR_ALERTS.log", "halt_history",
                     "auto_trader_config.json"):
            self.assertRegex(text, name + r"[^\n]*not found")
        self.assertIn("Window", text)

    def test_missing_dir_entirely(self):
        rc = run(self.root / "nope", self.out)
        self.assertEqual(rc, 0)
        self.assertEqual(len(list(self.out.glob("TESTNET_STATUS_*.md"))), 1)

    def test_sanitized(self):
        build_fixture(self.ex)
        text = self.report()
        for bad in (ORDER_ID, ORDER_ID2, "18273645123", KEY, "sk_live", PLAN, "4f9a8b7c6d5e", "client_id",
                    "api_key"):
            self.assertNotIn(bad, text)

    def test_scrub_function(self):
        import testnet_status as ts
        s = ts.scrub(f"order {ORDER_ID} key={KEY} client_secret: abcdef tail OK")
        for bad in (ORDER_ID, KEY, "abcdef"):
            self.assertNotIn(bad, s)
        self.assertIn("tail OK", s)

    def test_utf8_lf(self):
        build_fixture(self.ex)
        raw = (lambda: (self.report(), list(self.out.glob("*.md"))[0].read_bytes())[1])()
        self.assertNotIn(b"\r", raw)
        raw.decode("utf-8")
        self.assertTrue(raw.endswith(b"\n"))

    def test_window_override_and_malformed_lines(self):
        build_fixture(self.ex)
        self.assertEqual(run(self.ex, self.out, ["--hours", "1"]), 0)   # 11:00-12:00: nothing in fixture
        text = (self.out / "TESTNET_STATUS_2026-09-30.md").read_text(encoding="utf-8")
        toc = table(text)[("turn_of_candle", "jishu_1")]
        self.assertEqual((toc["Alerts"], toc["Entered"], toc["Closed"]), ("0", "0", "0"))
        self.assertIn("1 h", text)
        self.assertIn("unparseable", text)                              # the broken log line is reported, not fatal


if __name__ == "__main__":
    unittest.main()
