"""Targeted unit tests for scripts/dev/yt_tor.py (config, port, path, log, and control helpers).

Existing coverage check (git grep -l "yt_tor" -- scripts MyTradingSys):
- scripts/dev/test_yt_freedom.py already covers parse_sha256sums, verify, install (hash-mismatch abort),
  safe_extract (path escape / symlink), and a basic localhost check on write_torrc / socks_url.
- Uncovered helpers targeted here: SOCKS/CONTROL port constants, proxy_dir/tor_dir/torrc_path/exe_path,
  platform_tag mapping, full write_torrc directive & geoip output, bootstrapped log parsing,
  latest_version validation, and _control cookie-auth wire formatting (all offline, no tor started).

Mutation check (broken scratch copy of yt_tor.py):
- Mutation: in `bootstrapped()`, changed `marks[-1] == "100"` to `marks[0] == "100"`.
- Failing test: `test_bootstrapped_log_parsing` (failed with `assert False is True` on a
  `Bootstrapped 50% ... Bootstrapped 100%` log because `marks[0]` was `"50"`).
"""
import io
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
DEV_DIR = Path(os.environ.get("YT_TOR_MODULE_DIR") or (REPO_ROOT / "scripts" / "dev"))
if str(DEV_DIR) not in sys.path:
    sys.path.insert(0, str(DEV_DIR))

import yt_tor  # noqa: E402


def test_ports_and_paths(monkeypatch, tmp_path):
    # SOURCED: scripts/dev/yt_tor.py:34-35, 54-55
    assert yt_tor.SOCKS == ("127.0.0.1", 40050)
    assert yt_tor.CONTROL == ("127.0.0.1", 40051)
    assert yt_tor.socks_url() == "socks5h://127.0.0.1:40050"

    proxy = tmp_path / "custom_proxy"
    monkeypatch.setenv("YT_PROXY_DIR", str(proxy))
    assert yt_tor.proxy_dir() == proxy
    assert yt_tor.tor_dir() == proxy / "tor"
    assert yt_tor.torrc_path() == proxy / "tor" / "torrc"
    assert yt_tor.exe_path() is None

    exe_name = "tor.exe" if os.name == "nt" else "tor"
    fallback_exe = proxy / "tor" / exe_name
    fallback_exe.parent.mkdir(parents=True, exist_ok=True)
    fallback_exe.write_bytes(b"")
    assert yt_tor.exe_path() == fallback_exe

    preferred_exe = proxy / "tor" / "tor" / exe_name
    preferred_exe.parent.mkdir(parents=True, exist_ok=True)
    preferred_exe.write_bytes(b"")
    assert yt_tor.exe_path() == preferred_exe


def test_platform_tag_mapping(monkeypatch):
    cases = [
        ("Windows", "AMD64", "windows-x86_64"),
        ("Darwin", "arm64", "macos-aarch64"),
        ("Linux", "aarch64", "linux-aarch64"),
        ("FreeBSD", "amd64", "linux-x86_64"),
    ]
    for sysname, mach, expected in cases:
        monkeypatch.setattr(yt_tor.platform, "system", lambda s=sysname: s)
        monkeypatch.setattr(yt_tor.platform, "machine", lambda m=mach: m)
        assert yt_tor.platform_tag() == expected


def test_write_torrc_exact_lines_and_geoip(monkeypatch, tmp_path):
    proxy = tmp_path / "proxy"
    monkeypatch.setenv("YT_PROXY_DIR", str(proxy))
    yt_tor.write_torrc()

    tor_base = proxy / "tor"
    assert (tor_base / "data" / "state").is_dir()
    expected_base = [
        "SocksPort 127.0.0.1:40050",
        "ControlPort 127.0.0.1:40051",
        "CookieAuthentication 1",
        f"CookieAuthFile {(tor_base / 'data' / 'control_auth_cookie').as_posix()}",
        f"DataDirectory {(tor_base / 'data' / 'state').as_posix()}",
        "ClientOnly 1",
        "AvoidDiskWrites 1",
        f"Log notice file {(tor_base / 'tor.log').as_posix()}",
    ]
    assert yt_tor.torrc_path().read_text(encoding="utf-8").splitlines() == expected_base

    (tor_base / "data" / "geoip").write_text("", encoding="utf-8")
    (tor_base / "data" / "geoip6").write_text("", encoding="utf-8")
    yt_tor.write_torrc()
    expected_with_geoip = expected_base + [
        f"GeoIPFile {(tor_base / 'data' / 'geoip').as_posix()}",
        f"GeoIPv6File {(tor_base / 'data' / 'geoip6').as_posix()}",
    ]
    assert yt_tor.torrc_path().read_text(encoding="utf-8").splitlines() == expected_with_geoip


def test_bootstrapped_log_parsing(monkeypatch, tmp_path):
    proxy = tmp_path / "proxy"
    monkeypatch.setenv("YT_PROXY_DIR", str(proxy))
    log = proxy / "tor" / "tor.log"
    log.parent.mkdir(parents=True, exist_ok=True)

    assert yt_tor.bootstrapped() is False

    log.write_text("Starting tor\nNo bootstrap info\n", encoding="utf-8")
    assert yt_tor.bootstrapped() is False

    log.write_text("Bootstrapped 50% (loading_descriptors)\nBootstrapped 100% (done)\n", encoding="utf-8")
    assert yt_tor.bootstrapped() is True

    log.write_text("Bootstrapped 100% (done)\nBootstrapped 50% (restarting)\n", encoding="utf-8")
    assert yt_tor.bootstrapped() is False


def test_latest_version_and_control_auth_formatting(monkeypatch, tmp_path):
    assert yt_tor.latest_version(get=lambda _url: json.dumps({"version": "14.0.1"})) == "14.0.1"
    assert yt_tor.latest_version(get=lambda _url: json.dumps({"version": "14.0"})) == "14.0"
    for bad in ({}, {"version": "14.0.1-alpha"}):
        with pytest.raises(yt_tor.TorError):
            yt_tor.latest_version(get=lambda _url, b=bad: json.dumps(b))

    proxy = tmp_path / "proxy"
    monkeypatch.setenv("YT_PROXY_DIR", str(proxy))
    # Missing cookie returns False without opening a socket
    assert yt_tor._control("SIGNAL NEWNYM") is False

    cookie_path = proxy / "tor" / "data" / "control_auth_cookie"
    cookie_path.parent.mkdir(parents=True, exist_ok=True)
    cookie_path.write_bytes(b"\xde\xad\xbe\xef")

    sent = bytearray()

    class FakeSocket:
        def __init__(self, reply_bytes):
            self._r = io.BytesIO(reply_bytes)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def makefile(self, _mode, buffering=0):
            r = self._r

            class FakeFile:
                def write(self, data):
                    sent.extend(data)

                def readline(self):
                    return r.readline()

            return FakeFile()

    monkeypatch.setattr(yt_tor.socket, "create_connection", lambda addr, timeout=5: FakeSocket(b"250 OK\r\n250 OK\r\n"))
    assert yt_tor._control("SIGNAL NEWNYM") is True
    assert bytes(sent) == b"AUTHENTICATE deadbeef\r\nSIGNAL NEWNYM\r\n"

    monkeypatch.setattr(yt_tor.socket, "create_connection", lambda addr, timeout=5: FakeSocket(b"515 Bad auth\r\n"))
    assert yt_tor._control("SIGNAL NEWNYM") is False
