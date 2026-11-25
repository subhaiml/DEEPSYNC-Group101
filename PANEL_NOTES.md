# DEEPSYNC | Group 101 panel notebook

## The 30-second answer everyone should know

“We upload a short video of one person speaking. Our program measures three things: signs of manipulation in the face, signs of synthetic speech, and whether mouth opening follows the sound. Two pretrained models do the first two jobs. We combine their outputs with measurable signal features and show the evidence behind the final score. If part of the evidence is missing, the system can return inconclusive.”

Banglish: Ekta manush kotha bolchhe emon chhoto video dao. Face-ta dekhte edited lagchhe ki? Voice-e synthetic pattern achhe ki? Mukh kholar sathe awajer timing milchhe ki? Ei tinte signal miliye app ekta score dey. Score beshi hole video-ta aro check korte hobe.

## Who says what (proposed rehearsal roles)

These are speaking assignments. Describe actual team contributions after each person has run and understood their part.

| Person | Time | What to say and show |
|---|---:|---|
| Subharthi | 40 s | Introduce the single-channel blind spot. Open the app, select the reference clip and press Analyze. Explain that Python is running on this laptop. |
| Uttor | 45 s | Point at the face crop. “We take evenly spaced face samples, score each with ViT and compare sharpness inside and around the face.” |
| Snehal | 45 s | Point at Voice. “One model reads short waveform chunks. We also measure how the spectral envelope changes across time.” Play the reversed-sound example before analyzing it. |
| Sristi | 50 s | Point to the green mouth and orange energy curves. Explain why a short delay is allowed. Compare the original and edited timing scores. |
| Chiranjeeb | 45 s | Explain the final score, show the muted clip and its missing branches, and give one failure case. Close with the evaluation you would do next. |

During first model load, the other speakers can explain sampling and the branch models. If the panel interrupts, lead with the one-sentence answer, then point to the number, picture or code that supports it.

## Build record and code tour

1. Read the final report, especially Chapter 4. The supplied early proposal called for a CNN. The final report names a pretrained Vision Transformer. The implemented face classifier follows the final report. Use the term “frame-based visual classifier” if describing the original proposal and final build together.
2. Located earlier local DEEPSYNC implementations and the two complete model checkpoints on the development laptop. Reused the analytic modules from the earlier deepfake-astra project. This version simplifies the upload server and interface. Coding assistance was used for integration, interface, launcher, testing and notes. The group can demonstrate its understanding by making a new test clip, predicting which branch will change and checking the result.
3. processor.py calls FFprobe to look inside the uploaded file and FFmpeg to decode it. Video containers hold separate streams. Video becomes RGB frames at 15 per second, scaled to fit 640 by 640. Audio becomes a mono waveform with 16,000 samples per second. Stream start times are aligned. This implementation accepts up to 30 seconds for bounded memory and turnaround. The report illustrates a ten-second analysis.
4. visual_branch.py runs MediaPipe Face Mesh. It accepts frames with one detected face, uses landmark bounds with a 10% margin and records the mouth opening for each valid frame. Using the mesh to find both the crop and mouth avoids a separate detection pass. Lost or ambiguous frames have no mouth measurement.
5. The face model inspects up to 30 evenly spaced crops, eight at a time. It splits each image into patches and uses attention to compare regions. The model's fake-class outputs are averaged. OpenCV also calculates the strength of intensity changes with a Laplacian. We compare variance in the central half-width square with variance over the entire crop. A sharpness discontinuity can accompany blending. Glasses, shadows and compression can also produce it.
6. audio_branch.py evaluates up to four seconds per model call, ignores chunks shorter than one second or too quiet, and averages the usable model scores. Wav2Vec2 consumes raw audio. In parallel, librosa calculates 13 MFCCs. These summarize the broad shape of the frequency spectrum on a scale inspired by hearing. Low variation raises a simple heuristic score. Delta-MFCC variation, spectral flatness and zero-crossing rate are extra diagnostics in the JSON response. They do not all enter the fusion formula.
7. consistency_fusion.py compares mouth movement with sound energy. At each frame we divide the average of three vertical inner-lip distances by mouth width. There are eight unique landmarks: three pairs vertically and one pair horizontally. The ratio limits the effect of camera distance. For audio we take the square root of mean squared samples in a 100 ms window. Squaring prevents positive and negative samples cancelling out.
8. Normalize each series, smooth over three frames, exclude low-energy audio and invalid face frames. Shift the two sequences relative to each other from minus six to plus six frames. Pearson correlation measures whether they rise and fall together. Keep the highest usable correlation. Positive lag means audio energy follows the mouth signal. Sync suspicion = clip(1 minus peak correlation, 0.08, 0.92). Three-second local windows provide extra diagnostics. The main sync score uses the whole clip. An energy gate is a rough indicator of activity and can admit music or noise.
9. Combine the three branch scores with the report's veto rule below. app.py runs inference for one upload at a time, returns the results as JSON, and removes temporary files when the request exits. A second simultaneous request gets a busy response. index.html previews the selected file and plots the actual returned values using the browser canvas. All UI assets are local. There is no account, database, permanent upload history or remote inference API.
10. model_registry.py loads the two models on first use, checks which output label means fake, and reuses them for subsequent clips. It tests a small CUDA convolution before choosing GPU. A CPU path is available. START_DEEPSYNC.bat selects an interpreter and launch.py starts FastAPI through Uvicorn. SETUP_WINDOWS.bat installs dependencies and scripts/setup_models.py fetches pinned model versions on a new laptop.
11. Prepared one reference example and two controlled variants. The reversed version keeps the picture sequence and plays audio samples backwards. The muted version removes the audio stream. The tests exercise real file bytes and model inference. tests/test_fusion.py separately checks formula arithmetic, missing evidence, quiet inputs and a known artificial delay. See the measured run table in START_HERE.md.

