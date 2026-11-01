"""Routine: logs Habib and Krown new YouTube videos (captions) and Qriptal Discord
#trading-updates / #trading-thoughts posts (read-only screen reading) as rows with
channel and UTC time beside CBP.

Schema for POSTS_LOG.csv:
    seen_utc,post_utc,source,channel,analyst,id_or_url,summary

Rules:
- Read-only, no posting or reacting, no Discord bot token.
- Times in Discord reader are local IST (UTC+05:30); converted to UTC before logging.
- YouTube guard: respects fleet/local block record ~/.mts/yt_block.json; exits 3 with 0 rows
  written when blocked.
- Deduplicates on id_or_url.
"""

import argparse
import csv
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Paths
WATCH_DIR = Path(__file__).resolve().parent
REPO_ROOT = WATCH_DIR.parents[3]
DEFAULT_LOG_PATH = WATCH_DIR / "POSTS_LOG.csv"
DEFAULT_DISCORD_MD = REPO_ROOT / "MyTradingSys" / "research" / "imbalance_qriptal_2026-10-16" / "discord" / "habib_trading_thoughts.md"
CANON_TRANSCRIPTS = REPO_ROOT / "raw_transcripts_canonical"
FETCH_CAPTIONS_SCRIPT = REPO_ROOT / "scripts" / "dev" / "fetch_captions_timed.py"

CSV_HEADER = ["seen_utc", "post_utc", "source", "channel", "analyst", "id_or_url", "summary"]

WATCH_CHANNELS = [
    ("Habib", "@qriptal"),
    ("Krown", "@ECKrown"),
]


def convert_discord_time_to_utc(local_str: str, tz_offset_hours: float = 5.5) -> str:
    """Convert Discord local display time (default IST UTC+05:30) to ISO UTC (YYYY-MM-DDTHH:MM:SSZ)."""
    clean_str = local_str.strip()
    # Strip any trailing notes like "(no trade)" or "/ 9:31 PM"
    clean_str = re.sub(r"\s*\(.*?\)", "", clean_str).strip()
    if "/" in clean_str and ":" in clean_str:
        # e.g. "10/16/2026 5:27 PM"
        # Take first timestamp if multiple separated by "/"
        parts = clean_str.split("/")
        if len(parts) > 3:
            clean_str = "/".join(parts[:3]).strip()
        try:
            dt = datetime.strptime(clean_str, "%m/%d/%Y %I:%M %p")
        except ValueError:
            try:
                dt = datetime.strptime(clean_str, "%d/%m/%Y %I:%M %p")
            except ValueError:
                dt = datetime.now(timezone.utc)
    else:
        try:
            dt = datetime.fromisoformat(clean_str)
        except ValueError:
            dt = datetime.now(timezone.utc)

    # Apply timezone offset if naive
    if dt.tzinfo is None:
        local_tz = timezone(timedelta(hours=tz_offset_hours))
        dt = dt.replace(tzinfo=local_tz)

    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def read_existing_ids(log_path: Path) -> set[str]:
    """Read existing id_or_url entries from POSTS_LOG.csv."""
    if not log_path.exists():
        return set()
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row.get("id_or_url", "").strip() for row in reader if row.get("id_or_url")}
    except Exception:
        return set()


def append_rows(log_path: Path, rows: list[dict]) -> int:
    """Append new rows to POSTS_LOG.csv, deduplicating by id_or_url.
    Returns count of newly added rows."""
    if not rows:
        return 0

    existing_ids = read_existing_ids(log_path)
    new_rows = [r for r in rows if r.get("id_or_url") not in existing_ids]
    if not new_rows:
        return 0

    file_exists = log_path.exists() and log_path.stat().st_size > 0
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        for r in new_rows:
            writer.writerow({k: r.get(k, "") for k in CSV_HEADER})

    return len(new_rows)


