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
PRODUCTION_MANIFEST = (
    ROOT / "reel_assets" / "xray_family_contact_20261012_samples" / "production_manifest.md"
)
TELOP_DIR = ROOT / "reel_assets" / "xray_family_contact_20261012_telop_frames"
TELOP_MANIFEST = TELOP_DIR / "telop_manifest.json"
AUDIO_DIR = ROOT / "reel_assets" / "xray_family_contact_20261012_audio"
WORK_DIR = ROOT / "reel_assets" / "xray_family_contact_20261012_video_work"
VIDEO_DIR = ROOT / "reel_assets" / "xray_family_contact_20261012_video"
QA_DIR = ROOT / "reel_assets" / "xray_family_contact_20261012_video_qa"
ASSET_OUT = VIDEO_DIR / "xray_family_contact_v1.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "レントゲンを撮ったあと_家族に会っていい.mp4"
)
VIDEO_MANIFEST = VIDEO_DIR / "video_manifest.json"

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
PAUSE_LENGTH_SCALE = 0.32
PRE_PHONEME_LENGTH = 0.02
POST_PHONEME_LENGTH = 0.03
FINAL_BGM_TAIL = 1.0
BGM_VOLUME = "-27dB"


# One approved visual cut maps to one narration segment. Wording stays close
# to the approved script and the shorter on-screen message.
NARRATION = [
    "レントゲン後も、家族に会って大丈夫です。",
    "撮影後、体から放射線が出ることはありません。",
    "案内があれば確認して、普段どおりで大丈夫です。",
    "家族に近づいていいのか、気になりますよね。",
    "放射線が出るのは、撮影している間だけです。",
    "抱っこしても、そばにいても大丈夫です。",
    "放射性の薬を使う検査は、案内に従ってください。",
    "帰ったら、いつもどおり家族と過ごしてください。",
    "家族に聞かれたら、レントゲン後、体から放射線は出ないよ、と伝えられます。",
    "家族に聞かれたときに見返せるよう、保存しておいてください。",
]


def run(command: list[Path | str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(item) for item in command],
        check=True,
        capture_output=True,
        text=True,
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
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.96,
            "pauseLengthScale": PAUSE_LENGTH_SCALE,
            "prePhonemeLength": PRE_PHONEME_LENGTH,
            "postPhonemeLength": POST_PHONEME_LENGTH,
            "volumeScale": 1.0,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image_file:
        header = image_file.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"PNGとして読めません: {path}")
    return struct.unpack(">II", header[16:24])


def concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def approved_sources() -> list[Path]:
    pattern = re.compile(r"^\|\s*(\d{2})\s*\|\s*`([^`]+\.png)`\s*\|")
    entries = []
    for line in PRODUCTION_MANIFEST.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            entries.append((int(match.group(1)), Path(match.group(2)).resolve()))
    entries.sort(key=lambda item: item[0])
    if [cut for cut, _ in entries] != list(range(1, len(NARRATION) + 1)):
        raise ValueError("production_manifest.mdの承認カット順が1〜10ではありません。")
    return [path for _, path in entries]


def load_locked_frames() -> tuple[list[Path], list[dict], list[Path]]:
    sources = approved_sources()
    telop_data = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    if len(telop_data) != len(NARRATION):
        raise ValueError("テロップ数とナレーション数が一致しません。")
    if [item["cut"] for item in telop_data] != list(range(1, len(NARRATION) + 1)):
        raise ValueError("telop_manifest.jsonのカット順が1〜10ではありません。")
    if [Path(item["source"]).resolve() for item in telop_data] != sources:
        raise ValueError("承認画像とテロップ画像の対応が一致しません。")

    frames = [Path(item["output"]).resolve() for item in telop_data]
    listed = sorted(TELOP_DIR.glob("telop_[0-9][0-9]_*.png"))
    if listed != frames:
        raise ValueError("テロップフォルダの画像一覧とmanifestが一致しません。")
    for source, frame in zip(sources, frames):
        if not source.exists() or not frame.exists():
            raise FileNotFoundError(source if not source.exists() else frame)
        if png_size(frame) != (1080, 1920):
            raise ValueError(f"テロップ画像が1080x1920ではありません: {frame}")
    return frames, telop_data, sources


