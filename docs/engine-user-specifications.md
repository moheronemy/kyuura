# 利用者がエンジン用に指定した仕様の一覧（2026-11-01）

kyuura-engine の処理のために**利用者が指定した**簡略化・参照値・名前の扱い・規則を 1 か所で見るための一覧と、2026-11-01 に加えた記録です。どれも原典の調査・公式の裁定・最新の説明・エラッタ・転記の訂正・画像の照合ではありません。kyuura のカードデータ（印刷の文面・カード名の原表記・出典）と研究の記録（裁定・論点）は、この記録のために変えていません。

- 指定は利用者の依頼の中のもので、別の公開資料はありません。日付は kyuura に記録した日です。
- 「実装を確かめた」は、kyuura-engine の**公開済みの固定コミット**を `git fetch` して `git show`・`git grep` で読み、文書・登録・検査・テストのファイルと名前がそのコミットにあることを見た、という意味です。エンジンのコードは実行していません。エンジンのテスト・対戦の結果は**エンジンの報告**で、kyuura が再実行した結果ではありません。エンジンの作業中のツリー（手元の checkout）は読んでいません。
- `data/sidecar/rulings.json` の `engine_positions`・`engine_imports` には、どの指定も加えていません。`engine_positions` は取り込んだ版（`engine_imports`）の文書・節を要り、取り込みは版の裁定の表・未解決の一覧との照合を伴う作業です。利用者の指定を記録するためだけに版の取り込み・登録表の写しの更新はしない、という今回の範囲にしたがい、この文書に記録しました（7 章）。

## 1. 一覧

| 指定 | 対象 | kyuura の記録 | 記録の状態 | エンジンの実装 |
|---|---|---|---|---|
| 誕生日の条件を省き、毎回コイン 1 回 | _のピカチュウ PR1-044・PR1-090「おたんじょうび」 | [プロモ 3 枚の簡略化](engine-user-promo-simplifications.md) | 2026-10-31 に記録済み（変えていない） | 2 章 |
| 発話の条件を省く | ハマちゃんのヤドキング PR1-072「こまったなあ」「どつく」 | 同上 | 2026-10-31 に記録済み（変えていない） | 2 章 |
| 正解に公式図鑑の種族の身長を採る | カツラのクイズ その1 GD5-016 | この文書の 3 章 | **今回追加** | v0.129 `6673e7b`。**固定コミットで確かめた** |
| 交換が成立した 2 枚は受け取った側の所有 | とりかえっこプリーズ PR1-027 | [とりかえっこプリーズの所有者の簡略仕様](engine-user-swap-ownership.md) | 2026-10-31 に記録済み。**今回、実装の経過（8 章）を追加** | v0.130 `f9a66ac`。**固定コミットで確かめた** |
| 英語の併記を名前の判定に使わない | ナッシー［Exeggutor］ PR1-075・PR1-077 | この文書の 4 章 | **今回追加** | v0.131 `f715dd5`。**固定コミットで確かめた** |
| ［ちえくらべ］は任意・コストの前に投げる | ヤドキング neo1-049 | この文書の 5 章 | **今回追加** | v0.132 `a6c0c95`。**固定コミットで確かめた** |
| マウンテンクラッシュ・はかいのほのおの処理 | ひかるバンギラス neo4-082 | [ひかるバンギラスの処理](engine-user-shining-tyranitar.md) | 2026-11-01 に追加（そのときは v0.133 の**計画**・完成は**未確認**）。2026-11-02 に完成後の経過（7 章）を追加 | v0.133 `298f08d`。**固定コミットで確かめた**（ESP の実在の経路は未確認。8 章） |

別の種類の利用者の指定（目録・実装の範囲）として、タッチ交代！ PR1-038・タッチ世代交代！ PRN-048・カードトレーナー認定証 PR1-079 をエンジンの対象から外した記録が [プロモの収録範囲の調査](catalog-promo-survey.md) と [data-schema](data-schema.md) にあります（`engine_scope`。この一覧の処理の指定とは別）。

