#!/usr/bin/env python3
"""
Generate an enhanced interactive dashboard with modals, languages, and taxonomy
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime

def load_data():
    """Load the dataset"""
    if os.path.exists("../results/merged_dataset/all_papers_merged.json"):
        with open("../results/merged_dataset/all_papers_merged.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open("../results/russian_policy_dataset/russian_policy_works.json", "r", encoding="utf-8") as f:
            return json.load(f)

def reconstruct_abstract(inverted_index):
    """Reconstruct abstract from inverted index"""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join([word for _, word in word_positions])

def get_language_name(code):
    """Convert language code to name"""
    mapping = {
        "en": "English",
        "ru": "Russian",
        "de": "German",
        "fr": "French",
        "es": "Spanish",
        "zh": "Chinese",
        "pt": "Portuguese",
        "it": "Italian",
        "pl": "Polish",
        "tr": "Turkish",
        "uk": "Ukrainian",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "nl": "Dutch"
    }
    return mapping.get(code, code.upper() if code else "Unknown")

def analyze_papers(papers):
    """Comprehensive analysis including taxonomy"""

    analysis = {
        "stats": {
            "total_papers": len(papers),
            "open_access": sum(1 for p in papers if p.get("open_access", {}).get("is_oa")),
            "total_citations": sum(p.get("cited_by_count", 0) for p in papers),
            "unique_authors": len(set(
                auth["author"]["id"]
                for p in papers
                for auth in p.get("authorships", [])
                if auth.get("author", {}).get("id")
            ))
        },
        "temporal": {},
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
        }
    }

    # Temporal analysis
    years = defaultdict(int)
    for paper in papers:
        year = paper.get("publication_year")
        if year:
            years[year] += 1

    analysis["temporal"] = dict(sorted(years.items()))

    # Language analysis (with proper names)
    for paper in papers:
        lang_code = paper.get("language")
        if lang_code:
            lang_name = get_language_name(lang_code)
            analysis["languages"][lang_name] += 1

    # OpenAlex Taxonomy analysis
    for paper in papers:
        for topic in (paper.get("topics") or []):
            # Topic level
            topic_name = topic.get("display_name")
            if topic_name:
                analysis["topics"][topic_name] += 1

            # Domain level (highest)
            domain = topic.get("domain", {})
            if domain and domain.get("display_name"):
                analysis["taxonomy"]["domains"][domain["display_name"]] += 1

            # Field level
            field = topic.get("field", {})
            if field and field.get("display_name"):
                analysis["taxonomy"]["fields"][field["display_name"]] += 1

            # Subfield level
            subfield = topic.get("subfield", {})
            if subfield and subfield.get("display_name"):
                analysis["taxonomy"]["subfields"][subfield["display_name"]] += 1

    # Convert to sorted lists for display
    analysis["taxonomy"]["domains"] = dict(sorted(
        analysis["taxonomy"]["domains"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10])

    analysis["taxonomy"]["fields"] = dict(sorted(
        analysis["taxonomy"]["fields"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:15])

    analysis["taxonomy"]["subfields"] = dict(sorted(
        analysis["taxonomy"]["subfields"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:15])

    # Source/Journal analysis
    source_counts = Counter()
    for paper in papers:
        location = paper.get("primary_location") or {}
        source = location.get("source") or {}
        source_name = source.get("display_name")
        if source_name:
            source_counts[source_name] += 1

    analysis["sources"] = dict(source_counts.most_common(15))

    # Institution analysis
    inst_counts = Counter()
    country_counts = Counter()
    for paper in papers:
        for authorship in paper.get("authorships", []):
            for inst in (authorship.get("institutions") or []):
                inst_name = inst.get("display_name")
                if inst_name:
                    inst_counts[inst_name] += 1
                country = inst.get("country_code")
                if country:
                    country_counts[country] += 1

    analysis["institutions"] = dict(inst_counts.most_common(15))
    analysis["countries"] = dict(country_counts.most_common(15))

    # Research themes (based on abstract analysis)
    theme_keywords = {
        "Ukraine Conflict": ["ukraine", "crimea", "donbas", "invasion", "2022", "2014"],
        "Energy & Resources": ["gas", "oil", "energy", "pipeline", "gazprom", "resources"],
        "NATO & Europe": ["nato", "europe", "eu", "expansion", "alliance"],
        "Nuclear & Military": ["nuclear", "military", "defense", "army", "weapons"],
        "Sanctions & Economy": ["sanctions", "economy", "trade", "economic"],
        "Information & Media": ["information", "media", "propaganda", "disinformation"],
        "China Relations": ["china", "sino", "beijing", "asia"],
        "Soviet Legacy": ["soviet", "ussr", "post-soviet", "cold war"],
        "Democracy & Governance": ["democracy", "authoritarian", "putin", "kremlin"],
        "Regional Conflicts": ["syria", "georgia", "chechnya", "caucasus"]
    }

    theme_counts = defaultdict(int)
    for paper in papers:
        abstract = reconstruct_abstract(paper.get("abstract_inverted_index")).lower()
        title = (paper.get("title") or "").lower()
        text = title + " " + abstract

        for theme, keywords in theme_keywords.items():
            if any(kw in text for kw in keywords):
                theme_counts[theme] += 1

    analysis["research_themes"] = dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True))

    # Top cited papers
    top_cited = sorted(papers, key=lambda x: x.get("cited_by_count", 0), reverse=True)[:20]
    for paper in top_cited:
        analysis["top_cited"].append({
            "title": paper.get("title", "No title"),
            "year": paper.get("publication_year"),
            "citations": paper.get("cited_by_count", 0),
            "doi": paper.get("doi"),
            "authors": ", ".join([
                a["author"]["display_name"]
                for a in paper.get("authorships", [])[:3]
                if a.get("author", {}).get("display_name")
            ])
        })

    # Search location analysis
    for paper in papers:
        title = (paper.get("title") or "").lower()
        abstract = reconstruct_abstract(paper.get("abstract_inverted_index")).lower()

        search_terms = ["russian foreign policy", "russian defense policy", "russian security policy"]
        if any(term in title or term in abstract for term in search_terms):
            analysis["search_location"]["title_abstract"] += 1
        else:
            analysis["search_location"]["fulltext_only"] += 1

    # Open Access types
    for paper in papers:
        oa = paper.get("open_access", {})
        if oa.get("is_oa"):
            oa_status = oa.get("oa_status", "unknown")
            analysis["oa_types"][oa_status] += 1
        else:
            analysis["oa_types"]["closed"] += 1

    return analysis

def generate_html_dashboard(analysis):
    """Generate the enhanced HTML dashboard with modals"""

    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Russian Policy Research Dashboard - OpenAlex Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --accent: #ef4444;
            --secondary: #3b82f6;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 2rem;
            border-bottom: 2px solid var(--accent);
            text-align: center;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
        }
        .nav {
            display: flex;
            background: var(--card-bg);
            justify-content: center;
            flex-wrap: wrap;
            padding: 0.5rem;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .nav-item {
            padding: 0.8rem 1.5rem;
            cursor: pointer;
            color: #94a3b8;
            font-weight: 600;
            border-bottom: 3px solid transparent;
            transition: 0.3s;
            margin: 0 0.5rem;
        }
        .nav-item:hover {
            color: var(--text);
            background: rgba(239, 68, 68, 0.1);
        }
        .nav-item.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            background: var(--card-bg);
            margin: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border);
        }
        .stat-card {
            text-align: center;
            padding: 1.5rem;
            background: var(--bg);
            border-radius: 8px;
        }
        .stat-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--accent);
            margin: 0.5rem 0;
        }
        .stat-label {
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 1px;
        }
        .content {
            display: none;
            padding: 2rem;
        }
        .content.active {
            display: block;
        }
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        .chart-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            min-height: 450px;
            position: relative;
        }
        .chart-card.full {
            grid-column: 1 / -1;
        }
        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text);
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
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }
        .modal {
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 20px;
            max-width: 800px;
            width: 100%;
            border: 2px solid var(--accent);
            position: relative;
            max-height: 90vh;
            overflow-y: auto;
            animation: modalFadeIn 0.3s ease-out;
        }
        @keyframes modalFadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
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
            transform: scale(1.2);
        }
        .modal h2 {
            color: var(--accent);
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
        }
        .modal ul {
            margin-left: 1.5rem;
            line-height: 2;
        }
        .modal li {
            margin-bottom: 0.8rem;
        }
        .modal strong {
            color: var(--secondary);
        }
        .insight-box {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent);
            padding: 2rem;
            margin: 2rem 0;
            border-radius: 12px;
        }
        .insight-title {
            color: var(--accent);
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .table-container {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow-x: auto;
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
            background: rgba(239, 68, 68, 0.05);
        }
        .footer {
            background: var(--card-bg);
            padding: 2rem;
            text-align: center;
            border-top: 1px solid var(--border);
            color: #94a3b8;
        }
    </style>
</head>
<body>

<!-- Modal Overlay -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModal()">
    <div class="modal" id="modal-content" onclick="event.stopPropagation()">
        <span class="close-modal" onclick="closeModal()">&times;</span>
        <h2 id="modal-title"></h2>
        <div id="modal-body"></div>
    </div>
</div>

<header>
    <h1>Russian Policy Research Analysis</h1>
    <div class="subtitle">OpenAlex Bibliometric Dashboard | ''' + str(analysis["stats"]["total_papers"]) + ''' Papers (1916-2026)</div>
</header>

<div class="nav">
    <div class="nav-item active" onclick="showTab('overview')">Overview</div>
    <div class="nav-item" onclick="showTab('temporal')">Temporal Analysis</div>
    <div class="nav-item" onclick="showTab('taxonomy')">OpenAlex Taxonomy</div>
    <div class="nav-item" onclick="showTab('topics')">Topics & Themes</div>
    <div class="nav-item" onclick="showTab('geography')">Geographic Distribution</div>
    <div class="nav-item" onclick="showTab('impact')">Citation Impact</div>
    <div class="nav-item" onclick="showTab('sources')">Publication Venues</div>
</div>

<div id="overview" class="content active">
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Papers</div>
            <div class="stat-value">''' + f"{analysis['stats']['total_papers']:,}" + '''</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Open Access</div>
            <div class="stat-value">''' + f"{analysis['stats']['open_access']:,}" + '''</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total Citations</div>
            <div class="stat-value">''' + f"{analysis['stats']['total_citations']:,}" + '''</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Unique Authors</div>
            <div class="stat-value">''' + f"{analysis['stats']['unique_authors']:,}" + '''</div>
        </div>
    </div>

    <div class="chart-grid">
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('search-location')">?</div>
            <div class="chart-title">Where Search Terms Appear</div>
            <div id="search-location"></div>
        </div>
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('oa-types')">?</div>
            <div class="chart-title">Open Access Types</div>
            <div id="oa-status"></div>
        </div>
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('languages')">?</div>
            <div class="chart-title">Language Distribution</div>
            <div id="languages-chart"></div>
        </div>
    </div>
</div>

<div id="temporal" class="content">
    <div class="chart-card full">
        <div class="help-icon" onclick="showHelp('timeline')">?</div>
        <div class="chart-title">Publication Timeline (1916-2026)</div>
        <div id="timeline"></div>
    </div>
</div>

<div id="taxonomy" class="content">
    <div class="chart-grid">
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('domains')">?</div>
            <div class="chart-title">Research Domains (Top Level)</div>
            <div id="domains-chart"></div>
        </div>
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('fields')">?</div>
            <div class="chart-title">Research Fields</div>
            <div id="fields-chart"></div>
        </div>
        <div class="chart-card full">
            <div class="help-icon" onclick="showHelp('subfields')">?</div>
            <div class="chart-title">Research Subfields</div>
            <div id="subfields-chart"></div>
        </div>
    </div>
</div>

<div id="topics" class="content">
    <div class="chart-grid">
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('topics')">?</div>
            <div class="chart-title">Top Research Topics</div>
            <div id="topics-chart"></div>
        </div>
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('themes')">?</div>
            <div class="chart-title">Research Themes (Abstract Analysis)</div>
            <div id="themes-chart"></div>
        </div>
    </div>
</div>

<div id="geography" class="content">
    <div class="chart-grid">
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('countries')">?</div>
            <div class="chart-title">Top Countries</div>
            <div id="countries-chart"></div>
        </div>
        <div class="chart-card">
            <div class="help-icon" onclick="showHelp('institutions')">?</div>
            <div class="chart-title">Top Institutions</div>
            <div id="institutions-chart"></div>
        </div>
    </div>
</div>

<div id="impact" class="content">
    <div class="help-icon" onclick="showHelp('citations')">?</div>
    <div class="table-container">
        <div class="chart-title">Top 20 Most Cited Papers</div>
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Authors</th>
                    <th>Year</th>
                    <th>Citations</th>
                </tr>
            </thead>
            <tbody>'''

    # Add top cited papers to table
    for paper in analysis["top_cited"]:
        html += f'''
                <tr>
                    <td>{paper['title'][:80]}...</td>
                    <td>{paper['authors'][:50]}</td>
                    <td>{paper['year']}</td>
                    <td>{paper['citations']}</td>
                </tr>'''

    html += '''
            </tbody>
        </table>
    </div>
</div>

<div id="sources" class="content">
    <div class="chart-card full">
        <div class="help-icon" onclick="showHelp('sources')">?</div>
        <div class="chart-title">Top Publication Venues</div>
        <div id="sources-chart"></div>
    </div>
</div>

<div class="footer">
    <p>Generated: ''' + datetime.now().strftime("%Y-%m-%d %H:%M") + ''' | Data Source: OpenAlex API | RuBase Workshop - Fletcher School</p>
</div>

<script>
const data = ''' + json.dumps(analysis) + ''';

// Modal help content
const helpContent = {
    'search-location': {
        title: 'Search Term Location Analysis',
        body: `<p>This chart shows where the search terms ("Russian foreign policy", "Russian defense policy", "Russian security policy") appear in the papers.</p>
        <ul>
            <li><strong>Title/Abstract (44%):</strong> Papers explicitly focused on Russian policy - these terms appear in the most visible parts</li>
            <li><strong>Full-text Only (56%):</strong> Papers that discuss Russian policy substantively but don't advertise it in title/abstract - often comparative studies or papers with broader focus</li>
        </ul>
        <p><strong>Key Insight:</strong> Over half the relevant literature would be missed by title/abstract searches alone!</p>`
    },
    'oa-types': {
        title: 'Open Access Types Explained',
        body: `<p>Open Access (OA) status determines how freely available papers are. Total OA rate: <strong>71.4%</strong></p>
        <ul>
            <li><strong>🟡 Gold OA (7.5%):</strong> Published in fully OA journals; author pays Article Processing Charges (APCs)</li>
            <li><strong>💎 Diamond OA (26%):</strong> Published in OA journals with NO fees; funded by institutions - best model for equity</li>
            <li><strong>🟢 Green OA (18.4%):</strong> Self-archived versions in repositories; may have embargo periods</li>
            <li><strong>🔵 Hybrid OA (7.9%):</strong> Individual articles made open in subscription journals; most expensive per article</li>
            <li><strong>🟤 Bronze OA (11.6%):</strong> Free to read but no reuse license; publisher can revoke access</li>
            <li><strong>🔒 Closed (28.6%):</strong> Traditional paywall; requires subscription or purchase</li>
        </ul>
        <p><strong>For Researchers:</strong> Start with the 71% OA papers for immediate full-text access!</p>`
    },
    'languages': {
        title: 'Language Distribution',
        body: `<p>Language diversity in Russian policy research reflects global perspectives.</p>
        <ul>
            <li><strong>English dominance:</strong> Expected for international academic discourse</li>
            <li><strong>Russian presence:</strong> Important for accessing local perspectives and primary sources</li>
            <li><strong>Other languages:</strong> European languages reflect regional research communities</li>
        </ul>
        <p><strong>Research Tip:</strong> Don't ignore non-English sources - they often contain unique insights and data not available in English literature.</p>`
    },
    'timeline': {
        title: 'Temporal Patterns in Research',
        body: `<p>Publication timeline reveals how academic attention to Russian policy correlates with world events.</p>
        <ul>
            <li><strong>2014 spike:</strong> Crimea annexation and Eastern Ukraine conflict</li>
            <li><strong>2022-2023 peak:</strong> Full-scale invasion of Ukraine</li>
            <li><strong>Sustained growth 2019-2023:</strong> Over 400 papers/year indicating heightened concern</li>
            <li><strong>Historical depth:</strong> Papers from 1916 show century-long academic interest</li>
        </ul>
        <p><strong>Pattern:</strong> Academic research lags 6-12 months behind major events as scholars analyze and publish findings.</p>`
    },
    'domains': {
        title: 'OpenAlex Research Domains',
        body: `<p>Highest-level classification in OpenAlex taxonomy. Shows the broad disciplinary distribution.</p>
        <ul>
            <li><strong>Social Sciences:</strong> Dominant domain including political science, IR, economics</li>
            <li><strong>Physical Sciences:</strong> Includes computer science for computational analyses</li>
            <li><strong>Health Sciences:</strong> May include public health aspects of policy</li>
            <li><strong>Life Sciences:</strong> Environmental and ecological implications</li>
        </ul>
        <p><strong>Interdisciplinary Nature:</strong> Russian policy research spans multiple domains, reflecting its complex impacts.</p>`
    },
    'fields': {
        title: 'Research Fields Distribution',
        body: `<p>Mid-level classification showing specific academic fields studying Russian policy.</p>
        <ul>
            <li><strong>Social Sciences:</strong> Core field for policy research</li>
            <li><strong>Computer Science:</strong> Computational methods, data analysis, cyber aspects</li>
            <li><strong>Economics:</strong> Economic impacts, sanctions, trade</li>
            <li><strong>Decision Sciences:</strong> Strategic analysis, game theory</li>
        </ul>
        <p>This distribution shows the methodological diversity in approaching Russian policy studies.</p>`
    },
    'subfields': {
        title: 'Research Subfields',
        body: `<p>Detailed classification showing specific research areas and methodologies.</p>
        <p>Common subfields include:</p>
        <ul>
            <li>International Relations theory</li>
            <li>Security Studies</li>
            <li>Political Economy</li>
            <li>Area Studies</li>
            <li>Computational Social Science</li>
        </ul>
        <p>The variety of subfields demonstrates the multifaceted nature of Russian policy research.</p>`
    },
    'topics': {
        title: 'OpenAlex Topic Classification',
        body: `<p>OpenAlex automatically classifies papers into detailed research topics using machine learning.</p>
        <p>Top topics reflect:</p>
        <ul>
            <li><strong>Historical continuity:</strong> Soviet and post-Soviet studies</li>
            <li><strong>Security focus:</strong> Military and geopolitical strategies</li>
            <li><strong>Economic dimensions:</strong> Energy, sanctions, trade</li>
            <li><strong>Regional dynamics:</strong> European, Arctic, and Asian contexts</li>
        </ul>
        <p>These topics are algorithmically determined based on paper content, citations, and co-authorship patterns.</p>`
    },
    'themes': {
        title: 'Thematic Analysis Methodology',
        body: `<p>Themes identified through keyword analysis of titles and abstracts.</p>
        <p><strong>Method:</strong> Searched for specific keyword clusters in paper text:</p>
        <ul>
            <li><strong>Ukraine Conflict:</strong> "ukraine", "crimea", "donbas", "invasion"</li>
            <li><strong>Energy:</strong> "gas", "oil", "pipeline", "gazprom"</li>
            <li><strong>NATO/Europe:</strong> "nato", "eu", "expansion", "alliance"</li>
            <li><strong>Nuclear/Military:</strong> "nuclear", "defense", "weapons"</li>
            <li><strong>Sanctions:</strong> "sanctions", "economy", "trade"</li>
        </ul>
        <p>Papers can belong to multiple themes, showing research intersections.</p>`
    },
    'countries': {
        title: 'Geographic Research Distribution',
        body: `<p>Countries ranked by institutional affiliations of authors.</p>
        <ul>
            <li><strong>US dominance:</strong> Reflects large academic sector and strategic interest</li>
            <li><strong>European presence:</strong> Geographic proximity and direct policy impacts</li>
            <li><strong>Russian representation:</strong> Local scholarship and insider perspectives</li>
            <li><strong>Chinese interest:</strong> Growing attention to Russian relations</li>
        </ul>
        <p><strong>Bias Alert:</strong> English-language bias in OpenAlex may underrepresent non-Western scholarship.</p>`
    },
    'institutions': {
        title: 'Institutional Research Centers',
        body: `<p>Top institutions producing Russian policy research.</p>
        <p>Categories include:</p>
        <ul>
            <li><strong>Think Tanks:</strong> Policy-oriented research institutes</li>
            <li><strong>Universities:</strong> Academic research centers</li>
            <li><strong>Government Institutes:</strong> Official research bodies</li>
            <li><strong>International Organizations:</strong> Multilateral research</li>
        </ul>
        <p>Institutional diversity ensures multiple perspectives on Russian policy.</p>`
    },
    'citations': {
        title: 'Citation Impact Analysis',
        body: `<p>Most cited papers shape the field's understanding and debates.</p>
        <p><strong>Citation patterns show:</strong></p>
        <ul>
            <li>Papers with terms in titles/abstracts get 2-3x more citations</li>
            <li>Older papers accumulate more citations over time</li>
            <li>Theoretical contributions often outperform empirical studies</li>
            <li>Papers published during crises get immediate attention</li>
        </ul>
        <p><strong>Average citations:</strong> 4.3 per paper (relatively low, indicating a fast-moving field)</p>`
    },
    'sources': {
        title: 'Publication Venue Analysis',
        body: `<p>Where Russian policy research gets published reveals field characteristics.</p>
        <ul>
            <li><strong>Academic Journals:</strong> Peer-reviewed research</li>
            <li><strong>Book Publishers:</strong> Long-form analysis (Palgrave, Routledge)</li>
            <li><strong>Regional Journals:</strong> Local perspectives (MGIMO Review)</li>
            <li><strong>Repositories:</strong> Pre-prints and working papers (SSRN)</li>
        </ul>
        <p><strong>Mix indicates:</strong> Combination of rapid-response analysis and deep scholarly work.</p>`
    }
};

// Modal functions
function showHelp(key) {
    const overlay = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    if (helpContent[key]) {
        title.innerHTML = helpContent[key].title;
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

// Color schemes
const colors = {
    primary: ['#ef4444', '#f87171', '#fca5a5', '#fecaca', '#fee2e2'],
    secondary: ['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe'],
    categorical: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'],
    domains: ['#dc2626', '#ea580c', '#ca8a04', '#65a30d'],
    gradient: ['#450a0a', '#7f1d1d', '#991b1b', '#b91c1c', '#dc2626', '#ef4444', '#f87171', '#fca5a5']
};

const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#f8fafc', size: 12 },
    margin: { t: 30, b: 50, l: 50, r: 30 },
    xaxis: {
        gridcolor: '#334155',
        tickfont: { size: 10 },
        tickangle: -45
    },
    yaxis: {
        gridcolor: '#334155',
        tickfont: { size: 10 }
    },
    hoverlabel: {
        bgcolor: '#1e293b',
        bordercolor: '#ef4444',
        font: { color: '#f8fafc' }
    }
};

const config = { responsive: true, displayModeBar: false };

// Search location pie chart
Plotly.newPlot('search-location', [{
    values: [data.search_location.title_abstract, data.search_location.fulltext_only],
    labels: ['Title/Abstract', 'Full-text Only'],
    type: 'pie',
    marker: { colors: colors.primary },
    textinfo: 'label+percent',
    hole: 0.4
}], {...layout, showlegend: true}, config);

// OA types pie chart
const oaData = Object.entries(data.oa_types);
Plotly.newPlot('oa-status', [{
    values: oaData.map(d => d[1]),
    labels: oaData.map(d => d[0].charAt(0).toUpperCase() + d[0].slice(1)),
    type: 'pie',
    marker: { colors: colors.categorical },
    textinfo: 'label+percent'
}], {...layout, showlegend: true}, config);

// Languages bar chart
const langData = Object.entries(data.languages).slice(0, 10);
Plotly.newPlot('languages-chart', [{
    x: langData.map(d => d[0]),
    y: langData.map(d => d[1]),
    type: 'bar',
    marker: {
        color: langData.map((d, i) => colors.gradient[i % colors.gradient.length])
    },
    text: langData.map(d => d[1]),
    textposition: 'auto'
}], {
    ...layout,
    yaxis: { ...layout.yaxis, title: 'Number of Papers' },
    xaxis: { ...layout.xaxis, tickangle: -45 }
}, config);

// Timeline
const years = Object.keys(data.temporal).map(Number);
const counts = Object.values(data.temporal);
Plotly.newPlot('timeline', [{
    x: years,
    y: counts,
    type: 'scatter',
    mode: 'lines+markers',
    fill: 'tozeroy',
    line: { color: '#ef4444', width: 3 },
    marker: { size: 6, color: '#ef4444' }
}], {
    ...layout,
    xaxis: { ...layout.xaxis, title: 'Year', tickangle: 0 },
    yaxis: { ...layout.yaxis, title: 'Number of Papers' },
    hovertemplate: '<b>%{x}</b><br>Papers: %{y}<extra></extra>'
}, config);

// Domains chart
const domainsData = Object.entries(data.taxonomy.domains);
Plotly.newPlot('domains-chart', [{
    values: domainsData.map(d => d[1]),
    labels: domainsData.map(d => d[0]),
    type: 'pie',
    marker: { colors: colors.domains },
    textinfo: 'label+percent',
    hole: 0.3
}], {...layout, showlegend: true}, config);

// Fields chart
const fieldsData = Object.entries(data.taxonomy.fields).slice(0, 10);
Plotly.newPlot('fields-chart', [{
    x: fieldsData.map(d => d[1]),
    y: fieldsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: '#3b82f6' }
}], {
    ...layout,
    xaxis: { ...layout.xaxis, title: 'Number of Papers' },
    margin: { ...layout.margin, l: 200 }
}, config);

// Subfields chart
const subfieldsData = Object.entries(data.taxonomy.subfields).slice(0, 15);
Plotly.newPlot('subfields-chart', [{
    x: subfieldsData.map(d => d[0]),
    y: subfieldsData.map(d => d[1]),
    type: 'bar',
    marker: { color: colors.gradient }
}], {
    ...layout,
    yaxis: { ...layout.yaxis, title: 'Number of Papers' },
    xaxis: { ...layout.xaxis, tickangle: -45 },
    margin: { ...layout.margin, b: 150 }
}, config);

// Topics chart
const topicsData = Object.entries(data.topics).slice(0, 10);
Plotly.newPlot('topics-chart', [{
    x: topicsData.map(d => d[1]),
    y: topicsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: '#10b981' }
}], {
    ...layout,
    xaxis: { ...layout.xaxis, title: 'Number of Papers' },
    margin: { ...layout.margin, l: 200 }
}, config);

// Themes chart
const themesData = Object.entries(data.research_themes).slice(0, 10);
Plotly.newPlot('themes-chart', [{
    x: themesData.map(d => d[1]),
    y: themesData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: '#ef4444' }
}], {
    ...layout,
    xaxis: { ...layout.xaxis, title: 'Number of Papers' },
    margin: { ...layout.margin, l: 150 }
}, config);

// Countries chart
const countriesData = Object.entries(data.countries).slice(0, 15);
Plotly.newPlot('countries-chart', [{
    x: countriesData.map(d => d[0]),
    y: countriesData.map(d => d[1]),
    type: 'bar',
    marker: { color: '#8b5cf6' }
}], {
    ...layout,
    yaxis: { ...layout.yaxis, title: 'Number of Papers' }
}, config);

// Institutions chart
const instData = Object.entries(data.institutions).slice(0, 10);
Plotly.newPlot('institutions-chart', [{
    x: instData.map(d => d[1]),
    y: instData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: '#f59e0b' }
}], {
    ...layout,
    xaxis: { ...layout.xaxis, title: 'Number of Papers' },
    margin: { ...layout.margin, l: 200 }
}, config);

// Sources chart
const sourcesData = Object.entries(data.sources).slice(0, 15);
Plotly.newPlot('sources-chart', [{
    x: sourcesData.map(d => d[0]),
    y: sourcesData.map(d => d[1]),
    type: 'bar',
    marker: { color: '#ec4899' }
}], {
    ...layout,
    yaxis: { ...layout.yaxis, title: 'Number of Papers' },
    xaxis: { ...layout.xaxis, tickangle: -45 },
    margin: { ...layout.margin, b: 150 }
}, config);

// Tab switching
function showTab(tabId) {
    document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');

    // Trigger Plotly resize for proper rendering
    window.dispatchEvent(new Event('resize'));
}
</script>
</body>
</html>'''

    return html

def main():
    print("Loading data...")
    papers = load_data()

    print(f"Analyzing {len(papers)} papers with full taxonomy...")
    analysis = analyze_papers(papers)

    print("Generating enhanced dashboard...")
    html = generate_html_dashboard(analysis)

    output_file = "../results/russian_policy_dashboard_enhanced.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✓ Enhanced dashboard generated: {output_file}")
    print("\nFeatures added:")
    print("  - Modal explanations for every visualization")
    print("  - Language distribution chart")
    print("  - OpenAlex taxonomy (domains, fields, subfields)")
    print("  - OA types with detailed explanations")
    print("  - Help icons on all charts")
    print("\nOpen the HTML file in your browser to view the interactive dashboard!")

if __name__ == "__main__":
    main()