# Report: gemini-tom-v1fresh-to-v2-1113

Task: gemini-tom-v1fresh-to-v2-1113
Date: 2026-11-12 (UTC)
Worker: gemini-3.8-flash-low

## Summary
Re-extracted 19 Tom Vorwald video IDs from V1-fresh format to V2 format with verbatim quotes verified against transcripts on disk (`raw_transcripts_canonical/<id>_raw.txt`).
All 19 files created in `extracts/v2/tom/<id>_v2.md` and verified with `python scripts/dev/verify_extract_quotes.py`.

## Verification Command & Results
Command:
```bash
python scripts/dev/verify_extract_quotes.py extracts/v2/tom/9eHZMVXilgc_v2.md extracts/v2/tom/C9n_d91Uitc_v2.md extracts/v2/tom/Fj4FDZQxw0I_v2.md extracts/v2/tom/KEe_CWHyuSg_v2.md extracts/v2/tom/OUM9LYwL8eA_v2.md extracts/v2/tom/T6hDJcHrVBM_v2.md extracts/v2/tom/UOBgXV20yCM_v2.md extracts/v2/tom/VumVuGnCcFM_v2.md extracts/v2/tom/dh-ysRR8f-M_v2.md extracts/v2/tom/e6Gm1n2h05M_v2.md extracts/v2/tom/l8RZrBfzvp4_v2.md extracts/v2/tom/rrHj24GSR6M_v2.md extracts/v2/tom/sQ_biBKhPVU_v2.md extracts/v2/tom/v5EuDl9c0iI_v2.md extracts/v2/tom/vk0mkNPuhDc_v2.md extracts/v2/tom/vl01TiVTuoQ_v2.md extracts/v2/tom/wPMiyJXL0zU_v2.md extracts/v2/tom/yRvMW6lgN1o_v2.md extracts/v2/tom/zQTbdEweG3c_v2.md
```
Output:
`PASS: 0 problem(s)` (Exit code: 0)

## Verified Files (SOURCED / verified)
1. `extracts/v2/tom/9eHZMVXilgc_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/9eHZMVXilgc_raw.txt:1`
2. `extracts/v2/tom/C9n_d91Uitc_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/C9n_d91Uitc_raw.txt:1`
3. `extracts/v2/tom/Fj4FDZQxw0I_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/Fj4FDZQxw0I_raw.txt:1`
4. `extracts/v2/tom/KEe_CWHyuSg_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/KEe_CWHyuSg_raw.txt:1`
5. `extracts/v2/tom/OUM9LYwL8eA_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/OUM9LYwL8eA_raw.txt:1`
6. `extracts/v2/tom/T6hDJcHrVBM_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/T6hDJcHrVBM_raw.txt:1`
7. `extracts/v2/tom/UOBgXV20yCM_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/UOBgXV20yCM_raw.txt:1`
8. `extracts/v2/tom/VumVuGnCcFM_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/VumVuGnCcFM_raw.txt:1`
9. `extracts/v2/tom/dh-ysRR8f-M_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/dh-ysRR8f-M_raw.txt:1`
10. `extracts/v2/tom/e6Gm1n2h05M_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/e6Gm1n2h05M_raw.txt:1`
11. `extracts/v2/tom/l8RZrBfzvp4_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/l8RZrBfzvp4_raw.txt:1`
12. `extracts/v2/tom/rrHj24GSR6M_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/rrHj24GSR6M_raw.txt:1`
13. `extracts/v2/tom/sQ_biBKhPVU_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/sQ_biBKhPVU_raw.txt:1`
14. `extracts/v2/tom/v5EuDl9c0iI_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/v5EuDl9c0iI_raw.txt:1`
15. `extracts/v2/tom/vk0mkNPuhDc_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/vk0mkNPuhDc_raw.txt:1`
16. `extracts/v2/tom/vl01TiVTuoQ_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/vl01TiVTuoQ_raw.txt:1`
17. `extracts/v2/tom/wPMiyJXL0zU_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/wPMiyJXL0zU_raw.txt:1`
18. `extracts/v2/tom/yRvMW6lgN1o_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/yRvMW6lgN1o_raw.txt:1`
19. `extracts/v2/tom/zQTbdEweG3c_v2.md`: 6 quotes (2 BEGIN, 2 MIDDLE, 2 END), verified against `raw_transcripts_canonical/zQTbdEweG3c_raw.txt:1`

Total verified quotes: 114 (OURS).
Total files: 19 (SOURCED: task prompt list).
