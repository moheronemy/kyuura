#!/usr/bin/env python3
"""拡張パック以外の旧裏の商品のページを生成する。

対象: 拡張シート第1〜3弾、映画公開記念パック「サザンアイランド」、ポケモンジムの構築済みデッキ 6 種、
クイックスターターギフト、neo プレミアムファイル 1〜3、プロモーションカード。

入力: data/ja_text_pcgsearch.json（pcg-search.com から抽出）、data/ja_text_nazonobasho.json（サザンアイランドのレベル・備考）、
      data/cards.json（拡張パックと同じカードかの判定）、data/curation/other_products.json（発売日・構成・英語版の対応・日英の違い）、
      data/curation/sets.json（拡張パックの発売日）
出力: docs/cards/other-products.md（一覧）と docs/cards/products/*.md（商品ごと）

使い方: python3 scripts/build_other_products.py
"""
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'cards'
SI = '映画公開記念パック「サザンアイランド」'
DIFF_KIND_JA = {'text': '文面の意味', 'numbers': '数値', 'print': '英語版の表記・誤植', 'wording': '書き方（意味は同じ）', 'art': 'イラスト'}
GENERATED = ('<!-- このファイルは scripts/build_other_products.py が data/ja_text_pcgsearch.json と '
             'data/curation/other_products.json から生成しています。直接編集しないでください。 -->')
# サイトの表記の揺れ（カード名の照合だけに使う）
NAME_FIX = {'ウィンディ': 'ウインディ'}
# 商品のまとまり: (ページのファイル名, 見出し, pcg-search のキーの条件)
PAGES = [
    ('expansion-sheets', '拡張シート', 'expansion_sheet'),
    ('southern-islands', '映画公開記念パック「サザンアイランド」', 'southern_islands'),
    ('gym-decks', 'ポケモンジム（構築済みデッキ）', 'gym_deck'),
    ('quick-starter-gift', 'クイックスターターギフト', 'quick_starter_gift'),
    ('premium-files', 'neo プレミアムファイル', 'premium_file'),
    ('promos', 'プロモーションカード', 'promo'),
]


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def md(s):
    return (s or '').replace('|', '\\|').replace('\n', '<br>')


def page_id(card):
    return card['url'].rsplit('/', 1)[-1].removesuffix('.php')


def digits(s):
    return re.sub(r'\D', '', s or '')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    for a, b in NAME_FIX.items():
        s = s.replace(a, b)
    return re.sub(r'[\s\[\]・,、]', '', s).replace('?', '？')


def en_ref(e):
    return f"{e['set_name']} {e['number']}（{e['name']}）" if e else ''


def kind_short(card):
    k = card['kind'].replace('１', '1').replace('２', '2')
    return {'たねポケモン': 'たね', '1進化ポケモン': '1進化', '2進化ポケモン': '2進化'}.get(k, k)


def sig_pcg(c):
    """同じカードかを判定する鍵。ポケモンは名前・HP・特殊能力名・ワザ名、ほかは名前。"""
    if c.get('hp'):
        return (norm(c['name']), c['hp'], tuple(norm(x['name']) for x in c['powers']),
                tuple(norm(a['name']) for a in c['attacks']))
    return (norm(c['name']),)


def sig_record(r):
    p = r['pokemon']
    if p:
        return (norm(r['name']['ja']), p['hp'], tuple(norm(x['name']['ja']) for x in p['powers']),
                tuple(norm(a['name']['ja']) for a in p['attacks']))
    return (norm(r['name']['ja']),)


