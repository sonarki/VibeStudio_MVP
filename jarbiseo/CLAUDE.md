# JARBISEO (자비서) — Personal AI Assistant / Second Brain

> Project owner: 캡틴 (EGO Record). This file is the single source of truth for the JARBISEO project.
> Claude Code: read this fully before touching any code.

## What this is

A JARVIS-style personal AI assistant web app. A 3D orbital "second brain" node map visualizes the captain's projects; the assistant chats via Claude API with voice in/out, web search, and screen-capture analysis.

## Current state — Phase 1 COMPLETE

Single file: `jarbiseo-local.html` (vanilla JS + three.js r128 via cdnjs, no build step).

Working features:
- 3D orbital node map (6 hardcoded project nodes + children, drag-rotate, wheel-zoom, click → project card → briefing request)
- Chat with Claude API: model `claude-sonnet-4-6`, `web_search_20250305` tool enabled, direct browser fetch with `anthropic-dangerous-direct-browser-access: true` header, API key entered via modal (session-only, never persisted)
- STT: Web Speech API `ko-KR`
- TTS: `speechSynthesis` with voice selector; voices auto-marked ✓ (verified working) / ✕ (silent, detected by 2.5s watchdog)
- Screen share analysis: `getDisplayMedia` → JPEG frame → Claude vision
- Morning briefing button (🔔)
- Keyword-based node highlighting (mentioned projects pulse gold)
- Conversation history kept in memory, trimmed to last 24 turns

## Design system — NON-NEGOTIABLE, do not change

- Palette: bg `#060A12`, panel `#0D1520`, line `#22304a`, gold `#D9A441` (primary accent), teal `#3FA7A0` (secondary), text `#E6E9EF`, muted `#7C8798`
  (Gold + teal = the captain's established "Deep Gold + Cinematic Teal" brand grading)
- Fonts: `IBM Plex Sans KR` (body/UI), `JetBrains Mono` (HUD labels, letter-spaced uppercase)
- Aesthetic: dark space command deck; glassy panels with `backdrop-filter: blur`; the 3D brain is always the hero, UI stays as overlay

## Persona — NON-NEGOTIABLE

- Name: JARBISEO. Calm, precise, quietly loyal chief-of-staff / butler tone
- Always addresses the user as "캡틴 님", always responds in KOREAN
- Replies are spoken via TTS → default 2–5 concise sentences, no markdown formatting unless asked
- Captain's Rule #1: NEVER present uncertain information as fact; flag uncertainty explicitly

## Node map data shape (BRAIN array in the HTML)

```js
{ id, name, color (hex int), orbit (radius), speed, keywords[], children[], desc }
```

Current nodes: ELYSIA GRACE / G2R / 구독 헌터 / 뉴스 블로그 / 마스터플랜 / 채널 운영.

## Phase 2 goals — in priority order

1. **Local Node.js server (Express)**
   - Scans user-configured folders (config file, e.g. `jarbiseo.config.json` listing paths) and auto-generates the node map JSON: top-level folders → category nodes, subfolders/key files → child nodes
   - Serves the app at `http://localhost:PORT` and exposes `GET /api/brain` (node map) + `POST /api/chat` (proxies Claude API)
   - Move the API key server-side into `.env` (`ANTHROPIC_API_KEY`) — remove the browser key modal and the dangerous-direct-browser-access header
   - Add `GET /api/file?path=` (read-only, whitelist-guarded) so the assistant can answer questions about actual file contents
2. **ElevenLabs TTS** replacing browser TTS (`ELEVENLABS_API_KEY` + voice ID in `.env`); keep browser speechSynthesis as automatic fallback
3. **Long-term memory**: persist conversation log to `memory/log.json`; on startup inject a compact summary into the system prompt
4. **Model switching** by voice/text command ("두뇌를 ○○로 바꿔줘") across available Anthropic models

## Constraints

- Environment: Windows desktop, Chrome
- Keep it ONE npm project, minimal dependencies (express + dotenv is ideal; avoid heavy frameworks)
- Never break Phase 1 features while adding Phase 2
- Never commit `.env` or any API key; add `.gitignore` first
- All user-facing text in Korean; code comments in English

## Suggested first prompt for Claude Code

```
Read CLAUDE.md fully. Phase 1 is complete in jarbiseo-local.html.
Implement Phase 2 goal #1 only: create an Express server that scans
the folders listed in jarbiseo.config.json, auto-generates the BRAIN
node map, serves the app at localhost:3800, proxies the Claude API
with the key from .env, and adds a read-only whitelisted /api/file
endpoint. Refactor jarbiseo-local.html into public/index.html to
fetch the node map from /api/brain instead of the hardcoded array.
Do not change the design system or persona. When done, tell me the
exact commands to run it.
```
