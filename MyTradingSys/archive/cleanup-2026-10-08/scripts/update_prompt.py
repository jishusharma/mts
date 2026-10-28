#!/usr/bin/env python3
"""Reusable utility to write or update markdown files safely.

Usage:
    python update_prompt.py <file_path> <content_file>

This avoids PowerShell quoting/heredoc issues.
"""
import sys
from pathlib import Path


def write_markdown(file_path: str, content: str) -> None:
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {p} ({len(content)} chars)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_prompt.py <file_path> <content_file>")
        sys.exit(1)
    file_path = sys.argv[1]
    content_file = sys.argv[2]
    content = Path(content_file).read_text(encoding="utf-8")
    write_markdown(file_path, content)
