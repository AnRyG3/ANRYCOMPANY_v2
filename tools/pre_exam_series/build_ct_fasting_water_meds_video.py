from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "pre_exam_series" / "05_ct_fasting_water_meds_v1"
FRAME_DIR = ASSET_DIR / "final_text_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
FFPROBE = ROOT / "tools" / "ffmpeg" / "bin" / "ffprobe.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)

OUT = ASSET_DIR / "検査前に絶食や水分制限があるのはなぜ.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "検査前に絶食や水分制限があるのはなぜ.mp4"
)
MANIFEST = ASSET_DIR / "video_manifest.json"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2

FRAMES = [
    "01_reception.png",
    "02_reassure.png",
    "03_contrast_nausea.png",
    "04_airway_risk.png",
    "05_for_safety.png",
    "06_water_depends.png",
    "07_ask_water.png",
    "08_medicine_water.png",
    "09_medicine_separate.png",
    "10_follow_instruction.png",
    "11_ask_before_exam.png",
    "12_save_follow.png",
]

DISPLAY_NARRATION = [
    "CT検査の前に「絶食してください」と言われて、なぜと思いませんでしたか。",
    "理由がわかると、準備の大切さが納得できます。",
    "造影剤を使う検査では、まれに吐き気や気分不快が起こることがあります。",
    "そのとき胃に食べ物が残っていると、嘔吐した際に気道へ入る危険があります。それを防ぐために、絶食が指示されることがあります。",
    "あなたの安全のための準備です。",
    "水分については、検査の目的によって指示が異なります。担当のスタッフに確認してください。",
    "水分は少し飲んでもいいですか、と聞くことはおかしくありません。遠慮せず確認してください。",
    "普段飲んでいる薬は、絶食中でも少量の水で飲むよう指示される場合があります。ただし薬の種類によって異なるため、事前に確認してください。",
    "絶食と言われたから薬も飲まなかった、は体調に影響することがあります。薬と食事の指示は別物です。",
    "絶食の時間や内容は施設によって異なります。指示された内容を守ることが最も安全です。",
    "不安なことは検査前に聞いてください。確認することは正しい行動です。",
    "検査の不安を減らす解説を続けています。保存とフォローで次の投稿もお届けできます。",
]

VOICEVOX_TEXT = [
    "シーティー検査の前に、絶食してください、と言われて、なぜと思いませんでしたか。",
    "理由がわかると、準備の大切さが納得できます。",
    "造影剤を使う検査では、まれに吐き気や、気分不快が起こることがあります。",
    "そのとき胃に食べ物が残っていると、おうとした際に、気道へ入る危険があります。それを防ぐために、絶食が指示されることがあります。",
    "あなたの安全のための準備です。",
    "水分については、検査の目的によって指示が異なります。担当のスタッフに確認してください。",
    "水分は少し飲んでもいいですか、と聞くことはおかしくありません。遠慮せず確認してください。",
    "普段飲んでいる薬は、絶食中でも少量の水で飲むよう指示される場合があります。ただし薬の種類によって異なるため、事前に確認してください。",
    "絶食と言われたから薬も飲まなかった、は体調に影響することがあります。薬と食事の指示は別物です。",
    "絶食の時間や内容は施設によって異なります。指示された内容を守ることが最も安全です。",
    "不安なことは検査前に聞いてください。確認することは正しい行動です。",
    "検査の不安を減らす解説を続けています。保存とフォローで次の投稿もお届けできます。",
]

MIN_DURATIONS = [3.5, 3.0, 4.2, 6.2, 2.7, 4.6, 4.6, 6.5, 5.6, 4.8, 4.0, 4.8]


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

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for idx, text in enumerate(VOICEVOX_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[idx - 1], wav_duration(voice) + 0.35)
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
        for frame, duration in zip(frame_paths, durations):
            f.write(f"file '{frame.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frame_paths[-1].as_posix()}'\n")

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
            "[1:a]volume=1.45[voice];[2:a]volume=-24dB[bgm];"
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
        "title": "検査前に絶食や水分制限があるのはなぜ",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": "-24 dB",
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voicevox_text": VOICEVOX_TEXT,
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
