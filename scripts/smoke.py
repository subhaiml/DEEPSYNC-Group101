"""Offline end-to-end checks through the app's upload handler."""
import sys
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from app import analyze, dashboard

assert "DEEPSYNC" in Path(dashboard().path).read_text(encoding="utf-8-sig")
for name in ("oxford-short.mp4", "reversed-sound.mp4", "muted.mp4"):
    with (root / "demo" / name).open("rb") as clip:
        data = analyze(UploadFile(file=clip, filename=name))
    scores = [data[key]["score"] for key in ("visual", "audio", "sync", "fusion")]
    if name == "muted.mp4":
        assert scores[1:3] == [None, None] and "Inconclusive" in data["fusion"]["verdict"]
    else:
        assert all(isinstance(v, (float, int)) for v in scores) and data["visual"]["thumbnail"]
    print(name, data["device"], data["seconds"], scores, data["fusion"]["verdict"], flush=True)

try:
    analyze(UploadFile(file=BytesIO(b"invalid"), filename="broken.mp4"))
except HTTPException as exc:
    assert exc.status_code == 422
else:
    raise AssertionError("Invalid media was accepted")
print("Invalid media rejected.", flush=True)
