"""ベイビィポケモン 13 枚の準備と kyuura-engine v0.113（2d113b5）の報告事項の検査（2026-10-27）。

- カードのデータ: 13 枚の日本語版のカードの画像（pcg-search.com [N3]・なぞのばしょ [N1]）で、ルール文と進化先の欄を読んだ（data/curation/card_image_checks.json の IMG-）。
  ルール文の欠けた 6 枚は訂正の記録（data/curation/card_corrections.json）で埋め、進化先は新しい欄 pokemon.evolves_to（日本語名の配列。未確認は null）に入れた。
  公式の書籍のページとの照合（CC-）・最新の説明（LD-）ではない。
- ルール: 公式ルール 2000.02.14 版（『オフィシャルブック2000』[P43]）p.308・p.309・p.310・p.313〜p.315・p.323〜p.325。kyuura の既存の読み取り（2026-10-12）と、
  既存の転記 data/Silver_Bible_structured.md（existing_transcription。原典の画像では確かめていない）。後の資料『トレーナーズ』Vol.5 [P38] は根拠にしない。
  原典（ガイドブック）は読み直していない。
- エンジン: 登録表の写しを固定した v0.113（2d113b5）の木で作り直した。エンジンの全体のテストは再実行していない。
"""
import copy
import csv
import io
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402
import build_cardlist  # noqa: E402
import build_engine_targets as bet  # noqa: E402

BASE = '73a169063463bbf7bcaa3137d70cbf9721d11534'  # この作業の基準（main）
ENGINE = '2d113b5eeea0dbd4f7466e144f7a1345494405c0'  # kyuura-engine v0.113（固定した参照）
AT_COMMIT = 'e519b99e2adcc6c2cd0998569ae5ee1101de6e89'  # この作業のコミット（あとの作業の数と分けるための固定した入力）
RULE = '「ベイビィポケモン」がバトル場にいるかぎり、相手プレイヤーは、ワザを使うときにコインを投げて、「うら」なら、そのワザは失敗します。'
EVOLVES_TO = {
    'neo1-022': ['ブーバー'], 'neo1-042': ['ピカチュウ'], 'neo1-044': ['エレブー'], 'neo1-070': ['ピッピ'],
    'neo2-033': ['エビワラー', 'サワムラー', 'カポエラー'], 'neo2-050': ['プリン'], 'neo3-031': ['ルージュラ'],
    'PF2-007': ['ピカチュウ'], 'NIP1X-002': ['ブーバー'], 'NIP2X-002': ['ピカチュウ'], 'PRN-012': ['ピッピ'],
    'PRN-031': ['プリン'], 'PRN-037': ['ルージュラ'],
}
RULES_FILLED = ('neo1-022', 'neo1-042', 'neo1-044', 'neo1-070', 'neo2-033', 'neo2-050')
V0113_CARDS = ('neo1-063', 'neo3-028', 'neo3-043', 'neo3-044', 'neo4-022', 'PR1-078')


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def base_json(rel):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{BASE}:{rel}'], capture_output=True, text=True, check=True).stdout)


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.checks = load('data/curation/card_image_checks.json')


