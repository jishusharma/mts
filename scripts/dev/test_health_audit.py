import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import health_audit as H

NL = chr(10)
NUL = chr(0)


def test_b4_adoption_counts_standalone_and_folded(monkeypatch):
    log = NUL + "release a" + NL + "Result: claim a closed" + NL + NUL + "work b" + NL + "Result: claim b closed with the ship" + NL
    monkeypatch.setattr(H, "git", lambda *a, **k: log)
    assert H.b4_adoption(24) == (1, 1)


def test_bookkeeping_counts_upkeep_but_not_feature_commits(monkeypatch):
    upkeep = ["gate: register test_x", "CLAUDE.md: trim to size cap", "wavetrend: declare wiring registry entries",
              "lookahead allowlist: review imb.py window", "RELAY.md back under size cap", "CI red fix 2: pit_levels"]
    feature = ["tom study: new result", "W3: wire 6 layer sources", "q-sched-scope answered: JIS-NUC tasks unregistered",
               "stop-outcome registry of fires", "wiring of the live runner"]
    monkeypatch.setattr(H, "git", lambda *a, **k: NL.join(upkeep + feature))
    n, total, hit = H.bookkeeping(24)
    assert (n, total) == (len(upkeep), len(upkeep) + len(feature)) and sorted(hit) == sorted(upkeep)


def _runs(*concl):
    return {"workflow_runs": [{"id": i, "conclusion": c, "status": "completed", "created_at": "2026-10-17T07:36:00Z",
                               "head_sha": "abcdef012345"} for i, c in enumerate(concl)]}


def _fake(runs):
    def fake(url):
        if "/runs?" in url:
            return runs
        if url.endswith("/jobs"):
            return {"jobs": [{"id": 9, "conclusion": "failure", "steps": [{"name": "Offline gate", "conclusion": "failure"}]}]}
        return [{"annotation_level": "failure", "message": "Process completed with exit code 1."},
                {"annotation_level": "failure", "message": "1 step(s) failed: Step 3tl: Task card lint"}]
    return fake


def test_ci_survives_a_rate_limited_api(monkeypatch):
    monkeypatch.setattr(H, "fetch_json", lambda url: {"_error": "HTTP 403"})
    counts, err, latest, red = H.ci()
    assert counts is None and "403" in err and red == [] and latest == ""


def test_ci_names_the_failed_step_and_first_annotation(monkeypatch):
    monkeypatch.setattr(H, "fetch_json", _fake(_runs("failure")))
    counts, err, latest, red = H.ci()
    assert counts["failure"] == 1 and latest == "failure" and red[0][2] == ["Offline gate"] and "Step 3tl" in red[0][3]


def test_ci_latest_skips_cancelled_and_old_reds_are_history(monkeypatch):
    monkeypatch.setattr(H, "fetch_json", _fake(_runs(None, "cancelled", "success", "failure")))
    counts, err, latest, red = H.ci()
    assert latest == "success" and len(red) == 1


def _stub_everything(monkeypatch, latest):
    monkeypatch.setattr(H.TR, "report", lambda h: "last 72 h: 100 commits | overhead 40 (40%)")
    monkeypatch.setattr(H, "bookkeeping", lambda h: (1, 100, ["gate: register x"]))
    monkeypatch.setattr(H, "b4_adoption", lambda h: (1, 9))
    monkeypatch.setattr(H, "ci", lambda: (H.Counter({"success": 1}), "", latest, []))
    monkeypatch.setattr(H, "stale_claims", lambda: [])
    monkeypatch.setattr(H, "workflow_commits", lambda h: [])


def test_audit_flags_only_when_the_newest_run_is_red(monkeypatch):
    _stub_everything(monkeypatch, "success")
    text, flags = H.audit(72, fetch=False)
    assert flags == [] and "METRICS overhead=40 bookkeeping=1 b4=90 stale_claims=0 ci_latest=success" in text
    _stub_everything(monkeypatch, "failure")
    text, flags = H.audit(72, fetch=False)
    assert len(flags) == 1 and flags[0].startswith("CI RED") and "- CI RED" in text
