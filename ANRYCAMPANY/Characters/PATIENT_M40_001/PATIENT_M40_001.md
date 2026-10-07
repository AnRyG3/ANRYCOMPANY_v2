# PATIENT_M40_001

![[reference_sheet.png]]

## 登録状態

- ステータス: 採用済み
- 採用日: 2026-10-04
- 管理一覧: [[Characters]]

## 基本設定

| 項目 | 内容 |
| --- | --- |
| Character ID | PATIENT_M40_001 |
| 役割 | 一般患者 |
| 年齢 | 35〜45歳 |
| 性別 | 男性 |
| 体型 | 健康的な平均体型 |
| 髪型 | 清潔感のある短い黒髪、前髪は自然に整える |
| 服装 | チャコールグレーのカーディガン、淡いブルーグレーのシャツ、ネイビーのスラックス、黒い靴 |
| 主な用途 | PET、胃部X線、CT、MRI、手術歴、予約前、仕事帰り、運動習慣のある生活場面 |

## 外見

- 日本人男性。
- 実写に近い、自然で親しみやすい顔立ち。
- 落ち着いた目元と、控えめで温かい笑顔。
- 派手さのない、日常の検査受診者として自然な清潔感。
- 不安を強調せず、質問や確認をしやすい雰囲気。

## 画像生成で守ること

- `reference_sheet.png` と同じ登録人物として扱う。
- 実写に近い医療広報写真の質感にする。
- 顔、年齢感、髪型、体型を大きく変えない。
- 患者として描き、医療者の制服・IDバッジ・業務動作を使わない。
- 新しい私服差分は、事前に服装参照を登録してから使う。
- 読める氏名・病院名・ロゴを入れない。

## 禁止事項

- 別人化。
- 白衣、スクラブ、聴診器、医療者用IDバッジ。
- 医学的な説明、受付業務、医療処置を行う場面。
- 派手な髪色、アニメ化、モデル風・美容広告風の演出。
- 読める病院名、ロゴ、氏名、資格証番号。
- 不安をあおる表情や威圧的なポーズ。

## 保存画像

| ファイル | 用途 |
| --- | --- |
| `reference_sheet.png` | 登録基準画像。以後の患者場面で顔・髪型・体型を固定するための参照。 |
| `PATIENT_M40_001_leisure_exercise_ref.png` | 承認済み休日・運動前後用服装。チャコールグレーの軽量ランニングジャケット、濃紺の長袖トップ、黒いテーパードパンツ、黒いランニングシューズ。 |

## Readable Canonical Spec

| Field | Canonical value |
| --- | --- |
| Character ID | PATIENT_M40_001 |
| Role | General patient |
| Age range | 35-45 |
| Gender | Male |
| Body type | Healthy average build |
| Hair | Short neat black hair, naturally styled fringe |
| Face | Warm, approachable Japanese male face with calm eyes and a modest smile |
| Default clothing | Charcoal gray cardigan, pale blue-gray shirt, navy slacks, black shoes |
| Typical scenes | PET, upper GI X-ray, CT, MRI, surgical-history, appointment, workday, and exercise-habit scenes |

### Keep

- Keep the same registered face identity, age range, short black hairstyle, and average body type.
- Use photorealistic medical communications photography with a calm, everyday mood.
- Keep this character a patient, never a medical professional or reception staff member.

### Avoid

- Do not create a different person, a doctor, nurse, diagnostic radiologic technologist, or receptionist.
- Do not use white coats, scrubs, stethoscopes, medical staff ID badges, heavy styling, or intimidating expressions.
- Do not show readable names, hospital names, logos, or ID badge text.

### Generation Prompt Summary

PATIENT_M40_001, same registered person, no new person, no substitute face. Use the registered reference image. Fictional Japanese male general patient, age 35-45, short neat black hair, healthy average build, calm approachable face, charcoal gray cardigan over a pale blue-gray shirt, navy slacks, black shoes, photorealistic medical communications photography, no other people unless explicitly approved, no readable text, logos, or watermark.
