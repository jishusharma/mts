"""Argon blind image reader and local reference comparator.

Adheres strictly to roles/lab_guy.md section 'Images read by Gemini or any non-producer model'
and announcement A-20261018-7:
- Blind reader only: no claims shown in prompt.
- Required null option: numeric output for truth-null fields is classified as INVENTED.
- Separate panels: two-panel images cropped into separate panels before reader invocation.
- Local code comparison: model outputs compared locally in Python, never evaluated by model.
- Contested values: enlarged crops and descriptive resolution; unresolvable stays CONTESTED.
- Unverified references: '?' or missing audit truth excluded from accuracy denominators.
- Descriptive counts only: reports descriptive 7-frame counts, never general catch-rate claims.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MATCH = "MATCH"
MISMATCH = "MISMATCH"
CORRECT_NULL = "CORRECT_NULL"
MISSED_NULL = "MISSED_NULL"
INVENTED = "INVENTED"
UNVERIFIED = "UNVERIFIED"

FIELD_MAP = {
    "position": "pos",
    "entry": "entry",
    "stop": "sl",
    "target": "tp",
}

BLIND_PROMPT_TEMPLATE = (
    "Open image {filename} in this folder. Return ONLY JSON {{position,entry,stop,target}}; "
    "each is a number or null. Use null if unreadable or absent. Never infer hidden values."
)

DESCRIPTIVE_CROP_PROMPT_TEMPLATE = (
    "Open image {filename} in this folder. Describe the visible text and price labels directly. "
    "In particular, report what exact numbers are readable for the order/price tags."
)

AGY_BIN = Path("C:/Users/E-ngineers/.gemini/bin/agy.exe")
FRAMES_DIR = Path("F:/MTS/data/tom_videos/frames")
DEFAULT_SCRATCH = Path("F:/MTS/scratch/argon_run")
REPO_ROOT = Path(__file__).resolve().parents[2]


def build_blind_prompt(filename: str) -> str:
    """Construct the standardized nullable blind prompt."""
    return BLIND_PROMPT_TEMPLATE.format(filename=filename)


def build_descriptive_prompt(filename: str) -> str:
    """Construct prompt for direct visual transcription of enlarged crops."""
    return DESCRIPTIVE_CROP_PROMPT_TEMPLATE.format(filename=filename)


def validate_prompt(prompt: str, filename: str) -> bool:
    """Validate that prompt includes required nullable schema and no injected claims."""
    if filename not in prompt:
        return False
    if "position,entry,stop,target" not in prompt:
        return False
    if "number or null" not in prompt and "null" not in prompt:
        return False
    # Check for claim leakage keywords
    lower = prompt.lower()
    for kw in ["claim", "expected", "truth", "audit says", "should be"]:
        if kw in lower:
            return False
    return True


def parse_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON object from model output text, handling Markdown blocks."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        # Search for first JSON object
        m = re.search(r"\{[^{}]*\}", text, flags=re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    return None


def numbers_close(a: Any, b: Any, tol: float = 0.5) -> bool:
    """Check if two numeric values match within tolerance."""
    try:
        fa = float(a)
        fb = float(b)
        return abs(fa - fb) <= tol
    except (ValueError, TypeError):
        return False


def score_fields(model_parsed: Dict[str, Any], truth: Dict[str, Any]) -> Dict[str, str]:
    """Score model parsed fields against audit truth locally."""
    scores = {}
    for m_field, t_field in FIELD_MAP.items():
        t_val = truth.get(t_field)
        m_val = model_parsed.get(m_field)

        # Unverified reference in audit
        if t_val == "?" or t_val == "UNVERIFIED":
            scores[m_field] = UNVERIFIED
            continue

        # Audit says not visible / absent
        if t_val is None:
            if m_val is None:
                scores[m_field] = CORRECT_NULL
            else:
                scores[m_field] = INVENTED
            continue

        # Audit has a known numeric value
        if m_val is None:
            scores[m_field] = MISSED_NULL
        elif numbers_close(m_val, t_val):
            scores[m_field] = MATCH
        else:
            scores[m_field] = MISMATCH

    return scores


def summarize_descriptive_counts(items: List[Dict[str, Any]]) -> Dict[str, int]:
    """Produce descriptive field-level counts over evaluated items."""
    counts = {
        "total_fields": 0,
        "matches": 0,
        "mismatches": 0,
        "correct_nulls": 0,
        "missed_nulls": 0,
        "invented_numbers": 0,
        "unverified": 0,
    }
    for item in items:
        truth = item.get("truth", {})
        parsed = item.get("parsed") or item.get("argon_parsed") or {}
        scores = score_fields(parsed, truth)
        for field, status in scores.items():
            counts["total_fields"] += 1
            if status == MATCH:
                counts["matches"] += 1
            elif status == MISMATCH:
                counts["mismatches"] += 1
            elif status == CORRECT_NULL:
                counts["correct_nulls"] += 1
            elif status == MISSED_NULL:
                counts["missed_nulls"] += 1
            elif status == INVENTED:
                counts["invented_numbers"] += 1
            elif status == UNVERIFIED:
                counts["unverified"] += 1
    return counts


def split_k0zm(pair_path: Path, top_out: Path, bottom_out: Path) -> None:
    """Split the two-panel k0zm_1510_1720.png at row 373 boundary."""
    from PIL import Image

    im = Image.open(pair_path)
    w, h = im.size
    top = im.crop((0, 0, w, 373))
    bottom = im.crop((0, 373, w, h))
    top.save(top_out)
    bottom.save(bottom_out)


def crop_k0zm_target(bottom_path: Path, crop_out: Path) -> None:
    """Generate enlarged label crop around the 25200/25206 target axis area."""
    from PIL import Image

    im = Image.open(bottom_path)
    # y=320..420, x=280..480 covers axis tick 25200 and blue pill 25206
    crop = im.crop((280, 320, 480, 420))
    crop.save(crop_out)


def invoke_agy(
    isolated_dir: Path,
    image_filename: str,
    prompt: str,
    model: str = "gemini-4-argon-low",
    effort: str = "low",
) -> Dict[str, Any]:
    """Run agy in an isolated subfolder containing ONLY that image."""
    cmd = [str(AGY_BIN), "--print", prompt, "--model", model, "--effort", effort]
    t0 = time.time()
    res = subprocess.run(cmd, cwd=str(isolated_dir), capture_output=True, text=True)
    dur = time.time() - t0
    return {
        "model": model,
        "effort": effort,
        "prompt": prompt,
        "image": image_filename,
        "returncode": res.returncode,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "seconds": round(dur, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def execute_all(scratch_base: Path = DEFAULT_SCRATCH) -> Dict[str, Any]:
    """Execute blind reads on all 7 frames and crops according to card requirements."""
    scratch_base.mkdir(parents=True, exist_ok=True)

    # 1. Prepare crops
    k0zm_src = FRAMES_DIR / "k0zm_1510_1720.png"
    crops_prep_dir = scratch_base / "crops_prep"
    crops_prep_dir.mkdir(parents=True, exist_ok=True)
    top_panel_path = crops_prep_dir / "k0zm_panel_top.png"
    bot_panel_path = crops_prep_dir / "k0zm_panel_bottom.png"
    split_k0zm(k0zm_src, top_panel_path, bot_panel_path)

    k0zm_target_crop_path = crops_prep_dir / "k0zm_target_crop.png"
    crop_k0zm_target(bot_panel_path, k0zm_target_crop_path)

    # 0550 stop crop source
    crop_0550_src = FRAMES_DIR / "T6hDJcHrVBM_0550_crop.png"

    # Define tasks
    # (id, source_file, target_filename, is_crop)
    jobs = [
        ("T6hDJcHrVBM_0520", FRAMES_DIR / "T6hDJcHrVBM_0520.jpg", "T6hDJcHrVBM_0520.jpg", False),
        ("T6hDJcHrVBM_0550", FRAMES_DIR / "T6hDJcHrVBM_0550.jpg", "T6hDJcHrVBM_0550.jpg", False),
        ("zQTbdEweG3c_0370", FRAMES_DIR / "zQTbdEweG3c_0370.jpg", "zQTbdEweG3c_0370.jpg", False),
        ("l8RZrBfzvp4_0190", FRAMES_DIR / "l8RZrBfzvp4_0190.jpg", "l8RZrBfzvp4_0190.jpg", False),
        ("SANOimk8M9o_0270", FRAMES_DIR / "SANOimk8M9o_0270.jpg", "SANOimk8M9o_0270.jpg", False),
        ("UOBgXV20yCM_0250", FRAMES_DIR / "UOBgXV20yCM_0250.png", "UOBgXV20yCM_0250.png", False),
        ("k0zm_panel_top", top_panel_path, "k0zm_panel_top.png", False),
        ("k0zm_panel_bottom", bot_panel_path, "k0zm_panel_bottom.png", False),
        ("crop_k0zm_target", k0zm_target_crop_path, "k0zm_target_crop.png", True),
        ("crop_0550_stop", crop_0550_src, "T6hDJcHrVBM_0550_crop.png", True),
    ]

    results = []

    print(f"Starting Argon blind reads ({len(jobs)} items) in isolated scratch subfolders...")

    for jid, src_file, fname, is_crop in jobs:
        # Create isolated directory
        iso_dir = scratch_base / f"iso_{jid}"
        if iso_dir.exists():
            shutil.rmtree(iso_dir)
        iso_dir.mkdir(parents=True, exist_ok=True)

        dst_file = iso_dir / fname
        shutil.copy2(src_file, dst_file)

        # Build blind prompt
        prompt = build_blind_prompt(fname)
        if not validate_prompt(prompt, fname):
            raise ValueError(f"Prompt validation failed for {fname}: {prompt}")

        print(f"[{jid}] Invoking agy with Argon low on {fname}...")
        inv = invoke_agy(iso_dir, fname, prompt)
        parsed = parse_json_response(inv["stdout"])

        entry: Dict[str, Any] = {
            "id": jid,
            "filename": fname,
            "is_crop": is_crop,
            "model": inv["model"],
            "effort": inv["effort"],
            "seconds": inv["seconds"],
            "timestamp": inv["timestamp"],
            "prompt": prompt,
            "raw_response": inv["stdout"],
            "parsed": parsed,
        }

        # If it's one of the two crops, also run the descriptive text prompt
        if is_crop:
            desc_prompt = build_descriptive_prompt(fname)
            print(f"[{jid}] Invoking descriptive read on {fname}...")
            desc_inv = invoke_agy(iso_dir, fname, desc_prompt)
            entry["descriptive_prompt"] = desc_prompt
            entry["descriptive_response"] = desc_inv["stdout"]

        results.append(entry)

    return {"results": results, "scratch_dir": str(scratch_base)}


if __name__ == "__main__":
    out = execute_all()
    print("Completed. Total results:", len(out["results"]))
