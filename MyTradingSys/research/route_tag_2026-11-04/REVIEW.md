# REVIEW: route-tag gate (blind read, code only)

Read: scripts/dev/route_audit.py, sync.py check_route_tags (806-826) and commit_pending (780-803), tasks.py route_next (1387-1404) and cmd_done, test_route_audit.py. Run: `pytest scripts/dev/test_route_audit.py` 11 passed; `route_audit.py check --days 2` 3 findings over 240 gated Result commits (1 NO-CARD `Super`, 2 STALE-CARD), so the check flags what it should on live history.

Answer to the card question: check flags every Result commit with no Next, a Next card with no file, and a Next card open and untouched 72 h+. check_route_tags refuses ships with no tag anywhere or a bad/missing-card tag, but it is looser and different in kind from check (D2, D3).

## Defects (file:line)
- D1 route_audit.py:28-29 EXEMPT_SUBJECT is too wide. It matches on subject prefix alone, with no path test and no word boundary on `claim `, `release `, `heartbeat `, `lane health`. Verified: `claim jumper fix`, `release notes parser`, `lane healthcheck rewrite`, `signals study: new edge` (via `signals?\b`) are all exempt even when they touch .py or RESULT.md. Any study commit titled "signal..." or "release..." skips the gate. Fix: require the subject prefix AND (bookkeeping paths only); drop `signals?\b`.
- D2 sync.py:816-818 one tag anywhere in the ship satisfies every commit; route_audit.py:104-109 (covered_by_later) needs same author, descendant, within 12 h. A ship with 5 results and one Next passes the gate, then check can still flag the earlier ones as UNTAGGED if the tag is from another author or older than 12 h (e.g. a merged multi-author ship). Gate and audit disagree; align (apply covered_by_later in the gate).
- D3 sync.py:811-814 the gate looks at every non-exempt commit (no Result requirement) while route_audit.py:119 audits only commits with a `Result:` line. A commit with no Result and no Next fails the gate; the same commit passes check. Gate stricter than audit in this direction, looser in D2.
- D4 sync.py:811 uses `origin/fast-track..HEAD` with no fetch. A stale origin ref makes already-shipped commits count as this ship's (false refuse) or hides nothing; fails closed, but the refusal text says nothing about a stale ref.
- D5 route_audit.py:55-58 parse_next accepts any token matching CARD_ID as a card: `END` (no colon), `none`, `todo`, `tbd`. Verified `END` -> ('card','END'). Fails closed only because no such file exists; if a card with that id is ever created it satisfies the gate. A card whose id equals a stage word (`research`) is read as the stage.
- D6 route_audit.py:144-145 / sync.py:824: a Next card in state `done`/`dropped` is accepted (and skipped by STALE-CARD). A Result routed to a card that is already closed is a dead end that passes. Gate does not check card state at all.
- D7 route_audit.py:137 seen_cards.setdefault reports STALE-CARD only for the first commit naming the card; later commits routing to the same stale card are not listed. Also the staleness clock is the last commit touching the file on ref, so any bookkeeping touch (claim, fold context) resets it without the card moving.
- D8 tasks.py:1404 `return value.strip()` stores the whole raw string for card/stage kinds (`gemini-x (review)`, `Research`) in c["next"], not the parsed token `val`; later readers (route_audit parse_next re-parses, others may not) see trailing prose. Store `val`.
- D9 tasks.py:1400-1403 new: id is `[:40]` of the slug; if that path already exists the code skips filing but returns the id, silently linking the Next to an unrelated existing card with a colliding 40-char prefix.
- D10 sync.py:788,799 commit_pending builds the commit before the tag is validated; a bad `--next` (e.g. `new:"x"`, which parse_next refuses without allow_new) creates the commit and only then check_route_tags refuses; a rerun with a fixed tag adds another commit. Validate the tag before committing. Also --result/--next with an embedded newline can inject extra `Next:` lines (no stripping of newlines).

## Exempt-list gaps
- Too wide: D1 subjects. EXEMPT_PATH (route_audit.py:31) is fine for cards/claims/LAYERS.md but a card-only commit can carry a real `Result:` for work (e.g. a result written into a card) and is never audited.
- Too narrow: none found for reverts (`Revert `/`revert ` both covered); `Merge ` is moot (--no-merges at :74).

## False positives
- Observed: NO-CARD `Super` (a `Next: Super ...` prose line parsed as a card id, route_audit.py:55 takes the first token), STALE-CARD for refined cards not touched 72 h that are simply queued. The first is a grammar false positive (prose after Next:).

## Test gaps (test_route_audit.py)
- No test of the D1 subjects, of the 12 h / author boundary in covered_by_later, of check_route_tags on a Result-less commit, of Next pointing to a done card, of `END` without colon, or of the route_next card/stage value stored (D8). `test_exempt` "tasks: refine" passes by path, not subject, so the subject branch for `task:` is untested.

VERDICT: 10 defects, none blocking the happy path; D1, D2 and D6 are the ones that let a Result ship without a real route.
