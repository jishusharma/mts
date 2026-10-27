# TRANSCRIPT INVENTORY - v2 done vs total, per speaker

Task: 20261009-181324-transcript-inventory-tom-v2-done-vs-tota
Run: MTS-2026-10-10 (DSA), worktree mts-dsa
No download. Source: MyTradingSys/research/_archive/loose_2026-10/transcript_inventory_2026-10-09.md (regenerated this run),
gate scripts/dev/verify_extract_quotes.py run on every extracts/v2/tom/*_v2.md file.

## Table

| Speaker | raw files | v2 extracted | v2 gate | not extracted (v2) |
|---|---|---|---|---|
| Tom | 84 | 11 | 11/11 PASS | 26 (ids below) |
| Fabio | 8 | 0 | n/a | 8 (no v2 pass attempted) |
| Malkan | 4 | 0 | n/a | 4 |
| Tom channel (guest) | 13 | 0 | n/a | 7 |
| all | 109 | 11 | 11/11 PASS | 33 |

v2 ids present (all gate PASS, 0 problems each):
4MoNjEQ2Dd8, 5Ljfwvtktek, etg6j0JybfE, kXhIAug0Gh8, Of_wlv3xaZo, oPyUif2Zrtk, QClPWDJ-BrU,
ShYS_pD5cxQ, tS6ZEiHj8gQ, UrZ4vpHJ97g, WSCIURybK3U.

## Tom never-extracted ids (26)

uk4PZV59nYw, YYYuaetck_0, kKZCJui4S9U, viT_VzF5Fsw, Kg6sYKgtkrY, VOiy8mAALWA, 4VXpUjhKG2U,
lO-Iptd29t4, cw8LWQmec1E, 15JoLK0PbMU, 0CrkbfuIhkc, 1utSjHs_Mq8, 2xnNPIyHGQ4, gWjHq5UMisY,
UOBgXV20yCM, hQ8sOq67x5o, pgdmKLJ0hhA, qLnQan0KGmQ, yRvMW6lgN1o, zQTbdEweG3c, OUM9LYwL8eA,
and 5 more listed in the per-video table of the inventory file.

## Note

The earlier inventory (same file, previous run) showed Tom 5 v2; the tree now holds 11 and the file
was regenerated to match. Fabio, Malkan and the Tom-channel guests have no v2 extract; the task
scoped v2 to Tom, so they are counted and listed but not re-extracted here.