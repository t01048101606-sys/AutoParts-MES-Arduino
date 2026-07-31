# Chapter 0. Streamlit 개발 환경 설치

---

# 학습 목표

이번 장에서는 Streamlit 개발을 위한 기본 환경을 설치하고, 첫 번째 데모 앱을 실행해 본다.

이번 장을 마치면 다음을 할 수 있다.

- Python 설치 여부를 확인할 수 있다.
- 가상환경을 생성할 수 있다.
- Streamlit을 설치할 수 있다.
- Streamlit 데모 앱을 실행할 수 있다.
- `streamlit run app.py` 명령으로 웹 앱을 실행할 수 있다.

---

# 1. Streamlit 개발에 필요한 것

Streamlit 개발을 위해 기본적으로 필요한 것은 다음과 같다.

|항목|필수 여부|설명|
|----|----|----|
|Python|필수|Streamlit은 Python 기반 프레임워크이다.|
|pip|필수|Python 패키지 설치 도구이다.|
|venv|권장|프로젝트별 독립 환경을 만들기 위해 사용한다.|
|VS Code|권장|Python 코드 작성용 편집기이다.|
|Node.js|불필요|일반적인 Streamlit 개발에는 필요하지 않다.|

---

# 2. Node.js를 설치해야 하는가?

일반적인 Streamlit 개발에서는 **Node.js가 필요하지 않다.**

Streamlit은 Python 코드만으로 웹 화면을 만들 수 있는 프레임워크이다.

따라서 이번 강의에서는 Node.js를 설치하지 않는다.

Node.js가 필요한 경우는 다음과 같은 특수한 경우이다.

- Streamlit Custom Component를 직접 개발하는 경우
- React 기반 프론트엔드 컴포넌트를 직접 만드는 경우
- 별도의 JavaScript 프론트엔드와 연동하는 경우

이번 강의의 목표는 다음과 같다.

```text
Python

↓

Streamlit

↓

웹 화면
```

따라서 Python 환경만 준비하면 된다.

---

# 3. Python 설치 확인

터미널 또는 명령 프롬프트를 열고 다음 명령어를 실행한다.

## Windows

```bash
python --version
```

또는

```bash
py --version
```

## macOS / Ubuntu

```bash
python3 --version
```

정상적으로 설치되어 있다면 다음과 비슷하게 출력된다.

```text
Python 3.12.x
```

---

# 4. pip 설치 확인

pip는 Python 패키지를 설치하는 도구이다.

## Windows

```bash
pip --version
```

또는

```bash
py -m pip --version
```

## macOS / Ubuntu

```bash
python3 -m pip --version
```

정상 출력 예시는 다음과 같다.

```text
pip 24.x from ...
```
## pip가 없다면
```bash
sudo apt install python3-pip
```

---

# 5. 프로젝트 폴더 만들기

이번 강의에서는 다음과 같은 폴더를 사용한다.

```text
streamlit/
```

## Windows

```bash
mkdir streamlit
cd streamlit
```

## macOS / Ubuntu

```bash
mkdir streamlit
cd streamlit
```

---

# 6. 가상환경 만들기

가상환경은 프로젝트별로 Python 패키지를 독립적으로 관리하기 위한 공간이다.

가상환경을 사용하면 다른 프로젝트와 라이브러리 충돌을 줄일 수 있다.

---

## Windows

```bash
python -m venv [가상환경 이름]
```

또는

```bash
py -m venv [가상환경 이름]
```

가상환경 활성화

```bash
./[가상환경 이름]/Scripts/activate
```

정상적으로 활성화되면 터미널 앞에 다음과 같이 표시된다.

```text
(가상환경 이름)
```

---

## macOS / Ubuntu
가상환경 venv 모듈이 없다면
```bash
sudo apt install python3-venv
```
가상환경 설치

```bash
python3 -m venv virtual
```

가상환경 활성화

```bash
source virtual/bin/activate
```

정상적으로 활성화되면 터미널 앞에 다음과 같이 표시된다.

```text
(virtual)
```

가상환경 종료
```bash
deactivate
```
---

# 7. Streamlit 설치

가상환경이 활성화된 상태에서 다음 명령어를 실행한다.

```bash
pip install streamlit
```

설치가 끝나면 버전을 확인한다.

```bash
streamlit --version
```

정상 출력 예시는 다음과 같다.

```text
Streamlit, version 1.xx.x
```

---

# 8. Streamlit 데모 실행

Streamlit이 정상 설치되었는지 확인하기 위해 데모 앱을 실행한다.

```bash
streamlit hello
```

브라우저가 열리면서 Streamlit 예제 화면이 나타난다.

보통 다음 주소로 실행된다.

```text
http://localhost:8501
```

---

# 9. 첫 번째 app.py 만들기

프로젝트 폴더에 다음 파일을 만든다.

```text
app.py
```

파일 내용은 다음과 같다.

```python
import streamlit as st

st.title("Hello Streamlit")

st.write("Streamlit 설치가 완료되었습니다.")
```

---

# 10. app.py 실행하기

터미널에서 다음 명령어를 실행한다.

```bash
streamlit run app.py
```

브라우저에서 다음과 같은 화면이 나타난다.

