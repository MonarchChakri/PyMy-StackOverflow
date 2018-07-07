from django import forms

from pagedown.widgets import PagedownWidget

from .models import Answer


class AnswerForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'style': 'resize: none'}))

    class Meta:
        model = Answer
        fields = [
            'content',
        ]
