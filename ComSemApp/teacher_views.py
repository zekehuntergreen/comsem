from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from django.shortcuts import render, redirect
from django.http import HttpResponse
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

from ComSemApp import teacher_constants

import json, math, datetime, os
from .models import *


# DECORATORS
def is_teacher(user):
    return Teacher.objects.filter(user=user).exists()

def teaches_course(func):
    def wrapper(request, *args, **kwargs):
        valid = Course.objects.filter(teachers=request.user.teacher, id=args[0]).exists()
        if not valid:
            messages.error(request, 'Invalid course ID.')
            return redirect("/teacher/")
        return func(request, *args, **kwargs)
    return wrapper


def teaches_course_ajax(func):
    def wrapper(request, *args, **kwargs):
        course_id = request.POST.get('course_id', None)
        worksheet_id = request.POST.get('worksheet_id', None)

        # might need to seach for courseid from worksheetid
        if worksheet_id and int(worksheet_id) > 0:
            course_id = get_object_or_404(Worksheet, id=worksheet_id).course.id

        valid = Course.objects.filter(teachers=request.user.teacher, id=course_id).exists()
        if not valid:
            response = JsonResponse({"error": 'Invalid course ID.'})
            response.status_code = 403
            return response
        return func(request, *args, **kwargs)
    return wrapper


class TeacherViewMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        # is the user a teacher?
        teacher = Teacher.objects.filter(user=self.request.user)
        if not teacher.exists():
            return False
        else:
            self.teacher = teacher.first()
            self.institution = self.teacher.institution
            return True

    def _check_valid_course(self, course_id):
        courses = Course.objects.filter(teachers=self.request.user.teacher, id=course_id)
        if not courses.exists():
            return False
        return courses.first()

    def _handle_invalid_course(self):
        if self.request.is_ajax():
            response = JsonResponse({"error": 'Invalid Course ID'})
            response.status_code = 403
            return response
        else:
            messages.error(self.request, 'Invalid Course ID')
            return redirect("teacher")

    def _check_valid_worksheet(self, worksheet_id):
        worksheets = Worksheet.objects.filter(id=worksheet_id, course=self.course)
        if not worksheets.exists():
            return False
        return worksheets.first()

    def _handle_invalid_worksheet(self):
        if self.request.is_ajax():
            response = JsonResponse({"error": 'Invalid Worksheet ID'})
            response.status_code = 403
            return response
        else:
            messages.error(self.request, 'Invalid Worksheet ID')
            return redirect("teacher_course", course_id=self.course.id)


class CourseViewMixin(TeacherViewMixin):

    def dispatch(self, request, *args, **kwargs):
        # is the user a teacher for this course ?
        course_id = kwargs.get('course_id', None)
        self.course = self._check_valid_course(course_id)
        if not self.course:
            return self._handle_invalid_course()
        return super(CourseViewMixin, self).dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourseViewMixin, self).get_context_data(**kwargs)
        context['course'] = self.course
        return context


class WorksheetViewMixin(TeacherViewMixin):

    def dispatch(self, request, *args, **kwargs):
        # is the user a teacher for this course ?
        course_id = kwargs.get('course_id', None)
        self.course = self._check_valid_course(course_id)
        if not self.course:
            return self._handle_invalid_course()

        # is the worksheet valid for this course ?
        worksheet_id = kwargs.get('worksheet_id', None)
        self.worksheet = self._check_valid_worksheet(worksheet_id)
        if not self.worksheet:
            return self._handle_invalid_worksheet()
        return super(WorksheetViewMixin, self).dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super(WorksheetViewMixin, self).get_context_data(**kwargs)
        context['course'] = self.course
        context['worksheet'] = self.worksheet
        return context


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


class CourseDetailView(CourseViewMixin, DetailView):
    context_object_name = 'course'
    template_name = "ComSemApp/teacher/course.html"

    def get_object(self):
        return self.course


class WorksheetListView(CourseViewMixin, ListView):
    model = Worksheet
    template_name = 'ComSemApp/teacher/worksheet_list.html'
    context_object_name = 'worksheets'

    def get_queryset(self):
        return self.course.get_visible_worksheets()


class WorksheetDetailView(WorksheetViewMixin, DetailView):
    template_name = 'ComSemApp/teacher/view_worksheet.html'
    context_object_name = 'worksheet'

    def get_object(self):
        return self.worksheet


class WorksheetCreateView(CourseViewMixin, UpdateView):
    model = Worksheet
    fields = ["topic", "display_original", "display_reformulation_text",
                "display_reformulation_audio", "display_all_expressions"]
    template_name = "ComSemApp/teacher/edit_worksheet.html"

    # technically an UpdateView since a worksheet object with status PENDING is created in the get_object method
    def get_object(self):
        worksheet, created = Worksheet.objects.get_or_create_pending(self.teacher, self.course)
        return worksheet

    def form_valid(self, form):
        self.object.status = teacher_constants.WORKSHEET_STATUS_UNRELEASED
        return super(WorksheetCreateView,self).form_valid(form)

    def get_success_url(self):
        return reverse("teacher_course", kwargs={'course_id': self.course.id })