```text
Hello Streamlit

Streamlit 설치가 완료되었습니다.
```

---

# 11. 프로젝트 기본 구조

앞으로 강의에서 사용할 기본 구조는 다음과 같다.

```text
streamlit/

├── app.py
├── pages/
├── data/
├── db/
├── images/
├── source/
├── [가상환경 폴더]/
└── requirements.txt
```

---

## 폴더 설명

|폴더/파일|설명|
|---------|----|
|app.py|Streamlit 메인 실행 파일|
|pages/|멀티 페이지 파일 저장|
|data/|CSV, Excel 등 데이터 파일 저장|
|db/|SQLite 데이터베이스 파일 저장|
|images/|실행 화면 캡처 이미지 저장|
|source/|챕터별 예제 코드 저장|
|[가상환경폴더]/|Python 가상환경|
|requirements.txt|필요한 Python 패키지 목록|

---

# 12. requirements.txt 만들기

현재 프로젝트에서 사용하는 패키지 목록을 저장한다.

```bash
pip freeze > requirements.txt
```

생성된 파일 예시는 다음과 같다.

```text
streamlit==1.xx.x
pandas==x.x.x
```

다른 컴퓨터에서 같은 환경을 만들 때는 다음 명령어를 사용한다.

```bash
pip install -r requirements.txt
```

---

# 13. 자주 발생하는 오류

## 오류 1. streamlit 명령어를 찾을 수 없음

```text
streamlit: command not found
```

또는

```text
'streamlit'은 내부 또는 외부 명령이 아닙니다.
```

해결 방법

```bash
pip install streamlit
```

또는 가상환경이 활성화되어 있는지 확인한다.

```bash
[가상환경 폴더]\Scripts\activate
```

또는

```bash
source [가상환경 폴더]/bin/activate
```

---

## 오류 2. pip 명령어가 동작하지 않음

해결 방법

Windows

```bash
py -m pip install streamlit
```

macOS / Ubuntu

```bash
python3 -m pip install streamlit
```

---

## 오류 3. 포트가 이미 사용 중인 경우

기본 포트는 8501이다.

다른 포트로 실행하려면 다음과 같이 입력한다.

```bash
streamlit run app.py --server.port 8502
```

---

## 오류 4. 브라우저가 자동으로 열리지 않는 경우

터미널에 출력된 주소를 직접 브라우저에 입력한다.

```text
http://localhost:8501
```

---

# 14. 실습 1. 설치 확인

다음 명령어를 순서대로 실행해 보자.

```bash
python --version
pip --version
streamlit --version
```

macOS / Ubuntu에서는 다음 명령어를 사용할 수 있다.

```bash
python3 --version
python3 -m pip --version
streamlit --version
```

---

# 15. 실습 2. 데모 앱 실행

```bash
streamlit hello
```

브라우저에서 Streamlit 데모 화면이 나타나는지 확인한다.

---

# 16. 실습 3. 첫 번째 웹 앱 실행

`app.py` 파일을 만들고 다음 코드를 작성한다.

```python
import streamlit as st

st.title("My First Streamlit App")

st.write("첫 번째 Streamlit 웹 앱입니다.")
```

실행한다.

```bash
streamlit run app.py
```

---

# 17. 실습 4. 개발 폴더 구성하기

다음 구조로 폴더를 만들어 보자.

```text
streamlit_course/

├── app.py
├── pages/
├── data/
├── db/
├── images/
└── source/
```

---

# 핵심 정리

✔ Streamlit은 Python 기반 웹 앱 프레임워크이다.

✔ 일반적인 Streamlit 개발에는 Node.js가 필요하지 않다.

✔ 프로젝트별 가상환경을 사용하는 것이 좋다.

✔ Streamlit 설치 명령어는 다음과 같다.

```bash
pip install streamlit
```

✔ Streamlit 데모 실행 명령어는 다음과 같다.

```bash
streamlit hello
```

✔ Streamlit 앱 실행 명령어는 다음과 같다.

```bash
streamlit run app.py
```

---

# 연습 문제

## 문제 1

Streamlit 개발에 필수적인 언어는 무엇인가?

---

## 문제 2

Streamlit 설치 명령어를 작성하시오.

---

## 문제 3

Streamlit 데모 앱을 실행하는 명령어를 작성하시오.

---

## 문제 4

`app.py` 파일을 실행하는 명령어를 작성하시오.

---

## 문제 5

일반적인 Streamlit 개발에서 Node.js가 필요하지 않은 이유를 설명하시오.

---

# Chapter 1. Streamlit 소개

---

# 학습 목표

이번 장에서는 Streamlit이 무엇인지 이해하고, 개발 환경을 구축한 후 첫 번째 웹 애플리케이션을 실행할 수 있다.

학습이 끝나면 다음과 같은 작업을 할 수 있다.

- Streamlit의 특징을 설명할 수 있다.
- Streamlit을 설치할 수 있다.
- Streamlit 프로젝트를 생성할 수 있다.
- 첫 번째 웹 페이지를 실행할 수 있다.

---

# 1. Streamlit이란?

Streamlit은 **Python만으로 웹 애플리케이션을 만들 수 있는 오픈소스 프레임워크**이다.

