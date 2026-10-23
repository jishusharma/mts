"""Soak test for d-six-slots-poll (option A wake + option C idle line): three supervisors on three machines run the REAL
supervisor.plan() and supervisor.wait_for_transition() for hours against a simulated world (workers of 20 min to 3 h, gates,
CI, card queue, 5 h / weekly budget), with faults injected and every plan and wake checked against invariants as it happens.

Nothing real is touched: no git, no signal branch, no sessions; state files go to a temp dir. Reads are stubbed per machine.
  python scripts/dev/soak_six_slots.py                    3 h of virtual time in seconds (fake clock), seed 1
  python scripts/dev/soak_six_slots.py --seeds 1-20       the same over 20 seeds (summary per seed)
  python scripts/dev/soak_six_slots.py --real             3 h of wall-clock time (real sleeps, 5 min polls), log as it goes
  python scripts/dev/soak_six_slots.py --baseline         the same world with the old watcher (no --login): ramp-up compared
Exit 0 = no invariant broken. The log lines `FAIL` name each break.
"""
import argparse
import json
import random
import shutil
import sys
import tempfile
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import supervisor as S  # noqa: E402

UTC = timezone.utc
MACHINES = {"A": "DESKTOP-F7IU69N", "B": "JIS-NB", "C": "JIS-NUC"}
INV = {"machines": {"DESKTOP-F7IU69N": {"logins": ["A", "B", "C"]}, "JIS-NB": {"logins": ["B", "C"]},
                    "JIS-NUC": {"logins": ["A", "C"]}}}
GATES = 2
SHIP_MIN = 8            # a worker holds a gate this long at its end
AGENT_MIN = 2           # a supervisor's turn between a wake and its watcher (plan + spawn)
SPAWN_MIN = 3           # a spawned worker starts this long after the plan
STUCK_RULE = 2          # d-six-slots-poll: the wake is off after 2 plans in a row that started none (checked against this, not S.STUCK_MAX)
RAMP_RULE = 1           # operator 2026-10-22 "starts with minimum workers": checked against this, never against S.RAMP (a bug there must show)


class VClock:
    """Discrete-event clock for threads: time jumps to the earliest wake only when every thread sleeps."""
    def __init__(self, t0):
        self.t, self.cv, self.waiting, self.active = t0, threading.Condition(), {}, 0

    def now(self):
        return self.t

    def join(self):
        with self.cv:
            self.active += 1

    def leave(self):
        with self.cv:
            self.active -= 1
            self._advance()

    def sleep(self, s):
        me = threading.current_thread().name
        with self.cv:
            self.waiting[me] = self.t + timedelta(seconds=s)
            self.active -= 1
            self._advance()
            while me in self.waiting:
                self.cv.wait()

    def _advance(self):
        """Release ONE thread (earliest wake, then name): threads due at the same instant run one after another in a fixed order,
        so a seed always replays the same run (review 2026-10-22: order by OS scheduling made results differ per run)."""
        if self.active == 0 and self.waiting:
            k = min(self.waiting, key=lambda n: (self.waiting[n], n))
            self.t = max(self.t, self.waiting.pop(k))
            self.active += 1
            self.cv.notify_all()


class RClock:
    def __init__(self, t0=None):
        pass

    def now(self):
        return datetime.now(UTC)

    def join(self):
        pass

    def leave(self):
        pass

    def sleep(self, s):
        time.sleep(s)


