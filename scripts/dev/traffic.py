"""Pipeliner's allocator tool (was Traffic_Controller): what exists, what is alive, what budget is left, and who should do what next.
Design: MyTradingSys/system/TRAFFIC_CONTROLLER.md. Inventory: MyTradingSys/system/traffic_inventory.json.

  python scripts/dev/traffic.py status [--json] [--no-fetch]   inventory + liveness + budgets + leases + queue + proposed allocation
  python scripts/dev/traffic.py budget [--json] [--no-fetch]   SPEND/NORMAL/THROTTLE per Claude login + overall, from the newest BUDGET signal lines
  python scripts/dev/traffic.py measure [--hours 72] [--json]  idle hours per machine / sender / lab lane and duplicate work

Read-only: it fetches, reads trunk refs, the signal branch clone and the lab logs on this machine; it starts, posts and ships
nothing. The allocation is a PROPOSAL the Pipeliner session acts on (start_session here, a signal or desk row for
another machine, `codex_run.py tick` on the lab host). Every source is parsed whole (never a log tail); a source that cannot
be read is reported as `unknown` with the reason, never as idle.
"""
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hosts  # noqa: E402
REPO = Path(__file__).resolve().parents[2]
INVENTORY = "MyTradingSys/system/traffic_inventory.json"
TRUNK = "fast-track"
UTC = timezone.utc
NOISE_SUBJECT = re.compile(r"^(Merge |merge |claim |release |lane health|desk: |desk task: |lease |relay )")


def _flags():
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def run(args, cwd=None, timeout=120):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, creationflags=_flags())
        return r.returncode, r.stdout, r.stderr
    except (subprocess.TimeoutExpired, OSError) as e:
        return 124, "", str(e)


def git(repo, *args, timeout=120):
    return run(["git", "-C", str(repo), *args], timeout=timeout)


def utc(s):
    """ISO or compact (20261018T211243Z) -> aware datetime, or None."""
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%MZ"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=UTC)
        except ValueError:
            pass
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d.astimezone(UTC) if d.tzinfo else d.replace(tzinfo=UTC)
    except ValueError:
        return None


def load_inventory(repo=REPO):
    return json.loads((Path(repo) / INVENTORY).read_text(encoding="utf-8"))


def host_of_signal(sender, inv):
    h = sender.split("/")[0].lower()
    for name, m in inv["machines"].items():
        if h in [x.lower() for x in m["signal_ids"]]:
            return name
    return None


def host_of_prefix(prefix, inv):
    for name, m in inv["machines"].items():
        if prefix in m["branch_prefixes"]:
            return name
    return None


# ---------- sources (each returns (events, error)) ----------
def signals_dir():
    import mts_signal
    return mts_signal.home()


def read_signals(since, until, d=None):
    """[(dt, sender, kind, text)] from every signal file in the window (the clone mts_signal keeps)."""
    d = Path(d) if d else signals_dir()
    if not d.is_dir():
        return [], f"no signal clone at {d}"
    out, bad = [], 0
    for f in sorted(d.glob("*.json")):
        try:
            x = json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            bad += 1
            continue
        t = utc(x.get("t"))
        if t and since <= t <= until:
            out.append((t, str(x.get("from", "?")), str(x.get("kind", "")), str(x.get("text", ""))))
    return out, (f"{bad} signal file(s) unreadable: liveness may be incomplete" if bad else None)


def refresh_signals():
    try:
        import mts_signal
        mts_signal.ensure()
        h = mts_signal.home()
        git(h, "fetch", "-q", "origin", mts_signal.BRANCH, timeout=30)
        git(h, "reset", "-q", "--hard", "FETCH_HEAD", timeout=30)
        return None
    except Exception as e:  # stale clone is reported, not hidden
        return f"signal refresh failed: {type(e).__name__}"


SEP = "\x1e"


def read_commits(repo, since, until, ref=f"origin/{TRUNK}"):
    """[{sha, parents, at, email, subject, body}] for every commit on ref with author date in the window."""
    fmt = SEP + "%H%x1f%P%x1f%aI%x1f%ae%x1f%s%x1f%b"
    rc, out, err = git(repo, "log", ref, f"--since={(since - timedelta(days=2)).isoformat()}", f"--format={fmt}", timeout=180)
    if rc:
        return [], f"git log failed: {err.strip()[:200]}"
    rows = []
    for chunk in out.split(SEP)[1:]:
        p = chunk.split("\x1f")
        if len(p) < 6:
            continue
        at = utc(p[2])
        if at and since <= at <= until:
            rows.append({"sha": p[0], "parents": p[1].split(), "at": at, "email": p[3], "subject": p[4], "body": p[5]})
    return rows, None


