"""test_reply_shape_check.py: the det-only reply-shape guardrail flags an overlong, un-bold reply and lets a shaped one through.

No model call. Fails on pre-change code because scripts/dev/reply_shape_check.py does not exist there yet.
"""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reply_shape_check as rsc  # noqa: E402

START_TIMEOUT = 60  # generous: only a true hang should trip it, not a loaded gate
SCRIPT = Path(rsc.__file__).resolve()


def run_cli(args, input_text=None, stdin=None, timeout=START_TIMEOUT, start_delay=0.0):
    """Run the CLI with stdin passed explicitly (never inherited from a backgrounded gate)."""
    code = f"import time,runpy,sys; time.sleep({start_delay}); sys.argv=[{str(SCRIPT)!r}]+sys.argv[1:]; runpy.run_path({str(SCRIPT)!r}, run_name='__main__')"
    if input_text is not None:
        stdin = subprocess.PIPE
    elif stdin is None:
        stdin = subprocess.DEVNULL
    proc = subprocess.Popen([sys.executable, "-c", code, *args], stdin=stdin,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        if input_text is None:
            proc.wait(timeout=timeout)  # stdin stays open (PIPE) or is /dev/null: a CLI that reads it would hang here
            out, err = proc.stdout.read(), proc.stderr.read()
        else:
            out, err = proc.communicate(input_text, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise AssertionError("CLI hung (waited on stdin or never started)")
    return proc.returncode, out, err


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
        rc, _out, err = run_cli([], stdin=subprocess.PIPE, timeout=START_TIMEOUT)
        self.assertEqual(rc, 2, err)
        self.assertIn("REPLY_FILE or - is required", err)

    def test_no_args_with_devnull_stdin_exits_2(self):
        rc, _out, err = run_cli([], stdin=subprocess.DEVNULL, timeout=START_TIMEOUT)
        self.assertEqual(rc, 2, err)

    def test_explicit_dash_reads_piped_input(self):
        rc, out, err = run_cli(["-"], input_text=GOOD_REPLY, timeout=START_TIMEOUT)
        self.assertEqual(rc, 0, err)
        self.assertIn("reply-shape: ok", out)

    def test_explicit_dash_rejects_dummy_reply(self):
        rc, out, _err = run_cli(["-"], input_text="dummy reply", timeout=START_TIMEOUT)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("VIOLATION bold_first_line", out)

    def test_slow_interpreter_start_does_not_fail_the_gate(self):
        # A loaded ship gate can delay python start-up past a tight timeout; the harness must tolerate it
        # (pre-change tests used a fixed 2 s wait and failed here).
        rc, out, err = run_cli(["-"], input_text=GOOD_REPLY, timeout=START_TIMEOUT, start_delay=2.5)
        self.assertEqual(rc, 0, err)
        self.assertIn("reply-shape: ok", out)


if __name__ == "__main__":
    unittest.main()
