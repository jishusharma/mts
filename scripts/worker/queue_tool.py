import sys; sys.dont_write_bytecode = True
"""NUC worker queue tool, coordinator side (runs on the desktop).

The coordinator packs every task into a self-contained package: the task
text plus the real content of every file in its scope. The NUC worker needs
no access to the repository. Replies are checked mechanically before anyone
reads them in full.

Subcommands:
  pack SPEC [SPEC ...]  Build task packages from spec files into incoming/.
                        --lane dsa writes them to incoming_dsa/ (browser worker lane).
  status                One-screen summary of the queue and the worker heartbeat.
  verify [ID ...]       Mechanical checks on finished replies. No ID: every
                        reply that has no verdict yet. An explicit ID always
                        re-runs the checks and overwrites that id's verdict.
  lint SPEC [SPEC ...]  Check only that SCOPE/CREATE lines are bare paths.
  deploy                Copy the worker scripts into deploy/. The NUC launcher
                        installs a changed worker by itself within a minute.

Spec file format (header lines, one blank line, then the task body):
  TASK: one line, plain language
  SCOPE: path, path/dir/, path/file.md:120-260
  OUTPUT: what the reply must contain
  MODEL: optional, default qwen3-coder:30b
  OUTPUT_TOKENS: optional, default 4096
  THINK: optional true/false; sent to Ollama as "think" (use false for thinking models)
  EXPECT: optional, repeatable. Exact text the reply must contain.
          Never shown to the model. Used as the acceptance check.
  CREATE: optional, repeatable, bare path. A file the task is allowed to
          create that does not exist yet; verify will not flag it as an
          unknown file name or an out-of-scope proposal.
  OVERRIDE-CRITICAL: approved-by-operator   (only when SCOPE names a critical file)

Every file this tool writes is UTF-8 without BOM, LF line endings, written
to a temporary name first and then renamed, so a reader never sees half a file.
"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QUEUE = REPO / "Dumps" / "workers" / "NUC-QUEUE"
QUEUE_DIRS = ("incoming", "claimed", "done", "deploy", "specs", "incoming_dsa", "claimed_dsa")
DEPLOY_FILES = ("nuc-worker.ps1", "nuc-launcher.ps1", "setup-nuc.ps1")

DEFAULT_MODEL = "qwen3-coder:30b"
CTX_MIN = 4096
# Upper bound on the context window per task. Sized for the NUC's 32 GB:
# about 3 GB of attention cache for this model at this size, next to the
# roughly 19 GB model. Bigger tasks must be split, never truncated.
CTX_MAX = 32768
DEFAULT_OUTPUT_TOKENS = 4096
PROMPT_MARGIN_TOKENS = 512
# Deliberately pessimistic characters-per-token ratio, so the context window
# is always larger than the prompt. An undersized window silently drops the
# start of the prompt, which is how the old worker lost its file contents.
CHARS_PER_TOKEN = 3.0
MAX_FILE_BYTES = 120_000  # larger files must be scoped by line range

CRITICAL = {
    "mytradingsys/runtime/compiled_engine.md",
    "dsa_session_prompt.md",
    "mytradingsys/system/01_ai_behavior.md",
    "mytradingsys/runtime/mts_math.py",
    "mytradingsys/runtime/math_object_builder.py",
    "scripts/core/start-trading-day.ps1",
    "scripts/core/mode.ps1",
    "scripts/core/stop-day.ps1",
    "mytradingsys/project_vision.md",
}
BANNED_TERMS = ("git ", "commit", "push", "live trading", "mode.ps1", "stop-day.ps1")

WORKER_RULES = """You are a WORKER for the MTS project. You only produce text. You cannot run commands and you cannot open files.

