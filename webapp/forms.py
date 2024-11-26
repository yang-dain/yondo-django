from django import forms
from django.forms import DateInput, TextInput, Textarea, CheckboxInput
from .models import Event

class PostForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('start_date', 'end_date', 'name', 'memo', 'is_completed')
        widgets = {
            'start_date': DateInput(attrs={
                'type': 'date',
                'id': 'start-date',
                'class': 'date-input',
                'placeholder': '시작 날짜를 선택해주세요'
            }),
            'end_date': DateInput(attrs={
                'type': 'date',
                'id': 'end-date',
                'class': 'date-input',
                'placeholder': '종료 날짜를 선택해주세요'
            }),
            'name': TextInput(attrs={
                'id': 'schedule-title',
                'class': 'input-group',
                'placeholder': '일정이름을 입력하세요...'
            }),
            'memo': Textarea(attrs={
                'id': 'schedule-content',
                'class': 'input-group',
                'rows': 4,
                'placeholder': '메모를 입력하세요...'
            }),
            'is_completed': CheckboxInput(attrs={
                'id': 'is-completed',
                'class': 'checkbox-input'
            }),
        }
