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
    （data/cards.json が変わったら、照合し直すまでエラー。照合のあとでデータを訂正した欄は、訂正の記録
    data/curation/card_corrections.json に照合した値（before）から今の値（after）への訂正があり、その card_checks_affected に
    この照合の記録があればよい。過去の照合の記録は書きかえない）
  - 違い（differences）の文字列が、印刷の文面・最新の説明の中にそのままあるか
  - 出典の記号が docs/sources.md にあるか、ページが data/rule_history.json の documents のページの記録にあるか
  - 公式エラッタの記録があるカードの最新の説明は errata_ref で結ぶ（最新の説明とエラッタを混同しない）
  - カードの照合の結果: 差異なしなら、結んだ最新の説明にも違いがない。データの誤り（data_error）は照合した欄と今の値を書く。
    照合のあとで直したデータ（corrections）は、直したあとの値が照合した欄の写しと同じか。値の欠け（data_gaps）は、
    今の data/cards.json でも空か（値が入ったら照合し直す）
  - 裁定の分類: CONFIRMED は推論（inference）なし、SUPPORTED は推論が必要、UNRESOLVED は issues だけ。
    同じ問い（cards と question が同じ）の裁定・論点を 2 つ作らない
  - 結論・論点・推論の文に、エンジンの停止コード・例外の名前（UNRESOLVED_…・RuntimeError・POWER_SUPPRESSED など）を書かない
  - CONFIRMED の記録に、エンジンが CONFIRMED としていない裁定を対応させるときは reclassification（理由）が必要。
    SUPPORTED の記録に、エンジンが CONFIRMED だけとした裁定を対応させるときも reclassification（理由）が必要
  - エンジンが「実装上の仮定」だけとした裁定は、裁定・条項に対応させない（not_imported に理由を書く）。
    条項（rule_clauses）に対応させるのは、エンジンが CONFIRMED とした裁定だけ
  - エンジンの裁定 id: 版ごとの取り込み（engine_imports）の、文書ごとの範囲（ruling_sets）がすべて、どれかの記録か
    not_imported にあるか。対応は（取り込み, 文書, id）で区別する（版が違えば同じ id が別の裁定）。
    v0.26 からの取り込みの not_imported は classification（公式の資料による当てはめ・研究上の解釈・未解決の問いの当てはめ・
    エンジンの仮定・採用した仕様・実装の都合・表記の違い・処理の記録）を書き、status と合うか（excluded は仮定・実装の都合・表記、
    existing_record は kyuura_records の既存の記録、adopted_spec は engine_positions の記録）を確かめる
    engine_refs の文書・版・id が、その取り込みの範囲にあるか。同じ id を記録と not_imported の両方に置かない。
    同じ id を 2 つ以上の記録に対応させるときは、どれにも part（どの部分か）が必要。2 つの未解決の論点に同じ id を
    対応させない（未解決の論点の重複）。取り込みの imported_rulings・unresolved_rulings が対応から求めたものと同じか。
    not_imported の status（excluded は実装の判断だけ・deferred・needs_recheck）。別の版の裁定を仮に結べるのは、
    その版の取り込みがまだないあいだだけ
  - エンジンの未解決の裁定の一覧（engine_unresolved_index）の件数・重複・扱い（disposition）・論点への対応
    （not_yet_imported は、その版の取り込みがまだないあいだだけ）
  - 最新の説明・カードの照合の記録で、原典を誰が確かめたか: kyuura が画像を読んだ確認（verification の by: kyuura）がない
    記録は、kyuura-engine の照合の記録の取り込み（import_provenance）で、原典の確認日（source_checked_on）・その根拠・方法・
    エンジンの記録の場所を書く。取り込んだ日（imported_on）と原典の確認日を分け、取り込みの記録に kyuura の確認を書かない
  - エンジンの採用した仕様・簡略化・実装の事項（engine_positions）: kind・取り込み・カード・kyuura の記録があるか、裁定の status を
    持たないか、採用した仕様の裁定 id がその取り込みの not_imported に adopted_spec として結ばれているか
  - エンジンの未解決の一覧の数: 版ごとの engine_unresolved_total と、その版までに数える項目（counted_from_version の版から数える）が同じか
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
    'latest': re.compile(r'^LD-[A-Za-z0-9]+-\d{3}-((ATK|PWR)\d+|TRAINER)$'),
    'checks': re.compile(r'^CC-[A-Za-z0-9]+-\d{3}-[A-Z]\d+$'),
    'clause': re.compile(r'^GR-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'ruling': re.compile(r'^CR-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'issue': re.compile(r'^UQ-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'comparison': re.compile(r'^CMP-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
    'import': re.compile(r'^ENGINE-[A-Z0-9][A-Z0-9-]*$'),
    'position': re.compile(r'^ENG-V\d+-[A-Z0-9][A-Z0-9-]*[A-Z0-9]$'),
}
ENGINE_TOKENS = re.compile(r'UNRESOLVED_|RuntimeError|UnsupportedError|IllegalActionError|StateIntegrityError|Phase\.|'
                           r'\b[A-Z][A-Z0-9]*_[A-Z0-9_]*[A-Z0-9]\b')
COMMIT = re.compile(r'^[0-9a-f]{40}$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
IMPORT_PROVENANCE_KINDS = {
    'engine_record': 'kyuura-engine の照合の記録（kyuura_engine/data/card_verification.json）を取り込んだ。kyuura は原典の画像を読み直していない',
}
ENGINE_VERIFICATION_KEYS = ('record', 'source_checked_on', 'source_checked_on_basis', 'method')
DISPOSITIONS = {
    'issue': 'kyuura の未解決の論点（kyuura_issue）に取り込んだ',
    'implementation_only': '歴史上の論点ではない（エンジンの実装・処理の都合）。論点にしない',
    'out_of_scope': '取り込みの範囲（版ごとの取り込み engine_imports）の外の版の裁定。kyuura では原典を確かめておらず、論点にしていない',
    'not_yet_imported': 'その版の取り込み（engine_imports）がまだない。取り込んだら issue・implementation_only・out_of_scope のどれかにする（取り込んだ版には使えない）',
}
DISPOSITION_SHORT = {'issue': '論点に取り込んだ', 'implementation_only': '実装だけの問題', 'out_of_scope': '取り込みの範囲の外',
                     'not_yet_imported': 'その版を取り込む前'}
MAPPED_KINDS = ('ruling', 'issue', 'check', 'clause')
NOT_IMPORTED_STATUS = {
    'excluded': '対象外（実装の判断）',
    'deferred': '保留',
    'needs_recheck': '要再確認',
    'card_application': 'カードごとの当てはめ（新しい裁定にしない）',
    'existing_record': '既存の記録の当てはめ（kyuura_records）',
    'adopted_spec': 'エンジンの採用した仕様（engine_positions）',
}
# 取り込まない行の分類（v0.26 からの取り込みで必須）。公式の資料・研究上の解釈・未解決の論点・エンジンの仮定・実装の都合・処理の記録を分ける
NOT_IMPORTED_CLASSIFICATIONS = {
    'official_confirmed': 'エンジンが CONFIRMED とした当てはめ（カードの文面・一般規定がそのまま当てはまる）。kyuura は原典を読み直していない',
    'supported_interpretation': 'エンジンが SUPPORTED とした読み方（推論を含む研究上の解釈）',
    'unresolved_rules_question': '未解決の問いの当てはめ（既存の論点と同じ問い）',
    'engine_assumption': 'エンジンの実装上の仮定・判断・簡略化',
    'engine_adopted_spec': 'エンジンの採用した仕様（公式の裁定ではない）',
    'engine_implementation': 'エンジンの実装の都合（未対応・起こらない場面・計算の上限・保存の形式）',
    'notation_difference': '表記・転記の違い',
    'card_text_application': '印刷の文面・最新の説明と既存の記録から決めた処理の記録（分類の欄がない）',
}
CLASSIFICATION_STATUSES = {
    'excluded': {'engine_assumption', 'engine_implementation', 'notation_difference'},
    'card_application': {'official_confirmed', 'supported_interpretation', 'card_text_application'},
    'existing_record': {'official_confirmed', 'supported_interpretation', 'unresolved_rules_question', 'card_text_application'},
    'adopted_spec': {'engine_adopted_spec'},
    'deferred': set(NOT_IMPORTED_CLASSIFICATIONS),
    'needs_recheck': set(NOT_IMPORTED_CLASSIFICATIONS),
}
CLASSIFIED_FROM = 'v0.26'  # この版からの取り込みは、取り込まない行に classification を書く
ENGINE_POSITION_KINDS = {
    'adopted_spec': 'エンジンが採用した仕様（原典で決まらない点を、エンジンが決めて実装した。公式の裁定ではない）',
    'simplification': 'エンジンが簡略化した仕様（印刷の文面の処理を簡単にした。エラッタ・最新の説明ではない）',
    'implementation_matter': 'エンジンの実装の事項（不具合・未対応・制限。公式の未解決の裁定ではない）',
}


def basis_pages(rec):
    """記録が根拠に挙げる資料のページ（P43 p.16・p.90 のように）。根拠のない記録（推論だけ）は空。"""
    pages = []
    for b in rec.get('basis', []) + rec.get('sources', []):
        if b.get('source') and b.get('page'):
            pages.append((b['source'], str(b['page'])))
    if rec.get('source') and rec.get('pages'):
        pages += [(rec['source'], str(p)) for p in rec['pages']]
    if rec.get('source') and rec.get('page'):
        pages.append((rec['source'], str(rec['page'])))
    by_source = {}
    for src, page in pages:
        by_source.setdefault(src, [])
        if page not in by_source[src]:
            by_source[src].append(page)
    return '、'.join(f"{src} " + '・'.join(f'p.{p}' for p in ps) for src, ps in by_source.items())


def engine_cls_is_pure(cls, word):
    """エンジンの分類の文字列が word（CONFIRMED・実装上の仮定）だけで、ほかの分類を含まないか。"""
    others = [w for w in ('CONFIRMED', 'SUPPORTED', 'UNRESOLVED', '実装上の仮定', '実装上の扱い', '該当なし') if w != word]
    return bool(cls) and word in cls and not any(o in cls for o in others)
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
    ledger = root / 'data' / 'curation' / 'card_corrections.json'
    ctx['corrections'] = json.loads(ledger.read_text(encoding='utf-8'))['corrections'] if ledger.exists() else []
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
    if target['kind'] == 'trainer':
        return 'trainer'
    return f"pokemon.{TARGET_KINDS[target['kind']]}[{target['index']}]"


def target_label(target):
    if target.get('kind') == 'card':
        return 'カード'
    if target.get('kind') == 'trainer':
        return 'トレーナー'
    if target.get('kind') == 'energy':
        return 'エネルギー'
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
    out += [(x['id'], 'position', x) for x in r.get('engine_positions', [])]
    return out


def check_target(errors, where, cards, card_id, target, allow_card=False):
    if card_id not in cards:
        errors.append(f'{where}: カード id がない: {card_id}')
        return None
    if allow_card and target.get('kind') == 'card':
        return None
    if target.get('kind') == 'energy':
        card = cards[card_id]
        if card.get('category') != 'energy' or card['name']['ja'] != target.get('name_ja') or 'index' in target:
            errors.append(f'{where}: エネルギーの対象は、エネルギーカードのカード名を使い、index を持たない')
        return card.get('energy')
    if target.get('kind') == 'trainer':
        card = cards[card_id]
        if card.get('category') != 'trainer' or not isinstance(card.get('trainer'), dict):
            errors.append(f'{where}: {card_id} はトレーナーカードではない')
            return None
        if target.get('name_ja') != card['name']['ja'] or 'index' in target:
            errors.append(f'{where}: トレーナーの対象はカード名を使い、index を持たない')
        return card['trainer']
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


def ruling_set_ids(rs):
    """ruling_sets の 1 つの範囲の id（prefix + first〜last と、extra_ids）。"""
    return [f"{rs['prefix']}{n}" for n in range(rs['first'], rs['last'] + 1)] + list(rs.get('extra_ids', []))


def engine_uses(ctx):
    """（取り込み, 文書, エンジンの裁定 id）→ [（記録の種類, 記録の id, engine_refs の項目）]。"""
    out = defaultdict(list)
    r = ctx['rulings']
    for kind, recs in (('ruling', r['rulings']), ('issue', r['issues']), ('check', ctx['checks']['records']),
                       ('clause', r['rule_clauses'])):
        for x in recs:
            for e in x.get('engine_refs', []):
                out[(e.get('import'), e.get('document'), e['ruling_id'])].append((kind, x['id'], e))
    return out


def check_provenance(errors, w, x):
    """原典を誰が確かめたか。kyuura が画像を読んでいない記録（エンジンの照合の記録の取り込み）は import_provenance で区別し、
    原典の確認日（エンジンの記録の日付）と取り込んだ日を分ける。"""
    ver = x.get('verification', [])
    kyuura_read = any(v.get('by') == 'kyuura' for v in ver)
    prov = x.get('import_provenance')
    if prov is None:
        if not kyuura_read:
            errors.append(f'{w}: kyuura が原典を読んだ確認（verification の by: kyuura）がない。'
                          f'kyuura-engine の照合の記録の取り込みなら import_provenance を書く')
        return
    if prov.get('kind') not in IMPORT_PROVENANCE_KINDS:
        errors.append(f"{w}: import_provenance の kind の値が不正: {prov.get('kind')}")
    if kyuura_read or prov.get('kyuura_reread_source') is not False:
        errors.append(f'{w}: 取り込みの記録（import_provenance）に、kyuura が原典を読んだ確認を書かない'
                      f'（読み直したなら by: kyuura の確認を加え、import_provenance を外す）')
    imported_on = prov.get('imported_on') or ''
    if not DATE.match(imported_on):
        errors.append(f'{w}: import_provenance の imported_on（取り込んだ日）がない')
    if not prov.get('scope_note'):
        errors.append(f'{w}: import_provenance の scope_note（照合の範囲はエンジンの記録の範囲だけ、など）がない')
    engine = [v for v in ver if v.get('by') == 'kyuura-engine']
    if not engine:
        errors.append(f'{w}: import_provenance の記録に、kyuura-engine の照合の記録（verification の by: kyuura-engine）がない')
    for v in engine:
        for k in ENGINE_VERIFICATION_KEYS:
            if not v.get(k):
                errors.append(f'{w}: 取り込んだエンジンの照合の記録に {k} がない')
        checked = v.get('source_checked_on') or ''
        if checked and not DATE.match(checked):
            errors.append(f'{w}: source_checked_on の書式が不正: {checked}')
        elif checked and DATE.match(imported_on) and checked > imported_on:
            errors.append(f'{w}: 原典の確認日（{checked}）が取り込んだ日（{imported_on}）より後')


def provenance_text(x):
    """生成するページに書く、原典を確かめた人と日付（kyuura が読んだ記録は空）。"""
    prov = x.get('import_provenance')
    if not prov:
        return ''
    dates = sorted({v['source_checked_on'] for v in x.get('verification', []) if v.get('by') == 'kyuura-engine' and v.get('source_checked_on')})
    return (f"【kyuura-engine の照合の記録の取り込み。原典の確認 {'・'.join(dates)}（エンジン）、取り込み {prov.get('imported_on')}。"
            f"kyuura は画像を読み直していない】")


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
    positions = {x['id']: x for x in r.get('engine_positions', [])}
    all_record_ids = set(kinds)
    rd_items = {x['id'] for x in ctx['rule_differences']['items']}
    rh_ids = rule_history_ids(rh)
    errata = errata_cards(rh)

    # 規定・論点も、エンジンの記録の取り込みを独立の画像確認と混同しない。
    for x in r['rule_clauses'] + r['rulings'] + r['issues']:
        prov = x.get('source_provenance')
        if prov is None:
            continue
        if (prov.get('repository') != 'moheronemy/kyuura-engine'
                or not COMMIT.fullmatch(prov.get('commit') or '')
                or not DATE.fullmatch(prov.get('imported_on') or '')
                or not prov.get('document') or prov.get('kyuura_reread_source') is not False):
            errors.append(f"{x['id']}: エンジンの規定・論点の取り込みの出所が不正")
        if x.get('checked') == 'kyuura_image' or any(b.get('checked') == 'kyuura_image' for b in x.get('basis', [])):
            errors.append(f"{x['id']}: エンジンの記録の取り込みをkyuuraの画像確認にしない")

    # ---- 最新の説明
    L = ctx['latest']
    seen = {}
    for x in L['records']:
        w = x['id']
        item = check_target(errors, w, cards, x['card_id'], x['target'])
        if w.endswith('-TRAINER') != (x['target'].get('kind') == 'trainer'):
            errors.append(f'{w}: 最新の説明のidとトレーナーの対象が合わない')
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
        if pt.get('image_check') == 'different_text':
            if not pt.get('image_text_ja') or pt['image_text_ja'] == pt['text_ja'] or not pt.get('image_check_note'):
                errors.append(f'{w}: 図版の文面相違には、異なる image_text_ja と版を断定しない説明が必要')
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
        check_provenance(errors, w, x)

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
                # 照合のあとでデータを訂正した欄は、訂正の記録（data/curation/card_corrections.json）で、照合した値（before）から今の値（after）への
                # 訂正が記録されていればよい（過去の照合の記録を書きかえない）。記録がなければ照合し直す
                fix = next((c for c in ctx['corrections'] if c['card_id'] == x['card_id'] and c['field'] == path
                            and c['before'] == value and c['after'] == current), None)
                if fix is None:
                    errors.append(f'{w}: 照合した欄 {path} の写しが今の data/cards.json と違う（照合し直すか、訂正の記録 data/curation/card_corrections.json に前後の値を書く）')
                elif x['id'] not in fix.get('card_checks_affected', []):
                    errors.append(f"{w}: 照合した欄 {path} を訂正した記録 {fix['id']} の card_checks_affected に、この照合の記録がない")
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
            elif x.get('result') == 'no_difference' and latest[ref]['differences']:
                errors.append(f'{w}: 照合して差異なし（no_difference）なのに、結んだ最新の説明 {ref} に印刷の文面との違いがある')
        for d in diffs:
            if d['kind'] not in ('printed_vs_latest', 'data_error'):
                errors.append(f"{w}: 違いの種類が不正: {d['kind']}")
        if x.get('result') == 'data_error':
            de = x.get('data_error')
            if not isinstance(de, list) or not de:
                errors.append(f'{w}: data_error には、誤りの欄・kyuura の値・資料の値を書く（リスト）')
            else:
                for e in de:
                    if e.get('field') not in x['checked_fields']:
                        errors.append(f"{w}: data_error の欄 {e.get('field')} が checked_fields にない")
                    elif e.get('kyuura_value') != x['checked_fields'][e['field']]:
                        errors.append(f"{w}: data_error の kyuura の値が、照合した欄 {e['field']} の写しと違う")
                    if not e.get('source_value') or e.get('source_value') == e.get('kyuura_value'):
                        errors.append(f"{w}: data_error の資料の値がない（または kyuura の値と同じ）: {e.get('field')}")
                    if e.get('fix_status') != 'candidate':
                        errors.append(f"{w}: data_error の fix_status は candidate（この記録ではデータを直さない。修正は別の作業）")
        corrected = set()
        for c in x.get('corrections', []):
            f = c.get('field')
            corrected.add(f)
            if f not in x['checked_fields']:
                errors.append(f'{w}: corrections の欄 {f} が checked_fields にない（直した欄は照合し直して写す）')
            elif c.get('after') != x['checked_fields'][f]:
                errors.append(f'{w}: corrections の直したあとの値が、照合した欄 {f} の写しと違う')
            if c.get('before') == c.get('after'):
                errors.append(f'{w}: corrections の直す前と直したあとの値が同じ: {f}')
            if not re.fullmatch(r'[0-9a-f]{7,40}', c.get('commit') or ''):
                errors.append(f"{w}: corrections の commit（データを直したコミット）がない: {f}")
            for k in ('evidence', 'method'):
                if not c.get(k):
                    errors.append(f'{w}: corrections の {k} がない: {f}')
        if x.get('data_error') and corrected & {e.get('field') for e in x['data_error']}:
            errors.append(f'{w}: 同じ欄を data_error（修正の候補）と corrections（直した）の両方に書かない')
        for g in x.get('data_gaps', []):
            f = g.get('field')
            if f in x['checked_fields']:
                errors.append(f'{w}: data_gaps の欄 {f} を checked_fields に入れない（値がないので照合していない）')
            try:
                current = resolve(cards[x['card_id']], f)
            except (KeyError, TypeError):
                errors.append(f'{w}: data_gaps の欄 {f} が data/cards.json にない')
            else:
                if current not in (None, '', []):
                    errors.append(f'{w}: data_gaps の欄 {f} に値が入っている（照合し直して、記録を直す）')
                elif current != g.get('kyuura_value'):
                    errors.append(f'{w}: data_gaps の kyuura の値が、今の data/cards.json の {f} と違う')
            if not g.get('source_value'):
                errors.append(f'{w}: data_gaps の資料の値がない: {f}')
            if g.get('status') not in C.get('gap_statuses', {}):
                errors.append(f"{w}: data_gaps の status の値が不正: {g.get('status')}")
            for k in ('evidence', 'cause'):
                if not g.get(k):
                    errors.append(f'{w}: data_gaps の {k} がない: {f}')
        same_page ={y['id'] for y in L['records'] if y['card_id'] == x['card_id'] and y['latest_description']['source'] == x['source']
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
        if not x.get('verification'):
            errors.append(f'{w}: verification がない')
        check_provenance(errors, w, x)

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
        for e in x.get('engine_refs', []):
            if 'CONFIRMED' not in (e.get('engine_classification') or ''):
                errors.append(f"{w}: 一般の規定（条項）に、エンジンが CONFIRMED としていない裁定 {e['ruling_id']} を対応させている（推論を含むなら裁定 CR- にする）")

    # ---- 裁定
    basis_kinds = r['basis_kinds']
    seen_questions = {}
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
        rc = x.get('reclassification')
        if x.get('status') == 'CONFIRMED':
            weaker = [e['ruling_id'] for e in x.get('engine_refs', []) if 'CONFIRMED' not in e.get('engine_classification', 'CONFIRMED')]
            if weaker and not (rc and rc.get('reason') and rc.get('to') == 'CONFIRMED'):
                errors.append(f"{w}: エンジンが CONFIRMED としていない裁定（{'・'.join(weaker)}）を CONFIRMED にするには reclassification（理由）が必要")
        if x.get('status') == 'SUPPORTED':
            stronger = [e['ruling_id'] for e in x.get('engine_refs', []) if engine_cls_is_pure(e.get('engine_classification'), 'CONFIRMED')]
            if stronger and not (rc and rc.get('reason') and rc.get('to') == 'SUPPORTED'):
                errors.append(f"{w}: エンジンが CONFIRMED とした裁定（{'・'.join(stronger)}）を SUPPORTED にするには reclassification（理由）が必要")
        key = (frozenset((c['card_id'], c['target'].get('kind'), c['target'].get('index')) for c in x['cards']), x.get('question'))
        if key in seen_questions:
            errors.append(f'{w}: 同じカード・同じ問いの記録が {seen_questions[key]} にもある（裁定の重複）')
        seen_questions[key] = w

    # ---- 未解決の論点
    for x in r['issues']:
        w = x['id']
        if ('issue', x.get('question')) in seen_questions:
            errors.append(f"{w}: 同じ問いの未解決の論点が {seen_questions[('issue', x.get('question'))]} にもある（論点の重複）")
        seen_questions[('issue', x.get('question'))] = w
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
        if not x.get('engine_refs'):
            # kyuura の調査で立てた論点（エンジンの裁定に結ばない）。記録した日と、その時点の最新の取り込みを書く（過去の時点の数から外すため）
            ra = x.get('recorded_after') or {}
            if ra.get('import') not in imports or not DATE.fullmatch(ra.get('date') or ''):
                errors.append(f'{w}: engine_refs のない論点には recorded_after（記録した時点の最新の取り込み import と日付 date）が要る')
            if not x.get('not_in_engine_index'):
                errors.append(f'{w}: engine_refs のない論点は、エンジンの未解決の一覧に結べないので not_in_engine_index: true')
        a = x.get('audit')
        if not isinstance(a, dict):
            errors.append(f'{w}: audit（結果への影響・解決に要る資料・調べた範囲・新しく読んだ資料）がない')
            continue
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', a.get('audited_on') or ''):
            errors.append(f"{w}: audit の audited_on（日付）がない")
        if a.get('game_effect') not in r.get('game_effect_values', {}):
            errors.append(f"{w}: audit の game_effect の値が不正: {a.get('game_effect')}")
        for k in ('game_effect_note', 'resolution_needs', 'searched'):
            if not a.get(k):
                errors.append(f'{w}: audit の {k} がない')
        check_engine_text(errors, w, a.get('game_effect_note'), a.get('resolution_needs'))
        if not isinstance(a.get('new_sources'), list):
            errors.append(f'{w}: audit の new_sources はリスト（新しく読んだ資料がなければ空）')
        for ns in a.get('new_sources') or []:
            check_source(errors, w, ctx, ns.get('source'), ns.get('page'))
            if not ns.get('what'):
                errors.append(f"{w}: audit の new_sources に、読んで分かったことがない: p.{ns.get('page')}")
            if ns.get('resolves') is not False:
                errors.append(f"{w}: audit の new_sources で論点が決まるなら、論点のままにせず裁定にする（resolves は false）: p.{ns.get('page')}")
            if not any(str(src['page']) == str(ns.get('page')) or str(ns.get('page')) in str(src['page']).split('・')
                       for src in x.get('sources', [])):
                errors.append(f"{w}: audit の new_sources のページ p.{ns.get('page')} が sources にない")

    # ---- エンジンの裁定 id との対応（取り込み, 文書, id で区別する）
    uses = engine_uses(ctx)
    sets = {}  # (取り込み, 文書) → その文書の id の集合
    versions = Counter(imp.get('engine_version') for imp in r['engine_imports'])
    for v, n in versions.items():
        if n > 1:
            errors.append(f'engine_imports: 版 {v} の取り込みが {n} つある（版ごとに 1 つ）')
    for imp in r['engine_imports']:
        w = imp['id']
        for key in ('commit', 'parent_version_commit', 'kyuura_commit_used_by_engine'):
            if not COMMIT.match(imp.get(key) or ''):
                errors.append(f'{w}: {key} が 40 桁のコミットでない')
        prefixes = Counter((rs['document'], rs['prefix']) for rs in imp.get('ruling_sets', []))
        for (doc, pre), n in prefixes.items():
            if n > 1:
                errors.append(f'{w}: 文書 {doc} の接頭辞 {pre} の範囲が 2 つある')
        if len({rs['prefix'] for rs in imp.get('ruling_sets', [])}) != len(imp.get('ruling_sets', [])):
            errors.append(f'{w}: 1 つの取り込みの中で、同じ接頭辞を 2 つの文書に使っている（engine_mapping が区別できない）')
        if imp.get('no_ruling_tables'):
            # 裁定の表のない版（実装の履歴）。読んだ文書と、ルールに関わる記述の注記だけを持つ
            if imp.get('ruling_sets') or imp.get('not_imported'):
                errors.append(f'{w}: no_ruling_tables の取り込みに ruling_sets・not_imported がある')
            if not imp.get('notes'):
                errors.append(f'{w}: no_ruling_tables の取り込みに、裁定の表がないことと読んだ内容の注記（notes）がない')
        elif not imp.get('ruling_sets'):
            errors.append(f'{w}: ruling_sets がない（裁定の表のない版なら no_ruling_tables: true と注記を書く）')
        for rs in imp.get('ruling_sets', []):
            if rs['document'] not in imp['documents']:
                errors.append(f"{w}: ruling_sets の文書 {rs['document']} が documents にない")
            sets.setdefault((w, rs['document']), set()).update(ruling_set_ids(rs))
    for (imp_id, doc, rid), lst in uses.items():
        where = '・'.join(i for _, i, _ in lst)
        imp = imports.get(imp_id)
        if imp is None:
            errors.append(f'{where}: engine_refs の import がない: {imp_id}')
            continue
        # 別の版の裁定を、その版の取り込みがまだないあいだだけ、文書を読んだ取り込みに仮に結べる（v0.13 の取り込みが
        # v0.10・v0.12 の C34・C35・W24 を結んだ形）。その版を取り込んだら、その版の取り込みに移す
        provisional = set()
        for _, rec_id, e in lst:
            if e.get('engine_version') != imp['engine_version']:
                if e.get('engine_version') in versions:
                    errors.append(f"{rec_id}: エンジンの裁定 {rid} の版 {e.get('engine_version')} が、取り込み {imp_id} の版 {imp['engine_version']} と違う"
                                  f"（{e.get('engine_version')} の取り込みに結ぶ）")
                else:
                    provisional.add(rec_id)
        if doc not in imp['documents']:
            errors.append(f'{where}: エンジンの裁定 {rid} の文書 {doc} が、取り込み {imp_id} の documents にない')
        elif provisional and len(provisional) == len(lst):
            pass  # まだ取り込んでいない版の裁定なので、この取り込みの範囲（ruling_sets）には入らない
        elif rid not in sets.get((imp_id, doc), set()):
            errors.append(f'{where}: エンジンの裁定 {rid} が、取り込み {imp_id} の文書 {doc} の範囲（ruling_sets）にない（id か文書の誤り）')
        if len(lst) > 1 and any(not e.get('part') for _, _, e in lst):
            errors.append(f"エンジンの裁定 {rid}（{doc}）が {where} に対応している。分けるなら、どれにも part（どの部分か）を書く")
        issue_ids = {i for k, i, _ in lst if k == 'issue'}
        if len(issue_ids) > 1:
            errors.append(f"エンジンの裁定 {rid}（{doc}）が 2 つ以上の未解決の論点（{'・'.join(sorted(issue_ids))}）にある（未解決の論点の重複）")
        for kind, rec_id, e in lst:
            if kind in ('ruling', 'clause') and engine_cls_is_pure(e.get('engine_classification'), '実装上の仮定'):
                errors.append(f'{rec_id}: エンジンが実装上の仮定とした裁定 {rid} を、公式の裁定・条項に対応させている（not_imported に理由を書く）')
    for imp in r['engine_imports']:
        w = imp['id']
        skipped = Counter((n.get('document'), n['ruling_id']) for n in imp.get('not_imported', []))
        for (doc, rid), n in skipped.items():
            if n > 1:
                errors.append(f'{w}: not_imported に {rid}（{doc}）が 2 つある')
            if (w, doc, rid) in uses:
                errors.append(f"{w}: エンジンの裁定 {rid}（{doc}）が not_imported にも記録（{'・'.join(i for _, i, _ in uses[(w, doc, rid)])}）にもある")
            if doc not in imp['documents'] or rid not in sets.get((w, doc), set()):
                errors.append(f'{w}: not_imported の {rid}（{doc}）が、取り込みの範囲（ruling_sets）にない')
        for rs in imp.get('ruling_sets', []):
            for rid in ruling_set_ids(rs):
                if (w, rs['document'], rid) not in uses and (rs['document'], rid) not in skipped:
                    errors.append(f"{w}: エンジンの裁定 {rid} が、どの記録にも not_imported にもない（{rs['document']}）")
        classified = version_key(imp['engine_version']) >= version_key(CLASSIFIED_FROM)
        for n in imp.get('not_imported', []):
            nid = n.get('ruling_id')
            if not n.get('reason'):
                errors.append(f"{w}: not_imported の {nid} に理由がない")
            if n.get('status') not in NOT_IMPORTED_STATUS:
                errors.append(f"{w}: not_imported の {nid} の status の値が不正: {n.get('status')}（{'・'.join(NOT_IMPORTED_STATUS)}）")
                continue
            if not classified:
                if n['status'] not in ('excluded', 'deferred', 'needs_recheck'):
                    errors.append(f"{w}: not_imported の {nid} の status {n['status']} は、{CLASSIFIED_FROM} からの取り込みだけで使う")
                elif n['status'] == 'excluded' and not any(w_ in (n.get('engine_classification') or '') for w_ in ('実装上の仮定', '実装上の扱い', '実装の設計', '実装上の判断')):
                    errors.append(f"{w}: not_imported の {nid} を対象外（excluded）にしているが、エンジンの分類が実装の判断でない（保留 deferred か要再確認 needs_recheck）")
                continue
            cls = n.get('classification')
            if cls not in NOT_IMPORTED_CLASSIFICATIONS:
                errors.append(f"{w}: not_imported の {nid} の classification の値が不正: {cls}（{'・'.join(NOT_IMPORTED_CLASSIFICATIONS)}）")
            elif cls not in CLASSIFICATION_STATUSES[n['status']]:
                errors.append(f"{w}: not_imported の {nid} の status {n['status']} と classification {cls} が合わない")
            for ref in n.get('kyuura_records', []):
                if ref not in all_record_ids:
                    errors.append(f"{w}: not_imported の {nid} の kyuura_records の記録がない: {ref}")
            if n['status'] == 'existing_record' and not n.get('kyuura_records'):
                errors.append(f"{w}: not_imported の {nid} は既存の記録の当てはめ（existing_record）なのに kyuura_records がない")
            if n['status'] == 'adopted_spec' and n.get('engine_position') not in positions:
                errors.append(f"{w}: not_imported の {nid} の engine_position の記録がない: {n.get('engine_position')}")
            if cls == 'unresolved_rules_question' and n['status'] == 'existing_record' and not any(ref in issues for ref in n.get('kyuura_records', [])):
                errors.append(f"{w}: not_imported の {nid} は未解決の問いの当てはめなのに、kyuura_records に未解決の論点がない")
        mine = {k: v for k, v in uses.items() if k[0] == w}
        imported = sorted({i for lst in mine.values() for k, i, _ in lst if k != 'issue'})
        unresolved = sorted({i for lst in mine.values() for k, i, _ in lst if k == 'issue'})
        if 'imported_rulings' in imp and sorted(imp['imported_rulings']) != imported:
            errors.append(f"{w}: imported_rulings が対応から求めたものと違う（足りない: {'・'.join(sorted(set(imported) - set(imp['imported_rulings']))) or 'なし'}。"
                          f"余分: {'・'.join(sorted(set(imp['imported_rulings']) - set(imported))) or 'なし'}）")
        if 'unresolved_rulings' in imp and sorted(imp['unresolved_rulings']) != unresolved:
            errors.append(f"{w}: unresolved_rulings が対応から求めたものと違う（求めたもの: {'・'.join(unresolved) or 'なし'}）")
    # ---- エンジンの採用した仕様・簡略化・実装の事項（裁定・論点と分ける）
    for x in r.get('engine_positions', []):
        w = x['id']
        if x.get('kind') not in ENGINE_POSITION_KINDS:
            errors.append(f"{w}: kind の値が不正: {x.get('kind')}（{'・'.join(ENGINE_POSITION_KINDS)}）")
        imp = imports.get(x.get('engine_import'))
        if imp is None:
            errors.append(f"{w}: engine_import の取り込みがない: {x.get('engine_import')}")
        elif x.get('document') not in imp['documents']:
            errors.append(f"{w}: document {x.get('document')} が取り込み {imp['id']} の documents にない")
        for c in x.get('cards', []):
            check_target(errors, w, cards, c['card_id'], c['target'])
        for ref in x.get('kyuura_records', []):
            if ref not in all_record_ids:
                errors.append(f'{w}: kyuura_records の記録がない: {ref}')
        for k in ('summary', 'kyuura_handling'):
            if not x.get(k):
                errors.append(f'{w}: {k} がない')
        if 'status' in x or 'conclusion' in x:
            errors.append(f'{w}: エンジンの採用・簡略化・実装の事項に、裁定の status・conclusion を書かない（公式の裁定ではない）')
        if imp is not None:
            skipped = {n['ruling_id']: n for n in imp.get('not_imported', []) if n.get('document') == x.get('document')}
            for rid in x.get('engine_rulings', []):
                n = skipped.get(rid)
                if not n or n.get('status') != 'adopted_spec' or n.get('engine_position') != w:
                    errors.append(f'{w}: エンジンの裁定 {rid} が、取り込み {imp["id"]} の not_imported に adopted_spec（engine_position: {w}）としてない')
    idx = r.get('engine_unresolved_index', [])
    keys = Counter(u['engine_key'] for u in idx)
    for k, n in keys.items():
        if n > 1:
            errors.append(f'engine_unresolved_index: 重複: {k}')
    def vkey(v):
        return tuple(int(x) for x in re.findall(r'\d+', v))
    for imp in r['engine_imports']:
        if 'engine_unresolved_total' not in imp:
            continue
        # その版までの項目のうち、エンジンが数えているもの（in_engine_count が false でないもの）。エンジンの数え方の件数と同じか
        n = sum(1 for u in idx if vkey(u['engine_version']) <= vkey(imp['engine_version']) and u.get('in_engine_count', True)
                and vkey(u.get('counted_from_version') or u['engine_version']) <= vkey(imp['engine_version']))
        if n != imp['engine_unresolved_total']:
            errors.append(f"engine_unresolved_index: {imp['engine_version']} までの項目（エンジンが数えるもの）が {n} 件で、"
                          f"{imp['id']} の engine_unresolved_total の {imp['engine_unresolved_total']} と違う")
    imported_versions = {imp['engine_version'] for imp in r['engine_imports']}
    indexed_issues = set()
    for u in idx:
        k = u['engine_key']
        disp = u.get('disposition')
        if disp not in DISPOSITIONS:
            errors.append(f'engine_unresolved_index: {k} の disposition の値が不正: {disp}')
        if disp == 'not_yet_imported' and u.get('engine_version') in imported_versions:
            errors.append(f"engine_unresolved_index: {k} は取り込んだ版 {u['engine_version']} のものなので、not_yet_imported にしない")
        if disp == 'issue':
            if not u.get('kyuura_issue'):
                errors.append(f'engine_unresolved_index: {k} は disposition が issue なのに kyuura_issue がない')
        elif u.get('kyuura_issue') and disp != 'not_yet_imported':
            errors.append(f'engine_unresolved_index: {k} は disposition が {disp} なのに kyuura_issue がある')
        if disp != 'issue' and not u.get('reason'):
            errors.append(f'engine_unresolved_index: {k} を論点にしない理由（reason）がない')
        for f in ('stop_code_since', 'counted_from_version'):
            if u.get(f) and (u[f] not in imported_versions or vkey(u[f]) < vkey(u['engine_version'])):
                errors.append(f"engine_unresolved_index: {k} の {f}（{u[f]}）が、取り込んだ版でないか、項目の版より前")
        if u.get('stop_code_since') and not u.get('stop_code'):
            errors.append(f'engine_unresolved_index: {k} に stop_code_since があるのに停止コードがない')
        if disp == 'out_of_scope' and u.get('engine_version') in imported_versions:
            errors.append(f"engine_unresolved_index: {k} は取り込んだ版 {u['engine_version']} のものなので、out_of_scope にしない")
        for inst in u.get('instances', []):
            # 同じ問いの、あとの版の事例。その版の取り込みがあり、同じ論点に結ばれている
            if inst['engine_version'] not in imported_versions:
                errors.append(f"engine_unresolved_index: {k} の事例 {inst['ruling_id']} の版 {inst['engine_version']} の取り込みがない")
            elif u.get('kyuura_issue') in issues and not any(
                    e['ruling_id'] == inst['ruling_id'] and e['engine_version'] == inst['engine_version']
                    for e in issues[u['kyuura_issue']].get('engine_refs', [])):
                errors.append(f"engine_unresolved_index: {k} の事例 {inst['ruling_id']}（{inst['engine_version']}）が、論点 {u['kyuura_issue']} の engine_refs にない")
            elif disp != 'issue':
                errors.append(f'engine_unresolved_index: {k} は論点に取り込んでいないのに、事例（instances）がある')
        if u.get('kyuura_issue'):
            if u['kyuura_issue'] not in issues:
                errors.append(f"engine_unresolved_index: {k} の論点がない: {u['kyuura_issue']}")
            else:
                refs = {e['ruling_id'] for e in issues[u['kyuura_issue']].get('engine_refs', [])}
                ids = [i for i in k.split('/') if re.fullmatch(r'[A-Z]{1,3}\d+[a-z]?', i)]
                missing = [i for i in ids if i not in refs]
                if missing:
                    errors.append(f"engine_unresolved_index: {k} の論点 {u['kyuura_issue']} の engine_refs に {'・'.join(missing)} がない")
            indexed_issues.add(u['kyuura_issue'])
    for i in issues:
        if i not in indexed_issues and not issues[i].get('not_in_engine_index'):
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


def version_key(v):
    """'v0.17'・'v0.2b' などの版を比べるためのキー（数字の並び）。"""
    return tuple(int(x) for x in re.findall(r'\d+', v))


def unresolved_counts(ctx, as_of=None):
    """未解決の数を、kyuura の調査の論点とエンジンの数え方に分けて求める（同じ数として扱わない）。

    as_of（'v0.25' など）を渡すと、その版の時点の数にする: その版までの一覧の項目、その版で数えていた項目（counted_from_version）、
    その版で付いていた停止コード（stop_code_since）、その版までのエンジンの裁定に結んだ論点、その版までの事例（instances）。
    engine_refs のない論点（kyuura の調査で立てた論点）は recorded_after の取り込みのあとに記録したので、as_of がその取り込みの版より
    あとのとき（as_of を渡さない今の数を含む）だけ数える。過去の取り込みの検査が、あとの版の取り込みで変わらずに確かめられるようにする。

    - research_issues: kyuura の未解決の論点（issues）の数
    - engine_total: 最新の版でエンジンが数える未解決の裁定の数（engine_unresolved_index で in_engine_count が false でないもの）
    - engine_stop_codes: そのうち停止コードのあるもの
    - by_import: 取り込みごとの engine_unresolved_total（その版までの数）
    - v013_items・v017_additions・not_in_engine_count・out_of_scope: 一覧の項目の内訳（engine_key）
    - instances: 既存の項目の、あとの版の事例（新しい項目にしない）
    - issues_without_stop_code: 結んだ一覧の項目に停止コードがない論点（一覧にない論点も含む）
    - issues_not_in_index: エンジンの一覧の項目と結んでいない論点
    """
    r = ctx['rulings']
    latest = as_of or max((imp['engine_version'] for imp in r['engine_imports']), key=version_key)
    lk = version_key(latest)
    within = lambda v: version_key(v) <= lk
    idx = []
    for u in r['engine_unresolved_index']:
        if not within(u['engine_version']):
            continue
        u = dict(u, instances=[i for i in u.get('instances', []) if within(i['engine_version'])])
        if u.get('stop_code_since') and not within(u['stop_code_since']):
            u['stop_code'] = None
        if u.get('counted_from_version') and not within(u['counted_from_version']):
            u['in_engine_count'] = False
        idx.append(u)
    counted = [u for u in idx if u.get('in_engine_count', True)]
    imports = {imp['id']: imp for imp in r['engine_imports']}

    def counted_issue(x):
        if x.get('engine_refs'):
            return any(within(e['engine_version']) for e in x['engine_refs'])
        # kyuura の調査で立てた論点: 記録した時点の最新の取り込みより後の時点（今の数を含む）だけ数える
        rec = imports[x['recorded_after']['import']]
        return as_of is None or version_key(as_of) > version_key(rec['engine_version'])

    issues = [x for x in r['issues'] if counted_issue(x)]
    by_issue = defaultdict(list)
    for u in idx:
        if u.get('kyuura_issue'):
            by_issue[u['kyuura_issue']].append(u)
    return {
        'research_issues': len(issues),
        'latest_version': latest,
        'engine_total': len(counted),
        'engine_stop_codes': sum(1 for u in counted if u.get('stop_code')),
        'by_import': [(imp['engine_version'], imp['engine_unresolved_total']) for imp in r['engine_imports']
                      if 'engine_unresolved_total' in imp and within(imp['engine_version'])],
        'v013_items': [u['engine_key'] for u in counted if version_key(u['engine_version']) <= version_key('v0.13')],
        'v017_additions': [u['engine_key'] for u in counted if u['engine_version'] == 'v0.17' and not u.get('counted_from_version')],
        'v026_v068_additions': [u['engine_key'] for u in counted if version_key('v0.26') <= version_key(u['engine_version']) <= version_key('v0.68')],
        'counted_later': [(u['engine_key'], u['counted_from_version']) for u in counted if u.get('counted_from_version')],
        'not_in_engine_count': [u['engine_key'] for u in idx if not u.get('in_engine_count', True)],
        'out_of_scope': [u['engine_key'] for u in idx if u.get('disposition') == 'out_of_scope'],
        'instances': [(u['engine_key'], i['engine_version'], i['ruling_id']) for u in idx for i in u.get('instances', [])],
        'issues_without_stop_code': [x['id'] for x in issues if not any(u.get('stop_code') for u in by_issue.get(x['id'], []))],
        'issues_not_in_index': [x['id'] for x in issues if x['id'] not in by_issue],
        'stop_codes_by_issue': {x['id']: sorted({u['stop_code'] for u in by_issue.get(x['id'], []) if u.get('stop_code')}) for x in issues},
        'game_effect': Counter(x.get('audit', {}).get('game_effect') for x in issues),
    }


def kyuura_status_by_engine_id(ctx):
    """取り込みごとに、エンジンの裁定 id を kyuura の分類で数える（{版: Counter}）。

    分類: CONFIRMED・SUPPORTED（その id に対応する裁定がそれだけ。条項・照合が加わってもよい）・CONFIRMED+SUPPORTED（部分ごとに違う）・
    UNRESOLVED（未解決の論点に対応する部分がある）・clause_or_check（条項・照合だけ）・not_imported:<status>。
    """
    r = ctx['rulings']
    uses = engine_uses(ctx)
    status = {x['id']: x['status'] for x in r['rulings']}
    out = {}
    for imp in r['engine_imports']:
        tally = Counter()
        ni = {(x['document'], x['ruling_id']): x['status'] for x in imp.get('not_imported', [])}
        for rs in imp.get('ruling_sets', []):
            for rid in ruling_set_ids(rs):
                lst = uses.get((imp['id'], rs['document'], rid), [])
                if not lst:
                    tally['not_imported:' + ni.get((rs['document'], rid), '?')] += 1
                    continue
                kinds = {status[xid] if kind == 'ruling' else 'UNRESOLVED' if kind == 'issue' else 'clause_or_check' for kind, xid, _ in lst}
                if 'UNRESOLVED' in kinds:
                    tally['UNRESOLVED'] += 1
                elif {'CONFIRMED', 'SUPPORTED'} <= kinds:
                    tally['CONFIRMED+SUPPORTED'] += 1
                else:
                    tally[next((k for k in ('CONFIRMED', 'SUPPORTED') if k in kinds), 'clause_or_check')] += 1
        out[imp['engine_version']] = tally
    return out


def engine_mapping(ctx, import_id, document=None):
    """エンジンの裁定 id → [（記録の種類, 記録の id, engine_refs の項目）]。

    1 つの取り込みの中では接頭辞が文書ごとに違う（検査する）ので、id だけで引ける。document を渡すと、その文書の id だけ。
    版が違えば同じ id（S1 など）が別の裁定なので、取り込み（import_id）を必ず指定する。
    """
    out = defaultdict(list)
    for (imp, doc, rid), lst in engine_uses(ctx).items():
        if imp == import_id and (document is None or doc == document):
            out[rid].extend(lst)
    return out


def find_engine_ruling(ctx, engine_version, ruling_id, document=None):
    """エンジンの版と裁定 id（と文書）から、kyuura の記録・not_imported を引く。

    戻り値: [（取り込み, 文書, 記録の種類, 記録の id または None, 部分・理由）]
    """
    out = []
    for imp in ctx['rulings']['engine_imports']:
        if imp['engine_version'] != engine_version:
            continue
        for rs in imp.get('ruling_sets', []):
            doc = rs['document']
            if (document and doc != document) or ruling_id not in ruling_set_ids(rs):
                continue
            for kind, rec_id, e in engine_uses(ctx).get((imp['id'], doc, ruling_id), []):
                out.append((imp['id'], doc, kind, rec_id, e.get('part') or ''))
            for n in imp.get('not_imported', []):
                if n['ruling_id'] == ruling_id and n.get('document') == doc:
                    out.append((imp['id'], doc, 'not_imported', None, n['reason']))
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
    issues_by_id = {x['id']: x for x in r['issues']}
    clauses_by_id = {x['id']: x for x in r['rule_clauses']}
    checks_by_id = {x['id']: x for x in C['records']}
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
            '- **エンジンとの対応**: kyuura-engine（対戦処理の実装）の裁定 id との対応は、調査の履歴を追うための参照です。エンジンの実装・停止コード・例外は、公式の裁定として扱いません。',
            '- **原典を確かめた人**: kyuura が原典の画像を読んだ記録と、kyuura-engine の照合の記録を取り込んだ記録（【kyuura-engine の照合の記録の取り込み…】と書く）を区別します。'
            '取り込んだ記録の照合した欄はエンジンの記録の範囲だけで、原典の確認日（エンジンの記録の日付）と取り込んだ日を分けて書きます（`import_provenance`。再利用の手順は [エンジン開発の準備状況](../engine-readiness.md) の 10 章）。', '']

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
        if provenance_text(x):
            extra.append(provenance_text(x))
        out.append(f"- {x['id']}: " + ' '.join(md(e) for e in extra))
    out.append('')

    # 2. 照合
    out += ['## 2. カードの記録の照合', '',
            '照合の記録のないカードは未照合です（「照合して差異なし」とは別）。照合した欄の値は記録に写してあり、`data/cards.json` が変わると検査がエラーにします。', '',
            '| id | カード | 資料・ページ | 照合した欄 | 結果 | データの誤り | 見たこと |', '|---|---|---|---|---|---|---|']
    for x in C['records']:
        de = 'なし'
        if x['data_error']:
            de = 'あり（修正の候補）: ' + '、'.join(f"{e['field']} 「{e['kyuura_value']}」→ 資料「{e['source_value']}」" for e in x['data_error'])
        elif x.get('corrections'):
            de = 'なし（照合のあとで直した: ' + '、'.join(c['field'] for c in x['corrections']) + '）'
        if x.get('data_gaps'):
            de += '。値の欠け（調査課題）: ' + '、'.join(g['field'] for g in x['data_gaps'])
        out.append(f"| {x['id']} | {md(card_label(cards, x['card_id']))} | [{x['source']}] p.{x['page']}（{md(x['location'])}） | "
                   f"{md('、'.join(x['checked_fields']))} | {md(C['results'][x['result']])} | {md(de)} | "
                   f"{md(' '.join(([provenance_text(x)] if provenance_text(x) else []) + x['findings']))} |")
    out.append('')
    errs = [x for x in C['records'] if x['data_error']]
    if errs:
        out += ['データの誤りの候補（この記録では `data/cards.json` を直していない。修正は別の作業）:', '']
        for x in errs:
            for e in x['data_error']:
                out.append(f"- {x['id']}（{md(card_label(cards, x['card_id']))}）: `{e['field']}` は「{md(e['kyuura_value'])}」、"
                           f"資料は「{md(e['source_value'])}」（{md(e['evidence'])}）。{md(e.get('note', ''))}")
        out.append('')
    corrs = [x for x in C['records'] if x.get('corrections')]
    if corrs:
        out += ['照合のあとで直したデータ（`data/cards.json` の今の値と、照合した欄の写しは、直したあとの値）:', '']
        for x in corrs:
            for c in x['corrections']:
                out.append(f"- {x['id']}（{md(card_label(cards, x['card_id']))}）: `{c['field']}` を「{md(c['before'])}」から「{md(c['after'])}」に直した"
                           f"（{md(c['evidence'])}。{md(c['method'])}。コミット {c['commit'][:7]}）。{md(c.get('note', ''))}")
        out.append('')
    gaps = [x for x in C['records'] if x.get('data_gaps')]
    if gaps:
        out += ['値が欠けている欄（調査課題。値を入れていない。照合した欄には含めない）:', '']
        for x in gaps:
            for g in x['data_gaps']:
                out.append(f"- {x['id']}（{md(card_label(cards, x['card_id']))}）: `{g['field']}` は空。資料は「{md(g['source_value'])}」（{md(g['evidence'])}）。"
                           f"空の原因: {md(g['cause'])}。扱い: {md(C['gap_statuses'][g['status']])}。{md(g.get('note', ''))}")
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
    out.append('同じ問いを複数のカードにまとめた裁定（エンジンの複数の版の裁定を 1 つにしたもの）は「複数のカードに共通」の見出しにあります。')
    out.append('')
    groups = defaultdict(list)
    for x in r['rulings']:
        if len({c['card_id'] for c in x['cards']}) > 1:
            groups[('', '複数のカードに共通')].append(x)
        else:
            c = x['cards'][0]
            groups[(c['card_id'], target_label(c['target']))].append(x)
    for (cid, tl), lst in groups.items():
        out += [f'### {card_label(cards, cid)}・{tl}' if cid else f'### {tl}', '']
        topics = defaultdict(list)
        for x in lst:
            topics[x['topic']].append(x)
        for topic, xs in topics.items():
            out += [f'#### {topic}', '']
            for x in xs:
                out.append(f"- **{x['id']}**（{STATUS_JA[x['status']]}）{md(x['question'])} → **{md(x['conclusion'])}**")
                if len(x['cards']) > 1:
                    out.append('  - 対象: ' + '・'.join(md(f"{card_label(cards, c['card_id'])}の{target_label(c['target'])}") for c in x['cards']))
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
    uc = unresolved_counts(ctx)
    out += ['## 5. 未解決の論点', '',
            '公式の資料で決められない論点です。同じ問いのエンジンの裁定はまとめて 1 つの論点にし、事例（cases）として結びます。', '']
    for x in r['issues']:
        out += [f"### {x['id']}", '',
                f"- 論点: {md(x['question'])}",
                f"- 決められない理由: {md(x['why_unresolved'])}",
                f"- 公式の資料: {OFFICIAL_MATERIAL[x['official_material']]}（" + '、'.join(f"[{s['source']}] p.{s['page']} {s['location']}" for s in x['sources']) + '）',
                f"- 参照する条項: {'・'.join(x['rule_clause_refs'])}"]
        for c in x['cases']:
            eng = f"エンジンの {c['engine_ruling']}" if c.get('engine_ruling') else 'エンジンの裁定はない'
            out.append(f"- 事例: {card_label(cards, c['card_id'])}・{target_label(c['target'])}（{eng}）: {md(c['note'])}")
        if x.get('reachability'):
            out.append(f"- 起こるか: エンジンの対応カード — {md(x['reachability']['engine_card_pool'])}。旧裏期の全カード — {md(x['reachability']['all_cards'])}")
        for e in x.get('related_engine_rulings', []):
            out.append(f"- 関係するエンジンの裁定: {e['ruling_id']}（{e['engine_version']}・{e['document']}）: {md(e['relation'])}")
        if x.get('related_issues'):
            out.append(f"- 関係する論点: {'・'.join(x['related_issues'])}")
        for e in x['engine_refs']:
            out.append(f'- エンジン: {md(engine_line(e))}')
        if x.get('recorded_after'):
            ra = x['recorded_after']
            out.append(f"- kyuura の調査で立てた論点（{ra['date']}。取り込み {ra['import']} のあと）。エンジンの裁定に結んでいないので、"
                       'エンジンの未解決の裁定の一覧（8 章）には入っていない')
        elif x.get('not_in_engine_index'):
            out.append('- エンジンの未解決の裁定の一覧（8 章）には入っていない（エンジンは処理を決めている）')
        for n in x.get('notes', []):
            out.append(f'- 注: {md(n)}')
        a = x['audit']
        codes = uc['stop_codes_by_issue'][x['id']]
        out += [f"- 監査（{a['audited_on']}）:",
                f"  - 結果への影響: {md(r['game_effect_values'][a['game_effect']].split('（')[0])}。{md(a['game_effect_note'])}",
                f"  - 解決に要る資料: {md(a['resolution_needs'])}",
                f"  - 調べた範囲: {md(a['searched'])}",
                '  - この監査で新しく読んだ資料: ' + ('、'.join(f"[{n['source']}] p.{n['page']}（{md(n['what'])}）" for n in a['new_sources']) or 'なし'),
                '  - エンジンの停止: ' + ('、'.join(f'`{c}`' for c in codes) + '（8 章。停止コードは公式の裁定ではない）' if codes else 'なし（停止コードのない問い、またはエンジンの一覧にない）')]
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
    clause_ids = {x['id'] for x in r['rule_clauses']}
    out += ['## 7. kyuura-engine の裁定との対応', '',
            'エンジンの版ごとの取り込みです。エンジンの裁定の id は文書ごとの番号で、版が違えば同じ id（S1・G1・P1 など）が別の裁定です。'
            '対応は（取り込み, 文書, id）で区別しています。', '',
            '| 取り込み | 版 | コミット | 文書（裁定の表） | エンジンの裁定 | 記録に結んだ | 取り込んでいない | kyuura の記録 | 未解決の論点 |',
            '|---|---|---|---|---|---|---|---|---|']
    for imp in r['engine_imports']:
        ids = [(rs['document'], rid) for rs in imp.get('ruling_sets', []) for rid in ruling_set_ids(rs)]
        skipped = {(n.get('document'), n['ruling_id']) for n in imp.get('not_imported', [])}
        docs = list(dict.fromkeys(rs['document'] for rs in imp.get('ruling_sets', [])))
        if imp.get('no_ruling_tables'):
            docs = ['裁定の表なし（実装の履歴）']
        out.append(f"| {imp['id']} | {imp['engine_version']} | `{imp['commit'][:7]}` | {md('、'.join(docs))} | "
                   f"{len(ids)} | {len(ids) - len(skipped)} | {len(skipped)} | {len(imp.get('imported_rulings', []))} | {len(imp.get('unresolved_rulings', []))} |")
    out.append('')
    for imp in r['engine_imports']:
        out += [f"### {imp['id']}（{imp['engine_version']}）", '',
                '| 項目 | 内容 |', '|---|---|',
                f"| リポジトリ・ブランチ | {imp['repository']}（{imp['branch']}） |",
                f"| コミット | `{imp['commit']}`（{imp['engine_version']}。前の版 `{imp['parent_version_commit'][:7]}`） |"]
        if imp.get('documents_read_at'):
            out.append(f"| 文書を読んだコミット | `{imp['documents_read_at'][:7]}` |")
        out += [f"| エンジンが参照した kyuura のコミット | `{imp['kyuura_commit_used_by_engine']}` |",
                f"| 取り込んだ日 | {imp['imported_on']} |",
                f"| 読んだ文書 | {md('、'.join(imp['documents']))} |", '']
        out += [f'- {md(n)}' for n in imp.get('notes', [])]
        out.append('')
        for rs in imp.get('ruling_sets', []):
            mapping = engine_mapping(ctx, imp['id'], rs['document'])
            ids = ruling_set_ids(rs)
            skipped = {n['ruling_id']: n for n in imp.get('not_imported', []) if n.get('document') == rs['document']}
            reported = ('エンジンが報告した分類: ' + '・'.join(f'{k} {v}' for k, v in rs['engine_reported_counts'].items()) + '。'
                        if rs.get('engine_reported_counts') else '')
            extra = f"（ほかに {'・'.join(rs['extra_ids'])}）" if rs.get('extra_ids') else ''
            span = f"{rs['prefix']}{rs['first']}〜{rs['prefix']}{rs['last']}" if rs['last'] >= rs['first'] else ''
            out += [f"エンジンの裁定 {span}{extra if span else '・'.join(rs.get('extra_ids', []))}（{rs['document']}）。{reported}", '',
                    '| エンジンの id | エンジンの分類 | 取り込み | kyuura の記録 | kyuura の分類 | 根拠のページ（確認方法は各記録を参照） | 部分・備考・分類を変えた理由 |',
                    '|---|---|---|---|---|---|---|']
            tally = Counter()
            for rid in ids:
                lst = mapping.get(rid, [])
                if not lst:
                    n = skipped.get(rid, {})
                    cls = NOT_IMPORTED_CLASSIFICATIONS.get(n.get('classification'), '').split('（')[0]
                    recs = '・'.join(n.get('kyuura_records', [])) or '—'
                    out.append(f"| {rid} | {md(n.get('engine_classification', '—'))} | {NOT_IMPORTED_STATUS.get(n.get('status'), '—')} | {md(recs)} | "
                               f"{md(cls) or '—'} | — | {md(n.get('reason', ''))} |")
                    tally['取り込んでいない'] += 1
                    continue
                kinds = {k for k, _, _ in lst}
                tally['未解決の論点に結んだ' if kinds == {'issue'} else 'カードの照合に結んだ' if kinds == {'check'} else
                      '一般の規定（条項）に結んだ' if kinds == {'clause'} else
                      '分けて記録' if len(lst) > 1 else '裁定として記録'] += 1
                for kind, rec_id, e in lst:
                    if kind == 'ruling':
                        st = STATUS_JA[rul[rec_id]['status']]
                    elif kind == 'issue':
                        st = STATUS_JA['UNRESOLVED']
                    elif kind == 'clause':
                        st = '一般の規定（条項）'
                    else:
                        st = 'カードの照合'
                    note = '・'.join(s for s in (e.get('part'), e.get('engine_note')) if s)
                    rec = {'ruling': rul, 'issue': issues_by_id, 'clause': clauses_by_id, 'check': checks_by_id}[kind][rec_id]
                    if kind == 'ruling' and rec.get('reclassification') and (
                            engine_cls_is_pure(e.get('engine_classification'), 'CONFIRMED') != (rec['status'] == 'CONFIRMED')):
                        note = '・'.join(x for x in (note, f"分類を変えた理由: {rec['reclassification']['reason']}") if x)
                    out.append(f"| {rid} | {md(e.get('engine_classification', ''))} | 取り込み済み | {rec_id} | {st} | {md(basis_pages(rec))} | {md(note)} |")
            out += ['', '集計: ' + '、'.join(f'{k} {v}' for k, v in tally.items()) + '。', '']
            st_counts = Counter()
            for rid in ids:
                for kind, rec_id, _ in mapping.get(rid, []):
                    st_counts[({'ruling': None, 'issue': 'UNRESOLVED', 'check': 'カードの照合', 'clause': '一般の規定（条項）'}[kind]
                               or rul[rec_id]['status'], rec_id)] += 1
            by_status = Counter(s for s, _ in st_counts)
            out += ['対応する kyuura の記録（重複を除く）: ' + '、'.join(f'{k} {v}' for k, v in sorted(by_status.items())) + '。', '']

    # 8. エンジンの未解決の一覧
    idx = r.get('engine_unresolved_index', [])
    out += ['## 8. エンジンの未解決の裁定と kyuura の論点', '',
            f'kyuura-engine が「原典で決められない」として止めている、または決めていない裁定の一覧です（{len(idx)} 件。停止コードはエンジンの仕組みで、公式の裁定ではありません）。'
            '扱い（disposition）は、kyuura の論点に取り込んだもの・歴史上の論点ではない（実装だけの問題）もの・取り込みの範囲の外のものに分け、取り込んでいないものには理由を書いています。', '',
            '| エンジンの id | 版 | 文書 | 停止コード | 内容 | 扱い | kyuura の論点・理由 |', '|---|---|---|---|---|---|---|']
    for u in idx:
        how = u.get('kyuura_issue') or u.get('reason', '')
        out.append(f"| {u['engine_key']} | {u['engine_version']} | {u['document']} | {('`' + u['stop_code'] + '`') if u.get('stop_code') else '—'} | "
                   f"{md(u['summary'])} | {DISPOSITION_SHORT.get(u.get('disposition'), u.get('disposition'))} | {md(how)} |")
    out.append('')
    tally = Counter(u.get('disposition') for u in idx)
    out += ['扱いの集計: ' + '、'.join(f'{DISPOSITION_SHORT.get(k, k)} {v}' for k, v in tally.items()) + '。', '']
    positions = r.get('engine_positions', [])
    pos_section = ['## 9. エンジンの採用した仕様・簡略化・実装の事項', '',
                   'kyuura-engine が原典で決まらない点を決めて実装した仕様、処理を簡略化した仕様、実装の不具合・制限です。公式の裁定・エラッタ・最新の説明ではなく、'
                   'kyuura の裁定（CR-）・論点（UQ-）とは分けて記録しています（data/sidecar/rulings.json の engine_positions）。', '']
    for x in positions:
        cards_txt = '、'.join(f"{card_label(cards, c['card_id'])}・{target_label(c['target'])}" for c in x['cards'])
        pos_section += [f"### {x['id']}（{ENGINE_POSITION_KINDS[x['kind']].split('（')[0]}）", '',
                        f"- エンジン: {x['engine_import']}・{x['document']} {x.get('section', '')}" + (f"（裁定 {'・'.join(x['engine_rulings'])}）" if x.get('engine_rulings') else ''),
                        f"- カード: {cards_txt}",
                        f"- 内容: {md(x['summary'])}"]
        if x.get('engine_basis'):
            pos_section.append('- エンジンが挙げた根拠: ' + '；'.join(md(b) for b in x['engine_basis']))
        if x.get('kyuura_records'):
            pos_section.append('- kyuura の記録: ' + '・'.join(x['kyuura_records']))
        pos_section += [f"- kyuura での扱い: {md(x['kyuura_handling'])}", '']
    out += ['### 未解決の数の区別', '',
            'kyuura の調査の未解決（論点の数）と、エンジンの数え方（未解決の裁定・停止コード）は別の数です。どれも、ほかの数の代わりにしません。', '',
            f"- kyuura の未解決の論点: {uc['research_issues']} 件（5 章。結果への影響: " +
            '、'.join(f"{r['game_effect_values'][k].split('（')[0]} {v}" for k, v in uc['game_effect'].most_common()) + '）',
            f"- エンジンが数える未解決の裁定（{uc['latest_version']} まで）: {uc['engine_total']} 件。そのうち停止コードのあるもの {uc['engine_stop_codes']} 件。"
            '取り込みごとの数: ' + '、'.join(f'{v} {n} 件' for v, n in uc['by_import']),
            f"  - v0.13 までの項目: {len(uc['v013_items'])} 件（{'・'.join(uc['v013_items'])}）",
            f"  - v0.17 で加わった項目: {len(uc['v017_additions'])} 件（{'・'.join(uc['v017_additions'])}）",
            f"  - v0.26〜v0.68 で加わった項目: {len(uc['v026_v068_additions'])} 件",
            f"  - あとの版から数えるようになった項目: {len(uc['counted_later'])} 件（" + '、'.join(f'{k}（{v} から）' for k, v in uc['counted_later']) + '）',
            f"- エンジンが数に入れていない項目: {len(uc['not_in_engine_count'])} 件（{'・'.join(uc['not_in_engine_count'])}。設計の表の問い・今の対応カードでは起こらないコードのない問い。kyuura では論点にした）",
            f"- 既存の項目の、あとの版の事例（新しい項目にしない）: {len(uc['instances'])} 件（" +
            '、'.join(f'{k} → {v} の {rid}' for k, v, rid in uc['instances']) + '）',
            f"- 取り込みの範囲の外（v0.1〜v0.4b。kyuura では論点にしていない）: {len(uc['out_of_scope'])} 件（{'・'.join(uc['out_of_scope'])}）",
            f"- 停止コードのない論点: {len(uc['issues_without_stop_code'])} 件（{'・'.join(uc['issues_without_stop_code'])}）",
            f"- エンジンの一覧の項目と結んでいない論点: {len(uc['issues_not_in_index'])} 件（{'・'.join(uc['issues_not_in_index'])}）", '']
    out += pos_section
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
