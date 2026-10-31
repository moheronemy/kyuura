#!/usr/bin/env python3
"""調査の状況（docs/research-status.md）の数を、データと docs/sources.md から数える（読むだけで、ファイルは書き換えない）。

  - 出典の記号（docs/sources.md）: 原文・スキャン・保存された写しで読んだもの、検索結果の要約だけのもの、
    原本を確認していない当時の公式資料、開けなかったもの。区分は docs/sources.md の「調べ方について」の節と表による
  - ルール（data/rule_history.json・data/rule_differences.json）: 確度、根拠の種類、エラッタの段階、版の比較表のマス
  - カード（data/cards.json・data/ja_text_pcgsearch.json・data/curation/*）: 日本語テキストの有無と出典、
    数値の出典と転記との照合、日英の違いの記録、再録の組

docs/research-status.md の数は、このスクリプトの出力を写したものです。
数えられるのは、データに項目として記録されていることだけです。カードの画像や現物と照合したかどうかは、
カードごとの項目がないので数えていません（個別の記録にある言及の件数だけを示します）。

使い方: python3 scripts/research_stats.py
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def ja_fields(r):
    """日本語の欄（英語版に対応する欄があるもの）を (欄の種類, 値) で返す。"""
    p = r['pokemon']
    out = []
    if p:
        for x in p['powers']:
            out += [('特殊能力名', x['name']['ja']), ('特殊能力の効果文', x['text']['ja'])]
        for a in p['attacks']:
            out.append(('ワザ名', a['name']['ja']))
            if a['text']['en'] is not None:
                out.append(('ワザの効果文', a['text']['ja']))
        if p.get('rules_text') and p['rules_text'].get('en'):
            out.append(('ルール文', p['rules_text'].get('ja')))
    else:
        t = r['trainer'] or r['energy']
        if t and t.get('text') is not None:
            label = 'トレーナーの効果文' if r['trainer'] else '特殊エネルギーの効果文'
            out.append((label, t['text']['ja']))
    return out


def transcriptions():
    """日本語の転記（なぞのばしょ・ポケモンWiki）を、ページの URL から引けるようにする。"""
    out = {}
    for rel in ('data/ja_text_nazonobasho.json', 'data/ja_text_pokemonwiki.json'):
        for s in load(rel)['sets'].values():
            for c in s['cards']:
                out[c['url']] = c
    return out


def section(text, start, stop_prefix):
    """start の見出しから、次の stop_prefix で始まる行までの本文。"""
    a = text.index(start) + len(start)
    m = re.search(rf'^{re.escape(stop_prefix)}', text[a:], re.M)
    return text[a:a + m.start()] if m else text[a:]


def codes_in(text):
    """本文中の出典の記号（「P15〜P23」のような範囲も展開する）。"""
    out = set(re.findall(r'\b([A-Z]\d+)\b', text))
    for p, a, b in re.findall(r'\b([A-Z])(\d+)〜[A-Z]?(\d+)\b', text):
        out |= {f'{p}{n}' for n in range(int(a), int(b) + 1)}
    return out


def source_stats():
    text = (ROOT / 'docs' / 'sources.md').read_text(encoding='utf-8')
    codes = re.findall(r'^\| ([A-Z]\d+) \|', text, re.M)
    known = set(codes)
    read = codes_in(section(text, '### 原文・スキャン・保存された写しで読んだもの', '### ')) & known
    read |= set(re.findall(r'^\| ([A-Z]\d+) \|', section(text, '## 当時の印刷物', '## '), re.M))
    cited = set(re.findall(r'^\| ([A-Z]\d+) \|', section(text, '## 当時の公式資料（原本は未確認）', '## '), re.M))
    summary_sec = section(text, '### 検索結果の要約だけで確かめたもの', '### ')
    closed = {c for line in summary_sec.splitlines() if '開けず' in line for c in codes_in(line)} & known
    rows = []
    for prefix in sorted({c[0] for c in codes}):
        cs = [c for c in codes if c[0] == prefix]
        r = [c for c in cs if c in read]
        ci = [c for c in cs if c in cited and c not in read]
        cl = [c for c in cs if c in closed and c not in read]
        rest = len(cs) - len(r) - len(ci) - len(cl)
        rows.append((prefix, len(cs), len(r), rest, len(ci), len(cl)))
    print(f'## 出典の記号（docs/sources.md、{len(codes)} 件）\n')
    print('| 記号 | 件数 | 原文・スキャン・保存された写し・データで読んだ | 検索結果の要約だけ | 原本未確認（他の資料の引用だけ） | 開けなかった |')
    print('|---|---|---|---|---|---|')
    for row in rows:
        print('| ' + ' | '.join(str(x) for x in row) + ' |')
    print('\n「読んだ」は、その資料の本文を読めたという意味です。その資料が本文の個々の記述を裏付けるかは、記述ごとの出典の記号と確度で示しています。')


def rule_stats():
    h = load('data/rule_history.json')
    rd = load('data/rule_differences.json')
    print('\n## ルール\n')
    rows = Counter()
    for it in rd['items']:
        for side in ('jp', 'en'):
            for r in it.get(side) or []:
                rows[(side, r['confidence'])] += 1
    print(f"- 日米の違い（data/rule_differences.json）: {len(rd['items'])} 項目。行の確度 日本版 " +
          '・'.join(f"{c} {rows[('jp', c)]}" for c in ('確実', '有力', '未確認')) + '、英語版 ' +
          '・'.join(f"{c} {rows[('en', c)]}" for c in ('確実', '有力', '未確認')))
    recs = h['entries'] + h['errata']
    groups = Counter()
    for x in recs:
        groups[(x['id'].split('-')[0], x['confidence'])] += 1
    print(f'- 記録（data/rule_history.json の entries・errata）: {len(recs)} 件。id の種類ごとの確度: ' + '、'.join(
        f"{p}（" + '・'.join(f'{c} {groups[(p, c)]}' for c in ('確実', '有力', '未確認') if groups[(p, c)]) + '）'
        for p in sorted({k[0] for k in groups})))
    kinds = Counter()
    for x in recs:
        kinds.update({e['kind'] for e in x.get('evidence', [])})
    print('- 根拠の種類ごとの記録の数（1 件の記録に複数の種類があれば、それぞれに数える）: ' +
          '、'.join(f'{k} {kinds[k]}' for k in h['evidence_kinds']))
    stages = Counter((st['kind'], st['confidence']) for x in recs for st in x.get('stages', []))
    print('- エラッタの段階（stages）: ' + '、'.join(
        f"{k}（" + '・'.join(f'{c} {stages[(k, c)]}' for c in ('確実', '有力', '未確認') if stages[(k, c)]) + '）'
        for k in h['stage_kinds'] if any(stages[(k, c)] for c in ('確実', '有力', '未確認'))))
    eds = [e for e in h['jp_editions'] if e.get('in_matrix')]
    print('- 日本版のルールの版（jp_editions）: ' + '、'.join(f"{e['label']} {e['confidence']}" for e in eds))
    cells = [(row['id'], ed, c) for row in h['jp_edition_matrix'] for ed, c in row['cells'].items()]
    total = len(h['jp_edition_matrix']) * len(eds)
    print(f"- 版の比較表（jp_edition_matrix）: {len(h['jp_edition_matrix'])} 項目 × {len(eds)} 版 = {total} マス。"
          f"記録のあるマス {len(cells)}（残りの {total - len(cells)} マスは未確認）")
    print('  - 記録のあるマスの確度: ' + '、'.join(f'{k} {v}' for k, v in Counter(c['confidence'] for _, _, c in cells).most_common()))
    print('  - 根拠の性質: ' + '、'.join(f'{k} {v}' for k, v in Counter(c['evidence_type'] for _, _, c in cells).most_common()) +
          '（edition_document は版のルール文書そのもの）')
    print('  - 版ごとの記録のあるマス: ' + '、'.join(f"{e['label']} {sum(1 for _, ed, _ in cells if ed == e['id'])}" for e in eds))
    docs = h['documents']
    print(f"- スキャンで読んだ印刷物（documents）: {len(docs)} 冊、ページの記録 {sum(len(d.get('pages', [])) for d in docs)} 件")


def reprint_stats():
    import build_other_products as bop
    cat = bop.Catalog()
    groups = bop.reprint_groups(cat)
    rt = cat.cur.get('reprint_text', {})
    kinds = Counter()
    for sig, members in groups:
        base = next((g for g in members if any(bop.texts_of(g))), None)
        if base and any(g is not base and bop.text_differs(base, g) for g in members):
            note = rt.get(f'{sig[0]}/{sig[1]}' if len(sig) == 4 else sig[0]) or rt.get(sig[0]) or {}
            kinds[note.get('kind', '未分類')] += 1
    print(f"\n## 再録\n\n- 2 つ以上の商品に入っている同じカードの組: {len(groups)} 組（{sum(len(m) for _, m in groups)} 枚）")
    print(f"- そのうち、最初の収録と文面が違う収録がある組: {sum(kinds.values())} 組（" +
          '、'.join(f"{bop.REPRINT_KIND_JA.get(k, k)} {v}" for k, v in kinds.most_common()) + '）')


def non_pack_stats():
    """拡張パック以外の商品の記録（data/cards.json の product_group が expansion_pack 以外）と、元の項目の行き先。"""
    allc = load('data/cards.json')['cards']
    np_ = [r for r in allc if r.get('product_group', 'expansion_pack') != 'expansion_pack']
    items = load('data/product_items.json')
    groups = load('data/same_card_groups.json')
    ledger = load('data/curation/card_corrections.json')
    print(f'\n## data/cards.json（拡張パック以外の商品、{len(np_)} 件）\n')
    print('- 元の項目（data/ja_text_pcgsearch.json のカードページ）: ' + f"{len(items['items'])} 件（" +
          '、'.join(f'{k} {v}' for k, v in Counter(it['disposition'] for it in items['items']).most_common()) + '）')
    print('- 商品ごとの記録: ' + '、'.join(f"{p['id']} {p['counts']['card_records']}" for p in items['products']))
    print('- 種類: ' + '、'.join(f'{k} {v}' for k, v in Counter(r['category'] for r in np_).most_common()) +
          '。使える範囲（play_scope）: ' + '、'.join(f'{k} {v}' for k, v in Counter(r['play_scope'] for r in np_).most_common()))
    print('- 対戦のカードでない項目（non_game_items）: ' + '、'.join(f'{k} {v}' for k, v in Counter(x['kind'] for x in items['non_game_items']).most_common()))
    print('- 値の欠け（data_gaps）: ' + '、'.join(f'{k} {v}' for k, v in Counter(g for r in np_ for g in r['data_gaps']).most_common()))
    src = Counter(r['field_sources'].get('pokemon.evolves_from', 'なし') .split(':')[0] for r in np_
                  if r['pokemon'] and r['pokemon']['stage'] in ('stage1', 'stage2'))
    print('- 進化元の出どころ（1 進化・2 進化）: ' + '、'.join(f'{k} {v}' for k, v in src.most_common()))
    rt = Counter(r['field_sources'].get('pokemon.retreat_cost') for r in np_ if r['pokemon'])
    print('- にげるの出どころ: ' + '、'.join(f'{k} {v}' for k, v in rt.most_common()))
    print(f"- 同じカードの組（data/same_card_groups.json）: {len(groups['groups'])} 組（拡張パックとの組 "
          f"{sum(1 for g in groups['groups'] if any(m['product'] in ('PMCG1','PMCG2','PMCG3','PMCG4','PMCG5','PMCG6','neo1','neo2','neo3','neo4') for m in g['members']))}）")
    print(f"- 訂正の記録（data/curation/card_corrections.json）: 訂正 {len(ledger['corrections'])} 件（" +
          '、'.join(f'{k} {v}' for k, v in Counter(c['applied_by'] for c in ledger['corrections']).most_common()) + '）、候補 ' +
          f"{len(ledger['candidates'])} 件（" + '、'.join(f'{k} {v}' for k, v in Counter(c['status'] for c in ledger['candidates']).most_common()) + '）')


def main():
    cards = [r for r in load('data/cards.json')['cards'] if r.get('product_group', 'expansion_pack') == 'expansion_pack']
    tr = transcriptions()
    print(f'\n## data/cards.json（拡張パック 10 弾、{len(cards)} 件）\n')

    # 日本語テキスト
    full, partial, none_needed = 0, Counter(), 0
    missing_by_kind = Counter()
    for r in cards:
        f = ja_fields(r)
        if not f:
            none_needed += 1
            continue
        miss = [k for k, v in f if v is None]
        if miss:
            partial[r['id']] = len(miss)
            missing_by_kind.update(miss)
        else:
            full += 1
    print('### 日本語テキスト\n')
    print(f'- 日本語の欄（ワザ名・特殊能力名・効果文・ルール文）がすべてあるカード: {full}')
    print(f'- 一部が欠けているカード: {len(partial)}（欠けている欄: ' + '、'.join(f'{k} {v}' for k, v in missing_by_kind.items()) + '）')
    print(f'  - {", ".join(sorted(partial))}')
    print(f'- 日本語の欄がないカード（効果文のない基本エネルギー）: {none_needed}')
    src = Counter()
    for r in cards:
        u = r.get('ja_text_source') or ''
        src['なぞのばしょ [N1]' if 'nazonobasho' in u else 'ポケモンWiki [N2]' if 'pokemonwiki' in u
            else 'pcg-search の画像つきページ [N3]（data/curation/ja_text.json）' if 'pcg-search' in u else 'なし'] += 1
    print('- 日本語テキストの出典（ja_text_source）: ' + '、'.join(f'{k} {v}' for k, v in src.most_common()))
    curated = [k for k in load('data/curation/ja_text.json') if not k.startswith('_')]
    print(f'- 転記を手で直したカード（data/curation/ja_text.json）: {len(curated)}（{", ".join(curated)}）')

    # 数値（英語版から）と転記との照合
    pk = [r for r in cards if r['pokemon']]
    en_based = [r for r in pk if r['en_print']]
    print('\n### 数値（HP・タイプ・弱点・抵抗力・にげる・ワザのエネルギーとダメージ）\n')
    print(f'- ポケモン {len(pk)} 枚のうち、数値を英語版データから入れたもの: {len(en_based)}、日本語の転記から入れたもの（英語版のないカード）: {len(pk) - len(en_based)}')
    cmp = Counter()
    for r in en_based:
        t = tr.get(r.get('ja_text_source'))
        if not t:
            continue
        f = t['fields']
        cmp['HP'] += bool(f.get('HP'))
        cmp['にげる'] += bool(f.get('にげる') and f['にげる'] != 'n/a')
        cmp['タイプ'] += bool(f.get('タイプ'))
        cmp['弱点・抵抗力'] += any(k in f for k in ('弱点（×2）', '弱点'))
        cmp['ワザのエネルギーとダメージ'] += len(t['attacks']) == len(r['pokemon']['attacks'])
    print('- 日本語の転記と照合した欄（build_cardlist.py が取り込みのときに比べる）: ' + '、'.join(f'{k} {v} 枚' for k, v in cmp.items()))
    print('  - 照合したのは転記（なぞのばしょ・ポケモンWiki）と英語版データです。一致したものは、日本版の現物や画像と照合したことにはなりません')
    verdicts = Counter()
    for name in ('nazonobasho', 'pokemonwiki'):
        for k, x in load(f'data/curation/{name}_review.json').items():
            if not k.startswith('_'):
                verdicts[(name, x['verdict'], k.split('|')[1])] += 1
    label = {'site_error': 'サイトの誤記', 'en_data_error': '英語版データの誤り', 'possible_difference': '日英で違う可能性'}
    for name in ('nazonobasho', 'pokemonwiki'):
        rows = {k: v for k, v in verdicts.items() if k[0] == name}
        print(f'  - 食い違いの判定（data/curation/{name}_review.json）: {sum(rows.values())} 件。' +
              '、'.join(f'{label[k[1]]}（{k[2]}） {v}' for k, v in sorted(rows.items())))
    pcg_img = sum('pcg-search のカードの画像' in x.get('note', '') for name in ('nazonobasho', 'pokemonwiki')
                  for k, x in load(f'data/curation/{name}_review.json').items() if not k.startswith('_'))
    print(f'  - うち、pcg-search のカードの画像で確かめたと note に書いたもの: {pcg_img}')

    # 日英の対応と違い
    print('\n### 日英の対応と違い\n')
    no_en = [r['id'] for r in cards if not r['en_print']]
    print(f'- 英語版のないカード（日本のみ）: {len(no_en)}（{", ".join(no_en)}）')
    print('- カード名の確度（name_ja_confidence）: ' + '、'.join(f'{k} {v}' for k, v in Counter(r['name_ja_confidence'] for r in cards).most_common()))
    diff = [r for r in cards if r['jp_en_differences']]
    kinds = Counter(d['kind'] for r in cards for d in r['jp_en_differences'])
    conf = Counter(d['confidence'] for r in cards for d in r['jp_en_differences'])
    print(f'- 日英の違いを記録したカード: {len(diff)}（種類: ' + '、'.join(f'{k} {v}' for k, v in kinds.most_common()) +
          '。確度: ' + '、'.join(f'{k} {v}' for k, v in conf.most_common()) + '）')
    img = [r['id'] for r in cards for d in r['jp_en_differences'] if '画像' in (d.get('ja') or '')]
    print(f'- 日英の違いの記録のうち、本文に「画像」で確かめたと書いてあるもの: {len(img)}（カードごとの画像照合の項目はデータにないので、これ以外は数えられない）')

    # 拡張パック以外
    pcg = load('data/ja_text_pcgsearch.json')['products']
    cur = load('data/curation/other_products.json')
    allc = [c for cs in pcg.values() for c in cs]
    print(f'\n## data/ja_text_pcgsearch.json（拡張パック以外の商品、{len(allc)} 件）\n')
    print(f'- 商品（ページ）の数: {len(pcg)}')
    print('- 日本語の名前・数値・効果文は、すべて pcg-search の転記 [N3]（ページにカードの画像がある）。転記を画像と照合したかのカードごとの記録はない')
    en = cur.get('en_prints', {})
    print(f'- 英語版の対応を手で記録したカード（en_prints）: {len(en)}')
    diffs = cur.get('differences', {})
    print(f'- 日英の違いを記録したカード（differences）: {len([k for k, v in diffs.items() if isinstance(v, list)])}')
    named = cur.get('identified_cards', {})
    print(f'- pcg-search で名前が「-」のカードを特定したもの（identified_cards）: {len([k for k in named if not k.startswith("_")])}')


def sidecar_stats():
    lat = load('data/sidecar/latest_descriptions.json')['records']
    chk = load('data/sidecar/card_checks.json')['records']
    r = load('data/sidecar/rulings.json')
    print('\n## サイドカー（data/sidecar/）\n')
    print(f"- 公式の最新の説明: {len(lat)} 件（カード {len({x['card_id'] for x in lat})} 枚）。意味の違い: " +
          '、'.join(f'{k} {v}' for k, v in Counter(x['meaning_change'] for x in lat).most_common()) +
          '。図版との照合: ' + '、'.join(f'{k} {v}' for k, v in Counter(x['printed_text']['image_check'] for x in lat).most_common()))
    print(f"- カードの照合: {len(chk)} 件（" + '、'.join(f'{k} {v}' for k, v in Counter(x['result'] for x in chk).most_common()) +
          f"。データの誤り {sum(1 for x in chk if x['data_error'])}、照合のあとで直したもの {sum(1 for x in chk if x.get('corrections'))}、"
          f"値の欠け（調査課題） {sum(len(x.get('data_gaps', [])) for x in chk)}）")
    imp_lat = [x for x in lat if x.get('import_provenance')]
    imp_chk = [x for x in chk if x.get('import_provenance')]
    print(f"  - 原典を確かめた人: kyuura が画像を読んだもの 最新の説明 {len(lat) - len(imp_lat)}・カードの照合 {len(chk) - len(imp_chk)}、"
          f"kyuura-engine の照合の記録の取り込み（import_provenance。kyuura は読み直していない） 最新の説明 {len(imp_lat)}・カードの照合 {len(imp_chk)}")
    print(f"- 公式ルールの条項: {len(r['rule_clauses'])} 件")
    print(f"- 裁定: {len(r['rulings'])} 件（" + '、'.join(f'{k} {v}' for k, v in Counter(x['status'] for x in r['rulings']).most_common()) + '）')
    print('  - 根拠の種類ごとの記録の数（1 件に複数の種類があれば、それぞれに数える）: ' + '、'.join(
        f'{k} {v}' for k, v in Counter(k for x in r['rulings'] for k in {b['kind'] for b in x['basis']}).most_common()))
    print(f"- 未解決の論点: {len(r['issues'])} 件")
    print(f"- kyuura-engine の取り込み: {len(r['engine_imports'])} 件（版ごと）")
    total = 0
    for imp in r['engine_imports']:
        n = sum(rs['last'] - rs['first'] + 1 + len(rs.get('extra_ids', [])) for rs in imp.get('ruling_sets', []))
        total += n
        print(f"  - {imp['id']}（{imp['engine_version']}、{imp['commit'][:7]}）: エンジンの裁定 {n} 件、取り込んでいない {len(imp.get('not_imported', []))} 件、"
              f"対応する kyuura の記録 {len(imp.get('imported_rulings', []))} 件・未解決の論点 {len(imp.get('unresolved_rulings', []))} 件")
    idx = r['engine_unresolved_index']
    print(f"  - 合計: エンジンの裁定 {total} 件")
    print(f"- エンジンの未解決の裁定の一覧: {len(idx)} 件（" + '、'.join(f'{k} {v}' for k, v in Counter(u.get('disposition') for u in idx).most_common()) +
          f"。論点に結んだ項目 {sum(1 for u in idx if u['kyuura_issue'])}）")
    import build_card_rulings as bcr  # 未解決の数の区別（kyuura の論点の数とエンジンの数を分ける）
    ctx = bcr.load()
    uc = bcr.unresolved_counts(ctx)
    total = Counter()
    print('- エンジンの裁定 id ごとの kyuura の分類（対応する記録の分類。部分ごとに違えば CONFIRMED+SUPPORTED）:')
    for v, tally in bcr.kyuura_status_by_engine_id(ctx).items():
        total.update(tally)
        if tally:
            print(f'  - {v}: ' + '、'.join(f'{k} {n}' for k, n in sorted(tally.items())))
    print('  - 合計: ' + '、'.join(f'{k} {n}' for k, n in sorted(total.items())) + f'（{sum(total.values())} 件）')
    print(f"- 未解決の数の区別: kyuura の論点 {uc['research_issues']} 件（結果への影響: " +
          '、'.join(f'{k} {v}' for k, v in uc['game_effect'].most_common()) + '）。'
          f"エンジンが数える未解決の裁定（{uc['latest_version']} まで）{uc['engine_total']} 件・そのうち停止コード {uc['engine_stop_codes']} 件"
          f"（v0.13 まで {len(uc['v013_items'])}・v0.17 で加わった {len(uc['v017_additions'])}）。エンジンが数えていない項目 {len(uc['not_in_engine_count'])} 件、"
          f"あとの版の事例 {len(uc['instances'])} 件、取り込みの範囲の外 {len(uc['out_of_scope'])} 件。停止コードのない論点 {len(uc['issues_without_stop_code'])} 件、"
          f"エンジンの一覧と結んでいない論点 {len(uc['issues_not_in_index'])} 件" +
          ''.join(f"。エンジンが報告した数（{v}。kyuura の一覧と照らしていない）停止コード {c['stop_codes']}・未解決の裁定 {c['unresolved_rulings']}"
                  for v, c in uc['engine_reported']))


if __name__ == '__main__':
    source_stats()
    rule_stats()
    main()
    non_pack_stats()
    reprint_stats()
    sidecar_stats()