## Follow one calculation by hand

All branch scores range from 0 to 1. The interface multiplies by 100 for readability.

- Face V = 0.80 × mean ViT fake score + 0.20 × edge anomaly.
- Voice A = 0.75 × mean Wav2Vec2 fake score + 0.25 × MFCC anomaly. MFCC anomaly = clip(1 − mean temporal coefficient variance / 850, 0.08, 0.92).
- If V and A are both below 0.38 and raw C is below 0.80, effective sync E = 0.55 × C. Otherwise E = C. This reduces the contribution of moderate noisy sync evidence.
- Consensus = 0.40 V + 0.35 A + 0.25 E.
- Final = 0.60 × largest of V, A and E + 0.40 × consensus. A complete clip at or above 0.55 gets flagged.
- Worked example (invented inputs for arithmetic): V = 0.90, A = 0.15, C = 0.15. Gate is off. Simple average = 0.40. Consensus = 0.36 + 0.0525 + 0.0375 = 0.45. Final = 0.54 + 0.18 = 0.72. This shows how a strong visual warning survives averaging. It does not establish the face model's accuracy.
- Missing branches: branch cards show Unavailable. The backend may compute a partial index using renormalized weights for diagnostics. The page suppresses the combined number and gives an inconclusive verdict. Face coverage below 60% also forces an inconclusive verdict.

## Questions the panel may ask

**What is a deepfake?** A recording in which a generative model synthesizes or alters someone's appearance or voice. Ordinary dubbing is an edit that can produce a similar timing warning.

**What does multimodal mean?** We use two types of observations, image and sound. Synchrony is a relationship calculated from both. It supplies the third branch.

**Why check the three branches separately?** A voice replacement can leave the face unchanged. A face swap can retain the original voice. A wrong soundtrack may look and sound plausible when examined separately.

**What did you train? Which dataset did you collect?** This build runs pretrained, publicly available weights. No group training dataset or training run was used. The integration, signal calculations, scoring and reproducible experiments are the project work. The original authors' scores belong to their datasets.

**What exactly are the models?** The face checkpoint is dima806/deepfake_vs_real_image_detection. The audio checkpoint is MelodyMachine/Deepfake-audio-detection-V2. Both model folders contain configuration, preprocessing settings and weights. Revision IDs are in model_registry.py.

**Why a transformer when the abstract says CNN?** The early abstract proposed a CNN. In the final design the visual classifier is a ViT operating on patches. The executable and submitted final report agree on that classifier.

**What is inference? What is training?** Training updates weights using examples and feedback. Inference keeps those weights fixed and computes an output for a new input.

**Why both a neural model and a hand-designed feature?** The learned model supplies most of each branch score. A separate measurement supplies an interpretable cue and lets us inspect two sources of evidence. Its benefit still requires evaluation.

**Why 16 kHz and 15 FPS?** The speech model expects 16 kHz mono audio. At 15 FPS we get one mouth measurement about every 66.7 ms. This is a speed-detail tradeoff. Very fast movements can be missed.

**How do you know the face is speaking?** We assume a single visible speaker and compare mouth opening with energy. We do not identify the active speaker reliably in crowds or conversation.

