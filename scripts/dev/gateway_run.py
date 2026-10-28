"""gateway_run.py - run one headless Opus card on the API gateway, in the background, on the station that holds the key.

Why: the operator wants the gateway key used from the background while the app runs a subscription login (GATEWAY_NUC.md).
How: the key and base URL never leave this machine and never reach a prompt, argument, log or the repo:
  key  = ~/.mts_gateway/key (one line, user-only file, outside the repo) if present, else the operator's .reg file;
  base = inferenceGatewayBaseUrl in ~/Documents/claude-gateway/Claude-good.reg.
The child `claude -p` gets them as env only (subscription OAuth vars dropped), runs in its own gw-<card> worktree
marked .gateway_owner, and every output file is redacted. `start` registers ONE one-shot task that deletes itself
when the child exits (SCHEDULING_POLICY.md 4b2 pattern), so the run survives the ssh disconnect.
Usage (on the key station):
  python scripts/dev/gateway_run.py probe [--auth api-key|bearer]
  python scripts/dev/gateway_run.py start --card <id> --run <O1|O2|O3>
  python scripts/dev/gateway_run.py status
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
KEY_FILE = HOME / ".mts_gateway" / "key"
REG_FILE = HOME / "Documents" / "claude-gateway" / "Claude-good.reg"
RUNS = Path("F:/MTS/gateway_runs")
MODEL = "claude-opus-5-5"
DROP = re.compile(r"^(ANTHROPIC_|CLAUDE_CODE_OAUTH|CLAUDE_CODE_USE_)")

CHILD_PROMPT = (
    "You run on the MTS gateway, headless. Public tracked files only (GATEWAY_NUC.md rules 1-7): never read .secrets, "
    ".env, keys, ~/.mts_gateway, runtime data, the live tree or F:/ backups, and never print environment variables. "
    "You are already in your own worktree; skip sync.py start. Run MyTradingSys/system/handover/OPUS_RUNS.md {run} in full. "
    "Skip get_usage: write 'gateway: no meter'. Commit body adds 'Model: {model} via gateway'. "
    "Never ask; take the conservative default and log DECISION (OURS)."
)


def read_reg(path: Path) -> dict:
    raw = path.read_bytes()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    out = {}
    for line in text.splitlines():
        m = re.match(r'^"([^"]+)"="((?:[^"\\]|\\.)*)"', line.strip())
        if m:
            out[m.group(1)] = m.group(2).replace('\\"', '"').replace("\\\\", "\\")
    return out


def load_secret(key_file: Path = KEY_FILE, reg_file: Path = REG_FILE) -> tuple:
    reg = read_reg(reg_file) if reg_file.exists() else {}
    base = reg.get("inferenceGatewayBaseUrl", "")
    key = key_file.read_text(encoding="utf-8").strip() if key_file.exists() else reg.get("inferenceGatewayApiKey", "")
    if not base or not key:
        raise SystemExit("gateway_run: no base URL or key on this machine (names checked only)")
    return base, key


def child_env(base: str, key: str, auth: str, environ=None) -> dict:
    env = {k: v for k, v in (environ if environ is not None else os.environ).items() if not DROP.match(k)}
    env["ANTHROPIC_BASE_URL"] = base
    env["ANTHROPIC_AUTH_TOKEN" if auth == "bearer" else "ANTHROPIC_API_KEY"] = key
    env["MTS_GATEWAY"] = "1"
    return env


def redact(text: str, secret: str) -> str:
    return text.replace(secret, "<redacted>") if secret else text


def summary(stdout: str, key: str) -> dict:
    try:
        d = json.loads(stdout)
    except ValueError:
        return {"is_error": True, "result": redact(stdout[-400:], key)}
    res = str(d.get("result", ""))
    # the CLI reports is_error false on an auth failure; the text is the only signal
    bad = bool(d.get("is_error")) or bool(re.search(r"Invalid API key|API Error|authentication_error|401|403", res))
    return {"is_error": bad, "num_turns": d.get("num_turns"),
            "models": sorted((d.get("modelUsage") or {}).keys()), "result": redact(str(d.get("result", ""))[-400:], key)}


def claude_exe() -> str:
    p = HOME / ".local" / "bin" / "claude.exe"
    return str(p) if p.exists() else "claude"


def probe(auth: str) -> int:
    base, key = load_secret()
    r = subprocess.run([claude_exe(), "-p", "Reply with the single word OK.", "--model", MODEL, "--output-format", "json"],
                       env=child_env(base, key, auth), capture_output=True, text=True, timeout=180)
    s = summary(r.stdout, key)
    s["auth"], s["exit"], s["stderr"] = auth, r.returncode, redact(r.stderr[-300:], key)
    print(json.dumps(s))
    return 0 if r.returncode == 0 and not s["is_error"] else 1


def repo_root() -> Path:
    return Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                               capture_output=True, text=True, check=True).stdout.strip()).parent


def task_name(card: str) -> str:
    return "MTS-GW-" + re.sub(r"[^A-Za-z0-9-]", "-", card)[:40]


def start(card: str, run: str, auth: str) -> int:
    load_secret()  # fail early, names only
    repo = repo_root()
    wt = repo / ".claude" / "worktrees" / f"gw-{card}"
    subprocess.run(["git", "-C", str(repo), "fetch", "-q", "origin", "fast-track"], check=True)
    if not wt.exists():
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", f"gateway/{card}", "origin/fast-track"], check=True)
    (wt / ".gateway_owner").write_text(f"gateway_run {card}\n", encoding="utf-8", newline="\n")
    d = RUNS / card
    d.mkdir(parents=True, exist_ok=True)
    for f in ("done", "out.json", "err.log", "summary.json"):
        (d / f).unlink(missing_ok=True)
    me = wt / "scripts" / "dev" / "gateway_run.py"
    tr = f'"{sys.executable}" "{me}" child --card {card} --run {run} --auth {auth} --cwd "{wt}"'
    tn = task_name(card)
    subprocess.run(["schtasks", "/Create", "/TN", tn, "/SC", "ONCE", "/ST", "00:00", "/TR", tr, "/IT", "/F"],
                   check=True, capture_output=True)
    subprocess.run(["schtasks", "/Run", "/TN", tn], check=True, capture_output=True)
    print(f"started {card} ({run}) task={tn} tree={wt} logs={d}")
    return 0


def child(card: str, run: str, auth: str, cwd: str) -> int:
    d = RUNS / card
    rc, key = 1, ""
    try:
        base, key = load_secret()
        r = subprocess.run([claude_exe(), "-p", CHILD_PROMPT.format(run=run, model=MODEL), "--model", MODEL,
                            "--permission-mode", "bypassPermissions", "--output-format", "json"],
                           cwd=cwd, env=child_env(base, key, auth), capture_output=True, text=True, timeout=6 * 3600)
        rc = r.returncode
        (d / "out.json").write_text(redact(r.stdout, key), encoding="utf-8", newline="\n")
        (d / "err.log").write_text(redact(r.stderr, key), encoding="utf-8", newline="\n")
        (d / "summary.json").write_text(json.dumps(summary(r.stdout, key)), encoding="utf-8", newline="\n")
    except Exception as e:  # the task must still delete itself
        (d / "err.log").write_text(redact(repr(e), key), encoding="utf-8", newline="\n")
    finally:
        (d / "done").write_text(f"exit={rc}\n", encoding="utf-8", newline="\n")
        subprocess.run(["schtasks", "/Delete", "/TN", task_name(card), "/F"], capture_output=True)
    return rc


def status() -> int:
    for d in sorted(RUNS.glob("*")) if RUNS.exists() else []:
        done = (d / "done").read_text().strip() if (d / "done").exists() else "running"
        s = (d / "summary.json").read_text() if (d / "summary.json").exists() else ""
        print(f"{d.name}: {done} {s[:600]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probe", "start", "child", "status"])
    ap.add_argument("--card")
    ap.add_argument("--run")
    ap.add_argument("--cwd")
    ap.add_argument("--auth", choices=["api-key", "bearer"], default="api-key")
    a = ap.parse_args()
    if a.cmd == "probe":
        return probe(a.auth)
    if a.cmd == "start":
        return start(a.card, a.run, a.auth)
    if a.cmd == "child":
        return child(a.card, a.run, a.auth, a.cwd)
    return status()


if __name__ == "__main__":
    sys.exit(main())
