from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.http import JsonResponse
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.core.serializers import serialize
from django.contrib import messages
from django.conf import settings

from ComSemApp.teacher import constants
from ComSemApp.libs.mixins import RoleViewMixin, CourseViewMixin, WorksheetViewMixin

import json, math, datetime, os
from ComSemApp.models import *

import pickle
import tensorflow
from tensorflow import keras
from tensorflow.python.keras.preprocessing.text import Tokenizer
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

class TeacherViewMixin(RoleViewMixin):

    role_class = Teacher

    def _set_role_obj(self):
        # role_obj self in RoleViewMixin
        self.teacher = self.role_obj

    def _check_valid_course(self, course_id):
        courses = Course.objects.filter(teachers=self.request.user.teacher, id=course_id)
        if not courses.exists():
            return False
        return courses.first()


class TeacherCourseViewMixin(TeacherViewMixin, CourseViewMixin):

    def _get_invalid_course_redirect(self):
        return HttpResponseRedirect(reverse("teacher:courses"))


class TeacherWorksheetViewMixin(TeacherViewMixin, WorksheetViewMixin):

    def _get_invalid_worksheet_redirect(self):
        return HttpResponseRedirect(reverse("teacher:course", kwargs={"course_id": self.course.id}))


class CourseListView(TeacherViewMixin, ListView):
    # teacher home page
    model = Course
    template_name = 'ComSemApp/teacher/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(teachers=self.request.user.teacher)

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        context['teacher_view'] = True
        return context


class CourseDetailView(TeacherCourseViewMixin, DetailView):
    context_object_name = 'course'
    template_name = "ComSemApp/teacher/course.html"

    def get_object(self):
        return self.course


class WorksheetListView(TeacherCourseViewMixin, ListView):
    model = Worksheet
    template_name = 'ComSemApp/teacher/worksheet_list.html'
    context_object_name = 'worksheets'

    def get_queryset(self):
        return self.course.get_visible_worksheets()


class WorksheetDetailView(TeacherWorksheetViewMixin, DetailView):
    template_name = 'ComSemApp/teacher/view_worksheet.html'
    context_object_name = 'worksheet'

    def get_object(self):
        return self.worksheet

    def get_context_data(self, **kwargs):
        context = super(WorksheetDetailView, self).get_context_data(**kwargs)
        context['submissions'] = self.worksheet.submissions.exclude(status="pending")
        return context


class WorksheetCreateView(TeacherCourseViewMixin, UpdateView):
    model = Worksheet
    fields = ["topic", "display_original", "display_reformulation_text",
                "display_reformulation_audio", "display_all_expressions"]
    template_name = "ComSemApp/teacher/edit_worksheet.html"

    # technically an UpdateView since a worksheet object with status PENDING is created in the get_object method
    def get_object(self):
        worksheet, created = Worksheet.objects.get_or_create_pending(self.teacher, self.course)
        return worksheet

    def form_valid(self, form):
        self.object.status = constants.WORKSHEET_STATUS_UNRELEASED
        return super(WorksheetCreateView,self).form_valid(form)

    def get_success_url(self):
        return reverse("teacher:course", kwargs={'course_id': self.course.id })


class WorksheetUpdateView(TeacherWorksheetViewMixin, UpdateView):
    model = Worksheet
    fields = ["topic", "display_original", "display_reformulation_text",
                "display_reformulation_audio", "display_all_expressions"]
    template_name = "ComSemApp/teacher/edit_worksheet.html"
    context_object_name = 'worksheet'

    def get_object(self):
        return self.worksheet

    def get_success_url(self):
        return reverse("teacher:course", kwargs={'course_id': self.course.id })

# new view class for released worksheets being edited DF
class WorksheetReleasedUpdateView(TeacherWorksheetViewMixin, UpdateView):
    model = Worksheet
    fields = ["topic", "display_original", "display_reformulation_text",
                "display_reformulation_audio", "display_all_expressions"]
    template_name = "ComSemApp/teacher/edit_released_worksheet.html" #edit_worksheet.html -> edit_released_worksheet.html
    context_object_name = 'worksheet'

    def get_object(self):
        return self.worksheet

    def get_success_url(self):
        return reverse("teacher:course", kwargs={'course_id': self.course.id })


class WorksheetReleaseView(TeacherWorksheetViewMixin, View):
    model = Worksheet

    def get_object(self):
        return get_object_or_404(Worksheet, id=self.worksheet.id)

    def post(self, *args, **kwargs):
        worksheet = self.get_object()
        is_valid = worksheet.release()
        if is_valid: # vhl release if worksheet is not empty
            return HttpResponse(status=204)
        else: # vhl returns error message if worksheet is empty
            return HttpResponse(status=406, reason="worksheet cannot be empty")


