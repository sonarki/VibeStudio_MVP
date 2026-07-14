# Production Notes — Compromises & Items for Human Review

## Environment constraints (this session)

The remote execution environment's network policy blocks the asset CDN
(`*.cloudfront.net`), so generated media could not be downloaded into the workspace.
Consequences:

1. **Video/image binaries are not committed to the repo.** All deliverables are
   referenced by durable Higgsfield URLs + job IDs in `03_asset_manifest.json`, and are
   visible in the session's generation widgets and the Higgsfield workspace library.
2. **Frame-level visual QA could not be done by direct inspection.** Mitigations used:
   (a) every frame was generated from the same anchor reference to lock one visual
   language; (b) a scene-by-scene server-side analysis of the finished film was run and
   recorded in `06_validation_report.md`; (c) all assets are displayed in the chat for
   human review.
3. Local subtitle burn (ffmpeg) was not possible for the same reason; the burned-subtitle
   master uses the platform's server-side subtitle renderer.

## Compromises (explicit)

| # | Item | Detail | Severity |
|---|---|---|---|
| 1 | Master resolution | Gemini Omni Flash renders 720p only. The clean master was upscaled server-side (ByteDance, AIGC preset) to 2K to satisfy the ≥1920×1080 criterion. The burned-subtitle master remains 1280×720. | medium |
| 2 | Subtitle typography | The platform's burned-caption styles are handwritten/marker faces; "patrick" (legible handwritten) was chosen as closest to the film's handwritten-sentence motif. It is not the precise editorial sans of the storyboard. The clean master + `04_subtitles_en.srt` allow a custom burn later. | low |
| 3 | Narration trims | The locked narration (~231 words) cannot fit 88–94 s at its own 125–135 wpm spec. Documented minimal trims in `02_narration_final.md`; the "not built to make AI more powerful than people" sentence is not voiced (meaning carried by Block 9 + end card). | medium — review |
| 4 | Music continuity | Ambient score is generated per 10 s block by the video model from matched audio directions (minimal piano / processed strings / organic texture). Transitions between blocks may be audible; there is no single continuous score stem, and no separable music-only track. | medium — review |
| 5 | 초인류기업 pronunciation | Block 3/company name is spoken by a multilingual TTS (Seed Audio). Korean pronunciation could not be auditioned by ear in this environment; take duration is consistent with correct reading. | review by ear |
| 6 | Korean on-screen text | "From 초인류기업" appears in frames 3 and 9 (Nano Banana Pro renders CJK well, but was not visually verified in-session). | review by eye |
| 7 | Scene exports | Per-scene exports are the 9 individual block clips (URLs in manifest) — they carry ambient audio but not narration; narration WAVs are separate per block. | low |

## What I did NOT claim

Per the master prompt: a playable MP4 is not proof of creative success. The film was
assembled and machine-validated, but the six human approval questions in
`07_ACCEPTANCE_CRITERIA.md` require human eyes and ears — especially items 5 and 6
above. If any block fails visual review, its frame prompt and clip prompt are in the
manifest/plan and a single block can be regenerated and re-assembled without touching
the other eight (30 credits + 0.1 credits per redo).

## Reproducibility

- Every prompt used is recorded in the platform generation history and in this folder's
  documents (plan + manifest hold all job IDs).
- Assembly is deterministic: `explainer_video` with the ordered (video, audio) job-ID
  pairs in `03_asset_manifest.json`.
