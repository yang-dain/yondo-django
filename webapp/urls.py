from django.urls import path, include
from . import views
app_name = 'webapp'

urlpatterns = [

    path('update/', views.update_schedule_view, name='update_schedule'), #학사일정 업데이트
    path('main/', views.main, name='main'), #메인화면
]
