# CODE RED AUDIT: Complete Starvation of CODEX (GPT) and GEMINI Lanes Across All 3 Devices (2026-11-04)

- **Audit ID**: `CODE-RED-2026-11-04-CODEX-GEMINI-STARVATION`
- **Date**: `2026-11-04T07:15Z` (`2026-11-04T12:45+05:30`)
- **Severity**: **CODE RED — P1 CRITICAL / ZERO TOLERANCE**
- **Authority**: Operator Direct Mandate (`d-code-red-codex-gemini-starvation-1104`, `ANNOUNCEMENTS.md` `A-20261104-1`)
- **Author**: Gemini Pro / Argon (`DESKTOP-F7IU69N` / `JIS-LAPTOP`, session `MTS-2026-11-04-0715Z-GEM-BLD-code-red-lane-starvation-1104`)
- **Trunk Snapshot Audited**: `origin/fast-track` @ `cbfc521d4` (`2026-11-04T07:10Z`)

---

## 1. Operator Code Red Directive (Verbatim Mandate)

> **OPERATOR CODE RED (2026-11-04):**
> The operator is **furious** that Claude AI coordinators and planners across the three devices (`JIS-NB` / `JIS-DESKTOP`, `JIS-NUC`, and `DESKTOP-F7IU69N` / `JIS-LAPTOP`) have failed to create work for the `CODEX` (GPT) and `GEMINI` (Flash / Argon) LLMs, leaving both non-Claude lanes completely idle (`0` ready cards) and struggling to find work while Claude hoards work in its own `SONNET` lane (`28` ready cards) and burns Claude weekly/API budgets.
>
> **This has been a recurring miss for quite some time (`2026-10-30` in `A-20261030-2`, repeated again on `2026-11-03` and `2026-11-04`), and it WILL NOT BE TOLERATED.** It must be corrected immediately and permanently across all stations.

---

## 2. Quantitative Evidence of Lane Starvation

### 2.1 Live Queue Snapshot (`2026-11-04T07:10Z`, commit `cbfc521d4`)

At the time of this audit (`supervisor.lane_counts(tasks.load_all())` and `tasks.py status`):

| Metric / Lane | Ready Cards (`state=ready`) | Programmed Floor (`D11_PROGRAMME.md` / `supervisor.py`) | Floor Coverage | Open Non-Ready (`refined` / `blocked` / `raw`) | Status |
|---|---:|---:|---:|---:|---|
| **`CODEX` (GPT)** | **`0`** | **`8`** | **0% (STARVED)** | `8` blocked, `0` refined, `0` raw | **IDLE 13.5+ HOURS** (since `11-03T17:40Z`) |
| **`GEMINI` (`[GEMINI]` on `CODEX`)** | **`0`** | **`4`** | **0% (STARVED)** | `1` refined (blocked on deps), `0` raw | **IDLE 8.6+ HOURS** (since `11-03T22:39Z`) |
| **`SONNET` (Claude)** | **`28`** | `6` | **467% (HOARDED)** | `91` refined, `22` blocked, `5` raw | Over-queued 4.6x above floor |
| **`HAIKU` (Claude)** | **`4`** | `3` | **133%** | `8` refined, `0` blocked, `0` raw | Above floor (includes 1 misrouted Gemini card) |
| **`JIS-NB` (Desk/Host)** | **`6`** | — | — | `9` refined, `5` blocked, `2` raw | Active |
| **`OPUS` / `DSA-NUC`** | **`2`** (`1` / `1`) | — | — | `4` refined, `1` blocked | Active |
| **TOTAL** | **`40`** | — | — | `113` refined, `36` blocked, `7` raw | **`0` non-Claude LLM cards runnable** |

### 2.2 11-Day Card Creation Trajectory (`2026-10-25` to `2026-11-04`)

Counting every task card in `MyTradingSys/system/tasks/*.json` by `created` UTC date and target LLM (`SONNET`, `HAIKU`, `CODEX (GPT)`, `GEMINI`):

