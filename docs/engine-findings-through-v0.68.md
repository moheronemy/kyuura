# 拡張パック以外の商品の収録と、エンジンv0.26〜v0.68の記録の還元（作業の記録）

2026-10-19。kyuura の基準は main の `4b73536e5507581c3d2cf44f7d519021850f9e81`、作業ブランチは `claude/non-pack-catalog-engine-findings-v0.68`。
kyuura-engine は、ブランチ `claude/v0.68-final-pmcg-cards` のコミット `24bfbe2c1bf3b5fb0521e229ac92cf2fa4a154a1`（v0.68）を固定した読み取りの参照にした（エンジンの main は使っていない）。
エンジンのリポジトリ・写しの元（`ecb2d69`）・研究の基準（`3f34908`）・固定の参照データは変えていない。PR の作成・マージ・main への直接のプッシュはしていない。

この作業では原典（『オフィシャルブック2000』など）の画像を開いていない。Silver Bible のキャプチャ・OCR・画像の読み直しもしていない。
pcg-search.com は、同じ版のカードページを 187 ページだけ読み直した（2026-10-19。全 681 ページは取り直していない）。カード一覧のページも 1 回読み、取り込んだ 23 商品の欄が前の取得と同じことを確かめた。

## 1. 拡張パック以外の商品の収録

### 1.1 商品ごとの数

`data/product_items.json` の `counts`。元の項目は pcg-search のカードページの数で、カードの種類の数・デッキの封入枚数とは別。

| 記号 | 商品 | 発売 | 元の項目 | 記録 | 番号違いのまとめ | 対戦のカードでない項目 | 通常の対戦のカード |
|---|---|---|---|---|---|---|---|
| `ES1` | 拡張シート 第1弾（青版） | 1998-03-23 | 36 | 36 | 0 | 0 | 36 |
| `ES2` | 拡張シート 第2弾（赤版） | 1998-06-17 | 36 | 36 | 0 | 0 | 36 |
| `ES3` | 拡張シート 第3弾（緑版） | 1998-11-24 | 53 | 36 | 0 | 17 | 36 |
| `SI` | 映画公開記念パック「サザンアイランド」 | 1999-07-17 | 18 | 18 | 0 | 0 | 18 |
| `GD1` | ポケモンジム第1弾「ニビシティジム タケシ」 | 1998-04-26 | 25 | 25 | 0 | 0 | 25 |
| `GD2` | ポケモンジム第1弾「ハナダシティジム カスミ」 | 1998-04-26 | 24 | 24 | 0 | 0 | 24 |
| `GD3` | ポケモンジム第2弾「クチバシティジム マチス」 | 1998-07-25 | 25 | 25 | 0 | 0 | 25 |
| `GD4` | ポケモンジム第2弾「タマムシシティジム エリカ」 | 1998-07-25 | 28 | 28 | 0 | 0 | 28 |
| `GD5` | ポケモンジム第3弾「グレンタウンジム カツラ」 | 1999-02-26 | 25 | 25 | 0 | 0 | 25 |
| `GD6` | ポケモンジム第3弾「ヤマブキシティジム ナツメ」 | 1999-02-26 | 26 | 26 | 0 | 0 | 26 |
| `QSG` | クイックスターターギフト | 1998-12-04 | 58 | 58 | 0 | 0 | 58 |
| `IP1` | イントロパック（フシギダネデッキ） | 1999-07-30 | 40 | 21 | 19 | 0 | 21 |
| `IP2` | イントロパック（ゼニガメデッキ） | 1999-07-30 | 40 | 21 | 19 | 0 | 21 |
| `IPH` | イントロパック（キラカード） | 1999-07-30 | 2 | 2 | 0 | 0 | 2 |
| `PR1` | プロモーションカード（第1弾〜闇からの挑戦の時期） | — | 90 | 89 | 0 | 1 | 86 |
| `PF1` | プレミアムファイル | 1999-12-10 | 9 | 9 | 0 | 0 | 9 |
| `PF2` | プレミアムファイル2 | 2000-07-08 | 9 | 9 | 0 | 0 | 9 |
| `PF3` | プレミアムファイル3 | 2000-11-23 | 9 | 9 | 0 | 0 | 9 |
| `NIP1` | イントロパック★neo（チコリータデッキ） | 2001-04-06 | 30 | 16 | 14 | 0 | 16 |
| `NIP1X` | イントロパック★neo（チコリータデッキの拡張カード） | 2001-04-06 | 10 | 10 | 0 | 0 | 10 |
| `NIP2` | イントロパック★neo（ワニノコデッキ） | 2001-04-06 | 30 | 16 | 14 | 0 | 16 |
| `NIP2X` | イントロパック★neo（ワニノコデッキの拡張カード） | 2001-04-06 | 10 | 10 | 0 | 0 | 10 |
| `PRN` | プロモーションカード（neo の時期） | — | 48 | 48 | 0 | 0 | 47 |
| 計 | | | 681 | 597 | 66 | 18 | 593 |

- 通常の対戦のカードでない記録 4 件: ガルーラルール専用（PR1-038 タッチ交代！・PRN-048 タッチ世代交代！）、カードに「公式大会では使えません」とある（PR1-027 とりかえっこプリーズ・PR1-073 カスミのてあて）。`play_scope` で区別し、記録には入れた。
- 対戦のカードでない項目 18 件（拡張シート第3弾の裏面の違うおまけのカード 17 件と、イラストコンテストの賞のカード 1 件）は `data/cards.json` に入れず、`data/product_items.json` の `non_game_items` に元のページから追えるように残した。

### 1.2 id の規則

