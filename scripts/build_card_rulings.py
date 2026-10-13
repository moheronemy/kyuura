#!/usr/bin/env python3
"""data/sidecar/ の記録（公式の最新の説明・カードの照合・裁定と未解決の論点）を検査し、
docs/rules/card-rulings.md を生成する。

サイドカーは data/cards.json を変えずに、カード・ワザに出典つきの情報を加えるファイルです
（形式は docs/data-schema.md の「サイドカー」）。

  - data/sidecar/latest_descriptions.json: 公式の書籍の「最新の説明」と印刷の文面の違い
  - data/sidecar/card_checks.json: カードの記録を公式の資料のページと照合した記録
  - data/sidecar/rulings.json: 公式ルールの条項・カードの裁定・未解決の論点・kyuura-engine の裁定 id との対応

検査すること:
  - id の書式と重複（3 つのファイルを通して。data/rule_history.json の id とも重ならない）
  - カード id があるか、ワザ・特殊能力の位置と名前が data/cards.json と合うか
  - 印刷の文面の写し（printed_text.text_ja）と照合した欄の写し（checked_fields）が、今の data/cards.json と同じか
    （data/cards.json が変わったら、照合し直すまでエラー）
  - 違い（differences）の文字列が、印刷の文面・最新の説明の中にそのままあるか
  - 出典の記号が docs/sources.md にあるか、ページが data/rule_history.json の documents のページの記録にあるか
  - 公式エラッタの記録があるカードの最新の説明は errata_ref で結ぶ（最新の説明とエラッタを混同しない）
  - 裁定の分類: CONFIRMED は推論（inference）なし、SUPPORTED は推論が必要、UNRESOLVED は issues だけ
  - 結論・論点・推論の文に、エンジンの停止コード・例外の名前（UNRESOLVED_…・RuntimeError など）を書かない
  - CONFIRMED の記録に、エンジンが CONFIRMED としていない裁定を対応させるときは reclassification（理由）が必要
  - エンジンの裁定 id: 取り込んだ範囲（S1〜S49 など）がすべて、どれかの記録か not_imported にあるか。
    同じ id を 2 つ以上の記録に対応させるときは、どれにも part（どの部分か）が必要。2 つの未解決の論点に同じ id を
    対応させない（未解決の論点の重複）
  - エンジンの未解決の裁定の一覧（engine_unresolved_index）の件数・重複・論点への対応
  - --check: 生成結果が docs/rules/card-rulings.md と同じか（ファイルは書き換えない）

使い方: python3 scripts/build_card_rulings.py [--check]
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_REL = Path('docs') / 'rules' / 'card-rulings.md'
FILES = {'latest': 'latest_descriptions.json', 'checks': 'card_checks.json', 'rulings': 'rulings.json'}
GENERATED = ('<!-- このファイルは scripts/build_card_rulings.py が data/sidecar/ から生成しています。'
             '直接編集せず、データを直してから再生成してください。 -->')
ID_PATTERNS = {
    'latest': re.compile(r'^LD-[A-Za-z0-9]+-\d{3}-(ATK|PWR)\d+$'),
    'checks': re.compile(r'^CC-[A-Za-z0-9]+-\d{3}-[A-Z]\d+$'),
    'clause': re.compile(r'^GR-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'ruling': re.compile(r'^CR-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'issue': re.compile(r'^UQ-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'comparison': re.compile(r'^CMP-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'import': re.compile(r'^ENGINE-[A-Z0-9][A-Z0-9-]*$'),
}
ENGINE_TOKENS = re.compile(r'UNRESOLVED_|RuntimeError|UnsupportedError|IllegalActionError|StateIntegrityError|Phase\.')
RULING_STATUS = ('CONFIRMED', 'SUPPORTED')
STATUS_JA = {'CONFIRMED': 'CONFIRMED（確認）', 'SUPPORTED': 'SUPPORTED（推論）', 'UNRESOLVED': 'UNRESOLVED（未解決）'}
OFFICIAL_MATERIAL = {'none_found': '公式の資料に判断材料が見つからない', 'insufficient': '公式の資料の記述だけでは決められない'}
TARGET_KINDS = {'attack': 'attacks', 'power': 'powers'}
BASIS_SHORT = {'card_text': 'カードの文面', 'card_commentary': '書籍の解説', 'general_rule': '一般の規定', 'derived': '規定からの帰結'}


# ---------------------------------------------------------------- 読み込み
def source_codes(root):
    text = (root / 'docs' / 'sources.md').read_text(encoding='utf-8')
    return set(re.findall(r'^\| ([A-Z]\d+) \|', text, re.M))


def load(root=ROOT):
    """検査と生成に使うものをまとめて読む。"""
    side = root / 'data' / 'sidecar'
    ctx = {key: json.loads((side / name).read_text(encoding='utf-8')) for key, name in FILES.items()}
    ctx['cards'] = {c['id']: c for c in json.loads((root / 'data' / 'cards.json').read_text(encoding='utf-8'))['cards']}
    ctx['rule_history'] = json.loads((root / 'data' / 'rule_history.json').read_text(encoding='utf-8'))
    ctx['rule_differences'] = json.loads((root / 'data' / 'rule_differences.json').read_text(encoding='utf-8'))
    ctx['codes'] = source_codes(root)
    return ctx


def resolve(obj, path):
    """'pokemon.attacks[1].text.ja' のような道筋で値を取り出す（ないときは KeyError）。"""
    cur = obj
    for part in path.replace(']', '').replace('[', '.').split('.'):
        if isinstance(cur, list):
            if not part.isdigit() or int(part) >= len(cur):
                raise KeyError(path)
            cur = cur[int(part)]
        elif isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(path)
    return cur


def target_path(target):
    return f"pokemon.{TARGET_KINDS[target['kind']]}[{target['index']}]"


def target_label(target):
    if target.get('kind') == 'card':
        return 'カード'
    return {'attack': 'ワザ', 'power': '特殊能力'}[target['kind']] + f"「{target['name_ja']}」"


# ---------------------------------------------------------------- 検査
def rule_history_ids(rh):
    return {x['id'] for key in ('events', 'entries', 'errata') for x in rh.get(key, [])}


def errata_cards(rh):
    """公式エラッタ・印刷の変更の記録があるカード → 記録の id。"""
    out = defaultdict(list)
    for x in rh.get('errata', []) + rh.get('entries', []):
        if x.get('category') in ('official_errata', 'printed_text_change'):
            for c in x.get('cards', []):
                out[c].append(x['id'])
    return out


def page_known(rh, code, page):
    """documents に資料があるなら、ページがその記録（1 ページまたは範囲）にあるか。資料がなければ True。"""
    docs = {d['code']: d for d in rh.get('documents', [])}
    if code not in docs:
        return True
    page = str(page)
    for pg in docs[code]['pages']:
        printed = str(pg['printed'])
        if printed == page:
            return True
        m = re.fullmatch(r'(\d+)〜(\d+)', printed)
        if m and page.isdigit() and int(m.group(1)) <= int(page) <= int(m.group(2)):
            return True
    return False


def all_ids(ctx):
    """（id, 種類, 記録）の一覧。"""
    out = [(x['id'], 'latest', x) for x in ctx['latest']['records']]
    out += [(x['id'], 'checks', x) for x in ctx['checks']['records']]
    r = ctx['rulings']
    out += [(x['id'], 'clause', x) for x in r['rule_clauses']]
    out += [(x['id'], 'ruling', x) for x in r['rulings']]
    out += [(x['id'], 'issue', x) for x in r['issues']]
    out += [(x['id'], 'comparison', x) for x in r.get('comparisons', [])]
    out += [(x['id'], 'import', x) for x in r['engine_imports']]
    return out


def check_target(errors, where, cards, card_id, target, allow_card=False):
    if card_id not in cards:
        errors.append(f'{where}: カード id がない: {card_id}')
        return None
    if allow_card and target.get('kind') == 'card':
        return None
    if target.get('kind') not in TARGET_KINDS:
        errors.append(f"{where}: 対象の種類が不正: {target.get('kind')}")
        return None
    try:
        item = resolve(cards[card_id], target_path(target))
    except KeyError:
        errors.append(f"{where}: {card_id} に {target_path(target)} がない")
        return None
    if item['name']['ja'] != target.get('name_ja'):
        errors.append(f"{where}: {card_id} の {target_path(target)} の名前が「{item['name']['ja']}」で、記録の「{target.get('name_ja')}」と違う")
    return item


def check_source(errors, where, ctx, code, page):
    if code not in ctx['codes']:
        errors.append(f'{where}: 出典の記号がない: {code}')
    elif page is not None and not page_known(ctx['rule_history'], code, page):
        errors.append(f'{where}: {code} の p.{page} が data/rule_history.json の documents のページの記録にない')


def check_engine_text(errors, where, *texts):
    for t in texts:
        if t and ENGINE_TOKENS.search(t):
            errors.append(f'{where}: エンジンの停止コード・例外の名前を、公式の裁定の文に書いている: {ENGINE_TOKENS.search(t).group(0)}')


def validate(ctx):
    errors = []
    cards, rh = ctx['cards'], ctx['rule_history']
    for key, name in FILES.items():
        if ctx[key].get('schema_version') != 1:
            errors.append(f'{name}: schema_version が 1 でない')

    ids = all_ids(ctx)
    kinds = {}
    for i, kind, _ in ids:
        if i in kinds:
            errors.append(f'id の重複: {i}')
        kinds[i] = kind
        if not ID_PATTERNS[kind].match(i):
            errors.append(f'id の書式が不正（{kind}）: {i}')
    for i in set(kinds) & rule_history_ids(rh):
        errors.append(f'id が data/rule_history.json の id と重なる: {i}')

    r = ctx['rulings']
    imports = {x['id']: x for x in r['engine_imports']}
    clauses = {x['id'] for x in r['rule_clauses']}
    latest = {x['id']: x for x in ctx['latest']['records']}
    rulings = {x['id']: x for x in r['rulings']}
    issues = {x['id']: x for x in r['issues']}
    rd_items = {x['id'] for x in ctx['rule_differences']['items']}
    rh_ids = rule_history_ids(rh)
    errata = errata_cards(rh)

    # ---- 最新の説明
    L = ctx['latest']
    seen = {}
    for x in L['records']:
        w = x['id']
        item = check_target(errors, w, cards, x['card_id'], x['target'])
        if x['card_id'] in cards and cards[x['card_id']]['name']['ja'] != x.get('card_name_ja'):
            errors.append(f"{w}: カード名が data/cards.json と違う: {x.get('card_name_ja')}")
        key = (x['card_id'], x['target']['kind'], x['target'].get('index'))
        if key in seen:
            errors.append(f'{w}: 同じカード・ワザの最新の説明が {seen[key]} にもある')
        seen[key] = w
        pt = x['printed_text']
        if item is not None:
            if pt['path'] != target_path(x['target']) + '.text.ja':
                errors.append(f"{w}: printed_text.path が対象と合わない: {pt['path']}")
            current = item['text']['ja']
            if pt['text_ja'] != current:
                errors.append(f'{w}: 印刷の文面の写しが今の data/cards.json と違う（data/cards.json が変わった。照合し直す）')
        if pt.get('image_check') not in L['image_check_values']:
            errors.append(f"{w}: image_check の値が不正: {pt.get('image_check')}")
        ld = x['latest_description']
        if not ld.get('text_ja'):
            errors.append(f'{w}: 最新の説明の文面がない')
        check_source(errors, w, ctx, ld['source'], ld['page'])
        check_source(errors, w, ctx, ld['scan'], None)
        for q in x.get('also_quoted', []):
            check_source(errors, w, ctx, q['source'], q['page'])
        if x.get('book_rule') not in clauses:
            errors.append(f"{w}: book_rule の条項がない: {x.get('book_rule')}")
        if x.get('classification') not in L['classifications']:
            errors.append(f"{w}: classification の値が不正: {x.get('classification')}")
        if x.get('errata_ref') is not None and x['errata_ref'] not in rh_ids:
            errors.append(f"{w}: errata_ref の記録がない: {x['errata_ref']}")
        if errata.get(x['card_id']) and not x.get('errata_ref'):
            errors.append(f"{w}: {x['card_id']} には公式エラッタ・印刷の変更の記録（{'・'.join(errata[x['card_id']])}）がある。errata_ref で結ぶ")
        diffs = x.get('differences', [])
        if item is not None and ld.get('text_ja'):
            if (pt['text_ja'] == ld['text_ja']) != (not diffs):
                errors.append(f'{w}: 文面が同じなら differences は空、違うなら 1 つ以上')
            for dfx in diffs:
                if dfx['kind'] not in L['difference_kinds']:
                    errors.append(f"{w}: 違いの種類が不正: {dfx['kind']}")
                if dfx['printed'] not in pt['text_ja']:
                    errors.append(f"{w}: 違いの「{dfx['printed']}」が印刷の文面にない")
                if dfx['latest'] not in ld['text_ja']:
                    errors.append(f"{w}: 違いの「{dfx['latest']}」が最新の説明にない")
        if x.get('meaning_change') not in L['meaning_change_values']:
            errors.append(f"{w}: meaning_change の値が不正: {x.get('meaning_change')}")
        if any(dfx['kind'] == 'meaning' for dfx in diffs) and x.get('meaning_change') != 'changed':
            errors.append(f'{w}: 種類 meaning の違いがあるのに meaning_change が changed でない')
        if not x.get('verification'):
            errors.append(f'{w}: verification がない')
        for v in x.get('verification', []):
            if v.get('by') == 'kyuura-engine' and v.get('import') not in imports:
                errors.append(f"{w}: verification の import がない: {v.get('import')}")

    # ---- カードの照合
    C = ctx['checks']
    seen = {}
    for x in C['records']:
        w = x['id']
        if x['card_id'] not in cards:
            errors.append(f"{w}: カード id がない: {x['card_id']}")
            continue
        if cards[x['card_id']]['name']['ja'] != x.get('card_name_ja'):
            errors.append(f"{w}: カード名が data/cards.json と違う: {x.get('card_name_ja')}")
        key = (x['card_id'], x['source'], x['page'])
        if key in seen:
            errors.append(f'{w}: 同じカード・資料・ページの照合が {seen[key]} にもある')
        seen[key] = w
        check_source(errors, w, ctx, x['source'], x['page'])
        for path, value in x['checked_fields'].items():
            try:
                current = resolve(cards[x['card_id']], path)
            except KeyError:
                errors.append(f'{w}: 照合した欄 {path} が data/cards.json にない')
                continue
            if current != value:
                errors.append(f'{w}: 照合した欄 {path} の写しが今の data/cards.json と違う（照合し直す）')
        if x.get('result') not in C['results']:
            errors.append(f"{w}: result の値が不正: {x.get('result')}")
        if (x.get('result') == 'data_error') != bool(x.get('data_error')):
            errors.append(f'{w}: result と data_error が合わない')
        diffs = x.get('differences', [])
        if x.get('result') == 'no_difference' and diffs:
            errors.append(f'{w}: 差異なし（no_difference）なのに differences がある')
        if x.get('result') == 'printed_vs_latest_only' and (not diffs or any(d['kind'] != 'printed_vs_latest' for d in diffs)):
            errors.append(f'{w}: printed_vs_latest_only なら、違いはすべて printed_vs_latest で 1 つ以上')
        for d in diffs:
            ref = d.get('latest_description_ref')
            if d['kind'] == 'printed_vs_latest' and (ref not in latest or latest[ref]['card_id'] != x['card_id']):
                errors.append(f'{w}: 違いの最新の説明の記録がない（または別のカード）: {ref}')
        for ref in x.get('latest_description_refs', []):
            if ref not in latest:
                errors.append(f'{w}: 最新の説明の記録がない: {ref}')
        same_page = {y['id'] for y in L['records'] if y['card_id'] == x['card_id'] and y['latest_description']['source'] == x['source']
                     and y['latest_description']['page'] == x['page']}
        missing = same_page - set(x.get('latest_description_refs', []))
        if missing:
            errors.append(f"{w}: 同じページの最新の説明の記録を結んでいない: {'・'.join(sorted(missing))}")
        for s in x.get('not_confused_with', []):
            cid = s.split('（')[0]
            if cid not in cards:
                errors.append(f'{w}: not_confused_with のカード id がない: {cid}')
        for v in x.get('verification', []):
            if v.get('by') == 'kyuura-engine' and v.get('import') not in imports:
                errors.append(f"{w}: verification の import がない: {v.get('import')}")

    # ---- 条項
    for x in r['rule_clauses']:
        w = x['id']
        for p in x['pages']:
            check_source(errors, w, ctx, x['source'], p)
        for ref in x.get('rule_history_refs', []):
            if ref not in rh_ids:
                errors.append(f'{w}: rule_history の記録がない: {ref}')
        for ref in x.get('rule_differences_refs', []):
            if ref not in rd_items:
                errors.append(f'{w}: rule_differences の項目がない: {ref}')

    # ---- 裁定
    basis_kinds = r['basis_kinds']
    for x in r['rulings']:
        w = x['id']
        if x.get('status') not in RULING_STATUS:
            errors.append(f"{w}: status の値が不正（裁定は CONFIRMED・SUPPORTED。未解決は issues に書く）: {x.get('status')}")
        for c in x['cards']:
            check_target(errors, w, cards, c['card_id'], c['target'], allow_card=True)
        for c in x.get('related_cards', []):
            if c not in cards:
                errors.append(f'{w}: related_cards のカード id がない: {c}')
        if not x.get('basis'):
            errors.append(f'{w}: basis がない')
        for b in x.get('basis', []):
            if b['kind'] not in basis_kinds:
                errors.append(f"{w}: 根拠の種類が不正: {b['kind']}")
            if b['kind'] == 'derived':
                if not b.get('statement'):
                    errors.append(f'{w}: derived の根拠に statement がない')
                check_engine_text(errors, w, b.get('statement'))
            elif 'card_ref' in b:
                if b['card_ref'] not in cards:
                    errors.append(f"{w}: 根拠のカード id がない: {b['card_ref']}")
                else:
                    try:
                        value = resolve(cards[b['card_ref']], b['field'])
                        if b.get('quote') and b['quote'] not in (value or ''):
                            errors.append(f"{w}: 根拠の引用が {b['card_ref']} の {b['field']} にない")
                    except KeyError:
                        errors.append(f"{w}: 根拠の欄がない: {b['card_ref']} {b['field']}")
            else:
                check_source(errors, w, ctx, b.get('source'), b.get('page'))
            if b['kind'] != 'derived' and b.get('checked') not in r['checked_values']:
                errors.append(f"{w}: 根拠の checked の値が不正: {b.get('checked')}")
        if x.get('status') == 'CONFIRMED' and x.get('inference'):
            errors.append(f'{w}: CONFIRMED に推論（inference）がある。推論を含むなら SUPPORTED にするか、記録を分ける')
        if x.get('status') == 'SUPPORTED' and not x.get('inference'):
            errors.append(f'{w}: SUPPORTED に推論（inference）がない')
        check_engine_text(errors, w, x.get('question'), x.get('conclusion'), x.get('inference'))
        for ref in x.get('rule_clause_refs', []):
            if ref not in clauses:
                errors.append(f'{w}: 条項がない: {ref}')
        targets = {c['card_id'] for c in x['cards']} | set(x.get('related_cards', []))
        for ref in x.get('latest_description_refs', []):
            if ref not in latest:
                errors.append(f'{w}: 最新の説明の記録がない: {ref}')
            elif latest[ref]['card_id'] not in targets:
                errors.append(f'{w}: 最新の説明 {ref} のカードが cards・related_cards にない')
        for ref in x.get('related_rulings', []):
            if ref not in rulings and ref not in issues:
                errors.append(f'{w}: related_rulings の記録がない: {ref}')
        for e in x.get('engine_refs', []):
            if e.get('import') not in imports:
                errors.append(f"{w}: engine_refs の import がない: {e.get('import')}")
        if x.get('status') == 'CONFIRMED':
            weaker = [e['ruling_id'] for e in x.get('engine_refs', []) if 'CONFIRMED' not in e.get('engine_classification', 'CONFIRMED')]
            rc = x.get('reclassification')
            if weaker and not (rc and rc.get('reason') and rc.get('to') == 'CONFIRMED'):
                errors.append(f"{w}: エンジンが CONFIRMED としていない裁定（{'・'.join(weaker)}）を CONFIRMED にするには reclassification（理由）が必要")

    # ---- 未解決の論点
    for x in r['issues']:
        w = x['id']
        if x.get('status') != 'UNRESOLVED':
            errors.append(f'{w}: 論点の status は UNRESOLVED')
        if not x.get('question') or not x.get('why_unresolved'):
            errors.append(f'{w}: question・why_unresolved がない')
        check_engine_text(errors, w, x.get('question'), x.get('why_unresolved'))
        if x.get('official_material') not in OFFICIAL_MATERIAL:
            errors.append(f"{w}: official_material の値が不正: {x.get('official_material')}")
        for s in x.get('sources', []):
            check_source(errors, w, ctx, s['source'], s['page'])
        for ref in x.get('rule_clause_refs', []):
            if ref not in clauses:
                errors.append(f'{w}: 条項がない: {ref}')
        eng = {e['ruling_id'] for e in x.get('engine_refs', [])}
        for c in x.get('cases', []):
            check_target(errors, w, cards, c['card_id'], c['target'])
            if c.get('engine_ruling') and c['engine_ruling'] not in eng:
                errors.append(f"{w}: 事例のエンジンの裁定 {c['engine_ruling']} が engine_refs にない")
        for e in x.get('engine_refs', []):
            if e.get('import') not in imports:
                errors.append(f"{w}: engine_refs の import がない: {e.get('import')}")

    # ---- エンジンの裁定 id との対応
    uses = defaultdict(list)
    for kind, recs in (('ruling', r['rulings']), ('issue', r['issues']), ('check', C['records'])):
        for x in recs:
            for e in x.get('engine_refs', []):
                uses[(e.get('import'), e['ruling_id'])].append((kind, x['id'], e))
    for (imp, rid), lst in uses.items():
        if len(lst) > 1 and any(not e.get('part') for _, _, e in lst):
            errors.append(f"エンジンの裁定 {rid} が {'・'.join(i for _, i, _ in lst)} に対応している。分けるなら、どれにも part（どの部分か）を書く")
        issue_ids = {i for k, i, _ in lst if k == 'issue'}
        if len(issue_ids) > 1:
            errors.append(f"エンジンの裁定 {rid} が 2 つ以上の未解決の論点（{'・'.join(sorted(issue_ids))}）にある（未解決の論点の重複）")
    for imp in r['engine_imports']:
        skipped = {n['ruling_id'] for n in imp.get('not_imported', [])}
        for rs in imp.get('ruling_sets', []):
            for n in range(rs['first'], rs['last'] + 1):
                rid = f"{rs['prefix']}{n}"
                if (imp['id'], rid) not in uses and rid not in skipped:
                    errors.append(f"{imp['id']}: エンジンの裁定 {rid} が、どの記録にも not_imported にもない")
        for n in imp.get('not_imported', []):
            if not n.get('reason'):
                errors.append(f"{imp['id']}: not_imported の {n.get('ruling_id')} に理由がない")
    idx = r.get('engine_unresolved_index', [])
    keys = Counter(u['engine_key'] for u in idx)
    for k, n in keys.items():
        if n > 1:
            errors.append(f'engine_unresolved_index: 重複: {k}')
    totals = {imp.get('engine_unresolved_total') for imp in r['engine_imports'] if 'engine_unresolved_total' in imp}
    for t in totals:
        if t != len(idx):
            errors.append(f'engine_unresolved_index: 件数が {len(idx)} で、engine_unresolved_total の {t} と違う')
    indexed_issues = set()
    for u in idx:
        if u.get('kyuura_issue'):
            if u['kyuura_issue'] not in issues:
                errors.append(f"engine_unresolved_index: {u['engine_key']} の論点がない: {u['kyuura_issue']}")
            indexed_issues.add(u['kyuura_issue'])
    for i in issues:
        if i not in indexed_issues:
            errors.append(f'{i}: engine_unresolved_index のどの項目からも結ばれていない')

    # ---- 比較
    for x in r.get('comparisons', []):
        for col in x['columns']:
            if col not in latest:
                errors.append(f"{x['id']}: 列の最新の説明の記録がない: {col}")
        for row in x['rows']:
            if len(row['values']) != len(x['columns']):
                errors.append(f"{x['id']}: 「{row['aspect']}」の値の数が列の数と違う")
    return errors


# ---------------------------------------------------------------- 参照のための関数
def annotations_for(ctx, card_id):
    """カード 1 枚に結びついたサイドカーの記録（記録がなければどれも空のリスト）。"""
    in_cards = lambda x: any(c['card_id'] == card_id for c in x['cards'])
    r = ctx['rulings']
    return {
        'latest_descriptions': [x for x in ctx['latest']['records'] if x['card_id'] == card_id],
        'card_checks': [x for x in ctx['checks']['records'] if x['card_id'] == card_id],
        'rulings': [x for x in r['rulings'] if in_cards(x)],
        'related_rulings': [x for x in r['rulings'] if not in_cards(x) and card_id in x.get('related_cards', [])],
        'issues': [x for x in r['issues'] if any(c['card_id'] == card_id for c in x.get('cases', []))],
    }


def engine_mapping(ctx, import_id):
    """エンジンの裁定 id → [（記録の種類, 記録の id, engine_refs の項目）]。"""
    out = defaultdict(list)
    r = ctx['rulings']
    for kind, recs in (('ruling', r['rulings']), ('issue', r['issues']), ('check', ctx['checks']['records'])):
        for x in recs:
            for e in x.get('engine_refs', []):
                if e.get('import') == import_id:
                    out[e['ruling_id']].append((kind, x['id'], e))
    return out


# ---------------------------------------------------------------- 生成
def md(s):
    return str(s if s is not None else '').replace('|', '\\|').replace('\n', '<br>')


def card_label(cards, cid):
    c = cards.get(cid)
    return f"{c['name']['ja']}（{cid}）" if c else cid


def basis_line(b, r):
    kind = BASIS_SHORT.get(b['kind'], b['kind'])
    if b['kind'] == 'derived':
        return f"{kind}: {b['statement']}"
    if 'card_ref' in b:
        where = f"{b['card_ref']} の {b['field']}（{r['checked_values'][b['checked']]}）"
    else:
        where = f"[{b['source']}] p.{b['page']} {b['location']}（{r['checked_values'][b['checked']].split('（')[0]}）"
    q = f"「{b['quote']}」" if b.get('quote') else ''
    return f"{kind}: {where}{(' ' + q) if q else ''}"


def engine_line(e):
    s = f"{e['ruling_id']}（{e['engine_version']}・{e['document']}）"
    if e.get('engine_classification'):
        s += f"。エンジンの分類: {e['engine_classification']}"
    if e.get('part'):
        s += f"。部分: {e['part']}"
    if e.get('engine_note'):
        s += f"。{e['engine_note']}"
    return s


def build(ctx):
    cards, r = ctx['cards'], ctx['rulings']
    L, C = ctx['latest'], ctx['checks']
    lat = {x['id']: x for x in L['records']}
    rul = {x['id']: x for x in r['rulings']}
    out = [GENERATED, '', '# カードの裁定と公式の最新の説明', '',
           'カード・ワザごとに、公式の資料で確かめた情報（公式の書籍の「最新の説明」、カードの記録の照合、裁定、未解決の論点）をまとめたページです。'
           'データは `data/sidecar/` にあり、`data/cards.json` は変えていません（形式は [データの構造](../data-schema.md) の「サイドカー」）。'
           '出典の記号は [出典と確認状況](../sources.md)、ページごとの照合の記録は [印刷物の照合記録](../printed-sources.md) を参照してください。', '',
           '次のものを区別しています。', '',
           '- **印刷の文面**: カードに印刷された文面。`data/cards.json` の日本語の文面はこれで、書きかえていません。',
           '- **最新の説明**: 公式の書籍（『ポケモンカードオフィシャルブック2000』[P43]）がカードごとに載せた書き直しの文面。p.6 は、わからない内容があればこれにしたがうとする。訂正告知（エラッタ）とは別の分類です（公式エラッタは [エラッタの履歴](errata-history.md)）。',
           '- **裁定**: 公式の資料から判断したこと。分類は次のとおりです。']
    for k, v in r['status_values'].items():
        out.append(f'  - {STATUS_JA[k]}: {v}')
    out += ['- **根拠の種類**: ' + '、'.join(f"{k}（{v}）" for k, v in r['basis_kinds'].items()) + '。推論はどれにも入れず、SUPPORTED の「推論」に書きます。',
            '- **エンジンとの対応**: kyuura-engine（対戦処理の実装）の裁定 id との対応は、調査の履歴を追うための参照です。エンジンの実装・停止コード・例外は、公式の裁定として扱いません。', '']

    # 1. 最新の説明
    out += ['## 1. 公式の最新の説明（印刷の文面との違い）', '',
            '| id | カード | 対象 | 印刷の文面（`data/cards.json`） | 最新の説明 | 違い | 意味の違い | 図版との照合 |', '|---|---|---|---|---|---|---|---|']
    for x in L['records']:
        ld = x['latest_description']
        diffs = '<br>'.join(f"「{d['printed']}」→「{d['latest']}」（{L['difference_kinds'][d['kind']].split('（')[0]}）" for d in x['differences']) or 'なし'
        out.append(f"| {x['id']} | {md(card_label(cards, x['card_id']))} | {md(target_label(x['target']))} | {md(x['printed_text']['text_ja'])} | "
                   f"{md(ld['text_ja'])}（[{ld['source']}] p.{ld['page']} {md(ld['location'])}） | {md(diffs)} | "
                   f"{md(L['meaning_change_values'][x['meaning_change']].split('（')[0])}。{md(x['meaning_note'])} | "
                   f"{md(L['image_check_values'][x['printed_text']['image_check']])}。{md(x['printed_text']['image_check_note'])} |")
    out.append('')
    for x in L['records']:
        extra = [f"同じ文面の引用: " + '、'.join(f"[{q['source']}] p.{q['page']} {q['location']}" for q in x['also_quoted'])] if x['also_quoted'] else []
        extra += [f"分類: {L['classifications'][x['classification']].split('（')[0]}。公式エラッタの記録: {x['errata_ref'] or 'なし（訂正告知は見つかっていない）'}"]
        extra += x['notes']
        out.append(f"- {x['id']}: " + ' '.join(md(e) for e in extra))
    out.append('')

    # 2. 照合
    out += ['## 2. カードの記録の照合', '',
            '照合の記録のないカードは未照合です（「照合して差異なし」とは別）。照合した欄の値は記録に写してあり、`data/cards.json` が変わると検査がエラーにします。', '',
            '| id | カード | 資料・ページ | 照合した欄 | 結果 | データの誤り | 見たこと |', '|---|---|---|---|---|---|---|']
    for x in C['records']:
        out.append(f"| {x['id']} | {md(card_label(cards, x['card_id']))} | [{x['source']}] p.{x['page']}（{md(x['location'])}） | "
                   f"{md('、'.join(x['checked_fields']))} | {md(C['results'][x['result']])} | {'あり' if x['data_error'] else 'なし'} | "
                   f"{md(' '.join(x['findings']))} |")
    out.append('')

    # 3. 条項
    out += ['## 3. 公式ルールの条項', '',
            '裁定が参照する公式ルールの箇所です。規則の本体の記録は `data/rule_history.json`（`NEO-2000-OFFICIAL-RULES` など）と `data/rule_differences.json` にあり、ここは参照する位置の索引です。', '',
            '| id | 資料・ページ | 箇所 | 要旨 | 本体の記録 |', '|---|---|---|---|---|']
    for x in r['rule_clauses']:
        refs = '・'.join(x['rule_history_refs'] + [f"rule_differences の {i}" for i in x['rule_differences_refs']])
        out.append(f"| {x['id']} | [{x['source']}] p.{'・p.'.join(x['pages'])} | {md(x['section'])} | {md(x['summary'])} | {md(refs)} |")
    out.append('')

    # 4. 裁定
    out += ['## 4. 裁定', '']
    counts = Counter(x['status'] for x in r['rulings'])
    out.append('記録 ' + str(len(r['rulings'])) + ' 件（' + '・'.join(f'{k} {counts[k]}' for k in RULING_STATUS) + '）。未解決の論点は 5 章です。')
    out.append('')
    groups = defaultdict(list)
    for x in r['rulings']:
        c = x['cards'][0]
        groups[(c['card_id'], target_label(c['target']))].append(x)
    for (cid, tl), lst in groups.items():
        out += [f'### {card_label(cards, cid)}・{tl}', '']
        topics = defaultdict(list)
        for x in lst:
            topics[x['topic']].append(x)
        for topic, xs in topics.items():
            out += [f'#### {topic}', '']
            for x in xs:
                out.append(f"- **{x['id']}**（{STATUS_JA[x['status']]}）{md(x['question'])} → **{md(x['conclusion'])}**")
                for b in x['basis']:
                    out.append(f'  - 根拠: {md(basis_line(b, r))}')
                if x.get('inference'):
                    out.append(f"  - 推論: {md(x['inference'])}")
                refs = x['rule_clause_refs'] + x['latest_description_refs'] + x['related_rulings']
                if refs:
                    out.append(f"  - 参照: {'・'.join(refs)}")
                if x.get('related_cards'):
                    out.append(f"  - 関係するカード: {'・'.join(card_label(cards, c) for c in x['related_cards'])}")
                for e in x['engine_refs']:
                    out.append(f'  - エンジン: {md(engine_line(e))}')
                if x.get('reclassification'):
                    rc = x['reclassification']
                    out.append(f"  - 分類の変更: {md(rc['from'])} → {rc['to']}。{md(rc['reason'])}")
                for n in x.get('notes', []):
                    out.append(f'  - 注: {md(n)}')
            out.append('')

    # 5. 論点
    out += ['## 5. 未解決の論点', '',
            '公式の資料で決められない論点です。同じ問いのエンジンの裁定はまとめて 1 つの論点にし、事例（cases）として結びます。', '']
    for x in r['issues']:
        out += [f"### {x['id']}", '',
                f"- 論点: {md(x['question'])}",
                f"- 決められない理由: {md(x['why_unresolved'])}",
                f"- 公式の資料: {OFFICIAL_MATERIAL[x['official_material']]}（" + '、'.join(f"[{s['source']}] p.{s['page']} {s['location']}" for s in x['sources']) + '）',
                f"- 参照する条項: {'・'.join(x['rule_clause_refs'])}"]
        for c in x['cases']:
            out.append(f"- 事例: {card_label(cards, c['card_id'])}・{target_label(c['target'])}（エンジンの {c['engine_ruling']}）: {md(c['note'])}")
        if x.get('reachability'):
            out.append(f"- 起こるか: エンジンの対応カード — {md(x['reachability']['engine_card_pool'])}。旧裏期の全カード — {md(x['reachability']['all_cards'])}")
        for e in x.get('related_engine_rulings', []):
            out.append(f"- 関係するエンジンの裁定: {e['ruling_id']}（{e['engine_version']}・{e['document']}）: {md(e['relation'])}")
        for e in x['engine_refs']:
            out.append(f'- エンジン: {md(engine_line(e))}')
        for n in x.get('notes', []):
            out.append(f'- 注: {md(n)}')
        out.append('')

    # 6. 比較
    out += ['## 6. 比較', '']
    for x in r.get('comparisons', []):
        cols = [lat[cid] for cid in x['columns']]
        out += [f"### {x['id']}: {x['title']}", '',
                '| 項目 | ' + ' | '.join(md(f"{card_label(cards, c['card_id'])}「{c['target']['name_ja']}」") for c in cols) + ' | 根拠 |',
                '|---|' + '---|' * len(cols) + '---|']
        for row in x['rows']:
            out.append(f"| {md(row['aspect'])} | " + ' | '.join(md(v) for v in row['values']) + f" | {md(row['basis'])} |")
        out.append('')
        out += [f'- {md(n)}' for n in x.get('notes', [])]
        out.append('')

    # 7. エンジンとの対応
    out += ['## 7. kyuura-engine の裁定との対応', '']
    for imp in r['engine_imports']:
        out += [f"### {imp['id']}", '',
                '| 項目 | 内容 |', '|---|---|',
                f"| リポジトリ・ブランチ | {imp['repository']}（{imp['branch']}） |",
                f"| コミット | `{imp['commit']}`（{imp['engine_version']}。前の版 `{imp['parent_version_commit'][:7]}`） |",
                f"| エンジンが参照した kyuura のコミット | `{imp['kyuura_commit_used_by_engine']}` |",
                f"| 取り込んだ日 | {imp['imported_on']} |",
                f"| 読んだ文書 | {md('、'.join(imp['documents']))} |", '']
        out += [f'- {md(n)}' for n in imp.get('notes', [])]
        out.append('')
        mapping = engine_mapping(ctx, imp['id'])
        for rs in imp.get('ruling_sets', []):
            reported = '・'.join(f'{k} {v}' for k, v in rs['engine_reported_counts'].items())
            out += [f"エンジンの裁定 {rs['prefix']}{rs['first']}〜{rs['prefix']}{rs['last']}（{rs['document']}）。エンジンが報告した分類: {reported}。", '',
                    '| エンジンの id | エンジンの分類 | kyuura の記録 | kyuura の分類 | 部分・備考 |', '|---|---|---|---|---|']
            tally = Counter()
            for n in range(rs['first'], rs['last'] + 1):
                rid = f"{rs['prefix']}{n}"
                lst = mapping.get(rid, [])
                if not lst:
                    out.append(f'| {rid} | — | 取り込んでいない | — | — |')
                    tally['取り込んでいない'] += 1
                    continue
                kinds = {k for k, _, _ in lst}
                tally['未解決の論点に結んだ' if kinds == {'issue'} else 'カードの照合に結んだ' if kinds == {'check'} else
                      '裁定として記録（分けた）' if len(lst) > 1 else '裁定として記録'] += 1
                for kind, rec_id, e in lst:
                    if kind == 'ruling':
                        st = STATUS_JA[rul[rec_id]['status']]
                    elif kind == 'issue':
                        st = STATUS_JA['UNRESOLVED']
                    else:
                        st = 'カードの照合'
                    note = '・'.join(s for s in (e.get('part'), e.get('engine_note')) if s)
                    out.append(f"| {rid} | {md(e.get('engine_classification', ''))} | {rec_id} | {st} | {md(note)} |")
            out += ['', '集計: ' + '、'.join(f'{k} {v}' for k, v in tally.items()) + '。', '']
            st_counts = Counter()
            for n in range(rs['first'], rs['last'] + 1):
                for kind, rec_id, _ in mapping.get(f"{rs['prefix']}{n}", []):
                    st_counts[(rul[rec_id]['status'] if kind == 'ruling' else 'UNRESOLVED' if kind == 'issue' else 'カードの照合', rec_id)] += 1
            by_status = Counter(s for s, _ in st_counts)
            out += ['対応する kyuura の記録（重複を除く）: ' + '、'.join(f'{k} {v}' for k, v in sorted(by_status.items())) + '。', '']
        if imp.get('not_imported'):
            out += [f"- 取り込んでいない: {n['ruling_id']}（{md(n['reason'])}）" for n in imp['not_imported']] + ['']

    # 8. エンジンの未解決の一覧
    idx = r.get('engine_unresolved_index', [])
    out += ['## 8. エンジンの未解決の裁定と kyuura の論点', '',
            f'kyuura-engine が「原典で決められない」として止めている、または決めていない裁定の一覧です（{len(idx)} 件。停止コードはエンジンの仕組みで、公式の裁定ではありません）。'
            'kyuura の論点に取り込んだものだけ、論点の id を書いています。', '',
            '| エンジンの id | 版 | 文書 | 停止コード | 内容 | kyuura の論点 |', '|---|---|---|---|---|---|']
    for u in idx:
        out.append(f"| {u['engine_key']} | {u['engine_version']} | {u['document']} | {('`' + u['stop_code'] + '`') if u.get('stop_code') else '—'} | {md(u['summary'])} | {u.get('kyuura_issue') or '取り込んでいない'} |")
    out.append('')
    return '\n'.join(out)


def main():
    check = '--check' in sys.argv[1:]
    ctx = load()
    errors = validate(ctx)
    if errors:
        for e in errors:
            print('エラー:', e, file=sys.stderr)
        sys.exit(1)
    text = build(ctx)
    out = ROOT / OUT_REL
    if check:
        if not out.exists() or out.read_text(encoding='utf-8') != text:
            print(f'{OUT_REL} が data/sidecar/ と合いません。python3 scripts/build_card_rulings.py で生成してください', file=sys.stderr)
            sys.exit(1)
    else:
        out.write_text(text, encoding='utf-8')
    r = ctx['rulings']
    print(f"{len(ctx['latest']['records'])} latest descriptions, {len(ctx['checks']['records'])} card checks, "
          f"{len(r['rule_clauses'])} clauses, {len(r['rulings'])} rulings, {len(r['issues'])} issues; OK")


if __name__ == '__main__':
    main()
