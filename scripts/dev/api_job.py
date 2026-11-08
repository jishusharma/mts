"""Headless Builder jobs on the Claude API credit: one launcher so every super session runs them the same way.

<<<<<<< Updated upstream
  python scripts/dev/api_job.py launch <slug> --card <card-id> --model claude-opus-5-5 --max-usd 8 [--max-turns 200] [--max-tokens 32000] [--dry-run]
=======
  python scripts/dev/api_job.py launch <slug> --card <card-id> --model claude-opus-5-5 --max-usd 8 [--max-turns 200] [--dry-run]
>>>>>>> Stashed changes
  python scripts/dev/api_job.py launch <slug> --prompt-file p.txt ...        (a prompt of your own instead of a card brief)
  python scripts/dev/api_job.py status [<slug>]          running | done (cost, turns, minutes, last line) for one or all runs
  python scripts/dev/api_job.py ledger <slug> --outcome "shipped <sha>; <number>"   append the Spent row (PLAN_API_CREDITS_*.md)
  python scripts/dev/api_job.py total                    USD in the Spent ledger (today and all)

<<<<<<< Updated upstream
Engine (2026-11-07): default `--engine api` runs scripts/dev/api_agent.py on the raw Messages API, the only path the promotional
credit pays; `--engine claude` (`claude -p`) carries the claude-code beta, which the org refuses ("credit balance is too low"), and
with an OAuth login present it silently bills that login's subscription (every Spent row before 2026-11-07 was such a run).
=======
>>>>>>> Stashed changes
Rules (PLAN_API_CREDITS_2026-11-04.md): one job at a time per machine; every job carries --max-budget-usd; the key is read from
F:/ClaudePlaform/key.txt (env MTS_API_KEY_FILE overrides) into the child's environment only, never printed, logged or put in a
prompt; a prompt that names a secret-like path is refused; hooks are off under a nested headless run (disableAllHooks), so the
Builder preamble below carries the CLAUDE.md rules. Output: F:/MTS/api_runs/<slug>/{out.jsonl,err.txt,meta.json,prompt.txt}.
Wake on completion: `supervisor.py wait --login <L>` with run_in_background (wakes on a job end and AT the 5 h reset; never `&`).
"""
from __future__ import annotations
import argparse
import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[2]
RUNS = Path(os.environ.get("MTS_API_RUNS", "F:/MTS/api_runs"))
KEY_FILE_DEFAULT = "F:/ClaudePlaform/key.txt"
LEDGER = REPO / "MyTradingSys/system/PLAN_API_CREDITS_2026-11-04.md"
BLOCKED = (".secrets", ".env", ".pem", ".key", "api_key", "apikey", "key.txt", ".ovpn")
<<<<<<< Updated upstream
MODEL_NAMES = {"claude-opus-5-5": "Opus 5.5", "claude-sonnet-5-5": "Sonnet 5.5", "claude-haiku-5-5": "Haiku 5.5",
               "claude-fable-5-1": "Fable 5.1"}
=======
MODEL_NAMES = {"claude-opus-5-5": "Opus 5.5", "claude-sonnet-5-5": "Sonnet 5.5", "claude-haiku-5-5": "Haiku 5.5"}
>>>>>>> Stashed changes

PREAMBLE = """You are Builder. Headless job on the Claude API credit; hooks are off, so these rules replace them.
Boot: python scripts/dev/sync.py start {slug} --worker; work only in the printed WORKTREE (git -C <tree> for git, never cd x && git).
Card: {card}. Claim it first: python scripts/dev/sync.py claim "{card}".
Run with zero operator input: never ask; take the conservative default, log DECISION (OURS) in the card note, continue.
Hard rules: testnet only; never read .secrets/, .env, keys; never deploy, restart processes, touch HALT, open trades; never commit
runtime/order/account data (public repo); never commit to master; never rebase/reset/force-push. Windows: write files with newline='\\n'.
Gate: new tests must fail on the pre-change code once; python scripts/dev/run_all_tests.py --quick before the ship.
Ship once: python scripts/dev/sync.py ship --release {slug} (commit body carries a `Result: <what works now / the number>` line and a `Next: <card-id | stage | END: why>` line,
ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`); then python scripts/dev/tasks.py done {card} --result "<number/file>" --next "<same tag>".
Feeder rule (ANNOUNCEMENTS A-20261104-1): if you ship a study or a .py file, file its companion card the same run:
python scripts/dev/tasks.py new --lane CODEX --prio 3 --kind audit "[GEMINI] blind read of <file>" (or a gpt-spec-tests-<name> CODEX card).
Stop at the turn cap and report. Final reply, at most 6 lines: `Result:` line first, then the content sha, then `Noticed:` (or `Noticed: none`).

{brief}
"""


