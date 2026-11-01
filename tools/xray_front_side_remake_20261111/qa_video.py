"""Check the rendered reel against its nine approved telop frames."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "xray_front_side_remake_20261111"
REPORT = UNIT / "audio_video_report.json"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
QA_DIR = UNIT / "qa_video"


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    video = Path(report["video"])
    if not video.is_file() or len(report["cuts"]) != 9:
        raise RuntimeError("Finished video or cut plan missing")
    QA_DIR.mkdir(parents=True, exist_ok=True)
    contact = Image.new("RGB", (270 * 3, (480 + 34) * 3), "white")
    draw = ImageDraw.Draw(contact)
    font = ImageFont.truetype(str(FONT), 22)
    records = []
    elapsed = 0.0
    for i, (cut, expected_path) in enumerate(zip(report["cuts"], report["telop_frames"]), 1):
        midpoint = elapsed + cut["cut_seconds"] / 2
        still = QA_DIR / f"video_mid_{i:02d}.png"
        subprocess.run(
            [str(FFMPEG), "-y", "-loglevel", "error", "-ss", f"{midpoint:.3f}",
             "-i", str(video), "-frames:v", "1", str(still)],
            check=True,
        )
        with Image.open(still) as actual_raw, Image.open(expected_path) as expected_raw:
            actual = actual_raw.convert("RGB")
            expected = expected_raw.convert("RGB")
            if actual.size != expected.size or actual.size != (1080, 1920):
                raise RuntimeError(f"Wrong video frame size at cut {i}")
            compare_size = (108, 192)
            actual_small = actual.resize(compare_size, Image.Resampling.LANCZOS)
            expected_small = expected.resize(compare_size, Image.Resampling.LANCZOS)
            difference = ImageChops.difference(actual_small, expected_small)
            mean_difference = sum(ImageStat.Stat(difference).mean) / 3
            if mean_difference > 15:
                raise RuntimeError(f"Cut {i} does not match its telop frame: {mean_difference:.1f}")
            thumb = actual.resize((270, 480), Image.Resampling.LANCZOS)
        x = ((i - 1) % 3) * 270
        y = ((i - 1) // 3) * 514
        contact.paste(thumb, (x, y))
        draw.text((x + 10, y + 484), f"{i:02d}", font=font, fill=(16, 36, 55))
        records.append(
            {
                "cut": i,
                "midpoint_seconds": round(midpoint, 3),
                "video_frame": str(still),
                "expected_telop_frame": expected_path,
                "mean_pixel_difference": round(mean_difference, 3),
            }
        )
        elapsed += cut["cut_seconds"]
        print(f"cut {i:02d}: {mean_difference:.2f} mean pixel difference", flush=True)
    contact.save(QA_DIR / "video_contact_sheet.png")
    (QA_DIR / "qa_report.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