기존 웹 개발은 HTML, CSS, JavaScript를 함께 사용해야 했지만,
Streamlit은 Python 코드만으로 화면을 만들 수 있다.

대표적인 활용 분야는 다음과 같다.

- 데이터 분석 결과 시각화
- 머신러닝 모델 데모
- AI 챗봇
- 대시보드
- MES 모니터링 화면
- 생산 현황 조회 시스템
- 간단한 업무용 웹 프로그램

즉,

> **Python 개발자가 가장 빠르게 웹 서비스를 만들 수 있는 프레임워크**라고 생각하면 된다.

---

# 2. Streamlit의 특징

## 매우 적은 코드

다음 한 줄만으로 웹 화면을 만들 수 있다.

```python
import streamlit as st

st.title("Hello Streamlit")
```

실행하면 브라우저에서 바로 확인할 수 있다.

---

## HTML을 몰라도 된다.

기존 웹 개발

```
Python
↓

Flask

↓

HTML

↓

CSS

↓

JavaScript

↓

웹 브라우저
```

Streamlit

```
Python

↓

Streamlit

↓

웹 브라우저
```

복잡한 프론트엔드 개발 없이도
웹 화면을 만들 수 있다.

---

## 빠른 개발 속도

예를 들어

MES 생산현황

- 생산량
- 불량률
- 설비상태

를 보여주는 페이지를 만든다면

Flask는

- HTML 작성
- CSS 작성
- JavaScript 작성

등이 필요하지만

Streamlit은 Python 코드만 작성하면 된다.

---

## 데이터 분석 라이브러리와 궁합이 좋다.

대표적으로

- Pandas
- NumPy
- Matplotlib
- Plotly
- OpenCV
- Scikit-learn
- TensorFlow
- PyTorch

등과 매우 잘 연동된다.

---

# 3. 왜 Flask, Django 대신 Streamlit인가?

많은 학생들이 이런 질문을 한다.

> "웹 개발은 Flask나 Django를 배우는 것이 아닌가요?"

물론 그렇다.

하지만 목적이 다르다.

|항목|Streamlit|Flask|Django|
|----|---------|------|-------|
|난이도|★★★★★ 쉬움|중간|어려움|
|HTML 필요|거의 없음|필요|필요|
|JavaScript|거의 없음|필요|필요|
|개발 속도|매우 빠름|보통|느림|
|AI 프로젝트|매우 적합|적합|적합|
|대규모 서비스|부적합|가능|매우 적합|

---

## Streamlit이 적합한 경우

- AI 데모
- 데이터 분석
- 강의 실습
- MES 시연
- 관리자 페이지
- 사내 업무 프로그램

---

## Flask가 적합한 경우

- REST API
- 웹 백엔드
- React와 연동

---

## Django가 적합한 경우

- 쇼핑몰
- 회원관리
- 게시판
- 기업용 웹서비스

---

# 4. 설치

먼저 Python이 설치되어 있어야 한다.

버전을 확인한다.

```bash
python --version
```

또는

```bash
python3 --version
```

---

## pip 확인

```bash
pip --version
```

---

## Streamlit 설치

```bash
pip install streamlit
```

설치가 완료되면

```bash
streamlit --version
```

으로 정상 설치 여부를 확인할 수 있다.

예)

```
Streamlit, version 1.xx.x
```

---

# 5. 첫 번째 프로젝트

새 폴더를 만든다.

```
streamlit_basic/
```

그 안에

```
app.py
```

파일을 만든다.

다음 코드를 입력한다.

```python
import streamlit as st

st.title("Hello Streamlit!")

st.write("첫 번째 Streamlit 프로그램입니다.")
```

---

# 6. 실행 방법

터미널에서

```bash
streamlit run app.py
```

를 실행한다.

예시

```bash
cd streamlit_basic

streamlit run app.py
```

그러면 자동으로 브라우저가 실행된다.

주소는 보통 다음과 같다.

```
http://localhost:8501
```

브라우저를 열면

```
Hello Streamlit!

첫 번째 Streamlit 프로그램입니다.
```

가 출력된다.

---

# 7. 프로젝트 구조

보통 다음과 같이 구성한다.

```
project/

│
├── app.py
│
├── pages/
│
├── data/
│
├── db/
│
├── images/
│
├── utils/
│
└── requirements.txt
```

---

## app.py

프로그램의 시작 파일

```
웹이 시작되는 메인 페이지
```

---

## pages/

멀티 페이지를 저장한다.

예)

```
pages/

01_dashboard.py

02_customer.py

03_inventory.py
```

---

## data/

CSV

Excel

JSON

등 데이터를 저장한다.

예)

```
sales.csv

employees.csv

product.xlsx
```

---

## db/

SQLite 데이터베이스 등을 저장한다.

예)

```
factory.db

mes.db
```

---

## images/

이미지 파일

```
logo.png

factory.jpg
```

---

## utils/

공통 함수

예)

```
db.py

chart.py

config.py
```

---

## requirements.txt

필요한 라이브러리를 기록한다.

예)

```
streamlit
pandas
plotly
openpyxl
sqlite3
```

실제 프로젝트에서는

```bash
pip freeze > requirements.txt
```

