# 造影CTの話が出たら、腎臓について何を伝える？ — 画像計画

## 現在の段階

- 台本と01の確認用フレームはユーザー承認済み。02〜11の画像を制作し、全11枚の画像確認待ち。
- テロップ、音声、動画、生成スクリプトは作らない。
- 画像の正式採用と全画像の承認後に、別途 `production_manifest.md` で入力画像を固定する。

## 共通方針

- 縦長の実写調。診察室と手元の資料を中心にし、患者さん自身が造影CTを予約する描写は使わない。
- 医療上の判断、採血結果の有効期間、検査値や病院名を画像に書き込まない。文字は後の承認段階で入れる。
- 表情は落ち着いた相談の範囲にとどめ、不安を強調しない。
- 患者 `PATIENT_F50_001` は全カットで同一の淡いニュートラル色カーディガン、白系インナー、ライトグレー系パンツ、歩きやすい靴を固定。服装参照: `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\PATIENT_F50_001\reference_sheet.png`。
- 医師 `DOCTOR_001` は全カットで白衣、ライトブルーのシャツ、ダークスラックスを固定。参照: `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\DOCTOR_001\reference_sheet.png`。
- ほかの人物は出さない。文字入れ用の余白は確保するが、現段階でテロップは入れない。

## 11枚の構成

| 枚 | 承認済み文言（ナレーション＝テロップ） | 画像の要点 |
|---|---|---|
| 01 | 造影CTの話なら、腎臓のことを医師に伝えて。 | 診察室で患者が医師に話しかける場面。診察から始まることを一目で示す。確認用フレーム候補。 |
| 02 | 造影剤を使えるのか、気になりますよね。 | 同じ患者が診察中に少し考える表情。過度に不安そうにしない。 |
| 03 | 伝えるのは、腎臓の病気や腎機能の低下を指摘されたことです。 | 診察で患者が既往について説明し、医師が聴く。 |
| 04 | 造影CTでは、施設が定める期間内の採血結果で腎機能を確認します。 | 医師が採血結果を確認する手元。数値・期限・個人情報は読めない。 |
| 05 | その期間や、結果がないときの対応は施設によって違います。 | 診察で医師が検査の進め方を説明する様子。期限を示すカレンダーや断定的な表示は避ける。 |
| 06 | 最近の採血結果が手元にあれば、診察で医師に見せてください。 | 患者が持参した採血結果を医師に見せる手元。持参が必須に見えない自然な場面。 |
| 07 | 造影剤を使うかどうかは、医師が判断します。 | 医師が診察資料を確認しながら丁寧に説明する。判断済みの印や合否表示は出さない。 |
| 08 | 数値を覚えていなくても、腎臓について言われたことを伝えて大丈夫です。 | 患者が穏やかに口頭で説明する。数値の吹き出しは出さない。 |
| 09 | 採血結果が手元になくても、診察で医師に相談してください。 | 医師が患者の話を聴く診察場面。採血結果を持っていない人を責める印象にしない。 |
| 10 | 診察では「腎臓が悪いと言われたことがありますが、造影CTの前に確認することはありますか？」と聞いてみてください。 | 同じ診察場面をやや引きで見せ、後で長い例文を読みやすく置ける余白を確保する。 |
| 11 | この聞き方を保存して診察前に見返し、よければフォローしてください。 | スマートフォンで見返す場面。保存を主役にし、予告表示は入れない。 |

## 確認用フレーム

- まず01を制作し、登録キャラクターの顔・年齢・髪型・体型・服装一致を確認する。
- 01が不一致なら不採用として扱い、残りの画像制作に進まない。
- 01の確認用フレーム: `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_samples\01_consultation_sample.png`。ユーザー承認済み。制作側の一次確認でも `PATIENT_F50_001` と `DOCTOR_001` の顔・年齢感・髪型・服装が参照画像と一致し、診察場面として成立。

## 画像確認用ファイル

以下は制作済みの画像。02〜11のユーザー確認前なので、`production_manifest.md` はまだ作成しない。

| 枚 | ファイル |
|---|---|
| 01 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\01_consultation.png` |
| 02 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\02_thoughtful_patient.png` |
| 03 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\03_history_discussion.png` |
| 04 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\04_blood_result_review.png` |
| 05 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\05_facility_explanation.png` |
| 06 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\06_result_handover.png` |
| 07 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\07_doctor_judgment.png` |
| 08 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\08_patient_speaks.png` |
| 09 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\09_consult_without_result.png` |
| 10 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\10_example_question.png` |
| 11 | `F:\ANRYCAMPANY\reel_assets\ct_series\ct_contrast_kidney_consult_v1_images\11_save_before_consult.png` |
