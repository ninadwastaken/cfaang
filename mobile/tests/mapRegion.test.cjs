const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const vm = require('node:vm');
const helpers = {};
vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/utils/mapRegion.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, { exports: helpers });
test('fits both people and outlying recommendations without swapping latitude and longitude', () => {
  const points = [{ lat: 40.73, lon: -73.99 }, { lat: 40.75, lon: -73.97 }, { lat: 40.8, lon: -74.1 }];
  const region = helpers.mapRegion(points);
  for (const point of points) {
    assert.ok(Math.abs(point.lat - region.latitude) < region.latitudeDelta / 2);
    assert.ok(Math.abs(point.lon - region.longitude) < region.longitudeDelta / 2);
  }
  assert.equal(helpers.coordinate(points[0]).latitude, 40.73);
  assert.equal(helpers.coordinate(points[0]).longitude, -73.99);
});
test('coincident starting points and an empty result list still have a usable viewport', () => {
  const point = { lat: 40.73, lon: -73.99 };
  const region = helpers.mapRegion([point, point, point]);
  assert.equal(region.latitude, point.lat);
  assert.equal(region.longitude, point.lon);
  assert.ok(region.latitudeDelta > 0);
  assert.ok(region.longitudeDelta > 0);
});
