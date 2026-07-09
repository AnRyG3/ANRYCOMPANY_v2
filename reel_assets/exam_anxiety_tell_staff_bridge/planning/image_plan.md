# 検査が不安なとき、どこまで伝えていいの？ 画像計画

## 制作ステータス

- 承認範囲: 画像計画、確認用フレーム1〜2枚
- 生成済み: 背景画像12枚、要点テロップ入り画像12枚、音声、動画、確認用コンタクトシート
- 未実施: 投稿情報作成

## 基本方針

- 縦9:16、リアル写真スタイル。
- 文字入れ前提の背景画像として作成するため、画像内には読める文字を入れない。
- 検査室、検査室前、操作室の雰囲気は清潔で穏やかにする。
- 不安表情は軽めにし、煽りや恐怖表現にしない。
- 病院名、氏名、患者ID、資格番号、読めるロゴは入れない。

## 使用キャラクター

- `PATIENT_F30_001`: 32〜38歳女性、一般患者。今回の確認用フレーム1に合わせて、アイボリー系トップス、セージグリーンのパンツ、ベージュ靴で固定する。他の服色は入れない。白ブラウス＋ベージュ系パンツは避ける。
- `RT_TECH_002`: 31歳女性、診療放射線技師。ネイビースクラブ、白い靴、読めないIDバッジ。
- `PATIENT_M02_001`: 2才男児、一般患者。グレー半袖Tシャツ、ネイビー半ズボン、裸足。

## 12枚構成

| No. | テロップ案 | 画像内容 | キャラ・服装 | 生成メモ |
| --- | --- | --- | --- | --- |
| 1 | 「不安なこと、全部伝えていいのか分からなくて…」 | 検査室前で少し悩む女性患者 | `PATIENT_F30_001` 夏の私服 | 確認用フレーム生成済み。表情は軽い不安。 |
| 2 | 検査について気になることは、伝えていただいて大丈夫です。 | 検査室前または操作室前で穏やかに説明する診療放射線技師 | `RT_TECH_002` | 確認用フレーム生成済み。開いた手で説明。 |
| 3 | 「こんなこと聞いていいのかな」と遠慮されるかた、実はとても多いんです。 | 検査前に少し迷う患者の様子 | `PATIENT_F30_001` または登録済み一般患者 | 視聴者が自分ごと化しやすい表情。 |
| 4 | 些細なことでも、教えていただいたほうが私たちも対応しやすいんです。 | メモを取りながら話を聞く診療放射線技師 | `RT_TECH_002` | 威圧感なく、聞く姿勢を強調。 |
| 5 | お子さんが怖がっていることも、ご自身が緊張していることも、大切な情報です。 | 女性患者と小児患者、または親子の検査前シーン | `PATIENT_F30_001`, `PATIENT_M02_001` | 情報量が多くなりすぎないよう、親子を1画面に静かに配置。 |
| 6 | 伝えていただければ、声のかけかたや進めかたを変えることができます。 | 検査前に進め方を調整している様子 | `RT_TECH_002` | 書類やタブレットは文字を読めない状態にする。 |
| 7 | 「こんな些細なことで」と思う必要はありません。 | 少し安心した患者の表情 | `PATIENT_F30_001` | 表情を不安から安心へ移す中盤の転換。 |
| 8 | 検査を受けるのは子どもだけではなく、大人のかたの不安も大切です。 | 大人の患者が検査室前で待つ様子 | `PATIENT_F30_001` または登録済み大人患者 | 小児シリーズから一般向けへの橋渡し。 |
| 9 | 不安なまま検査を受けるより、伝えていただくほうが進めやすくなることがあります。 | 穏やかに声をかける診療放射線技師 | `RT_TECH_002` | 医療的断定を避けた安心表現。 |
| 10 | 遠慮せず、思っていることを教えてください。 | 患者に寄り添う診療放射線技師 | `RT_TECH_002`, 必要なら `PATIENT_F30_001` | 身体接触は控えめ。距離感は自然に。 |
| 11 | 【保存】不安なときに見返せるよう、保存しておいてください。 | スマホだけが写る保存イメージ | 人物なし | 手元を出す場合も個人情報や画面文字は読めないようにする。 |
| 12 | 診療放射線技師の発信　フォローで応援お願いします | 軽くお辞儀する診療放射線技師 | `RT_TECH_002` | エンドカード用。明るく丁寧な締め。 |

## 確認用フレーム

- `sample_frames/frame01_patient_hesitating_sample.png`
- `sample_frames/frame02_rt_tech_reassuring_sample.png`

## 生成済み背景画像

- `image_frames/frame01_patient_hesitating.png`
- `image_frames/frame02_rt_tech_reassuring.png`
- `image_frames/frame03_patient_hesitating_question.png`
- `image_frames/frame04_rt_tech_taking_notes.png`
- `image_frames/frame05_parent_child_concerns.png`
- `image_frames/frame06_rt_tech_adjusting_plan.png`
- `image_frames/frame07_patient_relieved.png`
- `image_frames/frame08_adult_patient_bridge.png`
- `image_frames/frame09_rt_tech_calm_reassurance.png`
- `image_frames/frame10_rt_tech_supporting_patient.png`
- `image_frames/frame11_smartphone_save_cta.png`
- `image_frames/frame12_rt_tech_bowing_end.png`
- `planning/contact_sheet_image_frames.jpg`

## 生成済みテロップ入り画像

- `text_frames/01_text_patient_hesitating.png`
- `text_frames/02_text_rt_tech_reassuring.png`
- `text_frames/03_text_patient_hesitating_question.png`
- `text_frames/04_text_rt_tech_taking_notes.png`
- `text_frames/05_text_parent_child_concerns.png`
- `text_frames/06_text_rt_tech_adjusting_plan.png`
- `text_frames/07_text_patient_relieved.png`
- `text_frames/08_text_adult_patient_bridge.png`
- `text_frames/09_text_rt_tech_calm_reassurance.png`
- `text_frames/10_text_rt_tech_supporting_patient.png`
- `text_frames/11_text_smartphone_save_cta.png`
- `text_frames/12_text_rt_tech_bowing_end.png`
- `planning/contact_sheet_text_frames.jpg`

## 生成済み音声・動画

- `audio/voice.wav`
- `検査が不安なときどこまで伝えていいの.mp4`
- `F:\ANRYCAMPANY\01_ショート動画_リール_YouTubeShorts\インスタ完成形\検査が不安なときどこまで伝えていいの.mp4`
- `video_manifest.json`
