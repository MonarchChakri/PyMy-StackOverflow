import markdown_deux
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from questions.models import Question


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField(null=False, max_length=400)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_delete_url(self):
        return reverse("questions:answers:answers_delete", kwargs={'id': self.id, 'slug': self.question.slug})

    def get_update_url(self):
        return reverse("questions:answers:answers_update", kwargs={'id': self.id, 'slug': self.question.slug})

    def get_absolute_url(self):
        return reverse("questions:answers:answers_thread", kwargs={'id': self.id, 'slug': self.question.slug})

    def get_markdown(self):
        content = self.content
        return mark_safe(markdown_deux.markdown(content))

    def children(self):
        return Answer.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True

    class Meta:
        ordering = ['-id', '-timestamp', '-updated']
