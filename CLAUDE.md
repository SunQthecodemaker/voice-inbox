# ⚠️ 프로젝트 식별: **voice-inbox**

> 이 디렉토리 = `z:/web/voice-inbox/`. 음성/텍스트 → AI 분류 → Notion 저장 시스템.
> 다른 프로젝트(offapp·모바일진단서 등)와 **분리된 프로젝트**임.
>
> **"마지막 작업", "이어서 해줘" 등 요청 시 처리 순서:**
> 1. ✅ `.claude/memory/sessions/` 의 가장 최근 1개 본문을 명시 Read — 그 내용 기준
> 2. ✅ 추가 컨텍스트는 [`.claude/memory/`](./.claude/memory/) 안의 다른 세션 본문 / intent.md 참조
> 3. ❌ 전역 MEMORY "최근 세션" 시간순 최상단만 보고 판단 금지

---

# voice-inbox — 작업 컨텍스트

> ℹ️ 공통 절대 규칙은 `~/.claude/CLAUDE.md`에 있고 자동 로드됩니다.

## 프로젝트 정보

- **경로**: `Z:/web/voice-inbox/`
- **목적**: 음성/텍스트 메모 → AI 자동 분류 → Notion 저장
- **레포**: `SunQthecodemaker/dental-ai-coder`
- **사이트**: https://sunqthecodemaker.github.io/voice-inbox/
- **AI 모델**: MiniMax M2.7 (Claude API 금지)

---

## 아키텍처

- **프론트엔드**: `voice-inbox.html` (GitHub Pages)
  - 음성인식: 브라우저 Web Speech API (서버 비용 0)
- **백엔드**: Supabase Edge Function (v9)
  - URL: `https://chnqtrmlglqdmzqwsazm.supabase.co/functions/v1/voice-inbox`
  - `/classify` → MiniMax M2.7 AI 분류
  - `/notion` → Notion API 저장
  - `/migrate` → 옛 row → 컨테이너 분배 (일회성, 재호출 안전)
- **저장소**: Notion DB (ID: `337f3e715c448015b711cdb3e15b3416`)
  - 컬럼: 제목 / 영역 / 항목 / 유형 / 내용 / 날짜 / 상태
  - 분류 체계: **영역**(병원/개인업무/개인생활) × **항목**(진료실/데스크/기공실/마케팅/경영/개발/학습/강의준비/건강/가족/기타) × **유형**(할일/일정/아이디어)

---

## Notion 저장 방식 (2026-04-27, Edge Function v8+)

**항목별 누적 페이지 방식.** 매 입력마다 새 row 생성 → 항목별 컨테이너 페이지 하나에 블록 누적.

- 컨테이너 제목: `📂 {영역} · {항목}` (예: `📂 병원 · 진료실`)
  - "기타"가 영역마다 있어서 disambiguation 위해 영역+항목 조합
- 컨테이너 식별: 상태 = "컨테이너"
- `/notion` 핸들러 흐름:
  1. DB query로 제목 == 컨테이너 제목 검색
  2. 있으면 그 페이지 children에 PATCH로 블록 append
  3. 없으면 컨테이너 페이지 신규 생성 후 첫 블록 추가
- 블록 형식:
  - 유형 = 할일 → `to_do` 블록 (체크박스)
  - 유형 = 일정 → `bulleted_list_item` + 📅
  - 유형 = 아이디어 → `bulleted_list_item` + 💡
  - 내용: `[MM/DD HH:mm] {아이콘} 제목 — 내용본문` (KST, 제목 bold)

---

## 완료 상태

- Step 1~3 ✅ (2026-04-07)
- Step 4 ✅ 분류 체계 재설계 (2026-04-11) — 영역/항목/유형 3단계
- Step 5 ✅ 항목별 누적 페이지 (2026-04-27) — Edge Function v8
- Step 6 ✅ 기존 데이터 마이그레이션 (2026-04-27) — Edge Function v9
  - 옛 row 10개 → 컨테이너 6개 분배 후 원본 archived

---

## 다음 작업 후보

- 누적 기록 기반 Q&A 기능 (사용자 요청, 미착수)
  - 방식 1 추천: 질문 → Notion DB query → LLM 요약 응답
  - 현재 데이터 규모(개인 메모)에서는 벡터 검색 없이 직접 query+LLM 충분

---

## 자격증명

```cmd
%USERPROFILE%\.claude\setup\credentials\get-secret.cmd github.pat
%USERPROFILE%\.claude\setup\credentials\get-secret.cmd minimax.api_key
```

---

**Why:** 빠른 메모 입력 → 자동 정리/분류 워크플로우 구축
