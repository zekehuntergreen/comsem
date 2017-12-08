from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from .models import Student

# TESTS
def is_student(user):
    return Student.objects.filter(user=user).exists()

def student(request):
    return HttpResponse("<b>Student home</b>.")
