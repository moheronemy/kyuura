"""サイドカー（data/sidecar/）の検査と参照のテスト。

v0.13 の取り込み（kyuura-engine 8facf3a。わるいカメール PMCG4-021 の「こうらがえし」）の記録を、
『ポケモンカードオフィシャルブック2000』[P43] p.88・p.89・p.321 などで確かめた内容に対して確かめる。
検査が誤りを見つけることは、正しいデータを壊したコピーで確かめる（破壊テスト）。

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


def bcr_vkey(v):
    """エンジンの版の並び（v0.2b・v0.13 など。枝番の文字は無視する）。"""
    import re
    return tuple(int(x) for x in re.findall(r'\d+', v))

# 印刷の文面（data/cards.json）と、p.89 の「ワザ」欄の最新の説明
PRINTED_SHELL_ATTACK = ('次の相手の番で、このカードが相手のワザによってダメージを受けた時、'
                        '(このカードが「きぜつ」するしないにかかわらず、)そのポケモンにも同じダメージを与える。(ダメージ以外の効果は与えない)')
LATEST_SHELL_ATTACK = ('次の相手の番、このカードが相手のワザによってダメージを受けたとき、'
                       '（それによってこのカードが「きぜつ」しても、）そのポケモンにも同じダメージを与える。（ダメージ以外の効果は与えない）')


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()

    def copy(self):
        return copy.deepcopy(self.ctx)

    def find(self, ctx, kind, id_):
        recs = {'latest': ctx['latest']['records'], 'checks': ctx['checks']['records'],
                'rulings': ctx['rulings']['rulings'], 'issues': ctx['rulings']['issues'],
                'clauses': ctx['rulings']['rule_clauses']}[kind]
        return next(x for x in recs if x['id'] == id_)

    def assert_detected(self, ctx, fragment):
        errors = bcr.validate(ctx)
        self.assertTrue(any(fragment in e for e in errors), f'「{fragment}」のエラーがない: {errors}')


class ValidDataTest(Base):
    def test_current_data_has_no_errors(self):
        self.assertEqual(bcr.validate(self.ctx), [])

    def test_generated_page_is_up_to_date(self):
        out = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_card_rulings.py'), '--check'],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)


class CardReferenceTest(Base):
    """J1: カードの参照（PMCG4-018・PMCG4-021。p.88・p.89）。"""

    def test_target_cards_exist_and_are_identified(self):
        cards = self.ctx['cards']
        self.assertEqual(cards['PMCG4-018']['name']['ja'], 'ゼニガメ')
        self.assertEqual(cards['PMCG4-018']['pokemon']['hp'], 50)
        self.assertEqual(cards['PMCG4-021']['name']['ja'], 'わるいカメール')
        self.assertEqual(cards['PMCG4-021']['pokemon']['evolves_from']['ja'], 'ゼニガメ')
        self.assertEqual(cards['PMCG4-021']['pokemon']['attacks'][1]['name']['ja'], 'こうらがえし')

    def test_not_confused_with_other_cards(self):
        cards = self.ctx['cards']
        self.assertEqual(cards['PMCG4-008']['name']['ja'], 'わるいアーボック')
        self.assertEqual(cards['PMCG4-024']['name']['ja'], 'わるいカメックス')
        self.assertEqual(cards['PMCG1-027']['name']['ja'], 'カメール')
        for cid in ('PMCG4-024', 'PMCG4-008'):
            notes = bcr.annotations_for(self.ctx, cid)
            self.assertEqual(notes['latest_descriptions'], [], cid)
            self.assertEqual(notes['card_checks'], [], cid)
            self.assertEqual(notes['rulings'], [], cid)
        # 第1弾のゼニガメ・カメールは v0.6 の取り込み（p.87・p.88）で自分の記録を持つ。わるいカメールの記録とは混ざらない
        for cid in ('PMCG1-027', 'PMCG1-023'):
            notes = bcr.annotations_for(self.ctx, cid)
            for kind in ('latest_descriptions', 'card_checks'):
                self.assertTrue(all(x['card_id'] == cid for x in notes[kind]), cid)
            self.assertFalse([x['id'] for x in notes['rulings'] if x['id'].startswith('CR-SHELL-ATTACK')], cid)

    def test_unknown_card_id_is_rejected(self):
        ctx = self.copy()
        self.find(ctx, 'latest', 'LD-PMCG4-021-ATK1')['card_id'] = 'PMCG4-999'
        self.assert_detected(ctx, 'カード id がない: PMCG4-999')
        ctx = self.copy()
        self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-COST')['cards'][0]['card_id'] = 'PMCG4-999'
        self.assert_detected(ctx, 'カード id がない: PMCG4-999')

    def test_wrong_attack_is_rejected(self):
        ctx = self.copy()
        self.find(ctx, 'latest', 'LD-PMCG4-021-ATK1')['target']['index'] = 0
        self.assert_detected(ctx, '名前が「おうふくびんた」')

    def test_source_and_page_must_exist(self):
        ctx = self.copy()
        self.find(ctx, 'latest', 'LD-PMCG4-021-ATK1')['latest_description']['page'] = '999'
        self.assert_detected(ctx, 'p.999 が data/rule_history.json の documents のページの記録にない')
        ctx = self.copy()
        self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-COST')['basis'][0]['source'] = 'P99'
        self.assert_detected(ctx, '出典の記号がない: P99')


class LatestDescriptionTest(Base):
    """J2: 最新の説明（p.89）。印刷の文面は data/cards.json のまま。"""

    def test_printed_text_is_kept(self):
        self.assertEqual(self.ctx['cards']['PMCG4-021']['pokemon']['attacks'][1]['text']['ja'], PRINTED_SHELL_ATTACK)
        self.assertNotIn('latest_description', json.dumps(self.ctx['cards']['PMCG4-021'], ensure_ascii=False))

    def test_latest_description_and_source(self):
        ld = next(x for x in bcr.annotations_for(self.ctx, 'PMCG4-021')['latest_descriptions'] if x['target']['index'] == 1)
        self.assertEqual(ld['latest_description']['text_ja'], LATEST_SHELL_ATTACK)
        self.assertEqual((ld['latest_description']['source'], ld['latest_description']['page']), ('P43', '89'))
        self.assertEqual(ld['printed_text']['text_ja'], PRINTED_SHELL_ATTACK)

    def test_differences_are_traceable(self):
        ld = self.find(self.ctx, 'latest', 'LD-PMCG4-021-ATK1')
        pairs = {(d['printed'], d['latest']) for d in ld['differences']}
        self.assertIn(('次の相手の番で', '次の相手の番'), pairs)
        self.assertIn(('受けた時', '受けたとき'), pairs)
        self.assertIn(('(このカードが「きぜつ」するしないにかかわらず、)', '（それによってこのカードが「きぜつ」しても、）'), pairs)
        ctx = self.copy()
        self.find(ctx, 'latest', 'LD-PMCG4-021-ATK1')['differences'][0]['printed'] = '次の番で'
        self.assert_detected(ctx, '「次の番で」が印刷の文面にない')

    def test_latest_description_is_not_errata(self):
        ld = self.find(self.ctx, 'latest', 'LD-PMCG4-021-ATK1')
        self.assertEqual(ld['classification'], 'latest_description')
        self.assertIsNone(ld['errata_ref'])
        self.assertNotIn('PMCG4-021', bcr.errata_cards(self.ctx['rule_history']))
        ctx = self.copy()
        next(x for x in ctx['rule_history']['errata'] if x['id'] == 'ERR-PLUSPOWER')['cards'].append('PMCG4-021')
        self.assert_detected(ctx, 'errata_ref で結ぶ')

    def test_printed_text_drift_is_detected(self):
        ctx = self.copy()
        ctx['cards']['PMCG4-021']['pokemon']['attacks'][1]['text']['ja'] = LATEST_SHELL_ATTACK
        self.assert_detected(ctx, '印刷の文面の写しが今の data/cards.json と違う')
        self.assert_detected(ctx, '照合した欄 pokemon.attacks[1].text.ja の写しが今の data/cards.json と違う')

    def test_checked_without_difference_is_distinct_from_unchecked(self):
        squirtle = bcr.annotations_for(self.ctx, 'PMCG4-018')['card_checks']
        self.assertEqual([c['result'] for c in squirtle], ['no_difference'])
        self.assertEqual(bcr.annotations_for(self.ctx, 'PMCG1-002')['card_checks'], [])  # 未照合（v0.5 の取り込みで PMCG1-001 は照合ずみになった）

    def test_printed_vs_latest_is_not_a_data_error(self):
        check = self.find(self.ctx, 'checks', 'CC-PMCG4-021-P43')
        self.assertFalse(check['data_error'])
        self.assertEqual(check['result'], 'printed_vs_latest_only')


class RulingTest(Base):
    """J3: 裁定と、エンジンの S1〜S49 との対応。"""

    def test_every_engine_ruling_is_traceable(self):
        mapping = bcr.engine_mapping(self.ctx, 'ENGINE-8FACF3A')
        for n in range(1, 50):
            self.assertIn(f'S{n}', mapping, f'S{n}')

    def test_confirmed_and_supported_bases(self):
        for x in self.ctx['rulings']['rulings']:
            if x['status'] == 'CONFIRMED':
                self.assertFalse(x['inference'], x['id'])
            else:
                self.assertEqual(x['status'], 'SUPPORTED', x['id'])
                self.assertTrue(x['inference'], x['id'])
        ctx = self.copy()
        self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-ATTACKER-PLUSPOWER')['inference'] = None
        self.assert_detected(ctx, 'SUPPORTED に推論（inference）がない')

    def test_supported_is_not_upgraded_without_reason(self):
        ctx = self.copy()
        x = self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-OWN-RESISTANCE')
        x['status'], x['inference'] = 'CONFIRMED', None
        self.assert_detected(ctx, 'reclassification（理由）が必要')

    def test_reclassification_is_recorded(self):
        x = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-ENDS-ON-DEVOLUTION')
        self.assertEqual(x['reclassification']['to'], 'CONFIRMED')
        self.assertTrue(x['reclassification']['reason'])
        self.assertIn('p.324', x['basis'][0]['location'])

    def test_unresolved_only_as_issues_with_reasons(self):
        for x in self.ctx['rulings']['issues']:
            self.assertEqual(x['status'], 'UNRESOLVED')
            self.assertTrue(x['why_unresolved'])
        ctx = self.copy()
        self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-COST')['status'] = 'UNRESOLVED'
        self.assert_detected(ctx, 'status の値が不正')

    def test_s37_and_w24_are_one_issue(self):
        mapping = bcr.engine_mapping(self.ctx, 'ENGINE-8FACF3A')
        self.assertEqual([i for _, i, _ in mapping['S37']], ['UQ-RETALIATION-DOUBLE-KO'])
        # W24 は、v0.12 の取り込み（ENGINE-B8054AF）があればそこに、なければ v0.13 の取り込みに仮に結ぶ
        v012 = [imp['id'] for imp in self.ctx['rulings']['engine_imports'] if imp['engine_version'] == 'v0.12']
        mapping = bcr.engine_mapping(self.ctx, v012[0]) if v012 else mapping
        self.assertEqual([i for _, i, _ in mapping['W24']], ['UQ-RETALIATION-DOUBLE-KO'])
        issue = self.find(self.ctx, 'issues', 'UQ-RETALIATION-DOUBLE-KO')
        self.assertEqual({c['card_id'] for c in issue['cases']}, {'PMCG4-021', 'PMCG5-020'})
        ctx = self.copy()
        dup = copy.deepcopy(self.find(ctx, 'issues', 'UQ-RETALIATION-DOUBLE-KO'))
        dup['id'] = 'UQ-SHELL-ATTACK-DOUBLE-KO'
        dup['engine_refs'] = [e for e in dup['engine_refs'] if e['ruling_id'] == 'S37']
        dup['cases'] = [c for c in dup['cases'] if c['engine_ruling'] == 'S37']
        ctx['rulings']['issues'].append(dup)
        self.assert_detected(ctx, '2 つ以上の未解決の論点')

    def test_s7_is_tied_to_c34_c35(self):
        issue = self.find(self.ctx, 'issues', 'UQ-MULTIPLE-DAMAGE-TRIGGERS-ONE-ATTACK')
        # v0.13 の S7 は C34・C35 と同じ論点（v0.17 の Z18・DR18 も同じ問いとして加わる）
        self.assertTrue({'C34', 'C35', 'S7'} <= {e['ruling_id'] for e in issue['engine_refs']})
        self.assertIn('engine_card_pool', issue['reachability'])
        self.assertEqual(issue['official_material'], 'none_found')

    def test_engine_runtime_error_is_not_an_official_ruling(self):
        for x in self.ctx['rulings']['rulings'] + self.ctx['rulings']['issues']:
            for key in ('question', 'conclusion', 'inference', 'why_unresolved'):
                self.assertNotIn('RuntimeError', x.get(key) or '', x['id'])
        ctx = self.copy()
        self.find(ctx, 'issues', 'UQ-MULTIPLE-DAMAGE-TRIGGERS-ONE-ATTACK')['why_unresolved'] += ' RuntimeError で止める'
        self.assert_detected(ctx, 'エンジンの停止コード・例外の名前')
        ctx = self.copy()
        self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-NO-CHAIN')['conclusion'] = 'UNRESOLVED_RETALIATION_DOUBLE_KNOCKOUT で止める'
        self.assert_detected(ctx, 'エンジンの停止コード・例外の名前')

    def test_unmapped_engine_ruling_is_detected(self):
        ctx = self.copy()
        self.find(ctx, 'checks', 'CC-PMCG4-018-P43')['engine_refs'] = []
        self.assert_detected(ctx, 'エンジンの裁定 S43 が、どの記録にも not_imported にもない')

    def test_split_without_part_is_detected(self):
        ctx = self.copy()
        for e in self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-STAR-BOOMERANG')['engine_refs']:
            e.pop('part', None)
        self.assert_detected(ctx, 'part（どの部分か）を書く')

    def test_duplicate_and_malformed_ids_are_detected(self):
        ctx = self.copy()
        ctx['rulings']['rulings'].append(copy.deepcopy(self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-COST')))
        self.assert_detected(ctx, 'id の重複: CR-SHELL-ATTACK-COST')
        ctx = self.copy()
        self.find(ctx, 'rulings', 'CR-SHELL-ATTACK-COST')['id'] = 'RULING-1'
        self.assert_detected(ctx, 'id の書式が不正')

    def test_engine_unresolved_index(self):
        idx = self.ctx['rulings']['engine_unresolved_index']
        # v0.13 までの項目は 22 件（停止コード 17 件）。あとの版の項目はこの数に足す（過去の件数を総数として固定しない）
        old = [u for u in idx if bcr_vkey(u['engine_version']) <= (0, 13)]
        self.assertEqual(len(old), 22)
        self.assertEqual(sum(1 for u in old if u['stop_code']), 17)
        imported = {u['engine_key']: u['kyuura_issue'] for u in idx if u['kyuura_issue']}
        # v0.13 の取り込みの 2 件はどの段階でも同じ論点に結ぶ
        self.assertEqual(imported['W24'], 'UQ-RETALIATION-DOUBLE-KO')
        self.assertEqual(imported['C34/C35'], 'UQ-MULTIPLE-DAMAGE-TRIGGERS-ONE-ATTACK')
        versions = {imp['engine_version'] for imp in self.ctx['rulings']['engine_imports']}
        for u in idx:
            # その版を取り込む前の項目だけが not_yet_imported（取り込んだ版の項目は、論点・実装だけ・範囲外のどれか）
            self.assertEqual(u['disposition'] == 'not_yet_imported', u['engine_version'] not in versions
                             and u['disposition'] not in ('out_of_scope', 'issue'), u['engine_key'])
        if 'v0.10' in versions:
            self.assertEqual(imported['C18'], 'UQ-COUNTERATTACK-DOUBLE-KO')  # W24 の論点にはまとめない
        for key, version in (('G37', 'v0.11'), ('G40', 'v0.11'), ('T27', 'v0.9')):
            if version in versions:
                self.assertTrue(imported[key].startswith('UQ-'), key)
        ctx = self.copy()
        ctx['rulings']['engine_unresolved_index'] = [u for u in ctx['rulings']['engine_unresolved_index'] if u['engine_key'] != 'MULLIGAN']
        self.assert_detected(ctx, 'v0.13 までの項目（エンジンが数えるもの）が 21 件')


class RuleReferenceTest(Base):
    """J4: 公式ルールの条項（p.321 など）と、カード固有の説明の区別。"""

    def test_damage_order_clause_points_to_the_general_rule(self):
        clause = self.find(self.ctx, 'clauses', 'GR-2000-P321-DAMAGE-ORDER')
        self.assertIn('NEO-2000-OFFICIAL-RULES', clause['rule_history_refs'])
        self.assertIn('weakness_resistance', clause['rule_differences_refs'])
        self.assertTrue(bcr.page_known(self.ctx['rule_history'], 'P43', '321'))
        ctx = self.copy()
        self.find(ctx, 'clauses', 'GR-2000-P321-DAMAGE-ORDER')['rule_history_refs'].append('NEO-1999-NOTHING')
        self.assert_detected(ctx, 'rule_history の記録がない: NEO-1999-NOTHING')

    def test_card_commentary_and_general_rule_are_distinct(self):
        weakness = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-OWN-WEAKNESS')
        self.assertEqual({b['kind'] for b in weakness['basis']}, {'card_commentary'})
        resistance = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-OWN-RESISTANCE')
        self.assertIn('general_rule', {b['kind'] for b in resistance['basis']})
        self.assertEqual(resistance['status'], 'SUPPORTED')

    def test_star_boomerang_example(self):
        x = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-STAR-BOOMERANG')
        self.assertEqual(x['status'], 'CONFIRMED')
        self.assertEqual(x['basis'][0]['page'], '89')
        self.assertIn('LD-PMCG5-027-ATK0', x['latest_description_refs'])
        related = bcr.annotations_for(self.ctx, 'PMCG5-027')['related_rulings']
        self.assertIn('CR-SHELL-ATTACK-STAR-BOOMERANG', [r['id'] for r in related])

    def test_persistent_effect_sources(self):
        expiry = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-EXPIRY')
        self.assertEqual((expiry['basis'][0]['source'], expiry['basis'][0]['page']), ('P43', '89'))
        bench = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-ENDS-ON-BENCH')
        self.assertIn('GR-2000-P322-PERSISTENT-EFFECTS', bench['rule_clause_refs'])

    def test_received_and_returned_damage_are_distinct_records(self):
        received = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-RECEIVED-DAMAGE')
        returned = self.find(self.ctx, 'rulings', 'CR-SHELL-ATTACK-RETURN-IS-ATTACK-DAMAGE')
        self.assertNotEqual(received['conclusion'], returned['conclusion'])
        self.assertIn('GR-2000-P321-ATTACK-DAMAGE', returned['rule_clause_refs'])


class CompatibilityTest(Base):
    """J5: 既存のデータと読み手の互換性。"""

    def test_card_data_counts_and_ids(self):
        ids = [c['id'] for c in json.loads((ROOT / 'data' / 'cards.json').read_text(encoding='utf-8'))['cards']]
        self.assertEqual(len(ids), 780)
        self.assertEqual(len(set(ids)), 780)

    def test_cards_without_sidecar_records(self):
        notes = bcr.annotations_for(self.ctx, 'PMCG1-002')  # v0.5 の取り込みで PMCG1-001 には記録ができた
        self.assertEqual(notes, {'latest_descriptions': [], 'card_checks': [], 'rulings': [], 'related_rulings': [], 'issues': []})

    def test_existing_builders_still_pass(self):
        for script in ('build_rule_history.py', 'build_rule_differences.py'):
            out = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), '--check'], capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, f'{script}: {out.stderr}')

    def test_card_json_has_no_sidecar_fields(self):
        text = (ROOT / 'data' / 'cards.json').read_text(encoding='utf-8')
        for key in ('latest_description', 'engine_refs', 'LD-PMCG4-021'):
            self.assertNotIn(key, text)


if __name__ == '__main__':
    unittest.main()
