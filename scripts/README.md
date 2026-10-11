# 生成スクリプト

`docs/cards/*.md` と `data/cards.{json,csv}` は、次の手順で作り直せます。

```sh
WORK=/path/to/workdir
git clone --depth 1 https://github.com/tcgdex/cards-database.git "$WORK/cards-database"
git clone --depth 1 https://github.com/PokemonTCG/pokemon-tcg-data.git "$WORK/pokemon-tcg-data"
curl -sS -o "$WORK/pokemon_species_names.csv" \
  https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_names.csv

# TCGdex の TypeScript 定義を JSON に変換（Node.js 18 以降）
node scripts/ts2json.mjs "$WORK/cards-database" "$WORK/jp.json"

# 日本語テキストを取得・抽出（なぞのばしょ。取得は 1.5 秒間隔で約 450 ページ）
python3 scripts/nazonobasho.py fetch --cache "$WORK/nazonobasho"
python3 scripts/nazonobasho.py extract --cache "$WORK/nazonobasho" --out data/ja_text_nazonobasho.json

# 日本語テキストを変換（ポケモンWiki。ブラウザで保存したデータ data/raw/*.json から。ネットワークは使わない）
python3 scripts/pokemonwiki.py --raw data/raw --out data/ja_text_pokemonwiki.json

# 拡張パック以外の商品（拡張シート、サザンアイランド、ジムデッキ、クイックスターターギフト、イントロパック、プレミアムファイル、プロモ）を取得・抽出（pcg-search.com。取得は 2 秒間隔で約 680 ページ）
python3 scripts/pcg_search.py fetch --cache "$WORK/pcgsearch"
python3 scripts/pcg_search.py extract --cache "$WORK/pcgsearch" --out data/ja_text_pcgsearch.json

# カードリストを生成（Python 3.9 以降、標準ライブラリのみ）
python3 scripts/build_cardlist.py --jp "$WORK/jp.json" \
  --en "$WORK/pokemon-tcg-data" --species "$WORK/pokemon_species_names.csv"

# 日米のルールの違いのページを生成（data/rule_differences.json → docs/rules/differences.md）
python3 scripts/build_rule_differences.py

# ルール・エラッタの履歴を検査し、エラッタの履歴のページを生成（data/rule_history.json → docs/rules/errata-history.md）
python3 scripts/build_rule_history.py

# 拡張パック以外の商品のページと、再録の対応付けのページを生成（→ docs/cards/other-products.md、docs/cards/products/*.md、docs/cards/reprints.md）
python3 scripts/build_other_products.py

# 生成物が元データと合っているかだけを検査（ファイルは書き換えない。食い違いや参照切れがあれば終了コード 1）
python3 scripts/build_rule_differences.py --check
python3 scripts/build_rule_history.py --check
```

生成されるもの:

| スクリプト | 出力 |
|---|---|
| `build_cardlist.py` | `data/cards.json`、`data/cards.csv`、`data/attacks.csv`、`data/powers.csv`、`docs/cards/` の各弾のページ・`card-differences.md`・`english-only.md` |
| `build_rule_differences.py` | `docs/rules/differences.md`（あわせて出典の記号・`data/rule_history.json` の id の参照切れと、確度の更新漏れを検査） |
| `build_rule_history.py` | `docs/rules/errata-history.md`（あわせて `data/rule_history.json` と `docs/rules/mixed-2002.md`・`kangaskhan-2002.md` の id・カード id・出典の記号の参照切れと、日付の矛盾（公表・適用の順、出来事の日付との食い違い、誤りと判断した日付の使用）を検査） |
| `nazonobasho.py extract` | `data/ja_text_nazonobasho.json`（日本語テキスト。カードテキストと印刷情報の欄だけを残す） |
| `pcg_search.py extract` | `data/ja_text_pcgsearch.json`（拡張パック以外の商品の 681 枚） |
| `build_other_products.py` | `docs/cards/other-products.md`（一覧）、`docs/cards/products/*.md`（商品ごと）、`docs/cards/reprints.md`（再録の対応付けと点検の結果） |
| `pokemonwiki.py` | `data/ja_text_pokemonwiki.json`（`data/raw/` のポケモンWiki のデータを、なぞのばしょと同じ形に変換したもの） |

`build_cardlist.py` は、日本語テキストの出典ごとに、カードと英語版データの数値（HP・コスト・ダメージ・にげる）やカード名の食い違いを `data/ja_text_<出典>_report.json`（`nazonobasho`・`pokemonwiki`）に書き出します。`data/curation/<出典>_review.json` に判定のない食い違いがあると、実行時に一覧を表示します。

- 同じカードが両方の出典にあるときは、なぞのばしょを使います（現在は重なりなし）。
- ポケモンWiki のデータには、保存した人が付けたカード id の候補（`kyuura_card_id`）があり、照合の手がかりにしています。

`data/raw/` はポケモンWiki のカードページをブラウザで保存し、カードごとの欄を抜き出した JSON です（手で用意する元データ。弾ごとに 1 ファイル）。

`data/rule_differences.json`・`data/rule_history.json` は手で編集する元データです（生成物ではありません）。

手作業で作った補正データは `data/curation/` にあります。

| ファイル | 内容 |
|---|---|
| `trainers.json` | トレーナー・エネルギーの日本版 ↔ 英語版の対応と、日本語の公式名、その確認状況 |
| `pokemon_overrides.json` | 自動照合できないポケモンの対応付け（出典データの名前の誤り、アンノーンの文字など） |
| `naming.json` | 英語版の接頭辞（Light、Rocket's）の日本語表記、アンノーンの表記 |
| `jp_only.json` | 英語版に対応カードがない日本版カード |
| `card_differences.json` | カードごとの日英の違い（文面・エラッタ・収録先・表記） |
| `ja_text.json` | 日本版の公式テキストの手入力用（なぞのばしょ・ポケモンWiki より優先）。現在はなぞのばしょの誤記を直した 1 枚（ポケモンジャングルのプリン） |
| `nazonobasho_map.json` | なぞのばしょのページとカードの対応を手で決めたもの（自動で決まらないもの） |
| `nazonobasho_review.json` | なぞのばしょと英語版データの数値の食い違いの判定 |
| `pokemonwiki_map.json` | ポケモンWiki のページとカードの対応を手で決めたもの |
| `pokemonwiki_review.json` | ポケモンWiki と英語版データの食い違いの判定 |
| `other_products.json` | 拡張パック以外の商品の発売日、デッキ・シートの構成、プロモの配布方法、英語版の対応、日英の違い、イントロパックのカードの Bulbapedia のページ、再録の文面の書き換えの分類 |
| `en_fixes.json` | 英語版カードデータの誤りの補正（ワザのダメージ・効果文・名前・コスト） |
| `sets.json` | 各弾の名前・発売日・収録数 |

最後に生成したときの出典データ:

- tcgdex/cards-database `4199850a6af49665db0080fa2bb9ef751750a406`
- PokemonTCG/pokemon-tcg-data `39a26a144c8b6ef6c2fb17b2c29d0bb7121e3a11`
