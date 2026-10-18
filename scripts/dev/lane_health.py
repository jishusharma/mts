"""GPT lane health: is the Codex lab alive, and where do its cards go while it is not?

  python scripts/dev/lane_health.py status                    # plain words: lane state, rerouted and paused cards
  python scripts/dev/lane_health.py sweep [--apply] [--ship]  # scheduled: heartbeat check, reroute/pause/resume; --ship commits + ships the changes
  python scripts/dev/lane_health.py beat                      # the lab host says "alive" (codex_run.py tick does this)
  python scripts/dev/lane_health.py down "<why>" | up "<why>" # operator override
  python scripts/dev/lane_health.py classify <log>            # what error text the lane health would see in a Codex log

State: MyTradingSys/system/lane_state.json (git, so every host and the Control Room read the same). Rules, in one place:
- DOWN at once when a run died on an out-of-credits / usage-limit error (reason credits | limit), after 3 runs in a row that
  wrote nothing (reason failing), or when the lab host's heartbeat is older than HEARTBEAT_DOWN_S (reason heartbeat), or when the allowance
  window is spent (codex_run: 5-hour >= 85% / week >= WEEK_STOP; reason window, `until` = the reset: the lane comes back by itself, no probe).
- A down lane lets ONE card run as a probe every PROBE_S (crucial / gpt_only cards first, since only GPT may do them). A run that
  ends DONE or BLOCKED brings the lane back up; a fresh heartbeat brings a heartbeat-down lane back up.
- While down, a ready CODEX card is moved off the lane unless the card is flagged `crucial` or `gpt_only` (default off):
  run/audit cards get a DSA desk row with a prompt cut from the card (DSA bridge format, DSA_DELEGATION.md); build cards and
  cards that need to look at frames/images go to lane SONNET (DSA is text only). Flagged cards stay put, PAUSED with the reason shown on the Control Room.
- When the lane is up again: a DSA row nobody took is cancelled and the card is back on CODEX; a SONNET card nobody claimed
  goes back to CODEX; work already taken or done stays where it is. A finished DSA row closes its card. Paused cards resume
  by themselves (nothing skips them any more).
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks  # noqa: E402

REPO = tasks.REPO
STATE = "MyTradingSys/system/lane_state.json"
HEARTBEAT_DOWN_S = 3 * 3600     # the lab ticks every 30 min: 6 missed ticks = down
HEARTBEAT_WRITE_S = 3600        # a heartbeat is pushed at most hourly
HB_REF = "lane-heartbeat"       # B17: heartbeats go to this side branch (never trunk): 55 of 1822 commits in 72 h were an hourly heartbeat-only edit of lane_state.json
PROBE_S = 3600                  # a down lane lets one card try again this often
OVERRIDE_S = 3 * 3600            # operator "GPT is back": the allowance reading is not trusted for this long
FAILS_DOWN = 3                  # runs in a row that wrote nothing and hit no known error
TAIL = 4000                     # characters of a run log that are read for an error: the end, never the echoed prompt
CREDITS = re.compile(r"out of (?:credits?|tokens)|insufficient[_ ](?:credits?|quota|funds|balance)|no (?:remaining |more )?credits?|"
                     r"credits? (?:have been |are |is |were )?(?:exhausted|depleted|used up|run out)|run out of credits?|"
                     r"credit balance|(?:add|purchase|buy|top up)(?: more)? credits?|exceeded your (?:current )?quota|billing", re.I)
LIMIT = re.compile(r"usage limit|rate[ _]limit(?: reached| exceeded)?|too many requests|limit reached", re.I)
SAFE_FALLBACK = "SONNET"        # lane for rerouted build cards and for cards that need to SEE images (DSA is text only)
VISION = re.compile(r"\b(frames?|images?|png|jpe?g|screenshots?)\b", re.I)
REPORT_TEST = "Report file exists with the findings table or numbers and the verdict line; no code or spec changed"
HOLD_REASONS = ("credits", "limit", "failing")


def utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except (TypeError, ValueError):
        return 0.0


def classify(text):
    """'credits' | 'limit' | '' from the END of a Codex run log (the head holds the echoed prompt and repo text)."""
    tail = (text or "")[-TAIL:]
    if CREDITS.search(tail):
        return "credits"
    return "limit" if LIMIT.search(tail) else ""


def error_line(text):
    """The ERROR line a person should see on the Control Room (reset time included), cut to 200 characters."""
    hits = [ln.strip() for ln in (text or "")[-TAIL:].splitlines() if ln.strip().upper().startswith("ERROR") and (CREDITS.search(ln) or LIMIT.search(ln))]
    return hits[-1][:200] if hits else ""


# ---- state ----------------------------------------------------------------------------------------------------------------
def blank():
    return {"status": "up", "reason": "", "detail": "", "since": "", "heartbeat": "", "last_ok": "", "last_error": "",
            "last_probe": "", "fails": 0, "resumed": "", "until": "", "override": ""}


def load(repo=REPO):
    p = Path(repo) / STATE
    try:
        return {**blank(), **json.loads(p.read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        return blank()


def remote_heartbeat(repo, fetch=False):
    """Newest heartbeat on origin's HB_REF side branch ('' when there is none or git cannot say). Fail open: no signal is never 'down'."""
    try:
        if fetch:
            git(repo, "fetch", "--quiet", "origin", HB_REF, check=False)
        r = git(repo, "show", f"origin/{HB_REF}:heartbeat", check=False)
        return r.stdout.strip() if r.returncode == 0 and epoch(r.stdout.strip()) else ""
    except OSError:
        return ""


