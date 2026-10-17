"""Task cards: the refinement stage between an idea (Inbox item, registry row, follow-up) and a session that runs it.

  python scripts/dev/tasks.py new "<title>" [--id B170] [--ref B170] [--lane SONNET] [--prio 3] [--from-inbox <fb id>] [--layer tom]
  python scripts/dev/tasks.py check [<id>]          # Definition of Ready; promotes raw/refined -> ready when it passes (fail closed)
  python scripts/dev/tasks.py lint                  # every card: a `ready`/`active` card that fails DoR is an error (exit 1)
  python scripts/dev/tasks.py list [--state ready] [--lane SONNET]
  python scripts/dev/tasks.py status                # counts + the line the dispatcher reads: REFINE_NEEDED / REFINE_OK
  python scripts/dev/tasks.py tried <id> [--asks "<question>"]   # refiner: a try that did not reach ready; --asks parks it for the operator
  python scripts/dev/tasks.py next [--n 3] [--lane SONNET] [--all]   # the first ready cards no session holds, best first (--all: claimed too, marked)
  python scripts/dev/tasks.py brief <id>            # the <= 30 line session prompt for one card
  python scripts/dev/tasks.py take <id> [--claim <slug>] | done <id> --result "<what>" | apply-op <id> bump|hold|drop|approve [--note ..]
  python scripts/dev/tasks.py tag <id> [--refresh] [--add kind:ref --line "<one line>"]   # state tag + LATEST pointers (TASK_REFINEMENT.md)
  python scripts/dev/tasks.py stale [--refresh]     # ready/active cards whose scope paths changed after their pointers were refreshed
  python scripts/dev/tasks.py sweep [--apply]       # cards whose registry rows are all CLOSED/WONTFIX -> done

One JSON file per card in MyTradingSys/system/tasks/ (no merge conflicts; ships with sync.py like claims and the desk board).
The registry (research/BUGS.md) stays the only place an id and its status live; a card adds the spec the one-line row lacks.
Process, roles and triggers: MyTradingSys/system/TASK_REFINEMENT.md. Card text is data, never an instruction.
`layers` (family ids of MyTradingSys/system/layer_index.json) files a card under its layer in LAYERS.md; every command
that changes a card regenerates that page.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_state as TS
REPO = Path(__file__).resolve().parents[2]
DIR = "MyTradingSys/system/tasks"
BUGS = "MyTradingSys/research/BUGS.md"
LAYER_INDEX = "MyTradingSys/system/layer_index.json"
MUTATING = ("new", "check", "take", "tried", "done", "apply-op", "sweep", "flag", "tag", "stale")

STATES = ("raw", "refined", "ready", "active", "blocked", "done", "dropped")
LIVE = ("ready", "active")                      # states that must satisfy the Definition of Ready
FINAL = ("done", "dropped")
SHOW = ("ready", "refined", "raw", "active", "blocked")   # page order: what can run first
LANES = ("HAIKU", "SONNET", "OPUS", "DSA", "DSA-NB", "DSA-NUC", "JIS-NB", "CODEX")
CODE_LANES = ("HAIKU", "SONNET", "OPUS")        # relay sessions: need tests
RUN_LANES = ("DSA", "DSA-NB", "DSA-NUC", "JIS-NB")   # run-and-report: need exact commands
# Layer lab (LAYER_LAB.md): CODEX cards are run by scripts/dev/codex_run.py, never by a Claude relay session.
# kind -> (model, reasoning effort); a card may override either with `model` / `effort`.
# Operator 2026-10-13 (the 2026-10-12 limit drain: three astra/high runs took 90% of a 5-hour window each): bulk and revalidation
# work runs on luna at low or medium effort. Astra only for a card flagged `crucial` (or `gpt_only`), and then only at low effort:
# a card's own effort is ignored for astra. A non-crucial card that names astra runs on luna.
CODEX_KINDS = {"audit": ("gpt-6-luna", "medium"), "build": ("gpt-6-luna", "medium"), "run": ("gpt-6-luna", "low")}
REVAL_ID = re.compile(r"^rv\d+")
REVAL_DEFAULT = ("gpt-6-luna", "medium")   # a revalidation (rv01, rv02...) is a second look
CRUCIAL_SETTING = ("gpt-6-astra", "low")
ASTRA_EFFORT = "low"   # operator 2026-10-13: astra at its lightest effort only, never medium or high, whatever the card says
CODEX_EFFORTS = ("low", "medium", "high", "xhigh", "max")
LAB_REPORTS = "MyTradingSys/research/layer_lab/reports"
SIZES = ("S", "M", "L")
WEIGHTS = ("ROUTINE", "IMPORTANT", "CRUCIAL", "CRITICAL")   # optional card field; Session_Planner Duty 5
WORKERS = ("agent", "session")                   # WORKERS.md: who runs the card; set during refinement
AGENT_MAX_TURNS = 15                             # WORKERS.md: a one-use Agent only for <= 15 turns and size S
SESSION_MAX_TURNS = 40                           # RELAY.md hand-over cap: a card needing more is split
MAX_TRIES = 2                                    # refiner attempts per card; then it is parked, not retried every tick
BUFFER = 3                                       # ready cards to keep in stock before the refiner stops
MAX_BRIEF = 30                                   # RELAY.md Task list standard: block <= 30 lines
MAX_FIELD = 400                                  # chars per text field: a card is a prompt, not an essay
PLACEHOLDER = re.compile(r"\b(TBD|TODO|figure out|\?\?|to be decided)\b", re.I)
TEXT = ("title", "goal", "done_when", "tests")
LISTS = ("scope_in", "scope_out", "steps", "commands", "sources", "refs", "depends_on", "layers")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tdir(repo=REPO):
    return Path(repo) / DIR


def path_of(repo, cid):
    return tdir(repo) / f"{cid}.json"


def save(repo, card):
    p = path_of(repo, card["id"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(card, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return p


def load_all(repo=REPO):
    d = tdir(repo)
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))] if d.is_dir() else []


def get(repo, cid):
    p = path_of(repo, cid)
    if not p.is_file():
        raise SystemExit(f"tasks: no card {cid}")
    return json.loads(p.read_text(encoding="utf-8"))


def registry(repo=REPO):
    """{id: STATUS} from the BUGS.md rows (B-/T- ids). Missing file -> {}."""
    p = Path(repo) / BUGS
    out = {}
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if line.startswith("|") and len(c) >= 5 and re.fullmatch(r"[BT]-?\d+", c[0]):
                out[c[0]] = c[2]
    return out


def layer_families(repo=REPO):
    """Family ids a card's `layers` may name; empty when the index is absent (a test repo)."""
    p = Path(repo) / LAYER_INDEX
    return [f["id"] for f in json.loads(p.read_text(encoding="utf-8"))["families"]] if p.is_file() else []


