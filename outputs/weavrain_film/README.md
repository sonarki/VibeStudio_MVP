# WEAVRAIN — 90-Second Product Film

Final deliverables for the WEAVRAIN product film (초인류기업), produced from the
`WEAVRAIN_Claude_90s_Product_Film` brief package.

## Watch

| Master | Link |
|---|---|
| **Clean master, 2K, 24 fps (primary)** | [MP4](https://d8j0ntlcm91z4.cloudfront.net/user_2wX3UthAZov98dVbNmHugZwVghT/hf_20260714_050048_f119f1b0-a5f8-4920-a7cc-406cdda5e9b6.mp4) |
| Clean master, 720p (original render) | [MP4](https://d8j0ntlcm91z4.cloudfront.net/user_2wX3UthAZov98dVbNmHugZwVghT/hf_20260714_045848_f709e320-abcb-47d2-a3d1-78b735e360e7.mp4) |
| Burned English subtitles, 720p | [MP4](https://d8j0ntlcm91z4.cloudfront.net/user_2wX3UthAZov98dVbNmHugZwVghT/hf_20260714_045908_4c7d8d96-ade4-4141-96de-af12bd09f94e.mp4) |

Duration 90.0 s · 16:9 · English narration (voice: Harrison, Seed Audio) · 9 scenes

## Files

- `01_production_plan.md` — pipeline, style system, block map, models, voice selection
- `02_narration_final.md` — the 9 voiced narration blocks + documented timing edits
- `03_asset_manifest.json` — every job ID and URL (frames, clips, voice takes, masters)
- `04_subtitles_en.srt` — English subtitles (block-centered timing, 2-line phrase groups)
- `05_production_notes.md` — compromises and items flagged for human review
- `06_validation_report.md` — acceptance-criteria results with evidence

## Regenerating a single scene

Each scene is an independent block: regenerate its frame and/or clip (prompts are in the
platform history; IDs in the manifest), re-voice if needed, and re-run the `explainer_video`
assembly with the updated job ID — the other eight blocks are untouched.
