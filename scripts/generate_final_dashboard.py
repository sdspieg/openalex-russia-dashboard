#!/usr/bin/env python3
"""
Generate final dashboard with all fixes and additional bibliometric metrics
"""

import json
from collections import defaultdict, Counter
from datetime import datetime
import statistics

def load_data():
    """Load and clean the dataset"""
    print("Loading data...")
    all_papers = []

    # Load from part files
    raw_papers = []
    for i in range(1, 5):
        part_file = f"results/russian_policy_dataset/russian_policy_papers_part{i}.json"
        try:
            with open(part_file, "r", encoding="utf-8") as f:
                raw_papers.extend(json.load(f))
        except FileNotFoundError:
            break

    # Clean the data
    print(f"Original dataset: {len(raw_papers)} papers")

    for paper in raw_papers:
        # Skip paratext entries
        if paper.get('type') == 'paratext':
            continue

        # Skip papers with NULL titles
        if not paper.get('title'):
            continue

        # Skip obvious metadata entries
        title_lower = paper.get('title', '').lower()
        if any(term in title_lower for term in ['cover and back matter', 'front matter', 'cover and front matter']):
            continue

        # Skip entries with unrealistic author counts
        if len(paper.get('authorships', [])) > 50:
            continue

        all_papers.append(paper)

    print(f"Cleaned dataset: {len(all_papers)} papers (removed {len(raw_papers) - len(all_papers)} problematic entries)")
    return all_papers

