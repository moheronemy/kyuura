"""拡張パック以外の商品のカードを、data/cards.json の記録の形に正規化する（scripts/build_cardlist.py から使う）。

入力（どれもリポジトリの中のファイル。ネットワークは使わない）:
  - data/ja_text_pcgsearch.json: pcg-search.com の転記（scripts/pcg_search.py extract の出力。ここでは書き換えない）
  - data/pcgsearch_page_checks.json: 進化元・にげるなどを確かめるために、同じサイトの同じ版のページを読み直した抽出
    （scripts/pcg_search.py extract-pages の出力）
  - data/ja_text_nazonobasho.json: サザンアイランドのレベル（なぞのばしょの転記）
  - data/curation/other_products.json: 商品の名前・発売日・構成、英語版の対応、日英の違い、名前の確認、数値の判定
  - data/curation/non_pack.json: 商品の記号、番号違いのまとめ、対戦のカードでない項目、補足欄の役割、使える範囲

カード id は「商品の記号-カードページ名の末尾 3 桁」（例 GD1-009 = 1stgymd1009）。サイトの並び順（list_number）は使わないので、
並び順が変わっても id は変わらない。同じ商品の中で番号だけが違うページ（イントロパックのデッキ）は 1 つの記録にまとめ、
いちばん小さいページの番号を id にする。

正規化の規則（欄ごとの出どころは、記録の field_sources に書く）:
  - 名前・段階・HP・タイプ・弱点・抵抗力・にげる・特殊能力・ワザ・本文は pcg-search の転記。英語版の文面で補わない。
  - 進化元（pokemon.evolves_from）は、(1) 同じカードの拡張パックの記録（名前・HP・特殊能力名・ワザ名が同じ）、
    (2) 同じサイトのカードページの「進化ライン検索」の 1 つ前の段階の名前（1 つに決まるときだけ）の順に使う。
    (2) は、進化ラインでそのページのカードの位置の段階が、サイトの種類の欄（記録の段階）と同じときだけ使う。違えば段階を
    不足（data_gaps の pokemon.stage）にして進化元を入れない。
    名前の接頭辞から推測しない。英語版の進化元は照らし合わせに使うだけで、値にしない。どちらもなければ null（data_gaps）。
  - にげる: 転記の null は、サイトの欄の「-」（にげるエネルギーなし。0）か空欄。読み直したページで「-」を確かめたものは
    「-」、ほかは転記の null を 0 と読んだもの（field_sources に区別して書く）。
  - 英語の欄（name.en・ワザなどの en）は、英語版の対応（other_products.json の en_prints）、または同じカードの拡張パックの記録から。
    日本語の欄を英語版で埋めない。
"""
import difflib
import json
import re
import unicodedata
from pathlib import Path

KIND = {
    'たねポケモン': ('pokemon', 'basic'), '１進化ポケモン': ('pokemon', 'stage1'), '２進化ポケモン': ('pokemon', 'stage2'),
    'ベイビィポケモン': ('pokemon', 'baby'),
    'トレーナー': ('trainer', []), 'スタジアム': ('trainer', ['stadium']), 'ポケモンのどうぐ': ('trainer', ['pokemon_tool']),
    '基本エネルギー': ('energy', 'basic'), '特殊エネルギー': ('energy', 'special'),
}
NON_GAME_PCG_KINDS = {'EXTRA RULE', 'デッキ', 'PASS CARD', 'その他', 'ILLUSTRATOR'}
JA_TYPE = {'草': 'grass', '炎': 'fire', '水': 'water', '雷': 'lightning', '超': 'psychic', '闘': 'fighting',
           '無': 'colorless', '悪': 'darkness', '鋼': 'metal'}
RARITY = {  # pcg-search のレアリティの表記 → rarity_jp（code, mark, holo）
    '●': ('common', '●', False), '◆': ('uncommon', '◆', False), '★': ('rare', '★', False),
    '★(キラ)': ('holo_rare', '★', True),
    '-': ('no_mark', None, False), '-(キラ)': ('no_mark', None, True),
    '★★(キラ)': ('special', None, True), '★★★(キラ)': ('special', None, True), '☆(キラ)': ('special', None, True),
}
NAME_FIX = {'ウィンディ': 'ウインディ'}  # サイトの表記の揺れ（同じカードの判定だけに使う）
STAGE_BEFORE = {'stage1': 'evoBasic', 'stage2': 'evoStage1'}
LINE_STAGE = {'baby': 'evoBaby', 'basic': 'evoBasic', 'stage1': 'evoStage1', 'stage2': 'evoStage2'}  # サイトの進化ラインの区分
STAGE_CONFLICT = 'pcg_search_kind_conflicts_with_evolution_line'


