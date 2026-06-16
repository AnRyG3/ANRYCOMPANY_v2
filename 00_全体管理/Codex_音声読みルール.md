# Codex 音声読みルール

ANRYCAMPANYのVOICEVOX音声生成では、次の読みを毎回固定する。

## 固定読み

- 骨密度: こつみつど
- 骨密度検査: こつみつど検査
- DXA: できさ
- 乳房: にゅうぼう
- 値: あたい

## 運用

- 画像テロップは漢字・英字のままでよい。
- ナレーション用テキストでは、誤読しやすい語だけひらがなへ置き換える。
- VOICEVOX生成前に、台本・生成スクリプト・音声用テキストでこの読みを確認する。
- 画像枚数と音声区切りは原則1対1にする。複数枚に1音声をまたがせる場合は、事前に理由を明記する。
# Codex voice reading fixed rules

This readable section is authoritative when the garbled section above is hard to read.

## Must apply before VOICEVOX synthesis

- 骨密度 -> こつみつど
- 人を指す「方」 -> かた
  - Example: 戸惑う方 -> 戸惑うかた
  - Example: ご家族がいる方 -> ご家族がいるかた

Do not rely on VOICEVOX default reading for these words. Convert the narration text before audio generation.