def refresh_layers(repo=REPO):
    """Regenerate LAYERS.md after a card change, so its open-card lists never go stale. Never fails the card command."""
    if not (Path(repo) / LAYER_INDEX).is_file():
        return
    try:
        import make_layers_md
        make_layers_md.write(repo)
    except Exception as e:   # the card change already landed; say so, do not hide it
        print(f"tasks: LAYERS.md not regenerated: {e}")


def blank(cid, title, **kw):
    return {"id": cid, "title": title, "state": "raw", "prio": kw.get("prio", 3), "lane": kw.get("lane", ""), "size": "", "est_turns": None, "worker": "", "weight": "",
            "layers": kw.get("layers", []),
            "goal": "", "scope_in": [], "scope_out": [], "steps": [], "commands": [], "tests": "", "done_when": "",
            "sources": [], "depends_on": [], "refs": kw.get("refs", []), "live_path": False, "approved_by": "",
            "from_inbox": kw.get("from_inbox", ""), "refine_tries": 0, "asks": "", "created": now(), "refined_by": "", "note": "", "result": ""}


def worker_problems(card):
    """WORKERS.md: the worker type is chosen up front from the estimated turns; agent only for size S and <= AGENT_MAX_TURNS."""
    p = []
    t, w = card.get("est_turns"), card.get("worker")
    if not isinstance(t, int) or isinstance(t, bool) or t < 1:
        p.append("est_turns must be a whole number of expected assistant turns (>= 1)")
    elif t > SESSION_MAX_TURNS:
        p.append(f"est_turns {t} > {SESSION_MAX_TURNS}: split the card (hand-over cap)")
    if w not in WORKERS:
        p.append(f"worker must be one of {', '.join(WORKERS)} (WORKERS.md)")
    elif w == "agent" and isinstance(t, int) and (t > AGENT_MAX_TURNS or card.get("size") != "S"):
        p.append(f"worker agent only for size S and est_turns <= {AGENT_MAX_TURNS}: make it a session")
    return p


