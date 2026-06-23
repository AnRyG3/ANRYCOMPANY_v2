from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave

ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "breath_hold_xray_series"
FRAME_DIR = ASSET_DIR / "text_frames"
AUDIO_DIR = ASSET_DIR / "audio"
WORK_DIR = ASSET_DIR / "_video_work"
OUT_DIR = ASSET_DIR / "video"
FINAL_DIR = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.20
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "healing_wind.mp3"

NARRATION = [
    "レントゲンの後、ちゃんと息を止められていたかな、と不安になったことはありませんか。",
    "大丈夫です。息を止めるタイミングに不安を感じるかたは、とても多いです。",
    "診療放射線技師は、画像がブレにくいタイミングを見ながら撮影しています。",
    "吸って、と声をかけるのは、肺を大きく広げて、奥まで見えやすくするためです。",
    "実は、患者さんの呼吸の動きも、ちゃんと見ています。",
    "止めにくそうな時は、声をかける長さやタイミングを調整することもあります。",
    "少しズレても、画像が大きくブレていなければ、問題ないことが多いです。",
    "うまく止めようと力むより、リラックスして合図に合わせるほうが、きれいに撮れます。",
    "ちゃんと見て撮ってくれている、とわかると、少し安心できますよね。",
    "次に検査を受ける時は、止めなきゃではなく、吸って合図に合わせるだけで大丈夫、と思ってみてください。",
    "検査前の不安を、安心に変える情報を発信中です。",
    "保存して、検査前に見返してください。",
]


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
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()


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
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    missing = [str(FRAME_DIR / f"frame_{i:02d}_text.png") for i in range(1, 13) if not (FRAME_DIR / f"frame_{i:02d}_text.png").exists()]
    if missing:
        raise FileNotFoundError("Missing frames:\n" + "\n".join(missing))
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
        pad_seconds = 0.35 if idx < 11 else 0.55
        run([FFMPEG, "-y", "-i", voice, "-af", f"apad=pad_dur={pad_seconds}", "-ar", "44100", "-ac", "2", padded])
        padded_segments.append(padded)
        frame_durations.append(wav_duration(padded))

    concat_audio = WORK_DIR / "voice_segments.txt"
    concat_audio.write_text("".join(f"file '{p.as_posix()}'\n" for p in padded_segments), encoding="utf-8")
    voice_all = AUDIO_DIR / "voice_all.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_audio, "-c", "copy", voice_all])
    total_duration = wav_duration(voice_all)

    bgm_wav = AUDIO_DIR / "bgm.wav"
    fade_out_start = max(total_duration - 1.2, 0)
    run([
        FFMPEG, "-y", "-stream_loop", "-1", "-i", BGM, "-t", f"{total_duration:.3f}",
        "-af", f"volume=0.16,afade=t=in:st=0:d=0.7,afade=t=out:st={fade_out_start:.3f}:d=1.2",
        "-ar", "44100", "-ac", "2", bgm_wav,
    ])

    mix = AUDIO_DIR / "voice_bgm_mix.wav"
    run([
        FFMPEG, "-y", "-i", voice_all, "-i", bgm_wav,
        "-filter_complex", "[0:a]volume=1.0[a0];[1:a]volume=0.45[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0",
        "-ar", "44100", "-ac", "2", mix,
    ])

    clips = []
    for idx, duration in enumerate(frame_durations, start=1):
        frame = FRAME_DIR / f"frame_{idx:02d}_text.png"
        clip = WORK_DIR / f"clip_{idx:02d}.mp4"
        run([
            FFMPEG, "-y", "-loop", "1", "-t", f"{duration:.3f}", "-i", frame,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-r", "30", "-an", "-c:v", "libx264", "-preset", "veryfast", clip,
        ])
        clips.append(clip)

    concat_video = WORK_DIR / "clips.txt"
    concat_video.write_text("".join(f"file '{p.as_posix()}';\n" for p in clips).replace(";", ""), encoding="utf-8")
    silent_video = WORK_DIR / "silent_video.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_video, "-c", "copy", silent_video])

    final_video = OUT_DIR / "naze_iki_wo_sutte_tomeru_no_20260620.mp4"
    run([
        FFMPEG, "-y", "-i", silent_video, "-i", mix,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final_video,
    ])

    final_copy = FINAL_DIR / "なぜ息を吸って止めるの.mp4"
    run([FFMPEG, "-y", "-i", final_video, "-c", "copy", final_copy])

    manifest = {
        "voice_engine": "VOICEVOX",
        "speaker": SPEAKER,
        "speed": SPEED,
        "bgm": str(BGM),
        "duration_sec": round(total_duration, 3),
        "frames": str(FRAME_DIR),
        "audio_mix": str(mix),
        "video": str(final_video),
        "final_copy": str(final_copy),
        "narration": NARRATION,
        "frame_durations_sec": [round(v, 3) for v in frame_durations],
    }
    (OUT_DIR / "video_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(final_video)
    print(final_copy)
    print(round(total_duration, 3))


if __name__ == "__main__":
    main()
