from pathlib import Path
import json
import urllib.parse
import urllib.request


ROOT = Path(r"F:\ANRYCAMPANY")
OUT_DIR = ROOT / "reel_assets" / "result_wait_series" / "05_scan_choice" / "voice_samples"
VOICEVOX = "http://127.0.0.1:50021"

TEXT = (
    "再検査と言われたら、次はどの検査？ "
    "シーティー？ エムアールアイ？ エコー？ 不安になりますよね。 "
    "でも、悪い結果だから、とは限りません。 "
    "医師が、一番見やすい方法を、選んでいます。"
)

SPEAKERS = [
    ("もち子さん", 20),
    ("小夜_SAYO", 46),
    ("あんこもん", 113),
    ("東北イタコ", 109),
    ("東北きりたん", 108),
]


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


def synthesize(text, speaker_id, out):
    query = json.loads(post_json("/audio_query", {"text": text, "speaker": speaker_id}))
    query["speedScale"] = 1.10
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = 0.08
    query["postPhonemeLength"] = 0.14
    out.write_bytes(post_json("/synthesis", {"speaker": speaker_id}, query))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for label, speaker_id in SPEAKERS:
        out = OUT_DIR / f"{speaker_id:03d}_{label}.wav"
        synthesize(TEXT, speaker_id, out)
        files.append({"speaker": label, "style_id": speaker_id, "file": str(out)})
        print(out)
    (OUT_DIR / "manifest.json").write_text(
        json.dumps({"text": TEXT, "samples": files}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
