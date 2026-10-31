"""kyuura-engine v0.122 のあとの調査（2026-10-30）の検査: 名前・文面のカードの画像の確認と、トレーナーの手順の整理。

- 優先A: ウィンディ（GD5-007・IP2-032・PR1-016）、ナッシー[Exeggutor]（PR1-075・PR1-077）、プクリン ES1-027 のふくらむを、同じ版のカードの画像
  （pcg-search.com [N3]・なぞのばしょ [N1]）で読んだ（data/curation/card_image_checks.json の IMG-）。比べた登録済みのカードのうち、
  ウィンディ PMCG1-019・カツラのウィンディ PMCG6-034 は、生成の値（種の名前の「ウインディ」）が印刷と違うので訂正した。
  公式ルール p.308（GR-2000-P308-SAME-NAME。文は既存の転記）で、印刷の名前がそろう 5 枚の同じ名前を確かめた（CR-ARCANINE-PRINTED-NAMES）。
- 優先B: ヤドキング neo1-049 のちえくらべ・フラッシュ ES2-035・とりかえっこプリーズ PR1-027 を、kyuura のカードの文面・既存の条項・
  既存の転記（『オフィシャルブック2000』p.293・p.312。kyuura は原典の画像を読んでいない）で整理した。決められない問いは論点にした。
- 基点: 2fe0bc0。kyuura-engine v0.122（e080c9e）は比べるためだけに読み、取り込んでいない（登録表の写しは v0.113 のまま）。
"""
import copy
import csv
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402
import build_cardlist  # noqa: E402

BASE = '2fe0bc042ce187d191843819262f8036abbb343d'  # この作業の基点
AT_COMMIT = '74b3ceb883dd815495d13b9987433fb14b36e44d'  # この作業の最後のコミット（あとの作業の訂正・記録と分けるため、この作業の差はこの時点で比べる）
# 画像の照合の記録 → （読んだ欄と値, 訂正）
IMAGES = {
    'IMG-GD5-007': ({'name.ja': 'カツラのウィンディ'}, []),
    'IMG-PMCG6-034': ({'name.ja': 'カツラのウィンディ'}, ['FIX-PMCG6-034-NAME-JA']),
    'IMG-PMCG1-019': ({'name.ja': 'ウィンディ'}, ['FIX-PMCG1-019-NAME-JA']),
    'IMG-IP2-032': ({'name.ja': 'ウィンディ'}, []),
    'IMG-PR1-016': ({'name.ja': 'ウィンディ'}, []),
    'IMG-PR1-077': ({'name.ja': 'ナッシー［Exeggutor］'}, []),
    'IMG-ES1-027': ({'pokemon.attacks[0].name.ja': 'ふくらむ'}, []),
}
FIXES = {'FIX-PMCG1-019-NAME-JA': ('PMCG1-019', 'ウインディ', 'ウィンディ'), 'FIX-PMCG6-034-NAME-JA': ('PMCG6-034', 'カツラのウインディ', 'カツラのウィンディ')}
TARGETS = ('GD5-007', 'IP2-032', 'PR1-016', 'PR1-075', 'PR1-077', 'ES1-027', 'neo1-049', 'ES2-035', 'PR1-027')  # v0.122 の未登録の 9 枚
INFLATE = 'このカードが次の相手に受けるダメージは「-10」される。'


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def at_base(rel, commit=BASE):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{rel}'], capture_output=True, text=True, check=True).stdout)


def at_commit(rel):
    """この作業のコミット（AT_COMMIT）の記録。あとの作業（2026-10-31 のすごいへんしん・わるいはどうの調査など）が値・記録を加えても、この作業の差を確かめる。"""
    return at_base(rel, AT_COMMIT)


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.fixes = {c['id']: c for c in cls.ledger['corrections']}
        cls.images = load('data/curation/card_image_checks.json')
        cls.checks = {x['id']: x for x in cls.images['checks']}


