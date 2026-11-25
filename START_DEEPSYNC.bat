@echo off
cd /d "%~dp0"
set "HF_HUB_OFFLINE=1"
set "NUMBA_CACHE_DIR=%LOCALAPPDATA%\DEEPSYNC\jit"
set "PY=python"
if exist "..\deepfake_forensics\venv\Scripts\python.exe" set "PY=..\deepfake_forensics\venv\Scripts\python.exe"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
"%PY%" launch.py
if errorlevel 1 pause

