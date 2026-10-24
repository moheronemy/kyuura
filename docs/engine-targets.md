# エンジンの実装の対象

<!-- このファイルは scripts/build_engine_targets.py が data/cards.json・data/curation/engine_registered_cards.json などから生成しています。直接編集せず、データを直してから再生成してください。 -->

kyuura の記録（`data/cards.json`）ごとに、エンジンの実装の対象にできるか（category）と、kyuura-engine v0.68（ブランチ `claude/v0.68-final-pmcg-cards`、コミット `24bfbe2`）の登録との対応（engine_status）を、機械で読める一覧 [`data/engine_targets.json`](../data/engine_targets.json) にまとめています。この一覧は kyuura のデータとエンジンの登録表の写し（[`data/curation/engine_registered_cards.json`](../data/curation/engine_registered_cards.json)。2026-10-19 に scripts/snapshot_engine_registry.py で作成）から作ったもので、エンジンの実装の状況の正本はエンジンのリポジトリです。

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

- `data_missing` の理由（category_reasons）は、記録の `data_gaps` のうちエンジンが使う欄（名前・段階・進化元・HP・タイプ・ルールの文・特殊能力・ワザの名前と説明・トレーナーと特殊エネルギーの説明）の欠けです。図鑑番号・レベル・シリーズの欠けは数えません。
- `special_rule_design` は `play_scope` が `standard` でない記録（ガルーラルール専用・公式大会で使えないと書かれたカード）。
- `mechanically_equivalent` は、エンジンが使う欄がすべて登録されたカードと同じで、ワザ・特殊能力・トレーナー・特殊エネルギーの名前と説明が、エンジンが登録のときに照合した文面（`text_ja`）とも同じもの（`equivalent_to` に登録されたカード）。
- `reuse_candidate` は、同じカードの組（`same_card_group`。名前・HP・特殊能力名・ワザ名が同じ）に登録されたカードがあって欄の一部が違うもの（`reuse_basis: same_card_group`。`nearest_registered` の `differences`）か、効果の文面がどれも登録された実装の文面と同じもの（`reuse_basis: registered_effect_texts`。`effects_with_registered_text`）。名前が同じでも別のカード（HP・ワザが違う）は組にならない。
- `new_effect_needed` は、登録された実装と同じ文面のない効果（`effects_without_registered_text`）があるもの。文面が違っても既存の実装で処理できる場合はある（エンジンが文面の形を確かめて決める）。
- `released_after_rule_base` は、発売日が公式ルール 2000.02.14版の日付（2000-02-14）より後か。後に出たカードは、その時点の公式ルールで処理が決まっているとは限りません（実装の対象から外すものではない。ルールの版の判断に使う）。日付が分からなければ null。

## 数

記録 1377 件（このほか、対戦のカードでない項目 18 件。`non_game_items`）。

| 商品の種類 | 記録 | `registered` | `mechanically_equivalent` | `reuse_candidate` | `new_effect_needed` | `candidate` | `data_missing` | `special_rule_design` |
|---|---|---|---|---|---|---|---|---|
| 拡張パック | 780 | 457 | 0 | 48 | 275 | 770 | 10 | 0 |
| 拡張シート | 108 | 0 | 0 | 18 | 90 | 104 | 4 | 0 |
| ポケモンジムのデッキ | 153 | 0 | 52 | 62 | 39 | 146 | 7 | 0 |
| イントロパック | 96 | 0 | 24 | 44 | 28 | 94 | 2 | 0 |
| プレミアムファイル | 27 | 0 | 0 | 2 | 25 | 27 | 0 | 0 |
| プロモ | 137 | 0 | 20 | 14 | 103 | 129 | 4 | 4 |
| クイックスターターギフト | 58 | 0 | 0 | 16 | 42 | 58 | 0 | 0 |
| サザンアイランド | 18 | 0 | 0 | 6 | 12 | 18 | 0 | 0 |
| 計 | 1377 | 457 | 96 | 210 | 614 | 1346 | 27 | 4 |

## 登録されたカードと処理に使う欄が同じ記録（mechanically_equivalent）

96 件。エンジンが登録するときは、同じ登録をこの id にも加え、最新の説明・エラッタが同じように当てはまるかを確かめます。

