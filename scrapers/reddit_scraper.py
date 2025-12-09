# Reddit scraper implementation

"""
Usage:
  python reddit_scraper.py --subreddits numerology,astrology --limit 50

Requires: create Reddit app and set env vars:
REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, MONGO_URI
"""
import os
import argparse
import json
import time
import hashlib
from datetime import datetime
from praw import Reddit
from pymongo.errors import DuplicateKeyError
from mongo_connection import insert_raw
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "insight-scraper/0.1")

def hash_handle(handle):
    if not handle:
        return ""
    return hashlib.sha256(handle.encode("utf-8")).hexdigest()

def make_doc(platform, source_url, post_type, text, metadata, author_handle):
    return {
        "id": f"{platform}_{metadata.get('id')}",
        "platform": platform,
        "scraper": "reddit_scraper",
        "scrape_run_id": f"run_{int(time.time())}",
        "scraped_at": datetime.utcnow().isoformat(),
        "source_url": source_url,
        "post_type": post_type,
        "author_handle_hash": hash_handle(author_handle),
        "text": text,
        "language": "en",
        "metadata": metadata
    }

def run(subreddits, limit):
    reddit = Reddit(client_id=REDDIT_CLIENT_ID,
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT)
    docs = []
    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        # choose top/hot/new as needed
        for post in tqdm(subreddit.hot(limit=limit), desc=f"posts:{sub}"):
            post.comments.replace_more(limit=0)
            # collect top-level comments
            for comment in post.comments.list()[:200]:
                metadata = {
                    "id": comment.id,
                    "post_id": post.id,
                    "subreddit": sub,
                    "post_title": post.title,
                    "score": getattr(comment, "score", None),
                    "created_utc": getattr(comment, "created_utc", None),
                    "permalink": f"https://reddit.com{comment.permalink}"
                }
                doc = make_doc("reddit", metadata["permalink"], "comment", comment.body, metadata, getattr(comment,"author",""))
                docs.append(doc)
            time.sleep(1)  # polite pacing
    # save to local file
    out_path = f"data/raw/reddit/reddit_raw_{int(time.time())}.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    # insert to mongo
    if docs:
        insert_raw(docs)
    print(f"Saved {len(docs)} reddit comments to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddits", required=True, help="comma separated list")
    parser.add_argument("--limit", type=int, default=20, help="posts per subreddit")
    args = parser.parse_args()
    subs = [s.strip() for s in args.subreddits.split(",")]
    run(subs, args.limit)
