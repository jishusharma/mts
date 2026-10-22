"""Safety guard: the CLAUDE.md "Hard rules" as a PreToolUse hook (operator 2026-10-22: rules that are only instructions are not a fix).

Registered (by the operator, in .claude/settings.json) as `python scripts/dev/safety_guard.py hook` on Read, Grep, Glob, Edit, Write,
NotebookEdit, Bash and PowerShell. It prints a deny JSON ({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision":
"deny", "permissionDecisionReason": "safety_guard: ..."}}) or nothing. Subagents follow the same rules (agent_id is NOT a bypass).
Fail closed: Edit/Write/NotebookEdit/Bash/PowerShell input that cannot be parsed is denied ("unparsable"); any other tool_name passes.

Rules (source: CLAUDE.md, section "Hard rules" unless noted):
 1 SECRETS  ("never read `.secrets/`, `.env`, keys", Hard rules, Testnet line): any path argument (file_path, path, pattern, glob,
            notebook_path) or Bash/PowerShell text naming a `.secrets` directory, `.env` / `.env.*` (not .env.example/.sample/.template),
            `*.pem`, `*.key`, `id_rsa`. Editing a `.gitignore` is allowed, and so is `git check-ignore`.
 2 GIT      ("Never commit to master, never rebase/reset/force-push"; "Others' uncommitted files: don't stash, clean, revert"; environment
            stash note): git push with -f/--force*/+refspec; git reset --hard; git rebase (not --abort); git clean -f; bare git stash / pop /
            save (only `stash push -u -m <tag>`, list, show, apply, drop pass); git commit or push naming master; git checkout -- . /
            git checkout . / git restore . ; git branch -D.
 3 LIVE TREE ("The live tree (`.mts_live`) ... changes only by a manual or coordinator-run deploy", Hard rules): the live tree is every
            directory that holds a FILE named `.mts_live` (auto_deploy.Ops.is_live, sync.LIVE_MARKER; found by walking up the parents,
            cached). Edit/Write/NotebookEdit inside it is denied. Bash/PowerShell: a write verb (> >> tee Set-Content Add-Content Out-File
            New-Item rm del Remove-Item mv cp Copy-Item touch mkdir sed -i, git commit|merge|pull|checkout|reset|...) on a path in that tree
            (or with the working directory, including after `cd`, in it) is denied. Reads stay allowed.
 4 RUNTIME  ("Builders never deploy, stop/restart processes, touch HALT files or open trades", Hard rules): taskkill, Stop-Process,
            Restart-Computer, `mts start|stop|restart`, writes/deletes of a file named HALT or AUTO_PAUSE, deribit_orders,
            `private/(buy|sell|edit|cancel)`.
Never blocked: reads of logs, grep/echo of these words, git log/show/diff/status, `python scripts/dev/sync.py ...` (and desk/dsa/tasks,
which do their own git), tests.

OVERRIDE for a deliberate operator or coordinator deploy (DEPLOY_RUNBOOK.md flow): put the token `#deploy-ok` in the command text
(e.g. `git -C <live tree> pull  #deploy-ok`). It lifts rules 3 and 4 only; secrets and git safety stay on.
MTS_SAFETY_GUARD=0 disables the whole hook: tests only.

  python scripts/dev/safety_guard.py check '<hook payload json>'    prints the decision (debug)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import turn_meter  # noqa: E402,F401  is_subagent exists for callers; the guard deliberately does NOT skip subagents

LIVE_MARKER = ".mts_live"
OVERRIDE = "#deploy-ok"
GUARDED = ("Read", "Grep", "Glob", "Edit", "Write", "NotebookEdit", "Bash", "PowerShell")
FILE_TOOLS = ("Edit", "Write", "NotebookEdit")
SHELL_TOOLS = ("Bash", "PowerShell")
PATH_KEYS = ("file_path", "path", "pattern", "glob", "notebook_path")

_live_cache = {}


# ---------------------------------------------------------------- live tree
def norm(p):
    p = str(p).replace("\\", "/")
    if os.name == "nt":
        m = re.match(r"^/([A-Za-z])(/|$)", p)
        if m:
            p = m.group(1).upper() + ":" + p[2:]
    return p


def live_root(path, base=None):
    """The live-tree root holding the marker file at or above path, else None (cached per directory)."""
    try:
        p = norm(path)
        if base and not re.match(r"^([A-Za-z]:)?/", p):
            p = norm(base) + "/" + p
        cur = os.path.normpath(os.path.abspath(p))
    except (ValueError, OSError, TypeError):
        return None
    seen = []
    root = None
    while True:
        if cur in _live_cache:
            root = _live_cache[cur]
            break
        seen.append(cur)
        if os.path.isfile(os.path.join(cur, LIVE_MARKER)):
            root = cur
            break
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    for d in seen:
        _live_cache[d] = root
    return root


# ---------------------------------------------------------------- secrets
SECRET_EXEMPT = ("example", "sample", "template", "dist")
ENV_RE = re.compile(r"(?:^|[\s/\\\"'=:(*,])\.env(?:\.([\w.*-]*))?(?=$|[\s\"';|&)*?\]\\/,])")
SECRETS_DIR_RE = re.compile(r"(?:^|[\s/\\\"'=:(*,])\.secrets(?=$|[\s\"';|&)*?\]\\/,])")
KEY_RE = re.compile(r"\.(?:pem|key)(?=$|[\s\"';|&)*?\]\\,])")
RSA_RE = re.compile(r"(?<![\w.-])id_rsa(?!\.pub)")


def secret_hit(text):
    t = str(text)
    if SECRETS_DIR_RE.search(t):
        return "a .secrets directory"
    for m in ENV_RE.finditer(t):
        suf = (m.group(1) or "").lower()
        if suf.split(".")[-1] not in SECRET_EXEMPT:
            return "a .env file"
    if KEY_RE.search(t):
        return "a .pem/.key file"
    if RSA_RE.search(t):
        return "id_rsa"
    return None


SECRET_FIX = ("Do not read or touch secrets/keys (CLAUDE.md Hard rules: never read .secrets/, .env, keys). Use .env.example or ask the "
              "operator to run it himself.")


# ---------------------------------------------------------------- shell text helpers
HEREDOC_RE = re.compile(r"(<<-?\s*['\"]?(\w+)['\"]?[^\n]*)\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", re.S)
HERESTR_RE = re.compile(r"@(['\"])\s*\n.*?\n\1@", re.S)
TOKEN_RE = re.compile(r"\"[^\"]*\"|'[^']*'|[^\s]+")
READ_FIRST = {"echo", "printf", "grep", "egrep", "fgrep", "rg", "ag", "findstr", "select-string", "sls", "cat", "type", "get-content", "gc",
              "head", "tail", "less", "more", "ls", "dir", "get-childitem", "gci", "wc", "diff", "sort", "where", "which",
              "get-command", "write-host", "write-output", "man", "help", "test", "gh"}
OWN_GIT_SCRIPTS = ("sync.py", "desk.py", "dsa.py", "tasks.py", "make_status.py", "run_all_tests.py", "safety_guard.py")
SHELLS = {"bash", "sh", "zsh", "pwsh", "powershell", "cmd", "eval", "ssh"}
PYTHONS = {"python", "python3", "py"}
PREFIX_WORDS = {"sudo", "time", "env", "call", "nohup", "command", "exec", "start-process", "&", "."}


def strip_heredocs(cmd):
    return HERESTR_RE.sub("", HEREDOC_RE.sub(r"\1", cmd))


def split_segments(cmd):
    """Quote-aware split on ; && || | newline."""
    segs, cur, q, i = [], [], None, 0
    while i < len(cmd):
        c = cmd[i]
        if q:
            cur.append(c)
            if c == q:
                q = None
        elif c in "\"'":
            q = c
            cur.append(c)
        elif c in ";\n|":
            segs.append("".join(cur))
            cur = []
            if c == "|" and cmd[i + 1:i + 2] == "|":
                i += 1
        elif c == "&" and cmd[i + 1:i + 2] == "&":
            segs.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(c)
        i += 1
    segs.append("".join(cur))
    return [s.strip() for s in segs if s.strip()]


def tokens(seg):
    out = []
    for t in TOKEN_RE.findall(seg):
        if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
            t = t[1:-1]
        out.append(t)
    return out


def base(tok):
    b = tok.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return b[:-4] if b.endswith(".exe") else b


def first_word(toks):
    i = 0
    while i < len(toks) and (re.match(r"^[A-Za-z_]\w*=", toks[i]) or base(toks[i]) in PREFIX_WORDS):
        i += 1
    return (base(toks[i]) if i < len(toks) else ""), i


# ---------------------------------------------------------------- rule 2: git
def force_flag(a):
    return a.startswith("--force") or bool(re.fullmatch(r"-[A-Za-z]*f[A-Za-z]*", a))


def git_subcommands(toks):
    """Yield (subcommand, args) for each `git` word in toks."""
    for i, t in enumerate(toks):
        if base(t) != "git":
            continue
        j = i + 1
        while j < len(toks) and toks[j].startswith("-"):
            j += 2 if toks[j] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
        if j < len(toks):
            yield toks[j].lower(), toks[j + 1:]


def is_master(a):
    return bool(re.search(r"(?:^|[:/+])master$", a))


def git_reason(sub, args):
    if sub == "push":
        if any(force_flag(a) and not a.startswith("--follow") for a in args if a.startswith("-")) or any(a.startswith("+") and len(a) > 1 for a in args):
            return "git push with --force/-f/+refspec", "Push normally (`python scripts/dev/sync.py ship`); never rewrite shared history."
        if any(is_master(a) for a in args if not a.startswith("-")):
            return "git push naming master", "Never push to master; ship through `python scripts/dev/sync.py ship`."
    elif sub == "commit":
        skip, names = False, False
        for a in args:
            if skip:
                skip = False
            elif a in ("-m", "--message", "-F", "--file", "-C", "-c"):
                skip = True
            elif not a.startswith("-") and is_master(a):
                names = True
        if names:
            return "git commit naming master", "Never commit to master; work on your <host>/<slug> branch."
    elif sub == "reset" and "--hard" in args:
        return "git reset --hard", "Never reset; use `git revert`-free flow: a new commit, or ask the operator."
    elif sub == "rebase" and not any(a in ("--abort", "--quit") for a in args):
        return "git rebase", "Never rebase; merge origin/fast-track into your branch instead."
    elif sub == "clean" and any(force_flag(a) for a in args if a.startswith("-")):
        return "git clean -f", "Never clean: it deletes others' uncommitted files. Remove your own files by path."
    elif sub == "stash":
        pos = [a for a in args if not a.startswith("-")]
        has_u = any(a in ("--include-untracked", "--all") or re.fullmatch(r"-[A-Za-z]*u[A-Za-z]*", a) for a in args)
        has_m = any(a in ("-m", "--message") or a.startswith("--message=") or re.fullmatch(r"-[A-Za-z]*m[A-Za-z]*", a) for a in args)
        sub2 = pos[0].lower() if pos else ""
        if sub2 in ("list", "show", "apply", "drop"):
            return None
        if sub2 in ("pop", "save", "clear", "branch"):
            return f"git stash {sub2}", ("The stash stack is shared: use `git stash push -u -m <tag>`, capture the sha, `git stash apply <sha>`, "
                                         "never pop; or make a WIP commit.")
        if sub2 in ("", "push") and not (has_u and has_m):
            return "bare git stash", "Use `git stash push -u -m <unique-tag>` (never bare stash/pop: the stack is shared), or a WIP commit."
    elif sub == "checkout" and (args and any(a in (".", ":/", "*") for a in args)):
        return "git checkout . (discards work)", "Revert only your own files by path, never `.`."
    elif sub == "restore" and any(a in (".", ":/", "*") for a in args):
        if "--staged" in args and "--worktree" not in args and "-W" not in args:
            return None
        return "git restore . (discards work)", "Restore your own files by path, never `.`."
    elif sub == "branch" and any(re.fullmatch(r"-[A-Za-z]*D[A-Za-z]*", a) for a in args):
        return "git branch -D", "Do not force-delete branches; ask the operator (`git branch -d` for merged ones)."
    return None


# ---------------------------------------------------------------- rule 3/4 verbs
RUNTIME_RES = [
    (re.compile(r"(?<![\w.-])taskkill(?:\.exe)?(?![\w-])", re.I), "taskkill"),
    (re.compile(r"(?<![\w-])Stop-Process(?![\w-])", re.I), "Stop-Process"),
    (re.compile(r"(?<![\w-])Restart-Computer(?![\w-])", re.I), "Restart-Computer"),
    (re.compile(r"(?<![\w-])mts\s+(?:start|stop|restart)(?![\w-])", re.I), "mts start|stop|restart"),
    (re.compile(r"(?<![\w])deribit_orders(?![\w])"), "deribit_orders"),
    (re.compile(r"private/(?:buy|sell|edit|cancel)(?![\w])", re.I), "a Deribit private order endpoint"),
]
RUNTIME_FIX = ("Builders never deploy, restart processes, touch HALT/AUTO_PAUSE or open trades (CLAUDE.md Hard rules). Report it to the "
               "coordinator/operator; a deliberate operator deploy adds `#deploy-ok` to the command (DEPLOY_RUNBOOK.md).")
WRITE_VERBS = {"tee", "set-content", "add-content", "out-file", "new-item", "ni", "rm", "del", "erase", "remove-item", "ri", "rmdir", "rd",
               "mv", "move", "move-item", "mi", "cp", "copy", "copy-item", "touch", "mkdir", "md", "clear-content", "rename-item", "ren"}
COPY_VERBS = {"cp", "copy", "copy-item"}
GIT_WRITE = {"commit", "merge", "pull", "checkout", "reset", "rebase", "add", "restore", "clean", "cherry-pick", "revert", "am", "apply",
             "switch", "stash", "rm", "mv"}
HALT_RE = re.compile(r"(?:^|[\s/\\\"'=])(?:HALT|AUTO_PAUSE)(?:\.\w+)?(?=$|[\s\"';|&)])")
REDIR_RE = re.compile(r"\d*>>?\s*(?!&)([^\s|;&<>]+)")
NULLS = ("/dev/null", "nul", "$null")


def redirects(seg):
    return [m for m in (x.strip("\"'") for x in REDIR_RE.findall(seg)) if m.lower() not in NULLS]


def has_write_verb_for_halt(seg, toks):
    if redirects(seg) and HALT_RE.search(" ".join(redirects(seg))):
        return True
    verbs = [t.lower() for t in toks if t.lower() in WRITE_VERBS or t.lower() == "-delete"]
    return bool(verbs) and bool(HALT_RE.search(seg))


# ---------------------------------------------------------------- the shell check
def shell_reason(cmd, cwd, depth=0):
    override = OVERRIDE in cmd
    cmd = strip_heredocs(cmd)
    cur = cwd or os.getcwd()
    for seg in split_segments(cmd):
        toks = tokens(seg)
        if not toks:
            continue
        fw, fi = first_word(toks)
        sec_seg = seg
        # secrets (git check-ignore is the one allowed mention)
        if not (fw == "git" and "check-ignore" in toks):
            s = secret_hit(sec_seg if not (fw == "git" and "commit" in toks) else " ".join(
                t for k, t in enumerate(toks) if not (k and toks[k - 1] in ("-m", "--message", "-F"))))
            if s:
                return f"command names {s}. {SECRET_FIX}"
        own = any(base(t) in OWN_GIT_SCRIPTS for t in toks[fi:fi + 4]) and fw in PYTHONS | {"pytest"}
        testrun = fw in PYTHONS and "-m" in toks[fi:fi + 3] and any(t in ("unittest", "pytest") for t in toks[fi:fi + 4])
        skip_text = fw in READ_FIRST or fw == "git" or own or testrun or fw == "pytest"
        # nested shells: bash -c "git push -f"
        if fw in SHELLS and depth < 3:
            for t in toks[fi + 1:]:
                if " " in t:
                    r = shell_reason(t + (" " + OVERRIDE if override else ""), cur, depth + 1)
                    if r:
                        return r
        # rule 2
        if not (own or testrun) and fw not in READ_FIRST:
            for sub, args in git_subcommands(toks):
                r = git_reason(sub, args)
                if r:
                    return f"{r[0]} is denied (CLAUDE.md Hard rules). Fix: {r[1]}"
        # cd tracking
        if fw in ("cd", "set-location", "sl", "pushd", "chdir") and len(toks) > fi + 1:
            arg = [t for t in toks[fi + 1:] if not t.startswith("-") or t.startswith("-Path")][-1] if toks[fi + 1:] else ""
            arg = norm(arg)
            cur = arg if re.match(r"^([A-Za-z]:)?/", arg) else norm(cur) + "/" + arg
            continue
        if override:
            continue
        # rule 4
        if has_write_verb_for_halt(seg, toks):
            return f"command writes or deletes a HALT/AUTO_PAUSE file. {RUNTIME_FIX}"
        if not skip_text:
            for rx, label in RUNTIME_RES:
                if rx.search(seg):
                    return f"command uses {label}. {RUNTIME_FIX}"
        # rule 3
        r = live_shell_reason(seg, toks, fw, fi, cur, own)
        if r:
            return r
    return None


LIVE_FIX = ("The live tree (.mts_live) changes only by a deploy (DEPLOY_RUNBOOK.md). Work in your worktree and `python scripts/dev/sync.py ship`; "
            "a deliberate operator/coordinator deploy adds `#deploy-ok` to the command.")


def live_shell_reason(seg, toks, fw, fi, cur, own):
    if own:
        return None
    for tgt in redirects(seg):
        if live_root(tgt, cur):
            return f"redirect writes into the live tree ({live_root(tgt, cur)}). {LIVE_FIX}"
    low = [t.lower() for t in toks]
    for i, t in enumerate(toks):
        lt = low[i]
        verb = lt in WRITE_VERBS
        gitw = base(t) == "git" and any(sub in GIT_WRITE for sub, _ in git_subcommands(toks[i:i + 8]))
        sed_i = lt == "sed" and any(a.startswith("-i") and not a.startswith("--") for a in toks[i + 1:i + 4])
        if not (verb or gitw or sed_i):
            continue
        if gitw:
            sub_toks = toks[i:i + 8]
            rest = [sub_toks[k + 1] for k, x in enumerate(sub_toks[:-1]) if x == "-C"] or [cur]
            rest += [x for x in toks[i + 1:] if ("/" in x or chr(92) in x)]
        else:
            rest = [x for x in toks[i + 1:] if not x.startswith("-")]
            if lt in COPY_VERBS:
                rest = rest[-1:]
            if not rest:
                rest = [cur]
        for x in rest:
            r = live_root(x, cur)
            if r:
                return f"{('git write' if gitw else lt)} targets the live tree ({r}). {LIVE_FIX}"
    return None


# ---------------------------------------------------------------- decide
def deny_reason(ev):
    tool = ev.get("tool_name") or ""
    if tool not in GUARDED:
        return None
    inp = ev.get("tool_input")
    cwd = ev.get("cwd") or None
    if tool in SHELL_TOOLS:
        if not isinstance(inp, dict) or not isinstance(inp.get("command"), str):
            return "unparsable " + tool + " input (no command string); retry with a plain command"
        return shell_reason(inp["command"], cwd)
    if not isinstance(inp, dict):
        return "unparsable " + tool + " input" if tool in FILE_TOOLS else None
    paths = [(k, inp[k]) for k in PATH_KEYS if isinstance(inp.get(k), str) and inp[k]]
    if tool in FILE_TOOLS:
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        fp = inp.get(key) or inp.get("file_path") or inp.get("notebook_path")
        if not isinstance(fp, str) or not fp:
            return f"unparsable {tool} input (no {key}); pass the file path"
        paths = [(key, fp)]
    for k, v in paths:
        if v.replace("\\", "/").rsplit("/", 1)[-1] == ".gitignore" and tool in FILE_TOOLS:
            continue
        s = secret_hit(norm(v))
        if s:
            return f"{tool} {k} names {s}. {SECRET_FIX}"
    if tool in FILE_TOOLS:
        r = live_root(paths[0][1], cwd)
        if r:
            return (f"{tool} on {paths[0][1]} is inside the live tree ({r}). The live tree changes only by a deploy (DEPLOY_RUNBOOK.md): "
                    "edit the same file in your worktree and ship it with `python scripts/dev/sync.py ship`.")
    return None


def decide(ev):
    if os.environ.get("MTS_SAFETY_GUARD") == "0":
        return None
    try:
        return deny_reason(ev)
    except Exception as e:  # fail closed on the write/exec tools
        if (ev.get("tool_name") or "") in FILE_TOOLS + SHELL_TOOLS:
            return f"unparsable input ({type(e).__name__}); simplify the call"
        return None


def hook():
    raw = sys.stdin.read()
    try:
        ev = json.loads(raw or "{}")
        if not isinstance(ev, dict):
            raise ValueError("not an object")
    except ValueError:
        m = re.search(r'"tool_name"\s*:\s*"(\w+)"', raw or "")
        if m and m.group(1) in FILE_TOOLS + SHELL_TOOLS and os.environ.get("MTS_SAFETY_GUARD") != "0":
            ev = None
            reason = f"unparsable {m.group(1)} hook input"
        else:
            return 0
    else:
        reason = decide(ev)
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": "safety_guard: " + reason}}))
    return 0


def main(argv):
    if argv[:1] == ["hook"]:
        return hook()
    if argv[:1] == ["check"] and len(argv) >= 2:
        print(decide(json.loads(argv[1])) or "allow")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
