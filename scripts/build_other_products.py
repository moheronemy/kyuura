#!/usr/bin/env python3
"""拡張パック以外の旧裏の商品のページを生成する。

対象: 拡張シート第1〜3弾、映画公開記念パック「サザンアイランド」、ポケモンジムの構築済みデッキ 6 種、
クイックスターターギフト、イントロパック・イントロパック★neo、neo プレミアムファイル 1〜3、プロモーションカード。
あわせて、商品をまたいだ同じカード（再録）の判定のしかたと点検の結果のページ（docs/cards/reprints.md）を作る。

入力: data/ja_text_pcgsearch.json（pcg-search.com から抽出）、data/ja_text_nazonobasho.json（サザンアイランドのレベル・備考）、
      data/cards.json（拡張パックと同じカードかの判定）、data/curation/other_products.json（発売日・構成・英語版の対応・日英の違い）、
      data/curation/sets.json（拡張パックの発売日）
      data/curation/en_fixes.json（英語版データの補正。再録の点検のページに載せる）
出力: docs/cards/other-products.md（一覧）、docs/cards/products/*.md（商品ごと）、docs/cards/reprints.md（再録の対応付け）

使い方: python3 scripts/build_other_products.py
"""
import difflib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'cards'
SI = '映画公開記念パック「サザンアイランド」'
DIFF_KIND_JA = {'text': '文面の意味', 'numbers': '数値', 'print': '英語版の表記・誤植', 'wording': '書き方（意味は同じ）', 'art': 'イラスト',
                'errata': 'エラッタ'}
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
    ('intro-packs', 'イントロパック・イントロパック★neo', 'intro_pack'),
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
        self.key_of = {}
        for key, cards in self.data.items():
            for c in cards:
                self.key_of[id(c)] = key
                label = 'プロモ' if (self.products.get(key) or {}).get('group') == 'promo' else self.short_name(key)
                self.groups.setdefault(sig_pcg(c), []).append(
                    {'date': self.date_of(key, c), 'product': label, 'card': c, 'key': key})

    def display_name(self, c):
        """pcg-search で名前が「-」のカードは、data/curation/other_products.json の identified_cards の名前を使う。"""
        ident = self.cur.get('identified_cards', {}).get(page_id(c))
        return ident['name'] if c['name'] == '-' and ident else c['name']

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
        for g in sorted(self.same(c), key=lambda g: g['date'] or '9999'):  # 同じカードのほかの商品の版
            e = 'card' in g and self.cur['en_prints'].get(page_id(g['card']))
            if e:
                return en_ref(e)
        return ''

    def products_of(self, sig):
        """同じカードが入っている商品（発売日順、重複なし）。"""
        seen, out = set(), []
        for g in sorted(self.groups.get(sig, []), key=lambda g: g['date'] or '9999'):
            if g['product'] not in seen:
                seen.add(g['product'])
                out.append((g['date'], g['product']))
        return out

    def appears(self, c):
        """同じカードの、ほかの商品での収録（発売日順）。同じデッキの中の同じカードは除く（プロモは配布ごとに別なので残す）。"""
        seen, out = set(), []
        key = self.key_of.get(id(c))
        promo = (self.products.get(key) or {}).get('group') == 'promo'
        for g in sorted(self.same(c), key=lambda g: g['date'] or '9999'):
            if g.get('key') == key and not promo:
                continue
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


