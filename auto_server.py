from flask import Flask, request, jsonify
import os
import easyocr
import re
from datetime import datetime
import google.oauth2.credentials
from googleapiclient.discovery import build
import json

# auto_server.py 역할 : 
# 이미지 파일 받고 -> OCR로 텍스트 추출 -> 일정 파싱 -> 구글 캘린더에 자동 등록하는 서버 API

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads' # 이미지 저장 폴더
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========== Google Calendar 설정 ==========
# 클라이언트 정보 읽기
with open("credentials.json") as f:
    google_creds = json.load(f)["web"]

# Google Calendar에 일정 추가하는 함수
def insert_to_calendar(event, token):
    creds = google.oauth2.credentials.Credentials(
        token,
        refresh_token=None,
        token_uri=google_creds['token_uri'],
        client_id=google_creds['client_id'],
        client_secret=google_creds['client_secret'],
        scopes=['https://www.googleapis.com/auth/calendar.events']
    )
    service = build('calendar', 'v3', credentials=creds)

    # 캘린더에 등록할 이벤트 정보 구성
    event_body = {
        'summary': event['name'],
        'start': {'dateTime': f"{event['date']}T{event['start']}:00", 'timeZone': 'Asia/Seoul'},
        'end': {'dateTime': f"{event['date']}T{event['end']}:00", 'timeZone': 'Asia/Seoul'},
    }
    # 실제 일정 등록 요청
    service.events().insert(calendarId='primary', body=event_body).execute()


# ========== OCR + 파싱 함수 ==========
# 이미지 분석해서 이름, 날짜, 시간대등 일정 데이터 추출
def extract_schedule_from_image(image_path):
    reader = easyocr.Reader(['ko', 'en'])
    results = reader.readtext(image_path, detail=0) # 텍스트만 추출

    lines = [line.strip() for line in results if line.strip()] # 빈 줄 제거
    schedules = []        # 추출된 일정 저장
    current_dates = []    # 날짜 후보
    current_name = ""     # 현재 이름
    date_blocks = []      # 주 단위 날짜 묶음
    base_year = 2025      # 기본 연도
    base_month = 7        # 기본 월

    for line in lines:
        #숫자만 있는 줄 : 날짜로 간주
        if re.fullmatch(r'\d{1,2}', line):
            current_dates.append(int(line))
            continue

        # "일" 키워드로 주차 구분
        if line == "일" and current_dates:
            date_blocks.append(current_dates)
            current_dates = []
            continue

        # 이름 줄 
        if re.fullmatch(r"[가-힣]{2,4}", line):
            current_name = line
            day_index = 0
            continue

        # 시간대 
        if re.fullmatch(r"\d{1,2}-\d{1,2}(\.\d+)?", line):
            if not current_name or not date_blocks:
                continue
            try:
                dates = date_blocks[-1]
                date_val = dates[day_index]
                day_index += 1
            except IndexError:
                continue

            # 시작 - 종료 시간 분리
            times = re.findall(r"\d{1,2}", line)
            if len(times) >= 2:
                start_hour = int(times[0])
                end_hour = int(float(times[1]))
                date_str = f"{base_year}-{base_month:02d}-{date_val:02d}"
                schedules.append({
                    "name": current_name,
                    "date": date_str,
                    "start": f"{start_hour:02d}:00",
                    "end": f"{end_hour:02d}:00"
                })

    return schedules


# ========== API 엔드포인트 ==========
# 이미지 업로드 API : Postman에서 추출
@app.route('/upload-image', methods=['POST'])
def upload_image():
    file = request.files['image'] 
    token = request.form.get('access_token')
    if not token:
        return jsonify({"error": "access_token required"}), 400

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    # OCR 후 일정 파싱
    schedule_list = extract_schedule_from_image(filename)

    # 일정 등록
    for item in schedule_list:
        insert_to_calendar(item, token)

    # 응답 반환
    return jsonify({"status": "success", "count": len(schedule_list), "data": schedule_list})

# 서버 실행 (디버그 모드)
if __name__ == '__main__':
    app.run(debug=True)
