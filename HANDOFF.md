# Handoff — 2026-07-27 · 하루자동화 런칭 자산 + 콘텐츠 엔진

## Done (verified)

- **하루자동화 런칭 자산 8종** — `haruauto/00~07`, 커밋 `d617e1c` 및 후속 커밋, `origin/claude/second-project-nlcds4`에 푸시됨
- **자동화 뼈대 2종 실행 검증** — 주장이 아니라 실제 로그로 확인:
  - `haruauto/templates/sheet_pipeline/logs/run.log` — dry-run + 실제 실행 모두 성공.
    엑셀 2개(6행) 취합 → 빈 행 1 제외 → 숫자 변환 실패 1건 건너뜀 → 중복 1행 제거 → 4행,
    결과 파일 `주문취합_20260727_0547.xlsx` 생성됨
  - `haruauto/templates/doc_factory/logs/run.log` — 3건 문서 생성 성공.
    재실행 시 `overwrite: false` 동작 확인(기존 파일 3건 보호·건너뜀·경고 기록)
- **아웃라이어 포맷 리서치** — vidiQ Instagram/TikTok 아웃라이어 12건 수집 (`embeddingType: format`,
  200K+ 조회, 채널 중앙값 대비 10~580배). 원자료 요약은 `haruauto/07_CONTENT_ENGINE.md` B절에 표로 보존
- **`haruauto/07_CONTENT_ENGINE.md` 신규 작성** — 무얼굴 숏폼 배포 엔진.
  포맷 3종 + 촬영 대본 8편 + 하드룰 + 중단 기준. 대본 소재는 전부 위 실제 실행 로그에서만 가져옴

## Not done / in flight

- **`CONTACT_EMAIL` 자리표시자 4개 파일에 잔존** — `01_LANDING.html` · `02_GUMROAD_KIT.md` ·
  `03_MARKETPLACE_PROPOSAL.md` · `04_SALES_SCRIPT.md`.
  **블로커: 캡틴의 신규 Gmail 주소.** 받는 즉시 일괄 치환
- **랜딩페이지 미배포** — 위 이메일 + Gumroad 링크 2개가 선행 조건
- **Gumroad 상품 미등록 / 마켓플레이스 계정 미개설** — 전부 캡틴 액션. 에이전트가 대신할 수 없음
- **숏폼 8편 미촬영** — 화면 녹화는 캡틴 로컬 환경 필요

## Decisions made by the human this session

- 하루자동화는 HookForge와 **완전히 분리된 신규 사업**. 공유 자산은 Gumroad 결제뿐
- 가격: SPRINT ₩4,900,000 / LITE ₩1,900,000, 24시간 납기 + 미달 시 전액 환불
- 동시 수주 상한 **2건**

## Standing rules added/changed

- **가짜 후기 · 가짜 고객사 로고 · 가짜 실적 숫자 절대 금지.** 신생 팀임을 먼저 밝히고
  위험을 우리가 전부 지는 방식으로 이긴다
- **24시간에 안 될 것 같으면 수주하지 않는다.** 환불 보장은 진짜로 지킨다
- (신규) **콘텐츠 화면에 나오는 로그·결과물은 전부 실제 실행에서 나온 것만 쓴다.**
  처리 시간 수치는 고객 실측이 나오기 전까지 콘텐츠에 넣지 않는다
- (신규) **납품이 콘텐츠보다 항상 우선.** 동시 수주 2건이면 업로드 전면 중단

## Next first action

**캡틴에게 3줄 회신을 받는다** (신규 Gmail 주소 + Gumroad SPRINT/LITE 링크 2개).
받는 즉시 4개 파일의 `CONTACT_EMAIL` 일괄 치환 → 랜딩페이지 배포.
그 전까지 에이전트가 진행할 수 있는 런칭 작업은 없다.

## Do-not-repeat

- **런칭 순서를 뒤집지 말 것.** 숏폼 콘텐츠(`07`)는 T+7~30 채널이고 오늘의 매출과 무관하다.
  마켓플레이스 공고 15건 지원이 끝나기 전에 콘텐츠 제작에 착수하면 오늘을 잃는다
- **글로벌 아웃라이어 데이터를 타깃 근거로 오용하지 말 것.** 수집한 12건은 영어권 계정이며
  `format` 임베딩으로 검색했다. 가져올 수 있는 것은 **포맷 구조뿐**이고,
  오디언스(국내 소상공인·중소기업 실무자)는 여기서 도출되지 않는다
- **템플릿 "동작 확인 완료"를 로그 없이 주장하지 말 것.** 근거는 `logs/run.log`다