명령으로 생성하는 경우가 많다.

---

# 실습 1

새 프로젝트를 만든다.

```
streamlit_basic
```

생성 후

```
app.py
```

를 만든다.

다음 코드를 입력한다.

```python
import streamlit as st

st.title("My First Streamlit")

st.write("안녕하세요.")
```

실행한다.

```bash
streamlit run app.py
```

---

# 실습 2

다음 내용을 출력하도록 수정해 보자.

```
스마트팩토리 MES

현재 생산량

오늘 불량률

설비 가동률
```

힌트

```python
st.title()

st.header()

st.write()
```

---

# 실습 3

프로젝트를 다음과 같이 구성해 보자.

```
mes_project/

app.py

pages/

data/

db/

images/

utils/
```

---

# 핵심 정리

✔ Streamlit은 Python만으로 웹을 만들 수 있는 프레임워크이다.

✔ HTML, CSS, JavaScript를 거의 작성하지 않아도 된다.

✔ 데이터 분석과 AI 프로젝트에 매우 적합하다.

✔ 실행 명령은 다음과 같다.

```bash
streamlit run app.py
```

✔ 기본 프로젝트 구조는 다음과 같다.

```
project/

app.py

pages/

data/

db/

images/

utils/
```

---

# 연습 문제

## 문제 1

Streamlit의 가장 큰 장점은 무엇인가?

---

## 문제 2

Streamlit을 실행하는 명령어를 작성하시오.

---

## 문제 3

프로젝트에서 여러 화면을 저장하는 폴더 이름은?

---

## 문제 4

SQLite 데이터베이스 파일은 일반적으로 어느 폴더에 저장하는가?

---

## 문제 5

Flask와 Streamlit의 가장 큰 차이점을 설명하시오.

# Chapter 2. 첫 번째 웹 만들기

---

# 학습 목표

이번 장에서는 Streamlit에서 가장 많이 사용하는 출력 함수를 익히고,
Python 코드만으로 간단한 웹 페이지를 만드는 방법을 학습한다.

학습이 끝나면 다음과 같은 작업을 할 수 있다.

- 제목과 부제목을 출력할 수 있다.
- 일반 텍스트를 출력할 수 있다.
- Markdown 문법을 사용할 수 있다.
- 코드 블록을 출력할 수 있다.
- 캡션을 작성할 수 있다.
- 간단한 회사 소개 페이지를 만들 수 있다.

---

# 1. Streamlit 출력 함수

웹 페이지는 결국 **사용자에게 정보를 보여주는 화면**이다.

Streamlit은 다양한 출력 함수를 제공한다.

이번 장에서 배울 함수는 다음과 같다.

|함수|설명|
|----|----|
|st.title()|가장 큰 제목|
|st.header()|중간 제목|
|st.subheader()|작은 제목|
|st.write()|일반 텍스트 및 객체 출력|
|st.markdown()|Markdown 문법 출력|
|st.code()|소스 코드 출력|
|st.caption()|작은 설명(캡션) 출력|

---

# 2. st.title()

가장 큰 제목을 출력한다.

웹 사이트의 메인 제목에 사용한다.

```python
import streamlit as st

st.title("스마트팩토리 MES")
```

실행 결과

```
스마트팩토리 MES
================
```

---

## 여러 개 작성 가능

```python
st.title("회사 소개")

st.title("제품 소개")
```

하지만 일반적으로 **페이지에는 하나의 title만 사용하는 것이 좋다.**

---

# 3. st.header()

중간 크기의 제목을 출력한다.

주제별 구분에 많이 사용한다.

```python
import streamlit as st

st.header("회사 소개")
```

---

## 예제

```python
st.title("ABC Company")

st.header("회사소개")

st.header("주요사업")

st.header("오시는 길")
```

---

# 4. st.subheader()

Header보다 작은 제목이다.

세부 항목을 구분할 때 사용한다.

```python
st.subheader("AI 사업부")
```

---

## 예제

```python
st.header("사업 분야")

st.subheader("AI")

st.subheader("스마트팩토리")

st.subheader("클라우드")
```

---

# 5. st.write()

가장 많이 사용하는 함수이다.

문자열은 물론 숫자, 리스트, DataFrame 등도 출력할 수 있다.

```python
st.write("안녕하세요.")
```

---

## 여러 줄 출력

```python
st.write("회사명 : ABC")

st.write("대표 : 홍길동")

st.write("설립 : 2020")
```

---

## 숫자 출력

```python
sales = 3500

st.write(sales)
```

---

## 리스트 출력

```python
items = ["PLC", "MES", "SCADA"]

st.write(items)
```

---

# 6. st.markdown()

Markdown 문법을 사용할 수 있다.

GitHub에서 사용하는 Markdown과 거의 동일하다.

```python
st.markdown("# 제목")
```

---

## 굵은 글씨

```python
st.markdown("**스마트팩토리**")
```

결과

**스마트팩토리**

---

## 기울임

```python
st.markdown("*Python*")
```

---

## 목록

```python
st.markdown("""
- MES
- SCADA
- ERP
""")
```

---

## 번호 목록

```python
st.markdown("""
1. 생산관리
2. 품질관리
3. 설비관리
""")
```

