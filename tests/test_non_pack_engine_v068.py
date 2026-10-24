"""拡張パック以外の商品の収録（形式 3）・エンジンの実装の対象の一覧・kyuura-engine v0.26〜v0.68 の取り込み・カードデータの訂正の検査（2026-10-19）。

原典の再読はしていない。エンジンの記録は固定した参照（kyuura-engine 24bfbe2）から取り込んだ。根拠の誌面は、取り込んだ記録の
sources・verification に書いた（『オフィシャルブック2000』[P43] の公式ルール pp.306〜325 ほか）。
"""
import copy
import csv
import io
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402
import build_cardlist  # noqa: E402
import non_pack  # noqa: E402

BASE = '4b73536e5507581c3d2cf44f7d519021850f9e81'  # この作業の基準（main）
ENGINE = '24bfbe2c1bf3b5fb0521e229ac92cf2fa4a154a1'  # kyuura-engine v0.68（固定した参照）
KANGASKHAN_BEFORE = 'コインを投げて「おもて」なら、自分の山札の上からカードを1枚ひいて、手札に加える。'
KANGASKHAN_AFTER = '自分の山札の上からカードを1枚ひいて、手札に加える。'


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def base_json(rel):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{rel}'], capture_output=True, text=True, check=True).stdout)


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.items = load('data/product_items.json')
        cls.np = load('data/curation/non_pack.json')
        cls.pcg = load('data/ja_text_pcgsearch.json')
        cls.page_checks = load('data/pcgsearch_page_checks.json')
        cls.groups = load('data/same_card_groups.json')
        cls.non_pack = [c for c in cls.cards if c['product_group'] != 'expansion_pack']


