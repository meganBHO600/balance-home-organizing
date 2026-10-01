-- Balance Home Organizing — blog storage
--
-- Posts live here rather than in the static build so Megan can publish without
-- a git push or a rebuild. The Worker renders /blog and /blog/<slug> from this.

CREATE TABLE IF NOT EXISTS posts (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  slug          TEXT    NOT NULL UNIQUE,
  title         TEXT    NOT NULL,
  excerpt       TEXT    NOT NULL DEFAULT '',
  body_html     TEXT    NOT NULL DEFAULT '',
  thumb         TEXT,                                  -- listing image, site-relative or absolute
  author        TEXT    NOT NULL DEFAULT 'Megan Mossuto',
  status        TEXT    NOT NULL DEFAULT 'draft',      -- draft | published
  published_at  INTEGER,                               -- epoch ms; NULL until published
  created_at    INTEGER NOT NULL,
  updated_at    INTEGER NOT NULL,

  -- her operational workflow
  pin_url       TEXT,        -- the Pinterest pin this post is linked from
  pin_image     TEXT,        -- generated or uploaded pin graphic
  pin_status    TEXT NOT NULL DEFAULT 'none',  -- none | ready | posted
  amazon_links  TEXT NOT NULL DEFAULT '[]',    -- JSON array of {label, url, image}

  CHECK (status IN ('draft','published')),
  CHECK (pin_status IN ('none','ready','posted'))
);

CREATE INDEX IF NOT EXISTS idx_posts_published
  ON posts (status, published_at DESC);

-- Tags and categories, kept relational so archive pages stay cheap to query.
CREATE TABLE IF NOT EXISTS terms (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,                        -- tag | category
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  UNIQUE (kind, slug),
  CHECK (kind IN ('tag','category'))
);

CREATE TABLE IF NOT EXISTS post_terms (
  post_id INTEGER NOT NULL REFERENCES posts (id) ON DELETE CASCADE,
  term_id INTEGER NOT NULL REFERENCES terms (id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, term_id)
);

CREATE INDEX IF NOT EXISTS idx_post_terms_term ON post_terms (term_id);
