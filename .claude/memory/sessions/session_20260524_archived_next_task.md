# voice-inbox — next task

> 마지막 갱신: 2026-05-20 (PC1, SUNQGM)
> 마지막 세션: [session_20260520_obsidian_accumulate_bot_split.md](session_20260520_obsidian_accumulate_bot_split.md)
> 이전: [session_20260518_obsidian_integration_planning.md](session_20260518_obsidian_integration_planning.md)

## 현재 상태

**Phase 1 보류 검토 중** — 텔레그램 봇(`Z:/web/tgbot/`) 존재 발견. 봇이 `claude.exe` subprocess 게이트웨이라 `/옵시` 슬래시 그대로 활용 가능 → voice-inbox 자체 필요성 재평가 단계.

이번 세션 산출물:
- [`intent.md`](../../intent.md) 신규 — 본질·매핑(옵션 A)·그룹 누적 결정 박힘
- `C:/Users/sunq8/.claude/commands/옵시.md` 누적 모드 추가 (PC1 로컬, NAS 미반영)

## 결정 대기 (가장 중요)

**텔레그램 봇 운영 전략** — 다음 세션에서 사용자가 셋 중 선택:

| 옵션 | 내용 |
|---|---|
| **1 (추천)** | 봇 두 개 분리: `@SunQ_memo_bot`(신규, 메모 전용·음성 STT) + `@SunQ_assist_bot`(기존, 범용) |
| 2 | 한 봇·자동 분기 (음성=메모, 텍스트=어시스턴트) |
| 3 | 한 봇·명시 트리거만 (`/메모`, `#그룹`) |

결정 후 voice-inbox Phase 1 부활/폐기도 같이 정함.

## 다음 단계 (옵션 1 가정)

1. `Z:/web/tgbot/bot.py` 코드 Read — 현재 시스템 프롬프트, `/옵시` 슬래시 호출 가능 여부, 음성 메시지(`.ogg`) 처리 단계 존재 여부 확인
2. BotFather 에서 새 봇 생성 → 토큰
3. `Z:\web\.claude-setup\credentials\set-secret.cmd telegram.bot.memo_token "<값>"`
4. `bot.py` 복제 → `bot-memo.py`. 진입점 시스템 프롬프트만 다름:
   - "텔레그램에서 온 모든 메시지는 vault 메모 입력. `#그룹명` prefix 또는 자연어 누적 지시 있으면 그 그룹에 누적, 없으면 단발 메모. `/옵시` 슬래시 호출. 명시 작업 지시(유튜브 정리 등)는 그 지시 우선"
5. `install.ps1` 에 새 Task Scheduler 항목 추가
6. 음성 메시지 STT — Whisper 로컬·Whisper API·MiniMax·기타 중 결정 후 통합
7. intent.md "결정 기록" 섹션에 봇 분리 결과 + voice-inbox Phase 1 처리 방침 추가

## 사후 처리

- **다음 `/sunq` 호출 시** `옵시.md` 슬래시(NAS 정본·sunq설정.md) 동기화 필요 — 이 세션에서 PC1 만 수정됨

## 환경

- 레포: SunQthecodemaker/voice-inbox · main
- 배포: https://sunqthecodemaker.github.io/voice-inbox/
- Edge Function: v5 (MiniMax M2.7) — Phase 1 보류로 v6 미진행
- vault: `\\Sunq\sunq\vault\` (Synology Drive sync)
- 텔레그램 봇 코드: `Z:/web/tgbot/` (별도 프로젝트)
- 봇 인증·STT 키 등 자격증명: `Z:\web\.claude-setup\credentials\secrets.json`

## 보류된 Phase 1 단계 (참고용)

봇 통합이 실측 후 부족하면 부활:

1. 자격증명 받기 (Synology WebDAV user/password)
2. Edge Function `voice-inbox` 코드 fetch
3. `/notion` 제거, `/vault` 신설 (WebDAV PUT)
4. `/classify` 재작성 (영역 3개 enum + 자유 태그) — **그룹 누적 모드 분기도 같이**
5. voice-inbox.html UI 교체 (영역 select + chip 자동완성 + 그룹 칩 추가)
6. 배포·검증
7. 기존 Notion 메모 이관(선택)
