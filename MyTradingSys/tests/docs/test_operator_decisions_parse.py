"""Every ```json block in OPERATOR_DECISIONS.md parses; ids and orders are unique (seed-from-file contract)."""
import collections
import json
import re
from pathlib import Path

F = Path(__file__).resolve().parents[2] / "system" / "OPERATOR_DECISIONS.md"
BLOCK = re.compile(r"```json\n(.*?)\n```", re.S)


def _docs():
    text = F.read_text(encoding="utf-8")
    out = []
    for m in BLOCK.finditer(text):
        line = text[: m.start()].count("\n") + 1
        out.append((line, m.group(1)))
    return out


def test_every_json_block_parses():
    bad = []
    for line, body in _docs():
        try:
            json.loads(body)
        except ValueError as e:
            bad.append(f"line {line}: {e}")
    assert not bad, bad


def test_ids_and_orders_unique():
    ids, orders = collections.Counter(), collections.Counter()
    for _, body in _docs():
        d = json.loads(body)
        if "id" in d:
            ids[d["id"]] += 1
        if "order" in d and d["order"] >= 46:  # blocks before 46 are the old hand-numbered format
            orders[d["order"]] += 1
    assert [k for k, v in ids.items() if v > 1] == []
    assert [k for k, v in orders.items() if v > 1] == []


def test_voice_rule_in_reply_and_role_docs():
    """bug-headless-wake-voice-misread: dictated 'cloud' = Claude, answer the question asked."""
    base = F.parent
    for rel in ("OPERATOR_REPLY_FORMAT.md", "roles/supervisor.md", "roles/builder.md"):
        t = (base / rel).read_text(encoding="utf-8")
        assert 'dictated "cloud"' in t and "means Claude" in t, rel
