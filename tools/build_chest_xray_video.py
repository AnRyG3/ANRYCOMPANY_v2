from pathlib import Path
import subprocess
import wave

ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "chest_xray_series" / "01_what_it_shows"
FRAME_DIR = ASSET_DIR / "text_frames_v1"
AUDIO_DIR = ASSET_DIR / "audio_v1"
WORK_DIR = ASSET_DIR / "_video_work_v1"
OUT_DIR = ASSET_DIR / "video_v1"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def wav_duration(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    clips = []
    for idx in range(1, 13):
        frame = FRAME_DIR / f"{idx:02d}.png"
        voice = WORK_DIR.parent / "_audio_work_v1" / f"voice_{idx:02d}_padded.wav"
        duration = wav_duration(voice)
        clip = WORK_DIR / f"clip_{idx:02d}.mp4"
        run([
            FFMPEG, "-y",
            "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-r", "30", "-an", "-c:v", "libx264", "-preset", "veryfast", clip,
        ])
        clips.append(clip)

    concat_file = WORK_DIR / "clips.txt"
    concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", silent_video])

    out = OUT_DIR / "chest_xray_what_it_shows_v1.mp4"
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", AUDIO_DIR / "voice_bgm_mix.wav",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", out,
    ])
    print(out)


if __name__ == "__main__":
    main()
