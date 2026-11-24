const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const vm = require('node:vm');
const helpers = {};
vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/utils/startingLocation.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, { exports: helpers });
test('picked coordinates survive route serialization without precision loss', () => {
  const point = { lat: 40.74234567, lon: -73.98765432 };
  const parsed = helpers.parseLocation(JSON.stringify(helpers.pickedLocation(point)));
  assert.equal(parsed.lat, point.lat);
  assert.equal(parsed.lon, point.lon);
  assert.match(parsed.name, /Map point/);
});
test('rejects malformed and out-of-area route coordinates', () => {
  for (const value of ['invalid', 'null', '[]', '{}', JSON.stringify({ name: '', lat: 40.7, lon: -74 }),
    JSON.stringify({ name: 'Boston', lat: 42.36, lon: -71.05 }),
    JSON.stringify({ name: 'bad', lat: '40.7', lon: -74 })]) assert.equal(helpers.parseLocation(value), null);
  assert.equal(helpers.inServiceArea({ lat: NaN, lon: -74 }), false);
  assert.equal(helpers.inServiceArea({ lat: 40.7, lon: Infinity }), false);
});
