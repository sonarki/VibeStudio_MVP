import os
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="VibeStudio • MVP", page_icon="🎬", layout="wide")

# ---------- Banner ----------
st.markdown("""
# 🎬 VibeStudio • MVP
**Goal:** Free, modular AI studio for Image → Video → LipSync (pipeline-first)

> Truth note: This starter works locally without external GPUs. 
> Model calls are stubbed with clear TODOs for HF/Replicate/Spaces. 
> Security: Never hardcode API keys; use environment variables.
""")

# ---------- Sidebar: Pipeline & Keys ----------
with st.sidebar:
    st.header("🔐 Keys & Pipeline")
    st.markdown("Configure keys via environment variables or secrets.toml.")
    st.code("export HF_TOKEN=...  # Hugging Face\nexport REPLICATE_API_TOKEN=...")
    st.divider()
    st.subheader("Pipeline")
    st.markdown("1) Image  →  2) Motion  →  3) LipSync")
    st.caption("Keep each step independent; cache outputs between steps.")

# ---------- Utility ----------
def save_bytes(name: str, data: bytes, folder: str = "outputs"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    with open(path, "wb") as f:
        f.write(data)
    return path

def stamp(name: str, ext: str):
    return f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{name}.{ext}"

st.session_state.setdefault("last_image_path", None)
st.session_state.setdefault("last_video_path", None)
st.session_state.setdefault("last_audio_path", None)

# ---------- Tabs ----------
tab_img, tab_vid, tab_lip, tab_map = st.tabs(["🖼 Image", "🎥 Motion", "👄 LipSync", "🗺 Doc Map"])

# ----------------- Image Tab -----------------
with tab_img:
    st.subheader("🖼 Image Generator (Stable Diffusion / Flux placeholder)")
    prompt = st.text_area("Prompt", height=120, placeholder="Describe the scene…")
    col1, col2, col3 = st.columns(3)
    with col1:
        steps = st.slider("Steps", 10, 50, 28)
    with col2:
        guidance = st.slider("Guidance", 1.0, 15.0, 7.5)
    with col3:
        seed = st.number_input("Seed (optional)", min_value=0, value=0, step=1)

    st.info("TODO: Replace stub with real call (HF Inference or local SD-WebUI API).")

    if st.button("Generate Image (stub)"):
        # Stub: create a tiny PNG placeholder
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (1280, 720), (18, 22, 28))
        d = ImageDraw.Draw(img)
        text = "IMAGE PLACEHOLDER\n— replace with SD / Flux output —"
        d.text((40, 40), text, fill=(240, 240, 240))
        fn = stamp("image", "png")
        path = save_bytes(fn, img.tobytes())  # raw bytes (incorrect for PNG on purpose?)
        # fix: save properly as PNG
        path = os.path.join("outputs", fn)
        img.save(path, "PNG")
        st.session_state["last_image_path"] = path
        st.success(f"Saved: {path}")
        st.image(img, use_container_width=True)

    if st.session_state["last_image_path"]:
        st.caption(f"Last image: {st.session_state['last_image_path']}")
        st.download_button("⬇️ Download image", data=open(st.session_state["last_image_path"], "rb"), file_name=os.path.basename(st.session_state["last_image_path"]))

