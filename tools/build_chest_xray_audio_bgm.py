from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request
import wave

ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "chest_xray_series" / "01_what_it_shows"
AUDIO_DIR = ASSET_DIR / "audio_v1"
WORK_DIR = ASSET_DIR / "_audio_work_v1"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.20

BGM_SRC = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "healing_wind.mp3"

NARRATION = [
    "レントゲン、何か見つかったら、どうしよう。",
    "検査室に入るとき、そう思ったことはありませんか？",
    "その不安、おかしくないです。",
    "胸のレントゲンは、主に三つを見ています。肺、心臓、骨です。",
    "肺では、影や白く見える部分がないかを確認します。",
    "心臓では、大きさや形を確認します。",
    "骨では、肋骨や背骨の状態も確認できます。",
    "一枚の写真から、多くの情報を確認できます。",
    "何を見てもらっているか、わかると、少し気持ちが楽になります。",
    "異常が見つかることが怖いのは当然です。",
    "でも、見つけるための検査だから、受けてよかったと思える日が来ます。",
    "あとで見返せるように、保存しておいてください。",
]


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def post_json(path, params=None, payload=None):
    query = urllib.parse.urlencode(params or {})
    url = f"{VOICEVOX}{path}"
    if query:
        url += f"?{query}"
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def synthesize_voice(text, out):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = SPEED
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.16
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def wav_duration(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    segments = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        run([FFMPEG, "-y", "-i", voice, "-af", "apad=pad_dur=0.18", "-ar", "44100", "-ac", "2", padded])
        segments.append(padded)

    concat_file = WORK_DIR / "voice_segments.txt"
    concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments), encoding="utf-8")
    voice_out = AUDIO_DIR / "voice.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", voice_out])

    duration = wav_duration(voice_out)
    bgm_out = AUDIO_DIR / "bgm.wav"
    run([
        FFMPEG, "-y", "-stream_loop", "-1", "-i", BGM_SRC, "-t", f"{duration:.3f}",
        "-af", "volume=0.18,afade=t=in:st=0:d=0.8,afade=t=out:st={:.3f}:d=1.2".format(max(duration - 1.2, 0)),
        "-ar", "44100", "-ac", "2", bgm_out,
    ])

    mix_out = AUDIO_DIR / "voice_bgm_mix.wav"
    run([
        FFMPEG, "-y", "-i", voice_out, "-i", bgm_out,
        "-filter_complex", "[0:a]volume=1.0[a0];[1:a]volume=0.55[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0",
        "-ar", "44100", "-ac", "2", mix_out,
    ])

    manifest = {
        "speaker": SPEAKER,
        "speed": SPEED,
        "bgm": str(BGM_SRC),
        "duration_sec": round(duration, 3),
        "narration": NARRATION,
        "files": {
            "voice": str(voice_out),
            "bgm": str(bgm_out),
            "mix": str(mix_out),
        },
    }
    (AUDIO_DIR / "audio_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(AUDIO_DIR)


if __name__ == "__main__":
    main()
