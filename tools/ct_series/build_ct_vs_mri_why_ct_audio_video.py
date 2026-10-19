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
UNIT = ROOT / "reel_assets" / "ct_series" / "ct_vs_mri_why_ct_v1_samples"
PRODUCTION_MANIFEST = UNIT / "production_manifest.md"
TELOP_MANIFEST = UNIT / "telop_frames" / "telop_manifest.json"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "video_work"
QA_DIR = UNIT / "video_qa"
ASSET_OUT = UNIT / "ct_vs_mri_why_ct_v1.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "医師がCTって言った。MRIじゃなくて大丈夫？.mp4"
)
VIDEO_MANIFEST = UNIT / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
FONT_PATH = ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"
FINAL_BGM_TAIL = 1.0


# Each approved visual cut maps to exactly one narration segment. Kana is used
# only where it makes the voice engine's reading unambiguous.
NARRATION = [
    "医師に、シーティーと言われて、エムアールアイじゃなくて大丈夫、と思っても、おかしくありません。",
    "シーティーとエムアールアイは、調べる目的に応じて、使い分ける検査です。",
    "理由が気になったら、医師に聞いて大丈夫です。",
    "エムアールアイのほうが詳しそうなイメージがあるので、不安になりますよね。",
    "シーティーとエムアールアイは、体の中を見る方法が違う検査です。",
    "どちらが上ということではなく、見たいものによって、得意なことが変わります。",
    "検査内容は、医師が決めます。",
    "施設によって、検査の進め方や、案内が違う場合もあります。",
    "聞いたら失礼かな、と思わなくて大丈夫です。",
    "診察室では、今回、シーティーを受ける理由を教えていただけますか、と聞いてみてください。",
    "次に検査を言われたときに見返せるよう、保存しておいてください。",
]


def run(command: list[Path | str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(item) for item in command],
        check=True,
        capture_output=capture,
        text=capture,
        encoding="utf-8",
        errors="replace",
    )


