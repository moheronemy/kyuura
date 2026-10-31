# エンジンの実装の対象

<!-- このファイルは scripts/build_engine_targets.py が data/cards.json・data/curation/engine_registered_cards.json などから生成しています。直接編集せず、データを直してから再生成してください。 -->

kyuura の記録（`data/cards.json`）ごとに、エンジンの実装の対象にできるか（category）と、kyuura-engine v0.113（ブランチ `claude/v0.113-variable-coins-search-attachments`、コミット `2d113b5`）の登録との対応（engine_status）を、機械で読める一覧 [`data/engine_targets.json`](../data/engine_targets.json) にまとめています。この一覧は kyuura のデータとエンジンの登録表の写し（[`data/curation/engine_registered_cards.json`](../data/curation/engine_registered_cards.json)。2026-10-27 に scripts/snapshot_engine_registry.py で作成）から作ったもので、エンジンの実装の状況の正本はエンジンのリポジトリです。写しの `registry_id`（`kyuura-engine-0.13`）は登録表の名前で、版の番号ではありません（版は上の v0.113）。

前の写しの参照（その時点の取得日・件数のまま。中身は git の履歴にあります。研究の取り込みの範囲は別で、[研究の状況](research-status.md) と data/sidecar/rulings.json の engine_imports に書きます）:

- v0.68（コミット `24bfbe2`、2026-10-19 に作成、2026-10-27 に置きかえ）: 対戦用のカード 457、登録のあるカード 451（ワザ 597・トレーナー 94・特殊能力 58・特殊エネルギー 4）

- エンジンの登録はカード id ごとです。登録のない id を、同じ処理のカードがあっても実装済みとは数えません。
- 強さ・勝率・デッキの釣り合いは評価していません。新しいカードの効果は実装していません。
- 印刷の文面・公式の最新の説明・公式エラッタ・研究上の解釈・エンジンの採用した仕様は別のものです。この一覧の「同じ」は kyuura の転記の欄が同じことで、最新の説明やエラッタが同じように当てはまるかは、登録するときにエンジンが確かめます。

## 分け方

| 欄 | 値 | 意味 |
|---|---|---|
| category | `candidate` | 対象にできる |
| category | `data_missing` | 値の欠けがある |
| category | `special_rule_design` | 特別なルールの設計が要る |
| category | `non_game` | 対戦のカードでない |
| engine_status | `registered` | 登録あり（エンジンの対戦用のカード id） |
| engine_status | `mechanically_equivalent` | 登録されたカードと処理に使う欄が同じ（id は未登録） |
| engine_status | `reuse_candidate` | 再利用の候補（確かめてから登録） |
| engine_status | `new_effect_needed` | 新しい効果の実装が要る |

- `data_missing` の理由（category_reasons）は、記録の `data_gaps` のうちエンジンが使う欄（名前・段階・進化元・ベイビィの進化先・HP・タイプ・ルールの文・特殊能力・ワザの名前と説明・トレーナーと特殊エネルギーの説明）の欠けです。ベイビィの進化先（`pokemon.evolves_to`）はエンジンの写しがまだ取り出さない欄ですが、進化できるカードを決めるので、欠け（未確認）と、登録されたカードと同じかの比べに含めます。図鑑番号・レベル・シリーズの欠けは数えません。
- `special_rule_design` は `play_scope` が `standard` でない記録（公式大会で使えないと書かれたカード。ガルーラルール専用のカードは 2026-10-31 から対象外の記録）。
- `mechanically_equivalent` は、エンジンが使う欄がすべて登録されたカードと同じで、ワザ・特殊能力・トレーナー・特殊エネルギーの名前と説明が、エンジンが登録のときに照合した文面（`text_ja`）とも同じもの（`equivalent_to` に登録されたカード）。
- `reuse_candidate` は、同じカードの組（`same_card_group`。名前・HP・特殊能力名・ワザ名が同じ）に登録されたカードがあって欄の一部が違うもの（`reuse_basis: same_card_group`。`nearest_registered` の `differences`）か、効果の文面がどれも登録された実装の文面と同じもの（`reuse_basis: registered_effect_texts`。`effects_with_registered_text`）。名前が同じでも別のカード（HP・ワザが違う）は組にならない。
- `new_effect_needed` は、登録された実装と同じ文面のない効果（`effects_without_registered_text`）があるもの。文面が違っても既存の実装で処理できる場合はある（エンジンが文面の形を確かめて決める）。
- `released_after_rule_base` は、発売日が公式ルール 2000.02.14版の日付（2000-02-14）より後か。後に出たカードは、その時点の公式ルールで処理が決まっているとは限りません（実装の対象から外すものではない。ルールの版の判断に使う）。日付が分からなければ null。