def die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def check_prompt(text: str) -> None:
    low = text.lower()
    hit = [b for b in BLOCKED if b in low]
    if hit:
        die(f"REFUSED: prompt names a secret-like path {hit}")


def key_file() -> Path:
    return Path(os.environ.get("MTS_API_KEY_FILE", KEY_FILE_DEFAULT))


def child_env(base: dict, kf: Path) -> dict:
    env = {k: v for k, v in base.items() if k not in ("CLAUDE_CODE_OAUTH_TOKEN", "CLAUDECODE")}
    env["ANTHROPIC_API_KEY"] = "".join(io.open(kf, encoding="utf-8").read().split())
    return env


<<<<<<< Updated upstream
def build_cmd(model: str, max_usd: float, max_turns: int, engine: str = "api", cwd: str = "", out_dir: str = "",
              max_tokens: int | None = None) -> list[str]:
    if engine == "api":  # raw Messages API: the only path the promotional credit pays (measured 2026-11-07, see api_agent.py)
        cmd = [sys.executable, str(REPO / "scripts/dev/api_agent.py"), "--model", model, "--max-usd", str(max_usd),
               "--max-turns", str(max_turns), "--cwd", cwd or str(REPO), "--out", out_dir]
        return cmd + ["--max-tokens", str(max_tokens)] if max_tokens else cmd
=======
def build_cmd(model: str, max_usd: float, max_turns: int) -> list[str]:
>>>>>>> Stashed changes
    exe = shutil.which("claude") or "claude"
    return [exe, "-p", "--model", model, "--permission-mode", "bypassPermissions",
            "--settings", '{"disableAllHooks":true}', "--max-budget-usd", str(max_usd), "--max-turns", str(max_turns),
            "--output-format", "stream-json", "--verbose"]


def compose_prompt(brief: str, slug: str, card: str) -> str:
    return PREAMBLE.format(slug=slug, card=card, brief=brief)


