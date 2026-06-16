from pathlib import Path
import json
import shutil
import subprocess
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "06_yam70_meaning"
FRAME_DIR = ASSET_DIR / "final_text_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work_from_existing_audio"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "骨密度の結果_YAM70って何.mp4"
FINAL_OUT = FINAL_DIR / "骨密度の結果_YAM70って何.mp4"

MIN_DURATIONS = [3.1, 4.1, 2.8, 4.6, 6.0, 3.6, 5.8, 4.6, 4.8, 3.2, 3.5, 3.8]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def find_bgm():
    for name in ("Kind_Heart.mp3", "healing_wind.mp3"):
        candidates = list(ROOT.rglob(name))
        if candidates:
            return candidates[0]
    raise FileNotFoundError("BGM mp3 not found")


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    frames = [FRAME_DIR / f"frame_{idx:02d}.png" for idx in range(1, 13)]
    voices = [AUDIO_DIR / f"voice_{idx:02d}.wav" for idx in range(1, 13)]
    combined_voice = AUDIO_DIR / "voice.wav"
    bgm = find_bgm()

    for required in [FFMPEG, bgm, *frames, *voices, combined_voice]:
        if not required.exists():
            raise FileNotFoundError(required)

    durations = []
    for idx, voice in enumerate(voices, start=1):
        durations.append(max(MIN_DURATIONS[idx - 1], wav_duration(voice) + 0.42))

    frames_txt = WORK_DIR / "frames.txt"
    with frames_txt.open("w", encoding="utf-8") as f:
        for frame, duration in zip(frames, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

    silent = WORK_DIR / "silent.mp4"
    run([
        FFMPEG,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        frames_txt,
        "-vf",
        "scale=1080:1920,format=yuv420p",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        silent,
    ])
    run([
        FFMPEG,
        "-y",
        "-i",
        silent,
        "-i",
        combined_voice,
        "-stream_loop",
        "-1",
        "-i",
        bgm,
        "-filter_complex",
        "[1:a]volume=1.45[voice];[2:a]volume=-26dB[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,"
        "alimiter=limit=0.95[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-shortest",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        OUT,
    ])
    shutil.copy2(OUT, FINAL_OUT)

    manifest = {
        "title": "骨密度の結果、YAM70%って何？",
        "audio_source": str(combined_voice),
        "bgm": str(bgm),
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "frames": [str(path) for path in frames],
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
