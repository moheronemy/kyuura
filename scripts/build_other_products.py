#!/usr/bin/env python3
"""拡張パック以外の旧裏の商品（拡張シート、映画公開記念パック「サザンアイランド」）のページを生成する。

入力: data/ja_text_pcgsearch.json（pcg-search.com から抽出）、data/ja_text_nazonobasho.json（サザンアイランドのレベル・備考）、
      data/curation/other_products.json（発売日・英語版の対応・日英の違い）
出力: docs/cards/other-products.md

使い方: python3 scripts/build_other_products.py
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SI = '映画公開記念パック「サザンアイランド」'
DIFF_KIND_JA = {'text': '文面の意味', 'numbers': '数値', 'print': '英語版の表記・誤植', 'wording': '書き方（意味は同じ）'}


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def md(s):
    return (s or '').replace('|', '\\|').replace('\n', '<br>')


def page_id(card):
    return card['url'].rsplit('/', 1)[-1].removesuffix('.php')


def digits(s):
    return re.sub(r'\D', '', s or '')


def en_ref(e):
    return f"{e['set_name']} {e['number']}（{e['name']}）" if e else ''


def kind_short(card):
    k = card['kind'].replace('１', '1').replace('２', '2')
    return {'たねポケモン': 'たね', '1進化ポケモン': '1進化', '2進化ポケモン': '2進化'}.get(k, k)


def card_table(cards, en_prints):
    lines = ['| 番号 | カード名 | 種類 | タイプ | HP | レア | 英語版 |', '|---|---|---|---|---|---|---|']
    for c in cards:
        lines.append('| {} | [{}]({}) | {} | {} | {} | {} | {} |'.format(
            c['list_number'], md(c['name']), c['url'], kind_short(c), c.get('type') or '',
            c.get('hp') or '', c['rarity'] if c['rarity'] not in (None, '-') else '', en_ref(en_prints.get(page_id(c)))))
    return lines


def transcription_diffs(si_cards, nz_cards):
    """サザンアイランドの 2 つの転記（pcg-search となぞのばしょ）の、名前・HP・ダメージの食い違い。"""
    out = []
    for c in si_cards:
        z = nz_cards.get(c['name'])
        if not z:
            out.append((c['name'], 'カード', '（なし）', c['name']))
            continue
        if str(c.get('hp')) != str(z['fields'].get('HP')):
            out.append((c['name'], 'HP', z['fields'].get('HP'), c.get('hp')))
        for a, b in zip(z['attacks'], c['attacks']):
            if a['name'] != b['name']:
                out.append((c['name'], 'ワザ名', a['name'], b['name']))
            if digits(a['damage']) != digits(b['damage']):
                out.append((c['name'], f"{b['name']} のダメージ", a['damage'] or '（空欄）', b['damage'] or '（空欄）'))
    return out


def main():
    data = load('data/ja_text_pcgsearch.json')['products']
    cur = load('data/curation/other_products.json')
    en_prints, diffs = cur['en_prints'], cur['differences']
    nz = {c['fields']['カード名称']: c for c in
          load('data/ja_text_nazonobasho.json')['sets']['cardlist-pmcg-southernisland']['cards']}
    sheets = [p for p in cur['products'] if p['pcg_title'] != SI]
    si_meta = next(p for p in cur['products'] if p['pcg_title'] == SI)

    L = ['# 拡張シートとサザンアイランド', '',
         '<!-- このファイルは scripts/build_other_products.py が data/ja_text_pcgsearch.json と data/curation/other_products.json から生成しています。直接編集しないでください。 -->', '',
         '拡張パック以外で旧裏期に日本で出た商品のうち、「拡張シート」（第1〜3弾）と映画公開記念パック「サザンアイランド」をまとめたページです。',
         'これらのカードは、拡張パック 10 弾のデータ（`data/cards.json`）には入れず、`data/ja_text_pcgsearch.json` に収録しています。', '',
         '- カードの欄（名前・HP・ワザ・効果文など）は、ポケモンカード 旧シリーズ検索（pcg-search.com）[N3] の転記です。カード名から各カードのページにリンクしています。',
         '- サザンアイランドは、なぞのばしょ [N1] の転記とも突き合わせました。',
         '- 商品の情報（発売日・シートの構成・英語版の配布など）は、主に Bulbapedia [X30][X31][X41]〜[X44] によります。',
         '- 確度（確実／有力／未確認）と出典の記号は [出典と確認状況](../sources.md) を参照。', '',
         '## 1. 拡張シート', '',
         '### 概要', '',
         '- 正式な商品名は「拡張シート」。英語圏の Vending Machine cards（自販機カード）はコレクターの通称です [X30]。**確実**',
         '- 自動販売機から出てくるシートで、カードをはがして使いました [X30]。1 シート 100 円 [X39]。**有力**',
         '- 各弾 18 種のシートがあり、シートには番号が付いていて、同じ番号のシートには必ず同じカードが入っています [X30][X43]。**確実**',
         '  - 青版・赤版: カード 3 枚と、厚紙のダメージカウンター・コイン。',
         '  - 緑版: カード 3 枚と、裏面の違うおまけのカード 1 枚（下記）。',
         '  - 18 種のシートをそろえると全カードがそろい、コモンの一部は 2 枚になります（18 シート × 3 枚 = 54 枠に 36 種）。',
         '- シートの裏はカントー地方の 6 つの場所を描いたもので、各場所に 3 シートずつあり、カードもその場所にちなんだポケモンです [X30][X43]。**確実**',
         '- カードは光沢のある紙に印刷され、カード番号はありません [X30]。下のカードリストの番号は pcg-search の並び順です。**確実**',
         '- 1997年12月の次世代ワールドホビーフェアで、先行版のシート（ピカチュウ、ミュウツー、ミュウ）が配られました。公式には番号なしのプロモで、ファンは「シリーズ 00」と呼ぶことがあります [X30]。**有力**',
         '- コロコロコミックのイラストコンテストの入賞作 4 点が、3 つの弾のカードのイラストに使われています（カビゴンなど）[X30][X41]。**有力**', '',
         '| 弾 | 発売日 | 収録 | レアリティ | 英語版になったカード |', '|---|---|---|---|---|']
    for p in sheets:
        cards = data[p['pcg_title']]
        main_cards = [c for c in cards if c['list_number'] != '-/-']
        extra = len(cards) - len(main_cards)
        rar = Counter(c['rarity'] for c in main_cards)
        en_n = sum(1 for c in cards if page_id(c) in en_prints)
        L.append('| {} | {} | {} 枚{} | ● {}・◆ {} | {} 枚 |'.format(
            p['name'], p['release_date'], len(main_cards), f'＋おまけ {extra} 種' if extra else '',
            rar.get('●', 0), rar.get('◆', 0), en_n))
    L += ['', '- 発売日・収録枚数は Bulbapedia [X30][X44] と pcg-search [N3] で一致します。**確実**',
          '- レアリティは pcg-search [N3] の記号です。Bulbapedia [X30] のコモン・アンコモンとも全カード一致しますが、青版の「化石の発掘」「月の石」だけは、pcg-search が ◆、Bulbapedia が「レアリティなし（拡張シートのトレーナーでこの 2 枚だけ）」としています。', '',
          '### シートの構成', '',
          'Bulbapedia [X43] によります。場所の名前はゲームの日本語名に置き換えたもので、シートの表記そのものではありません。', '']
    by_id = {page_id(c): c for p in sheets for c in data[p['pcg_title']]}
    for p in sheets:
        L += [f"#### {p['name']}", '', '| シート | 場所 | カード |', '|---|---|---|']
        for sh in cur['sheets'][p['pcg_title']]:
            names = [x[len('name:'):] if x.startswith('name:') else by_id[x]['name'] for x in sh['cards']]
            L.append(f"| {sh['sheet']} | {sh['area_ja']}（{sh['area_en']}） | {'、'.join(names)} |")
        L.append('')
    L += ['### 英語版になったカード', '',
          '拡張シートのカードの多くは日本でしか出ていません。英語版になったのは次の 6 枚で、どれも Wizards Black Star Promos です。WotC 期の英語版の全セット（e シリーズ、Legendary Collection、プロモを含む）と数値・ワザを突き合わせても、ほかに対応するカードはありませんでした [N3][X30][X41]。**確実**', '',
          '| 日本版 | 英語版 | 英語版の配布 | 備考 |', '|---|---|---|---|']
    for p in sheets:
        for c in data[p['pcg_title']]:
            e = en_prints.get(page_id(c))
            if e:
                L.append(f"| {c['name']}（{p['name']}） | {en_ref(e)} | {e.get('released', '')} {e.get('distribution', '')} | {md(e.get('note'))} |")
    L += ['', '日英の文面の違い:', '',
          '| カード | 種類 | 内容 | 日本版 | 英語版 | 確度 | 出典 |', '|---|---|---|---|---|---|---|']
    for p in sheets:
        for c in data[p['pcg_title']]:
            for d in diffs.get(page_id(c), []):
                L.append('| {} / {} | {} | {} | {} | {} | {} | {} |'.format(
                    c['name'], en_prints[page_id(c)]['name'], DIFF_KIND_JA[d['kind']], md(d['summary']), md(d['ja']), md(d['en']),
                    d['confidence'], ''.join(f'[{s}]' for s in d['sources'])))
    L += ['', '- 英語版は 2002年の書き方で、特殊能力が働かなくなる条件が「ねむり・マヒ・こんらん」から「特殊状態（Special Condition）」に変わっています。どく・やけどのときも働かなくなるので、意味が違います。',
          '- ピカチュウ・ブーバー・ストライク・エレブーの 4 枚は、日英の文面の意味に違いは見つかりませんでした。', '',
          '### 緑版のおまけカード', '']
    green = next(p for p in sheets if '緑版' in p['name'])
    groups = {}
    for c in data[green['pcg_title']]:
        if c['list_number'] == '-/-':
            groups.setdefault(c['kind'], []).append(c)
    labels = {'EXTRA RULE': 'おすすめルール（EXTRA RULE）', 'デッキ': 'デッキ（デッキレシピ）', 'PASS CARD': 'パスカード',
              'たねポケモン': 'ジョークカード（ポケモン）'}
    for kind, cs in groups.items():
        names = '、'.join(f"[{c['name']}]({c['url']})" if c['name'] != '-' else '（名前の記載なし）' for c in cs)
        L.append(f"- {labels.get(kind, kind)}（{len(cs)} 種）: {names}")
    L += ['',
          '- pcg-search で名前の記載がない 3 種は、Bulbapedia によると「イマクニ？のコーナー」「ハズレ？」「Pokémon Machine」で、どれも手描きのジョークカードです [X43]。**有力**',
          '- 「マサキのパソコン」は「通信進化キャンペーン」（1998-11-24〜1999-04-30）の応募用カードです。ユンゲラー・ゴーリキー・ゴローン・ゴースト・オムナイトのカードと一緒に送ると、進化後（フーディン・カイリキー・ゴローニャ・ゲンガー・オムスター）のキラのプロモカードがもらえました [X30][X43]。**確実**',
          '- おすすめルールのカードのうち「サイドカード4枚戦」「『こんらん』で20ダメージルール」は、当時の公式トーナメントで採用されていたと書かれています [N3]。ルールの資料では [日本版のルール](../rules/japanese.md) で使っています。',
          '- オーヤマのピカチュウはジョークカードで、ワザのダメージが「10ぐらい」となっています [N3]。', '',
          '### 対戦での扱い', '',
          '- 2001年の殿堂レギュレーションでは、ジム系のカードとともに拡張シートのカードは使えませんでした [J23]。**有力**', '']
    for p in sheets:
        L += [f"### カードリスト: {p['name']}", ''] + card_table(data[p['pcg_title']], en_prints) + ['']

    si_cards = data[SI]
    L += ['## 2. 映画公開記念パック「サザンアイランド」', '',
          '### 概要', '',
          f"- 商品名は映画公開記念パック「サザンアイランド」。発売は {si_meta['release_date']}（劇場版『幻のポケモン ルギア爆誕』の公開日）[X31][X44]。**確実**",
          '  - 3 枚入り 200 円（税別）で、夏の期間限定の商品でした [J24]。**有力**',
          '- 「トロピカルアイランド」と「レインボーアイランド」の 2 つのコレクションがあり、それぞれ 3 つの場所の 3 枚組があります [N3][X31]。**確実**',
          '  - 3 枚を並べると 1 枚の風景画になり、そのうち 1 枚がキラです。場所ごとのポストカードも付いていました。',
          '  - 映画の公開に合わせて、9 枚ずつのファイル（コレクション）で出たほか、3 枚組の箱入りでも売られました [X31]。**有力**',
          '  - イラストは、トロピカルアイランドが Naoyo Kimura、レインボーアイランドが Keiko Fukuyama [X31][N3]。**確実**',
          '- 日本版は番号もレアリティマークもなく、旧裏（第1弾〜ロケット団）の形のカードです。金・銀の世代のポケモン（トゲピー、マリル、ヤドキング、レディバ）が旧裏の形で出たのはこの商品だけです [X31]。**確実**',
          '  - この 4 枚には図鑑番号が印刷されていません [N1]。**有力**',
          '- 英語版 Southern Islands（2001-07-31）は同じ 18 枚を 1 つのセットにしたもので、1〜18 の番号があり、カードは Neo の形です [X31]。**確実**', '',
          '| コレクション | 場所 | カード（★ はキラ） | 英語版の番号 |', '|---|---|---|---|']
    packs = {}
    for c in si_cards:
        packs.setdefault(c['remarks'], []).append(c)
    for remark, cs in packs.items():
        coll, place = remark.split(' ', 1)
        names = '、'.join(c['name'] + ('★' if 'キラ' in (c['rarity'] or '') else '') for c in cs)
        nums = '・'.join(en_prints[page_id(c)]['number'] for c in cs)
        L.append(f'| {coll} | {place} | {names} | {nums} |')
    L += ['', 'キラの位置は pcg-search [N3]、英語版の番号との対応は Bulbapedia [X31] と英語版データによります。', '',
          '### カードリスト', '',
          '| カード名 | 種類 | LV | タイプ | HP | 弱点 | 抵抗力 | にげる | 英語版 |', '|---|---|---|---|---|---|---|---|---|']
    for c in si_cards:
        z = nz.get(c['name'], {}).get('fields', {})
        L.append('| [{}]({}) | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            c['name'], c['url'], kind_short(c), z.get('LV.', ''), c.get('type') or '', c.get('hp') or '',
            c.get('weakness') or '', c.get('resistance') or '', len(c.get('retreat') or ''), en_ref(en_prints.get(page_id(c)))))
    L += ['', 'LV はなぞのばしょ [N1]、ほかは pcg-search [N3] の記載です。', '',
          '### 日英の違い', '',
          '| カード | 種類 | 内容 | 日本版 | 英語版 | 確度 | 出典 |', '|---|---|---|---|---|---|---|']
    for c in si_cards:
        for d in diffs.get(page_id(c), []):
            L.append('| {} / {} | {} | {} | {} | {} | {} | {} |'.format(
                c['name'], en_prints[page_id(c)]['name'], DIFF_KIND_JA[d['kind']], md(d['summary']), md(d['ja']), md(d['en']),
                d['confidence'], ''.join(f'[{s}]' for s in d['sources'])))
    L += ['', '### 2 つの転記の食い違い', '',
          'pcg-search [N3] となぞのばしょ [N1] の転記を、カード名・HP・ワザ名・ダメージで突き合わせた結果です。効果文の細かな表記の揺れ（「受けない」と「うけない」など）は除いています。', '',
          '| カード | 項目 | なぞのばしょ | pcg-search |', '|---|---|---|---|']
    for row in transcription_diffs(si_cards, nz):
        L.append('| {} | {} | {} | {} |'.format(*(md(str(x)) for x in row)))
    L += ['', '- ダメージは、2 件とも英語版の値（30、20）と pcg-search 側が一致します。',
          '- ワザ名は「のびるベロ」が正しく、pcg-search 側の誤記です。',
          '- 弱点・抵抗力・にげるは、3 つの資料（2 つの転記と英語版）で全カード一致しました。', '',
          '## まだ確認できていないこと', '',
          '- 拡張シートの自動販売機の種類（バンダイの「ジャンボカードダス」とする情報があるが未確認）',
          '- 青版の「化石の発掘」「月の石」のレアリティマークの有無（pcg-search と Bulbapedia で食い違い）',
          '- サザンアイランドの販売場所（映画館だけだったか）と、ファイル版と 3 枚組の箱の関係', '']
    (ROOT / 'docs' / 'cards' / 'other-products.md').write_text('\n'.join(L), encoding='utf-8')
    print(sum(len(v) for v in data.values()), 'cards')


if __name__ == '__main__':
    main()
