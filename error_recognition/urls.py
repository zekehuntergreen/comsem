from django.urls import path

from . import views


app_name = "error_recognition"
urlpatterns = [
    path('', views.ErrorRecognitionTestWelcome.as_view(), name='welcome'),
]
