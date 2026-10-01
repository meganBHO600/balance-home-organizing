/**
 * Blog rendering from D1.
 *
 * Posts live in the database so Megan can publish without a git push. The page
 * shell comes from chrome.json, which tools/build.py generates from the same
 * nav()/footer() used by the static pages — so the two cannot drift apart.
 *
 * Anything not found in D1 falls through to the static files, so the site keeps
 * working before and during the migration.
 */
import chrome from './chrome.json';

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function shell(kind, { title, description, headExtra = '', body }) {
  const c = chrome[kind];
  return (
    c.head
      .replace('@@TITLE@@', esc(title))
      .replace('@@DESCRIPTION@@', esc(description))
      .replace('@@HEAD_EXTRA@@', headExtra) +
    body +
    c.tail
  );
}

const html = (markup, status = 200) =>
  new Response(markup, {
    status,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'public, max-age=60',
    },
  });

function fmtDate(ms) {
  return new Date(ms).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC',
  });
}

/** Open Graph + article schema so a pin created from this URL fills itself in. */
function postHead(post, origin) {
  const url = `${origin}/blog/${post.slug}`;
  const img = post.pin_image || post.thumb;
  const abs = img ? (img.startsWith('http') ? img : `${origin}/${img.replace(/^\.\.\//, '')}`) : null;
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.excerpt || post.title,
    datePublished: post.published_at ? new Date(post.published_at).toISOString() : undefined,
    author: { '@type': 'Person', name: post.author },
    publisher: { '@type': 'Organization', name: 'Balance Home Organizing' },
    mainEntityOfPage: url,
    image: abs || undefined,
  };
  return [
    `<link rel="canonical" href="${esc(url)}" />`,
    `<meta property="og:type" content="article" />`,
    `<meta property="og:title" content="${esc(post.title)}" />`,
    `<meta property="og:description" content="${esc(post.excerpt || post.title)}" />`,
    `<meta property="og:url" content="${esc(url)}" />`,
    abs ? `<meta property="og:image" content="${esc(abs)}" />` : '',
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<script type="application/ld+json">${JSON.stringify(schema)}</script>`,
  ].filter(Boolean).join('\n');
}

export async function renderPost(env, slug, origin) {
  const post = await env.DB.prepare(
    `SELECT * FROM posts WHERE slug = ? AND status = 'published'`
  ).bind(slug).first();
  if (!post) return null;

  const terms = await env.DB.prepare(
    `SELECT t.kind, t.name, t.slug FROM terms t
       JOIN post_terms pt ON pt.term_id = t.id
       JOIN posts p ON p.id = pt.post_id
      WHERE p.slug = ? ORDER BY t.kind, t.name`
  ).bind(slug).all();

  const neighbours = await env.DB.prepare(
    `SELECT slug, title, published_at FROM posts
      WHERE status = 'published' ORDER BY published_at DESC`
  ).all();
  const list = neighbours.results || [];
  const i = list.findIndex((p) => p.slug === slug);
  const newer = i > 0 ? list[i - 1] : null;
  const older = i >= 0 && i < list.length - 1 ? list[i + 1] : null;

  const termLinks = (terms.results || [])
    .map((t) => `<a href="${t.kind}/${esc(t.slug)}.html">${esc(t.name)}</a>`)
    .join('');

  const nav = [
    newer ? `<a href="${esc(newer.slug)}" rel="prev">&larr; ${esc(newer.title)}</a>` : '',
    older ? `<a href="${esc(older.slug)}" rel="next">${esc(older.title)} &rarr;</a>` : '',
  ].filter(Boolean).join('');

  const body = `<article class="post">
  <header class="post__header">
    <p class="post__meta"><time datetime="${new Date(post.published_at).toISOString().slice(0, 10)}">${fmtDate(post.published_at)}</time>
      ${post.author ? '&middot; ' + esc(post.author) : ''}</p>
    <h1>${esc(post.title)}</h1>
  </header>
  <div class="post__body">
${post.body_html}
  </div>
  ${termLinks ? `<p class="post__terms">${termLinks}</p>` : ''}
  <p class="post__back"><a href="../blog.html">&larr; All tips</a></p>
  ${nav ? `<nav class="post-nav" aria-label="More posts">${nav}</nav>` : ''}
</article>`;

  return html(shell('post', {
    title: `${post.title} — Balance Home Organizing`,
    description: (post.excerpt || post.title).slice(0, 180),
    headExtra: postHead(post, origin),
    body,
  }));
}
