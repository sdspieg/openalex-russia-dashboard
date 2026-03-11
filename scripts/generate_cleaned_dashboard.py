#!/usr/bin/env python3
"""
Generate cleaned dashboard excluding paratext and other data quality issues
"""

import json
from collections import defaultdict, Counter
from datetime import datetime

def load_data():
    """Load and clean the dataset"""
    print("Loading data...")
    all_papers = []

    # Load from merged dataset
    with open("results/merged_dataset/all_papers_merged.json", "r", encoding="utf-8") as f:
        raw_papers = json.load(f)

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
    """Analyze the cleaned dataset"""
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
        }
    }

    # Basic stats
    analysis["stats"]["total_papers"] = len(papers)

    # Process each paper
    citations = []
    authors_set = set()
    search_terms = ["russian foreign policy", "russian defense policy", "russian security policy",
                    "russia foreign policy", "russia defense policy", "russia security policy"]

    for paper in papers:
        # Year
        year = paper.get("publication_year")
        if year:
            analysis["temporal"][year] += 1

        # Citations
        cited_count = paper.get("cited_by_count", 0)
        citations.append(cited_count)

        # Authors
        for authorship in paper.get("authorships", []):
            author = authorship.get("author", {})
            if author and author.get("id"):
                authors_set.add(author.get("id"))

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
        "IT": "Italy", "NL": "Netherlands", "AU": "Australia"
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
    """Generate the cleaned HTML dashboard"""
    print("Generating cleaned dashboard...")

    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Russian Policy Research Dashboard - OpenAlex Analysis (Cleaned)</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --accent: #38bdf8;
            --warning: #f59e0b;
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
    </style>
</head>
<body>

<div class="warning-banner">
    ⚠️ DATA CLEANED: Removed ''' + str(len(json.load(open("results/merged_dataset/all_papers_merged.json"))) - analysis["stats"]["total_papers"]) + ''' paratext/metadata entries for accurate analysis
</div>

<header>
    <h1>Russian Policy Research Analysis (Cleaned)</h1>
    <div class="subtitle">
        <span>Source: OpenAlex API</span><br>
        ''' + f'{analysis["stats"]["total_papers"]:,}' + ''' Papers | ''' + f'{(analysis["stats"]["open_access"] / analysis["stats"]["total_papers"] * 100):.1f}' + '''% Open Access
    </div>
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

<div class="stats">
    <div class="stat-card"><h3>Total Papers</h3><p>''' + f'{analysis["stats"]["total_papers"]:,}' + '''</p></div>
    <div class="stat-card"><h3>Open Access</h3><p>''' + f'{analysis["stats"]["open_access"]:,}' + '''</p></div>
    <div class="stat-card"><h3>Total Citations</h3><p>''' + f'{analysis["stats"]["total_citations"]:,}' + '''</p></div>
    <div class="stat-card"><h3>Unique Authors</h3><p>''' + f'{analysis["stats"]["unique_authors"]:,}' + '''</p></div>
</div>

<div class="content-area">
    <div id="overview" class="content active">
        <div class="grid">
            <div class="card" id="search-location"></div>
            <div class="card" id="oa-status"></div>
            <div class="card" id="languages-chart"></div>
        </div>
    </div>

    <div id="temporal" class="content">
        <div class="grid">
            <div class="card full" id="timeline"></div>
        </div>
    </div>

    <div id="taxonomy" class="content">
        <div class="grid">
            <div class="card" id="domains-chart"></div>
            <div class="card" id="fields-chart"></div>
            <div class="card full" id="subfields-chart"></div>
        </div>
    </div>

    <div id="topics" class="content">
        <div class="grid">
            <div class="card" id="topics-chart"></div>
            <div class="card" id="themes-chart"></div>
        </div>
    </div>

    <div id="geography" class="content">
        <div class="grid">
            <div class="card" id="countries-chart"></div>
            <div class="card" id="institutions-chart"></div>
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
            <div class="card full" id="sources-chart"></div>
        </div>
    </div>
</div>

<div class="footer">
    <p>Generated: ''' + datetime.now().strftime("%Y-%m-%d %H:%M") + ''' | Data Source: OpenAlex API (Cleaned) | Excluded paratext and metadata entries</p>
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

// Tab switching
function showTab(id) {
    document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    if(window.event && event.currentTarget.classList.contains('nav-item')) event.currentTarget.classList.add('active');
    window.dispatchEvent(new Event('resize'));
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
Plotly.newPlot('languages-chart', [{
    x: langData.map(d => d[1]),
    y: langData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Language Distribution',
    margin: { l: 100 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
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
    line: { color: '#38bdf8', width: 2 },
    marker: { size: 4, color: '#38bdf8' }
}], {
    ...layout,
    title: 'Publication Timeline',
    xaxis: { ...layout.xaxis, title: 'Year' },
    yaxis: { ...layout.yaxis, title: 'Number of Papers' }
}, config);

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
Plotly.newPlot('fields-chart', [{
    x: fieldsData.map(d => d[1]),
    y: fieldsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Research Fields',
    margin: { l: 200 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
}, config);

// Subfields bar
const subfieldsData = Object.entries(data.taxonomy.subfields).slice(0, 10);
Plotly.newPlot('subfields-chart', [{
    x: subfieldsData.map(d => d[1]),
    y: subfieldsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Research Subfields (Top 10)',
    margin: { l: 250 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
}, config);

// Topics bar
const topicsData = Object.entries(data.topics).slice(0, 10);
Plotly.newPlot('topics-chart', [{
    x: topicsData.map(d => d[1]),
    y: topicsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Top Research Topics',
    margin: { l: 250 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
}, config);

// Themes bar
const themesData = Object.entries(data.research_themes).slice(0, 10);
Plotly.newPlot('themes-chart', [{
    x: themesData.map(d => d[1]),
    y: themesData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Research Themes',
    margin: { l: 180 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
}, config);

// Countries bar
const countriesData = Object.entries(data.countries).slice(0, 15);
Plotly.newPlot('countries-chart', [{
    x: countriesData.map(d => d[0]),
    y: countriesData.map(d => d[1]),
    type: 'bar',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Top Countries',
    yaxis: { ...layout.yaxis, title: 'Papers' },
    xaxis: { ...layout.xaxis, tickangle: -45 },
    margin: { ...layout.margin, b: 100 }
}, config);

// Institutions bar
const instData = Object.entries(data.institutions).slice(0, 10);
Plotly.newPlot('institutions-chart', [{
    x: instData.map(d => d[1]),
    y: instData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Top Institutions',
    margin: { l: 250 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
}, config);

// Sources bar
const sourcesData = Object.entries(data.sources).slice(0, 15);
Plotly.newPlot('sources-chart', [{
    x: sourcesData.map(d => d[1]),
    y: sourcesData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: tab20 }
}], {
    ...layout,
    title: 'Top Publication Venues',
    margin: { l: 350 },
    yaxis: { ...layout.yaxis, autorange: 'reversed' }
}, config);

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
    output_file = "index_cleaned.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard generated: {output_file}")
    print(f"Total papers after cleaning: {analysis['stats']['total_papers']}")
    print(f"Removed paratext and metadata: {6329 - analysis['stats']['total_papers']} entries")

if __name__ == "__main__":
    main()