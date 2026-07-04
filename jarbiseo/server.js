/**
 * JARBISEO (자비서) — Phase 2 local server
 *
 * - Scans folders listed in jarbiseo.config.json and auto-generates the BRAIN node map
 * - Serves the app (public/) at http://localhost:PORT
 * - GET  /api/brain          → node map JSON
 * - POST /api/chat           → proxies the Claude API (key lives server-side in .env)
 * - GET  /api/file?path=...  → read-only file access, whitelisted to scanPaths
 *
 * Dependencies: express + dotenv only. Node >= 18 (global fetch).
 */

'use strict';

require('dotenv').config();

const express = require('express');
const fs = require('fs');
const fsp = require('fs/promises');
const path = require('path');

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const CONFIG_PATH = process.env.JARBISEO_CONFIG || path.join(__dirname, 'jarbiseo.config.json');

const DEFAULT_CONFIG = {
  port: 3800,
  scanPaths: [],
  maxCategories: 12,
  maxChildren: 8,
  keyFileExtensions: ['.md', '.txt', '.html', '.js', '.py', '.json', '.pdf', '.docx'],
  ignoreNames: ['node_modules', '.git', '.venv', 'venv', '__pycache__', 'dist', 'build', '.next', '.cache'],
};

function loadConfig() {
  try {
    const raw = fs.readFileSync(CONFIG_PATH, 'utf8');
    return { ...DEFAULT_CONFIG, ...JSON.parse(raw) };
  } catch (err) {
    console.warn(`[config] Could not read ${CONFIG_PATH} (${err.message}) — using defaults.`);
    return { ...DEFAULT_CONFIG };
  }
}

const config = loadConfig();
const PORT = Number(process.env.PORT || config.port || 3800);
const MODEL = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-6';
const MAX_HISTORY_TURNS = 24;
const MAX_FILE_BYTES = 256 * 1024; // /api/file read cap

// Absolute, normalized whitelist roots for /api/file (and the scan itself)
const WHITELIST_ROOTS = (config.scanPaths || [])
  .map((p) => path.resolve(p))
  .filter((p) => {
    try {
      return fs.statSync(p).isDirectory();
    } catch {
      return false;
    }
  });

// ---------------------------------------------------------------------------
// BRAIN node map generation
// ---------------------------------------------------------------------------

// Node palette: gold/teal brand colors first, then harmonious dark-deck hues
const NODE_COLORS = [0xd9a441, 0x3fa7a0, 0x7c8fd0, 0xc06b5a, 0x8fbf6b, 0xb08bc9, 0x5aa3c0, 0xc9a35a];

// Fallback map used when no configured folder exists yet (mirrors Phase 1's six
// hardcoded projects so the app never starts empty).
const FALLBACK_BRAIN = [
  { id: 'elysia', name: 'ELYSIA GRACE', color: 0xd9a441, orbit: 26, speed: 0.05, keywords: ['elysia', 'grace', '엘리시아'], children: ['세계관', '캐릭터', '대본'], desc: '엘리시아 그레이스 프로젝트. (기본 노드 — 폴더 스캔이 설정되면 자동 생성 노드로 대체됩니다.)' },
  { id: 'g2r', name: 'G2R', color: 0x3fa7a0, orbit: 33, speed: 0.042, keywords: ['g2r', '지투알'], children: ['기획', '개발', '테스트'], desc: 'G2R 프로젝트. (기본 노드)' },
  { id: 'subhunter', name: '구독 헌터', color: 0x7c8fd0, orbit: 40, speed: 0.036, keywords: ['구독', '헌터', '구독헌터'], children: ['채널 리서치', '콘텐츠', '분석'], desc: '구독자 성장 전략 프로젝트. (기본 노드)' },
  { id: 'newsblog', name: '뉴스 블로그', color: 0xc06b5a, orbit: 47, speed: 0.03, keywords: ['뉴스', '블로그'], children: ['수집', '작성', '발행'], desc: '뉴스 블로그 운영. (기본 노드)' },
  { id: 'masterplan', name: '마스터플랜', color: 0x8fbf6b, orbit: 54, speed: 0.026, keywords: ['마스터플랜', '계획', '플랜'], children: ['비전', '로드맵', '분기 목표'], desc: '캡틴의 마스터플랜. (기본 노드)' },
  { id: 'channel', name: '채널 운영', color: 0xb08bc9, orbit: 61, speed: 0.022, keywords: ['채널', '운영', '유튜브'], children: ['업로드', '커뮤니티', '수익화'], desc: '채널 운영 현황. (기본 노드)' },
];

