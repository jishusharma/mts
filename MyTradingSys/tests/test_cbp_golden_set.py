"""CBP golden set: hand-made cases (transcript, stub extractor output, expected outcome) through cbp_run.run_once.

A change to the quote gate, expiry or dedupe fails one parametrized test. Synthetic fixtures only (golden_cbp/cases.json);
no real channel content. The mutation test proves the harness goes red when the quote check is switched off.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys"))
sys.path.insert(0, str(ROOT / "scripts" / "dev"))

import cbp  # noqa: E402
import cbp_run  # noqa: E402

DATA = json.loads((Path(__file__).parent / "golden_cbp" / "cases.json").read_text(encoding="utf-8"))
NOW = datetime.fromisoformat(DATA["now"].replace("Z", "+00:00"))
CASES = DATA["cases"]
QUOTE_CASES = [c["id"] for c in CASES if c["expect"].get("reason", "").startswith("quote not in")]


def run_case(case, tmp_path, monkeypatch):
    """Run one case; return a list of mismatches against its expectation (empty = pass)."""
    tr = tmp_path / "tr"
    tr.mkdir(parents=True)
    if case.get("transcript"):
        (tr / (case["video_id"] + "_timed.txt")).write_text(
            "# Video ID: %s\n# Title: fixture\n# Published: %s\n# Analyst: %s\n# ---\n%s"
            % (case["video_id"], case["published"], case["analyst"], case["transcript"]), encoding="utf-8")
    monkeypatch.setattr(cbp_run, "TRANSCRIPTS", tr)
    st = tmp_path / "s.json"
    if case.get("seed_rows"):
        cbp.save({"rows": case["seed_rows"]}, st)
    if case.get("seed_verdict"):  # known video: row and verdict both on file, so no second LLM pass
        st.with_name("verdicts.json").write_text(json.dumps(
            {case["video_id"]: {"analyst": case["analyst"], "published": case["published"]}}), encoding="utf-8")
    calls = []

    def extract(video, body):
        calls.append(video[0])
        return case["extract"]

    exp = case["expect"]
    got = cbp_run.run_once(NOW, fetch=lambda *a: None, extract=extract, store=st)
    bad = []
    if list(got) != exp["counts"]:
        bad.append("counts %s != %s" % (list(got), exp["counts"]))
    data = cbp.load(st)
    if "stored" in exp and [r["video_id"] for r in data["rows"]] != exp["stored"]:
        bad.append("stored %s != %s" % ([r["video_id"] for r in data["rows"]], exp["stored"]))
    if "stored_quotes" in exp and len(data["rows"][0]["quotes"]) != exp["stored_quotes"]:
        bad.append("stored quotes %d != %d" % (len(data["rows"][0]["quotes"]), exp["stored_quotes"]))
    if "reason" in exp:
        reasons = [x[2] for x in data["rejected"]]
        if not (len(reasons) == 1 and exp["reason"] in reasons[0]):
            bad.append("rejected %s lacks %r" % (reasons, exp["reason"]))
    elif data["rejected"]:
        bad.append("unexpected rejection %s" % data["rejected"])
    if "query" in exp:
        ids = [r["video_id"] for r in cbp.query(store=st, now=NOW)]
        if ids != exp["query"]:
            bad.append("query %s != %s" % (ids, exp["query"]))
    if "tradable" in exp and any(cbp.is_tradable(r) for r in data["rows"]) != exp["tradable"]:
        bad.append("tradable != %s" % exp["tradable"])
    if "extract_calls" in exp and len(calls) != exp["extract_calls"]:
        bad.append("extract calls %d != %d" % (len(calls), exp["extract_calls"]))
    return bad


def test_golden_set_covers_the_d5_failures():
    ids = {c["id"] for c in CASES}
    assert len(CASES) >= 10 and len(ids) == len(CASES)
    assert {"fabricated_quote", "wrong_direction", "missing_expires_at", "duplicate_video_id"} <= ids


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_golden_case(case, tmp_path, monkeypatch):
    assert run_case(case, tmp_path, monkeypatch) == []


def test_mutation_quote_check_off_turns_harness_red(tmp_path, monkeypatch):
    """Fail-first proof: with the quote check disabled, every quote-rejection case must go red."""
    assert QUOTE_CASES
    monkeypatch.setattr(cbp_run.vq, "first_missing", lambda *a, **k: None)
    red = [c["id"] for c in CASES if c["id"] in QUOTE_CASES
           and run_case(c, tmp_path / c["id"], monkeypatch) != []]
    assert red == QUOTE_CASES
