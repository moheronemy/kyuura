# 利用者が指定したひかるバンギラスの処理（エンジン固有の扱い。2026-11-01 の記録）

kyuura-engine の v0.133 に向けて、ひかるバンギラス（neo 第4弾。`neo4-082`）の 2 つのワザ「マウンテンクラッシュ」「はかいのほのお」の処理を**利用者が指定した**記録です。原典の調査・公式の裁定・エラッタ・最新の説明・転記の訂正・画像の照合ではありません。kyuura のカードデータ（印刷の文面の転記）と研究の記録（裁定・論点）は変えていません。

**この記録は実装の計画です。** v0.133 は実装中で、完成・動作の確認はしていません（6 章）。

一覧は [利用者がエンジン用に指定した仕様の一覧](engine-user-specifications.md) にあります。

## 1. 位置づけ

- 分類: 利用者の指定による**エンジンの処理の仕様**（kyuura の sidecar の `engine_positions` でいう `kind: simplification`・`adopted_spec` に当たる性質のもの）。公式の裁定（CR-… の CONFIRMED・SUPPORTED）・最新の説明（LD-…）・エラッタ・転記の訂正・画像の照合（IMG-…）として登録していません。
- この記録のために、カードの画像・『オフィシャルブック2000』・Q&A を新しく確かめていません。カードの文面は kyuura の値、関係する裁定・論点は 2026-10-31 の [プクリン・コインで決まる枚数の不足の調査](wigglytuff-unbounded-shortage-research.md) の記録をそのまま参照しました。
- 日付: 2026-11-01 は kyuura にこの指定を記録した日です。カードの発売日・原典の公表日ではありません。指定は利用者の依頼の中のもので、別の公開資料はありません。

## 2. 対象と印刷の文面

kyuura の値は `data/cards.json`（基点 `9242b9b` の値。この作業で変えていない）からそのまま引用しました。

| 対象 | 必要なエネルギー・ダメージ | 印刷の文面（kyuura の転記。`pokemon.attacks[i].text.ja`） |
|---|---|---|
| `neo4-082` attack0「マウンテンクラッシュ」 | 悪闘闘・30 | 「うら」が出るまでコインを投げつづけ、その間に出た「おもて」の数ぶんのカードを、相手の山札の上からトラッシュする。 |
| `neo4-082` attack1「はかいのほのお」 | 悪炎炎炎・50 | 自分についている「炎」エネルギーカードの枚数ぶんコインを投げ、「おもて」の数ぶんの「炎」エネルギーカードを、自分からトラッシュする。その後、「おもて」の数ぶんの「エネルギーカード」を、相手からトラッシュする。(自分についている「炎」エネルギーカードをトラッシュできないとき、このワザは失敗する。) |

- 印刷は 2026-10-31 にカードの画像（IMG-neo4-082）で転記と同じことを確かめた記録があります。英語版の「If it has fewer Energy cards than that, remove all of them.」に当たる文は日本語の印刷にありません。**この指定の「不足なら残りすべて」は、英語版の文から持ちこんだものではなく、利用者の指定です。**
- 『オフィシャルブック2000』はこのカード（2001 年）より前の本で、このカードの最新の説明・解説はありません。

## 3. 指定された処理

### 3.1 マウンテンクラッシュ

1. 通常どおり基本 30 ダメージを処理する。
2. 山札の残りの数で打ち切らず、「うら」が出るまでコインを投げる。
3. 「おもて」の数と、相手の残りの山札の枚数の**少ない方**だけ、相手の山札の上からトラッシュする。
4. ナツメのESPで投げ直した場合は、最終のコインの結果を使う。
5. 山札が空になっただけでは、その場で負けにしない。

**不足のとき残りすべてをトラッシュする（3）が、この指定で決めた扱いです。** ほかの、数が足りなくなる効果（怪電波マシーン neo4-108・ファイヤーのドライアップ ES2-005・QSG-055 など）へ一律には当てはめません。

