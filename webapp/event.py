from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Event, Custom_user, School_Event
from datetime import date

from django.db.models import Q


def school_event_list():
    school_events_queryset = School_Event.objects.values('id', 'start_date', 'end_date', 'name')

    def format_event(event):

        if not event['start_date']:
            event['start_date'] = event['end_date']

        event['start_date'] = event['start_date'].isoformat() if event['start_date'] else None
        event['end_date'] = event['end_date'].isoformat()
        return event

    return {"school_events": [format_event(event) for event in school_events_queryset],}


def event_list(custom_user):
    today = date.today()

    # 끝난 이벤트
    end_events_queryset = Event.objects.filter(
        Q(end_date__lt=today) | Q(is_completed=True),
        user=custom_user
    ).values('id', 'start_date', 'end_date', 'name', 'memo')

    # 진행중 이벤트
    events_queryset = Event.objects.filter(
        ~Q(end_date__lt=today) & ~Q(is_completed=True),
        user=custom_user
    ).values('id', 'start_date', 'end_date', 'name', 'memo')


    def format_event(event):
        event['start_date'] = event['start_date'].isoformat()  # 'YYYY-MM-DD' 형식
        event['end_date'] = event['end_date'].isoformat()
        return event

    return {
        "current_events": [format_event(event) for event in events_queryset],
        "ended_events": [format_event(event) for event in end_events_queryset],
    }