---

## 인용문

```python
st.markdown("> Streamlit은 매우 빠른 웹 개발 도구입니다.")
```

---

## 수평선

```python
st.markdown("---")
```

---

# 7. st.code()

소스 코드를 보기 좋게 출력한다.

```python
code = '''
for i in range(5):
    print(i)
'''

st.code(code)
```

---

## 언어 지정

```python
st.code(code, language="python")
```

---

## SQL 출력

```python
sql = '''
SELECT *
FROM customers;
'''

st.code(sql, language="sql")
```

---

# 8. st.caption()

작은 설명을 출력한다.

보통 이미지 설명이나 참고 문헌 등에 사용한다.

```python
st.caption("Version 1.0")
```

---

## 예제

```python
st.caption("Copyright © 2026 ABC Company")
```

---

# 출력 함수 비교

|함수|크기|용도|
|----|----|----|
|title|★★★★★|메인 제목|
|header|★★★★|큰 항목|
|subheader|★★★|세부 항목|
|write|★★|일반 내용|
|markdown|다양|Markdown 출력|
|code|코드|소스 코드|
|caption|작음|설명|

---

# 실습 1

다음 화면을 만들어 보자.

```python
import streamlit as st

st.title("스마트팩토리")

st.header("MES")

st.subheader("생산관리")

st.write("MES는 Manufacturing Execution System입니다.")

st.caption("Version 1.0")
```

---

# 실습 2

다음 Markdown을 출력해 보자.

```python
st.markdown("""
# Python

## Streamlit

- AI
- Dashboard
- MES

**Python Web**
""")
```

---

# 실습 3

다음 Python 코드를 출력해 보자.

```python
code = '''
for i in range(10):
    print(i)
'''

st.code(code, language="python")
```

---

# 실습 4

SQL 문장을 출력해 보자.

```python
sql = '''
SELECT *
FROM employee
WHERE dept='AI';
'''

st.code(sql, language="sql")
```

---

# 종합 실습 : 회사 소개 페이지 만들기

이번 장에서 배운 함수만 사용하여 회사 소개 페이지를 만들어 보자.

파일 이름

```
app.py
```

소스 코드

```python
import streamlit as st

st.title("Vertha Systems")

st.caption("AI · Smart Factory · Software Development")

st.markdown("---")

st.header("회사 소개")

st.write("""
Vertha Systems는 AI와 스마트팩토리 기술을 기반으로
기업의 디지털 전환(DX)과 AI 전환(AX)을 지원하는
소프트웨어 전문 기업입니다.
""")

st.header("주요 사업")

st.markdown("""
- AI 솔루션 개발
- 스마트팩토리 구축
- MES 개발
- 데이터 분석
- Python 교육
- 소프트웨어 컨설팅
""")

st.header("핵심 기술")

st.markdown("""
- Python
- Streamlit
- FastAPI
- SQLite
- PostgreSQL
- Pandas
- OpenCV
- AI Agent
""")

st.header("예제 코드")

code = '''
def hello():
    print("Welcome Vertha Systems")
'''

st.code(code, language="python")

st.header("연락처")

st.write("Email : contact@verthasys.co.kr")

st.caption("Copyright © 2026 Vertha Systems")
```

---

# 도전 실습

다음 항목을 추가하여 회사 소개 페이지를 완성해 보자.

- 회사 연혁
- 조직도
- 대표 인사말
- 서비스 소개
- 교육 과정
- 개발 기술
- 고객사
- 찾아오는 길
- 버전 정보

---

# 핵심 정리

✔ **st.title()**은 페이지의 가장 큰 제목을 출력한다.

✔ **st.header()**는 큰 항목을 구분한다.

✔ **st.subheader()**는 세부 항목을 구분한다.

✔ **st.write()**는 가장 많이 사용하는 출력 함수이며 문자열, 숫자, 리스트 등 다양한 객체를 출력할 수 있다.

✔ **st.markdown()**은 GitHub Markdown 문법을 그대로 사용할 수 있다.

✔ **st.code()**는 소스 코드를 보기 좋게 출력한다.

✔ **st.caption()**은 작은 설명이나 버전 정보를 출력할 때 사용한다.

---

# 연습 문제

## 문제 1

페이지의 가장 큰 제목을 출력하는 함수는 무엇인가?

---

## 문제 2

Markdown 문법을 출력하는 함수는 무엇인가?

---

## 문제 3

Python 코드를 보기 좋게 출력하는 함수는 무엇인가?

---

## 문제 4

다음과 같은 화면을 만들어 보시오.

```
회사 소개

사업 분야

AI

Python으로 개발합니다.
```

---

## 문제 5

오늘 배운 함수만 이용하여 **자신의 회사 또는 가상의 IT 회사를 소개하는 웹 페이지**를 작성해 보시오.

# Chapter 3. 입력 컴포넌트(Input Components)

---

# 학습 목표

이번 장에서는 사용자가 웹 페이지에 데이터를 입력할 수 있도록 하는 **입력 컴포넌트(Input Widget)** 를 학습한다.

이번 장을 마치면 다음과 같은 프로그램을 만들 수 있다.

