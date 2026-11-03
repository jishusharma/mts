"""S4 consumer: one fixture row run_once -> store -> cbp.query -> cbp.candidates -> CANDIDATE_UNTESTED record.
Never an order, never promoted_setups.json (D5 as built: no queue, no ack)."""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys"))
sys.path.insert(0, str(ROOT / "scripts" / "dev"))

import cbp  # noqa: E402
import cbp_run  # noqa: E402
from test_cbp_query import GOOD, NOW, _setup  # noqa: E402

PROMOTED = ROOT / "MyTradingSys" / "execution" / "promoted_setups.json"


def _run(tmp_path, monkeypatch, extracted=GOOD):
    st = _setup(tmp_path, monkeypatch)
    assert cbp_run.run_once(NOW, fetch=lambda *a: None, extract=lambda v, b: extracted, store=st) == (1, 1, 0)
    return st


def test_one_row_flows_to_one_untested_candidate(tmp_path, monkeypatch):
    before = PROMOTED.read_bytes()
    st = _run(tmp_path, monkeypatch)
    files = sorted(p.name for p in tmp_path.rglob("*") if p.is_file())
    recs = cbp.candidates(cbp.query(store=st, now=NOW), now=NOW)
    assert len(recs) == 1
    r = recs[0]
    assert r["source"] == "cbp:Krown"
    assert r["status"] == "CANDIDATE_UNTESTED"
    assert r["order_eligible"] is False
    assert r["evidence"] == "V" * 11
    assert cbp.parse_expiry(r["expires_at"]) > NOW
    assert sorted(p.name for p in tmp_path.rglob("*") if p.is_file()) == files  # candidates() wrote no file
    assert PROMOTED.read_bytes() == before


def test_untradable_row_gives_none(tmp_path, monkeypatch):
    bare = dict(GOOD, trades=[dict(GOOD["trades"][0], target="", invalidation="")])
    st = _run(tmp_path, monkeypatch, bare)
    assert cbp.candidates(cbp.query(store=st, now=NOW), now=NOW) == []


def test_expired_row_gives_none(tmp_path, monkeypatch):
    st = _run(tmp_path, monkeypatch)
    rows = cbp.query(store=st, now=NOW)
    later = datetime(2026, 12, 1, tzinfo=timezone.utc)
    assert cbp.candidates(rows, now=later) == []
