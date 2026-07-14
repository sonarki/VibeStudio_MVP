# WEAVRAIN — 90-Second Product Film · Production Plan (as executed)

**Product:** WEAVRAIN — a human-sovereign intelligence evolution system
**Company:** 초인류기업 (English descriptor: "a human intelligence company")
**Deliverable:** 90.0-second English product film, 16:9, narrated, with burned-subtitle and clean masters + SRT
**Pipeline:** Higgsfield MCP `video-explainer` workflow (9 fixed 10-second blocks)

## Architecture

The film is built as **9 blocks × 10.0 s = 90.0 s exactly** (inside the 88–92 s target).
Each block = one composed key frame (Nano Banana Pro) → one 10 s clip (Gemini Omni Flash,
720p, native ambient sound) → one narration take (Seed Audio, voice "Harrison") laid over
the clip at assembly (server-side `explainer_video`), voice centered in the block window.

Visual coherence is enforced structurally: **every frame after the anchor is generated with
the anchor frame (Fragmentation) as its style reference**, and every clip is generated with
its own block frame as the image reference. One visual language, one palette, one material
world across all 9 scenes.

## Style system

- Premium cinematic editorial 2.5D illustration (explicitly non-photoreal per workflow rules)
- Deep charcoal / soft black fields · warm off-white paper · restrained amber accents ·
  occasional cool gray-blue
- Tactile paper grain, translucent glass layers, precise hairline rules, generous negative space
- One focal point per shot; camera locked or single slow push-in; stillness as design
- Banned (enforced in every prompt): orb, galaxy, robot, node graph, dashboard, neon,
  particles, brain cliché, text morphing

## The three mandatory style frames

| Frame | Scene | Job ID |
|---|---|---|
| A — Fragmentation (anchor) | Block 1 | `fc282aa1-d73b-4a77-b570-fb36a9aa88fe` |
| B — Memory Threshold | Block 5 | `76ab9f4b-d8dc-4ff1-8d67-313c4e0ed6ec` |
| C — Sovereignty Sentinel | Block 8 | `b5d43e7b-023c-41ee-851c-b078865cf1a5` |

All other block frames (2, 3, 4, 6, 7, 9) derive from anchor A by image reference.

## Block map (scene ↔ storyboard)

| Block | Time | Storyboard scene | On-screen text |
|---|---|---|---|
| 1 | 0:00–0:10 | 1 — Pieces left behind | (none — handwriting only) |
| 2 | 0:10–0:20 | 2 — Speed is not continuity | "Speed is not continuity." |
| 3 | 0:20–0:30 | 3 — Product reveal | "From 초인류기업" / "WEAVRAIN" / "Not another AI assistant." |
| 4 | 0:30–0:40 | 4 — Living second-brain structure | MEMORY / CONTEXT / DECISION / CREATION / OUTCOME |
| 5 | 0:40–0:50 | 5 — The first sentence | "Begin with the first sentence only you can write." |
| 6 | 0:50–1:00 | 6 — Practical value | RECOVER CONTEXT / CONNECT MEANING / PRESERVE REASONS / LEARN FROM OUTCOMES |
| 7 | 1:00–1:10 | 7 — Discernment | FACT / INFERENCE / SUGGESTION · "Uncertainty remains visible." |
| 8 | 1:10–1:20 | 8 — Sovereignty Sentinel | "SOVEREIGNTY SENTINEL" panel · Review / Pause |
| 9 | 1:20–1:30 | 9+10 — Human authority + end card | "WEAVRAIN" · "Your memory. Your intelligence. Your authority." · footer |

## Voice

- Engine: Seed Audio 1.0 (ByteDance) via `generate_audio`
- Voice: **Harrison** (preset, male) — `573e5163-59b3-4926-aab1-951ef2985f81`
- Selection method: three candidates (Sterling, Harrison, Nora) were auditioned on the
  opening line and measured. Harrison's natural pace ≈ **125 wpm**, exactly matching the
  locked delivery spec (125–135 wpm, calm). Sterling ≈ 97 wpm and Nora ≈ 88 wpm were
  too slow for the fixed 10 s block windows.
- speech_rate 0 / loudness_rate 0 / pitch_rate 0 (fully natural delivery)
- Every take verified against the ≤ 9.5 s block-window limit via measured `durationSec`;
  overruns were re-written (minimal timing edits) and re-voiced, never time-stretched.

## Audio design

Per-clip ambient sound is generated natively by Gemini Omni Flash from per-block AUDIO
directions (minimal piano, processed strings, organic electronic texture, soft diegetic
SFX — no voice). Narration is laid over each block at assembly.

## Models used

| Purpose | Model | Cost |
|---|---|---|
| Frames (9) | `nano_banana_pro` → nano_banana_2, 1k, 16:9 | 2 cr each |
| Clips (9 × 10 s) | `gemini_omni` (Gemini Omni Flash), 720p, native audio | 30 cr each |
| Narration (9 takes + tests) | `seed_audio`, voice Harrison | 0.1 cr each |
| Assembly (clean + subtitled) | `explainer_video` (server-side) | free + 0.05 cr/block subs |
| Upscale to ≥1080p | `upscale_video` | per provider |
