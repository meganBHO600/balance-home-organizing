/** The /admin interface. Self-contained so it needs no build step. */
export function adminPage(user) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Write a post — Balance Home Organizing</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap" />
<style>
  :root{--ink:#4a433a;--accent:#b23b24;--accent-600:#94311e;--bg:#f5f6f4;--line:color-mix(in srgb,#4a433a 14%,transparent);--warm:#eee0cb}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:Montserrat,system-ui,sans-serif;line-height:1.6}
  header{display:flex;align-items:center;gap:1rem;padding:1rem 1.5rem;border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:5}
  header h1{font-size:1.1rem;font-weight:600;margin:0}
  header .who{margin-left:auto;font-size:.8rem;opacity:.7}
  .wrap{max-width:1100px;margin:0 auto;padding:1.5rem}
  .cols{display:grid;grid-template-columns:300px 1fr;gap:1.5rem;align-items:start}
  @media(max-width:860px){.cols{grid-template-columns:1fr}}
  .card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:1.25rem}
  label{display:block;font-size:.8rem;font-weight:600;margin:0 0 .35rem;letter-spacing:.02em}
  .hint{font-weight:400;opacity:.65;font-size:.75rem}
  input,textarea,select{width:100%;font:inherit;font-size:.9rem;color:var(--ink);background:#fbfbfa;
    border:1px solid color-mix(in srgb,#4a433a 30%,transparent);border-radius:5px;padding:.55rem .65rem;margin-bottom:.9rem}
  textarea{resize:vertical;line-height:1.65}
  #body_md{min-height:460px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.85rem}
  input:focus,textarea:focus{outline:2px solid var(--ink);outline-offset:1px;border-color:var(--ink)}
  button{font:inherit;font-size:.8rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;
    padding:.6rem 1.1rem;border:1px solid transparent;border-radius:5px;cursor:pointer}
  .primary{background:var(--accent);color:#fff}.primary:hover{background:var(--accent-600)}
  .ghost{background:transparent;color:var(--accent);border-color:var(--accent)}.ghost:hover{background:var(--accent);color:#fff}
  .danger{background:transparent;color:#8a3d29;border-color:color-mix(in srgb,#8a3d29 40%,transparent)}
  .bar{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;margin-top:1rem;padding-top:1rem;border-top:1px solid var(--line)}
  .bar .right{margin-left:auto;display:flex;gap:.6rem}
  ul.posts{list-style:none;margin:0;padding:0;max-height:70vh;overflow:auto}
  ul.posts li{border-bottom:1px solid var(--line)}
  ul.posts button{width:100%;text-align:left;background:none;border:0;padding:.7rem .5rem;text-transform:none;
    letter-spacing:0;font-weight:500;font-size:.85rem;border-radius:0}
  ul.posts button:hover{background:var(--warm)}
  .tag{font-size:.65rem;text-transform:uppercase;letter-spacing:.06em;padding:.1rem .4rem;border-radius:3px;margin-left:.4rem}
  .draft{background:#f0e6d8;color:#8a6a3d}.live{background:#dfe9e0;color:#3f5a45}
  .status{font-size:.85rem;padding:.6rem .8rem;border-radius:5px;margin-bottom:1rem;display:none}
  .status.show{display:block}
  .ok{background:#e4ece5;color:#2f5137}.err{background:#f7e6e1;color:#8a3d29}
  .links-row{display:grid;grid-template-columns:1fr 1.6fr auto;gap:.5rem;align-items:start}
  .preview{border:1px dashed var(--line);border-radius:6px;padding:1rem;margin-top:.5rem;max-height:420px;overflow:auto;background:#fff}
  .preview h2{font-size:1.3rem}.preview h3{font-size:1.1rem}.preview img{max-width:100%;height:auto;border-radius:6px}
  details{margin-bottom:.9rem}summary{cursor:pointer;font-size:.8rem;font-weight:600}
</style>
</head>
<body>
<header>
  <h1>Balance Home Organizing — posts</h1>
  <span class="who">${user}</span>
</header>

<div class="wrap">
  <p class="status" id="status"></p>
  <div class="cols">
    <div class="card">
      <button class="primary" id="new" style="width:100%;margin-bottom:1rem">+ New post</button>
      <ul class="posts" id="list"><li style="padding:.7rem .5rem;opacity:.6">Loading…</li></ul>
    </div>

    <div class="card">
      <form id="form">
        <input type="hidden" id="orig_slug" />

        <label for="title">Title</label>
        <input id="title" required placeholder="5 Pantry Essentials for Busy Families" />

        <label for="body_md">Post <span class="hint">— paste straight from ChatGPT. Markdown formatting is kept.</span></label>
        <textarea id="body_md" placeholder="Paste your post here…"></textarea>

        <details>
          <summary>Preview</summary>
          <div class="preview" id="preview"></div>
        </details>

        <details>
          <summary>Image, address and summary</summary>
          <div style="margin-top:.8rem">
            <label for="thumb">Main image <span class="hint">— the picture that shows on the blog list and on Pinterest</span></label>
            <input id="thumb" placeholder="assets/img/posts/my-photo.jpg or a full https:// address" />
            <label for="slug">Web address <span class="hint">— filled in from the title; change only if you need to</span></label>
            <input id="slug" placeholder="5-pantry-essentials-for-busy-families" />
            <label for="excerpt">Summary <span class="hint">— shown on Pinterest and in Google. Left blank, it uses your opening lines.</span></label>
            <textarea id="excerpt" rows="2"></textarea>
          </div>
        </details>

        <details>
          <summary>Amazon products and Pinterest</summary>
          <div style="margin-top:.8rem">
            <label>Amazon links <span class="hint">— these appear at the end of the post</span></label>
            <div id="links"></div>
            <button type="button" class="ghost" id="addlink" style="margin-bottom:1rem">+ Add product</button>
            <label for="pin_url">Pinterest pin address <span class="hint">— paste it here after you pin this post</span></label>
            <input id="pin_url" placeholder="https://pinterest.com/pin/..." />
          </div>
        </details>

        <div class="bar">
          <button type="button" class="ghost" id="save">Save draft</button>
          <button type="button" class="primary" id="publish">Publish</button>
          <div class="right">
            <button type="button" class="ghost" id="view">View</button>
            <button type="button" class="danger" id="del">Delete</button>
          </div>
        </div>
      </form>
    </div>
  </div>
</div>

<script type="module">
const $ = (id) => document.getElementById(id);
const api = '/api/admin/posts';
let current = null;

function say(msg, bad) {
  const s = $('status');
  s.textContent = msg;
  s.className = 'status show ' + (bad ? 'err' : 'ok');
  if (!bad) setTimeout(() => (s.className = 'status'), 4000);
}

function slugify(t) {
  return t.toLowerCase().replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 80);
}

async function loadList() {
  const r = await fetch(api);
  const { posts = [] } = await r.json();
  $('list').innerHTML = posts.length ? '' : '<li style="padding:.7rem .5rem;opacity:.6">No posts yet</li>';
  for (const p of posts) {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.innerHTML = p.title + '<span class="tag ' + (p.status === 'published' ? 'live">live' : 'draft">draft') + '</span>';
    b.onclick = () => load(p.slug);
    li.appendChild(b);
    $('list').appendChild(li);
  }
}

function linkRow(l = {}) {
  const d = document.createElement('div');
  d.className = 'links-row';
  d.innerHTML = '<input placeholder="Product name" value="' + (l.label || '') + '" />' +
                '<input placeholder="https://amzn.to/..." value="' + (l.url || '') + '" />' +
                '<button type="button" class="danger" style="padding:.5rem .7rem">×</button>';
  d.querySelector('button').onclick = () => d.remove();
  $('links').appendChild(d);
}

function collectLinks() {
  return [...$('links').children].map((d) => {
    const [a, b] = d.querySelectorAll('input');
    return { label: a.value.trim(), url: b.value.trim() };
  }).filter((l) => l.url);
}

function blank() {
  current = null;
  $('orig_slug').value = '';
  for (const id of ['title', 'body_md', 'thumb', 'slug', 'excerpt', 'pin_url']) $(id).value = '';
  $('links').innerHTML = '';
  $('preview').innerHTML = '';
  $('title').focus();
}

async function load(slug) {
  const r = await fetch(api + '/' + encodeURIComponent(slug));
  if (!r.ok) return say('Could not open that post.', true);
  const { post } = await r.json();
  current = post;
  $('orig_slug').value = post.slug;
  $('title').value = post.title || '';
  $('body_md').value = post.body_md || '';
  $('thumb').value = post.thumb || '';
  $('slug').value = post.slug || '';
  $('excerpt').value = post.excerpt || '';
  $('pin_url').value = post.pin_url || '';
  $('links').innerHTML = '';
  try { JSON.parse(post.amazon_links || '[]').forEach(linkRow); } catch {}
  if (!post.body_md && post.body_html) {
    $('preview').innerHTML = post.body_html;
    say('This post came across from the old site, so the editor box is empty. Its page is unchanged — paste new text only if you want to rewrite it.');
  }
  window.scrollTo(0, 0);
}

async function save(status) {
  const title = $('title').value.trim();
  if (!title) return say('Give the post a title first.', true);
  const payload = {
    title,
    slug: $('slug').value.trim() || slugify(title),
    body_md: $('body_md').value,
    excerpt: $('excerpt').value.trim(),
    thumb: $('thumb').value.trim(),
    pin_url: $('pin_url').value.trim(),
    amazon_links: collectLinks(),
    status,
  };
  const editing = $('orig_slug').value;
  const r = await fetch(editing ? api + '/' + encodeURIComponent(editing) : api, {
    method: editing ? 'PUT' : 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const out = await r.json();
  if (!r.ok) return say(out.error || 'That did not save.', true);
  $('orig_slug').value = out.slug;
  $('slug').value = out.slug;
  say(status === 'published' ? 'Published — it is live on the site now.' : 'Draft saved.');
  loadList();
}

$('new').onclick = blank;
$('save').onclick = () => save('draft');
$('publish').onclick = () => save('published');
$('view').onclick = () => {
  const s = $('slug').value.trim() || slugify($('title').value);
  if (s) window.open('/blog/' + s, '_blank');
};
$('del').onclick = async () => {
  const s = $('orig_slug').value;
  if (!s) return blank();
  if (!confirm('Delete this post? This cannot be undone.')) return;
  const r = await fetch(api + '/' + encodeURIComponent(s), { method: 'DELETE' });
  if (!r.ok) return say('Could not delete that post.', true);
  say('Post deleted.');
  blank(); loadList();
};
$('addlink').onclick = () => linkRow();
$('title').addEventListener('blur', () => {
  if (!$('slug').value.trim() && $('title').value.trim()) $('slug').value = slugify($('title').value);
});

let t;
$('body_md').addEventListener('input', () => {
  clearTimeout(t);
  t = setTimeout(async () => {
    const r = await fetch('/api/admin/preview', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ body_md: $('body_md').value }),
    });
    if (r.ok) $('preview').innerHTML = (await r.json()).html;
  }, 400);
});

loadList();
</script>
</body>
</html>`;
}