## 数

記録 1374 件（通常対戦のエンジンの対象。このほか、対象から外した記録 3 件（`excluded_records`）と、対戦のカードでない項目 18 件（`non_game_items`））。`data/cards.csv` の目録だけの行（`data/curation/catalog_items.json` の `KC-` の項目）は、この一覧に入れていません。

| 商品の種類 | 記録 | `registered` | `mechanically_equivalent` | `reuse_candidate` | `new_effect_needed` | `candidate` | `data_missing` | `special_rule_design` |
|---|---|---|---|---|---|---|---|---|
| 拡張パック | 780 | 723 | 0 | 0 | 57 | 779 | 1 | 0 |
| 拡張シート | 108 | 91 | 0 | 0 | 17 | 108 | 0 | 0 |
| ポケモンジムのデッキ | 153 | 147 | 1 | 0 | 5 | 147 | 6 | 0 |
| イントロパック | 96 | 92 | 0 | 1 | 3 | 94 | 2 | 0 |
| プレミアムファイル | 27 | 20 | 0 | 0 | 7 | 27 | 0 | 0 |
| プロモ | 134 | 105 | 0 | 4 | 25 | 132 | 0 | 2 |
| クイックスターターギフト | 58 | 56 | 0 | 0 | 2 | 58 | 0 | 0 |
| サザンアイランド | 18 | 16 | 0 | 0 | 2 | 18 | 0 | 0 |
| 計 | 1374 | 1250 | 1 | 5 | 118 | 1363 | 9 | 2 |

## 登録されたカードと処理に使う欄が同じ記録（mechanically_equivalent）

1 件。エンジンが登録するときは、同じ登録をこの id にも加え、最新の説明・エラッタが同じように当てはまるかを確かめます。

| id | 名前 | 同じ欄の登録 | category |
|---|---|---|---|
| `GD5-007` | カツラのウィンディ | `PMCG6-034` | `candidate` |

## 再利用の候補（reuse_candidate。拡張パック以外の商品）

5 件。違う欄（differences）を確かめてから登録します。拡張パック（neo）の候補は `data/engine_targets.json` にあります。

