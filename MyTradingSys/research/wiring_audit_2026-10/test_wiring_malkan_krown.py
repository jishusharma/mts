"""Checks for WIRING_MALKAN_KROWN.{csv,md}: footer row count, verdicts, every Krown ledger rule present, quotes verify (exit 0)."""
import csv
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CSV = HERE / "WIRING_MALKAN_KROWN.csv"
MD = HERE / "WIRING_MALKAN_KROWN.md"
QUOTES = HERE / "QUOTES_USED_MALKAN_KROWN.md"
LEDGER = HERE.parent / "krown_ta101_2026-10-13" / "KROWN_RULES.csv"
VERDICTS = {"wired", "unwired-worth-wiring", "not-worth-wiring"}


def rows():
    with CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_md_footer_equals_csv_rows():
    last = [ln for ln in MD.read_text(encoding="utf-8").splitlines() if ln.strip()][-1]
    assert last == f"ROWS: {len(rows())}"


def test_every_krown_ledger_rule_has_a_row():
    with LEDGER.open(encoding="utf-8", newline="") as fh:
        ledger = {r["rule_id"] for r in csv.DictReader(fh)}
    assert ledger <= {r["rule_id"] for r in rows() if r["trader"] == "Krown"}


def test_verdicts_and_locations():
    for r in rows():
        assert r["verdict"] in VERDICTS, r["rule_id"]
        assert r["code_file_line"] and r["test"] and r["rule_file_line"], r["rule_id"]
        if r["verdict"] == "wired":
            assert r["extent"] in ("full", "partial") and r["code_file_line"] != "none (no code)", r["rule_id"]
        if r["quote_status"] == "OK":
            assert r["quote"] and r["quote_file_line"], r["rule_id"]


def test_quotes_verify():
    res = subprocess.run([sys.executable, str(ROOT / "scripts/dev/verify_extract_quotes.py"), str(QUOTES)],
                         cwd=ROOT, capture_output=True, text=True)
    assert res.returncode == 0, res.stdout[-500:]
