# voice-inbox — next task

> 마지막 갱신: 2026-05-18 (DESKTOP-J4M90RN, PC3)
> 마지막 세션: [session_20260518_obsidian_integration_planning.md](session_20260518_obsidian_integration_planning.md)

## 현재 상태

**기획 완료, 구현 0** — 옵시디언 통합 기획안 [기획안.html](../../기획안.html) v0.2 작성됨. 핵심 결정 모두 확정:

- 옵시디언 vault 정본 (`\\Sunq\sunq\vault\inbox\`)
- Notion 즉시 폐기
- NAS WebDAV 통로 (`sunq818.synology.me:5006`)
- 영역 1축 + 자유 태그

## 다음 단계 — Phase 1: Edge Function `/vault` 신설

순서대로:

1. **자격증명 받기** — 사용자에게 Synology WebDAV 계정·비밀번호 요청 → `set-secret.cmd synology.webdav.user <값>` / `synology.webdav.password <값>` 영속화
2. **Edge Function 코드 fetch** — Supabase MCP `get_edge_function` (project_id `chnqtrmlglqdmzqwsazm`, function `voice-inbox`)
3. **`/notion` 제거, `/vault` 신설** — WebDAV PUT, frontmatter 구성, 파일명 `YYYY-MM-DD HHmm - {title}.md`
4. **`/classify` 재작성** — 영역 3개 enum만, 항목·유형 제거, `tags: string[]` 자유 N개. AI 프롬프트에 기존 태그 컨텍스트 주입 (vault `.tag_index.md` 별도 파일이 가장 단순)
5. **voice-inbox.html UI 교체** — 영역 select 1개 + chip 자동완성. `AREA_DEPT_MAP`·`TYPES` 상수 제거
6. **배포 + 검증** — commit → push → GitHub Pages 반영 대기 → Playwright 로 실제 메모 1건 입력 → vault 에 .md 떨어지는지 확인
7. **(선택) 기존 Notion 메모 이관** — 1회성 export → frontmatter 변환 → vault 적재

## 환경

- 레포: SunQthecodemaker/voice-inbox · main
- 배포: https://sunqthecodemaker.github.io/voice-inbox/
- Edge Function: v5 (MiniMax M2.7) — Phase 1 후 v6 으로
- vault: `\\Sunq\sunq\vault\` (Synology Drive sync 운영 중)
- 차용 reference: 오픈채팅정리 프로젝트 vault append 패턴

## 메모리 시스템 트랙 (별도)

이번 세션 인지 실패 4건 → `Z:\web\메모리시스템\멍청이.md` + `Z:\web\.claude-memory\project_memory_recall_fixes.md` 트래킹.
**별도 세션에서 처리** — voice-inbox 작업과 분리.