class World:
    def __init__(self, clock, t0, rng, faults=True):
        self.clock, self.t0, self.rng, self.faults = clock, t0, rng, faults
        self.lock = threading.RLock()
        self.cards = {h: [{"id": f"{h[:3].lower()}-{i}", "lane": "SONNET"} for i in range(n)]
                      for h, n in (("DESKTOP-F7IU69N", 12), ("JIS-NB", 8), ("JIS-NUC", 10))}
        self.workers = []           # {login, host, start, end, card}
        self.signals = []           # (dt, sender, kind, text)
        self.five = {"A": 40.0, "B": 10.0, "C": 5.0}
        self.week = {"A": 60.0, "B": 40.0, "C": 20.0}
        self.five_reset = {lg: t0 + timedelta(hours=h) for lg, h in (("A", 2.5), ("B", 4.5), ("C", 3.5))}
        self.week_reset = t0 + timedelta(days=3)
        self.foreign = {h: [] for h in MACHINES.values()}      # other sessions' gate use: (start, end)
        if faults:      # both gates of two machines busy for the first 25 min (other sessions shipping): no wake may fire then
            for h in ("DESKTOP-F7IU69N", "JIS-NB"):
                self.foreign[h] += [(t0, t0 + timedelta(minutes=25))] * 2
        for h in self.foreign:
            for _ in range(4):
                s = t0 + timedelta(minutes=rng.uniform(0, 180))
                self.foreign[h].append((s, s + timedelta(minutes=rng.uniform(3, 10))))
        self.last = t0

    def m(self, t=None):
        return ((t or self.clock.now()) - self.t0).total_seconds() / 60

    def update(self):
        now = self.clock.now()
        dt_h = (now - self.last).total_seconds() / 3600
        if dt_h > 0:
            for lg in self.five:
                run = self.running(lg, now)
                add = (4.0 * run + 1.0) * dt_h
                self.five[lg] += add
                self.week[lg] += 0.12 * add
                if now >= self.five_reset[lg]:
                    self.five[lg], self.five_reset[lg] = 0.0, self.five_reset[lg] + timedelta(hours=5)
            self.last = now

    def running(self, login, now=None):
        now = now or self.clock.now()
        return sum(1 for w in self.workers if w["login"] == login and w["start"] <= now < w["end"])

    def ci_red(self):
        return self.faults and any(a <= self.m() < b for a, b in ((60, 85), (118, 128), (150, 165), (240, 255)))

    def busy(self, host):
        now = self.clock.now()
        own = sum(1 for w in self.workers if w["host"] == host and w["end"] - timedelta(minutes=SHIP_MIN) <= now < w["end"])
        frn = sum(1 for s, e in self.foreign[host] if s <= now < e)
        return min(GATES, own + frn)

    def rd(self, login):
        self.update()
        return {"five": round(self.five[login], 1), "week": round(self.week[login], 1),
                "five_reset": self.five_reset[login].strftime("%Y-%m-%dT%H:%MZ"), "week_reset": self.week_reset.strftime("%Y-%m-%dT%H:%MZ")}

    def start(self, login, host, card, dur_min):
        s = self.clock.now() + timedelta(minutes=SPAWN_MIN)
        self.workers.append({"login": login, "host": host, "card": card, "start": s, "end": s + timedelta(minutes=dur_min)})
        self.cards[host] = [c for c in self.cards[host] if c["id"] != card]

    def probe(self, host):
        def p(repo, shas):
            with self.lock:
                self.update()
                return {"shas": {}, "ci_red": self.ci_red(), "busy_slots": self.busy(host), "total_slots": GATES}
        return p


class Monitor:
    def __init__(self, out, quiet=False):
        self.out, self.quiet, self.fails, self.lock = out, quiet, [], threading.Lock()
        self.woke_at = {}               # login -> set of plan `at` already woken on
        self.idle_told = {}             # host -> last minute told
        self.wakes = {"ACTIONABLE": 0, "TRANSITION": 0, "TIMEOUT": 0}
        self.plans = 0
        self.samples = []               # (minute, running per login)
        self.allowed = {}               # login -> slots of its last plan
        self.idle_slot_min = 0          # minutes x slots a plan allowed that stood empty with cards ready and CI green
        self.dup_idle = 0               # the idle line for one machine from a second supervisor within IDLE_NAG_H (owner change)
        self.missed = 0                 # poll minutes where a wake was due (the A rule) and none came within 10 min

    def log(self, s):
        if self.quiet and not s.startswith(("SUMMARY", "FAIL", "SOAK", "  ")):
            return
        with self.lock:
            print(s, file=self.out, flush=True)

    def fail(self, m, s):
        self.fails.append(f"T+{m:05.1f} {s}")
        self.log(f"FAIL T+{m:05.1f} {s}")