class CardValueTest(Data):
    """カード本体の値の変更は、登録済みの 2 枚の名前だけ。調べた 9 枚の値は変えていない。"""

    def test_only_two_names_changed(self):
        old = {c['id']: c for c in at_base('data/cards.json')['cards']}
        then = {c['id']: c for c in at_commit('data/cards.json')['cards']}  # この作業のコミットの値（あとの作業の訂正を混ぜない）
        self.assertEqual(set(old), set(self.by_id))
        self.assertEqual(set(then), set(self.by_id))
        self.assertEqual(len(self.cards), 1377)
        changed = {i for i in old if old[i] != then[i]}
        self.assertEqual(changed, {'PMCG1-019', 'PMCG6-034'})
        for fid, (cid, before, after) in FIXES.items():
            a, b = copy.deepcopy(old[cid]), copy.deepcopy(then[cid])
            self.assertEqual((a['name']['ja'], b['name']['ja']), (before, after))
            for r in (a, b):  # 名前・注記・訂正の記録のほかは同じ
                r['name']['ja'] = None
                r['notes'] = []
                r.pop('corrections', None)
            self.assertEqual(a, b, cid)
        for cid in TARGETS:
            self.assertEqual(self.by_id[cid], old[cid], cid)
        # 英語の併記は名前・ワザ名・進化元のどれも、転記の書き方のまま（正規化していない）
        for cid in ('PR1-075', 'PR1-077'):
            p = self.by_id[cid]
            self.assertEqual((self.by_id[cid]['name']['ja'], p['pokemon']['attacks'][0]['name']['ja'], p['pokemon']['evolves_from']['ja']),
                             ('ナッシー［Exeggutor］', 'ふみつけ[Stomp]', 'タマタマ'))
        self.assertEqual(self.by_id['ES1-027']['pokemon']['attacks'][0]['text']['ja'], INFLATE)  # 読めない字を補っていない

    def test_json_and_csv_agree(self):
        rows = {r['id']: r for r in csv.DictReader(io.StringIO((ROOT / 'data' / 'cards.csv').read_text(encoding='utf-8')))}
        self.assertEqual(set(rows), set(self.by_id))
        for cid in ('PMCG1-019', 'PMCG6-034', 'GD5-007', 'IP2-032', 'PR1-016', 'PR1-075', 'PR1-077'):
            self.assertEqual(rows[cid]['name_ja'], self.by_id[cid]['name']['ja'], cid)
            self.assertEqual(rows[cid]['corrections'].split(), [x['id'] for x in self.by_id[cid].get('corrections') or []], cid)


class ImageAndCorrectionTest(Data):
    """画像の照合の記録・訂正・生成した値が同じ内容を指す。訂正は生成のたびにかかり、before が今の値と違えば止まる。"""

    def test_records(self):
        then = {x['id'] for x in at_commit('data/curation/card_image_checks.json')['checks']}
        new = then - {x['id'] for x in at_base('data/curation/card_image_checks.json')['checks']}
        self.assertEqual(new, set(IMAGES))
        self.assertLessEqual(then, set(self.checks))  # あとの作業は記録を加えるだけ
        self.assertNotIn('IMG-PR1-075', self.checks)  # pcg-search の画像は「Dummy」の代わりの画像なので、印刷の確認にしない
        for iid, (values, fixes) in IMAGES.items():
            x = self.checks[iid]
            self.assertEqual((x['print_values'], x['corrections'], x['checked_on']), (values, fixes, '2026-10-30'), iid)
            for t in x['site_transcriptions']:
                self.assertNotIn('image_sha256', t)  # サイトの転記は画像の読み取りと分ける
            if len(x['images']) == 2:
                self.assertIn('独立した 2 枚の実物の照合とは数えない', x['independence'], iid)
            else:
                self.assertIn('1 枚だけ', x['independence'], iid)
        self.assertEqual([i['site'] for i in self.checks['IMG-PMCG1-019']['images']], ['pcg-search.com [N3]', 'なぞのばしょ [N1]'])

    def test_corrections_are_reapplied_and_checked(self):
        old_cands = {(c['card_id'], c['field']): c for c in at_base('data/curation/card_corrections.json')['candidates']}
        cands = {(c['card_id'], c['field']) for c in self.ledger['candidates']}
        for fid, (cid, before, after) in FIXES.items():
            c = self.fixes[fid]
            self.assertEqual((c['card_id'], c['field'], c['before'], c['after'], c['kind'], c['basis'], c['image_check'], c['card_checks_affected']),
                             (cid, 'name.ja', before, after, 'generated_value_error', 'card_image_check', f'IMG-{cid}', []), fid)
            self.assertEqual(c['previous_candidate'], old_cands[(cid, 'name.ja')])  # 前の候補をそのまま移した
            self.assertNotIn((cid, 'name.ja'), cands)
            rec = copy.deepcopy(self.by_id[cid])
            rec['name']['ja'] = before
            rec['notes'] = []
            rec.pop('corrections')
            build_cardlist.apply_corrections([rec], {'corrections': [c], 'candidates': []})
            self.assertEqual(rec['name']['ja'], after)
            again = copy.deepcopy(rec)  # すでに直っていれば before と合わずに止まる
            again.pop('corrections')
            with self.assertRaises(SystemExit):
                build_cardlist.apply_corrections([again], {'corrections': [c], 'candidates': []})
        # プクリンは訂正しない（読めない字がある）。候補として残す
        cand = next(c for c in self.ledger['candidates'] if c['card_id'] == 'ES1-027')
        self.assertEqual((cand['field'], cand['status'], cand['kyuura_value'], cand['image_check']),
                         ('pokemon.attacks[0].text.ja', 'held_illegible_print', INFLATE, 'IMG-ES1-027'))
        self.assertFalse([c for c in self.ledger['corrections'] if c['card_id'] in TARGETS and c['decided_on'] == '2026-10-30'])

    def test_broken_records_are_rejected(self):
        ok = ([copy.deepcopy(c) for c in self.cards], copy.deepcopy(self.images), copy.deepcopy(self.ledger))
        build_cardlist.check_image_checks(*ok)

        def img(doc, iid):
            return next(x for x in doc['checks'] if x['id'] == iid)

        def fix(led, fid):
            return next(c for c in led['corrections'] if c['id'] == fid)

        def rejected(change):
            recs, doc, led = copy.deepcopy(ok)
            change(recs, doc, led)
            with self.assertRaises(SystemExit):
                build_cardlist.check_image_checks(recs, doc, led)

        rejected(lambda r, d, l: next(c for c in r if c['id'] == 'PMCG1-019')['name'].update(ja='ウインディ'))  # 生成の値が印刷と違う
        rejected(lambda r, d, l: img(d, 'IMG-IP2-032')['print_values'].update({'name.ja': 'ウインディ'}))  # 種の名前にそろえる
        rejected(lambda r, d, l: fix(l, 'FIX-PMCG6-034-NAME-JA').update(image_check='IMG-GD5-007'))  # 別の版の画像
        rejected(lambda r, d, l: img(d, 'IMG-PMCG6-034').update(corrections=[]))  # 参照切れ（訂正が記録にない）
        rejected(lambda r, d, l: img(d, 'IMG-PR1-077')['print_values'].update({'name.ja': 'ナッシー'}))  # 併記を除く正規化
        rejected(lambda r, d, l: next(c for c in r if c['id'] == 'ES1-027')['pokemon']['attacks'][0]['name'].update(ja='ふくらむ[Inflate]'))


