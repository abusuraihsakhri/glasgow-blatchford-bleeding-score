const { test } = require('node:test');
const assert = require('node:assert/strict');
const { calculate } = require('./gbs.js');
const base = { urea: 5, hemoglobin: 14, sex: 'male', sbp: 120, pulse: 80, melena: false, syncope: false, hepaticDisease: false, cardiacFailure: false };
const score = (change) => calculate({ ...base, ...change });
test('complete zero and GBS=1 qualify for very-low-risk assessment', () => {
  assert.equal(score({}).score, 0);
  assert.equal(score({ melena: true }).score, 1);
  assert.equal(score({ melena: true }).veryLowRisk, true);
  assert.equal(score({ melena: true, syncope: true }).veryLowRisk, false);
});
test('exact urea cutoffs', () => {
  for (const [value, pts] of [[6.49,0],[6.5,2],[7.99,2],[8,3],[9.99,3],[10,4],[24.99,4],[25,6]])
    assert.equal(score({ urea: value }).components.urea, pts);
});
test('hemoglobin thresholds handle decimals and sex-specific intervals', () => {
  for (const [sex,value,pts] of [['male',9.99,6],['male',10,3],['male',11.99,3],['male',12,1],['male',12.99,1],['male',13,0],['female',9.99,6],['female',10,1],['female',11.99,1],['female',12,0]])
    assert.equal(score({ sex, hemoglobin: value }).components.hemoglobin, pts);
});
test('systolic cutoffs include fractional readings', () => {
  for (const [value,pts] of [[89.99,3],[90,2],[99.99,2],[100,1],[109.99,1],[110,0]])
    assert.equal(score({ sbp: value }).components.sbp, pts);
});
test('maximum score is 23', () => {
  assert.equal(score({ urea: 25, hemoglobin: 9, sbp: 80, pulse: 100, melena:true, syncope:true, hepaticDisease:true, cardiacFailure:true }).score, 23);
});
test('non-finite, missing, wrong types and out-of-range values fail closed', () => {
  for (const value of [NaN, Infinity, -1, 301, '', null, undefined]) assert.throws(() => score({ sbp: value }));
  assert.throws(() => score({ sex: 'other' }));
  assert.throws(() => score({ melena: 'false' }));
});
