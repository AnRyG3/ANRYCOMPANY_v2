from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "exam_anxiety_tell_staff_bridge"
FRAME_DIR = ASSET_DIR / "text_frames"
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

OUT = ASSET_DIR / "検査が不安なときどこまで伝えていいの.mp4"
FINAL_OUT = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタ完成形"
    / "検査が不安なときどこまで伝えていいの.mp4"
)

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "01_text_patient_hesitating.png",
    "02_text_rt_tech_reassuring.png",
    "03_text_patient_hesitating_question.png",
    "04_text_rt_tech_taking_notes.png",
    "05_text_parent_child_concerns.png",
    "06_text_rt_tech_adjusting_plan.png",
    "07_text_patient_relieved.png",
    "08_text_adult_patient_bridge.png",
    "09_text_rt_tech_calm_reassurance.png",
    "10_text_rt_tech_supporting_patient.png",
    "11_text_smartphone_save_cta.png",
    "12_text_rt_tech_bowing_end.png",
]

DISPLAY_NARRATION = [
    "不安なこと、全部伝えていいのか分からなくて。そう感じる方は少なくありません。",
    "大丈夫です。検査について気になることは、伝えていただいて大丈夫です。",
    "こんなこと聞いていいのかな、と遠慮される方は、実はとても多いんです。",
    "些細なことでも、教えていただいたほうが、私たちも対応しやすくなります。",
    "お子さんが怖がっていることも、ご自身が緊張していることも、大切な情報です。",
    "伝えていただければ、声のかけ方や進め方を変えることができます。",
    "こんな些細なことで、と思う必要はありません。",
    "検査を受けるのは子どもだけではなく、大人の方の不安も大切です。",
    "不安なまま検査を受けるより、伝えていただくほうが進めやすくなることがあります。",
    "遠慮せず、思っていることを教えてください。",
    "不安なときに見返せるよう、保存しておいてください。",
    "診療放射線技師の発信、フォローで応援お願いします。",
]

VOICEVOX_TEXT = [
    "不安なこと、全部伝えていいのか分からなくて。そう感じるかたは少なくありません。",
    "大丈夫です。検査について気になることは、伝えていただいて大丈夫です。",
    "こんなこと聞いていいのかな、と遠慮されるかたは、実はとても多いんです。",
    "些細なことでも、教えていただいたほうが、私たちも対応しやすくなります。",
    "お子さんが怖がっていることも、ご自身が緊張していることも、大切な情報です。",
    "伝えていただければ、声のかけかたや進めかたを変えることができます。",
    "こんな些細なことで、と思う必要はありません。",
    "検査を受けるのは子どもだけではなく、大人のかたの不安も大切です。",
    "不安なまま検査を受けるより、伝えていただくほうが進めやすくなることがあります。",
    "遠慮せず、思っていることを教えてください。",
    "不安なときに見返せるよう、保存しておいてください。",
    "しんりょうほうしゃせんぎしの発信、フォローで応援お願いします。",
]

MIN_DURATIONS = [4.7, 5.0, 4.8, 4.8, 5.3, 4.8, 3.7, 4.7, 5.4, 3.5, 3.8, 4.5]


def run(cmd: list[Path | str]) -> None:
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path: str, params=None, payload=None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=90) as res:
        return res.read()


def synthesize_voice(text: str, out: Path) -> None:
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = VOICE_SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main() -> None:
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
        "title": "検査が不安なとき、どこまで伝えていいの？",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
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
