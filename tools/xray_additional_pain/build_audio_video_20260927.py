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
FRAME_DIR = ROOT / "reel_assets" / "xray_additional_pain_20260927_telop_frames"
ASSET_DIR = ROOT / "reel_assets" / "xray_additional_pain_20260927_video"
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
TAIL_SECONDS = 0.02
BGM_VOLUME = "-27dB"
TITLE = "レントゲン_ついでに別の痛い場所も撮ってもらえる_20260927"
OUT = ASSET_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / OUT.name
MANIFEST = ASSET_DIR / "video_manifest.json"
QA_CONTACT = QA_DIR / "qa_midframes_contact_sheet.jpg"

FRAMES = [
    "telop_01_hook_another_pain.png",
    "telop_02_consult_doctor_next.png",
    "telop_03_natural_question.png",
    "telop_04_ordered_area_confirmed.png",
    "telop_05_technologist_checks_order.png",
    "telop_06_doctor_considers_need.png",
    "telop_07_process_reassurance.png",
    "telop_08_tell_doctor_symptoms.png",
    "telop_09_save_before_consultation.png",
    "telop_10_follow_cta_technologist.png",
]

# Display and narration remain one-to-one. VOICE_TEXT uses natural spoken
# punctuation and kana only where needed for a stable reading.
DISPLAY_NARRATION = [
    "ここも痛い。ついでに撮ってもらえるかな。",
    "別の痛い場所は、診察で医師に伝えてください。",
    "ついでにと思う気持ちは、自然なことです。",
    "レントゲンは、医師から指示された部位を撮影します。",
    "撮影する部位は、事前の指示で決まっています。",
    "追加の撮影が必要かどうかは、医師が判断します。",
    "少し手間に感じても、必要性を確認する大切な手順です。",
    "診察では、ここも痛いと伝えてください。",
    "診察前に見返せるよう、この投稿を保存しておいてください。",
    "役に立ったら、フォローもお願いします。",
]
VOICE_TEXT = DISPLAY_NARRATION[:]


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
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
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
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def make_contact_sheet(paths: list[Path]) -> None:
    columns, thumb_w, thumb_h, label_h = 4, 216, 384, 36
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT_PATH), 20)
    for index, path in enumerate(paths):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(path), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=font, fill=(16, 36, 55))
    sheet.save(QA_CONTACT, quality=94)


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

    padded_wavs: list[Path] = []
    raw_durations: list[float] = []
    cut_durations: list[float] = []
    for index, narration in enumerate(VOICE_TEXT, start=1):
        raw = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize(narration, raw)
        raw_duration = wav_duration(raw)
        cut_duration = raw_duration + TAIL_SECONDS
        run(
            [
                FFMPEG, "-y", "-loglevel", "error", "-i", raw,
                "-af", f"apad=pad_dur={TAIL_SECONDS:.3f},atrim=duration={cut_duration:.3f}",
                "-ar", "44100", "-ac", "2", padded,
            ]
        )
        raw_durations.append(raw_duration)
        cut_durations.append(cut_duration)
        padded_wavs.append(padded)

    segment_paths: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, cut_durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
                "-vf", "scale=1080:1920,format=yuv420p", "-r", "30",
                "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", segment,
            ]
        )
        segment_paths.append(segment)

    voice_list = WORK_DIR / "voice_segments.txt"
    video_list = WORK_DIR / "video_segments.txt"
    write_concat(padded_wavs, voice_list)
    write_concat(segment_paths, video_list)
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
    run(
        [
            FFMPEG, "-y", "-loglevel", "error", "-i", silent_video, "-i", voice_all,
            "-stream_loop", "-1", "-i", BGM,
            "-filter_complex",
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[a]",
            "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    qa_paths: list[Path] = []
    elapsed = 0.0
    for index, duration in enumerate(cut_durations, start=1):
        midpoint = elapsed + duration / 2
        qa_frame = QA_DIR / f"qa_mid_{index:02d}.jpg"
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{midpoint:.3f}", "-i", OUT, "-frames:v", "1", qa_frame])
        qa_paths.append(qa_frame)
        elapsed += duration
    make_contact_sheet(qa_paths)

    video_info = probe_video(OUT)
    voice_duration = wav_duration(voice_all)
    manifest = {
        "title": TITLE,
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "tail_seconds_per_cut": TAIL_SECONDS,
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "frames": [str(path.relative_to(ROOT)) for path in frame_paths],
        "raw_voice_durations_seconds": [round(value, 3) for value in raw_durations],
        "cut_durations_seconds": [round(value, 3) for value in cut_durations],
        "voice_audio": str(voice_all.relative_to(ROOT)),
        "asset_video": str(OUT.relative_to(ROOT)),
        "final_video": str(FINAL_OUT.relative_to(ROOT)),
        "qa_contact_sheet": str(QA_CONTACT.relative_to(ROOT)),
        "qa": {
            **video_info,
            "voice_duration_seconds": round(voice_duration, 3),
            "audio_video_duration_difference_seconds": round(abs(video_info["duration_seconds"] - voice_duration), 3),
            "frame_narration_mapping": "one telop frame per matching narration segment",
            "long_silent_pause": "none; each frame adds only 0.02 seconds after the matching voice segment",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(json.dumps({"video": str(OUT), "final": str(FINAL_OUT), "qa": manifest["qa"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
