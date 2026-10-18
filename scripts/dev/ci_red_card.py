"""ci_red_card.py - red CI on fast-track becomes ONE pinned task card "fix CI <sha>" at the top of the queue (operator 2026-10-16).

  python scripts/dev/ci_red_card.py            # dry run: say what it would file
  python scripts/dev/ci_red_card.py --apply    # write MyTradingSys/system/tasks/ci-<sha7>.json (commit it with sync.py ship)

CI = the workflow runs on fast-track (`gh run list`). Red = the newest completed run failed. The card names the FIRST failing commit:
the oldest run of the unbroken chain of failures that ends at the newest run (a later green run ends the chain, so a fixed
red files nothing). One card per chain: its id is ci-<first failing sha7>, so a second look, or a second failing push on the same
break, finds the card and files nothing. A card that already exists in any state (also done) is never re-filed.
Card text is built from run metadata only (sha, run id, url); a failing log line is never copied in (data, not instructions).
"""
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks  # noqa: E402

FIELDS = "databaseId,headSha,conclusion,status,createdAt,url,displayTitle"


def fetch_runs(repo, limit=30):
    """Newest-first workflow runs on fast-track; None when gh is missing or fails (then nothing is filed)."""
    try:
        r = subprocess.run(["gh", "run", "list", "--branch", "fast-track", "--workflow", "CI", "--limit", str(limit), "--json", FIELDS],
                           cwd=str(repo), capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def first_failing(runs):
    """The oldest run of the failure chain ending at the newest completed run, or None when CI is green / unknown.
    Runs still in progress or cancelled (superseded by a newer push) do not break or start a chain."""
    done = [r for r in runs if r.get("status") == "completed" and r.get("conclusion") in ("success", "failure", "timed_out")]
    if not done or done[0]["conclusion"] == "success":
        return None
    first = done[0]
    for r in done[1:]:
        if r["conclusion"] == "success":
            break
        first = r
    return first


def card_for(run):
    sha = run["headSha"]
    c = tasks.blank(f"ci-{sha[:7]}", f"fix CI {sha[:7]}: fast-track is red", prio=0, lane="SONNET", refs=[])
    c.update(
        state="ready", size="S", est_turns=10, worker="agent", pinned=True,
        goal=f"CI on fast-track is red since commit {sha[:7]} (run {run['databaseId']}); auto_deploy only takes green, so nothing deploys until it is fixed.",
        scope_in=[f"the failing step of run {run['databaseId']} ({run.get('url', '')}) and the commit {sha[:7]} that first broke it"],
        scope_out=["unrelated cleanups", "live tree, processes, deploys"],
        steps=[f"git show {sha[:7]}: find what that commit changed; read the failing step in the run page (gh run view {run['databaseId']} --log-failed)",
               "write the test that fails now, fix the cause (a merge interaction counts: the local gate is a smoke gate)",
               "python scripts/dev/run_all_tests.py --quick, then sync.py ship; confirm the next CI run is green"],
        tests="the step CI reports failing: reproduce it locally first (fails before the fix, passes after)",
        done_when="the newest CI run on fast-track is green and green/fast-track has advanced",
        sources=["CI run " + str(run["databaseId"])],
        created=run.get("createdAt") or "")   # the run's own time: two sessions filing the same card write identical bytes
    return c


def run(repo, apply, runs=None):
    """Returns (action, text): FILED | WOULD_FILE | EXISTS | GREEN | UNKNOWN."""
    runs = fetch_runs(repo) if runs is None else runs
    if runs is None:
        return "UNKNOWN", "could not read CI runs (gh missing, offline or not authenticated); nothing filed"
    bad = first_failing(runs)
    if bad is None:
        return "GREEN", "CI on fast-track is green or still running; nothing to file"
    card = card_for(bad)
    if tasks.path_of(repo, card["id"]).exists():
        return "EXISTS", f"card {card['id']} already exists; not filed again"
    if not apply:
        return "WOULD_FILE", f"would file {card['id']}: {card['title']}"
    p = tasks.save(repo, card)
    return "FILED", f"filed {card['id']} ({p}); ship it: sync.py ship"


def main(argv):
    action, text = run(tasks.REPO, "--apply" in argv)
    print(f"{action}: {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