class Catalog:
    """全商品（拡張パック 10 弾と pcg-search の商品）のカードを、同じカードごとにまとめる。"""

    def __init__(self):
        self.data = load('data/ja_text_pcgsearch.json')['products']
        self.cur = load('data/curation/other_products.json')
        self.records = load('data/cards.json')['cards']
        sets = load('data/curation/sets.json')
        self.products = {p['pcg_title']: p for p in self.cur['products']}
        self.promo_info = self.cur.get('promos', {})
        self.groups = {}
        for r in self.records:
            m = re.match(r'(\d+)年(\d+)月(\d+)日', sets[r['jp_set']]['release'])
            date = f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
            label = f"{sets[r['jp_set']]['label']} {sets[r['jp_set']]['ja']}"
            self.groups.setdefault(sig_record(r), []).append({'date': date, 'product': label, 'record': r})
        for key, cards in self.data.items():
            for c in cards:
                self.groups.setdefault(sig_pcg(c), []).append(
                    {'date': self.date_of(key, c), 'product': self.short_name(key), 'card': c, 'key': key})

    def short_name(self, key):
        return self.products[key]['name'] if key in self.products else key

    def date_of(self, key, c):
        info = self.promo_info.get(page_id(c))
        if info and info.get('date'):
            return info['date']
        return (self.products.get(key) or {}).get('release_date')

    def same(self, c):
        """同じカードが入っているほかの商品（自分以外）。"""
        return [g for g in self.groups.get(sig_pcg(c), []) if g.get('card') is not c]

    def pack_record(self, c):
        return next((g['record'] for g in self.same(c) if 'record' in g), None)

    def en(self, c):
        e = self.cur['en_prints'].get(page_id(c))
        if e:
            return en_ref(e)
        r = self.pack_record(c)
        if r and r['en_print']:
            return f"{r['en_print']['set_name']} {r['en_print']['numbers'][0]}（{r['name']['en']}）"
        return ''

    def appears(self, c):
        """同じカードの、ほかの商品での収録（発売日順）。"""
        seen, out = set(), []
        for g in sorted(self.same(c), key=lambda g: g['date'] or '9999'):
            label = g['product'] + (f"（{g['date']}）" if g['date'] else '')
            if label not in seen:
                seen.add(label)
                out.append(label)
        return out

    def first(self, c, key):
        """このカードの日本での初出が、この商品か。"""
        mine = self.date_of(key, c)
        others = [g['date'] for g in self.same(c) if g['date']]
        return bool(mine) and all(mine <= d for d in others)


def card_table(cat, cards, key, qty=None, en_prints=None):
    head = '| 番号 | カード名 | 種類 | タイプ | HP | レア |' + (' 枚数 |' if qty else '') + ' 英語版 | ほかの収録 |'
    lines = [head, '|' + '---|' * (head.count('|') - 1)]
    for c in cards:
        row = [c['list_number'], f"[{md(c['name'])}]({c['url']})", kind_short(c), c.get('type') or '', str(c.get('hp') or ''),
               c['rarity'] if c['rarity'] not in (None, '-') else '']
        if qty:
            row.append(str(qty.get(page_id(c), '')))
        row += [cat.en(c), '<br>'.join(cat.appears(c))]
        lines.append('| ' + ' | '.join(row) + ' |')
    return lines


def diff_rows(cat, cards):
    rows = []
    for c in cards:
        for d in cat.cur['differences'].get(page_id(c), []):
            e = cat.cur['en_prints'].get(page_id(c), {})
            rows.append('| {} / {} | {} | {} | {} | {} | {} | {} |'.format(
                c['name'], e.get('name', ''), DIFF_KIND_JA[d['kind']], md(d['summary']), md(d['ja']), md(d['en']),
                d['confidence'], ''.join(f'[{s}]' for s in d['sources'])))
    return rows


def header(title, depth=1):
    up = '../' * depth
    return [f'# {title}', '', GENERATED, '',
            f'[拡張パック以外の商品の一覧](../other-products.md) ／ 出典の記号: [出典と確認状況]({up}../sources.md)', '',
            '- カードの欄（名前・HP・ワザなど）は、ポケモンカード 旧シリーズ検索（pcg-search.com）[N3] の転記です。カード名から各カードのページにリンクしています。',
            '- 「番号」は pcg-search の並び順で、カードに印刷された番号ではありません。',
            '- 「ほかの収録」は、名前（ポケモンは HP・特殊能力名・ワザ名も）が同じカードが入っているほかの商品です（拡張パック 10 弾と、このページ群の商品）。', '']


