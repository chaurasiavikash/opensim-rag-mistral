#!/usr/bin/env python3
"""
OpenSim Scraper Runner

This script runs all the scrapers to collect OpenSim documentation
from various sources and organizes the collected data.
"""

import os
import sys
import time
import json
import subprocess
import pandas as pd
from datetime import datetime

# Configuration
DATA_DIR = "../data"
LOG_DIR = "../logs"
SCRAPERS_DIR = "scrapers"

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# List of scrapers to run
SCRAPERS = [
    {"name": "confluence_scraper", "script": "confluence_scraper.py", "enabled": True},
    {"name": "github_scraper", "script": "github_scraper.py", "enabled": True},
    {"name": "api_docs_scraper", "script": "api_docs_scraper.py", "enabled": True},
    {"name": "scholar_scraper", "script": "scholar_scraper.py", "enabled": True}
]

def run_scraper(scraper):
    """Run a scraper script and log the output."""
    name = scraper["name"]
    script = scraper["script"]
    
    print(f"\n{'='*80}")
    print(f"Running {name} ({script})...")
    print(f"{'='*80}")
    
    # Create log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"{name}_{timestamp}.log")
    
    # Command to run
    cmd = [sys.executable, os.path.join(SCRAPERS_DIR, script)]
    
    try:
        # Run the scraper and capture output
        with open(log_file, "w") as f:
            f.write(f"Running {name} ({script}) at {timestamp}\n\n")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream and log output
            for line in process.stdout:
                print(line, end="")
                f.write(line)
            
            process.wait()
            
            if process.returncode == 0:
                status = "SUCCESS"
            else:
                status = f"FAILED (code {process.returncode})"
            
            end_message = f"\n\n{name} completed with status: {status}"
            print(end_message)
            f.write(end_message)
        
        return process.returncode == 0
    
    except Exception as e:
        error_message = f"Error running {name}: {e}"
        print(error_message)
        
        with open(log_file, "a") as f:
            f.write(f"\n\n{error_message}")
        
        return False

def collect_metadata():
    """Collect and combine metadata from all scrapers."""
    print("\nCollecting metadata from all sources...")
    
    combined_metadata = []
    
    # Directories to check for metadata
    metadata_dirs = [
        os.path.join(DATA_DIR, "confluence_docs"),
        os.path.join(DATA_DIR, "github_docs"),
        os.path.join(DATA_DIR, "api_docs"),
        os.path.join(DATA_DIR, "papers")
    ]
    
    for directory in metadata_dirs:
        metadata_file = os.path.join(directory, "metadata.json")
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                
                # Add source information
                source = os.path.basename(directory)
                for item in metadata:
                    item["source"] = source
                
                combined_metadata.extend(metadata)
                print(f"Added {len(metadata)} items from {source}")
            
            except Exception as e:
                print(f"Error reading metadata from {metadata_file}: {e}")
    
    # Save combined metadata
    combined_file = os.path.join(DATA_DIR, "combined_metadata.json")
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(combined_metadata, f, indent=2)
    
    # Create a DataFrame for easier analysis
    df = pd.DataFrame(combined_metadata)
    csv_file = os.path.join(DATA_DIR, "combined_metadata.csv")
    df.to_csv(csv_file, index=False)
    
    print(f"Combined metadata saved with {len(combined_metadata)} items")
    return combined_metadata

def main():
    """Main function to run all scrapers."""
    start_time = time.time()
    print(f"Starting OpenSim scraper runner at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run each enabled scraper
    for scraper in SCRAPERS:
        if scraper["enabled"]:
            success = run_scraper(scraper)
            results.append({
                "name": scraper["name"],
                "success": success
            })
        else:
            print(f"Skipping disabled scraper: {scraper['name']}")
    
    # Collect and combine metadata
    metadata = collect_metadata()
    
    # Print summary
    print("\n" + "="*80)
    print("SCRAPING SUMMARY")
    print("="*80)
    
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        print(f"{result['name']}: {status}")
    
    print(f"\nTotal documents collected: {len(metadata)}")
    print(f"Total time: {(time.time() - start_time) / 60:.2f} minutes")
    print("\nScraping completed!")

if __name__ == "__main__":
    main()