Rules:
1. The SOURCE blocks below are the complete, current content of every file in this task's scope, read from disk when the task was packed. They are your only source of truth about the repository.
2. Never invent file names, file contents, values or results. If something you need is not in the SOURCE blocks, write NOT IN SCOPE: followed by what is missing, and continue with the rest.
3. Quote verbatim when asked to quote. Write file names exactly as they appear in the SOURCE headers.
4. To propose a change to a file, output the complete new content of that file, and nothing else, between these two marker lines:
<<<FILE relative/path/from/repository/root
>>>END FILE
5. Begin your reply with exactly these five lines, then give the details:
TASK: one line
STATUS: DONE or PARTIAL or BLOCKED
SUMMARY: one line
FINDINGS: one line
NEXT: one line"""

HEADER_RE = re.compile(r"^([A-Z][A-Z_-]*):[ \t]*(.*)$")
SCOPE_RANGE_RE = re.compile(r"^(.*?):(\d+)-(\d+)$")
ID_RE = re.compile(r"^\d{3,}-[A-Za-z0-9][A-Za-z0-9-]*$")
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
PATH_REF_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\\-]*\.(?:md|py|ps1|java|json|txt|xml|csv|yml|yaml)\b")
FILE_BLOCK_RE = re.compile(r"^<<<FILE[ \t]+(.+?)[ \t]*\r?\n(.*?)^>{3,}\s*END\s+FILE\s*$", re.M | re.S)
# Every <<<FILE ...>>> header line, whether or not its block closed properly.
FILE_HEADER_RE = re.compile(r"^<<<FILE[ \t]+(.+?)[ \t]*\r?$", re.M)


# ---------- small helpers ----------

def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def utc_stamp(t=None):
    return (t or utc_now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except (TypeError, ValueError):
        return None


def age_text(t):
    if t is None:
        return "unknown age"
    secs = int((utc_now() - t).total_seconds())
    if secs < 120:
        return f"{secs} s ago"
    if secs < 7200:
        return f"{secs // 60} min ago"
    return f"{secs // 3600} h ago"


def sha12(data):
    return hashlib.sha256(data).hexdigest()[:12]


def write_atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def read_text(path):
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return data.decode("utf-8")


def rel_of(path):
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def norm_rel(text):
    text = text.strip().strip("`\"'").replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def ensure_dirs():
    for d in QUEUE_DIRS:
        (QUEUE / d).mkdir(parents=True, exist_ok=True)


def squash(text):
    return " ".join(text.split())


# ---------- pack ----------

class Refused(Exception):
    pass


def check_bare_path_line(key, val):
    """SCOPE/CREATE entries must be bare comma-separated paths, never prose."""
    for entry in val.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if " " in entry or "(" in entry or ")" in entry:
            raise Refused(
                f"{key} entry is not a bare path (looks like prose): '{entry}'. "
                f"Move the explanation into the task body and keep {key} to bare paths only."
            )


def parse_spec(path):
    lines = read_text(path).splitlines()
    head, expect, create, scope, i = {}, [], [], [], 0
    while i < len(lines) and lines[i].strip():
        m = HEADER_RE.match(lines[i])
        if not m:
            break
        key, val = m.group(1), m.group(2).strip()
        if key == "EXPECT":
            if val:
                expect.append(val)
        elif key == "CREATE":
            if val:
                check_bare_path_line("CREATE", val)
                create.append(val)
        elif key == "SCOPE":
            if val:
                check_bare_path_line("SCOPE", val)
                scope.append(val)
        else:
            head[key] = val
        i += 1
    body = "\n".join(lines[i:]).strip()
    if scope:
        head["SCOPE"] = ",".join(scope)
    return head, expect, create, body


def is_text_file(path):
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if b"\x00" in data[:8192]:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def resolve_scope(scope_line):
    """Return a list of (path, first_line, last_line) with line numbers 1-based, or None for whole file."""
    entries = [e.strip() for e in scope_line.split(",") if e.strip()]
    if not entries:
        raise Refused("SCOPE is empty")
    picked, seen = [], set()
    for entry in entries:
        first = last = None
        m = SCOPE_RANGE_RE.match(entry)
        if m:
            entry, first, last = m.group(1), int(m.group(2)), int(m.group(3))
            if first < 1 or last < first:
                raise Refused(f"bad line range in SCOPE entry {entry}:{first}-{last}")
        rel = norm_rel(entry)
        if not rel or re.match(r"^[A-Za-z]:", rel):
            raise Refused(f"SCOPE entry must be a path relative to the repository root: {entry}")
        target = (REPO / rel).resolve()
        try:
            target.relative_to(REPO.resolve())
        except ValueError:
            raise Refused(f"SCOPE entry points outside the repository: {entry}")
        if not target.exists():
            raise Refused(f"SCOPE entry not found on disk: {entry}")
        if target.is_dir():
            if first is not None:
                raise Refused(f"line range given for a folder: {entry}")
            files = sorted(
                p for p in target.rglob("*")
                if p.is_file()
                and not any(part.startswith(".") or part == "__pycache__" for part in p.relative_to(target).parts)
                and not p.name.endswith((".new", ".bak", ".tmp", ".old"))
                and is_text_file(p)
            )
            for p in files:
                key = (rel_of(p), None, None)
                if key not in seen:
                    seen.add(key)
                    picked.append((p, None, None))
        else:
            if not is_text_file(target):
                raise Refused(f"not a UTF-8 text file: {entry}")
            key = (rel_of(target), first, last)
            if key not in seen:
                seen.add(key)
                picked.append((target, first, last))
    if not picked:
        raise Refused("SCOPE resolved to no text files")
    return picked


def slice_of(path, first, last):
    text = read_text(path)
    lines = text.splitlines(keepends=True)
    total = len(lines)
    if first is None:
        return text, 1, total, total
    if first > total:
        raise Refused(f"{rel_of(path)} has {total} lines; range starts at {first}")
    last = min(last, total)
    return "".join(lines[first - 1:last]), first, last, total


def build_package(spec_path, lane="default"):
    task_id = spec_path.name[:-3] if spec_path.name.endswith(".md") else spec_path.stem
    if not ID_RE.match(task_id):
        raise Refused(f"spec file name must look like 004-short-name.md, got {spec_path.name}")
    head, expect, create, body = parse_spec(spec_path)
    for key in ("TASK", "SCOPE"):
        if not head.get(key):
            raise Refused(f"spec has no {key}: line")
    spec_words = (head.get("TASK", "") + "\n" + head.get("OUTPUT", "") + "\n" + body).lower()
    for term in BANNED_TERMS:
        # word-start match: "digit" must not trip "git " (2026-09-28 false positive)
        if re.search(r"(?<![a-z0-9])" + re.escape(term), spec_words):
            raise Refused(f"task text contains a banned term: '{term.strip()}'")
    for (kind, name) in (("incoming", ".task.json"), ("claimed", ".task.json"), ("done", ".task.json"),
                         ("incoming_dsa", ".task.json"), ("claimed_dsa", ".task.json")):
        if (QUEUE / kind / (task_id + name)).exists():
            raise Refused(f"a package with id {task_id} already exists in {kind}/")

    picked = resolve_scope(head["SCOPE"])
    override = head.get("OVERRIDE-CRITICAL", "") == "approved-by-operator"
    create_paths = []
    for raw in create:
        for sub in raw.split(","):
            sub = sub.strip()
            if not sub:
                continue
            rel = norm_rel(sub)
            if not rel or re.match(r"^[A-Za-z]:", rel):
                raise Refused(f"CREATE entry must be a path relative to the repository root: {sub}")
            target = (REPO / rel).resolve()
            try:
                target.relative_to(REPO.resolve())
            except ValueError:
                raise Refused(f"CREATE entry points outside the repository: {sub}")
            if rel.lower() in CRITICAL:
                raise Refused(
                    f"CREATE names a critical file {rel}; critical files must already "
                    f"exist and go through SCOPE with OVERRIDE-CRITICAL"
                )
            if rel not in create_paths:
                create_paths.append(rel)
    blocks, scope_meta = [], []
    for path, first, last in picked:
        rel = rel_of(path)
        if rel.lower() in CRITICAL and not override:
            raise Refused(f"SCOPE includes critical file {rel}; add the line OVERRIDE-CRITICAL: approved-by-operator")
        if first is None and path.stat().st_size > MAX_FILE_BYTES:
            raise Refused(f"{rel} is {path.stat().st_size // 1024} KB; scope it by line range, for example {rel}:1-300")
        content, a, b, total = slice_of(path, first, last)
        where = f"whole file, {total} lines" if first is None else f"lines {a}-{b} of {total}"
        if not content.endswith("\n"):
            content += "\n"
        blocks.append(f"<<<SOURCE {rel} ({where})\n{content}>>>END SOURCE")
        scope_meta.append({
            "path": rel,
            "lines": None if first is None else [a, b],
            "sha256": sha12(content.encode("utf-8")) if first is not None else sha12(path.read_bytes()),
            "bytes": len(content.encode("utf-8")),
        })

    task_lines = [f"TASK: {head['TASK']}"]
    if head.get("OUTPUT"):
        task_lines.append(f"OUTPUT: {head['OUTPUT']}")
    if body:
        task_lines += ["", body]
    task_text = "\n".join(task_lines)

    prompt = (
        WORKER_RULES
        + f"\n\n=== SOURCE FILES ({len(blocks)} files, read from disk {utc_stamp()}) ===\n\n"
        + "\n\n".join(blocks)
        + "\n\n=== END OF SOURCE FILES ===\n\n=== TASK ===\n"
        + task_text
        + "\n\nAnswer from the SOURCE blocks only. Start with the five lines TASK, STATUS, SUMMARY, FINDINGS, NEXT.\n"
    )
    output_tokens = int(head.get("OUTPUT_TOKENS") or DEFAULT_OUTPUT_TOKENS)
    est_tokens = math.ceil(len(prompt) / CHARS_PER_TOKEN)
    need = est_tokens + output_tokens + PROMPT_MARGIN_TOKENS
    if need > CTX_MAX:
        raise Refused(
            f"too large for one task: about {est_tokens} prompt tokens + {output_tokens} reply tokens "
            f"> {CTX_MAX}; split SCOPE into smaller packages or use line ranges"
        )
    num_ctx = max(CTX_MIN, math.ceil(need / 2048) * 2048)

    pkg = {
        "schema": 1,
        "id": task_id,
        "created_utc": utc_stamp(),
        "task": head["TASK"],
        "model": head.get("MODEL") or DEFAULT_MODEL,
        "num_ctx": num_ctx,
        "num_predict": output_tokens,
        "est_prompt_tokens": est_tokens,
        "scope": scope_meta,
        "expect": expect,
        "create": create_paths,
        "spec_file": rel_of(spec_path),
        "prompt": prompt,
        **({"think": str(head["THINK"]).strip().lower() == "true"} if head.get("THINK") else {}),
    }
    if lane != "default":
        pkg["lane"] = lane
    return pkg


def cmd_pack(args):
    ensure_dirs()
    failures = 0
    for spec in args.specs:
        spec_path = Path(spec)
        if not spec_path.is_absolute():
            cand = QUEUE / "specs" / spec
            spec_path = cand if cand.exists() else (Path.cwd() / spec)
        try:
            if not spec_path.exists():
                raise Refused(f"spec not found: {spec}")
            lane = getattr(args, "lane", "default")
            pkg = build_package(spec_path, lane)
            inbox = "incoming_dsa" if lane == "dsa" else "incoming"
            out = QUEUE / inbox / f"{pkg['id']}.task.json"
            write_atomic(out, json.dumps(pkg, ensure_ascii=True, indent=1) + "\n")
            print(f"PACKED  {pkg['id']}  files={len(pkg['scope'])}  prompt~{pkg['est_prompt_tokens']} tokens  "
                  f"num_ctx={pkg['num_ctx']}  expect={len(pkg['expect'])}  model={pkg['model']}")
        except Refused as exc:
            failures += 1
            print(f"REFUSED {spec_path.name}: {exc}")
    return 1 if failures else 0


def cmd_lint(args):
    """Check only that SCOPE/CREATE lines in each spec are bare paths."""
    ok = True
    for spec in args.specs:
        spec_path = Path(spec)
        if not spec_path.is_absolute():
            cand = QUEUE / "specs" / spec
            spec_path = cand if cand.exists() else (Path.cwd() / spec)
        try:
            if not spec_path.exists():
                raise Refused(f"spec not found: {spec}")
            parse_spec(spec_path)
            print(f"OK      {spec_path.name}")
        except Refused as exc:
            ok = False
            print(f"REFUSED {spec_path.name}: {exc}")
    return 0 if ok else 1


# ---------- status ----------

HEARTBEAT_FRESH_S = 180  # a worker that has not beaten for 3 min is not running


def read_heartbeat(path):
    """(heartbeat, time, fresh). No file: (None, None, False). An unreadable file raises ValueError/OSError."""
    if not path.exists():
        return None, None, False
    hb = json.loads(read_text(path))
    t = parse_utc(hb.get("utc"))
    return hb, t, bool(t and (utc_now() - t).total_seconds() < HEARTBEAT_FRESH_S)


def last_beat(hb, t):
    return f"; last heartbeat {hb.get('state', '?')} {age_text(t)}" if hb else ""


def print_dsa_status():
    """Both lanes are dormant by design (Qwen retired 2026-10-01; DSA work goes through AIBridge + the desk board),
    so only a fresh heartbeat is shown as a live worker; anything else is one honest 'dormant' line, never a fault."""
    waiting = len(list((QUEUE / "incoming_dsa").glob("*.task.json")))
    running = len(list((QUEUE / "claimed_dsa").glob("*.task.json")))
    try:
        hb, t, fresh = read_heartbeat(QUEUE / "heartbeat_dsa.json")
    except (ValueError, OSError) as exc:
        print(f"DSA-WORKER heartbeat unreadable: {exc}; incoming_dsa {waiting}")
        return
    if not fresh:
        print(f"DSA-WORKER dormant: DSA work goes through AIBridge + the desk board (DSA_DELEGATION.md){last_beat(hb, t)}; "
              f"incoming_dsa {waiting}; running {running}")
        return
    task = f" task {hb['task']}" if hb.get("task") else ""
    note = f" ({hb['note']})" if hb.get("note") else ""
    print(f"DSA-WORKER {hb.get('state', '?')}{task}{note}, heartbeat {age_text(t)}; "
          f"incoming_dsa {waiting}; running {running}")
    if hb.get("state") == "needs-human":
        print("WARNING  DSA worker needs the operator (challenge, login or repeated errors)")


def cmd_status(args):
    ensure_dirs()
    try:
        hb, t, fresh = read_heartbeat(QUEUE / "heartbeat.json")
        if fresh:
            task = f" task {hb['task']}" if hb.get("task") else ""
            print(f"WORKER   {hb.get('state', '?')}{task}, heartbeat {age_text(t)} "
                  f"(host {hb.get('host')}, worker {hb.get('worker')})")
        else:
            print(f"WORKER   lane retired 2026-10-01 (Qwen NUC worker; scheduled task disabled on JIS-NUC; DEVICES.md){last_beat(hb, t)}")
    except (ValueError, OSError) as exc:
        print(f"WORKER   heartbeat unreadable: {exc}")
    incoming = sorted((QUEUE / "incoming").glob("*.task.json"))
    claimed = sorted((QUEUE / "claimed").glob("*.task.json"))
    replies = sorted((QUEUE / "done").glob("*.reply.json"))
    unverified = [r for r in replies if not (QUEUE / "done" / r.name.replace(".reply.json", ".verdict.txt")).exists()]
    oldest = ""
    if incoming:
        oldest = f", oldest waiting {age_text(dt.datetime.fromtimestamp(incoming[0].stat().st_mtime, dt.timezone.utc))}"
    print(f"QUEUE    waiting {len(incoming)}{oldest}; running {len(claimed)}; replies {len(replies)}; not yet verified {len(unverified)}")
    print_dsa_status()
    verdicts = sorted((QUEUE / "done").glob("*.verdict.txt"), key=lambda p: p.stat().st_mtime)[-3:]
    for v in verdicts:
        first_two = read_text(v).splitlines()[:2]
        status = first_two[1].split(":", 1)[1].strip() if len(first_two) > 1 and ":" in first_two[1] else "?"
        print(f"RECENT   {v.name[:-len('.verdict.txt')]}: {status}")
    return 0


# ---------- verify ----------

def load_json(path):
    return json.loads(read_text(path))


def find_package(task_id):
    for kind in ("done", "claimed", "incoming", "claimed_dsa", "incoming_dsa"):
        p = QUEUE / kind / f"{task_id}.task.json"
        if p.exists():
            return load_json(p)
    return None


def current_hash(entry):
    path = REPO / entry["path"]
    if not path.exists():
        return None
    if entry.get("lines"):
        try:
            content, _, _, _ = slice_of(path, entry["lines"][0], entry["lines"][1])
        except Refused:
            return None
        if not content.endswith("\n"):
            content += "\n"
        return sha12(content.encode("utf-8"))
    return sha12(path.read_bytes())


def match_line_endings(new_text, old_text):
    crlf = old_text.count("\r\n")
    lf_only = old_text.count("\n") - crlf
    new_text = new_text.replace("\r\n", "\n")
    if old_text.endswith("\n") and not new_text.endswith("\n"):
        new_text += "\n"
    if crlf > lf_only:
        new_text = new_text.replace("\n", "\r\n")
    return new_text


def verify_one(task_id):
    done = QUEUE / "done"
    reply_path = done / f"{task_id}.reply.json"
    if not reply_path.exists():
        return None, [f"no reply for {task_id} in done/"]
    reply = load_json(reply_path)
    pkg = find_package(task_id) or {}
    task_line = pkg.get("task", "(package not found)")
    fail, review, notes = [], [], []

    if reply.get("worker_status") != "ok":
        fail.append(f"worker error: {reply.get('error', 'unknown')}")
    response = ANSI_RE.sub("", reply.get("response") or "")
    if reply.get("done_reason") == "timeout":
        fail.append("reply timed out before the answer was stable; it may be cut off (browser worker)")
    if reply.get("done_reason") == "length":
        fail.append(f"reply cut off at the {pkg.get('num_predict')} token limit; raise OUTPUT_TOKENS or narrow the task")

    # 1. acceptance checks written by the coordinator, never shown to the model
    expect = pkg.get("expect") or []
    flat = squash(response)
    missing = [e for e in expect if squash(e) not in flat]
    for e in missing:
        fail.append(f"expected text missing: {e[:90]}")

    # 2. file names the reply mentions that do not exist
    scope_paths = {e["path"] for e in pkg.get("scope", [])}
    scope_names = {p.rsplit("/", 1)[-1] for p in scope_paths}
    scope_dirs = {(REPO / p).parent for p in scope_paths}
    create_paths = {norm_rel(p) for p in pkg.get("create", [])}
    create_names = {p.rsplit("/", 1)[-1] for p in create_paths}
    # Every <<<FILE ...>>> header the model wrote, whether or not its closing
    # marker matched FILE_BLOCK_RE. These are proposal targets -- the task's
    # own output -- never an "unknown file name", regardless of whether
    # section 4 below ends up actually writing them.
    declared_targets = {norm_rel(m.group(1)) for m in FILE_HEADER_RE.finditer(response)}
    declared_names = {p.rsplit("/", 1)[-1] for p in declared_targets}
    proposals = list(FILE_BLOCK_RE.finditer(response))
    prose = FILE_BLOCK_RE.sub("", response)
    unknown, warn = [], []
    for ref in sorted(set(PATH_REF_RE.findall(prose))):
        r = norm_rel(ref)
        name = r.rsplit("/", 1)[-1]
        known = (
            r in scope_paths or r in scope_names
            or r in create_paths or r in create_names
            or r in declared_targets or name in declared_names
        )
        if known:
            continue
        if "/" in r and (REPO / r).exists():
            continue
        if "/" not in r and (name in scope_names or any((d / name).exists() for d in scope_dirs) or (REPO / name).exists()):
            continue
        if "/" in r:
            # looks like a genuine file path the model invented out of thin air
            unknown.append(r)
        else:
            # a bare name with no directory is very likely a literal used
            # inside code or test data (a sample CSV name, say) and not a
            # reference to a real file; note it, do not block on it.
            warn.append(r)
    for r in unknown:
        fail.append(f"file name not found in scope or repository: {r}")
    for r in warn:
        review.append(f"name not found in scope or repository, referenced only in code/text: {r}")

    # 3. inputs changed since packing
    for entry in pkg.get("scope", []):
        now = current_hash(entry)
        if now != entry["sha256"]:
            review.append(f"input changed since packing: {entry['path']}")

    # 4. proposed file changes: written as <target>.new next to the target, plus one diff file
    diff_chunks = []
    written_py = []
    for m in proposals:
        target_rel = norm_rel(m.group(1))
        body = m.group(2)
        target = (REPO / target_rel).resolve()
        try:
            target.relative_to(REPO.resolve())
        except ValueError:
            fail.append(f"proposal points outside the repository: {target_rel}")
            continue
        if target_rel not in scope_paths and target_rel not in create_paths:
            review.append(f"proposal for a file outside the task scope, not written: {target_rel}")
            continue
        old_text = read_text(target) if target.exists() else ""
        new_text = match_line_endings(body, old_text)
        new_path = target.with_name(target.name + ".new")
        if new_path.exists():
            new_path = done / task_id / (target_rel.replace("/", "__") + ".new")
            review.append(f"{target_rel}.new already existed; proposal kept at {rel_of(new_path)}")
        write_atomic(new_path, new_text)  # newline="\n" writes CRLF text unchanged
        diff = list(difflib.unified_diff(
            old_text.replace("\r\n", "\n").splitlines(keepends=True),
            new_text.replace("\r\n", "\n").splitlines(keepends=True),
            fromfile=f"a/{target_rel}", tofile=f"b/{target_rel}.new"))
        added = sum(1 for d in diff if d.startswith("+") and not d.startswith("+++"))
        removed = sum(1 for d in diff if d.startswith("-") and not d.startswith("---"))
        crit = "; CRITICAL FILE: four-step proof on apply" if target_rel.lower() in CRITICAL else ""
        review.append(f"proposal {rel_of(new_path)}: +{added} -{removed} lines{crit}")
        diff_chunks.append("".join(diff))
        if target_rel.endswith(".py"):
            written_py.append((target_rel, new_path))
    if diff_chunks:
        write_atomic(done / f"{task_id}.diff", "\n".join(diff_chunks))

    # 5. compile/test gate: a claimed DONE that does not even parse must not pass
    if written_py:
        by_stem = {Path(t).stem: p for t, p in written_py}
        syntax_fail = []
        for target_rel, new_path in written_py:
            with tempfile.TemporaryDirectory() as td:
                tmp_py = Path(td) / Path(target_rel).name
                shutil.copyfile(new_path, tmp_py)
                try:
                    r = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(tmp_py)],
                        capture_output=True, text=True, timeout=30,
                    )
                except subprocess.TimeoutExpired:
                    syntax_fail.append((target_rel, "py_compile timed out"))
                    continue
                if r.returncode != 0:
                    msg_lines = (r.stderr or r.stdout).strip().splitlines()
                    syntax_fail.append((target_rel, msg_lines[-1] if msg_lines else "compile error"))
        if syntax_fail:
            for target_rel, msg in syntax_fail:
                fail.append(f"syntax error in proposal {target_rel}: {msg}")
        else:
            failing_tests, ran_any, total_n, passed_n = [], False, 0, 0
            for target_rel, new_path in written_py:
                stem = Path(target_rel).stem
                if not stem.startswith("test_"):
                    continue
                module_path = by_stem.get(stem[len("test_"):])
                if module_path is None:
                    continue
                ran_any = True
                with tempfile.TemporaryDirectory() as td:
                    tdp = Path(td)
                    shutil.copyfile(module_path, tdp / f"{stem[len('test_'):]}.py")
                    shutil.copyfile(new_path, tdp / f"{stem}.py")
                    try:
                        r = subprocess.run(
                            [sys.executable, "-m", "unittest", stem],
                            cwd=str(tdp), capture_output=True, text=True, timeout=120,
                        )
                    except subprocess.TimeoutExpired:
                        failing_tests.append(f"{stem} (timed out)")
                        continue
                    out = r.stdout + r.stderr
                    m = re.search(r"Ran (\d+) tests?", out)
                    n = int(m.group(1)) if m else 0
                    total_n += n
                    if r.returncode == 0:
                        passed_n += n
                    else:
                        names = re.findall(r"^(?:FAIL|ERROR): (\S+)", out, re.M)
                        failing_tests.extend(names or [f"{stem} (failed)"])
            if not ran_any:
                review.append("compile OK (no matching test_*.py proposal to run)")
            elif failing_tests:
                review.append(f"tests failing: {', '.join(failing_tests[:10])}")
            else:
                review.append(f"compile OK, tests {passed_n}/{total_n}")

    tokens_in = reply.get("prompt_eval_count")
    tokens_out = reply.get("eval_count")
    secs = reply.get("wall_seconds")
    notes.append(f"tokens in {tokens_in} (packed estimate {pkg.get('est_prompt_tokens')}), out {tokens_out}, "
                 f"context {reply.get('num_ctx')}, {secs} s on {reply.get('host')}")

    verdict = "FAIL" if fail else ("REVIEW" if review else "PASS")
    status = {"PASS": "DONE", "REVIEW": "PARTIAL", "FAIL": "BLOCKED"}[verdict]
    next_step = {
        "PASS": "accept the reply",
        "REVIEW": "read the listed proposals or changed inputs, then apply or discard",
        "FAIL": "do not use this reply; fix the listed cause and pack a new task",
    }[verdict]
    findings = (f"verdict {verdict}; expected {len(expect) - len(missing)}/{len(expect)}; "
                f"unknown file names {len(unknown)}; proposals {len(proposals)}")
    out = [
        f"TASK:     {task_id} - {task_line}",
        f"STATUS:   {status}",
        f"SUMMARY:  {notes[0]}",
        f"FINDINGS: {findings}",
        f"NEXT:     {next_step}",
    ]
    details = fail + review
    out += [f"  - {d}" for d in details[:20]]
    if len(details) > 20:
        out.append(f"  - ... {len(details) - 20} more")
    write_atomic(done / f"{task_id}.verdict.txt", "\n".join(out) + "\n")
    return verdict, out


def cmd_verify(args):
    ensure_dirs()
    done = QUEUE / "done"
    ids = args.ids
    if not ids:
        ids = sorted(
            p.name[:-len(".reply.json")] for p in done.glob("*.reply.json")
            if not (done / p.name.replace(".reply.json", ".verdict.txt")).exists()
        )
        if not ids:
            print("nothing to verify")
            return 0
    worst = 0
    for task_id in ids:
        verdict, lines = verify_one(task_id)
        print("\n".join(lines))
        worst = max(worst, {"PASS": 0, "REVIEW": 1, "FAIL": 2, None: 2}[verdict])
    return worst


# ---------- deploy ----------

def cmd_deploy(args):
    ensure_dirs()
    src_dir = REPO / "scripts" / "worker"
    for name in DEPLOY_FILES:
        src = src_dir / name
        if not src.exists():
            print(f"MISSING {src}")
            return 1
        dst = QUEUE / "deploy" / name
        tmp = dst.with_name("." + name + ".tmp")
        shutil.copyfile(src, tmp)
        os.replace(tmp, dst)
        print(f"DEPLOYED {name}  sha256 {sha12(dst.read_bytes())}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="NUC worker queue tool (coordinator side)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pack", help="build task packages from spec files")
    p.add_argument("specs", nargs="+")
    p.add_argument("--lane", choices=("default", "dsa"), default="default",
                   help="dsa: write to incoming_dsa/ for the browser worker")
    p.set_defaults(func=cmd_pack)
    l = sub.add_parser("lint", help="check SCOPE/CREATE lines are bare paths, nothing else")
    l.add_argument("specs", nargs="+")
    l.set_defaults(func=cmd_lint)
    s = sub.add_parser("status", help="queue and worker summary")
    s.set_defaults(func=cmd_status)
    v = sub.add_parser("verify", help="mechanical checks on replies")
    v.add_argument("ids", nargs="*")
    v.set_defaults(func=cmd_verify)
    d = sub.add_parser("deploy", help="publish worker scripts to deploy/")
    d.set_defaults(func=cmd_deploy)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
