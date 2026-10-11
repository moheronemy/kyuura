#!/usr/bin/env python3
"""旧裏カードリストの生成スクリプト。

入力:
  - TCGdex cards-database の data-asia を ts2json.mjs で変換した JSON
    （日本版の収録構成・レアリティの出典）
  - PokemonTCG/pokemon-tcg-data の cards/en/*.json
    （WotC 英語版の出典。HP・タイプ・ワザ・効果文はここから取る）
  - PokeAPI の pokemon_species_names.csv（ポケモンの日本語・英語の種族名）
  - data/curation/*.json（手作業で確認した対応表・日本語名・日本語テキスト・日英の違い）

出力:
  - data/cards.json（構造化データ。スキーマは docs/data-schema.md）
  - data/cards.csv, data/attacks.csv, data/powers.csv（表形式の写し）
  - docs/cards/*.md

使い方:
  python3 scripts/build_cardlist.py --jp jp.json --en <pokemon-tcg-data> \
      --species pokemon_species_names.csv
"""
import argparse
import csv
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = 2

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

# 構造化データでの列挙値（英小文字）と、日本語の表示名
TYPE_ID = {'Grass': 'grass', 'Fire': 'fire', 'Water': 'water', 'Lightning': 'lightning',
           'Psychic': 'psychic', 'Fighting': 'fighting', 'Colorless': 'colorless',
           'Darkness': 'darkness', 'Metal': 'metal'}
TYPE_JA = {'grass': '草', 'fire': '炎', 'water': '水', 'lightning': '雷', 'psychic': '超',
           'fighting': '闘', 'colorless': '無色', 'darkness': '悪', 'metal': '鋼'}
STAGE_ID = {'Basic': 'basic', 'Stage 1': 'stage1', 'Stage 2': 'stage2', 'Baby': 'baby'}
STAGE_JA = {'basic': 'たね', 'stage1': '1進化', 'stage2': '2進化', 'baby': 'ベイビィ'}
TRAINER_KIND_ID = {'Stadium': 'stadium', 'Pokémon Tool': 'pokemon_tool',
                   "Rocket's Secret Machine": 'rockets_secret_machine',
                   'Goldenrod Game Corner': 'goldenrod_game_corner'}
TRAINER_KIND_JA = {'stadium': 'スタジアム', 'pokemon_tool': 'ポケモンのどうぐ',
                   'rockets_secret_machine': 'ロケット団秘密メカ',
                   'goldenrod_game_corner': 'Goldenrod Game Corner'}
POWER_KIND_ID = {'Pokémon Power': 'pokemon_power', 'Poké-Power': 'poke_power', 'Poké-Body': 'poke_body'}
POWER_KIND_JA = {'pokemon_power': 'ポケモンパワー', 'poke_power': 'ポケパワー', 'poke_body': 'ポケボディー'}
# TCGdex のレアリティ表記 → (コード, 日本版の記号)
RARITY = {'Common': ('common', '●'), 'Uncommon': ('uncommon', '◆'), 'Rare': ('rare', '★'),
          'Holo Rare': ('holo_rare', '★'), 'Secret Rare': ('special', None),
          'Hyper rare': ('special', None), 'Ultra Rare': ('special', None)}
OWNERS = [("Brock's", 'タケシの', ['タケシ']), ("Misty's", 'カスミの', ['カスミ']),
          ("Erika's", 'エリカの', ['エリカ']), ("Lt. Surge's", 'マチスの', ['マチス']),
          ("Sabrina's", 'ナツメの', ['ナツメ']), ("Koga's", 'キョウの', ['キョウ']),
          ("Blaine's", 'カツラの', ['カツラ']), ("Giovanni's", 'サカキの', ['サカキ', 'ジョバンニ']),
          ("Rocket's", None, ['R団', 'ロケット団'])]
# 英語名の接頭辞 → 日本語名の接頭辞。None は naming.json で確定させる。
PREFIX_JA = {'Dark ': 'わるい', 'Shining ': 'ひかる', 'Light ': None}
PREFIX_HINT = {'Dark ': ['わるい', 'ダーク', '暗い', 'Dark'],
               'Light ': ['軽', 'ライト', 'やさしい', 'Light', '光から'],
               'Shining ': ['輝く', 'ひかる', 'Shining']}
JA_TEXT_MISSING = 'この弾の日本語のワザ名・特殊能力名・効果文は未収録です（[理由](README.md#日本語テキストについて)）。'
JA_TEXT_PRESENT = ('日本語のワザ名・特殊能力名・効果文は、各カードの「日本語テキストの出典」にあるページ（{sites}）から取り込んだものです'
                   '（[詳細](README.md#日本語テキストについて)）。数値は英語版データの値で、日本語版の記載と食い違うものは備考に書いています。'
                   '英語版に対応カードがないものは、数値も日本語の出典の値です。')


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def num_key(n):
    m = re.match(r'(\d+)', str(n))
    return int(m.group(1)) if m else 0


def dmg_digits(x):
    if x is None:
        return ''
    m = re.match(r'\d+', str(x))
    return m.group(0) if m else ''


def parse_damage(s):
    """英語版の威力表記（"30", "30+", "10×", "30-", "?", ""）を構造化する。"""
    s = (s or '').strip()
    if not s:
        return None
    m = re.fullmatch(r'(\d+)?\s*([+×x\-?])?', s)
    if not m:
        raise SystemExit(f'unknown damage notation: {s!r}')
    base, mod = m.groups()
    return {'base': int(base) if base else None,
            'modifier': {'x': '×'}.get(mod, mod),
            'display': s}


def parse_wr(entries):
    out = []
    for w in entries or []:
        m = re.fullmatch(r'([×x+\-])(\d+)', w['value'])
        if not m:
            raise SystemExit(f'unknown weakness/resistance value: {w}')
        out.append({'type': TYPE_ID[w['type']], 'operator': {'x': '×'}.get(m.group(1), m.group(1)),
                    'value': int(m.group(2))})
    return out


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
        da, db = dmg_digits(a.get('damage')), dmg_digits(b.get('damage'))
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


