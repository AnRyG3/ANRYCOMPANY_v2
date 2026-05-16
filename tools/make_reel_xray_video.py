# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import math
import os
import subprocess
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BASE = Path(r"C:\Users\maruk\OneDrive\デスクトップ\Anry campany\01_ショート動画_リール_YouTubeShorts\放射線技師の安心ラボ\Reels\2026-05-13_レントゲン_検査前に外すもの")
FFMPEG = Path(r"C:\Users\maruk\OneDrive\デスクトップ\Anry campany\tools\ffmpeg\bin\ffmpeg.exe")
FONT_BOLD = r"C:\Windows\Fonts\BIZ-UDGothicB.ttc"
FONT_REG = r"C:\Windows\Fonts\BIZ-UDGothicR.ttc"
VOICEVOX = "http://127.0.0.1:50021"
SPEAKER = 8

W, H = 1080, 1920
NAVY = (18, 59, 93, 255)
BLUE = (87, 199, 232, 255)
YELLOW = (255, 216, 77, 255)
WHITE = (255, 255, 255, 255)
CYAN_DARK = (37, 92, 124, 255)


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size=size, index=0)


def fit_cover(img: Image.Image, size=(W, H), focus_x=0.5, focus_y=0.5) -> Image.Image:
    iw, ih = img.size
    tw, th = size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = int((nw - tw) * focus_x)
    top = int((nh - th) * focus_y)
    return resized.crop((left, top, left + tw, top + th))


def fit_contain(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    return img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)


def draw_centered(draw: ImageDraw.ImageDraw, text: str, y: int, fnt, fill=NAVY, stroke=4):
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    x = (W - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=WHITE)


def draw_pill(draw: ImageDraw.ImageDraw, text: str, y: int, fnt, fill=NAVY, bg=YELLOW, pad_x=26, pad_y=10):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) // 2
    draw.rounded_rectangle((x - pad_x, y - pad_y, x + tw + pad_x, y + th + pad_y + 10), radius=24, fill=bg)
    draw.text((x, y), text, font=fnt, fill=fill)


