"""次版のカードの文面と進化データの調査（2026-10-30）の検査。

- 優先A（5 枚）: ピカチュウ（PR1-001・PR1-003・PR1-017）のなきごえ、ヤドラン（ES3-021）のおおいびき、ボロのつりざお（neo3-053）。
  『オフィシャルブック2000』[P43] p.127・p.156（スキャン [J38] の PDF 129・158）を画像で読み、最新の説明（LD-）・照合（CC-）・裁定（CR-）・論点（UQ-）を加えた。
  カードの画像（IMG-）は pcg-search.com [N3] の 1 枚ずつ（関連の IP1-040 も）。ボロのつりざおは画像で「1枚」を確かめ、文面を訂正した。
- 優先B（12 枚）: アンノーン M・U・A（neo2-027・028・030）のルール文、GD3-003・ES2-011・ES2-028・ES2-029・ES3-018・PRN-030・PRN-039・
  PRN-040・PRN-045 の段階・進化元。同じ商品・番号のカードの画像（IMG-）で確かめ、訂正（FIX-）で入れた。
- 基準: この作業の基準のコミット e519b99。比べる値はこのコミットの記録（あとの作業で数が増えても、この時点の値を確かめる）。
- 公式ルール 2000.02.14 版（P43）の範囲だけ。英語版の文面・現代のルール・後年の裁定は根拠にしない。
"""
import copy
import csv
import io
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402
import build_cardlist  # noqa: E402

BASE = 'e519b99e2adcc6c2cd0998569ae5ee1101de6e89'  # この作業の基準
# この作業のコミット。同じ日（2026-10-30）のあとの作業の照合の記録（neo2 の化石 4 枚。tests/test_neo2_fossil_type_cost.py）と分けるため、
# この作業の照合の記録は、このコミットにある id で選ぶ
AT_COMMIT = 'c932625053f4cd4d784585f8b6144121499d85ed'
UNOWN_RULE = '「アンノーン」はデッキに4枚までしか入れることができません。'
ROD = 'コインを2枚投げ、すべて「おもて」なら「ポケモンのカード」を、すべて「うら」なら「トレーナーカード」を、あなたのトラッシュから1枚選び出し、相手プレイヤーに見せてから、手札に加える。'
# 訂正の id → （カード id, 欄, 訂正のあとの値。進化元は日本語名）
FIXES = {
    'FIX-neo3-053-TRAINER-TEXT-JA': ('neo3-053', 'trainer.text.ja', ROD),
    'FIX-neo2-027-RULES-TEXT-JA': ('neo2-027', 'pokemon.rules_text.ja', UNOWN_RULE),
    'FIX-neo2-028-RULES-TEXT-JA': ('neo2-028', 'pokemon.rules_text.ja', UNOWN_RULE),
    'FIX-neo2-030-RULES-TEXT-JA': ('neo2-030', 'pokemon.rules_text.ja', UNOWN_RULE),
    'FIX-GD3-003-EVOLVES-FROM': ('GD3-003', 'pokemon.evolves_from', 'マチスのピカチュウ'),
    'FIX-ES2-011-EVOLVES-FROM': ('ES2-011', 'pokemon.evolves_from', 'なにかの化石'),
    'FIX-ES2-028-EVOLVES-FROM': ('ES2-028', 'pokemon.evolves_from', 'なにかの化石'),
    'FIX-ES2-029-EVOLVES-FROM': ('ES2-029', 'pokemon.evolves_from', 'なにかの化石'),
    'FIX-ES3-018-EVOLVES-FROM': ('ES3-018', 'pokemon.evolves_from', 'なにかの化石'),
    'FIX-PRN-030-STAGE': ('PRN-030', 'pokemon.stage', 'basic'),
    'FIX-PRN-039-EVOLVES-FROM': ('PRN-039', 'pokemon.evolves_from', 'フシギダネ'),
    'FIX-PRN-040-EVOLVES-FROM': ('PRN-040', 'pokemon.evolves_from', 'わるいフシギソウ'),
    'FIX-PRN-045-EVOLVES-FROM': ('PRN-045', 'pokemon.evolves_from', 'オニスズメ'),
}
A_CARDS = ('PR1-001', 'PR1-003', 'PR1-017', 'ES3-021', 'neo3-053')
B_CARDS = ('neo2-027', 'neo2-028', 'neo2-030', 'GD3-003', 'ES2-011', 'ES2-028', 'ES2-029', 'ES3-018', 'PRN-030', 'PRN-039', 'PRN-040', 'PRN-045')
UNOWN = ('neo2-027', 'neo2-028', 'neo2-030')
# 訂正したカードで変わってよい欄（訂正した欄・その記録・欠けの一覧・出どころ。GD3-003 の英語名は生成が進化ラインから足す）
BOOKKEEPING = {'corrections', 'notes', 'data_gaps', 'field_sources.pokemon.stage', 'field_sources.pokemon.evolves_from'}


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def at_base(rel):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{rel}'], capture_output=True, text=True, check=True).stdout)


