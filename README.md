# DEEPSYNC | Group 101

Multimodal deepfake detection using the face, voice and lip timing in a short video.

## Clone and run on Windows

Install Git for Windows with Git LFS. Run git lfs install before cloning using the HTTPS URL under GitHub's Code button. Inside the cloned folder run:

    git lfs pull
    git lfs fsck

Both pretrained checkpoints are tracked in models/. Install 64-bit Python 3.12 and FFmpeg with ffprobe available on PATH. Double-click SETUP_WINDOWS.bat with internet available for Python dependencies. Wait for READY after the real inference checks. Then double-click START_DEEPSYNC.bat and open http://127.0.0.1:8101.

OPEN_ME_FIRST.txt has beginner-friendly installation commands and the demo order. PANEL_NOTES.md contains five speaking parts and viva answers. The original and reversed-sound examples have identical pictures. Compare the two voice scores, then show why muted.mp4 gives an inconclusive verdict. Source and attribution for the clips are in demo/README.md.
