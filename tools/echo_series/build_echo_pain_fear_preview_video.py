from pathlib import Path
import subprocess


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "echo_series" / "03_pain_fear"
FRAME_DIR = ASSET_DIR / "final_text_frames"
WORK_DIR = ASSET_DIR / "_video_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "preview_silent.mp4"


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    frames = [FRAME_DIR / f"frame_{i:02d}.png" for i in range(1, 13)]
    missing = [str(path) for path in frames if not path.exists()]
    if missing:
        raise FileNotFoundError("\n".join(missing))

    concat = WORK_DIR / "frames.txt"
    with concat.open("w", encoding="utf-8") as f:
        for idx, frame in enumerate(frames):
            duration = 2.7 if idx < 10 else 3.2
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.2f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

    cmd = [
        str(FFMPEG),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat),
        "-vf",
        "scale=1080:1920,format=yuv420p",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(OUT),
    ]
    subprocess.run(cmd, check=True)
    print(OUT)


if __name__ == "__main__":
    main()
