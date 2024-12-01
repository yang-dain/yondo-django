from lib2to3.fixes.fix_input import context

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Custom_user,Event
import json
from .event import event_list, school_event_list
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from django.http import JsonResponse

from django.http import HttpResponse
from django.utils.dateformat import DateFormat
from datetime import date
from .schedule import update_schedule
import os

# Create your views here.
def update_schedule_view(request):
    input_file_path = os.path.join(os.path.dirname(__file__), 'schedule.txt')  # 파일 경로
    update_schedule(input_file_path)
    return HttpResponse("School_Event 테이블이 업데이트되었습니다.")

def main(request):
    user_id = request.session.get('user_id')
    is_logged_in = request.session.get('is_logged_in', 0)
    print(f"User ID: {user_id}, Is Logged In: {is_logged_in}")  # 세션 값 확인하려고 잠깐 넣었어용
    
    try:
        school_events = school_event_list()
        for event in school_events["school_events"]:
            event["content"] = event.pop("name")
            event["type"] = "school"

        if user_id:
            custom_user = get_object_or_404(Custom_user, id=user_id)
            mode = int(custom_user.mode)  # 0: 다크모드, 1: 라이트모드
            request.session['mode'] = mode
            print(f"mode: {mode}")

            hide_school_events = custom_user.hide_school_events
            hide_end_events = custom_user.hide_end_events
            events_data = event_list(custom_user)
            for event in events_data["current_events"]:
                event["content"] = event.pop("name")
                event["type"] = "current"
                event.pop("memo", None)

            for event in events_data["ended_events"]:
                event["content"] = event.pop("name")
                event["type"] = "ended"
                event.pop("memo", None)

            current_events = json.dumps(events_data['current_events'])
            ended_events = json.dumps(events_data['ended_events'])
        else: #비로그인 시
            mode = 1  # 라이트모드 기본값
            request.session['mode'] = mode

            hide_school_events = False
            hide_end_events = False
            current_events = json.dumps([])  # 비로그인 사용자의 경우 빈 리스트로 처리
            ended_events = json.dumps([])

        return render(request, 'DASH-01.html', {
            'school_events': json.dumps(school_events),
            'current_events' : current_events,
            'ended_events' : ended_events,
            'hide_school_events': hide_school_events,
            'hide_end_events': hide_end_events,
            'is_logged_in': request.session.get('is_logged_in', 0),
            'mode': mode
        })

    except KeyError as e:
        print(f"KeyError occurred: {e}")
        return render(request, 'error-light.html', {'error_message': f"KeyError: {e}"})
    except Exception as e:
        print(f"Error occurred: {e}")
        return render(request, 'error-light.html', {'error_message': str(e)})

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
                request.session['is_logged_in'] = 1 # 세션 로그인 상태
                messages.success(request, '로그인 되었습니다.')
                return redirect('webapp:main')  # 로그인 후 메인 페이지로 리디렉션
            else:
                # 비밀번호 불일치
                messages.error(request, '아이디 또는 비밀번호가 일치하지 않습니다.')
        except Custom_user.DoesNotExist:
            # 아이디가 존재하지 않는 경우
            messages.error(request, '아이디 또는 비밀번호가 일치하지 않습니다.')

    return render(request, 'AUTH-01.html')
def logout(request):
    try:
        del request.session['user_id']
        del request.session['is_logged_in']
        messages.success(request, '로그아웃 되었습니다.')
        return redirect('webapp:main')
    except KeyError:
        pass

    return redirect('webapp:main')

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

    return render(request, 'AUTH-02.html')


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
            return  redirect('webapp:login')

            # 아이디를 알림 팝업으로 표시하도록 메시지 전달
            return render(request, 'AUTH-01.html')

        except Custom_user.DoesNotExist:
            # 이름이나 이메일이 일치하지 않으면 오류 메시지
            messages.error(request, '입력한 정보와 일치하는 아이디가 없습니다.')
            return render(request, 'AUTH-03.html')

    return render(request, 'AUTH-03.html')
    

def find_pw(request):
    if request.method == "POST":
        userid = request.POST.get('userid')  # 아이디
        pw_qust = request.POST.get('pw_qust') or 0 # 질문
        pw_ans = request.POST.get('pw_ans')    # 답변

        try:
            custom_user = Custom_user.objects.get(id=userid)

            # 사용자가 입력한 질문과 답변이 맞는지 비교
            if custom_user.pw_qust == int(pw_qust) and custom_user.pw_ans == pw_ans:
                # 답변이 맞으면 새로운 비밀번호 입력 페이지로 리디렉션
                request.session['user_id'] = userid
                return redirect('webapp:reset_pw')
            else:
                # 질문 또는 답변이 틀린 경우
                messages.error(request, '질문 또는 답변이 일치하지 않습니다.')
        except Custom_user.DoesNotExist:
            # 아이디가 존재하지 않는 경우
            messages.error(request, '아이디가 존재하지 않습니다.')

    return render(request, 'AUTH-04.html')

