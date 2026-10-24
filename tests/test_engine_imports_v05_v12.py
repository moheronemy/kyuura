"""kyuura-engine v0.5〜v0.12 の取り込み（版ごとの engine_imports）の網羅・分類・重複の検査と、破壊テスト。

原典は『ポケモンカードオフィシャルブック2000』[P43]（スキャン [J38]）。カードの最新の説明は pp.13・14・16・45・47・48・82・87・88・90・149・151・153・
158・159・160・189・190・191・192・193、一般の規定は pp.307・309〜312・319〜325（kyuura が画像で確かめた）。
エンジンの記録（docs/*-v0.5.md〜docs/*-v0.12.md）は調査の履歴で、原典ではない。

使い方: python3 -m unittest discover -s tests（リポジトリの直下。標準ライブラリだけ）
"""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402

# 版ごとの取り込み: 版 → (取り込みの id, コミット, {文書: 裁定の id の数})
IMPORTS = {
    'v0.5': ('ENGINE-0FBC3AB', '0fbc3ab', {'docs/venusaur-v0.5.md': 13, 'docs/bulbasaur-line-v0.5.md': 12, 'docs/pokemon-powers-v0.5.md': 18}),
    'v0.6': ('ENGINE-787FFF9', '787fff9', {'docs/rain-dance-v0.6.md': 20}),
    'v0.7': ('ENGINE-22CBE24', '22cbe24', {'docs/damage-swap-v0.7.md': 25, 'docs/alakazam-line-v0.7.md': 10}),
    'v0.8': ('ENGINE-D057F57', 'd057f57', {'docs/chemical-gas-v0.8.md': 33, 'docs/grimer-line-v0.8.md': 9}),
    'v0.9': ('ENGINE-995504E', '995504e', {'docs/transparency-v0.9.md': 43, 'docs/haunter-line-v0.9.md': 13}),
    'v0.10': ('ENGINE-43EC8BA', '43ec8ba', {'docs/counterattack-v0.10.md': 43, 'docs/machamp-line-v0.10.md': 12}),
    'v0.11': ('ENGINE-8BD1E5B', '8bd1e5b', {'docs/guts-v0.11.md': 42, 'docs/giovanni-machamp-line-v0.11.md': 14}),
    'v0.12': ('ENGINE-B8054AF', 'b8054af', {'docs/phoenix-v0.12.md': 35, 'docs/rocket-moltres-v0.12.md': 30}),
}
PROTECTED = ('data/cards.json', 'data/cards.csv', 'data/attacks.csv', 'data/powers.csv', 'data/ja_text_pcgsearch.json', 'data/rule_differences.json')


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()

    def copy(self):
        return copy.deepcopy(self.ctx)

    def rec(self, ctx, kind, id_):
        recs = {'latest': ctx['latest']['records'], 'checks': ctx['checks']['records'], 'rulings': ctx['rulings']['rulings'],
                'issues': ctx['rulings']['issues'], 'clauses': ctx['rulings']['rule_clauses'], 'imports': ctx['rulings']['engine_imports']}[kind]
        return next(x for x in recs if x['id'] == id_)

    def assert_detected(self, ctx, fragment):
        errors = bcr.validate(ctx)
        self.assertTrue(any(fragment in e for e in errors), f'「{fragment}」のエラーがない: {errors[:5]}')