- **カード**: 「商品の記号-カードページ名の末尾 3 桁」（例 `GD1-009` = `1stgymd1009`）。サイトの並び順（`list_number`）に依らない。既存の 780 件の id は変えていない。
- **商品**: `data/curation/non_pack.json` の `products` の記号（ES1〜ES3・SI・GD1〜GD6・QSG・IP1・IP2・IPH・PR1・PF1〜PF3・NIP1・NIP1X・NIP2・NIP2X・PRN）。一度決めたら変えない。
- **元の項目との対応**: `data/product_items.json` の `items`（ページ → `card`・`copy`・`non_game` と記録の id）。記録の `source_ids.pcg_search` と `copies` から逆に引ける。
- **番号違いのまとめ**: イントロパックのデッキ（IP1・IP2・NIP1・NIP2）は、番号（丸数字）ごとにページがある。番号のほかの欄がすべて同じページだけを 1 つの記録にまとめ、いちばん小さいページの番号を id にした（66 ページ）。プロモは同じ内容でも配布ごとに別の記録のまま。
- **同じカードの組**（`data/same_card_groups.json`）: 名前（表記の揺れ「ウィンディ／ウインディ」だけを正規化）・HP・特殊能力名・ワザ名が同じ記録をまとめ、数値・文面の違いを要素ごとに書いた。名前だけではまとめない。201 組（拡張パックの記録を含む組 135）。組の 2 件目以降の要素 288 件のうち、数値と文面（句読点の違いを除く）が最初の記録と同じもの 200 件。文面は、同じ 189・句読点だけ違う 11・似ている 16・違う 72。ページの判定（`docs/cards/reprints.md`）との食い違いは 0。

### 1.3 欄の正規化と値の欠け

- 名前・段階・HP・タイプ・弱点・抵抗力・にげる・特殊能力・ワザ・本文は pcg-search の転記。英語版の文面では補っていない。
- **進化元**: 1 進化・2 進化 135 枚のうち、同じカードの拡張パックの記録から 21 枚、同じサイトのカードページの「進化ライン検索」から 105 枚。9 枚は値の欠け（化石のポケモン 4 枚は進化ラインに「なにかの化石」「ちていのかせき」の 2 つがあり決まらない、「わるい」のポケモン 3 枚は進化ラインの名前が「わるい」のない名前、マチスのライチュウ GD3-003 と neo のプロモのカポエラー PRN-030 はサイトの種類の欄（1 進化）と進化ラインの段階（たね）が違う。この 2 枚は段階も値の欠け）。英語版の進化元は照らし合わせにだけ使った（同じ 51、違う 0。進化ラインと同じ 20）。名前の接頭辞からの推測はしていない。
  - 作業の途中で、進化ラインのたねポケモンの位置にいる自分自身を進化元として読む誤り（マチスのライチュウ）を見つけて直し、段階の食い違いを検査に加えた。
- **にげる**: 転記の `null` 63 枚は、読み直したページですべて「-」（にげるエネルギーなし。0）だった（`pcg_search_page_dash`）。
- **補足欄**: 4 枚の補足（大会での扱いの表示・専用ルールの表示）と 2 枚のカードの説明の文は、本文につながず `notes` に残した。
- **値の欠け**（`data_gaps`。欄ごと。商品全体は止めていない）: レベル 423（pcg-search にレベルの欄がない）、図鑑番号 227、進化元 9、エネルギーの効果文 8（無色2個エネルギー。転記に説明文がない。印刷のカードに説明文がないのかは確かめていない）、段階 2。
- 読み直した 187 ページは、転記と同じ方法で読んだ欄がすべて転記と同じだった（`transcript_differences` 0）。

### 1.4 収録していない商品・範囲

`data/curation/non_pack.json` の `uncovered_products`（ページは [拡張パック以外の商品](cards/other-products.md)）。

- pcg-search の「第1弾 スターターパック」（基本エネルギー 6 種）: 拡張パックの記録 PMCG1-097〜102 として収録済み。ページとの対応づけはしていない。
- 「ポケモンカードGB」「GB2」の専用カード（48 ページ）: ソフトの中だけのカードで対象外。
- ポケモンカードVS・★web・それ以降: 新裏の別のシリーズで対象外（範囲を広げていない）。
- pcg-search のカードリストにない旧裏期の商品・配布物: 調べていない。23 商品ですべてを収録できたとは言えない。

## 2. エンジンの実装の対象

`data/engine_targets.json`（読み方は [エンジンの実装の対象](engine-targets.md)）。エンジンの登録表の写し `data/curation/engine_registered_cards.json`（v0.68: ワザ 597・トレーナー 94・特殊能力 58・特殊エネルギー 4、対戦用のカード 457）と比べた。

| | 件数 |
|---|---|
| エンジンの登録がある id（拡張パック第1〜6弾） | 457 |
| 登録のない id で、エンジンが使う欄が登録されたカードと同じもの（`mechanically_equivalent`。実装済みとは数えない） | 96（ポケモンジム 52・イントロパック 24・プロモ 20） |
| 再利用の候補（同じカードの組に登録があって欄の一部が違う 80・効果の文面がどれも登録された実装と同じ 130） | 210 |
| 新しい効果の実装が要るもの | 614 |
| 実装の対象の分類: 対象にできる 1,343・値の欠け 30・特別なルールの設計 4・対戦のカードでない 18 | |

新しいカードの効果は実装していない。強さ・勝率・デッキの釣り合いは評価していない。

## 3. エンジン v0.26〜v0.68 の還元

### 3.1 版ごとの取り込み

取り込みは版ごとに 1 件（`data/sidecar/rulings.json` の `engine_imports`）。文書は固定した参照（`24bfbe2`）で読み、コミットは各版の最後のコミット。エンジンの表で id の付いた行と、研究の対応表（`research_links.json`）の停止コードの id を、（版・文書・id）で数えた。id のない表（カードの一覧・登録の表）の行は、取り込みの単位にしていない。

