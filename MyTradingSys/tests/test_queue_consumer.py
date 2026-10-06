import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "queue"))

import consumer  # noqa: E402


def _write(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def test_consumer_end_to_end(tmp_path):
    q = tmp_path / "mts_queue"
    q.mkdir()
    base = {
        "id": "test_fresh",
        "queued_at": "2026-09-30T00:00:00Z",
        "source": {"analyst": "T", "channel": "c", "video_id": "v", "publish_date": "2026-09-30"},
        "asset": "BTC",
        "direction": "LONG",
        "entry_trigger": "x",
        "target": {"type": "level"},
        "invalidation": "y",
        "status": "pending",
        "expires_at": "2099-01-01T00:00:00Z",
    }
    expired = dict(base, id="test_expired", expires_at="2020-01-01T00:00:00Z")
    already_consumed = dict(base, id="test_already_consumed", status="consumed")
    already_rejected = dict(base, id="test_already_rejected", status="rejected")
    _write(q / "pending.json", [base, expired, already_consumed, already_rejected])

    pending_before = json.loads((q / "pending.json").read_text(encoding="utf-8"))
    r = consumer.consume(q)

    assert "test_fresh" in r["consumed"]
    assert "test_expired" in r["rejected_expired"]
    skipped_ids = [x["id"] for x in r["skipped_status"]]
    assert "test_already_consumed" in skipped_ids
    assert "test_already_rejected" in skipped_ids

    assert (q / "acks" / "test_fresh.json").exists()
    assert (q / "acks" / "test_expired.json").exists()
    assert not (q / "acks" / "test_already_consumed.json").exists()
    assert not (q / "acks" / "test_already_rejected.json").exists()

    # contract: MTS never rewrites CBP's pending.json
    assert json.loads((q / "pending.json").read_text(encoding="utf-8")) == pending_before
