# Artifact sync across Claude accounts

Artifacts and pins belong to one claude.ai account; nothing syncs them. Git does.
This folder is the single source of truth for every page we keep pinned.

## Rules
1. Every pinned page has its HTML here: `<slug>.html`. The repo copy wins.
2. `manifest.json` lists each page: slug, title, pinned, db collections, owner account,
   and the artifact URL on each account (`urls.desktop` = gmail account, `urls.cloud` = other account).
3. Edit the HTML here, ship (`sync.py ship`), then on EACH account a session runs:
   publish `<slug>.html` to that account's URL from the manifest (or publish new, record the URL), pin if `pinned: true`.
4. Pages with a database (`db` non-empty, e.g. Control Room inbox) have ONE owner account.
   The other account's copy is read-only reference; don't write inbox/decisions there.
5. Unpin anything on either account that isn't `pinned: true` here.

## Session prompt (paste into any account to align it)
```
Align artifacts with MyTradingSys/system/artifacts/manifest.json: for each entry, publish <slug>.html
to this account's URL (urls.<account>; empty = publish new and record URL in manifest), pin if pinned,
unpin anything else pinned. If an entry has no .html yet and this account owns it, read the artifact
and save its HTML here first. Ship via sync.py.
```

## Status 2026-10-09
- Desktop (gmail) account: the 3 pinned pages are not on this account; its 6 old artifacts were unpinned.
- Owner (cloud) account saved the 3 HTML files and URLs (html_saved: true). Desktop account aligned 2026-10-09: all 3 published + pinned (Control Room as read-only mirror, no db).
- Control Room db collections are `decisions` and `feedback` (not `inbox`).