def name_key(s):
    return re.sub(r'[^a-z0-9]', '', s.lower().replace('♀', 'f').replace('♂', 'm'))


def species_names(path):
    """図鑑番号 → 日本語名、英語名（正規化済み）→ 図鑑番号。"""
    ja, en = {}, {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            sid = int(row['pokemon_species_id'])
            if row['local_language_id'] == '1':  # ja-Hrkt
                ja[sid] = row['name']
            elif row['local_language_id'] == '9':  # en
                en[name_key(row['name'])] = sid
    return ja, en


def normalize_ja(name):
    # PokeAPI の全角数字（ポリゴン２）をカード表記に合わせて半角にする
    return name.translate(str.maketrans('０１２３４５６７８９', '0123456789')) if name else name


class Namer:
    """英語版のポケモンのカード名から日本語のカード名を組み立てる。"""

    def __init__(self, species_path, conv, extra=None):
        self.ja, self.en = species_names(species_path)
        self.conv = conv
        self.extra = extra or {}  # ポケモン以外から進化する場合（なにかの化石）など

    def from_en(self, name, dex=None):
        if name in self.extra:
            return self.extra[name]
        own = owner_of_en(name)
        pre = None if own else prefix_of_en(name)
        base_en = name[len(own) + 1:] if own else (name[len(pre):] if pre else name)
        if dex is None:
            base_en = re.sub(r'\s*\[[A-Z]\]$', '', base_en)
            dex = self.en.get(name_key(base_en))
        base = self.ja.get(dex)
        if base is None:
            return None
        if dex == 201:
            m = re.search(r'\[([A-Z])\]', name)
            return self.conv['unown_format'].format(letter=m.group(1)) if m else base
        if own:
            ja_prefix = dict((o[0], o[1]) for o in OWNERS)[own] or self.conv['owner_prefix'].get(own)
            return normalize_ja((ja_prefix or f'{own} ') + base)
        if pre:
            ja_prefix = PREFIX_JA[pre] or self.conv['prefix'].get(pre.strip())
            return normalize_ja((ja_prefix or pre) + base)
        return normalize_ja(base)


def en_print(cards, primary):
    s = cards[0]['_set']
    return {'set_id': s, 'set_name': EN_SET_NAMES[s],
            'numbers': [c['number'] for c in sorted(cards, key=lambda c: num_key(c['number']))],
            'differs_from_primary': s != primary}


def match_pokemon(jc, key, ov, en, search):
    if 'en' in ov:
        return [en[i] for i in ov['en']]
    hint = ov.get('name_hint', jc['name']['ja'])
    cands = []
    for c in en.values():
        if c['supertype'] != 'Pokémon':
            continue
        sc = score(jc, c, hint)
        if sc is not None:
            cands.append((sc, c))
    if not cands:
        raise SystemExit(f'no English match for {key} {jc["name"]["ja"]}')
    top = max(sc for sc, _ in cands)
    tops = [c for sc, c in cands if sc == top]
    order = search + [x for x in EN_ORDER if x not in search]
    chosen_set = min({c['_set'] for c in tops}, key=order.index)
    best = [c for c in tops if c['_set'] == chosen_set]
    if len({card_signature(c) for c in best}) > 1:
        raise SystemExit(f'ambiguous match for {key}: {[c["id"] for c in best]}')
    return best


def plain(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


def en_reprints(e0, en):
    """英語版の他セットでの再録。ポケモンは同名・同 HP・同じワザ名の並び、トレーナー・エネルギーは同名。
    英語版データの上で元のカードと違う欄を differences に入れる（cost・damage・text・weakness・resistance・retreat）。"""
    out = []
    for c in en.values():
        if c['_set'] == e0['_set'] or c['supertype'] != e0['supertype'] or c['name'] != e0['name']:
            continue
        diff = []
        if c['supertype'] == 'Pokémon':
            atk0, atk1 = e0.get('attacks', []), c.get('attacks', [])
            if c.get('hp') != e0.get('hp') or [a['name'] for a in atk1] != [a['name'] for a in atk0] \
                    or [a['name'] for a in c.get('abilities', [])] != [a['name'] for a in e0.get('abilities', [])]:
                continue
            if any(sorted(a.get('cost', [])) != sorted(b.get('cost', [])) for a, b in zip(atk0, atk1)):
                diff.append('cost')
            if any(a.get('damage') != b.get('damage') for a, b in zip(atk0, atk1)):
                diff.append('damage')
            texts = [a.get('text') for a in atk0] + [a.get('text') for a in e0.get('abilities', [])]
            texts1 = [a.get('text') for a in atk1] + [a.get('text') for a in c.get('abilities', [])]
            if [plain(t) for t in texts] != [plain(t) for t in texts1]:
                diff.append('text')
            for key, label in (('weaknesses', 'weakness'), ('resistances', 'resistance'),
                               ('convertedRetreatCost', 'retreat')):
                if c.get(key) != e0.get(key):
                    diff.append(label)
        elif plain(' '.join(c.get('rules', []))) != plain(' '.join(e0.get('rules', []))):
            diff.append('text')
        out.append({'set_id': c['_set'], 'set_name': EN_SET_NAMES[c['_set']], 'number': c['number'],
                    'differences': diff})
    return sorted(out, key=lambda x: (EN_ORDER.index(x['set_id']), num_key(x['number'])))


def bilingual(en_value, ja_value=None):
    return {'ja': ja_value or None, 'en': en_value or None}


def build_pokemon(e0, namer, ja_text):
    jt_powers = ja_text.get('powers', [])
    jt_attacks = ja_text.get('attacks', [])
    powers = []
    for i, a in enumerate(e0.get('abilities', [])):
        jt = jt_powers[i] if i < len(jt_powers) else {}
        powers.append({'kind': POWER_KIND_ID[a['type']],
                       'name': bilingual(a['name'], jt.get('name')),
                       'text': bilingual(a.get('text'), jt.get('text'))})
    attacks = []
    for i, a in enumerate(e0.get('attacks', [])):
        jt = jt_attacks[i] if i < len(jt_attacks) else {}
        cost = [TYPE_ID[x] for x in a.get('cost', []) if x != 'Free']
        attacks.append({'name': bilingual(a['name'], jt.get('name')),
                        'cost': cost,
                        'cost_total': len(cost),
                        'damage': parse_damage(a.get('damage')),
                        'text': bilingual(a.get('text') or None, jt.get('text'))})
    evo = e0.get('evolvesFrom')
    rules_en = ' '.join(e0.get('rules', [])) or None
    return {
        'dex': e0.get('nationalPokedexNumbers', []),
        'stage': STAGE_ID[(e0.get('subtypes') or ['Basic'])[0]],
        'evolves_from': {'ja': namer.from_en(evo), 'en': evo} if evo else None,
        'hp': int(e0['hp']),
        'types': [TYPE_ID[t] for t in e0.get('types', [])],
        'weaknesses': parse_wr(e0.get('weaknesses')),
        'resistances': parse_wr(e0.get('resistances')),
        'retreat_cost': e0.get('convertedRetreatCost', 0),
        'rules_text': bilingual(rules_en, ja_text.get('rules_text')) if rules_en else None,
        'powers': powers,
        'attacks': attacks,
    }


def build_records(args):
    jp = {s['id']: s for s in load_json(args.jp)}
    en = {}
    for s in EN_ORDER:
        for c in load_json(Path(args.en) / 'cards' / 'en' / f'{s}.json'):
            c['_set'] = s
            en[c['id']] = c
    cur = ROOT / 'data' / 'curation'
    for cid, fix in load_json(cur / 'en_fixes.json').items():  # 英語版データの誤りを補正
        if cid.startswith('_'):
            continue
        for af in fix.get('attacks', []):
            atk = next(a for a in en[cid]['attacks'] if a['name'] == af['name'])
            atk.update({k: v for k, v in af.items() if k not in ('name', 'rename')})
            if 'rename' in af:  # ワザ名の誤り
                atk['name'] = af['rename']
    overrides = load_json(cur / 'pokemon_overrides.json')
    trainers = load_json(cur / 'trainers.json')
    jp_only = load_json(cur / 'jp_only.json')
    ja_texts = load_json(cur / 'ja_text.json')
    diffs = load_json(cur / 'card_differences.json')
    trainer_ja = {en[t['en'][0]]['name']: t['ja'] for t in trainers.values() if t['ja']}
    namer = Namer(args.species, load_json(cur / 'naming.json'), trainer_ja)

    records, matched_en = [], set()
    for set_id, _, primary, search in JP_SETS:
        sort_ov = overrides.get('_sort', {})
        cards = sorted(jp[set_id]['cards'],
                       key=lambda c: num_key(sort_ov.get(f"{set_id}-{c['localId']}", c['localId'])))
        for seq, jc in enumerate(cards, 1):
            key = f"{set_id}-{jc['localId']}"
            ov = overrides.get(key, {})
            ja_text = ja_texts.get(key, {})
            label = jc.get('rarity')
            code, mark = RARITY[label]
            rec = {'id': key, 'jp_set': set_id, 'seq': seq,
                   'category': jc['category'].lower(),
                   'name': {'ja': None, 'en': None},
                   'name_ja_confidence': None,
                   'rarity_jp': {'code': code, 'mark': mark,
                                 'holo': any(v.get('type') == 'holo' for v in jc.get('variants', [])),
                                 'source_label': label},
                   'en_print': None, 'en_reprints': [],
                   'pokemon': None, 'trainer': None, 'energy': None,
                   'jp_en_differences': diffs.get(key, []),
                   'notes': [x for x in (ov.get('note'), ja_text.get('note')) if x],
                   'source_ids': {'tcgdex': key, 'pokemontcg': []},
                   'ja_text_source': ja_text.get('source'),
                   'jp_print': None}
            if jc['category'] == 'Pokemon' and key in jp_only:
                rec['name']['ja'] = jp_only[key]['ja_name']
                rec['name_ja_confidence'] = '有力'
                rec['notes'].append(jp_only[key]['note'])
                rec['pokemon'] = {'dex': jc.get('dexId', []), 'stage': STAGE_ID.get(jc.get('stage'), None),
                                  'evolves_from': None, 'hp': jc.get('hp'),
                                  'types': [TYPE_ID[t] for t in jc.get('types', [])],
                                  'weaknesses': [], 'resistances': [], 'retreat_cost': jc.get('retreat'),
                                  'rules_text': None, 'powers': [], 'attacks': []}
                records.append(rec)
                continue
            if jc['category'] == 'Pokemon':
                best = match_pokemon(jc, key, ov, en, search)
                e0 = best[0]
                rec['name']['ja'] = normalize_ja(ov.get('ja_name') or namer.from_en(e0['name'], (e0.get('nationalPokedexNumbers') or [None])[0]))
                rec['name_ja_confidence'] = '有力'  # 図鑑番号から生成し、別データと全件照合済み
                rec['pokemon'] = build_pokemon(e0, namer, ja_text)
                if jc.get('hp') and str(jc['hp']) != e0['hp']:
                    rec['notes'].append(f"TCGdex の日本版データでは HP {jc['hp']}（英語版は {e0['hp']}）")
                rec['en_reprints'] = en_reprints(e0, en)
            else:
                t = trainers.get(key)
                if t is None:
                    raise SystemExit(f'trainer/energy not curated: {key} {jc["name"]["ja"]}')
                best = [en[i] for i in t['en']]
                e0 = best[0]
                rec['name']['ja'] = t['ja'] or None
                rec['name_ja_confidence'] = t['confidence'] if t['ja'] else None
                if t.get('note'):
                    rec['notes'].append(t['note'])
                if 'Basic' not in e0.get('subtypes', []):  # 基本エネルギーの再録は載せない
                    rec['en_reprints'] = en_reprints(e0, en)
                text = bilingual(' '.join(e0.get('rules', [])) or None, ja_text.get('text'))
                if e0['supertype'] == 'Trainer':
                    rec['trainer'] = {'kinds': [TRAINER_KIND_ID[x] for x in e0.get('subtypes', [])],
                                      'text': text}
                else:
                    special = 'Special' in e0.get('subtypes', [])
                    provides = [] if special else [TYPE_ID[e0['name'].replace(' Energy', '')]]
                    rec['energy'] = {'kind': 'special' if special else 'basic', 'provides': provides,
                                     'text': text if special else None}
            rec['name']['en'] = e0['name']
            rec['en_print'] = en_print(best, primary)
            rec['source_ids']['pokemontcg'] = sorted((c['id'] for c in best), key=lambda i: num_key(i.split('-')[1]))
            matched_en.update(c['id'] for c in best)
            records.append(rec)

    for source, label in JA_SOURCES:  # 先に並べた出典ほど優先（手入力の ja_text.json はさらに優先）
        src_path = ROOT / 'data' / f'ja_text_{source}.json'
        if not src_path.exists():
            continue
        pairs, unmatched = match_ja_source(records, load_json(src_path), load_json(cur / f'{source}_map.json'))
        report = []
        for r, c in pairs:
            apply_ja_source(r, c, report, label)
        review = load_json(cur / f'{source}_review.json')
        unreviewed = [x for x in report if f'{x[0]}|{x[1]}' not in review]
        if unreviewed:
            print(f'{source}: 未確認の食い違い（data/curation/{source}_review.json に判定を追加してください）:')
            for x in unreviewed:
                print('  ', x)
        with open(ROOT / 'data' / f'ja_text_{source}_report.json', 'w', encoding='utf-8') as f:
            json.dump({'unmatched': unmatched, 'differences': report}, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print(f'{source}: {len(pairs)} matched, {len(unmatched)} unmatched, {len(report)} differences')

    unknown = set(diffs) - {r['id'] for r in records} - {'_comment'}
    unknown |= set(ja_texts) - {r['id'] for r in records} - {'_comment', '_example'}
    if unknown:
        raise SystemExit(f'curation keys without a card: {sorted(unknown)}')
    en_only = [c for c in en.values()
               if c['_set'] in ('base1', 'base2', 'base3', 'base5', 'gym1', 'gym2', 'neo1', 'neo2', 'neo3', 'neo4')
               and c['id'] not in matched_en
               and not (c['supertype'] == 'Energy' and 'Basic' in c.get('subtypes', []))]
    return records, en_only


# ---- 日本語テキスト（なぞのばしょ・ポケモンWiki）の取り込み -----------------

# (出典名, 表示名)。data/ja_text_<出典名>.json と data/curation/<出典名>_{map,review}.json を使う
JA_SOURCES = [('nazonobasho', 'なぞのばしょ'), ('pokemonwiki', 'ポケモンWiki')]

JA_ENERGY = {'草': 'grass', '炎': 'fire', '水': 'water', '雷': 'lightning', '超': 'psychic',
             '闘': 'fighting', '無': 'colorless', '悪': 'darkness', '鋼': 'metal'}


def norm_name(s):
    import unicodedata
    return re.sub(r'[\s\[\]]', '', unicodedata.normalize('NFKC', s or ''))


def ja_cost(s):
    return sorted(JA_ENERGY[ch] for ch in (s or '') if ch in JA_ENERGY)


def attack_sig_en(p):
    return [(sorted(a['cost']), dmg_digits((a['damage'] or {}).get('display'))) for a in p['attacks']]


def attack_sig_ja(c):
    return [(ja_cost(a['cost']), dmg_digits(a['damage'])) for a in c['attacks']]


def match_score(r, c):
    """出典のカード c とレコード r の一致度。出典には名前・数値とも誤記があるため、
    名前・HP・ワザの数・コスト・ダメージの一致を合計して判定する。"""
    sc = 2 if norm_name(c['fields'].get('カード名称')) == norm_name(r['name']['ja']) else 0
    if c.get('hint_id') == r['id']:  # 出典側で付けた対応（ポケモンWiki の保存データ）
        sc += 3
    p = r['pokemon']
    if not p or not (c['attacks'] or c['powers']):
        return sc
    if str(p['hp']) == str(c['fields'].get('HP')):
        sc += 2
    if len(p['attacks']) == len(c['attacks']):
        sc += 1
    for (cost, dmg), (jcost, jdmg) in zip(attack_sig_en(p), attack_sig_ja(c)):
        sc += (cost == jcost) + (dmg == jdmg)
    return sc


def match_ja_source(records, data, manual):
    """出典のカードをレコードに対応付ける。戻り値は [(record, card)] と未対応のリスト。"""
    pairs, unmatched = [], []
    for page, info in data['sets'].items():
        set_id = info['tcgdex_set']
        if not set_id:
            continue
        pool = [r for r in records if r['jp_set'] == set_id]
        used = set()
        for c in info['cards']:
            slug = urllib.parse.unquote(c['url'].rstrip('/').rsplit('/', 1)[-1])
            unown = re.search(r'unknown-([a-z])$', slug)
            if slug in manual:
                if manual[slug] is None:
                    continue
                cands = [r for r in pool if r['id'] == manual[slug]]
            elif unown:  # アンノーンは能力違いで数値が同じなので、URL の文字で対応付ける
                cands = [r for r in pool if r['name']['ja'] == f'アンノーン{unown.group(1).upper()}']
            else:
                scored = sorted(((match_score(r, c), r) for r in pool if r['id'] not in used),
                                key=lambda x: -x[0])
                top = scored[0][0] if scored else 0
                cands = [r for sc, r in scored if sc == top] if top >= 2 else []
            if len(cands) != 1:
                unmatched.append((page, slug, c['fields'].get('カード名称'), [r['id'] for r in cands]))
                continue
            used.add(cands[0]['id'])
            pairs.append((cands[0], c))
    return pairs, unmatched


def ja_wr(s):
    """「炎×2」「闘-30」「なし」を構造化する。"""
    m = re.fullmatch(r'([草炎水雷超闘無悪鋼])\s*([×x+\-－])\s*(\d+)', (s or '').strip())
    if not m:
        return []
    op = {'x': '×', '－': '-'}.get(m.group(2), m.group(2))
    return [{'type': JA_ENERGY[m.group(1)], 'operator': op, 'value': int(m.group(3))}]


def fill_jp_only(p, c):
    f = c['fields']
    if str(f.get('HP', '')).isdigit():
        p['hp'] = int(f['HP'])
    if f.get('にげる'):
        p['retreat_cost'] = len([ch for ch in f['にげる'] if ch in JA_ENERGY])
    p['weaknesses'], p['resistances'] = ja_wr(f.get('弱点')), ja_wr(f.get('抵抗力'))
    p['powers'] = [{'kind': 'pokemon_power', 'name': {'ja': x['name'], 'en': None},
                    'text': {'ja': x['text'], 'en': None}} for x in c['powers']]
    p['attacks'] = []
    for x in c['attacks']:
        cost = [JA_ENERGY[ch] for ch in (x['cost'] or '') if ch in JA_ENERGY]
        dmg = (x['damage'] or '').replace('＋', '+').replace('x', '×').replace('X', '×').strip()
        p['attacks'].append({'name': {'ja': x['name'], 'en': None}, 'cost': cost, 'cost_total': len(cost),
                             'damage': parse_damage(dmg), 'text': {'ja': x['text'], 'en': None}})


def none_or(v):
    return None if v in (None, '', 'n/a') else v


def apply_ja_source(r, c, report, label):
    """対応付けたカードの日本語テキストをレコードに入れ、日英の数値の食い違いを report に記録する。"""
    if r['jp_print'] and r['ja_text_source']:  # 先の出典で埋まっている
        return
    f = c['fields']
    lv = f.get('LV.')
    r['jp_print'] = {
        'level': int(lv) if lv and lv.isdigit() else None,
        'rarity': none_or(f.get('レアリティ')),
        'series': none_or(f.get('シリーズ')),
        'remarks': [x.lstrip('・').strip() for x in (none_or(f.get('備考')) or '').split('\n') if x.strip()],
        'source': c['url'],
    }
    if r['ja_text_source']:  # ja_text.json（手入力）を優先
        return
    r['ja_text_source'] = c['url']
    jname = c['fields'].get('カード名称')
    if norm_name(jname) != norm_name(r['name']['ja']):
        report.append((r['id'], 'name', r['name']['ja'], jname))
    elif not r['pokemon']:
        # トレーナー・エネルギーの名前が、別系統の出典と一致したら確度を一段上げる
        r['name_ja_confidence'] = {'未確認': '有力', '有力': '確実'}.get(r['name_ja_confidence'], r['name_ja_confidence'])
    p = r['pokemon']
    if p and r['en_print'] is None:  # 英語版のない日本のみのカード: 数値・ワザも日本語の出典から作る
        fill_jp_only(p, c)
        return
    if p:
        if len(c['powers']) == len(p['powers']):
            for pw, jp in zip(p['powers'], c['powers']):
                pw['name']['ja'], pw['text']['ja'] = jp['name'], jp['text']
        else:
            report.append((r['id'], 'powers_count', len(p['powers']), len(c['powers'])))
        if len(c['attacks']) == len(p['attacks']):
            for a, ja in zip(p['attacks'], c['attacks']):
                a['name']['ja'], a['text']['ja'] = ja['name'], ja['text']
                if sorted(a['cost']) != ja_cost(ja['cost']):
                    report.append((r['id'], 'cost', f"{a['name']['en']} {a['cost']}", ja['cost']))
                if dmg_digits((a['damage'] or {}).get('display')) != dmg_digits(ja['damage']):
                    report.append((r['id'], 'damage', f"{a['name']['en']} {(a['damage'] or {}).get('display')}", ja['damage']))
        else:
            report.append((r['id'], 'attacks_count', len(p['attacks']), len(c['attacks'])))
        hp = c['fields'].get('HP')
        if hp and str(p['hp']) != hp:
            report.append((r['id'], 'hp', p['hp'], hp))
        retreat = c['fields'].get('にげる')
        if retreat and retreat != 'n/a' and len(ja_cost(retreat)) != p['retreat_cost']:
            report.append((r['id'], 'retreat', p['retreat_cost'], retreat))
        if c.get('rules_text') and p['rules_text']:
            p['rules_text']['ja'] = c['rules_text']
    else:
        target = r['trainer'] or r['energy']
        if target and target.get('text') is not None:
            target['text']['ja'] = c['text']


# ---- 出力 ----------------------------------------------------------------

def types_ja(types):
    return '・'.join(TYPE_JA[t] for t in types)


def cost_ja(cost):
    return ''.join(TYPE_JA[t][0] if t != 'colorless' else '無' for t in cost) or '―'


def wr_ja(items):
    return '、'.join(f"{TYPE_JA[w['type']]}{w['operator']}{w['value']}" for w in items) or 'なし'


def kind_ja(r):
    if r['pokemon']:
        return 'ポケモン'
    if r['energy']:
        return '特殊エネルギー' if r['energy']['kind'] == 'special' else '基本エネルギー'
    kinds = r['trainer']['kinds']
    return 'トレーナー' + (f"（{'・'.join(TRAINER_KIND_JA[k] for k in kinds)}）" if kinds else '')


def rarity_ja(r):
    rj = r['rarity_jp']
    if rj['code'] == 'special':
        return '特殊'
    return rj['mark'] + ('キラ' if rj['code'] == 'holo_rare' else '')


def en_ref(r):
    p = r['en_print']
    return f"{p['set_name']} {'・'.join(p['numbers'])}" if p else ''


REPRINT_DIFF_JA = {'cost': 'コスト', 'damage': 'ダメージ', 'text': '文面', 'weakness': '弱点', 'resistance': '抵抗力',
                   'retreat': 'にげる'}


def reprint_ref(x):
    ref = f"{EN_SET_ABBR[x['set_id']]} {x['number']}"
    if x.get('differences'):
        ref += f"（{'・'.join(REPRINT_DIFF_JA[d] for d in x['differences'])}が違う）"
    return ref


def md(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def name_cell(r):
    ja = r['name']['ja']
    if not ja:
        return '（公式名未確認）'
    return md(ja) + (' ※' if r['name_ja_confidence'] == '未確認' else '')


def both(b):
    """{ja, en} を「日本語 / English」の 1 行にする。"""
    if b is None:
        return ''
    parts = [x for x in (b.get('ja'), b.get('en')) if x]
    return ' / '.join(parts)


def write_json(records):
    doc = {
        'schema_version': SCHEMA_VERSION,
        'description': '旧裏（1996〜2001年）の日本版拡張パック10弾の全カードと、対応する英語版（WotC）カード。スキーマは docs/data-schema.md を参照。',
        'text_availability': {
            'en': 'ワザ・ポケモンパワー・トレーナー・特殊エネルギーの英語版の名前と文面は全件収録（PokemonTCG/pokemon-tcg-data）。',
            'ja': 'カード名は収録。ワザ名・ポケモンパワー名・効果文の日本語版は、なぞのばしょ・ポケモンWiki の転記（出典は各カードの ja_text_source）と data/curation/ja_text.json から収録し、出典にないものは null。英語からの翻訳は入れていない。',
        },
        'cards': records,
    }
    with open(ROOT / 'data' / 'cards.json', 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')


def write_csvs(records):
    d = ROOT / 'data'
    with open(d / 'cards.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'jp_set', 'seq', 'category', 'name_ja', 'name_en', 'name_ja_confidence',
                    'rarity_jp', 'holo', 'en_set', 'en_numbers', 'stage', 'evolves_from_ja', 'evolves_from_en',
                    'hp', 'types', 'weaknesses', 'resistances', 'retreat_cost', 'trainer_kinds',
                    'energy_kind', 'text_ja', 'text_en', 'jp_en_differences', 'notes'])
        for r in records:
            p, t, e = r['pokemon'], r['trainer'], r['energy']
            text = (t or {}).get('text') or (e or {}).get('text') or (p or {}).get('rules_text') or {}
            w.writerow([r['id'], r['jp_set'], r['seq'], r['category'], r['name']['ja'] or '', r['name']['en'] or '',
                        r['name_ja_confidence'] or '', r['rarity_jp']['code'], r['rarity_jp']['holo'],
                        (r['en_print'] or {}).get('set_id', ''), ' '.join((r['en_print'] or {}).get('numbers', [])),
                        (p or {}).get('stage') or '',
                        ((p or {}).get('evolves_from') or {}).get('ja') or '',
                        ((p or {}).get('evolves_from') or {}).get('en') or '',
                        (p or {}).get('hp') or '', ' '.join((p or {}).get('types', [])),
                        ' '.join(f"{x['type']}{x['operator']}{x['value']}" for x in (p or {}).get('weaknesses', [])),
                        ' '.join(f"{x['type']}{x['operator']}{x['value']}" for x in (p or {}).get('resistances', [])),
                        '' if p is None or p['retreat_cost'] is None else p['retreat_cost'],
                        ' '.join((t or {}).get('kinds', [])), (e or {}).get('kind', ''),
                        text.get('ja') or '', text.get('en') or '',
                        ' / '.join(f"[{x['kind']}] {x['summary']}" for x in r['jp_en_differences']),
                        ' / '.join(r['notes'])])
    with open(d / 'attacks.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['card_id', 'index', 'name_ja', 'name_en', 'cost', 'cost_total',
                    'damage_base', 'damage_modifier', 'damage_display', 'text_ja', 'text_en'])
        for r in records:
            for i, a in enumerate((r['pokemon'] or {}).get('attacks', []), 1):
                dmg = a['damage'] or {}
                w.writerow([r['id'], i, a['name']['ja'] or '', a['name']['en'], ' '.join(a['cost']), a['cost_total'],
                            '' if dmg.get('base') is None else dmg['base'], dmg.get('modifier') or '',
                            dmg.get('display') or '', a['text']['ja'] or '', a['text']['en'] or ''])
    with open(d / 'powers.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['card_id', 'index', 'kind', 'name_ja', 'name_en', 'text_ja', 'text_en'])
        for r in records:
            for i, a in enumerate((r['pokemon'] or {}).get('powers', []), 1):
                w.writerow([r['id'], i, a['kind'], a['name']['ja'] or '', a['name']['en'],
                            a['text']['ja'] or '', a['text']['en'] or ''])


def card_detail(r):
    """カード 1 枚分の詳細（Markdown）。"""
    title = r['name']['ja'] or '（公式名未確認）'
    if r['name']['en']:
        title += f" / {r['name']['en']}"
    lines = [f"### {r['seq']}. {title}", '']
    head = [kind_ja(r)]
    p = r['pokemon']
    if p:
        evo = f"（{both(p['evolves_from'])} から進化）" if p['evolves_from'] else ''
        lv = (r['jp_print'] or {}).get('level')  # 英語版データのレベルには誤りがあるため使わない
        head = [f"{STAGE_JA.get(p['stage'], '')}{evo}"] + ([f"LV.{lv}"] if lv else []) + [types_ja(p['types']), f"HP {p['hp']}",
                f"弱点 {wr_ja(p['weaknesses'])}", f"抵抗力 {wr_ja(p['resistances'])}",
                f"にげる {p['retreat_cost'] if p['retreat_cost'] is not None else '?'}"]
    head.append(f"レア {rarity_ja(r)}")
    lines.append('／'.join(head))
    lines.append('')
    lines.append(f"英語版: {en_ref(r) or 'なし'}")
    lines.append('')
    if p:
        if p['rules_text']:
            lines += [f"- ルール: {both(p['rules_text'])}"]
        for pw in p['powers']:
            lines.append(f"- {POWER_KIND_JA[pw['kind']]}「{both(pw['name'])}」")
            if pw['text']['ja']:
                lines.append(f"  - 日本語: {pw['text']['ja']}")
            if pw['text']['en']:
                lines.append(f"  - 英語: {pw['text']['en']}")
        if p['powers'] or p['rules_text']:
            lines.append('')
        if p['attacks']:
            lines += ['| ワザ | エネルギー | ダメージ | 効果 |', '|---|---|---:|---|']
            for a in p['attacks']:
                effect = ' '.join(x for x in (f"日本語: {a['text']['ja']}" if a['text']['ja'] else '',
                                             f"英語: {a['text']['en']}" if a['text']['en'] else '') if x)
                lines.append(f"| {md(both(a['name']))} | {cost_ja(a['cost'])} | "
                             f"{md((a['damage'] or {}).get('display', ''))} | {md(effect)} |")
            lines.append('')
    else:
        text = (r['trainer'] or r['energy'] or {}).get('text')
        if text:
            if text['ja']:
                lines.append(f"- 日本語: {text['ja']}")
            if text['en']:
                lines.append(f"- 英語: {text['en']}")
            lines.append('')
    if r['ja_text_source']:
        src = r['ja_text_source']
        site = ('なぞのばしょ' if 'nazonobasho.com' in src else 'ポケモンWiki' if 'pokemonwiki.com' in src
                else 'ポケモンカード 旧シリーズ検索' if 'pcg-search.com' in src else src)
        lines.append(f"- 日本語テキストの出典: [{site}]({src})" if src.startswith('http') else f"- 日本語テキストの出典: {src}")
    for d in r['jp_en_differences']:
        lines.append(f"- **日英の違い（{d['summary']}、確度: {d['confidence']}）** 日本版: {d['ja']} ／ 英語版: {d['en']}")
    for n in r['notes']:
        lines.append(f"- 備考: {n}")
    jpp = r['jp_print'] or {}
    if jpp.get('series'):
        lines.append(f"- 日本版の収録商品: {jpp['series']}")
    for n in jpp.get('remarks', []):
        lines.append(f"- 日本版の印刷について: {n}")
    if r['jp_en_differences'] or r['notes'] or r['ja_text_source'] or jpp:
        lines.append('')
    return lines


def write_set_docs(records, en_only):
    out = ROOT / 'docs' / 'cards'
    out.mkdir(parents=True, exist_ok=True)
    set_meta = load_json(ROOT / 'data' / 'curation' / 'sets.json')
    for set_id, slug, primary, _ in JP_SETS:
        meta = set_meta[set_id]
        rs = [r for r in records if r['jp_set'] == set_id]
        lines = [f"# {meta['ja']}（{meta['label']}）", '',
                 f"- 発売日: {meta['release']}",
                 f"- 収録枚数: {meta['count']}",
                 f"- 主に対応する英語版: {meta['en']}", '',
                 '## カード一覧', '',
                 '備考の「再録」は英語版の別セット（Base Set 2・Legendary Collection・プロモなど）への再録です。'
                 '「（文面が違う）」などは、英語版データの上で元のカードと欄が違うもの（多くは書き方の統一による言い換え）です。'
                 '判定の方法と点検の結果は [再録カードの対応付け](reprints.md) にあります。', '',
                 '| No. | 日本語名 | 種類 | タイプ | 進化 | HP | レア | 英語版（WotC） | 備考 |',
                 '|---:|---|---|---|---|---:|---|---|---|']
        for r in rs:
            p = r['pokemon']
            en_cell = f"{md(r['name']['en'])}<br>{en_ref(r)}" if r['en_print'] else '（英語版なし）'
            if r['en_print'] and r['en_print']['differs_from_primary']:
                en_cell += ' ⚠'
            notes = [f"日英の違い: {d['summary']}" for d in r['jp_en_differences']] + list(r['notes'])
            if r['en_reprints']:
                notes.append('再録: ' + '、'.join(reprint_ref(x) for x in r['en_reprints']))
            lines.append('| {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
                r['seq'], name_cell(r), kind_ja(r), types_ja(p['types']) if p else '',
                STAGE_JA.get(p['stage'], '') if p else '', p['hp'] if p else '',
                rarity_ja(r), en_cell, '<br>'.join(md(n) for n in notes)))
        moved = [r for r in rs if r['en_print'] and r['en_print']['differs_from_primary']]
        lines += ['', '## 英語版との対応メモ', '']
        if moved:
            lines += [f"⚠ 印のカードは、英語版では {meta['en']} 以外のセットに収録されています。", '']
            lines += [f"- {r['name']['ja'] or '（公式名未確認）'} → {r['name']['en']}（{en_ref(r)}）" for r in moved]
        else:
            lines.append(f"日本版の全カードが {meta['en']} に収録されています。")
        jo = [r for r in rs if not r['en_print']]
        if jo:
            lines += ['', '英語版に対応カードがないもの:', '']
            lines += [f"- {r['name']['ja']}：{'／'.join(r['notes'])}" for r in jo]
        eo = sorted([c for c in en_only if c['_set'] == primary], key=lambda c: num_key(c['number']))
        if eo:
            lines += ['', f"{meta['en']} にあって、日本版の本弾に収録されていないカード（基本エネルギー除く）:", '']
            lines += [f"- {c['number']} {c['name']}" for c in eo]
        sites = [label for source, label in JA_SOURCES if any(source in (r['ja_text_source'] or '') for r in rs)]
        lines += ['', '## カード詳細', '', JA_TEXT_PRESENT.format(sites='、'.join(sites)) if sites else JA_TEXT_MISSING, '',
                  'エネルギーの記号: 草・炎・水・雷・超・闘・悪・鋼、無 = 無色。', '']
        for r in rs:
            lines += card_detail(r)
        lines += ['---', '', '凡例・出典は [カードリストの見かた](README.md) を参照。', '']
        (out / f'{slug}.md').write_text('\n'.join(lines), encoding='utf-8')

    origins = jp_origins()
    lines = ['# 英語版のみに見られるカード（日本の拡張パック未収録）', '',
             '英語版（WotC）の各セットに収録されているが、日本の旧裏拡張パック 10 弾のどれにも対応カードが見つからないもの。',
             '基本エネルギーは除外。', '',
             '「日本での初出」は、拡張パック以外の商品（ジムデッキ、拡張シート、プレミアムファイル、プロモなど）の調査から、'
             '同じカードが日本で最初に出た商品を付けたものです（[拡張パック以外の商品](other-products.md)）。', '']
    for s in ['base1', 'base2', 'base3', 'base5', 'gym1', 'gym2', 'neo1', 'neo2', 'neo3', 'neo4']:
        eo = sorted([c for c in en_only if c['_set'] == s], key=lambda c: num_key(c['number']))
        lines += [f'## {EN_SET_NAMES[s]}', '']
        if not eo:
            lines += ['（なし）', '']
            continue
        lines += [f'{len(eo)} 枚', '', '| 番号 | カード名 | 日本での初出 | 日本語名 |', '|---|---|---|---|']
        for c in eo:
            o = origins.get((s, c['number']))
            first = f"{o[0][1]}（{o[0][0]}）" if o else '未確認'
            lines.append(f"| {c['number']} | {c['name']} | {first} | {o[0][2] if o else ''} |")
        lines.append('')
    (out / 'english-only.md').write_text('\n'.join(lines), encoding='utf-8')


DIFF_KIND_JA = {'text': '文面の意味', 'numbers': '数値', 'errata': 'エラッタ', 'placement': '収録先', 'print': '英語版の表記・誤植',
                'wording': '書き方（意味は同じ）', 'art': 'イラスト',
                'regulation': '大会での扱い'}


def jp_origins():
    """英語版のカード (セット id, 番号) → 日本で同じカードが出た拡張パック以外の商品 [(日付, 商品名, 日本語名)]（日付順）。
    data/curation/other_products.json の英語版の対応と、data/ja_text_pcgsearch.json のカードから作る。"""
    cur_path, data_path = ROOT / 'data' / 'curation' / 'other_products.json', ROOT / 'data' / 'ja_text_pcgsearch.json'
    if not (cur_path.exists() and data_path.exists()):
        return {}
    cur, data = load_json(cur_path), load_json(data_path)['products']
    products = {p['pcg_title']: p for p in cur['products']}
    promos = cur.get('promos', {})
    def sig(c):  # 同じカードの判定（build_other_products.py と同じ考え方: 名前・HP・特殊能力名・ワザ名）
        return (norm_name(c['name']).replace('ウィンディ', 'ウインディ'), c.get('hp'),
                tuple(norm_name(x['name']) for x in c['powers']), tuple(norm_name(a['name']) for a in c['attacks']))
    page_of, by_sig = {}, {}
    for key, cards in data.items():
        for c in cards:
            page = c['url'].rsplit('/', 1)[-1][:-len('.php')]
            date = (promos.get(page) or {}).get('date') or products[key].get('release_date') or '9999'
            page_of[page] = c
            by_sig.setdefault(sig(c), []).append((date, products[key]['name'], c['name']))
    out = {}
    for page, e in cur['en_prints'].items():
        if page in page_of:
            out.setdefault((e['set_id'], e['number']), set()).update(by_sig[sig(page_of[page])])
    return {k: sorted(v) for k, v in out.items()}


def write_card_differences(records):
    lines = ['# カードの日英の違い', '',
             '<!-- このファイルは scripts/build_cardlist.py が data/curation/card_differences.json から生成しています。直接編集しないでください。 -->', '',
             '日本版と英語版（WotC 版）で、文面の意味・エラッタ・収録先・表記・書き方・イラストが違うと指摘されているカードの一覧です。',
             'ルールの違いは [日米のルールの違い](../rules/differences.md)、弾ごとの収録内容の違いは [収録内容・製品の違い](set-differences.md) を参照してください。', '',
             '- 英語版の文面は英語版カードデータ（pokemon-tcg-data）で確認したもの。日本版の文面は、なぞのばしょ [N1]・ポケモンWiki [N2] の転記で確認できたものは「」で引用し、それ以外は二次資料の説明によるものです。',
             '- 日英の文面を全カードで厳密に突き合わせたわけではありません。ここに挙げたのは、二次資料で指摘されたもの、特殊能力が使えなくなる状態の書き方を機械的に比べて見つかったもの、リーダーズスタジアムのワザ・特殊能力・トレーナーと、ポケモンWiki から取り込んだほかの弾のトレーナーの文面を読み比べて見つかったものです。',
             '- jklacz は「WotC 期の約 50 枚が誤訳されており、ほとんどは訂正されないままだった（多くはエネルギー記号の誤りなどの小さなもの）」としています [X3]。ここに挙げたのは、そのうち内容を確認できたものだけです。',
             '- 出典の記号は [出典と確認状況](../sources.md)、データは `data/cards.json` の `jp_en_differences` にあります。', '',
             '| カード | 種類 | 内容 | 日本版 | 英語版 | 確度 | 出典 |', '|---|---|---|---|---|---|---|']
    for r in records:
        for d in r['jp_en_differences']:
            name = f"{r['name']['ja']} / {r['name']['en']}<br>（{r['jp_set']}・{en_ref(r)}）"
            lines.append('| {} | {} | {} | {} | {} | {} | {} |'.format(
                md(name).replace('&lt;br&gt;', '<br>'), DIFF_KIND_JA[d['kind']], md(d['summary']), md(d['ja']), md(d['en']),
                d['confidence'], ''.join(f'[{s}]' for s in d['sources']) or '―'))
    lines += ['', '## 日本の拡張パックにないカードの例', '',
              '- オーダイル（英語版 Neo Genesis 5 の Riptide。日本では neo プレミアムファイル）: 日本版は、追加ダメージを山札にもどす水エネルギーの枚数で数えると明記している。英語版は数える対象があいまい [X3]（有力）', '',
              '## 情報源が 1 件だけで、裏付けが取れていない指摘（未確認）', '',
              '- わるいゴルバット（Team Rocket）の弱点・抵抗力の扱い',
              '- メリープ（Neo Genesis）の Static Electricity の対象',
              '- ひかるライチュウ（Neo Destiny）の Thundersquall でエネルギーをトラッシュするか',
              '- ふうせんのみ（Neo Revelation）の文面', '']
    (ROOT / 'docs' / 'cards' / 'card-differences.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jp', required=True)
    ap.add_argument('--en', required=True, help='pokemon-tcg-data のパス')
    ap.add_argument('--species', required=True)
    args = ap.parse_args()
    records, en_only = build_records(args)
    write_json(records)
    write_csvs(records)
    write_set_docs(records, en_only)
    write_card_differences(records)
    print(f'{len(records)} cards, {len(en_only)} english-only')


if __name__ == '__main__':
    main()
