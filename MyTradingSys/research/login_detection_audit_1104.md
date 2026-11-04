# Login detection audit (2026-11-04)

Card: login-detection-reads-the-wrong-account-. Scope: scripts/dev/mts_signal.py, read only. No code change.
Evidence: code reading. The detected letter was not run on JIS-NUC (this check ran on JIS-NB). The account address is never printed here.

## Sources of the login letter, in order

1. Env MTS_LOGIN (login(), mts_signal.py L133-135). Wins over everything.
2. The home config file (L136-142): `oauthAccount.emailAddress` from `~/.claude.json`, or the path in env MTS_CLAUDE_JSON. Only the first match of OAUTH_EMAIL_RE (L110) is used.
3. The address maps to a letter through the LOGINS rows of CLOUD_ACCOUNTS.md (_letter_for, L117-127). Rows are keyed by full address, local part, or prefix.
4. Nothing matched: the letter is "" and the typed letter stands.

## ROOT CAUSE

- resolve_login (mts_signal.py L157-164) lets the detected letter beat the typed one. On a mismatch it prints `LOGIN MISMATCH` and uses the detected letter (L162-163).
- login() reads the home file, which is the command-line config. It is not the signed-in account of the running app session. When the file holds another sign-in, the detected letter is A while the app runs B. This matches the card: supervisor wait said A, the 2026-11-08 reset matches B.
- The wrong letter then reaches every signal path. The sender id uses it (who(), L168), login_line() prints it (L1067-1071), and the records carry it.
- The only override is env MTS_LOGIN, which login() checks first (L133). Nothing in the code tells the operator that the file is the source.

## PROPOSED FIX (for a later code card, not this one)

1. resolve_login (L157-164): when the typed letter and the file-detected letter differ, do not post under the file letter. Fail closed (safety rule): refuse the budget or wait post and say so in one line, or post with the typed letter and a `login_src=typed` note. Conservative default (OURS): refuse.
2. login() (L130-154): return the source with the letter (env, file, none) so the message names where the letter came from.
3. Tests, fail-first: point MTS_CLAUDE_JSON at a fixture whose oauthAccount maps to A, pass B, and assert that no record carries A. Also cover the env override and the no-match case.
4. Confirm on JIS-NUC before the fix: the letter from login() with MTS_LOGIN unset, read by the operator, and whether the app keeps its account somewhere other than the home file.
