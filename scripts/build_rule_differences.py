#!/usr/bin/env python3
"""data/rule_differences.json から docs/rules/differences.md を生成する。

使い方: python3 scripts/build_rule_differences.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS_ORDER = ['違う', '時期により違う', '違う可能性あり', '同じ', '不明']


def refs(sources):
    return ''.join(f'[{s}]' for s in sources)


def tail(e):
    """確度と出典。本文が「未確認」だけなら確度を重ねない。本文中に出典記号があれば繰り返さない。"""
    conf = '' if e['rule'] == '未確認' else f"（{e['confidence']}）"
    src = '' if any(f'[{x}]' in e['rule'] for x in e['sources']) else refs(e['sources'])
    return conf + src


def cell(entries):
    out = [f"**{e['period']}**: {e['rule']}{tail(e)}" for e in entries]
    return '<br>'.join(x.replace('|', '\\|') for x in out)


def main():
    data = json.loads((ROOT / 'data' / 'rule_differences.json').read_text(encoding='utf-8'))
    items = data['items']
    unknown = {i['status'] for i in items} - set(STATUS_ORDER)
    if unknown:
        raise SystemExit(f'unknown status: {unknown}')
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
        '日本版は時期によってルールが違います。各版の施行時期:',
        '',
        '| 版 | 時期 |',
        '|---|---|',
    ]
    lines += [f'| {k} | {v} |' for k, v in data['jp_periods'].items()]
    lines += ['', '## 一覧', '', '| 項目 | 判定 | 日本版 | 英語版（WotC） |', '|---|---|---|---|']
    for it in sorted(items, key=lambda i: STATUS_ORDER.index(i['status'])):
        lines.append(f"| [{it['topic']}](#{it['id']}) | {it['status']} | {cell(it['jp'])} | {cell(it['en'])} |")
    lines += ['', '判定の意味:', '']
    lines += [f'- **{k}**: {v}' for k, v in data['status_values'].items()]
    lines += ['', '## よくある誤解', '']
    for m in data['misconceptions']:
        lines += [f"### 「{m['claim']}」", '', f"→ 誤り。{m['fact']}（{m['confidence']}）{refs(m['sources'])}", '']
        if m['later_rules']:
            lines += ['この種の制限は、どれも旧裏期・WotC 期より後に加わったものです。', '',
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
                lines.append(f"| {label} | {e['period']} | {e['rule'].replace('|', '\\|')} | {e['confidence']} | {refs(e['sources']) or '―'} |")
        lines.append('')
        for n in it['notes']:
            lines.append(f'- {n}')
        if it['notes']:
            lines.append('')
    pw = data['post_wotc_changes']
    lines += ['## 参考: 2003年以降の英語版の変更', '', f"{pw['summary']} {refs(pw['sources'])}", '']
    lines += [f'- {c}' for c in pw['changes']]
    lines.append('')
    (ROOT / 'docs' / 'rules' / 'differences.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(items)} items')


if __name__ == '__main__':
    main()
