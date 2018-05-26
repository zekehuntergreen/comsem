from django.conf.urls import url

from . import views, admin_views, teacher_views, student_views, corpus_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^initiate_roles/$', views.initiate_roles, name='initiate_roles'),

    # ADMIN
    url(r'^admin/$', admin_views.admin, name='admin'),

    url(r'^admin/teachers/$', admin_views.TeacherList.as_view(), name='admin_teachers'),
    url(r'^admin/teacher/create/$', admin_views.TeacherCreate.as_view(), name='admin_create_teacher'),
    url(r'^admin/teacher/(?P<pk>[0-9]+)/$', admin_views.TeacherUpdate.as_view(), name='admin_edit_teacher'),

    url(r'^admin/students/$', admin_views.StudentList.as_view(), name='admin_students'),
    url(r'^admin/student/create/$', admin_views.StudentCreate.as_view(), name='admin_create_student'),
    url(r'^admin/student/(?P<pk>[0-9]+)/$', admin_views.StudentUpdate.as_view(), name='admin_edit_student'),

    url(r'^admin/courses/$', admin_views.CourseList.as_view(), name='admin_courses'),
    url(r'^admin/course/create/$', admin_views.CourseCreate.as_view(), name='admin_create_course'),
    url(r'^admin/course/(?P<pk>[0-9]+)/$', admin_views.CourseUpdate.as_view(), name='admin_edit_course'),

    url(r'^admin/course_types/$', admin_views.CourseTypeList.as_view(), name='admin_course_types'),
    url(r'^admin/course_type/create/$', admin_views.CourseTypeCreate.as_view(), name='admin_create_course_type'),
    url(r'^admin/course_type/(?P<pk>[0-9]+)/$', admin_views.CourseTypeUpdate.as_view(), name='admin_edit_course_type'),

    url(r'^admin/sessions/$', admin_views.SessionList.as_view(), name='admin_sessions'),
    url(r'^admin/session/create/$', admin_views.SessionCreate.as_view(), name='admin_create_session'),
    url(r'^admin/session/(?P<pk>[0-9]+)/$', admin_views.SessionUpdate.as_view(), name='admin_edit_session'),

    url(r'^admin/session_types/$', admin_views.SessionTypeList.as_view(), name='admin_session_types'),
    url(r'^admin/session_type/create/$', admin_views.SessionTypeCreate.as_view(), name='admin_create_session_type'),
    url(r'^admin/session_type/(?P<pk>[0-9]+)/$', admin_views.SessionTypeUpdate.as_view(), name='admin_edit_session_type'),




    url(r'^admin/edit/([\w_]+)/([0-9]+)/$', admin_views.edit_obj, name='admin_edit_obj'),
    url(r'^admin/delete_obj/([\w_]+)/([0-9]+)/$', admin_views.delete_obj, name='admin_delete_obj'),



    # TEACHER
    url(r'^teacher/$', teacher_views.teacher, name='teacher'),
    url(r'^teacher/course/([0-9]+)/$', teacher_views.course, name='teacher_course'),
    url(r'^teacher/course/([0-9]+)/worksheet/([0-9]+)/$', teacher_views.worksheet, name='teacher_worksheet'),
    url(r'^teacher/course/([0-9]+)/worksheet/([0-9]+)/submission/([0-9]+)/$', teacher_views.submission, name='teacher_submission'),

    url(r'^ajax/course_students/$', teacher_views.course_students, name='course_students'),
    url(r'^ajax/save_worksheet/$', teacher_views.save_worksheet, name='save_worksheet'),
    url(r'^ajax/delete_worksheet/$', teacher_views.delete_worksheet, name='delete_worksheet'),
    url(r'^ajax/release_worksheet/$', teacher_views.release_worksheet, name='release_worksheet'),


    # STUDENT
    url(r'^student/$', student_views.student, name='student'),
    url(r'^student/course/([0-9]+)/$', student_views.course, name='student_course'),
    url(r'^student/worksheet/([0-9]+)/$', student_views.worksheet, name='student_worksheet'),

    url(r'^ajax/save_submission/$', student_views.save_submission, name='save_submission'),


    # CORPUS
    url(r'^teacher/corpus/search$', corpus_views.corpus_search, name='teacher_corpus_search'),
    url(r'^admin/corpus/search$', corpus_views.corpus_search, name='admin_corpus_search'),
    url(r'^ajax/populate_word_tag/$', corpus_views.populate_word_tag, name='populate_word_tag'),
    url(r'^ajax/search_results/$', corpus_views.search_results, name='search_results'),

    # url(r'^corpus/stats$', corpus_views.corpus_stats, name='corpus_stats'),
]
