"""Build the approved 11-cut heart-size result reel with VOICEVOX."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image


ROOT = Path(r"F:\ANRYCAMPANY")
UNIT = ROOT / "reel_assets" / "chest_xray_series" / "heart_size_result_consult_20261026"
FRAME_DIR = UNIT / "telop_frames"
AUDIO_DIR = UNIT / "audio"
WORK_DIR = UNIT / "_video_work"
VIDEO_DIR = UNIT / "video"
OUT = VIDEO_DIR / "chest_xray_heart_size_result_20261026.mp4"
FINAL = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / "胸部レントゲンで心臓が大きいと言われたら_20261026.mp4"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER_ID = 20  # もち子さん・ノーマル
SPEED_SCALE = 1.15
FPS = 30
SCENE_PAUSE = 0.12
FINAL_BGM_TAIL = 1.0


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def run(parts: list[str | Path]) -> None:
    subprocess.run([str(part) for part in parts], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def post(path: str, params: dict, data: dict | None = None) -> bytes:
    url = VOICEVOX + path + "?" + urllib.parse.urlencode(params)
    body = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def approved_sources() -> dict[int, Path]:
    manifest = (UNIT / "production_manifest.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\|\s*(\d{2})\s*\|\s*`([^`]+)`\s*\|", manifest, re.M)
    assert len(rows) == 11
    result = {int(number): Path(path) for number, path in rows}
    assert sorted(result) == list(range(1, 12))
    assert len(set(result.values())) == 11
    return result


def approved_narration() -> dict[int, str]:
    plan = (UNIT / "image_plan.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\|\s*(\d{1,2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$", plan, re.M)
    result = {int(number): text for number, text, _ in rows if int(number) in range(1, 12)}
    assert sorted(result) == list(range(1, 12)), sorted(result)
    return result


def check_source_lock(sources: dict[int, Path]) -> list[Path]:
    qa = json.loads((FRAME_DIR / "telop_qa.json").read_text(encoding="utf-8"))
    assert len(qa) == 11
    frames = []
    for cut in range(1, 12):
        source = sources[cut]
        row = qa[cut - 1]
        frame = FRAME_DIR / f"frame_{cut:02d}_telop.png"
        assert row["cut"] == cut and Path(row["source"]).resolve() == source.resolve()
        assert Path(row["output"]).resolve() == frame.resolve()
        assert source.is_file() and digest(source) == row["source_sha256"]
        assert frame.is_file() and row["font_size"] == 60
        with Image.open(frame) as image:
            assert image.size == (941, 1672)
        frames.append(frame)
    assert sources[5].name == "frame_05_comparison_v7_941.png"
    assert qa[4]["position"] == "下中央"
    return frames


def check_speaker() -> None:
    with urllib.request.urlopen(VOICEVOX + "/speakers", timeout=10) as response:
        speakers = json.load(response)
    matches = [(speaker["name"], style["name"]) for speaker in speakers for style in speaker["styles"] if style["id"] == SPEAKER_ID]
    assert len(matches) == 1 and "もち子さん" in matches[0][0] and matches[0][1] == "ノーマル", matches


def synthesize(text: str, target: Path) -> dict:
    query = json.loads(post("/audio_query", {"text": text, "speaker": SPEAKER_ID}))
    query.update({
        "speedScale": SPEED_SCALE,
        "pitchScale": 0.0,
        "intonationScale": 1.06,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.08,
        "postPhonemeLength": 0.18,
    })
    target.write_bytes(post("/synthesis", {"speaker": SPEAKER_ID}, query))
    return query


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def write_concat(paths: list[Path], target: Path) -> None:
    target.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def main() -> None:
    sources = approved_sources()
    frames = check_source_lock(sources)
    narration = approved_narration()
    for required in (FFMPEG, BGM):
        assert required.is_file(), required
    assert not FINAL.exists(), f"Final output already exists: {FINAL}"
    check_speaker()
    for folder in (AUDIO_DIR, WORK_DIR, VIDEO_DIR, FINAL.parent):
        folder.mkdir(parents=True, exist_ok=True)

    scene_audio = []
    scene_video = []
    records = []
    for cut in range(1, 12):
        spoken = narration[cut]
        raw = AUDIO_DIR / f"voice_{cut:02d}.wav"
        query = synthesize(spoken, raw)
        voice_seconds = duration(raw)
        scene_frames = math.ceil((voice_seconds + SCENE_PAUSE) * FPS)
        if cut == 11:
            scene_frames += int(FINAL_BGM_TAIL * FPS)
        scene_seconds = scene_frames / FPS
        padded = WORK_DIR / f"voice_{cut:02d}_padded.wav"
        segment = WORK_DIR / f"scene_{cut:02d}.mp4"
        run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", raw,
             "-af", f"aresample=48000,apad,atrim=duration={scene_seconds:.6f}",
             "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", padded])
        run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS),
             "-i", frames[cut - 1], "-vf", "scale=1080:1920,format=yuv420p", "-frames:v", str(scene_frames),
             "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-tune", "stillimage", segment])
        scene_audio.append(padded)
        scene_video.append(segment)
        records.append({"cut": cut, "source": str(sources[cut]), "frame": str(frames[cut - 1]),
                        "narration": spoken, "voice": str(raw), "speedScale": query["speedScale"],
                        "voice_seconds": round(voice_seconds, 3), "scene_seconds": round(scene_seconds, 3),
                        "scene_frames": scene_frames})
        print(f"cut {cut:02d}: voice {voice_seconds:.2f}s, scene {scene_seconds:.2f}s", flush=True)

    voice_list = WORK_DIR / "voice_segments.txt"
    video_list = WORK_DIR / "video_segments.txt"
    write_concat(scene_audio, voice_list)
    write_concat(scene_video, video_list)
    voice_all = AUDIO_DIR / "voice_all.wav"
    video_silent = WORK_DIR / "video_silent.mp4"
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", voice_list,
         "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", video_list,
         "-c", "copy", video_silent])
    total = sum(row["scene_frames"] for row in records) / FPS
    bgm_fade_start = max(0.0, total - 1.0)
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", video_silent, "-i", voice_all,
         "-stream_loop", "-1", "-i", BGM,
         "-filter_complex", f"[1:a]volume=1.08[voice];[2:a]volume=-30dB,afade=t=out:st={bgm_fade_start:.3f}:d=1[bgm];"
                           "[voice][bgm]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{total:.6f}", "-movflags", "+faststart", OUT])
    shutil.copy2(OUT, FINAL)
    report = {"title": "胸部レントゲンで心臓が大きいと言われたら", "voice_engine": "VOICEVOX",
              "speaker": "もち子さん・ノーマル", "speaker_id": SPEAKER_ID, "speedScale": SPEED_SCALE,
              "additional_tempo_filter": False, "bgm": str(BGM), "bgm_volume": "-30dB",
              "final_visual_tail_seconds": FINAL_BGM_TAIL, "total_seconds": round(total, 3),
              "voice_all": str(voice_all), "asset_video": str(OUT), "final_video": str(FINAL), "cuts": records}
    (UNIT / "video_manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"TOTAL {total:.3f}s\nFINAL {FINAL}", flush=True)


if __name__ == "__main__":
    main()
