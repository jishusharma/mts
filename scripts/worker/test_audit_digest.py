"""Tests for scripts/worker/audit_digest.py, written from the design in
Dumps/workers/NUC-QUEUE/specs/096-audit-digest.md (T056). The module does not exist yet, so this file
currently fails at import time with ModuleNotFoundError -- expected until 096's reply is promoted from
audit_digest.py.new to audit_digest.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_digest  # noqa: E402


ONE_FINDING_REPLY = (
    "TASK: Audit (A7)\nSTATUS: DONE\nSUMMARY: s\nFINDINGS: f\nNEXT: n\n\n"
    "FINDING 1 | A7 | severity H | MyTradingSys/execution/risk_guard.py:21\n"
    "QUOTE: MAX_ACCOUNT_NOTIONAL_USD = 10000\n"
    "WHY: hardcoded cap can't be tuned per environment\n"
    "FIX: read it from a config file instead\n"
)

NO_FINDINGS_REPLY = "TASK: Audit (A1)\nSTATUS: DONE\nSUMMARY: s\nFINDINGS: f\nNEXT: n\n\nNO FINDINGS\n"


# ---------- load_closed_ids ----------

def test_load_closed_ids_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "CLOSED_PATH", tmp_path / "nope.json")
    assert audit_digest.load_closed_ids() == set()


def test_load_closed_ids_reads_json_list(tmp_path, monkeypatch):
    p = tmp_path / "closed.json"
    p.write_text(json.dumps(["abc1234567", "def7654321"]), encoding="utf-8")
    monkeypatch.setattr(audit_digest, "CLOSED_PATH", p)
    assert audit_digest.load_closed_ids() == {"abc1234567", "def7654321"}


# ---------- parse_findings ----------

def test_parse_findings_basic():
    findings = audit_digest.parse_findings("098-x", ONE_FINDING_REPLY)
    assert len(findings) == 1
    f = findings[0]
    assert f["template"] == "A7"
    assert f["severity"] == "H"
    assert f["path"] == "MyTradingSys/execution/risk_guard.py"
    assert f["line"] == 21
    assert f["quote"] == "MAX_ACCOUNT_NOTIONAL_USD = 10000"
    assert "cap can't be tuned" in f["why"]
    assert "config file" in f["fix"]


def test_parse_findings_no_findings_returns_empty():
    assert audit_digest.parse_findings("097-x", NO_FINDINGS_REPLY) == []


def test_parse_findings_malformed_block_is_skipped():
    bad = (
        "TASK: Audit (A1)\nSTATUS: DONE\nSUMMARY: s\nFINDINGS: f\nNEXT: n\n\n"
        "FINDING 1 | A1 | severity L | a.py:5\n"
        "QUOTE: some line\n"
        "NEXT: missing WHY/FIX lines entirely\n"
    )
    assert audit_digest.parse_findings("x", bad) == []


def test_parse_findings_multiple_blocks():
    two = ONE_FINDING_REPLY + (
        "FINDING 2 | A7 | severity L | MyTradingSys/execution/risk_guard.py:37\n"
        "QUOTE: if current_position_notional_usd < 0:\n"
        "WHY: minor style note\n"
        "FIX: none needed\n"
    )
    findings = audit_digest.parse_findings("x", two)
    assert len(findings) == 2
    assert findings[1]["line"] == 37


# ---------- quote_matches ----------

def test_quote_matches_exact_line(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "REPO", tmp_path)
    f = tmp_path / "mod.py"
    f.write_text("\n".join(f"line{i}" for i in range(1, 11)), encoding="utf-8")
    assert audit_digest.quote_matches("mod.py", 5, "line5") is True


def test_quote_matches_within_tolerance(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "REPO", tmp_path)
    f = tmp_path / "mod.py"
    f.write_text("\n".join(f"line{i}" for i in range(1, 11)), encoding="utf-8")
    # claimed line 5, real content is at line 7 -- within +-3
    assert audit_digest.quote_matches("mod.py", 5, "line7") is True


def test_quote_matches_outside_tolerance_is_false(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "REPO", tmp_path)
    f = tmp_path / "mod.py"
    f.write_text("\n".join(f"line{i}" for i in range(1, 11)), encoding="utf-8")
    assert audit_digest.quote_matches("mod.py", 1, "line9") is False


def test_quote_matches_missing_file_is_false(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "REPO", tmp_path)
    assert audit_digest.quote_matches("nope.py", 1, "anything") is False


# ---------- finding_id ----------

def test_finding_id_stable_for_same_inputs():
    a = audit_digest.finding_id("p.py", "some line")
    b = audit_digest.finding_id("p.py", "some line")
    assert a == b
    assert len(a) == 10


def test_finding_id_differs_for_different_quote():
    a = audit_digest.finding_id("p.py", "line one")
    b = audit_digest.finding_id("p.py", "line two")
    assert a != b


# ---------- iter_audit_tasks ----------

def _write_task(done_dir, task_id, task_text, response_text, verdict_line4, finished_utc="2026-09-28T00:00:00Z"):
    (done_dir / f"{task_id}.task.json").write_text(
        json.dumps({"id": task_id, "task": task_text}), encoding="utf-8"
    )
    (done_dir / f"{task_id}.reply.json").write_text(
        json.dumps({"response": response_text, "finished_utc": finished_utc}), encoding="utf-8"
    )
    verdict_lines = ["TASK:     x", "STATUS:   DONE", "SUMMARY:  s", verdict_line4, "NEXT:     n"]
    (done_dir / f"{task_id}.verdict.txt").write_text("\n".join(verdict_lines), encoding="utf-8")


def test_iter_audit_tasks_skips_non_audit_task(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "DONE_DIR", tmp_path)
    _write_task(tmp_path, "010-devtask", "Draft two sections", "irrelevant", "FINDINGS: verdict PASS; x")
    assert list(audit_digest.iter_audit_tasks()) == []


def test_iter_audit_tasks_skips_verdict_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "DONE_DIR", tmp_path)
    _write_task(tmp_path, "097-x", "Audit (A1) -- x", ONE_FINDING_REPLY, "FINDINGS: verdict FAIL; x")
    assert list(audit_digest.iter_audit_tasks()) == []


def test_iter_audit_tasks_skips_missing_verdict(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "DONE_DIR", tmp_path)
    (tmp_path / "097-x.task.json").write_text(json.dumps({"task": "Audit (A1) -- x"}), encoding="utf-8")
    (tmp_path / "097-x.reply.json").write_text(json.dumps({"response": "NO FINDINGS"}), encoding="utf-8")
    assert list(audit_digest.iter_audit_tasks()) == []


def test_iter_audit_tasks_yields_valid_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "DONE_DIR", tmp_path)
    _write_task(tmp_path, "098-x", "Audit (A7) -- x", ONE_FINDING_REPLY, "FINDINGS: verdict PASS; x")
    items = list(audit_digest.iter_audit_tasks())
    assert len(items) == 1
    task_id, response, ts, template = items[0]
    assert task_id == "098-x"
    assert response == ONE_FINDING_REPLY
    assert ts == "2026-09-28T00:00:00Z"


# ---------- render_digest ----------

def test_render_digest_no_findings_message():
    text = audit_digest.render_digest([], closed_count=0, dropped_unconfirmed=0)
    assert "(no open findings)" in text
    assert "# Audit digest (T056)" in text


def test_render_digest_one_line_per_finding_and_caps():
    findings = []
    for i in range(50):
        findings.append({
            "task_id": f"{900 + i}-audit-x",
            "template": "A1",
            "severity": "L",
            "path": "a.py",
            "line": i + 1,
            "quote": f"q{i}",
            "why": "why text",
            "fix": "fix text",
            "finished_utc": f"2026-09-{(i % 27) + 1:02d}T00:00:00Z",
        })
    text = audit_digest.render_digest(findings, closed_count=0, dropped_unconfirmed=0)
    finding_lines = [l for l in text.splitlines() if l.startswith("- [")]
    assert len(finding_lines) == audit_digest.MAX_FINDINGS
    assert all("\n" not in l for l in finding_lines)


# ---------- run_digest (integration) ----------

def test_run_digest_end_to_end(tmp_path, monkeypatch):
    done = tmp_path / "done"
    done.mkdir()
    monkeypatch.setattr(audit_digest, "DONE_DIR", done)
    out_path = tmp_path / "AUDIT_DIGEST.md"
    monkeypatch.setattr(audit_digest, "OUT_PATH", out_path)
    monkeypatch.setattr(audit_digest, "CLOSED_PATH", tmp_path / "closed.json")
    monkeypatch.setattr(audit_digest, "REPO", tmp_path)

    real_file = tmp_path / "MyTradingSys" / "execution" / "risk_guard.py"
    real_file.parent.mkdir(parents=True)
    real_file.write_text("x\n" * 20 + "MAX_ACCOUNT_NOTIONAL_USD = 10000\n", encoding="utf-8")
    reply = ONE_FINDING_REPLY.replace(
        "MyTradingSys/execution/risk_guard.py:21",
        "MyTradingSys/execution/risk_guard.py:21",
    )
    _write_task(done, "098-audit-a7-risk-guard", "Audit (A7) -- x", reply, "FINDINGS: verdict PASS; x")

    rc = audit_digest.run_digest()
    assert rc == 0
    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")
    assert "risk_guard.py:21" in text


# ---------- real reply-format variants seen in done/9*-audit-*.reply.json ----------

REAL_LONGSEV = (
    "TASK: Audit (A3)\nSTATUS: DONE\nSUMMARY: s\nFINDINGS: 1 finding\nNEXT: n\n\n"
    "FINDING 1 | A-001 | MEDIUM | MyTradingSys/x/y.py:28\n"
    'QUOTE: "Raise whatever `find_swings` raises on empty `bars`."\n'
    "WHY: ambiguous\nFIX: clarify\n"
)
REAL_ONELINE = (
    "TASK: Audit (A1)\nSTATUS: DONE\nSUMMARY: s\nFINDINGS: 1\nNEXT: n\n\n"
    "FINDING 1 | A1-001 | severity H | MyTradingSys/backtest/bt/bt_stats.py:42 | return mean / sd | "
    "uses n-1 not n | use population sd\n\nNO FINDINGS\n"
)
REAL_BOLD = (
    "**FINDING 2** | A1 | severity **L** | a/b.py:3\n\n**QUOTE:** `x = 1`\n\n**WHY:** w\n\n**FIX:** f\n"
)
NOFIND_HEADER = "FINDINGS: NO FINDINGS\nNEXT: done\n"


def test_parse_long_severity_and_quoted_quote():
    f = audit_digest.parse_findings("904-x", REAL_LONGSEV, "A3")
    assert len(f) == 1
    assert f[0]["severity"] == "M" and f[0]["template"] == "A3"
    assert f[0]["quote"] == "Raise whatever `find_swings` raises on empty `bars`."
    assert f[0]["line"] == 28


def test_parse_one_line_pipe_form():
    f = audit_digest.parse_findings("914-x", REAL_ONELINE)
    assert len(f) == 1
    assert f[0]["quote"] == "return mean / sd" and f[0]["severity"] == "H"
    assert f[0]["path"].endswith("bt_stats.py") and f[0]["line"] == 42


def test_parse_markdown_bold_blank_lines():
    f = audit_digest.parse_findings("9-x", REAL_BOLD)
    assert len(f) == 1 and f[0]["quote"] == "x = 1" and f[0]["severity"] == "L"


def test_findings_summary_line_is_not_a_finding():
    assert audit_digest.parse_findings("9-x", NOFIND_HEADER) == []
    assert audit_digest.parse_findings_ex("9-x", NOFIND_HEADER) == ([], 0)


def test_quote_substring_of_line_and_line_off(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_digest, "REPO", tmp_path)
    (tmp_path / "f.py").write_text("a\n" * 30 + "    return mean / sd\n" + "b\n" * 30, encoding="utf-8")
    assert audit_digest.quote_status("f.py", 31, "return mean / sd") == "ok"
    assert audit_digest.quote_status("f.py", 5, "return mean / sd") == "line_off"
    assert audit_digest.quote_status("f.py", 31, "nope") == "quote_not_found"
    assert audit_digest.quote_status("g.py", 31, "x") == "file_missing"


def test_run_digest_reports_drop_reasons_and_sorts_by_severity(tmp_path, monkeypatch):
    done = tmp_path / "done"
    done.mkdir()
    monkeypatch.setattr(audit_digest, "DONE_DIR", done)
    out = tmp_path / "D.md"
    monkeypatch.setattr(audit_digest, "OUT_PATH", out)
    monkeypatch.setattr(audit_digest, "CLOSED_PATH", tmp_path / "c.json")
    monkeypatch.setattr(audit_digest, "REPO", tmp_path)
    (tmp_path / "MyTradingSys" / "backtest" / "bt").mkdir(parents=True)
    (tmp_path / "MyTradingSys/backtest/bt/bt_stats.py").write_text("q\n" * 41 + "    return mean / sd\n", encoding="utf-8")
    _write_task(done, "914-audit-a1-x", "Audit (A1) -- x", REAL_ONELINE, "FINDINGS: verdict PASS; x")
    _write_task(done, "915-audit-a1-y", "Audit (A1) -- y", REAL_BOLD, "FINDINGS: verdict PASS; x")
    _write_task(done, "916-audit-a1-z", "Audit (A1) -- z", NOFIND_HEADER, "FINDINGS: verdict PASS; x")
    assert audit_digest.run_digest() == 0
    text = out.read_text(encoding="utf-8")
    assert "bt_stats.py:42" in text
    assert "Dropped by reason:" in text and "file_missing=1" in text