def load(root, rel):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def page_id(url):
    return url.rsplit('/', 1)[-1].removesuffix('.php')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    for a, b in NAME_FIX.items():
        s = s.replace(a, b)
    return re.sub(r'[\s\[\]・,、]', '', s).replace('?', '？')


def without_english(s):
    """名前の英語の併記（「ナッシー［Exeggutor］」の［…］）を除く。"""
    return re.sub(r'\[[^\]]*\]', '', unicodedata.normalize('NFKC', s or ''))


def plain_ja(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s。、・「」『』()（）,.!?\[\]【】]', '', s)


def ja_damage(s):
    """pcg-search のダメージの表記（"20"、"30+"、"10×"、"40-"）を構造化する。数値でない表記はエラー。"""
    if s is None:
        return None
    m = re.fullmatch(r'(\d+)([+×\-])?', s)
    if not m:
        raise SystemExit(f'pcg-search のダメージの表記が読めない: {s!r}')
    return {'base': int(m.group(1)), 'modifier': m.group(2), 'display': s}


def ja_wr(s):
    """「超×2」「闘-30」→ [{type, operator, value}]。null は空。"""
    if s is None:
        return []
    m = re.fullmatch(r'([草炎水雷超闘無悪鋼])([×\-+])(\d+)', s)
    if not m:
        raise SystemExit(f'pcg-search の弱点・抵抗力の表記が読めない: {s!r}')
    return [{'type': JA_TYPE[m.group(1)], 'operator': m.group(2), 'value': int(m.group(3))}]


def ja_cost(s):
    out = []
    for ch in s or '':
        if ch not in JA_TYPE:
            raise SystemExit(f'pcg-search のエネルギーの記号が読めない: {s!r}')
        out.append(JA_TYPE[ch])
    return out


def bilingual(ja, en=None):
    return {'ja': ja, 'en': en}


def same_content(a, b):
    """同じ商品の中で、番号（list_number）とページ（url）のほかがすべて同じか。"""
    strip = lambda c: {k: v for k, v in c.items() if k not in ('list_number', 'url')}
    return strip(a) == strip(b)


