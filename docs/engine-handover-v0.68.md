# kyuura-engine への引き継ぎ（v0.68 の参照から、2026-10-19）

kyuura の作業ブランチ `claude/non-pack-catalog-engine-findings-v0.68`（基準 `4b73536`）で行った変更のうち、エンジンの側の作業に関わることです。
エンジンの参照は kyuura-engine のブランチ `claude/v0.68-final-pmcg-cards`・コミット `24bfbe2c1bf3b5fb0521e229ac92cf2fa4a154a1` で、エンジンは変えていません。
エンジンの写しの元（`KYUURA_COMMIT` = `ecb2d69`）・研究の基準（`research_links.json` の `research_commit` = `3f34908`）は自動では更新しません。上げるかどうか・いつ上げるかはエンジンの側で決めてください。
作業の全体と数は [還元の記録](engine-findings-through-v0.68.md) にあります。

## 1. 新しいカード id

- `data/cards.json` は形式 3（`schema_version: 3`）。拡張パックの 780 件（`PMCG1-001`〜`neo4-113`）の id は変わらず、拡張パック以外の商品の記録 597 件を加えました。
- 新しい id は「商品の記号-カードページ名の末尾 3 桁」（例 `GD1-009`・`IP1-023`・`PR1-038`・`PRN-030`）。商品の記号の一覧は `data/curation/non_pack.json` の `products`、ページ ↔ id の対応は `data/product_items.json` の `items`、記録の `source_ids.pcg_search` です。サイトの並び順には依りません。
- 記録の形は拡張パックと同じです（`category`・`name`・`pokemon`・`trainer`・`energy`・`jp_print` など）。形式 3 で全記録に `product_group`・`play_scope`・`same_card_group`・`data_gaps`・`source_ids.pcg_search` を加え、拡張パック以外の記録には `copies`・`field_sources` があります。`corrections` は訂正のあった記録だけです。
- エンジンの `FIELDS_USED_BY_ENGINE` の欄は、拡張パック以外の記録でも同じ意味です。ただし次の点に注意してください。
  - 日本語の文面は pcg-search.com の転記です。`card_sources.json` の方針どおり、同じサイトとの比較は独立した照合になりません。
  - 進化元は `field_sources["pokemon.evolves_from"]` が `same_card:<拡張パックの id>`（同じカードの拡張パックの記録）か `pcg_search_evolution_line`（サイトの進化ライン）です。値がない記録は `data_gaps` に `pokemon.evolves_from` があります（9 件）。段階がサイトの中で食い違う 2 件（GD3-003・PRN-030）は `data_gaps` に `pokemon.stage` があります。
  - にげるの 0 は、読み直したページの「-」で確かめたもの（`pcg_search_page_dash`）です。
  - `play_scope` が `standard` でない 4 件（ガルーラルール専用・公式大会で使えないと書かれたカード）は、通常の対戦の対象に入れるかをエンジンの側で決めてください。
  - レベル（`jp_print.level`）は pcg-search にないので、拡張パック以外の記録の多く（423 件）で空です。

## 2. 取り出し方

- `scripts/extract_kyuura_cards.py` はカード id の組（`POOL_V0_*`）で取り出すので、新しい id は組に加えない限り写しに入りません。形式 3 の新しい欄は `FIELDS` にないので写しには入りません（入れる必要があれば `FIELDS` に加え、写しの形式の変更として扱ってください）。
- `source.schema_version` は 2 から 3 になります（写しの `source.schema_version` が変わる）。
- 実装の対象の選び方は [エンジンの実装の対象](engine-targets.md)・`data/engine_targets.json` を使えます。
  - `mechanically_equivalent`（96 件）: エンジンが使う欄と、ワザ・特殊能力・トレーナー・特殊エネルギーの名前と説明が、v0.68 の登録が照合した文面（`text_ja`）と同じ記録。`equivalent_to` の登録を同じ id に加えるだけで照合が通る見込みですが、最新の説明・エラッタが同じように当てはまるかはエンジンで確かめてください（実装済みとは数えていません）。
  - `reuse_candidate`（210 件）: 同じカードの組に登録があって欄の一部が違うもの（`nearest_registered` の `differences`）か、効果の文面がどれも登録された実装の文面と同じもの（`effects_with_registered_text`）。
  - `new_effect_needed`（614 件）: 登録された実装と同じ文面のない効果（`effects_without_registered_text`）があるもの。
  - `category` が `data_missing`（30 件）・`special_rule_design`（4 件）の記録は、データかルールの設計を先に決める必要があります。`released_after_rule_base` は発売日が 2000.02.14 より後か（ルールの版の判断用。対象から外すものではありません）。
- エンジンの版を上げたら、kyuura の側で `python3 -I scripts/snapshot_engine_registry.py --engine <木> --commit <コミット> …` と `python3 scripts/build_engine_targets.py` を作り直します（自動では更新しません）。

## 3. 研究の対応表（`research_links.json`）の変更

研究の基準をこの作業のコミット以降に上げるときに、対応表を次のように更新できます。

