import json

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from ComSemApp import teacher_constants

from .teacher_views import create_file_url, handle_uploaded_file # helpers from theacher views - could be put in seperate module

from .models import *
from ComSemApp.libs.mixins import RoleViewMixin, CourseViewMixin, WorksheetViewMixin, SubmissionViewMixin


class StudentViewMixin(RoleViewMixin):

    role_class = Student

    def _set_role_obj(self):
        # role_obj self in RoleViewMixin
        self.student = self.role_obj

    def _check_valid_course(self, course_id):
        courses = Course.objects.filter(students=self.request.user.student, id=course_id)
        if not courses.exists():
            return False
        return courses.first()


class StudentCourseViewMixin(StudentViewMixin, CourseViewMixin):

    def _get_invalid_course_redirect(self):
        return HttpResponseRedirect(reverse("student"))


class StudentWorksheetViewMixin(StudentViewMixin, WorksheetViewMixin):

    def _get_invalid_worksheet_redirect(self):
        return HttpResponseRedirect(reverse("student_course", kwargs={"course_id": self.course.id}))


class StudentSubmissionViewMixin(StudentViewMixin, SubmissionViewMixin):

    def _get_invalid_submission_redirect(self):
        return HttpResponseRedirect(reverse("student_course", kwargs={"course_id": self.course.id}))


class CourseListView(StudentViewMixin, ListView):
    # student home page
    model = Course
    template_name = 'ComSemApp/student/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(students=self.student)


class CourseDetailView(StudentCourseViewMixin, DetailView):
    context_object_name = 'course'
    template_name = "ComSemApp/student/course.html"

    def get_object(self):
        return self.course

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        worksheets = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED)

        # TODO should this logic be in the worksheet model ?
        for worksheet in worksheets:
            last_submission = worksheet.last_submission(self.student)
            last_submission_status = last_submission.status if last_submission else "none"
            last_submission_id = last_submission.id if last_submission else 0
            status_colors = {
                "complete": "success",
                "incomplete": "danger",
                "ungraded": "warning",
                "pending": "light",
                "none": "info",
            }
            button_texts = {
                "complete": 'Review Worksheet',
                "incomplete": "Create Submission",
                "ungraded": "Edit Submission",
                "pending": "Complete Submission",
                "none": "Create Submission",
            }
            link_urls = {
                "complete": reverse("student_submission_list",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
                "incomplete": reverse("student_create_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
                "ungraded": reverse("student_update_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id, 'submission_id': last_submission_id}),
                "pending": reverse("student_create_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
                "none": reverse("student_create_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
            }

            worksheet.last_submission_status = last_submission_status
            worksheet.status_color = status_colors[last_submission_status]
            worksheet.button_text = button_texts[last_submission_status]
            worksheet.link_url = link_urls[last_submission_status]

        context['worksheets'] = worksheets
        return context


class SubmissionListView(StudentWorksheetViewMixin, ListView):
    template_name = 'ComSemApp/student/submission_list.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        return StudentSubmission.objects.filter(student=self.student, worksheet=self.worksheet)


class SubmissionUpdateCreateMixin(UpdateView):
    context_object_name = 'submission'
    template_name = "ComSemApp/student/create_submission.html"
    fields = []

    def get_context_data(self, **kwargs):
        context = super(SubmissionUpdateCreateMixin, self).get_context_data(**kwargs)
        context['previous_submissions'] = StudentSubmission.objects.filter(worksheet=self.worksheet, student=self.student).exclude(status__in=['pending', 'ungraded'])
        return context

    def get_success_url(self):
        return reverse("student_course", kwargs={'course_id': self.course.id })


class SubmissionCreateView(StudentWorksheetViewMixin, SubmissionUpdateCreateMixin):

    def dispatch(self, request, *args, **kwargs):
        response = super(SubmissionCreateView, self).dispatch(request, *args, **kwargs)
        # user can't create if there is an updatable submission
        if StudentSubmission.objects.filter(student=self.student, worksheet=self.worksheet, status__in=['ungraded', 'complete']).exists():
            messages.error(self.request, "You may not create a submission for this worksheet")
            return HttpResponseRedirect(reverse("student_course", kwargs={'course_id': self.course.id }))
        return response

    def get_object(self):
        submission, created = StudentSubmission.objects.get_or_create_pending(self.student, self.worksheet)
        return submission

    def form_valid(self, form):
        self.object.status = 'ungraded'
        return super(SubmissionCreateView, self).form_valid(form)


class SubmissionUpdateView(StudentSubmissionViewMixin, SubmissionUpdateCreateMixin):
    # update view that doesn't actually change the object. only used for success_url

    def get_object(self):
        return get_object_or_404(StudentSubmission, id=self.submission.id, status="ungraded")


class ExpressionListView(StudentSubmissionViewMixin, ListView):
    context_object_name = 'expressions'
    template_name = "ComSemApp/student/expression_list.html"

    def get_queryset(self):
        expression_filters = Q(worksheet=self.worksheet)
        if not self.worksheet.display_all_expressions:
            expression_filters &= (Q(student=self.student) | Q(student=None) | Q(all_do=True))
        expressions = Expression.objects.filter(expression_filters)
        for expression in expressions:
            attempt = None
            attempts = StudentAttempt.objects.filter(student_submission=self.submission, expression=expression)
            if attempts:
                attempt = attempts.first()
            expression.attempt = attempt
        return expressions


class AttemptCreateView(StudentSubmissionViewMixin, CreateView):
    model = StudentAttempt
    template_name = "ComSemApp/student/attempt_form.html"
    fields = ["reformulation_text", "reformulation_audio"]

    def get_context_data(self, **kwargs):
        context = super(AttemptCreateView, self).get_context_data(**kwargs)
        # TODO - expression mixin rather than grabbing expression twice ?
        expression_id = self.kwargs.get('expression_id')
        expression = get_object_or_404(Expression, id=expression_id, worksheet=self.worksheet)
        context['expression'] = expression
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        expression_id = self.kwargs.get('expression_id')
        expression = get_object_or_404(Expression, id=expression_id, worksheet=self.worksheet)

        attempt = form.save(commit=False)
        attempt.student_submission = self.submission
        attempt.expression = expression
        attempt.save()
        if attempt.reformulation_audio:
            # TODO - audio_file should really be part of the form and can be merged with reformulation_audio
            audio_file = self.request.FILES.get('audio_file', None)
            if audio_file:
                url = create_file_url("AttemptReformulations", attempt.id)
                handle_uploaded_file(audio_file, url)
        return JsonResponse({}, status=200)


class AttemptUpdateView(StudentSubmissionViewMixin, UpdateView):
    context_object_name = 'attempt'
    template_name = "ComSemApp/student/attempt_form.html"
    fields = ["reformulation_text", "reformulation_audio"]

    def get_context_data(self, **kwargs):
        context = super(AttemptUpdateView, self).get_context_data(**kwargs)
        context['expression'] = self.object.expression
        return context

    def get_object(self, **kwargs):
        attempt_id = self.kwargs.get('attempt_id')
        return get_object_or_404(StudentAttempt, student_submission=self.submission, id=attempt_id)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        attempt = form.save(commit=False)
        attempt.save()
        if attempt.reformulation_audio:
            # TODO - audio_file should really be part of the form and can be merged with reformulation_audio
            audio_file = self.request.FILES.get('audio_file', None)
            if audio_file:
                url = create_file_url("AttemptReformulations", attempt.id)
                handle_uploaded_file(audio_file, url)
        return JsonResponse({}, status=200)

