#!/usr/bin/env python3
"""
Merge the title/abstract search results with fulltext-only results
Create a unified dataset with source indicators
"""

import json
import os

def merge_datasets():
    print("Loading datasets...")

    # Load title/abstract search results
    with open("../results/russian_policy_dataset/russian_policy_works.json", "r", encoding="utf-8") as f:
        tak_papers = json.load(f)

    # Load fulltext-only results
    with open("../results/fulltext_only_results/fulltext_only_papers.json", "r", encoding="utf-8") as f:
        fulltext_papers = json.load(f)

    print(f"Title/Abstract search: {len(tak_papers)} papers")
    print(f"Fulltext-only search: {len(fulltext_papers)} papers")

    # Create merged dataset with source indicators
    merged = {}

    # Add TAK papers
    for paper in tak_papers:
        paper_id = paper.get("id")
        paper["search_source"] = "title_abstract"
        paper["in_title_abstract"] = True
        paper["in_fulltext_only"] = False
        merged[paper_id] = paper

    # Add fulltext-only papers
    for paper in fulltext_papers:
        paper_id = paper.get("id")
        if paper_id not in merged:
            paper["search_source"] = "fulltext_only"
            paper["in_title_abstract"] = False
            paper["in_fulltext_only"] = True
            merged[paper_id] = paper
        else:
            # This shouldn't happen based on our search, but just in case
            merged[paper_id]["search_source"] = "both"
            merged[paper_id]["in_fulltext_only"] = True

    # Convert to list
    merged_list = list(merged.values())

    print(f"\nTotal unique papers: {len(merged_list)}")

    # Save merged dataset
    output_dir = "../results/merged_dataset"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "all_papers_merged.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved merged dataset to {output_file}")

    # Create analysis summary
    analyze_merged(merged_list)

    return merged_list

def analyze_merged(papers):
    """Analyze the merged dataset"""

    # Count by source
    tak_count = sum(1 for p in papers if p["search_source"] == "title_abstract")
    ft_count = sum(1 for p in papers if p["search_source"] == "fulltext_only")
    both_count = sum(1 for p in papers if p["search_source"] == "both")

    # Year analysis
    years_tak = {}
    years_ft = {}

    for paper in papers:
        year = paper.get("publication_year")
        if year:
            if paper["search_source"] == "title_abstract":
                years_tak[year] = years_tak.get(year, 0) + 1
            elif paper["search_source"] == "fulltext_only":
                years_ft[year] = years_ft.get(year, 0) + 1

    # Open Access analysis
    oa_tak = sum(1 for p in papers if p["search_source"] == "title_abstract" and p.get("open_access", {}).get("is_oa"))
    oa_ft = sum(1 for p in papers if p["search_source"] == "fulltext_only" and p.get("open_access", {}).get("is_oa"))

    # Citations analysis
    citations_tak = [p.get("cited_by_count", 0) for p in papers if p["search_source"] == "title_abstract"]
    citations_ft = [p.get("cited_by_count", 0) for p in papers if p["search_source"] == "fulltext_only"]

    avg_cite_tak = sum(citations_tak) / len(citations_tak) if citations_tak else 0
    avg_cite_ft = sum(citations_ft) / len(citations_ft) if citations_ft else 0

    # Save analysis
    analysis = {
        "total_papers": len(papers),
        "source_breakdown": {
            "title_abstract": tak_count,
            "fulltext_only": ft_count,
            "both": both_count
        },
        "open_access": {
            "title_abstract": f"{oa_tak}/{tak_count} ({100*oa_tak/tak_count:.1f}%)",
            "fulltext_only": f"{oa_ft}/{ft_count} ({100*oa_ft/ft_count:.1f}%)"
        },
        "citations": {
            "avg_title_abstract": round(avg_cite_tak, 1),
            "avg_fulltext_only": round(avg_cite_ft, 1),
            "total_citations": sum(citations_tak) + sum(citations_ft)
        },
        "temporal_range": {
            "earliest": min(min(years_tak.keys(), default=9999), min(years_ft.keys(), default=9999)),
            "latest": max(max(years_tak.keys(), default=0), max(years_ft.keys(), default=0))
        }
    }

    with open("../results/merged_dataset/analysis_summary.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print("\n" + "="*60)
    print("MERGED DATASET ANALYSIS")
    print("="*60)
    print(f"Total papers: {len(papers)}")
    print(f"  - From title/abstract: {tak_count} ({100*tak_count/len(papers):.1f}%)")
    print(f"  - From fulltext-only: {ft_count} ({100*ft_count/len(papers):.1f}%)")
    print(f"\nAverage citations:")
    print(f"  - Title/abstract papers: {avg_cite_tak:.1f}")
    print(f"  - Fulltext-only papers: {avg_cite_ft:.1f}")
    print(f"\nInsight: Papers with terms in title/abstract are cited {avg_cite_tak/avg_cite_ft:.1f}x more!")

if __name__ == "__main__":
    merge_datasets()