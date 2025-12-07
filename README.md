## TED 한–영 병렬 코퍼스 수집 및 정제

> TED 자막 페이지에서 한국어–영어 병렬 문장을 수집하고,  
> LLM / 번역 모델 학습에 사용할 수 있는 **병렬 코퍼스**로 정제하는 파이프라인입니다.

- 대상: TED 공식 사이트의 자막(Transcript)
- 언어: **한국어(`ko`) – 영어(`en`)**
- 출력: `CSV`, `JSONL` 병렬 코퍼스


### 기능 개요

#### 1. TED 자막 스크래핑

- Playwright 기반 브라우저 자동화를 통해 TED 자막 페이지에 접속
- 선택한 언어(한국어/영어) 자막을 **문단 단위**로 수집
- 동일한 문단에 대해 한국어–영어 문단을 정렬하여 병렬 데이터 생성
<br><br>
#### 2. 비의미 텍스트 및 노이즈 제거

다음과 같은 **모델 학습에 불필요한 텍스트**를 정규표현식 기반으로 제거

- `(Laughter)`, `(Applause)` 등 괄호 기반 메타 텍스트
- 연속 공백, 양쪽 공백, 특수문자 등
<br><br>
#### 3. 부모 문단(길이 이상치) 제거

TED 자막 구조상 전체 스크립트가 하나의 문단으로 뭉쳐 있는 **'부모 문단(Parent Node)'** 이 함께 수집되는 문제 발생

- 문단 길이의 분포(Distribution)를 분석하여, **평균 길이 대비 과도하게 긴 문단(3배 이상)** 을 이상치로 간주하고 자동으로 필터링
<br><br>
#### 4. 병렬 코퍼스 생성 및 저장

정제된 문단 단위 데이터를 다음 형식으로 저장

1. `clean_ted.csv`
   - 사람이 보기 쉬운 `CSV` 형식
2. `clean_ted.jsonl`
   - LLM 학습에 바로 활용할 수 있는 `JSON Lines` 형식

---


### **Before - 원본 데이터**
<div align="left">
  <img src="https://github.com/user-attachments/assets/5e7eae73-868a-496a-8a5a-534cdf973539" width="500"/>
</div>

<br><br>

### **After - 정제된 병렬 코퍼스**
<div align="left">
  <img src="https://github.com/user-attachments/assets/bbb42e77-2d4c-4d15-8a89-b428a1047e02" width="700"/>
</div>

---

### 기술 스택

- **언어**: Python
- **크롤링**: Playwright
- **데이터 처리**: pandas
- **기타**: re(정규표현식)



