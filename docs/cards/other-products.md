# 拡張パック以外の商品

<!-- このファイルは scripts/build_other_products.py が data/ja_text_pcgsearch.json と data/curation/other_products.json から生成しています。直接編集しないでください。 -->

旧裏期に日本で出た、拡張パック 10 弾以外の商品のカードをまとめたページ群です。
これらのカードは拡張パックのデータ（`data/cards.json`）には入れず、`data/ja_text_pcgsearch.json` に収録しています。

- カードの欄は、ポケモンカード 旧シリーズ検索（pcg-search.com）[N3] の転記です。
- 商品の情報（発売日・構成・英語版の配布など）は、主に Bulbapedia [X30][X31][X41]〜[X48] によります（MediaWiki の API でページの原文を取得して確認）。
- 確度（確実／有力／未確認）と出典の記号は [出典と確認状況](../sources.md) を参照。

| 商品 | 発売 | カード | 英語版 | ページ |
|---|---|---|---|---|
| 拡張シート（3 種）| 1998-03〜1998-11 | 125 種 | 英語版になったのは 6 枚（Wizards Black Star Promos） | [expansion-sheets.md](products/expansion-sheets.md) |
| 映画公開記念パック「サザンアイランド」（1 種）| 1999-07-17 | 18 種 | Southern Islands（2001）の 18 枚 | [southern-islands.md](products/southern-islands.md) |
| ポケモンジム（構築済みデッキ）（6 種）| 1998-04〜1999-02 | 153 種 | デッキにしかなかったカードは Gym Heroes・Gym Challenge へ | [gym-decks.md](products/gym-decks.md) |
| クイックスターターギフト（1 種）| 1998-12-04 | 58 種 | 再録だけ | [quick-starter-gift.md](products/quick-starter-gift.md) |
| イントロパック・イントロパック★neo（7 種）| 1999-07-30・2001-04-06 | 162 種 | このパックだけのカードは英語版なし | [intro-packs.md](products/intro-packs.md) |
| neo プレミアムファイル（3 種）| 1999-12〜2000-11 | 27 種 | Neo Genesis・Discovery・Revelation へ | [premium-files.md](products/premium-files.md) |
| プロモーションカード（旧裏期・neo 期）| 1996〜2001 | 138 種 | 一部が Wizards Black Star Promos など | [promos.md](products/promos.md) |

英語版にあって日本の拡張パックにないカードの、日本での初出は [英語版のみに見られるカード](english-only.md) にあります。
商品をまたいだ同じカード（再録）の判定のしかたと点検の結果は [再録カードの対応付け](reprints.md) にあります。

## まだ確認できていないこと

- 拡張シートの自動販売機の種類（バンダイの「ジャンボカードダス」とする情報があるが未確認）
- 青版の「化石の発掘」「月の石」のレアリティマークの有無（pcg-search と Bulbapedia で食い違い）
- サザンアイランドの 3 枚入りパックの販売場所（ファイル版は上映館だけ）
- プロモカードのうち、配布方法を突き合わせられなかったもの（[プロモーションカード](products/promos.md) で空欄のもの）
- Wizards Black Star Promos のうち、日本のカードとの対応がわからなかったもの（[プロモーションカード](products/promos.md) の表にない番号）
