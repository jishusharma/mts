"""Read-only audit of .claude/settings*.json permissions for unattended runs.
Usage: python scripts/dev/perm_audit.py [--settings FILE ...]   (exit 1 on a finding)
Default files: .claude/settings.json and .claude/settings.local.json in the git top level
and in the main checkout. Never edits anything; the fix is a per-machine edit (SURFACE_POLICY.md)."""
import json, os, re, subprocess, sys

NEEDED_GIT = ("merge", "commit", "pull", "fetch")  # sync.py runs these; a deny stalls the run
PATH_RULE = re.compile(r"^(?:Read|Write|Edit|MultiEdit)\((.*)\)$")


def _abs_outside(path, root):
    p = path.replace("\\", "/")
    if p.startswith("//") or re.match(r"^[A-Za-z]:/", p) or p.startswith("/"):
        if root and p.lower().replace("//", "/").startswith(root.replace("\\", "/").lower()):
            return False
        return True
    return p.startswith("..")


def audit(settings, root="", skip_bash=False):
    perm = (settings or {}).get("permissions", {}) or {}
    allow, deny = perm.get("allow", []) or [], perm.get("deny", []) or []
    out = []
    for g in NEEDED_GIT:
        for d in deny:
            if re.match(r"^Bash\(git %s(?:[ :*)]|$)" % g, d):
                out.append("FINDING denied git %s: %s (sync.py needs it)" % (g, d))
    if not skip_bash and not any(a == "Bash" or a.startswith("Bash(") for a in allow) and perm.get("defaultMode") not in ("bypassPermissions", "acceptEdits"):
        out.append("FINDING no Bash allow rule: every shell call prompts")
    for a in allow:
        m = PATH_RULE.match(a)
        if m and _abs_outside(m.group(1), root):
            out.append("FINDING path outside the checkout in allow: %s (prompts even in Bypass)" % a)
    for d in perm.get("additionalDirectories", []) or []:
        if _abs_outside(d, root):
            out.append("FINDING additionalDirectories outside the checkout: %s" % d)
    return out


def _git(*a):
    try:
        return subprocess.run(["git", *a], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    files = []
    explicit = "--settings" in argv
    if "--settings" in argv:
        files = argv[argv.index("--settings") + 1:]
    root = _git("rev-parse", "--show-toplevel")
    if not files:
        common = _git("rev-parse", "--git-common-dir")
        main_root = os.path.dirname(os.path.abspath(common)) if common else root
        for r in dict.fromkeys([root, main_root]):
            for n in ("settings.json", "settings.local.json"):
                files.append(os.path.join(r, ".claude", n))
    bad = 0
    for f in files:
        if not os.path.isfile(f):
            print("OK (absent) " + f)
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                s = json.load(fh)
        except Exception as e:
            print("FINDING unreadable %s: %s" % (f, e)); bad += 1; continue
        # settings.json alone often has no allow list; only the local file (or an explicit --settings) is judged for it
        res = audit(s, root, skip_bash=(not explicit and os.path.basename(f) == "settings.json"))
        for line in res:
            print("%s: %s" % (f, line))
        bad += len(res)
        if not res:
            print("OK " + f)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
