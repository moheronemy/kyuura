# データの構造（`data/cards.json`）

`data/cards.json` は、旧裏の拡張パック 10 弾の全 780 枚を、日本版を基準に 1 枚 1 レコードで収録した構造化データです。`scripts/build_cardlist.py` で生成しています。

## 全体

```json
{
  "schema_version": 2,
  "description": "...",
  "text_availability": {"en": "...", "ja": "..."},
  "cards": [ { ...カード... } ]
}
```

## カード

| フィールド | 型 | 内容 |
|---|---|---|
| `id` | 文字列 | カード id。TCGdex の日本版 id（例 `PMCG1-011`、`neo4-113`） |
| `jp_set` | 文字列 | 日本版の弾。`PMCG1`〜`PMCG6`（第1〜6弾）、`neo1`〜`neo4` |
| `seq` | 整数 | 弾の中の通し番号。カードに印刷された番号ではない |
| `category` | 文字列 | `pokemon`／`trainer`／`energy` |
| `name` | 日英 | カード名 `{"ja": "フシギバナ", "en": "Venusaur"}` |
| `name_ja_confidence` | 文字列 | 日本語名の確度。`確実`／`有力`／`未確認`。日本語名がなければ `null` |
| `rarity_jp` | オブジェクト | 日本版のレアリティ（下記） |
| `en_print` | オブジェクト／null | 対応する英語版カード（下記）。英語版がないカードは `null`（そのカードの `pokemon` の値は日本語の出典から埋め、英語の欄は `null`） |
| `en_reprints` | 配列 | 英語版の別セットへの再録 `[{"set_id", "set_name", "number", "differences"}]`。ポケモンは英語名・HP・ワザ名・ポケモンパワー名が同じもの、トレーナー・特殊エネルギーは英語名が同じもの。`differences` は英語版データの上で元のカードと違う欄（`cost`・`damage`・`text`・`weakness`・`resistance`・`retreat`）。判定と点検の結果は [再録カードの対応付け](cards/reprints.md) |
| `pokemon` | オブジェクト／null | ポケモンのデータ（下記）。ポケモン以外は `null` |
| `trainer` | オブジェクト／null | トレーナーのデータ（下記） |
| `energy` | オブジェクト／null | エネルギーのデータ（下記） |
| `jp_en_differences` | 配列 | このカードの日英の違い（下記）。[カードの日英の違い](cards/card-differences.md) と同じ内容 |
| `notes` | 文字列の配列 | 備考 |
| `source_ids` | オブジェクト | 出典データでの id `{"tcgdex": "...", "pokemontcg": ["base1-15"]}` |
| `ja_text_source` | 文字列／null | 日本語テキスト（ワザ名・特殊能力・効果文）の出典。なぞのばしょ・ポケモンWiki のカードページの URL。未収録なら `null` |
| `jp_print` | オブジェクト／null | 日本版の印刷についての情報（下記）。なぞのばしょ・ポケモンWiki にカードページがあるカードだけ |

### 日英の値

名前や文面は、日本語と英語を並べたオブジェクトです。

```json
{"ja": null, "en": "Energy Trans"}
```