def keys_of(cat, group):
    return [k for k, p in cat.products.items() if p.get('group') == group and k in cat.data]


# ---- 拡張シート -----------------------------------------------------------

def page_expansion_sheets(cat):
    cur, data = cat.cur, cat.data
    en_prints, sheets = cur['en_prints'], [cat.products[k] for k in keys_of(cat, 'expansion_sheet')]
    L = header('拡張シート') + [
        '## 概要', '',
        '- 正式な商品名は「拡張シート」。英語圏の Vending Machine cards（自販機カード）はコレクターの通称です [X30]。**確実**',
        '- 自動販売機から出てくるシートで、カードをはがして使いました [X30]。1 シート 100 円 [X39]。**有力**',
        '- 各弾 18 種のシートがあり、シートには番号が付いていて、同じ番号のシートには必ず同じカードが入っています [X30][X43]。**確実**',
        '  - 青版・赤版: カード 3 枚と、厚紙のダメージカウンター・コイン。',
        '  - 緑版: カード 3 枚と、裏面の違うおまけのカード 1 枚（下記）。',
        '  - 18 種のシートをそろえると全カードがそろい、コモンの一部は 2 枚になります（18 シート × 3 枚 = 54 枠に 36 種）。',
        '- シートの裏はカントー地方の 6 つの場所を描いたもので、各場所に 3 シートずつあり、カードもその場所にちなんだポケモンです [X30][X43]。**確実**',
        '- カードは光沢のある紙に印刷され、カード番号はありません [X30]。**確実**',
        '- 1997年12月の次世代ワールドホビーフェアで、先行版のシート（ピカチュウ、ミュウツー、ミュウ）が配られました。公式には番号なしのプロモで、ファンは「シリーズ 00」と呼ぶことがあります [X30]。**有力**',
        '- コロコロコミックのイラストコンテストの入賞作 4 点が、3 つの弾のカードのイラストに使われています（カビゴンなど）[X30][X41]。**有力**',
        '- 拡張シートのカードは、クイックスターターギフト（1998年12月）に光沢なし・レアリティマークなしで再録されました' +
        ('（[クイックスターターギフト](quick-starter-gift.md)）。' if keys_of(cat, 'quick_starter_gift') else '。'), '',
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
          '## シートの構成', '',
          'Bulbapedia [X43] によります。場所の名前はゲームの日本語名に置き換えたもので、シートの表記そのものではありません。', '']
    by_id = {page_id(c): c for p in sheets for c in data[p['pcg_title']]}
    for p in sheets:
        L += [f"### {p['name']}", '', '| シート | 場所 | カード |', '|---|---|---|']
        for sh in cur['sheets'][p['pcg_title']]:
            names = [x[len('name:'):] if x.startswith('name:') else by_id[x]['name'] for x in sh['cards']]
            L.append(f"| {sh['sheet']} | {sh['area_ja']}（{sh['area_en']}） | {'、'.join(names)} |")
        L.append('')
    L += ['## 英語版になったカード', '',
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
        L += diff_rows(cat, data[p['pcg_title']])
    L += ['', '- 英語版は 2002年の書き方で、特殊能力が働かなくなる条件が「ねむり・マヒ・こんらん」から「特殊状態（Special Condition）」に変わっています。どく・やけどのときも働かなくなるので、意味が違います。',
          '- ピカチュウ・ブーバー・ストライク・エレブーの 4 枚は、日英の文面の意味に違いは見つかりませんでした。', '',
          '## 緑版のおまけカード', '']
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
          '- おすすめルールのカードのうち「サイドカード4枚戦」「『こんらん』で20ダメージルール」は、当時の公式トーナメントで採用されていたと書かれています [N3]。ルールの資料では [日本版のルール](../../rules/japanese.md) で使っています。',
          '- オーヤマのピカチュウはジョークカードで、ワザのダメージが「10ぐらい」となっています [N3]。', '',
          '## 対戦での扱い', '',
          '- 2001年の殿堂レギュレーションでは、ジム系のカードとともに拡張シートのカードは使えませんでした [J23]。**有力**', '']
    for p in sheets:
        L += [f"## カードリスト: {p['name']}", ''] + card_table(cat, data[p['pcg_title']], p['pcg_title']) + ['']
    return L