| id | 名前 | 同じ欄の登録 | category |
|---|---|---|---|
| `GD1-002` | タケシのロコン | `PMCG5-018` | `candidate` |
| `GD1-009` | タケシのゴローニャ | `PMCG5-053` | `candidate` |
| `GD1-011` | タケシのイワーク | `PMCG5-048` | `candidate` |
| `GD1-013` | タケシのサイドン | `PMCG5-055` | `candidate` |
| `GD1-015` | 思い出させる | `PMCG5-071` | `candidate` |
| `GD1-019` | タケシの育て方 | `PMCG5-077` | `candidate` |
| `GD1-025` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `GD2-004` | カスミのドククラゲ | `PMCG5-033` | `candidate` |
| `GD2-008` | カスミのタッツー | `PMCG5-025` | `candidate` |
| `GD2-010` | カスミのトサキント | `PMCG5-026` | `candidate` |
| `GD2-012` | カスミのヒトデマン | `PMCG5-027` | `candidate` |
| `GD2-015` | カスミ | `PMCG5-085` | `candidate` |
| `GD2-016` | カスミのいかり | `PMCG5-075` | `candidate` |
| `GD2-017` | カスミの勝負 | `PMCG5-068` | `candidate` |
| `GD2-018` | カスミのなみだ | `PMCG5-069` | `candidate` |
| `GD2-024` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `GD3-001` | マチスのピカチュウ | `PMCG5-036` | `candidate` |
| `GD3-004` | マチスのコイル | `PMCG5-039` | `candidate` |
| `GD3-005` | マチスのコイル | `PMCG5-037` | `candidate` |
| `GD3-006` | マチスのレアコイル | `PMCG5-040` | `candidate` |
| `GD3-007` | マチスのビリリダマ | `PMCG5-038` | `candidate` |
| `GD3-015` | エネルギーサーキュレート | `PMCG5-067` | `candidate` |
| `GD3-016` | スパイ作戦 | `PMCG5-088` | `candidate` |
| `GD3-021` | マチス | `PMCG5-092` | `candidate` |
| `GD3-022` | マチスの交渉 | `PMCG5-081` | `candidate` |
| `GD3-025` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `GD4-002` | エリカのナゾノクサ | `PMCG5-002` | `candidate` |
| `GD4-006` | エリカのマダツボミ | `PMCG5-005` | `candidate` |
| `GD4-008` | エリカのウツボット | `PMCG5-015` | `candidate` |
| `GD4-010` | エリカのナッシー | `PMCG5-013` | `candidate` |
| `GD4-011` | エリカのモンジャラ | `PMCG5-006` | `candidate` |
| `GD4-013` | エリカのミニリュウ | `PMCG5-063` | `candidate` |
| `GD4-016` | エリカ | `PMCG5-083` | `candidate` |
| `GD4-017` | エリカのお付き | `PMCG5-072` | `candidate` |
| `GD4-018` | エリカの香水 | `PMCG5-073` | `candidate` |
| `GD4-026` | 礼儀作法 | `PMCG5-082` | `candidate` |
| `GD4-028` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `GD5-002` | カツラのロコン | `PMCG6-026` | `candidate` |
| `GD5-004` | カツラのキュウコン | `PMCG6-033` | `candidate` |
| `GD5-009` | カツラのポニータ | `PMCG6-028` | `candidate` |
| `GD5-010` | カツラのギャロップ | `PMCG6-030` | `candidate` |
| `GD5-012` | カツラのドードー | `PMCG6-064` | `candidate` |
| `GD5-014` | カツラ | `PMCG6-093` | `candidate` |
| `GD5-015` | カツラのギャンブル | `PMCG6-076` | `candidate` |
| `GD5-025` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `GD6-003` | ナツメのユンゲラー | `PMCG6-047` | `candidate` |
| `GD6-004` | ナツメのフーディン | `PMCG6-053` | `candidate` |
| `GD6-013` | ナツメのポリゴン | `PMCG6-066` | `candidate` |
| `GD6-017` | ナツメ | `PMCG6-098` | `candidate` |
| `GD6-018` | ナツメのESP | `PMCG6-087` | `candidate` |
| `GD6-019` | ナツメの眼 | `PMCG6-078` | `candidate` |
| `GD6-026` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `IP1-002` | スリープ | `PMCG1-045` | `candidate` |
| `IP1-004` | 草エネルギー | `PMCG1-097` | `candidate` |
| `IP1-006` | 雷エネルギー | `PMCG1-100` | `candidate` |
| `IP1-013` | ピカチュウ | `PMCG1-035` | `candidate` |
| `IP1-023` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `IP1-024` | 超エネルギー | `PMCG1-101` | `candidate` |
| `IP2-001` | ガーディ | `PMCG1-018` | `candidate` |
| `IP2-002` | ディグダ | `PMCG1-052` | `candidate` |
| `IP2-004` | 炎エネルギー | `PMCG1-098` | `candidate` |
| `IP2-005` | 水エネルギー | `PMCG1-099` | `candidate` |
| `IP2-012` | 闘エネルギー | `PMCG1-102` | `candidate` |
| `IP2-014` | プリン | `PMCG2-035` | `candidate` |
| `IP2-025` | 無色2個エネルギー | `PMCG1-096` | `data_missing` |
| `IP2-035` | ワンリキー | `PMCG1-053` | `candidate` |
| `PR1-019` | わるいペルシアン | `PMCG4-048` | `candidate` |
| `PR1-031` | カスミのヒトデマン | `PMCG5-027` | `candidate` |
| `PR1-032` | タケシのイワーク | `PMCG5-048` | `candidate` |
| `PR1-039` | エリカのミニリュウ | `PMCG5-063` | `candidate` |
| `PR1-047` | エリカのフシギダネ | `PMCG5-007` | `candidate` |
| `PR1-048` | カスミのメノクラゲ | `PMCG5-030` | `candidate` |
| `PR1-049` | タケシのマンキー | `PMCG5-045` | `candidate` |
| `PR1-050` | マチスのサンダース | `PMCG5-042` | `candidate` |
| `PR1-061` | マンキー | `PMCG2-028` | `candidate` |
| `PR1-076` | コダック | `PMCG3-010` | `candidate` |
| `PR1-080` | ギャラドス | `PMCG1-034` | `candidate` |
| `PR1-081` | ピカチュウ | `PMCG1-035` | `candidate` |
| `PR1-082` | ニョロモ | `PMCG1-024` | `candidate` |
| `PR1-083` | フシギダネ | `PMCG1-001` | `candidate` |
| `PR1-084` | コイキング | `PMCG1-031` | `candidate` |
| `PR1-085` | ゼニガメ | `PMCG1-023` | `candidate` |
| `PR1-086` | ドガース | `PMCG1-006` | `candidate` |
| `PR1-087` | ラッキー | `PMCG1-068` | `candidate` |
| `PR1-088` | フリーザー | `PMCG3-023` | `candidate` |
| `PR1-089` | ヒトカゲ | `PMCG1-014` | `candidate` |
| `NIP1-003` | 草エネルギー | `PMCG1-097` | `candidate` |
| `NIP1-005` | 炎エネルギー | `PMCG1-098` | `candidate` |
| `NIP1-006` | 闘エネルギー | `PMCG1-102` | `candidate` |
| `NIP1-010` | ドガース | `PMCG4-005` | `candidate` |
| `NIP1-012` | ガーディ | `PMCG1-018` | `candidate` |
| `NIP1X-003` | ワンリキー | `PMCG4-040` | `candidate` |
| `NIP2-001` | ピカチュウ | `PMCG1-035` | `candidate` |
| `NIP2-005` | 水エネルギー | `PMCG1-099` | `candidate` |
| `NIP2-006` | 雷エネルギー | `PMCG1-100` | `candidate` |
| `NIP2-007` | 超エネルギー | `PMCG1-101` | `candidate` |

## 再利用の候補（reuse_candidate。拡張パック以外の商品）

162 件。違う欄（differences）を確かめてから登録します。拡張パック（neo）の候補は `data/engine_targets.json` にあります。

