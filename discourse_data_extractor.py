import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

class DisourseDataExtractor:

  def __init__(self) -> None:
      self.DISCOURSE_BASE = "https://discourse.onlinedegree.iitm.ac.in"
      self.CATEGORY_ID = 34
      self.START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
      self.END_DATE   = datetime(2025, 4, 14, 23, 59, 59, tzinfo=timezone.utc)
      self.DISCOURSE_FORUM_SESSION = os.getenv("DISCOURSE_FORUM_SESSION")
      self.DISCOURSE_T_COOKIE = os.getenv("DISCOURSE_T_COOKIE")


      self.session = requests.Session()
      self.session.headers.update({
          "User-Agent": "Mozilla/5.0",
          "Accept": "application/json, text/javascript, */*; q=0.01",
          "X-Requested-With": "XMLHttpRequest",
          "Referer": f"{self.DISCOURSE_BASE}/c/courses/tds-kb",
          "Origin": self.DISCOURSE_BASE
      })
      self.session.cookies.set("_forum_session", self.DISCOURSE_FORUM_SESSION, domain="discourse.onlinedegree.iitm.ac.in", path="/")
      self.session.cookies.set("_t", self.DISCOURSE_T_COOKIE, domain="discourse.onlinedegree.iitm.ac.in", path="/")

  def parse_date(self,iso_str):
      return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

  def get_category_page(self,page=0):
      url = f"{self.DISCOURSE_BASE}/c/courses/tds-kb/{self.CATEGORY_ID}.json?page={page}"
      r = self.session.get(url)
      r.raise_for_status()
      return r.json()

  def get_topic_json(self,topic_id):
      url = f"{self.DISCOURSE_BASE}/t/{topic_id}.json"
      r = self.session.get(url)
      r.raise_for_status()
      return r.json()

  def filter_topics(self):
    filtered_topics = []
    page = 0
    while True:
        print(f"🔍 Fetching topic list page {page}...")
        data = self.get_category_page(page)
        topics = data.get("topic_list", {}).get("topics", [])
        if not topics:
            break

        for t in topics:
            try:
                created_at = self.parse_date(t["created_at"])
                if self.START_DATE <= created_at <= self.END_DATE:
                    filtered_topics.append({
                        "id": t["id"],
                        "slug": t["slug"],
                        "title": t["title"],
                        "created_at": created_at
                    })
            except Exception as e:
                print(f"⚠️ Skipping malformed topic: {e}")
        page += 1
        time.sleep(0.5)

    print(f"\n✅ Found {len(filtered_topics)} topics between Jan and Apr 2025.")
    return filtered_topics

  def discourse_extracted_data(self):

    post_dict = {}
    filtered_topics = self.filter_topics()
    for topic in filtered_topics:
        topic_id = topic["id"]
        slug = topic["slug"]
        topic_url = f"{self.DISCOURSE_BASE}/t/{slug}/{topic_id}"
        print(f"\n📄 Fetching Topic {topic_id}: {topic['title']}")

        try:
            topic_json = self.get_topic_json(topic_id)
            posts = topic_json.get("post_stream", {}).get("posts", [])
            if not posts:
                continue

            # Combine all post bodies (HTML), strip tags
            full_text = ""
            for post in posts:
                html = post.get("cooked", "")
                soup = BeautifulSoup(html, "html.parser")
                clean_text = soup.get_text(separator="\n", strip=True)
                full_text += clean_text + "\n\n"

            post_dict[topic_url] = full_text.strip()
            print(f"   ✅ Added: {topic_url}")

            time.sleep(0.3)

        except Exception as e:
            print(f"   ❌ Error in topic {topic_id}: {e}")
    return post_dict