# ----------------- Motion Tab -----------------
with tab_vid:
    st.subheader("🎥 Motion (AnimateDiff / Pika placeholder)")
    st.caption("Input can be the last generated image or upload your own.")
    use_last = st.checkbox("Use last generated image", value=bool(st.session_state["last_image_path"]))
    upl = st.file_uploader("Or upload image", type=["png", "jpg", "jpeg"])
    seconds = st.slider("Duration (sec)", 2, 10, 5)
    st.info("TODO: Replace stub with real call (Replicate Pika / AnimateDiff).")

    if st.button("Generate Motion (stub)"):
        import numpy as np
        import imageio
        from PIL import Image

        # Choose frame source
        if use_last and st.session_state["last_image_path"]:
            src = Image.open(st.session_state["last_image_path"]).convert("RGB")
        elif upl:
            src = Image.open(upl).convert("RGB")
        else:
            st.error("No image provided.")
            st.stop()

        w, h = src.size
        frames = []
        n_frames = seconds * 8  # 8 fps placeholder
        for i in range(n_frames):
            # Simple parallax-like horizontal drift
            shift = int(5 * np.sin(i / 4.0))
            frame = Image.new("RGB", (w, h), (0, 0, 0))
            frame.paste(src, (shift, 0))
            frames.append(np.array(frame))

        fn = stamp("motion", "mp4")
        out_path = os.path.join("outputs", fn)
        imageio.mimwrite(out_path, frames, fps=8, quality=8)
        st.session_state["last_video_path"] = out_path
        st.success(f"Saved video: {out_path}")
        st.video(out_path)

    if st.session_state["last_video_path"]:
        st.download_button("⬇️ Download video", data=open(st.session_state["last_video_path"], "rb"), file_name=os.path.basename(st.session_state["last_video_path"]))

# ----------------- LipSync Tab -----------------
with tab_lip:
    st.subheader("👄 LipSync (SadTalker / Wav2Lip placeholder)")
    st.caption("Provide voice (audio) and a face (image/video).")
    face_src = st.file_uploader("Face image or video", type=["png", "jpg", "jpeg", "mp4"])
    audio_src = st.file_uploader("Voice audio", type=["wav", "mp3", "m4a"])
    st.info("TODO: Replace stub with real call (SadTalker HF Space, Wav2Lip local / API).")

    if st.button("Synthesize LipSync (stub)"):
        # Stub: simply mux audio onto last video if exists, else show message.
        if not audio_src:
            st.error("Please upload an audio file.")
            st.stop()
        if not st.session_state["last_video_path"]:
            st.warning("No generated video found. Using a black canvas placeholder.")
            # Create a blank video with the audio duration? For simplicity skip duration sync.
        # Save audio to outputs
        audio_fn = stamp("voice", "wav")
        audio_path = os.path.join("outputs", audio_fn)
        with open(audio_path, "wb") as f:
            f.write(audio_src.read())
        st.session_state["last_audio_path"] = audio_path
        st.success(f"Saved audio: {audio_path}")
        st.write("Stub complete. Replace this block with SadTalker/Wav2Lip integration.")
        if st.session_state["last_video_path"]:
            st.video(st.session_state["last_video_path"])

# ----------------- Doc Map Tab -----------------
with tab_map:
    st.subheader("🗺 Document Folder → Node Map")
    st.caption("Scan a local folder and auto-build a graph: folders + documents, "
               "with markdown cross-links. Also available as a standalone server: "
               "`python server.py` → http://localhost:8765/")
    default_dir = os.environ.get("DOCS_DIR") or os.path.expanduser("~/Documents")
    if not os.path.isdir(default_dir):
        default_dir = os.getcwd()
    folder = st.text_input("Folder to scan", value=default_dir)
    max_nodes = st.slider("Max nodes", 50, 2000, 800, step=50)

    if st.button("Scan & Build Node Map"):
        import streamlit.components.v1 as components
        from docmap.scanner import scan_folder
        from docmap.viz import render_html
        try:
            nm = scan_folder(folder, max_nodes=max_nodes).to_dict()
        except ValueError as e:
            st.error(str(e))
            st.stop()
        c = nm["counts"]
        st.success(f"Scanned {nm['root']}: {c['folders']} folders, {c['docs']} docs, "
                   f"{c['edges']} edges ({c['skipped_files']} non-doc files skipped)"
                   + (" — truncated at max nodes" if nm["truncated"] else ""))
        components.html(render_html(nm), height=620)
        import json as _json
        st.download_button("⬇️ Download nodemap.json",
                           data=_json.dumps(nm, ensure_ascii=False, indent=2),
                           file_name="nodemap.json", mime="application/json")

st.divider()
st.markdown("**Quality Gate**: Tabs visible, stub I/O working, downloads enabled, clear TODOs noted.")