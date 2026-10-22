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
import hashlib
import json
import os
import re
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_state as TS
REPO = Path(__file__).resolve().parents[2]
DIR = "MyTradingSys/system/tasks"
BUGS = "MyTradingSys/research/BUGS.md"
LAYER_INDEX = "MyTradingSys/system/layer_index.json"
MUTATING = ("new", "need", "fill", "check", "take", "tried", "done", "apply-op", "sweep", "flag", "tag", "stale")

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
FORMULAS = "MyTradingSys/backtest/layers/FORMULAS.md"
TRIALS = "MyTradingSys/research/layer_lab/TRIALS.md"
RUNS_JSONL = Path(os.environ.get("CODEX_HOME") or "F:/codex_home") / "lab_runs" / "runs.jsonl"   # lab host only; CI runners and other machines have no F:
SIZES = ("S", "M", "L")
WEIGHTS = ("ROUTINE", "IMPORTANT", "CRUCIAL", "CRITICAL", "B-SHARED")   # optional card field; Session_Planner Duty 5
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


def promote_shared(repo):
    """Mark a cited card B-SHARED when another card names it in scope_in."""
    d = tdir(repo)
    if not d.is_dir():
        return
    cards = [json.loads(p.read_text(encoding="utf-8")) for p in d.glob("*.json")]
    by_id = {c.get("id"): c for c in cards}
    cited = set()
    for source in cards:
        for item in source.get("scope_in", []):
            text = str(item)
            for cid in by_id:
                if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(cid)}(?![A-Za-z0-9_-])", text):
                    cited.add(cid)
    for cid in cited:
        target = by_id[cid]
        if target.get("weight") != "B-SHARED":
            target["weight"] = "B-SHARED"
            p = path_of(repo, cid)
            p.write_text(json.dumps(target, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def save(repo, card):
    p = path_of(repo, card["id"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(card, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    promote_shared(repo)
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
            "sources": [], "depends_on": [], "refs": kw.get("refs", []), "formula_id": kw.get("formula_id", ""), "formula_ids": kw.get("formula_ids", []),
            "mutation_check": kw.get("mutation_check", ""), "live_path": False, "approved_by": "",
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


def problems(card, cards=None, reg=None, repo=None):
    """Definition of Ready: [] when a session can run the card with no question to anyone. Every miss is named."""
    p = []
    repo = Path(repo or REPO)
    card_list = cards if cards is not None else load_all(repo)
    cards = {c["id"]: c for c in card_list}
    p.extend(result_trust_problems(card, repo))
    reg = reg or {}
    for k in TEXT[:3]:
        if not str(card.get(k, "")).strip():
            p.append(f"{k} is empty")
    for k in ("scope_in", "steps"):
        if not card.get(k):
            p.append(f"{k} is empty")
    # Formula IDs are canonical section identifiers (for example s15) from FORMULAS.md.
    formula_ids = list(card.get("formula_ids", []))
    if card.get("formula_id"):
        formula_ids.append(card["formula_id"])
    if formula_ids:
        formula_path = repo / FORMULAS
        try:
            formula_text = formula_path.read_text(encoding="utf-8-sig")
            known = set(re.findall(r"(?im)^#{1,6}\s*(?:section\s+)?(\d+(?:\.\d+)*)\b", formula_text))
            known |= {"s" + item for item in known}
            known |= set(re.findall(r"(?im)\b(?:section\s+)?(s\d+(?:\.\d+)*)\b", formula_text))
            for fid in formula_ids:
                if str(fid) not in known:
                    p.append(f"formula id {fid!r} not found in {FORMULAS}")
        except OSError:
            p.append(f"formula source missing: {FORMULAS}")
    holdouts = []
    if card.get("holdout_path"):
        holdouts.append(card["holdout_path"])
    if card.get("holdout"):
        holdouts.append(card["holdout"])
    if isinstance(card.get("holdout_paths"), list):
        holdouts.extend(card["holdout_paths"])
    for hp in holdouts:
        h_path = (repo / hp) if not Path(hp).is_absolute() else Path(hp)
        if not h_path.exists():
            p.append(f"holdout path {hp!r} not found")
    if holdouts and not card.get("split_dates") and not card.get("split_date") and not card.get("split"):
        p.append("split dates is empty")
    elif "split_dates" in card and not card.get("split_dates"):
        p.append("split dates is empty")
    if card.get("lane") == "CODEX" and card.get("kind") == "run":
        try:
            if not RUNS_JSONL.is_file():
                raise FileNotFoundError(RUNS_JSONL)    # off the lab host the count cannot be checked: not a card defect (CI red 2026-10-17)
            ledger = (repo / TRIALS).read_text(encoding="utf-8-sig")
            rows = [json.loads(line) for line in RUNS_JSONL.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
            runs = sum(row.get("card") == card.get("id") for row in rows)
            trials = sum(bool(re.search(rf"(?<![A-Za-z0-9_-]){re.escape(card.get('id', ''))}(?![A-Za-z0-9_-])", line)) for line in ledger.splitlines() if line.lstrip().startswith("|"))
            if trials != runs:
                p.append(f"trial-ledger count {trials} != runs.jsonl count {runs} for {card.get('id')}")
        except FileNotFoundError:
            pass
        except (OSError, ValueError, json.JSONDecodeError) as e:
            p.append(f"run accounting unavailable: {e}")
    if card.get("lane") == "CODEX" and card.get("kind") == "build" and "mutation_check" in card:
        probe = str(card.get("mutation_check", "")).strip()
        match = re.fullmatch(r"([^:]+\.py)::(test_[A-Za-z0-9_]+)", probe)
        if not match:
            p.append("mutation_check must name path/to/test.py::test_* for dummy or shuffled output")
        else:
            test_path = repo / match.group(1)
            try:
                test_source = test_path.read_text(encoding="utf-8-sig")
                if not re.search(rf"(?m)^\s*def\s+{re.escape(match.group(2))}\s*\(", test_source):
                    p.append(f"mutation_check test not found: {probe}")
                elif (not re.search(r"(?i)(dummy|shuffl)", test_source)
                      or not (re.search(r"(?i)raises|fail", test_source) or re.search(r"assert[^\n]*(?:!=|not in|is not)", test_source))):
                    p.append("mutation_check test must assert rejection of dummy or shuffled output")
            except OSError:
                p.append(f"mutation_check test file missing: {match.group(1)}")
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
    receipt = card.get("review_receipt") or card.get("review_stamp")
    if isinstance(receipt, dict):
        reviewer = str(receipt.get("reviewer") or "").strip()
        producer = str(receipt.get("producer") or card.get("producer") or card.get("refined_by") or card.get("worker") or "").strip()
        if reviewer and producer and reviewer.casefold() == producer.casefold():
            p.append(f"producer {producer!r} cannot self-review")
        elif reviewer.casefold() in {"self", "producer"}:
            p.append("producer cannot self-review")
        if stamp_kind(card, repo) != "real":
            p.append("review receipt voided: scope or card changed after review")
    elif card.get("note"):
        note = card["note"]
        for m in REVIEWED_RE.finditer(note):
            reviewer = m.group(1).strip("<>[](){}.,:;").casefold()
            producer = str(card.get("producer") or card.get("refined_by") or "").strip().casefold()
            if producer and reviewer == producer:
                p.append(f"producer {producer!r} cannot self-review")
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
    if card.get("hosts"):
        L.append(f"Host: run only on {' or '.join(card['hosts'])} (data or tools there)")
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


def cmd_need(a):
    """Pre-run item of a card (operator 2026-10-22: "whatever needs to be done regarding a task before it is run, MTS must know").
    `--host` pins the card to machines; `what` + `--lane` makes a raw prerequisite card an agent owns and adds it to depends_on,
    so dispatch holds the card until the prerequisite is done. Enforced at session end by prereq_guard.py (Stop hook)."""
    c = get(REPO, a.id)
    if a.host:
        c["hosts"] = sorted(set(c.get("hosts", [])) | set(a.host))
        print(f"{c['id']}: hosts {', '.join(c['hosts'])}")
    if a.what:
        if not a.lane:
            raise SystemExit("tasks: need with a description needs --lane (who does it); an operator-only item is not a card")
        nid = (c["id"] + "-need-" + re.sub(r"[^a-z0-9]+", "-", a.what.lower()).strip("-"))[:60].rstrip("-")
        if not path_of(REPO, nid).exists():
            n = blank(nid, f"Prereq of {c['id']}: {a.what}"[:120], prio=min(c.get("prio", 3), 3), lane=a.lane, refs=[path_of(REPO, c["id"]).as_posix()])
            n["goal"] = a.what[:MAX_FIELD]
            n["note"] = f"PREREQ of {c['id']}: {c['id']} waits on this card (depends_on)."
            if a.role:
                n["role"] = a.role
            save(REPO, n)
            print(f"wrote {path_of(REPO, nid)} (state raw, lane {a.lane})")
        if nid not in c.get("depends_on", []):
            c["depends_on"] = list(c.get("depends_on", [])) + [nid]
        print(f"{c['id']}: depends_on {', '.join(c['depends_on'])}")
    if not (a.host or a.what):
        raise SystemExit("tasks: need <id> [\"<what>\" --lane L] [--host H]")
    save(REPO, c)
    return 0


def cmd_fill(a):
    c = get(REPO, a.id)
    if a.size:
        c["size"] = a.size
    if a.worker:
        c["worker"] = a.worker
    if a.est_turns is not None:
        c["est_turns"] = a.est_turns
    if a.goal is not None:
        c["goal"] = a.goal
    if a.done_when is not None:
        c["done_when"] = a.done_when
    if a.tests is not None:
        c["tests"] = a.tests
    if a.scope_in is not None:
        c["scope_in"] = a.scope_in
    if a.scope_out is not None:
        c["scope_out"] = a.scope_out
    if a.steps is not None:
        c["steps"] = a.steps
    if a.commands is not None:
        c["commands"] = a.commands
    if a.sources is not None:
        c["sources"] = a.sources
    if a.refs is not None:
        c["refs"] = a.refs
    if a.layers is not None:
        c["layers"] = a.layers
    if a.weight is not None:
        c["weight"] = a.weight
    if a.lane is not None:
        c["lane"] = a.lane
    if a.formula_id is not None:
        c["formula_id"] = a.formula_id
    if a.holdout_path is not None:
        c["holdout_path"] = a.holdout_path
    if a.split_dates is not None:
        c["split_dates"] = a.split_dates
    if a.note is not None:
        c["note"] = a.note
    save(REPO, c)
    return cmd_check(argparse.Namespace(id=c["id"], demote=False))


def cmd_check(a):
    cards = load_all(REPO)
    reg = registry(REPO)
    bad = 0
    for c in cards:
        if (a.id and c["id"] != a.id) or c["state"] not in ("raw", "refined", "ready", "active"):
            continue
        miss = problems(c, cards, reg, repo=REPO)
        if not miss and c["state"] in ("raw", "refined"):
            miss = promotion_problems(c, repo=REPO)
        elif not miss and c["state"] in LIVE and needs_review(c) and stamp_kind(c, repo=REPO) != "real":
            miss = ["review stamp voided or missing: scope or card changed after review"]
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
            bad += 1 if a.id else (c["state"] in LIVE)
            if c["state"] in LIVE and a.demote:
                c["state"] = "refined"
                save(REPO, c)
            print(f"{c['id']}: NOT READY ({c['state']}): " + "; ".join(miss))
        elif c["state"] == "raw" and a.id:
            bad += 1
            print(f"{c['id']}: raw: " + "; ".join(miss))
    return 1 if bad else 0


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


REVIEW_WEIGHTS = ("CRUCIAL", "CRITICAL")   # lab_guy v3.1: these weights (or class C2/C3) need a real review stamp before start and finish
SOFT_WEIGHTS = ("IMPORTANT",)              # IMPORTANT / class C1: a real review stamp is needed to be PROMOTED to ready (`check`), not to be taken
# Two stamp formats are in use: planner `REVIEWED:<date> <ACCEPT|T0-ONLY>` (session_planner.md) and legacy `REVIEWED: <who> <date>`.
STAMP_PLAN_RE = re.compile(r"^REVIEWED:[ \t]*(\d{4}-\d{2}-\d{2})[ \t]+(ACCEPT|T0-ONLY)(?:[ \t]|$)", re.I | re.M)
REVIEWED_RE = re.compile(r"^REVIEWED:[ \t]+(?!\d{4}-\d{2}-\d{2})(\S+)[ \t]+(\d{4}-\d{2}-\d{2})(?:[ \t]|$)", re.I | re.M)
HOLD_RE = re.compile(r"HOLD[ :]+(A-\d{8}-\d+)")
HOLD_CLEARED_RE = re.compile(r"HOLD-CLEARED[ :]+(A-\d{8}-\d+)")


def review_hashes(card, repo=None):
    """Compute content hashes of card, code, spec, data, and scope files."""
    repo = Path(repo or REPO)
    contract_fields = {k: card.get(k) for k in (
        "id", "title", "goal", "scope_in", "scope_out", "steps", "commands",
        "tests", "done_when", "weight", "lane", "size", "kind", "formula_id",
        "formula_ids", "holdout_path", "split_dates"
    ) if k in card}
    card_hash = hashlib.sha256(json.dumps(contract_fields, sort_keys=True).encode("utf-8")).hexdigest()[:12]

    file_hashes = {}
    code_files = {}
    spec_files = {}
    data_files = {}
    for s in card.get("scope_in", []):
        t = str(s).split()[0].rstrip(",;") if str(s).strip() else ""
        t = re.sub(r":\d[\d,\-]*$", "", t).rstrip("/")
        if not t:
            continue
        p = (repo / t) if not Path(t).is_absolute() else Path(t)
        if p.is_file():
            h = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
            file_hashes[t] = h
            ext = p.suffix.lower()
            if ext in (".py", ".java", ".ts", ".js", ".c", ".cpp", ".sh"):
                code_files[t] = h
            elif ext in (".md", ".txt", ".rst") or "spec" in t.lower():
                spec_files[t] = h
            elif ext in (".csv", ".json", ".npz", ".parquet", ".zip", ".dat") or "data" in t.lower():
                data_files[t] = h

    scope_hash = hashlib.sha256(json.dumps(file_hashes, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    code_hash = hashlib.sha256(json.dumps(code_files, sort_keys=True).encode("utf-8")).hexdigest()[:12] if code_files else ""
    spec_hash = hashlib.sha256(json.dumps(spec_files, sort_keys=True).encode("utf-8")).hexdigest()[:12] if spec_files else ""
    data_hash = hashlib.sha256(json.dumps(data_files, sort_keys=True).encode("utf-8")).hexdigest()[:12] if data_files else ""

    try:
        lc = TS.last_change(repo, TS.scope_paths(card, repo)) if hasattr(TS, "last_change") else None
        scope_sha = lc[0] if lc else ""
    except Exception:
        scope_sha = ""

    return {
        "card": card_hash,
        "scope": scope_hash,
        "code": code_hash,
        "spec": spec_hash,
        "data": data_hash,
        "scope_sha": scope_sha,
        "files": file_hashes,
    }


def make_review_receipt(card, reviewer, repo=None, date=None, producer=None):
    """Create a content-bound review receipt dict recording hashes of card, spec, data and code."""
    repo = Path(repo or REPO)
    date_str = date or now()[:10]
    hashes = review_hashes(card, repo)
    receipt = {
        "reviewer": reviewer,
        "date": date_str,
        "card_hash": hashes["card"],
        "scope_hash": hashes["scope"],
        "code_hash": hashes["code"],
        "spec_hash": hashes["spec"],
        "data_hash": hashes["data"],
        "scope_sha": hashes["scope_sha"],
        "files": hashes["files"],
    }
    prod = producer or card.get("producer") or card.get("refined_by")
    if prod:
        receipt["producer"] = prod
    return receipt


def stamp_kind(card, repo=None):
    """'real' (a verified review stamp), 't0' (T0-ONLY: machine checks only, no reviewer ran) or '' (none/void/rejected)."""
    repo = Path(repo or REPO)
    note = str(card.get("note") or "")
    receipt = card.get("review_receipt") or card.get("review_stamp")

    if isinstance(receipt, dict):
        reviewer = str(receipt.get("reviewer") or "").strip()
        producer = str(receipt.get("producer") or card.get("producer") or card.get("refined_by") or "").strip()
        producer_ids = {str(card.get(k) or "").strip().casefold() for k in ("producer", "producer_model", "vendor", "model", "worker", "refined_by", "author") if card.get(k)}
        if producer:
            producer_ids.add(producer.casefold())
        if not reviewer or reviewer.casefold() in {"", "x", "self", "producer", "reviewer", "pending", "unknown"} or reviewer.casefold() in producer_ids:
            return ""
        cur = review_hashes(card, repo)
        if receipt.get("card_hash") and receipt["card_hash"] != cur["card"]:
            return ""
        if receipt.get("scope_hash") and receipt["scope_hash"] != cur["scope"]:
            return ""
        if receipt.get("code_hash") and cur.get("code") and receipt["code_hash"] != cur["code"]:
            return ""
        if receipt.get("spec_hash") and cur.get("spec") and receipt["spec_hash"] != cur["spec"]:
            return ""
        if receipt.get("data_hash") and cur.get("data") and receipt["data_hash"] != cur["data"]:
            return ""
        if receipt.get("scope_sha") and cur.get("scope_sha") and receipt["scope_sha"] != cur["scope_sha"]:
            return ""
        if receipt.get("files"):
            for fpath, fhash in receipt["files"].items():
                if cur.get("files", {}).get(fpath) != fhash:
                    return ""
        return "real"

    for m in STAMP_PLAN_RE.finditer(note):
        try:
            datetime.strptime(m.group(1), "%Y-%m-%d")
        except ValueError:
            continue
        if m.group(2).upper() == "T0-ONLY":
            return "t0"
        m_rev = re.search(r"\b(?:reviewer|by)\s*[:=]\s*(\S+)\b", note, re.I)
        if m_rev:
            rev = m_rev.group(1).strip("<>[](){}.,:;").casefold()
            producer_ids = {str(card.get(k) or "").strip().casefold() for k in ("producer", "producer_model", "vendor", "model", "worker", "refined_by", "author") if card.get(k)}
            if rev in producer_ids or rev in {"self", "producer"}:
                return ""
        cur = review_hashes(card, repo)
        m_scope = re.search(r"\b(?:scope|scope_hash)=([a-f0-9]+)\b", note, re.I)
        if m_scope and m_scope.group(1).lower() != cur["scope"].lower():
            return ""
        m_card = re.search(r"\b(?:card|card_hash)=([a-f0-9]+)\b", note, re.I)
        if m_card and m_card.group(1).lower() != cur["card"].lower():
            return ""
        m_code = re.search(r"\b(?:code|code_hash)=([a-f0-9]+)\b", note, re.I)
        if m_code and m_code.group(1).lower() != cur.get("code", "").lower():
            return ""
        m_spec = re.search(r"\b(?:spec|spec_hash)=([a-f0-9]+)\b", note, re.I)
        if m_spec and m_spec.group(1).lower() != cur.get("spec", "").lower():
            return ""
        m_data = re.search(r"\b(?:data|data_hash)=([a-f0-9]+)\b", note, re.I)
        if m_data and m_data.group(1).lower() != cur.get("data", "").lower():
            return ""
        return "real"

    for m in REVIEWED_RE.finditer(note):
        reviewer = m.group(1).strip("<>[](){}.,:;").casefold()
        try:
            datetime.strptime(m.group(2), "%Y-%m-%d")
        except ValueError:
            continue
        producer_ids = {str(card.get(k) or "").strip().casefold() for k in ("producer", "producer_model", "vendor", "model", "worker", "refined_by", "author") if card.get(k)}
        m_prod = re.search(r"\b(?:producer)\s*[:=]\s*(\S+)\b", note, re.I)
        if m_prod:
            producer_ids.add(m_prod.group(1).strip("<>[](){}.,:;").casefold())
        if reviewer in {"", "x", "self", "producer", "reviewer", "pending", "unknown"} or reviewer in producer_ids:
            return ""
        cur = review_hashes(card, repo)
        m_scope = re.search(r"\b(?:scope|scope_hash)=([a-f0-9]+)\b", note, re.I)
        if m_scope and m_scope.group(1).lower() != cur["scope"].lower():
            return ""
        m_card = re.search(r"\b(?:card|card_hash)=([a-f0-9]+)\b", note, re.I)
        if m_card and m_card.group(1).lower() != cur["card"].lower():
            return ""
        m_code = re.search(r"\b(?:code|code_hash)=([a-f0-9]+)\b", note, re.I)
        if m_code and m_code.group(1).lower() != cur.get("code", "").lower():
            return ""
        m_spec = re.search(r"\b(?:spec|spec_hash)=([a-f0-9]+)\b", note, re.I)
        if m_spec and m_spec.group(1).lower() != cur.get("spec", "").lower():
            return ""
        m_data = re.search(r"\b(?:data|data_hash)=([a-f0-9]+)\b", note, re.I)
        if m_data and m_data.group(1).lower() != cur.get("data", "").lower():
            return ""
        return "real"
    return ""


def card_class(card):
    """C0-C3: the card's own `class` field, else `class=Cn` / `CLASS:Cn` in the note stamp; a live-path card is C3 at least."""
    values = []
    raw = card.get("class", "")
    field = raw.strip().upper() if isinstance(raw, str) else ""
    if raw is not None and not isinstance(raw, str):
        values.append("C3")
    elif field:
        values.append(field if re.fullmatch(r"C[0-3]", field) else "C3")
    note = card.get("note", "")
    if note is not None and not isinstance(note, str):
        values.append("C3")
        note = ""
    for m in re.finditer(r"\bclass(?:[ \t]*[=:]|[ \t]+(?=[Cc](?:\d|x\b|[ \t-])|\d))", note or "", re.I):
        value = re.match(r"[ \t]*(C[0-3])\b", (note or "")[m.end():], re.I) if re.search(r"[=:]", m.group()) else None
        values.append(value.group(1).upper() if value else "C3")
    c = max(values, key=lambda x: int(x[1:])) if values else ""
    if card.get("live_path", False) is not False:
        c = "C3"
    return c


def active_holds(repo=None):
    """Announcement ids that are HOLD or STOP entries and not marked lifted/retired/closed."""
    try:
        text = ((repo or REPO) / "MyTradingSys" / "system" / "ANNOUNCEMENTS.md").read_text(encoding="utf-8")
    except OSError:
        return set()
    return {m.group(1) for m in re.finditer(r"^### (A-\d{8}-\d+) (?:HOLD|STOP)(?!.*(?:LIFTED|RETIRED|CLOSED))", text, re.M)}


def hold_problems(card, holds=None):
    """Active announcement holds named in the note (`HOLD A-...`) and not cleared there (`HOLD-CLEARED A-...`)."""
    note = str(card.get("note") or "")
    held = {h for h in HOLD_RE.findall(note)} - set(HOLD_CLEARED_RE.findall(note))
    held &= active_holds() if holds is None else set(holds)
    return [f"held by {h}: stays refined until the announcement is lifted ('HOLD-CLEARED {h}' in the note)" for h in sorted(held)]


def needs_review(card):
    """'hard' (crucial/critical or C2/C3: needed to take and finish), 'soft' (important or C1: needed to promote), or ''."""
    raw = card.get("weight", "")
    if raw is not None and not isinstance(raw, str):
        return "hard"
    w = (raw or "").strip().upper()
    if w and w not in WEIGHTS:
        return "hard"
    if w in REVIEW_WEIGHTS or card_class(card) in ("C2", "C3"):
        return "hard"
    if w in SOFT_WEIGHTS or card_class(card) == "C1":
        return "soft"
    return ""


def promotion_problems(card, holds=None, repo=None):
    """Why `check` must not promote a raw/refined card to ready: an active hold, or no real review for important/crucial/critical or C1+."""
    p = hold_problems(card, holds)
    if needs_review(card) and stamp_kind(card, repo=repo) != "real":
        p.append("needs a real review stamp (ACCEPT or 'REVIEWED: <reviewer> <date>'), not " + ("T0-ONLY" if stamp_kind(card, repo=repo) == "t0" else "none") + ": Lab_Guy pass (roles/lab_guy.md)")
    return p


def review_gate(card, finishing=False, result="", repo=None):
    """Problems stopping a crucial/critical (or C2/C3, or live-path) card from being taken or marked done. routine/important pass.
    The weight itself is set by the reviewer/planner (the note stamp), never by the producer."""
    p = result_trust_problems(card, repo)
    for key in ("note", "class", "weight"):
        if card.get(key) is not None and not isinstance(card.get(key), str):
            p.append(f"{key} must be a string")
    if "live_path" in card and type(card["live_path"]) is not bool:
        p.append("live_path must be a boolean")
    weight = card.get("weight")
    if isinstance(weight, str) and weight.strip() and weight.strip().upper() not in WEIGHTS:
        p.append("weight is not a recognized review weight")
    if needs_review(card) != "hard":
        return p
    if stamp_kind(card, repo=repo) != "real":
        p.append("weight/class needs a real review: add 'REVIEWED: <reviewer> <date>' or 'REVIEWED:<date> ACCEPT' to the note first (T0-ONLY is not a review)")
    if finishing and not str(result or "").strip():
        p.append("a result receipt is required (--result with the evidence)")
    return p


TRUST_LEVELS = {"UNCHECKED": -1, "DISPUTED": -1, "MACHINE-OK": 0, "VERIFIED-C1": 1, "VERIFIED-C2": 2}


def result_bases(card, repo=None):
    """Explicit card citations in scope_in: card:ID, task JSON path, or an existing bare ID."""
    repo = Path(repo or REPO)
    found = {}
    for item in card.get("scope_in", []):
        token = str(item).split()[0].rstrip(",;") if str(item).strip() else ""
        token = token.replace(chr(92), "/")
        explicit = token.startswith("card:")
        if explicit:
            cid = token[5:]
        elif token.startswith("MyTradingSys/system/tasks/") and token.endswith(".json"):
            cid = Path(token).stem
            explicit = True
        elif re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", token):
            cid = token
        else:
            continue
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", cid):
            raise ValueError(f"invalid cited card {token!r}")
        path = path_of(repo, cid)
        if explicit or path.is_file():
            if not path.is_file():
                raise ValueError(f"missing cited card {cid}")
            if cid == card.get("id"):
                raise ValueError("a result cannot cite itself as a trusted base")
            found[cid] = get(repo, cid)
    return found


def result_fingerprint(card, repo=None):
    repo = Path(repo or REPO)
    bases = result_bases(card, repo)
    scope = []
    for item in card.get("scope_in", []):
        token = str(item).split()[0].rstrip(",;") if str(item).strip() else ""
        token = re.sub(r":\d[\d,\-]*$", "", token)
        cid = token[5:] if token.startswith("card:") else Path(token).stem if token.startswith("MyTradingSys/system/tasks/") else token
        if cid in bases:
            continue  # bind result semantics below, not mutable sharing metadata
        path = repo / token
        if path.is_dir():
            raise ValueError(f"trust requires explicit file pins, not directory scope: {token}")
        if not path.is_file():
            raise ValueError(f"trust source file is missing: {token}")
        scope.append(token)
    hashes = review_hashes(dict(card, scope_in=scope, weight=""), repo)
    data = {"scope_data": hashes["data"], "cited_results": {
        cid: {k: base.get(k) for k in ("state", "result", "scope_in", "goal", "result_receipt", "flow_receipt")}
        for cid, base in bases.items()}}
    for item in card.get("flow", {}).get("data_scope", []):
        path = repo / item
        if not path.is_file():
            raise ValueError(f"trust data pin is not an explicit file: {item}")
        data[item] = hashlib.sha256(path.read_bytes()).hexdigest()
    # Scope content binds code/spec/data even in scratch repos with no git history.
    # Unrelated HEAD/claim changes do not expire a result.
    contract = {"scope": hashes["scope"], "card": hashes["card"], "result": card.get("result"), "flow": card.get("flow")}
    revision = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(), hashes["scope_sha"] + ":" + revision


def trust_evidence(repo, evidence):
    root = Path(repo or REPO).resolve()
    path = (root / evidence).resolve()
    path.relative_to(root)  # no evidence escaping the checkout
    if not path.is_file():
        raise ValueError("trust evidence file is missing")
    return path


def make_result_trust(card, tag, checker_model, effort, evidence, repo=None, date=None):
    """Bind an explicitly supplied assessment; never infer verification from card completion.

    This is evidence bookkeeping, not reviewer authentication (stamp-writer R1).
    """
    if tag not in TRUST_LEVELS:
        raise ValueError("unknown trust tag")
    data, revision = result_fingerprint(card, repo)
    proof = trust_evidence(repo, evidence)
    return {"tag": tag, "checker_model": checker_model, "effort": effort,
            "date": date or now()[:10], "data_hash": data, "code_revision": revision,
            "evidence": proof.relative_to(Path(repo or REPO).resolve()).as_posix(),
            "evidence_sha256": hashlib.sha256(proof.read_bytes()).hexdigest()}


def result_trust_problems(card, repo=None, _seen=None):
    repo = Path(repo or REPO)
    try:
        seen = set(_seen or ())
        if card.get("id") in seen:
            raise ValueError("cycle in cited result dependencies")
        seen.add(card.get("id"))
        bases = result_bases(card, repo)
        weight = str(card.get("weight") or "").strip().upper()
        required = max(int((card_class(card) or "C0")[1]),
                       2 if weight in REVIEW_WEIGHTS else 1 if weight in SOFT_WEIGHTS or weight == "B-SHARED" else 0)
        flow_class = card.get("flow", {}).get("risk_class", "C0")
        required = max(required, int(flow_class[1]) if isinstance(flow_class, str) and re.fullmatch(r"C[0-3]", flow_class) else 3)
        errors = []
        for cid, base in bases.items():
            try:
                receipt = base.get("flow_receipt") if base.get("flow") else base.get("result_receipt")
                trust = (receipt or {}).get("trust", {})
                tag = trust.get("tag", "UNCHECKED")
                if base.get("state") != "done" or TRUST_LEVELS.get(tag, -1) < required:
                    raise ValueError(f"{tag}: requires trust at class C{required} or above")
                for key in ("checker_model", "effort", "date", "data_hash", "code_revision", "evidence", "evidence_sha256"):
                    if not isinstance(trust.get(key), str) or not trust[key].strip():
                        raise ValueError(f"missing trust {key}")
                day = datetime.strptime(trust["date"], "%Y-%m-%d")
                if day.strftime("%Y-%m-%d") > now()[:10]:
                    raise ValueError("trust date is in the future")
                data, revision = result_fingerprint(base, repo)
                if trust["data_hash"] != data or trust["code_revision"] != revision:
                    raise ValueError("trust expired: data or code/scope revision changed")
                proof = trust_evidence(repo, trust["evidence"])
                if hashlib.sha256(proof.read_bytes()).hexdigest() != trust["evidence_sha256"]:
                    raise ValueError("trust expired: evidence changed")
                upstream = result_trust_problems(base, repo, seen)
                if upstream:
                    raise ValueError("upstream result trust invalid: " + "; ".join(upstream))
            except Exception as e:
                errors.append(f"cited result {cid}: {e}")
        return errors
    except Exception as e:
        return [f"result trust gate error: {e}"]


def mark_shared_bases(card, repo=None):
    """Only mutating lifecycle commands call this; queue queries remain read-only."""
    repo = Path(repo or REPO)
    try:
        bases = result_bases(card, repo)
    except (ValueError, OSError):
        return  # the read-only trust gate reports invalid/missing citations
    for cid, base in bases.items():
        base["weight"] = "B-SHARED"
        base["class"] = "C3" if card_class(base) == "C3" else "C2"
        base["shared_consumers"] = sorted(set(base.get("shared_consumers", [])) | {card["id"]})
        save(repo, base)


def cmd_take(a):
    c = get(REPO, a.id)
    if c["state"] != "ready":
        raise SystemExit(f"tasks: {a.id} is {c['state']}, only a ready card can be taken")
    mark_shared_bases(c, REPO)
    gate = review_gate(c, repo=REPO)
    if gate:
        raise SystemExit(f"tasks: {a.id} cannot be taken: " + "; ".join(gate))
    miss = problems(c, load_all(REPO), registry(REPO), repo=REPO)
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
    if c.get("state") not in ("ready", "active"):
        raise SystemExit(f"tasks: {a.id} is {c.get('state')}, only a ready or active card can be marked done")
    mark_shared_bases(c, REPO)
    gate = review_gate(c, finishing=True, result=a.result, repo=REPO)
    if c["state"] == "ready":   # runners claim via sync.py and never call `take`: ready->done needs every gate `take` would apply
        gate += promotion_problems(c, repo=REPO) + problems(c, load_all(REPO), registry(REPO), repo=REPO)
    if gate:
        raise SystemExit(f"tasks: {a.id} cannot be marked done: " + "; ".join(gate))
    c.update(state="done", result=a.result, closed=now())
    c.setdefault("result_receipt", {}).setdefault("trust", {"tag": "UNCHECKED"})
    c.setdefault("taken", c["closed"])
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
                gate = review_gate(c, finishing=True, result=c.get("result") or "registry rows closed")
                if gate:
                    print(f"{c['id']}: cannot be marked done: " + "; ".join(gate))
                    continue
                c.update(state="done", result=c.get("result") or "registry rows closed", closed=now())
                save(REPO, c)
    if not hit:
        print("sweep: nothing to retire")


# ---- dispatch snapshot (RU1) ---------------------------------------------------------------------------------------

WEIGHT_ORDER = {w: i for i, w in enumerate(WEIGHTS)}        # ROUTINE < IMPORTANT < CRUCIAL < CRITICAL < B-SHARED (higher runs first)
CLASS_WEIGHT = {"C1": "IMPORTANT", "C2": "CRUCIAL", "C3": "CRITICAL"}
REVIEWER_SLOT = {"ROUTINE": "none (coordinator spot-check)", "IMPORTANT": "coordinator reads Result",
                 "CRUCIAL": "review Agent", "CRITICAL": "REVIEW session", "B-SHARED": "REVIEW session"}   # session_planner.md Duty 5
DISPATCH_TABLE_MAX = 15                                      # session_planner.md Duty 2: max 15 lines


def effective_weight(card):
    """The card's weight raised (never lowered) to what its class / live_path demands (session_planner.md Duty 5)."""
    w = str(card.get("weight") or "ROUTINE").upper()
    floor = "CRITICAL" if card.get("live_path") else CLASS_WEIGHT.get(card_class(card), "ROUTINE")
    return max(w, floor, key=lambda x: WEIGHT_ORDER.get(x, 0))


def exclusion(card, cards, reg, holds, claims, lane_st, as_of, host=None, repo=REPO):
    """(code, why) when the card must not be dispatched now, else None. Order: state, hold, claim, dependency, lane, readiness."""
    import sync
    import lane_health
    if card["state"] != "ready":
        return ("state", f"not ready: state is {card['state']}")
    held = hold_problems(card, holds)
    if held:
        return ("hold", held[0].split(":")[0])
    own = claim_of(card, claims)
    if own:
        return ("claimed", f"claimed by {own.get('host', '?')}/{own.get('account', '?')}")
    mine = [x.rstrip("/") for x in card.get("scope_in", [])]
    for slug in sorted(claims):
        hit = sync.area_overlap(mine, sync.claim_areas(claims[slug])) if mine else None
        if hit:
            return ("claimed", f"area {hit[0]} overlaps claim {slug}")
    miss = problems(card, cards, reg)
    dep = [m for m in miss if m.startswith("depends_on ")]
    if dep:
        return ("dependency", dep[0])
    if card["lane"] == "CODEX" and lane_st["status"] == "down" and lane_health.allow(lane_st, as_of) == "":
        return ("lane_down", lane_health.why_down(lane_st))
    if host and card["lane"] == "JIS-NB" and host != "JIS-NB":
        return ("host", f"lane JIS-NB needs host JIS-NB, not {host}")
    if host and card.get("hosts") and host not in card["hosts"]:
        return ("host", f"needs host {' or '.join(card['hosts'])}, not {host}")
    if miss:
        return ("not_ready", "not ready: " + miss[0])
    if needs_review(card) == "hard" and stamp_kind(card) != "real":
        return ("no_stamp", "needs a real review stamp (Lab_Guy pass)")
    return None


def card_role(card):
    """Determine the role for a card: explicit card['role'], or inferred by lane/kind/title."""
    if card.get("role"):
        return str(card["role"])
    lane = str(card.get("lane") or "")
    kind = str(card.get("kind") or "")
    title = str(card.get("title") or "")
    cid = str(card.get("id") or "")

    # Network / nowin cards
    if "nowin" in cid.lower() or "Network:" in title or "network" in cid.lower():
        return "Builder"   # a fix needs a fail-first test (Sonnet); Admin_Guy (Haiku) only triages and makes the card
    # CODEX cards -> Lab_Guy
    if lane == "CODEX":
        return "Lab_Guy"
    # Audits -> MTS_Doctor
    if kind == "audit" or "audit" in cid.lower():
        return "MTS_Doctor"
    # Build / tool / default cards -> Builder
    return "Builder"


def shard_of(card_id, logins):
    """Which login's supervisor owns this card when several coordinate at once (SUPER_LOOP.md): a stable hash of the id over the
    sorted login letters. Pure and identical on every machine, so three supervisors split the ready list without talking."""
    ls = sorted(set(logins))
    return ls[zlib.crc32(card_id.encode("utf-8")) % len(ls)] if ls else ""


def dispatch(cards, reg, holds, claims, lane_st, as_of, host=None, repo=REPO, login=None, logins=None):
    """Pure ranked snapshot: {as_of, host, dispatch: [...], excluded: [...]}. Same inputs -> same dict (as_of is an input).
    With `login` and at least two `logins` (the supervisors alive), each row gets `shard` and `own`; after pinned (CI) cards the
    caller's own shard is ranked first, so parallel supervisors start different cards instead of racing for the same claim."""
    inc, exc = [], []
    sharded = bool(login) and len(set(logins or ())) >= 2
    if sharded:
        logins = sorted(set(logins) | {login})
    for c in cards:
        if c["state"] in FINAL:
            continue
        ex = exclusion(c, cards, reg, holds, claims, lane_st, as_of, host, repo)
        if ex:
            exc.append({"id": c["id"], "state": c["state"], "reason_code": ex[0], "why": ex[1]})
            continue
        w = effective_weight(c)
        role = card_role(c)
        inc.append({"id": c["id"], "title": c["title"], "lane": c["lane"], "role": role, "weight": w, "prio": c.get("prio", 3),
                    "pinned": bool(c.get("pinned")), "est_turns": c.get("est_turns"), "worker": c.get("worker") or "",
                    "reviewer": REVIEWER_SLOT[w], "scope_in": list(c.get("scope_in", [])), "depends_on": list(c.get("depends_on", [])),
                    "created": c.get("created", "")})
        if sharded:
            inc[-1]["shard"] = shard_of(c["id"], logins)
            inc[-1]["own"] = inc[-1]["shard"] == login
    # CI red first (pinned), then (sharded) own shard, then priority, then heavier weight first, then oldest, then id (total order = deterministic)
    inc.sort(key=lambda r: (not r["pinned"], not r.get("own", True), r["prio"], -WEIGHT_ORDER.get(r["weight"], 0), r["created"], r["id"]))
    for n, r in enumerate(inc, 1):
        r["rank"] = n
        del r["created"]
    exc.sort(key=lambda r: (r["reason_code"], r["id"]))
    return {"as_of": as_of.strftime("%Y-%m-%dT%H:%M:%SZ"), "host": host or "", "dispatch": inc, "excluded": exc}


def dispatch_table(snap):
    """The <=15-line table session_planner.md Duty 2 asks for, plus one summary line of exclusions."""
    lines = [f"DISPATCH as_of {snap['as_of']}: {len(snap['dispatch'])} card(s), {len(snap['excluded'])} excluded"]
    for r in snap["dispatch"][:DISPATCH_TABLE_MAX - 3]:
        est = f"{r['est_turns']}t" if r["est_turns"] else "-"
        lines.append(f"{r['rank']}. {r['id']} [{r['lane']}] {r['weight']} p{r['prio']} {r['worker'] or '-'} {est} review={r['reviewer']}")
    left = len(snap["dispatch"]) - (DISPATCH_TABLE_MAX - 3)
    if left > 0:
        lines.append(f"... +{left} more (--json)")
    by = {}
    for e in snap["excluded"]:
        by[e["reason_code"]] = by.get(e["reason_code"], 0) + 1
    lines.append("excluded: " + (", ".join(f"{k} {by[k]}" for k in sorted(by)) or "none"))
    return lines


def cmd_dispatch(a):
    import lane_health
    as_of = datetime.strptime(a.as_of, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) if a.as_of else datetime.now(timezone.utc).replace(microsecond=0)
    cards = load_all(REPO)
    snap = dispatch(cards, registry(REPO), active_holds(REPO), open_claims(REPO), lane_health.load(REPO), as_of, a.host, REPO,
                    login=a.login or os.environ.get("MTS_LOGIN"), logins=a.logins.split(",") if a.logins else None)
    if a.json:
        print(json.dumps(snap, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(chr(10).join(dispatch_table(snap)))
    return 0


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
    ne = sp.add_parser("need", help="record a pre-run item: a prerequisite card an agent owns (depends_on) and/or a host pin")
    ne.add_argument("id")
    ne.add_argument("what", nargs="?")
    ne.add_argument("--lane", choices=LANES)
    ne.add_argument("--role", help="role that owns the prerequisite, e.g. Lab_Guy")
    ne.add_argument("--host", action="append", help="machine the card must run on; repeat for several")
    ne.set_defaults(f=cmd_need)
    fi = sp.add_parser("fill", help="set raw-card fields from flags and run check (promotes without hand JSON edits)")
    fi.add_argument("id")
    fi.add_argument("--size", choices=("S", "M"))
    fi.add_argument("--worker", choices=WORKERS)
    fi.add_argument("--est-turns", type=int)
    fi.add_argument("--goal")
    fi.add_argument("--done-when")
    fi.add_argument("--tests")
    fi.add_argument("--scope-in", action="append", dest="scope_in")
    fi.add_argument("--scope-out", action="append", dest="scope_out")
    fi.add_argument("--step", "--steps", action="append", dest="steps")
    fi.add_argument("--command", "--commands", action="append", dest="commands")
    fi.add_argument("--source", "--sources", action="append", dest="sources")
    fi.add_argument("--ref", "--refs", action="append", dest="refs")
    fi.add_argument("--layer", "--layers", action="append", dest="layers")
    fi.add_argument("--weight", choices=WEIGHTS)
    fi.add_argument("--lane", choices=LANES)
    fi.add_argument("--formula-id")
    fi.add_argument("--holdout-path")
    fi.add_argument("--split-date", "--split-dates", action="append", dest="split_dates")
    fi.add_argument("--note")
    fi.set_defaults(f=cmd_fill)
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
    dp = sp.add_parser("dispatch", help="ranked snapshot of dispatchable cards with why-excluded (session_planner.md Duty 2)")
    dp.add_argument("--json", action="store_true")
    dp.add_argument("--host", help="JIS-NB cards are excluded unless this is JIS-NB")
    dp.add_argument("--login", help="this supervisor's login letter (default env MTS_LOGIN); with --logins ranks its own shard first")
    dp.add_argument("--logins", help="comma list of the logins whose supervisors are alive, e.g. A,B,C")
    dp.add_argument("--as-of", help="UTC YYYY-MM-DDTHH:MM:SSZ (default now); the only wall-clock value in the output")
    dp.set_defaults(f=cmd_dispatch)
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
