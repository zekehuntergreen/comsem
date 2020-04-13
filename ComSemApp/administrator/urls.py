from django.conf.urls import url
from ComSemApp.administrator import views
from ComSemApp.corpus import views as corpus_views

app_name = 'admin'
urlpatterns = [
    url(r'^$', views.TeacherListView.as_view(), name='home'),

    url(r'^teachers/$', views.TeacherListView.as_view(), name='teachers'),
    url(r'^teacher/create/$', views.TeacherCreateView.as_view(), name='create_teacher'),
    url(r'^teacher/(?P<pk>[0-9]+)/$', views.TeacherUpdateView.as_view(), name='edit_teacher'),
    url(r'^teacher/(?P<pk>[0-9]+)/delete/$', views.TeacherDisactivateView.as_view(), name='disactivate_teacher'),

    url(r'^students/$', views.StudentListView.as_view(), name='students'),
    url(r'^student/create/$', views.StudentCreateView.as_view(), name='create_student'),
    url(r'^student/(?P<pk>[0-9]+)/$', views.StudentUpdateView.as_view(), name='edit_student'),
    url(r'^student/(?P<pk>[0-9]+)/reset-password/$', views.StudentResetPassword.as_view(), name='reset_student_password'),
    url(r'^student/(?P<pk>[0-9]+)/delete/$', views.StudentDisactivateView.as_view(), name='disactivate_student'),

    url(r'^courses/$', views.CourseListView.as_view(), name='courses'),
    url(r'^course/create/$', views.CourseCreateView.as_view(), name='create_course'),
    url(r'^course/(?P<pk>[0-9]+)/$', views.CourseUpdateView.as_view(), name='edit_course'),

    url(r'^course_types/$', views.CourseTypeListView.as_view(), name='course_types'),
    url(r'^course_type/create/$', views.CourseTypeCreateView.as_view(), name='create_course_type'),
    url(r'^course_type/(?P<pk>[0-9]+)/$', views.CourseTypeUpdateView.as_view(), name='edit_course_type'),

    url(r'^sessions/$', views.SessionListView.as_view(), name='sessions'),
    url(r'^session/create/$', views.SessionCreateView.as_view(), name='create_session'),
    url(r'^session/(?P<pk>[0-9]+)/$', views.SessionUpdateView.as_view(), name='edit_session'),

    url(r'^session_types/$', views.SessionTypeListView.as_view(), name='session_types'),
    url(r'^session_type/create/$', views.SessionTypeCreateView.as_view(), name='create_session_type'),
    url(r'^session_type/(?P<pk>[0-9]+)/$', views.SessionTypeUpdateView.as_view(), name='edit_session_type'),

    url(r'^corpus/search$', corpus_views.corpus_search, name='corpus_search'),
]
