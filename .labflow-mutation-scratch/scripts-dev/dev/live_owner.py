"""One-owner guard for the live testnet loop (DEVICES.md section 3).

The loop runs on exactly ONE host. Marker = {host, utc heartbeat} in
<owner dir>/live_owner.json. Owner dir: env MTS_LIVE_OWNER_DIR (a share both hosts
can read) else runtime_data/ (single-host mode). Host: env MTS_HOST else hostname.

check(): refuse (exit 1) when another host's heartbeat is younger than STALE_SEC,
or the marker / owner dir cannot be read or parsed (fail closed). A missing marker in a
readable dir means no owner: allow. Same host always allowed (restart).
claim(): refresh own heartbeat; refuses to overwrite a fresh peer. release(): drop own marker.
CLI: live_owner.py check|claim|release  (exit 0 ok, 1 refuse).
"""
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hosts  # noqa: E402

STALE_SEC = 180  # OURS: supervisor tick is 30 s; 6 missed ticks = dead
ROOT = Path(__file__).resolve().parents[2]


def host():
    return (os.environ.get("MTS_HOST") or socket.gethostname()).lower()


def _same(a, b):
    """JIS-NB and JIS-DESKTOP are one machine (hosts.py): an owner file written under the old name still matches."""
    return hosts.same_host(a, b) or str(a).lower() == str(b).lower()


def marker_path(owner_dir=None):
    d = owner_dir or os.environ.get("MTS_LIVE_OWNER_DIR") or str(ROOT / "runtime_data")
    return Path(d) / "live_owner.json"


def _now():
    return datetime.now(timezone.utc)


def _read(path):
    """-> (marker|None, error|None). Missing file in a readable dir = (None, None)."""
    try:
        if not path.parent.is_dir():
            return None, f"owner dir not reachable: {path.parent}"
        if not path.exists():
            return None, None
        m = json.loads(path.read_text(encoding="utf-8"))
        hb = datetime.fromisoformat(m["heartbeat"])
        if hb.tzinfo is None:
            return None, "heartbeat has no timezone"
        return {"host": str(m["host"]).lower(), "heartbeat": hb}, None
    except Exception as e:  # unreadable, corrupt, IO error: fail closed
        return None, f"marker unreadable: {e!r}"


def check(owner_dir=None, me=None, now=None, stale_sec=STALE_SEC):
    """-> (ok, message)."""
    me = (me or host()).lower()
    m, err = _read(marker_path(owner_dir))
    if err:
        return False, f"REFUSE: {err} (fail closed)"
    if m is None or _same(m["host"], me):
        return True, "ok: no other owner"
    age = ((now or _now()) - m["heartbeat"]).total_seconds()
    if age < stale_sec:
        return False, f"REFUSE: live loop owned by {m['host']}, heartbeat {int(age)}s ago (<{stale_sec}s)"
    return True, f"ok: owner {m['host']} stale ({int(age)}s)"


def claim(owner_dir=None, me=None, now=None, stale_sec=STALE_SEC):
    me = (me or host()).lower()
    ok, msg = check(owner_dir, me, now, stale_sec)
    if not ok:
        return False, msg
    p = marker_path(owner_dir)
    try:
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(json.dumps({"host": me, "heartbeat": (now or _now()).isoformat()}),
                       encoding="utf-8", newline="\n")
        os.replace(tmp, p)
    except Exception as e:
        return False, f"REFUSE: cannot write marker: {e!r} (fail closed)"
    return True, f"claimed by {me}"


def release(owner_dir=None, me=None):
    """Remove the marker only if it is ours."""
    me = (me or host()).lower()
    p = marker_path(owner_dir)
    m, err = _read(p)
    if m is not None and _same(m["host"], me):
        try:
            p.unlink()
        except FileNotFoundError:
            pass
        return True, "released"
    return True, "nothing of ours to release"


if __name__ == "__main__":
    verb = sys.argv[1] if len(sys.argv) > 1 else "check"
    fn = {"check": check, "claim": claim, "release": release}.get(verb)
    if not fn:
        print("usage: live_owner.py check|claim|release")
        sys.exit(2)
    ok, msg = fn()
    print(msg)
    sys.exit(0 if ok else 1)