## 2. 誕生日・発話の条件の省略（2026-10-31 の記録の、その後）

[プロモ 3 枚の簡略化](engine-user-promo-simplifications.md) の 1〜6 章は変えていません（6 章は「計画だけで、実装は確かめていない」のまま）。

- 2026-11-01 に読んだ v0.129 の固定コミット `6673e7bfd5a3e5bc0a3369b7725648b293b26099` の木には、`kyuura_engine/effects.py` の `USER_SIMPLIFICATIONS`（`UserSimplification`。v0.127 の記録）に `PR1-044/attack/0`・`PR1-090/attack/0`・`PR1-072/attack/0`・`PR1-072/attack/1` の 4 件があります。
- **v0.127 の版のコミットは固定しておらず、利用者からの完成報告も今回は受けていません。** 後の版の木に登録があることを見ただけで、v0.127 の実装を独立に確かめたとは記録しません。

## 3. カツラのクイズ その1（GD5-016）の正解（今回追加）

### 3.1 利用者の指定

- 正解には、kyuura が集めた全国図鑑 No.001〜251 の通常の姿の、公式図鑑の身長（[`data/species_heights.json`](../data/species_heights.json)）を採る。
- カードに印刷された身長を確かめた値ではない。
- 答えは整数 cm で比べる。単位のついた入力を cm にする換算と、正誤の判定を分ける。
- カードの図鑑番号（`pokemon.dex`）の欠けを、名前から推測して補わない。

### 3.2 原文・既存の記録との関係

- 印刷の文面（kyuura の値。`trainer.text.ja`）: 「あなたの手札から「ポケモン」のカードを1枚選び、おもてを下にして、置く。相手プレイヤーにそのポケモンの名前を伝え、その身長を答えてもらう。その後、置いたカードをおもてにして、正解なら、相手プレイヤーは山札からカードを2枚引く。正解でないなら、あなたは山札からカードを2枚引く。(置いたカードは、手札にもどす)」。文面は変えていません。
- 印刷の文面は「その身長」の基準・単位・比べ方を書きません。[公式図鑑の種族の身長の引き継ぎ](engine-handover-species-heights.md) 3 章で「エンジンの仕様として別に決めること（kyuura は決めていない）」とした事項のうち、**正解の基準**と**答えの比べ方**を利用者が指定しました。カードの時期（1996〜2001 年）の図鑑・カードに印刷された身長と同じかは、確かめていないままです。
- 参照値（`data/species_heights.json`）は公式のポケモンずかんから集めた値で、印刷の訂正・最新の説明ではありません。kyuura にこのカードの最新の説明（LD-）・照合（CC-）・裁定の記録はありません。
- 図鑑番号のないポケモンのカード（kyuura の `data/cards.json` では 1,068 枚のうち 227 枚）は、参照値と結べません。この指定で図鑑番号を補っていません。

### 3.3 実装を確かめた範囲（v0.129）

| 項目 | 値 |
|---|---|
| 完成報告 | v0.129・`6673e7bfd5a3e5bc0a3369b7725648b293b26099`・`docs/blaines-quiz-heights-v0.129.md` |
| 公開 | ブランチ `claude/v0.129-blaines-quiz-heights` の先頭（2026-11-01 の `git ls-remote`）。v0.130〜v0.132 と `main`（`9f00943`）の祖先 |
| 文書 | `docs/blaines-quiz-heights-v0.129.md` の 3 章「利用者が指定した参照値（USER-QUIZ-HEIGHT-OFFICIAL-ZUKAN）」・4〜6 章 |
| 記録・登録 | `kyuura_engine/effects.py` の `USER_SPECIFIED_REFERENCES`（種類 `USER-QUIZ-HEIGHT-OFFICIAL-ZUKAN`・対象 `GD5-016/trainer`）・`BlainesHeightQuiz`・登録 `"GD5-016": TrainerEntry(...)`。参照値の写し `kyuura_engine/data/species_heights.json`（出典に kyuura `9242b9be89be0f747279f39c11875d1ed61763ec`） |
| 換算と判定 | 換算 `kyuura_engine/heights.py` の `height_answer_cm`（単位のある入力だけ）、判定は整数 cm の完全一致、値で答える決定 `kyuura_engine/decisions.py` の `VALUE_RANGE`。種族は図鑑番号だけで引く（`card_height`） |
| 検査 | `scripts/check_card_sources.py`（`user_specified_reference`）・`scripts/check_research_links.py`（`latest_descriptions.user_specified_references`）・`tests/log_audit.py` の `v129_problems` |
| テスト | `tests/test_blaines_quiz_heights_v0_129.py`（`RegistrationTest`・`QuizFlowTest`・`MissingReferenceTest`・`VisibilityTest`・`SaveRestoreTest`・`TrainerPathTest`）・`tests/test_species_heights_v0_129.py` |
| エンジンの報告（kyuura は再実行していない） | 全体のテスト 242 モジュール・7,073 件・失敗 0、正式な対戦 20 局で正解 26・不正解 29（コミットの文と文書 10 章） |