### 3.2 はかいのほのお

順番:

1. 必要なエネルギーとは別に、自分に「炎」エネルギーカードが 1 枚以上ついていることを、**宣言の条件**として確かめる。
2. 「炎」エネルギーカードの枚数ぶんコインを投げる。
3. 「おもて」の数だけ、自分の「炎」エネルギーカードをトラッシュする。
4. 基本 50 ダメージを処理する。
5. 「おもて」の数だけ、相手のエネルギーカードをトラッシュする。足りなければ、残っている分すべてを対象にする。

補足（利用者の指定）:

- 「炎」エネルギーカードが 0 枚なら宣言できず、コイン・ダメージ・トラッシュをしない。
- 「炎」エネルギーカードが 1 枚以上あれば、「おもて」が 0 回でも成功する。基本 50 ダメージで、両方のトラッシュは 0 枚。
- 相手が防護されていても（「ダメージを受けない」状態など）、コインと自分の「炎」のトラッシュは行う。
- 相手へのダメージと相手のトラッシュには、それぞれエンジンの既存の防護の規定を当てはめる（この指定で新しい防護の規定を決めない）。
- 数えるのは「炎」エネルギーの個数ではなく、「炎」エネルギーカードの**枚数**。
- 特殊エネルギーの色の判定などは、この指定で新しく決めたことにしない。

## 4. 原文・既存の記録との関係

### 4.1 既存の裁定と同じ内容（指定で新しく決めたものではない）

| 指定 | 既存の記録 |
|---|---|
| マウンテンクラッシュの 1（30 ダメージが先）・5（山札がなくなっても、その時点では負けない） | CR-MOUNTAIN-CRUSH-PROCEDURE（CONFIRMED）。負けは自分の番の最初に引けないとき（p.312） |
| マウンテンクラッシュの 2（打ち切らない） | CR-UNTIL-TAILS-NOT-CAPPED（SUPPORTED） |
| はかいのほのおの 2・3・5 の行き先（自分の「炎」をトラッシュ、相手のエネルギーカードをトラッシュ。手札にはもどさない） | CR-DESTRUCTIVE-FIRE-TEXT（CONFIRMED） |

### 4.2 利用者の指定で決めたこと（原文・既存の記録では決まっていない）

| 指定 | 原文との差 | 関係する論点（**どれも未解決のまま**） |
|---|---|---|
| マウンテンクラッシュの 3: 「おもて」の数と山札の少ない方をトラッシュ | 印刷は「「おもて」の数ぶんのカードを」で、山札が少ないときを書かない。p.312 の「引けるだけ」は引く場面の文 | UQ-STATED-COUNT-SHORT（neo4-082 の事例） |
| マウンテンクラッシュの 4: ESP の投げ直しは最終の結果 | 印刷はやり直しを書かない。ナツメのESP（PMCG6-087）の文面は「もう1度やり直してよい」 | UQ-ESP-REDO。kyuura の記録では、ナツメのESPは「ナツメのポケモン」につけるカードで、この記録はひかるバンギラスにESPがはたらく経路が実在するかを確かめていない（指定は、その経路がある場合の結果の扱い） |
| はかいのほのおの 1: 「炎」エネルギーカード 1 枚以上を宣言の条件にする。0 枚なら宣言できない | 印刷は「トラッシュできないとき、このワザは失敗する」で、使えない（宣言できない）とは書かない。p.323 は失敗しても使ったことになるとする。指定では、0 枚のときはワザを使わない（失敗したワザを使ったことにもならない） | UQ-DESTRUCTIVE-FIRE-FAILURE（N = 0 の場面） |
| はかいのほのおの「おもて」0 回で成功（50 ダメージ・トラッシュ 0 枚） | 「トラッシュできないとき」に「おもて」0 回が当たるかを印刷は書かない。たつまきなどの「すべて「うら」なら失敗」とは書き方が違う | UQ-DESTRUCTIVE-FIRE-FAILURE（N > 0・H = 0 の場面） |
| はかいのほのおの順番: 自分の「炎」のトラッシュ（3）が 50 ダメージ（4）より先 | p.309 の手順 6 はダメージの処理を先、それ以外の効果をあとにする。印刷の文は「…自分からトラッシュする。その後、…相手からトラッシュする。」で、ダメージとの前後を書かない。**この順番は一般の規定の順と違い、利用者の指定によるもの** | UQ-DESTRUCTIVE-FIRE-FAILURE（順番） |
| はかいのほのおの 5: 相手のエネルギーカードが足りなければ残りすべて | 印刷は「「おもて」の数ぶんの「エネルギーカード」を」で、足りないときを書かない。英語版の文は根拠にしていない | UQ-STATED-COUNT-SHORT（neo4-082 の事例） |
| はかいのほのお: 相手が防護されていてもコインと自分の「炎」のトラッシュは行う | 相手への要素が無効なときの、要素の中のコインを書いた原典はない | UQ-COIN-IN-NULLIFIED-ELEMENT・UQ-DESTRUCTIVE-FIRE-FAILURE（相手への要素が無効なとき） |