class NonPack:
    """拡張パック以外の商品の、正規化した記録と、元の項目の一覧。"""

    def __init__(self, root: Path, en_cards: dict, namer=None):
        self.root = root
        self.en = en_cards
        self.namer = namer
        self.data = load(root, 'data/ja_text_pcgsearch.json')['products']
        self.cur = load(root, 'data/curation/other_products.json')
        self.np = load(root, 'data/curation/non_pack.json')
        checks_path = root / 'data' / 'pcgsearch_page_checks.json'
        self.checks = load(root, 'data/pcgsearch_page_checks.json')['pages'] if checks_path.exists() else {}
        self.products = {p['pcg_title']: p for p in self.cur['products']}
        nz = load(root, 'data/ja_text_nazonobasho.json')['sets'].get('cardlist-pmcg-southernisland', {}).get('cards', [])
        self.si_level = {c['fields'].get('カード名称'): c['fields'].get('LV.') for c in nz}
        missing = set(self.data) - set(self.np['products'])
        if missing:
            raise SystemExit(f'data/curation/non_pack.json に商品の記号がない: {sorted(missing)}')
        codes = [v['code'] for v in self.np['products'].values()]
        if len(codes) != len(set(codes)):
            raise SystemExit('data/curation/non_pack.json の商品の記号が重複している')

    # ---- 元の項目 → 記録・まとめ・対象外 -------------------------------------------------
    def build(self):
        records, items, non_game = [], [], []
        ng = {k: v for k, v in self.np['non_game_items'].items() if not k.startswith('_')}
        seen_ng = set()
        for title, cards in self.data.items():
            meta = self.np['products'][title]
            code, prefix = meta['code'], meta['page_prefix']
            prod = self.products.get(title, {})
            groups = []  # [(代表の項目, [項目])]
            for c in cards:
                pid = page_id(c['url'])
                if not re.fullmatch(re.escape(prefix) + r'\d{3}', pid):
                    raise SystemExit(f'カードページ名が商品の規則に合わない: {title} {pid}')
                if pid in ng:
                    seen_ng.add(pid)
                    item_id = f'{code}-{pid[-3:]}'
                    non_game.append({
                        'id': item_id, 'product': code, 'page': pid, 'url': c['url'], 'list_number': c['list_number'],
                        'kind': ng[pid]['kind'], 'pcg_kind': c['kind'], 'name': c['name'],
                        'display_name': (self.cur.get('identified_cards', {}).get(pid) or {}).get('name') if c['name'] == '-' else c['name'],
                        'text': c.get('text'), 'note': c.get('note'), 'attacks': c.get('attacks') or [],
                        'reason': ng[pid]['reason']})
                    items.append({'page': pid, 'url': c['url'], 'product': code, 'list_number': c['list_number'],
                                  'pcg_kind': c['kind'], 'name': c['name'], 'disposition': 'non_game', 'id': item_id})
                    continue
                if c['kind'] in NON_GAME_PCG_KINDS or c['kind'] not in KIND:
                    raise SystemExit(f'対戦のカードでない種類が non_pack.json の non_game_items にない: {pid} {c["kind"]}')
                target = None
                if meta.get('merge_numbered_copies'):
                    target = next((g for g in groups if same_content(g[0], c)), None)
                if target:
                    target[1].append(c)
                else:
                    groups.append((c, [c]))
            for seq, (rep, members) in enumerate(groups, 1):
                rec = self.record(title, code, prod, seq, rep, members)
                records.append(rec)
                for m in members:
                    items.append({'page': page_id(m['url']), 'url': m['url'], 'product': code, 'list_number': m['list_number'],
                                  'pcg_kind': m['kind'], 'name': m['name'],
                                  'disposition': 'card' if m is rep else 'copy', 'id': rec['id']})
        unknown = set(ng) - seen_ng
        if unknown:
            raise SystemExit(f'non_pack.json の non_game_items のページが転記にない: {sorted(unknown)}')
        ids = [r['id'] for r in records] + [x['id'] for x in non_game]
        if len(ids) != len(set(ids)):
            raise SystemExit('拡張パック以外の商品の id が重複している')
        return records, items, non_game

    def record(self, title, code, prod, seq, c, members):
        pid = page_id(c['url'])
        category, sub = KIND[c['kind']]
        cid = f'{code}-{pid[-3:]}'
        roles = self.np.get('note_roles', {})
        role = roles.get(pid, 'rules')
        notes, sources = [], {}
        ident = self.cur.get('identified_cards', {}).get(pid)
        name = ident['name'] if c['name'] == '-' and ident else c['name']
        code_r, mark, holo = RARITY.get(c['rarity'] or '-', (None, None, None))
        if code_r is None:
            raise SystemExit(f'pcg-search のレアリティの表記が読めない: {pid} {c["rarity"]!r}')
        rec = {
            'id': cid, 'jp_set': code, 'seq': seq, 'category': category,
            'name': bilingual(name), 'name_ja_confidence': '有力',
            'rarity_jp': {'code': code_r, 'mark': mark, 'holo': holo, 'source_label': c['rarity']},
            'en_print': None, 'en_reprints': [],
            'pokemon': None, 'trainer': None, 'energy': None,
            'jp_en_differences': [d for m in members for d in self.cur['differences'].get(page_id(m['url']), [])],
            'notes': notes,
            'source_ids': {'tcgdex': None, 'pokemontcg': [], 'pcg_search': [page_id(m['url']) for m in members]},
            'ja_text_source': c['url'],
            'jp_print': {'level': None, 'rarity': c['rarity'], 'series': title,
                         'remarks': [c['remarks']] if c.get('remarks') else [], 'source': c['url']},
            'product_group': prod.get('group'),
            'copies': [{'page': page_id(m['url']), 'list_number': m['list_number']} for m in members],
            'play_scope': 'standard',
            'field_sources': sources,
        }
        sources['name.ja'] = 'pcg_search' if c['name'] != '-' else 'other_products.identified_cards'
        scope = self.np.get('play_scope', {}).get(pid)
        if scope:
            rec['play_scope'] = scope['scope']
        text_parts = [c.get('text')]
        if c.get('note'):
            if role == 'rules':
                text_parts.append(c['note'])
            elif role in ('flavor', 'label'):
                notes.append(f"カードの補足欄（{'説明の文' if role == 'flavor' else '扱いの表示'}）: {c['note']}")
            else:
                raise SystemExit(f'non_pack.json の note_roles の値が不正: {pid} {role}')
        if category == 'pokemon':
            p = {
                'dex': [], 'stage': sub, 'evolves_from': None, 'hp': c.get('hp'),
                'types': ja_cost(c.get('type')),
                'weaknesses': ja_wr(c.get('weakness')), 'resistances': ja_wr(c.get('resistance')),
                'retreat_cost': len(ja_cost(c.get('retreat'))),
                'rules_text': bilingual(c['note']) if c.get('note') and role == 'rules' else None,
                'powers': [{'kind': 'pokemon_power', 'name': bilingual(x['name']), 'text': bilingual(x['text'])} for x in c['powers']],
                'attacks': [{'name': bilingual(a['name']), 'cost': ja_cost(a['cost']), 'cost_total': len(ja_cost(a['cost'])),
                             'damage': ja_damage(a['damage']), 'text': bilingual(a['text'])} for a in c['attacks']],
            }
            if c.get('text'):
                raise SystemExit(f'ポケモンの本文の欄に文がある（扱いを決める）: {pid}')
            rec['pokemon'] = p
            check = self.checks.get(pid, {})
            if c.get('retreat') is None:
                sources['pokemon.retreat_cost'] = ('pcg_search_page_dash' if check.get('retreat_raw') == '-'
                                                   else 'pcg_search_null_read_as_zero')
            else:
                sources['pokemon.retreat_cost'] = 'pcg_search'
            if p['rules_text']:
                sources['pokemon.rules_text.ja'] = 'pcg_search.note'
        elif category == 'trainer':
            rec['trainer'] = {'kinds': list(sub), 'text': bilingual('\n'.join(x for x in text_parts if x) or None)}
        else:
            if sub == 'basic':
                m = re.fullmatch(r'([草炎水雷超闘])エネルギー', c['name'])
                if not m:
                    raise SystemExit(f'基本エネルギーの名前が読めない: {pid} {c["name"]}')
                rec['energy'] = {'kind': 'basic', 'provides': [JA_TYPE[m.group(1)]], 'text': None}
            else:
                rec['energy'] = {'kind': 'special', 'provides': [],
                                 'text': bilingual('\n'.join(x for x in text_parts if x) or None)}
        if code == 'SI':
            lv = self.si_level.get(c['name'])
            if lv and lv.isdigit():
                rec['jp_print']['level'] = int(lv)
                sources['jp_print.level'] = 'nazonobasho（サザンアイランド）'
        en = self.cur['en_prints'].get(pid)
        if en:
            rec['en_print'] = {'set_id': en['set_id'], 'set_name': en['set_name'], 'numbers': [en['number']],
                               'differs_from_primary': None}
            rec['name']['en'] = en.get('name')
            sources['en_print'] = 'other_products.en_prints'
            ec = self.en.get(f"{en['set_id']}-{en['number']}")
            if ec:
                rec['source_ids']['pokemontcg'] = [ec['id']]
                self.fill_english(rec, ec, f"pokemontcg:{ec['id']}")
        check = self.checks.get(pid, {})
        if check.get('name') and norm(check['name']) != norm(c['name']):
            raise SystemExit(f'読み直したページの名前が転記と違う: {pid} {check["name"]} / {c["name"]}')
        return rec

    def fill_english(self, rec, ec, basis):
        """英語版のカードから英語の欄だけを入れる（並びが合うときだけ。日本語の欄・数値は変えない）。"""
        p = rec['pokemon']
        src = rec['field_sources']
        if p and ec.get('supertype') == 'Pokémon':
            atk, pw = ec.get('attacks', []), ec.get('abilities', [])
            if len(atk) == len(p['attacks']) and len(pw) == len(p['powers']):
                for a, e in zip(p['attacks'], atk):
                    a['name']['en'], a['text']['en'] = e['name'], e.get('text') or None
                for x, e in zip(p['powers'], pw):
                    x['name']['en'], x['text']['en'] = e['name'], e.get('text')
                src['english_text'] = basis
            if not p['dex'] and ec.get('nationalPokedexNumbers'):
                p['dex'] = ec['nationalPokedexNumbers']
                src['pokemon.dex'] = basis
        elif not p:
            target = rec['trainer'] or rec['energy']
            if target and target.get('text') is not None and ec.get('rules'):
                target['text']['en'] = ' '.join(ec['rules'])
                src['english_text'] = basis

    # ---- 進化元 -----------------------------------------------------------------------
    def evolution_line_name(self, rec):
        """同じサイトのカードページの「進化ライン検索」で、このカードの 1 つ前の段階の名前。

        戻り値: (名前の集合, 使わなかったページの一覧 [(ページ, 理由)])。サイトがそのページのカードとする位置（current）が 1 つで、
        名前（英語の併記［…］を除く）が記録の名前と同じで、その位置の段階が記録の段階（サイトの種類の欄）と同じページだけを使う。
        名前が違うページ（理由 "name:…"。例: 「わるい」のない名前）・段階が合わないページ（理由は進化ラインの区分。例: 種類は
        1 進化なのに、進化ラインではたねポケモンの位置）は使わない。
        """
        p = rec['pokemon']
        names, mismatches = set(), []
        for pid in rec['source_ids']['pcg_search']:
            line = self.checks.get(pid, {}).get('evolution_line')
            if not line:
                continue
            cur = [e for e in line if e['current']]
            if len(cur) != 1 or norm(without_english(cur[0]['name'])) != norm(without_english(rec['name']['ja'])):
                mismatches.append((pid, 'name:' + ' / '.join(e['name'] for e in cur)))  # 例: 「わるい」のない名前
                continue
            if cur[0]['stage'] != LINE_STAGE.get(p['stage']):
                mismatches.append((pid, cur[0]['stage']))
                continue
            names |= {e['name'] for e in line if e['stage'] == STAGE_BEFORE.get(p['stage']) and not e['current']}
        return names, mismatches


