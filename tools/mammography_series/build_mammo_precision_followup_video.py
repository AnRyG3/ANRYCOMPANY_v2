from pathlib import Path
import json
import shutil
import subprocess


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "mammo_result_notice_v1"
FRAME_DIR = ASSET_DIR / "final_text_frames_precision_followup_20260623"
AUDIO_DIR = ASSET_DIR / "audio_precision_followup_20260623"
WORK_DIR = ASSET_DIR / "_video_work_precision_followup_20260623"
MANIFEST = ASSET_DIR / "video_manifest_precision_followup_20260623.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "マンモで要精密検査_次に何をする_20260623.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "マンモで要精密検査_次に何をする_20260623.mp4"
)


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    audio_manifest = json.loads((ASSET_DIR / "audio_manifest_precision_followup_20260623.json").read_text(encoding="utf-8"))
    durations = audio_manifest["durations_seconds"]
    frames = [FRAME_DIR / f"frame_{idx:02d}.png" for idx in range(1, 11)]
    audio = AUDIO_DIR / "voice_with_bgm.m4a"

    for required in [FFMPEG, audio, *frames]:
        if not required.exists():
            raise FileNotFoundError(required)

    frames_txt = WORK_DIR / "frames.txt"
    with frames_txt.open("w", encoding="utf-8") as f:
        for frame, duration in zip(frames, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

    silent = WORK_DIR / "silent.mp4"
    run(
        [
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
        ]
    )
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            silent,
            "-i",
            audio,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-shortest",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    manifest = {
        "title": "マンモで要精密検査、次に何をする？",
        "frames": [str(path) for path in frames],
        "audio": str(audio),
        "durations_seconds": durations,
        "total_seconds": audio_manifest["total_seconds"],
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "voice_speed": audio_manifest["voice_speed"],
        "reading_note": "方 is read as かた in the narration source.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
