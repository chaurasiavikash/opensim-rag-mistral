#!/usr/bin/env python3
"""
OpenSim API Documentation Scraper

This script scrapes the OpenSim API documentation from simtk.org,
extracting class and function documentation for the RAG system.
"""

import os
import time
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse

# Configuration
BASE_URL = "https://simtk.org/api_docs/opensim/api_docs/"
OUTPUT_DIR = "../data/api_docs"
DELAY = 1  # Delay between requests in seconds

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# Store metadata about scraped pages
metadata = []
# Track visited URLs to avoid duplicates
visited_urls = set()

def clean_filename(filename):
    """Clean a string to make it suitable for a filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def extract_content(soup):
    """Extract the main content from a BeautifulSoup object."""
    # Find the main content div - this may need adjustment based on the site structure
    content_div = soup.find("div", {"class": "contents"})
    if not content_div:
        content_div = soup.find("div", {"id": "content"})
    if not content_div:
        # If specific content div not found, use the body
        content_div = soup.body
    
    # Extract text content
    if content_div:
        # Remove script and style elements
        for script in content_div(["script", "style"]):
            script.decompose()
        
        # Get text
        text = content_div.get_text(separator="\n", strip=True)
        
        # Clean up text
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n\n".join(lines)
        
        return text
    
    return ""

def extract_links(soup, base_url):
    """Extract links from a BeautifulSoup object."""
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        # Skip empty links, anchors, and javascript links
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        
        # Make absolute URL
        absolute_url = urljoin(base_url, href)
        
        # Only include links to the same domain
        if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
            links.append(absolute_url)
    
    return links

def scrape_page(url, depth=0, max_depth=3):
    """Scrape a page and its linked pages up to max_depth."""
    if depth > max_depth or url in visited_urls:
        return
    
    print(f"Scraping: {url}")
    visited_urls.add(url)
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title
        title_elem = soup.find("title")
        title = title_elem.text if title_elem else "Untitled"
        
        # Clean title for filename
        clean_title = clean_filename(title)
        
        # Extract content
        content = extract_content(soup)
        
        # Save content to file
        filename = f"{clean_title}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d')}\n")
            f.write("\n")
            f.write(content)
        
        # Add to metadata
        metadata.append({
            "title": title,
            "url": url,
            "filename": filename,
            "date_scraped": time.strftime("%Y-%m-%d"),
            "content_length": len(content)
        })
        
        # Extract links for further scraping
        links = extract_links(soup, url)
        
        # Delay to be respectful to the server
        time.sleep(DELAY)
        
        # Recursively scrape linked pages
        for link in links:
            scrape_page(link, depth + 1, max_depth)
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")

def scrape_class_list():
    """Scrape the class list page to get links to all classes."""
    class_list_url = urljoin(BASE_URL, "classes.html")
    
    try:
        response = requests.get(class_list_url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all class links
        class_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "class" in href and href.endswith(".html"):
                class_links.append(urljoin(BASE_URL, href))
        
        return class_links
    
    except Exception as e:
        print(f"Error scraping class list: {e}")
        return []

def main():
    """Main function to scrape OpenSim API documentation."""
    print("Starting OpenSim API documentation scraper...")
    
    # Scrape the main page
    scrape_page(BASE_URL, max_depth=1)
    
    # Scrape class list
    class_links = scrape_class_list()
    print(f"Found {len(class_links)} classes to scrape.")
    
    # Scrape each class page
    for link in class_links:
        scrape_page(link, max_depth=0)  # Don't follow links from class pages
    
    # Save metadata
    metadata_file = os.path.join(OUTPUT_DIR, "metadata.json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    # Create a DataFrame for easier analysis
    df = pd.DataFrame(metadata)
    csv_file = os.path.join(OUTPUT_DIR, "metadata.csv")
    df.to_csv(csv_file, index=False)
    
    print(f"\nScraping completed. Scraped {len(metadata)} pages.")
    print(f"Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
