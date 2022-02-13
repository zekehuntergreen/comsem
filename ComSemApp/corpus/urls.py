from django.conf.urls import url
from ComSemApp.corpus import views

app_name = 'corpus'
urlpatterns = [
    url(r'^populate_word_tag/$', views.populate_word_tag, name='populate_word_tag'),
    url(r'^search_results/$', views.search_results, name='search_results'),

    url(r'^get_error_sub/', views.subcategories, name='get_error_sub'),
    url(r'^error_search_results/$', views.error_search_results,
        name='error_search_results'),

]
