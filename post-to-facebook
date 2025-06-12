# post-to-facebook.py

import feedparser
import requests
import random
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables (retrieved from GitHub Secrets)
RSS_URL = os.getenv("RSS_URL")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

# Keywords to filter by (optional)
# Only entries containing at least one of these keywords in their title will be considered.
KEYWORDS = ["funny", "meme", "lol", "humor", "relatable", "joke"]

def fetch_memes():
    """
    Fetches entries from the RSS feed and filters them based on keywords.
    Attempts to find an image URL within the entry.
    Returns a list of tuples: (title, link, image_url_if_any).
    """
    if not RSS_URL:
        logging.error("RSS_URL environment variable is not set.")
        return []

    try:
        feed = feedparser.parse(RSS_URL)
        if feed.bozo:
            logging.warning(f"Error parsing RSS feed (bozo bit set): {feed.bozo_exception}")

    except Exception as e:
        logging.error(f"Failed to parse RSS feed from {RSS_URL}: {e}")
        return []

    memes = []
    for entry in feed.entries:
        title = entry.title.lower()
        link = entry.link
        image_url = None

        # Check for keywords in the title
        if KEYWORDS and not any(keyword in title for keyword in KEYWORDS):
            logging.info(f"Skipping entry '{entry.title}' - no matching keywords.")
            continue

        # Attempt to find an image URL
        # Check media:content (common for images in feeds)
        if hasattr(entry, 'media_content') and entry.media_content:
            for media_item in entry.media_content:
                if 'url' in media_item and media_item.get('type', '').startswith('image/'):
                    image_url = media_item['url']
                    break
        
        # Check enclosures (also common for attachments like images)
        if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'href' in enclosure and enclosure.get('type', '').startswith('image/'):
                    image_url = enclosure['href']
                    break

        memes.append((entry.title, link, image_url))
        logging.info(f"Found meme: '{entry.title}' (Link: {link}, Image: {image_url or 'N/A'})")

    return memes

def post_to_facebook(message, link, image_url=None):
    """
    Posts content to the Facebook page. Prioritizes image posts if an image_url is provided,
    otherwise falls back to a link post.
    """
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logging.error("Facebook PAGE_ACCESS_TOKEN or PAGE_ID environment variables are not set.")
        return None

    api_url = f"https://graph.facebook.com/{PAGE_ID}"
    payload = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    if image_url:
        # Attempt to post an image
        endpoint = f"{api_url}/photos"
        payload["url"] = image_url
        payload["caption"] = message
        logging.info(f"Attempting to post image: '{message}' from {image_url}")
    else:
        # Fallback to posting a link
        endpoint = f"{api_url}/feed"
        payload["message"] = message
        payload["link"] = link
        logging.info(f"Attempting to post link: '{message}' to {link}")

    try:
        r = requests.post(endpoint, data=payload)
        r.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        response_data = r.json()
        logging.info(f"Successfully posted (status: {r.status_code}). Response: {response_data}")
        return response_data
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error posting to Facebook: {http_err} - Response: {r.text}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error posting to Facebook: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error posting to Facebook: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An unexpected request error occurred: {req_err}")
    except ValueError as json_err:
        logging.error(f"JSON decoding error from Facebook response: {json_err} - Raw response: {r.text}")
    return None

def main():
    """
    Main function to fetch a random meme and post it to Facebook.
    """
    logging.info("Starting meme posting process...")
    memes = fetch_memes()

    if memes:
        meme_title, meme_link, meme_image_url = random.choice(memes)
        logging.info(f"Selected meme: Title='{meme_title}', Link='{meme_link}', Image='{meme_image_url}'")
        post_to_facebook(meme_title, meme_link, meme_image_url)
    else:
        logging.info("No memes found or matched the filter.")
    logging.info("Meme posting process finished.")

if __name__ == "__main__":
    main()