class EvolvesToTest(Data):
    """進化先の欄（pokemon.evolves_to）: ベイビィだけに置き、印刷で確かめた値を訂正で入れる（未確認は null。推測で埋めない）。"""

    def test_values_and_where_the_field_is(self):
        babies = {c['id'] for c in self.cards if (c['pokemon'] or {}).get('stage') == 'baby'}
        self.assertEqual(babies, set(EVOLVES_TO))
        for c in self.cards:
            p = c['pokemon']
            if not p:
                continue
            if p['stage'] == 'baby':
                self.assertEqual(p['evolves_to'], EVOLVES_TO[c['id']], c['id'])  # バルキーは 3 つとも、印刷の順
                self.assertIsNone(p['evolves_from'])
                self.assertEqual(list(p)[:4], ['dex', 'stage', 'evolves_from', 'evolves_to'])
                self.assertNotIn('pokemon.evolves_to', c['data_gaps'])
            else:
                self.assertNotIn('evolves_to', p, c['id'])  # 欄がない = 適用外（進化できないという意味ではない）

    def test_evolution_targets_keep_their_printed_stage(self):
        # ベイビィから進化できることを理由に、進化先のカードの stage・evolves_from を変えていない
        # この作業のコミット（e519b99）と基準（73a1690）で比べる。あとの作業で、進化先のカードの段階を画像で確かめて直したもの
        # （2026-10-30 の PRN-030 カポエラー。印刷はたねポケモン）は、画像の照合の記録を持つ訂正だけ
        names = {n for v in EVOLVES_TO.values() for n in v}
        old = {c['id']: c for c in base_json('data/cards.json')['cards']}
        then = {c['id']: c for c in json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{AT_COMMIT}:data/cards.json'],
                                                                capture_output=True, text=True, check=True).stdout)['cards']}
        targets = [c for c in then.values() if c['pokemon'] and c['name']['ja'] in names]
        self.assertTrue(targets)
        fixes = {(c['card_id'], c['field']): c for c in self.ledger['corrections']}
        for c in targets:
            for k in ('stage', 'evolves_from'):
                self.assertEqual(c['pokemon'][k], old[c['id']]['pokemon'][k], c['id'])
                if self.by_id[c['id']]['pokemon'][k] != c['pokemon'][k]:
                    fix = fixes[(c['id'], f'pokemon.{k}')]
                    self.assertEqual((fix['basis'], fix['decided_on'] > '2026-10-27'), ('card_image_check', True), c['id'])
                    self.assertTrue(fix['image_check'])

    def test_unconfirmed_stays_null_and_is_a_gap(self):
        rec = copy.deepcopy(self.by_id['neo2-033'])
        rec['pokemon'].pop('evolves_to')
        rec['notes'], rec['corrections'] = [], []
        build_cardlist.add_evolves_to(rec)
        self.assertIsNone(rec['pokemon']['evolves_to'])
        build_cardlist.check_evolves_to([rec], {'corrections': []})
        self.assertIn('pokemon.evolves_to', build_cardlist.non_pack.data_gaps(rec))
        self.assertEqual(build_cardlist.evolves_to_status(rec['pokemon']), 'unconfirmed')
        # 訂正の記録なしの値・[]・空白のある名前・ベイビィ以外の欄は受け付けない
        for bad in (['エビワラー'], [], ['エビ ワラー']):
            r = copy.deepcopy(rec)
            r['pokemon']['evolves_to'] = bad
            with self.assertRaises(SystemExit):
                build_cardlist.check_evolves_to([r], {'corrections': []})
        basic = copy.deepcopy(next(c for c in self.cards if c['name']['ja'] == 'ピカチュウ' and c['pokemon']['stage'] == 'basic'))
        basic['pokemon']['evolves_to'] = None
        with self.assertRaises(SystemExit):
            build_cardlist.check_evolves_to([basic], {'corrections': []})

    def test_corrections_are_reapplied_on_regeneration(self):
        fix = next(c for c in self.ledger['corrections'] if c['id'] == 'FIX-neo2-033-EVOLVES-TO')
        rec = copy.deepcopy(self.by_id['neo2-033'])
        rec['pokemon'].pop('evolves_to')
        rec['notes'] = []
        rec.pop('corrections')
        build_cardlist.add_evolves_to(rec)
        build_cardlist.apply_corrections([rec], {'corrections': [fix], 'candidates': []})
        self.assertEqual(rec['pokemon']['evolves_to'], ['エビワラー', 'サワムラー', 'カポエラー'])
        self.assertIn('「エビワラー・サワムラー・カポエラー」を入れた', rec['notes'][0])
        again = copy.deepcopy(rec)  # 値が入っていれば（before が null でなければ）止まる
        again.pop('corrections')
        with self.assertRaises(SystemExit):
            build_cardlist.apply_corrections([again], {'corrections': [fix], 'candidates': []})

    def test_json_and_csv_agree(self):
        rows = {r['id']: r for r in csv.DictReader(io.StringIO((ROOT / 'data' / 'cards.csv').read_text(encoding='utf-8')))}
        self.assertEqual(len(rows), len(self.cards))
        for c in self.cards:
            p, row = c['pokemon'], rows[c['id']]
            self.assertEqual(row['evolves_to_status'], build_cardlist.evolves_to_status(p), c['id'])
            self.assertEqual(row['evolves_to_ja'].split(), (p or {}).get('evolves_to') or [], c['id'])
        self.assertEqual(Counter(r['evolves_to_status'] for r in rows.values())['printed'], 13)


