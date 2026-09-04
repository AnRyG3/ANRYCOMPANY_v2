from pathlib import Path
import json
import math
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "libre2_xray_ct_20260831"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
QA_DIR = ASSET_DIR / "qa_midframes"
MANIFEST = ASSET_DIR / "video_manifest_20260831.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

OUT = VIDEO_DIR / "リブレ2_X線_CT検査で外す必要はありますか_20260831.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-26dB"
TAIL_PADDING_SECONDS = 0.06

FRAMES = [
    "telop_01_patient_home_sensor.png",
    "telop_02_reception_sensor_notice.png",
    "telop_03_rt_instruction_update.png",
    "telop_04_old_instruction_leaflet.png",
    "telop_05_ct_room_sensor_check.png",
    "telop_06_mri_entrance_remove.png",
    "telop_07_instruction_transition.png",
    "telop_08_rt_questionnaire_check.png",
    "telop_09_patient_tells_rt.png",
    "telop_10_save_cta_phone.png",
]

DISPLAY_NARRATION = [
    "このセンサー、今日の検査で外すのかな。",
    "まず受付や検査前に、「リブレをつけています」と伝えてください。",
    "FreeStyleリブレ2は、X線・CT検査での案内が見直されました。",
    "以前は、X線やCTの時も外すように書かれていました。",
    "今はX線・CTでは、原則、外す必要はありません。",
    "ただしMRI検査は、今まで通り検査前に外します。",
    "新しい表示は、2026年10月以降に順番に切り替わる予定です。",
    "しばらくは古い説明書の製品もあります。迷う時は現場で確認します。",
    "迷ったら、「これをつけています」と、遠慮なく伝えてください。",
    "検査前日や受付前に見返せるように、保存しておいてください。",
]

VOICE_TEXT = [
    "このセンサー、今日の検査で外すのかな。",
    "まず受付や検査前に、リブレをつけています、と伝えてください。",
    "フリースタイルリブレツーは、エックス線、シーティー検査での案内が見直されました。",
    "以前は、エックス線やシーティーの時も、外すように書かれていました。",
    "今はエックス線、シーティーでは、原則、外す必要はありません。",
    "ただしエムアールアイ検査は、今まで通り、検査前に外します。",
    "新しい表示は、二千二十六年十月以降に、順番に切り替わる予定です。",
    "しばらくは、古い説明書の製品もあります。迷う時は、現場で確認します。",
    "迷ったら、これをつけています、と、遠慮なく伝えてください。",
    "検査前日や受付前に見返せるように、保存しておいてください。",
]


def run(cmd: list[Path | str], capture: bool = False, check: bool = True):
    result = subprocess.run(
        [str(part) for part in cmd],
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
    )
    return result if capture else None


def post_json(path: str, params=None, payload=None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}" + (f"?{query}" if query else "")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def check_voicevox() -> None:
    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()


def synthesize_voice(text: str, output: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update(
        {
            "speedScale": VOICE_SPEED,
            "pitchScale": 0.0,
            "intonationScale": 0.95,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.03,
            "postPhonemeLength": 0.04,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_probe(path: Path) -> str:
    result = run([FFMPEG, "-hide_banner", "-i", path], capture=True, check=False)
    return (result.stderr or "") + (result.stdout or "")


def media_duration(path: Path) -> float:
    text = media_probe(path)
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if not match:
        raise RuntimeError(f"Could not parse duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def has_audio_stream(path: Path) -> bool:
    return "Audio:" in media_probe(path)


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = size
    scale = max(w / img.width, h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def make_qa_contact_sheet(paths: list[Path], output: Path) -> None:
    cols = 2
    thumb_w, thumb_h = 270, 480
    label_h = 40
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    label_font = ImageFont.truetype(
        str(ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"),
        22,
    )
    draw = ImageDraw.Draw(sheet)
    for idx, path in enumerate(paths):
        img = cover(Image.open(path).convert("RGB"), (thumb_w, thumb_h))
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(img, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 10, y + thumb_h + 8), f"{idx + 1:02d}", font=label_font, fill=(12, 34, 64))
    sheet.save(output, quality=94)


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)
    check_voicevox()

    padded_wavs: list[Path] = []
    raw_voice_durations: list[float] = []
    durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        raw_duration = wav_duration(voice)
        duration = raw_duration + TAIL_PADDING_SECONDS
        raw_voice_durations.append(raw_duration)
        durations.append(duration)
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
                "-i",
                voice,
                "-af",
                f"apad=pad_dur={TAIL_PADDING_SECONDS:.3f},atrim=duration={duration:.3f}",
                "-ar",
                "44100",
                "-ac",
                "2",
                padded,
            ]
        )
        padded_wavs.append(padded)

    voice_txt = WORK_DIR / "voice_segments.txt"
    voice_txt.write_text("".join(f"file '{wav.as_posix()}'\n" for wav in padded_wavs), encoding="utf-8")

    segment_paths: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
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
            ]
        )
        segment_paths.append(segment)

    segments_txt = WORK_DIR / "video_segments.txt"
    segments_txt.write_text("".join(f"file '{path.as_posix()}'\n" for path in segment_paths), encoding="utf-8")
    silent_video = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", segments_txt, "-c", "copy", silent_video])
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])

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
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0.1:normalize=0,"
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
            "-movflags",
            "+faststart",
            OUT,
        ]
    )
    shutil.copy2(OUT, FINAL_OUT)

    qa_paths: list[Path] = []
    elapsed = 0.0
    for index, duration in enumerate(durations, start=1):
        midpoint = elapsed + duration / 2
        qa_path = QA_DIR / f"qa_mid_{index:02d}.jpg"
        run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{midpoint:.3f}", "-i", OUT, "-frames:v", "1", qa_path])
        qa_paths.append(qa_path)
        elapsed += duration
    qa_contact = QA_DIR / "qa_midframes_contact_sheet.jpg"
    make_qa_contact_sheet(qa_paths, qa_contact)

    video_seconds = media_duration(OUT)
    voice_seconds = wav_duration(voice_all)
    manifest = {
        "title": "リブレ2をつけたままX線・CT検査を受けてもいい？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "raw_voice_seconds": [round(value, 3) for value in raw_voice_durations],
        "durations_seconds": [round(value, 3) for value in durations],
        "tail_padding_seconds_each": TAIL_PADDING_SECONDS,
        "total_timeline_seconds": round(sum(durations), 3),
        "voice_audio_seconds": round(voice_seconds, 3),
        "video_seconds": round(video_seconds, 3),
        "max_added_gap_seconds": TAIL_PADDING_SECONDS,
        "audio_stream_present": has_audio_stream(OUT),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "qa_contact_sheet": str(qa_contact),
        "alignment_check": [
            {
                "index": i,
                "frame": FRAMES[i - 1],
                "display_narration": DISPLAY_NARRATION[i - 1],
                "voice_text": VOICE_TEXT[i - 1],
                "duration_seconds": round(durations[i - 1], 3),
            }
            for i in range(1, len(FRAMES) + 1)
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)
    print(qa_contact)
    print(f"timeline_seconds={sum(durations):.3f}")
    print(f"voice_seconds={voice_seconds:.3f}")
    print(f"video_seconds={video_seconds:.3f}")
    print(f"audio_stream_present={has_audio_stream(OUT)}")


if __name__ == "__main__":
    main()
