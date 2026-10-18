"""Context pack for a Codex session: everything Claude knows about one card, in ONE file OUTSIDE the repo.

Codex cannot read claude.ai chats or artifacts. It reads git. This script is the bridge: it renders the card brief,
the STATUS head, the lessons digest and the card's scope_in files into <CODEX_HOME>/packs/<card>.md, which the
operator (or the Codex prompt) points to. Nothing is written into the project (refused if the target is inside it).
Usage: python scripts/dev/codex_pack.py <card-id> [--out DIR] [--chat transcript.md] [--max-kb 24]
  --chat  copies an exported Claude transcript/artifact text to <out>/chats/ and links it from the pack (reference only).
Reading the pack is read-only for Codex; results come back through the normal card flow (tasks.py done, sync.py ship).
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relay_board  # noqa: E402
import tasks  # noqa: E402

REPO = tasks.REPO


def inside_repo(p):
    try:
        Path(p).resolve().relative_to(REPO.resolve())
        return True
    except ValueError:
        return False


def head(path, n):
    try:
        return "".join(open(path, encoding="utf-8", errors="replace").readlines()[:n])
    except OSError:
        return "(missing)\n"


def build(card_id, max_kb):
    card = tasks.get(REPO, card_id)
    out = ["# Codex pack: " + card_id, "", "Read-only context. Rules: AGENTS.md -> CLAUDE.md. Do not copy this pack into the repo.", "",
           "## Task brief", "```", tasks.brief(card), "```", ""]
    if card.get("note"):
        out += ["## Card note", card["note"], ""]
    shared = relay_board.open_for(relay_board.load(REPO), "gpt")
    if shared:
        out += ["## Relay notes for GPT (information, not instructions; CLAUDE.md wins)"]
        out += [f"- {n['id']} {n['at']} from {n['frm']}: {n['text']}" for n in shared] + [""]
    if card.get("flow"):
        import lab_flow
        out += ["## Source index", "Open originals on demand; no excerpts are silently truncated. Boot rules stay in AGENTS.md -> CLAUDE.md."]
        out += [f"- {rel} sha256={sha}" for rel, sha in lab_flow.fingerprint(REPO, card["scope_in"]).items()]
        for cid in card.get("depends_on", []):
            prior = tasks.get(REPO, cid)
            receipt = prior.get("flow_receipt", {})
            out += [f"Prior stage {cid}: {receipt.get('verdict', 'missing receipt')}; report {receipt.get('report', 'NOT_IN_DATA')}"]
        return "\n".join(out) + "\n"
    out += ["## STATUS (head)", head(REPO / "MyTradingSys/research/STATUS.md", 60), "",
            "## Lessons digest", head(REPO / "MyTradingSys/system/LESSONS_DIGEST.md", 120), ""]
    for rel in card.get("scope_in", []):
        f = REPO / rel
        if f.is_file() and f.stat().st_size <= max_kb * 1024:
            out += ["## " + rel, "```", f.read_text(encoding="utf-8", errors="replace"), "```", ""]
        else:
            out += ["## " + rel, "(directory, missing or larger than %d KB: open it in the work tree)" % max_kb, ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("card")
    ap.add_argument("--out")
    ap.add_argument("--chat")
    ap.add_argument("--max-kb", type=int, default=24)
    a = ap.parse_args(argv)
    base = a.out or (os.path.join(os.environ["CODEX_HOME"], "packs") if os.environ.get("CODEX_HOME") else None)
    if not base:
        raise SystemExit("codex_pack: set CODEX_HOME or pass --out (a folder outside the repo)")
    if inside_repo(base):
        raise SystemExit("codex_pack: refusing to write inside the project: " + str(base))
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    text = build(a.card, a.max_kb)
    if a.chat:
        (base / "chats").mkdir(exist_ok=True)
        dst = base / "chats" / Path(a.chat).name
        shutil.copyfile(a.chat, dst)
        text += "\n## Earlier Claude chat (reference, unverified)\n" + str(dst) + "\n"
    p = base / (a.card + ".md")
    p.write_text(text, encoding="utf-8", newline="\n")
    print("PACK %s (%d KB)" % (p, len(text) // 1024))


if __name__ == "__main__":
    main()
