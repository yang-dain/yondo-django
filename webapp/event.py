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

    # 각 이벤트를 포맷하여 반환
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

# 일정 추가
def event_create(request):
    user = get_object_or_404(Custom_user, pk=user_id)
    if request.method == "POST":
        name = request.POST['name']
        start_date = request.POST.get('start_date')
        end_date = request.POST['end_date']
        memo = request.POST.get('memo', '')
        is_completed = request.POST.get('is_completed', 'off') == 'on'

        Event.objects.create(
            user=user,
            name=name,
            start_date=start_date,
            end_date=end_date,
            memo=memo,
            is_completed=is_completed
        )
        return redirect('event_list', user_id=user_id)

    return render(request, 'TODO-02-light.html', {'user': user, 'user_key': user.key})

# 일정 변경/삭제
def event_manage(request, user_id, event_id):
    user = get_object_or_404(Custom_user, pk=user_id)
    event = get_object_or_404(Event, id=event_id, user=user)

    if request.method == "POST":
        action = request.POST.get('action')
        if action == "update":  # 수정
            event.name = request.POST.get('name', event.name)
            event.start_date = request.POST.get('start_date', event.start_date)
            event.end_date = request.POST.get('end_date', event.end_date)
            event.memo = request.POST.get('memo', event.memo)
            event.is_completed = request.POST.get('is_completed') == "true"
            event.save()
            return JsonResponse({'status': 'success', 'message': 'Event updated successfully'})

        elif action == "delete":  # 삭제
            event.delete()
            return JsonResponse({'status': 'success', 'message': 'Event deleted successfully'})

    return render(request, 'TODO-03-light.html', {'user': user, 'event': event})
