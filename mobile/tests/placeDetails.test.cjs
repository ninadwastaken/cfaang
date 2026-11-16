const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const vm = require('node:vm');
const exportsForTest = {};
vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/utils/placeDetails.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, { exports: exportsForTest });
const { placeDetails, walkingEstimate } = exportsForTest;
test('formats full and partial addresses without inventing data', () => {
  const full = placeDetails({ 'addr:housenumber': '12', 'addr:street': 'Broadway', 'addr:city': 'New York', amenity: 'ice_cream' });
  assert.equal(full.address, '12 Broadway, New York');
  assert.equal(full.category, 'ice cream');
  assert.equal(placeDetails({ 'addr:street': 'Broadway' }).address, 'Broadway');
  assert.equal(placeDetails({ 'addr:full': 'Custom address', 'addr:street': 'Broadway' }).address, 'Custom address');
  assert.equal(placeDetails({}).address, 'Address not listed');
  assert.equal(placeDetails({}).category, 'Category not listed');
  assert.equal(placeDetails({ leisure: 'park' }).category, 'park');
});
test('distinguishes unavailable and rounded-zero walking estimates', () => {
  assert.equal(walkingEstimate(undefined), 'Estimate unavailable');
  assert.equal(walkingEstimate(0), 'Under 1 min');
  assert.equal(walkingEstimate(15), 'About 15 min');
});
