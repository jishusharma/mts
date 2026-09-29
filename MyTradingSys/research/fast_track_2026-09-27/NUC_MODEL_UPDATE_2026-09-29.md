# NUC worker model update, 2026-09-29 (updates WORKER_MODEL_RESEARCH.md of 2026-09-28)

Method: playbook tiers (T1 peer-reviewed/regulated, T2 replicated practitioner, T3 individual/community, REJECT unverifiable/marketing) applied to LLM
engineering. No T1/T2 sources exist for local-CPU LLM speed; everything below is T3 at best. Vendor-reported figures are tagged [VENDOR].
Only pages opened in this session are cited. Nothing here was run on the NUC. Baseline box (from WORKER_MODEL_RESEARCH.md): i7-10710U, 6C/12T, 31.8 GB.

## Recommendation
Keep qwen3-coder:30b as the sole worker for now, and PILOT exactly one challenger in the 3-task bake-off: **qwen3.6:35b (Q4_K_M, thinking OFF)**.
It is the same MoE shape (35B total / 3B active), Qwen's own card [VENDOR] shows a large coding gain (LiveCodeBench v6 80.4, SWE-bench Verified 73.4)
against the ~50 SWE-bench Verified that independent trackers report for qwen3-coder:30b. Risks: 23 GB weights leave ~8 GB for Windows+KV (tight, no
headroom for a second model), and it thinks by default (the exact gpt-oss failure mode), so thinking must be disabled and verified. No SWITCH is justified
until it passes the bake-off; no CPU tok/s figure for any challenger was found. The cheapest real win is not a new model: run llama-server directly with
`-ub 2048` / `--spec-type ngram-mod` (Q2 items 1-3), which targets the prompt-processing phase that dominates 2-6k-token tasks.

## Q1: candidates (released or updated in the last ~3 months unless noted)
| Model | Size / active | RAM (Q4) | Evidence (source tier) | CPU tok/s | Verdict |
|---|---|---|---|---|---|
| qwen3-coder:30b (baseline) | 30.5B / 3.3B | ~18.6 GB | SWE-bench Verified "50-52 under standard scaffolding", LiveCodeBench "40.3" (orcarouter blog, T3, secondhand); Qwen card claim 51.6 with OpenHands 100 turns [VENDOR], repro details requested but not given (HF discussion 30) | 12-15 (prior note) | baseline |
| qwen3.6:35b (Apr 2026, Ollama "updated 3 weeks ago") | 35B / 3B | Ollama tag 23 GB (incl. 0.9 GB vision projector); Unsloth UD-Q4_K_XL "23 GB" | HF card [VENDOR]: LiveCodeBench v6 80.4 vs 74.6 for Qwen3.5-35B-A3B; SWE-bench Verified 73.4 vs 70.0. Independent gist (T3, GPU, no LCB): SWE-V 73.4/Pro 49.5 quoted from vendor, notes "documented community performance regression" and 4-20 pts below 27B dense | none found (GPU 160 tok/s on 3090Ti is irrelevant) | PILOT (thinking off) |
| laguna-xs-2.1 (Poolside, 2026-07-02) | 33B / 3B | Ollama q4_K_M 20 GB | Poolside blog [VENDOR]: SWE-bench Multilingual 63.1 (from 57.7); SWE-V 70.9 appears only in a search snippet of a third-party page, not verified on the vendor page I opened. Ollama page: thinking model, macOS empty-output bug (irrelevant on Windows) | none found | PILOT-2 only if Qwen3.6 fails on RAM; thinking-by-default risk |
| Nemotron 3.5 Lightning (NVIDIA, 2026-08-11) | 30B / 3B hybrid Mamba-2 MoE | Unsloth: 4-bit "~20GB" | Only agentic PinchBench "86%" [VENDOR]; dev.to lists SWE-V 51.56 (T3, unverified secondhand). No code-gen benchmark that beats baseline | no CPU numbers | NO (no evidence) |
| Qwen3.8-27B (2026-08-14) | 27.8B dense | 17.7 GB | dev.to: LiveCodeBench v6 90.3 (secondhand, likely vendor). orcarouter (T3): "Qwen3.8-27B has no numbers of its own", "Vendor claims do not count" | ~7 tok/s on Mac mini M4 (dev.to, T3); dense 27B on a 10710U would be several-fold slower than MoE | NO (dense, CPU-hostile, unverified) |
| Devstral Small 2 24B | 24B dense | 15.2 GB | 68.0 SWE-V [VENDOR, from prior note] | dense, slow | NO (dense) |
| gpt-oss:20b | 21B MoE | ~13 GB | local bake-off: 1632 s, 7000 tokens all reasoning, empty reply | - | NO (measured) |
| GLM flash, Granite, Seed-Coder, Ling/Ring, DeepSeek small | - | - | Searched only via roundup pages; no source opened with numbers. Not evaluated | - | NOT VERIFIED (REJECT as evidence) |
Note: no "Qwen3.6-Coder" exists in what I found; the Ollama tag `qwen3.6:35b-coding` is a sampling-defaults variant, not a coder finetune (inferred from the tag page, which lists the same 35B Q4_K_M).