def post_json(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize_voice(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update({
        "speedScale": VOICE_SPEED,
        "pitchScale": 0.0,
        "intonationScale": 0.96,
        "pauseLengthScale": 0.32,
        "prePhonemeLength": 0.02,
        "postPhonemeLength": 0.04,
        "volumeScale": 1.0,
    })
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def load_locked_frames() -> tuple[list[Path], list[dict]]:
    if not PRODUCTION_MANIFEST.exists() or not TELOP_MANIFEST.exists():
        raise FileNotFoundError("production_manifest.md or telop_manifest.json is missing")
    production_text = PRODUCTION_MANIFEST.read_text(encoding="utf-8-sig")
    telop_data = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    if len(telop_data) != len(NARRATION) or [item["cut"] for item in telop_data] != list(range(1, 12)):
        raise ValueError("Telop count or cut order does not match the approved 11-cut structure")

    frames = []
    for item in telop_data:
        source = Path(item["source"])
        frame = Path(item["output"])
        if str(source) not in production_text:
            raise ValueError(f"Telop source is not locked in production_manifest.md: {source}")
        if not source.exists() or not frame.exists():
            raise FileNotFoundError(source if not source.exists() else frame)
        frames.append(frame)
    return frames, telop_data


def detect_long_silences(audio: Path) -> list[dict]:
    completed = run([
        FFMPEG,
        "-hide_banner",
        "-i",
        audio,
        "-af",
        "silencedetect=noise=-42dB:d=0.35",
        "-f",
        "null",
        "-",
    ], capture=True)
    log = completed.stderr
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", log)]
    endings = [
        (float(end), float(duration))
        for end, duration in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", log)
    ]
    return [
        {"start": round(start, 3), "end": round(end, 3), "duration": round(duration, 3)}
        for start, (end, duration) in zip(starts, endings)
    ]


def probe_duration(media: Path) -> float:
    completed = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-i", str(media)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    match = re.search(r"Duration: (\d+):(\d+):([0-9.]+)", completed.stderr)
    if not match:
        raise ValueError(f"Could not read duration: {media}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - size[0]) // 2
    y = (resized.height - size[1]) // 2
    return resized.crop((x, y, x + size[0], y + size[1]))


def make_video_sample_sheet(video: Path, durations: list[float]) -> Path:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    elapsed = 0.0
    samples = []
    for index, duration in enumerate(durations, start=1):
        timestamp = elapsed + duration / 2
        sample = QA_DIR / f"sample_{index:02d}.png"
        run([
            FFMPEG,
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            video,
            "-frames:v",
            "1",
            sample,
        ])
        samples.append(sample)
        elapsed += duration

    thumb_w, thumb_h, label_h, columns = 270, 480, 40, 3
    rows = math.ceil(len(samples) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_PATH), 22)
    for index, sample in enumerate(samples):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        sheet.paste(cover(Image.open(sample), (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 10, y + thumb_h + 6), f"CUT {index + 1:02d}", font=label_font, fill=(16, 36, 55))
    output = QA_DIR / "contact_sheet_video_samples.png"
    sheet.save(output)
    return output


def main() -> None:
    for required in (FFMPEG, BGM, FONT_PATH):
        if not required.exists():
            raise FileNotFoundError(required)
    frames, telop_data = load_locked_frames()

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    voice_paths, durations = [], []
    for index, text in enumerate(NARRATION, start=1):
        voice_path = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(text, voice_path)
        voice_paths.append(voice_path)
        durations.append(wav_duration(voice_path))

    voice_list = WORK_DIR / "voice_segments.txt"
    concat_list(voice_paths, voice_list)
    voice_all = AUDIO_DIR / "narration.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_durations = durations.copy()
    video_durations[-1] += FINAL_BGM_TAIL
    video_segments = []
    for index, (frame, duration) in enumerate(zip(frames, video_durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run([
            FFMPEG,
            "-y",
            "-loop",
            "1",
            "-t",
            f"{duration:.3f}",
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
        ])
        video_segments.append(segment)

    video_list = WORK_DIR / "video_segments.txt"
    concat_list(video_segments, video_list)
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    total_duration = sum(video_durations)
    fade_start = max(0.0, total_duration - 0.8)
    audio_filter = (
        f"[1:a]apad=pad_dur={FINAL_BGM_TAIL:.3f},atrim=duration={total_duration:.3f},volume=1.4[voice];"
        f"[2:a]volume={BGM_VOLUME},afade=t=out:st={fade_start:.3f}:d=0.8[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]"
    )
    run([
        FFMPEG,
        "-y",
        "-i",
        silent_video,
        "-i",
        voice_all,
        "-stream_loop",
        "-1",
        "-i",
        BGM,
        "-filter_complex",
        audio_filter,
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-t",
        f"{total_duration:.3f}",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        ASSET_OUT,
    ])
    shutil.copy2(ASSET_OUT, FINAL_OUT)

    long_silences = detect_long_silences(voice_all)
    measured_video_duration = probe_duration(ASSET_OUT)
    sample_sheet = make_video_sample_sheet(ASSET_OUT, video_durations)
    if abs(measured_video_duration - total_duration) > 0.12:
        raise ValueError(
            f"Video duration mismatch: expected {total_duration:.3f}, measured {measured_video_duration:.3f}"
        )

    mapping = []
    for index, (frame, text, duration, telop) in enumerate(
        zip(frames, NARRATION, durations, telop_data), start=1
    ):
        mapping.append({
            "cut": index,
            "source_image": telop["source"],
            "telop_frame": str(frame),
            "telop_text": telop["text"],
            "voice_text": text,
            "voice_file": str(voice_paths[index - 1]),
            "voice_duration_seconds": round(duration, 3),
            "alignment_checked": True,
        })

    VIDEO_MANIFEST.write_text(json.dumps({
        "title": "医師がCTって言った。MRIじゃなくて大丈夫？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "pause_length_scale": 0.32,
        "artificial_transition_silence_seconds": 0.0,
        "final_bgm_only_tail_seconds": FINAL_BGM_TAIL,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "cut_mapping": mapping,
        "narration_duration_seconds": round(sum(durations), 3),
        "target_video_duration_seconds": round(total_duration, 3),
        "measured_video_duration_seconds": round(measured_video_duration, 3),
        "silence_detection_threshold": "-42 dB for 0.35 seconds",
        "detected_long_silences": long_silences,
        "voice_audio": str(voice_all),
        "asset_video": str(ASSET_OUT),
        "final_video": str(FINAL_OUT),
        "video_sample_sheet": str(sample_sheet),
    }, ensure_ascii=False, indent=2), encoding="utf-8-sig")

    print(voice_all)
    print(ASSET_OUT)
    print(FINAL_OUT)
    print(f"narration_seconds={sum(durations):.3f}")
    print(f"video_seconds={measured_video_duration:.3f}")
    print(f"long_silences={len(long_silences)}")
    print(sample_sheet)


if __name__ == "__main__":
    main()
