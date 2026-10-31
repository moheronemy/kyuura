#!/usr/bin/env python3
"""kyuura-engine の固定した版から、カードの効果の登録表と対戦用のカード id を data/curation/engine_registered_cards.json に写す。

エンジンの木（git archive などで展開した、決まったコミットの木）を読み取るだけで、エンジンは変えない。
エンジンのコードを読み込んで実行するので、信頼できるエンジンの木だけに使う（`python3 -I` で、作業ディレクトリのファイルを読み込まない）。

使い方（kyuura の直下で）:
  git -C ../kyuura-engine archive 24bfbe2c1bf3b5fb0521e229ac92cf2fa4a154a1 | tar -x -C /tmp/eng068
  python3 -I scripts/snapshot_engine_registry.py --engine /tmp/eng068 --commit 24bfbe2c1bf3b5fb0521e229ac92cf2fa4a154a1 \
      --branch claude/v0.68-final-pmcg-cards --version v0.68 --extracted-on 2026-10-19

写すもの:
  - playable: エンジンの kyuura_engine.cards.load_card_pool().playable_ids（エンジンの分類で対戦に使えるカード）
  - cards: kyuura_engine.effects.DEFAULT_EFFECTS の登録（ワザ・トレーナー・ポケモンパワー・特殊エネルギー）。implementation は実装のクラス名、
    text_ja は登録のときにエンジンが照合した kyuura の写しの文面、play_text_ja・source はエンジンが従う文面と出典（エンジンの採用で、kyuura の裁定ではない）
エンジンの版を上げるときは、新しい版の木で作り直し、scripts/build_engine_targets.py で data/engine_targets.json を作り直す（自動では更新しない）。
前の写しの参照（版・コミット・取得日・件数）は previous_snapshots に残す（前の写しの登録の中身は git の履歴にある。前の版の時点の取得日や件数を、
新しい版の値で書きかえない）。同じコミットで作り直したときは previous_snapshots を変えない。
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'curation' / 'engine_registered_cards.json'


def entry(e, index=None):
    out = {} if index is None else {'index': index}
    out.update({'name_ja': e.name_ja, 'implementation': type(e.effect).__name__, 'text_ja': e.text_ja,
                'play_text_ja': e.play_text_ja, 'source': e.source})
    return out


def snapshot(engine):
    sys.path.insert(0, str(engine))
    from kyuura_engine import cards as engine_cards
    from kyuura_engine.effects import DEFAULT_EFFECTS as R
    pool = engine_cards.load_card_pool()
    out = {}
    for k in R.attack_keys():
        out.setdefault(k.card_id, {}).setdefault('attacks', []).append(entry(R.attack_entry(k.card_id, k.attack_index), k.attack_index))
    for cid in R.trainer_ids():
        out.setdefault(cid, {})['trainer'] = entry(R.trainer_entry(cid))
    for k in sorted(R._powers):
        out.setdefault(k.card_id, {}).setdefault('powers', []).append(entry(R._powers[k], k.power_index))
    for cid in sorted(R._energies):
        out.setdefault(cid, {})['energy'] = entry(R._energies[cid])
    counts = {'attacks': len(R._attacks), 'trainers': len(R._trainers), 'powers': len(R._powers), 'energies': len(R._energies),
              'playable_cards': len(pool.playable_ids), 'cards_with_registrations': len(out)}
    copied = pool.source.get('commit') if hasattr(pool.source, 'get') else None
    return R.id, counts, sorted(pool.playable_ids), dict(sorted(out.items())), copied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', type=Path, required=True, help='エンジンの木（決まったコミットを展開したもの）')
    ap.add_argument('--commit', required=True)
    ap.add_argument('--branch', required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--extracted-on', required=True)
    ap.add_argument('--out', type=Path, default=OUT)
    args = ap.parse_args()
    registry_id, counts, playable, cards, copied = snapshot(args.engine)
    previous = []
    if args.out.exists():
        old = json.loads(args.out.read_text(encoding='utf-8'))
        previous = old.get('previous_snapshots', [])
        if old['engine']['commit'] != args.commit:
            previous = [{'engine': old['engine'], 'extracted_on': old['extracted_on'], 'registry_id': old['registry_id'],
                         'counts': old['counts'], 'replaced_on': args.extracted_on}] + previous
    doc = {
        '_comment': 'kyuura-engine の固定した版の、カードの効果の登録表（effects.py の DEFAULT_EFFECTS）と対戦用のカード id の写し。'
                    'scripts/build_engine_targets.py が、記録とエンジンの登録の対応を調べるのに使う。エンジンの実装の記録で、kyuura の裁定・原典の照合ではない'
                    '（play_text_ja・source はエンジンが従う文面とその出典）。手で編集しない。エンジンの版を上げるときは scripts/snapshot_engine_registry.py で作り直す'
                    '（自動では更新しない）。',
        'engine': {'repository': 'https://github.com/moheronemy/kyuura-engine', 'branch': args.branch, 'commit': args.commit,
                   'version': args.version, 'kyuura_commit_copied_by_engine': copied},
        'extracted_on': args.extracted_on,
        'how': 'scripts/snapshot_engine_registry.py。playable は kyuura_engine.cards.load_card_pool().playable_ids、cards は '
               'kyuura_engine.effects.DEFAULT_EFFECTS の登録。implementation は実装のクラス名。text_ja は登録したときにエンジンが照合した kyuura の写しの文面'
               '（写しの元のコミットの値に、エンジンの補正 CONFIRMED_CORRECTIONS・USER_PROVIDED_CORRECTIONS を当てはめたもの）',
        'registry_id': registry_id,
        'counts': counts,
        'previous_snapshots': previous,
        'playable': playable,
        'cards': cards,
    }
    args.out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(registry_id, counts, file=sys.stderr)


if __name__ == '__main__':
    main()
