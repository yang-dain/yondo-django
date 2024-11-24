from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Event, Custom_user
from datetime import date, timedelta
from django.db.models import Q


def event_list(request, user_id):
    user = get_object_or_404(Custom_user, pk=user_id)

    year = request.GET.get('year')
    month = request.GET.get('month')

    if year and month:
        year = int(year)
        month = int(month)
        try:
            current_date = date(year, month, 1)
        except ValueError:
            current_date = date.today()
    else:
        current_date = date.today()

    today = date.today()  # 현재 날짜와 시간을 포함한 datetime 객체
    first_day = current_date.replace(day=1)
    last_day = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # 이전 달과 다음 달 계산
    previous_month = (first_day - timedelta(days=1)).replace(day=1)
    next_month = (last_day + timedelta(days=31)).replace(day=1)
    next_last_day = (next_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    prev_first_day = previous_month
    prev_last_day = (previous_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    next_first_day = next_month
    next_last_day = next_last_day

    # 일정 필터링
    if current_date.month == today.month and current_date.year == today.year:
        # 현재 달의 일정
        current_events = Event.objects.filter(
            user=user,
            start_date__lte=last_day,  # 시작일은 이번 달 내에 있어야 함
            end_date__gte=today  # 종료일은 오늘 이후여야 함
        ).exclude(is_completed=True)

        ended_events = Event.objects.filter(
            Q(end_date__lt=today) | Q(is_completed=True),
            user=user
        ).exclude(end_date__lte=prev_last_day)
    elif current_date < today.replace(day=1):
        # 이전 달의 일정
        current_events = Event.objects.filter(
            user=user,
            start_date__gte=prev_first_day,
            start_date__lte=prev_last_day,
            end_date__gte=today,  # 종료일은 오늘 이후여야 함
            is_completed=False
        )
        ended_events = Event.objects.filter(end_date__lte=prev_last_day)
    else:
        # 다음 달의 일정
        current_events = Event.objects.filter(
            user=user,
            end_date__gte=next_first_day,
            end_date__lte=next_last_day,
            is_completed=False
        )
        ended_events = Event.objects.none()  # 다음 달로 이동 시 종료된 일정 표시 안 함

    context = {
        'current_events': current_events,
        'ended_events': ended_events,
        'user': user,
        'current_year': current_date.year,
        'current_month': current_date.month,
        'previous_year': previous_month.year,
        'previous_month': previous_month.month,
        'next_year': next_month.year,
        'next_month': next_month.month,
    }
    return render(request, 'TODO-01-light.html', context)



# 일정 추가
def event_create(request, user_id):
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
