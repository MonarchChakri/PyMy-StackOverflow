import markdown_deux
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
# Create your models here.
# MVC Model View Controller
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class Question(models.Model):

    title = models.CharField(max_length=128, null=False)
    content = models.TextField(null=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    slug = models.SlugField(unique=True)

    status = models.BooleanField(null=False, default=False)

    reputation_set = set()

    reputation_count = 0

    reputation_str = models.TextField(default=',')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("questions:questions_detail", kwargs={'slug': self.slug})

    def get_markdown(self):
        content = self.content
        return mark_safe(markdown_deux.markdown(content))

    @property
    def answers(self):
        import answers.models
        return answers.models.Answer.objects.filter(question=self, parent=None)

    class Meta:
        ordering = ['-id', '-timestamp', '-updated']


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Question.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = f'{slug}-{qs.first().id}'
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_question_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_question_receiver, sender=Question)