### 4.3 この指定で決めていないこと

- 特殊エネルギー（レインボーエネルギーなど）・［エネエネ］などでついたカードを「「炎」エネルギーカード」に数えるか、［すごいへんしん］の色の扱い（UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY・UQ-SUPER-TRANSFORM-ENERGY-COLORS）。v0.124 のあとの引き継ぎ 6 章の「Super（すごいへんしん）で色を払えることと「炎」エネルギーカードとして数えることは別」もそのままです。
- トラッシュする自分の「炎」エネルギーカード・相手のエネルギーカードを、どれをだれが選ぶか（指定は枚数と行き先だけを書く）。
- 相手へのダメージ・トラッシュに当てはめる防護の規定の中身（エンジンの既存の規定のまま）。
- ほかのカードの不足の処理（3.1 の最後）。この指定は UQ-STATED-COUNT-SHORT の一般の答えではありません。
- ナツメのESPが 2 枚以上ついているとき・相手のコインなど、UQ-ESP-REDO のほかの事例。

## 5. 変えていないもの

- `data/cards.json` の 1,377 枚の値・id、`data/cards.csv`・`data/attacks.csv`、印刷の文面、訂正の候補。
- `data/sidecar/` の裁定・論点・最新の説明・照合（CR-MOUNTAIN-CRUSH-PROCEDURE・CR-DESTRUCTIVE-FIRE-TEXT・CR-UNTIL-TAILS-NOT-CAPPED・UQ-STATED-COUNT-SHORT・UQ-DESTRUCTIVE-FIRE-FAILURE・UQ-ESP-REDO・UQ-COIN-IN-NULLIFIED-ELEMENT・UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY は基点のまま）。
- `engine_positions`・`engine_imports` には**加えていません**（6 章）。エンジンの登録表の写し（`data/curation/engine_registered_cards.json`。v0.113 のまま）、`data/engine_targets.json`（neo4-082 の 2 つのワザは基点のまま）。
- エンジンのリポジトリ（コードの変更・対戦の実行はしていない）。

## 6. エンジンの実装の状態（2026-11-01 の時点）

**計画だけで、実装は確かめていません。**

- 2026-11-01 に kyuura-engine の公開の ref（`git ls-remote`）を見た時点で、v0.133 のブランチ・コミットはありませんでした。いちばん新しい公開の版は v0.132 `a6c0c955fa66200f8677a87201b3726101383ec5`（`main` の `9f00943` は v0.132 の PR #25 のマージ）です。
- v0.132 の文書（`docs/slowking-mind-games-v0.132.md` の 12 章）は、ひかるバンギラス neo4-082 を未登録のまま残る対象として挙げています（固定したコミットを `git show` で読んだ。作業中のツリーは読んでいない）。
- v0.133 の版・コミット・検査・テストの結果は**未確定**です。予定の版の番号を、完成した実装として記録していません。

