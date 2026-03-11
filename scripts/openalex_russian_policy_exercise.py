#!/usr/bin/env python3
"""
OpenAlex Exercise: Russian Foreign/Defense/Security Policy Research
RuBase Workshop - Fletcher School, March 2026

This script demonstrates how to use the OpenAlex API to conduct a systematic
bibliometric search for academic research on Russian policy topics.
"""

import os
import json
import time
import requests
from datetime import datetime

# ----------------- CONFIGURATION -----------------
# IMPORTANT: Replace with your email for polite pool access
MAILTO = "workshop@example.com"  # Using example email for demo

BASE_URL = "https://api.openalex.org"
DATA_DIR = "../results/russian_policy_dataset"
PER_PAGE = 200  # Maximum allowed per page

# Our search query - combining three policy areas
# Using OR operator to get papers mentioning ANY of these terms
SEARCH_QUERY = '"Russian foreign policy" OR "Russian defense policy" OR "Russian security policy"'

def fetch_russian_policy_works():
    """
    Fetch all works matching our Russian policy search criteria.
    Uses cursor-based pagination to handle large result sets.
    """
    print(f"[*] Starting OpenAlex search for Russian policy research")
    print(f"    Search query: {SEARCH_QUERY}")
    print(f"    This may take a few minutes depending on the number of results...")

    works = []
    cursor = "*"  # Start with wildcard cursor
    page_count = 0

    while cursor:
        page_count += 1

        # Build API parameters
        params = {
            "search": SEARCH_QUERY,  # Using search parameter for full-text search
            "per_page": PER_PAGE,
            "cursor": cursor,
            "mailto": MAILTO  # Important for polite pool
        }

        # Make API request
        print(f"    - Fetching page {page_count}...")
        res = requests.get(f"{BASE_URL}/works", params=params)

        if res.status_code != 200:
            print(f"    [ERROR] API returned status {res.status_code}")
            print(f"    Response: {res.text}")
            break

        data = res.json()
        results = data.get("results", [])

        if not results:
            break  # No more results

        works.extend(results)

        # Get next cursor from metadata
        cursor = data.get("meta", {}).get("next_cursor")

        print(f"    - Downloaded {len(works)} works so far...")

        # Be polite to the API
        time.sleep(0.1)  # 100ms delay between requests

    print(f"\n[✓] Successfully downloaded {len(works)} works!")

    # Save the results
    os.makedirs(DATA_DIR, exist_ok=True)
    output_file = os.path.join(DATA_DIR, "russian_policy_works.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(works, f, indent=2, ensure_ascii=False)

    print(f"[✓] Saved to {output_file}")

    return works

def analyze_results(works):
    """
    Perform basic analysis on the retrieved works.
    """
    print("\n" + "="*60)
    print("ANALYSIS OF RUSSIAN POLICY RESEARCH")
    print("="*60)

    # Basic statistics
    print(f"\nTotal papers found: {len(works)}")

    # Year distribution
    years = {}
    for work in works:
        year = work.get("publication_year")
        if year:
            years[year] = years.get(year, 0) + 1

    if years:
        print(f"\nPublication years: {min(years.keys())} - {max(years.keys())}")
        print("\nTop 5 most productive years:")
        for year, count in sorted(years.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {year}: {count} papers")

    # Open Access analysis
    oa_count = sum(1 for w in works if w.get("open_access", {}).get("is_oa", False))
    print(f"\nOpen Access papers: {oa_count}/{len(works)} ({100*oa_count/len(works):.1f}%)")

    # Top journals/sources
    sources = {}
    for work in works:
        location = work.get("primary_location") or {}
        source = location.get("source") or {}
        source_name = source.get("display_name")
        if source_name:
            sources[source_name] = sources.get(source_name, 0) + 1

    if sources:
        print("\nTop 10 publication venues:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {source}: {count} papers")

    # Topic analysis
    topics = {}
    for work in works:
        for topic in (work.get("topics") or []):
            topic_name = topic.get("display_name")
            if topic_name:
                topics[topic_name] = topics.get(topic_name, 0) + 1

    if topics:
        print("\nTop 10 research topics:")
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {topic}: {count} papers")

    # Citation analysis
    citations = [w.get("cited_by_count", 0) for w in works]
    if citations:
        print(f"\nCitation statistics:")
        print(f"  Total citations: {sum(citations):,}")
        print(f"  Average citations per paper: {sum(citations)/len(citations):.1f}")
        print(f"  Most cited paper: {max(citations):,} citations")

    # Export titles and abstracts for further analysis
    export_abstracts(works)

def export_abstracts(works):
    """
    Export titles and abstracts for LLM analysis.
    """
    output_file = os.path.join(DATA_DIR, "titles_and_abstracts.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        for i, work in enumerate(works, 1):
            title = work.get("title", "No title")
            year = work.get("publication_year", "Unknown year")

            # Get abstract from inverted index
            abstract = ""
            inverted_abstract = work.get("abstract_inverted_index")
            if inverted_abstract:
                # Reconstruct abstract from inverted index
                word_positions = []
                for word, positions in inverted_abstract.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join([word for _, word in word_positions])

            f.write(f"="*80 + "\n")
            f.write(f"Paper {i}: {title}\n")
            f.write(f"Year: {year}\n")
            f.write(f"DOI: {work.get('doi', 'No DOI')}\n")
            f.write(f"\nAbstract:\n{abstract if abstract else 'No abstract available'}\n")
            f.write("\n")

    print(f"\n[✓] Exported titles and abstracts to {output_file}")

def main():
    """
    Main execution function.
    """
    print("="*60)
    print("OpenAlex Russian Policy Research Exercise")
    print("RuBase Workshop - Fletcher School")
    print("="*60)

    # Check if email has been configured
    if MAILTO == "your.email@fletcher.edu":
        print("\n[!] WARNING: Please update the MAILTO variable with your email address!")
        print("    This is required for OpenAlex's polite pool access.")
        print("    Edit line 16 of this script and replace with your actual email.")
        return

    # Fetch the data
    works = fetch_russian_policy_works()

    if works:
        # Analyze what we found
        analyze_results(works)

        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Review the downloaded data in the 'russian_policy_dataset' folder")
        print("2. Open 'russian_policy_works.json' to see the full metadata")
        print("3. Use 'titles_and_abstracts.txt' for LLM-based analysis")
        print("4. Consider filtering by year, journal, or open access status")
        print("5. Export to CSV for analysis in Excel or other tools")
    else:
        print("\n[!] No works found. Check your search query and internet connection.")

if __name__ == "__main__":
    main()