"""Single-instance lease for singleton roles (Pipeliner, Traffic_Controller), across machines and on one machine.
Design and the 2026-10-18 double-run evidence: MyTradingSys/system/TRAFFIC_CONTROLLER.md, section "Part A".

  python scripts/dev/lease.py acquire <Role>    take or renew the lease (exit 0 = you hold it)
  python scripts/dev/lease.py renew <Role>      heartbeat; also done by every guarded write when < RENEW_BELOW is left
  python scripts/dev/lease.py release <Role>    give it up (only the holder can)
  python scripts/dev/lease.py status [<Role>] [--json]   who holds what on origin/fast-track (read-only)
  python scripts/dev/lease.py guard             exit 0 unless this session is a singleton role without a valid lease

Exit codes: 0 ok; 3 REFUSED (another live holder, a lost race, or a same-host duplicate); 4 UNREACHABLE/AMBIGUOUS
(fetch or push failed, or the lease file is unreadable): fail closed, never run optimistically.

How it works. The only medium all machines share is git trunk, so the lease is one JSON file per role on
origin/fast-track (MyTradingSys/system/leases/<role>.json). Acquire = compare-and-swap: read the lease at origin's tip T,
decide (free / expired / mine -> take; another live holder -> refuse), build ONE commit with parent T that rewrites only
that file (git plumbing in a private index, the same path `sync.py claim` uses: no merge, no gate, no worktree change), and
push it as a plain fast-forward. The server accepts it only while fast-track still points at T, so of two racing
acquirers exactly one push lands; the loser's push is rejected (non-fast-forward), it re-reads the fresh state and sees
the winner. No force-push, no rebase. A push that fails for any other reason is ambiguous: re-fetch and look for our
own nonce; if the fetch fails too -> exit 4.
Liveness: the holder writes `expires` = now + TTL; every guarded write renews when less than RENEW_BELOW remains. Another
instance may take over only after expires + SKEW (machine clocks may differ by minutes); the holder itself stops trusting
its lease at expires - SKEW. A same-machine duplicate is refused first by a local lock (~/.claude/mts-leases/<role>.json,
updated under an O_EXCL mutex), without the network.
Identity: host + a hash of CLAUDE_CODE_SESSION_ID (or MTS_LEASE_SESSION for non-Claude runners); never the raw id
(the repo is public). Which role a session plays: MTS_ROLE, else the role_loader hook's record for the session, else
the marker `acquire` writes locally.
"""
import hashlib
import json
import os
import random
import re
import socket
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TRUNK = "fast-track"
LEASE_DIR = "MyTradingSys/system/leases"
SINGLETONS = ("Pipeliner", "Traffic_Controller")
TTL = 45 * 60            # a lease lives 45 min after the last write; OURS: one Pipeliner opening is 20-40 min (ROLES.md)
RENEW_BELOW = 25 * 60    # guarded writes renew when less than this remains (so at most ~1 renew commit per 20 min)
SKEW = 5 * 60            # clock-difference allowance between machines, both sides
MIN_FOR_SHIP = 20 * 60   # a ship needs this much lease left at its start: the clean gate is 544 s (GATE_SPEED.md)
CAS_TRIES = 4
MUTEX_STALE = 600        # seconds after which a leftover local mutex file is broken (> a full CAS loop: 4 x (45 s fetch + 60 s push))
OK, REFUSED, UNREACHABLE = 0, 3, 4


class LeaseError(Exception):
    code = UNREACHABLE


class Refused(LeaseError):
    code = REFUSED


class Unreachable(LeaseError):
    code = UNREACHABLE


def _flags():
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def git(repo, *args, env=None, stdin=None, timeout=60):
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, input=stdin,
                              timeout=timeout, creationflags=_flags(), encoding="utf-8", errors="replace")
    except (subprocess.TimeoutExpired, OSError) as e:
        return subprocess.CompletedProcess(args, 124, "", f"{type(e).__name__}: {e}")


def slug(role):
    if not role:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", role.lower()).strip("_")