### 実装が完成したあとに取り込むときに要るもの

`engine_positions` に記録する（`kind: simplification` か `adopted_spec`）には、次を確かめます。今回はどれも**未確定**です。

1. エンジンの完成した版の固定コミット（公開されたもの）と、その版の取り込み `engine_imports`（`ENGINE-<先頭 7 桁>`）。
2. 版の文書の中でこの仕様を書いた節（`document`・`section`）。
3. 登録（効果の登録表の (カード id, ワザの位置)）・利用者の指定の記録・検査とテストの場所。結果はエンジンの報告によるものと書く。
4. 3 章の指定とエンジンの実装が同じか。違えば、利用者の指定とエンジンの実装を分けて書く。
5. 4.2 節の論点が、kyuura では未解決のままであること（`kyuura_handling`: 「エンジンが採用した利用者の指定で、公式のエラッタ・最新の説明・裁定ではない。UQ-STATED-COUNT-SHORT・UQ-DESTRUCTIVE-FIRE-FAILURE は未解決のまま。kyuura のカードデータは印刷の文面のまま」）。

## 7. 完成後の経過（2026-11-02 日本時間の追記。v0.133 の完成と実装の確認）

1〜6 章は変えていません。6 章の「計画だけで、実装は確かめていません」「v0.133 のブランチ・コミットはありませんでした」は、2026-11-01 の記録の時点の状態として残します。この章は、そのあとの経過です。3 章の利用者の指定は変えていません。

### 7.1 確かめたエンジンの版

| 項目 | 値 |
|---|---|
| 版 | v0.133（版 0.133.0） |
| 公開のブランチ | `claude/v0.133-shining-tyranitar`（2026-11-02 の `git ls-remote` で先頭が下のコミット） |
| 最終コミット | `298f08d603c1f763fc45a97fc306291d8b95abb0`（親 `0aa97c4`。基点は `main` の `9f009436733ad0b060d8a22a7bddad26fe73ff3e`。`main` にはまだ入っていない） |
| 版の文書 | `docs/shining-tyranitar-v0.133.md`（3 章 利用者が指定した規則、4〜6 章 処理、9 章 単体のテスト、10〜11 章 対戦と検証、12 章 数・制限・kyuura への報告事項） |
| 途中のコミット（文書 12.3 の 3） | エンジン `db050cc`・テストの期待 `c08177f`・道具 `65c13a1`・`f8565a1`・監査の直し `1d66fd9`・全体の実行のあとのテストの直し `0aa97c4` |

確かめ方: 固定コミットを kyuura とは別の場所に `git fetch` し、`git show`・`git grep`・`git diff` で読んだだけです（読み取りだけ）。エンジンの作業中のツリーは読んでいません。エンジンのコードの実行・テストの実行・対戦はしていません。

### 7.2 コードで確かめた場所（`298f08d` の木）

