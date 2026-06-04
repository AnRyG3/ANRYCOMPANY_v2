import build_keigo_work_stamps as builder
from PIL import Image, ImageDraw, ImageFont


builder.OUT_DIR = (
    builder.ROOT
    / "02_LINEスタンプ"
    / "あんりぃ_LINEスタンプ制作工場"
    / "04_完成画像"
    / "敬語・仕事返信スタンプ_あんりぃ40"
    / "02_本制作40個"
)

FRONT = "03_real_base_front_sit_necklace.png"
SOFT = "04_real_base_threequarter_tongue_necklace.png"
STAND = "05_real_base_standing_plain.png"
APOLOGY = "06_real_base_front_sit_apology_necklace.png"
POSE_OHAYOU = "pose:01_ohayou_transparent.png"
POSE_OTSUKARE = "pose:02_otsukaresama_transparent.png"
POSE_ARIGATOU = "pose:03_arigatou_transparent.png"
POSE_RYOUKAI = "pose:04_ryoukai_transparent.png"
POSE_YOROSHIKU = "pose:05_yoroshiku_transparent.png"
POSE_OYASUMI = "pose:06_oyasumi_transparent.png"
POSE_GOMENNE = "pose:07_gomenne_transparent.png"
POSE_HAAI = "pose:08_haai_transparent.png"
POSE_OK = "pose:09_ok_transparent.png"
POSE_UNUN = "pose:10_unun_transparent.png"
POSE_SORENA = "pose:11_sorena_transparent.png"
POSE_WAKARU = "pose:12_wakaru_transparent.png"
POSE_TASHIKANI = "pose:13_tashikani_transparent.png"
POSE_IINE = "pose:14_iine_transparent.png"
POSE_SUGOI = "pose:15_sugoi_transparent.png"
POSE_KAWAII = "pose:16_kawaii_transparent.png"
POSE_TASUKARU = "pose:17_tasukaru_transparent.png"
POSE_ARIGATOO = "pose:18_arigatoo_transparent.png"
POSE_ITSUMO = "pose:19_itsumo_arigatou_transparent.png"
POSE_MURISHINAI = "pose:20_murishinaidene_transparent.png"

NAVY = (42, 91, 150, 255)
GREEN = (47, 120, 92, 255)
BROWN = (121, 82, 65, 255)
PURPLE = (117, 82, 119, 255)
BLUE = (50, 99, 153, 255)

builder.STAMPS = [
    ("01", "おつかれ\nさまです", POSE_OTSUKARE, NAVY, "soft"),
    ("02", "ありがとう\nございます", POSE_ARIGATOU, GREEN, "sparkle"),
    ("03", "承知しました", POSE_RYOUKAI, NAVY, "check"),
    ("04", "了解です", POSE_HAAI, BLUE, "check"),
    ("05", "よろしく\nお願いします", POSE_YOROSHIKU, BROWN, "soft"),
    ("06", "確認します", POSE_OK, GREEN, "document"),
    ("07", "少々お待ち\nください", FRONT, BLUE, "clock"),
    ("08", "助かります", POSE_TASUKARU, GREEN, "sparkle"),
    ("09", "おはよう\nございます", POSE_OHAYOU, NAVY, "soft"),
    ("10", "お先に\n失礼します", POSE_IINE, BROWN, "soft"),
    ("11", "お願いします", POSE_YOROSHIKU, BROWN, "soft"),
    ("12", "かしこまり\nました", POSE_RYOUKAI, NAVY, "check"),
    ("13", "問題\nありません", POSE_OK, GREEN, "check"),
    ("14", "大丈夫です", POSE_UNUN, GREEN, "soft"),
    ("15", "対応します", POSE_HAAI, NAVY, "check"),
    ("16", "確認しました", POSE_OK, GREEN, "check"),
    ("17", "共有します", POSE_RYOUKAI, GREEN, "document"),
    ("18", "送付します", POSE_HAAI, BLUE, "document"),
    ("19", "受け取り\nました", POSE_ARIGATOU, GREEN, "check"),
    ("20", "後ほど\n連絡します", FRONT, BLUE, "clock"),
    ("21", "返信遅れます", APOLOGY, PURPLE, "sweat"),
    ("22", "遅れます", APOLOGY, PURPLE, "sweat"),
    ("23", "到着しました", POSE_HAAI, GREEN, "check"),
    ("24", "向かって\nいます", POSE_RYOUKAI, BLUE, "soft"),
    ("25", "休憩します", POSE_OYASUMI, GREEN, "soft"),
    ("26", "離席します", POSE_IINE, BLUE, "soft"),
    ("27", "戻りました", POSE_HAAI, GREEN, "soft"),
    ("28", "お休みします", APOLOGY, PURPLE, "soft"),
    ("29", "申し訳\nありません", APOLOGY, PURPLE, "sweat"),
    ("30", "すみません", APOLOGY, PURPLE, "sweat"),
    ("31", "お待たせ\nしました", POSE_ARIGATOO, GREEN, "sparkle"),
    ("32", "お気遣い\n感謝です", POSE_ITSUMO, GREEN, "sparkle"),
    ("33", "無理しないで\nください", POSE_MURISHINAI, BLUE, "soft"),
    ("34", "ご自愛\nください", POSE_MURISHINAI, GREEN, "soft"),
    ("35", "応援して\nいます", POSE_HAAI, GREEN, "sparkle"),
    ("36", "さすがです", POSE_SUGOI, GREEN, "sparkle"),
    ("37", "素敵です", POSE_KAWAII, GREEN, "sparkle"),
    ("38", "いいですね", POSE_IINE, GREEN, "soft"),
    ("39", "またお願い\nします", POSE_UNUN, BROWN, "soft"),
    ("40", "失礼します", POSE_YOROSHIKU, BROWN, "soft"),
]


def create_preview(rendered):
    columns = 5
    rows = 8
    preview = Image.new(
        "RGBA",
        (builder.CANVAS[0] * columns, builder.CANVAS[1] * rows),
        (246, 244, 241, 255),
    )
    draw = ImageDraw.Draw(preview)
    font = ImageFont.truetype(str(builder.FONT_PATH), size=22)
    for idx, (number, image) in enumerate(rendered):
        x = (idx % columns) * builder.CANVAS[0]
        y = (idx // columns) * builder.CANVAS[1]
        preview.alpha_composite(image, (x, y))
        draw.text((x + 9, y + 8), number, font=font, fill=(110, 104, 100, 255))
    preview.convert("RGB").save(builder.OUT_DIR / "preview_keigo_work_all_40.png", quality=95)


if __name__ == "__main__":
    builder.create_preview = create_preview
    builder.main()
