/**
 * /admin — where Megan writes and publishes.
 *
 * Auth is Cloudflare Access (Google sign-in). Access validates at the edge and
 * injects the user's email; this checks that header against an allowlist.
 *
 * It fails CLOSED: no header means no access. If Access is ever misconfigured
 * or removed, the admin locks rather than opening to the public. workers.dev is
 * disabled in wrangler.jsonc so there is no route that bypasses Access.
 */
import { markdownToHtml, autoExcerpt, slugify } from './markdown.js';

const ALLOWED = ['megan@balancehomeorganizing.com', 'jason.mossuto@gmail.com'];

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

export function adminUser(request) {
  const email = request.headers.get('Cf-Access-Authenticated-User-Email');
  if (!email) return null;
  return ALLOWED.includes(email.toLowerCase()) ? email.toLowerCase() : null;
}

export function adminDenied() {
  return new Response(
    `<!doctype html><html><head><meta charset="utf-8"><title>Not available</title>
     <style>body{font-family:system-ui,sans-serif;max-width:34rem;margin:15vh auto;padding:0 1.5rem;line-height:1.6;color:#4a433a}
     code{background:#f0efed;padding:.15em .4em;border-radius:3px}</style></head>
     <body><h1>Admin is locked</h1>
     <p>This area is protected by Cloudflare Access and no verified sign-in was found.</p>
     <p>If you are setting this up: create an Access application for
     <code>balancehomeorganizing.com/admin*</code> with a Google login policy.</p>
     </body></html>`,
    { status: 403, headers: { 'content-type': 'text/html; charset=utf-8' } }
  );
}

/** body_md was added after the first migration; add it if an older DB lacks it. */
async function ensureSchema(env) {
  try {
    await env.DB.prepare('SELECT body_md FROM posts LIMIT 1').first();
  } catch {
    try { await env.DB.exec("ALTER TABLE posts ADD COLUMN body_md TEXT NOT NULL DEFAULT ''"); } catch {}
  }
}

async function setTerms(env, postId, kind, names) {
  await env.DB.prepare(
    `DELETE FROM post_terms WHERE post_id = ? AND term_id IN (SELECT id FROM terms WHERE kind = ?)`
  ).bind(postId, kind).run();
  for (const raw of names) {
    const name = String(raw).trim();
    if (!name) continue;
    const slug = slugify(name);
    await env.DB.prepare('INSERT OR IGNORE INTO terms (kind, name, slug) VALUES (?, ?, ?)')
      .bind(kind, name, slug).run();
    await env.DB.prepare(
      `INSERT OR IGNORE INTO post_terms (post_id, term_id)
       SELECT ?, id FROM terms WHERE kind = ? AND slug = ?`
    ).bind(postId, kind, slug).run();
  }
}

async function loadTerms(env, postId) {
  const r = await env.DB.prepare(
    `SELECT t.kind, t.name FROM terms t JOIN post_terms pt ON pt.term_id = t.id WHERE pt.post_id = ?`
  ).bind(postId).all();
  const out = { tag: [], category: [] };
  for (const row of r.results || []) out[row.kind]?.push(row.name);
  return out;
}

export async function handleAdminApi(request, env, url) {
  const user = adminUser(request);
  if (!user) return json({ error: 'Not authorised.' }, 403);
  await ensureSchema(env);

  const m = url.pathname.match(/^\/api\/admin\/posts(?:\/([^/]+))?$/);
  if (!m) return json({ error: 'Not found.' }, 404);
  const slug = m[1] ? decodeURIComponent(m[1]) : null;
  const method = request.method;

  if (!slug && method === 'GET') {
    const r = await env.DB.prepare(
      `SELECT slug, title, status, published_at, updated_at, pin_status, pin_url
         FROM posts ORDER BY COALESCE(published_at, updated_at) DESC`
    ).all();
    return json({ posts: r.results || [] });
  }

  if (slug && method === 'GET') {
    const post = await env.DB.prepare('SELECT * FROM posts WHERE slug = ?').bind(slug).first();
    if (!post) return json({ error: 'Not found.' }, 404);
    return json({ post: { ...post, terms: await loadTerms(env, post.id) } });
  }

  if (method === 'POST' || method === 'PUT') {
    let data;
    try { data = await request.json(); } catch { return json({ error: 'Bad request body.' }, 400); }

    const title = String(data.title || '').trim();
    if (!title) return json({ error: 'A title is required.' }, 400);

    const bodyMd = String(data.body_md || '');
    const bodyHtml = markdownToHtml(bodyMd);
    const excerpt = String(data.excerpt || '').trim() || autoExcerpt(bodyHtml);
    const newSlug = slugify(data.slug || title);
    const status = data.status === 'published' ? 'published' : 'draft';
    const now = Date.now();

    const amazon = Array.isArray(data.amazon_links)
      ? JSON.stringify(data.amazon_links.filter((l) => l && l.url))
      : '[]';

    if (method === 'POST') {
      const clash = await env.DB.prepare('SELECT 1 FROM posts WHERE slug = ?').bind(newSlug).first();
      if (clash) return json({ error: `A post with the address “${newSlug}” already exists.` }, 409);
      await env.DB.prepare(
        `INSERT INTO posts (slug, title, excerpt, body_md, body_html, thumb, author, status,
                            published_at, created_at, updated_at, pin_url, amazon_links)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).bind(newSlug, title, excerpt, bodyMd, bodyHtml, data.thumb || null,
             data.author || 'Megan Mossuto', status,
             status === 'published' ? (data.published_at || now) : null,
             now, now, data.pin_url || null, amazon).run();
    } else {
      const existing = await env.DB.prepare('SELECT * FROM posts WHERE slug = ?').bind(slug).first();
      if (!existing) return json({ error: 'Not found.' }, 404);
      if (newSlug !== slug) {
        const clash = await env.DB.prepare('SELECT 1 FROM posts WHERE slug = ?').bind(newSlug).first();
        if (clash) return json({ error: `A post with the address “${newSlug}” already exists.` }, 409);
      }
      await env.DB.prepare(
        `UPDATE posts SET slug = ?, title = ?, excerpt = ?, body_md = ?, body_html = ?, thumb = ?,
                          status = ?, published_at = ?, updated_at = ?, pin_url = ?, amazon_links = ?
         WHERE slug = ?`
      ).bind(newSlug, title, excerpt, bodyMd, bodyHtml, data.thumb || null, status,
             status === 'published' ? (existing.published_at || data.published_at || now) : null,
             now, data.pin_url || null, amazon, slug).run();
    }

    const saved = await env.DB.prepare('SELECT * FROM posts WHERE slug = ?').bind(newSlug).first();
    await setTerms(env, saved.id, 'tag', data.tags || []);
    await setTerms(env, saved.id, 'category', data.categories || []);
    return json({ ok: true, slug: newSlug, status });
  }

  if (slug && method === 'DELETE') {
    await env.DB.prepare('DELETE FROM posts WHERE slug = ?').bind(slug).run();
    return json({ ok: true });
  }

  return json({ error: 'Method not allowed.' }, 405);
}
