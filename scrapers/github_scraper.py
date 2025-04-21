#!/usr/bin/env python3
"""
OpenSim GitHub Repository Scraper

This script scrapes content from OpenSim GitHub repositories,
focusing on documentation files, README files, and other relevant content.
"""

import os
import time
import json
import requests
import base64
import pandas as pd
from urllib.parse import urljoin

# Configuration
OUTPUT_DIR = "../data/github_docs"
DELAY = 1  # Delay between requests in seconds

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# GitHub API endpoints
GITHUB_API = "https://api.github.com"
REPOS = [
    "opensim-org/opensim-core",
    "opensim-org/opensim-gui",
    "opensim-org/opensim-moco",
    "opensim-org/SCONE"
]

# Headers for GitHub API
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "OpenSim-RAG-Project"
}

# File extensions and names to focus on
DOC_EXTENSIONS = ['.md', '.txt', '.rst', '.ipynb']
DOC_FILENAMES = ['readme', 'contributing', 'documentation', 'guide', 'tutorial', 'example', 'howto', 'faq']

# Store metadata about scraped files
metadata = []

def is_documentation_file(filename):
    """Check if a file is likely to be documentation."""
    filename_lower = filename.lower()
    
    # Check extensions
    if any(filename_lower.endswith(ext) for ext in DOC_EXTENSIONS):
        return True
    
    # Check filenames
    if any(doc_name in filename_lower for doc_name in DOC_FILENAMES):
        return True
    
    return False

def get_repo_contents(repo, path=""):
    """Get contents of a repository at a specific path."""
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {url}: {response.status_code}")
        return []

def get_file_content(repo, path):
    """Get content of a specific file in a repository."""
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        content_data = response.json()
        if content_data.get("encoding") == "base64" and content_data.get("content"):
            return base64.b64decode(content_data["content"]).decode('utf-8')
    
    return None

def process_repo_contents(repo, path="", depth=0, max_depth=5):
    """Process contents of a repository recursively."""
    if depth > max_depth:
        return
    
    contents = get_repo_contents(repo, path)
    
    if not isinstance(contents, list):
        # Handle case where contents is not a list (e.g., it's a file)
        return
    
    for item in contents:
        if item["type"] == "dir":
            # Process directory recursively
            process_repo_contents(repo, item["path"], depth + 1, max_depth)
        elif item["type"] == "file" and is_documentation_file(item["name"]):
            # Process documentation file
            print(f"Processing file: {item['path']}")
            content = get_file_content(repo, item["path"])
            
            if content:
                # Create filename
                filename = f"{repo.replace('/', '_')}_{item['path'].replace('/', '_')}"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                # Save content to file
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Repository: {repo}\n")
                    f.write(f"Path: {item['path']}\n")
                    f.write(f"URL: {item['html_url']}\n")
                    f.write(f"Date: {time.strftime('%Y-%m-%d')}\n")
                    f.write("\n")
                    f.write(content)
                
                # Add to metadata
                metadata.append({
                    "repository": repo,
                    "path": item["path"],
                    "url": item["html_url"],
                    "filename": filename,
                    "date_scraped": time.strftime("%Y-%m-%d"),
                    "content_length": len(content)
                })
            
            # Delay to be respectful to the API rate limits
            time.sleep(DELAY)

def get_repo_issues(repo, state="open", per_page=100, max_pages=5):
    """Get issues from a repository."""
    issues = []
    
    for page in range(1, max_pages + 1):
        url = f"{GITHUB_API}/repos/{repo}/issues"
        params = {
            "state": state,
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            page_issues = response.json()
            if not page_issues:
                break
            
            issues.extend(page_issues)
            time.sleep(DELAY)
        else:
            print(f"Error fetching issues for {repo}: {response.status_code}")
            break
    
    return issues

def process_repo_issues(repo):
    """Process issues from a repository."""
    print(f"Processing issues for {repo}")
    
    issues = get_repo_issues(repo)
    
    for issue in issues:
        # Create filename
        issue_number = issue["number"]
        filename = f"{repo.replace('/', '_')}_issue_{issue_number}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Extract content
        title = issue["title"]
        body = issue["body"] or ""
        url = issue["html_url"]
        created_at = issue["created_at"]
        
        # Save content to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Repository: {repo}\n")
            f.write(f"Issue: #{issue_number}\n")
            f.write(f"Title: {title}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Created: {created_at}\n")
            f.write(f"Date Scraped: {time.strftime('%Y-%m-%d')}\n")
            f.write("\n")
            f.write(body)
        
        # Add to metadata
        metadata.append({
            "repository": repo,
            "type": "issue",
            "number": issue_number,
            "title": title,
            "url": url,
            "created_at": created_at,
            "filename": filename,
            "date_scraped": time.strftime("%Y-%m-%d"),
            "content_length": len(body)
        })

def main():
    """Main function to scrape OpenSim GitHub repositories."""
    print("Starting OpenSim GitHub repository scraper...")
    
    for repo in REPOS:
        print(f"\nProcessing repository: {repo}")
        
        # Process repository contents
        process_repo_contents(repo)
        
        # Process repository issues
        process_repo_issues(repo)
    
    # Save metadata
    metadata_file = os.path.join(OUTPUT_DIR, "metadata.json")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    # Create a DataFrame for easier analysis
    df = pd.DataFrame(metadata)
    csv_file = os.path.join(OUTPUT_DIR, "metadata.csv")
    df.to_csv(csv_file, index=False)
    
    print(f"\nScraping completed. Scraped {len(metadata)} files.")
    print(f"Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