def run(minutes=180, seed=1, real=False, baseline=False, faults=True, out=sys.stdout, poll_s=300, quiet=False):
    rng = random.Random(seed)
    t0 = datetime.now(UTC).replace(microsecond=0) if real else datetime(2026, 10, 19, 6, 0, tzinfo=UTC)
    clock = RClock() if real else VClock(t0)
    world, mon = World(clock, t0, rng, faults), Monitor(out, quiet)
    tmp = Path(tempfile.mkdtemp(prefix="soak6_"))
    end = t0 + timedelta(minutes=minutes)
    restore = _patch(world, clock, tmp)
    mon.log(f"SOAK seed={seed} {'real' if real else 'virtual'} {minutes} min from {t0:%H:%MZ} baseline={baseline} faults={faults} home={tmp}")

    def sup(login):
        host = MACHINES[login]
        home = tmp / login
        home.mkdir()
        repo = tmp / f"repo-{host}"
        repo.mkdir(exist_ok=True)
        try:
            clock.sleep(0)                      # line up behind the others: the first instant runs in name order too
            if faults and login == "C":
                clock.sleep(90 * 60)            # JIS-NUC has no supervisor for 90 min: the idle line must name it
            slip_done = False
            while clock.now() < end:
                m = world.m()
                if faults and login == "B" and 130 <= m < 136:
                    (home / "B-last-plan.json").write_text("{not json", encoding="utf-8")
                    (home / "B-woke.txt").write_bytes(b"\xff\xfe\x00bad")
                with world.lock:
                    world.update()
                    running = world.running(login)
                    lines, data = S.plan(repo, login, world.rd(login), running=running, send=True, no_fetch=True, host=host,
                                         home=home, now=clock.now())
                    _check_plan(mon, world, login, host, lines, data, running)
                    fail_spawn = faults and login == "B" and 140 <= m < 200
                    for cid in data["picks"][:data["free"]]:
                        if not fail_spawn and rng.random() > 0.15:
                            world.start(login, host, cid, rng.choice([20, 45, 90, 120, 180, 180]))
                clock.sleep(AGENT_MIN * 60)
                rc, why = _watch(world, clock, mon, login, host, repo, home, baseline, poll_s)
                if faults and login == "A" and not slip_done and why.startswith("ACTIONABLE"):
                    slip_done = True        # a watcher restarted without a new plan (compaction, a slip): must not wake on the same plan
                    rc2, why2 = _watch(world, clock, mon, login, host, repo, home, baseline, poll_s, slip=True)
        except Exception:
            mon.fail(world.m(), f"{login} supervisor crashed: {traceback.format_exc()[-400:]}")
        finally:
            with world.lock:
                world.signals.append((clock.now(), login, "note", f"BUDGET login={login} 5h=0% week=0% sup={host} mode=ENDED"))
            clock.leave()

    def sampler():
        try:
            clock.sleep(0)
            while clock.now() < end:
                with world.lock:
                    world.update()
                    mon.samples.append((world.m(), {lg: world.running(lg) for lg in MACHINES}))
                    if not world.ci_red():
                        for lg, h in MACHINES.items():
                            if world.cards[h] and lg in mon.allowed:
                                mon.idle_slot_min += max(0, mon.allowed[lg] - world.running(lg))
                clock.sleep(60)
        finally:
            clock.leave()

    ths = [threading.Thread(target=sup, args=(lg,), name=lg, daemon=True) for lg in MACHINES] + \
          [threading.Thread(target=sampler, name="sampler", daemon=True)]
    for _ in ths:
        clock.join()        # every thread counts as awake before any sleeps: the fake clock never jumps past a late starter
    try:
        for t in ths:
            t.start()
        for t in ths:
            t.join(None if real else 300)
            if t.is_alive():        # a hung clock fails the run instead of hanging CI
                mon.fail(world.m(), f"thread {t.name} still running after the run (clock hung?)")
                break
    finally:
        restore()
        shutil.rmtree(tmp, ignore_errors=True)
    return _summary(mon, world, minutes)


