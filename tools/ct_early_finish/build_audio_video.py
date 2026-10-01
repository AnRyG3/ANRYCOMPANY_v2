from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
FRAME_DIR = ROOT / "reel_assets" / "ct_series" / "ct_early_finish_v1_telop_frames"
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_early_finish_v1_video"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_work"
QA_DIR = ASSET_DIR / "qa_midframes"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
VOICEVOX = "http://127.0.0.1:50021"

SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-27dB"
TITLE = "CT検査_もう終わったのと驚かれる理由_20261001"
OUT = ASSET_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

FRAMES = [
    "telop_01_hook.png",
    "telop_02_referral.png",
    "telop_03_reassurance.png",
    "telop_04_ask.png",
    "telop_05_ct_feature.png",
    "telop_06_short_design.png",
    "telop_07_plain_ct.png",
    "telop_08_duration_varies.png",
    "telop_09_not_insufficient.png",
    "telop_10_save.png",
]

# One narration segment is paired with one matching telop frame.
# No silent tail is added between segments.
VOICE_TEXT = [
    "もう終わり。ちゃんと撮れてるのかな。単純CTのあと、そう驚くかたがいます。",
    "他院から紹介されて来たかたなら、わざわざ来たのに、もう終わりと感じることもあります。",
    "不安になるのは、自然なことです。",
    "気になったら、その場で、診療放射線技師に聞いてください。",
    "CTは、短時間で広い範囲を撮影できる装置です。",
    "短時間で撮影できるように、装置が作られています。",
    "造影剤を使わない単純CTは、短時間で終わることがあります。",
    "検査時間は内容や施設で変わります。",
    "早く終わっても、それだけで撮影が不十分とは限りません。",
    "CTが早く終わって不安になったときに、見返せるよう保存しておいてください。",
]


def run(command: list[Path | str], capture: bool = False, check: bool = True) -> subprocess.CompletedProcess[str] | None:
    result = subprocess.run(
        [str(part) for part in command],
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )
    return result if capture else None


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    request = urllib.request.Request(
        f"{VOICEVOX}{path}" + (f"?{query}" if query else ""),
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.95,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.03,
            "postPhonemeLength": 0.03,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def write_concat(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = image.convert("RGB")
    scale = max(width / image.width, height / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left, top = (resized.width - width) // 2, (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def make_contact_sheet(paths: list[Path]) -> None:
    columns, thumb_w, thumb_h, label_h = 3, 216, 384, 36
    sheet = Image.new("RGB", (columns * thumb_w, math.ceil(len(paths) / columns) * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_PATH), 20)
    for index, path in enumerate(paths):
        x, y = (index % columns) * thumb_w, (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=(16, 36, 55))
    sheet.save(QA_DIR / "qa_midframes_contact_sheet.png")


def probe_video(path: Path) -> dict:
    result = run([FFMPEG, "-hide_banner", "-i", path], capture=True, check=False)
    details = (result.stdout or "") + (result.stderr or "")
    duration = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", details)
    resolution = re.search(r"Video:.*?(\d{3,4})x(\d{3,4})", details)
    if duration is None or resolution is None:
        raise RuntimeError(f"Could not inspect video: {path}")
    hours, minutes, seconds = duration.groups()
    return {
        "duration_seconds": round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3),
        "resolution": f"{resolution.group(1)}x{resolution.group(2)}",
        "has_audio_stream": "Audio:" in details,
    }


def main() -> None:
    for directory in [AUDIO_DIR, WORK_DIR, QA_DIR, FINAL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, FONT_PATH, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()

    raw_wavs, durations = [], []
    for index, narration in enumerate(VOICE_TEXT, start=1):
        output = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize(narration, output)
        raw_wavs.append(output)
        durations.append(wav_duration(output))

    segments = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        output = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{duration:.6f}", "-i", frame,
                "-vf", "scale=1080:1920,format=yuv420p", "-r", "30", "-c:v", "libx264", "-tune", "stillimage",
                "-pix_fmt", "yuv420p", output,
            ]
        )
        segments.append(output)

    voice_list, video_list = WORK_DIR / "voice_segments.txt", WORK_DIR / "video_segments.txt"
    write_concat(raw_wavs, voice_list)
    write_concat(segments, video_list)
    voice_all, silent_video = AUDIO_DIR / "voice_all.wav", WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run(
        [
            FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
            "-filter_complex",
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
            "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    qa_paths, elapsed = [], 0.0
    for index, duration in enumerate(durations, start=1):
        midpoint = elapsed + duration / 2
        output = QA_DIR / f"qa_mid_{index:02d}.jpg"
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{midpoint:.6f}", "-i", OUT, "-frames:v", "1", output])
        qa_paths.append(output)
        elapsed += duration
    make_contact_sheet(qa_paths)

    video_info = probe_video(OUT)
    voice_duration = wav_duration(voice_all)
    manifest = {
        "title": TITLE,
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "voice_text": VOICE_TEXT,
        "frames": [str(path.relative_to(ROOT)) for path in frame_paths],
        "raw_voice_durations_seconds": [round(value, 3) for value in durations],
        "asset_video": str(OUT.relative_to(ROOT)),
        "final_video": str(FINAL_OUT.relative_to(ROOT)),
        "qa_contact_sheet": str((QA_DIR / "qa_midframes_contact_sheet.png").relative_to(ROOT)),
        "qa": {
            **video_info,
            "voice_duration_seconds": round(voice_duration, 3),
            "audio_video_duration_difference_seconds": round(abs(video_info["duration_seconds"] - voice_duration), 3),
            "frame_narration_mapping": "one telop frame per matching narration segment",
            "deliberate_silent_pause": "none",
        },
    }
    (ASSET_DIR / "video_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(json.dumps({"video": str(OUT), "final": str(FINAL_OUT), "qa": manifest["qa"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
