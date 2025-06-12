# post.py

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

# Customization for your posts
POST_PREFIX = "🤣 Daily Meme: " # Customize this prefix. Set to "" if you don't want a prefix.
DEFAULT_HASHTAGS = ["#Meme", "#LOL", "#Funny", "#DankMemes", "#Humor", "#Relatable", "#Comedy", "#MemesDaily", "#InstaMemes", "#Laughter", "#MemeLife", "#Hilarious", "#FunniestMemes"] # Customize your hashtags here

# Keywords to filter by (optional)
# Set to empty list [] to disable filtering.
# Only entries containing at least one of these keywords in their title will be considered if not empty.
KEYWORDS = [] # Keywords filter is now DISABLED

def fetch_memes():
    """
    Fetches entries from the RSS feed by first getting raw content,
    then parsing it, and attempts to find an image URL within the entry.
    Returns a list of tuples: (title, link, image_url_if_any).
    """
    if not RSS_URL:
        logging.error("RSS_URL environment variable is not set. Cannot fetch memes.")
        return []

    raw_feed_content = None
    try:
        # First, fetch the raw content of the RSS feed using requests
        response = requests.get(RSS_URL, timeout=15) # Added a timeout for robustness
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        raw_feed_content = response.text
        logging.info(f"Successfully fetched raw RSS feed content from {RSS_URL}. Length: {len(raw_feed_content)} characters. First 200 chars: '{raw_feed_content[:200]}'")

        # Now, pass the raw content to feedparser
        feed = feedparser.parse(raw_feed_content)
        if feed.bozo:
            logging.warning(f"Error parsing RSS feed (bozo bit set): {feed.bozo_exception}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch RSS feed content from {RSS_URL}: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred during RSS feed parsing: {e}")
        if raw_feed_content:
            logging.error(f"Raw content that caused error (first 200 chars): '{raw_feed_content[:200]}'")
        return []

    memes = []
    for entry in feed.entries:
        title = entry.title.lower()
        link = entry.link
        image_url = None

        # Check for keywords in the title if KEYWORDS list is not empty
        if KEYWORDS and not any(keyword in title for keyword in KEYWORDS):
            logging.info(f"Skipping entry '{entry.title}' - no matching keywords.")
            continue

        # Attempt to find an image URL from media:content or enclosures
        if hasattr(entry, 'media_content') and entry.media_content:
            for media_item in entry.media_content:
                if 'url' in media_item and media_item.get('type', '').startswith('image/'):
                    image_url = media_item['url']
                    break

        # Corrected typo: was .enclosure, should be .enclosures (this ensures correct parsing)
        if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'href' in enclosure and enclosure.get('type', '').startswith('image/'):
                    image_url = enclosure['href']
                    break

        # --- REVERTED CHANGE: This now adds entry regardless of image_url ---
        # If image_url is None, post_to_facebook will fall back to a link post
        memes.append((entry.title, link, image_url))
        logging.info(f"Found entry: '{entry.title}' (Link: {link}, Image: {image_url or 'N/A'})")

    return memes

def post_to_facebook(message, link, image_url=None):
    """
    Posts content to the Facebook page. Prioritizes image posts if an image_url is provided,
    otherwise falls back to a link post.
    """
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logging.error("Facebook PAGE_ACCESS_TOKEN or PAGE_ID environment variables are not set. Cannot post.")
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
        # Fallback to posting a link if no image URL
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

        # Construct the final message with prefix and hashtags
        final_message_parts = []
        if POST_PREFIX:
            final_message_parts.append(POST_PREFIX)

        final_message_parts.append(meme_title) # Add the original meme title

        # Append hashtags, joined by a space
        hashtags_string = " ".join(DEFAULT_HASHTAGS)
        final_message_parts.append(hashtags_string)

        final_message = "\n\n".join(final_message_parts) # Join parts with two newlines for spacing

        logging.info(f"Selected meme: Title='{meme_title}', Link='{meme_link}', Image='{meme_image_url}'")
        logging.info(f"Posting message: '{final_message}'")
        post_to_facebook(final_message, meme_link, meme_image_url)
    else:
        logging.info("No memes found or matched the filter. Skipping post.")
    logging.info("Meme posting process finished.")

if __name__ == "__main__":
    main()
