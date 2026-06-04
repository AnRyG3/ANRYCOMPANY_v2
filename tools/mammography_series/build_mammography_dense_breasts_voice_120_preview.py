from pathlib import Path
import json
import subprocess
import urllib.parse
import urllib.request


ROOT = Path(r"F:\ANRYCAMPANY")
ASSET_DIR = ROOT / "reel_assets" / "mammography_series" / "03_dense_breasts"
AUDIO_DIR = ASSET_DIR / "audio_120_preview"
WORK_DIR = ASSET_DIR / "_voice_120_preview_work"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
OUT = ASSET_DIR / "高濃度乳房って何_音声比較_速度1.20.wav"

VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20

NARRATION = [
    "こうのうどにゅうぼうって、病気なの。",
    "言葉だけ見ると、不安になりますよね。",
    "こうのうどにゅうぼうは、乳腺の割合が多い状態です。",
    "病気ではなく、にゅうぼうの特徴のひとつです。",
    "マンモでは、乳腺も病変も白く写ることがあります。",
    "そのため、病変が見えにくい場合があります。",
    "必要に応じて、エコーなどを組み合わせます。",
    "結果で気になったら、医療機関へ相談してください。",
    "マンモグラフィー認定技師、監修済み。",
    "検査前の不安を、安心に変える情報を発信中。",
    "あとで見返せるように、保存してまた見よう。",
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
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def synthesize_voice(text, out):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": SPEAKER}))
    query["speedScale"] = 1.20
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    out.write_bytes(post_json("/synthesis", {"speaker": SPEAKER}, query))


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    segments = []
    for idx, text in enumerate(NARRATION, start=1):
        voice = AUDIO_DIR / f"voice_{idx:02d}.wav"
        padded = WORK_DIR / f"voice_{idx:02d}_padded.wav"
        synthesize_voice(text, voice)
        run([
            FFMPEG, "-y", "-i", voice, "-af", "apad=pad_dur=0.22",
            "-ar", "44100", "-ac", "2", padded,
        ])
        segments.append(padded)

    concat_file = WORK_DIR / "voice_segments.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for segment in segments:
            f.write(f"file '{segment.as_posix()}'\n")

    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", OUT])
    print(OUT)


if __name__ == "__main__":
    main()
