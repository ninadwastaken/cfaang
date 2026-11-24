const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const vm = require('node:vm');

function details(properties) {
  const exports = {};
  const source = ts.transpileModule(fs.readFileSync('src/data/place-details.ts', 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText;
  vm.runInNewContext(source, { exports });
  return exports.placeDetails(properties);
}

test('formats a street address and preserves listed hours', () => {
  const result = details({ 'addr:housenumber': ' 12 ', 'addr:street': ' Broadway ',
    'addr:city': 'New York', 'addr:postcode': '10004', opening_hours: ' Mo-Fr 09:00-17:00 ' });
  assert.equal(result.address, '12 Broadway, New York, 10004');
  assert.equal(result.hours, 'Mo-Fr 09:00-17:00');
});

test('prefers the full address when available', () => {
  assert.equal(details({ 'addr:full': ' 12 Broadway, Suite 2 ',
    'addr:street': 'Broadway' }).address, '12 Broadway, Suite 2');
});

test('supports street-only addresses without inventing a house number', () => {
  assert.equal(details({ 'addr:street': 'Broadway' }).address, 'Broadway');
});

test('does not present a city or house number alone as a street address', () => {
  assert.equal(details({ 'addr:city': 'New York', 'addr:housenumber': '12' }).address, null);
});

test('omits missing, blank, and non-text details', () => {
  for (const properties of [{}, { 'addr:full': ' ', opening_hours: '' },
    { 'addr:street': {}, opening_hours: ['24/7'] }]) {
    const result = details(properties);
    assert.equal(result.address, null);
    assert.equal(result.hours, null);
  }
});
