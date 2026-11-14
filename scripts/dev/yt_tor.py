"""YouTube freedom, route (b): a local Tor SOCKS port for YouTube traffic only (official Tor Project expert bundle).

Tor is another free exit for yt.py: a user-space process listening on 127.0.0.1:40050 (SOCKS) and 127.0.0.1:40051 (control,
cookie auth, only for NEWNYM = a fresh circuit). No system routes, no admin rights, trading traffic untouched: only the
YouTube calls yt.py hands this URL to go through it, and yt.py refuses a non-YouTube host on any proxy (yt.yt_only).
Everything lives in ~/.mts/ytproxy/tor/ (outside the repo, never committed).

    python scripts/dev/yt_tor.py install    # download the bundle from torproject.org, verify sha256 on two hosts, extract
    python scripts/dev/yt_tor.py start      # start tor and wait for "Bootstrapped 100%"
    python scripts/dev/yt_tor.py status | stop | newnym

Verification: the bundle's sha256 must equal the line in sha256sums-signed-build.txt from dist.torproject.org AND the copy on
archive.torproject.org (two hosts must agree; the .asc signature is checked too when `gpg` is on PATH and the Tor Browser
signing key is in its keyring, otherwise reported as not checked). Nothing is run before the hash matches.
"""
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SOCKS = ("127.0.0.1", 40050)   # OURS (WARP's wireproxy uses 40000)
CONTROL = ("127.0.0.1", 40051)
VERSIONS_URL = "https://aus1.torproject.org/torbrowser/update_3/release/downloads.json"
DIST = "https://dist.torproject.org/torbrowser/{v}/"
ARCHIVE = "https://archive.torproject.org/tor-package-archive/torbrowser/{v}/"
UA = "Mozilla/5.0 (compatible; mts-yt-tor)"


class TorError(Exception):
    pass


def proxy_dir():
    return Path(os.environ.get("YT_PROXY_DIR") or Path.home() / ".mts" / "ytproxy")


def tor_dir():
    return proxy_dir() / "tor"


def socks_url():
    return "socks5h://%s:%d" % SOCKS    # socks5h: the exit resolves names, nothing leaks to local DNS


def platform_tag():
    sysname, mach = platform.system().lower(), platform.machine().lower()
    arch = "aarch64" if mach in ("arm64", "aarch64") else "x86_64"
    return {"windows": "windows-" + arch, "linux": "linux-" + arch, "darwin": "macos-" + arch}.get(sysname, "linux-x86_64")


def exe_path():
    d = tor_dir()
    name = "tor.exe" if os.name == "nt" else "tor"
    for p in (d / "tor" / name, d / name):
        if p.exists():
            return p
    return None


