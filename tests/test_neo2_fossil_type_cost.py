"""neo2（遺跡をこえて...）の化石 4 枚のタイプとワザの必要なエネルギーの、カードの画像の照合（2026-10-30）の検査。

- kyuura-engine v0.120（8bb771f）の docs/fossil-basic-virtual-attacks-v0.120.md が、カブト（neo2-014）・カブトプス（neo2-018）のタイプ「水」と
  ワザの「闘」、オムナイト（neo2-032）・オムスター（neo2-035）のタイプ「闘」とワザの「水」を、タイプの写しの入れ違いの候補として報告した。
- 4 枚それぞれの日本語版のカードの画像（pcg-search.com [N3]・なぞのばしょ [N1]）で、タイプの記号と各ワザのコストの記号を読んだ
  （data/curation/card_image_checks.json の IMG-）。4 枚とも今までの値と同じなので、訂正はない（before と after が同じ訂正を作らない）。
- カードの画像の照合で、公式の書籍の照合（CC-）・最新の説明（LD-）・公式エラッタではない。
"""
import copy
import csv
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_cardlist  # noqa: E402

BASE = 'c932625053f4cd4d784585f8b6144121499d85ed'  # この作業の基点（次の便のカードの文面と進化データの調査）
AT_COMMIT = '2fe0bc042ce187d191843819262f8036abbb343d'  # この作業のコミット（あとの作業の訂正・記録と分けるため）
# 画像で読んだ値: カード id → （タイプ, [各ワザのコスト]）
PRINTED = {
    'neo2-014': (['water'], [['fighting', 'colorless']]),
    'neo2-018': (['water'], [['colorless'], ['fighting']]),
    'neo2-032': (['fighting'], [['water']]),
    'neo2-035': (['fighting'], [['water'], ['water', 'water', 'water']]),
}
OTHER_VERSION = {'neo2-014': 'PMCG3-035'}  # 同じ名前の別の版（化石の秘密のカブト。タイプは闘）


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def at_base(rel, commit=BASE):
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{rel}'], capture_output=True, text=True, check=True).stdout


