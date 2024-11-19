from django.urls import path, include
from . import views
app_name = 'webapp'

urlpatterns = [

    path('update/', views.update_schedule_view, name='update_schedule'),
]
