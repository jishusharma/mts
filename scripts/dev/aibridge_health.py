"""aibridge_health.py - is the DSA AI Bridge agent answering on 127.0.0.1:7181, and which bridge version runs where?

Exit 0 = port accepts a TCP connection and the agent replies to an OPTIONS request (any HTTP status);
exit 1 = down. The version lines are report-only and never change the exit code. Sends no token and runs no command:
GET /ping is the agent's token-free identity probe.
Usage: python scripts/dev/aibridge_health.py [F:/AIBridge]
"""
import json
import os
import subprocess
import socket
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aibridge_version as av  # noqa: E402

HOST, PORT = "127.0.0.1", 7181


def liveness() -> int:
    try:
        s = socket.create_connection((HOST, PORT), timeout=3)
    except OSError as e:
        print(f"aibridge: DOWN ({e})")
        return 1
    try:
        s.settimeout(3)
        s.sendall(b"OPTIONS /run HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
        data = s.recv(256)
    except OSError as e:
        print(f"aibridge: port open, no HTTP reply ({e})")
        return 1
    finally:
        s.close()
    first = data.split(b"\r\n", 1)[0].decode("ascii", "replace")
    print(f"aibridge: UP ({first})")
    return 0 if first.startswith("HTTP/") else 1


def installed_version(root):
    """(extension manifest version, agent version) of the copy on disk under root; None where unreadable."""
    try:
        with open(os.path.join(root, "extension", "manifest.json"), encoding="utf-8-sig") as f:
            manifest = json.load(f)["version"]
    except (OSError, ValueError, KeyError):
        manifest = None
    try:
        with open(os.path.join(root, "src", "agent.ps1"), encoding="utf-8-sig") as f:
            agent = av.version_at(f.read(), r"\$AgentVersion = '([^']+)'")
    except OSError:
        agent = None
    return manifest, agent


def running_version():
    """Agent version from GET /ping (no token, no origin header), or None when nothing answers."""
    try:
        with urllib.request.urlopen(f"http://{HOST}:{PORT}/ping", timeout=3) as r:
            return json.loads(r.read().decode("utf-8", "replace")).get("agent")
    except Exception:
        return None


def trunk_current():
    """RELEASES.json current on origin/fast-track as last fetched (no network); this checkout's when git cannot say."""
    r = subprocess.run(["git", "-C", av.REPO, "show", f"origin/fast-track:{av.RELEASES_REL}"], capture_output=True, text=True)
    if r.returncode == 0:
        return json.loads(r.stdout)["current"], "origin/fast-track"
    return av.load(av.REPO)["current"], "this checkout"


def version_report(root) -> None:
    manifest, agent = installed_version(root)
    running = running_version()
    trunk, src = trunk_current()
    print(f"bridge version: installed {manifest or 'none'} ({root}; agent file {agent or 'none'}) | "
          f"running agent {running or 'no answer'} | this checkout {av.load(av.REPO)['current']} | trunk {trunk} ({src})")
    if manifest != trunk:
        print(f"WARN installed {manifest} is not trunk {trunk}: from a checkout at origin/fast-track run "
              f"python scripts/dev/aibridge_install.py {root} --restart-agent, then reload the extension in chrome://extensions and F5 the chat")
    if running and manifest and running != manifest:
        print(f"WARN running agent {running} is not the installed {manifest}: restart the agent (aibridge_install.py --restart-agent)")


def main(argv) -> int:
    root = next((a for a in argv if not a.startswith("--")), "F:/AIBridge").rstrip("/\\")
    rc = liveness()
    version_report(root)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
