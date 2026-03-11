#!/usr/bin/env python3
"""
Export OpenAlex results to CSV for Excel/spreadsheet analysis
"""

import json
import csv
import os

def export_to_csv():
    # Load the JSON data
    json_path = "../results/russian_policy_dataset/russian_policy_works.json"
    csv_path = "../results/russian_policy_dataset/russian_policy_papers.csv"

    print("Loading JSON data...")
    with open(json_path, "r", encoding="utf-8") as f:
        works = json.load(f)

    print(f"Exporting {len(works)} papers to CSV...")

    # Create CSV with selected fields
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header row
        writer.writerow([
            "Title",
            "Year",
            "Authors",
            "Journal/Source",
            "Citations",
            "Open Access",
            "DOI",
            "Topics",
            "Countries",
            "Abstract Length"
        ])

        # Data rows
        for w in works:
            # Extract authors
            authors = []
            for authorship in w.get("authorships", []):
                author = authorship.get("author", {})
                if author.get("display_name"):
                    authors.append(author["display_name"])
            authors_str = "; ".join(authors[:5])  # First 5 authors
            if len(authors) > 5:
                authors_str += f" ... (+{len(authors)-5} more)"

            # Extract source
            source = ""
            location = w.get("primary_location") or {}
            if location.get("source"):
                source = location["source"].get("display_name", "")

            # Extract topics
            topics = []
            for topic in (w.get("topics") or [])[:3]:  # Top 3 topics
                topics.append(topic.get("display_name", ""))
            topics_str = "; ".join(topics)

            # Extract countries from institutions
            countries = set()
            for authorship in w.get("authorships", []):
                for inst in (authorship.get("institutions") or []):
                    country = inst.get("country_code", "")
                    if country:
                        countries.add(country)
            countries_str = ", ".join(sorted(countries))

            # Calculate abstract length
            abstract_length = 0
            if w.get("abstract_inverted_index"):
                abstract_length = len(w["abstract_inverted_index"])

            # Write row
            writer.writerow([
                w.get("title", ""),
                w.get("publication_year", ""),
                authors_str,
                source,
                w.get("cited_by_count", 0),
                "Yes" if w.get("open_access", {}).get("is_oa") else "No",
                w.get("doi", ""),
                topics_str,
                countries_str,
                abstract_length
            ])

    print(f"✓ Exported to: {csv_path}")
    print("  You can now open this file in Excel or any spreadsheet software")

if __name__ == "__main__":
    export_to_csv()