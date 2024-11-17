from django.shortcuts import render
from .models import School_Event

from django.http import HttpResponse
from .schedule import update_schedule  #학사일정 추출하는 schedule.py import
import os

# Create your views here.
def update_schedule_view(request):
    input_file_path = os.path.join(os.path.dirname(__file__), 'schedule.txt')  # 파일 경로
    update_schedule(input_file_path)
    return HttpResponse("School_Event 테이블이 업데이트되었습니다.")

def main(request):
    # 모든 학사 일정을 가져옴
    school_events = School_Event.objects.all()
    # 템플릿에 데이터 전달
    return render(request, 'DASH-01-light.html', {'school_events': school_events})