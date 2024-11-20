from django.shortcuts import render
from .models import School_Event
import json

from django.http import HttpResponse
from django.utils.dateformat import DateFormat
from .schedule import update_schedule  #학사일정 추출하는 schedule.py import
import os

# Create your views here.
def update_schedule_view(request):
    input_file_path = os.path.join(os.path.dirname(__file__), 'schedule.txt')  # 파일 경로
    update_schedule(input_file_path)
    return HttpResponse("School_Event 테이블이 업데이트되었습니다.")


def main(request):
    try:
        # 모든 학사 일정 가져오기
        school_events = School_Event.objects.all()

        event_data = []
        for event in school_events:
            start_date = DateFormat(event.start_date).format("Y-m-d") if event.start_date else None
            end_date = DateFormat(event.end_date).format("Y-m-d") if event.end_date else None

            # 일정 표시 형식 결정
            if start_date:  # 연속 일정 (start_date와 end_date 둘 다 있을 경우)
                date_range = f"{start_date} ~ {end_date}"
            else:  # 단일 일정 (start_date가 없을 경우)
                date_range = end_date

            # 데이터 추가
            event_data.append({
                "name": event.name,
                "date_range": date_range,  # 표시용 날짜 범위
                "start_date": start_date,  # 캘린더 이벤트에 사용
                "end_date": end_date       # 캘린더 이벤트에 사용
            })

        # 템플릿으로 데이터 전달
        return render(request, 'DASH-01-light.html', {'school_events': json.dumps(event_data)})

    except Exception as e:
        print(f"Error occurred: {e}")
        return render(request, 'error.html', {'error_message': str(e)})
