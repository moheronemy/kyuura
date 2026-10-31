#!/usr/bin/env python3
"""目録（data/cards.csv）の行と、記録の目録の分類（catalog_class・engine_scope）を作る。

data/cards.csv は、対戦のカードだけでなく、目録に収録する公式のカード類を横断して検索できる一覧にする。行は 3 つの元データから作り、
同じ項目を別々に手入力しない。

  1. data/cards.json の記録（対戦のカードの記録。拡張パック・拡張パック以外の商品）
  2. data/product_items.json の non_game_items（pcg-search の転記のうち、通常の対戦のデッキに入れるカードではない項目）
  3. data/curation/catalog_items.json の items（pcg-search の転記にない項目。公式の書籍などで確かめて手で記録したもの）

記録の分類は次の 3 つを別々の欄にする（docs/data-schema.md）。
  - catalog_class: 目録の分類（battle・special_rule・award・jumbo と、non_game_items の kind）
  - play_scope: 通常対戦での使用範囲（data/cards.json の記録だけ。standard・kangaskhan_rule・not_for_official_tournaments）
  - engine_scope: 通常対戦のエンジンの実装の対象か（target・excluded・undecided）と、その理由（engine_scope_reason）

data/cards.json の記録の catalog_class・engine_scope は data/curation/non_pack.json の catalog_scope の明示の指定から決める
（指定のない記録は battle・target。play_scope が kangaskhan_rule の記録に指定がなければ止める）。
通常対戦の対象を取り出すときは、行の数や product_group ではなく、catalog_class と engine_scope で選ぶ（battle_records・
battle_rows）。

使い方（リポジトリの直下で）:
  python3 scripts/catalog.py          data/cards.csv を、data/cards.json・data/product_items.json・catalog_items.json から書き直す
  python3 scripts/catalog.py --check  書き換えずに、data/cards.csv が元データと同じか・id と参照を検査する
scripts/build_cardlist.py も、data/cards.json を作ったあとで同じ関数で data/cards.csv を書く（同じ結果になる）。
"""
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_CLASSES = {
    'battle': '対戦用（通常の対戦のデッキに入れるカード）',
    'special_rule': '専用ルール用（ガルーラルールなど、決まったルールの対戦で使うカード）',
    'award': '認定・賞品（認定証・入賞賞品・特典のカード。対戦に使う効果がない）',
    'jumbo': 'ジャンボカード（通常のカードより大きい印刷物）',
    # data/curation/non_pack.json の non_game_items の kind（既存の分類をそのまま使う）
    'extra_rule': 'おすすめルールのカード', 'deck_recipe': 'デッキのカード（デッキレシピ）', 'joke_card': 'ジョークカード',
    'pass_card': 'パスカード', 'other': 'その他',
}
ENGINE_SCOPES = {'target': '通常対戦のエンジンの実装の対象', 'excluded': '対象外（理由は engine_scope_reason）',
                 'undecided': '未判断（理由は engine_scope_reason）'}
RESEARCH_STATUSES = {
    'transcribed': '出典サイトの転記（なぞのばしょ・ポケモンWiki・pcg-search など。data/cards.json の ja_text_source・source_pages）',
    'card_image_checked': 'kyuura がカードの画像で印刷の欄を読んだ記録がある（data/curation/card_image_checks.json）',
    'book_image_read': '公式の書籍の図版で名前・本文を読んだ（data/curation/catalog_items.json）',
    'book_listed': '公式の書籍の掲載で名前・配布を確かめた（本文は転記していない）',
}
CARD_COLUMNS = ['id', 'jp_set', 'seq', 'category', 'name_ja', 'name_en', 'name_ja_confidence',
                'rarity_jp', 'holo', 'en_set', 'en_numbers', 'stage', 'evolves_from_ja', 'evolves_from_en',
                'evolves_to_status', 'evolves_to_ja', 'hp', 'types', 'weaknesses', 'resistances', 'retreat_cost', 'trainer_kinds',
                'energy_kind', 'text_ja', 'text_en', 'jp_en_differences', 'notes',
                'product_group', 'play_scope', 'same_card_group', 'source_pages', 'data_gaps', 'corrections']
# 2026-10-31 に加えた欄（既存の欄の位置を変えないよう、後ろに足す）
CATALOG_COLUMNS = ['official_number', 'catalog_class', 'engine_scope', 'engine_scope_reason', 'research_status', 'sources']
COLUMNS = CARD_COLUMNS + CATALOG_COLUMNS
KC_ID = re.compile(r'^KC-\d{4}$')
CARD_ID = re.compile(r'^[A-Za-z][A-Za-z0-9]*-\d{3}$')


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


