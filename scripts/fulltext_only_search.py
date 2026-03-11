#!/usr/bin/env python3
"""
Search for papers with terms in FULLTEXT but NOT in Title/Abstract/Keywords
This finds papers we might have missed with regular search
"""

import os
import json
import time
import requests

# Configuration
MAILTO = "workshop@example.com"
BASE_URL = "https://api.openalex.org"
PER_PAGE = 200

# Our search terms
SEARCH_TERMS = [
    "Russian foreign policy",
    "Russian defense policy",
    "Russian security policy"
]

def search_fulltext_not_tak(search_term):
    """
    Search for papers with term in fulltext but NOT in title/abstract
    Using OpenAlex's filter syntax
    """
    print(f"\n[*] Searching for '{search_term}' in fulltext ONLY (not in title/abstract)...")

    works = []
    cursor = "*"
    page_count = 0

    # Build the filter: has term in fulltext but NOT in regular search
    # This is a bit complex - we need papers where fulltext.search matches
    # but the regular search doesn't match
    filter_query = f'fulltext.search:"{search_term}"'

    while cursor:
        page_count += 1

        params = {
            "filter": filter_query,
            "per_page": PER_PAGE,
            "cursor": cursor,
            "mailto": MAILTO
        }

        print(f"    - Fetching page {page_count}...")
        res = requests.get(f"{BASE_URL}/works", params=params)

        if res.status_code != 200:
            print(f"    [ERROR] API returned status {res.status_code}")
            break

        data = res.json()
        results = data.get("results", [])

        if not results:
            break

        # Filter out papers that have the term in title or abstract
        for paper in results:
            title = (paper.get("title") or "").lower()

            # Get abstract text
            abstract = ""
            inverted_abstract = paper.get("abstract_inverted_index")
            if inverted_abstract:
                word_positions = []
                for word, positions in inverted_abstract.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join([word for _, word in word_positions]).lower()

            # Check if term appears in title or abstract
            search_term_lower = search_term.lower()
            if search_term_lower not in title and search_term_lower not in abstract:
                # This paper has the term in fulltext but NOT in title/abstract!
                works.append(paper)

        cursor = data.get("meta", {}).get("next_cursor")

        print(f"    - Found {len(works)} fulltext-only papers so far...")
        time.sleep(0.1)

    return works

def main():
    print("="*60)
    print("OpenAlex Fulltext-Only Search")
    print("Finding papers missed by title/abstract search")
    print("="*60)

    all_fulltext_only = []

    for term in SEARCH_TERMS:
        results = search_fulltext_not_tak(term)
        print(f"✓ Found {len(results)} papers with '{term}' in fulltext only")
        all_fulltext_only.extend(results)

    # Remove duplicates (papers might match multiple terms)
    unique_papers = {}
    for paper in all_fulltext_only:
        paper_id = paper.get("id")
        if paper_id not in unique_papers:
            unique_papers[paper_id] = paper

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Total unique papers found in fulltext-only: {len(unique_papers)}")

    # Save results
    output_dir = "../results/fulltext_only_results"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "fulltext_only_papers.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(list(unique_papers.values()), f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(unique_papers)} fulltext-only papers to {output_file}")

    # Show some examples
    if unique_papers:
        print("\n" + "="*60)
        print("EXAMPLE PAPERS (fulltext mention only)")
        print("="*60)

        for i, paper in enumerate(list(unique_papers.values())[:5], 1):
            print(f"\n{i}. {paper.get('title', 'No title')}")
            print(f"   Year: {paper.get('publication_year', 'Unknown')}")
            print(f"   DOI: {paper.get('doi', 'No DOI')}")

    # Analysis
    print("\n" + "="*60)
    print("WHAT THIS MEANS")
    print("="*60)
    print(f"Original search found: 6,329 papers (mostly from title/abstract matches)")
    print(f"Fulltext-only search found: {len(unique_papers)} additional papers")

    if len(unique_papers) > 0:
        pct_missed = (len(unique_papers) / 6329) * 100
        print(f"We potentially missed ~{pct_missed:.1f}% of relevant papers")
        print("\nThese papers mention Russian policy in the body text but not in title/abstract")
        print("They might be:")
        print("- Comparative studies mentioning Russia as one of many cases")
        print("- Papers with broader titles that discuss Russia in detail")
        print("- Historical papers where Russia is discussed but not the main focus")

if __name__ == "__main__":
    main()