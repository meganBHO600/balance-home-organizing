/* Contact + Join Our Team forms.
 *
 * No submission endpoint is wired yet (open item in the build spec). Rather than
 * fake a success state, the form validates, then hands off to the visitor's mail
 * client with the message prefilled and says so plainly.
 *
 * To send server-side instead, put the endpoint on the form:
 *   <form data-form="contact" data-endpoint="https://...">
 * and this posts the fields as JSON.
 */
(function () {
  'use strict';

  var SUBJECTS = {
    contact: 'Website enquiry — Balance Home Organizing',
    join: 'Joining the team — Balance Home Organizing'
  };
  var INBOX = 'megan@balancehomeorganizing.com';

  function firstInvalid(form) {
    var fields = form.querySelectorAll('input[required], textarea[required]');
    for (var i = 0; i < fields.length; i++) {
      if (!fields[i].checkValidity()) return fields[i];
    }
    return null;
  }

  function labelFor(field) {
    var el = field.closest('div');
    var label = el && el.querySelector('label[for="' + field.id + '"]');
    return label ? label.firstChild.nodeValue.trim() : 'This field';
  }

  function status(form, message, tone) {
    var box = form.querySelector('.form-status');
    if (!box) return;
    box.textContent = message;
    box.hidden = false;
    box.style.background = tone === 'error' ? '#f7e6e1' : 'var(--color-accent-100)';
    box.style.color = tone === 'error' ? '#8a3d29' : 'var(--color-accent-700)';
  }

  function mailtoUrl(form, kind) {
    return 'mailto:' + INBOX +
      '?subject=' + encodeURIComponent(SUBJECTS[kind] || SUBJECTS.contact) +
      '&body=' + encodeURIComponent(body(form));
  }

  function body(form) {
    var out = [];
    form.querySelectorAll('input, textarea').forEach(function (f) {
      if (f.type === 'radio' && !f.checked) return;
      if (!f.name || !f.value || f.name === 'website') return;
      out.push(f.name.replace(/_/g, ' ') + ': ' + f.value);
    });
    return out.join('\n');
  }

  document.querySelectorAll('form[data-form]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();

      var bad = firstInvalid(form);
      if (bad) {
        status(form, labelFor(bad) + ' needs to be filled in before sending.', 'error');
        bad.focus();
        return;
      }

      var kind = form.getAttribute('data-form');
      var endpoint = form.getAttribute('data-endpoint');

      if (endpoint) {
        var data = {};
        form.querySelectorAll('input, textarea').forEach(function (f) {
          if (f.type === 'radio' && !f.checked) return;
          if (f.name) data[f.name] = f.value;
        });
        status(form, 'Sending…');
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        }).then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (body) {
            if (!r.ok) throw new Error(body.error || 'Request failed');
            form.reset();
            status(form, 'Message sent. We usually reply within a business day.');
          });
        }).catch(function (err) {
          // fall back to the visitor's mail client so a submission is never lost
          status(form, (err.message || 'That did not send.') +
                       ' Opening your email app instead \u2014 or write to ' + INBOX + '.', 'error');
          window.location.href = mailtoUrl(form, kind);
        });
        return;
      }

      window.location.href = mailtoUrl(form, kind);
      status(form, 'Opening your email app with this message ready to send. ' +
                   'If nothing opens, email ' + INBOX + ' directly.');
    });
  });
})();
