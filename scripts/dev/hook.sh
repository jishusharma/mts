#!/bin/sh
# Hook launcher: windowless on Windows (pythonw + nowin_hook.py), plain python everywhere else (cloud, Linux).
# Usage in .claude/settings.json: sh "$CLAUDE_PROJECT_DIR/scripts/dev/hook.sh" "$CLAUDE_PROJECT_DIR/scripts/dev/<script>.py" <args>
here=$(dirname "$0")
if command -v pythonw >/dev/null 2>&1; then
  exec pythonw "$here/nowin_hook.py" "$@"
fi
exec python "$@"
