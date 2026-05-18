---
name: voice-inbox 옵시디언 통합 기획 + 인지실패 트래킹 도입
description: voice-inbox 활용도 저하 진단 → 옵시디언 정본 전환·Notion 폐기·자유 태그 도입 기획안(HTML) 작성. 세션 중 사용자 지적 4건으로 인지 실패 트래킹 파일 신설
---

# 2026-05-18 voice-inbox 옵시디언 통합 기획 세션

## 변경 내용

| 파일 | 위치 | 작업 |
|---|---|---|
| 기획안.html | `z:\web\voice-inbox\` | 신규 — v0.2. 다크톤 self-contained 시각화. 진단 + 결정 + 아키텍처 + 데이터 모델 + UI 변화 + 워크플로우 + Phase 3단계 + 부록 |
| 멍청이.md | `z:\web\메모리시스템\` | 신규 작성 → 이동. 이번 세션 인지 실패 4건 사례 기록 (vault 위치·메타 표현·비교 정보 부족·옵시디언 sync 자동화) |
| project_memory_recall_fixes.md | `z:\web\.claude-memory\` | 신규 — 인지 실패 패턴 누적·진단·대책 5옵션. 이번 세션 외 다른 트랙으로 처리 결정 (사용자 분리) |
| MEMORY.md | `z:\web\.claude-memory\` | 시스템 맵 섹션에 project_memory_recall_fixes 한 줄 추가 |
| voice-inbox.html | `z:\web\voice-inbox\` | **변경 없음** — 코드 수정은 Phase 1 단계에서 |
| Edge Function v5 | Supabase | **변경 없음** — Phase 1 단계에서 `/notion` 제거 + `/vault` 신설 |

## 결정 사항

| 항목 | 결정 | 대안과의 차이 |
|---|---|---|
| 저장소 정본 | **옵시디언 vault 단독** | Notion 정본·듀얼 저장 대안 폐기. 사용자 페인(검색·재발견 약함 + 아이디어 발전 안 됨)이 정확히 옵시디언 강점에 매핑됨 |
| Notion 처리 | **즉시 폐기** | 듀얼 N주 후 폐기·병행 유지 대안 폐기. 사용자 "역할이 단지 백업이라면 굳이 필요 없음" |
| vault 쓰기 통로 | NAS WebDAV (Edge Function → `\\Sunq\sunq\vault\inbox\`) | GitHub 경유 명시 거부 (사용자). 로컬 polling 패턴 (오픈채팅정리)은 즉시성 떨어져 제외 |
| 분류 모델 | **영역 1축 고정 + 자유 태그 N개** | 폐쇄형 사전(현재)·완전 자유태깅 대안 폐기. 영역 3개(병원·개인업무·개인생활)는 MOC·회고 뷰 분리에 진짜 필요, 항목·유형은 메모 내용 따라 자라남 |
| 동의어 폭주 방지 | vault 기존 태그를 AI 프롬프트 컨텍스트로 주입 + UI 자동완성 | AI 가 매번 새 태그 양산하면 nested tag 구조 무너짐 |
| 파일 단위 | 메모 1개 = `.md` 1파일, `inbox\` 1폴더에 평면 적재 | 영역별 폴더 분리 대안 폐기. 분류는 frontmatter tags 가 담당 |
| 메모리 시스템 대책 | **다른 세션·다른 폴더(`Z:\web\메모리시스템\`)에서 처리** | 본 세션 범위에서 분리 |

## 미완료 / 이슈

- **기획안만 작성, 코드 변경 0** — voice-inbox.html / Edge Function 모두 미수정
- **WebDAV 자격증명 미준비** — secrets.json 에 `synology.webdav.user` / `synology.webdav.password` 신규 박아야 함. 사용자에게 받지 않음
- **AI 프롬프트 자유 태그 N개 가이드 미작성** — 현재 v5 프롬프트는 영역/항목/유형 3개 고정. 재작성 필요
- **기존 태그 캐시 fetch 메커니즘 미설계** — Edge Function 이 vault 의 모든 .md frontmatter `tags` 를 어떻게 주기 수집? (옵션: WebDAV LIST + 파일별 frontmatter 파싱 캐시 / 옵션: 별도 인덱스 파일을 vault 안에 둠)
- **기존 Notion DB 메모 이관 미정** — 1회성 export 필요 시 별도 작업
- **PC2 가 sunq설정.md 정본 갱신** — 이 PC(PC3) 마지막 본 값 비어있음. 사용자에게 `/sunq` 권장 알림 마지막 보고에 포함

## 다음 단계 (Phase 1 — Edge Function /vault 신설)

다음 PC 가 "voice-inbox 이어서" 하면 곧장:

1. `Z:\web\.claude-setup\credentials\set-secret.cmd synology.webdav.user <값>` + `synology.webdav.password <값>` 사용자에게 받아 영속화
2. Supabase Edge Function 의 [voice-inbox v5](https://chnqtrmlglqdmzqwsazm.supabase.co/functions/v1/voice-inbox) 코드 fetch (Supabase MCP `get_edge_function`)
3. `/notion` 핸들러 제거, `/vault` 신설:
   - 입력: title, area, tags[], content, source
   - 처리: 파일명 `YYYY-MM-DD HHmm - {title}.md` 생성, frontmatter 구성
   - 출력: PUT `https://sunq818.synology.me:5006/vault/inbox/<파일명>` (Basic Auth)
