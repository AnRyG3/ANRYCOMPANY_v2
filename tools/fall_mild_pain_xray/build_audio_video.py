from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "fall_mild_pain_xray_20260730"
FRAME_DIR = ASSET_DIR / "telop_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
MANIFEST = ASSET_DIR / "video_manifest.json"

FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
OUT = ASSET_DIR / "高齢者が転んだあと_痛みが軽くても検査する理由.mp4"
FINAL_OUT = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "telop_01_home_after_fall.png",
    "telop_02_xray_explanation.png",
    "telop_03_reassurance.png",
    "telop_04_xray_review_hands.png",
    "telop_05_xray_room.png",
    "telop_06_rt_explains_monitor.png",
    "telop_07_exam_table_guidance.png",
    "telop_08_hesitation_corridor.png",
    "telop_09_reassuring_closing.png",
    "telop_10_save_cta_bg.png",
    "telop_11_follow_cta_bg.png",
]

DISPLAY_NARRATION = [
    "転んだあと、痛みが軽い。検査はいらない？",
    "病院に行くほどでもないと思うと、検査を受けるのをためらってしまう。",
    "その気持ち、おかしくありません。",
    "実は、骨に異常があっても、痛みが軽く感じられることがあります。",
    "特に高齢の方は、痛みの感じ方に個人差があり、強く痛まないこともあります。",
    "痛みの強さと、骨折の有無は、必ずしも一致しません。",
    "転んだ後は、痛みが軽くても、一度確認しておくことが大切です。",
    "それでも、大げさにしたくないと、検査を先延ばしにしたくなる。",
    "大げさではありません。早めの確認が、その後の安心につながります。",
    "本人や家族が不安なときに見返せるよう、保存しておいてください。",
    "検査のこと、これからも一緒に考えていきます。フォローして次の投稿も見てください。",
]

VOICE_TEXT = [
    "転んだあと、痛みが軽い。検査はいらない。",
    "病院に行くほどでもないと思うと、検査を受けるのをためらってしまう。",
    "その気持ち、おかしくありません。",
    "実は、骨に異常があっても、痛みが軽く感じられることがあります。",
    "特に高齢のかたは、痛みの感じ方に個人差があり、強く痛まないこともあります。",
    "痛みの強さと、骨折の有無は、必ずしも一致しません。",
    "転んだ後は、痛みが軽くても、一度確認しておくことが大切です。",
    "それでも、大げさにしたくないと、検査を先延ばしにしたくなる。",
    "大げさではありません。早めの確認が、その後の安心につながります。",
    "本人や家族が不安なときに見返せるよう、保存しておいてください。",
    "検査のこと、これからも一緒に考えていきます。フォローして次の投稿も見てください。",
]

MIN_DURATIONS = [3.2, 4.8, 2.6, 4.2, 5.0, 4.4, 4.8, 4.2, 4.8, 4.6, 5.2]


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
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / frame for frame in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for index, text in enumerate(VOICE_TEXT, start=1):
        voice = AUDIO_DIR / f"voice_{index:02d}.wav"
        padded = WORK_DIR / f"voice_{index:02d}_padded.wav"
        synthesize_voice(text, voice)
        duration = max(MIN_DURATIONS[index - 1], wav_duration(voice) + 0.35)
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
    frames_txt.write_text(
        "".join(
            f"file '{frame.as_posix()}'\nduration {duration:.3f}\n"
            for frame, duration in zip(frame_paths, durations)
        )
        + f"file '{frame_paths[-1].as_posix()}'\n",
        encoding="utf-8",
    )

    voice_txt = WORK_DIR / "voice_segments.txt"
    voice_txt.write_text("".join(f"file '{wav.as_posix()}'\n" for wav in padded_wavs), encoding="utf-8")

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
            "-tune",
            "stillimage",
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
        "title": "高齢者が転んだあと、痛みが軽くても検査する理由",
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
