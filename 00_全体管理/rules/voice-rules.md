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
- 方: かた
- 他にも: ほかにも
- 微調整: びちょうせい

For ambiguous or repeatedly misread words, use kana in the actual text passed to the voice engine from the first generation. If a word is still misread after one correction, avoid the problematic kanji/word in voice-only text and rewrite the spoken phrase while keeping the display text unchanged when appropriate.

## Pacing

- Use `。` for clear pauses.
- Avoid `？` when the engine stretches the ending too much; rewrite naturally.
- For contrast phrases, split with punctuation when needed.