class ImageCheckTest(Data):
    """カードの画像の照合の記録・訂正の記録・生成した値が同じ内容を指す。照合の記録・最新の説明（CC-・LD-）ではない。"""

    def test_records_point_to_the_same_values(self):
        # この作業（2026-10-27）の照合の記録。あとの作業の記録（2026-10-30 のピカチュウ・ヤドラン・ボロのつりざおなど）は
        # tests/test_next_engine_text_evolution.py が確かめる
        checks = {x['card_id']: x for x in self.checks['checks'] if x['checked_on'] == '2026-10-27'}
        self.assertEqual(set(checks), set(EVOLVES_TO))
        fixes = {c['id']: c for c in self.ledger['corrections']}
        for cid, x in checks.items():
            self.assertEqual(x['print_values'], {'pokemon.rules_text.ja': RULE, 'pokemon.evolves_to': EVOLVES_TO[cid]})
            self.assertEqual(self.by_id[cid]['pokemon']['rules_text']['ja'], RULE)
            self.assertEqual([i['site'] for i in x['images']], ['pcg-search.com [N3]'] + (['なぞのばしょ [N1]'] if cid.startswith(('neo1', 'neo2')) else []))
            self.assertIn('独立した 2 枚の実物の照合とは数えない' if len(x['images']) == 2 else '1 枚だけ', x['independence'])
            for fid in x['corrections']:
                c = fixes[fid]
                self.assertEqual((c['basis'], c['image_check'], c['card_checks_affected'], c['kyuura_saw_image']), ('card_image_check', x['id'], [], True))
                self.assertIn('CC-', c['confirmed_by'])
                self.assertIn('LD-', c['confirmed_by'])
            self.assertEqual([y['id'] for y in self.by_id[cid]['corrections']], x['corrections'])
        # ルール文を埋めたのは欠けていた 6 枚だけ。7 枚は今までの値（転記）が画像と同じで、訂正はない
        filled = sorted(c['card_id'] for c in self.ledger['corrections'] if c['field'] == 'pokemon.rules_text.ja' and c['decided_on'] == '2026-10-27')
        self.assertEqual(filled, sorted(RULES_FILLED))
        for cid in set(EVOLVES_TO) - set(RULES_FILLED):
            self.assertIn('existing_value', checks[cid])
        self.assertIn('修正前', checks['neo1-042']['print_version'])

    def test_out_of_scope_values_are_not_filled(self):
        self.assertEqual(self.by_id['PRN-037']['pokemon']['types'], ['water'])  # 超のムチュールに合わせない
        old = {c['id']: c for c in base_json('data/cards.json')['cards']}
        for cid in EVOLVES_TO:
            for k in ('dex',):
                self.assertEqual(self.by_id[cid]['pokemon'][k], old[cid]['pokemon'][k], cid)
            self.assertEqual(self.by_id[cid]['jp_print'], old[cid]['jp_print'], cid)  # レベルなどを補っていない

    def test_broken_records_are_rejected(self):
        records = [copy.deepcopy(c) for c in self.cards]
        ok = (records, copy.deepcopy(self.checks), copy.deepcopy(self.ledger))
        build_cardlist.check_image_checks(*ok)

        def broken(change):
            recs, doc, led = copy.deepcopy(ok)
            change(recs, doc, led)
            with self.assertRaises(SystemExit):
                build_cardlist.check_image_checks(recs, doc, led)

        broken(lambda r, d, l: d['checks'].append(copy.deepcopy(d['checks'][0])))  # id の重複
        broken(lambda r, d, l: d['checks'][0]['images'][0].update(image_sha256='abc'))  # 画像の記録の欠け
        broken(lambda r, d, l: d['checks'][4]['print_values'].update({'pokemon.evolves_to': ['サワムラー', 'エビワラー', 'カポエラー']}))  # 生成した値と違う
        broken(lambda r, d, l: d['checks'][0]['corrections'].append('FIX-NOT-THERE'))  # 参照切れ
        broken(lambda r, d, l: next(c for c in l['corrections'] if c['id'] == 'FIX-PRN-037-EVOLVES-TO').update(image_check='IMG-PRN-099'))
        broken(lambda r, d, l: next(c for c in l['corrections'] if c['id'] == 'FIX-PRN-037-EVOLVES-TO').update(basis='kyuura_source_check'))  # 証拠の分類の誤り
        broken(lambda r, d, l: next(c for c in l['corrections'] if c['id'] == 'FIX-PRN-037-EVOLVES-TO').update(card_checks_affected=['CC-PMCG6-063-P229']))
        broken(lambda r, d, l: next(c for c in l['corrections'] if c['id'] == 'FIX-neo2-023-RULES-TEXT-JA').pop('evidence'))  # 画像の記録のない card_image_check
        with self.assertRaises(SystemExit):  # 進化先の訂正の根拠が画像の照合でない
            led = copy.deepcopy(self.ledger)
            next(c for c in led['corrections'] if c['id'] == 'FIX-PRN-037-EVOLVES-TO').update(basis='user_provided')
            build_cardlist.check_evolves_to(records, led)


