"""Artifact registry: one list of every claude.ai page we keep, so every account shows the same pages at the same links.

  python scripts/dev/artifacts.py check                     # registry is consistent with the repo (gate step)
  python scripts/dev/artifacts.py list                      # table: page, status, urls, last published
  python scripts/dev/artifacts.py plan --account jishu.sharma   # what a session on that account must publish / pin / record
  python scripts/dev/artifacts.py build                     # regenerate every page that has a generator in this repo
  python scripts/dev/artifacts.py stale                     # STALE <slug> <url> for each page whose repo build differs from what was last published
  python scripts/dev/artifacts.py publish-record --slug X [--date YYYY-MM-DD]   # after an Artifact publish: store published_sha + the publish date (default today)
  python scripts/dev/artifacts.py banner --slug research_map [--file live.html]   # insert/refresh the "Part of MTS Home" line

Pages are republished over their existing url (Artifact tool: `url` = the account's url), which keeps the link and the pin.
A session cannot delete or unpin an artifact: `plan` prints those as a list for the operator.
"""
import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
REG = REPO / "MyTradingSys" / "system" / "artifacts" / "registry.json"
STATUSES = ("canonical", "retire", "needs-url")
URL_PREFIX = "https://claude.ai/artifact/"


BANNER_START, BANNER_END = "<!--mts-home:start-->", "<!--mts-home:end-->"


def load(path=REG):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def owner(pg):
    return pg.get("single_owner") or next((a for a, u in pg["urls"].items() if u), "")


def home_url(reg):
    pg = next((p for p in reg["pages"] if p["slug"] == reg.get("home_slug")), None)
    return pg["urls"].get(owner(pg), "") if pg else ""


def banner(reg, slug):
    """The 'Part of MTS Home' line every page carries at its top (operator 2026-10-16: how to open it, explained on the page itself)."""
    pg = next(p for p in reg["pages"] if p["slug"] == slug)
    url = home_url(reg)
    link = (f'<a href="{html.escape(url)}" target="_blank" rel="noopener" style="color:var(--accent);font-weight:700">MTS Home</a>'
            if url else "<b>MTS Home</b>")
    style = ("display:block;margin:12px 0 0;padding:10px 14px;border:1px solid var(--line);border-radius:10px;"
             "background:var(--accent-soft);color:var(--ink);font-size:.92rem;line-height:1.5;max-width:75ch;overflow-wrap:anywhere")
    return (f'{BANNER_START}<aside class="mts-home" role="note" style="{style}">Part of {link}, the one list of every MTS page. '
            f'Owner login: <b>{html.escape(owner(pg))}</b>. Any of your logins opens this same link once the owner has shared it with that login. '
            f'Your notes: {html.escape(pg.get("notes_go_to", ""))}</aside>{BANNER_END}')


def put_banner(text, reg, slug, strict=True):
    """Insert or refresh the banner: between its markers, else before <main class="wrap" id="main">, else just inside the first <div class="wrap">."""
    b = banner(reg, slug)
    if BANNER_START in text:
        return re.sub(re.escape(BANNER_START) + ".*?" + re.escape(BANNER_END), lambda m: b, text, count=1, flags=re.S)
    main = '<main class="wrap" id="main">'
    if main in text:
        return text.replace(main, f'<div class="wrap" style="padding-block:0">{b}</div>\n{main}', 1)
    if '<div class="wrap">' in text:
        return text.replace('<div class="wrap">', '<div class="wrap">\n' + b, 1)
    if strict:
        raise SystemExit(f"artifacts: no place for the MTS Home banner in {slug}")
    return text  # a test fragment with no page wrapper


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
        for k in ("owner_app", "refresh", "last_published", "purpose", "notes_go_to"):
            if k not in pg:
                p.append(f"{s}: no {k}")
        if pg.get("single_owner") and pg["single_owner"] not in accounts:
            p.append(f"{s}: single_owner {pg['single_owner']} is not an account")
        if pg.get("banner") and pg.get("html") and (Path(repo) / pg["html"]).is_file() \
                and BANNER_START not in (Path(repo) / pg["html"]).read_text(encoding="utf-8"):
            p.append(f"{s}: html has no MTS Home banner (artifacts.py banner --slug {s})")
    # one hub, owned by the home login (DECISION 2026-10-16, access_model)
    if reg.get("home_login") not in accounts:
        p.append(f"home_login {reg.get('home_login')!r} is not an account")
    hub = next((pg for pg in reg["pages"] if pg["slug"] == reg.get("home_slug")), None)
    if not hub:
        p.append(f"home_slug {reg.get('home_slug')!r} names no page")
    elif hub.get("single_owner") != reg.get("home_login") or not home_url(reg):
        p.append(f"{hub['slug']}: the hub must be owned by home_login and have its url")
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
                live = pg["urls"].get(pg["single_owner"], "")
                out.append(f"  NO COPY      {pg['title']}: single copy on {pg['single_owner']} {live}; open that link (shared with this login), "
                           f"republish only over it and only with edit access (Artifact read says 'writer')")
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


