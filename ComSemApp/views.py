import requests

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .models import Admin, Teacher, Student
from ComSemApp.administrator.forms import SignupForm, ContactForm

# TODO - these are the sort of extra views that don't exactly fit into one of the existing "apps"
# and should be reorganized and tested


class RecaptchaFormView(FormView):
    success_message = None

    def _verify_recaptcha(self):
        params = {
            'secret': settings.RECAPCHA_SECRET_KEY,
            'response': self.request._post['g-recaptcha-response'],
        }
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', params)
        response_json = response.json()
        return response_json.get('success')

    def form_valid(self, form):
        recaptcha_success = self._verify_recaptcha()
        if recaptcha_success:
            form.send_email()
            messages.success(self.request, self.success_message)
        else:
            messages.error(self.request, 'There was a problem processing your request.')
        return super().form_valid(form)


class About(RecaptchaFormView):
    template_name = 'ComSemApp/about/home.html'
    form_class = SignupForm
    success_url = reverse_lazy("about")
    success_message = ('Your request has been sent successfully! '
                        'We will contact you shortly to set up an account.')


class Contact(RecaptchaFormView):
    template_name = 'ComSemApp/about/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy("about")
    success_message = ('Your message has been sent successfully!')


class AboutTeacher(TemplateView):
    template_name = "ComSemApp/about/teacher.html"


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
        return redirect('/administrator/')

    if Teacher.objects.filter(user=request.user).exists():
        return redirect('/teacher/')

    if Student.objects.filter(user=request.user).exists():
        return redirect('/student/')


# error annotation drop down boxes
@login_required
def error_search(request):
    tags = Tag.object.all()
    errors = ErrorCategory.objects.all()
    template = loader.get_template('ComSemApp') # TODO: we do not have a template yet
    return HttpResponse(template.render({'tags': tags, 'errors': errors, 'offsetRange': [i for i in range(-8, 8+i)]}, request))

@login_required
def subcategories(request):
    error_type = request.GET['err']
    result_set = []
    all_subcategories = []
    answer = str(error_type[1:-1])
    selected_error = ErrorCategory.objects.get(category=answer)
    all_subcategories = selected_error.errorsubcategory_set.all()
    for subs in all_subcategories:
        result_set.append({'name': subs.subcategory})
    return HttpResponse(json.dumps(result_set), content_type='application/json')