| id | 名前 | いちばん近い登録 | 違う欄 |
|---|---|---|---|
| `GD1-004` | タケシのサンドパン | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD1-006` | タケシのイシツブテ | `PMCG5-047` | pokemon.attacks[0].text.ja |
| `GD1-008` | タケシのゴローン | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD1-014` | エネルギー回収 | `PMCG1-076` | trainer.text.ja |
| `GD1-016` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `GD1-017` | 元気のかけら | `PMCG1-078` | trainer.text.ja |
| `GD1-018` | タケシ | `PMCG5-089` | trainer.text.ja |
| `GD1-020` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `GD1-021` | ポケモンいれかえ | `PMCG1-073` | trainer.text.ja |
| `GD1-022` | ポケモン図鑑HANDY505 | `PMCG1-082` | name.ja, trainer.text.ja |
| `GD1-023` | ポケモンセンター | `PMCG1-083` | trainer.text.ja |
| `GD1-024` | ニビシティジム | `PMCG5-079` | trainer.text.ja |
| `GD2-005` | カスミのパウワウ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD2-009` | カスミのトサキント | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD2-013` | カスミのヒトデマン | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD2-014` | カスミのスターミー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD2-019` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `GD2-020` | ディフェンダー | `PMCG1-079` | trainer.text.ja |
| `GD2-021` | 突風 | `PMCG1-072` | trainer.text.ja |
| `GD2-022` | モンスターボール | `PMCG2-048` | trainer.text.ja |
| `GD2-023` | ハナダシティジム | `PMCG5-080` | trainer.text.ja |
| `GD3-002` | マチスのピカチュウ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD3-008` | マチスのビリリダマ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD3-013` | マチスのオニスズメ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD3-014` | いいきずぐすり | `PMCG1-075` | trainer.text.ja |
| `GD3-017` | ディフェンダー | `PMCG1-079` | trainer.text.ja |
| `GD3-018` | 突風 | `PMCG1-072` | trainer.text.ja |
| `GD3-019` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `GD3-020` | ポケモンいれかえ | `PMCG1-073` | trainer.text.ja |
| `GD3-023` | モンスターボール | `PMCG2-048` | trainer.text.ja |
| `GD3-024` | クチバシティジム | `PMCG5-076` | trainer.text.ja |
| `GD4-004` | エリカのラフレシア | `PMCG5-014` | pokemon.attacks[0].text.ja, pokemon.powers[0].text.ja |
| `GD4-005` | エリカのマダツボミ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD4-014` | エネルギー回収 | `PMCG1-076` | trainer.text.ja |
| `GD4-015` | エネルギー転送 | `PMCG3-044` | trainer.text.ja |
| `GD4-019` | お上品攻撃 | `PMCG5-074` | trainer.text.ja |
| `GD4-020` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `GD4-021` | ディフェンダー | `PMCG1-079` | trainer.text.ja |
| `GD4-022` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `GD4-023` | プラスパワー | `PMCG1-081` | trainer.text.ja |
| `GD4-024` | ポケモンいれかえ | `PMCG1-073` | trainer.text.ja |
| `GD4-025` | リサイクル | `PMCG3-047` | trainer.text.ja |
| `GD4-027` | タマムシシティジム | `PMCG5-078` | trainer.text.ja |
| `GD5-007` | カツラのウィンディ | `PMCG6-034` | name.ja |
| `GD5-008` | カツラのポニータ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD5-011` | カツラのブーバー | `PMCG6-031` | pokemon.attacks[1].text.ja |
| `GD5-013` | カツラのドードリオ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD5-018` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `GD5-020` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `GD5-022` | ポケモンいれかえ | `PMCG1-073` | trainer.text.ja |
| `GD5-023` | ポケモン図鑑HANDY505 | `PMCG1-082` | name.ja, trainer.text.ja |
| `GD5-024` | グレンタウンジム | `PMCG6-085` | trainer.text.ja |
| `GD6-006` | ナツメのゴース | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `GD6-010` | ナツメのスリーパー | `PMCG6-051` | pokemon.attacks[0].text.ja |
| `GD6-014` | エネルギー回収 | `PMCG1-076` | trainer.text.ja |
| `GD6-015` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `GD6-016` | ディフェンダー | `PMCG1-079` | trainer.text.ja |
| `GD6-020` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `GD6-021` | プラスパワー | `PMCG1-081` | trainer.text.ja |
| `GD6-022` | ポケモンセンター | `PMCG1-083` | trainer.text.ja |
| `GD6-024` | ワープポイント | `PMCG6-080` | trainer.text.ja |
| `GD6-025` | ヤマブキシティジム | `PMCG6-090` | trainer.text.ja |
| `ES1-004` | ビードル | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-008` | ズバット | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-012` | カイロス | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-016` | ニョロモ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-017` | ニョロゾ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-018` | ニョロボン | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-024` | ポッポ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-030` | ベロリンガ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES1-032` | イーブイ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES2-008` | シェルダー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES2-009` | クラブ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES2-010` | ラプラス | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES2-019` | ルージュラ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES2-022` | ゴーリキー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES2-026` | サワムラー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES2-031` | オニドリル | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES3-015` | タッツー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `ES3-033` | ガルーラ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-006` | カイロス | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-014` | ニョロモ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-015` | ニョロゾ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-016` | ニョロボン | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-019` | ラプラス | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-031` | ルージュラ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-036` | ゴーリキー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-042` | ベロリンガ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-044` | ガルーラ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `QSG-047` | エネルギー回収 | `PMCG1-076` | trainer.text.ja |
| `QSG-048` | エネルギー転送 | `PMCG3-044` | trainer.text.ja |
| `QSG-049` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `QSG-050` | ギャンブラー | `PMCG3-045` | trainer.text.ja |
| `QSG-051` | 突風 | `PMCG1-072` | trainer.text.ja |
| `QSG-052` | ポケモンいれかえ | `PMCG1-073` | trainer.text.ja |
| `QSG-053` | ポケモン交換おじさん | `PMCG1-093` | trainer.text.ja |
| `SI-001` | レディバ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `SI-005` | ピジョット | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `SI-006` | イワーク | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `SI-007` | トゲピー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `SI-009` | ラッタ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `SI-015` | カメール | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP1-001` | フシギダネ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP1-007` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `IP1-016` | ニャース | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP1-019` | ポケモンいれかえ | `PMCG1-073` | trainer.text.ja |
| `IP1-026` | エレブー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP1-028` | 突風 | `PMCG1-072` | trainer.text.ja |
| `IP1-030` | ドードー | `PMCG1-061` | pokemon.attacks[0].text.ja |
| `IP1-037` | ルージュラ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP1-039` | ドガース | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP2-003` | カメール | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP2-007` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `IP2-009` | ニョロモ | `PMCG1-024` | pokemon.attacks[0].text.ja |
| `IP2-013` | オニスズメ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP2-016` | ゼニガメ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP2-019` | エネルギー・リムーブ | `PMCG1-070` | trainer.text.ja |
| `IP2-024` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `IP2-032` | ウィンディ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IP2-039` | ブーバー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `IPH-001` | フシギバナ | `PMCG1-011` | pokemon.powers[0].text.ja |
| `IPH-002` | カメックス | `PMCG1-032` | pokemon.attacks[0].text.ja, pokemon.powers[0].text.ja |
| `PR1-011` | なみのりピカチュウ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PR1-014` | なみのりピカチュウ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PR1-028` | カメックス | `PMCG1-032` | pokemon.attacks[0].text.ja, pokemon.powers[0].text.ja |
| `PR1-029` | フシギバナ | `PMCG1-011` | pokemon.powers[0].text.ja |
| `PR1-030` | リザードン | `PMCG1-021` | pokemon.attacks[0].text.ja, pokemon.powers[0].text.ja |
| `PR1-033` | カモネギ | `PMCG1-063` | pokemon.attacks[0].text.ja |
| `PR1-045` | ディグダ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PR1-066` | マリル | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PR1-069` | ？？？ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PF1-007` | ワニノコ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PF2-004` | エーフィ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP1-001` | チコリータ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP1-002` | ヒマナッツ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP1-007` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `NIP1-008` | ヒメグマ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP1-015` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `NIP1-016` | ヒノアラシ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP1-020` | マサキ | `PMCG1-074` | trainer.text.ja |
| `NIP1-022` | パラス | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP1-024` | ベイリーフ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP1X-006` | プラスパワー | `PMCG1-081` | trainer.text.ja |
| `NIP1X-007` | ポケモンいれかえ | `PMCG1-073` | trainer.text.ja |
| `NIP2-002` | マリル | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2-003` | ホーホー | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2-004` | アリゲイツ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2-008` | なんでもなおし | `PMCG1-080` | trainer.text.ja |
| `NIP2-016` | ワニノコ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2-018` | メリープ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2-020` | きずぐすり | `PMCG1-071` | trainer.text.ja |
| `NIP2-024` | ハリーセン | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2-025` | マサキ | `PMCG1-074` | trainer.text.ja |
| `NIP2-026` | モココ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2X-004` | ネイティ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `NIP2X-006` | ディフェンダー | `PMCG1-079` | trainer.text.ja |
| `NIP2X-007` | 突風 | `PMCG1-072` | trainer.text.ja |
| `PRN-006` | チコリータ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PRN-009` | チコリータ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PRN-013` | ルージュラ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PRN-038` | ノコッチ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |
| `PRN-047` | ハネッコ | （同じカードの組の登録なし。効果の文面がどれも登録された実装と同じ） | |

