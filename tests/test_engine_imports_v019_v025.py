"""トレーナーの最新の説明と、v0.19〜v0.25の記録取り込みの検査。原典の再読はしていない。"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import build_card_rulings as bcr


class TrainerImportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()

    def latest(self, ctx, cid='PMCG1-090'):
        return next(x for x in ctx['latest']['records'] if x['id'] == f'LD-{cid}-TRAINER')

    def assert_invalid(self, ctx, text):
        self.assertTrue(any(text in e for e in bcr.validate(ctx)), text)

    def test_six_cards_have_imported_latest_descriptions_and_checks(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        for cid, page in [('PMCG1-077','255'), ('PMCG1-072','255'), ('PMCG1-090','260'),
                          ('PMCG1-076','257'), ('PMCG1-093','259'), ('PMCG1-094','259')]:
            ld = self.latest(self.ctx, cid)
            cc = next(x for x in self.ctx['checks']['records'] if x['id'] == f'CC-{cid}-P{page}')
            self.assertIn(ld['id'], cc['latest_description_refs'])
            for x in [ld, cc]:
                self.assertIs(x['import_provenance']['kyuura_reread_source'], False)
                self.assertEqual(x['verification'][0]['by'], 'kyuura-engine')
                self.assertEqual(x['verification'][0]['source_checked_on'], '2026-10-15')

    def test_trainer_target_rejects_pokemon_and_wrong_name(self):
        for change in ['pokemon', 'name']:
            ctx = copy.deepcopy(self.ctx)
            x = self.latest(ctx)
            if change == 'pokemon':
                x['card_id'] = 'PMCG1-001'
            else:
                x['target']['name_ja'] = 'マサキ'
            self.assert_invalid(ctx, 'トレーナー')

    def test_trainer_path_and_printed_snapshot_are_checked(self):
        for field, value, error in [('path','pokemon.attacks[0].text.ja','path'), ('text_ja','変更した転記','写し')]:
            ctx = copy.deepcopy(self.ctx)
            self.latest(ctx)['printed_text'][field] = value
            self.assert_invalid(ctx, error)

    def test_trainer_target_does_not_accept_an_attack_index(self):
        ctx = copy.deepcopy(self.ctx)
        self.latest(ctx)['target']['index'] = 0
        self.assert_invalid(ctx, 'index')

    def test_trainer_id_cannot_be_used_for_an_attack(self):
        ctx = copy.deepcopy(self.ctx)
        self.latest(ctx)['target'] = {'kind':'attack', 'index':0, 'name_ja':'ワザ'}
        self.assert_invalid(ctx, 'idとトレーナー')

    def test_different_image_text_is_not_a_card_data_error(self):
        for cid in ['PMCG1-072','PMCG1-076']:
            x = self.latest(self.ctx, cid)
            self.assertEqual(x['printed_text']['image_check'], 'different_text')
            self.assertNotEqual(x['printed_text']['image_text_ja'], x['printed_text']['text_ja'])
            cc = next(c for c in self.ctx['checks']['records'] if c['card_id'] == cid)
            self.assertIs(cc['data_error'], False)
            self.assertNotIn('trainer.text.ja', cc['checked_fields'])

    def test_different_image_requires_actual_text_and_explanation(self):
        for key in ['image_text_ja', 'image_check_note']:
            ctx = copy.deepcopy(self.ctx)
            del self.latest(ctx, 'PMCG1-072')['printed_text'][key]
            self.assert_invalid(ctx, '図版の文面相違')

    def test_errata_link_is_required_for_energy_retrieval(self):
        ctx = copy.deepcopy(self.ctx)
        self.assertEqual(self.latest(ctx, 'PMCG1-076')['errata_ref'], 'ERR-ENERGY-RETRIEVAL')
        self.latest(ctx, 'PMCG1-076')['errata_ref'] = None
        self.assert_invalid(ctx, 'errata_ref')

    def test_every_ruling_in_six_tables_has_a_disposition(self):
        uses = bcr.engine_uses(self.ctx)
        sizes = {'v0.19':13, 'v0.21':18, 'v0.22':21, 'v0.23':17, 'v0.24':19, 'v0.25':22}
        for imp in self.ctx['rulings']['engine_imports']:
            if imp['engine_version'] not in sizes:
                continue
            rs = imp['ruling_sets'][0]
            skipped = {x['ruling_id'] for x in imp['not_imported']}
            mapped = {key[2] for key in uses if key[0] == imp['id']}
            expected = {f"{rs['prefix']}{i}" for i in range(1, sizes[imp['engine_version']]+1)}
            self.assertFalse(skipped & mapped)
            self.assertEqual(skipped | mapped, expected)

    def test_four_new_engine_questions_and_existing_hp_question_are_separate(self):
        # v0.25 の時点の数（あとの版の取り込みは as_of で除く。v0.26〜v0.68 の取り込みは tests/test_non_pack_engine_v068.py）
        uc = bcr.unresolved_counts(self.ctx, as_of='v0.25')
        self.assertEqual((uc['research_issues'], uc['engine_total'], uc['engine_stop_codes']), (24,28,22))
        idx = {x['engine_key']: x for x in self.ctx['rulings']['engine_unresolved_index']}
        self.assertEqual(len({idx[k]['kyuura_issue'] for k in ['GW5','CS6','ER9','ER10']}), 4)
        self.assertIn({'engine_version':'v0.25','ruling_id':'BR17'}, idx['EVOLUTION-HP']['instances'])
        self.assertNotIn('BR17', idx)

    def test_supported_and_mixed_rows_are_not_promoted(self):
        for version, rid in [('v0.22','CS14'), ('v0.23','ER13'), ('v0.25','BR6')]:
            found = bcr.find_engine_ruling(self.ctx, version, rid)
            record = next(x for x in self.ctx['rulings']['rulings'] if x['id'] == found[0][3])
            self.assertEqual(record['status'], 'SUPPORTED')
        imp = next(x for x in self.ctx['rulings']['engine_imports'] if x['engine_version']=='v0.25')
        self.assertEqual(next(x for x in imp['not_imported'] if x['ruling_id']=='BR5')['status'], 'deferred')

    def test_imported_rulings_cannot_claim_independent_image_checks(self):
        ctx = copy.deepcopy(self.ctx)
        x = next(x for x in ctx['rulings']['rulings'] if x.get('source_provenance'))
        x['basis'][0]['checked'] = 'kyuura_image'
        self.assert_invalid(ctx, '取り込みをkyuuraの画像確認にしない')

    def test_imported_ruling_provenance_requires_commit_and_no_reread(self):
        ctx = copy.deepcopy(self.ctx)
        x = next(x for x in ctx['rulings']['rulings'] if x.get('source_provenance'))
        x['source_provenance']['commit'] = 'not-a-commit'
        self.assert_invalid(ctx, '取り込みの出所が不正')


if __name__ == '__main__':
    unittest.main()
