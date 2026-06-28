from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_side_effects_v1"
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
OUT = ASSET_DIR / "造影剤の副作用やアレルギーが怖い方へ.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "造影剤の副作用やアレルギーが怖い方へ.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-23dB"

NARRATION = [
    "造影剤の副作用やアレルギーが怖くて、検査が不安なかたへ。",
    "怖いと感じるのは、おかしくありません。体に注射するものですから、不安になって当然です。",
    "造影剤の副作用には、軽いものと、重いものがあります。",
    "軽い副作用は、吐き気、かゆみ、ほっしんなどです。目安として、約百人に二人の割合で起こることがあります。",
    "重い副作用は、呼吸困難、血圧低下などです。目安として、およそ二千五百人に一人の割合とされています。",
    "可能性はゼロではありません。ただし、万が一に備えて、医療スタッフが検査中も検査後も対応できる体制を整えています。",
    "以前に造影剤で気分が悪くなったことがあるかた、アレルギーやぜんそくがあるかたは、必ず事前にスタッフへ伝えてください。",
    "検査前の問診票にある質問は、あなたのリスクを確認するためのものです。正確に答えることが安全につながります。",
    "副作用は検査後、数時間から数日後に出ることもあります。気になる症状が出たら、検査を受けた医療機関へ連絡してください。",
    "リスクを知った上で検査に臨むことが、一番安心につながります。",
    "あなたの安全のために、医療スタッフは準備しています。",
    "検査や健診の不安を減らす解説を続けています。保存とフォローで、次の投稿もお届けできます。",
]

FRAMES = [
    "s01_home_anxiety_telop.png",
    "s02_reassurance_home_telop.png",
    "s03_ct_room_overview_telop.png",
    "s04_iv_preparation_telop.png",
    "s05_staff_monitoring_patient_telop.png",
    "s06_control_room_monitoring_telop.png",
    "s07_pre_exam_interview_telop.png",
    "s08_questionnaire_closeup_telop.png",
    "s09_after_exam_phone_call_telop.png",
    "s10_calm_after_understanding_telop.png",
    "s11_pre_exam_staff_reassurance_telop.png",
    "s12_cta_smartphone_telop.png",
]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path, params=None, payload=None):
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()


def synthesize_voice(text: str, out: Path):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = VOICE_SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.96
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def min_duration_for(index: int) -> float:
    if index in {4, 5, 6, 7, 8, 9, 12}:
        return 5.2
    if index in {2, 10, 11}:
        return 4.0
    return 3.4


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    frames = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frames]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(min_duration_for(idx), wav_duration(voice) + 0.42)
        durations.append(duration)
        run(
            [
                FFMPEG,
                "-y",
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

    frames_txt = WORK_DIR / "frames.txt"
    with frames_txt.open("w", encoding="utf-8") as f:
        for frame, duration in zip(frames, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1].as_posix()}'\n")

    voice_txt = WORK_DIR / "voice_segments.txt"
    with voice_txt.open("w", encoding="utf-8") as f:
        for wav in padded_wavs:
            f.write(f"file '{wav.as_posix()}'\n")

    silent_video = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
    run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            frames_txt,
            "-vf",
            "scale=1080:1920,format=yuv420p",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            silent_video,
        ]
    )
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
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
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,"
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

    manifest = {
        "title": "造影剤の副作用やアレルギーが怖い方へ",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frames],
        "narration": NARRATION,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(FINAL_OUT)


if __name__ == "__main__":
    main()
