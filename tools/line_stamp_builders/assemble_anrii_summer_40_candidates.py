from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"F:\ANRYCAMPANY")
BASE = ROOT / r"02_LINEスタンプ\あんりぃ_LINEスタンプ制作工場\04_完成画像\夏を感じるスタンプ_あんりぃ40"
OUT_DIR = BASE / "03_40個完成"
PREVIEW = OUT_DIR / "preview_all_40_submission_candidates.png"
FONT = Path(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc")

SOURCES = [
    BASE / r"01_試作5個\提出用候補_5個\01_atsui_submission_candidate.png",
    BASE / r"01_試作5個\提出用候補_5個\02_natsudane_submission_candidate.png",
    BASE / r"01_試作5個\提出用候補_5個\03_otsukare_summer_submission_candidate.png",
    BASE / r"01_試作5個\提出用候補_5個\04_suibun_submission_candidate.png",
    BASE / r"01_試作5個\提出用候補_5個\05_suzundemasu_submission_candidate.png",
    BASE / r"02_提出用候補_06-10\個別PNG\06_ice_tabeteyo_submission_candidate.png",
    BASE / r"02_提出用候補_06-10\個別PNG\07_tokeru_submission_candidate.png",
    BASE / r"02_提出用候補_06-10\個別PNG\08_umi_ikitai_submission_candidate.png",
    BASE / r"02_提出用候補_06-10\個別PNG\09_pool_saikou_submission_candidate.png",
    BASE / r"02_提出用候補_06-10\個別PNG\10_hanabi_kirei_submission_candidate.png",
    BASE / r"03_提出用候補_11-15\個別PNG\11_matsuri_da_submission_candidate.png",
    BASE / r"03_提出用候補_11-15\個別PNG\12_kakigoori_tabetai_submission_candidate.png",
    BASE / r"03_提出用候補_11-15\個別PNG\13_suika_submission_candidate.png",
    BASE / r"03_提出用候補_11-15\個別PNG\14_natsubate_chuu_submission_candidate.png",
    BASE / r"03_提出用候補_11-15\個別PNG\15_hinyari_submission_candidate.png",
    BASE / r"04_提出用候補_16-20\個別PNG\16_hiyake_shita_submission_candidate.png",
    BASE / r"04_提出用候補_16-20\個別PNG\17_mushiyoke_kanryou_submission_candidate.png",
    BASE / r"04_提出用候補_16-20\個別PNG\18_kayui_submission_candidate.png",
    BASE / r"04_提出用候補_16-20\個別PNG\19_yuusuzumi_submission_candidate.png",
    BASE / r"04_提出用候補_16-20\個別PNG\20_ii_tenki_submission_candidate.png",
    BASE / r"05_提出用候補_21-25\個別PNG\21_guerrilla_gouu_submission_candidate.png",
    BASE / r"05_提出用候補_21-25\個別PNG\22_kasa_wasureta_submission_candidate.png",
    BASE / r"05_提出用候補_21-25\個別PNG\23_yakeru_submission_candidate.png",
    BASE / r"05_提出用候補_21-25\個別PNG\24_reibou_saikou_submission_candidate.png",
    BASE / r"05_提出用候補_21-25\個別PNG\25_soumen_tabeteyo_submission_candidate.png",
    BASE / r"06_提出用候補_26-30\個別PNG\26_natsuyasumi_submission_candidate.png",
    BASE / r"06_提出用候補_26-30\個別PNG\27_shukudai_yabai_submission_candidate.png",
    BASE / r"06_提出用候補_26-30\個別PNG\28_obon_desune_submission_candidate.png",
    BASE / r"06_提出用候補_26-30\個別PNG\29_kisei_shimasu_submission_candidate.png",
    BASE / r"06_提出用候補_26-30\個別PNG\30_ittekimasu_submission_candidate.png",
    BASE / r"07_提出用候補_31-35\個別PNG\31_tadaima_submission_candidate.png",
    BASE / r"07_提出用候補_31-35\個別PNG\32_kanpai_submission_candidate.png",
    BASE / r"07_提出用候補_31-35\個別PNG\33_negurushii_submission_candidate.png",
    BASE / r"07_提出用候補_31-35\個別PNG\34_fuurin_chirin_submission_candidate.png",
    BASE / r"07_提出用候補_31-35\個別PNG\35_himawari_mankai_submission_candidate.png",
    BASE / r"08_提出用候補_36-40\個別PNG\36_nyuudougumo_mokumoku_submission_candidate.png",
    BASE / r"08_提出用候補_36-40\個別PNG\37_senkou_hanabi_submission_candidate.png",
    BASE / r"08_提出用候補_36-40\個別PNG\38_natsu_no_omoide_submission_candidate.png",
    BASE / r"08_提出用候補_36-40\個別PNG\39_muri_atsui_submission_candidate.png",
    BASE / r"08_提出用候補_36-40\個別PNG\40_mata_asobo_submission_candidate.png",
]


def make_preview(paths: list[Path]) -> None:
    cols = 8
    rows = 5
    cell_w, cell_h = 190, 178
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), (246, 246, 246))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 18) if FONT.exists() else ImageFont.load_default()

    for idx, path in enumerate(paths):
        image = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
        bg.alpha_composite(image)
        bg.thumbnail((170, 150), Image.Resampling.LANCZOS)
        col = idx % cols
        row = idx // cols
        x = col * cell_w + (cell_w - bg.width) // 2
        y = row * cell_h + 22
        sheet.paste(bg.convert("RGB"), (x, y))
        draw.text((col * cell_w + 8, row * cell_h + 4), f"{idx + 1:02d}", fill=(80, 80, 80), font=font)
    sheet.save(PREVIEW, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    for index, source in enumerate(SOURCES, start=1):
        if not source.exists():
            raise FileNotFoundError(source)
        out = OUT_DIR / f"{index:02d}.png"
        shutil.copy2(source, out)
        output_paths.append(out)
    make_preview(output_paths)
    print(PREVIEW)
    print(OUT_DIR)


if __name__ == "__main__":
    main()
