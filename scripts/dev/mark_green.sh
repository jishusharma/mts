#!/usr/bin/env bash
# CI mark-green step (CI_SPEED_DIAGNOSIS 2026-10-22 #1): publish <sha> as green/fast-track unless the published green SHA
# is not an ancestor of <sha> (an older, slower run finishing after a newer one must never move the live pointer backwards).
# Usage: mark_green.sh <sha> [remote]. Needs full history (checkout fetch-depth: 0).
set -euo pipefail
sha="$1"
remote="${2:-origin}"
if git fetch --quiet "$remote" "+refs/heads/green/fast-track:refs/remotes/$remote/green/fast-track" 2>/dev/null; then
  green="$(git rev-parse "refs/remotes/$remote/green/fast-track")"
  if ! git merge-base --is-ancestor "$green" "$sha"; then
    echo "mark-green: skipped, green/fast-track ($green) is not an ancestor of $sha (a newer SHA is already green)"
    exit 0
  fi
fi
git push --force "$remote" "$sha:refs/heads/green/fast-track"