- **停止コード**: 研究の対応表で `kyuura_disposition: not_in_kyuura` だった 123 件は、すべて kyuura の論点に結ばれています（v0.26〜v0.68 の停止コードはこの作業で結んだ。2026-10-19 に確かめた）（`data/sidecar/rulings.json` の `engine_unresolved_index`。`stop_code` → `kyuura_issue`）。新しい論点 47 件のほか、HC3 → UQ-COIN-IN-NULLIFIED-ELEMENT、TS1 → UQ-TRANSPARENCY-COIN-ORDER、MH1・DV1 → UQ-EVOLUTION-HP-BELOW-DAMAGE、DR8・DR13 → 既存の UQ-ENERGY-DRAIN-ATTACKER-KO・UQ-ENERGY-DRAIN-NO-ENERGY（kyuura ではすでに論点。エンジンの報告事項 3 の「まだない」は研究の基準 `3f34908` の時点のこと）。v0.21〜v0.23 の GW5・CS6・ER9・ER10 も、v0.25 までの取り込みで kyuura の論点になっています。一覧は [カードの裁定と公式の最新の説明](rules/card-rulings.md) の 8 章です。
- **コードのない問い**: SS1 → UQ-SPEED-STAR-SCOPE、ED1 → UQ-COPIED-ATTACK、FL0・BG0 → UQ-REACTIVE-SWITCH-DURING-ATTACK、ES0 → UQ-ESP-REDO（FL0・BG0・ES0 はエンジンが数えないので `in_engine_count: false`）。
- **同じ問いにまとめた論点**: kyuura は、同じ形の問い（使えないと書かれていないカードを対象のないときに使えるか、など）をカードをまたいで 1 つの論点にまとめ、エンジンの id を事例（`cases`）に残しました。カードごとに答えが同じとは限らないので、エンジンの停止コードを 1 つにまとめる必要はありません（停止コード ↔ 論点は多対 1）。
- **採用した仕様**: DR1・DR6（・DR12）は `implementation_assumptions_with_issue` のまま、kyuura では `engine_positions` の ENG-V068-ENERGY-DRAIN-ADOPTED-SPEC に記録しました。kyuura の論点 UQ-ENERGY-DRAIN-DECLARATION・UQ-ENERGY-DRAIN-TIMING は UNRESOLVED のままです。
- **実装の事項・簡略化**: マチスの秘策の受け付けの不具合と組の上限は ENG-V068-SECRET-MANEUVER-IDENTITY、イマクニ？のドードーの簡略化は ENG-V068-IMAKUNI-DODUO-SIMPLIFIED です。研究の対応表の停止コードには入れないでください（公式の未解決の裁定ではない）。
- **既存の項目の停止コード**: kyuura がコードのない問いとして取り込んだ T27・C34/C35・G40・P19・P32（v0.31 の文書で停止コードが見える）・Z9（v0.61）・DR8・DR13（v0.68）に停止コードを書き、`stop_code_since` に版を書きました。
- **照合の記録**: v0.27・v0.28 の 11 枚（`card_verification.json`）は、kyuura の CC-・LD- になりました（`card_checks`・`latest_descriptions` の対応に加えられます）。最新の説明の id は LD-PMCG2-017-ATK0・LD-PMCG1-026-ATK0・LD-PMCG2-006-ATK1・LD-PMCG1-068-ATK0・LD-PMCG3-012-ATK1・LD-PMCG3-022-ATK0。

## 4. 写しの元を上げるときの手順

1. kyuura のこの作業のコミット（またはそれ以降）を、`KYUURA_COMMIT` の候補にする。
2. `CONFIRMED_CORRECTIONS`（PMCG2-041）: kyuura のデータにすでに反映されているので、写しの元を上げると「写しの元の値が `before`」の確かめが通らなくなります。修正の記録を外し、kyuura の訂正の記録（`data/curation/card_corrections.json` の FIX-PMCG2-041-ATK0-NAME・FIX-PMCG2-041-LEVEL）を参照する形にしてください。
3. `USER_PROVIDED_CORRECTIONS`（PMCG2-046）: kyuura のデータを同じ欄・同じ前後で直しました（FIX-PMCG2-046-ATK0-TEXT。`basis: user_provided`。kyuura も画像を見ていない）。写しの元を上げると `user_correction_problems` の「写しの元の値が `before`」が通らなくなるので、エンジンの補正を外し、kyuura の訂正の記録を出典にしてください。`card_sources.json` の PMCG2-046 の `basis`（`user_provided_correction`）は、kyuura の訂正の記録の id に置きかえられます。
4. 写しの元 `ecb2d69` から値の変わった拡張パックの記録（形式 3 の欄を除く。2026-10-19 に比べた）: PMCG2-041（ワザ 1 の名前・レベル・`ja_text_source`・`notes`）、PMCG2-046（ワザ 1 の説明・`notes`）、PMCG6-023（`jp_en_differences`。エンジンは使わない欄）の 3 枚だけです。拡張パック以外の記録はエンジンの組にありません。`scripts/extract_kyuura_cards.py` の書き出しを作り直し、変わった欄に対応するテストと文書を見直してください。
5. `research_links.json` の `research_commit` を上げ、3 章の対応（`kyuura_disposition`・`kyuura_issue`）を更新する。
6. 訂正の候補（`data/curation/card_corrections.json` の `candidates`）は kyuura のデータを直していません。エンジンの `card_sources.json` の違い（87 件）は、kyuura では `held_transcription_difference` です。わるいカメックス（PMCG4-024）のハイドロキャノンの「エネルギーがいている時」は、誤りの可能性が高いが印刷で確かめていない（`held_likely_transcription_error`）ので、直していません。

## 5. kyuura の側で変えなかったこと

- エンジンのリポジトリ・写し・研究の基準・固定の参照データ（`compat_base_4bd97bf.json` など）。
- 印刷の文面（イマクニ？のドードーの文面など）。エンジンの採用・簡略化はカードデータに反映していません。
- 公式の裁定の分類（CONFIRMED・SUPPORTED）。エンジンが CONFIRMED・SUPPORTED とした v0.26〜v0.68 のカードごとの当てはめは、kyuura の新しい裁定にしていません（理由つきで `not_imported`）。