# ---- サザンアイランド ------------------------------------------------------

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


def page_southern_islands(cat):
    en_prints = cat.cur['en_prints']
    si_meta = cat.products[SI]
    si_cards = cat.data[SI]
    nz = {c['fields']['カード名称']: c for c in
          load('data/ja_text_nazonobasho.json')['sets']['cardlist-pmcg-southernisland']['cards']}
    L = header('映画公開記念パック「サザンアイランド」') + [
        '- サザンアイランドは、なぞのばしょ [N1] の転記とも突き合わせました。', '',
        '## 概要', '',
        f"- 劇場版『幻のポケモン ルギア爆誕』の公開日 {si_meta['release_date']} に、2 種類の商品で出ました [X31][X44][X46]。**確実**",
        '  - 映画公開記念パック「サザンアイランド」: 3 枚入りの箱で 6 種類。場所ごとのポストカード付き。3 枚入り 200 円（税別）[J24]。',
        '  - 「サザンアイランド」映画公開記念セット: 上映館だけで売られた、9 枚入りのファイル。トロピカルアイランドとレインボーアイランドの 2 種類 [X46]。',
        '  - パックは夏の期間限定の商品でした [J24]。**有力**',
        '- 「トロピカルアイランド」と「レインボーアイランド」の 2 つのコレクションに、それぞれ 3 つの場所の 3 枚組があります。3 枚を並べると 1 枚の風景画になり、そのうち 1 枚がキラです [N3][X31]。**確実**',
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
          '## カードリスト', '',
          '| カード名 | 種類 | LV | タイプ | HP | 弱点 | 抵抗力 | にげる | 英語版 |', '|---|---|---|---|---|---|---|---|---|']
    for c in si_cards:
        z = nz.get(c['name'], {}).get('fields', {})
        L.append('| [{}]({}) | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            c['name'], c['url'], kind_short(c), z.get('LV.', ''), c.get('type') or '', c.get('hp') or '',
            c.get('weakness') or '', c.get('resistance') or '', len(c.get('retreat') or ''), en_ref(en_prints.get(page_id(c)))))
    L += ['', 'LV はなぞのばしょ [N1]、ほかは pcg-search [N3] の記載です。', '',
          '## 日英の違い', '',
          '| カード | 種類 | 内容 | 日本版 | 英語版 | 確度 | 出典 |', '|---|---|---|---|---|---|---|']
    L += diff_rows(cat, si_cards)
    L += ['', '## 2 つの転記の食い違い', '',
          'pcg-search [N3] となぞのばしょ [N1] の転記を、カード名・HP・ワザ名・ダメージで突き合わせた結果です。効果文の細かな表記の揺れ（「受けない」と「うけない」など）は除いています。', '',
          '| カード | 項目 | なぞのばしょ | pcg-search |', '|---|---|---|---|']
    for row in transcription_diffs(si_cards, nz):
        L.append('| {} | {} | {} | {} |'.format(*(md(str(x)) for x in row)))
    L += ['', '- ダメージは、2 件とも英語版の値（30、20）と pcg-search 側が一致します。',
          '- ワザ名は「のびるベロ」が正しく、pcg-search 側の誤記です。',
          '- 弱点・抵抗力・にげるは、3 つの資料（2 つの転記と英語版）で全カード一致しました。', '']
    return L