def _watch(world, clock, mon, login, host, repo, home, baseline, poll_s, slip=False):
    started = clock.now()
    last = S._last_plan(login, home)
    try:
        rc, why = S.wait_for_transition(repo=repo, shas=[], timeout=50 * 60, interval=poll_s, probe=world.probe(host),
                                        fetcher=lambda r: None, sleeper=clock.sleep, login=None if baseline else login, home=home)
    except Exception:
        mon.fail(world.m(), f"{login} watcher crashed: {traceback.format_exc()[-300:]}")
        return 9, "crash"
    m, took = world.m(), (clock.now() - started).total_seconds() / 60
    kind = why.split()[0]
    mon.wakes[kind] = mon.wakes.get(kind, 0) + 1
    mon.log(f"T+{m:05.1f} {login} wake {why[:110]} after {took:.0f} min{' (restarted watcher)' if slip else ''}")
    if took > 50.01:
        mon.fail(m, f"{login} watcher ran {took:.1f} min > 50")
    if kind == "ACTIONABLE":
        if int(last.get("spare") or 0) <= 0 or int(last.get("ready_more") or 0) <= 0:
            mon.fail(m, f"{login} ACTIONABLE on a plan with spare={last.get('spare')} ready_more={last.get('ready_more')}")
        with world.lock:
            world.update()
            red, busy = world.ci_red(), world.busy(host)
        at = str(last.get("at"))
        if red:
            mon.fail(m, f"{login} ACTIONABLE while CI red")
        if busy >= GATES:
            mon.fail(m, f"{login} ACTIONABLE with all gates busy")
        if at in mon.woke_at.setdefault(login, set()):
            mon.fail(m, f"{login} second ACTIONABLE on plan {at}")
        mon.woke_at[login].add(at)
        pl = last.get("plan") or {}
        if pl.get("mode") not in ("SPEND", "NORMAL") or int(last.get("stuck") or 0) >= STUCK_RULE:
            mon.fail(m, f"{login} ACTIONABLE on mode={pl.get('mode')} stuck={last.get('stuck')}")
        if baseline:
            mon.fail(m, f"{login} ACTIONABLE in baseline run")
    elif kind == "TIMEOUT" and not baseline and not slip:
        # liveness: a fresh plan with spare slots and ready cards, green CI, a free gate and stuck < STUCK_MAX must wake at the first poll
        pl = last.get("plan") or {}
        due = (pl.get("mode") in ("SPEND", "NORMAL") and int(last.get("spare") or 0) > 0 and int(last.get("ready_more") or 0) > 0
               and int(last.get("stuck") or 0) < S.STUCK_MAX)
        if due and not world.ci_red():
            mon.missed += 1
            mon.log(f"T+{m:05.1f} {login} NOTE timeout on a plan that looked actionable (gates or CI blocked every poll?)")
    return rc, why


def _check_plan(mon, world, login, host, lines, data, running):
    m = world.m()
    mon.plans += 1
    pl = data["plan"]
    mon.allowed[login] = pl["slots"]
    if pl["new"] > RAMP_RULE:
        mon.fail(m, f"{login} plan new={pl['new']} > {RAMP_RULE} (start light)")
    if data["free"] > pl["new"]:
        mon.fail(m, f"{login} free={data['free']} > new={pl['new']}")
    if world.ci_red() and data["free"]:
        mon.fail(m, f"{login} plan told to start {data['free']} worker(s) while CI red")
    live_hosts = {s["host"] for s in data["live"].values()}
    told = [x for x in lines if x.startswith("OPERATOR start a Supervisor on ")]
    for x in told:
        h = x.split(" on ", 1)[1].split(":", 1)[0]
        lg = x.rsplit("Login ", 1)[1].rstrip(".`")
        if h in live_hosts:
            mon.fail(m, f"{login} told operator to start a Supervisor on {h}, which has a live one")
        if lg in data["live"]:
            mon.fail(m, f"{login} offered login {lg} that already runs a supervisor")
        # the IDLE_NAG_H stamp is per supervisor (its own machine): the same supervisor never repeats it within IDLE_NAG_H; when the
        # lane owner changes (a lower login boots) the new owner may say it once more (known, accepted 2026-10-22: one extra line)
        prev = mon.idle_told.get((login, h))
        if prev is not None and m - prev < S.IDLE_NAG_H * 60:
            mon.fail(m, f"{login} idle line for {h} again after {m - prev:.0f} min")
        others = [k for k in mon.idle_told if k[1] == h and k[0] != login and m - mon.idle_told[k] < S.IDLE_NAG_H * 60]
        if others:
            mon.dup_idle += 1
        mon.idle_told[(login, h)] = m
        if S.lane_owner(data["live"]) != login:
            mon.fail(m, f"{login} printed the idle line but is not the lane owner")
    offered = [x.rsplit("Login ", 1)[1].rstrip(".`") for x in told]
    if len(offered) != len(set(offered)):
        mon.fail(m, f"{login} offered one login for two machines: {offered}")
    mon.log(f"T+{m:05.1f} {login} plan mode={pl['mode']} 5h={pl['five']:.0f} slots={pl['slots']} run={running} new={pl['new']} "
            f"free={data['free']} spare={data['spare']} ready_more={data['ready_more']} stuck={data['stuck']} gates={world.busy(host)}/{GATES}"
            f"{' CI-RED' if world.ci_red() else ''}" + "".join(f" | {x[:60]}" for x in told))


