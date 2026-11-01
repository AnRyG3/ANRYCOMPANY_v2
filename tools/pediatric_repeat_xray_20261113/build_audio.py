"""Generate the approved ten-cut narration with VOICEVOX Mochiko-san."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "pediatric_repeat_xray_20261113"
FRAMES = UNIT / "telop_frames"
OUT = UNIT / "audio"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER_ID = 20  # もち子さん・ノーマル。APIの/speakersで実行時に検証する。
SPEED_SCALE = 1.15  # ユーザー指定。動画側では追加の倍速処理をしない。

NARRATION = [
    "子どものレントゲン、また撮るの？ そう思ったら、今回の目的を医師に聞いて大丈夫です。",
    "また撮ると聞いて、心配になるのは自然なことです。",
    "レントゲンは、診断のため、または経過を見るために行われます。",
    "前回と今回で、撮る目的が違うことがあります。",
    "撮るかどうかは、診察した医師が必要性を見て決めます。",
    "前に撮ったことがあれば、覚えている範囲で医師に伝えてください。",
    "撮影条件は、診断に使える画質を保ちながら、子どもの体の大きさに合わせて調整します。",
    "心配な気持ちも、医師に伝えて大丈夫です。今回の目的を聞いてみてください。",
    "たとえば、こう聞いてみてください。前にも撮りましたが、今回は何のための撮影ですか。",
    "次の診察で見返せるよう、この言葉を保存しておいてください。",
]


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def checked_frames() -> list[Path]:
    rows = re.findall(
        r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|",
        (UNIT / "production_manifest.md").read_text(encoding="utf-8"),
        re.M,
    )
    qa = json.loads((FRAMES / "qa_report.json").read_text(encoding="utf-8"))
    if len(rows) != 10 or len(qa) != 10 or len(NARRATION) != 10:
        raise RuntimeError("Source, telop and narration counts must all be 10")
    result = []
    for cut, ((number, name), record) in enumerate(zip(rows, qa), 1):
        source = Path(name)
        frame = FRAMES / f"telop_{cut:02d}.png"
        if int(number) != cut or source != Path(record["source"]):
            raise RuntimeError(f"Source order mismatch at cut {cut}")
        if not source.is_file() or digest(source) != record["source_sha256"]:
            raise RuntimeError(f"Approved source image changed at cut {cut}")
        if frame != Path(record["output"]) or not frame.is_file():
            raise RuntimeError(f"Telop frame mismatch at cut {cut}")
        with Image.open(frame) as image:
            if image.size != (1080, 1920):
                raise RuntimeError(f"Wrong frame dimensions at cut {cut}")
        result.append(frame)
    return result


def post(path: str, params: dict, data: dict | None = None) -> bytes:
    url = VOICEVOX + path + "?" + urllib.parse.urlencode(params)
    body = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def main() -> None:
    checked_frames()
    with urllib.request.urlopen(VOICEVOX + "/speakers", timeout=10) as response:
        speakers = json.load(response)
    matches = [
        (speaker["name"], style["name"])
        for speaker in speakers
        for style in speaker["styles"]
        if style["id"] == SPEAKER_ID
    ]
    if len(matches) != 1 or "もち子さん" not in matches[0][0] or matches[0][1] != "ノーマル":
        raise RuntimeError(f"Speaker 20 is not Mochiko-san Normal: {matches!r}")

    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for cut, spoken in enumerate(NARRATION, 1):
        query = json.loads(post("/audio_query", {"text": spoken, "speaker": SPEAKER_ID}))
        query.update({
            "speedScale": SPEED_SCALE,
            "pitchScale": 0.0,
            "intonationScale": 1.06,
            "volumeScale": 1.0,
            "prePhonemeLength": 0.08,
            "postPhonemeLength": 0.16,
        })
        path = OUT / f"voice_{cut:02d}.wav"
        path.write_bytes(post("/synthesis", {"speaker": SPEAKER_ID}, query))
        (OUT / f"query_{cut:02d}.json").write_text(
            json.dumps(query, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        with wave.open(str(path), "rb") as audio:
            duration = audio.getnframes() / audio.getframerate()
            sample_rate = audio.getframerate()
        records.append({
            "cut": cut,
            "narration": spoken,
            "voice": str(path),
            "seconds": round(duration, 3),
            "sample_rate": sample_rate,
            "speaker": "もち子さん・ノーマル",
            "speaker_id": SPEAKER_ID,
            "speedScale": query["speedScale"],
            "intonationScale": query["intonationScale"],
        })
        print(f"cut {cut:02d}: {duration:.2f}s", flush=True)
    (OUT / "narration_manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"TOTAL RAW VOICE {sum(row['seconds'] for row in records):.2f}s", flush=True)


if __name__ == "__main__":
    main()
