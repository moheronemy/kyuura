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

# カードリストを生成（Python 3.9 以降、標準ライブラリのみ）
python3 scripts/build_cardlist.py --jp "$WORK/jp.json" \
  --en "$WORK/pokemon-tcg-data" --species "$WORK/pokemon_species_names.csv"

# 日米のルールの違いのページを生成（data/rule_differences.json → docs/rules/differences.md）
python3 scripts/build_rule_differences.py
```

生成されるもの:

| スクリプト | 出力 |
|---|---|
| `build_cardlist.py` | `data/cards.json`、`data/cards.csv`、`data/attacks.csv`、`data/powers.csv`、`docs/cards/` の各弾のページ・`card-differences.md`・`english-only.md` |
| `build_rule_differences.py` | `docs/rules/differences.md` |

`data/rule_differences.json` は手で編集する元データです（生成物ではありません）。

手作業で作った補正データは `data/curation/` にあります。

| ファイル | 内容 |
|---|---|
| `trainers.json` | トレーナー・エネルギーの日本版 ↔ 英語版の対応と、日本語の公式名、その確認状況 |
| `pokemon_overrides.json` | 自動照合できないポケモンの対応付け（出典データの名前の誤り、アンノーンの文字など） |
| `naming.json` | 英語版の接頭辞（Light、Rocket's）の日本語表記、アンノーンの表記 |
| `jp_only.json` | 英語版に対応カードがない日本版カード |
| `card_differences.json` | カードごとの日英の違い（文面・エラッタ・収録先・表記） |
| `ja_text.json` | 日本版の公式テキスト（ワザ名・ポケモンパワー・効果文）。現在は空 |
| `sets.json` | 各弾の名前・発売日・収録数 |

最後に生成したときの出典データ:

- tcgdex/cards-database `4199850a6af49665db0080fa2bb9ef751750a406`
- PokemonTCG/pokemon-tcg-data `39a26a144c8b6ef6c2fb17b2c29d0bb7121e3a11`