| UTC Date | `SONNET` Created | `HAIKU` Created | `CODEX (GPT)` Created | `GEMINI` Created | Non-Claude Share (`GPT + GEMINI`) | Notes |
|---|---:|---:|---:|---:|---:|---|
| `2026-10-25` | 26 | 4 | 15 | 0 | 33.3% | Pre-Gemini lane |
| `2026-10-26` | 15 | 6 | 17 | 0 | 44.7% | NUC Codex active |
| `2026-10-27` | 30 | 9 | 1 | 0 | 2.5% | First starvation drop |
| `2026-10-28` | 53 | 11 | 22 | 0 | 25.6% | Recovery |
| `2026-10-29` | 34 | 25 | 3 | 0 | 4.8% | Second starvation drop -> triggered `D11_PROGRAMME.md` (`A-20261030-2`) |
| `2026-10-30` | 66 | 13 | 12 | 29 | 34.2% | Operator intervened (`d-super-session-programme`); D11 feeder rule written |
| `2026-10-31` | 85 | 5 | 7 | 35 | 31.8% | High Gemini batch |
| `2026-11-01` | 26 | 4 | 5 | 15 | 40.0% | Steady |
| `2026-11-02` | 32 | 7 | 12 | 22 | 46.6% | Steady |
| `2026-11-03` | 32 | 3 | 4 | 20 | 40.7% | Last GPT card created `16:00Z`; last Gemini card created `20:21Z` |
| **`2026-11-04`** | **`6`** | **`1`** | **`0`** | **`0`** | **`0.0%`** | **COMPLETE COLLAPSE: 0 GPT and 0 GEMINI cards created in 12+ hours** |

### 2.3 Timeline of the 2026-11-03 / 2026-11-04 Starvation Collapse

- **`2026-11-03T16:00:54Z`**: Last `CODEX` (GPT) card created (`audit-prereg-Freeze-dates-1103`).
- **`2026-11-03T17:40:14Z`**: Last `CODEX` (GPT) card finished (`audit-prereg-Freeze-dates-1103`, commit `bc29d04fb`). From `17:40Z` onward (**13.5+ hours**), the GPT lane on `JIS-NUC` had **0 ready cards**.
- **`2026-11-03T20:21:41Z`**: Last `[GEMINI]` batch of 4 Argon cards created (`gemini-blind-read-charts-1103`, `gemini-context-filter-audit-1103`, `gemini-session-edge-scan-1103`, `gemini-yt-5-more-claims-1103`).
- **`2026-11-03T22:39:11Z`**: Laptop Gemini session (`DESKTOP-F7IU69N`) finished and shipped the last ready `[GEMINI]` card (`gemini-yt-5-more-claims-1103`, commit `fa4bb8e25`). From `22:39Z` onward (**8.6+ hours**), the `[GEMINI]` lane across all devices had **0 ready cards**.
- **`2026-11-04T00:00Z` – `07:10Z`**: Over 35 commits landed on `origin/fast-track` from Claude sessions on `JIS-NB` (`login C`) and `JIS-NUC` (`login B`), including **8 new backtest/context study results and 5 production/backtest Python modules**, plus a dedicated `Session_Planner` run (`df453c532` at `05:14Z`). **Not a single valid `CODEX` (GPT) or `[GEMINI]` card was created.**

---

## 3. Seven Root Causes Identified (With Exact File & Line Evidence)

### Root Cause 1: Total Violation of the `D11_PROGRAMME.md` Feeder Rule by Claude Coordinators (`JIS-NB/C` and `JIS-NUC/B`)

`MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` (lines 50–56) and `MyTradingSys/system/ANNOUNCEMENTS.md` (`A-20261030-2`, line 25) establish a mandatory law:

> **The feeder rule (why the queues never go dry again):**
> Every ship produces its check in another vendor's lane in the same wake:
> - a new `.py` without a test -> `gpt-spec-tests-<name>` (`CODEX`, kind `audit`);
> - a result or audit file with numbers -> `[GEMINI]` blind re-read (or a GPT re-derive when Gemini produced it);
> - a rule edit -> `haiku-count-verify-<name>` (`HAIKU`).

On `2026-11-04` between `00:00Z` and `07:05Z`, Claude sessions (`login C` Unblock MTS super session on `JIS-NB`) shipped **8 quantitative study results** and **5 code changes**:
1. `8ce5461b0` / `85eb02983`: `MyTradingSys/research/bb_range_to_range_2026-11-04/RESULT.md` + `trades.csv` + `summary.csv`
2. `f38aa80a3` / `85eb02983`: `MyTradingSys/research/bb_range_retest_2026-11-04/RESULT.md` + `long_window_2017_2026.csv`
3. `07f4d20f0`: `MyTradingSys/research/bb_long_window_2026-11-04/RESULT.md` + `summary.csv` + `trades.csv`
4. `83a512a2e` / `f934791b5`: `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/RESULT.md` + `long_window_2017_2026.csv`
5. `c509665ff` / `1c865e8c7`: `MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/RESULT.md` + `long_window_2017_2026.csv`
6. `acbf0676c`: `MyTradingSys/research/fabio_valentini/FABIO_L1_REPORT.md` + `fabio_l1_strict_rerun.json`
7. `aa8d1b819`: `MyTradingSys/research/klines_history_2017/regime_mix_long.py` + `backtest/fetch_binance_archive.py`
8. `d91081762` / `cbfc521d4` / `20165a523`: `backtest/research_kit.py`, `backtest/layers/alerts/live_confluence_feed.py`, `backtest/layers/rsi/div_flags_chart.py`

