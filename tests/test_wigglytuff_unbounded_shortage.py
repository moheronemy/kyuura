"""プクリンの最新の説明・コインで決まる枚数の不足の調査（2026-10-31）の検査。

- 原典: 『ポケモンカードオフィシャルブック2000』[P43] p.226（PDF 228）の拡張シート第1弾青版のプクリン（［てだすけ］・ふくらむの最新の説明・図版・解説）、
  p.82（PDF 84）の拡張シート第2弾赤版・クイックスターターギフトパックのファイヤー（ドライアップ）、p.195・p.66 の解説、p.309・p.312・p.323 の一般の規定を、
  スキャン [J38] の画像で読んだ（kyuura_image）。
- カードの画像（pcg-search.com [N3]）で、ファイヤー 2 枚（ES2-005・QSG-055。別々の画像）・ひかるバンギラス neo4-082・怪電波マシーン neo4-108 の文面を読んだ（訂正なし）。
  英語版の「少なければ全て」の文は日本語の印刷にない。プクリン ES1-027 の新しい画像は見つからない（同じ画像は新しい確認に数えない）。
- 基点: b9e7cff。kyuura-engine v0.124（e165fe0）は比べるためだけに読み、取り込んでいない（登録表の写しは v0.113 のまま）。
"""
import atexit
import copy
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402

BASE = 'b9e7cff6d2b2c6b4539ec45e61bf453879adab3a'  # この作業の基点
# この作業の最後のコミット。同じ日のあとの作業（ちえくらべ・フラッシュ・とりかえっこプリーズの調査。PR1-027 の読点の訂正・新しい記録）を
# 混ぜないよう、この作業の差はこの時点の木で比べる（期待値は変えていない）
AT_COMMIT = '134a664c6adf67d5604148a31b58e1a7d26d4d6d'
TARGETS = ('ES1-027', 'neo4-082', 'neo4-108', 'ES2-005', 'QSG-055')
INFLATE_KYUURA = 'このカードが次の相手に受けるダメージは「-10」される。'  # 転記（「の」と漢字 1 字が欠けている。候補のまま）
INFLATE_LD = '次の相手の番、このカードが受けるダメージは「-10」される。（ダメージ以外の効果はそのまま）'
HELP_LD = 'この力は、自分の番ごとに1回、このカードがベンチにいるとき使える。コインを投げて「おもて」なら、自分の対戦ポケモンの「どく・ねむり・マヒ・こんらん」状態のうちの1つを回復させる。'
DRY_LD = '相手の場にいるポケモンを1匹選ぶ。その後、「うら」が出るまでコインを投げ続け、「おもて」の数ぶんの「水」エネルギーカードを、そのポケモンからトラッシュする。'
NEW_IMAGES = {'IMG-ES2-005', 'IMG-QSG-055', 'IMG-neo4-082', 'IMG-neo4-108'}
NEW_LD = {'LD-ES1-027-PWR0', 'LD-ES1-027-ATK0', 'LD-ES2-005-ATK0', 'LD-QSG-055-ATK0'}
NEW_CC = {'CC-ES1-027-P226', 'CC-ES2-005-P82', 'CC-QSG-055-P82'}
NEW_RULINGS = {
    'CR-HELPING-HAND-USE': 'CONFIRMED', 'CR-INFLATE-LATEST': 'CONFIRMED', 'CR-INFLATE-DAMAGE-STEP': 'SUPPORTED',
    'CR-DRY-UP-PROCEDURE': 'CONFIRMED', 'CR-MOUNTAIN-CRUSH-PROCEDURE': 'CONFIRMED', 'CR-THOUGHT-WAVE-MACHINE-PROCEDURE': 'CONFIRMED',
    'CR-DESTRUCTIVE-FIRE-TEXT': 'CONFIRMED', 'CR-UNTIL-TAILS-NOT-CAPPED': 'SUPPORTED',
}
NEW_ISSUES = {'UQ-DESTRUCTIVE-FIRE-FAILURE', 'UQ-HELPING-HAND-CHOICE'}
CASE_ADDED = {  # 既存の論点 → 加えた事例の数（問い・分類・監査は変えない）
    'UQ-STATED-COUNT-SHORT': 5, 'UQ-CARD-USE-WITHOUT-TARGET': 2, 'UQ-NON-ATTACK-DAMAGE-MODIFIERS': 1, 'UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY': 1,
}
NOTED_CLAUSES = {'GR-2000-P312-DECK-HAND-DISCARD', 'GR-2000-P323-ATTACK-FAILURE'}


