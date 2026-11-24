const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const vm = require('node:vm');
const helpers = {};
vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/utils/sharePlace.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, { exports: helpers, URLSearchParams });
test('shares the place and its address with destination-only directions', () => {
  const content = helpers.sharePlaceContent({ name: ' City Library ', lat: 40.7527, lon: -73.9772 }, ' 12 Main Street ');
  assert.equal(content.title, 'City Library · Meet Me');
  assert.match(content.message, /Let's meet at City Library\.\n12 Main Street\nDirections:/);
  const url = new URL(content.message.split('Directions: ')[1]);
  assert.equal(url.origin, 'https://www.google.com');
  assert.equal(url.searchParams.get('destination'), '40.7527,-73.9772');
  assert.equal(url.searchParams.get('api'), '1');
  assert.equal(url.searchParams.has('origin'), false);
});
test('handles missing names and addresses without sharing placeholder text', () => {
  const content = helpers.sharePlaceContent({ name: null, lat: 40.7, lon: -74 }, null);
  assert.match(content.message, /Let's meet at Meeting spot\./);
  assert.doesNotMatch(content.message, /undefined|null|Address not listed|\n\n/);
});
