from __future__ import annotations

import json
import math
import re
import shutil
import struct
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "echo_series" / "09_heart_echo_breakfast_v1_samples"
TELOP_DIR = UNIT / "telop_frames"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "_video_work"
VIDEO_DIR = UNIT / "video"
QA_DIR = UNIT / "qa_midframes"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
FONT = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.2
BETWEEN_CUT_TAIL = 0.03
FINAL_BGM_HOLD = 1.0
MAX_LONG_PUNCTUATION_PAUSE = 0.22
BGM_VOLUME = "-27dB"
OUTPUT = VIDEO_DIR / "心臓エコーの朝_朝ごはんを食べてもいい_20261013.mp4"
FINAL_OUTPUT = FINAL_DIR / OUTPUT.name

DISPLAY_NARRATION = [
    "胸からの心エコーは、朝食を食べてよい場合も。まず案内票を確認。",
    "ただ、同じ日に別の検査があると変わるので、案内票で確認してください。",
    "迷ったら「朝ごはんは食べてきていいですか？」と、予約のときに聞いて大丈夫です。",
    "検査の朝は、食べていいのか、抜くべきなのか、迷いますよね。",
    "心臓エコーは、胸に機械をあてて、心臓の動きや形を見る検査です。",
    "この検査自体は、食事の制限を設けていない病院があります。",
    "同じ日に腹部エコーなど、食事制限のある検査を受けるなら、指示が変わります。",
    "口から行う経食道心エコーは別の検査で、事前に食事制限があります。",
    "病院によって違うので、手元の案内票を、ぜひ確認してください。",
    "案内票で確認するのは、心エコーの種類と、同じ日に受ける検査です。",
    "検査前日の夜に見返せるよう、保存しておいてください。",
]

# Voice-only text uses kana where VOICEVOX readings can be ambiguous.
VOICE_TEXT = [
    "胸からの心臓エコーは、朝食を食べてよい場合もあります。まず、あんないひょうを確認してください。",
    "ただ、同じ日に別の検査があると変わるので、あんないひょうで確認してください。",
    "迷ったら、朝ごはんは食べてきていいですか、と、予約のときに聞いて大丈夫です。",
    "検査の朝は、食べていいのか、抜くべきなのか、迷いますよね。",
    "心臓エコーは、胸に機械をあてて、心臓の動きや形を見る検査です。",
    "この検査自体は、食事の制限を設けていない病院があります。",
    "同じ日に、ふくぶエコーなど、食事制限のある検査を受けるなら、指示が変わります。",
    "口から行う、けいしょくどう心臓エコーは別の検査で、事前に食事制限があります。",
    "病院によって違うので、手元のあんないひょうを、ぜひ確認してください。",
    "あんないひょうで確認するのは、心臓エコーの種類と、同じ日に受ける検査です。",
    "検査前日の夜に見返せるよう、保存しておいてください。",
]


def run(command: list[object], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(part) for part in command],
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )


