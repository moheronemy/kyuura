# kyuura — 旧裏ポケモンカードの資料

初期のポケモンカードゲーム、いわゆる「旧裏（きゅううら）」のカードリストとルールをまとめた資料集です。
日本版（メディアファクトリー発売）と英語版（Wizards of the Coast 発売）の違いを明らかにすることを主な目的にしています。

## 旧裏とは

- 1996年10月の第1弾から 2001年まで、日本で発売されたポケモンカードの通称です。カードの裏面が、現在とは違う「ポケットモンスターカードゲーム」のデザインでした。
  - 裏面は 2001年7月の「ポケモンカード★VS」から現在のデザインに変わりました（[出典と確認状況](docs/sources.md) の X35）。
- 拡張パックは次の 10 弾です。
  - 第1弾「拡張パック」から第6弾「闇からの挑戦」まで（「ポケットモンスターカードゲーム」の時期）。
  - neo 第1〜4弾「金、銀、新世界へ...」〜「闇、そして光へ...」（「ポケモンカード★neo」の時期）。
- 英語版は Wizards of the Coast（WotC）が 1999年1月の Base Set から 2003年まで発売しました。日本の弾をもとにしていますが、ルールや収録内容に違いがあります。

## 目次

### ルール

- [日米のルールの違い](docs/rules/differences.md) — **まずこれ**。ルールの違いだけを項目ごとに比べた専用ページ（データ: [`data/rule_differences.json`](data/rule_differences.json)）
- [日本版のルールと変遷](docs/rules/japanese.md) — ルールの版（公式ルール第2版〜第4版、ルールブック第5版など）での変更点、公式大会のルール
- [日本版のルールの版ごとの比較（1996〜1999年）](docs/rules/japanese-editions.md) — 第1版〜第5版を項目ごとに並べた表。確認できなかったマスは「未確認」
- [英語版（WotC 版）のルール](docs/rules/wotc.md) — 1999〜2003年。2003年の変更も参考に記載
- [旧裏・新裏の混合ルール（2001〜2003年）](docs/rules/mixed-2002.md) — 裏面の変更後の混合、サポーター・ポケパワー/ポケボディーへの読み替え、殿堂入りカード、バトルロード 2002
- [新ガルーラルール（2002年）](docs/rules/kangaskhan-2002.md) — 旧裏と新裏の山札を使い分ける 2 人 1 組の対戦と「タッチ世代交代！」
- [カードの文面の変更とエラッタの履歴](docs/rules/errata-history.md) — 印刷の変更・公式エラッタ・読み替えの区別
- [カードの裁定と公式の最新の説明](docs/rules/card-rulings.md) — カード・ワザごとの公式の書籍の「最新の説明」（印刷の文面とは別に記録）、照合、裁定（CONFIRMED・SUPPORTED）、未解決の論点、kyuura-engine v0.25までの裁定 id との対応（エナジートランス・あまごい・ダメージスワップ・かがくへんかガス・とうめい・はんげき・こんじょう・ふしちょう・ほのおのかべ・こうらがえし・わるいねぞう・たおれこむ・だつりょくえきなど）
- [出典と確認状況](docs/sources.md)、[印刷物の照合記録](docs/printed-sources.md)（スキャンで確認した会報・雑誌・書籍の巻号とページ）
- [調査の状況](docs/research-status.md) — 分野ごとにどこまで確かめられたか、件数、未解決の問題、必要な原本
- [エンジン開発の準備状況](docs/engine-readiness.md) — 対戦エンジン（別のリポジトリ [kyuura-engine](https://github.com/moheronemy/kyuura-engine)）の基準にしたルールと調査データ。エンジンを作り始める前の計画も記録として残している

### カード

- [カードリストの見かた](docs/cards/README.md) と各弾のリスト（10 弾・780 枚。一覧表と、ワザ・ポケモンパワー・効果文つきのカード詳細）
- [カードの日英の違い](docs/cards/card-differences.md) — 文面の意味・エラッタ・表記・イラスト
- [収録内容・製品の違い](docs/cards/set-differences.md) — 弾の対応、印刷、裏面
- [英語版のみに見られるカード](docs/cards/english-only.md)
- [再録カードの対応付け](docs/cards/reprints.md) — 商品をまたいだ同じカードと英語版の再録の判定のしかた、点検の結果
- [拡張パック以外の商品](docs/cards/other-products.md) — 拡張シート第1〜3弾、映画公開記念パック「サザンアイランド」、ポケモンジムの構築済みデッキ 6 種、クイックスターターギフト、イントロパック・イントロパック★neo、neo プレミアムファイル 1〜3、プロモのカードリスト

### データ

- [`data/cards.json`](data/cards.json) — 構造化データ（スキーマ: [docs/data-schema.md](docs/data-schema.md)）
- [`data/cards.csv`](data/cards.csv)、[`data/attacks.csv`](data/attacks.csv)、[`data/powers.csv`](data/powers.csv) — 表形式の写し
- [`data/rule_differences.json`](data/rule_differences.json) — 日米のルールの違い
- [`data/rule_history.json`](data/rule_history.json) — 旧裏期のルール・大会レギュレーション・エラッタの記録（日付・地域・対象カード・根拠の種類・確度）、日本版のルールの版ごとの比較、スキャンで確認した印刷物の巻号・ページ
- [`data/sidecar/`](data/sidecar/) — `data/cards.json` を変えずにカード・ワザに加える出典つきの情報（公式の最新の説明、カードの照合、裁定と未解決の論点）。形式は [docs/data-schema.md の「サイドカー」](docs/data-schema.md#サイドカーdatasidecar)
- 生成スクリプト: [`scripts/`](scripts/README.md)、テスト: `python3 -m unittest discover -s tests`

### サイドカーの使いかた（リポジトリの直下で実行）

印刷の文面は `data/cards.json`、公式の書籍の最新の説明・照合・裁定・未解決の論点は `data/sidecar/` にあります（最新の説明は印刷の文面を書きかえず、公式エラッタとも別に記録しています）。どれも `scripts/build_card_rulings.py` の関数で引けます。

```python
import sys; sys.path.insert(0, 'scripts')
import build_card_rulings as bcr

ctx = bcr.load()
card = ctx['cards']['PMCG1-032']                                   # カメックス
# 1. 印刷の文面（data/cards.json）
print(card['pokemon']['powers'][0]['text']['ja'])
# 2. 公式の最新の説明（『オフィシャルブック2000』のページつき）と、印刷の文面との違い
notes = bcr.annotations_for(ctx, 'PMCG1-032')
for ld in notes['latest_descriptions']:
    print(ld['id'], ld['latest_description']['page'], ld['latest_description']['text_ja'], ld['meaning_change'])
# 3. そのカードの裁定（CONFIRMED・SUPPORTED）。複数のカードに共通の裁定も入る
for x in notes['rulings']:
    print(x['id'], x['status'], x['conclusion'])
# 4. 裁定の根拠の一般の規定（条項）
clauses = {c['id']: c for c in ctx['rulings']['rule_clauses']}
for ref in notes['rulings'][0]['rule_clause_refs']:
    print(ref, clauses[ref]['section'])
# 5. 未解決の論点（公式の資料で決められない問い）
for q in notes['issues']:
    print(q['id'], q['question'], q['audit']['game_effect'])   # 結果への影響（監査）
# 6. kyuura-engine の版と裁定の id から、kyuura の記録を引く（版が違えば同じ id でも別の裁定）
print(bcr.find_engine_ruling(ctx, 'v0.6', 'R13'))   # あまごいのあとの通常のエネルギー → 未解決の論点
print(bcr.find_engine_ruling(ctx, 'v0.13', 'S1'))   # こうらがえし（v0.7 の S1 はダメージスワップ）
# 7. 未解決の数（kyuura の論点の数と、エンジンの未解決の裁定・停止コードの数は別の数）
uc = bcr.unresolved_counts(ctx)
print(uc['research_issues'], uc['engine_total'], uc['engine_stop_codes'])
```

7. **エンジンの新しい版を取り込むとき**: `data/sidecar/rulings.json` の `engine_imports` に版ごとの記録を 1 件加え（`ENGINE-<コミットの先頭 7 桁>`。`commit`・`documents`・文書ごとの `ruling_sets`）、範囲のすべての id を記録の `engine_refs` か `not_imported`（理由つき）に結びます。最新の説明・照合・裁定は、[照合済みの記録の再利用手順](docs/engine-readiness.md#10-照合済みの記録の再利用2026-10-15)に従って記録します。原典の確認者と範囲が追えるエンジンの記録は、出所を保って取り込めます。不足する範囲は不足として記録し、画像の確認には自動で進みません（ガイドブックの読み直しは明示的に依頼されたときだけ。2026-10-15 からの方針）。エンジンが kyuura のデータを採用した記録と pcg-search.com との照合は、原典の照合ではないので、照合の記録（`CC-`）として取り込みません（[エンジン開発の準備状況](docs/engine-readiness.md#12-カードデータの信頼と照合の方針2026-10-15) の 12 章）。形式は [docs/data-schema.md の「サイドカー」](docs/data-schema.md#サイドカーdatasidecar)。
8. **検査**: `python3 scripts/build_card_rulings.py --check`（データの検査と、生成したページ [docs/rules/card-rulings.md](docs/rules/card-rulings.md) が最新か）、`python3 -m unittest discover -s tests`。生成したページは手で編集しません（`python3 scripts/build_card_rulings.py` で作り直す）。

**日本語テキストについて**:
- カード名は日英とも全件収録しています。
- ワザ名・特殊能力名・効果文は、英語版は全件、日本版は全 10 弾の 774 枚（効果文のない基本エネルギー 6 枚以外の全カード）を収録しています。
  - 出典は、第1〜4弾と neo 第1〜2弾が [なぞのばしょ](https://nazonobasho.com/)、第5〜6弾と neo 第3〜4弾が [ポケモンWiki](https://wiki.pokemonwiki.com/)（ブラウザで保存したページ）です。
- 無色2個エネルギーの効果文と、neo 第1〜2弾のベイビィ・アンノーン 12 枚のルール文は、なぞのばしょに記載がなく未収録です。詳しくは [カードリストの見かた](docs/cards/README.md#日本語テキストについて) を参照してください。

## 日英のルールの違い（要約）

詳しくは [日米のルールの違い](docs/rules/differences.md) を参照してください。

| 項目 | 日本版（旧裏） | 英語版（WotC） |
|---|---|---|
| 先攻の最初の番のドロー | 1999年の第5版から引ける（第5版がこれを「新ルール」とするので、それより前は引けなかったと読める。発売元のガイドブックの基本の遊びかたには先攻の例外が書かれていない）。2001〜2002年の公式大会は大会専用ルールで引けない | 引ける |
| たねポケモンがいない場合 | 初期は引き直し 2 回まで、3 回目で負け、相手は引かない。1999年の第5版から回数の制限がなくなり、相手が 2 枚まで引ける | 引き直しのたびに、相手は 2 枚まで引ける |
| こんらんでワザ失敗 | 第5版より前は、ワザのダメージと効果を自分が受ける（1997〜1998年の会報で確認）。第5版から自分に 20 ダメージ | 自分に 20 ダメージ |
| 対戦準備のベンチ | 初期は 0〜1 匹（英語資料による）。第5版から 5 匹まで | 5 匹まで |
| サドンデス | 第2版ではおたがいの 7 匹目のポケモンで勝負。1997年11月の第3版から、サイド 1 枚で最初から対戦し直す | サイド 1 枚で対戦し直す |
| 先攻 1 ターン目のワザ・トレーナー | 制限なし | 制限なし（同じ） |
| 1 番ににげられる回数 | 制限なし | 制限なし（同じ） |

**注意**: この資料は、ネットワークに制限のある環境で、ウェブ検索の要約をもとに作り始めました。その後、当時の会報・雑誌・書籍のスキャンと公式サイトの保存版で照合した項目がありますが、ルールブックそのものは第4版の冊子のスキャンだけを読み、ほかの版と印刷物の実物は照合していません。各項目には確度（確実／有力／未確認）を付けています。確度の意味と調べ方の限界は [ルール資料の README](docs/rules/README.md) を参照してください。
