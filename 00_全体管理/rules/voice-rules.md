# ANRYCAMPANY Voice Rules

Use this file before audio generation or narration reading edits.

## Speed

- Voice speed is fixed at 1.2x unless the user explicitly requests another speed.
- Do not change to 1.1x, normal speed, or any other speed without approval.

## Reading Substitutions

Use these substitutions in voice-only narration text. Image text may keep normal kanji or English.

- 骨密度: こつみつど
- 骨密度検査: こつみつど検査
- DXA: できさ
- 乳房: にゅうぼう
- 値: あたい

For ambiguous words, prefer kana in the actual text passed to the voice engine.

## Pacing

- Use `。` for clear pauses.
- Avoid `？` when the engine stretches the ending too much; rewrite naturally.
- For contrast phrases, split with punctuation when needed.