| 版 | コミット | 取り込み | 文書 | id | 論点に結んだ | 取り込まない | 結んだ論点 |
|---|---|---|---|---|---|---|---|
| v0.26 | `fcf8987` | ENGINE-FCF8987 | preset-decks-v0.26.md、v0.26-verification.md | 0 | 0 | 0 | 裁定の表なし |
| v0.27 | `e730ce2` | ENGINE-E730CE2 | scyther-v0.27.md、v0.27-verification.md | 22 | 0 | 22 | — |
| v0.28 | `c7382db` | ENGINE-C7382DB | existing-effect-pokemon-v0.28.md | 0 | 0 | 0 | 裁定の表なし |
| v0.29 | `102bc6c` | ENGINE-102BC6C | existing-effect-pokemon-v0.29.md | 0 | 0 | 0 | 裁定の表なし |
| v0.30 | `43fed61` | ENGINE-43FED61 | discard-energy-attacks-v0.30.md | 0 | 0 | 0 | 裁定の表なし |
| v0.31 | `3a21551` | ENGINE-3A21551 | held-cards-v0.31.md | 15 | 10 | 5 | UQ-COIN-IN-NULLIFIED-ELEMENT・UQ-COPIED-ATTACK・UQ-DESTINY-BOND-KO・UQ-DISCARD-ENERGY-TIMING-CONFUSION・UQ-ENERGY-BURN-TRANSFER・UQ-EXTRA-ENERGY-COLORLESS・UQ-STATED-COUNT-SHORT・UQ-TARGET-WITHOUT-EFFECT・UQ-UP-TO-ZERO-CHOICE |
| v0.32 | `f8563c3` | ENGINE-F8563C3 | bench-search-counter-drain-v0.32.md | 21 | 1 | 20 | UQ-OPPONENT-POKEMON-COUNTERS |
| v0.33 | `382fed4` | ENGINE-382FED4 | cd4-opponent-energy-coins-v0.33.md | 31 | 0 | 31 | — |
| v0.34 | `2d0f60f` | ENGINE-2D0F60F | barrier-resume-coin-bonus-v0.34.md | 9 | 2 | 7 | UQ-POISON-OVERWRITE-ORDER・UQ-REDUCED-DAMAGE-BENCH-TARGET |
| v0.35 | `3730b3f` | ENGINE-3730B3F | coin-groups-damage-order-v0.35.md | 0 | 0 | 0 | 裁定の表なし |
| v0.36 | `b2d6a26` | ENGINE-B2D6A26 | sand-attack-retreat-lock-v0.36.md | 31 | 3 | 28 | UQ-ATTACK-PRE-DAMAGE-COIN-ORDER・UQ-RETURN-TO-DECK-KO-ORDER |
| v0.37 | `beb7b0d` | ENGINE-BEB7B0D | fifteen-reused-effects-v0.37.md | 1 | 1 | 0 | UQ-BENCH-DAMAGE-WEAKNESS-RESISTANCE |
| v0.38 | `0f6f601` | ENGINE-0F6F601 | bench-switch-combined-v0.38.md | 18 | 1 | 17 | UQ-DAMAGE-TRIGGER-TIMING |
| v0.39 | `ffb941c` | ENGINE-FFB941C | selfdestruct-spread-count-v0.39.md | 25 | 1 | 24 | UQ-UP-TO-ZERO-CHOICE |
| v0.40 | `cbc5515` | ENGINE-CBC5515 | count-condition-switch-return-v0.40.md | 35 | 1 | 34 | UQ-ATTACK-LOCK-SOURCE-RETURNED |
| v0.41 | `3a412d0` | ENGINE-3A412D0 | heal-counter-status-v0.41.md | 29 | 1 | 28 | UQ-COUNTER-TRANSFER-PROTECTED |
| v0.42 | `1e0d340` | ENGINE-1E0D340 | power-decisions-v0.42.md | 2 | 2 | 0 | UQ-CARD-USE-WITHOUT-TARGET |
| v0.43 | `96a0f1d` | ENGINE-96A0F1D | declared-entry-powers-v0.43.md | 2 | 2 | 0 | UQ-ENTRY-POWER-DURING-ATTACK・UQ-UP-TO-ZERO-CHOICE |
| v0.44 | `7e8a930` | ENGINE-7E8A930 | search-evolution-once-attacks-v0.44.md | 6 | 3 | 3 | UQ-CARD-USE-WITHOUT-TARGET・UQ-EVOLUTION-PERMISSION-FROM-DECK・UQ-STATED-COUNT-SHORT |
| v0.45 | `c7c91ac` | ENGINE-C7C91AC | conditional-damage-energy-v0.45.md | 2 | 2 | 0 | UQ-ATTACK-PRE-DAMAGE-COIN-ORDER・UQ-EVOLUTION-PERMISSION-FROM-DECK |
| v0.46 | `30e856e` | ENGINE-30E856E | continuous-powers-v0.46.md | 2 | 2 | 0 | UQ-CALMING-AROMA-RETALIATION・UQ-RETREAT-COST-PAYMENT |
| v0.47 | `556a21a` | ENGINE-556A21A | fossil-hidden-info-v0.47.md | 4 | 4 | 0 | UQ-NON-ATTACK-DAMAGE-MODIFIERS・UQ-PLAY-AS-POKEMON |
| v0.48 | `7d7f4c5` | ENGINE-7D7F4C5 | effective-pokemon-properties-v0.48.md | 3 | 3 | 0 | UQ-CHANGE-ABSENT-WEAKNESS-RESISTANCE・UQ-EVOLUTION-HP-BELOW-DAMAGE・UQ-SHIFT-COLOR-DURATION |
| v0.49 | `2f63654` | ENGINE-2F63654 | virtual-attacks-transformation-v0.49.md | 11 | 11 | 0 | UQ-COPIED-ATTACK・UQ-RECALL-SCOPE・UQ-SHAPESHIFT-SCOPE・UQ-TRANSFORM-SCOPE |
| v0.50 | `218eac7` | ENGINE-218EAC7 | mew-devolution-spray-v0.50.md | 5 | 5 | 0 | UQ-CARD-USE-WITHOUT-TARGET・UQ-DEVOLUTION-SAME-TURN・UQ-EVOLUTION-HP-BELOW-DAMAGE・UQ-SHAPESHIFT-SCOPE |
| v0.51 | `674aff0` | ENGINE-674AFF0 | discard-to-bench-v0.51.md | 16 | 2 | 14 | UQ-CARD-USE-WITHOUT-TARGET |
| v0.52 | `adc5448` | ENGINE-ADC5448 | field-return-v0.52.md | 3 | 3 | 0 | UQ-ATTACHED-CARDS-WHEN-RETURNED・UQ-CARD-USE-WITHOUT-TARGET |
| v0.53 | `a48b49b` | ENGINE-A48B49B | search-retrieval-trainers-v0.53.md | 10 | 3 | 7 | UQ-CARD-USE-WITHOUT-TARGET・UQ-STATED-COUNT-SHORT・UQ-UP-TO-ZERO-CHOICE |
| v0.54 | `d86776f` | ENGINE-D86776F | hand-deck-trainers-v0.54.md | 1 | 1 | 0 | UQ-UP-TO-ZERO-CHOICE |
| v0.55 | `352c0a2` | ENGINE-352C0A2 | instant-trainers-v0.55.md | 8 | 8 | 0 | UQ-CARD-USE-WITHOUT-TARGET・UQ-STATED-COUNT-SHORT・UQ-TARGET-WITHOUT-EFFECT |
| v0.56 | `8d24eb2` | ENGINE-8D24EB2 | trainer-decisions-turn-effects-v0.56.md | 6 | 6 | 0 | UQ-CARD-USE-WITHOUT-TARGET・UQ-MISTY-SELF-DAMAGE・UQ-POISON-OVERWRITE-ORDER・UQ-UP-TO-ZERO-CHOICE |
| v0.57 | `5b32812` | ENGINE-5B32812 | stadiums-v0.57.md | 8 | 8 | 0 | UQ-ATTACK-PRE-DAMAGE-COIN-ORDER・UQ-CARD-USE-WITHOUT-TARGET・UQ-CHAOS-GYM-BORROWED-TURN・UQ-FUCHSIA-GYM-ONCE-PER-TURN・UQ-NON-ATTACK-DAMAGE-MODIFIERS・UQ-STATED-COUNT-SHORT・UQ-TARGET-WITHOUT-EFFECT・UQ-TRAINER-BAN-SCOPE |
| v0.58 | `1392f8c` | ENGINE-1392F8C | stadium-reuse-special-energy-v0.58.md | 11 | 6 | 5 | UQ-NON-ATTACK-DAMAGE-MODIFIERS・UQ-RETREAT-COST-PAYMENT・UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY |
| v0.59 | `20a99f1` | ENGINE-20A99F1 | energy-control-power-suppression-v0.59.md | 10 | 7 | 3 | UQ-ATTACH-BLOCK-SCOPE・UQ-BLAINE-SECOND-ATTACH・UQ-BUZZAP-TARGET-AND-COLOR・UQ-GOOP-GAS-NEW-POKEMON・UQ-SHAPESHIFT-SCOPE・UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY |
| v0.60 | `f2068f6` | ENGINE-F2068F6 | coins-defense-rebellion-v0.60.md | 2 | 2 | 0 | UQ-SPEED-STAR-SCOPE・UQ-TRANSPARENCY-COIN-ORDER |
| v0.61 | `4748b10` | ENGINE-4748B10 | reactive-powers-trainer-damage-v0.61.md | 7 | 7 | 0 | UQ-COUNTERATTACK-DOUBLE-KO・UQ-DESTINY-BOND-KO・UQ-NON-ATTACK-DAMAGE-MODIFIERS・UQ-POWER-DAMAGE-WEAKNESS-RESISTANCE・UQ-SCRAM-TIMING・UQ-SINKHOLE-TIMING |
| v0.62 | `2c8440d` | ENGINE-2C8440D | history-attacks-v0.62.md | 5 | 5 | 0 | UQ-COPIED-ATTACK |
| v0.63 | `5b00b5d` | ENGINE-5B00B5D | hidden-card-trainers-v0.63.md | 2 | 2 | 0 | UQ-CARD-USE-WITHOUT-TARGET・UQ-UP-TO-ZERO-CHOICE |
| v0.64 | `3fd2e89` | ENGINE-3FD2E89 | geodude-line-unbounded-coins-v0.64.md | 0 | 0 | 0 | 裁定の表なし |
| v0.65 | `1e54e3a` | ENGINE-1E54E3A | reactive-decisions-v0.65.md | 10 | 10 | 0 | UQ-ATTACHED-CARDS-WHEN-RETURNED・UQ-REACTIVE-SWITCH-DURING-ATTACK・UQ-TRAINER-BAN-SCOPE |
| v0.66 | `20c82da` | ENGINE-20C82DA | optional-trainers-v0.66.md | 5 | 5 | 0 | UQ-CHARITY-BELOW-ZERO・UQ-ESP-REDO |
| v0.67 | `a83779a` | ENGINE-A83779A | secret-plan-preflight-v0.67.md | 2 | 2 | 0 | UQ-FACE-DOWN-CARD |
| v0.68 | `24bfbe2` | ENGINE-24BFBE2 | final-pmcg-cards-v0.68.md | 18 | 4 | 14 | UQ-ENERGY-DRAIN-ATTACKER-KO・UQ-ENERGY-DRAIN-NO-ENERGY・UQ-MULTIPLE-DAMAGE-TRIGGERS-ONE-ATTACK |

