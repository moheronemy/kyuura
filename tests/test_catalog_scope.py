"""目録（data/cards.csv）の収録範囲と分類の検査（2026-10-31）。

- 目録の一覧: data/cards.csv は data/cards.json の記録・data/product_items.json の non_game_items・data/curation/catalog_items.json
  から scripts/catalog.py が作る（手で追記しない）。
- 分類: 目録の分類（catalog_class）・通常対戦での使用範囲（play_scope）・通常対戦のエンジンの対象（engine_scope）を別の欄にする。
- 利用者の指定（2026-10-31）による移管: タッチ交代！ PR1-038・タッチ世代交代！ PRN-048（専用ルール用）、カードトレーナー認定証 PR1-079
  （認定・賞品）を通常対戦のエンジンの対象から外す。公式の裁定・エラッタ・印刷の訂正ではない。
- 追加: 『ポケモンカードオフィシャルブック2000』[P43]（kyuura の記録 id: data/rule_history.json の documents の P43）の
  p.300〜301（入賞賞品カード 15）・p.251（スペシャルジャンボカード 8）・p.122（トロピカルプレゼント）を図版で読んだ（スキャン [J38]）。
- 比較: Bulbapedia の番号なしプロモの一覧 [X48]（data/curation/promo_survey.json）。
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
import catalog  # noqa: E402

BASE = '0dadab8ca33e43dfc2114b617ac4281b7eb58de2'  # この作業の基点
MOVED = {'PR1-038': ('special_rule', 'kangaskhan_rule'), 'PRN-048': ('special_rule', 'kangaskhan_rule'),
         'PR1-079': ('award', 'standard')}
NEW_FIELDS = ('catalog_class', 'engine_scope', 'engine_scope_reason')
KC_REGISTERED = {f'KC-{i:04d}' for i in range(1, 25)}  # 2026-10-31 に割り当てた id（消さない・使い回さない）


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def at_base(rel):
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{rel}'], capture_output=True, text=True, check=True).stdout


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.items = load('data/product_items.json')
        cls.cat = load('data/curation/catalog_items.json')
        cls.survey = load('data/curation/promo_survey.json')
        cls.np = load('data/curation/non_pack.json')
        with open(ROOT / 'data' / 'cards.csv', encoding='utf-8', newline='') as f:
            cls.csv_text = f.read()
        cls.rows = list(csv.DictReader(io.StringIO(cls.csv_text)))
        cls.row = {r['id']: r for r in cls.rows}


class GenerationTest(Data):
    def test_csv_is_generated_from_the_sources(self):
        # CSV と生成元（data/cards.json・non_game_items・catalog_items.json）が同じ。id・参照・分類の検査も通る
        self.assertEqual(catalog.check(), [])
        groups = {p['id']: p['group'] for p in self.items['products']}
        text = catalog.render_csv(catalog.rows(self.cards, self.items['non_game_items'], self.cat, groups,
                                               load('data/curation/card_image_checks.json')))
        self.assertEqual(text, self.csv_text)

    def test_columns_are_appended_and_old_values_are_kept(self):
        old = list(csv.reader(io.StringIO(at_base('data/cards.csv'))))
        new = list(csv.reader(io.StringIO(self.csv_text)))
        self.assertEqual(new[0][:len(old[0])], old[0])  # 既存の欄の位置は変えない
        self.assertEqual(new[0][len(old[0]):], catalog.CATALOG_COLUMNS)
        for a, b in zip(old[1:], new[1:]):
            self.assertEqual(b[:len(a)], a, a[0])  # 既存の行の既存の欄の値は同じ（基点の行は同じ順で先頭にある）

    def test_card_records_are_unchanged_except_the_new_fields(self):
        old = json.loads(at_base('data/cards.json'))
        new = load('data/cards.json')
        self.assertEqual({k: v for k, v in old.items() if k != 'cards'}, {k: v for k, v in new.items() if k != 'cards'})
        self.assertEqual([c['id'] for c in old['cards']], [c['id'] for c in new['cards']])
        for a, b in zip(old['cards'], new['cards']):
            self.assertEqual(a, {k: v for k, v in b.items() if k not in NEW_FIELDS}, a['id'])
        # 拡張パック以外の商品の元の項目の行き先・同じカードの組も変えていない（counts の通常の対戦のカードの数のほか）
        old_items = json.loads(at_base('data/product_items.json'))
        self.assertEqual(old_items['items'], self.items['items'])
        self.assertEqual(old_items['non_game_items'], self.items['non_game_items'])
        self.assertEqual(at_base('data/same_card_groups.json'), (ROOT / 'data' / 'same_card_groups.json').read_text(encoding='utf-8'))

    def test_engine_snapshot_and_sidecar_are_not_rewritten(self):
        for rel in ('data/curation/engine_registered_cards.json', 'data/sidecar/rulings.json', 'data/sidecar/card_checks.json',
                    'data/sidecar/latest_descriptions.json', 'data/curation/card_corrections.json', 'data/curation/card_image_checks.json'):
            self.assertEqual(at_base(rel), (ROOT / rel).read_text(encoding='utf-8'), rel)


class IdTest(Data):
    def test_ids_are_unique_and_existing_ids_are_kept(self):
        ids = [r['id'] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        before = {r['id'] for r in csv.DictReader(io.StringIO(at_base('data/cards.csv')))}
        before |= {x['id'] for x in json.loads(at_base('data/product_items.json'))['non_game_items']}
        self.assertLessEqual(before, set(ids))  # 既存の id（記録・対象外の項目）は分類を変えても残る
        self.assertLessEqual(KC_REGISTERED, {x['id'] for x in self.cat['items']})  # 割り当てた KC- の id は消さない
        for x in self.cat['items']:
            self.assertRegex(x['id'], r'^KC-\d{4}$')
            self.assertNotIn(x['id'], before)

    def test_no_duplicate_of_existing_entries(self):
        names = Counter(x['name_ja'] for x in self.cat['items'])
        self.assertNotIn('ポケモンイラストレーター', names)  # PR1-015（non_game_items）があるので重ねて登録しない
        self.assertNotIn('トロピカルウインド', names)  # PR1-074 がある
        self.assertEqual(self.row['PR1-015']['catalog_class'], 'award')
        self.assertEqual(self.row['PR1-074']['catalog_class'], 'battle')

    def test_csv_and_schema_say_ids_are_internal(self):
        schema = (ROOT / 'docs' / 'data-schema.md').read_text(encoding='utf-8')
        self.assertIn('内部識別子', schema)
        self.assertIn('公式のカード番号ではない', schema)
        self.assertIn('内部識別子', self.cat['id_rule'])
        # 公式の番号は確かめたものだけ入れる（今は確かめた番号がない）
        self.assertEqual({r['official_number'] for r in self.rows}, {''})


class ScopeTest(Data):
    def test_moved_cards_keep_their_record(self):
        old = {c['id']: c for c in json.loads(at_base('data/cards.json'))['cards']}
        des = self.np['catalog_scope']
        for cid, (cls, play) in MOVED.items():
            c = self.by_id[cid]
            self.assertEqual({k: v for k, v in c.items() if k not in NEW_FIELDS}, old[cid])  # 記録・文面・出典・id は同じ
            self.assertEqual((c['catalog_class'], c['play_scope'], c['engine_scope']), (cls, play, 'excluded'))
            self.assertTrue(c['engine_scope_reason'])
            self.assertIn('利用者の指定', des[cid]['basis'])
            self.assertIn('公式の裁定・エラッタ・印刷の訂正ではない', des[cid]['basis'])
            for word in ('使用禁止', '遊べない'):
                self.assertNotIn(word, c['engine_scope_reason'])
        # タッチ系 2 枚は専用ルールで使うカードという事実を残す（play_scope と補足欄の表示）
        for cid in ('PR1-038', 'PRN-048'):
            self.assertIn('専用', self.by_id[cid]['engine_scope_reason'])
            self.assertTrue(any('ガルーラルール専用' in n for n in self.by_id[cid]['notes']))
        # 訂正・エラッタとして記録していない
        corr = load('data/curation/card_corrections.json')
        self.assertFalse([x for x in corr['corrections'] if x.get('card_id') in MOVED])
        errata = json.dumps(load('data/rule_history.json')['errata'], ensure_ascii=False)
        for cid in MOVED:
            self.assertEqual(errata.count(cid), json.dumps(json.loads(at_base('data/rule_history.json'))['errata'], ensure_ascii=False).count(cid))

    def test_battle_extraction_uses_the_explicit_classes(self):
        battle = {r['id'] for r in catalog.battle_records(self.cards)}
        self.assertEqual({r['id'] for r in catalog.battle_rows(self.csv_text)}, battle)
        self.assertFalse(battle & set(MOVED))
        self.assertFalse(battle & {x['id'] for x in self.items['non_game_items']})
        self.assertFalse(battle & {x['id'] for x in self.cat['items']})
        targets = load('data/engine_targets.json')
        self.assertEqual({r['id'] for r in targets['cards']}, battle)
        self.assertEqual({x['id'] for x in targets['excluded_records']}, set(MOVED))
        # 未実装の件数（new_effect_needed）にも、対象外の記録・目録だけの行は入らない
        self.assertFalse({r['id'] for r in targets['cards'] if r['engine_status'] == 'new_effect_needed'} & set(MOVED))

    def test_kangaskhan_rule_needs_an_explicit_designation(self):
        records = copy.deepcopy(self.cards)
        np_ = copy.deepcopy(self.np)
        del np_['catalog_scope']['PRN-048']
        with self.assertRaises(SystemExit):
            catalog.apply_catalog_scope(records, np_)
        np_ = copy.deepcopy(self.np)
        np_['catalog_scope']['PR1-079']['page'] = '1stp080'
        with self.assertRaises(SystemExit):
            catalog.apply_catalog_scope(copy.deepcopy(self.cards), np_)
        np_ = copy.deepcopy(self.np)
        np_['catalog_scope']['PR1-079']['engine_scope_reason'] = ''
        with self.assertRaises(SystemExit):
            catalog.apply_catalog_scope(copy.deepcopy(self.cards), np_)

    def test_broken_data_is_detected(self):
        def errs(cards=None, items=None, cat=None, survey=None):
            return catalog.problems(cards or self.cards, items or self.items, cat or self.cat, survey or self.survey)
        self.assertEqual(errs(), [])
        cat = copy.deepcopy(self.cat)
        cat['items'][0]['id'] = 'PR1-038'
        self.assertTrue(any('重複' in e for e in errs(cat=cat)))
        cat = copy.deepcopy(self.cat)
        cat['items'][0]['hp'] = 60
        self.assertTrue(any('対戦のカードの欄' in e for e in errs(cat=cat)))
        cat = copy.deepcopy(self.cat)
        cat['items'][0]['catalog_class'] = 'battle'
        self.assertTrue(errs(cat=cat))
        cat = copy.deepcopy(self.cat)
        cat['items'][-1]['related_ids'] = ['PR1-999']
        self.assertTrue(any('related_ids' in e for e in errs(cat=cat)))
        survey = copy.deepcopy(self.survey)
        survey['comparisons'][0]['entries'][0]['catalog_ids'] = ['KC-9999']
        self.assertTrue(any('catalog_ids がない' in e for e in errs(survey=survey)))
        cards = copy.deepcopy(self.cards)
        next(c for c in cards if c['id'] == 'PR1-038')['catalog_class'] = 'battle'
        self.assertTrue(any('専用ルール' in e for e in errs(cards=cards)))

    def test_breakdown(self):
        # 2026-10-31 の内訳（総数を固定条件にしない。分類ごとの根拠: 記録 1,377 のうち移管 3、non_game_items 18、書籍で確かめた追加 24）
        c = Counter((r['catalog_class'], r['engine_scope']) for r in self.rows)
        self.assertEqual(c[('battle', 'target')], len(self.cards) - len(MOVED))
        self.assertEqual(c[('special_rule', 'excluded')], 2)
        self.assertEqual(c[('jumbo', 'excluded')], 8)
        # 認定・賞品: ポケモンイラストレーター PR1-015・カードトレーナー認定証 PR1-079・入賞賞品カード 15・トロピカルプレゼント
        self.assertEqual(c[('award', 'excluded')], 1 + 1 + 15 + 1)
        self.assertEqual(sum(n for (k, s), n in c.items() if k in ('extra_rule', 'deck_recipe', 'joke_card', 'pass_card', 'other')),
                         len(self.items['non_game_items']) - 1)
        self.assertEqual(len(self.rows), len(self.cards) + len(self.items['non_game_items']) + len(self.cat['items']))


class ResearchTest(Data):
    def test_prize_cards_are_fifteen_prints_with_texts(self):
        prizes = [x for x in self.cat['items'] if x['group_ja'].endswith('入賞賞品カード')]
        self.assertEqual(len(prizes), 15)  # 5 群 × No.1〜No.3 の掲載枠。本文が群ごとに違うので 15 の別の印刷物
        self.assertEqual(len({(x['group_ja'], x['name_ja']) for x in prizes}), 15)
        self.assertEqual(len({x['printed_text_ja'] for x in prizes}), 15)
        tropical = [x for x in prizes if x['group_ja'].startswith('トロピカル')]
        self.assertIn('参加権', tropical[0]['printed_text_ja'])
        self.assertNotIn('参加権', tropical[1]['printed_text_ja'])
        self.assertTrue(all(x['research_status'] == 'book_image_read' for x in prizes))

    def test_jumbo_cards_are_listed_not_merged(self):
        jumbo = [x for x in self.cat['items'] if x['catalog_class'] == 'jumbo']
        self.assertEqual(len(jumbo), 8)  # p.251 の掲載。全件とは断定しない（未確認に書く）
        for x in jumbo:
            self.assertIsNone(x['printed_text_ja'])  # 図版の文字は転記していない
            self.assertTrue(any('全件とは限らない' in u for u in x['unconfirmed']))
        charizard = next(x for x in jumbo if x['name_ja'].startswith('Charizard'))
        self.assertIn('CONFLICT', charizard['date'])

    def test_tropical_present(self):
        tp = next(x for x in self.cat['items'] if x['name_ja'] == 'トロピカルプレゼント')
        self.assertEqual(tp['related_ids'], ['PR1-074'])
        self.assertEqual(tp['sources'][0]['pages'], ['122'])
        self.assertIn('ゲットGETポイント', tp['printed_text_ja'])
        self.assertTrue(any('読めない' in u for u in tp['unconfirmed']))

    def test_survey_covers_every_existing_promo(self):
        x48 = self.survey['comparisons'][0]
        self.assertEqual(x48['source'], 'X48')
        promo_ids = {it['id'] for it in self.items['items'] if it['product'] in ('PR1', 'PRN')}
        existing = {i for e in x48['entries'] if e['status'] == 'existing' for i in e['catalog_ids']}
        self.assertEqual(existing, promo_ids)  # pcg-search のプロモの項目はすべて独立した一覧の項目と対応した
        self.assertEqual(Counter(e['status'] for e in x48['entries']),
                         {'existing': 138, 'existing_other_product': 27, 'added': 24, 'addition_candidate': 28,
                          'variant_candidate': 4, 'unconfirmed': 30, 'out_of_scope': 21})
        for e in x48['entries']:
            if e['status'] == 'out_of_scope':
                self.assertNotIn('大会賞品', e['note'][:4])
            if e['year'] == '2002':
                self.assertNotEqual(e['status'], 'out_of_scope')  # 2002年だから自動では除外しない

    def test_book_pages_are_recorded(self):
        p43 = next(d for d in load('data/rule_history.json')['documents'] if d['code'] == 'P43')
        pages = {p['printed'] for p in p43['pages']}
        self.assertLessEqual({'122', '251', '300', '301'}, pages)


if __name__ == '__main__':
    unittest.main()
