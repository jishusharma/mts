"""Reusable lab flows: ordered lenses, evidence gates and economical context."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks
import lab_flow as F
import codex_run as R
import codex_pack as P


def spec():
    return {"id": "pilot", "recipe": "critical-audit", "goal": "Check the source contract",
            "criteria": ["Every claim has file evidence", "Missing data is explicit"],
            "scope_in": ["source.md"]}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(tasks, "REPO", tmp_path)
    (tmp_path / "source.md").write_text("original source", encoding="utf-8")
    ledger = tmp_path / tasks.TRIALS
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("| date | card | command | data | result |\n|---|---|---|---|---|\n", encoding="utf-8")
    return tmp_path


def complete(repo, card, verdict="PASS"):
    p = repo / tasks.LAB_REPORTS / (card["id"] + ".md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"Report for card {card['id']}\nEvidence source.md:1 source.md:2\nC1: PASS\nC2: PASS\n", encoding="utf-8")
    return F.finish(repo, card["id"], str(p.relative_to(repo)), verdict, "evidence checked")


def test_launch_orders_models_and_lenses_without_duplicate_work(repo):
    cards = F.launch(repo, spec())
    assert [tasks.codex_setting(c) for c in cards] == [("gpt-6.1-sol", "medium"), ("gpt-6-astra", "low")]
    assert cards[1]["depends_on"] == [cards[0]["id"]]
    assert tasks.ready_cards(repo)[0] == [cards[0]]
    assert all(len(tasks.brief(c).splitlines()) <= 30 for c in cards)
    assert "C1" in tasks.brief(cards[0])


def test_same_model_stage_is_refused_but_gemini_stage_is_accepted(repo, monkeypatch):
    # The producer and reviewer may share a vendor, but must not share a model.
    recipe = [
        ("producer", "codex", "audit", "gpt-6.1-sol", "medium", "Produce the scoped implementation."),
        ("challenge", "gemini", "audit", "gemini-2.5-pro", "low", "Independently challenge the report."),
    ]
    monkeypatch.setitem(F.RECIPES, "crossvendor-fixture", recipe)
    cards = F.launch(repo, spec() | {"id": "crossvendor", "recipe": "crossvendor-fixture"})
    assert cards[1]["vendor"] == "gemini"
    assert cards[1]["model"] == "gemini-2.5-pro"
    assert "agy.exe --print" in " ".join(cards[1]["steps"])
    assert "inline" in " ".join(cards[1]["steps"]).lower()
    complete(repo, cards[0])
    cards = tasks.load_all(repo)
    assert not F.gate(cards[1], cards, repo)

    recipe[1] = ("challenge", "gemini", "audit", "gpt-6.1-sol", "low", "Same model is forbidden.")
    with pytest.raises(ValueError, match="producer model"):
        F.launch(repo, spec() | {"id": "same-model", "recipe": "crossvendor-fixture"})


def test_finish_receipt_records_stage_model_id(repo, monkeypatch):
    recipe = [
        ("producer", "codex", "audit", "gpt-6.1-sol", "medium", "Producer."),
        ("challenge", "gemini", "audit", "gemini-fixture-model", "low", "Reviewer."),
    ]
    monkeypatch.setitem(F.RECIPES, "receipt-fixture", recipe)
    cards = F.launch(repo, spec() | {"id": "receipt", "recipe": "receipt-fixture"})
    done = complete(repo, cards[0])
    assert done["flow_receipt"]["model"] == "gpt-6.1-sol"


def test_done_alone_cannot_unlock_the_next_lens(repo):
    a, b = F.launch(repo, spec())
    a["state"] = "done"
    tasks.save(repo, a)
    assert tasks.ready_cards(repo)[0] == []
    assert any("receipt" in x for x in tasks.problems(b, tasks.load_all(repo)))


def test_pass_evidence_unlocks_and_changed_source_invalidates(repo):
    a, b = F.launch(repo, spec())
    complete(repo, a)
    assert [c["id"] for c in tasks.ready_cards(repo)[0]] == [b["id"]]
    (repo / "source.md").write_text("changed source", encoding="utf-8")
    assert tasks.ready_cards(repo)[0] == []


def test_rework_and_missing_criterion_cannot_advance(repo):
    a, b = F.launch(repo, spec())
    complete(repo, a, "REWORK")
    assert tasks.ready_cards(repo)[0] == []
    report = repo / tasks.LAB_REPORTS / (a["id"] + ".md")
    report.write_text(f"Report for card {a['id']}\nC1: PASS", encoding="utf-8")
    with pytest.raises(ValueError, match="C2"):
        F.finish(repo, a["id"], str(report.relative_to(repo)), "PASS", "check")


def test_duplicate_launch_never_overwrites_and_preview_writes_nothing(repo):
    F.launch(repo, spec(), preview=True)
    assert not (repo / tasks.DIR).exists()
    F.launch(repo, spec())
    with pytest.raises(ValueError, match="exists"):
        F.launch(repo, spec())


@pytest.mark.parametrize("scope", [["../escape"], [".env"], ["MyTradingSys/execution/x.py"], ["missing.md"]])
def test_unsafe_or_missing_scope_is_rejected(repo, scope):
    with pytest.raises(ValueError):
        F.launch(repo, spec() | {"scope_in": scope})


def test_legacy_done_cannot_bypass_flow_receipt(repo):
    a, _ = F.launch(repo, spec())
    with pytest.raises(SystemExit, match="lab_flow.py finish"):
        tasks.main(["done", a["id"], "--result", "done"])
    assert tasks.get(repo, a["id"])["state"] == "ready"


def test_report_mutation_and_contract_drift_block_next_stage(repo):
    a, b = F.launch(repo, spec())
    complete(repo, a)
    b["flow"]["criteria"][0] = "changed goal"
    tasks.save(repo, b)
    assert tasks.ready_cards(repo)[0] == []
    b["flow"]["criteria"][0] = spec()["criteria"][0]
    tasks.save(repo, b)
    (repo / tasks.LAB_REPORTS / (a["id"] + ".md")).write_text("changed", encoding="utf-8")
    assert tasks.ready_cards(repo)[0] == []


def test_flow_optimization_drops_arbitrary_share_caps_but_keeps_real_headroom():
    now = 100000
    rl = {"primary": {"used_percent": 10, "resets_at": 102000}, "secondary": {"used_percent": 10, "resets_at": 1000000}}
    rows = [{"at": "1970-01-02T03:40:00Z", "model": "gpt-6-luna", "effort": "low", "window_pts": 1, "week_pts": 1}] * 10
    assert R.budget_hold("gpt-6.1-sol", "medium", rl, rows, now)[0]
    assert R.budget_hold("gpt-6.1-sol", "medium", rl, rows, now, optimization=True) == ("", 0)
    rl["primary"]["used_percent"] = 99
    assert R.budget_hold("gpt-6.1-sol", "medium", rl, rows, now, optimization=True)[0]


def test_flow_pack_is_source_index_without_repeated_boot_documents(repo, monkeypatch):
    a, _ = F.launch(repo, spec())
    monkeypatch.setattr(P, "REPO", repo)
    pack = P.build(a["id"], 24)
    assert "Source index" in pack
    assert "\noriginal source\n" not in pack
    assert "## STATUS" not in pack
    assert "C1" in pack


def test_runner_requires_valid_receipt_even_if_card_json_says_done(repo, monkeypatch):
    a, _ = F.launch(repo, spec())
    monkeypatch.setattr(R, "REPO", repo)
    done = complete(repo, a)
    assert R.judge(done, [done["flow_receipt"]["report"]], "audit", []) == "DONE"
    done.pop("flow_receipt")
    assert R.judge(done, ["report.md"], "audit", []) == "BLOCKED"


def test_editing_current_goal_or_model_cannot_silently_change_recipe(repo):
    a, _ = F.launch(repo, spec())
    a["goal"] = "A different task"
    assert F.gate(a, tasks.load_all(repo), repo)
    a["goal"] = a["flow"]["goal"]
    a["model"] = "gpt-6-luna"
    assert F.gate(a, tasks.load_all(repo), repo)


def test_effective_model_mismatch_revokes_receipt_and_holds_child(repo):
    a, b = F.launch(repo, spec())
    complete(repo, a)
    assert tasks.get(repo, b["id"])["state"] == "ready"
    F.reject_run(repo, a["id"], "CLI used a different model")
    assert tasks.ready_cards(repo)[0] == []
    assert "flow_receipt" not in tasks.get(repo, a["id"])


def test_run_commands_are_part_of_contract(repo):
    run_spec = spec() | {"id": "run", "recipe": "run-review", "commands": ["python study.py"]}
    cards = F.launch(repo, run_spec)
    cards[0]["commands"] = ["python study.py --range holdout"]
    assert any("contract" in e for e in F.gate(cards[0], tasks.load_all(repo), repo))
    mutation = repo / "scripts/dev/test_mutation.py"
    mutation.parent.mkdir(parents=True, exist_ok=True)
    mutation.write_text("def test_dummy_output_rejected():\n    assert output != 'dummy'\n", encoding="utf-8")
    build_spec = spec() | {"id": "build", "recipe": "build-review", "tests": "pytest scripts/dev/test_x.py", "mutation_check": "scripts/dev/test_mutation.py::test_dummy_output_rejected"}
    build_cards = F.launch(repo, build_spec)
    build_cards[0]["tests"] = "pytest scripts/dev/test_other.py"
    assert any("contract" in e for e in F.gate(build_cards[0], tasks.load_all(repo), repo))


def test_stage_two_cannot_clear_previous_dependency(repo):
    a, b = F.launch(repo, spec())
    b["depends_on"] = []
    b["state"] = "ready"
    assert any("depends_on" in e for e in F.gate(b, [a, b], repo))


def test_stage_two_cannot_reuse_stage_one_report(repo):
    a, b = F.launch(repo, spec())
    complete(repo, a)
    with pytest.raises(ValueError, match="already used"):
        F.finish(repo, b["id"], tasks.get(repo, a["id"])["flow_receipt"]["report"], "PASS", "copied")


def test_status_lines_without_evidence_are_rejected(repo):
    a, _ = F.launch(repo, spec())
    p = repo / tasks.LAB_REPORTS / (a["id"] + ".md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"Report for card {a['id']}\nC1: PASS\nC2: PASS\n", encoding="utf-8")
    with pytest.raises(ValueError, match="evidence"):
        F.finish(repo, a["id"], str(p.relative_to(repo)), "PASS", "no evidence")


def test_data_scope_hash_changes_when_data_file_changes(repo, monkeypatch, tmp_path):
    data_root = tmp_path / "data"
    data_root.mkdir()
    data_file = data_root / "dev.csv"
    data_file.write_text("t,c\n1719705600000,1\n", encoding="utf-8")
    monkeypatch.setattr(F, "DATA_ROOT", data_root, raising=False)
    scope = [str(data_file)]
    before = F.fingerprint(repo, ["source.md"], scope)
    data_file.write_text("t,c\n1719705600000,2\n", encoding="utf-8")
    after = F.fingerprint(repo, ["source.md"], scope)
    assert before != after
    data_key = "data:dev.csv"
    assert before[data_key] != after[data_key]
    cards = F.launch(repo, spec() | {"data_scope": [str(data_file)]})
    done = complete(repo, cards[0])
    assert done["flow_receipt"]["sources"][data_key] == after[data_key]


def test_holdout_data_path_is_refused(repo, monkeypatch, tmp_path):
    data_root = tmp_path / "data"
    holdout = data_root / "holdout" / "secret.csv"
    holdout.parent.mkdir(parents=True)
    holdout.write_text("not for lab", encoding="utf-8")
    monkeypatch.setattr(F, "DATA_ROOT", data_root, raising=False)
    with pytest.raises(ValueError, match="holdout"):
        F.safe_file(repo, str(holdout))


def test_renamed_dev_copy_with_post_cutoff_bar_is_refused(repo, monkeypatch, tmp_path):
    import numpy as np
    data_root = tmp_path / "data"
    data_root.mkdir()
    copied = data_root / "renamed.npz"
    # 2024-07-01T00:00:00Z is the first disallowed open time.
    np.savez(copied, t=np.array([1719792000000, 1720000000000], dtype=np.int64), c=np.array([1., 2.]))
    monkeypatch.setattr(F, "DATA_ROOT", data_root, raising=False)
    with pytest.raises(ValueError, match="post-cutoff"):
        F.safe_file(repo, str(copied))


def test_unsupported_data_extension_is_refused(repo, monkeypatch, tmp_path):
    data_root = tmp_path / "data"
    opaque = data_root / "renamed.parquet"
    opaque.parent.mkdir(parents=True)
    opaque.write_bytes(b"opaque data")
    monkeypatch.setattr(F, "DATA_ROOT", data_root, raising=False)
    with pytest.raises(ValueError, match="cannot verify data timestamps"):
        F.safe_file(repo, str(opaque))


def test_seconds_epoch_after_cutoff_is_refused(repo, monkeypatch, tmp_path):
    data_root = tmp_path / "data"
    seconds = data_root / "renamed.csv"
    seconds.parent.mkdir(parents=True)
    seconds.write_text("timestamp,close\n1735689600,1.0\n", encoding="utf-8")
    monkeypatch.setattr(F, "DATA_ROOT", data_root, raising=False)
    with pytest.raises(ValueError, match="post-cutoff"):
        F.safe_file(repo, str(seconds))

