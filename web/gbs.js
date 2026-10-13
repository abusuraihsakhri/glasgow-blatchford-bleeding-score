/* Pure, dependency-free Glasgow–Blatchford score. Urea in mmol/L. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.GBS = api;
})(typeof globalThis !== 'undefined' ? globalThis : undefined, function () {
  'use strict';
  const required = ['urea', 'hemoglobin', 'sbp', 'pulse'];
  const bounds = { urea: [0, 100], hemoglobin: [0, 30], sbp: [0, 300], pulse: [0, 300] };
  const symptoms = ['melena', 'syncope', 'hepaticDisease', 'cardiacFailure'];

  function calculate(input) {
    if (!input || typeof input !== 'object') throw new Error('Provide the clinical measurements.');
    if (input.sex !== 'male' && input.sex !== 'female') throw new Error('Select the hemoglobin reference category.');
    for (const key of required) {
      if (typeof input[key] !== 'number' || !Number.isFinite(input[key]) ||
          input[key] < bounds[key][0] || input[key] > bounds[key][1]) {
        throw new Error('Enter a valid ' + key + ' measurement.');
      }
    }
    for (const key of symptoms) {
      if (typeof input[key] !== 'boolean') throw new Error('Invalid ' + key + ' response.');
    }
    const { urea, hemoglobin, sbp, pulse, sex } = input;
    const components = {
      urea: urea >= 25 ? 6 : urea >= 10 ? 4 : urea >= 8 ? 3 : urea >= 6.5 ? 2 : 0,
      hemoglobin: hemoglobin < 10 ? 6 : sex === 'male' ?
        (hemoglobin < 12 ? 3 : hemoglobin < 13 ? 1 : 0) : (hemoglobin < 12 ? 1 : 0),
      sbp: sbp < 90 ? 3 : sbp < 100 ? 2 : sbp < 110 ? 1 : 0,
      pulse: pulse >= 100 ? 1 : 0,
      melena: input.melena ? 1 : 0,
      syncope: input.syncope ? 2 : 0,
      hepaticDisease: input.hepaticDisease ? 2 : 0,
      cardiacFailure: input.cardiacFailure ? 2 : 0
    };
    const score = Object.values(components).reduce((sum, value) => sum + value, 0);
    return {
      score, maxScore: 23, components, veryLowRisk: score <= 1,
      category: score <= 1 ? 'Very low risk by GBS' : 'Not in the very-low-risk GBS group',
      message: score <= 1
        ? 'GBS 0–1: outpatient follow-up may be considered after clinical assessment. Ongoing bleeding, instability, or other concerns override the score.'
        : 'GBS >1: the very-low-risk outpatient criterion is not met. Assess admission, resuscitation, and endoscopy from the full clinical picture.'
    };
  }
  return { calculate };
});
