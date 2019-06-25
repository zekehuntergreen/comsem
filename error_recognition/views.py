from django.views.generic.base import TemplateView


class ErrorRecognitionTestWelcome(TemplateView):
    template_name = "error_recognition/welcome.html"