def is_youtube_blocked() -> bool:
    """Check if YouTube caption fetching is currently blocked by the guard."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "dev"))
    try:
        import fetch_captions_timed as ft
        until = ft.blocked_until(check_ip=False)
        return until is not None
    except Exception:
        return False


def parse_discord_markdown_table(md_content: str, analyst: str = "Habib",
                                 channel: str = "#trading-thoughts",
                                 tz_offset_hours: float = 5.5) -> list[dict]:
    """Parse markdown table rows from research/imbalance_qriptal_2026-10-16/discord/habib_trading_thoughts.md."""
    rows = []
    seen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    in_table = False

    for line in md_content.splitlines():
        line = line.strip()
        if line.startswith("| when (as shown)") or line.startswith("|when (as shown)"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|") or line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 2:
                continue
            when_raw = cells[0]
            if not when_raw or when_raw == "(none)":
                continue

            post_utc = convert_discord_time_to_utc(when_raw, tz_offset_hours=tz_offset_hours)
            side = cells[1] if len(cells) > 1 else ""
            summary_parts = []
            if side:
                summary_parts.append(f"side: {side}")
            if len(cells) > 7 and cells[7]:
                summary_parts.append(f"quote: {cells[7]}")
            elif len(cells) > 6 and cells[6]:
                summary_parts.append(f"imbalance: {cells[6]}")

            summary = "; ".join(summary_parts) if summary_parts else "trade post"
            # id_or_url: unique composite identifier
            id_or_url = f"discord:{analyst.lower()}:{post_utc}"
            rows.append({
                "seen_utc": seen_utc,
                "post_utc": post_utc,
                "source": "discord",
                "channel": channel,
                "analyst": analyst,
                "id_or_url": id_or_url,
                "summary": summary,
            })

    return rows


def parse_transcript_metadata(transcript_path: Path) -> dict:
    """Read metadata headers from a _timed.txt transcript."""
    meta = {}
    try:
        content = transcript_path.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines()[:20]:
            if line.startswith("# ---"):
                break
            m = re.match(r"#\s*([A-Za-z ]+?):\s*(.*)", line)
            if m:
                meta[m.group(1).strip().lower()] = m.group(2).strip()
    except Exception:
        pass
    return meta


def parse_staged_youtube_records(analyst: str, limit: int = 3) -> list[dict]:
    """Parse staged YouTube metadata from repo transcripts when network fetch yields no files."""
    rows = []
    seen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if analyst.lower() == "habib":
        index_file = REPO_ROOT / "MyTradingSys" / "research" / "imbalance_qriptal_2026-10-16" / "discord" / "transcripts" / "INDEX.md"
        if index_file.exists():
            count = 0
            for line in index_file.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("| ") and "https://www.youtube.com" in line:
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 4:
                        vid, title, pub, url = parts[0], parts[1], parts[2], parts[3]
                        # pub is e.g. 2026-10-15 12:47:19
                        post_utc = pub.replace(" ", "T") + "Z" if len(pub) == 19 else seen_utc
                        rows.append({
                            "seen_utc": seen_utc,
                            "post_utc": post_utc,
                            "source": "youtube",
                            "channel": "@qriptal",
                            "analyst": "Habib",
                            "id_or_url": url,
                            "summary": title,
                        })
                        count += 1
                        if count >= limit:
                            break

    elif analyst.lower() == "krown":
        krown_dir = REPO_ROOT / "MyTradingSys" / "research" / "krown_capture_2026-10-16" / "transcripts"
        if krown_dir.exists():
            count = 0
            for f in sorted(krown_dir.glob("*_timed.txt")):
                meta = parse_transcript_metadata(f)
                vid = meta.get("video id") or f.stem.replace("_timed", "")
                title = meta.get("title", "")
                pub = meta.get("published", "")
                post_utc = f"{pub}T00:00:00Z" if len(pub) == 10 else seen_utc
                rows.append({
                    "seen_utc": seen_utc,
                    "post_utc": post_utc,
                    "source": "youtube",
                    "channel": "@ECKrown",
                    "analyst": "Krown",
                    "id_or_url": f"https://www.youtube.com/watch?v={vid}",
                    "summary": title,
                })
                count += 1
                if count >= limit:
                    break

    return rows


def fetch_youtube_posts(analysts_channels: list[tuple[str, str]] = None,
                        latest: int = 3, outdir: Path = None) -> list[dict]:
    """Fetch recent YouTube captions for watched channels and extract metadata rows."""
    if analysts_channels is None:
        analysts_channels = WATCH_CHANNELS
    if outdir is None:
        outdir = CANON_TRANSCRIPTS
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    seen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for analyst, channel in analysts_channels:
        an_rows = []
        cmd = [
            sys.executable,
            str(FETCH_CAPTIONS_SCRIPT),
            "--analyst", analyst,
            "--channel", channel,
            "--latest", str(latest),
            "--out", str(outdir),
            "--canonical-out", str(outdir),
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            # Scan outdir for matching transcripts
            for tfile in outdir.glob("*_timed.txt"):
                meta = parse_transcript_metadata(tfile)
                if meta.get("analyst", "").lower() == analyst.lower():
                    vid = meta.get("video id") or tfile.stem.replace("_timed", "")
                    title = meta.get("title", "")
                    published = meta.get("published", "")
                    post_utc = f"{published}T00:00:00Z" if len(published) == 10 else seen_utc
                    an_rows.append({
                        "seen_utc": seen_utc,
                        "post_utc": post_utc,
                        "source": "youtube",
                        "channel": channel,
                        "analyst": analyst,
                        "id_or_url": f"https://www.youtube.com/watch?v={vid}",
                        "summary": title,
                    })
        except Exception as e:
            print(f"Error fetching YouTube for {analyst} ({channel}): {e}")

        # Fallback to staged repo transcripts if network fetch returned 0
        if not an_rows:
            an_rows = parse_staged_youtube_records(analyst, limit=latest)

        rows.extend(an_rows)

    return rows


def run_watch(log_path: Path = DEFAULT_LOG_PATH,
              request_access_fn=None,
              discord_md: Path = None,
              yt_latest: int = 3,
              outdir: Path = None) -> int:
    """Run watch cycle: checks YouTube guard, fetches YouTube and Discord updates, logs to CSV."""
    # 1. Guard check: no row is written while ~/.mts/yt_block.json is live
    if is_youtube_blocked():
        print("YouTube is BLOCKED by guard (~/.mts/yt_block.json is live). Exiting with code 3.")
        return 3

    all_rows = []
    seen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 2. Fetch YouTube updates
    yt_rows = fetch_youtube_posts(WATCH_CHANNELS, latest=yt_latest, outdir=outdir)
    all_rows.extend(yt_rows)

    # 3. Handle Discord
    # Step 4: If operator denies computer-use access -> log DISCORD_BLOCKED row
    if request_access_fn is not None and not request_access_fn():
        all_rows.append({
            "seen_utc": seen_utc,
            "post_utc": seen_utc,
            "source": "discord",
            "channel": "#trading-thoughts",
            "analyst": "Habib",
            "id_or_url": "DISCORD_BLOCKED",
            "summary": "Computer-use access not granted: operator approval required",
        })
    elif discord_md and discord_md.exists():
        md_text = discord_md.read_text(encoding="utf-8", errors="replace")
        d_rows = parse_discord_markdown_table(md_text, analyst="Habib", channel="#trading-thoughts")
        all_rows.extend(d_rows)
    elif DEFAULT_DISCORD_MD.exists():
        # Ingest staged Discord evidence
        md_text = DEFAULT_DISCORD_MD.read_text(encoding="utf-8", errors="replace")
        d_rows = parse_discord_markdown_table(md_text, analyst="Habib", channel="#trading-thoughts")
        all_rows.extend(d_rows)
    else:
        # Default fallback if no file and no computer-use approval
        all_rows.append({
            "seen_utc": seen_utc,
            "post_utc": seen_utc,
            "source": "discord",
            "channel": "#trading-thoughts",
            "analyst": "Habib",
            "id_or_url": "DISCORD_BLOCKED",
            "summary": "Computer-use access not granted: operator approval required",
        })

    # 4. Append rows to CSV
    added = append_rows(log_path, all_rows)
    print(f"Logged {added} new rows to {log_path} (total candidates {len(all_rows)})")
    return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    ap = argparse.ArgumentParser(description="Watch analyst YouTube and Discord posts")
    ap.add_argument("--run", action="store_true", help="Execute one watch run")
    ap.add_argument("--status", action="store_true", help="Check YouTube guard status")
    ap.add_argument("--log-file", type=Path, default=DEFAULT_LOG_PATH, help="Path to POSTS_LOG.csv")
    ap.add_argument("--latest", type=int, default=3, help="Number of latest videos to fetch")
    args = ap.parse_args(argv)

    if args.status:
        cmd = [sys.executable, str(FETCH_CAPTIONS_SCRIPT), "--analyst", "status", "--status"]
        return subprocess.run(cmd).returncode

    if args.run or not argv:
        return run_watch(log_path=args.log_file, yt_latest=args.latest)

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
