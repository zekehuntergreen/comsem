from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template import loader
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


from .models import Admin, Teacher, Student

# home page
def index(request):
    template = loader.get_template('ComSemApp/home.html')
    return HttpResponse(template.render({}, request))


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('initiate_roles')
        else:
            messages.error(request, 'Please correct the above error.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ComSemApp/standard_form.html', {
        'form': form,
        'page_title': 'Change Password'
    })

# called when user logs in, puts current role in session
@login_required
def initiate_roles(request):
    if Admin.objects.filter(user=request.user).exists():
        return redirect('/admin/')

    if Teacher.objects.filter(user=request.user).exists():
        return redirect('/teacher/')

    if Student.objects.filter(user=request.user).exists():
        return redirect('/student/')
