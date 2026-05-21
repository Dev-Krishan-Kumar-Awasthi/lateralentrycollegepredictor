/**
 * WhatsApp & Telegram share helpers
 */
(function (global) {
  'use strict';

  function encode(text) {
    return encodeURIComponent(text);
  }

  function whatsappUrl(text) {
    return 'https://api.whatsapp.com/send?text=' + encode(text);
  }

  function telegramUrl(text) {
    return 'https://t.me/share/url?url=' + encode(global.location ? global.location.origin : '') +
      '&text=' + encode(text);
  }

  function sharePrediction(params) {
    const host = global.location ? global.location.origin : '';
    const url = host + '/predictor?' + new URLSearchParams(params).toString();
    const cgpa = params.cgpa || '';
    const text =
      'Check my MP DTE Lateral Entry college prediction (CGPA ' + cgpa + '):\n' +
      url + '\n\nBuilt with MP BTech Lateral Entry College Predictor';
    return { whatsapp: whatsappUrl(text), telegram: telegramUrl(text), url: url };
  }

  function shareSimulatorResult(college, branch, success) {
    const host = global.location ? global.location.origin : '';
    let text;
    if (success && college) {
      text =
        'Mock allotment result: ' + college + ' — ' + branch +
        '\nTry the MP DTE Lateral Entry Simulator: ' + host + '/simulator';
    } else {
      text = 'I checked my MP DTE Lateral Entry chances here: ' + host + '/simulator';
    }
    return { whatsapp: whatsappUrl(text), telegram: telegramUrl(text) };
  }

  function bindShareButtons(container, links) {
    if (!container) return;
    const wa = container.querySelector('[data-share-whatsapp]');
    const tg = container.querySelector('[data-share-telegram]');
    if (wa) wa.href = links.whatsapp;
    if (tg) tg.href = links.telegram;
  }

  global.ShareUtils = {
    whatsappUrl: whatsappUrl,
    telegramUrl: telegramUrl,
    sharePrediction: sharePrediction,
    shareSimulatorResult: shareSimulatorResult,
    bindShareButtons: bindShareButtons,
  };
})(typeof window !== 'undefined' ? window : global);
