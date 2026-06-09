#!/usr/bin/env python3
"""Organize SunQ voice-inbox raw notes into wiki collection notes.

Input:  vault raw/inbox/*.md written by voice-inbox /vault endpoint.
Output: append normalized entries to wiki/{치과,개인,기타}/Voice Inbox 정리함.md
        and mark source note frontmatter as status: 정리완료.

The script is intentionally conservative:
- never deletes raw notes
- skips notes already marked 정리완료/processed
- supports --dry-run
- uses only stdlib so it can run inside Hermes or from NAS/PC Python
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_VAULT = Path("/root/hermes-knowledge/vault-live")
AREA_MAP = {
    "병원": "치과",
    "치과": "치과",
    "개인업무": "개인",
    "개인": "개인",
    "개인생활": "기타",
    "기타": "기타",
    "사업": "사업",
    "학술": "학술",
}
TARGET_NOTE = "Voice Inbox 정리함.md"
DONE_STATUSES = {"정리완료", "완료", "처리완료", "processed", "done", "archive", "archived"}

@dataclass
class VoiceMemo:
    path: Path
    meta: Dict[str, object]
    body: str
    original: str


def now_kst() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec="seconds")


def split_frontmatter(text: str) -> Tuple[Dict[str, object], str, str]:
    """Return meta, body_without_original, original_text."""
    meta: Dict[str, object] = {}
    body = text
    if text.startswith("---\n") or text.startswith("---\r\n"):
        # tolerate CRLF by normalizing internal parsing only
        normalized = text.replace("\r\n", "\n")
        parts = normalized.split("---\n", 2)
        if len(parts) >= 3:
            raw_meta = parts[1]
            body = parts[2]
            current_key = None
            for line in raw_meta.splitlines():
                if not line.strip():
                    continue
                if line.startswith("  - ") and current_key:
                    meta.setdefault(current_key, [])
                    if isinstance(meta[current_key], list):
                        meta[current_key].append(line[4:].strip())
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    current_key = k.strip()
                    v = v.strip()
                    if v == "":
                        meta[current_key] = []
                    else:
                        meta[current_key] = v
    original = ""
    # voice-inbox format: body --- 원본:
    m = re.search(r"\n---\s*\n\s*원본:\s*\n(?P<original>.*)\s*$", body, flags=re.S)
    if m:
        original = m.group("original").strip()
        body = body[: m.start()].strip()
    else:
        body = body.strip()
    return meta, body, original


def render_frontmatter(meta: Dict[str, object]) -> str:
    order = ["area", "tags", "status", "created", "source", "organized", "organized_target"]
    keys = order + [k for k in meta.keys() if k not in order]
    lines = ["---"]
    for k in keys:
        if k not in meta:
            continue
        v = meta[k]
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def read_memo(path: Path) -> VoiceMemo:
    text = path.read_text(encoding="utf-8", errors="replace")
    meta, body, original = split_frontmatter(text)
    return VoiceMemo(path=path, meta=meta, body=body, original=original)


def is_unprocessed(m: VoiceMemo) -> bool:
    status = str(m.meta.get("status", "")).strip().lower()
    if status in {s.lower() for s in DONE_STATUSES}:
        return False
    if m.meta.get("organized") or m.meta.get("organized_target"):
        return False
    return True


def tags_of(m: VoiceMemo) -> List[str]:
    tags = m.meta.get("tags", [])
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    if isinstance(tags, str):
        return [t.strip() for t in re.split(r"[,#]", tags) if t.strip()]
    return []


def target_domain(m: VoiceMemo) -> str:
    area = str(m.meta.get("area", "기타")).strip()
    text = " ".join([area, m.path.name, m.body, m.original, " ".join(tags_of(m))])
    # Domain override for common clinic/business terms, because older classifier sometimes labels clinic work as 개인업무.
    if re.search(r"병원|치과|진료|데스크|기공|환자|수납|마케팅", text):
        return "치과"
    if re.search(r"제이스퀘어|법인|중국|사입|유통|청소|건물관리", text):
        return "사업"
    return AREA_MAP.get(area, "기타")


def item_type(m: VoiceMemo) -> str:
    text = " ".join([m.path.name, m.body, m.original, " ".join(tags_of(m))])
    if re.search(r"회의|안건|논의|말해야|팀장", text):
        return "회의안건"
    if re.search(r"해야|할일|처리|등록|예약|확인|보내|작성|수정", text):
        return "할일"
    if re.search(r"일정|약속|예약|다음 주|월요일|화요일|수요일|목요일|금요일|토요일|일요일|오전|오후|\d+시", text):
        return "일정"
    if re.search(r"아이디어|자동화|개선|만들|구상|기획", text):
        return "아이디어"
    return "기록"


def safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def ensure_target_note(path: Path, domain: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    title = path.stem
    path.write_text(
        f"# {title}\n\n"
        f"voice-inbox raw 메모를 Hermes가 후처리해 모으는 정리함. 원본 raw 파일은 삭제하지 않고 링크로 남긴다.\n\n"
        f"## 미처리/신규\n\n"
        f"## 회의안건\n\n"
        f"## 할일\n\n"
        f"## 일정\n\n"
        f"## 아이디어\n\n"
        f"## 기록\n\n",
        encoding="utf-8",
    )


def append_under_heading(path: Path, heading: str, entry: str) -> None:
    text = path.read_text(encoding="utf-8")
    marker = f"## {heading}"
    if marker not in text:
        text += f"\n{marker}\n\n"
    # Insert directly after heading block's existing content by appending before next heading, preserving newest first under heading.
    pattern = re.compile(rf"(^## {re.escape(heading)}\s*\n)", flags=re.M)
    m = pattern.search(text)
    if not m:
        text += f"\n{marker}\n\n{entry}\n"
    else:
        insert_at = m.end()
        text = text[:insert_at] + "\n" + entry.rstrip() + "\n" + text[insert_at:]
    path.write_text(text, encoding="utf-8")


def make_entry(m: VoiceMemo, root: Path, domain: str, typ: str) -> str:
    tags = tags_of(m)
    created = str(m.meta.get("created", ""))
    source = str(m.meta.get("source", ""))
    title = m.path.stem
    summary = m.body.strip() or m.original.strip() or title
    original = m.original.strip()
    rel = safe_rel(m.path, root)
    tag_text = " ".join(f"#{t.replace(' ', '_')}" for t in tags)
    lines = [
        f"### {title}",
        f"- 분류: {domain} / {typ}",
        f"- 생성: {created or '-'} · 출처: {source or '-'}",
        f"- 태그: {tag_text or '-'}",
        f"- 원본 파일: `{rel}`",
        f"- 요약: {summary}",
    ]
    if original and original != summary:
        lines.append(f"- 원문: {original}")
    lines.append("")
    return "\n".join(lines)


def mark_processed(m: VoiceMemo, target_rel: str) -> None:
    meta = dict(m.meta)
    meta["status"] = "정리완료"
    meta["organized"] = now_kst()
    meta["organized_target"] = target_rel
    body = m.body.strip()
    text = render_frontmatter(meta) + body + "\n"
    if m.original.strip():
        text += "\n---\n\n원본:\n\n" + m.original.strip() + "\n"
    m.path.write_text(text, encoding="utf-8")


def organize(root: Path, apply: bool = False, limit: int | None = None) -> List[str]:
    raw_inbox = root / "raw" / "inbox"
    wiki = root / "wiki"
    if not raw_inbox.exists():
        raise SystemExit(f"raw inbox not found: {raw_inbox}")
    memos = [read_memo(p) for p in sorted(raw_inbox.glob("*.md"), key=lambda p: p.stat().st_mtime)]
    memos = [m for m in memos if is_unprocessed(m)]
    if limit:
        memos = memos[:limit]
    results = []
    for m in memos:
        domain = target_domain(m)
        typ = item_type(m)
        target = wiki / domain / TARGET_NOTE
        target_rel = safe_rel(target, root)
        entry = make_entry(m, root, domain, typ)
        results.append(f"{safe_rel(m.path, root)} -> {target_rel} [{typ}]")
        if apply:
            ensure_target_note(target, domain)
            append_under_heading(target, typ, entry)
            mark_processed(m, target_rel)
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(DEFAULT_VAULT), help="vault root containing raw/ and wiki/")
    ap.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    root = Path(args.vault).expanduser().resolve()
    results = organize(root, apply=args.apply, limit=args.limit)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"voice-inbox organize {mode}: {len(results)} item(s)")
    for line in results:
        print("- " + line)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
