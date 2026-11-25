"""Bounded media decoding with original audio/video start-time alignment."""
import json
import subprocess
from pathlib import Path
import cv2
import numpy as np
import soundfile as sf

FPS = 15
MAX_SECONDS = 30

def run(args):
    result = subprocess.run(args, capture_output=True, timeout=120)
    if result.returncode:
        raise ValueError('Unable to decode media. Please use a valid MP4, MOV or WebM video.')
    return result.stdout

def prepare(path, work):
    info = json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    video = next((s for s in info['streams'] if s['codec_type']=='video'), None)
    audio = next((s for s in info['streams'] if s['codec_type']=='audio'), None)
    if not video:
        raise ValueError('This file has no video stream.')
    duration = float(info['format'].get('duration', 0))
    if duration <= 0 or duration > MAX_SECONDS:
        raise ValueError(f'Use a clip between 1 and {MAX_SECONDS} seconds. This file is {duration:.1f}s.')
    if int(video['width'])*int(video['height']) > 3840*2160:
        raise ValueError('Maximum input resolution is 3840 × 2160.')
    out = Path(work)/'frames.mp4'
    run(['ffmpeg','-v','error','-y','-i',str(path),'-map','0:v:0','-an','-vf',"fps=15,scale=640:640:force_original_aspect_ratio=decrease:force_divisible_by=2",'-t',str(MAX_SECONDS),str(out)])
    cap = cv2.VideoCapture(str(out)); frames=[]
    while len(frames) < FPS*MAX_SECONDS:
        ok, frame = cap.read()
        if not ok: break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    cap.release()
    if len(frames)<15:
        raise ValueError('At least one second of decodable video is required.')
    y = None
    if audio:
        wav=Path(work)/'audio.wav'
        run(['ffmpeg','-v','error','-y','-i',str(path),'-map','0:a:0','-ac','1','-ar','16000','-t',str(MAX_SECONDS),str(wav)])
        y,_=sf.read(wav,dtype='float32')
        offset=round((float(audio.get('start_time',0))-float(video.get('start_time',0)))*16000)
        extent = round(len(frames) * 16000 / FPS)
        offset = max(-len(y), min(offset, extent))
        y=np.pad(y,(max(0,offset),0))[max(0,-offset):][:extent]
    return frames, y, {'duration':duration,'fps':FPS,'sample_rate':16000,'frames':len(frames),'has_audio':audio is not None}

