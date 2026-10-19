# ポケモンジム（構築済みデッキ）

<!-- このファイルは scripts/build_other_products.py が data/ja_text_pcgsearch.json と data/curation/other_products.json から生成しています。直接編集しないでください。 -->

[拡張パック以外の商品の一覧](../other-products.md) ／ 出典の記号: [出典と確認状況](../../sources.md)

- カードの欄（名前・HP・ワザなど）は、ポケモンカード 旧シリーズ検索（pcg-search.com）[N3] の転記です。カード名から各カードのページにリンクしています。
- 「番号」は pcg-search の並び順で、カードに印刷された番号ではありません。
- 「ほかの収録」は、名前（ポケモンは HP・特殊能力名・ワザ名も）が同じカードが入っているほかの商品です（拡張パック 10 弾と、このページ群の商品）。
- 「id」は `data/cards.json` のカードの id（商品の記号とカードページ名の末尾 3 桁。[data/product_items.json](../../../data/product_items.json) にページとの対応）。「→」は番号だけが違うページを、代表のページの記録にまとめたもの。「対象外」は通常の対戦のデッキに入れるカードではない項目（`data/product_items.json` の non_game_items）。

## 概要

- ジムリーダーとその「〇〇の」ポケモンを使う構築済みデッキで、日本だけで 6 種類出ました [X46]。**確実**
- 各デッキは 64 枚で、60 枚のデッキと、入れ替えて使う「拡張カード」4 枚。ほかにコイン、ルールブック、「ポケモンジムガイド」などが入っていました [X46]。**確実**
- 拡張パック「リーダーズスタジアム」（1998-10-24）・「闇からの挑戦」（1999-06-25）に先立って出ており、デッキのカードの一部はその後の拡張パックにも収録されました。
- 英語版では、デッキにしかなかったカードは Gym Heroes・Gym Challenge に入れられ、デッキの中身は英語版のテーマデッキ（Brock、Misty など）の元になりました [X46]。**確実**
  - デッキで決まったレアリティのまま英語版のセットに入ったため、Gym Heroes にはタケシのイワークなどの「コモンなのにレア」のカードがあります [X46]。**有力**

| デッキ | 発売日 | 枚数 | カードの種類 | デッキで初めて出たカード | 英語版のテーマデッキ |
|---|---|---|---|---|---|
| ポケモンジム第1弾「ニビシティジム タケシ」 | 1998-04-26 | 64 | 25（基本エネルギーを除く） | 16 | Brock |
| ポケモンジム第1弾「ハナダシティジム カスミ」 | 1998-04-26 | 64 | 24（基本エネルギーを除く） | 18 | Misty |
| ポケモンジム第2弾「クチバシティジム マチス」 | 1998-07-25 | 64 | 25（基本エネルギーを除く） | 17 | Lt. Surge |
| ポケモンジム第2弾「タマムシシティジム エリカ」 | 1998-07-25 | 64 | 28（基本エネルギーを除く） | 18 | Erika |
| ポケモンジム第3弾「グレンタウンジム カツラ」 | 1999-02-26 | 64 | 25（基本エネルギーを除く） | 18 | Blaine |
| ポケモンジム第3弾「ヤマブキシティジム ナツメ」 | 1999-02-26 | 64 | 26（基本エネルギーを除く） | 17 | Sabrina |

- 発売日・枚数・デッキリストは Bulbapedia [X46] によります。カードの欄は pcg-search [N3]。
- デッキの各カードが英語版のどのカードになったかは、Bulbapedia のデッキのカードのページ（英語版のカードへの転送）と、カードの数値・ワザの照合の両方で確かめ、全カード一致しました。**確実**

## ポケモンジム第1弾「ニビシティジム タケシ」

発売日 1998-04-26。

