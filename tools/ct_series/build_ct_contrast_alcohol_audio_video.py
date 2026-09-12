from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "ct_series" / "ct_contrast_alcohol_v1"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "造影CTのあと、お酒は飲んでもいい？.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"


# VOICE_TEXT uses kana where it helps preserve the intended readings.  Every
# segment maps to exactly one telop frame; there is no artificial still-frame
# padding after a sentence.
SEGMENTS = [
    {
        "frame": "01_hook_convenience_store_telop.png",
        "display": "今日、造影CTだった。お酒、飲んでいい？",
        "voice": "今日、ぞうえいシーティーだったけど、お酒、飲んでいいのかな。",
    },
    {
        "frame": "02_hesitation_at_shelf_telop.png",
        "display": "検査のとき、聞きそびれた…",
        "voice": "検査のとき、聞きそびれた。",
    },
    {
        "frame": "03_check_instructions_telop.png",
        "display": "案内は医療機関で違うこともあります",
        "voice": "実は、医療機関によって、案内が違うこともあります。",
    },
    {
        "frame": "04_pour_water_telop.png",
        "display": "造影剤の多くは尿から出ていきます",
        "voice": "ぞうえい剤の多くは、時間とともに、にょうから出ていきます。",
    },
    {
        "frame": "05_choose_water_telop.png",
        "display": "水分制限がなければ 水やお茶で水分補給",
        "voice": "水分制限がなければ、水やお茶で、水分をとりましょう。",
    },
    {
        "frame": "06_water_not_alcohol_telop.png",
        "display": "お酒は 水分補給の代わりにはなりません",
        "voice": "お酒は、水分補給の代わりにはなりません。",
    },
    {
        "frame": "07_check_facility_guidance_telop.png",
        "display": "当日の飲酒を控えるよう 案内する施設もあります",
        "voice": "検査当日の飲酒を、控えるよう案内する施設もあります。",
    },
    {
        "frame": "08_follow_individual_guidance_telop.png",
        "display": "腎臓の病気・水分制限がある方は 個別の説明を優先",
        "voice": "腎臓の病気や、水分制限があるかたは、受けた説明を優先してください。",
    },
    {
        "frame": "09_call_facility_telop.png",
        "display": "迷ったら 受けた医療機関へ確認",
        "voice": "迷ったら、検査を受けた医療機関へ、確認しましょう。",
    },
    {
        "frame": "10_cta_home_telop.png",
        "display": "帰宅後に見返すなら 保存・フォロー",
        "voice": "ぞうえいシーティーを受けた日の帰宅後に、見返せるよう、保存とフォローをお願いします。",
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
            "pauseLengthScale": 0.45,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.04,
            "postPhonemeLength": 0.10,
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
        "".join(f"file '{path.as_posix()}'\n" for path in voice_paths), encoding="utf-8"
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
        "".join(f"file '{path.as_posix()}'\n" for path in video_segments), encoding="utf-8"
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
            f"[1:a]volume=1.45[voice];[2:a]volume={BGM_VOLUME}[bgm];"
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
                "title": "造影CTのあと、お酒は飲んでもいい？",
                "speaker": f"VOICEVOX speaker id {SPEAKER}",
                "voice_speed": VOICE_SPEED,
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
