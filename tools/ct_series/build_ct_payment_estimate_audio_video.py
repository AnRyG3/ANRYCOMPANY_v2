from __future__ import annotations

import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_payment_estimate_v1_samples"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
SOURCE_MANIFEST = ASSET_DIR / "production_manifest.md"
TELOP_MANIFEST = FRAME_DIR / "telop_manifest.json"
VIDEO_MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
OUT = ASSET_DIR / "CTを撮る日の会計、いくらくらい？.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / OUT.name
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"
FINAL_BGM_TAIL_SECONDS = 1.0


# One narration segment maps to exactly one approved telop frame.  There is no
# added silence between cuts. The last CTA remains visible for one second with
# BGM after the narration, as required by voice-rules.md.
SEGMENTS = [
    {
        "source": "scene_01_ct_payment_question_v2.png",
        "frame": "telop_01_payment_estimate.png",
        "display": "CTの日 会計の目安／事前に聞いて大丈夫",
        "voice": "シーティーを撮る日の会計が気になるときは、事前に受付や会計窓口で、目安を聞いて大丈夫です。",
    },
    {
        "source": "scene_02_reception_guidance.png",
        "frame": "telop_02_hospital_difference.png",
        "display": "金額は／病院ごとに違います",
        "voice": "金額は病院ごとに違うので、先に聞いておくと安心です。",
    },
    {
        "source": "scene_03_payment_method.png",
        "frame": "telop_03_payment_method.png",
        "display": "使える／支払い方法も確認",
        "voice": "あわせて、クレジットカードなど、使える支払い方法も確認してください。",
    },
    {
        "source": "scene_04_payment_concern.png",
        "frame": "telop_04_payment_concern.png",
        "display": "当日の会計／気になりますよね",
        "voice": "当日の会計がいくらになるのか、気になりますよね。",
    },
    {
        "source": "scene_05_ct_contrast_difference.png",
        "frame": "telop_05_contrast_cost.png",
        "display": "造影剤の有無で／費用が変わることも",
        "voice": "シーティーの費用は、ぞうえい剤を使うかどうかで変わります。",
    },
    {
        "source": "scene_06_consultation_and_ct_flow.png",
        "frame": "telop_06_other_factors.png",
        "display": "初診・再診／診察やほかの検査でも／金額が変わることも",
        "voice": "初診か再診か、診察やほかの検査が一緒かどうかでも変わります。",
    },
    {
        "source": "scene_07_coverage_difference.png",
        "frame": "telop_07_burden_ratio.png",
        "display": "負担割合によって／窓口の金額は変わります",
        "voice": "保険の負担割合によっても、窓口で払う金額は違います。",
    },
    {
        "source": "scene_08_confirm_at_reception.png",
        "frame": "telop_08_where_to_ask.png",
        "display": "目安と支払い方法は／受付・会計窓口へ",
        "voice": "会計の目安や支払い方法は、受付や会計窓口に確認してみてください。",
    },
    {
        "source": "scene_09_note_for_preparation.png",
        "frame": "telop_09_prepare.png",
        "display": "目安がわかると／当日の準備がしやすい",
        "voice": "聞きにくくても、目安がわかると、当日の準備がしやすくなります。",
    },
    {
        "source": "scene_10_ask_reception_v2.png",
        "frame": "telop_10_question_phrase.png",
        "display": "だいたいいくらになりそうですか？／使える支払い方法も教えてください",
        "voice": "聞くときは、こう伝えてみてください。シーティー検査がある日の会計は、だいたいいくらになりそうですか。使える支払い方法も教えてください。",
    },
    {
        "source": "scene_11_save_before_exam_day.png",
        "frame": "telop_11_save.png",
        "display": "予約日の前に／見返せるよう 保存",
        "voice": "予約日の前に見返せるよう、保存しておいてください。",
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
            "prePhonemeLength": 0.01,
            "postPhonemeLength": 0.04,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def validate_source_lock() -> list[Path]:
    if not SOURCE_MANIFEST.exists() or not TELOP_MANIFEST.exists():
        raise FileNotFoundError("production_manifest.md or telop_manifest.json is missing")

    source_manifest_text = SOURCE_MANIFEST.read_text(encoding="utf-8-sig")
    telop_entries = json.loads(TELOP_MANIFEST.read_text(encoding="utf-8-sig"))
    if len(telop_entries) != len(SEGMENTS):
        raise RuntimeError("Telop frame count does not match narration segment count")

    frame_paths: list[Path] = []
    for index, (segment, entry) in enumerate(zip(SEGMENTS, telop_entries), start=1):
        source = ASSET_DIR / segment["source"]
        frame = FRAME_DIR / segment["frame"]
        if str(source) not in source_manifest_text:
            raise RuntimeError(f"Cut {index:02d} source is not locked in production_manifest.md")
        if Path(entry["source"]) != source or Path(entry["output"]) != frame:
            raise RuntimeError(f"Cut {index:02d} telop mapping differs from the source lock")
        if not source.exists() or not frame.exists():
            raise FileNotFoundError(source if not source.exists() else frame)
        frame_paths.append(frame)
    return frame_paths


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    if not FFMPEG.exists() or not BGM.exists():
        raise FileNotFoundError("ffmpeg or BGM is missing")

    frame_paths = validate_source_lock()

    voice_paths: list[Path] = []
    durations: list[float] = []
    for index, segment in enumerate(SEGMENTS, start=1):
        voice_path = AUDIO_DIR / f"voice_{index:02d}.wav"
        synthesize_voice(segment["voice"], voice_path)
        voice_paths.append(voice_path)
        durations.append(wav_duration(voice_path))

    voice_list = WORK_DIR / "voice_segments.txt"
    voice_list.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in voice_paths), encoding="utf-8"
    )
    voice_all = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])

    video_segments: list[Path] = []
    for index, (frame, duration) in enumerate(zip(frame_paths, durations), start=1):
        if index == len(frame_paths):
            duration += FINAL_BGM_TAIL_SECONDS
        video_segment = WORK_DIR / f"segment_{index:02d}.mp4"
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
                video_segment,
            ]
        )
        video_segments.append(video_segment)

    video_list = WORK_DIR / "video_segments.txt"
    video_list.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in video_segments), encoding="utf-8"
    )
    silent_video = WORK_DIR / "silent.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", silent_video])

    narration_seconds = sum(durations)
    total_seconds = narration_seconds + FINAL_BGM_TAIL_SECONDS
    fade_start = max(0.0, total_seconds - FINAL_BGM_TAIL_SECONDS)
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
            f"[1:a]volume=1.45,apad=pad_dur={FINAL_BGM_TAIL_SECONDS}[voice];"
            f"[2:a]volume={BGM_VOLUME},atrim=duration={total_seconds:.3f},"
            f"afade=t=out:st={fade_start:.3f}:d={FINAL_BGM_TAIL_SECONDS}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-t",
            f"{total_seconds:.3f}",
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

    VIDEO_MANIFEST.write_text(
        json.dumps(
            {
                "title": "CTを撮る日の会計、いくらくらい？",
                "speaker": f"VOICEVOX speaker id {SPEAKER}",
                "voice_speed": VOICE_SPEED,
                "artificial_transition_silence_seconds": 0,
                "final_bgm_tail_seconds": FINAL_BGM_TAIL_SECONDS,
                "voice_text": [segment["voice"] for segment in SEGMENTS],
                "display_text": [segment["display"] for segment in SEGMENTS],
                "source_images": [str(ASSET_DIR / segment["source"]) for segment in SEGMENTS],
                "frames": [str(path) for path in frame_paths],
                "voice_files": [str(path) for path in voice_paths],
                "durations_seconds": [round(value, 3) for value in durations],
                "narration_seconds": round(narration_seconds, 3),
                "total_seconds": round(total_seconds, 3),
                "voice_audio": str(voice_all),
                "bgm": str(BGM),
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
    print(f"narration={narration_seconds:.3f}s total={total_seconds:.3f}s")


if __name__ == "__main__":
    main()
