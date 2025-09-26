from playwright.sync_api import sync_playwright
from conf import links
import os


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless=False → brauzer oynasi ochiladi
    page = browser.new_page()
    page.goto(links[0])

    # Masalan, h1 sarlavhalarni yig‘ish
    titles = page.query_selector_all("h1")
    for t in titles:
        print(t.inner_text())

    browser.close()