def default_worker(card):
    """(est_turns, worker) for a card that gets a Claude lane without refinement (CI red card, lane reroute); the refiner sets real ones."""
    return (12, "agent") if card.get("size") == "S" else (30, "session")


def problems(card, cards=None, reg=None):
    """Definition of Ready: [] when a session can run the card with no question to anyone. Every miss is named."""
    p = []
    card_list = cards or []
    cards = {c["id"]: c for c in card_list}
    reg = reg or {}
    for k in TEXT[:3]:
        if not str(card.get(k, "")).strip():
            p.append(f"{k} is empty")
    for k in ("scope_in", "steps"):
        if not card.get(k):
            p.append(f"{k} is empty")
    w = card.get("weight") or ""
    if w and w not in WEIGHTS:
        p.append(f"weight {w!r} not one of {', '.join(WEIGHTS)}")
    lane = card.get("lane", "")
    if lane not in LANES:
        p.append(f"lane {lane!r} not one of {', '.join(LANES)}")
    if card.get("size") not in ("S", "M"):
        p.append("size must be S or M (L = split it into cards that fit one session, ~50k tokens)" if card.get("size") == "L"
                 else "size is empty (S or M)")
    if lane in CODE_LANES:
        p.extend(worker_problems(card))
    if lane in CODE_LANES and not str(card.get("tests", "")).strip():
        p.append("tests is empty (code lane: name the fail-first test)")
    if lane in RUN_LANES and not card.get("commands"):
        p.append("commands is empty (run lane: paste copy-ready commands)")
    if lane == "CODEX":
        kind = card.get("kind", "")
        if kind not in CODEX_KINDS:
            p.append(f"kind {kind!r} not one of {', '.join(CODEX_KINDS)} (lane CODEX)")
        if kind == "build" and not str(card.get("tests", "")).strip():
            p.append("tests is empty (CODEX build: name the fail-first test)")
        if kind == "run" and not card.get("commands"):
            p.append("commands is empty (CODEX run: paste copy-ready commands)")
        if card.get("effort") and card["effort"] not in CODEX_EFFORTS:
            p.append(f"effort {card['effort']!r} not one of {', '.join(CODEX_EFFORTS)}")
    fams = layer_families()
    for x in card.get("layers", []):
        if fams and x not in fams:
            p.append(f"layers: {x!r} is not a family in {LAYER_INDEX} ({', '.join(fams)})")
    if lane == "OPUS" and not card.get("approved_by"):
        p.append("lane OPUS needs approved_by (operator names Opus; CLAUDE.md)")
    if lane == "OPUS" and not str(card.get("crucial", "")).strip():
        p.append("lane OPUS needs crucial: one line on why only Opus fits (live money, irreversible data, or a no-undo design call; WORKERS.md rule 6)")
    if card.get("live_path") and lane != "JIS-NB":
        p.append("live_path card must be lane JIS-NB (desk task; builders never touch the live tree or restart)")
    for k in TEXT + LISTS:
        v = card.get(k, "")
        for s in (v if isinstance(v, list) else [v]):
            if PLACEHOLDER.search(str(s)):
                p.append(f"{k} has a placeholder ({PLACEHOLDER.search(str(s)).group(0)})")
            if len(str(s)) > MAX_FIELD:
                p.append(f"{k} item over {MAX_FIELD} chars: shorten or link a file")
    for d in card.get("depends_on", []):
        c = cards.get(d)
        if c is not None:
            if c["state"] != "done":
                p.append(f"depends_on {d} is {c['state']}")
        elif reg.get(d) not in ("CLOSED", "WONTFIX"):
            p.append(f"depends_on {d} is {reg.get(d, 'unknown')}")
    if card.get("flow"):
        import lab_flow
        p += lab_flow.gate(card, card_list, REPO)
    if len(brief(card).splitlines()) > MAX_BRIEF:
        p.append(f"brief is over {MAX_BRIEF} lines: fewer steps or split the card")
    return sorted(set(p))


