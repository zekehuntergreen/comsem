from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template import loader
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail



from .models import Admin, Teacher, Student
from .forms import SignupForm

# home page
def index(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # send a message to us
            email = form.cleaned_data['email']

            message = "Somebody has requested to join Communications Seminar!\nHere is their info:\n\n"

            for key in form.cleaned_data.keys():
                message += "\t" + key + ": " + form.cleaned_data[key] + "\n"

            recipients = ['hunter@gonzaga.edu']

            send_mail("Request to join ComSem", message, email, recipients)

            # send them a confirmation message ?


            form = SignupForm() # clear the form

            messages.success(request, 'Your form has been sent successfully!')
        else:
            messages.error(request, 'Please correct the above error.')
    else:
        form = SignupForm()

    return render(request, 'ComSemApp/home.html', {
        'form': form,
    })


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
