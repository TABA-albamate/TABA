# 🧠 AI 기반 일정 자동 등록 시스템

> 이미지 또는 엑셀로 된 일정표를 AI로 자동 분석하고, Google Calendar에 일정으로 등록하는 Flask 기반 서버입니다.

---

## 🚀 프로젝트 개요

- **입력**: 알바 스케줄 이미지 (`.png`, `.jpg` 등)
- **처리**:
  - EasyOCR로 텍스트 추출
  - 이름, 날짜, 시간대 파싱
  - Google Calendar API를 통해 자동 등록
- **출력**: 구글 캘린더에 자동 생성된 일정

---

## 🧰 기술 스택

| 구성 요소 | 사용 기술 |
|-----------|-----------|
| 서버 프레임워크 | Flask |
| AI 문자 인식 | EasyOCR |
| 캘린더 연동 | Google Calendar API |
| 테스트 도구 | Postman |
| 개발 환경 | VSCode + Python (venv) |

---

## 📦 주요 파일 구조

📁 PRAC/
├── app.py # 구글 OAuth 인증 및 테스트용 일정 등록
├── auto_server.py # 이미지 기반 일정 등록 서버
├── ocr_test.py # 로컬 OCR 파싱 테스트용 스크립트
├── credentials.json # 🔒 Git에 포함 X (OAuth 비밀키)
├── uploads/ # 업로드된 이미지 저장 폴더
└── .gitignore # 민감 파일 추적 제외 설정

yaml
복사
편집

---

## 🔐 OAuth 인증 흐름

1. `/authorize` → 구글 로그인 후 `/oauth2callback`으로 리디렉션
2. Access Token 발급
3. `create_event()`에서 일정 등록 API 호출 가능

---

## 📸 이미지 일정 등록 방법 (Postman)

1. **POST 요청**


⚠️ 주의 사항

credentials.json, client_secret_*.json은 절대 Git에 올리지 말 것

.gitignore에 해당 파일 포함됨

실수로 올렸을 경우 git filter-repo로 히스토리 정리 필요
