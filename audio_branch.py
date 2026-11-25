import librosa
import numpy as np
import torch
from model_registry import registry

def analyze(y):
    if y is None or len(y)<16000 or np.sqrt(np.mean(y*y))<.003:
        return {'score':None,'reason':'Audio absent, too short, or too quiet.'}
    mfcc=librosa.feature.mfcc(y=y,sr=16000,n_mfcc=13)
    variance=float(np.mean(np.var(mfcc,axis=1)))
    heuristic=float(np.clip(1-variance/850,.08,.92))
    processor,model,fake_id=registry.get('audio'); scores=[]
    with torch.inference_mode():
        for i in range(0,len(y),64000):
            chunk=y[i:i+64000]
            if len(chunk)<16000 or np.sqrt(np.mean(chunk*chunk))<.003: continue
            inputs=processor(chunk,sampling_rate=16000,return_tensors='pt',padding=True).to(registry.device)
            scores.append(float(model(**inputs).logits.softmax(-1)[0,fake_id].cpu()))
    if not scores: return {'score':None,'reason':'Insufficient audible audio.'}
    deep=float(np.mean(scores))
    return {'score':.75*deep+.25*heuristic,'deep_score':deep,'mfcc_score':heuristic,'mfcc_variance':variance,
            'delta_variance':float(np.var(librosa.feature.delta(mfcc))),
            'spectral_flatness':float(np.mean(librosa.feature.spectral_flatness(y=y))),
            'zero_crossing_rate':float(np.mean(librosa.feature.zero_crossing_rate(y))),
            'chunks':len(scores),'reason':'Wav2Vec2 + report-defined MFCC cue. Music and non-speech are outside validation scope.'}
