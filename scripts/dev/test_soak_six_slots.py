"""d-six-slots-poll soak (soak_six_slots.py) in CI: 3 supervisors x 3 h of virtual time per seed, faults injected, the real
supervisor.plan() and wait_for_transition(). The monitor itself is mutation-checked so a green soak means something."""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import supervisor as S  # noqa: E402
import soak_six_slots as K  # noqa: E402


def _fails(seeds, **kw):
    return sum(K.run(180, s, out=io.StringIO(), quiet=True, **kw)["fails"] for s in seeds)


def test_ten_seeds_of_three_hours_break_no_invariant_and_a_seed_replays_the_same():
    assert _fails(range(1, 11)) == 0
    assert _fails(range(1, 4), faults=False) == 0
    assert K.run(180, 3, out=io.StringIO(), quiet=True) == K.run(180, 3, out=io.StringIO(), quiet=True)


def test_the_soak_restores_everything_it_stubbed():
    before = (S._now_utc, S.read_gate_slots, S.read_ci, S._dispatch_raw)
    K.run(30, 1, out=io.StringIO(), quiet=True)
    assert (S._now_utc, S.read_gate_slots, S.read_ci, S._dispatch_raw) == before


def test_the_monitor_catches_a_wake_that_ignores_full_gates_and_a_ramp_past_one(monkeypatch):
    orig = S._actionable
    monkeypatch.setattr(S, "_actionable", lambda last, cur, now=None: orig(last, dict(cur, busy_slots=0), now))
    assert _fails(range(1, 4)) > 0
    monkeypatch.setattr(S, "_actionable", orig)
    monkeypatch.setattr(S, "RAMP", 3)
    assert _fails(range(1, 4)) > 0


def test_the_wake_leaves_fewer_slots_empty_than_the_old_watcher():
    new = sum(K.run(180, s, out=io.StringIO(), quiet=True)["idle_slot_min"] for s in range(1, 7))
    old = sum(K.run(180, s, out=io.StringIO(), quiet=True, baseline=True)["idle_slot_min"] for s in range(1, 7))
    assert new < 0.8 * old, (new, old)      # 2026-10-22: see the soak section of research/thinker/2026-10-22_six_slots.md
