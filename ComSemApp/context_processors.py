from .models import Admin, Teacher, Student

# info to be displayed in dropdown menu - user's roles.
def user_info(request):
    if request.user.is_authenticated:
        user_info = {}
        if Admin.objects.filter(user=request.user).exists():
            user_info['admin'] = {
                'current': request.path.startswith('/admin/'),
            }
        if Teacher.objects.filter(user=request.user).exists():
            user_info['teacher'] = {
                'current': request.path.startswith('/teacher/'),
            }
        if Student.objects.filter(user=request.user).exists():
            user_info['student'] = {
                'current': request.path.startswith('/student/'),
            }

        return {'user_info': user_info}
    else:
        return {}
