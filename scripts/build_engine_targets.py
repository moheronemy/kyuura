#!/usr/bin/env python3
"""エンジンの実装の対象の一覧（data/engine_targets.json）と、その読み方のページ（docs/engine-targets.md）を作る。

入力（どれもリポジトリの中のファイル）:
  - data/cards.json: カードの記録（拡張パック・拡張パック以外の商品）
  - data/product_items.json: 商品と、対戦のカードでない項目（non_game_items）
  - data/curation/sets.json・data/curation/other_products.json: 発売日（ルールの基準の日付との前後を見るため）
  - data/curation/engine_registered_cards.json: kyuura-engine の固定した版の登録表の写し（scripts/snapshot_engine_registry.py）

記録ごとに 2 つのことを分けて書く。
  - category（実装の対象にできるか。データから決める）:
      candidate（対象にできる）・data_missing（エンジンが使う欄に値の欠けがある）・
      special_rule_design（通常の対戦と扱いが違う。ガルーラルール専用・公式大会で使えないと書かれたカード）・
      non_game（対戦のカードでない項目。data/product_items.json の non_game_items）
  - engine_status（エンジンの登録との対応。エンジンの版は engine_reference）:
      registered（エンジンの対戦用のカード id）・
      mechanically_equivalent（登録のないカード id で、エンジンが使う欄がすべて、登録されたカードと同じ。登録の照合した文面とも同じ）・
      reuse_candidate（同じカードの組（data/same_card_groups.json）に登録されたカードがあって欄の一部が違う（reuse_basis: same_card_group）、
        または効果の文面がどれも登録された実装の文面と同じ（reuse_basis: registered_effect_texts）。確かめてから登録する）・
      new_effect_needed（登録された実装と同じ文面のない効果がある）
  mechanically_equivalent・reuse_candidate は、エンジンで実装済みとは数えない（エンジンの登録はカード id ごと）。

エンジンが使う欄は、エンジンの scripts/extract_kyuura_cards.py の FIELDS_USED_BY_ENGINE のうち日本語の欄（名前・段階・進化元・HP・タイプ・
弱点・抵抗力・にげる・ルールの文・特殊能力・ワザの名前・コスト・ダメージ・説明・トレーナー・エネルギー）と、ベイビィの進化先（pokemon.evolves_to。
2026-10-27 に加えた欄。エンジンの写しはまだ取り出していないが、どのカードを上に重ねて進化できるかを決める欄なので、同じかの比べ・値の欠けに含める）。

使い方: python3 scripts/build_engine_targets.py [--check]
  --check: 生成結果が data/engine_targets.json・docs/engine-targets.md と同じか（ファイルは書き換えない）
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / 'data' / 'engine_targets.json'
OUT_MD = ROOT / 'docs' / 'engine-targets.md'
RULE_BASE_DATE = '2000-02-14'  # 公式ルール 2000.02.14版（NEO-2000-OFFICIAL-RULES）
GENERATED = ('<!-- このファイルは scripts/build_engine_targets.py が data/cards.json・data/curation/engine_registered_cards.json などから'
             '生成しています。直接編集せず、データを直してから再生成してください。 -->')
# data_gaps のうち、エンジンが処理に使う欄の欠け（図鑑番号・レベル・シリーズの欠けは数えない）
ENGINE_GAP = re.compile(r'^(name\.ja|pokemon\.(evolves_from|evolves_to|stage|hp|types|rules_text\.ja|powers\[\d+\]\.ja|attacks\[\d+\]\.(name|text)\.ja)|'
                        r'trainer\.text\.ja|energy\.text\.ja)$')
STATUS_ORDER = ['registered', 'mechanically_equivalent', 'reuse_candidate', 'new_effect_needed']
CATEGORY_ORDER = ['candidate', 'data_missing', 'special_rule_design', 'non_game']


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def ja(x):
    return (x or {}).get('ja')


def engine_view(r):
    """エンジンが使う欄（日本語の欄）を、欄の名前 → 値の辞書にする。"""
    v = {'category': r['category'], 'name.ja': r['name']['ja']}
    p = r['pokemon']
    if p:
        v.update({'pokemon.stage': p['stage'], 'pokemon.evolves_from.ja': ja(p['evolves_from']), 'pokemon.hp': p['hp'],
                  'pokemon.types': p['types'], 'pokemon.weaknesses': p['weaknesses'], 'pokemon.resistances': p['resistances'],
                  'pokemon.retreat_cost': p['retreat_cost'], 'pokemon.rules_text.ja': ja(p['rules_text'])})
        if 'evolves_to' in p:  # 進化先の欄のある段階（ベイビィ）だけ。欄のない段階とは別の値（欄がない）として比べる
            v['pokemon.evolves_to'] = p['evolves_to']
        for i, x in enumerate(p['powers']):
            v.update({f'pokemon.powers[{i}].kind': x['kind'], f'pokemon.powers[{i}].name.ja': x['name']['ja'],
                      f'pokemon.powers[{i}].text.ja': x['text']['ja']})
        for i, a in enumerate(p['attacks']):
            d = a['damage']
            v.update({f'pokemon.attacks[{i}].name.ja': a['name']['ja'], f'pokemon.attacks[{i}].cost': a['cost'],
                      f'pokemon.attacks[{i}].damage': None if d is None else [d['base'], d['modifier']],
                      f'pokemon.attacks[{i}].text.ja': a['text']['ja']})
        v['pokemon.powers'] = len(p['powers'])
        v['pokemon.attacks'] = len(p['attacks'])
    if r['trainer']:
        v.update({'trainer.kinds': r['trainer']['kinds'], 'trainer.text.ja': ja(r['trainer'].get('text'))})
    if r['energy']:
        v.update({'energy.kind': r['energy']['kind'], 'energy.provides': r['energy']['provides'],
                  'energy.text.ja': ja(r['energy'].get('text'))})
    return v


def registered_view(r, reg):
    """登録されたカードの、エンジンが照合した値（登録の名前・文面）で置きかえた欄。"""
    v = engine_view(r)
    for a in reg.get('attacks', []):
        if a['name_ja'] is not None:
            v[f"pokemon.attacks[{a['index']}].name.ja"] = a['name_ja']
        if a['text_ja'] is not None or v.get(f"pokemon.attacks[{a['index']}].text.ja") is not None:
            v[f"pokemon.attacks[{a['index']}].text.ja"] = a['text_ja']
    for x in reg.get('powers', []):
        v[f"pokemon.powers[{x['index']}].name.ja"] = x['name_ja']
        v[f"pokemon.powers[{x['index']}].text.ja"] = x['text_ja']
    if 'trainer' in reg:
        v['name.ja'] = reg['trainer']['name_ja']
        v['trainer.text.ja'] = reg['trainer']['text_ja']
    if 'energy' in reg:
        v['name.ja'] = reg['energy']['name_ja']
        v['energy.text.ja'] = reg['energy']['text_ja']
    return v


def diff_fields(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def release_date(r, products, pack_dates, promos):
    if r['product_group'] == 'expansion_pack':
        return pack_dates.get(r['jp_set'])
    pid = (r['source_ids'].get('pcg_search') or [None])[0]
    if r['product_group'] == 'promo':
        return (promos.get(pid) or {}).get('date')
    return products[r['jp_set']]['release_date']


def after_rule_base(date):
    """発売日が公式ルール 2000.02.14版の日付より後か（True）・前か（False）・決まらない（None。日付がない・同じ年や月までしかない）。"""
    if not date:
        return None
    base = RULE_BASE_DATE[:len(date)]
    if len(date) < 10 and date == base:
        return None
    return date > base


def effect_index(snapshot):
    """登録された実装を、照合した文面ごとに引く表（ワザ・特殊能力・トレーナー・特殊エネルギー）。"""
    idx = {'attack': defaultdict(set), 'power': defaultdict(set), 'trainer': defaultdict(set), 'energy': defaultdict(set)}
    for cid, reg in snapshot['cards'].items():
        for a in reg.get('attacks', []):
            if a['text_ja']:
                idx['attack'][a['text_ja']].add(a['implementation'])
        for x in reg.get('powers', []):
            if x['text_ja']:
                idx['power'][x['text_ja']].add(x['implementation'])
        if 'trainer' in reg and reg['trainer']['text_ja']:
            idx['trainer'][reg['trainer']['text_ja']].add(reg['trainer']['implementation'])
        if 'energy' in reg and reg['energy']['text_ja']:
            idx['energy'][reg['energy']['text_ja']].add(reg['energy']['implementation'])
    return idx


def effect_parts(r):
    """記録の効果の要素 [(要素, 位置, 名前, 文面, ダメージの記号)]。"""
    out = []
    p = r['pokemon']
    if p:
        if ja(p['rules_text']):
            out.append(('rules_text', None, None, ja(p['rules_text']), None))
        for i, x in enumerate(p['powers']):
            out.append(('power', i, x['name']['ja'], x['text']['ja'], None))
        for i, a in enumerate(p['attacks']):
            out.append(('attack', i, a['name']['ja'], a['text']['ja'], (a['damage'] or {}).get('modifier')))
    if r['trainer']:
        out.append(('trainer', None, r['name']['ja'], ja(r['trainer'].get('text')), None))
    if r['energy'] and r['energy']['kind'] == 'special':
        out.append(('energy', None, r['name']['ja'], ja(r['energy'].get('text')), None))
    return out


def match_effects(r, idx):
    matched, unmatched = [], []
    for part, i, name, text, modifier in effect_parts(r):
        ref = {'part': part, 'index': i, 'name_ja': name}
        if part == 'attack' and text is None and modifier is None:
            continue  # 説明のないダメージだけのワザ
        found = sorted(idx.get(part, {}).get(text, ())) if text else []
        if found:
            matched.append(dict(ref, implementations=found))
        else:
            unmatched.append(dict(ref, text_ja=text, reason='no_text' if text is None else
                                  'rules_text_not_registered' if part == 'rules_text' else 'no_registered_text'))
    return matched, unmatched


def build():
    cards = load('data/cards.json')['cards']
    items = load('data/product_items.json')
    snap = load('data/curation/engine_registered_cards.json')
    sets = load('data/curation/sets.json')
    promos = load('data/curation/other_products.json')['promos']
    products = {p['id']: p for p in items['products']}
    pack_dates = {}
    for set_id, s in sets.items():
        m = re.match(r'(\d+)年(\d+)月(\d+)日', s.get('release', '') if isinstance(s, dict) else '')
        if m:
            pack_dates[set_id] = f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
    by_id = {r['id']: r for r in cards}
    playable = set(snap['playable'])
    missing = sorted(playable - set(by_id))
    if missing:
        raise SystemExit(f'エンジンの対戦用のカード id が data/cards.json にない: {missing}')
    reg_views = {cid: registered_view(by_id[cid], snap['cards'].get(cid, {})) for cid in sorted(playable)}
    by_name = defaultdict(list)
    for cid in sorted(playable):
        by_name[by_id[cid]['name']['ja']].append(cid)
    idx = effect_index(snap)
    group_members = defaultdict(list)
    for r in cards:
        if r['same_card_group']:
            group_members[r['same_card_group']].append(r['id'])

    rows = []
    for r in cards:
        row = {'id': r['id'], 'name_ja': r['name']['ja'], 'product_group': r['product_group'], 'jp_set': r['jp_set'],
               'play_scope': r['play_scope'], 'same_card_group': r['same_card_group']}
        date = release_date(r, products, pack_dates, promos)
        row['release_date'] = date
        row['released_after_rule_base'] = after_rule_base(date)
        gaps = [g for g in r['data_gaps'] if ENGINE_GAP.match(g)]
        if r['play_scope'] != 'standard':
            row['category'], row['category_reasons'] = 'special_rule_design', [f"play_scope: {r['play_scope']}"]
        elif gaps:
            row['category'], row['category_reasons'] = 'data_missing', gaps
        else:
            row['category'], row['category_reasons'] = 'candidate', []
        view = engine_view(r)
        if r['id'] in playable:
            row['engine_status'] = 'registered'
            reg = reg_views[r['id']]
            changed = diff_fields(view, reg)
            if changed:
                row['changed_since_registration'] = changed  # kyuura の今の値と、エンジンが照合した値の違い
        else:
            same = [cid for cid in by_name.get(r['name']['ja'], []) if reg_views[cid] == view]
            if same:
                row['engine_status'] = 'mechanically_equivalent'
                row['equivalent_to'] = same
            else:
                # 同じカードの組（名前・HP・特殊能力名・ワザ名が同じ。data/same_card_groups.json）の登録されたカード
                near = sorted(((len(diff_fields(view, reg_views[cid])), cid) for cid in group_members.get(r['same_card_group'], [])
                               if cid in playable))
                matched, unmatched = match_effects(r, idx)
                if near:
                    row['engine_status'], row['reuse_basis'] = 'reuse_candidate', 'same_card_group'
                    row['nearest_registered'] = [{'id': cid, 'differences': diff_fields(view, reg_views[cid])} for _, cid in near[:3]]
                elif not unmatched:
                    row['engine_status'], row['reuse_basis'] = 'reuse_candidate', 'registered_effect_texts'
                else:
                    row['engine_status'] = 'new_effect_needed'
                if matched:
                    row['effects_with_registered_text'] = matched
                if unmatched:
                    row['effects_without_registered_text'] = unmatched
        rows.append(row)

    non_game = [{'item_id': x['id'], 'page': x['page'], 'product': x['product'], 'name_ja': x['name'], 'kind': x['kind'],
                 'category': 'non_game', 'reason': x['reason']} for x in items['non_game_items']]
    counts = {
        'records': len(rows),
        'by_category': dict(sorted(Counter(r['category'] for r in rows).items())),
        'non_game_items': len(non_game),
        'by_engine_status': {k: sum(1 for r in rows if r['engine_status'] == k) for k in STATUS_ORDER},
        'by_product_group': {},
    }
    groups = sorted({r['product_group'] for r in rows}, key=lambda g: (g != 'expansion_pack', g))
    for g in groups:
        sub = [r for r in rows if r['product_group'] == g]
        counts['by_product_group'][g] = {'records': len(sub),
                                         'by_engine_status': {k: sum(1 for r in sub if r['engine_status'] == k) for k in STATUS_ORDER},
                                         'by_category': dict(sorted(Counter(r['category'] for r in sub).items()))}
    doc = {
        'schema_version': 1,
        'description': 'エンジンの実装の対象の一覧（scripts/build_engine_targets.py が生成。手で編集しない）。読み方は docs/engine-targets.md。'
                       'category はデータから決めた実装の対象の分類、engine_status は engine_reference の版の登録との対応。'
                       'mechanically_equivalent・reuse_candidate は実装済みではない（エンジンの登録はカード id ごと）。',
        'engine_reference': {**snap['engine'], 'registry_id': snap['registry_id'], 'counts': snap['counts'],
                             'snapshot': 'data/curation/engine_registered_cards.json', 'extracted_on': snap['extracted_on'],
                             'previous_snapshots': snap.get('previous_snapshots', [])},
        'rule_base_date': RULE_BASE_DATE,
        'counts': counts,
        'cards': rows,
        'non_game_items': non_game,
    }
    return doc, render(doc)


def md(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


STATUS_JA = {'registered': '登録あり（エンジンの対戦用のカード id）', 'mechanically_equivalent': '登録されたカードと処理に使う欄が同じ（id は未登録）',
             'reuse_candidate': '再利用の候補（確かめてから登録）', 'new_effect_needed': '新しい効果の実装が要る'}
CATEGORY_JA = {'candidate': '対象にできる', 'data_missing': '値の欠けがある', 'special_rule_design': '特別なルールの設計が要る', 'non_game': '対戦のカードでない'}
GROUP_JA = {'expansion_pack': '拡張パック', 'expansion_sheet': '拡張シート', 'southern_islands': 'サザンアイランド', 'gym_deck': 'ポケモンジムのデッキ',
            'quick_starter_gift': 'クイックスターターギフト', 'intro_pack': 'イントロパック', 'premium_file': 'プレミアムファイル', 'promo': 'プロモ'}


def render(doc):
    c = doc['counts']
    e = doc['engine_reference']
    L = ['# エンジンの実装の対象', '', GENERATED, '',
         f"kyuura の記録（`data/cards.json`）ごとに、エンジンの実装の対象にできるか（category）と、kyuura-engine {e['version']}"
         f"（ブランチ `{e['branch']}`、コミット `{e['commit'][:7]}`）の登録との対応（engine_status）を、機械で読める一覧 "
         '[`data/engine_targets.json`](../data/engine_targets.json) にまとめています。この一覧は kyuura のデータとエンジンの登録表の写し'
         '（[`data/curation/engine_registered_cards.json`](../data/curation/engine_registered_cards.json)。'
         f"{e['extracted_on']} に scripts/snapshot_engine_registry.py で作成）から作ったもので、エンジンの実装の状況の正本はエンジンのリポジトリです。"
         f"写しの `registry_id`（`{e['registry_id']}`）は登録表の名前で、版の番号ではありません（版は上の {e['version']}）。", '']
    if e['previous_snapshots']:
        L += ['前の写しの参照（その時点の取得日・件数のまま。中身は git の履歴にあります。研究の取り込みの範囲は別で、'
              '[研究の状況](research-status.md) と data/sidecar/rulings.json の engine_imports に書きます）:', '']
        for p in e['previous_snapshots']:
            n = p['counts']
            L.append(f"- {p['engine']['version']}（コミット `{p['engine']['commit'][:7]}`、{p['extracted_on']} に作成、{p['replaced_on']} に置きかえ）: "
                     f"対戦用のカード {n['playable_cards']}、登録のあるカード {n['cards_with_registrations']}"
                     f"（ワザ {n['attacks']}・トレーナー {n['trainers']}・特殊能力 {n['powers']}・特殊エネルギー {n['energies']}）")
        L.append('')
    L += [
         '- エンジンの登録はカード id ごとです。登録のない id を、同じ処理のカードがあっても実装済みとは数えません。',
         '- 強さ・勝率・デッキの釣り合いは評価していません。新しいカードの効果は実装していません。',
         '- 印刷の文面・公式の最新の説明・公式エラッタ・研究上の解釈・エンジンの採用した仕様は別のものです。この一覧の「同じ」は kyuura の転記の欄が同じことで、'
         '最新の説明やエラッタが同じように当てはまるかは、登録するときにエンジンが確かめます。', '',
         '## 分け方', '',
         '| 欄 | 値 | 意味 |', '|---|---|---|']
    for k in CATEGORY_ORDER:
        L.append(f'| category | `{k}` | {CATEGORY_JA[k]} |')
    for k in STATUS_ORDER:
        L.append(f'| engine_status | `{k}` | {STATUS_JA[k]} |')
    L += ['',
          '- `data_missing` の理由（category_reasons）は、記録の `data_gaps` のうちエンジンが使う欄（名前・段階・進化元・ベイビィの進化先・HP・タイプ・ルールの文・特殊能力・ワザの名前と説明・'
          'トレーナーと特殊エネルギーの説明）の欠けです。ベイビィの進化先（`pokemon.evolves_to`）はエンジンの写しがまだ取り出さない欄ですが、'
          '進化できるカードを決めるので、欠け（未確認）と、登録されたカードと同じかの比べに含めます。図鑑番号・レベル・シリーズの欠けは数えません。',
          '- `special_rule_design` は `play_scope` が `standard` でない記録（ガルーラルール専用・公式大会で使えないと書かれたカード）。',
          '- `mechanically_equivalent` は、エンジンが使う欄がすべて登録されたカードと同じで、ワザ・特殊能力・トレーナー・特殊エネルギーの名前と説明が、'
          'エンジンが登録のときに照合した文面（`text_ja`）とも同じもの（`equivalent_to` に登録されたカード）。',
          '- `reuse_candidate` は、同じカードの組（`same_card_group`。名前・HP・特殊能力名・ワザ名が同じ）に登録されたカードがあって欄の一部が違うもの'
          '（`reuse_basis: same_card_group`。`nearest_registered` の `differences`）か、効果の文面がどれも登録された実装の文面と同じもの'
          '（`reuse_basis: registered_effect_texts`。`effects_with_registered_text`）。名前が同じでも別のカード（HP・ワザが違う）は組にならない。',
          '- `new_effect_needed` は、登録された実装と同じ文面のない効果（`effects_without_registered_text`）があるもの。文面が違っても既存の実装で処理できる場合はある'
          '（エンジンが文面の形を確かめて決める）。',
          f"- `released_after_rule_base` は、発売日が公式ルール 2000.02.14版の日付（{doc['rule_base_date']}）より後か。後に出たカードは、"
          'その時点の公式ルールで処理が決まっているとは限りません（実装の対象から外すものではない。ルールの版の判断に使う）。日付が分からなければ null。', '',
          '## 数', '',
          f"記録 {c['records']} 件（このほか、対戦のカードでない項目 {c['non_game_items']} 件。`non_game_items`）。", '',
          '| 商品の種類 | 記録 | ' + ' | '.join(f'`{k}`' for k in STATUS_ORDER) + ' | ' + ' | '.join(f'`{k}`' for k in CATEGORY_ORDER[:3]) + ' |',
          '|---|---|' + '---|' * (len(STATUS_ORDER) + 3)]
    for g, x in c['by_product_group'].items():
        L.append(f"| {GROUP_JA.get(g, g)} | {x['records']} | " + ' | '.join(str(x['by_engine_status'][k]) for k in STATUS_ORDER) + ' | '
                 + ' | '.join(str(x['by_category'].get(k, 0)) for k in CATEGORY_ORDER[:3]) + ' |')
    L.append(f"| 計 | {c['records']} | " + ' | '.join(str(c['by_engine_status'][k]) for k in STATUS_ORDER) + ' | '
             + ' | '.join(str(c['by_category'].get(k, 0)) for k in CATEGORY_ORDER[:3]) + ' |')
    rows = doc['cards']
    eq = [r for r in rows if r['engine_status'] == 'mechanically_equivalent']
    L += ['', '## 登録されたカードと処理に使う欄が同じ記録（mechanically_equivalent）', '',
          f'{len(eq)} 件。エンジンが登録するときは、同じ登録をこの id にも加え、最新の説明・エラッタが同じように当てはまるかを確かめます。', '',
          '| id | 名前 | 同じ欄の登録 | category |', '|---|---|---|---|']
    for r in eq:
        L.append(f"| `{r['id']}` | {md(r['name_ja'])} | {', '.join(f'`{x}`' for x in r['equivalent_to'])} | `{r['category']}` |")
    reuse = [r for r in rows if r['engine_status'] == 'reuse_candidate' and r['product_group'] != 'expansion_pack']
    L += ['', '## 再利用の候補（reuse_candidate。拡張パック以外の商品）', '',
          f'{len(reuse)} 件。違う欄（differences）を確かめてから登録します。拡張パック（neo）の候補は `data/engine_targets.json` にあります。', '',
          '| id | 名前 | いちばん近い登録 | 違う欄 |', '|---|---|---|---|']
    for r in reuse:
        near = (r.get('nearest_registered') or [None])[0]
        if near:
            L.append(f"| `{r['id']}` | {md(r['name_ja'])} | `{near['id']}` | {md(', '.join(near['differences']))} |")
        else:
            L.append(f"| `{r['id']}` | {md(r['name_ja'])} | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |")
    new = [r for r in rows if r['engine_status'] == 'new_effect_needed' and r['product_group'] != 'expansion_pack']
    L += ['', '## 新しい効果の実装が要る記録（new_effect_needed。拡張パック以外の商品）', '',
          f'{len(new)} 件。拡張パック（neo）の記録は `data/engine_targets.json` にあります。', '',
          '| id | 名前 | 登録された文面のない効果 | category |', '|---|---|---|---|']
    for r in new:
        parts = [f"{x['part']}{'' if x['index'] is None else x['index']}「{x['name_ja'] or ''}」" for x in r['effects_without_registered_text']]
        L.append(f"| `{r['id']}` | {md(r['name_ja'])} | {md('、'.join(parts))} | `{r['category']}` |")
    other = [r for r in rows if r['category'] != 'candidate' and r['product_group'] != 'expansion_pack']
    L += ['', '## 値の欠け・特別なルールの記録（拡張パック以外の商品）', '',
          '| id | 名前 | category | 理由 |', '|---|---|---|---|']
    for r in other:
        L.append(f"| `{r['id']}` | {md(r['name_ja'])} | `{r['category']}` | {md(', '.join(r['category_reasons']))} |")
    changed = [r for r in rows if r.get('changed_since_registration')]
    L += ['', '## 登録のあとで kyuura の値が変わったカード', '',
          'エンジンが登録のときに照合した値（写しの元のコミットの値にエンジンの補正を当てはめたもの）と、今の kyuura の値が違う欄です。'
          'エンジンが写しのコミットを上げるときに確かめます。', '']
    if changed:
        L += ['| id | 名前 | 違う欄 |', '|---|---|---|']
        for r in changed:
            L.append(f"| `{r['id']}` | {md(r['name_ja'])} | {md(', '.join(r['changed_since_registration']))} |")
    else:
        L.append('ありません。')
    L += ['', '## 対戦のカードでない項目（non_game）', '',
          '`data/cards.json` に入れず、`data/product_items.json` の `non_game_items` に元の項目から追えるように残しています。', '',
          '| 項目の id | 元のページ | 名前 | 種類 |', '|---|---|---|---|']
    for x in doc['non_game_items']:
        L.append(f"| `{x['item_id']}` | `{x['page']}` | {md(x['name_ja'] or '')} | `{x['kind']}` |")
    L.append('')
    return '\n'.join(L)


def main():
    check = '--check' in sys.argv[1:]
    doc, text = build()
    data = json.dumps(doc, ensure_ascii=False, indent=1) + '\n'
    if check:
        bad = [p for p, s in ((OUT_JSON, data), (OUT_MD, text)) if not p.exists() or p.read_text(encoding='utf-8') != s]
        if bad:
            raise SystemExit('生成結果が違う: ' + ', '.join(str(p.relative_to(ROOT)) for p in bad))
        print('ok', file=sys.stderr)
        return
    OUT_JSON.write_text(data, encoding='utf-8')
    OUT_MD.write_text(text, encoding='utf-8')
    print(json.dumps(doc['counts'], ensure_ascii=False), file=sys.stderr)


if __name__ == '__main__':
    main()
