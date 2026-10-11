// TCGdex (cards-database) の data-asia/*.ts カード定義を JSON に変換する。
// 使い方: node scripts/ts2json.mjs <cards-database のパス> <出力 JSON パス>
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const [, , root, out] = process.argv;
if (!root || !out) {
  console.error('usage: node scripts/ts2json.mjs <cards-database> <out.json>');
  process.exit(1);
}

const SETS = [
  ['PMCG', 'PMCG1'], ['PMCG', 'PMCG2'], ['PMCG', 'PMCG3'], ['PMCG', 'PMCG4'],
  ['PMCG', 'PMCG5'], ['PMCG', 'PMCG6'],
  ['neo', 'neo1'], ['neo', 'neo2'], ['neo', 'neo3'], ['neo', 'neo4'],
];

function evalTs(src, varName) {
  const body = src
    .replace(/^\s*import .*$/gm, '')
    .replace(/^\s*export default .*$/gm, '')
    .replace(new RegExp(`const ${varName}\\s*:\\s*\\w+\\s*=`), `const ${varName} =`)
    .replace(/\bset:\s*Set\s*,/g, 'set: null,')
    .replace(/\bserie:\s*serie\s*,/g, 'serie: null,');
  return vm.runInNewContext(`${body}\n;${varName}`);
}

const result = [];
for (const [serie, id] of SETS) {
  const dir = path.join(root, 'data-asia', serie, id);
  const meta = evalTs(fs.readFileSync(`${dir}.ts`, 'utf8'), 'set');
  const cards = [];
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('.ts')).sort()) {
    const card = evalTs(fs.readFileSync(path.join(dir, f), 'utf8'), 'card');
    delete card.set;
    cards.push({ localId: f.replace(/\.ts$/, ''), ...card });
  }
  result.push({ id, name: meta.name, cardCount: meta.cardCount, releaseDate: meta.releaseDate, cards });
}
fs.writeFileSync(out, JSON.stringify(result, null, 1));
console.log(result.map((s) => `${s.id}: ${s.cards.length}`).join('\n'));