| id | 名前 | いちばん近い登録 | 違う欄 |
|---|---|---|---|
| `IP2-032` | ウィンディ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PR1-001` | ピカチュウ | `IP1-040` | pokemon.attacks[0].text.ja |
| `PR1-003` | ピカチュウ | `IP1-040` | pokemon.attacks[0].text.ja |
| `PR1-017` | ピカチュウ | `IP1-040` | pokemon.attacks[0].text.ja |
| `PRN-030` | カポエラー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |

## 新しい効果の実装が要る記録（new_effect_needed。拡張パック以外の商品）

61 件。拡張パック（neo）の記録は `data/engine_targets.json` にあります。

| id | 名前 | 登録された文面のない効果 | category |
|---|---|---|---|
| `GD1-010` | タケシのイワーク | attack1「ちていいどう」 | `candidate` |
| `GD2-007` | カスミのパルシェン | power0「シェルアーマー」 | `candidate` |
| `GD3-003` | マチスのライチュウ | attack1「10まんボルト」 | `candidate` |
| `GD5-016` | カツラのクイズ その1 | trainer「カツラのクイズ その1」 | `candidate` |
| `GD6-005` | ナツメのゴース | attack1「ぱっときえる」 | `candidate` |
| `ES1-027` | プクリン | power0「てだすけ」、attack0「ふくらむ」 | `candidate` |
| `ES2-005` | ファイヤー | attack0「ドライアップ」 | `candidate` |
| `ES2-011` | オムナイト | power0「げんしのゆめ」 | `candidate` |
| `ES2-028` | カブト | power0「かせきか」 | `candidate` |
| `ES2-029` | プテラ | attack1「きりもみアタック」 | `candidate` |
| `ES2-032` | メタモン | power0「すごいへんしん」 | `candidate` |
| `ES2-035` | フラッシュ | trainer「フラッシュ」 | `candidate` |
| `ES3-006` | ウツドン | attack0「さいせい」 | `candidate` |
| `ES3-007` | マタドガス | power0「ポイズンミスト」、attack0「ガスばくはつ」 | `candidate` |
| `ES3-016` | シードラ | attack0「ウォーターボム」 | `candidate` |
| `ES3-017` | ヒトデマン | attack0「なぞのこうせん」 | `candidate` |
| `ES3-018` | オムナイト | power0「かせきのみちびき」 | `candidate` |
| `ES3-020` | ユンゲラー | attack0「エナジーさいせい」、attack1「エナジーショック」 | `candidate` |
| `ES3-021` | ヤドラン | attack0「おおあくび」、attack1「おおいびき」 | `candidate` |
| `ES3-025` | スリーパー | power0「にんぎょうつかい」 | `candidate` |
| `ES3-029` | ゴローン | attack0「がんせきくだき」 | `candidate` |
| `ES3-032` | ピジョン | attack0「ツイスター」、attack1「そらをとぶ」 | `candidate` |
| `QSG-027` | ユンゲラー | attack0「エナジーさいせい」、attack1「エナジーショック」 | `candidate` |
| `QSG-055` | ファイヤー | attack0「ドライアップ」 | `candidate` |
| `SI-008` | フシギソウ | attack0「ふしぎなかおり」 | `candidate` |
| `SI-011` | ラフレシア | attack0「ごくらくかふん」、attack1「さいあくかふん」 | `candidate` |
| `PR1-016` | ウィンディ | attack1「いかりのほのお」 | `candidate` |
| `PR1-021` | ミュウ | attack1「サイコデュープ」 | `candidate` |
| `PR1-022` | ミュウツー | attack0「エナジーコントロール」、attack1「テレキネシス」 | `candidate` |
| `PR1-025` | ニャース | attack1「まるもうけ」 | `candidate` |
| `PR1-027` | とりかえっこプリーズ | trainer「とりかえっこプリーズ」 | `special_rule_design` |
| `PR1-043` | カイリュー | power0「トランスポート」、attack0「マッハひこう」 | `candidate` |
| `PR1-044` | _のピカチュウ | attack0「おたんじょうび」 | `candidate` |
| `PR1-054` | ゴローニャ | attack1「ロックブラスト」 | `candidate` |
| `PR1-055` | フーディン | attack1「トランスダメージ」 | `candidate` |
| `PR1-065` | トゲピー | attack0「なきつく」、attack1「ゆびをふる」 | `candidate` |
| `PR1-068` | サカキのニドキング | power0「めいれい」 | `candidate` |
| `PR1-072` | ハマちゃんのヤドキング | attack0「こまったなあ」、attack1「どつく」 | `candidate` |
| `PR1-073` | カスミのてあて | trainer「カスミのてあて」 | `special_rule_design` |
| `PR1-075` | ナッシー［Exeggutor］ | attack0「ふみつけ[Stomp]」 | `candidate` |
| `PR1-077` | ナッシー［Exeggutor］ | attack0「ふみつけ[Stomp]」 | `candidate` |
| `PR1-090` | _のピカチュウ | attack0「おたんじょうび」 | `candidate` |
| `PF2-006` | ブラッキー | attack1「おいうち」 | `candidate` |
| `PF2-007` | ピチュー | rules_text「」、attack0「いっしょにあそぼ」 | `candidate` |
| `PF3-001` | ウソッキー | power0「ものまね」 | `candidate` |
| `PF3-004` | ライコウ | power0「でんせつのからだ」 | `candidate` |
| `PF3-005` | エンテイ | power0「でんせつのからだ」、attack0「メガフレイム」 | `candidate` |
| `PF3-006` | スイクン | power0「でんせつのからだ」、attack0「クリスタルウェーブ」 | `candidate` |
| `PF3-008` | ルギア | attack0「エアロウイング」 | `candidate` |
| `NIP1X-002` | ブビィ | rules_text「」 | `candidate` |
| `NIP1X-004` | イシツブテ | attack0「いしなだれ」 | `candidate` |
| `NIP2X-002` | ピチュー | rules_text「」 | `candidate` |
| `PRN-001` | ヤミカラス | attack1「おいうち」 | `candidate` |
| `PRN-012` | ピィ | rules_text「」、attack0「ピッピッ」 | `candidate` |
| `PRN-031` | ププリン | rules_text「」 | `candidate` |
| `PRN-036` | ムウマ | attack0「いたみわけ」 | `candidate` |
| `PRN-037` | ムチュール | rules_text「」、attack0「なげキッス」 | `candidate` |
| `PRN-039` | わるいフシギソウ | power0「つるでひっぱる」、attack0「みだれうち」 | `candidate` |
| `PRN-040` | わるいフシギバナ | attack0「いやなかふん」 | `candidate` |
| `PRN-041` | GR団のミュウツー | power0「わるいはどう」、attack0「わるいぞうふく」 | `candidate` |
| `PRN-045` | わるいオニドリル | attack0「たかくとぶ」、attack1「ドリルダイブ」 | `candidate` |

## 値の欠け・特別なルールの記録（拡張パック以外の商品）

| id | 名前 | category | 理由 |
|---|---|---|---|
| `GD1-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD2-024` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD3-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD4-028` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD5-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD6-026` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `IP1-023` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `IP2-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `PR1-027` | とりかえっこプリーズ | `special_rule_design` | play_scope: not_for_official_tournaments |
| `PR1-073` | カスミのてあて | `special_rule_design` | play_scope: not_for_official_tournaments |

