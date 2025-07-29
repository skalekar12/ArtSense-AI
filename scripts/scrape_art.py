import os
import csv
import time
import random
import re
from playwright.sync_api import sync_playwright, Page, TimeoutError
import requests

# --- Configuration ---
# 1. The starting URL for the list of artworks.
START_URL = "https://www.wikiart.org/en/vincent-van-gogh/all-works/text-list"
BASE_URL = "https://www.wikiart.org"

# 2. Output directories and files.
DATA_DIR = "data"
IMAGE_DIR = os.path.join(DATA_DIR, "raw_art")
CSV_FILE = os.path.join(DATA_DIR, "metadata.csv")
CSV_HEADER = ["filename", "artist", "title", "style_period", "year"]


# --- Helper Functions ---

def sanitize_filename(name: str) -> str:
    """Removes illegal characters from a string to make it a valid filename."""
    # Remove punctuation
    name = re.sub(r'[^\w\s-]', '', name)
    # Replace whitespace and hyphens with a single underscore
    name = re.sub(r'[-\s]+', '_', name)
    return name.strip('_')


def get_processed_files() -> set:
    """Reads the CSV file to get a set of already downloaded artwork filenames."""
    if not os.path.exists(CSV_FILE):
        return set()

    processed = set()
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header
            next(reader, None)
            for row in reader:
                if row:  # Ensure the row is not empty
                    processed.add(row[0])
    except (IOError, csv.Error) as e:
        print(f"Warning: Could not read existing CSV file. Starting fresh. Error: {e}")
        return set()

    return processed


def extract_artwork_details(page: Page, artwork_url: str) -> dict | None:
    """Navigates to an artwork's detail page and extracts its information."""
    try:
        print(f"  Navigating to details page: {artwork_url}")
        page.goto(artwork_url, wait_until="domcontentloaded", timeout=60000)

        # Respectful delay
        time.sleep(random.uniform(1.0, 2.5))

        # Extract high-resolution image URL
        # The main image is usually marked with itemprop="image"
        image_locator = page.locator('img[itemprop="image"]')
        image_url = image_locator.get_attribute('src')
        if not image_url:
            print(f"  [Warning] Could not find high-res image URL for {artwork_url}")
            return None

        # Extract Style/Period
        style_locator = page.locator('li.s-li-style a')
        style = style_locator.inner_text() if style_locator.count() > 0 else "N/A"

        return {
            "image_url": image_url,
            "style_period": style.strip()
        }
    except TimeoutError:
        print(f"  [Error] Timeout while loading details page: {artwork_url}")
        return None
    except Exception as e:
        print(f"  [Error] An unexpected error occurred on details page {artwork_url}: {e}")
        return None


# --- Main Execution ---

def main():
    """Main function to orchestrate the scraping process."""
    print("🎨 Starting ArtSense AI Scraper...")

    # Ensure output directories exist
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # Resume Capability: Load already processed files
    processed_files = get_processed_files()
    if processed_files:
        print(f"Resuming scrape. Found {len(processed_files)} previously downloaded artworks.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print(f"Navigating to start URL: {START_URL}")
            page.goto(START_URL, wait_until="domcontentloaded", timeout=60000)

            # Extract artist name once from the main page title
            h1_text = page.locator('h1').inner_text()
            artist_name = h1_text.split('by')[-1].strip()
            print(f"Artist found: {artist_name}")

            # Get all artwork list items
            artwork_items = page.locator('ul.painting-list-text > li').all()
            print(f"Found {len(artwork_items)} total artworks on the list page.")

            # Open CSV in append mode to save new entries
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header only if the file is new/empty
                if not processed_files and os.path.getsize(CSV_FILE) == 0:
                    writer.writerow(CSV_HEADER)

                for i, item in enumerate(artwork_items):
                    try:
                        title_locator = item.locator('a')
                        title = title_locator.inner_text().strip()

                        # Generate a clean filename to check if it's already processed
                        sanitized_title = sanitize_filename(title)
                        sanitized_artist = sanitize_filename(artist_name)
                        filename = f"{sanitized_artist}_{sanitized_title}.jpg"

                        # --- Resume Logic ---
                        if filename in processed_files:
                            print(f"Skipping ({i + 1}/{len(artwork_items)}): '{title}' (Already downloaded)")
                            continue

                        print(f"Processing ({i + 1}/{len(artwork_items)}): '{title}'")

                        year_locator = item.locator('span.year')
                        year = year_locator.inner_text().strip() if year_locator.count() > 0 else "N/A"

                        details_url_relative = title_locator.get_attribute('href')
                        details_url_full = f"{BASE_URL}{details_url_relative}"

                        # --- Data Extraction from Detail Page ---
                        details = extract_artwork_details(page, details_url_full)
                        if not details:
                            print(f"  [Skipped] Could not retrieve details for '{title}'.")
                            continue

                        # --- Data Saving ---
                        image_path = os.path.join(IMAGE_DIR, filename)

                        # Download the image
                        print(f"  Downloading image from: {details['image_url']}")
                        response = requests.get(details['image_url'], timeout=60)
                        response.raise_for_status()  # Raise an exception for bad status codes

                        with open(image_path, 'wb') as img_file:
                            img_file.write(response.content)
                        print(f"  Image saved to: {image_path}")

                        # Append metadata to CSV
                        metadata_row = [filename, artist_name, title, details['style_period'], year]
                        writer.writerow(metadata_row)
                        f.flush()  # Ensure it's written to disk immediately

                        # Add to our set to prevent re-downloading in this session
                        processed_files.add(filename)

                        # Respectful Scraping: Pause before the next item
                        time.sleep(random.uniform(1.5, 3.0))

                    except Exception as e:
                        print(f"[ERROR] Failed to process an item. Error: {e}. Moving to the next one.")
                        continue

        except TimeoutError:
            print(f"Fatal Error: Timed out while loading the main page: {START_URL}")
        except Exception as e:
            print(f"A fatal error occurred: {e}")
        finally:
            browser.close()
            print("✅ Scraper finished its run.")


if __name__ == "__main__":
    main()