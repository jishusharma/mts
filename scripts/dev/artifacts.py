"""Artifact registry: one list of every claude.ai page we keep, so every account shows the same pages at the same links.

  python scripts/dev/artifacts.py check                     # registry is consistent with the repo (gate step)
  python scripts/dev/artifacts.py list                      # table: page, status, urls, last published
  python scripts/dev/artifacts.py plan --account jishu.sharma   # what a session on that account must publish / pin / record
  python scripts/dev/artifacts.py build                     # regenerate every page that has a generator in this repo
  python scripts/dev/artifacts.py stale                     # STALE <slug> <url> for each page whose repo build differs from what was last published
  python scripts/dev/artifacts.py publish-record --slug X [--date YYYY-MM-DD] [--ship]   # --ship commits+ships registry.json itself; after an Artifact publish: store published_sha + the publish date (default today)
  python scripts/dev/artifacts.py stamp --file page.html   # put "Updated <UTC>" first on a built page (build does it for generated pages)
  python scripts/dev/artifacts.py republish                 # REPUBLISH <slug> <html> <url> for each stale page (publisher login only; --all: any login)
  python scripts/dev/artifacts.py banner --slug research_map [--file live.html]   # insert/refresh the "Part of MTS Home" line
  python scripts/dev/artifacts.py audit-links               # audit registry vs repo copy and verify relative links across pages

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
import time
from collections import namedtuple
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
REG = REPO / "MyTradingSys" / "system" / "artifacts" / "registry.json"
STALE_CACHE_TIMEOUT_S = 180     # OURS: the background refresh of the hook cache dies after this
STATUSES = ("canonical", "retire", "needs-url")
URL_PREFIX = "https://claude.ai/artifact/"


BANNER_START, BANNER_END = "<!--mts-home:start-->", "<!--mts-home:end-->"
STAMP_START, STAMP_END = "<!--mts-stamp:start-->", "<!--mts-stamp:end-->"
STAMP_RE = re.compile(re.escape(STAMP_START) + ".*?" + re.escape(STAMP_END), re.S)
# registry account of each login letter (CLOUD_ACCOUNTS.md LOGINS); a session publishes only when its account is in registry["publishers"]
LOGIN_ACCOUNT = {"A": "jishu.sharma", "B": "jishu.awgp", "C": "jishusharma1985"}


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


def stamp_block(now=None):
    """The 'Updated <UTC> · <IST>' line every generated page shows first (operator 2026-11-07 pages follow builds; 2026-11-13 both zones, one clock)."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    ist = now + timedelta(hours=5, minutes=30)           # IST has no DST: a fixed +05:30 from the same instant
    style = "margin:0;padding:6px 14px;font:600 .8rem/1.4 ui-monospace,Consolas,monospace;color:var(--muted,#666)"
    return (f'{STAMP_START}{chr(10)}<p class="mts-updated" style="{style}">Updated {now.strftime("%Y-%m-%d %H:%M")} UTC'
            f' · {ist.strftime("%H:%M")} IST{"" if ist.date() == now.date() else " " + ist.strftime("%d %b")}</p>{STAMP_END}')


def put_stamp(text, now=None):
    """Insert or refresh the stamp: between its markers, else right after <body ...>, else before the first <main>/<div class=wrap>, else at the very top."""
    b = stamp_block(now)
    if STAMP_START in text:
        return STAMP_RE.sub(lambda m: b, text, count=1)
    m = re.search(r"<body[^>]*>", text, re.I)
    if m:
        return text[:m.end()] + b + text[m.end():]
    m = re.search(r'<main|<div class="wrap"', text)      # a page with no <body>: before its first wrapper, after <title>/<style>
    return text[:m.start()] + b + text[m.start():] if m else b + text


def write_stamped(path, text, now=None):
    """Write a built page with its Updated stamp; when the content (stamp, DATA generated time, publish dates blanked) equals the file already
    there, keep the file's stamp so a rebuild with no change leaves the tree clean (the minute alone dirtied it on every build)."""
    path = Path(path)
    new = put_stamp(text, now)
    try:
        old = path.read_text(encoding="utf-8")
    except OSError:
        old = None
    if old is not None and content_hash(old) == content_hash(new):
        return False
    path.write_text(new, encoding="utf-8", newline=chr(10))
    return True


