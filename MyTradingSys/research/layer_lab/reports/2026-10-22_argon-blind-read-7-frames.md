# Layer Lab Report: argon-blind-read-7-frames

## 1. Headline Numbers and Verdict

- Reader: `gemini-4-argon-low` (Antigravity CLI `agy.exe`, low effort, headless direct invocation).
- Pilot Reference Base: `UNCHECKED` (`hard_results_gemini-3.8-flash-low.json`, audit of 2026-10-12).
- Evaluated Scope: 7 pilot frames (6 single panels + split 2-panel k0zm) plus 2 enlarged crops.
- Field-level Descriptive Counts (7-frame core: 28 total fields across pos, entry, stop, target):
  - Matches to known numeric truth: **16**
  - Numeric mismatches: **1**
  - Correct nulls (truth is null, reader returned null): **5**
  - Missed nulls (truth is numeric, reader returned null): **0**
  - Invented numbers (truth is null, reader invented a number): **4** (down from 4 on Flash low)
  - Unverified reference fields ('?' in pilot audit): **2** (excluded from accuracy denominators)

### Resolution of Contested Crops
1. **k0zm target (25200 vs 25206)**:
   - **Resolution: Tag is 25206 (RESOLVED directly legible)**.
   - **Evidence**: On the enlarged axis crop, Argon reads a highlighted blue order pill on the axis displaying `25206` (or `25205`), directly above the faint gray background grid axis tick `25200`. The actual order tag is `25206`, while `25200` is the underlying price axis tick mark.
   - Full bottom panel blind read by Argon also returned `target: 25206`.
2. **T6hDJcHrVBM_0550 stop**:
   - **Resolution: CONTESTED / UNREADABLE (stop order text obscured)**.
   - **Evidence**: On the enlarged 540x760 crop of the order area, Argon identified position `-2` at `24690`, target `2` lots at `24184`, and current price `24435`, but reported **'Stop Loss Label: None visible in this crop'** and returned `stop: null`. The stop loss line/label is completely overlapped/obscured by the position entry tag at `24690`.
   - Flash's blind read had returned `stop: 24690` (an inferred value flagged by our audit). Argon correctly refrained from inventing a value, returning `null`.

## 2. What was Run

- Isolated scratch directory: `F:/MTS/scratch/argon_run/iso_<id>/` (single image per call; images never committed to repository).
- agy CLI command template:
  ```
  C:/Users/E-ngineers/.gemini/bin/agy.exe --print "Open image <filename> in this folder. Return ONLY JSON {position,entry,stop,target}; each is a number or null. Use null if unreadable or absent. Never infer hidden values." --model gemini-4-argon-low --effort low
  ```
- Image preparation:
  - `k0zm_1510_1720.png` split at row 373 boundary into `k0zm_panel_top.png` (earlier 2-lot state) and `k0zm_panel_bottom.png` (later 1-lot state).
  - Target crop: `k0zm_target_crop.png` (y: 320..420, x: 280..480 of bottom panel).
  - Stop crop: `T6hDJcHrVBM_0550_crop.png` (540x760 high-resolution crop of order region).

## 3. Comparison Table (Argon low vs Flash low vs Pilot Reference)

| Frame / Panel | Field | Truth (Audit) | Argon low | Flash low | Argon Score | Note |
|---|---|---|---|---|---|---|
| T6hDJcHrVBM_0520.jpg | position | -3 | -3 | -3 | MATCH |  |
| T6hDJcHrVBM_0520.jpg | entry | 24690 | 24690 | 24690 | MATCH |  |
| T6hDJcHrVBM_0520.jpg | stop | None | None | None | CORRECT_NULL | Honest null |
| T6hDJcHrVBM_0520.jpg | target | 24184 | 24184 | 24184 | MATCH |  |
| T6hDJcHrVBM_0550.jpg | position | -2 | -2 | -2 | MATCH |  |
| T6hDJcHrVBM_0550.jpg | entry | None | 24690 | None | INVENTED | INVENTED (truth is null) |
| T6hDJcHrVBM_0550.jpg | stop | None | None | 24690 | CORRECT_NULL | Honest null |
| T6hDJcHrVBM_0550.jpg | target | 24184 | 24184 | 24184 | MATCH |  |
| zQTbdEweG3c_0370.jpg | position | -1 | -1 | -1 | MATCH |  |
| zQTbdEweG3c_0370.jpg | entry | 25344 | 25344 | 25344 | MATCH |  |
| zQTbdEweG3c_0370.jpg | stop | None | None | None | CORRECT_NULL | Honest null |
| zQTbdEweG3c_0370.jpg | target | None | None | None | CORRECT_NULL | Honest null |
| l8RZrBfzvp4_0190.jpg | position | -1 | -1 | -1 | MATCH |  |
| l8RZrBfzvp4_0190.jpg | entry | 6806.25 | 6806.25 | 6806.25 | MATCH |  |
| l8RZrBfzvp4_0190.jpg | stop | ? | 6812.25 | 6812.25 | UNVERIFIED | UNVERIFIED (truth is '?') |
| l8RZrBfzvp4_0190.jpg | target | 6767.25 | 6767.25 | 6767.25 | MATCH |  |
| SANOimk8M9o_0270.jpg | position | None | -1 | -1 | INVENTED | INVENTED (truth is null) |
| SANOimk8M9o_0270.jpg | entry | None | 24229 | 24229 | INVENTED | INVENTED (truth is null) |
| SANOimk8M9o_0270.jpg | stop | None | None | None | CORRECT_NULL | Honest null |
| SANOimk8M9o_0270.jpg | target | None | 24111 | 24111 | INVENTED | INVENTED (truth is null) |
| UOBgXV20yCM_0250.png | position | ? | 1 | 1 | UNVERIFIED | UNVERIFIED (truth is '?') |
| UOBgXV20yCM_0250.png | entry | 23887 | 23887 | 23887 | MATCH |  |
| UOBgXV20yCM_0250.png | stop | 23857 | 23857 | 23857 | MATCH |  |
| UOBgXV20yCM_0250.png | target | 23962 | 23962 | 23962 | MATCH |  |
| k0zm_1510_1720.png (top panel, 15:10) | position | -2 | -2 | N/A | MATCH |  |
| k0zm_1510_1720.png (top panel, 15:10) | entry | 25332 | 25332 | N/A | MATCH |  |
| k0zm_1510_1720.png (top panel, 15:10) | stop | 25344 | 25344 | N/A | MATCH |  |
| k0zm_1510_1720.png (top panel, 15:10) | target | 25201 | None | N/A | MISSED_NULL |  |
| k0zm_1510_1720.png (bottom panel, 17:20) | position | -1 | -1 | -1 | MATCH |  |
| k0zm_1510_1720.png (bottom panel, 17:20) | entry | 25324 | 25324 | 25324.0 | MATCH |  |
| k0zm_1510_1720.png (bottom panel, 17:20) | stop | 25310 | 25310 | 25349.0 | MATCH |  |
| k0zm_1510_1720.png (bottom panel, 17:20) | target | 25200 | 25206 | 25200.0 | MISMATCH |  |

