from __future__ import annotations

import json
import re
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path


ROOT = Path(r"F:\ANRYCAMPANY")
IMAGE_DIR = ROOT / "reel_assets" / "bone_density_series" / "artificial_hip_dxa_20261006_images"
TELOP_DIR = ROOT / "reel_assets" / "bone_density_series" / "artificial_hip_dxa_20261006_telop_frames"
UNIT_DIR = ROOT / "reel_assets" / "bone_density_series" / "artificial_hip_dxa_20261006_video"
AUDIO_DIR = UNIT_DIR / "audio"
WORK_DIR = UNIT_DIR / "_work"
VIDEO_DIR = UNIT_DIR / "video"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
BGM = ROOT / "01_ショート動画_リール_YouTubeShorts" / "インスタリール用" / "BGM フリー素材" / "Kind_Heart.mp3"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 20
SPEED = 1.2
FINAL_BGM_TAIL = 1.0
OUTPUT = VIDEO_DIR / "人工股関節と骨密度検査_20261006.mp4"

# Voice-only readings follow voice-rules.md. Each item maps one-to-one to a telop frame.
VOICE_TEXT = [
    "人工股関節があっても、こつみつど検査は受けられます。",
    "デキサでは、ようついと、こかんせつを測定します。",
    "人工股関節が入った側は、通常の評価には使いません。",
    "片側だけなら、反対側を測定します。",
    "両側に入っている場合、股関節のこつみつどは測れません。",
    "検査前に、人工股関節があることと左右を、診療放射線技師に伝えてください。",
    "検査前に見返せるよう、保存しておいてください。",
]


def run(command: list[Path | str]) -> None:
    subprocess.run([str(part) for part in command], check=True)


def post(path: str, params: dict | None = None, payload: dict | None = None) -> bytes:
    query = urllib.parse.urlencode(params or {})
    request = urllib.request.Request(
        VOICEVOX + path + ("?" + query if query else ""),
        data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def synthesize(text: str, output: Path) -> None:
    query = json.loads(post("/audio_query", {"text": text, "speaker": SPEAKER}))
    query.update(
        {
            "speedScale": SPEED,
            "pitchScale": 0,
            "intonationScale": 0.95,
            "prePhonemeLength": 0,
            "postPhonemeLength": 0,
            "pauseLengthScale": 0.9,
        }
    )
    output.write_bytes(post("/synthesis", {"speaker": SPEAKER}, query))


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def write_concat_list(paths: list[Path], output: Path) -> None:
    output.write_text("".join(f"file '{path.as_posix()}'\n" for path in paths), encoding="utf-8")


def validate_source_lock() -> tuple[list[Path], list[Path]]:
    image_manifest = (IMAGE_DIR / "production_manifest.md").read_text(encoding="utf-8")
    approved_images_section = image_manifest.split("## Character Clothing Lock", maxsplit=1)[0]
    locked_images = [
        Path(path) for path in re.findall(r"`([A-Za-z]:\\[^`]+\\[^`]+\.png)`", approved_images_section)
    ]
    telop_manifest = json.loads((TELOP_DIR / "telop_manifest.json").read_text(encoding="utf-8"))
    telops = [Path(path) for path in telop_manifest["telop_frames"]]
    if len(locked_images) != 7 or len(telops) != 7:
        raise RuntimeError("Expected seven locked images and seven telop frames.")
    if not all(path.exists() for path in locked_images + telops):
        raise RuntimeError("A locked image or telop frame is missing.")
    expected_telop_names = [f"telop_{number:02d}.png" for number in range(1, 8)]
    if [path.name for path in telops] != expected_telop_names:
        raise RuntimeError("Telop frames are not in cut order.")
    return locked_images, telops


def main() -> None:
    if not FFMPEG.exists() or not BGM.exists():
        raise FileNotFoundError("ffmpeg or BGM file is missing")
    locked_images, telops = validate_source_lock()
    for directory in (AUDIO_DIR, WORK_DIR, VIDEO_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    wavs: list[Path] = []
    durations: list[float] = []
    for number, text in enumerate(VOICE_TEXT, start=1):
        wav = AUDIO_DIR / f"voice_{number:02d}.wav"
        synthesize(text, wav)
        wavs.append(wav)
        durations.append(duration(wav))

    # No artificial silence is inserted between spoken cuts. The final visual retains BGM only.
    voice_list = WORK_DIR / "voice_concat.txt"
    write_concat_list(wavs, voice_list)
    narration = AUDIO_DIR / "narration_full.wav"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", voice_list, "-c:a", "pcm_s16le", narration])

    segments: list[Path] = []
    cut_durations = durations[:-1] + [durations[-1] + FINAL_BGM_TAIL]
    for number, (telop, cut_duration) in enumerate(zip(telops, cut_durations), start=1):
        segment = WORK_DIR / f"segment_{number:02d}.mp4"
        run(
            [
                FFMPEG,
                "-y",
                "-loop",
                "1",
                "-t",
                f"{cut_duration:.3f}",
                "-i",
                telop,
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
                segment,
            ]
        )
        segments.append(segment)

    video_list = WORK_DIR / "video_concat.txt"
    write_concat_list(segments, video_list)
    visual = WORK_DIR / "visual.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", video_list, "-c", "copy", visual])

    total_duration = sum(cut_durations)
    fade_start = max(0, total_duration - 0.7)
    audio_filter = (
        f"[1:a]volume=1.45[v];"
        f"[2:a]volume=-27dB,atrim=duration={total_duration:.3f},"
        f"afade=t=out:st={fade_start:.3f}:d=0.7[b];"
        "[v][b]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[a]"
    )
    run(
        [
            FFMPEG,
            "-y",
            "-i",
            visual,
            "-i",
            narration,
            "-stream_loop",
            "-1",
            "-i",
            BGM,
            "-filter_complex",
            audio_filter,
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
            OUTPUT,
        ]
    )

    manifest = {
        "source_images": [str(path) for path in locked_images],
        "telop_frames": [str(path) for path in telops],
        "voice_text": VOICE_TEXT,
        "voice_speed": SPEED,
        "voice_durations_seconds": durations,
        "cut_durations_seconds": cut_durations,
        "pacing": "No added silent gaps between cuts; final visual has a 1.0-second BGM-only tail.",
        "video": str(OUTPUT),
    }
    (VIDEO_DIR / "video_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
