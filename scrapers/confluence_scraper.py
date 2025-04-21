#!/usr/bin/env python3
"""
OpenSim Documentation Scraper for Atlassian Confluence

This script scrapes the OpenSim documentation from the Atlassian Confluence site.
It navigates through the documentation pages, extracts content, and saves it to files.
"""

import os
import time
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse

# Configuration
BASE_URL = "https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim"
OUTPUT_DIR = "../data/confluence_docs"
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

# List of main sections to scrape - Updated with correct URLs
MAIN_SECTIONS = [
    {"url": "/overview", "name": "Overview"},
    {"url": "/pages/53084226", "name": "Workflows"},
    {"url": "/pages/53084161", "name": "UsersGuide"},
    {"url": "/pages/53084170", "name": "Tutorials"},
    {"url": "/pages/53084173", "name": "Troubleshooting"},
    {"url": "/pages/53084176", "name": "Models"}
]

# Track visited URLs to avoid duplicates
visited_urls = set()
# Store metadata about scraped pages
metadata = []

def clean_filename(filename):
    """Clean a string to make it suitable for a filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def extract_content(soup):
    """Extract the main content from a BeautifulSoup object."""
    # Find the main content div - this may need adjustment based on the site structure
    content_div = soup.find("div", {"id": "main-content"})
    if not content_div:
        content_div = soup.find("div", {"class": "wiki-content"})
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
        # Skip empty links, anchors, and external links
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

def main():
    """Main function to scrape OpenSim documentation."""
    print("Starting OpenSim documentation scraper...")
    
    # Try to scrape the main documentation page first
    main_url = "https://opensim.stanford.edu/"
    print(f"Scraping main page: {main_url}")
    try:
        response = requests.get(main_url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title and content
        title = "OpenSim Main Page"
        content = extract_content(soup)
        
        # Save content to file
        filename = "OpenSim_Main_Page.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"URL: {main_url}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d')}\n")
            f.write("\n")
            f.write(content)
        
        # Add to metadata
        metadata.append({
            "title": title,
            "url": main_url,
            "filename": filename,
            "date_scraped": time.strftime("%Y-%m-%d"),
            "content_length": len(content)
        })
        
        # Extract links for further scraping
        links = extract_links(soup, main_url)
        
        # Scrape linked pages
        for link in links:
            if "opensim.stanford.edu" in link:
                scrape_page(link, max_depth=1)
    
    except Exception as e:
        print(f"Error scraping main page: {e}")
    
    # Try to scrape the documentation site
    doc_url = "https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/overview"
    print(f"Scraping documentation page: {doc_url}")
    try:
        scrape_page(doc_url, max_depth=2)
    except Exception as e:
        print(f"Error scraping documentation page: {e}")
    
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
