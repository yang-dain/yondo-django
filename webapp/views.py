from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import School_Event
from .models import Custom_user
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

def login(request):
    if request.method == "POST":
        # 폼에서 받은 아이디와 비밀번호
        userid = request.POST.get('userid')
        password = request.POST.get('password')

        try:
            # 아이디로 사용자 찾기
            user = Custom_user.objects.get(id=userid)

            # 비밀번호가 일치하는지 확인 (평문 비교)
            if user.pw == password:  # 평문 비밀번호 비교
                # 비밀번호 일치 -> 로그인 처리
                request.session['user_id'] = user.id  # 세션에 사용자 ID 저장
                messages.success(request, '로그인 성공!')
                return redirect('webapp:main')  # 로그인 후 메인 페이지로 리디렉션
            else:
                # 비밀번호 불일치
                messages.error(request, '아이디 또는 비밀번호가 일치하지 않습니다.')
        except Custom_user.DoesNotExist:
            # 아이디가 존재하지 않는 경우
            messages.error(request, '아이디 또는 비밀번호가 일치하지 않습니다.')

    return render(request, 'AUTH-01-light.html')

def signup(request):
    # AUTH-02-light.html에서 입력값 받아옴
    if request.method == "POST":
        name = request.POST.get('name')
        user_id = request.POST.get('id')
        pw = request.POST.get('pw')
        pw_confirm = request.POST.get('pw_confirm')
        user_email = request.POST.get('email')
        pw_qust = request.POST.get('pw_qust') or 0
        pw_ans = request.POST.get('pw_ans')

        #pw 확인
        if pw != pw_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, 'AUTH-02-light.html')

        #id 중복 확인
        if Custom_user.objects.filter(id=user_id).exists():
            messages.error(request, '이미 존재하는 아이디입니다.')
            return render(request, 'AUTH-02-light.html')

        # custom_user 테이블에 저장
        try:
            Custom_user.objects.create(
                name=name,
                id=user_id,
                pw=pw,
                user_email=user_email,
                pw_qust=int(pw_qust),
                pw_ans=pw_ans
            )
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('webapp:main')
        except Exception as e:
            messages.error(request, f'회원가입 중 오류가 발생했습니다: {e}')
            return render(request, 'AUTH-02-light.html')

    return render(request, 'AUTH-02-light.html')
