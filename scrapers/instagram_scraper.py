# Instagram scraper implementation (optional)

"""
Instaloader fetches posts and comments from public profiles.
Usage:
  python instagram_scraper.py --profiles "numerology_page,another_page" --max_posts 5 --max_comments 50

Note:
- Instaloader respects Instagram rules; avoid heavy scraping.
- For business accounts you control, use Facebook Graph API instead.
"""
import os
import json
import time
import hashlib
from datetime import datetime
import instaloader
from mongo_connection import insert_raw
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

L = instaloader.Instaloader(download_comments=False, save_metadata=False, compress_json=False)

def hash_handle(handle):
    if not handle:
        return ""
    return hashlib.sha256(handle.encode("utf-8")).hexdigest()

def make_doc(profile, post_shortcode, comment, caption):
    metadata = {
        "id": comment['id'] if isinstance(comment, dict) and 'id' in comment else f"{post_shortcode}_{hashlib.sha1(comment[:30].encode()).hexdigest()}",
        "post_shortcode": post_shortcode,
        "profile": profile,
        "caption": caption
    }
    return {
        "id": f"instagram_{metadata['id']}",
        "platform": "instagram",
        "scraper": "instagram_scraper",
        "scrape_run_id": f"run_{int(time.time())}",
        "scraped_at": datetime.utcnow().isoformat(),
        "source_url": f"https://www.instagram.com/p/{post_shortcode}/",
        "post_type": "comment",
        "author_handle_hash": hash_handle(comment.owner_username if hasattr(comment, 'owner_username') else ""),
        "text": comment.text if hasattr(comment, 'text') else (comment.get('text') if isinstance(comment, dict) else str(comment)),
        "language": "en",
        "metadata": metadata
    }

def run(profiles, max_posts=3, max_comments=50):
    docs = []
    for profile_name in profiles:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        count_posts = 0
        for post in tqdm(profile.get_posts(), desc=f"posts:{profile_name}"):
            if count_posts >= max_posts:
                break
            caption = post.caption or ""
            shortcode = post.shortcode
            # Instaloader does not expose comments easily via API; we can use post.get_comments()
            ccount = 0
            for comment in post.get_comments():
                docs.append(make_doc(profile_name, shortcode, comment, caption))
                ccount += 1
                if ccount >= max_comments:
                    break
            count_posts += 1
            time.sleep(1)
    out_path = f"data/raw/instagram/instagram_raw_{int(time.time())}.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([d for d in docs], f, ensure_ascii=False, indent=2)
    if docs:
        insert_raw(docs)
    print(f"Saved {len(docs)} instagram comments to {out_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", required=True, help="comma separated profile names")
    parser.add_argument("--max_posts", type=int, default=3)
    parser.add_argument("--max_comments", type=int, default=30)
    args = parser.parse_args()
    profiles = [p.strip() for p in args.profiles.split(",")]
    run(profiles, args.max_posts, args.max_comments)