class CoverageTest(Base):
    """取り込みの網羅（372 件）と、版ごとの取り込みの記録。"""

    def test_current_data_has_no_errors(self):
        self.assertEqual(bcr.validate(self.ctx), [])

    def test_one_import_per_version(self):
        imps = {x['engine_version']: x for x in self.ctx['rulings']['engine_imports']}
        order = sorted(imps, key=lambda v: [int(n) for n in v[1:].split('.')])
        self.assertEqual(order[:9], ['v0.5', 'v0.6', 'v0.7', 'v0.8', 'v0.9', 'v0.10', 'v0.11', 'v0.12', 'v0.13'])
        self.assertEqual(len(order), len(self.ctx['rulings']['engine_imports']))  # 版ごとに 1 つ（v0.14 からは test_engine_imports_v014_v017）
        for v, (imp_id, commit, docs) in IMPORTS.items():
            imp = imps[v]
            self.assertEqual(imp['id'], imp_id)
            self.assertTrue(imp['commit'].startswith(commit), v)
            self.assertEqual(imp['documents_read_at'], '8facf3aeac35d3473ab382ad49b77062f86fd492')
            for doc in docs:
                self.assertIn(doc, imp['documents'])
            for key in ('imported_rulings', 'unresolved_rulings', 'not_imported', 'notes', 'ruling_sets'):
                self.assertIn(key, imp, v)

    def test_every_engine_ruling_is_traceable(self):
        total = 0
        for v, (imp_id, _, docs) in IMPORTS.items():
            imp = self.rec(self.ctx, 'imports', imp_id)
            for doc, n in docs.items():
                ids = [rid for rs in imp['ruling_sets'] if rs['document'] == doc for rid in bcr.ruling_set_ids(rs)]
                self.assertEqual(len(ids), n, (v, doc))
                mapping = bcr.engine_mapping(self.ctx, imp_id, doc)
                skipped = {x['ruling_id'] for x in imp['not_imported'] if x['document'] == doc}
                for rid in ids:
                    self.assertTrue(rid in mapping or rid in skipped, (v, doc, rid))
                    self.assertFalse(rid in mapping and rid in skipped, (v, doc, rid))
                total += n
        self.assertEqual(total, 372)

    def test_not_imported_have_reasons(self):
        n = 0
        for imp in self.ctx['rulings']['engine_imports']:
            for x in imp['not_imported']:
                self.assertTrue(x['reason'], x['ruling_id'])
                n += imp['engine_version'] in IMPORTS
        self.assertEqual(n, 16)  # 実装上の仮定・該当なし・到達しない・実装上の扱い（v0.5〜v0.12）

    def test_same_id_in_different_versions_is_distinct(self):
        # S1: v0.7（ダメージスワップ）と v0.13（こうらがえし）。G1: v0.8 と v0.11。P1: v0.5 と v0.12。H4: v0.6 と v0.9
        s1_v07 = bcr.find_engine_ruling(self.ctx, 'v0.7', 'S1')
        s1_v13 = bcr.find_engine_ruling(self.ctx, 'v0.13', 'S1')
        self.assertIn('CR-POWER-OWN-TURN-BEFORE-ATTACK', [r for _, _, _, r, _ in s1_v07])
        self.assertIn('CR-SHELL-ATTACK-COST', [r for _, _, _, r, _ in s1_v13])
        self.assertEqual([r for _, _, _, r, _ in bcr.find_engine_ruling(self.ctx, 'v0.9', 'H4')], ['UQ-ENERGY-CONVERSION-ZERO'])
        self.assertEqual([r for _, _, _, r, _ in bcr.find_engine_ruling(self.ctx, 'v0.6', 'H4')], ['CC-PMCG1-032-P43'])
        self.assertIn('CR-CHEMICAL-GAS-NOT-DECLARED', [r for _, _, _, r, _ in bcr.find_engine_ruling(self.ctx, 'v0.8', 'G1')])
        self.assertIn('CR-POWER-DECLARED-BY-USE-WORDING', [r for _, _, _, r, _ in bcr.find_engine_ruling(self.ctx, 'v0.11', 'G1')])
        self.assertEqual(bcr.find_engine_ruling(self.ctx, 'v0.12', 'P34')[0][2], 'not_imported')

    def test_imported_and_unresolved_lists_match_mapping(self):
        for imp in self.ctx['rulings']['engine_imports']:
            uses = [(k, i) for (iid, _, _), lst in bcr.engine_uses(self.ctx).items() if iid == imp['id'] for k, i, _ in lst]
            self.assertEqual(sorted(imp['imported_rulings']), sorted({i for k, i in uses if k != 'issue'}), imp['id'])
            self.assertEqual(sorted(imp['unresolved_rulings']), sorted({i for k, i in uses if k == 'issue'}), imp['id'])

    def test_engine_unresolved_index_dispositions(self):
        idx = {u['engine_key']: u for u in self.ctx['rulings']['engine_unresolved_index']}
        self.assertEqual(len([u for u in idx.values() if bcr.version_key(u['engine_version']) <= (0, 13)]), 22)
        for key in ('R13', 'T19b', 'H4', 'C18', 'G37', 'W24', 'T27', 'C34/C35', 'G40', 'P19', 'P32'):
            self.assertEqual(idx[key]['disposition'], 'issue', key)
        for key in ('MULLIGAN', 'POTION-WITHOUT-DAMAGE', 'POTION-UNDAMAGED-TARGET', 'SWITCH-WITHOUT-BENCH', 'CHECK-DOUBLE-KO',
                    'REPARALYSIS', 'CONFUSION-MODIFIERS', 'RETREAT-AFTER-CONFUSION-CLEARED'):
            self.assertEqual(idx[key]['disposition'], 'out_of_scope', key)
            self.assertTrue(idx[key]['reason'], key)
        self.assertEqual(idx['PREVENTED-COIN-DAMAGE']['kyuura_issue'], idx['T19b']['kyuura_issue'])