def at_commit(rel):
    """この作業のコミット（AT_COMMIT）の記録。あとの作業（2026-10-30 の v0.122 のあとの調査など）が値・記録を加えても、この作業の差を確かめる。"""
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{AT_COMMIT}:{rel}'], capture_output=True, text=True, check=True).stdout)


def changed_paths(a, b, path=''):
    """2 つの記録の違う欄（辞書と、同じ長さの辞書の配列は中まで見る）。"""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            yield from changed_paths(a.get(k), b.get(k), f'{path}.{k}' if path else k)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and all(isinstance(x, dict) for x in a + b):
        for i, (x, y) in enumerate(zip(a, b)):
            yield from changed_paths(x, y, f'{path}[{i}]')
    elif a != b:
        yield path


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.fixes = {c['id']: c for c in cls.ledger['corrections']}
        cls.images = load('data/curation/card_image_checks.json')
        then = {x['id'] for x in json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{AT_COMMIT}:data/curation/card_image_checks.json'],
                                                           capture_output=True, text=True, check=True).stdout)['checks']}
        cls.new_images = {x['card_id']: x for x in cls.images['checks'] if x['checked_on'] == '2026-10-30' and x['id'] in then}


class CardValueTest(Data):
    """カードの値の変更は、画像で確かめた 13 件の訂正だけ（基準 e519b99 との差）。印刷の値・ほかのカードは変えていない。"""

    def test_only_the_corrected_fields_changed(self):
        # 基点（e519b99）とこの作業のコミット（c932625）の差。あとの作業の訂正（PMCG1-019・PMCG6-034 の名前など）はここに入れない
        old = {c['id']: c for c in at_base('data/cards.json')['cards']}
        then = {c['id']: c for c in at_commit('data/cards.json')['cards']}
        self.assertEqual(set(old), set(then))  # 総数 1,377 件と id の集合
        self.assertEqual(set(then), set(self.by_id))
        self.assertEqual(len(self.cards), 1377)
        allowed = {}
        for cid, field, _ in FIXES.values():
            allowed.setdefault(cid, set(BOOKKEEPING)).add(field)
        changed = {i: set(changed_paths(old[i], then[i])) for i in old}
        changed = {i: p for i, p in changed.items() if p}
        self.assertEqual(set(changed), set(allowed))
        for cid, paths in changed.items():
            self.assertTrue(paths <= allowed[cid], (cid, paths - allowed[cid]))
            self.assertNotIn('jp_print', {p.split('.')[0] for p in paths}, cid)  # レベルなどを補っていない
            self.assertNotIn('pokemon.dex', paths, cid)
        # 優先Aのピカチュウ・ヤドランと、関連の IP1-040 は、印刷の値を変えていない（画像の値が今までの値と同じ）
        for cid in ('PR1-001', 'PR1-003', 'PR1-017', 'ES3-021', 'IP1-040'):
            self.assertNotIn(cid, changed)
            self.assertIn('existing_value', self.new_images[cid])

    def test_corrections_and_values(self):
        new = {c['id'] for c in at_commit('data/curation/card_corrections.json')['corrections']} - {c['id'] for c in at_base('data/curation/card_corrections.json')['corrections']}
        self.assertEqual(new, set(FIXES))
        for fid, (cid, field, after) in FIXES.items():
            c = self.fixes[fid]
            self.assertEqual((c['card_id'], c['field'], c['basis'], c['image_check'], c['decided_on'], c['kyuura_saw_image'], c['card_checks_affected']),
                             (cid, field, 'card_image_check', f'IMG-{cid}', '2026-10-30', True, []), fid)
            self.assertIn('最新の説明', c['not_errata'])  # 公式エラッタ・最新の説明として扱わない
            value = build_cardlist.get_field(self.by_id[cid], field)
            self.assertEqual(value['ja'] if isinstance(value, dict) else value, after, fid)
            self.assertEqual([x['id'] for x in self.by_id[cid]['corrections']], [fid])
            self.assertNotIn(field, self.by_id[cid]['data_gaps'])
        # 段階は印刷の値（進化元を埋めたカードの段階は変えていない。PRN-030 はたね、PRN-040 は 2 進化）
        for cid in B_CARDS:
            x = self.new_images[cid]
            if 'pokemon.stage' in x['print_values']:
                self.assertEqual(self.by_id[cid]['pokemon']['stage'], x['print_values']['pokemon.stage'], cid)
        self.assertEqual(self.by_id['PRN-030']['pokemon']['evolves_from'], None)  # 印刷に進化元の欄がない（読めないのではない）
        self.assertEqual(self.by_id['GD3-003']['field_sources']['pokemon.stage'], 'card_image_check:IMG-GD3-003')

    def test_unown_text_is_read_per_card(self):
        # グループの裁定（CR-UNOWN-DECK-LIMIT-ALL-LETTERS）・ほかの文字の文面から写していない。3 枚とも、それぞれの画像の照合の記録を持つ
        for cid in UNOWN:
            c = self.fixes[f'FIX-{cid}-RULES-TEXT-JA']
            self.assertEqual(c['previous_candidate']['status'], 'gap_open')
            self.assertIn('写していない', c['basis_detail'])
            self.assertEqual(self.new_images[cid]['print_values'], {'pokemon.rules_text.ja': UNOWN_RULE})
        cands = {(c['card_id'], c['field']) for c in self.ledger['candidates']}
        self.assertFalse({(cid, 'pokemon.rules_text.ja') for cid in UNOWN} & cands)
        # 未確認の欄（レベル）は候補に残す。値は埋めない
        for cid in ('PR1-001', 'PR1-003', 'PR1-017', 'IP1-040', 'ES3-021'):
            self.assertIn((cid, 'jp_print.level'), cands)
            self.assertIsNone(self.by_id[cid]['jp_print']['level'])

    def test_json_and_csv_agree(self):
        rows = {r['id']: r for r in csv.DictReader(io.StringIO((ROOT / 'data' / 'cards.csv').read_text(encoding='utf-8')))}
        self.assertEqual(set(rows), set(self.by_id))
        for cid in A_CARDS + B_CARDS:
            c, row = self.by_id[cid], rows[cid]
            p = c['pokemon']
            if p:
                self.assertEqual(row['stage'], p['stage'], cid)
                self.assertEqual(row['evolves_from_ja'], (p['evolves_from'] or {}).get('ja') or '', cid)
            self.assertEqual(row['corrections'].split(), [x['id'] for x in c.get('corrections') or []], cid)
        for cid in UNOWN:
            self.assertIn(UNOWN_RULE, rows[cid]['text_ja'])
        self.assertIn(ROD, rows['neo3-053']['text_ja'])