def brief(card):
    """The session prompt for one card. <= 30 lines by lint."""
    L = [f"TASK {card['id']} [{card.get('lane', '?')}, size {card.get('size') or '?'}, {card.get('worker') or '?'} ~{card.get('est_turns') or '?'} turns, prio {card.get('prio', '?')}]: {card['title']}",
         f"Goal: {card.get('goal', '')}",
         f"Scope in: {'; '.join(card.get('scope_in', []))}" + (f" | out: {'; '.join(card['scope_out'])}" if card.get("scope_out") else "")]
    if card.get("weight"):
        L.insert(2, f"Weight: {card['weight']}")
    L += [f"{i}. {s}" for i, s in enumerate(card.get("steps", []), 1)]
    if card.get("commands"):
        L += ["Commands:"] + [f"  {c}" for c in card["commands"]]
    if card.get("tests"):
        L.append(f"Tests (fail on old code first): {card['tests']}")
    L.append(f"Done when: {card.get('done_when', '')}")
    if card.get("sources"):
        L.append(f"Sources: {'; '.join(card['sources'])}")
    if card.get("refs"):
        L.append(f"Registry: {' '.join(card['refs'])}")
    if card.get("layers"):
        L.append(f"Layer: {', '.join(card['layers'])}: read its section of MyTradingSys/system/LAYERS.md (spec, ledger, backtests, cards)")
    if card.get("flow"):
        f = card["flow"]
        L.append(f"Flow {f['id']} stage {f['stage']} ({f['recipe']}): {f['lens']}")
        L += [f"C{i + 1}: {criterion}" for i, criterion in enumerate(f["criteria"])]
        L.append("Predecessor receipt/report: " + ", ".join(card.get("depends_on", [])) + "; read its card JSON for the report path.")
    if card.get("lane") == "CODEX":
        L.append(f"Report: {LAB_REPORTS}/<UTC date>_{card['id']}.md (findings or numbers, each with file:line or command)")
    if card.get("flow"):
        L.append(f"Close: python scripts/dev/lab_flow.py finish {card['id']} --report REPORT_PATH --verdict PASS|REWORK|BLOCKED --result \"evidence summary\"; runner ships.")
    else:
        L.append(f"Close: sync.py claim, work, tasks.py done {card['id']} --result \"<number/file>\", sync.py ship --release <slug>; report it shipped only with an empty `git cherry origin/fast-track <sha>`.")
    return "\n".join(L)


def codex_setting(card):
    """(model, effort) a CODEX card runs with: the kind's default unless the card names its own."""
    model, effort = CODEX_KINDS[card["kind"]]
    crucial = bool(card.get("crucial") or card.get("gpt_only"))
    if card["kind"] == "audit" and REVAL_ID.match(str(card.get("id", ""))):
        model, effort = REVAL_DEFAULT
    if crucial:
        model, effort = CRUCIAL_SETTING
    model, effort = card.get("model") or model, card.get("effort") or effort
    if model == CRUCIAL_SETTING[0] and not crucial:
        model = CODEX_KINDS["build"][0]   # astra is the scarce model: a card that is not crucial may not spend it
    elif model == CRUCIAL_SETTING[0]:
        effort = ASTRA_EFFORT
    return model, effort


def rank(card):
    return (not card.get("pinned", False), card.get("prio", 3), card.get("created", ""))


