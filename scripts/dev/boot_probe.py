"""boot_probe.py - one BOOT signal per session and per subagent: what it loaded first, and whether its role banner is genuine.

Operator 2026-10-22: "is the initial token load correct here? this is something that you need to monitor for each
session/sub-session and agent". turn_meter.py's PostToolUse hook calls maybe_spawn() on every tool call; the first call of a
session (or of one subagent) leaves a marker and starts `boot_probe.py report` detached, so the hook itself only checks a
file. The report reads the transcript head and sends one signal (mts_signal.py, kind note):
  BOOT <role|-> banner=<ok|STALE|FAIL ...|none|late|n/a> first=<N>k <model> [agent:<type>] [HIGH]
first = input + cache read + cache write of the first assistant message = everything loaded before the first reply
(system prompt, tools, CLAUDE.md, hook text, the first prompt). HIGH above FIRST_HIGH (CONTEXT_BASELINE.md: a first-turn
median above 60k means a connector or skill switch is still on). banner: role_loader.verify() of the first reply's
`ROLE LOADED` line against the role file and this session's injection record; `none` = a role was injected and the first
reply has no banner; late = the first reply is older than 15 min (a session already running when the probe arrived); n/a = no
role injected (or a subagent).
  python scripts/dev/boot_probe.py report --transcript <path> --sid <id> [--agent <type>] [--cwd <dir>] [--dry]
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FIRST_HIGH = 60_000
LATE_S = 15 * 60            # first reply older than this when the probe runs: banner=late (not judged)
HEAD_MAX = 4 << 20          # transcript bytes read from the start (the first reply is near the top)


def home():
    return Path(os.environ.get("MTS_BOOT_PROBE_HOME") or Path(tempfile.gettempdir()) / "mts_boot_probe")


def marker(payload):
    key = "%s__%s" % (payload.get("session_id") or "nosession", payload.get("agent_id") or "main")
    return home() / (re.sub(r"[^A-Za-z0-9_.-]", "_", key) + ".done")


def real_transcript(path):
    """A Claude Code transcript (an existing .jsonl outside the temp dir): tests that fire the hook with tmp transcripts
    never start a report, so no test sends a signal."""
    try:
        p = Path(path).resolve()
        return p.suffix == ".jsonl" and p.is_file() and Path(tempfile.gettempdir()).resolve() not in p.parents
    except (OSError, ValueError, TypeError):
        return False


def maybe_spawn(payload):
    """Hook side: on the first PostToolUse of this session/subagent, mark it and start the report. Never raises."""
    if os.environ.get("MTS_BOOT_PROBE", "").lower() == "off" or payload.get("hook_event_name") != "PostToolUse":
        return False
    if not payload.get("session_id") or not real_transcript(payload.get("transcript_path")):
        return False
    m = marker(payload)
    try:
        if m.exists():
            return False
        m.parent.mkdir(parents=True, exist_ok=True)
        m.write_text("", encoding="utf-8")
    except OSError:
        return False
    args = [sys.executable, str(Path(__file__).resolve()), "report", "--transcript", str(payload["transcript_path"]),
            "--sid", str(payload["session_id"]), "--cwd", str(payload.get("cwd") or "")]
    if payload.get("agent_id"):
        args += ["--agent", str(payload.get("agent_type") or "agent")]
    try:
        flags = 0x08000000 if os.name == "nt" else 0      # CREATE_NO_WINDOW (mts_signal.spawn_send: no git window flashing)
        subprocess.Popen(args, cwd=payload.get("cwd") or None, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, creationflags=flags, close_fds=True)
    except OSError:
        return False
    return True


def first_turn(path):
    """(model, first-turn tokens, text of the first reply before its first tool call, its ISO timestamp).
    ("", 0, "", "") when unreadable."""
    model, tokens, text, mid, at = "", 0, [], None, ""
    try:
        with open(path, "rb") as f:
            data = f.read(HEAD_MAX)
    except OSError:
        return "", 0, "", ""
    for raw in data.split(b"\n"):
        if b'"assistant"' not in raw:
            continue
        try:
            row = json.loads(raw)
        except ValueError:
            continue
        msg = row.get("message") or {}
        if row.get("type") != "assistant" or str(msg.get("model") or "").startswith("<"):
            continue
        if mid is None:
            mid, at = msg.get("id"), str(row.get("timestamp") or "")
        if msg.get("id") != mid:
            break
        u = msg.get("usage") or {}
        if u and not tokens:
            model = str(msg.get("model") or "").lower()
            tokens = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        content = msg.get("content")
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content or []
        stop = False
        for b in blocks:
            if isinstance(b, dict) and b.get("type") == "text":
                text.append(str(b.get("text") or ""))
            elif isinstance(b, dict) and b.get("type") == "tool_use":
                stop = True
        if stop:
            break
    return model, tokens, "\n".join(text), at


def banner_status(text, sid, agent):
    """(role name or '-', status) for the first reply."""
    if agent:
        return "-", "n/a"
    try:
        import role_loader
        roles = role_loader.injected(sid)
    except Exception:
        return "-", "n/a"
    if not roles:
        return "-", "n/a"
    name = str(roles[-1])
    if "ROLE LOADED" not in text and "ROLE NOT LOADED" not in text:
        return name, "none"
    lines = []
    code = role_loader.verify(text, role=name, sid=sid, out=lines.append)
    if code == 0:
        return name, "ok"
    if code == 2:
        return name, "STALE"
    why = " ".join((lines[0] if lines else "").split())
    return name, "FAIL " + re.sub(r"^FAIL\s*", "", why)[:90]


def late(at, now=None):
    """The first reply is older than LATE_S: the session ran before this probe reached it, and role_loader's record may have
    moved on since (a compaction re-injects the newer file), so its banner is not judged."""
    try:
        t = datetime.fromisoformat(at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return False
    return ((now or datetime.now(timezone.utc)) - t).total_seconds() > LATE_S


def report_line(path, sid, agent="", now=None):
    model, tokens, text, at = first_turn(path)
    name, status = banner_status(text, sid, agent)
    if late(at, now) and status not in ("n/a",):
        status = "late"
    parts = ["BOOT", name, "banner=" + status, "first=%dk" % round(tokens / 1000) if tokens else "first=?", model or "model?"]
    if agent:
        parts.append("agent:" + agent)
    if tokens > FIRST_HIGH:
        parts.append("HIGH")
    return " ".join(parts)


def main(argv):
    if not argv or argv[0] != "report":
        print(__doc__)
        return 2
    opt = {}
    i = 1
    while i < len(argv):
        if argv[i] == "--dry":
            opt["dry"] = True
            i += 1
        else:
            opt[argv[i].lstrip("-")] = argv[i + 1] if i + 1 < len(argv) else ""
            i += 2
    line = report_line(opt.get("transcript", ""), opt.get("sid", ""), opt.get("agent", ""))
    if opt.get("dry"):
        print(line)
        return 0
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import mts_signal
    mts_signal.send(line, kind="note", cwd=opt.get("cwd") or None, sid=opt.get("sid", ""))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main(sys.argv[1:]))
