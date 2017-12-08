from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Admin, Teacher, Student

def index(request):
    return HttpResponse("<b>Communication Seminar</b> index.")

# called when user logs in, puts current role in session
@login_required
def initiate_roles(request):
    if Admin.objects.filter(user=request.user).exists():
        return redirect('/admin/')

    if Teacher.objects.filter(user=request.user).exists():
        return redirect('/teacher/')

    if Student.objects.filter(user=request.user).exists():
        return redirect('/student/')
