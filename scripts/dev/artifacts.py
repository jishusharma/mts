"""Artifact registry: one list of every claude.ai page we keep, so every account shows the same pages at the same links.

  python scripts/dev/artifacts.py check                     # registry is consistent with the repo (gate step)
  python scripts/dev/artifacts.py list                      # table: page, status, urls, last published
  python scripts/dev/artifacts.py plan --account jishu.sharma   # what a session on that account must publish / pin / record
  python scripts/dev/artifacts.py build                     # regenerate every page that has a generator in this repo

Pages are republished over their existing url (Artifact tool: `url` = the account's url), which keeps the link and the pin.
A session cannot delete or unpin an artifact: `plan` prints those as a list for the operator.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
REG = REPO / "MyTradingSys" / "system" / "artifacts" / "registry.json"
STATUSES = ("canonical", "retire", "needs-url")
URL_PREFIX = "https://claude.ai/artifact/"


def load(path=REG):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def problems(reg, repo=REPO):
    p, accounts = [], list(reg["accounts"])
    seen = {}
    for pg in reg["pages"]:
        s = pg["slug"]
        if pg["status"] not in STATUSES:
            p.append(f"{s}: status {pg['status']!r} not one of {STATUSES}")
        for a, u in pg["urls"].items():
            if a not in accounts:
                p.append(f"{s}: unknown account {a}")
            if u and not u.startswith(URL_PREFIX):
                p.append(f"{s}: bad url for {a}: {u}")
            if u:
                if u in seen:
                    p.append(f"{s}: url {u} also used by {seen[u]}")
                seen[u] = s
        if pg["status"] == "canonical" and not any(pg["urls"].values()):
            p.append(f"{s}: canonical page with no url on any account")
        if pg["status"] == "needs-url" and any(pg["urls"].values()):
            p.append(f"{s}: has a url, status should be canonical")
        if pg.get("pointer_html") and not (Path(repo) / pg["pointer_html"]).is_file():
            p.append(f"{s}: pointer_html {pg['pointer_html']} missing")
        if pg.get("html") and not (Path(repo) / pg["html"]).is_file():
            p.append(f"{s}: html {pg['html']} missing")
        g = pg.get("generator") or ""
        if g.startswith("scripts/") and not (Path(repo) / g).is_file():
            p.append(f"{s}: generator {g} missing")
        for k in ("owner_app", "refresh", "last_published"):
            if k not in pg:
                p.append(f"{s}: no {k}")
    for a, rows in reg.get("unpinned_old", {}).items():
        for r in rows if isinstance(rows, list) else []:
            if r["url"] in seen:
                p.append(f"unpinned_old repeats registry url {r['url']}")
    return p


def plan(reg, account):
    if account not in reg["accounts"]:
        raise SystemExit(f"artifacts: account must be one of {list(reg['accounts'])}")
    out = [f"ACCOUNT {account}: align artifacts with registry.json, republish over the existing url, never publish a second copy."]
    for pg in reg["pages"]:
        u = pg["urls"].get(account, "")
        if pg.get("single_owner") and account != pg["single_owner"]:
            # one live copy only (operator 2026-10-15: no duplicate Control Room): other logins hold a pointer page, never a copy
            if u:
                out.append(f"  REPLACE      {pg['title']} <- {pg['pointer_html']} (pointer, no capabilities)  url={u}; OPERATOR: delete it from the app menu, then blank urls.{account}")
            else:
                out.append(f"  NO COPY      {pg['title']}: single copy on {pg['single_owner']}")
        elif pg["status"] == "retire":
            out.append(f"  OPERATOR UNPIN+DELETE  {pg['title']}  {u or '(not on this account)'}  ({pg['note']})")
        elif pg["status"] == "needs-url":
            out.append(f"  RECORD URL   {pg['title']}: read it from the Artifacts list, put it in registry.json urls.{account}")
        elif u:
            src = pg["html"] or "(no repo html: leave as is)"
            out.append(f"  REPUBLISH    {pg['title']} <- {src}  url={u}" + ("  [pin]" if pg["pinned"] else ""))
        elif not pg["html"] and not pg["generator"]:
            out.append(f"  NO COPY      {pg['title']}: authored in claude.ai, share the link from {', '.join(a for a, x in pg['urls'].items() if x)}")
        else:
            src = pg["html"] or "scripts/dev/make_* output"
            out.append(f"  PUBLISH NEW  {pg['title']} <- {src}; record the url in registry.json urls.{account}" + ("; pin" if pg["pinned"] else ""))
    olds = reg.get("unpinned_old", {}).get(account, [])
    for r in olds:
        out.append(f"  OPERATOR ARCHIVE?  {r['title']}  {r['url']}")
    return out


def cmd_list(reg):
    for pg in reg["pages"]:
        urls = " ".join(f"{a.split('.')[-1]}={u.rsplit('/', 1)[-1] or '-'}" for a, u in pg["urls"].items())
        print(f"{pg['slug']:20} {pg['status']:10} {'pin' if pg['pinned'] else '   '} {urls}  pub {pg['last_published']}")


def cmd_build(reg):
    for pg in reg["pages"]:
        g = pg.get("generator") or ""
        if g.startswith("scripts/"):
            print("build", pg["slug"])
            subprocess.run([sys.executable, str(REPO / g), "--out", str(REPO / pg["html"])], check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "list", "plan", "build"])
    ap.add_argument("--account", default="jishu.sharma")
    a = ap.parse_args(argv)
    reg = load()
    if a.cmd == "check":
        p = problems(reg)
        print("\n".join(p) if p else f"artifacts: {len(reg['pages'])} pages ok")
        return 1 if p else 0
    if a.cmd == "list":
        cmd_list(reg)
    elif a.cmd == "plan":
        print("\n".join(plan(reg, a.account)))
    else:
        cmd_build(reg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