def load(rel):
    """この作業のコミット（AT_COMMIT）の値。"""
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{AT_COMMIT}:{rel}'], capture_output=True, text=True, check=True).stdout)


_TREE = None


def commit_tree():
    """AT_COMMIT の木を一時ディレクトリに展開する（build_card_rulings.load はファイルの木を読むため）。"""
    global _TREE
    if _TREE is None:
        tmp = tempfile.TemporaryDirectory()
        atexit.register(tmp.cleanup)
        data = subprocess.run(['git', '-C', str(ROOT), 'archive', AT_COMMIT], capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(data)) as tar:
            tar.extractall(tmp.name, filter='data')
        _TREE = (tmp, Path(tmp.name))
    return _TREE[1]


def at_base(rel):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{rel}'], capture_output=True, text=True, check=True).stdout)


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.checks = {x['id']: x for x in load('data/curation/card_image_checks.json')['checks']}
        cls.ctx = bcr.load(commit_tree())  # この作業のコミットの記録
        cls.latest = {x['id']: x for x in cls.ctx['latest']['records']}
        cls.cc = {x['id']: x for x in cls.ctx['checks']['records']}
        r = cls.ctx['rulings']
        cls.clauses = {x['id']: x for x in r['rule_clauses']}
        cls.rulings = {x['id']: x for x in r['rulings']}
        cls.issues = {x['id']: x for x in r['issues']}


class CardValueTest(Data):
    """カードの値は変えていない（1,377 枚・id の集合・全欄が基点と同じ）。プクリンの読めない 1 字を補っていない。"""

    def test_no_card_value_changed(self):
        old = {c['id']: c for c in at_base('data/cards.json')['cards']}
        self.assertEqual(len(self.cards), 1377)
        self.assertEqual(set(old), set(self.by_id))
        self.assertEqual([i for i in old if old[i] != self.by_id[i]], [])
        self.assertEqual(self.ledger['corrections'], at_base('data/curation/card_corrections.json')['corrections'])  # 訂正は加えていない

    def test_inflate_print_is_not_filled_from_latest_description(self):
        self.assertEqual(self.by_id['ES1-027']['pokemon']['attacks'][0]['text']['ja'], INFLATE_KYUURA)
        cand = [c for c in self.ledger['candidates'] if c['card_id'] == 'ES1-027']
        self.assertEqual(len(cand), 1)
        self.assertEqual((cand[0]['field'], cand[0]['status']), ('pokemon.attacks[0].text.ja', 'held_illegible_print'))
        old = next(c for c in at_base('data/curation/card_corrections.json')['candidates'] if c['card_id'] == 'ES1-027')
        self.assertEqual({k: v for k, v in cand[0].items() if k != 'later_notes'}, old)  # 過去の候補の文は書きかえない
        self.assertEqual([n['date'] for n in cand[0]['later_notes']], ['2026-10-31'])
        for text in (json.dumps(self.by_id['ES1-027'], ensure_ascii=False), json.dumps(self.checks['IMG-ES1-027'], ensure_ascii=False)):
            self.assertNotIn('相手の番に受ける', text)  # 「番」を推測で埋めていない

    def test_english_only_sentences_are_not_added(self):
        for cid, path in (('neo4-108', ('trainer',)), ('neo4-082', ('pokemon', 'attacks', 1))):
            x = self.by_id[cid]
            for k in path:
                x = x[k]
            self.assertNotIn('少な', x['text']['ja'], cid)
            self.assertNotIn('全て', x['text']['ja'], cid)
            self.assertIn('fewer', x['text']['en'], cid)  # 英語版にだけある文


