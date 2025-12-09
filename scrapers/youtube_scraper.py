# YouTube scraper implementation

"""
Usage:
  python youtube_scraper.py --query "life path number" --max_videos 10 --max_comments 100

Requires: set YOUTUBE_API_KEY in .env
"""
import os
import json
import time
import hashlib
from datetime import datetime
from googleapiclient.discovery import build
from mongo_connection import insert_raw
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def hash_handle(handle):
    if not handle:
        return ""
    return hashlib.sha256(handle.encode("utf-8")).hexdigest()

def make_doc(video_id, comment, video_title):
    metadata = {
        "id": comment["id"],
        "video_id": video_id,
        "video_title": video_title,
        "likeCount": comment["snippet"].get("likeCount", 0),
        "publishedAt": comment["snippet"].get("publishedAt")
    }
    return {
        "id": f"youtube_{comment['id']}",
        "platform": "youtube",
        "scraper": "youtube_scraper",
        "scrape_run_id": f"run_{int(time.time())}",
        "scraped_at": datetime.utcnow().isoformat(),
        "source_url": f"https://www.youtube.com/watch?v={video_id}&lc={comment['id']}",
        "post_type": "comment",
        "author_handle_hash": hash_handle(comment["snippet"].get("authorDisplayName","")),
        "text": comment["snippet"].get("textDisplay",""),
        "language": "en",
        "metadata": metadata
    }

def run(query, max_videos=10, max_comments=50):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    search_response = youtube.search().list(q=query, type="video", part="id,snippet", maxResults=max_videos).execute()
    docs = []
    for item in tqdm(search_response.get("items", []), desc="videos"):
        vid = item["id"]["videoId"]
        title = item["snippet"]["title"]
        # fetch comments
        try:
            request = youtube.commentThreads().list(part="snippet", videoId=vid, maxResults=100, textFormat="plainText")
            response = request.execute()
            count = 0
            while response and count < max_comments:
                for it in response.get("items", []):
                    top = it["snippet"]["topLevelComment"]
                    docs.append(make_doc(vid, top, title))
                    count += 1
                    if count >= max_comments:
                        break
                if count >= max_comments:
                    break
                if "nextPageToken" in response:
                    request = youtube.commentThreads().list(part="snippet", videoId=vid, pageToken=response["nextPageToken"], maxResults=100, textFormat="plainText")
                    response = request.execute()
                else:
                    break
                time.sleep(1)
        except Exception as e:
            print("Comments fetch error:", e)
        time.sleep(1)  # polite
    # save file and insert
    out_path = f"data/raw/youtube/youtube_raw_{int(time.time())}.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    if docs:
        insert_raw(docs)
    print(f"Saved {len(docs)} youtube comments to {out_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--max_videos", type=int, default=10)
    parser.add_argument("--max_comments", type=int, default=50)
    args = parser.parse_args()
    run(args.query, args.max_videos, args.max_comments)
