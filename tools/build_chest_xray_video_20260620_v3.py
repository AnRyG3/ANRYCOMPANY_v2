from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave

ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "chest_xray_series"
FRAME_DIR = ASSET_DIR / "text_frames_20260619_v2"
AUDIO_DIR = ASSET_DIR / "audio_20260620_v3"
WORK_DIR = ASSET_DIR / "_video_work_20260620_v3"
OUT_DIR = ASSET_DIR / "video_20260620_v3"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.20
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "healing_wind.mp3"

NARRATION = [
    "お腹が痛いのに、なぜ胸のレントゲンを撮るんだろう。そう思ったことはありませんか。",
    "説明がないと、不思議に感じるのは当然です。",
    "実は、ちゃんと理由があります。胸のレントゲンは、お腹の異常を見つけるヒントになることがあります。",
    "たとえば、消化管に穴があいたとき。空気がおなかの中に漏れて、横隔膜のしたにたまることがあります。",
    "その空気は、立った姿勢の胸部エックス線で、確認しやすい場合があります。",
    "また、手術前に胸を撮ることもあります。麻酔の前に、肺や心臓を確認するためです。",
    "念のためだけではなく、あなたの安全のために確認しています。",
    "胸のレントゲンでは、肺、心臓、横隔膜まわりを一度に確認できます。",
    "理由がわかると、ちゃんと診てもらっていると少し安心できますよね。",
    "検査には、一つひとつ理由があります。疑問に思ったときは、遠慮なく聞いてください。",
    "検査前の不安を、安心に変える情報を発信中です。",
    "あとで見返せるように、保存しておいてください。",
]


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
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def synthesize_voice(text, output):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.18
    output.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / float(audio.getframerate())


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    missing_frames = [
        str(FRAME_DIR / f"frame_{i:02d}_text.png")
        for i in range(1, 13)
        if not (FRAME_DIR / f"frame_{i:02d}_text.png").exists()
    ]
    if missing_frames:
        raise FileNotFoundError("\n".join(missing_frames))
    if not FFMPEG.exists():
        raise FileNotFoundError(str(FFMPEG))
    if not BGM.exists():
        raise FileNotFoundError(str(BGM))

    padded_segments = []
    frame_durations = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        pad_seconds = 0.45 if idx in {4, 5} else (0.28 if idx < 11 else 0.55)
        run([FFMPEG, "-y", "-i", voice, "-af", f"apad=pad_dur={pad_seconds}", "-ar", "44100", "-ac", "2", padded])
        padded_segments.append(padded)
        frame_durations.append(wav_duration(padded))

    concat_audio = WORK_DIR / "voice_segments.txt"
    concat_audio.write_text("".join(f"file '{path.as_posix()}'\n" for path in padded_segments), encoding="utf-8")
    voice_all = AUDIO_DIR / "voice_all.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_audio, "-c", "copy", voice_all])
    total_duration = wav_duration(voice_all)

    bgm_wav = AUDIO_DIR / "bgm.wav"
    fade_out_start = max(total_duration - 1.2, 0)
    run([
        FFMPEG,
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        BGM,
        "-t",
        f"{total_duration:.3f}",
        "-af",
        f"volume=0.16,afade=t=in:st=0:d=0.7,afade=t=out:st={fade_out_start:.3f}:d=1.2",
        "-ar",
        "44100",
        "-ac",
        "2",
        bgm_wav,
    ])

    mix = AUDIO_DIR / "voice_bgm_mix.wav"
    run([
        FFMPEG,
        "-y",
        "-i",
        voice_all,
        "-i",
        bgm_wav,
        "-filter_complex",
        "[0:a]volume=1.0[a0];[1:a]volume=0.45[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0",
        "-ar",
        "44100",
        "-ac",
        "2",
        mix,
    ])

    clips = []
    for idx, duration in enumerate(frame_durations, start=1):
        frame = FRAME_DIR / f"frame_{idx:02d}_text.png"
        clip = WORK_DIR / f"clip_{idx:02d}.mp4"
        run([
            FFMPEG,
            "-y",
            "-loop",
            "1",
            "-t",
            f"{duration:.3f}",
            "-i",
            frame,
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-r",
            "30",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            clip,
        ])
        clips.append(clip)

    concat_video = WORK_DIR / "clips.txt"
    concat_video.write_text("".join(f"file '{path.as_posix()}'\n" for path in clips), encoding="utf-8")
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_video, "-c", "copy", silent_video])

    final_video = OUT_DIR / "chest_xray_abdominal_pain_20260620_v3.mp4"
    run([
        FFMPEG,
        "-y",
        "-i",
        silent_video,
        "-i",
        mix,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        final_video,
    ])

    manifest = {
        "voice_engine": "VOICEVOX",
        "speaker": SPEAKER,
        "speed": SPEED,
        "bgm": str(BGM),
        "duration_sec": round(total_duration, 3),
        "frames": str(FRAME_DIR),
        "audio_mix": str(mix),
        "video": str(final_video),
        "narration": NARRATION,
        "frame_durations_sec": [round(value, 3) for value in frame_durations],
    }
    (OUT_DIR / "video_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(final_video)


if __name__ == "__main__":
    main()
