from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "mri_series" / "mri_kairo_20261109"
VIDEO_DIR = UNIT / "video"
VIDEO = VIDEO_DIR / "MRI_貼るカイロ_20261109_review.mp4"
MANIFEST = VIDEO_DIR / "video_manifest.json"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
QA_DIR = VIDEO_DIR / "qa"


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cuts = data["cut_timing"]
    if len(cuts) != 10 or data["voicevox_speedScale"] != 1.15 or data["video_playback_speed"] != 1.0:
        raise RuntimeError("Cut count or speed metadata mismatch")
    QA_DIR.mkdir(parents=True, exist_ok=True)

    decode = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-loglevel", "error", "-i", str(VIDEO), "-f", "null", "NUL"],
        capture_output=True,
    )
    if decode.returncode:
        raise RuntimeError(decode.stderr.decode("utf-8", errors="replace"))

    sheet = Image.new("RGB", (1080, 850), (245, 246, 248))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT), 22)
    frames = []
    for index, cut in enumerate(cuts):
        midpoint = (cut["start_seconds"] + cut["end_seconds"]) / 2
        frame_path = QA_DIR / f"video_cut_{index + 1:02d}.png"
        result = subprocess.run(
            [str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{midpoint:.3f}", "-i", str(VIDEO), "-frames:v", "1", str(frame_path)],
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
        with Image.open(frame_path) as raw:
            if raw.size != (1080, 1920):
                raise RuntimeError(f"Unexpected video frame size: {raw.size}")
            thumb = raw.resize((216, 384), Image.Resampling.LANCZOS)
        x = (index % 5) * 216
        y = (index // 5) * 425
        sheet.paste(thumb, (x, y))
        draw.text((x + 9, y + 387), f"{index + 1:02d}  {midpoint:.1f}s", fill=(12, 34, 64), font=label_font)
        frames.append({"cut": index + 1, "time_seconds": round(midpoint, 3), "screenshot": str(frame_path)})

    sheet_path = QA_DIR / "video_contact_sheet.png"
    sheet.save(sheet_path)
    (QA_DIR / "qa_report.json").write_text(
        json.dumps({"decode_ok": True, "sampled_cuts": frames, "contact_sheet": str(sheet_path)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Video decoded and {len(frames)} cut midpoints sampled: {sheet_path}")


if __name__ == "__main__":
    main()
