"""
MTS consumer for the CBP mts_queue contract.

Reads CryptoScrapper/mts_queue/pending.json, writes acks to
mts_queue/acks/<id>.json, and never modifies pending.json (CBP owns it;
the ack file is the only consumed/rejected state).

Read-only on markets. Never places orders. No live process imports it.
"""
import datetime
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

# Operator 2026-10-14: F:\CryptoScrapper is authoritative. MTS_CBP_QUEUE overrides it on a host
# whose CBP checkout lives elsewhere (the NUC keeps it under IdeaProjects).
DEFAULT_QUEUE = Path(os.environ.get("MTS_CBP_QUEUE") or r"F:\CryptoScrapper\mts_queue")
CONSUMER_ID = "MTS-consumer-v1"


def parse_iso(s):
    if s is None:
        return None
    s = str(s).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.datetime.fromisoformat(s)


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def _write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def consume(queue_dir, validate=None, on_consume=None):
    """validate(alert)->list of error strings (non-empty rejects); on_consume(alert) runs for accepted ones."""
    queue_dir = Path(queue_dir)
    pending_path = queue_dir / "pending.json"
    acks_dir = queue_dir / "acks"
    acks_dir.mkdir(exist_ok=True)
    with open(pending_path, "r", encoding="utf-8-sig") as f:
        alerts = json.load(f)
    if not isinstance(alerts, list):
        raise ValueError("pending.json must contain a list")
    now = now_utc()
    result = {"consumed": [], "rejected_expired": [], "skipped_acked": [], "skipped_status": []}
    for a in alerts:
        aid = a.get("id")
        if not aid:
            continue
        ack_file = acks_dir / (aid + ".json")
        if ack_file.exists():
            result["skipped_acked"].append(aid)
            continue
        status = (a.get("status") or "").lower()
        if status != "pending":
            result["skipped_status"].append({"id": aid, "status": status})
            continue
        exp = parse_iso(a.get("expires_at"))
        ack = {
            "id": aid,
            "acked_at": now.isoformat().replace("+00:00", "Z"),
            "consumer": CONSUMER_ID,
            "asset": a.get("asset"),
            "direction": a.get("direction"),
            "entry_trigger": a.get("entry_trigger"),
            "target": a.get("target"),
            "invalidation": a.get("invalidation"),
            "stop_loss": a.get("stop_loss"),
            "expires_at": a.get("expires_at"),
            "source": a.get("source"),
        }
        if exp is not None and exp < now:
            ack["decision"] = "rejected"
            ack["reason"] = "expired before consumption"
            _write_json(ack_file, ack)
            result["rejected_expired"].append(aid)
            continue
        errors = validate(a) if validate else []
        if errors:
            ack["decision"] = "rejected"
            ack["reason"] = "invalid: " + "; ".join(errors)
            _write_json(ack_file, ack)
            result.setdefault("rejected_invalid", []).append(aid)
            continue
        if on_consume:
            on_consume(a)
        ack["decision"] = "consumed"
        _write_json(ack_file, ack)
        result["consumed"].append(aid)
    return result


if __name__ == "__main__":
    q = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_QUEUE
    r = consume(q)
    print(json.dumps(r, indent=2))