| 対象 | 場所 |
|---|---|
| 登録 | `kyuura_engine/effects.py` の `V0_133_ATTACKS`: `AttackKey("neo4-082", 0)` → `DamageThenMillOpponentUntilTailsUpToDeck`、`AttackKey("neo4-082", 1)` → `CoinsPerOwnTypedCardsDiscardThenDamageThenOpponentEnergy`（どちらも印刷の文面 `_printed(...)`。最新の説明はない） |
| 利用者の指定の記録 | `kyuura_engine/effects.py` の `USER_SPECIFIED_RULES["neo4-082/attack/0"]`（種類 `USER-MOUNTAIN-CRUSH-MILL-UP-TO-DECK`、解決済みにしない論点 `UQ-STATED-COUNT-SHORT`）・`["neo4-082/attack/1"]`（種類 `USER-DESTRUCTIVE-FIRE-DECLARE-ORDER-UP-TO`、論点 `UQ-DESTRUCTIVE-FIRE-FAILURE`、関係する論点 `UQ-STATED-COUNT-SHORT`）。どちらも `text_difference`（印刷の文面と採用した処理の差）と「記録しない扱い」（公式の裁定・最新の説明・エラッタ・転記の訂正・論点の解決）を持つ。登録の型は記録と同じ印刷の文面のときだけ登録できる（`_attack_rule_problems`） |
| 要素の並び | `kyuura_engine/resolution/programs.py` の表（15909〜15914 行）: マウンテンクラッシュ `Damage(OPP, Printed())` → `MillOpponentDeckUntilTailsUpTo`、はかいのほのお `OwnTypedEnergyCardsRequired(FIRE)` → `Coin("coin", per_attached=FIRE)` → `DiscardOwnTypedEnergyByHeads` → `Damage(OPP, Printed())` → `DiscardOpponentEnergyUpToHeads` |
| 共通の処理 | `kyuura_engine/resolution/programs.py` の `MillOpponentDeckUntilTailsUpTo`（`run.flip_until_tails` で「うら」まで、山札の枚数 D はコインの前に数え、`min(H, D)` 枚を `zones.discard_from_deck`、H > D ならログ `user_rule_count_short`。負けの判定は加えていない）・`capped_classes`（先読みの組）・`note_count_short`・`OwnTypedEnergyCardsRequired`・`DiscardOwnTypedEnergyByHeads`・`DiscardOpponentEnergyUpToHeads`（`min(H, M)` 枚。M = 0 も不足の記録）・`kind_grouped_answers`。宣言の条件 `kyuura_engine/effects.py` の `typed_energy_card_usage_problem`（`IllegalActionError("NO_TYPED_ENERGY_CARDS")`。`kyuura_engine/checks.py` の `usage_problem` の呼び出しから） |
| 記録・対応表 | `kyuura_engine/data/card_sources.json` の `neo4-082`（`user_specified_rule`）、`kyuura_engine/data/research_links.json`（`latest_descriptions.user_specified_rules`・事例の扱い `user_specified_rule`） |
| 検査 | `scripts/check_card_sources.py` の `user_specified_rule_problems`（ワザの対象では `text_difference` を必ず書く）・`scripts/check_research_links.py` の 4f-3 |
| 監査 | `tests/log_audit.py` の `v133_problems`・`v133_snapshot` |
| テスト | `tests/test_shining_tyranitar_v0_133.py`（32 件。`RegistrationTest`・`MountainCrushTest`・`DestructiveFireTest`・`PersistenceAndAnswersTest`・`AuditTamperingTest`・`DocumentTest`） |

### 7.3 指定と実装の照合