def ready_cards(repo=REPO, lane=None):
    cards = load_all(repo)
    byid = {c["id"]: c for c in cards}
    reg = registry(repo)
    out = [c for c in cards if c["state"] == "ready" and (not lane or c["lane"] == lane) and not problems(c, cards, reg)]
    return sorted(out, key=rank), byid


def open_claims(repo):
    """{claim slug: claim fields} of the claim files on origin/fast-track, read with sync.py's own reader (as of the last fetch).
    {} when git or the ref is unavailable (a test repo, a fresh clone): the claim itself stays the lock, `sync.py claim` refuses."""
    import sync   # scripts/dev is on sys.path wherever tasks.py runs or is imported by name
    try:
        return dict(sync.read_claims(repo, f"origin/{sync.TRUNK}"))
    except (OSError, sync.SyncError):
        return {}


def claim_of(card, claims):
    """The open claim on this card, or None: `sync.py claim <id>` files it under slugify(id) (lower case, 40 chars)."""
    import sync
    return claims.get(sync.slugify(card["id"]))


def counts(cards):
    return {s: sum(c["state"] == s for c in cards) for s in STATES}


def refinable(card):
    """A card the refiner may work on now: waiting, no open question for the operator, tries left."""
    return card["state"] in ("raw", "refined") and not card.get("asks") and card.get("refine_tries", 0) < MAX_TRIES


def status_line(cards):
    """REFINE_NEEDED only while work the refiner can actually do waits; parked cards (asked the operator, or tried
    MAX_TRIES times) never keep it on, so a stuck card cannot start a session every tick."""
    n = counts(cards)
    todo = sum(refinable(c) for c in cards)
    parked = n["raw"] + n["refined"] - todo
    # The buffer is for relay builders: ready run-lane cards (DSA, JIS-NB) cannot be taken by them, so they do not count
    # (2026-10-11: three ready DSA cards kept REFINE_OK while 17 cards waited and builders had one task).
    ready = sum(c["state"] == "ready" and c.get("lane") in CODE_LANES for c in cards)
    tail = f"refinable={todo} parked={parked} ready={n['ready']} builder_ready={ready} buffer={BUFFER}"
    return ("REFINE_NEEDED " if todo > 0 and ready < BUFFER else "REFINE_OK ") + tail


def summary(repo=REPO):
    """Compact rows for the Control Room page (open cards only, best first) + counts."""
    cards = load_all(repo)
    reg = registry(repo)
    rows = []
    for c in sorted((c for c in cards if c["state"] in SHOW), key=lambda c: (SHOW.index(c["state"]), rank(c))):
        miss = problems(c, cards, reg) if c["state"] != "raw" else []
        rows.append({"id": c["id"], "title": c["title"], "state": c["state"], "prio": c.get("prio", 3), "lane": c.get("lane", ""),
                     "size": c.get("size", ""), "goal": c.get("goal", ""), "done_when": c.get("done_when", ""),
                     "pinned": bool(c.get("pinned")), "needs_approval": c.get("lane") == "OPUS" and not c.get("approved_by"),
                     "missing": miss[:4], "note": c.get("note", ""), "asks": c.get("asks", ""),
                     "parked": c["state"] in ("raw", "refined") and not refinable(c)})
    return {"counts": counts(cards), "line": status_line(cards), "rows": rows}


# ---- commands --------------------------------------------------------------------------------------------------

def cmd_new(a):
    cid = a.id or re.sub(r"[^a-z0-9]+", "-", a.title.lower()).strip("-")[:40]
    if path_of(REPO, cid).exists():
        raise SystemExit(f"tasks: card {cid} exists")
    fams = layer_families()
    bad = [x for x in (a.layer or []) if x not in fams]
    if bad:
        raise SystemExit(f"tasks: unknown layer {', '.join(bad)}; families: {', '.join(fams)}")
    card = blank(cid, a.title, prio=a.prio, lane=a.lane or "", refs=a.ref or [], from_inbox=a.from_inbox or "", layers=a.layer or [])
    if a.kind:
        card["kind"] = a.kind
    if a.crucial:
        card["crucial"] = True
    print(f"wrote {save(REPO, card)} (state raw; refine it, then `tasks.py check {cid}`)")


