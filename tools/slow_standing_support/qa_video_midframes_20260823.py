from pathlib import Path
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
MANIFEST = ROOT / "reel_assets" / "slow_standing_support_20260823" / "video_manifest_20260823.json"
OUT_DIR = ROOT / "reel_assets" / "slow_standing_support_20260823" / "_video_work" / "qa_midframes"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = size
    scale = max(w / img.width, h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    video = Path(manifest["asset_video"])
    durations = manifest["durations_seconds"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    shots: list[Path] = []
    cursor = 0.0
    for index, duration in enumerate(durations, start=1):
        midpoint = cursor + duration / 2
        out = OUT_DIR / f"mid_{index:02d}.jpg"
        subprocess.run(
            [
                str(FFMPEG),
                "-y",
                "-loglevel",
                "error",
                "-ss",
                f"{midpoint:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(out),
            ],
            check=True,
        )
        shots.append(out)
        cursor += duration

    cols, rows = 3, 4
    tw, th = 240, 426
    label_h = 34
    sheet = Image.new("RGB", (cols * tw, rows * (th + label_h)), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, path in enumerate(shots):
        thumb = cover(Image.open(path).convert("RGB"), (tw, th))
        x = (index % cols) * tw
        y = (index // cols) * (th + label_h)
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + th + 8), f"{index + 1:02d} {durations[index]:.2f}s", fill=(0, 0, 0), font=font)

    contact = OUT_DIR / "qa_midframes_contact_sheet.jpg"
    sheet.save(contact, quality=92)
    print(contact)


if __name__ == "__main__":
    main()
