"""Per-layer index for every session (Claude or Codex): spec, ledger, latest results, open cards, roadmap.

  python scripts/dev/make_layers_md.py          # writes MyTradingSys/system/LAYERS.md
  python scripts/dev/make_layers_md.py --check  # exit 1 if a pointer is dead (card state may differ; regenerate to refresh)

Hand-kept pointers: MyTradingSys/system/layer_index.json. Open cards are read live from system/tasks/*.json (glob by card id),
so the page never carries a copy of card state. Zero model tokens.
"""
import argparse
import fnmatch
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
IDX = REPO / "MyTradingSys" / "system" / "layer_index.json"
TASKS = REPO / "MyTradingSys" / "system" / "tasks"
OUT = REPO / "MyTradingSys" / "system" / "LAYERS.md"
SECTIONS = (("spec", "Spec / sources"), ("code", "Code"), ("ledger", "Ledger"), ("results", "Latest results"), ("roadmap", "Roadmap"))


def missing_paths(idx):
    bad = []
    for f in idx["families"]:
        for key, _ in SECTIONS:
            bad += [(f["id"], p) for p in f[key] if not (REPO / p).exists()]
    bad += [("cross_cutting", c["where"].split(" ")[0].rstrip(";")) for c in idx["cross_cutting"]
            if "/" in c["where"].split(" ")[0].rstrip(";") and not (REPO / c["where"].split(" ")[0].rstrip(";")).exists()]
    return bad


def cards():
    out = []
    for p in sorted(TASKS.glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except ValueError:
            pass
    return out


def render(idx):
    allc = cards()
    L = ["# LAYERS - one index per layer (generated; do not hand-edit)", "",
         "Source: `MyTradingSys/system/layer_index.json` (pointers) + live task cards. Regenerate: `python scripts/dev/make_layers_md.py`.",
         "Add a layer or move a file: edit the JSON, regenerate; `--check` / `tests/test_layers_index.py` fail on a dead pointer.",
         "Rules: Tom is core, every other family is a separate layer and never a Tom filter (CLAUDE.md). A new result goes in the family's",
         "Latest results AND as a row in `layer_map.json`. Two tracks work here: Claude sessions and the Codex layer lab (lane CODEX); both read this page first.", ""]
    for f in idx["families"]:
        L += [f"## {f['name']}", f"- Status: {f['status']}", f"- Tracks: {f['tracks']}"]
        for key, label in SECTIONS:
            if f[key]:
                L.append(f"- {label}: " + "; ".join(f"`{p}`" for p in f[key]))
        mine = [c for c in allc if c.get("state") != "done" and any(fnmatch.fnmatch(c["id"], g) for g in f["cards"])]
        if mine:
            L.append("- Open cards (`tasks.py brief <id>`):")
            L += [f"  - `{c['id']}` {c.get('state')} p{c.get('prio')} {c.get('lane')}: {c.get('title', '')[:110]}" for c in sorted(mine, key=lambda c: (c.get("prio", 9), c["id"]))]
        else:
            L.append("- Open cards: none")
        L.append("")
    L += ["## Cross-cutting", ""] + [f"- {c['what']}: {c['where']}" for c in idx["cross_cutting"]] + [""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    idx = json.loads(IDX.read_text(encoding="utf-8"))
    bad = missing_paths(idx)
    for fam, p in bad:
        print(f"MISSING {fam}: {p}")
    text = render(idx)
    if a.check:
        print("pointers ok" if not bad else f"{len(bad)} dead pointer(s)")
        return 1 if bad else 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(REPO)} ({len(idx['families'])} families)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