def rel_path(role):
    return f"{LEASE_DIR}/{slug(role)}.json"


def canon(role):
    if not role:
        raise LeaseError(f"{role!r} is not a singleton role ({', '.join(SINGLETONS)})")
    for r in SINGLETONS:
        if slug(r) == slug(role):
            return r
    raise LeaseError(f"{role!r} is not a singleton role ({', '.join(SINGLETONS)})")


# ---------- identity ----------
_LOCAL = threading.local()   # tests: per-thread identity (two "machines" racing in one process)


def _env(name):
    over = getattr(_LOCAL, "env", None)
    return over.get(name) if over is not None else os.environ.get(name)


def host():
    return (_env("MTS_LEASE_HOST") or socket.gethostname()).upper()


def session_key():
    raw = _env("MTS_LEASE_SESSION") or _env("CLAUDE_CODE_SESSION_ID") or ""
    if not raw:
        return ""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def me():
    """Who is asking. Without a session id the identity is the host alone: two such runners on one host are one
    identity, which is why non-Claude runners must set MTS_LEASE_SESSION (TRAFFIC_CONTROLLER.md)."""
    s = session_key() or "nosession"
    acct = _env("MTS_ACCOUNT") or "?"
    acct = "?" if "@" in acct else (re.sub(r"[^A-Za-z0-9_-]", "", acct)[:32] or "?")   # public repo: a short label, never an email
    return {"host": host(), "account": acct, "session": s, "key": f"{host()}/{s}"}


def home():
    return Path(_env("MTS_LEASE_HOME") or Path.home() / ".claude" / "mts-leases")


# ---------- which role is this session ----------
def role_name(role):
    """Exact singleton name for any spelling (pipeliner, traffic controller); other names unchanged, never raises."""
    if not isinstance(role, str):
        return role
    try:
        return canon(role)
    except LeaseError:
        return role


def current_role(env=None):
    env = os.environ if env is None else env
    if env.get("MTS_ROLE"):
        return role_name(env["MTS_ROLE"])
    sid = env.get("CLAUDE_CODE_SESSION_ID")
    if sid:
        try:
            import role_loader
            roles = [role_name(r) for r in role_loader.injected(sid)]
            single = [r for r in roles if r in SINGLETONS]
            if single or roles:
                return single[-1] if single else roles[-1]   # a later mention of another role never hides a singleton
        except Exception:
            pass
    try:
        d = json.loads((home() / "roles" / f"{me()['key'].replace('/', '_')}.json").read_text(encoding="utf-8"))
        return role_name(d.get("role"))
    except Exception:
        return None


def _mark_role(role):
    p = home() / "roles" / f"{me()['key'].replace('/', '_')}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"role": role, "at": int(time.time())}))


