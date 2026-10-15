"""kyuura-engine の照合の記録の取り込み（2026-10-15）の検査と破壊テスト。

- エンジンの照合の記録（kyuura_engine/data/card_verification.json。v0.17 の d90bce1・v0.18 の 46a3e2e）を、kyuura の照合の記録（CC-）
  34 件と最新の説明の記録（LD-）5 件として取り込んだ。kyuura は原典（『ポケモンカードオフィシャルブック2000』[P43]、スキャン [J38]）の
  画像を読み直していない。取り込んだ記録は import_provenance を持ち、原典の確認日（エンジンの記録の日付）と取り込んだ日を分ける。
- 照合した欄は、エンジンの記録が照合したと書いた項目だけ。照合していない欄は fields_not_checked に理由とともに書く。
- 再利用の手順は docs/engine-readiness.md の 10 章。

使い方: python3 -m unittest discover -s tests（リポジトリの直下。標準ライブラリだけ）
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402

IMPORTED_ON = '2026-10-15'
NEW_LD = ['LD-PMCG1-003-ATK0', 'LD-PMCG1-009-ATK0', 'LD-PMCG1-012-ATK0', 'LD-PMCG2-007-ATK0', 'LD-PMCG2-007-ATK1']
NEW_CC_CARDS = ['PMCG1-002', 'PMCG1-003', 'PMCG1-004', 'PMCG1-009', 'PMCG1-012', 'PMCG1-014', 'PMCG1-015', 'PMCG1-016', 'PMCG1-018',
                'PMCG1-025', 'PMCG1-029', 'PMCG1-030', 'PMCG1-035', 'PMCG1-037', 'PMCG1-052', 'PMCG1-058', 'PMCG1-060', 'PMCG1-061',
                'PMCG1-065', 'PMCG1-071', 'PMCG1-073', 'PMCG1-074', 'PMCG1-079', 'PMCG1-081', 'PMCG1-097', 'PMCG1-098', 'PMCG1-099',
                'PMCG1-100', 'PMCG1-101', 'PMCG1-102', 'PMCG2-003', 'PMCG2-007', 'PMCG2-010', 'PMCG6-044']


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()

    def copy(self):
        return copy.deepcopy(self.ctx)

    def find(self, ctx, kind, rid):
        return next(x for x in ctx[kind]['records'] if x['id'] == rid)

    def imported(self, ctx=None):
        ctx = ctx or self.ctx
        return ([x for x in ctx['latest']['records'] if x.get('import_provenance')],
                [x for x in ctx['checks']['records'] if x.get('import_provenance')])

    def assert_detected(self, ctx, fragment):
        errors = bcr.validate(ctx)
        self.assertTrue(any(fragment in e for e in errors), f'「{fragment}」のエラーがない: {errors[:5]}')


class ImportedRecordsTest(Base):
    def test_current_data_has_no_errors(self):
        self.assertEqual(bcr.validate(self.ctx), [])

    def test_imported_set(self):
        """取り込んだのは CC- 34 件（34 枚）と LD- 5 件で、kyuura が画像を読んだ既存の記録（by: kyuura）とは重ならない。"""
        ld, cc = self.imported()
        self.assertEqual(sorted(x['id'] for x in ld), sorted(NEW_LD))
        self.assertEqual(sorted(x['card_id'] for x in cc), sorted(NEW_CC_CARDS))
        for x in ld + cc:
            self.assertFalse(any(v['by'] == 'kyuura' for v in x['verification']), x['id'])
            self.assertEqual(x['import_provenance']['imported_on'], IMPORTED_ON)
            self.assertIs(x['import_provenance']['kyuura_reread_source'], False)

    def test_source_check_date_is_not_the_import_date(self):
        """原典の確認日はエンジンの記録の日付（2026-10-12・ナツメのヤドンは 2026-10-14）で、取り込んだ日（2026-10-15）とは別。"""
        ld, cc = self.imported()
        dates = {v['source_checked_on'] for x in ld + cc for v in x['verification']}
        self.assertEqual(dates, {'2026-10-12', '2026-10-14'})
        for x in ld + cc:
            for v in x['verification']:
                self.assertLess(v['source_checked_on'], x['import_provenance']['imported_on'])
                self.assertTrue(v['method'] and v['scope'] and v['record'].startswith('cards.'), x['id'])

    def test_kyuura_read_records_are_unchanged_in_kind(self):
        """kyuura が画像を読んだ記録（2026-10-14 まで）は import_provenance を持たない。"""
        for kind in ('latest', 'checks'):
            for x in self.ctx[kind]['records']:
                if any(v['by'] == 'kyuura' for v in x['verification']):
                    self.assertNotIn('import_provenance', x, x['id'])

    def test_scope_is_limited_to_the_engine_record(self):
        """照合した欄はエンジンの記録の範囲だけ: v0.1 のたねポケモンは名前・段階を照合していない、トレーナーは文面（マサキを除く）、
        基本エネルギーは種類だけ、ドードーのみだれづきとヒトカゲのひのこの文面は照合していない。"""
        checks = {x['card_id']: x for x in self.imported()[1]}
        for cid in ('PMCG1-016', 'PMCG1-018', 'PMCG1-025', 'PMCG1-029', 'PMCG1-037', 'PMCG1-052', 'PMCG1-058', 'PMCG1-060', 'PMCG1-065'):
            self.assertNotIn('name.ja', checks[cid]['checked_fields'], cid)
            self.assertNotIn('pokemon.stage', checks[cid]['checked_fields'], cid)
        for cid in ('PMCG1-071', 'PMCG1-073', 'PMCG1-079', 'PMCG1-081'):
            self.assertEqual(list(checks[cid]['checked_fields']), ['name.ja'], cid)
            self.assertTrue(any(f.startswith('trainer.text.ja') for f in checks[cid]['fields_not_checked']), cid)
        self.assertIn('trainer.text.ja', checks['PMCG1-074']['checked_fields'])
        for n in range(97, 103):
            self.assertEqual(sorted(checks[f'PMCG1-{n:03d}']['checked_fields']), ['energy.kind', 'energy.provides'])
        self.assertNotIn('pokemon.attacks[0].text.ja', checks['PMCG1-061']['checked_fields'])
        self.assertNotIn('pokemon.attacks[1].text.ja', checks['PMCG1-014']['checked_fields'])

    def test_doduo_text_is_left_open(self):
        """みだれづき: 図版の文面も kyuura の文面と違い、図版の版が決まらないので、最新の説明の記録にも、データの誤りにもしない。"""
        self.assertFalse([x for x in self.ctx['latest']['records'] if x['card_id'] == 'PMCG1-061'])
        cc = self.find(self.ctx, 'checks', 'CC-PMCG1-061-P231')
        self.assertEqual(cc['result'], 'no_difference')
        self.assertTrue(any('調査課題' in f for f in cc['findings']))

    def test_ponyta_attack_name_is_a_candidate(self):
        """ポニータのワザ名（けりとばす／けとばす）は修正の候補（data/cards.json は直していない）。"""
        cc = self.find(self.ctx, 'checks', 'CC-PMCG1-016-P75')
        self.assertEqual(cc['result'], 'data_error')
        self.assertEqual([(e['field'], e['kyuura_value'], e['source_value'], e['fix_status']) for e in cc['data_error']],
                         [('pokemon.attacks[0].name.ja', 'けりとばす', 'けとばす', 'candidate')])
        self.assertEqual(self.ctx['cards']['PMCG1-016']['pokemon']['attacks'][0]['name']['ja'], 'けりとばす')

    def test_latest_descriptions_are_linked_from_the_checks(self):
        for rid in NEW_LD:
            ld = self.find(self.ctx, 'latest', rid)
            cc = next(x for x in self.ctx['checks']['records'] if x['card_id'] == ld['card_id'] and x['page'] == ld['latest_description']['page'])
            self.assertIn(rid, cc['latest_description_refs'])
            self.assertEqual(cc['result'], 'printed_vs_latest_only')

    def test_pages_are_indexed(self):
        """取り込んだ記録のページは、P43 のページの記録（data/rule_history.json の documents）から引ける。"""
        doc = next(d for d in self.ctx['rule_history']['documents'] if d['code'] == 'P43')
        refs = {r for p in doc['pages'] for r in p['refs']}
        ld, cc = self.imported()
        for x in ld + cc:
            self.assertIn(x['id'], refs)

    def test_v018_import_has_no_rulings(self):
        imp = next(x for x in self.ctx['rulings']['engine_imports'] if x['engine_version'] == 'v0.18')
        self.assertEqual(imp['id'], 'ENGINE-46A3E2E')
        self.assertTrue(imp['no_ruling_tables'])
        self.assertEqual((imp['imported_rulings'], imp['unresolved_rulings']), ([], []))
        self.assertEqual(imp['engine_unresolved_total'], 24)
        self.assertIn('kyuura_engine/data/card_verification.json', imp['documents'])
        self.assertFalse([k for k in bcr.engine_uses(self.ctx) if k[0] == imp['id']])

    def test_generated_page_marks_imported_records(self):
        text = (ROOT / 'docs' / 'rules' / 'card-rulings.md').read_text(encoding='utf-8')
        self.assertIn('【kyuura-engine の照合の記録の取り込み。原典の確認 2026-10-12（エンジン）、取り込み 2026-10-15。kyuura は画像を読み直していない】', text)


class ProvenanceRulesTest(Base):
    """破壊テスト: 取り込んだ記録を、kyuura が画像で確かめた記録と取りちがえない。"""

    def test_record_without_any_source_reader_is_rejected(self):
        ctx = self.copy()
        del self.find(ctx, 'checks', 'CC-PMCG1-002-P17')['import_provenance']
        self.assert_detected(ctx, 'kyuura が原典を読んだ確認（verification の by: kyuura）がない')

    def test_import_cannot_claim_kyuura_reread(self):
        ctx = self.copy()
        self.find(ctx, 'checks', 'CC-PMCG1-002-P17')['import_provenance']['kyuura_reread_source'] = True
        self.assert_detected(ctx, 'kyuura が原典を読んだ確認を書かない')
        ctx = self.copy()
        self.find(ctx, 'latest', 'LD-PMCG1-003-ATK0')['verification'].append({'by': 'kyuura', 'date': IMPORTED_ON, 'method': '—', 'result': '—'})
        self.assert_detected(ctx, 'kyuura が原典を読んだ確認を書かない')

    def test_dates_are_required_and_ordered(self):
        ctx = self.copy()
        del self.find(ctx, 'checks', 'CC-PMCG1-002-P17')['verification'][0]['source_checked_on']
        self.assert_detected(ctx, 'source_checked_on がない')
        ctx = self.copy()
        self.find(ctx, 'checks', 'CC-PMCG1-002-P17')['verification'][0]['source_checked_on'] = '2026-10-16'
        self.assert_detected(ctx, 'より後')
        ctx = self.copy()
        del self.find(ctx, 'latest', 'LD-PMCG2-007-ATK1')['import_provenance']['imported_on']
        self.assert_detected(ctx, 'imported_on（取り込んだ日）がない')

    def test_engine_record_location_and_method_are_required(self):
        for key in ('record', 'method', 'source_checked_on_basis'):
            ctx = self.copy()
            del self.find(ctx, 'checks', 'CC-PMCG1-097-P318')['verification'][0][key]
            self.assert_detected(ctx, f'取り込んだエンジンの照合の記録に {key} がない')

    def test_unknown_provenance_kind_is_rejected(self):
        ctx = self.copy()
        self.find(ctx, 'checks', 'CC-PMCG1-002-P17')['import_provenance']['kind'] = 'tests_passed'
        self.assert_detected(ctx, 'import_provenance の kind の値が不正')


if __name__ == '__main__':
    unittest.main()
