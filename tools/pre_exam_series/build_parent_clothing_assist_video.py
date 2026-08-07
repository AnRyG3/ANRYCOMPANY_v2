from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "parent_clothing_assist_video"
FRAME_DIR = ROOT / "reel_assets" / "parent_clothing_assist_telop_frames"
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
BGM_VOLUME = "-25dB"
TAIL_PADDING_SECONDS = 0.3

TITLE = "親の着替えが不安な時_付き添い家族が先に伝えたいこと"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / f"{TITLE}.mp4"

FRAMES = [
    "frame_01_opening_patient_changing_room_telop.png",
    "frame_02_family_view_waiting_area_telop.png",
    "frame_03_reassured_patient_bench_telop.png",
    "frame_04_clothing_varies_by_person_telop.png",
    "frame_05_info_to_share_checklist_telop.png",
    "frame_06_staff_support_preparation_area_telop.png",
    "frame_07_no_need_to_force_patient_telop.png",
    "frame_08_how_much_to_tell_memo_telop.png",
    "frame_09_staff_prepares_gown_telop.png",
    "frame_10_save_cta_background_telop.png",
    "frame_11_follow_cta_background_telop.png",
]

DISPLAY_NARRATION = [
    "親の着替え、一人でできるかな。付き添いながら気になってしまうことがあります。",
    "手伝った方がいいのか、それとも見守るだけでいいのか、迷ってしまう。",
    "その気持ち、おかしくありません。",
    "実は、着替えの手伝いが必要かどうかは、人によって大きく異なります。",
    "普段どのくらい自分で着替えられるか、立つ、袖を通す、ボタンを留める時に手伝いが必要かを、先にスタッフへ伝えていただけると助かります。",
    "施設や状況によって、ご家族に手伝っていただくこともあれば、スタッフが対応することもあります。",
    "無理にご本人だけで着替えようとしなくて大丈夫です。",
    "それでも、どこまで伝えればいいのかと、悩んでしまう。",
    "普段の様子を伝えていただくことが、当日の負担を減らすことにつながっています。",
    "親の検査前に見返せるように、保存しておいてください。",
    "検査前の不安が少し軽くなる話を、診療放射線技師の目線で発信しています。",
]

VOICEVOX_TEXT = [
    "親の着替え、一人でできるかな。付き添いながら気になってしまうことがあります。",
    "手伝ったほうがいいのか、それとも見守るだけでいいのか、迷ってしまう。",
    "その気持ち、おかしくありません。",
    "実は、着替えの手伝いが必要かどうかは、人によって大きく異なります。",
    "普段どのくらい自分で着替えられるか。立つ、袖を通す、ボタンを留める時に手伝いが必要かを、先にスタッフへ伝えていただけると助かります。",
    "施設や状況によって、ご家族に手伝っていただくこともあれば、スタッフが対応することもあります。",
    "無理にご本人だけで着替えようとしなくて大丈夫です。",
    "それでも、どこまで伝えればいいのかと、悩んでしまう。",
    "普段の様子を伝えていただくことが、当日の負担を減らすことにつながっています。",
    "親の検査前に見返せるように、保存しておいてください。",
    "検査前の不安が少し軽くなる話を、しんりょうほうしゃせんぎしの目線で発信しています。",
]

MIN_DURATIONS = [4.6, 4.8, 3.2, 4.8, 8.4, 6.0, 4.7, 4.0, 5.2, 3.8, 5.3]


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


def ffmpeg_info(path: Path) -> str:
    result = subprocess.run(
        [str(FFMPEG), "-hide_banner", "-i", str(path)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        text=True,
    )
    return result.stderr


def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    urllib.request.urlopen(f"{VOICEVOX}/version", timeout=5).read()

    padded_wavs: list[Path] = []
    durations: list[float] = []
    for index, text in enumerate(VOICEVOX_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[index - 1], wav_duration(voice) + TAIL_PADDING_SECONDS)
        durations.append(duration)
        run(
            [
                FFMPEG,
                "-hide_banner",
                "-loglevel",
                "error",
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
                "-hide_banner",
                "-loglevel",
                "error",
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
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", video_txt, "-c", "copy", silent_video])
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", voice_txt, "-c", "copy", voice_all])
    run(
        [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
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
        "title": TITLE,
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
        "ffmpeg_info": ffmpeg_info(FINAL_OUT),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(FINAL_OUT)
    print(f"total_seconds={sum(durations):.3f}")


if __name__ == "__main__":
    main()
