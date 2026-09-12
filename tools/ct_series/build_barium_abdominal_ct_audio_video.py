from __future__ import annotations

import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "barium_abdominal_ct_v1_images"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "胃のバリウム検査のあと、すぐ腹部CTを受けてもいい？.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"


# One narration segment maps to exactly one telop frame. Voice-only text uses
# kana for unambiguous readings, and no artificial still-frame padding is added.
SEGMENTS = [
    {
        "frame": "01_hook_appointment_slip_telop.png",
        "display": "バリウム検査の3日後に 腹部CT。このまま受けていい？",
        "voice": "ばりうむ検査の3日後に、腹部シーティー。このまま受けていいのかな。",
    },
    {
        "frame": "02_call_to_confirm_telop.png",
        "display": "まず、予約先へ確認しましょう",
        "voice": "まずは、腹部シーティーの予約先へ、確認しましょう。",
    },
    {
        "frame": "03_ct_room_telop.png",
        "display": "確認が必要な主な理由は 画像への影響です",
        "voice": "確認が必要な主な理由は、画像への影響です。",
    },
    {
        "frame": "04_patient_ct_room_telop.png",
        "display": "腸に残ったバリウム 白く強く映ります",
        "voice": "腸にばりうむが残ると、シーティーでは、白く強く映ります。",
    },
    {
        "frame": "05_ct_control_room_telop.png",
        "display": "その周りが見えにくく なることがあります",
        "voice": "すると、その周りが見えにくくなることがあります。",
    },
    {
        "frame": "06_calm_explanation_telop.png",
        "display": "画像を正確に見るための確認です",
        "voice": "画像を正確に見るために、確認が必要なんです。",
    },
    {
        "frame": "07_calendar_check_telop.png",
        "display": "1週間ほど空ける案内もあります",
        "voice": "いっしゅうかんほど、間隔を空ける案内もあります。",
    },
    {
        "frame": "08_tell_staff_telop.png",
        "display": "ただし、施設や検査内容で対応は異なります",
        "voice": "ただし、施設や検査内容によって、対応は異なります。",
    },
    {
        "frame": "09_call_with_date_telop.png",
        "display": "「○日にバリウム検査」と予約先へ伝えましょう",
        "voice": "予約のときに、ばりうむ検査を受けた日を、伝えましょう。",
    },
    {
        "frame": "10_save_cta_background_telop.png",
        "display": "腹部CT前に見返せるよう 保存・共有",
        "voice": "腹部シーティーの前に見返せるよう、保存して、ご家族にも共有してください。",
    },
]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(item) for item in command], check=True)


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
            "intonationScale": 0.96,
            "pauseLengthScale": 0.35,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.02,
            "postPhonemeLength": 0.05,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    if not FFMPEG.exists() or not BGM.exists():
        raise FileNotFoundError("ffmpeg or BGM is missing")

    frame_paths = [FRAME_DIR / segment["frame"] for segment in SEGMENTS]
    for frame in frame_paths:
        if not frame.exists():
            raise FileNotFoundError(frame)

    voice_paths = []
    durations = []
    for index, segment in enumerate(SEGMENTS, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(segment["voice"], voice)
        voice_paths.append(voice)
        durations.append(wav_duration(voice))

    voice_list = WORK_DIR / "voice_segments.txt"
    voice_list.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in voice_paths), encoding="utf-8"
    )
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_segments = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        segment = WORK_DIR / f"segment_{index:02d}.mp4"
        run(
            [
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
            ]
        )
        video_segments.append(segment)

    video_list = WORK_DIR / "video_segments.txt"
    video_list.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in video_segments), encoding="utf-8"
    )
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])
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
            f"[1:a]volume=1.4[voice];[2:a]volume={BGM_VOLUME}[bgm];"
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

    MANIFEST.write_text(
        json.dumps(
            {
                "title": "胃のバリウム検査のあと、すぐ腹部CTを受けてもいい？",
                "speaker": f"VOICEVOX speaker id {SPEAKER}",
                "voice_speed": VOICE_SPEED,
                "artificial_transition_silence_seconds": 0,
                "voice_text": [segment["voice"] for segment in SEGMENTS],
                "display_text": [segment["display"] for segment in SEGMENTS],
                "frames": [str(path) for path in frame_paths],
                "durations_seconds": [round(value, 3) for value in durations],
                "total_seconds": round(sum(durations), 3),
                "voice_audio": str(voice_all),
                "asset_video": str(OUT),
                "final_video": str(FINAL_OUT),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8-sig",
    )
    print(OUT)
    print(FINAL_OUT)
    print(round(sum(durations), 3))


if __name__ == "__main__":
    main()
