# Worker Model Research — qwen3-coder:30b alternatives, Ollama CPU tuning, spec->code quality techniques

Date: 2026-09-28. Box: Intel i7-10710U, 6 cores/12 threads, 32GB RAM, Windows 10, CPU-only Ollama.

## 1. Candidate models vs qwen3-coder:30b

Baseline: qwen3-coder:30b (Qwen3-Coder-30B-A3B, MoE, 3.3B active/30B total, 256K ctx native).
Q4_K_M ≈ 18-19GB. CPU reports ~12-15 tok/s on comparable 6-8 core desktop CPUs with 32GB
DDR4/5 (RAM bandwidth-bound, not core-bound) — matches this NUC class. [Arsturn]

| Model | Type | Active/Total | Quant footprint | Evidence | Verdict for this box |
|---|---|---|---|---|---|
| **qwen3-coder:30b** (current) | MoE | 3.3B/30B | ~19GB Q4_K_M | 80% code-gen / 77% tool-selection on independent local-harness CPU run [Morph]; strong LiveCodeBench/agentic scores in Qwen's own reports | Baseline — best speed/quality ratio already found for CPU-only |
| **GLM-4.6-Air / glm-4.7-flash** (MoE, ~"Air" size class) | MoE | small active fraction | ~19GB (glm-4.7-flash, 198K ctx) | Listed as a leading 2026 open-weight coding MoE in multiple "best Ollama models" roundups [Morph, LocalAIMaster]; no independently verified CPU tok/s or LiveCodeBench number found in this pass | **Worth a bench trial** — same MoE-on-CPU shape as qwen3-coder, but no hard benchmark evidence gathered here justifies switching yet |
| **Qwen3.6-27B** | dense | 27B/27B | ~16GB Q4_K_M | 77.2% SWE-bench Verified, 83.9% LiveCodeBench (best-in-class quality numbers found) [Morph] | Dense 27B on CPU-only will be markedly slower than qwen3-coder's 3.3B-active MoE at similar RAM — expect roughly 3-5x slower tok/s for a ~35% parameter-count increase with all params active every token. Given tasks already take 30-60 min, likely **not acceptable** unless quality gain justifies 2-3hr tasks. |
| **Devstral Small 2 24B** (Mistral, Apache-2.0) | dense | 24B/24B | ~25GB RAM/VRAM | 68.0% SWE-bench Verified, 55.7% SWE-bench Multilingual, 22.5% Terminal-Bench 2, trained specifically for coding agents (Mistral + All Hands AI), Nov 2025 release [Unsloth, HF] | Best *quality* evidence of any candidate (hard agentic benchmark, not just HumanEval), but **dense 24B is CPU-hostile**: expect low single-digit tok/s on this box, pushing 30-60min tasks toward multiple hours. Only try if truncation/wrong-math losses are costing more than the extra wall-clock. |
| **gpt-oss:20b** (OpenAI open-weights) | MoE-ish (MXFP4 native) | — | fits 16GB tier | Cited as the 16GB-VRAM pick, 128K context, good general+code quality [Morph, LocalAIMaster] | Smaller than qwen3-coder30b's active-param budget won't clearly beat it on code quality; mainly useful if RAM headroom needs to shrink, not a quality upgrade |

**Bottom line for Q1**: nothing found in this search pass has hard, independently-verified evidence of beating qwen3-coder:30b on code quality *while* matching its CPU throughput. The two plausible upgrades are (a) **GLM-4.6-Air/glm-4.7-flash** — same MoE-active-param class, worth a timed side-by-side trial on 3-5 real specs before switching, since no independent benchmark was found; and (b) **Devstral Small 2 24B** — best hard agentic-benchmark evidence (68% SWE-bench Verified) but dense, so expect a large speed penalty on CPU-only that likely conflicts with the "30-60 min per task" budget. Recommend: pilot GLM-4.6-Air/flash on a handful of specs first (cheap to test, similar architecture shape); only pilot Devstral if truncation/math-error losses exceed what a 2-4x slowdown would cost.

## 2. Ollama/CPU tuning

