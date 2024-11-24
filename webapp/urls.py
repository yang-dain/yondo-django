from django.urls import path, include
from . import views
from .views import event_manage, event_list, event_create
app_name = 'webapp'

urlpatterns = [

    path('update/', views.update_schedule_view, name='update_schedule'), #학사일정 업데이트
    path('main/', views.main, name='main'), #메인화면
    path('login/', views.login, name='login'), #로그인
    path('signup/', views.signup, name='signup'), #회원가입
    path('event/<int:user_id>/', views.event_list, name='event_list,'), #일정 목록
    path('event/<int:user_id>/create/', views.event_create, name='event_create'), #일정 추가
    path('event/<int:user_id>/manage', views.event_manage, name='event_manage'), #일정 변경/삭제
]