class ImageCheckTest(Data):
    """カードの画像の照合: 4 枚の新しい記録。同じカードの組の 2 枚は別々の画像で読み、片方を他方の記録にしない。"""

    def test_new_records(self):
        new = set(self.checks) - {x['id'] for x in at_base('data/curation/card_image_checks.json')['checks']}
        self.assertEqual(new, NEW_IMAGES)
        for iid in new:
            x = self.checks[iid]
            self.assertEqual((x['checked_on'], [i['site'] for i in x['images']], x['corrections']), ('2026-10-31', ['pcg-search.com [N3]'], []), iid)
            for t in x['site_transcriptions']:
                self.assertNotIn('image_sha256', t)  # サイトの転記は画像の読み取りと分ける
        self.assertEqual(self.checks['IMG-ES1-027'], next(x for x in at_base('data/curation/card_image_checks.json')['checks'] if x['id'] == 'IMG-ES1-027'))

    def test_same_card_group_images_are_separate(self):
        a, b = self.checks['IMG-ES2-005'], self.checks['IMG-QSG-055']
        self.assertEqual(self.by_id['ES2-005']['same_card_group'], self.by_id['QSG-055']['same_card_group'])
        self.assertNotEqual(a['images'][0]['image_sha256'], b['images'][0]['image_sha256'])
        self.assertNotEqual(a['images'][0]['image_url'], b['images'][0]['image_url'])
        self.assertEqual((a['card_id'], b['card_id']), ('ES2-005', 'QSG-055'))

    def test_english_sentence_absence_is_recorded(self):
        for iid in ('IMG-neo4-082', 'IMG-neo4-108'):
            self.assertIn('日本語の印刷にない', json.dumps(self.checks[iid]['print_text'], ensure_ascii=False), iid)


