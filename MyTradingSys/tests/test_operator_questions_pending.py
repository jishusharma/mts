import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add repo root and scripts/dev to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import operator_questions as oq


SAMPLE_OPERATOR_DECISIONS = """# OPERATOR DECISIONS

## q1-one-control-room | asked 2026-10-13 | Process

Which Control Room page holds your questions and Inbox?

Recommended: This page is the one place
Answer: This page is the one place
Operator note (verbatim): (none)
Applied: 2026-10-13: this page (NUC account) is the one place; already treated so since the answer.

```json
{
 "order": 1,
 "stage": "Process",
 "weight": "ROUTINE",
 "refs": "artifact registry",
 "title": "Which Control Room page holds your questions and Inbox?",
 "why": "Explanation...",
 "options": [
  "This page is the one place"
 ],
 "recommended": "This page is the one place"
}
```

## q2-jis-nb-dark | asked 2026-10-13 | Live testnet

JIS-NB looks dark: trading halted, live view 23 hours old. Can you open Claude there?

Recommended: I will open Claude on JIS-NB; find the cause, then clear the halt
Answer: (none yet)
Operator note (verbatim): (none)
Applied: (not yet)

```json
{
 "order": 2,
 "stage": "Live testnet",
 "weight": "CRITICAL",
 "refs": "exec-halt-entry-10031",
 "title": "JIS-NB looks dark: trading halted, live view 23 hours old. Can you open Claude there?",
 "why": "Explanation...",
 "options": [
  "I will open Claude on JIS-NB"
 ],
 "recommended": "I will open Claude on JIS-NB"
}
```

## q3-fabio-video-method | asked 2026-10-14 | Fabio

Fabio's videos: keep reading one 250-second window per session?

Recommended: Pre-screen windows with a script, read only those with a trade
Answer: (none yet)
Operator note (verbatim): (none)
Applied: (not yet)

```json
{
 "order": 3,
 "stage": "Fabio",
 "weight": "IMPORTANT",
 "refs": "fabio",
 "title": "Fabio's videos: keep reading one 250-second window per session?",
 "why": "Explanation...",
 "options": [
  "Pre-screen windows"
 ],
 "recommended": "Pre-screen windows"
}
```
"""


class OperatorQuestionsPendingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.log_file = self.tmp_path / "operator_questions.jsonl"
        self.decisions_file = self.tmp_path / "OPERATOR_DECISIONS.md"
        self.decisions_file.write_text(SAMPLE_OPERATOR_DECISIONS, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_pending_filtering_and_ranking(self):
        """A fixture log with one answered and one open question lists only the open one, ranked, drops automated/pasted."""
        log_rows = [
            # Answered in OPERATOR_DECISIONS (q1)
            {
                "utc": "2026-10-13T10:00:00Z",
                "session_id": "sess-1",
                "tags": ["control-room"],
                "prompt": "Which Control Room page holds your questions and Inbox?"
            },
            # Open question in OPERATOR_DECISIONS (q2 - CRITICAL weight)
            {
                "utc": "2026-10-13T11:00:00Z",
                "session_id": "sess-2",
                "tags": ["halt"],
                "prompt": "JIS-NB looks dark: trading halted, live view 23 hours old. Can you open Claude there?"
            },
            # Open question in OPERATOR_DECISIONS (q3 - IMPORTANT weight)
            {
                "utc": "2026-10-14T09:00:00Z",
                "session_id": "sess-3",
                "tags": ["fabio"],
                "prompt": "Fabio's videos: keep reading one 250-second window per session?"
            },
            # Unmatched open typed question from log (not in OPERATOR_DECISIONS at all -> pending)
            {
                "utc": "2026-10-15T12:00:00Z",
                "session_id": "sess-4",
                "tags": ["question"],
                "prompt": "Should we increase trade allocation for BTC?"
            },
            # Automated / pasted content (should be filtered out)
            {
                "utc": "2026-10-16T12:00:00Z",
                "session_id": "sess-5",
                "tags": [],
                "prompt": "<task-notification> Background task completed"
            },
            {
                "utc": "2026-10-16T13:00:00Z",
                "session_id": "sess-6",
                "tags": [],
                "prompt": "<pasted_content>\nLong report pasted here...\n</pasted_content>"
            },
            {
                "utc": "2026-10-16T14:00:00Z",
                "session_id": "sess-7",
                "tags": [],
                "prompt": "x" * 3500  # Too long (> MAX_TYPED_CHARS)
            }
        ]
        self.log_file.write_text(
            "\n".join(json.dumps(r) for r in log_rows) + "\n",
            encoding="utf-8"
        )

        # Call get_pending (or pending)
        pending = oq.pending_questions(log_path=self.log_file, decisions_path=self.decisions_file)

        # q1 is answered, so it must not be present
        prompts = [p["prompt"] for p in pending]
        self.assertNotIn("Which Control Room page holds your questions and Inbox?", prompts)

        # Automated / pasted rows must not be present
        self.assertNotIn("<task-notification> Background task completed", prompts)
        self.assertNotIn("<pasted_content>\nLong report pasted here...\n</pasted_content>", prompts)

        # Open questions must be present
        self.assertIn("JIS-NB looks dark: trading halted, live view 23 hours old. Can you open Claude there?", prompts)
        self.assertIn("Fabio's videos: keep reading one 250-second window per session?", prompts)
        self.assertIn("Should we increase trade allocation for BTC?", prompts)

        # Ranking: CRITICAL first, then IMPORTANT, then ROUTINE/unranked
        # q2 (CRITICAL) must be ranked before q3 (IMPORTANT)
        idx_q2 = next(i for i, p in enumerate(pending) if "JIS-NB looks dark" in p["prompt"])
        idx_q3 = next(i for i, p in enumerate(pending) if "Fabio's videos" in p["prompt"])
        self.assertLess(idx_q2, idx_q3)

    def test_cli_pending_subcommand(self):
        """CLI operator_questions.py pending runs and produces expected output."""
        log_rows = [
            {
                "utc": "2026-10-13T10:00:00Z",
                "session_id": "sess-1",
                "tags": ["control-room"],
                "prompt": "Which Control Room page holds your questions and Inbox?"
            },
            {
                "utc": "2026-10-13T11:00:00Z",
                "session_id": "sess-2",
                "tags": ["halt"],
                "prompt": "JIS-NB looks dark: trading halted, live view 23 hours old. Can you open Claude there?"
            }
        ]
        self.log_file.write_text(
            "\n".join(json.dumps(r) for r in log_rows) + "\n",
            encoding="utf-8"
        )

        env = os.environ.copy()
        env["OPERATOR_QUESTIONS_FILE"] = str(self.log_file)
        env["OPERATOR_DECISIONS_FILE"] = str(self.decisions_file)

        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "dev" / "operator_questions.py"), "pending"],
            capture_output=True,
            text=True,
            env=env
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("JIS-NB looks dark", r.stdout)
        self.assertNotIn("Which Control Room page", r.stdout)


if __name__ == "__main__":
    unittest.main()