function slugify(name, index) {
  const slug = name
    .toLowerCase()
    .replace(/[^a-z0-9가-힣]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return slug || `node-${index}`;
}

async function listEntriesSafe(dir) {
  try {
    return await fsp.readdir(dir, { withFileTypes: true });
  } catch {
    return [];
  }
}

function isIgnored(name, cfg) {
  if (name.startsWith('.')) return true;
  return cfg.ignoreNames.includes(name);
}

/**
 * Scan configured roots: each top-level folder becomes a category node,
 * its subfolders + key files become child nodes.
 */
async function buildBrain() {
  if (WHITELIST_ROOTS.length === 0) {
    return { source: 'fallback', generatedAt: new Date().toISOString(), nodes: FALLBACK_BRAIN };
  }

  const nodes = [];
  let index = 0;

  for (const root of WHITELIST_ROOTS) {
    const entries = await listEntriesSafe(root);
    const categories = entries.filter((e) => e.isDirectory() && !isIgnored(e.name, config));

    for (const cat of categories) {
      if (nodes.length >= config.maxCategories) break;
      const catPath = path.join(root, cat.name);
      const subEntries = await listEntriesSafe(catPath);

      const childDirs = subEntries
        .filter((e) => e.isDirectory() && !isIgnored(e.name, config))
        .map((e) => e.name);
      const childFiles = subEntries
        .filter((e) => e.isFile() && config.keyFileExtensions.includes(path.extname(e.name).toLowerCase()))
        .map((e) => e.name);

      const children = [...childDirs, ...childFiles].slice(0, config.maxChildren);

      nodes.push({
        id: slugify(cat.name, index),
        name: cat.name,
        color: NODE_COLORS[index % NODE_COLORS.length],
        orbit: 26 + index * 7,
        speed: Math.max(0.014, 0.05 - index * 0.004),
        keywords: [cat.name, cat.name.toLowerCase(), ...children.map((c) => c.toLowerCase())].filter(Boolean),
        children,
        desc: `폴더: ${catPath} · 하위 폴더 ${childDirs.length}개, 주요 파일 ${childFiles.length}개`,
        path: catPath,
      });
      index += 1;
    }
  }

  if (nodes.length === 0) {
    return { source: 'fallback', generatedAt: new Date().toISOString(), nodes: FALLBACK_BRAIN };
  }
  return { source: 'scan', generatedAt: new Date().toISOString(), nodes };
}

// ---------------------------------------------------------------------------
// Claude API proxy
// ---------------------------------------------------------------------------

const PERSONA_SYSTEM_PROMPT = `당신은 "자비서(JARBISEO)"입니다. 캡틴(EGO Record)의 개인 AI 비서이자 세컨드 브레인입니다.

행동 규칙:
1. 사용자를 항상 "캡틴 님"이라고 부르고, 반드시 한국어로만 답합니다.
2. 차분하고 정확하며 조용히 충성스러운 수석 비서/집사의 어조를 유지합니다.
3. 답변은 음성(TTS)으로 재생되므로 기본적으로 2~5문장으로 간결하게 말하고, 요청받지 않는 한 마크다운 서식을 쓰지 않습니다.
4. 캡틴의 제1원칙: 불확실한 정보를 절대 사실처럼 말하지 않습니다. 불확실하면 "확실하지 않습니다"라고 명시적으로 밝힙니다.
5. 화면 이미지가 주어지면 화면 내용을 분석해 보고합니다.`;

async function buildSystemPrompt() {
  try {
    const brain = await buildBrain();
    const names = brain.nodes.map((n) => n.name).join(', ');
    return `${PERSONA_SYSTEM_PROMPT}\n\n현재 캡틴의 프로젝트 노드 맵: ${names}. 브리핑 요청 시 이 프로젝트들을 기준으로 보고합니다.`;
  } catch {
    return PERSONA_SYSTEM_PROMPT;
  }
}

function sanitizeMessages(messages) {
  if (!Array.isArray(messages)) return null;
  const clean = messages
    .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && m.content)
    .slice(-MAX_HISTORY_TURNS);
  if (clean.length === 0 || clean[clean.length - 1].role !== 'user') return null;
  return clean;
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

const app = express();
app.use(express.json({ limit: '25mb' })); // screen captures arrive as base64 JPEG
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/brain', async (_req, res) => {
  try {
    res.json(await buildBrain());
  } catch (err) {
    console.error('[brain]', err);
    res.status(500).json({ error: '노드 맵 생성 중 오류가 발생했습니다.' });
  }
});

