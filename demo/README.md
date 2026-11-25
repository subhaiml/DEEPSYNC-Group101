# Demo clip provenance

oxford-short.mp4 is an eight-second excerpt of the Oxford VGG SyncNet example, obtained from the local project sample. Source: https://www.robots.ox.ac.uk/~vgg/software/lipsync/data/example.avi (referenced by https://github.com/joonson/syncnet_python/blob/master/download_model.sh).

reversed-sound.mp4 and muted.mp4 are controlled derivatives made with the commands below. They preserve the video stream. Use the samples for a local demonstration and follow the source's media terms for wider distribution. Bring a consented team recording for questions about real-world performance.

    ffmpeg -i oxford-short.mp4 -af areverse -c:v copy -c:a aac reversed-sound.mp4
    ffmpeg -i oxford-short.mp4 -an -c:v copy muted.mp4

Model sources and attribution: https://huggingface.co/dima806/deepfake_vs_real_image_detection and https://huggingface.co/MelodyMachine/Deepfake-audio-detection-V2 . Their model cards accompany the installed weights. This project uses public pretrained classifiers for inference.
