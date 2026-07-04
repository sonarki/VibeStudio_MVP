# VibeStudio • MVP (Free Image → Video → LipSync)

**Truth-first notice:** This starter runs locally with stubs (no external GPUs).  
Plug in real models later via Hugging Face / Replicate / Spaces as noted below.

## Run (15 minutes)
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows) .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Integrations (replace stubs)
- **Image:** Hugging Face Inference (Flux, SDXL), or SD-WebUI API
- **Motion:** Replicate (Pika), AnimateDiff Space
- **LipSync:** SadTalker Space, Wav2Lip local inference

### Security
- Do **NOT** hardcode API keys. Use env vars or Streamlit secrets.
- Example:
```
export HF_TOKEN=...
export REPLICATE_API_TOKEN=...
```

## Pipeline
1) Generate Image → 2) Animate to Video → 3) LipSync with voice  
Keep each step independent; cache files in `outputs/`.

## Doc Node Map (local server)
Scan a documents folder and auto-build an interactive node map
(folders + documents + markdown cross-links). 100% local — nothing leaves
your machine.

```bash
export DOCS_DIR=~/Documents   # optional (defaults to ~/Documents, else CWD)
python server.py              # → http://localhost:8765/
```

- `GET /` — interactive graph (self-contained HTML, no CDN)
- `GET /api/nodemap?path=...&max_nodes=800` — graph as JSON
- Also embedded in the Streamlit app as the **🗺 Doc Map** tab.

## Known limits (be honest)
- Stubs simulate motion & I/O only.
- Real quality depends on the model endpoints you attach.
- Free GPUs may sleep; use Spaces or local GPUs for stability.