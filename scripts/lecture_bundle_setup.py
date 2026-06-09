#!/usr/bin/env python3
"""Create/organize a lecture bundle: transcript + photos -> vault wiki + optional Notion DB page.

Bundle convention:
  raw/학술/lectures/YYYY-MM-DD_학회명_강연명/
    transcript.txt or transcript.md
    photos/001.jpg ...
    metadata.json (optional)

This script creates a markdown summary in wiki/학술 and, if --notion is set,
creates an item in Notion DB '09 학회강연 Lectures'.

For now Notion stores the final text and source/vault links. Direct Notion image upload
is left as a switch (--upload-images) for later testing with a real Slack attachment.
"""
from __future__ import annotations

import argparse, datetime as dt, json, mimetypes, os, re, sys, urllib.request, urllib.error
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_VAULT = Path('/root/hermes-knowledge/vault-live')
LECTURE_DB_ID = '378f3e71-5c44-814a-8671-c68c5cee9731'
LECTURE_DATA_SOURCE_ID = '378f3e71-5c44-8187-95fe-000b169fa979'
IMG_EXTS = {'.jpg','.jpeg','.png','.webp','.gif'}


def slug(s: str) -> str:
    s = re.sub(r'[\\/:*?"<>|]+', '_', s).strip()
    s = re.sub(r'\s+', '_', s)
    return s[:120] or 'lecture'


def today() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime('%Y-%m-%d')


def load_env(path='/root/.hermes/.env'):
    p=Path(path)
    if not p.exists(): return
    for line in p.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k,v=line.split('=',1)
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def notion_request(path: str, payload: Dict[str, Any], method='POST', version='2022-06-28') -> Dict[str, Any]:
    key=os.environ.get('NOTION_API_KEY') or os.environ.get('NOTION_TOKEN') or os.environ.get('NOTION_API_TOKEN')
    if not key: raise RuntimeError('NOTION_API_KEY missing')
    data=json.dumps(payload, ensure_ascii=False).encode()
    req=urllib.request.Request('https://api.notion.com'+path, data=data, method=method)
    req.add_header('Authorization','Bearer '+key)
    req.add_header('Notion-Version', version)
    req.add_header('Content-Type','application/json')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Notion HTTP {e.code}: {e.read().decode()}')


def find_transcript(bundle: Path) -> Path|None:
    names = ['transcript.md','transcript.txt','녹취.md','녹취.txt']
    for n in names:
        p=bundle/n
        if p.exists(): return p
    candidates=[p for p in bundle.iterdir() if p.is_file() and p.suffix.lower() in {'.md','.txt'} and p.name!='metadata.json']
    return candidates[0] if candidates else None


def collect_photos(bundle: Path) -> List[Path]:
    photos=[]
    for d in [bundle/'photos', bundle/'사진', bundle]:
        if d.exists():
            photos += [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS]
    return sorted(set(photos), key=lambda p: p.name)


def read_meta(bundle: Path) -> Dict[str, Any]:
    meta={}
    mp=bundle/'metadata.json'
    if mp.exists():
        meta=json.loads(mp.read_text(encoding='utf-8'))
    parts=bundle.name.split('_')
    meta.setdefault('date', parts[0] if parts and re.match(r'\d{4}-\d{2}-\d{2}', parts[0]) else today())
    meta.setdefault('conference', parts[1] if len(parts)>1 else '')
    meta.setdefault('title', '_'.join(parts[2:]) if len(parts)>2 else bundle.name)
    meta.setdefault('field','학술')
    return meta


def summarize(transcript: str) -> str:
    # deterministic lightweight summary placeholder; Hermes can improve by editing the wiki/Notion page later.
    lines=[ln.strip() for ln in transcript.splitlines() if ln.strip()]
    head=' '.join(lines[:8])[:900]
    if not head: head='녹취 텍스트가 비어 있습니다. 사진과 현장 메모를 기준으로 추후 보완 필요.'
    return head


