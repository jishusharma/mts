"""Ship train, card 3/5 (SHIP_TRAIN.md): bisect a red batch, eject failing refs, signal their author, status file for `ship --train`.

Pure logic plus thin git/signal edges, so train.yml (card 2) calls it and tests fake the edges.
  queue ref      queue/<host>/<slug>: the name is the blame record (the git author is the same on every machine).
  bisect_batch   red batch -> each ref alone, in parallel -> eject the failing ones -> re-run the rest (the ejected ones never land).
  signal_eject   mts_signal note to <host> naming the slug, the failing test id and a link.
  status file    train/<host>__<slug>.json on the mts-signals branch; `sync.py ship --train` polls it (replaces the CI wait for that ship).
CLI (for the workflow):  ship_train.py status <ref> <state> [--test ID] [--link URL]   |   ship_train.py eject <ref> --test ID --link URL
States: queued, landed, ejected. A fake or ejected ref is never auto-reverted (SHIP_TRAIN.md DECISION).
"""
import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mts_signal as S  # noqa: E402

QUEUE_PREFIX = "queue/"
STATUS_DIR = "train"
STATES = ("queued", "landed", "ejected")
WAIT_S = 1800          # OURS: ship --train gives the train 30 min (CI median 5 min, batch cap 4, red path +12 min)
POLL_S = 20
MAX_PARALLEL = 4       # SHIP_TRAIN.md batch cap


def queue_ref(branch, host=""):
    """queue/<host>/<slug> for a work branch `<host>/<slug>`; a bare branch name takes `host`."""
    b = branch.strip().strip("/")
    if b.startswith(QUEUE_PREFIX):
        return b
    if "/" not in b:
        b = f"{host or S.host()}/{b}"
    return QUEUE_PREFIX + b


def split_ref(ref):
    """(host, slug) of queue/<host>/<slug>; slug may contain '/'. ValueError when the ref has no host and slug."""
    parts = ref.strip("/").split("/", 2)
    if len(parts) < 3 or parts[0] != QUEUE_PREFIX.strip("/") or not parts[1] or not parts[2]:
        raise ValueError(f"not a queue ref: {ref!r} (want queue/<host>/<slug>)")
    return parts[1], parts[2]


def status_name(ref):
    host, slug = split_ref(ref)
    return f"{re.sub(r'[^A-Za-z0-9._-]+', '-', host)}__{re.sub(r'[^A-Za-z0-9._-]+', '-', slug)}.json"


def bisect_batch(refs, run_ref, run_batch):
    """A red batch: run every ref alone (parallel, at most MAX_PARALLEL at once), eject those that fail, re-run the rest together.
    run_ref(ref) -> (ok, test_id, link); run_batch(refs) -> bool. Returns dict(green, ejected={ref: (test_id, link)}, batch_ok).
    The remainder re-run is skipped when nothing is left; when it is still red the survivors do NOT land (batch_ok False):
    an interaction between two refs is not blamed on either (conservative, OURS)."""
    refs = list(refs)
    with ThreadPoolExecutor(max_workers=max(1, min(MAX_PARALLEL, len(refs) or 1))) as pool:
        results = list(pool.map(run_ref, refs))
    ejected = {r: (res[1], res[2]) for r, res in zip(refs, results) if not res[0]}
    green = [r for r in refs if r not in ejected]
    batch_ok = False   # nothing ejected yet the batch was red (interaction or flake): nothing lands here
    if ejected and green:
        batch_ok = bool(run_batch(green))
    return {"green": green, "ejected": ejected, "batch_ok": batch_ok}


def eject_text(ref, test_id, link):
    host, slug = split_ref(ref)
    return f"train ejected {slug}: failing test {test_id or 'unknown'}; {link or 'no link'}"


def signal_eject(ref, test_id, link, send=None):
    """mts_signal note to the host named in the ref; the slug, failing test id and link ride in the text. Returns send's result."""
    host, slug = split_ref(ref)
    send = send or S.send
    return send(eject_text(ref, test_id, link), to=host, kind="note", extra={"train_ref": ref})


def _write_status(h, ref, state, test_id="", link="", utc=None):
    d = h / STATUS_DIR
    d.mkdir(parents=True, exist_ok=True)
    rec = {"ref": ref, "state": state, "test": test_id, "link": link, "t": utc or S.stamp()}
    (d / status_name(ref)).write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8", newline="\n")
    return rec


def set_status(ref, state, test_id="", link="", cwd=None):
    """Write train/<host>__<slug>.json on mts-signals and push (retry on a lost race). True when it reached origin."""
    if state not in STATES:
        raise ValueError(f"state must be one of {STATES}")
    h = S.ensure(cwd)
    if h is None:
        return False
    for _ in range(4):
        _write_status(h, ref, state, test_id, link)
        S.git(h, "add", "-A")
        S.git(h, "commit", "-q", "-m", f"train {state} {ref}", check=False)
        if S.git(h, "push", "-q", "origin", f"HEAD:refs/heads/{S.BRANCH}", check=False).returncode == 0:
            S.mark_synced()
            return True
        S.git(h, "fetch", "-q", "origin", S.BRANCH, check=False)
        S.git(h, "reset", "-q", "--hard", "FETCH_HEAD", check=False)
    return False


def read_status(ref, cwd=None):
    """The status dict of `ref` on origin/mts-signals right now (fetches), or None."""
    h = S.ensure(cwd)
    if h is None:
        return None
    p = h / STATUS_DIR / status_name(ref)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def wait_status(ref, since=None, fetch=read_status, sleep=time.sleep, now_fn=time.monotonic, timeout=WAIT_S, poll=POLL_S, out=print):
    """Poll until the train marks `ref` landed or ejected. A status stamped before `since` (a previous run of the same slug) is ignored.
    Returns 'landed', 'ejected' or 'timeout' (the push is done; the train may still land it)."""
    end = now_fn() + timeout
    while True:
        st = fetch(ref)
        if st and st.get("state") in ("landed", "ejected") and (since is None or str(st.get("t", "")) >= since):
            if st["state"] == "ejected":
                out(f"train ejected {ref}: failing test {st.get('test') or 'unknown'}; {st.get('link') or 'no link'}")
            else:
                out(f"train landed {ref}")
            return st["state"]
        if now_fn() >= end:
            out(f"train: no verdict for {ref} after {int(timeout)} s; the push is done, the train may still land it")
            return "timeout"
        sleep(poll)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("ref")
    s.add_argument("state", choices=STATES)
    s.add_argument("--test", default="")
    s.add_argument("--link", default="")
    e = sub.add_parser("eject")
    e.add_argument("ref")
    e.add_argument("--test", default="")
    e.add_argument("--link", default="")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "status":
            ok = set_status(a.ref, a.state, a.test, a.link)
        else:
            ok = set_status(a.ref, "ejected", a.test, a.link) and signal_eject(a.ref, a.test, a.link)
    except ValueError as err:
        print(f"ship_train: {err}", file=sys.stderr)
        return 2
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