def reset_pw(request):
    if request.method == "POST":
        new_pw = request.POST.get('new_pw')
        new_pw_confirm = request.POST.get('new_pw_confirm')

        try:
            user_id = request.session.get('user_id')

            if not user_id:
                return redirect('webapp:login')

            custom_user = get_object_or_404(Custom_user, id=user_id)

            # 새 비밀번호와 확인 비밀번호가 같은지 확인
            if new_pw != new_pw_confirm:
                messages.error(request, '새 비밀번호가 일치하지 않습니다.')
                return render(request, 'AUTH-05.html')

            # 새 비밀번호 업데이트
            custom_user.pw = new_pw
            custom_user.save()

            request.session.flush() # 세션 초기화
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            messages.success(request, '다시 로그인 해주세요.')
            return redirect('webapp:login')  # 로그인 페이지로 이동

        except Custom_user.DoesNotExist:
            messages.error(request, '사용자를 찾을 수 없습니다.')
            return redirect('webapp:find_pw')  # 비밀번호 찾기 페이지로 이동

    return render(request, 'AUTH-05.html')

def del_account(request): #회원 탈퇴
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('webapp:login')  

    try:
        custom_user = Custom_user.objects.get(id=user_id)

        if request.method == "POST":  # POST 요청으로 탈퇴 실행
            print(custom_user)
            custom_user.delete() # 사용자 삭제
            request.session.flush() # 세션 종료 및 로그아웃

            return render(request, 'withdraw-light.html')

        # 탈퇴 확인 페이지 렌더링
        return render(request, 'withdraw-light.html')

    except Custom_user.DoesNotExist:
        messages.error(request, '사용자를 찾을 수 없습니다.')
        return redirect('webapp:login')

def todo_view(request): #일정 목록
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('webapp:login')

    custom_user = get_object_or_404(Custom_user, id=user_id)

    event_data = school_event_list()
    events_data = event_list(custom_user)


    return render(request, 'TODO-01.html', {
        'school_events': json.dumps(event_data['school_events']), # 학사일정
        'current_events': json.dumps(events_data['current_events']),  # 예정된 일정
        'ended_events': json.dumps(events_data['ended_events']),  # 종료된 일정
    })

def mypage(request): #마이페이지

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('webapp:login')

    custom_user = get_object_or_404(Custom_user, id=user_id)

    user_name = custom_user.name
    join_date = custom_user.join_date
    today = date.today()
    days_elapsed = (today - join_date).days

    user_events_data = event_list(custom_user)
    current_events = user_events_data.get("current_events", [])
    ended_events = user_events_data.get("ended_events", [])

    completed_schedules = len(ended_events)
    remaining_schedules = len(current_events)

    mode = request.session.get('mode', 1)
    print(f"mode: {mode}")

    # 템플릿에 데이터 전달
    return render(request, 'SET-00.html', {
        'user_name': user_name,
        'days_elapsed': days_elapsed,
        'completed_schedules': completed_schedules,
        'remaining_schedules': remaining_schedules,
        'mode': mode,
    })

def account(request): # 내 정보 관리
    user_id = request.session.get('user_id') 

    if not user_id:
        return redirect('webapp:login')

    custom_user = get_object_or_404(Custom_user, id=user_id)
    mode = request.session.get('mode', 1)
    print(f"mode: {mode}")

    return render(request, 'SET-01.html', {
        'user': custom_user,
        'mode': mode,
    })  # user 데이터 전달


def schedule_list(request): #내 일정 관리
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('webapp:login')

    custom_user = get_object_or_404(Custom_user, id=user_id)
    mode = request.session.get('mode', 1)
    print(f"mode: {mode}")

    return render(request, 'SET-03.html', {
        'mode': mode,
    })  # user 데이터 전달