- 計: id 398 件（論点に結んだ 136・取り込まない 262）。v0.5〜v0.25 とあわせて 979 件。
- 取り込まない 262 件の分類: 処理の記録（分類の欄のない、印刷の文面と既存の記録から決めた処理）143・エンジンが CONFIRMED とした当てはめ 56・SUPPORTED の読み方 37・既存の論点の当てはめ 10・実装上の仮定 9・実装の都合 4・採用した仕様 3。状態: カードごとの当てはめ 226・既存の記録の当てはめ（`kyuura_records`）20・対象外 13・採用した仕様 3。
- CONFIRMED・SUPPORTED の当てはめを新しい裁定（`CR-`）にしなかった理由: カードごとの文面の当てはめで、既存の一般規定（`GR-`）・裁定の再利用であること、kyuura が原典を読み直していないこと、テストが通ったことは公式の裁定の根拠にならないこと。行ごとの理由とエンジンの分類は `not_imported` にある。

### 3.2 未解決の論点

エンジンの停止コード（と数えるコードのない問い）を、kyuura の論点に結んだ。同じ形の問いはカードをまとめ（カードごとの答えは同じとは限らないので、事例 `cases` にエンジンの id を残す）、同じ問いが既存の論点にあれば既存の論点に結んだ。

- 新しい論点 47 件:

