from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "family_accompanying_exam_preparation"
FRAME_DIR = ROOT / "reel_assets" / "family_accompanying_exam_preparation_telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
VIDEO_DIR = ASSET_DIR / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
FFPROBE = ROOT / "tools" / "ffmpeg" / "bin" / "ffprobe.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-24dB"
TAIL_PADDING_SECONDS = 0.25

TITLE = "高齢の親を検査に連れて行く時_事前に準備しておきたいこと"
OUT = VIDEO_DIR / f"{TITLE}.mp4"
FINAL_OUT = FINAL_DIR / f"{TITLE}.mp4"

FRAMES = [
    "frame_01_opening_preparation_bag_telop.png",
    "frame_02_mild_uncertainty_bag_telop.png",
    "frame_03_calm_waiting_empathy_telop.png",
    "frame_04_three_point_checklist_telop.png",
    "frame_05_medicine_referral_checklist_telop.png",
    "frame_06_easy_change_clothes_telop.png",
    "frame_07_metal_items_ready_telop.png",
    "frame_08_mild_concern_waiting_telop.png",
    "frame_09_reception_question_ok_telop.png",
    "frame_10_save_cta_background_telop.png",
    "frame_11_follow_cta_background_telop.png",
]

NARRATION = [
    "高齢の親の検査に付き添う時、当日の持ち物で迷うことがあります。",
    "何か足りなかったらどうしようと、直前に不安になることもあります。",
    "その気持ち、おかしくありません。",
    "事前に確認しておくと安心なものを、3つだけお話しします。",
    "お薬手帳や紹介状があれば、持参していただくと確認がスムーズになります。",
    "服装は、検査によって着替えが必要になることもあるため、脱ぎ着しやすい服だと安心です。",
    "金属類やアクセサリーは、検査内容によって外すことがあります。外しやすい状態にしておくと安心です。",
    "それでも、これで足りているかなと不安になることはあります。",
    "分からないことがあれば、当日スタッフに確認していただいて大丈夫です。",
    "付き添い前に見返せるように、保存しておいてください。",
    "検査前の不安を少し軽くする話を、これからも発信しています。",
]

MIN_DURATIONS = [3.2, 3.8, 2.4, 3.6, 4.4, 5.5, 6.0, 3.8, 4.2, 3.4, 4.0]


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

    padded_wavs: list[Path] = []
    durations: list[float] = []
    for index, text in enumerate(NARRATION, start=1):
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

    metadata = ffmpeg_info(FINAL_OUT)
    manifest = {
        "title": TITLE,
        "speaker": f"VOICEVOX speaker id {SPEAKER}",
        "voice_speed": VOICE_SPEED,
        "bgm": str(BGM),
        "bgm_volume": BGM_VOLUME,
        "frames": [str(path) for path in frame_paths],
        "narration": NARRATION,
        "durations_seconds": [round(value, 3) for value in durations],
        "total_seconds": round(sum(durations), 3),
        "voice_audio": str(voice_all),
        "asset_video": str(OUT),
        "final_video": str(FINAL_OUT),
        "ffmpeg_info": metadata,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(FINAL_OUT)
    print(f"total_seconds={sum(durations):.3f}")


if __name__ == "__main__":
    main()