# ---- 同じカードの組（商品をまたいだ再録の候補） ----------------------------------------------

def signature(r):
    """同じカードの候補の鍵。ポケモンは名前・HP・特殊能力名・ワザ名、トレーナー・エネルギーは名前と種類。"""
    p = r['pokemon']
    if p:
        return ('pokemon', norm(r['name']['ja']), p['hp'], tuple(norm(x['name']['ja']) for x in p['powers']),
                tuple(norm(a['name']['ja']) for a in p['attacks']))
    if r['energy']:
        return ('energy', r['energy']['kind'], norm(r['name']['ja']))
    return ('trainer', tuple(r['trainer']['kinds']), norm(r['name']['ja']))


def numbers(r):
    p = r['pokemon']
    if not p:
        return None
    wr = lambda xs: [(x['type'], x['operator'], x['value']) for x in xs]
    return {'types': p['types'], 'weaknesses': wr(p['weaknesses']), 'resistances': wr(p['resistances']),
            'retreat_cost': p['retreat_cost'], 'stage': p['stage'],
            'attacks': [(sorted(a['cost']), (a['damage'] or {}).get('display')) for a in p['attacks']]}


def texts(r):
    p = r['pokemon']
    if p:
        return [x['text']['ja'] for x in p['powers']] + [a['text']['ja'] for a in p['attacks']] + \
               [(p['rules_text'] or {}).get('ja')]
    t = (r['trainer'] or r['energy'] or {}).get('text') or {}
    return [t.get('ja')]