# ---------- local lock (same machine) ----------
@contextmanager
def local_mutex(role):
    d = home()
    d.mkdir(parents=True, exist_ok=True)
    m = d / f"{slug(role)}.mutex"
    t0 = time.time()
    while True:
        try:
            fd = os.open(str(m), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - m.stat().st_mtime > MUTEX_STALE:
                    m.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.time() - t0 > 30:
                raise Refused(f"local lease mutex {m} busy for 30 s (another acquire on this machine)")
            time.sleep(0.2 + random.random() * 0.3)
    try:
        yield
    finally:
        try:
            m.unlink()
        except FileNotFoundError:
            pass


def local_state(role):
    try:
        return json.loads((home() / f"{slug(role)}.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def write_local(role, state):
    p = home() / f"{slug(role)}.json"
    if state is None:
        p.unlink(missing_ok=True)
        return
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(state, indent=1, sort_keys=True))
    os.replace(tmp, p)


def check_local(role, now):
    """A live local holder that is not me = same-host duplicate (refused without the network)."""
    st = local_state(role)
    if st and st.get("holder", {}).get("key") != me()["key"] and st.get("state") == "held" \
            and now < float(st.get("expires", 0)) + SKEW:
        h = st["holder"]
        raise Refused(f"{role}: same-host duplicate: session {h.get('session')} on {h.get('host')} holds the local lock until "
                      f"{iso(float(st['expires']))} (+{SKEW // 60} min skew)")


# ---------- trunk state ----------
def iso(epoch):
    return datetime.fromtimestamp(float(epoch), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(repo):
    r = git(repo, "fetch", "--quiet", "origin", TRUNK, timeout=45)
    if r.returncode != 0:
        raise Unreachable(f"fetch origin {TRUNK} failed (lease state unreachable, refusing): {r.stderr.strip()[:200]}")


def read_trunk(repo, role, ref=None):
    """(tip sha, lease dict or None). Raises Unreachable when the ref or the file cannot be read cleanly."""
    ref = ref or f"origin/{TRUNK}"
    tip = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if tip.returncode != 0 or not tip.stdout.strip():
        raise Unreachable(f"cannot resolve {ref}")
    tip = tip.stdout.strip()
    rel = rel_path(role)
    ls = git(repo, "ls-tree", tip, rel)
    if ls.returncode != 0:
        raise Unreachable(f"ls-tree {rel} failed: {ls.stderr.strip()[:200]}")
    if not ls.stdout.strip():
        return tip, None
    show = git(repo, "show", f"{tip}:{rel}")
    try:
        d = json.loads(show.stdout)
        if show.returncode != 0 or not isinstance(d, dict) or d.get("state") not in ("held", "released"):
            raise ValueError("bad shape")
        if d["state"] == "held" and (float(d.get("expires") or 0) <= 0 or not isinstance(d.get("holder"), dict)
                                     or not d["holder"].get("key")):
            raise ValueError("held without expiry or holder")
    except (ValueError, TypeError):
        raise Unreachable(f"lease file {rel} at {tip[:8]} is unreadable: ambiguous state, refusing")
    return tip, d


def classify(d, now, key):
    """free | mine | held | expired (from the asker's side, with the skew allowance)."""
    if d is None or d.get("state") == "released":
        return "free"
    if d.get("holder", {}).get("key") == key:
        return "mine"
    if now < float(d["expires"]) + SKEW:
        return "held"
    return "expired"


def describe(d, now=None):
    now = time.time() if now is None else now
    if not d:
        return "free (never taken)"
    h = d.get("holder", {})
    who = f"{h.get('host', '?')}/{h.get('account', '?')} session {h.get('session', '?')}"
    if d.get("state") == "released":
        return f"free (released by {who} at {iso(d.get('renewed', 0))})"
    left = float(d["expires"]) - now
    tail = f"expires {iso(d['expires'])} ({left / 60:+.0f} min)" if left > -SKEW else f"EXPIRED {iso(d['expires'])}, takeover allowed"
    return f"held by {who}, {tail}"


def _commit(repo, parent, rel, text, msg):
    gitdir = git(repo, "rev-parse", "--absolute-git-dir").stdout.strip()
    idx = Path(gitdir) / f"lease-index-{os.getpid()}-{random.randrange(1 << 30)}"
    env = {**os.environ, "GIT_INDEX_FILE": str(idx)}

    def plumb(*args, stdin=None):
        r = git(repo, *args, env=env, stdin=stdin)
        if r.returncode != 0:
            raise Unreachable(f"git {args[0]} failed: {r.stderr.strip()[:200]}")
        return r.stdout.strip()
    try:
        plumb("read-tree", parent)
        blob = plumb("hash-object", "-w", "--stdin", stdin=text)
        plumb("update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}")
        return plumb("commit-tree", plumb("write-tree"), "-p", parent, "-m", msg)
    finally:
        idx.unlink(missing_ok=True)


REJECT_RE = re.compile(r"\[rejected\]|non-fast-forward|fetch first|\(stale info\)|cannot lock ref|failed to update ref", re.I)


def push(repo, commit):
    """'ok' | 'rejected' (someone moved trunk first: we lost this round) | 'error' (unknown: maybe landed)."""
    r = git(repo, "push", "--quiet", "--porcelain", "origin", f"{commit}:refs/heads/{TRUNK}", timeout=60)
    if r.returncode == 0:
        return "ok"
    return "rejected" if REJECT_RE.search(r.stdout + r.stderr) else "error"


def _write(repo, role, new, verb, now_fn, hooks):
    """CAS loop: decide on fresh state each round; only a fast-forward of the exact tip we read lands."""
    rel = rel_path(role)
    if not session_key():
        raise Unreachable(f"{role}: no session id (CLAUDE_CODE_SESSION_ID or MTS_LEASE_SESSION); two such runners on one "
                          "host would share one identity, refusing")
    key = me()["key"]
    for attempt in range(1, CAS_TRIES + 1):
        fetch(repo)
        tip, cur = read_trunk(repo, role)
        now = now_fn()
        kind = classify(cur, now, key)
        body = new(cur, kind, now)          # raises Refused when this verb may not proceed
        if body is None:
            return cur
        body = {**body, "write_id": os.urandom(6).hex()}   # fresh per write: proves THIS write landed after a push error
        text = json.dumps(body, indent=1, sort_keys=True) + "\n"
        msg = (f"lease {slug(role)}: {verb} by {key}\n\nResult: {role} lease {verb} by {body['holder']['host']}/"
               f"{body['holder']['account']} until {iso(body['expires'])}")
        commit = _commit(repo, tip, rel, text, msg)
        if hooks.get("before_push"):
            hooks["before_push"](attempt)
        res = push(repo, commit)
        if res == "ok":
            return body
        if res == "error":
            fetch(repo)                     # Unreachable here = exit 4: we cannot tell whether we hold it
            _, after = read_trunk(repo, role)
            if after and after.get("write_id") == body["write_id"]:
                return body
        time.sleep(0.3 + random.random())   # rejected: someone else moved trunk; re-decide on the fresh state
    raise Unreachable(f"{role}: lease push still not accepted after {CAS_TRIES} rounds (busy trunk); refusing")


def acquire(repo, role, now_fn=time.time, hooks=None):
    role = canon(role)
    ident = me()

    def new(cur, kind, now):
        if kind == "held":
            raise Refused(f"{role}: {describe(cur, now)}. Do not run a second {role}.")
        prev = cur if kind in ("expired", "mine") else None
        acquired = float(cur["acquired"]) if (kind == "mine" and cur and cur.get("state") == "held") else now
        return {"role": role, "state": "held", "holder": {k: ident[k] for k in ("host", "account", "session", "key")},
                "nonce": cur["nonce"] if kind == "mine" and cur.get("state") == "held" else os.urandom(8).hex(),
                "acquired": int(acquired), "renewed": int(now), "expires": int(now + TTL), "ttl": TTL,
                "took_over_from": (prev or {}).get("holder", {}).get("key") if kind == "expired" else None}
    with local_mutex(role):
        check_local(role, now_fn())
        body = _write(repo, role, new, "acquire", now_fn, hooks or {})
        write_local(role, body)
    _mark_role(role)
    return body


def renew(repo, role, now_fn=time.time, hooks=None):
    """Heartbeat. The holder may also re-take its own expired lease if nobody took it over (same as acquire)."""
    role = canon(role)
    ident = me()

    def new(cur, kind, now):
        if kind != "mine":   # held/expired by another = LOST; free/released = nothing to renew
            raise Refused(f"{role}: not renewable, {describe(cur, now)}. Stop: run acquire only if no other {role} runs.")
        return {**cur, "holder": {k: ident[k] for k in ("host", "account", "session", "key")},
                "renewed": int(now), "expires": int(now + TTL), "ttl": TTL}
    with local_mutex(role):
        body = _write(repo, role, new, "renew", now_fn, hooks or {})
        write_local(role, body)
    return body


def release(repo, role, now_fn=time.time):
    role = canon(role)

    def new(cur, kind, now):
        if kind in ("held", "expired"):
            raise Refused(f"{role}: not ours to release, {describe(cur, now)}")
        if kind != "mine" or cur.get("state") != "held":
            return None                     # free or already released: nothing to do
        return {**cur, "state": "released", "renewed": int(now), "expires": int(now)}
    with local_mutex(role):
        body = _write(repo, role, new, "release", now_fn, {})
        st = local_state(role)
        if st and st.get("holder", {}).get("key") == me()["key"]:
            write_local(role, None)
    return body


def require(repo, role, min_remaining=0, now_fn=time.time):
    """Fail-closed check before a write on the role's behalf: fresh trunk state must name this session as holder with
    at least max(min_remaining, SKEW) left; renews when less than RENEW_BELOW is left."""
    role = canon(role)
    if not session_key():
        raise Unreachable(f"{role}: no session id, cannot prove this session holds the lease; refusing")
    fetch(repo)
    _, cur = read_trunk(repo, role)
    now = now_fn()
    kind = classify(cur, now, me()["key"])
    if kind != "mine" or cur.get("state") != "held":
        raise Refused(f"{role}: this session does not hold the lease ({describe(cur, now)}). "
                      f"Run `python scripts/dev/lease.py acquire {role}` first; refused.")
    left = float(cur["expires"]) - now
    if left < max(RENEW_BELOW, min_remaining + SKEW):
        cur = renew(repo, role, now_fn)
    return cur


def guard(repo, min_remaining=0, env=None):
    """For CLI entry points that write: a singleton-role session must hold its lease. Other sessions pass.
    Under pytest the guard is off unless MTS_LEASE_TEST_FORCE=1 (the gate runs suites inside role sessions)."""
    env = os.environ if env is None else env
    if env.get("PYTEST_CURRENT_TEST") and not env.get("MTS_LEASE_TEST_FORCE"):
        return None
    role = role_name(current_role(env))
    if not role or role not in SINGLETONS:
        return None
    return require(repo, role, min_remaining)


def status(repo, roles=SINGLETONS, do_fetch=True):
    """{role: {...}} read-only; 'error' set when the state cannot be read."""
    out = {}
    fetched = True
    if do_fetch:
        try:
            fetch(repo)
        except LeaseError:
            fetched = False
    for role in roles:
        try:
            tip, d = read_trunk(repo, role)
            out[role] = {"trunk": tip[:12], "lease": d, "text": describe(d), "fetched": fetched,
                         "state": classify(d, time.time(), me()["key"])}
        except LeaseError as e:
            out[role] = {"error": str(e), "fetched": fetched, "state": "unknown"}
    return out


def banner_text(repo, role):
    """One short phrase for the role_loader banner, from the local origin ref (the hook already fetched)."""
    try:
        _, d = read_trunk(repo, canon(role))
        return "lease " + describe(d)
    except LeaseError as e:
        return f"lease UNKNOWN ({e})"


def toplevel():
    r = git(".", "rev-parse", "--show-toplevel")
    if r.returncode != 0:
        raise LeaseError("not inside a git checkout")
    return Path(r.stdout.strip())


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    try:
        repo = toplevel()
        if cmd == "status":
            roles = [canon(r) for r in rest if not r.startswith("--")] or list(SINGLETONS)
            res = status(repo, roles)
            if "--json" in rest:
                print(json.dumps(res, indent=1, sort_keys=True))
            else:
                for r, v in res.items():
                    print(f"{r}: {v.get('text') or v.get('error')}" + ("" if v.get("fetched") else " [fetch FAILED: local ref]"))
            return OK if all("error" not in v for v in res.values()) else UNREACHABLE
        if cmd == "guard":
            got = guard(repo)
            print(f"lease ok: {describe(got)}" if got else "lease guard: not a singleton-role session")
            return OK
        if cmd in ("acquire", "renew", "release") and rest:
            body = {"acquire": acquire, "renew": renew, "release": release}[cmd](repo, rest[0])
            print(f"{canon(rest[0])}: {cmd} ok, " + describe(body))
            return OK
    except LeaseError as e:
        print(f"LEASE {'REFUSED' if e.code == REFUSED else 'UNREACHABLE'}: {e}", file=sys.stderr)
        return e.code
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