**Feeder cards filed by Claude across all 8 ships**: **ZERO (`0` `[GEMINI]` blind-read cards, `0` `gpt-spec-tests-*` cards).**
Even after writing `d-eco-mode-1104` in `OPERATOR_DECISIONS.md:1703` (*"Gemini (both logins) and Codex lanes are fed first by the Planner (LANE LOW floors stand)"*), the Claude coordinator immediately moved on without filing a single Gemini or Codex card.

---

### Root Cause 2: Two Structural Bugs in `scripts/dev/supervisor.py` (`LANE_FLOORS` and `plan_lines`)

Inspection of `scripts/dev/supervisor.py` reveals why the automated supervisor failed to force a `Session_Planner` run when `CODEX` and `GEMINI` hit `0`:

1. **Defect 2A — `CODEX` Is Omitted from `LANE_FLOORS` (`supervisor.py:283`)**:
   ```python
   LANE_FLOORS = {"SONNET": 6, "HAIKU": 3, "GEMINI": 4}
   ```
   `CODEX` (floor `8` per `D11_PROGRAMME.md:56`) is missing from `LANE_FLOORS`. Instead, `CODEX < 8` is checked at `supervisor.py:1124-1125`:
   ```python
   if me_codex and 0 <= cx < 8:
       out.append(f"{step}. NOTE CODEX lane {cx} ready (< 8): seed from D11_PROGRAMME.md section 6")
   ```
   Because this line is gated behind `if me_codex` (`lane_owner(live, NUC) == h`), when `JIS-NUC` has no active supervisor heartbeat (`SUPERVISOR_B.md` had `mode=ENDED` or stale timestamp) or when `JIS-NB` (`login C`) is driving the fleet, `JIS-NB` sees only a passive `NOTE` (or nothing at all when `JIS-NUC` holds the heartbeat), never a `LANE LOW` alert.

2. **Defect 2B — `LANE LOW` Does Not Trigger `RUN Session_Planner` (`supervisor.py:1106-1114` & `tasks.py:593-599`)**:
   In `supervisor.py:1106-1114`:
   ```python
   for ln, fl in LANE_FLOORS.items():
       if lc.get(ln, 0) < fl:
           out.append(f"{step}. LANE LOW {ln} {lc.get(ln, 0)} (< {fl}): seed from D11_PROGRAMME.md section 6")
           step += 1
   if ctx.get("refine_raw") and not hold:
       out.append(f"{step}. RUN Session_Planner (Agent, sonnet): refine {ctx['refine_raw']} raw cards")
   ```
   And in `scripts/dev/tasks.py:593-599`:
   ```python
   CODE_LANES = ("HAIKU", "SONNET", "OPUS")
   def builder_ready(cards: list[dict]) -> int:
       return sum(1 for c in cards if c.get("state") == "ready" and c.get("lane") in CODE_LANES and not is_gemini_card(c))
   def refine_due(cards: list[dict]) -> int:
       raw = [c for c in cards if c.get("state") == "raw"]
       return len(raw) if raw and (stale_raw(cards) or builder_ready(cards) < BUFFER) else 0
   ```
   `tasks.refine_due()` **only counts Claude `CODE_LANES` (`HAIKU`, `SONNET`, `OPUS`)**! Because `SONNET` had `28` ready cards (`>= BUFFER` of `6`), `builder_ready(cards) < BUFFER` was `False`. Once the stale raw cards were touched by `planner-20261104`, `refine_due()` returned `0`, so `supervisor.py` **stopped emitting `RUN Session_Planner` altogether**, even though `GEMINI` was at `0 (< 4)` and `CODEX` was at `0 (< 8)`!

---

### Root Cause 3: `MyTradingSys/system/roles/session_planner.md` Completely Omits `D11_PROGRAMME.md`, `LANE LOW`, `CODEX`, and `GEMINI` Seeding

