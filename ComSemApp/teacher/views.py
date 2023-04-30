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

import json, math, datetime, os, csv
from ComSemApp.models import *


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

    def get_context_data(self, **kwargs):
        context = super(TeacherViewMixin, self).get_context_data(**kwargs)
        # TODO show each of the user's institutions if they have more than one
        context['institution'] = self.institution.first()
        return context


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


class DownloadCourseCSV(TeacherCourseViewMixin, View):

    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.course}.csv"'

        writer = csv.writer(response)
        students = self.course.students.all()
        worksheets = self.course.worksheets.all()
        writer.writerow(['Worksheet Number', 'Expression Number', 'All Do', 'Student', 'Sentence'])

        # All non-AllDo sentences, ordered by student, then worksheet, then expression
        for student in students:
            expressions = Expression.objects.filter(
                student=student,
                worksheet__in=worksheets,
                all_do=False
            ).order_by('worksheet__date')
            for expression in expressions:
                self._write_expression_row(writer, expression)
            if expressions:
                writer.writerow(['', '', '', ''])

        # With All of the AllDo sentences just once at the end, ordered by Worksheet and sentence.
        expressions = Expression.objects.filter(
            all_do=True,
            worksheet__in=worksheets
        ).order_by('worksheet__date')
        if expressions:
            writer.writerow(['ALL-DO', '', '', ''])
        for expression in expressions:
            self._write_expression_row(writer, expression, all_do=True)

        return response

    def _write_expression_row(self, writer, expression, all_do=False):
        worksheet = expression.worksheet
        worksheet_number = worksheet.get_number()
        expression_number = expression.get_number()
        row = [
            f"{worksheet_number}",
            f"{expression_number}",
            "" if all_do else str(expression.student),
            f"{expression}"
        ]
        writer.writerow(row)


class WorksheetListView(TeacherCourseViewMixin, ListView):
    model = Worksheet
    template_name = 'ComSemApp/teacher/worksheet_list.html'
    context_object_name = 'worksheets'

    def get_queryset(self):
        return self.course.get_visible_worksheets().order_by('-date')


class WorksheetDetailView(TeacherWorksheetViewMixin, DetailView):
    template_name = 'ComSemApp/teacher/view_worksheet.html'
    context_object_name = 'worksheet'

    def get_object(self):
        return self.worksheet

    def get_context_data(self, **kwargs):
        context = super(WorksheetDetailView, self).get_context_data(**kwargs)
        context['submissions'] = self.worksheet.submissions.exclude(status="pending")
        context['worksheets'] = self.course.get_visible_worksheets()
        return context


class WorksheetCreateView(TeacherCourseViewMixin, UpdateView):
    model = Worksheet
    fields = ["topic", "display_original", "display_reformulation_text",
                "display_reformulation_audio", "display_all_expressions"]
    template_name = "ComSemApp/teacher/edit_worksheet.html"

    # technically an UpdateView since a worksheet object with status PENDING is created in the get_object method
    def get_object(self):
        worksheet, _ = Worksheet.objects.get_or_create_pending(self.teacher, self.course)
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
        if is_valid:
            return HttpResponse(status=204)
        return HttpResponse(status=406, reason="Worksheet must have at least one expression with a reforumlation.")


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
            text_correct = self.request.POST.get("T" + str(attempt.id), None) == '1' # get text
            audio_correct = self.request.POST.get("A" + str(attempt.id), None) == '1' # gets audio

            attempt.text_correct = text_correct # marks text
            if attempt.audio: # sets audio correct if there is audio
                attempt.audio_correct = audio_correct
            else: # sets audio_correct to None if there is no audio
                attempt.audio_correct = None
                
            attempt.save()
            if attempt.audio: # case for if there is audio
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


class SpeakingPracticeAttemptReviewView(TeacherCourseViewMixin, ListView):
    """
    This view displays the SpeakingPracticeReviewRequestListView and the
    SpeakingPracticeAttemptReviewCreateView/SpeakingPracticeAttemptReviewUpdateView
    """
    model = SpeakingPracticeAttempt
    template_name = "ComSemApp/teacher/attempt_request_review.html"


