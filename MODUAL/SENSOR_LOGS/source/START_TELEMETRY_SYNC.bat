@echo off
title TELEMETRY BUFFER & SNAPSHOT SYNC DAEMON - 075203003486_10152484_20260724124936
echo ====================================================================
echo TELEMETRY BUFFER & SNAPSHOT SYNC DAEMON - HOME_HALINH
echo PROVENANCE: 075203003486_10152484_20260724124936
echo CANONICAL: 0000_THE_MASTER_TEACHER.md - HÀ LINH (LÃNH ĐẠO)
echo ====================================================================
REM Run from the supplied script carrier. Python locates real C:/Dropbox data first.
if not exist "%~dp0telemetry_buffer_sync.py" (
  echo Cannot find telemetry_buffer_sync.py alongside this launcher.
  exit /b 2
)
REM Explicit interactive daemon mode; Scheduled Task without arguments is one-shot.
python "%~dp0telemetry_buffer_sync.py" --loop
pause
