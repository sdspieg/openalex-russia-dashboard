#!/usr/bin/env python3
"""
Capture screenshots of each slide in the landing page
"""

from playwright.sync_api import sync_playwright
import time

def capture_slides():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Navigate to the landing page
        page.goto("http://localhost:8089/landing_data_story.html")

        # Wait for page to load
        page.wait_for_selector('.slide')
        time.sleep(2)

        # Get total number of slides
        total_slides = page.evaluate("document.querySelectorAll('.slide').length")
        print(f"Found {total_slides} slides")

        # Capture each slide
        for i in range(total_slides):
            # Show the slide
            page.evaluate(f"goToSlide({i})")
            time.sleep(1)  # Wait for animation

            # Take screenshot
            filename = f"slide_{i+1:02d}.png"
            page.screenshot(path=filename, full_page=False)
            print(f"Captured {filename}")

        browser.close()
        print(f"\nAll {total_slides} slides captured successfully!")

if __name__ == "__main__":
    capture_slides()