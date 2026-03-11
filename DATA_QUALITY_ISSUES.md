# OpenAlex Dataset Quality Issues

## Critical Data Anomaly: PSR Cover Matter

### Summary
A major data quality issue has been identified where OpenAlex incorrectly parsed journal metadata as a research article, resulting in severely inflated authorship counts for multiple institutions.

### Details

**Problematic Entry:**
- **Title:** "PSR volume 92 issue 4 Cover and Back matter"
- **Year:** 1998
- **DOI:** https://doi.org/10.1017/s0003055400215785
- **OpenAlex ID:** https://openalex.org/W4244387853
- **Document Type:** Correctly identified as "paratext" but still processed as an article

### The Error

OpenAlex has incorrectly:
1. Parsed the American Political Science Review's cover/back matter as if it were a research article
2. Listed 67 individuals as "co-authors" of this non-existent paper
3. Assigned EACH person simultaneous affiliations with 11 institutions:
   - University of Central Florida
   - Yale University
   - University of Chicago
   - University of Miami
   - University of Cambridge
   - University of California, Los Angeles
   - Virginia Tech
   - Chicago Kent College of Law
   - Bridge University
   - nView Medical (United States)
   - Florida State University

### Impact on Statistics

This single error accounts for:
- **67 of 69** (97%) of University of Central Florida's "authorship instances"
- Inflated counts for all 11 institutions listed above
- False inclusion in the Russian policy dataset (matched on "policy" keyword)

### Notable "Authors" Listed
The 67 people incorrectly listed as authors include prominent figures who likely appeared in the journal's editorial board or acknowledgments:
- Daniel Patrick Moynihan (former U.S. Senator)
- Richard A. Epstein (legal scholar)
- Harvey Silverglate (civil liberties attorney)
- Michael Mandelbaum (foreign policy expert)

### Implications

1. **Institution counts are unreliable:** Any institution showing exactly 67 papers may be affected by this error
2. **Author counts are inflated:** The dataset shows 6,971 unique authors, but many may be from similar errors
3. **Search results are contaminated:** This entry has no relation to Russian foreign policy but appears in results

### Recommendations

1. Filter out all entries with `type: "paratext"` before analysis
2. Flag any paper with >20 authors for manual review
3. Check for other journal metadata entries (search for "Cover and Back matter", "Front matter", etc.)
4. Verify institution counts independently before using in research

---

## Additional Data Quality Issues Found

### 1. Paratext Contamination
- **99 paratext entries** incorrectly included in research dataset
- These are journal metadata (covers, front/back matter) not research articles
- Affects multiple journals including:
  - SLR (Slavic Review): Multiple volumes from 1994-2020
  - PSR (Political Science Review): Multiple volumes from 1960-1999
  - WPO (World Politics): Various issues
  - NPS: Various issues

### 2. NULL and Missing Titles
- **81 papers with NULL titles** in the dataset
- Makes it impossible to identify what these papers actually are

### 3. Abnormal Author Counts
- **Multiple entries with exactly 100 authors** (statistically impossible)
- Document types include: paratext, books, book chapters
- Examples:
  - "International Conference on Eurasian Economies 2022" (100 authors)
  - "References" (2006) - 100 authors for a reference list!
  - "Select Bibliography" (2018) - 100 authors for a bibliography!

### 4. Duplicate Titles
- **110 duplicate titles found**, including:
  - "Introduction" (22 duplicates)
  - "Russian Foreign Policy" (13 duplicates)
  - "Conclusion" (8 duplicates)
  - "Bibliography" (8 duplicates)
  - "Book Reviews" (6 duplicates)
- These generic titles suggest chapter-level entries mixed with full works

### 5. Temporal Anomalies
- **11 papers supposedly from before 1950**, including:
  - Papers from 1916, 1927, 1940s
  - Unlikely to be digitized/indexed for "Russian foreign policy" searches
  - May be historical references incorrectly parsed as primary sources

### 6. Cover/Matter Keywords
- **65 titles containing "cover", "matter", "front matter", "back matter"**
- Clear indication of journal metadata pollution

### Summary Statistics
- **At least 99 paratext entries** (1.6% of dataset)
- **81 NULL titles** (1.3% of dataset)
- **110 duplicate titles** (1.7% of unique titles)
- **Combined error rate: ~4-5% of dataset** is likely corrupted

### Recommendations for Data Cleaning

1. **Remove all paratext entries** (`type == 'paratext'`)
2. **Remove entries with NULL titles**
3. **Remove or flag entries with >50 authors** for manual review
4. **Deduplicate entries** with identical titles and years
5. **Remove journal metadata** (titles containing "cover", "matter", etc.)
6. **Validate temporal range** - consider removing pre-1950 entries
7. **Recalculate all statistics** after cleaning

### Impact on Analysis

These errors significantly affect:
- Institution rankings (inflated by ~100-author entries)
- Author counts (inflated by metadata entries)
- Temporal trends (contaminated by misdated entries)
- Topic analysis (non-research content included)

### Date Discovered
March 9, 2026

### Discovered By
Systematic analysis of OpenAlex Russian policy dataset revealing multiple categories of data quality issues.