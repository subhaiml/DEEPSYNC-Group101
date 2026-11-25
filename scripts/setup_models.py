"""Download pinned, safetensors-only public model weights for offline inference."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from huggingface_hub import snapshot_download
from model_registry import SPECS, ROOT
for branch, (repo, revision) in SPECS.items():
    print(f'Downloading {branch}: {repo}', flush=True)
    snapshot_download(repo, revision=revision, local_dir=ROOT/'models'/branch,
                      allow_patterns=['config.json', 'preprocessor_config.json', 'model.safetensors', 'README.md'])
print('Models ready. Inference runs locally without network access.')

