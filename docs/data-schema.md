# データの構造（`data/cards.json`）

`data/cards.json` は、旧裏の日本版のカードを 1 枚 1 レコードで収録した構造化データです。拡張パック 10 弾の全 780 枚と、拡張パック以外の商品（拡張シート・サザンアイランド・ポケモンジムのデッキ・クイックスターターギフト・イントロパック・neo プレミアムファイル・プロモ）の対戦に使うカード 597 枚の、計 1,377 件です（形式 3。2026-10-19 から）。`scripts/build_cardlist.py` で生成しています（拡張パック以外の商品の正規化は `scripts/non_pack.py`）。拡張パックの 780 件の id・欄は形式 2 のままで、形式 3 で加えた欄を全記録に持ちます。

## 全体

```json
{
  "schema_version": 3,
  "description": "...",
  "text_availability": {"en": "...", "ja": "..."},
  "cards": [ { ...カード... } ]
}
```

## カード

| フィールド | 型 | 内容 |
|---|---|---|
| `id` | 文字列 | カード id。拡張パックは TCGdex の日本版 id（例 `PMCG1-011`、`neo4-113`）。拡張パック以外の商品は「商品の記号-カードページ名の末尾 3 桁」（例 `GD1-009` = pcg-search の `1stgymd1009`。下の「拡張パック以外の商品の記録」） |
| `jp_set` | 文字列 | 日本版の弾。`PMCG1`〜`PMCG6`（第1〜6弾）、`neo1`〜`neo4`。拡張パック以外の商品の記録は商品の記号（`GD1`・`ES1`・`PR1` など） |
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
| `jp_print` | オブジェクト／null | 日本版の印刷についての情報（下記）。なぞのばしょ・ポケモンWiki にカードページがあるカード（拡張パック以外の商品は pcg-search のカードページ）だけ |
| `product_group` | 文字列 | 商品の種類（形式 3）。`expansion_pack`（拡張パック）・`expansion_sheet`・`southern_islands`・`gym_deck`・`quick_starter_gift`・`intro_pack`・`premium_file`・`promo` |
| `play_scope` | 文字列 | 対戦での扱い（形式 3）。`standard`（通常の対戦のカード）・`kangaskhan_rule`（2 人 1 組の「ガルーラルール」専用）・`not_for_official_tournaments`（カードに「公式大会では使えません」とある）。`data/curation/non_pack.json` の `play_scope` |
| `same_card_group` | 文字列／null | 商品をまたいだ同じカードの組の id（`SC-<最初の記録の id>`。`data/same_card_groups.json`）。組がなければ `null` |
| `data_gaps` | 文字列の配列 | 値のない欄（調査・転記の不足。形式 3）。例 `pokemon.evolves_from`・`pokemon.evolves_to`（ベイビィの進化先が未確認）・`jp_print.level`・`energy.text.ja`・`pokemon.stage`（サイトの種類の欄と進化ラインの段階が違う）。英語版がないことは数えない |
| `source_ids.pcg_search` | 文字列の配列 | pcg-search.com のカードページ名（形式 3）。拡張パックの記録は空（拡張パックのページとは結んでいない） |
| `copies` | 配列 | 拡張パック以外の商品の記録だけ。同じ商品の中で番号だけが違うページ（イントロパックのデッキ）をまとめた元のページ `[{page, list_number}]`。1 ページなら 1 件 |
| `field_sources` | オブジェクト | 拡張パック以外の商品の記録だけ。欄の出どころ（`pcg_search`・`pcg_search_page_dash`（読み直したページで「-」）・`pcg_search_null_read_as_zero`・`pcg_search_evolution_line`・`same_card:<拡張パックの id>`・`other_products.en_prints`・`pokemontcg:<id>`・`pcg_search_kind_conflicts_with_evolution_line`） |
| `corrections` | 配列 | 訂正の記録（`data/curation/card_corrections.json`）で直した欄があるときだけ `[{id, field, before, after, basis, decided_on}]` |

### 日英の値

名前や文面は、日本語と英語を並べたオブジェクトです。

```json
{"ja": null, "en": "Energy Trans"}
```