class NonPackCatalogTest(Data):
    """拡張パック以外の商品の記録（data/cards.json の形式 3）。"""

    def test_counts(self):
        self.assertEqual(Counter(c['product_group'] == 'expansion_pack' for c in self.cards), {True: 780, False: 597})
        self.assertEqual(len(self.items['non_game_items']), 18)
        self.assertEqual(sum(len(v) for v in self.pcg['products'].values()), 681)
        self.assertEqual(Counter(x['disposition'] for x in self.items['items']), {'card': 597, 'copy': 66, 'non_game': 18})

    def test_ids_follow_the_product_code_and_page_rule(self):
        # カード id = 商品の記号 + カードページ名の末尾 3 桁（サイトの並び順は使わない）
        codes = {v['code']: v['page_prefix'] for v in self.np['products'].values()}
        self.assertEqual(len(codes), len(self.np['products']))
        ids = [c['id'] for c in self.cards]
        self.assertEqual(len(ids), len(set(ids)))
        for c in self.non_pack:
            code, num = c['id'].rsplit('-', 1)
            self.assertIn(code, codes, c['id'])
            self.assertEqual(c['jp_set'], code)
            page = c['source_ids']['pcg_search'][0]
            self.assertTrue(page.startswith(codes[code]) and page.endswith(num), (c['id'], page))

    def test_existing_ids_and_references_are_kept(self):
        base = base_json('data/cards.json')
        self.assertEqual({c['id'] for c in base['cards']}, {c['id'] for c in self.cards if c['product_group'] == 'expansion_pack'})
        ctx = bcr.load()
        self.assertEqual(bcr.validate(ctx), [])
        refs = set()
        for rec in ctx['latest']['records'] + ctx['checks']['records']:
            refs.add(rec['card_id'])
        for x in ctx['rulings']['rulings']:
            refs |= {c['card_id'] for c in x['cards']}
        for x in ctx['rulings']['issues']:
            refs |= {c['card_id'] for c in x['cases']}
        self.assertFalse(refs - set(self.by_id))

    def test_every_source_item_is_traceable(self):
        items = {x['page']: x for x in self.items['items']}
        self.assertEqual(len(items), len(self.items['items']))
        for product, entries in self.pcg['products'].items():
            for e in entries:
                page = non_pack.page_id(e['url'])
                self.assertIn(page, items, page)
                x = items[page]
                if x['disposition'] == 'card':
                    self.assertIn(page, self.by_id[x['id']]['source_ids']['pcg_search'], page)
                elif x['disposition'] == 'copy':
                    rec = self.by_id[x['id']]
                    self.assertIn(page, [cp['page'] for cp in rec['copies']], page)
                else:
                    ng = next(n for n in self.items['non_game_items'] if n['page'] == page)
                    self.assertTrue(ng['reason'])
                    self.assertNotIn(ng['id'], self.by_id)

    def test_each_page_belongs_to_one_record(self):
        owner = Counter(p for c in self.non_pack for p in c['source_ids']['pcg_search'])
        self.assertEqual([p for p, n in owner.items() if n > 1], [])
        for c in self.cards:
            if c['product_group'] == 'expansion_pack':
                self.assertEqual(c['source_ids']['pcg_search'], [], c['id'])

    def test_merged_copies_are_identical_except_their_number(self):
        transcript = {non_pack.page_id(e['url']): e for v in self.pcg['products'].values() for e in v}
        for c in self.non_pack:
            pages = [cp['page'] for cp in c.get('copies', [])]
            if len(pages) < 2:
                continue
            first = {k: v for k, v in transcript[pages[0]].items() if k not in ('list_number', 'url')}
            for p in pages[1:]:
                self.assertEqual({k: v for k, v in transcript[p].items() if k not in ('list_number', 'url')}, first, (c['id'], p))

    def test_same_card_groups_do_not_merge_by_name_alone(self):
        for g in self.groups['groups']:
            members = [self.by_id[m['id']] for m in g['members']]
            self.assertEqual(len({non_pack.signature(m) for m in members}), 1, g['id'])
            for m in g['members'][1:]:
                if m['numbers_differ'] or m['text'] == 'different':
                    self.assertFalse(m['equivalent_to_first'], (g['id'], m['id']))
        # 名前が同じでも HP・ワザの違うカードは別の組（例: 第1弾のフシギダネと拡張シートのフシギダネ）
        self.assertNotEqual(self.by_id['PMCG1-001']['same_card_group'], self.by_id['QSG-001']['same_card_group'])

    def test_json_and_csv_agree(self):
        rows = list(csv.DictReader(io.StringIO((ROOT / 'data' / 'cards.csv').read_text(encoding='utf-8'))))
        self.assertEqual([r['id'] for r in rows], [c['id'] for c in self.cards])
        for r in rows:
            c = self.by_id[r['id']]
            self.assertEqual(r['name_ja'], c['name']['ja'] or '')
            self.assertEqual(r['product_group'], c['product_group'])
            self.assertEqual(r['play_scope'], c['play_scope'])
            self.assertEqual(r['same_card_group'], c['same_card_group'] or '')
            self.assertEqual(r['hp'], '' if not c['pokemon'] or c['pokemon']['hp'] is None else str(c['pokemon']['hp']))
        attacks = list(csv.DictReader(io.StringIO((ROOT / 'data' / 'attacks.csv').read_text(encoding='utf-8'))))
        powers = list(csv.DictReader(io.StringIO((ROOT / 'data' / 'powers.csv').read_text(encoding='utf-8'))))
        self.assertEqual(len(attacks), sum(len(c['pokemon']['attacks']) for c in self.cards if c['pokemon']))
        self.assertEqual(len(powers), sum(len(c['pokemon']['powers']) for c in self.cards if c['pokemon']))
        for a in attacks:
            c = self.by_id[a['card_id']]
            self.assertEqual(a['text_ja'], c['pokemon']['attacks'][int(a['index']) - 1]['text']['ja'] or '', a['card_id'])  # index は 1 から

    def test_evolves_from_has_a_source_or_a_gap(self):
        # 名前の接頭辞・英語版の進化元から推測しない（英語版は照らし合わせだけ）
        for c in self.non_pack:
            p = c['pokemon']
            if not p or p['stage'] not in ('stage1', 'stage2'):
                continue
            src = c['field_sources'].get('pokemon.evolves_from')
            if p['evolves_from']:
                self.assertTrue(src == 'pcg_search_evolution_line' or src.startswith('same_card:PMCG') or src.startswith('same_card:neo'), (c['id'], src))
            else:
                self.assertIn('pokemon.evolves_from', c['data_gaps'], c['id'])
        # サイトの種類の欄と進化ラインの段階が違うカードは、段階を値の欠けにして進化元を入れない
        for cid in ('GD3-003', 'PRN-030'):
            self.assertIn('pokemon.stage', self.by_id[cid]['data_gaps'])
            self.assertIsNone(self.by_id[cid]['pokemon']['evolves_from'])
        # 進化ラインの名前が「わるい」のない名前のページからは入れない
        self.assertIsNone(self.by_id['PRN-040']['pokemon']['evolves_from'])

    def test_null_retreat_reading(self):
        checks = self.page_checks['pages']
        for c in self.non_pack:
            src = c['field_sources'].get('pokemon.retreat_cost')
            if src == 'pcg_search_page_dash':
                self.assertEqual(c['pokemon']['retreat_cost'], 0, c['id'])
                self.assertEqual(checks[c['source_ids']['pcg_search'][0]]['retreat_raw'], '-', c['id'])
        # 読み直したページは、転記と同じ方法で読んで転記と同じ
        self.assertEqual([p for p, v in checks.items() if v['transcript_differences']], [])

    def test_special_cards_are_not_ordinary_play(self):
        scopes = {c['id']: c['play_scope'] for c in self.non_pack if c['play_scope'] != 'standard'}
        self.assertEqual(scopes, {'PR1-038': 'kangaskhan_rule', 'PRN-048': 'kangaskhan_rule',
                                  'PR1-027': 'not_for_official_tournaments', 'PR1-073': 'not_for_official_tournaments'})
        kinds = Counter(n['kind'] for n in self.items['non_game_items'])
        self.assertEqual(kinds, {'extra_rule': 5, 'deck_recipe': 5, 'other': 4, 'pass_card': 2, 'joke_card': 1, 'award': 1})

    def test_uncovered_products_are_listed(self):
        unc = self.np['uncovered_products']
        self.assertTrue(any('GB' in u['target'] for u in unc))
        self.assertTrue(any('調べていない' in u['basis'] or '調べていない' in u['status'] for u in unc))

    def test_bad_input_is_rejected(self):
        with self.assertRaises(SystemExit):
            non_pack.ja_damage('10ぐらい')
        self.assertEqual(non_pack.ja_damage('20×'), {'base': 20, 'modifier': '×', 'display': '20×'})


