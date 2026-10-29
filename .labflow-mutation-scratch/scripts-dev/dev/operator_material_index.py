"""Local-only index of operator screenshots and notes on one machine.

Walks --roots, lists png/jpg and txt/md/docx files, tags topics by keyword,
takes a text snippet from txt/md/docx, writes JSONL to --out
(default F:/MTS/data/operator_material_index/<host>.jsonl, outside the repo).
Stdout prints counts only (the repo is public: no file names there).
Never copies files; never writes anywhere but --out.
DECISION (OURS): OCR not done; no counts file committed (scope_in lists none).
"""
import argparse
import json
import os
import re
import socket
import sys
import zipfile

IMG = {".png", ".jpg", ".jpeg"}
TXT = {".txt", ".md"}
DOC = {".docx"}
SKIP = {".git", "node_modules", "__pycache__", "$recycle.bin", "system volume information",
        "windows", "program files", "program files (x86)", "programdata", "appdata", ".venv", "venv"}
TOPICS = ["RSI", "divergence", "Malkan", "Krown", "Tom", "Fabio"]
_TOPIC_RE = {t: re.compile(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])", re.I) for t in TOPICS}
SNIPPET = 300


def tag(text):
    return [t for t in TOPICS if _TOPIC_RE[t].search(text)]


def docx_text(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return ""
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", "", xml)


def txt_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(20000)
    except Exception:
        return ""


def walk(roots):
    for root in roots:
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x.lower() not in SKIP]
            for fn in files:
                yield os.path.join(d, fn)


def build(roots):
    rows = []
    for p in walk(roots):
        ext = os.path.splitext(p)[1].lower()
        if ext in IMG:
            kind, text = "image", ""
        elif ext in TXT:
            kind, text = "note", txt_text(p)
        elif ext in DOC:
            kind, text = "docx", docx_text(p)
        else:
            continue
        try:
            size = os.path.getsize(p)
        except OSError:
            size = -1
        topics = tag(os.path.basename(p) + "\n" + text)
        snip = " ".join(text.split())[:SNIPPET]
        rows.append({"path": p, "kind": kind, "ext": ext, "size": size, "topics": topics, "snippet": snip})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--roots", nargs="+", required=True)
    ap.add_argument("--host", default=socket.gethostname().lower())
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    out = a.out or "F:/MTS/data/operator_material_index/%s.jsonl" % a.host
    rows = build(a.roots)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            r["host"] = a.host
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    tagged = sum(1 for r in rows if r["topics"])
    print("host=%s rows=%d tagged=%d %s" % (a.host, len(rows), tagged,
          " ".join("%s=%d" % kv for kv in sorted(kinds.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