# ---- ポケモンジム ---------------------------------------------------------

def page_gym_decks(cat):
    keys = keys_of(cat, 'gym_deck')
    L = header('ポケモンジム（構築済みデッキ）') + [
        '## 概要', '',
        '- ジムリーダーとその「〇〇の」ポケモンを使う構築済みデッキで、日本だけで 6 種類出ました [X46]。**確実**',
        '- 各デッキは 64 枚で、60 枚のデッキと、入れ替えて使う「拡張カード」4 枚。ほかにコイン、ルールブック、「ポケモンジムガイド」などが入っていました [X46]。**確実**',
        '- 拡張パック「リーダーズスタジアム」（1998-10-24）・「闇からの挑戦」（1999-06-25）に先立って出ており、デッキのカードの一部はその後の拡張パックにも収録されました。',
        '- 英語版では、デッキにしかなかったカードは Gym Heroes・Gym Challenge に入れられ、デッキの中身は英語版のテーマデッキ（Brock、Misty など）の元になりました [X46]。**確実**',
        '  - デッキで決まったレアリティのまま英語版のセットに入ったため、Gym Heroes にはタケシのイワークなどの「コモンなのにレア」のカードがあります [X46]。**有力**', '',
        '| デッキ | 発売日 | 枚数 | カードの種類 | デッキで初めて出たカード | 英語版のテーマデッキ |', '|---|---|---|---|---|---|']
    theme = {'タケシ': 'Brock', 'カスミ': 'Misty', 'マチス': 'Lt. Surge', 'エリカ': 'Erika', 'ナツメ': 'Sabrina', 'カツラ': 'Blaine'}
    for k in keys:
        cards = cat.data[k]
        deck = cat.cur['decks'][k]
        total = sum(e['qty'] for e in deck['cards']) + sum(e['qty'] for e in deck['basic_energy'])
        new = sum(1 for c in cards if cat.first(c, k))
        leader = next(v for j, v in theme.items() if j in k)
        L.append(f"| {cat.short_name(k)} | {cat.products[k]['release_date']} | {total} | {len(cards)}（基本エネルギーを除く） | {new} | {leader} |")
    L += ['', '- 発売日・枚数・デッキリストは Bulbapedia [X46] によります。カードの欄は pcg-search [N3]。',
          '- デッキの各カードが英語版のどのカードになったかは、Bulbapedia のデッキのカードのページ（英語版のカードへの転送）と、カードの数値・ワザの照合の両方で確かめ、全カード一致しました。**確実**', '']
    for k in keys:
        deck = cat.cur['decks'][k]
        qty = {e['page']: e['qty'] for e in deck['cards']}
        L += [f"## {cat.short_name(k)}", '', f"発売日 {cat.products[k]['release_date']}。", '']
        L += card_table(cat, cat.data[k], k, qty=qty)
        L += ['', '基本エネルギー: ' + '、'.join(f"{e['name']} {e['qty']} 枚" for e in deck['basic_energy']), '']
    return L


# ---- クイックスターターギフト ----------------------------------------------

