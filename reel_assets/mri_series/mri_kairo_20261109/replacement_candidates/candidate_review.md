# 08・09差し替え候補（2026-11-01承認済み）

受付はカイロの確認を行わないという2026-11-01の指摘に合わせた画像候補。ユーザー承認後、バイト単位で同一の画像を制作フォルダ直下にコピーし、`production_manifest.md` の08・09を更新した。元の08・09画像は変更していない。

| カット | 候補 | 目的 |
|---|---|---|
| 08 | `cut_08_exam_waiting_candidate.png` | 受付カウンターではなく、検査前の待合を示す。人物なし。 |
| 09 | `cut_09_patient_technologist_candidate.png` | 患者が検査担当者である `RT_TECH_001` に伝える。受付スタッフは登場しない。上中央の例文余白を確保。 |

09の患者は `PATIENT_F30_001`。服装参照は `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_winter_ref.png`。検査担当者は `RT_TECH_001`、服装参照は `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\RT_TECH_001\reference_sheet.png`。

承認後の入力画像: `../image_08_exam_waiting.png`、`../image_09_patient_technologist_PATIENT_F30_001_RT_TECH_001.png`。テロップ画像は再生成・再確認済み。音声・動画はテロップ承認まで作らない。
