#!/usr/bin/env python3
"""data/rule_differences.json を検査し、docs/rules/differences.md を生成する。

検査すること:
  - 判定（status）と確度（confidence）の値
  - 出典の記号（sources、本文中の [X52] など）が docs/sources.md にあるか
  - refs（data/rule_history.json の id）と、本文中の MIX- などの id があるか
  - 確度の更新漏れ: refs で参照した rule_history の記録より確度が低い行は、
    confidence_note（範囲が違う理由）がなければエラー
  - --check: 生成結果が docs/rules/differences.md と同じか（ファイルは書き換えない）

使い方: python3 scripts/build_rule_differences.py [--check]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'rules' / 'differences.md'
STATUS_ORDER = ['違う', '時期により違う', '違う可能性あり', '同じ', '不明']
CONFIDENCE_RANK = {'未確認': 0, '有力': 1, '確実': 2}
SRC_RE = re.compile(r'\[([A-Z]\d+)\]')
ID_RE = re.compile(r'\b(?:EV|MIX|KGR|EN|ERR|TXT|RUL)-[A-Z0-9][A-Z0-9-]*[A-Z0-9]\b')


def refs(sources):
    return ''.join(f'[{s}]' for s in sources)


def tail(e):
    """確度と出典。本文が「未確認」だけなら確度を重ねない。本文中に出典記号があれば繰り返さない。"""
    conf = '' if e['rule'] == '未確認' else f"（{e['confidence']}）"
    src = '' if any(f'[{x}]' in e['rule'] for x in e['sources']) else refs(e['sources'])
    return conf + src


def source_codes():
    text = (ROOT / 'docs' / 'sources.md').read_text(encoding='utf-8')
    return set(re.findall(r'^\| ([A-Z]\d+) \|', text, re.M))


def history_confidence():
    """data/rule_history.json の id → 確度（events は確度を持たないので None）。"""
    h = json.loads((ROOT / 'data' / 'rule_history.json').read_text(encoding='utf-8'))
    return {x['id']: x.get('confidence') for x in h['events'] + h['entries'] + h['errata']}


def rows(data):
    """検査の対象になる行（項目の各時期、よくある誤解とその後のルール）を (場所, 行) で返す。"""
    for it in data['items']:
        for side in ('jp', 'en'):
            for k, e in enumerate(it[side]):
                yield f"{it['id']}.{side}[{k}]", e
    for k, m in enumerate(data['misconceptions']):
        yield f'misconceptions[{k}]', m
        for j, r in enumerate(m['later_rules']):
            yield f'misconceptions[{k}].later_rules[{j}]', r


def validate(data, codes, hist):
    errors = []
    for it in data['items']:
        if it['status'] not in STATUS_ORDER:
            errors.append(f"{it['id']}: 判定の値が不正: {it['status']}")
    for where, e in rows(data):
        if e.get('confidence') not in CONFIDENCE_RANK:
            errors.append(f"{where}: 確度の値が不正: {e.get('confidence')}")
        for s in e.get('sources', []):
            if s not in codes:
                errors.append(f'{where}: 出典の記号がない: {s}')
        text = json.dumps({k: v for k, v in e.items() if k not in ('sources', 'refs', 'later_rules')}, ensure_ascii=False)
        for s in SRC_RE.findall(text):
            if s not in codes:
                errors.append(f'{where}: 本文の出典の記号がない: {s}')
        for ref in e.get('refs', []) + ID_RE.findall(text):
            if ref not in hist:
                errors.append(f'{where}: rule_history の id がない: {ref}')
        known = [hist[r] for r in e.get('refs', []) if hist.get(r)]
        if known and e.get('confidence') in CONFIDENCE_RANK and not e.get('confidence_note'):
            best = max(known, key=CONFIDENCE_RANK.get)
            if CONFIDENCE_RANK[e['confidence']] < CONFIDENCE_RANK[best]:
                errors.append(f"{where}: 確度「{e['confidence']}」が、参照した記録（{'・'.join(e['refs'])}）の「{best}」より低い。"
                              '更新漏れでなければ confidence_note に理由を書く')
    for it in data['items']:
        text = json.dumps(it['notes'], ensure_ascii=False)
        for s in SRC_RE.findall(text):
            if s not in codes:
                errors.append(f"{it['id']}.notes: 出典の記号がない: {s}")
        for ref in ID_RE.findall(text):
            if ref not in hist:
                errors.append(f"{it['id']}.notes: rule_history の id がない: {ref}")
    for s in data['post_wotc_changes']['sources']:
        if s not in codes:
            errors.append(f'post_wotc_changes: 出典の記号がない: {s}')
    return errors


def conf_cell(e):
    return e['confidence'] + (f"（{e['confidence_note']}）" if e.get('confidence_note') else '')


def cell(entries):
    out = [f"**{e['period']}**: {e['rule']}{tail(e)}" for e in entries]
    return '<br>'.join(x.replace('|', '\\|') for x in out)


def build(data, editions):
    items = data['items']
    lines = [
        '# 日米のルールの違い（旧裏期の日本版 × WotC 期の英語版）',
        '',
        '<!-- このファイルは scripts/build_rule_differences.py が data/rule_differences.json から生成しています。直接編集しないでください。 -->',
        '',
        '旧裏期の日本版ルール（1996〜2001年）と、Wizards of the Coast が英語版を出していた時期（1999〜2003年）のルールを、項目ごとに並べたページです。',
        'カードの文面や収録内容の違いは [カードの日英の違い](../cards/card-differences.md) と [収録内容・製品の違い](../cards/set-differences.md) にあります。',
        '',
        '- 機械可読なデータ: [`data/rule_differences.json`](../../data/rule_differences.json)',
        '- 確度（確実／有力／未確認）と調べ方の限界: [ルール資料の README](README.md)',
        '- 出典の記号（[J1] など）: [出典と確認状況](../sources.md)',
        '- 日本版の各版の詳しい内容: [日本版のルールと変遷](japanese.md)',
        '- 英語版の詳しい内容: [英語版（WotC 版）のルール](wotc.md)',
        '',
        '日本版は時期によってルールが違います。各版の時期（`data/rule_history.json` の `jp_editions`。版ごとの比較は [日本版のルールの版ごとの比較](japanese-editions.md)）:',
        '',
        '| 版 | 時期 | 確度 |',
        '|---|---|---|',
    ]
    lines += [f"| {e['label']} | {e['period']} | {e['confidence']} |" for e in editions]
    lines += ['', '## 一覧', '', '| 項目 | 判定 | 日本版 | 英語版（WotC） |', '|---|---|---|---|']
    for it in sorted(items, key=lambda i: STATUS_ORDER.index(i['status'])):
        lines.append(f"| [{it['topic']}](#{it['id']}) | {it['status']} | {cell(it['jp'])} | {cell(it['en'])} |")
    lines += ['', '判定の意味:', '']
    lines += [f'- **{k}**: {v}' for k, v in data['status_values'].items()]
    lines += ['', '## よくある誤解', '']
    for m in data['misconceptions']:
        lines += [f"### 「{m['claim']}」", '', f"→ 誤り。{m['fact']}（{m['confidence']}）{refs(m['sources'])}", '']
        if m['later_rules']:
            lines += [m.get('later_rules_note', 'この種の制限は、どれも旧裏期・WotC 期より後に加わったものです。'), '',
                      '| 時期 | 地域 | 内容 | 確度 |', '|---|---|---|---|']
            lines += [f"| {r['year']} | {r['region']} | {r['rule']} | {r['confidence']} {refs(r['sources'])} |"
                      for r in m['later_rules']]
            lines.append('')
    lines += ['## 項目ごとの詳細', '']
    for it in items:
        lines += [f"<a id=\"{it['id']}\"></a>", '', f"### {it['topic']}", '', f"判定: **{it['status']}**", '']
        lines += ['| | 時期 | ルール | 確度 | 出典 |', '|---|---|---|---|---|']
        for side, label in (('jp', '日本版'), ('en', '英語版')):
            for e in it[side]:
                lines.append(f"| {label} | {e['period']} | {e['rule'].replace('|', '\\|')} | {conf_cell(e)} | {refs(e['sources']) or '―'} |")
        lines.append('')
        for n in it['notes']:
            lines.append(f'- {n}')
        if it['notes']:
            lines.append('')
    pw = data['post_wotc_changes']
    lines += ['## 参考: 2003年以降の英語版の変更', '', f"{pw['summary']} {refs(pw['sources'])}", '']
    lines += [f'- {c}' for c in pw['changes']]
    lines.append('')
    return '\n'.join(lines)


def main():
    check = '--check' in sys.argv[1:]
    data = json.loads((ROOT / 'data' / 'rule_differences.json').read_text(encoding='utf-8'))
    errors = validate(data, source_codes(), history_confidence())
    editions = json.loads((ROOT / 'data' / 'rule_history.json').read_text(encoding='utf-8'))['jp_editions']
    text = build(data, editions)
    if check:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != text:
            errors.append(f'{OUT.relative_to(ROOT)} が data/rule_differences.json から生成した内容と違う（生成し直す）')
    else:
        OUT.write_text(text, encoding='utf-8')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        raise SystemExit(f'{len(errors)} 件の問題')
    print(f"{len(data['items'])} items; OK")


if __name__ == '__main__':
    main()
