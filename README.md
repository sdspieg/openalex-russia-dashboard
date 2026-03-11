# OpenAlex Russian Policy Research Dashboard

Interactive bibliometric analysis of Russian foreign, defense, and security policy research from OpenAlex.

## Live Dashboard
[View Dashboard](https://sdspieg.github.io/openalex-russian-policy/)

## Overview
- 6,329 papers analyzed (1916-2026)
- 71.4% open access rate
- Interactive visualizations with detailed explanations
- OpenAlex taxonomy analysis

## Key Findings

### The Hidden Literature Problem
**56% of relevant papers** (3,508 out of 6,329) only mention "Russian foreign policy", "Russian defense policy", or "Russian security policy" in the full-text, not in titles or abstracts. This demonstrates the critical importance of full-text search capabilities in comprehensive literature reviews.

### Open Access Distribution
- **Diamond OA:** 26% (no author fees)
- **Green OA:** 18.4% (repository archived)
- **Bronze OA:** 11.6% (free but no license)
- **Hybrid OA:** 7.9% (individual articles open)
- **Gold OA:** 7.5% (fully OA journal with fees)
- **Closed:** 28.6% (paywall restricted)

### Language Coverage
While English dominates (68.7%), significant research exists in:
- Russian: 29%
- Chinese: 1.5%
- German: 0.6%
- 12 other languages

### Research Growth
- Pre-2014: ~50 papers/year
- 2014-2021: ~150 papers/year (post-Crimea)
- 2022-2023: ~400 papers/year (Ukraine invasion)
- 2024-2026: Sustained high interest

## Features
- Temporal analysis of publication trends
- Geographic distribution of research
- Open Access types breakdown with explanations
- Language distribution analysis
- OpenAlex taxonomy (domains, fields, subfields)
- Citation impact analysis
- Author collaboration patterns
- Interactive modal help system

## Data Source
OpenAlex API - March 2026

Search Query: "Russian foreign policy" OR "Russian defense policy" OR "Russian security policy"

## Workshop Information
Created for the RuBase Methods Workshop at The Fletcher School
March 11-13, 2026

## Technical Stack
- **Data Source:** OpenAlex API
- **Data Processing:** Python with requests library
- **Visualizations:** Plotly.js
- **Deployment:** GitHub Pages

## Repository Structure
```
├── index.html                    # Main dashboard
├── scripts/                      # Python data collection scripts
│   ├── openalex_russian_policy_exercise.py
│   ├── generate_enhanced_dashboard.py
│   └── export_to_csv.py
├── results/                      # Data and output files
│   ├── russian_policy_papers.json
│   ├── russian_policy_papers.csv
│   └── russian_policy_dashboard_enhanced.html
└── documentation/                # Explanatory documents
    ├── OPEN_ACCESS_EXPLAINED.md
    ├── LANGUAGE_DISTRIBUTION_INSIGHTS.md
    └── OPENALEX_TAXONOMY_EXPLAINED.md
```

## How to Use

### For Workshop Participants
1. Visit the [live dashboard](https://sdspieg.github.io/openalex-russian-policy/)
2. Click on any visualization for interactive exploration
3. Use the "?" buttons to learn about each metric
4. Download the CSV file for your own analysis

### For Researchers
1. Clone this repository
2. Install Python dependencies: `pip install requests`
3. Run data collection: `python scripts/openalex_russian_policy_exercise.py`
4. Generate dashboard: `python scripts/generate_enhanced_dashboard.py`

## Citation
If you use this dashboard or data in your research, please cite:
```
RuBase Methods Workshop (2026). OpenAlex Russian Policy Research Dashboard.
The Fletcher School, Tufts University. https://sdspieg.github.io/openalex-russian-policy/
```

## License
MIT License - See LICENSE file for details

## Acknowledgments
- OpenAlex for providing free bibliometric data
- The Fletcher School for hosting the workshop
- Workshop participants for valuable feedback