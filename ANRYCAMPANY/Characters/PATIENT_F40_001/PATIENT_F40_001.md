# PATIENT_F40_001

![[reference_sheet.png]]

## 基本設定

| 項目           | 内容                                                         |
| ------------ | ---------------------------------------------------------- |
| Character ID | PATIENT_F40_001                                            |
| 職業           | 一般患者                                                       |
| 年齢           | 42〜48歳                                                     |
| 性別           | 女性                                                         |
| 体型           | 健康的でスタイルのよい平均体型。過度なモデル体型にはしない。                             |
| 髪型           | ダークブラウン。肩上のロングボブ。フルポニーテールにできない長さ。自然で現代的なスタイル。              |
| 服装           | 40代女性らしい現代的なカジュアル服。白ブラウスとベージュ系パンツの組み合わせは使用しない。医療者の制服は着せない。 |
| 役割           | マンモグラフィ、CT、MRI、健診、予防検査を受ける40代女性患者の代表。                      |

## 外見

- 日本人女性。
- 上品で成熟した印象。
- 健康的で魅力的な見た目。
- 洗練された自然な美しさ。
- 働く女性のような雰囲気。
- 自信があり、落ち着いている。
- 20代、30代の患者キャラクターとは明確に違う年齢感。
- 若作りではない。
- かわいい系ではなく、上品な大人の美しさ。
- 少し縦長の卵型の顔。
- はっきりした顔立ち。
- 知的で表情豊かな目。
- 整った鼻筋。
- 自然な笑顔。
- 大人の女性らしい印象。

## 性格

- 落ち着いている。
- 自信がある。
- 現実的。
- 知的。
- 親しみやすい。

## 画像生成で守ること

- 実写に近い自然光の写真にする。
- 医療者ではなく、一般患者として見える私服にする。
- 肩上のロングボブを維持する。
- 40代女性らしい現代的なカジュアル服を維持する。白ブラウスとベージュ系パンツの組み合わせは使用しない。
- 顔、年齢感、髪型、体型、服装を大きく変えない。
- マンモグラフィ、CT、MRI、健診、予防検査の説明場面で使う場合も、不安を強めすぎない。
- キャラクターの一貫性を最優先にする。
- 実在の人物や有名人に寄せない。

## 禁止事項

- 別人化。
- 若すぎる見た目。
- かわいい系、アイドル風の見た目。
- 医療者の制服、スクラブ、白衣、IDバッジ。
- 派手メイク。
- 金髪。
- アニメ化。
- モデル風、グラビア風、美容広告風の演出。
- 読める病院名、ロゴ、氏名の表示。
- 不安をあおりすぎる表情。
- 白ブラウスとベージュ系パンツの組み合わせ。

## 保存画像

| ファイル | 用途 |
| --- | --- |
| `reference_sheet.png` | 現在の基準画像。6方向ターンアラウンド参照用。 |
| `front.png` | 正面用。 |
| `left45.png` | 左45度用。 |
| `right45.png` | 右45度用。 |
| `left_side_profile.png` | 左側面用。 |
| `right_side_profile.png` | 右側面用。 |
| `side.png` | 既存運用向けの横向き代表カット。 |
| `back.png` | 背面用。 |
| `expressions/` | 表情差分用フォルダ。 |
| `../_clothing_variants_20260630/PATIENT_F40_001_seasonal_summer_casual.png` | Approved seasonal summer casual clothing variant. |
| `../_clothing_variants_20260630/PATIENT_F40_001_exam_gown.png` | Approved patient examination gown variant. |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_spring_ref.png` | 春の私服参考。 |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_summer_ref.png` | 夏の私服参考。 |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_autumn_ref.png` | 秋の私服参考。 |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_winter_ref.png` | 冬の私服参考。 |

## 生成用プロンプト要約

Japanese female general patient, age 42-48, photorealistic natural lighting, elegant mature Japanese woman, healthy attractive appearance, sophisticated natural beauty, working professional, confident and composed, slightly longer oval face, defined facial structure, expressive intelligent eyes, refined nose, natural smile, mature feminine appearance, dark brown shoulder-length long bob, hair just above shoulders, healthy stylish average build, age-appropriate modern casual clothing, no white blouse with beige pants, pure white background, represents women undergoing mammography, CT, MRI, health screening, and preventive examinations, full-body character consistency, fictional person, not based on any real person or celebrity.

## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | PATIENT_F40_001 |
| Role | General patient |
| Age range | 42-48 |
| Gender | Female |
| Body type | Healthy average build with good style; not an exaggerated model body |
| Hair | Dark brown shoulder-length long bob, just above the shoulders; not long enough for a full ponytail |
| Face | Elegant mature Japanese woman, refined natural beauty, confident, composed, slightly longer oval face, defined facial structure, expressive intelligent eyes, refined nose, natural smile |
| Personality | Calm, confident, realistic, intelligent, approachable |
| Default clothing | Age-appropriate modern casual clothing; never use a white blouse with beige pants; not medical staff clothing |
| Approved seasonal summer casual variant | Light beige linen-blend blouse with modest neckline and short sleeves, charcoal or muted navy straight ankle pants, calm taupe low-heel shoes. Saved as `../_clothing_variants_20260630/PATIENT_F40_001_seasonal_summer_casual.png`. |
| Approved patient examination gown variant | Simple pale warm-gray/beige patient examination gown, loose modest short-sleeve tunic and matching easy pants, simple patient slippers. This is patient clothing, not staff scrubs. Saved as `../_clothing_variants_20260630/PATIENT_F40_001_exam_gown.png`. |
| Seasonal clothing reference set | Use the selected spring, summer, autumn, and winter private-clothing references saved under `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\`. These are clothing and season references; keep the character face identity from this Character ID. |
| Typical scenes | Mammography, CT, MRI, health screening, and preventive examination scenes |

### Keep

- Keep the same face identity, age range, shoulder-length long bob, healthy average build, and elegant mature patient feeling.
- Keep this character clearly in her 40s; not too young and not idol-like.
- Keep the patient as an ordinary person, not a healthcare worker.
- Use the approved examination gown variant only when the character is clearly a patient in an exam or preparation scene.
- Keep anxiety mild and realistic, not exaggerated.

### Avoid

- Do not put this character in scrubs, white coat, nurse uniform, ID badge, or medical staff clothing.
- Do not use heavy makeup, gold hair, anime style, cute idol styling, model-like glamour, beauty-ad styling, readable names, logos, or patient identifiers.
- Do not change face, age, hairstyle, body type, or clothing rules without explicit approval.
- Do not dress this character in a white blouse with beige pants.

### Generation Prompt Summary

Japanese female general patient, age 42-48, photorealistic natural lighting, elegant mature Japanese woman, healthy attractive appearance, sophisticated natural beauty, working professional, confident and composed, slightly longer oval face, defined facial structure, expressive intelligent eyes, refined nose, natural smile, mature feminine appearance, dark brown shoulder-length long bob just above shoulders, healthy stylish average build, age-appropriate modern casual clothing, never a white blouse with beige pants, fictional person, not based on any real person or celebrity, character consistency critical.