- 指定との対応: 文書の利用者の指定の文は「クイズの正解には、今回収集した全国図鑑No.001〜251の通常の姿の公式図鑑値を採用します。」。図鑑番号のないカードは選ぶと `UNSUPPORTED_QUIZ_HEIGHT_WITHOUT_DEX` で止め、名前から補わない（エンジンの未対応で、研究上の未解決ではない、とエンジンは書く）。答えの API は整数 cm、換算は外の層の責任。どれも 3.1 節の指定と合います。
- エンジンの写しの図鑑番号のないポケモンのカードは 225 枚（v0.129 の文書）。kyuura の 227 枚との差は、v0.129 で未登録のナッシー PR1-075・PR1-077（どちらも `pokemon.dex` がない）が写しにないためと読めます（kyuura の側で 1 枚ずつは照らしていない）。

## 4. ナッシー［Exeggutor］（PR1-075・PR1-077）の名前（今回追加）

### 4.1 利用者の指定

- 英語の併記を名前の判定に使わない。カード名を「ナッシー」、進化元を「タマタマ」、ワザ名を日本語の部分（「ふみつけ」）として扱う。
- 通常のナッシーと同じ名前として、デッキの 4 枚の制限・名前の比べ・クイズなどを処理する。
- HP・ワザの内容などを、ほかのナッシーのものへ置きかえる指定ではない。
- 原文と表示用の併記は残す。

### 4.2 原文・既存の記録との関係

- kyuura の値（`data/cards.json`。この作業で変えていない）: 名前 `name.ja`「ナッシー［Exeggutor］」、進化元 `pokemon.evolves_from.ja`「タマタマ」、ワザ名「ふみつけ[Stomp]」。カード名の原表記は変えていません。
- 印刷: PR1-077 はカードの画像（IMG-PR1-077）で名前「ナッシー[Exeggutor]」・「タマタマ[Exeggcute]から進化」・ワザ名を確かめた記録があります。**PR1-075 の印刷は未確認**のままです（pcg-search の画像は代わりの画像）。
- **UQ-BILINGUAL-NAME-GLOSS（英語の括弧書きは名前の一部か）は未解決のまま**です。利用者の指定は、エンジンがどう処理するかの指定で、p.308 の「別の言葉」に訳の併記が当たるかを決めたものではありません。[v0.122 のあとの引き継ぎ](engine-handover-after-v0.122.md) 3 章の「どちらに決めるかは原典で決まっていない」もそのままです。
- 範囲は 2 枚の 3 つの欄だけです。ほかのカードの括弧書き（アンノーン[N] など）の扱いは決めていません。

### 4.3 実装を確かめた範囲（v0.131）