def publishers(reg):
    return list(reg.get("publishers") or [])


def is_publisher(reg, letter):
    """True when login letter A/B/C maps to an account listed in registry publishers."""
    return LOGIN_ACCOUNT.get(str(letter or "").strip().upper()[:1], "\0") in publishers(reg)


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
    for a in publishers(reg):
        if a not in accounts:
            p.append(f"publishers: {a!r} is not an account")
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
        if account in (pg.get("deleted") or {}):   # the operator deleted this copy; the url stays as a record
            out.append(f"  DELETED      {pg['title']}  {u}  (operator, {pg['deleted'][account]})")
            continue
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
VOLATILE = re.compile(r'"(?:generated|commit|pub)":\s*"[^"]*"|"(?:[a-z_]*age_h|minutes)":\s*-?[0-9.]+|"behind":\s*(?:true|false)')


def content_hash(text):
    """sha256 of the page html with the DATA `generated` stamp, the 'Updated' stamp and `commit` sha blanked (a rebuild alone is not a change)."""
    text = STAMP_RE.sub("", text)
    return hashlib.sha256(VOLATILE.sub(lambda m: m.group(0).split(":")[0] + ': ""', text).encode("utf-8")).hexdigest()


def repo_html(pg, repo=REPO):
    return (Path(repo) / pg["html"]).read_text(encoding="utf-8")


def generated_only(pg):
    """A page with no repo html whose generator is a .py in this repo (sim_desk): it exists only as build output."""
    g = pg.get("generator") or ""
    return not pg.get("html") and g.endswith(".py") and "(" not in g


def build_html(pg, repo=REPO):
    """The page as the repo would build it now, in a temp file: generator output, else the hand-made html file."""
    g = pg.get("generator") or ""
    if not (g.startswith("scripts/") or generated_only(pg)):
        return repo_html(pg, repo)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "page.html"
        subprocess.run([sys.executable, str(Path(repo) / g), "--out", str(out)], check=True, capture_output=True, creationflags=(0x08000000 if sys.platform == 'win32' else 0))
        return out.read_text(encoding="utf-8")


def tracked(reg):
    """Pages that are live on their owner's login and have repo html: the ones that can lag the repo."""
    return [pg for pg in reg["pages"] if pg["status"] == "canonical" and (pg.get("html") or generated_only(pg)) and pg["urls"].get(owner(pg))]


def feed_pages(reg):
    """Canonical pages on their owner's login that declare `feeds` (input paths/globs) or `max_age_h`: the pages whose DATA can go old
    while the repo build hash stays the same (the hash check alone never flagged cbp_analyst_desk, buy_crypto or the live page)."""
    return [pg for pg in reg["pages"] if pg["status"] == "canonical" and pg["urls"].get(owner(pg)) and (pg.get("feeds") or pg.get("max_age_h"))]


def feed_files(pg, repo=REPO):
    """Existing files behind a page's `feeds`: absolute, ~ or repo-relative paths, globs allowed. A feed that is absent on this machine is skipped."""
    import glob
    out = []
    for f in pg.get("feeds") or []:
        f = str(Path(f).expanduser()) if f.startswith("~") else f
        pat = f if Path(f).is_absolute() else str(Path(repo) / f)
        out += [Path(x) for x in glob.glob(pat) if Path(x).is_file()]
    return out


def published_at(pg):
    """UTC time of the last publish: `published_at` (set by publish-record), else the start of the `last_published` day (conservative)."""
    pa = pg.get("published_at")
    try:
        if pa:
            return datetime.fromisoformat(pa.replace("Z", "+00:00"))
        return datetime.fromisoformat(pg["last_published"][owner(pg)]).replace(tzinfo=timezone.utc)
    except (ValueError, KeyError, TypeError):
        return None


REG_RECORD_FIELDS = ("published_at", "published_sha", "last_published", "feed_hashes")


