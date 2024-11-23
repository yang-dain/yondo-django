from django.urls import path, include
from . import views
app_name = 'webapp'

urlpatterns = [

    path('update/', views.update_schedule_view, name='update_schedule'), #학사일정 업데이트
    path('main/', views.main, name='main'), #메인화면
    path('login/', views.login, name='login'), #로그인
    path('signup/', views.signup, name='signup'), #회원가입
]

