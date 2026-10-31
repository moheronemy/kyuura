# 出典と確認状況

## 調べ方について

このページは、参照した資料の一覧と、それぞれをどこまで確かめたかの記録です。分野ごとの確認状況と件数は [調査の状況](research-status.md) にまとめています。

資料については、次の 3 つを分けて書いています。

- 資料があること（ほかの資料の引用や書誌でわかる）
- 資料を読めたこと（原文・スキャン・保存された写しを実際に読んだ）
- その資料が、ある記述を裏付けること（本文で出典の記号を付けた箇所。読めた資料でも、記述の全部を裏付けるとは限らない）

### 原文・スキャン・保存された写しで読んだもの

- 当時の印刷物: Elite Fourum のスレッドで公開された Google Drive の PDF [J37] で、『ポケモンカード・ファンクラブ』Vol.1〜5、『トレーナーズ』Vol.1〜21（どちらも全号）、ガイドブック [P29]、『めざせ! ポケモンカードマスター』[P34] の誌面を読みました。『ポケモンカードオフィシャルブック2000』[P43] は、Internet Archive のスキャン [J38] で、公式ルール（pp.306〜326）と、エラッタ・日英の違いにかかわるカードのページ、わるいカメールの「こうらがえし」にかかわるページ（p.82・p.88・p.89・p.111・p.192・p.203・p.279。2026-10-13）を読みました（2026年10月。全ページは読んでいない）。『ルールブック第4版』の冊子 [P44] は、Internet Archive のスキャン [J39] で全ページを読みました（2026年10月）。どれもスキャンで読んだもので、実物ではありません（[当時の印刷物](#当時の印刷物スキャンで誌面を確認)、[印刷物の照合記録](printed-sources.md)）。
  - Drive の PDF は、drive.google.com のビューアーがページごとに返す画像で読みました。ファイルの直接のダウンロード（drive.usercontent.google.com）とビューアーのスクリプト（www.gstatic.com）は、作成環境のネットワーク制限で開けませんでした（回避はしていません）。
  - スキャンは個人が自分の所有する冊子を取り込んで公開したもので、号数・ページは誌面の表示（表紙・ノンブル・奥付）で確かめました。
- 公式サイトの当時のページ（P10、P15〜P23、P28）: Internet Archive に保存された写しで原文を読みました。画像で書かれた部分は、保存された写しをブラウザで表示して確かめました。
- Bulbapedia（X10、X11、X30、X31、X37、X38、X41〜X58）: MediaWiki の API でページの原文（ウィキテキスト）を取得しました。記事ページは Cloudflare の確認画面になるため API を使っています（確認画面の回避はしていません）。
- なぞのばしょ（J22、J23、J25〜J28、N1）と pcg-search（N3。カードの画像を含む）: ページを直接取得しました。
- 旧裏 wiki（J1、J6、J36）: サイトは Cloudflare の確認画面（HTTP 403）で開けないため、Internet Archive に保存された写しで本文を読みました（J1 は 2026-03-20、J6 は 2026-01-28、J36 は 2026-02-06 の保存）。
- note（J30、J31、J32）とポケブーン（J33、J34）: 直接取得しました。J32 の記事の中の画像（新ガルーラルールの説明の誌面の写真）も確認しました。記事の説明は『トレーナーズ』Vol.14 p.21 としていますが、スキャン [J37] で照合すると Vol.15 p.21 のページでした。
- ポケモンWiki のカードのページ（N2）: ユーザーがブラウザで保存したもの（`data/raw/`）を使いました。
- Elite Fourum のスレッド「Pokémon TCG set credits」[X21]: ルールブックの表紙・クレジットのページの写真を見ました（2026年10月。本文のページは写っていない）。
- カードのデータ（pokemon-tcg-data、TCGdex、PokeAPI、Scrydex 由来のデータ [S1]）: 公開されているリポジトリのデータを使いました（[カードリストのデータ](#カードリストのデータ)）。

### 検索結果の要約だけで確かめたもの

- 上に挙げていない資料（旧裏 wiki のほかのページ、ポケモンWiki のカード以外のページ、Wikipedia、ポケブーンの J29、Pojo に転載された WotC のルールブック、Jason Klaczynski 氏のサイトなど）は、作成環境のネットワーク制限やサイト側の制限で開けておらず、ウェブ検索の結果（検索エンジンが返す要約と抜粋）だけで確かめています。回避はしていません。
  - 引用の文言は原文と一字一句同じとは限らず、要約の取り違えが含まれている可能性もあります。
  - 最初に作った文書（日本版・英語版のルール、日米の違い）は、この方法で書き始めました。その後に上の資料で確かめ直した記述には、出典の記号と確度を付け直しています。要約だけによる記述は、本文でそう書いています。
- 駿河屋（J35）は開けず、内容を確認していません。
- 公開・引用の前に、各ページを開いて確認してください。英語版のルールは、WotC の Advanced Rulebook [E4][E5] を優先してください（このリポジトリでは原文を確認できていません）。

### 読めなかったもの

- 日本のルールブック・遊びかた説明書の第1〜3版・第5版の本文（第4版は [P44] を読んだ）。
- 『大人にもわかるポケモンカード戦略』（初版・改訂版）の本文。探した結果は [まだ確認できていないこと](#まだ確認できていないこと) に書いています。
- スレッド [J37] の最初の投稿の OneDrive（1drv.ms）のリンクは、作成環境のネットワーク制限で開けませんでした（回避はしていません）。Internet Archive の資料のページ（archive.org）は、2026年10月に作成環境の設定で許可され、[J38] と [J39] を読みました。

## 日本語の資料

「旧裏 wiki」は、ファンによる「ポケモンカード旧裏面＠研究・考察 Wiki*」のことです。

| 記号 | 資料 | URL |
|---|---|---|
| J1 | 旧裏 wiki「当時のルール」。『オフィシャルブック2000』『めざせ！ポケモンカードマスター』『ポケモンカード トレーナーズ vol.1』などを出典にしている。ルールブックの各版、殿堂ランクの各版（2001.03・2001.01・2001.09・2001.12・2002.05）。Internet Archive の 2026-03-20 の保存で本文を確認（ページの最終更新 2025-10-21） | https://wikiwiki.jp/pcg-base-neo/当時のルール （保存: https://web.archive.org/web/20260320192127/https://wikiwiki.jp/pcg-base-neo/%E5%BD%93%E6%99%82%E3%81%AE%E3%83%AB%E3%83%BC%E3%83%AB ） |
| J2 | 旧裏 wiki「対戦ルール」（現代の旧裏対戦の統一ルール。にげるの項は『ポケモンカード オフィシャルブック2000』p310-311 を出典に挙げる） | https://wikiwiki.jp/pcg-base-neo/対戦ルール |
| J3 | 旧裏 wiki「用語集」 | https://wikiwiki.jp/pcg-base-neo/用語集 |
| J4 | 旧裏 wiki「『こんらん』で20ダメージルール」 | https://wikiwiki.jp/pcg-base-neo/「こんらん」で20ダメージルール |
| J5 | 旧裏 wiki「効果別分類」 | https://wikiwiki.jp/pcg-base-neo/効果別分類 |
| J6 | 旧裏 wiki「旧裏の歴史」（年表。『トレーナーズ』の各号の発行日など）。Internet Archive の 2026-01-28 の保存で本文を確認（ページの最終更新 2026-01-06） | https://wikiwiki.jp/pcg-base-neo/旧裏の歴史 （保存: https://web.archive.org/web/20260128203304/https://wikiwiki.jp/pcg-base-neo/%E6%97%A7%E8%A3%8F%E3%81%AE%E6%AD%B4%E5%8F%B2 ） |
| J7 | 旧裏 wiki「第1回 公式トーナメント レギュレーション」 | https://wikiwiki.jp/pcg-base-neo/第1回%20公式トーナメント%20レギュレーション |
| J8 | 旧裏 wiki「第2回 公式トーナメント大会 レギュレーション」 | https://wikiwiki.jp/pcg-base-neo/第2回%20公式トーナメント大会%20レギュレーション |
| J9 | 旧裏 wiki「当時の記録」 | https://wikiwiki.jp/pcg-base-neo/当時の記録 |
| J10 | ポケモンWiki「ポケットモンスターカードゲーム」 | https://wiki.xn--rckteqa2e.com/wiki/ポケットモンスターカードゲーム |
| J11 | ポケモンWiki「ねむり」 | https://wiki.xn--rckteqa2e.com/wiki/ねむり |
| J12 | ポケモンWiki「ポケットモンスターカードゲーム 第1弾スターターパック」 | https://wiki.xn--rckteqa2e.com/wiki/ポケットモンスターカードゲーム_第1弾スターターパック |
| J13 | プレイジム TOKYO の note（店舗の旧裏ルール） | https://note.com/play_gym_tokyo/n/n7ca38fdc6070 |
| J14 | ののほほ氏の note | https://note.com/nonohoho/n/na42d3f8a7960 |
| J15 | Revenir 氏の note | https://note.com/revenir/n/n61d22055219e |
| J16 | アニヲタWiki（こんらんの項目） | https://w.atwiki.jp/aniwotawiki/pages/45923.html |
| J17 | ピクシブ百科事典「こんらん」 | https://dic.pixiv.net/a/こんらん |
| J18 | ポケカ wiki（seesaa）「こんらん」 | https://seesaawiki.jp/w/jester_the_pcg/d/%A4%B3%A4%F3%A4%E9%A4%F3 |
| J19 | どらぽん氏の note | https://note.com/_dorapon_/n/nabb35e02c844 |
| J20 | トレトク「おすすめルール No.02」の販売ページ | https://www.toretoku.jp/item/details/89135 |
| J21 | Wikipedia「ポケモンカードゲームの公式大会一覧」 | https://ja.wikipedia.org/wiki/ポケモンカードゲームの公式大会一覧 |
| J22 | nazonobasho「カメックスメガバトル 1998 レギュレーション」 | https://nazonobasho.com/regulation-kamexmegabattle1998/ |
| J23 | nazonobasho「2001年 殿堂レギュレーション」 | https://nazonobasho.com/2001dendou-regulation/ |
| J24 | ポケモンWiki「ポケットモンスターカードゲーム 映画公開記念パック サザンアイランド」（発売日・価格・構成） | https://wiki.xn--rckteqa2e.com/wiki/ポケットモンスターカードゲーム_映画公開記念パック_サザンアイランド |
| J25 | なぞのばしょ「ポケモンカードe 第1弾」の商品紹介（裏面の変更、新旧の裏面を混ぜるときの方法、特殊能力・サポーター・やけど。『トレーナーズ』Vol.12・13 を出典に挙げる） | https://nazonobasho.com/product-e1/ |
| J26 | なぞのばしょ「グループタッグマッチ｜バトル★ネオ サマーロード｜レギュレーション」（2001年のハーフデッキ・殿堂ランク） | https://nazonobasho.com/grouptagmatch/ |
| J27 | なぞのばしょ「ポケモンカード・ファンクラブ」（会報の各号の紹介。Vol.5 のガルーラルールと「タッチ交代！」） | https://nazonobasho.com/pokemoncardfanclub/ |
| J28 | なぞのばしょ「ポケモンカードゲームADV 第1弾」の商品紹介（ポケモンex。『トレーナーズ』Vol.20 を出典に挙げる） | https://nazonobasho.com/product-adv01/ |
| J29 | ポケブーン「バトルロード サマー★2002 &『ポケモンフェスタ2002』」（新ガルーラルールの案内の転記。検索結果の要約だけで確認） | https://pokeboon.com/jp/promo_event/battle-road-summer-2002-and-pokemon-festa-2002/ |
| J30 | ももち氏の note「老害、昔を振り返る その１」（2021-08-30 公開。バトル★ネオ サマーロード2001 とバトルロード スプリング★2002 のシニアの部の回想。2026年10月に本文を確認） | https://note.com/arcanine/n/nb465d938f3fb |
| J31 | プレイジム TOKYO の note「【ポケモンカードe】シリーズ現在のルールとの相違点について」（2024-02-02 公開。2003年1月時点のルールを適用するとする店舗のルール。使えるカードは ★VS・★Web・ポケモンカードe。2026年10月に本文を確認） | https://note.com/play_gym_tokyo/n/nd37499228118 |
| J32 | なにものか氏の note「【イベント】第9回ニモノ杯クラシック・新ガルーラバトルの部［8/14（月）横浜（関内）］」（2023-07-30 公開、2023-08-13 更新。2023年の再現大会の要項。「新ガルーラルールの説明」の誌面の写真を掲載（記事は Vol.14 p.21 とするが、スキャン [J37] では Vol.15 p.21 [P24]）。本文と写真を 2026年10月に確認） | https://note.com/nimono_note/n/nbe579f5b16f1 （写真: https://assets.st-note.com/img/1690551618718-c5MuLaFidk.jpg ） |
| J33 | ポケブーン「『ポケモンカード トレーナーズ』Vol.1～Vol.21までの一覧」（2020-09-04 公開。各号の「発行年」・目次・おまけ。本文を確認） | https://pokeboon.com/jp/pokemoncard-trainers/ |
| J34 | ポケブーン「009/P マサキ：『ポケモンカードトレーナーズVOL.13』おまけカード」（2019-05-01 公開。「リリース 2001年11月1日(木）」。本文を確認） | https://pokeboon.com/jp/009p-bill-promo/ |
| J35 | 駿河屋の商品ページ（『トレーナーズ』Vol.13 とされる。作成環境のネットワーク制限で開けず、内容は未確認） | https://www.suruga-ya.jp/product/detail/620027658 |
| J37 | Elite Fourum のスレッド「Japanese Document Archives, Trainer Mags, Silver Bible PDF's」（2021-06-28 開始）の投稿 36（dromanyte、2024-10-16）が公開した Google Drive のフォルダの PDF（『ポケモンカード トレーナーズ』Vol.1〜21、『ポケモンカード・ファンクラブ』Vol.1〜5、ガイドブック、リザードンメガバトルの公式ドキュメントブックなどのスキャン）。巻号ごとのファイルの URL とページは [印刷物の照合記録](printed-sources.md) | https://www.elitefourum.com/t/japanese-document-archives-trainer-mags-silver-bible-pdfs/33002 （フォルダ: https://drive.google.com/drive/folders/1NLN44XMNsVNwaGeBuOuanJLWIzdbHqKM ） |
| J36 | 旧裏 wiki「バトルネオ★サマーロード レギュレーション」（2001年のジュニア・シニアリーグのカードプールと殿堂ポイント。Internet Archive の 2026-02-06 の保存で本文を確認。ページの最終更新 2024-04-30） | https://wikiwiki.jp/pcg-base-neo/バトルネオ★サマーロード%20レギュレーション （保存: https://web.archive.org/web/20260206111650/https://wikiwiki.jp/pcg-base-neo/%E3%83%90%E3%83%88%E3%83%AB%E3%83%8D%E3%82%AA%E2%98%85%E3%82%B5%E3%83%9E%E3%83%BC%E3%83%AD%E3%83%BC%E3%83%89%20%E3%83%AC%E3%82%AE%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3 ） |
| J38 | Internet Archive「ポケモンカードオフィシャルブック2000 : Creatures」（2022-12-10 に登録された全ページのスキャン。PDF・OCR つき） | https://archive.org/details/pokemoncard-officialbook2000 |
| J39 | Internet Archive「ポケモンカードゲーム ルールブック第4版」（2022-11-03 に登録された冊子の全ページのスキャン。PDF 41 葉（表紙・見開き 39・裏表紙）、OCR つき。資料の日付の記入はない） | https://archive.org/details/pokemoncard-rulebook-4 |

## 英語版（WotC）の公式資料の転載

| 記号 | 資料 | URL |
|---|---|---|
| E1 | WotC Basic Rules（Pojo 転載） | https://www.pojo.com/pokemon/rules/oldbasicrules.html |
| E2 | WotC Expert Rules（Pojo 転載） | https://www.pojo.com/pokemon/rules/oldexpertrules.html |
| E3 | Expert Rules Additions – What's New in the Neo Genesis Expansion?（2000年） | https://www.pojo.com/pokemon/rules/neorules1.pdf |
| E4 | Advanced Rulebook Version 8（Expedition、2002年） | https://www.pojo.com/pokemon/rules/PokemonE-Rulebook.pdf |
| E5 | Advanced Rulebook Version 9（Aquapolis、2003年） | https://www.pojo.com/pokemon/rules/PokemonA-Rulebook.pdf （別所: https://www.judgeball.com/files/archives/tcg-rulebooks/en/WOTCE2.pdf ） |
| E6 | Judge Ball のルールブック保管庫 | https://www.judgeball.com/archives/tcg-rulebooks/ |
| E7 | Pojo「2003年のルール変更」（EX Ruby & Sapphire） | https://www.pojo.com/Features/2003/rules.html |
| E8 | Expert Rules（やけどを含む後期版、Pojo 転載） | https://www.pojo.com/pokemon/rules/expertrules.html |
| E9 | WotC Rulings Compendium（ミラー）、裁定 854 | https://compendium.pokegym.net/compendium.html 、 https://compendium.pokegym.net/ruling/854/ |

## その他の資料（主に英語）

| 記号 | 資料 | URL |
|---|---|---|
| X1 | Jason Klaczynski「Original Rules」（日本の初期ルールの解説） | https://jklaczpokemon.com/original-rules/ |
| X2 | Jason Klaczynski「Pokémon WotC Rules」 | https://jklaczpokemon.com/pokemon-wotc-rules/ |
| X3 | Jason Klaczynski「WotC Erratas」 | https://jklaczpokemon.com/wotc-erratas/ |
| X4 | Jason Klaczynski「Prop 15/3」 | https://jklaczpokemon.com/prop-15-3/ |
| X5 | pokemon1999.org「The Rules of Old School Pokémon」 | https://pokemon1999.org/the-rules-of-old-school-pokemon/ |
| X6 | PTCG Archive「First Turn Rules」 | https://ptcgarchive.com/first-turn-rules-full/ |
| X7 | Bulbapedia「Special Condition (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Special_Condition_(TCG) |
| X8 | Bulbapedia「Retreat Cost (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Retreat_Cost_(TCG) |
| X9 | Bulbapedia「Errata (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Errata_(TCG) |
| X10 | Bulbapedia「2001-02 Modified format (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/2001-02_Modified_format_(TCG) |
| X11 | Bulbapedia「2002-03 Modified format (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/2002-03_Modified_format_(TCG) |
| X12 | Bulbapedia「_____'s Pikachu (Wizards Promo 24)」「Unlimited format (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Unlimited_format_(TCG) |
| X13 | Pojo の掲示板（日本の初期ルールについてのスレッド） | https://www.pojo.biz/board/showthread.php?t=1302237 |
| X14 | TCG ONE フォーラム「WotC erratas complete list」 | https://forum.tcgone.net/t/wotc-erratas-complete-list/9383 |
| X15 | Bulbapedia「Slowking (Neo Genesis 14)」 | https://bulbapedia.bulbagarden.net/wiki/Slowking_(Neo_Genesis_14) |
| X16 | Smogon「The Smog」Issue 10 の TCG 記事 | https://www.smogon.com/smog/issue10/tcg2 |
| X17 | Bulbapedia「Pokémon Breeder (Base Set 76)」「Rocket's Sneak Attack (Team Rocket 16)」「Imposter Professor Oak (Base Set 73)」 | https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Breeder_(Base_Set_76) |
| X18 | TCG ONE フォーラム「EX era rule accuracy」、SixPrizes の記事（2004年の先攻サポーター禁止） | https://forum.tcgone.net/t/ex-era-rule-accuracy/629 、 https://sixprizes.com/2009/07/30/is-it-better-to/ |
| X20 | Bulbapedia「20 Damage from Confusion (Vending S3)」 | https://bulbapedia.bulbagarden.net/wiki/20_Damage_from_Confusion_(Vending_S3) |
| X21 | Elite Fourum「Pokémon TCG set credits」 | https://www.elitefourum.com/t/pokemon-tcg-set-credits/50879 |
| X22 | Bulbapedia「Darkness Energy (Neo Genesis 104)」 | https://bulbapedia.bulbagarden.net/wiki/Darkness_Energy_(Neo_Genesis_104) |
| X23 | Pojo の Q&A（Expedition の鋼エネルギーについて。URL は未取得） | ― |
| X24 | Jason Klaczynski「1999 Base-Fossil」ほか | https://jklaczpokemon.com/1999-base-fossil/ |
| X26 | Bulbapedia「Jungle (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Jungle_(TCG) |
| X27 | Bulbapedia「Team Rocket (TCG)」「Dark Raichu (Team Rocket 83)」 | https://bulbapedia.bulbagarden.net/wiki/Dark_Raichu_(Team_Rocket_83) |
| X28 | Bulbapedia「Gym Heroes (TCG)」「Hanada City Gym (TCG)」、Serebii の Gym Heroes ページ | https://bulbapedia.bulbagarden.net/wiki/Gym_Heroes_(TCG) 、 https://www.serebii.net/card/gymheroes/ |
| X29 | Elite Fourum「Neo Genesis English vs Japanese」、Flipside Gaming「Hidden Gems: Neo Premium Files」 | https://elitefourum.com/t/neo-genesis-english-vs-japanese/29546 、 https://flipsidegaming.com/blogs/pokemon-blog/hidden-gems-neo-premium-files |
| X30 | Bulbapedia「Vending Machine cards (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Vending_Machine_cards_(TCG) |
| X31 | Bulbapedia「Southern Islands (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Southern_Islands_(TCG) |
| X32 | Bulbapedia「Pokémon VS (TCG)」（日本で最初に番号を付けた弾）、Bill's Archive | https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_VS_(TCG) 、 https://billsarchive.com/expansion-pack-jp.html |
| X33 | カドヤ（マークなし初版についての記事） | https://www.kadoya78.com/news/pokemon/894/ |
| X34 | 旧ポケカ買取の記事（リザードンの「かいりきポケモン」誤植）、Elite Fourum「No rarity Japanese Base Set」 | https://kyupokeca-kaitori.com/apps/note/charizard-kairiki-difference 、 https://www.elitefourum.com/t/no-rarity-japanese-base-set/11607 |
| X35 | ポケモンカードゲーム公式「20周年 クロニクル」（2001年7月に裏面デザイン変更） | https://www.pokemon-card.com/20th/chronicle/ |
| X36 | ポケモンWiki「ポケモンカード★web」、Samurai Sword Tokyo「Japanese Pokémon card backs explained」 | https://wiki.pokemonwiki.com/wiki/ポケモンカード★web 、 https://samuraiswordtokyo.com/blogs/news/japanese-pokemon-card-backs-explained |
| X37 | Bulbapedia「Brock's Ninetales (Gym Challenge 3)」（日本版ははじめ、のせたカードのポケモンパワーを使えたこと） | https://bulbapedia.bulbagarden.net/wiki/Brock%27s_Ninetales_(Gym_Challenge_3) |
| X38 | Bulbapedia「Koga's Ditto (Gym Challenge 10)」 | https://bulbapedia.bulbagarden.net/wiki/Koga%27s_Ditto_(Gym_Challenge_10) |
| X39 | Serebii「Vending Machine Series」（拡張シートの価格・構成） | https://serebii.net/card/vendingmachineset2 |
| X40 | Pokumon「Vending Machine Sheet 1〜3」（拡張シートの発売日・シートの構成・正式名） | https://pokumon.com/vending-machine-sheet-1/ |
| X41 | Bulbapedia「Wizards Black Star Promos (TCG)」と各カードのページ（日本での初出・英語版の配布・日英の違い・日本語のワザ名） | https://bulbapedia.bulbagarden.net/wiki/Wizards_Black_Star_Promos_(TCG) ほか |
| X42 | Bulbapedia「Tentacruel (Southern Islands 10)」（どくばりの日英の違い） | https://bulbapedia.bulbagarden.net/wiki/Tentacruel_(Southern_Islands_10) |
| X43 | Bulbapedia の拡張シートのシート構成（Template:ExpansionSheet/Series1〜3）と各カードのページ（Bill's PC、Imakuni?'s Corner、Lose?、Pokémon Machine、Fossil Excavation、Kadabra・Haunter (Vending S3)） | https://bulbapedia.bulbagarden.net/wiki/Template:ExpansionSheet/Series1 ほか |
| X44 | Bulbapedia「List of Japanese Pokémon Trading Card Game expansions」（日本の弾と商品の発売日・枚数） | https://bulbapedia.bulbagarden.net/wiki/List_of_Japanese_Pok%C3%A9mon_Trading_Card_Game_expansions |
| X45 | Bulbapedia の英語版セットのページ（Gym Heroes、Gym Challenge、Neo Genesis、Neo Discovery、Neo Revelation。イラストが日英で違うカード） | https://bulbapedia.bulbagarden.net/wiki/Gym_Heroes_(TCG) ほか |
| X46 | Bulbapedia「Original TCG Era merchandise」、ジムデッキ 6 種のページ（Nivi City Gym など）、「Quick Starter Gift Set (TCG)」、ジムデッキのカードのページ（英語版のカードへの転送） | https://bulbapedia.bulbagarden.net/wiki/Original_TCG_Era_merchandise ほか |
| X47 | Bulbapedia「Neo TCG Era merchandise」（プレミアムファイル 1〜3） | https://bulbapedia.bulbagarden.net/wiki/Neo_TCG_Era_merchandise |
| X48 | Bulbapedia「Unnumbered Promotional cards (TCG)/1996-2005」（日本の番号なしプロモの一覧） | https://bulbapedia.bulbagarden.net/wiki/Unnumbered_Promotional_cards_(TCG)/1996-2005 |
| X49 | Bulbapedia「Intro Pack (TCG)」「Original TCG Era merchandise」と、イントロパックの各カードのページ（発売日・内容・デッキリスト・カードの番号・同じカードへの転送） | https://bulbapedia.bulbagarden.net/wiki/Intro_Pack_(TCG) ほか |
| X50 | Bulbapedia「Intro Pack Neo (TCG)」「Neo TCG Era merchandise」と、イントロパック★neo の各カードのページ | https://bulbapedia.bulbagarden.net/wiki/Intro_Pack_Neo_(TCG) ほか |
| X51 | Bulbapedia の再録の点検に使ったカードのページ（「Flying Pikachu (Wizards Promo 25)」「Flying Pikachu (ANA promo 99)」「Sabrina's Abra (Gym Challenge 93)」「Jolteon (Jungle 4)」「Grimer (Fossil 48)」「Gastly (Fossil 33)」） | https://bulbapedia.bulbagarden.net/wiki/Flying_Pikachu_(ANA_promo_99) ほか |
| X52 | Bulbapedia「Errata (TCG)」（日本だけのエラッタ: プラスパワー、エネルギー回収・超エネルギー回収、タケシのキュウコン、旧裏・neo のトレーナーのサポーター化、特殊能力のポケパワー・ポケボディー化。当時の資料の号数・ページを挙げる） | https://bulbapedia.bulbagarden.net/wiki/Errata_(TCG) |
| X53 | Bulbapedia「Touch Generation Change! (New Garura Parent/Child promo)」「Touch Change! (Garura Parent/Child promo)」「Touch Exchange! (PCG-P Promo 130)」「Kangaskhan (Garura Parent/Child promo)」 | https://bulbapedia.bulbagarden.net/wiki/Touch_Generation_Change!_(New_Garura_Parent/Child_promo) ほか |
| X54 | Bulbapedia「Pokémon VS (TCG)」「Pokémon Web (TCG)」「Supporter card (TCG)」「Pokémon Power (TCG)」「Special Condition (TCG)」 | https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_VS_(TCG) ほか |
| X55 | Bulbapedia「P Promotional cards (TCG)」、「Unnumbered Promotional cards (TCG)/1996-2005」の 2002年の項、「No.1 Trainer (Pokémon Card Game Official Tournament promo)」「Elite Four Trainer (Battle Road Summer 2002 finals promo)」（大会の日程・会場・部門） | https://bulbapedia.bulbagarden.net/wiki/No.1_Trainer_(Pok%C3%A9mon_Card_Game_Official_Tournament_promo) ほか |
| X56 | Bulbapedia「Energy Removal (Base Set 92)」「Energy Removal 2 (Expedition 140)」「Super Energy Removal (Base Set 79)」「Super Energy Removal 2 (Aquapolis 134)」「Charizard (Base Set 4)」「Slowking (Neo Genesis 14)」 | https://bulbapedia.bulbagarden.net/wiki/Energy_Removal_2_(Expedition_140) ほか |
| X57 | Bulbapedia「No.1 Trainer (Pokémon Card Game Official Tournament promo)」「No.2 Trainer (…)」「No.3 Trainer (…)」（大会の入賞の賞品のカードの版ごとの本文の英訳・配布の大会と時期。2026-10-31 に MediaWiki の API で取得。No.1 の版は revision 4589167） | https://bulbapedia.bulbagarden.net/wiki/No.1_Trainer_(Pok%C3%A9mon_Card_Game_Official_Tournament_promo) ほか |
| X58 | Bulbapedia のジャンボカード・ファンクラブの特典のカードのページ（「Pikachu, Jigglypuff, and Clefairy (CoroCoro promo)」「Articuno, Moltres, and Zapdos (Warner Bros. promo)」「Mewtwo Strikes Back」「Pikachu's Summer Vacation」「Pokémon Plaza」「Lawrence III」「Pokémon Valley」「Pichu and Pikachu」「Crystal Tower's Entei」（以上 CoroCoro promo）、「Charizard (Base Set 4)」、「Tropical Present」「New Year Present」「New Century Present」（Fan Club promo。Tropical Present は revision 4464780）。2026-10-31 に MediaWiki の API で取得） | https://bulbapedia.bulbagarden.net/wiki/Tropical_Present_(Fan_Club_promo) ほか |

## 当時の公式資料（ウェブアーカイブで原文を確認）

当時の公式サイトのページで、Internet Archive（Wayback Machine）に保存された写しで原文を読んだものです。保存された時点の内容で、公開日の時点の版と同じかは、保存日の範囲でしか言えません。

| 記号 | 資料 | 内容・確認した写し |
|---|---|---|
| P10 | 公式サイト（pokemon-card.com）「ポケモンカードｅシリーズ以前の特殊能力 Ｑ＆Ａ」（ページの日付 2002.5.24） | 旧裏・neo の特殊能力の「ポケボディー」一覧表（65 行。ここにないものはすべてポケパワー）と、ブビィ「モクモク」の Q&A。保存の写し: 2002-06-10 https://web.archive.org/web/20020610221924/http://www.pokemon-card.com:80/play/q_and_a/e_before_qa.html （日付の表示なし）、2005-10-18 https://web.archive.org/web/20051018170017/http://www.pokemon-card.com:80/play/q_and_a/e_before_qa.html 、2007-02-09 https://web.archive.org/web/20070209013655/http://www.pokemon-card.com/asobikata/qa_020524_2.html 。2002-08-04 の「あそびかたQ&A」の目次（https://web.archive.org/web/20020804064207/http://www.pokemon-card.com:80/play/play_qa.html ）からリンクされている。Bulbapedia [X52] も出典に挙げる |
| P15 | 公式サイト「殿堂入りカード」（2001年）: 「『殿堂入りカード』とは？」（/play/dendo1.html）と「PCL認定『殿堂入りカード』リスト」（/play/dendo2.html） | 2001-07-24 の写し: 32 種。凡例「＝2001年夏から追加されるカードだよ」と 6 種の色の付いた行。2001-11-04 の写し: 36 種。凡例「＝2001年9月から追加されたカードだよ」と 4 種の色の付いた行（凡例の色の画像は保存されていない）。https://web.archive.org/web/20010724222610/http://www.pokemon-card.com:80/play/dendo2.html 、https://web.archive.org/web/20011104124800/http://www.pokemon-card.com:80/play/dendo2.html |
| P16 | 公式サイト「殿堂入りカード」（2002年）: 「殿堂入りカードリスト」（/play/dendo/list.html）、「『殿堂入りカード』ってなに？」（/play/dendo/what.html）、目次（/play/play_dendo.html） | 2002-01-19 の写し:「『殿堂入りカード』リスト（2001年12月版）」。2002-06-04 の写し: 2002年の一覧に「（2001年5月版）」と表示（目次は「2002年5月版」）。2002-08-05 の写し: 見出しは「2002年5月版」、ページの題名は「2001年5月版」のまま。https://web.archive.org/web/20020119223256/http://www.pokemon-card.com:80/play/dendo/list.html 、https://web.archive.org/web/20020604200248/http://www.pokemon-card.com:80/play/dendo/list.html 、https://web.archive.org/web/20020805034629/http://www.pokemon-card.com:80/play/dendo/list.html |
| P17 | 公式サイト「いろんなルールで遊ぼう！」: 「ミックスデッキルール＜基本のルール＞」（/play/ironnarule/mix1.html）、「＜いろんな遊びかた＞」（mix2.html）、「ハーフデッキルール」（half.html） | 2002-01-19 の写しなど。https://web.archive.org/web/20020119223510/http://www.pokemon-card.com:80/play/ironnarule/mix1.html 、https://web.archive.org/web/20020119220836/http://www.pokemon-card.com:80/play/ironnarule/mix2.html 、https://web.archive.org/web/20020119223607/http://www.pokemon-card.com:80/play/ironnarule/half.html |
| P18 | 公式サイト「新ガルーラルールであそぼう！」（/play/ironnarule/galura_rule01.html〜04.html、目次 galura_rule_top.html） | 2002-03-05〜2002-04-04 の写し。https://web.archive.org/web/20020404005141/http://www.pokemon-card.com:80/play/ironnarule/galura_rule01.html 、https://web.archive.org/web/20020306000907/http://www.pokemon-card.com:80/play/ironnarule/galura_rule02.html 、https://web.archive.org/web/20020306001040/http://www.pokemon-card.com:80/play/ironnarule/galura_rule03.html 、https://web.archive.org/web/20020305235849/http://www.pokemon-card.com:80/play/ironnarule/galura_rule04.html |
| P19 | 公式サイト「バトルロード スプリング2002」: マスター・シニア・ジュニアトレーナーズリーグのレギュレーション（/event/sp2002_master.html ほか）、「レギュレーションに関するQ&A」（sp2002qa_regulation.html）、「トーナメントのチェックポイント」（sp2002_checkpoint.html）、「コーナーしょうかい」（sp2002_corner.html）、「追加・変更」（sp2002_tuika_henkou.html） | 2002-02-10〜2002-04-11 の写し。https://web.archive.org/web/20020210025450/http://www.pokemon-card.com:80/event/sp2002_master.html 、https://web.archive.org/web/20020210031032/http://www.pokemon-card.com:80/event/sp2002qa_regulation.html 、https://web.archive.org/web/20020210023029/http://www.pokemon-card.com:80/event/sp2002_checkpoint.html 、https://web.archive.org/web/20020411020409/http://www.pokemon-card.com:80/event/sp2002_corner.html 。チェックポイントからリンクされた詳しい説明（sub_sp2002_rule.html など）は保存されていない |
| P20 | 公式サイト「バトルロード サマー2002」: マスター・シニア・ジュニアトレーナーズリーグと予選リーグのレギュレーション（/event/summer2002/regu_master.html ほか。ページの日付 2002.5.1）、「コーナーしょうかい」（corner1.html・corner2.html） | 2002-06-11〜2002-08-09 の写し。https://web.archive.org/web/20020611025724/http://www.pokemon-card.com:80/event/summer2002/regu_master.html 、https://web.archive.org/web/20020809005812/http://www.pokemon-card.com:80/event/summer2002/regu_yosen.html 、https://web.archive.org/web/20020809005121/http://www.pokemon-card.com:80/event/summer2002/corner2.html |
| P21 | 公式サイトの『トレーナーズ』の発売告知（/hot/tre10.html・tre11.html・tre13.html）と、トップページの更新情報（/top.html） | Vol.13: 2001-10-16 の写し「全国書店・玩具店にて 2001年11月2日(金)発売」。Vol.11:「2001年5月25日(金)発売」。Vol.10:「2001年3月9日(金)発売」。トップページ（2001-10-24 の写し）: 「ポケモンカード★web」ポケモンセンターオンラインで10月20日より限定発売、更新情報「10/12 ポケモンカードトレーナーズVol.13 発売情報」「9/28 PCL公認『殿堂入りカード』リスト更新」。https://web.archive.org/web/20011016061859/http://www.pokemon-card.com:80/hot/tre13.html 、https://web.archive.org/web/20011024211606/http://pokemon-card.com:80/top.html |
| P22 | 公式サイト「サポーター」（/hot/play_supporter.html） | 2001-12-18 の写し。サポーターの説明とルール。https://web.archive.org/web/20011218055040/http://www.pokemon-card.com:80/hot/play_supporter.html |
| P23 | 公式サイト「プレイルール」（/play/officialrule/official_rule.txt） | 2002-01-19 の写し。スタンダードデッキ・ハーフデッキ・ミックスデッキ、特殊状態など。https://web.archive.org/web/20020119220950/http://www.pokemon-card.com:80/play/officialrule/official_rule.txt |
| P28 | 公式サイトの 2003年の大会のページ:「バトルロード スプリング2003」（/event/topics/sp2003.html。ページの日付 2003.2.28）、「バトルロード サマー２００３」公式トーナメント・レギュレーション（/event/summer2003_tournament.html）、「バトルロード オータム２００３」レギュレーション（/event/topics/autumn2003_regu.html。ページの日付 2003.9.26）、イベントレポート（/event/event_report/2003.html）、次世代ワールドホビーフェアの告知（/event/topics/w_h_f_17.html） | 2003-04-08・2003-05-26・2003-10-05・2004-04-21・2003-01-24 の写し。https://web.archive.org/web/20030408231042/http://www.pokemon-card.com:80/event/topics/sp2003.html 、https://web.archive.org/web/20030526080306/http://www.pokemon-card.com:80/event/summer2003_tournament.html 、https://web.archive.org/web/20031005061158/http://www.pokemon-card.com:80/event/topics/autumn2003_regu.html |

## 当時の印刷物（スキャンで誌面を確認）

当時の印刷物のページを、スキャン（会報・雑誌などは [J37] の PDF、[P43] は Internet Archive の [J38]、[P44] は Internet Archive の [J39]）で読んだものです。印刷物の実物を手に取って確かめたものではありません。号数・ページ・発行日は誌面の表示（表紙・ノンブル・奥付）で確かめました。

- 巻号ごと・ページごとの記録（PDF のページ番号、スキャンのファイルの URL、そのページを根拠にした `data/rule_history.json` の id）は [印刷物の照合記録](printed-sources.md) にあります（`data/rule_history.json` の `documents` から生成）。
- 雑誌の発行日（表紙・奥付）は、公式サイトが告知した発売日（[P21]）と違うことがあり、どちらも記録しています。『トレーナーズ』Vol.14 以降はファンクラブ会員限定誌（Vol.13 の奥付による）で、書店での発売日はありません。
- 初版と違う刷を確認したものは、その刷を書いています（[P29] は第4刷、[P30] は第3刷）。後の刷で文面が直された可能性があるので、初版の内容としては扱っていません。

| 記号 | 資料 | 発行日（確認した刷） |
|---|---|---|
| P29 | 『すぐわかるポケモンカードゲームの遊びかた』（メディアファクトリー） | 1996年11月30日初版（第4刷 1997年8月31日） |
| P30 | 『ポケモンカード・ファンクラブ』Vol.1 | 1997年6月5日初版（第3刷 1997年8月31日） |
| P35 | 『ポケモンカード・ファンクラブ』Vol.2 | 1997年9月5日発売（年表 [P34]。スキャンに奥付がなく、発行日・刷は未確認） |
| P31 | 『ポケモンカード・ファンクラブ』Vol.3 | 1997年11月18日 |
| P1 | 『ポケモンカード・ファンクラブ』Vol.4 | 1998年2月28日 |
| P2 | 『ポケモンカード・ファンクラブ』Vol.5 | 1998年6月10日 |
| P34 | 『めざせ! ポケモンカードマスター』（リザードンメガバトル公式ドキュメントブック。ルールの版の発表日を載せた年表がある） | 1998年10月20日 |
| P32 | 『ポケモンカード トレーナーズ』Vol.1 | 1999年5月28日 |
| P33 | 『トレーナーズ』Vol.2 | 1999年7月1日 |
| P36 | 『トレーナーズ』Vol.3 | 1999年9月1日 |
| P37 | 『トレーナーズ』Vol.4 | 1999年12月1日 |
| P38 | 『トレーナーズ』Vol.5 | 2000年3月1日 |
| P3 | 『トレーナーズ』Vol.6 | 2000年5月1日 |
| P39 | 『トレーナーズ』Vol.7 | 2000年7月1日 |
| P40 | 『トレーナーズ』Vol.8 | 2000年9月1日 |
| P41 | 『トレーナーズ』Vol.9 | 2000年12月1日（発行は株式会社ポケモン、販売はメディアファクトリー） |
| P4 | 『トレーナーズ』Vol.10 | 2001年3月1日（公式の発売日 3月9日 [P21]） |
| P13 | 『トレーナーズ』Vol.11 | 2001年5月1日（奥付。公式の発売日 5月25日 [P21]） |
| P5 | 『トレーナーズ』Vol.12 | 2001年7月1日 |
| P6 | 『トレーナーズ』Vol.13 | 2001年11月1日（公式の発売日 11月2日 [P21]。Bulbapedia [X55] は 2001年9月とする） |
| P7 | 『トレーナーズ』Vol.14 | 2002年1月5日 |
| P24 | 『トレーナーズ』Vol.15 | 2002年3月5日 |
| P8 | 『トレーナーズ』Vol.16 | 2002年5月5日 |
| P42 | 『トレーナーズ』Vol.17 | 2002年7月5日 |
| P25 | 『トレーナーズ』Vol.18 | 2002年9月5日 |
| P26 | 『トレーナーズ』Vol.19 | 2002年11月5日 |
| P9 | 『トレーナーズ』Vol.20 | 2003年1月5日 |
| P27 | 『トレーナーズ』Vol.21 | 2003年3月5日 |
| P43 | 『ポケモンカードオフィシャルブック2000』（メディアファクトリー。監修 クリーチャーズ。「公式ルール 2000.02.14版」とカードごとの「最新の説明」を収録。スキャンは [J38]） | 2000年2月29日初版第1刷（発売予定日 2000年2月18日 [P37]） |
| P44 | 『ポケットモンスター カードゲーム ルールブック第4版（ルール改訂あり）』（カードの大きさの冊子。制作 クリーチャーズ、発売元 メディアファクトリー。本文での自称は「遊び方説明書」。スキャンは [J39]） | 発行日・刷の表示なし（奥付は制作・発売元・著作権表示だけ）。本文が「ロケット団」と「ポケモンジム」シリーズにふれるので、1998年4月ごろ以降の刷とみられる（推定）。公式ルール第4版の発表日 1998年1月1日 [P34] と同じ内容かは未確認 |

同じ Drive のフォルダで、読めなかったもの・使わなかったもの:

- 「Silver Bible」（『ポケモンカード オフィシャルブック2000』とされる PDF。ファイルの id は 1_7qbNFKoU7ukyKY77KGqv6Aj2vRj_eAM）は、ビューアーがページの画像を返さず（3 回試して同じ。3 回目はページの情報の要求も 404）、読めませんでした。ファイルの直接のダウンロードは、上のとおりネットワーク制限で開けませんでした。同じ本は、のちに Internet Archive のスキャン [J38] で読みました（[P43]）。
- 「Rulebooks」のフォルダは韓国語版のルールブック（「Official Rulebook Ver 3.0」「Playmanual Ver 4」）だけで、日本語版のルールブックはありませんでした。
- 『ポケモンカード・ファンクラブ』Vol.2（P35）と『トレーナーズ』Vol.3〜5・7〜9・17（P36〜P42）は、2026年10月に全ページを読み、ルールの記事・Q&A・大会の規定を照合しました（ルールの記述がなかった範囲も [印刷物の照合記録](printed-sources.md) に書いています）。
- 『トレーナーズ』Vol.3 p.6 のシークレットスーパーバトル日本一決定戦のレギュレーション「タカハシの挑戦状」は、写真の字がつぶれていて読めませんでした（ビューアーの最大の解像度でも読めず、それ以上の解像度の要求は拒否された）。

## 当時の公式資料（原本は未確認）

ほかの資料が号数・ページを挙げて引用している、当時の公式資料です。このリポジトリの作成では原本を確認できていません。カッコ内は、その資料を引用している資料です。

| 記号 | 資料 | 内容・引用元 |
|---|---|---|
| P11 | 公式 PDF「『クラシックレギュレーション2016』及び、基本ルールの詳細」（2016年9月21日。後年の公式資料） | 2001年のバトル★ネオ サマーロードと同様の基本ルールとする（検索結果の要約）。https://www.pokemon-card.com/20th/assets/docs/classic-regulation.pdf |
| P12 | 公式サイト「詳しいレギュレーション」（2000年12月20日） | 検索結果に出たが本文は未確認。https://www.pokemon-card.com/info/2000/20001220_001586.html |
| P14 | 2001年夏のチャンピオンズリーグ、チャレンジパスポート（旧裏 wiki の記述による） | 殿堂の 2001.09版（[J1]）。なぞのばしょ [J23] には載っていない。同じ一覧は公式サイト [P15] の 2001-11-04 の写しで確認（チャンピオンズリーグ・チャレンジパスポートの原本は未確認） |

## カードテキストの出典

| 記号 | 資料 | URL |
|---|---|---|
| N1 | なぞのばしょ（旧裏カードの個別ページ。カード名・レベル・ワザ・特殊能力・効果文・収録商品・印刷上の備考を掲載） | https://nazonobasho.com/ （カードごとの URL は `data/cards.json` の `ja_text_source`） |
| N2 | ポケモンWiki（旧裏カードの個別ページ。ユーザーがブラウザで保存し、カード名・レベル・ワザ・特殊能力・説明文・レアリティ・収録シリーズを抜き出したもの。版 id 付き） | https://wiki.pokemonwiki.com/ （保存データは `data/raw/`、カードごとの URL は `data/cards.json` の `ja_text_source`） |
| N3 | ポケモンカード 旧シリーズ検索（pcg-search.com。旧裏の商品ごとのカードリストとカード個別ページ。拡張パック以外の商品の取り込みに使用。一部はカードの画像で確認） | https://pcg-search.com/card/card_list.php （カードごとの URL は `data/ja_text_pcgsearch.json` の `url`） |
| S1 | Scrydex 由来の日本版カードデータ（第三者のリポジトリにある写し。カード名・コスト・ダメージ・HP・にげる） | https://github.com/MarkHughes88/bindlr-prototype （`data/pokemon/raw/ja/expansions`） |

## カードリストのデータ

| データ | 用途 | URL |
|---|---|---|
| TCGdex cards-database（MIT ライセンス） | 日本版の収録構成・レアリティ | https://github.com/tcgdex/cards-database |
| PokemonTCG/pokemon-tcg-data | 英語版のカード情報 | https://github.com/PokemonTCG/pokemon-tcg-data |
| TCGdex cards-database の英語データ（`data/`） | 英語版データの欠落の確認と補正（ワザ・ポケモンパワー・トレーナーの効果文の有無を全件照合） | https://github.com/tcgdex/cards-database |
| PokeAPI | 日本語のポケモン名 | https://github.com/PokeAPI/pokeapi |
| Scrydex 由来の日本版カードデータ（第三者のリポジトリに置かれた写し） | 日本語カード名とレアリティの照合のみ。データ自体は収録していない | https://github.com/MarkHughes88/bindlr-prototype （`data/pokemon/raw/ja/expansions`） |

### カード名の照合結果

- **ポケモンのカード名**: 図鑑番号から組み立てた名前を、Scrydex 由来のデータの日本語名と全件照合しました。両データの不一致は 2 種類だけでした。
  - 「R団の」の表記: Scrydex 由来の名前に合わせました。
  - 数字の全角・半角
- **ポケモンのカード名となぞのばしょ**: なぞのばしょのカード名とも照合し、食い違いはサイトの誤記 3 件だけでした（トランセルのページが「キャタピー」、「ダクトリオ」、アンノーンD のページが「アンノーン[I]」）。
- **カード名とポケモンWiki**: 食い違いは 2 件で、どちらもサイトの転記の誤りと判定しました（「カツラのウィンディ」、空欄の長さが違う「_のラッキー」）。
- **トレーナー名の修正**: ポケモンWiki の表記に合わせて、闇からの挑戦の「キョウ秘伝 変わり身の術」を「キョウ秘伝,変わり身の術」にしました。
- **トレーナー・エネルギーのカード名**: 確度を `data/curation/trainers.json` の `confidence` に記録し、なぞのばしょのカード名と一致したものは確度を一段上げています（`data/cards.json` の `name_ja_confidence` が最終的な確度）。
  - ポケモンWiki のカード名と一致したものも同じく一段上げています。
  - **確実**（132 枚）: 互いに独立した 2 系統以上の出典で一致。
  - **有力**（21 枚）: 出典が 1 系統、または独立かどうか分からない 2 系統で一致。
  - **未確認**: 0 枚。以前は闇からの挑戦の「ロケット団の実験」が TCGdex にしかない名前でしたが、ポケモンWiki のカード名と一致して有力になりました。
  - なぞのばしょの表記に合わせて、第1弾の 3 枚を修正しました: 元気のかけら（TCGdex は「げんきのかけら」）、ポケモン図鑑 HANDY505（同「ポケモン図鑑」）、無色2個エネルギー（同「ダブル無色エネルギー」）。
- **レアリティ**: TCGdex と Scrydex 由来のデータで、ひかるポケモン 10 枚と、デルビル（闇、そして光へ...）の表記が食い違っています。カードリストの備考に記載しています。

## カードテキスト

- 英語版の名前と文面（ワザ・ポケモンパワー・トレーナー・特殊エネルギー）: PokemonTCG/pokemon-tcg-data（全件）。
  - 効果文の有無を TCGdex の英語データと全件照合しました。pokemon-tcg-data で効果文が欠けていたのは、ブラッキー（Neo Discovery 13）のだましうち（Feint Attack）だけでした。TCGdex の文面で補っています（`en_fixes.json`）。
  - 日本版にだけ効果文があるワザは、ほかにキョウのメタモン（Gym Challenge 10）のはたく（Pound）があります。これは欠落ではなく、英語版では同じ条件を Giant Growth の効果文に書いているためです [X38]（[カードの日英の違い](cards/card-differences.md)）。
- 日本版の名前と文面:
  - なぞのばしょ [N1]: 第1〜4弾、neo 第1〜2弾（410 枚）。
  - ポケモンWiki [N2]: 第5弾 リーダーズスタジアム、第6弾 闇からの挑戦、neo 第3弾 めざめる伝説、neo 第4弾 闇、そして光へ...（364 枚）。
  - 未収録は、無色2個エネルギーの効果文と、neo 第1〜2弾のベイビィ 6 枚・アンノーン 3 枚（M・U・A）のルール文だけ（なぞのばしょに記載がない。[詳細](cards/README.md#日本語テキストについて)）。アンノーンI・D・F のルール文は、2026-10-24 に pcg-search [N3]・なぞのばしょ [N1] のカードの画像で確かめて入れた（[アンノーンの調査](unown-research-v0.97.md)）。
- 日本版にしかないカード（イマクニ？のドードー、_____のラッキー など）は、英語版データがないため、HP・弱点・ワザなどもポケモンWiki の記載から埋めています（英語の欄は `null`）。
- なぞのばしょの記載と英語版データの食い違い 24 件の判定（`data/curation/nazonobasho_review.json`）。取り込みのときに、カード名・HP・ワザのコストとダメージ・にげるに加えて、タイプ・弱点・抵抗力も比べています（2026年10月から）。

  | 判定 | 件数 | 内容 |
  |---|---|---|
  | サイトの誤記 | 14 | Scrydex 由来の日本版データ [S1] が英語版と一致 |
  | サイトの誤記 | 9 | pcg-search のカードの画像 [N3] で、英語版と同じことを確認。タイプ 1 件（エアームド）、弱点 6 件（ゴーリキー、ナゾノクサ、クサイハナ、ラフレシア、わるいカメックス、アリゲイツ）、抵抗力 1 件（ブーバー）、にげる 1 件（ヤドキング） |
  | 英語版データの誤り | 1 | Neo Genesis のレディバ。Comet Punch のダメージ欄が空（`en_fixes.json` で 10× に補正） |

  - ヤドキング（neo 第1弾）のにげるコストは、以前は「日英で違う可能性」（日本版の 2 データで 1、英語版で 3）として、[カードの日英の違い](cards/card-differences.md) に**未確認**で載せていました。カードの画像では 3 で、なぞのばしょと Scrydex 由来のデータの両方の誤りでした。日英の違いの記録から外しました。
  - `data/cards.json` の数値は英語版データから入れているので、この 9 件の転記の誤りはカードのデータには入っていません。

- ポケモンWiki の数値・カード名と英語版データの食い違い 3 件の判定（`data/curation/pokemonwiki_review.json`）: 3 件ともサイトの転記の誤り。

  | カード | 欄 | 内容 |
  |---|---|---|
  | カツラのウインディ（闇からの挑戦） | カード名 | サイトの表記が「ウィンディ」 |
  | _____のラッキー（闇からの挑戦） | カード名 | サイトの表記が「_のラッキー」（空欄の長さ） |
  | アンノーンT（闇、そして光へ...） | ワザのコスト | サイトは「超」1 個。英語版データと Scrydex 由来の日本版データ [S1] は「超・無色」 |

- ポケモンWiki のトレーナーのページには、後年の再録版の説明文が併記されていることがあります。取り込んだ 73 枚は、すべて旧裏の版の説明文を選んでいることと、英語版と意味が対応することを確かめました。
- リーダーズスタジアムで、日英の文面の意味の違いが 4 枚見つかりました（[カードの日英の違い](cards/card-differences.md)）。エリカのピッピ・エネルギーサーキュレート・お上品攻撃の日本版の文面は、2026年10月に pcg-search のカードの画像 [N3] でも確認しました（それまではポケモンWiki の転記 1 系統だけでした）。
  - タケシのキュウコン: ばけるで、のせたカードのポケモンパワーを使えるか。日本版の当初の文面とエラッタについて [X37]。
  - エリカのピッピ: つきのちからで、自分自身も進化させられるか。
  - エネルギーサーキュレート: 手札にもどせるのが基本エネルギーだけか。
  - お上品攻撃: 手札にもどすのが自分の番の終わりか、相手の番の終わりか。
- 拡張パック以外の商品（拡張シート第1〜3弾、映画公開記念パック「サザンアイランド」、ポケモンジムの構築済みデッキ 6 種、クイックスターターギフト、イントロパック・イントロパック★neo、neo プレミアムファイル 1〜3、プロモ）の 681 枚は、pcg-search [N3] から取り込みました（`data/ja_text_pcgsearch.json`、[拡張パック以外の商品](cards/other-products.md)）。
  - サザンアイランドの 18 枚はなぞのばしょ [N1] の転記とも照合し、食い違いは 3 件（転記の誤り）でした。
  - 拡張パック 10 弾のデータ（`data/cards.json`）には入れていません。
- 商品をまたいだ同じカード（再録）の判定を点検しました（[再録カードの対応付け](cards/reprints.md)）。
  - 同じカードとした組の中の数値の食い違いは 1 件で、pcg-search の転記の誤り（ナツメのスリーパーの「20×」の「×」が落ちている。カードの画像で確認）。
  - イントロパックの 92 枚を Bulbapedia の同じカードへの転送 [X49][X50] と照合し、なぞのばしょのプリン（ポケモンジャングル）のワザ名の誤記を見つけて直しました（`data/curation/ja_text.json`）。
  - 『ポケモンカードオフィシャルブック2000』p.234 [P43] の画像で、なぞのばしょのベロリンガ（ポケモンジャングル。PMCG2-041）のワザ名（「したでなめる」→「まきつくベロ」）とレベル（29 → 26）の誤記を見つけて直しました（2026年10月。`data/curation/ja_text.json`。レベルの補正のために、`ja_text.json` に `jp_print` の欄を加えた）。kyuura-engine v0.17 の報告によるもので、照合の記録は `data/sidecar/card_checks.json` の CC-PMCG2-041-P234。
  - 全日空のそらをとぶピカチュウ 2 枚の配布時期の取り違えを直しました [X51]。
  - 再録の文面の比較から、エネルギー回収（第1弾）と超エネルギー回収（1997年のプロモ）の日英の違いが見つかりました（カードの画像で確認）。
  - 英語版の再録は、トレーナー・特殊エネルギーにも広げ、英語版データの誤記で見落としていた Legendary Collection の 2 枚を補いました（`en_fixes.json`）。
- 取得方法:
  - 旧裏 wiki（wikiwiki.jp）とポケモンWiki は、Cloudflare の自動アクセス防止で作成環境から取得できませんでした。回避はしていません。
  - ポケモンWiki のページは、ユーザーがブラウザで保存したもの（`data/raw/`）を使っています。
  - Bulbapedia は記事ページが Cloudflare の確認画面になるため、公開されている MediaWiki の API（`api.php` の `action=parse`）でウィキテキストを取得しました（2 秒間隔）。確認画面の回避はしていません。
  - Pokumon（X40）と Serebii（X39）は直接読めておらず、検索結果の要約によります。

## まだ確認できていないこと

- 日本のルールブック・遊びかた説明書の第1〜3版・第5版の原文（現物・画像）。第4版は冊子のスキャン [P44] で読んだ（2026年10月）
  - 第2〜5版の時期、第3版と第5版で変わった点は、当時の会報・雑誌・書籍のスキャン [P31][P32][P34] で確認した。第4版以外の版の文書そのものの文面は確認していない
  - 第2版・第4版で変わった点。第4版の冊子は表紙に「（ルール改訂あり）」とあるが、何を改訂したかは本文に書かれていない。第3版の変更 4 点 [P31] はすべて本文にあり、第3版になくて第4版で初めて入ったと確かめられる規定は見つからなかった（第3版の本文と比べられないため）
  - 読んだ冊子が、1998年1月1日に発表された公式ルール第4版 [P34] の最初の内容と同じか（冊子に発行日・刷の表示がなく、本文の商品の記述から 1998年4月ごろ以降の刷とみられる）
  - 第1版のサドンデス、第5版のサイドの枚数と対戦準備の細部、第4版以外の版の最初の番の進化の制限
  - 年表の「公式ルール第N版」と『トレーナーズ』Vol.1 の「ルールブック第5版」が同じ番号の系列か（第4版の冊子の表紙が「ルールブック第4版」なので、同じ系列とみる見方と合う）。neo（2000年）の「追加修正」[P38] がルールブックの何版にあたるか
  - 1999年秋〜2000年春と 2001年春の公式大会の先攻の最初のドローの扱い（2000年夏のワールドチャレンジは部門で逆だった [P39]。チャレンジロード'99 とメガバトル2000 の誌面の規定には書かれていない [P33][P38]）
- 『大人にもわかるポケモンカード戦略』（1997年3月20日発売）とその改訂版（1997年11月20日発売）の本文。
  - 発売日は、『オフィシャルブック2000』p.339 の書籍一覧（Elite Fourum に投稿された見本ページの画像）でも同じです。改訂版には第3版の「公式ルール」が載っていました [P31][P34]。『めざせ! ポケモンカードマスター』の年表の注は、改訂版を「「第1弾」から「化石の秘密」までのカードを掲載した」本で、「カードの正しい解釈が掲載されている」とし、編集はクリーチャーズとしています [P34]。
  - 公開されたスキャンも、図書館の所蔵の記録も見つかりませんでした（2026年10月。書店・図書館のサイトは作成環境から開けず、検索結果の要約による）。ISBN は初版 4-88991-427-7、改訂版 4-88991-486-2（書店の要約による）。
- 『ポケモンカードオフィシャルブック2000』[P43] のうち、まだ読んでいないページ（カードの解説の大部分、コラム、デッキ、年表など）。公式ルール（pp.306〜326）と、エラッタ・日英の違いにかかわるカードのページ、わるいカメールの「こうらがえし」にかかわるページは 2026年10月に Internet Archive のスキャン [J38] で読んだ（[印刷物の照合記録](printed-sources.md#p43)、[カードの裁定と公式の最新の説明](rules/card-rulings.md)）。
  - kyuura-engine（対戦処理の実装。別のリポジトリ）が v0.5〜v0.17 で照合した結果を取り込むときに、記録の根拠にするページは kyuura でも画像で読み直した（2026年10月。pp.13・14・16・45・47・48・49・55・82・87・88・90・138・149・151・153・155・158〜160・189〜193・229・245・265 と、公式ルールの pp.307・309〜312・319・320・322〜325。データの調査で pp.200・234）。サイドカー（`data/sidecar/`）の記録が根拠に挙げるページは、すべて kyuura で読んだページ。エンジンの照合の記録は調査の履歴として `data/sidecar/rulings.json` の `engine_refs` から参照するだけで、出典の記号は付けていない（原典の代わりにしない）。
  - エンジンの v0.5〜v0.12 の文書が関連として挙げるページのうち、次のページは kyuura ではまだ読んでいない: pp.8・18・20・21・24・52・67・70・98・100・113・129・148・150・152・157・186・188・206・213・235・248・256・261・277・285・298・361。ほかのカード（カスミのドククラゲ・タケシのキュウコン・レインボーエネルギーなど）の解説で、kyuura の記録の根拠には使っていない。v0.17 の文書が挙げる p.38（クサイハナ「ゆめみのまい」）・p.19（バタフリー）・p.164・p.58・p.34 も読んでいない。
  - 予告された「記述変更カードの解説」[P36][P37] という独立した章はなく、カードごとに「最新の説明」を載せる形になっていた。
- ルールブック・遊びかた説明書の現物について見つかったもの:
  - Internet Archive のスキャン [J39] は、表紙に「ルールブック第4版」「（ルール改訂あり）」と印刷された冊子 [P44] で、2026年10月に全ページを読んだ。Elite Fourum の写真 [X21] の冊子と表紙・クレジットのページ（p.77。ポケモンジムのスタッフを含む）が同じ。
  - Elite Fourum の写真 [X21] で、第3版のクレジットのページ（p.45）と、ネオのスターターパックの「遊びかた説明書 第1版」の奥付も見た（どちらも本文は未確認）。
  - 1996年の第1版と 1999年の第5版は、本文も写真も見つかりませんでした。
- WotC の Base Set ルールブック（1999年）の原文
  - マリガンの文言、コイン投げのタイミング
- 英語版での、どくのダメージ量・弱点抵抗力の計算順の明文（日本版は会報 Vol.1 [P30]・Vol.4 [P1] で確認）、両方の版での最初の番の進化の制限の明文
- 「イマクニ？のドードー」「_____のラッキー」が拡張パックに封入されていたか
- 遺跡の石版が絵柄違い 2 種だったか（TCGdex となぞのばしょは 2 種、Scrydex 由来のデータは 1 種として掲載）
- 無色2個エネルギーの効果文と、neo 第1〜2弾のベイビィ・アンノーン（M・U・A）のルール文の日本版の文面
- プラスパワーの変更（ベンチへのダメージに +10 しない）を、第1弾の版に使い始めた時期。会報 Vol.4 [P1]（1998年2月）は予告だけで、第1弾の版も新しい文面で使うと確認できる最初の資料は『オフィシャルブック2000』[P43]（2000年2月）。そのあいだの告知は、会報 Vol.2〜5、『トレーナーズ』Vol.1〜4 には見つからない
- タケシのキュウコンの変更（2000年5月の『トレーナーズ』Vol.6 [P3] で確認）より前の告知があったか（Vol.5 [P38] にはない。2000年2月の『オフィシャルブック2000』[P43] の「ばける」の説明には、まだ制限がない）
- なぞのばしょ・ポケモンWiki から取り込んだ効果文の誤字（数値以外は英語版と突き合わせていない。別の商品に再録のあるカードは、pcg-search の転記とワザ名が一致することを確かめた）
- 拡張パック以外の商品について未確認のこと（[一覧](cards/other-products.md#まだ確認できていないこと)）
- 2001〜2003年の旧裏・新裏の混合ルール、新ガルーラルール、旧裏カードの読み替え・エラッタの細部（[混合ルール](rules/mixed-2002.md#7-まだ確認できていないこと)、[新ガルーラルール](rules/kangaskhan-2002.md#open-questions)、`data/rule_history.json` の `open_questions`）
- 英語版の区分 Goldenrod Game Corner（カードめくりゲーム、スロットゲーム）の日本語の区分名。なぞのばしょの分類は「トレーナーカード」だけ