| 項目 | 値 |
|---|---|
| 完成報告 | v0.131・`f715dd57abef80729ecf9ceb7bb796b3502e4ecd`・登録 `effects.USER_SPECIFIED_NAMES`・`tests/test_exeggutor_bilingual_names_v0_131.py` |
| 公開 | kyuura-engine の `refs/pull/24/head`（2026-11-01 の `git ls-remote`）。v0.132（`a6c0c95`）と `main`（`9f00943`）の祖先 |
| 文書 | `docs/exeggutor-bilingual-names-v0.131.md` の 3 章「利用者が指定した名前の扱い（USER-BILINGUAL-NAME-JAPANESE）」 |
| 記録・登録 | `kyuura_engine/effects.py` の `USER_SPECIFIED_NAMES`（種類 `USER-BILINGUAL-NAME-JAPANESE`・対象 `PR1-075/name`・`PR1-077/name`。欄ごとに写しの値・判定に使う値・表示用の併記）・`V0_131_ATTACKS`・`SAME_DATA_CARDS_V0_131`・`BILINGUAL_COIN_BONUS_PATTERN`、当てはめ `kyuura_engine/cards.py` の `_user_specified_names`（原文は `printed_name_ja` に残す） |
| 検査 | `scripts/check_card_sources.py` の `user_specified_name_problems`・`scripts/check_research_links.py`（`latest_descriptions.user_specified_names`） |
| テスト | `tests/test_exeggutor_bilingual_names_v0_131.py`（`RegistrationTest`・`OriginalTextTest`・`DeckTest`・`EvolutionTest`・`SameNameEffectTest`・`QuizTest`・`StompTest`・`CopyTransformTest`・`PersistenceTest`） |
| エンジンの報告（kyuura は再実行していない） | 全体のテスト 245 モジュール・7,146 件（失敗 1 を直して再実行 0）、正式な対戦 20 局で両方のカードがふみつけを宣言（コミットの文） |

- 指定との対応: 文書の利用者の指定の文は「対象2枚の英語併記は翻訳表示として扱い、判定に使いません。」で、名前・4 枚の制限・進化元・ワザ名・クイズ・性能を置きかえないこと・原文を残すことが 4.1 節と合います。英語だけの「Exeggutor」は別名として受け付けない、とエンジンは書きます（指定の範囲の外）。
- 2 枚は図鑑番号がないので、カツラのクイズ その1 では選ぶと止まります（3 章の指定のとおり補わない）。

## 5. ヤドキング（neo1-049）の［ちえくらべ］（今回追加）

### 5.1 利用者の指定

発動は任意。順序は次のとおり。

1. 相手が使うトレーナーカードを使えるかを、状態を変えずに確かめる。
2. ヤドキングの側が［ちえくらべ］を発動するかを選ぶ。
3. 発動するなら、コインを投げる。
4. 「おもて」なら使用を止め、コストを払わず、そのトレーナーカードを相手（トレーナーを使ったプレイヤー）の山札の上へ置く。
5. 「うら」、または発動しないなら、通常のコストの支払いと効果へ進む。

錯乱ジムとの前後関係は、この指定に含まない。

### 5.2 原文・既存の記録との関係

- 印刷の文面（kyuura の値。`pokemon.powers[0].text.ja`）は変えていません。決まっている範囲（バトル場にいるとき、相手が手札から出して使うとき、スタジアム・どうぐも当たる）は CR-MIND-GAMES-SCOPE・CR-MIND-GAMES-STADIUM-TOOL（CONFIRMED）のままです。
- この指定に関わる、実在する論点（`data/sidecar/rulings.json` で確かめた。どちらも `UNRESOLVED`。この記録で変えていない）:
  - **UQ-MIND-GAMES-OPTIONAL**: 持ち主が必ずコインを投げるのか、使うかを選べるのか。→ 指定は「任意」。
  - **UQ-MIND-GAMES-TRAINER-STEP**: トレーナーカードを使う手順（手札から出して見せる → 使うための条件 → 説明）のどこで投げるのか。→ 指定は「使えるかを確かめたあと、コストを払う前」。錯乱ジムのコインとの前後はこの論点の事例のまま残ります。
- 指定は、歴史資料上どちらの読み方が正しいかを決めたものではありません。[ちえくらべ・フラッシュ・とりかえっこプリーズの調査](trainer-reaction-faceup-ownership-research.md) 3.2・3.3 節の候補と比べもそのままです。

