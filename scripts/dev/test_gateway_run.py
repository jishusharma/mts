import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gateway_run as g  # noqa: E402

FAKE = "sk-test-" + "x" * 20


def _reg(tmp_path, key=FAKE):
    body = ('Windows Registry Editor Version 5.00\r\n\r\n[HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Claude]\r\n'
            '"inferenceGatewayBaseUrl"="https://gw.example/"\r\n'
            f'"inferenceGatewayApiKey"="{key}"\r\n"inferenceProvider"="gateway"\r\n')
    p = tmp_path / "Claude-good.reg"
    p.write_bytes(b"\xff\xfe" + body.encode("utf-16-le"))
    return p


def test_reg_parse_utf16(tmp_path):
    r = g.read_reg(_reg(tmp_path))
    assert r["inferenceGatewayBaseUrl"] == "https://gw.example/" and r["inferenceGatewayApiKey"] == FAKE


def test_key_file_wins_over_reg(tmp_path):
    kf = tmp_path / "key"
    kf.write_text("sk-newer\n", encoding="utf-8")
    assert g.load_secret(kf, _reg(tmp_path)) == ("https://gw.example/", "sk-newer")


def test_child_env_drops_subscription_and_sets_gateway():
    env = g.child_env("https://gw.example/", FAKE, "api-key",
                      {"PATH": "x", "CLAUDE_CODE_OAUTH_TOKEN": "sub", "ANTHROPIC_BASE_URL": "https://api.anthropic.com"})
    assert "CLAUDE_CODE_OAUTH_TOKEN" not in env and env["ANTHROPIC_BASE_URL"] == "https://gw.example/"
    assert env["ANTHROPIC_API_KEY"] == FAKE and env["MTS_GATEWAY"] == "1" and env["PATH"] == "x"
    assert g.child_env("b", FAKE, "bearer", {})["ANTHROPIC_AUTH_TOKEN"] == FAKE


def test_summary_and_prompt_never_hold_key():
    s = g.summary('{"is_error": false, "num_turns": 1, "modelUsage": {"claude-opus-5-5": {}}, "result": "ok ' + FAKE + '"}', FAKE)
    assert FAKE not in str(s) and s["models"] == ["claude-opus-5-5"]
    assert FAKE not in g.summary("boom " + FAKE, FAKE)["result"]
    assert "{" not in g.CHILD_PROMPT.format(run="O1", model=g.MODEL)


def test_invalid_key_text_is_an_error():
    s = g.summary('{"is_error": false, "num_turns": 1, "modelUsage": {}, "result": "Invalid API key. Please check"}', FAKE)
    assert s["is_error"] is True


def test_repo_root_is_the_main_checkout():
    root = g.repo_root(Path(__file__).parent)
    assert (root / ".git").is_dir() and (root / "scripts" / "dev").is_dir()


def test_stream_json_summary_reads_last_result_line():
    stream = '{"type": "system", "session_id": "s"}\n{"type": "result", "is_error": false, "num_turns": 7, "modelUsage": {"claude-opus-5-5": {}}, "result": "done"}\n'
    s = g.summary(stream, FAKE)
    assert s["is_error"] is False and s["num_turns"] == 7


def test_resume_args_compact_on_same_session():
    a = g.claude_args("/compact", "sid-1", True)
    assert a[2] == "/compact" and a[-2:] == ["--resume", "sid-1"] and "stream-json" in a
    assert g.claude_args("x", "", True)[-1] == "--continue"
    assert g.claude_args("x", "sid-1", False)[-2:] == ["--session-id", "sid-1"]


def test_verdict_restart_hang_and_cap():
    assert g.verdict(True, True, False, 0, True, 0) == "done"
    assert g.verdict(False, True, False, 1, False, 0) == "resume"            # station restarted: task not Running
    assert g.verdict(False, True, True, g.HANG_MIN, True, 0) == "kill-resume"
    assert g.verdict(False, True, True, g.HANG_MIN, False, 0) == "running"   # old json run: silence is normal
    assert g.verdict(False, True, True, 5, True, 0) == "running"
    assert g.verdict(False, True, False, 1, True, g.MAX_RESUMES) == "gave-up"
    assert g.verdict(False, False, False, 0, False, 0) == "idle"
