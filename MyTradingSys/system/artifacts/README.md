# Artifact sync across Claude accounts

Artifacts and pins belong to one claude.ai account; nothing syncs them. Git does. `registry.json` (this folder) is the single list:
page, status, generator script, owner app, refresh cadence, url on each account, last published. It replaced manifest.json 2026-10-12.

## Rules
1. One page = one url per account. Always republish OVER that url (Artifact tool `url` = the account's url): the link stays current and the pin stays.
   Never publish a second copy of a page; a new page is a new registry row first.
2. Generated pages (`generator` is a script here) are rebuilt from the repo: `python scripts/dev/artifacts.py build`; nobody edits the HTML by hand.
   CBP pages come from the CBP daily workflow (CryptoScrapper tree); the repo HTML is a snapshot.
3. A page with a db (Control Room) keeps separate databases per account. Only one account should take Inbox/decisions (registry note).
4. A session cannot delete or unpin an artifact. `artifacts.py plan --account <account>` prints what that account's session must republish, publish new or record,
   and the OPERATOR lines (unpin, delete, archive) only Jis can do in the app.
5. `python scripts/dev/artifacts.py check` fails on a duplicate url, an unknown status, or a missing html or generator.

## Align an account (paste into a session on that account)
```
python scripts/dev/artifacts.py plan --account <jishu.awgp|jishu.sharma>
Do each REPUBLISH / PUBLISH NEW / RECORD URL line (read the Artifacts list for a missing url), update registry.json
(urls, last_published), `artifacts.py check`, ship via sync.py. Leave the OPERATOR lines to Jis.
```
