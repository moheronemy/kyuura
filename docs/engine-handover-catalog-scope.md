# 目録の分類と通常対戦の対象の引き継ぎ（2026-10-31）

kyuura-engine への引き継ぎです。調査と整備の記録は [プロモの収録範囲の調査と目録の整備](catalog-promo-survey.md)。**kyuura はエンジンを変えていません。** エンジンの登録表の写し（`data/curation/engine_registered_cards.json`。v0.113 `2d113b5`）も書き換えていません。kyuura の分類を変えただけで、エンジン側が対応したことにはなりません。下の 2〜4 章は、エンジンの写しの元（`KYUURA_COMMIT`）をこの作業のコミットに上げるときに、エンジン側で確かめることです。

## 1. 採用するコミットと変わるもの

- kyuura のコミット: この作業の最後のコミット（ブランチ `claude/eloquent-lamport-5xyv5r`）。基点は `0dadab8`。
- `data/cards.json` の `cards`: **記録の集合・順番・id・既存の欄の値は変わりません**（1,377 件）。全記録に 3 つの欄が加わります。
  - `catalog_class`: 目録の分類（`battle`・`special_rule`・`award`）
  - `engine_scope`: 通常対戦のエンジンの実装の対象か（`target`・`excluded`・`undecided`）
  - `engine_scope_reason`: 対象でない理由（`target` なら `null`）
- `schema_version` は 3 のまま（欄を足しただけ）。
- `data/cards.csv` は目録の一覧になり、`data/cards.json` にない行（`non_game_items` の 18 と `KC-` の 24）と、後ろに 6 つの欄が加わりました。**エンジンは CSV を読まないので、エンジンの写しには影響しません**（エンジンが CSV を読むように変えるなら、`catalog_class` が `battle` で `engine_scope` が `target` の行だけを選んでください）。
- 非対戦の項目（入賞賞品カード・ジャンボカード・おすすめルールのカードなど）は `data/cards.json` に入れていません。エンジンの写しに入ることはありません。

## 2. 対象から外した 3 枚（利用者の指定）

| id | 名前 | `catalog_class` | `play_scope` | `engine_scope` | v0.113 の写しの登録 |
|---|---|---|---|---|---|
| `PR1-038` | タッチ交代！ | `special_rule` | `kangaskhan_rule` | `excluded` | 対戦用のカード id にない（未登録） |
| `PRN-048` | タッチ世代交代！ | `special_rule` | `kangaskhan_rule` | `excluded` | 未登録 |
| `PR1-079` | カードトレーナー認定証 | `award` | `standard` | `excluded` | 未登録 |

- 目録の分類と実装範囲の指定で、公式の裁定・エラッタ・印刷の訂正ではありません。カードの記録・文面・出典・id は残っています。
- タッチ系の 2 枚は専用ルール（ガルーラルール・新ガルーラルール）で使うカードです。「遊べない」「公式に使用禁止」のカードとして扱わないでください。専用ルールを実装するかは別の判断で、今回の指定は**通常対戦**のエンジンの対象から外すことです。
- kyuura の `data/engine_targets.json` では、3 枚を `cards` から `excluded_records` に移しました。未実装の件数（`new_effect_needed`）は 121 から 118 になり（3 枚とも `new_effect_needed` だった）、`special_rule_design` は 4 から 2（`PR1-027`・`PR1-073`。公式大会で使えないと書かれたカード。分類は変えていない）になりました。これは kyuura の一覧の数で、エンジンの数ではありません。

## 3. エンジンで確かめること

1. **写しの欄**: v0.5 の時点の `scripts/extract_kyuura_cards.py` は、決まった欄（`FIELDS`）だけを写していました（今の版は kyuura から確かめていない）。新しい 3 つの欄を写しに入れるか、入れないかを決めてください。入れない場合、エンジンの写しは変わりません（3 枚の記録の写す欄の値は基点と同じ）。
2. **カードの分類（`cards.py`）**: 3 枚は v0.113 の登録表で対戦用のカード id ではありません。エンジンの分類が「未対応のカード」として数えているなら、kyuura の指定に合わせて「対象外（理由つき）」として別に数えるかを決めてください。kyuura の `engine_scope` を、エンジンが自動で読んで分類を変えるかどうかも、エンジン側の設計です。
3. **デッキの検査**: 通常対戦のデッキの検査で 3 枚をどう拒否するか（未対応のカードとしてか、対象外としてか）と、そのエラーコード。kyuura は「使用禁止」とは決めていません。
4. **件数の報告**: エンジンの未実装・未対応の件数に 3 枚を数えているなら、内訳を分けてください。kyuura の目録だけの行（`KC-`・`non_game_items`）は、もともとエンジンの写しにないので数に入りません。
5. **とりかえっこプリーズ `PR1-027`・カスミのてあて `PR1-073`**: `play_scope` は `not_for_official_tournaments` のまま、`catalog_class` は `battle`、`engine_scope` は `target` です（変えていない。`PR1-027` の所有者の簡略仕様は [利用者が採用した簡略仕様](engine-user-swap-ownership.md)）。

## 4. 変わらないこと

- 既存のカードの値・文面・訂正の記録・照合の記録・サイドカー（最新の説明・裁定・論点）は変わっていません（`tests/test_catalog_scope.py` が基点と比べる）。
- `PR1-015` ポケモンイラストレーター（`non_game_items`）、`PR1-074` トロピカルウインド（対戦用）の扱いは変わっていません。
- 新しく加えた `KC-` の項目（入賞賞品カード 15・スペシャルジャンボカード 8・トロピカルプレゼント 1）は、どれも `engine_scope` が `excluded` です。エンジンの対象の候補ではありません。
