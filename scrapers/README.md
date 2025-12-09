# Scrapers Playbook — What to scrape, where, and how

**Goal:** collect 200–500 high-quality user statements across platforms (Reddit, YouTube, Instagram, App Store/Play Store, Quora, Twitter/X). Store raw JSON into `data/raw/<platform>/` and insert into `raw_comments` collection in MongoDB.

## Principles

- Quality > quantity: limit to 200–500 comments per platform.
- Save raw output unchanged (don’t clean until ETL).
- Always include source metadata (url, timestamp, author-hash).
- Pseudonymize author handles (hash them) — no PII.
- Respect platform TOS / use official APIs where available.

---

## Standard fields to capture (every platform)

Use this JSON skeleton for every scraped item:

```json
{
  "id": "<platform>_<source_id>",
  "platform": "reddit|youtube|instagram|playstore|appstore|quora|twitter",
  "scraper": "<script_name>",
  "scrape_run_id": "<uuid>",
  "scraped_at": "2025-12-09T15:04:00Z",
  "source_url": "https://...",
  "post_type": "comment|post|review|caption",
  "author_handle_hash": "<sha256_of_handle_or_empty>",
  "text": "Raw text content (exact)",
  "language": "en|hi|etc",
  "metadata": {
    "upvotes": 123,
    "replies_count": 12,
    "rating": 4.0,
    "title": "video/post title",
    "video_id": "..."
  }
}
```

Keep this minimal — add platform-specific metadata in `metadata`.

---

## Platform-by-platform: what to scrape & how (step-by-step)

---

## 1) Reddit (best source for honest long-form comments)

**Why:** candid, long posts and comment threads; high signal for pain/desire.

**What to scrape (prioritize):**

- Post title
- Top-level comments (first 100 comments per thread)
- Comment body, score (upvotes), created_utc, parent_id, permalink
- Subreddit name
- Post URL & post id
- Number of comments
- Author handle hashed

**Tools (recommended):**

- PRAW (Python Reddit API Wrapper) — official API
- Or Apify / Apify actor if no API access

**Step-by-step:**

1. Register Reddit app, get `client_id`, `client_secret`, `user_agent`.
2. Choose seed subreddits (e.g., r/numerology, r/astrology, r/selfimprovement).
3. For each subreddit, fetch N recent/top posts (N=20–50).
4. For each post, fetch comments (limit e.g., 100). Flatten threaded comments to capture replies optionally.
5. For each comment/post build JSON skeleton and write to `data/raw/reddit/`.
6. Insert into Mongo `raw_comments` collection.

**Notes:**

- Use `limit` and `sort` parameters (hot/new/top) to vary signal.
- Respect API rate limits (use PRAW’s built-in backoff).
- Keep run size bounded (don’t fetch entire subreddits).

---

## 2) YouTube (video comments — emotional and candid)

**Why:** long comment threads, narrative examples, strong emotion.

**What to scrape:**

- Video title
- Video id
- Comment id, comment text, likeCount, publishedAt
- Reply count / thread info
- Video URL
- Channel name (hash)
- For top comments and replies (limit per video e.g., 100)

**Tools:**

- YouTube Data API (v3) — official
- Or lightweight wrappers (googleapiclient)

**Step-by-step:**

1. Create Google Cloud project, enable YouTube Data API, get API key.
2. Search videos by keywords: “life path number”, “numerology”, “birth number”.
3. For each video id, call `commentThreads.list` (part=snippet) with `maxResults` (50–100).
4. Extract snippet.topLevelComment.snippet.textDisplay, likeCount, publishedAt.
5. Save JSON to `data/raw/youtube/` and insert to Mongo.

**Notes:**

- API quota: track usage; avoid heavy pagination in first runs.
- Include video title so you can group comments by topic later.

---

## 3) Instagram (comments on public posts & reels)

**Why:** short emotional reactions, language/phrasing patterns.

**What to scrape:**

- Post/reel caption
- Comment text
- Comment id, created_at, like_count
- Post URL, account (hash)
- Hashtags used

**Tools:**

- Facebook Graph API (for business accounts you control)
- For public scraping: Instaloader (python) or Apify / Phantombuster (ease)
- Playwright/selenium as last resort (avoid if TOS prohibits)

**Step-by-step:**

1. Prefer posts from high-engagement public accounts (numerology pages).
2. Use Apify / Phantombuster actor or Instaloader to fetch recent posts and comments (limit e.g., 200 comments in total per account).
3. Save raw JSON to `data/raw/instagram/`.
4. Hash author handles, store caption + comment.

**Notes:**

- Instagram scraping is brittle; start with a few accounts.
- If you own a business account, Graph API is safer but limited to your content.

---

## 4) Play Store / App Store (app reviews)

**Why:** explicit user complaints and praise about existing apps (pain/gap data).

**What to scrape:**