MONTHS = {m: i for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                                       'October', 'November', 'December'], 1)}
DIST_JA = [  # Bulbapedia の配布の記載 → 日本語（言い回しが確かなものだけ。ほかは英語のまま）
    (r'(?:Gekkan )?CoroCoro Comic (\w+) (\d{4}) issue insert', lambda m: f'月刊コロコロコミック {m[2]}年{MONTHS[m[1]]}月号の付録'),
    (r'Bessatsu CoroCoro Comic Special (\w+) (\d{4}) issue insert', lambda m: f'別冊コロコロコミックスペシャル {m[2]}年{MONTHS[m[1]]}月号の付録'),
    (r'Pokémon Card Trainers Vol\. (\d+) insert', lambda m: f'『ポケモンカード トレーナーズ』Vol.{m[1]} の付録'),
    (r'How I Became a Pokémon Card Vol\. (\d+) insert', lambda m: f'『ポケモンカードになったワケ』{m[1]} 巻の付録'),
    (r'Pokémon Card Fan Club Vol\. (\d+)(?: insert)?', lambda m: f'ポケモンカードファンクラブ会報 Vol.{m[1]}'),
    (r'Pokémon Card Fan Club (\d+) GET point prize', lambda m: f'ポケモンカードファンクラブ {m[1]} GET ポイントの景品'),
    (r'Easily Understand How to Play Pokémon Cards: Latest Edition', lambda m: '『すぐわかるポケモンカードの遊びかた 最新版』の付録'),
    (r'Easily Understand How to Play Pokémon Cards', lambda m: '『すぐわかるポケモンカードの遊びかた』の付録'),
    (r'All Nippon Airlines (".*?")(?: campaign)?(?: phase (\d))?', lambda m: f'全日空（ANA）のキャンペーン {m[1]}' + (f' 第{m[2]}期' if m[2] else '')),
    (r'World Hobby Fair Special Limited Expansion Sheet', lambda m: '次世代ワールドホビーフェアの限定拡張シート'),
    (r'World Hobby Fair 2000 commemoration card', lambda m: 'ワールドホビーフェア 2000 の記念カード'),
    (r'Champion Road 2000 participation prize', lambda m: 'チャンピオンロード 2000 の参加賞'),
    (r'New Garura Parent/Child Tournament participation prize', lambda m: '新ガルーラ親子大会の参加賞'),
    (r'Tropical Mega Battle finals participation prize', lambda m: 'トロピカルメガバトル決勝大会の参加賞'),
    (r'Toyota campaign', lambda m: 'トヨタのキャンペーン'),
    (r'Nintendo 64 Double Get Campaign', lambda m: 'NINTENDO64 ダブルゲットキャンペーン'),
    (r'Trade Please campaign', lambda m: '「とりかえっこプリーズ」キャンペーン'),
    (r'Pokémon Song Best Collection CD insert', lambda m: 'CD『ポケモンソング ベストコレクション』の付録'),
    (r'Pokémon Card GB Official Guidebook insert', lambda m: '『ポケモンカードGB 公式ガイドブック』の付録'),
    (r'Pokémon Trading Card Game 2: The Invasion of Team GR! insert|Pokémon Card GB2: Here Comes Team GR! insert', lambda m: 'ゲームボーイ『ポケモンカードGB2 GR団参上!』の付録'),
    (r'Pokémon Card GB2: Here Comes Team GR! Official Guidebook insert', lambda m: '『ポケモンカードGB2 GR団参上!』公式ガイドブックの付録'),
    (r'Pokémon Trading Card Game insert', lambda m: 'ゲームボーイ『ポケモンカードGB』の付録'),
    (r'Pocket Monsters Fan Book insert', lambda m: '『ポケットモンスター ファンブック』の付録'),
    (r'Official Card File insert', lambda m: 'オフィシャルカードファイルの付録'),
    (r'JR East Pokémon Stamp Rally', lambda m: 'JR東日本 ポケモンスタンプラリー'),
    (r'CoroCoro Best Photo Contest', lambda m: 'コロコロ ベストフォトコンテストの賞品'),
    (r'64 Mario Stadium Best Photo Contest', lambda m: '64マリオスタジアム ベストフォトコンテストの賞品'),
    (r'Communication Evolution Campaign', lambda m: '通信進化キャンペーン（拡張シート第3弾のマサキのパソコンで応募）'),
    (r"Mirage Pokémon: Lugia's Explosive Birth movie pamphlet", lambda m: '映画『幻のポケモン ルギア爆誕』のパンフレット'),
    (r'Emperor of the Crystal Tower: Entei theatrical release', lambda m: '映画『結晶塔の帝王 ENTEI』の上映館'),
    (r"Garura Parent/Child Tournament winner's prize", lambda m: 'ガルーラ親子大会の優勝賞'),
    (r'Blastoise Mega Battle participation', lambda m: 'カメックスメガバトルの参加賞'),
    (r'Riding on Lapras CD insert', lambda m: 'CD「ラプラスにのって」の付録'),
    (r"Meowth's Party CD insert", lambda m: 'CD「ニャースのパーティ」の付録'),
    (r'All Card Calendar', lambda m: 'オールカードカレンダー'),
    (r'Pokémon Card Game Illust Artist Contest', lambda m: 'ポケモンカードゲーム イラストレーターコンテストの賞品'),
]


def dist_ja(text):
    """Bulbapedia の配布の記載を日本語に。訳せないものは英語のまま（Bulbapedia）と付ける。日付の括弧は除く。"""
    if not text:
        return ''
    for pat, fn in DIST_JA:
        m = re.match(pat, text)
        if m:
            return fn(m)
    return re.sub(r'\s*\([^)]*\d{4}\)$', '', text) + '（Bulbapedia）'


