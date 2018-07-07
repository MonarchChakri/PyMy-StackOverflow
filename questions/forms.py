from django import forms

from pagedown.widgets import PagedownWidget

from .models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'title',
            'content',
        ]

        widgets = {
            'content': PagedownWidget(show_preview=False, attrs={'style': 'resize: none'}, template='pagedown.html'),
        }
