# Lab_Guy spec detail for card rv05-h2-position-line-evidence (2026-10-18, labguy-pass-b)

Full text of the items the card shortens (card item limit 400 chars). The card is the contract; this file is the detail.

## steps item 1

Write blind reads first. Rows = CSV file lines 33 (F8), 45 (F12), 47 (F12-m2), 49 (F13), 50 (F13-m1), header is line 1, fields = entry (position-line average) and stop. Extract the full-resolution frame at each cited chart time t from F:/MTS/data/fabio_videos/DyS79Eb92Ug.f398.mp4 with cv2.VideoCapture (cv2 present, no ffmpeg on NB; the lowres/ 960x540 sheets cannot settle small text), crop one panel per read into a scratch dir (not committed), and record row, field, frame_t, value or NULL in RV05_H2_READS.csv BEFORE opening the CSV values or the RV05 table (A-20261018-7: unreadable allowed, a number for an unreadable field is an invented value)

## steps item 2

Compare in code, not by eye. Status per row x field: KEPT (read within 0.25 pt, one NQ tick, of the CSV cell), CHANGED (this read agrees within 0.25 pt with one earlier read, RV05 report or AUDIT H1, and differs from the CSV cell), CONTESTED (all three reads differ; known cases: F12 entry CSV 25105.78 vs RV05 25105.18, F12-m2 stop 25098.75 vs 25098.25, F13 entry CSV 25106.50 vs line 25108.90), NOT_IN_DATA. This card's own read never settles a contested value (A-20261018-7 point 5): the CSV cell stays, the note says CONTESTED, and ONE desk row (desk.py post --target DSA-NUC, panel crops, blind, null allowed) asks a non-Claude reader

## steps item 3

Write the adjudication into the ledger .md (status table with frame times; F13 replacement entry, F12-m2 stop, partial-coverage 8 covered vs 10 open, label-denominator conventions explicit; DEFAULT (OURS): displayed position-line average outranks a label-derived value, the label-derived value stays in the note as cross-check) and apply CHANGED cells to the CSV with the frame time in the note

## steps item 4

check script check_rv05_h2.py (new, fabio_transfer/): every row x field has a status, every CHANGED cell has a frame time or NOT_IN_DATA, READS.csv has a reading (NULL allowed) per row x field, CHANGED count equals the number of CSV cells that differ from git HEAD

## done_when

5 rows x {entry, stop} = 10 fields each carry a status KEPT/CHANGED/CONTESTED/NOT_IN_DATA with frame time in the ledger .md; RV05_H2_READS.csv holds the blind reads (NULL where unreadable, no invented value); CHANGED cells are in the CSV with the frame time; CONTESTED fields keep the CSV value and name the desk row id; check_rv05_h2.py exits 0 and test_ledger_audit.py is green. Verify: content commit sha, git cherry origin/fast-track <sha> empty, git ls-tree shows the files.