| 番号 | id | カード名 | 種類 | タイプ | HP | レア | 枚数 | 英語版 | ほかの収録 |
|---|---|---|---|---|---|---|---|---|---|
| 001/025 | `GD1-001` | [タケシのズバット](https://pcg-search.com/card/1st/1stgymd1001.php) | たね | 草 | 30 |  | 1 | Gym Heroes 24（Brock's Zubat） |  |
| 002/025 | `GD1-002` | [タケシのロコン](https://pcg-search.com/card/1st/1stgymd1002.php) | たね | 炎 | 40 |  | 1 | Gym Heroes 73（Brock's Vulpix） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 003/025 | `GD1-003` | [タケシのサンド](https://pcg-search.com/card/1st/1stgymd1003.php) | たね | 闘 | 40 |  | 2 | Gym Heroes 71（Brock's Sandshrew） |  |
| 004/025 | `GD1-004` | [タケシのサンドパン](https://pcg-search.com/card/1st/1stgymd1004.php) | 1進化 | 闘 | 60 |  | 1 | Gym Heroes 23（Brock's Sandslash） |  |
| 005/025 | `GD1-005` | [タケシのマンキー](https://pcg-search.com/card/1st/1stgymd1005.php) | たね | 闘 | 40 |  | 2 | Gym Heroes 67（Brock's Mankey） |  |
| 006/025 | `GD1-006` | [タケシのイシツブテ](https://pcg-search.com/card/1st/1stgymd1006.php) | たね | 闘 | 40 |  | 2 | Gym Heroes 66（Brock's Geodude） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 007/025 | `GD1-007` | [タケシのイシツブテ](https://pcg-search.com/card/1st/1stgymd1007.php) | たね | 闘 | 50 |  | 2 | Gym Heroes 38（Brock's Geodude） |  |
| 008/025 | `GD1-008` | [タケシのゴローン](https://pcg-search.com/card/1st/1stgymd1008.php) | 1進化 | 闘 | 70 |  | 2 | Gym Heroes 40（Brock's Graveler） |  |
| 009/025 | `GD1-009` | [タケシのゴローニャ](https://pcg-search.com/card/1st/1stgymd1009.php) | 2進化 | 闘 | 90 |  | 1 | Gym Heroes 20（Brock's Golem） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 010/025 | `GD1-010` | [タケシのイワーク](https://pcg-search.com/card/1st/1stgymd1010.php) | たね | 闘 | 70 |  | 2 | Gym Heroes 21（Brock's Onix） |  |
| 011/025 | `GD1-011` | [タケシのイワーク](https://pcg-search.com/card/1st/1stgymd1011.php) | たね | 闘 | 100 |  | 2 | Gym Heroes 69（Brock's Onix） | プロモ（1998-02-15）<br>第5弾 リーダーズスタジアム（1998-10-24） |
| 012/025 | `GD1-012` | [タケシのサイホーン](https://pcg-search.com/card/1st/1stgymd1012.php) | たね | 闘 | 60 |  | 2 | Gym Heroes 22（Brock's Rhyhorn） |  |
| 013/025 | `GD1-013` | [タケシのサイドン](https://pcg-search.com/card/1st/1stgymd1013.php) | 1進化 | 闘 | 80 | -(キラ) | 1 | Gym Heroes 2（Brock's Rhydon） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 014/025 | `GD1-014` | [エネルギー回収](https://pcg-search.com/card/1st/1stgymd1014.php) | トレーナー |  |  |  | 1 | Base Set 81（Energy Retrieval） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26） |
| 015/025 | `GD1-015` | [思い出させる](https://pcg-search.com/card/1st/1stgymd1015.php) | トレーナー |  |  |  | 1 | Gym Heroes 116（Recall） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 016/025 | `GD1-016` | [きずぐすり](https://pcg-search.com/card/1st/1stgymd1016.php) | トレーナー |  |  |  | 1 | Base Set 94（Potion） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 017/025 | `GD1-017` | [元気のかけら](https://pcg-search.com/card/1st/1stgymd1017.php) | トレーナー |  |  |  | 1 | Base Set 89（Revive） | 第1弾 拡張パック（1996-10-20） |
| 018/025 | `GD1-018` | [タケシ](https://pcg-search.com/card/1st/1stgymd1018.php) | トレーナー |  |  | -(キラ) | 1 | Gym Heroes 15（Brock） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 019/025 | `GD1-019` | [タケシの育て方](https://pcg-search.com/card/1st/1stgymd1019.php) | トレーナー |  |  |  | 1 | Gym Heroes 106（Brock's Training Method） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 020/025 | `GD1-020` | [なんでもなおし](https://pcg-search.com/card/1st/1stgymd1020.php) | トレーナー |  |  |  | 1 | Base Set 82（Full Heal） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 021/025 | `GD1-021` | [ポケモンいれかえ](https://pcg-search.com/card/1st/1stgymd1021.php) | トレーナー |  |  |  | 2 | Base Set 95（Switch） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキの拡張カード）（2001-04-06） |
| 022/025 | `GD1-022` | [ポケモン図鑑HANDY505](https://pcg-search.com/card/1st/1stgymd1022.php) | トレーナー |  |  |  | 1 | Base Set 87（Pokédex） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26） |
| 023/025 | `GD1-023` | [ポケモンセンター](https://pcg-search.com/card/1st/1stgymd1023.php) | トレーナー |  |  |  | 1 | Base Set 85（Pokémon Center） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26） |
| 024/025 | `GD1-024` | [ニビシティジム](https://pcg-search.com/card/1st/1stgymd1024.php) | スタジアム |  |  |  | 1 | Gym Heroes 115（Pewter City Gym） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 025/025 | `GD1-025` | [無色2個エネルギー](https://pcg-search.com/card/1st/1stgymd1025.php) | 特殊エネルギー |  |  |  | 1 | Base Set 96（Double Colorless Energy） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30） |

基本エネルギー: Fire Energy 2 枚、Fighting Energy 28 枚

## ポケモンジム第1弾「ハナダシティジム カスミ」

発売日 1998-04-26。

| 番号 | id | カード名 | 種類 | タイプ | HP | レア | 枚数 | 英語版 | ほかの収録 |
|---|---|---|---|---|---|---|---|---|---|
| 001/024 | `GD2-001` | [カスミのコダック](https://pcg-search.com/card/1st/1stgymd2001.php) | たね | 水 | 50 |  | 1 | Gym Heroes 54（Misty's Psyduck） |  |
| 002/024 | `GD2-002` | [カスミのニョロモ](https://pcg-search.com/card/1st/1stgymd2002.php) | たね | 水 | 50 |  | 2 | Gym Heroes 87（Misty's Poliwag） |  |
| 003/024 | `GD2-003` | [カスミのメノクラゲ](https://pcg-search.com/card/1st/1stgymd2003.php) | たね | 水 | 40 |  | 2 | Gym Heroes 32（Misty's Tentacool） |  |
| 004/024 | `GD2-004` | [カスミのドククラゲ](https://pcg-search.com/card/1st/1stgymd2004.php) | 1進化 | 水 | 70 | -(キラ) | 1 | Gym Heroes 10（Misty's Tentacruel） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 005/024 | `GD2-005` | [カスミのパウワウ](https://pcg-search.com/card/1st/1stgymd2005.php) | たね | 水 | 60 |  | 1 | Gym Heroes 88（Misty's Seel） |  |
| 006/024 | `GD2-006` | [カスミのシェルダー](https://pcg-search.com/card/1st/1stgymd2006.php) | たね | 水 | 40 |  | 2 | Gym Heroes 89（Misty's Shellder） |  |
| 007/024 | `GD2-007` | [カスミのパルシェン](https://pcg-search.com/card/1st/1stgymd2007.php) | 1進化 | 水 | 70 |  | 2 | Gym Heroes 29（Misty's Cloyster） |  |
| 008/024 | `GD2-008` | [カスミのタッツー](https://pcg-search.com/card/1st/1stgymd2008.php) | たね | 水 | 40 |  | 2 | Gym Heroes 86（Misty's Horsea） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 009/024 | `GD2-009` | [カスミのトサキント](https://pcg-search.com/card/1st/1stgymd2009.php) | たね | 水 | 30 |  | 2 | Gym Heroes 30（Misty's Goldeen） |  |
| 010/024 | `GD2-010` | [カスミのトサキント](https://pcg-search.com/card/1st/1stgymd2010.php) | たね | 水 | 40 |  | 2 | Gym Heroes 85（Misty's Goldeen） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 011/024 | `GD2-011` | [カスミのアズマオウ](https://pcg-search.com/card/1st/1stgymd2011.php) | 1進化 | 水 | 70 |  | 2 | Gym Heroes 55（Misty's Seaking） |  |
| 012/024 | `GD2-012` | [カスミのヒトデマン](https://pcg-search.com/card/1st/1stgymd2012.php) | たね | 水 | 40 |  | 2 | Gym Challenge 92（Misty's Staryu） | プロモ（1998-02-15）<br>第5弾 リーダーズスタジアム（1998-10-24） |
| 013/024 | `GD2-013` | [カスミのヒトデマン](https://pcg-search.com/card/1st/1stgymd2013.php) | たね | 水 | 50 |  | 2 | Gym Heroes 90（Misty's Staryu） |  |
| 014/024 | `GD2-014` | [カスミのスターミー](https://pcg-search.com/card/1st/1stgymd2014.php) | 1進化 | 水 | 80 |  | 3 | Gym Heroes 56（Misty's Starmie） |  |
| 015/024 | `GD2-015` | [カスミ](https://pcg-search.com/card/1st/1stgymd2015.php) | トレーナー |  |  | -(キラ) | 1 | Gym Heroes 18（Misty） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 016/024 | `GD2-016` | [カスミのいかり](https://pcg-search.com/card/1st/1stgymd2016.php) | トレーナー |  |  |  | 1 | Gym Heroes 114（Misty's Wrath） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 017/024 | `GD2-017` | [カスミの勝負](https://pcg-search.com/card/1st/1stgymd2017.php) | トレーナー |  |  |  | 2 | Gym Heroes 123（Misty's Duel） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 018/024 | `GD2-018` | [カスミのなみだ](https://pcg-search.com/card/1st/1stgymd2018.php) | トレーナー |  |  |  | 2 | Gym Challenge 118（Misty's Tears） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 019/024 | `GD2-019` | [きずぐすり](https://pcg-search.com/card/1st/1stgymd2019.php) | トレーナー |  |  |  | 1 | Base Set 94（Potion） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 020/024 | `GD2-020` | [ディフェンダー](https://pcg-search.com/card/1st/1stgymd2020.php) | トレーナー |  |  |  | 1 | Base Set 80（Defender） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック★neo（ワニノコデッキの拡張カード）（2001-04-06） |
| 021/024 | `GD2-021` | [突風](https://pcg-search.com/card/1st/1stgymd2021.php) | トレーナー |  |  |  | 1 | Base Set 93（Gust of Wind） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック★neo（ワニノコデッキの拡張カード）（2001-04-06） |
| 022/024 | `GD2-022` | [モンスターボール](https://pcg-search.com/card/1st/1stgymd2022.php) | トレーナー |  |  |  | 1 | Jungle 64（Poké Ball） | 第2弾 ポケモンジャングル（1997-03-05）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25） |
| 023/024 | `GD2-023` | [ハナダシティジム](https://pcg-search.com/card/1st/1stgymd2023.php) | スタジアム |  |  |  | 1 | Gym Heroes 108（Cerulean City Gym） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 024/024 | `GD2-024` | [無色2個エネルギー](https://pcg-search.com/card/1st/1stgymd2024.php) | 特殊エネルギー |  |  |  | 1 | Base Set 96（Double Colorless Energy） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30） |

基本エネルギー: Water Energy 26 枚

## ポケモンジム第2弾「クチバシティジム マチス」

発売日 1998-07-25。

| 番号 | id | カード名 | 種類 | タイプ | HP | レア | 枚数 | 英語版 | ほかの収録 |
|---|---|---|---|---|---|---|---|---|---|
| 001/025 | `GD3-001` | [マチスのピカチュウ](https://pcg-search.com/card/1st/1stgymd3001.php) | たね | 雷 | 40 |  | 2 | Gym Challenge 84（Lt. Surge's Pikachu） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 002/025 | `GD3-002` | [マチスのピカチュウ](https://pcg-search.com/card/1st/1stgymd3002.php) | たね | 雷 | 50 |  | 2 | Gym Heroes 81（Lt. Surge's Pikachu） |  |
| 003/025 | `GD3-003` | [マチスのライチュウ](https://pcg-search.com/card/1st/1stgymd3003.php) | 1進化 | 雷 | 70 |  | 2 | Gym Heroes 28（Lt. Surge's Raichu） |  |
| 004/025 | `GD3-004` | [マチスのコイル](https://pcg-search.com/card/1st/1stgymd3004.php) | たね | 雷 | 30 |  | 1 | Gym Heroes 50（Lt. Surge's Magnemite） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 005/025 | `GD3-005` | [マチスのコイル](https://pcg-search.com/card/1st/1stgymd3005.php) | たね | 雷 | 40 |  | 2 | Gym Heroes 80（Lt. Surge's Magnemite） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 006/025 | `GD3-006` | [マチスのレアコイル](https://pcg-search.com/card/1st/1stgymd3006.php) | 1進化 | 雷 | 70 | -(キラ) | 1 | Gym Heroes 8（Lt. Surge's Magneton） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 007/025 | `GD3-007` | [マチスのビリリダマ](https://pcg-search.com/card/1st/1stgymd3007.php) | たね | 雷 | 40 |  | 2 | Gym Heroes 84（Lt. Surge's Voltorb） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 008/025 | `GD3-008` | [マチスのビリリダマ](https://pcg-search.com/card/1st/1stgymd3008.php) | たね | 雷 | 50 |  | 2 | Gym Challenge 86（Lt. Surge's Voltorb） |  |
| 009/025 | `GD3-009` | [マチスのマルマイン](https://pcg-search.com/card/1st/1stgymd3009.php) | 1進化 | 雷 | 70 |  | 2 | Gym Challenge 52（Lt. Surge's Electrode） |  |
| 010/025 | `GD3-010` | [マチスのエレブー](https://pcg-search.com/card/1st/1stgymd3010.php) | たね | 雷 | 60 |  | 2 | Gym Heroes 27（Lt. Surge's Electabuzz） | プロモ（1998-07-15） |
| 011/025 | `GD3-011` | [マチスのコラッタ](https://pcg-search.com/card/1st/1stgymd3011.php) | たね | 無 | 40 |  | 2 | Gym Heroes 82（Lt. Surge's Rattata） |  |
| 012/025 | `GD3-012` | [マチスのラッタ](https://pcg-search.com/card/1st/1stgymd3012.php) | 1進化 | 無 | 70 |  | 1 | Gym Heroes 51（Lt. Surge's Raticate） |  |
| 013/025 | `GD3-013` | [マチスのオニスズメ](https://pcg-search.com/card/1st/1stgymd3013.php) | たね | 無 | 30 |  | 2 | Gym Heroes 52（Lt. Surge's Spearow） |  |
| 014/025 | `GD3-014` | [いいきずぐすり](https://pcg-search.com/card/1st/1stgymd3014.php) | トレーナー |  |  |  | 1 | Base Set 90（Super Potion） | 第1弾 拡張パック（1996-10-20） |
| 015/025 | `GD3-015` | [エネルギーサーキュレート](https://pcg-search.com/card/1st/1stgymd3015.php) | トレーナー |  |  |  | 2 | Gym Heroes 122（Energy Flow） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 016/025 | `GD3-016` | [スパイ作戦](https://pcg-search.com/card/1st/1stgymd3016.php) | トレーナー |  |  |  | 2 | Gym Heroes 118（Secret Mission） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 017/025 | `GD3-017` | [ディフェンダー](https://pcg-search.com/card/1st/1stgymd3017.php) | トレーナー |  |  |  | 1 | Base Set 80（Defender） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック★neo（ワニノコデッキの拡張カード）（2001-04-06） |
| 018/025 | `GD3-018` | [突風](https://pcg-search.com/card/1st/1stgymd3018.php) | トレーナー |  |  |  | 1 | Base Set 93（Gust of Wind） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>クイックスターターギフト（1998-12-04）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック★neo（ワニノコデッキの拡張カード）（2001-04-06） |
| 019/025 | `GD3-019` | [なんでもなおし](https://pcg-search.com/card/1st/1stgymd3019.php) | トレーナー |  |  |  | 1 | Base Set 82（Full Heal） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 020/025 | `GD3-020` | [ポケモンいれかえ](https://pcg-search.com/card/1st/1stgymd3020.php) | トレーナー |  |  |  | 1 | Base Set 95（Switch） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキの拡張カード）（2001-04-06） |
| 021/025 | `GD3-021` | [マチス](https://pcg-search.com/card/1st/1stgymd3021.php) | トレーナー |  |  | -(キラ) | 1 | Gym Heroes 17（Lt. Surge） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 022/025 | `GD3-022` | [マチスの交渉](https://pcg-search.com/card/1st/1stgymd3022.php) | トレーナー |  |  |  | 1 | Gym Heroes 112（Lt. Surge's Treaty） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 023/025 | `GD3-023` | [モンスターボール](https://pcg-search.com/card/1st/1stgymd3023.php) | トレーナー |  |  |  | 2 | Jungle 64（Poké Ball） | 第2弾 ポケモンジャングル（1997-03-05）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26） |
| 024/025 | `GD3-024` | [クチバシティジム](https://pcg-search.com/card/1st/1stgymd3024.php) | スタジアム |  |  |  | 1 | Gym Heroes 120（Vermilion City Gym） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 025/025 | `GD3-025` | [無色2個エネルギー](https://pcg-search.com/card/1st/1stgymd3025.php) | 特殊エネルギー |  |  |  | 1 | Base Set 96（Double Colorless Energy） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30） |

基本エネルギー: Lightning Energy 26 枚

## ポケモンジム第2弾「タマムシシティジム エリカ」

発売日 1998-07-25。

| 番号 | id | カード名 | 種類 | タイプ | HP | レア | 枚数 | 英語版 | ほかの収録 |
|---|---|---|---|---|---|---|---|---|---|
| 001/028 | `GD4-001` | [エリカのナゾノクサ](https://pcg-search.com/card/1st/1stgymd4001.php) | たね | 草 | 40 |  | 2 | Gym Heroes 47（Erika's Oddish） |  |
| 002/028 | `GD4-002` | [エリカのナゾノクサ](https://pcg-search.com/card/1st/1stgymd4002.php) | たね | 草 | 50 |  | 2 | Gym Heroes 78（Erika's Oddish） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 003/028 | `GD4-003` | [エリカのクサイハナ](https://pcg-search.com/card/1st/1stgymd4003.php) | 1進化 | 草 | 70 |  | 2 | Gym Heroes 46（Erika's Gloom） |  |
| 004/028 | `GD4-004` | [エリカのラフレシア](https://pcg-search.com/card/1st/1stgymd4004.php) | 2進化 | 草 | 80 | -(キラ) | 1 | Gym Heroes 5（Erika's Vileplume） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 005/028 | `GD4-005` | [エリカのマダツボミ](https://pcg-search.com/card/1st/1stgymd4005.php) | たね | 草 | 40 |  | 2 | Gym Heroes 75（Erika's Bellsprout） |  |
| 006/028 | `GD4-006` | [エリカのマダツボミ](https://pcg-search.com/card/1st/1stgymd4006.php) | たね | 草 | 50 |  | 2 | Gym Heroes 76（Erika's Bellsprout） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 007/028 | `GD4-007` | [エリカのウツドン](https://pcg-search.com/card/1st/1stgymd4007.php) | 1進化 | 草 | 70 |  | 2 | Gym Heroes 49（Erika's Weepinbell） |  |
| 008/028 | `GD4-008` | [エリカのウツボット](https://pcg-search.com/card/1st/1stgymd4008.php) | 2進化 | 草 | 80 |  | 1 | Gym Heroes 26（Erika's Victreebel） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 009/028 | `GD4-009` | [エリカのタマタマ](https://pcg-search.com/card/1st/1stgymd4009.php) | たね | 草 | 40 |  | 2 | Gym Heroes 77（Erika's Exeggcute） |  |
| 010/028 | `GD4-010` | [エリカのナッシー](https://pcg-search.com/card/1st/1stgymd4010.php) | 1進化 | 草 | 70 |  | 1 | Gym Heroes 44（Erika's Exeggutor） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 011/028 | `GD4-011` | [エリカのモンジャラ](https://pcg-search.com/card/1st/1stgymd4011.php) | たね | 草 | 60 |  | 2 | Gym Heroes 79（Erika's Tangela） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 012/028 | `GD4-012` | [エリカのピッピ](https://pcg-search.com/card/1st/1stgymd4012.php) | たね | 無 | 50 |  | 2 | Gym Heroes 25（Erika's Clefairy） |  |
| 013/028 | `GD4-013` | [エリカのミニリュウ](https://pcg-search.com/card/1st/1stgymd4013.php) | たね | 無 | 40 |  | 1 | Gym Heroes 42（Erika's Dratini） | プロモ（1998-07-15）<br>第5弾 リーダーズスタジアム（1998-10-24） |
| 014/028 | `GD4-014` | [エネルギー回収](https://pcg-search.com/card/1st/1stgymd4014.php) | トレーナー |  |  |  | 1 | Base Set 81（Energy Retrieval） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26） |
| 015/028 | `GD4-015` | [エネルギー転送](https://pcg-search.com/card/1st/1stgymd4015.php) | トレーナー |  |  |  | 2 | Fossil 59（Energy Search） | 第3弾 化石の秘密（1997-06-21）<br>クイックスターターギフト（1998-12-04） |
| 016/028 | `GD4-016` | [エリカ](https://pcg-search.com/card/1st/1stgymd4016.php) | トレーナー |  |  | -(キラ) | 1 | Gym Heroes 16（Erika） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 017/028 | `GD4-017` | [エリカのお付き](https://pcg-search.com/card/1st/1stgymd4017.php) | トレーナー |  |  |  | 1 | Gym Heroes 109（Erika's Maids） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 018/028 | `GD4-018` | [エリカの香水](https://pcg-search.com/card/1st/1stgymd4018.php) | トレーナー |  |  |  | 1 | Gym Heroes 110（Erika's Perfume） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 019/028 | `GD4-019` | [お上品攻撃](https://pcg-search.com/card/1st/1stgymd4019.php) | トレーナー |  |  |  | 1 | Gym Heroes 99（Charity） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 020/028 | `GD4-020` | [きずぐすり](https://pcg-search.com/card/1st/1stgymd4020.php) | トレーナー |  |  |  | 1 | Base Set 94（Potion） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 021/028 | `GD4-021` | [ディフェンダー](https://pcg-search.com/card/1st/1stgymd4021.php) | トレーナー |  |  |  | 2 | Base Set 80（Defender） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック★neo（ワニノコデッキの拡張カード）（2001-04-06） |
| 022/028 | `GD4-022` | [なんでもなおし](https://pcg-search.com/card/1st/1stgymd4022.php) | トレーナー |  |  |  | 1 | Base Set 82（Full Heal） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 023/028 | `GD4-023` | [プラスパワー](https://pcg-search.com/card/1st/1stgymd4023.php) | トレーナー |  |  |  | 1 | Base Set 84（PlusPower） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック★neo（チコリータデッキの拡張カード）（2001-04-06） |
| 024/028 | `GD4-024` | [ポケモンいれかえ](https://pcg-search.com/card/1st/1stgymd4024.php) | トレーナー |  |  |  | 1 | Base Set 95（Switch） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキの拡張カード）（2001-04-06） |
| 025/028 | `GD4-025` | [リサイクル](https://pcg-search.com/card/1st/1stgymd4025.php) | トレーナー |  |  |  | 1 | Fossil 61（Recycle） | 第3弾 化石の秘密（1997-06-21） |
| 026/028 | `GD4-026` | [礼儀作法](https://pcg-search.com/card/1st/1stgymd4026.php) | トレーナー |  |  |  | 1 | Gym Heroes 111（Good Manners） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 027/028 | `GD4-027` | [タマムシシティジム](https://pcg-search.com/card/1st/1stgymd4027.php) | スタジアム |  |  |  | 1 | Gym Heroes 107（Celadon City Gym） | 第5弾 リーダーズスタジアム（1998-10-24） |
| 028/028 | `GD4-028` | [無色2個エネルギー](https://pcg-search.com/card/1st/1stgymd4028.php) | 特殊エネルギー |  |  |  | 1 | Base Set 96（Double Colorless Energy） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30） |

基本エネルギー: Grass Energy 20 枚、Psychic Energy 5 枚

## ポケモンジム第3弾「グレンタウンジム カツラ」

発売日 1999-02-26。

| 番号 | id | カード名 | 種類 | タイプ | HP | レア | 枚数 | 英語版 | ほかの収録 |
|---|---|---|---|---|---|---|---|---|---|
| 001/025 | `GD5-001` | [カツラのヒトカゲ](https://pcg-search.com/card/1st/1stgymd5001.php) | たね | 炎 | 50 |  | 2 | Gym Challenge 60（Blaine's Charmander） |  |
| 002/025 | `GD5-002` | [カツラのロコン](https://pcg-search.com/card/1st/1stgymd5002.php) | たね | 炎 | 40 |  | 2 | Gym Heroes 65（Blaine's Vulpix） | 第6弾 闇からの挑戦（1999-06-25） |
| 003/025 | `GD5-003` | [カツラのロコン](https://pcg-search.com/card/1st/1stgymd5003.php) | たね | 炎 | 50 |  | 1 | Gym Challenge 66（Blaine's Vulpix） |  |
| 004/025 | `GD5-004` | [カツラのキュウコン](https://pcg-search.com/card/1st/1stgymd5004.php) | 1進化 | 炎 | 60 |  | 1 | Gym Challenge 21（Blaine's Ninetales） | 第6弾 闇からの挑戦（1999-06-25） |
| 005/025 | `GD5-005` | [カツラのガーディ](https://pcg-search.com/card/1st/1stgymd5005.php) | たね | 炎 | 50 |  | 2 | Gym Heroes 35（Blaine's Growlithe） | プロモ（1999-02-15） |
| 006/025 | `GD5-006` | [カツラのガーディ](https://pcg-search.com/card/1st/1stgymd5006.php) | たね | 炎 | 60 |  | 2 | Gym Challenge 62（Blaine's Growlithe） |  |
| 007/025 | `GD5-007` | [カツラのウィンディ](https://pcg-search.com/card/1st/1stgymd5007.php) | 1進化 | 炎 | 90 | -(キラ) | 1 | Gym Challenge 1（Blaine's Arcanine） | 第6弾 闇からの挑戦（1999-06-25） |
| 008/025 | `GD5-008` | [カツラのポニータ](https://pcg-search.com/card/1st/1stgymd5008.php) | たね | 炎 | 40 |  | 2 | Gym Heroes 63（Blaine's Ponyta） |  |
| 009/025 | `GD5-009` | [カツラのポニータ](https://pcg-search.com/card/1st/1stgymd5009.php) | たね | 炎 | 50 |  | 2 | Gym Challenge 64（Blaine's Ponyta） | 第6弾 闇からの挑戦（1999-06-25） |
| 010/025 | `GD5-010` | [カツラのギャロップ](https://pcg-search.com/card/1st/1stgymd5010.php) | 1進化 | 炎 | 70 |  | 2 | Gym Challenge 33（Blaine's Rapidash） | 第6弾 闇からの挑戦（1999-06-25） |
| 011/025 | `GD5-011` | [カツラのブーバー](https://pcg-search.com/card/1st/1stgymd5011.php) | たね | 炎 | 60 |  | 2 | Gym Heroes 37（Blaine's Magmar） | 第6弾 闇からの挑戦（1999-06-25） |
| 012/025 | `GD5-012` | [カツラのドードー](https://pcg-search.com/card/1st/1stgymd5012.php) | たね | 無 | 50 |  | 2 | Gym Challenge 61（Blaine's Doduo） | 第6弾 闇からの挑戦（1999-06-25） |
| 013/025 | `GD5-013` | [カツラのドードリオ](https://pcg-search.com/card/1st/1stgymd5013.php) | 1進化 | 無 | 70 |  | 1 | Gym Challenge 32（Blaine's Dodrio） |  |
| 014/025 | `GD5-014` | [カツラ](https://pcg-search.com/card/1st/1stgymd5014.php) | トレーナー |  |  | -(キラ) | 1 | Gym Challenge 17（Blaine） | 第6弾 闇からの挑戦（1999-06-25） |
| 015/025 | `GD5-015` | [カツラのギャンブル](https://pcg-search.com/card/1st/1stgymd5015.php) | トレーナー |  |  |  | 2 | Gym Heroes 121（Blaine's Gamble） | 第6弾 闇からの挑戦（1999-06-25） |
| 016/025 | `GD5-016` | [カツラのクイズ その1](https://pcg-search.com/card/1st/1stgymd5016.php) | トレーナー |  |  |  | 2 | Gym Heroes 97（Blaine's Quiz 1） |  |
| 017/025 | `GD5-017` | [カツラのクイズ その2](https://pcg-search.com/card/1st/1stgymd5017.php) | トレーナー |  |  |  | 1 | Gym Challenge 111（Blaine's Quiz 2） |  |
| 018/025 | `GD5-018` | [きずぐすり](https://pcg-search.com/card/1st/1stgymd5018.php) | トレーナー |  |  |  | 1 | Base Set 94（Potion） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 019/025 | `GD5-019` | [元気のかたまり](https://pcg-search.com/card/1st/1stgymd5019.php) | トレーナー |  |  |  | 1 | Gym Challenge 117（Max Revive） | 拡張シート 第2弾（赤版）（1998-06-17） |
| 020/025 | `GD5-020` | [なんでもなおし](https://pcg-search.com/card/1st/1stgymd5020.php) | トレーナー |  |  |  | 1 | Base Set 82（Full Heal） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 021/025 | `GD5-021` | [熱血!](https://pcg-search.com/card/1st/1stgymd5021.php) | トレーナー |  |  |  | 2 | Gym Challenge 124（Fervor） |  |
| 022/025 | `GD5-022` | [ポケモンいれかえ](https://pcg-search.com/card/1st/1stgymd5022.php) | トレーナー |  |  |  | 1 | Base Set 95（Switch） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキの拡張カード）（2001-04-06） |
| 023/025 | `GD5-023` | [ポケモン図鑑HANDY505](https://pcg-search.com/card/1st/1stgymd5023.php) | トレーナー |  |  |  | 1 | Base Set 87（Pokédex） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26） |
| 024/025 | `GD5-024` | [グレンタウンジム](https://pcg-search.com/card/1st/1stgymd5024.php) | スタジアム |  |  |  | 1 | Gym Challenge 113（Cinnabar City Gym） | 第6弾 闇からの挑戦（1999-06-25） |
| 025/025 | `GD5-025` | [無色2個エネルギー](https://pcg-search.com/card/1st/1stgymd5025.php) | 特殊エネルギー |  |  |  | 1 | Base Set 96（Double Colorless Energy） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「ヤマブキシティジム ナツメ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30） |

基本エネルギー: Fire Energy 27 枚

## ポケモンジム第3弾「ヤマブキシティジム ナツメ」

発売日 1999-02-26。

| 番号 | id | カード名 | 種類 | タイプ | HP | レア | 枚数 | 英語版 | ほかの収録 |
|---|---|---|---|---|---|---|---|---|---|
| 001/026 | `GD6-001` | [ナツメのケーシィ](https://pcg-search.com/card/1st/1stgymd6001.php) | たね | 超 | 40 |  | 2 | Gym Challenge 93（Sabrina's Abra） | プロモ（1999-02-15） |
| 002/026 | `GD6-002` | [ナツメのケーシィ](https://pcg-search.com/card/1st/1stgymd6002.php) | たね | 超 | 50 |  | 2 | Gym Challenge 94（Sabrina's Abra） |  |
| 003/026 | `GD6-003` | [ナツメのユンゲラー](https://pcg-search.com/card/1st/1stgymd6003.php) | 1進化 | 超 | 70 |  | 2 | Gym Challenge 58（Sabrina's Kadabra） | 第6弾 闇からの挑戦（1999-06-25） |
| 004/026 | `GD6-004` | [ナツメのフーディン](https://pcg-search.com/card/1st/1stgymd6004.php) | 2進化 | 超 | 80 | -(キラ) | 1 | Gym Challenge 16（Sabrina's Alakazam） | 第6弾 闇からの挑戦（1999-06-25） |
| 005/026 | `GD6-005` | [ナツメのゴース](https://pcg-search.com/card/1st/1stgymd6005.php) | たね | 超 | 30 |  | 2 | Gym Challenge 96（Sabrina's Gastly） |  |
| 006/026 | `GD6-006` | [ナツメのゴース](https://pcg-search.com/card/1st/1stgymd6006.php) | たね | 超 | 50 |  | 2 | Gym Heroes 93（Sabrina's Gastly） |  |
| 007/026 | `GD6-007` | [ナツメのゴースト](https://pcg-search.com/card/1st/1stgymd6007.php) | 1進化 | 超 | 70 |  | 2 | Gym Challenge 55（Sabrina's Haunter） |  |
| 008/026 | `GD6-008` | [ナツメのゲンガー](https://pcg-search.com/card/1st/1stgymd6008.php) | 2進化 | 超 | 90 |  | 1 | Gym Challenge 29（Sabrina's Gengar） |  |
| 009/026 | `GD6-009` | [ナツメのスリープ](https://pcg-search.com/card/1st/1stgymd6009.php) | たね | 超 | 50 |  | 2 | Gym Challenge 95（Sabrina's Drowzee） |  |
| 010/026 | `GD6-010` | [ナツメのスリーパー](https://pcg-search.com/card/1st/1stgymd6010.php) | 1進化 | 超 | 70 |  | 1 | Gym Challenge 56（Sabrina's Hypno） | 第6弾 闇からの挑戦（1999-06-25） |
| 011/026 | `GD6-011` | [ナツメのバリヤード](https://pcg-search.com/card/1st/1stgymd6011.php) | たね | 超 | 60 |  | 2 | Gym Challenge 59（Sabrina's Mr. Mime） |  |
| 012/026 | `GD6-012` | [ナツメのルージュラ](https://pcg-search.com/card/1st/1stgymd6012.php) | たね | 超 | 60 |  | 2 | Gym Heroes 59（Sabrina's Jynx） |  |
| 013/026 | `GD6-013` | [ナツメのポリゴン](https://pcg-search.com/card/1st/1stgymd6013.php) | たね | 無 | 40 |  | 2 | Gym Challenge 98（Sabrina's Porygon） | 第6弾 闇からの挑戦（1999-06-25） |
| 014/026 | `GD6-014` | [エネルギー回収](https://pcg-search.com/card/1st/1stgymd6014.php) | トレーナー |  |  |  | 1 | Base Set 81（Energy Retrieval） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04） |
| 015/026 | `GD6-015` | [きずぐすり](https://pcg-search.com/card/1st/1stgymd6015.php) | トレーナー |  |  |  | 1 | Base Set 94（Potion） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>クイックスターターギフト（1998-12-04）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 016/026 | `GD6-016` | [ディフェンダー](https://pcg-search.com/card/1st/1stgymd6016.php) | トレーナー |  |  |  | 1 | Base Set 80（Defender） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>イントロパック★neo（ワニノコデッキの拡張カード）（2001-04-06） |
| 017/026 | `GD6-017` | [ナツメ](https://pcg-search.com/card/1st/1stgymd6017.php) | トレーナー |  |  | -(キラ) | 1 | Gym Challenge 20（Sabrina） | 第6弾 闇からの挑戦（1999-06-25） |
| 018/026 | `GD6-018` | [ナツメのESP](https://pcg-search.com/card/1st/1stgymd6018.php) | トレーナー |  |  |  | 1 | Gym Heroes 117（Sabrina's ESP） | 第6弾 闇からの挑戦（1999-06-25） |
| 019/026 | `GD6-019` | [ナツメの眼](https://pcg-search.com/card/1st/1stgymd6019.php) | トレーナー |  |  |  | 2 | Gym Heroes 125（Sabrina's Gaze） | 第6弾 闇からの挑戦（1999-06-25） |
| 020/026 | `GD6-020` | [なんでもなおし](https://pcg-search.com/card/1st/1stgymd6020.php) | トレーナー |  |  |  | 1 | Base Set 82（Full Heal） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>イントロパック（ゼニガメデッキ）（1999-07-30）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 021/026 | `GD6-021` | [プラスパワー](https://pcg-search.com/card/1st/1stgymd6021.php) | トレーナー |  |  |  | 1 | Base Set 84（PlusPower） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>イントロパック★neo（チコリータデッキの拡張カード）（2001-04-06） |
| 022/026 | `GD6-022` | [ポケモンセンター](https://pcg-search.com/card/1st/1stgymd6022.php) | トレーナー |  |  |  | 1 | Base Set 85（Pokémon Center） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26） |
| 023/026 | `GD6-023` | [マスターボール](https://pcg-search.com/card/1st/1stgymd6023.php) | トレーナー |  |  |  | 1 | Gym Challenge 116（Master Ball） | 拡張シート 第2弾（赤版）（1998-06-17）<br>クイックスターターギフト（1998-12-04）<br>イントロパック★neo（チコリータデッキ）（2001-04-06）<br>イントロパック★neo（ワニノコデッキ）（2001-04-06） |
| 024/026 | `GD6-024` | [ワープポイント](https://pcg-search.com/card/1st/1stgymd6024.php) | トレーナー |  |  |  | 2 | Gym Challenge 126（Warp Point） | 第6弾 闇からの挑戦（1999-06-25） |
| 025/026 | `GD6-025` | [ヤマブキシティジム](https://pcg-search.com/card/1st/1stgymd6025.php) | スタジアム |  |  |  | 1 | Gym Challenge 122（Saffron City Gym） | 第6弾 闇からの挑戦（1999-06-25） |
| 026/026 | `GD6-026` | [無色2個エネルギー](https://pcg-search.com/card/1st/1stgymd6026.php) | 特殊エネルギー |  |  |  | 1 | Base Set 96（Double Colorless Energy） | 第1弾 拡張パック（1996-10-20）<br>ポケモンジム第1弾「ニビシティジム タケシ」（1998-04-26）<br>ポケモンジム第1弾「ハナダシティジム カスミ」（1998-04-26）<br>ポケモンジム第2弾「クチバシティジム マチス」（1998-07-25）<br>ポケモンジム第2弾「タマムシシティジム エリカ」（1998-07-25）<br>ポケモンジム第3弾「グレンタウンジム カツラ」（1999-02-26）<br>イントロパック（フシギダネデッキ）（1999-07-30）<br>イントロパック（ゼニガメデッキ）（1999-07-30） |

基本エネルギー: Psychic Energy 26 枚
