"""Render a NodeMap dict as a self-contained HTML page.

No CDN / external requests: a small vanilla-JS force layout on <canvas>,
so it works offline and inside Streamlit's component iframe.
"""

import json

_PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Doc Node Map</title>
<style>
  html, body { margin: 0; height: 100%; background: #12161c; color: #eee;
               font-family: system-ui, sans-serif; }
  #wrap { position: relative; height: 100%; }
  canvas { display: block; width: 100%; height: 100%; }
  #hud { position: absolute; top: 8px; left: 10px; font-size: 12px;
         color: #9ab; pointer-events: none; }
  #tip { position: absolute; display: none; background: #000c; color: #fff;
         font-size: 12px; padding: 3px 7px; border-radius: 4px;
         pointer-events: none; white-space: nowrap; }
</style>
</head>
<body>
<div id="wrap">
  <canvas id="cv"></canvas>
  <div id="hud">__HUD__</div>
  <div id="tip"></div>
</div>
<script>
const DATA = __DATA__;
const cv = document.getElementById("cv"), ctx = cv.getContext("2d");
const tip = document.getElementById("tip");
let W, H;
function resize() {
  W = cv.clientWidth; H = cv.clientHeight;
  cv.width = W * devicePixelRatio; cv.height = H * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
}
window.addEventListener("resize", resize); resize();

const nodes = DATA.nodes.map((n, i) => ({
  ...n,
  x: W/2 + 120 * Math.cos(i * 2.4) * (1 + i/25),
  y: H/2 + 120 * Math.sin(i * 2.4) * (1 + i/25),
  vx: 0, vy: 0,
  r: n.type === "folder" ? 9 : 5,
}));
const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
const edges = DATA.edges
  .filter(e => byId[e.source] && byId[e.target])
  .map(e => ({ s: byId[e.source], t: byId[e.target], kind: e.kind }));

let alpha = 1, dragging = null;
function step() {
  // repulsion (O(n^2) — fine for <= ~800 nodes)
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y;
      let d2 = dx*dx + dy*dy || 1;
      if (d2 > 40000) continue;
      const f = 900 / d2;
      dx *= f; dy *= f;
      a.vx += dx; a.vy += dy; b.vx -= dx; b.vy -= dy;
    }
  }
  // springs
  for (const e of edges) {
    const rest = e.kind === "contains" ? 60 : 100;
    let dx = e.t.x - e.s.x, dy = e.t.y - e.s.y;
    const d = Math.sqrt(dx*dx + dy*dy) || 1;
    const f = 0.02 * (d - rest) / d;
    dx *= f; dy *= f;
    e.s.vx += dx; e.s.vy += dy; e.t.vx -= dx; e.t.vy -= dy;
  }
  // centering + integrate
  for (const n of nodes) {
    n.vx += (W/2 - n.x) * 0.002; n.vy += (H/2 - n.y) * 0.002;
    if (n !== dragging) { n.x += n.vx * alpha; n.y += n.vy * alpha; }
    n.vx *= 0.6; n.vy *= 0.6;
  }
  alpha = Math.max(0.05, alpha * 0.995);
}

function draw() {
  ctx.clearRect(0, 0, W, H);
  for (const e of edges) {
    ctx.strokeStyle = e.kind === "links_to" ? "#c9a227" : "#3a4656";
    ctx.lineWidth = e.kind === "links_to" ? 1.4 : 1;
    ctx.beginPath(); ctx.moveTo(e.s.x, e.s.y); ctx.lineTo(e.t.x, e.t.y); ctx.stroke();
  }
  for (const n of nodes) {
    ctx.fillStyle = n.type === "folder" ? "#4f8cc9" : "#7bc96f";
    ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, 7); ctx.fill();
    if (n.type === "folder") {
      ctx.fillStyle = "#cfd8e3"; ctx.font = "11px system-ui";
      ctx.fillText(n.label, n.x + n.r + 3, n.y + 4);
    }
  }
}

function tick() { step(); draw(); requestAnimationFrame(tick); }
tick();

function pick(mx, my) {
  let best = null, bd = 144;
  for (const n of nodes) {
    const d = (n.x-mx)**2 + (n.y-my)**2;
    if (d < bd) { bd = d; best = n; }
  }
  return best;
}
cv.addEventListener("mousemove", ev => {
  const mx = ev.offsetX, my = ev.offsetY;
  if (dragging) { dragging.x = mx; dragging.y = my; alpha = 0.4; }
  const n = pick(mx, my);
  if (n) {
    tip.style.display = "block";
    tip.style.left = (mx + 12) + "px"; tip.style.top = (my + 12) + "px";
    tip.textContent = n.id + (n.size ? ` (${(n.size/1024).toFixed(1)} KB)` : "");
  } else tip.style.display = "none";
});
cv.addEventListener("mousedown", ev => { dragging = pick(ev.offsetX, ev.offsetY); });
window.addEventListener("mouseup", () => { dragging = null; });
</script>
</body>
</html>"""


def render_html(nodemap: dict) -> str:
    """Return a full standalone HTML page for the given NodeMap dict."""
    c = nodemap.get("counts", {})
    hud = (
        f"📁 {nodemap.get('root', '')} — "
        f"{c.get('folders', 0)} folders · {c.get('docs', 0)} docs · "
        f"{c.get('edges', 0)} edges"
        + (" · ⚠ truncated" if nodemap.get("truncated") else "")
    )
    return (
        _PAGE
        .replace("__HUD__", hud)
        .replace("__DATA__", json.dumps(nodemap, ensure_ascii=False))
    )
