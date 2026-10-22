"""
CBP -> MTS adapter. CBP (CryptoScrapper) stays a separate producer and writes
mts_queue/pending.json (contract: queue/cbp_contract_v1.schema.json). This adapter
validates each pending entry and turns accepted ones into CANDIDATES appended to
<out_dir>/cbp_candidates.jsonl, then acks via consumer.consume.

A candidate is an analyst idea, not a signal: order_eligible is always False and the
status is CANDIDATE_UNTESTED until a backtest of that analyst's rule exists. No field
here is tuned or defaulted (provenance rule); values are copied from CBP as written.
Read-only on markets. Never places orders. No live process imports this module.
"""
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import consumer  # noqa: E402

CONTRACT_VERSION = 1
DIRECTIONS = ("LONG", "SHORT")
REQUIRED = ("id", "queued_at", "source", "asset", "direction", "entry_trigger",
            "target", "invalidation", "expires_at")
SOURCE_REQUIRED = ("analyst", "channel", "video_id", "publish_date")
QUOTED = re.compile(r'"([^"]{8,})"')
DEFAULT_TRANSCRIPTS = Path(r"F:\CryptoScrapper\cbp_v2\inbox")
DEFAULT_OUT = Path(__file__).resolve().parent / "candidates"


def validate(alert):
    """Return a list of contract violations (empty = valid)."""
    if not isinstance(alert, dict):
        return ["entry is not an object"]
    errs = []
    ver = alert.get("contract_version", CONTRACT_VERSION)
    if ver != CONTRACT_VERSION:
        errs.append("unsupported contract_version %r" % (ver,))
    for k in REQUIRED:
        if alert.get(k) in (None, "", {}):
            errs.append("missing " + k)
    src = alert.get("source")
    if isinstance(src, dict):
        errs += ["missing source." + k for k in SOURCE_REQUIRED if not src.get(k)]
    elif src not in (None, "", {}):
        errs.append("source must be an object")
    if alert.get("direction") not in DIRECTIONS and alert.get("direction") not in (None, ""):
        errs.append("direction must be LONG or SHORT")
    if alert.get("target") not in (None, "", {}) and not isinstance(alert["target"], dict):
        errs.append("target must be an object")
    for k in ("expires_at", "queued_at"):
        if alert.get(k):
            try:
                consumer.parse_iso(alert[k])
            except ValueError:
                errs.append(k + " is not ISO-8601")
    return errs


def _norm(s):
    return " ".join(re.sub(r"[^a-z0-9%]+", " ", s.lower()).split())


def quote_errors(alert, transcript_dir):
    """Every analyst quote (text in double quotes) in entry_trigger/target.note/invalidation must occur
    in the transcript <dir>/<analyst>_<video_id>.txt (case/punctuation-insensitive); at least one is required."""
    src = alert.get("source") or {}
    path = Path(transcript_dir) / ("%s_%s.txt" % (src.get("analyst"), src.get("video_id")))
    try:
        body = _norm(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return ["no transcript " + path.name]
    tgt = alert.get("target") if isinstance(alert.get("target"), dict) else {}
    fields = [alert.get("entry_trigger"), tgt.get("note"), alert.get("invalidation")]
    quotes = [q for f in fields if isinstance(f, str) for q in QUOTED.findall(f)]
    errs = ["quote not in transcript: " + q for q in quotes if _norm(q) not in body]
    if not quotes:
        errs.append("no analyst quote to verify")
    return errs


def to_candidate(alert):
    return {
        "cand_id": "cbp:" + alert["id"],
        "origin": "CBP",
        "status": "CANDIDATE_UNTESTED",
        "order_eligible": False,
        "asset": alert["asset"],
        "direction": alert["direction"],
        "entry_trigger": alert["entry_trigger"],
        "target": alert["target"],
        "invalidation": alert["invalidation"],
        "stop_loss": alert.get("stop_loss"),
        "expires_at": alert["expires_at"],
        "queued_at": alert["queued_at"],
        "source": alert["source"],
        "ingested_at": consumer.now_utc().isoformat().replace("+00:00", "Z"),
    }


def ingest(queue_dir, out_dir=DEFAULT_OUT, transcript_dir=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "cbp_candidates.jsonl"
    seen = set()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            seen = {json.loads(l)["cand_id"] for l in f if l.strip()}

    def emit(alert):
        c = to_candidate(alert)
        if c["cand_id"] in seen:
            return
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
        seen.add(c["cand_id"])

    check = validate if transcript_dir is None else (lambda a: validate(a) or quote_errors(a, transcript_dir))
    return consumer.consume(queue_dir, validate=check, on_consume=emit)


if __name__ == "__main__":
    # One command a session can run (no scheduler): python queue/cbp_adapter.py --verify-quotes [queue] [out]
    args = [a for a in sys.argv[1:] if a != "--verify-quotes"]
    tdir = DEFAULT_TRANSCRIPTS if "--verify-quotes" in sys.argv else None
    q = Path(args[0]) if args else consumer.DEFAULT_QUEUE
    o = Path(args[1]) if len(args) > 1 else DEFAULT_OUT
    print(json.dumps(ingest(q, o, tdir), indent=2))