## Q2: tuning, ranked by (gain x confidence) / effort
1. **Bigger prompt batch (`-b 2048 -ub 2048`, llama-server) and run llama-server instead of Ollama.** Evidence: Ryzen 7 8745HS CPU-only Qwen3-30B-A3B, vanilla llama.cpp PP 63 / TG 22 tok/s; batch 2048 + flash-attn on the ik_llama.cpp fork reached PP 225 / TG 25 (ik_llama discussion 666, T3, one user, different CPU). i7-9750H laptop report: `-ub 2048` "huge speedup" to prefill (llama.cpp discussion, T3). Expected: prefill 2-3x on 4-6k prompts (prefill is likely the larger share of 200-350 s); TG unchanged. Effort medium (new server, queue tool must speak OpenAI API to :8080). Risk: batch sizes >2048 hurt MoE; Ollama `num_batch` is the same knob if you stay on Ollama (try 1024 then 2048).
   ```
   llama-server -m Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf -t 6 -tb 6 -c 16384 -b 2048 -ub 2048 -fa on --cache-type-k q8_0 --cache-type-v q8_0 --port 8080 --jinja
   ```
2. **Threads = 6 physical cores** (`-t 6 -tb 6`; Ollama `num_thread 6`). Evidence: guide result "SMT hurts performance" (search summary of llama.cpp guide, T3); prior note suggested 8, so bench 6/8/10 with `llama-bench -t 6,8,10`. Gain 0-30%, effort low, risk none. Ollama: set in Modelfile `PARAMETER num_thread 6`, `PARAMETER num_batch 1024`, `PARAMETER num_ctx 12288` (prompt + 8k output must fit).
3. **Draft-free speculative decoding for code edits: `--spec-type ngram-mod`** (llama.cpp speculative.md, official docs T2-ish: "Iterating over a block of text/code" benefits from ngram; "MoEs require long drafts" so raise `--spec-ngram-mod-n-max`). Helps rewrite/edit tasks that copy existing code (e.g. spec 126 rewrote a docstring); little on fresh code. Gain unquantified for this box; effort low once on llama-server; risk: rejected drafts cost extra verifications on CPU. Bench with and without. Ollama: v0.32.6 reportedly adds automatic MTP (nexgpu blog T3: "official figures not disclosed", models unspecified); it did not appear in the release notes I could see (v0.33.1-v0.40.0), so treat as unproven. MTP heads are documented for Qwen3.6 (Unsloth: `--spec-type draft-mtp --spec-draft-n-max 2`, "+78%" on an A10G GPU, runaihome T3), not for qwen3-coder; classic small-draft-model needs a compatible tiny Qwen3-Coder, and none was verified.
4. **Thinking off + strict prompting.** Qwen3-Coder is non-thinking only (HF card), so nothing to do; for Qwen3.6 use `--chat-template-kwargs "{\"enable_thinking\":false}"` (llama.cpp, PowerShell quoting from Unsloth) or Ollama API `"think": false`, then sampling temp 0.7 / top_p 0.8 / top_k 20 (Qwen card non-thinking) or 0.6 for precise code. Also keep OUTPUT_TOKENS above thinking budget. Gain: removes empty-reply failures; effort low.
5. **KV cache q8_0 is fine; keep it.** Evidence: "+0.004 perplexity" and "PPL 6.20 vs 6.19" (blog summaries, T3); q4_0 has a documented cliff (avoid). Only speed cost is per-token dequant at long context; at 2-6k it is negligible. Gain none; no change.
6. **Pin weights: `--mlock`** (llama-server) so Windows cannot page the 18 GB model out. Caveat: mlock implies mmap in new llama.cpp; a MoE user reported 25-27 -> 7.55 tok/s when the loading mode was wrong (search summary, T3). With 31.8 GB and 18 GB weights, keep-alive residency is already fine on Ollama; try only if first-token latency varies. Risk: on Qwen3.6 (23 GB) mlock could starve Windows.
7. **Unsloth dynamic quants (UD-Q4_K_XL) / IQ4_XS.** Unsloth page confirms UD-Q4_K_XL for Qwen3.6 needs 23 GB; no independent code-quality-vs-speed comparison was found. Gain unproven; skip until a challenger is chosen, then A/B against Q4_K_M in the bake-off.
8. **iGPU offload: NO.** The i7-10710U's integrated graphics (UHD, Gen9.5; from general knowledge, not verified this session) share the same DDR4 bandwidth that limits decode; no SYCL/Vulkan evidence was gathered. Not worth the effort.
9. **ik_llama.cpp fork** (fused MoE kernels, PP 63 -> 225 above). Largest reported prefill gain but the build was Zen4-specific clang; Windows/Intel AVX2 build effort and risk are high. Consider only if item 1 falls short.

