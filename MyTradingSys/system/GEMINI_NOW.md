# GEMINI NOW (edge push, 2026-11-13 to 20:00Z)

Both Gemini accounts expire in about 24 h; run every card. NUC runs the flash set, the laptop runs the argon twins then the NK caption batches. Outputs land on `gemini-q/<id>` branches only; a Claude session reviews and ships.

## Laptop (JIS-LAPTOP, login A): paste this one line into a PowerShell window (it opens in system32, so it starts with cd)

```powershell
cd C:\MTS\mts-lenovo ; git fetch -q origin ; git merge -q --ff-only origin/fast-track ; python scripts/dev/gemini_queue.py run gemini-edge-hilega-formula-argon-1113:low:argon gemini-edge-mine-cbp-argon-1113:low:argon gemini-edge-mine-malkan-argon-1113:low:argon gemini-edge-mine-nk-argon-1113:low:argon gemini-edge-mine-tomfabio-argon-1113:low:argon gemini-edge-review-adx-di-argon-1113:low:argon gemini-edge-review-edge-hunt-argon-1113:low:argon gemini-edge-review-h3-ny-open-argon-1113:low:argon gemini-edge-review-live-aid-flags-argon-1113:low:argon gemini-edge-review-malkan-window-argon-1113:low:argon gemini-edge-review-pre-us-failed-break-argon-1113:low:argon gemini-edge-review-us-open-trader-argon-1113:low:argon gemini-edge-nk-batch5-1113:low:flash gemini-edge-nk-batch4-1113:low:flash gemini-edge-nk-batch3-1113:low:flash gemini-edge-nk-batch2-1113:low:flash gemini-edge-nk-batch1-1113:low:flash
```

## NUC (JIS-NUC): started by the desktop Claude session over the SSH gate, nothing to do.

Cards: `python scripts/dev/tasks.py list --lane CODEX --state ready` (29 `gemini-edge-*-1113`). A card another host claimed prints SKIP and the run moves on. NK batches need captions: they stop with NOT_IN_DATA.md while the fetch lock is on (NUC to 2026-11-16T14:21Z).
