from .models import Admin, Teacher, Student
from django.conf import settings
from django.urls import reverse

# info to be displayed in dropdown menu - user's roles.
def user_info(request):
    available_roles = {}
    current_role = ''
    minton_style = 'blue-vertical'

    if request.user.is_authenticated:

        if Admin.objects.filter(user=request.user).exists():
            current = request.path.startswith('/admin/')
            if current:
                current_role = 'admin'
                minton_style = 'blue-vertical-dark'
            available_roles['admin'] = reverse("admin:home")
        if Teacher.objects.filter(user=request.user).exists():
            current = request.path.startswith('/teacher/')
            if current:
                current_role = 'teacher'
                minton_style = 'blue-vertical'
            available_roles['teacher'] = reverse("teacher:courses")
        if Student.objects.filter(user=request.user).exists():
            current = request.path.startswith('/student/')
            if current:
                current_role = 'student'
                minton_style = 'green-vertical'
            available_roles['student'] = reverse("student:courses")

    return {
        "available_roles": available_roles,
        "current_role": current_role,
        "minton_style": minton_style,
        "live": settings.LIVE,
    }