class ClassificationTest(Base):
    """CONFIRMED・SUPPORTED・UNRESOLVED の分類と、エンジンの分類との違いの記録。"""

    def test_confirmed_and_supported(self):
        for x in self.ctx['rulings']['rulings']:
            self.assertIn(x['status'], ('CONFIRMED', 'SUPPORTED'), x['id'])
            self.assertEqual(bool(x['inference']), x['status'] == 'SUPPORTED', x['id'])
            self.assertTrue(x['basis'], x['id'])

    def test_downgrades_and_upgrades_are_recorded(self):
        for rid, to in (('CR-EFFECTS-AFTER-KO', 'SUPPORTED'), ('CR-KARATE-CHOP-DAMAGE', 'SUPPORTED'), ('CR-FIRE-WALL-EXPIRY', 'SUPPORTED'),
                        ('CR-RAIN-DANCE-BENCH', 'CONFIRMED'), ('CR-PHOENIX-ANY-CAUSE', 'CONFIRMED'), ('CR-ENERGY-TRANS-RAINBOW', 'CONFIRMED')):
            x = self.rec(self.ctx, 'rulings', rid)
            self.assertEqual(x['status'], to, rid)
            self.assertEqual(x['reclassification']['to'], to, rid)
            self.assertTrue(x['reclassification']['reason'], rid)

    def test_field_definition_is_used(self):
        # p.312「「バトル場」と「ベンチ」を合わせて、「場」と呼びます。」（エンジンの R6 は定義の文がないとしていた）
        clause = self.rec(self.ctx, 'clauses', 'GR-2000-P312-FIELD')
        self.assertIn('「バトル場」と「ベンチ」を合わせて「場」と呼ぶ', clause['summary'])
        self.assertTrue(bcr.page_known(self.ctx['rule_history'], 'P43', '312'))

    def test_general_rules_are_clauses_not_per_card_rulings(self):
        clause = self.rec(self.ctx, 'clauses', 'GR-2000-P311-POKEMON-POWERS')
        ids = {e['ruling_id'] for e in clause['engine_refs']}
        self.assertTrue({'P1', 'P5', 'P6', 'P7', 'P8', 'V9', 'R8', 'S4'} <= ids)
        for e in clause['engine_refs']:
            self.assertIn('CONFIRMED', e['engine_classification'])
        # 特殊状態による特殊能力の制限は、一般の規定にしない（説明ごと）
        x = self.rec(self.ctx, 'rulings', 'CR-POWER-STATUS-BY-DESCRIPTION')
        self.assertEqual(x['status'], 'SUPPORTED')
        self.assertNotIn('P15', ids)

    def test_counter_move_clause_is_reused(self):
        # v0.7 の S19 は、v0.13 の取り込みで作った GR-2000-P320-COUNTER-MOVE に結ぶ（新しい条項を作らない）
        clause = self.rec(self.ctx, 'clauses', 'GR-2000-P320-COUNTER-MOVE')
        self.assertIn(('ENGINE-22CBE24', 'S19'), {(e['import'], e['ruling_id']) for e in clause['engine_refs']})
        self.assertEqual(sum(1 for c in self.ctx['rulings']['rule_clauses'] if 'COUNTER-MOVE' in c['id']), 1)

    def test_rain_dance_r13_is_separated_from_the_engine_stop(self):
        issue = self.rec(self.ctx, 'issues', 'UQ-RAIN-DANCE-ATTACH-COUNT')
        self.assertNotIn('UNRESOLVED_', issue['question'] + issue['why_unresolved'])
        r13 = next(e for e in issue['engine_refs'] if e['ruling_id'] == 'R13')
        self.assertIn('エンジンの実装', r13['engine_note'])
        sep = self.rec(self.ctx, 'rulings', 'CR-RAIN-DANCE-SEPARATE-PROCEDURE')
        self.assertEqual(sep['status'], 'CONFIRMED')
        self.assertEqual({e['ruling_id'] for e in sep['engine_refs']}, {'R11'})

    def test_c18_is_not_merged_into_w24(self):
        w = self.rec(self.ctx, 'issues', 'UQ-RETALIATION-DOUBLE-KO')
        c = self.rec(self.ctx, 'issues', 'UQ-COUNTERATTACK-DOUBLE-KO')
        self.assertEqual({e['ruling_id'] for e in w['engine_refs']}, {'W24', 'S37'})
        self.assertEqual({e['ruling_id'] for e in c['engine_refs']} & {'W24', 'S37'}, set())  # W24・S37 とは別の論点
        self.assertIn('C18', {e['ruling_id'] for e in c['engine_refs']})
        self.assertIn('まとめる根拠', ' '.join(c['notes']))

    def test_optional_use_stays_supported(self):
        x = self.rec(self.ctx, 'rulings', 'CR-POWER-OPTIONAL-DECLARATION')
        self.assertEqual(x['status'], 'SUPPORTED')
        self.assertEqual({e['ruling_id'] for e in x['engine_refs']}, {'G10', 'P2'})

    def test_phoenix_order_issues(self):
        order = self.rec(self.ctx, 'issues', 'UQ-PHOENIX-KO-PROCESS-ORDER')
        self.assertEqual({c['engine_ruling'] for c in order['cases']}, {'P27', 'P28', 'P30'})
        self.assertEqual({e['ruling_id'] for e in self.rec(self.ctx, 'issues', 'UQ-PHOENIX-GAS-SOURCE-KO')['engine_refs']}, {'P19'})
        self.assertEqual({e['ruling_id'] for e in self.rec(self.ctx, 'issues', 'UQ-POST-KO-POWERS-ORDER')['engine_refs']}, {'P32'})
        self.assertTrue({'G37', 'G30'} <= {e['ruling_id'] for e in self.rec(self.ctx, 'issues', 'UQ-GUTS-ATTACK-EFFECT')['engine_refs']})
        self.assertEqual({e['ruling_id'] for e in self.rec(self.ctx, 'issues', 'UQ-KO-PREVENTION-ORDER')['engine_refs']}, {'G40', 'G16'})

    def test_fire_wall_latest_description_is_not_duplicated(self):
        lds = [x for x in self.ctx['latest']['records'] if x['card_id'] == 'PMCG5-020' and x['target']['kind'] == 'attack']
        self.assertEqual([x['id'] for x in lds], ['LD-PMCG5-020-ATK0'])
        self.assertEqual(lds[0]['printed_text']['image_check'], 'consistent_where_legible')

    def test_data_error_candidates_are_reported_not_fixed(self):
        cards = self.ctx['cards']
        ivy = self.rec(self.ctx, 'checks', 'CC-PMCG1-008-P43')
        self.assertEqual(ivy['result'], 'data_error')
        self.assertEqual(ivy['data_error'][0]['source_value'], 'つるのむち')
        self.assertEqual(cards['PMCG1-008']['pokemon']['attacks'][0]['name']['ja'], 'つるのムチ')  # 直していない
        abra = self.rec(self.ctx, 'checks', 'CC-PMCG1-043-P43')
        self.assertEqual(abra['data_error'][0]['fix_status'], 'candidate')
        self.assertIn('投げて、', cards['PMCG1-043']['pokemon']['attacks'][0]['text']['ja'])

    def test_latest_description_differences(self):
        leech = self.rec(self.ctx, 'latest', 'LD-PMCG1-001-ATK0')
        self.assertEqual(leech['meaning_change'], 'changed')  # 「とりのぞくことができる」→「とりのぞく」
        ca = self.rec(self.ctx, 'latest', 'LD-PMCG1-057-PWR0')
        self.assertEqual(ca['meaning_change'], 'changed')
        tr = self.rec(self.ctx, 'latest', 'LD-PMCG3-030-PWR0')
        self.assertEqual({q['page'] for q in tr['also_quoted']}, {'159', '323'})
        for x in self.ctx['latest']['records']:
            if x['target']['kind'] != 'trainer':
                self.assertIsNone(x['errata_ref'], x['id'])  # この取り込みのワザ・特殊能力は公式エラッタではない