class SpeakingPracticeReviewRequestsListView(TeacherCourseViewMixin, ListView):
    """
    This view presents the list of review requests. on tghe SpeakingPracticeAttemptReviewPage 
    """
    model = SpeakingPracticeAttemptReviewRequest
    template_name = 'ComSemApp/teacher/request_list.html'
    context_object_name = 'requests'

    def get_queryset(self) -> QuerySet[SpeakingPracticeAttemptReviewRequest]:
        """
        Returns the queryset of SpeakingPracticeAttemptReviewRequests
        """
        return self.course.get_speaking_practice_review_requests().order_by('review','-date')


class SpeakingPracticeAttemptReviewCreateView(TeacherCourseViewMixin, CreateView):
    """
        This view presents SpeakingPracticeAttempt information and then creates a SpeakingPracticeAttemptReview
        for a SpeakingPracticeAttemptReviewRequest
    """
    model = SpeakingPracticeAttemptReview
    template_name = "ComSemApp/teacher/attempt_request_info.html"
    fields = ["request", "reviewer", "comments"]

    def get_context_data(self, **kwargs):
        """
            returns context data. This data is the SpeakingPracticeAttempt
        """
        context = super().get_context_data(**kwargs)
        attempt_id = self.kwargs.get('attempt_id')
        attempt = get_object_or_404(SpeakingPracticeAttempt, id=attempt_id)
        context['attempt'] = attempt
        return context
    

    def form_invalid(self, form) -> JsonResponse:
        """
            If there is incorrect information in the form sent, it will receive
            a Http 400 error
        """
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form) -> HttpResponse:
        """
            Handles a form to update data in the SpeakingPracticeAttemptReview Model.

            If there is a newScore, that field is changed on the attempt. 
            If this is the first time a new score is being inputted, the original score
            field will be set. 
        """
        review = form.save(commit=False)
        newScore = self.request.POST.get('newScore')
        if newScore:
            id = self.request.POST.get('request')
            attempt = get_object_or_404(SpeakingPracticeAttempt, id=id)
            review.original_score = attempt.correct
            attempt.correct = newScore
            attempt.save()
        review.save()
        return HttpResponse(status=201)
    
class SpeakingPracticeAttemptReviewUpdateView(TeacherCourseViewMixin, UpdateView):
    """
        This view presents SpeakingPracticeAttempt information and then updates a SpeakingPracticeAttemptReview
        for a SpeakingPracticeAttemptReviewRequest
    """
    model = SpeakingPracticeAttemptReview
    template_name = "ComSemApp/teacher/attempt_request_info.html"
    fields = ["reviewer", "comments"]
    context_object_name = 'review'

    def get_object(self, **kwargs):
        """
            Returns an SpeakingPracticeAttemptReview. This is the instance that is updated
            in this view.
        """
        attempt_id = self.kwargs.get('attempt_id')
        review = get_object_or_404(SpeakingPracticeAttemptReview, request=attempt_id)
        return review

    def get_context_data(self, **kwargs):
        """
            returns context data. This data is the SpeakingPracticeAttempt
        """
        context = super().get_context_data(**kwargs)
        attempt_id = self.kwargs.get('attempt_id')
        attempt = get_object_or_404(SpeakingPracticeAttempt, id=attempt_id)
        context['attempt'] = attempt
        return context

    def form_invalid(self, form) -> JsonResponse:
        """
            If there is incorrect information in the form sent, it will receive
            a Http 400 error
        """
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form) -> HttpResponse:
        """
            Handles a form to update data in the SpeakingPracticeAttemptReview Model.

            If there is a newScore, that field is changed on the attempt. 
            If this is the first time a new score is being inputted, the original score
            field will be set. 
        """
        review = form.save(commit=False)
        newScore = self.request.POST.get('newScore')
        if newScore:
            id = self.request.POST.get('request')
            attempt = get_object_or_404(SpeakingPracticeAttempt, id=id)
            if review.original_score is None:
                review.original_score = attempt.correct
            attempt.correct = newScore
            attempt.save()
        review.save()
        return HttpResponse(status=204)

