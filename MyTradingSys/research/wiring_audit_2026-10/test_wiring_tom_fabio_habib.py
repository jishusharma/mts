"""Checks for WIRING_TOM_FABIO_HABIB.{csv,md}: footer row count, verdicts, quotes verify (exit 0)."""
import csv
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2] if (HERE.parents[2] / "scripts").exists() else HERE.parents[3]
CSV = HERE / "WIRING_TOM_FABIO_HABIB.csv"
MD = HERE / "WIRING_TOM_FABIO_HABIB.md"
QUOTES = HERE / "QUOTES_USED_TOM_FABIO.md"
VERDICTS = {"wired", "unwired-worth-wiring", "not-worth-wiring"}


def rows():
    with CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_md_footer_equals_csv_rows():
    last = [ln for ln in MD.read_text(encoding="utf-8").splitlines() if ln.strip()][-1]
    assert last == f"ROWS: {len(rows())}"


def test_every_row_has_verdict_quote_and_locations():
    rs = rows()
    assert len(rs) >= 400
    for r in rs:
        assert r["verdict"] in VERDICTS, r["rule_id"]
        assert r["quote_file_line"] and r["code_file_line"] and r["rule_id"], r["rule_id"]
        if r["quote_status"] == "OK":
            assert r["quote"], r["rule_id"]
        if r["verdict"] == "unwired-worth-wiring":
            assert r["priority"] in {"H", "M", "L"}, r["rule_id"]


def test_one_row_per_tom_quote_id():
    ids = [r["rule_id"] for r in rows() if r["trader"] == "Tom"]
    assert len(ids) == len(set(ids)) == 270


def test_no_quote_rows_listed_in_md():
    md = MD.read_text(encoding="utf-8")
    for r in rows():
        if r["quote_status"] != "OK":
            assert f"| {r['rule_id']} |" in md, r["rule_id"]


def test_verify_extract_quotes_exit_zero():
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "dev" / "verify_extract_quotes.py"), str(QUOTES)],
                       capture_output=True, text=True, cwd=str(ROOT))
    assert p.returncode == 0, p.stdout[-500:]
