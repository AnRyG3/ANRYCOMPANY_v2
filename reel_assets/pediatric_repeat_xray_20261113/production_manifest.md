# Production Manifest

画像全体の承認: 2026-11-02。下記10枚をカット順に固定する。元の裸足サンプルは使用しない。

## Approved Images

| Cut | Approved input image (absolute path) | Purpose |
|---|---|---|
| 01 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\sample_01_consultation_hook_shoes.png` | 冒頭：質問できること |
| 02 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_02_parent_concern.png` | 保護者の心配 |
| 03 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_03_doctor_explains.png` | 診断・経過を見る目的 |
| 04 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_04_prior_image_purpose.png` | 今回の目的の違い |
| 05 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_05_medical_necessity.png` | 医師の必要性判断 |
| 06 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_06_tell_previous_xray.png` | 前の撮影を伝える |
| 07 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_07_xray_preparation_v2.png` | 体格に合わせた撮影準備。修正版を承認済み |
| 08 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_08_share_concern.png` | 心配と目的の確認 |
| 09 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_09_question_example.png` | 診察で使える例文 |
| 10 | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\cut_10_save_for_visit.png` | 保存CTA |

## Character Clothing Lock

| Character ID | Approved clothing reference (absolute path) | Applies to cuts |
|---|---|---|
| `PATIENT_F30_001` | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_autumn_arrival_greige_ref.png` | 01-06, 08-10 |
| `PATIENT_M02_001` | `F:\ANRYCAMPANY\reel_assets\pediatric_repeat_xray_20261113\sample_01_consultation_hook_shoes.png` | 01-10。ユーザー指定の紺色スニーカーと薄いグレーの靴下を含む |
| `DOCTOR_001` | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\DOCTOR_001\reference_sheet.png` | 01, 03-06, 08-09 |

## Source Lock Check

- 承認済みの入力画像は10枚。文字入れは上表の順序と絶対パスが一致した場合のみ実行する。
- `sample_01_consultation_hook.png` は比較用の裸足画像であり、入力に使用しない。
- 07の修正版はユーザーが承認済み。旧 `cut_07_xray_preparation.png` は入力に使用しない。
