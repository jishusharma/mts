# B087 - pick_task re-picks the same row; two smaller flags

Status: CLOSED. Severity: MED. Opened 2026-10-03.

## Defect

Sub-item (a) re-pick loop. pick_task.py leaves a row QUEUED after
picking it. The next wake picks the same row again. Until the row
lands (status becomes LANDED), every wake re-composes the same
prompt and overwrites next_task.txt.

Sub-item (b) size header edited to satisfy a test. The
03_FILE_INDEX.md SIZE header was rewritten to a new number so
test_4 passes. The header is a claim, not a measurement; editing
the claim to fit the test inverts the check.

Sub-item (c) mts go <id> uses claude --name. --session-id expects
a UUID, which no operator types by hand. The naming convention for
a CL session started by mts go is not specified anywhere on disk.

## Evidence

Session MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher, own words:
  (a) Rows stay QUEUED after a pick, so the same row is re-picked
      each wake until it lands.
  (b) the 03_FILE_INDEX.md size header went from ~45KB to ~46KB
      so the integrity test passes with the three new rows
  (c) mts go <id> uses claude --name, because --session-id needs
      a UUID

## Fix (Claude decides mechanism)

  (a) candidate: pick_state.json records picks; a picked-but-unlanded
      row is skipped until an explicit reset or a status change in
      BUGS.md. pick_task.py reads its own pick_state.json.
  (b) candidate: SIZE header is computed by make_status, or removed
      from test_4 scope. Never rewrite a claim to fit a test.
  (c) candidate: mts go <id> requires a kebab slug; the CLI derives
      the session id from slug + current UTC, per SURFACE_POLICY
      section 4.

Claude to choose and document each.

## Receipt

(a) scripts/sched/pick_task.py:128 load_state, :137 held_row, :225 current_pick_id, main HOLD branch: pick_state.json, 6h cooldown (env MTS_PICK_COOLDOWN_H), one row offered at a time, state entry dropped when row stops being pickable. Tests: test_pick_task.py test_8_second_wake_holds_same_row, test_9_cooldown_expiry_repicks_never_starves, test_10_landed_row_leaves_state_and_next_row_is_offered, test_11_corrupt_state_never_blocks_a_pick, test_12_held_row_with_missing_prompt_is_recomposed. (b) 03_FILE_INDEX.md SIZE header now reads computed; MyTradingSys/tests/docs/test_integrity.py test_4_file_index_size_claim rejects a hand-kept KB figure and enforces a 100KB ceiling. (c) scripts/sched/go.py:23-34 slug derives MTS-<UTC>-CLI-BLD-<slug> per SURFACE_POLICY s4; tests test_go.py test_4_slug_derives_policy_session_id_and_rewrites_prompt, test_5_bad_slug_rejected_nothing_launched; pick_task slug capped at 20 chars (test_13_session_slug_within_20_chars).

# END
