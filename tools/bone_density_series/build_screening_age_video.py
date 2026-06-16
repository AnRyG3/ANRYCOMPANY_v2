from pathlib import Path
import json
import shutil
import subprocess


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "bone_density_series" / "07_bone_density_screening_age"
FRAME_DIR = ASSET_DIR / "final_text_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"

OUT = ASSET_DIR / "骨密度検査_何歳から受ければいい.mp4"
FINAL_OUT = FINAL_DIR / "骨密度検査_何歳から受ければいい.mp4"
SIZE = "1080:1920"


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def find_bgm():
    for name in ("healing_wind.mp3", "Kind_Heart.mp3"):
        candidates = list(ROOT.rglob(name))
        if candidates:
            return candidates[0]
    return None


def load_manifest():
    path = ASSET_DIR / "audio_manifest.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def build_silent_video(frames, durations, out):
    frames_txt = WORK_DIR / "frames.txt"
    with frames_txt.open("w", encoding="utf-8") as f:
        for frame, duration in zip(frames, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

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
        f"scale={SIZE},format=yuv420p",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        out,
    ])


def mux_audio(silent, voice, bgm):
    if bgm:
        run([
            FFMPEG,
            "-y",
            "-i",
            silent,
            "-i",
            voice,
            "-stream_loop",
            "-1",
            "-i",
            bgm,
            "-filter_complex",
            "[1:a]volume=1.35[voice];[2:a]volume=-26dB[bgm];"
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
    else:
        run([
            FFMPEG,
            "-y",
            "-i",
            silent,
            "-i",
            voice,
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
            OUT,
        ])


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    if not FFMPEG.exists():
        raise FileNotFoundError(FFMPEG)

    manifest = load_manifest()
    durations = [float(value) for value in manifest["durations_seconds"]]
    frames = [FRAME_DIR / f"frame_{idx:02d}.png" for idx in range(1, 13)]
    voice = AUDIO_DIR / "voice.wav"
    required = [*frames, voice]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)

    silent = WORK_DIR / "silent.mp4"
    bgm = find_bgm()
    build_silent_video(frames, durations, silent)
    mux_audio(silent, voice, bgm)
    shutil.copy2(OUT, FINAL_OUT)

    video_manifest = {
        "title": "骨密度検査、何歳から受ければいい？",
        "asset_dir": str(ASSET_DIR),
        "frames": [str(path) for path in frames],
        "voice": str(voice),
        "bgm": None if bgm is None else str(bgm),
        "voice_speed": manifest.get("voice_speed", "1.20x"),
        "durations_seconds": durations,
        "total_seconds": round(sum(durations), 3),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "note": "画像12枚と作成済みVOICEVOX音声を同期。BGMは小さくミックス。",
    }
    (ASSET_DIR / "video_manifest.json").write_text(
        json.dumps(video_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