def text_relation(a, b):
    ta, tb = texts(a), texts(b)
    if ta == tb:
        return 'same'
    if all((not x and not y) or (x and y and plain_ja(x) == plain_ja(y)) for x, y in zip(ta, tb)) and len(ta) == len(tb):
        return 'same_ignoring_punctuation'
    ratio = min((difflib.SequenceMatcher(None, plain_ja(x), plain_ja(y)).ratio() if x and y else (1.0 if not x and not y else 0.0))
                for x, y in zip(ta, tb)) if ta else 1.0
    return 'similar' if ratio >= 0.9 else 'different'


def link(records, np, pack_dates, product_dates, reprint_text, reprint_checks, namer=None):
    """同じカードの組を作り、拡張パック以外の記録の進化元・英語の欄を、組の拡張パックの記録・カードページから入れる。

    戻り値: (組の一覧, 照らし合わせの結果の一覧)。記録には same_card_group を入れる。
    """
    def date(r):
        if r['product_group'] == 'expansion_pack':
            return pack_dates[r['jp_set']]
        pid = r['source_ids']['pcg_search'][0]
        return (np.cur.get('promos', {}).get(pid) or {}).get('date') or product_dates.get(r['jp_set']) or '9999'

    by_sig = {}
    for r in records:
        by_sig.setdefault(signature(r), []).append(r)
    groups, checks = [], []
    for sig, members in by_sig.items():
        if len(members) < 2:
            members[0]['same_card_group'] = None
            continue
        members.sort(key=lambda r: (date(r), r['id']))
        first = members[0]
        gid = f"SC-{first['id']}"
        name = first['name']['ja']
        curated = reprint_text.get(name) or (reprint_text.get(f"{name}/{first['pokemon']['hp']}") if first['pokemon'] else None)
        rows = []
        for m in members:
            m['same_card_group'] = gid
            row = {'id': m['id'], 'product': m['jp_set'], 'date': date(m)}
            if m is not first:
                na, nb = numbers(first), numbers(m)
                row['numbers_differ'] = sorted(k for k in (na or {}) if na[k] != nb[k]) if na else []
                row['text'] = text_relation(first, m)
                row['equivalent_to_first'] = not row['numbers_differ'] and row['text'] in ('same', 'same_ignoring_punctuation')
                note = reprint_checks.get(name) if row['numbers_differ'] else None
                if note:
                    row['numbers_note'] = note
            rows.append(row)
        group = {'id': gid, 'kind': sig[0], 'name_ja': name,
                 'basis_fields': (['name.ja', 'pokemon.hp', 'pokemon.powers[].name.ja', 'pokemon.attacks[].name.ja'] if sig[0] == 'pokemon'
                                  else ['name.ja', 'energy.kind'] if sig[0] == 'energy' else ['name.ja', 'trainer.kinds']),
                 'members': rows}
        if curated:
            group['text_difference'] = {'kind': curated['kind'], 'summary': curated['summary'], 'source': 'other_products.reprint_text'}
        groups.append(group)

        packs = [m for m in members if m['product_group'] == 'expansion_pack']
        for m in members:
            if m['product_group'] == 'expansion_pack':
                continue
            src = m['field_sources']
            # 進化元: 組の拡張パックの記録（同じカード）
            if m['pokemon'] and m['pokemon']['stage'] in STAGE_BEFORE and packs:
                evo = {json.dumps(p['pokemon']['evolves_from'], ensure_ascii=False) for p in packs if p['pokemon']['evolves_from']}
                if len(evo) == 1:
                    m['pokemon']['evolves_from'] = json.loads(evo.pop())
                    src['pokemon.evolves_from'] = f"same_card:{packs[0]['id']}"
                elif len(evo) > 1:
                    checks.append(('evolves_from_conflict_in_pack', m['id'], sorted(evo)))
            # 英語の欄・図鑑番号: 英語版の対応がないとき、数値の同じ拡張パックの記録から
            ref = next((p for p in packs if numbers(p) == numbers(m) and text_relation(p, m) != 'different'), None)
            if ref and not m['en_print'] and ref['en_print']:
                m['en_print'] = dict(ref['en_print'], differs_from_primary=None)
                m['name']['en'] = ref['name']['en']
                m['source_ids']['pokemontcg'] = list(ref['source_ids']['pokemontcg'])
                src['en_print'] = f"same_card:{ref['id']}"
                copy_english(m, ref, f"same_card:{ref['id']}")
            if ref and m['pokemon'] and not m['pokemon']['dex']:
                m['pokemon']['dex'] = list(ref['pokemon']['dex'])
                src['pokemon.dex'] = f"same_card:{ref['id']}"

    # 進化元: カードページの「進化ライン検索」（同じカードの拡張パックの記録がないとき）・照らし合わせ
    for r in records:
        if r['product_group'] == 'expansion_pack' or not r['pokemon'] or r['pokemon']['stage'] not in STAGE_BEFORE:
            continue
        line, mismatches = np.evolution_line_name(r)
        for kind, found in (('evolution_line_name_differs', [m for _, m in mismatches if m.startswith('name:')]),
                            ('stage_differs_from_line', [m for _, m in mismatches if not m.startswith('name:')])):
            if not found:
                continue
            checks.append((kind, r['id'], r['pokemon']['stage'], sorted(found)))
            if kind == 'stage_differs_from_line':
                # サイトの種類の欄と進化ラインの段階が違う。どちらが印刷どおりか決められないので、段階を不足にし、進化元を入れない
                r['field_sources']['pokemon.stage'] = STAGE_CONFLICT
        cur = r['pokemon']['evolves_from']
        if cur:
            if line and {norm(x) for x in line} != {norm(cur['ja'])}:
                checks.append(('evolves_from_line_differs', r['id'], cur['ja'], sorted(line)))
            elif line:
                checks.append(('evolves_from_line_agrees', r['id'], cur['ja']))
        elif len(line) == 1:
            r['pokemon']['evolves_from'] = {'ja': next(iter(line)), 'en': None}
            r['field_sources']['pokemon.evolves_from'] = 'pcg_search_evolution_line'
        elif len(line) > 1:
            checks.append(('evolves_from_line_ambiguous', r['id'], sorted(line)))
        # 英語版の対応の進化元は、照らし合わせだけに使う（値にしない）
        en_id = (r['source_ids']['pokemontcg'] or [None])[0]
        ec = np.en.get(en_id) if en_id else None
        if ec and ec.get('evolvesFrom') and namer and r['pokemon']['evolves_from']:
            ja = namer.from_en(ec['evolvesFrom'])
            same = ja and norm(ja) == norm(r['pokemon']['evolves_from']['ja'])
            checks.append(('evolves_from_english_agrees' if same else 'evolves_from_english_differs', r['id'],
                           r['pokemon']['evolves_from']['ja'], ec['evolvesFrom'], ja))
            if same and not r['pokemon']['evolves_from'].get('en'):
                r['pokemon']['evolves_from']['en'] = ec['evolvesFrom']
    return groups, checks


