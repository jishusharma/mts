"""Tests for host_health.py (2026-10-20 ship stalls): synthetic process snapshots, no real process is touched."""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import host_health as h  # noqa: E402

NOW = 1_000_000.0


def P(pid, ppid, name, cmd="", age=10_000, cpu=1.0):
    return {"pid": pid, "ppid": ppid, "name": name, "cmd": cmd or name, "created": NOW - age, "cpu": cpu}


def env(monkeypatch, tmp_path):
    monkeypatch.setenv("MTS_HOST_HEALTH_DIR", str(tmp_path / "hh"))
    monkeypatch.setenv("MTS_GATE_SLOTS_DIR", str(tmp_path / "slots"))


def test_orphan_gate_found_and_live_ones_spared():
    procs = [P(1, 0, "claude.exe"), P(2, 1, "bash.exe"), P(3, 2, "python.exe", "python run_all_tests.py --quick"),      # live: claude above
             P(10, 99, "python.exe", "python scripts/dev/run_all_tests.py --quick"),                                      # parent gone
             P(11, 10, "python.exe", "python run_all_tests.py step"),                                                      # child of the orphan
             P(20, 21, "python.exe", "python run_all_tests.py"), P(21, 99, "python.exe", "python scripts/dev/sync.py ship"),  # live ship above
             P(30, 99, "python.exe", "python run_all_tests.py --root C:/x/.mts_live"),                                     # live tree
             P(40, 99, "python.exe", "python run_all_tests.py", age=30)]                                                   # too young
    assert [p["pid"] for p in h.find_orphan_gates(procs, NOW, me=9999)] == [10]


