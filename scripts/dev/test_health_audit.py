import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import health_audit as H

NL = chr(10)
NUL = chr(0)


def test_b4_adoption_counts_standalone_and_folded(monkeypatch):
    log = NUL + "release a" + NL + "Result: claim a closed" + NL + NUL + "work b" + NL + "Result: claim b closed with the ship" + NL
    monkeypatch.setattr(H, "git", lambda *a: log)
    assert H.b4_adoption(24) == (1, 1)


def test_bookkeeping_counts_registry_and_cap_subjects(monkeypatch):
    subs = NL.join(["gate: register test_x", "CLAUDE.md: trim to size cap", "tom study: new result", "wiring registry: drop entry"])
    monkeypatch.setattr(H, "git", lambda *a: subs)
    n, total, hit = H.bookkeeping(24)
    assert (n, total) == (3, 4) and "tom study: new result" not in hit


def test_ci_survives_a_rate_limited_api(monkeypatch):
    monkeypatch.setattr(H, "fetch_json", lambda url: {"_error": "HTTP 403"})
    counts, err, red = H.ci()
    assert counts is None and "403" in err and red == []


def test_ci_names_the_failed_step_and_first_annotation(monkeypatch):
    def fake(url):
        if "/runs?" in url:
            return {"workflow_runs": [{"id": 1, "conclusion": "failure", "status": "completed", "created_at": "2026-10-17T07:36:00Z",
                                       "head_sha": "abcdef012345"}]}
        if url.endswith("/jobs"):
            return {"jobs": [{"id": 9, "conclusion": "failure", "steps": [{"name": "Offline gate", "conclusion": "failure"}]}]}
        return [{"annotation_level": "failure", "message": "Process completed with exit code 1."},
                {"annotation_level": "failure", "message": "1 step(s) failed: Step 3tl: Task card lint"}]
    monkeypatch.setattr(H, "fetch_json", fake)
    counts, err, red = H.ci()
    assert counts["failure"] == 1 and red[0][2] == ["Offline gate"] and "Step 3tl" in red[0][3]