class CorrectionTest(Data):
    """カードデータの訂正（data/curation/card_corrections.json）。"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ledger = load('data/curation/card_corrections.json')

    def test_kangaskhan_is_corrected_from_the_ledger(self):
        # 利用者が示した訂正（実物のカードの画像。kyuura は画像を見ていない）。エラッタ・再録の変更ではない
        self.assertEqual(self.by_id['PMCG2-046']['pokemon']['attacks'][0]['text']['ja'], KANGASKHAN_AFTER)
        self.assertEqual(base_json('data/cards.json')['cards'][[c['id'] for c in base_json('data/cards.json')['cards']].index('PMCG2-046')]
                         ['pokemon']['attacks'][0]['text']['ja'], KANGASKHAN_BEFORE)
        fix = next(c for c in self.ledger['corrections'] if c['id'] == 'FIX-PMCG2-046-ATK0-TEXT')
        self.assertEqual((fix['before'], fix['after'], fix['basis'], fix['kyuura_saw_image']), (KANGASKHAN_BEFORE, KANGASKHAN_AFTER, 'user_provided', False))
        self.assertNotIn('record', fix)
        self.assertNotIn('commit', fix)
        ctx = bcr.load()
        self.assertFalse([x for x in ctx['checks']['records'] + ctx['latest']['records'] if x['card_id'] == 'PMCG2-046'])

    def test_regeneration_reapplies_the_correction_and_rejects_unexpected_values(self):
        record = copy.deepcopy(self.by_id['PMCG2-046'])
        record['pokemon']['attacks'][0]['text']['ja'] = KANGASKHAN_BEFORE  # 転記の元の値（なぞのばしょ）
        record.pop('corrections', None)
        ledger = {'corrections': [c for c in self.ledger['corrections'] if c['id'] == 'FIX-PMCG2-046-ATK0-TEXT'], 'candidates': []}
        build_cardlist.apply_corrections([record], ledger)
        self.assertEqual(record['pokemon']['attacks'][0]['text']['ja'], KANGASKHAN_AFTER)
        self.assertEqual([c['id'] for c in record['corrections']], ['FIX-PMCG2-046-ATK0-TEXT'])
        other = copy.deepcopy(record)
        other['pokemon']['attacks'][0]['text']['ja'] = '別の値'
        other.pop('corrections')
        with self.assertRaises(SystemExit):
            build_cardlist.apply_corrections([other], ledger)
        with self.assertRaises(SystemExit):
            build_cardlist.apply_corrections([copy.deepcopy(record)], {'corrections': ledger['corrections'] * 2, 'candidates': []})

    def test_every_candidate_has_a_status_and_reason(self):
        statuses = Counter(c['status'] for c in self.ledger['candidates'])
        self.assertLessEqual(set(statuses), {'held_print_version', 'held_transcription_difference', 'held_likely_transcription_error',
                                             'version_difference', 'gap_open'})
        for c in self.ledger['candidates']:
            self.assertTrue(c['reason'], c['card_id'])
            self.assertIn(c['card_id'], self.by_id)
        # ベロリンガ（PMCG2-041）は前の作業で直した訂正のまま（新しい訂正にしない・古い値にもどさない）
        b = [c for c in self.ledger['corrections'] if c['card_id'] == 'PMCG2-041']
        self.assertEqual({c['applied_by'] for c in b}, {'ja_text.json'})
        self.assertEqual(self.by_id['PMCG2-041']['pokemon']['attacks'][0]['name']['ja'], 'まきつくベロ')
        self.assertEqual(self.by_id['PMCG2-041']['jp_print']['level'], 26)

    def test_card_check_values_are_checked_through_the_correction_history(self):
        ctx = bcr.load()
        cc = next(x for x in ctx['checks']['records'] if x['id'] == 'CC-PMCG1-002-P17')
        cc['checked_fields']['pokemon.attacks[0].text.ja'] = '照合したときの値'
        self.assertTrue(any('照合した欄 pokemon.attacks[0].text.ja の写しが今の data/cards.json と違う' in e for e in bcr.validate(ctx)))
        fix = {'id': 'FIX-TEST', 'card_id': 'PMCG1-002', 'field': 'pokemon.attacks[0].text.ja', 'before': '照合したときの値',
               'after': self.by_id['PMCG1-002']['pokemon']['attacks'][0]['text']['ja'], 'card_checks_affected': []}
        ctx['corrections'] = ctx['corrections'] + [fix]
        self.assertTrue(any('card_checks_affected に、この照合の記録がない' in e for e in bcr.validate(ctx)))
        fix['card_checks_affected'] = ['CC-PMCG1-002-P17']
        self.assertEqual(bcr.validate(ctx), [])


class EngineTargetsTest(Data):
    """エンジンの実装の対象の一覧（data/engine_targets.json）。"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.targets = load('data/engine_targets.json')
        cls.snapshot = load('data/curation/engine_registered_cards.json')

    def test_generated_files_are_current(self):
        out = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_engine_targets.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        out = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_other_products.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_snapshot_is_the_fixed_engine_version(self):
        self.assertEqual(self.snapshot['engine']['commit'], ENGINE)
        self.assertEqual(self.snapshot['counts'], {'attacks': 597, 'trainers': 94, 'powers': 58, 'energies': 4,
                                                   'playable_cards': 457, 'cards_with_registrations': 451})

    def test_only_registered_ids_count_as_registered(self):
        rows = {r['id']: r for r in self.targets['cards']}
        registered = {i for i, r in rows.items() if r['engine_status'] == 'registered'}
        self.assertEqual(registered, set(self.snapshot['playable']))
        self.assertTrue(all(self.by_id[i]['product_group'] == 'expansion_pack' for i in registered))
        for r in rows.values():
            if r['engine_status'] == 'mechanically_equivalent':
                self.assertTrue(set(r['equivalent_to']) <= registered, r['id'])
                self.assertNotIn(r['id'], registered)
        self.assertEqual(sum(self.targets['counts']['by_engine_status'].values()), len(self.cards))
        self.assertEqual(len(self.targets['non_game_items']), 18)
        # 拡張シートの同じ名前の別のカード（HP・ワザが違う）は、登録されたカードの再利用の候補にしない
        self.assertNotIn('nearest_registered', rows['QSG-001'])


