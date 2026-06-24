# ANRYCAMPANY Codex Guidance

This file is for Codex. Keep it concise and mostly ASCII to reduce prompt and encoding overhead.
User-facing Obsidian notes, scripts, captions, and deliverables should stay in Japanese unless the user explicitly asks otherwise.

## Core Behavior

- Reply in Japanese unless the user explicitly asks for another language.
- Before changing files, inspect relevant existing files and current git status.
- Do not overwrite, delete, move, or revert user changes unless the user clearly asks for that exact action.
- Keep changes narrowly focused on the user's latest request.
- If a request is ambiguous, choose the smallest useful action and state the assumption.
- Confirm before actions that may affect many files, published content, medical accuracy, money, accounts, or irreversible state.

## Workspace Context

- Treat this workspace as the content and operations workspace for ANRYCAMPANY.
- Treat Obsidian notes under `ANRYCAMPANY/` as the primary source of truth.
- At the start of ANRYCAMPANY work, read `README.md` and `00_*/Codex_最初に読む.md`.
- For company-wide operations, also read `00_*/ANRYCAMPANY_毎日運用マニュアル.md`.
- For task selection, next actions, ideas, or planning, check `ANRYCAMPANY/06_アイデア.md` first; `ANRYCAMPANY/99_Codex依頼メモ.md` is secondary.
- If Japanese text looks garbled in terminal output, first retry with UTF-8/BOM-safe reading before reporting a problem.
- Prefer existing folder structure, naming patterns, scripts, and asset conventions.
- Preserve Japanese filenames and existing content organization.

## Always-On Rules

- For medical or radiation-related content, avoid exaggeration and unsupported claims. Prefer calm, anxiety-reducing wording.
- In new ANRYCAMPANY Japanese text, never use the 5-kanji job title U+653E U+5C04 U+7DDA U+6280 U+5E2B.
- Always use the 7-kanji official term U+8A3A U+7642 U+653E U+5C04 U+7DDA U+6280 U+5E2B.
- Treat those terms as different qualifications/work scopes, not interchangeable wording.
- Do not silently rewrite older existing assets unless the user asks for a cleanup.
- In future hashtag suggestions and posting metadata, do not include `#ANRYCAMPANY`.

## Reel and Video Work

- For ANRYCAMPANY video/reel work, read `00_全体管理/rules/reel-core.md` before proposing or producing.
- Do not create images, frames, audio, video, or generation scripts until the required approval gate is met.
- When a person may appear in an image, read `00_全体管理/rules/character-rules.md` and the relevant Character ID note before proposing or generating that person.
- Read stage-specific rules only when needed:
  - audio/narration: `00_全体管理/rules/voice-rules.md`
  - posting notes: `00_全体管理/rules/posting-info-rules.md`
  - final completion report: `00_全体管理/rules/final-checklist.md`

## Task Discipline

- Do not invent unrelated deliverables or start broad cleanup during a narrow task.
- When generating scripts or assets after approval, verify the output exists and report the final file path.
- When editing text, keep the user's tone and intended audience unless asked to rewrite style.
- When modifying code, run the most relevant available check when practical.
- Use skills for repeatable workflows that need a fixed procedure; keep durable rules in this file or `00_全体管理/rules/`.
