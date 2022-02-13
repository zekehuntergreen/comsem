from django.conf.urls import url
from ComSemApp.teacher import views
from ComSemApp.corpus import views as corpus_views

app_name = 'teacher'
urlpatterns = [
    url(r'^$', views.CourseListView.as_view(), name='courses'),
    url(r'^course/(?P<course_id>[0-9]+)/$', views.CourseDetailView.as_view(), name='course'),
    url(r'^course/(?P<course_id>[0-9]+)/download$', views.DownloadCourseCSV.as_view(), name='download_course_csv'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/create/$', views.WorksheetCreateView.as_view(), name='worksheet_create'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/list/$', views.WorksheetListView.as_view(), name='worksheet_list'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/$', views.WorksheetDetailView.as_view(), name='worksheet_detail'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/update/$', views.WorksheetUpdateView.as_view(), name='worksheet_update'),

    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/update_released/$', views.WorksheetReleasedUpdateView.as_view(), name='worksheet_released_update'),
    
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/release/$', views.WorksheetReleaseView.as_view(), name='worksheet_release'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/delete/$', views.WorksheetDeleteView.as_view(), name='worksheet_delete'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expressions/$', views.ExpressionListView.as_view(), name='expressions'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expression/create/$', views.ExpressionCreateView.as_view(), name='expression_create'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expression/(?P<expression_id>[0-9]+)/update/$', views.ExpressionUpdateView.as_view(), name='expression_update'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/expression/(?P<expression_id>[0-9]+)/delete/$', views.ExpressionDeleteView.as_view(), name='expression_delete'),
    url(r'^course/(?P<course_id>[0-9]+)/worksheet/(?P<worksheet_id>[0-9]+)/submission/(?P<submission_id>[0-9]+)/$', views.SubmissionView.as_view(), name='submission'),

    url(r'^corpus/search$', corpus_views.corpus_search, name='corpus_search'),
    url(r'^corpus/error_search$', corpus_views.error_search, name='error_search'),
]
