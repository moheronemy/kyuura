"""kyuura-engine v0.13〜v0.17 の取り込みの整合と、v0.17 の取り込み（Z1〜Z30・DR1〜DR20）の網羅・分類、破壊テスト。

- v0.13 の取り込み（ENGINE-8FACF3A。わるいカメールの S1〜S49）は作り直さず、そのまま保つ。
- v0.14〜v0.16 は実装の履歴（イベントの仕組み・先読み・旧経路の撤去）で、裁定の表がない。読んだ文書と、ルールに関わる記述の
  注記だけを持つ（no_ruling_tables）。エンジンの実装の判断を公式の裁定として加えない。
- v0.17 の原典は p.245（R団のカビゴン）・p.49（キョウのベトベトン）・p.55（モンジャラ）・p.229（サカキのニャース）・p.138（マチスの
  マルマインのショックボム）・p.155（ナツメのヤドンのぐうたらこうげき）と、公式ルール pp.309〜325（kyuura が画像で確かめた）。
- エンジンの文書は調査の履歴で、原典ではない。原典は『ポケモンカードオフィシャルブック2000』[P43]（スキャン [J38]）。

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

BASE = 'bcf38c70a263b04dde9c25b602b65f5bad8f04dc'  # この作業の基準（v0.13 の取り込みのあと）
ENGINE_HEAD = 'd90bce183fde925ed61d83f26e16856a0af6a0f8'  # 参照したエンジンのコミット（v0.17.0）
HISTORY = {  # 裁定の表のない版: 版 → (取り込みの id, コミット)
    'v0.14': ('ENGINE-0900209', '0900209ca14f761cb85b9dbb8bde11d5dd8e314b'),
    'v0.15': ('ENGINE-AA551AB', 'aa551ab0601e916c3fae3195780eb0aa07761deb'),
    'v0.16': ('ENGINE-15770C6', '15770c6686dd5dc54380058b7a53c0276e5c6172'),
}


def base_json(path):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{path}'], capture_output=True, text=True, check=True).stdout)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()

    def copy(self):
        return copy.deepcopy(self.ctx)

    def imp(self, ctx, version):
        return next(x for x in ctx['rulings']['engine_imports'] if x['engine_version'] == version)

    def assert_detected(self, ctx, fragment):
        errors = bcr.validate(ctx)
        self.assertTrue(any(fragment in e for e in errors), f'「{fragment}」のエラーがない: {errors[:5]}')


class V013KeptTest(Base):
    """v0.13 の取り込みを作り直さない（S1〜S49 の対応・既存の記録を保つ）。"""

    def test_v013_records_are_kept(self):
        old = base_json('data/sidecar/rulings.json')
        now = self.ctx['rulings']
        for key in ('rulings', 'rule_clauses', 'issues', 'comparisons'):
            ids = {x['id'] for x in now[key]}
            for x in old[key]:
                self.assertIn(x['id'], ids, x['id'])
        # 既存の裁定（CR-）は 1 件も書きかえていない
        rul = {x['id']: x for x in now['rulings']}
        for x in old['rulings']:
            self.assertEqual(rul[x['id']], x, x['id'])
        for name in ('latest_descriptions', 'card_checks'):
            ids = {x['id'] for x in self.ctx['latest' if name == 'latest_descriptions' else 'checks']['records']}
            for x in base_json(f'data/sidecar/{name}.json')['records']:
                self.assertIn(x['id'], ids, x['id'])

    def test_s1_to_s49_mapping_is_unchanged(self):
        def mapping(r, checks):
            out = {}
            for kind in ('rulings', 'issues', 'rule_clauses'):
                for x in r[kind]:
                    for e in x.get('engine_refs', []):
                        if e['import'] == 'ENGINE-8FACF3A' and e['document'] == 'docs/shell-attack-v0.13.md':
                            out.setdefault(e['ruling_id'], set()).add(x['id'])
            for x in checks:
                for e in x.get('engine_refs', []):
                    if e['import'] == 'ENGINE-8FACF3A' and e['document'] == 'docs/shell-attack-v0.13.md':
                        out.setdefault(e['ruling_id'], set()).add(x['id'])
            return out
        old = mapping(base_json('data/sidecar/rulings.json'), base_json('data/sidecar/card_checks.json')['records'])
        now = mapping(self.ctx['rulings'], self.ctx['checks']['records'])
        self.assertEqual(now, old)
        self.assertEqual(sorted(now, key=lambda i: int(i[1:])), [f'S{n}' for n in range(1, 50)])

    def test_v013_import_is_the_same_commit(self):
        imp = self.imp(self.ctx, 'v0.13')
        self.assertEqual(imp['id'], 'ENGINE-8FACF3A')
        self.assertTrue(imp['commit'].startswith('8facf3a'))
        self.assertTrue(any('d90bce1' in n for n in imp['notes']))  # v0.17 でも文書が変わっていないことの注記


class ImplementationHistoryTest(Base):
    """v0.14〜v0.16 は裁定の表のない版。実装の履歴を公式の裁定にしない。"""

    def test_history_versions_have_no_rulings(self):
        for v, (imp_id, commit) in HISTORY.items():
            imp = self.imp(self.ctx, v)
            self.assertEqual(imp['id'], imp_id)
            self.assertEqual(imp['commit'], commit)
            self.assertTrue(imp.get('no_ruling_tables'), v)
            self.assertEqual(imp['ruling_sets'], [], v)
            self.assertEqual(imp['imported_rulings'], [], v)
            self.assertEqual(imp['unresolved_rulings'], [], v)
            self.assertEqual(imp['documents_read_at'], ENGINE_HEAD, v)
            self.assertTrue(imp['notes'], v)
            # どの記録からも結ばれていない（公式の裁定・論点にしていない）
            self.assertFalse([k for k in bcr.engine_uses(self.ctx) if k[0] == imp_id], v)

    def test_listed_documents_were_requested(self):
        self.assertIn('docs/event-model-v0.14.md', self.imp(self.ctx, 'v0.14')['documents'])
        self.assertIn('docs/event-prototype-verification-v0.14.md', self.imp(self.ctx, 'v0.14')['documents'])
        self.assertIn('docs/event-integration-verification-v0.15d.md', self.imp(self.ctx, 'v0.15')['documents'])
        self.assertIn('docs/kernel-consolidation-verification-v0.16e.md', self.imp(self.ctx, 'v0.16')['documents'])
        self.assertIn('docs/preflight-consolidation-v0.16c.md', self.imp(self.ctx, 'v0.16')['documents'])

    def test_ruling_sets_in_a_history_version_are_rejected(self):
        ctx = self.copy()
        imp = self.imp(ctx, 'v0.14')
        imp['ruling_sets'].append({'prefix': 'M', 'first': 1, 'last': 27, 'document': 'docs/event-prototype-verification-v0.14.md',
                                   'engine_reported_counts': {}})
        self.assert_detected(ctx, 'no_ruling_tables の取り込みに ruling_sets')

    def test_import_without_ruling_sets_must_say_so(self):
        ctx = self.copy()
        del self.imp(ctx, 'v0.15')['no_ruling_tables']
        self.assert_detected(ctx, 'ruling_sets がない')

    def test_history_note_is_required(self):
        ctx = self.copy()
        self.imp(ctx, 'v0.16')['notes'] = []
        self.assert_detected(ctx, '注記（notes）がない')


class TransitionalStateTest(Base):
    """段階を分けた取り込みの途中だけの形（not_yet_imported・別の版の取り込みへの仮の対応）を、取り込んだ版に使わない。"""

    def test_not_yet_imported_is_rejected_for_an_imported_version(self):
        ctx = self.copy()
        u = next(x for x in ctx['rulings']['engine_unresolved_index'] if x['engine_key'] == 'C18')
        u['disposition'], u['reason'], u['kyuura_issue'] = 'not_yet_imported', '取り込みの前', None
        self.assert_detected(ctx, 'not_yet_imported にしない')

    def test_provisional_link_is_rejected_once_the_version_is_imported(self):
        ctx = self.copy()
        issue = next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-RETALIATION-DOUBLE-KO')
        e = next(e for e in issue['engine_refs'] if e['ruling_id'] == 'W24')
        e['import'] = 'ENGINE-8FACF3A'  # v0.12 の取り込みがあるのに、v0.13 の取り込みに結ぶ
        self.assert_detected(ctx, 'v0.12 の取り込みに結ぶ')

    def test_not_imported_status_is_required(self):
        ctx = self.copy()
        n = self.imp(ctx, 'v0.5')['not_imported'][0]
        del n['status']
        self.assert_detected(ctx, 'status の値が不正')

    def test_excluded_only_for_implementation_decisions(self):
        ctx = self.copy()
        n = next(n for n in self.imp(ctx, 'v0.5')['not_imported'] if n['ruling_id'] == 'P17')  # 該当なし（エンジンは判断していない）
        n['status'] = 'excluded'
        self.assert_detected(ctx, '対象外（excluded）にしているが')


class V017CoverageTest(Base):
    """v0.17 の裁定 Z1〜Z30・DR1〜DR20 の網羅と、4 枚のカードの照合。"""

    def test_all_v017_rulings_are_mapped_or_not_imported(self):
        imp = self.imp(self.ctx, 'v0.17')
        self.assertEqual(imp['id'], 'ENGINE-D90BCE1')
        self.assertEqual(imp['commit'], ENGINE_HEAD)
        uses = bcr.engine_uses(self.ctx)
        skipped = {n['ruling_id'] for n in imp['not_imported']}
        self.assertEqual(skipped, {'DR14', 'DR20'})
        for doc, ids in (('docs/rocket-snorlax-v0.17b.md', [f'Z{n}' for n in range(1, 31)]),
                         ('docs/kogas-muk-event-design-v0.17c.md', [f'DR{n}' for n in range(1, 21)])):
            for rid in ids:
                self.assertTrue(('ENGINE-D90BCE1', doc, rid) in uses or rid in skipped, rid)

    def test_four_cards_are_checked_against_the_book(self):
        checks = {x['card_id']: x for x in self.ctx['checks']['records']}
        expect = {'PMCG1-007': ('55', 'no_difference'), 'PMCG6-063': ('229', 'no_difference'),
                  'PMCG6-073': ('245', 'printed_vs_latest_only'), 'PMCG6-023': ('49', 'printed_vs_latest_only')}
        for cid, (page, result) in expect.items():
            self.assertEqual(checks[cid]['page'], page, cid)
            self.assertEqual(checks[cid]['result'], result, cid)
            # kyuura が自分で画像を読んだ記録と、エンジンの記録が分けて書かれている
            by = [v['by'] for v in checks[cid]['verification']]
            self.assertEqual(by, ['kyuura', 'kyuura-engine'], cid)
            self.assertEqual(checks[cid]['verification'][0]['date'], '2026-10-14')

    def test_latest_descriptions_do_not_overwrite_printed_text(self):
        cards = self.ctx['cards']
        lds = {x['id']: x for x in self.ctx['latest']['records']}
        for ld_id, path in (('LD-PMCG6-073-PWR0', ('powers', 0)), ('LD-PMCG6-073-ATK0', ('attacks', 0)), ('LD-PMCG6-023-PWR0', ('powers', 0))):
            ld = lds[ld_id]
            printed = cards[ld['card_id']]['pokemon'][path[0]][path[1]]['text']['ja']
            self.assertEqual(ld['printed_text']['text_ja'], printed)  # data/cards.json の印刷の文面のまま
            self.assertNotEqual(ld['latest_description']['text_ja'], printed)
            self.assertIsNone(ld['errata_ref'])  # 最新の説明は公式エラッタではない
        # モンジャラ・サカキのニャースは最新の説明と印刷の文面が同じなので、最新の説明の記録を作らない
        self.assertFalse([x for x in lds.values() if x['card_id'] in ('PMCG1-007', 'PMCG6-063')])


class V017ClassificationTest(Base):
    """Z9・Z23・DR1・DR6 などを、根拠なしに解決済みにしない。エンジンの停止コードを公式の裁定にしない。"""

    def issue(self, issue_id):
        return next(x for x in self.ctx['rulings']['issues'] if x['id'] == issue_id)

    def test_z9_and_z23_are_unresolved_issues(self):
        mapping = bcr.engine_mapping(self.ctx, 'ENGINE-D90BCE1', 'docs/rocket-snorlax-v0.17b.md')
        self.assertEqual([(k, i) for k, i, _ in mapping['Z9']], [('issue', 'UQ-POWER-DAMAGE-WEAKNESS-RESISTANCE')])
        self.assertEqual([(k, i) for k, i, _ in mapping['Z23']], [('issue', 'UQ-EFFECT-AFTER-NO-DAMAGE')])
        idx = {u['engine_key']: u for u in self.ctx['rulings']['engine_unresolved_index']}
        # v0.17 ではコードのない問い（結果が変わる場合だけ止める）。エンジンは v0.61 で停止コードを付けた（stop_code_since）
        self.assertTrue(idx['Z9']['stop_code'] is None or bcr.version_key(idx['Z9']['stop_code_since']) > (0, 17))
        self.assertEqual(idx['Z23']['stop_code'], 'UNRESOLVED_EFFECT_AFTER_NO_DAMAGE')  # 停止コードは対応の記録だけに書く
        z9 = self.issue('UQ-POWER-DAMAGE-WEAKNESS-RESISTANCE')
        # 「今のデータでは結果が変わらない」ことと、裁定が未解決であることを分けて書く
        self.assertIn('裁定が決まったことではない', ' '.join(z9['notes']))
        self.assertIn('無色の弱点・抵抗力', z9['reachability']['all_cards'])

    def test_no_colorless_weakness_or_resistance_in_the_data(self):
        # Z9 の「結果が変わらない」の根拠（kyuura のデータ）
        for c in self.ctx['cards'].values():
            if c.get('pokemon'):
                types = [w['type'] for w in c['pokemon']['weaknesses'] + c['pokemon']['resistances']]
                self.assertNotIn('colorless', types, c['id'])

    def test_energy_drain_questions_are_separate_issues(self):
        idx = {u['engine_key']: u for u in self.ctx['rulings']['engine_unresolved_index']}
        expect = {'DR1': 'UQ-ENERGY-DRAIN-DECLARATION', 'DR6': 'UQ-ENERGY-DRAIN-TIMING', 'DR8': 'UQ-ENERGY-DRAIN-ATTACKER-KO',
                  'DR13': 'UQ-ENERGY-DRAIN-NO-ENERGY'}
        for key, issue_id in expect.items():
            self.assertEqual(idx[key]['kyuura_issue'], issue_id, key)
            # v0.17 ではエンジンの 24 件には入らない（カードを延期）。DR8・DR13 は v0.68 から数える（counted_from_version）
            counted_at_v017 = idx[key].get('in_engine_count', True) and bcr.version_key(idx[key].get('counted_from_version') or 'v0.17') <= (0, 17)
            self.assertFalse(counted_at_v017, key)
        self.assertIn('UQ-ENERGY-DRAIN-TIMING', self.issue('UQ-ENERGY-DRAIN-DECLARATION')['related_issues'])
        # DR18 は C34/C35 と同じ論点（新しい論点にしない）
        self.assertIn(('v0.17', 'DR18'), {(i['engine_version'], i['ruling_id']) for i in idx['C34/C35']['instances']})

    def test_later_rules_and_english_text_are_not_used_as_basis(self):
        decl = self.issue('UQ-ENERGY-DRAIN-DECLARATION')
        notes = ' '.join(decl['notes'])
        self.assertIn('2002年', notes)  # 後年の「ポケボディーとして扱う」一覧は当てはめないと書く
        self.assertIn('当てはめない', notes)
        for x in self.ctx['rulings']['rulings']:
            if any(c['card_id'] == 'PMCG6-023' for c in x['cards']):
                for b in x['basis']:
                    self.assertEqual(b.get('source', 'P43'), 'P43', x['id'])  # 根拠は『オフィシャルブック2000』だけ
                    self.assertNotIn('if it has any', b.get('quote', ''), x['id'])

    def test_confirmed_energy_drain_items(self):
        rul = {x['id']: x for x in self.ctx['rulings']['rulings']}
        for rid, engine_id in (('CR-ENERGY-DRAIN-AFTER-DAMAGE', 'DR5'), ('CR-ENERGY-DRAIN-EVEN-IF-KO', 'DR9'),
                               ('CR-ENERGY-DRAIN-CHOICE', 'DR11'), ('CR-ENERGY-DRAIN-BENCH', 'DR17')):
            self.assertEqual(rul[rid]['status'], 'CONFIRMED', rid)
            self.assertIn(engine_id, {e['ruling_id'] for e in rul[rid]['engine_refs']})
        for rid in ('CR-ENERGY-DRAIN-WHO-FLIPS', 'CR-ENERGY-DRAIN-WHO-CHOOSES', 'CR-ENERGY-DRAIN-RETURN-DAMAGE', 'CR-ENERGY-DRAIN-EVERY-TIME'):
            self.assertEqual(rul[rid]['status'], 'SUPPORTED', rid)
            self.assertTrue(rul[rid]['inference'], rid)

    def test_same_question_instances_are_not_new_issues(self):
        idx = {u['engine_key']: u for u in self.ctx['rulings']['engine_unresolved_index']}
        # v0.17 までの事例（あとの版の事例は v0.26〜v0.68 の取り込みで加えた）
        upto = lambda u: [i for i in u['instances'] if bcr.version_key(i['engine_version']) <= (0, 17)]
        self.assertEqual(upto(idx['C18']), [{'engine_version': 'v0.17', 'ruling_id': 'Z13'}])
        self.assertEqual(upto(idx['G37']), [{'engine_version': 'v0.17', 'ruling_id': 'Z22'}])
        self.assertEqual(idx['CHECK-SLEEP-COIN-ORDER']['kyuura_issue'], 'UQ-POKEMON-CHECK-SLEEP-COIN-ORDER')
        # わるいねぞうの同時のきぜつは、はんげきの論点（C18）と同じ論点で、ほのおのかべの論点（W24）とは別
        ca = self.issue('UQ-COUNTERATTACK-DOUBLE-KO')
        self.assertEqual({c['engine_ruling'] for c in ca['cases']}, {'C18', 'Z13'})

    def test_counts(self):
        # v0.17 の時点（あとの版で付いた停止コード・数えるようになった項目は as_of で除く）
        uc = bcr.unresolved_counts(self.ctx, as_of='v0.17')
        self.assertEqual(uc['engine_stop_codes'], 18)  # エンジンの停止コード（v0.17）
        self.assertEqual(uc['engine_total'], 24)  # エンジンの数え方の未解決の裁定（v0.17）
        issues = self.ctx['rulings']['issues']
        self.assertEqual(len({x['id'] for x in issues}), len(issues))


class V017BreakageTest(Base):
    """v0.17 の取り込みで加えた検査が、壊したデータを見つけること。"""

    def test_mapping_z23_to_a_confirmed_ruling_needs_a_reason(self):
        ctx = self.copy()
        rul = next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-COLLAPSE-ORDER')
        z23 = next(e for x in ctx['rulings']['issues'] if x['id'] == 'UQ-EFFECT-AFTER-NO-DAMAGE' for e in x['engine_refs'])
        rul['engine_refs'].append(dict(z23, part='ダメージを与えなかったとき'))
        rul['engine_refs'][0]['part'] = '要素の順番'
        self.assert_detected(ctx, 'reclassification')

    def test_stop_code_in_a_ruling_text_is_rejected(self):
        ctx = self.copy()
        issue = next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-EFFECT-AFTER-NO-DAMAGE')
        issue['why_unresolved'] += '（UNRESOLVED_EFFECT_AFTER_NO_DAMAGE）'
        self.assert_detected(ctx, 'UQ-EFFECT-AFTER-NO-DAMAGE')

    def test_instance_must_be_linked_to_the_issue(self):
        ctx = self.copy()
        issue = next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-COUNTERATTACK-DOUBLE-KO')
        issue['engine_refs'] = [e for e in issue['engine_refs'] if e['ruling_id'] != 'Z13']
        issue['cases'] = [c for c in issue['cases'] if c.get('engine_ruling') != 'Z13']
        self.assert_detected(ctx, 'C18 の事例 Z13（v0.17）が、論点 UQ-COUNTERATTACK-DOUBLE-KO の engine_refs にない')

    def test_engine_count_mismatch_is_detected(self):
        ctx = self.copy()
        u = next(x for x in ctx['rulings']['engine_unresolved_index'] if x['engine_key'] == 'DR1')
        u['in_engine_count'] = True  # エンジンが数えていない項目を数える
        self.assert_detected(ctx, 'v0.17 までの項目（エンジンが数えるもの）が 25 件')

    def test_duplicate_issue_for_z13_is_rejected(self):
        ctx = self.copy()
        dup = copy.deepcopy(next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-COUNTERATTACK-DOUBLE-KO'))
        dup['id'] = 'UQ-RESTLESS-SLEEP-DOUBLE-KO'
        dup['engine_refs'] = [e for e in dup['engine_refs'] if e['ruling_id'] == 'Z13']
        dup['cases'] = [c for c in dup['cases'] if c.get('engine_ruling') == 'Z13']
        ctx['rulings']['issues'].append(dup)
        self.assert_detected(ctx, '2 つ以上の未解決の論点')


class DataMismatchTest(Base):
    """エンジン v0.17 が報告したデータの食い違い（段階 F）。

    - ベロリンガ（PMCG2-041）: 『オフィシャルブック2000』p.234 [P43] の見出し・図版・「ワザ」欄で、ワザ 1 の名前（まきつくベロ）と
      レベル（26）を確かめ、カードのデータの生成の手順（data/curation/ja_text.json → scripts/build_cardlist.py）で直した。
      照合の記録 CC-PMCG2-041-P234 は、直したあとの値を写し、直す前の値を corrections に書く。
    - タケシのイワーク（PMCG5-048）: p.200 の見出しに収録が 2 行あるが、jp_print.series は空のまま（推測で埋めない）。
      空の原因（ポケモンWiki の保存データの set_name が空）を data_gaps に書く（CC-PMCG5-048-P200）。
    """

    def check(self, ctx, cid):
        return next(x for x in ctx['checks']['records'] if x['id'] == cid)

    def test_lickitung_is_corrected_with_the_previous_values_recorded(self):
        x = self.check(self.ctx, 'CC-PMCG2-041-P234')
        self.assertEqual((x['source'], x['page'], x['result']), ('P43', '234', 'no_difference'))
        self.assertEqual(x['checked_fields']['pokemon.attacks[0].name.ja'], 'まきつくベロ')
        self.assertEqual(x['checked_fields']['jp_print.level'], 26)
        before = {c['id']: c for c in base_json('data/cards.json')['cards']}['PMCG2-041']
        corr = {c['field']: c for c in x['corrections']}
        self.assertEqual(set(corr), {'pokemon.attacks[0].name.ja', 'jp_print.level'})
        self.assertEqual(corr['pokemon.attacks[0].name.ja']['before'], before['pokemon']['attacks'][0]['name']['ja'])
        self.assertEqual(corr['jp_print.level']['before'], before['jp_print']['level'])
        # 効果文・エネルギー・ダメージは直す前から同じ（ワザ名とレベルだけを直した）
        for f in ('text', 'cost', 'damage'):
            self.assertEqual(before['pokemon']['attacks'][0][f], self.ctx['cards']['PMCG2-041']['pokemon']['attacks'][0][f], f)
        self.assertTrue(all(c['commit'].startswith('f52a8e2') for c in x['corrections']))

    def test_onix_series_is_left_empty_as_an_open_gap(self):
        x = self.check(self.ctx, 'CC-PMCG5-048-P200')
        self.assertIsNone(self.ctx['cards']['PMCG5-048']['jp_print']['series'])
        self.assertNotIn('jp_print.series', x['checked_fields'])
        (gap,) = x['data_gaps']
        self.assertEqual((gap['field'], gap['kyuura_value'], gap['status']), ('jp_print.series', None, 'open'))
        self.assertIn('ポケモンジム第1弾タケシ', gap['source_value'])
        self.assertIn('Set name missing', gap['cause'])

    def test_the_gap_is_systemic_as_recorded(self):
        # data_gaps の cause に書いた数（series が空のカードは 50 枚。どれもポケモンWiki の保存データの set_name が空で warnings「Set name missing」）
        empty = sorted(cid for cid, c in self.ctx['cards'].items() if c.get('jp_print') and c['jp_print'].get('series') is None)
        self.assertEqual(len(empty), 50)
        self.assertIn('PMCG5-048', empty)
        raw = {}  # 出典のページ（jp_print.source）→ 保存データの記録
        for path in sorted((ROOT / 'data' / 'raw').glob('*.json')):
            for item in json.loads(path.read_text(encoding='utf-8')):
                raw.setdefault(item['card']['source_url'], []).append(item['card'])
        for cid in empty:
            (c,) = raw[self.ctx['cards'][cid]['jp_print']['source']]
            self.assertEqual(c['set_name'], '', cid)
            self.assertIn('Set name missing', c['warnings'], cid)
        self.assertEqual(sum(1 for lst in raw.values() for c in lst if not c.get('set_name')), 50)

    def test_filling_the_gap_requires_a_new_check(self):
        ctx = self.copy()
        ctx['cards']['PMCG5-048']['jp_print']['series'] = 'リーダーズスタジアム'
        self.assert_detected(ctx, 'data_gaps の欄 jp_print.series に値が入っている')

    def test_gap_field_is_not_a_checked_field(self):
        ctx = self.copy()
        self.check(ctx, 'CC-PMCG5-048-P200')['checked_fields']['jp_print.series'] = None
        self.assert_detected(ctx, 'data_gaps の欄 jp_print.series を checked_fields に入れない')

    def test_gap_needs_a_known_status_and_a_cause(self):
        ctx = self.copy()
        gap = self.check(ctx, 'CC-PMCG5-048-P200')['data_gaps'][0]
        gap['status'] = 'filled'
        del gap['cause']
        self.assert_detected(ctx, 'data_gaps の status の値が不正')
        self.assert_detected(ctx, 'data_gaps の cause がない')

    def test_correction_must_match_the_checked_value(self):
        ctx = self.copy()
        corr = self.check(ctx, 'CC-PMCG2-041-P234')['corrections'][0]
        corr['after'] = 'したでなめる'
        self.assert_detected(ctx, '直したあとの値が、照合した欄 pokemon.attacks[0].name.ja の写しと違う')

    def test_correction_needs_the_commit(self):
        ctx = self.copy()
        del self.check(ctx, 'CC-PMCG2-041-P234')['corrections'][1]['commit']
        self.assert_detected(ctx, 'corrections の commit')

    def test_reverting_the_data_is_detected(self):
        ctx = self.copy()
        ctx['cards']['PMCG2-041']['pokemon']['attacks'][0]['name']['ja'] = 'したでなめる'
        self.assert_detected(ctx, 'CC-PMCG2-041-P234: 照合した欄 pokemon.attacks[0].name.ja の写しが今の data/cards.json と違う')


class UnresolvedAuditTest(Base):
    """未解決の論点の監査（段階 G）: 論点ごとの audit と、未解決の数の区別。

    kyuura の調査の未解決（論点の数）と、エンジンの数え方（未解決の裁定・停止コード）を別の数として求める。
    22（v0.13 までのエンジンの数）を全体の数として固定しない。停止コードは公式の裁定ではないので、論点の文に書かない。
    """

    def issue(self, ctx, iid):
        return next(x for x in ctx['rulings']['issues'] if x['id'] == iid)

    def test_every_issue_is_audited(self):
        values = self.ctx['rulings']['game_effect_values']
        for x in self.ctx['rulings']['issues']:
            a = x['audit']
            self.assertIn(a['game_effect'], values, x['id'])
            for k in ('game_effect_note', 'resolution_needs', 'searched'):
                self.assertTrue(a[k], (x['id'], k))
            self.assertTrue(all(n['resolves'] is False for n in a['new_sources']), x['id'])

    def test_counts_are_kept_apart(self):
        # v0.25 の時点の数（v0.26〜v0.68 の取り込みの数は tests/test_non_pack_engine_v068.py）
        uc = bcr.unresolved_counts(self.ctx, as_of='v0.25')
        self.assertEqual(uc['research_issues'], 24)
        self.assertEqual((uc['engine_total'], uc['engine_stop_codes']), (28, 22))
        # v0.18（ENGINE-46A3E2E。2026-10-15 に取り込んだ。新しい未解決の裁定はない）も 24
        self.assertEqual([(v, n) for v, n in uc['by_import'] if bcr.version_key(v) <= (0, 18)],
                         [('v0.13', 22), ('v0.17', 24), ('v0.18', 24)])
        self.assertEqual(len(uc['v013_items']), 22)
        self.assertEqual(uc['v017_additions'], ['Z9', 'Z23'])
        self.assertEqual(uc['not_in_engine_count'], ['DR1', 'DR6', 'DR8', 'DR13'])
        self.assertEqual(sorted(r for _, v, r in uc['instances'] if v == 'v0.17'), ['DR18', 'Z13', 'Z18', 'Z22', 'Z29'])
        self.assertEqual(uc['issues_not_in_index'], ['UQ-PHOENIX-KO-PROCESS-ORDER'])
        self.assertNotEqual(uc['research_issues'], uc['engine_total'])

    def test_z9_result_and_ruling_are_separate(self):
        # Z9: 今のデータで結果が変わらないこと（わるいねぞうは無色、無色の弱点・抵抗力がない）と、裁定が決まらないことを分ける（p.245・p.138・p.321）
        a = self.issue(self.ctx, 'UQ-POWER-DAMAGE-WEAKNESS-RESISTANCE')['audit']
        self.assertEqual(a['game_effect'], 'game_result')
        self.assertIn('今のデータでは結果が変わらない', a['game_effect_note'])
        self.assertIn('裁定が決まったことではない', a['game_effect_note'])
        # v0.25 までは停止コードのない問い。エンジンは v0.61 で停止コードを付けた（裁定が決まったことではない）
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.25')['stop_codes_by_issue']['UQ-POWER-DAMAGE-WEAKNESS-RESISTANCE'], [])

    def test_z23_stop_code_is_only_in_the_index(self):
        # Z23 の停止コードは一覧（engine_unresolved_index）にだけあり、論点の文（question・why_unresolved・audit）にはない（p.245・p.155）
        x = self.issue(self.ctx, 'UQ-EFFECT-AFTER-NO-DAMAGE')
        self.assertEqual(bcr.unresolved_counts(self.ctx)['stop_codes_by_issue'][x['id']], ['UNRESOLVED_EFFECT_AFTER_NO_DAMAGE'])
        text = json.dumps({k: x[k] for k in ('question', 'why_unresolved', 'audit')}, ensure_ascii=False)
        self.assertNotIn('UNRESOLVED_', text)

    def test_coin_only_issues(self):
        # 盤面が変わらないとみられる（コインの有無・順番だけ）論点。どれも論点のまま（裁定にしない）
        rng = sorted(x['id'] for x in self.ctx['rulings']['issues'] if x['audit']['game_effect'] == 'rng_only')
        self.assertEqual(rng, ['UQ-COIN-IN-NULLIFIED-ELEMENT', 'UQ-ENERGY-DRAIN-NO-ENERGY',
                               'UQ-POKEMON-CHECK-SLEEP-COIN-ORDER', 'UQ-TRANSPARENCY-COIN-ORDER'])

    def test_missing_audit_is_detected(self):
        ctx = self.copy()
        del self.issue(ctx, 'UQ-ENERGY-DRAIN-TIMING')['audit']
        self.assert_detected(ctx, 'UQ-ENERGY-DRAIN-TIMING: audit')

    def test_bad_game_effect_is_detected(self):
        ctx = self.copy()
        self.issue(ctx, 'UQ-ENERGY-DRAIN-TIMING')['audit']['game_effect'] = 'none'
        self.assert_detected(ctx, 'game_effect の値が不正')

    def test_resolving_source_is_rejected(self):
        ctx = self.copy()
        self.issue(ctx, 'UQ-EFFECT-AFTER-NO-DAMAGE')['audit']['new_sources'][0]['resolves'] = True
        self.assert_detected(ctx, 'resolves は false')

    def test_new_source_must_be_in_sources(self):
        ctx = self.copy()
        self.issue(ctx, 'UQ-EFFECT-AFTER-NO-DAMAGE')['audit']['new_sources'].append(
            {'source': 'P43', 'page': '200', 'what': 'x', 'resolves': False})
        self.assert_detected(ctx, 'new_sources のページ p.200 が sources にない')

    def test_stop_code_in_resolution_needs_is_rejected(self):
        ctx = self.copy()
        self.issue(ctx, 'UQ-EFFECT-AFTER-NO-DAMAGE')['audit']['resolution_needs'] += '（UNRESOLVED_EFFECT_AFTER_NO_DAMAGE）'
        self.assert_detected(ctx, 'エンジンの停止コード')


if __name__ == '__main__':
    unittest.main()
