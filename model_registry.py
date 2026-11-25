from pathlib import Path
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification, AutoFeatureExtractor, AutoModelForAudioClassification

ROOT = Path(__file__).resolve().parent
SPECS = {
    'visual': ('dima806/deepfake_vs_real_image_detection', '29e4cf9efc543845610045f6ba7e88e5cf9d9301'),
    'audio': ('MelodyMachine/Deepfake-audio-detection-V2', 'de3cde5a29c449bb5268814e421b46bf6ebdcd72'),
}

def get_working_device():
    if torch.cuda.is_available():
        try:
            torch.nn.Conv2d(1, 1, 1).cuda()(torch.ones(1, 1, 8, 8, device='cuda'))
            torch.cuda.synchronize()
            return 'cuda'
        except Exception:
            pass
    torch.set_num_threads(min(8, torch.get_num_threads()))
    return 'cpu'

class Registry:
    def __init__(self):
        self.device = get_working_device()
        self.cache = {}

    def get(self, branch):
        if branch not in self.cache:
            path = ROOT / 'models' / branch
            if not (path / 'config.json').exists():
                raise RuntimeError('Models not installed. Run python scripts/setup_models.py first.')
            pcls, mcls = (AutoImageProcessor, AutoModelForImageClassification) if branch == 'visual' else (AutoFeatureExtractor, AutoModelForAudioClassification)
            processor = pcls.from_pretrained(path, local_files_only=True)
            model = mcls.from_pretrained(path, local_files_only=True, use_safetensors=True).to(self.device).eval()
            labels = {int(k): str(v).lower() for k, v in model.config.id2label.items()}
            ids = [k for k,v in labels.items() if v in ('fake', 'spoof', 'deepfake')]
            if len(ids) != 1:
                raise RuntimeError(f'Unverified fake label mapping: {labels}')
            self.cache[branch] = (processor, model, ids[0])
        return self.cache[branch]

registry = Registry()
