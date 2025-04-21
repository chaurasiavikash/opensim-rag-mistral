#!/usr/bin/env python3
"""
OpenSim Scholar Scraper

This script searches for and collects open access papers related to OpenSim
from Google Scholar and other academic sources.
"""

import os
import time
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin, quote_plus

# Configuration
OUTPUT_DIR = "../data/papers"
DELAY = 3  # Delay between requests in seconds (higher for academic sites)
MAX_PAPERS = 100  # Maximum number of papers to collect

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

# Search queries
SEARCH_QUERIES = [
    "OpenSim biomechanics software",
    "OpenSim musculoskeletal modeling",
    "OpenSim gait analysis",
    "OpenSim simulation tutorial",
    "OpenSim Stanford biomechanics"
]

# Store metadata about scraped papers
metadata = []

def clean_filename(filename):
    """Clean a string to make it suitable for a filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def search_scholar(query, start=0, num_results=10):
    """Search Google Scholar for papers."""
    base_url = "https://scholar.google.com/scholar"
    params = {
        "q": query,
        "start": start,
        "hl": "en",
        "as_sdt": "0,5",  # Include citations
        "num": num_results
    }
    
    # Construct URL
    url_parts = []
    for key, value in params.items():
        url_parts.append(f"{key}={quote_plus(str(value))}")
    url = f"{base_url}?{'&'.join(url_parts)}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        return response.text
    except Exception as e:
        print(f"Error searching Google Scholar: {e}")
        return None

def extract_paper_info(html):
    """Extract paper information from Google Scholar search results."""
    if not html:
        return []
    
    papers = []
    soup = BeautifulSoup(html, "html.parser")
    
    # Find all paper entries
    for result in soup.select(".gs_r.gs_or.gs_scl"):
        try:
            # Extract title and link
            title_elem = result.select_one(".gs_rt a")
            title = title_elem.text if title_elem else "Unknown Title"
            link = title_elem["href"] if title_elem and "href" in title_elem.attrs else None
            
            # Extract authors, venue, year
            authors_venue_elem = result.select_one(".gs_a")
            authors_venue_text = authors_venue_elem.text if authors_venue_elem else ""
            
            # Try to extract year using regex
            year_match = re.search(r'\b(19|20)\d{2}\b', authors_venue_text)
            year = year_match.group(0) if year_match else "Unknown Year"
            
            # Extract abstract
            abstract_elem = result.select_one(".gs_rs")
            abstract = abstract_elem.text if abstract_elem else ""
            
            # Check if PDF is available
            pdf_link = None
            for a_tag in result.select(".gs_or_ggsm a"):
                if "[PDF]" in a_tag.text:
                    pdf_link = a_tag["href"]
                    break
            
            papers.append({
                "title": title,
                "authors": authors_venue_text,
                "year": year,
                "abstract": abstract,
                "link": link,
                "pdf_link": pdf_link
            })
        
        except Exception as e:
            print(f"Error extracting paper info: {e}")
    
    return papers

def download_pdf(url, filename):
    """Download a PDF file."""
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        
        # Check if it's actually a PDF
        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" not in content_type and not url.lower().endswith(".pdf"):
            print(f"Warning: URL does not appear to be a PDF: {url}")
            return False
        
        # Save the PDF
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return False

def main():
    """Main function to search for and collect OpenSim papers."""
    print("Starting OpenSim paper collection...")
    
    papers_collected = 0
    
    for query in SEARCH_QUERIES:
        print(f"\nSearching for: {query}")
        
        # Search multiple pages
        for page in range(0, 5):  # 5 pages, 10 results each = 50 max per query
            if papers_collected >= MAX_PAPERS:
                break
            
            start = page * 10
            html = search_scholar(query, start=start)
            
            if not html:
                continue
            
            papers = extract_paper_info(html)
            print(f"Found {len(papers)} papers on page {page+1}")
            
            for paper in papers:
                if papers_collected >= MAX_PAPERS:
                    break
                
                # Create a clean filename from the title
                base_filename = clean_filename(paper["title"])[:100]  # Limit length
                
                # Save paper metadata and abstract
                metadata_filename = f"{base_filename}.txt"
                metadata_path = os.path.join(OUTPUT_DIR, metadata_filename)
                
                with open(metadata_path, "w", encoding="utf-8") as f:
                    f.write(f"Title: {paper['title']}\n")
                    f.write(f"Authors: {paper['authors']}\n")
                    f.write(f"Year: {paper['year']}\n")
                    f.write(f"Link: {paper['link']}\n")
                    f.write(f"PDF Link: {paper['pdf_link']}\n")
                    f.write(f"Query: {query}\n")
                    f.write(f"Date Collected: {time.strftime('%Y-%m-%d')}\n")
                    f.write("\nAbstract:\n")
                    f.write(paper["abstract"])
                
                # Add to metadata
                paper_metadata = {
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "year": paper["year"],
                    "link": paper["link"],
                    "pdf_link": paper["pdf_link"],
                    "query": query,
                    "filename": metadata_filename,
                    "pdf_downloaded": False,
                    "date_collected": time.strftime("%Y-%m-%d")
                }
                
                # Try to download PDF if available
                if paper["pdf_link"]:
                    pdf_filename = f"{base_filename}.pdf"
                    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
                    
                    print(f"Downloading PDF: {paper['title']}")
                    success = download_pdf(paper["pdf_link"], pdf_path)
                    
                    if success:
                        paper_metadata["pdf_downloaded"] = True
                        paper_metadata["pdf_filename"] = pdf_filename
                
                metadata.append(paper_metadata)
                papers_collected += 1
            
            # Delay between pages to avoid being blocked
            time.sleep(DELAY)
    
    # Save metadata
    metadata_file = os.path.join(OUTPUT_DIR, "metadata.json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    # Create a DataFrame for easier analysis
    df = pd.DataFrame(metadata)
    csv_file = os.path.join(OUTPUT_DIR, "metadata.csv")
    df.to_csv(csv_file, index=False)
    
    print(f"\nPaper collection completed. Collected {papers_collected} papers.")
    print(f"Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
