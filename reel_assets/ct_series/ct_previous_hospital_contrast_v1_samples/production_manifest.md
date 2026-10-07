# Production Manifest

## Approved Images

| Cut | Approved input image (absolute path) | Purpose |
| --- | --- | --- |
| 01 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\sample_01_hook_patient_ct_room.png` | 前の病院でCTを撮ったのに、また造影CT？ |
| 02 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\sample_02_ct_room_injector.png` | 単純CTだけでは分からないことがないか確認する |
| 03 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\scene_03_injector_detail_v2.png` | 造影剤で見え方が変わる |
| 04 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\scene_04_ct_room_wide.png` | 必要な情報に応じて追加することがある |
| 05 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\scene_05_patient_waiting.png` | 前のCTを撮っていても追加することがある |
| 06 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\scene_06_patient_corridor.png` | 造影CTが必要かは医師が判断する |
| 07 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\scene_07_patient_reception.png` | 以前の造影剤での気分不良は事前に伝える |
| 08 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_previous_hospital_contrast_v1_samples\scene_08_patient_ct_room.png` | 気になることは検査前に確認する |

## Character Clothing Lock

| Character ID | Approved clothing reference (absolute path) | Applies to cuts |
| --- | --- | --- |
| `PATIENT_F30_001` | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_autumn_ref.png` | 01, 05-08 |

## Text-Frame Check

- Telop input count: 8
- Approved image count: 8
- Cut order: 01 to 08, one-to-one
- Source images above are the only permitted inputs for telop generation.
