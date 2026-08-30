# MRI前、マグネットネイルしてたらどうする？ 画像計画

作成日: 2026-08-27
段階: 画像計画 + 全11枚の素画像 + テロップ入り静止画 + 音声 + 動画まで

## 承認状態

- 台本方向: 承認済み
- 画像計画: 作成済み
- 確認用フレーム: 承認済み
- 素画像: 全11枚作成済み
- テロップ入り静止画: 全11枚作成済み
- 音声: 作成済み
- 動画: 作成済み

## 使用キャラクター

- 患者: `PATIENT_F20_001`
  - 20代女性患者
  - 夏の私服参照
  - 不安を強めすぎず、「知らなくて当然だが、気づいて相談できる」表情
- 診療放射線技師: `RT_TECH_001`
  - ネイビースクラブ
  - 落ち着いて相談を受ける役割

## 全体方針

- 主軸は「できる・できないの断定」ではなく「患者さんの体へのリスクがあるため、予約検査なら事前に相談・準備してほしい」。
- 「外しておくのが基本」という医療者側の当たり前感は出さない。
- 患者さんを責めない。知らなくて当然の前提で、早めに気づくと安全に準備できる流れにする。
- ネイルは美容広告風に見せず、検査前の確認対象として自然に見せる。
- 画像内に読める病院名、氏名、ID、説明文は入れない。テロップは後工程。

## 画像構成案

1. MRI予約票やスマホを見ながら、マグネットネイルに気づく患者
   - 対応台本: 「MRI予約あるのに、マグネットネイルしてる…これ外した方がいい？」
   - 目的: 冒頭3秒。対象者 + 具体場面 + 迷い。

2. 問診票でネイル項目に気づく患者
   - 対応台本: MRI検査前の問診票で、ネイルについて聞かれて驚く方がいます
   - 目的: 患者さんにとって当たり前ではないことを自然に示す。

3. 手元のマグネットネイルの寄り
   - 対応台本: マグネットネイルや一部のジェルネイルには、鉄粉など金属成分が含まれることがあります
   - 目的: 美容寄りにせず、成分確認の話へつなぐ。

4. MRI装置のある検査室
   - 対応台本: MRIは強い磁石と電波を使う検査です
   - 目的: 危険演出ではなく、検査環境の説明。

5. 患者が検査前に手元を見て少し迷う
   - 対応台本: ネイルの成分によっては熱を持ったり、変色したり、画像に影響したりする可能性があります
   - 目的: リスクを冷静に伝える。

6. 診療放射線技師が患者の手元を確認している
   - 対応台本: 大事なのは、画像の乱れだけでなく、患者さんの体へのリスクがあることです
   - 目的: 安全面が主理由だと伝える。

7. MRI装置の前で、手元も装置内に入ることがわかる構図
   - 対応台本: 撮影する場所が手元から離れていても、MRI装置の中に入るため「関係ない」とは言い切れません
   - 目的: 「部位が遠いから大丈夫」と思い込まないようにする。

8. 予約日前にネイルオフを検討している患者
   - 対応台本: 施設によって対応は分かれますが、MRIの予約があるときは、事前にネイルを外して来てもらえると安心です
   - 目的: 医療者の当たり前ではなく、患者さんの準備行動として見せる。

9. 受付または検査前相談で、患者がネイルを見せて相談する
   - 対応台本: 外せない場合や、対象かわからない場合は、予約時や検査前に相談してください
   - 目的: 行動の出口を明確にする。

10. スマホで保存する患者または家族
    - 対応台本: MRI予約がある人や家族は、検査前日や受付前に見返せるように保存しておいてください
    - 目的: 保存CTA。誰が・いつ見返すかを明確化。

11. 診療放射線技師が落ち着いて案内する締め
    - 対応台本: 他の検査前の疑問も、診療放射線技師目線で発信しています
    - 目的: 継続視聴・フォロー導線。

## 確認用サンプル

- `samples/sample_01_mri_reservation_magnet_nail_patient.png`
  - Frame 1想定。
  - 患者キャラの顔・年齢感・髪型は概ね通過。
  - 服装は夏服参照よりカーディガン寄り。最終生成時は必要に応じて夏私服へ寄せる。

- `samples/sample_02_mri_nail_consult_rt.png`
  - Frame 9想定。
  - 患者と診療放射線技師の相談場面として通過。
  - 背景にMRI装置が入り、検査前相談の文脈が伝わる。

## 作成済み素画像

- `images/frame_01_mri_reservation_magnet_nail_patient.png`
- `images/frame_02_mri_questionnaire_nail_item.png`
- `images/frame_03_magnet_nail_closeup.png`
- `images/frame_04_clean_mri_room.png`
- `images/frame_05_patient_checks_nails_waiting.png`
- `images/frame_06_rt_checks_patient_nails.png`
- `images/frame_07_patient_enters_mri_bore_hands_inside.png`
- `images/frame_08_patient_prepares_nail_removal.png`
- `images/frame_09_mri_nail_consult_rt.png`
- `images/frame_10_save_cta_phone.png`
- `images/frame_11_rt_closing_mri_corridor.png`

## 作成済みテロップ入り静止画

- `telop_frames/telop_01_mri_reservation_magnet_nail_patient.png`
- `telop_frames/telop_02_mri_questionnaire_nail_item.png`
- `telop_frames/telop_03_magnet_nail_closeup.png`
- `telop_frames/telop_04_clean_mri_room.png`
- `telop_frames/telop_05_patient_checks_nails_waiting.png`
- `telop_frames/telop_06_rt_checks_patient_nails.png`
- `telop_frames/telop_07_patient_enters_mri_bore_hands_inside.png`
- `telop_frames/telop_08_patient_prepares_nail_removal.png`
- `telop_frames/telop_09_mri_nail_consult_rt.png`
- `telop_frames/telop_10_save_cta_phone.png`
- `telop_frames/telop_11_rt_closing_mri_corridor.png`
- `telop_frames/contact_sheet_20260827_telop_frames.jpg`

## 作成済み音声・動画

- `audio/voice.wav`
- `video/MRI前_マグネットネイルしてたらどうする_20260827.mp4`
- `F:\ANRYCAMPANY\01_ショート動画_リール_YouTubeShorts\インスタ完成形\MRI前_マグネットネイルしてたらどうする_20260827.mp4`
- `qa_midframes/qa_midframes_contact_sheet.jpg`
- `video_manifest_20260827.json`

## 次の承認後に進めること

- 動画仕様: 1080x1920、30fps、AAC音声あり。
- 尺: 約56.23秒。
- 音声速度: 1.2x。
- 画像と音声: 11フレーム、11ナレーションで対応。
- 追加余白: 各セグメント末尾0.04秒。