class RegenerationTest(Data):
    """訂正は生成のたびにかかる（cards.json だけを直していない）。before が今の値と違う・参照が切れた・別の版の画像の記録は止まる。"""

    def test_corrections_are_reapplied(self):
        for fid, (cid, field, after) in FIXES.items():
            c = self.fixes[fid]
            rec = copy.deepcopy(self.by_id[cid])
            build_cardlist.set_field(rec, field, copy.deepcopy(c['before']))
            rec['notes'] = []
            rec.pop('corrections')
            if 'field_sources' in rec:
                rec['field_sources'] = {k: None for k in rec['field_sources']}
            build_cardlist.apply_corrections([rec], {'corrections': [c], 'candidates': []})
            value = build_cardlist.get_field(rec, field)
            self.assertEqual(value['ja'] if isinstance(value, dict) else value, after, fid)
            if 'field_sources' in rec and field in build_cardlist.SOURCED_FIELDS:
                self.assertEqual(rec['field_sources'][field], f'card_corrections:{fid}')
            again = copy.deepcopy(rec)  # 値が直っていれば before と合わないので止まる
            again.pop('corrections')
            with self.assertRaises(SystemExit):
                build_cardlist.apply_corrections([again], {'corrections': [c], 'candidates': []})
        self.assertIn('「マチスのピカチュウ」を入れた', self.by_id['GD3-003']['notes'][0])  # 名前は日本語名で書く

    def test_confirmed_stage_conflict(self):
        rec = copy.deepcopy(self.by_id['GD3-003'])
        rec['field_sources']['pokemon.stage'] = build_cardlist.non_pack.STAGE_CONFLICT
        self.assertIn('pokemon.stage', build_cardlist.non_pack.data_gaps(rec))
        build_cardlist.confirm_stage_by_image_checks([rec], {'checks': [self.new_images['GD3-003']]})
        self.assertEqual(rec['field_sources']['pokemon.stage'], 'card_image_check:IMG-GD3-003')
        self.assertNotIn('pokemon.stage', build_cardlist.non_pack.data_gaps(rec))
        # 画像の照合のないカードの食い違いは残す
        other = copy.deepcopy(rec)
        other['field_sources']['pokemon.stage'] = build_cardlist.non_pack.STAGE_CONFLICT
        build_cardlist.confirm_stage_by_image_checks([other], {'checks': []})
        self.assertEqual(other['field_sources']['pokemon.stage'], build_cardlist.non_pack.STAGE_CONFLICT)

    def test_broken_records_are_rejected(self):
        ok = ([copy.deepcopy(c) for c in self.cards], copy.deepcopy(self.images), copy.deepcopy(self.ledger))
        build_cardlist.check_image_checks(*ok)

        def broken(change):
            recs, doc, led = copy.deepcopy(ok)
            change(recs, doc, led)
            with self.assertRaises(SystemExit):
                build_cardlist.check_image_checks(recs, doc, led)

        def fix(led, name):
            return next(c for c in led['corrections'] if c['id'] == name)

        def img(doc, name):
            return next(x for x in doc['checks'] if x['id'] == name)

        broken(lambda r, d, l: img(d, 'IMG-PRN-030')['print_values'].update({'pokemon.stage': 'stage1'}))  # 生成した値と違う
        broken(lambda r, d, l: img(d, 'IMG-neo2-028')['corrections'].append('FIX-NOT-THERE'))  # 参照切れ
        broken(lambda r, d, l: fix(l, 'FIX-ES2-011-EVOLVES-FROM').update(image_check='IMG-ES2-028'))  # 別のカードの画像
        broken(lambda r, d, l: img(d, 'IMG-ES2-028').update(corrections=['FIX-ES2-011-EVOLVES-FROM']))  # 別のカードの訂正
        broken(lambda r, d, l: fix(l, 'FIX-neo2-030-RULES-TEXT-JA').update(after='「アンノーン」はデッキに4枚まで入れることができます。'))
        broken(lambda r, d, l: fix(l, 'FIX-PRN-040-EVOLVES-FROM').update(after={'ja': 'フシギソウ', 'en': None}))  # 印刷と違う進化元
        broken(lambda r, d, l: fix(l, 'FIX-neo3-053-TRAINER-TEXT-JA').update(basis='kyuura_source_check'))  # 証拠の分類の誤り
        broken(lambda r, d, l: img(d, 'IMG-neo3-053')['images'][0].update(image_sha256='abc'))  # 画像の記録の欠け
        broken(lambda r, d, l: d['checks'].append(copy.deepcopy(img(d, 'IMG-PR1-017'))))  # id の重複
        broken(lambda r, d, l: next(c for c in r if c['id'] == 'PR1-017')['pokemon']['attacks'][0]['text'].update(ja='次の相手の番、このワザを受けた相手は、このカードにダメージを与えるとき、そのダメージが「-10」される。'))  # 印刷の欄を最新の説明で上書き


