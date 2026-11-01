"""利用者がエンジン用に指定した仕様の記録（2026-11-01）の検査。

- 記録: docs/engine-user-specifications.md（一覧と、カツラのクイズ その1 GD5-016・ナッシー［Exeggutor］ PR1-075・PR1-077・
  ヤドキング neo1-049 の［ちえくらべ］）、docs/engine-user-shining-tyranitar.md（ひかるバンギラス neo4-082。v0.133 の計画）、
  docs/engine-user-swap-ownership.md の 8 章・docs/engine-user-promo-simplifications.md の 7 章（追記）。
- 利用者の指定は、公式の裁定・最新の説明・エラッタ・転記の訂正・画像の照合ではない。歴史的な未解決の論点は解決済みにしない。
  原文（印刷の文面・カード名の原表記・カードデータ）は変えない。engine_positions・engine_imports に加えない。
- 実装の確認は kyuura-engine の公開済みの固定コミット（v0.129 6673e7b・v0.130 f9a66ac・v0.131 f715dd5・v0.132 a6c0c95）を読んだ範囲。
  v0.133 は計画で、完成・動作は確かめていない。
- 基点: 9242b9be89be0f747279f39c11875d1ed61763ec（main。PR #8 のマージ）。カードの値・sidecar・目録・エンジンの対象は基点と同じであることを確かめる。
"""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = '9242b9be89be0f747279f39c11875d1ed61763ec'  # この作業の基点
# この作業でデータを変えていないことは、この作業の記録のコミットで比べる（あとの作業のデータの変更と分ける）
AT_COMMIT = 'cc0526f994cd1e8f7c98e9526a7d4d8381f25b8c'
HUB = 'docs/engine-user-specifications.md'
TYRANITAR = 'docs/engine-user-shining-tyranitar.md'
SWAP = 'docs/engine-user-swap-ownership.md'
PROMO = 'docs/engine-user-promo-simplifications.md'

# 利用者から完成報告のあった版（固定した公開のコミット）
COMPLETED = {
    'v0.129': ('6673e7bfd5a3e5bc0a3369b7725648b293b26099', 'docs/blaines-quiz-heights-v0.129.md'),
    'v0.130': ('f9a66acee37948ffdc764a44c3c66b369fc2001a', 'docs/trade-please-ownership-v0.130.md'),
    'v0.131': ('f715dd57abef80729ecf9ceb7bb796b3502e4ecd', 'docs/exeggutor-bilingual-names-v0.131.md'),
    'v0.132': ('a6c0c955fa66200f8677a87201b3726101383ec5', 'docs/slowking-mind-games-v0.132.md'),
}
# 指定に関わり、未解決のまま残す論点
UNRESOLVED_KEPT = {
    'UQ-STATED-COUNT-SHORT', 'UQ-DESTRUCTIVE-FIRE-FAILURE', 'UQ-ESP-REDO', 'UQ-COIN-IN-NULLIFIED-ELEMENT',
    'UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY', 'UQ-SUPER-TRANSFORM-ENERGY-COLORS', 'UQ-BILINGUAL-NAME-GLOSS',
    'UQ-SWAP-PLEASE-OWNERSHIP', 'UQ-CHAOS-GYM-BORROWED-TURN', 'UQ-MIND-GAMES-OPTIONAL', 'UQ-MIND-GAMES-TRAINER-STEP',
}
# 指定と同じ内容の既存の裁定（分類は基点のまま）
RULINGS_KEPT = {
    'CR-MOUNTAIN-CRUSH-PROCEDURE': 'CONFIRMED', 'CR-DESTRUCTIVE-FIRE-TEXT': 'CONFIRMED', 'CR-UNTIL-TAILS-NOT-CAPPED': 'SUPPORTED',
    'CR-MIND-GAMES-SCOPE': 'CONFIRMED', 'CR-MIND-GAMES-STADIUM-TOOL': 'CONFIRMED',
}
# この作業で変えないデータ（カード本体・CSV の印刷値・sidecar・目録・エンジンの対象集合・参照データ）
UNCHANGED = [
    'data/cards.json', 'data/cards.csv', 'data/attacks.csv', 'data/powers.csv', 'data/engine_targets.json',
    'data/sidecar/rulings.json', 'data/sidecar/latest_descriptions.json', 'data/sidecar/card_checks.json',
    'data/curation/card_corrections.json', 'data/curation/card_image_checks.json', 'data/curation/engine_registered_cards.json',
    'data/species_heights.json',
]
SPEC_IDS = ['neo4-082', 'GD5-016', 'PR1-027', 'PR1-075', 'PR1-077', 'neo1-049', 'PR1-044', 'PR1-090', 'PR1-072']


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def load(rel):
    return json.loads(read(rel))


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def section(text, heading):
    """見出し（## または ###）から、同じか上の段の次の見出しまで。"""
    level = len(heading) - len(heading.lstrip('#'))
    start = text.index(heading)
    rest = text[start + len(heading):]
    m = re.search(r'^#{1,%d} ' % level, rest, flags=re.M)
    return heading + (rest[:m.start()] if m else rest)


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = {c['id']: c for c in load('data/cards.json')['cards']}
        r = load('data/sidecar/rulings.json')
        cls.issues = {x['id']: x for x in r['issues']}
        cls.rulings = {x['id']: x for x in r['rulings']}
        cls.positions = r['engine_positions']
        cls.imports = r['engine_imports']
        cls.hub = read(HUB)
        cls.tyranitar = read(TYRANITAR)