While `SUPER_SESSION.md:20` and `D11_PROGRAMME.md:56` state that *"when `supervisor.py plan` prints `LANE LOW`, the `Session_Planner` feeds that lane from section 6 first, then refines raw cards"*, `MyTradingSys/system/roles/session_planner.md` (lines 1–73) **never mentions `D11_PROGRAMME.md`, `LANE LOW`, `[GEMINI]`, or seeding feeder cards**.
- Its `Boot` (lines 15–18) and `Duty 1` (lines 20–35) instruct the planner solely to *"refine (`raw -> ready`), take cards by priority (`p1` first), at most 5 per run"*.
- Consequently, when `Session_Planner` ran on `2026-11-04T05:14Z` (commit `df453c532`, `MTS-2026-11-04-0512Z-NUC-B-PLN-planner-20261104`), it followed `session_planner.md` literally: it refined 10 `SONNET` cards (`cbp-run-py-rebuild-the-cbp-analyst-desk-`, `fabio-l1-has-no-run-on-the-strict-detect`, `klines-history-extend-2017`, `krown-hidden-divergence-confluence-feed`, etc.) and created **zero** `CODEX` (GPT) or `[GEMINI]` cards.

---

### Root Cause 4: Misrouting of Intended Gemini Work onto Claude's `HAIKU` Lane + Ignored Cross-Station Broadcast (`malkan-hindi-extract` / `b-1aa316`)

1. At `2026-11-03T22:13Z`, `JIS-NB/C` sent high-priority broadcast `b-1aa316`:
   > `B/NUC: please queue the 6 Malkan Hindi videos on gemini_queue at low effort (d-move-lagging-layers-1104)...`
2. `JIS-NUC/B` left broadcast `b-1aa316` unacknowledged (`state: none`) for **over 9 hours**.
3. When a session on `JIS-NUC` finally created `MyTradingSys/system/tasks/malkan-hindi-extract.json` at `2026-11-04T05:11Z` (commit `ab7835410`), the commit message read:
   > `malkan-hindi-extract: raw->ready (6 Hindi videos, Gemini lane)`
   Yet inside `malkan-hindi-extract.json`, the author set:
   - `"lane": "HAIKU"` (instead of `"CODEX"`)
   - `"title": "Extract Malkan RSI divergence concepts from the 6 Hindi videos"` (omitting the mandatory `"[GEMINI]"` prefix!)
4. In `scripts/dev/tasks.py:589-590`:
   ```python
   def is_gemini_card(c: dict) -> bool:
       return "[GEMINI]" in c.get("title", "").upper()
   ```
   Because `"lane"` was set to `"HAIKU"` and `"[GEMINI]"` was omitted from `"title"`, `is_gemini_card()` returned `False` and `tasks.py list --lane CODEX --state ready` excluded it. Neither NUC's `gemini_queue.py` nor the laptop's Antigravity Gemini session could see or claim the card.

---

### Root Cause 5: 113 Cards Bottlenecked in `refined` State (50 Ready-to-Promote Cards Never Checked; 60 Missing Review Stamps)

Running `tasks.problems()` and `tasks.promotion_problems()` across all `113` `refined` cards on trunk shows a massive artificial dam:
- **`50` `refined` cards (`44%`) already pass every single DoR and promotion gate (`WOULD PROMOTE` immediately if `tasks.py check <id>` were run on them)**, because their `REVIEWED:` stamps or dependencies were added after their last `tasks.py check` call!
- **`60` `refined` cards (`53%`) pass all DoR fields (`problems() == []`) but are parked solely on `promotion_problems()`**:
  - `45` cards lack a `REVIEWED:` stamp in `note` (`d-reviews-on-haiku-credit-1104` noted this backlog, yet no batch promoted any `CODEX` or `[GEMINI]` cards).
  - `15` cards have `REVIEWED: ... T0-ONLY` on `IMPORTANT+` weight.
- **`8` `CODEX` cards sit in `blocked` state** (`cbp-quote-gate-review`, `codex-gpt-exhaust-full`, `lf-cryptocred-gpt-rederive`, `lf-guidance-gpt-rederive`, `t08-original-input-window-provenance`, `tom-btc-dev-backtest`, `tom-btc-encode`, `tom-btc-other-setups`) and **`1` `[GEMINI]` card sits in `refined` state** (`rsi-deep-crossvendor-review`, blocked on `rsi-deep-engine*`), with zero unblocked replacements seeded alongside them.