- 직원 등록 화면
- 회원 가입 화면
- 제품 등록 화면
- 고객 정보 입력 화면
- 생산 정보 입력 화면

이번 장에서 학습할 컴포넌트는 다음과 같다.

- `st.text_input()`
- `st.number_input()`
- `st.date_input()`
- `st.checkbox()`
- `st.radio()`
- `st.selectbox()`
- `st.multiselect()`
- `st.slider()`

---

# 1. 입력 컴포넌트란?

웹 프로그램은 단순히 정보를 출력하는 것만으로는 충분하지 않다.

사용자로부터 데이터를 입력받아야 한다.

예를 들어

- 로그인
- 회원가입
- 직원등록
- 주문등록
- 제품등록
- 생산실적 입력

모두 입력 컴포넌트를 사용한다.

Streamlit은 Python 코드만으로 이러한 입력 화면을 쉽게 만들 수 있다.

---

# 2. st.text_input()

문자열을 입력받는다.

가장 많이 사용하는 입력 컴포넌트이다.

```python
import streamlit as st

name = st.text_input("이름")

st.write(name)
```

실행 결과

```
이름

____________________
```

입력하면 즉시 화면에 출력된다.

---

## 기본값 지정

```python
name = st.text_input(
    "이름",
    value="홍길동"
)
```

---

## placeholder 사용

```python
name = st.text_input(
    "이름",
    placeholder="이름을 입력하세요."
)
```

---

# 3. st.number_input()

숫자를 입력받는다.

```python
age = st.number_input("나이")
```

---

## 최소값과 최대값

```python
age = st.number_input(
    "나이",
    min_value=20,
    max_value=60
)
```

---

## 증가 단위 지정

```python
salary = st.number_input(
    "연봉",
    step=100
)
```

---

# 4. st.date_input()

날짜를 입력받는다.

```python
birthday = st.date_input("입사일")
```

---

## 결과 출력

```python
st.write(birthday)
```

---

# 5. st.checkbox()

체크 여부를 선택한다.

```python
agree = st.checkbox("동의합니다.")
```

---

## 예제

```python
if agree:
    st.write("동의 완료")
else:
    st.write("동의하지 않음")
```

---

# 6. st.radio()

여러 개 중 하나를 선택한다.

```python
gender = st.radio(
    "성별",
    ["남성", "여성"]
)
```

---

## 예제

```python
st.write(gender)
```

---

# 7. st.selectbox()

드롭다운 메뉴이다.

```python
dept = st.selectbox(
    "부서",
    [
        "생산팀",
        "품질팀",
        "설비팀",
        "AI개발팀"
    ]
)
```

---

## 결과 출력

```python
st.write(dept)
```

---

# 8. st.multiselect()

여러 개를 선택할 수 있다.

```python
skills = st.multiselect(
    "보유 기술",
    [
        "Python",
        "C++",
        "SQL",
        "PLC",
        "ROS"
    ]
)
```

---

## 결과 출력

```python
st.write(skills)
```

---

# 9. st.slider()

범위를 선택한다.

```python
score = st.slider(
    "평가 점수",
    0,
    100
)
```

---

## 범위 지정

```python
experience = st.slider(
    "경력(년)",
    0,
    30,
    5
)
```

---

# 입력 컴포넌트 비교

|컴포넌트|용도|
|---------|----|
|text_input|문자 입력|
|number_input|숫자 입력|
|date_input|날짜 입력|
|checkbox|체크 여부|
|radio|한 개 선택|
|selectbox|드롭다운 선택|
|multiselect|여러 개 선택|
|slider|범위 선택|

---

# 실습 1

간단한 회원 정보를 입력받아 출력해 보자.

```python
import streamlit as st

name = st.text_input("이름")

age = st.number_input(
    "나이",
    min_value=20,
    max_value=70
)

st.write(name)
st.write(age)
```

---

# 실습 2

부서를 선택해 보자.

```python
dept = st.selectbox(
    "부서",
    [
        "생산",
        "품질",
        "설비",
        "영업"
    ]
)

st.write(dept)
```

---

# 실습 3

보유 기술을 선택해 보자.

```python
skills = st.multiselect(
    "보유 기술",
    [
        "Python",
        "SQL",
        "PLC",
        "AI",
        "Linux"
    ]
)

st.write(skills)
```

---

# 종합 실습 : 직원 등록 화면 만들기

이번 장에서 배운 입력 컴포넌트를 이용하여 직원 등록 화면을 만들어 보자.

파일 이름

```
app.py
```

```python
import streamlit as st

st.title("직원 등록")

st.markdown("---")

emp_name = st.text_input(
    "직원 이름",
    placeholder="이름을 입력하세요."
)

emp_no = st.number_input(
    "사번",
    min_value=1000,
    step=1
)

hire_date = st.date_input("입사일")

gender = st.radio(
    "성별",
    [
        "남성",
        "여성"
    ]
)

department = st.selectbox(
    "부서",
    [
        "생산팀",
        "품질팀",
        "설비팀",
        "AI개발팀",
        "경영지원팀"
    ]
)

skills = st.multiselect(
    "보유 기술",
    [
        "Python",
        "SQL",
        "PLC",
        "OpenCV",
        "ROS",
        "Linux"
    ]
)

career = st.slider(
    "경력(년)",
    0,
    30,
    1
)

is_active = st.checkbox(
    "현재 재직 중"
)

st.markdown("---")

st.header("입력 결과")

st.write("직원명 :", emp_name)
st.write("사번 :", emp_no)
st.write("입사일 :", hire_date)
st.write("성별 :", gender)
st.write("부서 :", department)
st.write("보유기술 :", skills)
st.write("경력 :", career)
st.write("재직여부 :", is_active)
```