### 5.3 実装を確かめた範囲（v0.132）

| 項目 | 値 |
|---|---|
| 完成報告 | v0.132・`a6c0c95`・`docs/slowking-mind-games-v0.132.md` |
| 完全なハッシュ | `a6c0c955fa66200f8677a87201b3726101383ec5`（2026-11-01 の `git ls-remote` で kyuura-engine の `refs/pull/25/head` がこの値。`main` の `9f009436733ad0b060d8a22a7bddad26fe73ff3e` は PR #25 のマージで、このコミットを含む） |
| 文書 | `docs/slowking-mind-games-v0.132.md` の 3 章「利用者が指定した規則（USER-MIND-GAMES-OPTIONAL-BEFORE-COST）」・5 章・6 章 |
| 記録・登録 | `kyuura_engine/effects.py` の `USER_SPECIFIED_RULES["neo1-049/power/0"]`（種類 `USER-MIND-GAMES-OPTIONAL-BEFORE-COST`。解決済みにしない論点 `UQ-MIND-GAMES-OPTIONAL`、関係する論点 `UQ-MIND-GAMES-TRAINER-STEP`）・`BlockOpponentHandTrainerOnHeads`・`V0_132_POWERS`・`V0_132_ATTACKS`・`trainer_reaction_sources`・`trainer_reaction_use_stop` |
| 手順 | `kyuura_engine/engine.py` の `_play_trainer`・`_offer_trainer_reaction`・`_resume_trainer_reaction`・`_trainer_reaction_decline_check`、山札の上に置く `kyuura_engine/zones.py` の `blocked_trainer_to_deck_top` |
| 検査 | `scripts/check_card_sources.py` の `user_specified_rule_problems`・`scripts/check_research_links.py`（`latest_descriptions.user_specified_rules`）・`tests/log_audit.py` の `v132_problems` |
| テスト | `tests/test_slowking_mind_games_v0_132.py`（`RegistrationTest`・`ThreePathsTest`・`ScopeTest`・`DeclineLookaheadTest`・`CopyAndEspTest`・`PersistenceAndAnswersTest`・`MudImpactTest`・`OwnershipTest`・`AuditTamperingTest`・`DocumentTest`） |
| エンジンの報告（kyuura は再実行していない） | 全体のテスト 246 モジュール・7,177 件（失敗 10 を直して再実行 0）、正式な対戦 36 局で機会 150・使う 79（おもて 48・うら 31）・使わない 71、2 局が錯乱ジム（MG1）での道具の予期しない拒否（コミットの文と文書 10・12 章） |

- 指定との対応: 記録の手順は 5.1 節と同じ順で、「使えないカードの宣言には選択もコインもない」とします。「おもて」で置く先は「使ったプレイヤーの山札の上」（5.1 節の「相手の山札」と同じプレイヤー。ヤドキングの側から見た相手）。
- 指定が決めない場面は、エンジンが止めます（エンジンの報告）: 錯乱ジムとの前後 `UNRESOLVED_MIND_GAMES_CHAOS_GYM_ORDER`（MG1）、ポケモンとして出すトレーナー `UNRESOLVED_MIND_GAMES_PLAY_AS_POKEMON`（MG2）、使ったら番が終わるトレーナー `UNRESOLVED_MIND_GAMES_BLOCKED_TURN_END`（MG3）、おもてのカードのある山札（既存の FU4）。MG3 の問いは kyuura に論点がない、とエンジンは報告しています（kyuura では論点を加えていない。7 章）。

## 6. とりかえっこプリーズ（PR1-027）

指定の内容・原文との差・決めていないことは [とりかえっこプリーズの所有者の簡略仕様](engine-user-swap-ownership.md) の 1〜6 章（2026-10-31）にあります。今回の利用者の指定（交換が成立した 2 枚は対戦終了まで受け取った側の所有、以後の移動は新しい所有者が基準、元の出所は追跡用に保持し実物の所有権とは区別、拒否なら所有者を変えず通常の 2 枚引き、錯乱ジムの「あなた」「相手」は決めない）は、その 3 章・5 章と同じ内容で、新しく決めたことはありません。実装の経過は同じ文書の 8 章（今回追加）に書きました。