def cmd_check(a):
    cards = load_all(REPO)
    reg = registry(REPO)
    bad = 0
    for c in cards:
        if (a.id and c["id"] != a.id) or c["state"] not in ("raw", "refined", "ready", "active"):
            continue
        miss = problems(c, cards, reg)
        if not miss:
            if c["state"] in ("raw", "refined"):
                c.update(state="ready", asks="")
                TS.refresh(c, REPO, now())
                save(REPO, c)
                print(f"{c['id']}: READY (promoted)")
            else:
                late = TS.overdue(c, REPO)
                if late and not a.id:
                    bad += 1
                if late or a.id:
                    print(f"{c['id']}: {c['state']} and passes" + (f" but STALE: {late}" if late else ""))
        elif a.id or c["state"] in LIVE:
            bad += c["state"] in LIVE
            if c["state"] in LIVE and a.demote:
                c["state"] = "refined"
                save(REPO, c)
            print(f"{c['id']}: NOT READY ({c['state']}): " + "; ".join(miss))
        elif c["state"] == "raw" and a.id:
            print(f"{c['id']}: raw: " + "; ".join(miss))
    return 1 if bad and not a.id else 0


def cmd_lint(a):
    cards = load_all(REPO)
    reg = registry(REPO)
    errs = []
    warns = []
    for c in cards:
        if c["state"] not in STATES:
            errs.append(f"{c['id']}: unknown state {c['state']!r}")
        elif c["state"] in LIVE:
            errs += [f"{c['id']} ({c['state']}): {m}" for m in problems(c, cards, reg)]
            if c["state"] == "ready":
                late = TS.overdue(c, REPO)
                if late:          # a warning, never a failure: lint feeds every ship gate and trunk CI (red 2026-10-17 07:36)
                    warns.append(f"WARN {c['id']} (ready): STALE {late}; run `tasks.py tag {c['id']} --refresh` after re-reading the card")
        if c["id"] + ".json" != path_of(REPO, c["id"]).name:
            errs.append(f"{c['id']}: file name differs from id")
    print("\n".join(errs + warns) if errs else "\n".join(warns + [f"tasks lint: {len(cards)} cards OK | {status_line(cards)}"]))
    return 1 if errs else 0


def cmd_list(a):
    for c in load_all(REPO):
        if (not a.state or c["state"] == a.state) and (not a.lane or c["lane"] == a.lane):
            print(f"{c['id']:<24} {c['state']:<8} p{c.get('prio', 3)} {c.get('lane', '-'):<8} {c.get('size') or '-':<2} {c['title'][:70]}")


def cmd_status(a):
    cards = load_all(REPO)
    n = counts(cards)
    print(" | ".join(f"{s} {n[s]}" for s in STATES))
    print(status_line(cards))


def cmd_next(a):
    cs, _ = ready_cards(REPO, a.lane)
    if not a.lane:   # CODEX cards belong to the layer-lab runner; a Claude session asking "what next" never sees them
        cs = [c for c in cs if c["lane"] != "CODEX"]
    held = open_claims(REPO)
    free = [c for c in cs if not claim_of(c, held)]
    shown = cs if a.all else free
    if not shown:
        n_held = len(cs) - len(free)
        print("NO_READY_CARD: run the refiner (TASK_REFINEMENT.md) or hand off with --stop"
              + (f" ({n_held} ready card(s) held by an open claim; `tasks.py next --all` lists them)" if n_held else ""))
        return 1
    for c in shown[:a.n]:
        owner = claim_of(c, held) if a.all else None
        note = f" (claimed by {owner.get('host', '?')}/{owner.get('account', '?')})" if owner else ""
        print(f"{c['id']} [{c['lane']}, {c['size']}, p{c['prio']}] {c['title']}{note}")
    return 0


def cmd_brief(a):
    c = get(REPO, a.id)
    miss = problems(c, load_all(REPO), registry(REPO))
    if miss:
        raise SystemExit(f"tasks: {a.id} is not ready: " + "; ".join(miss))
    print(brief(c))
    print(chr(10).join(TS.latest_block(c, REPO, TS.state_tag(c, REPO, claim_of(c, open_claims(REPO)), registry(REPO)))))


