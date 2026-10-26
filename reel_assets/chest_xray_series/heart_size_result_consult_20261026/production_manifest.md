# Production Manifest

画像承認: 2026-10-26。11枚の文字なし画像を以下の順で固定する。5枚目は立位ブッキー台とポータブル装置を比較する `frame_05_comparison_v7_941.png`（承認画像を共通の941px幅に調整したもの）。旧版の5枚目は使用しない。

## Approved Images

| Cut | Approved input image (absolute path) | Purpose |
|---|---|---|
| 01 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\sample_01_result_waiting_no_text.png` | 結果を見た患者 |
| 02 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_02_no_text.png` | 一言だけでは理由不明 |
| 03 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_03_no_text.png` | 胸部X線に写る範囲 |
| 04 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_04_no_text.png` | 心臓の影 |
| 05 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_05_comparison_v7_941.png` | 立位ブッキー台とポータブル装置の比較 |
| 06 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_06_no_text.png` | 写真だけでは決めない |
| 07 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\sample_07_doctor_explanation_no_text.png` | 診察での説明 |
| 08 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_08_no_text.png` | 患者からの質問 |
| 09 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_09_no_text.png` | 質問のメモ |
| 10 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_10_no_text.png` | 診察で使う質問 |
| 11 | `F:\ANRYCAMPANY\reel_assets\chest_xray_series\heart_size_result_consult_20261026\frame_11_no_text.png` | 保存案内 |

## Character Clothing Lock

| Character ID | Approved clothing reference (absolute path) | Applies to cuts |
|---|---|---|
| `PATIENT_F40_001` | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_spring_ref.png` | 01, 02, 07, 08, 09, 10, 11 |
| `DOCTOR_001` | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\DOCTOR_001\reference_sheet.png` | 04, 06, 07, 08, 10 |
| `RT_TECH_001` | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\RT_TECH_001\reference_sheet.png` | 05 |

## Next Gate

画像・テロップ11枚はユーザー承認済み。VOICEVOX「もち子さん」（speedScale 1.15）の音声と動画を作成済み。カット別の音声尺・画像対応・出力先は `video_manifest.json` に記録。完成動画はユーザー確認待ち。
