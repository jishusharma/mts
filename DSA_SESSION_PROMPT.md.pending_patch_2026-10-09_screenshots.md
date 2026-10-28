# Pending patch - DSA_SESSION_PROMPT.md (screenshots)

Target: DSA_SESSION_PROMPT.md
Anchor: section 0 rule list, immediately after rule 13 ("Direct mode only: run one bridge call ...").
Status: not applied. Reason: the prompt has a size budget and a conformance eval (slim boot 2026-10-09); apply with the other pending patches in one pass and re-run the eval.
Author: MTS-2026-10-09 screenshot intake session

Splice as rule 14 (about 700 bytes):

14. Screenshots. Chat keeps the pixels and nothing reaches the disk, so an image shown here is NOT saved. The first line of any reply that rests on an image says "SHOT NOT SAVED (chat has no disk)". Read it by methodology/screenshot_intake.md: classify it, then one claim row per chart claim (MATCH / MISMATCH / NOT_IN_DATA) checked against files you read yourself. Write the read as text to MyTradingSys/research/screenshots/<date>_<symbol>_<set>.md through AIRUN with `Shots: chat-only`, and file every MISMATCH and NOT_IN_DATA. If the image matters beyond this chat, ask the operator to paste it in a Code session or drop the file in runtime_data/screenshots/inbox/. Never describe an unsaved image as stored.

Context: on 2026-10-09 the operator asked whether every session knows an image is saved. Code sessions now learn it from a hook; DSA cannot, because a chat has no disk. This rule makes the gap visible instead of silent.
