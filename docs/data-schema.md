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
| `en_print` | オブジェクト／null | 対応する英語版カード（下記）。英語版がないカードは `null` |
| `en_reprints` | 配列 | 英語版の別セットへの再録 `[{"set_id", "set_name", "number"}]` |
| `pokemon` | オブジェクト／null | ポケモンのデータ（下記）。ポケモン以外は `null` |
| `trainer` | オブジェクト／null | トレーナーのデータ（下記） |
| `energy` | オブジェクト／null | エネルギーのデータ（下記） |
| `jp_en_differences` | 配列 | このカードの日英の違い（下記）。[カードの日英の違い](cards/card-differences.md) と同じ内容 |
| `notes` | 文字列の配列 | 備考 |
| `source_ids` | オブジェクト | 出典データでの id `{"tcgdex": "...", "pokemontcg": ["base1-15"]}` |
| `ja_text_source` | 文字列／null | 日本語テキストを入れた場合、その出典 |

### 日英の値

名前や文面は、日本語と英語を並べたオブジェクトです。

```json
{"ja": null, "en": "Energy Trans"}
```

- `ja`: 日本版（公式の印刷文面）。カード名以外は現在すべて `null`（[理由](cards/README.md#日本語テキストについて)）。
- `en`: 英語版（WotC 版）の文面。

### `rarity_jp`

| フィールド | 内容 |
|---|---|
| `code` | `common`／`uncommon`／`rare`／`holo_rare`／`special`（通常の構成に当てはまらないもの） |
| `mark` | 日本版の記号 `●`／`◆`／`★`。`special` は `null` |
| `holo` | キラ（ホロ）の版があるか |
| `source_label` | 出典データ（TCGdex）の表記そのまま |

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
| `rockets_secret_machine` | 英語版の区分 Rocket's Secret Machine（日本語の区分名は未確認） |
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

`kind` は `text`（文面の意味）／`errata`（後年のエラッタ）／`placement`（収録先）／`print`（英語版の表記・誤植）。`sources` の記号は [出典と確認状況](sources.md) を参照。

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