class ImageEvidenceTest(Data):
    """画像の照合の記録: サイトの転記と画像の読み取りを分け、同じスキャンの 2 つのサイトを独立の 2 回と数えない。CC- にしない。"""

    def test_records_and_counts(self):
        self.assertEqual(set(self.new_images), set(A_CARDS + B_CARDS) | {'IP1-040'})
        before = {x['id'] for x in at_base('data/curation/card_image_checks.json')['checks']}
        self.assertFalse({x['id'] for x in self.new_images.values()} & before)
        sites = Counter(len(x['images']) for x in self.new_images.values())
        self.assertEqual(sites, Counter({1: 15, 2: 3}))  # 18 枚のカード。2 つのサイトはアンノーンの 3 枚だけ
        for cid, x in self.new_images.items():
            self.assertEqual(x['id'], f'IMG-{cid}')
            self.assertTrue(x['site_transcriptions'], cid)  # サイトの転記は画像の読み取りと別の項目
            for t in x['site_transcriptions']:
                self.assertNotIn('image_sha256', t)
            if len(x['images']) == 2:
                self.assertIn('独立した 2 枚の実物の照合とは数えない', x['independence'], cid)
                self.assertIn(cid, UNOWN)
            else:
                self.assertIn('1 枚だけ', x['independence'], cid)
        # カードの画像だけで確かめたカードは、公式の書籍のページとの照合（CC-）にしない
        cc_cards = {x['card_id'] for x in load('data/sidecar/card_checks.json')['records']}
        self.assertFalse(cc_cards & (set(B_CARDS) | {'neo3-053', 'PR1-001', 'PR1-017'}))

    def test_book_checks_are_only_the_figures(self):
        ctx = bcr.load()
        # この作業のコミット（AT_COMMIT）にある記録で選ぶ（あとの作業の照合・最新の説明を混ぜない）
        then_cc = {x['id'] for x in at_commit('data/sidecar/card_checks.json')['records']}
        then_ld = {x['id'] for x in at_commit('data/sidecar/latest_descriptions.json')['records']}
        new_cc = ({x['id'] for x in ctx['checks']['records']} & then_cc) - {x['id'] for x in at_base('data/sidecar/card_checks.json')['records']}
        # 図版がそのカードの印刷のもの（figure）だけを照合（CC-）にする。見出しだけで当てはめたカード・カードの画像だけのカードは CC- にしない
        self.assertEqual(new_cc, {'CC-PR1-003-P127', 'CC-IP1-040-P127', 'CC-ES3-021-P156'})
        latest = {x['id']: x for x in ctx['latest']['records']}
        new_ld = (set(latest) & then_ld) - {x['id'] for x in at_base('data/sidecar/latest_descriptions.json')['records']}
        self.assertEqual(new_ld, {'LD-PR1-001-ATK0', 'LD-PR1-003-ATK0', 'LD-PR1-017-ATK0', 'LD-IP1-040-ATK0', 'LD-ES3-021-ATK1'})
        by = {i: (latest[i]['applies_to_print']['by'], latest[i]['printed_text']['image_check']) for i in new_ld}
        self.assertEqual(by, {'LD-PR1-003-ATK0': ('figure', 'consistent_where_legible'), 'LD-IP1-040-ATK0': ('figure', 'consistent_where_legible'),
                              'LD-ES3-021-ATK1': ('figure', 'consistent_where_legible'),
                              'LD-PR1-001-ATK0': ('heading_listing', 'not_checked'), 'LD-PR1-017-ATK0': ('heading_listing', 'not_checked')})
        for i in new_ld:  # 印刷の欄は印刷のまま（最新の説明で上書きしていない）
            x = latest[i]
            self.assertEqual(build_cardlist.get_field(ctx['cards'][x['card_id']], x['printed_text']['path']), x['printed_text']['text_ja'], i)
            self.assertEqual((x['classification'], x['errata_ref'], x['book_rule']), ('latest_description', None, 'GR-P43-P6-LATEST-DESCRIPTION'), i)
        self.assertIn('推論', latest['LD-PR1-017-ATK0']['applies_to_print']['basis'])  # トヨタのカードの特定は推論
        self.assertEqual({latest[i]['meaning_change'] for i in ('LD-PR1-001-ATK0', 'LD-PR1-003-ATK0', 'LD-PR1-017-ATK0', 'LD-ES3-021-ATK1')}, {'changed'})
        self.assertEqual(latest['LD-IP1-040-ATK0']['meaning_change'], 'none_apparent')

    def test_applies_to_print_misuse_is_rejected(self):
        ctx = bcr.load()
        self.assertEqual(bcr.validate(ctx), [])

        def errors(name, change):
            c = copy.deepcopy(ctx)
            change(next(x for x in c['latest']['records'] if x['id'] == name))
            return [e for e in bcr.validate(c) if name in e]

        self.assertTrue(errors('LD-PR1-017-ATK0', lambda x: x['applies_to_print'].update(by='figure')))  # 図版で照合していないのに figure
        self.assertTrue(errors('LD-PR1-003-ATK0', lambda x: x['applies_to_print'].update(by='heading_listing')))  # 図版で照合したのに見出しだけ
        self.assertTrue(errors('LD-PR1-001-ATK0', lambda x: x['printed_text'].update(image_check='match')))  # 見出しで当てはめたカードの印刷を図版で確かめたことにしない
        self.assertTrue(errors('LD-PR1-001-ATK0', lambda x: x['applies_to_print'].pop('basis')))
        self.assertTrue(errors('LD-ES3-021-ATK1', lambda x: x['applies_to_print'].update(by='same_artwork')))


