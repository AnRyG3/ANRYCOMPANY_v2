# PATIENT_F30_001

![[reference_sheet.png]]

## 基本設定

| 項目 | 内容 |
| --- | --- |
| Character ID | PATIENT_F30_001 |
| 職業 | 一般患者 |
| 年齢 | 32〜38歳 |
| 性別 | 女性 |
| 体型 | 健康的でスタイルのよい平均体型。過度なモデル体型にはしない。 |
| 髪型 | ライトブラウンのロングヘア。自然な日常ヘアスタイル。 |
| 服装 | 30代女性らしい現代的な私服。白ブラウスとベージュ系パンツの組み合わせは使用しない。医療者の制服は着せない。 |
| 役割 | CT、MRI、レントゲン、健診を受ける30代女性患者の代表。 |

## 外見

- 日本人女性。
- 自然な日本人女性の美しさ。
- 大人っぽく親しみやすい。
- 上品だが、一般の患者さんとして共感しやすい。
- 働く女性、または母親のような雰囲気。
- バランスのよい顔立ち。
- 少し卵型の顔。
- 温かく表情豊かな目。
- 自然な笑顔。
- 柔らかく女性らしい顔立ち。
- 親しみやすく知的な印象。
- リラックスして話しかけやすい雰囲気。

## 性格

- 温かい。
- 親しみやすい。
- 現実的。
- 自信がある。
- 共感しやすい。

## 画像生成で守ること

- 実写に近い自然光の写真にする。
- 医療者ではなく、一般患者として見える私服にする。
- ライトブラウンのロングヘアを維持する。
- 30代女性らしい現代的な私服感を維持する。白ブラウスとベージュ系パンツの組み合わせは使用しない。
- 顔、年齢感、髪型、体型、服装を大きく変えない。
- CT、MRI、レントゲン、健診の説明場面で使う場合も、不安を強めすぎない。
- キャラクターの一貫性を最優先にする。
- 実在の人物や有名人に寄せない。

## 禁止事項

- 別人化。
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
| `../_clothing_variants_20260630/PATIENT_F30_001_seasonal_summer_casual.png` | Approved seasonal summer casual clothing variant. |
| `../_clothing_variants_20260630/PATIENT_F30_001_exam_gown.png` | Approved patient examination gown variant. |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_spring_ref.png` | 春の私服参考。 |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_summer_ref.png` | 夏の私服参考。 |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_autumn_ref.png` | 秋の私服参考。 |
| `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_winter_ref.png` | 冬の私服参考。 |

## 生成用プロンプト要約

Japanese female general patient, age 32-38, photorealistic natural lighting, natural Japanese beauty, mature and approachable, elegant but relatable, looks like a working professional or mother, balanced facial proportions, slightly oval face, warm expressive eyes, natural smile, soft feminine facial features, friendly intelligent appearance, light brown long natural hair, healthy average build with good style, age-appropriate modern casual clothing, no white blouse with beige pants, pure white background, full-body character consistency, fictional person, not based on any real person or celebrity.

## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | PATIENT_F30_001 |
| Role | General patient |
| Age range | 32-38 |
| Gender | Female |
| Body type | Healthy average build with good style; not an exaggerated model body |
| Hair | Light brown long natural hair |
| Face | Mature approachable Japanese woman, balanced facial proportions, slightly oval face, warm expressive eyes, natural smile, soft feminine features |
| Personality | Warm, realistic, confident, relatable, easy to empathize with |
| Default clothing | Age-appropriate modern casual clothing; never use a white blouse with beige pants; not medical staff clothing |
| Approved corridor clothing variant for breath-hold X-ray video | White draped sleeveless/off-shoulder style top and black pants |
| Exam-room clothing variant | Simple pale medical examination gown only when explicitly in an exam-room scene |
| Approved seasonal summer casual variant | Airy ivory short-sleeve blouse or lightweight knit top, soft sage green ankle-length tapered pants, beige low-heel flats. Saved as `../_clothing_variants_20260630/PATIENT_F30_001_seasonal_summer_casual.png`. |
| Approved patient examination gown variant | Simple pale warm-gray/beige patient examination gown, loose modest short-sleeve tunic and matching easy pants, simple patient slippers. This is patient clothing, not staff scrubs. Saved as `../_clothing_variants_20260630/PATIENT_F30_001_exam_gown.png`. |
| Seasonal clothing reference set | Use the selected spring, summer, autumn, and winter private-clothing references saved under `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\`. These are clothing and season references; keep the character face identity from this Character ID. |
| Typical scenes | CT, MRI, X-ray, and health screening explanation scenes |

### Keep

- Keep the same face identity, age range, light brown long hair, healthy average build, and approachable patient feeling.
- Keep the patient as an ordinary person, not a healthcare worker.
- Use examination gown only in exam-room scenes when explicitly needed.
- Use the approved white draped top and black pants for the breath-hold X-ray corridor scenes.
- Keep anxiety mild and realistic, not exaggerated.

### Avoid

- Do not put this character in scrubs, white coat, nurse uniform, ID badge, or medical staff clothing.
- Do not use heavy makeup, gold hair, anime style, model-like glamour, beauty-ad styling, readable names, logos, or patient identifiers.
- Do not change face, age, hairstyle, body type, or clothing rules without explicit approval.
- Do not dress this character in a white blouse with beige pants.

### Generation Prompt Summary

Japanese female general patient, age 32-38, photorealistic natural lighting, natural Japanese beauty, mature and approachable, elegant but relatable, working professional or mother-like atmosphere, balanced facial proportions, slightly oval face, warm expressive eyes, natural smile, soft feminine features, friendly intelligent appearance, light brown long natural hair, healthy average build with good style, age-appropriate modern casual clothing, never a white blouse with beige pants, fictional person, not based on any real person or celebrity, character consistency critical.