| 指定（3 章） | コード・テストで確かめたこと | 判定 |
|---|---|---|
| マウンテンクラッシュ: 基本 30 のあと、「うら」まで投げる | 要素の並びが `Damage` → `MillOpponentDeckUntilTailsUpTo`。テスト `test_damage_first_and_deck_out_only_at_draw` | 一致 |
| 山札の枚数でコインを打ち切らない | `MillOpponentDeckUntilTailsUpTo.run` は D を数えたあと `flip_until_tails` で投げ、D で打ち切る分岐がない。テスト `test_heads_against_deck_sizes`（山札 0 枚でも「うら」まで） | 一致 |
| 「おもて」の数と山札の少ない方をトラッシュ | `count = min(heads, available)`。H > D で `user_rule_count_short` | 一致 |
| 山札が空になっただけでは負けにしない | 要素に負けの判定がない。テスト `test_damage_first_and_deck_out_only_at_draw`（山札切れは相手の番の最初に引くとき） | 一致 |
| ESP の投げ直しは最終の結果 | 共通のやり直しの処理。テスト `test_esp_short_to_enough_and_back` | 仕組みは一致。**経路は 7.5 節** |
| はかいのほのお: 炎エネルギーカード 0 枚なら宣言できない | `typed_energy_card_usage_problem`（`attached_basic_energy` が 0 なら拒否）。テスト `test_no_fire_cards_is_rejected_without_change`（状態・乱数・ログが変わらない） | 一致（色の読み方で枚数が変わりうるときは拒否せず既存の停止。7.6 節） |
| 炎エネルギーカードの枚数ぶんコイン（個数ではない） | `Coin(per_attached=FIRE)` と宣言の条件が同じ `attached_basic_energy`（基本エネルギーカードの枚数） | 一致 |
| 「おもて」の数だけ自分の炎をトラッシュ → 50 → 相手のエネルギーカード | 要素の並び（7.2 節）。テスト `test_order_and_opponent_counts` | 一致 |
| 相手が足りなければある分すべて | `DiscardOpponentEnergyUpToHeads.run` の `min(heads, len(options))`、すべてなら決定なし。テスト `test_order_and_opponent_counts`（多い・同じ・少ない・0 枚） | 一致 |
| 炎 1 枚以上なら「おもて」0 回でも成功 | 「おもて」0 は自分・相手とも 0 枚で、失敗の分岐がない。テスト `test_zero_heads_succeeds` | 一致 |
| 防護があってもコインと自分の炎のトラッシュは行い、ダメージと相手のトラッシュはそれぞれ既存の防護 | 相手のトラッシュは `reaches`・`_voided`（既存の効果の防護）、ダメージは既存の `Damage`。テスト `test_damage_only_protection`・`test_effect_protection_keeps_own_discard`・`test_keep_voids_only_the_opponent_discard` | 一致 |

実装が指定に加えた・具体化したこと（**利用者の指定として kyuura に記録したものではない**。エンジンの実装・既存の規定の当てはめ）:

- トラッシュする自分の炎・相手のエネルギーカードは、ワザを使ったプレイヤーが選ぶ（決定 `DISCARD_ENERGY`・`DISCARD_OPPONENT_ENERGY`）。エンジンの文書 3.2 節は指定の文を「選んでトラッシュする」と引きますが、kyuura の 3 章の指定は選ぶ人を書いておらず、4.3 節の「この指定で決めていないこと」のままです。
- マウンテンクラッシュで、相手の対戦ポケモンへの防護を相手の山札に当てはめない（文書 3.1 節・4 章。v0.115 のやまくだき `MillOpponentDeck` と同じ既存の扱い）。kyuura の 3 章の指定には含まれていません。
- はかいのほのおで相手がこのワザで HP 以上になったら、相手のトラッシュは処理しない（p.309。親の型と同じ）。

### 7.4 エンジンの報告（kyuura は実行していない）

次は、エンジンの版の文書（11 章・10 章）とコミットの文による**エンジンの報告**です。kyuura が実行した結果ではありません。

- 全体のテスト（コミット `f8565a1` の木。2026-11-01 23:11:07〜2026-11-02 00:21:01 日本時間）: 247 モジュール・7,208 件、**失敗 2**・エラー 0・スキップ 1（既知: `tests.test_cross_version_compatibility.FullComparisonTest.test_no_differences`。`KYUURA_COMPAT_BASE` を設定したときだけ）・時間切れ 0。
- 直したあとの追加の再実行（`0aa97c4` の木）: 3 モジュール・82 件（`test_counter_keep_energy_protection_v0_101` 41・`test_cross_version_compatibility` 9（スキップ 1）・`test_shining_tyranitar_v0_133` 32）、失敗 0・エラー 0。
- 最後に加えたテスト 1 件をふくむ総数は 7,209 件ですが、**その状態で全体は再実行していません**（文書 11.4 節）。
- lockstep（v0.132 `a6c0c95` の木と `f8565a1` の木）: 290 対戦・48,092 歩・食い違い 0。ひかるバンギラスは lockstep の組に入らないので、新しい経路はこの比べを通っていません。
- 前の版の組: 11 版・632 局、差 0（所要時間と鍵 `v133` だけを除いた比べ）。
- 正式な対戦（2 回目。`f8565a1` の木）: 28 局・2,809 歩。通常の終局 27・従来の停止 1（X133 どうしの seed 3。対戦準備の `UNRESOLVED_MULLIGAN_COMPENSATION`。v0.1 からの既存の停止）。内部エラー 0・予期しない拒否 0・監査の失敗 0。

