#!/usr/bin/env python3
"""ルール・レギュレーション・エラッタの履歴（data/rule_history.json）を検査し、docs/rules/errata-history.md を生成する。

検査すること:
  - id（EV-・MIX-・KGR-・EN-・ERR-・TXT-・RUL-）の重複
  - applies_to.events・cards・card_lists のカード id の参照切れ
    （カード id は data/cards.json の id か、data/ja_text_pcgsearch.json のページ名）
  - 出典の記号（source・cites、本文中の [X52] など）が docs/sources.md にあるか
  - 手書きの docs/rules/mixed-2002.md・kangaskhan-2002.md の中の id が存在するか
  - 日付の矛盾:
    - events の date・other_dates・rejected_dates の書式と、期間（開始 ≦ 終了）
    - 記録の announced ≦ effective_from ≦ effective_until（先頭の日付どうし。精度の粗い方に合わせて比べる）
    - announced_event・effective_event を書いた記録は、その出来事の date か other_dates と日付が合うか
    - applies_to.events の大会（type が tournament）が、記録の適用期間に入っているか
    - events の rejected_dates（資料が挙げるが誤りと判断した日付）が、keywords と同じ文の中で、
      その日付を挙げた資料（claimed_by の記号）や「以前の版」の説明なしに使われていないか
      （data/rule_history.json・data/rule_differences.json・手書きの docs/rules/*.md・docs/sources.md）。
      正当に違う日付（雑誌の発行日と発売日など）は other_dates に書くので、単純な文字列の一致では検出しない
  - --check: 生成結果が docs/rules/errata-history.md と同じか（ファイルは書き換えない）

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
HANDWRITTEN = [ROOT / 'docs' / 'rules' / 'mixed-2002.md', ROOT / 'docs' / 'rules' / 'kangaskhan-2002.md']
# rejected_dates を探す文書（手書き。生成物は元データを検査すれば足りる）
PROSE = HANDWRITTEN + [ROOT / 'docs' / 'rules' / n for n in ('japanese.md', 'wotc.md', 'README.md')] + [ROOT / 'docs' / 'sources.md']
DATE_RE = re.compile(r'^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?')
DATE_FULL_RE = re.compile(r'^\d{4}(?:-\d{2}(?:-\d{2})?)?$')
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
ID_RE = re.compile(r'\b(?:EV|MIX|KGR|EN|ERR|TXT|RUL)-[A-Z0-9][A-Z0-9-]*[A-Z0-9]\b')
SRC_RE = re.compile(r'\[([A-Z]\d+)\]')
GENERATED = ('<!-- このファイルは scripts/build_rule_history.py が data/rule_history.json から生成しています。'
             '直接編集しないでください。 -->')
REGION_JA = {'JP': '日本版', 'EN': '英語版'}
EVIDENCE_SHORT = {'original': '原本', 'archived_official': '公式ページの保存版（原文を確認）', 'scan_image': '印刷物の写真（文面を確認）', 'card_image': 'カードの画像',
                  'official_later': '後年の公式資料', 'secondary_direct': '二次資料（本文を確認）', 'search_summary': '検索結果の要約のみ'}


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
        for key, ev_key in (('announced', 'announced_event'), ('effective_from', 'effective_event')):
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
    return errors


def evidence_line(e):
    cites = f"（当時の資料: {'・'.join(f'[{c}]' for c in e['cites'])}）" if e.get('cites') else ''
    return f"[{e['source']}] {md(e['detail'])}{cites} — {EVIDENCE_SHORT[e['kind']]}"


def card_cell(cards, ids):
    return '<br>'.join(cards.label(i) for i in ids)


def detail(x, data, cards):
    L = [f'<a id="{x['id'].lower()}"></a>', '', f"### {x['id']}: {x['title']}", '',
         f"- 地域: {REGION_JA[x['region']]}　区分: {data['categories'][x['category']]}"]
    for key, label in (('announced', '公表'), ('effective_from', '適用・印刷の開始'), ('effective_until', '適用の終了')):
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
    L += ['', '- 当時の公式資料のうち原文を確認できたのは、公式サイトのページ（[P10]、[P15]〜[P23]、[P28]。Internet Archive に保存された写し）と、'
          '『トレーナーズ』Vol.10〜16・18〜21 と 1996年のガイドブックの誌面（[P4]〜[P9]、[P13]、[P24]〜[P27]、[P29]。[J37] のスキャン）です。'
          'ルールブック・ファンクラブ会報の原本と、『トレーナーズ』Vol.9 以前・Vol.17 は確認できていません。'
          '二次資料が挙げている当時の資料は [P1] などの記号で示しています。', '',
          '## 一覧', '',
          '| id | 地域 | 区分 | 対象 | 公表・印刷 | 確度 |', '|---|---|---|---|---|---|']
    for x in errata:
        target = '、'.join(cards.label(c) for c in x.get('cards', [])) or ('一覧のカード' if x.get('cards_from') else '')
        when = x.get('announced') or x.get('effective_from') or ''
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


def main():
    check = '--check' in sys.argv[1:]
    data = json.loads(DATA.read_text(encoding='utf-8'))
    cards = Cards()
    errors = validate(data, cards, source_codes())
    text = '\n'.join(build(data, cards))
    if check:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != text:
            errors.append(f'{OUT.relative_to(ROOT)} が data/rule_history.json から生成した内容と違う（生成し直す）')
    else:
        OUT.write_text(text, encoding='utf-8')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        raise SystemExit(f'{len(errors)} 件の参照切れ・不正な値')
    print(len(data['events']), 'events,', len(data['entries']), 'entries,', len(data['errata']), 'errata; OK')


if __name__ == '__main__':
    main()
