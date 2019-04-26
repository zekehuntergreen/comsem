from django.conf.urls import url
from ComSemApp.discussionBoard import view

app_name = 'discussion_board'
urlpatterns = [
    url(r'^$', view.TopicListView.as_view(), name='topics'),
    url(r'^topic/(?P<topic_id>[0-9]+)/$', view.ReplyView.as_view(), name='topic'),
    url(r'^newtopic/$', view.CreateThreadView.as_view(),name='create_topic')
]