class SourceReadingTest(Data):
    """原典の読み取り: p.226（プクリン）・p.82（ファイヤー）。最新の説明は印刷の文面と分け、図版で特定していない印刷に図版の照合を数えない。"""

    def test_latest_descriptions(self):
        self.assertEqual(set(self.latest) - {x['id'] for x in at_base('data/sidecar/latest_descriptions.json')['records']}, NEW_LD)
        self.assertEqual(self.latest['LD-ES1-027-PWR0']['latest_description']['text_ja'], HELP_LD)
        self.assertEqual(self.latest['LD-ES1-027-ATK0']['latest_description']['text_ja'], INFLATE_LD)
        for i in ('LD-ES1-027-PWR0', 'LD-ES1-027-ATK0'):
            ld = self.latest[i]
            self.assertEqual((ld['latest_description']['page'], ld['latest_description']['pdf_page'], ld['applies_to_print']['by']), ('226', 228, 'figure'), i)
            self.assertEqual({v['by'] for v in ld['verification']}, {'kyuura'}, i)
            self.assertNotIn('import_provenance', ld, i)
        pt = self.latest['LD-ES1-027-ATK0']['printed_text']
        self.assertEqual((pt['text_ja'], pt['image_check']), (INFLATE_KYUURA, 'different_text'))  # 印刷の欄は転記のまま
        self.assertIn('■', pt['image_text_ja'])  # 図版でも読めない字は読めないまま
        for cid in ('ES2-005', 'QSG-055'):
            ld = self.latest[f'LD-{cid}-ATK0']
            self.assertEqual(ld['latest_description']['text_ja'], DRY_LD)
            self.assertEqual((ld['latest_description']['page'], ld['applies_to_print']['by'], ld['printed_text']['image_check']), ('82', 'heading_listing', 'not_checked'), cid)

    def test_card_checks(self):
        self.assertEqual(set(self.cc) - {x['id'] for x in at_base('data/sidecar/card_checks.json')['records']}, NEW_CC)
        x = self.cc['CC-ES1-027-P226']
        self.assertEqual(x['result'], 'data_error')
        self.assertEqual([(e['field'], e['fix_status']) for e in x['data_error']], [('pokemon.attacks[0].text.ja', 'candidate')])
        self.assertEqual([g['field'] for g in x['data_gaps']], ['jp_print.level'])  # レベルは埋めていない
        for cid in ('ES2-005', 'QSG-055'):
            y = self.cc[f'CC-{cid}-P82']
            self.assertNotIn('pokemon.attacks[0].text.ja', y['checked_fields'], cid)  # 版を特定していない図版の文面をこの印刷の照合にしない
            self.assertEqual(y['result'], 'printed_vs_latest_only', cid)

    def test_heading_listing_cannot_claim_figure(self):
        ctx = copy.deepcopy(self.ctx)
        ld = next(x for x in ctx['latest']['records'] if x['id'] == 'LD-QSG-055-ATK0')
        ld['applies_to_print']['by'] = 'figure'
        self.assertTrue(any('LD-QSG-055-ATK0' in e and 'figure' in e for e in bcr.validate(ctx)))

    def test_page_records(self):
        doc = next(y for y in self.ctx['rule_history']['documents'] if y['code'] == 'P43')
        pages = {str(p['printed']): p for p in doc['pages']}
        self.assertEqual((pages['226']['pdf'], pages['195']['pdf']), (228, 197))
        self.assertLessEqual({'LD-ES1-027-PWR0', 'LD-ES1-027-ATK0', 'CC-ES1-027-P226'}, set(pages['226']['refs']))
        self.assertLessEqual({'LD-ES2-005-ATK0', 'LD-QSG-055-ATK0', 'CC-PMCG5-020-P82'}, set(pages['82']['refs']))  # 既存の参照を残した
        # p.312 の条項はエンジンの記録の取り込みのまま（読み直しは注記だけ。確かめ方の値を上げていない）
        old = {x['id']: x for x in at_base('data/sidecar/rulings.json')['rule_clauses']}
        for cid in NOTED_CLAUSES:
            self.assertEqual({k: v for k, v in self.clauses[cid].items() if k != 'notes'}, {k: v for k, v in old[cid].items() if k != 'notes'}, cid)
            self.assertEqual(self.clauses[cid]['notes'][:len(old[cid].get('notes', []))], old[cid].get('notes', []), cid)


