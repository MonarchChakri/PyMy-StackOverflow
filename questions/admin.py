from django.contrib import admin

# Register your models here.
from .models import Question


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'updated', 'timestamp']
    list_filter = ['updated', 'timestamp']
    search_fields = ['title', 'content']

    class Meta:
        model = Question


admin.site.register(Question, QuestionAdmin)