| 論点 | 問い（要約） | エンジンの id | 事例 |
|---|---|---|---|
| UQ-CARD-USE-WITHOUT-TARGET | 「使えない」と書かれていないトレーナー・スタジアム・特殊能力を、説明が選ばせるもの・処理するものがないときに使えるか（使って何も起こらずに使… | DV4（v0.50）・EM1（v0.55）・FG2（v0.57）・FH1（v0.55）・FJ1（v0.52）・FT1（v0.51）・GL1（v0.55）・LS1（v0.56）・MY1（v0.56）・PW1（v0.42）・PW2（v0.42）・QZ1（v0.63）・RG1（v0.56）・RV1（v0.51）・SB1（v0.55）・ST1（v0.53）・SU2（v0.52）・TR1（v0.44） | 18 |
| UQ-TARGET-WITHOUT-EFFECT | 説明の効果が何も起こらないポケモン（ダメージカウンターがない・エネルギーカードがついていない・特殊状態がない）を、トレーナー・スタジアム・特… | GL2（v0.55）・HC8（v0.31）・SB2（v0.55）・SP1（v0.55）・TG1（v0.57） | 5 |
| UQ-UP-TO-ZERO-CHOICE | 「最大N枚」「好きなだけ」と書き、「のぞむなら」「てよい」「ことができる」のない効果で、選べるものがあるのに 0 枚（0 匹）を選べるか | GS1（v0.39）・HC5（v0.31）・HC5（v0.54）・HC5（v0.63）・HC7（v0.31）・NG1（v0.53）・PW3（v0.43）・RT1（v0.56） | 10 |
| UQ-STATED-COUNT-SHORT | 説明が決まった枚数・個数を扱う効果で、選べるもの・山札・ダメージカウンターがその数より少ないとき、できるだけ処理するのか、その要素を処理しな… | FC1（v0.44）・FC1（v0.53）・HC6（v0.31）・MW1（v0.55）・VG1（v0.57） | 7 |
| UQ-SPECIAL-ENERGY-AS-TYPED-ENERGY | レインボーエネルギー・［エネエネ］でエネルギーとしてついたカード・無色の特殊エネルギーを、説明の「「X」エネルギー（カード）」「基本エネルギ… | BZ2（v0.59）・RB1（v0.58）・RB2（v0.58）・RB3（v0.58）・TE2（v0.58） | 5 |
| UQ-NON-ATTACK-DAMAGE-MODIFIERS | ワザでないダメージ（ポケモンチェックのどく・レインボーエネルギーの 10・スタジアム・トレーナーのダメージ）に、受けるダメージを変える特殊能… | EX1（v0.57）・KA1（v0.47）・RB4（v0.58）・TD1（v0.61） | 4 |
| UQ-ATTACK-PRE-DAMAGE-COIN-ORDER | ワザの宣言のあとに投げるコイン（p.309 の手順 4 の効果・手順 5 のこんらん・クチバシティジム）が重なるとき、どの順番に投げ、手順 … | AC13（v0.36）・AC13（v0.45）・AC6（v0.36）・VM1（v0.57） | 3 |
| UQ-TRAINER-BAN-SCOPE | トレーナーカードを使えない効果がはたらいているプレイヤーが、場のスタジアムの効果を使う・ついているトレーナーカードの効果（変わり身の術の入れ… | NT3（v0.65）・STB1（v0.57） | 2 |
| UQ-ATTACHED-CARDS-WHEN-RETURNED | 場のポケモンを手札・山札にもどす効果で、ついているトレーナーカード（プラスパワー・ディフェンダー・変わり身の術）をどこに置くか | NT2（v0.65）・SU1（v0.52） | 2 |
| UQ-POISON-OVERWRITE-ORDER | 受けるダメージの違う特殊などくが重なるとき（通常のどくのポケモンがどくどくを受ける・キョウのどくとワザの特殊などく）、どちらの量のどくが残る… | KG1（v0.56）・TP3（v0.34） | 2 |
| UQ-RETREAT-COST-PAYMENT | 「にげる」のエネルギーの数を変える効果が重なるとき・1 枚で 2 個を出すエネルギーで払うとき、トラッシュしてよいカードの数をどう決めるか | CP2（v0.46）・RT1（v0.58） | 2 |
| UQ-TRANSFORM-SCOPE | メタモンの［へんしん］で相手の対戦ポケモンと同じカードになったとき、写したカードの何が使えるか（タイプのエネルギーの数え方・写したカードの特… | TE1（v0.49）・TF1（v0.49）・TF2（v0.49） | 3 |
| UQ-SHAPESHIFT-SCOPE | タケシのキュウコンの「ばける」でのせたカードのあるポケモンの扱い（かがくへんかガスで力が消えたとき・のせたカードの「場に出た時」の特殊能力・… | BZ4（v0.59）・DG1（v0.49）・DG2（v0.49）・DG3（v0.49）・DV5（v0.50） | 5 |
| UQ-RECALL-SCOPE | 思い出させるで進化前のカードのワザを使うとき、どのワザを選べるか（進化していない・2 進化のいちばん下のたね・使ったあと対戦ポケモンが入れか… | RC1（v0.49）・RC2（v0.49）・RC3（v0.49）・RC4（v0.49） | 4 |
| UQ-DEVOLUTION-SAME-TURN | その番に退化したポケモンを同じ番に進化させられるか、また退化の前にその番に使った「自分の番ごとに1回」の特殊能力を、またいちばん上になったカ… | DV2（v0.50）・DV3（v0.50） | 2 |
| UQ-COPIED-ATTACK | ほかのカードのワザを自分のワザとして使う・まねる効果（ゆびをふる・ちょうのうりょく・オウムがえし・へんしん・思い出させる）で、そのワザの使う… | ED1（v0.62）・HC9（v0.31）・MM1（v0.62）・MM2（v0.62）・OM1（v0.62）・OM2（v0.62）・VA1（v0.49） | 8 |
| UQ-REACTIVE-SWITCH-DURING-ATTACK | 相手のワザの最中に、ついているトレーナー・特殊能力で入れ替える・ダメージを肩代わりする（変わり身の術・［にげこむ］・［ベンチガード］）とき、… | BG0（v0.65）・BG1（v0.65）・BG2（v0.65）・FL0（v0.65）・FL1（v0.65）・KD1（v0.65）・NT1（v0.65）・RX1（v0.65） | 8 |
| UQ-ESP-REDO | ナツメのESPでコインを投げ直すとき、相手プレイヤーが投げるコイン・2 枚以上ついているとき・「ナツメのポケモン」でなくなったときをどう扱う… | ES0（v0.66）・ES1（v0.66）・ES2（v0.66）・ES3（v0.66） | 4 |
| UQ-PLAY-AS-POKEMON | ポケモンとして出すトレーナーカード（なにかの化石・ピッピ人形）を、対戦準備の最初のポケモンとして出せるか、「にげる」のエネルギーの数、ポケモ… | PF1（v0.47）・PF2（v0.47）・PF3（v0.47） | 3 |
| UQ-FACE-DOWN-CARD | マチスの秘策でうらにしてベンチに出したカードの、うらのあいだの名前・HP・タイプ・ワザなど（「たねポケモン」としてあつかわれる以外の項目）を… | FD1（v0.67）・FD2（v0.67） | 2 |
| UQ-BUZZAP-TARGET-AND-COLOR | マルマインの［エネエネ］で、相手の場のポケモンにつけられるか、「好きな色」に無色・悪・鋼を選べるか | BZ1（v0.59）・BZ3（v0.59） | 2 |
| UQ-SCRAM-TIMING | タケシのオコリザルの［ずらかる］がはたらく時点（残りHPが「10」を通るとき・ワザの途中・同時に 2 匹）と、力が消えていたあいだに「10」… | SC1（v0.61）・SC2（v0.61） | 2 |
| UQ-DESTINY-BOND-KO | みちづれで相手の対戦ポケモンもきぜつするとき、同時のきぜつ（p.324）として扱うか（勝ち負けが決まる場合） | HC2（v0.31）・HC2（v0.61） | 1 |
| UQ-RETURN-TO-DECK-KO-ORDER | ワザで自分を山札にもどし（バトル場が空き）、同じワザで相手の対戦ポケモンがきぜつするとき、ワザを使ったプレイヤーがバトル場に出す時点と、きぜ… | RD9（v0.36） | 1 |
| UQ-OPPONENT-POKEMON-COUNTERS | ルージュラの「ヨガのポーズ」の「相手のポケモンにのっているダメージカウンター」が、相手の対戦ポケモンだけか、相手の場のポケモンすべてか | CD4（v0.32） | 1 |
| UQ-BENCH-DAMAGE-WEAKNESS-RESISTANCE | 控えポケモンへのダメージで、説明に「弱点・抵抗力に関係なく」と書かれていないとき、弱点・抵抗力を計算するか | JS1（v0.37） | 1 |
| UQ-REDUCED-DAMAGE-BENCH-TARGET | カラカラの「なきつく」の「このカードにワザを使う時」のダメージを減らす効果が、カラカラが控えにいて控えへのダメージを受けるときにもはたらくか | NK5（v0.34） | 1 |
| UQ-MISTY-SELF-DAMAGE | トレーナーのカスミの「対戦ポケモンにダメージを与える時」の + 20 が、ワザを使うポケモン自身へのダメージにもはたらくか | MS1（v0.56） | 1 |
| UQ-CHARITY-BELOW-ZERO | お上品攻撃の「好きなだけ小さく」で、5 段階のダメージを 0 より小さくできるか | CA1（v0.66） | 1 |
| UQ-SPEED-STAR-SCOPE | タケシのサンドパンの「スピードスター」が除く「効果」に、相手の場のほかのポケモンの特殊能力が含まれるか | SS1（v0.60） | 1 |
| UQ-EXTRA-ENERGY-COLORLESS | 「ワザに必要なエネルギーよりも多く「水」エネルギーがついている時」の多いエネルギーの数を、無色のぶんを水で払ったとして数えるか | HC4（v0.31） | 1 |
| UQ-CALMING-AROMA-RETALIATION | エリカのフシギソウの［くつろぐかおり］が、返す効果（ほのおのかべ・こうらがえしなど）のダメージを半分にするか | CP1（v0.46） | 1 |
| UQ-SINKHOLE-TIMING | わるいダグトリオの［おとしあな］が、「にげる」の手順のどの時点ではたらくか（こんらんで失敗したとき・バトル場とベンチで受けるダメージが違うと… | SH1（v0.61） | 1 |
| UQ-DAMAGE-TRIGGER-TIMING | ダメージ → ダメージ以外の効果 → ダメージの順のワザで、「ダメージを受けたとき」にはたらく効果をどの時点で処理するか | GK1（v0.38） | 1 |
| UQ-ENTRY-POWER-DURING-ATTACK | ワザの効果で山札から重ねた（進化させた）カードの「場に出た時」の特殊能力を、ワザの最中に使えるか | PW4（v0.43） | 1 |
| UQ-GOOP-GAS-NEW-POKEMON | まきちらせ!ベトベトガスの効果がはたらく間に場に出した・進化させた・退化させたポケモンの特殊能力も消えるか | GG1（v0.59） | 1 |
| UQ-SHIFT-COLOR-DURATION | モルフォンの［へんしょく］で変えた色が、使った番のあと・ベンチにもどったあと・力が消えているあいだも続くか | VS1（v0.48） | 1 |
| UQ-CHANGE-ABSENT-WEAKNESS-RESISTANCE | 弱点・抵抗力のないポケモンの弱点・抵抗力を「好きな色にかえる」と、新しく持たせるのか | PG1（v0.48） | 1 |
| UQ-ATTACH-BLOCK-SCOPE | カスミのメノクラゲの「クリスタルビーム」を受けたポケモンを、場のエネルギーのつけかえの移動先・［エネエネ］のつける先に選べるか | CB1（v0.59） | 1 |
| UQ-ATTACK-LOCK-SOURCE-RETURNED | サカキのニドキングの「すごむ」の効果を与えたポケモンが、同じ番に突風などでバトル場にもどったとき、効果がどうなるか | SG1（v0.40） | 1 |
| UQ-BLAINE-SECOND-ATTACH | トレーナーのカツラの効果がはたらく番に、手札からエネルギーをつける通常の操作をもう一度できるか | BL1（v0.59） | 1 |
| UQ-EVOLUTION-PERMISSION-FROM-DECK | トレーナーのサカキの許可で制限が外れたポケモンを、山札から重ねる効果（ワザ・特殊能力）で進化させられるか | GV1（v0.44）・GV1（v0.45） | 1 |
| UQ-ENERGY-BURN-TRANSFER | リザードンの［エナジーバーン］で「炎」になった草エネルギーカードを、フシギバナの［エナジートランス］（「草」エネルギーをつけかえる）でつけか… | HC10（v0.31） | 1 |
| UQ-COUNTER-TRANSFER-PROTECTED | ダメージカウンターを相手にうつす効果（ダメージシフト・チェンジダメージ）で、相手がその効果を受けない状態のとき、どうなるか | CX1（v0.41） | 1 |
| UQ-FUCHSIA-GYM-ONCE-PER-TURN | セキチクシティジムの「自分の番ごとに1回」を、プレイヤーで数えるか、スタジアムのカードで数えるか（入れかわった別のカードでもう一度使えるか） | FG1（v0.57） | 1 |
| UQ-CHAOS-GYM-BORROWED-TURN | 錯乱ジムで相手プレイヤーがかわりに使ったトレーナーの説明が「あなたの番」などを書くとき、どの番を指すか・使えるか | CH1（v0.57） | 1 |
| UQ-DISCARD-ENERGY-TIMING-CONFUSION | 「はがしてすてる」ワザをこんらん状態で使い「うら」が出たとき、エネルギーをトラッシュするか（トラッシュが使うための条件か、ワザの効果か） | HC1（v0.31） | 1 |

