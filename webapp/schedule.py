import re
from datetime import datetime
from .models import School_Event  # Django 모델 임포트

def update_schedule(input_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_year = 2024
    current_month = None
    month_map = {
        "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
        "JAN": "01", "FEB": "02"
    }

    events = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 월 정보 갱신
        if any(month in line for month in month_map.keys()):
            current_month = month_map[line.split()[1]]
            if current_month == "01":
                current_year += 1
            i += 1
            continue

        # 일정 처리
        if "(" in line:
            if "~" in line:  # 날짜 범위
                date_part = line.split("~")
                start_day = re.search(r'\d+', date_part[0]).group()
                end_day_part = date_part[1].strip()

                # 요일 정보 제거
                end_day_part = re.sub(r'\(.*?\)', '', end_day_part).strip()

                # 종료 날짜에 달 정보가 포함되어 있는지 확인
                if "." in end_day_part:
                    # 종료 날짜에 달 정보가 있으면 분리
                    end_month, end_day = end_day_part.split(".")
                    end_month = f"{int(end_month):02}"  # 월 정보 포맷팅
                else:
                    # 달 정보가 없으면 현재 달 사용
                    end_month = current_month
                    end_day = re.search(r'\d+', end_day_part).group()

                # 시작 및 종료 날짜 계산
                start_date = datetime.strptime(f"{current_year}-{current_month}-{start_day}", "%Y-%m-%d")
                end_date = datetime.strptime(f"{current_year}-{end_month}-{end_day}", "%Y-%m-%d")

            else:  # 단일 날짜
                end_day = re.search(r'\d+', line).group()
                end_date = datetime.strptime(f"{current_year}-{current_month}-{end_day}", "%Y-%m-%d")
                start_date = None

            event_name = lines[i + 1].strip()
            events.append(School_Event(name=event_name, start_date=start_date, end_date=end_date))
            i += 2
        else:
            i += 1

    # 데이터베이스에 저장
    School_Event.objects.bulk_create(events)
