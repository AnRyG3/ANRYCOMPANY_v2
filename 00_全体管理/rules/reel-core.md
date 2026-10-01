# ANRYCAMPANY Reel Core Rules

Use this file for reel or short-video planning and production.

## Approval Gates

1. Obsidian check.
2. Proposal only: script, posting-info direction, CTA, and image structure.
3. After script approval: image plan and only 1-2 sample frames.
4. After sample approval: remaining images.
5. After image approval: create `production_manifest.md` in the production-unit folder and lock the approved images in cut order.
6. After the manifest check: text insertion and final text frames.
7. After telop approval: audio and video generation.

Do not create images, frames, audio, video, or generation scripts before the matching approval gate.

## Source Lock

For every new video, create `production_manifest.md` after image approval and before text insertion. It is the only allowed source list for telop, audio, and video generation.

Use this format:

```markdown
# Production Manifest

## Approved Images

| Cut | Approved input image (absolute path) | Purpose |
|---|---|---|
| 01 | `F:\\ANRYCAMPANY\\reel_assets\\...\\01.png` | hook |
```

- List every approved input image once, in final cut order, including a common end card when used.
- Do not use any image that is not listed in this manifest for telop, audio, or video generation.
- Before text insertion, compare the actual input images with the manifest. Stop generation if the count, cut order, or absolute paths differ.
- Before audio/video generation, confirm that every telop frame maps one-to-one and in the same cut order to its manifest image. Stop generation if the count, order, or source-image path differs.
- If an approved source image changes, return to image approval before replacing its manifest entry.

## Prohibited Source Areas

Never use images from the following areas as production-frame inputs for a new video:

- `reel_assets/_不採用_今後使わない`
- `reel_assets/_archive_*`
- `reel_assets/capcut_exports`
- `codex_generated_images`
- Reference-only folders, including `reel_assets/reference_photos`, `reel_assets/character_references`, and `reel_assets/ct_patient_pov_reference_cuts`

Images in `codex_generated_images` may be used only after they are explicitly promoted into the relevant production-unit folder and recorded in `production_manifest.md`. Reference-only images may support planning or character/reference checks, but cannot be production-frame inputs.

## Default Shape

- Narration: around 500 Japanese characters by default.
- Image structure: around 10 images including CTA by default.
- Explain before expanding beyond 10 images.
- Keep one telop short; move long explanations to narration.
- Confirm text placement, image count, CTA, and common assets before final text insertion.
- Avoid unsupported medical claims and anxiety-increasing wording.

## Visual Direction

- Main visuals should be realistic clinical scenes, realistic equipment, realistic people, or realistic inspection rooms.
- Do not use diagram-only visuals made from circles, lines, squares, triangles, arrows, icons, or abstract cards as the main style.
- Use diagrams only when the user asks for them or when a small overlay is necessary.
- Read `00_全体管理/rules/telop-style-rules.md` before final text insertion or text-frame generation.

## Characters

- If a person appears, use only registered characters under `ANRYCAMPANY/Characters/`.
- Read `00_全体管理/rules/character-rules.md` before proposing or generating person images.
- Before generating any person image, pass `00_全体管理/rules/character-generation-gate.md`; if the registered character identity is not locked, stop before generation.
- For planning, use `ANRYCAMPANY/Characters/_character_quickref.md` and `_patient_clothing_index.md` before opening full Character ID notes.

## Audio

- Voice speed is fixed at 1.2x unless the user explicitly requests another speed.
- Read `00_全体管理/rules/voice-rules.md` before audio generation or narration reading edits.