def cmd_tag(a):
    """Print the state tag + LATEST block; --refresh recomputes the pointers, --add records a manual one (decision, signal...)."""
    c = get(REPO, a.id)
    if a.add:
        kind, _, ref = a.add.partition(":")
        TS.add_entry(c, kind, ref, now(), a.line or "")
    if a.refresh or a.add:
        TS.refresh(c, REPO, now())
        save(REPO, c)
    print(chr(10).join(TS.latest_block(c, REPO, TS.state_tag(c, REPO, claim_of(c, open_claims(REPO)), registry(REPO)))))


def cmd_stale(a):
    """Ready/active cards whose scope changed after their pointers were refreshed (exit 1 when any are listed and not refreshed)."""
    hit = 0
    for c in load_all(REPO):
        why = TS.stale_reason(c, REPO)
        if why:
            hit += 1
            print(f"{c['id']} ({c['state']}): {why}" + (" -> refreshed" if a.refresh else ""))
            if a.refresh:
                TS.refresh(c, REPO, now())
                save(REPO, c)
    if not hit:
        print("stale: every ready/active card's pointers match its scope")
    return 1 if hit and not a.refresh else 0


def cmd_take(a):
    c = get(REPO, a.id)
    if c["state"] != "ready":
        raise SystemExit(f"tasks: {a.id} is {c['state']}, only a ready card can be taken")
    miss = problems(c, load_all(REPO), registry(REPO))
    if miss:
        raise SystemExit(f"tasks: {a.id} fails the Definition of Ready: " + "; ".join(miss))
    c.update(state="active", claim=a.claim or "", taken=now())
    save(REPO, c)
    print(f"{a.id}: active")


def cmd_tried(a):
    """Refiner: record a try that did not end `ready`. --asks parks the card until the operator answers (`apply-op retry`)."""
    c = get(REPO, a.id)
    c["refine_tries"] = c.get("refine_tries", 0) + 1
    if a.asks:
        c["asks"] = a.asks[:300]
    save(REPO, c)
    print(f"{a.id}: try {c['refine_tries']}/{MAX_TRIES}" + (" parked: asks the operator" if c.get("asks") else " parked: no tries left" if not refinable(c) else ""))


def cmd_done(a):
    c = get(REPO, a.id)
    if c.get("flow"):
        raise SystemExit("tasks: flow cards close through lab_flow.py finish (evidence receipt required)")
    c.update(state="done", result=a.result, closed=now())
    head = TS.git(REPO, "rev-parse", "--short", "HEAD")
    if head:   # base the work was done on; the ship commit that carries this card becomes the tag (SHIPPED@<sha>)
        TS.add_entry(c, "ship", head, c["closed"], a.result)
    save(REPO, c)
    print(f"{a.id}: done")


def cmd_flag(a):
    """crucial / gpt_only: a CODEX card with either waits for GPT when the lane is down (lane_health.py); default off."""
    c = get(REPO, a.id)
    if a.off:
        c.pop(a.flag, None)
    else:
        c[a.flag] = True
    save(REPO, c)
    print(f"{a.id}: {a.flag} {'off' if a.off else 'on'}")


def cmd_apply_op(a):
    """Operator action from the Control Room (db taskops/<id>), applied by the pickup session."""
    c = get(REPO, a.id)
    if a.op == "bump":
        c.update(prio=1, pinned=True)
    elif a.op == "hold":
        c.update(state="blocked", pinned=False)
    elif a.op == "drop":
        c.update(state="dropped", pinned=False)
    elif a.op == "approve":
        c["approved_by"] = "operator"
    elif a.op == "release" and c["state"] == "blocked":
        c["state"] = "refined"
    elif a.op == "retry":
        c.update(refine_tries=0, asks="")
    if a.note:
        c["note"] = a.note[:300]
    save(REPO, c)
    print(f"{a.id}: {a.op} -> {c['state']}")


