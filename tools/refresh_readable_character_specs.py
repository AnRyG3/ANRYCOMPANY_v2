from pathlib import Path

ROOT = Path(r"F:\ANRYCAMPANY")
CHAR_ROOT = ROOT / "ANRYCAMPANY" / "Characters"
JP_RT = "\u8a3a\u7642\u653e\u5c04\u7dda\u6280\u5e2b"

INDEX_SECTION = f"""
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

## Readable Production Rules

- Before generating any person image for ANRYCAMPANY videos or reels, inspect the relevant Character ID note and reference images.
- Use only registered characters under `ANRYCAMPANY/Characters/`.
- Do not invent unregistered doctors, nurses, patients, diagnostic radiologic technologists, or background medical staff.
- In new Japanese text, write the profession as `{JP_RT}`.
- Do not use the shortened 5-kanji job title in new Japanese text.
- Keep each character's face, age range, hairstyle, body type, clothing rules, role, and prohibited items consistent.
- Do not show readable patient names, hospital names, logos, license numbers, or ID badge text.
- Avoid glamorous model-like styling, heavy makeup, gold hair, anime style, fear-heavy expressions, and excessive beauty-advertising retouching.
""".strip()

SPECS = {
"RT_TECH_001": f"""
## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | RT_TECH_001 |
| Role | Diagnostic radiologic technologist |
| Japanese role name for new text | {JP_RT} |
| Age | 30 |
| Gender | Female |
| Hair | Dark brown hair tied back in a low ponytail |
| Face | Japanese female, gentle oval face, soft facial features, large kind eyes, warm smile, natural beauty |
| Clothing | Navy blue medical scrubs, white medical shoes, hospital ID badge without readable text |
| Role in scenes | Main reassuring diagnostic radiologic technologist character for patient-friendly radiology explanations |
| Typical locations | Radiography room, CT room, MRI room, hospital corridor, control room, consultation support scenes |

### Keep

- Keep the same face identity, age range, low ponytail, navy scrubs, white shoes, and calm professional mood.
- Keep the character approachable, trustworthy, patient-friendly, and comforting.
- Use photorealistic medical advertising photography and realistic clinical rooms.

### Avoid

- Do not write the shortened 5-kanji job title in new Japanese text; use `{JP_RT}`.
- Do not use heavy makeup, gold hair, anime style, model-like styling, beauty-ad retouching, fear-heavy expressions, or intimidating poses.
- Do not show readable hospital names, patient names, logos, qualification numbers, license numbers, or ID badge text.
- Do not turn this character into a nurse, doctor, or patient.

### Generation Prompt Summary

Japanese female diagnostic radiologic technologist, age 30, photorealistic medical advertising photography, natural beauty, gentle oval face, soft facial features, warm smile, large kind eyes, calm and reassuring presence, dark brown hair tied back in a low ponytail, navy blue medical scrubs, white medical shoes, hospital ID badge without readable text, clean hospital environment, patient-friendly, trustworthy, comforting, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
"RT_TECH_002": f"""
## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | RT_TECH_002 |
| Role | Diagnostic radiologic technologist |
| Japanese role name for new text | {JP_RT} |
| Age | 31 |
| Gender | Female |
| Hair | Dark brown hair tied back in a low ponytail |
| Face | Warm Japanese female face, soft features, large kind eyes, reassuring smile |
| Clothing | Navy blue medical scrubs, white shoes, hospital ID badge without readable text |
| Role in scenes | Secondary/support diagnostic radiologic technologist character for X-ray, CT, MRI, and patient reassurance scenes |
| Typical locations | Radiology rooms, control rooms, examination rooms, hospital corridors |

### Keep

- Keep the same face identity, low ponytail, navy scrubs, white shoes, and calm professional mood.
- Keep the character approachable, trustworthy, and comforting.
- Use realistic radiology rooms, control rooms, examination rooms, or hospital corridors.

### Avoid

- Do not write the shortened 5-kanji job title in new Japanese text; use `{JP_RT}`.
- Do not use heavy makeup, gold hair, anime style, model-like styling, fear-heavy expressions, readable names, logos, or ID badge text.
- Do not turn this character into a nurse, doctor, or patient.

### Generation Prompt Summary

Japanese female diagnostic radiologic technologist, age 31, photorealistic clinical photography, warm reassuring Japanese face, soft features, large kind eyes, gentle smile, dark brown low ponytail, navy blue medical scrubs, white shoes, hospital ID badge without readable text, realistic radiology room, trustworthy and patient-friendly, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
"DOCTOR_001": """
## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | DOCTOR_001 |
| Role | Physician |
| Age range | 40-45 |
| Gender | Male |
| Body type | Average build |
| Hair | Short black hair, neat and professional |
| Face | Japanese male physician, intelligent, warm, trustworthy, calm |
| Clothing | White coat, light blue dress shirt, dark trousers, hospital ID badge without readable text |
| Role in scenes | Explains diagnosis, answers patient questions, recommends or explains examinations, supports decision-making |
| Works with | RT_TECH_001, RT_TECH_002, NURSE_001 |

### Keep

- Keep the same face identity, age range, short black hair, white coat, light blue shirt, and calm professional mood.
- Keep explanations kind, concise, and reassuring.
- Use realistic hospital consultation rooms, corridors, or explanation scenes.

### Avoid

- Do not use flashy hair, heavy cosmetic retouching, anime style, fear-heavy expressions, readable names, logos, or ID badge text.
- Do not turn this character into a nurse, patient, or diagnostic radiologic technologist.

### Generation Prompt Summary

Japanese male physician, age 40-45, photorealistic hospital photography, intelligent warm trustworthy face, calm expression, short neat black hair, average build, white coat, light blue dress shirt, dark trousers, hospital ID badge without readable text, realistic consultation room or hospital corridor, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
"NURSE_001": """
## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | NURSE_001 |
| Role | Nurse |
| Age range | 28-34 |
| Gender | Female |
| Body type | Healthy average build |
| Hair | Dark brown hair, neatly tied in a professional low bun |
| Face | Warm Japanese female face, soft rounded features, gentle jawline, friendly eyes |
| Clothing | Modern pastel blue nurse scrubs, white medical shoes, hospital ID badge without readable text |
| Role in scenes | Patient support, examination preparation guidance, reassurance, calm explanations |
| Works with | RT_TECH_001, RT_TECH_002, DOCTOR_001 |

### Keep

- Keep the same face identity, low bun hairstyle, pastel blue scrubs, white shoes, and warm expression.
- Keep the mood reassuring, practical, and professional.
- Use photorealistic medical photography.

### Avoid

- Do not use heavy makeup, gold hair, model-like styling, anime style, fear-heavy expressions, or dramatic poses.
- Do not show readable names, logos, license numbers, or ID badge text.
- Do not change this character into a doctor, patient, or diagnostic radiologic technologist.

### Generation Prompt Summary

Japanese female nurse, age 28-34, photorealistic medical photography, warm friendly Japanese face, soft rounded features, gentle jawline, friendly eyes, dark brown hair in a professional low bun, modern pastel blue nurse scrubs, white medical shoes, hospital ID badge without readable text, calm patient support scene, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
"PATIENT_F20_001": """
## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | PATIENT_F20_001 |
| Role | General patient |
| Age range | 22-28 |
| Gender | Female |
| Body type | Healthy average build |
| Hair | Dark brown, medium-length, natural shoulder-length look with bangs |
| Face | Natural Japanese young adult, slightly oval small face, clear healthy skin, refined features, large natural eyes, gentle jawline |
| Personality | Friendly, relatable, slightly nervous about examinations, easy for patients to empathize with |
| Default clothing | Casual everyday clothing, not medical clothing |
| Approved clothing variant for chest X-ray abdominal pain video | Loose oversized white summer shirt, bright light blue wide-leg denim pants, simple casual sandals |
| Typical scenes | CT, MRI, X-ray, and health screening explanation scenes |

### Keep

- Keep the same face identity, age range, hairstyle, body type, and approachable patient feeling.
- Keep the patient as an ordinary person, not a healthcare worker.
- Keep expressions mild and realistic; anxiety should be understandable but not excessive.
- Use photorealistic natural lifestyle or clinical photography.

### Avoid

- Do not put this character in scrubs, white coat, nurse uniform, hospital gown, ID badge, or other medical staff clothing unless explicitly approved.
- Do not make the face look like a fashion model, celebrity, anime character, or unrelated person.
- Do not use heavy makeup, gold hair, dramatic fear, readable names, logos, or patient identifiers.

### Generation Prompt Summary

Japanese female general patient, age 22-28, photorealistic natural lighting, natural Japanese young adult, slightly oval small face, clear healthy skin, refined features, large natural eyes, gentle jawline, dark brown medium-length shoulder-length hair with bangs, healthy average build, casual everyday clothing, friendly relatable patient, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
"PATIENT_F30_001": """
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
| Default clothing | Soft neutral modern casual clothing; white blouse, beige pants, natural-color shoes; not medical staff clothing |
| Approved corridor clothing variant for breath-hold X-ray video | White draped sleeveless/off-shoulder style top and black pants |
| Exam-room clothing variant | Simple pale medical examination gown only when explicitly in an exam-room scene |
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

### Generation Prompt Summary

Japanese female general patient, age 32-38, photorealistic natural lighting, natural Japanese beauty, mature and approachable, elegant but relatable, working professional or mother-like atmosphere, balanced facial proportions, slightly oval face, warm expressive eyes, natural smile, soft feminine features, friendly intelligent appearance, light brown long natural hair, healthy average build with good style, casual modern clothing in soft neutral colors, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
"PATIENT_F40_001": """
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
| Default clothing | Modern casual clothing; white blouse, greige trousers, calm shoes; not medical staff clothing |
| Typical scenes | Mammography, CT, MRI, health screening, and preventive examination scenes |

### Keep

- Keep the same face identity, age range, shoulder-length long bob, healthy average build, and elegant mature patient feeling.
- Keep this character clearly in her 40s; not too young and not idol-like.
- Keep the patient as an ordinary person, not a healthcare worker.
- Keep anxiety mild and realistic, not exaggerated.

### Avoid

- Do not put this character in scrubs, white coat, nurse uniform, ID badge, or medical staff clothing.
- Do not use heavy makeup, gold hair, anime style, cute idol styling, model-like glamour, beauty-ad styling, readable names, logos, or patient identifiers.
- Do not change face, age, hairstyle, body type, or clothing rules without explicit approval.

### Generation Prompt Summary

Japanese female general patient, age 42-48, photorealistic natural lighting, elegant mature Japanese woman, healthy attractive appearance, sophisticated natural beauty, working professional, confident and composed, slightly longer oval face, defined facial structure, expressive intelligent eyes, refined nose, natural smile, mature feminine appearance, dark brown shoulder-length long bob just above shoulders, healthy stylish average build, modern casual clothing, white blouse, greige trousers, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
"PATIENT_F50_001": """
## Readable Canonical Spec

This English section is canonical for Codex and image generation. Use it when older Japanese text or terminal output appears garbled.

| Field | Canonical value |
| --- | --- |
| Character ID | PATIENT_F50_001 |
| Role | General patient |
| Age range | 52-58 |
| Gender | Female |
| Body type | Healthy average build, active adult impression |
| Hair | Dark brown short bob, chin-length to jaw-length, practical modern hairstyle |
| Face | Elegant sophisticated Japanese woman, healthy natural aging, slightly longer oval face, defined facial structure, intelligent expressive eyes, natural smile, subtle smile lines |
| Personality | Calm, confident, realistic, intelligent, approachable, health-conscious |
| Default clothing | Modern neutral casual clothing; pale neutral cardigan, white inner top, light gray pants, comfortable shoes; not medical staff clothing |
| Typical scenes | Mammography, CT, MRI, bone density examinations, health screening, and preventive healthcare scenes |

### Keep

- Keep the same face identity, age range, short bob, healthy average build, and mature approachable patient feeling.
- Keep this character clearly in her 50s; not too young and not celebrity-like.
- Keep the patient as an ordinary person, not a healthcare worker.
- Keep anxiety mild and realistic, not exaggerated.

### Avoid

- Do not put this character in scrubs, white coat, nurse uniform, ID badge, or medical staff clothing.
- Do not use heavy makeup, gold hair, anime style, model-like glamour, beauty-ad styling, readable names, logos, or patient identifiers.
- Do not change face, age, hairstyle, body type, or clothing rules without explicit approval.

### Generation Prompt Summary

Japanese female general patient, age 52-58, photorealistic natural lighting, elegant sophisticated Japanese woman, healthy attractive appearance, confident and graceful, health-conscious professional or active adult, natural mature beauty, slightly longer oval face, well-defined facial structure, intelligent expressive eyes, natural smile, refined facial features, healthy natural aging, subtle smile lines, dark brown short bob, chin-length to jaw-length hair, healthy average build, modern neutral casual clothing, cardigan, white inner top, light gray pants, fictional person, not based on any real person or celebrity, character consistency critical.
""".strip(),
}

START_MARKERS = ["## Readable Character Index", "## Readable Canonical Spec"]


def replace_or_append(path: Path, marker: str, section: str) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    idx = text.find(marker)
    if idx >= 0:
        text = text[:idx].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")

replace_or_append(CHAR_ROOT / "Characters.md", "## Readable Character Index", INDEX_SECTION)
for char_id, section in SPECS.items():
    replace_or_append(CHAR_ROOT / char_id / f"{char_id}.md", "## Readable Canonical Spec", section)

# Replace the old helper script so future runs produce the corrected readable sections.
helper = ROOT / "tools" / "append_readable_character_specs_20260620.py"
helper.write_text(
    "from pathlib import Path\n"
    "import runpy\n\n"
    "# Compatibility wrapper. The canonical implementation is refresh_readable_character_specs.py.\n"
    "runpy.run_path(str(Path(__file__).with_name('refresh_readable_character_specs.py')), run_name='__main__')\n",
    encoding="utf-8",
    newline="\n",
)

# Keep a readable Obsidian note explaining the encoding policy.
encoding_note = ROOT / "ANRYCAMPANY" / ("Codex_" + "\u6587\u5b57\u5316\u3051\u5bfe\u7b56" + "_2026-06-20.md")
NOTE_TEXT = """---
title: Codex \u6587\u5b57\u5316\u3051\u5bfe\u7b56 2026-06-20
date: 2026-06-20
tags:
  - codex
  - encoding
  - characters
---

# Codex \u6587\u5b57\u5316\u3051\u5bfe\u7b56 2026-06-20

## \u76ee\u7684

\u4e00\u90e8\u306e\u30bf\u30fc\u30df\u30ca\u30eb\u8868\u793a\u3084\u30c4\u30fc\u30eb\u51fa\u529b\u3067\u306f\u3001\u65e5\u672c\u8a9e\u304c\u6587\u5b57\u5316\u3051\u3057\u3066\u898b\u3048\u308b\u3053\u3068\u304c\u3042\u308a\u307e\u3059\u3002\u5b9f\u30d5\u30a1\u30a4\u30eb\u304cUTF-8\u3067\u6b63\u3057\u304f\u4fdd\u5b58\u3055\u308c\u3066\u3044\u3066\u3082\u3001\u8868\u793a\u74b0\u5883\u306e\u554f\u984c\u3067\u8aad\u3081\u306a\u3044\u5834\u5408\u304c\u3042\u308a\u307e\u3059\u3002

\u305d\u306e\u305f\u3081\u3001ANRYCAMPANY\u306e\u30ad\u30e3\u30e9\u30af\u30bf\u30fc\u60c5\u5831\u306b\u306f\u3001Codex\u3068\u753b\u50cf\u751f\u6210\u304c\u78ba\u5b9f\u306b\u8aad\u3081\u308b\u82f1\u8a9e\u306e\u6b63\u672c\u30bb\u30af\u30b7\u30e7\u30f3\u3092\u8ffd\u52a0\u3057\u307e\u3059\u3002

## \u30ad\u30e3\u30e9\u30af\u30bf\u30fc\u78ba\u8a8d\u306e\u512a\u5148\u9806\u4f4d

1. \u5404Character ID\u30ce\u30fc\u30c8\u306e `Readable Canonical Spec`
2. `reference_sheet.png` \u3068\u5404\u53c2\u7167\u753b\u50cf
3. \u65e5\u672c\u8a9e\u306e\u57fa\u672c\u8a2d\u5b9a\u30bb\u30af\u30b7\u30e7\u30f3

## \u7d76\u5bfe\u30eb\u30fc\u30eb

- \u4eba\u7269\u753b\u50cf\u3092\u4f5c\u308b\u524d\u306b\u3001\u8a72\u5f53Character ID\u30ce\u30fc\u30c8\u3068\u53c2\u7167\u753b\u50cf\u3092\u78ba\u8a8d\u3059\u308b\u3002
- \u767b\u9332\u6e08\u307f\u30ad\u30e3\u30e9\u30af\u30bf\u30fc\u3060\u3051\u3092\u4f7f\u3046\u3002
- \u80cc\u666f\u4eba\u7269\u3067\u3082\u672a\u767b\u9332\u306e\u533b\u5e2b\u3001\u770b\u8b77\u5e2b\u3001\u60a3\u8005\u3001\u8a3a\u7642\u653e\u5c04\u7dda\u6280\u5e2b\u3092\u4f5c\u3089\u306a\u3044\u3002
- \u65b0\u3057\u3044\u65e5\u672c\u8a9e\u30c6\u30ad\u30b9\u30c8\u3067\u306f\u8077\u696d\u540d\u3092\u5fc5\u305a\u300c\u8a3a\u7642\u653e\u5c04\u7dda\u6280\u5e2b\u300d\u3068\u66f8\u304f\u3002
- \u77ed\u7e2e\u8868\u8a18\u306e5\u6f22\u5b57\u8077\u7a2e\u540d\u306f\u65b0\u898f\u5236\u4f5c\u7269\u3067\u306f\u4f7f\u308f\u306a\u3044\u3002
- \u8aad\u3081\u308b\u60a3\u8005\u540d\u3001\u75c5\u9662\u540d\u3001\u30ed\u30b4\u3001\u8cc7\u683c\u756a\u53f7\u3001ID\u30d0\u30c3\u30b8\u6587\u5b57\u306f\u51fa\u3055\u306a\u3044\u3002

## \u4eca\u56de\u6574\u5099\u3057\u305f\u5834\u6240

- [[Characters/Characters]]
- [[Characters/RT_TECH_001/RT_TECH_001]]
- [[Characters/RT_TECH_002/RT_TECH_002]]
- [[Characters/DOCTOR_001/DOCTOR_001]]
- [[Characters/NURSE_001/NURSE_001]]
- [[Characters/PATIENT_F20_001/PATIENT_F20_001]]
- [[Characters/PATIENT_F30_001/PATIENT_F30_001]]
- [[Characters/PATIENT_F40_001/PATIENT_F40_001]]
- [[Characters/PATIENT_F50_001/PATIENT_F50_001]]

## \u88dc\u8db3

Obsidian\u672c\u6587\u305d\u306e\u3082\u306e\u304c\u58ca\u308c\u3066\u3044\u308b\u5834\u5408\u306f\u3001\u5143\u60c5\u5831\u3092\u63a8\u6e2c\u3057\u3066\u4e0a\u66f8\u304d\u305b\u305a\u3001\u8aad\u3081\u308b\u88dc\u8db3\u30bb\u30af\u30b7\u30e7\u30f3\u3092\u8ffd\u52a0\u3057\u3066\u5fa9\u65e7\u3057\u307e\u3059\u3002
"""
encoding_note.write_text(NOTE_TEXT, encoding="utf-8", newline="\n")

print("refreshed readable character specs and encoding note")
