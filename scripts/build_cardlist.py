#!/usr/bin/env python3
"""旧裏カードリストの生成スクリプト。

入力:
  - TCGdex cards-database の data-asia を ts2json.mjs で変換した JSON
    （日本版の収録構成・レアリティの出典）
  - PokemonTCG/pokemon-tcg-data の cards/en/*.json
    （WotC 英語版の出典。HP・タイプ等の数値もここから取る）
  - PokeAPI の pokemon_species_names.csv（ポケモンの日本語種族名）
  - data/curation/*.json（手作業で確認した対応表・日本語名）

出力:
  - data/cards.json, data/cards.csv
  - docs/cards/*.md

使い方:
  python3 scripts/build_cardlist.py --jp jp.json --en <pokemon-tcg-data> \
      --species pokemon_species_names.csv
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 日本版の弾 → 主に対応する英語版セット（比較の基準）
JP_SETS = [
    # id, ファイル名, 主対応EN, 探索順
    ('PMCG1', '01-pmcg1-kakucho-pack', 'base1', ['base1']),
    ('PMCG2', '02-pmcg2-jungle', 'base2', ['base2']),
    ('PMCG3', '03-pmcg3-kaseki', 'base3', ['base3']),
    ('PMCG4', '04-pmcg4-rocket', 'base5', ['base5']),
    ('PMCG5', '05-pmcg5-leaders-stadium', 'gym1', ['gym1', 'gym2']),
    ('PMCG6', '06-pmcg6-yami-kara-no-chosen', 'gym2', ['gym2', 'gym1']),
    ('neo1', '07-neo1-kin-gin-shinsekai', 'neo1', ['neo1', 'neo2']),
    ('neo2', '08-neo2-iseki-wo-koete', 'neo2', ['neo2', 'neo3', 'neo1']),
    ('neo3', '09-neo3-mezameru-densetsu', 'neo3', ['neo3', 'neo2', 'neo4']),
    ('neo4', '10-neo4-yami-soshite-hikari', 'neo4', ['neo4', 'neo3']),
]
EN_ORDER = ['base1', 'base2', 'base3', 'base5', 'gym1', 'gym2', 'neo1', 'neo2',
            'neo3', 'neo4', 'si1', 'basep', 'base4', 'base6']
EN_SET_NAMES = {
    'base1': 'Base Set', 'base2': 'Jungle', 'base3': 'Fossil', 'base4': 'Base Set 2',
    'base5': 'Team Rocket', 'gym1': 'Gym Heroes', 'gym2': 'Gym Challenge',
    'neo1': 'Neo Genesis', 'neo2': 'Neo Discovery', 'neo3': 'Neo Revelation',
    'neo4': 'Neo Destiny', 'base6': 'Legendary Collection', 'si1': 'Southern Islands',
    'basep': 'Wizards Black Star Promos',
}
EN_SET_ABBR = {'base1': 'BS', 'base2': 'JU', 'base3': 'FO', 'base4': 'BS2', 'base5': 'TR',
               'gym1': 'G1', 'gym2': 'G2', 'neo1': 'N1', 'neo2': 'N2', 'neo3': 'N3', 'neo4': 'N4',
               'base6': 'LC', 'si1': 'SI', 'basep': 'Promo'}
TYPE_JA = {'Grass': '草', 'Fire': '炎', 'Water': '水', 'Lightning': '雷', 'Psychic': '超',
           'Fighting': '闘', 'Colorless': '無色', 'Darkness': '悪', 'Metal': '鋼'}
STAGE_JA = {'Basic': 'たね', 'Stage 1': '1進化', 'Stage 2': '2進化', 'Baby': 'ベイビィ'}
RARITY_JA = {'Common': '●', 'Uncommon': '◆', 'Rare': '★', 'Holo Rare': '★キラ',
             'Secret Rare': '特殊', 'Hyper rare': '特殊', 'Ultra Rare': '特殊'}
OWNERS = [("Brock's", 'タケシの', ['タケシ']), ("Misty's", 'カスミの', ['カスミ']),
          ("Erika's", 'エリカの', ['エリカ']), ("Lt. Surge's", 'マチスの', ['マチス']),
          ("Sabrina's", 'ナツメの', ['ナツメ']), ("Koga's", 'キョウの', ['キョウ']),
          ("Blaine's", 'カツラの', ['カツラ']), ("Giovanni's", 'サカキの', ['サカキ', 'ジョバンニ']),
          ("Rocket's", None, ['R団', 'ロケット団'])]
# 英語名の接頭辞 → 日本語名の接頭辞。None は curation で確定させる。
PREFIX_JA = {'Dark ': 'わるい', 'Shining ': 'ひかる', 'Light ': None}
PREFIX_HINT = {'Dark ': ['わるい', 'ダーク', '暗い', 'Dark'],
               'Light ': ['軽', 'ライト', 'やさしい', 'Light', '光から'],
               'Shining ': ['輝く', 'ひかる', 'Shining']}


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def num_key(n):
    m = re.match(r'(\d+)', str(n))
    return int(m.group(1)) if m else 0


def dmg(x):
    if x is None:
        return ''
    m = re.match(r'\d+', str(x))
    return m.group(0) if m else ''


def owner_of_ja(name):
    for en, _, hints in OWNERS:
        if any(name.startswith(h) for h in hints):
            return en
    return None


def owner_of_en(name):
    for en, _, _ in OWNERS:
        if name.startswith(en + ' '):
            return en
    return None


def prefix_of_en(name):
    for p in PREFIX_HINT:
        if name.startswith(p):
            return p
    return None


def prefix_of_ja(name):
    for p, hints in PREFIX_HINT.items():
        if any(h in name for h in hints):
            return p
    return None


def unown_letter_ja(name):
    m = re.search(r'([A-Za-z])\s*$', name)
    return m.group(1).upper() if m else None


def score(jc, ec, name_hint):
    """日本版カード jc と英語版カード ec の一致度。不一致なら None。"""
    if tuple(jc.get('dexId') or []) != tuple(ec.get('nationalPokedexNumbers') or []):
        return None
    if jc.get('hp') and ec.get('hp') and str(jc['hp']) != ec['hp']:
        return None
    if owner_of_ja(name_hint) != owner_of_en(ec['name']):
        return None
    if prefix_of_ja(name_hint) != prefix_of_en(ec['name']):
        return None
    if 201 in (jc.get('dexId') or []):
        letter = unown_letter_ja(name_hint)
        if letter and f'[{letter}]' not in ec['name']:
            return None
    ja, ea = jc.get('attacks', []), ec.get('attacks', [])
    if len(ja) > len(ea):
        return None
    sc = 2 if len(ja) == len(ea) else 0
    for a, b in zip(ja, ea):
        if sorted(a.get('cost') or []) == sorted(x for x in b.get('cost', []) if x != 'Free'):
            sc += 2
        else:
            sc -= 3
        da, db = dmg(a.get('damage')), dmg(b.get('damage'))
        if da and da != db:
            sc -= 3
        elif da:
            sc += 1
    if bool(jc.get('abilities')) == bool(ec.get('abilities')):
        sc += 1
    if jc.get('retreat') is not None and jc['retreat'] == ec.get('convertedRetreatCost', 0):
        sc += 1
    return sc


def card_signature(c):
    """同一カードのホロ版・ノーマル版を同一視するための署名。"""
    return (c['name'], c.get('hp'), tuple(a['name'] for a in c.get('attacks', [])),
            tuple(a['name'] for a in c.get('abilities', [])), tuple(c.get('rules', [])))


def species_ja(path):
    names = {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['local_language_id'] == '1':  # ja-Hrkt
                names[int(row['pokemon_species_id'])] = row['name']
    return names


def ja_pokemon_name(ec, species, conv):
    """英語名と図鑑番号から日本語カード名を組み立てる。"""
    dex = (ec.get('nationalPokedexNumbers') or [None])[0]
    base = species.get(dex)
    if base is None:
        return None
    name = ec['name']
    if dex == 201:
        m = re.search(r'\[([A-Z])\]', name)
        return conv['unown_format'].format(letter=m.group(1)) if m else base
    own = owner_of_en(name)
    if own:
        ja_prefix = dict((o[0], o[1]) for o in OWNERS)[own] or conv['owner_prefix'].get(own)
        return (ja_prefix or f'{own} ') + base
    p = prefix_of_en(name)
    if p:
        ja_prefix = PREFIX_JA[p] or conv['prefix'].get(p.strip())
        return (ja_prefix or p) + base
    return base


def normalize_ja(name):
    # PokeAPI の全角数字（ポリゴン２）をカード表記に合わせて半角にする
    return name.translate(str.maketrans('０１２３４５６７８９', '0123456789')) if name else name


def en_ref(cards):
    """同一セット内の重複（ホロ／ノーマル）をまとめて表記する。"""
    if not cards:
        return ''
    s = cards[0]['_set']
    nums = '・'.join(f"{c['number']}" for c in sorted(cards, key=lambda c: num_key(c['number'])))
    return f"{EN_SET_NAMES[s]} {nums}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jp', required=True)
    ap.add_argument('--en', required=True, help='pokemon-tcg-data のパス')
    ap.add_argument('--species', required=True)
    args = ap.parse_args()

    jp = {s['id']: s for s in load_json(args.jp)}
    en = {}
    for s in EN_ORDER:
        for c in load_json(Path(args.en) / 'cards' / 'en' / f'{s}.json'):
            c['_set'] = s
            en[c['id']] = c
    species = species_ja(args.species)
    cur = ROOT / 'data' / 'curation'
    overrides = load_json(cur / 'pokemon_overrides.json')
    trainers = load_json(cur / 'trainers.json')
    conv = load_json(cur / 'naming.json')
    jp_only = load_json(cur / 'jp_only.json')

    records = []
    matched_en = set()
    for set_id, slug, primary, search in JP_SETS:
        s = jp[set_id]
        cards = sorted(s['cards'], key=lambda c: num_key(overrides.get('_sort', {}).get(f"{set_id}-{c['localId']}", c['localId'])))
        for seq, jc in enumerate(cards, 1):
            key = f"{set_id}-{jc['localId']}"
            rec = {'jp_set': set_id, 'seq': seq, 'tcgdex_id': key,
                   'category': jc['category'], 'rarity_jp': jc.get('rarity'),
                   'holo': any(v.get('type') == 'holo' for v in jc.get('variants', [])),
                   'notes': []}
            ov = overrides.get(key, {})
            if ov.get('note'):
                rec['notes'].append(ov['note'])
            if jc['category'] == 'Pokemon':
                if key in jp_only:
                    best = []
                elif 'en' in ov:
                    best = [en[i] for i in ov['en']]
                else:
                    hint = ov.get('name_hint', jc['name']['ja'])
                    cands = []
                    for c in en.values():
                        if c['supertype'] != 'Pokémon':
                            continue
                        sc = score(jc, c, hint)
                        if sc is not None:
                            cands.append((sc, c))
                    if cands:
                        top = max(sc for sc, _ in cands)
                        tops = [c for sc, c in cands if sc == top]
                        order = search + [x for x in EN_ORDER if x not in search]
                        chosen_set = min({c['_set'] for c in tops}, key=order.index)
                        best = [c for c in tops if c['_set'] == chosen_set]
                        if len({card_signature(c) for c in best}) > 1:
                            raise SystemExit(f'ambiguous match for {key}: {[c["id"] for c in best]}')
                    else:
                        best = []
                if not best and key not in jp_only:
                    raise SystemExit(f'no English match for {key} {jc["name"]["ja"]}')
                if best:
                    e0 = best[0]
                    rec['ja_name'] = normalize_ja(ov.get('ja_name') or ja_pokemon_name(e0, species, conv))
                    rec['ja_name_basis'] = 'curated' if ov.get('ja_name') else 'generated'
                else:
                    rec['ja_name'] = jp_only[key]['ja_name']
                    rec['ja_name_basis'] = 'curated'
                    rec['notes'].append(jp_only[key]['note'])
            else:
                t = trainers.get(key)
                if t is None:
                    raise SystemExit(f'trainer/energy not curated: {key} {jc["name"]["ja"]}')
                best = [en[i] for i in t['en']] if t.get('en') else []
                rec['ja_name'] = t['ja']
                rec['ja_name_basis'] = t.get('confidence', '未確認') if t['ja'] else 'unknown'
                if t.get('note'):
                    rec['notes'].append(t['note'])
            for c in best:
                matched_en.add(c['id'])
            if best:
                e0 = best[0]
                rec['en_name'] = e0['name']
                rec['en_set'] = e0['_set']
                rec['en_numbers'] = [c['number'] for c in sorted(best, key=lambda c: num_key(c['number']))]
                rec['en_ref'] = en_ref(best)
                rec['en_set_differs'] = e0['_set'] != primary
                rec['types'] = e0.get('types', [])
                rec['stage'] = (e0.get('subtypes') or [''])[0] if e0['supertype'] == 'Pokémon' else ''
                rec['subtypes'] = e0.get('subtypes', [])
                rec['hp'] = e0.get('hp', '') if e0['supertype'] == 'Pokémon' else ''
                rec['evolves_from'] = e0.get('evolvesFrom', '')
                rec['weaknesses'] = [f"{w['type']}{w['value']}" for w in e0.get('weaknesses', [])]
                rec['resistances'] = [f"{w['type']}{w['value']}" for w in e0.get('resistances', [])]
                rec['retreat'] = e0.get('convertedRetreatCost', 0) if e0['supertype'] == 'Pokémon' else ''
                rec['powers'] = [f"{a.get('type', '')}: {a['name']}" for a in e0.get('abilities', [])]
                rec['attacks'] = [{'name': a['name'],
                                   'cost': ''.join(TYPE_JA.get(x, x)[0] if x != 'Free' else '-' for x in a.get('cost', [])),
                                   'damage': a.get('damage', '')} for a in e0.get('attacks', [])]
                # 英語版の他セットでの再録（同名・同数値）
                rec['en_reprints'] = []
                if e0['supertype'] == 'Pokémon':
                    for c in en.values():
                        if c['_set'] != e0['_set'] and c['name'] == e0['name'] \
                                and c.get('hp') == e0.get('hp') \
                                and [a['name'] for a in c.get('attacks', [])] == [a['name'] for a in e0.get('attacks', [])]:
                            rec['en_reprints'].append(f"{EN_SET_ABBR[c['_set']]} {c['number']}")
                if jc.get('hp') and e0.get('hp') and str(jc['hp']) != e0['hp']:
                    rec['notes'].append(f"TCGdex の日本版データでは HP {jc['hp']}（英語版は {e0['hp']}）")
            else:
                rec.update({'en_name': '', 'en_set': '', 'en_numbers': [], 'en_ref': '',
                            'en_set_differs': False, 'types': [TYPE_JA_REV.get(t, t) for t in jc.get('types', [])],
                            'stage': jc.get('stage', ''), 'subtypes': [], 'hp': str(jc.get('hp', '')),
                            'evolves_from': '', 'weaknesses': [], 'resistances': [],
                            'retreat': jc.get('retreat', ''), 'powers': [], 'attacks': [], 'en_reprints': []})
            records.append(rec)

    en_only = [c for c in en.values()
               if c['_set'] in ('base1', 'base2', 'base3', 'base5', 'gym1', 'gym2', 'neo1', 'neo2', 'neo3', 'neo4')
               and c['id'] not in matched_en
               and not (c['supertype'] == 'Energy' and 'Basic' in c.get('subtypes', []))]
    write_outputs(records, en_only, jp, en)


TYPE_JA_REV = {}


def md_escape(s):
    return str(s).replace('|', '\\|')


def kind_ja(r):
    if r['category'] == 'Pokemon':
        return 'ポケモン'
    if r['category'] == 'Energy':
        return '特殊エネルギー' if 'Special' in r['subtypes'] else '基本エネルギー'
    sub = [x for x in r['subtypes'] if x not in ('Item',)]
    label = {'Stadium': 'スタジアム', 'Pokémon Tool': 'ポケモンのどうぐ'}
    return 'トレーナー' + (f"（{'・'.join(label.get(x, x) for x in sub)}）" if sub else '')


def write_outputs(records, en_only, jp, en):
    data_dir = ROOT / 'data'
    data_dir.mkdir(exist_ok=True)
    with open(data_dir / 'cards.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    with open(data_dir / 'cards.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['jp_set', 'seq', 'ja_name', 'ja_name_basis', 'category', 'rarity_jp', 'holo',
                    'en_name', 'en_set', 'en_numbers', 'types', 'stage', 'hp', 'evolves_from',
                    'weaknesses', 'resistances', 'retreat', 'powers', 'attacks', 'en_reprints', 'notes',
                    'tcgdex_id'])
        for r in records:
            w.writerow([r['jp_set'], r['seq'], r['ja_name'], r['ja_name_basis'], r['category'],
                        r['rarity_jp'], r['holo'], r['en_name'], r['en_set'], ' '.join(r['en_numbers']),
                        ' '.join(r['types']), r['stage'], r['hp'], r['evolves_from'],
                        ' '.join(r['weaknesses']), ' '.join(r['resistances']), r['retreat'],
                        ' / '.join(r['powers']),
                        ' / '.join(f"{a['name']} [{a['cost']}] {a['damage']}".strip() for a in r['attacks']),
                        ' / '.join(r['en_reprints']), ' / '.join(r['notes']), r['tcgdex_id']])

    out = ROOT / 'docs' / 'cards'
    out.mkdir(parents=True, exist_ok=True)
    set_meta = load_json(ROOT / 'data' / 'curation' / 'sets.json')
    for set_id, slug, primary, _ in JP_SETS:
        meta = set_meta[set_id]
        rs = [r for r in records if r['jp_set'] == set_id]
        lines = [f"# {meta['ja']}（{meta['label']}）", '',
                 f"- 発売日: {meta['release']}",
                 f"- 収録枚数: {meta['count']}",
                 f"- 主に対応する英語版: {meta['en']}", '']
        if meta.get('intro'):
            lines += [meta['intro'], '']
        lines += ['| No. | 日本語名 | 種類 | タイプ | 進化 | HP | レア | 英語版（WotC） | 備考 |',
                  '|---:|---|---|---|---|---:|---|---|---|']
        for r in rs:
            if not r['ja_name']:
                name_cell = '（公式名未確認）'
            else:
                mark = '' if r['ja_name_basis'] in ('generated', 'curated', '確実', '有力') else ' ※'
                name_cell = md_escape(r['ja_name']) + mark
            en_cell = f"{md_escape(r['en_name'])}<br>{r['en_ref']}" if r['en_name'] else '（英語版なし）'
            if r['en_set_differs']:
                en_cell += ' ⚠'
            notes = list(r['notes'])
            if r['en_reprints']:
                notes.append('再録: ' + '、'.join(r['en_reprints']))
            lines.append('| {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
                r['seq'], name_cell, kind_ja(r),
                '・'.join(TYPE_JA.get(t, t) for t in r['types']),
                STAGE_JA.get(r['stage'], r['stage']), r['hp'],
                RARITY_JA.get(r['rarity_jp'], r['rarity_jp'] or ''), en_cell,
                md_escape('<br>'.join(notes))))
        moved = [r for r in rs if r['en_set_differs']]
        lines += ['', '## 英語版との対応メモ', '']
        if moved:
            lines.append(f"⚠ 印のカードは、英語版では {meta['en']} 以外のセットに収録されています。")
            lines.append('')
            for r in moved:
                lines.append(f"- {r['ja_name'] or '（公式名未確認）'} → {r['en_name']}（{r['en_ref']}）")
        else:
            lines.append(f"日本版の全カードが {meta['en']} に収録されています。")
        jo = [r for r in rs if not r['en_name']]
        if jo:
            lines += ['', '英語版に対応カードがないもの:', '']
            for r in jo:
                lines.append(f"- {r['ja_name']}：{'／'.join(r['notes'])}")
        eo = [c for c in en_only if c['_set'] == primary]
        if eo:
            lines += ['', f"{meta['en']} にあって、日本版の本弾に収録されていないカード（基本エネルギー除く）:", '']
            for c in sorted(eo, key=lambda c: num_key(c['number'])):
                lines.append(f"- {c['number']} {c['name']}")
        lines += ['', '---', '', '凡例・出典は [カードリストの見かた](README.md) を参照。', '']
        (out / f'{slug}.md').write_text('\n'.join(lines), encoding='utf-8')
    # 英語版セットごとの「日本の拡張パックに無いカード」一覧
    lines = ['# 英語版のみに見られるカード（日本の拡張パック未収録）', '',
             '英語版（WotC）の各セットに収録されているが、日本の旧裏拡張パック 10 弾のどれにも対応カードが見つからないもの。',
             '日本ではスターターデッキ・テーマデッキ・プロモなど拡張パック以外の商品で出たカードが多い（個別の初出は未調査）。',
             '基本エネルギーは除外。', '']
    for s in ['base1', 'base2', 'base3', 'base5', 'gym1', 'gym2', 'neo1', 'neo2', 'neo3', 'neo4']:
        eo = sorted([c for c in en_only if c['_set'] == s], key=lambda c: num_key(c['number']))
        lines += [f'## {EN_SET_NAMES[s]}', '']
        if not eo:
            lines += ['（なし）', '']
            continue
        lines += [f'{len(eo)} 枚', '']
        for c in eo:
            lines.append(f"- {c['number']} {c['name']}")
        lines.append('')
    (out / 'english-only.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(records)} records, {len(en_only)} english-only')


if __name__ == '__main__':
    main()
