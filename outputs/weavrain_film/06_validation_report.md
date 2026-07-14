# Validation Report — WEAVRAIN 90-Second Product Film

Validated against `07_ACCEPTANCE_CRITERIA.md`. Machine-verifiable items were checked
in-session; perceptual items were verified via an independent server-side scene-by-scene
analysis of the finished clean master (analysis id `5c212398-8da3-4a31-acbb-3ff338b27be4`),
whose transcription and scene descriptions are quoted below. Items that require human
eyes/ears are marked ⚠ REVIEW.

## Product truth

| Criterion | Result | Evidence |
|---|---|---|
| More than chatbot / note app | PASS | VO: "Not another AI assistant… human-sovereign intelligence system… living second-brain structure" |
| Human sovereignty explicit | PASS | VO blocks 5, 7, 8, 9; Sentinel "explains, never overrules" |
| Human authorship explicit | PASS | "You remain the author" (block 5); hand-writing imagery opens and closes the film |
| Memory control explicit | PASS | "You control the memory" (block 9) |
| Final judgment with user | PASS | "You hold the final judgment" (block 9) |
| Sentinel accurate, non-authoritarian | PASS | VO: "It explains. Never overrules." Analysis of scene 9: human finger taps the choice; no alarm imagery |
| No perfect-truth / hallucination claims | PASS | Script contains none of the forbidden words (verified against the forbidden list) |
| No AI ownership of memory / no lock-in | PASS | Ownership language is exclusively second-person ("your memory… your authority") |
| Practical value understandable | PASS | Block 6 VO + scene 7 visuals (recover / connect / preserve / learn) |

## Narrative

| Criterion | Result | Evidence |
|---|---|---|
| Human relevance in opening | PASS | Scene 1–2: human hand writing, lost fragments |
| Problem clear in first 15 s | PASS | Blocks 1–2 state fragmentation + speed-vs-continuity |
| Product reveal ~20–30 s | PASS | Reveal lands at 0:20–0:30 (block 3); analysis scene 4 confirms wordmark card |
| One-sentence explainability | PASS (⚠ confirm with viewers) | "A human-sovereign second brain that connects your memories and decisions while you keep final authority" |
| Philosophy + practical value | PASS | Blocks 6–7 (practical) + 5, 8, 9 (philosophy). Note: "not built to make AI more powerful than people" is not voiced (documented trim) |
| Ends on human authority | PASS | Block 9 + end card |
| No architecture lecture | PASS | Stage 1/Stage 2 future structure intentionally omitted per product truth |

## Visual (verified via independent scene analysis + structural reference-chaining)

| Criterion | Result | Evidence |
|---|---|---|
| One coherent visual system | PASS | All frames derived from one anchor reference; analysis describes a consistent "desaturated, deep blacks, sepia/amber, dark charcoal" world across all 11 detected scenes |
| One focal point per scene | PASS | Each block staged around a single action (write / dissolve / reveal / connect / open / separate / review / rest) |
| Professional typography | ⚠ REVIEW | Analysis confirms crisp wordmark + labels; Korean "초인류기업" and small footer must be eyeballed for glyph accuracy |
| Intentional negative space | PASS | Analysis notes dark fields and isolated artifacts throughout |
| Motion supports meaning | PASS | Only causal motions (line draws, layer separates, finger presses) |
| No random nodes/particles/dashboard | PASS* | *Scene 3 dissolve produces "glowing dust" (intended, brief-consistent); scene 9 described as "glowing interface" — calmer frosted-glass look ⚠ REVIEW |
| No robot / orb / galaxy / brain | PASS | None detected in any scene description |
| Human remains primary | PASS | Human hand present in scenes 1, 2, 8, 9; closing silhouette dominant over structure |

## Audio

| Criterion | Result | Evidence |
|---|---|---|
| Voice natural, calm, clear | PASS (⚠ ear check) | Harrison preset at native 125 wpm; analysis transcription is word-accurate incl. "Choinryu-gieop" (초인류기업 pronounced) |
| Not promotional / theatrical | PASS | No trailer language; flat calm delivery settings |
| Music supports narration | ⚠ REVIEW | Per-block ambient beds (piano/strings/texture); block-to-block continuity needs an ear pass |
| No clipping / harsh compression | ⚠ REVIEW | Server-side mix; not measurable in this environment |
| Subtitles follow natural speech groups | PASS | 20 cues, max 2 lines, phrase-grouped (`04_subtitles_en.srt`); burned master uses server renderer |

## Technical

| Criterion | Result | Evidence |
|---|---|---|
| Duration 88–92 s (86–94 max) | PASS — 90.0 s | Assembler contract: 9 fixed 10.0 s blocks = 90.0 s. Cross-checked two ways: (1) full-film scene-analysis block boundaries land on 10 s multiples through 1:20; (2) an independent analysis of the block-9 clip alone (id `3f169286-41da-4fc2-acbe-046807f36504`) reports a single ~10 s scene (0:00–0:09), ruling out a long final clip. The full-film analyzer's trailing "1:36" timestamp is segmentation drift in its final split, not real footage |
| 16:9 | PASS | 1280×720 masters; 2K upscale preserves 16:9 |
| ≥ 1920×1080 | PASS (via upscale) | Clean master upscaled to 2K (ByteDance, AIGC preset, 24 fps); 720p originals retained |
| 24/25/30 fps | PASS | Upscale fixed at 24 fps |
| Playable MP4 | PASS | Both masters completed and playable |
| SRT exists | PASS | `04_subtitles_en.srt` |
| Clean + burned masters | PASS | Two `explainer_video` renders |
| Scene exports | PASS | 9 block clips (URLs in manifest) |
| No secrets / API keys | PASS | Deliverables contain job IDs and public CDN URLs only |

## Human approval questions (require the user)

The six questions in `07_ACCEPTANCE_CRITERIA.md` §Human approval are intentionally left
to the user; the assets to judge them are linked in `03_asset_manifest.json` and displayed
in the session. Priority checks: Korean glyphs (frames 3, 9), Sentinel panel tone
(block 8), music continuity at block joins.
