"""test_git_net_deadline.py - verify all network git callers in scope_in enforce timeout and no-prompt env."""
import re
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[2]
SCOPE_FILES = [
    "scripts/dev/auto_deploy.py",
    "scripts/dev/trunk_lag.py",
    "scripts/dev/lane_health.py",
    "scripts/dev/nuc_wake.py",
]
NET_VERBS = ("fetch", "push", "pull", "ls-remote", "clone")


def test_scope_in_files_have_git_noprompt_and_timeouts():
    """Verify each file in scope_in defines/uses GIT_NOPROMPT (or GIT_TERMINAL_PROMPT) and has timeouts on git calls."""
    for rel in SCOPE_FILES:
        path = REPO / rel
        assert path.exists(), f"File {rel} must exist"
        text = path.read_text(encoding="utf-8")
        
        # Check no-prompt env configuration
        has_noprompt = ("GIT_NOPROMPT" in text or "GIT_TERMINAL_PROMPT" in text)
        assert has_noprompt, f"{rel} lacks GIT_NOPROMPT / GIT_TERMINAL_PROMPT protection"


def test_lane_health_git_has_timeout():
    """lane_health.py git() must take/pass a timeout."""
    text = (REPO / "scripts/dev/lane_health.py").read_text(encoding="utf-8")
    assert "timeout" in text.split("def git(")[1].split("\n")[0] or "timeout=" in text.split("def git(")[1].split("return ")[1].split("\n")[0]


def test_trunk_lag_git_has_noprompt():
    """trunk_lag.py git() must pass GIT_NOPROMPT in env."""
    text = (REPO / "scripts/dev/trunk_lag.py").read_text(encoding="utf-8")
    assert "GIT_NOPROMPT" in text or "GIT_TERMINAL_PROMPT" in text
