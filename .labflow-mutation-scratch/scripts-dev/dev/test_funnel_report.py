"""Tests for funnel_report.py. Expected numbers are counted by hand from the fixtures below."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funnel_report as fr  # noqa: E402

D1_MS = 1790553600000  # 2026-09-28T00:00:00Z
SRC = "layer:rsi:rsi_events:15m"


def alert(t_close):
    return {"layer": "rsi", "sub": "rsi_events", "tf": "15m", "event": "cross", "t_close": t_close}


TRADES = [
    {"ts": "2026-09-28T01:00:00Z", "event": "signal_rejected", "source": SRC},
    {"ts": "2026-09-28T02:00:00Z", "event": "skipped_busy", "source": SRC},
    {"ts": "2026-09-28T03:00:00Z", "event": "skipped_auto_pause", "source": SRC},
    {"ts": "2026-09-28T04:00:00Z", "event": "trade_attempt", "source": SRC, "outcome": "entered"},
    {"ts": "2026-09-28T05:00:00Z", "event": "trade_attempt", "source": SRC, "outcome": "no_fill"},
    {"ts": "2026-09-28T06:00:00Z", "event": "trade_attempt", "source": SRC, "outcome": "entry_failed"},
    {"ts": "2026-09-29T01:00:00Z", "event": "trade_attempt", "source": "tom", "outcome": "entered"},
    {"ts": "2026-09-29T02:00:00Z", "event": "start"},
]
LEDGER = [
    {"plan_id": "A", "source": SRC, "alert_ts": "2026-09-28T04:00:00Z", "exits": [{}], "net_pnl_usd": 1.5},
    {"plan_id": "B", "source": SRC, "alert_ts": "2026-09-28T04:30:00Z", "exits": [{}], "net_pnl_usd": -0.5},
    {"plan_id": "B", "source": SRC, "alert_ts": "2026-09-28T04:30:00Z", "exits": [{}], "net_pnl_usd": -1.0},  # dup, last wins
    {"plan_id": "C", "source": "tom", "alert_ts": "2026-09-29T01:00:00Z", "exits": [], "net_pnl_usd": None},  # open: not closed
    {"plan_id": "D", "source": None, "alert_ts": "2026-09-29T01:00:00Z", "exits": [{}], "net_pnl_usd": None},
]
ALERTS = [alert(D1_MS + 1000), alert(D1_MS + 2000), alert(D1_MS + 86400000 + 1000), {"layer": "x"}]


class FunnelTests(unittest.TestCase):
    def test_counts_per_day_and_source(self):
        t = fr.build(TRADES, LEDGER, ALERTS)
        v = t[("2026-09-28", SRC)]
        self.assertEqual((v["alerts"], v["rejected"], v["skipped"]), (2, 1, 2))
        self.assertEqual((v["attempts"], v["filled"], v["nofill"]), (3, 1, 2))
        self.assertEqual((v["closed"], v["wins"]), (2, 1))
        self.assertAlmostEqual(v["net"], 1.5 - 1.0)
        self.assertEqual(t[("2026-09-29", SRC)]["alerts"], 1)

    def test_open_trade_not_closed_and_unknown_source(self):
        t = fr.build(TRADES, LEDGER, ALERTS)
        self.assertEqual(t[("2026-09-29", "tom")]["closed"], 0)
        self.assertEqual(t[("2026-09-29", "tom")]["filled"], 1)
        self.assertEqual(t[("2026-09-29", "unknown")]["closed"], 1)
        self.assertEqual(t[("2026-09-29", "unknown")]["net"], 0)

    def test_alert_without_t_close_ignored(self):
        self.assertEqual(sum(v["alerts"] for v in fr.build([], [], [{"layer": "x"}]).values()), 0)

    def test_cli_read_only_and_tolerates_bad_lines(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "execution").mkdir()
            (root / "runtime" / "alerts").mkdir(parents=True)
            (root / "execution" / "auto_trades.jsonl").write_text(
                "\n".join(json.dumps(r) for r in TRADES) + "\nnot json\n", encoding="utf-8", newline="\n")
            (root / "execution" / "trade_ledger.jsonl").write_text(
                "\n".join(json.dumps(r) for r in LEDGER) + "\n", encoding="utf-8", newline="\n")
            (root / "runtime" / "alerts" / "15m.jsonl").write_text(
                "\n".join(json.dumps(r) for r in ALERTS) + "\n", encoding="utf-8", newline="\n")
            before = sorted((p.name, p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file())
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = fr.main(["--root", str(root), "--day", "2026-09-28"])
            after = sorted((p.name, p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file())
            self.assertEqual(rc, 0)
            self.assertEqual(before, after)
            out = buf.getvalue()
            self.assertIn("| 2026-09-28 | %s | 2 | 1 | 2 | 3 | 1 | 2 | 2 | 1 | 0.5000 |" % SRC, out)
            self.assertNotIn("2026-09-29", out)
            self.assertIn("unparseable lines: 1", out)

    def test_missing_files_empty_table(self):
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(fr.main(["--root", td]), 0)
            self.assertIn("| TOTAL |", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