## 7. 記録のしかたと、決めていないこと

- **原文を書き換えていません。** 利用者の指定のために、印刷の文面・カード名の原表記・カードデータ・公式情報の出典を変えていません。
- **歴史的な未解決は解決済みにしていません。** UQ-STATED-COUNT-SHORT・UQ-DESTRUCTIVE-FIRE-FAILURE・UQ-ESP-REDO・UQ-BILINGUAL-NAME-GLOSS・UQ-SWAP-PLEASE-OWNERSHIP・UQ-CHAOS-GYM-BORROWED-TURN・UQ-MIND-GAMES-OPTIONAL・UQ-MIND-GAMES-TRAINER-STEP は `UNRESOLVED` のままです（`tests/test_engine_user_specifications.py` が確かめる）。
- **計画と確かめた実装を分けています。** ひかるバンギラスは計画だけです（2026-11-01 の時点。2026-11-02 に v0.133 を固定コミットで確かめた経過は 8 章）。v0.129〜v0.132 は固定コミットを読んで場所を確かめましたが、コードの実行・テストの再実行はしていません。
- **`engine_positions`・`engine_imports` に加えていません。** v0.129〜v0.132 は完成した固定コミットがありますが、取り込み（`engine_imports`）は版の裁定の表・未解決の一覧・停止コード（v0.132 の MG1〜MG3 など）と kyuura の記録との照合を伴い、今回の範囲（利用者の指定の記録）を超えます。取り込むときは、各指定の文書の節（`document`・`section`）・登録・検査の場所（この文書の 3.3・4.3・5.3 節、swap の 8 章）を使い、`kyuura_handling` に「利用者の指定で、公式の裁定・最新の説明・エラッタではない。論点は未解決のまま」と書きます。未完成の版（v0.133）の取り込みの記録・架空のコミットは作りません。
- エンジンの報告事項のうち、MG3 の新しい問い・PR1-027 の名前の末尾の「！」・図鑑番号のない 225 枚などは、この記録で論点・訂正にしていません（別の作業）。
- エンジンの登録表の写し（`data/curation/engine_registered_cards.json`。v0.113）・`data/engine_targets.json` は変えていません。

## 8. ひかるバンギラスの完成後の経過（2026-11-02 日本時間の追記）

1〜7 章は 2026-11-01 の記録で、変えていません（1 章の表の該当行だけ、今の状態に合わせた）。

- 利用者からの完成報告: v0.133・ブランチ `claude/v0.133-shining-tyranitar`・最終コミット `298f08d603c1f763fc45a97fc306291d8b95abb0`・版の文書 `docs/shining-tyranitar-v0.133.md`（kyuura への報告事項は 12 章）。
- 固定コミットを読み取りだけで確かめ、登録・利用者の指定の記録・共通の処理・検査・監査・テストの場所と、指定との照合を [ひかるバンギラスの処理](engine-user-shining-tyranitar.md) の 7 章に書きました。3 章の指定はどれも実装と一致しました。実装が具体化したこと（トラッシュするカードを選ぶのはワザを使ったプレイヤー・相手のポケモンへの防護を山札に当てはめない）は、利用者の指定としては記録していません。
- テスト・対戦の結果はエンジンの報告で、kyuura は実行していません（全体の実行 247 モジュール・7,208 件・失敗 2、直したあとの追加の再実行 3 モジュール・82 件・失敗 0、7,209 件の状態の全体の再実行はない）。
- **ナツメのESPの経路は確認済みにしていません**（テストは色マーカーを直接のせた盤面で、仕組みの確認）。
- UQ-STATED-COUNT-SHORT・UQ-DESTRUCTIVE-FIRE-FAILURE などは未解決のままです。「足りなければあるだけ」はこの 2 つのワザだけで、ほかのカードに広げていません。
- `engine_positions`・`engine_imports` には、今回も加えていません（7 章の理由のまま）。