def _patch(world, clock, tmp):
    """Stub every read of supervisor/traffic/mts_signal for this world; returns a function that puts all of it back."""
    import os
    import traffic
    import mts_signal
    saved = [(mod, name, getattr(mod, name)) for mod, names in (
        (S, ("_now_utc", "read_gate_slots", "fetch_origin", "read_ci", "_git_show", "_local_bridge", "nuc_budget_ok", "_dispatch_raw")),
        (mts_signal, ("send",)), (traffic, ("read_signals", "refresh_signals", "budget_view", "inv_cache"))) for name in names]
    env = os.environ.get("MTS_RELAY_HOME")

    def restore():
        for mod, name, val in saved:
            setattr(mod, name, val)
        if env is None:
            os.environ.pop("MTS_RELAY_HOME", None)
        else:
            os.environ["MTS_RELAY_HOME"] = env
    host_of = lambda repo: Path(repo).name.split("repo-", 1)[-1]
    S._now_utc = clock.now
    S.read_gate_slots = lambda repo=None: {"busy": world.busy(host_of(repo)), "total": GATES, "free": GATES - world.busy(host_of(repo))}
    S.fetch_origin = lambda repo=None: None
    S.read_ci = lambda now=None, use_cache=False: {"red": world.ci_red(), "message": "soak"}
    S._git_show = lambda repo, rel: None
    S._local_bridge = lambda host: None
    S.nuc_budget_ok = lambda *a, **k: False
    S._dispatch_raw = lambda repo, as_of, host=None, login=None, logins=None: {"dispatch": list(world.cards[host_of(repo)])}

    def send(text, to="all", kind="note", **k):
        world.signals.append((clock.now(), "soak", kind, text))
        return True

    def read_signals(since, until, d=None):
        return [r for r in world.signals if since <= r[0] <= until], None

    def budget_view(do_fetch=True, now=None, hours=48):
        now = now or clock.now()
        world.update()
        view = {"logins": {lg: {"state": "SPEND" if world.five[lg] < 60 else "THROTTLE", "at": now.strftime("%Y-%m-%dT%H:%MZ"),
                                "week": world.week[lg], "reset": world.week_reset.strftime("%Y-%m-%dT%H:%MZ")} for lg in MACHINES}}
        return view, []
    mts_signal.send = send
    traffic.read_signals = read_signals
    traffic.refresh_signals = lambda *a, **k: None
    traffic.budget_view = budget_view
    traffic.inv_cache = lambda: INV
    os.environ["MTS_RELAY_HOME"] = str(tmp / "relay")
    return restore


def _summary(mon, world, minutes):
    per = {lg: [s[1][lg] for s in mon.samples] for lg in MACHINES}
    avg = {lg: round(sum(v) / max(1, len(v)), 2) for lg, v in per.items()}
    first = {}
    for lg in MACHINES:
        for mm, r in mon.samples:
            if r[lg] >= 2:
                first[lg] = round(mm)
                break
    used = sum(1 for w in world.workers)
    left = {h: len(c) for h, c in world.cards.items()}
    res = {"fails": len(mon.fails), "plans": mon.plans, "wakes": mon.wakes, "avg_running": avg, "min_to_2_workers": first,
           "workers_started": used, "cards_left": left, "missed_wake_timeouts": mon.missed,
           "idle_slot_min": mon.idle_slot_min, "dup_idle_lines": mon.dup_idle}
    mon.log("SUMMARY " + json.dumps(res, sort_keys=True))
    for f in mon.fails:
        mon.log("  " + f)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=180)
    ap.add_argument("--seeds", default="1")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--no-faults", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="only SUMMARY and FAIL lines")
    a = ap.parse_args(argv)
    lo, _, hi = a.seeds.partition("-")
    bad = 0
    for seed in range(int(lo), int(hi or lo) + 1):
        r = run(a.minutes, seed, a.real, a.baseline, not a.no_faults, quiet=a.quiet)
        bad += r["fails"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
