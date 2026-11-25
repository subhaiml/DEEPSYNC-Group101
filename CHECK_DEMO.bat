@echo off
cd /d "%~dp0"
set "HF_HUB_OFFLINE=1"
set "NUMBA_CACHE_DIR=%LOCALAPPDATA%\DEEPSYNC\jit"
".venv\Scripts\python.exe" scripts\smoke.py
if errorlevel 1 goto :failure
echo READY: Both model checkpoints ran, all three clips were processed, and corrupt media was rejected.
pause
exit /b 0
:failure
echo CHECK FAILED. Save the error above before closing the window.
pause
exit /b 1
