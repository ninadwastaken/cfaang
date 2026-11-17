const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const vm = require('node:vm');
function load(file) {
  const exports = {};
  vm.runInNewContext(ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText, { exports, process: { env: {} }, require: name => load(path.resolve(path.dirname(file), name) + '.ts') });
  return exports;
}
const { encodeSearch, decodeSearch } = load('src/utils/savedSearch.ts');
const draft = { person1: { name: 'My map pin', lat: 40.74234567, lon: -73.98765432 },
  person2: { name: 'Grand Central', lat: 40.7527, lon: -73.9772 }, category: 'Parks', sort: 'closest' };
test('restores both precise starting points, category, and sort across serialization', () => {
  assert.equal(JSON.stringify(decodeSearch(encodeSearch(draft))), JSON.stringify(draft));
});
test('ignores corrupt or incompatible saved searches instead of crashing startup', () => {
  for (const raw of [null, '', 'broken json', 'null', '{}', JSON.stringify({ version: 2, ...draft }),
    JSON.stringify({ version: 1, ...draft, category: 'invalid' }),
    JSON.stringify({ version: 1, ...draft, sort: 'invalid' }),
    JSON.stringify({ version: 1, ...draft, person1: { name: 'Outside area', lat: 42, lon: -74 } }),
    JSON.stringify({ version: 1, ...draft, person2: null })]) assert.equal(decodeSearch(raw), null);
});
