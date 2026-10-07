# Patient Clothing Index

患者キャラクターの服装参照先。画像生成時は年代と季節、または検査着を指定して使う。

## Common Rules

- 20代、30代、40代患者は、この索引の季節別私服または確定済み検査着を使う。
- 20代、30代、40代患者に白ブラウス＋ベージュ系パンツの組み合わせは使わない。
- 服装参考は服装と季節感の参照用。顔は各Character IDの基準顔を優先する。
- 検査着は私服差分とは別の「検査着カテゴリ」として扱い、`ANRYCAMPANY/Characters/_clothing_variants_20260630/` の確定済み画像だけを使う。
- 成人患者の非季節差分は、来院・受付用、仕事帰り用、休日・運動前後用、健診用の4カテゴリーで追加する。
- 新しい服装差分は、Character ID・カテゴリー・絶対パスをこの索引へ登録し、承認済み参照画像としてから使う。

## 同一動画内の服装固定（絶対ルール）

- 同じCharacter IDが1本の動画に出る場合、全カットで同一の承認済み服装参照画像を使う。
- 上下、羽織り、靴、アクセサリー、検査着を含め、動画途中で変更しない。
- 場面が受付・待合・検査室などに変わっても、服装は変更しない。
- 服装参照は画像構成と `production_manifest.md` に絶対パスで記録する。異なる服装のカットは不採用とし、同一服装で再生成する。

## 成人患者の私服カテゴリー

| カテゴリー | 目的 | 基本条件 |
| --- | --- | --- |
| 来院・受付用 | 予約、受付、問診票、待合 | 控えめな普段着 |
| 仕事帰り用 | 受診前後、通勤、予約変更 | きれいめカジュアル |
| 休日・運動前後用 | PET前の運動など生活場面 | 動きやすい服 |
| 健診用 | 胃部X線、健診、検査前 | 金具が少なく着脱しやすい服 |

## 検査着カテゴリ（私服とは別管理）

- 検査着は来院・受付用、仕事帰り用、休日・運動前後用、健診用の私服カテゴリーには含めない。
- 検査着を使う動画では、選択した確定済み検査着を同一動画の全カットで固定する。
- 私服を選んだ動画では、検査着へ切り替えない。検査着を選んだ動画では、私服へ切り替えない。

## PATIENT_F20_001

| 用途 | 参照画像 |
| --- | --- |
| 春の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F20_001\PATIENT_F20_001_spring_ref.png` |
| 夏の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F20_001\PATIENT_F20_001_summer_ref.png` |
| 秋の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F20_001\PATIENT_F20_001_autumn_ref.png` |
| 冬の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F20_001\PATIENT_F20_001_winter_ref.png` |
| 検査着 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F20_001_exam_gown.png` |

## PATIENT_F30_001

| 用途 | 参照画像 |
| --- | --- |
| 春の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_spring_ref.png` |
| 夏の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_summer_ref.png` |
| 秋の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_autumn_ref.png` |
| 冬の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F30_001\PATIENT_F30_001_winter_ref.png` |
| 検査着 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F30_001_exam_gown.png` |

## PATIENT_F40_001

| 用途 | 参照画像 |
| --- | --- |
| 春の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_spring_ref.png` |
| 夏の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_summer_ref.png` |
| 秋の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_autumn_ref.png` |
| 冬の私服 | `F:\ANRYCAMPANY\reel_assets\character_references\patients\PATIENT_F40_001\PATIENT_F40_001_winter_ref.png` |
| 検査着 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F40_001_exam_gown.png` |

## PATIENT_M40_001

| 用途 | 参照画像 |
| --- | --- |
| 現在の私服 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\PATIENT_M40_001\reference_sheet.png` |
| 休日・運動前後用 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\PATIENT_M40_001\PATIENT_M40_001_leisure_exercise_ref.png` |

## PATIENT_F60_001

| 用途 | 参照画像 |
| --- | --- |
| 現在の私服 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\PATIENT_F60_001\reference_sheet.png` |

## PATIENT_F10_001

| 用途 | 参照画像 |
| --- | --- |
| 現在の私服 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\PATIENT_F10_001\reference_sheet.png` |

## PATIENT_M02_001

| 用途 | 参照画像 |
| --- | --- |
| 基準服 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\PATIENT_M02_001\reference_sheet.png` |

## Other Clothing Variants

| Character ID | 参照画像 | 用途 |
| --- | --- | --- |
| NURSE_001 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\NURSE_001_navy_scrubs_pink_collar.png` | 紺色スクラブ、襟元ピンク差し色 |
| PATIENT_F20_001 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F20_001_seasonal_summer_casual.png` | 旧夏服バリアント。必要時のみ |
| PATIENT_F30_001 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F30_001_seasonal_summer_casual.png` | 旧夏服バリアント。必要時のみ |
| PATIENT_F40_001 | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F40_001_seasonal_summer_casual.png` | 旧夏服バリアント。必要時のみ |

## Contact Sheets

- 季節別患者服一覧: `F:\ANRYCAMPANY\reel_assets\character_references\patients\selected_patient_season_refs_contact_sheet.png`
- 検査着・看護師服一覧: `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\clothing_variants_contact_sheet.png`

## Readable Patient Clothing Index Addendum

This English section is canonical for the newly added exam gown variants.

| Character ID | Variant | Reference image | Use |
| --- | --- | --- | --- |
| PATIENT_F50_001 | Exam gown | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F50_001_exam_gown.png` | Light greige patient exam gown, front-view full-body reference. |
| PATIENT_F70_001 | Exam gown | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_F70_001_exam_gown.png` | Light greige patient exam gown, front-view full-body reference. |
| PATIENT_M70_001 | Exam gown | `F:\ANRYCAMPANY\ANRYCAMPANY\Characters\_clothing_variants_20260630\PATIENT_M70_001_exam_gown.png` | Light greige patient exam gown, front-view full-body reference. |
