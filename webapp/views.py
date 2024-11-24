from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Custom_user
import json
from .event import event_list, event_manage, event_create, school_event_list
from django.shortcuts import render, get_object_or_404, redirect


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
        school_events = school_event_list()
        return render(request, 'DASH-01-light.html', {'school_events': json.dumps(school_events)})

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


def find_id(request):
    if request.method == "POST":
        name = request.POST.get('name')  # 이름
        email = request.POST.get('email')  # 이메일

        try:
            # 이름과 이메일로 사용자 찾기
            user = Custom_user.objects.get(name=name, user_email=email)

            # 사용자 찾았을 때 아이디 반환
            user_id = user.id  # 또는 user.id, user.username 등으로 아이디 값을 반환

            # 성공 메시지
            messages.success(request, f"{name}님의 아이디는 {user_id}입니다.")

            # 아이디를 알림 팝업으로 표시하도록 메시지 전달
            return render(request, 'AUTH-01-light.html')

        except Custom_user.DoesNotExist:
            # 이름이나 이메일이 일치하지 않으면 오류 메시지
            messages.error(request, '입력한 정보와 일치하는 아이디가 없습니다.')
            return render(request, 'AUTH-03-light.html')

    return render(request, 'AUTH-03-light.html')

def find_pw(request):
    if request.method == "POST":
        userid = request.POST.get('userid')  # 아이디
        pw_qust = request.POST.get('pw_qust') or 0 # 질문
        pw_ans = request.POST.get('pw_ans')    # 답변

        try:
            # 아이디로 사용자 찾기
            user = Custom_user.objects.get(id=userid)

            # 사용자가 입력한 질문과 답변이 맞는지 비교
            if user.pw_qust == int(pw_qust) and user.pw_ans == pw_ans:
                # 답변이 맞으면 새로운 비밀번호 입력 페이지로 리디렉션
                return redirect('webapp:reset_pw', userid=userid)
            else:
                # 질문 또는 답변이 틀린 경우
                messages.error(request, '질문 또는 답변이 일치하지 않습니다.')
        except Custom_user.DoesNotExist:
            # 아이디가 존재하지 않는 경우
            messages.error(request, '아이디가 존재하지 않습니다.')

    return render(request, 'AUTH-04-light.html')

def reset_pw(request, userid):
    if request.method == "POST":
        cur_pw = request.POST.get('cur_pw')
        new_pw = request.POST.get('new_pw')
        new_pw_confirm = request.POST.get('new_pw_confirm')

        try:
            # 사용자 찾기
            user = Custom_user.objects.get(id=userid)

            # 현재 비밀번호 확인
            if user.pw != cur_pw:
                messages.error(request, '현재 비밀번호가 일치하지 않습니다.')
                return render(request, 'AUTH-05-light.html')

            # 새 비밀번호와 확인 비밀번호가 같은지 확인
            if new_pw != new_pw_confirm:
                messages.error(request, '새 비밀번호가 일치하지 않습니다.')
                return render(request, 'AUTH-05-light.html')

            # 새 비밀번호 업데이트
            user.pw = new_pw
            user.save()

            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            return redirect('webapp:login')  # 로그인 페이지로 이동

        except Custom_user.DoesNotExist:
            messages.error(request, '사용자를 찾을 수 없습니다.')
            return redirect('webapp:find_pw')  # 비밀번호 찾기 페이지로 이동

    return render(request, 'AUTH-05-light.html')


def todo_view(request): #일정 목록
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('/webapp/login/')

    custom_user = get_object_or_404(Custom_user, id=user_id)

    event_data = school_event_list()
    events_data = event_list(custom_user)


    return render(request, 'TODO-01-light.html', {
        'school_events': json.dumps(event_data['school_events']), # 학사일정
        'current_events': json.dumps(events_data['current_events']),  # 예정된 일정
        'ended_events': json.dumps(events_data['ended_events']),  # 종료된 일정
    })
