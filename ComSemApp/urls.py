from django.conf.urls import url

from . import views, admin_views, teacher_views, student_views, corpus_views

urlpatterns = [
    url(r'^$', views.about, name='about'),
    url(r'^about/teacher$', views.AboutTeacher.as_view(), name='about_teacher'),

    url(r'^initiate_roles/$', views.initiate_roles, name='initiate_roles'),

    # ADMIN
    url(r'^admin/$', admin_views.StudentListView.as_view(), name='admin'),

    url(r'^admin/teachers/$', admin_views.TeacherListView.as_view(), name='admin_teachers'),
    url(r'^admin/teacher/create/$', admin_views.TeacherCreateView.as_view(), name='admin_create_teacher'),
    url(r'^admin/teacher/(?P<pk>[0-9]+)/$', admin_views.TeacherUpdateView.as_view(), name='admin_edit_teacher'),
    url(r'^admin/teacher/(?P<pk>[0-9]+)/delete/$', admin_views.TeacherDisactivateView.as_view(), name='admin_disactivate_teacher'),

    url(r'^admin/students/$', admin_views.StudentListView.as_view(), name='admin_students'),
    url(r'^admin/student/create/$', admin_views.StudentCreateView.as_view(), name='admin_create_student'),
    url(r'^admin/student/(?P<pk>[0-9]+)/$', admin_views.StudentUpdateView.as_view(), name='admin_edit_student'),
    url(r'^admin/student/(?P<pk>[0-9]+)/delete/$', admin_views.StudentDisactivateView.as_view(), name='admin_disactivate_student'),

    url(r'^admin/courses/$', admin_views.CourseListView.as_view(), name='admin_courses'),
    url(r'^admin/course/create/$', admin_views.CourseCreateView.as_view(), name='admin_create_course'),
    url(r'^admin/course/(?P<pk>[0-9]+)/$', admin_views.CourseUpdateView.as_view(), name='admin_edit_course'),
    url(r'^admin/course/(?P<pk>[0-9]+)/delete/$', admin_views.CourseDeleteView.as_view(), name='admin_delete_course'),

    url(r'^admin/course_types/$', admin_views.CourseTypeListView.as_view(), name='admin_course_types'),
    url(r'^admin/course_type/create/$', admin_views.CourseTypeCreateView.as_view(), name='admin_create_course_type'),
    url(r'^admin/course_type/(?P<pk>[0-9]+)/$', admin_views.CourseTypeUpdateView.as_view(), name='admin_edit_course_type'),
    url(r'^admin/course_type/(?P<pk>[0-9]+)/delete/$', admin_views.CourseTypeDeleteView.as_view(), name='admin_delete_course_type'),

    url(r'^admin/sessions/$', admin_views.SessionListView.as_view(), name='admin_sessions'),
    url(r'^admin/session/create/$', admin_views.SessionCreateView.as_view(), name='admin_create_session'),
    url(r'^admin/session/(?P<pk>[0-9]+)/$', admin_views.SessionUpdateView.as_view(), name='admin_edit_session'),
    url(r'^admin/session/(?P<pk>[0-9]+)/delete/$', admin_views.SessionDeleteView.as_view(), name='admin_delete_session'),

    url(r'^admin/session_types/$', admin_views.SessionTypeListView.as_view(), name='admin_session_types'),
    url(r'^admin/session_type/create/$', admin_views.SessionTypeCreateView.as_view(), name='admin_create_session_type'),
    url(r'^admin/session_type/(?P<pk>[0-9]+)/$', admin_views.SessionTypeUpdateView.as_view(), name='admin_edit_session_type'),
    url(r'^admin/session_type/(?P<pk>[0-9]+)/delete/$', admin_views.SessionTypeDeleteView.as_view(), name='admin_delete_session_type'),


    # TEACHER
    url(r'^teacher/$', teacher_views.CourseListView.as_view(), name='teacher'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/$', teacher_views.CourseDetailView.as_view(), name='teacher_course'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/create/$', teacher_views.WorksheetCreateView.as_view(), name='teacher_worksheet_create'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/list/$', teacher_views.WorksheetListView.as_view(), name='teacher_worksheet_list'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/$', teacher_views.WorksheetDetailView.as_view(), name='teacher_worksheet_detail'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/update/$', teacher_views.WorksheetUpdateView.as_view(), name='teacher_worksheet_update'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/release/$', teacher_views.WorksheetReleaseView.as_view(), name='teacher_worksheet_release'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/delete/$', teacher_views.WorksheetDeleteView.as_view(), name='teacher_worksheet_delete'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expressions/$', teacher_views.ExpressionListView.as_view(), name='teacher_expressions'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expression/create/$', teacher_views.ExpressionCreateView.as_view(), name='teacher_expression_create'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expression/(?P<expression_id>[0-9]+)/update/$', teacher_views.ExpressionUpdateView.as_view(), name='teacher_expression_update'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expression/(?P<expression_id>[0-9]+)/delete/$', teacher_views.ExpressionDeleteView.as_view(), name='teacher_expression_delete'),
    url(r'^teacher/course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/$', teacher_views.SubmissionView.as_view(), name='teacher_submission'),



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