## 新しい効果の実装が要る記録（new_effect_needed。拡張パック以外の商品）

339 件。拡張パック（neo）の記録は `data/engine_targets.json` にあります。

| id | 名前 | 登録された文面のない効果 | category |
|---|---|---|---|
| `GD1-001` | タケシのズバット | attack0「しらせる」 | `candidate` |
| `GD1-003` | タケシのサンド | attack0「まるくなる」 | `candidate` |
| `GD1-005` | タケシのマンキー | attack0「からかう」 | `candidate` |
| `GD1-007` | タケシのイシツブテ | attack1「ロングショット」 | `candidate` |
| `GD1-010` | タケシのイワーク | attack1「ちていいどう」 | `candidate` |
| `GD1-012` | タケシのサイホーン | attack0「つのでなげる」、attack1「とっしん」 | `candidate` |
| `GD2-001` | カスミのコダック | attack1「たすけをよぶ」 | `candidate` |
| `GD2-002` | カスミのニョロモ | attack0「めまわし」、attack1「しっぽビンタ」 | `candidate` |
| `GD2-003` | カスミのメノクラゲ | attack1「くらげのむれ」 | `candidate` |
| `GD2-006` | カスミのシェルダー | attack1「からではさむ」 | `candidate` |
| `GD2-007` | カスミのパルシェン | power0「シェルアーマー」 | `candidate` |
| `GD2-011` | カスミのアズマオウ | attack1「だくりゅう」 | `candidate` |
| `GD3-003` | マチスのライチュウ | attack1「10まんボルト」 | `data_missing` |
| `GD3-009` | マチスのマルマイン | power0「ショックボム」、attack0「パワーアップボール」 | `candidate` |
| `GD3-010` | マチスのエレブー | attack1「デンキとばし」 | `candidate` |
| `GD3-011` | マチスのコラッタ | attack0「きあいだめ」 | `candidate` |
| `GD3-012` | マチスのラッタ | attack0「いかりのまえば」 | `candidate` |
| `GD4-001` | エリカのナゾノクサ | power0「こうごうせい」 | `candidate` |
| `GD4-003` | エリカのクサイハナ | attack0「ゆめみのまい」、attack1「くさいにおい」 | `candidate` |
| `GD4-007` | エリカのウツドン | attack0「ねむけどく」 | `candidate` |
| `GD4-009` | エリカのタマタマ | attack0「たまなげ」、attack1「サイコキネシス」 | `candidate` |
| `GD4-012` | エリカのピッピ | attack0「おつきみ」 | `candidate` |
| `GD5-001` | カツラのヒトカゲ | attack0「ファイヤーテール」 | `candidate` |
| `GD5-003` | カツラのロコン | attack1「おにびあつめ」 | `candidate` |
| `GD5-005` | カツラのガーディ | attack0「ふりとばす」 | `candidate` |
| `GD5-006` | カツラのガーディ | attack0「もえあがる」 | `candidate` |
| `GD5-016` | カツラのクイズ その1 | trainer「カツラのクイズ その1」 | `candidate` |
| `GD5-017` | カツラのクイズ その2 | trainer「カツラのクイズ その2」 | `candidate` |
| `GD5-019` | 元気のかたまり | trainer「元気のかたまり」 | `candidate` |
| `GD5-021` | 熱血! | trainer「熱血!」 | `candidate` |
| `GD6-001` | ナツメのケーシィ | attack1「シンクロウェーブ」 | `candidate` |
| `GD6-002` | ナツメのケーシィ | attack0「とうし」 | `candidate` |
| `GD6-005` | ナツメのゴース | attack1「ぱっときえる」 | `candidate` |
| `GD6-007` | ナツメのゴースト | attack1「かげからおそう」 | `candidate` |
| `GD6-008` | ナツメのゲンガー | attack0「やみのはどう」 | `candidate` |
| `GD6-009` | ナツメのスリープ | attack0「エナジーサポート」 | `candidate` |
| `GD6-011` | ナツメのバリヤード | attack0「マジックダーツ」 | `candidate` |
| `GD6-012` | ナツメのルージュラ | attack1「めざめのキッス」 | `candidate` |
| `GD6-023` | マスターボール | trainer「マスターボール」 | `candidate` |
| `ES1-001` | フシギダネ | attack0「かいふく」 | `candidate` |
| `ES1-002` | キャタピー | attack1「からまるいと」 | `candidate` |
| `ES1-003` | トランセル | power0「グリーンシールド」 | `candidate` |
| `ES1-005` | コクーン | power0「どくのたいえき」 | `candidate` |
| `ES1-006` | ニドラン♀ | attack0「しっぽをふる」 | `candidate` |
| `ES1-007` | ニドラン♂ | attack0「きあいだめ」 | `candidate` |
| `ES1-009` | ゴルバット | attack0「きゅうけつ」、attack1「きゅうこうか」 | `candidate` |
| `ES1-010` | パラス | attack1「ほうしをとばす」 | `candidate` |
| `ES1-011` | パラセクト | attack1「きゅうけつ」 | `candidate` |
| `ES1-013` | ヒトカゲ | attack0「なきごえ」 | `candidate` |
| `ES1-014` | ギャロップ | attack0「かえんじごく」、attack1「けりとばす」 | `candidate` |
| `ES1-015` | ゼニガメ | attack0「ウォーターパワー」 | `candidate` |
| `ES1-019` | ピカチュウ | attack1「こうそくいどう」 | `candidate` |
| `ES1-020` | ケーシィ | attack0「サイキックビーム」 | `candidate` |
| `ES1-021` | バリヤード | power0「ニュートラルダメージ」、attack0「ジャグリング」 | `candidate` |
| `ES1-022` | ミュウツー | attack0「サイコクラッシュ」 | `candidate` |
| `ES1-023` | イシツブテ | attack1「かたくなる」 | `candidate` |
| `ES1-025` | コラッタ | attack1「しっぽをふる」 | `candidate` |
| `ES1-026` | ピッピ | attack0「このゆびとまれ」 | `candidate` |
| `ES1-027` | プクリン | power0「てだすけ」、attack0「ふくらむ」 | `candidate` |
| `ES1-028` | ドードー | attack0「なきごえ」 | `candidate` |
| `ES1-029` | ドードリオ | attack1「トライアタック」 | `candidate` |
| `ES1-031` | ラッキー | attack1「おうふくビンタ」 | `candidate` |
| `ES1-033` | ポリゴン | attack0「3Dアタック」、attack1「テクスチャー2」 | `candidate` |
| `ES1-034` | カビゴン | power0「とおせんぼ」、attack0「ねころぶ」 | `candidate` |
| `ES1-035` | 化石の発掘 | trainer「化石の発掘」 | `candidate` |
| `ES1-036` | 月の石 | trainer「月の石」 | `candidate` |
| `ES2-001` | モルフォン | attack0「たつまきおこし」、attack1「レインボーパウダー」 | `candidate` |
| `ES2-002` | ベトベター | attack0「ベトベトえき」 | `candidate` |
| `ES2-003` | ドガース | power0「ぶんれつ」、attack0「ふしぎなガス」 | `candidate` |
| `ES2-004` | モンジャラ | attack0「からみつく」 | `candidate` |
| `ES2-005` | ファイヤー | attack0「ドライアップ」 | `candidate` |
| `ES2-006` | パウワウ | attack0「なきごえ」 | `candidate` |
| `ES2-007` | ジュゴン | attack0「ねむる」 | `candidate` |
| `ES2-011` | オムナイト | power0「げんしのゆめ」 | `data_missing` |
| `ES2-012` | フリーザー | power0「オーロラヴェール」 | `candidate` |
| `ES2-013` | ライチュウ | attack0「ろうでん」 | `candidate` |
| `ES2-014` | コイル | power0「マグネット」、attack0「ちょうでんどう」 | `candidate` |
| `ES2-015` | レアコイル | attack0「マイクロウェーブ」 | `candidate` |
| `ES2-016` | ビリリダマ | attack1「みんなでスパーク」 | `candidate` |
| `ES2-017` | エレブー | attack0「ひらいしん」、attack1「かみなりショック」 | `candidate` |
| `ES2-018` | サンダー | attack0「らくらい」、attack1「サンダークラッシュ」 | `candidate` |
| `ES2-020` | サンド | attack1「スピードスター」 | `candidate` |
| `ES2-021` | ワンリキー | attack0「きあいいっぱつ」 | `candidate` |
| `ES2-023` | ゴローン | attack0「れんぞくいわなげ」、attack1「じしん」 | `candidate` |
| `ES2-024` | イワーク | attack1「いわふうじ」 | `candidate` |
| `ES2-025` | ガラガラ | attack0「ほねさがし」、attack1「ほねこんぼう」 | `candidate` |
| `ES2-027` | エビワラー | attack0「マッハパンチ」 | `candidate` |
| `ES2-028` | カブト | power0「かせきか」 | `data_missing` |
| `ES2-029` | プテラ | attack1「きりもみアタック」 | `data_missing` |
| `ES2-030` | オニスズメ | attack0「みだれづき」 | `candidate` |
| `ES2-032` | メタモン | power0「すごいへんしん」 | `candidate` |
| `ES2-033` | エフェクトガード | trainer「エフェクトガード」 | `candidate` |
| `ES2-034` | 元気のかたまり | trainer「元気のかたまり」 | `candidate` |
| `ES2-035` | フラッシュ | trainer「フラッシュ」 | `candidate` |
| `ES2-036` | マスターボール | trainer「マスターボール」 | `candidate` |
| `ES3-001` | アーボック | attack1「もうどく」 | `candidate` |
| `ES3-002` | ニドリーナ | attack0「なかまのちから」、attack1「みだれひっかき」 | `candidate` |
| `ES3-003` | ニドリーノ | attack0「こうそくづき」 | `candidate` |
| `ES3-004` | コンパン | attack0「かなしばり」 | `candidate` |
| `ES3-005` | マダツボミ | attack0「ゆれる」 | `candidate` |
| `ES3-006` | ウツドン | attack0「さいせい」 | `candidate` |
| `ES3-007` | マタドガス | power0「ポイズンミスト」、attack0「ガスばくはつ」 | `candidate` |
| `ES3-008` | ストライク | attack0「スラッシュダウン」 | `candidate` |
| `ES3-009` | ロコン | attack0「きつねび」 | `candidate` |
| `ES3-010` | ガーディ | attack0「おつかい」、attack1「ひのこ」 | `candidate` |
| `ES3-011` | ポニータ | attack1「ひばな」 | `candidate` |
| `ES3-012` | ブーバー | attack0「ファイヤーバーン」 | `candidate` |
| `ES3-013` | ゴルダック | attack0「サイコキネシス」 | `candidate` |
| `ES3-014` | キングラー | attack0「しおまねき」、attack1「もろばバサミ」 | `candidate` |
| `ES3-016` | シードラ | attack0「ウォーターボム」 | `candidate` |
| `ES3-017` | ヒトデマン | attack0「なぞのこうせん」 | `candidate` |
| `ES3-018` | オムナイト | power0「かせきのみちびき」 | `data_missing` |
| `ES3-019` | ユンゲラー | attack0「サイコパニック」、attack1「ブリンク」 | `candidate` |
| `ES3-020` | ユンゲラー | attack0「エナジーさいせい」、attack1「エナジーショック」 | `candidate` |
| `ES3-021` | ヤドラン | attack0「おおあくび」、attack1「おおいびき」 | `candidate` |
| `ES3-022` | ゴース | attack0「こわがらせる」 | `candidate` |
| `ES3-023` | ゴースト | attack1「おんねん」 | `candidate` |
| `ES3-024` | ゴースト | attack0「ポルターガイスト」、attack1「ナイトメア」 | `candidate` |
| `ES3-025` | スリーパー | power0「にんぎょうつかい」 | `candidate` |
| `ES3-026` | ミュウツー | attack0「かんぜんかいふく」、attack1「サイコブラスト」 | `candidate` |
| `ES3-027` | サンドパン | attack0「すながくれ」、attack1「ローリングニードル」 | `candidate` |
| `ES3-028` | ゴーリキー | attack1「きあいだま」 | `candidate` |
| `ES3-029` | ゴローン | attack0「がんせきくだき」 | `candidate` |
| `ES3-030` | カラカラ | attack0「ほねをなげる」 | `candidate` |
| `ES3-031` | サイドン | attack0「やまくずし」 | `candidate` |
| `ES3-032` | ピジョン | attack0「ツイスター」、attack1「そらをとぶ」 | `candidate` |
| `ES3-034` | ケンタロス | attack0「ふんだりけったり」 | `candidate` |
| `ES3-035` | ポケモン再転送 | trainer「ポケモン再転送」 | `candidate` |
| `ES3-036` | ポケモンタワー | trainer「ポケモンタワー」 | `candidate` |
| `QSG-001` | フシギダネ | attack0「かいふく」 | `candidate` |
| `QSG-002` | キャタピー | attack1「からまるいと」 | `candidate` |
| `QSG-003` | トランセル | power0「グリーンシールド」 | `candidate` |
| `QSG-004` | ニドラン♀ | attack0「しっぽをふる」 | `candidate` |
| `QSG-005` | ニドラン♂ | attack0「きあいだめ」 | `candidate` |
| `QSG-007` | ヒトカゲ | attack0「なきごえ」 | `candidate` |
| `QSG-008` | ロコン | attack0「きつねび」 | `candidate` |
| `QSG-009` | ガーディ | attack0「おつかい」、attack1「ひのこ」 | `candidate` |
| `QSG-010` | ポニータ | attack1「ひばな」 | `candidate` |
| `QSG-011` | ギャロップ | attack0「かえんじごく」、attack1「けりとばす」 | `candidate` |
| `QSG-012` | ブーバー | attack0「ファイヤーバーン」 | `candidate` |
| `QSG-013` | ゼニガメ | attack0「ウォーターパワー」 | `candidate` |
| `QSG-017` | パウワウ | attack0「なきごえ」 | `candidate` |
| `QSG-018` | ジュゴン | attack0「ねむる」 | `candidate` |
| `QSG-020` | ピカチュウ | attack1「こうそくいどう」 | `candidate` |
| `QSG-021` | ピカチュウ | attack0「じゅうでん」、attack1「10まんボルト」 | `candidate` |
| `QSG-022` | ライチュウ | attack0「ろうでん」 | `candidate` |
| `QSG-023` | コイル | power0「マグネット」、attack0「ちょうでんどう」 | `candidate` |
| `QSG-024` | レアコイル | attack0「マイクロウェーブ」 | `candidate` |
| `QSG-025` | ビリリダマ | attack1「みんなでスパーク」 | `candidate` |
| `QSG-026` | ケーシィ | attack0「サイキックビーム」 | `candidate` |
| `QSG-027` | ユンゲラー | attack0「エナジーさいせい」、attack1「エナジーショック」 | `candidate` |
| `QSG-028` | ゴース | attack0「こわがらせる」 | `candidate` |
| `QSG-029` | ゴースト | attack0「ポルターガイスト」、attack1「ナイトメア」 | `candidate` |
| `QSG-030` | バリヤード | power0「ニュートラルダメージ」、attack0「ジャグリング」 | `candidate` |
| `QSG-032` | ミュウツー | attack0「サイコクラッシュ」 | `candidate` |
| `QSG-033` | サンド | attack1「スピードスター」 | `candidate` |
| `QSG-034` | サンドパン | attack0「すながくれ」、attack1「ローリングニードル」 | `candidate` |
| `QSG-035` | ワンリキー | attack0「きあいいっぱつ」 | `candidate` |
| `QSG-037` | イワーク | attack1「いわふうじ」 | `candidate` |
| `QSG-038` | エビワラー | attack0「マッハパンチ」 | `candidate` |
| `QSG-039` | コラッタ | attack1「しっぽをふる」 | `candidate` |
| `QSG-040` | ピッピ | attack0「このゆびとまれ」 | `candidate` |
| `QSG-041` | ドードー | attack0「なきごえ」 | `candidate` |
| `QSG-043` | ラッキー | attack1「おうふくビンタ」 | `candidate` |
| `QSG-045` | ポリゴン | attack0「3Dアタック」、attack1「テクスチャー2」 | `candidate` |
| `QSG-046` | カビゴン | power0「とおせんぼ」、attack0「ねころぶ」 | `candidate` |
| `QSG-054` | ストライク | attack0「スラッシュダウン」 | `candidate` |
| `QSG-055` | ファイヤー | attack0「ドライアップ」 | `candidate` |
| `QSG-056` | サンダー | attack0「らくらい」、attack1「サンダークラッシュ」 | `candidate` |
| `QSG-057` | フリーザー | power0「オーロラヴェール」 | `candidate` |
| `QSG-058` | マスターボール | trainer「マスターボール」 | `candidate` |
| `SI-002` | プリン | attack0「ひとみでさそう」 | `candidate` |
| `SI-003` | バタフリー | attack0「そらをとぶ」、attack1「レインボーパウダー」 | `candidate` |
| `SI-004` | ミュウ | attack0「レインボーウェーブ」 | `candidate` |
| `SI-008` | フシギソウ | attack0「ふしぎなかおり」 | `candidate` |
| `SI-010` | ベロリンガ | attack0「きずをなめる」、attack1「のびるベロ」 | `candidate` |
| `SI-011` | ラフレシア | attack0「ごくらくかふん」、attack1「さいあくかふん」 | `candidate` |
| `SI-012` | オコリザル | attack1「いかりくるう」 | `candidate` |
| `SI-013` | ナッシー | attack0「ねらいだま」 | `candidate` |
| `SI-014` | ヤドキング | attack0「ひらめく」、attack1「サイコキネシス」 | `candidate` |
| `SI-016` | ドククラゲ | attack0「しょくしゅをつかう」 | `candidate` |
| `SI-017` | マリル | attack0「みずとばし」 | `candidate` |
| `SI-018` | ラプラス | attack0「やさしいうた」 | `candidate` |
| `IP1-003` | ライチュウ | attack1「10まんボルト」 | `candidate` |
| `IP1-009` | スーパーポケモン回収 | trainer「スーパーポケモン回収」 | `candidate` |
| `IP1-018` | フシギダネ | attack0「かいふく」 | `candidate` |
| `IP1-020` | マサキの転送装置 | trainer「マサキの転送装置」 | `candidate` |
| `IP1-022` | フシギソウ | attack0「やどりぎのたね」 | `candidate` |
| `IP1-040` | ピカチュウ | attack0「なきごえ」 | `candidate` |
| `IP2-018` | ゼニガメ | attack0「ウォーターパワー」 | `candidate` |
| `IP2-021` | マサキの転送装置 | trainer「マサキの転送装置」 | `candidate` |
| `IP2-026` | ガーディ | attack1「ひのこ」 | `candidate` |
| `IP2-029` | スーパーポケモン回収 | trainer「スーパーポケモン回収」 | `candidate` |
| `PR1-001` | ピカチュウ | attack0「なきごえ」 | `candidate` |
| `PR1-002` | プリン | attack0「かいふく」 | `candidate` |
| `PR1-003` | ピカチュウ | attack0「なきごえ」 | `candidate` |
| `PR1-004` | プリン | attack0「かいふく」 | `candidate` |
| `PR1-005` | ミュウ | power0「ニュートラルシールド」 | `candidate` |
| `PR1-006` | ヤドン | attack1「ドわすれ」 | `candidate` |
| `PR1-007` | ミュウツー | attack0「エネルギーきゅうしゅう」 | `candidate` |
| `PR1-008` | ミュウツー | attack0「エネルギーきゅうしゅう」 | `candidate` |
| `PR1-009` | 超エネルギー回収 | trainer「超エネルギー回収」 | `candidate` |
| `PR1-010` | エレブー | attack0「ひかりのかべ」 | `candidate` |
| `PR1-012` | ミュウ | power0「ニュートラルシールド」 | `candidate` |
| `PR1-013` | イマクニ？ | trainer「イマクニ？」 | `candidate` |
| `PR1-016` | ウィンディ | attack1「いかりのほのお」 | `candidate` |
| `PR1-017` | ピカチュウ | attack0「なきごえ」 | `candidate` |
| `PR1-018` | そらをとぶピカチュウ | attack1「そらをとぶ」 | `candidate` |
| `PR1-020` | ピカチュウ | attack0「じゅうでん」、attack1「10まんボルト」 | `candidate` |
| `PR1-021` | ミュウ | attack1「サイコデュープ」 | `candidate` |
| `PR1-022` | ミュウツー | attack0「エナジーコントロール」、attack1「テレキネシス」 | `candidate` |
| `PR1-023` | かっこいいポリゴン | attack0「テクスチャーマジック」 | `candidate` |
| `PR1-024` | くいしんぼカビゴン | attack0「たべる」、attack1「ころがる」 | `candidate` |
| `PR1-025` | ニャース | attack1「まるもうけ」 | `candidate` |
| `PR1-026` | パソコン大暴走！ | trainer「パソコン大暴走！」 | `candidate` |
| `PR1-027` | とりかえっこプリーズ | trainer「とりかえっこプリーズ」 | `special_rule_design` |
| `PR1-034` | カラカラ | attack0「ほねさがし」、attack1「ボーンキラー」 | `candidate` |
| `PR1-035` | ルージュラ | attack0「あくまののろい」 | `candidate` |
| `PR1-036` | コイキング | attack0「びちびち」 | `candidate` |
| `PR1-037` | ガルーラ | attack0「ピヨピヨパンチ」 | `candidate` |
| `PR1-038` | タッチ交代！ | trainer「タッチ交代！」 | `special_rule_design` |
| `PR1-040` | マチスのエレブー | attack1「デンキとばし」 | `candidate` |
| `PR1-041` | パソコン大暴走！ | trainer「パソコン大暴走！」 | `candidate` |
| `PR1-042` | そらをとぶピカチュウ | attack1「そらをとぶ」 | `candidate` |
| `PR1-043` | カイリュー | power0「トランスポート」、attack0「マッハひこう」 | `candidate` |
| `PR1-044` | _のピカチュウ | attack0「おたんじょうび」 | `candidate` |
| `PR1-046` | ダグトリオ | power0「もぐる」、attack0「アースウェイブ」 | `candidate` |
| `PR1-051` | オムスター | attack0「しょくしゅをつかう」、attack1「ふしょくえき」 | `candidate` |
| `PR1-052` | カイリキー | attack0「いかりばくはつ」、attack1「なげとばす」 | `candidate` |
| `PR1-053` | ゲンガー | power0「やみのちから」、attack0「サイコホラー」 | `candidate` |
| `PR1-054` | ゴローニャ | attack1「ロックブラスト」 | `candidate` |
| `PR1-055` | フーディン | attack0「サイコパニック」、attack1「トランスダメージ」 | `candidate` |
| `PR1-056` | カイリュー | power0「いやしのかぜ」 | `candidate` |
| `PR1-057` | ニャース | attack0「ねこパンチ」 | `candidate` |
| `PR1-058` | フシギバナ | power0「ソーラーパワー」、attack0「メガドレイン」 | `candidate` |
| `PR1-059` | カツラのガーディ | attack0「ふりとばす」 | `candidate` |
| `PR1-060` | ナツメのケーシィ | attack1「シンクロウェーブ」 | `candidate` |
| `PR1-062` | ピカチュウ | attack1「10まんボルト」 | `candidate` |
| `PR1-063` | そらをとぶピカチュウ | attack1「そらをとぶ」 | `candidate` |
| `PR1-064` | フリーザー | attack0「ダイヤモンドダスト」 | `candidate` |
| `PR1-065` | トゲピー | attack0「なきつく」、attack1「ゆびをふる」 | `candidate` |
| `PR1-067` | キョウの忍者ジム | trainer「キョウの忍者ジム」 | `candidate` |
| `PR1-068` | サカキのニドキング | power0「めいれい」 | `candidate` |
| `PR1-070` | サンダー | attack0「ライトニングバーン」 | `candidate` |
| `PR1-071` | ファイヤー | attack0「ハイパーフレイム」 | `candidate` |
| `PR1-072` | ハマちゃんのヤドキング | attack0「こまったなあ」、attack1「どつく」 | `candidate` |
| `PR1-073` | カスミのてあて | trainer「カスミのてあて」 | `special_rule_design` |
| `PR1-074` | トロピカルウインド | trainer「トロピカルウインド」 | `candidate` |
| `PR1-075` | ナッシー［Exeggutor］ | attack0「ふみつけ[Stomp]」 | `candidate` |
| `PR1-077` | ナッシー［Exeggutor］ | attack0「ふみつけ[Stomp]」 | `candidate` |
| `PR1-078` | ロケット団のニャース | attack0「だいぎゃくてん？」 | `candidate` |
| `PR1-079` | カードトレーナー認定証 | trainer「カードトレーナー認定証」 | `candidate` |
| `PR1-090` | _のピカチュウ | attack0「おたんじょうび」 | `candidate` |
| `PF1-001` | チコリータ | attack0「なきごえ」 | `candidate` |
| `PF1-002` | ベイリーフ | attack1「しんぴのこな」 | `candidate` |
| `PF1-003` | メガニウム | power0「ハーブのかおり」 | `candidate` |
| `PF1-004` | ヒノアラシ | attack0「にらみつける」 | `candidate` |
| `PF1-005` | マグマラシ | attack0「ひのこ」、attack1「ほのおのかぜ」 | `candidate` |
| `PF1-006` | バクフーン | power0「ファイヤーブースト」、attack0「かえんぐるま」 | `candidate` |
| `PF1-008` | アリゲイツ | attack1「まきこむ」 | `candidate` |
| `PF1-009` | オーダイル | power0「どしゃぶり」、attack0「ぎゃくりゅう」 | `candidate` |
| `PF2-001` | アンノーン[N] | rules_text「」、power0「NORMAL df[ノーマル ディーエフ]」 | `candidate` |
| `PF2-002` | アンノーン[E] | rules_text「」、power0「ENGAGE[エンゲージ]」 | `candidate` |
| `PF2-003` | アンノーン[O] | rules_text「」、power0「OBSERVE[オブザーブ]」 | `candidate` |
| `PF2-005` | イーブイ | power0「エナジーしんか」 | `candidate` |
| `PF2-006` | ブラッキー | attack1「おいうち」 | `candidate` |
| `PF2-007` | ピチュー | rules_text「」、attack0「いっしょにあそぼ」 | `candidate` |
| `PF2-008` | エンテイ | power0「はしりさる」、attack0「ほのおのまもり」 | `candidate` |
| `PF2-009` | リザードン | power0「ファイヤーレイズ」、attack0「ほのおのうず」 | `candidate` |
| `PF3-001` | ウソッキー | power0「ものまね」 | `candidate` |
| `PF3-002` | セレビィ | attack0「サイコリーフ」 | `candidate` |
| `PF3-003` | ニューラ | attack0「だましとる」 | `candidate` |
| `PF3-004` | ライコウ | power0「でんせつのからだ」 | `candidate` |
| `PF3-005` | エンテイ | power0「でんせつのからだ」、attack0「メガフレイム」 | `candidate` |
| `PF3-006` | スイクン | power0「でんせつのからだ」、attack0「クリスタルウェーブ」 | `candidate` |
| `PF3-007` | ホウオウ | attack0「レインボーバーン」 | `candidate` |
| `PF3-008` | ルギア | attack0「エアロウイング」 | `candidate` |
| `PF3-009` | エアームド | attack0「みだれづき」 | `candidate` |
| `NIP1-013` | マグマラシ | attack1「かえんほうしゃ」 | `candidate` |
| `NIP1-021` | マスターボール | trainer「マスターボール」 | `candidate` |
| `NIP1X-001` | メガニウム | power0「ハーブのかおり」 | `candidate` |
| `NIP1X-002` | ブビィ | rules_text「」 | `candidate` |
| `NIP1X-004` | イシツブテ | attack0「いしなだれ」 | `candidate` |
| `NIP1X-005` | エアームド | attack1「メタルスラッシュ」 | `candidate` |
| `NIP1X-008` | きのみ | trainer「きのみ」 | `candidate` |
| `NIP1X-009` | エネルギースタジアム | trainer「エネルギースタジアム」 | `candidate` |
| `NIP1X-010` | 鋼エネルギー | energy「鋼エネルギー」 | `candidate` |
| `NIP2-010` | テッポウオ | attack0「みずでっぽう」 | `candidate` |
| `NIP2-022` | マスターボール | trainer「マスターボール」 | `candidate` |
| `NIP2X-001` | オーダイル | power0「どしゃぶり」、attack0「ぎゃくりゅう」 | `candidate` |
| `NIP2X-002` | ピチュー | rules_text「」 | `candidate` |
| `NIP2X-003` | ケーシィ | attack1「はかいビーム」 | `candidate` |
| `NIP2X-005` | デルビル | attack1「ごうだつ」 | `candidate` |
| `NIP2X-008` | きのみ | trainer「きのみ」 | `candidate` |
| `NIP2X-009` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `NIP2X-010` | 悪エネルギー | energy「悪エネルギー」 | `candidate` |
| `PRN-001` | ヤミカラス | attack1「おいうち」 | `candidate` |
| `PRN-002` | 悪エネルギー | energy「悪エネルギー」 | `candidate` |
| `PRN-003` | ウパー | attack0「しっぽをふる」、attack1「みずでっぽう」 | `candidate` |
| `PRN-004` | きのみ | trainer「きのみ」 | `candidate` |
| `PRN-005` | きせきのみ | trainer「きせきのみ」 | `candidate` |
| `PRN-007` | ヒノアラシ | attack0「ひばな」 | `candidate` |
| `PRN-008` | ワニノコ | attack0「にらみつける」 | `candidate` |
| `PRN-010` | ヒノアラシ | attack0「ひばな」 | `candidate` |
| `PRN-011` | ワニノコ | attack0「にらみつける」 | `candidate` |
| `PRN-012` | ピィ | rules_text「」、attack0「ピッピッ」 | `candidate` |
| `PRN-014` | ハガネール | attack0「メタルクラッシュ」、attack1「じひびき」 | `candidate` |
| `PRN-015` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-016` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-017` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-018` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-019` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-020` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-021` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-022` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-023` | ポリゴン | attack0「オールクリア」、attack1「ハイパーテクスチャー」 | `candidate` |
| `PRN-024` | イーブイ | power0「れんさしんか」 | `candidate` |
| `PRN-025` | ハッサム | attack0「にらみつける」、attack1「メタルニッパー」 | `candidate` |
| `PRN-026` | おどれ！neo★イマクニ？ | trainer「おどれ！neo★イマクニ？」 | `candidate` |
| `PRN-027` | ラッキースタジアム | trainer「ラッキースタジアム」 | `candidate` |
| `PRN-028` | マリル | attack0「はずむ」 | `candidate` |
| `PRN-029` | ドーブル | attack0「ペイント」 | `candidate` |
| `PRN-030` | カポエラー | attack0「れんぞくキック」、attack1「こうそくスピン」 | `data_missing` |
| `PRN-031` | ププリン | rules_text「」 | `candidate` |
| `PRN-032` | ヒマナッツ | attack0「せいちょう」、attack1「メガドレイン」 | `candidate` |
| `PRN-033` | トゲピー | attack0「はしゃぐ」 | `candidate` |
| `PRN-034` | アンノーン[J] | rules_text「」、power0「JOIN[ジョイン]」 | `candidate` |
| `PRN-035` | アンノーン[R] | rules_text「」、power0「REASSURE[リーアシュア]」 | `candidate` |
| `PRN-036` | ムウマ | attack0「いたみわけ」 | `candidate` |
| `PRN-037` | ムチュール | rules_text「」、attack0「なげキッス」 | `candidate` |
| `PRN-039` | わるいフシギソウ | power0「つるでひっぱる」、attack0「みだれうち」 | `data_missing` |
| `PRN-040` | わるいフシギバナ | attack0「いやなかふん」 | `data_missing` |
| `PRN-041` | GR団のミュウツー | power0「わるいはどう」、attack0「わるいぞうふく」 | `candidate` |
| `PRN-042` | ルギア | attack0「エアロブラスト」 | `candidate` |
| `PRN-043` | キレイハナ | attack0「フローラルスピン」 | `candidate` |
| `PRN-044` | ひかるミュウ | rules_text「」、attack0「フラッシュサーチ」、attack1「ふしぎなほのお」 | `candidate` |
| `PRN-045` | わるいオニドリル | attack0「たかくとぶ」、attack1「ドリルダイブ」 | `data_missing` |
| `PRN-046` | ひかるコイキング | rules_text「」、attack0「きんいろのうろこ」、attack1「りゅうのきずな」 | `candidate` |
| `PRN-048` | タッチ世代交代！ | trainer「タッチ世代交代！」 | `special_rule_design` |

