#!/usr/bin/env python3
"""
Visually inspect the dashboard using Playwright
Takes screenshots of each tab for verification
"""

from playwright.sync_api import sync_playwright
import os
import time

def inspect_dashboard():
    dashboard_path = os.path.abspath("../results/russian_policy_dashboard.html")
    screenshot_dir = "../results/dashboard_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        # Load the dashboard
        print(f"Loading dashboard: file://{dashboard_path}")
        page.goto(f"file://{dashboard_path}")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Wait for Plotly to render

        # Define tabs to check
        tabs = [
            ("overview", "Overview Tab"),
            ("temporal", "Temporal Analysis"),
            ("topics", "Topics & Themes"),
            ("geography", "Geographic Distribution"),
            ("impact", "Citation Impact"),
            ("sources", "Publication Venues")
        ]

        # Take screenshot of each tab
        for tab_id, tab_name in tabs:
            print(f"\nInspecting {tab_name}...")

            # Click on the tab
            if tab_id != "overview":  # Overview is already active
                page.click(f"text={tab_name}")
                time.sleep(1)  # Wait for tab to load

            # Take full page screenshot
            screenshot_path = f"{screenshot_dir}/{tab_id}_tab.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"  ✓ Screenshot saved: {screenshot_path}")

            # Check for specific elements
            if tab_id == "overview":
                # Check for OA visualization
                oa_chart = page.query_selector("#oa-status")
                if oa_chart:
                    print("  ✓ Open Access chart found")
                else:
                    print("  ✗ Open Access chart MISSING!")

                search_location = page.query_selector("#search-location")
                if search_location:
                    print("  ✓ Search Location chart found")
                else:
                    print("  ✗ Search Location chart MISSING!")

            elif tab_id == "temporal":
                timeline = page.query_selector("#timeline")
                if timeline:
                    print("  ✓ Timeline chart found")
                else:
                    print("  ✗ Timeline chart MISSING!")

            elif tab_id == "topics":
                topics_chart = page.query_selector("#topics-chart")
                themes_chart = page.query_selector("#themes-chart")
                if topics_chart and themes_chart:
                    print("  ✓ Both topic charts found")
                else:
                    print("  ✗ Topic charts MISSING!")

            # Get any console errors
            page.on("console", lambda msg: print(f"  Console: {msg.text}") if msg.type == "error" else None)

        # Check data in console
        print("\n\nChecking data integrity...")
        data_check = page.evaluate("""
            () => {
                const results = {};

                // Check if data object exists
                if (typeof data !== 'undefined') {
                    results.dataExists = true;
                    results.totalPapers = data.stats?.total_papers;
                    results.openAccess = data.stats?.open_access;
                    results.citations = data.stats?.total_citations;

                    // Check OA types
                    results.oaTypes = data.oa_types || {};

                    // Check search location
                    results.searchLocation = data.search_location || {};
                } else {
                    results.dataExists = false;
                }

                return results;
            }
        """)

        print(f"Data object exists: {data_check.get('dataExists')}")
        if data_check.get('dataExists'):
            print(f"Total papers: {data_check.get('totalPapers')}")
            print(f"Open Access: {data_check.get('openAccess')}")
            print(f"Citations: {data_check.get('citations')}")
            print(f"OA Types: {data_check.get('oaTypes')}")
            print(f"Search Location: {data_check.get('searchLocation')}")

        browser.close()
        print(f"\n✓ Inspection complete! Screenshots saved in {screenshot_dir}")

if __name__ == "__main__":
    inspect_dashboard()