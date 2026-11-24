const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const vm = require('node:vm');

// Exercise the screen's empty state with native UI and navigation boundaries stubbed.
function emptyScreen(radius, canGoBack) {
  const calls = [];
  const element = (type, props) => ({ type, props });
  const modules = {
    'react/jsx-runtime': { jsx: element, jsxs: element, Fragment: 'Fragment' },
    react: {
      useMemo: fn => fn(), useEffect: () => {},
      useState: initial => [initial?.status === 'loading'
        ? { status: 'success', data: { radius, Spots: [], count: 0 } } : initial, () => {}],
    },
    'expo-router': {
      useLocalSearchParams: () => ({ from: 'a', to: 'b', category: 'Cafés' }),
      router: { canGoBack: () => canGoBack, back: () => calls.push('back'), replace: path => calls.push(path) },
    },
    'react-native': Object.fromEntries(['ActivityIndicator', 'Pressable', 'ScrollView', 'Text', 'View'].map(name => [name, name])),
    'react-native-safe-area-context': { SafeAreaView: 'SafeAreaView' },
    '../../api': { categories: ['Cafés'], categoryPlaceNames: { Cafés: 'café' } },
    '../components/ui': { colors: {}, ui: {} },
    '../utils/startingLocation': { parseLocation: name => ({ name, lat: 40.7, lon: -74 }) },
    '../state/SearchProvider': { useSearch: () => ({ draft: { sort: 'fair' } }) },
  };
  const exports = {};
  vm.runInNewContext(ts.transpileModule(fs.readFileSync('src/app/results.tsx', 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
  }).outputText, { exports, require: name => modules[name] ?? {} });
  const outer = exports.default();
  const tree = outer.type(outer.props);
  const nodes = [];
  function visit(node) {
    if (Array.isArray(node)) return node.forEach(visit);
    if (!node || typeof node !== 'object') return;
    nodes.push(node);
    visit(node.props?.children);
  }
  visit(tree);
  return { nodes, calls };
}

for (const radius of [5000, 10000]) {
  for (const canGoBack of [true, false]) {
    test(`empty search at ${radius} lets users revise inputs (back=${canGoBack})`, () => {
      const { nodes, calls } = emptyScreen(radius, canGoBack);
      const buttons = nodes.filter(node => node.type === 'Pressable');
      const label = button => button.props.children?.props?.children;
      assert.equal(buttons.some(button => String(label(button)).includes('Search within')), false);
      const edit = buttons.find(button => label(button) === 'Change category or starting points');
      assert.ok(edit, 'empty state offers an input-edit action');
      edit.props.onPress();
      assert.deepEqual(calls, [canGoBack ? 'back' : '/']);
    });
  }
}