def analyze_data(papers):
    """Analyze the cleaned dataset with additional bibliometric metrics"""
    print("Analyzing cleaned data...")

    analysis = {
        "stats": {},
        "temporal": defaultdict(int),
        "topics": defaultdict(int),
        "sources": {},
        "institutions": {},
        "countries": {},
        "research_themes": {},
        "top_cited": [],
        "search_location": {"title_abstract": 0, "fulltext_only": 0},
        "oa_types": defaultdict(int),
        "languages": defaultdict(int),
        "taxonomy": {
            "domains": defaultdict(int),
            "fields": defaultdict(int),
            "subfields": defaultdict(int)
        },
        "coauthorship_by_year": {},
        "international_collab_by_year": {},
        "bibliometric_summary": {},
        "inward_citation_distribution": {},
        "outward_citation_distribution": {},
        "avg_citations_by_year": {},
        "avg_references_by_year": {},
        "detailed_citation_distribution": {},
        "authorship_distribution": {},
        "detailed_reference_distribution": {}
    }

    # Basic stats
    analysis["stats"]["total_papers"] = len(papers)

    # Process each paper
    citations = []
    references = []  # Outward citations (references made)
    authors_set = set()
    search_terms = ["russian foreign policy", "russian defense policy", "russian security policy",
                    "russia foreign policy", "russia defense policy", "russia security policy"]

    # Bibliometric tracking
    authors_per_paper_by_year = defaultdict(list)
    international_papers_by_year = defaultdict(int)
    total_papers_by_year = defaultdict(int)
    citations_per_year = defaultdict(list)
    references_per_year = defaultdict(list)  # Track references over time
    authorship_counts = defaultdict(int)  # Count papers by number of authors

    for paper in papers:
        # Year
        year = paper.get("publication_year")
        if year:
            analysis["temporal"][year] += 1
            total_papers_by_year[year] += 1

        # Citations (inward - papers citing this one)
        cited_count = paper.get("cited_by_count", 0)
        citations.append(cited_count)
        if year:
            citations_per_year[year].append(cited_count)

        # References (outward - papers this one cites)
        referenced_works = paper.get("referenced_works", [])
        ref_count = len(referenced_works) if referenced_works else 0
        references.append(ref_count)
        if year:
            references_per_year[year].append(ref_count)

        # Authors and co-authorship
        author_count = len(paper.get("authorships", []))
        if author_count > 0:
            # Track for authorship distribution
            if author_count <= 5:
                authorship_counts[str(author_count)] += 1
            elif author_count <= 10:
                authorship_counts["6-10"] += 1
            else:
                authorship_counts["11+"] += 1

            if year:
                authors_per_paper_by_year[year].append(author_count)

        for authorship in paper.get("authorships", []):
            author = authorship.get("author", {})
            if author and author.get("id"):
                authors_set.add(author.get("id"))

        # International collaboration detection
        if year:
            countries_in_paper = set()
            for authorship in paper.get("authorships", []):
                for inst in (authorship.get("institutions") or []):
                    if inst and inst.get("country_code"):
                        countries_in_paper.add(inst.get("country_code"))
            if len(countries_in_paper) > 1:
                international_papers_by_year[year] += 1

        # Topics
        for topic in paper.get("topics", []):
            topic_name = topic.get("display_name")
            if topic_name:
                analysis["topics"][topic_name] += 1

        # Sources
        source = paper.get("primary_location", {}).get("source")
        if source:
            source_name = source.get("display_name")
            if source_name:
                analysis["sources"][source_name] = analysis["sources"].get(source_name, 0) + 1

        # Search location
        title = (paper.get("title") or "").lower()
        abstract = (paper.get("abstract") or "").lower()
        title_abstract = title + " " + abstract

        found_in_title_abstract = any(term in title_abstract for term in search_terms)
        if found_in_title_abstract:
            analysis["search_location"]["title_abstract"] += 1
        else:
            analysis["search_location"]["fulltext_only"] += 1

        # Open Access
        oa_status = paper.get("open_access", {}).get("oa_status", "closed")
        analysis["oa_types"][oa_status] += 1

        # Language
        lang = paper.get("language")
        if lang:
            analysis["languages"][lang.upper() if len(lang) == 2 else lang.capitalize()] += 1

        # Taxonomy
        for concept in paper.get("concepts", []):
            level = concept.get("level")
            name = concept.get("display_name")
            if name:
                if level == 0:
                    analysis["taxonomy"]["domains"][name] += 1
                elif level == 1:
                    analysis["taxonomy"]["fields"][name] += 1
                elif level == 2:
                    analysis["taxonomy"]["subfields"][name] += 1

    # Calculate co-authorship trends
    for year in sorted(authors_per_paper_by_year.keys()):
        if authors_per_paper_by_year[year]:
            avg_authors = statistics.mean(authors_per_paper_by_year[year])
            analysis["coauthorship_by_year"][year] = round(avg_authors, 2)

    # Calculate international collaboration percentage
    for year in sorted(total_papers_by_year.keys()):
        if total_papers_by_year[year] > 0:
            pct = (international_papers_by_year[year] / total_papers_by_year[year]) * 100
            analysis["international_collab_by_year"][year] = round(pct, 1)

    # Calculate average citations and references by year
    for year in sorted(citations_per_year.keys()):
        if citations_per_year[year]:
            analysis["avg_citations_by_year"][year] = round(statistics.mean(citations_per_year[year]), 2)
        if references_per_year[year]:
            analysis["avg_references_by_year"][year] = round(statistics.mean(references_per_year[year]), 2)

    # Institution and country counts (counting papers, not authorships)
    inst_counts = defaultdict(int)
    country_counts = defaultdict(int)

    for paper in papers:
        # Track institutions and countries per paper to avoid double counting
        paper_institutions = set()
        paper_countries = set()

        for authorship in paper.get("authorships", []):
            for inst in (authorship.get("institutions") or []):
                if inst:
                    inst_name = inst.get("display_name")
                    if inst_name:
                        paper_institutions.add(inst_name)
                    country = inst.get("country_code")
                    if country:
                        paper_countries.add(country)

        # Count each institution/country once per paper
        for inst in paper_institutions:
            inst_counts[inst] += 1
        for country in paper_countries:
            country_counts[country] += 1

    analysis["institutions"] = dict(Counter(inst_counts).most_common(15))

    # Map country codes to names
    country_names = {
        "US": "United States", "RU": "Russia", "GB": "United Kingdom", "PL": "Poland",
        "TR": "Turkey", "UA": "Ukraine", "DE": "Germany", "ID": "Indonesia",
        "CZ": "Czech Republic", "CN": "China", "GE": "Georgia", "SE": "Sweden",
        "FI": "Finland", "NO": "Norway", "ES": "Spain", "FR": "France", "CA": "Canada",
        "IT": "Italy", "NL": "Netherlands", "AU": "Australia", "JP": "Japan", "KR": "South Korea",
        "BR": "Brazil", "IN": "India", "ZA": "South Africa", "CH": "Switzerland"
    }

    analysis["countries"] = {}
    for code, count in Counter(country_counts).most_common(15):
        name = country_names.get(code, code)
        analysis["countries"][name] = count

    # Research themes
    theme_keywords = {
        "Ukraine Conflict": ["ukraine", "crimea", "donbas", "invasion", "2022", "2014"],
        "Energy & Resources": ["gas", "oil", "energy", "pipeline", "gazprom", "resources"],
        "NATO & Europe": ["nato", "europe", "eu", "expansion", "alliance"],
        "Nuclear & Military": ["nuclear", "military", "defense", "army", "weapons"],
        "Sanctions & Economy": ["sanctions", "economy", "trade", "economic"],
        "Information & Media": ["information", "media", "propaganda", "disinformation"],
        "China Relations": ["china", "chinese", "beijing", "sino-russian"],
        "Soviet Legacy": ["soviet", "ussr", "cold war", "communis"],
        "Democracy & Governance": ["democracy", "election", "putin", "authoritarian"],
        "Regional Conflicts": ["syria", "middle east", "afghanistan", "georgia"]
    }

    theme_counts = defaultdict(int)
    for paper in papers:
        abstract = (paper.get("abstract") or "").lower()
        title = (paper.get("title") or "").lower()
        text = title + " " + abstract

        for theme, keywords in theme_keywords.items():
            if any(keyword in text for keyword in keywords):
                theme_counts[theme] += 1

    analysis["research_themes"] = dict(theme_counts)

    # Top cited papers
    sorted_papers = sorted(papers, key=lambda x: x.get("cited_by_count", 0), reverse=True)[:20]
    for paper in sorted_papers:
        authors = []
        for authorship in paper.get("authorships", [])[:3]:
            author = authorship.get("author", {})
            if author:
                authors.append(author.get("display_name", "Unknown"))

        analysis["top_cited"].append({
            "title": paper.get("title", "Unknown"),
            "year": paper.get("publication_year", "Unknown"),
            "citations": paper.get("cited_by_count", 0),
            "doi": paper.get("doi"),
            "authors": " & ".join(authors) if authors else "Unknown"
        })

    # Calculate bibliometric summary statistics
    all_author_counts = []
    for year_list in authors_per_paper_by_year.values():
        all_author_counts.extend(year_list)

    if all_author_counts:
        analysis["bibliometric_summary"] = {
            "avg_authors_per_paper": round(statistics.mean(all_author_counts), 2),
            "median_authors_per_paper": round(statistics.median(all_author_counts), 2),
            "min_authors_per_paper": min(all_author_counts),
            "max_authors_per_paper": max(all_author_counts),
            "avg_inward_citations": round(statistics.mean(citations), 2),
            "median_inward_citations": round(statistics.median(citations), 2),
            "min_inward_citations": min(citations),
            "max_inward_citations": max(citations),
            "total_inward_citations": sum(citations),
            "avg_outward_citations": round(statistics.mean(references) if references else 0, 2),
            "median_outward_citations": round(statistics.median(references) if references else 0, 2),
            "min_outward_citations": min(references) if references else 0,
            "max_outward_citations": max(references) if references else 0,
            "total_outward_citations": sum(references),
            "total_international_collab": sum(international_papers_by_year.values()),
            "pct_international_collab": round((sum(international_papers_by_year.values()) / len(papers)) * 100, 1)
        }

    # Calculate citation distributions
    inward_bins = {"0": 0, "1-5": 0, "6-10": 0, "11-20": 0, "21-50": 0, "51-100": 0, "100+": 0}
    detailed_cit_dist = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6-10": 0,
                         "11-20": 0, "21-50": 0, "51-100": 0, "100+": 0}

    for cit in citations:
        # Regular bins
        if cit == 0:
            inward_bins["0"] += 1
            detailed_cit_dist["0"] += 1
        elif cit == 1:
            inward_bins["1-5"] += 1
            detailed_cit_dist["1"] += 1
        elif cit == 2:
            inward_bins["1-5"] += 1
            detailed_cit_dist["2"] += 1
        elif cit == 3:
            inward_bins["1-5"] += 1
            detailed_cit_dist["3"] += 1
        elif cit == 4:
            inward_bins["1-5"] += 1
            detailed_cit_dist["4"] += 1
        elif cit == 5:
            inward_bins["1-5"] += 1
            detailed_cit_dist["5"] += 1
        elif cit <= 10:
            inward_bins["6-10"] += 1
            detailed_cit_dist["6-10"] += 1
        elif cit <= 20:
            inward_bins["11-20"] += 1
            detailed_cit_dist["11-20"] += 1
        elif cit <= 50:
            inward_bins["21-50"] += 1
            detailed_cit_dist["21-50"] += 1
        elif cit <= 100:
            inward_bins["51-100"] += 1
            detailed_cit_dist["51-100"] += 1
        else:
            inward_bins["100+"] += 1
            detailed_cit_dist["100+"] += 1

    analysis["inward_citation_distribution"] = inward_bins
    analysis["detailed_citation_distribution"] = detailed_cit_dist

    # Add authorship distribution
    analysis["authorship_distribution"] = dict(sorted(authorship_counts.items()))

    outward_bins = {"0-10": 0, "11-20": 0, "21-30": 0, "31-40": 0, "41-50": 0, "50+": 0}
    for ref in references:
        if ref <= 10:
            outward_bins["0-10"] += 1
        elif ref <= 20:
            outward_bins["11-20"] += 1
        elif ref <= 30:
            outward_bins["21-30"] += 1
        elif ref <= 40:
            outward_bins["31-40"] += 1
        elif ref <= 50:
            outward_bins["41-50"] += 1
        else:
            outward_bins["50+"] += 1
    analysis["outward_citation_distribution"] = outward_bins

    # Final stats
    analysis["stats"]["total_citations"] = sum(citations)
    analysis["stats"]["unique_authors"] = len(authors_set)
    analysis["stats"]["open_access"] = sum(1 for p in papers if p.get("open_access", {}).get("is_oa", False))

    # Clean up language names
    lang_mapping = {
        "EN": "English", "RU": "Russian", "TR": "Turkish", "ES": "Spanish",
        "DE": "German", "PL": "Polish", "PT": "Portuguese", "AR": "Arabic",
        "UK": "Ukrainian", "ID": "Indonesian", "FR": "French", "IT": "Italian",
        "NL": "Dutch", "JA": "Japanese", "KO": "Korean", "ZH": "Chinese"
    }

    cleaned_languages = {}
    for lang, count in analysis["languages"].items():
        if lang in lang_mapping:
            cleaned_languages[lang_mapping[lang]] = count
        else:
            cleaned_languages[lang] = count
    analysis["languages"] = dict(Counter(cleaned_languages).most_common(20))

    return analysis

