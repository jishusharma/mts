"""Spec checks for the token-free AIBridge health probe."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("aibridge_health_under_test", HERE / "aibridge_health.py")
health = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(health)


class FakeSocket:
    def __init__(self, reply=b"HTTP/1.1 503 Unavailable\r\n", recv_error=None):
        self.reply, self.recv_error = reply, recv_error
        self.closed = False
        self.sent = None
        self.timeout = None

    def settimeout(self, value):
        self.timeout = value

    def sendall(self, data):
        self.sent = data

    def recv(self, size):
        assert size == 256
        if self.recv_error:
            raise self.recv_error
        return self.reply[:size]

    def close(self):
        self.closed = True


def test_liveness_accepts_any_http_status_at_256_byte_read_limit(monkeypatch, capsys):
    prefix = b"HTTP/1.1 503 "
    sock = FakeSocket(prefix + b"x" * (256 - len(prefix)))
    monkeypatch.setattr(health.socket, "create_connection", lambda *a, **k: sock)
    assert health.liveness() == 0
    assert "UP (HTTP/1.1 503" in capsys.readouterr().out
    assert sock.timeout == 3 and sock.closed
    assert sock.sent.startswith(b"OPTIONS /run HTTP/1.1\r\n")


def test_liveness_accepts_one_byte_below_read_limit(monkeypatch, capsys):
    prefix = b"HTTP/1.1 204 OK\r\n"
    sock = FakeSocket(prefix + b"x" * (255 - len(prefix)))
    monkeypatch.setattr(health.socket, "create_connection", lambda *a, **k: sock)
    assert health.liveness() == 0
    assert "UP (HTTP/1.1 204 OK)" in capsys.readouterr().out


def test_liveness_reply_one_byte_over_limit_still_checks_status_line(monkeypatch, capsys):
    prefix = b"HTTP/1.1 200 OK\r\n"
    sock = FakeSocket(prefix + b"x" * (257 - len(prefix)))
    monkeypatch.setattr(health.socket, "create_connection", lambda *a, **k: sock)
    assert health.liveness() == 0
    assert "UP (HTTP/1.1 200 OK)" in capsys.readouterr().out


def test_liveness_connect_error_is_down(monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise OSError("refused")
    monkeypatch.setattr(health.socket, "create_connection", fail)
    assert health.liveness() == 1
    assert "DOWN (refused)" in capsys.readouterr().out


def test_liveness_recv_error_closes_socket_and_is_down(monkeypatch, capsys):
    sock = FakeSocket(recv_error=TimeoutError("timed out"))
    monkeypatch.setattr(health.socket, "create_connection", lambda *a, **k: sock)
    assert health.liveness() == 1
    assert "port open, no HTTP reply (timed out)" in capsys.readouterr().out
    assert sock.closed


def test_liveness_empty_or_non_http_reply_is_down(monkeypatch, capsys):
    sock = FakeSocket(b"")
    monkeypatch.setattr(health.socket, "create_connection", lambda *a, **k: sock)
    assert health.liveness() == 1
    assert "UP ()" in capsys.readouterr().out


def test_liveness_malformed_non_http_status_line_is_down(monkeypatch, capsys):
    sock = FakeSocket(b"NOT HTTP\r\n")
    monkeypatch.setattr(health.socket, "create_connection", lambda *a, **k: sock)
    assert health.liveness() == 1
    assert "UP (NOT HTTP)" in capsys.readouterr().out


def test_installed_version_reads_manifest_and_agent_from_temp_root(tmp_path):
    (tmp_path / "extension").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "extension" / "manifest.json").write_text('{"version":"1.2.3"}', encoding="utf-8")
    (tmp_path / "src" / "agent.ps1").write_text("$AgentVersion = '1.2.3'\n", encoding="utf-8")
    assert health.installed_version(str(tmp_path)) == ("1.2.3", "1.2.3")


def test_installed_version_empty_root_returns_none_values(tmp_path):
    assert health.installed_version(str(tmp_path)) == (None, None)


@pytest.mark.parametrize("manifest", ["{bad", "{}"])
def test_installed_version_malformed_or_missing_version_is_none(tmp_path, manifest):
    path = tmp_path / "extension"
    path.mkdir()
    (path / "manifest.json").write_text(manifest, encoding="utf-8")
    assert health.installed_version(str(tmp_path))[0] is None


def test_running_version_reads_agent_field(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"agent":"1.2.3"}'
    monkeypatch.setattr(health.urllib.request, "urlopen", lambda *a, **k: Response())
    assert health.running_version() == "1.2.3"


@pytest.mark.parametrize("payload", [b"", b"not json", b"{}"])
def test_running_version_empty_malformed_or_missing_agent_returns_none(monkeypatch, payload):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return payload
    monkeypatch.setattr(health.urllib.request, "urlopen", lambda *a, **k: Response())
    assert health.running_version() is None


def test_running_version_request_error_returns_none(monkeypatch):
    monkeypatch.setattr(health.urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(OSError("offline")))
    assert health.running_version() is None


def test_trunk_current_uses_origin_release_when_git_show_succeeds(monkeypatch):
    monkeypatch.setattr(health.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0], 0, '{"current":"2.0"}', ""))
    assert health.trunk_current() == ("2.0", "origin/fast-track")


def test_trunk_current_falls_back_to_checkout_when_git_show_fails(monkeypatch):
    monkeypatch.setattr(health.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0], 1, "", "missing ref"))
    monkeypatch.setattr(health.av, "load", lambda root: {"current": "1.9"})
    assert health.trunk_current() == ("1.9", "this checkout")


def test_version_report_warns_for_installed_and_running_mismatches(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(health, "installed_version", lambda root: ("1.0", "agent-file"))
    monkeypatch.setattr(health, "running_version", lambda: "2.0")
    monkeypatch.setattr(health, "trunk_current", lambda: ("3.0", "origin/fast-track"))
    monkeypatch.setattr(health.av, "load", lambda root: {"current": "3.0"})
    health.version_report(str(tmp_path))
    out = capsys.readouterr().out
    assert "WARN installed 1.0 is not trunk 3.0" in out
    assert "WARN running agent 2.0 is not the installed 1.0" in out


def test_main_defaults_root_and_returns_liveness_code(monkeypatch, capsys):
    seen = []
    monkeypatch.setattr(health, "liveness", lambda: 1)
    monkeypatch.setattr(health, "version_report", lambda root: seen.append(root))
    assert health.main([]) == 1
    assert seen == ["F:/AIBridge"]

