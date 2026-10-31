#!/usr/bin/env python3
"""公式図鑑の種族の身長（全国図鑑 No.001〜251）の収集・検査（2026-10-31〜）。

「カツラのクイズ その1」（GD5-016 ほか）の実装の準備として、公式に公開されている図鑑の
「種族の身長」を、カードデータ（data/cards.json）とは別の参照データ data/species_heights.json に集める。

- 集めるのは公式図鑑の種族の身長で、旧裏カードに印刷された身長ではない。カードの欄を補完・訂正しない。
- 公式図鑑の値をクイズの正解に採るかは、エンジンの仕様として別に決める（docs/engine-handover-species-heights.md）。
- 出典は公式のものだけ（SOURCES）。PokeAPI・ファンWiki・第三者の転載は使わない。取得できない番号は
  未確認（status "unverified"）のまま残し、0cm や推測の値で埋めない。
- 画像は取得しない。取得したページは --cache の作業用のディレクトリに置き（リポジトリに入れない）、
  リポジトリには再確認に要る最小限の抜き出し（名前・姿・身長の原表記）と、応答の sha256・バイト数だけを残す。

使いかた（リポジトリの直下で）:

    python3 scripts/species_heights.py init                     # 251 件の未確認の枠を作る（既存の観測があれば止まる）
    python3 scripts/species_heights.py fetch --cache DIR --dex 1,25,201        # まず少数件（試し取り）
    python3 scripts/species_heights.py extract --cache DIR --dex 1,25,201 --retrieved-on YYYY-MM-DD
    python3 scripts/species_heights.py fetch --cache DIR --range 1-251 --full-range   # 試し取りを確かめたあと
    python3 scripts/species_heights.py record-access --source SRC-ZUKAN-JP --date YYYY-MM-DD --result blocked --detail "..."
    python3 scripts/species_heights.py --check [--cache DIR]    # 検査（--cache があれば保存した応答と抜き出しも照らす）
    python3 scripts/species_heights.py report                   # 件数（取得済み・未確認・食い違い）とカードとの対応

標準ライブラリだけを使う。
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'species_heights.json'
CARDS = ROOT / 'data' / 'cards.json'

DEX_FIRST, DEX_LAST = 1, 251
SCHEMA_VERSION = 1
STATUSES = ('unverified', 'confirmed', 'conflict', 'needs_review')
USER_AGENT = 'kyuura-research/1.0 (+https://github.com/moheronemy/kyuura; species height reference, low rate)'
DEFAULT_INTERVAL = 5.0  # 秒。1 件ごとの間隔（これより短くしない）
MIN_INTERVAL = 3.0

# 公式の出典だけをここに置く。ここにない出典の観測は --check がエラーにする。
SOURCES = {
    'SRC-ZUKAN-JP': {
        'name_ja': 'ポケモンずかん（ポケモン公式サイト）',
        'publisher': '株式会社ポケモン',
        'official': True,
        'base_url': 'https://zukan.pokemon.co.jp/',
        'detail_url': 'https://zukan.pokemon.co.jp/detail/{dex:04d}',
        'robots_url': 'https://zukan.pokemon.co.jp/robots.txt',
        'height_unit': 'm',
        'parser': 'zukan_jp_json_data',
    },
}

# 使わない出典（公式情報として扱わない）。記録のために名前を残す。
EXCLUDED_SOURCES = [
    {'name': 'PokeAPI', 'reason': '第三者の構造化データ（公式ではない）'},
    {'name': 'ポケモンWiki・Bulbapedia・Serebii などのファンサイト', 'reason': '第三者の転載・編集（公式ではない）'},
    {'name': 'ウェブアーカイブの保存版（web.archive.org）',
     'reason': '2026-10-31 は、公式サイトへの接続が拒否された代わりにアーカイブから取る経路を使わなかった（環境の制限の回避になるため）。'
               '保存版を使うかは、利用者が出典の扱いを決めてから'},
    {'name': 'ポケモンカードゲーム公式サイト（www.pokemon-card.com）のカード検索',
     'reason': 'カードに印刷された値で、公式図鑑の種族の値ではない（集める値の位置づけが違う）'},
    {'name': 'カードの画像・OCR', 'reason': '依頼の範囲の外（カードの印刷欄を読まない）'},
]

FORM_POLICY = ('当時（第1・第2世代）に対応する通常の姿だけを採る。公式ずかんの detail/{番号4桁}（姿の番号 sub 0）を基本にし、'
               '抜き出した姿の名前が空でなければ needs_review にする。リージョンフォーム・メガシンカ・キョダイマックス・'
               '後世の姿・性別の違いの別項目は採らない。アンノーン（No.201）の文字の違いは、sub 0 の姿を記録し、'
               'ほかの文字の姿は集めない（同じ値かは確かめていない）')


# ---------------------------------------------------------------- 正規化

_HEIGHT_RE = re.compile(r'^\s*([0-9]+(?:\.[0-9]+)?)\s*(m|ｍ|cm|ｃｍ)\s*$')


def normalize_height_cm(raw: str) -> int:
    """身長の原表記（例 "0.7m"・"8.8 m"・"70cm"）を整数 cm にする。

    小数は Decimal で扱い、整数 cm にならない値・0 以下・単位のない値は ValueError。
    丸めない（丸めが要る表記は原表記を残して人が確かめる）。
    """
    if not isinstance(raw, str):
        raise ValueError(f'身長の原表記が文字列でない: {raw!r}')
    m = _HEIGHT_RE.match(raw)
    if not m:
        raise ValueError(f'身長の原表記を読めない: {raw!r}')
    try:
        value = Decimal(m.group(1))
    except InvalidOperation as e:  # pragma: no cover - 正規表現で数字に限っている
        raise ValueError(f'身長の数を読めない: {raw!r}') from e
    unit = m.group(2)
    cm = value * 100 if unit in ('m', 'ｍ') else value
    if cm != cm.to_integral_value():
        raise ValueError(f'整数 cm にならない: {raw!r} → {cm} cm')
    cm = int(cm)
    if cm <= 0:
        raise ValueError(f'身長が 0 以下: {raw!r}')
    return cm


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_json(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


# ---------------------------------------------------------------- 抜き出し

class ParseError(ValueError):
    pass


_JSON_DATA_RE = re.compile(r'<script[^>]*\bid=["\']json-data["\'][^>]*>(.*?)</script>', re.S | re.I)


def parse_zukan_jp(body: bytes) -> dict:
    """公式ポケモンずかんの詳細ページから、名前・姿・身長の原表記を抜き出す。

    ページに埋めこまれた JSON（<script id="json-data">）の pokemon の項目
    （no・sub・name・takasa、姿の名前は sub_name か form_name）を読む。
    この形は 2026-10-31 の時点で実際のページと照らしていない（接続できなかった）。
    形が違えば ParseError で止まり、値を推測しない（試し取りで形を確かめてから全件に広げる）。
    """
    text = body.decode('utf-8')
    m = _JSON_DATA_RE.search(text)
    if not m:
        raise ParseError('json-data の script がない')
    try:
        data = json.loads(html.unescape(m.group(1)).strip())
    except json.JSONDecodeError as e:
        raise ParseError(f'json-data が JSON でない: {e}') from e
    p = data.get('pokemon') if isinstance(data, dict) else None
    if not isinstance(p, dict):
        raise ParseError('json-data に pokemon の項目がない')
    missing = [k for k in ('no', 'name', 'takasa') if k not in p]
    if missing:
        raise ParseError(f'pokemon の項目が足りない: {missing}')
    try:
        no = int(str(p['no']))
    except ValueError as e:
        raise ParseError(f'no が数でない: {p["no"]!r}') from e
    sub_raw = p.get('sub', 0)
    try:
        sub = int(str(sub_raw)) if sub_raw not in (None, '') else 0
    except ValueError as e:
        raise ParseError(f'sub が数でない: {sub_raw!r}') from e
    form_name = p.get('sub_name', p.get('form_name')) or ''
    name = str(p['name']).strip()
    takasa = str(p['takasa']).strip()
    if not name or not takasa:
        raise ParseError('name か takasa が空')
    return {'no': no, 'sub': sub, 'name': name, 'form_name': str(form_name).strip(), 'takasa': takasa}


PARSERS = {'zukan_jp_json_data': parse_zukan_jp}


# ---------------------------------------------------------------- データ

def blank_entry(dex: int) -> dict:
    return {
        'dex': dex,
        'name_ja': None,
        'form': {'kind': 'default', 'source_form_id': None, 'form_name': None},
        'height': {'raw': None, 'cm': None, 'source': None},
        'status': 'unverified',
        'status_reason': 'not_collected',
        'observations': [],
    }


def skeleton() -> dict:
    return {
        'schema_version': SCHEMA_VERSION,
        'description': ('公式図鑑の種族の身長（全国図鑑 No.001〜251・当時に対応する通常の姿）。カードに印刷された身長ではない。'
                        'カードとは全国図鑑番号（data/cards.json の pokemon.dex）で対応づける。'
                        'クイズの正解にどの値を使うかはエンジンの仕様として別に決める。'),
        'scope': {'dex_first': DEX_FIRST, 'dex_last': DEX_LAST, 'form_policy': FORM_POLICY},
        'status_values': {
            'unverified': '公式の資料から取得できていない（height・name_ja は null。0 にしない）',
            'confirmed': '公式の資料の観測が 1 件以上あり、身長・名前・姿がすべて一致する',
            'conflict': '公式の資料の観測どうしで身長が違う（height は null、すべての観測を残す）',
            'needs_review': '観測はあるが、姿の名前がある・名前がカードの記録と合わないなど、人の確認が要る（height は null）',
        },
        'sources': {k: {kk: vv for kk, vv in v.items() if kk != 'parser'} | {'access_log': []}
                    for k, v in SOURCES.items()},
        'excluded_sources': EXCLUDED_SOURCES,
        'species': [blank_entry(d) for d in range(DEX_FIRST, DEX_LAST + 1)],
    }


def load_data(path: Path = DATA) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def dump_data(data: dict, path: Path = DATA) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def species_index(data: dict) -> dict:
    return {e['dex']: e for e in data['species']}


def resolve_status(entry: dict, card_names: dict | None = None) -> None:
    """観測から status・name_ja・form・height を決め直す（観測だけが根拠。観測がなければ未確認）。"""
    obs = entry['observations']
    entry['name_ja'] = None
    entry['form'] = {'kind': 'default', 'source_form_id': None, 'form_name': None}
    entry['height'] = {'raw': None, 'cm': None, 'source': None}
    if not obs:
        entry['status'] = 'unverified'
        if entry.get('status_reason') in (None, '', 'conflicting_official_values', 'needs_review'):
            entry['status_reason'] = 'not_collected'
        return
    cms = {o['cm'] for o in obs}
    names = {o['name_ja'] for o in obs}
    if len(cms) > 1:
        entry['status'] = 'conflict'
        entry['status_reason'] = 'conflicting_official_values'
        return
    reasons = []
    if len(names) > 1:
        reasons.append('official_names_differ')
    if any(o.get('form_name') for o in obs):
        reasons.append('form_name_present')
    if any(o.get('source_form_id') not in (0, None) for o in obs):
        reasons.append('non_default_form_id')
    if card_names is not None:
        cn = card_names.get(entry['dex'], set())
        name = next(iter(names))
        if cn and not any(name in n for n in cn):
            reasons.append('name_not_in_kyuura_card_names')
    if reasons:
        entry['status'] = 'needs_review'
        entry['status_reason'] = ','.join(reasons)
        return
    o = obs[0]
    entry['status'] = 'confirmed'
    entry['status_reason'] = None
    entry['name_ja'] = o['name_ja']
    entry['form'] = {'kind': 'default', 'source_form_id': o.get('source_form_id'), 'form_name': o.get('form_name') or None}
    entry['height'] = {'raw': o['raw_height'], 'cm': o['cm'], 'source': o['source']}


def make_observation(source_id: str, dex: int, url: str, retrieved_on: str, body: bytes) -> dict:
    """保存した応答から観測を 1 件作る。抜き出せなければ ParseError、番号が違えば ValueError。"""
    src = SOURCES[source_id]
    ext = PARSERS[src['parser']](body)
    if ext['no'] != dex:
        raise ValueError(f'No.{dex:03d} のページの番号が {ext["no"]}')
    cm = normalize_height_cm(ext['takasa'])
    return {
        'source': source_id,
        'url': url,
        'retrieved_on': retrieved_on,
        'name_ja': ext['name'],
        'source_form_id': ext['sub'],
        'form_name': ext['form_name'] or None,
        'raw_height': ext['takasa'],
        'cm': cm,
        'extract': ext,
        'extract_sha256': sha256_bytes(canonical_json(ext)),
        'response_sha256': sha256_bytes(body),
        'response_bytes': len(body),
    }


# ---------------------------------------------------------------- カードとの対応

def card_names_by_dex(cards: list) -> dict:
    """図鑑番号 → kyuura のカード名の集合（名前の確認にだけ使う。名前の出典にはしない）。"""
    out: dict = {}
    for c in cards:
        p = c.get('pokemon')
        if not p:
            continue
        for d in p.get('dex') or []:
            out.setdefault(d, set()).add(c['name']['ja'])
    return out


def species_for_card(card: dict, data: dict) -> list:
    """カードの種族の参照データを、カードの pokemon.dex（全国図鑑番号）だけで引く。

    dex のないカードは空のリスト（名前の文字列から推測しない。所有者名つきカードも同じ）。
    """
    p = card.get('pokemon')
    if not p or not p.get('dex'):
        return []
    idx = species_index(data)
    return [idx[d] for d in p['dex'] if d in idx]


def link_report(cards: list, data: dict) -> dict:
    pokemon = [c for c in cards if c.get('pokemon')]
    linked = [c for c in pokemon if species_for_card(c, data)]
    no_dex = [c['id'] for c in pokemon if not c['pokemon'].get('dex')]
    out_of_range = sorted({d for c in pokemon for d in (c['pokemon'].get('dex') or [])
                           if not DEX_FIRST <= d <= DEX_LAST})
    idx = species_index(data)
    linked_status = Counter(idx[d]['status'] for c in linked for d in c['pokemon']['dex'])
    return {'pokemon_cards': len(pokemon), 'linked_by_dex': len(linked), 'without_dex': len(no_dex),
            'without_dex_ids': no_dex, 'dex_out_of_range': out_of_range,
            'linked_card_species_status': dict(linked_status)}


# ---------------------------------------------------------------- 検査

def check_data(data: dict, cards: list | None = None, cache: Path | None = None) -> list:
    """データの検査。問題の文のリストを返す（空なら合格）。"""
    errs = []
    if data.get('schema_version') != SCHEMA_VERSION:
        errs.append(f'schema_version が {SCHEMA_VERSION} でない')
    sp = data.get('species')
    if not isinstance(sp, list):
        return errs + ['species がリストでない']
    dexes = [e.get('dex') for e in sp]
    dup = sorted(d for d, n in Counter(dexes).items() if n > 1)
    if dup:
        errs.append(f'番号の重複: {dup}')
    expected = set(range(DEX_FIRST, DEX_LAST + 1))
    missing = sorted(expected - set(dexes))
    extra = sorted(d for d in set(dexes) - expected if d is not None)
    if missing:
        errs.append(f'番号の欠け: {missing}')
    if extra or None in dexes:
        errs.append(f'範囲の外の番号: {extra or [None]}')
    if dexes != sorted(dexes):
        errs.append('species が番号の順でない')
    if set(data.get('sources', {})) - set(SOURCES):
        errs.append(f'登録のない出典: {sorted(set(data["sources"]) - set(SOURCES))}')
    for k, v in data.get('sources', {}).items():
        if not v.get('official'):
            errs.append(f'{k}: 公式の出典でない')
        for a in v.get('access_log', []):
            if not {'date', 'result', 'detail'} <= set(a):
                errs.append(f'{k}: access_log の項目が足りない: {a}')
    cn = card_names_by_dex(cards) if cards is not None else None
    for e in sp:
        d = e.get('dex')
        tag = f'No.{d:03d}' if isinstance(d, int) else f'No.{d}'
        st = e.get('status')
        if st not in STATUSES:
            errs.append(f'{tag}: status が不正: {st!r}')
            continue
        h = e.get('height') or {}
        if st != 'confirmed':
            if h.get('cm') is not None or h.get('raw') is not None or e.get('name_ja') is not None:
                errs.append(f'{tag}: {st} なのに身長・名前がある（未確認・食い違いは値を入れない）')
        if st == 'unverified' and e.get('observations'):
            errs.append(f'{tag}: 観測があるのに unverified')
        if st != 'unverified' and not e.get('observations'):
            errs.append(f'{tag}: 観測がないのに {st}')
        if st != 'unverified' and not e.get('status_reason') and st != 'confirmed':
            errs.append(f'{tag}: {st} の理由がない')
        if st == 'unverified' and not e.get('status_reason'):
            errs.append(f'{tag}: unverified の理由がない')
        for o in e.get('observations', []):
            src = o.get('source')
            if src not in SOURCES:
                errs.append(f'{tag}: 公式の出典でない観測: {src!r}')
                continue
            for k in ('url', 'retrieved_on', 'name_ja', 'raw_height', 'cm', 'extract', 'extract_sha256',
                      'response_sha256', 'response_bytes'):
                if o.get(k) in (None, ''):
                    errs.append(f'{tag}: 観測の {k} がない')
            if o.get('url') != SOURCES[src]['detail_url'].format(dex=d):
                errs.append(f'{tag}: 観測の URL が {SOURCES[src]["detail_url"].format(dex=d)} でない: {o.get("url")}')
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(o.get('retrieved_on', ''))):
                errs.append(f'{tag}: 取得日の形が違う: {o.get("retrieved_on")!r}')
            try:
                if normalize_height_cm(o.get('raw_height')) != o.get('cm'):
                    errs.append(f'{tag}: 原表記 {o.get("raw_height")!r} の換算が {o.get("cm")} でない')
            except ValueError as ex:
                errs.append(f'{tag}: {ex}')
            ext = o.get('extract') or {}
            if o.get('extract_sha256') != sha256_bytes(canonical_json(ext)):
                errs.append(f'{tag}: 抜き出しの sha256 が合わない')
            if (ext.get('no'), ext.get('name'), ext.get('takasa'), ext.get('sub'), ext.get('form_name') or None) != \
                    (d, o.get('name_ja'), o.get('raw_height'), o.get('source_form_id'), o.get('form_name')):
                errs.append(f'{tag}: 観測の値と抜き出しが合わない')
            if cache is not None:
                f = cache_path(cache, src, d)
                if f.exists():
                    body = f.read_bytes()
                    if sha256_bytes(body) != o.get('response_sha256'):
                        errs.append(f'{tag}: キャッシュの応答の sha256 が保存した値と違う（取り直した資料が変わった）')
                    else:
                        try:
                            if PARSERS[SOURCES[src]['parser']](body) != ext:
                                errs.append(f'{tag}: キャッシュの応答から抜き出し直した値が保存した抜き出しと違う')
                        except ParseError as ex:
                            errs.append(f'{tag}: キャッシュの応答を読めない: {ex}')
        # 観測から決め直した結果と同じか
        probe = json.loads(json.dumps(e))
        resolve_status(probe, cn)
        for k in ('status', 'name_ja', 'form', 'height'):
            if probe.get(k) != e.get(k):
                errs.append(f'{tag}: {k} が観測から決めた値と違う（{e.get(k)!r} → {probe.get(k)!r}）')
                break
    return errs


def counts(data: dict) -> dict:
    c = Counter(e['status'] for e in data['species'])
    return {s: c.get(s, 0) for s in STATUSES} | {'total': len(data['species'])}


# ---------------------------------------------------------------- 取得

def cache_path(cache: Path, source_id: str, dex: int) -> Path:
    return cache / source_id / f'{dex:04d}.html'


def parse_dex_args(dex: str | None, rng: str | None) -> list:
    out = set()
    if dex:
        for x in dex.split(','):
            out.add(int(x))
    if rng:
        a, b = rng.split('-')
        out.update(range(int(a), int(b) + 1))
    bad = sorted(d for d in out if not DEX_FIRST <= d <= DEX_LAST)
    if bad:
        raise SystemExit(f'範囲の外: {bad}')
    return sorted(out)


def fetch(source_id: str, dexes: list, cache: Path, interval: float) -> dict:
    """公式の資料を低い頻度で取得し、キャッシュに置く（キャッシュがあれば取り直さない）。

    robots.txt を先に読み、許されていない URL は取らない。失敗は記録して続ける（値は作らない）。
    """
    if interval < MIN_INTERVAL:
        raise SystemExit(f'間隔は {MIN_INTERVAL} 秒以上にする')
    src = SOURCES[source_id]
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(src['robots_url'])
    try:
        req = urllib.request.Request(src['robots_url'], headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as r:
            rp.parse(r.read().decode('utf-8', 'replace').splitlines())
    except Exception as e:  # 接続できなければ何も取らない
        return {'robots': f'error: {type(e).__name__}: {e}', 'fetched': [], 'cached': [], 'failed': dexes}
    result = {'robots': 'ok', 'fetched': [], 'cached': [], 'failed': [], 'disallowed': []}
    first = True
    for d in dexes:
        url = src['detail_url'].format(dex=d)
        f = cache_path(cache, source_id, d)
        if f.exists():
            result['cached'].append(d)
            continue
        if not rp.can_fetch(USER_AGENT, url):
            result['disallowed'].append(d)
            continue
        if not first:
            time.sleep(interval)
        first = False
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(body)
            result['fetched'].append(d)
        except Exception as e:
            result['failed'].append({'dex': d, 'error': f'{type(e).__name__}: {e}'})
    return result


def extract(data: dict, source_id: str, dexes: list, cache: Path, retrieved_on: str, cards: list | None) -> dict:
    """キャッシュの応答から観測を作り、データに入れる（同じ出典の観測は置きかえる。ほかの出典の観測は残す）。"""
    idx = species_index(data)
    cn = card_names_by_dex(cards) if cards is not None else None
    res = {'recorded': [], 'missing_cache': [], 'parse_failed': []}
    for d in dexes:
        f = cache_path(cache, source_id, d)
        e = idx[d]
        if not f.exists():
            res['missing_cache'].append(d)
            continue
        try:
            o = make_observation(source_id, d, SOURCES[source_id]['detail_url'].format(dex=d), retrieved_on, f.read_bytes())
        except (ParseError, ValueError) as ex:
            res['parse_failed'].append({'dex': d, 'error': str(ex)})
            if not e['observations']:
                e['status_reason'] = 'parse_failed'
            continue
        e['observations'] = [x for x in e['observations'] if x['source'] != source_id] + [o]
        resolve_status(e, cn)
        res['recorded'].append(d)
    return res


# ---------------------------------------------------------------- コマンド

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--check', action='store_true', help='検査だけ（書き換えない）')
    ap.add_argument('--cache', type=Path, help='--check で照らす応答のキャッシュ')
    sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('init')
    f = sub.add_parser('fetch')
    f.add_argument('--source', default='SRC-ZUKAN-JP', choices=sorted(SOURCES))
    f.add_argument('--cache', type=Path, required=True)
    f.add_argument('--dex')
    f.add_argument('--range')
    f.add_argument('--interval', type=float, default=DEFAULT_INTERVAL)
    f.add_argument('--full-range', action='store_true', help='10 件を超えて取るときに要る（試し取りを確かめたあと）')
    x = sub.add_parser('extract')
    x.add_argument('--source', default='SRC-ZUKAN-JP', choices=sorted(SOURCES))
    x.add_argument('--cache', type=Path, required=True)
    x.add_argument('--dex')
    x.add_argument('--range')
    x.add_argument('--retrieved-on', required=True)
    a = sub.add_parser('record-access')
    a.add_argument('--source', default='SRC-ZUKAN-JP', choices=sorted(SOURCES))
    a.add_argument('--date', required=True)
    a.add_argument('--result', required=True, choices=['ok', 'blocked', 'error', 'terms_checked'])
    a.add_argument('--detail', required=True)
    a.add_argument('--reason-for-unverified', help='未確認の項目の status_reason を置きかえる（観測のない項目だけ）')
    sub.add_parser('report')
    args = ap.parse_args(argv)

    cards = json.loads(CARDS.read_text(encoding='utf-8'))['cards']
    if args.check:
        data = load_data()
        errs = check_data(data, cards, args.cache)
        for e in errs:
            print('エラー:', e)
        print(json.dumps(counts(data), ensure_ascii=False))
        return 1 if errs else 0
    if args.cmd == 'init':
        if DATA.exists() and any(e['observations'] for e in load_data()['species']):
            raise SystemExit('観測のあるデータは init で作り直さない')
        dump_data(skeleton())
        return 0
    if args.cmd == 'fetch':
        dexes = parse_dex_args(args.dex, args.range)
        if len(dexes) > 10 and not args.full_range:
            raise SystemExit('10 件を超える取得は、試し取りで形・単位・姿を確かめてから --full-range をつける')
        print(json.dumps(fetch(args.source, dexes, args.cache, args.interval), ensure_ascii=False, indent=1))
        return 0
    if args.cmd == 'extract':
        data = load_data()
        res = extract(data, args.source, parse_dex_args(args.dex, args.range), args.cache, args.retrieved_on, cards)
        dump_data(data)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    if args.cmd == 'record-access':
        data = load_data()
        data['sources'][args.source]['access_log'].append({'date': args.date, 'result': args.result, 'detail': args.detail})
        if args.reason_for_unverified:
            for e in data['species']:
                if e['status'] == 'unverified' and not e['observations']:
                    e['status_reason'] = args.reason_for_unverified
        dump_data(data)
        return 0
    if args.cmd == 'report':
        data = load_data()
        rep = {'counts': counts(data), 'links': link_report(cards, data)}
        rep['links']['without_dex_ids'] = f'{len(rep["links"]["without_dex_ids"])} 件（省略）'
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
