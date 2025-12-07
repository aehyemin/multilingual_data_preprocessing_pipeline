from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re


def get_newest_talk_url(limit=30):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()   
        
        page.goto('https://www.ted.com/talks?sort=newest')
        page.wait_for_load_state("networkidle")
        card = page.locator("a[href^='/talks/']")
        cnt = card.count()
        urls = []
        
        for i in range(cnt):
            href = card.nth(i).get_attribute("href")
            if href:
                urls.append("https://www.ted.com" + href)
            if len(urls) >= limit:
                break
         
    return urls


def has_korean_transcript(page) -> bool:
    choose_lang = page.get_by_role("combobox")
    option = choose_lang.locator("option").all()
    
    for i in option:
        val = i.get_attribute("value")
        if val == "ko":
            return True
    return False
    
    
def extract_script(page, lang_label:str): #자막 추출
    page.wait_for_selector("div.mx-auto.mb-10.w-full div[role='button']", timeout=10000)
    container = page.locator("div.mx-auto.mb-10.w-full").first

    paragraph_divs = container.locator("div.w-full:has(div[role='button'])")
    count = paragraph_divs.count()
    print(f"{count}개")

    paragraphs = []

    for i in range(count):
        para = paragraph_divs.nth(i)
        script_text = para.locator(
            "div[role='button'] span.text-textPrimary-onLight.font-normal.text-tui-base.leading-tui-lg.tracking-tui-tight"
        ).all_text_contents()

        text = " ".join(t.strip() for t in script_text if t.strip())
        text = re.sub(r"\s+", " ", text).strip()

        if text:
            paragraphs.append(text)

    unique_paragraphs = []
    seen = set()
    for t in paragraphs:
        if t in seen:
            continue
        seen.add(t)
        unique_paragraphs.append(t)

    if unique_paragraphs:
        avg_len = sum(len(t) for t in unique_paragraphs) / len(unique_paragraphs)
        if len(unique_paragraphs[0]) > avg_len * 1.5:
            unique_paragraphs = unique_paragraphs[1:]

    return unique_paragraphs


def scrap_ted_script(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
    
        page.goto(f"{url}/transcript?language=en")
    
        try:
            btn = page.get_by_role("button", name="이 대화 상자 닫기")
            btn.click()
        except:
            pass

        if not has_korean_transcript(page):
            print("한국어 자막없음")
            return None
        
        en_script = extract_script(page, "EN")
        
        
        page.get_by_role("combobox").select_option("ko")
        ko_script = extract_script(page, "KO")
        
                

        min_len = min(len(ko_script), len(en_script))
        
        print(f"짧은쪽{min_len}")
        
        data = []
        for i in range(min_len):
            data.append(
                {
                    "idx": i,
                    "ko": ko_script[i],
                    "en": en_script[i]
                }
            )

        context.close()
        browser.close()
        
        return data

if __name__ == "__main__":
    urls = get_newest_talk_url(limit=30)

    data = []
    for u in urls:
        print(f"{u} 처리 중")
        data_list = scrap_ted_script(u)   
        if not data_list:
            continue
        data.extend(data_list)     

    if data:
        df = pd.DataFrame(data)
        df.to_csv("ted_parallel_blocks.csv", index=False, encoding="utf-8-sig")
        print(f" {len(df)}개")
        print(df.head())
    else:
        print("\n 실패.")
        
    
    