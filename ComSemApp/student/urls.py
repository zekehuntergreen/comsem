from django.conf.urls import url
from ComSemApp.student import views
from ComSemApp.discussionBoard import view as discussion_views

app_name = 'student'
urlpatterns = [
    url(r'^$', views.CourseListView.as_view(), name='courses'),

    # url(r'^course/googleTranscribe/$', views.googleTranscribe, name="googleTranscribe"),

    url(r'^course/(?P<course_id>[0-9]+)/$', views.CourseDetailView.as_view(), name='course'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/list/$', views.SubmissionListView.as_view(), name='submission_list'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/create/$', views.SubmissionCreateView.as_view(), name='create_submission'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/update/$', views.SubmissionUpdateView.as_view(), name='update_submission'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/expressions/$', views.ExpressionListView.as_view(), name='worksheet_expression_list'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/expression/(?P<expression_id>[0-9]+)/create/$', views.AttemptCreateView.as_view(), name='create_attempt'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/attempt/(?P<attempt_id>[0-9]+)/update/$', views.AttemptUpdateView.as_view(), name='update_attempt'),
    url(r'^discussion_board$', discussion_views.TopicListView.as_view(), name='student_discussion_board'),
    url(r'^topic/(?P<topic_id>[0-9]+)/$', discussion_views.ReplyView.as_view(), name='student_topic'),
    url(r'^newtopic/$', discussion_views.CreateThreadView.as_view(),name='student_create_topic')
]