class WorksheetUpdateView(WorksheetViewMixin, UpdateView):
    model = Worksheet
    fields = ["topic", "display_original", "display_reformulation_text",
                "display_reformulation_audio", "display_all_expressions"]
    template_name = "ComSemApp/teacher/edit_worksheet.html"
    context_object_name = 'worksheet'

    def get_object(self):
        return get_object_or_404(Worksheet, course=self.course, id=self.worksheet.id)

    def get_success_url(self):
        return reverse("teacher_course", kwargs={'course_id': self.course.id })


class WorksheetReleaseView(WorksheetViewMixin, View):
    model = Worksheet

    def get_object(self):
        return get_object_or_404(Worksheet, id=self.worksheet.id)

    def post(self, *args, **kwargs):
        worksheet = self.get_object()
        worksheet.release()
        return HttpResponse(status=204)


class WorksheetDeleteView(WorksheetViewMixin, DeleteView):
    model = Worksheet

    def get_object(self):
        return get_object_or_404(Worksheet, id=self.worksheet.id, status=teacher_constants.WORKSHEET_STATUS_UNRELEASED)

    def post(self, *args, **kwargs):
        worksheet = self.get_object()
        worksheet.delete()
        return HttpResponse(status=204)


class ExpressionListView(WorksheetViewMixin, ListView):
    model = Expression
    template_name = "ComSemApp/teacher/expressions.html"
    context_object_name = 'expressions'

    def get_queryset(self):
        return Expression.objects.filter(worksheet=self.worksheet)

    def get_context_data(self, **kwargs):
        context = super(ExpressionListView, self).get_context_data(**kwargs)
        context['course'] = self.course
        context['worksheet'] = self.worksheet
        return context


class ExpressionCreateView(WorksheetViewMixin, CreateView):
    model = Expression
    template_name = "ComSemApp/teacher/expression_form.html"
    fields = ["expression", "student", "all_do", "pronunciation", "context_vocabulary",
                "reformulation_text", "reformulation_audio"]

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        expression = form.save(commit=False)
        expression.worksheet = self.worksheet
        expression.save()
        if expression.reformulation_audio:
            # TODO - audio_file should really be part of the form and can be merged with reformulation_audio
            audio_file = self.request.FILES.get('audio_file', None)
            if audio_file:
                url = create_file_url("ExpressionReformulations", expression.id)
                handle_uploaded_file(audio_file, url)
        return JsonResponse({}, status=200)


class ExpressionUpdateView(WorksheetViewMixin, UpdateView):
    model = Expression
    template_name = "ComSemApp/teacher/expression_form.html"
    fields = ["expression", "student", "all_do", "pronunciation", "context_vocabulary",
                "reformulation_text", "reformulation_audio"]

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
        if expression.reformulation_audio:
            # TODO - audio_file should really be part of the form and can be merged with reformulation_audio
            audio_file = self.request.FILES.get('audio_file', None)
            if audio_file:
                url = create_file_url("ExpressionReformulations", expression.id)
                handle_uploaded_file(audio_file, url)
        return JsonResponse({}, status=200)


class ExpressionDeleteView(WorksheetViewMixin, DeleteView):
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
        reformulation_audio = expression.reformulation_audio
        # delete audio file if it exists
        if reformulation_audio:
            url = create_file_url("ExpressionReformulations", expression.id)
            delete_file(url)
        expression.delete()
        return HttpResponse(status=204)


class SubmissionView(WorksheetViewMixin, DetailView):
    template_name = "ComSemApp/teacher/view_submission.html"
    context_object_name = "submission"

    def get_object(self):
        submission_id = self.kwargs.get('submission_id', None)
        return get_object_or_404(StudentSubmission, id=submission_id, worksheet=self.worksheet)

    def post(self, *args, **kwargs):
        submission = self.get_object()
        attempts = submission.studentattempt_set.all()

        all_correct = True
        # status of each attempt
        for attempt in attempts:
            correct = self.request.POST.get(str(attempt.id), None) == '1'
            attempt.correct = correct
            attempt.save()

            if not correct:
                all_correct = False

        # handle status of the submission
        # TODO - use constants
        if all_correct:
            submission.status = 'complete'
        else:
            submission.status = 'incomplete'

        submission.save()

        messages.success(self.request, 'Assessment saved ', 'success')
        return redirect('teacher_worksheet_detail', self.course.id, self.worksheet.id)


# TODO - delete
def jsonify_expressions(expression_queryset):
    expressions = list(expression_queryset.values())

    # need to get name of assigned student seperately
    for i in range(len(expressions)):
        student = expression_queryset[i].student
        expressions[i]['student_name'] = str(student) if student else None
        expressions[i]['reformulation_audio'] = False if expressions[i]['reformulation_audio'] == '0' else True

    return json.dumps(expressions)


def create_file_url(directory, e):
    id_floor = int(math.floor(e/1000))
    url = settings.EFS_DIR
    url += directory + '/' + str(id_floor)
    if not os.path.exists(url):
        os.makedirs(url)
    filename = e - (id_floor * 1000)
    url += '/' + str(filename) + ".ogg"
    return url


def handle_uploaded_file(f, url):
    with open(url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def delete_file(url):
    os.remove(url)


