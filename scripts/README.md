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

# 進化元・にげるを確かめるために、拡張パック以外の商品のカードページの一部を読み直す（2026-10-19 は 187 ページ。全ページは取り直さない）。
# URL の一覧は data/pcgsearch_page_checks.json の pages の url。転記（ja_text_pcgsearch.json）と違う欄は transcript_differences に残る
python3 -c "import json;[print(v['url']) for v in json.load(open('data/pcgsearch_page_checks.json'))['pages'].values()]" > "$WORK/page_urls.txt"
python3 scripts/pcg_search.py fetch-pages --cache "$WORK/pcgcheck" --urls "$WORK/page_urls.txt"
python3 scripts/pcg_search.py extract-pages --cache "$WORK/pcgcheck" --urls "$WORK/page_urls.txt" \
  --checked-on 2026-10-19 --out data/pcgsearch_page_checks.json

# カードリストを生成（Python 3.9 以降、標準ライブラリのみ）。拡張パック以外の商品の記録（scripts/non_pack.py）・
# 訂正の記録（data/curation/card_corrections.json）の当てはめ・同じカードの組もここで作る。--check は書き換えずに比べる
python3 scripts/build_cardlist.py --jp "$WORK/jp.json" \
  --en "$WORK/pokemon-tcg-data" --species "$WORK/pokemon_species_names.csv" [--check]

# kyuura-engine の登録表の写しを作り直す（エンジンの版を上げるときだけ。決まったコミットの木を git archive で展開して使う）
# 前の写しの参照（版・コミット・取得日・件数）は previous_snapshots に残る（2026-10-27 に v0.68 から v0.113 に上げた）
python3 -I scripts/snapshot_engine_registry.py --engine "$WORK/kyuura-engine-2d113b5" --commit 2d113b5eeea0dbd4f7466e144f7a1345494405c0 \
  --branch claude/v0.113-variable-coins-search-attachments --version v0.113 --extracted-on 2026-10-27

# エンジンの実装の対象の一覧を生成（data/curation/engine_registered_cards.json・data/cards.json → data/engine_targets.json、docs/engine-targets.md）
python3 scripts/build_engine_targets.py

# 日米のルールの違いのページを生成（data/rule_differences.json → docs/rules/differences.md）
python3 scripts/build_rule_differences.py

# ルール・エラッタの履歴を検査し、エラッタの履歴・版ごとの比較・印刷物の照合記録のページを生成
# （data/rule_history.json → docs/rules/errata-history.md、docs/rules/japanese-editions.md、docs/printed-sources.md）
python3 scripts/build_rule_history.py

# カードの最新の説明・照合・裁定（サイドカー）を検査し、ページを生成（data/sidecar/ → docs/rules/card-rulings.md）
python3 scripts/build_card_rulings.py

# 拡張パック以外の商品のページと、再録の対応付けのページを生成（→ docs/cards/other-products.md、docs/cards/products/*.md、docs/cards/reprints.md）
python3 scripts/build_other_products.py

# 生成物が元データと合っているかだけを検査（ファイルは書き換えない。食い違いや参照切れがあれば終了コード 1）
python3 scripts/build_rule_differences.py --check
python3 scripts/build_rule_history.py --check
python3 scripts/build_card_rulings.py --check
python3 scripts/build_other_products.py --check
python3 scripts/build_engine_targets.py --check

# サイドカーの検査のテスト（破壊テストを含む。標準ライブラリだけ）
python3 -m unittest discover -s tests

