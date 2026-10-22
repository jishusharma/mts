"""CI watch: one line in every session's context when fast-track CI is red (operator 2026-10-18).

Why it exists: the STATUS.md `CI green:` line judges CI from the age of the oldest commit not yet on origin/green/fast-track.
Green is flaky-intermittent (13 success / 7 failure in 30 runs on 2026-10-17), so the green ref kept moving and the line read
"CI running" through five red runs in a row. Coordinators read STATUS once at boot, so nobody saw it. This hook reads the
real run conclusions from the public API (no login, no `gh`: JIS-NUC has none) and speaks on every operator turn.

Claude Code hook (project .claude/settings.json): SessionStart and UserPromptSubmit print one line when the newest finished
runs failed MIN_STREAK times in a row (cancelled runs are coalescing, not results, and are skipped). Silent when green,
offline or rate limited. Cached CACHE_MIN minutes, so it costs at most 12 API calls an hour. Never raises, never blocks.

  python scripts/dev/ci_watch.py        print the line now (exit 1 when red), ignoring the cache
Env: MTS_CI_WATCH=off disables; MTS_CI_WATCH_HOME (cache dir).
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com/repos/jishusharma/mts/actions/workflows/ci.yml/runs?branch=fast-track&per_page=30"
MIN_STREAK = 2
CACHE_MIN = 5


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def streak(runs):
    """(failed_in_a_row, newest_failed_run, last_success_run) from runs newest first; cancelled and unfinished runs are skipped."""
    finished = [r for r in runs if r.get("conclusion") in ("success", "failure", "timed_out", "startup_failure")]
    n = 0
    for r in finished:
        if r["conclusion"] == "success":
            break
        n += 1
    ok = next((r for r in finished if r["conclusion"] == "success"), None)
    return n, (finished[0] if n else None), ok


def message(runs, now=None):
    n, bad, ok = streak(runs)
    if n < MIN_STREAK:
        return ""
    now = now or datetime.now(timezone.utc)
    since = f"last green {(now - parse(ok['created_at'])).total_seconds() / 3600:.1f} h ago ({ok['head_sha'][:8]})" if ok else "no green run in the last 30"
    return (f"CI RED: the newest {n} finished fast-track runs failed in a row (newest {bad['head_sha'][:8]}); {since}. "
            f"Nothing deploys while red. Fix CI first (CLAUDE.md boot step 2): `python scripts/dev/health_audit.py` names the failing steps.")


def home():
    return Path(os.environ.get("MTS_CI_WATCH_HOME") or Path.home() / ".claude")


def fetch():
    import urllib.request   # lazy: ~0.47 s of import time that a cache hit never needs
    req = urllib.request.Request(API, headers={"User-Agent": "mts-ci-watch"})
    with urllib.request.urlopen(req, timeout=4) as r:
        return json.load(r)["workflow_runs"]


def current(use_cache=True):
    cache = home() / "mts-ci-watch.json"
    if use_cache:
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            if time.time() - c["at"] < CACHE_MIN * 60:
                return c["runs"] or []
        except (OSError, ValueError, KeyError):
            pass
    try:
        runs = [{k: r.get(k) for k in ("conclusion", "head_sha", "created_at")} for r in fetch()]
        err = None
    except Exception as e:      # offline / rate limited: remember it for the TTL so each prompt does not wait on the network
        runs, err = None, e
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"at": time.time(), "runs": runs}), encoding="utf-8", newline=chr(10))
    except OSError:
        pass
    if err is not None:
        raise err
    return runs


def hook():
    if os.environ.get("MTS_CI_WATCH", "").lower() == "off":
        return 0
    try:
        try:
            if not sys.stdin.isatty():
                sys.stdin.buffer.read()     # drain the hook payload; its content is not needed
        except (OSError, ValueError, AttributeError):
            pass
        text = message(current())
        if text:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print(text)
    except Exception:
        pass    # offline, rate limited, bad JSON: a watcher must never break a prompt
    return 0


def main(argv):
    if argv and argv[0] == "hook":
        return hook()
    text = message(current(use_cache=False))
    print(text or "CI ok: fewer than %d failed runs in a row" % MIN_STREAK)
    return 1 if text else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
