# ANRYCAMPANY Codex Guidance

This file is for Codex. Keep it in English/ASCII as much as possible to reduce encoding mistakes.
User-facing Obsidian notes, scripts, captions, and deliverables should stay in Japanese unless the user explicitly asks otherwise.

## Core Behavior

- Reply in Japanese unless the user explicitly asks for another language.
- Before changing files, inspect the relevant existing files and current git status.
- Do not overwrite, delete, move, or revert user changes unless the user clearly asks for that exact action.
- Keep changes narrowly focused on the user's latest request.
- If a request is ambiguous, choose the smallest useful action and state the assumption.
- If an action may affect many files, published content, medical accuracy, money, accounts, or irreversible state, confirm before proceeding.

## Workspace Priorities

- Treat this workspace as a content and operations workspace for ANRYCAMPANY.
- Treat Obsidian notes as the primary source of truth for ANRYCAMPANY planning and operations.
- At the start of ANRYCAMPANY work, read `README.md`.
- Also read the top-level management note under the folder starting with `00_`; locate the file whose basename starts with `Codex_` and means "read first".
- For company-wide operations, also read the daily operations manual in the same top-level management folder.
- For task selection, next-action requests, video ideas, LINE stamp ideas, blog ideas, or planning, check the Obsidian vault under `ANRYCAMPANY/`, especially the ideas note whose basename starts with `06_`.
- Treat the Obsidian request inbox note whose basename starts with `99_Codex` as secondary, not the main idea source.
- If an Obsidian note appears garbled or unreadable, say so. Do not guess. Fall back to readable management notes and nearby readable files.
- Prefer existing folder structure, naming patterns, scripts, and asset conventions.
- Preserve Japanese filenames and existing content organization.
- For video, reel, LINE stamp, blog, and posting assets, check nearby files before creating new structures.
- For medical or radiation-related content, avoid exaggeration and unsupported claims. Prefer calm, anxiety-reducing wording.

## Absolute Job Title Rule

- In new ANRYCAMPANY Japanese text, never use the 5-kanji term U+653E U+5C04 U+7DDA U+6280 U+5E2B.
- Always use the 7-kanji official term U+8A3A U+7642 U+653E U+5C04 U+7DDA U+6280 U+5E2B.
- Treat those terms as different qualifications/work scopes, not interchangeable wording.
- Do not silently rewrite older existing assets unless the user asks for a cleanup.

## Absolute Video Production Rules

- For ANRYCAMPANY video work, any user phrase meaning "start video production" means: inspect Obsidian and present only the script/posting-info/image-structure proposal first.
- Do not create images, frames, audio, video, or generation scripts until the user explicitly approves the prior step.
- Required order: Obsidian check -> script proposal -> user approval -> image plan and 1-2 sample frames -> user approval -> remaining images -> user approval -> audio/video generation.
- First image work after script approval is limited to the image plan and 1-2 sample frames for user review.
- Text placement, number of images, CTA, and common assets must be confirmed before adding final text to images.
- Voice speed is fixed at 1.2x unless the user explicitly requests another speed. Do not change to 1.1x, normal speed, or any other speed without approval.
- Keep narration text around 500 Japanese characters by default.
- Keep image structures around 10 images including CTA by default. If more are needed, explain why before expanding.

## Absolute Visual Style Rule

- Do not use simple diagram-only visuals made from circles, lines, squares, triangles, arrows, or other geometric shapes as the main image style.
- The user wants realistic images for ANRYCAMPANY videos and reels.
- Prefer real-looking clinical scenes, realistic equipment, realistic people, and realistic inspection rooms.
- Use diagrams only when the user explicitly asks for a diagram, or when a small overlay is necessary to explain positioning. Even then, keep the primary visual realistic.
- Do not replace a requested realistic medical scene with abstract icons, schematic cards, or shape-based drawings.

## Absolute Character Usage Rule

- For ANRYCAMPANY video or reel production, when an image includes a person, use only registered characters under `ANRYCAMPANY/Characters/`.
- Before proposing or generating any person image, inspect the relevant Character ID note and reference images.
- Do not invent, generate, or substitute a new person or new character on your own.
- Do not create an unregistered doctor, nurse, patient, or healthcare worker, even as a background person, unless the user explicitly approves creating a new Character ID first.
- Maintain the registered character's face, age range, hairstyle, body type, clothing rules, role, and prohibited items.
- If no existing registered character fits the scene, stop at the proposal stage and ask whether to create a new Character ID. Do not generate the image first.
- This rule is absolute and applies even when making sample frames, draft images, thumbnails, or video assets.

## Task Discipline

- Restate the practical goal briefly when needed, then proceed.
- Do not invent unrelated deliverables.
- Do not start broad refactors or cleanup while doing a narrow content or script task.
- When generating scripts or assets after approval, verify the output exists and report the final file path.
- When editing text, keep the user's tone and intended audience unless asked to rewrite the style.
- When modifying code, run the most relevant available check when practical.

## Communication

- Keep updates concise and non-technical unless technical detail is needed.
- Report what changed, where it changed, and any checks that were run.
- If something cannot be verified, say that directly.

## Stable Memory

- Use Codex Memories for preferences and recurring context.
- Use this `AGENTS.md` for rules that must apply every time.
- Use Skills for repeatable workflows that need a fixed procedure.
