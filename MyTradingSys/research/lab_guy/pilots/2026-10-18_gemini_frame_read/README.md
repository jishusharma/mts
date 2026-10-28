# Gemini image-reading pilot, 2026-10-18 (one pilot, not a measured catch rate)

Model: Gemini 3.8 Flash, low effort, headless `agy.exe --print ... --model gemini-3.8-flash-low`.
Images are passed by copying the frame into a scratch folder, running agy.exe with that folder as the working directory and naming the file in the prompt
("Open the image <name> in this folder"); only that folder is visible to the model. Two calls per frame: BLIND read (no claim shown) and VERIFY (a claim shown,
one field planted wrong in 6 of 7 cases; for k0zm the shown claim was the true stop 25310 with target 25206 instead of 25200).
Truth = our 2026-10-12 frame audit; null = audit says not visible (any number there is an invented value).
Results file (this folder): `hard_results_gemini-3.8-flash-low.json`. Frame images are not copied (source: F:/MTS/data/tom_videos/frames; may carry account data).

Frames (7): T6hDJcHrVBM_0520.jpg, T6hDJcHrVBM_0550.jpg, zQTbdEweG3c_0370.jpg, l8RZrBfzvp4_0190.jpg, SANOimk8M9o_0270.jpg, UOBgXV20yCM_0250.png, k0zm_1510_1720.png

## Findings
- Blind read mostly honest on the stop: null on T6hDJcHrVBM_0520, zQTbdEweG3c_0370, SANOimk8M9o_0270 (did not invent the ledger's 24220 stop).
  But on SANOimk8M9o_0270 (audit: nothing readable) it still returned position -1, entry 24229, target 24111: invented values in the other fields.
- One inferred value: T6hDJcHrVBM_0550 stop 24690 (audit: not readable; also what we inferred ourselves).
- One panel mix-up: k0zm_1510_1720.png blind stop 25349 (earlier 2-lot state, top panel); the later state (bottom panel) is 25310.
- Verify mode weak: confirmed stop 25400 on zQTbdEweG3c_0370 although its own blind read was null; confirmed target 25206 on k0zm_1510_1720.png although its blind
  read said 25200; on T6hDJcHrVBM_0520 it refuted the claim but also called the correct entry 24690 wrong. The 'unreadable' answer was used 0 times in 7 calls.
- Not done: Argon on the same 7 frames; a larger crop to settle 25200 vs 25206 and the 0550 stop (card `argon-blind-read-7-frames`).

Rules drawn from this: `MyTradingSys/system/roles/lab_guy.md`, section "Using Gemini (or any non-producer model) to read images".
