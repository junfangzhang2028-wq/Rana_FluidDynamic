// Run with: node tests/canal_height.test.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '../docs/index.html'), 'utf8');
function load(source) {
  const start = source.indexOf('var AqueousOutflow = (function');
  assert.ok(start >= 0);
  const ctx = {};
  vm.createContext(ctx);
  vm.runInContext(source.slice(start, source.indexOf('</script>', start)), ctx);
  return ctx.AqueousOutflow;
}
const fixed = load(html);
// Reconstruct only the previous output conversion to check unchanged flow/pressure.
const previous = load(html.replace('getH(pressure[i] - S.Pev, iop, i)', 'getH(pressure[i], iop, i)'));
assert.match(html, /Etm \(mmHg\)/);
const results = [];
for (const pev of [0, 8]) {
  const cases = (pev === 0 ? [5, 15, 30, 45] : [15, 30, 45])
    .map(iop => ({mode: 'constant pressure', iop}));
  cases.push({mode: 'constant flow', qt: 5});
  for (const condition of cases) {
    const payload = {...condition, pev, rtm: 2, etm: 13, h0: 20, hs: 3,
      n: 30, m: 40, geometry: 'ellipse', surgery: 'None', max_error: 1e-7};
    const result = fixed.solvePayload(payload);
    const old = previous.solvePayload(payload);
    assert.equal(JSON.stringify(result.metrics), JSON.stringify(old.metrics));
    assert.equal(JSON.stringify(result.series.pressure), JSON.stringify(old.series.pressure));
    if (pev === 0) assert.equal(JSON.stringify(result.series.height), JSON.stringify(old.series.height));
    for (let i = 0; i < result.series.height.y.length; i++) {
      // Independent evaluation of paper equations (4)-(6), using absolute pressures.
      const dp = result.metrics.iop - result.series.pressure.y[i];
      const ks = 13 * (1 - 3 / 20);
      const expected = Math.min(20, dp < ks ? 20 * (1 - dp / 13) : 3 * Math.cbrt(ks / dp));
      assert.ok(Math.abs(result.series.height.y[i] - expected) < 1e-10,
        `Height mismatch: Pev=${pev}, IOP=${result.metrics.iop}, node=${i}`);
    }
    results.push({pev, mode: condition.mode, iop: result.metrics.iop,
      min: Math.min(...result.series.height.y), max: Math.max(...result.series.height.y)});
  }
}
const high = results.find(r => r.pev === 8 && r.iop === 45);
assert.ok(high.max < 3, 'At Pev=8, IOP=45 every baseline node is septae-supported');
console.table(results);
console.log('PASS: height physics, Pev=0 preservation, unchanged pressure/flow, ETM units.');
