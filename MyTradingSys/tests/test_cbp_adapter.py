import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "queue"))

import cbp_adapter  # noqa: E402


def _good(i="g1", **kw):
    a = {"id": i, "queued_at": "2026-09-30T00:00:00Z",
         "source": {"analyst": "T", "channel": "c", "video_id": "v", "publish_date": "2026-09-30"},
         "asset": "BTC", "direction": "LONG", "entry_trigger": "x", "target": {"type": "level"},
         "invalidation": "y", "status": "pending", "expires_at": "2099-01-01T00:00:00Z"}
    a.update(kw)
    return a


def _q(tmp_path, alerts):
    q = tmp_path / "mts_queue"
    q.mkdir()
    (q / "pending.json").write_text(json.dumps(alerts), encoding="utf-8")
    return q


def test_validate_flags_each_violation():
    assert cbp_adapter.validate(_good()) == []
    assert any("direction" in e for e in cbp_adapter.validate(_good(direction="UP")))
    assert any("missing invalidation" in e for e in cbp_adapter.validate(_good(invalidation="")))
    assert any("source.video_id" in e for e in cbp_adapter.validate(_good(source={"analyst": "T", "channel": "c", "publish_date": "d"})))
    assert any("contract_version" in e for e in cbp_adapter.validate(_good(contract_version=2)))
    assert any("ISO" in e for e in cbp_adapter.validate(_good(expires_at="soon")))


def test_ingest_makes_untested_non_order_candidates_idempotently(tmp_path):
    q = _q(tmp_path, [_good("g1"), _good("bad", direction="UP"), _good("old", expires_at="2020-01-01T00:00:00Z")])
    out = tmp_path / "cand"
    r = cbp_adapter.ingest(q, out)
    assert r["consumed"] == ["g1"] and r["rejected_invalid"] == ["bad"] and r["rejected_expired"] == ["old"]
    rows = [json.loads(l) for l in (out / "cbp_candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [c["cand_id"] for c in rows] == ["cbp:g1"]
    assert rows[0]["order_eligible"] is False and rows[0]["status"] == "CANDIDATE_UNTESTED"
    assert json.loads((q / "acks" / "bad.json").read_text(encoding="utf-8"))["decision"] == "rejected"
    # second run: nothing new, no duplicate rows
    cbp_adapter.ingest(q, out)
    assert len((out / "cbp_candidates.jsonl").read_text(encoding="utf-8").splitlines()) == 1


def test_adapter_has_no_order_path():
    src = Path(cbp_adapter.__file__).read_text(encoding="utf-8")
    assert "auto_trader" not in src and "place_order" not in src


def test_default_queue_is_f_tree_and_env_overrides(tmp_path):
    import importlib
    import os
    import consumer
    saved = os.environ.pop("MTS_CBP_QUEUE", None)
    try:
        importlib.reload(consumer)
        assert str(consumer.DEFAULT_QUEUE) == r"F:\CryptoScrapper\mts_queue" or consumer.DEFAULT_QUEUE.as_posix() == "F:/CryptoScrapper/mts_queue"
        os.environ["MTS_CBP_QUEUE"] = str(tmp_path)
        importlib.reload(consumer)
        assert consumer.DEFAULT_QUEUE == tmp_path
    finally:
        os.environ.pop("MTS_CBP_QUEUE", None)
        if saved:
            os.environ["MTS_CBP_QUEUE"] = saved
        importlib.reload(consumer)


def test_quote_verified_row_is_consumed_and_unverifiable_quote_rejected(tmp_path):
    tr = tmp_path / "inbox"
    tr.mkdir()
    (tr / "T_v.txt").write_text("header\n\nSo we're probably looking at 87,000 bucks, that is my line in the sand now.\n", encoding="utf-8")
    ok = _good("ok", target={"type": "fixed_price", "note": '87,000 ("we\'re probably looking at 87,000 bucks")'},
               invalidation='close below 79,700 ("that is my line in the sand now")')
    fake = _good("fake", invalidation='close below 1 ("the analyst never said this sentence")')
    noquote = _good("noquote")
    q = _q(tmp_path, [ok, fake, noquote])
    out = tmp_path / "cand"
    r = cbp_adapter.ingest(q, out, transcript_dir=tr)
    assert r["consumed"] == ["ok"] and sorted(r["rejected_invalid"]) == ["fake", "noquote"]
    ack = json.loads((q / "acks" / "ok.json").read_text(encoding="utf-8"))
    assert ack["decision"] == "consumed"
    assert "never said" in json.loads((q / "acks" / "fake.json").read_text(encoding="utf-8"))["reason"]
    rows = [json.loads(l) for l in (out / "cbp_candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [c["cand_id"] for c in rows] == ["cbp:ok"] and rows[0]["order_eligible"] is False
