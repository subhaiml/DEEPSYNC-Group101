"""Local upload endpoint. All three scores are computed from the uploaded bytes."""
from pathlib import Path
from subprocess import TimeoutExpired
from tempfile import TemporaryDirectory
from threading import Lock
from time import perf_counter

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

import audio_branch
import consistency_fusion
import processor
import visual_branch
from model_registry import registry

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="DEEPSYNC")
inference_lock = Lock()


@app.get("/")
def dashboard():
    return FileResponse(ROOT / "index.html")


@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    if not inference_lock.acquire(blocking=False):
        raise HTTPException(409, "Another clip is being analyzed. Try again in a moment.")
    try:
        with TemporaryDirectory(prefix="deepsync-") as work:
            source = Path(work) / "upload"
            with source.open("wb") as target:
                while chunk := file.file.read(1024 * 1024):
                    if target.tell() + len(chunk) > 100 * 1024 * 1024:
                        raise HTTPException(413, "Choose a clip smaller than 100 MiB.")
                    target.write(chunk)
            start = perf_counter()
            frames, waveform, media = processor.prepare(source, work)
            visual = visual_branch.analyze(frames)
            audio = audio_branch.analyze(waveform)
            sync = consistency_fusion.analyze(visual.pop("mar"), waveform)
            fusion = consistency_fusion.fuse(visual["score"], audio["score"], sync["score"])
            if visual["coverage"] < 0.6:
                fusion["verdict"] = "Inconclusive"
                fusion["reason"] = "One clear face was visible in fewer than 60% of frames."
            return dict(media=media, visual=visual, audio=audio, sync=sync, fusion=fusion,
                        device=registry.device, seconds=round(perf_counter() - start, 2))
    except TimeoutExpired as exc:
        raise HTTPException(422, "Decoding took too long. Try a shorter MP4.") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        file.file.close()
        inference_lock.release()