def post(request): #일정 추가
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('webapp:login')

    custom_user = get_object_or_404(Custom_user, id=user_id)
    hide_school_events = custom_user.hide_school_events
    hide_end_events = custom_user.hide_end_events
    events_data = event_list(custom_user)
    for event in events_data["current_events"]:
        event["title"] = event.pop("name")
        event["type"] = "current"
        event.pop("memo", None)

    for event in events_data["ended_events"]:
        event["title"] = event.pop("name")
        event["type"] = "ended"
        event.pop("memo", None)

    school_events = school_event_list()
    for event in school_events["school_events"]:
        event["title"] = event.pop("name")
        event["type"] = "school"

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = custom_user
            post.save()
            messages.success(request, "일정이 추가되었습니다.")
            return redirect('webapp:post')
        else:
            messages.error(request, '유효하지 않은 데이터입니다.')
            return redirect('webapp:post')
    else:
        form = PostForm()

    context = {'form': form, 'user_id': user_id,
               'hide_school_events': hide_school_events,
               'hide_end_events': hide_end_events,
               'school_events': json.dumps(school_events),
            'current_events' : json.dumps(events_data['current_events']),
            'ended_events' : json.dumps(events_data['ended_events']),}


    return render(request, 'TODO-02.html', context)


def edit(request, event_id=None):  # 일정 변경/삭제
    user_id = request.session.get('user_id')
    event = None

    if not user_id:
        return redirect('webapp:login')

    custom_user = get_object_or_404(Custom_user, id=user_id)
    hide_school_events = custom_user.hide_school_events
    hide_end_events = custom_user.hide_end_events
    events_data = event_list(custom_user)

    for event in events_data["current_events"]:
        event["title"] = event.pop("name")
        event["type"] = "current"

    for event in events_data["ended_events"]:
        event["title"] = event.pop("name")
        event["type"] = "ended"

    school_events = school_event_list()
    for event in school_events["school_events"]:
        event["title"] = event.pop("name")
        event["type"] = "school"

    if request.method == "GET":
        if event_id:
            event = get_object_or_404(Event, id=event_id)
        else:
            event = None

        # 모델 인스턴스 변환 로직
        if isinstance(event, dict):
            event = Event(
                id=event.get('id'),
                start_date=event.get('start_date'),
                end_date=event.get('end_date'),
                name=event.get('title')
            )

        form = PostForm(instance=event)
        context = {
            'form': form,
            'user_id': user_id,
            'hide_school_events': hide_school_events,
            'hide_end_events': hide_end_events,
            'school_events': json.dumps(school_events),
            'current_events': json.dumps(events_data['current_events']),
            'ended_events': json.dumps(events_data['ended_events']),
        }
        return render(request, 'TODO-03.html', context)

    if request.method == "POST":
        event_id = request.POST.get('event_id')
        if event_id:
            event = get_object_or_404(Event, id=event_id)

        # 모델 인스턴스 변환 로직
        if isinstance(event, dict):
            event = Event(
                id=event.get('id'),
                start_date=event.get('start_date'),
                end_date=event.get('end_date'),
                name=event.get('title')
            )

        if 'delete' in request.POST:  # 삭제 요청
            if event:
                event.delete()
                messages.success(request, "일정이 삭제되었습니다.")
            return redirect('webapp:edit')

        # 수정 요청 처리
        form = PostForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "일정이 변경되었습니다.")
            return redirect('webapp:edit')

    # POST 요청 처리 후 유효하지 않은 폼 처리
    form = PostForm(instance=event)
    context = {
        'form': form,
        'user_id': user_id,
        'hide_school_events': hide_school_events,
        'hide_end_events': hide_end_events,
        'school_events': json.dumps(school_events),
        'current_events': json.dumps(events_data['current_events']),
        'ended_events': json.dumps(events_data['ended_events']),
    }
    return render(request, 'TODO-03.html', context)



def ui_list(request): #ui 관리
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('webapp:login')

    custom_user = get_object_or_404(Custom_user, id=user_id)

    if request.method == "POST":
        # 버튼의 타입에 따라 상태 변경
        toggle_type = request.POST.get('type')  # "school_events" 또는 "end_events" 또는 "dark_mode"
        if toggle_type == "school_events":
            custom_user.hide_school_events = not custom_user.hide_school_events
        elif toggle_type == "end_events":
            custom_user.hide_end_events = not custom_user.hide_end_events
        elif toggle_type == "dark_mode": # True: 다크모드, False: 라이트모드
            custom_user.mode = 1 if custom_user.mode == 0 else 0
        custom_user.save()

    # 사용자 설정 상태 전달
    context = {
        "hide_school_events": custom_user.hide_school_events,
        "hide_end_events": custom_user.hide_end_events,
        "mode": custom_user.mode,
    }
    return render(request, "SET-02.html", context)
