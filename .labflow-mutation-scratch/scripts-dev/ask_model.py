"""Ask Gemini or GPT a question straight from a session: prompt in, answer out (no desk row, no card).

  python scripts/dev/ask_model.py gemini "<prompt>" [--model flash|argon|sonnet|opus] [--effort low|medium|high] [--file PATH ...]
  python scripts/dev/ask_model.py gpt    "<prompt>" [--model <codex model>]          [--effort low|medium|high] [--file PATH ...]
  python scripts/dev/ask_model.py --prompt-file p.txt gemini                          (long prompts)

Read-only by design: the model runs in a fresh scratch folder (F:/MTS/ask/<utc>), never in a work tree or the live tree.
--file copies the named files into that folder (images and text), so the model sees only those. No write mode, no
--dangerously-skip-permissions, no git. Answer goes to stdout and to <scratch>/answer.txt. For work that must change
the repo use a card (gemini_queue.py / codex_run.py); this is for questions, reviews, frame reads and second opinions.
Gemini = Antigravity `agy --print` on the Google Pro login (quota pools: GEMINI_START.md). GPT = Codex CLI `exec`, read-only
sandbox (CODEX_HOME F:/codex_home, same login as the lab). Env: MTS_CODEX_EXE, MTS_ASK_ROOT, MTS_ASK_TIMEOUT_S (300).
Never put secrets, .secrets/ or .env content in a prompt or --file.
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import nowin  # no console flash under pythonw
    nowin.install()
except Exception:  # pragma: no cover
    pass

AGY = Path.home() / '.gemini' / 'bin' / 'agy.exe'
GEMINI_FAMILY = {'flash': 'gemini-3.8-flash', 'argon': 'gemini-4-argon', 'sonnet': 'claude-sonnet-5-5', 'opus': 'claude-opus-5-5'}
BLOCKED = ('.secrets', '.env', '.pem', '.key')


def scratch_dir(env=os.environ) -> Path:
    root = Path(env.get('MTS_ASK_ROOT') or 'F:/MTS/ask')
    d = root / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    d.mkdir(parents=True, exist_ok=True)
    return d


def stage_files(files, dest: Path) -> list[str]:
    names = []
    for f in files:
        p = Path(f)
        if any(b in str(p).lower() for b in BLOCKED):
            raise SystemExit(f'ask_model: refusing {p} (secret-like path)')
        if not p.is_file():
            raise SystemExit(f'ask_model: no such file {p}')
        shutil.copy(p, dest / p.name)
        names.append(p.name)
    return names


def gemini_model(model: str, effort: str) -> str:
    fam = GEMINI_FAMILY.get(model, model)
    return fam if fam.rsplit('-', 1)[-1] in ('low', 'medium', 'high') else f'{fam}-{effort}'


def gemini_cmd(prompt: str, model: str, effort: str, exe=AGY) -> list[str]:
    return [str(exe), '--print', prompt, '--model', gemini_model(model, effort)]


def find_codex(env=os.environ) -> str:
    import codex_run
    return codex_run.find_exe(env)


def gpt_cmd(model: str | None, effort: str, wd: Path, exe: str) -> list[str]:
    cmd = [exe, 'exec']
    if model:
        cmd += ['-m', model]
    return cmd + ['--skip-git-repo-check', '-c', f'model_reasoning_effort="{effort}"', '-s', 'read-only', '-C', str(wd), '-']  # prompt on stdin


def with_files(prompt: str, names: list[str]) -> str:
    if not names:
        return prompt
    return f'Files in this folder (open them as needed): {", ".join(names)}.\n{prompt}'


def run(which: str, prompt: str, model: str | None, effort: str, files, env=os.environ) -> tuple[int, str, Path]:
    wd = scratch_dir(env)
    prompt = with_files(prompt, stage_files(files, wd))
    timeout = int(env.get('MTS_ASK_TIMEOUT_S') or 300)
    penv = dict(env, CODEX_HOME=env.get('CODEX_HOME') or 'F:/codex_home')
    if which == 'gemini':
        if not AGY.exists():
            raise SystemExit(f'ask_model: agy not found at {AGY} (install: GEMINI_START.md)')
        r = subprocess.run(gemini_cmd(prompt, model or 'flash', effort), cwd=wd, capture_output=True, text=True, timeout=timeout)
    else:
        r = subprocess.run(gpt_cmd(model, effort, wd, find_codex(env)), cwd=wd, input=prompt, capture_output=True,
                           text=True, timeout=timeout, env=penv)
    out = (r.stdout or '').strip() or (r.stderr or '').strip()
    (wd / 'answer.txt').write_text(out, encoding='utf-8', newline='\n')
    return r.returncode, out, wd


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('which', choices=('gemini', 'gpt'))
    ap.add_argument('prompt', nargs='?')
    ap.add_argument('--prompt-file')
    ap.add_argument('--model')
    ap.add_argument('--effort', default='low', choices=('low', 'medium', 'high'))
    ap.add_argument('--file', action='append', default=[])
    a = ap.parse_args(argv)
    prompt = Path(a.prompt_file).read_text(encoding='utf-8') if a.prompt_file else a.prompt
    if not prompt:
        ap.error('give a prompt or --prompt-file')
    code, out, wd = run(a.which, prompt, a.model, a.effort, a.file)
    print(out)
    print(f'[ask_model {a.which} exit {code}; scratch {wd}]', file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main())
