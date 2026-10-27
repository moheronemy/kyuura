"""アンノーンI・D・F・[N]・[J] の調査（2026-10-24。kyuura-engine v0.97 の前の研究）の検査。

- ルール文: アンノーンI（neo2-023）・D（neo2-025）・F（neo2-026）は、カードの画像（pcg-search.com [N3]・なぞのばしょ [N1]）で読んだ
  「「アンノーン」はデッキに4枚までしか入れることができません。」を訂正の記録（data/curation/card_corrections.json）で入れた。
  公式の書籍のページとの照合（CC-）ではない。『トレーナーズ』Vol.7 p.3 [P39] は数字が読めず、Vol.8 p.32 [P40] は記事の文（既存の記録）。
- 裁定・論点: 公式ルール 2000.02.14版（『オフィシャルブック2000』[P43]）p.307・p.308（カードの記述・同じ名前）、p.312（場）、
  p.319（HP とダメージ）、p.321（ワザによるダメージ計算の順番）、p.311・p.323・p.325（特殊能力・同じタイミング）。英語版の文面は根拠にしない。
- 原典（ガイドブック）の新しい読み直しはしていない。エンジンの比較元は kyuura-engine v0.96（f3770975）で、裁定の証拠にしていない。
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import build_card_rulings as bcr  # noqa: E402
import build_cardlist  # noqa: E402

RULE = '「アンノーン」はデッキに4枚までしか入れることができません。'
FILLED = ('neo2-023', 'neo2-025', 'neo2-026')
NOT_READ = ('neo2-027', 'neo2-028', 'neo2-030')
NEW_RULINGS = {
    'CR-UNOWN-DECK-LIMIT-ALL-LETTERS': 'SUPPORTED',
    'CR-UNOWN-DF-PROTECTS-OWN-UNOWN': 'CONFIRMED',
    'CR-UNOWN-DF-SOURCE-TYPE': 'SUPPORTED',
    'CR-UNOWN-DF-AT-MOST-ONE': 'CONFIRMED',
    'CR-UNOWN-DF-DAMAGE-STEP': 'SUPPORTED',
}


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_id = {c['id']: c for c in load('data/cards.json')['cards']}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.ctx = bcr.load()
        cls.rulings = {x['id']: x for x in cls.ctx['rulings']['rulings']}
        cls.issues = {x['id']: x for x in cls.ctx['rulings']['issues']}


class RulesTextTest(Base):
    """ルール文の欠けを、カードの画像で確かめた文面で埋めた（ほかの文字の文面・英語版から写していない）。"""

    def test_three_cards_have_the_printed_rules_text(self):
        for cid in FILLED:
            p = self.by_id[cid]['pokemon']
            self.assertEqual(p['rules_text']['ja'], RULE, cid)
            self.assertNotIn('pokemon.rules_text.ja', self.by_id[cid]['data_gaps'], cid)
        # アンノーン[N]・[J] の転記（pcg-search）と一字一句同じ（かぎかっこを含む）
        for cid in ('PF2-001', 'PRN-034'):
            self.assertEqual(self.by_id[cid]['pokemon']['rules_text']['ja'], RULE, cid)

    def test_corrections_record_the_image_check_and_not_a_book_check(self):
        # この調査の時点（2026-10-24）までのルール文の訂正。2026-10-27 のベイビィ 6 枚の訂正（FIX-neo1-022-RULES-TEXT-JA など）は
        # tests/test_baby_preparation_v0113.py が確かめる
        fixes = {c['card_id']: c for c in self.ledger['corrections']
                 if c['field'] == 'pokemon.rules_text.ja' and c['decided_on'] <= '2026-10-24'}
        self.assertEqual(sorted(fixes), list(FILLED))
        for cid, c in fixes.items():
            self.assertEqual((c['before'], c['after'], c['applied_by'], c['basis'], c['kind']),
                             (None, RULE, 'card_corrections', 'card_image_check', 'transcription_omission'), cid)
            self.assertIs(c['kyuura_saw_image'], True)
            self.assertEqual(c['decided_on'], '2026-10-24')
            self.assertEqual([e['site'] for e in c['evidence']], ['pcg-search.com [N3]', 'なぞのばしょ [N1]'])
            for e in c['evidence']:
                self.assertRegex(e['image_sha256'], r'^[0-9a-f]{64}$')
                self.assertTrue(e['image_url'].startswith('https://'))
            self.assertIn('CC-', c['confirmed_by'])  # 照合の記録ではないと明記
            self.assertIn('独立した 2 枚の実物の照合とは数えない', c['scope'])
            self.assertEqual(c['card_checks_affected'], [])
            self.assertEqual([x['id'] for x in self.by_id[cid]['corrections']], [c['id']])
        # カードの id と転記元の URL の番号の違い（D は neo2-026-unknown-d、F は neo2-025-unknown-f）
        self.assertIn('neo2-026-unknown-d', fixes['neo2-025']['evidence'][1]['page_url'])
        self.assertIn('neo2-025-unknown-f', fixes['neo2-026']['evidence'][1]['page_url'])
        # D の転記元の名前の誤り（既存の判定）は二重に訂正しない
        self.assertIn('neo2-025|name', load('data/curation/nazonobasho_review.json'))
        self.assertFalse([c for c in self.ledger['corrections'] if c['card_id'] == 'neo2-025' and c['field'] == 'name.ja'])

    def test_letters_not_read_stay_empty(self):
        cands = {(c['card_id'], c['field']): c for c in self.ledger['candidates']}
        for cid in NOT_READ:
            self.assertIsNone(self.by_id[cid]['pokemon']['rules_text']['ja'], cid)
            self.assertIn('pokemon.rules_text.ja', self.by_id[cid]['data_gaps'])
            self.assertEqual(cands[(cid, 'pokemon.rules_text.ja')]['status'], 'gap_open')

    def test_regeneration_fills_only_an_empty_value(self):
        fix = next(c for c in self.ledger['corrections'] if c['id'] == 'FIX-neo2-025-RULES-TEXT-JA')
        record = copy.deepcopy(self.by_id['neo2-025'])
        record['pokemon']['rules_text']['ja'] = None  # 転記（なぞのばしょ）の値
        record['notes'] = []
        record.pop('corrections', None)
        build_cardlist.apply_corrections([record], {'corrections': [fix], 'candidates': []})
        self.assertEqual(record['pokemon']['rules_text']['ja'], RULE)
        self.assertTrue(record['notes'][0].startswith('訂正（FIX-neo2-025-RULES-TEXT-JA）: 空だった pokemon.rules_text.ja に'))
        other = copy.deepcopy(record)  # 出典に値が入ったら止まる（記録を見直す）
        other.pop('corrections')
        with self.assertRaises(SystemExit):
            build_cardlist.apply_corrections([other], {'corrections': [fix], 'candidates': []})


class CandidateTest(Base):
    """訂正しなかった候補（推測で埋めない・英語の文面で日本語の処理を決めない）。"""

    def test_levels_seen_on_images_are_not_filled(self):
        cands = {(c['card_id'], c['field']): c for c in self.ledger['candidates']}
        for cid, level in (('PF2-001', 14), ('PRN-034', 16)):
            c = cands[(cid, 'jp_print.level')]
            self.assertEqual((c['status'], c['other_value'], c['kyuura_value']), ('gap_open', level, None))
            self.assertIsNone(self.by_id[cid]['jp_print']['level'])

    def test_unown_dragon_is_held(self):
        c = next(c for c in self.ledger['candidates'] if c['card_id'] == 'PRN-034' and c['field'] == 'pokemon.powers[0].text.en')
        self.assertEqual(c['status'], 'held_transcription_difference')
        self.assertEqual(self.by_id['PRN-034']['pokemon']['powers'][0]['text']['en'], c['kyuura_value'])
        self.assertIn('Unown Dragon', c['kyuura_value'])
        self.assertIn('Unown N', c['other_value'])

    def test_jp_en_differences_of_the_damage_reducing_powers(self):
        for cid in ('neo2-025', 'PF2-001'):
            d = self.by_id[cid]['jp_en_differences']
            self.assertEqual([x['kind'] for x in d], ['text'], cid)
            self.assertIn('1 of your Pokémon', d[0]['en'])
            self.assertIn('自分の場の「アンノーン」', d[0]['ja'])


class RulingsTest(Base):
    """新しい裁定（p.307・p.308・p.312・p.319・p.321）。英語版の文面・エンジンの挙動を根拠にしない。"""

    def test_statuses_and_inference(self):
        for rid, status in NEW_RULINGS.items():
            x = self.rulings[rid]
            self.assertEqual(x['status'], status, rid)
            self.assertEqual(bool(x['inference']), status == 'SUPPORTED', rid)
            self.assertEqual(x['engine_refs'], [], rid)
            for b in x['basis']:
                self.assertFalse(b.get('field', '').endswith('.en'), rid)  # 英語の文面を根拠にしない

    def test_deck_limit_uses_p40_but_not_p39_or_p10(self):
        x = self.rulings['CR-UNOWN-DECK-LIMIT-ALL-LETTERS']
        sources = [(b.get('source'), b.get('page')) for b in x['basis'] if 'source' in b]
        self.assertIn(('P40', '32'), sources)
        self.assertNotIn('P39', [s for s, _ in sources])
        self.assertTrue(any('数字が読めない' in n for n in x['notes']))
        self.assertTrue(any('P10' in n and '根拠にしていない' in n for n in x['notes']))
        self.assertEqual(sorted(c['card_id'] for c in x['cards']), sorted(FILLED + ('PF2-001', 'PRN-034')))
        p40 = next(d for d in self.ctx['rule_history']['documents'] if d['code'] == 'P40')
        self.assertEqual(next(p for p in p40['pages'] if p['printed'] == '32')['refs'], ['CR-UNOWN-DECK-LIMIT-ALL-LETTERS'])
        p39 = next(d for d in self.ctx['rule_history']['documents'] if d['code'] == 'P39')
        self.assertEqual(next(p for p in p39['pages'] if p['printed'] == '3')['refs'], [])

    def test_at_most_one_is_card_text_and_which_one_is_open(self):
        x = self.rulings['CR-UNOWN-DF-AT-MOST-ONE']
        self.assertEqual({b['kind'] for b in x['basis']}, {'card_text'})
        self.assertIn('UQ-SELF-EXCLUDING-POWER-COPIES', x['conclusion'])


class IssuesTest(Base):
    """未解決の論点の追加・追記（既存の論点の問い・分類を変えない）。"""

    def test_new_issue_is_kyuura_research_without_engine_refs(self):
        q = self.issues['UQ-SELF-EXCLUDING-POWER-COPIES']
        self.assertEqual((q['status'], q['engine_refs'], q['not_in_engine_index']), ('UNRESOLVED', [], True))
        self.assertEqual(q['recorded_after'], {'import': 'ENGINE-24BFBE2', 'date': '2026-10-24'})
        self.assertEqual([c['card_id'] for c in q['cases']], ['neo2-025', 'PF2-001', 'neo2-027', 'neo4-046', 'PRN-041'])
        self.assertEqual(q['audit']['game_effect'], 'game_result')
        self.assertEqual(q['audit']['new_sources'], [])

    def test_existing_issue_questions_are_unchanged(self):
        self.assertEqual(self.issues['UQ-SPEED-STAR-SCOPE']['question'],
                         'タケシのサンドパンの「スピードスター」が除く「効果」に、相手の場のほかのポケモンの特殊能力が含まれるか')
        self.assertEqual([e['ruling_id'] for e in self.issues['UQ-SPEED-STAR-SCOPE']['engine_refs']], ['SS1'])
        self.assertIn('PF2-001', [c['card_id'] for c in self.issues['UQ-SPEED-STAR-SCOPE']['cases']])
        self.assertNotIn('neo2-040', [c['card_id'] for c in self.issues['UQ-SPEED-STAR-SCOPE']['cases']])  # だましうち（FA1）は含めない
        na = self.issues['UQ-NON-ATTACK-DAMAGE-MODIFIERS']
        self.assertTrue(na['question'].startswith('ワザでないダメージ'))
        self.assertIn('PF2-001', [c['card_id'] for c in na['cases']])
        self.assertEqual([e['ruling_id'] for e in na['engine_refs']], ['KA1', 'RB4', 'EX1', 'TD1'])
        cu = [c['card_id'] for c in self.issues['UQ-CARD-USE-WITHOUT-TARGET']['cases']]
        self.assertTrue({'neo2-023', 'neo2-026', 'PRN-034'} <= set(cu))
        # 特殊能力のダメージの弱点・抵抗力（Z9）は効果を除く範囲と別の論点のまま
        self.assertNotIn('PF2-001', [c['card_id'] for c in self.issues['UQ-POWER-DAMAGE-WEAKNESS-RESISTANCE']['cases']])

    def test_counts_at_past_imports_do_not_include_the_new_issue(self):
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.68')['research_issues'], 71)
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.25')['research_issues'], 24)
        # アンノーンの論点を数える、次の取り込み（v0.113。2026-10-27）の時点の数。そのあとに記録したベイビィの論点
        # （UQ-NEO-TEXT-BABY-CATEGORIES）は数えない（今の数は tests/test_baby_preparation_v0113.py）
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.113')['research_issues'], 72)

    def test_validation_requires_recorded_after_and_index_flag(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        ctx = copy.deepcopy(self.ctx)
        q = next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-SELF-EXCLUDING-POWER-COPIES')
        q.pop('recorded_after')
        self.assertTrue(any('recorded_after' in e for e in bcr.validate(ctx)))
        ctx = copy.deepcopy(self.ctx)
        q = next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-SELF-EXCLUDING-POWER-COPIES')
        q['not_in_engine_index'] = False
        self.assertTrue(any('not_in_engine_index' in e for e in bcr.validate(ctx)))

    def test_no_stop_codes_in_research_text(self):
        q = self.issues['UQ-SELF-EXCLUDING-POWER-COPIES']
        for text in (q['question'], q['why_unresolved'], q['audit']['game_effect_note'], q['audit']['resolution_needs']):
            self.assertIsNone(bcr.ENGINE_TOKENS.search(text))


if __name__ == '__main__':
    unittest.main()
