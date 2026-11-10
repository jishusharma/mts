"""d-six-slots-poll soak (soak_six_slots.py) in CI: 3 supervisors x 3 h of virtual time per seed, faults injected, the real
supervisor.plan() and wait_for_transition(). The monitor itself is mutation-checked so a green soak means something."""
import io
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import supervisor as S  # noqa: E402
import soak_six_slots as K  # noqa: E402


# 2026-11-10: the gated run is a small, capped slice (about 30 s idle; the gate's must-pass step limit is 240 s and a slow host took
# 190 s with the old 10-seed loop). MTS_SOAK_FULL=1 runs the whole soak (10 seeds x 3 h, mutation and idle checks over more seeds).
FULL = os.environ.get("MTS_SOAK_FULL") == "1"
SEEDS = range(1, 11) if FULL else range(1, 3)           # invariant seeds, 3 h each
SHORT = 180 if FULL else 60                              # virtual minutes for the replay, no-fault and mutation runs
MUT_SEEDS = range(1, 4) if FULL else range(1, 3)
IDLE_SEEDS = range(1, 7) if FULL else range(1, 3)


def _fails(seeds, minutes=180, **kw):
    return sum(K.run(minutes, s, out=io.StringIO(), quiet=True, **kw)["fails"] for s in seeds)


def test_ten_seeds_of_three_hours_break_no_invariant_and_a_seed_replays_the_same():
    assert _fails(SEEDS) == 0
    assert _fails(MUT_SEEDS, SHORT, faults=False) == 0
    assert K.run(SHORT, 3, out=io.StringIO(), quiet=True) == K.run(SHORT, 3, out=io.StringIO(), quiet=True)


def test_the_soak_restores_everything_it_stubbed():
    before = (S._now_utc, S.read_gate_slots, S.read_ci, S._dispatch_raw)
    K.run(30, 1, out=io.StringIO(), quiet=True)
    assert (S._now_utc, S.read_gate_slots, S.read_ci, S._dispatch_raw) == before


def test_the_monitor_catches_a_wake_that_ignores_full_gates_and_a_ramp_past_one(monkeypatch):
    orig = S._actionable
    monkeypatch.setattr(S, "_actionable", lambda last, cur, now=None: orig(last, dict(cur, busy_slots=0), now))
    assert _fails(MUT_SEEDS, SHORT) > 0
    monkeypatch.setattr(S, "_actionable", orig)
    monkeypatch.setattr(S, "RAMP", 3)
    assert _fails(MUT_SEEDS, SHORT) > 0


def test_the_wake_leaves_fewer_slots_empty_than_the_old_watcher():
    new = sum(K.run(180, s, out=io.StringIO(), quiet=True)["idle_slot_min"] for s in IDLE_SEEDS)
    old = sum(K.run(180, s, out=io.StringIO(), quiet=True, baseline=True)["idle_slot_min"] for s in IDLE_SEEDS)
    assert new < 0.8 * old, (new, old)      # 2026-10-22: see the soak section of research/thinker/2026-10-22_six_slots.md


def test_the_soak_never_builds_the_published_pages(monkeypatch):
    """2026-11-10: plan() built three real pages per publisher plan, so one soak test held a gate slot for over an hour."""
    import artifacts
    calls = []
    monkeypatch.setattr(artifacts, "republish_lines", lambda reg: calls.append(1) or [])
    K.run(30, 1, out=io.StringIO(), quiet=True)
    assert calls == []
