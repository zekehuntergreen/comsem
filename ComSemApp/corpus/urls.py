from django.conf.urls import url
from ComSemApp.admin import views
from ComSemApp.corpus import views

app_name = 'admin'
urlpatterns = [
    url(r'^populate_word_tag/$', views.populate_word_tag, name='populate_word_tag'),
    url(r'^search_results/$', views.search_results, name='search_results'),

    # url(r'^corpus/stats$', views.corpus_stats, name='corpus_stats'),
]