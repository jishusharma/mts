import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))

import dsa_eval  # noqa: E402
from dsa_eval_scenarios import SCENARIOS  # noqa: E402


def test_ids_unique_and_fields_present():
    ids = [s["id"] for s in SCENARIOS]
    assert len(ids) == len(set(ids)) >= 10
    for s in SCENARIOS:
        assert s["source"] and s["message"] and s["must"] is not None and s["good"] and s["bad"]


def test_every_good_fixture_passes():
    for s in SCENARIOS:
        ok, fails = dsa_eval.score_reply(s, s["good"])
        assert ok, (s["id"], fails)


def test_every_bad_fixture_fails():
    # a check that cannot fail is not a gate
    for s in SCENARIOS:
        ok, _ = dsa_eval.score_reply(s, s["bad"])
        assert not ok, s["id"]


def test_empty_reply_fails_and_block_cap_enforced():
    s9 = next(s for s in SCENARIOS if s["id"] == "S09-no-paste-request")
    assert dsa_eval.score_reply(s9, "")[0] is False
    two = s9["good"] + "\n" + s9["good"]
    ok, fails = dsa_eval.score_reply(s9, two)
    assert not ok and any(f.startswith("blocks") for f in fails)


def test_score_all_reports_missing_replies_as_fail():
    rows = dsa_eval.score_all({})
    assert len(rows) == len(SCENARIOS) and not any(r["pass"] for r in rows)