def copy_english(m, ref, basis):
    """同じカードの拡張パックの記録から、英語の欄（名前・文面）だけを写す（並びが合うときだけ）。"""
    p, q = m['pokemon'], ref['pokemon']
    if p and q:
        if len(p['attacks']) == len(q['attacks']) and len(p['powers']) == len(q['powers']):
            for a, b in zip(p['attacks'], q['attacks']):
                a['name']['en'], a['text']['en'] = b['name']['en'], b['text']['en']
            for a, b in zip(p['powers'], q['powers']):
                a['name']['en'], a['text']['en'] = b['name']['en'], b['text']['en']
            if p['rules_text'] and q['rules_text']:
                p['rules_text']['en'] = q['rules_text']['en']
            m['field_sources']['english_text'] = basis
    else:
        t, u = (m['trainer'] or m['energy']), (ref['trainer'] or ref['energy'])
        if t and u and t.get('text') and u.get('text'):
            t['text']['en'] = u['text']['en']
            m['field_sources']['english_text'] = basis


def data_gaps(r):
    """記録で値がない欄（調査・転記の不足）。英語版がないことは不足に数えない。"""
    g = []
    if not r['name']['ja']:
        g.append('name.ja')
    p = r['pokemon']
    jp = r['jp_print']
    if p:
        if r.get('field_sources', {}).get('pokemon.stage') == STAGE_CONFLICT:
            g.append('pokemon.stage')
        if p['stage'] in STAGE_BEFORE and not p['evolves_from']:
            g.append('pokemon.evolves_from')
        if p['hp'] is None:
            g.append('pokemon.hp')
        if not p['types']:
            g.append('pokemon.types')
        for i, x in enumerate(p['powers']):
            if not x['name']['ja'] or not x['text']['ja']:
                g.append(f'pokemon.powers[{i}].ja')
        for i, a in enumerate(p['attacks']):
            if not a['name']['ja']:
                g.append(f'pokemon.attacks[{i}].name.ja')
            if a['text']['ja'] is None and a['text']['en']:
                g.append(f'pokemon.attacks[{i}].text.ja')
        if p['rules_text'] and not p['rules_text']['ja']:
            g.append('pokemon.rules_text.ja')
        if not p['dex']:
            g.append('pokemon.dex')
        if not jp or jp.get('level') is None:
            g.append('jp_print.level')
    t = r['trainer'] or (r['energy'] if r['energy'] and r['energy']['kind'] == 'special' else None)
    if t and not (t.get('text') or {}).get('ja'):
        g.append(('trainer' if r['trainer'] else 'energy') + '.text.ja')
    if jp is None:
        g.append('jp_print')
    elif jp.get('series') is None:
        g.append('jp_print.series')
    return g
