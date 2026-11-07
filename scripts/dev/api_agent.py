"""Headless Builder on the Claude API credit through the raw Messages API (no Claude Code beta). Stdlib only.

Why this exists (measured 2026-11-07, Lead C): the org's promotional credit pays plain /v1/messages calls, but any request that
carries the `claude-code-20250219` beta (every `claude -p` run) is refused with "credit balance is too low" (purchased balance
$0, no payment method). So `claude -p` never billed the credit: with the login's OAuth present it fell back to the subscription.
This runner speaks the plain API with four tools (read_file, write_file, list_dir, run_cmd) inside one working directory.

  python scripts/dev/api_agent.py --model claude-sonnet-5-5 --max-usd 2 --max-turns 60 --cwd <worktree> --out <dir> < prompt.txt
Writes <out>/out.jsonl: one JSON per API turn and a final {"type":"result", "total_cost_usd", "num_turns", "duration_ms",
"result", "subtype"} record, the same shape api_job.py reads. Key: env ANTHROPIC_API_KEY, else env MTS_API_KEY_FILE, else
F:/ClaudePlaform/key.txt; never printed. A tool call on a secret-like path is refused. Cost = tokens x PRICE_PER_MTOK (OURS,
list price; the console is the bill). Stops at --max-usd, --max-turns, or when the model answers without a tool call.
"""
from __future__ import annotations
import argparse
import datetime as dt
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
API = "https://api.anthropic.com/v1/messages"
PRICE_PER_MTOK = {"claude-haiku-5-5": (1.0, 5.0), "claude-sonnet-5-5": (3.0, 15.0), "claude-opus-5-5": (5.0, 25.0)}  # OURS
CACHE_READ_FACTOR = 0.1  # cached input is billed at a tenth (OURS placeholder, list price)
BLOCKED = (".secrets", ".env", ".pem", ".ovpn", "key.txt", "cookies_", "background.js", "config.json", "api_key", "apikey")
TOOLS = [
    {"name": "read_file", "description": "Read a UTF-8 text file (path relative to the working directory). Returns at most max_chars.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "max_chars": {"type": "integer", "default": 20000}},
                      "required": ["path"]}},
    {"name": "write_file", "description": "Write a UTF-8 text file with LF newlines (creates parent folders). Overwrites.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "list_dir", "description": "List a directory (names, dirs end with /).",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string", "default": "."}}}},
    {"name": "run_cmd", "description": "Run a shell command in the working directory (timeout seconds, default 300). Returns rc, stdout, stderr (each capped).",
     "input_schema": {"type": "object", "properties": {"cmd": {"type": "string"}, "timeout": {"type": "integer", "default": 300}}, "required": ["cmd"]}},
]
SYSTEM = ("You are a headless Builder working in one checkout with four tools. Finish the task, then answer in plain text with no tool "
          "call: a `Result:` line first, then what you shipped or wrote, then `Noticed:`. Never ask questions; take the conservative "
          "default and say so. Never read secrets (.secrets, .env, keys); never run destructive git (reset, rebase, force-push); "
          "never touch the live tree, HALT or orders.")


def get_key() -> str:
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    kf = Path(os.environ.get("MTS_API_KEY_FILE", "F:/ClaudePlaform/key.txt"))
    if not kf.exists():
        raise SystemExit(f"key file missing: {kf}")
    return "".join(io.open(kf, encoding="utf-8").read().split())


def blocked(text: str) -> bool:
    low = text.lower().replace("\\", "/")
    return any(b in low for b in BLOCKED)


def run_tool(name: str, inp: dict, cwd: Path) -> str:
    try:
        if name in ("read_file", "write_file", "list_dir"):
            rel = str(inp.get("path", "."))
            if blocked(rel):
                return f"REFUSED: secret-like path {rel}"
            p = (cwd / rel).resolve()
            if name == "read_file":
                n = int(inp.get("max_chars", 20000) or 20000)
                text = io.open(p, encoding="utf-8", errors="replace").read()
                return text[:n] + (f"\n...[truncated, {len(text)} chars total]" if len(text) > n else "")
            if name == "write_file":
                p.parent.mkdir(parents=True, exist_ok=True)
                io.open(p, "w", encoding="utf-8", newline="\n").write(str(inp.get("content", "")))
                return f"wrote {len(str(inp.get('content', '')))} chars to {rel}"
            return "\n".join(sorted(e.name + ("/" if e.is_dir() else "") for e in p.iterdir()))[:20000]
        if name == "run_cmd":
            cmd = str(inp.get("cmd", ""))
            if blocked(cmd):
                return "REFUSED: command names a secret-like path"
            t = min(int(inp.get("timeout", 300) or 300), 900)
            env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
            env["PYTHONIOENCODING"] = "utf-8"
            r = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=t, env=env, stdin=subprocess.DEVNULL)
            return f"rc={r.returncode}\nstdout:\n{r.stdout[-12000:]}\nstderr:\n{r.stderr[-4000:]}"
        return f"unknown tool {name}"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:  # the model gets the error text and continues
        return f"ERROR: {type(e).__name__}: {str(e)[:500]}"


