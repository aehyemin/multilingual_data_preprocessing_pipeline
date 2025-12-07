import pandas as pd
import re
import json
INPUT_CSV = "ted_parallel_blocks.csv"
OUTPUT_CSV = "clean_ted.csv"
OUTPUT_JSONL = "clean_ted.jsonl"


def cleaning(text:str) -> str:
    if not isinstance(text, str):
        return ""
    
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def del_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=["ko", "en", "url"])
    after = len(df)
    print(f"중복제거 {before - after} 줄")
    return df


def del_parents(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cnt = 0
    
    for url, group in df.groupby("url"):
        group = group.copy()
        group["len_ko"] = group["ko"].apply(lambda x: len(x) if isinstance(x, str) else 0)

        if len(group) <= 1:
            rows.append(group)
            continue
        
        max_idx = group["len_ko"].idxmax()
        max_len = group.loc[max_idx, "len_ko"]
        avg_len = group["len_ko"].mean()
        
        if max_len > avg_len * 3:
            group = group.drop(index=max_idx)
            cnt += 1
        rows.append(group.drop(columns=["len_ko"]))
        
    result = pd.concat(rows, ignore_index=True)
    return result   


def main():
    df = pd.read_csv(INPUT_CSV)
    
    df["ko"] = df["ko"].apply(cleaning)
    df["en"] = df["en"].apply(cleaning)   
    
    df = del_duplicates(df)
    df = del_parents(df)
    
    df = df.reset_index(drop=True)
    df["idx"] = df.index      

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"최종 행 수: {len(df)}")

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            obj = {
                "ko": row["ko"], 
                "en": row["en"],
                "url": row["url"],
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()