- 既存の論点に結んだもの: HC3（v0.31）→ UQ-COIN-IN-NULLIFIED-ELEMENT、TS1（v0.60）→ UQ-TRANSPARENCY-COIN-ORDER、MH1（v0.48）・DV1（v0.50）→ UQ-EVOLUTION-HP-BELOW-DAMAGE、C18（v0.61）→ UQ-COUNTERATTACK-DOUBLE-KO、Z9（v0.61）→ UQ-POWER-DAMAGE-WEAKNESS-RESISTANCE、DR8・DR13（v0.68）→ UQ-ENERGY-DRAIN-ATTACKER-KO・UQ-ENERGY-DRAIN-NO-ENERGY、DR18・DR19（v0.68）→ UQ-MULTIPLE-DAMAGE-TRIGGERS-ONE-ATTACK。
- エンジンの未解決の一覧（`engine_unresolved_index`）: 156 件（v0.26〜v0.68 で 124 件を加えた）。エンジンが数える未解決の裁定は v0.68 まで 151 件・停止コード 149 件で、エンジンの研究の対応表の数と同じ。kyuura の論点は 71 件で、別の数（そろえていない）。数えない項目 5 件（DR1・DR6 と、今の対応カードでは起こらないコードのない問い FL0・BG0・ES0）。
- 既存の項目のうち、コードのない問いとして取り込んだあとでエンジンが停止コードを付けた 8 件（T27・C34/C35・G40・P19・P32 は v0.31、Z9 は v0.61、DR8・DR13 は v0.68）は、`stop_code_since` に版を書き、過去の版の数（`unresolved_counts(ctx, as_of=…)`）が変わらないようにした。DR8・DR13 は `counted_from_version: v0.68`。