class EngineImportV068Test(unittest.TestCase):
    """kyuura-engine v0.26〜v0.68 の取り込み（data/sidecar/rulings.json）。"""

    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()
        cls.r = cls.ctx['rulings']
        cls.imports = {imp['engine_version']: imp for imp in cls.r['engine_imports']}
        cls.issues = {x['id']: x for x in cls.r['issues']}

    def copy(self):
        return copy.deepcopy(self.ctx)

    def assert_detected(self, ctx, text):
        errors = bcr.validate(ctx)
        self.assertTrue(any(text in e for e in errors), (text, errors[:5]))

    def test_one_import_per_version_with_fixed_documents(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        for n in range(26, 69):
            imp = self.imports[f'v0.{n}']
            self.assertRegex(imp['commit'], r'^[0-9a-f]{40}$')
            self.assertEqual(imp['documents_read_at'], ENGINE)
            self.assertEqual(imp['imported_on'], '2026-10-19')
        self.assertEqual(self.imports['v0.68']['engine_unresolved_total'], 151)

    def test_counts_are_kept_apart(self):
        # 研究の論点の数と、エンジンの停止コード・未解決の裁定の数を同じにそろえない
        # v0.68 の取り込みの時点は 71。2026-10-24 のアンノーンの調査で kyuura の論点 UQ-SELF-EXCLUDING-POWER-COPIES（エンジンの裁定に結ばない）を加えて、今は 72
        at_import = bcr.unresolved_counts(self.ctx, as_of='v0.68')
        self.assertEqual((at_import['research_issues'], at_import['engine_total'], at_import['engine_stop_codes']), (71, 151, 149))
        now = bcr.unresolved_counts(self.ctx)
        self.assertEqual((now['research_issues'], now['engine_total'], now['engine_stop_codes']), (72, 151, 149))
        old = bcr.unresolved_counts(self.ctx, as_of='v0.25')
        self.assertEqual((old['research_issues'], old['engine_total'], old['engine_stop_codes']), (24, 28, 22))

    def test_rows_not_imported_are_classified(self):
        n = Counter()
        ids = mapped = 0
        uses = bcr.engine_uses(self.ctx)
        for v, imp in self.imports.items():
            if bcr.version_key(v) < (0, 26):
                continue
            for rs in imp['ruling_sets']:
                for rid in bcr.ruling_set_ids(rs):
                    ids += 1
                    mapped += (imp['id'], rs['document'], rid) in uses
            for x in imp['not_imported']:
                self.assertIn(x['classification'], bcr.NOT_IMPORTED_CLASSIFICATIONS)
                self.assertTrue(x['reason'])
                n[x['classification']] += 1
        # 表の行・停止コードの id（版・文書・id で 1 つ）は、どれも論点に結ぶか取り込まない理由がある（2026-10-19 の取り込みの数）
        self.assertEqual((ids, mapped, sum(n.values())), (ids, ids - sum(n.values()), 262))
        self.assertEqual(n, {'card_text_application': 143, 'official_confirmed': 56, 'supported_interpretation': 37,
                             'unresolved_rules_question': 10, 'engine_assumption': 9, 'engine_implementation': 4, 'engine_adopted_spec': 3})
        # テストの成功は公式の裁定の根拠にしない（CONFIRMED の当てはめも新しい裁定にしない）
        self.assertFalse([e for x in self.r['rulings'] for e in x.get('engine_refs', []) if bcr.version_key(e['engine_version']) >= (0, 26)])

    def test_missing_and_double_mappings_are_detected(self):
        ctx = self.copy()
        imp = next(i for i in ctx['rulings']['engine_imports'] if i['engine_version'] == 'v0.27')
        imp['not_imported'] = [x for x in imp['not_imported'] if x['ruling_id'] != 'SC5']
        self.assert_detected(ctx, 'エンジンの裁定 SC5 が、どの記録にも not_imported にもない')
        ctx = self.copy()
        imp = next(i for i in ctx['rulings']['engine_imports'] if i['engine_version'] == 'v0.31')
        imp['not_imported'].append({'ruling_id': 'HC5', 'document': 'docs/held-cards-v0.31.md', 'engine_classification': '—',
                                    'status': 'card_application', 'classification': 'card_text_application', 'reason': 'テスト'})
        self.assert_detected(ctx, 'エンジンの裁定 HC5（docs/held-cards-v0.31.md）が not_imported にも記録')
        ctx = self.copy()
        uq = next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-STATED-COUNT-SHORT')
        uq['engine_refs'].append(next(e for e in ctx['rulings']['issues'] if e['id'] == 'UQ-UP-TO-ZERO-CHOICE')['engine_refs'][0])
        self.assert_detected(ctx, '2 つ以上の未解決の論点')

    def test_wrong_classification_is_detected(self):
        ctx = self.copy()
        imp = next(i for i in ctx['rulings']['engine_imports'] if i['engine_version'] == 'v0.27')
        imp['not_imported'][0]['classification'] = 'engine_assumption'  # 実装の仮定を card_application にしない
        self.assert_detected(ctx, 'と classification engine_assumption が合わない')
        ctx = self.copy()
        imp = next(i for i in ctx['rulings']['engine_imports'] if i['engine_version'] == 'v0.27')
        del imp['not_imported'][0]['classification']
        self.assert_detected(ctx, 'classification の値が不正')
        ctx = self.copy()
        imp = next(i for i in ctx['rulings']['engine_imports'] if i['engine_version'] == 'v0.68')
        x = next(x for x in imp['not_imported'] if x['status'] == 'existing_record')
        x['kyuura_records'] = []
        self.assert_detected(ctx, 'existing_record）なのに kyuura_records がない')

    def test_kogas_muk_adopted_spec_is_not_a_ruling(self):
        # 2000.02.14 版の基準で DR1・DR6 は未解決のまま。エンジンの採用した仕様は engine_positions に分けて書く
        for uq in ('UQ-ENERGY-DRAIN-DECLARATION', 'UQ-ENERGY-DRAIN-TIMING'):
            self.assertEqual(self.issues[uq]['status'], 'UNRESOLVED')
        pos = {x['id']: x for x in self.r['engine_positions']}
        spec = pos['ENG-V068-ENERGY-DRAIN-ADOPTED-SPEC']
        self.assertEqual(spec['kind'], 'adopted_spec')
        self.assertEqual(spec['engine_rulings'], ['DR1', 'DR6', 'DR12'])
        self.assertIn('MIX-POWER-ERRATA', ' '.join(spec['engine_basis']))
        self.assertIn('読み替えない', spec['kyuura_handling'])
        ni = {x['ruling_id']: x for x in self.imports['v0.68']['not_imported']}
        for rid in ('DR1', 'DR6', 'DR12'):
            self.assertEqual((ni[rid]['status'], ni[rid]['engine_position']), ('adopted_spec', spec['id']))
        uses = bcr.engine_uses(self.ctx)
        self.assertEqual([i for _, i, _ in uses[(self.imports['v0.68']['id'], 'docs/final-pmcg-cards-v0.68.md', 'DR8')]], ['UQ-ENERGY-DRAIN-ATTACKER-KO'])
        self.assertEqual([i for _, i, _ in uses[(self.imports['v0.68']['id'], 'docs/final-pmcg-cards-v0.68.md', 'DR13')]], ['UQ-ENERGY-DRAIN-NO-ENERGY'])
        ctx = self.copy()
        p = next(x for x in ctx['rulings']['engine_positions'] if x['id'] == spec['id'])
        p['status'] = 'CONFIRMED'
        self.assert_detected(ctx, '裁定の status・conclusion を書かない')
        ctx = self.copy()
        imp = next(i for i in ctx['rulings']['engine_imports'] if i['engine_version'] == 'v0.68')
        next(x for x in imp['not_imported'] if x['ruling_id'] == 'DR6')['status'] = 'card_application'
        self.assert_detected(ctx, 'エンジンの裁定 DR6 が、取り込み')

    def test_doduo_simplification_keeps_the_printed_text(self):
        pos = {x['id']: x for x in self.r['engine_positions']}
        d = pos['ENG-V068-IMAKUNI-DODUO-SIMPLIFIED']
        self.assertEqual(d['kind'], 'simplification')
        self.assertIn('エラッタ・最新の説明・裁定ではない', d['kyuura_handling'])
        base = {c['id']: c for c in base_json('data/cards.json')['cards']}
        now = {c['id']: c for c in load('data/cards.json')['cards']}
        self.assertEqual(base['PMCG6-074']['pokemon'], now['PMCG6-074']['pokemon'])
        self.assertFalse([x for x in self.ctx['latest']['records'] if x['card_id'] == 'PMCG6-074'])

    def test_secret_maneuver_implementation_matter_is_separate(self):
        pos = {x['id']: x for x in self.r['engine_positions']}
        m = pos['ENG-V068-SECRET-MANEUVER-IDENTITY']
        self.assertEqual(m['kind'], 'implementation_matter')
        q = self.issues['UQ-FACE-DOWN-CARD']
        self.assertEqual({c['engine_ruling'] for c in q['cases']}, {'FD1', 'FD2'})
        self.assertNotIn('デッキの中身', q['question'] + q['why_unresolved'])

    def test_adoption_records_are_not_imported_as_source_checks(self):
        # card_sources.json（kyuura データの採用・pcg-search.com との比較）は照合の記録（CC-）にしない
        for x in self.ctx['checks']['records'] + self.ctx['latest']['records']:
            for v in x.get('verification', []):
                self.assertNotIn('card_sources.json', v.get('document', ''), x['id'])
        new = [x for x in self.ctx['checks']['records'] if x.get('import_provenance', {}).get('imported_on') == '2026-10-19']
        self.assertEqual(len(new), 11)
        for x in new:
            self.assertEqual(x['verification'][0]['source_checked_on'], '2026-10-15')
            self.assertIs(x['import_provenance']['kyuura_reread_source'], False)

    def test_existing_questions_are_reused(self):
        uses = bcr.engine_uses(self.ctx)
        by_id = {imp['engine_version']: imp['id'] for imp in self.r['engine_imports']}
        self.assertEqual([i for _, i, _ in uses[(by_id['v0.31'], 'docs/held-cards-v0.31.md', 'HC3')]], ['UQ-COIN-IN-NULLIFIED-ELEMENT'])
        self.assertEqual([i for _, i, _ in uses[(by_id['v0.60'], 'docs/coins-defense-rebellion-v0.60.md', 'TS1')]], ['UQ-TRANSPARENCY-COIN-ORDER'])
        self.assertEqual([i for _, i, _ in uses[(by_id['v0.48'], 'docs/effective-pokemon-properties-v0.48.md', 'MH1')]], ['UQ-EVOLUTION-HP-BELOW-DAMAGE'])
        new = [x for x in self.r['issues'] if x.get('source_provenance', {}).get('imported_on') == '2026-10-19']
        self.assertEqual(len(new), 47)
        for x in new:
            self.assertIs(x['source_provenance']['kyuura_reread_source'], False)
            self.assertTrue(x['engine_refs'])
            self.assertTrue(x['cases'])
            self.assertFalse(re.search(r'UNRESOLVED_', x['question'] + x['why_unresolved']), x['id'])


if __name__ == '__main__':
    unittest.main()
