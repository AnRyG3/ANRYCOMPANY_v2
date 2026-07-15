# 骨折の診断、レントゲンだけじゃダメなの？ 画像計画

## 前提

- 台本: ユーザー承認済み改訂版を使用。
- 修正反映:
  - CTとMRIを固定順序に見せず、部位や状況に応じて選択される表現にする。
  - 「不安を感じなくて大丈夫」を、不安を自然な感情として受け止める表現にする。
  - 「見逃しなく」を「見逃しを減らし」に変更する。
- 画像数: 12枚（CTA 2枚を含む）。
- 使用キャラ:
  - `PATIENT_F50_001`: 52〜58歳の女性一般患者。淡いニュートラルカラーのカーディガン、白系インナー、ライトグレー系パンツ、歩きやすい靴。
  - `DOCTOR_001`: 40〜45歳の男性医師。白衣、ライトブルーのワイシャツ、ダークスラックス、読めないIDバッジ。
  - `RT_TECH_001`: 30歳女性の診療放射線技師。ネイビースクラブ、白い医療用シューズ、読めないIDバッジ。
- 画角: 縦9:16。
- 画調: 実写に近い医療広告写真。清潔で落ち着いた院内、過度な不安表現なし。
- 文字入れ: 今回は未実施。最終テロップ前に `telop-style-rules.md` を確認する。

## 画像構成

| Slide | 目的 | 画像内容 | 注意 |
| --- | --- | --- | --- |
| 1 | 疑問の導入 | 診察室。股関節のレントゲン風画像が表示されたモニターの前で、`DOCTOR_001` と向き合う `PATIENT_F50_001`。患者は少し戸惑った表情。 | 上部にテロップ余白。実在患者情報、読める文字、病院名、ロゴなし。表情は軽い疑問に留める。 |
| 2 | 患者の疑問 | `PATIENT_F50_001` が軽く首をかしげて考え込むクローズアップ。 | 同じ服装と年齢感を維持。不安を強めすぎない。 |
| 3 | レントゲンの役割 | 清潔なレントゲン撮影室。装置中心のシンプルな背景。 | 人物なし。装置を現実的に描写し、読める表示は入れない。 |
| 4 | 写りにくい骨折 | 検査室の壁や機材を軽くぼかした、清潔感のある背景。 | 人物なし。説明テロップを載せやすい余白を確保。 |
| 5 | 判断が難しい例 | CT室の入口またはCT装置の一部が見える、静かで整然とした空間。 | 人物なし。MRI装置と混同しない。読める案内表示なし。 |
| 6 | CTの説明 | CT装置の寝台に仰向けになる `PATIENT_F50_001`。そばで `RT_TECH_001` が穏やかに準備・説明している。 | 患者は承認済みの私服。CTガントリを現実的に描写。不要な露出や処置器具なし。上部に余白。 |
| 7 | MRIの説明 | MRI室。MRI装置の一部が見える落ち着いた背景。 | 人物なし。CTと区別できる長いボア形状。磁性体を想起させる不要な小物なし。 |
| 8 | 段階への納得 | `PATIENT_F50_001` が軽く驚きながらも納得しかけているクローズアップ。 | 驚きを大げさにしない。服装・髪型・顔を維持。 |
| 9 | 不安への声かけ | `RT_TECH_001` が穏やかな表情で `PATIENT_F50_001` に話しかける。 | 診療放射線技師として描写。医師・看護師の服装にしない。 |
| 10 | 安心して退出 | 検査室を出る `PATIENT_F50_001` の後ろ姿。落ち着いた足取り。 | `back.png` を参照。病変や痛みを誇張しない。 |
| 11 | 保存CTA | スマートフォンを保存操作している手元。背景は柔らかくぼかした検査室。 | 画面内に読める文字や実在アプリのロゴを入れない。 |
| 12 | フォローCTA | `RT_TECH_001` が軽くお辞儀している背景。 | 最終テキスト用。文字入れは後工程。上部から中央に十分な余白。 |

## 今回の確認用フレーム

- Slide 1: `sample_frames/slide01_doctor_patient_hip_xray_sample.png`
  - 医師・患者・股関節レントゲン風モニターを含む導入場面。
- Slide 6 revised sample: `sample_frames/slide06_ct_patient_rt_tech_sample_v2.png`
  - 実機CT資料を参照し、薄い水平天板とガントリへの接続を再現。
  - 患者は天井方向を見て自然に仰向けになり、`RT_TECH_001` は患者と目を合わせず位置合わせに集中する。
  - 初回案 `sample_frames/slide06_ct_patient_rt_tech_sample.png` は比較用として保持。

## 生成済み背景画像

- Slide 1: `sample_frames/slide01_doctor_patient_hip_xray_sample.png`
- Slide 2: `sample_frames/slide02_patient_puzzled.png`
- Slide 3: `sample_frames/slide03_xray_room.png`
- Slide 4: `sample_frames/slide04_blurred_exam_room.png`
- Slide 5: `sample_frames/slide05_ct_room_partial.png`
- Slide 6: `sample_frames/slide06_ct_patient_rt_tech_sample_v2.png`
- Slide 7: `sample_frames/slide07_mri_room.png`
- Slide 8: `sample_frames/slide08_patient_understands.png`
- Slide 9: `sample_frames/slide09_rt_tech_reassures_patient.png`
- Slide 10: `sample_frames/slide10_patient_leaves.png`
- Slide 11: `sample_frames/slide11_save_phone_cta_bg.png`
- Slide 12: `sample_frames/slide12_rt_tech_bow_cta_bg.png`

## 未実施工程

- テロップ・CTA文字入れ。
- 音声、動画、投稿情報の作成。
