from django.contrib import admin
from .models import Custom_user, Event, School_Event

# Register your models here.

admin.site.register(Custom_user)
admin.site.register(Event)
admin.site.register(School_Event)
