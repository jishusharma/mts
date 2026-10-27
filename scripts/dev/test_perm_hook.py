import sys, pathlib, unittest, json, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import perm_hook as h

REQ = {"hook_event_name": "PermissionRequest", "tool_name": "Bash", "permission_mode": "bypassPermissions",
       "tool_input": {"command": "mkdir /f/MTS_backup_dirty && cp a /f/MTS_backup_dirty && git pull"}}


class T(unittest.TestCase):
    def test_allows_any_tool(self):
        out = h.decide(REQ)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PermissionRequest")
        self.assertEqual(out["hookSpecificOutput"]["decision"]["behavior"], "allow")

    def test_allows_mcp_and_write(self):
        for name in ("Write", "mcp__ccd_session__start_session", "WebFetch", "PowerShell"):
            self.assertEqual(h.decide({**REQ, "tool_name": name})["hookSpecificOutput"]["decision"]["behavior"], "allow")

    def test_garbage_input_still_allows(self):
        self.assertEqual(h.decide(None)["hookSpecificOutput"]["decision"]["behavior"], "allow")

    def test_log_line_has_tool_mode_and_clipped_detail(self):
        with tempfile.TemporaryDirectory() as d:
            log = pathlib.Path(d) / "perm.jsonl"
            h.log_request({**REQ, "tool_input": {"command": "x" * 500}}, log)
            row = json.loads(log.read_text().splitlines()[0])
            self.assertEqual((row["tool"], row["mode"]), ("Bash", "bypassPermissions"))
            self.assertLessEqual(len(row["detail"]), 160)

    def test_main_prints_allow_json_and_exits_0(self):
        import io, contextlib
        buf = io.StringIO()
        sys.stdin = io.StringIO(json.dumps(REQ))
        with contextlib.redirect_stdout(buf):
            rc = h.main(log_path=pathlib.Path(tempfile.mkdtemp()) / "p.jsonl")
        sys.stdin = sys.__stdin__
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(buf.getvalue())["hookSpecificOutput"]["decision"]["behavior"], "allow")

    def test_install_merges_idempotently(self):
        s = {"hooks": {"UserPromptSubmit": [{"hooks": []}]}}
        a = h.install_into_settings(s, "python x.py")
        b = h.install_into_settings(a, "python x.py")
        self.assertEqual(len(b["hooks"]["PermissionRequest"]), 1)
        self.assertIn("UserPromptSubmit", b["hooks"])


if __name__ == "__main__":
    unittest.main()