---

# 도전 실습 1

직원 등록 화면에 다음 항목을 추가해 보자.

- 이메일
- 전화번호
- 주소
- 직급
- 연봉

---

# 도전 실습 2

다음 화면을 만들어 보자.

```
제품 등록 화면

제품명

제품번호

생산일

제품 종류

사용 가능한 설비

품질 등급

재고 여부
```

---

# 도전 실습 3

고객 등록 화면을 만들어 보자.

입력 항목

- 고객명
- 전화번호
- 주소
- 거래 시작일
- 거래 상태
- 구매 제품
- 거래 등급

---

# 핵심 정리

✔ `st.text_input()`은 문자열을 입력받는다.

✔ `st.number_input()`은 숫자를 입력받는다.

✔ `st.date_input()`은 날짜를 선택한다.

✔ `st.checkbox()`는 참(True) 또는 거짓(False)을 선택한다.

✔ `st.radio()`는 여러 항목 중 하나를 선택한다.

✔ `st.selectbox()`는 드롭다운 목록을 제공한다.

✔ `st.multiselect()`는 여러 항목을 동시에 선택할 수 있다.

✔ `st.slider()`는 일정 범위의 값을 선택할 때 사용한다.

---

# 연습 문제

## 문제 1

직원 이름을 입력받는 입력창을 작성하시오.

---

## 문제 2

20~60세 사이의 나이를 입력받는 숫자 입력창을 작성하시오.

---

## 문제 3

생산팀, 품질팀, 설비팀 중 하나를 선택하는 드롭다운을 작성하시오.

---

## 문제 4

Python, SQL, PLC를 여러 개 선택할 수 있는 입력 컴포넌트를 작성하시오.

---

## 문제 5

오늘 배운 모든 입력 컴포넌트를 이용하여 **직원 등록 화면** 또는 **회원 가입 화면**을 작성해 보시오.

---

# 다음 장 예고

다음 장에서는 **버튼과 이벤트 처리**를 학습한다.

학습 내용

- `st.button()`
- `st.form()`
- `st.form_submit_button()`
- 입력 데이터 검증
- 등록 버튼 구현
- 초기화 버튼 구현
- 간단한 CRUD 화면 만들기

이를 통해 입력받은 데이터를 실제 프로그램처럼 처리하는 방법을 익히게 된다.

# Chapter 4. 버튼과 이벤트(Button & Event)

---

# 학습 목표

이번 장에서는 **버튼(Button)** 과 **이벤트(Event)** 의 개념을 이해하고,
사용자의 입력을 처리하는 방법을 학습한다.

이번 장을 마치면 다음과 같은 프로그램을 만들 수 있다.

- 로그인 화면
- 회원 가입 화면
- 직원 등록 화면
- 제품 등록 화면
- 데이터 저장 버튼 구현

이번 장에서 학습할 내용

- `st.button()`
- `st.form()`
- `st.form_submit_button()`

---

# 1. 이벤트(Event)란?

웹 프로그램은 사용자의 행동에 따라 동작한다.

예를 들어

- 버튼 클릭
- 로그인
- 검색
- 저장
- 삭제
- 수정

모두 이벤트(Event)이다.

예를 들어 로그인 화면에서는

```
아이디 입력

↓

비밀번호 입력

↓

로그인 버튼 클릭

↓

로그인 처리
```

이러한 흐름으로 프로그램이 동작한다.

---

# 2. st.button()

가장 많이 사용하는 버튼이다.

버튼을 누르면 **True**를 반환한다.

```python
import streamlit as st

if st.button("클릭"):
    st.write("버튼이 눌렸습니다.")
```

실행 화면

```
[ 클릭 ]
```

버튼을 누르는 순간

```
버튼이 눌렸습니다.
```

가 출력된다.

---

## 버튼 반환값

```python
result = st.button("저장")

st.write(result)
```

버튼을 누르기 전

```
False
```

버튼을 누른 순간

```
True
```

---

# 3. 버튼과 입력창 함께 사용하기

```python
import streamlit as st

name = st.text_input("이름")

if st.button("확인"):
    st.write("입력한 이름 :", name)
```

실행 순서

```
이름 입력

↓

확인 버튼 클릭

↓

결과 출력
```

---

# 4. 여러 개의 버튼

```python
if st.button("등록"):
    st.write("등록")

if st.button("삭제"):
    st.write("삭제")

if st.button("수정"):
    st.write("수정")
```

실행 화면

```
[등록]

[삭제]

[수정]
```

---

# 5. st.form()

입력 컴포넌트를 하나의 그룹으로 묶는다.

실무에서는 매우 많이 사용하는 기능이다.

