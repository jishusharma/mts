"""asks_gaps: an ask with no card/commit after 24 h and an OPEN item with no live card must be listed (T054 news step, 33 days)."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import operator_questions as oq

NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
INDEX = """# ITEMS INDEX
T054 | OPEN    | T054_us_news.md | US session alerts, news sentiment
T040 | OPEN    | T040_tick.md | tick delta layer
T035 | CLOSED  | T035_cvd.md | defer
"""


def row(hours_ago, text):
    return {"utc": (NOW - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ"), "prompt": text}


def card(state, created_hours_ago, **kw):
    c = {"id": "c", "state": state, "title": "", "goal": "", "note": "", "refs": [],
         "created": (NOW - timedelta(hours=created_hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    c.update(kw)
    return c


def gaps(rows, cards=(), commits=(), ledger=""):
    return oq.asks_gaps(repo=REPO, now=NOW, rows=rows, cards=list(cards), commits=list(commits), ledger_text=ledger, index_text=INDEX)


class AsksGapsTest(unittest.TestCase):
    ASK = "Please build a news panel for the dashboard with hack alerts"

    def test_old_ask_without_card_or_commit_is_listed(self):
        g = gaps([row(48, self.ASK)])
        self.assertEqual(len(g["asks"]), 1)

    def test_recent_ask_is_not_yet_a_gap(self):
        self.assertEqual(gaps([row(5, self.ASK)])["asks"], [])

    def test_card_after_ask_closes_it(self):
        c = card("ready", 40, title="News panel on dashboard", goal="hack alerts feed")
        self.assertEqual(gaps([row(48, self.ASK)], cards=[c])["asks"], [])

    def test_commit_after_ask_closes_it(self):
        com = [(NOW - timedelta(hours=30), "dashboard news panel with hack alerts")]
        self.assertEqual(gaps([row(48, self.ASK)], commits=com)["asks"], [])

    def test_ledger_row_with_stamp_closes_it_but_open_row_does_not(self):
        stamp = (NOW - timedelta(hours=48)).strftime("%m-%d %H:%M")
        self.assertEqual(gaps([row(48, self.ASK)], ledger=f"| A1 | {stamp} | news | DONE | abc123 |")["asks"], [])
        self.assertEqual(len(gaps([row(48, self.ASK)], ledger=f"| A1 | {stamp} | news | OPEN | - |")["asks"]), 1)

    def test_ledger_audited_through_covers_older_asks(self):
        cut = (NOW - timedelta(hours=40)).strftime("%Y-%m-%dT%H:%MZ")
        self.assertEqual(gaps([row(48, self.ASK)], ledger=f"Audited through: {cut} ")["asks"], [])
        self.assertEqual(len(gaps([row(30, self.ASK)], ledger=f"Audited through: {cut} ")["asks"]), 1)

    def test_chat_is_not_an_ask(self):
        self.assertEqual(gaps([row(48, "okay thanks, that looks fine to me now")])["asks"], [])

    def test_open_item_without_live_card_is_listed(self):
        ids = [i["id"] for i in gaps([])["items"]]
        self.assertEqual(ids, ["T054", "T040"])

    def test_live_card_naming_item_closes_it_but_done_card_does_not(self):
        self.assertEqual([i["id"] for i in gaps([], cards=[card("ready", 1, refs=["T054"])])["items"]], ["T040"])
        self.assertEqual([i["id"] for i in gaps([], cards=[card("done", 1, refs=["T054"])])["items"]], ["T054", "T040"])


if __name__ == "__main__":
    unittest.main()