### 3.3 エンジンの採用した仕様・簡略化・実装の事項（裁定と分けた）

`engine_positions`（公式の裁定ではないので `status` を持たない）。

- **ENG-V068-ENERGY-DRAIN-ADOPTED-SPEC（キョウのベトベトンの［だつりょくえき］）**: エンジンの採用した仕様（自動的にはたらく・ダメージのあと、ダメージ以外の効果の前）。2000.02.14 版の基準では DR1・DR6 は未解決のまま（UQ-ENERGY-DRAIN-DECLARATION・UQ-ENERGY-DRAIN-TIMING）。エンジンが挙げた MIX-POWER-ERRATA・MIX-POWER-SPLIT は 2002 年の記録で、2000.02.14 版の直接の裁定として読み替えない。DR8・DR13 は既存の論点、DR18・DR19 は UQ-MULTIPLE-DAMAGE-TRIGGERS-ONE-ATTACK。DR2・DR4・DR5・DR9・DR15・DR17・DR3・DR7・DR10・DR16 は v0.17c の取り込みの既存の裁定（`CR-ENERGY-DRAIN-*` など）の当てはめ。
- **ENG-V068-IMAKUNI-DODUO-SIMPLIFIED（イマクニ？のドードー）**: 「ハモる」はすぐにふつうの 30 ダメージ、［にげまくり］は物理的にカードを投げる処理を省いてふつうの「にげる」。エンジンの簡略化で、エラッタ・最新の説明ではない。kyuura のカードデータは印刷の文面のまま。
- **ENG-V068-SECRET-MANEUVER-IDENTITY（マチスの秘策）**: v0.67 の、見えないデッキの中身で受け付けるかが変わる不具合（v0.68 で修正）と、相手のうらのカードを 2 枚以上指定するコマンドを受け付けない制限は、エンジンの実装の事項で、公式の未解決の裁定ではない。FD1・FD2（うらのカードの項目、爆発ジムとの関係）は UQ-FACE-DOWN-CARD。

### 3.4 照合の記録・最新の説明の取り込み

エンジン v0.27（ストライク）・v0.28（10 枚）の『オフィシャルブック2000』の照合の記録（`card_verification.json`。原典の確認 2026-10-15、エンジン）を、照合の記録 11 件・最新の説明 6 件として取り込んだ（`import_provenance`。取り込み 2026-10-19。kyuura は読み直していない）。P43 のページの記録を 11 件加えた。

- 照合の記録: CC-PMCG2-017-P56・CC-PMCG1-026-P112・CC-PMCG1-045-P164・CC-PMCG1-068-P235・CC-PMCG2-006-P49・CC-PMCG2-018-P58・CC-PMCG2-021-P108・CC-PMCG2-022-P109・CC-PMCG2-035-P225・CC-PMCG3-012-P103・CC-PMCG3-022-P116。
- 最新の説明: LD-PMCG2-017-ATK0（つるぎのまい。「2倍」と「「60」になる」。印刷だけでは処理が決まらない）・LD-PMCG1-026-ATK0・LD-PMCG2-006-ATK1・LD-PMCG1-068-ATK0・LD-PMCG3-012-ATK1・LD-PMCG3-022-ATK0（図版の読み「エネルギーカード」は kyuura の文面と違うが、読み取りの確度が低く版も確かめていないので、転記の誤りとは断定しない）。
- タマタマのワザ名（やどりぎのタネ／たね）はデータの誤りの候補（`data_error`）にした（フシギソウの「つるのムチ」と同じ扱い）。
- `card_sources.json`（kyuura データの採用の記録、pcg-search.com との比較）は、原典の照合（CC-）として取り込んでいない。同じサイトのデータどうしの比較は、独立した照合に数えない。

