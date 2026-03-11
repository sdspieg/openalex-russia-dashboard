# GitHub Pages Deployment Instructions

## Live URLs

Your OpenAlex Russia Dashboard is now live at:
- **GitHub Repository**: https://github.com/sdspieg/openalex-russia-dashboard
- **GitHub Pages (Live Site)**: https://sdspieg.github.io/openalex-russia-dashboard/

## Accessing Different Pages

- **Main Dashboard**: https://sdspieg.github.io/openalex-russia-dashboard/index.html
- **Data Story Landing Page**: https://sdspieg.github.io/openalex-russia-dashboard/landing_data_story.html

## How to Update the Site

### Option 1: Using Command Line

1. Make your changes locally
2. Commit and push to GitHub:
```bash
cd ~/openalex-dashboard
git add -A
git commit -m "Your update message"
git push origin main
```
3. GitHub Pages will automatically update within 1-2 minutes

### Option 2: Direct GitHub Editing

1. Go to https://github.com/sdspieg/openalex-russia-dashboard
2. Click on any file to edit it
3. Click the pencil icon to edit
4. Make your changes
5. Commit directly to main branch
6. Site updates automatically

## Repository Structure

```
openalex-russia-dashboard/
├── index.html                    # Main dashboard
├── landing_data_story.html       # PowerPoint-style data story
├── results/                      # Data files
│   └── russian_policy_dataset/
│       ├── russian_policy_papers.csv
│       └── russian_policy_papers_part*.json
├── scripts/                      # Python scripts for data collection
├── documentation/                # Documentation files
└── slide_*.png                   # Screenshots of landing page slides
```

## GitHub Pages Configuration

- **Branch**: main
- **Path**: / (root)
- **Custom Domain**: Not configured (using github.io subdomain)
- **HTTPS**: Enforced

## Troubleshooting

### If the site doesn't update:
1. Check GitHub Actions: https://github.com/sdspieg/openalex-russia-dashboard/actions
2. Clear browser cache (Ctrl+Shift+R)
3. Wait 2-5 minutes for GitHub Pages to rebuild

### To check deployment status:
```bash
gh api repos/sdspieg/openalex-russia-dashboard/pages/builds/latest
```

### To manually trigger rebuild:
```bash
# Make a small change and push
echo " " >> README.md
git add README.md
git commit -m "Trigger rebuild"
git push origin main
```

## Local Development

To run locally:
```bash
cd ~/openalex-dashboard
python3 -m http.server 8089
# Open browser to http://localhost:8089
```

## Future Enhancements

Consider adding:
- Custom domain (e.g., openalex.yourdomain.com)
- Google Analytics for tracking
- Auto-deployment from Dropbox folder using GitHub Actions
- Data refresh automation

## Support

For issues or questions:
- Repository Issues: https://github.com/sdspieg/openalex-russia-dashboard/issues
- GitHub Pages Docs: https://docs.github.com/en/pages