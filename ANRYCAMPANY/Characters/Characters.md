# Characters

ANRYCAMPANYで使う人物キャラクターの管理場所。

## 登録済み

| Character ID | 職業 | 役割 | 参照 |
| --- | --- | --- | --- |
| RT_TECH_001 | 診療放射線技師 | 診療放射線技師の安心ラボのメインキャラクター | [[RT_TECH_001/RT_TECH_001]] |
| RT_TECH_002 | 診療放射線技師 | 診療放射線技師の安心ラボのサブ候補キャラクター | [[RT_TECH_002/RT_TECH_002]] |
| DOCTOR_001 | 医師 | 診断説明と検査提案を行う医師キャラクター | [[DOCTOR_001/DOCTOR_001]] |
| NURSE_001 | 看護師 | 検査前説明と患者さんサポートを行う看護師キャラクター | [[NURSE_001/NURSE_001]] |
| PATIENT_F20_001 | 一般患者 | CT、MRI、レントゲン、健診を受ける20代女性患者キャラクター | [[PATIENT_F20_001/PATIENT_F20_001]] |
| PATIENT_F30_001 | 一般患者 | CT、MRI、レントゲン、健診を受ける30代女性患者キャラクター | [[PATIENT_F30_001/PATIENT_F30_001]] |
| PATIENT_F40_001 | 一般患者 | マンモグラフィ、CT、MRI、健診、予防検査を受ける40代女性患者キャラクター | [[PATIENT_F40_001/PATIENT_F40_001]] |
| PATIENT_F50_001 | 一般患者 | マンモグラフィ、CT、MRI、骨密度検査、健診、予防医療を受ける50代女性患者キャラクター | [[PATIENT_F50_001/PATIENT_F50_001]] |
| PATIENT_M02_001 | 一般患者 | 小児のレントゲン、CT、MRI、検査説明を受ける2才男児患者キャラクター | [[PATIENT_M02_001/PATIENT_M02_001]] |

## 運用ルール

- 画像生成や動画制作で人物を使う前に、該当Character IDの設定を確認する。
- 新しい生成では、別人化を避けるために `reference_sheet.png` を参照する。
- 新規テキストでは職業名を必ず「診療放射線技師」と書く。
- 派手なメイク、金髪、アニメ化、過度な美容広告風の表現は避ける。
- 画像差分を追加したら、各キャラクターフォルダに保存し、メモへ追記する。

## Readable Character Index

This English section is the canonical reference for Codex and image generation. Use it when terminal output, older Japanese text, or Obsidian display appears garbled.

| Character ID | Role | Use | Note |
| --- | --- | --- | --- |
| RT_TECH_001 | Diagnostic radiologic technologist | Main reassuring diagnostic radiologic technologist character | [[RT_TECH_001/RT_TECH_001]] |
| RT_TECH_002 | Diagnostic radiologic technologist | Secondary/support diagnostic radiologic technologist character | [[RT_TECH_002/RT_TECH_002]] |
| DOCTOR_001 | Physician | Physician who explains findings and supports medical decision-making | [[DOCTOR_001/DOCTOR_001]] |
| NURSE_001 | Nurse | Nurse who supports patients and explains preparation calmly | [[NURSE_001/NURSE_001]] |
| PATIENT_F20_001 | General patient, female, 20s | Patient for CT, MRI, X-ray, and health screening scenes | [[PATIENT_F20_001/PATIENT_F20_001]] |
| PATIENT_F30_001 | General patient, female, 30s | Patient for CT, MRI, X-ray, and health screening scenes | [[PATIENT_F30_001/PATIENT_F30_001]] |
| PATIENT_F40_001 | General patient, female, 40s | Patient for mammography, CT, MRI, screening, and preventive care scenes | [[PATIENT_F40_001/PATIENT_F40_001]] |
| PATIENT_F50_001 | General patient, female, 50s | Patient for mammography, CT, MRI, bone density, screening, and preventive care scenes | [[PATIENT_F50_001/PATIENT_F50_001]] |
| PATIENT_M02_001 | General pediatric patient, male, 2 years old | Pediatric patient for X-ray, CT, MRI, and examination explanation scenes | [[PATIENT_M02_001/PATIENT_M02_001]] |

## Readable Production Rules

- Before generating any person image for ANRYCAMPANY videos or reels, inspect the relevant Character ID note and reference images.
- Use only registered characters under `ANRYCAMPANY/Characters/`.
- Do not invent unregistered doctors, nurses, patients, diagnostic radiologic technologists, or background medical staff.
- In new Japanese text, write the profession as `診療放射線技師`.
- Do not use the shortened 5-kanji job title in new Japanese text.
- Keep each character's face, age range, hairstyle, body type, clothing rules, role, and prohibited items consistent.
- Do not show readable patient names, hospital names, logos, license numbers, or ID badge text.
- Avoid glamorous model-like styling, heavy makeup, gold hair, anime style, fear-heavy expressions, and excessive beauty-advertising retouching.
