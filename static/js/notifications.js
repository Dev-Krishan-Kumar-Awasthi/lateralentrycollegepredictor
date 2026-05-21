/**
 * Browser notification subscription for counselling dates
 */
(function (global) {
  'use strict';

  function isSupported() {
    return 'Notification' in global && 'serviceWorker' in navigator;
  }

  function requestPermission() {
    if (!isSupported()) return Promise.resolve('unsupported');
    return Notification.requestPermission();
  }

  function showLocal(title, body) {
    if (!isSupported() || Notification.permission !== 'granted') return;
    new Notification(title, {
      body: body,
      icon: '/static/favicon.png',
      badge: '/static/favicon.png',
    });
  }

  function scheduleReminders(events) {
    if (!events || !events.length) return;
    const key = 'mp_dte_notif_scheduled';
    if (localStorage.getItem(key)) return;
    events.forEach(function (ev) {
      const d = new Date(ev.date);
      const now = new Date();
      const diff = d - now;
      if (diff > 0 && diff < 7 * 24 * 60 * 60 * 1000) {
        setTimeout(function () {
          showLocal('DTE MP: ' + ev.title, ev.description || 'Check dte.mponline.gov.in');
        }, Math.min(diff, 2147483647));
      }
    });
    localStorage.setItem(key, '1');
  }

  function initSubscribeButton(btnId, eventsUrl) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    btn.addEventListener('click', function () {
      requestPermission().then(function (perm) {
        if (perm === 'granted') {
          fetch(eventsUrl || '/api/v1/counselling-schedule')
            .then(function (r) { return r.json(); })
            .then(function (data) { scheduleReminders(data.events || []); });
          btn.textContent = 'Notifications Enabled';
          btn.disabled = true;
          showLocal('Subscribed!', 'We will remind you of upcoming DTE counselling dates.');
        } else if (perm === 'denied') {
          if (global.showToast) global.showToast('Please allow notifications in browser settings.', 'error');
          else alert('Please allow notifications in browser settings.');
        }
      });
    });
  }

  global.MpNotifications = {
    isSupported: isSupported,
    requestPermission: requestPermission,
    initSubscribeButton: initSubscribeButton,
    scheduleReminders: scheduleReminders,
  };
})(typeof window !== 'undefined' ? window : global);