---

### Root Cause 6: Unharvested `gemini-q/*` Branches Left Stranded on Disk by Claude Sessions

`GEMINI_START.md:22` states that when Gemini runs via `gemini_queue.py` on `JIS-NUC`, Gemini commits to branch `gemini-q/<id>` and stops because *"a Claude session reviews the diff (`git log -p gemini-q/<id>`) and ships it."*
- `sync.py where` shows **3 completed `gemini-q/*` worktrees sitting unshipped on disk**:
  1. `gemini-q/gemini-param-labels-studies-1101` (`unshipped-commits=1`)
  2. `gemini-q/gpt-mutation-trendline-core-1031` (`unshipped-commits=1`)
  3. `gemini-q/gpt-rederive-tom-vp-return-to-value` (`unshipped-commits=1`)
- Because Claude sessions neglected to review and ship `gemini-q/*` branches—and because `supervisor.py` has no step that alerts on unharvested `gemini-q/*` branches—completed Gemini work was left stranded outside trunk while the cards themselves had to be redone or shipped manually by laptop Gemini sessions.

---

### Root Cause 7: Multi-Device Dispatch Siloing Across the 3 Stations (`JIS-NB`, `JIS-NUC`, `DESKTOP-F7IU69N`)

The operator runs three machines:
1. **`JIS-NB` (`JIS-DESKTOP`, `login C`)**: Runs the Unblock MTS super session and builds/backtests, generating massive verification debt (8 study ships + 5 code modules on 2026-11-04 alone) without creating `CODEX` or `[GEMINI]` cards.
2. **`JIS-NUC` (`login B` / Gateway)**: Hosts `codex_run.py` (GPT-5.4 high) and `gemini_queue.py` (Gemini CLI). When `login B` paused at its 65% cap (`05:08Z`) or focused on `SONNET` cards, and `CODEX` / `GEMINI` queues hit `0`, `JIS-NUC`'s non-Claude engines sat completely dark.
3. **`DESKTOP-F7IU69N` (`JIS-LAPTOP`, `login A` + Antigravity Gemini Pro `mts-gemini`)**: While Claude `login A` rests until its Friday reset (`d-eco-mode-1104`), the laptop's **Antigravity Gemini Pro session (`mts-gemini`) is live, unrestricted by Claude weekly caps, and actively polling `--lane CODEX` for `[GEMINI]` and `CODEX` cards**. Because `supervisor.py:1122` only considered `gemini_queue.py` on `JIS-NUC` and Claude sessions created `0` `[GEMINI]` / `CODEX` cards on `2026-11-04`, the laptop station's LLM capacity was completely wasted.

---

## 4. Immediate Corrective Actions Executed in This Turn

To resolve this Code Red end-to-end immediately, this session has executed and shipped the following on `origin/fast-track`:

1. **Filed `ANNOUNCEMENTS.md` `A-20261104-1 DO-NOW CODE RED`**:
   - Placed at the very top of `## ACTIVE` in `MyTradingSys/system/ANNOUNCEMENTS.md` so every session on every station (`JIS-NB`, `JIS-NUC`, `DESKTOP-F7IU69N`) reads it at boot.
2. **Recorded Operator Decision `d-code-red-codex-gemini-starvation-1104` in `MyTradingSys/system/OPERATOR_DECISIONS.md`**:
   - Documented the operator's verbatim fury, zero-tolerance warning, and mandatory cross-device rules.
3. **Updated `MyTradingSys/system/roles/session_planner.md` (Boot + Duty 0 / Duty 1)**:
   - Made feeding `CODEX` (floor `>= 8` ready) and `GEMINI` (floor `>= 4` ready) from `D11_PROGRAMME.md` section 6 and recent ships the **first mandatory duty** of every `Session_Planner` run before refining any `SONNET` card.
4. **Fixed Misrouted Card `malkan-hindi-extract`**:
   - Corrected `MyTradingSys/system/tasks/malkan-hindi-extract.json` from `"lane": "HAIKU"` to `"lane": "CODEX"`, `"kind": "run"`, `"weight": "ROUTINE"`, and prefixed title with `"[GEMINI] Extract Malkan RSI divergence concepts from the 6 Hindi videos"` so it is immediately runnable by Gemini.