## 登録のあとで kyuura の値が変わったカード

エンジンが登録のときに照合した値（写しの元のコミットの値にエンジンの補正を当てはめたもの）と、今の kyuura の値が違う欄です。エンジンが写しのコミットを上げるときに確かめます。

ありません。

## 通常対戦のエンジンの対象から外した記録（excluded_records）

`data/cards.json` の記録のうち、`catalog_class` が `battle` でないか `engine_scope` が `target` でないもの（`data/curation/non_pack.json` の `catalog_scope` の明示の指定）。目録の分類と実装範囲の指定で、公式の裁定・エラッタ・印刷の訂正ではありません。カードの記録・文面・id は `data/cards.json` に残っています。エンジンの登録表の写しは変えていません（エンジンの取り込みは [引き継ぎ](engine-handover-catalog-scope.md)）。

| id | 名前 | catalog_class | play_scope | 理由 |
|---|---|---|---|---|
| `PR1-038` | タッチ交代！ | `special_rule` | `kangaskhan_rule` | ガルーラルール専用のカード（専用ルールで使う。通常の対戦のカードではない）。通常対戦のエンジンの実装の対象から外す |
| `PR1-079` | カードトレーナー認定証 | `award` | `standard` | 認定証のカード（本文はチャレンジパスポートの記録による公式カードトレーナーの認定で、対戦の手順を書いていない）。通常対戦のエンジンの実装の対象から外す |
| `PRN-048` | タッチ世代交代！ | `special_rule` | `kangaskhan_rule` | 新ガルーラルール専用のカード（専用ルールで使う。通常の対戦のカードではない）。通常対戦のエンジンの実装の対象から外す |

## 対戦のカードでない項目（non_game）

`data/cards.json` に入れず、`data/product_items.json` の `non_game_items` に元の項目から追えるように残しています。

| 項目の id | 元のページ | 名前 | 種類 |
|---|---|---|---|
| `ES3-037` | `1stex3037` | サイドカード4枚戦 | `extra_rule` |
| `ES3-038` | `1stex3038` | 「こんらん」で20ダメージルール | `extra_rule` |
| `ES3-039` | `1stex3039` | 3デッキ戦 | `extra_rule` |
| `ES3-040` | `1stex3040` | ダグトリオチームバトル 3vs3 | `extra_rule` |
| `ES3-041` | `1stex3041` | デッキ交換戦 | `extra_rule` |
| `ES3-042` | `1stex3042` | ポケモンタワーのなぞ? | `deck_recipe` |
| `ES3-043` | `1stex3043` | ポケモンやしきでアッチッチ! | `deck_recipe` |
| `ES3-044` | `1stex3044` | サファリゾーンでおおあばれ! | `deck_recipe` |
| `ES3-045` | `1stex3045` | ふたごじまのタッツー | `deck_recipe` |
| `ES3-046` | `1stex3046` | ハナダ!さいごのどうくつ | `deck_recipe` |
| `ES3-047` | `1stex3047` | オーヤマのピカチュウ | `joke_card` |
| `ES3-048` | `1stex3048` | イマクニ?のわるだくみ | `other` |
| `ES3-049` | `1stex3049` | - | `other` |
| `ES3-050` | `1stex3050` | - | `other` |
| `ES3-051` | `1stex3051` | - | `other` |
| `ES3-052` | `1stex3052` | イマクニ?のパソコン | `pass_card` |
| `ES3-053` | `1stex3053` | マサキのパソコン | `pass_card` |
| `PR1-015` | `1stp015` | ポケモンイラストレーター | `award` |
