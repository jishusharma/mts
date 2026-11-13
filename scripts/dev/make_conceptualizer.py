"""Conceptualizer page: every trading layer's concepts in one app (operator 2026-11-12: "turn these PPTs into an application called
Conceptualizer ... put them inside one application, something like the one-page simulator").

  python scripts/dev/make_conceptualizer.py              # writes MyTradingSys/system/artifacts/conceptualizer.html
  python scripts/dev/make_conceptualizer.py --out x.html

Read-only over the repo, zero model tokens. Data, none typed into the page by hand:
  MyTradingSys/research/conceptualizer/concepts.json    layers -> concepts (a new concept = one row)
  MyTradingSys/research/conceptualizer/diagrams/*.svg   one diagram per concept (the `diagram` field)
Registry row: conceptualizer. Publish with the Artifact tool over that url, then artifacts.py publish-record --slug conceptualizer.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artifacts as af  # noqa: E402  (stamp, MTS Home banner)

REPO = HERE.parents[1]
SRC = REPO / "MyTradingSys" / "research" / "conceptualizer"
TPL = HERE / "conceptualizer.tpl.html"
OUT = REPO / "MyTradingSys" / "system" / "artifacts" / "conceptualizer.html"
STATUSES = ("failed", "inconclusive", "promising", "untested")
FIDELITY = ("match", "simplified", "distorted", "untested")
TAGS = ("SOURCED", "OURS", "NOT_SEEN")  # NOT_SEEN = a slot of the trader's that no verified source states
SIZE = re.compile(r"\blots?\b|₹|\brupees?\b", re.I)  # public repo, context only: no position sizes in rows
NEEDED = ("id", "name", "who", "status", "quote", "rule", "ours", "params", "code", "fidelity", "support", "test", "sim", "ideas", "question")


def problems(data, src=SRC):
    """Every row the page cannot render, as text (empty list = ok)."""
    out = []
    for L in data.get("layers", []):
        seen = set()
        for c in L.get("concepts", []):
            cid = f"{L.get('id')}/{c.get('id')}"
            out += [f"{cid}: no {k}" for k in NEEDED if k not in c]
            if c.get("id") in seen:
                out.append(f"{cid}: duplicate id")
            seen.add(c.get("id"))
            if c.get("status") not in STATUSES:
                out.append(f"{cid}: status {c.get('status')!r} not one of {STATUSES}")
            if (c.get("fidelity") or [None])[0] not in FIDELITY:
                out.append(f"{cid}: fidelity grade not one of {FIDELITY}")
            for p in c.get("params", []):
                if len(p) != 3 or not p[2].startswith(TAGS):
                    out.append(f"{cid}: param {p!r} needs a SOURCED, OURS or NOT_SEEN tag")
                if SIZE.search(" ".join(map(str, p))):
                    out.append(f"{cid}: param {p[0]!r} carries a size word (lot, rupee)")
            d = c.get("diagram")
            if d and not (src / "diagrams" / d).is_file():
                out.append(f"{cid}: diagram {d} missing")
    return out


def load(src=SRC):
    data = json.loads((src / "concepts.json").read_text(encoding="utf-8"))
    bad = problems(data, src)
    if bad:
        raise SystemExit("conceptualizer: " + "; ".join(bad))
    for L in data["layers"]:
        for c in L["concepts"]:
            d = c.get("diagram")
            c["svg"] = lf((src / "diagrams" / d).read_text(encoding="utf-8")).strip() if d else ""
    return data


def lf(text):
    """LF line ends on every host, so a Windows checkout and CI build the same page hash."""
    return text.replace("\r\n", "\n")


def render(data):
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return af.put_banner(lf(TPL.read_text(encoding="utf-8")).replace("__DATA__", blob), af.load(), "conceptualizer", strict=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    af.write_stamped(out, render(load()))
    print(f"conceptualizer: wrote {out}")


if __name__ == "__main__":
    main()
