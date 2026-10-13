"""Per-layer index for every session (Claude or Codex): spec, code, ledger, backtests, lab reports, roadmap, open cards.

  python scripts/dev/make_layers_md.py          # writes MyTradingSys/system/LAYERS.md
  python scripts/dev/make_layers_md.py --check  # exit 1 on a dead pointer or a layer_map layer with no family

Sources, none copied by hand into the page:
  MyTradingSys/system/layer_index.json   family pointers (spec, code, ledger, docs, roadmap) + which layer_map layers it owns
  MyTradingSys/system/layer_map.json     layer status and every backtest row (verdict, report) -> "Backtests"
  MyTradingSys/system/tasks/*.json       open cards, joined by the card's `layers` field (id globs only as a fallback)
  MyTradingSys/research/layer_lab/reports  Codex lab reports, joined through their card id
tasks.py regenerates the page after every card change. Zero model tokens.
"""
import argparse
import fnmatch
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
SYS = "MyTradingSys/system"
IDX = REPO / SYS / "layer_index.json"
MAP = REPO / SYS / "layer_map.json"
OUT = REPO / SYS / "LAYERS.md"
LAB = "MyTradingSys/research/layer_lab/reports"
SECTIONS = (("spec", "Spec / sources"), ("code", "Code"), ("ledger", "Ledger"), ("results", "Other results"), ("roadmap", "Roadmap"))
OPEN = ("raw", "refined", "ready", "active", "blocked")
LAB_SHOWN = 4


def load(repo=REPO):
    repo = Path(repo)
    idx = json.loads((repo / SYS / "layer_index.json").read_text(encoding="utf-8"))
    lmap = json.loads((repo / SYS / "layer_map.json").read_text(encoding="utf-8"))
    cards = []
    for p in sorted((repo / SYS / "tasks").glob("*.json")):
        try:
            cards.append(json.loads(p.read_text(encoding="utf-8")))
        except ValueError:
            pass
    lab = repo / LAB
    reports = sorted((p.name for p in lab.glob("*.md") if p.name != "README.md"), reverse=True) if lab.is_dir() else []
    return idx, lmap, cards, reports


def family_ids(repo=REPO):
    return [f["id"] for f in json.loads((Path(repo) / SYS / "layer_index.json").read_text(encoding="utf-8"))["families"]]


def problems(idx, lmap, repo=REPO):
    """Dead pointers and layer ownership errors; [] when the index is sound."""
    repo = Path(repo)
    bad = []
    for f in idx["families"]:
        for key, _ in SECTIONS:
            bad += [f"{f['id']}: missing {p}" for p in f.get(key, []) if not (repo / p).exists()]
    for c in idx.get("cross_cutting", []):
        p = c["where"].split(" ")[0].rstrip(";")
        if "/" in p and not (repo / p).exists():
            bad.append(f"cross_cutting: missing {p}")
    owned = [lid for f in idx["families"] for lid in f.get("layers", [])]
    known = {layer["id"] for layer in lmap["layers"]}
    bad += [f"layer_map layer {lid} has no family in layer_index.json" for lid in sorted(known - set(owned))]
    bad += [f"layer_index.json names unknown layer {lid}" for lid in sorted(set(owned) - known)]
    bad += [f"layer {lid} is in more than one family" for lid in sorted({x for x in owned if owned.count(x) > 1})]
    return bad


def card_family(card, fams):
    """Families a card belongs to: its `layers` field, else the first family whose glob matches its id."""
    if card.get("layers"):
        return [x for x in card["layers"] if x in fams]
    for fid, f in fams.items():
        if any(fnmatch.fnmatch(card["id"], g) for g in f.get("cards", [])):
            return [fid]
    return []


def render(idx, lmap, cards, reports):
    fams = {f["id"]: f for f in idx["families"]}
    layers = {layer["id"]: layer for layer in lmap["layers"]}
    by_card = {c["id"]: card_family(c, fams) for c in cards}
    L = ["# LAYERS - one index per layer family (generated; do not hand-edit)", "",
         "Read this before touching any layer (Claude and Codex). Regenerate: `python scripts/dev/make_layers_md.py` (tasks.py does it on",
         "every card change). Pointers: `layer_index.json`; layer status and backtests: `layer_map.json`; cards: `system/tasks/`.",
         "Rules: no fixed core; layers may combine or filter each other, results decide (CLAUDE.md, 2026-10-13). A new backtest is a row in",
         "`layer_map.json` (it then shows here); a new layer joins a family in `layer_index.json`; a new card names `--layer <family>`.", "",
         "Families: " + " | ".join(f"{f['id']} = {f['name']}" for f in idx["families"]), ""]
    for f in idx["families"]:
        L += [f"## {f['name']} (`{f['id']}`)", f"- Status: {f['status']}", f"- Tracks: {f['tracks']}"]
        for lid in f.get("layers", []):
            layer = layers[lid]
            L.append(f"- Layer `{lid}`: {layer.get('status', '')} | module {layer.get('module', '')}")
        shown = set()
        bts = sorted((b for b in lmap["backtests"] if set(b.get("layers", [])) & set(f.get("layers", []))),
                     key=lambda b: b.get("date", ""), reverse=True)
        if bts:
            L.append("- Backtests (layer_map.json, newest first):")
            for b in bts:
                shown.add(b.get("report"))
                L.append(f"  - {b.get('date', '?')} `{b['id']}`: {str(b.get('verdict') or 'not recorded')[:120]} | `{b.get('report')}`")
        for key, label in SECTIONS:
            items = [p for p in f.get(key, []) if not (key == "results" and p in shown)]
            if items:
                L.append(f"- {label}: " + "; ".join(f"`{p}`" for p in items))
        lab = [r for r in reports if f["id"] in by_card.get(Path(r).stem.split("_", 1)[-1], [])]
        if lab:
            L.append(f"- Codex lab reports (newest {min(len(lab), LAB_SHOWN)} of {len(lab)}): " + "; ".join(f"`{LAB}/{r}`" for r in lab[:LAB_SHOWN]))
        mine = sorted((c for c in cards if c.get("state") in OPEN and f["id"] in by_card[c["id"]]),
                      key=lambda c: (c.get("prio", 9), c["id"]))
        if mine:
            L.append("- Open cards (`python scripts/dev/tasks.py brief <id>`):")
            L += [f"  - `{c['id']}` {c['state']} p{c.get('prio')} {c.get('lane')}: {c.get('title', '')[:110]}" for c in mine]
        else:
            L.append("- Open cards: none")
        L.append("")
    L += ["## Cross-cutting", ""] + [f"- {c['what']}: {c['where']}" for c in idx.get("cross_cutting", [])] + [""]
    return "\n".join(L)


def write(repo=REPO):
    """Regenerate LAYERS.md; returns the problem list (the page is written either way)."""
    idx, lmap, cards, reports = load(repo)
    (Path(repo) / SYS / "LAYERS.md").write_text(render(idx, lmap, cards, reports), encoding="utf-8", newline="\n")
    return problems(idx, lmap, repo)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        idx, lmap, _, _ = load()
        bad = problems(idx, lmap)
    else:
        bad = write()
        print(f"wrote {OUT.relative_to(REPO)}")
    for b in bad:
        print(f"LAYERS: {b}")
    if a.check and not bad:
        print("LAYERS: pointers ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