def page_quick_starter_gift(cat):
    k = keys_of(cat, 'quick_starter_gift')[0]
    q = cat.cur.get('quick_starter_gift', {})
    L = header('クイックスターターギフト') + [
        '## 概要', '',
        f"- 2 人ですぐに対戦できるセットで、{cat.products[k]['release_date']} 発売 [X46]。**確実**",
        '- 「赤デッキ」と「緑デッキ」の 2 つのデッキ（名前はゲームの『赤』『緑』から）、デッキケース 2 個、ダメージカウンター、どくマーカー、コイン 2 枚、プレイマット、ルールブック、拡張シート第1弾（青版）1 シート、『すぐわかる ポケモンカードの遊びかた 最新版』が入っていました [X46]。**確実**',
        '- デッキのカードは、すべて既に出たカードの再録で、ほとんどが拡張シートのカードです。拡張シートと違って光沢のない紙で、レアリティマークがありません [X46]。**確実**',
        '  - ストライク、ファイヤー、サンダー、フリーザー、マスターボールは、この商品だけのキラ版です（拡張シートではキラでない）[X46]。**確実**', '']
    if q:
        L += ['| デッキ | 主なタイプ | 枚数 |', '|---|---|---|']
        for d in ('red', 'green'):
            deck = q[d]
            total = sum(e['qty'] for e in deck['cards']) + sum(e['qty'] for e in deck['basic_energy'])
            L.append(f"| {deck['name']} | {deck['types']} | {total} |")
        L.append('')
    L += ['## カードリスト', '']
    qty = {}
    for d in ('red', 'green'):
        for e in q.get(d, {}).get('cards', []):
            qty.setdefault(e['page'], []).append(f"{q[d]['name'][0]}{e['qty']}")
    qty = {k2: '・'.join(v) for k2, v in qty.items()}
    L += card_table(cat, cat.data[k], k, qty=qty if qty else None)
    if qty:
        L += ['', '枚数の「赤」「緑」は、赤デッキ・緑デッキの枚数（Bulbapedia [X46] のデッキリストによる）。']
        for d in ('red', 'green'):
            L.append(f"- {q[d]['name']}の基本エネルギー: " + '、'.join(f"{e['name']} {e['qty']} 枚" for e in q[d]['basic_energy']))
    L.append('')
    return L


# ---- プレミアムファイル -----------------------------------------------------

def page_premium_files(cat):
    keys = keys_of(cat, 'premium_file')
    L = header('neo プレミアムファイル') + [
        '## 概要', '',
        '- 『金・銀』の発売などに合わせて出た、9 枚のカードとファイルのセットです。3 種類あります [X47]。**確実**',
        '- 英語版では、9 枚ずつが Neo Genesis・Neo Discovery・Neo Revelation に入れられました（Neo Discovery は 5 枚）[X29][X47]。**確実**', '',
        '| 商品 | 発売日 | 内容 | 英語版 |', '|---|---|---|---|',
        '| プレミアムファイル | 1999-12-10 | 金・銀の最初のポケモン 3 匹とその進化形の 9 枚。カードの本付き | Neo Genesis |',
        '| プレミアムファイル2 | 2000-07-08（上映館）、2000-08-05（一般） | 『結晶塔の帝王 ENTEI』関連のリザードン・エンテイ・ピチューなど 9 枚。3 枚はコスモ柄の反転キラ | Neo Discovery |',
        '| プレミアムファイル3 | 2000-11-23 | ルギア・ホウオウ・セレビィ・エンテイ・ライコウ・スイクンなど、全タイプの 9 枚 | Neo Revelation |', '',
        '発売日と内容は Bulbapedia [X47] によります。**確実**', '']
    for k in keys:
        L += [f"## {cat.short_name(k)}", ''] + card_table(cat, cat.data[k], k) + ['']
    return L


# ---- プロモ ---------------------------------------------------------------

def page_promos(cat):
    keys = keys_of(cat, 'promo')
    L = header('プロモーションカード') + [
        '## 概要', '',
        '- 旧裏期のプロモカードには番号がなく、雑誌の付録、キャンペーン、大会の賞品、映画、本・CD の付録などで配られました [X48]。**確実**',
        '- 配布方法と時期は、Bulbapedia の日本の番号なしプロモの一覧 [X48] と突き合わせたものです。突き合わせられなかったカードは空欄にしています。',
        '- 拡張パック・ジムデッキなどと同じカードのプロモ（イラストやマークが違うだけのもの）は、「ほかの収録」に載せています。', '']
    for k in keys:
        cards = cat.data[k]
        L += [f"## {cat.short_name(k)}", '',
              '| 番号 | カード名 | 種類 | HP | 配布 | 英語版 | ほかの収録 |', '|---|---|---|---|---|---|---|']
        for c in cards:
            info = cat.promo_info.get(page_id(c), {})
            dist = md(info.get('distribution', ''))
            if info.get('date'):
                dist = f"{info['date']} {dist}"
            L.append('| {} | [{}]({}) | {} | {} | {} | {} | {} |'.format(
                c['list_number'], md(c['name']), c['url'], kind_short(c), c.get('hp') or '', dist, cat.en(c),
                '<br>'.join(cat.appears(c))))
        L.append('')
    return L


