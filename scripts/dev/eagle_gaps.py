"""Eagle_Eyes gap sweep: find missing pieces and broken links across every layer and backtest.

  python scripts/dev/eagle_gaps.py                # print the gap list
  python scripts/dev/eagle_gaps.py --write <md>   # also write the report (proof file)

Reads only hand-kept indexes (layer_index.json, layer_map.json, system/tasks/*.json) and checks the
files they point at exist on disk. Each gap has a kind, the object it belongs to and the missing link.
Kinds:
  PATH_MISSING      a spec/code/ledger/results/roadmap/module/report path that is not on disk
  LAYER_NO_BACKTEST a layer_map layer that no backtest row names
  BT_UNKNOWN_LAYER  a backtest row naming a layer that layer_map does not define
  BT_NO_REPORT      a backtest row with no report path
  BT_NO_VERDICT     a backtest row with no verdict
  BT_FIELD_NULL     a backtest row with a null fees/split/n field (fee-net and OOS cannot be checked)
  LAYER_NO_FAMILY   a layer that no family in layer_index.json owns
  FAMILY_NO_CODE    a family with no code pointer
  FAMILY_NO_CARD    a family with no open task card (nothing is moving it)
  CARD_DEAD_LAYER   an open card whose `layers` names an unknown family
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SYS = Path("MyTradingSys") / "system"
LINK_KEYS = ("spec", "code", "ledger", "results", "roadmap", "path")
CLOSED = {"done", "closed", "dropped", "cancelled", "wontfix", "shipped"}


def _paths(val):
    """Split a pointer field (str with ';' or list) into clean path strings."""
    items = val if isinstance(val, list) else [val]
    out = []
    for it in items:
        if not isinstance(it, str):
            continue
        for part in it.split(";"):
            p = re.sub(r"\s*\(.*\)\s*$", "", part.strip()).strip("` ")
            if p and ("/" in p or "." in p) and " " not in p:
                out.append(p)
    return out


def _exists(repo, p):
    p = p.split("#")[0].split(":")[0] if not re.match(r"^[A-Za-z]:", p) else p
    for base in (repo, repo / "MyTradingSys"):
        if any(ch in p for ch in "*?"):
            if list(base.glob(p)):
                return True
        elif (base / p).exists():
            return True
    if "/" not in p:  # bare file name: short form, found anywhere in the tree
        return any(True for _ in repo.rglob(p))
    return False


def load(repo):
    idx = json.loads((repo / SYS / "layer_index.json").read_text(encoding="utf-8"))
    lmap = json.loads((repo / SYS / "layer_map.json").read_text(encoding="utf-8"))
    cards = []
    for p in sorted((repo / SYS / "tasks").glob("*.json")):
        try:
            cards.append(json.loads(p.read_text(encoding="utf-8")))
        except (ValueError, OSError):
            cards.append({"id": p.stem, "_bad": True})
    return idx, lmap, cards


def gaps(repo=REPO):
    repo = Path(repo)
    idx, lmap, cards = load(repo)
    out = []
    add = lambda kind, obj, what: out.append((kind, obj, what))
    layers = {l["id"]: l for l in lmap.get("layers", [])}
    fams = idx.get("families", [])
    fam_ids = {f["id"] for f in fams}
    owned = {}
    for f in fams:
        for lid in f.get("layers") or []:
            owned[lid] = f["id"]
        for key in LINK_KEYS:
            for p in _paths(f.get(key)):
                if not _exists(repo, p):
                    add("PATH_MISSING", f"family:{f['id']}", f"{key} -> {p}")
        if not _paths(f.get("code")):
            add("FAMILY_NO_CODE", f"family:{f['id']}", "no code pointer")
    tested = set()
    for b in lmap.get("backtests", []):
        bid = f"backtest:{b.get('id')}"
        for lid in b.get("layers") or []:
            tested.add(lid)
            if lid not in layers:
                add("BT_UNKNOWN_LAYER", bid, f"layer {lid} not in layer_map layers")
        rep = _paths(b.get("report"))
        if not rep:
            add("BT_NO_REPORT", bid, "report is null")
        for p in rep:
            if not _exists(repo, p):
                add("PATH_MISSING", bid, f"report -> {p}")
        if not b.get("verdict"):
            add("BT_NO_VERDICT", bid, "verdict is null")
        for k in ("fees", "split", "n"):
            if b.get(k) in (None, ""):
                add("BT_FIELD_NULL", bid, f"{k} not recorded")
    for lid, l in layers.items():
        if lid not in tested:
            add("LAYER_NO_BACKTEST", f"layer:{lid}", "no backtest row names it")
        if lid not in owned:
            add("LAYER_NO_FAMILY", f"layer:{lid}", "no family owns it")
        for p in _paths(l.get("module")):
            if not _exists(repo, p):
                add("PATH_MISSING", f"layer:{lid}", f"module -> {p}")
    open_cards = [c for c in cards if str(c.get("state", "")).lower() not in CLOSED and not c.get("closed")]
    moved = set()
    for c in open_cards:
        cl = c.get("layers") or []
        cl = [cl] if isinstance(cl, str) else cl
        for fid in cl:
            if fid in fam_ids:
                moved.add(fid)
            else:
                add("CARD_DEAD_LAYER", f"card:{c.get('id')}", f"layers names unknown family {fid}")
    for f in fams:
        if f["id"] not in moved:
            add("FAMILY_NO_CARD", f"family:{f['id']}", "no open card names this family")
    return out


def render(found):
    from collections import Counter
    cnt = Counter(k for k, _, _ in found)
    L = ["# Eagle_Eyes gap sweep (generated by scripts/dev/eagle_gaps.py; do not hand-edit)", "",
         f"Total gaps: {len(found)}", "", "| kind | count |", "|---|---|"]
    L += [f"| {k} | {n} |" for k, n in sorted(cnt.items())]
    L += ["", "| kind | object | missing link |", "|---|---|---|"]
    L += [f"| {k} | `{o}` | {w} |" for k, o, w in sorted(found)]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write")
    ap.add_argument("--repo", default=str(REPO))
    a = ap.parse_args(argv)
    found = gaps(a.repo)
    for k, o, w in sorted(found):
        print(f"{k}\t{o}\t{w}")
    print(f"TOTAL {len(found)}")
    if a.write:
        Path(a.write).write_text(render(found), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