def card_table(cat, cards, key, qty=None, en_prints=None):
    head = '| 番号 | カード名 | 種類 | タイプ | HP | レア |' + (' 枚数 |' if qty else '') + ' 英語版 | ほかの収録 |'
    lines = [head, '|' + '---|' * (head.count('|') - 1)]
    for c in cards:
        name = cat.display_name(c)
        name = f"[{md(name)}]({c['url']})" + ('（名前はカードの画像で確認）' if name != c['name'] else '')
        row = [c['list_number'], name, kind_short(c), c.get('type') or '', str(c.get('hp') or ''),
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


def header(title, depth=1, numbers='「番号」は pcg-search の並び順で、カードに印刷された番号ではありません。'):
    up = '../' * depth
    return [f'# {title}', '', GENERATED, '',
            f'[拡張パック以外の商品の一覧](../other-products.md) ／ 出典の記号: [出典と確認状況]({up}../sources.md)', '',
            '- カードの欄（名前・HP・ワザなど）は、ポケモンカード 旧シリーズ検索（pcg-search.com）[N3] の転記です。カード名から各カードのページにリンクしています。',
            f'- {numbers}',
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
            names = [x[len('name:'):] if x.startswith('name:') else cat.display_name(by_id[x]) for x in sh['cards']]
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
        names = '、'.join(f"[{cat.display_name(c)}]({c['url']})" for c in cs)
        L.append(f"- {labels.get(kind, kind)}（{len(cs)} 種）: {names}")
    L += ['',
          '- pcg-search で名前の記載がない 3 種（1stex3049〜3051）は、カードの画像と Bulbapedia で「イマクニ？のコーナー」（見出しは「イマクニ？の オレにも言わせろ!! のコーナー」）、「ハズレ？」、「Pokémon Machine」と確かめました。どれも手描きのジョークカードです [N3][X43]。**確実**（pcg-search の転記データは変えずに、`data/curation/other_products.json` の `identified_cards` で名前を付けています）',
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


# ---- イントロパック -------------------------------------------------------

BASIC_ENERGY = {f'{t}エネルギー' for t in '草炎水雷超闘'}


def is_basic_energy(c):
    return c['name'] in BASIC_ENERGY and not c.get('hp')


def bulba_cell(cat, c):
    b = cat.cur.get('intro_packs', {}).get('bulbapedia', {}).get(page_id(c))
    if not b:
        return ''
    return f"同じカード: {b['same_as']}" if b['same_as'] else 'このパックのカード'


def page_intro_packs(cat):
    keys = keys_of(cat, 'intro_pack')
    L = header('イントロパック・イントロパック★neo',
               numbers='「番号」は pcg-search の並び順です。デッキのカードでは、カードに印刷された丸数字と一致します（キラカードと拡張カードには印刷された番号がない）。') + [
        '## 概要', '',
        '### イントロパック（1999-07-30）', '',
        '- 初めて遊ぶ人向けのセットで、フシギダネデッキとゼニガメデッキ（各 40 枚）、キラカードのフシギバナとカメックス、'
        '遊びかたのビデオ（VHS。タレントのセイン・カミュが案内役）、ルールブック、ダメージカウンター 30 個、どくマーカー 2 個、コイン、プレイマットが入っていました [X49]。**確実**',
        '- デッキのカードには丸で囲んだ番号があり（フシギダネデッキは黒丸に白字、ゼニガメデッキは白丸に黒字）、pcg-search の並びの番号と一致します。キラカードの 2 枚には番号がありません [X49]。**確実**',
        '- 多くは拡張パック第1弾・拡張シートのカードの再録です。neo 第1弾（2000年）の「マサキの転送装置」「スーパーポケモン回収」が先に入っており、このパックで初めて出たカード（新しいイラスト）もあります [X49]。**確実**',
        '- レアリティマークはありません [X49]。**確実**', '',
        '### イントロパック★neo（2001-04-06）', '',
        '- チコリータデッキとワニノコデッキ（各 30 枚）と、それぞれに加えて遊ぶ「拡張カード」10 枚のセットです。ビデオはなく、ルールブック、ダメージカウンター、状態を表すマーカー、コイン、プレイマットが入っていました [X50]。**確実**',
        '- 30 枚のデッキのカードには丸で囲んだ番号（チコリータデッキは白丸に黒字、ワニノコデッキは黒丸に白字）があり、拡張カードには番号がありません [X50]。**確実**',
        '- 拡張パック第1弾と neo 第1〜3弾などのカードの再録に、このパックで初めて出たカードが加わっています [X50]。**確実**', '',
        '### 英語版', '',
        '- このパックだけのカード（新しいイラストのカード）は、英語版にはなっていません（Bulbapedia で英語版のないカードとされている）[X49][X50]。**確実**',
        '- イントロパックで neo 第1弾より先に出た「マサキの転送装置」「スーパーポケモン回収」は、英語版では Neo Genesis に入りました [X49]。**確実**',
        '- 再録のカードの「英語版」の欄は、元のカードの英語版です。', '',
        '| 商品 | 発売日 | 枚数 | 基本エネルギー以外 | このパックで初めて出たカード（種類） |', '|---|---|---|---|---|']
    for k in keys:
        cards = cat.data[k]
        named = [c for c in cards if not is_basic_energy(c)]
        new = len({sig_pcg(c) for c in named if cat.first(c, k)})  # 同じデッキの中の同じカードは 1 つと数える
        L.append(f"| {cat.short_name(k)} | {cat.products[k]['release_date']} | {len(cards)} | {len(named)} | {new} |")
    L += ['', '- 発売日・内容・デッキリストは Bulbapedia [X49][X50] によります。カードの欄は pcg-search [N3]。',
          '- 「Bulbapedia」の欄は、Bulbapedia のカードのページが別のカードのページに転送されるか（同じカードとして扱われているか）です。'
          'この欄と「ほかの収録」（名前・HP・ワザ名による判定）は、全カードで食い違いがありません（[再録カードの対応付け](../reprints.md)）。', '']
    for k in keys:
        cards = cat.data[k]
        L += [f"## {cat.short_name(k)}", '',
              '| 番号 | カード名 | 種類 | タイプ | HP | 英語版 | ほかの収録 | Bulbapedia |', '|---|---|---|---|---|---|---|---|']
        for c in cards:
            if is_basic_energy(c):
                continue
            L.append('| {} | [{}]({}) | {} | {} | {} | {} | {} | {} |'.format(
                c['list_number'], md(c['name']), c['url'], kind_short(c), c.get('type') or '', c.get('hp') or '',
                cat.en(c), '<br>'.join(cat.appears(c)), bulba_cell(cat, c)))
        energy = {}
        for c in cards:
            if is_basic_energy(c):
                energy.setdefault(c['name'], []).append(str(int(c['list_number'].split('/')[0])))
        if energy:
            L += ['', '基本エネルギー: ' + '、'.join(f"{n} {len(v)} 枚（{'・'.join(v)}）" for n, v in energy.items())]
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
    # Wizards Black Star Promos の日本での初出（pcg-search のカードとの対応がわかったもの）
    first = {}
    for key, cards in cat.data.items():
        for c in cards:
            e = cat.cur['en_prints'].get(page_id(c))
            if e and e['set_id'] == 'basep':
                date = cat.date_of(key, c) or '9999'
                dist = cat.promo_info.get(page_id(c), {})
                where = (dist.get('distribution') or dist_ja(dist.get('distribution_en'))) if dist else cat.short_name(key)
                first.setdefault(int(e['number']), []).append((date, e['name'], c['name'], where.replace('\n', ' ')))
    L += ['## Wizards Black Star Promos の日本での初出', '',
          '英語版のプロモ（Wizards Black Star Promos、全 53 枚）は、ミュウ（8・9。日本では「化石の秘密」）を除いて、日本でプロモや特別な商品として先に出たカードです [X41]。'
          'このページ群のカードと対応がわかったものを載せています（Bulbapedia の英語版カードのページにある日本語のワザ名と照合）。', '',
          '| 番号 | 英語版 | 日本語名 | 日本での初出 |', '|---|---|---|---|']
    for num in sorted(first):
        date, en_name, ja_name, where = sorted(first[num])[0]
        L.append(f"| {num} | {en_name} | {ja_name} | {date} {md(where)} |")
    L += ['', f'対応がわかったのは {len(first)} 枚です。', '']
    for k in keys:
        cards = cat.data[k]
        L += [f"## {cat.short_name(k)}", '',
              '| 番号 | カード名 | 種類 | HP | 配布 | 英語版 | ほかの収録 |', '|---|---|---|---|---|---|---|']
        for c in cards:
            info = cat.promo_info.get(page_id(c), {})
            dist = md((info.get('distribution') or '').replace('\n', ' ') or dist_ja(info.get('distribution_en')))
            if info.get('date'):
                dist = f"{info['date']} {dist}"
            if info.get('note'):
                dist += f"<br>（{md(info['note'])}）"
            L.append('| {} | [{}]({}) | {} | {} | {} | {} | {} |'.format(
                c['list_number'], md(c['name']), c['url'], kind_short(c), c.get('hp') or '', dist, cat.en(c),
                '<br>'.join(cat.appears(c))))
        L.append('')
    return L


# ---- 再録の対応付け ---------------------------------------------------------

TYPE_SYM = {'grass': '草', 'fire': '炎', 'water': '水', 'lightning': '雷', 'psychic': '超', 'fighting': '闘',
            'colorless': '無', 'darkness': '悪', 'metal': '鋼'}
REPRINT_KIND_JA = {'meaning': '意味が変わる', 'clarify': '補足・対象の明記', 'wording': '書き方だけ'}
REPRINT_DIFF_JA = {'cost': 'コスト', 'damage': 'ダメージ', 'text': '文面', 'weakness': '弱点', 'resistance': '抵抗力',
                   'retreat': 'にげる'}
EN_ABBR = {'base1': 'BS', 'base2': 'JU', 'base3': 'FO', 'base4': 'BS2', 'base5': 'TR', 'gym1': 'G1', 'gym2': 'G2',
           'neo1': 'N1', 'neo2': 'N2', 'neo3': 'N3', 'neo4': 'N4', 'base6': 'LC', 'si1': 'SI', 'basep': 'Promo'}
# Bulbapedia のカードのページ名の括弧内 → 英語版のセット id、または pcg-search の商品
BULBA_EN = {'Base Set': 'base1', 'Jungle': 'base2', 'Fossil': 'base3', 'Team Rocket': 'base5', 'Gym Heroes': 'gym1',
            'Gym Challenge': 'gym2', 'Neo Genesis': 'neo1', 'Neo Discovery': 'neo2', 'Neo Revelation': 'neo3',
            'Neo Destiny': 'neo4', 'Wizards Promo': 'basep', 'Southern Islands': 'si1', 'Legendary Collection': 'base6'}
BULBA_JP = {'Vending S1': '拡張シート 第1弾(青版)', 'Vending S2': '拡張シート 第2弾(赤版)', 'Vending S3': '拡張シート 第3弾(緑版)',
            'Bulbasaur Deck': 'イントロパック(フシギダネデッキ)', 'Squirtle Deck': 'イントロパック(ゼニガメデッキ)',
            'Chikorita Half Deck': 'イントロパック★neo(チコリータデッキ)', 'Totodile Half Deck': 'イントロパック★neo(ワニノコデッキ)'}


def member_label(g):
    return f"{g['product']}（{g['record']['id']}）" if 'record' in g else f"{g['product']}（{page_id(g['card'])}）"


def numbers_of(g):
    """同じカードの組の中で比べる数値の欄（タイプ・弱点・抵抗力・にげる・ワザのコストとダメージ）。"""
    if 'record' in g:
        p = g['record']['pokemon']
        if not p:
            return None
        wr = lambda xs: ''.join(f"{TYPE_SYM[x['type']]}{x['operator']}{x['value']}" for x in xs) or None
        return {'タイプ': ''.join(TYPE_SYM[t] for t in p['types']), '弱点': wr(p['weaknesses']),
                '抵抗力': wr(p['resistances']), 'にげる': p['retreat_cost'] or 0,
                'ワザ': [(''.join(sorted(TYPE_SYM[x] for x in a['cost'])), (a['damage'] or {}).get('display') or '')
                        for a in p['attacks']]}
    c = g['card']
    if not c.get('hp'):
        return None
    return {'タイプ': c['type'], '弱点': c['weakness'], '抵抗力': c['resistance'], 'にげる': len(c['retreat'] or ''),
            'ワザ': [(''.join(sorted(a['cost'])), a['damage'] or '') for a in c['attacks']]}


def texts_of(g):
    """効果文の並び（ポケモンは特殊能力・ワザの順、ほかは本文）。pcg-search は本文が 2 つの欄に分かれていることがあるのでつなぐ。"""
    if 'record' in g:
        r = g['record']
        p = r['pokemon']
        if p:
            return [x['text']['ja'] for x in p['powers']] + [a['text']['ja'] for a in p['attacks']]
        return [((r['trainer'] or r['energy'] or {}).get('text') or {}).get('ja')]
    c = g['card']
    if c.get('hp'):
        return [x['text'] for x in c['powers']] + [a['text'] for a in c['attacks']]
    return ['\n'.join(x for x in (c['text'], c['note']) if x) or None]


def plain_ja(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s。、・「」『』()（）,.!?\[\]【】]', '', s)


def text_differs(a, b):
    """書き方の違いがあるか（転記の小さな揺れは無視するため、似ている度合い 0.9 未満を違いとする）。"""
    return any(x and y and difflib.SequenceMatcher(None, plain_ja(x), plain_ja(y)).ratio() < 0.9
               for x, y in zip(texts_of(a), texts_of(b)))


def texts_similar(a, b):
    """効果文がおおむね同じか（両方ないものは同じとみなす）。"""
    return all((not x and not y) or (x and y and difflib.SequenceMatcher(None, plain_ja(x), plain_ja(y)).ratio() >= 0.9)
               for x, y in zip(texts_of(a), texts_of(b)))


def basic_energy_group(members):
    g = members[0]
    if 'record' in g:
        return bool(g['record']['energy']) and g['record']['energy']['kind'] == 'basic'
    return is_basic_energy(g['card'])


def reprint_groups(cat):
    """2 つ以上の商品に入っている同じカード（基本エネルギーを除く）。最初の収録の日付順。"""
    out = []
    for sig, members in cat.groups.items():
        if len(cat.products_of(sig)) < 2 or basic_energy_group(members):
            continue
        out.append((sig, sorted(members, key=lambda g: g['date'] or '9999')))
    return sorted(out, key=lambda x: (x[1][0]['date'] or '9999', x[0][0]))


def en_ids_of(cat, members):
    have = set()
    for g in members:
        if 'record' in g:
            r = g['record']
            if r['en_print']:
                have |= {(r['en_print']['set_id'], n) for n in r['en_print']['numbers']}
                have |= {(x['set_id'], x['number']) for x in r['en_reprints']}
        else:
            e = cat.cur['en_prints'].get(page_id(g['card']))
            if e:
                have.add((e['set_id'], e['number']))
    return have


def bulba_check(cat):
    """イントロパックのカードの、Bulbapedia のページの転送先と、名前・HP・ワザ名による判定を比べる。"""
    bp = cat.cur.get('intro_packs', {}).get('bulbapedia', {})
    pages = {page_id(c): (k, c) for k in cat.data for c in cat.data[k]}
    intro = set(keys_of(cat, 'intro_pack'))
    bad = []
    for pid, b in bp.items():
        k, c = pages[pid]
        same, t = cat.same(c), b['same_as']
        if t is None:  # Bulbapedia ではこのパックのカード → 先に出たほかの商品の同じカードがないこと
            mine = cat.date_of(k, c) or ''
            ok = not [g for g in same if g.get('key') not in intro and (g['date'] or '') < mine]
        else:
            inside = re.search(r'\(([^()]*)\)$', t).group(1)
            setname, num = inside.rsplit(' ', 1)
            if inside in BULBA_JP:
                ok = any(g.get('key') == BULBA_JP[inside] for g in same)
            elif setname in BULBA_JP:
                ok = any(g.get('key') == BULBA_JP[setname] and int(g['card']['list_number'].split('/')[0]) == int(num)
                         for g in same)
            else:
                ok = (BULBA_EN[setname], num) in en_ids_of(cat, same)
        if not ok:
            bad.append((k, c, t))
    return len(bp), bad


def page_reprints(cat):
    groups = reprint_groups(cat)
    L = ['# 再録カードの対応付け', '', GENERATED.replace('data/ja_text_pcgsearch.json と data/curation/other_products.json',
                                                     'data/cards.json・data/ja_text_pcgsearch.json・data/curation/'), '',
         '出典の記号: [出典と確認状況](../sources.md)', '',
         '旧裏期には、同じカードが別の商品に何度も入りました（拡張パックのカードがジムデッキ・クイックスターターギフト・イントロパックに、'
         'プロモのカードが拡張パックに、など）。英語版でも Base Set 2・Legendary Collection などに再録があります。'
         'このページは、このリポジトリで「同じカード」をどう判定しているかと、その判定を点検した結果です。', '',
         '## 判定のしかた', '',
         '### 日本版（商品をまたいだ同じカード）', '',
         '- 拡張パック 10 弾のカード（`data/cards.json`）と、拡張パック以外の商品のカード（`data/ja_text_pcgsearch.json`）を通して、'
         '次が同じものを同じカードとしています（`scripts/build_other_products.py`）。',
         '  - ポケモン: カード名・HP・特殊能力（ポケモンパワー）の名前・ワザの名前の並び',
         '  - トレーナー・エネルギー: カード名',
         '- 名前は Unicode の NFKC で正規化し、空白・中黒・括弧などを除いて比べます。サイトの表記の揺れ（ウィンディ／ウインディ）は直してから比べます。',
         '- レベル・イラスト・レアリティマーク・文面の書き方は比べていません。旧裏期の再録では、これらが変わることがあるためです'
         '（例: ナツメのケーシィはジムデッキとプロモでイラストとレベルが違うが、Bulbapedia でも同じカードとして扱われている [X51]）。',
         '- 商品のページの「ほかの収録」と「英語版」の欄（同じカードのほかの版の英語版）は、この判定によります。'
         'イラストの違う版が英語版でも別々に出ているもの（ナツメのケーシィ: Gym Challenge 93 と Wizards Black Star Promos 19）は、イラストの合うほうに対応付けています。', '',
         '### 英語版（別のセットへの再録）', '',
         '- `scripts/build_cardlist.py` が、英語版のデータ（pokemon-tcg-data）の中で、次が同じカードを別のセットへの再録としています（`data/cards.json` の `en_reprints`）。',
         '  - ポケモン: 英語名・HP・ワザ名の並び・ポケモンパワー名',
         '  - トレーナー・特殊エネルギー: 英語名（基本エネルギーは除く）',
         '- 再録のうち、英語版データの上でコスト・ダメージ・文面・弱点・抵抗力・にげるが元のカードと違うものは `differences` に記録し、'
         '各弾のページの備考に「（文面が違う）」などと書いています。', '']

    # ---- 点検: 日本版
    num_bad = []
    for sig, members in groups:
        base = next((g for g in members if numbers_of(g)), None)
        if not base:
            continue
        nb = numbers_of(base)
        for g in members:
            n = numbers_of(g)
            if g is base or not n:
                continue
            for f in ('タイプ', '弱点', '抵抗力', 'にげる'):
                if nb[f] != n[f]:
                    num_bad.append((sig[0], member_label(base), member_label(g), f, nb[f], n[f]))
            for i, (a, b) in enumerate(zip(nb['ワザ'], n['ワザ'])):
                if a != b:
                    num_bad.append((sig[0], member_label(base), member_label(g), f'{i + 1} つめのワザ', ' '.join(a), ' '.join(b)))
    checked, bulba_bad = bulba_check(cat)
    by_name = {}
    for sig in cat.groups:
        if len(sig) == 4:
            by_name.setdefault((sig[0], sig[1]), []).append(sig)
    near = [(a, b) for sigs in by_name.values() for i, a in enumerate(sigs) for b in sigs[i + 1:]]
    near_same_numbers = [(a, b) for a, b in near if len(a[2]) == len(b[2]) and len(a[3]) == len(b[3])
                         and numbers_of(cat.groups[a][0]) and numbers_of(cat.groups[a][0])['ワザ'] == numbers_of(cat.groups[b][0])['ワザ']]
    suspicious = [(a, b) for a, b in near_same_numbers if texts_similar(cat.groups[a][0], cat.groups[b][0])]
    n_cards = sum(len(m) for _, m in groups)
    L += ['## 点検の結果', '',
          '### 日本版', '',
          f'- 2 つ以上の商品に入っている同じカードは {len(groups)} 組（{n_cards} 枚。基本エネルギーを除く）です。一覧はこのページの最後にあります。',
          f'- **数値の照合**: 同じカードとした組の中で、タイプ・弱点・抵抗力・にげる・ワザのコストとダメージを比べました。食い違いは {len(num_bad)} 件です。']
    notes = cat.cur.get('reprint_checks', {})
    for name, a, b, f, x, y in num_bad:
        L.append(f'  - {name}: {a} と {b} で{f}が「{x}」と「{y}」。{notes.get(name, "（未確認）")}')
    L += [f'- **Bulbapedia との照合**: イントロパック・イントロパック★neo の {checked} 枚（基本エネルギーを除く）について、'
          'Bulbapedia のカードのページが別のカードのページに転送されるか（同じカードとして扱われているか）[X49][X50] と、この判定を比べました。'
          f'食い違いは {len(bulba_bad)} 件です。']
    for k, c, t in bulba_bad:
        L.append(f"  - {cat.short_name(k)} の {c['name']}（Bulbapedia: {t or 'このパックのカード'}）")
    L += [f'- **名前と HP が同じでワザが違うもの**は、別のカードとして扱っています（{len(near)} 組。例: そらをとぶピカチュウの LV.12（でんきショック）と LV.11（でんげき））。'
          f'このうち、ワザのコストとダメージまで同じで、特殊能力名・ワザ名だけが違う組は {len(near_same_numbers)} 組あり、'
          f'効果文まで同じ組（転記の誤りの疑いがあるもの）は {len(suspicious)} 組です。']
    for a, b in near_same_numbers:
        mark = '（効果文も同じ。要確認）' if (a, b) in suspicious else '（効果文が違う別のカード）'
        L.append(f"  - {a[0]} HP{a[1]}: {'・'.join(a[2] + a[3])} ／ {'・'.join(b[2] + b[3])}{mark}")
    L += ['',
          '### 点検で見つけて直したこと', '',
          '- 拡張パック「ポケモンジャングル」のプリン（PMCG2-035）は、なぞのばしょの転記で 2 つめのワザ名が「こもりうた」になっていました（正しくは「はたく」）。'
          'このため、イントロパック（ゼニガメデッキ）に再録された同じカードと別のカードと判定されていました。'
          'Bulbapedia との照合で見つかり、`data/curation/ja_text.json` で直しました [N3][X49]。**確実**',
          '- 全日空（ANA）のキャンペーンのそらをとぶピカチュウ 2 枚の配布時期を取り違えていました。'
          '1998 年（カイリューとの 2 枚組）は 1997 年のコロコロコミックの付録と同じ LV.12・でんきショックのカード、'
          '1999 年（フリーザーとの 2 枚組）は LV.11・でんげきの別のカードです（Bulbapedia の個別のページ [X51] と、pcg-search のカードの画像で確認）。'
          'pcg-search の並びでは LV.11 の版が 1998 年のカイリューの隣にあります。**確実**',
          '- 再録の文面を比べた結果、拡張パック第1弾の「エネルギー回収」の印刷は「2枚の好きなエネルギーカード」で、英語版（basic Energy cards）と違うことがわかりました'
          '（のちの再録で「基本エネルギーカード」に改められた）。1997 年のプロモの「超エネルギー回収」も同じです。**確実**（印刷の文面）',
          '  - その後の調査で、1998年に両方を基本エネルギーだけに限る公式エラッタが出ていたとわかりました（Bulbapedia がファンクラブ会報 Vol.5 p.16 を出典に挙げる）[X52]。**有力**'
          '印刷の違いとエラッタは [エラッタの履歴](../rules/errata-history.md) に分けて記録し、[日英の違い](card-differences.md) はエラッタとして載せています。',
          '- 英語版: トレーナー・特殊エネルギーの別のセットへの再録を記録していなかったので、加えました。',
          '- 英語版: 英語版データの誤記のため、Legendary Collection への再録と判定できていなかったカードがありました。`data/curation/en_fixes.json` で直しています。']
    fixes = load('data/curation/en_fixes.json')
    for cid, fx in fixes.items():
        if cid.split('-')[0] in ('base4', 'base6', 'basep'):
            L.append(f"  - {cid}: {fx['reason']}")
    L.append('')

    # ---- 日本版の文面の改訂
    rt = cat.cur.get('reprint_text', {})
    rows = []
    for sig, members in groups:
        base = next((g for g in members if any(texts_of(g))), None)
        if not base:
            continue
        diff = []
        for g in members:
            if g is not base and text_differs(base, g) and g['product'] not in diff:
                diff.append(g['product'])
        if diff:
            note = rt.get(f'{sig[0]}/{sig[1]}' if len(sig) == 4 else sig[0]) or rt.get(sig[0], {})
            rows.append(f"| {md(sig[0])} | {base['product']}（{base['date']}） | {'<br>'.join(diff)} | "
                        f"{md(note.get('summary', ''))} | {REPRINT_KIND_JA.get(note.get('kind'), '未分類')} |")
    L += ['### 日本版の文面の書き換え', '',
          '同じカードでも、のちの商品の再録では文面が書き換えられていることがあります（1998年のジムデッキのころから、'
          '「あなたの」「〜してよい」「トラッシュする」などの書き方にそろえられた）。最初の収録と文面が違う再録を挙げます'
          '（転記の小さな揺れを除くため、文字列がおおむね同じものは除いています）。'
          '多くは書き方だけの違いですが、意味が変わるものもあります。文面は、拡張パックはなぞのばしょ・ポケモンWiki、ほかの商品は pcg-search の転記によります。', '',
          '| カード | 最初の収録 | 文面が違う収録 | 違い | 区分 |', '|---|---|---|---|---|'] + rows + ['']

    # ---- 英語版
    recs = cat.records
    n_pk = sum(1 for r in recs if r['category'] == 'pokemon' and r['en_reprints'])
    n_tr = sum(1 for r in recs if r['category'] != 'pokemon' and r['en_reprints'])
    diff_rows_en = []
    for r in recs:
        for x in r['en_reprints']:
            if x.get('differences'):
                diff_rows_en.append(f"| {r['id']} {md(r['name']['ja'] or '')} | {r['en_print']['set_name']} {r['en_print']['numbers'][0]}（{md(r['name']['en'])}） | "
                                    f"{x['set_name']} {x['number']} | {'・'.join(REPRINT_DIFF_JA[d] for d in x['differences'])} |")
    L += ['### 英語版', '',
          f'- 別のセットへの再録があるのは、ポケモン {n_pk} 枚、トレーナー・特殊エネルギー {n_tr} 枚です（日本版の拡張パック 10 弾のカードのうち）。',
          f'- そのうち、英語版データの上で元のカードと欄が違う再録は {len(diff_rows_en)} 件です。ほとんどは文面の書き換え（Base Set 2 の「You can\'t add more than 20 damage in this way」、'
          'Legendary Collection の「or this attack does nothing」など、書き方の統一）で、意味が変わるものは少数です'
          '（例: Legendary Collection のサイホーンのにらみつけるは「Rhyhorn を攻撃できない」が「攻撃できない」に）。', '',
          '| 日本版 | 英語版（元のカード） | 再録 | 違う欄 |', '|---|---|---|---|'] + diff_rows_en + ['']

    # ---- 一覧
    L += ['## 同じカードの一覧', '',
          '2 つ以上の商品に入っている同じカード（基本エネルギーを除く）を、最初の収録の日付順に並べます。', '',
          '| カード | HP | 収録（発売日順） | 英語版 |', '|---|---|---|---|']
    for sig, members in groups:
        prods = cat.products_of(sig)
        first = next((g['card'] for g in members if 'card' in g), None)
        en = cat.en(first) if first else ''
        if not en:
            r = next((g['record'] for g in members if 'record' in g), None)
            en = f"{r['en_print']['set_name']} {r['en_print']['numbers'][0]}（{r['name']['en']}）" if r and r['en_print'] else ''
        hp = str(sig[1]) if len(sig) == 4 else ''
        L.append(f"| {md(members[0]['record']['name']['ja'] if 'record' in members[0] else members[0]['card']['name'])} | {hp} | "
                 f"{'<br>'.join(f'{p}（{d}）' if d else p for d, p in prods)} | {md(en)} |")
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
        'intro_pack': ('1999-07-30・2001-04-06', 'このパックだけのカードは英語版なし'),
        'premium_file': ('1999-12〜2000-11', 'Neo Genesis・Discovery・Revelation へ'),
        'promo': ('1996〜2001', '一部が Wizards Black Star Promos など'),
    }
    for slug, title, group in PAGES:
        keys = keys_of(cat, group)
        if not keys:
            continue
        n_cards = sum(len(cat.data[k]) for k in keys)
        date, en = rows[group]
        kinds = '旧裏期・neo 期' if group == 'promo' else f'{len(keys)} 種'
        L.append(f"| {title}（{kinds}）| {date} | {n_cards} 種 | {en} | [{slug}.md](products/{slug}.md) |")
    L += ['', '英語版にあって日本の拡張パックにないカードの、日本での初出は [英語版のみに見られるカード](english-only.md) にあります。',
          '商品をまたいだ同じカード（再録）の判定のしかたと点検の結果は [再録カードの対応付け](reprints.md) にあります。', '',
          '## まだ確認できていないこと', '',
          '- 拡張シートの自動販売機の種類（バンダイの「ジャンボカードダス」とする情報があるが未確認）',
          '- 青版の「化石の発掘」「月の石」のレアリティマークの有無（pcg-search と Bulbapedia で食い違い）',
          '- サザンアイランドの 3 枚入りパックの販売場所（ファイル版は上映館だけ）']
    if keys_of(cat, 'promo'):
        L.append('- プロモカードのうち、配布方法を突き合わせられなかったもの（[プロモーションカード](products/promos.md) で空欄のもの）')
        L.append('- Wizards Black Star Promos のうち、日本のカードとの対応がわからなかったもの（[プロモーションカード](products/promos.md) の表にない番号）')
    L.append('')
    return L


def main():
    cat = Catalog()
    (OUT / 'products').mkdir(exist_ok=True)
    builders = {'expansion-sheets': page_expansion_sheets, 'southern-islands': page_southern_islands,
                'gym-decks': page_gym_decks, 'quick-starter-gift': page_quick_starter_gift,
                'intro-packs': page_intro_packs, 'premium-files': page_premium_files, 'promos': page_promos}
    for slug, title, group in PAGES:
        if keys_of(cat, group):
            (OUT / 'products' / f'{slug}.md').write_text('\n'.join(builders[slug](cat)), encoding='utf-8')
    (OUT / 'other-products.md').write_text('\n'.join(page_index(cat)), encoding='utf-8')
    (OUT / 'reprints.md').write_text('\n'.join(page_reprints(cat)), encoding='utf-8')
    print(sum(len(v) for v in cat.data.values()), 'cards')


if __name__ == '__main__':
    main()