報告と文書の差・補足:

- 引用した数（247・7,208・失敗 2・エラー 0・スキップ 1、3 モジュール・82 件、7,209 件で全体を再実行していない、290 局・48,092 歩・差 0、11 版・632 局・差 0、28 局・内部エラー 0・監査の失敗 0・既存の準備段階の停止 1）は、固定コミットの文書と同じでした。632 局は文書 11.3 節の表の 11 版の局の和（32+32+24+108+104+96+80+32+48+40+36）と合います。82 件は 41+9+32 と合います。
- 正式な対戦は **2 回目**の結果です。文書 10 章によると、同じ計画の 1 回目（`65c13a1` の木）は 28 局で内部エラー 1・監査の失敗 1 で、原因は道具（手札を隠した写しで方策を試した）と監査（こんらんのコインをワザのコインに数えた）で、エンジンではないと報告されています。直したあと同じ計画で 2 回目を走らせ、両方を記録したと書かれています（選び直していない）。
- 文書 10 章に「13.3 節で確かめた」とありますが、文書に 13 章はありません（文書の中の参照の誤りと読める。11.3 節の前の版の組のことか）。

### 7.5 全体のテストの失敗 2 件（実際の差分で確かめた範囲）

- **v0.101 の確かめ**（`tests.test_counter_keep_energy_protection_v0_101.SharedCoinTest.test_no_shared_coin_decides_an_opponent_energy_discard`）: `git diff f8565a1 0aa97c4` で、このテストに、はかいのほのお（`AttackKey("neo4-082", 1)`）だけを名前つきの例外にする 9 行の変更（例外の要素が `USER_DESTRUCTIVE_FIRE_RULE` を持つことを確かめる。ほかのワザの確かめはそのまま）があり、`tests/test_shining_tyranitar_v0_133.py` に［KEEP］のテスト（`test_keep_voids_only_the_opponent_discard`）を加える 13 行の変更があることを確かめました。エンジンのコード（`kyuura_engine/`）はこのコミットで変わっていません。
- **compat_driver.py の指紋**（`tests.test_cross_version_compatibility.FixtureComparisonTest.test_fixture_was_made_by_this_driver_from_the_base`）: `git diff 9f00943 298f08d -- tools/compat_driver.py` は空で、リポジトリの内容は基点から変わっていません。原因が作業ツリーの CRLF による指紋の不一致だったこと（`7275c3cd…` と `05d4a802…`）は**エンジンの報告**で、作業ツリーの改行はコミットに残らないので、kyuura はコミットからは確かめられません。

### 7.6 残る制限（実装の記録とは別に保持する）

