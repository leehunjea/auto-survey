# Naver Form Auto Survey 🤖

네이버 폼 설문조사 자동화 도구 - Selenium 기반 설문 자동 제출 프로그램

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 주요 기능

- ✅ **자동 설문 제출**: 네이버 폼 설문을 자동으로 작성 및 제출
- 🎲 **가중치 기반 랜덤 응답**: 각 질문별 옵션 선택 비율 설정 가능
- 🔄 **무한 반복 모드**: '설문 추가 참여' 버튼 자동 클릭으로 연속 제출
- 📊 **실시간 통계**: 진행 상황 및 성공률 실시간 표시
- ⚡ **최적화된 성능**: 불필요한 대기 시간 최소화

## 🎯 사용 사례

- 설문조사 데이터 수집을 위한 자동화
- 다양한 응답 패턴 시뮬레이션
- 설문 시스템 테스트

## 🚀 시작하기

### 필요 환경

- Python 3.8 이상
- Chrome 브라우저

### 설치

1. 저장소 클론
git clone https://github.com/yourusername/auto-survey.git
cd naver-form-auto-surve

2. 필요한 패키지 설치
pip install -r requirements.txt

### 사용 방법

1. `survey_bot.py` 파일에서 설문 URL 설정
survey_url = ""
2. 응답 비율 커스터마이징 (선택 사항)

3. 프로그램 실행
python survey_bot.py
text

python survey_bot.py
### 실행 옵션

100회 제출 후 종료
automate_survey_loop(survey_url, max_count=100)

무한 반복 (Ctrl+C로 중단)
automate_survey_loop(survey_url)

## 📊 실행 예시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 설문 자동화 시작 (랜덤 비율 적용)
🎯 목표: 100회
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 [1회차] 진행 중... (성공: 0) ✅
📋 [2회차] 진행 중... (성공: 1) ✅
📋 [3회차] 진행 중... (성공: 2) ✅
...
📋 [100회차] 진행 중... (성공: 99) ✅

🎉 목표 100회 달성!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 종료 - 성공: 100/100회 (100.0%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⚙️ 설정 옵션

### 응답 비율 설정

`RESPONSE_WEIGHTS` 딕셔너리에서 각 질문별 선택 확률을 가중치로 설정:

### 대기 시간 조정

네트워크 속도에 따라 대기 시간 조정 가능:

time.sleep(5) # 페이지 로딩 대기 (기본 5초)
time.sleep(random.randint(2, 5)) # 다음 설문 대기 (2-5초 랜덤)

## 🛠️ 기술 스택

- **Selenium**: 웹 브라우저 자동화
- **webdriver-manager**: ChromeDriver 자동 관리
- **Python random**: 가중치 기반 랜덤 선택

## 📝 프로젝트 구조
naver-form-auto-survey/
├── survey_bot.py # 메인 실행 파일
├── requirements.txt # 필요 패키지 목록
├── README.md # 프로젝트 설명
├── LICENSE # MIT 라이선스
└── .gitignore # Git 제외 파일 설정

text

## ⚠️ 주의사항

- 이 도구는 **교육 및 테스트 목적**으로만 사용하세요
- 네이버 폼 이용 약관을 준수하세요
- 과도한 자동화는 IP 차단의 원인이 될 수 있습니다
- 실제 설문에 사용 시 설문 작성자의 동의를 받으세요

## 🐛 문제 해결

### Chrome 버전 오류
Chrome 버전과 ChromeDriver 버전 불일치 시
pip install --upgrade webdriver-manager


### 요소를 찾을 수 없음
- 대기 시간을 늘려보세요 (`time.sleep` 값 증가)
- 네이버 폼의 HTML 구조가 변경되었을 수 있습니다

### 제출 버튼 클릭 실패
- 필수 항목이 모두 체크되었는지 확인하세요
- 네트워크 속도가 느린 경우 대기 시간을 늘리세요

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여

Pull Request를 환영합니다! 주요 변경사항은 먼저 Issue를 열어 논의해주세요.

## 👨‍💻 개발자

- **lee hun jea** - [GitHub](https://github.com/leehunjea)

## 🙏 감사의 글

- Selenium 프로젝트
- webdriver-manager 개발자들

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!
