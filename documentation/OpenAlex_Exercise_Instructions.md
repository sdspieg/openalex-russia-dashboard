# OpenAlex Bibliometric Exercise: Discovering Your Research Domain

## Workshop Exercise for Day 1: DISCOVER

### Learning Objectives
By the end of this exercise, you will:
1. Understand how to use OpenAlex's API for systematic literature discovery
2. Learn to construct effective search queries for YOUR specific research area
3. Practice extracting and analyzing bibliometric metadata
4. Prepare a corpus for subsequent LLM analysis

### What is OpenAlex?
OpenAlex is a free, open-source index of over 250 million academic works. It provides:
- Full-text search across 60+ million open-access papers
- Complete bibliometric metadata (citations, authors, institutions, topics)
- RESTful API with no authentication required (though email is recommended)
- Daily updates from thousands of publishers and repositories

### Exercise Overview
You'll search for academic research in YOUR field of interest, then analyze the results to understand:
- Research trends over time
- Key publication venues
- Citation patterns
- Topic distributions
- Open access availability

## Part 1: Crafting Your Search Strategy

### Example Search Queries by Discipline

#### Political Science / International Relations
```python
"Russian foreign policy" OR "Russian defense policy" OR "Russian security policy"
# OR try: "NATO expansion" OR "European security architecture"
# OR try: "China belt and road" OR "BRI geopolitics"
```

#### History
```python
"Soviet collapse" OR "post-Soviet transition" OR "Russian democratization"
# OR try: "Cold War archives" OR "Soviet documents declassified"
# OR try: "Gorbachev reforms" OR "perestroika glasnost"
```

#### Economics
```python
"Russian economy sanctions" OR "Russia energy exports" OR "ruble crisis"
# OR try: "emerging markets volatility" OR "BRICS economies"
# OR try: "resource curse" AND "Russia"
```

#### Area Studies (Different Countries)
```python
# China focus:
"Chinese foreign policy" OR "China rise" OR "China US competition"

# Middle East focus:
"Iran nuclear program" OR "Saudi Arabia Vision 2030" OR "Gulf security"

# Europe focus:
"European strategic autonomy" OR "EU defense policy" OR "Brexit security implications"
```

#### Security Studies
```python
"hybrid warfare" OR "gray zone conflict" OR "information warfare"
# OR try: "nuclear deterrence" AND "21st century"
# OR try: "cyber warfare" OR "cyber deterrence"
```

#### Sociology / Anthropology
```python
"Russian civil society" OR "Russian social movements" OR "Russian nationalism"
# OR try: "post-Soviet identity" OR "Russian diaspora"
```

### Constructing Your Own Query
1. **Identify 2-3 key concepts** in your research area
2. **Use quoted phrases** for exact matches: `"your exact phrase"`
3. **Connect with OR** to broaden: `"concept A" OR "concept B"`
4. **Use AND to narrow**: `"broad topic" AND "specific aspect"`
5. **Consider synonyms**: Include alternative terms for the same concept

### API Endpoint
```
https://api.openalex.org/works?search=YOUR_QUERY
```

## Part 2: Running the Exercise

### Prerequisites
1. Python 3.x installed
2. `requests` library (`pip install requests`)
3. Internet connection
4. Your email address (for polite pool access)

### Step-by-Step Instructions

#### Step 1: Set Up Your Environment
```bash
# Navigate to the workshop folder
cd "/mnt/c/Users/Stephan/Dropbox/Presentations/2603 - Boston"

# Install required library if needed
pip install requests
```

#### Step 2: Configure the Script for YOUR Research
Edit `openalex_russian_policy_exercise.py`:

**Line 16 - Add your email:**
```python
MAILTO = "your.email@fletcher.edu"  # Replace with YOUR email
```

**Line 24 - Add YOUR search query:**
```python
# Replace this with YOUR research topic from Part 1 above
SEARCH_QUERY = '"your first concept" OR "your second concept"'

# Examples:
# SEARCH_QUERY = '"NATO expansion" OR "European security architecture"'  # IR
# SEARCH_QUERY = '"Soviet collapse" OR "post-Soviet transition"'  # History
# SEARCH_QUERY = '"emerging markets" AND "financial crisis"'  # Economics
# SEARCH_QUERY = '"Chinese soft power" OR "China public diplomacy"'  # China studies
```

#### Step 3: Run the Script
```bash
python openalex_russian_policy_exercise.py
```

#### Step 4: Monitor Progress
The script will show:
- Number of pages being downloaded
- Running count of papers found
- Analysis results when complete

Expected output:
```
===========================================================
OpenAlex Russian Policy Research Exercise
RuBase Workshop - Fletcher School
===========================================================
[*] Starting OpenAlex search for Russian policy research
    Search query: "Russian foreign policy" OR "Russian defense policy" OR "Russian security policy"
    - Fetching page 1...
    - Downloaded 200 works so far...
    - Fetching page 2...
    - Downloaded 400 works so far...
    ...
```

## Part 3: Understanding the Output

### Generated Files

1. **`russian_policy_dataset/russian_policy_works.json`**
   - Complete metadata for all papers
   - Includes authors, institutions, citations, topics, etc.

2. **`russian_policy_dataset/titles_and_abstracts.txt`**
   - Human-readable text file
   - Ready for LLM analysis in tomorrow's session

### Key Metrics to Observe (Adapt to Your Field)

