"""すごいへんしん（メタモン ES2-032）・わるいはどう（GR団のミュウツー PRN-041）の調査（2026-10-31）の検査。

- 原典: 『ポケモンカードオフィシャルブック2000』[P43] p.239（PDF 241）の拡張シート第2弾赤版のメタモンの最新の説明と解説、
  p.324〜325（PDF 326・327）の公式ルール「20 ポケモンの変身」を、スキャン [J38] の画像で読んだ（kyuura_image）。
- カードの画像（pcg-search.com [N3]）で 2 枚の文面を読んだ（data/curation/card_image_checks.json の IMG-）。メタモンの転記の片仮名「カ」1 字を
  印刷の「力」に直した（FIX-ES2-032-POWER0-TEXT-JA）。GR団のミュウツーは訂正なし。
- 基点: 74b3ceb。kyuura-engine v0.123（25552b8）は比べるためだけに読み、取り込んでいない（登録表の写しは v0.113 のまま）。
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

BASE = '74b3ceb883dd815495d13b9987433fb14b36e44d'  # この作業の基点
AT_COMMIT = '9731354f7e5c6bca08c88bbe98f9449ae96ea7a7'  # この作業の最後のコミット（あとの作業の記録と分けるため、この作業の差はこの時点で比べる）
FIX = 'FIX-ES2-032-POWER0-TEXT-JA'
NEW_CLAUSES = {'GR-2000-P324-TRANSFORM-DEFINITION', 'GR-2000-P324-TRANSFORM-TOP-CARD', 'GR-2000-P324-TRANSFORM-NAME-AND-KIND',
               'GR-2000-P325-TRANSFORM-OWN-STATE', 'GR-2000-P325-TRANSFORM-NOT-NEW', 'GR-2000-P325-TRANSFORM-DURING-ACTION'}
NEW_RULINGS = {
    'CR-TRANSFORM-COPIES-TOP-CARD': 'CONFIRMED', 'CR-TRANSFORM-NAME-AND-KIND': 'CONFIRMED', 'CR-TRANSFORM-BABY-RULE': 'CONFIRMED',
    'CR-TRANSFORM-KEEPS-OWN-STATE': 'CONFIRMED', 'CR-TRANSFORM-NOT-NEWLY-PLAYED': 'CONFIRMED', 'CR-TRANSFORM-FROZEN-DURING-ACTION': 'CONFIRMED',
    'CR-TRANSFORM-REVERT-KNOCKOUT': 'CONFIRMED', 'CR-SUPER-TRANSFORM-REVERT-KNOCKOUT': 'SUPPORTED', 'CR-SUPER-TRANSFORM-CHOICE': 'CONFIRMED',
    'CR-SUPER-TRANSFORM-REVERT-CONDITIONS': 'CONFIRMED', 'CR-SUPER-TRANSFORM-ONCE-PER-TURN': 'SUPPORTED', 'CR-SUPER-TRANSFORM-RETRY-AFTER-SCOOP-UP': 'SUPPORTED',
    'CR-SUPER-TRANSFORM-ENERGY-PAYMENT': 'CONFIRMED', 'CR-DARK-PULSE-SCOPE': 'CONFIRMED', 'CR-DARK-POKEMON-CATEGORY': 'SUPPORTED',
    'CR-DARK-PULSE-DAMAGE-STEP': 'SUPPORTED', 'CR-DARK-COSTUME-COINS': 'CONFIRMED',
}
NEW_ISSUES = {'UQ-TRANSFORM-ENERGY-COLOR-LIST', 'UQ-SUPER-TRANSFORM-TARGETS', 'UQ-SUPER-TRANSFORM-SOURCE-CHANGES', 'UQ-SUPER-TRANSFORM-COPIED-POWERS',
              'UQ-SUPER-TRANSFORM-SUPPRESSED-FORM', 'UQ-SUPER-TRANSFORM-ENERGY-COLORS', 'UQ-TRANSFORM-REVERT-KNOCKOUT-TIMING', 'UQ-TRANSFORM-BABY-AND-BASIC',
              'UQ-DARK-PULSE-TIMING'}
NOTED_ISSUES = {'UQ-TRANSFORM-SCOPE', 'UQ-REACTIVE-SWITCH-DURING-ATTACK', 'UQ-SELF-EXCLUDING-POWER-COPIES'}  # 注記を加えただけの既存の論点
EIGHT = '「草・炎・水・雷・超・闘・悪・鋼」'
SIX = '「草・炎・水・雷・超・闘」'


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def at_base(rel, commit=BASE):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{rel}'], capture_output=True, text=True, check=True).stdout)


def at_commit(rel):
    """この作業のコミット（AT_COMMIT）の記録。あとの作業（2026-10-31 のプクリン・コインで決まる枚数の不足の調査など）が同じ日の記録を加えても、この作業の差を確かめる。"""
    return at_base(rel, AT_COMMIT)


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.fixes = {c['id']: c for c in cls.ledger['corrections']}
        cls.checks = {x['id']: x for x in load('data/curation/card_image_checks.json')['checks']}
        cls.ctx = bcr.load()
        cls.latest = {x['id']: x for x in cls.ctx['latest']['records']}
        cls.cc = {x['id']: x for x in cls.ctx['checks']['records']}
        r = cls.ctx['rulings']
        cls.clauses = {x['id']: x for x in r['rule_clauses']}
        cls.rulings = {x['id']: x for x in r['rulings']}
        cls.issues = {x['id']: x for x in r['issues']}


class CardValueTest(Data):
    """カードの値で変わったのは、メタモン ES2-032 の特殊能力の文面の 1 字だけ（片仮名「カ」→ 漢字「力」）。"""

    def test_only_one_character_changed(self):
        old = {c['id']: c for c in at_base('data/cards.json')['cards']}
        self.assertEqual(set(old), set(self.by_id))
        self.assertEqual(len(self.cards), 1377)
        self.assertEqual({i for i in old if old[i] != self.by_id[i]}, {'ES2-032'})
        a, b = old['ES2-032'], self.by_id['ES2-032']
        before, after = a['pokemon']['powers'][0]['text']['ja'], b['pokemon']['powers'][0]['text']['ja']
        self.assertEqual(len(before), len(after))
        diff = [(x, y) for x, y in zip(before, after) if x != y]
        self.assertEqual(diff, [('カ', '力')])  # 片仮名 U+30AB → 漢字 U+529B の 1 字
        a, b = copy.deepcopy(a), copy.deepcopy(b)
        for r in (a, b):  # 文面・注記・訂正の記録のほかは同じ
            r['pokemon']['powers'][0]['text']['ja'] = None
            r['notes'] = []
            r.pop('corrections', None)
        self.assertEqual(a, b)
        self.assertEqual(self.by_id['PRN-041'], old['PRN-041'])  # GR団のミュウツーは訂正なし

    def test_out_of_scope_values_are_not_filled(self):
        # 画像・書籍にレベル（LV.15・LV.35）・図鑑番号が見えても埋めない。公式大会の補足の文で play_scope を変えない
        for cid in ('ES2-032', 'PRN-041'):
            self.assertIsNone(self.by_id[cid]['jp_print']['level'], cid)
            self.assertEqual(self.by_id[cid]['pokemon']['dex'], [], cid)
        self.assertEqual(self.by_id['PRN-041']['play_scope'], 'standard')
        self.assertEqual(self.by_id['ES2-032']['pokemon']['attacks'], [])

    def test_json_and_csv_agree(self):
        rows = {r['id']: r for r in csv.DictReader(io.StringIO((ROOT / 'data' / 'cards.csv').read_text(encoding='utf-8')))}
        self.assertEqual(rows['ES2-032']['corrections'].split(), [FIX])
        powers = [r for r in csv.DictReader(io.StringIO((ROOT / 'data' / 'powers.csv').read_text(encoding='utf-8'))) if r['card_id'] == 'ES2-032']
        self.assertEqual(len(powers), 1)
        self.assertIn(self.by_id['ES2-032']['pokemon']['powers'][0]['text']['ja'], powers[0].values())


class ImageAndCorrectionTest(Data):
    """カードの画像の照合の記録と訂正。訂正は生成のたびにかかり、before が今の値と違えば止まる。"""

    def test_records(self):
        then = {x['id'] for x in at_commit('data/curation/card_image_checks.json')['checks']}  # あとの作業の記録を数えない
        new = then - {x['id'] for x in at_base('data/curation/card_image_checks.json')['checks']}
        self.assertEqual(new, {'IMG-ES2-032', 'IMG-PRN-041'})
        self.assertLessEqual(then, set(self.checks))  # あとの作業は記録を加えるだけ
        for iid in new:
            x = self.checks[iid]
            self.assertEqual((x['checked_on'], [i['site'] for i in x['images']]), ('2026-10-31', ['pcg-search.com [N3]']), iid)
            for t in x['site_transcriptions']:
                self.assertNotIn('image_sha256', t)  # サイトの転記は画像の読み取りと分ける
        self.assertEqual(self.checks['IMG-ES2-032']['corrections'], [FIX])
        self.assertEqual(self.checks['IMG-PRN-041']['corrections'], [])
        self.assertIn('公式大会では使うことができません', json.dumps(self.checks['IMG-PRN-041']['print_text'], ensure_ascii=False))

    def test_correction_is_reapplied_and_checked(self):
        c = self.fixes[FIX]
        self.assertEqual((c['field'], c['kind'], c['basis'], c['image_check'], c['card_checks_affected']),
                         ('pokemon.powers[0].text.ja', 'transcription_error', 'card_image_check', 'IMG-ES2-032', []))
        rec = copy.deepcopy(self.by_id['ES2-032'])
        rec['pokemon']['powers'][0]['text']['ja'] = c['before']
        rec['notes'] = []
        rec.pop('corrections')
        build_cardlist.apply_corrections([rec], {'corrections': [c], 'candidates': []})
        self.assertEqual(rec['pokemon']['powers'][0]['text']['ja'], c['after'])
        again = copy.deepcopy(rec)  # すでに直っていれば before と合わずに止まる
        again.pop('corrections')
        with self.assertRaises(SystemExit):
            build_cardlist.apply_corrections([again], {'corrections': [c], 'candidates': []})

    def test_mismatches_are_rejected(self):
        doc = load('data/curation/card_image_checks.json')
        ok = ([copy.deepcopy(c) for c in self.cards], doc, copy.deepcopy(self.ledger))
        build_cardlist.check_image_checks(*ok)

        def rejected(change):
            recs, d, led = copy.deepcopy(ok)
            change(recs, d, led)
            with self.assertRaises(SystemExit):
                build_cardlist.check_image_checks(recs, d, led)

        img = lambda d, i: next(x for x in d['checks'] if x['id'] == i)  # noqa: E731
        # 転記の「カ」にもどる（再生成で訂正が外れた）・画像の値の書きかえ・ほかのカードへの当てはめは止まる
        rejected(lambda r, d, l: next(c for c in r if c['id'] == 'ES2-032')['pokemon']['powers'][0]['text'].update(ja=self.fixes[FIX]['before']))
        rejected(lambda r, d, l: img(d, 'IMG-PRN-041')['print_values'].update({'pokemon.attacks[0].damage.display': '20'}))
        rejected(lambda r, d, l: img(d, 'IMG-ES2-032').update(card_id='PMCG3-042', id='IMG-PMCG3-042'))


class SourceReadingTest(Data):
    """p.239 の最新の説明・照合と、p.324〜325 の条項。原典の画像で読んだ記録と、既存の転記・エンジンの記録を分ける。"""

    def test_latest_description_and_check(self):
        ld = self.latest['LD-ES2-032-PWR0']
        self.assertEqual((ld['latest_description']['page'], ld['latest_description']['pdf_page'], ld['latest_description']['source']), ('239', 241, 'P43'))
        self.assertEqual((ld['applies_to_print']['by'], ld['applies_to_print']['heading']), ('figure', '拡張シート第2弾赤版'))
        self.assertEqual((ld['printed_text']['image_check'], ld['meaning_change'], ld['classification']),
                         ('consistent_where_legible', 'ambiguous_in_print', 'latest_description'))
        self.assertIn(EIGHT, ld['latest_description']['text_ja'])  # 8 つの色（原典の画像。転記の誤りではない）
        self.assertNotIn(SIX, ld['latest_description']['text_ja'])
        self.assertIn('おたがいの場にいるポケモンの中から', ld['latest_description']['text_ja'])
        # 印刷の欄は印刷のまま（最新の説明で上書きしていない）
        self.assertEqual(ld['printed_text']['text_ja'], self.by_id['ES2-032']['pokemon']['powers'][0]['text']['ja'])
        self.assertNotIn(EIGHT, ld['printed_text']['text_ja'])
        self.assertEqual([v['date'] for v in ld['verification']], ['2026-10-31'])
        cc = self.cc['CC-ES2-032-P239']
        self.assertEqual((cc['result'], cc['latest_description_refs']), ('printed_vs_latest_only', ['LD-ES2-032-PWR0']))
        self.assertEqual([(g['field'], g['kyuura_value'], g['source_value']) for g in cc['data_gaps']], [('jp_print.level', None, 15)])  # 埋めていない
        # 化石のメタモン・GR団のミュウツーには最新の説明を作っていない（化石は 2 か所の説明が食い違う。GR団のミュウツーは本にない）
        self.assertFalse([i for i, x in self.latest.items() if x['card_id'] in ('PMCG3-042', 'PRN-041')])

    def test_clauses_and_page_records(self):
        new = set(self.clauses) - {x['id'] for x in at_base('data/sidecar/rulings.json')['rule_clauses']}
        self.assertEqual(new, NEW_CLAUSES)
        for i in new:
            self.assertTrue(self.clauses[i]['checked'].startswith('kyuura_image（2026-10-31'), i)
            self.assertEqual(self.clauses[i]['pages'], ['321〜325'], i)
        p43 = next(d for d in load('data/rule_history.json')['documents'] if d['code'] == 'P43')
        pages = {str(p['printed']): p for p in p43['pages']}
        self.assertEqual(pages['239']['pdf'], 241)
        self.assertTrue(NEW_CLAUSES <= set(pages['321〜325']['refs']))
        self.assertTrue({'LD-ES2-032-PWR0', 'CC-ES2-032-P239'} <= set(pages['239']['refs']))

    def test_color_list_conflict_is_an_issue(self):
        q = self.issues['UQ-TRANSFORM-ENERGY-COLOR-LIST']
        self.assertEqual(q['status'], 'UNRESOLVED')
        self.assertIn('8 つの色', q['why_unresolved'])
        self.assertIn('6 つ', q['why_unresolved'])
        self.assertEqual({s['page'] for s in q['sources'] if s['source'] == 'P43'}, {'239', '321〜325'})
        self.assertEqual([c['card_id'] for c in q['cases']], ['PMCG3-042'])

    def test_transcription_is_not_raised_to_image(self):
        # ポケモン回収の解説（p.260）は既存の転記で、kyuura は画像を読んでいない
        r = self.rulings['CR-SUPER-TRANSFORM-RETRY-AFTER-SCOOP-UP']
        self.assertEqual(r['status'], 'SUPPORTED')
        self.assertEqual({b['checked'] for b in r['basis'] if b.get('page') == '260'}, {'existing_transcription'})
        for i in NEW_RULINGS:  # この作業の記録で、kyuura が画像を読んでいないページ（p.260・p.72・p.47）を画像の確認にしていない
            for b in self.rulings[i]['basis']:
                if b.get('source') == 'P43' and b.get('page') in ('260', '72', '47'):
                    self.assertEqual(b['checked'], 'existing_transcription', i)


class RulingTest(Data):
    """裁定と論点: 原典で決まるものだけ CONFIRMED。既存の論点には注記を加えただけ。"""

    def test_new_records(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        base = at_base('data/sidecar/rulings.json')
        then = at_commit('data/sidecar/rulings.json')  # この作業のコミットの記録（あとの作業の裁定・論点・事例を混ぜない）
        rulings = {x['id']: x for x in then['rulings']}
        issues = {x['id']: x for x in then['issues']}
        self.assertLessEqual(set(rulings), set(self.rulings))  # あとの作業は記録を加えるだけ
        self.assertLessEqual(set(issues), set(self.issues))
        new_r = set(rulings) - {x['id'] for x in base['rulings']}
        self.assertEqual({i: rulings[i]['status'] for i in new_r}, NEW_RULINGS)
        for i, st in NEW_RULINGS.items():
            self.assertEqual(bool(rulings[i]['inference']), st == 'SUPPORTED', i)
            self.assertEqual(rulings[i]['engine_refs'], [], i)  # エンジンの裁定を kyuura の裁定に結んでいない
            self.assertEqual(self.rulings[i], rulings[i], i)  # あとの作業はこの作業の裁定を変えていない
        new_i = set(issues) - {x['id'] for x in base['issues']}
        self.assertEqual(new_i, NEW_ISSUES)
        for i in new_i:
            q = issues[i]
            self.assertEqual((q['status'], q['engine_refs'], q['recorded_after']), ('UNRESOLVED', [], {'import': 'ENGINE-2D113B5', 'date': '2026-10-31'}), i)
        # 既存の記録は、3 つの論点に注記を加えただけ（問い・事例・エンジンの記録・監査は変えない）
        now = {x['id']: x for k in ('issues', 'rulings', 'rule_clauses') for x in then[k]}
        changed = sorted(x['id'] for k in ('issues', 'rulings', 'rule_clauses') for x in base[k] if x != now[x['id']])
        self.assertEqual(changed, sorted(NOTED_ISSUES))
        for i in NOTED_ISSUES:
            old = next(x for x in base['issues'] if x['id'] == i)
            self.assertEqual({k: v for k, v in issues[i].items() if k != 'notes'}, {k: v for k, v in old.items() if k != 'notes'}, i)
            self.assertEqual(issues[i]['notes'][:len(old['notes'])], old['notes'], i)
            self.assertEqual(len(issues[i]['notes']), len(old['notes']) + 1, i)
            self.assertTrue(issues[i]['notes'][-1].startswith('2026-10-31'), i)

    def test_engine_derived_questions_are_not_closed(self):
        # TF1・TF2・TE1・TE2・RX1・DF1 などの論点は UNRESOLVED のまま（答えられた部分は注記と別の裁定）
        for i in ('UQ-TRANSFORM-SCOPE', 'UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY', 'UQ-REACTIVE-SWITCH-DURING-ATTACK', 'UQ-SELF-EXCLUDING-POWER-COPIES', 'UQ-SHAPESHIFT-SCOPE'):
            self.assertEqual(self.issues[i]['status'], 'UNRESOLVED', i)
        self.assertEqual([e['ruling_id'] for e in self.issues['UQ-TRANSFORM-SCOPE']['engine_refs']], ['TE1', 'TF1', 'TF2'])

    def test_dark_category_is_by_name_not_type(self):
        self.assertEqual(self.rulings['CR-DARK-POKEMON-CATEGORY']['status'], 'SUPPORTED')
        dark = [c for c in self.cards if (c['name']['ja'] or '').startswith('わるい')]
        self.assertEqual(len(dark), 61)
        self.assertFalse([c['id'] for c in dark if 'darkness' in c['pokemon']['types']])  # 「わるい」ポケモンに「悪」タイプはない
        self.assertFalse([c['id'] for c in self.cards if c['name']['ja'] == 'わるい'])  # 名前がちょうど「わるい」のカードはない
        self.assertFalse(self.by_id['PRN-041']['name']['ja'].startswith('わるい'))

    def test_confirmed_needs_no_inference_and_pages_must_be_recorded(self):
        ctx = copy.deepcopy(self.ctx)  # 推論を含む記録を CONFIRMED にしない
        next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-DARK-POKEMON-CATEGORY')['status'] = 'CONFIRMED'
        self.assertTrue(any('CR-DARK-POKEMON-CATEGORY' in e and 'inference' in e for e in bcr.validate(ctx)))
        ctx = copy.deepcopy(self.ctx)  # ページの記録のない原典のページを、読んだページとして書かない
        next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-TRANSFORM-ENERGY-COLOR-LIST')['sources'][0]['page'] = '238'
        self.assertTrue(any('p.238' in e for e in bcr.validate(ctx)))
        ctx = copy.deepcopy(self.ctx)  # 既存の転記の引用は、転記のそのページにある文だけ
        b = next(b for b in next(x for x in ctx['rulings']['rulings'] if x['id'] == 'CR-SUPER-TRANSFORM-RETRY-AFTER-SCOOP-UP')['basis']
                 if b['checked'] == 'existing_transcription')
        b['transcription']['quote'] += '（同じ番に）'
        self.assertTrue(any('転記の PDF' in e for e in bcr.validate(ctx)))

    def test_counts(self):
        # この作業のコミットの時点の数（あとの作業の記録を数えない。期待値は変えていない）
        then = dict(self.ctx, rulings=at_commit('data/sidecar/rulings.json'), latest=at_commit('data/sidecar/latest_descriptions.json'),
                    checks=at_commit('data/sidecar/card_checks.json'))
        r, latest, checks = then['rulings'], then['latest']['records'], then['checks']['records']
        self.assertEqual((len(latest), len(checks), len(r['rule_clauses']), len(r['rulings']), len(r['issues'])), (48, 85, 41, 337, 88))
        self.assertEqual(bcr.unresolved_counts(then)['research_issues'], 88)
        self.assertEqual(bcr.unresolved_counts(then, as_of='v0.113')['research_issues'], 72)  # 取り込んだ版の時点の数は変わらない
        self.assertFalse({'v0.122', 'v0.123'} & {i['engine_version'] for i in r['engine_imports']})  # 取り込んでいない


class RegistryTest(Data):
    """登録表の写し（v0.113）は変えない。実装の対象の一覧で変わるのは、メタモンの文面の写しだけ。"""

    def test_snapshot_and_targets(self):
        self.assertEqual(load('data/curation/engine_registered_cards.json'), at_base('data/curation/engine_registered_cards.json'))
        rows = {r['id']: r for r in load('data/engine_targets.json')['cards']}
        old = {r['id']: r for r in at_base('data/engine_targets.json')['cards']}
        self.assertEqual({i for i in rows if rows[i] != old[i]}, {'ES2-032'})
        self.assertEqual({k for k in rows['ES2-032'] if rows['ES2-032'][k] != old['ES2-032'][k]}, {'effects_without_registered_text'})  # 文面の写しだけ
        for cid in ('ES2-032', 'PRN-041'):
            self.assertEqual(rows[cid]['engine_status'], old[cid]['engine_status'], cid)
            self.assertNotEqual(rows[cid]['engine_status'], 'registered', cid)
        self.assertEqual(rows['PMCG3-042']['engine_status'], 'registered')  # 化石のメタモンは登録済み（解釈の影響は引き継ぎに書いた）
        self.assertEqual(sum(r['engine_status'] == 'registered' for r in rows.values()), 1250)


if __name__ == '__main__':
    unittest.main()
