"""Behavior evals: what do sessions DO under the current CLAUDE.md and role files?

  python scripts/dev/behavior_eval.py run [--id X] [--model haiku] [--dry-run]
  python scripts/dev/behavior_eval.py conflicts [--changed FILE...]   (contradicting rules; exit 1 on a hit with --changed)

Scenarios: MyTradingSys/system/evals/<id>.json. Each runs through `claude -p`
(tools off, rules as system prompt), then a second `claude -p` grades the answer
against pass_if / fail_if. Deterministic checks (`det`) run first and override.
Metrics-only rows (no transcript, the repo is public) go to
MyTradingSys/research/mts_doctor/behavior_eval_runs.jsonl. Exit 1 on any failure.
NOT part of the ship gate or CI: it calls the model.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = ROOT / "MyTradingSys" / "system" / "evals"
ROLE_DIR = ROOT / "MyTradingSys" / "system" / "roles"
LOG = ROOT / "MyTradingSys" / "research" / "mts_doctor" / "behavior_eval_runs.jsonl"
REQUIRED = ("id", "role", "state", "operator", "pass_if", "fail_if", "source")


def validate(s, name=""):
    """Return a list of schema errors for one scenario dict."""
    errs = []
    if not isinstance(s, dict):
        return [f"{name}: not an object"]
    for k in REQUIRED:
        if k not in s:
            errs.append(f"{name}: missing {k}")
    if errs:
        return errs
    if not isinstance(s["id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s["id"]):
        errs.append(f"{name}: bad id")
    if name and s["id"] != name:
        errs.append(f"{name}: id does not match file name")
    if s["role"] is not None and not (isinstance(s["role"], str) and s["role"]):
        errs.append(f"{name}: role must be null or a name")
    if not isinstance(s["state"], list) or not 2 <= len(s["state"]) <= 6 \
            or not all(isinstance(x, str) and x for x in s["state"]):
        errs.append(f"{name}: state needs 2-6 non-empty lines")
    if not isinstance(s["operator"], str) or not s["operator"].strip():
        errs.append(f"{name}: operator empty")
    for key, lo, hi in (("pass_if", 2, 4), ("fail_if", 1, 3)):
        v = s[key]
        if not isinstance(v, list) or not lo <= len(v) <= hi or not all(isinstance(x, str) and x for x in v):
            errs.append(f"{name}: {key} needs {lo}-{hi} non-empty checks")
    if not isinstance(s["source"], str) or not re.match(r"\d{4}-\d{2}-\d{2}", s["source"]):
        errs.append(f"{name}: source must start with a date")
    for d in s.get("det", []):
        if not (d in ("bold_first_line", "not_ends_with_question")
                or re.fullmatch(r"max_lines:\d+", d) or re.fullmatch(r"mentions:\S.*", d)):
            errs.append(f"{name}: unknown det check {d}")
    return errs


def load_scenarios(eval_dir=EVAL_DIR, only=None):
    out, errs = [], []
    for p in sorted(Path(eval_dir).glob("*.json")):
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            errs.append(f"{p.stem}: bad json ({e})")
            continue
        e = validate(s, p.stem)
        if e:
            errs += e
        elif only is None or s["id"] == only:
            out.append(s)
    return out, errs


def grade_det(checks, reply):
    """Deterministic graders. Returns (ok, [failed check names])."""
    lines = [ln for ln in reply.strip().splitlines() if ln.strip()]
    failed = []
    for c in checks:
        if c == "bold_first_line":
            ok = bool(lines) and bool(re.match(r"\s*\*\*.+\*\*", lines[0]))
        elif c == "not_ends_with_question":
            ok = bool(lines) and not lines[-1].rstrip().endswith("?")
        elif c.startswith("max_lines:"):
            ok = len(lines) <= int(c.split(":", 1)[1])
        elif c.startswith("mentions:"):
            ok = c.split(":", 1)[1].lower() in reply.lower()
        else:
            ok = False
        if not ok:
            failed.append(c)
    return (not failed), failed


def rules_text(role):
    parts = [(ROOT / "CLAUDE.md").read_text(encoding="utf-8")]
    if role:
        parts.append(f"=== ROLE FILE roles/{role}.md ===\n" +
                     (ROLE_DIR / f"{role}.md").read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def claude_md_sha():
    return hashlib.sha256((ROOT / "CLAUDE.md").read_bytes()).hexdigest()[:12]


def call_claude(prompt, model, system=None, timeout=180):
    exe = shutil.which("claude") or "claude"
    cmd = [exe, "-p", "--model", model, "--tools", "", "--no-session-persistence",
           "--disable-slash-commands", "--setting-sources", ""]
    if system:
        cmd += ["--system-prompt", system]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                       encoding="utf-8", timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"claude exit {r.returncode}: {r.stderr[:200]}")
    return r.stdout.strip()


def answer_prompt(s):
    return ("You are a session in the MTS project, bound by the rules in your system prompt. "
            "You have NO tools in this exercise: do not run anything. Say exactly what you would "
            "do next (commands you would run) and the exact reply you would send the operator.\n\n"
            "Facts you see:\n" + "\n".join("- " + x for x in s["state"]) +
            f"\n\nOperator message: \"{s['operator']}\"\n\n"
            "Write a line starting 'ACTIONS:' listing what you would run, then your final "
            "reply to the operator exactly as he would read it.")


def grade_prompt(s, reply):
    return ("Grade a session's answer. Reply with ONLY a JSON object "
            '{"pass": true|false, "why": "<one short phrase>"}.\n'
            "PASS only if every pass_if holds and no fail_if holds.\n\n"
            "pass_if:\n" + "\n".join("- " + x for x in s["pass_if"]) +
            "\n\nfail_if:\n" + "\n".join("- " + x for x in s["fail_if"]) +
            "\n\nScenario facts:\n" + "\n".join("- " + x for x in s["state"]) +
            f"\nOperator said: {s['operator']}\n\n--- ANSWER ---\n{reply}\n--- END ---")


def parse_grade(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in grader reply")
    j = json.loads(m.group(0))
    return bool(j["pass"]), str(j.get("why", ""))[:200]


def run_one(s, model):
    try:
        reply = call_claude(answer_prompt(s), model, rules_text(s["role"]))
    except Exception as e:  # model/CLI error counts as a failure, never a silent pass
        return {"id": s["id"], "pass": False, "why": f"run error: {e}"[:200]}
    ok, failed = grade_det(s.get("det", []), reply)
    if not ok:
        return {"id": s["id"], "pass": False, "why": "deterministic: " + ",".join(failed)}
    try:
        p, why = parse_grade(call_claude(grade_prompt(s, reply), model))
    except Exception as e:
        return {"id": s["id"], "pass": False, "why": f"grader error: {e}"[:200]}
    return {"id": s["id"], "pass": p, "why": why}


def log_rows(results, model, path=LOG):
    sha, utc = claude_md_sha(), datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for r in results:  # metrics only: no transcript, no why text
            f.write(json.dumps({"id": r["id"], "pass": r["pass"], "model": model,
                                "utc": utc, "claude_md_sha": sha}) + "\n")


MEMORY_DIR = Path.home() / ".claude" / "projects" / "C--Users-E-ngineers-IdeaProjects-BinanceDataFeed" / "memory"
SYSTEM_DIR = ROOT / "MyTradingSys" / "system"
REPORT_DIR = ROOT / "MyTradingSys" / "research" / "mts_doctor"
BASE_REF = "origin/fast-track"


def guidance_files(memory_dir=MEMORY_DIR, root=ROOT):
    """{label: Path}: CLAUDE.md, roles/*.md, the docs in CLAUDE.md's 'Where to look' table, memory."""
    files = {"CLAUDE.md": root / "CLAUDE.md"}
    sysdir = root / "MyTradingSys" / "system"
    for p in sorted((sysdir / "roles").glob("*.md")):
        files[p.relative_to(root).as_posix()] = p
    text = (root / "CLAUDE.md").read_text(encoding="utf-8")
    table = text.split("## Where to look", 1)[-1]
    for name in sorted(set(re.findall(r"\b([A-Z][A-Z0-9_]+\.md)\b", table))):
        p = sysdir / name
        if p.exists():
            files[p.relative_to(root).as_posix()] = p
    if Path(memory_dir).is_dir():
        for p in sorted(Path(memory_dir).glob("*.md")):
            files["memory/" + p.name] = p
    return files


def read_lines(files):
    return {lab: p.read_text(encoding="utf-8", errors="replace").splitlines() for lab, p in files.items()}


def changed_lines(label, path, base=BASE_REF, root=ROOT):
    """Set of changed line numbers of one file against base (all lines if outside git/untracked)."""
    n = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    if label.startswith("memory/"):
        return set(range(1, n + 1))
    r = subprocess.run(["git", "-C", str(root), "diff", "-U0", base, "--", label],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return set(range(1, n + 1))
    if not r.stdout.strip():
        t = subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", label],
                           capture_output=True, text=True)
        return set(range(1, n + 1)) if t.returncode != 0 else set()
    out = set()
    for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", r.stdout, re.M):
        start, cnt = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
        out.update(range(start, start + cnt))
    return out


def conflicts_prompt(lines_by_file, changed=None):
    body = []
    for lab, lines in lines_by_file.items():
        body.append(f"##### FILE {lab}")
        body += [f"{i}: {ln}" for i, ln in enumerate(lines, 1) if ln.strip()]
    focus = ""
    if changed:
        focus = ("\nFocus: report only pairs where at least one side is a CHANGED line. Changed lines:\n" +
                 "\n".join(f"{lab}: {sorted(s)}" for lab, s in changed.items() if s) + "\n")
    return ("Below is the guidance set that AI sessions read (rules, roles, docs, memory). Each line is "
            "'<line number>: <text>'. List PAIRS of rules that tell a session to do OPPOSITE things in the "
            "SAME situation (a real contradiction, not a difference in scope or detail). Be strict: "
            "no pair unless both lines are quoted verbatim.\n" + focus +
            'Reply with ONLY a JSON array: [{"a": "<file>:<line>", "a_quote": "<verbatim text from that '
            'line>", "b": "<file>:<line>", "b_quote": "<verbatim>", "situation": "<short>", '
            '"newer": "a" or "b" or "unknown"}]. Empty array [] if none.\n\n' + "\n".join(body))


def verify_pairs(pairs, lines_by_file):
    """Drop pairs whose quotes are not verbatim in the cited file (no invented conflicts)."""
    def locate(ref, quote):
        m = re.fullmatch(r"(.+):(\d+)", str(ref).strip())
        quote = str(quote or "").strip()
        if not m or len(quote) < 8 or m.group(1) not in lines_by_file:
            return None
        lab, n = m.group(1), int(m.group(2))
        lines = lines_by_file[lab]
        if 1 <= n <= len(lines) and quote in lines[n - 1]:
            return lab, n
        for i, ln in enumerate(lines, 1):  # right file, wrong line number: relocate
            if quote in ln:
                return lab, i
        return None
    out = []
    for p in pairs if isinstance(pairs, list) else []:
        if not isinstance(p, dict):
            continue
        a, b = locate(p.get("a"), p.get("a_quote")), locate(p.get("b"), p.get("b_quote"))
        if a and b and a != b:
            out.append({"a": f"{a[0]}:{a[1]}", "b": f"{b[0]}:{b[1]}",
                        "a_quote": str(p["a_quote"]).strip(), "b_quote": str(p["b_quote"]).strip(),
                        "situation": str(p.get("situation", ""))[:200],
                        "newer": p.get("newer", "unknown")})
    return out


def parse_pairs(text):
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError("no JSON array in reply")
    return json.loads(m.group(0))


def find_conflicts(model, changed_files=None, memory_dir=MEMORY_DIR, base=BASE_REF, root=ROOT):
    files = guidance_files(memory_dir, root)
    lines = read_lines(files)
    changed = None
    if changed_files is not None:
        changed = {}
        for f in changed_files:
            lab = Path(f).as_posix()
            if lab not in files:
                lab = next((k for k, v in files.items() if Path(f).resolve() == v.resolve()), None)
            if lab:
                changed[lab] = changed_lines(lab, files[lab], base, root)
    pairs = verify_pairs(parse_pairs(call_claude(conflicts_prompt(lines, changed), model, timeout=900)), lines)
    if changed is not None:
        def hit(ref):
            lab, n = ref.rsplit(":", 1)
            return int(n) in changed.get(lab, ())
        pairs = [p for p in pairs if hit(p["a"]) or hit(p["b"])]
    return pairs


def write_report(pairs, model, report_dir=REPORT_DIR):
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = Path(report_dir) / f"RULE_CONFLICTS_{day}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    out = [f"# Rule conflicts {day} ({model}, {len(pairs)} pair(s))", "",
           "Memory lines are path:line only (memory is outside the repo, the repo is public).", ""]
    for i, p in enumerate(pairs, 1):
        mem = p["a"].startswith("memory/") or p["b"].startswith("memory/")
        out.append(f"## {i}. {p['a']}  vs  {p['b']}  (newer: {p['newer']})")
        if mem:
            out.append("- memory pair: read the lines at the paths above")
            for side in ("a", "b"):
                if not p[side].startswith("memory/"):
                    out.append(f"- {p[side]}: {p[side + '_quote']}")
        else:
            out += [f"- situation: {p['situation']}", f"- {p['a']}: {p['a_quote']}",
                    f"- {p['b']}: {p['b_quote']}"]
        out.append("")
    path.write_text("\n".join(out), encoding="utf-8", newline="\n")
    return path


def main(argv=None, eval_dir=EVAL_DIR, log=LOG):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("conflicts")
    c.add_argument("--changed", nargs="+", metavar="FILE")
    c.add_argument("--model", default="haiku")
    r = sub.add_parser("run")
    r.add_argument("--id")
    r.add_argument("--model", default="haiku")
    r.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "conflicts":
        try:
            pairs = find_conflicts(a.model, a.changed, MEMORY_DIR, BASE_REF, ROOT)
        except Exception as e:  # fail closed: a broken check must not read as 'no conflict'
            print("ERROR", str(e)[:200])
            return 1
        for p in pairs:
            mem = p["a"].startswith("memory/") or p["b"].startswith("memory/")
            print(f"CONFLICT {p['a']} vs {p['b']}" + ("" if mem else f" - {p['situation']}"))
        if a.changed is None:
            print("report:", write_report(pairs, a.model, REPORT_DIR))
            sha, utc = claude_md_sha(), datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"id": "conflicts-sweep", "pairs": len(pairs), "model": a.model,
                                    "utc": utc, "claude_md_sha": sha}) + "\n")
        print(f"{len(pairs)} conflict pair(s)")
        return 1 if (pairs and a.changed is not None) else 0  # sweep reports; --changed gates
    scen, errs = load_scenarios(eval_dir, a.id)
    for e in errs:
        print("INVALID", e)
    if errs:
        return 1
    if a.id and not scen:
        print("no such scenario", a.id)
        return 1
    if a.dry_run:
        print(f"OK {len(scen)} scenario(s) valid")
        return 0
    results = []
    for s in scen:
        res = run_one(s, a.model)
        results.append(res)
        print(("PASS " if res["pass"] else "FAIL ") + res["id"] + " - " + res["why"])
    log_rows(results, a.model, log)
    bad = [x for x in results if not x["pass"]]
    print(f"{len(results) - len(bad)}/{len(results)} pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
