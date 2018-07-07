from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

import accounts.views
import project.views
import questions.views

handler404 = 'project.views.handler404'

urlpatterns = [

    url(r'^signup/', accounts.views.register_view, name='signup'),
    url(r'^login/', accounts.views.login_view, name='login'),
    url(r'^password/$', accounts.views.change_password, name='change_password'),
    url(r'^get_user/(?P<id>\d+)/', accounts.views.get_user_view, name='get_user'),
    url(r'^logout/', accounts.views.logout_user, name='logout'),

    url(r'^$', project.views.redirect_to_home, name='root'),
    url(r'^questions/', include(('questions.urls', 'questions'))),
    url(r'^api/get_questions/', questions.views.get_questions, name='get_questions'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += (url(r'^admin/', admin.site.urls),)