### 3.5 取り込まなかったもの（理由）

- 表の行 262 件（3.1。行ごとの理由は `not_imported`）。
- `card_sources.json` の採用の記録（v0.29〜v0.68 の多くのカード）と pcg-search.com との比較: 原典の照合ではない（3.4）。違いのうち kyuura のデータの訂正の候補は、`data/curation/card_corrections.json` の `candidates`（`held_transcription_difference` など）に理由つきで残した。
- エンジンの未対応のコード（`UNSUPPORTED_…`。秘策の組の上限・先読みの上限など）・テストの数・対戦の数: 実装の事項で、論点にしない。
- id のない表の行・本文の記述: 読んだが、行単位では取り込んでいない（必要な事項は該当の論点・`engine_positions` に書いた）。

## 4. カードデータの訂正

`data/curation/card_corrections.json`。訂正は生成のたびに当てはめ、当てはめる前の値が `before` でなければ止まる（作り直しても訂正は残る）。

| id | カード・欄 | 前 → 後 | 根拠 | 状態 |
|---|---|---|---|---|
| FIX-PMCG2-046-ATK0-TEXT | ガルーラ・こどものおつかいの説明 | 「コインを投げて「おもて」なら、自分の山札の…」→「自分の山札の上からカードを1枚ひいて、手札に加える。」 | 利用者が実物のカード（LV.40・HP90）の画像を示し、なぞのばしょの記載の誤りと明示した（承認済み）。kyuura は画像を見ていない（利用者の環境の画像のパスは記録したが、この環境にはない）。エラッタ・再録の変更ではない。CC・LD・資料のページ・修正のコミットは作っていない | 今回直した |
| FIX-GD6-010-ATK1-DAMAGE | ナツメのスリーパー（GD6-010）・ワザ 2 のダメージ | 「20」→「20×」 | kyuura の既存の判定（`other_products.json` の `reprint_checks`。pcg-search のカードの画像。**確実**）。同じカードの PMCG6-051 も「20×」 | 今回直した |
| FIX-SI-010-ATK1-NAME | ベロリンガ（SI-010）・ワザ 2 の名前 | 「のびるべ口」→「のびるベロ」 | kyuura の既存の判定（サザンアイランドの 2 つの転記の突き合わせ） | 今回直した |
| FIX-PMCG2-041-ATK0-NAME・FIX-PMCG2-041-LEVEL | ベロリンガ（PMCG2-041） | したでなめる → まきつくベロ、LV.29 → 26 | CC-PMCG2-041-P234（前の作業。f52a8e2） | 反映済み（重複して直さない・もどさない） |

- エンジン v0.68 の `USER_PROVIDED_CORRECTIONS`（PMCG2-046 の同じ欄・同じ前後）とは同じ内容。エンジンの補正は変えていない（[エンジンへの引き継ぎ](engine-handover-v0.68.md)）。
- 訂正しなかった候補 97 件: 別の転記（pcg-search.com）との違い 87（エンジンの `card_sources.json` の照合の違い。どれもエンジンの判定では処理に影響しない）、印刷の版が決まらない 6（フシギソウ・ケーシィ・ポニータ・ドードー・突風・タマタマ）、値の欠け 2（タケシのイワークのシリーズ・無色2個エネルギーの効果文）、版の違い 1（エネルギー回収）、誤りの可能性が高いが印刷で確かめていない 1（わるいカメックスのハイドロキャノンの「エネルギーがいている時」）。ラプラスの図版の読みは別の転記との違い（読み取りの確度が低い）。
- 照合の記録が照合した値と今の値が訂正で変わった場合は、照合の記録を書きかえず、訂正の記録の `card_checks_affected` で確かめる（`scripts/build_card_rulings.py`）。今回の訂正で照合の記録の写しが変わったものはない。

## 5. 検証

実行した検査（最終のコードで実行。結果は作業の報告に書いた）:

- `python3 scripts/build_card_rulings.py --check`、`python3 scripts/build_rule_history.py --check`、`python3 scripts/build_rule_differences.py --check`、`python3 scripts/build_other_products.py --check`、`python3 scripts/build_engine_targets.py --check`
- `python3 scripts/build_cardlist.py --jp … --en … --species … --check`（記録した固定の版の外部の入力。20 ファイルが今のファイルと同じ）
- `python3 -m unittest discover -s tests`（`tests/test_non_pack_engine_v068.py` を加えた: id と元の項目の追跡、ページと記録の 1 対 1、番号違いのまとめが番号以外同じこと、名前だけでまとめないこと、JSON と CSV の一致、進化元の出どころ、にげるの読み、訂正の再生成と不正な値の拒否、照合の記録と訂正の履歴、実装の対象の数と登録の区別、取り込みの漏れ・二重の対応・分類の誤りの検出、採用した仕様を裁定にしないこと）。v0.5〜v0.25 の取り込みの検査は、その版の時点の数（`as_of`）で確かめるようにした（検査の条件は緩めていない）。拡張パックの 780 件の変化は、訂正の記録の欄と形式 3 の欄だけであることを、v0.13 の取り込みのコミット（bcf38c7）と比べて確かめる。
- `python3 scripts/research_stats.py`（数の写し）
- `python3 scripts/pcg_search.py extract-pages --cache … --urls … --checked-on 2026-10-19`（2026-10-19 に読み直してキャッシュした 187 ページから作り直し、`data/pcgsearch_page_checks.json` と同じ）

実行していない検査: エンジンの全体のテスト・対戦の比較・性能の測定・勝率の評価（依頼の範囲の外）。pcg-search の全 681 ページの取り直し。原典の画像の読み直し。

## 6. 残っている不足

- 拡張パック以外の商品のレベル（423）・図鑑番号（227）・進化元（9）・段階（2）・無色2個エネルギーの効果文（8）。
- pcg-search の一覧にない商品・配布物の調査。
- 未解決の論点 71 件（当時の Q&A・大会の裁定・雑誌の記事は探していない）。
- 訂正の候補 97 件（印刷の版の画像・別の資料が要る）。
