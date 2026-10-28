import sys; sys.dont_write_bytecode = True
"""DSA browser worker: a second queue worker next to the Qwen one.

Takes packed tasks from NUC-QUEUE/incoming_dsa/, pastes each prompt into the
operator's own logged-in chat page (dsa_page.py, Playwright over CDP), waits
for the answer and writes done/<id>.reply.json in the same schema as
nuc-worker.ps1, so `queue_tool.py verify` works unchanged.

Rules built in (see research/fast_track_2026-09-27/DSA_BROWSER_WORKER_PLAN.md):
  - one task at a time, min gap between tasks, hourly and daily caps
  - a login / CAPTCHA / "verify you are human" page: stop, heartbeat
    needs-human, task goes back to incoming_dsa. Never interact with it.
  - 3 consecutive errors: heartbeat needs-human until the operator touches
    the resume flag file (dsa_resume.flag in the queue root) or restarts.
  - prompt too long for one paste: error reply, no auto-splitting
  - crash: the claimed task goes back to incoming_dsa
No stealth or anti-detection code. The worker never types credentials.

Lane isolation: reads only incoming_dsa/, claims into claimed_dsa/ (NOT the
shared claimed/, whose restore logic belongs to the Qwen worker), writes
done/ and heartbeat_dsa.json.

Usage:
  python scripts/worker/dsa_worker.py                loop
  python scripts/worker/dsa_worker.py --once         at most one task, then exit
  python scripts/worker/dsa_worker.py --calibrate    print which selectors match
  python scripts/worker/dsa_worker.py --config F.json
Exit codes (--once): 0 ok/idle, 3 needs-human.
"""
import argparse
import json
import os
import socket
import time
import datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORKER_NAME = "dsa-web"

DEFAULTS = {
    "queue_root": str(REPO / "Dumps" / "workers" / "NUC-QUEUE"),
    "min_gap_s": 60,
    "max_per_hour": 10,
    "max_per_day": 60,
    "poll_s": 15,            # idle loop sleep
    "poll_wait_s": 1.0,      # answer polling interval
    "stable_s": 5,           # answer text unchanged this long (and stop button gone) = done
    "min_timeout_s": 120,
    "max_timeout_s": 900,    # cap 15 min
    "tokens_per_s": 8,       # timeout = num_predict / tokens_per_s, clamped
    "max_prompt_chars": 100000,
    "error_limit": 3,
    "cdp_url": "http://127.0.0.1:9222",
    "selectors_file": str(HERE / "dsa_selectors.json"),
}


class PageError(Exception):
    """Site/browser problem while driving the page (selector missing, timeout...)."""


class PromptTooLong(Exception):
    pass


class ChallengeSeen(Exception):
    pass


class ChatPage:
    """Adapter interface. dsa_page.PlaywrightChatPage implements it; tests use a fake."""

    def new_chat(self):
        raise NotImplementedError

    def send(self, prompt):
        raise NotImplementedError

    def challenge_seen(self):
        raise NotImplementedError

    def is_generating(self):
        raise NotImplementedError

    def current_text(self):
        raise NotImplementedError

    def read_last(self):
        """Final answer, preferably via the copy button (keeps markdown)."""
        raise NotImplementedError

    def calibrate(self):
        """Return {selector_name: match_count}."""
        raise NotImplementedError


