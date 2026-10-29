"""config_check.py - the config files that are not code but break things when wrong (GATE_SPEED D5, gate step 3js).

  python scripts/dev/config_check.py     exit 1 and one line per problem

Checks: .claude/settings.json parses and every hook command names a script that exists in the repo (a broken hook breaks every
session, and no test ran on a settings.json-only change before the smoke gate took it); secret paths stay ignored in this PUBLIC repo
(`git check-ignore`, so a .gitignore edit that un-ignores them fails the gate).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SETTINGS = ".claude/settings.json"
SECRET_SENTINELS = (".secrets/key.txt", ".env", ".env.local")   # CLAUDE.md hard rules: never read or commit .secrets/, .env


def hook_scripts(settings):
    """Repo-relative script paths that the hook commands run ($CLAUDE_PROJECT_DIR/<path>.py|.ps1)."""
    out = []
    for groups in (settings.get("hooks") or {}).values():
        for g in groups or []:
            for h in g.get("hooks") or []:
                for m in re.finditer(r"\$\{?CLAUDE_PROJECT_DIR\}?[/\\]([\w./\\-]+\.(?:py|ps1))", h.get("command") or ""):
                    out.append(m.group(1).replace("\\", "/"))
    return out


def problems(root=REPO):
    root = Path(root)
    bad = []
    p = root / SETTINGS
    if p.exists():
        try:
            settings = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return [f"{SETTINGS}: does not parse: {e}"]
        bad += [f"{SETTINGS}: hook script missing: {s}" for s in hook_scripts(settings) if not (root / s).is_file()]
    r = subprocess.run(["git", "-C", str(root), "check-ignore", "--no-index", *SECRET_SENTINELS], capture_output=True, text=True)
    ignored = set(r.stdout.split())
    bad += [f".gitignore: secret path not ignored: {s}" for s in SECRET_SENTINELS if s not in ignored]
    return bad


def main():
    bad = problems()
    for b in bad:
        print(b)
    print("config check: " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