Operator steps (RDP to JIS-NUC, Ollama route, safest first): `ollama show qwen3-coder:30b --modelfile > Q.modelfile`; append `PARAMETER num_thread 6`, `PARAMETER num_batch 1024`, `PARAMETER num_ctx 12288`; `ollama create qwen3-coder-t6 -f Q.modelfile`; run spec 128 (the 211 s task) via the queue against the new tag, compare wall-clock. For the challenger: `ollama pull qwen3.6:35b`, then send `"think": false` in the request options and confirm the reply contains no `<think>`.

## 3-task bake-off protocol (specs 126 / 128 / 129, Sonnet tests unchanged)
Baseline: 126 = 340 s 10/10, 128 = 211 s 10/10, 129 = 348 s 15/15 (MODEL_BAKEOFF.md).
1. Copy each spec, change only `MODEL:`, suffix output `_<tag>.py.new`; OUTPUT_TOKENS unchanged (non-thinking). One arm at a time, NUM_PARALLEL=1, model warm (run a 1-line prompt first so load time is excluded), nothing else scheduled on the NUC.
2. Arms: A = qwen3-coder-t6 (tuning only: Q2 items 1-2); B = qwen3.6:35b think off (Q4_K_M); C (optional) = llama-server with ngram-mod + `-ub 2048`.
3. Record wall-clock from the verify SUMMARY line, done_reason, eval tokens, raw tests passed (temp-dir copy), and hand-fixes needed (docstring loss counted as a defect). Watch free RAM (Task Manager) for paging; abort an arm at 900 s.
4. Decision rule: SWITCH to B only if tests >= baseline on all three AND no more hand-fixes AND wall-clock <= 1.3x baseline AND zero empty/thinking replies; keep tuning (A/C) if wall-clock improves >= 20% with equal tests; otherwise NO. Repeat any single failing task once to separate variance from real failure (n=3 is a smoke test, not statistics).

## Sources (tier; all opened this session)
- https://huggingface.co/Qwen/Qwen3.6-35B-A3B (T3 [VENDOR]: LCB v6 80.4, SWE-V 73.4, thinking default, sampling)
- https://ollama.com/library/qwen3.6:35b-coding (T3: 23 GB, Q4_K_M, thinking tag)
- https://unsloth.ai/docs/models/qwen3.6 (T3: 23 GB UD-Q4_K_XL, enable_thinking false, MTP flags)
- https://gist.github.com/hungson175/61a805368649c225026a69adf2ad87e0 (T3: independent GPU coding comparison; regression note)
- https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct (T3 [VENDOR]: non-thinking only, sampling) and .../discussions/30 (51.6 claim, repro missing)
- https://www.orcarouter.ai/blog/qwen-3-8-27b-vs-qwen3-30b-a3b (T3: SWE-V 50-52, LCB 40.3; Qwen3.8-27B unmeasured)
- https://poolside.ai/blog/introducing-laguna-xs-2-1 (T3 [VENDOR]); https://ollama.com/library/laguna-xs-2.1 (T3)
- https://unsloth.ai/docs/models/nemotron-3.5 (T3 [VENDOR]); https://dev.to/klukyanov/best-ollama-models-for-coding-writing-and-medicine-september-2026-4a89 (T3 roundup, numbers secondhand)
- https://github.com/ggml-org/llama.cpp/blob/master/docs/speculative.md (T2-ish project docs: ngram/MTP/draft)
- https://runaihome.com/blog/speculative-decoding-llama-cpp-local-llm-setup-2026/ (T3: flags, GPU speedups, backfire <60-70% acceptance)
- https://nexgpu.net/blog/en/archives/60/ (T3: Ollama 0.32.6 MTP, no figures); https://github.com/ollama/ollama/releases (viewed, no MTP mention in the versions shown)
- https://github.com/ikawrakow/ik_llama.cpp/discussions/666 (T3, one user: PP 63 -> 225)
- Search-result summaries only (page not opened; treat as weak T3): llama.cpp discussion 21112 / MoE offload guides (batch 2048, threads, mlock), KV-cache quantization blogs (modelpiper, inventivehq, openclawdc)
- REJECT/unused: roundup sites' "best model" rankings without method (morphllm 429 error, localaimaster), GLM/Granite/Seed/Ling/DeepSeek claims (nothing opened)

> Supervisor check 2026-09-29: ollama.com/library/qwen3.6 lists tag `qwen3.6:35b` (23 GB; the 35B-A3B MoE, per its chart name), not `35b-a3b` - tag corrected above. Benchmark numbers are only in an image there; treat as vendor-reported.