def post(path: str, params: dict[str, object], payload: dict[str, object] | None = None) -> bytes:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{VOICEVOX}{path}?{query}",
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post("/audio_query", {"text": text, "speaker": SPEAKER}))
    for phrase in query.get("accent_phrases", []):
        pause_mora = phrase.get("pause_mora")
        if pause_mora and pause_mora.get("vowel_length", 0) > MAX_LONG_PUNCTUATION_PAUSE:
            pause_mora["vowel_length"] = MAX_LONG_PUNCTUATION_PAUSE
    query.update(
        {
            "speedScale": SPEED,
            "pitchScale": 0,
            "intonationScale": 0.95,
            "prePhonemeLength": 0,
            "postPhonemeLength": 0,
        }
    )
    output.write_bytes(post("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image_file:
        header = image_file.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"PNGとして読めません: {path}")
    return struct.unpack(">II", header[16:24])


def write_concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def approved_source_images() -> list[Path]:
    text = (UNIT / "production_manifest.md").read_text(encoding="utf-8-sig")
    paths = [Path(item) for item in re.findall(r"`([A-Za-z]:\\[^`]+\.png)`", text)[:11]]
    if len(paths) != len(VOICE_TEXT):
        raise RuntimeError("production_manifest.md の承認画像が11枚ではありません。")
    if any(not path.exists() for path in paths):
        raise RuntimeError("production_manifest.md の承認画像に存在しないファイルがあります。")
    return paths


def locked_telop_frames(source_images: list[Path]) -> list[Path]:
    entries = json.loads((TELOP_DIR / "telop_manifest.json").read_text(encoding="utf-8-sig"))
    if [entry["index"] for entry in entries] != list(range(1, len(VOICE_TEXT) + 1)):
        raise RuntimeError("telop_manifest.json のカット順が1〜11ではありません。")
    telop_sources = [(ROOT / Path(entry["source"])).resolve() for entry in entries]
    if telop_sources != [path.resolve() for path in source_images]:
        raise RuntimeError("承認画像とテロップの対応がproduction_manifestと一致しません。")
    frames = [(ROOT / Path(entry["output"])).resolve() for entry in entries]
    listed_frames = sorted(TELOP_DIR.glob("telop_[0-9][0-9].png"))
    if [path.resolve() for path in listed_frames] != frames:
        raise RuntimeError("テロップフォルダの画像一覧とtelop_manifestが一致しません。")
    for frame in frames:
        if not frame.exists() or png_size(frame) != (1080, 1920):
            raise RuntimeError(f"テロップ画像が存在しないか1080x1920ではありません: {frame}")
    return frames


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = max(width / image.width, height / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def make_qa_contact_sheet(paths: list[Path], output: Path) -> None:
    cols, thumb_w, thumb_h, label_h = 4, 270, 480, 40
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT), 22)
    for index, path in enumerate(paths):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        image = cover(Image.open(path).convert("RGB"), (thumb_w, thumb_h))
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 8, y + thumb_h + 7), f"{index + 1:02d}", font=label_font, fill=(12, 34, 58))
    sheet.save(output, quality=92)