def make_wiki(bundle: Path, vault: Path) -> Path:
    meta=read_meta(bundle)
    tr_path=find_transcript(bundle)
    transcript=tr_path.read_text(encoding='utf-8', errors='replace') if tr_path else ''
    photos=collect_photos(bundle)
    title=f"{meta.get('date')} {meta.get('conference')} {meta.get('title')}".strip()
    wiki_dir=vault/'wiki'/'학술'
    wiki_dir.mkdir(parents=True, exist_ok=True)
    out=wiki_dir/(slug(title)+'_정리.md')
    rel_bundle=os.path.relpath(bundle, out.parent)
    lines=[
        f"# {title}",
        '',
        '## 메타',
        f"- 학회명: {meta.get('conference','') or '-'}",
        f"- 강연일: {meta.get('date','')}",
        f"- 원본 폴더: `{os.path.relpath(bundle, vault)}`",
        f"- 녹취 파일: `{os.path.relpath(tr_path, vault) if tr_path else '-'}`",
        f"- 사진 수: {len(photos)}",
        '',
        '## 핵심 요약',
        summarize(transcript),
        '',
        '## 사진 / 슬라이드',
    ]
    for i,p in enumerate(photos,1):
        rel=os.path.relpath(p, out.parent)
        lines += ['', f"### 사진 {i}: {p.name}", f"![사진 {i}]({rel})", '', '- 관련 내용:', '- 임상/업무 적용 포인트:']
    lines += ['', '## 녹취 원문', '', '```text', transcript.strip(), '```', '']
    out.write_text('\n'.join(lines), encoding='utf-8')
    return out


def create_notion_page(bundle: Path, wiki: Path, vault: Path) -> Dict[str, Any]:
    load_env()
    meta=read_meta(bundle)
    photos=collect_photos(bundle)
    title=f"{meta.get('date')} {meta.get('conference')} {meta.get('title')}".strip()
    wiki_uri='file://'+str(wiki)
    bundle_uri='file://'+str(bundle)
    payload={
      'parent': {'database_id': LECTURE_DB_ID},
      'properties': {
        '제목': {'title':[{'text':{'content':title}}]},
        '학회명': {'rich_text':[{'text':{'content':str(meta.get('conference',''))}}]},
        '강연일': {'date': {'start': str(meta.get('date') or today())}},
        '분야': {'select': {'name': str(meta.get('field') or '학술')}},
        '상태': {'select': {'name':'정리완료'}},
        '출처': {'multi_select': [{'name':'녹취앱'},{'name':'Slack'},{'name':'Hermes'}]},
        '사진수': {'number': len(photos)},
        '원본경로': {'url': bundle_uri},
        'Vault정리본': {'url': wiki_uri},
      }
    }
    page=notion_request('/v1/pages', payload, version='2022-06-28')
    page_id=page['id']
    # Append text blocks. Notion rich_text content cap is 2000 chars; keep concise.
    md=wiki.read_text(encoding='utf-8')
    summary=re.search(r'## 핵심 요약\n(?P<s>.*?)(\n## |\Z)', md, flags=re.S)
    summary_text=(summary.group('s').strip() if summary else '')[:1800]
    children=[
      {'object':'block','type':'paragraph','paragraph':{'rich_text':[{'type':'text','text':{'content':'Vault 정리본과 원본 bundle 경로는 DB 속성에 연결되어 있습니다.'}}]}},
      {'object':'block','type':'paragraph','paragraph':{'rich_text':[{'type':'text','text':{'content':'핵심 요약: '+summary_text[:1800]}}]}},
    ]
    for i,p in enumerate(photos[:20],1):
        children.append({'object':'block','type':'paragraph','paragraph':{'rich_text':[{'type':'text','text':{'content':f'사진 {i}: {p.name} — 원본 경로: {p}'}}]}})
    notion_request(f'/v1/blocks/{page_id}/children', {'children': children}, method='PATCH', version='2022-06-28')
    return {'id':page_id, 'url': page.get('url')}


def init_bundle(vault: Path, conference: str, title: str, date: str|None=None) -> Path:
    date=date or today()
    bundle=vault/'raw'/'학술'/'lectures'/slug(f'{date}_{conference}_{title}')
    (bundle/'photos').mkdir(parents=True, exist_ok=True)
    meta={'date':date,'conference':conference,'title':title,'field':'학술'}
    (bundle/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    tr=bundle/'transcript.txt'
    if not tr.exists(): tr.write_text('여기에 녹취앱에서 만든 텍스트를 붙여넣거나 파일을 교체하세요.\n', encoding='utf-8')
    return bundle


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--vault', default=str(DEFAULT_VAULT))
    ap.add_argument('--init', nargs=2, metavar=('CONFERENCE','TITLE'))
    ap.add_argument('--date')
    ap.add_argument('--bundle')
    ap.add_argument('--notion', action='store_true')
    args=ap.parse_args()
    vault=Path(args.vault).resolve()
    if args.init:
        bundle=init_bundle(vault,args.init[0],args.init[1],args.date)
        print('INIT', bundle)
        return
    if not args.bundle:
        raise SystemExit('Use --init or --bundle')
    bundle=Path(args.bundle).resolve()
    wiki=make_wiki(bundle,vault)
    print('WIKI', wiki)
    if args.notion:
        page=create_notion_page(bundle,wiki,vault)
        print('NOTION', page.get('url'), page.get('id'))

if __name__=='__main__': main()
