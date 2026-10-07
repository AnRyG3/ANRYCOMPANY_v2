# Production Manifest

## Approved Images

| Cut | Approved input image (absolute path) | Purpose |
|---|---|---|
| 01 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_samples\sample_01_hook_sleeping_mri.png` | MRI中に寝てもよいかという疑問と条件付き回答 |
| 02 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_02_head_spine_joint_rest.png` | 頭・背骨・関節などでは眠ってもよい場合がある |
| 03 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_03_keep_still.png` | 眠って体が動くと画像がぶれることがある |
| 04 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_04_intercom_voice.png` | 動いた場合は検査中に声をかけることがある |
| 05 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_samples\sample_02_abdominal_breath_hold.png` | お腹などでは息止めの合図が必要なことがある |
| 06 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_06_stay_awake_calm.png` | 合図がある検査では起きているようお願いすることがある |
| 07 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_07_tell_before_exam.png` | 眠りそうで心配なら検査前に伝える |
| 08 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_08_question_phrase.png` | 息止めの合図があるか確認する一文 |
| 09 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_09_ask_staff.png` | 自分の検査について担当者へ確認する |
| 10 | `F:\ANRYCAMPANY\reel_assets\mri_series\mri_sleep_20261007_images\frame_10_follow_cta.png` | 検査前の疑問に答える発信のフォローCTA |

## Character Clothing Lock

| Character ID | Approved clothing reference (absolute path) | Applies to cuts |
|---|---|---|
| `PATIENT_F30_001` | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F30_001_exam_gown.png` | 01-10 |

## Footwear Handling

- Cuts 01-06: MRI寝台上では患者用スリッパを脱ぎ、裸足。
- Cuts 07-10: 立位・待合では同じ承認済み患者用スリッパを着用。

## Lock Status

- Image approval: approved by user.
- Count and cut order: 10 images, verified before telop generation.
- Telop source lock: only the images listed above may be used.
- Audio and video: approved by user for generation on 2026-10-07.
- Audio and video generation: completed on 2026-10-07.
- Final video: `F:\ANRYCAMPANY\01_ショート動画_リール_YouTubeShorts\インスタ完成形\MRI中_寝てもいい_20261007.mp4`