# 調査の状況（docs/research-status.md）の数を数える（読むだけ）
python3 scripts/research_stats.py
```

生成されるもの:

| スクリプト | 出力 |
|---|---|
| `build_cardlist.py` | `data/cards.json`、`data/cards.csv`、`data/attacks.csv`、`data/powers.csv`、`data/product_items.json`（拡張パック以外の商品の元の項目の行き先）、`data/same_card_groups.json`（商品をまたいだ同じカードの組）、`docs/cards/` の各弾のページ・`card-differences.md`・`english-only.md`。`--check` で書き換えずに比べる（外部の入力は下の記録した版を使う） |
| `non_pack.py` | `build_cardlist.py` が使う。拡張パック以外の商品の転記を `data/cards.json` の記録の形にする（id・欄・進化元・にげる・同じカードの組・値の欠け。規則は [データの構造](../docs/data-schema.md#拡張パック以外の商品の記録)） |
| `pcg_search.py fetch-pages`・`extract-pages` | `data/pcgsearch_page_checks.json`（読み直したカードページの、転記にない欄・区別と、転記との違い） |
| `snapshot_engine_registry.py` | `data/curation/engine_registered_cards.json`（kyuura-engine の決まったコミットの登録表と対戦用のカード id の写し。エンジンのコードを読み込むので信頼できる木だけに使う） |
| `build_engine_targets.py` | `data/engine_targets.json`、`docs/engine-targets.md`（記録ごとの実装の対象の分類とエンジンの登録との対応）。`--check` |
| `build_rule_differences.py` | `docs/rules/differences.md`（あわせて出典の記号・`data/rule_history.json` の id の参照切れと、確度の更新漏れを検査） |
| `build_rule_history.py` | `docs/rules/errata-history.md`、`docs/rules/japanese-editions.md`（日本版のルールの版ごとの比較）、`docs/printed-sources.md`（スキャンで確認した印刷物の巻号・ページ）。あわせて `data/rule_history.json` と `docs/rules/mixed-2002.md`・`kangaskhan-2002.md`・`japanese.md` の id・カード id・出典の記号の参照切れ、日付の矛盾（公表・適用の順、出来事の日付との食い違い、誤りと判断した日付の使用、印刷テキストの変更・公式エラッタで新しい文面の印刷の日付を適用の開始に書いていないか、印刷の開始と段階の日付の食い違い）、版の日付と出来事の食い違い、比較表の項目と `data/rule_differences.json` の対応と確度の食い違い、比較表で二次資料・推定だけのマスを「確実」にしていないか、公式エラッタに分類した記録に確認できた公式の告知の段階と当時の資料での呼び方（`term_in_sources`）があるか、原本との照合を書いた記録に原本の根拠があるか、スキャンを根拠にした記録の資料が `documents` にあるかを検査 |
| `build_card_rulings.py` | `docs/rules/card-rulings.md`。あわせて `data/sidecar/` の id の書式・重複、カード id とワザの位置・名前、印刷の文面と照合した欄の写しが今の `data/cards.json` と同じか、違いの文字列が文面にあるか、出典の記号とページ（`data/rule_history.json` の `documents`）、公式エラッタの記録との結び付け、CONFIRMED・SUPPORTED の根拠と推論、裁定の文にエンジンの停止コード・例外の名前がないか、エンジンの裁定 id の対応（版ごとの取り込み `engine_imports` の文書・裁定の組の範囲。id は文書ごとにしか一意でないので（取り込み, 文書, id）で数える。漏れ・二重の対応・`not_imported` との重なり・別の版の文書・範囲外の id・分けた対応の `part`）、エンジンの分類と kyuura の分類の食い違い（`reclassification` の有無）、一般規定の記録（`rule_clauses`）に対応させたエンジンの裁定が CONFIRMED か、同じ問いの裁定・未解決の論点の重複、カードの照合の `no_difference` と最新の説明の違いの食い違い、データの誤りの候補（`data_error`）の書式、エンジンの未解決の裁定の一覧（`engine_unresolved_index`）の件数・扱い（`disposition`）・理由を検査 |
| `nazonobasho.py extract` | `data/ja_text_nazonobasho.json`（日本語テキスト。カードテキストと印刷情報の欄だけを残す） |
| `pcg_search.py extract` | `data/ja_text_pcgsearch.json`（拡張パック以外の商品の 681 枚） |
| `build_other_products.py` | `docs/cards/other-products.md`（一覧）、`docs/cards/products/*.md`（商品ごと）、`docs/cards/reprints.md`（再録の対応付けと点検の結果）。`--check` |
| `pokemonwiki.py` | `data/ja_text_pokemonwiki.json`（`data/raw/` のポケモンWiki のデータを、なぞのばしょと同じ形に変換したもの） |
| `research_stats.py` | 出力なし（標準出力に表示するだけ）。出典の記号の区分（`docs/sources.md`）、ルールの記録の確度・根拠の種類・エラッタの段階・版の比較表のマス、カードの日本語テキストと数値の出典、日英の違い、再録の組を数える。`docs/research-status.md` の数はこの出力による |

`build_cardlist.py` は、日本語テキストの出典ごとに、カードと英語版データの数値（HP・コスト・ダメージ・にげる・タイプ・弱点・抵抗力）やカード名の食い違いを `data/ja_text_<出典>_report.json`（`nazonobasho`・`pokemonwiki`）に書き出します。`data/curation/<出典>_review.json` に判定のない食い違いがあると、実行時に一覧を表示します。

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
| `sets.json` | 各弾の名前・発売日・収録数。資料によって発売日が違う弾は `release_note` に別の日付とその資料を書く（各弾のページの発売日の後ろに表示） |
| `non_pack.json` | 拡張パック以外の商品の記号（id の規則）、番号違いのまとめ、対戦のカードでない項目、補足欄の役割、使える範囲（`play_scope`）、収録していない商品・範囲（`uncovered_products`） |
| `card_corrections.json` | カードデータの訂正の記録（生成のたびに当てはめる。当てはめる前の値が違えば止まる）と、訂正しなかった候補とその理由 |
| `card_image_checks.json` | kyuura がカードの画像で印刷の欄を読んだ記録（`IMG-`。2026-10-27 のベイビィ 13 枚から）。`build_cardlist.py` が、画像の値・訂正の記録・生成した値が同じかを確かめる（違えば止まる） |
| `engine_registered_cards.json` | kyuura-engine の固定した版の登録表の写し（生成物。`snapshot_engine_registry.py`） |

最後に生成したときの出典データ:

- tcgdex/cards-database `4199850a6af49665db0080fa2bb9ef751750a406`
- PokemonTCG/pokemon-tcg-data `39a26a144c8b6ef6c2fb17b2c29d0bb7121e3a11`
- pcg-search.com のカードページの読み直し 2026-10-19（`data/pcgsearch_page_checks.json`）
- kyuura-engine `2d113b5eeea0dbd4f7466e144f7a1345494405c0`（v0.113。`data/curation/engine_registered_cards.json`。2026-10-27 に作り直した。その前は `24bfbe2c1bf3b5fb0521e229ac92cf2fa4a154a1`（v0.68）で、`previous_snapshots` に残す）
- カードの画像の照合の記録 `data/curation/card_image_checks.json`（2026-10-27。生成の入力ではなく、生成した値と照らす記録）

2026-10-19 に、この入力で `build_cardlist.py --check` が今のファイルと同じになることを確かめました（20 ファイル）。2026-10-27 にも同じ入力（tcgdex・pokemon-tcg-data は上のコミット）で確かめました（20 ファイル）。