def utc_stamp(epoch=None):
    t = dt.datetime.fromtimestamp(time.time() if epoch is None else epoch, dt.timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def write_atomic(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def load_config(path=None):
    cfg = dict(DEFAULTS)
    if path:
        with open(path, encoding="utf-8") as fh:
            user = json.load(fh)
        cfg.update({k: v for k, v in user.items() if not k.startswith("_")})
    return cfg


class DsaWorker:
    def __init__(self, page, cfg, clock=time.time, sleep=time.sleep, log=print):
        self.page = page
        self.cfg = cfg
        self.clock = clock
        self.sleep = sleep
        self.log = log
        root = Path(cfg["queue_root"])
        self.root = root
        self.incoming = root / "incoming_dsa"
        self.claimed = root / "claimed_dsa"
        self.done = root / "done"
        self.hb_path = root / "heartbeat_dsa.json"
        self.pace_path = root / "dsa_pace.json"
        self.resume_flag = root / "dsa_resume.flag"
        for d in (self.incoming, self.claimed, self.done):
            d.mkdir(parents=True, exist_ok=True)
        self.host = socket.gethostname()
        self.errors = 0
        self.needs_human = None  # None | "challenge" | "errors"

    # ---------- heartbeat / pacing state ----------
    def heartbeat(self, state, task="", note=""):
        hb = {"host": self.host, "state": state, "task": task, "utc": utc_stamp(self.clock()),
              "worker": WORKER_NAME, "pid": os.getpid()}
        if note:
            hb["note"] = note
        try:
            write_atomic(self.hb_path, json.dumps(hb))
        except OSError:
            pass

    def _finished_times(self):
        try:
            with open(self.pace_path, encoding="utf-8") as fh:
                return [float(x) for x in json.load(fh)]
        except (OSError, ValueError, TypeError):
            return []

    def _record_finish(self):
        now = self.clock()
        times = [t for t in self._finished_times() if t > now - 86400] + [now]
        write_atomic(self.pace_path, json.dumps(times))

    def pacing_block(self, ignore_gap=False):
        """Return None when a task may start now, else a short reason.
        B080 fix 2026-10-01: drop stale, future, or non-epoch entries before the
        window sums, and self-heal the pace file so a corrupted file cannot stall
        the worker for hours."""
        now = self.clock()
        raw = self._finished_times()
        times = [t for t in raw if now - 86400 < t <= now + 60]
        if len(times) != len(raw):
            try:
                write_atomic(self.pace_path, json.dumps(sorted(times)))
            except OSError:
                pass
        if not ignore_gap and times and now - max(times) < self.cfg["min_gap_s"]:
            return "min-gap"
        if sum(1 for t in times if t > now - 3600) >= self.cfg["max_per_hour"]:
            return "hourly-cap"
        if sum(1 for t in times if t > now - 86400) >= self.cfg["max_per_day"]:
            return "daily-cap"
        return None

    # ---------- queue ----------
    def restore_claimed(self):
        for f in sorted(self.claimed.glob("*.task.json")):
            os.replace(f, self.incoming / f.name)
            self.log(f"requeued interrupted task {f.name[:-len('.task.json')]}")

    def _next_task(self):
        cands = sorted(p for p in self.incoming.glob("*.task.json") if not p.name.startswith("."))
        return cands[0] if cands else None

    def _claim(self, path):
        dst = self.claimed / path.name
        try:
            os.replace(path, dst)
        except OSError:
            return None
        return dst

    def _requeue(self, claimed_path):
        if claimed_path.exists():
            os.replace(claimed_path, self.incoming / claimed_path.name)

    def _finish(self, claimed_path, reply):
        """Task file into done/ first, reply last (the reply is what verify looks for)."""
        tid = reply["id"]
        if claimed_path.exists():
            os.replace(claimed_path, self.done / f"{tid}.task.json")
        write_atomic(self.done / f"{tid}.reply.json", json.dumps(reply, indent=1) + "\n")

    # ---------- one task ----------
    def _timeout_for(self, pkg):
        c = self.cfg
        t = float(pkg.get("num_predict") or 4096) / float(c["tokens_per_s"])
        return max(float(c["min_timeout_s"]), min(float(c["max_timeout_s"]), t))

    def _wait_done(self, timeout):
        """Return (text, done_reason). Done = stop button gone AND text unchanged stable_s."""
        c = self.cfg
        start = self.clock()
        last_text, last_change = None, start
        while True:
            now = self.clock()
            if self.page.challenge_seen():
                raise ChallengeSeen()
            text = self.page.current_text() or ""
            if text != last_text:
                last_text, last_change = text, now
            elif text and not self.page.is_generating() and now - last_change >= c["stable_s"]:
                return text, "stop"
            if now - start >= timeout:
                return text, "timeout"
            self.sleep(c["poll_wait_s"])

    def _run(self, pkg, reply):
        prompt = str(pkg.get("prompt", ""))
        if len(prompt) > self.cfg["max_prompt_chars"]:
            raise PromptTooLong(f"prompt too long ({len(prompt)} chars > {self.cfg['max_prompt_chars']})")
        self.page.new_chat()
        if self.page.challenge_seen():
            raise ChallengeSeen()
        self.page.send(prompt)
        text, reason = self._wait_done(self._timeout_for(pkg))
        answer = text
        try:
            got = self.page.read_last()
            if got and got.strip():
                answer = got
        except PageError:
            pass  # keep the innerText we already have
        if not answer.strip():
            raise PageError("empty answer")
        reply["response"] = answer
        reply["done_reason"] = reason
        reply["worker_status"] = "ok"

    def process(self, claimed_path):
        """Run a claimed task. Returns 'done', 'error' or 'challenge'."""
        tid = claimed_path.name[:-len(".task.json")]
        started = self.clock()
        reply = {"schema": 1, "id": tid, "worker": WORKER_NAME, "host": self.host,
                 "model": "dsa-web", "started_utc": utc_stamp(started)}
        self.heartbeat("running", tid)
        outcome = "done"
        try:
            with open(claimed_path, encoding="utf-8") as fh:
                pkg = json.load(fh)
            self._run(pkg, reply)
            self.errors = 0
        except ChallengeSeen:
            self._requeue(claimed_path)
            self.needs_human = "challenge"
            self.heartbeat("needs-human", "", "challenge or login page; clear it by hand")
            self.log(f"challenge while running {tid}; task requeued")
            return "challenge"
        except (PromptTooLong, PageError, ValueError, KeyError) as exc:
            outcome = "error"
            reply.update(worker_status="error", response="", done_reason="error", error=str(exc))
            if isinstance(exc, PromptTooLong):
                reply["error"] = "error: " + str(exc)  # the task's fault, not the site's
            else:
                self.errors += 1
        except BaseException:
            self._requeue(claimed_path)
            self.heartbeat("error", "", "crashed; task requeued")
            raise
        reply["finished_utc"] = utc_stamp(self.clock())
        reply["wall_seconds"] = round(self.clock() - started, 1)
        self._finish(claimed_path, reply)
        self._record_finish()
        self.log(f"finished {tid}: {reply['worker_status']} {reply['done_reason']}")
        if self.errors >= self.cfg["error_limit"]:
            self.needs_human = "errors"
            self.heartbeat("needs-human", "", f"{self.errors} consecutive errors")
        else:
            self.heartbeat("idle")
        return outcome

    # ---------- loop ----------
    def step(self, ignore_gap=False):
        """One scheduling pass. Returns 'idle', 'paced', 'needs-human', 'done', 'error' or 'challenge'."""
        if self.needs_human == "challenge":
            if self.page.challenge_seen():
                self.heartbeat("needs-human", "", "challenge or login page; clear it by hand")
                return "needs-human"
            self.needs_human = None
        elif self.needs_human == "errors":
            if self.resume_flag.exists():
                self.resume_flag.unlink()
                self.errors = 0
                self.needs_human = None
            else:
                self.heartbeat("needs-human", "", f"{self.errors} consecutive errors; touch dsa_resume.flag")
                return "needs-human"
        nxt = self._next_task()
        if nxt is None:
            self.heartbeat("idle")
            return "idle"
        block = self.pacing_block(ignore_gap)
        if block:
            self.heartbeat("idle", "", f"paced: {block}")
            return "paced"
        claimed = self._claim(nxt)
        if claimed is None:
            return "idle"
        return self.process(claimed)

    def run(self, once=False):
        self.restore_claimed()
        while True:
            res = self.step(ignore_gap=once)
            if once:
                return 3 if res in ("needs-human", "challenge") else 0
            if res in ("done", "error"):
                continue
            self.sleep(self.cfg["poll_s"])


def make_page(cfg):
    # when run as a script this module is __main__; make dsa_page share these exception classes
    sys.modules.setdefault("dsa_worker", sys.modules[__name__])
    import dsa_page  # lazy: needs playwright, tests do not
    return dsa_page.PlaywrightChatPage(cfg["cdp_url"], cfg["selectors_file"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="DSA browser queue worker")
    ap.add_argument("--once", action="store_true", help="process at most one task, then exit")
    ap.add_argument("--calibrate", action="store_true", help="print which selectors match the open page")
    ap.add_argument("--config", help="JSON file overriding the defaults")
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    page = make_page(cfg)
    if args.calibrate:
        res = page.calibrate()
        for name, n in res.items():
            print(f"{'OK  ' if n else 'MISS'} {name}: {n} match(es)")
        return 0 if all(res.values()) else 1
    worker = DsaWorker(page, cfg)
    return worker.run(once=args.once)


if __name__ == "__main__":
    sys.exit(main())
