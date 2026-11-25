# DEEPSYNC | Start here

**Group 101 · Multimodal Deepfake Detection using Audio-Visual Consistency Analysis**

## On the prepared laptop

1. In File Explorer open **D:\2026\SEM 5\innfinal**. Double-click **START_DEEPSYNC.bat**. Keep the black terminal window open. The launcher uses the existing Python environment in the sibling deepfake_forensics folder. The two model checkpoints are already in this project's models folder.
2. Wait for the browser to open. If it does not open automatically once the terminal says the server is running, type **http://127.0.0.1:8101** in Chrome or Edge. Opening index.html directly will not start the upload service.
3. Click **Choose File**, open **demo**, select **oxford-short.mp4**, then click **Analyze video**. The first request loads the model weights. Show the result, the three scores, the face image and the two curves. Open **How this result was calculated** to see fusion details.
4. Repeat with **reversed-sound.mp4**. The video frames are identical. Listen to the changed soundtrack and compare the voice and timing scores. Then try **muted.mp4** to show how the system handles missing evidence.
5. You can also upload your own 5–10 second clip. Use one front-facing speaker, visible lips and clear speech. To stop the server, click its terminal and press **Ctrl+C**.

**If the local server is blocked:** Double-click **OFFLINE_DEMO.bat**, select a video, and wait. This runs the same models and opens a newly generated evidence page in the browser without using a network port. Repeat for the next video. The HTML includes the face thumbnail and signals. The terminal prints its temporary file path so you can remove it after the demo.

## What actually happened in an offline inference check on this laptop

The upload handler decoded these files, ran the real models on CUDA and produced the following results. Scores below are out of 100. Fresh installs, different library versions and hardware can cause small differences, especially for the reference clip, which is near the cutoff.

| Input | Face | Voice | Lip timing | Combined | What to point at |
|---|---:|---:|---:|---:|---|
| Oxford reference, 8 seconds | 63.9 | 2.0 | 50.7 | 54.0 | Below the 55 threshold, narrowly. A single high face score deserves discussion. |
| Same video, sound reversed | 63.9 | 77.0 | 59.1 | 73.1 | Above threshold. Voice changed most. The face score stayed the same. |
| Same video, audio removed | 63.9 | Unavailable | Unavailable | Inconclusive | The only usable branch was the face. |
| Invalid bytes named .mp4 | — | — | — | Upload rejected | The decoder checks the contents. |

First recorded processing time was 29.66 s, then 3.18 s for the reversed file and 2.63 s for the muted one. Times exclude launching Python and browser rendering. Seven additional numerical tests passed, including a recovery test with a known 267 ms delay. The Oxford clip is an execution example without a verified real/fake label here. Reversing its audio creates a known edit. It does not create an AI-generated voice.

## On a different Windows laptop

1. Extract the entire project ZIP to an ordinary folder, for example **Documents\DEEPSYNC**. Install 64-bit Python 3.12 with the Windows Python launcher. Install FFmpeg with FFprobe on PATH. One Windows option is to run **winget install --id Gyan.FFmpeg -e** in PowerShell. Reopen PowerShell and check **py -3.12 --version**, **ffmpeg -version** and **ffprobe -version**.
2. Double-click **SETUP_WINDOWS.bat** with internet access. It creates a private .venv, installs Python packages and downloads the two pinned model checkpoints. Allow several GB of disk space. The compact ZIP includes source and demo videos; the model weights alone total about 722 MB and are fetched during setup. The original prepared project folder already has these weights. To avoid downloading weights again, copy its models folder as well and install only the Python dependencies using the commands below.
3. Double-click **START_DEEPSYNC.bat**. Inference and the dashboard work offline once dependencies and models are present. The fresh-install path supports CPU inference; timing depends on the machine. Rehearse with the same laptop that will be used in the room.

Manual setup in the extracted folder matches the batch file:

    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe scripts\setup_models.py

## Reproduce the checks

On the prepared laptop, open PowerShell in the project folder:

    & '..\deepfake_forensics\venv\Scripts\python.exe' scripts\smoke.py
    python -m pytest -q tests

On a fresh installation replace the first command's interpreter and the second command's python with .\.venv\Scripts\python.exe. The smoke script calls the actual upload handler directly; it needs neither a browser nor a listening server.

## If something goes wrong in the room

| Symptom | Action |
|---|---|
| First analysis takes longer | Keep the terminal open. Rehearse one upload beforehand to load models into memory. |
| Browser cannot connect | Check the terminal for errors and confirm the URL and port. Use OFFLINE_DEMO.bat if the lab blocks local servers. |
| Model files missing | Run SETUP_WINDOWS.bat with internet before the presentation, or restore the complete models folder from the prepared laptop. |
| Clip rejected | Use a decodable video from 1 to 30 s, at most 100 MiB, within the supported resolution. Standard phone H.264/AAC MP4 is a convenient choice. |
| Inconclusive | Check for one clear visible face, speech and mouth movement. A silent or faceless result is an intended demonstration. |
| Module import error after moving folders | Run SETUP_WINDOWS.bat in the new folder. Copying a Windows virtual environment between machines can break its paths. |
| Port occupied | Reuse the running DEEPSYNC window or close its terminal with Ctrl+C before starting again. |
| Genuine-looking clip gets flagged | Show the branch breakdown and explain false positives. Avoid treating this as evidence against a person. |

Read **PANEL_NOTES.md** next for the five-person script, build record, worked numerical and viva answers.