def shade_bottom(img: Image.Image, height=430) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(height):
        a = int(150 * (i / height) ** 1.8)
        d.line((0, H - height + i, W, H - height + i), fill=(0, 0, 0, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def base_from_image(path: Path, focus_x=0.5, focus_y=0.5) -> Image.Image:
    return fit_cover(Image.open(path).convert("RGB"), focus_x=focus_x, focus_y=focus_y).convert("RGBA")


def xray_portrait() -> Image.Image:
    src = Image.open(BASE / "real_xray_chest_necklace.jpg").convert("RGB")
    sw, sh = src.size
    crop_w = int(sh * 0.62)
    cx = int(sw * 0.52)
    left = max(0, min(sw - crop_w, cx - crop_w // 2))
    crop = src.crop((left, 0, left + crop_w, sh))
    bg = crop.resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(10))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (245, 250, 252)), 0.20).convert("RGBA")
    panel = crop.resize((1000, 1370), Image.Resampling.LANCZOS).convert("RGBA")
    px, py = 40, 285
    mask = Image.new("L", panel.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, panel.width, panel.height), radius=32, fill=255)
    shadow = Image.new("RGBA", (panel.width + 28, panel.height + 28), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((14, 14, panel.width + 14, panel.height + 14), radius=36, fill=(0, 0, 0, 75))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    bg.alpha_composite(shadow, (px - 14, py - 14))
    bg.paste(panel, (px, py), mask)
    return bg


def make_scene_01(out: Path):
    img = shade_bottom(base_from_image(BASE / "scene_01_hook_shippu.png", focus_y=0.45), 500)
    d = ImageDraw.Draw(img)
    draw_centered(d, "その湿布、", 102, font(82), fill=WHITE, stroke=5)
    draw_pill(d, "写ることがあります", 214, font(68))
    draw_centered(d, "え、湿布って写るの？", 1600, font(58), fill=WHITE, stroke=5)
    img.convert("RGB").save(out, quality=95)


def make_scene_02(out: Path):
    img = shade_bottom(base_from_image(BASE / "scene_02_checklist.png", focus_y=0.48), 500)
    d = ImageDraw.Draw(img)
    draw_centered(d, "撮影部位によっては", 82, font(62), fill=WHITE, stroke=5)
    draw_pill(d, "外すことがあります", 170, font(72))
    draw_centered(d, "湿布 / カイロ / 金属 / アクセ", 1600, font(48), fill=WHITE, stroke=5)
    img.convert("RGB").save(out, quality=95)


def make_scene_03(out: Path):
    img = Image.open(BASE / "scene_04_real_xray_telop.png").convert("RGB")
    fit_cover(img).save(out, quality=95)


def make_scene_04_quiz(out: Path):
    img = xray_portrait()
    d = ImageDraw.Draw(img)
    draw_centered(d, "懐炉はどこに", 78, font(68), fill=WHITE, stroke=5)
    draw_pill(d, "写ってる？", 172, font(84))
    d.rounded_rectangle((112, 1660, W - 112, 1805), radius=26, fill=(255, 255, 255, 238))
    draw_centered(d, "答えは最後で...", 1695, font(60), fill=NAVY, stroke=0)
    img.convert("RGB").save(out, quality=95)


def make_scene_05_safe(out: Path):
    img = shade_bottom(base_from_image(BASE / "scene_03_explanation.png", focus_y=0.48), 560)
    d = ImageDraw.Draw(img)
    draw_centered(d, "見たい患部に重なると", 88, font(60), fill=WHITE, stroke=5)
    draw_pill(d, "分かりにくくなることも", 178, font(62))
    draw_centered(d, "迷ったらスタッフへ聞いてOK", 1610, font(54), fill=WHITE, stroke=5)
    img.convert("RGB").save(out, quality=95)


def make_scene_06_answer(out: Path):
    img = xray_portrait()
    d = ImageDraw.Draw(img)
    # The warmer is the dense granular area over the viewer's right lower lung field.
    cx, cy, r = 800, 1035, 185
    for width, alpha in [(18, 255), (28, 90)]:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=YELLOW[:3] + (alpha,), width=width)
    d.line((cx - 260, cy - 260, cx - 90, cy - 95), fill=YELLOW, width=18)
    d.polygon([(cx - 100, cy - 100), (cx - 145, cy - 112), (cx - 112, cy - 145)], fill=YELLOW)
    draw_pill(d, "ここです", 126, font(92))
    img.convert("RGB").save(out, quality=95)


