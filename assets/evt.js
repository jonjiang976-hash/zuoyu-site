/* Cookie-free, first-party event counter for zuoyugarment.com
   - No cookies, no localStorage identifiers, no personal data, IP is never stored.
   - Only aggregate daily counts per event name (see /api/evt on the site Worker).
   - Honours Do Not Track and an explicit opt-out: localStorage.zy_no_track = "1". */
(function () {
  try {
    if (navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.msDoNotTrack === '1') return;
    if (localStorage && localStorage.getItem('zy_no_track') === '1') return;
  } catch (e) {}

  var ENDPOINT = '/api/evt';
  var sent = {};

  function send(name) {
    if (!name || sent[name]) return;
    sent[name] = 1;
    var payload = JSON.stringify({ e: name, p: location.pathname.slice(0, 120) });
    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([payload], { type: 'application/json' });
        if (navigator.sendBeacon(ENDPOINT, blob)) return;
      }
    } catch (e) {}
    try {
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true,
        credentials: 'omit'
      });
    } catch (e) {}
  }

  window.zyEvt = send;

  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a') : null;
    if (!a || !a.href) return;
    var h = a.href;
    if (h.indexOf('wa.me') > -1 || /whatsapp/i.test(h)) send('whatsapp_click');
    else if (h.indexOf('mailto:') === 0) send('email_click');
    else if (h.indexOf('made-in-china.com') > -1) send('mic_click');
    else if (h.indexOf('alibaba.com') > -1) send('alibaba_click');
  }, { passive: true });
})();