4. `/classify` 핸들러: 영역 3개만 enum, 항목·유형 제거 + `tags: string[]` 자유 제안 N개. AI 프롬프트에 기존 태그 캐시 주입 가이드 추가
5. 기존 태그 캐시: 옵션 검토 후 단순한 쪽 선택 (vault 안 `.tag_index.md` 별도 파일 유지가 가장 단순)
6. voice-inbox.html: 영역 select 1개 + chip 자동완성 UI 로 교체. AREA_DEPT_MAP·TYPES 상수 제거, localStorage 데이터 마이그레이션 처리
7. 배포 → Playwright 로 https://sunqthecodemaker.github.io/voice-inbox/ 검증 (실제 메모 1건 입력 → vault 에 .md 떨어지는지 확인)

## 환경 의존성

- **레포**: SunQthecodemaker/voice-inbox (main 브랜치 — d366640 → 다음 commit 으로 기획안.html 추가)
- **Edge Function 현재**: v5 (MiniMax M2.7, `/classify` + `/notion`)
- **Notion DB**: 337f3e715c448015b711cdb3e15b3416 — Phase 1 후 폐기 (UI 삭제는 사용자 결정)
- **vault 정본**: `\\Sunq\sunq\vault\` (Synology Drive sync 운영 중, [handoff/SUNQGM_20260513-2128_ns.md:108](../../../.claude-memory/handoff/SUNQGM_20260513-2128_ns.md) 참조)
- **NAS WebDAV 인프라**: `sunq818.synology.me:5006`, 인증서·포트포워딩 준비됨 ([reference_nas_infrastructure.md](../../../.claude-memory/reference_nas_infrastructure.md))
- **오픈채팅정리 vault append 패턴**: voice-inbox 가 운영 관습 차용 ([handoff/DESKTOP-N9UPRG7_20260516-0943_ns.md](../../../.claude-memory/handoff/DESKTOP-N9UPRG7_20260516-0943_ns.md))
- **메모리시스템 폴더**: `Z:\web\메모리시스템\` — 사용자가 본 세션 중 신설. `reference_folder_structure.md` 정본 갱신 미반영 (사용자 trigger 대기)
- **세션 중 사용자 룰 추가**: `feedback_thinking_hang_recovery.md`, `feedback_no_over_explain.md`, `feedback_persist_for_future_agents.md` 외 다수가 본 세션 중 박힘 (MEMORY.md 갱신 알림으로 확인)