- 特殊エネルギーなどで「炎」エネルギーカードの枚数が色の読み方で変わりうるとき（レインボーエネルギー RB1・［エネエネ］BZ2・ミラクルエネルギー MEC1・色を変えたカード CE3・［へんしん］TE1・［すごいへんしん］SV5）は、既存の停止が残ります（`typed_energy_card_reading_open` が真なら宣言の条件では拒否せず、コインの前の既存の止め方）。UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY・UQ-SUPER-TRANSFORM-ENERGY-COLORS は決めていません。
- コピー（相手のワザとして使う）で説明が条件を書かないときは、既存の HC9 などの制限が残ります（`OwnTypedEnergyCardsRequired.copy_problem`）。
- 既存の不足時の停止（たつまき FC1・ドライアップ DU1・怪電波マシーン TW1・TW2・HC6・MW1・FU1 など）は変えていません。コードで確かめたのは、記録の範囲の文（「ほかのカードの…不足に広げない」）と、テスト `test_other_shortage_types_keep_their_stops`（登録表のほかのワザの要素が v0.133 の新しい要素を使わない・たつまきは親の型 `DiscardOpponentEnergyByHeads` のまま）です。途中停止からの再開が未対応のまま変わっていないことは、文書 12.1 節の**エンジンの報告**です（kyuura はコードで確かめていない）。**「足りなければあるだけ」は、この 2 つのワザだけ**です。
- 正式な対戦では、マウンテンクラッシュの山札の不足は 0 回でした（エンジンの報告。文書 10 章の表）。山札の不足と山札切れまでの流れは単体のテストだけです。
- 炎エネルギーカード 0 枚の宣言の拒否とナツメのESPは、正式な対戦では 0 回で、単体のテストだけです。
- **ナツメのESPの経路は確認済みとしません。** ESPのテスト（`test_esp_short_to_enough_and_back`・`test_esp_replaces_only_the_coins`）は、v0.113 のテストの `esp_board` を使います。ナツメのESP（PMCG6-087）は手札から `PlayTrainer` でナツメのフーディン（PMCG6-053。［サイコリンク］）につけていますが、ベンチのひかるバンギラスの「超」の色は、`build_test_state` で**色マーカー（`MARKER_COLOR`・超）を直接のせた盤面**です。悪タイプのひかるバンギラスを［サイコリンク］の「自分の場の「超」ポケモン」にするカードの経路は、テストでは再現していません。したがって、このテストは ESP のやり直しの**仕組み**（最後の並びを使う・ダメージはくり返さない）の確認で、実在するカードの経路で起こることの確認ではありません。経路が実在するかは、この記録では確かめていません。
- 研究の論点はどれも未解決のままです: UQ-STATED-COUNT-SHORT・UQ-DESTRUCTIVE-FIRE-FAILURE・UQ-ESP-REDO・UQ-COIN-IN-NULLIFIED-ELEMENT・UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY・UQ-SUPER-TRANSFORM-ENERGY-COLORS。

### 7.7 エンジンの報告事項（12.3 節）のうち、この記録に関わるもの

- 12.3 の 2「kyuura には今回の指定の記録はない（71d1728・9242b9b とも）」: その 2 つのコミットには記録がありません。この記録（1〜6 章）は 2026-11-01 に作業ブランチ `claude/eloquent-lamport-5xyv5r`（コミット `5780108`）に加えたもので、記録の時点で kyuura の `main` には入っていません。エンジンはこの記録を読まずに実装しています。3 章の指定と、エンジンの文書 3 章の指定の文は、7.3 節の 2 点（選ぶ人・山札への防護）のほかは同じ内容でした。
- 12.3 の 5「kyuura の登録表の写しが v0.113 のまま」・12.3 の 6（ほかの版の利用者の指定）は、この記録の範囲の外です（登録表の写し・ほかのカードの記録は変えていない）。

### 7.8 この追記で変えていないもの

- 3 章の指定・4 章の原文との差・5 章・6 章。
- `data/cards.json`・CSV・印刷の文面・訂正・`data/sidecar/`（裁定・論点）・`data/engine_targets.json`（neo4-082 は基点のまま）・登録表の写し（v0.113）。
- `engine_positions`・`engine_imports` には、今回も加えていません。取り込むときに要るもの（6 章の 1〜5）のうち、固定コミット（1 の前半）・文書の節（2）・登録と検査の場所（3）・照合（4）はこの章で分かりましたが、版の取り込み（`engine_imports`。v0.69〜v0.132 は取り込んでいない）は今回の範囲の外です。
