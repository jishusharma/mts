import sys; sys.dont_write_bytecode = True
"""test_aibridge_pacing.py - the DeepSeek block guard (card dsa-bridge-avoid-deepseek-block-1108, DSA_BLOCK_REVIEW.md rank 1).

DeepSeek suspended the AWGP profile until 2026-11-11 after the bridge sent 205 auto runs on 2026-11-07 (peak 45 an hour, median
16 s between auto runs, 43 gaps under 10 s, one account on three machines). This replays that day's shape through the pacing guard
in scripts/aibridge/extension/loop.js (run by node): no accepted post closer than 20 s + the 5 s jitter floor, no hour over 30,
no day over 200, every refused post says paced (0.7.34 caps; 0.7.33 had 60 s, 15, 80). It fails on 0.7.32, which has no guard (L.paceReplay does not exist).

The replay timestamps are rebuilt from the audit counts in DSA_BLOCK_REVIEW.md section 2 (205 rows in 13 h, hourly counts below,
peak 45), not copied from audit.jsonl: that file is runtime data and stays out of the public repo.
"""
import json
import os
import random
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
LOOP = ROOT / "scripts" / "aibridge" / "extension" / "loop.js"
DAY0_MS = 1794009600000          # 2026-11-07T00:00:00Z
HOURLY = [8, 12, 45, 30, 22, 18, 14, 12, 10, 16, 8, 6, 4]   # 205 rows over 13 hours, peak 45


def audit_shape_2026_11_07():
    """205 epoch-ms timestamps shaped like the 11-07 audit: bursts of 3-5 posts, short gaps inside a burst."""
    rng = random.Random(20261107)
    out = []
    for h, n in enumerate(HOURLY):
        t = DAY0_MS + (8 + h) * 3600000 + rng.randint(0, 60000)
        left = n
        while left > 0:
            for _ in range(min(left, rng.randint(3, 5))):
                out.append(t)
                left -= 1
                t += int(rng.choice([rng.uniform(3, 9), rng.uniform(12, 30)]) * 1000)
            t += int((3600000 / max(n, 1)) * rng.uniform(1.5, 3.0))
            if t > DAY0_MS + (9 + h) * 3600000:
                t = DAY0_MS + (8 + h) * 3600000 + rng.randint(0, 3000000)
    out = sorted(out)[:205]
    assert len(out) == 205
    return out


def test_fixture_has_the_shape_of_the_block_day():
    ts = audit_shape_2026_11_07()
    gaps = [b - a for a, b in zip(ts, ts[1:])]
    assert len(ts) == 205
    assert sum(1 for g in gaps if g < 10000) >= 43
    per_hour = {}
    for t in ts:
        per_hour[t // 3600000] = per_hour.get(t // 3600000, 0) + 1
    assert max(per_hour.values()) > 30   # over the guard's 30 an hour


def replay(ts, seed=7):
    js = ("const L=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{"
          "let x=7+0*1;const seed=Number(process.argv[2]);let a=seed>>>0;"
          "const rand=()=>{a=(a*1664525+1013904223)>>>0;return a/4294967296;};"
          "process.stdout.write(JSON.stringify(L.paceReplay(JSON.parse(s),rand)));});")
    r = subprocess.run(["node", "-e", js, str(LOOP), str(seed)], input=json.dumps(ts), capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_replay_of_the_2026_11_07_audit_is_paced():
    ts = audit_shape_2026_11_07()
    res = replay(ts)
    granted = res["granted"]
    refused = res["refused"]
    assert len(granted) + len(refused) == 205
    assert granted, "the guard must let some posts through"
    gaps = [b - a for a, b in zip(granted, granted[1:])]
    assert all(g >= 20000 + 5000 for g in gaps), "no accepted post closer than 20 s + the 5 s jitter floor: %r" % min(gaps)
    for i, g in enumerate(granted):
        assert sum(1 for x in granted[: i + 1] if g - x < 3600000) <= 30, "hour over 30"
        assert sum(1 for x in granted[: i + 1] if g - x < 86400000) <= 200, "day over 200"
    assert len(granted) <= 200
    assert refused and all(r["reason"] == "paced" for r in refused)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_replay_with_other_jitter_seeds_holds_the_same_limits():
    ts = audit_shape_2026_11_07()
    for seed in (1, 99, 4242):
        granted = replay(ts, seed)["granted"]
        assert all(b - a >= 25000 for a, b in zip(granted, granted[1:]))
        assert len(granted) <= 200