5. **Created and Pinned the #1 Highest-Priority Task Card `code-red-codex-gemini-lane-feeder-1104` (`p1`, `pinned: true`, `state: ready`, `weight: IMPORTANT`)**:
   - Ranks at the top of `tasks.py dispatch` for all Claude coordinators/builders to wire `supervisor.py` enforcement (`CODEX: 8` in `LANE_FLOORS`, `refine_due` / `RUN Session_Planner` triggered whenever `CODEX < 8` or `GEMINI < 4`, and `gemini-q/*` harvest checks).
6. **Seeded and Promoted 8 Immediate `ready` Cards (`4` `[GEMINI]` + `4` `CODEX` GPT) from Today's 2026-11-04 Unchecked Ships**:
   - **`[GEMINI]` Ready Cards (plus `malkan-hindi-extract` = 5 `[GEMINI]` ready, above floor of 4)**:
     1. `malkan-hindi-extract` (`[GEMINI] Extract Malkan RSI divergence concepts from the 6 Hindi videos`)
     2. `gemini-blind-read-bb-range-studies-1104` (`[GEMINI] Blind read of Bollinger range-to-range, retest, and long-window RESULT.md vs CSVs`)
     3. `gemini-blind-read-wavetrend-c30-retest-1104` (`[GEMINI] Blind read of WaveTrend C30 retest and long-window RESULT.md vs CSVs`)
     4. `gemini-blind-read-rsi-div-mtf-gated-1104` (`[GEMINI] Blind read of RSI divergence MTF gated and long-window RESULT.md vs CSVs`)
     5. `gemini-blind-read-fabio-l1-strict-1104` (`[GEMINI] Blind read of FABIO_L1_REPORT.md vs fabio_l1_strict_rerun.json`)
   - **`CODEX` (GPT) Ready Cards (8 `CODEX` GPT ready, meeting the floor of 8)**:
     1. `gpt-spec-tests-research-kit-context-1104` (`GPT spec and mutation tests for research_kit.py context harness and retest-entry mode`)
     2. `gpt-spec-tests-live-confluence-feed-1104` (`GPT spec and mutation tests for live_confluence_feed.py Malkan RSI divergence wiring`)
     3. `gpt-spec-tests-div-flags-chart-1104` (`GPT spec tests for div_flags_chart.py 12/18/>18 bar close-only divergence windows`)
     4. `gpt-spec-tests-fetch-binance-archive-1104` (`GPT spec tests for fetch_binance_archive.py and klines_history_2017/regime_mix_long.py`)
     5. `gpt-rederive-bb-range-to-range-1104` (`GPT independent re-derivation of bb_range_to_range_2026-11-04 session range metrics`)
     6. `gpt-rederive-wavetrend-c30-retest-1104` (`GPT independent re-derivation of wavetrend_c30_retest_2026-11-04 retest+RSI+session metrics`)
     7. `gpt-rederive-rsi-div-mtf-gated-1104` (`GPT independent re-derivation of rsi_divergence_mtf_gated_2026-11-04 strict vs bear-proxy metrics`)
     8. `gpt-audit-context-filter-review-1104` (`GPT audit of CONTEXT_FILTER_REVIEW_2026-11-04.md classifications against backtest scripts`)
7. **Broadcasted High-Priority Code Red & Direct Station Pings (`mts_signal.py`)**:
   - Sent `--prio high` broadcast to all stations and direct `mts_signal.py ask --type task` pings to `JIS-NB`, `JIS-NUC`, `DESKTOP-F7IU69N`, and logins `A`, `B`, `C`.

---

## 5. Permanent Non-Negotiable Rules Going Forward

1. **No Ship Without a Cross-Vendor Feeder Card**: Any Claude session shipping a study (`RESULT.md`, `REPORT.md`, `DEV_CHECK.md`) or new/edited `.py` module without filing and promoting its companion `[GEMINI]` blind-read card and/or `CODEX` (`gpt-spec-tests-*` / `gpt-rederive-*`) card in the same wake is in violation of `A-20261104-1`.
2. **Hard Queue Floors (`CODEX >= 8`, `GEMINI >= 4`)**: Whenever `CODEX` (GPT) ready `< 8` or `GEMINI` ready `< 4`, `Session_Planner` and the active coordinator MUST replenish those lanes to floor **before** refining or dispatching any new `SONNET` card.
3. **`[GEMINI]` Naming Invariant**: Every card intended for Gemini MUST have `"lane": "CODEX"` and start its `"title"` with `"[GEMINI] "` so `tasks.is_gemini_card()` returns `True` across all 3 stations.