#### Temporal Patterns
- When was research on your topic most active?
- Can you identify spikes around major events?
- How has the volume changed over the past decade?

#### Geographic & Institutional Distribution
- Which countries/institutions dominate your field?
- Are there regional biases in who studies what?
- Where are the emerging research centers?

#### Open Access Availability
- What percentage of papers are freely available?
- Does open access correlate with citations in your field?

#### Topic Clustering
- What related topics appear frequently with yours?
- Can you identify distinct research communities or schools of thought?
- What interdisciplinary connections emerge?

## Part 4: Hands-On Analysis Tasks

### Task 1: Filter by Year
Modify the script to only fetch papers from 2022 onwards:
```python
params = {
    "search": SEARCH_QUERY,
    "filter": "publication_year:2022-2026",  # Add this line
    "per_page": PER_PAGE,
    ...
}
```

### Task 2: Find Your Institution
Check if your institution has published on this topic:
```python
# In the analyze_results function, add:
my_institution = "Fletcher"  # or your institution
for work in works:
    for authorship in work.get("authorships", []):
        for inst in authorship.get("institutions", []):
            if my_institution in inst.get("display_name", ""):
                print(f"Found: {work.get('title')}")
```

### Task 3: Export for Excel
Add CSV export capability:
```python
import csv

def export_to_csv(works):
    with open("russian_policy_papers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Year", "Journal", "Citations", "DOI"])
        for w in works:
            writer.writerow([
                w.get("title"),
                w.get("publication_year"),
                w.get("primary_location", {}).get("source", {}).get("display_name"),
                w.get("cited_by_count"),
                w.get("doi")
            ])
```

## Part 5: Discussion Questions

### General Questions (All Disciplines)
1. **Coverage**: Are there gaps in OpenAlex's coverage of your research area?
2. **Language Bias**: How many non-English papers did you find? What does this tell you?
3. **Citation Patterns**: Which papers are most influential? Can you explain why?
4. **Interdisciplinary Connections**: What unexpected fields cite work in your area?

### Discipline-Specific Reflections

**For Historians:**
- How well are primary sources and archives represented?
- Can you track historiographical debates through citation patterns?

**For Political Scientists/IR:**
- How do publication patterns correlate with real-world events?
- Is there a theory vs. policy divide in the literature?

**For Economists:**
- What's the balance between theoretical and empirical work?
- How quickly do papers on current economic crises appear?

**For Area Studies Scholars:**
- Is there a bias toward certain regions or countries?
- How well represented are local scholars from the region you study?

**For Security Studies:**
- How has the field evolved with new forms of conflict?
- What's the lag between emerging threats and academic analysis?

## Advanced Extensions (Optional)

### Extension 1: Comparative Analysis
Compare your topic across different contexts:

**For Country Comparisons:**
```python
SEARCH_QUERY_COUNTRY_A = '"Russia energy exports" OR "Gazprom"'
SEARCH_QUERY_COUNTRY_B = '"Saudi Arabia energy exports" OR "Aramco"'
```

**For Temporal Comparisons:**
```python
# Cold War era vs. post-Cold War
params["filter"] = "publication_year:1980-1991"  # Cold War
params["filter"] = "publication_year:2010-2024"  # Recent
```

**For Methodological Comparisons:**
```python
# Quantitative vs. qualitative methods in your field
SEARCH_QUERY = '"your topic" AND ("regression analysis" OR "statistical model")'
SEARCH_QUERY = '"your topic" AND ("case study" OR "ethnography" OR "interviews")'
```

### Extension 2: Author Networks
Extract co-authorship patterns to identify research communities:
```python
def build_author_network(works):
    coauthorships = {}
    for work in works:
        authors = [a["author"]["display_name"]
                  for a in work.get("authorships", [])
                  if a.get("author", {}).get("display_name")]
        # Build edge list for network analysis
```

### Extension 3: Full Entity Enrichment
Fetch complete profiles for all authors, institutions, and journals (like the GDELT example):
```python
def fetch_all_entities(works):
    # Extract unique entity IDs
    # Batch fetch full profiles
    # Save to separate folders
```

## Troubleshooting

### Common Issues and Solutions

1. **"No module named 'requests'"**
   ```bash
   pip install requests
   ```

2. **Rate limit errors**
   - Make sure you've added your email to MAILTO
   - The script includes delays, but you can increase `time.sleep(0.1)` to `time.sleep(0.5)`

3. **No results found**
   - Check your internet connection
   - Verify the API is working: https://api.openalex.org/works?search=test

4. **Unicode/encoding errors**
   - The script uses UTF-8 encoding
   - On Windows, you might need to run: `chcp 65001` before running Python

## Next Steps

Tomorrow (Day 2), we'll use the extracted abstracts to:
1. Build a custom taxonomy for Russian policy research
2. Use LLMs to classify papers into our taxonomy
3. Identify research gaps and opportunities

## Additional Resources

- OpenAlex Documentation: https://docs.openalex.org
- API Playground: https://openalex.org/works
- Example Notebooks: https://github.com/ourresearch/openalex-documentation
- The Lens (alternative): https://www.lens.org

## Notes for Instructors

- Total exercise time: 30-45 minutes
- Expected data volume: 500-2000 papers depending on exact query
- API is free but polite (100ms between requests)
- Can be run simultaneously by all participants
- Results can be cached/shared if internet is slow