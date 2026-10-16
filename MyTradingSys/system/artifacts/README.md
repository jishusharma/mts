# Artifact sync across Claude accounts

Artifacts and pins belong to one claude.ai account; nothing syncs them. Git does. `registry.json` (this folder) is the single list:
page, status, generator script, owner app, refresh cadence, url on each account, last published. It replaced manifest.json 2026-10-12.

## Rules
1. One page = one url per account. Always republish OVER that url (Artifact tool `url` = the account's url): the link stays current and the pin stays.
   Never publish a second copy of a page; a new page is a new registry row first.
2. Generated pages (`generator` is a script here) are rebuilt from the repo: `python scripts/dev/artifacts.py build`; nobody edits the HTML by hand.
   CBP pages come from the CBP daily workflow (CryptoScrapper tree); the repo HTML is a snapshot.
3. A page's db belongs to that one page (one url), not to a login: shared with edit access, all logins write the same db. Copies on other accounts had their own empty dbs, which is why there are no copies any more.
4. A session cannot delete or unpin an artifact. `artifacts.py plan --account <account>` prints what that account's session must republish, publish new or record,
   and the OPERATOR lines (unpin, delete, archive) only Jis can do in the app.
5. `python scripts/dev/artifacts.py check` fails on a duplicate url, an unknown status, or a missing html or generator.

## Which login, which page (DECISION OURS, 2026-10-16, mts-home)
**One copy of every page, at one url, owned by one login. MTS Home lists them all:** https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3 (pinned on jishusharma1985).

| Login | Owns (republish only these, over their url) |
|---|---|
| jishusharma1985 (HOME) | MTS Home (generated: `make_home.py`), MTS Research Map (db `requests`), MTS Session Planner (db `selection`) |
| jishu.sharma | MTS Control Room (Inbox + decisions db, q21), MTS Layers, Tom and Fabio deck, CBP Monday + Consensus desks (CBP routine) |
| jishu.awgp | nothing live: old copies only, listed on MTS Home under "Old copies to delete" |

Why jishusharma1985 is home: it runs the super sessions (Max budget), holds the Research Map requests db and the Planner. Checked 2026-10-16 with
`Artifact list` from a session on it: owns 9nqpZe, 2Ti4CG and 3 "Moved" stubs, cannot read Ep6gA5 (not shared yet). The Control Room stays on
jishu.sharma: moving it would split the Inbox (q21).

How it behaves (claude.ai, checked against the Artifact tool rules 2026-10-16):
- A page's database belongs to the page, not to a login. Shared with edit access, every login writes the SAME notes. Viewers cannot write.
- Pins are per login; pages are not copied. Pin MTS Home on each login.
- Sharing is the owner's Share menu: invite the other logins' emails (other accounts = guests), edit access. Claude cannot change sharing.
- A session on any login may republish a page only over its registry url and only when `Artifact read` says "writer". Not shared or not
  writer: leave the page alone and say so. NEVER publish without `url` (that makes a second copy), never write a Control Room db from
  another login (q21).
- Every page carries a "Part of MTS Home" banner (`artifacts.py banner --slug <slug>`, or the generator adds it). `check` fails when a
  `banner: true` page's repo html lacks it.
- Republishing a page with a db or user capability: omit `capabilities` (the stored declaration carries forward).

Session on a login that is not the page owner: `artifacts.py plan --account <login>` prints NO COPY lines with the live url.

### One-time checklist for a session on jishu.sharma (not done from here)
1. `python scripts/dev/artifacts.py build`, then republish MTS Control Room and MTS Layers over their jishu.sharma urls: both now carry the banner
   and the Control Room "Pages" table lists MTS Home, the Research Map and the Planner.
2. Tom and Fabio deck (Slides, no repo html) and the CBP desks (CBP routine, CryptoScrapper tree): add this line at the top on their next edit:
   "Part of MTS Home (https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3), the one list of every MTS page. Owner login: jishu.sharma. Any of
   your logins opens this same link once the owner has shared it with that login. Your notes: read only."
3. Operator (Share menu): share the Control Room, Layers, deck and both CBP desks with jishusharma1985 (edit access); on jishusharma1985 share
   MTS Home, Research Map and Planner with jishu.sharma (edit access).

## Align an account (paste into a session on that account)
```
python scripts/dev/artifacts.py plan --account <jishu.awgp|jishu.sharma>
Do each REPUBLISH / PUBLISH NEW / RECORD URL line (read the Artifacts list for a missing url), update registry.json
(urls, last_published), `artifacts.py check`, ship via sync.py. Leave the OPERATOR lines to Jis.
```