class UnchangedDataTest(Data):
    def test_data_files_equal_base(self):
        """カード本体・CSV の印刷値・sidecar・目録・エンジンの対象集合・参照データは基点と同じ（利用者の指定のために書き換えない）。"""
        for rel in UNCHANGED:
            with self.subTest(rel=rel):
                at = [subprocess.run(['git', '-C', str(ROOT), 'show', f'{c}:{rel}'], capture_output=True, check=True).stdout
                      for c in (BASE, AT_COMMIT)]
                self.assertEqual(at[0], at[1])

    def test_cards_keep_original_names(self):
        """カード名の原表記は残る（ナッシー［Exeggutor］・ワザ名の併記）。今のデータで確かめる。"""
        for cid in ('PR1-075', 'PR1-077'):
            c = self.cards[cid]
            self.assertEqual(c['name']['ja'], 'ナッシー［Exeggutor］')
            self.assertEqual(c['pokemon']['evolves_from']['ja'], 'タマタマ')
            self.assertEqual(c['pokemon']['attacks'][0]['name']['ja'], 'ふみつけ[Stomp]')


class ResearchRecordsTest(Data):
    def test_issues_stay_unresolved(self):
        for iid in sorted(UNRESOLVED_KEPT):
            with self.subTest(issue=iid):
                self.assertIn(iid, self.issues)
                self.assertEqual(self.issues[iid]['status'], 'UNRESOLVED')

    def test_mind_games_issues_are_real(self):
        """ちえくらべの任意性・投げる時点の論点は、実在する 2 つの id（依頼で挙がった別名を作らない）。"""
        self.assertIn('UQ-MIND-GAMES-OPTIONAL', self.hub)
        self.assertIn('UQ-MIND-GAMES-TRAINER-STEP', self.hub)
        mind = sorted(i for i in self.issues if i.startswith('UQ-MIND-GAMES'))
        self.assertEqual(mind, ['UQ-MIND-GAMES-OPTIONAL', 'UQ-MIND-GAMES-TRAINER-STEP'])
        self.assertNotIn('UQ-SLOWKING', json.dumps(list(self.issues)))

    def test_rulings_keep_status(self):
        for rid, status in RULINGS_KEPT.items():
            with self.subTest(ruling=rid):
                self.assertEqual(self.rulings[rid]['status'], status)

    def test_no_engine_position_or_import_for_user_specs(self):
        """利用者の指定は engine_positions・engine_imports に入れていない（計画を取り込みとして記録しない。架空のコミットを作らない）。"""
        dumped = json.dumps(self.positions, ensure_ascii=False)
        for cid in ('neo4-082', 'GD5-016', 'PR1-027', 'PR1-075', 'PR1-077', 'neo1-049'):
            self.assertNotIn(f'"{cid}"', dumped)
        versions = {x.get('engine_version') for x in self.imports}
        for v in ('v0.127', 'v0.129', 'v0.130', 'v0.131', 'v0.132', 'v0.133'):
            self.assertNotIn(v, versions)
        commits = {x.get('commit') for x in self.imports}
        for commit, _ in COMPLETED.values():
            self.assertNotIn(commit, commits)


class QuotedTextTest(Data):
    def test_tyranitar_printed_text(self):
        """記録に引いた印刷の文面は kyuura の値と同じ。"""
        attacks = self.cards['neo4-082']['pokemon']['attacks']
        self.assertEqual([a['name']['ja'] for a in attacks], ['マウンテンクラッシュ', 'はかいのほのお'])
        for a in attacks:
            self.assertIn(a['text']['ja'], self.tyranitar)
        self.assertEqual([a['damage']['base'] for a in attacks], [30, 50])

    def test_quiz_printed_text(self):
        self.assertIn(self.cards['GD5-016']['trainer']['text']['ja'], self.hub)

    def test_card_ids_exist(self):
        for cid in SPEC_IDS:
            self.assertIn(cid, self.cards)

    def test_referenced_ids_exist(self):
        """記録が挙げる UQ-・CR-・IMG- の id は、kyuura の記録にある。"""
        image_checks = {x['id'] for x in load('data/curation/card_image_checks.json')['checks']}
        for rel in (HUB, TYRANITAR):
            text = read(rel)
            for iid in set(re.findall(r'\bUQ-[A-Z0-9-]*[A-Z0-9]', text)):
                self.assertIn(iid, self.issues, (rel, iid))
            for rid in set(re.findall(r'\bCR-[A-Z0-9-]*[A-Z0-9]', text)):
                self.assertIn(rid, self.rulings, (rel, rid))
            for img in set(re.findall(r'\bIMG-[A-Za-z0-9-]*[A-Za-z0-9]', text)):
                self.assertIn(img, image_checks, (rel, img))


