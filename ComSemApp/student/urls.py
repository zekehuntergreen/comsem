from django.conf.urls import url
from ComSemApp.student import views

app_name = 'student'
urlpatterns = [
    url(r'^$', views.CourseListView.as_view(), name='courses'),
    url(r'^course/(?P<course_id>[0-9]+)/$', views.CourseDetailView.as_view(), name='course'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/list/$', views.SubmissionListView.as_view(), name='submission_list'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/create/$', views.SubmissionCreateView.as_view(), name='create_submission'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/update/$', views.SubmissionUpdateView.as_view(), name='update_submission'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/expressions/$', views.ExpressionListView.as_view(), name='worksheet_expression_list'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/expression/(?P<expression_id>[0-9]+)/create/$', views.AttemptCreateView.as_view(), name='create_attempt'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/attempt/(?P<attempt_id>[0-9]+)/update/$', views.AttemptUpdateView.as_view(), name='update_attempt'),
    # reviewsheet is the reading and listening practice tool
    url(r'^course/(?P<course_id>[0-9]+)/reviewsheet/generator/$', views.ReviewsheetGeneratorView.as_view(), name='generate_reviewsheet'),
    url(r'^course/(?P<course_id>[0-9]+)/reviewsheet/$', views.ReviewsheetGetView.as_view(), name='create_reviewsheet'),
    url(r'^course/(?P<course_id>[0-9]+)/reviewsheet/$', views.ReviewsheetView.as_view(), name='reviewsheet'),
    url(r'^course/(?P<course_id>[0-9]+)/reviewsheet/save$', views.ReviewAttemptCreateView.as_view(), name='save_reviewsheet'),
    # speakingpractice is the speaking practice tool
    url(r'^course/(?P<course_id>[0-9]+)/speakingpractice/$', views.SpeakingPracticeView.as_view(), name='speaking_practice'),
    url(r'^course/(?P<course_id>[0-9]+)/speakingpractice/generator/$', views.SpeakingPracticeGeneratorView.as_view(), name='speaking_practice_generator'),
    url(r'^course/(?P<course_id>[0-9]+)/speakingpractice/results/$', views.SpeakingPracticeResultsView.as_view(), name='speaking_practice_results'),
    url(r'^course/(?P<course_id>[0-9]+)/speakingpractice/instructions/$', views.SpeakingPracticeInstructionsView.as_view(), name='speaking_practice_instructions'),
    url(r'^course/(?P<course_id>[0-9]+)/speakingpractice/save$', views.SpeakingPracticeAttemptCreateView.as_view(), name='speaking_practice_submit'),
    url(r'^course/(?P<course_id>[0-9]+)/speakingpractice/session$', views.SpeakingPracticeSessionCreateView.as_view(), name='speaking_practice_session_create'),
    url(r'^course/(?P<course_id>[0-9]+)/speakingpractice/request$', views.SpeakingPracticeTeacherReviewRequestCreateView.as_view(), name='speaking_practice_review_request')
]