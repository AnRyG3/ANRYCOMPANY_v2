from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "family_accompanying_exam_general"
FRAME_DIR = ROOT / "reel_assets" / "family_accompanying_exam_general_telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2

TITLE = "親の検査、付き添いは検査室まで一緒に入れますか"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / OUT.name

FRAMES = [
    "approved_20260804_frame_01_exam_room_door_telop.png",
    "approved_20260804_frame_02_threshold_confusion_telop.png",
    "approved_20260804_frame_03_empathy_hands_telop.png",
    "approved_20260804_frame_04_exam_type_rules_telop.png",
    "approved_20260804_frame_05_ct_safety_management_telop.png",
    "approved_20260804_frame_06_waiting_outside_telop.png",
    "approved_20260804_frame_07_support_nearby_telop.png",
    "approved_20260804_frame_08_ask_before_exam_telop.png",
    "approved_20260804_frame_09_mild_concern_waiting_telop.png",
    "approved_20260804_frame_10_staff_voice_support_telop_v2.png",
    "approved_20260804_frame_11_save_cta_background_telop.png",
    "approved_20260804_frame_12_follow_cta_background_telop.png",
]

DISPLAY_NARRATION = [
    "親の検査、検査室まで一緒に入れる？",
    "検査室の前で、離れなければいけないの？と急に不安になることがあります。",
    "その気持ち、おかしくありません。",
    "実は、検査室へ一緒に入れるかどうかは、検査の種類や施設のルールによって異なります。",
    "X線やCTなど放射線を使う検査では、安全管理のため、外で待っていただくことがあります。",
    "付き添いの方には、検査室の外で待っていただく時間もあります。",
    "一方で、検査によっては、そばにいていただいた方が安心につながる場合もあります。",
    "分からないときは、検査前にスタッフへ確認しておくと安心です。",
    "それでも、「一人にさせてしまって大丈夫かな」と心配になることもあります。",
    "離れる場合も、スタッフが声をかけながら検査を進めていきます。",
    "付き添いで迷ったときのために、保存しておいてください。",
    "検査前の不安を減らす話を、フォローして一緒に確認していきましょう。",
]

VOICE_TEXT = [
    "親の検査、検査室まで一緒に、はいることはできるのでしょうか。",
    "検査室の前で、離れなければいけないのかな、と、急に不安になることがあります。",
    "その気持ち、おかしくありません。",
    "実は、検査室へ一緒に、はいることができるかどうかは、検査の種類や施設のルールによって異なります。",
    "エックス線やシーティーなど、放射線を使う検査では、安全管理のため、外で待っていただくことがあります。",
    "付き添いのかたには、検査室の外で待っていただく時間もあります。",
    "一方で、検査によっては、そばにいていただいたほうが、安心につながる場合もあります。",
    "分からないときは、検査前にスタッフへ確認しておくと安心です。",
    "それでも、一人にさせてしまって大丈夫かな、と心配になることもあります。",
    "離れる場合も、スタッフが声をかけながら、検査を進めていきます。",
    "付き添いで迷ったときのために、保存しておいてください。",
    "検査前の不安を減らす話を、フォローして一緒に確認していきましょう。",
]

MIN_DURATIONS = [2.8, 4.2, 2.4, 2.4, 4.8, 3.4, 4.4, 3.6, 4.2, 3.6, 3.0, 4.0]
TAIL_PADDING_SECONDS = 0.12


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


def concat_file(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


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
        duration = max(MIN_DURATIONS[index - 1], wav_duration(voice) + TAIL_PADDING_SECONDS)
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

    video_txt = WORK_DIR / "video_segments.txt"
    voice_txt = WORK_DIR / "voice_segments.txt"
    silent_video = WORK_DIR / "silent.mp4"
    voice_all = AUDIO_DIR / "voice.wav"

    concat_file(segment_paths, video_txt)
    concat_file(padded_wavs, voice_txt)
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_txt, "-c", "copy", silent_video])
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
        "title": TITLE,
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": "-22dB",
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
    print(f"total_seconds={sum(durations):.3f}")


if __name__ == "__main__":
    main()