class RulingTest(unittest.TestCase):
    """裁定と論点: 原典で決まるものだけ CONFIRMED。既存の転記・エンジンの記録の条項を、kyuura の画像の確認にしない。"""

    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()
        r = cls.ctx['rulings']
        cls.rulings = {x['id']: x for x in r['rulings']}
        cls.issues = {x['id']: x for x in r['issues']}
        cls.base = at_base('data/sidecar/rulings.json')

    def test_new_records(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        new_r = set(self.rulings) - {x['id'] for x in self.base['rulings']}
        self.assertEqual({i: self.rulings[i]['status'] for i in new_r},
                         {'CR-ARCANINE-PRINTED-NAMES': 'CONFIRMED', 'CR-MIND-GAMES-SCOPE': 'CONFIRMED', 'CR-FLASH-PROCEDURE': 'CONFIRMED',
                          'CR-SWAP-PLEASE-PROCEDURE': 'CONFIRMED', 'CR-SWAP-PLEASE-USE-CONDITION': 'SUPPORTED'})
        new_i = set(self.issues) - {x['id'] for x in self.base['issues']}
        self.assertEqual(new_i, {'UQ-BILINGUAL-NAME-GLOSS', 'UQ-MIND-GAMES-OPTIONAL', 'UQ-MIND-GAMES-TRAINER-STEP', 'UQ-FLASH-FACE-UP-DECK',
                                 'UQ-SWAP-PLEASE-OWNERSHIP'})
        for i in new_i:
            q = self.issues[i]
            self.assertEqual((q['status'], q['engine_refs'], q['recorded_after']), ('UNRESOLVED', [], {'import': 'ENGINE-2D113B5', 'date': '2026-10-30'}), i)
        # 印刷の名前がそろう 5 枚: ウィンディ 3 枚・カツラのウィンディ 2 枚
        cards = {c['card_id'] for c in self.rulings['CR-ARCANINE-PRINTED-NAMES']['cards']}
        names = {c: self.ctx['cards'][c]['name']['ja'] for c in cards}
        self.assertEqual(sorted(names.values()), ['ウィンディ'] * 3 + ['カツラのウィンディ'] * 2)
        # 既存の論点には事例と注記を追記しただけ（問い・分類・監査は変えない）
        for i, cid in (('UQ-STATED-COUNT-SHORT', 'ES2-035'), ('UQ-CHAOS-GYM-BORROWED-TURN', 'PR1-027')):
            old = next(x for x in self.base['issues'] if x['id'] == i)
            self.assertEqual({k: v for k, v in self.issues[i].items() if k not in ('cases', 'notes')}, {k: v for k, v in old.items() if k not in ('cases', 'notes')})
            for k in ('cases', 'notes'):
                self.assertEqual(self.issues[i][k][:len(old[k])], old[k], i)
            self.assertEqual([c['card_id'] for c in self.issues[i]['cases'][len(old['cases']):]], [cid])
        now = {x['id']: x for k in ('issues', 'rulings', 'rule_clauses') for x in self.ctx['rulings'][k]}
        changed = [x['id'] for k in ('issues', 'rulings', 'rule_clauses') for x in self.base[k] if x != now[x['id']]]
        self.assertEqual(sorted(changed), ['UQ-CHAOS-GYM-BORROWED-TURN', 'UQ-STATED-COUNT-SHORT'])  # ほかの既存の記録は書きかえていない

    def test_transcription_is_not_raised_to_image(self):
        # p.293・p.308・p.312 の文は既存の転記。p.310 はエンジンの記録の条項
        for i in ('CR-ARCANINE-PRINTED-NAMES',):
            self.assertTrue(all(b['checked'] in ('kyuura_data', 'existing_transcription') for b in self.rulings[i]['basis']))
        b310 = [b for b in self.rulings['CR-SWAP-PLEASE-USE-CONDITION']['basis'] if b.get('page') == '310']
        self.assertEqual([b['checked'] for b in b310], ['engine_report'])
        src = self.issues['UQ-SWAP-PLEASE-OWNERSHIP']['sources']
        self.assertIsNone(src[0]['page'])  # p.293 のページの記録はない（原典を読んでいない）
        ctx = copy.deepcopy(self.ctx)
        b = next(b for b in next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-ARCANINE-PRINTED-NAMES')['basis'] if b.get('transcription'))
        b['transcription']['quote'] = b['transcription']['quote'].replace('別の', '同じ')
        self.assertTrue(any('転記の PDF' in e for e in bcr.validate(ctx)))
        ctx = copy.deepcopy(self.ctx)  # 推論を含む記録を CONFIRMED にしない
        next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-SWAP-PLEASE-USE-CONDITION')['status'] = 'CONFIRMED'
        self.assertTrue(any('CR-SWAP-PLEASE-USE-CONDITION' in e and 'inference' in e for e in bcr.validate(ctx)))
        ctx = copy.deepcopy(self.ctx)  # ページの記録のない原典のページを、読んだページとして書かない
        next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-SWAP-PLEASE-OWNERSHIP')['sources'][0]['page'] = '293'
        self.assertTrue(any('p.293' in e for e in bcr.validate(ctx)))

    def test_counts(self):
        # この作業のコミットの時点の数（あとの作業の記録を数えない。期待値は変えていない）
        then = dict(self.ctx, rulings=at_commit('data/sidecar/rulings.json'), latest=at_commit('data/sidecar/latest_descriptions.json'),
                    checks=at_commit('data/sidecar/card_checks.json'))
        r, latest, checks = then['rulings'], then['latest']['records'], then['checks']['records']
        self.assertEqual((len(latest), len(checks), len(r['rule_clauses']), len(r['rulings']), len(r['issues'])), (47, 84, 35, 320, 79))
        self.assertEqual(bcr.unresolved_counts(then)['research_issues'], 79)
        self.assertEqual(bcr.unresolved_counts(then, as_of='v0.113')['research_issues'], 72)  # 取り込んだ版の時点の数は変わらない
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.113')['research_issues'], 72)  # 今の記録でも、取り込んだ版の時点の数は同じ
        self.assertNotIn('v0.122', {i['engine_version'] for i in r['engine_imports']})  # v0.122 は取り込んでいない


class RegistryTest(Data):
    """登録表の写し（v0.113）は変えない。実装の対象の一覧で変わるのは、名前を直した 2 枚と、PMCG6-034 と同じになった GD5-007 だけ。"""

    def test_snapshot_and_targets(self):
        self.assertEqual(load('data/curation/engine_registered_cards.json'), at_base('data/curation/engine_registered_cards.json'))
        rows = {r['id']: r for r in at_commit('data/engine_targets.json')['cards']}  # この作業のコミットの一覧（あとの作業の文面の訂正を混ぜない）
        old = {r['id']: r for r in at_base('data/engine_targets.json')['cards']}
        self.assertEqual({i for i in rows if rows[i] != old[i]}, {'PMCG1-019', 'PMCG6-034', 'GD5-007'})
        self.assertEqual(sum(r['engine_status'] == 'registered' for r in rows.values()), 1250)
        self.assertEqual((old['GD5-007']['engine_status'], rows['GD5-007']['engine_status'], rows['GD5-007']['equivalent_to']),
                         ('reuse_candidate', 'mechanically_equivalent', ['PMCG6-034']))
        for cid in ('PMCG1-019', 'PMCG6-034'):
            self.assertEqual((rows[cid]['engine_status'], rows[cid]['name_ja']), ('registered', self.by_id[cid]['name']['ja']))


if __name__ == '__main__':
    unittest.main()
