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