class WorksheetDeleteView(TeacherWorksheetViewMixin, DeleteView):
    model = Worksheet

    def get_object(self):
        return get_object_or_404(Worksheet, id=self.worksheet.id, status=constants.WORKSHEET_STATUS_UNRELEASED)

    def post(self, *args, **kwargs):
        worksheet = self.get_object()
        worksheet.delete()
        return HttpResponse(status=204)


class ExpressionListView(TeacherWorksheetViewMixin, ListView):
    model = Expression
    template_name = "ComSemApp/teacher/expressions.html"
    context_object_name = 'expressions'

    def get_queryset(self):
        return Expression.objects.filter(worksheet=self.worksheet)


class ExpressionCreateView(TeacherWorksheetViewMixin, CreateView):
    model = Expression
    template_name = "ComSemApp/teacher/expression_form.html"
    fields = ["expression", "student", "all_do", "pronunciation", "context_vocabulary",
                "reformulation_text", "audio"]

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        expression = form.save(commit=False)
        expression.worksheet = self.worksheet
        expression.save()
        return JsonResponse({}, status=200)


class ExpressionUpdateView(TeacherWorksheetViewMixin, UpdateView):
    model = Expression
    template_name = "ComSemApp/teacher/expression_form.html"
    fields = ["expression", "student", "all_do", "pronunciation", "context_vocabulary",
                "reformulation_text", "audio"]

    def get_object(self):
        expression_id = self.kwargs.get('expression_id', None)
        expressions = Expression.objects.filter(id=expression_id, worksheet=self.worksheet)
        if not expressions.exists():
            # only ajax right now
            response = JsonResponse({"error": 'Invalid Expression ID.'})
            response.status_code = 403
            return response
        return expressions.first()

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        expression = form.save()
        # delete audio field manually if it's not in the form data
        # why should we have to do this ?
        if 'delete_audio' in form.data:
            expression.audio = None
            expression.save()
        return JsonResponse({}, status=200)


class ExpressionDeleteView(TeacherWorksheetViewMixin, DeleteView):
    model = Expression

    def get_object(self):
        expression_id = self.kwargs.get('expression_id', None)
        expressions = Expression.objects.filter(id=expression_id, worksheet=self.worksheet)
        if not expressions.exists():
            # only ajax right now
            response = JsonResponse({"error": 'Invalid Expression ID.'})
            response.status_code = 403
            return response
        return expressions.first()

    def post(self, *args, **kwargs):
        expression = self.get_object()
        audio = expression.audio
        # delete audio file if it exists
        # TODO override model's delete method
        if audio:
            delete_file(audio.url)
        expression.delete()
        return HttpResponse(status=204)