# ---- data/cards.json の記録の分類 -----------------------------------------------

def scope_designations(non_pack):
    return {k: v for k, v in non_pack.get('catalog_scope', {}).items() if not k.startswith('_')}


def apply_catalog_scope(records, non_pack):
    """記録に catalog_class・engine_scope・engine_scope_reason を付ける（scripts/build_cardlist.py から呼ぶ）。"""
    des = scope_designations(non_pack)
    by_id = {r['id']: r for r in records}
    unknown = sorted(set(des) - set(by_id))
    if unknown:
        raise SystemExit(f'non_pack.json の catalog_scope の id が記録にない: {unknown}')
    for r in records:
        d = des.get(r['id'])
        if d:
            if d.get('page') and d['page'] not in r['source_ids']['pcg_search']:
                raise SystemExit(f"non_pack.json の catalog_scope の page が記録と合わない: {r['id']} {d['page']}")
            if d['catalog_class'] not in CATALOG_CLASSES or d['engine_scope'] not in ENGINE_SCOPES:
                raise SystemExit(f"non_pack.json の catalog_scope の値が不正: {r['id']}")
            if d['engine_scope'] != 'target' and not d.get('engine_scope_reason'):
                raise SystemExit(f"non_pack.json の catalog_scope に対象外・未判断の理由がない: {r['id']}")
            r['catalog_class'], r['engine_scope'] = d['catalog_class'], d['engine_scope']
            r['engine_scope_reason'] = d.get('engine_scope_reason') if d['engine_scope'] != 'target' else None
        elif r['play_scope'] in ('standard', 'not_for_official_tournaments'):
            r['catalog_class'], r['engine_scope'], r['engine_scope_reason'] = 'battle', 'target', None
        else:
            raise SystemExit(f"play_scope が {r['play_scope']} の記録に、non_pack.json の catalog_scope の指定がない: {r['id']}")
    return records


def battle_records(records):
    """通常対戦のエンジンの対象の記録（明示の分類で選ぶ。行の数・product_group では選ばない）。"""
    return [r for r in records if r.get('catalog_class') == 'battle' and r.get('engine_scope') == 'target']


# ---- 行 ------------------------------------------------------------------------

def evolves_to_status(p):
    """CSV の evolves_to_status: 空（ポケモンでない）・not_applicable（欄のない段階）・unconfirmed（null）・printed（名前がある）。
    printed_none（[]。印刷に進化先がないと明示）は形式の上の値で、今は check_evolves_to が受け付けない。"""
    if not p:
        return ''
    if 'evolves_to' not in p:
        return 'not_applicable'
    v = p['evolves_to']
    return 'unconfirmed' if v is None else 'printed' if v else 'printed_none'


def image_checked_ids(image_checks):
    return {x['card_id'] for x in image_checks['checks']}


def card_row(r, image_checked):
    p, t, e = r['pokemon'], r['trainer'], r['energy']
    text = (t or {}).get('text') or (e or {}).get('text') or (p or {}).get('rules_text') or {}
    return [r['id'], r['jp_set'], r['seq'], r['category'], r['name']['ja'] or '', r['name']['en'] or '',
            r['name_ja_confidence'] or '', r['rarity_jp']['code'], r['rarity_jp']['holo'],
            (r['en_print'] or {}).get('set_id', ''), ' '.join((r['en_print'] or {}).get('numbers', [])),
            (p or {}).get('stage') or '',
            ((p or {}).get('evolves_from') or {}).get('ja') or '',
            ((p or {}).get('evolves_from') or {}).get('en') or '',
            evolves_to_status(p), ' '.join((p or {}).get('evolves_to') or []),
            (p or {}).get('hp') or '', ' '.join((p or {}).get('types', [])),
            ' '.join(f"{x['type']}{x['operator']}{x['value']}" for x in (p or {}).get('weaknesses', [])),
            ' '.join(f"{x['type']}{x['operator']}{x['value']}" for x in (p or {}).get('resistances', [])),
            '' if p is None or p['retreat_cost'] is None else p['retreat_cost'],
            ' '.join((t or {}).get('kinds', [])), (e or {}).get('kind', ''),
            text.get('ja') or '', text.get('en') or '',
            ' / '.join(f"[{x['kind']}] {x['summary']}" for x in r['jp_en_differences']),
            ' / '.join(r['notes']),
            r['product_group'], r['play_scope'], r['same_card_group'] or '',
            ' '.join(r['source_ids']['pcg_search']), ' '.join(r['data_gaps']),
            ' '.join(c['id'] for c in r.get('corrections', [])),
            '', r['catalog_class'], r['engine_scope'], r['engine_scope_reason'] or '',
            'card_image_checked' if r['id'] in image_checked else 'transcribed', '']


