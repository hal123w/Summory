from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Summary


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class SummaryCreateForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = ('title', 'category', 'original_text')
        labels = {
            'title': 'タイトル（任意）',
            'category': 'カテゴリ（任意・1つ）',
            'original_text': '原文',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': '空なら要約の先頭を使います',
                'class': 'input',
            }),
            'category': forms.TextInput(attrs={
                'placeholder': '例: 田中さんメール、授業資料',
                'class': 'input',
                'list': 'category-suggestions',
            }),
            'original_text': forms.Textarea(attrs={
                'placeholder': '要約したい文章を貼り付けてください',
                'rows': 12,
                'class': 'input textarea',
            }),
        }


class SummaryEditForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = ('title', 'category', 'summary_text', 'original_text')
        labels = {
            'title': 'タイトル',
            'category': 'カテゴリ（任意・1つ）',
            'summary_text': '要約',
            'original_text': '原文',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'category': forms.TextInput(attrs={
                'class': 'input',
                'list': 'category-suggestions',
            }),
            'summary_text': forms.Textarea(attrs={
                'rows': 8,
                'class': 'input textarea',
            }),
            'original_text': forms.Textarea(attrs={
                'rows': 10,
                'class': 'input textarea',
            }),
        }
