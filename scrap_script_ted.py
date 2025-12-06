from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re

def extract_script(page, lang_label:str): #자막 추출
    print(f"{lang_label} 자막 추출")
    
        
    page.wait_for_selector("div.mx-auto.mb-10.w-full div[role='button']", timeout=10000)

    transcript_block = page.locator("div.mx-auto.mb-10.w-full").first
    transcript_one_block = transcript_block.locator("div[role='button']")
    cnt = transcript_one_block.count()
    
    segments = []
    
    for i in range(cnt):
        block = transcript_one_block.nth(i)
        script_text = block.locator("span.text-textPrimary-onLight.font-normal.text-tui-base.leading-tui-lg.tracking-tui-tight").all_text_contents()
        text = ' '.join(t.strip() for t in script_text if t.strip())
        text = re.sub(r"\s+", " ", text).strip()
    
        if text:
            segments.append(text)

    return segments


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
        
        
        ko_script = extract_script(page, "KO")
        
                
        print("EN 페이지 접속")
        page.goto(f"{url}/transcript?language=en")
        time.sleep(1)
        page.get_by_role("combobox").select_option("en")


        en_script = extract_script(page, "EN")
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
    url = "https://www.ted.com/talks/jennifer_doudna_how_crispr_lets_us_edit_our_dna"
    data_list = scrap_ted_script(url)

    if data_list:
        df = pd.DataFrame(data_list)
        df.to_csv("ted_parallel_blocks.csv", index=False, encoding="utf-8-sig")
        print(f" {len(df)}개")
        print(df.head())
    else:
        print("\n 실패.")
