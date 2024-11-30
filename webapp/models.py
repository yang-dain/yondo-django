from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Custom_user(models.Model):
    key = models.AutoField(primary_key=True)
    id = models.CharField(unique=True , max_length=10, blank=False, null=False)
    pw = models.CharField(max_length=20, blank=False, null=False)
    user_email = models.EmailField(max_length=128, blank=False, null=False)
    pw_qust = models.IntegerField(default=0)
    pw_ans = models.CharField(max_length=10, blank=False, null=False)
    name = models.CharField(max_length=10, blank=False, null=False)
    join_date = models.DateField(auto_now_add=True)
    hide_school_events = models.BooleanField(default=False)
    hide_end_events = models.BooleanField(default=False)
    mode = models.BooleanField(default=False)

class Event(models.Model):
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, blank=False, null=False)
    start_date = models.DateField(blank=True, null=True)
    end_date =  models.DateField(blank=False, null=False)
    memo = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

class School_Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, blank=False, null=False)
    start_date = models.DateField(blank=True, null=True)
    end_date =  models.DateField(blank=False, null=False)