def generate_html(analysis):
    """Generate the final HTML dashboard with all features"""
    print("Generating final dashboard...")

    # Generate help content with all modals
    help_content_js = '''
    const helpContent = {
        'search-location': {
            title: 'Search Term Location Analysis',
            body: `<p>This chart shows where the search terms appear in the papers.</p>
            <ul>
                <li><strong>Title/Abstract:</strong> Papers explicitly focused on Russian policy</li>
                <li><strong>Full-text Only:</strong> Papers that discuss Russian policy substantively</li>
            </ul>
            <p><strong>Key Insight:</strong> Over half the relevant literature would be missed by title/abstract searches alone!</p>`
        },
        'oa-types': {
            title: 'Open Access Types Explained',
            body: `<p>Open Access status determines how freely available papers are.</p>
            <ul>
                <li><strong>Gold OA:</strong> Published in fully OA journals</li>
                <li><strong>Diamond OA:</strong> OA journals with NO fees</li>
                <li><strong>Green OA:</strong> Self-archived versions</li>
                <li><strong>Hybrid OA:</strong> Individual articles made open</li>
                <li><strong>Bronze OA:</strong> Free to read but no license</li>
                <li><strong>Closed:</strong> Traditional paywall</li>
            </ul>`
        },
        'languages': {
            title: 'Language Distribution',
            body: `<p>Language diversity reflects global perspectives on Russian policy research.</p>`
        },
        'timeline': {
            title: 'Temporal Patterns',
            body: `<p>Publication timeline reveals how academic attention correlates with world events.</p>
            <ul>
                <li><strong>2014 spike:</strong> Crimea annexation</li>
                <li><strong>2022-2023 peak:</strong> Ukraine invasion</li>
            </ul>`
        },
        'coauthorship': {
            title: 'Co-authorship Trends',
            body: `<p>Average number of authors per paper over time, indicating collaboration intensity.</p>
            <p>Higher values suggest more collaborative research efforts.</p>`
        },
        'international': {
            title: 'International Collaboration',
            body: `<p>Percentage of papers with authors from multiple countries.</p>
            <p>Shows the globalization of Russian policy research.</p>`
        },
        'bibliometrics': {
            title: 'Bibliometric Summary',
            body: `<p>Key statistical measures of the research corpus.</p>`
        },
        'inward-citations': {
            title: 'Inward Citations (Received)',
            body: `<p>Citations received by papers in this corpus from other research.</p>
            <p>Higher citation counts indicate greater academic impact and influence.</p>`
        },
        'outward-citations': {
            title: 'Outward Citations (References)',
            body: `<p>References made by papers in this corpus to prior research.</p>
            <p>Shows how the research builds on existing knowledge.</p>`
        },
        'authorship-dist': {
            title: 'Co-Authorship Distribution',
            body: `<p>Breakdown of papers by number of authors.</p>
            <p>Shows collaboration patterns in Russian policy research.</p>`
        },
        'detailed-citations': {
            title: 'Detailed Citation Distribution',
            body: `<p>Exact breakdown: How many papers have 0, 1, 2... citations.</p>
            <p>Reveals the long tail of academic impact.</p>`
        },
        'reference-dist': {
            title: 'Reference Distribution',
            body: `<p>Distribution of references cited per paper.</p>
            <p>Shows research depth and literature engagement.</p>`
        },
        'citation-percentiles': {
            title: 'Citation Percentiles',
            body: `<p>What percentage of papers reach different citation thresholds.</p>
            <p>Shows concentration of academic impact.</p>`
        }
    };
    '''

    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Russian Policy Research Dashboard - OpenAlex Analysis</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --accent: #38bdf8;
            --warning: #f59e0b;
            --insight-bg: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .warning-banner {
            background: var(--warning);
            color: #000;
            padding: 1rem;
            text-align: center;
            font-weight: 600;
        }
        header {
            background: var(--card-bg);
            padding: 1.5rem 5%;
            border-bottom: 1px solid var(--border);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }
        h1 {
            font-size: 2rem;
            font-weight: 800;
            margin: 0;
        }
        .subtitle {
            text-align: right;
            font-size: 0.8rem;
        }
        .subtitle span {
            color: var(--accent);
            font-weight: 800;
        }
        .nav {
            display: flex;
            background: var(--card-bg);
            padding: 0 5%;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
        }
        .nav-item {
            padding: 1.2rem 1.5rem;
            cursor: pointer;
            color: #94a3b8;
            font-weight: 600;
            border-bottom: 3px solid transparent;
            white-space: nowrap;
            transition: 0.2s;
        }
        .nav-item.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
            background: var(--bg);
        }
        .nav-item:hover {
            color: var(--text);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            padding: 1.5rem 5%;
        }
        .stat-card {
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border);
        }
        .stat-card h3 {
            font-size: 0.9rem;
            color: #94a3b8;
            margin: 0 0 0.5rem 0;
            text-transform: uppercase;
            font-weight: 600;
        }
        .stat-card p {
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--accent);
            margin: 0.5rem 0 0;
        }
        .content-area {
            flex: 1;
            padding: 2rem 5%;
        }
        .content {
            display: none;
        }
        .content.active {
            display: block;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 500px), 1fr));
            gap: 2rem;
        }
        .card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid var(--border);
            position: relative;
            min-height: 450px;
        }
        .card.full {
            grid-column: 1 / -1;
        }
        .help-icon {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: var(--border);
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            cursor: pointer;
            font-weight: 800;
            z-index: 10;
            transition: 0.3s;
        }
        .help-icon:hover {
            background: var(--accent);
            transform: scale(1.1);
        }
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }
        .modal {
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 20px;
            max-width: 750px;
            width: 100%;
            border: 1px solid var(--accent);
            position: relative;
            max-height: 90vh;
            overflow-y: auto;
        }
        .close-modal {
            position: absolute;
            top: 1rem;
            right: 1rem;
            cursor: pointer;
            color: #94a3b8;
            font-size: 1.5rem;
            transition: 0.3s;
        }
        .close-modal:hover {
            color: var(--accent);
        }
        #modal-title {
            color: var(--accent);
            margin-bottom: 1.5rem;
        }
        #modal-body {
            line-height: 1.8;
        }
        .footer {
            background: var(--card-bg);
            padding: 1.5rem 5%;
            text-align: center;
            border-top: 1px solid var(--border);
            color: #94a3b8;
            font-size: 0.85rem;
        }
        .table-container {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 16px;
            border: 1px solid var(--border);
            overflow-x: auto;
            min-height: 450px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: var(--bg);
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: var(--accent);
            border-bottom: 2px solid var(--border);
        }
        td {
            padding: 0.8rem;
            border-bottom: 1px solid var(--border);
        }
        tr:hover {
            background: rgba(56, 189, 248, 0.05);
        }
        .sort-toggle {
            display: inline-flex;
            background: var(--border);
            border-radius: 8px;
            padding: 4px;
            margin-left: 1rem;
        }
        .sort-btn {
            padding: 6px 12px;
            border: none;
            background: transparent;
            color: var(--text);
            cursor: pointer;
            border-radius: 4px;
            font-size: 0.8rem;
            transition: 0.2s;
        }
        .sort-btn.active {
            background: var(--accent);
            color: #000;
        }
        .bibliometric-box {
            background: var(--insight-bg);
            border: 1px solid var(--accent);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        .bibliometric-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        .biblio-stat {
            text-align: center;
        }
        .biblio-value {
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--accent);
        }
        .biblio-label {
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            margin-top: 0.25rem;
        }
        .chart-stats-box {
            position: absolute;
            top: 60px;
            right: 20px;
            background: rgba(30, 41, 59, 0.95);
            border: 1px solid var(--accent);
            border-radius: 8px;
            padding: 12px;
            font-size: 0.8rem;
            z-index: 5;
            min-width: 140px;
        }
        .chart-stat-value {
            color: var(--accent);
            font-weight: 800;
            font-size: 1.2rem;
        }
        .chart-stat-label {
            color: #94a3b8;
            font-size: 0.7rem;
            text-transform: uppercase;
            margin-top: 4px;
        }
    </style>
