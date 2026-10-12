#!/usr/bin/env python3
"""ルール・レギュレーション・エラッタの履歴（data/rule_history.json）を検査し、次のページを生成する。

  - docs/rules/errata-history.md（カードの文面の変更とエラッタの履歴）
  - docs/rules/japanese-editions.md（日本版のルールの版ごとの比較。jp_editions・jp_edition_matrix から）
  - docs/printed-sources.md（スキャンで確認した印刷物の巻号・ページごとの記録。documents から）

検査すること:
  - id（EV-・MIX-・KGR-・EN-・ERR-・TXT-・RUL-・REG-・NEO-）の重複
  - applies_to.events・cards・card_lists のカード id の参照切れ
    （カード id は data/cards.json の id か、data/ja_text_pcgsearch.json のページ名）
  - 出典の記号（source・cites、本文中の [X52] など）が docs/sources.md にあるか
  - 手書きの docs/rules/mixed-2002.md・kangaskhan-2002.md・japanese.md の中の id が存在するか
  - 日付の矛盾:
    - events の date・other_dates・rejected_dates の書式と、期間（開始 ≦ 終了）
    - 記録の announced ≦ effective_from ≦ effective_until（先頭の日付どうし。精度の粗い方に合わせて比べる）。
      printed_from（新しい文面の印刷の開始）は告知より早いことがあるので、この順の検査には入れない
    - announced_event・printed_event・effective_event を書いた記録は、その出来事の date か other_dates と日付が合うか
    - 印刷テキストの変更・公式エラッタ（printed_text_change・official_errata）で、適用の開始（effective_from・effective_event）に
      印刷の日付を書いていないか（商品の出来事を effective_event にしていないか、日付を書いた effective_from が「印刷」の説明でないか）。
      印刷の開始は printed_from に書く。printed_from の日付と、stages の印刷の変更（printed_change）の日付が合うか
    - applies_to.events の大会（type が tournament）が、記録の適用期間に入っているか
    - events の rejected_dates（資料が挙げるが誤りと判断した日付）が、keywords と同じ文の中で、
      その日付を挙げた資料（claimed_by の記号）や「以前の版」の説明なしに使われていないか
      （data/rule_history.json・data/rule_differences.json・手書きの docs/rules/*.md・docs/sources.md）。
      正当に違う日付（雑誌の発行日と発売日など）は other_dates に書くので、単純な文字列の一致では検出しない
  - documents: 記号が docs/sources.md にあるか、ページの refs の id があるか。スキャン（kind が scan_image で
    source が J37）を根拠にした記録が挙げる当時の資料（cites）が、documents にあるか
  - jp_editions・jp_edition_matrix: 版の出来事の日付、出典の記号、確度・根拠の種類・根拠の性質の値、
    rd_item（data/rule_differences.json の項目）があるか、表のマスの版が jp_editions の版か。
    二次資料だけ・推定だけのマスを「確実」にしていないか。
    比較表のマスと、日米の違いの表（rule_differences）の「第N版」の行とで、確度が食い違っていないか、
    rule_differences の行が、比較表で未確認の版まで含めていないか
  - errata の stages（予告・印刷の変更・公式の告知・適用の段階）: 段階の種類・確度・日付の書式・出典。
    公式エラッタ（official_errata）に分類した記録に、確認できた「公式の告知」の段階があるか
    （変更の予告や再録の文面の変更だけで公式エラッタとしていないか）
  - verification に「原本と照合した」などと書いた記録に、根拠の種類 original があるか
  - カードの日英の違い（data/curation/card_differences.json・other_products.json の differences）で
    エラッタ（kind が errata）とした記録が、公式エラッタ（official_errata）の記録のカードか
  - --check: 生成結果が上の 3 つのページと同じか（ファイルは書き換えない）

使い方: python3 scripts/build_rule_history.py [--check]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_other_products as bop  # noqa: E402  同じカードの判定（Catalog）を使う

DATA = ROOT / 'data' / 'rule_history.json'
OUT = ROOT / 'docs' / 'rules' / 'errata-history.md'
OUT_EDITIONS = ROOT / 'docs' / 'rules' / 'japanese-editions.md'
OUT_DOCUMENTS = ROOT / 'docs' / 'printed-sources.md'
HANDWRITTEN = [ROOT / 'docs' / 'rules' / n for n in ('mixed-2002.md', 'kangaskhan-2002.md', 'japanese.md')]
# rejected_dates を探す文書（手書き。生成物は元データを検査すれば足りる）
PROSE = HANDWRITTEN + [ROOT / 'docs' / 'rules' / n for n in ('wotc.md', 'README.md')] + [ROOT / 'docs' / 'sources.md']
DATE_RE = re.compile(r'^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?')
DATE_FULL_RE = re.compile(r'^\d{4}(?:-\d{2}(?:-\d{2})?)?$')
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
ID_RE = re.compile(r'\b(?:EV|MIX|KGR|EN|ERR|TXT|RUL|REG|NEO)-[A-Z0-9][A-Z0-9-]*[A-Z0-9]\b')
SRC_RE = re.compile(r'\[([A-Z]\d+)\]')
GENERATED = ('<!-- このファイルは scripts/build_rule_history.py が data/rule_history.json から生成しています。'
             '直接編集しないでください。 -->')
REGION_JA = {'JP': '日本版', 'EN': '英語版'}
EVIDENCE_SHORT = {'original': '原本', 'archived_official': '公式ページの保存版（原文を確認）', 'scan_image': '印刷物のスキャン・写真（文面を確認）', 'card_image': 'カードの画像',
                  'official_later': '後年の公式資料', 'secondary_direct': '二次資料（本文を確認）', 'search_summary': '検索結果の要約のみ'}


MATRIX_TYPE_SHORT = {'edition_document': '版の文書', 'contemporary_official': '同時期の公式資料', 'later_official': '後の公式資料の「前のルール」',
                     'secondary': '二次資料', 'inferred': '推定'}
ORIGINAL_CLAIM_RE = re.compile(r'原本(?:と|で|を)(?:照合|確認)(?:した|済)')
EDITION_RE = re.compile(r'^第(\d)版')
BASIS_SHORT = {'original': '原本', 'archived_official': '公式サイトの保存版', 'scan_image': 'スキャン', 'card_image': 'カードの画像',
               'official_later': '後年の公式資料', 'secondary_direct': '二次資料', 'search_summary': '検索結果の要約'}


def md(s):
    return str(s or '').replace('|', '\\|').replace('\n', '<br>')


def source_codes():
    text = (ROOT / 'docs' / 'sources.md').read_text(encoding='utf-8')
    return set(re.findall(r'^\| ([A-Z]\d+) \|', text, re.M))


class Cards:
    """カード id から名前と、同じカードのほかの版を引く。"""

    def __init__(self):
        self.cat = bop.Catalog()
        self.records = {r['id']: r for r in self.cat.records}
        self.pages = {}
        for key, cards in self.cat.data.items():
            for c in cards:
                self.pages[bop.page_id(c)] = (key, c)

    def exists(self, cid):
        return cid in self.records or cid in self.pages

    def label(self, cid):
        if cid in self.records:
            r = self.records[cid]
            return f"{r['name']['ja'] or r['name']['en']}（{cid}）"
        key, c = self.pages[cid]
        return f"{c['name']}（{self.cat.short_name(key)}、{cid}）"

    def others(self, cid):
        """同じカード（名前・HP・ワザ名が同じ）のほかの版の id。"""
        if cid in self.records:
            members = self.cat.groups.get(bop.sig_record(self.records[cid]), [])
        else:
            members = self.cat.groups.get(bop.sig_pcg(self.pages[cid][1]), [])
        out = []
        for g in members:
            i = g['record']['id'] if 'record' in g else bop.page_id(g['card'])
            if i != cid and i not in out:
                out.append(i)
        return out


def lead_date(s):
    """文字列の先頭の日付（YYYY、YYYY-MM、YYYY-MM-DD）。なければ None。"""
    m = DATE_RE.match(str(s or ''))
    return '-'.join(g for g in m.groups() if g) if m else None


def lead_text(v):
    """一覧の表に出す短い日付。先頭が日付ならその日付、「未確認（…）」などは括弧の前まで。"""
    m = DATE_RE.match(v)
    return m.group(0) if m else v.split('（')[0]


def le(a, b):
    """a ≦ b（精度の粗い方に合わせて比べる）。"""
    n = min(len(a), len(b))
    return a[:n] <= b[:n]


def compatible(a, b):
    return a.startswith(b) or b.startswith(a)


def event_dates(e):
    start, _, end = e['date'].partition('/')
    return start, end or start


def date_patterns(d):
    """rejected_dates の日付を、本文での書き方の正規表現にする（より細かい日付の一部としての一致は除く）。"""
    y, _, rest = d.partition('-')
    if not rest:
        return [re.compile(rf'{y}(?![-\d])'), re.compile(rf'{y}年(?!\d)')]
    m, _, day = rest.partition('-')
    mi = int(m)
    if not day:
        return [re.compile(rf'{y}-{m}(?!-\d)'), re.compile(rf'{y}年0?{mi}月(?!\d)'), re.compile(rf'{MONTHS[mi - 1]},? {y}')]
    return [re.compile(rf'{y}-{m}-{day}'), re.compile(rf'{y}年0?{mi}月0?{int(day)}日')]


def sentences(text):
    return [s for s in re.split(r'[。\n]', text) if s.strip()]


def strings(x, skip=()):
    """JSON の値の中の文字列をすべて返す（skip のキーの下は除く）。"""
    if isinstance(x, str):
        yield x
    elif isinstance(x, list):
        for v in x:
            yield from strings(v, skip)
    elif isinstance(x, dict):
        for k, v in x.items():
            if k not in skip:
                yield from strings(v, skip)


def validate_dates(data, codes):
    errors = []
    events = {e['id']: e for e in data['events']}
    for e in data['events']:
        start, end = event_dates(e)
        for d in (start, end):
            if not DATE_FULL_RE.match(d):
                errors.append(f"{e['id']}: date の書式が不正: {e['date']}")
        if not le(start, end):
            errors.append(f"{e['id']}: 期間の開始が終了より後: {e['date']}")
        for o in e.get('other_dates', []) + e.get('rejected_dates', []):
            if not DATE_FULL_RE.match(o['date']):
                errors.append(f"{e['id']}: other_dates・rejected_dates の書式が不正: {o['date']}")
            for s in o.get('sources', []) + o.get('claimed_by', []):
                if s not in codes:
                    errors.append(f"{e['id']}: other_dates・rejected_dates の出典の記号がない: {s}")
        for r in e.get('rejected_dates', []):
            if r['date'] in [start, end] + [o['date'] for o in e.get('other_dates', [])]:
                errors.append(f"{e['id']}: rejected_dates の {r['date']} が date か other_dates と同じ")
    for x in data['entries'] + data['errata']:
        a, f, u = (lead_date(x.get(k)) for k in ('announced', 'effective_from', 'effective_until'))
        for p, q, label in ((a, f, '公表 ≦ 適用開始'), (f, u, '適用開始 ≦ 適用終了'), (a, u, '公表 ≦ 適用終了')):
            if p and q and not le(p, q):
                errors.append(f"{x['id']}: 日付の順が逆（{label}）: {p} > {q}")
        for key, ev_key in (('announced', 'announced_event'), ('printed_from', 'printed_event'), ('effective_from', 'effective_event')):
            if not x.get(ev_key):
                continue
            ev = events.get(x[ev_key])
            if ev is None:
                errors.append(f"{x['id']}: {ev_key} の出来事がない: {x[ev_key]}")
                continue
            mine = lead_date(x.get(key))
            known = [event_dates(ev)[0]] + [o['date'] for o in ev.get('other_dates', [])]
            if not mine or not any(compatible(mine, k) for k in known):
                errors.append(f"{x['id']}: {key}（{x.get(key)}）が {ev['id']} の日付（{'・'.join(known)}）と合わない")
        if x.get('category') in ('printed_text_change', 'official_errata'):
            ev = events.get(x.get('effective_event'))
            if ev and ev['type'] == 'product':
                errors.append(f"{x['id']}: effective_event が商品の出来事（{ev['id']}）。新しい文面の印刷の開始なら printed_event・printed_from に書く")
            if f and '印刷' in x['effective_from']:  # 日付を書いた適用の開始が、印刷の日付の説明になっている
                errors.append(f"{x['id']}: effective_from が印刷の日付になっている。印刷の開始は printed_from に書く: {x['effective_from'][:60]}")
            p = lead_date(x.get('printed_from'))
            for st in x.get('stages', []):
                if st['kind'] == 'printed_change' and st.get('date') and p and not compatible(st['date'], p):
                    errors.append(f"{x['id']}: printed_from（{p}）と、段階 printed_change の日付（{st['date']}）が合わない")
        for eid in (x.get('applies_to') or {}).get('events', []):
            ev = events.get(eid)
            if not ev or ev['type'] != 'tournament':
                continue
            start = event_dates(ev)[0]
            if f and not le(f, start):
                errors.append(f"{x['id']}: 大会 {eid}（{start}）が適用開始（{f}）より前")
            if u and not le(start, u):
                errors.append(f"{x['id']}: 大会 {eid}（{start}）が適用終了（{u}）より後")
    # rejected_dates が、その日付を挙げた資料の説明なしに使われていないか
    texts = [(x['id'], s) for x in all_items(data) for s in strings(x, skip=('evidence', 'rejected_dates', 'other_dates'))]
    diff = json.loads((ROOT / 'data' / 'rule_differences.json').read_text(encoding='utf-8'))
    texts += [('data/rule_differences.json', s) for s in strings(diff)]
    texts += [(str(path.relative_to(ROOT)), path.read_text(encoding='utf-8')) for path in PROSE if path.exists()]
    for e in data['events']:
        for r in e.get('rejected_dates', []):
            pats = date_patterns(r['date'])
            for where, text in texts:
                for s in sentences(text):
                    if not any(k in s for k in r['keywords']) or not any(pt.search(s) for pt in pats):
                        continue
                    if any(f'[{c}]' in s for c in r['claimed_by']) or '以前の版' in s:
                        continue
                    errors.append(f"{where}: {e['id']} の誤りと判断した日付 {r['date']} が、出典（{'・'.join(r['claimed_by'])}）の説明なしに使われている: {s.strip()[:80]}")
    return errors


def all_items(data):
    return data['events'] + data['entries'] + data['errata']


def validate(data, cards, codes):
    errors = []
    ids = [x['id'] for x in all_items(data)]
    for i in {i for i in ids if ids.count(i) > 1}:
        errors.append(f'id の重複: {i}')
    known = set(ids)
    events = {e['id'] for e in data['events']}
    for x in all_items(data):
        for e in (x.get('applies_to') or {}).get('events', []):
            if e not in events:
                errors.append(f"{x['id']}: 大会・商品の id がない: {e}")
        for c in x.get('cards', []):
            if not cards.exists(c):
                errors.append(f"{x['id']}: カード id がない: {c}")
        if x.get('cards_from') and x['cards_from'] not in data['card_lists']:
            errors.append(f"{x['id']}: card_lists がない: {x['cards_from']}")
        for e in x.get('evidence', []):
            for s in [e['source']] + e.get('cites', []):
                if s not in codes:
                    errors.append(f"{x['id']}: 出典の記号がない: {s}")
            if e['kind'] not in data['evidence_kinds']:
                errors.append(f"{x['id']}: 証拠の種類がない: {e['kind']}")
        text = json.dumps({k: v for k, v in x.items() if k != 'evidence'}, ensure_ascii=False)
        for s in SRC_RE.findall(text):
            if s not in codes:
                errors.append(f"{x['id']}: 本文の出典の記号がない: {s}")
        for ref in ID_RE.findall(text):
            if ref not in known and ref != x['id']:
                errors.append(f"{x['id']}: 本文の id がない: {ref}")
        if x.get('confidence') and x['confidence'] not in data['confidence_values']:
            errors.append(f"{x['id']}: 確度の値が不正: {x['confidence']}")
        if x.get('category') and x['category'] not in data['categories']:
            errors.append(f"{x['id']}: 区分の値が不正: {x['category']}")
        kinds = {e['kind'] for e in x.get('evidence', [])}
        if ORIGINAL_CLAIM_RE.search(x.get('verification') or '') and 'original' not in kinds:
            errors.append(f"{x['id']}: verification が原本との照合を書いているが、根拠に original がない")
        errors += validate_stages(x, data, codes)
    for name, lst in data['card_lists'].items():
        if lst['entry'] not in known:
            errors.append(f'card_lists.{name}: entry がない: {lst["entry"]}')
        for row in lst['cards']:
            if 'qa' in row and set(row['qa']) != {'type', 'name', 'series', 'power'}:
                errors.append(f"card_lists.{name}: qa の欄が不正: {row['bulbapedia']}")
            if not row['ids']:
                errors.append(f"card_lists.{name}: 対応するカードがない: {row['bulbapedia']}")
            for c in row['ids']:
                if not cards.exists(c):
                    errors.append(f'card_lists.{name}: カード id がない: {c}')
    for path in HANDWRITTEN:
        if not path.exists():
            errors.append(f'{path.relative_to(ROOT)} がない')
            continue
        text = path.read_text(encoding='utf-8')
        for ref in sorted(set(ID_RE.findall(text))):
            if ref not in known:
                errors.append(f'{path.relative_to(ROOT)}: id がない: {ref}')
        for s in sorted(set(SRC_RE.findall(text))):
            if s not in codes:
                errors.append(f'{path.relative_to(ROOT)}: 出典の記号がない: {s}')
    errors += validate_dates(data, codes)
    errors += validate_documents(data, codes, known)
    errors += validate_editions(data, codes)
    errors += validate_card_errata(data)
    return errors


def validate_card_errata(data):
    """カードの日英の違いで「エラッタ」（kind が errata）とした記録が、公式エラッタの記録（official_errata）のカードか。
    再録の文面の変更や予告だけのもの（プラスパワーなど）を、カードの側でエラッタとして載せていないかを見る。"""
    errors = []
    official = {c for x in all_items(data) if x.get('category') == 'official_errata' for c in x.get('cards', [])}
    diffs = json.loads((ROOT / 'data' / 'curation' / 'card_differences.json').read_text(encoding='utf-8'))
    other = json.loads((ROOT / 'data' / 'curation' / 'other_products.json').read_text(encoding='utf-8'))['differences']
    for where, table in (('card_differences.json', diffs), ('other_products.json の differences', other)):
        for cid, entries in table.items():
            if cid.startswith('_'):
                continue
            for d in entries:
                if d['kind'] == 'errata' and cid not in official:
                    errors.append(f"data/curation/{where}: {cid} の「{d['summary']}」をエラッタとしているが、"
                                  f"data/rule_history.json に公式エラッタ（official_errata）の記録がない")
    return errors


def validate_stages(x, data, codes):
    errors = []
    stages = x.get('stages', [])
    for st in stages:
        if st['kind'] not in data['stage_kinds']:
            errors.append(f"{x['id']}: 段階の種類がない: {st['kind']}")
        if st['confidence'] not in data['confidence_values']:
            errors.append(f"{x['id']}: 段階の確度の値が不正: {st['confidence']}")
        if st.get('date') and not DATE_FULL_RE.match(st['date']):
            errors.append(f"{x['id']}: 段階の日付の書式が不正: {st['date']}")
        if st['confidence'] != '未確認' and not st.get('sources'):
            errors.append(f"{x['id']}: 確認した段階（{st['kind']}）に出典がない")
        for c in st.get('sources', []) + SRC_RE.findall(json.dumps(st, ensure_ascii=False)):
            if c not in codes:
                errors.append(f"{x['id']}: 段階の出典の記号がない: {c}")
    if x.get('category') == 'official_errata':
        notices = [st for st in stages if st['kind'] == 'official_notice']
        if not stages:
            errors.append(f"{x['id']}: 公式エラッタに分類しているが、stages（予告・印刷・告知・適用の区別）がない")
        elif not any(st['confidence'] in ('確実', '有力') for st in notices):
            errors.append(f"{x['id']}: 公式エラッタに分類しているが、公式の告知（official_notice）の段階が確認できていない")
        a = lead_date(x.get('announced'))
        for st in notices:
            if st.get('date') and a and not compatible(st['date'], a):
                errors.append(f"{x['id']}: 公式の告知の段階の日付（{st['date']}）が announced（{a}）と合わない")
    for st in stages:
        if st['kind'] in ('official_notice', 'applied') and st['confidence'] == '未確認' and st.get('date'):
            errors.append(f"{x['id']}: 未確認の段階（{st['kind']}）に日付がある（推定した日付を確定日として書かない）")
    return errors


def validate_documents(data, codes, known):
    errors = []
    docs = {}
    for doc in data.get('documents', []):
        c = doc['code']
        if c in docs:
            errors.append(f'documents: 記号の重複: {c}')
        docs[c] = doc
        for s in (c, doc['scan']['source']):
            if s not in codes:
                errors.append(f'documents.{c}: 出典の記号がない: {s}')
        for key in ('issued', 'released'):
            if doc.get(key) and not DATE_FULL_RE.match(doc[key]):
                errors.append(f'documents.{c}: {key} の書式が不正: {doc[key]}')
        for pg in doc['pages']:
            for r in pg['refs']:
                if r not in known:
                    errors.append(f'documents.{c}: p.{pg["printed"]} の id がない: {r}')
    for x in all_items(data):
        for e in x.get('evidence', []):
            if e['kind'] == 'scan_image' and e['source'] == 'J37':
                for c in e.get('cites', []):
                    if c not in docs:
                        errors.append(f"{x['id']}: スキャンの資料 {c} が documents にない")
    return errors


def validate_editions(data, codes):
    errors = []
    events = {e['id']: e for e in data['events']}
    eds = {}
    for ed in data.get('jp_editions', []):
        if ed['id'] in eds:
            errors.append(f"jp_editions: id の重複: {ed['id']}")
        eds[ed['id']] = ed
        if not DATE_FULL_RE.match(ed['date']):
            errors.append(f"jp_editions.{ed['id']}: date の書式が不正: {ed['date']}")
        ev = events.get(ed.get('event'))
        if ed.get('event') and ev is None:
            errors.append(f"jp_editions.{ed['id']}: 出来事がない: {ed['event']}")
        elif ev and not compatible(ed['date'], event_dates(ev)[0]):
            errors.append(f"jp_editions.{ed['id']}: date（{ed['date']}）が {ev['id']} の日付と合わない")
        if ed['confidence'] not in data['confidence_values']:
            errors.append(f"jp_editions.{ed['id']}: 確度の値が不正")
        for s in ed['sources'] + SRC_RE.findall(json.dumps(ed, ensure_ascii=False)):
            if s not in codes:
                errors.append(f"jp_editions.{ed['id']}: 出典の記号がない: {s}")
    columns = {e for e, v in eds.items() if v['in_matrix']}
    diff = json.loads((ROOT / 'data' / 'rule_differences.json').read_text(encoding='utf-8'))
    items_by_id = {i['id']: i for i in diff['items']}
    items = set(items_by_id)
    rows = set()
    for row in data.get('jp_edition_matrix', []):
        rid = row['id']
        if rid in rows:
            errors.append(f'jp_edition_matrix: id の重複: {rid}')
        rows.add(rid)
        if row.get('rd_item') and row['rd_item'] not in items:
            errors.append(f"jp_edition_matrix.{rid}: rule_differences の項目がない: {row['rd_item']}")
        for ed, c in row['cells'].items():
            if ed not in columns:
                errors.append(f'jp_edition_matrix.{rid}: 版がない: {ed}')
            if c['confidence'] not in data['confidence_values']:
                errors.append(f'jp_edition_matrix.{rid}.{ed}: 確度の値が不正')
            if c['basis'] not in data['evidence_kinds']:
                errors.append(f'jp_edition_matrix.{rid}.{ed}: 根拠の種類がない: {c["basis"]}')
            if not c['sources']:
                errors.append(f'jp_edition_matrix.{rid}.{ed}: 出典がない')
            if c.get('evidence_type') not in data['matrix_evidence_types']:
                errors.append(f'jp_edition_matrix.{rid}.{ed}: 根拠の性質の値が不正: {c.get("evidence_type")}')
            elif c['evidence_type'] in ('secondary', 'inferred') and c['confidence'] == '確実':
                errors.append(f'jp_edition_matrix.{rid}.{ed}: 二次資料だけ・推定だけのマスを「確実」にしている')
            if not c.get('scope'):
                errors.append(f'jp_edition_matrix.{rid}.{ed}: 裏付けの範囲（scope）がない')
        errors += compare_with_differences(row, eds, items_by_id.get(row.get('rd_item')))
        for s in SRC_RE.findall(json.dumps(row, ensure_ascii=False)) + [s for c in row['cells'].values() for s in c['sources']]:
            if s not in codes:
                errors.append(f'jp_edition_matrix.{rid}: 出典の記号がない: {s}')
    return errors


def editions_of_period(period, last):
    """rule_differences の行の時期（「第1版〜第4版」「第3版（…）以降」「第5版より前」など）が指す版の番号。版で始まらなければ空。"""
    m = EDITION_RE.match(period)
    if not m:
        return set()
    n = int(m.group(1))
    rest = period[m.end():]
    if rest.startswith('〜第'):
        return set(range(n, int(rest[2]) + 1))
    if rest.startswith('より前'):
        return set(range(1, n))
    if rest.startswith('まで'):
        return set(range(1, n + 1))
    if re.match(r'^(?:（[^）]*）)?以降', rest):
        return set(range(n, last + 1))
    return {n}


def compare_with_differences(row, eds, item):
    """版ごとの比較表のマスと、日米の違いの表の「第N版」の行の確度を突き合わせる。"""
    if item is None:
        return []
    errors = []
    number = {e: int(EDITION_RE.match(v['label']).group(1)) for e, v in eds.items() if v['in_matrix']}
    last = max(number.values())
    rows = item['jp']
    if 'rd_periods' in row:  # 同じ項目を比較表の複数の行に分けたときは、対応する行だけを比べる
        periods = {r['period'] for r in rows}
        errors += [f"jp_edition_matrix.{row['id']}: rd_periods の時期が rule_differences にない: {p}" for p in row['rd_periods'] if p not in periods]
        rows = [r for r in rows if r['period'] in row['rd_periods']]
    for r in rows:
        covered = editions_of_period(r['period'], last)
        for ed, n in number.items():
            if n not in covered:
                continue
            cell = row['cells'].get(ed)
            if cell is None:
                errors.append(f"jp_edition_matrix.{row['id']}: rule_differences の行「{r['period']}」が第{n}版を含むが、比較表のマスは未確認")
            elif cell['confidence'] != r['confidence'] and not cell.get('rd_note'):
                errors.append(f"jp_edition_matrix.{row['id']}.{ed}: 確度（{cell['confidence']}）が rule_differences の行「{r['period']}」（{r['confidence']}）と違う（理由は rd_note に書く）")
    return errors


def evidence_line(e):
    cites = f"（当時の資料: {'・'.join(f'[{c}]' for c in e['cites'])}）" if e.get('cites') else ''
    return f"[{e['source']}] {md(e['detail'])}{cites} — {EVIDENCE_SHORT[e['kind']]}"


def card_cell(cards, ids):
    return '<br>'.join(cards.label(i) for i in ids)


def detail(x, data, cards):
    L = [f'<a id="{x['id'].lower()}"></a>', '', f"### {x['id']}: {x['title']}", '',
         f"- 地域: {REGION_JA[x['region']]}　区分: {data['categories'][x['category']]}"]
    if x.get('id_note'):
        L.append(f"- id について: {x['id_note']}")
    for key, label in (('announced', '公表'), ('printed_from', '新しい文面の印刷の開始'), ('effective_from', '適用の開始'),
                       ('effective_until', '適用の終了')):
        if x.get(key):
            L.append(f'- {label}: {x[key]}')
    if x.get('applies_to', {}).get('events'):
        names = {e['id']: e['name'] for e in data['events']}
        L.append('- 対象の大会・商品: ' + '、'.join(f"{names[e]}（{e}）" for e in x['applies_to']['events']))
    if x.get('cards'):
        L.append('- 対象のカード: ' + '、'.join(cards.label(c) for c in x['cards']))
        others = [o for c in x['cards'] for o in cards.others(c)]
        if others:
            L.append('  - 同じカードのほかの版: ' + '、'.join(cards.label(o) for o in others))
    for c in x.get('external_cards', []):
        L.append(f"- このリポジトリにないカード: {c['name']}（{c['ref']}。{c['note']}）")
    for key, label in (('printed_text', '印刷された文面'), ('play_text', 'エラッタ後・読み替え後'), ('before', '変更前'), ('after', '変更後')):
        if x.get(key):
            L.append(f'- {label}: {x[key]}')
    if x.get('stages'):
        L.append('- 段階ごとの確認状況:')
        L.append('')
        L.append('  | 段階 | 日付 | 内容 | 確度 | 出典 |')
        L.append('  |---|---|---|---|---|')
        for st in x['stages']:
            L.append(f"  | {data['stage_kinds'][st['kind']]} | {st.get('date') or '—'} | {md(st['text'])} | {st['confidence']} | {cite(st.get('sources', [])) or '—'} |")
        L.append('')
    for n in x.get('notes', []):
        L.append(f'- {n}')
    L.append('- 根拠:')
    for e in x.get('evidence', []):
        L.append(f"  - {evidence_line(e)}")
    if x.get('verification'):
        L.append(f"- 原本との照合: {x['verification']}")
    L.append(f"- 確度: **{x['confidence']}**")
    if x.get('open_questions'):
        L.append('- 未解決: ' + '／'.join(x['open_questions']))
    L.append('')
    return L


def qa_cell(q):
    return f"{q['type']}・{q['name']}（{q['series']}）「{q['power']}」"


def card_list_table(lst, cards):
    has_qa = any('qa' in row for row in lst['cards'])
    head = ['Q&A の表記（属性・カード名（シリーズ）「特殊能力」）'] if has_qa else []
    head += ['Bulbapedia の表記', 'このリポジトリのカード', '同じカードのほかの版']
    L = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    for row in lst['cards']:
        others = [o for i in row['ids'] for o in cards.others(i) if o not in row['ids']]
        cells = [md(qa_cell(row['qa']))] if has_qa else []
        cells += [md(row['bulbapedia']), card_cell(cards, row['ids']), card_cell(cards, others)]
        L.append('| ' + ' | '.join(cells) + ' |')
    return L


def build(data, cards):
    # カードの扱いを変える記録（読み替えの一覧 cards_from を持つ大会のレギュレーションを含む）
    errata = data['errata'] + [x for x in data['entries']
                               if x['category'] in ('official_errata', 'printed_text_change', 'card_ruling') or x.get('cards_from')]
    errata.sort(key=lambda x: (x['region'], x['id']))
    L = ['# カードの文面の変更とエラッタの履歴', '', GENERATED, '',
         '旧裏期（1996〜2001年）のカードについて、印刷された文面の変更、公式エラッタ、ルールによる読み替えを記録します。'
         '2001〜2003年の旧裏・新裏の混合ルールは [旧裏・新裏の混合ルール](mixed-2002.md)、出典の記号は [出典と確認状況](../sources.md) を参照してください。', '',
         '<a id="kinds"></a>', '', '## 3 つの区別', '',
         '| 区分 | 意味 | 例 |', '|---|---|---|',
         '| 印刷テキストの変更 | 再録や新しい版に、違う文面が印刷されたこと。**それだけでは古い版の扱いは変わらない** | ジムデッキの再録の書き換え（[再録カードの対応付け](../cards/reprints.md)） |',
         '| 公式エラッタ | 印刷された版にかかわらず、別の文面で使うよう公式に指定されたこと | エネルギー回収を基本エネルギーだけにする（1998年） |',
         '| ルール変更・裁定 | カードの文面は変わらないが、ルールや裁定で効果の扱いが変わること | 旧裏の特殊能力をポケパワー・ポケボディーとして扱う（2002年） |', '',
         '- 再録で文面が変わったことだけを根拠に、古い版にも同じエラッタが出たとはしていません。エラッタの告知を確認できないものは「未確認」としています。',
         '- 日本版（メディアファクトリー／ポケモン）と英語版（WotC）の扱いは分けて書いています。英語版だけのエラッタ・禁止は、日本版には当てはまりません。', '',
         '## 根拠の種類と確度', '',
         '| 根拠の種類 | 意味 |', '|---|---|']
    L += [f'| {k} | {v} |' for k, v in data['evidence_kinds'].items()]
    L += ['', '表の短い名前（各項目の「根拠」で使用）: ' + '、'.join(f'{k} = {v}' for k, v in EVIDENCE_SHORT.items()) + '。',
          '', '| 確度 | 意味 |', '|---|---|']
    L += [f'| {k} | {v} |' for k, v in data['confidence_values'].items()]
    scanned = '、'.join(f"[{d['code']}]" for d in data['documents'])
    L += ['', '- 当時の公式資料のうち原文を確認できたのは、公式サイトのページ（[P10]、[P15]〜[P23]、[P28]。Internet Archive に保存された写し）と、'
          f"[印刷物の照合記録](../printed-sources.md) の {len(data['documents'])} 冊の誌面（{scanned}。[J37] のスキャンで、実物ではない）です。"
          'ルールブック（どの版も）の原文は確認できていません。'
          '二次資料が挙げている当時の資料も [P1] などの記号で示しています。',
          '- エラッタの記録の一部には「段階ごとの確認状況」を付けています。変更の予告、新しい文面の印刷、既存のカードにも適用する公式の告知、'
          '実際の適用（大会・ふだんの対戦）を分けて、それぞれ確認できたかを書いています。予告や再録の文面の変更だけでは、公式エラッタとはしていません。', '',
          '## 一覧', '',
          '| id | 地域 | 区分 | 対象 | 公表・印刷・適用 | 確度 |', '|---|---|---|---|---|---|']
    for x in errata:
        target = '、'.join(cards.label(c) for c in x.get('cards', [])) or ('一覧のカード' if x.get('cards_from') else '')
        when = '<br>'.join(f"{label} {lead_text(x[key])}" for key, label in
                           (('announced', '公表'), ('printed_from', '印刷'), ('effective_from', '適用')) if x.get(key))
        L.append(f"| [{x['id']}](#{x['id'].lower()}) | {REGION_JA[x['region']]} | {data['categories'][x['category']].split('（')[0]} | "
                 f"{md(x['title'])}<br>{md(target)} | {md(when)} | {x['confidence']} |")
    L += ['', '## 詳細', '']
    for x in errata:
        L += detail(x, data, cards)
    for name, title in (('supporter', 'サポーターとして扱う旧裏・neo のトレーナー（日本だけ）'),
                        ('poke_body', 'ポケボディーとして扱う旧裏・neo の特殊能力（日本だけ）')):
        lst = data['card_lists'][name]
        L += [f'<a id="{name.replace("_", "-")}-list"></a>', '', f'## {title}', '', f"{lst['note']} 根拠と確度は {lst['entry']} を参照。", '']
        L += card_list_table(lst, cards) + ['']
    L += ['## 年表', '', '| 日付 | 地域 | 出来事 | id |', '|---|---|---|---|']
    for e in sorted(data['events'], key=lambda e: e['date']):
        other = ''.join(f"<br>（{o['label']}: {o['date']}）" for o in e.get('other_dates', []))
        L.append(f"| {e['date']}{other} | {REGION_JA[e['region']]} | {md(e['name'])} | {e['id']} |")
    L.append('')
    return L


def cite(sources):
    return ''.join(f'[{s}]' for s in sources)


def build_editions(data):
    eds = data['jp_editions']
    cols = [e for e in eds if e['in_matrix']]
    L = ['# 日本版のルールの版ごとの比較（1996〜1999年）', '',
         '<!-- このファイルは scripts/build_rule_history.py が data/rule_history.json の jp_editions・jp_edition_matrix から生成しています。直接編集しないでください。 -->', '',
         '旧裏期の日本版のルールを、版ごと・項目ごとに並べた表です。ルールの説明と資料の食い違いは [日本版のルールと変遷](japanese.md)、'
         '英語版との比較は [日米のルールの違い](differences.md)、出典の記号は [出典と確認状況](../sources.md)、'
         'スキャンで確認した誌面のページは [印刷物の照合記録](../printed-sources.md) を参照してください。', '',
         '- 版ごとの文書（ルールブック・遊びかた説明書）の原文は、どの版も確認できていません。表の内容は、各版の時期の公式の雑誌・書籍の説明（スキャン）と二次資料によります。',
         '- 原文や当時の説明で確認できなかったマスは「未確認」です。ほかの版の内容から推測して埋めていません。',
         '- 「公式ルール」「ルールブック」「遊びかた説明書」は資料によって呼び方が違います。1997年の会報は、詳しい「公式ルール」は書籍（『大人にもわかるポケモンカード戦略』）に載せ、スターターパックの「遊びかた説明書」は「順次改定される予定」と書いています [P31]。版の番号が同じ文書の系列を指すかは確認できていません。',
         '- 発売元のガイドブック [P29] の「公式ルール」は、基本の遊びかたとは別の追加ルールとして書かれています。公式大会の大会専用ルールも、基本ルールとは別のものです。', '',
         '## 版と時期', '',
         '版の日付は発表・告知の日で、ルールが実際に使われ始めた日（適用）とは限りません。', '',
         '| 版 | 時期 | 資料での呼び名 | 適用 | 根拠 | 確度 |', '|---|---|---|---|---|---|']
    for e in eds:
        extra = [s for s in e['sources'] if f'[{s}]' not in e['basis'] + e['name_in_sources'] + e['period'] + e['applied']]
        L.append(f"| {e['label']} | {md(e['period'])} | {md(e['name_in_sources'])} | {md(e['applied'])} | {md(e['basis'])} {cite(extra)} | {e['confidence']} |")
    L += ['', '## 項目ごとの比較', '',
          '各マスは「内容（確度・根拠の性質）[出典]」です。根拠の性質:', '']
    L += [f"- **{MATRIX_TYPE_SHORT[k]}**: {v}" for k, v in data['matrix_evidence_types'].items()]
    L += ['', 'どの資料がどの時期・範囲まで裏付けるか（裏付けの範囲）と、資料の確認方法（スキャン・二次資料など）は、[項目ごとの補足](#notes) にマスごとに書いています。', '',
          '| 項目 | ' + ' | '.join(c['label'] for c in cols) + ' |', '|---|' + '---|' * len(cols)]
    for row in data['jp_edition_matrix']:
        cells = []
        for c in cols:
            v = row['cells'].get(c['id'])
            cells.append('未確認' if v is None else f"{md(v['text'])}（{v['confidence']}・{MATRIX_TYPE_SHORT[v['evidence_type']]}）{cite(v['sources'])}")
        L.append(f"| [{row['label']}](#{row['id']}) | " + ' | '.join(cells) + ' |')
    L += ['', '<a id="notes"></a>', '', '## 項目ごとの補足', '']
    for row in data['jp_edition_matrix']:
        L += [f'<a id="{row["id"]}"></a>', '', f"### {row['label']}", '']
        if row.get('rd_item'):
            L.append(f"- 英語版との比較: [日米のルールの違い](differences.md#{row['rd_item']})")
        for c in cols:
            v = row['cells'].get(c['id'])
            if v is None:
                continue
            note = f"（{v['rd_note']}）" if v.get('rd_note') else ''
            L.append(f"- {c['label']}: {MATRIX_TYPE_SHORT[v['evidence_type']]}・{BASIS_SHORT[v['basis']]} {cite(v['sources'])}。裏付けの範囲: {md(v['scope'])}{md(note)}")
        for n in row['notes']:
            L.append(f'- {n}')
        L.append('')
    return L


def build_documents(data):
    names = {x['id']: x.get('title') or x.get('name') for x in all_items(data)}
    L = ['# 印刷物の照合記録', '',
         '<!-- このファイルは scripts/build_rule_history.py が data/rule_history.json の documents から生成しています。直接編集しないでください。 -->', '',
         '当時の印刷物を、スキャン（[出典と確認状況](sources.md) の J37。Elite Fourum のスレッドで公開された Google Drive の PDF）で確認した記録です。'
         '印刷物の実物を確認したものではありません。ページ番号は誌面に印刷された番号（ノンブル）、PDF のページは Drive のビューアーで数えたページです。', '',
         '- スキャンのファイルは第三者が公開したもので、公開が続く保証はありません。',
         '- 確認した刷が初版でないものは、その刷を書いています。初版の文面と同じとは限りません。',
         '- 本文の引用は、それぞれの記録（`data/rule_history.json` の id）にあります。ここにはページの内容の要約だけを置いています。', '',
         '| 記号 | 資料 | 発行日 | 発売日 | 確認した刷 | スキャン |', '|---|---|---|---|---|---|']
    for doc in data['documents']:
        L.append(f"| [{doc['code']}](#{doc['code'].lower()}) | {md(doc['title'])} | {doc.get('issued') or '—'} | {doc.get('released') or '—'} | "
                 f"{md(doc['printing_checked'])} | [PDF]({doc['scan']['url']}) |")
    L.append('')
    for doc in data['documents']:
        L += [f'<a id="{doc["code"].lower()}"></a>', '', f"## {doc['code']}: {doc['title']}", '',
              f"- 発行: {md(doc['publisher'])}",
              f"- 発行日: {doc.get('issued') or '未確認'}" + (f"（発売日 {doc['released']}）" if doc.get('released') else ''),
              f"- 確認した刷: {doc['printing_checked']}",
              f"- スキャン: {doc['scan']['url']}（[{doc['scan']['source']}]" + (f"、PDF {doc['scan']['pdf_pages']} ページ）" if doc['scan']['pdf_pages'] else '）')]
        for n in doc['notes']:
            L.append(f'- {n}')
        L += ['', '| ページ | PDF のページ | 内容 | 根拠にした記録 |', '|---|---|---|---|']
        for pg in doc['pages']:
            refs = '<br>'.join(f'{r}（{md(names.get(r, ""))}）' for r in pg['refs']) or '—'
            L.append(f"| {pg['printed']} | {pg['pdf']} | {md(pg['content'])} | {refs} |")
        L.append('')
    return L


def main():
    check = '--check' in sys.argv[1:]
    data = json.loads(DATA.read_text(encoding='utf-8'))
    cards = Cards()
    errors = validate(data, cards, source_codes())
    outputs = [(OUT, '\n'.join(build(data, cards))), (OUT_EDITIONS, '\n'.join(build_editions(data))),
               (OUT_DOCUMENTS, '\n'.join(build_documents(data)))]
    for path, text in outputs:
        if check:
            if not path.exists() or path.read_text(encoding='utf-8') != text:
                errors.append(f'{path.relative_to(ROOT)} が data/rule_history.json から生成した内容と違う（生成し直す）')
        else:
            path.write_text(text, encoding='utf-8')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        raise SystemExit(f'{len(errors)} 件の参照切れ・不正な値')
    print(len(data['events']), 'events,', len(data['entries']), 'entries,', len(data['errata']), 'errata; OK')


if __name__ == '__main__':
    main()
