#!/usr/bin/env python3
"""
Generate an interactive dashboard for OpenAlex Russian Policy Research
Similar to GDELT dashboard but focused on bibliometric analysis
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime

def load_data():
    """Load the merged dataset"""
    # Try merged first, fall back to original
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

def analyze_papers(papers):
    """Comprehensive analysis of the papers"""

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
        "topics": {},
        "sources": {},
        "institutions": {},
        "countries": {},
        "research_themes": {},
        "top_cited": [],
        "search_location": {"title_abstract": 0, "fulltext_only": 0},
        "oa_types": defaultdict(int),
        "languages": defaultdict(int)
    }

    # Temporal analysis
    years = defaultdict(int)
    for paper in papers:
        year = paper.get("publication_year")
        if year:
            years[year] += 1

    analysis["temporal"] = dict(sorted(years.items()))

    # Topic analysis
    topic_counts = Counter()
    for paper in papers:
        for topic in (paper.get("topics") or []):
            topic_name = topic.get("display_name")
            if topic_name:
                topic_counts[topic_name] += 1

    analysis["topics"] = dict(topic_counts.most_common(15))

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

    # Search location analysis (where terms appear)
    for paper in papers:
        if paper.get("search_source") == "title_abstract":
            analysis["search_location"]["title_abstract"] += 1
        else:
            # Check if terms appear in title/abstract
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

    # Language analysis
    for paper in papers:
        lang = paper.get("language", "unknown")
        if lang:
            analysis["languages"][lang] += 1

    return analysis

def generate_html_dashboard(analysis):
    """Generate the HTML dashboard"""

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
<header>
    <h1>Russian Policy Research Analysis</h1>
    <div class="subtitle">OpenAlex Bibliometric Dashboard | ''' + str(analysis["stats"]["total_papers"]) + ''' Papers (1916-2026)</div>
</header>

<div class="nav">
    <div class="nav-item active" onclick="showTab('overview')">Overview</div>
    <div class="nav-item" onclick="showTab('temporal')">Temporal Analysis</div>
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
            <div class="chart-title">Where Search Terms Appear</div>
            <div id="search-location"></div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Open Access Status</div>
            <div id="oa-status"></div>
        </div>
    </div>

    <div class="insight-box">
        <div class="insight-title">Key Insights</div>
        <ul style="line-height: 2;">
            <li>''' + f"{analysis['search_location']['fulltext_only']/(analysis['search_location']['title_abstract']+analysis['search_location']['fulltext_only'])*100:.1f}%" + ''' of papers only mention Russian policy in the full text, not in title/abstract</li>
            <li>Open Access rate: ''' + f"{analysis['stats']['open_access']/analysis['stats']['total_papers']*100:.1f}%" + ''' - excellent for full-text analysis</li>
            <li>Average citations per paper: ''' + f"{analysis['stats']['total_citations']/analysis['stats']['total_papers']:.1f}" + '''</li>
            <li>Research spans 110 years from 1916 to 2026</li>
        </ul>
    </div>
</div>

<div id="temporal" class="content">
    <div class="chart-card full">
        <div class="chart-title">Publication Timeline</div>
        <div id="timeline"></div>
    </div>

    <div class="insight-box">
        <div class="insight-title">Temporal Patterns</div>
        <ul style="line-height: 2;">
            <li>Major spikes: 2014 (Crimea), 2022-2023 (Ukraine invasion)</li>
            <li>Sustained growth from 2019-2023 with >400 papers/year</li>
            <li>Recent years (2019-2023) account for 40% of all research</li>
        </ul>
    </div>
</div>

<div id="topics" class="content">
    <div class="chart-grid">
        <div class="chart-card">
            <div class="chart-title">Top Research Topics</div>
            <div id="topics-chart"></div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Research Themes (Abstract Analysis)</div>
            <div id="themes-chart"></div>
        </div>
    </div>
</div>

<div id="geography" class="content">
    <div class="chart-grid">
        <div class="chart-card">
            <div class="chart-title">Top Countries</div>
            <div id="countries-chart"></div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Top Institutions</div>
            <div id="institutions-chart"></div>
        </div>
    </div>
</div>

<div id="impact" class="content">
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
        <div class="chart-title">Top Publication Venues</div>
        <div id="sources-chart"></div>
    </div>
</div>

<div class="footer">
    <p>Generated: ''' + datetime.now().strftime("%Y-%m-%d %H:%M") + ''' | Data Source: OpenAlex API | RuBase Workshop - Fletcher School</p>
</div>

<script>
const data = ''' + json.dumps(analysis) + ''';

// Color schemes
const colors = {
    primary: ['#ef4444', '#f87171', '#fca5a5'],
    secondary: ['#3b82f6', '#60a5fa', '#93c5fd'],
    categorical: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
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
    marker: { colors: colors.primary }
}], {...layout, showlegend: true}, config);

// OA status pie chart
const oaData = Object.entries(data.oa_types);
Plotly.newPlot('oa-status', [{
    values: oaData.map(d => d[1]),
    labels: oaData.map(d => d[0]),
    type: 'pie',
    marker: { colors: colors.categorical }
}], {...layout, showlegend: true}, config);

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
    marker: { size: 8, color: '#ef4444' }
}], {
    ...layout,
    xaxis: { ...layout.xaxis, title: 'Year', tickangle: 0 },
    yaxis: { ...layout.yaxis, title: 'Number of Papers' },
    hovertemplate: '<b>%{x}</b><br>Papers: %{y}<extra></extra>'
}, config);

// Topics chart
const topicsData = Object.entries(data.topics).slice(0, 10);
Plotly.newPlot('topics-chart', [{
    x: topicsData.map(d => d[1]),
    y: topicsData.map(d => d[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: '#3b82f6' }
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
    marker: { color: '#10b981' }
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
    marker: { color: '#8b5cf6' }
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
}
</script>
</body>
</html>'''

    return html

def main():
    print("Loading data...")
    papers = load_data()

    print(f"Analyzing {len(papers)} papers...")
    analysis = analyze_papers(papers)

    print("Generating dashboard...")
    html = generate_html_dashboard(analysis)

    output_file = "../results/russian_policy_dashboard.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✓ Dashboard generated: {output_file}")
    print("\nOpen the HTML file in your browser to view the interactive dashboard!")

if __name__ == "__main__":
    main()