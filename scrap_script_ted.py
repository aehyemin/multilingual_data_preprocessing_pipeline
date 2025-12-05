from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re


def scrap_ted_script(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"{url}/transcript?language=ko")

        try:
            btn = page.get_by_role("button", name="이 대화 상자 닫기")
            btn.click()
        except:
            pass

        context.close()
        browser.close()

if __name__ == "__main__":
    url = "https://www.ted.com/talks/jennifer_doudna_how_crispr_lets_us_edit_our_dna"
    data_list = scrap_ted_script(url)


