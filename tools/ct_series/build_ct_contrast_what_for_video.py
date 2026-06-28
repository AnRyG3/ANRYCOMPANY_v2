from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_what_for_v1"
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
OUT = ASSET_DIR / "造影剤って何のために使うの.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "造影剤って何のために使うの.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2

NARRATION = [
    "CTの予約をしたら、造影剤を使いますと言われて、不安になっていませんか。",
    "造影剤は、CTをより正確にするために使う薬です。必要性や体調を確認しながら使われます。",
    "造影剤を使うと、単純CTよりも血管や組織の見え方がより鮮明になります。判断しにくい部分を、はっきり確認するために使います。",
    "たとえば、がんや炎症では、血流や造影され方の違いが画像に現れることがあります。造影剤は、その違いを確認する助けになります。",
    "造影剤は、腕の静脈から注射します。点滴の針を刺すのと同じイメージです。",
    "注射のあと、体が温かくなる感覚があることがあります。これは造影剤の性質によるもので、異常ではありません。",
    "検査中は、医師や診療放射線技師が状態を確認しながら進めます。一人で受けるわけではありません。",
    "造影が必要と言われたのは、より正確に確認したいという判断です。追加されたからといって、必ずしも悪い結果が出ているわけではありません。",
    "造影CTは、毎日多くの患者さんが受けている検査です。特別なことではありません。",
    "不安に感じるのはおかしくありません。でも、あなたのために選ばれた検査です。",
    "次回は、検査前に絶食や水分制限があるのはなぜ、をお伝えします。",
    "検査や健診の不安を減らす解説を続けています。保存とフォローで、次の投稿もお届けできます。",
]

FRAMES = [
    "S01_home_appointment_telop.png",
    "S02_reassured_patient_telop.png",
    "S03_ct_room_wide_telop.png",
    "S04_ct_monitor_telop.png",
    "S05_iv_line_telop.png",
    "S06_on_ct_table_telop.png",
    "S07_control_room_telop.png",
    "S08_doctor_explanation_telop.png",
    "S09_empty_corridor_telop.png",
    "S10_window_reassured_telop.png",
    "S11_next_preview_phone_telop.png",
    "S12_cta_phone_hands_telop.png",
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
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def synthesize_voice(text: str, out: Path):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = VOICE_SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


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
        min_duration = 3.0
        if idx in {3, 4, 8}:
            min_duration = 4.0
        if idx in {11, 12}:
            min_duration = 3.4
        duration = max(min_duration, wav_duration(voice) + 0.42)
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

    silent = WORK_DIR / "silent.mp4"
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
            silent,
        ]
    )
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            silent,
            "-i",
            voice_all,
            "-stream_loop",
            "-1",
            "-i",
            BGM,
            "-filter_complex",
            "[1:a]volume=1.45[voice];[2:a]volume=-22dB[bgm];"
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
        "title": "造影剤って何のために使うの？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": "-22 dB",
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