def card_brief(card: str) -> str:
    r = subprocess.run([sys.executable, str(REPO / "scripts/dev/tasks.py"), "brief", card], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0 or not r.stdout.strip():
        die(f"tasks.py brief {card} failed: {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def parse_result(out: Path) -> dict:
    last = None
    if out.exists():
        for line in io.open(out, encoding="utf-8", errors="replace"):
            line = line.strip()
            if line.startswith("{"):
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") == "result":
                    last = rec
    if not last:
        return {"done": False, "cost": None, "turns": None, "minutes": None, "subtype": None, "text": ""}
    return {"done": True, "cost": last.get("total_cost_usd"), "turns": last.get("num_turns"),
            "minutes": int(last.get("duration_ms", 0) or 0) // 60000, "subtype": last.get("subtype"),
            "text": str(last.get("result", ""))[:400]}


def running_jobs() -> list[str]:
    out = []
    for d in sorted(RUNS.glob("*/")) if RUNS.exists() else []:
        meta = d / "meta.json"
        if meta.exists() and not parse_result(d / "out.jsonl")["done"]:
            try:
                m = json.loads(meta.read_text(encoding="utf-8"))
            except ValueError:
                m = {}
            started = m.get("started", "")
            if started and (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(started)).total_seconds() < 6 * 3600:
                out.append(d.name)
    return out


def wait_line() -> str:
    """stall-fix-1104: the one wake source after a launch. A bg_watch/`&` watcher wakes nobody once the turn ends (L1 idled 3 h)."""
    return ("WAIT start `python scripts/dev/supervisor.py wait --login <L>` as a Bash call with run_in_background: true (no `&`, no "
            "redirect); it wakes you when this job ends and AT the 5 h reset; then end the turn with `supervisor.py watchcheck`")


def launch(a) -> None:
    if a.card:
        brief = card_brief(a.card)
        check_prompt(brief)  # the fixed preamble names the forbidden paths on purpose; only the brief is checked
        prompt = compose_prompt(brief, a.slug, a.card)
    elif a.prompt_file:
        prompt = io.open(a.prompt_file, encoding="utf-8").read()
        check_prompt(prompt)
    else:
        die("launch needs --card <id> or --prompt-file <path>")
    busy = running_jobs()
    if busy and not a.dry_run:
        die(f"REFUSED: one job at a time per machine; running: {busy} (api_job.py status)")
<<<<<<< Updated upstream
    d = RUNS / a.slug
    cmd = build_cmd(a.model, a.max_usd, a.max_turns, a.engine, a.cwd or str(REPO), str(d), a.max_tokens)
    if a.engine == "claude":
        print("WARNING: engine=claude sends the claude-code beta, which this org's promotional credit refuses; with an OAuth login "
              "present the run bills the LOGIN'S SUBSCRIPTION, not the credit (measured 2026-11-07).", file=sys.stderr)
    if a.dry_run:
        print("DRY-RUN", " ".join(cmd))
        print(f"DRY-RUN prompt {len(prompt)} chars -> {d / 'prompt.txt'}; cwd {a.cwd or REPO}; max_tokens {a.max_tokens or 'default'}")
=======
    cmd = build_cmd(a.model, a.max_usd, a.max_turns)
    d = RUNS / a.slug
    if a.dry_run:
        print("DRY-RUN", " ".join(cmd))
        print(f"DRY-RUN prompt {len(prompt)} chars -> {d / 'prompt.txt'}; cwd {a.cwd or REPO}")
>>>>>>> Stashed changes
        return
    kf = key_file()
    if not kf.exists():
        die(f"key file missing: {kf}")
    d.mkdir(parents=True, exist_ok=True)
    io.open(d / "prompt.txt", "w", encoding="utf-8", newline="\n").write(prompt)
<<<<<<< Updated upstream
    meta = {"slug": a.slug, "card": a.card, "model": a.model, "max_usd": a.max_usd, "max_turns": a.max_turns, "max_tokens": a.max_tokens, "engine": a.engine,
=======
    meta = {"slug": a.slug, "card": a.card, "model": a.model, "max_usd": a.max_usd, "max_turns": a.max_turns,
>>>>>>> Stashed changes
            "started": dt.datetime.now(dt.timezone.utc).isoformat(), "host": os.environ.get("COMPUTERNAME", ""), "cwd": a.cwd or str(REPO)}
    io.open(d / "meta.json", "w", encoding="utf-8", newline="\n").write(json.dumps(meta, indent=1))
    out = io.open(d / "out.jsonl", "ab")
    err = io.open(d / "err.txt", "ab")
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "DETACHED_PROCESS", 0)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=out, stderr=err, env=child_env(dict(os.environ), kf),
                         cwd=a.cwd or str(REPO), creationflags=flags)
    p.stdin.write(prompt.encode("utf-8"))
    p.stdin.close()
<<<<<<< Updated upstream
    print(f"LAUNCHED {a.slug} pid {p.pid} model {a.model} cap ${a.max_usd} max_tokens {a.max_tokens or 'default'} -> {d / 'out.jsonl'}")
=======
    print(f"LAUNCHED {a.slug} pid {p.pid} model {a.model} cap ${a.max_usd} -> {d / 'out.jsonl'}")
>>>>>>> Stashed changes
    print(wait_line())


def status(a) -> None:
    dirs = [RUNS / a.slug] if a.slug else (sorted(RUNS.glob("*/")) if RUNS.exists() else [])
    for d in dirs:
        if not (d / "meta.json").exists() and not (d / "out.jsonl").exists():
            continue  # helper folders such as _prompts are not runs
        r = parse_result(d / "out.jsonl")
        meta = {}
        if (d / "meta.json").exists():
            try:
                meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            except ValueError:
                pass
        state = "done" if r["done"] else "running"
        cost = f"${r['cost']:.2f}" if r["cost"] is not None else "-"
<<<<<<< Updated upstream
        print(f"{d.name:40s} {state:8s} {meta.get('model', '?'):18s} cost {cost:7s} turns {r['turns'] or '-':>4} {r['minutes'] if r['minutes'] is not None else '-':>3} min {r['subtype'] or ''} max_tokens {meta.get('max_tokens') or 'default'} | {r['text'].splitlines()[0][:90] if r['text'] else ''}")
=======
        print(f"{d.name:40s} {state:8s} {meta.get('model', '?'):18s} cost {cost:7s} turns {r['turns'] or '-':>4} {r['minutes'] if r['minutes'] is not None else '-':>3} min {r['subtype'] or ''} | {r['text'].splitlines()[0][:90] if r['text'] else ''}")
>>>>>>> Stashed changes


def ledger_append(plan: Path, date: str, job: str, model: str, cost: float, turns, outcome: str) -> None:
    text = io.open(plan, encoding="utf-8").read()
    if "## Spent" not in text:
        die(f"{plan} has no '## Spent' table")
    row = f"| {date} | {job} | {MODEL_NAMES.get(model, model)} | {cost:.2f} | {turns if turns is not None else '-'} | {outcome} |"
    if not text.endswith("\n"):
        text += "\n"
    io.open(plan, "w", encoding="utf-8", newline="\n").write(text + row + "\n")


def ledger_total(plan: Path, date: str | None = None) -> float:
    total = 0.0
    seen = False
    for line in io.open(plan, encoding="utf-8"):
        if line.startswith("## Spent"):
            seen = True
            continue
        if seen and line.startswith("| 20"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4 and (date is None or cells[0] == date):
                try:
                    total += float(cells[3])
                except ValueError:
                    pass
    return total


def ledger(a) -> None:
    r = parse_result(RUNS / a.slug / "out.jsonl")
    if not r["done"]:
        die(f"{a.slug} has no result record yet")
    meta = json.loads((RUNS / a.slug / "meta.json").read_text(encoding="utf-8")) if (RUNS / a.slug / "meta.json").exists() else {}
    ledger_append(LEDGER, date=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"), job=a.slug, model=meta.get("model", "?"),
                  cost=float(r["cost"] or 0.0), turns=r["turns"], outcome=f"{a.outcome}; cap was {meta.get('max_usd', '?')}")
    print(f"LEDGER {a.slug} ${float(r['cost'] or 0):.2f} -> {LEDGER.name}; total today ${ledger_total(LEDGER, dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')):.2f}")


def total(a) -> None:
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    print(f"TOTAL today {today} ${ledger_total(LEDGER, today):.2f} | all ${ledger_total(LEDGER):.2f} (ledger {LEDGER.name})")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("launch")
    l.add_argument("slug")
    l.add_argument("--card")
    l.add_argument("--prompt-file")
    l.add_argument("--model", default="claude-sonnet-5-5", choices=sorted(MODEL_NAMES))
    l.add_argument("--max-usd", type=float, required=True)
    l.add_argument("--max-turns", type=int, default=200)
<<<<<<< Updated upstream
    l.add_argument("--max-tokens", type=int, default=None,
                   help="cap of one reply, passed to api_agent.py (default: its per-model default, 32000; one retry at double on a cut-off)")
    l.add_argument("--cwd", help="run from this checkout (default: this repo)")
    l.add_argument("--engine", default="api", choices=("api", "claude"),
                   help="api = raw Messages API via api_agent.py (bills the credit); claude = `claude -p` (bills the subscription)")
=======
    l.add_argument("--cwd", help="run from this checkout (default: this repo)")
>>>>>>> Stashed changes
    l.add_argument("--dry-run", action="store_true")
    l.set_defaults(fn=launch)
    s = sub.add_parser("status")
    s.add_argument("slug", nargs="?")
    s.set_defaults(fn=status)
    g = sub.add_parser("ledger")
    g.add_argument("slug")
    g.add_argument("--outcome", required=True)
    g.set_defaults(fn=ledger)
    t = sub.add_parser("total")
    t.set_defaults(fn=total)
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # Windows cp1251 console vs job output
    a.fn(a)


if __name__ == "__main__":
    main()
