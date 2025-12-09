# Play Store scraper implementation (optional)

"""
Fetch Play Store app reviews using google_play_scraper (python).
Usage:
  python playstore_scraper.py --app com.example.app --max_reviews 200
"""
import os
import json
import time
import hashlib
from datetime import datetime
from google_play_scraper import reviews, Sort
from mongo_connection import insert_raw
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def hash_handle(handle):
    if not handle:
        return ""
    return hashlib.sha256(handle.encode("utf-8")).hexdigest()

def make_doc(app_id, review):
    metadata = {
        "id": review.get("reviewId") or review.get("id"),
        "app_id": app_id,
        "score": review.get("score"),
        "at": review.get("at").isoformat() if review.get("at") else None,
        "userName": review.get("userName")
    }
    return {
        "id": f"playstore_{metadata['id']}",
        "platform": "playstore",
        "scraper": "playstore_scraper",
        "scrape_run_id": f"run_{int(time.time())}",
        "scraped_at": datetime.utcnow().isoformat(),
        "source_url": f"https://play.google.com/store/apps/details?id={app_id}&reviewId={metadata['id']}",
        "post_type": "review",
        "author_handle_hash": hash_handle(review.get("userName","")),
        "text": review.get("content",""),
        "language": "en",
        "metadata": metadata
    }

def run(app_id, max_reviews=200):
    docs = []
    count = 0
    # reviews returns batches, use continuation token pattern
    result, token = reviews(app_id, lang='en', country='us', sort=Sort.NEW, count=200)
    for r in tqdm(result[:max_reviews], desc=f"reviews:{app_id}"):
        docs.append(make_doc(app_id, r))
    out_path = f"data/raw/playstore/playstore_raw_{app_id}_{int(time.time())}.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    if docs:
        insert_raw(docs)
    print(f"Saved {len(docs)} playstore reviews to {out_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", required=True, help="app id, e.g., com.example.app")
    parser.add_argument("--max_reviews", type=int, default=200)
    args = parser.parse_args()
    run(args.app, args.max_reviews)