def call_api(key: str, body: dict, retries: int = 4) -> dict:
    data = json.dumps(body).encode()
    for attempt in range(retries + 1):
        req = urllib.request.Request(API, data=data, headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                                               "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:400]
            if e.code in (429, 500, 502, 503, 529) and attempt < retries:
                time.sleep(10 * (attempt + 1))
                continue
            raise SystemExit(f"API HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries:
                time.sleep(10 * (attempt + 1))
                continue
            raise SystemExit(f"API unreachable: {e}")
    raise SystemExit("API retries exhausted")


def usd(model: str, usage: dict) -> float:
    pin, pout = PRICE_PER_MTOK.get(model, max(PRICE_PER_MTOK.values()))
    inp = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) * 1.25
    return (inp * pin + usage.get("cache_read_input_tokens", 0) * pin * CACHE_READ_FACTOR + usage.get("output_tokens", 0) * pout) / 1e6


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="claude-sonnet-5-5", choices=sorted(PRICE_PER_MTOK))
    ap.add_argument("--max-usd", type=float, required=True)
    ap.add_argument("--max-turns", type=int, default=100)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--out", required=True, help="folder for out.jsonl")
    ap.add_argument("--prompt-file", help="prompt text (default: stdin)")
    a = ap.parse_args(argv)
    cwd = Path(a.cwd).resolve()
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt = io.open(a.prompt_file, encoding="utf-8").read() if a.prompt_file else sys.stdin.read()
    if not prompt.strip():
        raise SystemExit("empty prompt")
    key = get_key()
    log = io.open(out_dir / "out.jsonl", "a", encoding="utf-8", newline="\n")
    system = [{"type": "text", "text": SYSTEM + f"\nWorking directory: {cwd}", "cache_control": {"type": "ephemeral"}}]
    messages = [{"role": "user", "content": prompt}]
    cost = 0.0
    t0 = time.time()
    turns = 0
    final = ""
    subtype = "success"
    while True:
        if turns >= a.max_turns:
            subtype, final = "error_max_turns", final or "stopped at the turn cap"
            break
        if cost >= a.max_usd:
            subtype, final = "error_max_budget_usd", final or f"stopped at the USD cap ({cost:.2f})"
            break
        body = {"model": a.model, "max_tokens": a.max_tokens, "system": system, "tools": TOOLS, "messages": messages}
        for m in messages:  # one moving cache breakpoint on the last user block (system holds the other)
            if isinstance(m["content"], list):
                for b in m["content"]:
                    b.pop("cache_control", None)
        last = messages[-1]
        if not isinstance(last["content"], list):
            last["content"] = [{"type": "text", "text": last["content"]}]
        last["content"][-1]["cache_control"] = {"type": "ephemeral"}
        resp = call_api(key, body)
        turns += 1
        cost += usd(a.model, resp.get("usage", {}))
        log.write(json.dumps({"type": "assistant", "turn": turns, "stop_reason": resp.get("stop_reason"), "usage": resp.get("usage"),
                              "cost_so_far": round(cost, 5), "content": resp.get("content")}) + "\n")
        log.flush()
        content = resp.get("content", [])
        messages.append({"role": "assistant", "content": content})
        tool_uses = [b for b in content if b.get("type") == "tool_use"]
        texts = [b.get("text", "") for b in content if b.get("type") == "text"]
        if texts:
            final = "\n".join(texts)
        if not tool_uses or resp.get("stop_reason") not in ("tool_use",):
            if resp.get("stop_reason") == "max_tokens":
                subtype = "error_max_tokens"
            break
        results = []
        for tu in tool_uses:
            res = run_tool(tu["name"], tu.get("input", {}) or {}, cwd)
            log.write(json.dumps({"type": "tool", "turn": turns, "name": tu["name"], "input": tu.get("input"), "result": res[:2000]}) + "\n")
            results.append({"type": "tool_result", "tool_use_id": tu["id"], "content": res})
        messages.append({"role": "user", "content": results})
    rec = {"type": "result", "subtype": subtype, "is_error": subtype != "success", "total_cost_usd": round(cost, 5), "num_turns": turns,
           "duration_ms": int((time.time() - t0) * 1000), "model": a.model, "result": final[:4000], "engine": "api_agent",
           "ended": dt.datetime.now(dt.timezone.utc).isoformat()}
    log.write(json.dumps(rec) + "\n")
    log.close()
    print(json.dumps({k: rec[k] for k in ("subtype", "total_cost_usd", "num_turns", "duration_ms")}))
    print(final[:1500])
    return 0 if subtype == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
