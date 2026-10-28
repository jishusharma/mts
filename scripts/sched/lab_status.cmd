@echo off
rem Codex layer lab status in plain words (MyTradingSys/system/LAYER_LAB.md, Checking on it). Copy or shortcut this to the desktop.
set CODEX_HOME=F:\codex_home
cd /d F:\MTS\mts-codex-lab
python scripts\dev\codex_run.py status
echo.
pause
