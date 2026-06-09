# next_task — voice-inbox

## 미션: 파일·사진 첨부 기능 추가 (2026-05-24)

### 배경 — 워크플로우 갭

폰에서 vault 에 박는 입력 인터페이스 현황:
- ✅ **텍스트·음성** → voice-inbox (이미 잘 됨, AI 자동 분류)
- ✅ **카톡 텍스트·URL** → PC `/옵시` slash sweep
- ❌ **폰에서 파일·사진** → **갭**

옵시 모바일 미사용 결정 (안드로이드 sandbox 로 NAS vault 직접 마운트 불가 + sync 도구 거치는 부담). → voice-inbox 가 이 갭도 메우는 것이 본질 (intent.md "vault 입력 인터페이스" 정의에 부합).

### 본질

**텍스트·음성·파일·사진 all-in-one 모바일 inbox**. vault 입력 단일 진입점.

### 핵심 요구사항

1. **UI 에 첨부 버튼** — 파일·사진 선택 (모바일 카메라 / 갤러리 / 파일)
2. **안드로이드 share intent 받기** — 카톡·갤러리·기타 앱에서 "공유 → voice-inbox" 1탭으로 들어오기 (PWA + Web Share Target API)
3. **첨부물 저장 경로** — `vault/수집함/attachments/{날짜}_{원본파일명}` (WebDAV PUT 또는 Supabase Storage 경유 후 vault sync)
4. **텍스트 캡션 동시 입력** — 첨부물 + 한 줄 캡션 → AI 분류 → 노트 생성 시 첨부 wikilink 포함
5. **PC `/옵시` 처리 연계** — 수집함 첨부물은 다음 `/옵시` sweep 에서 자동 영역 분류 + wiki 정리

### 비고

- 현재 voice-inbox 코드: 음성/텍스트 → MiniMax 분류 → Notion 또는 vault. intent.md (vault) 와 CLAUDE.md (Notion) 불일치 — 작업 시작 시 어느 쪽이 현행인지 먼저 확인
- WebDAV: `https://sunq818.synology.me:5006/sunq/vault/수집함/` (이미 PC RaiDrive·rclone 으로 검증)
- 인증: 시놀로지 vault 전용 계정 신규 발급 권장 (메인 계정 평문 노출 회피)
- PWA Web Share Target 안드로이드 Chrome 지원: https://web.dev/web-share-target/

### 관련

- [intent.md](../../intent.md) — voice-inbox 페르소나·본질
- [CLAUDE.md](../../CLAUDE.md) — 현 아키텍처 (옛 Notion 흐름 명시, intent 와 갱신 갭 있음)
- 사용자 프로필 — `Z:/web/claude-sync/memory/profile/user_profile.md` "모바일 메모 워크플로우" 섹션

### 우선순위

낮음·중간 — 현 갭 우회 가능 (PC 카톡에서 다운 후 vault/수집함/ 드롭). 사용자 짜증이 보이면 우선순위 ↑.
