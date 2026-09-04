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
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "hearing_aid_check"
FRAME_DIR = ROOT / "reel_assets" / "pre_exam_series" / "hearing_aid_check_telop"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
MANIFEST = ASSET_DIR / "video_manifest_20260830.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

OUT = VIDEO_DIR / "補聴器を外したら説明が聞こえない時_20260830.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"
TAIL_PADDING = 0.12
MIDFRAME_SHEET = ASSET_DIR / "video_qa_midframes_20260830.png"

FRAMES = [
    "telop_01_waiting_with_hearing_aid.png",
    "telop_02_explanation_before_removal.png",
    "telop_03_hearing_aid_listening_close.png",
    "telop_04_mri_before_removal.png",
    "telop_05_hearing_aids_outside_mri.png",
    "telop_06_ct_control_room_check.png",
    "telop_07_ct_light_signal_low_pillow.png",
    "telop_08_ct_patient_sees_light.png",
    "telop_09_reassuring_confirmation.png",
    "telop_10_save_cta_review.png",
    "telop_11_outro_rt_tech.png",
]

DISPLAY_NARRATION = [
    "「補聴器を外してください」と言われたけど、説明が聞こえなくなったらどうしよう。",
    "MRIやCTなどの検査前、補聴器を外す案内で不安になる方がいます。",
    "検査の説明は、補聴器をつけたまま、聞こえる状態で先に行います。",
    "補聴器を外すのは、それぞれの検査の直前で、MRIでは、検査室に入る直前に外していただきます。",
    "外した補聴器は、検査室の外で保管します。",
    "CTでは当院の場合、位置決めの撮影後に、アナウンスが聞こえているか確認しています。",
    "聞こえにくい場合は、事前にお伝えしたうえで、部屋の照明を暗くしたり明るくしたりして合図をします。",
    "声だけでなく、目で見て分かる方法でも確認できるようにしています。",
    "補聴器を外すタイミングも、聞こえない時の対応も、困らないように確認しながら進めています。",
    "補聴器を使っている方やご家族は、検査前日や受付前に見返せるように保存しておいてください。",
    "他の検査前の疑問も、診療放射線技師目線で発信しています。",
]

VOICE_TEXT = [
    "補聴器を外してください、と言われたけど、説明が聞こえなくなったらどうしよう。",
    "MRIやCTなどの検査前、補聴器を外す案内で、不安になるかたがいます。",
    "検査の説明は、補聴器をつけたまま、聞こえる状態で先に行います。",
    "補聴器を外すのは、それぞれの検査の直前で、MRIでは、検査室に入る直前に外していただきます。",
    "外した補聴器は、検査室の外で保管します。",
    "CTでは当院の場合、位置決めの撮影後に、アナウンスが聞こえているか確認しています。",
    "聞こえにくい場合は、事前にお伝えしたうえで、部屋の照明を暗くしたり明るくしたりして、合図をします。",
    "声だけでなく、目で見て分かる方法でも、確認できるようにしています。",
    "補聴器を外すタイミングも、聞こえない時の対応も、困らないように確認しながら進めています。",
    "補聴器を使っているかたやご家族は、検査前日や受付前に見返せるように、保存しておいてください。",
    "ほかの検査前の疑問も、診療放射線技師目線で発信しています。",
]


def run(cmd: list[Path | str]) -> None:
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path: str, params=None, payload=None) -> bytes:
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
            "intonationScale": 0.95,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.05,
            "postPhonemeLength": 0.08,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def media_duration(path: Path) -> float:
    completed = subprocess.run(
        [
            str(FFMPEG),
            "-hide_banner",
            "-i",
            str(path),
        ],
        capture_output=True,
    )
    stderr = completed.stderr.decode("utf-8", errors="ignore")
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    if not match:
        raise RuntimeError(f"Could not read duration from ffmpeg output for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def make_midframe_sheet(video: Path, durations: list[float]) -> None:
    thumbs = []
    elapsed = 0.0
    for index, duration in enumerate(durations, start=1):
        timestamp = elapsed + duration / 2
        thumb = WORK_DIR / f"midframe_{index:02d}.jpg"
        run(
            [
                FFMPEG,
                "-y",
                "-loglevel",
                "error",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                video,
                "-frames:v",
                "1",
                "-q:v",
                "2",
                thumb,
            ]
        )
        thumbs.append((thumb, timestamp))
        elapsed += duration

    cols = 4
    thumb_w, thumb_h = 270, 480
    label_h = 40
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (244, 246, 248))
    label_font = ImageFont.truetype(str(ROOT / "reel_assets" / "fonts" / "M_PLUS_Rounded_1c" / "MPLUSRounded1c-Bold.ttf"), 22)
    draw = ImageDraw.Draw(sheet)
    for idx, (path, timestamp) in enumerate(thumbs):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(img, (x + (thumb_w - img.width) // 2, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(255, 255, 255))
        draw.text((x + 10, y + thumb_h + 8), f"{idx + 1:02d} {timestamp:.1f}s", font=label_font, fill=(12, 34, 64))
    sheet.save(MIDFRAME_SHEET, quality=94)


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs: list[Path] = []
    durations: list[float] = []
    voice_durations: list[float] = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        raw_duration = wav_duration(voice)
        duration = raw_duration + TAIL_PADDING
        voice_durations.append(raw_duration)
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
                f"apad=pad_dur={duration:.3f},atrim=duration={duration:.3f}",
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
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
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

    make_midframe_sheet(OUT, durations)
    video_duration = media_duration(OUT)
    voice_duration = media_duration(voice_all)
    manifest = {
        "title": "補聴器を外したら説明が聞こえない時、どうすればいい？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "raw_voice_seconds": [round(value, 3) for value in voice_durations],
        "durations_seconds": [round(value, 3) for value in durations],
        "tail_padding_seconds_each": TAIL_PADDING,
        "total_planned_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "voice_audio_seconds": round(voice_duration, 3),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "video_seconds": round(video_duration, 3),
        "midframe_qa_sheet": str(MIDFRAME_SHEET),
        "sync_check": "Each frame duration follows its narration segment plus 0.12 seconds to avoid long silent holds.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)
    print(f"planned={sum(durations):.3f}")
    print(f"voice={voice_duration:.3f}")
    print(f"video={video_duration:.3f}")
    print(MIDFRAME_SHEET)


if __name__ == "__main__":
    main()