def push_heartbeat(repo, ts):
    """Write one heartbeat as a plumbing commit on the side branch HB_REF (parent = its tip) and push it. True when pushed."""
    try:
        def g(*args, stdin=None):
            r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, input=stdin)
            if r.returncode != 0:
                raise OSError(r.stderr)
            return r.stdout.strip()
        blob = g("hash-object", "-w", "--stdin", stdin=ts)
        tree = g("mktree", "-z", stdin=f"100644 blob {blob}" + chr(9) + "heartbeat" + chr(0))   # -z: text-mode stdin would turn the newline into CRLF on Windows
        parent = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "-q", f"origin/{HB_REF}"], capture_output=True, text=True)
        args = ["commit-tree", tree, "-m", f"heartbeat {ts}"] + (["-p", parent.stdout.strip()] if parent.returncode == 0 else [])
        commit = subprocess.run(["git", "-C", str(repo), "-c", "user.name=lane-health", "-c", "user.email=lane-health@local", *args],
                                capture_output=True, text=True)
        if commit.returncode != 0:
            return False
        return git(repo, "push", "--quiet", "origin", f"{commit.stdout.strip()}:refs/heads/{HB_REF}", check=False).returncode == 0
    except OSError:
        return False


def newest_heartbeat(st, repo):
    """The state's heartbeat, or the side branch's when that is newer (a fetched copy; no network call here)."""
    hb = remote_heartbeat(repo)
    return hb if epoch(hb) > epoch(st["heartbeat"]) else st["heartbeat"]


def save(repo, st):
    p = Path(repo) / STATE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return p


def go_down(st, reason, detail, now, until=None):
    """`until` (datetime): the allowance window resets then; the lane comes back up on its own (reason "window")."""
    st = dict(st)
    if st["status"] != "down":
        st.update(status="down", since=iso(now))
    st.update(reason=reason, detail=detail, last_error=iso(now), until=iso(until) if until else "", override="")
    return st


def go_up(st, now, why=""):
    st = dict(st)
    if st["status"] == "down":
        st["resumed"] = iso(now)
    st.update(status="up", reason="", detail=why, since="", fails=0, last_ok=iso(now), until="")
    return st


def record_run(st, outcome, error, now, detail=""):
    """Fold one Codex run into the state. `outcome` is codex_run's (DONE, BLOCKED, LIMIT, INCOMPLETE, ...), `error` classify()'s."""
    if outcome == "LIMIT" or error:
        return go_down(st, error or "limit", detail or "Codex run ended on an allowance/credit error", now)
    if outcome in ("DONE", "BLOCKED"):
        return go_up(st, now, "Codex run finished")
    if outcome == "INCOMPLETE":
        st = dict(st, fails=st["fails"] + 1)
        if st["fails"] >= FAILS_DOWN:
            return go_down(st, "failing", f"{st['fails']} runs in a row wrote nothing", now)
    return st


