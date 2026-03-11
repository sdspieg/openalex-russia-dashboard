# OpenAlex Russian Policy Research Dashboard

An interactive presentation and dashboard showcasing the power of OpenAlex for bibliometric analysis, featuring research on Russian foreign, defense, and security policy.

## Live Demo
🌐 **[View Live Dashboard](https://sdspieg.github.io/openalex-russia-dashboard/)**

## Project Overview

This project demonstrates OpenAlex's capabilities through a comprehensive analysis of Russian policy research literature. It consists of two main components:

1. **Landing Page Presentation** (`index.html`) - A 12-slide data story introducing OpenAlex
2. **Interactive Dashboard** (`dashboard.html`) - Deep-dive analytics with multiple visualizations

## 📁 Repository Structure

```
openalex/
│
├── 🎯 Core Files
│   ├── index.html                    # Landing page with 12-slide presentation
│   ├── dashboard.html                # Interactive analytical dashboard
│   └── logos_transparent.png         # Combined HCSS & RuBase logos
│
├── 📊 Scripts & Analysis
│   └── scripts/
│       ├── openalex_russian_policy_exercise.py    # Initial data collection
│       ├── openalex_simple_search.py              # Basic API queries
│       ├── fulltext_only_search.py                # Full-text search analysis
│       ├── merge_datasets.py                      # Data consolidation
│       ├── export_to_csv.py                       # CSV export utility
│       └── generate_final_dashboard.py            # Dashboard generator
│
├── 📝 Documentation
│   ├── README.md                     # This file
│   ├── DATA_QUALITY_ISSUES.md        # Known data limitations
│   ├── DEPLOYMENT_INSTRUCTIONS.md    # GitHub Pages setup guide
│   └── documentation/
│       ├── OPEN_ACCESS_EXPLAINED.md
│       ├── LANGUAGE_DISTRIBUTION_INSIGHTS.md
│       └── OPENALEX_TAXONOMY_EXPLAINED.md
│
├── 🎨 Assets
│   ├── hcss_logo.svg                 # HCSS organization logo
│   ├── rubase_logo.svg               # RuBase project logo
│   └── *.png                         # Various screenshots & visuals
│
└── 🔧 Configuration
    └── .git/                         # Git repository metadata
```

## 🚀 Key Features

### Landing Page Presentation
- **What is OpenAlex?** Introduction to the 293M+ scholarly works database
- **Interactive navigation** with keyboard controls (arrow keys, ESC)
- **Comparison with competitors** (Dimensions, Scopus, Web of Science)
- **Live API demonstrations** with real-time queries
- **Partner acknowledgments** for HCSS and RuBase projects

### Analytics Dashboard
- **6,329 papers analyzed** (1916-2026)
- **71.4% open access rate** breakdown by type
- **Temporal trends** showing research growth patterns
- **Geographic distribution** of global research output
- **Language diversity** across 15+ languages
- **OpenAlex taxonomy** mapping (domains → fields → subfields)
- **Citation impact** analysis and collaboration networks

## 📊 Key Insights

### The Hidden Literature Challenge
**56% of relevant papers** (3,508/6,329) only mention search terms in full-text, not titles/abstracts. This highlights the critical importance of full-text search capabilities. See [ZOTERO_INTEGRATION.md](./ZOTERO_INTEGRATION.md) for how to capture this hidden literature in your reference manager.

### Research Evolution
- **Pre-2014:** ~50 papers/year baseline
- **2014-2021:** ~150 papers/year (post-Crimea annexation)
- **2022-2023:** ~400 papers/year (Ukraine invasion surge)
- **2024-2026:** Sustained elevated interest

### Open Access Distribution
- **Diamond OA:** 26% (no fees, community-driven)
- **Green OA:** 18.4% (repository deposits)
- **Bronze OA:** 11.6% (free reading, no reuse)
- **Hybrid OA:** 7.9% (selective article access)
- **Gold OA:** 7.5% (full journal OA with APCs)
- **Closed:** 28.6% (subscription required)

## 🛠 Technical Architecture

### Data Pipeline
1. **Collection:** Python scripts query OpenAlex API
2. **Processing:** JSON data parsed and enriched
3. **Visualization:** Plotly.js for interactive charts
4. **Deployment:** Static site on GitHub Pages

### Technologies Used
- **Backend:** Python 3.x with requests library
- **Frontend:** HTML5, CSS3, JavaScript ES6
- **Visualization:** Plotly.js for interactive charts
- **Hosting:** GitHub Pages for static deployment
- **Version Control:** Git with GitHub remote

## 🎓 Workshop Context

Created for the **RuBase Methods Workshop** at The Fletcher School, Tufts University (March 11-13, 2026). This dashboard serves as both:
- A teaching tool for OpenAlex capabilities
- A practical demonstration of bibliometric analysis
- A resource for Russian policy researchers

## 🤝 Acknowledgments

- **OpenAlex** for providing free, open bibliometric data
- **Arcadia Fund** (Lisbet Rausing & Peter Baldwin) for supporting open science
- **HCSS** (The Hague Centre for Strategic Studies) for partnership
- **RuBase Project** for Russian expertise database collaboration
- **The Fletcher School** for hosting the workshop

## 📖 Usage Instructions

### For Workshop Participants
1. Visit the [live dashboard](https://sdspieg.github.io/openalex-russia-dashboard/)
2. Start with the landing page for context
3. Navigate to the dashboard for detailed analysis
4. Use "?" buttons for metric explanations
5. Download CSV data for custom analysis

### For Developers
```bash
# Clone repository
git clone https://github.com/sdspieg/openalex-russia-dashboard.git

# Install dependencies
pip install requests playwright

# Collect fresh data
python scripts/openalex_russian_policy_exercise.py

# Generate updated dashboard
python scripts/generate_final_dashboard.py

# Deploy to GitHub Pages
git add .
git commit -m "Update dashboard"
git push origin main
```

## 📄 License

MIT License - See LICENSE file for details

## 📬 Contact

For questions about this dashboard or the RuBase Methods Workshop, please contact the workshop organizers at The Fletcher School.

---

*Last updated: March 2026 | Data source: OpenAlex API*