class BreakageTest(Base):
    """壊したデータを検査が見つけること（18 種類）。"""

    def test_01_wrong_card_id(self):
        ctx = self.copy()
        self.rec(ctx, 'rulings', 'CR-ENERGY-TRANS-SOURCE')['cards'][0]['card_id'] = 'PMCG1-999'
        self.assert_detected(ctx, 'カード id がない: PMCG1-999')

    def test_02_wrong_attack_position(self):
        ctx = self.copy()
        self.rec(ctx, 'latest', 'LD-PMCG1-032-ATK0')['target']['index'] = 1
        self.assert_detected(ctx, 'LD-PMCG1-032-ATK0: PMCG1-032 に pokemon.attacks[1] がない')

    def test_03_wrong_power_position(self):
        ctx = self.copy()
        self.rec(ctx, 'rulings', 'CR-TRANSPARENCY-WHEN')['cards'][0]['target']['name_ja'] = 'あくむ'
        self.assert_detected(ctx, 'の名前が「とうめい」で、記録の「あくむ」と違う')

    def test_04_unknown_source(self):
        ctx = self.copy()
        self.rec(ctx, 'rulings', 'CR-HYDRO-PUMP-DAMAGE')['basis'][0]['source'] = 'P99'
        self.assert_detected(ctx, '出典の記号がない: P99')

    def test_05_unknown_page(self):
        ctx = self.copy()
        self.rec(ctx, 'latest', 'LD-PMCG1-049-PWR0')['latest_description']['page'] = '154'
        self.assert_detected(ctx, 'P43 の p.154 が data/rule_history.json の documents のページの記録にない')

    def test_06_duplicate_latest_description(self):
        ctx = self.copy()
        dup = copy.deepcopy(self.rec(ctx, 'latest', 'LD-PMCG5-020-ATK0'))
        dup['id'] = 'LD-PMCG5-020-ATK9'
        ctx['latest']['records'].append(dup)
        self.assert_detected(ctx, '同じカード・ワザの最新の説明が LD-PMCG5-020-ATK0 にもある')

    def test_07_duplicate_ruling(self):
        ctx = self.copy()
        dup = copy.deepcopy(self.rec(ctx, 'rulings', 'CR-POWER-POISON-ONLY'))
        dup['id'], dup['engine_refs'] = 'CR-POWER-POISON-ONLY-2', []
        ctx['rulings']['rulings'].append(dup)
        self.assert_detected(ctx, '同じカード・同じ問いの記録が CR-POWER-POISON-ONLY にもある')

    def test_08_duplicate_issue(self):
        ctx = self.copy()
        dup = copy.deepcopy(self.rec(ctx, 'issues', 'UQ-RAIN-DANCE-ATTACH-COUNT'))
        dup['id'], dup['engine_refs'], dup['cases'] = 'UQ-RAIN-DANCE-2', [], []
        ctx['rulings']['issues'].append(dup)
        self.assert_detected(ctx, '同じ問いの未解決の論点が UQ-RAIN-DANCE-ATTACH-COUNT にもある')

    def test_09_engine_id_omission(self):
        ctx = self.copy()
        x = self.rec(ctx, 'rulings', 'CR-HURRICANE-PUNCH')
        x['engine_refs'] = []
        self.assert_detected(ctx, 'エンジンの裁定 L12 が、どの記録にも not_imported にもない')

    def test_10_invalid_double_mapping(self):
        ctx = self.copy()
        e = copy.deepcopy(self.rec(ctx, 'issues', 'UQ-ENERGY-CONVERSION-ZERO')['engine_refs'][0])
        self.rec(ctx, 'issues', 'UQ-TRANSPARENCY-COIN-ORDER')['engine_refs'].append(e)
        self.assert_detected(ctx, '2 つ以上の未解決の論点')
        ctx = self.copy()
        imp = self.rec(ctx, 'imports', 'ENGINE-995504E')
        imp['not_imported'].append({'ruling_id': 'H4', 'document': 'docs/haunter-line-v0.9.md', 'reason': '試し'})
        self.assert_detected(ctx, 'not_imported にも記録')
        ctx = self.copy()
        e = self.rec(ctx, 'rulings', 'CR-NIGHTMARE')['engine_refs'][0]
        e['document'] = 'docs/rain-dance-v0.6.md'  # v0.9 の H12 を v0.6 の文書の id として結ぶ
        self.assert_detected(ctx, 'の documents にない')

    def test_11_supported_to_confirmed_without_reason(self):
        ctx = self.copy()
        x = self.rec(ctx, 'rulings', 'CR-POWER-USABLE-THE-TURN-EVOLVED')
        x['status'], x['inference'] = 'CONFIRMED', None
        self.assert_detected(ctx, 'reclassification（理由）が必要')
        ctx = self.copy()
        x = self.rec(ctx, 'rulings', 'CR-EFFECTS-AFTER-KO')
        del x['reclassification']
        self.assert_detected(ctx, 'を SUPPORTED にするには reclassification（理由）が必要')

    def test_12_runtime_error_as_ruling(self):
        ctx = self.copy()
        self.rec(ctx, 'issues', 'UQ-KO-PREVENTION-ORDER')['why_unresolved'] += '起こったら RuntimeError で止める'
        self.assert_detected(ctx, 'エンジンの停止コード・例外の名前')

    def test_13_stop_code_in_conclusion(self):
        ctx = self.copy()
        self.rec(ctx, 'rulings', 'CR-CHEMICAL-GAS-DECLARED-POWERS')['conclusion'] = 'POWER_SUPPRESSED で拒否する'
        self.assert_detected(ctx, 'エンジンの停止コード・例外の名前')
        ctx = self.copy()
        self.rec(ctx, 'rulings', 'CR-RAIN-DANCE-CARD')['basis'].append({'kind': 'derived', 'statement': 'UNRESOLVED_ATTACH_AFTER_POWER_ATTACH で止める'})
        self.assert_detected(ctx, 'エンジンの停止コード・例外の名前')

    def test_14_broken_v013_reference(self):
        ctx = self.copy()
        self.rec(ctx, 'rulings', 'CR-FIRE-WALL-TIMING')['related_rulings'].append('CR-SHELL-ATTACK-NOTHING')
        self.assert_detected(ctx, 'related_rulings の記録がない: CR-SHELL-ATTACK-NOTHING')
        ctx = self.copy()
        e = self.rec(ctx, 'issues', 'UQ-RETALIATION-DOUBLE-KO')['engine_refs'][1]
        e['ruling_id'] = 'S50'
        self.assert_detected(ctx, 'エンジンの裁定 S50 が、取り込み ENGINE-8FACF3A の文書 docs/shell-attack-v0.13.md の範囲（ruling_sets）にない')

    def test_15_broken_general_rule_reference(self):
        ctx = self.copy()
        self.rec(ctx, 'rulings', 'CR-RAIN-DANCE-TARGET')['rule_clause_refs'].append('GR-2000-P310-NOTHING')
        self.assert_detected(ctx, '条項がない: GR-2000-P310-NOTHING')
        ctx = self.copy()
        self.rec(ctx, 'clauses', 'GR-2000-P311-POKEMON-POWERS')['engine_refs'].append(
            {'import': 'ENGINE-0FBC3AB', 'engine_version': 'v0.5', 'document': 'docs/pokemon-powers-v0.5.md', 'ruling_id': 'P15',
             'engine_classification': 'SUPPORTED', 'part': '試し'})
        self.assert_detected(ctx, '一般の規定（条項）に、エンジンが CONFIRMED としていない裁定 P15')

    def test_16_printed_text_mismatch(self):
        ctx = self.copy()
        ctx['cards']['PMCG1-057']['pokemon']['powers'][0]['text']['ja'] = self.rec(ctx, 'latest', 'LD-PMCG1-057-PWR0')['latest_description']['text_ja']
        self.assert_detected(ctx, 'LD-PMCG1-057-PWR0: 印刷の文面の写しが今の data/cards.json と違う')
        self.assert_detected(ctx, 'CC-PMCG1-057-P43: 照合した欄 pokemon.powers[0].text.ja の写しが今の data/cards.json と違う')

    def test_17_faked_card_check_result(self):
        ctx = self.copy()
        x = self.rec(ctx, 'checks', 'CC-PMCG1-011-P43')
        x['result'], x['differences'] = 'no_difference', []
        self.assert_detected(ctx, '照合して差異なし（no_difference）なのに、結んだ最新の説明 LD-PMCG1-011-PWR0 に印刷の文面との違いがある')
        ctx = self.copy()
        x = self.rec(ctx, 'checks', 'CC-PMCG1-008-P43')
        x['data_error'][0]['kyuura_value'] = 'つるのむち'
        self.assert_detected(ctx, 'data_error の kyuura の値が、照合した欄 pokemon.attacks[0].name.ja の写しと違う')

    def test_18_unresolved_index_omission(self):
        ctx = self.copy()
        ctx['rulings']['engine_unresolved_index'] = [u for u in ctx['rulings']['engine_unresolved_index'] if u['engine_key'] != 'G37']
        self.assert_detected(ctx, 'v0.13 までの項目（エンジンが数えるもの）が 21 件')
        self.assert_detected(ctx, 'UQ-GUTS-ATTACK-EFFECT: engine_unresolved_index のどの項目からも結ばれていない')
        ctx = self.copy()
        u = next(u for u in ctx['rulings']['engine_unresolved_index'] if u['engine_key'] == 'P19')
        u['disposition'], u['kyuura_issue'] = 'out_of_scope', None
        self.assert_detected(ctx, 'P19 は取り込んだ版 v0.12 のものなので、out_of_scope にしない')


