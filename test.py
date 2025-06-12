# test.py

import requests
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables (retrieved from GitHub Secrets)
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

# --- Configuration for the Test Post ---
TEST_MESSAGE_PREFIX = "Automated Test Post from GitHub Actions!"
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z") # Get current time in local timezone
TEST_MESSAGE = f"{TEST_MESSAGE_PREFIX}\nPosted at: {CURRENT_TIME} EEST" # Include timestamp for unique messages

def post_test_message_to_facebook(message):
    """
    Posts a test message to the Facebook page.
    """
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logging.error("Facebook PAGE_ACCESS_TOKEN or PAGE_ID environment variables are not set.")
        return None

    api_url = f"https://graph.facebook.com/{PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }

    logging.info(f"Attempting to post test message: '{message}' to page ID {PAGE_ID}")

    try:
        r = requests.post(api_url, data=payload)
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
    Main function to post the test message.
    """
    logging.info("Starting Facebook test post process...")
    post_test_message_to_facebook(TEST_MESSAGE)
    logging.info("Facebook test post process finished.")

if __name__ == "__main__":
    main()
