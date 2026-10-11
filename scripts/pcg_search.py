#!/usr/bin/env python3
"""ポケモンカード 旧シリーズ検索（pcg-search.com）から、拡張パック以外の旧裏の商品のカードを取り出す。

対象: 拡張シート第1〜3弾、映画公開記念パック「サザンアイランド」、ポケモンジムの構築済みデッキ 6 種、
クイックスターターギフト、イントロパック（フシギダネデッキ・ゼニガメデッキ・キラカード）、
イントロパック★neo（チコリータデッキ・ワニノコデッキと各拡張カード）、neo プレミアムファイル 1〜3、旧裏期と neo 期のプロモ。

  fetch   カードリストのページと、対象の商品のカード個別ページを取得してキャッシュに保存する
          （robots.txt はなし。2 秒間隔で 1 件ずつ取得し、接続が切れたら間をあけて再試行。約 680 ページ）
  extract キャッシュした HTML からカードの欄を取り出し、JSON に書き出す

使い方:
  python3 scripts/pcg_search.py fetch   --cache <キャッシュ用ディレクトリ>
  python3 scripts/pcg_search.py extract --cache <キャッシュ用ディレクトリ> --out data/ja_text_pcgsearch.json

カード個別ページのワザのコスト・タイプ・弱点などはエネルギーの画像（en000〜en008.png）で表されているので、
画像のファイル名を記号（草・炎・水・雷・超・闘・無・悪・鋼）に読み替える。
「001/036」のような番号はサイトの並び順で、カードに印刷された番号ではない（イントロパックのデッキだけは印刷された丸数字と一致）。
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = 'https://pcg-search.com'
LIST_PAGE = '/card/card_list.php'
# 取り込む商品。(カードリストの見出しの表記, カードページのディレクトリ, 出力でのキー)。
# 「プロモ」のように同じ見出しが複数あるので、カードページのディレクトリで区別する
PRODUCTS = [
    ('拡張シート 第1弾(青版)', '/card/1st/', '拡張シート 第1弾(青版)'),
    ('拡張シート 第2弾(赤版)', '/card/1st/', '拡張シート 第2弾(赤版)'),
    ('拡張シート 第3弾(緑版)', '/card/1st/', '拡張シート 第3弾(緑版)'),
    ('映画公開記念パック「サザンアイランド」', '/card/1st/', '映画公開記念パック「サザンアイランド」'),
    ('ポケモンジム第1弾「ニビシティジム タケシ」', '/card/1st/', 'ポケモンジム第1弾「ニビシティジム タケシ」'),
    ('ポケモンジム第1弾「ハナダシティジム カスミ」', '/card/1st/', 'ポケモンジム第1弾「ハナダシティジム カスミ」'),
    ('ポケモンジム第2弾「クチバシティジム マチス」', '/card/1st/', 'ポケモンジム第2弾「クチバシティジム マチス」'),
    ('ポケモンジム第2弾「タマムシシティジム エリカ」', '/card/1st/', 'ポケモンジム第2弾「タマムシシティジム エリカ」'),
    ('ポケモンジム第3弾「グレンタウンジム カツラ」', '/card/1st/', 'ポケモンジム第3弾「グレンタウンジム カツラ」'),
    ('ポケモンジム第3弾「ヤマブキシティジム ナツメ」', '/card/1st/', 'ポケモンジム第3弾「ヤマブキシティジム ナツメ」'),
    ('クイックスターターギフト', '/card/1st/', 'クイックスターターギフト'),
    ('イントロパック(フシギダネデッキ)', '/card/1st/', 'イントロパック(フシギダネデッキ)'),
    ('イントロパック(ゼニガメデッキ)', '/card/1st/', 'イントロパック(ゼニガメデッキ)'),
    ('イントロパック(おまけカード)', '/card/1st/', 'イントロパック(おまけカード)'),
    ('プロモ', '/card/1st/', 'プロモ(旧裏)'),
    ('プレミアムファイル', '/card/neo/', 'プレミアムファイル'),
    ('プレミアムファイル2', '/card/neo/', 'プレミアムファイル2'),
    ('プレミアムファイル3', '/card/neo/', 'プレミアムファイル3'),
    ('イントロパック★neo(チコリータデッキ)', '/card/neo/', 'イントロパック★neo(チコリータデッキ)'),
    ('イントロパック★neo(チコリータデッキ：拡張カード)', '/card/neo/', 'イントロパック★neo(チコリータデッキ：拡張カード)'),
    ('イントロパック★neo(ワニノコデッキ)', '/card/neo/', 'イントロパック★neo(ワニノコデッキ)'),
    ('イントロパック★neo(ワニノコデッキ：拡張カード)', '/card/neo/', 'イントロパック★neo(ワニノコデッキ：拡張カード)'),
    ('プロモ', '/card/neo/', 'プロモ(neo)'),
]
UA = 'Mozilla/5.0 (compatible; kyuura-docs/1.0; +https://github.com/moheronemy/kyuura)'
DELAY = 2.0
ENERGY = {'000': '無', '001': '草', '002': '炎', '003': '水', '004': '雷',
          '005': '超', '006': '闘', '007': '悪', '008': '鋼'}


def get(url):
    for wait in (0, 5, 15, 30):
        time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode('utf-8')
        except OSError as e:  # 接続のリセットなど
            print(f'retry {url}: {e}', file=sys.stderr)
    raise RuntimeError(f'failed: {url}')


def cache_name(path):
    return path.strip('/').replace('/', '_')


def sections(list_html):
    """カードリストのページを、見出しごとの [(見出し, [(セルの文字列のリスト, リンク)])] に分ける。"""
    out = []
    for part in re.split(r'<div class="accordion-title js-accordion-title">', list_html)[1:]:
        title = html.unescape(re.match(r'([^<]*)', part).group(1)).strip()
        rows = []
        for tr in re.findall(r'<tr>(.*?)</tr>', part, re.S):
            cells = [html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
                     for t in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
            link = re.search(r'href="(/card/[^"]+\.php)"', tr)
            if link:
                rows.append((cells, link.group(1)))
        out.append((title, rows))
    return out


def selected(list_html):
    """取り込む商品の [(出力でのキー, 行)]。"""
    out = []
    for title, rows in sections(list_html):
        for t, d, key in PRODUCTS:
            if t == title and rows and rows[0][1].startswith(d):
                out.append((key, rows))
    return out


def fetch(cache):
    cache.mkdir(parents=True, exist_ok=True)
    list_file = cache / cache_name(LIST_PAGE + '.html')
    if not list_file.exists():
        list_file.write_text(get(BASE + LIST_PAGE), encoding='utf-8')
    for _, rows in selected(list_file.read_text(encoding='utf-8')):
        for _, link in rows:
            f = cache / cache_name(link + '.html')
            if f.exists():
                continue
            time.sleep(DELAY)
            f.write_text(get(BASE + link), encoding='utf-8')
            print(f'fetched {link}', file=sys.stderr)


def text(s):
    s = re.sub(r'<img[^>]*en(\d{3})\.png"[^>]*>', lambda m: ENERGY.get(m.group(1), '?'), s)
    s = re.sub(r'<br\s*/?>', '\n', s)
    return html.unescape(re.sub(r'<[^>]+>', '', s)).replace('　', ' ').strip()


def icons(s):
    return ''.join(ENERGY.get(x, '?') for x in re.findall(r'en(\d{3})\.png', s))


def parse_card(page_html):
    main = page_html[page_html.find('<div class="col-md-7">'):page_html.find('<p class="bikouTitle">')]
    card = {}
    m = re.search(r'<p class="dataField (cardNamePoke|cardName)">(.*?)</p>', main, re.S)
    head = m.group(2)
    card['kind'] = text(re.search(r'<span style="font-size:10px">(.*?)</span>', head, re.S).group(1))
    if m.group(1) == 'cardNamePoke':  # ポケモン: 名前の前にタイプの画像、後ろに HP
        card['type'] = icons(head.split('<span style="font-size:16px">')[0])
        card['name'] = text(re.sub(r'<span style="font-size:(10|16)px">.*?</span>|<img[^>]*>', '', head, flags=re.S))
        hp = re.search(r'HP:(\d+)', head)
        card['hp'] = int(hp.group(1)) if hp else None
        for label, key in (('弱点', 'weakness'), ('抵抗力', 'resistance'), ('にげる', 'retreat')):
            v = re.search(rf'<span class="dataField cardInfo">{label}(.*?)</span>', main, re.S).group(1)
            v = (icons(v) + text(re.sub(r'<img[^>]*>', '', v))).strip()
            card[key] = None if v in ('', '-') else v
    else:
        card['name'] = text(re.sub(r'<span style="font-size:10px">.*?</span>', '', head, flags=re.S))
    card['powers'] = [{'name': re.sub(r'^【特殊能力】', '', text(t)), 'text': text(d) or None} for t, d in
                      re.findall(r'<p class="pPowerTitle">(.*?)</p>\s*<p class="pPowerDetail">(.*?)</p>', main, re.S)]
    card['attacks'] = []
    for t, d in re.findall(r'<p class="wazaTitle">(.*?)</p>\s*<p class="wazaDetail">(.*?)</p>', main, re.S):
        rest = text(re.sub(r'<img[^>]*>', '', t))
        m2 = re.match(r'(.*?)\s+(\S*\d\S*)$', rest)  # 名前の後ろの「10」「20×」「10ぐらい」がダメージ
        name, damage = (m2.group(1), m2.group(2)) if m2 else (rest, None)
        card['attacks'].append({'name': name.strip(), 'cost': icons(t), 'damage': damage, 'text': text(d) or None})
    card['text'] = '\n'.join(text(x) for x in re.findall(r'<p class="trainerDetail">(.*?)</p>', main, re.S)) or None
    card['note'] = '\n'.join(text(x) for x in re.findall(r'<p class="ruleDetail">(.*?)</p>', main, re.S)) or None
    for v in re.findall(r'<p class="packName">(.*?)</p>', main, re.S):
        v = text(v)
        if v.startswith('illus.'):
            card['illustrator'] = v[len('illus.'):].strip()
    rarity = re.search(r'レアリティ(.*?)</span>', main, re.S)
    card['rarity'] = text(rarity.group(1)) if rarity else None
    remarks = re.search(r'<p class="bikouDetail">(.*?)</p>', page_html, re.S)
    card['remarks'] = (text(remarks.group(1)) if remarks else '') or None
    return card


def extract(cache, out):
    result = {'source': BASE + LIST_PAGE,
              'note': 'ポケモンカード 旧シリーズ検索（pcg-search.com）のカードページから scripts/pcg_search.py で抽出。'
                      'list_number はサイトの並び順で、カードに印刷された番号ではない。',
              'products': {}}
    for key, rows in selected((cache / cache_name(LIST_PAGE + '.html')).read_text(encoding='utf-8')):
        cards = []
        for cells, link in rows:
            card = {'list_number': cells[0], 'url': BASE + link}
            card.update(parse_card((cache / cache_name(link + '.html')).read_text(encoding='utf-8')))
            cards.append(card)
        result['products'][key] = cards
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print({k: len(v) for k, v in result['products'].items()}, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=['fetch', 'extract'])
    ap.add_argument('--cache', type=Path, required=True)
    ap.add_argument('--out', type=Path, default=Path('data/ja_text_pcgsearch.json'))
    args = ap.parse_args()
    if args.command == 'fetch':
        fetch(args.cache)
    else:
        extract(args.cache, args.out)


if __name__ == '__main__':
    main()
