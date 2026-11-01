"""bg_watch.py - background tasks that run past their wall-time cap, and aged raw cards (bg-process-audit 2026-10-28).

  python scripts/dev/bg_watch.py report        STALLED-BG / RAW-AGED lines (nothing printed = nothing over its cap)
  python scripts/dev/bg_watch.py until --file F --pattern RE [--timeout S] [--interval S]
                                               a poll loop WITH a deadline: exit 0 when RE appears in F, 124 on timeout
                                               (use it instead of `until grep ...; do sleep 5; done`, which has none)

Why: in 7 days 105 background tasks ran over 30 min (142 h); the worst were poll loops with no deadline (`until grep ...;
do sleep 5; done`: 18 h, 6.6 h, 20 h) and NUC ssh probes with no output (2 h). No session saw them: a background task's
only signal is its completion notice, which a hung task never sends. This reads the Claude Code transcripts of the
sessions active in the last `active_min` minutes, finds background tasks (Bash/PowerShell run_in_background or
auto-backgrounded, Agent) with no completion notice and no TaskStop, and prints one line per task over its cap.
supervisor.py plan prints the same lines every wake, so a coordinator sees them without asking.

Caps per kind (minutes, OURS; operator 2026-10-28 targets probe 2, NUC verb 5, worker 45; ship 20 = 10 gate + the
10-minute CI wait cap CI_WAIT_S in sync.py; a watcher gets its own --timeout + 5).
Read-only: it never stops a task (only the owning session can: TaskStop <id>).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CAPS = {"probe": 2, "nuc": 5, "poll-loop": 10, "tests": 20, "ship": 20, "gemini": 45, "worker": 45, "command": 10}
ID_RES = (re.compile(r"background with ID: ([a-z0-9]+)"), re.compile(r"moved to the background \(ID: ([a-z0-9]+)\)"),
          re.compile(r"agentId: ([a-z0-9]+)"))
OUT_RE = re.compile(r"Output is being written to: (\S+?\.output)")
NOTIF_RE = re.compile(r"<task-id>([a-z0-9]+)</task-id>")
PROBE_RE = re.compile(r"^\s*(cat|ls|grep|head|tail|git (log|status|show|diff|cherry)|wc|find|date)\b")


POLL_RE = re.compile(r"\b(until|while)\b.*(\bsleep\b|\bgrep\b|\btail\s+-[a-zA-Z]*f)")


def projects_root() -> Path:
    return Path(os.environ.get("MTS_BG_WATCH_ROOT") or (Path.home() / ".claude" / "projects"))


def kind_of(tool: str, what: str) -> tuple[str, int]:
    """(kind, cap minutes) for one background task."""
    w = what or ""
    if tool in ("Agent", "Task"):
        return "worker", CAPS["worker"]
    m = re.search(r"supervisor\.py wait\b.*?--timeout\s+(\d+)\s*(m|s|h)?", w)
    if m:
        n = int(m.group(1))
        n = n // 60 if m.group(2) == "s" else n * 60 if m.group(2) == "h" else n
        return "watcher", n + 5
    if "supervisor.py wait" in w:
        return "watcher", 55       # default --timeout 3000 s + 5
    if re.search(r"nuc_gate|nuc_lab\.py|nuc_wake\.py|\bssh\b", w):
        return "nuc", CAPS["nuc"]
    if "gemini_queue.py" in w:
        return "gemini", CAPS["gemini"]
    if "sync.py ship" in w:
        return "ship", CAPS["ship"]
    if POLL_RE.search(w):
        return "poll-loop", CAPS["poll-loop"]
    if "run_all_tests.py" in w or "pytest" in w:
        return "tests", CAPS["tests"]
    if PROBE_RE.search(w):
        return "probe", CAPS["probe"]
    return "command", CAPS["command"]


def _ts(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def _text(c) -> str:
    if isinstance(c, str):
        return c
    out = []
    for b in c or []:
        if isinstance(b, dict):
            if b.get("type") == "text":
                out.append(b.get("text", ""))
            elif b.get("type") == "tool_result":
                out.append(_text(b.get("content")))
    return "\n".join(out)


def _notified(d: dict) -> list[str]:
    """Task ids from a completion notice. It arrives as a user message or as a queued_command attachment; a tool result
    that merely quotes one (a grep of a transcript) does not count."""
    texts = []
    a = d.get("attachment")
    if isinstance(a, dict) and isinstance(a.get("prompt"), str):
        texts.append(a["prompt"])
    c = (d.get("message") or {}).get("content")
    if isinstance(c, str):
        texts.append(c)
    elif isinstance(c, list):
        texts += [b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"]
    return [i for t in texts if "<task-notification>" in t for i in NOTIF_RE.findall(t)]


def open_tasks(path: Path) -> list[dict]:
    """Background tasks started in one transcript that have no completion notice and no TaskStop yet."""
    uses, tasks, done = {}, {}, set()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            t = d.get("timestamp")
            if not t:
                continue
            c = (d.get("message") or {}).get("content")
            if d.get("type") == "assistant" and isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        inp = b.get("input") or {}
                        uses[b.get("id")] = (b.get("name"), inp, _ts(t))
                        if b.get("name") == "TaskStop":
                            done.add(inp.get("task_id") or inp.get("shell_id"))
            else:
                done.update(_notified(d))
            if d.get("type") == "user":
                if isinstance(c, list):
                    for b in c:
                        if not (isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in uses):
                            continue
                        name, inp, t0 = uses[b["tool_use_id"]]
                        if name not in ("Bash", "PowerShell", "Agent", "Task"):
                            continue
                        txt = _text(b.get("content"))
                        for rx in ID_RES:
                            m = rx.search(txt)
                            if m:
                                what = inp.get("command") or inp.get("description") or ""
                                if name in ("Agent", "Task"):
                                    what = "Agent " + (inp.get("description") or "")
                                o = OUT_RE.search(txt)
                                tasks.setdefault(m.group(1), {"id": m.group(1), "tool": name, "start": t0,
                                                              "what": " ".join(str(what).split()), "out": o.group(1) if o else ""})
                                break
    return [v for k, v in tasks.items() if k not in done]


def stalled(root: Path | None = None, now: float | None = None, active_min: int = 180) -> list[dict]:
    """Open background tasks over their cap, in sessions whose transcript moved in the last `active_min` minutes."""
    root = root or projects_root()
    now = now or time.time()
    rows = []
    if not root.is_dir():
        return rows
    for f in root.rglob("*.jsonl"):
        try:
            if now - f.stat().st_mtime > active_min * 60:
                continue
            found = open_tasks(f)
        except OSError:
            continue
        for v in found:
            kind, cap = kind_of(v["tool"], v["what"])
            age = (now - v["start"]) / 60
            if age <= cap:
                continue
            silent = None
            if v["out"]:
                try:
                    silent = (now - Path(v["out"]).stat().st_mtime) / 60
                except OSError:
                    pass
            rows.append({**v, "kind": kind, "cap": cap, "age": age, "silent": silent, "session": f.stem[:8]})
    return sorted(rows, key=lambda r: -r["age"])


def raw_aged(repo: Path, now: float | None = None, hours: int = 12) -> list[tuple[str, float]]:
    """IMPORTANT/CRUCIAL cards still `raw` after `hours`: a filed bug nobody refined (coordinator-sits-idle sat raw, unseen)."""
    now = now or time.time()
    out = []
    for p in sorted((Path(repo) / "MyTradingSys" / "system" / "tasks").glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("state") != "raw" or str(d.get("weight", "")).upper() not in ("IMPORTANT", "CRUCIAL"):
                continue
            h = (now - _ts(d["created"])) / 3600
        except (OSError, ValueError, KeyError, TypeError):
            continue
        if h >= hours:
            out.append((d["id"], h))
    return sorted(out, key=lambda x: -x[1])


DEADLINE_RE = re.compile(r"bg_watch\.py until|\btimeout\b|\$SECONDS|\bdate \+%s|\bfor\s+\w+\s+in\b|\bseq\b|-lt\b|-ge\b")


def unbounded_loop(what: str) -> bool:
    """True for an until/while-sleep loop with no deadline of its own: it ends only when its condition comes true."""
    return bool(POLL_RE.search(what or "")) and not DEADLINE_RE.search(what or "")


def wait_until(path, pattern, timeout_s=600.0, interval_s=5.0, sleep=time.sleep, now_fn=time.monotonic) -> int:
    """Poll `path` for a regex line match: 0 on match, 124 (like timeout(1)) once timeout_s has passed. A missing file is not a match."""
    rx = re.compile(pattern)
    t0 = now_fn()
    while True:
        try:
            if rx.search(Path(path).read_text(encoding="utf-8", errors="replace")):
                return 0
        except OSError:
            pass
        if now_fn() - t0 >= timeout_s:
            return 124
        sleep(interval_s)


def report_lines(repo: Path, root: Path | None = None, now: float | None = None) -> list[str]:
    lines = []
    for r in stalled(root, now):
        quiet = f", no output {r['silent']:.0f}m" if r["silent"] is not None and r["silent"] >= 5 else ""
        bare = r["kind"] == "poll-loop" and unbounded_loop(r["what"])
        lines.append(f"STALLED-BG {r['kind']} {r['id']} {r['age']:.0f}m > cap {r['cap']}m{quiet} (session {r['session']}): "
                     f"{r['what'][:70]} -> owner: TaskStop {r['id']}, say why in one line"
                     + (" (bare poll loop, no deadline: run TaskStop " + r["id"] + " now; the only allowed poll is "
                        "`bg_watch.py until --file F --pattern RE --timeout S`)" if bare else ""))
    raw = raw_aged(repo, now)
    if raw:
        top = ", ".join(f"{i} {h:.0f}h" for i, h in raw[:3])
        lines.append(f"RAW-AGED {len(raw)} IMPORTANT/CRUCIAL card(s) still raw > 12h ({top}): refine or drop one this wake")
    return lines


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["until"]:
        opts = {k: v for k, v in zip(argv[1::2], argv[2::2])}
        if not {"--file", "--pattern"} <= set(opts) or set(opts) - {"--file", "--pattern", "--timeout", "--interval"}:
            print(__doc__)
            return 2
        rc = wait_until(opts["--file"], opts["--pattern"], float(opts.get("--timeout", 600)), float(opts.get("--interval", 5)))
        if rc:
            print(f"bg_watch until: TIMEOUT after {opts.get('--timeout', 600)} s, no match for {opts['--pattern']!r} in {opts['--file']}")
        return rc
    if argv[:1] != ["report"]:
        print(__doc__)
        return 2
    for line in report_lines(Path(__file__).resolve().parents[2]):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
