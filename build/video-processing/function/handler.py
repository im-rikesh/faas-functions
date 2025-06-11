import datetime
import os
import stat
import subprocess
import json

# Define paths
SCRIPT_DIR = "/home/app"
FFMPEG_BINARY = "/usr/bin/ffmpeg"
WATERMARK_IMAGE = os.path.join(SCRIPT_DIR, 'python_logo.png')  # Watermark image
VIDEO_PATH = os.path.join(SCRIPT_DIR, 'driver-action-recognition.mp4')  # Input video

# Ensure required files exist
for path in [FFMPEG_BINARY, WATERMARK_IMAGE, VIDEO_PATH]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}")

# Make FFmpeg executable (if needed)
try:
    st = os.stat(FFMPEG_BINARY)
    os.chmod(FFMPEG_BINARY, st.st_mode | stat.S_IEXEC)
except OSError:
    pass

def call_ffmpeg(args):
    """Runs FFmpeg with given arguments."""
    ret = subprocess.run([FFMPEG_BINARY, '-y'] + args,
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if ret.returncode != 0:
        print('Invocation of FFmpeg failed!')
        print('Out: ', ret.stdout.decode('utf-8'))
        raise RuntimeError()

def apply_watermark(video):
    """Adds a watermark to the video."""
    output = os.path.join(SCRIPT_DIR, f'watermarked-{os.path.basename(video)}')
    call_ffmpeg(["-i", video,
                 "-i", WATERMARK_IMAGE,
                 "-filter_complex", "overlay=main_w/2-overlay_w/2:main_h/2-overlay_h/2",
                 output])
    return output

def extract_gif(video):
    """Extracts a 5-second GIF from the video starting at 3:00 (180s to 185s)."""
    output = os.path.join(SCRIPT_DIR, f'gif-{os.path.basename(video)}.gif')
    call_ffmpeg(["-i", video,
                 "-ss", "180",  # Start at 3:00 (180s)
                 "-t", "5",  # Duration 5 seconds (3:00 to 3:05)
                 "-vf", "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                 "-loop", "0", output])
    return output

def handle(_event=None):
    """Main OpenFaaS function handler."""
    try:
        # Measure Watermark Processing Time
        watermark_start = datetime.datetime.now()
        watermarked_video = apply_watermark(VIDEO_PATH)
        watermark_end = datetime.datetime.now()
        watermark_time = (watermark_end - watermark_start).total_seconds() * 1000  # ms

        # Measure GIF Extraction Time
        gif_start = datetime.datetime.now()
        gif_file = extract_gif(VIDEO_PATH)
        gif_end = datetime.datetime.now()
        gif_time = (gif_end - gif_start).total_seconds() * 1000  # ms

        return {
            "result": {
                "watermarked_video": watermarked_video,
                "gif_file": gif_file
            },
            "measurement": {
                "watermark_time": watermark_time,
                "gif_time": gif_time
            }
        }

    except Exception as e:
        return {"error": str(e)}