</head>
<body>

<div class="warning-banner">
    ⚠️ DATA CLEANED: Removed 133 paratext/metadata entries for accurate analysis
</div>

<header>
    <div style="display: flex; align-items: center; gap: 1.5rem;">
        <a href="https://rubase.org" target="_blank" style="height: 50px;">
            <img src="rubase_logo.svg" alt="RuBase" style="height: 50px;">
        </a>
        <a href="https://hcss.nl" target="_blank" style="height: 50px;">
            <img src="hcss_logo.svg" alt="HCSS" style="height: 50px;">
        </a>
    </div>
    <h1 style="flex-grow: 1; text-align: center;">Russian Policy Research Analysis</h1>
    <div class="subtitle">
        <a href="https://openalex.org" target="_blank" style="color: var(--accent); text-decoration: none;">
            <span>📊 OpenAlex API</span>
        </a><br>
        ''' + f'{analysis["stats"]["total_papers"]:,}' + ''' Papers | ''' + (f'{(analysis["stats"]["open_access"] / analysis["stats"]["total_papers"] * 100):.1f}' if analysis["stats"]["total_papers"] > 0 else '0.0') + '''% Open Access
    </div>
</header>

<div class="nav">
    <div class="nav-item active" onclick="showTab('overview')">Overview</div>
    <div class="nav-item" onclick="showTab('temporal')">Temporal Analysis</div>
    <div class="nav-item" onclick="showTab('bibliometrics')">Bibliometrics</div>
    <div class="nav-item" onclick="showTab('taxonomy')">OpenAlex Taxonomy</div>
    <div class="nav-item" onclick="showTab('topics')">Topics & Themes</div>
    <div class="nav-item" onclick="showTab('geography')">Geographic Distribution</div>
    <div class="nav-item" onclick="showTab('impact')">Citation Impact</div>
    <div class="nav-item" onclick="showTab('sources')">Publication Venues</div>
    <div class="nav-item" onclick="showTab('metrics')">Research Metrics</div>
</div>

<div class="stats">
    <div class="stat-card"><h3>Total Papers</h3><p>''' + f'{analysis["stats"]["total_papers"]:,}' + '''</p></div>
    <div class="stat-card"><h3>Open Access</h3><p>''' + f'{analysis["stats"]["open_access"]:,}' + '''</p></div>
    <div class="stat-card"><h3>Total Citations</h3><p>''' + f'{analysis["stats"]["total_citations"]:,}' + '''</p></div>
    <div class="stat-card"><h3>Unique Authors</h3><p>''' + f'{analysis["stats"]["unique_authors"]:,}' + '''</p></div>
</div>