- `ja`: 日本版の文面。第1〜4弾と neo 第1〜2弾はなぞのばしょ、第5〜6弾と neo 第3〜4弾はポケモンWiki の転記から取り込み済み。出典にないもの（無色2個エネルギーの効果文、neo 第1〜2弾のベイビィ・アンノーンのルール文）は `null`（[詳細](cards/README.md#日本語テキストについて)）。
- `en`: 英語版（WotC 版）の文面。

### `rarity_jp`

| フィールド | 内容 |
|---|---|
| `code` | `common`／`uncommon`／`rare`／`holo_rare`／`special`（通常の構成に当てはまらないもの） |
| `mark` | 日本版の記号 `●`／`◆`／`★`。`special` は `null` |
| `holo` | キラ（ホロ）の版があるか |
| `source_label` | 出典データ（TCGdex）の表記そのまま |

### `jp_print`

なぞのばしょ・ポケモンWiki のカードページの記載です。

| フィールド | 内容 |
|---|---|
| `level` | 日本版のレベル（LV.）。英語版データのレベルには誤りがあるため、レベルはここだけに持たせています |
| `rarity` | サイトのレアリティ表記（例 `★(R)`） |
| `series` | 収録商品（例 `第1弾拡張パック、スターターパック`）。ポケモンWiki は弾の名前（例 `闇からの挑戦`） |
| `remarks` | 印刷についての備考の配列（例 `初版はレアリティマークなし`）。ポケモンWiki には備考の欄がないため空配列 |
| `source` | カードページの URL |

### `en_print`

| フィールド | 内容 |
|---|---|
| `set_id` | 英語版セットの id（pokemon-tcg-data の id。`base1`＝Base Set など） |
| `set_name` | 英語版セット名 |
| `numbers` | カード番号の配列。同じセットにホロ版とノーマル版がある場合は 2 つ |
| `differs_from_primary` | この弾の主な対応セットとは別のセットに入っているなら `true` |

### `pokemon`

| フィールド | 型 | 内容 |
|---|---|---|
| `dex` | 整数の配列 | 全国図鑑番号 |
| `stage` | 文字列 | `basic`（たね）／`stage1`（1進化）／`stage2`（2進化）／`baby`（ベイビィ） |
| `evolves_from` | 日英／null | 進化元のカード名 |
| `hp` | 整数 | HP |
| `types` | 文字列の配列 | タイプ（下の列挙値） |
| `weaknesses` | 配列 | 弱点 `[{"type": "fire", "operator": "×", "value": 2}]` |
| `resistances` | 配列 | 抵抗力 `[{"type": "psychic", "operator": "-", "value": 30}]` |
| `retreat_cost` | 整数 | にげるためのエネルギーの数 |
| `rules_text` | 日英／null | ベイビィ・ひかるポケモン・アンノーンなどのルール文 |
| `powers` | 配列 | ポケモンパワー（下記） |
| `attacks` | 配列 | ワザ（下記） |

#### `powers` の要素

```json
{
  "kind": "pokemon_power",
  "name": {"ja": null, "en": "Energy Trans"},
  "text": {"ja": null, "en": "As often as you like during your turn ..."}
}
```

`kind` は旧裏期の範囲では常に `pokemon_power`（ポケモンパワー）です。

#### `attacks` の要素

```json
{
  "name": {"ja": null, "en": "Solarbeam"},
  "cost": ["grass", "grass", "grass", "grass"],
  "cost_total": 4,
  "damage": {"base": 60, "modifier": null, "display": "60"},
  "text": {"ja": null, "en": null}
}
```

| フィールド | 内容 |
|---|---|
| `cost` | 必要なエネルギーを 1 個ずつ並べた配列（タイプの列挙値） |
| `cost_total` | エネルギーの合計数 |
| `damage` | 威力。ダメージを書いていないワザは `null` |
| `damage.base` | 数値部分。数値がない場合は `null` |
| `damage.modifier` | `null`（固定）／`+`（以上、効果で増える）／`×`（倍数）／`-`（効果で減る）／`?`（数値なし） |
| `damage.display` | カードの表記そのまま（例 `30+`、`10×`） |
| `text` | 効果文。効果のないワザは `en` も `null` |

### `trainer`

```json
{"kinds": ["stadium"], "text": {"ja": null, "en": "..."}}
```

`kinds` の値は次のとおり。下位区分のない普通のトレーナーは空配列です。

| 値 | 内容 |
|---|---|
| `stadium` | スタジアム |
| `pokemon_tool` | ポケモンのどうぐ |
| `rockets_secret_machine` | ロケット団秘密メカ（英語版の区分 Rocket's Secret Machine。日本語の区分名はポケモンWiki の闇からの挑戦・闇、そして光へ... のカードの分類による） |
| `goldenrod_game_corner` | 英語版の区分 Goldenrod Game Corner（日本語の区分名は未確認） |

### `energy`

```json
{"kind": "basic", "provides": ["grass"], "text": null}
{"kind": "special", "provides": [], "text": {"ja": null, "en": "..."}}
```

特殊エネルギーの供給するタイプは `text` に書かれているため、`provides` は空です。

### `jp_en_differences` の要素

```json
{
  "kind": "text",
  "summary": "ポケモンパワー Mind Games の使える場所",
  "ja": "ヤドキングがバトル場にいるときだけ使える（二次資料による）",
  "en": "バトル場の条件がなく ...",
  "confidence": "有力",
  "sources": ["X3", "X15"]
}
```

`kind` は `text`（文面の意味）／`numbers`（数値）／`errata`（後年のエラッタ）／`regulation`（大会のレギュレーションでの扱い。印刷の文面は同じ）／`placement`（収録先）／`print`（英語版の表記・誤植）／`wording`（書き方の違い。効果は同じだが、説明を書いている場所や分け方が違う）／`art`（イラストの違い）。`sources` の記号は [出典と確認状況](sources.md) を参照。

## タイプの列挙値

| 値 | 日本語 |
|---|---|
| `grass` | 草 |
| `fire` | 炎 |
| `water` | 水 |
| `lightning` | 雷 |
| `psychic` | 超 |
| `fighting` | 闘 |
| `colorless` | 無色 |
| `darkness` | 悪 |
| `metal` | 鋼 |

## 表形式の写し

| ファイル | 1 行の単位 | 主な列 |
|---|---|---|
| `data/cards.csv` | カード 1 枚 | `id`、名前（日英）、レア、英語版、進化、HP、タイプ、弱点、抵抗力、にげる、トレーナー・エネルギーの区分と本文（日英）、日英の違い |
| `data/attacks.csv` | ワザ 1 つ | `card_id`、`index`、名前（日英）、`cost`（列挙値を空白区切り）、`cost_total`、`damage_base`、`damage_modifier`、`damage_display`、効果文（日英） |
| `data/powers.csv` | ポケモンパワー 1 つ | `card_id`、`index`、`kind`、名前（日英）、本文（日英） |

## `data/rule_differences.json`

日米のルールの違いのデータです。`items` の各要素が 1 項目で、`jp`・`en` にそれぞれ時期ごとのルール、`status` に判定（`違う`／`時期により違う`／`違う可能性あり`／`同じ`／`不明`）があります。[日米のルールの違い](rules/differences.md) はこのファイルから `scripts/build_rule_differences.py` で生成しています。

`jp`・`en` の各行（と `misconceptions` の行・`later_rules` の行）の欄:

| 欄 | 内容 |
|---|---|
| `period` | 時期。基本ルールと大会のルールは行を分ける（例:「2002年の公式大会」） |
| `rule`・`confidence`・`sources` | ルールの内容、確度、出典の記号（docs/sources.md） |
| `refs` | 関連する `data/rule_history.json` の id（任意）。存在しない id はエラー |
| `confidence_note` | `refs` の記録より確度を低くしている理由（任意）。範囲が違うなどの理由がないまま確度が低いと、確度の更新漏れとしてエラーになる |

`misconceptions` の `later_rules_note` は、後のルールの表の前に置く説明文です（任意）。

日本版の版の時期の表（以前の `jp_periods`）は、このファイルではなく `data/rule_history.json` の `jp_editions` から生成します。

## `data/rule_history.json`

旧裏期（1996〜2003年）のルール・大会レギュレーション・エラッタと、その根拠にした印刷物を記録する調査データです。次の 3 つはこのファイルから `scripts/build_rule_history.py` で生成します。

- [カードの文面の変更とエラッタの履歴](rules/errata-history.md)（`events`・`entries`・`errata`）
- [日本版のルールの版ごとの比較](rules/japanese-editions.md)（`jp_editions`・`jp_edition_matrix`）
- [印刷物の照合記録](printed-sources.md)（`documents`）

[旧裏・新裏の混合ルール](rules/mixed-2002.md)・[新ガルーラルール](rules/kangaskhan-2002.md)・[日本版のルールと変遷](rules/japanese.md) は手書きでこのファイルの id を参照します（参照切れは同じスクリプトが検査）。

| キー | 内容 |
|---|---|
| `categories` | 区分: `basic_rule`（基本ルール）、`tournament_regulation`（大会レギュレーション）、`card_ruling`（カード個別の裁定）、`official_errata`（公式エラッタ。このリポジトリの分類で、当時の資料が「エラッタ」と呼んだとは限らない）、`printed_text_change`（印刷テキストの変更）、`product_change` |
| `evidence_kinds` | 根拠の種類: `original`、`archived_official`（当時の公式サイトのページを Internet Archive の写しで読んだ）、`scan_image`（当時の印刷物のページの写真・スキャンで文面を確認した）、`card_image`、`official_later`、`secondary_direct`、`search_summary` |
| `confidence_values` | 確度（確実／有力／未確認）の基準 |
| `events` | 商品の発売・大会・雑誌の発行などの出来事（`id`、`date`、`region`、`type`、`name`、`notes`、`evidence`）。`date` は `YYYY`・`YYYY-MM`・`YYYY-MM-DD`、期間は `開始/終了`。雑誌は公式の発売日がわかればそれを、なければ表紙の発行日を使う。`other_dates`（`date`・`label`・`sources`）は正当に違う日付（雑誌の発行日など）、`rejected_dates`（`date`・`claimed_by`・`keywords`・`reason`）は資料が挙げるが誤りと判断した日付 |
| `entries` | ルール・レギュレーションの記録 |
| `errata` | カード個別のエラッタ・印刷テキストの変更・裁定の記録 |
| `card_lists` | 読み替えの対象カードの一覧（`supporter`: サポーターとして扱う 15 種、`poke_body`: ポケボディーとして扱うカード）。`ids` はこのリポジトリのカード id、`bulbapedia` は Bulbapedia の表記、`qa`（`poke_body` だけ）は公式 Q&A の原文の表記（`type`・`name`・`series`・`power`） |
| `jp_editions` | 日本版のルールの版（`id`: `ed1`〜`ed5` など、`label`、`date`: 発表・告知の日、`event`: 対応する `events` の id、`in_matrix`: 比較表の列にするか、`period`、`name_in_sources`: 資料での呼び名、`applied`: ルールが使われ始めた時期（発表日とは別。わからなければ「未確認」）、`basis`、`confidence`、`sources`）。`date` は `event` の日付と一致しなければエラー |
| `jp_edition_matrix` | 版ごとの比較表の行（`id`: ページ内のアンカー、`label`、`rd_item`: 対応する `data/rule_differences.json` の項目の `id` か `null`、`rd_periods`: 同じ項目を複数の行に分けたとき、突き合わせる rule_differences の行の時期（任意）、`cells`、`notes`）。`cells` は版の `id` をキーに `text`・`confidence`・`sources`・`basis`（資料の確認方法。`evidence_kinds` の値）・`evidence_type`（根拠の性質。`matrix_evidence_types` の値）・`scope`（その根拠が裏付ける時期・範囲）・`rd_note`（rule_differences の行と確度が違う理由。任意）を持つ。キーのない版は「未確認」と表示する（ほかの版から推測して埋めない）。`evidence_type` が `secondary`・`inferred` のマスは「確実」にできない。rule_differences の「第N版」で始まる行は、含む版のマスと確度が合わなければエラー（比較表で未確認の版を含めてもエラー） |
| `matrix_evidence_types` | 比較表のマスの根拠の性質: `edition_document`（版の文書そのもの）、`contemporary_official`（その版の時期の公式の雑誌・書籍・大会の要項）、`later_official`（後の公式資料の「前のルール」の説明。直前の版だけに当てはめる）、`secondary`（後年の二次資料）、`inferred`（公式資料の変更内容からの推定） |
| `stage_kinds` | エラッタの記録の段階: `preannouncement`（変更の予告・検討）、`printed_change`（新しい文面の印刷）、`official_notice`（既存のカードにも適用する公式の告知）、`applied`（実際の適用） |
| `documents` | スキャンで確認した印刷物の巻号ごとの記録（`code`: docs/sources.md の P 記号、`title`、`series`、`volume`、`publisher`、`issued`: 表紙・奥付の発行日、`released`: 公式の発売日（わからなければ `null`）、`printing_checked`: 確認した刷（奥付を見ていないものはそう書く）、`scan`（`source`: J37 など、`url`: 開けることを確かめたファイルの URL、`pdf_pages`）、`pages`（`printed`: 誌面のページ番号、`pdf`: PDF のページ、`content`: 要約、`refs`: そのページを根拠にした id）、`notes`）。`evidence` で J37 のスキャンを根拠にした記録の `cites` の P 記号は、ここに載っていなければエラー |

`entries`・`errata` の各要素の主な欄:

| 欄 | 内容 |
|---|---|
| `id` | ルールの識別 id（`MIX-`: 混合期、`KGR-`: ガルーラルール、`REG-`: 2001年より前の日本の大会レギュレーション、`NEO-`: neo 期の基本ルールの追加修正、`RB-`: 版の番号の付いたルールブック（冊子）の本文、`EN-`: 英語版、`ERR-`: エラッタ、`TXT-`: 印刷の変更、`RUL-`: 裁定） |
| `stages` | エラッタの段階ごとの確認状況（任意。`kind`: `stage_kinds` の値、`date`、`text`、`confidence`、`sources`）。公式エラッタ（`official_errata`）に分類した記録には必須で、確認できた `official_notice` がなければエラー（予告や再録の文面の変更だけで公式エラッタとしない）。未確認の `official_notice`・`applied` に日付を書くとエラー（推定した日付を確定日として書かない） |
| `term_in_sources` | 当時の資料での呼び方（「最新の説明」「ルール変更のお知らせ」など）。公式エラッタ（`official_errata`）に分類した記録には必須で、ないとエラー。分類名と当時の呼び方を混同しないために書く |
| `id_note` | id の文字列と内容がずれている理由（任意）。参照の互換性のため id は変えず、ここで説明する（例: `MIX-SUPPORTER-ERRATA` は公式エラッタではなく大会レギュレーション） |
| `region` | `JP`（日本版）／`EN`（英語版） |
| `category` | 上の区分 |
| `announced`・`effective_from`・`effective_until` | 公表日・適用の開始・終了。先頭に日付を書き、続けて説明を書く。わからないものは「未確認」などと文で書く。雑誌・会報の発行日は公表日で、適用の開始日とは限らない |
| `printed_from` | 新しい文面の印刷の開始（任意。印刷テキストの変更・公式エラッタで使う）。再録した商品の発売日などを書く。印刷の開始は、既存のカードに新しい文面を適用し始めた日とは別なので、`effective_from` には書かない（印刷テキストの変更・公式エラッタで、日付を書いた `effective_from` に「印刷」と書くとエラー）。告知より早いことがあるので、公表 ≦ 適用の順の検査には入れない。`stages` の `printed_change` の日付と合わないとエラー |
| `announced_event`・`printed_event`・`effective_event` | 公表・印刷の開始・適用の開始に当たる `events` の id（任意）。書いた場合は、日付が合うかを検査する。エラッタは、公表した会報・雑誌の号の出来事を `announced_event` にする（例: `ERR-ENERGY-RETRIEVAL` は `EV-1998-FANCLUB5`）。公表した資料を確認できていないものは書かない。印刷テキストの変更・公式エラッタで、商品の出来事（`type` が `product`）を `effective_event` にするとエラー（`printed_event` に書く） |
| `applies_to.events` | 対象の大会・商品（`events` の id） |
| `cards`・`cards_from`・`external_cards` | 対象カード（`data/cards.json` の id か `data/ja_text_pcgsearch.json` のページ名）、`card_lists` の名前、このリポジトリにないカード |
| `printed_text`・`play_text`・`before`・`after` | 印刷された文面、エラッタ後・読み替え後の文面、変更前・変更後のルール |
| `notes` | 資料の記述（食い違いは両方を並べる） |
| `evidence` | 根拠（`source`: docs/sources.md の記号、`kind`: 根拠の種類、`cites`: その資料が挙げる当時の公式資料 P1〜） |
| `verification` | 原本との照合状況 |
| `confidence`・`open_questions` | 確度と未解決の点 |

## `data/ja_text_pcgsearch.json`（拡張パック以外の商品）

拡張パック以外の商品のカードです。`data/cards.json` とは別のファイルで、pcg-search.com の記載をそのまま持っています（[拡張パック以外の商品](cards/other-products.md)）。

- `products` の各キーが商品名（サイトの見出し）、値がカードの配列です。
- カードの主な欄: `list_number`（サイトの並び順。印刷された番号ではない。イントロパックのデッキだけは印刷された丸数字と一致）、`url`、`kind`（たねポケモン／トレーナー／EXTRA RULE など）、`name`、`type`、`hp`、`weakness`、`resistance`、`retreat`、`powers`、`attacks`、`text`、`note`、`illustrator`、`rarity`、`remarks`。
- `text` と `note` はサイトのカードページの 2 つの欄（本文と補足）です。ポケモンのどうぐ・悪エネルギーなどでは、効果が `note` の側にあります。
- エネルギーは記号（草・炎・水・雷・超・闘・無）の文字列です。`retreat` はにげるのエネルギーを並べたもので、`null` はにげるコストなし。
- 商品についての補足は `data/curation/other_products.json` にあります。

| キー | 内容 |
|---|---|
| `products` | 商品ごとの名前、まとまり（`group`）、発売日、出典。資料によって発売日が違うものは、`release_note` に別の日付とその資料を書く（商品のページで「※」を付けて表示） |
| `en_prints` | pcg-search のカードページ名 → 対応する英語版カード。ここにないカードで、拡張パックと同じカードは `data/cards.json` の対応を使う |
| `differences` | 日英の違い（`data/curation/card_differences.json` と同じ形） |
| `sheets` | 拡張シートの各シートの場所とカード |
| `decks` | ジムデッキの構成（カードページ名と枚数、基本エネルギーの枚数） |
| `intro_packs` | イントロパック・イントロパック★neo のカードの Bulbapedia のページと、その転送先（Bulbapedia が同じカードとしているカード） |
| `quick_starter_gift` | クイックスターターギフトの赤デッキ・緑デッキの構成 |
| `promos` | プロモの配布（pcg-search の備考）、配布日と Bulbapedia の記載、補足（`note`） |
| `reprint_text` | 同じカードの再録で日本語の文面が違うものの、違いの説明と区分（`wording` 書き方だけ／`clarify` 補足・対象の明記／`meaning` 意味が変わる） |
| `reprint_checks` | 同じカードの組の中で数値が食い違ったものの判定 |
| `identified_cards` | pcg-search で名前が「-」のカードの、カードの画像などで確認した名前（転記データ自体は変えない） |

## サイドカー（`data/sidecar/`）

`data/cards.json` を変えずに、カード・ワザに出典つきの情報を加えるファイルです。カードの記録とは id（カード id、ワザ・特殊能力の位置）で結びます。検査と生成は `scripts/build_card_rulings.py`（生成するページは [カードの裁定と公式の最新の説明](rules/card-rulings.md)）、テストは `tests/test_card_rulings.py` です。サイドカーの記録がないカードは、どの一覧も空として扱います（`annotations_for`）。

| ファイル | 内容 | id の書式 |
|---|---|---|
| `latest_descriptions.json` | 公式の書籍の「最新の説明」と、印刷の文面（`data/cards.json`）の違い | `LD-<カード id>-ATK<位置>`（ワザ）・`LD-<カード id>-PWR<位置>`（特殊能力）。位置は `pokemon.attacks`・`pokemon.powers` の 0 から数えた番号 |
| `card_checks.json` | カードの記録を公式の資料のページと照合した記録 | `CC-<カード id>-<出典の記号>` |
| `rulings.json` | 公式ルールの条項の索引（`rule_clauses`）、カード・ワザごとの裁定（`rulings`）、未解決の論点（`issues`）、比較（`comparisons`）、kyuura-engine の取り込みの記録（`engine_imports`）、エンジンの未解決の裁定の一覧（`engine_unresolved_index`） | `GR-…`・`CR-…`・`UQ-…`・`CMP-…`・`ENGINE-…` |

id は 3 つのファイルを通して重複しないこと、`data/rule_history.json` の id と重ならないことを検査します。`data/rule_history.json` の `documents` のページの記録（`refs`）からも、これらの id を参照できます。

### `latest_descriptions.json` の `records`

| 項目 | 内容 |
|---|---|
| `card_id`・`card_name_ja`・`target` | 対象のカードと、ワザ・特殊能力（`kind`: `attack`・`power`、`index`、`name_ja`）。名前が `data/cards.json` と合わないとエラー |
| `printed_text` | 印刷の文面の場所（`path`）と、照合したときの写し（`text_ja`）。`data/cards.json` が変わって写しと違うとエラー（照合し直す）。`image_check` は書籍の図版の文面との照合（`match`・`consistent_where_legible`・`not_checked`） |
| `latest_description` | 最新の説明の文面（`text_ja`）、出典の記号（`source`）・スキャン（`scan`）・ページ（`page`。`data/rule_history.json` の `documents` にあるページ）・PDF のページ・位置 |
| `also_quoted` | 同じ書籍の別のページに同じ文面が引かれている場所 |
| `book_rule` | 最新の説明の扱いを決めた条項（`GR-P43-P6-LATEST-DESCRIPTION`） |
| `classification`・`errata_ref` | 分類は `latest_description`（最新の説明）。公式エラッタ・印刷の変更の記録（`data/rule_history.json`）があるカードは、`errata_ref` で結ばないとエラー（最新の説明とエラッタを混同しない） |
| `differences` | 違い（`printed`・`latest`・`kind`: `wording`・`clarification`・`meaning`）。文字列が印刷の文面・最新の説明の中にそのままないとエラー |
| `meaning_change`・`meaning_note` | 処理が変わるか（`none_apparent`・`changed`・`unknown`）と、その読み方（推論であることを書く） |
| `verification` | 確かめた記録（`by`: `kyuura`・`kyuura-engine`、日付・方法・結果） |

### `card_checks.json` の `records`

| 項目 | 内容 |
|---|---|
| `card_id`・`source`・`page`・`location` | 照合したカードと資料のページ |
| `checked_fields` | 照合した欄と、そのときの `data/cards.json` の値の写し。今の値と違うとエラー |
| `fields_not_checked` | 照合していない欄 |
| `result`・`data_error` | `no_difference`（照合して差異なし）・`printed_vs_latest_only`（違いは印刷の文面と最新の説明の違いだけ）・`data_error`（データの誤り。別の修正として扱う）。照合の記録のないカードは未照合 |
| `differences` | 違いの欄と、最新の説明の記録（`latest_description_ref`） |

### `rulings.json`

| 項目 | 内容 |
|---|---|
| `rule_clauses` | 裁定が参照する公式ルールの箇所（資料・ページ・節・要旨）。規則の本体の記録（`rule_history_refs`・`rule_differences_refs`）を必ず挙げる。新しい規則の記録ではなく、参照する位置の索引 |
| `rulings` の `status` | `CONFIRMED`（公式の資料に書かれている）・`SUPPORTED`（記述・例から読み取れるが、その場面そのものは書かれていない）。未解決の論点は `issues` に書き、裁定には `UNRESOLVED` を使わない |
| `rulings` の `basis` | 根拠。`kind` は `card_text`（カードの文面）・`card_commentary`（書籍のカードの解説・ワザ解説。関係するカードのものも含む）・`general_rule`（一般の規定がそのまま当てはまる）・`derived`（複数の規定から解釈の選択なしに導かれる。`statement` に書く）。資料のページ（`source`・`page`・`location`・`quote`）か、カードのデータ（`card_ref`・`field`）を指す。`checked` は確かめ方（`kyuura_image`・`kyuura_data`・`engine_report`） |
| `rulings` の `inference` | 推論。`SUPPORTED` には必須で、`CONFIRMED` にはあってはいけない |
| `rulings` の `engine_refs` | kyuura-engine の裁定 id との対応（`import`・`engine_version`・`document`・`ruling_id`・`engine_classification`・`engine_note`）。1 つの裁定を分けて記録したときは、それぞれに `part`。エンジンの分類が CONFIRMED でない裁定を `CONFIRMED` の記録に対応させるときは `reclassification`（`from`・`to`・`reason`）が必要 |
| `issues` | 未解決の論点（`question`・`why_unresolved`・`official_material`・`cases`（事例のカード・ワザとエンジンの裁定 id）・`reachability`・`engine_refs`）。同じ問いのエンジンの裁定は 1 つの論点にまとめる。同じエンジンの裁定を 2 つの論点に対応させるとエラー |
| `engine_imports` | 取り込んだエンジンのリポジトリ・ブランチ・コミット・読んだ文書。`ruling_sets` の範囲（S1〜S49 など）の id は、どれかの記録か `not_imported`（理由つき）にないとエラー |
| `engine_unresolved_index` | エンジンの未解決の裁定の一覧と、取り込んだ論点（`kyuura_issue`）。件数は `engine_unresolved_total` と同じ |

結論・論点・推論の文に、エンジンの停止コード・例外の名前（`UNRESOLVED_…`・`RuntimeError` など）を書くとエラーです。エンジンの実装の情報は `engine_refs`・`engine_unresolved_index` にだけ書きます。

参照の例（リポジトリの直下で実行）:

```python
import sys; sys.path.insert(0, 'scripts')
import build_card_rulings as bcr

ctx = bcr.load()
notes = bcr.annotations_for(ctx, 'PMCG4-021')
for ld in notes['latest_descriptions']:
    print(ld['target']['name_ja'], ld['latest_description']['page'], ld['latest_description']['text_ja'])
print(len(notes['rulings']), 'rulings;', [x['id'] for x in notes['issues']])
print(bcr.annotations_for(ctx, 'PMCG1-001'))  # 記録のないカード
```
