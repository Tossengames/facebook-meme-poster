import os
import requests
import feedparser
import random

# Config
page_id = os.getenv("PAGE_ID")
access_token = os.getenv("PAGE_ACCESS_TOKEN")
rss_url = "https://www.reddit.com/r/memes/.rss"

# Parse RSS
feed = feedparser.parse(rss_url)
entries = [entry for entry in feed.entries if 'i.redd.it' in entry.link]

# Select a good meme
if not entries:
    print("No memes found.")
    exit()

entry = random.choice(entries)
title = entry.title
image_url = entry.link

# Facebook post
url = f"https://graph.facebook.com/{page_id}/photos"
payload = {
    'url': image_url,
    'caption': title,
    'access_token': access_token
}

response = requests.post(url, data=payload)

if response.status_code == 200:
    print("✅ Meme posted successfully!")
else:
    print("❌ Failed to post meme.")
    print(response.text)
