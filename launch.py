"""Preflight and open the local dashboard once its server is ready."""
import os
import shutil
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
URL = "http://127.0.0.1:8101"
for tool in ("ffprobe", "ffmpeg"):
    if not shutil.which(tool):
        sys.exit(f"{tool} is missing. Follow the fresh setup in START_HERE.md.")
for branch in ("visual", "audio"):
    if not (ROOT / "models" / branch / "model.safetensors").is_file():
        sys.exit("Model weights are missing. Run SETUP_WINDOWS.bat first.")
with socket.socket() as probe:
    if probe.connect_ex(("127.0.0.1", 8101)) == 0:
        sys.exit("Port 8101 is already occupied. Check the existing demo window or close the other server.")
print(f"Starting DEEPSYNC. Keep this window open. Dashboard: {URL}", flush=True)

def open_when_ready():
    for _ in range(240):
        try:
            with urllib.request.urlopen(URL, timeout=1) as page:
                if page.status == 200:
                    webbrowser.open(URL)
                    return
        except OSError:
            time.sleep(1)

threading.Thread(target=open_when_ready, daemon=True).start()
import uvicorn
uvicorn.run("app:app", host="127.0.0.1", port=8101)
