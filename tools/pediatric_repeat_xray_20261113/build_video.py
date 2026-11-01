"""Assemble the ten locked telop frames with the approved VOICEVOX narration."""

from __future__ import annotations

import json
import math
import subprocess
import wave
from pathlib import Path

from build_audio import NARRATION, SPEED_SCALE, UNIT, checked_frames


ROOT = Path(r"F:\ANRYCAMPANY")
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
AUDIO = UNIT / "audio"
WORK = UNIT / "_video_work"
VIDEO = UNIT / "video"
OUT = VIDEO / "子どものレントゲン_前にも撮ったのにまた_20261113.mp4"
FINAL = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタ完成形" / OUT.name
FPS = 30
SCENE_BREATH = 0.08
FINAL_BGM_TAIL = 1.0


def run(parts: list[str | Path]) -> None:
    result = subprocess.run(
        [str(part) for part in parts], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def concat_file(paths: list[Path], target: Path) -> None:
    target.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8"
    )


def main() -> None:
    frames = checked_frames()
    narration = json.loads((AUDIO / "narration_manifest.json").read_text(encoding="utf-8"))
    if len(frames) != 10 or len(narration) != 10:
        raise RuntimeError("The approved ten-cut sequence is incomplete")
    if not FFMPEG.is_file() or not BGM.is_file():
        raise FileNotFoundError("Required FFmpeg or BGM file is missing")
    WORK.mkdir(parents=True, exist_ok=True)
    VIDEO.mkdir(parents=True, exist_ok=True)
    scene_audio, scene_video, records = [], [], []
    for cut, (frame, row) in enumerate(zip(frames, narration), 1):
        voice = AUDIO / f"voice_{cut:02d}.wav"
        if row["cut"] != cut or Path(row["voice"]) != voice:
            raise RuntimeError(f"Voice file mismatch at cut {cut}")
        if row["narration"] != NARRATION[cut - 1] or row["speedScale"] != SPEED_SCALE:
            raise RuntimeError(f"Narration or voice speed mismatch at cut {cut}")
        if not voice.is_file():
            raise FileNotFoundError(voice)
        voice_seconds = duration(voice)
        frame_count = math.ceil((voice_seconds + SCENE_BREATH) * FPS)
        if cut == 10:
            frame_count += round(FINAL_BGM_TAIL * FPS)
        scene_seconds = frame_count / FPS
        padded = WORK / f"voice_{cut:02d}_padded.wav"
        scene = WORK / f"scene_{cut:02d}.mp4"
        run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", voice,
             "-af", f"aresample=48000,apad,atrim=duration={scene_seconds:.6f}",
             "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", padded])
        run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-loop", "1",
             "-framerate", str(FPS), "-i", frame, "-vf", "format=yuv420p",
             "-frames:v", str(frame_count), "-r", str(FPS), "-c:v", "libx264",
             "-preset", "veryfast", "-crf", "19", "-tune", "stillimage", scene])
        scene_audio.append(padded)
        scene_video.append(scene)
        records.append({
            "cut": cut,
            "frame": str(frame),
            "voice": str(voice),
            "voice_seconds": round(voice_seconds, 3),
            "scene_seconds": round(scene_seconds, 3),
            "scene_frames": frame_count,
        })
        print(f"cut {cut:02d}: voice={voice_seconds:.2f}s scene={scene_seconds:.2f}s", flush=True)

    voice_list = WORK / "voice_segments.txt"
    video_list = WORK / "video_segments.txt"
    concat_file(scene_audio, voice_list)
    concat_file(scene_video, video_list)
    voice_all = AUDIO / "voice_all.wav"
    video_silent = WORK / "video_silent.mp4"
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", voice_list, "-c", "copy", voice_all])
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", video_list, "-c", "copy", video_silent])
    total = sum(row["scene_frames"] for row in records) / FPS
    fade_start = max(0, total - 1.0)
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", video_silent,
         "-i", voice_all, "-stream_loop", "-1", "-i", BGM,
         "-filter_complex",
         f"[1:a]volume=1.0[voice];[2:a]volume=-34dB,afade=t=out:st={fade_start:.3f}:d=1[bgm];"
         "[voice][bgm]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{total:.6f}", "-movflags", "+faststart", OUT])
    report = {
        "title": "子どものレントゲン、前にも撮ったのにまた撮るのはなぜ？",
        "speaker": "もち子さん・ノーマル",
        "speaker_id": 20,
        "speedScale": SPEED_SCALE,
        "additional_tempo_filter": False,
        "bgm": str(BGM),
        "bgm_volume": "-34dB",
        "final_bgm_tail_seconds": FINAL_BGM_TAIL,
        "total_seconds": round(total, 3),
        "voice_all": str(voice_all),
        "video": str(OUT),
        "final_video": str(FINAL),
        "cuts": records,
    }
    (UNIT / "video_manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"TOTAL {total:.3f}s\nVIDEO {OUT}", flush=True)


if __name__ == "__main__":
    main()
