#!/usr/bin/env python3
"""なぞのばしょ（nazonobasho.com）の旧裏カードページから、日本版のカードテキストを取り出す。

  fetch   カードリストのページとカード個別ページを取得してキャッシュに保存する
          （robots.txt で許可された範囲。1.5 秒間隔で 1 件ずつ取得）
  extract キャッシュした HTML からカードテキストを取り出し、JSON に書き出す

使い方:
  python3 scripts/nazonobasho.py fetch   --cache <キャッシュ用ディレクトリ>
  python3 scripts/nazonobasho.py extract --cache <キャッシュ用ディレクトリ> --out data/ja_text_nazonobasho.json
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = 'https://nazonobasho.com/'
# このサイトにカードリストがある旧裏の弾（2026年10月時点）。値は TCGdex の弾 id（None は拡張パック以外）
LIST_PAGES = {
    'cardlist-pmcg01': 'PMCG1',
    'cardlist-pmcg02-jungle': 'PMCG2',
    'cardlist-pmcg03-kaseki': 'PMCG3',
    'cardlist-pmcg04-rocket': 'PMCG4',
    'cardlist-neo01': 'neo1',
    'cardlist-neo02': 'neo2',
    'cardlist-neopf01': None,
    'cardlist-neopf02': None,
    'cardlist-pmcg-southernisland': None,
}
UA = 'Mozilla/5.0 (compatible; kyuura-docs/1.0; +https://github.com/moheronemy/kyuura)'
DELAY = 1.5


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8')


def slug_of(url):
    return url.rstrip('/').rsplit('/', 1)[-1]


def card_urls(list_html):
    a = list_html.find('<div class="entry-content')
    b = list_html.find('関連記事', a)
    urls = []
    for u in re.findall(r'href="(https://nazonobasho\.com/[^"]+/)"', list_html[a:b]):
        if u not in urls and not re.search(r'/(category|cardlist|product|tag|author|feed)', u):
            urls.append(u)
    return urls


def fetch(cache):
    cache.mkdir(parents=True, exist_ok=True)
    for page in LIST_PAGES:
        path = cache / f'{page}.html'
        if not path.exists():
            path.write_text(get(BASE + page + '/'), encoding='utf-8')
            time.sleep(DELAY)
    for page in LIST_PAGES:
        urls = card_urls((cache / f'{page}.html').read_text(encoding='utf-8'))
        for u in urls:
            path = cache / 'cards' / f'{slug_of(u)}.html'
            if path.exists():
                continue
            path.parent.mkdir(exist_ok=True)
            try:
                path.write_text(get(u), encoding='utf-8')
            except Exception as e:  # 取得できなかったページは記録して続ける
                print(f'failed: {u} {e}', file=sys.stderr)
            time.sleep(DELAY)
        print(f'{page}: {len(urls)} cards', file=sys.stderr)


def cell_text(inner):
    inner = re.sub(r'<br\s*/?>', '\n', inner)
    txt = html.unescape(re.sub(r'<[^>]+>', '', inner))
    txt = '\n'.join(line.strip() for line in txt.splitlines())
    return txt.strip()


def table_rows(page_html):
    a = page_html.find('<div class="entry-content')
    b = page_html.find('</table>', a)
    rows = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', page_html[a:b], re.S):
        cells = []
        for attrs, inner in re.findall(r'<td([^>]*)>(.*?)</td>', tr, re.S):
            m = re.search(r'rowspan="(\d+)"', attrs)
            cells.append((cell_text(inner), int(m.group(1)) if m else 1))
        rows.append(cells)
    return rows


def grouped(rows):
    """rowspan を展開して (見出し, [値...]) の列にする。"""
    out, label, left = [], None, 0
    for cells in rows:
        if left > 0 and len(cells) == 1:
            out[-1][1].append(cells[0][0])
            left -= 1
            continue
        if not cells:
            continue
        label, span = cells[0]
        values = [c[0] for c in cells[1:]]
        out.append((label, values))
        left = span - 1
    return out


def none_if_na(s):
    return None if s in ('', 'n/a', 'N/A', '-', '―') else s


ENERGY_RE = re.compile(r'^[草炎水雷超闘無悪鋼]+$')
DAMAGE_RE = re.compile(r'^\d+\s*[+＋×xX\-−]?$')
BLOCK_LABELS = ('特殊能力', 'ポケモンパワー', 'ポケパワー', 'ポケボディー', 'ワザ')


def is_text(s):
    return s in ('n/a', 'N/A') or '。' in s or len(s) >= 20


def split_blocks(values):
    """ワザ／特殊能力の欄を中身で判別して分ける。サイトの見出しは当てにならない
    （ワザが「特殊能力」の見出しの下にある、行数がまちまち、など）ため、
    2 行目がエネルギー記号だけならワザ、それ以外は特殊能力として読む。"""
    out, i = [], 0
    while i < len(values):
        name = values[i]
        i += 1
        if i < len(values) and ENERGY_RE.match(values[i]):
            cost = values[i]
            i += 1
            damage = text = None
            if i < len(values) and (DAMAGE_RE.match(values[i]) or (values[i] == 'n/a' and i + 1 < len(values) and is_text(values[i + 1]))):
                damage = none_if_na(values[i])
                i += 1
            if i < len(values) and is_text(values[i]):
                text = none_if_na(values[i])
                i += 1
            out.append(('attack', {'name': name, 'cost': cost, 'damage': damage, 'text': text}))
        else:
            text = None
            if i < len(values) and is_text(values[i]):
                text = none_if_na(values[i])
                i += 1
            out.append(('power', {'name': name, 'text': text}))
    return out


def parse_card(page_html):
    groups = grouped(table_rows(page_html))
    card = {'fields': {}, 'powers': [], 'attacks': [], 'text': None}
    for label, values in groups:
        if label in BLOCK_LABELS:
            for kind, item in split_blocks(values):
                (card['attacks'] if kind == 'attack' else card['powers']).append(item)
        elif label in ('効果', 'カード効果', 'テキスト', '説明'):
            card['text'] = none_if_na('\n'.join(values))
        else:
            card['fields'][label] = values[0] if len(values) == 1 else values
    return card


def extract(cache, out):
    result = {'source': BASE, 'note': 'なぞのばしょ（nazonobasho.com）のカード個別ページに掲載された日本版のカードテキスト。scripts/nazonobasho.py で抽出。',
              'sets': {}}
    for page, set_id in LIST_PAGES.items():
        urls = card_urls((cache / f'{page}.html').read_text(encoding='utf-8'))
        cards = []
        for pos, u in enumerate(urls, 1):
            path = cache / 'cards' / f'{slug_of(u)}.html'
            if not path.exists():
                print(f'missing: {u}', file=sys.stderr)
                continue
            c = parse_card(path.read_text(encoding='utf-8'))
            c.update({'url': u, 'list_position': pos})
            cards.append(c)
        result['sets'][page] = {'tcgdex_set': set_id, 'cards': cards}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(sum(len(s['cards']) for s in result['sets'].values()), 'cards', file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=['fetch', 'extract'])
    ap.add_argument('--cache', required=True, type=Path)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    if args.command == 'fetch':
        fetch(args.cache)
    else:
        extract(args.cache, args.out or Path('data/ja_text_nazonobasho.json'))


if __name__ == '__main__':
    main()
