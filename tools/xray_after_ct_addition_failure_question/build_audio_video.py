from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "xray_after_ct_addition_failure_question"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = (
    ROOT
    / "01_ショート動画_リール_YouTubeShorts"
    / "インスタリール用"
    / "BGM フリー素材"
    / "Kind_Heart.mp3"
)
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"

OUT = VIDEO_DIR / "レントゲンのあとCTを追加するのは失敗だったから.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "frame_01_waiting_explanation_telop.png",
    "frame_02_patient_concern_telop.png",
    "frame_03_rt_reassurance_telop.png",
    "frame_04_xray_room_telop.png",
    "frame_05_ct_room_explanation_telop.png",
    "frame_06_bone_images_monitor_telop.png",
    "frame_07_roles_explanation_telop.png",
    "frame_08_doctor_decision_bone_telop.png",
    "frame_09_patient_relieved_telop.png",
    "frame_10_save_cta_bg_telop.png",
    "frame_11_follow_cta_bg_telop.png",
]

DISPLAY_NARRATION = [
    "レントゲンのあとCTも、と言われると、撮り直し？失敗だったの？と不安になりますよね。",
    "そう感じても、おかしくありません。",
    "でも、CTの追加は、レントゲンが失敗だった、という意味ではありません。",
    "レントゲンでは、まず全体の状態を確認します。",
    "必要な部分を、CTで詳しく確認することがあります。",
    "骨の重なりやズレの向きは、レントゲンだけでは分かりにくいこともあります。",
    "レントゲンとCTは、どちらが上というより、それぞれ役割が違う検査です。",
    "CTを追加する必要性は、症状やレントゲンの結果をもとに、医師が判断します。",
    "レントゲンがあるからこそ、次にどこを見るかが決めやすくなります。最初の検査も、無駄ではありません。",
    "検査の流れが不安なときに見返せるよう、保存しておいてください。",
    "患者さんの不安を減らす検査の話を、フォローして一緒に確認していきましょう。",
]

VOICE_TEXT = [
    "レントゲンのあとシーティーも。と言われると、撮り直し。失敗だったの。と不安になりますよね。",
    "そう感じても、おかしくありません。",
    "でも、シーティーの追加は、レントゲンが失敗だった、という意味ではありません。",
    "レントゲンでは、まず全体の状態を確認します。",
    "必要な部分を、シーティーで詳しく確認することがあります。",
    "骨のかさなりやズレの向きは、レントゲンだけでは分かりにくいこともあります。",
    "レントゲンとシーティーは、どちらが上というより、それぞれ役割が違う検査です。",
    "シーティーを追加する必要性は、症状やレントゲンの結果をもとに、医師が判断します。",
    "レントゲンがあるからこそ、次にどこを見るかが決めやすくなります。最初の検査も、無駄ではありません。",
    "検査の流れが不安なときに見返せるよう、保存しておいてください。",
    "患者さんの不安を減らす検査の話を、フォローして一緒に確認していきましょう。",
]

MIN_DURATIONS = [5.2, 2.8, 4.6, 3.6, 3.8, 4.8, 5.0, 5.0, 6.0, 4.6, 5.0]


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
            "prePhonemeLength": 0.08,
            "postPhonemeLength": 0.16,
        }
    )
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


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
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[index - 1], wav_duration(voice) + 0.4)
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

    voice_txt = WORK_DIR / "voice_segments.txt"
    voice_txt.write_text("".join(f"file '{wav.as_posix()}'\n" for wav in padded_wavs), encoding="utf-8")

    silent_video = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"
    segment_paths: list[Path] = []
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
        segment_paths.append(segment)

    segments_txt = WORK_DIR / "video_segments.txt"
    segments_txt.write_text("".join(f"file '{path.as_posix()}'\n" for path in segment_paths), encoding="utf-8")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", segments_txt, "-c", "copy", silent_video])
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
        "title": "レントゲンのあとCTを追加するのは、失敗だったから?",
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "display_narration": DISPLAY_NARRATION,
        "voice_text": VOICE_TEXT,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(OUT)
    print(FINAL_OUT)
    print(round(sum(durations), 3))


if __name__ == "__main__":
    main()
