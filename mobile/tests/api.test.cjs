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
const result = { midpoint: p1, radius: 5000, Spots: [], count: 0 };
test('sends coordinates and category mappings with the correct response casing', async () => {
  for (const [label, category, type] of [['Cafés', 'amenity', 'cafe'], ['Parks', 'leisure', 'park'], ['Museums', 'tourism', 'museum']]) {
    const api = client(async url => {
      const parsed = new URL(url);
      assert.equal(parsed.pathname, '/meet');
      for (const [key, value] of Object.entries({ lat1: p1.lat, lon1: p1.lon, lat2: p2.lat, lon2: p2.lon, category, type, radius: 3000, limit: 50, sort: 'fair' })) {
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

test('starts at 5 km and preserves the expanded search radius', async () => {
  const expanded = { ...result, radius: 10000 };
  const api = client(async url => {
    assert.equal(new URL(url).searchParams.get('radius'), '5000');
    return { ok: true, json: async () => expanded };
  });
  assert.equal((await api.getMeetingSpots(p1, p2, 'Cafés')).radius, 10000);
});
test('rejects missing, invalid, or smaller-than-requested response radii', async () => {
  for (const radius of [undefined, null, '5000', NaN, Infinity, -1, 0, 1000, 10001]) {
    const api = client(async () => ({ ok: true, json: async () => ({ ...result, radius }) }));
    await assert.rejects(api.getMeetingSpots(p1, p2, 'Cafés'), /unexpected meeting results/);
  }
});

const spot = { name: 'Test café', lat: 40.74, lon: -73.98, dist_1: 1200,
  dist_2: 1400, dist_mid: 100, gap: 200, properties: {} };
test('supports both sorting modes and preserves server ordering', async () => {
  for (const sort of ['fair', 'closest']) {
    const response = { ...result, Spots: [spot, { ...spot, name: 'Second', gap: 100 }], count: 2 };
    const api = client(async url => {
      assert.equal(new URL(url).searchParams.get('sort'), sort);
      return { ok: true, json: async () => response };
    });
    assert.equal(await api.getMeetingSpots(p1, p2, 'Cafés', 5000, undefined, sort), response);
  }
});
test('rejects invalid sort options before fetching', async () => {
  const api = client(async () => { assert.fail('must not fetch'); });
  await assert.rejects(api.getMeetingSpots(p1, p2, 'Cafés', 5000, undefined, 'invalid'), /valid meeting sort/);
});
test('accepts zero gap and rejects missing or invalid gap values', async () => {
  const api = client(async () => ({ ok: true, json: async () => ({ ...result, Spots: [{ ...spot, gap: 0 }], count: 1 }) }));
  assert.equal((await api.getMeetingSpots(p1, p2, 'Parks')).Spots[0].gap, 0);
  for (const gap of [undefined, null, '200', -1, NaN, Infinity]) {
    const bad = client(async () => ({ ok: true, json: async () => ({ ...result, Spots: [{ ...spot, gap }], count: 1 }) }));
    await assert.rejects(bad.getMeetingSpots(p1, p2, 'Parks'), /unexpected meeting results/);
  }
});

test('checks database readiness independently from API liveness', async () => {
  const api = client(async url => {
    assert.equal(new URL(url).pathname, '/ready');
    return { ok: true, json: async () => ({ status: 'ok' }) };
  });
  assert.equal(await api.checkReadiness(), 'ok');
  const unavailable = client(async () => ({ ok: false, status: 503,
    json: async () => ({ message: 'Database is temporarily unavailable. Please try again.' }) }));
  await assert.rejects(unavailable.checkReadiness(), /Database is temporarily unavailable/);
  const malformed = client(async () => ({ ok: true, json: async () => ({}) }));
  await assert.rejects(malformed.checkReadiness(), /unexpected database readiness/);
});
test('accepts rough walking estimates and supports servers that omit them', async () => {
  for (const minutes of [undefined, 0, 15]) {
    const api = client(async () => ({ ok: true, json: async () => ({ ...result,
      Spots: [{ ...spot, walk_min_1: minutes, walk_min_2: minutes }], count: 1 }) }));
    assert.equal((await api.getMeetingSpots(p1, p2, 'Parks')).Spots[0].walk_min_1, minutes);
  }
  for (const minutes of [null, '15', -1, 1.5, NaN, Infinity]) {
    const api = client(async () => ({ ok: true, json: async () => ({ ...result,
      Spots: [{ ...spot, walk_min_1: minutes }], count: 1 }) }));
    await assert.rejects(api.getMeetingSpots(p1, p2, 'Parks'), /unexpected meeting results/);
  }
});
