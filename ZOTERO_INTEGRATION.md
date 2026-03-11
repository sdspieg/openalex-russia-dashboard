# OpenAlex to Zotero Integration Guide
## Building Comprehensive Corpora for LLM Analysis & Academic Reference

## The Dual Purpose: Why We Need Everything

Modern research requires TWO parallel workflows:

### 📚 Purpose 1: Traditional Academic Reference Management
- **Goal:** Capture all papers in Zotero/Mendeley/EndNote
- **Use:** Citations, footnotes, bibliographies
- **Need:** Complete metadata (authors, titles, DOIs, journals)

### 🤖 Purpose 2: LLM-Powered Corpus Analysis (Next Workshop Steps)
- **Goal:** Build comprehensive full-text corpus for AI analysis
- **Use:** Advanced computational text analysis
- **Need:** Maximum recall × precision of relevant full-text documents

### What We'll Do With This Corpus:
1. **Rich Taxonomy Development** - Use LLMs to build multi-level, multi-perspective taxonomies
2. **Intelligent Annotation** - Use LLMs to taxonomically annotate chunked text segments
3. **Pattern Discovery** - Identify themes and connections invisible to traditional methods
4. **Scale Analysis** - Process thousands of papers simultaneously

## The Hidden Literature Challenge

When using OpenAlex for comprehensive corpus building, we face a critical challenge:

**56% of relevant papers** in our Russian policy research dataset (3,508 out of 6,329) only mention search terms in their full-text, NOT in titles or abstracts. These papers are:
- Invisible to traditional database searches (Web of Science, Scopus)
- Missed by Zotero's web translator when browsing
- Excluded from standard bibliographic imports
- **CRITICAL for comprehensive LLM analysis** - they contain relevant content!

## Why This Matters for Both Workflows

### Traditional Workflow (Incomplete) ❌
1. Search database by title/abstract
2. Click Zotero browser button
3. Import visible results
4. **Miss 56% of relevant literature**
5. **Corpus too small for meaningful LLM analysis**
6. **References incomplete for comprehensive review**

### OpenAlex Full-Text Workflow (Comprehensive) ✅
1. Search OpenAlex including full-text
2. Export complete results with full-text flags
3. Import to Zotero for reference management
4. Build corpus with ALL relevant papers for LLM analysis
5. **Maximize recall while maintaining precision**
6. **Enable rich, multi-perspective taxonomic analysis**

## Step-by-Step Integration Process

### Step 1: Collect Data from OpenAlex

```python
import requests
import json

# OpenAlex API query with full-text search
def search_openalex_fulltext(query, mailto="your-email@example.com"):
    base_url = "https://api.openalex.org/works"

    params = {
        "search": query,  # Searches title, abstract, AND full-text
        "per-page": 200,
        "mailto": mailto
    }

    all_works = []
    cursor = "*"

    while cursor:
        params["cursor"] = cursor
        response = requests.get(base_url, params=params)
        data = response.json()

        all_works.extend(data["results"])
        cursor = data.get("meta", {}).get("next_cursor")

        if not cursor:
            break

    return all_works

# Example search
results = search_openalex_fulltext("Russian foreign policy OR Russian defense policy")
```

### Step 2: Convert to Zotero-Compatible Format

