"""Run the guarded YouTube caption fetch through a short-lived OpenVPN session (our home IP is YouTube-429 blocked).

Usage (repo root, elevated shell; the .ovpn profile lives OUTSIDE the repo and is never read, printed or copied here):
    python scripts/dev/yt_vpn_fetch.py --profile D:/vpn/x.ovpn --analyst Krown --out DIR [--max-videos 5] ID [ID ...]
    add --only-youtube-routes --routes-file google_cidrs.txt   (best effort: ranges move) for split routing.
Flow: refuse a profile inside the repo; note the public IP (api.ipify.org); start openvpn.exe as a child, wait for
"Initialization Sequence Completed" (--connect-timeout), verify the public IP CHANGED (else tear down and stop); call
fetch_captions_timed.main (same guard: <= 5 videos, ONE try per video, 20 s apart, stop at the first 429 / sign-in check,
no retry on another exit); ALWAYS tear openvpn down in a finally block and confirm the public IP is back to the original,
printing a loud WARNING and exiting 4 if not. Default is whole-machine routing for the few minutes the fetch takes.
--only-youtube-routes passes --route-nopull plus one --route per IPv4 CIDR in --routes-file (one per line, # comments),
plus a host route for api.ipify.org so the IP check sees the tunnel exit. The block record in ~/.mts/yt_block.json stores
the IP it was written from, so the VPN exit is not held back by the home IP record. Exit: 0/1 as the fetch, 2 refused
or setup failed, 4 IP not restored. Windows: openvpn needs admin; a non-elevated shell gets a clear message.
"""
import argparse
import ipaddress
import os
import queue
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fetch_captions_timed as ft  # noqa: E402

ROOT = HERE.parents[1]
OPENVPN = r"C:\Program Files\OpenVPN\bin\openvpn.exe"
READY = "Initialization Sequence Completed"
SHOW = (READY, "AUTH_FAILED", "TLS Error", "Options error", "fatal error", "Cannot open", "adapters on this system")
EXIT_REFUSED, EXIT_NOT_RESTORED = 2, 4
IP_HOST = "api.ipify.org"


def inside_repo(path):
    p = Path(path).resolve()
    return p == ROOT or ROOT in p.parents


def is_admin():
    if os.name == "nt":
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    return os.geteuid() == 0


def resolve_host(host):
    return sorted(set(socket.gethostbyname_ex(host)[2]))


def load_routes(path):
    """['net mask', ...] from a CIDR text file (IPv4 only; # comments and blanks skipped)."""
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        net = ipaddress.ip_network(line, strict=False)
        if net.version == 4:
            out.append(f"{net.network_address} {net.netmask}")
    return out


def build_cmd(exe, profile, routes=None):
    cmd = [exe, "--config", str(profile)]
    if routes is not None:
        cmd.append("--route-nopull")
        for r in routes:
            net, mask = r.split()
            cmd += ["--route", net, mask]
    return cmd


def wait_ready(proc, timeout):
    """True once openvpn prints the ready line; False on exit/timeout. Prints only whitelisted status lines."""
    q = queue.Queue()

    def pump():
        for line in proc.stdout:
            q.put(line)
        q.put(None)
    threading.Thread(target=pump, daemon=True).start()
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            line = q.get(timeout=0.2)
        except queue.Empty:
            continue
        if line is None:
            return False
        if any(m in line for m in SHOW):
            print("openvpn:", line.strip()[:160], flush=True)
        if READY in line:
            return True
    return False


def teardown(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)


def restored(original, tries=6, pause=5):
    for i in range(tries):
        if ft.public_ip() == original:
            return True
        if i < tries - 1:
            time.sleep(pause)
    return False


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--profile", required=True)
    ap.add_argument("--analyst", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-videos", type=int, default=5)
    ap.add_argument("--only-youtube-routes", action="store_true")
    ap.add_argument("--routes-file")
    ap.add_argument("--connect-timeout", type=int, default=60)
    ap.add_argument("--openvpn", default=OPENVPN)
    ap.add_argument("videos", nargs="+")
    a = ap.parse_args(argv)
    if inside_repo(a.profile):
        print("REFUSED: the .ovpn profile is inside the repo; keep it outside (never committed).")
        return EXIT_REFUSED
    if not Path(a.profile).is_file():
        print("REFUSED: profile file not found.")
        return EXIT_REFUSED
    routes = None
    if a.only_youtube_routes:
        if not a.routes_file:
            print("REFUSED: --only-youtube-routes needs --routes-file.")
            return EXIT_REFUSED
        routes = load_routes(a.routes_file) + [f"{ip} 255.255.255.255" for ip in resolve_host(IP_HOST)]
        print(f"split routing: {len(routes)} routes (best effort; ranges move)")
    if not is_admin():
        print("NOT ELEVATED: openvpn needs administrator rights. Re-run from an elevated (Run as administrator) shell.")
        return EXIT_REFUSED
    original = ft.public_ip()
    if not original:
        print("REFUSED: cannot read the current public IP, so a VPN change could not be verified.")
        return EXIT_REFUSED
    print(f"public IP before VPN: {original}")
    proc, result, not_restored = None, EXIT_REFUSED, False
    try:
        proc = subprocess.Popen(build_cmd(a.openvpn, a.profile, routes), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if not wait_ready(proc, a.connect_timeout):
            print("VPN did not come up in time; stopping.")
        else:
            now = ft.public_ip()
            if not now or now == original:
                print(f"VPN up but public IP did not change ({now}); stopping, nothing fetched.")
            else:
                print(f"public IP on VPN: {now}")
                result = ft.main(["--analyst", a.analyst, "--out", a.out,
                                  "--max-videos", str(min(a.max_videos, 5)), *a.videos])
    finally:
        if proc is not None:
            teardown(proc)
            if restored(original):
                print("VPN down, public IP restored.")
            else:
                not_restored = True
                print(f"WARNING WARNING: VPN torn down but public IP is NOT back to {original}. "
                      "Check the openvpn process and routes NOW.")
    return EXIT_NOT_RESTORED if not_restored else result


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
