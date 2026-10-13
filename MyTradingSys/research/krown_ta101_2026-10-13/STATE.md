# Krown TA 101 extraction - state (2026-10-13, written after the 2026-10-12 shutdown)

Playlist: TA 101 - Everything You Need To Know (PLPEz1q0esi3gEd4DMbaGwFf3uqwAY6vTU). 28 listed ids; 18 are hidden by YouTube
as unavailable (no title, no captions), so the reachable set is 18 videos.

DONE (8, transcripts + extracts, `verify_extract_quotes.py` PASS 0 problems on all 8):
6aA-P4Gvhrc, -NXzJs5JRks, UqAvU1loT_k, qEfES84jwwo, 14bxwxC8gBQ, _t_XIBrcjRk, 8MvxK_nxO-0, HhV4HI9p5Uw.

TODO (10, caption fetch stalled on YouTube rate limit 429 on 2026-10-13 10:30 local, nothing written):
hNfjyrJEytI fMRvOt26xcA 7IxfsuD2wCM kcMnnQr1VFg INOCBmqQupc vjzy_KxJ_y8 2ei4fj-Ba24 2-nG9bsMoPQ Aysdt7PBETQ LB3DRYxnA0A _JoJbu_Ug-A
(the last two are short, 256 s and 314 s.)

Retry (repo root of a work tree, a few hours after the last attempt; the fetch skips existing files, pauses 20 s per video):
`python scripts/dev/fetch_captions_timed.py --analyst Krown --out MyTradingSys/research/krown_ta101_2026-10-13/transcripts <ids>`
then extract each as the done ones (format: see extracts/extract_HhV4HI9p5Uw.md), run `verify_extract_quotes.py` on each.
If the host IP stays blocked, run the fetch from JIS-NB. Extraction is Sonnet work, one video per pass.