# ---- 一覧 -----------------------------------------------------------------

def page_index(cat):
    L = ['# 拡張パック以外の商品', '', GENERATED, '',
         '旧裏期に日本で出た、拡張パック 10 弾以外の商品のカードをまとめたページ群です。',
         'これらのカードは拡張パックのデータ（`data/cards.json`）には入れず、`data/ja_text_pcgsearch.json` に収録しています。', '',
         '- カードの欄は、ポケモンカード 旧シリーズ検索（pcg-search.com）[N3] の転記です。',
         '- 商品の情報（発売日・構成・英語版の配布など）は、主に Bulbapedia [X30][X31][X41]〜[X48] によります（MediaWiki の API でページの原文を取得して確認）。',
         '- 確度（確実／有力／未確認）と出典の記号は [出典と確認状況](../sources.md) を参照。', '',
         '| 商品 | 発売 | カード | 英語版 | ページ |', '|---|---|---|---|---|']
    rows = {
        'expansion_sheet': ('1998-03〜1998-11', '英語版になったのは 6 枚（Wizards Black Star Promos）'),
        'southern_islands': ('1999-07-17', 'Southern Islands（2001）の 18 枚'),
        'gym_deck': ('1998-04〜1999-02', 'デッキにしかなかったカードは Gym Heroes・Gym Challenge へ'),
        'quick_starter_gift': ('1998-12-04', '再録だけ'),
        'premium_file': ('1999-12〜2000-11', 'Neo Genesis・Discovery・Revelation へ'),
        'promo': ('1996〜2001', '一部が Wizards Black Star Promos など'),
    }
    for slug, title, group in PAGES:
        keys = keys_of(cat, group)
        if not keys:
            continue
        n_cards = sum(len(cat.data[k]) for k in keys)
        date, en = rows[group]
        L.append(f"| {title}（{len(keys)} 種）| {date} | {n_cards} 種 | {en} | [{slug}.md](products/{slug}.md) |")
    L += ['', '英語版にあって日本の拡張パックにないカードの、日本での初出は [英語版のみに見られるカード](english-only.md) にあります。', '',
          '## まだ確認できていないこと', '',
          '- 拡張シートの自動販売機の種類（バンダイの「ジャンボカードダス」とする情報があるが未確認）',
          '- 青版の「化石の発掘」「月の石」のレアリティマークの有無（pcg-search と Bulbapedia で食い違い）',
          '- サザンアイランドの 3 枚入りパックの販売場所（ファイル版は上映館だけ）']
    if keys_of(cat, 'promo'):
        L.append('- プロモカードのうち、配布方法を突き合わせられなかったもの（[プロモーションカード](products/promos.md) で空欄のもの）')
    L.append('')
    return L


def main():
    cat = Catalog()
    (OUT / 'products').mkdir(exist_ok=True)
    builders = {'expansion-sheets': page_expansion_sheets, 'southern-islands': page_southern_islands,
                'gym-decks': page_gym_decks, 'quick-starter-gift': page_quick_starter_gift,
                'premium-files': page_premium_files, 'promos': page_promos}
    for slug, title, group in PAGES:
        if keys_of(cat, group):
            (OUT / 'products' / f'{slug}.md').write_text('\n'.join(builders[slug](cat)), encoding='utf-8')
    (OUT / 'other-products.md').write_text('\n'.join(page_index(cat)), encoding='utf-8')
    print(sum(len(v) for v in cat.data.values()), 'cards')


if __name__ == '__main__':
    main()