class RegistryTest(Data):
    """エンジンの登録表の写し（固定した v0.113）と、実装の対象の一覧。"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.snapshot = load('data/curation/engine_registered_cards.json')
        cls.targets = load('data/engine_targets.json')

    def test_snapshot_is_the_fixed_v0113_tree(self):
        e = self.snapshot['engine']
        self.assertEqual((e['commit'], e['version'], e['branch'], e['kyuura_commit_copied_by_engine']),
                         (ENGINE, 'v0.113', 'claude/v0.113-variable-coins-search-attachments', BASE))
        self.assertEqual((self.snapshot['extracted_on'], self.snapshot['registry_id']), ('2026-10-27', 'kyuura-engine-0.13'))
        self.assertEqual(self.snapshot['counts'], {'attacks': 1589, 'trainers': 262, 'powers': 146, 'energies': 19,
                                                   'playable_cards': 1250, 'cards_with_registrations': 1232})
        prev = self.snapshot['previous_snapshots']
        self.assertEqual([(p['engine']['version'], p['extracted_on'], p['counts']['playable_cards']) for p in prev], [('v0.68', '2026-10-19', 457)])
        self.assertEqual(self.targets['engine_reference']['previous_snapshots'], prev)

    def test_targets_follow_the_1250_playable_ids(self):
        rows = {r['id']: r for r in self.targets['cards']}
        registered = {i for i, r in rows.items() if r['engine_status'] == 'registered'}
        self.assertEqual(registered, set(self.snapshot['playable']))
        self.assertEqual(Counter(self.by_id[i]['category'] for i in registered), Counter({'pokemon': 951, 'trainer': 262, 'energy': 37}))
        self.assertEqual(len(self.cards) - len(registered), 127)
        self.assertTrue(set(V0113_CARDS) <= registered)
        for cid in EVOLVES_TO:  # データを整えても、エンジンで実装済みにはならない
            self.assertEqual((rows[cid]['engine_status'], rows[cid]['category']), ('new_effect_needed', 'candidate'), cid)

    def test_the_new_field_counts_in_the_identity_comparison(self):
        a = copy.deepcopy(self.by_id['neo1-042'])
        b = copy.deepcopy(a)
        b['pokemon']['evolves_to'] = ['ライチュウ']
        self.assertEqual(bet.diff_fields(bet.engine_view(a), bet.engine_view(b)), ['pokemon.evolves_to'])
        self.assertNotIn('pokemon.evolves_to', bet.engine_view(self.by_id['PMCG1-025']))
        self.assertTrue(bet.ENGINE_GAP.match('pokemon.evolves_to'))


class SidecarTest(unittest.TestCase):
    """ベイビィの条項・裁定・論点（data/sidecar/rulings.json）と、v0.113 の報告事項の取り込み。"""

    @classmethod
    def setUpClass(cls):
        cls.ctx = bcr.load()
        r = cls.ctx['rulings']
        cls.clauses = {x['id']: x for x in r['rule_clauses']}
        cls.rulings = {x['id']: x for x in r['rulings']}
        cls.issues = {x['id']: x for x in r['issues']}
        cls.positions = {x['id']: x for x in r['engine_positions']}
        cls.imports = {x['engine_version']: x for x in r['engine_imports']}

    def test_clauses_rulings_and_issue(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        for cid in ('GR-2000-P308-BABY-SETUP', 'GR-2000-P309-BABY-BENCH', 'GR-2000-P313-POKEMON-COMPOSITION', 'GR-2000-P314-BABY-RULE',
                    'GR-2000-P310-BABY-EVOLUTION', 'GR-2000-P315-EVOLVED-BABY', 'GR-2000-P323-ATTACK-FAILURE', 'GR-2000-P325-PRE-NEO-BABY'):
            self.assertTrue(self.clauses[cid]['transcription_quotes'], cid)
        self.assertEqual({k: self.rulings[k]['status'] for k in self.rulings if k.startswith(('CR-BABY', 'CR-NEUTRAL-SHIELD-EVOLVED', 'CR-DEVOLUTION-SPRAY-EVOLVED'))},
                         {'CR-BABY-RULE-COIN': 'CONFIRMED', 'CR-BABY-RULE-COIN-STEP': 'SUPPORTED', 'CR-BABY-RULE-NOT-POWER': 'SUPPORTED',
                          'CR-BABY-WITHOUT-ATTACKS': 'SUPPORTED', 'CR-NEUTRAL-SHIELD-EVOLVED-BABY': 'CONFIRMED', 'CR-DEVOLUTION-SPRAY-EVOLVED-BABY': 'CONFIRMED'})
        # 一般の規定の当てはめは 1 つの記録（13 枚に分けない）
        self.assertEqual(len(self.rulings['CR-BABY-RULE-COIN']['cards']), 13)
        # 後の資料（P38）は根拠にしない
        for k in ('CR-BABY-RULE-COIN', 'CR-BABY-RULE-COIN-STEP', 'CR-BABY-RULE-NOT-POWER', 'CR-BABY-WITHOUT-ATTACKS'):
            self.assertFalse([b for b in self.rulings[k]['basis'] if b.get('source') == 'P38'], k)
        q = self.issues['UQ-NEO-TEXT-BABY-CATEGORIES']
        self.assertEqual((q['status'], q['engine_refs'], q['recorded_after']['import']), ('UNRESOLVED', [], 'ENGINE-2D113B5'))
        self.assertTrue(any(c['card_id'] == 'neo1-042' for c in self.issues['UQ-ATTACK-PRE-DAMAGE-COIN-ORDER']['cases']))

    def test_transcription_quotes_are_checked(self):
        ctx = copy.deepcopy(self.ctx)
        b = next(b for b in next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-BABY-RULE-COIN')['basis'] if b.get('transcription'))
        b['transcription']['quote'] = b['transcription']['quote'].replace('使ったこと', '使わなかったこと')
        self.assertTrue(any('転記の PDF' in e for e in bcr.validate(ctx)))
        ctx = copy.deepcopy(self.ctx)
        next(x for x in ctx['rulings']['rule_clauses'] if x['id'] == 'GR-2000-P315-EVOLVED-BABY')['transcription_quotes'] = []
        self.assertTrue(any('transcription_quotes' in e for e in bcr.validate(ctx)))

    def test_counts(self):
        # この作業のコミット（e519b99）の論点で数える（あとの作業で論点が増えても、この時点の 73 を確かめる。今の数は
        # tests/test_next_engine_text_evolution.py）
        then = dict(self.ctx, rulings=json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{AT_COMMIT}:data/sidecar/rulings.json'],
                                                                capture_output=True, text=True, check=True).stdout))
        self.assertEqual(bcr.unresolved_counts(then)['research_issues'], 73)
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.113')['research_issues'], 72)
        self.assertEqual(bcr.unresolved_counts(self.ctx)['latest_version'], 'v0.68')  # 照らした最後の取り込み

    def test_v0113_import_and_engine_positions(self):
        imp = self.imports['v0.113']
        self.assertEqual((imp['commit'], imp['parent_version_commit'], imp['kyuura_commit_used_by_engine'], imp['no_ruling_tables']),
                         (ENGINE, 'c6fb94ffd5890b80cce4807c21a8a1b73886b65c', BASE, True))
        self.assertEqual((imp['engine_reported_totals']['stop_codes'], imp['engine_reported_totals']['unresolved_rulings']), (237, 238))
        self.assertNotIn('engine_unresolved_total', imp)  # 範囲外の版を補って数を合わせない
        ctx = copy.deepcopy(self.ctx)
        next(i for i in ctx['rulings']['engine_imports'] if i['engine_version'] == 'v0.113')['engine_unresolved_total'] = 238
        self.assertTrue(any('engine_reported_totals' in e for e in bcr.validate(ctx)))
        states = {k: v['engine_fix']['state'] for k, v in self.positions.items() if k.startswith('ENG-V0113')}
        self.assertEqual(states, {'ENG-V0113-ESP-REDO-CARRIED-RESULTS': 'fixed', 'ENG-V0113-ESP-TENTACLE-GRIP-REACH': 'document_corrected',
                                  'ENG-V0113-ESP-REDO-SWITCH-RESULT': 'not_fixed', 'ENG-V0113-ATTRACT-CURRENT-SHORT-DECK': 'not_fixed'})
        for x in self.positions.values():
            self.assertNotIn('status', x)
            self.assertNotIn('conclusion', x)
        for i in ('UQ-STATED-COUNT-SHORT', 'UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY', 'UQ-UP-TO-ZERO-CHOICE', 'UQ-FACE-DOWN-CARD', 'UQ-COPIED-ATTACK', 'UQ-ESP-REDO'):
            self.assertEqual(self.issues[i]['status'], 'UNRESOLVED')
        self.assertFalse([i for i, x in self.issues.items() if 'ENG-V0113' in json.dumps(x, ensure_ascii=False)])  # 不具合を論点にしない

    def test_card_check_is_kept_and_followed_up(self):
        old = next(x for x in base_json('data/sidecar/card_checks.json')['records'] if x['id'] == 'CC-PMCG6-063-P229')
        new = next(x for x in self.ctx['checks']['records'] if x['id'] == 'CC-PMCG6-063-P229')
        self.assertEqual({k: v for k, v in new.items() if k != 'later_notes'}, old)  # 照合の結果・欄・日を書きかえない
        self.assertEqual((new['card_id'], new['card_name_ja']), ('PMCG6-063', 'サカキのニャース'))
        self.assertEqual(new['later_notes'][0]['card_ids'], ['PR1-078'])
        ctx = copy.deepcopy(self.ctx)
        next(x for x in ctx['checks']['records'] if x['id'] == 'CC-PMCG6-063-P229')['later_notes'][0]['source_rechecked'] = True
        self.assertTrue(any('later_notes' in e for e in bcr.validate(ctx)))
        cand = next(c for c in load('data/curation/card_corrections.json')['candidates'] if c['card_id'] == 'PR1-078')
        self.assertEqual((cand['field'], cand['status'], cand['other_value']), ('jp_print.level', 'gap_open', 11))
        self.assertIsNone(self.ctx['cards']['PR1-078']['jp_print']['level'])
        for rel in ('data/sidecar/rulings.json', 'data/sidecar/card_checks.json', 'data/curation/card_corrections.json'):
            self.assertNotIn('カスミのニャース', (ROOT / rel).read_text(encoding='utf-8'), rel)


if __name__ == '__main__':
    unittest.main()