def voicevox_wav(text: str, out: Path):
    query_url = f"{VOICEVOX}/audio_query?{urllib.parse.urlencode({'text': text, 'speaker': SPEAKER})}"
    req = urllib.request.Request(query_url, method="POST")
    with urllib.request.urlopen(req, timeout=30) as res:
        query = json.loads(res.read().decode("utf-8"))
    query["speedScale"] = 1.08
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.1
    synth_url = f"{VOICEVOX}/synthesis?{urllib.parse.urlencode({'speaker': SPEAKER})}"
    data = json.dumps(query).encode("utf-8")
    req = urllib.request.Request(synth_url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as res:
        out.write_bytes(res.read())


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def make_silence(path: Path, duration: float, framerate=24000):
    frames = int(duration * framerate)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(b"\x00\x00" * frames)


def make_pon(path: Path, duration=0.18, framerate=24000):
    frames = int(duration * framerate)
    samples = bytearray()
    for i in range(frames):
        t = i / framerate
        env = math.exp(-18 * t)
        val = int(16000 * env * math.sin(2 * math.pi * 880 * t))
        samples += int(val).to_bytes(2, "little", signed=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(bytes(samples))


def make_bgm(path: Path, duration: float, mute_tail: float = 1.25, framerate=24000):
    frames = int(duration * framerate)
    samples = bytearray()
    cutoff = max(0.0, duration - mute_tail)
    # Light, unobtrusive loop: soft pulse plus two calm tones. It ducks under narration.
    for i in range(frames):
        t = i / framerate
        if t >= cutoff:
            amp = 0.0
        else:
            fade_in = min(1.0, t / 0.8)
            fade_out = min(1.0, max(0.0, (cutoff - t) / 0.45))
            pulse = 0.72 + 0.28 * math.sin(2 * math.pi * 1.7 * t)
            amp = 1050 * fade_in * fade_out * pulse
        tone = (
            0.52 * math.sin(2 * math.pi * 220 * t)
            + 0.35 * math.sin(2 * math.pi * 330 * t)
            + 0.18 * math.sin(2 * math.pi * 440 * t)
        )
        val = int(amp * tone)
        samples += int(val).to_bytes(2, "little", signed=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(bytes(samples))


def concat_wavs(paths: list[Path], out: Path):
    with wave.open(str(paths[0]), "rb") as first:
        params = first.getparams()
    with wave.open(str(out), "wb") as dst:
        dst.setparams(params)
        for p in paths:
            with wave.open(str(p), "rb") as src:
                dst.writeframes(src.readframes(src.getnframes()))


def main():
    work = BASE / "_video_work"
    work.mkdir(exist_ok=True)
    scenes = [
        ("scene_01.png", make_scene_01, "その湿布、レントゲンに写ることがあります。え、湿布って写るの？と思った人へ。", 5.0),
        ("scene_02.png", make_scene_02, "湿布、カイロ、金属、アクセサリーは、撮影部位によっては外すことがあります。", 4.0),
        ("scene_03.png", make_scene_03, "実際のレントゲンでは、ネックレスやジッパーもこんなに写ります。", 5.0),
        ("scene_04_quiz.png", make_scene_04_quiz, "では問題です。この画像の懐炉、どこに写っているでしょう？答えは最後に出します。先に大事なことだけ。", 8.0),
        ("scene_05_safe.png", make_scene_05_safe, "見たい患部に重なると、画像が分かりにくくなることがあります。迷ったときは、外す前にスタッフへ聞いてOKです。", 8.0),
        ("scene_06_answer.png", make_scene_06_answer, "ここです。", 1.2),
    ]

    image_paths = []
    audio_parts = []
    durations = []
    for idx, (name, maker, text, min_duration) in enumerate(scenes, start=1):
        img_path = work / name
        maker(img_path)
        image_paths.append(img_path)
        wav_path = work / f"voice_{idx:02d}.wav"
        voicevox_wav(text, wav_path)
        dur = wav_duration(wav_path)
        pad = max(0.18, min_duration - dur)
        silence = work / f"silence_{idx:02d}.wav"
        make_silence(silence, pad)
        audio_parts.extend([wav_path, silence])
        durations.append(dur + pad)

    pon = work / "pon.wav"
    make_pon(pon)
    audio_parts.append(pon)
    concat_wavs(audio_parts, BASE / "voice.wav")
    total_duration = wav_duration(BASE / "voice.wav")
    make_bgm(BASE / "bgm.wav", total_duration, mute_tail=1.25)

    concat_file = work / "concat.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for img_path, dur in zip(image_paths, durations):
            f.write(f"file '{img_path.as_posix()}'\n")
            f.write(f"duration {dur:.3f}\n")
        f.write(f"file '{image_paths[-1].as_posix()}'\n")

    out = BASE / "final.mp4"
    cmd = [
        str(FFMPEG),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-i",
        str(BASE / "voice.wav"),
        "-i",
        str(BASE / "bgm.wav"),
        "-vf",
        "scale=1080:1920,format=yuv420p",
        "-filter_complex",
        "[1:a][2:a]amix=inputs=2:duration=first:weights=1 0.45[aout]",
        "-map",
        "0:v",
        "-map",
        "[aout]",
        "-c:v",
        "libx264",
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-shortest",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    print(out)


if __name__ == "__main__":
    main()
