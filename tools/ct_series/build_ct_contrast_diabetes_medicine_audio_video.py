from __future__ import annotations

import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_diabetes_medicine_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
OUT = ASSET_DIR / "造影CT前、糖尿病の薬はいつも通りでいい？.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"


# Every narration segment maps to one frame. Frame duration is taken directly
# from the synthesized WAV, with no added still-frame padding or long silence.
SEGMENTS = [
    {
        "frame": "01_hook_morning_medicine_telop.png",
        "display": "この糖尿病の薬 今朝も飲んでいい？",
        "voice": "この糖尿病の薬、今朝も飲んでいいのかな。",
    },
    {
        "frame": "02_check_appointment_guidance_telop.png",
        "display": "まず 予約時の案内を確認",
        "voice": "まず、予約時の案内を確認してください。",
    },
    {
        "frame": "03_reassured_no_self_decision_telop.png",
        "display": "自己判断しなくて 大丈夫です",
        "voice": "分からなくても、自己判断しなくて大丈夫です。",
    },
    {
        "frame": "04_compare_medicine_types_telop.png",
        "display": "糖尿病薬の一部は 休むことがあります",
        "voice": "ぞうえいシーティーでは、一部の糖尿病薬を休むことがあります。",
    },
    {
        "frame": "05_check_medicine_details_telop.png",
        "display": "薬の種類や状態で 対応は変わります",
        "voice": "ただし、薬の種類や体の状態で、対応は変わります。",
    },
    {
        "frame": "06_call_medical_facility_telop.png",
        "display": "不明なときは 医療機関へ確認",
        "voice": "案内が分からなければ、検査を受ける医療機関へ確認してください。",
    },
    {
        "frame": "07_bring_medication_notebook_telop.png",
        "display": "当日は お薬手帳を持参",
        "voice": "当日は、お薬手帳など、薬の名前が分かるものを持参してください。",
    },
    {
        "frame": "08_show_medication_notebook_telop.png",
        "display": "受付で自分から 見せて大丈夫です",
        "voice": "受付で、自分から見せて大丈夫です。",
    },
    {
        "frame": "09_prepare_night_before_telop.png",
        "display": "造影CTの前日に 見返せるよう保存",
        "voice": "ぞうえいシーティーの前日に見返せるよう、この投稿を保存してください。",
    },
    {
        "frame": "10_save_share_on_phone_telop.png",
        "display": "付き添うご家族にも この安心を共有",
        "voice": "付き添うご家族にも共有を。次の疑問に備えて、フォローをお願いします。",
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
            "postPhonemeLength": 0.06,
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
        "".join(f"file '{path.as_posix()}'\n" for path in voice_paths),
        encoding="utf-8",
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
        "".join(f"file '{path.as_posix()}'\n" for path in video_segments),
        encoding="utf-8",
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
                "title": "造影CT前、糖尿病の薬はいつも通りでいい？",
                "speaker": f"VOICEVOX speaker id {SPEAKER}",
                "voice_speed": VOICE_SPEED,
                "transition_silence_seconds": 0.08,
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
