import importlib.util
import json
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location(
    "role_hook_launcher_under_test", Path(__file__).with_name("role_hook_launcher.py")
)
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


def repo(tmp_path):
    (tmp_path / "MyTradingSys").mkdir()
    return tmp_path


def install_git(monkeypatch, *, rc=0, src='def handle(payload, top): return "banner"'):
    calls = []

    def fake_git(top, *args):
        calls.append(args)
        if args == ("rev-parse", "--show-toplevel"):
            return 0, str(top)
        return rc, src

    monkeypatch.setattr(launcher, "_git", fake_git)
    return calls


def test_at_boundary_of_known_roles_matches_role(monkeypatch, tmp_path):
    top = repo(tmp_path)
    install_git(monkeypatch)
    assert launcher.names_role("You are Lead") == "Lead"
    assert launcher.run({"cwd": str(top), "prompt": "You are Lead"}) == "banner"


def test_one_below_role_name_does_not_invoke_loader(monkeypatch, tmp_path):
    top = repo(tmp_path)
    calls = install_git(monkeypatch)
    assert launcher.names_role("You are Leadx") is None
    assert launcher.run({"cwd": str(top), "prompt": "You are Leadx"}) == "banner"
    # The trunk loader runs for ordinary prompts too; the expected loader output is still returned.
    assert calls[-1] == ("show", "origin/fast-track:scripts/dev/role_loader.py")


def test_one_above_role_name_does_not_match_role(monkeypatch, tmp_path):
    top = repo(tmp_path)
    install_git(monkeypatch, rc=1, src="")
    assert launcher.run({"cwd": str(top), "prompt": "You are Lead2"}) == ""


def test_empty_input_defaults_to_empty_payload_and_skips_non_repo(monkeypatch, tmp_path):
    monkeypatch.setattr(launcher, "toplevel", lambda cwd: None)
    assert launcher.run({}) == ""


def test_malformed_prompt_type_is_treated_as_empty(monkeypatch, tmp_path):
    top = repo(tmp_path)
    install_git(monkeypatch)
    assert launcher.run({"cwd": str(top), "prompt": ["You are Lead"]}) == "banner"


def test_role_with_missing_trunk_loader_reports_not_loaded(monkeypatch, tmp_path):
    top = repo(tmp_path)
    install_git(monkeypatch, rc=1, src="")
    result = json.loads(launcher.run({"cwd": str(top), "prompt": "You are Lead"}))
    context = result["hookSpecificOutput"]["additionalContext"]
    assert result["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "ROLE NOT LOADED: scripts/dev/role_loader.py missing" in context


def test_loader_exception_reports_type(monkeypatch, tmp_path):
    top = repo(tmp_path)
    install_git(monkeypatch, src='def handle(payload, top): raise ValueError("x")')
    result = json.loads(launcher.run({"cwd": str(top), "prompt": "You are Lead"}))
    assert "ROLE NOT LOADED: trunk role_loader failed: ValueError" in result["hookSpecificOutput"]["additionalContext"]


def test_existing_project_hook_skips_unless_stale_bare_login(tmp_path, monkeypatch):
    top = repo(tmp_path)
    (top / ".claude").mkdir()
    (top / ".claude" / "settings.json").write_text('{"command":"role_loader.py"}', encoding="utf-8")
    calls = install_git(monkeypatch)
    assert launcher.run({"cwd": str(top), "prompt": "You are Lead"}) == ""
    assert calls == [("rev-parse", "--show-toplevel")]


def test_install_and_uninstall_replace_only_launcher_entries(tmp_path, monkeypatch, capsys):
    home = tmp_path / ".claude"
    home.mkdir()
    settings = home / "settings.json"
    settings.write_text(json.dumps({"other": 7, "hooks": {"UserPromptSubmit": [
        {"hooks": [{"type": "command", "command": "keep-me"},
                    {"type": "command", "command": "python mts_role_launcher.py hook"}]}
    ]}}), encoding="utf-8")
    monkeypatch.setattr(launcher, "__file__", str(tmp_path / "source.py"))
    Path(launcher.__file__).write_text("source", encoding="utf-8")
    launcher.install(home)
    installed = json.loads(settings.read_text(encoding="utf-8"))
    assert installed["other"] == 7
    for event in ("SessionStart", "UserPromptSubmit"):
        entries = installed["hooks"][event]
        hooks = [hook for group in entries for hook in group["hooks"]]
        launcher_hooks = [hook for hook in hooks if "mts_role_launcher.py" in hook["command"]]
        assert len(launcher_hooks) == 1
        assert launcher_hooks[0]["type"] == "command" and launcher_hooks[0]["timeout"] == 20
    launcher.install(home, add=False)
    removed = json.loads(settings.read_text(encoding="utf-8"))
    assert removed == {"other": 7, "hooks": {"UserPromptSubmit": [{"hooks": [
        {"type": "command", "command": "keep-me"}
    ]}]}}