app.post('/api/chat', async (req, res) => {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: '서버에 ANTHROPIC_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인해 주세요.' });
  }

  const messages = sanitizeMessages(req.body && req.body.messages);
  if (!messages) {
    return res.status(400).json({ error: '유효한 messages 배열이 필요합니다 (마지막 메시지는 user 역할).' });
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1024,
        system: await buildSystemPrompt(),
        tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 3 }],
        messages,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      console.error('[chat] Claude API error:', response.status, JSON.stringify(data).slice(0, 500));
      const msg = (data && data.error && data.error.message) || 'Claude API 호출에 실패했습니다.';
      return res.status(response.status).json({ error: msg });
    }
    res.json(data);
  } catch (err) {
    console.error('[chat]', err);
    res.status(502).json({ error: 'Claude API 서버에 연결하지 못했습니다.' });
  }
});

app.get('/api/file', async (req, res) => {
  const requested = req.query.path;
  if (!requested || typeof requested !== 'string') {
    return res.status(400).json({ error: 'path 쿼리 파라미터가 필요합니다.' });
  }

  const resolved = path.resolve(requested);
  const allowed = WHITELIST_ROOTS.some(
    (root) => resolved === root || resolved.startsWith(root + path.sep)
  );
  if (!allowed) {
    return res.status(403).json({ error: '허용된 폴더(scanPaths) 밖의 경로는 읽을 수 없습니다.' });
  }

  try {
    const stat = await fsp.stat(resolved);
    if (stat.isDirectory()) {
      const entries = await listEntriesSafe(resolved);
      return res.json({
        path: resolved,
        type: 'directory',
        entries: entries
          .filter((e) => !isIgnored(e.name, config))
          .map((e) => ({ name: e.name, type: e.isDirectory() ? 'directory' : 'file' })),
      });
    }
    if (stat.size > MAX_FILE_BYTES) {
      return res.status(413).json({ error: `파일이 너무 큽니다 (${stat.size} bytes, 최대 ${MAX_FILE_BYTES}).` });
    }
    const buf = await fsp.readFile(resolved);
    if (buf.includes(0)) {
      return res.status(415).json({ error: '바이너리 파일은 읽을 수 없습니다 (텍스트 파일만 지원).' });
    }
    res.json({ path: resolved, type: 'file', content: buf.toString('utf8') });
  } catch (err) {
    if (err.code === 'ENOENT') return res.status(404).json({ error: '파일을 찾을 수 없습니다.' });
    console.error('[file]', err);
    res.status(500).json({ error: '파일을 읽는 중 오류가 발생했습니다.' });
  }
});

app.listen(PORT, () => {
  console.log(`JARBISEO server ready → http://localhost:${PORT}`);
  console.log(`  config: ${CONFIG_PATH}`);
  if (WHITELIST_ROOTS.length === 0) {
    console.log('  scanPaths: (none valid — serving fallback node map. Edit jarbiseo.config.json)');
  } else {
    console.log(`  scanPaths: ${WHITELIST_ROOTS.join(', ')}`);
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn('  WARNING: ANTHROPIC_API_KEY is not set — /api/chat will return an error. Create .env from .env.example.');
  }
});
