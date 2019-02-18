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
from django.template.defaulttags import register


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
    
    @register.filter('get_item')
    def get_item(dictionary, key):
        return dictionary.get(key)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data['bob'] = 'Ron Johnson'
        worksheets = Worksheet.objects.filter(course=self.course)
        subcountdict = {}
        ungradedcountdict = {}
        for student in self.course.students.all(): 
            subcount = 0
            ungradedcount = 0
            attemptcount = 0
            submissions = StudentSubmission.objects.filter(student=student)
            for submission in submissions :

                if submission.worksheet.course == self.course:
                    subcount = subcount + 1
                    print(submission.status)
                    if submission.status == 'ungraded':
                        ungradedcount = ungradedcount + 1
                    attemptcount = submission.get_number() + attemptcount

            subcountdict[student.user.username] = subcount
            ungradedcountdict[student.user.username] = ungradedcount
            attemptsdict[student.user.username] = attemptcount

        

        data['worksheetCount'] = len(worksheets)
        data['submissions'] = subcountdict
        data['ungraded'] = ungradedcountdict
        data['attempts'] = attemptsdict
        return data
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


class WorksheetReleaseView(TeacherWorksheetViewMixin, View):
    model = Worksheet

    def get_object(self):
        return get_object_or_404(Worksheet, id=self.worksheet.id)

    def post(self, *args, **kwargs):
        worksheet = self.get_object()
        worksheet.release()
        return HttpResponse(status=204)


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

    def get_object(self):
        submission_id = self.kwargs.get('submission_id', None)
        return get_object_or_404(StudentSubmission, id=submission_id, worksheet=self.worksheet)

    def post(self, *args, **kwargs):
        submission = self.get_object()

        all_correct = True
        # status of each attempt
        for attempt in submission.attempts.all():
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
        return redirect('teacher:worksheet_detail', self.course.id, self.worksheet.id)


def delete_file(url):
    try:
        os.remove(url)
    except FileNotFoundError:
        pass
