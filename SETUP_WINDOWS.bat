@echo off
cd /d "%~dp0"
where ffmpeg >nul 2>&1 || goto :media
where ffprobe >nul 2>&1 || goto :media
py -3.12 -c "import struct; assert struct.calcsize('P') == 8" || goto :python
if not exist ".venv\Scripts\python.exe" py -3.12 -m venv .venv
if errorlevel 1 goto :failure
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failure
echo Dependencies installed. Checking the included models and three clips...
call CHECK_DEMO.bat
exit /b %errorlevel%
:python
echo Install 64-bit Python 3.12 including the Python Launcher, then reopen setup.
goto :failure
:media
echo Install FFmpeg from PowerShell with: winget install --id Gyan.FFmpeg -e
echo Close this window and reopen setup after installation.
:failure
echo Setup incomplete. Read the first error above.
pause
exit /b 1
