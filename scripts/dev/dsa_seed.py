"""dsa_seed.py: the DSA chat seed for PARALLEL chats (chat slug, cards held by other DSA chats, UTF-8 stdout).

  python scripts/dev/dsa_seed.py [--print]    # the seed on the clipboard (--print: on stdout); paste in a new DeepSeek chat

It wraps dsa.seed_text (the base seed) and adds three things without touching dsa.py: dsa.py is a DSA-bridge file, and any
change to it forces a bridge version bump, which puts every running chat into a version mismatch (aibridge_version.py).
Fold this into dsa.py at the next planned bridge bump (card dsa-multi-chat-driver-1107). Stdlib only, ASCII output.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dsa  # noqa: E402

LANES = ("DSA", "DSA-NB", "DSA-NUC")
MAX_IDS = 6              # cards named in the seed (and at most ~90 chars of ids); the rest are "+N more"
ID_LINE = "$id = (hostname).ToLower() + '-' + (Get-Date).ToUniversalTime().ToString('MMdd-HHmm')"
UTF8_LINE = "$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'"


def parse_card_ids(text):
    """Unique card ids (first column) of `tasks.py list` output, in order."""
    seen = []
    for line in text.splitlines():
        parts = line.split()
        if parts and parts[0] not in seen:
            seen.append(parts[0])
    return seen


def claimed_dsa_cards(work=None):
    """Ids of cards active in the DSA lanes (held by DSA chats now). [] when tasks.py cannot say; never raises."""
    work = Path(work or Path.cwd())
    ids = []
    for lane in LANES:
        rc, out, _ = dsa.run([sys.executable, str(dsa.script_path(work, "tasks.py")), "list", "--state", "active", "--lane", lane],
                             cwd=work, timeout=60)
        if rc == 0:
            ids += [i for i in parse_card_ids(out) if i not in ids]
    return ids


def build_seed(host, slug=None, claimed=None):
    """The base seed with the chat slug fixed in the block, the UTF-8 env line, and the held-cards line."""
    slug = slug or (host.lower() + "-" + dsa.utc_now().strftime("%m%d-%H%M"))
    held = list(claimed or [])
    keep = []
    for cid in held[:MAX_IDS]:                        # whole ids only, so each line stays under the 200-char seed rule
        if len(", ".join(keep + [cid])) > 90:
            break
        keep.append(cid)
    shown = ", ".join(keep) + (f" (+{len(held) - len(keep)} more)" if len(held) > len(keep) else "")
    lines = dsa.seed_text(host).splitlines()
    if ID_LINE not in lines or not any(l.startswith("STEP 1.") for l in lines):
        raise dsa.Failed("base seed changed shape; update dsa_seed.py")
    out = []
    for ln in lines:
        if ln.startswith("STEP 1."):
            out += [f"Your chat slug: {slug} (worktree mts-dsa-{slug}). Held by other DSA chats now: {shown or 'none'}.",
                    "Several DSA chats run in parallel: take cards only via tasks.py take; prompt section 0b is the rule.", ""]
        if ln == ID_LINE:
            ln = f"$id = '{slug}'"
        out.append(ln)
        if ln.startswith("$ErrorActionPreference"):
            out.append(UTF8_LINE)
    text = "\n".join(out) + "\n"
    for ln in out:
        if len(ln) >= 200:
            raise dsa.Failed(f"seed line too long: {ln[:40]}")
    if len(text.encode("ascii")) > dsa.SEED_MAX_BYTES:
        raise dsa.Failed(f"seed over {dsa.SEED_MAX_BYTES} bytes")
    return text


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(prog="dsa_seed.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print", action="store_true", help="print the seed instead of copying it")
    a = ap.parse_args(argv)
    try:
        text = build_seed(dsa.hostname(), claimed=claimed_dsa_cards())
    except dsa.Failed as e:
        print(f"error: {e}")
        return 1
    if a.print or os.name != "nt":
        sys.stdout.write(text)
        return 0
    try:
        subprocess.run(["clip"], input=text, text=True, check=True, timeout=10)
        print(f"seed: {len(text)} chars on the clipboard")
    except (OSError, subprocess.SubprocessError) as e:
        sys.stdout.write(text)
        print(f"clipboard: FAILED {e}; the seed is printed above, copy it")
    print("NEXT: in the new DeepSeek chat press Ctrl+V, Enter; wait for the BOOT line; then say go, or name a task")
    return 0


if __name__ == "__main__":
    sys.exit(main())
