"""Transparent report fusion and conservative evidence-availability handling."""
import numpy as np

def normalize(x):
    return (x-np.min(x))/max(float(np.ptp(x)),1e-8)

def correlate(mar, rms, valid=None):
    m=np.asarray(mar,dtype=float); r=np.asarray(rms,dtype=float)
    valid=np.isfinite(m) if valid is None else np.asarray(valid)&np.isfinite(m)
    if valid.sum()<20 or np.std(m[valid])<.005 or np.max(r)<.003:
        return {'score':None,'reason':'Insufficient visible articulation or audible energy.','lags':[]}
    m=normalize(np.where(valid,m,np.nanmedian(m[valid])))
    r=normalize(r)
    m=np.convolve(np.pad(m,(1,1),mode='edge'),np.ones(3)/3,mode='valid')
    r=np.convolve(np.pad(r,(1,1),mode='edge'),np.ones(3)/3,mode='valid')
    lags=[]
    for lag in range(-6,7):
        a,b=(m[:-lag],r[lag:]) if lag>0 else (m[-lag:],r[:lag]) if lag<0 else (m,r)
        mask=(valid[:-lag] if lag>0 else valid[-lag:] if lag<0 else valid)&(b>.15)
        corr=None
        if mask.sum()>=15 and np.std(a[mask])>.02 and np.std(b[mask])>.02:
            corr=float(np.corrcoef(a[mask],b[mask])[0,1])
        lags.append({'lag_ms':round(lag*1000/15),'correlation':corr})
    usable=[x for x in lags if x['correlation'] is not None]
    base={'lags':lags,'mouth':m.tolist(),'energy':r.tolist(),'speech_fraction':float(np.mean(r>.15))}
    if not usable: return {**base,'score':None,'reason':'Not enough varying audio-active frames for correlation.'}
    best=max(usable,key=lambda x:x['correlation'])
    return {**base,'score':float(np.clip(1-best['correlation'],.08,.92)),
            'peak_correlation':best['correlation'],'lag_ms':best['lag_ms'],
            'reason':'Energy-gated geometric correlation; not phoneme recognition or proof of manipulation.'}

def analyze(mar,y):
    if y is None: return {'score':None,'reason':'No audio stream.','lags':[]}
    rms=[]
    for i in range(len(mar)):
        c=round(i/15*16000); segment=y[max(0,c-800):c+800]
        rms.append(float(np.sqrt(np.mean(segment**2))) if len(segment) else 0.)
    result=correlate([np.nan if v is None else v for v in mar],rms)
    result['timeline']=[{'time':round(i/15,3),'mouth':v,'rms':rms[i]} for i,v in enumerate(mar)]
    windows=[]
    for i in range(0,len(mar)-44,30):
        window=correlate([np.nan if v is None else v for v in mar[i:i+45]],rms[i:i+45])
        windows.append({'start':i/15,'end':(i+45)/15,'score':window['score'],'lag_ms':window.get('lag_ms')})
    result['windows']=windows
    return result

def fuse(visual,audio,sync):
    raw={'visual':visual,'audio':audio,'sync':sync}
    available={k:float(v) for k,v in raw.items() if v is not None}
    if not available: return {'score':None,'verdict':'Inconclusive','reason':'No usable evidence.','available':[]}
    effective=available.copy()
    gate=visual is not None and audio is not None and sync is not None and visual<.38 and audio<.38 and sync<.8
    if gate: effective['sync']*=.55
    weights={'visual':.4,'audio':.35,'sync':.25}
    consensus=sum(weights[k]*v for k,v in effective.items())/sum(weights[k] for k in effective)
    score=.6*max(effective.values())+.4*consensus
    complete=len(available)==3
    verdict=('Manipulation indicators' if score>=.55 else 'Low manipulation indicators') if complete else 'Inconclusive · partial evidence'
    return {'score':score,'verdict':verdict,'naive_average':float(np.mean(list(available.values()))),
            'consensus':consensus,'gate_applied':bool(gate),'effective':effective,'dominant':max(effective,key=effective.get),
            'available':list(available),'threshold':.55,'complete':complete,
            'reason':'Uncalibrated suspicion index, not probability of authenticity. Missing evidence never counts as authentic.'}