## 値の欠け・特別なルールの記録（拡張パック以外の商品）

| id | 名前 | category | 理由 |
|---|---|---|---|
| `GD1-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD2-024` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD3-003` | マチスのライチュウ | `data_missing` | pokemon.stage, pokemon.evolves_from |
| `GD3-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD4-028` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD5-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `GD6-026` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `ES2-011` | オムナイト | `data_missing` | pokemon.evolves_from |
| `ES2-028` | カブト | `data_missing` | pokemon.evolves_from |
| `ES2-029` | プテラ | `data_missing` | pokemon.evolves_from |
| `ES3-018` | オムナイト | `data_missing` | pokemon.evolves_from |
| `IP1-023` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `IP2-025` | 無色2個エネルギー | `data_missing` | energy.text.ja |
| `PR1-027` | とりかえっこプリーズ | `special_rule_design` | play_scope: not_for_official_tournaments |
| `PR1-038` | タッチ交代！ | `special_rule_design` | play_scope: kangaskhan_rule |
| `PR1-073` | カスミのてあて | `special_rule_design` | play_scope: not_for_official_tournaments |
| `PRN-030` | カポエラー | `data_missing` | pokemon.stage, pokemon.evolves_from |
| `PRN-039` | わるいフシギソウ | `data_missing` | pokemon.evolves_from |
| `PRN-040` | わるいフシギバナ | `data_missing` | pokemon.evolves_from |
| `PRN-045` | わるいオニドリル | `data_missing` | pokemon.evolves_from |
| `PRN-048` | タッチ世代交代！ | `special_rule_design` | play_scope: kangaskhan_rule |

## 登録のあとで kyuura の値が変わったカード

エンジンが登録のときに照合した値（写しの元のコミットの値にエンジンの補正を当てはめたもの）と、今の kyuura の値が違う欄です。エンジンが写しのコミットを上げるときに確かめます。

ありません。

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
