from pathlib import Path
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "fracture_xray_ct_mri_series"
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

OUT = VIDEO_DIR / "骨折の診断_レントゲンだけじゃダメなの.mp4"
FINAL_OUT = FINAL_DIR / "骨折の診断_レントゲンだけじゃダメなの.mp4"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
VOICE_SPEED = 1.2
BGM_VOLUME = "-25dB"

FRAMES = [
    "slide01_telop.png",
    "slide02_telop.png",
    "slide03_telop.png",
    "slide04_telop.png",
    "slide05_telop.png",
    "slide06_telop.png",
    "slide07_telop.png",
    "slide08_telop.png",
    "slide09_telop.png",
    "slide10_telop.png",
    "slide11_telop.png",
    "slide12_telop.png",
]

DISPLAY_NARRATION = [
    "レントゲンを撮ったのに、まだCTやMRIも必要なんですか。そう聞かれることがあります。",
    "レントゲンで骨折はわかるはずなのに、なぜ。と不思議に思われる方も多いです。",
    "レントゲンは骨の状態を知る、最初の大切な検査です。",
    "ただ、骨折には、レントゲンだけではっきり写らないケースもあります。",
    "反対側と比べても判断が難しい、ごく小さなヒビや、骨の重なりが多い部分の骨折などです。",
    "そういった場合、骨の形や骨折の状態を詳しく確認するため、CTを選ぶことがあります。",
    "一方、骨折が疑われる部位や状況によっては、レントゲンの次にMRIで骨の内部の変化を確認することもあります。",
    "そんなに何段階もあるんですね。と驚かれることもあります。",
    "検査が増えると、不安に感じることもあると思います。",
    "それは、見逃しを減らし、より正確な診断につなげるための、慎重な確認作業なんです。",
    "そういう流れだったんだ。と思った方は、スマートフォンに保存しておいてください。",
    "診療放射線技師の発信、フォローで応援お願いします。",
]

VOICEVOX_TEXT = [
    "レントゲンを撮ったのに、まだシーティーやエムアールアイも必要なんですか。そう聞かれることがあります。",
    "レントゲンで骨折はわかるはずなのに、なぜ。と不思議に思われるかたも多いです。",
    "レントゲンは骨の状態を知る、最初の大切な検査です。",
    "ただ、骨折には、レントゲンだけではっきり写らないケースもあります。",
    "反対側と比べても判断が難しい、ごく小さなヒビや、骨のかさなりが多い部分の骨折などです。",
    "そういった場合、骨の形や骨折の状態を詳しく確認するため、シーティーを選ぶことがあります。",
    "一方、骨折が疑われる部位や状況によっては、レントゲンの次にエムアールアイで骨の内部の変化を確認することもあります。",
    "そんなに何段階もあるんですね。と驚かれることもあります。",
    "検査が増えると、不安に感じることもあると思います。",
    "それは、見逃しを減らし、より正確な診断につなげるための、慎重な確認作業なんです。",
    "そういう流れだったんだ。と思ったかたは、スマートフォンに保存しておいてください。",
    "診療放射線技師の発信、フォローで応援お願いします。",
]

MIN_DURATIONS = [4.7, 4.6, 3.7, 4.1, 5.3, 5.0, 6.6, 4.0, 4.2, 6.2, 5.0, 4.0]


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def post_json(path, params=None, payload=None):
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize_voice(text, out):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = VOICE_SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 0.95
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    frame_paths = [FRAME_DIR / name for name in FRAMES]
    for required in [FFMPEG, BGM, *frame_paths]:
        if not required.exists():
            raise FileNotFoundError(required)

    padded_wavs = []
    durations = []
    for index, text in enumerate(VOICEVOX_TEXT, start=1):
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

    frames_txt = WORK_DIR / "frames.txt"
    with frames_txt.open("w", encoding="utf-8") as file:
        for frame, duration in zip(frame_paths, durations):
            file.write(f"file '{frame.as_posix()}'\n")
            file.write(f"duration {duration:.3f}\n")
        file.write(f"file '{frame_paths[-1].as_posix()}'\n")

    voice_txt = WORK_DIR / "voice_segments.txt"
    with voice_txt.open("w", encoding="utf-8") as file:
        for wav in padded_wavs:
            file.write(f"file '{wav.as_posix()}'\n")

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
        "title": "骨折の診断、レントゲンだけじゃダメなの？",
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
