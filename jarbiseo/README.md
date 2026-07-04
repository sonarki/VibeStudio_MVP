# JARBISEO (자비서) — Phase 2

JARVIS 스타일 개인 AI 비서. Phase 2에서 로컬 Express 서버가 추가되어 API 키가 브라우저를 떠나 서버(.env)로 이동했습니다.

## 가장 쉬운 실행 방법 (Windows)

1. 저장소를 ZIP으로 내려받아 압축을 풉니다.
2. `jarbiseo` 폴더 안의 **`자비서시작.bat`을 더블클릭**합니다.
3. 끝. 스크립트가 알아서 처리합니다:
   - Node.js가 없으면 설치 페이지를 열어 줍니다 (설치 후 다시 더블클릭)
   - 첫 실행 시 필요한 파일을 자동 설치합니다
   - API 키를 물어보고 `.env`에 안전하게 저장합니다 (최초 1회만)
   - 서버를 켜고 브라우저(http://localhost:3800)를 자동으로 엽니다

> 종료하려면 검은 콘솔 창을 닫으면 됩니다. 다음부터는 더블클릭 → 바로 실행.

**자동 업데이트:** 시작할 때마다 GitHub에서 최신 버전을 확인해 자동으로 받아옵니다. ZIP을 다시 내려받을 필요가 없습니다. (인터넷이 없으면 건너뛰고 현재 버전으로 실행 · `.env`의 API 키와 `jarbiseo.config.json`의 개인 설정은 업데이트에서 절대 덮어쓰지 않습니다)

## 수동 실행 (터미널 사용 시)

```bash
cd jarbiseo
npm install
copy .env.example .env     # 그 다음 .env를 열어 ANTHROPIC_API_KEY 입력
npm start
```

브라우저에서 **http://localhost:3800** 접속.

## 설정 — jarbiseo.config.json

```json
{
  "port": 3800,
  "scanPaths": ["C:/Users/Captain/Documents/Projects"],
  "maxChildren": 8
}
```

- `scanPaths`에 캡틴의 프로젝트 폴더 경로를 넣으면, **최상위 폴더 → 카테고리 노드**, **하위 폴더/주요 파일 → 자식 노드**로 노드 맵이 자동 생성됩니다.
- 유효한 경로가 하나도 없으면 Phase 1의 6개 기본 노드로 표시됩니다 (앱이 빈 화면으로 뜨지 않도록).
- `scanPaths`는 동시에 `/api/file`의 읽기 허용 화이트리스트입니다.

## API

| 엔드포인트 | 설명 |
|---|---|
| `GET /api/brain` | 폴더 스캔 기반 노드 맵 JSON |
| `POST /api/chat` | Claude API 프록시 (키는 서버의 `.env`에만 존재, web search 도구 포함) |
| `GET /api/file?path=...` | 읽기 전용 파일 조회 — `scanPaths` 내부 경로만 허용, 텍스트 256KB 제한 |

## Phase 1에서 달라진 점

- `jarbiseo-local.html` → `public/index.html`로 이전, 노드 맵은 `/api/brain`에서 로드
- API 키 입력 모달과 `anthropic-dangerous-direct-browser-access` 헤더 **제거** — 키는 서버 `.env`로 이동
- 나머지 Phase 1 기능 유지: 3D 궤도 노드 맵(드래그 회전/휠 줌/클릭 카드), STT(ko-KR), TTS(음성 선택 + 2.5초 무음 감지 ✓/✕), 화면 공유 분석, 아침 브리핑 🔔, 키워드 노드 하이라이트, 최근 24턴 대화 메모리
- **상시 청취 모드**: 🎤 버튼을 한 번 누르면 계속 듣습니다(다시 누르면 끔). 자비서가 말하는 동안은 자동으로 귀를 닫아 자기 목소리를 인식하지 않고, 응답 대기 중에 말한 내용은 기억했다가 이어서 전송합니다

## 보안

- `.env`는 절대 커밋하지 않습니다 (`.gitignore`에 포함).
- `/api/file`은 `scanPaths` 바깥 경로를 403으로 차단합니다.
