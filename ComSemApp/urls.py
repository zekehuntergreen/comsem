from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.about, name='about'),
    url(r'^about/teacher$', views.AboutTeacher.as_view(), name='about_teacher'),

    url(r'^initiate_roles/$', views.initiate_roles, name='initiate_roles'),

    url(r'^admin/', include('ComSemApp.admin.urls', namespace='admin')),
    url(r'^teacher/', include('ComSemApp.teacher.urls', namespace='teacher')),
    url(r'^student/', include('ComSemApp.student.urls', namespace='student')),
    url(r'^corpus/', include('ComSemApp.corpus.urls', namespace='corpus')),
]