def override_active(st, now):
    """Operator said GPT is back: codex_run skips its allowance pre-check until this time (a real limit error still marks the lane down)."""
    return now.timestamp() < epoch(st.get("override", ""))


def beat(st, now):
    return dict(st, heartbeat=iso(now))


def sweep_state(st, now):
    """Heartbeat rule. No heartbeat ever recorded = no signal yet (never down on a fresh install)."""
    hb = epoch(st["heartbeat"])
    if st["status"] == "down" and st["reason"] == "window" and now.timestamp() >= epoch(st["until"]):
        return go_up(st, now, "allowance window reset")
    if not hb:
        return st
    if now.timestamp() - hb > HEARTBEAT_DOWN_S and st["status"] == "up":
        return go_down(st, "heartbeat", f"no heartbeat from the lab host since {st['heartbeat']}", now)
    if now.timestamp() - hb <= HEARTBEAT_DOWN_S and st["status"] == "down" and st["reason"] == "heartbeat":
        return go_up(st, now, "heartbeat is back")
    return st


def allow(st, now):
    """'go' (lane up), 'probe' (down, one card may try), '' (down, hold)."""
    if st["status"] == "up":
        return "go"
    if st["reason"] == "window" and now.timestamp() >= epoch(st["until"]):
        return "go"
    if st["reason"] in HOLD_REASONS and now.timestamp() - max(epoch(st["since"]), epoch(st["last_probe"])) >= PROBE_S:
        return "probe"
    return ""


def is_crucial(card):
    return bool(card.get("crucial") or card.get("gpt_only"))


def why_down(st):
    return f"GPT lane down since {st['since'] or '?'}: {st['reason']}" + (f" ({st['detail']})" if st["detail"] else "")


# ---- reroute plan -----------------------------------------------------------------------------------------------------------
def dsa_need(card, when):
    """Desk-row text for DSA from a CODEX card, in the DSA bridge format (DSA_DELEGATION.md 'Making DSA tasks cheap to succeed'):
    exact commands, worktree, one observable, stop condition, results only from printed output. No source line starts with a hash."""
    cid = card["id"]
    report = f"{tasks.LAB_REPORTS}/{when.strftime('%Y-%m-%d')}_{cid}.md"
    L = [f"Rerouted from the GPT lane (credits/limit/outage) to DSA. Card {cid}: {card['title']}",
         "Worktree: mts-dsa (python scripts/dev/sync.py start first). Data on F:\\MTS\\data is read-only.",
         f"Full brief: python scripts/dev/tasks.py brief {cid}",
         f"Goal: {card.get('goal', card['title'])}",
         "Read: " + "; ".join(card.get("scope_in", []))]
    L += [f"Step {i}: {s}" for i, s in enumerate(card.get("steps", []), 1)]
    if card.get("commands"):
        L += ["Run exactly:"] + [f"  {c}" for c in card["commands"]]
    L += [f"Write the report to {report}: findings or numbers, each with file:line or the command you ran.",
          "Numbers come only from output you printed in the chat. Change no code or spec. Never read a holdout.",
          "If a command fails twice, close the desk row with --failed and the error text.",
          f"Close: python scripts/dev/desk.py done <row id> --result \"<verdict or number + {report}>\"."]
    return "\n".join(line[:200] for line in L)


def needs_vision(card):
    """Frames, images and screenshots can be read by a Claude session, not by DSA (a text chat through a shell bridge)."""
    text = " ".join([card.get("title", ""), card.get("goal", "")] + card.get("scope_in", []))   # not steps: the audit template itself says "video frames"
    return bool(VISION.search(text))