class PlanVersusImplementationTest(Data):
    def test_tyranitar_is_plan_only(self):
        """2026-11-01 の記録の時点（AT_COMMIT）では、v0.133 は計画で、完成・動作の確認を記録しない。コミットのハッシュを書かない。
        2026-11-02 の完成後の経過（7 章）のあとも、この時点の記録は git の固定コミットで確かめる（期待は変えていない。今の記録は
        tests/test_shining_tyranitar_v0_133_record.py）。"""
        tyranitar = git('show', f'{AT_COMMIT}:{TYRANITAR}')
        hub = git('show', f'{AT_COMMIT}:{HUB}')
        status = section(tyranitar, '## 6. エンジンの実装の状態（2026-11-01 の時点）')
        self.assertIn('計画だけで、実装は確かめていません', status)
        self.assertIn('v0.133 のブランチ・コミットはありませんでした', status)
        self.assertNotRegex(tyranitar, r'v0\.133[^\n]{0,40}`[0-9a-f]{7,40}`')
        row = [line for line in section(hub, '## 1. 一覧').splitlines() if 'ひかるバンギラス' in line]
        self.assertEqual(len(row), 1)
        self.assertIn('計画', row[0])
        self.assertIn('未確認', row[0])

    def test_tyranitar_spec_differences_recorded(self):
        """原文との差（宣言の条件・ダメージより先のトラッシュ・不足の扱い）と適用範囲を書く。"""
        diff = section(self.tyranitar, '### 4.2 利用者の指定で決めたこと（原文・既存の記録では決まっていない）')
        for phrase in ('宣言の条件', 'p.309 の手順 6', '残りすべて', 'UQ-STATED-COUNT-SHORT', 'UQ-DESTRUCTIVE-FIRE-FAILURE'):
            self.assertIn(phrase, diff)
        self.assertIn('ほかの、数が足りなくなる効果', self.tyranitar)
        self.assertIn('英語版の文から持ちこんだものではなく', self.tyranitar)

    def test_completed_reports_are_full_hashes(self):
        """完成報告の参照は 40 桁のハッシュと文書。v0.132 の短縮 a6c0c95 は完全なハッシュに結ぶ。"""
        for version, (commit, doc) in COMPLETED.items():
            with self.subTest(version=version):
                self.assertRegex(commit, r'^[0-9a-f]{40}$')
                self.assertIn(doc, self.hub + read(SWAP))
                self.assertIn(commit, self.hub + read(SWAP))
        self.assertTrue(COMPLETED['v0.132'][0].startswith('a6c0c95'))

    def test_engine_results_marked_as_engine_reports(self):
        """テストの結果は、kyuura が再実行した結果として書かない。"""
        for heading in ('### 3.3 実装を確かめた範囲（v0.129）', '### 4.3 実装を確かめた範囲（v0.131）', '### 5.3 実装を確かめた範囲（v0.132）'):
            with self.subTest(heading=heading):
                self.assertIn('エンジンの報告（kyuura は再実行していない）', section(self.hub, heading))
        swap8 = section(read(SWAP), '## 8. 実装の経過（2026-11-01 の追記）')
        self.assertIn('エンジンの報告', swap8)
        self.assertIn('kyuura は再実行していません', swap8)


class EarlierRecordsKeptTest(unittest.TestCase):
    def test_earlier_chapters_unchanged(self):
        """2026-10-31 の記録（誕生日・発話の省略、所有者の簡略仕様）の既存の章は、追記のほかは基点と同じ。"""
        for rel, appended in ((PROMO, '\n\n## 7. その後の経過（2026-11-01 の追記）'), (SWAP, '\n\n## 8. 実装の経過（2026-11-01 の追記）')):
            with self.subTest(rel=rel):
                now = read(rel)
                before = git('show', f'{BASE}:{rel}')
                self.assertTrue(now.startswith(before.rstrip('\n')), rel)
                self.assertIn(appended, now[len(before.rstrip('\n')):])

    def test_promo_plan_status_kept(self):
        """誕生日・発話の省略は、v0.127 を独立に確かめたとは書かない。"""
        promo = read(PROMO)
        self.assertIn('**計画だけで、実装は確かめていません。**', promo)
        self.assertIn('v0.127 の実装を独立に確かめたとは記録しません', promo)


if __name__ == '__main__':
    unittest.main()
