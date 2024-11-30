from django.urls import path, include
from . import views
app_name = 'webapp'


urlpatterns = [
    path('update/', views.update_schedule_view, name='update_schedule'), #학사일정 업데이트
    path('main/', views.main, name='main'), #메인화면
    path('login/', views.login, name='login'), #로그인
    path('logout/', views.logout, name='logout'), #로그아웃
    path('signup/', views.signup, name='signup'), #회원가입
    path('mypage/', views.mypage, name='mypage'),  # 마이페이지
    path('mypage/event', views.schedule_list, name='schedule_list'),  # 내 일정 관리
    path('event/', views.todo_view, name='todo_view'), #일정 목록
    path('event/create/', views.post, name='post'), #일정 추가
    path('event/edit/', views.edit, name='edit'),  # 일정 수정/삭제
    path('mypage/account/', views.account, name='account'),  # 내 정보 관리
    path('event/ui/', views.ui_list, name='ui_list'),  # ui 설정
    path('find_id/', views.find_id, name='find_id'), #아이디 찾기
    path('find_pw/', views.find_pw, name='find_pw'), #비밀번호 찾기
    path('reset_pw/', views.reset_pw, name='reset_pw'), #비밀번호 변경
    path('del_account/', views.del_account, name='del_account'), #회원 탈퇴
]