CLAIM_HOST = re.compile(r"Result: .+? on (\S+) works on")
MERGE_INTO = re.compile(r"into ([A-Za-z0-9_-]+)/")


def attribute_commits(repo, commits, signals, inv):
    """{sha: host}. Order: claim body host; author email known per machine; merge `into <prefix>/` plus that merge's
    branch-local commits; a merge whose prefix names no machine (claude/...) by a `done ship` signal from exactly one
    host within -5..+10 min."""
    by_sha = {c["sha"]: c for c in commits}
    host = {}
    authors = {a: n for n, m in inv["machines"].items() for a in m.get("authors", [])}
    ships = [(t, host_of_signal(s, inv)) for t, s, k, x in signals if k == "done" and x.startswith("ship")]
    for c in commits:
        m = CLAIM_HOST.search(c["body"])
        if m and m.group(1).upper() in inv["machines"]:
            host[c["sha"]] = m.group(1).upper()
        elif c["email"] in authors:
            host[c["sha"]] = authors[c["email"]]
    for c in commits:
        if len(c["parents"]) != 2 or c["sha"] in host:
            continue
        m = MERGE_INTO.search(c["subject"])
        h = host_of_prefix(m.group(1), inv) if m else None
        if not h:
            near = {hh for t, hh in ships if hh and timedelta(minutes=-5) <= c["at"] - t <= timedelta(minutes=10)}
            h = near.pop() if len(near) == 1 else None
        if not h:
            continue
        host[c["sha"]] = h
        rc, out, _ = git(repo, "rev-list", c["parents"][0], f"^{c['parents'][1]}", timeout=60)
        for s in out.split() if rc == 0 else []:
            if s in by_sha and s not in host:
                host[s] = h
    return host


def read_codex(path, since, until):
    p = Path(path)
    if not p.exists():
        return [], f"no codex run log at {p} (not the lab host?)"
    out = []
    for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            x = json.loads(ln)
        except ValueError:
            continue
        t = utc(x.get("at"))
        if not t:
            continue
        end = t + timedelta(seconds=float(x.get("seconds") or 0))
        if end >= since and t <= until:
            out.append({"start": t, "end": end, "card": x.get("card"), "outcome": x.get("outcome")})
    return out, None


EXIT_RE = re.compile(r"EXIT (-?\d+) after (\d+)s")


def read_gemini(d, since, until):
    """One job per F:/MTS/gq/<card>.log: end = file mtime, start = end - the `EXIT n after Ns` seconds; a log without an
    EXIT line that changed in the last 45 min is RUNNING."""
    d = Path(d)
    if not d.is_dir():
        return [], f"no gemini job dir at {d} (not the lab host?)"
    out = []
    for f in sorted(d.glob("*.log")):
        end = datetime.fromtimestamp(f.stat().st_mtime, UTC)
        text = f.read_text(encoding="utf-8", errors="replace")
        m = None
        for m in EXIT_RE.finditer(text):
            pass
        if f.stem in ("chain_after_reset", "wait_chain"):
            continue
        if m:
            start = end - timedelta(seconds=int(m.group(2)))
            state = "done" if m.group(1) == "0" else "failed"
        else:
            start = end - timedelta(minutes=1)
            state = "running" if (until - end) < timedelta(minutes=45) else "no-exit-line"
        if end >= since and start <= until:
            out.append({"start": start, "end": end, "card": f.stem, "state": state})
    return out, None


