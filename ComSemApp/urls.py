from django.conf.urls import url, include

from . import views
from ComSemApp.utils import transcribe, get_youglish_videos

urlpatterns = [
    url(r'^$', views.About.as_view(), name='about'),
    url(r'^about/teacher/$', views.AboutTeacher.as_view(), name='about_teacher'),
    url(r'^contact/$', views.Contact.as_view(), name='contact'),

    url(r'^initiate_roles/$', views.initiate_roles, name='initiate_roles'),
    url(r'^administrator/', include('ComSemApp.administrator.urls', namespace='administrator')),
    url(r'^teacher/', include('ComSemApp.teacher.urls', namespace='teacher')),
    url(r'^student/', include('ComSemApp.student.urls', namespace='student')),
    url(r'^corpus/', include('ComSemApp.corpus.urls', namespace='corpus')),
    url(r'^transcribe_audio/', transcribe, name='transcribe_audio'),
    url(r'^youglish_video', get_youglish_videos, name = 'get_youglish_videos')
]
