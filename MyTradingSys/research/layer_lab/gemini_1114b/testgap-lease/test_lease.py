"""Unit tests for scripts/dev/lease.py.

Mutation test record (Step 3):
Mutated copy created in scratch file with flipped branch:
  File: scripts/dev/lease.py:291
  Original:
    if now < float(d["expires"]) + SKEW:
        return "held"
  Mutated:
    if now >= float(d["expires"]) + SKEW:
        return "held"
Resulting failure when pointed at mutated copy:
  test_classify_held_by_other_within_skew failed with:
    AssertionError: assert 'expired' == 'held'
      - held
      + expired
"""
import sys
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[5]
DEV = REPO / "scripts" / "dev"
sys.path.insert(0, str(DEV))

import lease


def test_slug_normal():
    # SOURCED: return re.sub(r"[^a-z0-9]+", "_", role.lower()).strip("_") (scripts/dev/lease.py:84)
    # OURS: input "Pipeliner", lowercases to "pipeliner", strip "_" produces "pipeliner"
    assert lease.slug("Pipeliner") == "pipeliner"


def test_slug_empty():
    # SOURCED: if not role: return "" (scripts/dev/lease.py:82-83)
    # OURS: empty string input evaluates to falsy and returns ""
    assert lease.slug("") == ""


def test_canon_malformed_raises_lease_error():
    # SOURCED: SINGLETONS = ("Pipeliner",) (scripts/dev/lease.py:47)
    # SOURCED: raise LeaseError(f"{role!r} is not a singleton role ({', '.join(SINGLETONS)})") (scripts/dev/lease.py:97)
    # OURS: "Builder" is not in SINGLETONS, so canon("Builder") raises LeaseError
    with pytest.raises(lease.LeaseError):
        lease.canon("Builder")


def test_classify_held_by_other_within_skew():
    # SOURCED: SKEW = 5 * 60 (scripts/dev/lease.py:50)
    # SOURCED: if now < float(d["expires"]) + SKEW: return "held" (scripts/dev/lease.py:291-292)
    # OURS: expires = 1700001000, SKEW = 300, cutoff = 1700001000 + 300 = 1700001300. With now = 1700001200 < 1700001300, returns "held"
    d = {"state": "held", "holder": {"key": "OTHER/s2"}, "expires": 1700001000}
    assert lease.classify(d, now=1700001200, key="HOST/s1") == "held"


def test_classify_expired_by_other_past_skew():
    # SOURCED: SKEW = 5 * 60 (scripts/dev/lease.py:50)
    # SOURCED: if now < float(d["expires"]) + SKEW: return "held" (scripts/dev/lease.py:291-292)
    # SOURCED: return "expired" (scripts/dev/lease.py:293)
    # OURS: expires = 1700001000, SKEW = 300, cutoff = 1700001000 + 300 = 1700001300. With now = 1700001350 >= 1700001300, returns "expired"
    d = {"state": "held", "holder": {"key": "OTHER/s2"}, "expires": 1700001000}
    assert lease.classify(d, now=1700001350, key="HOST/s1") == "expired"


def test_classify_released_returns_free():
    # SOURCED: if d is None or d.get("state") == "released": return "free" (scripts/dev/lease.py:287-288)
    # OURS: dict with state="released" returns "free"
    assert lease.classify({"state": "released"}, now=1700001000, key="HOST/s1") == "free"


def test_runner_env_normal():
    # SOURCED: re.search(r"(?i)\b(?:you are|act as|acting as|role\s*[:=])\s+(?:the\s+)?" + re.escape(r) + r"\b", text or "") (scripts/dev/lease.py:152)
    # SOURCED: return {"MTS_ROLE": found, "MTS_LEASE_SESSION": str(run_id)} if found else {} (scripts/dev/lease.py:154)
    # OURS: "You are the Pipeliner for this task" matches singleton "Pipeliner", run_id 42 converts to string "42"
    assert lease.runner_env("You are the Pipeliner for this task", 42) == {"MTS_ROLE": "Pipeliner", "MTS_LEASE_SESSION": "42"}


def test_runner_env_bare_mention_returns_empty():
    # SOURCED: re.search(r"(?i)\b(?:you are|act as|acting as|role\s*[:=])\s+(?:the\s+)?" + re.escape(r) + r"\b", text or "") (scripts/dev/lease.py:152)
    # OURS: bare mention without role prefix does not match, returns empty dict {}
    assert lease.runner_env("Check pipeliner logs", 42) == {}


def test_local_state_malformed_returns_none(tmp_path, monkeypatch):
    # SOURCED: try: return json.loads((home() / f"{slug(role)}.json").read_text(encoding="utf-8")) except Exception: return None (scripts/dev/lease.py:221-224)
    # SOURCED: Path(_env("MTS_LEASE_HOME") or Path.home() / ".claude" / "mts-leases") (scripts/dev/lease.py:130)
    # OURS: malformed JSON content "{unclosed" causes json.loads to raise JSONDecodeError, returning None
    monkeypatch.setenv("MTS_LEASE_HOME", str(tmp_path))
    (tmp_path / "pipeliner.json").write_text("{unclosed", encoding="utf-8")
    assert lease.local_state("Pipeliner") is None