```python
def convert_to_ris(openalex_works):
    """Convert OpenAlex results to RIS format for Zotero import"""
    ris_entries = []

    for work in openalex_works:
        ris = []

        # Type of reference
        pub_type = work.get("type", "jour")
        if pub_type == "article":
            ris.append("TY  - JOUR")
        elif pub_type == "book":
            ris.append("TY  - BOOK")
        else:
            ris.append("TY  - GEN")

        # Title
        if work.get("title"):
            ris.append(f"TI  - {work['title']}")

        # Authors
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            if name:
                ris.append(f"AU  - {name}")

        # Publication year
        if work.get("publication_year"):
            ris.append(f"PY  - {work['publication_year']}")

        # Journal/Source
        source = work.get("primary_location", {}).get("source", {})
        if source.get("display_name"):
            ris.append(f"JO  - {source['display_name']}")

        # DOI
        doi = work.get("doi", "").replace("https://doi.org/", "")
        if doi:
            ris.append(f"DO  - {doi}")

        # Abstract
        if work.get("abstract"):
            # Clean abstract for RIS format
            abstract = work["abstract"].replace("\n", " ")
            ris.append(f"AB  - {abstract}")

        # OpenAlex ID as note
        ris.append(f"N1  - OpenAlex ID: {work['id']}")

        # URL
        if work.get("doi"):
            ris.append(f"UR  - {work['doi']}")

        # End of record
        ris.append("ER  - ")

        ris_entries.append("\n".join(ris))

    return "\n\n".join(ris_entries)

# Convert and save
ris_content = convert_to_ris(results)
with open("openalex_export.ris", "w", encoding="utf-8") as f:
    f.write(ris_content)
```

### Step 3: Import to Zotero

1. **Open Zotero Desktop**
2. **File → Import...**
3. **Select your RIS file** (openalex_export.ris)
4. **Choose import options:**
   - ✅ Place imported items in new collection
   - ✅ Download files (PDFs) when available
5. **Click Import**

## Alternative: BibTeX Format

If you prefer BibTeX format:

```python
def convert_to_bibtex(openalex_works):
    """Convert OpenAlex results to BibTeX format"""
    bibtex_entries = []

    for work in openalex_works:
        # Generate citation key
        first_author = ""
        if work.get("authorships"):
            first_author = work["authorships"][0].get("author", {}).get("display_name", "Unknown")
            first_author = first_author.split()[-1] if first_author else "Unknown"

        year = work.get("publication_year", "0000")
        work_id = work["id"].split("/")[-1]
        cite_key = f"{first_author}{year}_{work_id}"

        # Build BibTeX entry
        pub_type = "@article" if work.get("type") == "article" else "@misc"

        bibtex = [f"{pub_type}{{{cite_key},"]

        if work.get("title"):
            bibtex.append(f'  title = "{work["title"]}",')

        # Authors
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            if author.get("display_name"):
                authors.append(author["display_name"])
        if authors:
            bibtex.append(f'  author = "{" and ".join(authors)}",')

        if work.get("publication_year"):
            bibtex.append(f'  year = {work["publication_year"]},')

        # Journal
        source = work.get("primary_location", {}).get("source", {})
        if source.get("display_name"):
            bibtex.append(f'  journal = "{source["display_name"]}",')

        # DOI
        doi = work.get("doi", "").replace("https://doi.org/", "")
        if doi:
            bibtex.append(f'  doi = "{doi}",')

        # Abstract
        if work.get("abstract"):
            abstract = work["abstract"].replace("\n", " ").replace('"', "'")
            bibtex.append(f'  abstract = "{abstract}",')

        # Note with OpenAlex ID
        bibtex.append(f'  note = "OpenAlex ID: {work["id"]}"')

        bibtex.append("}")

        bibtex_entries.append("\n".join(bibtex))

    return "\n\n".join(bibtex_entries)
```

## Bulk Processing Tips

### For Large Result Sets (1000+ papers)

1. **Batch Processing:**
```python
def export_in_batches(works, batch_size=500):
    """Export large result sets in manageable batches"""
    for i in range(0, len(works), batch_size):
        batch = works[i:i+batch_size]
        ris_content = convert_to_ris(batch)

        filename = f"openalex_batch_{i//batch_size + 1}.ris"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(ris_content)

        print(f"Exported batch {i//batch_size + 1}: {len(batch)} items")
```

2. **Add Metadata Tags:**
```python
# Tag papers that were only found via full-text
for work in results:
    if not title_abstract_match(work, search_terms):
        # Add tag in RIS format
        ris.append("KW  - full-text-only")
        ris.append("KW  - hidden-literature")
```

