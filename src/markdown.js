/**
 * Markdown -> HTML, scoped to what ChatGPT actually produces in a blog post.
 *
 * Megan drafts in ChatGPT and pastes the result, which is Markdown. Stored raw
 * it would render as literal ## and ** on the page, so it is converted on save.
 *
 * Deliberately small: headings, bold, italic, links, images, lists, quotes,
 * rules and paragraphs. No HTML passthrough beyond a safe subset.
 */

const esc = (s) =>
  String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function inline(text) {
  let s = esc(text);
  // images before links — ![alt](src)
  s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g,
    (_, alt, src) => `<img src="${src}" alt="${alt}" loading="lazy" decoding="async" />`);
  // [text](url)
  s = s.replace(/\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g, (_, label, href) => {
    const external = /^https?:\/\//i.test(href) && !href.includes('balancehomeorganizing.com');
    return `<a href="${href}"${external ? ' target="_blank" rel="noopener"' : ''}>${label}</a>`;
  });
  s = s.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
  s = s.replace(/_([^_\n]+)_/g, '<em>$1</em>');
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  return s;
}

export function markdownToHtml(md) {
  const lines = String(md ?? '').replace(/\r\n?/g, '\n').split('\n');
  const out = [];
  let para = [];
  let list = null; // 'ul' | 'ol'

  const flushPara = () => {
    if (para.length) {
      out.push(`<p>${inline(para.join(' '))}</p>`);
      para = [];
    }
  };
  const flushList = () => {
    if (list) {
      out.push(`</${list}>`);
      list = null;
    }
  };

  for (const raw of lines) {
    const line = raw.trimEnd();

    if (!line.trim()) { flushPara(); flushList(); continue; }

    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if (h) {
      flushPara(); flushList();
      // the page already has an h1, so markdown h1 becomes h2
      const level = Math.min(Math.max(h[1].length + 1, 2), 5);
      out.push(`<h${level}>${inline(h[2])}</h${level}>`);
      continue;
    }

    if (/^\s*(?:---|\*\*\*|___)\s*$/.test(line)) {
      flushPara(); flushList(); out.push('<hr />'); continue;
    }

    const q = line.match(/^>\s?(.*)$/);
    if (q) { flushPara(); flushList(); out.push(`<blockquote><p>${inline(q[1])}</p></blockquote>`); continue; }

    const ul = line.match(/^\s*[-*+]\s+(.*)$/);
    const ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (ul || ol) {
      flushPara();
      const want = ul ? 'ul' : 'ol';
      if (list !== want) { flushList(); out.push(`<${want}>`); list = want; }
      out.push(`<li>${inline((ul || ol)[1])}</li>`);
      continue;
    }

    flushList();
    para.push(line.trim());
  }
  flushPara();
  flushList();
  return out.join('\n');
}

/** First ~200 characters of prose, for the excerpt and meta description. */
export function autoExcerpt(html, limit = 200) {
  const text = String(html ?? '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  if (text.length <= limit) return text;
  return text.slice(0, text.lastIndexOf(' ', limit) || limit).trim() + '…';
}

export function slugify(title) {
  return String(title ?? '')
    .toLowerCase()
    .replace(/['’]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80) || 'post';
}
