# twitter_scraper.py
"""
Uses snscrape (snscrape) to fetch tweets without needing API keys.
Install: pip install snscrape
Usage:
  python twitter_scraper.py --query "numerology OR life path" --max_tweets 200
"""
import os
import json
import time
import hashlib
from datetime import datetime
import snscrape.modules.twitter as sntwitter
from mongo_connection import insert_raw
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def hash_handle(handle):
    if not handle:
        return ""
    return hashlib.sha256(handle.encode("utf-8")).hexdigest()

def make_doc(tweet):
    metadata = {
        "id": tweet.id,
        "username": tweet.user.username,
        "replyCount": tweet.replyCount,
        "retweetCount": tweet.retweetCount,
        "likeCount": tweet.likeCount
    }
    return {
        "id": f"twitter_{tweet.id}",
        "platform": "twitter",
        "scraper": "twitter_scraper",
        "scrape_run_id": f"run_{int(time.time())}",
        "scraped_at": datetime.utcnow().isoformat(),
        "source_url": f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
        "post_type": "tweet",
        "author_handle_hash": hash_handle(tweet.user.username),
        "text": tweet.content,
        "language": tweet.lang if hasattr(tweet, "lang") else "en",
        "metadata": metadata
    }

def run(query, max_tweets=200):
    docs = []
    i = 0
    for tweet in tqdm(sntwitter.TwitterSearchScraper(query).get_items(), desc="tweets"):
        if i >= max_tweets:
            break
        docs.append(make_doc(tweet))
        i += 1
        time.sleep(0.05)
    out_path = f"data/raw/twitter/twitter_raw_{int(time.time())}.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    if docs:
        insert_raw(docs)
    print(f"Saved {len(docs)} tweets to {out_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--max_tweets", type=int, default=200)
    args = parser.parse_args()
    run(args.query, args.max_tweets)