def main() -> None:
    for required in (FFMPEG, BGM, FONT):
        if not required.exists():
            raise FileNotFoundError(required)

    source_images = approved_source_images()
    frames = locked_telop_frames(source_images)
    for directory in (AUDIO_DIR, WORK_DIR, VIDEO_DIR, QA_DIR, FINAL_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    raw_wavs: list[Path] = []
    padded_wavs: list[Path] = []
    video_segments: list[Path] = []
    voice_durations: list[float] = []
    cut_durations: list[float] = []
    timeline: list[dict[str, object]] = []
    cursor = 0.0

    for cut, (display_text, voice_text, source_image, frame) in enumerate(
        zip(DISPLAY_NARRATION, VOICE_TEXT, source_images, frames), start=1
    ):
        raw_wav = AUDIO_DIR / f"voice_{cut:02d}.wav"
        synthesize(voice_text, raw_wav)
        voice_duration = wav_duration(raw_wav)
        hold = FINAL_BGM_HOLD if cut == len(VOICE_TEXT) else BETWEEN_CUT_TAIL
        cut_duration = voice_duration + hold

        padded_wav = WORK_DIR / f"voice_{cut:02d}_timeline.wav"
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
                "-i",
                raw_wav,
                "-af",
                f"apad=pad_dur={cut_duration:.6f},atrim=duration={cut_duration:.6f}",
                "-ar",
                "44100",
                "-ac",
                "2",
                padded_wav,
            ]
        )

        segment = WORK_DIR / f"segment_{cut:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
                "-loop",
                "1",
                "-t",
                f"{cut_duration:.6f}",
                "-i",
                frame,
                "-vf",
                "scale=1080:1920,format=yuv420p",
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-tune",
                "stillimage",
                "-pix_fmt",
                "yuv420p",
                segment,
            ]
        )

        raw_wavs.append(raw_wav)
        padded_wavs.append(padded_wav)
        video_segments.append(segment)
        voice_durations.append(voice_duration)
        cut_durations.append(cut_duration)
        timeline.append(
            {
                "cut": cut,
                "start": round(cursor, 3),
                "voice_end": round(cursor + voice_duration, 3),
                "cut_end": round(cursor + cut_duration, 3),
                "display_narration": display_text,
                "voice_text": voice_text,
                "source_image": str(source_image),
                "telop_frame": str(frame),
                "voice_file": str(raw_wav),
            }
        )
        cursor += cut_duration

    voice_list = WORK_DIR / "voice_concat.txt"
    video_list = WORK_DIR / "video_concat.txt"
    write_concat_list(padded_wavs, voice_list)
    write_concat_list(video_segments, video_list)
    voice_all = AUDIO_DIR / "voice_all.wav"
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    run(
        [
            FFMPEG,
            "-y",
            "-loglevel",
            "error",
            "-i",
            silent_video,
            "-i",
            voice_all,
            "-stream_loop",
            "-1",
            "-i",
            BGM,
            "-filter_complex",
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95[audio]",
            "-map",
            "0:v",
            "-map",
            "[audio]",
            "-shortest",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            OUTPUT,
        ]
    )
    shutil.copy2(OUTPUT, FINAL_OUTPUT)

    qa_paths: list[Path] = []
    for item in timeline:
        midpoint = (float(item["start"]) + float(item["voice_end"])) / 2
        qa_path = QA_DIR / f"qa_mid_{int(item['cut']):02d}.jpg"
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
                "-ss",
                f"{midpoint:.3f}",
                "-i",
                OUTPUT,
                "-frames:v",
                "1",
                qa_path,
            ]
        )
        qa_paths.append(qa_path)
    qa_contact = QA_DIR / "qa_midframes_contact_sheet.jpg"
    make_qa_contact_sheet(qa_paths, qa_contact)

    silence_check = run(
        [
            FFMPEG,
            "-hide_banner",
            "-i",
            voice_all,
            "-af",
            "silencedetect=noise=-48dB:d=0.45",
            "-f",
            "null",
            "-",
        ],
        capture=True,
    )
    detected_silence = [
        line.strip()
        for line in silence_check.stderr.splitlines()
        if "silence_start" in line or "silence_end" in line
    ]

    audio_manifest = {
        "voice_engine": "VOICEVOX",
        "speaker": "もち子さん(cv 明日葉よもぎ)",
        "speaker_id": SPEAKER,
        "voice_speed": SPEED,
        "pre_phoneme_length": 0,
        "post_phoneme_length": 0,
        "max_long_punctuation_pause": MAX_LONG_PUNCTUATION_PAUSE,
        "between_cut_tail_seconds": BETWEEN_CUT_TAIL,
        "final_bgm_hold_seconds": FINAL_BGM_HOLD,
        "voice_text": VOICE_TEXT,
        "voice_files": [str(path) for path in raw_wavs],
        "voice_durations": [round(value, 3) for value in voice_durations],
        "detected_silence_over_0_45_seconds": detected_silence,
    }
    (AUDIO_DIR / "audio_manifest.json").write_text(
        json.dumps(audio_manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )

    video_manifest = {
        "title": "心臓エコーの朝、ごはんを食べてもいい？",
        "video": str(OUTPUT),
        "final_video": str(FINAL_OUTPUT),
        "resolution": "1080x1920",
        "fps": 30,
        "expected_duration_seconds": round(sum(cut_durations), 3),
        "pacing": "カット間0.03秒。最終カットのみ音声後にBGMだけ1.0秒。",
        "source_images": [str(path) for path in source_images],
        "telop_frames": [str(path) for path in frames],
        "timeline": timeline,
        "qa_contact_sheet": str(qa_contact),
    }
    (VIDEO_DIR / "video_manifest.json").write_text(
        json.dumps(video_manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig"
    )
    print(json.dumps(video_manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
