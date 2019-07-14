from django.urls import path

from . import views


app_name = "error_recognition"
urlpatterns = [
    path('error-recognition/', views.WelcomeView.as_view(), name='welcome'),
    path('l1', views.TestL1View.as_view(), name='l1'),  # no trailing slash !
    path('l2', views.TestL2View.as_view(), name='l2'),  # same !
]
