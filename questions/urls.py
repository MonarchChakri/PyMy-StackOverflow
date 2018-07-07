from django.conf.urls import url
from django.urls import include

from . import views

urlpatterns = [
    url(r'^$', views.questions_list, name='questions'),
    url(r'^create/$', views.questions_create, name='questions_create'),
    url(r'^(?P<slug>[\w-]+)/$', views.questions_detail, name='questions_detail'),
    url(r'^(?P<slug>[\w-]+)/update/$', views.questions_update, name='questions_update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', views.questions_delete, name='questions_delete'),
    url(r'^(?P<slug>[\w-]+)/upvote/$', views.questions_upvote, name='questions_upvote'),
    url(r'^(?P<slug>[\w-]+)/downvote/$', views.questions_downvote, name='questions_downvote'),
    url(r'^(?P<slug>[\w-]+)/answers/', include(('answers.urls', 'answers')), name='answers'),
]