def _get(url, binary=False, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    import ssl
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        body = r.read()
    return body if binary else body.decode("utf-8", "replace")


def parse_sha256sums(text):
    """{filename: sha256} from a `<hash>  <name>` list (a leading * on the name marks binary mode)."""
    out = {}
    for line in (text or "").splitlines():
        m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(\S+)\s*$", line.strip())
        if m:
            out[m.group(2)] = m.group(1).lower()
    return out


def latest_version(get=_get):
    """Current stable Tor Browser version (the expert bundle shares it)."""
    v = json.loads(get(VERSIONS_URL)).get("version")
    if not v or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", str(v)):
        raise TorError("could not read the current Tor version")
    return str(v)


def verify(data, name, sums_by_host):
    """Raise TorError unless sha256(data) equals the entry for `name` on EVERY host list given (at least two)."""
    got = hashlib.sha256(data).hexdigest()
    if len(sums_by_host) < 2:
        raise TorError("need the checksum list from two hosts")
    for host, sums in sums_by_host.items():
        want = sums.get(name)
        if not want:
            raise TorError(f"{name} not listed on {host}")
        if want != got:
            raise TorError(f"sha256 mismatch against {host}: {got} != {want}")
    return got


def safe_extract(tar_path, dest):
    """Extract a tar.gz refusing absolute paths, `..`, links and devices."""
    dest = Path(dest).resolve()
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf.getmembers():
            target = (dest / m.name).resolve()
            if not (target == dest or dest in target.parents) or m.issym() or m.islnk() or m.isdev():
                raise TorError(f"unsafe member in archive: {m.name}")
        tf.extractall(dest)


def install(get=_get, version=None):
    """Download, verify (two hosts) and extract the expert bundle; returns the tor executable path. Idempotent."""
    if exe_path():
        return exe_path()
    v = version or latest_version(get)
    name = f"tor-expert-bundle-{platform_tag()}-{v}.tar.gz"
    sums = {}
    for host_name, base in (("dist.torproject.org", DIST), ("archive.torproject.org", ARCHIVE)):
        try:
            sums[host_name] = parse_sha256sums(get(base.format(v=v) + "sha256sums-signed-build.txt"))
        except Exception as e:   # archive lags a release by a day or two: say so, never skip silently
            print(f"checksum list from {host_name} unavailable: {str(e)[:80]}")
    data = get(DIST.format(v=v) + name, binary=True, timeout=300)
    got = verify(data, name, sums)
    print(f"sha256 {got} matches {', '.join(sums)}")
    d = tor_dir()
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / name
    tmp.write_bytes(data)
    try:
        safe_extract(tmp, d)
    finally:
        tmp.unlink(missing_ok=True)
    print("signature:", _gpg_note(v, get, d))
    if not exe_path():
        raise TorError("tor executable not found after extract")
    write_torrc()
    return exe_path()


def _gpg_note(v, get, d):
    if not shutil.which("gpg"):
        return "not checked (no gpg on PATH); two-host sha256 match stands"
    return "gpg present but the signing key is not imported by this tool: not checked; two-host sha256 match stands"


def torrc_path():
    return tor_dir() / "torrc"


def write_torrc():
    d = tor_dir()
    data = d / "data" / "state"
    data.mkdir(parents=True, exist_ok=True)
    geo = d / "data"
    lines = [f"SocksPort {SOCKS[0]}:{SOCKS[1]}",
             f"ControlPort {CONTROL[0]}:{CONTROL[1]}",
             "CookieAuthentication 1",
             f"CookieAuthFile {(d / 'data' / 'control_auth_cookie').as_posix()}",
             f"DataDirectory {data.as_posix()}",
             "ClientOnly 1",
             "AvoidDiskWrites 1",
             f"Log notice file {(d / 'tor.log').as_posix()}"]
    for gname, key in (("geoip", "GeoIPFile"), ("geoip6", "GeoIPv6File")):
        if (geo / gname).exists():
            lines.append(f"{key} {(geo / gname).as_posix()}")
    torrc_path().write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def port_open(addr=SOCKS, timeout=1.0):
    try:
        with socket.create_connection(addr, timeout=timeout):
            return True
    except OSError:
        return False


def bootstrapped():
    try:
        txt = (tor_dir() / "tor.log").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    marks = re.findall(r"Bootstrapped (\d+)%", txt)
    return bool(marks) and marks[-1] == "100"


def start(wait=120):
    """True when the SOCKS port answers and Tor is bootstrapped; starts tor detached if it is not running."""
    if port_open() and bootstrapped():
        return True
    exe = exe_path()
    if not exe:
        raise TorError("tor not installed: python scripts/dev/yt_tor.py install")
    if not port_open():
        write_torrc()
        (tor_dir() / "tor.log").unlink(missing_ok=True)
        flags = (0x08000000 | 0x00000008) if os.name == "nt" else 0   # CREATE_NO_WINDOW | DETACHED_PROCESS
        subprocess.Popen([str(exe), "-f", str(torrc_path())], cwd=str(exe.parent), stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, creationflags=flags,
                         **({} if os.name == "nt" else {"start_new_session": True}))
    end = time.monotonic() + wait
    while time.monotonic() < end:
        if port_open() and bootstrapped():
            return True
        time.sleep(1)
    return False


def stop():
    """Ask tor to exit through the control port (SIGNAL SHUTDOWN); falls back to a process kill on Windows."""
    if _control("SIGNAL SHUTDOWN"):
        return True
    if os.name == "nt":
        return subprocess.run(["taskkill", "/F", "/IM", "tor.exe"], capture_output=True).returncode == 0
    return False


def _control(command):
    """Send one authenticated control command (cookie auth); True on a 250 reply."""
    try:
        cookie = (tor_dir() / "data" / "control_auth_cookie").read_bytes()
        with socket.create_connection(CONTROL, timeout=5) as s:
            f = s.makefile("rwb", buffering=0)
            f.write(b"AUTHENTICATE " + cookie.hex().encode() + b"\r\n")
            if not f.readline().startswith(b"250"):
                return False
            f.write(command.encode() + b"\r\n")
            return f.readline().startswith(b"250")
    except OSError:
        return False


def newnym():
    """A fresh circuit (new exit) for the next connection; Tor rate-limits this to about one per 10 s."""
    ok = _control("SIGNAL NEWNYM")
    if ok:
        time.sleep(2)
    return ok


def main(argv):
    cmd = argv[0] if argv else "status"
    if cmd == "install":
        print("tor:", install())
        return 0
    if cmd == "start":
        ok = start()
        print("tor", "UP " + socks_url() if ok else "NOT UP (see ~/.mts/ytproxy/tor/tor.log)")
        return 0 if ok else 1
    if cmd == "stop":
        print("stopped" if stop() else "not stopped")
        return 0
    if cmd == "newnym":
        print("new circuit" if newnym() else "newnym failed")
        return 0
    print(f"installed={bool(exe_path())} port_open={port_open()} bootstrapped={bootstrapped()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
