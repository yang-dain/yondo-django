from django.urls import path, include
from . import views
app_name = 'webapp'


urlpatterns = [
    path('update/', views.update_schedule_view, name='update_schedule'), #학사일정 업데이트
    path('main/', views.main, name='main'), #메인화면
    path('login/', views.login, name='login'), #로그인
    path('signup/', views.signup, name='signup'), #회원가입
    path('mypage/', views.mypage, name='mypage'),  # 마이페이지
    path('mypage/event', views.schedule_list, name='schedule_list'),  # 내 일정 관리
    path('event/', views.todo_view, name='todo_view'), #일정 목록
    path('event/create/', views.post, name='post'), #일정 추가
    path('event/edit/', views.todo_edit, name='todo_edit'),  # 일정 수정/삭제
    path('event/ui/', views.ui_list, name='ui_list'),  # ui 설정
    path('find_id/', views.find_id, name='find_id'), #아이디 찾기
    path('find_pw/', views.find_pw, name='find_pw'), #비밀번호 찾기
    path('reset_pw/<str:userid>', views.reset_pw, name='reset_pw'), #비밀번호 변경
]