class RulingTest(Data):
    """裁定と論点: 文面・最新の説明で決まるものだけ CONFIRMED。不足の問いは未解決のまま、事例を加えただけ。"""

    def test_new_records(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        base = at_base('data/sidecar/rulings.json')
        new_r = set(self.rulings) - {x['id'] for x in base['rulings']}
        self.assertEqual({i: self.rulings[i]['status'] for i in new_r}, NEW_RULINGS)
        for i, st in NEW_RULINGS.items():
            self.assertEqual(bool(self.rulings[i]['inference']), st == 'SUPPORTED', i)
            self.assertEqual(self.rulings[i]['engine_refs'], [], i)
        new_i = set(self.issues) - {x['id'] for x in base['issues']}
        self.assertEqual(new_i, NEW_ISSUES)
        for i in new_i:
            q = self.issues[i]
            self.assertEqual((q['status'], q['engine_refs'], q['recorded_after'], q['not_in_engine_index']),
                             ('UNRESOLVED', [], {'import': 'ENGINE-2D113B5', 'date': '2026-10-31'}, True), i)

    def test_existing_issues_only_gain_cases_and_notes(self):
        base = at_base('data/sidecar/rulings.json')
        now = {x['id']: x for k in ('issues', 'rulings', 'rule_clauses') for x in self.ctx['rulings'][k]}
        changed = {x['id'] for k in ('issues', 'rulings', 'rule_clauses') for x in base[k] if x != now[x['id']]}
        self.assertEqual(changed, set(CASE_ADDED) | NOTED_CLAUSES)
        for i, n in CASE_ADDED.items():
            old, cur = next(x for x in base['issues'] if x['id'] == i), self.issues[i]
            for k in ('question', 'why_unresolved', 'status', 'official_material', 'audit', 'engine_refs', 'reachability'):
                self.assertEqual(cur.get(k), old.get(k), (i, k))  # 問い・分類・過去の監査は変えない
            self.assertEqual(cur['cases'][:len(old['cases'])], old['cases'], i)
            self.assertEqual(len(cur['cases']) - len(old['cases']), n, i)
            self.assertEqual(cur['notes'][:len(old.get('notes', []))], old.get('notes', []), i)
            self.assertTrue(cur['notes'][-1].startswith('2026-10-31'), i)

    def test_shortage_cases_cover_the_four_cards(self):
        q = self.issues['UQ-STATED-COUNT-SHORT']
        self.assertEqual(q['status'], 'UNRESOLVED')
        added = {(c['card_id'], c['target'].get('index')) for c in q['cases'][-5:]}
        self.assertEqual(added, {('neo4-082', 0), ('neo4-082', 1), ('neo4-108', None), ('ES2-005', 0), ('QSG-055', 0)})

    def test_coin_flipping_is_not_capped_by_resources(self):
        r = self.rulings['CR-UNTIL-TAILS-NOT-CAPPED']
        self.assertEqual(r['status'], 'SUPPORTED')  # 公式の資料に直接の文はないので CONFIRMED にしない
        self.assertIn('やめない', r['conclusion'])
        self.assertIn('UQ-STATED-COUNT-SHORT', r['conclusion'])  # 足りないときの処理は決めない

    def test_destructive_fire_zero_heads_is_open(self):
        q = self.issues['UQ-DESTRUCTIVE-FIRE-FAILURE']
        notes = ' '.join(c['note'] for c in q['cases'])
        for key in ('H = 0', 'N = 0', '順番', 'ダメージを受けない'):
            self.assertIn(key, notes)
        self.assertNotIn('CR-DESTRUCTIVE-FIRE-ZERO', ' '.join(self.rulings))  # H = 0 の答えを裁定にしていない

    def test_latest_description_basis_is_image(self):
        for i in ('CR-HELPING-HAND-USE', 'CR-INFLATE-LATEST', 'CR-DRY-UP-PROCEDURE'):
            pages = {(b.get('page'), b.get('checked')) for b in self.rulings[i]['basis'] if b.get('source') == 'P43'}
            self.assertTrue(pages <= {('226', 'kyuura_image'), ('82', 'kyuura_image'), ('6', 'kyuura_image')}, i)

    def test_counts(self):
        r, latest, checks = self.ctx['rulings'], self.ctx['latest']['records'], self.ctx['checks']['records']
        self.assertEqual((len(latest), len(checks), len(r['rule_clauses']), len(r['rulings']), len(r['issues'])), (52, 88, 41, 345, 90))
        self.assertEqual(bcr.unresolved_counts(self.ctx)['research_issues'], 90)
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.113')['research_issues'], 72)  # 取り込んだ版の時点の数は変わらない
        self.assertFalse({'v0.118', 'v0.124'} & {i['engine_version'] for i in r['engine_imports']})  # 取り込んでいない


class RegistryTest(Data):
    """登録表の写し（v0.113）・実装の対象の一覧は変えない。5 つの id は未登録のまま。"""

    def test_snapshot_and_targets(self):
        self.assertEqual(load('data/curation/engine_registered_cards.json'), at_base('data/curation/engine_registered_cards.json'))
        rows = {r['id']: r for r in load('data/engine_targets.json')['cards']}
        self.assertEqual(rows, {r['id']: r for r in at_base('data/engine_targets.json')['cards']})
        for cid in TARGETS:
            self.assertNotEqual(rows[cid]['engine_status'], 'registered', cid)


if __name__ == '__main__':
    unittest.main()
