"""ci_fail.py: why is fast-track CI red? (no gh on JIS-NUC; uses ci_watch's saved GitHub login, never prints it)

  python scripts/dev/ci_fail.py        newest run states, then for the newest failed run: failing job names and FAILED test ids

The log request goes to GitHub with the login; GitHub answers with a redirect to a storage host, which is fetched WITHOUT
the Authorization header. parse_failures() is pure (log text in, lines out) and tested offline.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_watch  # noqa: E402

HIT = re.compile(r"(^|\s)(FAILED|ERROR) |Step \S+: FAIL|\d+ failed")
STAMP = re.compile(r"^\d{4}-\d\d-\d\dT[\d:.]+Z ")


def parse_failures(log_text, limit=30):
    """Lines of a CI job log that name a failure (FAILED/ERROR test ids, 'Step X: FAIL', 'N failed'), timestamp stripped, in order, deduplicated."""
    out = []
    for ln in log_text.splitlines():
        if not HIT.search(ln):
            continue
        ln = STAMP.sub("", ln.strip())[:240]
        if ln not in out:
            out.append(ln)
        if len(out) >= limit:
            break
    return out


def run_line(r):
    return "%s %s %s %s %s" % (r["id"], r["head_sha"][:9], r["status"], r.get("conclusion"), r["created_at"])


def fetch_log(url):
    """Job log text. The authorized request must not follow the redirect itself: the redirect target gets no Authorization header."""
    import urllib.error
    import urllib.request

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + ci_watch.token(), "User-Agent": "mts-ci-fail"})
    try:
        return urllib.request.build_opener(NoRedirect).open(req, timeout=30).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code not in (301, 302, 303, 307, 308):
            raise
        with urllib.request.urlopen(urllib.request.Request(e.headers["Location"], headers={"User-Agent": "mts-ci-fail"}), timeout=60) as r:
            return r.read().decode("utf-8", "replace")


def main():
    runs = ci_watch.fetch()
    for r in runs[:6]:
        print(run_line(r))
    bad = [r for r in runs if r.get("conclusion") == "failure"][:1]
    if not bad:
        print("no failed run in the newest 30")
        return 0
    r = bad[0]
    print("=== newest failed run", r["id"], r["head_sha"][:9])
    for j in ci_watch.get_json(r["jobs_url"], timeout=20)["jobs"]:
        if j.get("conclusion") != "failure":
            continue
        print("job", j["id"], j["name"])
        hits = parse_failures(fetch_log(j["url"] + "/logs"))
        print("  %d failure line(s)" % len(hits))
        for h in hits:
            print("  " + h)
    return 1


if __name__ == "__main__":
    sys.exit(main())