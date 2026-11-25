import base64
import cv2
import mediapipe as mp
import numpy as np
import torch
from PIL import Image
from model_registry import registry

def compute_laplacian_boundary_anomaly(crop):
    gray=cv2.cvtColor(cv2.resize(crop,(224,224)),cv2.COLOR_RGB2GRAY)
    lap=np.abs(cv2.Laplacian(gray,cv2.CV_64F))
    inner,total=np.var(lap[56:168,56:168]),np.var(lap)
    return float(np.clip(1.1*abs(inner-total)/max(inner,total,1e-8),.05,.95))

def analyze(frames):
    crops=[]; mar=[]; annotated=None; multiple=0
    with mp.solutions.face_mesh.FaceMesh(static_image_mode=False,max_num_faces=2,refine_landmarks=True,min_detection_confidence=.5) as mesh:
        for frame in frames:
            result=mesh.process(frame)
            faces=result.multi_face_landmarks or []
            if len(faces)!=1:
                mar.append(None); multiple+=int(len(faces)>1); continue
            h,w=frame.shape[:2]
            points=np.array([(p.x*w,p.y*h) for p in faces[0].landmark])
            width=np.linalg.norm(points[78]-points[308])
            mar.append(float(sum(np.linalg.norm(points[a]-points[b]) for a,b in [(82,87),(13,14),(312,317)])/(3*max(width,1e-6))))
            lo=points.min(axis=0); hi=points.max(axis=0); pad=(hi-lo)*.1
            x0,y0=np.maximum(lo-pad,0).astype(int); x1,y1=np.minimum(hi+pad,[w,h]).astype(int)
            if x1>x0 and y1>y0: crops.append((len(mar)-1,frame[y0:y1,x0:x1]))
            if annotated is None or len(mar)==len(frames)//2:
                annotated=frame.copy()
                for a,b in [(82,87),(13,14),(312,317),(78,308)]:
                    cv2.line(annotated,tuple(points[a].astype(int)),tuple(points[b].astype(int)),(70,230,192),2)
                cv2.rectangle(annotated,(x0,y0),(x1,y1),(70,230,192),1)
    base={'coverage':len(crops)/len(frames),'multiple_face_frames':multiple,'mar':mar,'thumbnail':None}
    if annotated is not None:
        _,jpg=cv2.imencode('.jpg',cv2.cvtColor(annotated,cv2.COLOR_RGB2BGR))
        base['thumbnail']='data:image/jpeg;base64,'+base64.b64encode(jpg).decode()
    if not crops: return {**base,'score':None,'reason':'No unambiguous face detected.'}
    selected=[crops[i] for i in np.linspace(0,len(crops)-1,min(30,len(crops)),dtype=int)]
    processor,model,fake_id=registry.get('visual'); scores=[]
    with torch.inference_mode():
        for start in range(0,len(selected),8):
            inputs=processor(images=[Image.fromarray(c) for _,c in selected[start:start+8]],return_tensors='pt').to(registry.device)
            scores.extend(model(**inputs).logits.softmax(-1)[:,fake_id].cpu().tolist())
    edges=[compute_laplacian_boundary_anomaly(c) for _,c in selected]
    deep=float(np.mean(scores)); edge=float(np.mean(edges))
    return {**base,'score':.8*deep+.2*edge,'deep_score':deep,'edge_score':edge,
            'samples':[{'time':i/15,'score':s} for (i,_),s in zip(selected,scores)],'reason':'ViT + report-defined Laplacian cue; heuristic is not calibrated.'}
