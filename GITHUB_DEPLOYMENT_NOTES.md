# GitHub Deployment Notes

## Issue: Large File Size Limits
GitHub has strict file size limits:
- **Warning**: Files over 50 MB generate warnings
- **Hard limit**: Files over 100 MB are rejected

## Problem Files
The following files exceed GitHub's limits:
- `results/merged_dataset/all_papers_merged.json` - 119.69 MB
- `results/russian_policy_dataset/russian_policy_works.json` - 119.12 MB
- `results/fulltext_only_results/fulltext_only_papers.json` - 70.15 MB

## Solution Already Implemented
We've already split the large dataset into smaller chunks:
- `results/russian_policy_dataset/russian_policy_papers_part1.json`
- `results/russian_policy_dataset/russian_policy_papers_part2.json`
- `results/russian_policy_dataset/russian_policy_papers_part3.json`
- `results/russian_policy_dataset/russian_policy_papers_part4.json`

Each part is under 50 MB for smooth GitHub deployment.

## Current Dashboard Status
The dashboard (`index.html`) has been successfully updated with:

### ✅ New Bibliometric Features
- **Inward Citations Chart**: Distribution of citations received (0, 1-5, 6-10, 11-20, 21-50, 51-100, 100+)
- **Outward Citations Chart**: Distribution of references made (0-10, 11-20, 21-30, 31-40, 41-50, 50+)
- **Embedded Stats Boxes**: Each chart now has a floating stats box showing:
  - Mean, median, and total values
  - Overall rates and percentages
- **Key Insights Banner**: Summary of bibliometric findings at bottom

### ✅ Fixed Issues
- **X-axis formatting**: All temporal charts now show "Year" with proper integer formatting
- **Stats display**: Added comprehensive textboxes with overall statistics in each chart
- **Color scheme**: Using tab20 colors consistently

### 📊 Current Statistics
- **Total Papers**: 6,196 (after cleaning 133 paratext entries)
- **Inward Citations**: 27,257 total (4.4 average, 1.0 median)
- **Outward Citations**: 173,677 total (28.03 average, 29.0 median)
- **International Collaboration**: 6.2% of papers
- **Average Authors per Paper**: 1.48

## Deployment Strategy
1. **For dashboard updates**: Only push `index.html` and assets
2. **For data files**: Use the pre-split part files (already done)
3. **Alternative**: Use Git LFS for large files (not needed since we have splits)

## Git Commands for Clean Deployment
```bash
# Add only the index file
git add index.html

# Commit with message
git commit -m "Update dashboard with citation visualizations"

# Push to GitHub Pages
git push origin main
```

## Live URL
https://sdspieg.github.io/openalex-russian-policy/

## Note
The dashboard reads from the merged dataset locally for generation, but only the final HTML needs to be deployed to GitHub Pages, making it lightweight and fast to load.