def cmd_sweep(a):
    cards = load_all(REPO)
    reg = registry(REPO)
    hit = 0
    for c in cards:
        refs = c.get("refs", [])
        if c["state"] not in FINAL and refs and all(reg.get(r) in ("CLOSED", "WONTFIX") for r in refs):
            hit += 1
            print(f"{c['id']}: all refs {' '.join(refs)} closed -> done" + ("" if a.apply else " (dry run)"))
            if a.apply:
                c.update(state="done", result=c.get("result") or "registry rows closed", closed=now())
                save(REPO, c)
    if not hit:
        print("sweep: nothing to retire")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    n = sp.add_parser("new")
    n.add_argument("title")
    n.add_argument("--id")
    n.add_argument("--ref", action="append")
    n.add_argument("--lane", choices=LANES)
    n.add_argument("--prio", type=int, default=3, choices=range(1, 6))
    n.add_argument("--from-inbox")
    n.add_argument("--kind", choices=tuple(CODEX_KINDS), help="lane CODEX only: audit | build | run")
    n.add_argument("--layer", action="append", help="layer family id (layer_index.json); repeat for several")
    n.add_argument("--crucial", action="store_true", help="lane CODEX: when the GPT lane is down this card waits for GPT instead of moving to DSA/Claude")
    n.set_defaults(f=cmd_new)
    c = sp.add_parser("check")
    c.add_argument("id", nargs="?")
    c.add_argument("--demote", action="store_true", help="send a ready/active card that now fails back to refined")
    c.set_defaults(f=cmd_check)
    sp.add_parser("lint").set_defaults(f=cmd_lint)
    ls = sp.add_parser("list")
    ls.add_argument("--state", choices=STATES)
    ls.add_argument("--lane", choices=LANES)
    ls.set_defaults(f=cmd_list)
    sp.add_parser("status").set_defaults(f=cmd_status)
    nx = sp.add_parser("next")
    nx.add_argument("--n", type=int, default=3)
    nx.add_argument("--lane", choices=LANES)
    nx.add_argument("--all", action="store_true", help="also list cards that hold an open claim, marked with the claimant")
    nx.set_defaults(f=cmd_next)
    b = sp.add_parser("brief")
    b.add_argument("id")
    b.set_defaults(f=cmd_brief)
    t = sp.add_parser("take")
    t.add_argument("id")
    t.add_argument("--claim")
    t.set_defaults(f=cmd_take)
    tr = sp.add_parser("tried")
    tr.add_argument("id")
    tr.add_argument("--asks")
    tr.set_defaults(f=cmd_tried)
    d = sp.add_parser("done")
    d.add_argument("id")
    d.add_argument("--result", required=True)
    d.set_defaults(f=cmd_done)
    fl = sp.add_parser("flag")
    fl.add_argument("id")
    fl.add_argument("flag", choices=("crucial", "gpt_only"))
    fl.add_argument("--off", action="store_true")
    fl.set_defaults(f=cmd_flag)
    o = sp.add_parser("apply-op")
    o.add_argument("id")
    o.add_argument("op", choices=("bump", "hold", "drop", "approve", "release", "retry"))
    o.add_argument("--note")
    o.set_defaults(f=cmd_apply_op)
    tg = sp.add_parser("tag")
    tg.add_argument("id")
    tg.add_argument("--refresh", action="store_true")
    tg.add_argument("--add", help="kind:ref, kind one of " + "|".join(TS.KINDS))
    tg.add_argument("--line", help="one-line note for --add")
    tg.set_defaults(f=cmd_tag)
    st = sp.add_parser("stale")
    st.add_argument("--refresh", action="store_true", help="recompute pointers of every stale card (after re-reading it)")
    st.set_defaults(f=cmd_stale)
    s = sp.add_parser("sweep")
    s.add_argument("--apply", action="store_true")
    s.set_defaults(f=cmd_sweep)
    a = ap.parse_args(argv)
    rc = a.f(a) or 0
    if a.cmd in MUTATING:
        refresh_layers(REPO)
    return rc


if __name__ == "__main__":
    sys.exit(main())
