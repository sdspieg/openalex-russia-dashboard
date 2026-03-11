#!/usr/bin/env python3
"""
SIMPLIFIED OpenAlex Search - For Workshop Beginners
This version has minimal code and clear explanations
"""

import requests
import json

# ========================================
# STEP 1: Configure your email
# ========================================
YOUR_EMAIL = "your.email@fletcher.edu"  # <- CHANGE THIS!

# ========================================
# STEP 2: Define what to search for
# ========================================
SEARCH_TERMS = '"Russian foreign policy" OR "Russian defense policy" OR "Russian security policy"'

# ========================================
# STEP 3: Run the search
# ========================================
def search_openalex():
    """Simple function to search OpenAlex"""

    print("Searching OpenAlex for:", SEARCH_TERMS)
    print("-" * 50)

    # Build the API URL
    url = "https://api.openalex.org/works"

    # Set up the search parameters
    params = {
        "search": SEARCH_TERMS,
        "per_page": 25,  # Just get 25 papers for this demo
        "mailto": YOUR_EMAIL
    }

    # Make the request
    response = requests.get(url, params=params)

    # Check if it worked
    if response.status_code != 200:
        print("Error: Could not connect to OpenAlex")
        return

    # Get the results
    data = response.json()
    papers = data["results"]

    print(f"Found {len(papers)} papers!")
    print("-" * 50)

    # Show what we found
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "No title")
        year = paper.get("publication_year", "Unknown")
        citations = paper.get("cited_by_count", 0)

        print(f"\n{i}. {title}")
        print(f"   Year: {year} | Citations: {citations}")

    # Save to file
    with open("my_search_results.json", "w") as f:
        json.dump(papers, f, indent=2)

    print("\n" + "=" * 50)
    print("Results saved to: my_search_results.json")
    print("=" * 50)

# ========================================
# STEP 4: Run the program
# ========================================
if __name__ == "__main__":
    # Check if email was updated
    if YOUR_EMAIL == "your.email@fletcher.edu":
        print("⚠️  Please update YOUR_EMAIL on line 12 first!")
    else:
        search_openalex()