from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<id>\d+)/$', views.answers_thread, name='answers_thread'),
    url(r'^(?P<id>\d+)/delete/$', views.answers_delete, name='answers_delete'),
]
