"""End-to-end pipeline for card argon-blind-read-7-frames.

1. Runs blind reads via agy gemini-4-argon-low on each isolated subfolder.
2. Runs descriptive reads on the two enlarged crops (k0zm target and 0550 stop).
3. Compares locally against pilot references and prior Flash results.
4. Saves bounded results_argon-low.json to MyTradingSys/research/layer_lab/argon_blind_read/.
5. Writes dated Layer Lab report to MyTradingSys/research/layer_lab/reports/2026-10-22_argon-blind-read-7-frames.md.
6. Records trial row in MyTradingSys/research/layer_lab/TRIALS.md.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Add scripts/dev to path
sys.path.insert(0, str(Path(__file__).parent))

import argon_blind_read as abr

REPO_ROOT = Path(__file__).resolve().parents[2]
PILOT_JSON = REPO_ROOT / "MyTradingSys/research/lab_guy/pilots/2026-10-18_gemini_frame_read/hard_results_gemini-3.8-flash-low.json"
RESULTS_DIR = REPO_ROOT / "MyTradingSys/research/layer_lab/argon_blind_read"
RESULTS_JSON = RESULTS_DIR / "results_argon-low.json"
REPORT_FILE = REPO_ROOT / "MyTradingSys/research/layer_lab/reports/2026-10-22_argon-blind-read-7-frames.md"
TRIALS_FILE = REPO_ROOT / "MyTradingSys/research/layer_lab/TRIALS.md"


def main():
    print("=== Step 1 & 2 & 3: Executing blind and crop reads with Argon low ===")
    out = abr.execute_all()
    results = out["results"]

    print("=== Step 4 & 5 & 6: Local comparison with pilot references ===")
    pilot_data = json.loads(PILOT_JSON.read_text(encoding="utf-8"))
    pilot_by_frame = {item["frame"]: item for item in pilot_data}

    # Map each execution result to its truth and prior Flash blind
    evaluated_items = []
    crop_items = []

    for r in results:
        fname = r["filename"]
        parsed = r["parsed"]
        is_crop = r["is_crop"]

        if is_crop:
            crop_items.append(r)
            continue

        truth_source = "PILOT_AUDIT_UNCHECKED"
        # For separated panels vs full frames
        if fname == "k0zm_panel_top.png":
            # Earlier state: 2-lot trade at 15:10
            truth = {"pos": -2, "entry": 25332, "sl": 25344, "tp": 25201}
            truth_source = "UNVERIFIED_LOCAL"  # not in the pilot audit file; hand-typed by the original run
            flash_blind = None
            frame_id = "k0zm_1510_1720.png (top panel, 15:10)"
        elif fname == "k0zm_panel_bottom.png":
            # Later state: 1-lot trade at 17:20 (matches pilot k0zm truth)
            truth = pilot_by_frame["k0zm_1510_1720.png"]["truth"]
            flash_blind = abr.parse_json_response(pilot_by_frame["k0zm_1510_1720.png"]["blind"])
            frame_id = "k0zm_1510_1720.png (bottom panel, 17:20)"
        else:
            ref = pilot_by_frame[fname]
            truth = ref["truth"]
            flash_blind = abr.parse_json_response(ref["blind"])
            frame_id = fname

        score = abr.score_fields(parsed or {}, truth)

        evaluated_items.append({
            "id": r["id"],
            "frame": frame_id,
            "filename": fname,
            "truth": truth,
            "truth_source": truth_source,
            "argon_parsed": parsed,
            "argon_scores": score,
            "flash_parsed": flash_blind,
            "raw_response": r["raw_response"],
            "seconds": r["seconds"],
            "timestamp": r["timestamp"],
        })

    # Seven-frame core summary (using the 6 original single panels + bottom panel of k0zm which represents the audited trade state)
    seven_frame_core = [item for item in evaluated_items if "top panel" not in item["frame"]]
    summary_7_core = abr.summarize_descriptive_counts(seven_frame_core)
    summary_flash_7 = flash_counts(seven_frame_core)

    # Full 8-panel summary including top panel
    summary_all_panels = abr.summarize_descriptive_counts(evaluated_items)

    print("Core 7-frame summary:", summary_7_core)
    print("All 8-panel summary:", summary_all_panels)

    # Save results_argon-low.json
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_payload = {
        "metadata": {
            "card": "argon-blind-read-7-frames",
            "model": "gemini-4-argon-low",
            "effort": "low",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "pilot_reference": str(PILOT_JSON.relative_to(REPO_ROOT)),
            "pilot_reference_trust": "UNVERIFIED",
        },
        "descriptive_counts_7_frames": summary_7_core,
        "flash_descriptive_counts_7_frames": summary_flash_7,
        "descriptive_counts_all_panels": summary_all_panels,
        "evaluations": evaluated_items,
        "crops": crop_items,
    }
    RESULTS_JSON.write_text(json.dumps(results_payload, indent=2), encoding="utf-8", newline="\n")
    print(f"Saved results to {RESULTS_JSON}")

    # Generate dated Layer Lab report
    print("=== Step 7 & 8: Generating dated Layer Lab report ===")
    generate_report(results_payload, REPORT_FILE)
    print(f"Saved report to {REPORT_FILE}")

    # Update TRIALS.md
    update_trials_ledger()
    print("Updated TRIALS.md")


def generate_report(data: Dict[str, Any], report_path: Path) -> None:
    evals = data["evaluations"]
    crops = data["crops"]
    counts = data["descriptive_counts_7_frames"]
    fcounts = data["flash_descriptive_counts_7_frames"]

    # Locate crop outputs
    k0zm_crop = next((c for c in crops if c["id"] == "crop_k0zm_target"), None)
    t6h_crop = next((c for c in crops if c["id"] == "crop_0550_stop"), None)

    k0zm_desc = k0zm_crop.get("descriptive_response", "").strip() if k0zm_crop else ""
    t6h_desc = t6h_crop.get("descriptive_response", "").strip() if t6h_crop else ""

    lines = [
        "# Layer Lab Report: argon-blind-read-7-frames",
        "",
        "## 1. Headline Numbers and Verdict",
        "",
        f"- Reader: `gemini-4-argon-low` (Antigravity CLI `agy.exe`, low effort, headless direct invocation).",
        f"- Pilot Reference Base: `UNVERIFIED` (`hard_results_gemini-3.8-flash-low.json`, our own 2026-10-12 audit, never independently re-read; every 'Truth' below inherits this). The k0zm top-panel reference (25332/25344/25201) is not in that file at all: UNVERIFIED_LOCAL, shown in the table but excluded from all counts.",
        f"- Evaluated Scope: 7 pilot frames (6 single panels + split 2-panel k0zm) plus 2 enlarged crops.",
        f"- Field-level Descriptive Counts (7-frame core: 28 total fields across pos, entry, stop, target):",
        f"  - Matches to known numeric truth: **{counts['matches']}**",
        f"  - Numeric mismatches: **{counts['mismatches']}**",
        f"  - Correct nulls (truth is null, reader returned null): **{counts['correct_nulls']}**",
        f"  - Missed nulls (truth is numeric, reader returned null): **{counts['missed_nulls']}**",
        f"  - Invented numbers (truth is null, reader invented a number): **{counts['invented_numbers']}** (Flash low: {fcounts['invented_numbers']}, same scoring; no difference)",
        f"  - Unverified reference fields ('?' in pilot audit): **{counts['unverified']}** (excluded from accuracy denominators)",
        "",
        "### Contested Crops (neither settled; a human read decides, not a model vote)",
        "1. **k0zm target (25200 vs 25206)**: CONTESTED.",
        "   - **Evidence**: One model (Argon low) reads a blue tag `25206` above a faint `25200` axis tick on the enlarged crop, and its full-panel read also gave 25206. Our audit says 25200 and Flash blind read 25200. That is one reader against the audit, so it is not settled; the audit value is not overturned. The 1 numeric mismatch in the counts is against this unconfirmed reference.",
        "2. **T6hDJcHrVBM_0550 stop**: CONTESTED / UNREADABLE.",
        "   - **Evidence**: On the enlarged 540x760 crop of the order area, Argon identified position `-2` at `24690`, target `2` lots at `24184`, and current price `24435`, but reported **'Stop Loss Label: None visible in this crop'** and returned `stop: null`. The stop loss line/label is completely overlapped/obscured by the position entry tag at `24690`.",
        "   - Flash's blind read had returned `stop: 24690` (an inferred value flagged by our audit). Argon returned `null` for stop on this crop (one run; not a general property).",
        "",
        "## 2. What was Run",
        "",
        "- Isolated scratch directory: `F:/MTS/scratch/argon_run/iso_<id>/` (single image per call; images never committed to repository).",
        "- agy CLI command template:",
        "  ```",
        '  C:/Users/E-ngineers/.gemini/bin/agy.exe --print "Open image <filename> in this folder. Return ONLY JSON {position,entry,stop,target}; each is a number or null. Use null if unreadable or absent. Never infer hidden values." --model gemini-4-argon-low --effort low',
        "  ```",
        "- Image preparation:",
        "  - `k0zm_1510_1720.png` split at row 373 boundary into `k0zm_panel_top.png` (earlier 2-lot state) and `k0zm_panel_bottom.png` (later 1-lot state).",
        "  - Target crop: `k0zm_target_crop.png` (y: 320..420, x: 280..480 of bottom panel).",
        "  - Stop crop: `T6hDJcHrVBM_0550_crop.png` (540x760 high-resolution crop of order region).",
        "",
        "## 3. Comparison Table (Argon low vs Flash low vs Pilot Reference)",
        "",
        "| Frame / Panel | Field | Truth (Audit) | Argon low | Flash low | Argon Score | Note |",
        "|---|---|---|---|---|---|---|",
    ]

    for ev in evals:
        fid = ev["frame"]
        t = ev["truth"]
        a = ev["argon_parsed"] or {}
        f = ev["flash_parsed"] or {}
        sc = ev["argon_scores"]

        for mf, tf in abr.FIELD_MAP.items():
            tv = t.get(tf)
            av = a.get(mf)
            fv = f.get(mf) if f else "N/A"
            status = sc.get(mf, "")
            note = ""
            if status == abr.INVENTED:
                note = "INVENTED (truth is null)"
            elif status == abr.UNVERIFIED:
                note = "UNVERIFIED (truth is '?')"
            elif tv is None and av is None:
                note = "Honest null"
            lines.append(f"| {fid} | {mf} | {tv} | {av} | {fv} | {status} | {note} |")

    lines += [
        "",
        "## 4. Enlarged Crop Transcriptions",
        "",
        "### Crop 1: k0zm Target (25200 vs 25206)",
        "- Image: `k0zm_target_crop.png`",
        "- Raw Argon Transcription:",
        "```",
        k0zm_desc,
        "```",
        "",
        "### Crop 2: T6hDJcHrVBM_0550 Stop",
        "- Image: `T6hDJcHrVBM_0550_crop.png`",
        "- Raw Argon Transcription:",
        "```",
        t6h_desc,
        "```",
        "",
        "## 5. Findings & Defect Ledger",
        "",
        "| Severity | File / Image | Finding | Classification | Disposition |",
        "|---|---|---|---|---|",
        "| MED | `k0zm_1510_1720.png` | Two-panel vertical stack mixes earlier state (stop 25344/25349) and later state (stop 25310). Split eliminates mixing. | E1 Data / Panel mixing | PASS: Separate panels evaluated cleanly. |",
        "| LOW | `k0zm` target | Argon reads tag `25206`; audit and Flash say `25200`. | E2 Definition / Precision | CONTESTED: needs a human read; audit not changed. |",
        "| LOW | `T6hDJcHrVBM_0550` stop | Stop loss label is overlapped and not readable. | E1 Data / Obscured field | CONTESTED: Marked unreadable / honest null. |",
        "",
        "## 6. Follow-up Cards",
        "",
        "- None created; this is a scoped Layer Lab run card.",
        "- Reference pilot base remains `UNVERIFIED` per Lab_Guy protocol; re-read by a human before any accuracy claim.",
    ]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def flash_counts(items):
    """Same scoring as Argon, applied to the stored Flash blind reads (truth-null + number = invented)."""
    pseudo = [{"truth": i["truth"], "parsed": i["flash_parsed"]} for i in items if i.get("flash_parsed")]
    return abr.summarize_descriptive_counts(pseudo)


def trials_headline(data):
    c = data["descriptive_counts_7_frames"]
    f = data["flash_descriptive_counts_7_frames"]
    return (f"Argon low, 7 frames, {c['total_fields']} fields (descriptive, UNVERIFIED reference): matches {c['matches']}, "
            f"mismatch {c['mismatches']}, correct null {c['correct_nulls']}, missed null {c['missed_nulls']}, "
            f"invented {c['invented_numbers']} (Flash {f['invented_numbers']}), unverified {c['unverified']}; "
            "k0zm target 25206 vs 25200 CONTESTED; 0550 stop CONTESTED; results in research/layer_lab/argon_blind_read/results_argon-low.json")


def rebuild_from_results():
    """Recompute counts, report and TRIALS row from the stored results (no model calls)."""
    data = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    data["metadata"]["pilot_reference_trust"] = "UNVERIFIED"
    for e in data["evaluations"]:
        e["truth_source"] = "UNVERIFIED_LOCAL" if "top panel" in e["frame"] else "PILOT_AUDIT_UNCHECKED"
        e["argon_scores"] = abr.score_fields(e["argon_parsed"] or {}, e["truth"])
    core = [e for e in data["evaluations"] if "top panel" not in e["frame"]]
    data["descriptive_counts_7_frames"] = abr.summarize_descriptive_counts(core)
    data["flash_descriptive_counts_7_frames"] = flash_counts(core)
    data["descriptive_counts_all_panels"] = abr.summarize_descriptive_counts(data["evaluations"])
    RESULTS_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8", newline=chr(10))
    generate_report(data, REPORT_FILE)
    update_trials_ledger()


def update_trials_ledger():
    """Add a counted trial row to TRIALS.md if not already present."""
    text = TRIALS_FILE.read_text(encoding="utf-8-sig")
    card_id = "argon-blind-read-7-frames"
    if f"| {card_id} |" in text:
        return

    date_str = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))["metadata"]["generated_utc"][:10]  # run date, not rebuild date
    cmd = 'C:/Users/E-ngineers/.gemini/bin/agy.exe --print "..." --model gemini-4-argon-low --effort low'
    data_range = "7 Tom frames + crops; pilot blind read comparison"
    headline = trials_headline(json.loads(RESULTS_JSON.read_text(encoding="utf-8")))

    row = f"| {date_str} | {card_id} | `{cmd}` | {data_range} | {headline} |\n"
    new_text = text.rstrip() + "\n" + row
    TRIALS_FILE.write_text(new_text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--rebuild" in sys.argv:
        rebuild_from_results()
    else:
        main()