class SubmissionView(TeacherWorksheetViewMixin, DetailView):
    template_name = "ComSemApp/teacher/view_submission.html"
    context_object_name = "submission"

    def get_object(self): # gets submission object and runs it through neural net
        submission_id = self.kwargs.get('submission_id', None)
        submission = get_object_or_404(StudentSubmission, id=submission_id, worksheet=self.worksheet)

        # open subject verb tokenizer
        with open('ComSemApp/ML/tokenizer.pickle', 'rb') as handle:
            tokenizer_sv = pickle.load(handle)
    
        # load subject verb error binary neural network
        new_model_sv = keras.models.load_model('ComSemApp/ML/pickled_binary_nn')

        # open tense tokenizer
        with open('ComSemApp/ML/tense_tokenizer.pickle', 'rb') as handle:
            tokenizer_tense = pickle.load(handle)

        # load tense error binary neural network
        new_model_tense = keras.models.load_model('ComSemApp/ML/pickled_tense_nn')


        # open noun phrase tokenizer
        with open('ComSemApp/ML/np_tokenizer.pickle', 'rb') as handle:
            tokenizer_np = pickle.load(handle)
        # load noun phrase binary neural network
        new_model_np = keras.models.load_model('ComSemApp/ML/pickled_np_nn')


        for attempt in submission.attempts.all():
            sv_classifier = 0 
            tense_classifier = 0 
            noun_phrase_classifier = 0
            final_classifier = ""

            # example input text
            text = attempt.reformulation_text

            # text must be placed in an array in order to be manipulated by tokenzier
            text_array = [text]
            print("\n")
            print(text)

            # tokenize text
            tokens_sv = tokenizer_sv.texts_to_sequences(text_array)

            # add padding to text to compare the text properly
            tokens_pad_sv = pad_sequences(tokens_sv,maxlen=39, padding='pre', truncating='pre')
            tokens_pad_sv.shape

            # print example of confidence that there is a sv agreement error in text
            print(new_model_sv.predict(tokens_pad_sv)[0][0])

            # less than 0.5 means it contains no error, greater than 0.5 means it does contain sv error
            if new_model_sv.predict(tokens_pad_sv)[0][0] > 0.5:
                sv_classifier =  new_model_sv.predict(tokens_pad_sv)[0][0]

            # print the sv classifier
            print("subject verb agreement error confidence ", sv_classifier)


            # tokenize text
            tokens_tense = tokenizer_tense.texts_to_sequences(text_array)

            # add padding to text to compare the text properly
            tokens_pad_tense = pad_sequences(tokens_tense,maxlen=39, padding='pre', truncating='pre')
            tokens_pad_tense.shape

            #print example of confidence that there is a tense error in text
            print(new_model_tense.predict(tokens_pad_tense)[0][0])

            # less than 0.5 means it contains no error, greater than 0.5 means it does contain a tense error
            if new_model_tense.predict(tokens_pad_tense)[0][0] > 0.5:
                tense_classifier =  new_model_tense.predict(tokens_pad_tense)[0][0]

            # print the tense classifier
            print("subject tense error confidence ", tense_classifier)

            # tokenize text
            tokens_np = tokenizer_np.texts_to_sequences(text_array)

            # add padding to text to compare the text properly
            tokens_pad_np = pad_sequences(tokens_np,maxlen=46, padding='pre', truncating='pre')
            tokens_pad_np.shape

            # print example of confidence that there is a np agreement error in text
            print(new_model_np.predict(tokens_pad_np)[0][0])

            # less than 0.5 means it contains no error, greater than 0.5 means it does contain np error
            if new_model_np.predict(tokens_pad_np)[0][0] > 0.5:
                noun_phrase_classifier =  new_model_np.predict(tokens_pad_np)[0][0]

            # print the noun phrase classifier
            print("noun phrase confidence ", noun_phrase_classifier)

            # compare confidence of each classifier and determine which has the highest confidence value
            if (sv_classifier > 0.5):
               final_classifier += "Chance of SV: " + "{:.2%}".format(sv_classifier) + " "

            if (tense_classifier > 0.5):
               final_classifier += "Chance of Tense: " + "{:.2%}".format(tense_classifier) + " "

            if (noun_phrase_classifier > 0.5):
               final_classifier += "Chance of NP: " + "{:.2%}".format(noun_phrase_classifier)

            if (len(final_classifier) == 0): # if final_classifier has a len of 0 no errors where detected
                final_classifier = "No errors have been detected"

            attempt.error_type = final_classifier # vhl update ml error type
            attempt.save()

        return submission 

    def get_submission(self):
        submission_id = self.kwargs.get('submission_id', None)
        return get_object_or_404(StudentSubmission, id=submission_id, worksheet=self.worksheet)

    def post(self, *args, **kwargs): # vhl determines whether a student submission is complete after a teacher grades it
        submission = self.get_submission()
        
        all_correct = True 
        # status of each attempt 
        for attempt in submission.attempts.all(): # added code to allow audio and text to be graded seperatly vhl
            text_correct = self.request.POST.get("T" + str(attempt.id), None) == '1' # get text
            is_audio = self.request.POST.get("A" + str(attempt.id)) is not None # checks for audio
            audio_correct = self.request.POST.get("A" + str(attempt.id), None) == '1' # gets audio
            
            
            attempt.correct = text_correct # marks text
            if is_audio: # adds audio if necessary
                attempt.audio_correct = audio_correct
            else: # adds None if there is not audio present
                attempt.audio_correct = None
            attempt.save()
            if is_audio: # case for if there is audio
                if (not text_correct) or (not audio_correct):
                    all_correct = False
            else: # case for text only
                if (not text_correct):
                    all_correct = False
                
        # handle status of the submission
        # TODO - use constants
        if all_correct:
            submission.status = 'complete'
        else:
            submission.status = 'incomplete'

        submission.save()

        messages.success(self.request, 'Assessment saved ', 'success')
        return redirect('teacher:worksheet_detail', self.course.id, self.worksheet.id)


def delete_file(url):
    try:
        os.remove(url)
    except FileNotFoundError:
        pass
