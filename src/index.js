/**
 * Balance Home Organizing — static site + form handler.
 *
 * Everything under site/ is served as static assets. Two POST endpoints accept
 * the Contact and Join Our Team forms and email them to the inbox below.
 *
 * Email goes out through Resend rather than Cloudflare Email Routing: routing
 * would require Cloudflare MX records on the domain, which would replace Google
 * Workspace and break megan@balancehomeorganizing.com. Resend touches no DNS.
 *
 * Required secret:  RESEND_API_KEY
 */

const INBOX = 'megan@balancehomeorganizing.com';
const FROM = 'Balance Home Organizing <onboarding@resend.dev>';

const FORMS = {
  '/api/contact': {
    subject: 'Website enquiry',
    required: ['first_name', 'last_name', 'email', 'message'],
    fields: ['first_name', 'last_name', 'email', 'phone', 'zip', 'past_organizer', 'message'],
  },
  '/api/join': {
    subject: 'Join our team enquiry',
    required: ['first_name', 'last_name', 'email', 'message'],
    fields: ['first_name', 'last_name', 'email', 'phone', 'message'],
  },
};

const LABELS = {
  first_name: 'First name', last_name: 'Last name', email: 'Email',
  phone: 'Phone', zip: 'Zip code', message: 'Message',
  past_organizer: 'Worked with an organizer before',
};

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });

const clean = (v, max = 4000) =>
  typeof v === 'string' ? v.replace(/\s+/g, ' ').trim().slice(0, max) : '';

function validate(spec, data) {
  // honeypot: a real person never fills a hidden field
  if (clean(data.website)) return 'spam';
  for (const key of spec.required) {
    if (!clean(data[key])) return `${LABELS[key] || key} is required.`;
  }
  const email = clean(data.email);
  if (!/^[^@\s]+@[^@\s.]+\.[^@\s]+$/.test(email)) return 'That email address does not look right.';
  if (clean(data.message).length < 2) return 'Message is required.';
  return null;
}

async function send(env, spec, data, request) {
  const lines = spec.fields
    .map((k) => (clean(data[k]) ? `${LABELS[k] || k}: ${clean(data[k])}` : null))
    .filter(Boolean);
  lines.push('', `Sent from ${new URL(request.url).hostname}`, new Date().toUTCString());

  const name = `${clean(data.first_name)} ${clean(data.last_name)}`.trim();
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${env.RESEND_API_KEY}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      from: FROM,
      to: [INBOX],
      reply_to: clean(data.email),
      subject: `${spec.subject}${name ? ` — ${name}` : ''}`,
      text: lines.join('\n'),
    }),
  });

  if (!res.ok) {
    throw new Error(`resend ${res.status}: ${(await res.text()).slice(0, 300)}`);
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const spec = FORMS[url.pathname];

    if (spec) {
      if (request.method !== 'POST') return json({ error: 'Method not allowed.' }, 405);

      let data;
      try {
        data = await request.json();
      } catch {
        return json({ error: 'Could not read that submission.' }, 400);
      }

      const problem = validate(spec, data);
      // a honeypot hit gets a success response so bots do not learn anything
      if (problem === 'spam') return json({ ok: true });
      if (problem) return json({ error: problem }, 400);

      if (!env.RESEND_API_KEY) {
        console.error('RESEND_API_KEY is not set');
        return json({ error: 'Email is not configured yet.' }, 503);
      }

      try {
        await send(env, spec, data, request);
        return json({ ok: true });
      } catch (err) {
        console.error('send failed', err.message);
        return json({ error: 'That did not send.' }, 502);
      }
    }

    return env.ASSETS.fetch(request);
  },
};
