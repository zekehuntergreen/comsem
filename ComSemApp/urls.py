from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^corpus/$', views.corpus, name='corpus'),

    url(r'^teacher/$', views.teacher, name='teacher'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/$', views.teacher_course, name='teacher_course'),
    url(r'^teacher/worksheet/(?P<worksheet_id>[0-9]+)/$', views.teacher_worksheet, name='teacher_worksheet'),

    url(r'^ajax/course_students/$', views.course_students, name='course_students'),

]
