#!/usr/bin/env python3
"""ポケモンWiki のカードページから手作業で保存したデータ（data/raw/*.json）を、
build_cardlist.py が読む形（なぞのばしょと同じ形式）に変換する。

ポケモンWiki は自動アクセスを Cloudflare で止めているため、ページはブラウザで保存し、
カード名・ワザ・特殊能力・説明文などを抜き出した JSON を data/raw/ に置いている。

使い方:
  python3 scripts/pokemonwiki.py --raw data/raw --out data/ja_text_pokemonwiki.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

# data/raw のファイル名 → TCGdex の弾 id
RAW_FILES = {
    'リーダーズスタジアム.json': 'PMCG5',
    '闇からの挑戦.json': 'PMCG6',
    'めざめる伝説.json': 'neo3',
    '闇そして光へ.json': 'neo4',
}
# トレーナーのページに複数の版の説明文があるとき、旧裏の版を選ぶための手がかり
ERA_HINTS = {'PMCG5': ('PMCG', 'リーダーズスタジアム'), 'PMCG6': ('PMCG',), 'neo3': ('neo',), 'neo4': ('neo', '闇、そして光へ')}


def pick_text(other, set_id):
    """説明文の候補から旧裏の版を選ぶ。戻り値は (本文, 選んだ欄の名前)。"""
    keys = [k for k in other if k.startswith('説明文')]
    for k in keys:
        label = k[len('説明文'):]
        if any(h in label for h in ERA_HINTS[set_id]):
            return other[k], k
    if '説明文' in other:
        return other['説明文'], '説明文'
    return None, None


def digits(s):
    m = re.search(r'\d+', s or '')
    return m.group(0) if m else None


def convert(raw_dir):
    result = {'source': 'https://wiki.pokemonwiki.com/',
              'note': 'ポケモンWiki のカードページをブラウザで保存したもの（data/raw/）を scripts/pokemonwiki.py で変換。',
              'sets': {}}
    for fname, set_id in RAW_FILES.items():
        path = raw_dir / fname
        if not path.exists():
            print(f'missing: {path}', file=sys.stderr)
            continue
        cards = []
        for pos, x in enumerate(json.loads(path.read_text(encoding='utf-8')), 1):
            c = x['card']
            other = json.loads(c.get('other_fields_json') or '{}')
            type_lines = (c.get('type_raw') or '').split('\n')
            text, text_field = (None, None)
            if c['card_kind'] != 'Pokemon':
                text, text_field = pick_text(other, set_id)
            fields = {
                'カード名称': c['card_name_ja'],
                'カード分類': c.get('stage_raw') or None,
                'LV.': digits(c.get('level_raw')),
                'HP': c.get('hp') or None,
                'タイプ': type_lines[0] or None,
                'にげる': (c.get('retreat_cost_raw') or '').lstrip('－-') or ('なし' if c.get('retreat_cost_raw') else None),
                '弱点': c.get('weakness_raw') or None,
                '抵抗力': c.get('resistance_raw') or None,
                'レアリティ': c.get('rarity_raw') or None,
                'シリーズ': c.get('set_name') or None,
            }
            cards.append({
                'fields': {k: v for k, v in fields.items() if v},
                'powers': [{'name': p['name'], 'text': p.get('effect_text_ja') or None} for p in x.get('powers', [])],
                'attacks': [{'name': a['name'], 'cost': a.get('cost_raw') or None,
                             'damage': a.get('damage_raw') or None, 'text': a.get('effect_text_ja') or None}
                            for a in x.get('attacks', [])],
                'text': text,
                'text_field': text_field,
                'rules_text': '\n'.join(type_lines[1:]).strip() or None,
                'url': c['source_url'],
                'permalink': c.get('source_permalink'),
                'revision': c.get('source_revision'),
                'hint_id': c.get('kyuura_card_id') or None,
                'list_position': pos,
            })
        result['sets'][fname] = {'tcgdex_set': set_id, 'cards': cards}
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', type=Path, default=Path('data/raw'))
    ap.add_argument('--out', type=Path, default=Path('data/ja_text_pokemonwiki.json'))
    args = ap.parse_args()
    result = convert(args.raw)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(sum(len(s['cards']) for s in result['sets'].values()), 'cards', file=sys.stderr)


if __name__ == '__main__':
    main()
