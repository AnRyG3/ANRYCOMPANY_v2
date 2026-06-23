from pathlib import Path
from PIL import Image, ImageDraw

folder = Path(r"F:\ANRYCAMPANY\reel_assets\chest_xray_series\text_frames_20260619_v2")
files = sorted(folder.glob("frame_*_text.png"))
print(len(files))
for path in files:
    with Image.open(path) as image:
        print(path.name, image.size)

thumb_w, thumb_h = 270, 480
sheet = Image.new("RGB", (thumb_w * 4, thumb_h * 3), (245, 245, 245))
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(files):
    with Image.open(path) as image:
        thumb = image.resize((thumb_w, thumb_h))
    x = (index % 4) * thumb_w
    y = (index // 4) * thumb_h
    sheet.paste(thumb, (x, y))
    draw.text((x + 8, y + 8), path.name, fill=(0, 0, 0))

sheet.save(folder / "contact_sheet_text_frames_v2.jpg", quality=90)