- `ja`: 日本版の文面。第1〜4弾と neo 第1〜2弾はなぞのばしょ、第5〜6弾と neo 第3〜4弾はポケモンWiki の転記から取り込み済み。出典にないもの（無色2個エネルギーの効果文、アンノーン M・U・A のルール文）は `null`（[詳細](cards/README.md#日本語テキストについて)）。アンノーンI・D・F のルール文と、neo 第1〜2弾のベイビィ 6 枚のルール文（なぞのばしょのページの「ルール」の欄を取り込み（`scripts/nazonobasho.py` の `KEEP_FIELDS`）が残していなかった）は、カードの画像で確かめた訂正の記録（`data/curation/card_corrections.json`）で入れている。
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
| `evolves_to` | 文字列の配列／null（ベイビィだけ） | ベイビィポケモンの進化先の欄（「〇〇へ進化」）の日本語名。印刷の順（バルキーは `["エビワラー", "サワムラー", "カポエラー"]`）。下の「進化先」 |
| `hp` | 整数 | HP |
| `types` | 文字列の配列 | タイプ（下の列挙値） |
| `weaknesses` | 配列 | 弱点 `[{"type": "fire", "operator": "×", "value": 2}]` |
| `resistances` | 配列 | 抵抗力 `[{"type": "psychic", "operator": "-", "value": 30}]` |
| `retreat_cost` | 整数 | にげるためのエネルギーの数 |
| `rules_text` | 日英／null | ベイビィ・ひかるポケモン・アンノーンなどのルール文 |
| `powers` | 配列 | ポケモンパワー（下記） |
| `attacks` | 配列 | ワザ（下記） |

#### 進化先（`pokemon.evolves_to`）

印刷に進化先の欄があるのはベイビィポケモン（`stage` が `baby`）だけなので、この欄はベイビィの記録にだけ置きます（2026-10-27 から）。値で次の 4 つを区別します。

| 値 | 意味 |
|---|---|
| 欄がない（`baby` 以外） | 適用外。その段階の印刷に進化先の欄がない。進化できない・進化先がないという意味ではない（たねポケモン・1 進化ポケモンの進化先は、進化カードの `evolves_from` から引く） |
| `null` | 未確認。進化先の欄はあるが、印刷で確かめた値がない（`data_gaps` に `pokemon.evolves_to`）。推測・同じ名前のほかの版から埋めない |
| 名前の配列 | 印刷の進化先の欄で確かめた名前（印刷の順）。カードの画像の照合の記録（`data/curation/card_image_checks.json`）と訂正の記録（`data/curation/card_corrections.json`。`kind: field_added_from_print`・`basis: card_image_check`）でたどれる |
| `[]` | 印刷に進化先がないと明示している（形式の上の値）。今の 1377 件に該当はなく、生成の検査が受け付けない（加えるときは根拠を記録して検査を直す） |

生成の順番: 記録を作る（拡張パック・拡張パック以外の商品）→ ベイビィの記録に `evolves_to: null` を置く（`evolves_from` のすぐあと）→ 訂正の記録を当てはめる（`before` が `null` でなければ止まる）→ 進化先の形と出どころの検査（null でない値は、画像の照合の記録を持つ訂正から入ったものだけ）→ 画像の照合の記録と生成した値の照らし合わせ → 同じカードの組・`data_gaps`。転記（なぞのばしょの「進化条件」など）からは作りません（転記の値は照合の記録の `site_transcriptions` に分けて残す）。ベイビィから進化できることを理由に、進化先のカードの `stage`（印刷の段階 `basic`）・`evolves_from` は変えません。場で「進化ポケモン」としてあつかうか（公式ルール p.315）は、場の状態の規定で、カードの段階の値ではありません（`data/sidecar/rulings.json` の GR-2000-P315-EVOLVED-BABY）。

`data/cards.csv` では `evolves_to_status`（空: ポケモンでない・`not_applicable`・`unconfirmed`・`printed`・`printed_none`）と `evolves_to_ja`（名前を空白区切り。ポケモンの日本語名は空白を含まない（検査で確かめる））の 2 列です。エンジンの写し（`scripts/extract_kyuura_cards.py`）は 2026-10-27 の時点でこの欄を取り出していません（`docs/engine-handover-baby-v0.113.md`）。

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
| `data/cards.csv` | カード 1 枚 | `id`、名前（日英）、レア、英語版、進化、HP、タイプ、弱点、抵抗力、にげる、トレーナー・エネルギーの区分と本文（日英）、日英の違い、`product_group`・`play_scope`・`same_card_group`・`source_pages`（pcg-search のページ名を空白区切り）・`data_gaps`（空白区切り）・`corrections`（訂正の id を空白区切り）・`evolves_to_status`・`evolves_to_ja`（ベイビィの進化先。上の「進化先」） |
| `data/attacks.csv` | ワザ 1 つ | `card_id`、`index`、名前（日英）、`cost`（列挙値を空白区切り）、`cost_total`、`damage_base`、`damage_modifier`、`damage_display`、効果文（日英） |
| `data/powers.csv` | ポケモンパワー 1 つ | `card_id`、`index`、`kind`、名前（日英）、本文（日英） |

`data/cards.json` と 3 つの CSV は、同じ記録から同じ生成で作ります（`tests/test_non_pack_engine_v068.py` が件数・主な欄の一致を確かめる）。

## 拡張パック以外の商品の記録

`data/ja_text_pcgsearch.json`（pcg-search.com の転記。23 商品・681 ページ）を、`scripts/non_pack.py` が `data/cards.json` の記録の形に正規化します。手作業の決め事は `data/curation/non_pack.json` にあります。

- **id**: 「商品の記号-カードページ名の末尾 3 桁」。サイトの並び順（`list_number`）は使わないので、並び順が変わっても id は変わりません。商品の記号は `data/curation/non_pack.json` の `products`（`ES1`〜`ES3` 拡張シート、`SI` サザンアイランド、`GD1`〜`GD6` ポケモンジム、`QSG`、`IP1`・`IP2`・`IPH` イントロパック、`PR1` 旧裏のプロモ、`PF1`〜`PF3`、`NIP1`・`NIP1X`・`NIP2`・`NIP2X` イントロパック★neo、`PRN` neo のプロモ）。一度決めたら変えません。
- **元の項目の行き先**: 681 ページは、記録（597）・同じ商品の番号違いのまとめ（イントロパックのデッキ。66。`copies`）・対戦のカードでない項目（18。`data/product_items.json` の `non_game_items`）のどれかで、`data/product_items.json` の `items` にページごとの行き先があります。ページの数はカードの種類の数ではなく、デッキの封入枚数とも別です（構築済みデッキの枚数は `data/curation/other_products.json` の `decks`）。
- **欄**: 名前・段階・HP・タイプ・弱点・抵抗力・にげる・特殊能力・ワザ・本文は pcg-search の転記です。英語版の文面で日本語の欄を補いません。
- **進化元**（`pokemon.evolves_from`）: (1) 同じカードの拡張パックの記録（名前・HP・特殊能力名・ワザ名が同じ）、(2) 同じサイトのカードページの「進化ライン検索」で 1 つ前の段階の名前（1 つに決まり、ページのカードの位置の段階がサイトの種類の欄と同じときだけ）、の順に使います。名前の接頭辞からは推測しません。英語版の進化元は照らし合わせ（`data/same_card_groups.json` の `evolves_from_checks`）にだけ使います。どれもなければ `null` で、`data_gaps` に入ります。種類の欄と進化ラインの段階が違うカードは、段階を `data_gaps`（`pokemon.stage`）にして進化元を入れません。
- **にげる**: 転記の `null` は、サイトの欄の「-」（にげるエネルギーなし。0）か空欄です。読み直したページ（`data/pcgsearch_page_checks.json`）で「-」を確かめたものは `pcg_search_page_dash` です。
- **補足欄**: 補足（サイトの ruleDetail）は、ふつうはカードのルールの文として本文につなぎます。カードの説明の文（`flavor`）・大会での扱いの表示（`label`）は `notes` に残します（`non_pack.json` の `note_roles`）。
- **レアリティ**: ●◆★ を common・uncommon・rare、「★(キラ)」を holo_rare、「-」を no_mark、「★★(キラ)」などを special（キラ）にします。

## `data/product_items.json`・`data/same_card_groups.json`

`scripts/build_cardlist.py` の出力です（手で編集しない）。

| ファイル | キー | 内容 |
|---|---|---|
| `product_items.json` | `products` | 商品ごとの記号・名前・まとまり・発売日・出典・数（`counts`: 元の項目・記録・番号違いのまとめ・対象外の項目・通常の対戦のカード）・構成（`composition`） |
| | `items` | 元の項目（ページ）ごとの行き先（`disposition`: `card` 記録・`copy` 番号違いのまとめ・`non_game` 対象外）と記録の `id` |
| | `non_game_items` | 対戦のカードでない項目（おすすめルール・デッキのカード・パスカード・ジョークカード・イラストレーターの賞のカードなど）。`kind` と `reason` |
| `same_card_groups.json` | `groups` | 商品をまたいだ同じカードの組（`basis_fields` で判定した欄。名前・HP・特殊能力名・ワザ名、トレーナー・エネルギーは名前と種類）。組の要素ごとに、数値の違う欄（`numbers_differ`）・文面の関係（`text`: `same`・`same_ignoring_punctuation`・`similar`・`different`）・最初の記録と同じ処理か（`equivalent_to_first`）。名前だけでまとめない |
| | `evolves_from_checks` | 進化元の照らし合わせ（進化ラインと同じ・違う・決まらない、英語版と同じ・違う、進化ラインの名前・段階が記録と違う） |

## `data/pcgsearch_page_checks.json`

pcg-search.com のカードページを読み直し、転記に入っていない欄と区別（弱点・抵抗力・にげるの欄の生の表記、「進化ライン検索」）だけを取り出したものです（`scripts/pcg_search.py extract-pages`。2026-10-19 に 187 ページ）。`transcript_differences` は、読み直したページを転記と同じ方法で読んだ欄のうち転記と違うもの（2026-10-19 は 0）。同じサイトのデータなので、転記の独立した照合には数えません。

## `data/curation/card_corrections.json`

カードデータの訂正の記録（`corrections`）と、訂正しなかった候補（`candidates`）です。

- `corrections`: `id`（`FIX-…`）・`card_id`・`field`・`before`・`after`・`kind`・`applied_by`（`card_corrections`: `scripts/build_cardlist.py` が生成のたびに当てはめる。当てはめる前の値が `before` でなければ止まる。`ja_text.json`: 前の作業で `data/curation/ja_text.json` で直したもので、生成した値が `after` かだけを確かめる）・`kind`（`transcription_error` 転記の誤り・`transcription_omission` 転記の欠け・`field_added_from_print` データの形になかった欄（`null` で作る）に印刷で確かめた値を入れる（2026-10-27 のベイビィの `pokemon.evolves_to`）。`before` が `null` の訂正は、空だった欄に値を入れる）・`basis`（`user_provided`・`kyuura_source_check`・`kyuura_existing_record`・`card_image_check`: kyuura がウェブに公開されたカードの画像を読んだ。公式の書籍のページとの照合（`CC-`）ではないので、照合の記録を作らず、`evidence`（サイト・ページと画像の URL・画像の形式と sha256・取得した日）・`identification`（同じカード・同じ版と決めた手がかり）・`scope`（確かめた欄と確かめていないこと）を書く。2026-10-24 のアンノーンI・D・F のルール文から。2026-10-27 からは、画像・特定の手がかり・読んだ欄を照合の記録 `data/curation/card_image_checks.json` に 1 枚 1 件で書き、訂正は `image_check` でその id を指す（`evidence` か `image_check` のどちらかがないとエラー））・`basis_detail`・`confirmed_by`・`card_checks_affected`（照合したときの値 `before` を写している照合の記録。`scripts/build_card_rulings.py` は、照合の記録の写しと今の値の違いをこの訂正で確かめる。過去の照合の記録は書きかえない）。公式エラッタ・最新の説明は書かない（`data/rule_history.json`・`data/sidecar/`）。
- 訂正の記録の `image_check`: カードの画像の照合の記録（下の `data/curation/card_image_checks.json`）の id。

## `data/curation/card_image_checks.json`

kyuura がウェブに公開されたカードの画像で印刷の欄を読んだ記録（照合の記録 `IMG-<カード id>`。2026-10-27 のベイビィ 13 枚から）。公式の書籍のページとの照合（`CC-`）・最新の説明（`LD-`）ではありません。

| 項目 | 内容 |
|---|---|
| `id`・`card_id`・`card_name_ja`・`kind`（`card_image_check`）・`checked_on`・`checked_by` | 記録と、読んだカード・日 |
| `images` | 画像ごとに `site`（`pcg-search.com [N3]`・`なぞのばしょ [N1]`）・`page_url`・`page_title`・`image_url`・`image_format`・`image_sha256`・`accessed_on` |
| `identification`・`independence` | 同じ日本語版の同じカードと決めた手がかり（名前・HP・タイプ・ワザや特殊能力・商品。カードの番号は使わない）と、画像が独立した照合か（同じ画像・同じスキャンの疑いがあれば独立と数えない） |
| `print_values` | 画像に写っている値（欄 → 値）。`scripts/build_cardlist.py` が、生成した `data/cards.json` の値（訂正のあと）と同じかを確かめる（違えば止まる） |
| `print_text` | 欄の印刷の文（進化先の欄の見出しと文など） |
| `site_transcriptions` | サイトの転記・解説の値（画像の値と分ける。照合の数に入れない）。`values` の `null` はその転記にその欄の文がないこと |
| `not_checked`・`print_version`・`existing_value` | 確かめていない欄、刷・版の注記（修正前・修正版など）、今までの値が画像と同じだったこと |
| `corrections` | この記録から書いた訂正の id。訂正は同じカード・`print_values` の欄・同じ値で、`basis` は `card_image_check`、`image_check` はこの記録、`card_checks_affected` は空（違えば止まる） |

- `candidates`: `status`（`held_print_version` 印刷の版が決まらない・`held_transcription_difference` 別の転記との違い・`held_likely_transcription_error` 誤りの可能性が高いが印刷で確かめていない・`version_difference` 版の違い（誤りではない）・`gap_open` 値の欠け）と `reason`。

## エンジンの実装の対象（`data/engine_targets.json`）

`scripts/build_engine_targets.py` の出力で、読み方は [エンジンの実装の対象](engine-targets.md) です。エンジンの登録表の写しは `data/curation/engine_registered_cards.json`（`scripts/snapshot_engine_registry.py`。エンジンの版を上げるときに作り直す）。記録ごとに `category`（`candidate`・`data_missing`・`special_rule_design`・`non_game`）と `engine_status`（`registered`・`mechanically_equivalent`・`reuse_candidate`・`new_effect_needed`）を分けて持ちます。写しを新しい版で作り直すと、前の写しの参照（版・コミット・取得日・件数）を `previous_snapshots` に残します（`engine_reference` にも写す。前の版の時点の取得日・件数を新しい値で書きかえない）。写しの `registry_id` は登録表の名前で、版の番号ではありません。同じかの比べ（`mechanically_equivalent`）と値の欠け（`data_missing`）には、エンジンの写しがまだ取り出さないベイビィの進化先（`pokemon.evolves_to`）も含めます。

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

拡張パック以外の商品のカードの、pcg-search.com の記載をそのまま持つ転記です（[拡張パック以外の商品](cards/other-products.md)）。生成のたびにこの転記から `data/cards.json` の記録を作り（上の「拡張パック以外の商品の記録」）、転記そのものは書き換えません。訂正は `data/curation/card_corrections.json` で当てはめます。

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

`data/cards.json` を変えずに、カード・ワザに出典つきの情報を加えるファイルです。カードの記録とは id（カード id、ワザ・特殊能力の位置）で結びます。検査と生成は `scripts/build_card_rulings.py`（生成するページは [カードの裁定と公式の最新の説明](rules/card-rulings.md)。手で編集しない）、テストは `tests/test_card_rulings.py`（v0.13 の取り込み）と `tests/test_engine_imports_v05_v12.py`（v0.5〜v0.12 の取り込み・破壊テスト）です。サイドカーの記録がないカードは、どの一覧も空として扱います（`annotations_for`）。

| ファイル | 内容 | id の書式 |
|---|---|---|
| `latest_descriptions.json` | 公式の書籍の「最新の説明」と、印刷の文面（`data/cards.json`）の違い | `LD-<カード id>-ATK<位置>`（ワザ）・`LD-<カード id>-PWR<位置>`（特殊能力）。位置は `pokemon.attacks`・`pokemon.powers` の 0 から数えた番号 |
| `card_checks.json` | カードの記録を公式の資料のページと照合した記録 | `CC-<カード id>-<出典の記号>` |
| `rulings.json` | 公式ルールの条項の索引（`rule_clauses`）、カード・ワザごとの裁定（`rulings`）、未解決の論点（`issues`）、比較（`comparisons`）、kyuura-engine の取り込みの記録（`engine_imports`）、エンジンの未解決の裁定の一覧（`engine_unresolved_index`）、エンジンの採用した仕様・簡略化・実装の事項（`engine_positions`。2026-10-19 から） | `GR-…`・`CR-…`・`UQ-…`・`CMP-…`・`ENGINE-…`・`ENG-V<版>-…` |

id は 3 つのファイルを通して重複しないこと、`data/rule_history.json` の id と重ならないことを検査します。`data/rule_history.json` の `documents` のページの記録（`refs`）からも、これらの id を参照できます。

### `latest_descriptions.json` の `records`

| 項目 | 内容 |
|---|---|
| `card_id`・`card_name_ja`・`target` | 対象のカードと、ワザ・特殊能力（`kind`: `attack`・`power`、`index`、`name_ja`）。トレーナーは `kind: trainer` とカード名の `name_ja` を持ち、`index` は持たない（id は `LD-<カード id>-TRAINER`、文面の path は `trainer.text.ja`）。名前・種類が `data/cards.json` と合わないとエラー |
| `printed_text` | 印刷の文面の場所（`path`）と、照合したときの写し（`text_ja`）。`data/cards.json` が変わって写しと違うとエラー（照合し直す）。`image_check` は書籍の図版の文面との照合（`match`・`consistent_where_legible`・`not_checked`）。図版と転記の文面が異なり、図版の版を特定できない場合は `different_text` と `image_text_ja`・版を断定しない `image_check_note` に別の文面を保存できる。これは転記の誤りとは断定しない。データの誤りと確認できる場合は `card_checks.json` の `data_error` に書く |
| `latest_description` | 最新の説明の文面（`text_ja`）、出典の記号（`source`）・スキャン（`scan`）・ページ（`page`。`data/rule_history.json` の `documents` にあるページ）・PDF のページ・位置 |
| `also_quoted` | 同じ書籍の別のページに同じ文面が引かれている場所 |
| `book_rule` | 最新の説明の扱いを決めた条項（`GR-P43-P6-LATEST-DESCRIPTION`） |
| `applies_to_print` | 書籍のどの欄から、このカード id に当てはめたか（あるときだけ。2026-10-30 から）。`heading`（欄の見出しの配布・商品）・`by`（`figure`: 欄の図版がこのカードの印刷で、図版を照合した。`heading_listing`: 見出しがこのカードの配布を挙げるが、図版は別の印刷）・`basis`（そう決めた手がかり）。書籍の 1 つの欄が複数の配布をまとめ、図版がそのうち 1 つだけのことがある（p.127 のピカチュウ）。`heading_listing` なら `printed_text.image_check` は `not_checked`、`figure` なら照合の結果がいる（違えばエラー）。見出しだけで当てはめた印刷を、図版で照合したことにしない |
| `classification`・`errata_ref` | 分類は `latest_description`（最新の説明）。公式エラッタ・印刷の変更の記録（`data/rule_history.json`）があるカードは、`errata_ref` で結ばないとエラー（最新の説明とエラッタを混同しない） |
| `differences` | 違い（`printed`・`latest`・`kind`: `wording`・`clarification`・`meaning`）。文字列が印刷の文面・最新の説明の中にそのままないとエラー |
| `meaning_change`・`meaning_note` | 処理が変わるか（`none_apparent`・`changed`・`ambiguous_in_print`（印刷の文面だけでは処理が決まらず、最新の説明がその読み方を決めた）・`unknown`）と、その読み方（推論であることを書く）。違いの種類に `meaning` があれば `changed` |
| `verification` | 確かめた記録（`by`: `kyuura`・`kyuura-engine`、日付・方法・結果）。kyuura が原典の画像を読んだ記録は `by: kyuura` を持つ。エンジンの照合の記録を取り込んだ記録（`import_provenance` のある記録）の `by: kyuura-engine` は、`record`（`card_verification.json` の中の場所。`cards.PMCG1-002` など）・`source_checked_on`（エンジンが原典を確かめた日）・`source_checked_on_basis`（その日付の根拠）・`method`・`scope`（エンジンが照合した項目）を持つ |
| `import_provenance` | kyuura が原典の画像を読んでいない記録（kyuura-engine の照合の記録の取り込み）だけ。`kind`（`engine_record`）・`imported_on`（取り込んだ日。原典の確認日とは別）・`kyuura_reread_source: false`・`source_commit`（エンジンのコミット）・`scope_note`。`by: kyuura` の確認と同時に持たない（読み直したら `by: kyuura` を加え、これを外す）。`by: kyuura` も `import_provenance` もない記録はエラー。再利用の手順は [エンジン開発の準備状況](engine-readiness.md) の 10 章 |

### `card_checks.json` の `records`

| 項目 | 内容 |
|---|---|
| `card_id`・`source`・`page`・`location` | 照合したカードと資料のページ |
| `checked_fields` | 照合した欄と、そのときの `data/cards.json` の値の写し。今の値と違うとエラー。ただし、照合のあとで訂正した欄は、`data/curation/card_corrections.json` の訂正（照合した値 → 今の値。`card_checks_affected` にこの記録）があればよい（過去の照合の記録は書きかえない） |
| `fields_not_checked` | 照合していない欄 |
| `result`・`data_error` | `no_difference`（照合して差異なし）・`printed_vs_latest_only`（違いは印刷の文面と最新の説明の違いだけ）・`data_error`（データの誤り。別の修正として扱う）。照合の記録のないカードは未照合。`no_difference` なら、結んだ最新の説明にも違いがないこと（違いがあるとエラー） |
| `data_error` の中身 | `result` が `data_error` のときだけ、`[{field, kyuura_value, source_value, evidence, fix_status, note}]`。`kyuura_value` は `checked_fields` の写しと同じ、`fix_status` は `candidate`（この記録ではデータを直さない。修正は別の作業）。ほかの結果では `false` |
| `differences` | 違いの欄と種類（`printed_vs_latest`: 最新の説明の記録 `latest_description_ref` と結ぶ。`data_error`: データの誤りの欄） |
| `corrections` | 照合のあとで `data/cards.json` を直した欄（あるときだけ）。`[{field, before, after, evidence, method, commit, note}]`。`after` は `checked_fields` の写し（直したあとの値）と同じ、`before` とは違う、`commit` はデータを直したコミット。直すのはカードのデータの生成の手順（`data/curation/` と `scripts/build_cardlist.py`）で、この記録ではない。同じ欄を `data_error`（修正の候補）と両方に書かない。例: ベロリンガ（PMCG2-041）のワザ名とレベル（`CC-PMCG2-041-P234`） |
| `data_gaps` | 値が空の欄（あるときだけ。調査課題）。`[{field, kyuura_value, source_value, evidence, cause, status, note}]`。`kyuura_value` は今の `data/cards.json` の値（空）と同じで、値が入るとエラー（照合し直す）。`checked_fields` には入れない（値がないので照合していない）。`cause` は空になった原因、`status` は見出しの `gap_statuses`（`open`: 値を入れていない。推測で埋めない）。例: タケシのイワーク（PMCG5-048）の `jp_print.series`（`CC-PMCG5-048-P200`） |
| `later_notes` | 照合のあとの追記（あるときだけ）。`[{recorded_on, by: kyuura, finding, card_ids, source_rechecked: false, note}]`。照合した日の `findings`・`checked_fields`・`verification` は書きかえず、`finding` に追記が指す findings の文を写す。原典を読み直したら `verification` に書く（`source_rechecked` は false でないとエラー）。例: CC-PMCG6-063-P229 の、同じページのロケット団のニャースと PR1-078 の対応（2026-10-27） |
| `verification`・`import_provenance` | 最新の説明と同じ。エンジンの照合の記録を取り込んだ記録の照合した欄（`checked_fields`）は、エンジンの記録が照合したと書いた項目（`scope`）だけで、照合していない欄は理由とともに `fields_not_checked` に書く。例: v0.1 のたねポケモン（名前・段階はエンジンの照合の項目にない）、図版の文面が転記と異なり版が未特定のトレーナー（文面は照合した欄に入れず、LDの `image_text_ja` に保存する。v0.18までの取り込みには、当時LD形式がなかったため所見にだけ記録したトレーナーもある）、基本エネルギー（公式ルール p.318 の種類だけ） |

### `rulings.json`

| 項目 | 内容 |
|---|---|
| `rule_clauses` | 裁定が参照する公式ルールの箇所（資料・ページ・節・要旨）。規則の本体の記録（`rule_history_refs`・`rule_differences_refs`）を必ず挙げる。新しい規則の記録ではなく、参照する位置の索引。エンジンの裁定が一般の規定をそのまま述べたもの（ベンチのポケモンも特殊能力を使える、など）は、カードごとの裁定を作らずに条項の `engine_refs` に結ぶ（エンジンが CONFIRMED としたものだけ。推論を含むなら裁定 `CR-` にする）。`checked` は確かめ方で、見出しの `checked_values` の値で始める（違えばエラー）。`transcription_quotes`（`[{file, pdf_page, page, quote}]`）は既存の転記の引用で、検査が転記の文と照らす（`existing_transcription` で始まる条項には必須） |
| `rulings` の `status` | `CONFIRMED`（公式の資料に書かれている）・`SUPPORTED`（記述・例から読み取れるが、その場面そのものは書かれていない）。未解決の論点は `issues` に書き、裁定には `UNRESOLVED` を使わない |
| `rulings` の `basis` | 根拠。`kind` は `card_text`（カードの文面）・`card_commentary`（書籍のカードの解説・ワザ解説。関係するカードのものも含む）・`general_rule`（一般の規定がそのまま当てはまる）・`derived`（複数の規定から解釈の選択なしに導かれる。`statement` に書く）。資料のページ（`source`・`page`・`location`・`quote`）か、カードのデータ（`card_ref`・`field`）を指す。`checked` は確かめ方（`kyuura_image`・`kyuura_data`・`engine_report`・`existing_transcription`）。`existing_transcription`（2026-10-27 から）は、既存の転記 `data/Silver_Bible_structured.md`（利用者が加えた『オフィシャルブック2000』の OCR・校正の転記。PDF の番号 = ページ + 2）の文で、kyuura は原典の画像で確かめていない。`transcription`（`file`・`pdf_page`・`page`・`quote`）が要り、引用が転記のそのページにないとエラー。エンジンの規定・論点の再利用は `source_provenance`（repository・40桁のcommit・document・imported_on・kyuura_reread_source: false、裁定はruling_idも）で出所を持つ。この記録を `kyuura_image` にするとエラー |
| `rulings` の `inference` | 推論。`SUPPORTED` には必須で、`CONFIRMED` にはあってはいけない |
| `rulings` の `cards` | 裁定の対象（カード id とワザ・特殊能力）。同じ問いを複数のカードにまとめるときは並べる（エンジンの複数の版の同じ裁定を 1 つにする。例: 「自分の番の中で何度でも使える」はエナジートランス・あまごい・ダメージスワップの 1 件）。同じ対象・同じ問いの裁定を 2 つ作るとエラー |
| `rulings` の `engine_refs` | kyuura-engine の裁定 id との対応（`import`・`engine_version`・`document`・`ruling_id`・`engine_classification`（エンジンの表の「分類」の欄の写し）・`part`・`engine_note`）。エンジンの裁定 id は文書ごとの番号で、版が違えば同じ id が別の裁定なので、（`import`・`document`・`ruling_id`）で区別する。1 つの裁定を分けて記録したときは、それぞれに `part`。エンジンの分類が CONFIRMED でない裁定を `CONFIRMED` の記録に対応させるとき、エンジンが CONFIRMED だけとした裁定を `SUPPORTED` の記録に対応させるときは `reclassification`（`from`・`to`・`reason`）が必要。エンジンが「実装上の仮定」だけとした裁定は、裁定・条項に対応させない（`not_imported`）。その版の取り込みがまだないあいだだけ、別の版の裁定を、その文書を `documents` に挙げた取り込みに仮に結べる（v0.13 の取り込みが v0.10・v0.12 の C34・C35・W24 を結んだ形）。その版を取り込んだら、その版の取り込みに移す（移さないとエラー） |
| `issues` | 未解決の論点（`question`・`why_unresolved`・`official_material`・`cases`（事例のカード・ワザとエンジンの裁定 id。対象の種類は `attack`・`power`・`trainer`・`energy`（エネルギーカードのカード名）・`card`（カード全体。ルール文など））・`reachability`・`related_engine_rulings`・`related_issues`・`engine_refs`）。`cases` の事例は、エンジンの裁定のない事例（同じ文面のほかのカードなど）も書ける（`engine_ruling` を省く）。同じ問いのエンジンの裁定は 1 つの論点にまとめる（同じ問いと言える根拠がないときはまとめない）。同じエンジンの裁定を 2 つの論点に対応させる・同じ問いの論点を 2 つ作るとエラー。エンジンの未解決の一覧にない論点（エンジンは処理を決めているが、公式の資料では決められないもの）は `not_in_engine_index: true`。kyuura の調査で立てた論点（エンジンの裁定に結ばない。`engine_refs` が空）は、`not_in_engine_index: true` と `recorded_after`（記録した日 `date` と、その時点の最新の取り込み `import`）を持つ。`unresolved_counts(ctx, as_of=…)` は、その取り込みの版より後の時点（今の数を含む）だけ数える（例: アンノーンの調査の UQ-SELF-EXCLUDING-POWER-COPIES は v0.68 の取り込みのあと） |
| `issues` の `audit` | 未解決の論点の監査（2026-10-14 から必須）。`audited_on`（日付）・`game_effect`（結果への影響。見出しの `game_effect_values`: `game_result` 盤面か勝ち負けが変わる・`rng_only` コインの有無・順番だけが変わる（推論）・`order_only` 処理の順番だけが変わる・`not_analyzed` 未調査）・`game_effect_note`・`resolution_needs`（解決に要る資料）・`searched`（調べた範囲。探していない資料も書く）・`new_sources`（この監査で新しく読んだページ `[{source, page, what, resolves: false}]`。ページは `sources` にあること。論点を決める資料なら論点にせず裁定にするので、`resolves` はいつも false）。決まらないこと（`question`）・カード（`cases`）・エンジンの id（`engine_refs`）・分類（`status`・`official_material`）は既存の項目。エンジンの停止コードは `engine_unresolved_index` から求め、論点の文には書かない。`resolution_needs`・`game_effect_note` に停止コード・例外の名前を書くとエラー |
| `engine_imports` | エンジンの版ごとに 1 件（`ENGINE-<コミットの先頭 7 桁>`）。`engine_version`・`commit`（その版のコミット）・`parent_version_commit`・`documents_read_at`（文書を読んだコミット）・`kyuura_commit_used_by_engine`・`documents`・`ruling_sets`（文書ごとの範囲 `prefix`・`first`・`last`・`document`・`extra_ids`（T19b のような枝番）・`engine_reported_counts`）・`imported_rulings`（結んだ kyuura の記録の id）・`unresolved_rulings`（結んだ論点の id）・`not_imported`（`ruling_id`・`document`・`engine_classification`・`reason`）・`notes`（取り込みの注記）・`engine_reported_totals`（エンジンの文書が報告した停止コード・未解決の裁定の数 `stop_codes`・`unresolved_rulings` と `note`。`engine_unresolved_index` と照らしていない版だけに書き、照らした数 `engine_unresolved_total` と同じ取り込みに書かない。v0.113 の 237・238。`unresolved_counts` の今の数は、照らした最後の取り込みまでで数える）。範囲の id は、どれかの記録か `not_imported` のどちらか一方にないとエラー。`imported_rulings`・`unresolved_rulings` は対応から求めたものと同じでないとエラー。1 つの取り込みの中で同じ接頭辞を 2 つの文書に使わない。`not_imported` の各項目に `status`（`excluded`: エンジンの実装の判断（実装上の仮定・実装上の扱い・実装の設計）で取り込まない、`deferred`: 保留（kyuura が原典を確かめていない・対象のカードを調べていない）、`needs_recheck`: 要再確認）。裁定の表のない版（実装の履歴。v0.14〜v0.16）は `no_ruling_tables: true` で、`ruling_sets`・`not_imported` を持たず、読んだ文書とルールに関わる記述を `notes` に書く。v0.26 からの取り込みは、`not_imported` の各項目に `classification`（`official_confirmed` エンジンが CONFIRMED とした当てはめ・`supported_interpretation` 研究上の解釈・`unresolved_rules_question` 既存の論点の当てはめ・`engine_assumption` 実装上の仮定・`engine_adopted_spec` 採用した仕様・`engine_implementation` 実装の都合・`notation_difference` 表記の違い・`card_text_application` 処理の記録）を書き、`status` に `card_application`（カードごとの当てはめ。新しい裁定にしない）・`existing_record`（`kyuura_records` の既存の記録の当てはめ）・`adopted_spec`（`engine_position` の記録）も使う。`status` と `classification` の組み合わせが合わないとエラー |
| `engine_positions` | エンジンの採用した仕様（`adopted_spec`）・簡略化した仕様（`simplification`）・実装の事項（`implementation_matter`。不具合・未対応・制限）。`engine_import`・`document`・`section`・`cards`・`engine_rulings`・`summary`・`engine_basis`・`kyuura_records`・`kyuura_handling`。公式の裁定ではないので `status`・`conclusion` を持たない（持つとエラー）。実装の事項は `engine_fix`（`state`: `fixed` その版で直した（エンジンの報告）・`not_fixed` その版の時点で直していない・`document_corrected` 文書の訂正（処理は変えていない）、`as_of`: 取り込みの版、`tests`）で、修正済み・未修正・文書の訂正を分けられる（v0.113 のESPの 3 件・ゆうでんの FC1 の制限）。採用した仕様の `engine_rulings` は、その取り込みの `not_imported` に `adopted_spec` として結ぶ。例: キョウのベトベトンの［だつりょくえき］（v0.68）・イマクニ？のドードーの簡略化・マチスの秘策の受け付けの不具合 |
| `engine_unresolved_index` | エンジンの未解決の裁定の一覧（件数は取り込みとともに増える。過去の件数を総数として固定しない）。`disposition` は `issue`（論点 `kyuura_issue` に取り込んだ）・`implementation_only`（歴史上の論点ではない）・`out_of_scope`（取り込みの範囲の外。取り込んだ版のものには使えない）・`not_yet_imported`（その版の取り込みがまだない。段階を分けた取り込みの途中だけで、取り込んだ版のものには使えない）。`issue` 以外は `reason` が必要。`question_kind` は問いの性質（`historical`）。`instances` は、同じ問いのあとの版の事例（`engine_version`・`ruling_id`。v0.17 の Z13 は C18 と同じ問い、など）で、新しい項目にしない（事例は同じ論点の `engine_refs` に結ぶ）。`in_engine_count: false` は、エンジンの数え方の件数に入らない項目（v0.17 のキョウのベトベトン。カードを延期したので、エンジンは数えていない）。`counted_from_version` は、あとの版から数えるようになった項目のその版（DR8・DR13 は v0.68 から）。`stop_code_since`・`stop_code_note` は、コードのない問いとして取り込んだあとでエンジンが停止コードを付けた版（エンジンの文書で最初に見える版）。過去の版の数は `unresolved_counts(ctx, as_of='v0.25')` のように求める。取り込みの `engine_unresolved_total` は、その版までの項目のうちエンジンが数えるものの件数と同じ（v0.13 は 22、v0.17 は 24）。kyuura の論点の数・エンジンの数・停止コードの数は別の数で、`scripts/build_card_rulings.py` の `unresolved_counts` が分けて求める（生成するページの 8 章「未解決の数の区別」） |

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
print(bcr.annotations_for(ctx, 'PMCG1-002'))  # 記録のないカード
print(bcr.find_engine_ruling(ctx, 'v0.7', 'S1'))  # エンジンの版と id から kyuura の記録を引く（v0.13 の S1 とは別）
```
