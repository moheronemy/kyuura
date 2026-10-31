"""ちえくらべ・フラッシュ・とりかえっこプリーズの調査（2026-10-31）の検査。

- 優先A ヤドキング neo1-049 の［ちえくらべ］: カードの画像（IMG-neo1-049）で全文を確かめた（訂正なし）。『オフィシャルブック2000』[P43] の
  p.310・p.311・p.317・p.291（PDF 312・313・319・293）を画像で読んだ。使うかを選べるか（UQ-MIND-GAMES-OPTIONAL）・手順のどこで投げるか
  （UQ-MIND-GAMES-TRAINER-STEP）は未解決のまま、候補と比べを記録した。決まったのはスタジアム・どうぐが当たること（CR-MIND-GAMES-STADIUM-TOOL）と、
  比べる記録の錯乱ジムのコインの位置（CR-CHAOS-GYM-COIN-BEFORE-CONDITIONS。SUPPORTED）。
- 優先B フラッシュ ES2-035: p.270（PDF 272）の最新の説明・図版・解説、p.228（PDF 230）の解説、カードの画像。いちばん上のカードが相手に見える
  ことだけが決まった（CR-FLASH-TOP-CARD-SEEN）。下のカード・ほかの効果の向きは UQ-FLASH-FACE-UP-DECK のまま。
- 優先C とりかえっこプリーズ PR1-027: p.293（PDF 295）の最新の説明・図版・解説、カードの画像。印刷の読点 1 つの欠けを直した（FIX-PR1-027-TEXT-JA）。
  対戦の中の持ち主は UQ-SWAP-PLEASE-OWNERSHIP のまま。名前の末尾の「！」は報告事項で、直していない。
- 基点: 134a664（プクリン・枚数不足の研究。main b9e7cff の 3 コミット先）。kyuura-engine v0.124（e165fe0）は比べるためだけに読み、取り込んでいない。
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

BASE = '134a664c6adf67d5604148a31b58e1a7d26d4d6d'  # この作業の基点
# この作業の終わりのコミット。カードの値の比べはこの時点に固定する（あとの作業の変更、たとえば 2026-10-31 の目録の分類の欄の追加と分ける）
AT_COMMIT = '57d01f45cfb8b086d03dc0525b329cf6adeff69b'
SWAP_BEFORE = '(このカードは、お互いに手札が1枚以上ある時だけ使える)'
SWAP_AFTER = '(このカードは、お互いに手札が1枚以上ある時だけ、使える)'
NEW_IMAGES = {'IMG-neo1-049', 'IMG-ES2-035', 'IMG-PR1-027'}
NEW_LD = {'LD-ES2-035-TRAINER', 'LD-PR1-027-TRAINER'}
NEW_CC = {'CC-ES2-035-P270', 'CC-PR1-027-P293'}
NEW_RULINGS = {
    'CR-FLASH-TOP-CARD-SEEN': 'CONFIRMED', 'CR-SWAP-PLEASE-USE-IN-GAME': 'CONFIRMED', 'CR-SWAP-PLEASE-REAL-TRADE-SEPARATE': 'SUPPORTED',
    'CR-CHAOS-GYM-COIN-BEFORE-CONDITIONS': 'SUPPORTED', 'CR-MIND-GAMES-STADIUM-TOOL': 'CONFIRMED',
}
STUDIED_ISSUES = {'UQ-MIND-GAMES-OPTIONAL', 'UQ-MIND-GAMES-TRAINER-STEP', 'UQ-FLASH-FACE-UP-DECK', 'UQ-SWAP-PLEASE-OWNERSHIP'}
QUOTE_FIXED = {'CR-SWAP-PLEASE-PROCEDURE', 'CR-SWAP-PLEASE-USE-CONDITION'}  # 訂正に合わせて引用の読点だけを直した
NEW_PAGES = {'270': 272, '228': 230, '293': 295, '291': 293}


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def at_base(rel, commit=BASE):
    return json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{rel}'], capture_output=True, text=True, check=True).stdout)


class Data(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load('data/cards.json')['cards']
        cls.by_id = {c['id']: c for c in cls.cards}
        cls.ledger = load('data/curation/card_corrections.json')
        cls.checks = {x['id']: x for x in load('data/curation/card_image_checks.json')['checks']}
        cls.ctx = bcr.load()
        cls.latest = {x['id']: x for x in cls.ctx['latest']['records']}
        cls.cc = {x['id']: x for x in cls.ctx['checks']['records']}
        r = cls.ctx['rulings']
        cls.clauses = {x['id']: x for x in r['rule_clauses']}
        cls.rulings = {x['id']: x for x in r['rulings']}
        cls.issues = {x['id']: x for x in r['issues']}
        cls.base_r = at_base('data/sidecar/rulings.json')


class CardValueTest(Data):
    """カードの値で変わったのは、とりかえっこプリーズ PR1-027 の文面の読点 1 つだけ。"""

    def test_only_one_comma_changed(self):
        old = {c['id']: c for c in at_base('data/cards.json')['cards']}
        then = {c['id']: c for c in at_base('data/cards.json', AT_COMMIT)['cards']}
        self.assertEqual(len(then), 1377)
        self.assertEqual(set(old), set(then))
        self.assertEqual(set(old), set(self.by_id))
        self.assertEqual({i for i in old if old[i] != then[i]}, {'PR1-027'})
        before, after = old['PR1-027']['trainer']['text']['ja'], then['PR1-027']['trainer']['text']['ja']
        self.assertEqual(self.by_id['PR1-027']['trainer']['text']['ja'], after)  # 今の値も同じ
        self.assertEqual(before.replace(SWAP_BEFORE, SWAP_AFTER), after)
        self.assertEqual(len(after), len(before) + 1)
        a, b = copy.deepcopy(old['PR1-027']), copy.deepcopy(then['PR1-027'])
        for r in (a, b):  # 文面・注記・訂正の記録のほかは同じ
            r['trainer']['text']['ja'] = None
            r['notes'] = r['notes'][:1]
            r.pop('corrections', None)
        self.assertEqual(a, b)

    def test_correction_ledger(self):
        old = at_base('data/curation/card_corrections.json')
        self.assertEqual(self.ledger['corrections'][:len(old['corrections'])], old['corrections'])  # 過去の訂正は変えていない
        self.assertEqual(self.ledger['candidates'], old['candidates'])
        new = self.ledger['corrections'][len(old['corrections']):]
        self.assertEqual([c['id'] for c in new], ['FIX-PR1-027-TEXT-JA'])
        fix = new[0]
        self.assertEqual((fix['card_id'], fix['field'], fix['basis'], fix['image_check'], fix['decided_on'], fix['kind']),
                         ('PR1-027', 'trainer.text.ja', 'card_image_check', 'IMG-PR1-027', '2026-10-31', 'transcription_error'))
        self.assertTrue(fix['before'].endswith(SWAP_BEFORE) and fix['after'].endswith(SWAP_AFTER))
        self.assertEqual(self.by_id['PR1-027']['corrections'][0]['id'], 'FIX-PR1-027-TEXT-JA')

    def test_out_of_scope_values_are_kept(self):
        # 名前の末尾の「！」は報告事項で直さない。レベル・図鑑番号は埋めない。英語版の文を日本語に加えない
        self.assertEqual(self.by_id['PR1-027']['name']['ja'], 'とりかえっこプリーズ')
        old = {c['id']: c for c in at_base('data/cards.json')['cards']}
        then = {c['id']: c for c in at_base('data/cards.json', AT_COMMIT)['cards']}
        for cid in ('neo1-049', 'ES2-035'):
            self.assertEqual(then[cid], old[cid], cid)
        self.assertEqual(self.by_id['neo1-049']['jp_print']['level'], 39)  # 拡張パックの値（画像の LV.39 と同じ）。変えていない
        self.assertIsNone(self.by_id['PR1-027']['jp_print']['level'])
        self.assertNotIn('のぞむなら', self.by_id['neo1-049']['pokemon']['powers'][0]['text']['ja'])

    def test_csv_matches_json(self):
        import csv
        with (ROOT / 'data' / 'cards.csv').open(encoding='utf-8', newline='') as f:
            rows = {r['id']: r for r in csv.DictReader(f)}
        self.assertTrue(rows['PR1-027']['text_ja'].endswith(SWAP_AFTER))


class ImageCheckTest(Data):
    """カードの画像の照合: 3 件。画像の値と生成した値が同じ。訂正は PR1-027 の 1 件だけ。"""

    def test_new_records(self):
        old = {x['id']: x for x in at_base('data/curation/card_image_checks.json')['checks']}
        self.assertEqual(set(self.checks) - set(old), NEW_IMAGES)
        for i, x in old.items():
            self.assertEqual(self.checks[i], x, i)
        for i in NEW_IMAGES:
            x = self.checks[i]
            self.assertEqual((x['checked_on'], x['checked_by'], len(x['images'])), ('2026-10-31', 'kyuura', 1), i)
            self.assertEqual(len(x['images'][0]['image_sha256']), 64, i)
            for f, v in x['print_values'].items():
                self.assertEqual(bcr.resolve(self.by_id[x['card_id']], f), v, (i, f))
        self.assertEqual(len({self.checks[i]['images'][0]['image_sha256'] for i in NEW_IMAGES}), 3)
        self.assertEqual({i: self.checks[i]['corrections'] for i in NEW_IMAGES},
                         {'IMG-neo1-049': [], 'IMG-ES2-035': [], 'IMG-PR1-027': ['FIX-PR1-027-TEXT-JA']})
        self.assertNotIn('name.ja', self.checks['IMG-PR1-027']['print_values'])  # 名前の「！」は値に入れていない（報告事項）


class SourceReadingTest(Data):
    """原典: p.270・p.293 の最新の説明は図版で照合した。p.228・p.291・p.310・p.311・p.317 は裁定・論点の根拠。"""

    def test_latest_descriptions_and_checks(self):
        self.assertEqual(bcr.validate(self.ctx), [])
        old_ld = {x['id'] for x in at_base('data/sidecar/latest_descriptions.json')['records']}
        old_cc = {x['id'] for x in at_base('data/sidecar/card_checks.json')['records']}
        self.assertEqual(set(self.latest) - old_ld, NEW_LD)
        self.assertEqual(set(self.cc) - old_cc, NEW_CC)
        for i in NEW_LD:
            x = self.latest[i]
            self.assertEqual((x['applies_to_print']['by'], x['printed_text']['image_check'], x['meaning_change']), ('figure', 'match', 'none_apparent'), i)
            self.assertEqual(x['verification'][0]['by'], 'kyuura')
        self.assertEqual({i: (self.cc[i]['page'], self.cc[i]['result']) for i in NEW_CC},
                         {'CC-ES2-035-P270': ('270', 'printed_vs_latest_only'), 'CC-PR1-027-P293': ('293', 'printed_vs_latest_only')})
        self.assertNotIn('name.ja', self.cc['CC-PR1-027-P293']['checked_fields'])

    def test_page_records(self):
        # この作業のコミットの時点で比べる（あとの作業がページの記録を加えても、この作業で加えたページは同じ）
        doc = next(d for d in at_base('data/rule_history.json', AT_COMMIT)['documents'] if d['code'] == 'P43')
        pages = {str(p['printed']): p for p in doc['pages']}
        old = {str(p['printed']) for p in next(d for d in at_base('data/rule_history.json')['documents'] if d['code'] == 'P43')['pages']}
        self.assertEqual(set(pages) - old, set(NEW_PAGES))
        now = next(d for d in self.ctx['rule_history']['documents'] if d['code'] == 'P43')
        self.assertTrue(all(pg in now['pages'] for pg in doc['pages']))  # この作業のページの記録は今も同じ値で残っている
        for page, pdf in NEW_PAGES.items():
            self.assertEqual(pages[page]['pdf'], pdf)
            self.assertIn('2026-10-31 に kyuura が画像で読んだ', pages[page]['content'])
        self.assertIn('2026-10-31 に kyuura が画像で読んだ', pages['310']['content'])
        # p.310 の条項は読んだことを注記しただけで、確かめ方の値（エンジンの記録の取り込み）は変えない
        base_clause = next(c for c in self.base_r['rule_clauses'] if c['id'] == 'GR-2000-P310-TRAINERS')
        now = self.clauses['GR-2000-P310-TRAINERS']
        self.assertEqual(now['checked'], 'engine_report')
        self.assertEqual({k: v for k, v in now.items() if k != 'notes'}, {k: v for k, v in base_clause.items() if k != 'notes'})
        self.assertEqual(now['notes'][:len(base_clause['notes'])], base_clause['notes'])

    def test_unread_page_is_rejected(self):
        # ページの記録を除くと、p.291 を引く記録が止まる（読んでいないページを根拠にしない）
        ctx = copy.deepcopy(self.ctx)
        doc = next(d for d in ctx['rule_history']['documents'] if d['code'] == 'P43')
        doc['pages'] = [p for p in doc['pages'] if str(p['printed']) != '291']
        errs = bcr.validate(ctx)
        self.assertTrue(any('CR-CHAOS-GYM-COIN-BEFORE-CONDITIONS' in e and 'p.291' in e for e in errs))


class RulingTest(Data):
    """裁定と論点: 推論を含むものだけ SUPPORTED。4 つの論点は未解決のまま、問い・事例を変えず、注記・出典・監査を加えた。"""

    def test_new_rulings(self):
        old = {x['id'] for x in self.base_r['rulings']}
        new = set(self.rulings) - old
        self.assertEqual({i: self.rulings[i]['status'] for i in new}, NEW_RULINGS)
        for i in new:
            x = self.rulings[i]
            self.assertEqual(x['status'] == 'SUPPORTED', bool(x['inference']), i)
            self.assertEqual(x['engine_refs'], [], i)
        self.assertEqual({x['id'] for x in self.base_r['issues']}, set(self.issues))  # 新しい論点は立てていない

    def test_studied_issues_stay_unresolved(self):
        old = {x['id']: x for x in self.base_r['issues']}
        for i in STUDIED_ISSUES:
            a, b = old[i], self.issues[i]
            self.assertEqual(b['status'], 'UNRESOLVED', i)
            for k in ('question', 'why_unresolved', 'cases', 'official_material', 'rule_clause_refs', 'reachability', 'recorded_after'):
                self.assertEqual(b.get(k), a.get(k), (i, k))
            self.assertEqual(b['notes'][:len(a['notes'])], a['notes'], i)
            self.assertEqual(b['sources'][:len(a['sources'])], a['sources'], i)
            self.assertIn(a['audit']['searched'], b['audit']['searched'], i)  # 前の監査の文を残した
            self.assertEqual(b['audit']['audited_on'], '2026-10-31')
            self.assertTrue(b['audit']['new_sources'] and all(ns['resolves'] is False for ns in b['audit']['new_sources']), i)
        # p.293 の最初の出典（既存の転記の記録）は page が null のまま残す
        self.assertIsNone(self.issues['UQ-SWAP-PLEASE-OWNERSHIP']['sources'][0]['page'])

    def test_only_expected_existing_records_changed(self):
        now = {x['id']: x for k in ('issues', 'rulings', 'rule_clauses') for x in self.ctx['rulings'][k]}
        changed = {x['id'] for k in ('issues', 'rulings', 'rule_clauses') for x in self.base_r[k] if x != now[x['id']]}
        self.assertEqual(changed, STUDIED_ISSUES | QUOTE_FIXED | {'GR-2000-P310-TRAINERS'})
        for i in QUOTE_FIXED:  # 引用の読点と注記のほかは同じ
            a = copy.deepcopy(next(x for x in self.base_r['rulings'] if x['id'] == i))
            b = copy.deepcopy(self.rulings[i])
            for x in (a, b):
                for bb in x['basis']:
                    if bb.get('quote') in (SWAP_BEFORE, SWAP_AFTER):
                        bb['quote'] = None
                x['notes'] = x['notes'][:len(a['notes'])]
            self.assertEqual(a, b, i)
            self.assertIn(SWAP_AFTER, [bb.get('quote') for bb in self.rulings[i]['basis']])

    def test_inference_is_not_confirmed(self):
        for i in ('CR-CHAOS-GYM-COIN-BEFORE-CONDITIONS', 'CR-SWAP-PLEASE-REAL-TRADE-SEPARATE'):
            ctx = copy.deepcopy(self.ctx)
            next(x for x in ctx['rulings']['rulings'] if x['id'] == i)['status'] = 'CONFIRMED'
            self.assertTrue(any(i in e and 'inference' in e for e in bcr.validate(ctx)), i)
        ctx = copy.deepcopy(self.ctx)  # 新しい資料で論点が決まったことにしない
        next(x for x in ctx['rulings']['issues'] if x['id'] == 'UQ-FLASH-FACE-UP-DECK')['audit']['new_sources'][0]['resolves'] = True
        self.assertTrue(any('UQ-FLASH-FACE-UP-DECK' in e and 'resolves' in e for e in bcr.validate(ctx)))

    def test_basis_is_kyuura_image_or_data(self):
        # 新しい裁定の根拠は、kyuura が画像で読んだ原典の文か kyuura のカードの値（画像で確かめた）。英語版・後年の資料・エンジンの実装は根拠にしない
        for i in NEW_RULINGS:
            for b in self.rulings[i]['basis']:
                if b['kind'] != 'derived':
                    self.assertIn(b['checked'], ('kyuura_image', 'kyuura_data'), i)
                    if 'source' in b:
                        self.assertEqual(b['source'], 'P43', i)
        self.assertNotIn('EN-2002-SLOWKING-BAN', json.dumps(self.rulings['CR-MIND-GAMES-STADIUM-TOOL']['basis'], ensure_ascii=False))

    def test_counts(self):
        r = self.ctx['rulings']
        self.assertEqual((len(self.latest), len(self.cc), len(r['rule_clauses']), len(r['rulings']), len(r['issues'])), (54, 90, 41, 350, 90))
        self.assertEqual(bcr.unresolved_counts(self.ctx)['research_issues'], 90)
        self.assertEqual(bcr.unresolved_counts(self.ctx, as_of='v0.113')['research_issues'], 72)  # 取り込んだ版の時点の数は変わらない
        self.assertFalse({'v0.118', 'v0.122', 'v0.123', 'v0.124', 'v0.125'} & {i['engine_version'] for i in r['engine_imports']})  # 取り込んでいない


class RegistryTest(Data):
    """登録表の写し（v0.113）は変えない。実装の対象の一覧で変わるのは、PR1-027 の文面の写しだけ（engine_status は同じ）。"""

    def test_snapshot_and_targets(self):
        self.assertEqual(load('data/curation/engine_registered_cards.json'), at_base('data/curation/engine_registered_cards.json'))
        rows = {r['id']: r for r in load('data/engine_targets.json')['cards']}
        old = {r['id']: r for r in at_base('data/engine_targets.json')['cards']}
        self.assertEqual({i for i in rows if rows[i] != old[i]}, {'PR1-027'})
        self.assertEqual({k for k in rows['PR1-027'] if rows['PR1-027'][k] != old['PR1-027'][k]}, {'effects_without_registered_text'})
        for cid in ('neo1-049', 'ES2-035', 'PR1-027'):
            self.assertEqual(rows[cid]['engine_status'], old[cid]['engine_status'], cid)
            self.assertNotEqual(rows[cid]['engine_status'], 'registered', cid)


if __name__ == '__main__':
    unittest.main()