## Verification Checklist

After importing to Zotero, verify:

- [ ] Total count matches OpenAlex results
- [ ] DOIs are properly linked
- [ ] Abstracts are included where available
- [ ] Publication years are correct
- [ ] Open Access papers are tagged
- [ ] Full-text-only papers are identified

## Common Issues & Solutions

### Issue: Missing Abstracts
**Solution:** OpenAlex may not have abstracts for all papers. Check the original source.

### Issue: Duplicate Entries
**Solution:** Zotero can merge duplicates. Select duplicates → Right-click → Merge Items

### Issue: Character Encoding Problems
**Solution:** Ensure UTF-8 encoding when saving RIS/BibTeX files:
```python
with open("export.ris", "w", encoding="utf-8") as f:
    f.write(ris_content)
```

### Issue: Import Fails
**Solution:** Validate your RIS/BibTeX format using online validators before importing

## Why Full-Text Search Matters

### Example: Russian Policy Research

**Traditional Search** (title/abstract only):
- Web of Science: ~2,800 results
- Scopus: ~3,100 results
- **Missing**: Papers that discuss Russian policy in methodology, case studies, or comparative analysis sections

**OpenAlex Full-Text Search**:
- Total: 6,329 results
- Title/abstract matches: 2,821 (45%)
- **Full-text only matches: 3,508 (55%)**
- These "hidden" papers include:
  - Comparative studies mentioning Russian policy
  - Methodology papers using Russian cases
  - Historical analyses with Russian policy sections
  - Regional studies with Russian policy context

## Best Practices for Dual-Purpose Corpus Building

### For Reference Management:
1. **Export complete metadata** including OpenAlex IDs for traceability
2. **Tag full-text-only matches** to identify hidden literature
3. **Verify imports** by comparing counts and spot-checking entries
4. **Organize collections** by search strategy or topic

### For LLM Corpus Analysis:
1. **Maximize recall** - Use full-text search to capture all relevant content
2. **Maintain precision** - Document inclusion/exclusion criteria
3. **Preserve full-text access** - Download PDFs where available
4. **Structure for chunking** - Organize papers by section for granular analysis
5. **Document provenance** - Track which papers came from full-text vs title/abstract matches

### The Precision × Recall Balance:
- **High Recall:** Capture everything potentially relevant (full-text search)
- **Maintained Precision:** Filter noise through:
  - Boolean operators (OR for synonyms, AND for requirements)
  - Year ranges for temporal relevance
  - Type filters (articles, not editorials)
  - Post-collection LLM filtering

## Next Steps in the Workshop

With your comprehensive corpus built from OpenAlex and organized in Zotero, you'll be ready for:

### Session 2: Building Rich Taxonomies with LLMs
- Create multi-level classification systems
- Develop multiple perspective taxonomies (theoretical, methodological, thematic)
- Use LLMs to suggest emergent categories from the corpus

### Session 3: Intelligent Corpus Annotation
- Chunk documents into analyzable segments
- Apply taxonomic labels using LLMs
- Create knowledge graphs from annotated content
- Discover hidden connections across the literature

## Further Resources

- [OpenAlex API Documentation](https://docs.openalex.org)
- [Zotero Import Documentation](https://www.zotero.org/support/importing)
- [RIS Format Specification](https://en.wikipedia.org/wiki/RIS_(file_format))
- [BibTeX Format Guide](https://www.bibtex.org/Format/)

## Related Documentation

- [DATA_QUALITY_ISSUES.md](./DATA_QUALITY_ISSUES.md) - Understanding OpenAlex data limitations
- [README.md](./README.md) - Project overview and the hidden literature problem
- [documentation/OPEN_ACCESS_EXPLAINED.md](./documentation/OPEN_ACCESS_EXPLAINED.md) - OA types in your imported library

---

*Remember: The papers you can't see in title/abstract searches may be the most important ones for understanding the full landscape of research.*