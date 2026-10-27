const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const vm = require('node:vm');
function client(fetch, timers = {}) {
  const exports = {};
  const source = ts.transpileModule(fs.readFileSync('api.ts', 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText;
  vm.runInNewContext(source, { exports, process: { env: { EXPO_PUBLIC_API_URL: 'http://localhost:8000/' } },
    fetch, URLSearchParams, AbortController, setTimeout, clearTimeout, ...timers });
  return exports;
}
const p1 = { lat: 40.7359, lon: -73.9911 };
const p2 = { lat: 40.7527, lon: -73.9772 };
const result = { midpoint: p1, Spots: [], count: 0 };
test('sends coordinates and category mappings with the correct response casing', async () => {
  for (const [label, category, type] of [['Cafés', 'amenity', 'cafe'], ['Parks', 'leisure', 'park'], ['Museums', 'tourism', 'museum']]) {
    const api = client(async url => {
      const parsed = new URL(url);
      assert.equal(parsed.pathname, '/meet');
      for (const [key, value] of Object.entries({ lat1: p1.lat, lon1: p1.lon, lat2: p2.lat, lon2: p2.lon, category, type, radius: 3000, limit: 50 })) {
        assert.equal(parsed.searchParams.get(key), String(value));
      }
      return { ok: true, json: async () => result };
    });
    assert.equal(await api.getMeetingSpots(p1, p2, label, 3000), result);
  }
});
test('surfaces backend validation and non-JSON server failures', async () => {
  let api = client(async () => ({ ok: false, status: 400, json: async () => ({ message: 'Bad coordinates' }) }));
  await assert.rejects(api.getMeetingSpots(p1, p2, 'Cafés'), /Bad coordinates/);
  api = client(async () => ({ ok: false, status: 500, json: async () => { throw new Error(); } }));
  await assert.rejects(api.getMeetingSpots(p1, p2, 'Cafés'), /status 500/);
});
test('rejects malformed results and invalid coordinates', async () => {
  const api = client(async () => ({ ok: true, json: async () => ({ spots: [] }) }));
  await assert.rejects(api.getMeetingSpots(p1, p2, 'Cafés'), /unexpected meeting results/);
  await assert.rejects(api.getMeetingSpots({ lat: NaN, lon: 0 }, p2, 'Cafés'), /valid starting locations/);
});
test('times out stalled requests', async () => {
  const api = client((_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener('abort', () => reject(new Error('aborted')));
  }), { setTimeout: callback => setTimeout(callback, 1) });
  await assert.rejects(api.getMeetingSpots(p1, p2, 'Parks'), /timed out/);
});