def plan(st, cards, desk_rows, claimed):
    """What to do now. cards = all cards, desk_rows = {id: row}, claimed = set of claim slugs. Pure.
    -> {reroute: [(card, 'DSA'|lane)], paused: [(card, why)], restore: [card], cancel: [(card, desk id)],
        close: [(card, desk id)], clear: [(card, desk id)]}"""
    out = {k: [] for k in ("reroute", "paused", "restore", "cancel", "close", "clear")}
    down = st["status"] == "down"
    for c in cards:
        if c.get("state") in tasks.FINAL:
            continue
        rr = c.get("reroute") or {}
        if rr.get("to") == "DSA":
            row = desk_rows.get(rr.get("desk"))
            if row and row["status"] == "done":
                out["close"].append((c, rr["desk"]))
            elif row and row["status"] == "failed":
                out["clear"].append((c, rr["desk"]))
            elif not down and (not row or row["status"] == "pending"):
                out["cancel"].append((c, rr.get("desk", "")))
        elif rr.get("to") == SAFE_FALLBACK and not down and c.get("lane") == SAFE_FALLBACK and c["state"] == "ready" \
                and tasks_slug(c["id"]) not in claimed:
            out["restore"].append(c)
        elif c.get("lane") == "CODEX" and c["state"] == "ready" and down and not rr:
            if is_crucial(c):
                out["paused"].append((c, why_down(st)))
            elif c.get("reroute_failed"):
                out["paused"].append((c, f"DSA could not do it ({c['reroute_failed']}); waits for GPT"))
            else:
                out["reroute"].append((c, SAFE_FALLBACK if c.get("kind") == "build" or needs_vision(c) else "DSA"))
        elif c.get("lane") == "CODEX" and c["state"] == "ready" and down and is_crucial(c):
            out["paused"].append((c, why_down(st)))
    return out


def tasks_slug(cid):
    return re.sub(r"[^a-z0-9]+", "-", cid.lower()).strip("-")


def apply_plan(repo, pl, st, now):
    """Write the plan into the work tree (cards + desk rows). -> (changed paths, summary lines). Commits nothing."""
    import desk
    changed, lines = [], []
    for c, to in pl["reroute"]:
        if to == "DSA":
            rid = now.strftime("%Y%m%d-%H%M%S-") + tasks_slug(c["id"])[:40]
            row = {"id": rid, "title": c["title"], "need": dsa_need(c, now), "done_when": c.get("done_when", ""), "target": "DSA",
                   "from": "lane_health", "posted": iso(now), "status": "pending", "card": c["id"], "rerouted_from": "CODEX"}
            changed.append(str(desk.save(repo, row).relative_to(repo)))
            c["reroute"] = {"to": "DSA", "desk": rid, "at": iso(now), "why": st["reason"]}
            lines.append(f"{c['id']} -> DSA desk row {rid}")
        else:
            c.update(lane=to, reroute={"to": to, "from": "CODEX", "at": iso(now), "why": st["reason"]})
            if to in tasks.CODE_LANES and not c.get("worker"):
                c["est_turns"], c["worker"] = tasks.default_worker(c)
            if not str(c.get("tests", "")).strip():   # lane SONNET needs a test to be ready (Definition of Ready); undone on restore
                c["tests"] = REPORT_TEST
                c["reroute"]["added_tests"] = True
            lines.append(f"{c['id']} -> lane {to}")
        changed.append(str(tasks.save(repo, c).relative_to(repo)))
    for c, why in pl["paused"]:
        lines.append(f"{c['id']} PAUSED: {why}")
    for c in pl["restore"]:
        c["lane"] = "CODEX"
        if c["reroute"].get("added_tests"):
            c["tests"] = ""
        c.pop("reroute", None)
        changed.append(str(tasks.save(repo, c).relative_to(repo)))
        lines.append(f"{c['id']} back on CODEX (GPT is up, nobody had claimed it)")
    for c, rid in pl["cancel"]:
        row = desk.tasks(repo) and next((r for r in desk.tasks(repo) if r["id"] == rid), None)
        if row and row["status"] == "pending":
            row.update(status="failed", result="cancelled: GPT lane is back, card returned to CODEX", finished=iso(now), host="lane_health")
            changed.append(str(desk.save(repo, row).relative_to(repo)))
        c.pop("reroute", None)
        changed.append(str(tasks.save(repo, c).relative_to(repo)))
        lines.append(f"{c['id']} back on CODEX (GPT is up, desk row {rid or '-'} cancelled)")
    for c, rid in pl["close"]:
        row = next(r for r in desk.tasks(repo) if r["id"] == rid)
        result = f"via DSA ({rid}): {row.get('result', '')}"[:380]
        try:
            gate = tasks.review_gate(c, finishing=True, result=result)
        except Exception as e:   # fail closed: an unreadable gate leaves the card open
            gate = [f"review gate error: {e}"]
        if gate:
            lines.append(f"{c['id']} DSA row {rid} finished but card not closed: " + "; ".join(gate))
            continue
        c.update(state="done", result=result, closed=iso(now))
        changed.append(str(tasks.save(repo, c).relative_to(repo)))
        lines.append(f"{c['id']} closed from DSA row {rid}")
    for c, rid in pl["clear"]:
        c.pop("reroute", None)
        c["reroute_failed"] = rid
        changed.append(str(tasks.save(repo, c).relative_to(repo)))
        lines.append(f"{c['id']} DSA row {rid} failed; card stays on CODEX (paused while GPT is down)")
    return changed, lines


