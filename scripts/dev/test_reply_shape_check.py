"""test_reply_shape_check.py: the det-only reply-shape guardrail flags an overlong, un-bold reply and lets a shaped one through.

No model call. Fails on pre-change code because scripts/dev/reply_shape_check.py does not exist there yet.
"""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reply_shape_check as rsc  # noqa: E402


# Deliberately overlong + no bold result line: violates BOTH det checks of h-reply-shape (max_lines:8, bold_first_line).
OVERLONG_REPLY = "\n".join(
    [
        "So I ran the script and it worked out, here is a bit of background on why I did it that way",
        "First I looked at the data, then I checked the docs, and then I made a few small edits along the way",
        "I also wanted to mention that there were a couple of caveats worth flagging before you read the numbers",
        "The whole thing took a while because I had to reconcile two files that had drifted out of sync over time",
        "In the end I settled on the approach above, though I acknowledge there are other ways this could have been done",
        "You might also want to check the related setting before you rely on the result shown here below",
        "One last note: the timestamp in the log line is in UTC, not local, so it will look a little off at first glance",
        "Please let me know if anything here is unclear and I am happy to walk through each step in more detail",
        "Thanks for asking, and I hope this answers the question of what happened and what to do next",
        "If anything is still missing I can add a small follow-up on that in a later session when the gate is green",
    ]
)

# Shaped right: bold result line first, table, short YOU DO; well under 8 content lines.
GOOD_REPLY = (
    "**Done: reply-shape guardrail wired, 3 checks pass.**\n"
    "| What | Status | Proof |\n"
    "| reply_shape_check.py | Done | exits 1 on a bad reply |\n"
    "\nYOU DO: nothing waiting for you."
)


class ReplyShape(unittest.TestCase):
    def test_det_checks_come_from_the_h_reply_shape_scenario(self):
        # The guardrail must actually be reading the shipped scenario, not a hard-coded copy.
        self.assertEqual(rsc.det_checks(), ["max_lines:8", "bold_first_line"])

    def test_overlong_unbold_reply_is_flagged(self):
        failed = rsc.check(OVERLONG_REPLY)
        self.assertIn("max_lines:8", failed, f"overlong reply not caught: {failed}")
        self.assertIn("bold_first_line", failed, f"missing bold first line not caught: {failed}")
        self.assertGreaterEqual(len(failed), 2)

    def test_shaped_reply_passes(self):
        self.assertEqual(rsc.check(GOOD_REPLY), [])

    def test_main_exit_code_is_nonzero_on_violation(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write(OVERLONG_REPLY)
            name = fh.name
        try:
            self.assertEqual(rsc.main([name]), 1, "a violating reply must exit non-zero")
        finally:
            Path(name).unlink(missing_ok=True)

    def test_main_exit_code_is_zero_on_ok(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write(GOOD_REPLY)
            name = fh.name
        try:
            self.assertEqual(rsc.main([name]), 0, "a shaped reply must exit zero")
        finally:
            Path(name).unlink(missing_ok=True)

    def test_no_args_with_open_stdin_exits_promptly(self):
        script = Path(rsc.__file__).resolve()
        proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            try:
                rc = proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                self.fail("CLI waited for EOF on stdin when no input source was named")
            _stdout, stderr = proc.communicate(timeout=1)
            self.assertEqual(rc, 2, stderr)
            self.assertIn("REPLY_FILE or - is required", stderr)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()

    def test_explicit_dash_reads_piped_input(self):
        script = Path(rsc.__file__).resolve()
        proc = subprocess.run(
            [sys.executable, str(script), "-"],
            input=GOOD_REPLY,
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("reply-shape: ok", proc.stdout)

    def test_explicit_dash_rejects_dummy_reply(self):
        script = Path(rsc.__file__).resolve()
        proc = subprocess.run(
            [sys.executable, str(script), "-"],
            input="dummy reply",
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("VIOLATION bold_first_line", proc.stdout)


if __name__ == "__main__":
    unittest.main()