**Is energy equal to speech?** No. A clap or background music can have high RMS. Whispering can have low RMS. This explains why we ask for a clear speech clip.

**Why allow ±400 ms?** Six frames at 15 FPS equals 0.4 s. Searching a small offset tolerates capture latency. It also means that a small deliberate delay may be absorbed. A best lag is an observed alignment, not a diagnosis of hardware latency.

**Why can the green and orange curves differ even for genuine speech?** Some consonants are loud with a nearly closed mouth. Camera angle, noise and different phonemes also affect the measurements. The two curves only approximate a relationship.

**What if a generated face is perfectly lip-synced?** The sync branch may show few indicators. The other branches may still flag it. All three can miss a high-quality fake.

**How are weights and threshold chosen?** They are fixed design choices from the submitted report. We have checked their arithmetic. A future study should tune them on validation data and lock them before testing.

**Is 72/100 the probability the video is fake?** No. It is a combined suspicion index. A calibrated probability would require many independently labeled clips and a separate calibration and evaluation procedure.

**How accurate is the whole system?** A general accuracy percentage has not been established. We can show measured scores, test outcomes and elapsed time for these clips. A three-clip demo cannot estimate population performance.

**What would proper evaluation look like?** Gather genuine, face-manipulated, voice-manipulated and mismatched talking-head clips. Keep identities and near-duplicate clips separate across development and test sets. Report confusion matrix, precision, recall, false-positive rate and the fraction of clips with enough evidence. Compare individual branches, ordinary averaging and veto fusion on the same clips.

**Explain precision and recall.** Precision asks how many flagged clips were actually manipulated. Recall asks how many of the manipulated clips we caught. Missing evidence must be counted separately so abstentions are visible.

**Why did the original clip score high on one branch?** These detectors can respond to appearance, source quality, compression or domain differences. Look at the branch breakdown before interpreting the final number. The Oxford clip has no verified authenticity label here.

**Does the demo actually detect changed audio or read filenames?** The endpoint saves uploaded bytes under a temporary generic name, decodes the tracks and runs inference. Rename a clip and upload it again to test this. No lookup table assigns verdicts to sample files.

**Is the reversed clip an AI voice clone?** It is a controlled audio edit. We know exactly how it was made, so it is useful for a timing experiment. Testing voice-clone accuracy requires labeled synthetic speech.

**What happens to a silent clip, hidden face or corrupt file?** Missing sound prevents voice and synchrony analysis. Missing faces prevent visual scoring. The page reports insufficient evidence. An undecodable upload gets an explanatory error.

**Does “real time” mean live webcam streaming?** This build analyzes an uploaded clip during the session and displays its measured processing time. It has no streaming webcam mode. Model loading makes the first request slower.

**What is the role of FastAPI?** The browser sends multipart video bytes to POST /analyze. Python runs the pipeline and returns JSON. GET / serves the page. The web page renders that response.

**What happens to uploads?** They are decoded inside a temporary directory that is cleaned up after the request. The browser displays the video locally. A process killed abruptly could leave temporary files.

**What is original about this semester project?** The demonstrable contribution is the integration of face, voice and timing evidence with visible measurements and a rule that preserves a strong single-branch warning. Literature novelty needs separate evidence. We use existing model architectures and weights.

**Are all the report's experiments reproduced today?** The written case-study numbers and GPU troubleshooting history are from the report. Our own run evidence is listed in START_HERE.md. The dashboard is intentionally simpler and uses native canvas. The audio activity gate, explicit abstention and mesh-based crop are implementation details of this build.

**Who wrote this and how did you build it?** Accurately describe the existing code that was reused, the coding assistance, the pretrained models and the checks your team personally performed. Each member should be able to open their file, explain its input and output, and demonstrate one failure case.

**What would you improve first?** Evaluate on independent labeled clips, especially compression, dubbing, different languages and unseen generators. Then tune the threshold and compare against the simple-average baseline. Better speech detection and phoneme alignment would address two limitations of the current sync branch.

## Five-minute practice before the viva

1. Everyone predicts which cards remain available for a muted video. Run it and check.
2. Each person explains one transformation from input to output in plain English. Then explain the same thing in Banglish without looking.
3. Have one member calculate the 0.72 worked example and another explain why confidence and accuracy are different.
4. Record eight seconds of one consenting team member speaking naturally with pauses. Upload it. Read whatever the app returns and explain one reason the score could be misleading.
5. Let a different member launch the app from a closed terminal and complete both demo uploads. If asked something untested, say “We have not measured that yet; here is how we would test it.”
