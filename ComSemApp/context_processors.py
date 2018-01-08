from .models import Admin, Teacher, Student

# info to be displayed in dropdown menu - user's roles.
def user_info(request):
    user_info = {}
    current_role = ''
    minton_style = 'blue-vertical'

    if request.user.is_authenticated:

        if Admin.objects.filter(user=request.user).exists():
            current = request.path.startswith('/admin/')
            if current:
                current_role = 'admin'
                minton_style = 'blue-vertical-dark'
            user_info['admin'] = {
                'current': current,
            }
        if Teacher.objects.filter(user=request.user).exists():
            current = request.path.startswith('/teacher/')
            if current:
                current_role = 'admin'
                minton_style = 'blue-vertical'
            user_info['teacher'] = {
                'current': current,
            }
        if Student.objects.filter(user=request.user).exists():
            current = request.path.startswith('/student/')
            if current:
                current_role = 'admin'
                minton_style = 'green-vertical'
            user_info['student'] = {
                'current': current,
            }

    return {'user_info': user_info, "current_role": current_role, "minton_style": minton_style}