- **Flash attention + KV cache quantization**: set `OLLAMA_FLASH_ATTENTION=1` (required first) then `OLLAMA_KV_CACHE_TYPE=q8_0` (near-lossless, ~half KV-cache RAM) or `q4_0` (quarter RAM, "modest quality loss" — avoid given existing wrong-math issue). [ModelPiper, Easton]
- **num_thread**: don't default to all 12 logical threads; tuned CPU-inference defaults found were `num_thread 8` with `num_batch 512`, `num_ctx 16384` — leaves headroom for OS/other processes and avoids hyperthread contention that hurts token/s on many CPU inference engines. [Easton] Test 6 vs 8 vs 10 on this box since it's a 6-core/12-thread part.
- **num_ctx sizing**: keep context to what the spec actually needs (your specs are ≤26k tokens in, ≤7k out) rather than defaulting to the model's max 256K — smaller `num_ctx` directly reduces both prompt-processing time and RAM/KV footprint on CPU.
- **keep_alive**: set long enough (e.g. `30m`+) to avoid repeated model reloads between queued tasks — reload of an 18-19GB Q4 model from disk/RAM is itself a multi-second-to-minute cost repeated per job if keep_alive is short or `0`.
- **OLLAMA_NUM_PARALLEL=1** on this box: CPU-only with one worker queue, parallel request slots just fragment the same RAM/CPU budget — keep it serialized. [Broadcom TechDocs, Easton]
- Sources: [Optimizing Ollama Performance on Windows (Medium)](https://medium.com/@kapildevkhatik2/optimizing-ollama-performance-on-windows-hardware-quantization-parallelism-more-fac04802288e), [Ollama Performance Tuning (Easton, 2026-04-10)](https://eastondev.com/blog/en/posts/ai/20260410-ollama-performance-optimization/), [OLLAMA_KV_CACHE_TYPE (ModelPiper)](https://modelpiper.com/blog/ollama-kv-cache-quantization), [Ollama FAQ](https://docs.ollama.com/faq)

## 3. Techniques to raise small-model code quality in an unattended spec→code pipeline

Ranked by expected gain for *this* setup (truncated replies, occasional wrong math, dropped content on full-file rewrites):

1. **Diff-based edits instead of full-file rewrites** — directly targets the "drops content in full-file rewrites" failure mode observed. Producing a patch/diff bounds output length to the size of the actual change rather than the whole file, which also mitigates truncation on your ~7k-token reply cap. Evidence is indirect (edit-level consistency work assumes diffs are more stable than full regenerations — see "Edit-level Majority Voting" below) but the mechanism directly matches the observed bug class. **Highest expected gain, lowest cost** — this is a harness/prompt change, not extra inference.
   - [Edit-level Majority Voting Mitigates Over-Correction (LLM-based GEC), arXiv 2605.13624](https://arxiv.org/pdf/2605.13624)

2. **Execution feedback / self-debugging retry loop (Reflexion-style)** — run the generated code against the spec's test(s); on failure, feed the traceback/error back to the model for one or two repair passes. This is the standard fix for "occasional wrong math" since arithmetic/logic bugs are exactly what unit-test execution catches that static generation misses. Directly matches your existing gate structure (tests must fail on pre-change code, then pass after) so the retry loop reuses infrastructure you already have.
   - [Self-Debugging: teaching LLMs to debug via execution results + self-explanation, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/2460396f2d0d421885997dd1612ac56b-Paper-Conference.pdf)
   - Reflexion (verbal RL + episodic memory across attempts) — foundational execution-feedback framing referenced across the self-debugging literature found here.
   - [Revisit Self-Debugging with Self-Generated Tests, arXiv 2501.12793](https://arxiv.org/html/2501.12793)

3. **Self-consistency / sample-and-vote (N-version + majority vote)** — generate 2-3 candidate implementations (or candidate diffs) at modest temperature and pick the one matching majority behavior on self-generated or spec-derived tests. Meaningful gain but costs 2-3x wall-clock on a box where single tasks already take 30-60 min — reserve for high-value/high-risk specs (e.g., execution/risk-guard code) rather than blanket use.
   - [Multi-Perspective Self-Consistency (MPSC) for code, arXiv 2309.17272](https://arxiv.org/html/2309.17272v1)
   - [Semantic Voting: Execution-Grounded Consensus for LLM Code Generation, arXiv 2605.08680](https://arxiv.org/pdf/2605.08680)
   - [Scalable Best-of-N Selection via Self-Certainty, arXiv 2502.18581](https://arxiv.org/pdf/2502.18581)

4. **Generate-then-critique / chain-of-verification (single-pass, no execution)** — cheaper than execution feedback when no test harness exists for a given spec fragment, but weaker signal than actually running the code; treat as a fallback for specs where tests aren't easy to derive, not a primary technique here since your pipeline already requires "tests come from Haiku/Sonnet, derived from the spec" — i.e., you already have the harness for technique #2, which should be preferred whenever available.

5. **Property-based / metamorphic testing** — good for catching the "occasional wrong math" class specifically (invariants like monotonicity, idempotence, boundary conditions) but requires Sonnet/Haiku to author property tests per spec, adding upstream cost. Recommend selectively for math-heavy specs (position sizing, PnL, risk calcs) rather than universally.

**Not prioritized**: differential/N-version testing across *different models* (e.g., cross-checking qwen output against a second local model) — theoretically sound but doubles CPU wall-clock on an already slow box for a marginal gain over execution-feedback retry; only worth it if #2 and #3 plateau.

## Report summary (≤20 lines)

**Top pick**: keep qwen3-coder:30b as primary; no candidate found here has verified evidence of beating it on quality *at matching CPU speed*. Pilot **GLM-4.6-Air/glm-4.7-flash** (same MoE-active-param shape, ~19GB) on a few real specs — best speed-matched candidate but unverified here. **Devstral Small 2 24B** has the strongest hard benchmark (68% SWE-bench Verified) but is dense, so expect a large CPU slowdown — only pilot if quality losses currently cost more than 2-4x wall-clock.

**Top 3 techniques**: (1) diff-based edits instead of full-file rewrites — directly fixes the dropped-content-on-rewrite bug, cheapest to add; (2) execution-feedback retry loop (Reflexion/self-debug: run spec tests, feed failures back for 1-2 repair passes) — directly fixes wrong-math bugs, reuses your existing test-gate infra; (3) self-consistency/sample-and-vote for high-value specs only, given the 2-3x cost.

**Top 3 Ollama settings**: (1) `OLLAMA_FLASH_ATTENTION=1` + `OLLAMA_KV_CACHE_TYPE=q8_0` (near-lossless, halves KV RAM); (2) `num_thread 8` (not all 12 threads), `num_batch 512`, size `num_ctx` to the actual ~26k prompt need rather than model max; (3) long `keep_alive` (avoid reload cost) with `OLLAMA_NUM_PARALLEL=1` (serialize, don't fragment RAM/CPU on this single-queue box).

## Sources
- https://www.morphllm.com/best-ollama-models
- https://localaimaster.com/blog/best-ollama-models
- https://www.arsturn.com/blog/running-qwen3-coder-30b-at-full-context-memory-requirements-performance-tips
- https://unsloth.ai/docs/models/tutorials/devstral-2
- https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512
- https://ollama.com/library/devstral:24b
- https://medium.com/@kapildevkhatik2/optimizing-ollama-performance-on-windows-hardware-quantization-parallelism-more-fac04802288e
- https://eastondev.com/blog/en/posts/ai/20260410-ollama-performance-optimization/
- https://modelpiper.com/blog/ollama-kv-cache-quantization
- https://docs.ollama.com/faq
- https://arxiv.org/pdf/2605.13624 (Edit-level Majority Voting / diff-based consistency)
- https://proceedings.iclr.cc/paper_files/paper/2024/file/2460396f2d0d421885997dd1612ac56b-Paper-Conference.pdf (Self-Debugging)
- https://arxiv.org/html/2501.12793 (Revisit Self-Debugging with Self-Generated Tests)
- https://arxiv.org/html/2309.17272v1 (Multi-Perspective Self-Consistency)
- https://arxiv.org/pdf/2605.08680 (Semantic Voting: Execution-Grounded Consensus)
- https://arxiv.org/pdf/2502.18581 (Scalable Best-of-N Selection via Self-Certainty)