def detect_long_silences(audio: Path) -> list[dict]:
    completed = run(
        [
            FFMPEG,
            "-hide_banner",
            "-i",
            audio,
            "-af",
            "silencedetect=noise=-42dB:d=0.40",
            "-f",
            "null",
            "-",
        ]
    )
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", completed.stderr)]
    endings = [
        (float(end), float(duration))
        for end, duration in re.findall(
            r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", completed.stderr
        )
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
        raise ValueError(f"動画尺を取得できません: {media}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
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
        run([FFMPEG, "-y", "-ss", f"{timestamp:.3f}", "-i", video, "-frames:v", "1", sample])
        samples.append(sample)
        elapsed += duration

    thumb_w, thumb_h, label_h, columns = 216, 384, 36, 5
    rows = math.ceil(len(samples) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), (246, 248, 250))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT_PATH), 20)
    for index, sample in enumerate(samples):
        x = (index % columns) * thumb_w
        y = (index // columns) * (thumb_h + label_h)
        with Image.open(sample) as image:
            sheet.paste(cover(image, (thumb_w, thumb_h)), (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill="white")
        draw.text((x + 8, y + thumb_h + 7), f"CUT {index + 1:02d}", font=label_font, fill=(16, 36, 55))
    output = QA_DIR / "contact_sheet_video_samples.png"
    sheet.save(output)
    return output


def main() -> None:
    for required in (FFMPEG, BGM, FONT_PATH, PRODUCTION_MANIFEST, TELOP_MANIFEST):
        if not required.exists():
            raise FileNotFoundError(required)

    frames, telop_data, sources = load_locked_frames()
    for directory in (AUDIO_DIR, WORK_DIR, VIDEO_DIR, QA_DIR, FINAL_OUT.parent):
        directory.mkdir(parents=True, exist_ok=True)

    voice_paths = []
    voice_durations = []
    for index, text in enumerate(NARRATION, start=1):
        voice_path = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(text, voice_path)
        voice_paths.append(voice_path)
        voice_durations.append(wav_duration(voice_path))

    voice_list = WORK_DIR / "voice_segments.txt"
    concat_list(voice_paths, voice_list)
    voice_all = AUDIO_DIR / "narration.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_durations = voice_durations.copy()
    video_durations[-1] += FINAL_BGM_TAIL
    video_segments = []
    for index, (frame, duration) in enumerate(zip(frames, video_durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-t",
                f"{duration:.6f}",
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
        video_segments.append(segment)

    video_list = WORK_DIR / "video_segments.txt"
    concat_list(video_segments, video_list)
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    total_duration = sum(video_durations)
    fade_start = max(0.0, total_duration - 0.8)
    audio_filter = (
        f"[1:a]apad=pad_dur={FINAL_BGM_TAIL:.3f},atrim=duration={total_duration:.6f},volume=1.4[voice];"
        f"[2:a]volume={BGM_VOLUME},afade=t=out:st={fade_start:.3f}:d=0.8[bgm];"
        "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]"
    )
    run(
        [
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
            f"{total_duration:.6f}",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            ASSET_OUT,
        ]
    )
    shutil.copy2(ASSET_OUT, FINAL_OUT)

    long_silences = detect_long_silences(voice_all)
    measured_duration = probe_duration(ASSET_OUT)
    sample_sheet = make_video_sample_sheet(ASSET_OUT, video_durations)
    if abs(measured_duration - total_duration) > 0.12:
        raise ValueError(
            f"動画尺が一致しません: expected={total_duration:.3f}, measured={measured_duration:.3f}"
        )

    mapping = []
    cursor = 0.0
    for index, (source, frame, telop, text, voice, voice_duration, video_duration) in enumerate(
        zip(sources, frames, telop_data, NARRATION, voice_paths, voice_durations, video_durations), start=1
    ):
        mapping.append(
            {
                "cut": index,
                "start_seconds": round(cursor, 3),
                "end_seconds": round(cursor + video_duration, 3),
                "source_image": str(source),
                "telop_frame": str(frame),
                "telop_text": telop["telop"],
                "voice_text": text,
                "voice_file": str(voice),
                "voice_duration_seconds": round(voice_duration, 3),
                "image_voice_alignment_checked": True,
            }
        )
        cursor += video_duration

    VIDEO_MANIFEST.write_text(
        json.dumps(
            {
                "title": "レントゲンを撮ったあと、家族に会っていい？",
                "speaker": f"VOICEVOX speaker id {SPEAKER}",
                "voice_speed": VOICE_SPEED,
                "pause_length_scale": PAUSE_LENGTH_SCALE,
                "pre_phoneme_length": PRE_PHONEME_LENGTH,
                "post_phoneme_length": POST_PHONEME_LENGTH,
                "artificial_transition_silence_seconds": 0.0,
                "final_bgm_only_tail_seconds": FINAL_BGM_TAIL,
                "bgm": str(BGM),
                "bgm_volume": BGM_VOLUME,
                "cut_mapping": mapping,
                "narration_duration_seconds": round(sum(voice_durations), 3),
                "expected_video_duration_seconds": round(total_duration, 3),
                "measured_video_duration_seconds": round(measured_duration, 3),
                "silence_detection_threshold": "-42 dB for 0.40 seconds",
                "detected_long_silences": long_silences,
                "voice_audio": str(voice_all),
                "asset_video": str(ASSET_OUT),
                "final_video": str(FINAL_OUT),
                "video_sample_sheet": str(sample_sheet),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )

    print(voice_all)
    print(ASSET_OUT)
    print(FINAL_OUT)
    print(f"narration_seconds={sum(voice_durations):.3f}")
    print(f"video_seconds={measured_duration:.3f}")
    print(f"long_silences={len(long_silences)}")
    print(sample_sheet)


if __name__ == "__main__":
    main()
