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

`kind` は `text`（文面の意味）／`numbers`（数値）／`errata`（後年のエラッタ）／`placement`（収録先）／`print`（英語版の表記・誤植）／`wording`（書き方の違い。効果は同じだが、説明を書いている場所や分け方が違う）／`art`（イラストの違い）。`sources` の記号は [出典と確認状況](sources.md) を参照。

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

日米のルールの違いのデータです。`items` の各要素が 1 項目で、`jp`・`en` にそれぞれ時期ごとのルール、`status` に判定（`違う`／`時期により違う`／`違う可能性あり`／`同じ`／`不明`）があります。[日米のルールの違い](rules/differences.md) はこのファイルから生成しています。

## `data/ja_text_pcgsearch.json`（拡張パック以外の商品）

拡張パック以外の商品のカードです。`data/cards.json` とは別のファイルで、pcg-search.com の記載をそのまま持っています（[拡張パック以外の商品](cards/other-products.md)）。

- `products` の各キーが商品名（サイトの見出し）、値がカードの配列です。
- カードの主な欄: `list_number`（サイトの並び順。印刷された番号ではない。イントロパックのデッキだけは印刷された丸数字と一致）、`url`、`kind`（たねポケモン／トレーナー／EXTRA RULE など）、`name`、`type`、`hp`、`weakness`、`resistance`、`retreat`、`powers`、`attacks`、`text`、`note`、`illustrator`、`rarity`、`remarks`。
- `text` と `note` はサイトのカードページの 2 つの欄（本文と補足）です。ポケモンのどうぐ・悪エネルギーなどでは、効果が `note` の側にあります。
- エネルギーは記号（草・炎・水・雷・超・闘・無）の文字列です。`retreat` はにげるのエネルギーを並べたもので、`null` はにげるコストなし。
- 商品についての補足は `data/curation/other_products.json` にあります。

| キー | 内容 |
|---|---|
| `products` | 商品ごとの名前、まとまり（`group`）、発売日、出典 |
| `en_prints` | pcg-search のカードページ名 → 対応する英語版カード。ここにないカードで、拡張パックと同じカードは `data/cards.json` の対応を使う |
| `differences` | 日英の違い（`data/curation/card_differences.json` と同じ形） |
| `sheets` | 拡張シートの各シートの場所とカード |
| `decks` | ジムデッキの構成（カードページ名と枚数、基本エネルギーの枚数） |
| `intro_packs` | イントロパック・イントロパック★neo のカードの Bulbapedia のページと、その転送先（Bulbapedia が同じカードとしているカード） |
| `quick_starter_gift` | クイックスターターギフトの赤デッキ・緑デッキの構成 |
| `promos` | プロモの配布（pcg-search の備考）、配布日と Bulbapedia の記載、補足（`note`） |
| `reprint_text` | 同じカードの再録で日本語の文面が違うものの、違いの説明と区分（`wording` 書き方だけ／`clarify` 補足・対象の明記／`meaning` 意味が変わる） |
| `reprint_checks` | 同じカードの組の中で数値が食い違ったものの判定 |