# ---- view (Control Room, status) ----------------------------------------------------------------------------------------------
def view(repo=REPO, cards=None, desk_rows=None, now=None):
    """JSON for the Control Room relay section."""
    import desk
    st, now = load(repo), now or utc()
    st["heartbeat"] = newest_heartbeat(st, repo)
    cards = tasks.load_all(repo) if cards is None else cards
    rows = {r["id"]: r for r in desk.tasks(repo)} if desk_rows is None else desk_rows
    pl = plan(st, cards, rows, set())
    moved = [{"id": c["id"], "title": c["title"], "to": (c["reroute"] or {}).get("to"), "desk": (c["reroute"] or {}).get("desk", ""),
              "desk_status": rows.get((c["reroute"] or {}).get("desk"), {}).get("status", "")}
             for c in cards if c.get("reroute") and c.get("state") not in tasks.FINAL]
    hb = epoch(st["heartbeat"])
    return {"status": st["status"], "reason": st["reason"], "detail": st["detail"], "since": st["since"], "resumed": st["resumed"],
            "heartbeat": st["heartbeat"], "heartbeat_age_h": round((now.timestamp() - hb) / 3600, 1) if hb else None,
            "next_probe": iso(datetime.fromtimestamp(max(epoch(st["since"]), epoch(st["last_probe"])) + PROBE_S, timezone.utc))
            if st["status"] == "down" and st["reason"] in HOLD_REASONS else "",
            "rerouted": moved,
            "paused": [{"id": c["id"], "title": c["title"], "why": why} for c, why in pl["paused"]]}


def status_text(v):
    L = [f"GPT lane: {v['status'].upper()}" + (f" ({v['reason']}) since {v['since']}" if v["status"] == "down" else "")
         + (f", heartbeat {v['heartbeat_age_h']} h ago" if v["heartbeat_age_h"] is not None else ", no heartbeat yet")]
    if v["detail"]:
        L.append(f"  {v['detail']}")
    if v["next_probe"]:
        L.append(f"  next probe (one card tries GPT again): {v['next_probe']}")
    if v["resumed"] and v["status"] == "up":
        L.append(f"  back up since {v['resumed']}")
    L += [f"  moved to {m['to']}: {m['id']}" + (f" (desk {m['desk']} {m['desk_status'] or 'missing'})" if m["desk"] else "") for m in v["rerouted"]]
    L += [f"  PAUSED (waits for GPT): {p['id']}: {p['why']}" for p in v["paused"]]
    return "\n".join(L)


# ---- running it -----------------------------------------------------------------------------------------------------------------
def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check)


def commit_ship(repo, paths, msg):
    """Commit exactly `paths` and run sync.py ship. Skips (False) when the tree holds other uncommitted work: that is never ours to ship."""
    paths = [str(x).replace(chr(92), "/") for x in paths]   # Windows callers pass relative_to() paths with backslashes; git status prints forward slashes
    others = [line for line in git(repo, "status", "--porcelain").stdout.splitlines() if line[3:].strip().strip('"') not in paths]
    if others:
        return False
    if not git(repo, "status", "--porcelain", "--", *paths).stdout.strip():
        return True   # nothing changed
    git(repo, "add", "--", *paths)
    git(repo, "commit", "-q", "-m", msg, "--", *paths)
    return subprocess.run([sys.executable, str(Path(repo) / "scripts/dev/sync.py"), "ship"], cwd=str(repo)).returncode == 0