class RulingTest(unittest.TestCase):
    """裁定・論点: 原典で確かめた範囲（CONFIRMED）と推論を含むもの（SUPPORTED）を分け、転記だけの根拠を画像の確認にしない。"""

    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()
        r = cls.ctx['rulings']
        cls.rulings = {x['id']: x for x in r['rulings']}
        cls.issues = {x['id']: x for x in r['issues']}

    def test_statuses_and_cards(self):
        base = at_base('data/sidecar/rulings.json')
        then = at_commit('data/sidecar/rulings.json')  # この作業のコミットの記録（あとの作業の裁定・論点・事例を含めない）
        then_issues = {x['id']: x for x in then['issues']}
        new = {x['id'] for x in then['rulings']} - {x['id'] for x in base['rulings']}
        self.assertEqual({i: self.rulings[i]['status'] for i in new},
                         {'CR-PIKACHU-GROWL-LATEST': 'CONFIRMED', 'CR-PIKACHU-GROWL-OPPONENT-EFFECT': 'SUPPORTED',
                          'CR-SLOWBRO-SNORE-WHILE-ASLEEP': 'CONFIRMED', 'CR-SLOWBRO-SNORE-AWAKE-FAILS': 'CONFIRMED',
                          'CR-SLOWBRO-SNORE-ONLY-THIS-ATTACK': 'SUPPORTED', 'CR-BORO-ROD-COIN-RESULTS': 'CONFIRMED',
                          'CR-BORO-ROD-POKEMON-CARDS': 'CONFIRMED'})
        for i in ('CR-PIKACHU-GROWL-LATEST', 'CR-PIKACHU-GROWL-OPPONENT-EFFECT'):
            # 3 枚とも独立に確かめたとは書かない: 図版・配布の見出しで当てはめた 3 枚と、推論で特定した PR1-017 を分ける
            self.assertEqual([c['card_id'] for c in self.rulings[i]['cards']], ['PR1-001', 'PR1-003', 'IP1-040'])
            self.assertEqual(self.rulings[i]['related_cards'], ['PR1-017'])
        self.assertEqual(set(then_issues) - {x['id'] for x in base['issues']}, {'UQ-GROWL-NON-ATTACK-DAMAGE'})
        q = self.issues['UQ-GROWL-NON-ATTACK-DAMAGE']
        self.assertEqual((q['status'], q['engine_refs'], q['recorded_after']), ('UNRESOLVED', [], {'import': 'ENGINE-2D113B5', 'date': '2026-10-30'}))
        # 既存の論点には事例と注記を追記しただけ（問い・状態・監査の日は変えない）
        for i, cid in (('UQ-COPIED-ATTACK', 'ES3-021'), ('UQ-CARD-USE-WITHOUT-TARGET', 'neo3-053')):
            old = next(x for x in base['issues'] if x['id'] == i)
            self.assertEqual({k: v for k, v in then_issues[i].items() if k not in ('cases', 'notes')}, {k: v for k, v in old.items() if k not in ('cases', 'notes')})
            for k in ('cases', 'notes'):
                self.assertEqual(then_issues[i][k][:len(old[k])], old[k], i)
            self.assertTrue(then_issues[i]['notes'][len(old['notes']):][0].startswith('2026-10-30: '), i)
            self.assertIn(cid, [c['card_id'] for c in then_issues[i]['cases'][len(old['cases']):]])
        self.assertEqual(then_issues['UQ-STATED-COUNT-SHORT'], next(x for x in base['issues'] if x['id'] == 'UQ-STATED-COUNT-SHORT'))

    def test_transcription_is_not_raised_to_image(self):
        for i in ('CR-BORO-ROD-POKEMON-CARDS', 'CR-SLOWBRO-SNORE-AWAKE-FAILS', 'CR-BORO-ROD-COIN-RESULTS'):
            for b in self.rulings[i]['basis']:
                if b.get('page') in ('312〜320', '310'):  # kyuura が今回の作業で画像を読んでいないページ
                    self.assertIn(b['checked'], ('existing_transcription', 'engine_report'), i)
        ctx = copy.deepcopy(self.ctx)
        b = next(b for b in next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-BORO-ROD-POKEMON-CARDS')['basis'] if b.get('transcription'))
        b['transcription']['quote'] = b['transcription']['quote'].replace('3つ', '2つ')
        self.assertTrue(any('転記の PDF' in e for e in bcr.validate(ctx)))
        ctx = copy.deepcopy(self.ctx)  # 推論を含む記録を CONFIRMED にしない
        next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-PIKACHU-GROWL-OPPONENT-EFFECT')['status'] = 'CONFIRMED'
        self.assertTrue(any('CR-PIKACHU-GROWL-OPPONENT-EFFECT' in e and 'inference' in e for e in bcr.validate(ctx)))

    def test_counts(self):
        # この作業のコミットの数（あとの作業の数は、その作業の検査が数える）
        then = dict(self.ctx, rulings=at_commit('data/sidecar/rulings.json'), latest=at_commit('data/sidecar/latest_descriptions.json'),
                    checks=at_commit('data/sidecar/card_checks.json'))
        r, latest, checks = then['rulings'], then['latest']['records'], then['checks']['records']
        self.assertEqual((len(latest), len(checks), len(r['rule_clauses']), len(r['rulings']), len(r['issues'])), (47, 84, 35, 315, 74))
        self.assertEqual(bcr.unresolved_counts(then)['research_issues'], 74)
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.113')['research_issues'], 72)  # 取り込んだ版の時点の数は変わらない


class RegistryTest(Data):
    """エンジンの登録表の写し（v0.113）は変えない。データを整えても実装済みにはならない。"""

    def test_snapshot_and_targets(self):
        self.assertEqual((ROOT / 'data/curation/engine_registered_cards.json').read_bytes(),
                         subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:data/curation/engine_registered_cards.json'],
                                        capture_output=True, check=True).stdout)
        snapshot = load('data/curation/engine_registered_cards.json')
        rows = {r['id']: r for r in at_commit('data/engine_targets.json')['cards']}  # この作業のコミットの一覧（あとの作業の名前の訂正の差を含めない）
        old = {r['id']: r for r in at_base('data/engine_targets.json')['cards']}
        registered = {i for i, r in rows.items() if r['engine_status'] == 'registered'}
        self.assertEqual(registered, set(snapshot['playable']))
        self.assertEqual(len(registered), 1250)
        self.assertEqual({i: r['engine_status'] for i, r in rows.items()}, {i: r['engine_status'] for i, r in old.items()})
        self.assertFalse(set(A_CARDS + B_CARDS) & registered)
        self.assertIn('IP1-040', registered)
        for cid in B_CARDS:
            self.assertEqual((old[cid]['category'], rows[cid]['category']), ('data_missing', 'candidate'), cid)
        changed = {i for i in rows if rows[i] != old[i]}
        self.assertEqual(changed, set(B_CARDS) | {'neo3-053'})
        self.assertEqual(Counter(r['category'] for r in rows.values()), Counter({'candidate': 1364, 'data_missing': 9, 'special_rule_design': 4}))
        self.assertEqual(rows['neo4-064']['category'], 'candidate')  # アンノーン W はこの作業で変えていない


if __name__ == '__main__':
    unittest.main()
