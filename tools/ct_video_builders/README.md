# CT Video Builders

CT系リール動画を生成するためのスクリプト置き場です。

## 主なスクリプト

- `build_ct_day1_video.ps1` : Day 1 CT動画生成
- `build_ct_day1_visual_refresh.ps1` : Day 1 ビジュアル更新版
- `build_ct_trilogy.ps1` : CT 3部作生成
- `build_ct_trilogy_v2_voicevox.ps1` : VOICEVOX版 CT 3部作生成
- `build_ct_trilogy.mjs` : 旧JavaScript版。文字化けが残っているため基本はPowerShell版を使う

## 使い方

PowerShell版はこのフォルダへ移動済みですが、内部では自動的に `F:\ANRYCAMPANY` をルートとして参照します。
VOICEVOXを使うものは、先にVOICEVOXを起動してから実行してください。