# ---------- measurement ----------
def hour_index(t, since):
    return int((t - since).total_seconds() // 3600)


def busy_hours(points, intervals, since, hours):
    b = set()
    for t in points:
        i = hour_index(t, since)
        if 0 <= i < hours:
            b.add(i)
    for s, e in intervals:
        for i in range(max(0, hour_index(s, since)), min(hours - 1, hour_index(e, since)) + 1):
            b.add(i)
    return b


def longest_gap(busy, hours):
    best = cur = 0
    for i in range(hours):
        cur = 0 if i in busy else cur + 1
        best = max(best, cur)
    return best


def summarize(name, points, intervals, since, hours, source, error=None):
    if error and not points and not intervals:
        return {"actor": name, "busy_h": None, "idle_h": None, "longest_idle_h": None, "source": source, "error": error}
    b = busy_hours(points, intervals, since, hours)
    return {"actor": name, "busy_h": len(b), "idle_h": hours - len(b), "longest_idle_h": longest_gap(b, hours),
            "events": len(points) + len(intervals), "source": source, **({"error": error} if error else {})}


def overlapping_claims(commits, host):
    """A `claim X` while an earlier `claim X` is still open (no `release X` between): two workers on one slug.
    A re-claim after a release is a retry and does not count."""
    out = {}
    open_ = {}
    for c in sorted(commits, key=lambda c: c["at"]):
        s = c["subject"]
        if s.startswith("claim "):
            k = s[6:].strip()
            if k in open_:
                out.setdefault(k, [open_[k]]).append(host.get(c["sha"], "?") + " " + c["at"].strftime("%m-%dT%H:%MZ"))
            else:
                open_[k] = host.get(c["sha"], "?") + " " + c["at"].strftime("%m-%dT%H:%MZ")
        elif s.startswith("release "):
            open_.pop(s[8:].strip(), None)
    return out


def duplicates(commits, host, signals, codex, gemini):
    out = {}
    acts = defaultdict(list)
    for c in commits:
        m = re.match(r"desk: (taken|done|failed) (\S+)", c["subject"])
        if m:
            acts[m.group(2)].append((m.group(1), host.get(c["sha"], "?"), c["at"].strftime("%m-%dT%H:%MZ")))
    out["desk_rows_closed_more_than_once"] = {k: v for k, v in acts.items() if sum(a[0] in ("done", "failed") for a in v) > 1}
    posts = Counter(c["subject"][len("desk task: "):].strip().lower() for c in commits if c["subject"].startswith("desk task: "))
    out["desk_rows_posted_twice"] = {k: n for k, n in posts.items() if n > 1}
    out["claims_overlapping"] = overlapping_claims(commits, host)
    runs = defaultdict(list)   # codex_run.py and gemini_queue.py claim their own card as the NUC login
    for r in list(codex) + list(gemini):
        runs[r["card"]].append((r["start"] - timedelta(minutes=10), r["end"] + timedelta(minutes=10)))
    work = defaultdict(list)   # card -> [(lane, start, end)]; a Claude claim lasts until its release (or the window end)
    for r in codex:
        work[r["card"]].append(("codex", r["start"], r["end"]))
    for r in gemini:
        work[r["card"]].append(("gemini-nuc", r["start"], r["end"]))
    end_of = max([c["at"] for c in commits] + [w[2] for ws in work.values() for w in ws], default=None)   # window end
    open_ = {}
    for c in sorted(commits, key=lambda c: c["at"]):
        s = c["subject"]
        if s.startswith("claim "):
            card = s[6:].strip()
            if host.get(c["sha"]) == "JIS-NUC" and any(a <= c["at"] <= b for a, b in runs.get(card, ())):
                continue  # the lab runner's own claim: same lane, not a second worker
            open_[card] = (host.get(c["sha"], "?"), c["at"])
        elif s.startswith("release ") and s[8:].strip() in open_:
            h, t = open_.pop(s[8:].strip())
            work[s[8:].strip()].append(("claude:" + h, t, c["at"]))
    for card, (h, t) in open_.items():
        work[card].append(("claude:" + h, t, end_of))
    lab, turn = {}, {}
    for card, ws in work.items():
        lanes = {w[0] for w in ws}
        if len(lanes) < 2:
            continue
        both = sorted({x for i, a in enumerate(ws) for b in ws[i + 1:] if a[0] != b[0] and a[1] <= b[2] and b[1] <= a[2]
                       for x in (a[0], b[0])})
        if any(not x.startswith("claude:") for x in both):
            lab[card] = both              # a lab lane ran it while another lane held or ran it
        elif not both:
            turn[card] = sorted(lanes)    # one after the other: a hand-over or a retry, not a collision
        # two Claude claims at once are already in claims_overlapping
    out["cards_worked_by_two_lanes"] = lab
    out["cards_claimed_by_two_hosts_in_turn"] = turn
    subj = defaultdict(set)
    for c in commits:
        if len(c["parents"]) == 1 and not NOISE_SUBJECT.match(c["subject"]):
            subj[c["subject"].strip()].add(host.get(c["sha"], "?"))
    out["same_subject_from_two_hosts"] = {k: sorted(v) for k, v in subj.items() if len(v - {"?"}) > 1}
    pipe = defaultdict(set)
    for c in commits:
        if re.match(r"(?:[\w-]+ & )?pipeliner:", c["subject"], re.I):   # a Pipeliner's own work commit, not a mention
            pipe[host.get(c["sha"], "?")].add(c["at"].strftime("%m-%dT%H:%MZ") + " " + c["sha"][:8])
    for t, s, k, x in signals:
        if x.startswith("PIPE:"):
            pipe[host_of_signal(s, inv_cache()) or s].add(t.strftime("%m-%dT%H:%MZ") + " signal PIPE")
    out["pipeliner_runs_by_host"] = {k: sorted(v) for k, v in pipe.items()}
    seen, rep = {}, 0
    for t, s, k, x in sorted(signals):
        key = (s, k, x)
        if key in seen and t - seen[key] <= timedelta(minutes=5):
            rep += 1
        seen[key] = t
    out["signal_lines_repeated_within_5min"] = rep
    return out


_INV = {}


def inv_cache():
    if not _INV:
        _INV.update(load_inventory())
    return _INV


def measure(repo=REPO, hours=72, until=None, inv=None, sig_dir=None, codex_log=None, gq_dir=None, do_fetch=True):
    inv = inv or inv_cache()
    until = until or datetime.now(UTC).replace(microsecond=0)
    since = until - timedelta(hours=hours)
    notes, stale = [], False
    if do_fetch:
        rc, _, err = git(repo, "fetch", "-q", "origin", TRUNK, timeout=60)
        if rc:
            stale = True
            notes.append(f"STALE: fetch failed, commit-based numbers come from the last fetched ref: {err.strip()[:120]}")
        e = refresh_signals() if sig_dir is None else None
        if e:
            notes.append(e)
    sigs, sig_err = read_signals(since, until, sig_dir)
    if sig_err:
        notes.append(sig_err)
    commits, git_err = read_commits(repo, since, until)
    host = attribute_commits(repo, commits, sigs, inv)
    codex, codex_err = read_codex(codex_log or inv["lanes"]["codex"]["runs_log"], since, until)
    gem, gem_err = read_gemini(gq_dir or inv["lanes"]["gemini-nuc"]["log_dir"], since, until)
    first_sig = min((t for t, *_ in sigs), default=None)
    if first_sig and first_sig - since > timedelta(hours=1):
        notes.append(f"signals start {first_sig:%Y-%m-%dT%H:%MZ}: the first {(first_sig - since).total_seconds() / 3600:.0f} h "
                     "of the window have no signal data (branch kept 7 days, created 2026-10-16)")
    rows = []
    for name in inv["machines"]:
        pts = [t for t, s, *_ in sigs if host_of_signal(s, inv) == name] + [c["at"] for c in commits if host.get(c["sha"]) == name]
        rows.append(summarize(name, pts, [], since, hours, "signals + attributed commits", sig_err or git_err))
    senders = sorted({s for _, s, *_ in sigs})
    for s in senders:
        rows.append(summarize("sender " + s, [t for t, ss, *_ in sigs if ss == s], [], since, hours, "signals only"))
    rows.append(summarize("lane codex", [], [(r["start"], r["end"]) for r in codex], since, hours, "runs.jsonl", codex_err))
    rows.append(summarize("lane gemini-nuc", [], [(r["start"], r["end"]) for r in gem], since, hours, "gq logs", gem_err))
    marker = inv["lanes"]["gemini-laptop"]["session_marker"]
    rows.append(summarize("lane gemini-laptop", [c["at"] for c in commits if marker in c["body"]], [], since, hours,
                          "commits with MTS-Session " + marker))
    dsa_ids = {c["subject"].split()[2] for c in commits if re.match(r"desk: (done|failed) ", c["subject"])}
    dsa_pts = [c["at"] for c in commits if re.match(r"desk: (done|failed) ", c["subject"]) and "dsa" in c["body"].lower()]
    rows.append(summarize("lane dsa (desk rows closed by DSA)", dsa_pts, [], since, hours, "desk commits naming dsa"))
    unattributed = sum(1 for c in commits if c["sha"] not in host)
    return {"stale": stale, "window": {"since": since.strftime("%Y-%m-%dT%H:%MZ"), "until": until.strftime("%Y-%m-%dT%H:%MZ"), "hours": hours},
            "counts": {"commits": len(commits), "attributed": len(commits) - unattributed, "signals": len(sigs),
                       "codex_runs": len(codex), "gemini_jobs": len(gem), "desk_rows_closed": len(dsa_ids)},
            "actors": rows, "duplicates": duplicates(commits, host, sigs, codex, gem), "notes": notes,
            "login_split": "not measurable: no event records the Claude login (A/B/C); senders are host/MTS_ACCOUNT. "
                           "Fix: BUDGET signal lines (TRAFFIC_CONTROLLER.md TC3)"}


# ---------- status + allocation ----------
def liveness(last, now, inv):
    if last is None:
        return "SILENT"
    m = (now - last).total_seconds() / 60
    return "ACTIVE" if m <= inv["liveness_min"]["active"] else "IDLE" if m <= inv["liveness_min"]["idle"] else "SILENT"


BUDGET_RE = re.compile(r"BUDGET login=([ABC]) 5h=(\d+)% week=(\d+)%(?: reset=(\d{4}-\d\d-\d\dT\d\d:\d\dZ?))?")
BUDGET_FRESH_H = 6        # a reading older than this counts as NORMAL / unknown (SUPER_SESSION.md Pacing)
WEEK_H = 168


def budgets_from_signals(sigs):
    """Latest `BUDGET login=A 5h=42% week=30%` line per login (sent by each session at boot, TC3)."""
    out = {}
    for t, s, k, x in sorted(sigs):
        m = BUDGET_RE.search(x)
        if m:
            out[m.group(1)] = {"five_h": int(m.group(2)), "week": int(m.group(3)), "at": t.strftime("%Y-%m-%dT%H:%MZ"), "from": s}
            if m.group(4):
                out[m.group(1)]["reset"] = m.group(4) if m.group(4).endswith("Z") else m.group(4) + "Z"
    return out


def pacing_state(b, now):
    """SPEND / NORMAL / THROTTLE for one login's reading (table in SUPER_SESSION.md 'Pacing'). f = share of the week elapsed,
    from `reset=` (weekly reset time; the week is 168 h). THROTTLE wins over SPEND. A reading older than BUDGET_FRESH_H, or one
    that lacks the numbers a rule needs, never produces SPEND: NORMAL with the reason."""
    at = utc(b.get("at"))
    if at is None or (now - at).total_seconds() > BUDGET_FRESH_H * 3600:
        return "NORMAL", f"reading older than {BUDGET_FRESH_H} h or undated: counted NORMAL"
    u, h5 = b.get("week"), b.get("five_h")
    reset = utc(b.get("reset"))
    if h5 is not None and h5 > 80:
        return "THROTTLE", f"5 h window {h5}% > 80"
    if u is None or reset is None:
        return "NORMAL", "no weekly % or reset time in the line: only the 5 h rule applies"
    left_h = (reset - now).total_seconds() / 3600
    if left_h <= 0 or left_h > WEEK_H:
        return "NORMAL", f"reset time {b.get('reset')} is past or more than a week away: reading unusable for pace"
    f = 1 - left_h / WEEK_H
    if u > 100 * f + 5:
        return "THROTTLE", f"week {u}% > pace {round(100 * f + 5)}% ({round(f * 100)}% of the week gone)"
    if u < 100 * f - 10 or (0 <= left_h < 24 and u < 85):
        return "SPEND", f"week {u}% under pace {round(100 * f - 10)}% or reset in {max(0, round(left_h))} h with room"
    return "NORMAL", f"week {u}% on pace ({round(f * 100)}% of the week gone)"


def spend_view(budgets, now):
    """{'logins': {L: {state, why, ...reading}}, 'overall': state, 'why'}: per login and overall. Overall: SPEND if any fresh login
    can spend (the work goes to that login); THROTTLE only when every reported login is THROTTLE; NORMAL otherwise; UNKNOWN when none."""
    rows = {}
    for lg, b in sorted(budgets.items()):
        if lg == "this_login":
            continue
        st, why = pacing_state(b, now)
        rows[lg] = {"state": st, "why": why, **{k: b.get(k) for k in ("five_h", "week", "reset", "at")}}
    states = [r["state"] for r in rows.values()]
    if not states:
        return {"logins": rows, "overall": "UNKNOWN", "why": "no BUDGET line in the window: each session sends one at start"}
    if "SPEND" in states:
        who = ",".join(l for l, r in rows.items() if r["state"] == "SPEND")
        return {"logins": rows, "overall": "SPEND", "why": f"login(s) {who} can spend"}
    if all(s == "THROTTLE" for s in states):
        return {"logins": rows, "overall": "THROTTLE", "why": "every reported login is THROTTLE"}
    return {"logins": rows, "overall": "NORMAL", "why": "no login can spend; not all are THROTTLE"}


def render_spend(v):
    L = ["SPEND view (per login, newest BUDGET line each)"]
    for lg, r in v["logins"].items():
        L.append(f"  login {lg}: {r['state']:<8} 5h={r['five_h']}% week={r['week']}% reset={r.get('reset') or '-'} "
                 f"at {r['at']}  ({r['why']})")
    L.append(f"  OVERALL: {v['overall']}  ({v['why']})")
    missing = [l for l in "ABC" if l not in v["logins"]]
    if missing:
        L.append(f"  no reading for login(s) {','.join(missing)}: send one from a session on that login (get_usage, then BUDGET line)")
    return "\n".join(L)


def budget_view(do_fetch=True, now=None, hours=48):
    now = now or datetime.now(UTC)
    err = refresh_signals() if do_fetch else None
    sigs, e = read_signals(now - timedelta(hours=hours), now)
    return spend_view(budgets_from_signals(sigs), now), [x for x in (err, e) if x]


CODEX_WIN = re.compile(r"5-hour window (\d+)% used")
CODEX_GUARD = re.compile(r"window (\d+)/(\d+) pts, (\d+)/(\d+) runs")
CODEX_READY = re.compile(r"Queue: (\d+) ready")


def codex_status(repo):
    rc, out, err = run([sys.executable, str(Path(repo) / "scripts/dev/codex_run.py"), "status"], cwd=str(repo), timeout=90)
    if rc:
        return {"state": "unknown", "error": (err or out).strip()[:160]}
    lines = out.splitlines()
    if not lines:
        return {"state": "unknown", "error": "codex_run.py status printed nothing"}
    d = {"state": "on" if ": on" in lines[0] else "off", "stalled": "STALLED" in out}
    for rx, keys in ((CODEX_WIN, ("allowance_5h_pct",)), (CODEX_GUARD, ("pts", "pts_cap", "runs", "runs_cap")), (CODEX_READY, ("ready",))):
        m = rx.search(out)
        if m:
            d.update({k: int(v) for k, v in zip(keys, m.groups())})
    return d


def allocate(state, inv):
    """Pure: proposals from a status dict. Each card id is given to at most one lane/machine (no double claims)."""
    props, used = [], set(state.get("reserved", ()))   # cards proposed on an earlier wake are not proposed again
    pace = inv["pacing"]
    alive = [h for h, m in state["machines"].items() if m["liveness"] in ("ACTIVE", "IDLE")]
    for role, l in state["leases"].items():
        st = l.get("state")
        if st == "unknown":
            props.append({"who": "operator", "action": f"{role} lease state unreadable: run nothing as {role}", "why": l.get("error")})
        elif st in ("free", "expired") and role == "Pipeliner" and (state["desk"].get("pending") or 0):
            pref = inv["singletons"][role]["prefer"]
            where = pref if pref in alive else (alive[0] if alive else None)
            if where:
                props.append({"who": where, "action": f"start `You are {role}.` (lease free; it acquires on boot)",
                              "why": f"{state['desk']['pending']} desk rows pending"})
    queue = state["queue"]
    cx = state["lanes"].get("codex", {})
    codex_cards = [c for c in queue if c["lane"] == "CODEX"]
    if cx.get("state") == "on" and codex_cards and cx.get("runs", 0) < cx.get("runs_cap", 10) \
            and cx.get("allowance_5h_pct", 100) < pace["normal_below"]:
        c = codex_cards[0]
        used.add(c["id"])
        props.append({"who": "JIS-NUC", "action": f"codex_run.py tick (next CODEX card {c['id']})",
                      "why": "lab lane " + ("STALLED" if cx.get("stalled") else "idle") + f", allowance {cx.get('allowance_5h_pct')}%"})
    if 0 <= cx.get("ready", 0) < inv["lanes"]["codex"]["keep_ready"]:
        props.append({"who": "Session_Planner", "action": "refine CODEX cards to 8+ ready", "why": f"{cx.get('ready')} ready"})
    gem = state["lanes"].get("gemini-nuc", {})
    if gem.get("running", 0) == 0:
        g = next((c for c in codex_cards if c["id"] not in used and re.search(r"video|youtube|transcript|caption|search", c["title"], re.I)), None)
        if g:
            used.add(g["id"])
            props.append({"who": "JIS-NUC", "action": f"gemini_queue.py run {g['id']}:medium (Lab_Guy reviews the branch)",
                          "why": "gemini lane idle; card needs commands/search"})
    budgets = state["budgets"]
    for h in alive:
        m = state["machines"][h]
        logins = [l for l in inv["machines"][h]["logins"] if l in budgets]
        b = min((budgets[l]["five_h"] for l in logins if "five_h" in budgets[l]), default=None)
        if b is not None and b >= pace["supervisor_only_below"]:
            continue
        free = max(0, inv["slots_per_machine"] - m["open_claims"])
        if b is None:
            free = min(free, 1)   # no BUDGET line for this machine's logins: one session at a time until one arrives (tc3)
        lane_ok = ("SONNET", "HAIKU") + (("JIS-NB",) if hosts.same_host(h, "JIS-NB") else ())
        crucial_only = b is not None and b >= pace["normal_below"]
        picks = [c for c in queue if c["id"] not in used and c["lane"] in lane_ok
                 and (not crucial_only or c.get("weight") in ("CRUCIAL", "CRITICAL"))][:free]
        for c in picks:
            used.add(c["id"])
        if picks:
            props.append({"who": h, "action": "start sessions for " + ", ".join(c["id"] for c in picks),
                          "why": f"{m['liveness']}, {free} free slot(s), 5h budget {b if b is not None else 'unknown'}%"})
    for h, m in state["machines"].items():
        if m["liveness"] == "SILENT" and m["open_claims"]:
            props.append({"who": "Pipeliner", "action": f"ask {h} by signal about {m['open_claims']} open claim(s); release only by claim rules",
                          "why": f"{h} silent since {m['last_seen'] or 'never in window'}"})
    return props


def status(repo=REPO, do_fetch=True, inv=None, now=None):
    inv = inv or inv_cache()
    now = now or datetime.now(UTC)
    errors = []
    if do_fetch:
        rc, _, err = git(repo, "fetch", "-q", "origin", TRUNK, timeout=60)
        if rc:
            errors.append("fetch failed: " + err.strip()[:120])
        e = refresh_signals()
        if e:
            errors.append(e)
    sigs, e = read_signals(now - timedelta(hours=24), now)
    if e:
        errors.append(e)
    import lease
    import sync
    leases = lease.status(repo, do_fetch=False)
    claims = sync.read_claims(repo, f"origin/{TRUNK}")
    machines = {}
    for h in inv["machines"]:
        last = max((t for t, s, *_ in sigs if host_of_signal(s, inv) == h), default=None)
        oc = [s for s, kv in claims if (kv.get("host") or "").upper() == h]
        machines[h] = {"liveness": liveness(last, now, inv), "last_seen": last.strftime("%Y-%m-%dT%H:%MZ") if last else None,
                       "open_claims": len(oc), "claims": oc}
    rc, out, err = run([sys.executable, str(Path(repo) / "scripts/dev/tasks.py"), "dispatch", "--json"], cwd=str(repo), timeout=120)
    try:
        queue = json.loads(out)["dispatch"]
    except (ValueError, KeyError):
        queue, _ = [], errors.append("tasks.py dispatch failed: " + err.strip()[:120])
    env = {**os.environ, "MTS_ROLE": "traffic-reader"}   # the sweep is a dry-run read: never a lease renew push from here
    try:
        r = subprocess.run([sys.executable, str(Path(repo) / "scripts/dev/desk.py"), "sweep", "--json", "--no-fetch"], cwd=str(repo),
                           env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                           creationflags=_flags())
        out, err = r.stdout, r.stderr
    except (subprocess.TimeoutExpired, OSError) as e:
        out, err = "", str(e)
    try:
        sw = json.loads(out)
        desk = {"pending": sw.get("pending", 0), "per_target": sw.get("pending_per_target", {}), "counts": sw.get("counts", {})}
    except ValueError:
        desk = {"pending": None, "error": (err or out).strip()[:160]}
        errors.append("desk.py sweep failed: " + desk["error"])
    lanes = {}
    if Path(inv["lanes"]["codex"]["runs_log"]).exists():
        lanes["codex"] = codex_status(repo)
    else:
        lanes["codex"] = {"state": "unknown", "error": "not the lab host"}
    gem, ge = read_gemini(inv["lanes"]["gemini-nuc"]["log_dir"], now - timedelta(hours=24), now)
    lanes["gemini-nuc"] = {"state": "unknown", "error": ge} if ge else {
        "running": sum(1 for g in gem if g["state"] == "running"),
        "last_end": max((g["end"] for g in gem), default=None) and max(g["end"] for g in gem).strftime("%Y-%m-%dT%H:%MZ"),
        "jobs_24h": len(gem)}
    budgets = budgets_from_signals(sigs)
    local = Path.home() / ".claude" / "mts-budget.json"
    if local.exists():
        try:
            raw = json.loads(local.read_text(encoding="utf-8"))
            nums = {k: raw[k] for k in ("five_h", "week", "pct_5h", "pct_week") if isinstance(raw.get(k), (int, float))}
            if nums:
                budgets.setdefault("this_login", nums)   # numbers only: the status may end up in a prompt or signal
        except (ValueError, OSError, AttributeError):
            pass
    state = {"as_of": now.strftime("%Y-%m-%dT%H:%MZ"), "machines": machines,
             "leases": {r: {"state": v.get("state"), "text": v.get("text"), "error": v.get("error")} for r, v in leases.items()},
             "lanes": lanes, "budgets": budgets, "desk": desk,
             "queue": [{k: c.get(k) for k in ("id", "lane", "weight", "title", "est_turns", "worker")} for c in queue],
             "errors": errors}
    if any(e.startswith(("fetch failed", "signal refresh failed")) for e in errors):
        state["allocation"] = [{"who": "Pipeliner", "action": "act on nothing: state is stale",
                                "why": "; ".join(errors)}]   # cached refs are not current state
    else:
        state["reserved"] = sorted(load_reserved(now))
        state["allocation"] = allocate(state, inv)
        save_reserved(now, state["allocation"])
    return state


RESERVED = Path.home() / ".claude" / "mts-traffic-reserved.json"
RESERVE_MIN = 60


def proposed_cards(props):
    out = []
    for p in props:
        a = p["action"]
        if a.startswith("start sessions for "):
            out += a[len("start sessions for "):].split(", ")
        elif "(next CODEX card " in a:
            out.append(a.split("(next CODEX card ")[1].rstrip(")"))
        elif a.startswith("gemini_queue.py run "):
            out.append(a.split()[2].split(":")[0])
    return out


def load_reserved(now, path=None):
    """Card ids proposed in the last RESERVE_MIN minutes (the controller is a singleton, so a local file is enough):
    a second wake before the worker's claim reaches trunk must not hand the same card to another worker."""
    try:
        d = json.loads(Path(path or RESERVED).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {k for k, until in d.items() if utc(until) and utc(until) > now}


def save_reserved(now, props, path=None):
    p = Path(path or RESERVED)
    keep = {k: (now + timedelta(minutes=RESERVE_MIN)).strftime("%Y-%m-%dT%H:%M:%SZ") for k in load_reserved(now, p)}
    try:
        old = json.loads(p.read_text(encoding="utf-8"))
        keep.update({k: v for k, v in old.items() if k in keep})
    except (OSError, ValueError):
        pass
    for c in proposed_cards(props):
        keep[c] = (now + timedelta(minutes=RESERVE_MIN)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(keep, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    except OSError:
        pass


def render_status(s):
    L = [f"Traffic {s['as_of']}" + (f"  ERRORS: {'; '.join(s['errors'])}" if s["errors"] else "")]
    for h, m in s["machines"].items():
        L.append(f"  {h:<16} {m['liveness']:<7} last {m['last_seen'] or '-'}  claims {m['open_claims']}")
    for r, l in s["leases"].items():
        L.append(f"  lease {r}: {l.get('text') or l.get('error')}")
    for n, l in s["lanes"].items():
        L.append(f"  lane {n}: " + ", ".join(f"{k}={v}" for k, v in l.items()))
    L.append(f"  budgets: {json.dumps(s['budgets']) if s['budgets'] else 'none reported (TC3 BUDGET lines)'}")
    L.append(f"  desk pending {s['desk'].get('pending')}  queue ready {len(s['queue'])} ({dict(Counter(c['lane'] for c in s['queue']))})")
    L.append("  PROPOSED:")
    L += [f"   - [{p['who']}] {p['action']}  ({p['why']})" for p in s["allocation"]] or ["   - nothing"]
    return "\n".join(L)


def render_measure(m):
    w = m["window"]
    L = [f"Measured {w['since']} .. {w['until']} ({w['hours']} h): " + ", ".join(f"{k} {v}" for k, v in m["counts"].items())]
    L.append(f"  {'actor':<40} {'busy_h':>6} {'idle_h':>6} {'longest idle':>12}  source")
    for r in m["actors"]:
        if r["busy_h"] is None:
            L.append(f"  {r['actor']:<40} {'?':>6} {'?':>6} {'?':>12}  {r['error']}")
        else:
            L.append(f"  {r['actor']:<40} {r['busy_h']:>6} {r['idle_h']:>6} {r['longest_idle_h']:>12}  {r['source']}")
    d = m["duplicates"]
    L.append("  Duplicates:")
    for k, v in d.items():
        L.append(f"   {k}: {len(v) if isinstance(v, dict) else v}")
        if isinstance(v, dict):
            L += [f"     {kk}: {vv}" for kk, vv in list(v.items())[:12]]
    L += [f"  note: {n}" for n in m["notes"]] + [f"  note: {m['login_split']}"]
    return "\n".join(L)


def main(argv):
    if not argv or argv[0] not in ("status", "measure", "budget"):
        print(__doc__)
        return 2
    if argv[0] == "budget":
        v, errs = budget_view(do_fetch="--no-fetch" not in argv)
        print(json.dumps({**v, "errors": errs}, indent=1) if "--json" in argv else render_spend(v) + "".join("\n  ERROR: " + x for x in errs))
        return 0 if not errs else 1
    if argv[0] == "measure":
        h = int(argv[argv.index("--hours") + 1]) if "--hours" in argv else 72
        m = measure(REPO, h, do_fetch="--no-fetch" not in argv)
        print(json.dumps(m, indent=1, default=str) if "--json" in argv else render_measure(m))
        return 0
    s = status(REPO, do_fetch="--no-fetch" not in argv)
    print(json.dumps(s, indent=1, default=str) if "--json" in argv else render_status(s))
    return 0 if not s["errors"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