class ProtectedDataTest(Base):
    """取り込みで変えないファイル（L 段階）と、エンジンの写しとの比較。

    2026-10-19 から、data/cards.json・CSV には拡張パック以外の商品の記録（形式 3）と、訂正の記録（data/curation/card_corrections.json）で
    当てはめた訂正がある。拡張パックの 780 件は、v0.13 の取り込みのコミット（bcf38c7）と比べて、次の欄だけが違う（一括で緩めない）:
      - CORRECTED（v0.17 の取り込みのデータの調査で直した欄）
      - 訂正の記録で当てはめた欄（その欄・notes・corrections。ja_text.json で直した訂正は corrections だけ）
      - 形式 3 で全記録に加えた欄（product_group・play_scope・same_card_group・data_gaps・source_ids.pcg_search。値が None のものは差にならない）
    """

    # v0.17 の取り込みのデータの調査（2026-10-14）で、data/curation/ から作り直して直したカードと欄だけ。ほかは bcf38c7 と同じ
    CORRECTED = {
        'PMCG2-041': {'.pokemon.attacks[0].name.ja', '.jp_print.level', '.ja_text_source', '.notes'},  # ベロリンガ（p.234。CC-PMCG2-041-P234）
        'PMCG6-023': {'.jp_en_differences'},  # キョウのベトベトンの日英の文面の違い（英語版の「if it has any」）
        # 2026-10-24 のアンノーンI・D・F・[N]・[J] の調査で加えた日英の違い（data/curation/card_differences.json。DARK df の対象と 2 匹以上の条件）。
        # ルール文を埋めた neo2-023・025・026 の欄は訂正の記録（FIX-neo2-0xx-RULES-TEXT-JA）から求める
        'neo2-025': {'.jp_en_differences'},
    }
    FORMAT3_FIELDS = ('.product_group', '.play_scope', '.same_card_group', '.data_gaps', '.source_ids.pcg_search')
    HEADER_CHANGED = {'schema_version', 'description', 'text_availability'}  # 形式 3 の説明（拡張パック以外の商品を収録）

    def ledger(self):
        return json.loads((ROOT / 'data' / 'curation' / 'card_corrections.json').read_text(encoding='utf-8'))['corrections']

    def expected_changes(self, cid, after):
        exp = set(self.CORRECTED.get(cid, set()))
        for f in self.FORMAT3_FIELDS:
            cur = after
            for part in f.strip('.').split('.'):
                cur = (cur or {}).get(part)
            if cur is not None:
                exp.add(f)
        for c in self.ledger():
            if c['card_id'] == cid:
                exp.add('.corrections')
                if c['applied_by'] == 'card_corrections':
                    exp |= {'.' + c['field'], '.notes'}
        return exp

    def test_protected_files_are_unchanged_since_v013_import(self):
        # v0.13 の取り込みのコミット（bcf38c7）と同じであること（カードのデータは、上の欄だけが違う）
        for path in PROTECTED:
            if path in ('data/cards.json', 'data/cards.csv', 'data/attacks.csv', 'data/powers.csv'):
                continue
            out = subprocess.run(['git', '-C', str(ROOT), 'diff', '--quiet', 'bcf38c7', '--', path])
            self.assertEqual(out.returncode, 0, path)
        old = json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', 'bcf38c7:data/cards.json'], capture_output=True, text=True, check=True).stdout)
        new = json.loads((ROOT / 'data' / 'cards.json').read_text(encoding='utf-8'))
        self.assertEqual({k for k in set(old) | set(new) if k != 'cards' and old.get(k) != new.get(k)}, self.HEADER_CHANGED)
        self.assertEqual((old['schema_version'], new['schema_version']), (2, 3))
        before = {c['id']: c for c in old['cards']}
        after = {c['id']: c for c in new['cards']}
        self.assertEqual(sorted(before), sorted(c['id'] for c in new['cards'] if c['product_group'] == 'expansion_pack'))
        self.assertFalse(set(before) & {c['id'] for c in new['cards'] if c['product_group'] != 'expansion_pack'})

        def changed(x, y, path=''):
            if isinstance(x, dict) and isinstance(y, dict):
                for k in set(x) | set(y):
                    yield from changed(x.get(k), y.get(k), f'{path}.{k}')
            elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y) and x and isinstance(x[0], dict):
                for i, (a, b) in enumerate(zip(x, y)):
                    yield from changed(a, b, f'{path}[{i}]')
            elif x != y:
                yield path
        for cid in before:
            self.assertEqual(set(changed(before[cid], after[cid])), self.expected_changes(cid, after[cid]), cid)
        # CSV: bcf38c7 の列の値は、上の欄の違うカードの行だけが違う。加わった行は拡張パック以外の商品の記録だけ
        import csv
        import io
        allowed = {cid for cid in before if self.expected_changes(cid, after[cid]) - set(self.FORMAT3_FIELDS)}
        for path, key in (('data/cards.csv', ('id',)), ('data/attacks.csv', ('card_id', 'index')), ('data/powers.csv', ('card_id', 'index'))):
            old_rows = list(csv.DictReader(io.StringIO(subprocess.run(['git', '-C', str(ROOT), 'show', f'bcf38c7:{path}'],
                                                                      capture_output=True, text=True, check=True).stdout)))
            new_rows = {tuple(r[k] for k in key): r for r in csv.DictReader(io.StringIO((ROOT / path).read_text(encoding='utf-8')))}
            for r in old_rows:
                k = tuple(r[c] for c in key)
                self.assertIn(k, new_rows, (path, k))
                diff = [c for c in r if r[c] != new_rows[k][c]]
                if diff:
                    self.assertIn(k[0], allowed, (path, k, diff))
            for k in set(new_rows) - {tuple(r[c] for c in key) for r in old_rows}:
                self.assertNotIn(k[0], before, (path, k))

    def test_card_json_has_no_sidecar_fields(self):
        text = (ROOT / 'data' / 'cards.json').read_text(encoding='utf-8')
        for key in ('latest_description', 'engine_refs', 'LD-PMCG1', 'CR-POWER'):
            self.assertNotIn(key, text)


if __name__ == '__main__':
    unittest.main()