def read_claimed(repo):
    try:
        import sync
        return {slug for slug, _ in sync.read_claims(repo, f"origin/{sync.TRUNK}")}
    except Exception:   # no git remote (tests, fresh clone): treat as nothing claimed
        return set()


def sweep(repo=REPO, now=None, do_apply=False, do_ship=False, beating=False):
    """One scheduled check. -> one report line (the Haiku watcher prints it verbatim)."""
    import desk
    now = now or utc()
    old = load(repo)
    remote_hb = remote_heartbeat(repo, fetch=True)
    seen = dict(old, heartbeat=remote_hb if epoch(remote_hb) > epoch(old["heartbeat"]) else old["heartbeat"])
    st = sweep_state(seen, now)
    hb_in_file = False   # a heartbeat that is not on the side branch has to go through the state file (no remote: tests, fresh clone)
    if beating and (epoch(seen["heartbeat"]) + HEARTBEAT_WRITE_S <= now.timestamp() or st["status"] != old["status"]):
        st = beat(st, now)
        hb_in_file = not push_heartbeat(repo, st["heartbeat"])
    cards = tasks.load_all(repo)
    pl = plan(st, cards, {r["id"]: r for r in desk.tasks(repo)}, read_claimed(repo))
    changed, lines = [], []
    if do_apply:
        changed, lines = apply_plan(repo, pl, st, now)
    else:
        lines = [f"{c['id']} would go to {to}" for c, to in pl["reroute"]] + [f"{c['id']} PAUSED" for c, _ in pl["paused"]]
    if {k: v for k, v in st.items() if k != "heartbeat"} != {k: v for k, v in old.items() if k != "heartbeat"}             or (hb_in_file and st["heartbeat"] != old["heartbeat"]):
        changed.append(str(save(repo, st).relative_to(repo)))
    elif git(repo, "status", "--porcelain", "--", STATE, check=False).stdout.strip():
        changed.append(STATE)   # state written by codex_run (window spent): ship it too, a dirty tree would stop the next tick
    shipped = ""
    if do_ship and changed:
        ok = commit_ship(repo, sorted(set(changed)), f"lane health: GPT {st['status']}" + (f" ({st['reason']})" if st["reason"] else "")
                         + f"\n\nResult: {len(lines)} card change(s); " + (why_down(st) if st["status"] == "down" else "GPT lane up") + "\n")
        shipped = " shipped" if ok else " NOT-SHIPPED"
    return (f"LANE gpt={st['status']}" + (f" reason={st['reason']}" if st["reason"] else "") + f" moved={len(pl['reroute'])}"
            f" paused={len(pl['paused'])} restored={len(pl['restore']) + len(pl['cancel'])} closed={len(pl['close'])}{shipped}"
            + ("".join(f"\n  {x}" for x in lines)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status")
    s = sp.add_parser("sweep")
    s.add_argument("--apply", action="store_true")
    s.add_argument("--ship", action="store_true")
    s.add_argument("--beat", action="store_true", help="this host runs the lab: record its heartbeat")
    sp.add_parser("beat")
    for n in ("down", "up"):
        sp.add_parser(n).add_argument("why")
    sp.add_parser("classify").add_argument("log")
    a = ap.parse_args(argv)
    if a.cmd == "status":
        print(status_text(view(REPO)))
    elif a.cmd == "sweep":
        print(sweep(REPO, None, a.apply or a.ship, a.ship, a.beat))
    elif a.cmd == "beat":
        save(REPO, beat(load(REPO), utc()))
    elif a.cmd in ("down", "up"):
        now, st = utc(), load(REPO)
        if a.cmd == "down":
            st = go_down(st, "manual", a.why, now)
        else:
            st = go_up(st, now, a.why)
            st["override"] = iso(now + timedelta(seconds=OVERRIDE_S))
        save(REPO, st)
        print(f"lane {a.cmd}; run `lane_health.py sweep --apply --ship` to move cards and ship")
    else:
        print(classify(Path(a.log).read_text(encoding="utf-8", errors="replace")) or "no error text found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