def blank_row(**values):
    row = dict.fromkeys(COLUMNS, '')
    unknown = set(values) - set(COLUMNS)
    if unknown:
        raise ValueError(f'unknown columns: {unknown}')
    row.update(values)
    return [row[c] for c in COLUMNS]


def non_game_row(x, product_groups):
    """data/product_items.json の non_game_items の項目（pcg-search の転記。対戦のカードではない）。"""
    notes = [x['reason']] + ([f"カードの補足欄: {x['note']}"] if x.get('note') else [])
    if x['display_name'] != x['name']:
        notes.append(f"pcg-search の名前の欄: {x['name']}")
    return blank_row(id=x['id'], jp_set=x['product'], name_ja=x['display_name'] or x['name'], name_ja_confidence='有力',
                     text_ja=x.get('text') or '', notes=' / '.join(notes), product_group=product_groups[x['product']],
                     source_pages=x['page'], catalog_class=x['kind'], engine_scope='excluded',
                     engine_scope_reason='通常の対戦のデッキに入れるカードではない項目（data/product_items.json の non_game_items）',
                     research_status='transcribed', sources='N3')


def catalog_item_row(x):
    """data/curation/catalog_items.json の項目（pcg-search の転記にない項目）。"""
    notes = [f"配布: {x['distribution_ja']}"]
    if x.get('date'):
        notes.append(f"時期: {x['date']}")
    if x.get('size'):
        notes.append(f"寸法: {x['size']}")
    if x.get('printed_header'):
        notes.append(f"上部の表示: {x['printed_header']}")
    notes += x.get('notes', [])
    notes += [f'未確認: {u}' for u in x.get('unconfirmed', [])]
    if x.get('related_ids'):
        notes.append('関連（別の項目）: ' + ' '.join(x['related_ids']))
    sources = ' '.join(f"{s['code']}" + (f" p.{','.join(s['pages'])}" if s.get('pages') else '') for s in x['sources'])
    return blank_row(id=x['id'], name_ja=x['name_ja'], name_ja_confidence='有力', text_ja=x.get('printed_text_ja') or '',
                     notes=' / '.join(notes), product_group=x['product_group'], official_number=x.get('official_number') or '',
                     catalog_class=x['catalog_class'], engine_scope=x['engine_scope'], engine_scope_reason=x['engine_scope_reason'] or '',
                     research_status=x['research_status'], sources=sources)


def rows(records, non_game_items, catalog_items, product_groups, image_checks):
    checked = image_checked_ids(image_checks)
    out = [card_row(r, checked) for r in records]
    out += [non_game_row(x, product_groups) for x in non_game_items]
    out += [catalog_item_row(x) for x in catalog_items['items']]
    return out