def feed_hash(path):
    """sha256 of a feed file's bytes, volatile stamps blanked as content_hash does. A registry.json feed (MTS Home) is hashed with the fields
    publish-record rewrites blanked, so recording a publish never re-stales the page that lists the registry."""
    raw = Path(path).read_bytes()
    if Path(path).name == "registry.json":
        try:
            d = json.loads(raw.decode("utf-8"))
            for pg in d.get("pages", []):
                for k in REG_RECORD_FIELDS:
                    pg.pop(k, None)
            return hashlib.sha256(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()
        except (ValueError, AttributeError):
            pass
    return content_hash(raw.decode("utf-8", "replace"))


def feed_key(f, repo=REPO):
    """Machine-independent key for a feed file (the registry is shared through git): repo-relative when inside the repo."""
    try:
        return Path(f).resolve().relative_to(Path(repo).resolve()).as_posix()
    except ValueError:
        return Path(f).as_posix()


def feed_hashes(pg, repo=REPO):
    return {feed_key(f, repo): feed_hash(f) for f in feed_files(pg, repo)}


def feed_reasons(pg, now=None, repo=REPO):
    """Why a feed page is stale: a feed whose content hash differs from the one stored at publish-record (mtime alone never counts; a page
    with no stored hashes falls back to feed mtime), or the last publish older than `max_age_h`. [] = current."""
    now = now or datetime.now(timezone.utc)
    pub, why = published_at(pg), []
    if pub is None:
        return ["no publish time recorded"]
    files = feed_files(pg, repo)
    stored = pg.get("feed_hashes")
    if files and stored is not None:
        changed = [f for f in files if stored.get(feed_key(f, repo)) != feed_hash(f)]
        if changed:
            why.append(f"feed {changed[0].name} content changed since the last publish")
    elif files:
        newest = max(files, key=lambda f: f.stat().st_mtime)
        fresh = datetime.fromtimestamp(newest.stat().st_mtime, timezone.utc)
        if (fresh - pub).total_seconds() > 2:     # published_at is whole seconds; a feed written in the same second is not newer
            why.append(f"feed {newest.name} is newer than the last publish ({fresh:%Y-%m-%d %H:%M}Z > {pub:%Y-%m-%d %H:%M}Z)")
    age = (now - pub).total_seconds() / 3600
    if pg.get("max_age_h") and age > float(pg["max_age_h"]):
        why.append(f"last publish {age:.0f} h ago, over max_age_h {pg['max_age_h']}")
    return why


def stale(reg, builder=build_html, now=None, repo=REPO):
    """[(slug, url, reason)] for each page whose repo build hash differs from published_sha, or whose feed is newer than its last publish,
    or which is older than max_age_h (root cause A, 2026-11-13)."""
    out, seen = [], set()
    for pg in tracked(reg):
        sha = pg.get("published_sha")
        if not sha:
            out.append((pg["slug"], pg["urls"][owner(pg)], "no published_sha recorded"))
        elif content_hash(builder(pg)) != sha:
            out.append((pg["slug"], pg["urls"][owner(pg)], "repo build differs from last publish"))
        else:
            continue
        seen.add(pg["slug"])
    for pg in feed_pages(reg):
        why = feed_reasons(pg, now, repo)
        if why and pg["slug"] in seen:
            out = [(s, u, w + "; " + "; ".join(why)) if s == pg["slug"] else (s, u, w) for s, u, w in out]
        elif why:
            out.append((pg["slug"], pg["urls"][owner(pg)], "; ".join(why)))
    return out


def stale_lines(reg, builder=build_html):
    return [f"STALE {s} {u}  ({why})" for s, u, why in stale(reg, builder)]


def publish_source(pg):
    """What a session publishes for this page: `publish_file` (a built file outside the repo), else the repo html, else the generator."""
    return pg.get("publish_file") or pg.get("html") or pg.get("generator")


def republish_lines(reg, builder=build_html):
    """One `REPUBLISH <slug> <file> <url>` line per stale page: <file> is publish_file, the repo html, or the generator for a page that exists only as build output."""
    out = []
    for s, u, _why in stale(reg, builder):
        pg = next(p for p in reg["pages"] if p["slug"] == s)
        out.append(f"REPUBLISH {s} {publish_source(pg)} {u}")
    return out


def producer_lines(reg, producer):
    """`REPUBLISH <slug> <file> <url>` for every canonical page whose registry `producer` is this one: a producer calls it when it finishes
    (cbp_run.py at the end of a run, buy_crypto.py after its feed), so a finished run names its pages (root cause C)."""
    return [f"REPUBLISH {pg['slug']} {publish_source(pg)} {pg['urls'][owner(pg)]}"
            for pg in reg["pages"] if pg["status"] == "canonical" and producer in ([pg["producer"]] if isinstance(pg.get("producer"), str) else pg.get("producer") or [])
            and pg["urls"].get(owner(pg))]


def behind(reg, pg, repo=REPO):
    """MTS Home badge: the repo html on disk differs from what was last published (no generator run, so Home can build itself)."""
    try:
        html = build_html(pg, repo) if generated_only(pg) else repo_html(pg, repo)
        return content_hash(html) != pg.get("published_sha")
    except (OSError, subprocess.CalledProcessError):
        return True


def publish_record(reg, slug, today=None, repo=REPO, now=None):
    pg = next((p for p in reg["pages"] if p["slug"] == slug), None)
    if not pg or not (pg.get("html") or generated_only(pg) or pg.get("feeds") or pg.get("max_age_h")):
        raise SystemExit(f"artifacts: no page {slug!r} with repo html, a buildable generator, or feeds")
    now = now or datetime.now(timezone.utc)
    if pg.get("html") or generated_only(pg):
        pg["published_sha"] = content_hash(build_html(pg, repo) if generated_only(pg) else repo_html(pg, repo))
    pg["last_published"][owner(pg)] = today or now.date().isoformat()
    pg["published_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    if pg.get("feeds"):
        pg["feed_hashes"] = feed_hashes(pg, repo)
    return pg.get("published_sha") or "(feed page, no sha)"


def ship_records(slugs, run=subprocess.run, repo=REPO):
    """Commit and ship ONLY registry.json after publish-record, so a publish record never sits uncommitted in a scratch tree
    (2026-11-13: stale kept listing pages that were already republished). Returns the ship exit code."""
    reg = str(REG.relative_to(repo)) if REG.is_absolute() else str(REG)
    msg = "Pages republished: publish records for " + ", ".join(slugs) + chr(10)*2 + "Result: registry publish records current" + chr(10) + "Next: END: records only"
    git = lambda *a: run(["git", "-C", str(repo), *a], capture_output=True, text=True)
    git("add", "--", reg)
    if git("diff", "--cached", "--quiet", "--", reg).returncode == 0:
        return 0
    if git("commit", "-m", msg, "--", reg).returncode != 0:
        return 1
    return run([sys.executable, str(Path(repo) / "scripts" / "dev" / "sync.py"), "ship"], cwd=str(repo)).returncode


def cmd_build(reg):
    for pg in reg["pages"]:
        g = pg.get("generator") or ""
        if g.startswith("scripts/") and pg["status"] != "retire":
            print("build", pg["slug"])
            subprocess.run([sys.executable, str(REPO / g), "--out", str(REPO / pg["html"])], check=True, creationflags=(0x08000000 if sys.platform == 'win32' else 0))
            f = REPO / pg["html"]
            write_stamped(f, f.read_text(encoding="utf-8"))   # the generator already stamped; no-op unless it did not


class AuditRow(namedtuple("AuditRow", ["page", "link", "target", "status"])):
    def __getitem__(self, item):
        if isinstance(item, str):
            return getattr(self, item)
        return super().__getitem__(item)

    def get(self, key, default=None):
        return getattr(self, key, default)


def format_audit_table(rows):
    cols = ["PAGE", "LINK", "TARGET", "STATUS"]
    if not rows:
        return "PAGE                 LINK                 TARGET               STATUS"
    widths = [len(c) for c in cols]
    for r in rows:
        widths[0] = max(widths[0], len(str(r.page)))
        widths[1] = max(widths[1], len(str(r.link)))
        widths[2] = max(widths[2], len(str(r.target)))
        widths[3] = max(widths[3], len(str(r.status)))
    header = f"{cols[0]:<{widths[0]}}  {cols[1]:<{widths[1]}}  {cols[2]:<{widths[2]}}  {cols[3]:<{widths[3]}}"
    lines = [header]
    for r in rows:
        lines.append(f"{str(r.page):<{widths[0]}}  {str(r.link):<{widths[1]}}  {str(r.target):<{widths[2]}}  {str(r.status):<{widths[3]}}")
    return "\n".join(lines)


def audit_links(reg, repo=REPO, fetcher=None, reader=None):
    """Checks registry vs repo copy (which is newer?), opens/verifies markdown relative links across registered pages,
    and returns a list of AuditRow(page, link, target, status). Injectable fetcher/reader for testing.
    """
    rows = []

    def read_file(path_str):
        if reader is not None:
            if callable(reader):
                try:
                    return reader(path_str)
                except (FileNotFoundError, KeyError, OSError):
                    return None
            elif isinstance(reader, dict):
                norm = str(path_str).replace("\\", "/")
                for k, v in reader.items():
                    if norm.endswith(k) or norm == k:
                        return v
                return None
        p = Path(path_str)
        if not p.is_absolute():
            p = Path(repo) / p
        if p.is_file():
            try:
                return p.read_text(encoding="utf-8")
            except OSError:
                return None
        return None

    def check_link_target(target, base_dir):
        clean_target = target.split("#")[0].split("?")[0].strip()
        if not clean_target:
            return "OK"
        if clean_target.startswith(("http://", "https://")):
            if fetcher is not None:
                try:
                    res = fetcher(clean_target) if callable(fetcher) else fetcher.get(clean_target)
                    return "OK" if res is not False and res is not None else "BROKEN"
                except Exception:
                    return "BROKEN"
            return "OK"

        # Relative path
        target_path = Path(clean_target)
        if not target_path.is_absolute():
            resolved = base_dir / target_path
        else:
            resolved = target_path

        resolved_str = str(resolved).replace("\\", "/")
        norm_clean = str(clean_target).replace("\\", "/")

        if reader is not None:
            c = read_file(resolved_str)
            if c is None:
                c = read_file(norm_clean)
            return "OK" if c is not None else "BROKEN"

        if fetcher is not None:
            try:
                res = fetcher(clean_target) if callable(fetcher) else fetcher.get(clean_target)
                if res is None:
                    res = fetcher(resolved_str) if callable(fetcher) else fetcher.get(resolved_str)
                return "OK" if res is not False and res is not None else "BROKEN"
            except Exception:
                return "BROKEN"

        # Check local disk
        if resolved.exists() or (Path(repo) / clean_target).exists():
            return "OK"
        return "BROKEN"

    for pg in reg.get("pages", []):
        slug = pg["slug"]
        file_key = pg.get("html") or pg.get("markdown") or pg.get("file") or pg.get("path")
        content = None
        base_dir = Path(repo)
        if file_key:
            base_dir = (Path(repo) / file_key).parent
            content = read_file(file_key)
            if content is None:
                content = read_file(str(base_dir / Path(file_key).name))

        # Check registry vs repo copy (which is newer?)
        if content is not None and file_key:
            sha = pg.get("published_sha")
            is_newer = False
            if not sha:
                is_newer = True
            elif content_hash(content) != sha:
                is_newer = True
            if is_newer:
                rows.append(AuditRow(page=slug, link="(repo copy)", target=file_key, status="NEWER_REPO_COPY"))

        # If content wasn't loaded from disk/reader, maybe fetcher can get it from URL
        if content is None and fetcher is not None and pg.get("urls"):
            u = pg["urls"].get(owner(pg)) or next((v for v in pg["urls"].values() if v), None)
            if u:
                try:
                    res = fetcher(u) if callable(fetcher) else fetcher.get(u)
                    if isinstance(res, str):
                        content = res
                except Exception:
                    pass

        # Opens/verifies markdown relative links across registered pages
        if content:
            # Remove <script> blocks to avoid matching JS template literals (e.g. ${esc(url)})
            clean_content = re.sub(r'<script\b[^>]*>.*?</script>', '', content, flags=re.S | re.I)
            seen_links = set()
            # 1. Markdown links: [text](target)
            for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', clean_content):
                link_text = m.group(1).strip()
                raw_target = m.group(2).strip()
                target = raw_target.split()[0] if raw_target else ""
                if not target or target.startswith(("#", "${", "javascript:")):
                    continue
                if (link_text, target) in seen_links:
                    continue
                seen_links.add((link_text, target))
                st = check_link_target(target, base_dir)
                rows.append(AuditRow(page=slug, link=link_text, target=target, status=st))

            # 2. HTML links: <a href="target">text</a>
            for m in re.finditer(r'<a\s+[^>]*?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', clean_content, re.S | re.I):
                target = m.group(1).strip()
                link_text = re.sub(r'<[^>]+>', '', m.group(2)).strip() or target
                if not target or target.startswith(("#", "${", "javascript:")):
                    continue
                if (link_text, target) in seen_links:
                    continue
                seen_links.add((link_text, target))
                st = check_link_target(target, base_dir)
                rows.append(AuditRow(page=slug, link=link_text, target=target, status=st))

    return rows


def cmd_audit_links(reg, repo=REPO, fetcher=None, reader=None):
    rows = audit_links(reg, repo=repo, fetcher=fetcher, reader=reader)
    print(format_audit_table(rows))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "list", "plan", "build", "banner", "stale", "publish-record", "audit-links", "stamp", "republish", "stale-cache"])
    ap.add_argument("--account", default="jishu.sharma")
    ap.add_argument("--slug", help="banner / publish-record: the registry page")
    ap.add_argument("--all", action="store_true", help="republish: print for any login, not only a publisher login")
    ap.add_argument("--file", help="banner / stamp: html to update in place (default: the page's repo html)")
    ap.add_argument("--date", help="publish-record: the day the page was last published (default today)")
    ap.add_argument("--ship", action="store_true", help="publish-record: commit and ship registry.json at once (no record left uncommitted)")
    a = ap.parse_args(argv)
    reg = load()
    if a.cmd == "audit-links":
        return cmd_audit_links(reg)
    if a.cmd == "banner":
        pg = next((p for p in reg["pages"] if p["slug"] == a.slug), None)
        if not pg:
            raise SystemExit(f"artifacts: no page {a.slug!r}")
        f = Path(a.file or REPO / pg["html"])
        f.write_text(put_banner(f.read_text(encoding="utf-8"), reg, a.slug), encoding="utf-8", newline="\n")
        print(f"banner: {a.slug} -> {f}")
        return 0
    if a.cmd == "stamp":
        f = Path(a.file or "")
        if not f.is_file():
            raise SystemExit("artifacts: stamp needs --file <existing html>")
        f.write_text(put_stamp(f.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        print(f"stamp: {f}")
        return 0
    if a.cmd == "stale-cache":      # the prompt hook's background refresh: slugs of stale pages -> --file (json), never raises
        import os
        import threading
        wd = threading.Timer(STALE_CACHE_TIMEOUT_S, lambda: os._exit(0))    # hard stop: a hung page build must not outlive its hook
        wd.daemon = True
        wd.start()
        try:
            f = Path(a.file)
            try:
                old = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                old = {}
            slugs = [s for s, _u, _w in stale(reg)]
            f.write_text(json.dumps({"at": time.time(), "key": REG.stat().st_mtime_ns, "slugs": slugs, "login": old.get("login", "")}),
                         encoding="utf-8", newline=chr(10))
        except Exception:
            pass
        return 0
    if a.cmd == "republish":
        import mts_signal
        if not a.all and not is_publisher(reg, mts_signal.login()):
            print("artifacts: this login is not a publisher (registry publishers); nothing to republish here")
            return 0
        lines = republish_lines(reg)
        print("\n".join(lines) if lines else "artifacts: no stale pages")
        return 0
    if a.cmd == "publish-record":
        sha = publish_record(reg, a.slug, today=a.date)
        REG.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"publish-record: {a.slug} published_sha={sha[:12] if len(sha) == 64 else sha}")
        return ship_records([a.slug]) if a.ship else 0
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