def test_run_reaps_only_orphan(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    killed = []
    procs = [P(10, 99, "python.exe", "python run_all_tests.py"), P(3, 1, "python.exe", "python run_all_tests.py"), P(1, 0, "claude.exe")]
    lines = h.run(str(tmp_path), procs=procs, kill=lambda pid: killed.append(pid) or True, now=NOW, post=False)
    assert killed == [10] and any("REAPED gate tree PID 10" in ln for ln in lines)
    killed.clear()
    h.run(str(tmp_path), procs=procs, kill=lambda pid: killed.append(pid) or True, now=NOW, reap=False, post=False)
    assert killed == []


def test_dead_owner_tickets_and_slots(tmp_path):
    d = tmp_path / "q"
    d.mkdir()
    (d / "a.json").write_text(json.dumps({"pid": 111, "t": NOW}))
    (d / "b.json").write_text(json.dumps({"pid": 222, "t": NOW}))      # alive, started before the ticket
    (d / "c.json").write_text(json.dumps({"pid": 333, "t": NOW}))      # alive but a younger process: PID reuse
    (d / "slot-0").write_text("111")
    (d / "half.json").write_text("{")
    alive = lambda pid: pid != 111
    start = {222: NOW - 500, 333: NOW + 500}.get
    got = {(p.name, why) for p, _, why in h.dead_owner_files(d, NOW, alive=alive, started=start)}
    assert got == {("a.json", "owner dead"), ("slot-0", "owner dead"), ("c.json", "PID reused by a younger process")}


def test_run_removes_dead_ticket(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    import sync
    d = sync.host_gate_slots_dir("ship-queue", str(tmp_path))
    t = d / "1-999999999.json"
    t.write_text(json.dumps({"pid": 999999999, "t": time.time()}))
    h.run(str(tmp_path), procs=[], kill=lambda p: True, post=False)
    assert not t.exists()


def test_strays_reported_with_stop_command_not_killed():
    procs = [P(1, 0, "claude.exe", age=30 * 3600), P(2, 1, "bash.exe", age=20 * 3600), P(21216, 2, "python.exe", "python vp.py", age=13 * 3600, cpu=37000),
             P(6760, 99, "python.exe", "python audit_rotation.py --t0", age=22 * 3600, cpu=60000),
             P(21440, 1, "wscript.exe", "wscript launch-audit-rotation.vbs", age=6 * 3600),
             P(24056, 21440, "python.exe", "python audit_rotation.py", age=5 * 3600, cpu=9000),
             P(5, 99, "python.exe", "python live_runner_cli.py", cpu=99999), P(6, 99, "svchost.exe", cpu=99999),
             P(7, 99, "python.exe", "python x.py", age=60, cpu=99999), P(8, 99, "python.exe", "python small.py", cpu=10)]
    got = {s["pid"]: s for s in h.find_strays(procs, NOW, me=9999)}
    assert set(got) == {21216, 6760, 24056}
    assert got[21216]["stop"] == "taskkill /PID 21216 /T /F" and "bash.exe[2]" in got[21216]["chain"]
    assert got[24056]["stop"] == "taskkill /PID 24056 /PID 21440 /T /F"
    assert "parent gone" in got[6760]["chain"]


def test_policy_allow_list_gates_the_kill(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    procs = [P(21216, 99, "python.exe", "python vp.py", age=13 * 3600, cpu=37000)]
    (tmp_path / "MyTradingSys/system").mkdir(parents=True)
    pol = tmp_path / h.POLICY_REL
    pol.write_text(h.POLICY_TEXT)
    assert h.parse_policy(h.POLICY_TEXT) == []            # shipped policy: empty allow-list
    killed = []
    out = h.run(str(tmp_path), procs=procs, kill=lambda p: killed.append(p) or True, now=NOW, post=False)
    assert killed == [] and any("stop: taskkill /PID 21216" in ln for ln in out)
    pol.write_text(h.POLICY_TEXT + "- allow: python VP.py\n")
    out = h.run(str(tmp_path), procs=procs, kill=lambda p: killed.append(p) or True, now=NOW, post=False)
    assert killed == [21216] and any("REAPED stray PID 21216" in ln for ln in out)


def test_shipped_policy_file_has_empty_allow_list():
    repo = Path(__file__).resolve().parents[2]
    assert h.parse_policy((repo / h.POLICY_REL).read_text(encoding="utf-8")) == []


def test_protected_never_a_stray():
    procs = [P(5, 99, "python.exe", "python live_runner_cli.py", age=99999, cpu=99999)]
    assert h.find_strays(procs, NOW, me=9999) == []


def test_disk_warn_prunes_only_own_prefixes(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    temp = tmp_path / "tmp"
    for n in ("mts_s4_a", "mts_changed_b", "mts_gate_slots", "other_big", "mts_s4_fresh"):
        (temp / n).mkdir(parents=True)
        (temp / n / "f").write_bytes(b"x" * 100)
    now = time.time()
    old = now - 3 * 86400
    for n in ("mts_s4_a", "mts_changed_b", "mts_gate_slots", "other_big"):
        os.utime(temp / n, (old, old))
    lines, freed = h.check_disk(str(tmp_path), temp=temp, now=now, free=3.0)
    assert {p.name for p in temp.iterdir()} == {"mts_gate_slots", "other_big", "mts_s4_fresh"} and freed > 0
    assert any("DISK WARN" in ln and "3.0 GB free" in ln for ln in lines) and any("largest in temp" in ln for ln in lines)


def test_disk_ok_is_silent_and_growth_warns(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    assert h.check_disk(str(tmp_path), temp=tmp_path, now=NOW, free=500.0)[0] == []
    lines, _ = h.check_disk(str(tmp_path), temp=tmp_path, now=NOW + 3600, free=490.0)   # 10 GB in 1 h, still above the threshold
    assert any("falling 10.0 GB/h" in ln for ln in lines)


def test_queue_warn_names_top_consumers():
    a = [P(1, 0, "a.exe", cpu=0), P(2, 0, "b.exe", cpu=0)]
    b = [P(1, 0, "a.exe", cpu=1.0), P(2, 0, "b.exe", cpu=30.0)]
    snaps = iter([a, b])
    out = h.check_queue(ncpu=8, qlen=102, snap=lambda: next(snaps), sleep=lambda s: None)
    assert len(out) == 1 and out[0].index("b.exe[2]") < out[0].index("a.exe[1]") and "102 > 4 x 8" in out[0]
    assert h.check_queue(ncpu=8, qlen=32, snap=lambda: [], sleep=lambda s: None) == []


def test_errors_never_block(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    monkeypatch.setattr(h, "run", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert h.run_safe(str(tmp_path)) == []
    assert "boom" in (tmp_path / "hh" / "health.log").read_text()


def test_one_part_failing_does_not_stop_the_others(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    monkeypatch.setattr(h, "check_disk", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("disk")))
    monkeypatch.setattr(h, "check_queue", lambda *a, **k: [])
    out = h.run(str(tmp_path), procs=[P(10, 99, "python.exe", "python run_all_tests.py")], kill=lambda p: True, now=NOW, post=False)
    assert any("REAPED gate tree PID 10" in ln for ln in out)
    assert "disk error" in (tmp_path / "hh" / "health.log").read_text()


def test_sync_ship_and_health_call_the_preflight(monkeypatch):
    import sync
    seen = []
    monkeypatch.setattr(sync, "run_host_health", lambda repo: seen.append(repo))
    monkeypatch.setattr(sync, "toplevel_or_none", lambda: "R")
    monkeypatch.setattr(sync, "ship", lambda *a, **k: None)
    monkeypatch.setattr(sync, "health", lambda repo: 0)
    monkeypatch.setattr(sync, "toplevel", lambda p: "R")
    monkeypatch.setattr(sync, "lease_guard", lambda argv: None)
    assert sync.main(["ship"]) == 0 and sync.main(["health"]) == 0
    assert seen == ["R", "R"]


def test_sync_run_host_health_swallows_errors(monkeypatch, tmp_path):
    import sync
    (tmp_path / "scripts" / "dev").mkdir(parents=True)
    (tmp_path / "scripts" / "dev" / "host_health.py").write_text("")
    monkeypatch.setattr(h, "run_safe", lambda repo: (_ for _ in ()).throw(RuntimeError("x")))
    assert sync.run_host_health(str(tmp_path)) == []


def test_sync_skips_host_health_in_throwaway_repo(monkeypatch, tmp_path):
    import sync
    monkeypatch.setattr(h, "run_safe", lambda repo: (_ for _ in ()).throw(AssertionError("scanned the host from a scratch repo")))
    assert sync.run_host_health(str(tmp_path)) == []
