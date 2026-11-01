"""ひかるバンギラス（neo4-082）の利用者指定の記録への、v0.133 の完成・実装の確認の追記（2026-11-02 日本時間）の検査。

- 追記: docs/engine-user-shining-tyranitar.md の 7 章、docs/engine-user-specifications.md の 1 章の該当行と 8 章、
  docs/engine-handover-after-v0.124.md の 9 章。2026-11-01 の計画・未確認の記述（1〜6 章）は、過去の時点として残す。
- 確かめたエンジン: kyuura-engine v0.133、ブランチ claude/v0.133-shining-tyranitar、最終コミット 298f08d603c1f763fc45a97fc306291d8b95abb0、
  版の文書 docs/shining-tyranitar-v0.133.md（12 章が kyuura への報告事項）。固定コミットを読み取りだけで確かめた。テスト・対戦の
  結果はエンジンの報告で、kyuura は実行していない。
- 利用者の指定は公式の裁定・最新の説明・エラッタ・転記の訂正ではない。UQ-STATED-COUNT-SHORT・UQ-DESTRUCTIVE-FIRE-FAILURE などは未解決のまま。
  engine_positions・engine_imports には加えない。カードデータ・CSV・sidecar・目録・エンジンの対象・登録表の写しは変えない。
- 基点: 5dc08e8c66f79f8bbd6f8d908ed995cbdf82f63b（2026-11-01 の利用者指定の記録の最後のコミット）。
"""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = '5dc08e8c66f79f8bbd6f8d908ed995cbdf82f63b'  # この作業の基点（2026-11-01 の記録）
TYRANITAR = 'docs/engine-user-shining-tyranitar.md'
HUB = 'docs/engine-user-specifications.md'
HANDOVER = 'docs/engine-handover-after-v0.124.md'
ENGINE_COMMIT = '298f08d603c1f763fc45a97fc306291d8b95abb0'
ENGINE_BRANCH = 'claude/v0.133-shining-tyranitar'
ENGINE_DOC = 'docs/shining-tyranitar-v0.133.md'
UNCHANGED = [
    'data/cards.json', 'data/cards.csv', 'data/attacks.csv', 'data/powers.csv', 'data/engine_targets.json',
    'data/sidecar/rulings.json', 'data/sidecar/latest_descriptions.json', 'data/sidecar/card_checks.json',
    'data/curation/card_corrections.json', 'data/curation/card_image_checks.json', 'data/curation/engine_registered_cards.json',
    'data/curation/catalog_items.json', 'data/species_heights.json',
]
UNRESOLVED_KEPT = {
    'UQ-STATED-COUNT-SHORT', 'UQ-DESTRUCTIVE-FIRE-FAILURE', 'UQ-ESP-REDO', 'UQ-COIN-IN-NULLIFIED-ELEMENT',
    'UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY', 'UQ-SUPER-TRANSFORM-ENERGY-COLORS',
}
# エンジンの報告から引いた数（版の文書 10・11 章）。kyuura が実行した結果ではない
ENGINE_REPORT = ('247 モジュール・7,208 件', '**失敗 2**・エラー 0・スキップ 1', '3 モジュール・82 件', '7,209 件',
                 '**その状態で全体は再実行していません**', '290 対戦・48,092 歩・食い違い 0', '11 版・632 局、差 0',
                 '28 局・2,809 歩', '内部エラー 0・予期しない拒否 0・監査の失敗 0', 'UNRESOLVED_MULLIGAN_COMPENSATION')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def section(text, heading):
    level = len(heading) - len(heading.lstrip('#'))
    start = text.index(heading)
    rest = text[start + len(heading):]
    m = re.search(r'^#{1,%d} ' % level, rest, flags=re.M)
    return heading + (rest[:m.start()] if m else rest)


class EarlierTextKeptTest(unittest.TestCase):
    def test_plan_chapters_kept_and_progress_appended(self):
        """2026-11-01 の計画・未確認の記述は消さず、日付つきの経過を末尾に加えた（1〜6 章は基点と同じ）。"""
        for rel, heading in ((TYRANITAR, '## 7. 完成後の経過（2026-11-02 日本時間の追記。v0.133 の完成と実装の確認）'),
                             (HANDOVER, '## 9. 追記: v0.133 の完成と実装の確認（2026-11-02 日本時間）')):
            with self.subTest(rel=rel):
                before = git('show', f'{BASE}:{rel}').rstrip('\n')
                now = read(rel)
                self.assertTrue(now.startswith(before))
                self.assertIn(heading, now[len(before):])
        plan = section(read(TYRANITAR), '## 6. エンジンの実装の状態（2026-11-01 の時点）')
        self.assertIn('**計画だけで、実装は確かめていません。**', plan)
        self.assertIn('v0.133 のブランチ・コミットはありませんでした', plan)

    def test_hub_changes_only_the_row_and_new_section(self):
        """一覧は 1 章の該当行（今の状態）と 7 章の 1 文の注記と 8 章（追記）だけを変えた。"""
        before = git('show', f'{BASE}:{HUB}').splitlines()
        now = read(HUB).splitlines()
        changed = [line for line in now if line not in before]
        self.assertTrue(any('ひかるバンギラス neo4-082' in line and ENGINE_COMMIT[:7] in line for line in changed))
        removed = [line for line in before if line not in now]
        self.assertEqual(len(removed), 2, removed)  # 表の行と、7 章の「ひかるバンギラスは計画だけです」の行（注記を加えた）
        self.assertIn('## 8. ひかるバンギラスの完成後の経過（2026-11-02 日本時間の追記）', read(HUB))


class CompletionRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read(TYRANITAR)
        cls.progress = section(cls.doc, '## 7. 完成後の経過（2026-11-02 日本時間の追記。v0.133 の完成と実装の確認）')

    def test_engine_reference(self):
        for text in (ENGINE_COMMIT, ENGINE_BRANCH, ENGINE_DOC, '12 章'):
            self.assertIn(text, self.progress)
        self.assertIn(ENGINE_COMMIT, read(HUB))
        self.assertIn(ENGINE_COMMIT, read(HANDOVER))

    def test_code_and_document_separated(self):
        """コードで確かめた場所と、エンジンの報告（文書の記述）を分けて書く。"""
        code = section(self.progress, '### 7.2 コードで確かめた場所（`298f08d` の木）')
        for name in ('V0_133_ATTACKS', 'USER_SPECIFIED_RULES["neo4-082/attack/0"]', 'MillOpponentDeckUntilTailsUpTo',
                     'DiscardOpponentEnergyUpToHeads', 'typed_energy_card_usage_problem', 'user_specified_rule_problems',
                     'v133_problems', 'tests/test_shining_tyranitar_v0_133.py'):
            self.assertIn(name, code)
        report = section(self.progress, '### 7.4 エンジンの報告（kyuura は実行していない）')
        for text in ENGINE_REPORT:
            self.assertIn(text, report)
        self.assertIn('kyuura が実行した結果ではありません', report)
        self.assertIn('1 回目', report)  # 正式な対戦の 1 回目（内部エラー 1・監査の失敗 1）を隠さない

    def test_matches_spec_and_engine_additions_are_not_user_spec(self):
        table = section(self.progress, '### 7.3 指定と実装の照合')
        self.assertGreaterEqual(table.count('| 一致'), 10)
        self.assertIn('利用者の指定として kyuura に記録したものではない', table)
        self.assertIn('ワザを使ったプレイヤーが選ぶ', table)

    def test_esp_not_counted_as_real_path(self):
        limits = section(self.progress, '### 7.6 残る制限（実装の記録とは別に保持する）')
        self.assertIn('**ナツメのESPの経路は確認済みとしません。**', limits)
        self.assertIn('色マーカー', limits)
        for text in ('RB1', 'HC9', 'FC1', '途中停止からの再開', '山札の不足は 0 回', '単体のテストだけ'):
            self.assertIn(text, limits)

    def test_full_run_failures_from_diffs(self):
        failures = section(self.progress, '### 7.5 全体のテストの失敗 2 件（実際の差分で確かめた範囲）')
        self.assertIn('git diff f8565a1 0aa97c4', failures)
        self.assertIn('git diff 9f00943 298f08d -- tools/compat_driver.py', failures)
        self.assertIn('CRLF', failures)
        self.assertIn('**エンジンの報告**', failures)


class ResearchUnchangedTest(unittest.TestCase):
    def test_data_files_equal_base(self):
        for rel in UNCHANGED:
            with self.subTest(rel=rel):
                self.assertEqual((ROOT / rel).read_bytes(),
                                 subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{rel}'], capture_output=True, check=True).stdout)

    def test_issues_unresolved_and_no_import(self):
        r = json.loads(read('data/sidecar/rulings.json'))
        issues = {x['id']: x for x in r['issues']}
        for iid in UNRESOLVED_KEPT:
            self.assertEqual(issues[iid]['status'], 'UNRESOLVED', iid)
        self.assertNotIn('"neo4-082"', json.dumps(r['engine_positions'], ensure_ascii=False))
        self.assertNotIn('v0.133', {x.get('engine_version') for x in r['engine_imports']})
        self.assertNotIn(ENGINE_COMMIT, {x.get('commit') for x in r['engine_imports']})


if __name__ == '__main__':
    unittest.main()
