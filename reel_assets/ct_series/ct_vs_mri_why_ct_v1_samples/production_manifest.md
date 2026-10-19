# Production Manifest: 医師がCTって言った。MRIじゃなくて大丈夫？

## Lock state

- Script: approved
- Image plan: approved
- Images: approved (11 cuts)
- Current stage: audio/video generated and checked
- Telop frames: approved (11 cuts)
- Audio: generated and checked
- Video: generated and checked

## Approved cut order

Only the files in this table may be used as source images for this production unit.

| Cut | Approved source image | Purpose |
| --- | --- | --- |
| 01 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\sample_01_consultation_question.png` | 冒頭の心の声 |
| 02 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_02_ct_room_v2.png` | 目的に応じた使い分け |
| 03 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_03_patient_asks_doctor.png` | 医師へ質問する行動 |
| 04 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_04_patient_waiting_with_paper.png` | 不安への共感 |
| 05 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\sample_02_ct_mri_comparison_v2.png` | CTとMRIの方法の違い |
| 06 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_06_ct_mri_equal_close_comparison_v2.png` | 優劣ではなく得意分野が違う |
| 07 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_07_doctor_explains_choice.png` | 検査内容は医師が決める |
| 08 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_08_imaging_department_corridor.png` | 施設による案内の違い |
| 09 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_09_patient_prepares_question.png` | 質問してよいという安心 |
| 10 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_10_patient_question_doctor.png` | 診察室で使える質問文 |
| 11 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_vs_mri_why_ct_v1_samples\scene_11_patient_saves_on_phone.png` | 保存CTA |

## Character / Clothing Lock

| Character ID | Reference | Applies to cuts |
| --- | --- | --- |
| `PATIENT_F50_001` | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\PATIENT_F50_001\reference_sheet.png` | 01, 03, 04, 07, 09, 10, 11 |
| `DOCTOR_001` | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\DOCTOR_001\reference_sheet.png` | 01, 03, 07, 10 |

## Telop lock

- 1画面1メッセージ、短い要点だけを表示する。
- X軸は全カット中央固定。左右へ逃がさない。
- 位置は上・中央・下の3区分だけを使い、中央を優先する。
- 人物の頭・顔・髪や、CTAの保存動作を隠す場合だけ上下へ移す。
- 白い角丸背景は不透明度70%。本文は濃紺、強調は青。
- 青は重要語だけに限定する。
- Font: `F:\ANRYCAMPANY\reel_assets\fonts\M_PLUS_Rounded_1c\MPLUSRounded1c-Bold.ttf`

## Excluded superseded images

- `scene_02_ct_room.png`
- `sample_02_ct_mri_comparison.png`
- `scene_06_ct_mri_equal_close_comparison.png`

These files remain for comparison only and must not be used downstream.