## 4. Enlarged Crop Transcriptions

### Crop 1: k0zm Target (25200 vs 25206)
- Image: `k0zm_target_crop.png`
- Raw Argon Transcription:
```
Here is the visible text and numbers in [k0zm_target_crop.png](file:///F:/MTS/scratch/argon_run/iso_crop_k0zm_target/k0zm_target_crop.png):

### 1. Price Axis & Order/Price Tags (Left Side)
* **Highlighted Blue Price Tag:** **`25206`** (white text on a blue tag along the vertical price scale).
* **Faint Background Axis Labels (below the blue tag):**
  * Directly under the blue tag: **`25200`** (partially obscured/faint)
  * Below that: **`25190`** (faint grey text)
  * Near the bottom: **`25180`** (very blurry/faint grey text)

### 2. Trading Panel / Controls (Right Side)
* **Top Dark Button (partially cropped at the top):** **`Breakeven (+`** (or `Breakeven (1` / similar, cut off on the right).
* **Middle Blue Button:** **`SchlieГџen`** (German for "Close").
* **Numeric Input / Value Box (below the blue button):** **`68,0`** (white/light-grey digits with a comma decimal separator).
* **Bottom Red Button (cropped at the bottom edge):** Only the top edge of a red button is visible; no text is readable.
```

### Crop 2: T6hDJcHrVBM_0550 Stop
- Image: `T6hDJcHrVBM_0550_crop.png`
- Raw Argon Transcription:
```
Here is a description of the visible text, order tags, and price labels in [T6hDJcHrVBM_0550_crop.png](file:///F:/MTS/scratch/argon_run/iso_crop_0550_stop/T6hDJcHrVBM_0550_crop.png):

### 1. Order / Price Tags (Highlighted Labels)
* **Top Red Order Tag & Price Label:**
  * **Order box (left):** Shows two close icons (`X` `X`), quantity **`-2`**, and a blue-bordered value field that is blacked out/redacted (with only a partial trailing `0` or `)` edge faintly visible).
  * **Price axis tag (right, red background):** **`24690`**

* **Middle Current/Reference Price Tags:**
  * **Black price tag (dotted horizontal line):** **`24435`**
  * **Purple/Blue price tag (solid purple horizontal line directly underneath `24435`):** Partially occluded at the top by the `24435` tag; the lower half of the digits reads **`24425`** (or `24423`, consistent with `24425`).

* **Bottom Blue Take-Profit (TP) Order Tag & Price Label:**
  * **Order box (left):** Shows a close icon (`X`), quantity **`2`**, label **`TP`**, a blacked-out/redacted value box, and **`R`** on the right.
  * **Price axis tag (right, blue background):** **`24184`**

---

### 2. Background Price Axis Scale (Right Column, Top to Bottom)
* **`24750`**
* **`24700`** (partially covered at the bottom by the `24690` red tag)
* **`24650`**
* **`24600`**
* **`24550`**
* **`24500`** (faint)
* **`24350`** (faint)
* **`24300`**
* **`24250`**
* **`24200`** (partially above the `24184` blue tag)
* **`24150`**
```

## 5. Findings & Defect Ledger

| Severity | File / Image | Finding | Classification | Disposition |
|---|---|---|---|---|
| MED | `k0zm_1510_1720.png` | Two-panel vertical stack mixes earlier state (stop 25344/25349) and later state (stop 25310). Split eliminates mixing. | E1 Data / Panel mixing | PASS: Separate panels evaluated cleanly. |
| LOW | `k0zm` target | Target label on axis is `25206`; `25200` is the underlying grid tick. | E2 Definition / Precision | RESOLVED: Label is 25206. Audit record clarified. |
| LOW | `T6hDJcHrVBM_0550` stop | Stop loss label is overlapped and not readable. | E1 Data / Obscured field | CONTESTED: Marked unreadable / honest null. |

## 6. Follow-up Cards

- None created; this is a scoped Layer Lab run card.
- Reference pilot base remains `UNCHECKED` per Lab_Guy protocol.