def render_csv(all_rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(COLUMNS)
    w.writerows(all_rows)
    return buf.getvalue()


def battle_rows(csv_text):
    """data/cards.csv の行のうち、通常対戦のエンジンの対象（catalog_class battle・engine_scope target）。CSV を読む側の例。"""
    return [r for r in csv.DictReader(io.StringIO(csv_text)) if r['catalog_class'] == 'battle' and r['engine_scope'] == 'target']


def write_cards_csv(records, non_game_items, product_groups):
    """scripts/build_cardlist.py から呼ぶ（records は分類済み）。"""
    text = render_csv(rows(records, non_game_items, load('data/curation/catalog_items.json'), product_groups,
                           load('data/curation/card_image_checks.json')))
    with open(ROOT / 'data' / 'cards.csv', 'w', encoding='utf-8', newline='') as f:
        f.write(text)


# ---- 検査 ------------------------------------------------------------------------

def problems(records, product_items, catalog_items, survey):
    """id の一意性・形・参照切れと、分類の値を調べる（エラーのリスト）。"""
    errors = []
    ids = [r['id'] for r in records] + [x['id'] for x in product_items['non_game_items']] + [x['id'] for x in catalog_items['items']]
    dup = sorted(k for k, n in Counter(ids).items() if n > 1)
    if dup:
        errors.append(f'id が重複している: {dup}')
    for r in records:
        if not CARD_ID.match(r['id']):
            errors.append(f"data/cards.json の id の形が違う: {r['id']}")
        if r.get('catalog_class') not in CATALOG_CLASSES or r.get('engine_scope') not in ENGINE_SCOPES:
            errors.append(f"data/cards.json の分類がない・不正: {r['id']}")
        elif r['engine_scope'] != 'target' and not r.get('engine_scope_reason'):
            errors.append(f"対象外・未判断の理由がない: {r['id']}")
        elif r['engine_scope'] == 'target' and r.get('engine_scope_reason'):
            errors.append(f"対象の記録に理由がある: {r['id']}")
        if r.get('catalog_class') == 'battle' and r['play_scope'] == 'kangaskhan_rule':
            errors.append(f"専用ルールのカードが battle になっている: {r['id']}")
    for x in product_items['non_game_items']:
        if x['kind'] not in CATALOG_CLASSES:
            errors.append(f"non_game_items の kind が目録の分類にない: {x['id']} {x['kind']}")
    for x in catalog_items['items']:
        w = x.get('id')
        if not KC_ID.match(w or ''):
            errors.append(f'catalog_items の id の形が違う（KC-0000）: {w}')
        if x.get('catalog_class') not in CATALOG_CLASSES or x['catalog_class'] == 'battle':
            errors.append(f'catalog_items の catalog_class が不正（対戦のカードは data/cards.json に記録する）: {w}')
        if x.get('engine_scope') not in ENGINE_SCOPES or x['engine_scope'] == 'target' or not x.get('engine_scope_reason'):
            errors.append(f'catalog_items の engine_scope は対象外・未判断で、理由が要る: {w}')
        if x.get('research_status') not in RESEARCH_STATUSES:
            errors.append(f'catalog_items の research_status が不正: {w}')
        if not x.get('sources') or not x.get('distribution_ja'):
            errors.append(f'catalog_items に出典・配布がない: {w}')
        for f in ('pokemon', 'hp', 'attacks', 'stage', 'evolves_from'):
            if f in x:
                errors.append(f'catalog_items に対戦のカードの欄がある（与えない）: {w} {f}')
        for ref in x.get('related_ids', []):
            if ref not in ids:
                errors.append(f'catalog_items の related_ids がない: {w} {ref}')
    known = set(ids)
    statuses = set(survey['scope']['statuses'])
    relations = set(survey['scope']['relations'])
    added = set()
    for comp in survey['comparisons']:
        for e in comp['entries']:
            where = f"promo_survey {comp['source']} {e.get('n', e.get('page'))}"
            if e['status'] not in statuses or e['relation'] not in relations:
                errors.append(f'{where}: status・relation の値が不正')
            for ref in e['catalog_ids']:
                if ref not in known:
                    errors.append(f'{where}: catalog_ids がない: {ref}')
            if e['status'] in ('existing', 'existing_other_product', 'added') and not e['catalog_ids']:
                errors.append(f'{where}: 収録済みなのに catalog_ids がない')
            if e['status'] == 'added':
                added.update(e['catalog_ids'])
                if any(not KC_ID.match(i) for i in e['catalog_ids']):
                    errors.append(f'{where}: added は catalog_items の項目')
            if e['status'] in ('addition_candidate', 'variant_candidate', 'out_of_scope', 'unconfirmed') and not e.get('note'):
                errors.append(f'{where}: 理由（note）がない')
    missing = sorted({x['id'] for x in catalog_items['items']} - added)
    if missing:
        errors.append(f'catalog_items の項目が promo_survey のどの比較からも参照されていない: {missing}')
    return errors


def check(write=False):
    records = load('data/cards.json')['cards']
    items = load('data/product_items.json')
    cat = load('data/curation/catalog_items.json')
    survey = load('data/curation/promo_survey.json')
    groups = {p['id']: p['group'] for p in items['products']}
    errors = problems(records, items, cat, survey)
    text = render_csv(rows(records, items['non_game_items'], cat, groups, load('data/curation/card_image_checks.json')))
    path = ROOT / 'data' / 'cards.csv'
    if write and not errors:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    else:
        with open(path, encoding='utf-8', newline='') as f:
            same = f.read() == text
        if not same:
            errors.append('data/cards.csv が元データ（data/cards.json・data/product_items.json・data/curation/catalog_items.json）と違う')
    return errors


def main():
    errors = check(write='--check' not in sys.argv[1:])
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        raise SystemExit(1)
    print('OK', file=sys.stderr)


if __name__ == '__main__':
    main()