class Fossils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.images = load('data/curation/card_image_checks.json')
        cls.checks = {x['card_id']: x for x in cls.images['checks'] if x['card_id'] in PRINTED}

    def test_image_records_read_type_and_each_cost(self):
        self.assertEqual(set(self.checks), set(PRINTED))
        for cid, (types, costs) in PRINTED.items():
            x = self.checks[cid]
            self.assertEqual((x['id'], x['kind'], x['checked_on'], x['card_name_ja']),
                             (f'IMG-{cid}', 'card_image_check', '2026-10-30', self.by_id[cid]['name']['ja']))
            expected = {'pokemon.types': types}
            for i, cost in enumerate(costs):
                expected[f'pokemon.attacks[{i}].cost'] = cost
                expected[f'pokemon.attacks[{i}].cost_total'] = len(cost)
            self.assertEqual(x['print_values'], expected, cid)  # 読んだのはタイプとワザのコストだけ（弱点・HP などは確かめた欄にしない）
            self.assertEqual(len(self.by_id[cid]['pokemon']['attacks']), len(costs), cid)  # すべてのワザのコストを読んだ
            # 画像は 2 つのサイトに 1 枚ずつ。独立した 2 件に数えない。サイトの転記は画像と分ける
            self.assertEqual([i['site'] for i in x['images']], ['pcg-search.com [N3]', 'なぞのばしょ [N1]'])
            self.assertIn('独立した 2 枚の実物の照合とは数えない', x['independence'])
            for t in x['site_transcriptions']:
                self.assertNotIn('image_sha256', t)
                self.assertEqual(t['values'], {k: v for k, v in expected.items() if not k.endswith('cost_total')})
            self.assertIn('pokemon.types', x['print_text'])

    def test_values_match_and_no_correction_is_made(self):
        fields = ('pokemon.types', 'pokemon.attacks')
        for cid, (types, costs) in PRINTED.items():
            p = self.by_id[cid]['pokemon']
            self.assertEqual(p['types'], types, cid)
            self.assertEqual([a['cost'] for a in p['attacks']], costs, cid)
            self.assertEqual([a['cost_total'] for a in p['attacks']], [len(c) for c in costs], cid)
            # 画像が今までの値と同じなので、訂正（before と after が同じ偽の訂正も）・候補を作らない
            self.assertEqual(self.checks[cid]['corrections'], [])
            self.assertFalse([c for c in self.ledger['corrections'] if c['card_id'] == cid and c['field'].startswith(fields)], cid)
            self.assertFalse([c for c in self.ledger['candidates'] if c['card_id'] == cid and c['field'].startswith(fields)], cid)
            self.assertNotIn('corrections', self.by_id[cid])
        self.assertFalse([c['id'] for c in self.ledger['corrections'] if c['applied_by'] == 'card_corrections' and c['before'] == c['after']])

    def test_card_data_is_unchanged_from_base(self):
        # この作業（基点 c932625 → 2fe0bc0）は照合の記録を加えただけで、カードの値・CSV・訂正の記録は基点と同じ（1,377 件と id の集合も同じ）。
        # あとの作業（2026-10-30 の名前の訂正など）の変更と分けるため、この作業のコミットの記録で比べる
        for rel in ('data/cards.json', 'data/cards.csv', 'data/attacks.csv', 'data/curation/card_corrections.json',
                    'data/engine_targets.json', 'data/curation/engine_registered_cards.json',
                    'data/sidecar/latest_descriptions.json', 'data/sidecar/card_checks.json', 'data/sidecar/rulings.json'):
            self.assertEqual(at_base(rel, AT_COMMIT), at_base(rel), rel)
        self.assertEqual(len(self.cards), 1377)
        old = {x['id'] for x in json.loads(at_base('data/curation/card_image_checks.json'))['checks']}
        then = {x['id'] for x in json.loads(at_base('data/curation/card_image_checks.json', AT_COMMIT))['checks']}
        self.assertEqual(then - old, {f'IMG-{c}' for c in PRINTED})
        # この作業のコミットでも、4 枚の記録は基点と同じ（時点を固定して比べる。2026-10-31 の目録の分類の欄の追加など、あとの作業の変更と分ける）
        base_cards = {c['id']: c for c in json.loads(at_base('data/cards.json'))['cards']}
        then_cards = {c['id']: c for c in json.loads(at_base('data/cards.json', AT_COMMIT))['cards']}
        for cid in PRINTED:
            self.assertEqual(then_cards[cid], base_cards[cid], cid)
        # 今の値は、目録の分類の欄（catalog_class・engine_scope・engine_scope_reason）のほかは、この作業のときと同じ
        for cid in PRINTED:
            now = {k: v for k, v in self.by_id[cid].items() if k not in ('catalog_class', 'engine_scope', 'engine_scope_reason')}
            self.assertEqual(now, then_cards[cid], cid)

    def test_json_and_csv_agree(self):
        rows = {r['id']: r for r in csv.DictReader(io.StringIO((ROOT / 'data' / 'cards.csv').read_text(encoding='utf-8')))}
        attacks = {(r['card_id'], int(r['index'])): r for r in csv.DictReader(io.StringIO((ROOT / 'data' / 'attacks.csv').read_text(encoding='utf-8')))}
        for cid, (types, costs) in PRINTED.items():
            self.assertEqual(rows[cid]['types'].split(), types, cid)
            for i, cost in enumerate(costs, 1):  # attacks.csv の index は 1 から
                self.assertEqual((attacks[(cid, i)]['cost'].split(), int(attacks[(cid, i)]['cost_total'])), (cost, len(cost)), (cid, i))

    def test_mismatches_are_rejected(self):
        records = [copy.deepcopy(c) for c in self.cards]
        ok = (records, copy.deepcopy(self.images), copy.deepcopy(self.ledger))
        build_cardlist.check_image_checks(*ok)

        def img(doc, cid):
            return next(x for x in doc['checks'] if x['card_id'] == cid)

        def rejected(change):
            recs, doc, led = copy.deepcopy(ok)
            change(recs, doc, led)
            with self.assertRaises(SystemExit):
                build_cardlist.check_image_checks(recs, doc, led)

        # 再生成で値が変わったら（英語版のデータの差しかえ・タイプをそろえる変更など）、画像の記録と合わずに止まる
        rejected(lambda r, d, l: next(c for c in r if c['id'] == 'neo2-014')['pokemon'].update(types=['fighting']))
        rejected(lambda r, d, l: next(c for c in r if c['id'] == 'neo2-035')['pokemon']['attacks'][1].update(cost=['fighting'] * 3))
        rejected(lambda r, d, l: next(c for c in r if c['id'] == 'neo2-018')['pokemon']['attacks'][1].update(cost_total=2))
        # 画像の値の書きかえ・別の版（化石の秘密のカブト）への当てはめ・参照切れは止まる
        rejected(lambda r, d, l: img(d, 'neo2-032')['print_values'].update({'pokemon.types': ['water']}))
        rejected(lambda r, d, l: img(d, 'neo2-014').update(card_id=OTHER_VERSION['neo2-014'], id=f"IMG-{OTHER_VERSION['neo2-014']}"))
        rejected(lambda r, d, l: img(d, 'neo2-018')['corrections'].append('FIX-NOT-THERE'))
        rejected(lambda r, d, l: d['checks'].append(copy.deepcopy(img(d, 'neo2-035'))))  # id の重複

    def test_a_correction_must_match_the_current_value_and_the_image(self):
        # 訂正を作るなら、before は今の値、after は画像の値（どちらかが違えば止まる）。今回は作らない
        fix = {'id': 'FIX-neo2-032-TYPES', 'card_id': 'neo2-032', 'card_name_ja': 'オムナイト', 'field': 'pokemon.types',
               'before': ['water'], 'after': ['fighting'], 'kind': 'transcription_error', 'applied_by': 'card_corrections',
               'decided_on': '2026-10-30', 'basis': 'card_image_check', 'image_check': 'IMG-neo2-032', 'basis_detail': '検査用',
               'card_checks_affected': []}
        rec = copy.deepcopy(self.by_id['neo2-032'])
        with self.assertRaises(SystemExit):  # before（水）が今の値（闘）と違う
            build_cardlist.apply_corrections([rec], {'corrections': [fix], 'candidates': []})
        swapped = dict(fix, before=['fighting'], after=['water'])  # タイプを「入れ違い」として直す訂正は画像と合わない
        led = copy.deepcopy(self.ledger)
        led['corrections'].append(swapped)
        doc = copy.deepcopy(self.images)
        next(x for x in doc['checks'] if x['card_id'] == 'neo2-032')['corrections'].append(swapped['id'])
        records = [copy.deepcopy(c) for c in self.cards]
        build_cardlist.apply_corrections(records, {'corrections': [swapped], 'candidates': []})
        with self.assertRaises(SystemExit):
            build_cardlist.check_image_checks(records, doc, led)

    def test_engine_snapshot_and_status_are_unchanged(self):
        snapshot = load('data/curation/engine_registered_cards.json')
        self.assertEqual(snapshot['engine']['version'], 'v0.113')  # v0.120 は取り込まない
        rows = {r['id']: r for r in load('data/engine_targets.json')['cards']}
        playable = set(snapshot['playable'])
        for cid in PRINTED:
            self.assertEqual(rows[cid]['engine_status'] == 'registered', cid in playable, cid)
        self.assertEqual({c for c in PRINTED if c in playable}, {'neo2-018', 'neo2-035'})  # v0.113 の写しの時点（v0.120 では 4 枚とも登録）


if __name__ == '__main__':
    unittest.main()
