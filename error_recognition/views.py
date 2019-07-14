from django.views.generic.base import TemplateView


class WelcomeView(TemplateView):
    template_name = "error_recognition/welcome.html"


class TestL1View(TemplateView):
    template_name = "error_recognition/l1.html"


class TestL2View(TemplateView):
    template_name = "error_recognition/l2.html"

