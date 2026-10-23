"""scripts/dev/boot_probe.py: one BOOT signal per session and per subagent (operator 2026-10-22: "is the initial token load
correct here? ... monitor for each session/sub-session and agent"). First-turn tokens from the transcript head, the first
reply's role banner checked, HIGH above 60k, and turn_meter's PostToolUse hook starts it once, subagents included."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import boot_probe  # noqa: E402
import role_loader  # noqa: E402
import turn_meter  # noqa: E402


NOW = datetime(2026, 10, 22, 23, 0, tzinfo=timezone.utc)


def assistant(mid, content, usage=None, model="claude-sonnet-5-5", at="2026-10-22T22:59:00.000Z"):
    msg = {"id": mid, "model": model, "content": content}
    if usage:
        msg["usage"] = usage
    return json.dumps({"type": "assistant", "timestamp": at, "message": msg})


USAGE = {"input_tokens": 3, "cache_creation_input_tokens": 20000, "cache_read_input_tokens": 32800}


class BootProbeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.env = mock.patch.dict(os.environ, {"MTS_BOOT_PROBE_HOME": str(self.dir / "probe"),
                                                "MTS_ROLES_HOME": str(self.dir / "roles"),
                                                "MTS_TURN_METER_HOME": str(self.dir / "tm")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def transcript(self, lines):
        p = self.dir / "t.jsonl"
        p.write_text("\n".join([json.dumps({"type": "user", "message": {"content": "I need mts doctor role"}})] + lines) + "\n",
                     encoding="utf-8")
        return p

    def test_first_turn_sums_the_first_message_and_stops_at_its_tool_call(self):
        p = self.transcript([
            assistant("m1", [{"type": "text", "text": "ROLE LOADED: x"}], USAGE),
            assistant("m1", [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}], USAGE),
            assistant("m1", [{"type": "text", "text": "after the call"}], USAGE),
            assistant("m2", [{"type": "text", "text": "second reply"}], {"input_tokens": 99000}),
        ])
        model, tokens, text, at = boot_probe.first_turn(p)
        self.assertEqual((model, tokens, at), ("claude-sonnet-5-5", 52803, "2026-10-22T22:59:00.000Z"))
        self.assertEqual(text, "ROLE LOADED: x")

    def test_report_line_flags_high_and_tags_agents(self):
        big = dict(USAGE, cache_read_input_tokens=50000)
        p = self.transcript([assistant("m1", [{"type": "text", "text": "hi"}], big)])
        self.assertEqual(boot_probe.report_line(p, "s1", now=NOW), "BOOT - banner=n/a first=70k claude-sonnet-5-5 HIGH")
        p = self.transcript([assistant("m1", [{"type": "text", "text": "hi"}], USAGE)])
        self.assertEqual(boot_probe.report_line(p, "s1", "Explore", now=NOW), "BOOT - banner=n/a first=53k claude-sonnet-5-5 agent:Explore")
        self.assertIn("first=? model?", boot_probe.report_line(self.dir / "missing.jsonl", "s1"))

    def test_banner_status_none_when_a_role_was_injected_and_no_banner(self):
        role_loader.mark_injected("s1", "MTS_Doctor", {"version": "v2", "token": "flag-lion"})
        self.assertEqual(boot_probe.banner_status("hello", "s1", ""), ("MTS_Doctor", "none"))
        self.assertEqual(boot_probe.banner_status("hello", "s2", ""), ("-", "n/a"))
        self.assertEqual(boot_probe.banner_status("ROLE LOADED: ...", "s1", "Explore"), ("-", "n/a"))

    def test_banner_status_maps_verify(self):
        role_loader.mark_injected("s1", "MTS_Doctor", {"version": "v2", "token": "flag-lion"})
        for code, want in ((0, "ok"), (2, "STALE")):
            with mock.patch.object(role_loader, "verify", return_value=code):
                self.assertEqual(boot_probe.banner_status("ROLE LOADED: x", "s1", ""), ("MTS_Doctor", want))

        def bad(text, role=None, sid=None, out=print):
            out("FAIL MTS_Doctor: banner v2/flag-lion does not match")
            return 1
        with mock.patch.object(role_loader, "verify", side_effect=bad):
            self.assertEqual(boot_probe.banner_status("ROLE LOADED: x", "s1", ""),
                             ("MTS_Doctor", "FAIL MTS_Doctor: banner v2/flag-lion does not match"))

    def test_a_session_older_than_the_probe_is_late_not_failed(self):
        """Live 2026-10-22 2250Z: a session running before the probe landed got banner=FAIL because a compaction had since
        re-recorded a newer token; its old first banner is not judged."""
        role_loader.mark_injected("s1", "Thinker", {"version": "v2", "token": "duck-nail"})
        old = self.transcript([assistant("m1", [{"type": "text", "text": "ROLE LOADED: x"}], USAGE, at="2026-10-22T19:27:34.545Z")])
        with mock.patch.object(role_loader, "verify", return_value=1):
            self.assertEqual(boot_probe.report_line(old, "s1", now=NOW), "BOOT Thinker banner=late first=53k claude-sonnet-5-5")
            new = self.transcript([assistant("m1", [{"type": "text", "text": "ROLE LOADED: x"}], USAGE)])
            self.assertTrue(boot_probe.report_line(new, "s1", now=NOW).startswith("BOOT Thinker banner=FAIL"))

    def test_spawns_once_per_session_and_per_subagent(self):
        p = self.transcript([])
        base = {"hook_event_name": "PostToolUse", "session_id": "s1", "transcript_path": str(p), "cwd": str(self.dir)}
        with mock.patch.object(boot_probe, "real_transcript", return_value=True), \
                mock.patch.object(boot_probe.subprocess, "Popen") as pop:
            self.assertTrue(boot_probe.maybe_spawn(base))
            self.assertFalse(boot_probe.maybe_spawn(base))
            self.assertTrue(boot_probe.maybe_spawn(dict(base, agent_id="a1", agent_type="Explore")))
            self.assertFalse(boot_probe.maybe_spawn(dict(base, agent_id="a1", agent_type="Explore")))
            self.assertFalse(boot_probe.maybe_spawn(dict(base, hook_event_name="PreToolUse", session_id="s9")))
        self.assertEqual(pop.call_count, 2)
        self.assertIn("--agent", pop.call_args_list[1][0][0])

    def test_tmp_transcripts_never_spawn(self):
        p = self.transcript([])
        with mock.patch.object(boot_probe.subprocess, "Popen") as pop:
            self.assertFalse(boot_probe.maybe_spawn({"hook_event_name": "PostToolUse", "session_id": "s1",
                                                     "transcript_path": str(p)}))
        pop.assert_not_called()

    def test_turn_meter_post_tool_use_starts_the_probe_for_sessions_and_subagents(self):
        with mock.patch.object(boot_probe, "maybe_spawn") as ms:
            turn_meter.handle({"hook_event_name": "PostToolUse", "session_id": "s1", "cwd": "C:/x"})
            turn_meter.handle({"hook_event_name": "PostToolUse", "session_id": "s1", "agent_id": "a1", "cwd": "C:/x"})
            turn_meter.handle({"hook_event_name": "UserPromptSubmit", "session_id": "s1", "prompt": "hi", "cwd": "C:/x"})
        self.assertEqual(ms.call_count, 2)


if __name__ == "__main__":
    unittest.main()
