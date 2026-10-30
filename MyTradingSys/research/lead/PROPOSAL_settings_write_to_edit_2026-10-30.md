# Proposal (NOT applied): `~/.claude/settings.json` Write rules (operator-owned file)

Claude Code prints a warning per `Write(F:/...)` allow rule at every headless start (seen in the failed wake's err.log). The rule form for file changes is `Edit(...)`, which already covers Write; each `Write` line below already has an `Edit` twin, so the fix is to delete the six `Write` lines. No access is lost.

```diff
       "Edit(F:/CryptoScrapper/**)",
       "Edit(//f/CryptoScrapper/**)",
-      "Write(F:/CryptoScrapper/**)",
-      "Write(//f/CryptoScrapper/**)",
       "Read(F:/Interview Prep/**)",
       "Read(//f/Interview Prep/**)",
       "Edit(F:/Interview Prep/**)",
       "Edit(//f/Interview Prep/**)",
-      "Write(F:/Interview Prep/**)",
-      "Write(//f/Interview Prep/**)",
       "Read(F:/MTS/**)",
       "Read(//f/MTS/**)",
       "Edit(F:/MTS/**)",
       "Edit(//f/MTS/**)",
-      "Write(F:/MTS/**)",
-      "Write(//f/MTS/**)",
```

Apply by hand (or tell a session to): remove those six lines, keep the JSON valid. Also check other settings files (`.claude/settings.local.json` in each checkout) for `Write(` lines.
