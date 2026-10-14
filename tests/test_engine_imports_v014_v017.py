"""kyuura-engine v0.13〜v0.17 の取り込みの整合と、破壊テスト。

- v0.13 の取り込み（ENGINE-8FACF3A。わるいカメールの S1〜S49）は作り直さず、そのまま保つ。
- v0.14〜v0.16 は実装の履歴（イベントの仕組み・先読み・旧経路の撤去）で、裁定の表がない。読んだ文書と、ルールに関わる記述の
  注記だけを持つ（no_ruling_tables）。エンジンの実装の判断を公式の裁定として加えない。
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


if __name__ == '__main__':
    unittest.main()