- App name
- Review id
- Review text
- Rating (1–5)
- Review date
- Device / version (if available)
- Reply from developer (if any)

**Tools:**

- 42matters, AppFollow (paid) or `google-play-scraper` (node) for Play Store
- `app-store-scraper` (node) or use App Store API via Apple if you have access
- Apify actors for app stores

**Step-by-step:**

1. Identify competitor apps (Co-Star, The Pattern, numerology apps).
2. Use `google-play-scraper` or Apify to fetch top N (e.g., 500) recent reviews.
3. Save raw JSON to `data/raw/playstore/` (and `appstore` similarly).
4. Insert into Mongo.

**Notes:**

- Reviews contain structured `rating` — great for quick sentiment proxies.
- Preserve review text exactly.

---

## 5) Quora (long-form questions & answers)

**Why:** users explain beliefs & reasoning; good for mental models.

**What to scrape:**

- Question title
- Top answers and comments
- Answer text, author (hash), upvotes
- Question URL

**Tools:**

- Apify Quora actor
- Manual copy-paste for narrow tests (quick founder method)

**Step-by-step:**

1. Search Quora for: “numerology accuracy”, “life purpose”, “how to understand myself”.
2. Use Apify actor or manual fetch to capture question + top answers.
3. Save to `data/raw/quora/`.

**Notes:**

- Quora scraping may be brittle; manual capture is acceptable for small samples.

---

## 6) Twitter / X (short opinions & trends)

**Why:** quick sentiment, trending opinions, skepticism signals.

**What to scrape:**

- Tweet id, text, created_at
- Retweet/like counts
- Thread context (if within a thread)
- Hashtags

**Tools:**

- Official X API (if available)
- Twint (unofficial) — use cautiously due to TOS
- Apify / third-party scrapers

**Step-by-step:**

1. Use X API to search keywords/hashtags: #numerology, #astrology, #selfawareness.
2. Fetch recent tweets (limit 200–500).
3. Save to `data/raw/twitter/`.

**Notes:**

- X/Twitter official API access may require levels; plan accordingly.

---

## Quick scraper run plan (founder, first pass — 7–10 days)

- Day 1: Reddit — 200 comments (5–10 top threads) → saved
- Day 2: YouTube — 150 comments (10–15 videos) → saved
- Day 3: Play Store/App Store — 200 reviews across 4 apps → saved
- Day 4: Instagram — 150 comments from 5 creators → saved
- Day 5: Quora + Twitter — 100 items each → saved
- Day 6: Sanity check + de-duplication; ensure all raw JSON files saved
- Day 7: Insert raw into Mongo & run basic clean script

Total target: ~1,000 raw items (ample for AI clustering).

---

### Run a Reddit scraper (high-level)

```bash
# pipelines/run_reddit.sh
python scrapers/reddit_scraper.py --subreddit numerology --limit 50
```

### Insert raw JSON into Mongo

```bash
python storage/insert_raw.py --file data/raw/reddit/comments_batch1.json
```

### Simple ETL run

```bash
python etl/process_batch.py --input data/raw/reddit/comments_batch1.json --output data/processed/reddit/clean1.json
```

(You’ll have these scripts in the repo; keep them simple and idempotent.)

---

## Platform-specific best practices & precautions

- **API first:** Always use official API if available (YouTube Data API, Reddit API, X API).
- **Rate limits:** Respect rate limits; put sleep/backoff; run small batches.
- **Avoid PII:** Hash handles; do not store emails/phones if accidentally scraped.
- **Robots.txt & TOS:** Read platform terms if you plan to scale or publish text.
- **Attribution:** Save `source_url` and `scraped_at` for every item (audit trail).
- **Data retention:** Decide how long to keep raw data (e.g., 365 days).
- **Ethics:** Use public content for research; do not republish verbatim in public-facing materials without paraphrasing or permission.

---

## Quick-check list before running scrapers

- [ ] MongoDB connection string configured in `.env`
- [ ] API keys placed in `config/credentials.json` (NOT in git)
- [ ] `data/raw/<platform>/` folder exists
- [ ] You have targeted seed posts / app ids / handles listed
- [ ] Rate limiter / backoff configured in scripts
- [ ] Run small test (10 items) before full run

---

## After scraping: minimal validation steps (1 hour)

1. Ensure each JSON has `platform`, `source_url`, `scraped_at`, `text`.
2. Check for duplicates (same text + source) and remove duplicates.
3. Confirm author_handle is hashed (or blank).
4. Randomly inspect 10 items for correctness.
5. Move raw JSON to `/data/raw/<platform>/completed/` and insert into Mongo.

---

## How to use the data next (fast founder steps)

1. Batch into 50–100 comments per AI prompt chunk.
2. Run clustering prompt (themes / pains / desires).
3. Extract top 10 themes, top emotional triggers, 3–5 personas.
4. Convert themes into product opportunities and messaging.