```python
import streamlit as st

with st.form("employee"):

    name = st.text_input("이름")

    age = st.number_input("나이")

    submit = st.form_submit_button("등록")
```

---

## Form을 사용하는 이유

Form을 사용하지 않으면

텍스트를 한 글자 입력할 때마다

Streamlit이 프로그램을 다시 실행한다.

예를 들어

```
홍

↓

홍길

↓

홍길동
```

입력할 때마다

프로그램이 다시 실행된다.

---

Form을 사용하면

```
입력 완료

↓

등록 버튼 클릭

↓

한 번만 실행
```

된다.

따라서

회원가입

직원등록

제품등록

로그인

등에서는 Form 사용을 권장한다.

---

# 6. st.form_submit_button()

Form 내부에서 사용하는 버튼이다.

```python
with st.form("member"):

    name = st.text_input("이름")

    submit = st.form_submit_button("가입")
```

---

## 결과 출력

```python
if submit:
    st.write(name)
```

---

# 7. 버튼과 Form의 차이

## 일반 버튼

```python
st.button("저장")
```

- 간단한 기능
- 조회 버튼
- 새로고침

등에 적합하다.

---

## Form

```python
with st.form():

    ...

    st.form_submit_button()
```

- 회원가입

- 로그인

- 직원등록

- 제품등록

- 주문등록

등 여러 입력을 한 번에 처리할 때 사용한다.

---

# Button와 Form 비교

|항목|Button|Form|
|----|------|----|
|사용 목적|간단한 이벤트|입력 데이터 처리|
|입력 그룹|불가능|가능|
|실무 사용 빈도|높음|매우 높음|
|회원가입|△|◎|
|로그인|△|◎|
|등록 화면|△|◎|

---

# 실습 1

버튼 클릭

```python
import streamlit as st

st.title("버튼 예제")

if st.button("클릭"):
    st.write("안녕하세요.")
```

---

# 실습 2

입력 후 버튼 클릭

```python
import streamlit as st

name = st.text_input("이름")

if st.button("확인"):
    st.success(name)
```

---

# 실습 3

Form 만들기

```python
import streamlit as st

with st.form("employee"):

    name = st.text_input("이름")

    age = st.number_input("나이")

    submit = st.form_submit_button("등록")

if submit:

    st.write(name)

    st.write(age)
```

---

# 종합 실습 : 로그인 화면 만들기

파일명

```
app.py
```

```python
import streamlit as st

st.title("MES 로그인")

st.markdown("---")

with st.form("login"):

    user_id = st.text_input(
        "아이디"
    )

    password = st.text_input(
        "비밀번호",
        type="password"
    )

    login = st.form_submit_button(
        "로그인"
    )

if login:

    if user_id == "admin" and password == "1234":

        st.success("로그인 성공")

    else:

        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
```

---

# 도전 실습 1

로그인 화면에 다음 항목을 추가해 보자.

- 로그인 유지

- 관리자 로그인

- 비밀번호 표시 여부

힌트

```
checkbox
```

---

# 도전 실습 2

회원 가입 화면을 만들어 보자.

입력 항목

- 아이디

- 비밀번호

- 이름

- 이메일

- 전화번호

- 가입 버튼

---

# 도전 실습 3

직원 등록 화면을 만들어 보자.

입력 항목

- 사번

- 이름

- 부서

- 입사일

- 등록 버튼

등록이 완료되면

```
등록되었습니다.
```

메시지를 출력하도록 작성해 보자.

---

# 핵심 정리

✔ `st.button()`은 가장 기본적인 버튼이다.

✔ 버튼을 클릭하면 `True`를 반환한다.

✔ `st.form()`은 여러 입력 컴포넌트를 하나의 그룹으로 묶는다.

✔ `st.form_submit_button()`은 Form 내부에서 사용하는 제출 버튼이다.

✔ 로그인, 회원가입, 직원등록과 같은 화면은 `Form`을 사용하는 것이 권장된다.

---

# 연습 문제

## 문제 1

버튼을 클릭하면 "Hello Streamlit"을 출력하는 프로그램을 작성하시오.

---

## 문제 2

이름을 입력받은 후 버튼을 누르면 이름을 출력하는 프로그램을 작성하시오.

---

## 문제 3

`st.form()`을 사용하는 이유를 설명하시오.

---

## 문제 4

아이디와 비밀번호를 입력받는 로그인 화면을 작성하시오.

---

## 문제 5

오늘 배운 내용을 이용하여 **회원가입 화면**, **직원 등록 화면**, 또는 **제품 등록 화면** 중 하나를 구현해 보시오.

---

# 실무 TIP

실제 업무에서는 로그인 버튼을 눌렀을 때 아이디와 비밀번호를 코드에 직접 비교하지 않는다.

일반적으로 다음과 같은 흐름으로 로그인 기능을 구현한다.

```
사용자 입력

↓

로그인 버튼 클릭

↓

SQLite 또는 PostgreSQL 조회

↓

사용자 존재 여부 확인

↓

로그인 성공 또는 실패
```

다음 장부터는 **SQLite 데이터베이스와 연동하여 로그인, 회원 관리, 직원 관리 등 실제 CRUD(Create, Read, Update, Delete) 프로그램을 구현**해 본다.
