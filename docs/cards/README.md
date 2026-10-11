# カードリストの見かた

旧裏（きゅううら）期に日本で発売された拡張パック 10 弾のカードリストです。
各弾のページは日本版の収録カードを 1 行 1 枚で並べ、対応する英語版（WotC 版）のカードを横に置いています。

| 弾 | 日本版 | 主に対応する英語版 |
|---|---|---|
| 第1弾 | [拡張パック](01-pmcg1-kakucho-pack.md) | Base Set |
| 第2弾 | [ポケモンジャングル](02-pmcg2-jungle.md) | Jungle |
| 第3弾 | [化石の秘密](03-pmcg3-kaseki.md) | Fossil |
| 第4弾 | [ロケット団](04-pmcg4-rocket.md) | Team Rocket |
| 第5弾 | [リーダーズスタジアム](05-pmcg5-leaders-stadium.md) | Gym Heroes |
| 第6弾 | [闇からの挑戦](06-pmcg6-yami-kara-no-chosen.md) | Gym Challenge |
| neo 第1弾 | [金、銀、新世界へ...](07-neo1-kin-gin-shinsekai.md) | Neo Genesis |
| neo 第2弾 | [遺跡をこえて...](08-neo2-iseki-wo-koete.md) | Neo Discovery |
| neo 第3弾 | [めざめる伝説](09-neo3-mezameru-densetsu.md) | Neo Revelation |
| neo 第4弾 | [闇、そして光へ...](10-neo4-yami-soshite-hikari.md) | Neo Destiny |

英語版にはあるが日本の拡張パックには入っていないカードは [english-only.md](english-only.md) にまとめています。

## 列の意味

| 列 | 内容 |
|---|---|
| No. | このリスト内の通し番号。旧裏カードにはコレクター番号（「1/102」のような番号）が印刷されていないため、並び順は出典データ（TCGdex）に従っています。カード上の番号ではありません。 |
| 日本語名 | 日本版のカード名。下の「日本語名の根拠」を参照。 |
| 種類 | ポケモン／トレーナー（スタジアム、ポケモンのどうぐ などの下位区分つき）／基本エネルギー／特殊エネルギー |
| タイプ・進化・HP | 英語版データの値です。日本版と英語版で同じと考えていますが、カードごとに日本版の現物と照合したわけではありません。 |
| レア | 日本版のレアリティ。● コモン、◆ アンコモン、★ レア、★キラ ホロ（キラ）レア、特殊 = 通常の3段階に当てはまらないもの（出典データ上の Secret Rare など）。 |
| 英語版（WotC） | 対応する英語版カードの名前と、セット名・カード番号。同じセットにホロ版とノーマル版の両方がある場合は番号を「・」でつないでいます。 |
| ⚠ | 英語版では、この弾の主な対応セットとは別のセットに入ったカード。 |
| 備考 | 「再録」は同じカードが英語版の別セットにも入っていることを示します（略号は下表）。 |

英語版セットの略号: BS = Base Set、JU = Jungle、FO = Fossil、BS2 = Base Set 2、TR = Team Rocket、G1 = Gym Heroes、G2 = Gym Challenge、N1〜N4 = Neo Genesis／Discovery／Revelation／Destiny、LC = Legendary Collection、SI = Southern Islands、Promo = Wizards Black Star Promos。

## 日本語名の根拠

- **ポケモンのカード名**: 対応する英語版カードの図鑑番号から、公式の日本語種族名を引いて組み立てています。
  - 接頭辞の付け方:
    - ジムリーダーのポケモン: 「タケシの」「カスミの」「エリカの」「マチスの」「ナツメの」「キョウの」「カツラの」「サカキの」
    - Rocket's → 「R団の」
    - Dark → 「わるい」
    - Light → 「やさしい」
    - Shining → 「ひかる」
    - アンノーンは「アンノーンA」の形
  - 組み立てた名前は、別系統の日本版カードデータ（Scrydex 由来）と全件照合済みです（[出典と確認状況](../sources.md#カード名の照合結果)）。
- **トレーナー・エネルギーのカード名**: 手作業で対応表（`data/curation/trainers.json`）を作り、確度（確実／有力／未確認）を記録しています。
  - 名前の後ろに **※** があるものは「未確認」です。日本語名の出典が 1 つ（TCGdex）しかなく、公式表記を確かめられていません。
  - 旧裏期の基本エネルギーは「草エネルギー」のように表記しています。「基本草エネルギー」という名前になったのは LEGEND 期からです（ポケモンWiki による）。

## 出典データと限界

- 日本版の収録構成とレアリティ: [TCGdex cards-database](https://github.com/tcgdex/cards-database)（MIT ライセンス）の `data-asia/PMCG`・`data-asia/neo`。
  - このデータの日本語テキスト（ワザ名・効果文・一部のカード名）は英語からの機械翻訳と見られ、公式の日本語テキストではありません。このリストでは使っていません。
  - 出典データでは、「闇からの挑戦」に「イマクニ？のドードー」「_____のラッキー」の 2 枚が入っています。どちらも通常のレアリティ構成から外れるカードで、本当に拡張パックに入っていたかは未確認です。
- 英語版のカード情報: [PokemonTCG/pokemon-tcg-data](https://github.com/PokemonTCG/pokemon-tcg-data)。
- 日本語カード名・レアリティの照合: Scrydex 由来の日本版データ（第三者のリポジトリにある写し）。照合に使っただけで、データ自体は収録していません。
- 日本語のポケモン名: [PokeAPI](https://github.com/PokeAPI/pokeapi) の `pokemon_species_names.csv`。
- 日本版と英語版の対応付けは、図鑑番号・HP・ワザのエネルギーコストとダメージ・名前の接頭辞（ジムリーダー名など）を突き合わせて自動で行い、自動では決まらないものを `data/curation/pokemon_overrides.json` で補正しています。
- ワザ・ポケモンパワー・弱点・抵抗力・にげるコスト（いずれも英語版の値）は `data/cards.csv`／`data/cards.json` に入っています。

生成手順は [scripts/README.md](../../scripts/README.md) を参照。