# build timestamp / head sha, clock-derived ages, and the registry publish dates the Control Room embeds: they change on every build or record, not content
VOLATILE = re.compile(r'"(?:generated|commit|pub)":\s*"[^"]*"|"(?:[a-z_]*age_h|minutes)":\s*-?[0-9.]+')


def content_hash(text):
    """sha256 of the page html with the DATA `generated` stamp and `commit` sha blanked (a rebuild alone is not a change)."""
    return hashlib.sha256(VOLATILE.sub(lambda m: m.group(0).split(":")[0] + ': ""', text).encode("utf-8")).hexdigest()


def repo_html(pg, repo=REPO):
    return (Path(repo) / pg["html"]).read_text(encoding="utf-8")


def build_html(pg, repo=REPO):
    """The page as the repo would build it now, in a temp file: generator output, else the hand-made html file."""
    g = pg.get("generator") or ""
    if not g.startswith("scripts/"):
        return repo_html(pg, repo)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "page.html"
        subprocess.run([sys.executable, str(Path(repo) / g), "--out", str(out)], check=True, capture_output=True)
        return out.read_text(encoding="utf-8")


def tracked(reg):
    """Pages that are live on their owner's login and have repo html: the ones that can lag the repo."""
    return [pg for pg in reg["pages"] if pg["status"] == "canonical" and pg.get("html") and pg["urls"].get(owner(pg))]


def stale(reg, builder=build_html):
    """[(slug, url, reason)] for each tracked page whose build hash differs from published_sha."""
    out = []
    for pg in tracked(reg):
        sha = pg.get("published_sha")
        if not sha:
            out.append((pg["slug"], pg["urls"][owner(pg)], "no published_sha recorded"))
        elif content_hash(builder(pg)) != sha:
            out.append((pg["slug"], pg["urls"][owner(pg)], "repo build differs from last publish"))
    return out


def stale_lines(reg, builder=build_html):
    return [f"STALE {s} {u}  ({why})" for s, u, why in stale(reg, builder)]


def behind(reg, pg, repo=REPO):
    """MTS Home badge: the repo html on disk differs from what was last published (no generator run, so Home can build itself)."""
    try:
        return content_hash(repo_html(pg, repo)) != pg.get("published_sha")
    except OSError:
        return True


def publish_record(reg, slug, today=None, repo=REPO):
    pg = next((p for p in reg["pages"] if p["slug"] == slug), None)
    if not pg or not pg.get("html"):
        raise SystemExit(f"artifacts: no page {slug!r} with repo html")
    pg["published_sha"] = content_hash(repo_html(pg, repo))
    pg["last_published"][owner(pg)] = today or date.today().isoformat()
    return pg["published_sha"]


def cmd_build(reg):
    for pg in reg["pages"]:
        g = pg.get("generator") or ""
        if g.startswith("scripts/"):
            print("build", pg["slug"])
            subprocess.run([sys.executable, str(REPO / g), "--out", str(REPO / pg["html"])], check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "list", "plan", "build", "banner", "stale", "publish-record"])
    ap.add_argument("--account", default="jishu.sharma")
    ap.add_argument("--slug", help="banner / publish-record: the registry page")
    ap.add_argument("--file", help="banner: html to update in place (default: the page's repo html)")
    ap.add_argument("--date", help="publish-record: the day the page was last published (default today)")
    a = ap.parse_args(argv)
    reg = load()
    if a.cmd == "banner":
        pg = next((p for p in reg["pages"] if p["slug"] == a.slug), None)
        if not pg:
            raise SystemExit(f"artifacts: no page {a.slug!r}")
        f = Path(a.file or REPO / pg["html"])
        f.write_text(put_banner(f.read_text(encoding="utf-8"), reg, a.slug), encoding="utf-8", newline="\n")
        print(f"banner: {a.slug} -> {f}")
        return 0
    if a.cmd == "publish-record":
        sha = publish_record(reg, a.slug, today=a.date)
        REG.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"publish-record: {a.slug} published_sha={sha[:12]}")
        return 0
    if a.cmd == "stale":
        lines = stale_lines(reg)
        print("\n".join(lines) if lines else f"artifacts: no stale pages ({len(tracked(reg))} checked)")
        return 0
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