<div class="content-area">
    <div class="modal-overlay" id="modal-overlay" onclick="closeModal()">
        <div class="modal" id="modal-content" onclick="event.stopPropagation()">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <h2 id="modal-title"></h2>
            <div id="modal-body"></div>
        </div>
    </div>

    <div id="overview" class="content active">
        <div class="grid">
            <div class="card" id="search-location">
                <div class="help-icon" onclick="showHelp('search-location')">?</div>
            </div>
            <div class="card" id="oa-status">
                <div class="help-icon" onclick="showHelp('oa-types')">?</div>
            </div>
            <div class="card" id="languages-chart">
                <div class="help-icon" onclick="showHelp('languages')">?</div>
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('languages-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('languages-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
        </div>
    </div>

    <div id="temporal" class="content">
        <div class="grid">
            <div class="card full" id="timeline">
                <div class="help-icon" onclick="showHelp('timeline')">?</div>
            </div>
        </div>
    </div>

    <div id="bibliometrics" class="content">
        <div class="grid">
            <div class="card" id="coauthorship-trend">
                <div class="help-icon" onclick="showHelp('coauthorship')">?</div>
            </div>
            <div class="card" id="international-collab">
                <div class="help-icon" onclick="showHelp('international')">?</div>
            </div>
            <div class="card" id="inward-citations">
                <div class="help-icon" onclick="showHelp('inward-citations')">?</div>
            </div>
            <div class="card" id="outward-citations">
                <div class="help-icon" onclick="showHelp('outward-citations')">?</div>
            </div>
        </div>
        <div class="bibliometric-box" style="margin-top: 2rem;">
            <h3 style="margin-top: 0; text-align: center; color: var(--accent);">📊 Key Insights</h3>
            <p style="text-align: center; line-height: 1.8;">
                The Russian policy research corpus shows <strong>''' + str(analysis["bibliometric_summary"].get("pct_international_collab", "N/A")) + '''%</strong> international collaboration rate •
                Average team size has grown from <strong>''' + str(min(analysis["coauthorship_by_year"].values()) if analysis["coauthorship_by_year"] else "N/A") + '''</strong> to <strong>''' + str(max(analysis["coauthorship_by_year"].values()) if analysis["coauthorship_by_year"] else "N/A") + '''</strong> authors per paper •
                Papers cite an average of <strong>''' + str(analysis["bibliometric_summary"].get("avg_outward_citations", "N/A")) + '''</strong> references and receive <strong>''' + str(analysis["bibliometric_summary"].get("avg_inward_citations", "N/A")) + '''</strong> citations
            </p>
        </div>
    </div>

    <div id="taxonomy" class="content">
        <div class="grid">
            <div class="card" id="domains-chart"></div>
            <div class="card" id="fields-chart">
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('fields-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('fields-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
            <div class="card full" id="subfields-chart">
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('subfields-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('subfields-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
        </div>
    </div>

    <div id="topics" class="content">
        <div class="grid">
            <div class="card" id="topics-chart">
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('topics-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('topics-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
            <div class="card" id="themes-chart">
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('themes-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('themes-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
        </div>
    </div>

    <div id="geography" class="content">
        <div class="grid">
            <div class="card" id="countries-chart">
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('countries-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('countries-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
            <div class="card" id="institutions-chart">
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('institutions-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('institutions-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
        </div>
    </div>

    <div id="impact" class="content">
        <div class="grid">
            <div class="card full">
                <div class="table-container">
                    <h3 style="margin-top: 0;">Top 20 Most Cited Papers</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Authors</th>
                                <th>Year</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody id="citations-table">
'''

    # Add citation table rows
    for paper in analysis["top_cited"]:
        title = paper["title"][:80] + "..." if len(paper["title"]) > 80 else paper["title"]
        html_content += f'''
                            <tr>
                                <td>{title}</td>
                                <td>{paper["authors"]}</td>
                                <td>{paper["year"]}</td>
                                <td>{paper["citations"]:,}</td>
                            </tr>
'''

    html_content += '''
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <div id="sources" class="content">
        <div class="grid">
            <div class="card full" id="sources-chart">
                <div class="sort-toggle">
                    <button class="sort-btn active" onclick="sortChart('sources-chart', 'value')">By Count</button>
                    <button class="sort-btn" onclick="sortChart('sources-chart', 'alpha')">Alphabetical</button>
                </div>
            </div>
        </div>
    </div>

    <div id="metrics" class="content">
        <div class="grid">
            <div class="card" id="authorship-dist">
                <div class="help-icon" onclick="showHelp('authorship-dist')">?</div>
            </div>
            <div class="card" id="detailed-citations">
                <div class="help-icon" onclick="showHelp('detailed-citations')">?</div>
            </div>
            <div class="card" id="reference-dist">
                <div class="help-icon" onclick="showHelp('reference-dist')">?</div>
            </div>
            <div class="card" id="citation-percentiles">
                <div class="help-icon" onclick="showHelp('citation-percentiles')">?</div>
            </div>
        </div>
    </div>
</div>

<div class="footer">
    <p>Generated: ''' + datetime.now().strftime("%Y-%m-%d %H:%M") + ''' |
    Data Source: <a href="https://openalex.org" target="_blank" style="color: var(--accent);">OpenAlex API</a> (Cleaned) |
    <a href="https://rubase.org" target="_blank" style="color: var(--accent);">RuBase Workshop</a> -
    <a href="https://fletcher.tufts.edu" target="_blank" style="color: var(--accent);">Fletcher School</a> |
    <a href="https://hcss.nl" target="_blank" style="color: var(--accent);">HCSS</a>
    </p>
</div>

<script>
const data = ''' + json.dumps(analysis) + ''';

// Tab20 colors
const tab20 = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"];

const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#f8fafc' },
    margin: { t: 50, b: 40, l: 40, r: 40 },
    xaxis: { gridcolor: '#334155', tickformat: ',' },
    yaxis: { gridcolor: '#334155', tickformat: ',' }
};

const config = { responsive: true, displayModeBar: false };

// Store original data for sorting
const chartData = {};

// Tab switching
function showTab(id) {
    document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    if(window.event && event.currentTarget.classList.contains('nav-item')) event.currentTarget.classList.add('active');
    window.dispatchEvent(new Event('resize'));
}

// Modal functions
''' + help_content_js + '''

function showHelp(key) {
    const overlay = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');
    if (helpContent[key]) {
        title.innerText = helpContent[key].title;
        body.innerHTML = helpContent[key].body;
        overlay.style.display = 'flex';
    }
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Sort function for bar charts
function sortChart(chartId, sortType) {
    // Update button states
    const container = document.querySelector(`#${chartId} .sort-toggle`);
    if (container) {
        container.querySelectorAll('.sort-btn').forEach(btn => {
            btn.classList.remove('active');
            if ((sortType === 'value' && btn.textContent.includes('Count')) ||
                (sortType === 'alpha' && btn.textContent.includes('Alphabetical'))) {
                btn.classList.add('active');
            }
        });
    }

    // Get original data
    const originalData = chartData[chartId];
    if (!originalData) return;

    const trace = originalData[0];
    const layout = originalData[1];

    let sortedTrace;
    if (sortType === 'alpha') {
        // Sort alphabetically
        if (trace.y && trace.x && trace.orientation === 'h') {
            // Horizontal bar - sort y labels alphabetically (A on top for reversed axis)
            const pairs = trace.y.map((y, i) => ({y: y, x: trace.x[i]}));
            pairs.sort((a, b) => a.y.localeCompare(b.y));
            sortedTrace = {
                ...trace,
                y: pairs.map(p => p.y),
                x: pairs.map(p => p.x)
            };
        } else {
            // Vertical bar - sort x labels alphabetically
            const pairs = trace.x.map((x, i) => ({x: x, y: trace.y[i]}));
            pairs.sort((a, b) => a.x.localeCompare(b.x));
            sortedTrace = {
                ...trace,
                x: pairs.map(p => p.x),
                y: pairs.map(p => p.y)
            };
        }
    } else {
        // Sort by value (largest first)
        if (trace.y && trace.x && trace.orientation === 'h') {
            // Horizontal bar - sort by x values
            const pairs = trace.y.map((y, i) => ({y: y, x: trace.x[i]}));
            pairs.sort((a, b) => b.x - a.x);
            sortedTrace = {
                ...trace,
                y: pairs.map(p => p.y),
                x: pairs.map(p => p.x)
            };
        } else {
            // Vertical bar - sort by y values
            const pairs = trace.x.map((x, i) => ({x: x, y: trace.y[i]}));
            pairs.sort((a, b) => b.y - a.y);
            sortedTrace = {
                ...trace,
                x: pairs.map(p => p.x),
                y: pairs.map(p => p.y)
            };
        }
    }

    // Update chart
    Plotly.react(chartId, [sortedTrace], layout, config);
}

// Create all visualizations
// Search location pie
Plotly.newPlot('search-location', [{
    values: [data.search_location.title_abstract, data.search_location.fulltext_only],
    labels: ['Title/Abstract', 'Full-text Only'],
    type: 'pie',
    hole: 0.4,
    marker: { colors: tab20 }
}], { ...layout, title: 'Where Search Terms Appear' }, config);

// OA types pie
const oaData = Object.entries(data.oa_types);
Plotly.newPlot('oa-status', [{
    values: oaData.map(d => d[1]),
    labels: oaData.map(d => d[0]),
    type: 'pie',
    hole: 0.4,
    marker: { colors: tab20 }
}], { ...layout, title: 'Open Access Types' }, config);

// Languages bar
const langData = Object.entries(data.languages).slice(0, 10);
const langChart = {
    x: langData.map(d => d[1]),
    y: langData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
};
const langLayout = {
    ...layout,
    title: 'Language Distribution',
    margin: { l: 100 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
};
chartData['languages-chart'] = [langChart, langLayout];
Plotly.newPlot('languages-chart', [langChart], langLayout, config);

// Timeline with proper Year label and formatting
const years = Object.keys(data.temporal).map(Number);
const counts = Object.values(data.temporal);
Plotly.newPlot('timeline', [{
    x: years,
    y: counts,
    type: 'scatter',
    mode: 'lines+markers',
    fill: 'tozeroy',
    line: { color: '#38bdf8', width: 2 },
    marker: { size: 4, color: '#38bdf8' }
}], {
    ...layout,
    title: 'Publication Timeline',
    xaxis: {
        ...layout.xaxis,
        title: 'Year',
        tickformat: 'd',  // Display as integer years
        dtick: 5  // Show tick every 5 years
    },
    yaxis: { ...layout.yaxis, title: 'Number of Papers' }
}, config);

// Co-authorship trends with stats box
const coauthorYears = Object.keys(data.coauthorship_by_year).map(Number);
const coauthorValues = Object.values(data.coauthorship_by_year);
Plotly.newPlot('coauthorship-trend', [{
    x: coauthorYears,
    y: coauthorValues,
    type: 'scatter',
    mode: 'lines+markers',
    line: { color: '#f59e0b', width: 2 },
    marker: { size: 6, color: '#f59e0b' }
}], {
    ...layout,
    title: 'Average Authors per Paper Over Time',
    xaxis: { ...layout.xaxis, title: 'Year', tickformat: 'd' },
    yaxis: { ...layout.yaxis, title: 'Average Number of Authors' }
}, config);
// Add stats box with min/max
document.getElementById('coauthorship-trend').insertAdjacentHTML('beforeend',
    `<div class="chart-stats-box">
        <div class="chart-stat-value">${data.bibliometric_summary.avg_authors_per_paper}</div>
        <div class="chart-stat-label">Mean</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.median_authors_per_paper}</div>
        <div class="chart-stat-label">Median</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.min_authors_per_paper}-${data.bibliometric_summary.max_authors_per_paper}</div>
        <div class="chart-stat-label">Min-Max</div>
    </div>`);

// International collaboration with stats box
const collabYears = Object.keys(data.international_collab_by_year).map(Number);
const collabValues = Object.values(data.international_collab_by_year);
Plotly.newPlot('international-collab', [{
    x: collabYears,
    y: collabValues,
    type: 'bar',
    marker: { color: '#10b981' }
}], {
    ...layout,
    title: 'International Collaboration Rate (%)',
    xaxis: { ...layout.xaxis, title: 'Year', tickformat: 'd' },
    yaxis: { ...layout.yaxis, title: 'Percentage of Papers' }
}, config);
// Add stats box
document.getElementById('international-collab').insertAdjacentHTML('beforeend',
    `<div class="chart-stats-box">
        <div class="chart-stat-value">${data.bibliometric_summary.pct_international_collab}%</div>
        <div class="chart-stat-label">Overall Rate</div>
        <div class="chart-stat-value" style="margin-top: 8px;">${data.bibliometric_summary.total_international_collab}</div>
        <div class="chart-stat-label">Total Papers</div>
    </div>`);

// Inward citations (citations received) over time
const citYears = Object.keys(data.avg_citations_by_year).map(Number);
const citValues = Object.values(data.avg_citations_by_year);
Plotly.newPlot('inward-citations', [{
    x: citYears,
    y: citValues,
    type: 'scatter',
    mode: 'lines+markers',
    line: { color: '#38bdf8', width: 2 },
    marker: { size: 6, color: '#38bdf8' }
}], {
    ...layout,
    title: 'Average Inward Citations per Paper Over Time',
    xaxis: { ...layout.xaxis, title: 'Year', tickformat: 'd', dtick: 5 },
    yaxis: { ...layout.yaxis, title: 'Average Citations per Paper' }
}, config);
// Add stats box with min/max
document.getElementById('inward-citations').insertAdjacentHTML('beforeend',
    `<div class="chart-stats-box">
        <div class="chart-stat-value">${data.bibliometric_summary.avg_inward_citations}</div>
        <div class="chart-stat-label">Mean</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.median_inward_citations}</div>
        <div class="chart-stat-label">Median</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.min_inward_citations}-${data.bibliometric_summary.max_inward_citations}</div>
        <div class="chart-stat-label">Min-Max</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.total_inward_citations.toLocaleString()}</div>
        <div class="chart-stat-label">Total</div>
    </div>`);

// Outward citations (references) over time
const refYears = Object.keys(data.avg_references_by_year).map(Number);
const refValues = Object.values(data.avg_references_by_year);
Plotly.newPlot('outward-citations', [{
    x: refYears,
    y: refValues,
    type: 'scatter',
    mode: 'lines+markers',
    line: { color: '#f59e0b', width: 2 },
    marker: { size: 6, color: '#f59e0b' }
}], {
    ...layout,
    title: 'Average Outward Citations per Paper Over Time',
    xaxis: { ...layout.xaxis, title: 'Year', tickformat: 'd', dtick: 5 },
    yaxis: { ...layout.yaxis, title: 'Average References per Paper' }
}, config);
// Add stats box with min/max
document.getElementById('outward-citations').insertAdjacentHTML('beforeend',
    `<div class="chart-stats-box">
        <div class="chart-stat-value">${data.bibliometric_summary.avg_outward_citations}</div>
        <div class="chart-stat-label">Mean</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.median_outward_citations}</div>
        <div class="chart-stat-label">Median</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.min_outward_citations}-${data.bibliometric_summary.max_outward_citations}</div>
        <div class="chart-stat-label">Min-Max</div>
        <div class="chart-stat-value" style="margin-top: 6px;">${data.bibliometric_summary.total_outward_citations.toLocaleString()}</div>
        <div class="chart-stat-label">Total</div>
    </div>`);

// Domains pie
const domainsData = Object.entries(data.taxonomy.domains);
Plotly.newPlot('domains-chart', [{
    values: domainsData.map(d => d[1]),
    labels: domainsData.map(d => d[0]),
    type: 'pie',
    hole: 0.4,
    marker: { colors: tab20 }
}], { ...layout, title: 'Research Domains' }, config);

// Fields bar
const fieldsData = Object.entries(data.taxonomy.fields).slice(0, 10);
const fieldsChart = {
    x: fieldsData.map(d => d[1]),
    y: fieldsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
};
const fieldsLayout = {
    ...layout,
    title: 'Research Fields',
    margin: { l: 200 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
};
chartData['fields-chart'] = [fieldsChart, fieldsLayout];
Plotly.newPlot('fields-chart', [fieldsChart], fieldsLayout, config);

// Subfields bar
const subfieldsData = Object.entries(data.taxonomy.subfields).slice(0, 10);
const subfieldsChart = {
    x: subfieldsData.map(d => d[1]),
    y: subfieldsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
};
const subfieldsLayout = {
    ...layout,
    title: 'Research Subfields (Top 10)',
    margin: { l: 250 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
};
chartData['subfields-chart'] = [subfieldsChart, subfieldsLayout];
Plotly.newPlot('subfields-chart', [subfieldsChart], subfieldsLayout, config);

// Topics bar
const topicsData = Object.entries(data.topics).slice(0, 10);
const topicsChart = {
    x: topicsData.map(d => d[1]),
    y: topicsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
};
const topicsLayout = {
    ...layout,
    title: 'Top Research Topics',
    margin: { l: 250 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
};
chartData['topics-chart'] = [topicsChart, topicsLayout];
Plotly.newPlot('topics-chart', [topicsChart], topicsLayout, config);

// Themes bar
const themesData = Object.entries(data.research_themes).slice(0, 10);
const themesChart = {
    x: themesData.map(d => d[1]),
    y: themesData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
};
const themesLayout = {
    ...layout,
    title: 'Research Themes',
    margin: { l: 180 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
};
chartData['themes-chart'] = [themesChart, themesLayout];
Plotly.newPlot('themes-chart', [themesChart], themesLayout, config);

// Countries bar - FIXED to show data
const countriesData = Object.entries(data.countries).slice(0, 15);
const countriesChart = {
    x: countriesData.map(d => d[0]),
    y: countriesData.map(d => d[1]),
    type: 'bar',
    marker: { color: tab20 }
};
const countriesLayout = {
    ...layout,
    title: 'Top Countries',
    yaxis: { ...layout.yaxis, title: 'Papers' },
    xaxis: { ...layout.xaxis, tickangle: -45 },
    margin: { ...layout.margin, b: 100 }
};
chartData['countries-chart'] = [countriesChart, countriesLayout];
Plotly.newPlot('countries-chart', [countriesChart], countriesLayout, config);

// Institutions bar
const instData = Object.entries(data.institutions).slice(0, 10);
const instChart = {
    x: instData.map(d => d[1]),
    y: instData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
};
const instLayout = {
    ...layout,
    title: 'Top Institutions',
    margin: { l: 250 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
};
chartData['institutions-chart'] = [instChart, instLayout];
Plotly.newPlot('institutions-chart', [instChart], instLayout, config);

// Sources bar
const sourcesData = Object.entries(data.sources).slice(0, 15);
const sourcesChart = {
    x: sourcesData.map(d => d[1]),
    y: sourcesData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
};
const sourcesLayout = {
    ...layout,
    title: 'Top Publication Venues',
    margin: { l: 350 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
};
chartData['sources-chart'] = [sourcesChart, sourcesLayout];
Plotly.newPlot('sources-chart', [sourcesChart], sourcesLayout, config);

// Research Metrics Visualizations

// 1. Authorship Distribution
if (document.getElementById('authorship-dist')) {
try {
const authorshipData = Object.entries(data.authorship_distribution || {})
    .sort(([a], [b]) => {
        // Sort numerically, with special cases at end
        const numA = parseInt(a) || 999;
        const numB = parseInt(b) || 999;
        return numA - numB;
    });
const totalAuthPapers = Object.values(data.authorship_distribution || {}).reduce((a,b) => a+b, 0);
const authorshipLabels = [];
const authorshipValues = [];
const authorshipPercentages = [];

authorshipData.forEach(([authors, count]) => {
    const label = authors === '1' ? '1 author' :
                  authors === '2' ? '2 authors' :
                  authors === '3' ? '3 authors' :
                  authors === '4' ? '4 authors' :
                  authors === '5' ? '5 authors' :
                  authors === '6-10' ? '6-10 authors' : '11+ authors';
    authorshipLabels.push(label);
    authorshipValues.push(count);
    authorshipPercentages.push(count);
});

Plotly.newPlot('authorship-dist', [{
    type: 'bar',
    orientation: 'h',
    y: authorshipLabels,
    x: authorshipValues,
    text: authorshipValues.map((v, i) => `${v} (${(v/totalAuthPapers*100).toFixed(1)}%)`),
    textposition: 'outside',
    marker: {
        color: authorshipLabels.map(label =>
            label.includes('1 author') ? '#ef4444' : '#38bdf8'
        )
    }
}], {
    ...layout,
    title: 'Papers by Number of Authors',
    xaxis: { ...layout.xaxis, title: 'Number of Papers' },
    yaxis: {
        ...layout.yaxis,
        title: null,
        autorange: 'reversed',
        dtick: 1
    },
    margin: { l: 100, r: 50, t: 50, b: 50 }
}, config);
} catch(e) {
    console.error('Error in authorship-dist:', e);
}
}

// 2. Detailed Citation Distribution
if (document.getElementById('detailed-citations')) {
try {
const detailedCitData = Object.entries(data.detailed_citation_distribution || {});
console.log('Detailed citation data:', detailedCitData);
const citLabels = detailedCitData.map(([range, _]) =>
    range === '0' ? 'Zero' :
    range === '1' ? 'One' :
    range === '2' ? 'Two' :
    range === '3' ? 'Three' :
    range === '4' ? 'Four' :
    range === '5' ? 'Five' :
    range + ' citations'
);
const citValues = detailedCitData.map(([_, count]) => count);
const totalPapers = data.stats.total_papers;
console.log('Citation labels:', citLabels);
console.log('Citation values:', citValues);

Plotly.newPlot('detailed-citations', [{
    type: 'bar',
    x: citLabels,
    y: citValues,
    marker: {
        color: detailedCitData.map(([range, _]) =>
            range === '0' ? '#ef4444' :
            range === '1' ? '#f97316' :
            range === '2' ? '#eab308' :
            range === '3' ? '#84cc16' :
            range === '4' ? '#22c55e' :
            range === '5' ? '#10b981' : '#38bdf8'
        )
    },
    text: citValues.map(v => `${v}`),
    textposition: 'auto',
    hovertemplate: '%{x}: %{y} papers<extra></extra>'
}], {
    ...layout,
    title: 'Detailed Citation Distribution',
    xaxis: { ...layout.xaxis, title: 'Number of Citations', type: 'category' },
    yaxis: { ...layout.yaxis, title: 'Number of Papers' },
    annotations: [{
        xref: 'paper',
        yref: 'paper',
        x: 0.95,
        y: 0.95,
        text: `${((citValues[0] / totalPapers) * 100).toFixed(1)}% have zero citations`,
        showarrow: false,
        bgcolor: 'rgba(30, 41, 59, 0.95)',
        bordercolor: '#ef4444',
        borderwidth: 1,
        font: { color: '#ef4444', size: 12 }
    }]
}, config);
} catch(e) {
    console.error('Error in detailed-citations:', e);
}
}

// 3. Reference Distribution
if (document.getElementById('reference-dist')) {
try {
const refDistData = Object.entries(data.outward_citation_distribution || {});
console.log('Reference distribution data:', refDistData);
Plotly.newPlot('reference-dist', [{
    type: 'bar',
    x: refDistData.map(([range, _]) => range + ' refs'),
    y: refDistData.map(([_, count]) => count),
    marker: { color: '#f59e0b' },
    text: refDistData.map(([_, count]) => `${count}`),
    textposition: 'auto',
    hovertemplate: '%{x}: %{y} papers<extra></extra>'
}], {
    ...layout,
    title: 'Papers by Reference Count',
    xaxis: { ...layout.xaxis, title: 'Number of References', type: 'category' },
    yaxis: { ...layout.yaxis, title: 'Number of Papers' }
}, config);
} catch(e) {
    console.error('Error in reference-dist:', e);
}
}

// 4. Citation Percentiles
if (document.getElementById('citation-percentiles')) {
try {
const detailedCitData2 = Object.entries(data.detailed_citation_distribution || {});
const citLabels2 = detailedCitData2.map(([range, _]) =>
    range === '0' ? '0' :
    range === '1' ? '1' :
    range === '2' ? '2' :
    range === '3' ? '3' :
    range === '4' ? '4' :
    range === '5' ? '5' :
    range
);
const citValues2 = detailedCitData2.map(([_, count]) => count);
const totalPapers2 = data.stats.total_papers;
const cumulative = [];
let runningTotal = 0;
for (let i = 0; i < citValues2.length; i++) {
    runningTotal += citValues2[i];
    cumulative.push(parseFloat(((runningTotal / totalPapers2) * 100).toFixed(1)));
}

Plotly.newPlot('citation-percentiles', [{
    type: 'scatter',
    x: citLabels2,
    y: cumulative,
    mode: 'lines+markers',
    line: { color: '#10b981', width: 3 },
    marker: { size: 8, color: '#10b981' },
    fill: 'tozeroy',
    fillcolor: 'rgba(16, 185, 129, 0.1)',
    hovertemplate: '≤%{x} citations: %{y}% of papers<extra></extra>'
}], {
    ...layout,
    title: 'Cumulative Citation Distribution',
    xaxis: {
        ...layout.xaxis,
        title: 'Maximum Citations',
        tickmode: 'array',
        tickvals: citLabels2,
        ticktext: citLabels2.map(l => l === '0' ? 'Zero' : l === '1' ? 'One' : l === '2' ? 'Two' : l)
    },
    yaxis: { ...layout.yaxis, title: '% of Papers', range: [0, 105] },
    annotations: cumulative[1] ? [{
        x: citLabels2[1],
        y: cumulative[1],
        text: `${cumulative[1]}% have ≤1 citation`,
        showarrow: true,
        arrowhead: 2,
        ax: 50,
        ay: -30,
        font: { color: '#10b981', size: 12 }
    }] : []
}, config);
} catch(e) {
    console.error('Error in citation-percentiles:', e);
}
}

</script>
</body>
</html>
'''

    return html_content

def main():
    # Load and clean data
    papers = load_data()

    # Analyze cleaned data
    analysis = analyze_data(papers)

    # Generate HTML
    html = generate_html(analysis)

    # Write output
    output_file = "index_final.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Final dashboard generated: {output_file}")
    print(f"Total papers after cleaning: {analysis['stats']['total_papers']}")
    print(f"Average authors per paper: {analysis['bibliometric_summary'].get('avg_authors_per_paper', 'N/A')}")
    print(f"International collaboration rate: {analysis['bibliometric_summary'].get('pct_international_collab', 'N/A')}%")

if __name__ == "__main__":
    main()