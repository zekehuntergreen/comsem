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

from django.http import JsonResponse
from .api_keys import API_KEY, YOUTUBE_API_KEY

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

    
def youglish_proxy(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        skip = request.GET.get('skip', 0)
        max = request.GET.get('max', 10)

        youglish_url = f'https://youglish.com/api/v1/videos/search?key={API_KEY}&query={query}&lg=english&max={max}&skip={skip}'

        try:
            # Make a GET request to the Youglish API using requests
            response = requests.get(youglish_url)
            data = response.json()

            # Add YouTube video details to each video result
            for video in data['results']:
                video_id = video['vid']
                video_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={YOUTUBE_API_KEY}&part=snippet'
                youtube_response = requests.get(video_url).json()
                video['title'] = youtube_response['items'][0]['snippet']['title']
                video['thumbnail'] = youtube_response['items'][0]['snippet']['thumbnails']['default']['url']

            # Return the response data as a JSON object to the client
            return JsonResponse(data)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'An error occurred while fetching data from Youglish API'})

    return JsonResponse({'error': 'Invalid Request'})
