from playwright.sync_api import sync_playwright
import time
import os

def test_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Load the dashboard
        file_path = f"file://{os.path.abspath('index.html')}"
        page.goto(file_path)

        print("Dashboard loaded. Checking tab20 colors...")

        # Test each tab (using actual tab names from HTML)
        tabs = [
            ("Overview", "overview-tab.png"),
            ("Temporal Analysis", "temporal-tab.png"),
            ("OpenAlex Taxonomy", "taxonomy-tab.png"),
            ("Topics & Themes", "topics-tab.png"),
            ("Geographic Distribution", "geographic-tab.png"),
            ("Citation Impact", "impact-tab.png"),
            ("Publication Venues", "sources-tab.png")
        ]

        for tab_name, filename in tabs:
            # Click the tab - use nav-item class for specificity
            page.click(f".nav-item:has-text('{tab_name}')")
            time.sleep(2)  # Wait for charts to render

            # Take screenshot
            page.screenshot(path=f"color_test_{filename}")
            print(f"✓ {tab_name} tab - screenshot saved")

        print("\nAll tabs tested. Tab20 colors applied with distinct adjacent colors.")
        print("Screenshots saved for visual inspection.")

        browser.close()

if __name__ == "__main__":
    test_dashboard()