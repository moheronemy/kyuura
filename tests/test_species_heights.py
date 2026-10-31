"""公式図鑑の種族の身長の参照データ（data/species_heights.json）の検査（2026-10-31）。

- 「カツラのクイズ その1」（GD5-016 ほか。data/cards.json）の実装の準備。集めるのは公式図鑑の種族の身長で、
  カードに印刷された身長ではない。カードの欄を補完・訂正しない（data/cards.json・data/cards.csv は変えない）。
- 2026-10-31 は公式の資料（SRC-ZUKAN-JP）に接続できず、251 件すべて未確認（値は null。0cm にしない）。
- 抜き出しのテストのページは、この検査のために作った架空のもの（名前「テストモン」）で、公式の資料ではない。
  公式ずかんのページの形と照らしていない（docs/species-heights.md 4 章）。
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import species_heights as sh  # noqa: E402

BASE = '71d1728938fb4c8fefde9b82779cdef74beb612d'  # この作業の基点（main）


def synthetic_page(no='0001', name='テストモン', takasa='1.5m', sub='0', extra=None):
    """架空の詳細ページ（2026-10-31 に確かめた公式ずかんのページの形だけをまねたもの。値は公式ではない）。"""
    extra = extra or {}
    page = f'{no}' if str(sub) in ('0', '') else f'{no}-{sub}'
    subname = f'<span class="subname">{extra["sub_name"]}</span>' if extra.get('sub_name') else ''
    return (f'<html><head><meta property="og:url" content="https://zukan.pokemon.co.jp/detail/{page}"></head><body>'
            f'<h2 class="ttl__detail">\n<small class="no">No.{no}</small>\n<span class="name">{name}</span>\n{subname}</h2>'
            f'<dl><dt class="header__detail-features">高さ：</dt><dd class="content__detail-features js-height">{takasa}</dd></dl>'
            f'<dd class="content__detail-features js-weight">1.0kg</dd></body></html>').encode('utf-8')


def load_cards():
    return json.loads(sh.CARDS.read_text(encoding='utf-8'))['cards']


class NormalizeTest(unittest.TestCase):
    def test_metres_to_integer_cm(self):
        for raw, cm in [('0.7m', 70), ('8.8m', 880), ('1.0 m', 100), ('14.5m', 1450), ('0.2m', 20),
                        ('2m', 200), ('70cm', 70), ('0.7ｍ', 70)]:
            self.assertEqual(sh.normalize_height_cm(raw), cm, raw)

    def test_rejects_unreadable_zero_and_fractional_cm(self):
        for raw in ['', '0m', '0.0m', '0.755m', '0.7', 'abc', '-1m', None, '0.7 kg']:
            with self.assertRaises(ValueError, msg=raw):
                sh.normalize_height_cm(raw)


class ParseTest(unittest.TestCase):
    def test_reads_embedded_json(self):
        ext = sh.parse_zukan_jp(synthetic_page())
        self.assertEqual(ext, {'no': 1, 'sub': 0, 'name': 'テストモン', 'form_name': '', 'takasa': '1.5m'})

    def test_form_name(self):
        ext = sh.parse_zukan_jp(synthetic_page(sub='1', extra={'sub_name': 'べつのすがた'}))
        self.assertEqual((ext['sub'], ext['form_name']), (1, 'べつのすがた'))

    def test_fails_closed(self):
        good = synthetic_page()
        for body in [b'<html></html>', good.replace(b'og:url', b'og:x'), good.replace(b'js-height', b'js-x'),
                     good.replace(b'No.0001', b'No.0002'), good.replace(b'class="name"', b'class="x"'),
                     good + good.split(b'<body>')[1], synthetic_page(takasa='')]:
            with self.assertRaises(sh.ParseError):
                sh.parse_zukan_jp(body)

    def test_number_mismatch(self):
        with self.assertRaises(ValueError):
            sh.make_observation('SRC-ZUKAN-JP', 2, 'u', '2026-10-31', synthetic_page(no='0001'))


def observation(dex=1, takasa='1.5m', name='テストモン', **kw):
    return sh.make_observation('SRC-ZUKAN-JP', dex, sh.SOURCES['SRC-ZUKAN-JP']['detail_url'].format(dex=dex),
                               '2026-10-31', synthetic_page(no=f'{dex:04d}', name=name, takasa=takasa, **kw))


class CurrentDataTest(unittest.TestCase):
    def setUp(self):
        self.data = sh.load_data()
        self.cards = load_cards()

    def test_check_passes(self):
        self.assertEqual(sh.check_data(self.data, self.cards), [])

    def test_values_only_when_confirmed(self):
        """未確認・食い違い・要確認の項目に値・名前を入れない（0cm にしない）。確認済みは観測の値と同じ。"""
        self.assertEqual(sh.counts(self.data)['total'], 251)
        for e in self.data['species']:
            if e['status'] == 'confirmed':
                self.assertGreater(e['height']['cm'], 0)
                self.assertEqual(e['height']['cm'], e['observations'][0]['cm'])
                self.assertEqual(e['name_ja'], e['observations'][0]['name_ja'])
            else:
                self.assertIsNone(e['height']['cm'])
                self.assertIsNone(e['name_ja'])
        log = self.data['sources']['SRC-ZUKAN-JP']['access_log']
        self.assertEqual((log[0]['date'], log[0]['result']), ('2026-10-31', 'blocked'))  # 最初は接続できなかった

    def test_probe_values(self):
        """試し取り（2026-10-31）の 3 件。公式ずかんの詳細ページの「高さ」の原表記と換算。"""
        idx = sh.species_index(self.data)
        for dex, name, raw, cm in [(1, 'フシギダネ', '0.7m', 70), (25, 'ピカチュウ', '0.4m', 40), (201, 'アンノーン', '0.5m', 50)]:
            e = idx[dex]
            self.assertEqual((e['status'], e['name_ja'], e['height']['raw'], e['height']['cm']), ('confirmed', name, raw, cm))
            self.assertEqual(e['form'], {'kind': 'default', 'source_form_id': 0, 'form_name': None})

    def test_full_range_collected(self):
        """2026-10-31 に No.001〜251 をすべて公式ずかんから取得した（未確認・食い違い・要確認 0）。"""
        self.assertEqual(sh.counts(self.data), {'unverified': 0, 'confirmed': 251, 'conflict': 0, 'needs_review': 0,
                                                'total': 251})
        idx = sh.species_index(self.data)
        for e in self.data['species']:
            self.assertEqual(e['form']['source_form_id'], 0)
            self.assertIsNone(e['form']['form_name'])
            self.assertEqual(e['observations'][0]['retrieved_on'], '2026-10-31')
        self.assertEqual(len({e['name_ja'] for e in self.data['species']}), 251)
        self.assertEqual((idx[95]['height']['raw'], idx[95]['height']['cm']), ('8.8m', 880))  # イワーク（3 桁 cm）
        # 公式の表記は全角数字。カード名「ポリゴン2」との照合だけ NFKC でそろえる（記録する名前は変えない）
        self.assertEqual(idx[233]['name_ja'], 'ポリゴン２')

    def test_name_check_uses_nfkc_only_for_matching(self):
        e = sh.blank_entry(1)
        e['observations'] = [observation(name='テストモン２')]
        sh.resolve_status(e, {1: {'わるいテストモン2'}})
        self.assertEqual((e['status'], e['name_ja']), ('confirmed', 'テストモン２'))

    def test_only_official_sources(self):
        self.assertEqual(set(self.data['sources']), {'SRC-ZUKAN-JP'})
        self.assertTrue(all(v['official'] for v in self.data['sources'].values()))
        names = ' '.join(x['name'] for x in self.data['excluded_sources'])
        self.assertIn('PokeAPI', names)

    def test_cards_link_only_by_dex(self):
        """カードとは pokemon.dex だけで結ぶ。dex のないカード（227 枚）を名前から推測して結ばない。"""
        cards = {c['id']: c for c in self.cards}
        self.assertEqual([e['dex'] for e in sh.species_for_card(cards['PMCG5-007'], self.data)], [1])  # エリカのフシギダネ
        self.assertEqual(sh.species_for_card(cards['ES1-001'], self.data), [])
        self.assertEqual(sh.species_for_card(cards['GD5-016'], self.data), [])  # トレーナー（カツラのクイズ その1）
        rep = sh.link_report(self.cards, self.data)
        self.assertEqual((rep['pokemon_cards'], rep['linked_by_dex'], rep['without_dex']), (1068, 841, 227))
        self.assertEqual(rep['dex_out_of_range'], [])


class CardsUnchangedTest(unittest.TestCase):
    def test_card_data_and_catalog_unchanged(self):
        for rel in ('data/cards.json', 'data/cards.csv', 'data/attacks.csv', 'data/powers.csv'):
            base = subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{rel}'], capture_output=True,
                                  check=True).stdout
            self.assertEqual((ROOT / rel).read_bytes(), base, rel)


class DestructiveTest(unittest.TestCase):
    def setUp(self):
        self.data = sh.skeleton()
        for e in self.data['species']:
            e['status_reason'] = 'source_unreachable'

    def errs(self, data=None):
        return sh.check_data(data or self.data)

    def test_skeleton_ok(self):
        self.assertEqual(self.errs(), [])

    def test_duplicate_missing_and_out_of_range(self):
        d = copy.deepcopy(self.data)
        d['species'][1] = copy.deepcopy(d['species'][0])
        self.assertTrue(any('重複' in e for e in self.errs(d)))
        self.assertTrue(any('欠け' in e for e in self.errs(d)))
        d = copy.deepcopy(self.data)
        d['species'].append(sh.blank_entry(252) | {'status_reason': 'x'})
        self.assertTrue(any('範囲の外' in e for e in self.errs(d)))

    def test_unverified_must_not_have_zero(self):
        d = copy.deepcopy(self.data)
        d['species'][0]['height']['cm'] = 0
        self.assertTrue(any('値を入れない' in e for e in self.errs(d)))

    def test_confirmed_from_observation(self):
        e = self.data['species'][0]
        e['observations'] = [observation()]
        sh.resolve_status(e)
        self.assertEqual((e['status'], e['height']['cm'], e['height']['raw'], e['name_ja']), ('confirmed', 150, '1.5m', 'テストモン'))
        self.assertEqual(self.errs(), [])

    def test_conflict_keeps_both(self):
        e = self.data['species'][0]
        a, b = observation(), observation(takasa='1.6m')
        b['url'] = a['url']
        e['observations'] = [a, b]
        sh.resolve_status(e)
        self.assertEqual((e['status'], e['height']['cm'], len(e['observations'])), ('conflict', None, 2))
        self.assertEqual(self.errs(), [])

    def test_form_name_needs_review(self):
        e = self.data['species'][0]
        e['observations'] = [observation(sub='1', extra={'sub_name': 'べつのすがた'})]
        sh.resolve_status(e)
        self.assertEqual(e['status'], 'needs_review')
        self.assertIsNone(e['height']['cm'])

    def test_name_not_in_card_names_needs_review(self):
        e = self.data['species'][0]
        e['observations'] = [observation()]
        sh.resolve_status(e, {1: {'フシギダネ', 'エリカのフシギダネ'}})
        self.assertEqual((e['status'], e['status_reason']), ('needs_review', 'name_not_in_kyuura_card_names'))

    def test_tampering_detected(self):
        e = self.data['species'][0]
        e['observations'] = [observation()]
        sh.resolve_status(e)
        for mutate, word in [(lambda o: o.update(cm=151), '換算'),
                             (lambda o: o.update(source='POKEAPI'), '公式の出典でない'),
                             (lambda o: o['extract'].update(takasa='1.6m'), 'sha256'),
                             (lambda o: o.update(url='https://example.org/'), 'URL')]:
            d = copy.deepcopy(self.data)
            mutate(d['species'][0]['observations'][0])
            self.assertTrue(any(word in x for x in self.errs(d)), word)
        d = copy.deepcopy(self.data)
        d['species'][0]['height']['cm'] = 999
        self.assertTrue(any('観測から決めた値と違う' in x for x in self.errs(d)))

    def test_cache_mismatch_detected(self):
        e = self.data['species'][0]
        e['observations'] = [observation()]
        sh.resolve_status(e)
        with tempfile.TemporaryDirectory() as t:
            f = sh.cache_path(Path(t), 'SRC-ZUKAN-JP', 1)
            f.parent.mkdir(parents=True)
            f.write_bytes(synthetic_page())
            self.assertEqual(sh.check_data(self.data, cache=Path(t)), [])
            notes = []
            f.write_bytes(synthetic_page() + b'<!-- changed on refetch -->')
            self.assertEqual(sh.check_data(self.data, cache=Path(t), notes=notes), [])
            self.assertEqual(len(notes), 1)
            f.write_bytes(synthetic_page(takasa='1.6m'))
            self.assertTrue(any('抜き出し直した値' in x for x in sh.check_data(self.data, cache=Path(t))))

    def test_extract_records_parse_failure_without_value(self):
        with tempfile.TemporaryDirectory() as t:
            f = sh.cache_path(Path(t), 'SRC-ZUKAN-JP', 2)
            f.parent.mkdir(parents=True)
            f.write_bytes(b'<html>no data</html>')
            res = sh.extract(self.data, 'SRC-ZUKAN-JP', [1, 2], Path(t), '2026-10-31', None)
        self.assertEqual(res['missing_cache'], [1])
        self.assertEqual([x['dex'] for x in res['parse_failed']], [2])
        e = self.data['species'][1]
        self.assertEqual((e['status'], e['status_reason'], e['height']['cm']), ('unverified', 'parse_failed', None))
        self.assertEqual(self.errs(), [])


if __name__ == '__main__':
    unittest.main()
